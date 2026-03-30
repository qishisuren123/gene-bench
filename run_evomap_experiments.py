#!/usr/bin/env python3
"""
EvoMap 双回路实验：测试记忆模式 vs 探索模式对代码生成的影响。

基于 evomap 2.0 架构：
  - 记忆模式（过去导向）: signals, failures, experience
  - 探索模式（未来导向）: persona, objective, direction, target_profile

三个核心实验：
  EX8: Memory vs Exploration — 记忆模式 vs 探索模式的引导效果
  EX9: Failure-Guided Learning — 失败案例是否比正确策略更有效
  EX10: Persona Spectrum — 角色定位的方向与精度如何影响生成

用法:
    python run_evomap_experiments.py --experiment ex8 \
        --gemini-key "$GEMINI_API_KEY"

    python run_evomap_experiments.py --experiment all \
        --gemini-key "$GEMINI_API_KEY"
"""

import argparse
import json
import os
import sys
import time
from pathlib import Path
from dataclasses import dataclass, asdict
from collections import Counter

# 复用已有模块
sys.path.insert(0, str(Path(__file__).parent))
from run_gene_bench import (
    MODEL_REGISTRY, SCENARIOS_DIR, GENES_DIR, DATA_DIR,
    call_llm, extract_python_code, evaluate_code, load_gene_for_trial,
    TEMPERATURE, MAX_TOKENS, EVAL_TIMEOUT,
)
from gene_builder import load_gene, serialize_gene

ROOT = Path(__file__).parent

# ── 场景选择 ──
# 选取对 Gene 敏感的场景（排除 always-pass 和 always-fail）
GENE_SENSITIVE_SCENARIOS = [
    "S012_uv_spectroscopy",     # 高方差，Gene 级别影响极大
    "S017_ctd_ocean",            # Gene 会毒害的场景
    "S105_community_detection",  # 高方差
    "S113_inventory_reorder",    # Gene 能救的场景
    "S101_climate_attribution",  # 策略主导型
    "S026_earthquake_catalog",   # Skill 会毒害
    "S007_data_viz",             # 变异敏感
    "S005_protein_parse",        # 组合敏感
    "S030_fossil_morpho",        # 中等难度
    "S011_particle_physics",     # 中等难度
    "S033_exoplanet_transit",    # 新增领域
    "S090_noise_reduction",      # 信号处理
    "S096_network_influence",    # 图分析
    "S112_midi_chords",          # 音乐
    "S103_instrumental_variable",# 因果推断
]


# ── 领域信息（persona/signals 生成用）──
DOMAIN_INFO = {
    "S012_uv_spectroscopy": {
        "domain": "spectroscopy",
        "expert": "analytical chemist specializing in UV-Vis spectroscopy",
        "adjacent": "infrared spectroscopy researcher",
        "wrong": "machine learning engineer working on NLP",
        "failure_patterns": [
            "Forgetting to convert min-distance from nm to data point indices — assumes 1nm spacing",
            "Using raw peak_widths output without converting back to wavelength units for FWHM",
            "Setting min_height too low and detecting noise as peaks",
            "Not handling the case where zero peaks are detected for a sample",
        ],
        "signals": ["absorbance", "wavelength", "peak detection", "FWHM", "Beer-Lambert", "baseline correction", "spectral resolution", "molar absorptivity"],
    },
    "S017_ctd_ocean": {
        "domain": "oceanography",
        "expert": "physical oceanographer specializing in CTD profiling",
        "adjacent": "marine biologist studying plankton distribution",
        "wrong": "financial analyst working on stock market prediction",
        "failure_patterns": [
            "Mishandling pressure-to-depth conversion without accounting for latitude",
            "Not applying the UNESCO equation of state for seawater density",
            "Ignoring the salinity effect on sound speed calculation",
            "Using linear interpolation where the thermocline requires higher-order methods",
        ],
        "signals": ["CTD", "pressure", "salinity", "temperature profile", "density", "mixed layer depth", "thermocline", "halocline"],
    },
    "S105_community_detection": {
        "domain": "graph analysis",
        "expert": "network scientist specializing in community structure analysis",
        "adjacent": "social scientist studying organizational networks",
        "wrong": "audio engineer working on sound processing",
        "failure_patterns": [
            "Label propagation oscillating without convergence — synchronous updates cause flip-flopping",
            "Computing modularity Q incorrectly — forgetting the 1/2m normalization factor",
            "Not handling disconnected components as separate communities",
            "Allowing label propagation to run indefinitely without a maximum iteration limit",
        ],
        "signals": ["modularity", "Louvain", "label propagation", "adjacency matrix", "community structure", "degree distribution", "clustering coefficient", "betweenness"],
    },
    "S113_inventory_reorder": {
        "domain": "supply chain optimization",
        "expert": "operations research specialist in inventory management",
        "adjacent": "logistics planner for warehouse operations",
        "wrong": "astrophysicist studying stellar evolution",
        "failure_patterns": [
            "Using the EOQ formula without accounting for lead time demand variability",
            "Setting safety stock based on average demand instead of demand standard deviation",
            "Not considering the service level z-score when computing reorder points",
            "Ignoring the relationship between order frequency and holding costs",
        ],
        "signals": ["EOQ", "reorder point", "safety stock", "lead time", "demand variability", "service level", "holding cost", "order cost"],
    },
    "S101_climate_attribution": {
        "domain": "climate science",
        "expert": "climate scientist specializing in detection and attribution studies",
        "adjacent": "atmospheric physicist studying radiative forcing",
        "wrong": "database administrator working on SQL optimization",
        "failure_patterns": [
            "Not normalizing forcing factors before regression, causing coefficient scale issues",
            "Computing attribution fractions from raw coefficients instead of absolute contributions",
            "Forgetting to add an intercept term in the regression model",
            "Using OLS when forcing factors are highly correlated — Ridge is more stable",
        ],
        "signals": ["attribution", "forcing", "regression", "GHG", "solar", "volcanic", "aerosol", "radiative balance"],
    },
    "S026_earthquake_catalog": {
        "domain": "seismology",
        "expert": "seismologist specializing in earthquake catalog analysis",
        "adjacent": "structural engineer studying building response to seismic waves",
        "wrong": "botanist studying plant growth patterns",
        "failure_patterns": [
            "Treating magnitude as a linear scale — it's logarithmic (each unit = 10x amplitude)",
            "Not handling catalog completeness — small events are under-reported",
            "Incorrect distance calculation — must use Haversine for lat/lon coordinates",
            "Forgetting to apply the Gutenberg-Richter law for frequency-magnitude distribution",
        ],
        "signals": ["magnitude", "epicenter", "depth", "Gutenberg-Richter", "b-value", "Haversine", "catalog completeness", "seismic moment"],
    },
    "S007_data_viz": {
        "domain": "data visualization",
        "expert": "data visualization specialist with expertise in scientific plotting",
        "adjacent": "UX designer working on dashboard interfaces",
        "wrong": "embedded systems programmer working on firmware",
        "failure_patterns": [
            "Choosing the wrong chart type for the data structure — scatter for categorical data",
            "Not setting proper figure DPI for publication-quality output",
            "Ignoring colorblind-safe palettes when designing multi-series plots",
            "Hard-coding axis limits instead of computing from data range with padding",
        ],
        "signals": ["matplotlib", "figure", "axes", "colormap", "legend", "annotation", "publication quality", "subplot"],
    },
    "S005_protein_parse": {
        "domain": "bioinformatics",
        "expert": "structural bioinformatician specializing in protein data analysis",
        "adjacent": "computational chemist studying molecular dynamics",
        "wrong": "civil engineer designing bridge structures",
        "failure_patterns": [
            "Assuming fixed-width columns in PDB format are always present — some optional",
            "Not handling alternate conformations (altLoc) correctly",
            "Treating B-factors as quality scores without understanding they're temperature factors",
            "Forgetting to convert PDB coordinates from Angstroms when computing distances",
        ],
        "signals": ["PDB", "ATOM", "residue", "chain", "B-factor", "coordinates", "secondary structure", "HETATM"],
    },
    "S030_fossil_morpho": {
        "domain": "paleontology",
        "expert": "paleontologist specializing in quantitative morphometric analysis",
        "adjacent": "evolutionary biologist studying phenotypic variation",
        "wrong": "telecommunications engineer working on signal routing",
        "failure_patterns": [
            "Using Euclidean distance on raw landmark coordinates without Procrustes alignment",
            "Not accounting for size in shape analysis — must separate size and shape components",
            "Applying PCA to raw coordinates instead of to Procrustes-aligned residuals",
            "Forgetting to check for landmark outliers before Procrustes superimposition",
        ],
        "signals": ["morphometrics", "landmark", "Procrustes", "PCA", "shape space", "centroid size", "allometry", "geometric morphometrics"],
    },
    "S011_particle_physics": {
        "domain": "particle physics",
        "expert": "experimental particle physicist specializing in data analysis at colliders",
        "adjacent": "nuclear physicist studying heavy-ion collisions",
        "wrong": "real estate analyst working on property valuations",
        "failure_patterns": [
            "Not accounting for detector acceptance and efficiency in cross-section calculations",
            "Using wrong kinematic variables — transverse momentum pT vs total momentum p",
            "Ignoring background subtraction when extracting signal peaks",
            "Computing invariant mass without proper four-vector algebra",
        ],
        "signals": ["invariant mass", "transverse momentum", "cross-section", "luminosity", "background subtraction", "histogram", "binning", "significance"],
    },
    "S033_exoplanet_transit": {
        "domain": "astrophysics",
        "expert": "astrophysicist specializing in exoplanet transit photometry",
        "adjacent": "stellar astronomer studying variable stars",
        "wrong": "marine biologist studying whale migration",
        "failure_patterns": [
            "Using a box-shaped transit model instead of proper limb-darkening curves",
            "Not detrending the light curve for systematic effects before fitting",
            "Computing transit depth without accounting for flux normalization",
            "Ignoring the ingress/egress shape which constrains planet-to-star radius ratio",
        ],
        "signals": ["transit", "light curve", "limb darkening", "epoch", "period", "depth", "flux", "phase folding"],
    },
    "S090_noise_reduction": {
        "domain": "signal processing",
        "expert": "signal processing engineer specializing in noise reduction algorithms",
        "adjacent": "acoustics researcher studying room impulse responses",
        "wrong": "graphic designer working on typography",
        "failure_patterns": [
            "Applying frequency-domain filtering without proper windowing, causing spectral leakage",
            "Using a fixed noise threshold instead of adaptive SNR-based estimation",
            "Forgetting overlap-add or overlap-save when processing signals in blocks",
            "Choosing filter order too high, introducing ringing artifacts in time domain",
        ],
        "signals": ["FFT", "spectral subtraction", "Wiener filter", "SNR", "window function", "overlap-add", "noise floor", "bandpass"],
    },
    "S096_network_influence": {
        "domain": "network science",
        "expert": "network scientist specializing in influence maximization",
        "adjacent": "sociologist studying information diffusion",
        "wrong": "pastry chef working on recipe optimization",
        "failure_patterns": [
            "Using degree centrality alone — high-degree nodes may be clustered together",
            "Not accounting for network structure in cascade simulation",
            "Ignoring the diminishing returns of adding nodes from the same community",
            "Computing influence spread without proper Monte Carlo averaging",
        ],
        "signals": ["centrality", "influence spread", "cascade", "seed set", "greedy algorithm", "IC model", "network topology", "k-core"],
    },
    "S112_midi_chords": {
        "domain": "music informatics",
        "expert": "music information retrieval researcher specializing in harmonic analysis",
        "adjacent": "audio engineer working on music production",
        "wrong": "geologist studying tectonic plate movements",
        "failure_patterns": [
            "Treating MIDI note numbers as frequencies — they're integer indices, not Hz",
            "Not grouping simultaneous note-on events within a timing tolerance window",
            "Classifying chords using only pitch class without considering inversions",
            "Ignoring note velocity when determining chord boundaries",
        ],
        "signals": ["MIDI", "note-on", "pitch class", "chord recognition", "interval", "velocity", "tick", "tempo"],
    },
    "S103_instrumental_variable": {
        "domain": "econometrics",
        "expert": "econometrician specializing in causal inference with instrumental variables",
        "adjacent": "biostatistician running clinical trials",
        "wrong": "animation artist working on character design",
        "failure_patterns": [
            "Using a weak instrument — the F-statistic on first stage should be >10",
            "Not checking the exclusion restriction — instrument may affect outcome directly",
            "Applying 2SLS without properly staging: first regress X on Z, then Y on X-hat",
            "Ignoring heteroscedasticity in standard errors after IV estimation",
        ],
        "signals": ["instrumental variable", "2SLS", "endogeneity", "first stage", "exclusion restriction", "Hausman test", "weak instrument", "LATE"],
    },
}


# ── Prompt 模板 ──

# --- EX8: Memory vs Exploration ---

def make_memory_signals_prompt(scenario_id: str) -> str:
    """记忆模式 - 仅信号/关键词（过去导向）"""
    info = DOMAIN_INFO.get(scenario_id, {})
    signals = info.get("signals", [])
    if not signals:
        # 回退到 gene keywords
        gene_path = GENES_DIR / f"{scenario_id}.json"
        if gene_path.exists():
            gene = json.loads(gene_path.read_text())
            signals = gene.get("keywords", [])

    return (
        "Based on accumulated experience with similar tasks, these domain signals "
        "have been identified as critical indicators of solution quality:\n\n"
        f"<memory-signals>\n"
        f"Relevant signals: {', '.join(signals)}\n"
        f"</memory-signals>\n\n"
        "Use these signals to orient your approach. They reflect patterns "
        "that consistently appear in successful solutions."
    )


def make_memory_failures_prompt(scenario_id: str) -> str:
    """记忆模式 - 失败经验（过去导向的负面知识）"""
    info = DOMAIN_INFO.get(scenario_id, {})
    failures = info.get("failure_patterns", [])
    if not failures:
        return ""

    failure_text = "\n".join(f"  - {f}" for f in failures)
    return (
        "Based on analysis of past failed attempts at similar tasks, "
        "these failure patterns have been documented:\n\n"
        "<memory-failures>\n"
        f"Common failure patterns:\n{failure_text}\n\n"
        "Each of these has caused solution failures in >30% of past attempts.\n"
        "</memory-failures>\n\n"
        "Learn from these failures. Avoid these specific pitfalls in your implementation."
    )


def make_memory_experience_prompt(scenario_id: str) -> str:
    """记忆模式 - 完整经验叙述（过去导向的正+负知识）"""
    info = DOMAIN_INFO.get(scenario_id, {})
    signals = info.get("signals", [])
    failures = info.get("failure_patterns", [])
    domain = info.get("domain", "this domain")

    # 加载 gene 的 strategy
    gene_path = GENES_DIR / f"{scenario_id}.json"
    strategy = []
    if gene_path.exists():
        gene = json.loads(gene_path.read_text())
        strategy = gene.get("strategy", [])

    failure_text = "\n".join(f"  - {f}" for f in failures[:3])
    strategy_text = "\n".join(f"  - {s}" for s in strategy[:3])

    return (
        f"Drawing from accumulated experience in {domain} tasks:\n\n"
        "<memory-experience>\n"
        f"Domain signals that matter: {', '.join(signals[:5])}\n\n"
        f"What worked in past successful solutions:\n{strategy_text}\n\n"
        f"What caused past failures:\n{failure_text}\n\n"
        "This experience was compiled from multiple iterations of similar tasks.\n"
        "</memory-experience>\n\n"
        "Use this experience to guide your approach. Trust patterns that "
        "consistently appear across solutions."
    )


def make_exploration_persona_prompt(scenario_id: str) -> str:
    """探索模式 - 专家角色设定（未来导向）"""
    info = DOMAIN_INFO.get(scenario_id, {})
    expert = info.get("expert", "domain expert")

    return (
        f"You are a {expert} with over 15 years of experience. "
        f"You have published extensively in this field and regularly solve "
        f"computational problems in your domain.\n\n"
        f"Approach this task as you would approach a real research problem "
        f"in your field — with rigor, domain expertise, and attention to "
        f"methodology that reflects your deep understanding."
    )


def make_exploration_objective_prompt(scenario_id: str) -> str:
    """探索模式 - 明确目标（未来导向）"""
    # 从 task.md 提取核心目标
    task_path = SCENARIOS_DIR / scenario_id / "task.md"
    task_desc = task_path.read_text().strip() if task_path.exists() else ""

    # 取第一句作为核心目标
    first_line = task_desc.split("\n")[0] if task_desc else "Complete the task"

    return (
        "Your objective is clearly defined:\n\n"
        "<exploration-objective>\n"
        f"Primary goal: {first_line}\n\n"
        "Success criteria:\n"
        "  1. All test cases must pass\n"
        "  2. Code must be self-contained and production-quality\n"
        "  3. Edge cases must be handled gracefully\n"
        "  4. Output format must match specifications exactly\n"
        "</exploration-objective>\n\n"
        "Focus relentlessly on meeting these criteria. "
        "Every design decision should serve the objective."
    )


def make_exploration_direction_prompt(scenario_id: str) -> str:
    """探索模式 - 策略方向（未来导向）"""
    gene_path = GENES_DIR / f"{scenario_id}.json"
    if not gene_path.exists():
        return ""
    gene = json.loads(gene_path.read_text())
    summary = gene.get("summary", "")

    return (
        "Strategic direction for your exploration:\n\n"
        "<exploration-direction>\n"
        f"Recommended approach: {summary}\n\n"
        "This direction has been identified as the most promising path "
        "for tasks of this type. Explore solutions that align with this guidance, "
        "but adapt as needed based on the specific requirements.\n"
        "</exploration-direction>"
    )


def make_exploration_full_prompt(scenario_id: str) -> str:
    """探索模式 - 完整探索配置（persona + objective + direction + target_profile）"""
    info = DOMAIN_INFO.get(scenario_id, {})
    expert = info.get("expert", "domain expert")
    domain = info.get("domain", "this domain")
    signals = info.get("signals", [])

    gene_path = GENES_DIR / f"{scenario_id}.json"
    summary = ""
    if gene_path.exists():
        gene = json.loads(gene_path.read_text())
        summary = gene.get("summary", "")

    task_path = SCENARIOS_DIR / scenario_id / "task.md"
    task_desc = task_path.read_text().strip() if task_path.exists() else ""
    first_line = task_desc.split("\n")[0] if task_desc else "Complete the task"

    return (
        f"<exploration-profile>\n"
        f"Persona: You are a {expert}\n"
        f"Objective: {first_line}\n"
        f"Direction: {summary}\n"
        f"Target profile: A solution demonstrating expertise in {domain}, "
        f"utilizing established methodology around {', '.join(signals[:4])}\n"
        f"</exploration-profile>\n\n"
        f"Execute this exploration with full domain expertise. "
        f"Your solution should reflect the analytical rigor of a published researcher."
    )


# --- EX9: Failure-Guided Learning ---

def make_correct_strategy_prompt(scenario_id: str) -> str:
    """仅正确策略（从 gene 提取）"""
    gene_path = GENES_DIR / f"{scenario_id}.json"
    if not gene_path.exists():
        return ""
    gene = json.loads(gene_path.read_text())
    strategy = gene.get("strategy", [])

    steps = "\n".join(f"  {i+1}. {s}" for i, s in enumerate(strategy))
    return (
        "Here is the correct approach to solve this task:\n\n"
        "<correct-strategy>\n"
        f"{steps}\n"
        "</correct-strategy>\n\n"
        "Follow this strategy step-by-step."
    )


def make_failure_warnings_prompt(scenario_id: str) -> str:
    """仅失败警告（负面知识）"""
    info = DOMAIN_INFO.get(scenario_id, {})
    failures = info.get("failure_patterns", [])
    if not failures:
        return ""

    failure_text = "\n".join(f"  {i+1}. {f}" for i, f in enumerate(failures))
    return (
        "WARNING: These are the most common mistakes that cause solutions to fail:\n\n"
        "<failure-warnings>\n"
        f"{failure_text}\n"
        "</failure-warnings>\n\n"
        "Each of these mistakes has been observed in multiple failed attempts. "
        "Make sure your solution avoids ALL of these pitfalls."
    )


def make_failure_then_strategy_prompt(scenario_id: str) -> str:
    """先给失败案例，再给正确策略"""
    failures = make_failure_warnings_prompt(scenario_id)
    strategy = make_correct_strategy_prompt(scenario_id)
    if not failures or not strategy:
        return failures + strategy

    return (
        "First, understand what NOT to do:\n\n"
        f"{failures}\n\n"
        "Now, here is the recommended approach:\n\n"
        f"{strategy}"
    )


def make_strategy_then_failure_prompt(scenario_id: str) -> str:
    """先给正确策略，再给失败案例（顺序对调）"""
    failures = make_failure_warnings_prompt(scenario_id)
    strategy = make_correct_strategy_prompt(scenario_id)
    if not failures or not strategy:
        return strategy + failures

    return (
        "Here is the recommended approach:\n\n"
        f"{strategy}\n\n"
        "And here are critical mistakes to avoid:\n\n"
        f"{failures}"
    )


# --- EX10: Persona Spectrum ---

def make_expert_exact_prompt(scenario_id: str) -> str:
    """精确领域专家 persona"""
    info = DOMAIN_INFO.get(scenario_id, {})
    expert = info.get("expert", "domain expert")
    return f"You are a {expert}. Solve this task using your specialized expertise."


def make_expert_adjacent_prompt(scenario_id: str) -> str:
    """相邻领域专家 persona"""
    info = DOMAIN_INFO.get(scenario_id, {})
    adjacent = info.get("adjacent", "related domain expert")
    return f"You are a {adjacent}. Apply your transferable skills to solve this task."


def make_expert_wrong_prompt(scenario_id: str) -> str:
    """错误领域专家 persona"""
    info = DOMAIN_INFO.get(scenario_id, {})
    wrong = info.get("wrong", "unrelated domain expert")
    return f"You are a {wrong}. Apply your analytical skills to solve this task."


def make_generic_senior_prompt(scenario_id: str) -> str:
    """通用高级工程师 persona"""
    return (
        "You are a senior software engineer with 20 years of experience. "
        "You excel at understanding new domains quickly and writing clean, correct code."
    )


def make_novice_prompt(scenario_id: str) -> str:
    """新手 persona"""
    info = DOMAIN_INFO.get(scenario_id, {})
    domain = info.get("domain", "this domain")
    return (
        f"You are a programming student who is learning about {domain} for the first time. "
        f"Be very careful and methodical. Double-check every step of your solution."
    )


# --- EX11: 负面知识密度（Failure Density） ---

def make_n_failures_prompt(scenario_id: str, n: int) -> str:
    """给 n 条失败警告"""
    info = DOMAIN_INFO.get(scenario_id, {})
    failures = info.get("failure_patterns", [])
    selected = failures[:n] if n <= len(failures) else failures
    if not selected:
        return ""

    failure_text = "\n".join(f"  {i+1}. {f}" for i, f in enumerate(selected))
    return (
        f"CRITICAL: Avoid these {len(selected)} documented failure patterns:\n\n"
        f"<failure-patterns>\n{failure_text}\n</failure-patterns>"
    )


# ── Trial 配置 ──

@dataclass
class EvoTrialConfig:
    scenario_id: str
    model: str
    experiment: str  # ex8, ex9, ex10, ex11
    condition: str
    run_id: int = 0

    @property
    def trial_key(self) -> str:
        return f"{self.scenario_id}__{self.model}__{self.experiment}__{self.condition}__r{self.run_id}"


# ── EX8 条件映射 ──
EX8_CONDITIONS = {
    "none":                 lambda sid: "",
    "memory_signals":       make_memory_signals_prompt,
    "memory_failures":      make_memory_failures_prompt,
    "memory_experience":    make_memory_experience_prompt,
    "exploration_persona":  make_exploration_persona_prompt,
    "exploration_objective": make_exploration_objective_prompt,
    "exploration_direction": make_exploration_direction_prompt,
    "exploration_full":     make_exploration_full_prompt,
    "gene_g3":              lambda sid: _get_gene_g3_prompt(sid),
}

# EX9 条件映射
EX9_CONDITIONS = {
    "none":                lambda sid: "",
    "correct_strategy":    make_correct_strategy_prompt,
    "failure_warnings":    make_failure_warnings_prompt,
    "failure_first":       make_failure_then_strategy_prompt,
    "strategy_first":      make_strategy_then_failure_prompt,
}

# EX10 条件映射
EX10_CONDITIONS = {
    "none":            lambda sid: "",
    "expert_exact":    make_expert_exact_prompt,
    "expert_adjacent": make_expert_adjacent_prompt,
    "expert_wrong":    make_expert_wrong_prompt,
    "generic_senior":  make_generic_senior_prompt,
    "novice":          make_novice_prompt,
}

# EX11 条件映射
EX11_CONDITIONS = {
    "0_failures":  lambda sid: "",
    "1_failure":   lambda sid: make_n_failures_prompt(sid, 1),
    "2_failures":  lambda sid: make_n_failures_prompt(sid, 2),
    "3_failures":  lambda sid: make_n_failures_prompt(sid, 3),
    "4_failures":  lambda sid: make_n_failures_prompt(sid, 4),
}


def _get_gene_g3_prompt(scenario_id: str) -> str:
    """获取标准 G3 Gene prompt（作为对照组）"""
    gene_path = GENES_DIR / f"{scenario_id}.json"
    if not gene_path.exists():
        return ""
    gene = json.loads(gene_path.read_text())
    text = serialize_gene(gene, "G3")
    return (
        "You are given the following strategic gene to guide your approach.\n"
        "The gene describes a high-level strategy — use it as directional guidance,\n"
        "not as implementation instructions.\n\n"
        f"<strategy-gene>\n{text}\n</strategy-gene>"
    )


# ── Trial 生成 ──

def generate_ex8_trials(models: list, scenarios: list) -> list:
    """EX8: Memory vs Exploration"""
    trials = []
    for m in models:
        for s in scenarios:
            for cond in EX8_CONDITIONS:
                trials.append(EvoTrialConfig(
                    scenario_id=s, model=m,
                    experiment="ex8", condition=cond,
                ))
    return trials


def generate_ex9_trials(models: list, scenarios: list) -> list:
    """EX9: Failure-Guided Learning"""
    trials = []
    for m in models:
        for s in scenarios:
            for cond in EX9_CONDITIONS:
                trials.append(EvoTrialConfig(
                    scenario_id=s, model=m,
                    experiment="ex9", condition=cond,
                ))
    return trials


def generate_ex10_trials(models: list, scenarios: list) -> list:
    """EX10: Persona Spectrum"""
    trials = []
    for m in models:
        for s in scenarios:
            for cond in EX10_CONDITIONS:
                trials.append(EvoTrialConfig(
                    scenario_id=s, model=m,
                    experiment="ex10", condition=cond,
                ))
    return trials


def generate_ex11_trials(models: list, scenarios: list) -> list:
    """EX11: Failure Density"""
    trials = []
    for m in models:
        for s in scenarios:
            for cond in EX11_CONDITIONS:
                trials.append(EvoTrialConfig(
                    scenario_id=s, model=m,
                    experiment="ex11", condition=cond,
                ))
    return trials


# ── 实验执行 ──

def get_system_prompt(trial: EvoTrialConfig) -> str:
    """根据实验条件生成系统提示"""
    cond_maps = {
        "ex8": EX8_CONDITIONS,
        "ex9": EX9_CONDITIONS,
        "ex10": EX10_CONDITIONS,
        "ex11": EX11_CONDITIONS,
    }
    cond_map = cond_maps.get(trial.experiment, {})
    func = cond_map.get(trial.condition)
    if func:
        return func(trial.scenario_id)
    return ""


def run_evomap_experiment(trials: list, gemini_key: str, yunwu_key: str,
                          output_file: Path, dry_run: bool = False, n_threads: int = 8):
    """执行 evomap 实验（支持多线程并行）"""
    from concurrent.futures import ThreadPoolExecutor, as_completed
    import threading

    write_lock = threading.Lock()
    counter = {"done": 0, "errors": 0, "total": 0}

    print(f"\n{'DRY RUN — ' if dry_run else ''}Running {len(trials)} evomap trials ({n_threads} threads)")
    print(f"Output: {output_file}\n")

    # 加载已完成的 trials
    completed = set()
    if output_file.exists():
        for line in output_file.read_text().strip().split("\n"):
            if line:
                try:
                    completed.add(json.loads(line)["trial_key"])
                except (json.JSONDecodeError, KeyError):
                    pass
        print(f"  Resuming: {len(completed)} trials already completed\n")

    pending = [t for t in trials if t.trial_key not in completed]
    counter["total"] = len(pending)
    print(f"  Pending: {len(pending)} trials\n")

    if dry_run:
        for trial in pending:
            print(f"  {trial.model:16s} {trial.scenario_id:28s} {trial.condition:25s} (dry run)")
        return

    output_file.parent.mkdir(parents=True, exist_ok=True)

    def run_single_trial(trial: EvoTrialConfig) -> None:
        """执行单个 trial（线程安全）"""
        scenario_dir = SCENARIOS_DIR / trial.scenario_id
        task_path = scenario_dir / "task.md"
        if not task_path.exists():
            return

        task_desc = task_path.read_text().strip()
        task_desc += "\n\nWrite a complete, self-contained Python solution. Output ONLY the code inside a single ```python code block. Do not include explanations outside the code block."

        system_prompt = get_system_prompt(trial)

        try:
            api_result = call_llm(trial.model, task_desc, system_prompt, yunwu_key, gemini_key)
        except Exception as e:
            result = {
                "trial_key": trial.trial_key,
                "trial_config": asdict(trial),
                "eval": {"passed": False, "n_pass": 0, "n_total": 0,
                         "pass_rate": 0, "error_type": f"api_error: {e}"},
                "code_length": 0,
                "prompt_tokens": len(system_prompt) // 4,
                "input_tokens": 0, "output_tokens": 0,
            }
            with write_lock:
                with open(output_file, "a") as f:
                    f.write(json.dumps(result, default=str) + "\n")
                counter["errors"] += 1
                counter["done"] += 1
                print(f"  [{counter['done']}/{counter['total']}] {trial.model:16s} {trial.scenario_id:28s} {trial.condition:25s} API ERROR: {e}")
            return

        code = extract_python_code(api_result["response"])
        if not code:
            result = {
                "trial_key": trial.trial_key,
                "trial_config": asdict(trial),
                "eval": {"passed": False, "n_pass": 0, "n_total": 0,
                         "pass_rate": 0, "error_type": "format_error"},
                "code_length": 0,
                "prompt_tokens": len(system_prompt) // 4,
                "input_tokens": api_result.get("input_tokens", 0),
                "output_tokens": api_result.get("output_tokens", 0),
            }
            status_str = "NO CODE"
        else:
            eval_result = evaluate_code(code, scenario_dir)
            result = {
                "trial_key": trial.trial_key,
                "trial_config": asdict(trial),
                "eval": eval_result,
                "code_length": len(code),
                "prompt_tokens": len(system_prompt) // 4,
                "input_tokens": api_result.get("input_tokens", 0),
                "output_tokens": api_result.get("output_tokens", 0),
            }
            if eval_result["passed"]:
                status_str = f"PASS ({eval_result['n_pass']}/{eval_result['n_total']})"
            else:
                status_str = f"FAIL ({eval_result.get('error_type', '?')})"

        with write_lock:
            with open(output_file, "a") as f:
                f.write(json.dumps(result, default=str) + "\n")
            counter["done"] += 1
            print(f"  [{counter['done']}/{counter['total']}] {trial.model:16s} {trial.scenario_id:28s} {trial.condition:25s} {status_str}")

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


# ── CLI ──

def main():
    parser = argparse.ArgumentParser(description="EvoMap 双回路实验")
    parser.add_argument("--experiment", choices=["ex8", "ex9", "ex10", "ex11", "all"],
                        default="all", help="Which experiment to run")
    parser.add_argument("--models", type=str, default="gemini_pro,gemini_flash",
                        help="Comma-separated model list")
    parser.add_argument("--scenarios", type=str, default=None,
                        help="Override scenario list (comma-separated)")
    parser.add_argument("--gemini-key", type=str,
                        default=os.environ.get("GEMINI_API_KEY", ""),
                        help="Gemini API key")
    parser.add_argument("--yunwu-key", type=str,
                        default=os.environ.get("YUNWU_API_KEY", ""),
                        help="yunwu.ai API key")
    parser.add_argument("--dry-run", action="store_true",
                        help="Print trial plan without executing")
    parser.add_argument("--output-dir", type=str, default=str(DATA_DIR),
                        help="Output directory")

    args = parser.parse_args()

    models = [m.strip() for m in args.models.split(",")]
    for m in models:
        if m not in MODEL_REGISTRY:
            parser.error(f"Unknown model: {m}")

    scenarios = (
        [s.strip() for s in args.scenarios.split(",")]
        if args.scenarios
        else GENE_SENSITIVE_SCENARIOS
    )

    output_dir = Path(args.output_dir)
    exp = args.experiment

    all_trials = {}

    if exp in ("ex8", "all"):
        t = generate_ex8_trials(models, scenarios)
        all_trials["ex8"] = t
        print(f"EX8 (Memory vs Exploration): {len(t)} trials")

    if exp in ("ex9", "all"):
        t = generate_ex9_trials(models, scenarios)
        all_trials["ex9"] = t
        print(f"EX9 (Failure-Guided Learning): {len(t)} trials")

    if exp in ("ex10", "all"):
        t = generate_ex10_trials(models, scenarios)
        all_trials["ex10"] = t
        print(f"EX10 (Persona Spectrum): {len(t)} trials")

    if exp in ("ex11", "all"):
        t = generate_ex11_trials(models, scenarios)
        all_trials["ex11"] = t
        print(f"EX11 (Failure Density): {len(t)} trials")

    total = sum(len(t) for t in all_trials.values())
    print(f"\nTotal: {total} trials across {len(all_trials)} experiments")

    if args.dry_run:
        print("\n--- Dry Run Summary ---")
        for name, trials in all_trials.items():
            by_cond = Counter(t.condition for t in trials)
            print(f"\n{name}:")
            for cond, c in sorted(by_cond.items()):
                print(f"  {cond:25s}: {c}")
        return

    # 逐实验执行
    for name, trials in all_trials.items():
        out_file = output_dir / f"evomap_{name}_results.jsonl"
        print(f"\n{'='*60}")
        print(f"Running {name}")
        print(f"{'='*60}")
        run_evomap_experiment(
            trials, args.gemini_key, args.yunwu_key, out_file, args.dry_run
        )

    print(f"\nAll experiments done! Results in {output_dir}/evomap_*.jsonl")


if __name__ == "__main__":
    main()
