#!/usr/bin/env python3
"""
Gene-Bench 可视化脚本。

生成 7 个 RQ 对应的核心图表：
  - RQ1: Gene 完整度热力图 (G0-G4 + L1)
  - RQ2: Gene vs Skill 对比条形图
  - RQ3: Gene 变异容忍度柱状图
  - RQ4: 跨领域迁移热力图
  - RQ5: Gene 组合效应图
  - RQ7: 接种效应对比图
  - Overview: Gene 收益散点图

用法: python generate_figures.py --data ../data/gene_bench_results.csv --outdir ../figures
"""

import argparse
import os
import json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

# ── 全局样式 ──
plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 11,
    "axes.titlesize": 13,
    "axes.labelsize": 12,
    "figure.dpi": 200,
    "savefig.bbox": "tight",
    "savefig.pad_inches": 0.15,
})

# 12 模型颜色方案
MODEL_COLORS = {
    "opus":         "#B07CC6",
    "sonnet":       "#E8907E",
    "haiku":        "#7FB3D8",
    "gpt5_4":       "#76C7A5",
    "gpt5_mini":    "#A8D08D",
    "gpt5_nano":    "#D4E6A5",
    "gemini_pro":   "#F4B860",
    "gemini_flash": "#F9D99A",
    "qwen_moe":     "#8DB6CD",
    "qwen_coder":   "#5F9EA0",
    "ds_v3":        "#DDA0DD",
    "ds_r1":        "#BA55D3",
}

MODEL_LABELS = {
    "opus":         "Opus 4.6",
    "sonnet":       "Sonnet 4.6",
    "haiku":        "Haiku 4.5",
    "gpt5_4":       "GPT-5.4",
    "gpt5_mini":    "GPT-5 Mini",
    "gpt5_nano":    "GPT-5 Nano",
    "gemini_pro":   "Gemini 3 Pro",
    "gemini_flash": "Gemini 2.5 Flash",
    "qwen_moe":     "Qwen3.5 MoE",
    "qwen_coder":   "Qwen3 Coder",
    "ds_v3":        "DS V3.2",
    "ds_r1":        "DS R1",
}

GENE_LEVEL_LABELS = {
    "G0": "G0\nNone",
    "G1": "G1\nKeywords",
    "G2": "G2\n+Summary",
    "G3": "G3\n+Strategy",
    "G4": "G4\n+Pitfalls",
    "L1": "L1\nSKILL.md",
}

# 模型排序（弱到强）
MODEL_ORDER = ["haiku", "gpt5_nano", "gpt5_mini", "gemini_flash", "qwen_moe",
               "gpt5_4", "sonnet", "gemini_pro", "ds_v3", "ds_r1", "qwen_coder", "opus"]

GENE_LEVEL_ORDER = ["G0", "G1", "G2", "G3", "G4", "L1"]


def load_jsonl(path):
    """加载 JSONL 结果文件为 DataFrame"""
    records = []
    with open(path) as f:
        for line in f:
            if line.strip():
                r = json.loads(line)
                flat = {
                    "trial_key": r.get("trial_key", ""),
                    "pass_rate": r.get("eval", {}).get("pass_rate", 0),
                    "n_pass": r.get("eval", {}).get("n_pass", 0),
                    "n_total": r.get("eval", {}).get("n_total", 0),
                    "passed": r.get("eval", {}).get("passed", False),
                    "error_type": r.get("eval", {}).get("error_type", ""),
                    "code_length": r.get("code_length", 0),
                    "gene_tokens": r.get("gene_tokens", 0),
                    "input_tokens": r.get("input_tokens", 0),
                    "output_tokens": r.get("output_tokens", 0),
                    "cost": r.get("cost", 0),
                }
                tc = r.get("trial_config", {})
                flat.update({
                    "model": tc.get("model", ""),
                    "scenario": tc.get("scenario_id", ""),
                    "rq": tc.get("rq", ""),
                    "condition": tc.get("condition", ""),
                    "gene_level": tc.get("gene_level", ""),
                    "mutation_type": tc.get("mutation_type", "none"),
                    "transfer_source": tc.get("transfer_source", "none"),
                    "vaccinated": tc.get("vaccinated", False),
                    "gene_author": tc.get("gene_author", "none"),
                })
                records.append(flat)
    return pd.DataFrame(records)


def fig_rq1_heatmap(df, outdir):
    """RQ1: Gene 完整度热力图 — model × gene_level → pass_rate"""
    sub = df[df["rq"] == "rq1"].copy()
    if sub.empty:
        print("  ⚠ RQ1: no data")
        return

    # 提取 gene_level
    models_present = [m for m in MODEL_ORDER if m in sub["model"].unique()]
    levels_present = [l for l in GENE_LEVEL_ORDER if l in sub["gene_level"].unique()]

    pivot = sub.groupby(["model", "gene_level"])["pass_rate"].mean().unstack()
    pivot = pivot.reindex(index=models_present, columns=levels_present)

    fig, ax = plt.subplots(figsize=(10, max(5, len(models_present) * 0.6)))
    data = pivot.values * 100

    im = ax.imshow(data, cmap="RdYlGn", aspect="auto", vmin=15, vmax=65)

    for i in range(data.shape[0]):
        for j in range(data.shape[1]):
            val = data[i, j]
            if not np.isnan(val):
                color = "white" if val < 25 or val > 60 else "black"
                ax.text(j, i, f"{val:.1f}%", ha="center", va="center",
                        fontsize=9, fontweight="bold", color=color)

    ax.set_xticks(range(len(levels_present)))
    ax.set_xticklabels([GENE_LEVEL_LABELS.get(l, l) for l in levels_present], fontsize=9)
    ax.set_yticks(range(len(models_present)))
    ax.set_yticklabels([MODEL_LABELS.get(m, m) for m in models_present], fontsize=10)

    # Delta 注释
    for i, m in enumerate(models_present):
        if "G0" in pivot.columns and levels_present[-1] in pivot.columns:
            g0 = pivot.loc[m, "G0"] * 100 if not np.isnan(pivot.loc[m, "G0"]) else 0
            best = pivot.loc[m, levels_present[-1]] * 100 if not np.isnan(pivot.loc[m, levels_present[-1]]) else 0
            delta = best - g0
            color = "#2E7D32" if delta > 3 else ("#C62828" if delta < -2 else "#666")
            sign = "+" if delta > 0 else ""
            ax.text(len(levels_present) + 0.3, i, f"Δ={sign}{delta:.1f}pp",
                    ha="left", va="center", fontsize=9, fontweight="bold", color=color)

    ax.set_title("RQ1: Gene Completeness Spectrum — Which Granularity Works Best?",
                 fontsize=13, fontweight="bold", pad=15)
    ax.set_xlabel("Gene Completeness Level", labelpad=10)

    cbar = plt.colorbar(im, ax=ax, shrink=0.8, pad=0.18)
    cbar.set_label("Mean Pass Rate (%)", fontsize=10)

    plt.tight_layout()
    path = os.path.join(outdir, "fig_rq1_gene_completeness.png")
    fig.savefig(path, dpi=200)
    plt.close(fig)
    print(f"  ✓ {path}")


def fig_rq2_gene_vs_skill(df, outdir):
    """RQ2: Gene vs Skill 对比 — 分组条形图"""
    sub = df[df["rq"] == "rq2"].copy()
    if sub.empty:
        print("  ⚠ RQ2: no data")
        return

    conditions = ["rq2_no_context", "rq2_gene_g3", "rq2_skill_l1", "rq2_skill_l4"]
    cond_labels = ["No Context\n(Baseline)", "Gene G3\n(~120 tok)", "Skill L1\n(~600 tok)", "Skill L4\n(Full)"]
    models_present = [m for m in MODEL_ORDER if m in sub["model"].unique()]

    fig, ax = plt.subplots(figsize=(12, 6))
    x = np.arange(len(conditions))
    width = 0.8 / max(len(models_present), 1)
    offsets = np.arange(len(models_present)) - (len(models_present) - 1) / 2

    for idx, m in enumerate(models_present):
        rates = []
        for c in conditions:
            vals = sub[(sub["model"] == m) & (sub["condition"] == c)]["pass_rate"]
            rates.append(vals.mean() * 100 if len(vals) > 0 else 0)
        ax.bar(x + offsets[idx] * width, rates, width * 0.9,
               label=MODEL_LABELS.get(m, m), color=MODEL_COLORS.get(m, "#999"),
               edgecolor="white", linewidth=0.5)

    ax.set_xticks(x)
    ax.set_xticklabels(cond_labels, fontsize=10)
    ax.set_ylabel("Mean Pass Rate (%)", fontsize=11)
    ax.set_title("RQ2: Can Lightweight Genes Match Full Skills?",
                 fontsize=14, fontweight="bold", pad=15)
    ax.legend(loc="upper left", ncol=3, fontsize=8, framealpha=0.9)
    ax.set_ylim(0, 85)
    ax.grid(axis="y", alpha=0.3)

    plt.tight_layout()
    path = os.path.join(outdir, "fig_rq2_gene_vs_skill.png")
    fig.savefig(path, dpi=200)
    plt.close(fig)
    print(f"  ✓ {path}")


def fig_rq3_mutation_tolerance(df, outdir):
    """RQ3: Gene 变异容忍度"""
    sub = df[df["rq"] == "rq3"].copy()
    if sub.empty:
        print("  ⚠ RQ3: no data")
        return

    mutation_types = ["wrong_algorithm", "wrong_domain", "inverted_priority", "stale_paradigm", "overconstrained"]
    mut_labels = ["Wrong\nAlgorithm", "Wrong\nDomain", "Inverted\nPriority", "Stale\nParadigm", "Over-\nconstrained"]
    models_present = [m for m in MODEL_ORDER if m in sub["model"].unique()]

    # 计算 clean baseline
    baselines = {}
    for m in models_present:
        clean = sub[(sub["model"] == m) & (sub["condition"] == "rq3_clean_g3")]["pass_rate"]
        baselines[m] = clean.mean() if len(clean) > 0 else 0

    fig, ax = plt.subplots(figsize=(12, 5.5))
    x = np.arange(len(mutation_types))
    width = 0.8 / max(len(models_present), 1)
    offsets = np.arange(len(models_present)) - (len(models_present) - 1) / 2

    for idx, m in enumerate(models_present):
        deltas = []
        for mt in mutation_types:
            cond = f"rq3_mutated_{mt}"
            vals = sub[(sub["model"] == m) & (sub["condition"] == cond)]["pass_rate"]
            avg = vals.mean() if len(vals) > 0 else 0
            deltas.append((avg - baselines[m]) * 100)
        ax.bar(x + offsets[idx] * width, deltas, width * 0.9,
               label=MODEL_LABELS.get(m, m), color=MODEL_COLORS.get(m, "#999"),
               edgecolor="white", linewidth=0.5)

    ax.axhline(y=0, color="black", linewidth=0.8)
    ax.set_xticks(x)
    ax.set_xticklabels(mut_labels, fontsize=9)
    ax.set_ylabel("Δ Pass Rate (pp) vs. Clean Gene", fontsize=11)
    ax.set_title("RQ3: How Robust Are Models to Gene Mutations?",
                 fontsize=14, fontweight="bold", pad=15)
    ax.legend(loc="lower left", ncol=3, fontsize=8, framealpha=0.9)
    ax.grid(axis="y", alpha=0.3)

    plt.tight_layout()
    path = os.path.join(outdir, "fig_rq3_mutation_tolerance.png")
    fig.savefig(path, dpi=200)
    plt.close(fig)
    print(f"  ✓ {path}")


def fig_rq4_transfer_heatmap(df, outdir):
    """RQ4: 跨领域迁移热力图"""
    sub = df[df["rq"] == "rq4"].copy()
    if sub.empty:
        print("  ⚠ RQ4: no data")
        return

    transfer_types = ["exact_match", "same_domain", "analogous_task", "unrelated", "none"]
    type_labels = ["Exact\nMatch", "Same\nDomain", "Analogous\nTask", "Unrelated", "No Gene"]
    models_present = [m for m in MODEL_ORDER if m in sub["model"].unique()]

    fig, ax = plt.subplots(figsize=(10, max(5, len(models_present) * 0.5)))

    data = np.zeros((len(models_present), len(transfer_types)))
    for i, m in enumerate(models_present):
        for j, tt in enumerate(transfer_types):
            cond = f"rq4_{tt}"
            vals = sub[(sub["model"] == m) & (sub["condition"] == cond)]["pass_rate"]
            data[i, j] = vals.mean() * 100 if len(vals) > 0 else np.nan

    im = ax.imshow(data, cmap="YlOrRd", aspect="auto", vmin=0, vmax=70)

    for i in range(data.shape[0]):
        for j in range(data.shape[1]):
            if not np.isnan(data[i, j]):
                color = "white" if data[i, j] > 50 else "black"
                ax.text(j, i, f"{data[i,j]:.1f}%", ha="center", va="center",
                        fontsize=9, color=color)

    ax.set_xticks(range(len(transfer_types)))
    ax.set_xticklabels(type_labels, fontsize=9)
    ax.set_yticks(range(len(models_present)))
    ax.set_yticklabels([MODEL_LABELS.get(m, m) for m in models_present], fontsize=10)
    ax.set_title("RQ4: Can Genes Transfer Across Domains?",
                 fontsize=14, fontweight="bold", pad=15)

    cbar = plt.colorbar(im, ax=ax, shrink=0.8)
    cbar.set_label("Mean Pass Rate (%)")

    plt.tight_layout()
    path = os.path.join(outdir, "fig_rq4_transfer.png")
    fig.savefig(path, dpi=200)
    plt.close(fig)
    print(f"  ✓ {path}")


def fig_rq7_vaccination(df, outdir):
    """RQ7: 接种效应对比"""
    sub = df[df["rq"] == "rq7"].copy()
    if sub.empty:
        print("  ⚠ RQ7: no data")
        return

    conditions = ["rq7_none", "rq7_clean_gene", "rq7_wrong_gene", "rq7_vaccinated_clean", "rq7_vaccinated_wrong"]
    cond_labels = ["No Gene", "Clean\nGene", "Wrong\nGene", "Vacc.\nClean", "Vacc.\nWrong"]
    models_present = [m for m in MODEL_ORDER if m in sub["model"].unique()]

    fig, ax = plt.subplots(figsize=(12, 6))
    x = np.arange(len(conditions))
    width = 0.8 / max(len(models_present), 1)
    offsets = np.arange(len(models_present)) - (len(models_present) - 1) / 2

    for idx, m in enumerate(models_present):
        rates = []
        for c in conditions:
            vals = sub[(sub["model"] == m) & (sub["condition"] == c)]["pass_rate"]
            rates.append(vals.mean() * 100 if len(vals) > 0 else 0)
        ax.bar(x + offsets[idx] * width, rates, width * 0.9,
               label=MODEL_LABELS.get(m, m), color=MODEL_COLORS.get(m, "#999"),
               edgecolor="white", linewidth=0.5)

    ax.set_xticks(x)
    ax.set_xticklabels(cond_labels, fontsize=10)
    ax.set_ylabel("Mean Pass Rate (%)", fontsize=11)
    ax.set_title("RQ7: Does Gene Vaccination Protect Against Bad Genes?",
                 fontsize=14, fontweight="bold", pad=15)
    ax.legend(loc="upper right", ncol=3, fontsize=8, framealpha=0.9)
    ax.set_ylim(0, 85)
    ax.grid(axis="y", alpha=0.3)

    plt.tight_layout()
    path = os.path.join(outdir, "fig_rq7_vaccination.png")
    fig.savefig(path, dpi=200)
    plt.close(fig)
    print(f"  ✓ {path}")


def fig_overview_scatter(df, outdir):
    """总览: G0 vs G3 pass_rate 散点图"""
    sub = df[df["rq"].isin(["rq1", "rq2"])].copy()
    if sub.empty:
        print("  ⚠ Overview: no data")
        return

    g0 = sub[sub["gene_level"] == "G0"].groupby(["model", "scenario"])["pass_rate"].mean().reset_index()
    g3 = sub[sub["gene_level"] == "G3"].groupby(["model", "scenario"])["pass_rate"].mean().reset_index()
    merged = g0.merge(g3, on=["model", "scenario"], suffixes=("_g0", "_g3"))

    if merged.empty:
        print("  ⚠ Overview: insufficient data for scatter")
        return

    fig, ax = plt.subplots(figsize=(8, 8))
    ax.plot([0, 1], [0, 1], "k--", alpha=0.3, linewidth=1)
    ax.fill_between([0, 1], [0, 1], [1, 1], alpha=0.06, color="green")
    ax.fill_between([0, 1], [0, 0], [0, 1], alpha=0.06, color="red")

    models_present = [m for m in MODEL_ORDER if m in merged["model"].unique()]
    for m in models_present:
        s = merged[merged["model"] == m]
        ax.scatter(s["pass_rate_g0"] * 100, s["pass_rate_g3"] * 100,
                   c=MODEL_COLORS.get(m, "#999"), label=MODEL_LABELS.get(m, m),
                   s=60, alpha=0.7, edgecolors="white", linewidth=0.5, zorder=3)

    ax.set_xlabel("Pass Rate without Gene — G0 (%)", fontsize=12)
    ax.set_ylabel("Pass Rate with Gene — G3 (%)", fontsize=12)
    ax.set_title("Overview: Does Adding a Gene Help?",
                 fontsize=14, fontweight="bold", pad=15)
    ax.set_xlim(-5, 105)
    ax.set_ylim(-5, 105)
    ax.set_aspect("equal")
    ax.legend(loc="lower right", fontsize=8, framealpha=0.9, ncol=2)
    ax.grid(alpha=0.2)

    ax.text(15, 90, "Gene Helps ↑", fontsize=11, color="#2E7D32", fontweight="bold", alpha=0.7)
    ax.text(70, 15, "Gene Hurts ↓", fontsize=11, color="#C62828", fontweight="bold", alpha=0.7)

    plt.tight_layout()
    path = os.path.join(outdir, "fig_overview_scatter.png")
    fig.savefig(path, dpi=200)
    plt.close(fig)
    print(f"  ✓ {path}")


def main():
    parser = argparse.ArgumentParser(description="Generate Gene-Bench figures")
    parser.add_argument("--data", default="../data/gene_bench_results.jsonl",
                        help="Path to gene_bench_results.jsonl")
    parser.add_argument("--outdir", default="../figures",
                        help="Output directory for figures")
    args = parser.parse_args()

    os.makedirs(args.outdir, exist_ok=True)
    print(f"Loading data from {args.data} ...")
    df = load_jsonl(args.data)
    print(f"  {len(df)} trials loaded")

    print(f"\nGenerating figures ...")
    fig_rq1_heatmap(df, args.outdir)
    fig_rq2_gene_vs_skill(df, args.outdir)
    fig_rq3_mutation_tolerance(df, args.outdir)
    fig_rq4_transfer_heatmap(df, args.outdir)
    fig_rq7_vaccination(df, args.outdir)
    fig_overview_scatter(df, args.outdir)

    print(f"\nDone! Figures saved to {args.outdir}/")


if __name__ == "__main__":
    main()
