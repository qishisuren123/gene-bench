#!/usr/bin/env python3
"""
统计汇总脚本。

生成每个 RQ 的汇总统计（均值、标准差、效应量等）。
"""

import argparse
import json
import sys
import numpy as np
import pandas as pd
from pathlib import Path


def load_jsonl(path):
    records = []
    with open(path) as f:
        for line in f:
            if line.strip():
                r = json.loads(line)
                tc = r.get("trial_config", {})
                records.append({
                    "trial_key": r.get("trial_key", ""),
                    "model": tc.get("model", ""),
                    "scenario": tc.get("scenario_id", ""),
                    "rq": tc.get("rq", ""),
                    "condition": tc.get("condition", ""),
                    "gene_level": tc.get("gene_level", ""),
                    "mutation_type": tc.get("mutation_type", "none"),
                    "vaccinated": tc.get("vaccinated", False),
                    "pass_rate": r.get("eval", {}).get("pass_rate", 0),
                    "passed": r.get("eval", {}).get("passed", False),
                    "cost": r.get("cost", 0),
                })
    return pd.DataFrame(records)


def stats_rq1(df):
    """RQ1: Gene 完整度梯度统计"""
    sub = df[df["rq"] == "rq1"]
    if sub.empty:
        print("  RQ1: No data")
        return

    print("\n" + "=" * 60)
    print("  RQ1: Gene Completeness Spectrum")
    print("=" * 60)

    for level in ["G0", "G1", "G2", "G3", "G4", "L1"]:
        level_data = sub[sub["gene_level"] == level]["pass_rate"]
        if not level_data.empty:
            print(f"  {level:4s}: mean={level_data.mean():.3f} ± {level_data.std():.3f}  n={len(level_data)}")

    # 最优级别
    by_level = sub.groupby("gene_level")["pass_rate"].mean()
    if not by_level.empty:
        best = by_level.idxmax()
        print(f"\n  Best overall level: {best} (mean={by_level[best]:.3f})")

    # 按模型的最优级别
    print("\n  Best level by model:")
    for m in sorted(sub["model"].unique()):
        m_data = sub[sub["model"] == m].groupby("gene_level")["pass_rate"].mean()
        if not m_data.empty:
            best_m = m_data.idxmax()
            print(f"    {m:15s}: {best_m} (mean={m_data[best_m]:.3f})")


def stats_rq2(df):
    """RQ2: Gene vs Skill 统计"""
    sub = df[df["rq"] == "rq2"]
    if sub.empty:
        print("  RQ2: No data")
        return

    print("\n" + "=" * 60)
    print("  RQ2: Gene vs Skill Face-Off")
    print("=" * 60)

    for cond in ["rq2_no_context", "rq2_gene_g3", "rq2_skill_l1", "rq2_skill_l4"]:
        data = sub[sub["condition"] == cond]["pass_rate"]
        if not data.empty:
            print(f"  {cond:20s}: mean={data.mean():.3f} ± {data.std():.3f}  n={len(data)}")

    # 核心比较: Gene G3 vs Skill L4
    g3 = sub[sub["condition"] == "rq2_gene_g3"]["pass_rate"].mean()
    l4 = sub[sub["condition"] == "rq2_skill_l4"]["pass_rate"].mean()
    g0 = sub[sub["condition"] == "rq2_no_context"]["pass_rate"].mean()
    if not np.isnan(g3) and not np.isnan(l4):
        print(f"\n  Gene G3 achieves {g3/max(l4, 0.001)*100:.1f}% of Skill L4 performance")
        print(f"  Gene G3 improvement over baseline: {(g3-g0)*100:+.1f}pp")
        print(f"  Skill L4 improvement over baseline: {(l4-g0)*100:+.1f}pp")


def stats_rq3(df):
    """RQ3: Gene 变异容忍度统计"""
    sub = df[df["rq"] == "rq3"]
    if sub.empty:
        print("  RQ3: No data")
        return

    print("\n" + "=" * 60)
    print("  RQ3: Gene Error Tolerance")
    print("=" * 60)

    clean = sub[sub["condition"] == "rq3_clean_g3"]["pass_rate"].mean()
    print(f"  Clean baseline: {clean:.3f}")

    for mt in ["wrong_algorithm", "wrong_domain", "inverted_priority", "stale_paradigm", "overconstrained"]:
        data = sub[sub["condition"] == f"rq3_mutated_{mt}"]["pass_rate"]
        if not data.empty:
            delta = (data.mean() - clean) * 100
            print(f"  {mt:20s}: mean={data.mean():.3f}  Δ={delta:+.1f}pp")


def stats_rq7(df):
    """RQ7: 接种效应统计"""
    sub = df[df["rq"] == "rq7"]
    if sub.empty:
        print("  RQ7: No data")
        return

    print("\n" + "=" * 60)
    print("  RQ7: Gene Vaccination Effect")
    print("=" * 60)

    for cond in ["rq7_none", "rq7_clean_gene", "rq7_wrong_gene", "rq7_vaccinated_clean", "rq7_vaccinated_wrong"]:
        data = sub[sub["condition"] == cond]["pass_rate"]
        if not data.empty:
            print(f"  {cond:25s}: mean={data.mean():.3f} ± {data.std():.3f}  n={len(data)}")


def overall_stats(df):
    """总体统计"""
    print("\n" + "=" * 60)
    print("  Overall Statistics")
    print("=" * 60)
    print(f"  Total trials: {len(df)}")
    print(f"  Total cost:   ${df['cost'].sum():.2f}")
    print(f"  Models:       {df['model'].nunique()}")
    print(f"  Scenarios:    {df['scenario'].nunique()}")
    print(f"  Pass rate:    {df['pass_rate'].mean():.3f} overall")

    print("\n  By RQ:")
    for rq in sorted(df["rq"].unique()):
        rq_data = df[df["rq"] == rq]
        print(f"    {rq}: {len(rq_data)} trials, mean pass_rate={rq_data['pass_rate'].mean():.3f}, cost=${rq_data['cost'].sum():.2f}")


def main():
    parser = argparse.ArgumentParser(description="Gene-Bench statistics summary")
    parser.add_argument("--data", default="../data/gene_bench_results.jsonl")
    args = parser.parse_args()

    df = load_jsonl(args.data)
    print(f"Loaded {len(df)} trials from {args.data}")

    overall_stats(df)
    stats_rq1(df)
    stats_rq2(df)
    stats_rq3(df)
    stats_rq7(df)


if __name__ == "__main__":
    main()
