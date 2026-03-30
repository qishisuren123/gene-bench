# Gene-Bench 进度记录

## 2026-03-17: Phase 3 机制探索实验（EX14-EX16）完成

### 新增实验: 600 trials
- EX14 (Failure Authenticity, 180 trials) — 失败的真假
- EX15 (Recipe Combination, 240 trials) — 最优配方组合
- EX16 (Difficulty & Stakes, 180 trials) — 难度感知与利害框架

### 问题修复
- EX15/EX16 首次运行因 API key 未传入全部失败 → 删除错误数据，前台重跑成功

### 关键新发现
1. **双通道机制**: 真实失败 = 信息(+9pp) + 信号(+5pp)，荒谬警告也能 +5pp
2. **编造假失败有毒**: plausible_fake 在 S113 上 0%(比 baseline 50% 还差)
3. **成分不可叠加**: full_recipe(+4.5pp) < 任何单成分(+8~10.5pp)
4. **"代码要上线" = 零成本最优**: high_stakes +7.0pp，不需要任何领域知识
5. **竞争框架伤强模型**: competitive 在 Pro 上 -12.7pp

### 实验总量: 3,168 trials

| 实验组 | 实验 | Trials | 状态 |
|--------|------|--------|------|
| RQ1 | Gene 完整度 G0-G4+L1 | 480 | ✅ |
| RQ2 | Gene vs Skill | 240 | ✅ |
| RQ3 | 错误容忍度 | 180 | ✅ |
| RQ4 | 跨领域迁移 | 48 | ✅ |
| RQ5 | 组合效应 | 100 | ✅ |
| RQ6 | 自生成 Gene | 120 | ✅ |
| RQ7 | 接种效应 | 150 | ✅ |
| EX8 | 记忆 vs 探索 | 270 | ✅ |
| EX9 | 失败引导 | 150 | ✅ |
| EX10 | 角色光谱 | 180 | ✅ |
| EX11 | 失败密度 | 150 | ✅ |
| EX12 | 自我预判 | 180 | ✅ |
| EX13 | 框架效应 | 180 | ✅ |
| EX14 | 失败真假 | 180 | ✅ |
| EX15 | 配方组合 | 240 | ✅ |
| EX16 | 难度感知 | 180 | ✅ |
| Pilot | Gemini 2.5 | 140 | ✅ |

### 产出
- `REPORT.md` — 完整技术报告（18 个核心发现，9 章）
- `data/` — 17 个 JSONL 结果文件 (3,168 trials)

---

## 2026-03-17: EvoMap 双回路实验（EX8-EX13）

### 新增文件
- `run_evomap_experiments.py` — 9 个实验（EX8-EX16）、15 个场景领域信息、多线程并行执行
- `launch_evomap.sh` — 并行启动脚本
- `finish_rq1_parallel.py` — RQ1 并行补完

### 问题修复
- Gemini API key 传递问题 → 直接传入 --gemini-key 参数
- 串行执行太慢 → ThreadPoolExecutor 8 workers，1110 trials 约 20 分钟
- RQ1 串行 3h → 并行后约 10 分钟

---

## 2026-03-17: Gemini API 调试 + 原始 RQ 实验

### 修复
- gemini-3-pro 404 → 改用 gemini-3-pro-preview
- "NO CODE" → 加大 max_output_tokens，修复未闭合代码块提取
- resp.text ValueError → try/except 手动提取 parts
- 缺 pandas/sklearn → 创建 gene-bench conda 环境

### 新增 Gemini 模型
gemini-2.5-pro, gemini-2.5-flash, gemini-3-pro-preview, gemini-3-flash-preview, gemini-3.1-pro-preview, gemini-3.1-flash-lite-preview

---

## 2026-03-16: 项目初始化

### 完成项
1. 项目结构 + 核心模块（gene_builder, gene_injector, budget_tracker）
2. 主实验脚本 run_gene_bench.py — 7 个 RQ trial 生成器
3. 45 个 Gene JSON（30 旧 + 15 新场景）
4. 15 个新场景 (S101-S115)
5. 分析脚本

### 文件清单
```
gene-bench/
├── run_gene_bench.py            # 主实验脚本 (~950 行)
├── run_evomap_experiments.py    # EvoMap 实验 EX8-EX16 (~1300 行)
├── finish_rq1_parallel.py       # RQ1 并行补完
├── launch_evomap.sh             # 并行启动脚本
├── gene_builder.py              # Gene 构建与变异
├── gene_injector.py             # Gene → prompt 注入
├── budget_tracker.py            # 预算追踪
├── distill_genes.py             # 从 SKILL.md 蒸馏 Gene
├── create_new_genes.py          # 新场景 Gene 生成
├── requirements.txt
├── PROGRESS.md
├── REPORT.md                    # ★ 技术报告（18 个发现）
├── genes/                       # 45 个 Gene JSON
├── scenarios/                   # 43 个场景
├── skills/                      # Skill 符号链接
├── data/                        # 17 个 JSONL 结果文件 (3,168 trials)
├── analysis/
└── figures/
```
