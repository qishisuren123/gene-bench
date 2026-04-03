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


# ── Skill 拆解与格式转换辅助函数（EX22-EX27 用）──

# SKILL.md 章节标题映射
_SKILL_SECTIONS = {
    "overview": "## Overview",
    "workflow": "## Workflow",
    "pitfalls": "## Common Pitfalls",
    "error_handling": "## Error Handling",
    "quick_reference": "## Quick Reference",
}


def extract_skill_section(skill_dir: Path, section: str) -> str:
    """
    从 SKILL.md 中提取单个章节内容。

    Args:
        skill_dir: 技能目录（含 SKILL.md）
        section: 章节名 (overview/workflow/pitfalls/error_handling/quick_reference)
    """
    if skill_dir is None:
        return ""
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        return ""

    content = skill_md.read_text()
    header = _SKILL_SECTIONS.get(section, "")
    if not header:
        return ""

    # 找到章节起始位置
    start = content.find(header)
    if start == -1:
        return ""

    # 找到下一个 ## 标题或文件末尾
    body_start = start + len(header)
    next_section = content.find("\n## ", body_start)
    if next_section == -1:
        section_text = content[body_start:]
    else:
        section_text = content[body_start:next_section]

    return section_text.strip()


def inject_skill_section(skill_dir: Path, section: str) -> str:
    """注入单个 SKILL.md 章节，带 XML 标签包装"""
    text = extract_skill_section(skill_dir, section)
    if not text:
        return ""
    return (
        f"You are given the following {section.replace('_', ' ')} guidance:\n\n"
        f"<skill-{section}>\n{text}\n</skill-{section}>"
    )


def inject_skill_truncated(skill_dir: Path, section: str, max_lines: int) -> str:
    """注入截断版的 SKILL.md 章节（取前 N 行）"""
    text = extract_skill_section(skill_dir, section)
    if not text:
        return ""
    lines = text.split("\n")[:max_lines]
    truncated = "\n".join(lines)
    return (
        f"You are given a brief {section.replace('_', ' ')} note:\n\n"
        f"<skill-{section}-short>\n{truncated}\n</skill-{section}-short>"
    )


def inject_pitfalls_as_xml(skill_dir: Path) -> str:
    """将 SKILL.md 的 pitfalls 章节转换为结构化 XML 格式"""
    text = extract_skill_section(skill_dir, "pitfalls")
    if not text:
        return ""

    # 解析 markdown pitfall 列表项
    pitfalls = []
    for line in text.split("\n"):
        line = line.strip()
        if line.startswith("- **"):
            # 提取 **title**: description 格式
            end_bold = line.find("**", 4)
            if end_bold > 0:
                title = line[4:end_bold]
                desc = line[end_bold+2:].lstrip(": ")
                pitfalls.append((title, desc))
            else:
                pitfalls.append(("", line[2:]))
        elif line.startswith("- "):
            pitfalls.append(("", line[2:]))

    if not pitfalls:
        return ""

    xml_parts = ['<pitfall-warnings severity="critical">']
    for i, (title, desc) in enumerate(pitfalls, 1):
        xml_parts.append(f'  <pitfall id="{i}" title="{title}">')
        xml_parts.append(f'    {desc}')
        xml_parts.append(f'  </pitfall>')
    xml_parts.append('</pitfall-warnings>')

    return (
        "CRITICAL: Review these documented pitfalls before implementation:\n\n"
        + "\n".join(xml_parts)
    )


def inject_evolution_event(gene: dict, scenario_id: str) -> str:
    """
    将 Gene 包装为 EvolutionEvent 叙事格式。
    模拟 evomap 的进化日志风格。
    """
    summary = gene.get("summary", "")
    strategy = gene.get("strategy", [])
    pitfalls = gene.get("pitfalls", [])
    keywords = gene.get("signals_match", gene.get("keywords", []))

    parts = [
        f'<evolution-event scenario="{scenario_id}">',
        f'  <generation>3</generation>',
        f'  <fitness>0.85</fitness>',
        f'  <insight>{summary}</insight>',
    ]
    if strategy:
        parts.append('  <learned-strategy>')
        for s in strategy:
            parts.append(f'    <step>{s}</step>')
        parts.append('  </learned-strategy>')
    if pitfalls:
        parts.append('  <failed-attempts>')
        for p in pitfalls:
            parts.append(f'    <failure>{p}</failure>')
        parts.append('  </failed-attempts>')
    if keywords:
        parts.append(f'  <domain-signals>{", ".join(keywords[:6])}</domain-signals>')
    parts.append('</evolution-event>')

    return (
        "This gene was evolved over multiple iterations. "
        "The following evolution event captures what was learned:\n\n"
        + "\n".join(parts)
    )
