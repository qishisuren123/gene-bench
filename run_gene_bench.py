#!/usr/bin/env python3
"""
Gene-Bench 主实验脚本（EX1-EX7）。

实验编号统一使用 EX1-EX27：
  - EX1-EX7: 本脚本（Gene 核心实验）
  - EX8-EX27: run_evomap_experiments.py（EvoMap 双回路实验）

用法:
    python run_gene_bench.py --experiment ex1 --models gemini_pro,gemini_flash --gemini-key "$GEMINI_KEY"
    python run_gene_bench.py --experiment all --dry-run
"""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from dataclasses import dataclass, asdict, field
from collections import Counter
from typing import Optional

# ── 路径 ──

ROOT = Path(__file__).parent
SCENARIOS_DIR = ROOT / "scenarios"
SKILLS_DIR = ROOT / "skills"
GENES_DIR = ROOT / "genes"
DATA_DIR = ROOT / "data"

# ── 模型注册表 ──

MODEL_REGISTRY = {
    # 短名称 -> (API模型ID, API通道, 价格层级)
    # API通道: "yunwu" = yunwu.ai 代理, "gemini" = Google 直连
    "opus":         ("claude-opus-4-6",          "yunwu",  "expensive"),
    "sonnet":       ("claude-sonnet-4-6",        "yunwu",  "medium"),
    "haiku":        ("claude-haiku-4-5",         "yunwu",  "cheap"),
    "gpt5_4":       ("gpt-5.4",                  "yunwu",  "medium"),
    "gpt5_mini":    ("gpt-5-mini",               "yunwu",  "cheap"),
    "gpt5_nano":    ("gpt-5-nano",               "yunwu",  "free"),
    "gemini_pro":   ("gemini-3.1-pro-preview",       "gemini", "free"),
    "gemini_flash": ("gemini-3.1-flash-lite-preview","gemini", "free"),
    "qwen_moe":     ("qwen3.5-397b-a17b",       "yunwu",  "cheap"),
    "qwen_coder":   ("qwen3-coder",             "yunwu",  "expensive"),
    "ds_v3":        ("deepseek-v3.2-exp",        "yunwu",  "medium"),
    "ds_r1":        ("deepseek-r1",              "yunwu",  "expensive"),
}

ALL_MODELS = list(MODEL_REGISTRY.keys())

# 贵模型列表（某些 RQ 减少场景数）
EXPENSIVE_MODELS = [k for k, v in MODEL_REGISTRY.items() if v[2] == "expensive"]

# ── 场景列表 ──

# 原始 30 个场景（复用 skill-bench）
ORIGINAL_SCENARIOS = [
    "S002_spike_behavior", "S005_protein_parse", "S007_data_viz",
    "S011_particle_physics", "S012_uv_spectroscopy", "S017_ctd_ocean",
    "S026_earthquake_catalog", "S028_audio_features", "S030_fossil_morpho",
    "S033_exoplanet_transit", "S036_cmb_power_spectrum", "S037_asteroid_orbit",
    "S044_bfactor_analysis", "S045_ramachandran", "S048_gene_ontology",
    "S052_phylogenetic_distance", "S053_methylation_beta", "S054_species_accumulation",
    "S060_phenology_shifts", "S067_salinity_gradient", "S068_weather_fronts",
    "S069_rainfall_extreme", "S072_ozone_profile", "S074_heat_index",
    "S077_grain_size", "S084_dose_response", "S090_noise_reduction",
    "S091_modulation_classify", "S093_echo_removal", "S096_network_influence",
]

# 新增 15 个场景
NEW_SCENARIOS = [
    "S101_climate_attribution", "S102_protein_secondary",
    "S103_instrumental_variable", "S104_multisensor_anomaly",
    "S105_community_detection", "S106_seismic_denoise",
    "S107_regime_switch", "S108_raman_spectroscopy",
    "S109_hdf5_chunked", "S110_log_regex",
    "S111_cuda_memory", "S112_midi_chords",
    "S113_inventory_reorder", "S114_obstacle_avoidance",
    "S115_quantum_circuit",
]

ALL_SCENARIOS = ORIGINAL_SCENARIOS + NEW_SCENARIOS

# 统一场景集: 所有实验使用全部 45 个场景
GENE_SENSITIVE_SCENARIOS = ALL_SCENARIOS  # 导出给 run_evomap_experiments.py 使用

EX1_SCENARIOS = ALL_SCENARIOS
EX2_SCENARIOS = ALL_SCENARIOS
EX3_SCENARIOS = ALL_SCENARIOS
EX4_SCENARIOS_PAIRS = [
    # (source_scenario, target_scenario, transfer_type)
    ("S090_noise_reduction", "S106_seismic_denoise", "analogous_task"),
    ("S068_weather_fronts", "S107_regime_switch", "analogous_task"),
    ("S012_uv_spectroscopy", "S108_raman_spectroscopy", "analogous_task"),
    ("S084_dose_response", "S113_inventory_reorder", "unrelated"),
    ("S002_spike_behavior", "S112_midi_chords", "unrelated"),
    ("S033_exoplanet_transit", "S111_cuda_memory", "unrelated"),
    ("S090_noise_reduction", "S090_noise_reduction", "exact_match"),
    ("S012_uv_spectroscopy", "S012_uv_spectroscopy", "exact_match"),
    ("S068_weather_fronts", "S068_weather_fronts", "exact_match"),
    ("S084_dose_response", "S084_dose_response", "exact_match"),
    ("S090_noise_reduction", "S093_echo_removal", "same_domain"),
    ("S012_uv_spectroscopy", "S077_grain_size", "same_domain"),
]
EX5_SCENARIOS = ALL_SCENARIOS
EX6_SCENARIOS = ALL_SCENARIOS
EX7_SCENARIOS = ALL_SCENARIOS

# Gene 完整度级别
GENE_LEVELS = ["G0", "G1", "G2", "G3", "G4", "L1"]

# Gene 变异类型
GENE_MUTATION_TYPES = [
    "wrong_algorithm", "wrong_domain", "inverted_priority",
    "stale_paradigm", "overconstrained",
]

# EX6 自生成 Gene 的作者模型
EX6_AUTHOR_MODELS = ["opus", "haiku", "gpt5_4", "gemini_pro"]

# 固定参数
TEMPERATURE = 0.0
MAX_TOKENS = 16384
EVAL_TIMEOUT = 120


# ── 数据类 ──

@dataclass
class TrialConfig:
    scenario_id: str
    model: str
    rq: str
    condition: str
    gene_level: str = "G0"
    mutation_type: str = "none"
    transfer_source: str = "none"
    combination_mode: str = "none"
    gene_author: str = "none"
    vaccinated: bool = False
    temperature: float = 0.0
    run_id: int = 0

    @property
    def trial_key(self) -> str:
        parts = [
            self.scenario_id, self.model, self.rq,
            self.condition, f"t{self.temperature}", f"r{self.run_id}",
        ]
        return "__".join(parts)


# ── Trial 生成器 ──

def generate_rq1_trials(models: list[str], scenarios: list[str]) -> list[TrialConfig]:
    """EX1: Gene 完整度梯度 — N 模型 × 45 场景 × 6 级别"""
    trials = []
    for m in models:
        for s in scenarios:
            for level in GENE_LEVELS:
                trials.append(TrialConfig(
                    scenario_id=s, model=m, rq="ex1",
                    condition=f"ex1_{level}",
                    gene_level=level,
                ))
    return trials


def generate_rq2_trials(models: list[str], scenarios: list[str]) -> list[TrialConfig]:
    """EX2: Gene vs Skill 正面对决 — N 模型 × 45 场景 × 4 条件"""
    trials = []
    conditions = [
        ("no_context", "G0"),
        ("gene_g3", "G3"),
        ("skill_l1", "L1"),
        ("skill_l4", "L4"),  # L4 = 完整 Skill 包
    ]
    for m in models:
        for s in scenarios:
            for cond_name, level in conditions:
                trials.append(TrialConfig(
                    scenario_id=s, model=m, rq="ex2",
                    condition=f"ex2_{cond_name}",
                    gene_level=level,
                ))
    return trials


def generate_rq3_trials(models: list[str], scenarios: list[str]) -> list[TrialConfig]:
    """EX3: Gene 错误容忍度 — N 模型 × 45 场景 × 6 条件"""
    trials = []
    for m in models:
        for s in scenarios:
            # clean baseline
            trials.append(TrialConfig(
                scenario_id=s, model=m, rq="ex3",
                condition="ex3_clean_g3",
                gene_level="G3",
            ))
            # 5 种变异
            for mt in GENE_MUTATION_TYPES:
                trials.append(TrialConfig(
                    scenario_id=s, model=m, rq="ex3",
                    condition=f"ex3_mutated_{mt}",
                    gene_level="G3",
                    mutation_type=mt,
                ))
    return trials


def generate_rq4_trials(models: list[str]) -> list[TrialConfig]:
    """EX4: 跨领域 Gene 迁移 — N 模型 × 12 场景对 × 5 条件"""
    trials = []
    for m in models:
        sc_pairs = EX4_SCENARIOS_PAIRS[:6] if m in EXPENSIVE_MODELS else EX4_SCENARIOS_PAIRS
        for source, target, transfer_type in sc_pairs:
            # 用 source 的 Gene 解 target 的任务
            trials.append(TrialConfig(
                scenario_id=target, model=m, rq="ex4",
                condition=f"ex4_{transfer_type}",
                gene_level="G3",
                transfer_source=source,
            ))
        # 每个 target 也需要 no_context baseline
        targets_seen = set()
        for _, target, _ in sc_pairs:
            if target not in targets_seen:
                targets_seen.add(target)
                trials.append(TrialConfig(
                    scenario_id=target, model=m, rq="ex4",
                    condition="ex4_none",
                    gene_level="G0",
                ))
    return trials


def generate_rq5_trials(models: list[str], scenarios: list[str]) -> list[TrialConfig]:
    """EX5: Gene 组合效应 — N 模型 × 45 场景 × 5 条件"""
    trials = []
    conditions = [
        ("single", "none"),
        ("2x_complementary", "complementary"),
        ("3x_complementary", "complementary"),
        ("2x_conflicting", "conflicting"),
        ("none", "none"),
    ]
    for m in models:
        for s in scenarios:
            for cond_name, combo_mode in conditions:
                level = "G0" if cond_name == "none" else "G3"
                trials.append(TrialConfig(
                    scenario_id=s, model=m, rq="ex5",
                    condition=f"ex5_{cond_name}",
                    gene_level=level,
                    combination_mode=combo_mode if cond_name != "single" else "none",
                ))
    return trials


def generate_rq6_trials(models: list[str], scenarios: list[str]) -> list[TrialConfig]:
    """EX6: 自生成 Gene — N 模型 × 45 场景 × 6 条件"""
    trials = []
    for m in models:
        for s in scenarios:
            # 4 个作者 Gene + 人工 Gene + 无 Gene
            for author in EX6_AUTHOR_MODELS:
                trials.append(TrialConfig(
                    scenario_id=s, model=m, rq="ex6",
                    condition=f"ex6_author_{author}",
                    gene_level="G3",
                    gene_author=author,
                ))
            # 人工 Gene
            trials.append(TrialConfig(
                scenario_id=s, model=m, rq="ex6",
                condition="ex6_human_gene",
                gene_level="G3",
                gene_author="human",
            ))
            # 无 Gene
            trials.append(TrialConfig(
                scenario_id=s, model=m, rq="ex6",
                condition="ex6_none",
                gene_level="G0",
            ))
    return trials


def generate_rq7_trials(models: list[str], scenarios: list[str]) -> list[TrialConfig]:
    """EX7: Gene 接种效应 — N 模型 × 45 场景 × 5 条件"""
    trials = []
    conditions = [
        ("none", "G0", False, "none"),
        ("clean_gene", "G3", False, "none"),
        ("wrong_gene", "G3", False, "wrong_algorithm"),
        ("vaccinated_clean", "G3", True, "none"),
        ("vaccinated_wrong", "G3", True, "wrong_algorithm"),
    ]
    for m in models:
        for s in scenarios:
            for cond_name, level, vacc, mt in conditions:
                trials.append(TrialConfig(
                    scenario_id=s, model=m, rq="ex7",
                    condition=f"ex7_{cond_name}",
                    gene_level=level,
                    mutation_type=mt,
                    vaccinated=vacc,
                ))
    return trials


# ── Gene 加载 ──

def load_gene_for_trial(trial: TrialConfig) -> Optional[dict]:
    """根据 trial 配置加载对应的 Gene JSON"""
    if trial.gene_level == "G0":
        return None

    # EX6: 自生成 Gene
    if trial.rq == "ex6" and trial.gene_author != "human":
        author_path = GENES_DIR / "self_generated" / trial.gene_author / f"{trial.scenario_id}.json"
        if author_path.exists():
            with open(author_path) as f:
                return json.load(f)

    # EX4: 跨领域迁移 — 加载 source 场景的 Gene
    if trial.rq == "ex4" and trial.transfer_source != "none":
        source_path = GENES_DIR / f"{trial.transfer_source}.json"
        if source_path.exists():
            with open(source_path) as f:
                return json.load(f)
        return None

    # 默认：加载目标场景的 Gene
    gene_path = GENES_DIR / f"{trial.scenario_id}.json"
    if gene_path.exists():
        with open(gene_path) as f:
            return json.load(f)

    return None


def prepare_system_prompt(trial: TrialConfig, gene: Optional[dict]) -> str:
    """根据 trial 配置构建系统提示"""
    # 延迟导入避免循环依赖
    from gene_injector import inject_gene, inject_skill_full, inject_vaccinated

    # L4 完整 Skill
    if trial.gene_level == "L4":
        skill_dir = SKILLS_DIR / trial.scenario_id / "direct"
        return inject_skill_full(skill_dir)

    # G0 或无 Gene
    if trial.gene_level == "G0" or gene is None:
        return ""

    # 变异处理（RQ3, RQ7）
    if trial.mutation_type != "none":
        from gene_builder import mutate_gene
        gene = mutate_gene(gene, trial.mutation_type)

    # EX5 组合处理
    if trial.combination_mode != "none" and trial.rq == "ex5":
        from gene_injector import inject_combined_genes
        # 加载互补/冲突 Gene（简化：用同领域其他场景的 Gene）
        extra_genes = _load_complementary_genes(trial)
        if extra_genes:
            all_genes = [gene] + extra_genes
            n = 2 if "2x" in trial.condition else 3
            all_genes = all_genes[:n]
            return inject_combined_genes(all_genes, trial.combination_mode)

    # L1 SKILL.md 对照
    skill_dir = SKILLS_DIR / trial.scenario_id / "direct"

    # 接种处理（RQ7）
    if trial.vaccinated:
        return inject_vaccinated(gene, trial.gene_level, skill_dir)

    # 标准 Gene 注入
    return inject_gene(gene, trial.gene_level, skill_dir)


def _load_complementary_genes(trial: TrialConfig) -> list[dict]:
    """为 RQ5 加载互补 Gene（同领域其他场景）"""
    genes = []
    for gene_file in sorted(GENES_DIR.glob("S*.json")):
        if gene_file.stem == trial.scenario_id:
            continue
        try:
            with open(gene_file) as f:
                g = json.load(f)
            genes.append(g)
        except (json.JSONDecodeError, IOError):
            pass
        if len(genes) >= 3:
            break
    return genes


# ── API 调用 ──

def call_yunwu(model_id: str, task_desc: str, system_prompt: str,
               api_key: str) -> dict:
    """通过 yunwu.ai 调用 LLM（OpenAI 兼容接口）"""
    import openai

    client = openai.OpenAI(
        api_key=api_key,
        base_url="https://yunwu.ai/v1",
    )

    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": task_desc})

    resp = client.chat.completions.create(
        model=model_id,
        messages=messages,
        max_tokens=MAX_TOKENS,
        temperature=TEMPERATURE,
    )

    choice = resp.choices[0]
    usage = resp.usage

    return {
        "response": choice.message.content or "",
        "input_tokens": usage.prompt_tokens if usage else 0,
        "output_tokens": usage.completion_tokens if usage else 0,
        "stop_reason": choice.finish_reason,
    }


def call_gemini(model_id: str, task_desc: str, system_prompt: str,
                api_key: str) -> dict:
    """通过 Google Gemini REST API 直连调用"""
    import urllib.request
    import urllib.error

    # 设置代理（如果需要代理访问 Google API，请设置 https_proxy 环境变量）
    proxy = os.environ.get("https_proxy", os.environ.get("http_proxy", ""))
    if proxy:
        proxy_handler = urllib.request.ProxyHandler({
            "http": proxy, "https": proxy,
        })
        opener = urllib.request.build_opener(proxy_handler)
    else:
        opener = urllib.request.build_opener()

    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_id}:generateContent?key={api_key}"

    # 构建请求体
    contents = [{"parts": [{"text": task_desc}]}]
    body = {
        "contents": contents,
        "generationConfig": {
            "maxOutputTokens": MAX_TOKENS,
            "temperature": TEMPERATURE,
        },
    }
    if system_prompt:
        body["systemInstruction"] = {"parts": [{"text": system_prompt}]}

    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(url, data=data, method="POST")
    req.add_header("Content-Type", "application/json")

    resp_data = opener.open(req, timeout=300).read()
    result = json.loads(resp_data)

    # 提取文本
    text = ""
    if "candidates" in result and result["candidates"]:
        parts = result["candidates"][0].get("content", {}).get("parts", [])
        text = "".join(p.get("text", "") for p in parts)

    # 提取 token 用量
    usage = result.get("usageMetadata", {})
    input_tokens = usage.get("promptTokenCount", 0)
    output_tokens = usage.get("candidatesTokenCount", 0)

    return {
        "response": text,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "stop_reason": "stop",
    }


def call_llm(model_key: str, task_desc: str, system_prompt: str,
             yunwu_key: str = "", gemini_key: str = "") -> dict:
    """统一 API 调用入口"""
    model_id, channel, _ = MODEL_REGISTRY[model_key]

    if channel == "gemini":
        if not gemini_key:
            raise ValueError(f"Gemini API key required for model {model_key}")
        return call_gemini(model_id, task_desc, system_prompt, gemini_key)
    else:
        if not yunwu_key:
            raise ValueError(f"yunwu.ai API key required for model {model_key}")
        return call_yunwu(model_id, task_desc, system_prompt, yunwu_key)


# ── 代码提取与评估 ──

def extract_python_code(text: str) -> str:
    """从 LLM 回复中提取 Python 代码"""
    blocks = re.findall(r"```python\s*\n(.*?)```", text, re.DOTALL)
    if not blocks:
        blocks = re.findall(r"```\s*\n(.*?)```", text, re.DOTALL)
    return max(blocks, key=len).strip() if blocks else ""


def evaluate_code(code: str, scenario_dir: Path, timeout: int = EVAL_TIMEOUT) -> dict:
    """在临时目录中执行生成的代码并运行测试"""
    test_script = scenario_dir / "test_script.py"
    if not test_script.exists():
        return {"passed": False, "n_pass": 0, "n_total": 0, "pass_rate": 0,
                "error_type": "no_test_script"}

    with tempfile.TemporaryDirectory() as tmpdir:
        # 写入生成的代码（test_script.py 中引用 solution.py 或 generated.py）
        for name in ["solution.py", "generated.py"]:
            (Path(tmpdir) / name).write_text(code)

        # 复制测试脚本和可能的数据文件
        shutil.copy(test_script, tmpdir)
        # 复制场景目录中的其他数据文件
        for f in scenario_dir.iterdir():
            if f.name != "test_script.py" and f.name != "task.md" and f.is_file():
                try:
                    shutil.copy(f, tmpdir)
                except Exception:
                    pass

        try:
            result = subprocess.run(
                [sys.executable, "test_script.py"],
                cwd=tmpdir, capture_output=True, text=True, timeout=timeout,
            )
            stdout = result.stdout
            stderr = result.stderr

            passes = stdout.count("PASS:")
            fails = stdout.count("FAIL:")
            total = passes + fails
            if total == 0:
                total = 1

            return {
                "passed": fails == 0 and passes > 0,
                "n_pass": passes,
                "n_total": total,
                "pass_rate": passes / total if total > 0 else 0,
                "error_type": "success" if fails == 0 and passes > 0 else "test_failure",
                "returncode": result.returncode,
            }
        except subprocess.TimeoutExpired:
            return {"passed": False, "n_pass": 0, "n_total": 1, "pass_rate": 0,
                    "error_type": "timeout"}
        except Exception as e:
            return {"passed": False, "n_pass": 0, "n_total": 1, "pass_rate": 0,
                    "error_type": str(type(e).__name__)}


# ── EX6 Phase 1: 自生成 Gene ──

GENE_GENERATION_PROMPT = """Analyze the following task and generate a strategic "gene" — a concise, high-level strategy guide.

Your output must be valid JSON with this exact structure:
{{
  "scenario_id": "{scenario_id}",
  "domain": "<one-word domain>",
  "keywords": ["<5-8 domain-specific keywords>"],
  "summary": "<one sentence describing the optimal strategy>",
  "strategy": ["<step 1>", "<step 2>", "<step 3>"],
  "pitfalls": ["<common mistake 1>", "<common mistake 2>"],
  "key_concepts": ["<important concept 1>", "<important concept 2>"]
}}

Focus on STRATEGY, not implementation. Describe WHAT approach to take and WHY, not HOW to code it.

Task:
{task_desc}
"""


def generate_self_gene(model_key: str, scenario_id: str, task_desc: str,
                       yunwu_key: str = "", gemini_key: str = "") -> Optional[dict]:
    """RQ6 Phase 1: 让模型为任务自生成 Gene"""
    prompt = GENE_GENERATION_PROMPT.format(
        scenario_id=scenario_id,
        task_desc=task_desc,
    )
    try:
        result = call_llm(model_key, prompt, "", yunwu_key, gemini_key)
        text = result["response"]
        # 提取 JSON
        json_match = re.search(r'\{[\s\S]*\}', text)
        if json_match:
            gene = json.loads(json_match.group())
            gene["_author"] = model_key
            return gene
    except Exception as e:
        print(f"    Gene generation failed for {model_key}/{scenario_id}: {e}")
    return None


def run_rq6_phase1(scenarios: list[str], yunwu_key: str, gemini_key: str,
                    output_dir: Path):
    """EX6 Phase 1: 4 个作者模型 × N 场景 → 自生成 Gene"""
    print("\n=== EX6 Phase 1: Generating self-authored genes ===")
    for author in EX6_AUTHOR_MODELS:
        author_dir = output_dir / "self_generated" / author
        author_dir.mkdir(parents=True, exist_ok=True)

        for s in scenarios:
            out_path = author_dir / f"{s}.json"
            if out_path.exists():
                print(f"  [skip] {author}/{s} (already exists)")
                continue

            task_path = SCENARIOS_DIR / s / "task.md"
            if not task_path.exists():
                print(f"  [skip] {author}/{s} (no task.md)")
                continue

            task_desc = task_path.read_text()
            print(f"  Generating: {author} → {s} ...", end="", flush=True)

            gene = generate_self_gene(author, s, task_desc, yunwu_key, gemini_key)
            if gene:
                with open(out_path, "w") as f:
                    json.dump(gene, f, indent=2, ensure_ascii=False)
                print(" OK")
            else:
                print(" FAILED")


# ── 主实验循环 ──

def run_experiment(trials: list[TrialConfig], yunwu_key: str, gemini_key: str,
                   output_file: Path, dry_run: bool = False, n_threads: int = 8):
    """执行实验（支持多线程并行）"""
    from budget_tracker import BudgetTracker
    from concurrent.futures import ThreadPoolExecutor, as_completed
    import threading

    tracker = BudgetTracker(budget=500.0, log_path=DATA_DIR / "budget_log.jsonl")
    write_lock = threading.Lock()
    counter = {"done": 0, "errors": 0, "total": 0}

    print(f"\n{'DRY RUN — ' if dry_run else ''}Running {len(trials)} trials ({n_threads} threads)")
    print(f"Output: {output_file}")
    ok, status = tracker.check_budget()
    print(f"Budget: {status}\n")

    if not ok and not dry_run:
        print("ERROR: Budget exceeded! Use --force to override.")
        return

    # 加载已完成的 trials（支持断点续跑）
    completed = set()
    if output_file.exists():
        for line in output_file.read_text().strip().split("\n"):
            if line:
                try:
                    completed.add(json.loads(line)["trial_key"])
                except (json.JSONDecodeError, KeyError):
                    pass
        print(f"  Resuming: {len(completed)} trials already completed\n")

    # 过滤掉已完成的
    pending = [t for t in trials if t.trial_key not in completed]
    counter["total"] = len(pending)
    print(f"  Pending: {len(pending)} trials\n")

    if dry_run:
        for trial in pending:
            print(f"  {trial.model:12s} {trial.scenario_id:28s} {trial.condition:30s} (dry run)")
        return

    output_file.parent.mkdir(parents=True, exist_ok=True)

    def run_single_trial(trial: TrialConfig) -> None:
        """执行单个 trial（线程安全）"""
        # 加载 task
        scenario_dir = SCENARIOS_DIR / trial.scenario_id
        task_path = scenario_dir / "task.md"
        if not task_path.exists():
            return

        task_desc = task_path.read_text()

        # 加载并准备 Gene
        gene = load_gene_for_trial(trial)
        system_prompt = prepare_system_prompt(trial, gene)

        # 调用 API
        try:
            api_result = call_llm(trial.model, task_desc, system_prompt, yunwu_key, gemini_key)
        except Exception as e:
            with write_lock:
                counter["errors"] += 1
                counter["done"] += 1
                print(f"  [{counter['done']}/{counter['total']}] {trial.model:12s} {trial.scenario_id:28s} {trial.condition:30s} API ERROR: {e}")
            return

        # 记录成本
        model_id = MODEL_REGISTRY[trial.model][0]
        cost = tracker.record(
            model_id,
            api_result.get("input_tokens", 0),
            api_result.get("output_tokens", 0),
            rq=trial.rq,
            scenario=trial.scenario_id,
        )

        # 提取代码
        code = extract_python_code(api_result["response"])
        if not code:
            result = {
                "trial_key": trial.trial_key,
                "trial_config": asdict(trial),
                "eval": {"passed": False, "n_pass": 0, "n_total": 0,
                         "pass_rate": 0, "error_type": "format_error"},
                "code_length": 0,
                "gene_tokens": len(system_prompt) // 4 if system_prompt else 0,
                "input_tokens": api_result.get("input_tokens", 0),
                "output_tokens": api_result.get("output_tokens", 0),
                "cost": cost,
            }
            status_str = f"NO CODE (${cost:.4f})"
        else:
            # 评估
            eval_result = evaluate_code(code, scenario_dir)
            result = {
                "trial_key": trial.trial_key,
                "trial_config": asdict(trial),
                "eval": eval_result,
                "code_length": len(code),
                "gene_tokens": len(system_prompt) // 4 if system_prompt else 0,
                "input_tokens": api_result.get("input_tokens", 0),
                "output_tokens": api_result.get("output_tokens", 0),
                "cost": cost,
            }
            if eval_result["passed"]:
                status_str = f"PASS ({eval_result['n_pass']}/{eval_result['n_total']}) ${cost:.4f}"
            else:
                status_str = f"FAIL ({eval_result['error_type']}) ${cost:.4f}"

        # 线程安全写入结果
        with write_lock:
            with open(output_file, "a") as f:
                f.write(json.dumps(result, default=str) + "\n")
            counter["done"] += 1
            print(f"  [{counter['done']}/{counter['total']}] {trial.model:12s} {trial.scenario_id:28s} {trial.condition:30s} {status_str}")

    # 并行执行
    with ThreadPoolExecutor(max_workers=n_threads) as executor:
        futures = [executor.submit(run_single_trial, t) for t in pending]
        for f in as_completed(futures):
            try:
                f.result()
            except Exception as e:
                with write_lock:
                    counter["errors"] += 1
                    print(f"  Unexpected error: {e}")

    print(f"\n  Completed: {counter['done']}, Errors: {counter['errors']}")

    # 打印预算报告
    print(tracker.report())


# ── CLI ──

def main():
    parser = argparse.ArgumentParser(
        description="Gene-Bench: Gene-level guided code generation experiments (EX1-EX7)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Dry run
  python run_gene_bench.py --dry-run

  # Pilot: 免费模型跑 EX1
  python run_gene_bench.py --experiment ex1 \\
      --models gemini_pro,gemini_flash \\
      --gemini-key "$GEMINI_KEY"

  # EX2: Gene vs Skill 正面对决
  python run_gene_bench.py --experiment ex2 \\
      --yunwu-key "$YUNWU_KEY" --gemini-key "$GEMINI_KEY"

  # 全部 EX1-EX7
  python run_gene_bench.py --experiment all \\
      --yunwu-key "$YUNWU_KEY" --gemini-key "$GEMINI_KEY"
""")

    parser.add_argument("--experiment", "--rq", dest="experiment",
                        choices=["ex1", "ex2", "ex3", "ex4", "ex5", "ex6", "ex7",
                                 "pilot", "all"],
                        default="all", help="Which experiment to run (EX1-EX7)")
    parser.add_argument("--models", type=str, default=None,
                        help=f"Comma-separated model list (default: all 12)")
    parser.add_argument("--scenarios", type=str, default=None,
                        help="Comma-separated scenario IDs (overrides RQ defaults)")
    parser.add_argument("--yunwu-key", type=str,
                        default=os.environ.get("YUNWU_API_KEY", ""),
                        help="yunwu.ai API key")
    parser.add_argument("--gemini-key", type=str,
                        default=os.environ.get("GEMINI_API_KEY", ""),
                        help="Gemini API key")
    parser.add_argument("--output", type=str,
                        default=str(DATA_DIR / "gene_bench_results.jsonl"),
                        help="Output JSONL file")
    parser.add_argument("--dry-run", action="store_true",
                        help="Print trial plan without executing")
    parser.add_argument("--force", action="store_true",
                        help="Override budget check")
    parser.add_argument("--ex6-phase1", "--rq6-phase1", dest="ex6_phase1",
                        action="store_true",
                        help="Run EX6 Phase 1 (self-generate genes) only")

    args = parser.parse_args()

    # 模型列表
    if args.models:
        models = [m.strip() for m in args.models.split(",")]
    elif args.experiment == "pilot":
        models = ["gemini_pro", "gemini_flash"]
    else:
        models = ALL_MODELS

    # 验证模型
    for m in models:
        if m not in MODEL_REGISTRY:
            parser.error(f"Unknown model: {m}. Choose from: {list(MODEL_REGISTRY.keys())}")

    # API key 检查
    if not args.dry_run:
        needs_yunwu = any(MODEL_REGISTRY[m][1] == "yunwu" for m in models)
        needs_gemini = any(MODEL_REGISTRY[m][1] == "gemini" for m in models)
        if needs_yunwu and not args.yunwu_key:
            parser.error("--yunwu-key required for yunwu.ai models (or set YUNWU_API_KEY)")
        if needs_gemini and not args.gemini_key:
            parser.error("--gemini-key required for Gemini models (or set GEMINI_API_KEY)")

    # EX6 Phase 1
    if args.ex6_phase1:
        scenarios = [s.strip() for s in args.scenarios.split(",")] if args.scenarios else EX6_SCENARIOS
        run_rq6_phase1(scenarios, args.yunwu_key, args.gemini_key, GENES_DIR)
        return

    # 自定义场景覆盖
    custom_scenarios = [s.strip() for s in args.scenarios.split(",")] if args.scenarios else None

    # 生成 trials
    trials = []
    ex = args.experiment

    if ex in ("ex1", "pilot", "all"):
        sc = custom_scenarios or EX1_SCENARIOS
        t = generate_rq1_trials(models, sc)
        print(f"EX1: {len(t)} trials")
        trials.extend(t)

    if ex in ("ex2", "all"):
        sc = custom_scenarios or EX2_SCENARIOS
        t = generate_rq2_trials(models, sc)
        print(f"EX2: {len(t)} trials")
        trials.extend(t)

    if ex in ("ex3", "all"):
        sc = custom_scenarios or EX3_SCENARIOS
        t = generate_rq3_trials(models, sc)
        print(f"EX3: {len(t)} trials")
        trials.extend(t)

    if ex in ("ex4", "all"):
        t = generate_rq4_trials(models)
        print(f"EX4: {len(t)} trials")
        trials.extend(t)

    if ex in ("ex5", "all"):
        sc = custom_scenarios or EX5_SCENARIOS
        t = generate_rq5_trials(models, sc)
        print(f"EX5: {len(t)} trials")
        trials.extend(t)

    if ex in ("ex6", "all"):
        sc = custom_scenarios or EX6_SCENARIOS
        t = generate_rq6_trials(models, sc)
        print(f"EX6: {len(t)} trials")
        trials.extend(t)

    if ex in ("ex7", "all"):
        sc = custom_scenarios or EX7_SCENARIOS
        t = generate_rq7_trials(models, sc)
        print(f"EX7: {len(t)} trials")
        trials.extend(t)

    print(f"\nTotal: {len(trials)} trials")

    # Dry run 汇总
    if args.dry_run:
        print("\n--- Dry Run Summary ---")
        by_model = Counter(t.model for t in trials)
        by_rq = Counter(t.rq for t in trials)
        by_cond = Counter(t.condition for t in trials)

        print("\nBy RQ:")
        for r, c in sorted(by_rq.items()):
            print(f"  {r}: {c}")

        print("\nBy model:")
        for m, c in by_model.most_common():
            tier = MODEL_REGISTRY[m][2]
            print(f"  {m:15s} ({tier:10s}): {c}")

        print("\nBy condition (top 20):")
        for cond, c in by_cond.most_common(20):
            print(f"  {cond}: {c}")

        # 粗略成本估算
        est_cost = 0
        for t in trials:
            _, _, tier = MODEL_REGISTRY[t.model]
            per_trial = {"free": 0, "cheap": 0.01, "medium": 0.04, "expensive": 0.12}
            est_cost += per_trial.get(tier, 0.05)
        print(f"\nEstimated cost: ~${est_cost:.0f}")
        return

    output_file = Path(args.output)
    run_experiment(trials, args.yunwu_key, args.gemini_key, output_file, dry_run=False)

    print(f"\nDone! Results saved to {output_file}")


if __name__ == "__main__":
    main()
