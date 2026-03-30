#!/usr/bin/env python3
"""
Gene 注入模块：将 Gene 序列化为 LLM prompt。

处理 G0-G4 级别的 Gene 注入，以及 L1（SKILL.md 对照组）。
"""

from pathlib import Path
from gene_builder import serialize_gene, wrap_gene_prompt, vaccinate_gene_text, combine_genes


# ── Gene 级别定义 ──
GENE_LEVELS = ["G0", "G1", "G2", "G3", "G4", "L1"]

GENE_LEVEL_DESCRIPTIONS = {
    "G0": "无引导（baseline）",
    "G1": "仅关键词（~25 tokens）",
    "G2": "关键词 + summary（~50 tokens）",
    "G3": "标准 Gene：关键词 + summary + strategy（~120 tokens）",
    "G4": "完整 Gene：+ pitfalls + key_concepts（~200 tokens）",
    "L1": "SKILL.md 全文（对照组，~600 tokens）",
}


def inject_gene(gene: dict, level: str, skill_dir: Path = None) -> str:
    """
    根据级别生成完整的系统提示文本。

    Args:
        gene: Gene JSON 字典
        level: G0/G1/G2/G3/G4/L1
        skill_dir: L1 级别需要的 SKILL.md 路径

    Returns:
        完整的系统提示文本（为空字符串表示无引导）
    """
    if level == "G0":
        return ""

    if level == "L1":
        # 对照组：直接使用 SKILL.md
        return _inject_skill_l1(skill_dir)

    # G1-G4: 使用 Gene 序列化
    gene_text = serialize_gene(gene, level)
    return wrap_gene_prompt(gene_text)


def _inject_skill_l1(skill_dir: Path) -> str:
    """L1 对照组：SKILL.md 全文"""
    if skill_dir is None:
        return ""
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        return ""
    content = skill_md.read_text()
    return (
        "You are given the following skill package to guide your work. "
        "Follow its instructions carefully.\n\n"
        f"<skill-package>\n<file path=\"SKILL.md\">\n{content}\n</file>\n</skill-package>"
    )


def inject_skill_full(skill_dir: Path) -> str:
    """L4 对照组：完整 Skill 包（SKILL.md + scripts + references）"""
    if skill_dir is None or not skill_dir.exists():
        return ""

    parts = []
    skill_md = skill_dir / "SKILL.md"
    if skill_md.exists():
        parts.append(f'<file path="SKILL.md">\n{skill_md.read_text()}\n</file>')

    scripts_dir = skill_dir / "scripts"
    if scripts_dir.exists():
        for f in sorted(scripts_dir.glob("*")):
            if f.is_file():
                try:
                    parts.append(f'<file path="scripts/{f.name}">\n{f.read_text()}\n</file>')
                except UnicodeDecodeError:
                    parts.append(f'<file path="scripts/{f.name}">[binary]</file>')

    refs_dir = skill_dir / "references"
    if refs_dir.exists():
        for f in sorted(refs_dir.glob("*")):
            if f.is_file():
                try:
                    parts.append(f'<file path="references/{f.name}">\n{f.read_text()}\n</file>')
                except UnicodeDecodeError:
                    pass

    if not parts:
        return ""

    content = "\n\n".join(parts)
    return (
        "You are given the following skill package to guide your work. "
        "Follow its instructions carefully.\n\n"
        f"<skill-package>\n{content}\n</skill-package>"
    )


def inject_vaccinated(gene: dict, level: str, skill_dir: Path = None) -> str:
    """注入带接种前缀的 Gene/Skill"""
    base_text = inject_gene(gene, level, skill_dir)
    if not base_text:
        return ""
    return vaccinate_gene_text(base_text)


def inject_combined_genes(genes: list[dict], mode: str = "complementary") -> str:
    """注入组合 Gene（RQ5）"""
    combined = combine_genes(genes, mode)
    gene_text = serialize_gene(combined, "G3")

    header = f"You are given {len(genes)} combined strategic genes ({mode} mode) to guide your approach.\n"
    header += "Use them as directional guidance, not as implementation instructions.\n\n"

    return header + f"<strategy-gene>\n{gene_text}\n</strategy-gene>"


def estimate_tokens(text: str) -> int:
    """粗略估算 token 数（英文约 4 字符/token）"""
    if not text:
        return 0
    return max(1, len(text) // 4)
