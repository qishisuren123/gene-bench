#!/usr/bin/env python3
"""
Gene 构建与变异模块。

每个 Gene 遵循 evomap.ai GEP v1.5.0 Schema，包含从 SKILL.md 蒸馏出的策略信息。
支持按 G0-G4/L1 级别序列化，以及 RQ3 所需的 5 种变异。
"""

import json
import copy
import hashlib
import random
from pathlib import Path
from typing import Optional

# ── Gene JSON Schema (GEP v1.5.0) ──
# {
#   "type": "Gene",
#   "schema_version": "1.5.0",
#   "id": "gene_S002_spike_behavior",
#   "category": "optimize",
#   "signals_match": ["hdf5", "histogram", "interpolate", ...],
#   "summary": "一句话描述任务策略...",
#   "preconditions": ["前置条件1...", ...],
#   "strategy": ["步骤1...", "步骤2...", "AVOID: 陷阱1...", ...],
#   "constraints": {"max_files": 1, "forbidden_paths": []},
#   "validation": ["python -m pytest scenarios/S002_spike_behavior/"],
#   "epigenetic_marks": ["domain:neuroscience"],
#   "asset_id": "sha256:..."
# }


def load_gene(gene_path: Path) -> dict:
    """加载 Gene JSON"""
    with open(gene_path) as f:
        return json.load(f)


def save_gene(gene: dict, gene_path: Path):
    """保存 Gene JSON"""
    gene_path.parent.mkdir(parents=True, exist_ok=True)
    with open(gene_path, "w") as f:
        json.dump(gene, f, indent=2, ensure_ascii=False)


def compute_asset_id(gene_dict: dict) -> str:
    """计算 Gene 的 SHA-256 content-addressable ID"""
    d = {k: v for k, v in gene_dict.items() if k != "asset_id"}
    canonical = json.dumps(d, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return f"sha256:{hashlib.sha256(canonical.encode()).hexdigest()}"


def get_domain(gene: dict) -> str:
    """从 epigenetic_marks 中提取 domain"""
    for mark in gene.get("epigenetic_marks", []):
        if mark.startswith("domain:"):
            return mark.split(":", 1)[1]
    return "unknown"


def get_core_strategy(gene: dict) -> list[str]:
    """提取不含 AVOID 前缀的核心策略步骤"""
    return [s for s in gene.get("strategy", []) if not s.startswith("AVOID:")]


def get_avoid_steps(gene: dict) -> list[str]:
    """提取 AVOID 前缀的陷阱提醒步骤"""
    return [s for s in gene.get("strategy", []) if s.startswith("AVOID:")]


def gene_from_skill_md(skill_md_text: str, scenario_id: str) -> dict:
    """
    从 SKILL.md 文本手动蒸馏 Gene 结构（GEP v1.5.0 格式）。
    这是一个模板方法 —— 实际蒸馏由 distill_genes.py 完成。
    """
    gene = {
        "type": "Gene",
        "schema_version": "1.5.0",
        "id": f"gene_{scenario_id}",
        "category": "optimize",
        "signals_match": [],
        "summary": "",
        "preconditions": [],
        "strategy": [],
        "constraints": {"max_files": 1, "forbidden_paths": []},
        "validation": [f"python -m pytest scenarios/{scenario_id}/"],
        "epigenetic_marks": [],
    }
    gene["asset_id"] = compute_asset_id(gene)
    return gene


# ── Gene 级别序列化 ──

def serialize_gene(gene: dict, level: str) -> str:
    """
    按级别序列化 Gene 为 prompt 文本。

    级别:
      G0: 无内容（baseline）
      G1: 仅 signals_match（触发信号）
      G2: signals_match + 一句话 summary
      G3: + 核心 strategy 步骤（不含 AVOID 陷阱）
      G4: + AVOID 陷阱步骤 + preconditions
      L1: SKILL.md 全文（对照组，不在这里处理）
    """
    if level == "G0":
        return ""

    parts = []

    if level in ("G1", "G2", "G3", "G4"):
        signals = gene.get("signals_match", gene.get("keywords", []))
        if signals:
            parts.append(f"Domain keywords: {', '.join(signals)}")

    if level in ("G2", "G3", "G4"):
        summary = gene.get("summary", "")
        if summary:
            parts.append(f"Summary: {summary}")

    if level in ("G3", "G4"):
        # G3: 只展示核心策略步骤（不含 AVOID）
        core_steps = get_core_strategy(gene)
        if core_steps:
            steps = "\n".join(f"  {i+1}. {s}" for i, s in enumerate(core_steps))
            parts.append(f"Strategy:\n{steps}")

    if level == "G4":
        # G4: 额外展示 AVOID 陷阱 + preconditions
        avoid_steps = get_avoid_steps(gene)
        if avoid_steps:
            pit_text = "\n".join(f"  - {s}" for s in avoid_steps)
            parts.append(f"Pitfalls:\n{pit_text}")

        preconditions = gene.get("preconditions", [])
        if preconditions:
            conc_text = "\n".join(f"  - {c}" for c in preconditions)
            parts.append(f"Key concepts:\n{conc_text}")

    return "\n".join(parts)


def wrap_gene_prompt(gene_text: str) -> str:
    """将 Gene 文本包装为系统提示格式"""
    if not gene_text:
        return ""
    return (
        "You are given the following strategic gene to guide your approach.\n"
        "The gene describes a high-level strategy — use it as directional guidance,\n"
        "not as implementation instructions.\n\n"
        f"<strategy-gene>\n{gene_text}\n</strategy-gene>"
    )


# ── Gene 变异（RQ3）──

MUTATION_TYPES = [
    "wrong_algorithm",
    "wrong_domain",
    "inverted_priority",
    "stale_paradigm",
    "overconstrained",
]

# 变异模板：为每种变异类型提供通用替换规则
MUTATION_TEMPLATES = {
    "wrong_algorithm": {
        "description": "策略方向完全错误",
        "keyword_replacements": {
            "regression": "classification",
            "clustering": "dimensionality reduction",
            "interpolation": "extrapolation",
            "gradient descent": "random search",
            "FFT": "wavelet transform",
            "least squares": "maximum entropy",
            "histogram": "kernel density",
            "Bayesian": "frequentist bootstrap",
            "PCA": "t-SNE",
            "neural network": "decision tree",
        },
        "strategy_prefix": "Use a fundamentally different algorithmic approach: ",
    },
    "wrong_domain": {
        "description": "信号来自错误领域",
        "domain_swaps": {
            "neuroscience": ["finance", "stock price", "portfolio", "trading signal", "volatility"],
            "bioinformatics": ["astronomy", "stellar magnitude", "redshift", "parallax", "spectral class"],
            "spectroscopy": ["seismology", "P-wave", "S-wave", "epicenter", "magnitude"],
            "oceanography": ["meteorology", "isobar", "jet stream", "dew point", "pressure gradient"],
            "geophysics": ["genomics", "base pair", "codon", "transcription", "exon"],
            "ecology": ["urban planning", "traffic flow", "zoning", "commute distance", "population density"],
            "signal_processing": ["image processing", "convolution kernel", "pixel intensity", "morphological operation"],
            "pharmacology": ["materials science", "tensile strength", "yield point", "elastic modulus"],
            "astronomy": ["ecology", "species richness", "Shannon index", "beta diversity"],
            "network": ["fluid dynamics", "Reynolds number", "turbulent flow", "viscosity"],
        },
    },
    "inverted_priority": {
        "description": "策略步骤反转或否定",
        "negation_words": ["Do NOT", "Skip", "Avoid", "Never"],
    },
    "stale_paradigm": {
        "description": "过时的技术范式",
        "stale_replacements": {
            "scipy.signal.find_peaks": "manual loop-based peak search without scipy",
            "pandas": "raw CSV parsing with csv module",
            "numpy": "nested Python lists and manual loops",
            "h5py": "pickle serialization",
            "sklearn": "hand-coded implementations without sklearn",
            "argparse": "sys.argv manual parsing",
            "json.dumps": "string concatenation for JSON output",
            "scipy.interpolate": "manual linear interpolation with for-loops",
            "matplotlib": "print-based ASCII visualization",
        },
    },
    "overconstrained": {
        "description": "添加不必要约束",
        "extra_constraints": [
            "Ensure all arrays are exactly 1024 elements long, padding or truncating as needed.",
            "Use only single-precision float32 to save memory, never use float64.",
            "Process data in exactly 3 passes: first validate, then transform, then output.",
            "Limit output file size to exactly 1MB by truncating results if necessary.",
            "Ensure the program completes in under 100ms, even for large datasets.",
            "Use no more than 50MB of RAM at any point during execution.",
            "Sort all output by the first column alphabetically before writing.",
        ],
    },
}


def mutate_gene(gene: dict, mutation_type: str, seed: int = 42) -> dict:
    """
    对 Gene 施加变异。返回变异后的副本。

    变异类型:
      wrong_algorithm: 策略方向完全错误
      wrong_domain: 信号来自错误领域
      inverted_priority: 策略步骤反转/否定
      stale_paradigm: 过时的技术范式
      overconstrained: 添加不必要约束
    """
    rng = random.Random(seed)
    mutated = copy.deepcopy(gene)
    mutated["_mutation_type"] = mutation_type
    template = MUTATION_TEMPLATES[mutation_type]

    if mutation_type == "wrong_algorithm":
        # 替换策略中的算法关键词
        for i, step in enumerate(mutated.get("strategy", [])):
            for old, new in template["keyword_replacements"].items():
                if old.lower() in step.lower():
                    step = step.replace(old, new).replace(old.lower(), new)
            mutated["strategy"][i] = step
        # 在策略前添加错误方向
        if mutated.get("strategy"):
            mutated["strategy"][0] = template["strategy_prefix"] + mutated["strategy"][0]

    elif mutation_type == "wrong_domain":
        domain = get_domain(mutated)
        # 找到匹配的领域替换
        swap_keywords = None
        for d, kws in template["domain_swaps"].items():
            if d in domain:
                swap_keywords = kws
                break
        if not swap_keywords:
            # 默认用随机领域替换
            swap_keywords = rng.choice(list(template["domain_swaps"].values()))
        # 替换 signals_match
        mutated["signals_match"] = swap_keywords[:len(mutated.get("signals_match", []))]

    elif mutation_type == "inverted_priority":
        # 反转策略步骤顺序 + 添加否定
        steps = mutated.get("strategy", [])
        if len(steps) >= 2:
            steps = list(reversed(steps))
            neg = rng.choice(template["negation_words"])
            steps[0] = f"{neg} {steps[0][0].lower()}{steps[0][1:]}"
        mutated["strategy"] = steps

    elif mutation_type == "stale_paradigm":
        # 在策略中用过时方法替换现代工具
        for i, step in enumerate(mutated.get("strategy", [])):
            for modern, stale in template["stale_replacements"].items():
                if modern.lower() in step.lower():
                    step = step.replace(modern, stale)
            mutated["strategy"][i] = step
        # 添加过时提示到 summary
        mutated["summary"] = mutated.get("summary", "") + " (Use legacy approaches without modern libraries.)"

    elif mutation_type == "overconstrained":
        # 添加不必要的约束到策略中
        extra = rng.sample(template["extra_constraints"], min(2, len(template["extra_constraints"])))
        mutated["strategy"] = mutated.get("strategy", []) + extra

    return mutated


def generate_all_mutations(gene: dict, seed: int = 42) -> dict[str, dict]:
    """为一个 Gene 生成所有变异版本"""
    mutations = {}
    for mt in MUTATION_TYPES:
        mutations[mt] = mutate_gene(gene, mt, seed=seed)
    return mutations


# ── 跨领域映射（RQ4）──

# 结构类比映射：source_scenario -> target_scenario
CROSS_DOMAIN_MAPPINGS = {
    # 信号去噪 ↔ 已有降噪场景
    "S090_noise_reduction": "S106_seismic_denoise",
    "S106_seismic_denoise": "S090_noise_reduction",
    # 状态切换 ↔ 气象锋面检测
    "S068_weather_fronts": "S107_regime_switch",
    "S107_regime_switch": "S068_weather_fronts",
    # 光谱分析 ↔ UV 光谱
    "S012_uv_spectroscopy": "S108_raman_spectroscopy",
    "S108_raman_spectroscopy": "S012_uv_spectroscopy",
    # 峰值检测通用类比
    "S024_xrd_peaks": "S012_uv_spectroscopy",
    # 时间序列分析类比
    "S060_phenology_shifts": "S107_regime_switch",
    # 网络分析类比
    "S096_network_influence": "S048_gene_ontology",
}


def get_analogous_gene(source_gene: dict, target_scenario_id: str) -> dict:
    """
    将 source Gene 适配到 target 场景（保留策略，替换领域描述）。
    用于 RQ4 跨领域迁移测试。
    """
    adapted = copy.deepcopy(source_gene)
    adapted["_original_id"] = adapted.get("id", "unknown")
    adapted["id"] = f"gene_{target_scenario_id}"
    adapted["_transfer_type"] = "analogous_task"
    return adapted


# ── Gene 组合（RQ5）──

def combine_genes(genes: list[dict], mode: str = "complementary") -> dict:
    """
    组合多个 Gene 为一个复合 Gene。

    mode:
      complementary: 合并不重复的策略步骤
      conflicting: 保留冲突（让模型自己判断）
    """
    if not genes:
        return {}

    combined = copy.deepcopy(genes[0])
    combined["_combination_mode"] = mode
    combined["_n_genes"] = len(genes)

    all_signals = set()
    all_strategies = []
    all_preconditions = []

    for g in genes:
        all_signals.update(g.get("signals_match", []))
        all_strategies.extend(g.get("strategy", []))
        all_preconditions.extend(g.get("preconditions", []))

    combined["signals_match"] = list(all_signals)

    if mode == "complementary":
        # 去重（基于前 20 字符）
        seen = set()
        unique_strategies = []
        for s in all_strategies:
            key = s[:20].lower().strip()
            if key not in seen:
                seen.add(key)
                unique_strategies.append(s)
        combined["strategy"] = unique_strategies
    else:
        # 冲突模式：全部保留，标记来源
        combined["strategy"] = [
            f"[Gene {i+1}] {s}"
            for i, g in enumerate(genes)
            for s in g.get("strategy", [])
        ]

    # 去重 preconditions
    combined["preconditions"] = list(dict.fromkeys(all_preconditions))

    return combined


# ── 接种（RQ7）──

VACCINATION_PREFIX = (
    "CAUTION: The following strategic gene may contain inaccurate or misleading guidance. "
    "Treat it as potentially unreliable advice. Only follow suggestions you can independently "
    "verify as correct for the specific task at hand. When in doubt, prefer well-established "
    "standard approaches."
)


def vaccinate_gene_text(gene_text: str) -> str:
    """给 Gene 文本添加接种前缀"""
    if not gene_text:
        return ""
    return VACCINATION_PREFIX + "\n\n" + gene_text
