#!/usr/bin/env python3
"""
从 SKILL.md 自动蒸馏 Gene JSON 文件（离线版，不调 API）。

解析 SKILL.md 的结构化 Markdown，提取 keywords/summary/strategy/pitfalls/key_concepts。
"""

import json
import re
import sys
from pathlib import Path

PILOT_SKILLS = Path("/mnt/shared-storage-user/renyiming/skill_v4_restored/pilot_experiment/skills")
BENCH_SKILLS = Path("/mnt/shared-storage-user/renyiming/skill_v4_restored/skill-bench/skills")
GENES_DIR = Path(__file__).parent / "genes"

# 场景到领域的映射
DOMAIN_MAP = {
    "S002_spike_behavior": "neuroscience",
    "S005_protein_parse": "bioinformatics",
    "S007_data_viz": "visualization",
    "S011_particle_physics": "physics",
    "S012_uv_spectroscopy": "spectroscopy",
    "S017_ctd_ocean": "oceanography",
    "S026_earthquake_catalog": "geophysics",
    "S028_audio_features": "audio",
    "S030_fossil_morpho": "paleontology",
    "S033_exoplanet_transit": "astronomy",
    "S036_cmb_power_spectrum": "cosmology",
    "S037_asteroid_orbit": "astronomy",
    "S044_bfactor_analysis": "structural_biology",
    "S045_ramachandran": "structural_biology",
    "S048_gene_ontology": "genomics",
    "S052_phylogenetic_distance": "evolutionary_biology",
    "S053_methylation_beta": "epigenetics",
    "S054_species_accumulation": "ecology",
    "S060_phenology_shifts": "ecology",
    "S067_salinity_gradient": "oceanography",
    "S068_weather_fronts": "meteorology",
    "S069_rainfall_extreme": "meteorology",
    "S072_ozone_profile": "atmospheric",
    "S074_heat_index": "meteorology",
    "S077_grain_size": "geology",
    "S084_dose_response": "pharmacology",
    "S090_noise_reduction": "signal_processing",
    "S091_modulation_classify": "signal_processing",
    "S093_echo_removal": "signal_processing",
    "S096_network_influence": "network",
}

SCENARIOS = list(DOMAIN_MAP.keys())


def find_skill_md(scenario_id: str) -> Path | None:
    """找到 SKILL.md 文件路径"""
    for base in [BENCH_SKILLS, PILOT_SKILLS]:
        p = base / scenario_id / "direct" / "SKILL.md"
        if p.exists():
            return p
    return None


def parse_skill_md(text: str) -> dict:
    """解析 SKILL.md 提取结构化信息"""
    sections = {}
    current_section = None
    current_lines = []

    for line in text.split("\n"):
        if line.startswith("## "):
            if current_section:
                sections[current_section] = "\n".join(current_lines).strip()
            current_section = line[3:].strip().lower()
            current_lines = []
        elif line.startswith("# ") and not current_section:
            sections["title"] = line[2:].strip()
        else:
            current_lines.append(line)

    if current_section:
        sections[current_section] = "\n".join(current_lines).strip()

    return sections


def extract_keywords(sections: dict, scenario_id: str) -> list[str]:
    """从各 section 提取关键词"""
    keywords = set()

    # 从 title 提取
    title = sections.get("title", "")
    # 去掉常见词，保留领域词
    stop_words = {"and", "the", "a", "an", "of", "for", "in", "to", "with", "from", "by", "on", "is", "are", "data", "analysis", "processing", "script", "python"}
    for word in re.findall(r'\b[A-Za-z][a-z]{2,}\b', title):
        if word.lower() not in stop_words:
            keywords.add(word.lower())

    # 从 overview 提取关键名词短语
    overview = sections.get("overview", "")
    # 提取引号中的术语和特殊格式的词
    for match in re.findall(r'`([^`]+)`', overview):
        keywords.add(match)
    for match in re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)+\b', overview):
        keywords.add(match.lower())

    # 从 workflow 中提取技术术语
    workflow = sections.get("workflow", "")
    tech_patterns = [
        r'scipy\.\w+\.\w+', r'np\.\w+', r'pandas?\b', r'h5py\b',
        r'argparse\b', r'interpolat\w+', r'histogram\b', r'CSV\b',
        r'HDF5\b', r'JSON\b', r'MATLAB\b', r'FFT\b', r'PCA\b',
    ]
    for pat in tech_patterns:
        for match in re.findall(pat, workflow, re.IGNORECASE):
            keywords.add(match.lower())

    # 从 common pitfalls 中提取加粗的关键词
    pitfalls = sections.get("common pitfalls", "")
    for match in re.findall(r'\*\*([^*]+)\*\*', pitfalls):
        keywords.add(match.lower().rstrip(':'))

    # 限制 5-8 个
    kw_list = sorted(keywords)[:8]
    if len(kw_list) < 5:
        # 补充场景名称中的词
        for word in scenario_id.split("_")[1:]:
            if word not in kw_list:
                kw_list.append(word)
            if len(kw_list) >= 5:
                break

    return kw_list


def extract_summary(sections: dict) -> str:
    """提取一句话 summary"""
    overview = sections.get("overview", "")
    # 取第一句话
    sentences = re.split(r'(?<=[.!?])\s+', overview)
    if sentences:
        return sentences[0].strip()
    return overview[:200]


def extract_strategy(sections: dict) -> list[str]:
    """从 workflow 提取 2-3 步核心策略"""
    workflow = sections.get("workflow", "")
    steps = re.findall(r'^\d+\.\s*(.+)$', workflow, re.MULTILINE)

    if len(steps) <= 3:
        return steps

    # 选择最关键的 3 步（跳过纯 setup 步骤如 argparse）
    important_steps = []
    setup_keywords = ["argparse", "parse command", "set up", "initialize", "print summary", "display"]

    for step in steps:
        is_setup = any(kw in step.lower() for kw in setup_keywords)
        if not is_setup:
            important_steps.append(step)

    # 如果过滤后太少，补回来
    if len(important_steps) < 2:
        important_steps = steps

    return important_steps[:3]


def extract_pitfalls(sections: dict) -> list[str]:
    """提取 pitfalls（简化版）"""
    pitfalls_text = sections.get("common pitfalls", "")
    pitfalls = []

    for match in re.findall(r'\*\*([^*]+)\*\*:\s*(.+?)(?=\n-|\n\n|$)', pitfalls_text, re.DOTALL):
        name, desc = match
        # 只取第一句
        first_sentence = re.split(r'(?<=[.!?])\s+', desc.strip())[0]
        pitfalls.append(f"{name}: {first_sentence}")

    return pitfalls[:3]


def extract_key_concepts(sections: dict) -> list[str]:
    """提取 key concepts（从 error handling 和 quick reference 推断）"""
    concepts = []

    # 从 error handling 提取
    error_handling = sections.get("error handling", "")
    for line in error_handling.split("\n"):
        line = line.strip()
        if line.startswith("- "):
            # 提取第一个动词短语作为概念
            concept = line[2:].strip()
            if len(concept) > 10:
                concepts.append(concept.split(".")[0].strip())

    return concepts[:3]


def distill_gene(scenario_id: str) -> dict | None:
    """从 SKILL.md 蒸馏 Gene JSON"""
    skill_md_path = find_skill_md(scenario_id)
    if not skill_md_path:
        print(f"  WARNING: No SKILL.md for {scenario_id}")
        return None

    text = skill_md_path.read_text()
    sections = parse_skill_md(text)

    gene = {
        "scenario_id": scenario_id,
        "domain": DOMAIN_MAP.get(scenario_id, "unknown"),
        "keywords": extract_keywords(sections, scenario_id),
        "summary": extract_summary(sections),
        "strategy": extract_strategy(sections),
        "pitfalls": extract_pitfalls(sections),
        "key_concepts": extract_key_concepts(sections),
    }

    return gene


def main():
    GENES_DIR.mkdir(parents=True, exist_ok=True)

    print(f"Distilling Gene JSON for {len(SCENARIOS)} scenarios...")
    success = 0
    for s in SCENARIOS:
        out_path = GENES_DIR / f"{s}.json"
        gene = distill_gene(s)
        if gene:
            with open(out_path, "w") as f:
                json.dump(gene, f, indent=2, ensure_ascii=False)
            n_kw = len(gene["keywords"])
            n_st = len(gene["strategy"])
            print(f"  ✓ {s}: {n_kw} keywords, {n_st} strategy steps")
            success += 1
        else:
            print(f"  ✗ {s}: FAILED")

    print(f"\nDone! {success}/{len(SCENARIOS)} genes created in {GENES_DIR}")


if __name__ == "__main__":
    main()
