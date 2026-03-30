#!/usr/bin/env python3
"""
将现有 Gene JSON 转换为 evomap.ai 官方 GEP v1.5.0 格式。

旧格式:
  scenario_id, domain, keywords, summary, strategy, pitfalls, key_concepts

新格式 (GEP v1.5.0):
  type, schema_version, id, category, signals_match, summary, preconditions,
  strategy, constraints, validation, epigenetic_marks, asset_id
"""

import json
import hashlib
from pathlib import Path

GENES_DIR = Path(__file__).parent / "genes"
SCENARIOS_DIR = Path(__file__).parent / "scenarios"

# 场景到领域的映射（保留用于 epigenetic_marks）
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
    "S101_climate_attribution": "climate_science",
    "S102_protein_secondary": "structural_biology",
    "S103_instrumental_variable": "econometrics",
    "S104_multisensor_anomaly": "sensor_fusion",
    "S105_community_detection": "network",
    "S106_seismic_denoise": "geophysics",
    "S107_regime_switch": "time_series",
    "S108_raman_spectroscopy": "spectroscopy",
    "S109_hdf5_chunked": "data_engineering",
    "S110_log_regex": "devops",
    "S111_cuda_memory": "gpu_computing",
    "S112_midi_chords": "music",
    "S113_inventory_reorder": "operations_research",
    "S114_obstacle_avoidance": "robotics",
    "S115_quantum_circuit": "quantum_computing",
}


def compute_asset_id(gene_dict: dict) -> str:
    """计算 Gene 的 SHA-256 content-addressable ID"""
    # 排除 asset_id 自身
    d = {k: v for k, v in gene_dict.items() if k != "asset_id"}
    canonical = json.dumps(d, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return f"sha256:{hashlib.sha256(canonical.encode()).hexdigest()}"


def convert_gene(old_gene: dict) -> dict:
    """将旧格式 Gene 转换为 GEP v1.5.0"""
    scenario_id = old_gene.get("scenario_id", "unknown")
    domain = old_gene.get("domain", DOMAIN_MAP.get(scenario_id, "unknown"))

    # signals_match: 从 keywords 转换，确保每个 >= 3 字符
    signals = [kw for kw in old_gene.get("keywords", []) if len(kw) >= 3]
    if not signals:
        signals = [scenario_id]

    # strategy: 保留原始 + 将 pitfalls 追加为 AVOID 步骤
    strategy = list(old_gene.get("strategy", []))
    for pitfall in old_gene.get("pitfalls", []):
        strategy.append(f"AVOID: {pitfall}")

    # preconditions: 从 key_concepts 转换
    preconditions = list(old_gene.get("key_concepts", []))

    # 构建新 Gene（先不含 asset_id）
    new_gene = {
        "type": "Gene",
        "schema_version": "1.5.0",
        "id": f"gene_{scenario_id}",
        "category": "optimize",
        "signals_match": signals,
        "summary": old_gene.get("summary", ""),
        "preconditions": preconditions if preconditions else [],
        "strategy": strategy,
        "constraints": {
            "max_files": 1,
            "forbidden_paths": []
        },
        "validation": [f"python -m pytest scenarios/{scenario_id}/"],
        "epigenetic_marks": [f"domain:{domain}"],
    }

    # 计算 asset_id
    new_gene["asset_id"] = compute_asset_id(new_gene)

    return new_gene


def main():
    gene_files = sorted(GENES_DIR.glob("S*.json"))
    print(f"转换 {len(gene_files)} 个 Gene 到 GEP v1.5.0 格式...\n")

    success = 0
    for gf in gene_files:
        old_gene = json.loads(gf.read_text())
        new_gene = convert_gene(old_gene)

        # 验证必填字段
        required = ["type", "schema_version", "id", "category", "signals_match",
                     "summary", "strategy", "constraints", "validation", "asset_id"]
        missing = [f for f in required if f not in new_gene or not new_gene[f]]
        if missing:
            print(f"  ✗ {gf.name}: 缺失字段 {missing}")
            continue

        # 写回
        gf.write_text(json.dumps(new_gene, indent=2, ensure_ascii=False))
        n_sig = len(new_gene["signals_match"])
        n_strat = len(new_gene["strategy"])
        print(f"  ✓ {gf.name}: {n_sig} signals, {n_strat} strategy steps, id={new_gene['id']}")
        success += 1

    print(f"\n完成! {success}/{len(gene_files)} 个 Gene 已转换为 GEP v1.5.0")


if __name__ == "__main__":
    main()
