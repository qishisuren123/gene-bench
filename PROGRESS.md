# Gene-Bench 进度记录

## 2026-04-02: 全面扩展 — 45 场景、GEP 格式、统一编号

### 本轮修改内容

1. **Gene 格式转 GEP v1.5.0**
   - 运行 `convert_genes_to_gep.py`，45 个 Gene 全部转为 12 字段 GEP 标准格式
   - 包含 type, schema_version, id, category, signals_match, summary, preconditions, strategy, constraints, validation, epigenetic_marks, asset_id

2. **扩展到全部 45 场景**
   - `GENE_SENSITIVE_SCENARIOS = ALL_SCENARIOS`（从 15 → 45）
   - 所有 EX1-EX27 实验统一使用 45 场景

3. **补建 10 个缺失 SKILL.md**
   - S102, S104, S106-S111, S114, S115 全部新建 SKILL.md + references
   - 现在 45/45 场景都有完整 SKILL.md

4. **补建 30 个 DOMAIN_INFO**
   - run_evomap_experiments.py 中 DOMAIN_INFO 从 15 扩展到 45 个场景
   - 每个条目含 domain, expert, adjacent, wrong, failure_patterns(4), signals(8)

5. **统一 RQ/EX 编号**
   - RQ1→EX1, RQ2→EX2, ..., RQ7→EX7
   - CLI 从 `--rq` 改为 `--experiment`
   - 条件名从 `rq1_G0` 改为 `ex1_G0`

6. **预检脚本 validate_setup.py**
   - 检查 45 场景: task.md + test_script + GEP Gene + SKILL.md + DOMAIN_INFO + 序列化非空
   - 全部通过 ✅

### 实验状态（代码已实现，待重跑）

| 实验 | 描述 | 条件数 | Trials (2模型×45场景) | 状态 |
|------|------|--------|----------------------|------|
| EX1 | Gene 完整度 G0-G4+L1 | 6 | 540 | 待跑 |
| EX2 | Gene vs Skill | 4 | 360 | 待跑 |
| EX3 | 错误容忍度 | 6 | 540 | 待跑 |
| EX4 | 跨领域迁移 | ~4 | 48 | 待跑 |
| EX5 | 组合效应 | 5 | 450 | 待跑 |
| EX6 | 自生成 Gene | 6 | 540 | 待跑 |
| EX7 | 接种效应 | 5 | 450 | 待跑 |
| EX8 | 记忆 vs 探索 | 9 | 810 | 待跑 |
| EX9 | 失败引导 | 5 | 450 | 待跑 |
| EX10 | 角色光谱 | 6 | 540 | 待跑 |
| EX11 | 失败密度 | 5 | 450 | 待跑 |
| EX12 | 自我预判 | 6 | 540 | 待跑 |
| EX13 | 框架效应 | 6 | 540 | 待跑 |
| EX14 | 失败真假 | 6 | 540 | 待跑 |
| EX15 | 组合饱和 | 8 | 720 | 待跑 |
| EX16 | 利害框架 | 6 | 540 | 待跑 |
| EX17 | 格式对比 | 6 | 540 | 待跑 |
| EX18 | 进化循环 | 5 | 450 | 待跑 |
| EX19 | vs PE方法 | 7 | 630 | 待跑 |
| EX20 | Gene复用 | 6 | 540 | 待跑 |
| EX21 | 生态对比 | 6 | 540 | 待跑 |
| EX22 | Skill归因 | 7 | 630 | 待跑 |
| EX23 | 截断效应 | 5 | 450 | 待跑 |
| EX24 | 互补性 | 5 | 450 | 待跑 |
| EX25 | 格式重包装 | 5 | 450 | 待跑 |
| EX26 | 进化叙事 | 5 | 450 | 待跑 |
| EX27 | 记忆来源 | 4 | 360 | 待跑 |

**总计: 13,548 trials (EX1-7: 2,928 + EX8-27: 10,620)**

### 下一步
1. 清空 `data/` 旧数据
2. 跑 EX1-7: `python run_gene_bench.py --experiment all --models gemini_pro,gemini_flash --gemini-key "$GEMINI_API_KEY"`
3. 跑 EX8-27: `python run_evomap_experiments.py --experiment all --models gemini_pro,gemini_flash --gemini-key "$GEMINI_API_KEY"`
4. 验证数据完整性
5. 基于实际数据重写报告

---

## 2026-04-01: 严谨性修复 — 审计、Bug 修复、全部实验实现

### 审计发现（详见 AUDIT.md）
- 旧数据: 磁盘只有 2,068 trials（5 个 JSONL），非声称的 4,948
- EX12-EX27 无代码、无数据，PROGRESS.md 中虚假标记为完成
- Bug: MAX_TOKENS=8192（应为 16384），gene 字段名错误导致 G1-G4 关键词为空
- 5 个场景缺少 SKILL.md

### 修复内容
1. `run_gene_bench.py`: MAX_TOKENS 8192 → 16384
2. `gene_builder.py`: 字段名 fallback（signals_match → keywords）
3. 统一场景集（当时 15 个，后扩展到 45）
4. 为 S101, S103, S105, S112, S113 创建 SKILL.md
5. `gene_injector.py`: 新增辅助函数
6. `run_evomap_experiments.py`: 实现 EX12-EX27

---

## 2026-03-17: 初始实验（实际完成部分）

实际有数据: 2,068 trials（RQ1-7: 1,318 + EX8-11: 750）
已知问题: MAX_TOKENS, gene 字段名 bug, 场景集不一致

---

## 2026-03-16: 项目初始化

项目结构 + 核心模块 + 45 个 Gene JSON + 15 个新场景
