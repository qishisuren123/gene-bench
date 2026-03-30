#!/usr/bin/env python3
"""
Gene vs Skill 对比分析脚本。

将 Gene-Bench 结果与 Skill-Bench 结果进行对比，生成对比报告和图表。
"""

import argparse
import json
import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


def load_gene_results(path):
    """加载 Gene-Bench JSONL"""
    records = []
    with open(path) as f:
        for line in f:
            if line.strip():
                r = json.loads(line)
                tc = r.get("trial_config", {})
                records.append({
                    "model": tc.get("model", ""),
                    "scenario": tc.get("scenario_id", ""),
                    "condition": tc.get("condition", ""),
                    "gene_level": tc.get("gene_level", ""),
                    "pass_rate": r.get("eval", {}).get("pass_rate", 0),
                    "gene_tokens": r.get("gene_tokens", 0),
                    "source": "gene_bench",
                })
    return pd.DataFrame(records)


def load_skill_results(path):
    """加载 Skill-Bench CSV"""
    df = pd.read_csv(path)
    df["source"] = "skill_bench"
    df = df.rename(columns={"skill_level": "gene_level"})
    return df


def compare_gene_skill(gene_df, skill_df, outdir):
    """Gene vs Skill 对比分析"""
    os.makedirs(outdir, exist_ok=True)

    # 1. 按模型对比 G3 vs L1 vs L4
    print("\n=== Gene G3 vs Skill L1 vs Skill L4 ===")
    print(f"{'Model':<15} {'G0':>8} {'G3':>8} {'L1':>8} {'L4':>8} {'G3-G0':>8} {'L4-G0':>8} {'G3/L4':>8}")
    print("-" * 85)

    models = sorted(set(gene_df["model"].unique()))
    report_rows = []

    for m in models:
        g0 = gene_df[(gene_df["model"] == m) & (gene_df["gene_level"] == "G0")]["pass_rate"].mean()
        g3 = gene_df[(gene_df["model"] == m) & (gene_df["gene_level"] == "G3")]["pass_rate"].mean()

        # Skill L1 和 L4
        skill_m = skill_df[skill_df["model"] == m] if m in skill_df["model"].values else pd.DataFrame()
        l1 = skill_m[skill_m["gene_level"] == "L1_skill_md"]["pass_rate"].mean() if not skill_m.empty else np.nan
        l4 = skill_m[skill_m["gene_level"] == "L4_full"]["pass_rate"].mean() if not skill_m.empty else np.nan

        g3_g0 = (g3 - g0) * 100 if not np.isnan(g3) else np.nan
        l4_g0 = (l4 - g0) * 100 if not np.isnan(l4) else np.nan
        ratio = g3 / l4 if not np.isnan(l4) and l4 > 0 else np.nan

        print(f"{m:<15} {g0*100:>7.1f}% {g3*100:>7.1f}% {l1*100:>7.1f}% {l4*100:>7.1f}% {g3_g0:>+7.1f}pp {l4_g0:>+7.1f}pp {ratio:>7.2f}")

        report_rows.append({
            "model": m, "G0": g0, "G3": g3, "L1": l1, "L4": l4,
            "G3_delta": g3_g0, "L4_delta": l4_g0, "G3_L4_ratio": ratio,
        })

    # 2. Token 效率对比
    print("\n=== Token Efficiency ===")
    gene_tokens = gene_df[gene_df["gene_level"] == "G3"]["gene_tokens"].mean()
    skill_tokens = skill_df[skill_df["gene_level"].isin(["L1_skill_md"])]["skill_tokens"].mean() if "skill_tokens" in skill_df.columns else 600
    print(f"  Gene G3 avg tokens: ~{gene_tokens:.0f}")
    print(f"  Skill L1 avg tokens: ~{skill_tokens:.0f}")
    print(f"  Token saving: {(1 - gene_tokens/max(skill_tokens, 1))*100:.0f}%")

    # 3. 保存报告
    report_df = pd.DataFrame(report_rows)
    report_path = os.path.join(outdir, "gene_vs_skill_comparison.csv")
    report_df.to_csv(report_path, index=False)
    print(f"\n  Report saved to {report_path}")

    return report_df


def fig_gene_vs_skill_bars(report_df, outdir):
    """Gene vs Skill 对比条形图"""
    if report_df.empty:
        return

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    # 左图：绝对 pass rate
    models = report_df["model"].values
    x = np.arange(len(models))
    w = 0.2

    for ax_idx, (ax, title) in enumerate(zip(axes, ["Absolute Pass Rate (%)", "Token Efficiency (Δ pp per 100 tokens)"])):
        if ax_idx == 0:
            ax.bar(x - 1.5*w, report_df["G0"]*100, w, label="G0 (Baseline)", color="#ccc")
            ax.bar(x - 0.5*w, report_df["G3"]*100, w, label="Gene G3 (~120 tok)", color="#76C7A5")
            ax.bar(x + 0.5*w, report_df["L1"]*100, w, label="Skill L1 (~600 tok)", color="#F4B860")
            ax.bar(x + 1.5*w, report_df["L4"]*100, w, label="Skill L4 (Full)", color="#E8907E")
            ax.set_ylabel("Mean Pass Rate (%)")
            ax.set_title("Gene vs Skill: Who Wins?", fontweight="bold")
        else:
            # Token 效率 = Δ pass_rate / tokens * 100
            g3_eff = report_df["G3_delta"] / 1.2  # ~120 tokens → per 100 tok
            l4_eff = report_df["L4_delta"] / 6.0   # ~600 tokens → per 100 tok
            ax.bar(x - 0.25*0.8, g3_eff, 0.4, label="Gene G3", color="#76C7A5")
            ax.bar(x + 0.25*0.8, l4_eff, 0.4, label="Skill L4", color="#E8907E")
            ax.set_ylabel("Δ pp per 100 tokens")
            ax.set_title("Token Efficiency Comparison", fontweight="bold")
            ax.axhline(y=0, color="black", linewidth=0.5)

        ax.set_xticks(x)
        ax.set_xticklabels(models, rotation=45, ha="right", fontsize=8)
        ax.legend(fontsize=8)
        ax.grid(axis="y", alpha=0.3)

    plt.tight_layout()
    path = os.path.join(outdir, "fig_gene_vs_skill_comparison.png")
    fig.savefig(path, dpi=200)
    plt.close(fig)
    print(f"  ✓ {path}")


def main():
    parser = argparse.ArgumentParser(description="Compare Gene-Bench vs Skill-Bench results")
    parser.add_argument("--gene-data", default="../data/gene_bench_results.jsonl")
    parser.add_argument("--skill-data", default="../data/skill_bench_results.csv")
    parser.add_argument("--outdir", default="../figures")
    args = parser.parse_args()

    gene_df = load_gene_results(args.gene_data)
    skill_df = load_skill_results(args.skill_data)

    print(f"Gene-Bench: {len(gene_df)} trials")
    print(f"Skill-Bench: {len(skill_df)} trials")

    report_df = compare_gene_skill(gene_df, skill_df, args.outdir)
    fig_gene_vs_skill_bars(report_df, args.outdir)


if __name__ == "__main__":
    main()
