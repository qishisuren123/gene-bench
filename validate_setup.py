#!/usr/bin/env python3
"""
Gene-Bench 预检脚本：验证所有 45 场景的基础设施完整性。

检查项：
1. 每个场景有 task.md + test_script.py
2. 每个场景有 GEP v1.5.0 格式的 Gene
3. 每个场景有 SKILL.md
4. 每个场景在 DOMAIN_INFO 中有条目
5. Gene 级别序列化非空
6. 可选：单场景 smoke test
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).parent
SCENARIOS_DIR = ROOT / "scenarios"
SKILLS_DIR = ROOT / "skills"
GENES_DIR = ROOT / "genes"

# GEP v1.5.0 必需字段
GEP_REQUIRED = [
    "type", "schema_version", "id", "category", "signals_match",
    "summary", "strategy", "constraints", "validation", "asset_id",
]


def check_scenarios():
    """检查 task.md + test_script.py"""
    errors = []
    gene_files = sorted(GENES_DIR.glob("S*.json"))
    scenario_ids = [f.stem for f in gene_files]

    for sid in scenario_ids:
        sc_dir = SCENARIOS_DIR / sid
        if not sc_dir.exists():
            errors.append(f"  ✗ {sid}: 场景目录不存在 {sc_dir}")
            continue
        if not (sc_dir / "task.md").exists():
            errors.append(f"  ✗ {sid}: 缺少 task.md")
        if not (sc_dir / "test_script.py").exists():
            errors.append(f"  ✗ {sid}: 缺少 test_script.py")

    return scenario_ids, errors


def check_genes(scenario_ids):
    """检查 Gene 是否为 GEP v1.5.0 格式"""
    errors = []
    for sid in scenario_ids:
        gene_path = GENES_DIR / f"{sid}.json"
        if not gene_path.exists():
            errors.append(f"  ✗ {sid}: Gene 文件不存在")
            continue
        try:
            gene = json.loads(gene_path.read_text())
        except json.JSONDecodeError as e:
            errors.append(f"  ✗ {sid}: Gene JSON 解析错误: {e}")
            continue

        # 检查 GEP 格式
        if gene.get("type") != "Gene":
            errors.append(f"  ✗ {sid}: type != 'Gene' (得到 {gene.get('type')})")
        if gene.get("schema_version") != "1.5.0":
            errors.append(f"  ✗ {sid}: schema_version != '1.5.0'")

        for field in GEP_REQUIRED:
            if field not in gene:
                errors.append(f"  ✗ {sid}: 缺少必需字段 '{field}'")
            elif not gene[field] and field not in ("preconditions",):
                errors.append(f"  ✗ {sid}: 必需字段 '{field}' 为空")

        # 检查关键字段非空
        if not gene.get("signals_match"):
            errors.append(f"  ✗ {sid}: signals_match 为空（G1 级别将无内容）")
        if not gene.get("strategy"):
            errors.append(f"  ✗ {sid}: strategy 为空")

    return errors


def check_skills(scenario_ids):
    """检查 SKILL.md 存在性"""
    errors = []
    for sid in scenario_ids:
        skill_md = SKILLS_DIR / sid / "direct" / "SKILL.md"
        if not skill_md.exists():
            errors.append(f"  ✗ {sid}: 缺少 SKILL.md ({skill_md})")
        else:
            content = skill_md.read_text()
            # 检查必需章节
            for section in ["## Overview", "## Workflow", "## Common Pitfalls"]:
                if section not in content:
                    errors.append(f"  ✗ {sid}: SKILL.md 缺少章节 '{section}'")
    return errors


def check_domain_info(scenario_ids):
    """检查 DOMAIN_INFO 覆盖"""
    errors = []
    # 导入 DOMAIN_INFO
    sys.path.insert(0, str(ROOT))
    from run_evomap_experiments import DOMAIN_INFO

    for sid in scenario_ids:
        if sid not in DOMAIN_INFO:
            errors.append(f"  ✗ {sid}: 不在 DOMAIN_INFO 中")
            continue
        info = DOMAIN_INFO[sid]
        for key in ["domain", "expert", "wrong", "failure_patterns", "signals"]:
            if not info.get(key):
                errors.append(f"  ✗ {sid}: DOMAIN_INFO 缺少 '{key}'")
        if len(info.get("failure_patterns", [])) < 2:
            errors.append(f"  ✗ {sid}: failure_patterns 不足 2 条")
        if len(info.get("signals", [])) < 4:
            errors.append(f"  ✗ {sid}: signals 不足 4 个")

    return errors


def check_gene_serialization(scenario_ids):
    """检查 Gene 在 G1-G4 级别序列化非空"""
    errors = []
    sys.path.insert(0, str(ROOT))
    from gene_builder import serialize_gene

    for sid in scenario_ids:
        gene_path = GENES_DIR / f"{sid}.json"
        if not gene_path.exists():
            continue
        gene = json.loads(gene_path.read_text())

        for level in ["G1", "G2", "G3", "G4"]:
            text = serialize_gene(gene, level)
            if not text.strip():
                errors.append(f"  ✗ {sid}: serialize_gene({level}) 返回空文本")

    return errors


def main():
    print("=" * 60)
    print("Gene-Bench 预检验证")
    print("=" * 60)

    all_errors = []

    # 1. 场景完整性
    print("\n[1/5] 检查场景 (task.md + test_script.py) ...")
    scenario_ids, errors = check_scenarios()
    print(f"  场景数: {len(scenario_ids)}")
    all_errors.extend(errors)
    if not errors:
        print("  ✓ 全部通过")
    else:
        for e in errors:
            print(e)

    # 2. Gene GEP 格式
    print("\n[2/5] 检查 Gene (GEP v1.5.0 格式) ...")
    errors = check_genes(scenario_ids)
    all_errors.extend(errors)
    if not errors:
        print("  ✓ 全部通过")
    else:
        for e in errors:
            print(e)

    # 3. SKILL.md
    print("\n[3/5] 检查 SKILL.md ...")
    errors = check_skills(scenario_ids)
    all_errors.extend(errors)
    if not errors:
        print("  ✓ 全部通过")
    else:
        for e in errors:
            print(e)

    # 4. DOMAIN_INFO
    print("\n[4/5] 检查 DOMAIN_INFO ...")
    errors = check_domain_info(scenario_ids)
    all_errors.extend(errors)
    if not errors:
        print("  ✓ 全部通过")
    else:
        for e in errors:
            print(e)

    # 5. Gene 序列化
    print("\n[5/5] 检查 Gene 序列化 (G1-G4 非空) ...")
    errors = check_gene_serialization(scenario_ids)
    all_errors.extend(errors)
    if not errors:
        print("  ✓ 全部通过")
    else:
        for e in errors:
            print(e)

    # 汇总
    print("\n" + "=" * 60)
    if all_errors:
        print(f"❌ 发现 {len(all_errors)} 个问题")
        sys.exit(1)
    else:
        print(f"✅ 全部 {len(scenario_ids)} 个场景验证通过！")
        print(f"  - {len(scenario_ids)} 个 task.md + test_script.py")
        print(f"  - {len(scenario_ids)} 个 GEP v1.5.0 Gene")
        print(f"  - {len(scenario_ids)} 个 SKILL.md")
        print(f"  - {len(scenario_ids)} 个 DOMAIN_INFO 条目")
        print(f"  - Gene G1-G4 序列化全部非空")
        sys.exit(0)


if __name__ == "__main__":
    main()
