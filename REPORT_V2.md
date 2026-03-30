# 如何用策略引导让大模型写出更好的代码

**Gene-Bench 实验技术报告 · Phase 1–5+**
**4,948 次受控实验 · 43 个科学计算场景 · 2 个 Gemini 模型**

---

## 目录

1. [背景：为什么需要引导？](#1-背景为什么需要引导)
2. [什么是 Gene？为什么需要 Gene？](#2-什么是-gene为什么需要-gene)
3. [实验设计](#3-实验设计)
4. [Gene 的发现与使用技巧](#4-gene-的发现与使用技巧)
5. [Skill 的发现与使用技巧](#5-skill-的发现与使用技巧)
6. [记忆回路：最强引导模式](#6-记忆回路最强引导模式)
7. [其他有趣发现](#7-其他有趣发现)
8. [跨实验规律与总体结论](#8-跨实验规律与总体结论)

---

## 1. 背景：为什么需要引导？

让大模型写代码，直接给任务描述就行吗？不行。

对同一道科学计算题——比如"用 scipy 检测 UV-Vis 光谱中的吸收峰"——Gemini 3.1 Pro 在毫无引导的情况下通过率只有 **0%**。但如果在 prompt 里加上四句话描述前人踩过的坑，通过率立刻跳到 **100%**。同样的代码，同样的模型，差距来自引导的有无。

这个实验系列的核心问题就是：**什么样的引导最有效？多少引导是刚好够用？引导是怎么生效的？**

我们借助 EvoMap 平台的两个核心概念——**Gene（基因）** 和 **Memory Loop（记忆回路）**——与传统的 Skill 文档做了系统的正面对比，跑了 4,948 次受控实验。

---

## 2. 什么是 Gene？为什么需要 Gene？

### 2.1 起点：Skill 文档

每个科学计算任务都有一份 **SKILL.md**——由领域专家编写的完整任务指南，包含：

```
## Overview      ← 一句话描述任务
## Workflow      ← 7 步操作流程
## Common Pitfalls  ← 4-5 个常见陷阱
## Error Handling   ← 边界情况处理
## Quick Reference  ← API 签名速查
```

加上两个 references 文件：
- `api_notes.md`：函数签名、参数说明（~80 tokens）
- `examples.md`：完整代码示例（~200 tokens）

整体约 **600-800 tokens**。这就是传统的"知识管理"方式——把专家知识整理成文档，塞给模型。

### 2.2 问题：Skill 文档太重了

600 tokens 的文档塞进 prompt，并不一定有效。实验证明（见第 5 节），完整 SKILL.md 在某些场景上效果等于没有，在弱模型上甚至有害。信息太多，模型不知道重点在哪。

### 2.3 Gene 是什么

Gene 是从 SKILL.md 蒸馏出来的**精炼策略模板**，遵循 EvoMap GEP v1.5.0 格式：

```json
{
  "id": "gene_S012_uv_spectroscopy",
  "signals_match": ["absorbance", "wavelength", "peak detection", "FWHM"],
  "summary": "Detect and analyze absorption peaks in UV-Vis spectra",
  "strategy": [
    "Load CSV data with wavelength column and sample absorbance columns",
    "Apply scipy.signal.find_peaks with prominence-based detection",
    "AVOID: Wavelength spacing assumption — convert min-distance using actual spacing",
    "AVOID: FWHM errors — peak_widths returns indices, convert to wavelength units",
    "Handle samples with no detected peaks by returning empty arrays"
  ]
}
```

注入时用 XML 标签包装：
```xml
<strategy-gene>
  [序列化的 Gene 内容]
</strategy-gene>
```

**Gene 的构建逻辑：** 不保留 Workflow（怎么一步步做），而是保留最核心的**策略方向**和最重要的**失败预防**（AVOID 步骤）。目标是用最少的 token 传递最高密度的信息。

### 2.4 Gene 的级别体系

Gene 有 5 个完整度级别，从空到完整：

| 级别 | 内容 | ~Tokens |
|------|------|---------|
| G0 | 无引导（baseline） | 0 |
| G1 | 仅 `signals_match` 关键词 | ~25 |
| G2 | + `summary` 一句话描述 | ~50 |
| **G3** | **+ 核心 strategy 步骤（不含 AVOID）** | **~120** |
| G4 | + AVOID 陷阱 + preconditions | ~200 |
| L1 | 完整 SKILL.md（对照组） | ~600 |

**G3 是标准配置**，在大多数实验中用作对照基准。

---

## 3. 实验设计

### 3.1 基础设施

| 维度 | 配置 |
|------|------|
| 模型 | Gemini 3.1 Pro Preview（强）、Gemini 3.1 Flash Lite Preview（弱） |
| 场景 | 43 个科学计算任务（光谱、地震、气候、图分析、音乐等） |
| 评估 | 每个场景有专属测试脚本，自动计算 pass rate（通过测试项数/总测试项数） |
| 参数 | temperature=0.0（确定性输出），max_tokens=16384 |
| 总计 | **4,948 次 trials** |

### 3.2 场景分类

43 个场景按难度分三类：

- **Always-pass（≥95%）：10 个** — 模型已经会了，引导不影响结果
- **Always-fail（≤5%）：11 个** — 超出模型能力，引导也救不了
- **Gene-sensitive（5%-95%）：22 个** — 引导策略的差异在这里显现

所有关键实验都在 gene-sensitive 场景上运行。

### 3.3 实验矩阵

全部实验分 5 个阶段：

| 阶段 | 实验编号 | 研究问题 | Trials |
|------|---------|---------|--------|
| Phase 1 | RQ1-RQ7 | Gene 完整度、Gene vs Skill、错误容忍度、复用性、作者效应 | 1,318 |
| Phase 2 | EX8-EX13 | 记忆 vs 探索双回路、失败引导、角色、密度、自我预判、框架 | 1,110 |
| Phase 3 | EX14-EX16 | 失败的真假、配方组合、难度感知 | 600 |
| Phase 4 | EX17-EX21 | 格式优势、进化循环、vs 常见方法、复用性、生态对比 | 900 |
| Phase 5+ | EX22-EX27 | Skill 成分归因、预算对决、互补性、Pitfalls 重包装、进化叙事、记忆来源 | 1,020 |
| **合计** | | | **4,948** |

### 3.4 执行方式

每个 trial 流程：

```
1. 读取场景的 task.md（任务描述）
2. 根据实验条件构建 system_prompt（Gene / Skill / 记忆 / 无）
3. 调用 Gemini API → 提取 ```python 代码块
4. 在隔离沙箱运行代码（超时 120 秒）
5. 运行测试脚本，记录 PASS/FAIL 和 pass_rate
6. 结果写入 JSONL 文件（支持断点续跑）
```

使用 ThreadPoolExecutor 8 线程并行，1,020 trials 约 55 分钟完成。

---

## 4. Gene 的发现与使用技巧

### 4.1 Gene 能带来多大提升？

在 gene-sensitive 场景上，G3 Gene 相比无引导（G0）：

- 整体 pass rate：**56.3% → 64.6%（+8.3pp）**
- 最极端案例：S012（UV-Vis 光谱），G0 = 0%，加上 Gene 后直接跳到可用水平

但这个均值掩盖了一个重要现象——**Gene 的效果在不同场景间差异极大**。有些场景 Gene 帮助很大，有些场景 Gene 会"有毒"（反而让通过率下降）。这就是为什么要搞清楚 Gene 的生效机制。

### 4.2 最优完整度：G3，不是更多

**实验：RQ1（480 trials）**

| Gene 级别 | 内容 | Pro | Flash | 整体 |
|----------|------|-----|-------|------|
| G0 (baseline) | 无引导 | 48.7% | 37.2% | 43.0% |
| G1 | 仅关键词 | 49.6% | 43.2% | 46.4% |
| G2 | +summary | 51.4% | 45.4% | 48.4% |
| **G3** | **+strategy** | **52.4%** | **44.7%** | **48.5%** |
| G4 | +AVOID+preconditions | 48.4% | 46.1% | 47.3% |
| L1 | 完整 SKILL.md | 51.0% | 43.2% | 47.1% |

**关键发现：G3 是峰值，G4 反而回落。**

加上 AVOID 陷阱和 preconditions 后（G4），Pro 的通过率反而比 G3 下降了 4pp。完整 SKILL.md（L1）也不如 G3，尽管 token 量多了 5 倍。

**原因：** 超过 G3 的额外信息开始产生噪声，稀释了核心策略的信号。G3 的 ~120 tokens 是信息密度的甜蜜点。

> **使用建议：** 用 G3 标准 Gene（~120 tokens），不要试图"加入更多信息"。

### 4.3 Gene 的错误容忍度：残缺的 Gene 也能用

**实验：RQ3（180 trials）**

我们故意给 Gene 注入各种"变异"，测试它的容错能力：

| 变异类型 | 说明 | 整体 pass rate | vs clean G3 |
|---------|------|--------------|-------------|
| Clean G3 | 正确的 Gene | 48.5% | baseline |
| **stale_paradigm** | **过时技术（如"用 csv 替代 pandas"）** | **51.0%** | **+2.5pp** |
| inverted_priority | 步骤顺序颠倒 | 49.6% | +1.1pp |
| wrong_domain | 用错误领域的 Gene | 48.5% | +0.0pp |
| overconstrained | 过度限制约束 | 47.3% | -1.2pp |
| wrong_algorithm | 推荐错误算法 | 46.1% | -2.4pp |

**最反直觉的发现：stale_paradigm 比正确的 Gene 还好（+2.5pp）。**

"用 csv 模块而不是 pandas"这种过时建议反而有效。可能的原因：过时策略破坏了 Gene 中可能误导模型的具体细节，但保留了有用的结构信息。就像一张模糊的地图——虽然细节不准，但大方向还在。

另一个发现：wrong_domain（用完全无关领域的 Gene）效果等于 clean G3，说明 Gene 的价值主要来自**结构和格式**，而非具体的领域知识。

> **使用建议：** Gene 即使有小错误也通常安全，只有推荐了根本错误的算法才会造成伤害。

### 4.4 Gene 的作者是谁无关紧要

**实验：RQ6（120 trials）**

我们用 5 个不同"作者"生成同一场景的 Gene：人类专家、GPT-5.4、Claude Haiku、Claude Opus、Gemini-3-Pro。

| Gene 作者 | Pass Rate |
|----------|-----------|
| Human | 82.2% |
| GPT-5.4 | 82.2% |
| Claude Haiku | 82.2% |
| Claude Opus | 82.2% |
| Gemini-3-Pro | 82.2% |
| No Gene | 76.3% |

**所有作者在每个场景上产生完全相同的结果。**

Gene 是一个**二进制开关**——有效果 vs 没有效果，而不是一个精细的知识载体。是否存在 Gene 比 Gene 的质量更重要。这意味着用大模型自动生成 Gene 和人工编写 Gene 效果完全相同，大幅降低了构建成本。

> **使用建议：** 可以用任何 LLM 自动生成 Gene，不需要人工精雕细琢。

### 4.5 Gene 的跨任务复用性

**实验：EX20（180 trials）**

Gene 能从一个任务迁移到相关任务吗？

| Gene 来源 | 说明 | Pro | Flash |
|---------|------|-----|-------|
| exact_gene | 精确匹配此任务的 Gene | 73.3% | 33.3% |
| sibling_gene | 同领域相关任务（如光谱→光谱） | 66.7% | 40.0% |
| generic_gene | 无任何领域知识的通用元基因 | 66.7% | **53.3%** |
| cousin_gene | 跨领域结构相似任务 | 73.3% | **20.0%** |
| none | 无 Gene | 66.7% | 40.0% |

**强模型（Pro）和弱模型（Flash）的反应方向完全相反：**

- **Pro**：精确 Gene 和跨域 Gene 效果相同（73.3%），说明 Gene 的结构比内容更重要
- **Flash**：具体领域 Gene 有害！cousin_gene 让 Flash 从 40% 跌到 20%；只有通用元基因（不含任何领域知识）对 Flash 安全（53.3%）

> **使用建议：**
> - Pro（强模型）：可以大胆跨任务复用 Gene，效果损失极小
> - Flash（弱模型）：**不要用具体领域 Gene**，只用记忆回路（memory_failures）或通用元基因

---

## 5. Skill 的发现与使用技巧

### 5.1 各成分的价值差异极大

**实验：EX22（210 trials）**

把 SKILL.md 拆开，逐段测试效果（baseline = 56.3%）：

| 成分 | 内容 | ~Tokens | Pass Rate | vs baseline |
|------|------|---------|-----------|-------------|
| skill_examples | references/examples.md（代码示例） | ~200 | 62.5% | **+6.2pp** |
| skill_full_l1 | 完整 SKILL.md | ~600 | 62.4% | +6.0pp |
| skill_workflow | ## Workflow 章节 | ~150 | 59.6% | +3.3pp |
| none | 无引导 | 0 | 56.3% | — |
| skill_api_notes | references/api_notes.md（API 签名） | ~80 | 56.0% | **-0.4pp** |
| skill_pitfalls | ## Common Pitfalls 章节 | ~120 | 55.1% | **-1.3pp** |

**几个令人惊讶的发现：**

1. **API 签名（api_notes）几乎无效（-0.4pp）。** 给模型查 API 参数表没有用——它自己知道怎么调用函数，缺的是策略和陷阱知识。

2. **Pitfalls 原文有害（-1.3pp）。** Common Pitfalls 章节讲的都是关键陷阱，理论上应该很有用，但 Markdown 格式的原文反而让通过率微降。后续实验（EX25）揭示了原因：不是内容问题，是格式问题（见 5.4 节）。

3. **代码示例是最有价值的成分（+6.2pp）。** 完整的代码示例和完整 SKILL.md 效果相当（+6.2pp vs +6.0pp），说明 SKILL.md 的价值几乎全部来自 examples。

> **使用建议：** 如果要用 Skill，只注入 `examples.md`，跳过 `api_notes.md` 和 Pitfalls 原文。

### 5.2 截断比完整更好

**实验：EX23（150 trials）——在 ~120 token 预算下的对决**

把各 Skill 成分截断到和 Gene G3 相当的 token 量（~120 tokens）：

| 条件 | 内容 | Pass Rate | vs baseline |
|------|------|-----------|-------------|
| skill_pitfalls_short | Pitfalls 前 3 条（截断） | 63.9% | **+7.6pp** |
| skill_workflow_short | Workflow 前 3 步（截断） | 60.5% | +4.2pp |
| skill_mixed_short | Overview 首句 + 前 2 条 Pitfalls | 57.3% | +1.0pp |
| none | 无引导 | 56.3% | — |

**最反直觉的发现：截断后的 Pitfalls（前 3 条）= +7.6pp，完整 Pitfalls = -1.3pp。**

把 5 条 pitfalls 截短到前 3 条，效果从负变成了 +7.6pp。**精炼反而比完整更有效**，再次验证"信息过载"效应。

混合（Overview + Pitfalls）效果最差（+1.0pp），说明在有限 token 预算下混搭不如专注于单一成分。

> **使用建议：** 如果要使用 Skill 的 Pitfalls，截取前 2-3 条最重要的，比注入全部 5 条更有效。

### 5.3 Gene 和 Skill 是互补还是冗余？

**实验：EX24（180 trials）**

| 条件 | 内容 | ~Tokens | Pass Rate | vs baseline |
|------|------|---------|-----------|-------------|
| gene_g3 | Gene only | ~120 | 64.6% | +8.3pp |
| gene_plus_examples | Gene + examples.md | ~320 | 64.0% | +7.7pp |
| skill_full_l1 | 完整 SKILL.md | ~600 | 62.4% | +6.0pp |
| gene_plus_api | Gene + api_notes.md | ~200 | 58.8% | +2.5pp |
| skill_api_notes | API 参考 only | ~80 | 56.0% | -0.4pp |

**结论：Gene 和 Skill 是冗余关系，不是互补。**

- gene_plus_examples（+7.7pp）≈ gene_g3（+8.3pp）：加上代码示例几乎没有增益
- gene_plus_api（+2.5pp）< gene_g3（+8.3pp）：加上 API 参考反而让 Gene 效果下降 5.8pp

Gene 已经包含了最关键的信息，Skill 的成分并不能提供增量价值。更糟糕的是，增加内容会稀释 Gene 的核心信号。

> **使用建议：** 在使用 Gene 的情况下，不要再堆叠 Skill 成分。

### 5.4 最重要发现：格式比内容更重要

**实验：EX25（180 trials）**

Common Pitfalls 原文有害（-1.3pp），这是内容问题还是格式问题？我们把同样的 Pitfalls 内容用不同格式重新包装：

| 条件 | 格式 | Pass Rate | vs baseline |
|------|------|-----------|-------------|
| memory_failures（人工编写） | EvoMap `<memory-failures>` XML | 67.2% | +10.9pp |
| skill_pitfalls_as_failures | Pitfalls → EvoMap XML（自动转换） | 65.7% | **+9.4pp** |
| skill_pitfalls_warning | Pitfalls + WARNING 框架 | 64.2% | +7.8pp |
| none | 无引导 | 56.3% | — |
| skill_pitfalls_raw | Pitfalls 原文（Markdown） | 55.1% | **-1.3pp** |

**这是 Phase 5 最核心的发现。**

同样的 Pitfalls 内容：
- Markdown 原文 → **-1.3pp（有害）**
- 换成 EvoMap XML 格式 → **+9.4pp（有效）**

两者差距 10.7pp，**仅仅通过重新格式化就完成了**。

而且，自动转换的效果（+9.4pp）非常接近人工精心编写的失败案例（+10.9pp），差距只有 1.5pp。这意味着：

> **实用建议：把任何文档里的 Pitfalls 提取出来，包装成 `<memory-failures>` XML 格式，就能获得接近手工策划的效果。**

按任务类型细分后，发现了进一步的规律：

| 任务类型 | baseline | XML 格式 | WARNING 框架 | Markdown 原文 |
|---------|---------|---------|------------|------------|
| API-DEPENDENT（5 场景） | 70.0% | +9.2pp | +9.2pp | -0.8pp |
| FORMULA-DEPENDENT（6 场景） | 34.2% | **+16.7pp** | +10.4pp | +2.5pp |
| PATTERN-DEPENDENT（4 场景） | 72.5% | -1.1pp | +2.3pp | **-7.4pp** |

- **公式型任务收益最大**（需要精确算法，Pitfalls 提示具体错误最有帮助）
- **模式型任务 Pitfalls 有害**（这类任务更依赖整体模式识别，具体警告反而干扰）

### 5.5 Skill 可以自动替代人工策划

**实验：EX27（120 trials）——失败知识来源对比**

| 来源 | 说明 | Pass Rate | vs baseline |
|------|------|-----------|-------------|
| memory_curated | 人工编写的失败案例 | 67.2% | +10.9pp |
| memory_from_skill | 从 SKILL.md Pitfalls 自动转换 | 65.7% | **+9.4pp** |
| memory_self_generated | 模型 Round 1 自己预测失败，Round 2 注入 | 60.5% | +4.2pp |
| none | 无引导 | 56.3% | — |

三种来源的排序符合直觉：人工策划 > 自动转换 > 模型自生成。但关键在于**差距**：

- 自动转换 vs 人工策划：仅差 1.5pp——**文档转换可替代人工策划**
- 模型自生成 vs 人工策划：差 6.7pp——**模型无法通过自我反思完全替代外部知识**

这对工程实践有重要意义：不需要人工从零写失败案例，从现有的 SKILL.md 自动提取 Pitfalls 并重格式化，就能获得 86% 的效果。

> **完整的 Skill 使用建议：**
>
> 1. **最优选择**：提取 SKILL.md 的 Common Pitfalls，转换为 `<memory-failures>` XML
> 2. **次优选择**：直接注入 `examples.md`（代码示例）
> 3. **可选补充**：Pitfalls 前 2-3 条截断版（不要完整 5 条）
> 4. **避免**：完整 SKILL.md 原文（过量）、api_notes.md（无效）、Pitfalls 原文 Markdown（有害）
> 5. **绝对避免**：在已有 Gene 的情况下再堆 Skill（信息稀释）

---

## 6. 记忆回路：最强引导模式

### 6.1 核心数据

**实验：EX8（270 trials）**——直接对比 EvoMap 的记忆和探索两个回路

| 条件 | 说明 | Pass Rate | vs baseline |
|------|------|-----------|-------------|
| **memory_failures** | **告诉模型前人怎么失败的** | **87.1%** | **+14.6pp** |
| exploration_objective | 给出明确目标 | 83.7% | +11.2pp |
| exploration_direction | 给出策略方向 | 79.5% | +7.0pp |
| gene_g3 | 标准 Gene | 76.4% | +3.9pp |
| none | 无引导 | 72.5% | — |
| **exploration_full** | **同时给出所有组件** | **65.6%** | **-7.0pp** |

`memory_failures`（~80 tokens，3-4 条失败案例）是全场最强。它的 prompt 格式：

```
Based on analysis of past failed attempts at similar tasks,
these failure patterns have been documented:

<memory-failures>
Common failure patterns:
  - Forgetting to convert min-distance from nm to data point indices
  - Using raw peak_widths output without converting back to wavelength units
  ...

Each of these has caused solution failures in >30% of past attempts.
</memory-failures>

Learn from these failures. Avoid these specific pitfalls in your implementation.
```

### 6.2 为什么失败知识有效？双通道机制

**实验：EX14（180 trials）**——测试失败引导生效的原因

| 条件 | 内容 | Pass Rate | vs baseline |
|------|------|-----------|-------------|
| real_failures | 真实的领域失败模式 | 87.1% | **+14.6pp** |
| generic_warnings | 通用编程警告（非领域特定） | 80.1% | +7.6pp |
| absurd_warnings | 完全荒谬的警告 | 77.5% | **+5.0pp** |
| plausible_fake | 看起来合理但编造的失败 | 73.0% | +0.5pp |
| none | 无引导 | 72.5% | — |
| cross_domain | 来自无关领域的真实失败 | 71.1% | -1.5pp |

**荒谬警告（+5.0pp）是最令人震惊的结果。** 内容是"确保代码不会产生自我意识"这种完全无意义的话，但居然有效。

这揭示了失败引导的**双通道机制**：

- **信息通道（~+9pp）**：真实失败提供了模型不知道的具体信息（从 real 到 generic 的差距）
- **信号通道（~+5pp）**：WARNING / CRITICAL 等关键词本身激活了模型的谨慎模式（荒谬警告也能触发）

**关键禁忌：编造的"合理"失败最危险（+0.5pp，接近无效）。** 某些场景上 plausible_fake 造成严重伤害——S113 库存优化：plausible_fake = 0%，真实失败 = 100%，荒谬警告 = 100%。

> **原则：有真实失败用真实失败；没有真实失败宁用荒谬警告，也不要编造领域失败。**

### 6.3 最优失败密度：2 条

**实验：EX11（150 trials）**

| 失败条数 | Pro | Flash | 整体 | vs 0 条 |
|---------|-----|-------|------|---------|
| 0 条 | 78.1% | 66.9% | 72.5% | — |
| 1 条 | 91.4% | 66.5% | 79.0% | +6.5pp |
| **2 条** | **91.4%** | **74.3%** | **82.9%** | **+10.4pp** |
| 3 条 | 84.8% | 75.9% | 80.3% | +7.8pp |
| 4 条 | 84.8% | 76.1% | 80.4% | +7.9pp |

2 条是甜蜜点。Pro 在 1 条时已饱和，Flash 在 2 条时达到最优。超过 2 条后边际收益为零。

### 6.4 WARNING 框架的威力

**实验：EX13（180 trials）**——同样的策略信息，不同的表述方式

| 表述框架 | 示例 | Pass Rate | vs baseline |
|---------|------|-----------|-------------|
| **warning** | "跳过此步骤会导致测试失败" | **83.1%** | **+10.5pp** |
| socratic | "你有没有考虑过X会怎样？" | 79.1% | +6.6pp |
| suggestive | "你可以考虑..." | 76.7% | +4.1pp |
| none | 无引导 | 72.5% | — |
| imperative | "你必须..." | 72.4% | -0.1pp |
| **teaching** | **"这背后的原理是..."** | **65.6%** | **-6.9pp** |

- **Warning 框架全面碾压（+10.5pp）**：把步骤改写成"不做这个会失败"的表述，比正向的"应该怎么做"效果好一倍多
- **命令语气无效（-0.1pp）**："你必须"和没说一样
- **Teaching 框架有害（-6.9pp）**：解释原理让模型花精力在理解上，而不是实现上。Flash 上 teaching = 53.7%，全场最低

### 6.5 成分不可叠加——最反直觉的组合效应

**实验：EX15（240 trials）**

找到三个各自 +8-10pp 的最优成分：novice 角色（+8pp）、warning 框架（+10.5pp）、2 条失败案例（+10.4pp）。把它们组合起来：

| 组合 | Pass Rate | vs baseline |
|------|-----------|-------------|
| warning_only | 83.1% | +10.5pp |
| failures_only | 82.9% | +10.4pp |
| novice_only | 80.6% | +8.0pp |
| novice + failures | 82.8% | +10.3pp |
| warning + failures | 79.7% | +7.1pp |
| novice + warning | 78.6% | +6.1pp |
| **novice + warning + failures（全组合）** | **77.1%** | **+4.5pp** |

**理论加性预测：+28.9pp。实际：+4.5pp。只达到预测值的 15.6%。**

**全部三个成分叠加，反而是所有非 baseline 条件中最差的。**

三个成分都通过"激活谨慎模式"生效。当谨慎模式已被一个成分充分触发，再加更多成分不会提供增量，只会占用 token 空间、稀释信号。

> **铁律：选一个最强成分全力使用，不要混搭。**

### 6.6 一轮预防 > 两轮重试

**实验：EX18（150 trials）**

| 策略 | API 调用次数 | ~Tokens | Pass Rate | vs 无引导 |
|------|------------|---------|-----------|---------|
| **单轮 + EvoMap 记忆** | **1 次** | **~1,893** | **73.3%** | **+20pp** |
| 两轮 + 具体错误信息 | 2 次 | ~2,811 | 66.7% | +13.3pp |
| 两轮 + 错误 + EvoMap 记忆 | 2 次 | ~2,845 | 66.7% | +13.3pp |
| 两轮 + 仅告知失败 | 2 次 | ~2,856 | 63.3% | +10pp |

单轮 EvoMap 记忆注入比两轮带错误重试高 6.6pp，同时省 33% token，省 1 次 API 调用。

**第二轮注入 EvoMap 记忆没有额外收益**（和只给错误信息一样）。EvoMap 记忆的价值在**首轮预防**，而不是事后补救。

> **原则：把失败知识提前告诉模型，比让它失败再修补更有效，也更便宜。**

---

## 7. 其他有趣发现

### 7.1 新手角色 > 专家角色

**实验：EX10（180 trials）**

| 角色 | Pro | Flash | 整体 | vs baseline |
|------|-----|-------|------|-------------|
| **novice**（"你是编程学生"） | **91.5%** | 69.7% | **80.6%** | **+8.0pp** |
| generic_senior（"你是资深工程师"） | 84.2% | **74.2%** | 79.2% | +6.7pp |
| expert_adjacent（相关领域专家） | 84.8% | 62.9% | 73.8% | +1.3pp |
| expert_wrong（完全不相关专家） | 84.2% | 62.7% | 73.5% | +0.9pp |
| **expert_exact**（**精确领域专家**） | **77.6%** | 69.2% | 73.4% | **+0.9pp** |
| none | 78.1% | 66.9% | 72.5% | — |

Pro 上，novice（91.5%）比 expert_exact（77.6%）高 **13.9pp**。

**机制：** novice persona 触发"谨慎模式"——更多验证、更多边界检查、更保守的实现。expert persona 触发"自信模式"——跳过验证步骤，使用复杂但容易出错的方法。

**专家领域精度完全无关**：expert_wrong（不相关领域专家 = 0.9pp）≈ expert_exact（精确领域专家 = 0.9pp）。告诉模型"你是 NLP 工程师"去解光谱问题，和"你是光谱化学家"效果完全一样。这说明 persona 的作用不是传递知识，而是激活态度。

### 7.2 "代码要上线"是零成本最优引导

**实验：EX16（180 trials）**

| 难度/利害框架 | prompt | Pass Rate | vs baseline |
|------------|--------|-----------|-------------|
| **high_stakes** | **"代码将部署到生产环境"** | **79.5%** | **+7.0pp** |
| easy_explicit | "这是一道简单任务" | 76.5% | +3.9pp |
| hard_explicit | "只有 30% 的 AI 能通过" | 74.7% | +2.1pp |
| none | 无引导 | 72.5% | — |
| **competitive** | **"与 100 个 AI 竞争"** | **70.5%** | **-2.1pp** |

一句 "This code will be deployed in a production system where correctness is paramount" 就能获得 **+7.0pp**，和很多复杂的 prompt engineering 方法效果相当，而且完全不需要任何领域知识。

**"这很简单" > "这很难"**（+3.9pp vs +2.1pp）——"这很简单"让模型选择更简洁的实现，反而减少了错误。

**竞争框架对强模型有害**：Pro 在 competitive 条件下 -12.7pp（跌到 65.4%），Flash 却 +8.6pp（升到 75.5%）。竞争压力让强模型追求"炫技"；弱模型被激励了。

### 7.3 自我预判是幻觉，橡皮鸭法对强模型有效

**实验：EX12（180 trials）**

| 方法 | 说明 | Pass Rate | vs baseline |
|------|------|-----------|-------------|
| curated_failures | 外部给出失败案例 | 79.5% | +7.0pp |
| **rubber_duck**（Pro） | **"先解释你的方案再编码"** | **91.4%** | **+16.6pp** |
| gene_g3 | Gene 引导 | 76.4% | +3.9pp |
| **self_anticipation** | **"先想想可能的失败再编码"** | **72.4%** | **≈ 0pp** |

- **自我预判（self_anticipation）完全无效**：让模型自己预测可能失败的地方，等于白说。模型无法可靠地预见自己的盲点——这正是外部提供失败知识的意义所在。

- **橡皮鸭法对 Pro 极有效（+16.6pp）**：先让强模型把实现思路讲一遍，再写代码，通过自我解释发现逻辑漏洞。但对 Flash（弱模型）只有 -6.2pp，弱模型的自我解释能力不足以产生校正效果。

### 7.4 进化叙事有附加价值

**实验：EX26（180 trials）**

| 条件 | 说明 | Pass Rate | vs baseline |
|------|------|-----------|-------------|
| **evolution_full** | Gene + EvolutionEvent（含失败尝试历史） | **67.4%** | **+11.1pp** |
| gene_g3 | 裸 Gene（仅最终策略） | 64.6% | +8.3pp |
| capsule_style | GEP Capsule 格式 | 62.5% | +6.2pp |
| failed_attempts_only | 仅失败记录，无最终策略 | 59.0% | +2.7pp |
| gene_with_confidence | Gene + GDI 分数/置信度 | 57.8% | +1.4pp |

告诉模型"这个策略是经过 3 次失败尝试后进化出来的"（evolution_full），比只给最终策略（gene_g3）多 +2.8pp。

**EvoMap 的 EvolutionEvent 设计有实验依据。**

几个边界情况：
- **仅有失败记录，没有最终策略（+2.7pp）**——知道失败但不知道正确做法，帮助很有限
- **GDI 置信度元数据（+1.4pp）**——告诉模型"这个 Gene 的置信度是 0.85"，几乎无效。纯数字元数据对模型没有引导作用

---

## 8. 跨实验规律与总体结论

### 8.1 信息量与效果的倒 U 关系

| token 量 | 最佳条件 | 效果 |
|---------|---------|------|
| ~20 tok | "你是学生"/ "这会上线" | +7-8pp |
| **~80 tok** | **memory_failures（2 条失败）** | **+14.6pp** ← 全场最优 |
| ~120 tok | Gene G3 | +8.3pp |
| ~157 tok | EvoMap 记忆（EX21 配置） | +20pp（特定场景） |
| ~200 tok | exploration_full（全部组件） | **-7pp** |
| ~477 tok | SKILL.md 全文 | +0pp |
| ~700 tok | SKILL.md + 代码示例 | **-3.3pp** |

存在明确的最优区间（**50-160 tokens**）。超过后效果急剧下降乃至转负。

### 8.2 组合惩罚定律

在 4 个独立实验中，将多个最优成分组合后的结果：

| 实验 | 单成分最优 | 组合效果 | 惩罚 |
|------|-----------|---------|------|
| EX8 | memory_failures +14.6pp | exploration_full（全组件）-7.0pp | -21.6pp |
| EX15 | warning_only +10.5pp | 三成分全组合 +4.5pp | -6.0pp |
| EX21 | memory_only +20pp | Gene+记忆组合 +3.3pp | -16.7pp |

**结论：每增加一个引导维度，效果衰减，不是叠加。** 所有高效成分都通过触发"谨慎模式"生效，谨慎模式被触发后是二值状态，多次触发没有增量。

### 8.3 强弱模型应采用不同策略

| 策略 | Pro（强模型） | Flash（弱模型） |
|------|------------|--------------|
| 最有效的单一成分 | memory_failures（+13pp） | memory_failures（**+27pp**） |
| Gene / Skill | 有效（+6-8pp） | **有害**（-7pp 到 -20pp） |
| 通用元基因 | 无效（0pp） | 有效（+13pp） |
| 橡皮鸭自我解释 | 极有效（+16pp） | 有害（-6pp） |
| 建议 | 记忆 > Gene > 无引导 | 记忆 > 通用元基因 > 无引导 >> Gene |

memory_failures 是唯一对两个模型都安全、都有正收益的组件。

### 8.4 总体结论

> **LLM 代码生成的最优引导策略是：用最小量的负面知识（~80 tokens），以 XML 结构化格式，在首轮注入。**
>
> "告诉模型前人如何失败"比"给模型完整的专家文档"高 20+ pp，比"让模型自己想"高 14pp，比"给正确策略"高 10pp。它通过双通道生效：真实失败内容提供信息（~+9pp），WARNING 信号激活谨慎模式（~+5pp）。
>
> **实用配方（任选其一）：**
> - 有 Skill 文档：提取 Common Pitfalls 前 2-3 条 → 包装为 `<memory-failures>` XML → **+9pp**
> - 有人工策划的失败案例：2 条 + warning 框架 + XML 标签 → **+14.6pp**
> - 什么都没有：一句 "This code will be deployed in production" → **+7pp**
>
> **最重要的禁忌：不要混合多个成分。**

---

## 附录：实验条件速查

### Gene 条件
| 条件 | 内容 | 建议 |
|------|------|------|
| G3 gene | 核心 strategy（~120 tok） | ✅ 标准配置 |
| G4 gene | G3 + AVOID + preconditions（~200 tok） | ⚠️ 对 Pro 可能有害 |
| L1 / SKILL.md 全文 | 完整文档（~600 tok） | ❌ 不如 G3 |
| 任何 LLM 生成的 Gene | 与人工编写等效 | ✅ 可自动化 |
| 跨域 Gene（Flash） | 其他领域的 Gene | ❌ 对 Flash 有害 |

### Memory 条件
| 条件 | 内容 | 建议 |
|------|------|------|
| 2 条真实失败 + XML | 领域专属 | ✅ 最优 |
| Pitfalls → XML 转换 | 从 SKILL.md 自动提取 | ✅ 接近最优（差 1.5pp） |
| warning 框架 | 步骤前加"不做这个会失败" | ✅ 有效（+10.5pp） |
| 通用编程警告 | 非领域特定 | ✅ 安全（+7.6pp） |
| 荒谬警告 | 纯 WARNING 信号 | ✅ 安全但弱（+5pp） |
| 编造的领域失败 | 看起来合理但虚假 | ❌ 危险，可能有毒 |
| 4+ 条失败案例 | 超过甜蜜点 | ⚠️ 无增益 |

### Skill 条件
| 条件 | 内容 | 建议 |
|------|------|------|
| examples.md | 代码示例（~200 tok） | ✅ 最有价值的 Skill 成分 |
| Pitfalls → XML | 格式转换后 | ✅ 强烈推荐 |
| Workflow 前 3 步 | 截断版（~80 tok） | ✅ 可用 |
| 完整 SKILL.md | ~600 tok | ⚠️ 不如 Gene，但安全 |
| api_notes.md | API 签名 | ❌ 几乎无效 |
| Pitfalls 原文（Markdown） | 未转换格式 | ❌ -1.3pp |
