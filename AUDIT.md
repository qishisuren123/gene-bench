# Gene-Bench 审计报告

日期: 2026-04-01

## 1. 数据缺口

**声称**: 4,948 次实验 (PROGRESS.md, README.md, REPORT_V3.md)
**实际**: 2,068 次实际数据行（不含 budget_log）

| 文件 | 行数 |
|------|------|
| gene_bench_results.jsonl | 1,318 |
| evomap_ex8_results.jsonl | 270 |
| evomap_ex9_results.jsonl | 150 |
| evomap_ex10_results.jsonl | 180 |
| evomap_ex11_results.jsonl | 150 |
| **合计** | **2,068** |

EX12-EX27（共 16 个实验）在 PROGRESS.md 中标记为 ✅ 完成，但磁盘上不存在对应的数据文件，也不存在实验代码实现。

## 2. 16 个实验无代码无数据

`run_evomap_experiments.py` 只实现了 EX8-EX11（4 个实验），以下实验在任何代码文件中都没有实现：

| 实验 | 描述 | PROGRESS.md 状态 | 实际状态 |
|------|------|------------------|----------|
| EX12 | 自我预判 | ✅ (180 trials) | 无代码、无数据 |
| EX13 | 框架效应 | ✅ (180 trials) | 无代码、无数据 |
| EX14 | 失败真假 | ✅ (180 trials) | 无代码、无数据 |
| EX15 | 配方组合 | ✅ (240 trials) | 无代码、无数据 |
| EX16 | 难度感知 | ✅ (180 trials) | 无代码、无数据 |
| EX17 | 格式对比 | 不存在 | 无代码、无数据 |
| EX18 | 进化循环 | 不存在 | 无代码、无数据 |
| EX19 | vs PE方法 | 不存在 | 无代码、无数据 |
| EX20 | Gene复用 | 不存在 | 无代码、无数据 |
| EX21 | 生态对比 | 不存在 | 无代码、无数据 |
| EX22 | Skill归因 | 不存在 | 无代码、无数据 |
| EX23 | 截断效应 | 不存在 | 无代码、无数据 |
| EX24 | 互补性 | 不存在 | 无代码、无数据 |
| EX25 | 格式重包装 | 不存在 | 无代码、无数据 |
| EX26 | 进化叙事 | 不存在 | 无代码、无数据 |
| EX27 | 记忆来源 | 不存在 | 无代码、无数据 |

## 3. 代码 Bug

### 3a. MAX_TOKENS 不一致
- `run_gene_bench.py` 第 139 行: `MAX_TOKENS = 8192`
- 报告和代码注释暗示应为 16384
- 影响: 长代码可能被截断，降低通过率

### 3b. Gene 字段名错误
- `gene_builder.py` 第 113 行: `gene.get("signals_match", [])`
- 所有 45 个 Gene JSON 文件使用 `keywords` 字段，不是 `signals_match`
- 影响: **G1-G4 所有级别的关键词行始终为空**，本质上 G1≈G0, G2 只有 summary
- 这意味着 RQ1 的"G1 仅关键词"条件实际注入了空字符串

### 3c. RQ 实验场景集不一致
- RQ1 使用 40 个场景, RQ2 使用 30 个, RQ3 使用 15 个, 各不相同
- EX8-EX11 使用 15 个 GENE_SENSITIVE_SCENARIOS
- 不同场景集导致 baseline 不可比, delta 计算无意义

## 4. 缺少 SKILL.md

15 个 GENE_SENSITIVE_SCENARIOS 中有 5 个没有 SKILL.md:

| 场景 | skills/ 目录 | 影响 |
|------|-------------|------|
| S101_climate_attribution | 不存在 | RQ2 L1/L4 条件为空 |
| S103_instrumental_variable | 不存在 | RQ2 L1/L4 条件为空 |
| S105_community_detection | 不存在 | RQ2 L1/L4 条件为空 |
| S112_midi_chords | 不存在 | RQ2 L1/L4 条件为空 |
| S113_inventory_reorder | 不存在 | RQ2 L1/L4 条件为空 |

## 5. PROGRESS.md 虚假完成标记

PROGRESS.md 记录 "EX12-EX16 完成, 共 3,168 trials"，但:
- EX12-EX16 没有任何代码实现
- 没有对应的数据文件
- 描述的"关键新发现"没有数据支撑

## 6. 修复计划

1. 修复 MAX_TOKENS → 16384
2. 修复 gene 字段 fallback: `signals_match` → `keywords`
3. 统一所有 RQ 使用 15 个 GENE_SENSITIVE_SCENARIOS
4. 为 5 个场景创建 SKILL.md
5. 实现 EX12-EX27 全部 16 个实验
6. 清空旧数据, 从零重跑
7. 基于实际数据重写报告
