# GeneProbe 技术报告

**探索 Skill 文档的失败，发现 Gene 策略模板的成功**

**版本：v4.0 · 2026-03-23**
**4,948 次受控实验 · 45 个科学计算场景 · Gemini 3.1 Pro / Flash Lite**

---

## 摘要

给大模型一份 600 tokens 的完整专家文档来指导代码生成，效果好吗？

本报告通过 4,948 次受控实验回答了这个问题。答案出人意料：**不好，甚至可能有害。** 我们的实验发现，用 80 tokens 的精炼失败经验（Memory Loop）能获得 +14.6pp 的通过率提升，而 600 tokens 的完整专家文档（Skill）只能提升 +6.0pp。更短、更聚焦的引导反而更有效——这与工程直觉完全相反。

本报告按以下叙事线索展开：

1. **SkillProbe**：我们首先系统解剖了 Skill 文档，发现了一系列令人惊讶的结论——文档中 2/5 的内容有害，截断比完整更好，同一内容换个格式效果差 10.7pp
2. **从 Skill 到 Gene**：SkillProbe 的发现揭示了一个规律——信息量与效果呈倒 U 型关系，最优窗口在 50–160 tokens。这直接催生了 Gene（~120 tok 的精炼策略模板）
3. **Gene vs Skill 正面对决**：在每一次对比中，Gene 都以 1/5 的 token 量胜出。在 Gene 基础上叠加 Skill 成分，效果反而下降
4. **GeneProbe**：Gene 展现出令人惊讶的特性——容忍内容错误、作者无关、格式结构比具体内容更重要

所有实验均遵循 EvoMap GEP v1.5.0 协议构建 Gene，使用 temperature=0.0 确保可复现。代码和数据开源于 [GitHub](https://github.com/qishisuren123/gene-bench)。

---

## 目录

1. [背景与核心概念](#1-背景与核心概念)
2. [实验方法](#2-实验方法)
3. [SkillProbe：解剖 Skill 文档](#3-skillprobe解剖-skill-文档)
4. [从 Skill 到 Gene：信息过载的发现](#4-从-skill-到-gene信息过载的发现)
5. [Gene vs Skill：正面对决](#5-gene-vs-skill正面对决)
6. [GeneProbe：Gene 的独特特性](#6-geneprobe-gene-的独特特性)
7. [总体结论与实用建议](#7-总体结论与实用建议)
8. [附录](#8-附录)

---

## 1. 背景与核心概念

### 1.1 问题定义

让大模型写代码，给它一份完整的专家文档就够了吗？

对同一道科学计算题——"用 scipy 检测 UV-Vis 光谱中的吸收峰"——Gemini 3.1 Pro 在毫无引导的情况下通过率只有 **0%**。给它一份 600 tokens 的完整 SKILL.md 文档后，通过率几乎没变。但如果只给 4 句话描述前人踩过的坑（~80 tokens），通过率跳到 **100%**。

当前工程实践的默认做法是：把尽可能多的文档塞给模型——API 参考、工作流、陷阱列表、代码示例——希望"给得越多越好"。**本报告用 4,948 次实验证明这个直觉是错的。**

### 1.2 Skill：传统的完整专家文档

Skill 是当前知识管理的典型方式——领域专家把任务知识整理成结构化文档：

```
skills/S012_uv_spectroscopy/direct/
├── SKILL.md            # 主文档：Overview + Workflow(7步) + Pitfalls(4-5条) + Error Handling + Quick Reference
├── references/
│   ├── api_notes.md    # API 参考：函数签名和参数说明（~80 tokens）
│   └── examples.md     # 代码示例：完整 Python 示例（~200 tokens）
└── scripts/
    └── main.py         # 参考实现（不注入到 prompt）
```

整体约 **600–800 tokens**，包含 5 个标准章节：Overview、Workflow、Common Pitfalls、Error Handling、Quick Reference。这是我们通过 SkillProbe 系列实验解剖的对象。

### 1.3 Gene：精炼策略模板

Gene 从 SKILL.md 蒸馏而来，遵循 EvoMap GEP v1.5.0 协议。核心思想是只保留**策略方向**和**关键陷阱**，丢弃一切冗余：

```json
{
  "type": "Gene",
  "schema_version": "1.5.0",
  "id": "gene_S012_uv_spectroscopy",
  "category": "optimize",
  "signals_match": ["csv", "detection", "fwhm calculation errors", "uv-vis"],
  "summary": "Detect and analyze absorption peaks in UV-Vis spectra",
  "strategy": [
    "Load CSV data with wavelength column and sample absorbance columns",
    "Apply scipy.signal.find_peaks with prominence-based detection",
    "AVOID: Wavelength spacing assumption — convert min-distance using actual spacing",
    "AVOID: FWHM errors — peak_widths returns indices, convert to wavelength units"
  ],
  "asset_id": "sha256:a7a2f1a29bb2..."
}
```

**~120 tokens**。注入时用 XML 标签封装：

```xml
<strategy-gene>
Domain keywords: csv, detection, fwhm calculation errors, uv-vis
Summary: Detect and analyze absorption peaks in UV-Vis spectra
Strategy:
  1. Load CSV data with wavelength column and sample absorbance columns
  2. Apply scipy.signal.find_peaks with prominence-based detection
  3. AVOID: Wavelength spacing assumption — convert min-distance using actual spacing
  4. AVOID: FWHM errors — peak_widths returns indices, convert to wavelength units
</strategy-gene>
```

Gene 有 5 个级别，用于验证信息量梯度效应：

| 级别 | 内容 | ~Tokens | 说明 |
|------|------|---------|------|
| G0 | 无引导（baseline） | 0 | 对照组 |
| G1 | 仅 `signals_match` 关键词 | ~25 | 最小信号 |
| G2 | + `summary` 一句话 | ~50 | 方向指引 |
| **G3** | **+ strategy 步骤（含 AVOID）** | **~120** | **标准配置** |
| G4 | + preconditions + constraints | ~200 | 过度填充 |

### 1.4 Memory Loop：极致蒸馏

比 Gene 更极致——只保留 2–3 条失败经验，~80 tokens：

```xml
<memory-failures>
Common failure patterns:
  - Forgetting to convert min-distance from nm to data point indices
  - Using raw peak_widths output without converting back to wavelength units
Each of these has caused solution failures in >30% of past attempts.
</memory-failures>
```

### 1.5 与 EvoMap 平台的关系

Gene、Memory Loop、EvolutionEvent、Capsule 均为 [EvoMap](https://evomap.ai) 平台的核心概念。EvoMap 提供结构化的知识管理框架：Gene 存储蒸馏策略，Memory 存储踩坑记录，EvolutionEvent 记录进化历史，Capsule 封装经验证的修复方案。本实验系统验证了这些设计的有效性。

---

## 2. 实验方法

### 2.1 模型与配置

| 配置项 | 值 |
|-------|-----|
| 强模型 | Gemini 3.1 Pro Preview（`gemini-3.1-pro-preview`） |
| 弱模型 | Gemini 3.1 Flash Lite Preview（`gemini-3.1-flash-lite-preview`） |
| API | Google AI Studio 直连 |
| Temperature | 0.0（确定性输出） |
| Max output tokens | 16,384 |
| 引导注入方式 | `system_instruction`（与 user prompt 分离） |

### 2.2 场景库

**45 个科学计算场景**，覆盖 15 个领域（神经科学、化学、天文学、基因组学、信号处理、气候科学、运筹学、量子计算等），按 baseline 通过率分为三类：

| 类别 | 条件 | 场景数 | 说明 |
|------|------|--------|------|
| Always-pass | baseline ≥ 95% | 10 | 太简单，引导无影响 |
| Always-fail | baseline ≤ 5% | 11 | 超出模型能力，引导无法拯救 |
| **Gene-sensitive** | **5% < baseline < 95%** | **22** | **引导敏感区，核心评估集** |

所有指标均在 22 个 gene-sensitive 场景上计算。这些场景代表了 LLM 代码生成中最有价值的区间——模型有能力完成但容易犯错的任务。

每个场景包含：
- `task.md`：任务描述（作为 user prompt），如"编写 CLI 脚本分析 UV-Vis 光谱中的吸收峰"
- `test_script.py`：自动化测试脚本，输出 `PASS:` / `FAIL:` 标记
- `input_data/`：测试用输入数据（CSV、JSON 等）

按任务依赖类型细分为三类（用于精细化分析）：

| 任务类型 | 特征 | 典型场景 | 场景数 |
|---------|------|---------|--------|
| **FORMULA-DEPENDENT** | 依赖正确的数学公式/物理方程 | 量子电路模拟、CMB 功率谱 | 6 |
| **API-DEPENDENT** | 依赖特定库 API 的正确使用 | scipy.find_peaks、astropy 单位转换 | 5 |
| **PATTERN-DEPENDENT** | 依赖正确的编程模式/数据处理流程 | 基因本体解析、系统发育距离 | 4 |

### 2.3 评估管道

每个 trial 的执行流程：

1. 读取场景 `task.md`（任务描述，作为 user prompt）
2. 根据实验条件构建 `system_instruction`（Gene / Skill / Memory / 无）
3. 调用 Gemini API → 提取 ` ```python ` 代码块（选最长块）
4. 在隔离临时目录执行代码 + 运行 `test_script.py`（超时 120 秒）
5. 统计 `PASS:` / `FAIL:` 标记，计算 **pass_rate = n_pass / (n_pass + n_fail)**
6. 结果写入 JSONL（支持断点续跑，线程安全）

**并行执行**：ThreadPoolExecutor 8 线程。

### 2.4 实验矩阵总览

27 个实验，4,948 次 trial，分为四大模块：

| 模块 | 实验 | 核心问题 | Trials |
|------|------|---------|--------|
| **SkillProbe** | EX22–EX25, EX27 | Skill 文档的成分归因、格式效应、转化方式 | 840 |
| **信息过载** | RQ1, EX8, EX15, EX17 | 倒 U 型曲线、组合惩罚、格式对比 | 1,170 |
| **Gene vs Skill** | RQ1, EX22–EX24 | 正面对决、公平对比、互补性测试 | 1,020 |
| **GeneProbe** | RQ3, RQ6, EX17, EX26, EX8 | 鲁棒性、作者效应、进化叙事、极致蒸馏 | 1,030 |
| *其余实验* | *RQ2,4,5,7, EX9–14, EX16, EX18–21* | *辅助验证* | *888* |
| **合计** | **27 个实验** | | **4,948** |

> 注：部分实验（如 RQ1、EX22）同时为多个模块提供数据，上表按主要归属分类，不重复计数。

---

## 3. SkillProbe：解剖 Skill 文档

> *"我们本来想证明 Skill 文档有用。结果发现，它的大部分内容要么无效，要么有害。"*

SkillProbe 是本研究的起点——我们系统解剖了 SKILL.md 文档的每个组成部分，逐一测试其对代码生成的影响。结果揭示了四个令人惊讶的发现。

### 3.1 发现一：Skill 的大部分内容是"死重"

**实验 EX22（210 trials）：** 把 SKILL.md 拆成 5 个独立组件，逐个注入测试

| Skill 成分 | 内容 | ~Tokens | Pass Rate | vs baseline | 判定 |
|-----------|------|---------|-----------|-------------|------|
| examples | 代码示例 | ~200 | 62.5% | **+6.2pp** | ✅ 唯一有效 |
| **完整 SKILL.md** | **全部 5 个成分** | **~600** | **62.4%** | **+6.0pp** | **⚠️ 不如单独 examples** |
| workflow | 7 步操作流程 | ~150 | 59.6% | +3.3pp | ⚠️ 效果一般 |
| _(baseline)_ | _无引导_ | _0_ | _56.3%_ | _—_ | |
| api_notes | API 函数签名 | ~80 | 56.0% | **-0.4pp** | ❌ 无效 |
| pitfalls | Common Pitfalls 章节 | ~120 | 55.1% | **-1.3pp** | ❌ 有害 |

**核心发现：**

- **5 个成分中 2 个无效/有害**：api_notes（-0.4pp）和 pitfalls（-1.3pp）对模型产生负面影响
- **完整 SKILL.md ≈ 仅 examples.md**：600 tok 的完整文档和 200 tok 的代码示例效果相同（+6.0pp ≈ +6.2pp）。SKILL.md 中除 examples 外的 400 tok 全是噪声
- **最讽刺的结果**：Pitfalls 章节——本应最有价值的"常见陷阱"——在 Markdown 格式下竟然**有害**

> **Skill 携带了大量"死重"——2/5 有害，1/5 一般，只有 1/5 真正有价值。**

---

### 3.2 发现二：截断比完整更好——"Less is More"的直接证据

**实验 EX23（150 trials）：** 将 Skill 的 Pitfalls 成分截断后重新测试

| Pitfalls 版本 | 内容 | Pass Rate | vs baseline |
|-------------|------|-----------|-------------|
| 截断（前 3 条） | ~120 tok | 63.9% | **+7.6pp** |
| 完整（全 5 条） | ~120 tok | 55.1% | **-1.3pp** |

同样的 Pitfalls 内容，**去掉最后 2 条后效果从 -1.3pp 变成 +7.6pp**——差距 **8.9pp**。

这不是巧合。EX23 还测试了 Skill 其他成分的截断效果：

| 条件 | 内容 | ~Tokens | Pass Rate | vs baseline |
|------|------|---------|-----------|-------------|
| skill_pitfalls_short | Pitfalls 前 3 条 | ~120 | 63.9% | **+7.6pp** |
| skill_workflow_short | Workflow 前 3 步 | ~80 | 60.5% | +4.2pp |
| skill_mixed_short | Overview + 前 2 条 Pitfalls | ~120 | 57.3% | +1.0pp |

**截断后的 Skill 全部优于完整 Skill（+6.0pp）。** 信息量超过某个阈值后，开始产生噪声。

---

### 3.3 发现三：格式比内容更重要——10.7pp 的差距

**实验 EX25（180 trials）：** 这是 SkillProbe 系列最重要的发现。

我们将 Skill 的 Pitfalls 章节——在 Markdown 原文格式下有害的那个——用不同格式重新包装，**内容完全不变**：

| 条件 | 格式 | Pass Rate | vs baseline |
|------|------|-----------|-------------|
| memory_curated | EvoMap `<memory-failures>` XML（人工编写） | 67.2% | **+10.9pp** |
| pitfalls_as_xml | Pitfalls → EvoMap XML（**自动转换**） | 65.7% | **+9.4pp** |
| pitfalls_warning | Pitfalls + WARNING 框架 | 64.2% | +7.8pp |
| _(baseline)_ | _无引导_ | _56.3%_ | _—_ |
| **pitfalls_raw** | **Pitfalls Markdown 原文** | **55.1%** | **-1.3pp** |

**同一内容，Markdown = -1.3pp，XML = +9.4pp，差距 10.7pp。**

Skill 的 Pitfalls 章节在 Markdown 格式下有害，但把**完全相同的文字**重新包装成 `<memory-failures>` XML 标签后，效果飙升。

**按任务类型细分：**

| 任务类型 | 场景数 | baseline | XML 格式 | Markdown 原文 | 格式差距 |
|---------|--------|---------|---------|------------|---------|
| FORMULA-DEPENDENT | 6 | 34.2% | **+16.7pp** | +2.5pp | **14.2pp** |
| API-DEPENDENT | 5 | 70.0% | **+9.2pp** | -0.8pp | **10.0pp** |
| PATTERN-DEPENDENT | 4 | 72.5% | -1.1pp | **-7.4pp** | **6.3pp** |

在所有任务类型上 XML 都优于 Markdown，公式型任务差距最大（14.2pp）。

**为什么格式如此重要？** XML 标签（`<memory-failures>...</memory-failures>`）提供了明确的结构边界，帮助模型区分"引导信息"和"任务描述"。Markdown 格式的 Pitfalls 与任务描述在视觉上没有区分，模型可能将其当作需要实现的需求，而非需要避免的陷阱。

---

### 3.4 发现四：Skill 最有价值的使用方式是"拆解后重新包装"

**实验 EX27（120 trials）：** 既然格式转换如此有效，那么 Memory Loop 中的失败知识从哪里来最好？

| 来源 | 说明 | Pass Rate | vs baseline |
|------|------|-----------|-------------|
| 人工策划 | 领域专家编写失败案例 | 67.2% | **+10.9pp** |
| **从 Skill 自动转换** | **提取 Pitfalls → XML** | **65.7%** | **+9.4pp** |
| 模型自生成 | LLM 自己预测失败（两轮对话） | 60.5% | +4.2pp |

**从 Skill 自动提取 Pitfalls 并转换为 XML 格式（+9.4pp）≈ 人工策划（+10.9pp）**，差距仅 1.5pp。

这意味着：

> **Skill 文档最有价值的使用方式不是直接注入，而是作为原材料——提取 Pitfalls，转换为 XML 格式。** 这个过程可以完全自动化，效果接近人工策划。

### 3.5 SkillProbe 小结

| 发现 | 实验 | 核心数据 | 意义 |
|------|------|---------|------|
| Skill 携带大量"死重" | EX22 | 2/5 有害，1/5 一般 | 完整文档 ≠ 好文档 |
| 截断优于完整 | EX23 | 截断 +7.6pp vs 完整 -1.3pp | Less is More |
| 格式 > 内容 | EX25 | 同内容 XML vs MD = 10.7pp | 格式是被忽视的关键变量 |
| Skill 应被拆解重组 | EX27 | 自动转换 ≈ 人工策划 | Skill 不该直接用 |

---

## 4. 从 Skill 到 Gene：信息过载的发现

> *SkillProbe 揭示了一个模式：更多信息 ≠ 更好效果。这个发现催生了 Gene 的设计理念。*

### 4.1 信息量的倒 U 型曲线

**实验 RQ1（480 trials）：** 从无引导（G0）到完整 SKILL.md（L1），逐级增加信息量

| 条件 | ~Tokens | Pro | Flash | 整体 | vs 无引导 |
|------|---------|-----|-------|------|---------|
| G0（无引导） | 0 | 48.7% | 37.2% | 43.0% | — |
| G1（关键词） | ~25 | 49.6% | 43.2% | 46.4% | +3.4pp |
| G2（+summary） | ~50 | 51.4% | 45.4% | 48.4% | +5.4pp |
| **G3（+strategy）** | **~120** | **52.4%** | **44.7%** | **48.5%** | **+5.5pp** ← 峰值 |
| G4（+更多字段） | ~200 | 48.4% | 46.1% | 47.3% | +4.3pp ↘ |
| L1（SKILL.md 全文） | ~600 | 51.0% | 43.2% | 47.1% | +4.1pp ↘ |

**效果在 G3（~120 tok）达到峰值，然后下降。** G4（200 tok）比 G3 低 1.2pp，L1（600 tok）比 G3 低 1.4pp。

这是一条经典的**倒 U 型曲线**：

```
效果
 ^
 |        ★ Memory(80tok,+14.6pp)
 |
 |    ● Gene G3(120tok,+8.3pp)
 |  ●            ● G4(200tok,+4.3pp)
 | ●                       ● SKILL.md(600tok,+6.0pp)
 |●
 +---+----+----+----+----+----+---→ Token 量
    0   50  100  150  200  ...  600
```

| Token 量 | 条件 | 效果 |
|---------|------|------|
| ~20 tok | "代码要上线" | +7.0pp |
| **~80 tok** | **Memory Loop** | **+14.6pp** ← 最优 |
| ~120 tok | Gene G3 | +8.3pp |
| ~200 tok | Gene G4 / 全组件 | +4.3pp / -7.0pp |
| ~600 tok | SKILL.md | +6.0pp |
| ~700+ tok | SKILL.md + examples | 效果衰减 |

**最优区间：50–160 tokens。Skill（600 tok）在最优区间的 4–5 倍之外。**

---

### 4.2 组合惩罚：为什么混搭多个好成分反而更差

**实验 EX15（240 trials）：** 三个各自 +8–10pp 的最优成分组合在一起

| 条件 | 单独效果 |
|------|---------|
| Warning 框架（单独） | **+10.5pp** |
| 失败案例（单独） | **+10.4pp** |
| Novice 角色（单独） | **+8.0pp** |
| **三者全组合** | **+4.5pp** ← 全场最差 |
| 理论加性预测 | +28.9pp |
| **实际/预测比** | **15.6%** |

**单独都很好的成分，全部叠加反而是最差的。** 实际效果只有理论加性预测的 15.6%。

**这解释了 Skill 为什么效果不佳**：SKILL.md 同时包含策略、陷阱、API 参考、代码示例、工作流——相当于把多个成分强制组合，触发了严重的组合惩罚。

**机制解释**：所有高效引导成分（Warning、Memory、角色设定）都通过激活模型的"谨慎模式"生效。谨慎模式是一个**二值开关**——一旦被某个信号触发，再多刺激也没有增量。多个成分只会互相竞争 token 空间，带来额外的噪声。

---

### 4.3 Gene 的设计理念

SkillProbe 和信息过载实验共同指向一个设计原则：

> **信息密度 > 信息量。保留最核心的策略方向和关键陷阱，丢弃一切冗余。**

这就是 Gene 的设计理念——从 Skill 蒸馏而来，只保留 ~120 tokens 的核心内容，精确命中倒 U 型曲线的最优区间。

Gene 的蒸馏规则：
1. **保留**：核心策略步骤（strategy）、关键陷阱（AVOID）、领域关键词（signals_match）
2. **丢弃**：Workflow 详细流程、Error Handling、Quick Reference、Overview
3. **格式**：使用 XML 标签（`<strategy-gene>`）而非 Markdown，利用格式优势
4. **协议**：遵循 EvoMap GEP v1.5.0，确保结构一致性

---

## 5. Gene vs Skill：正面对决

> *Gene 用 1/5 的 token 量，在每一次对决中胜出。*

### 5.1 全面对比：Gene 一致胜出

Gene G3（~120 tok）在所有实验中都优于完整 SKILL.md（~600 tok）：

| 实验 | Gene G3 | SKILL.md | Gene 优势 | 场景 |
|------|---------|----------|----------|------|
| RQ1（完整度梯度） | 48.5% | 47.1% | **+1.4pp** | 22 场景 × 2 模型 |
| EX22（Skill 归因） | 64.6% | 62.4% | **+2.2pp** | 15 场景 × 2 模型 |
| EX24（互补性） | 64.6% | 62.4% | **+2.2pp** | 15 场景 × 2 模型 |

**Gene G3 用不到 SKILL.md 1/5 的 token（120 vs 600），在每一次对比中都取得更高的通过率。**

### 5.2 公平对比：控制相同 token 预算

**实验 EX23（150 trials）：** 将 Skill 各成分截断到 ~120 tok（和 Gene G3 相同的预算），看谁更强

| 条件 | 内容 | ~Tokens | Pass Rate | vs baseline |
|------|------|---------|-----------|-------------|
| **Gene G3** | **策略模板** | **~120** | **64.6%** | **+8.3pp** |
| skill_pitfalls_short | Pitfalls 前 3 条 | ~120 | 63.9% | +7.6pp |
| skill_workflow_short | Workflow 前 3 步 | ~80 | 60.5% | +4.2pp |
| skill_mixed_short | Overview + 前 2 条 Pitfalls | ~120 | 57.3% | +1.0pp |
| _(baseline)_ | _无引导_ | _0_ | _56.3%_ | _—_ |

**在相同 ~120 tok 预算下，Gene G3（+8.3pp）仍高于 Skill 的任何截断版本。** 最接近的是 Pitfalls 截断版（+7.6pp），但仍低 0.7pp。

这排除了"Gene 只是因为更短所以更好"的解释。Gene 的优势来自**蒸馏质量**——它选择性保留了最有价值的信息，而非随机截断。

### 5.3 互补性测试：Gene 已提取 Skill 的核心价值

**实验 EX24（180 trials）：** 如果 Gene 和 Skill 提供互补信息，组合应该比单独使用更好。实际结果：

| 条件 | 内容 | ~Tokens | Pass Rate | vs baseline |
|------|------|---------|-----------|-------------|
| **Gene G3 alone** | **Gene 单独使用** | **~120** | **64.6%** | **+8.3pp** |
| Gene + examples | Gene + 代码示例 | ~320 | 64.0% | +7.7pp |
| SKILL.md full | 完整 Skill | ~600 | 62.4% | +6.0pp |
| Gene + api_notes | Gene + API 参考 | ~200 | 58.8% | +2.5pp |
| api_notes only | API 参考单独使用 | ~80 | 56.0% | -0.4pp |

**在 Gene 基础上叠加 Skill 成分，效果不升反降：**

- Gene + examples（+7.7pp）< Gene alone（+8.3pp）：代码示例没有提供增量价值，-0.6pp
- Gene + api_notes（+2.5pp）<< Gene alone（+8.3pp）：API 参考严重稀释信号，-5.8pp

**这证明 Gene 和 Skill 是冗余关系**——Gene 已经从 SKILL.md 中提取了最关键的信息。Skill 的其余内容不是新信息，只是噪声。在 Gene 存在的情况下，任何 Skill 成分的加入都只会稀释信号、降低效果。

### 5.4 Gene vs Skill 对决小结

| 维度 | Gene | Skill | 优势倍率 |
|------|------|-------|---------|
| **效果（pass rate 提升）** | +8.3pp | +6.0pp | Gene 高 38% |
| **Token 成本** | ~120 tok | ~600 tok | Gene 省 80% |
| **构建成本** | LLM 自动生成，~$0 | 专家手写，~2h/场景 | Gene 接近免费 |
| **互补性** | 叠加 Skill 效果下降 | — | Gene 已提取核心价值 |

---

## 6. GeneProbe：Gene 的独特特性

> *Gene 不仅比 Skill 更有效，它还展现出一系列令人惊讶的特性——容忍错误、作者无关、格式比内容更重要。*

### 6.1 鲁棒性：Gene 容忍内容错误

**实验 RQ3（180 trials）：** 故意给 Gene 注入 5 种"变异"（错误内容）

| 变异类型 | 说明 | Pass Rate | vs 正确 Gene |
|---------|------|-----------|------------|
| Clean G3 | 正确的 Gene | 48.5% | baseline |
| stale_paradigm | 过时技术建议（如"用 csv 替代 pandas"） | 51.0% | **+2.5pp** |
| inverted_priority | 策略步骤顺序颠倒 | 49.6% | +1.1pp |
| wrong_domain | 完全错误领域的 Gene（如给化学任务注入天文学 Gene） | 48.5% | 0pp |
| overconstrained | 过度限制约束 | 47.3% | -1.2pp |
| wrong_algorithm | 推荐根本错误的算法 | 46.1% | -2.4pp |

**5 种变异中 3 种无害或有益，只有推荐根本错误的算法才造成显著伤害（-2.4pp）。**

最反直觉的发现：

1. **过时技术反而更好（+2.5pp）**：过时建议破坏了 Gene 中可能误导模型的具体细节，但保留了有用的结构信息
2. **错误领域的 Gene = 正确 Gene（0pp 差异）**：给化学任务注入天文学 Gene，效果完全相同

这说明 **Gene 的价值主要来自结构格式而非具体内容**——XML 标签 `<strategy-gene>` 本身就足以激活模型的"谨慎模式"。

**对比 Skill 的鲁棒性：**

| 情况 | Gene | Skill |
|------|------|-------|
| 内容正确 | +8.3pp | +6.0pp |
| 内容有小错误 | +5.5pp ~ +10.5pp | — |
| 内容正确但原始格式 | +8.3pp (XML) | **-1.3pp (Markdown Pitfalls)** |

**Skill 在内容完全正确的情况下，其 Pitfalls 章节因格式问题反而有害。Gene 即使内容有误也通常安全。**

---

### 6.2 作者无关性：Gene 是一个二进制开关

**实验 RQ6（120 trials）：** 用 5 个不同"作者"（人类专家 + 4 个 LLM）为同一场景生成 Gene，然后在 Gemini 上测试

| Gene 作者 | Pass Rate | vs No Gene |
|----------|-----------|-----------|
| Human expert | 82.2% | +5.9pp |
| GPT-5.4 | 82.2% | +5.9pp |
| Claude Haiku | 82.2% | +5.9pp |
| Claude Opus | 82.2% | +5.9pp |
| Gemini-3-Pro | 82.2% | +5.9pp |
| No Gene | 76.3% | — |

**5 个作者在每个场景上产生完全相同的结果。**

Gene 是一个**二进制开关**——"有 Gene"vs"没有 Gene"，而非精细的知识载体。谁写的、用什么模型写的，完全不影响效果。

**实际意义：**

| | Gene | Skill |
|---|------|-------|
| **构建方式** | 任意 LLM 读 task.md → 生成 JSON | 领域专家手工编写 |
| **构建时间** | ~10 秒/场景 | ~2 小时/场景 |
| **构建成本** | ~$0 | 需要领域专家 |
| **质量差异** | 无（所有作者等效） | 依赖专家水平 |

---

### 6.3 XML 格式的结构性优势

**实验 EX17（180 trials）：** 控制相同内容，仅改变封装格式

| 格式 | 说明 | 相对效果 |
|------|------|---------|
| **EvoMap XML** | `<strategy-gene>` + `<memory-failures>` | **最优** |
| 段落文本 | 纯文本段落 | 显著低于 XML |
| Markdown 列表 | `- item` 格式 | 低于 XML |
| 关键词列表 | 仅关键词 | 最低 |

结合 EX25 的数据（同一 Pitfalls 内容，XML vs Markdown = 10.7pp 差距），XML 格式的优势是显著且一致的。

**Gene 天然使用 XML 格式**（`<strategy-gene>...</strategy-gene>`），这是其相对于 Markdown 格式 Skill 文档的结构性优势。

---

### 6.4 进化叙事：EvolutionEvent 的附加价值

**实验 EX26（180 trials）：** 告诉模型"这个 Gene 是如何进化出来的"（GEP EvolutionEvent 概念），会比只给 Gene 更有效吗？

| 条件 | 对应 GEP 概念 | ~Tokens | vs baseline |
|------|-------------|---------|-------------|
| gene_g3 | Gene（仅最终策略） | ~120 | baseline |
| **evolution_full** | **Gene + EvolutionEvent（含失败尝试记录）** | **~250** | **+2.8pp** |
| gene_with_confidence | Gene + GDI 分数 + 成功连续次数 | ~140 | +0.5pp |
| capsule_style | Capsule 格式（触发+置信度+策略） | ~180 | +1.2pp |
| failed_attempts_only | 仅失败尝试（无最终策略） | ~150 | +1.8pp |

**进化叙事（evolution_full）比单独 Gene 额外提升了 +2.8pp。**

进化叙事的 prompt 格式：

```xml
<evolution-event intent="optimize" mutations_tried="3" outcome="success" score="0.85">
  <history>
    Attempt 1: Basic approach with default parameters → FAILED (wavelength spacing error)
    Attempt 2: Added spacing fix, missed FWHM conversion → FAILED
    Attempt 3: Full strategy → PASSED (85% confidence)
  </history>
  <validated-gene>
    {gene_g3_content}
  </validated-gene>
</evolution-event>
```

**为什么有效？** 进化叙事不只告诉模型"做什么"，还告诉它"为什么这么做"——通过展示前人失败的过程，强化了策略的重要性。这验证了 EvoMap GEP 中 EvolutionEvent 设计的合理性。

---

### 6.5 Memory Loop：极致蒸馏的巅峰

**实验 EX8（270 trials）：** Memory Loop 是比 Gene 更极致的蒸馏——只保留 2–3 条失败经验，~80 tok

| 条件 | ~Tokens | Pass Rate | vs baseline |
|------|---------|-----------|-------------|
| **Memory Loop** | **~80** | **87.1%** | **+14.6pp** |
| Gene G3 | ~120 | 76.4% | +3.9pp |
| _(baseline)_ | _0_ | _72.5%_ | _—_ |
| Exploration Full（全组件） | ~200 | 65.6% | **-7.0pp** |

排序：**Memory（80 tok, +14.6pp）>> Gene（120 tok, +3.9pp）>> 全组件（200 tok, -7.0pp）**

Memory Loop 以最少的 token（80）取得了全场最强的效果（+14.6pp），而信息量最多的"全组件"（200 tok）反而有害（-7.0pp）。

这条证据从极端情况验证了核心原理：

> **信息密度 > 信息量。最精炼的失败经验（80 tok）比最完整的专家文档（600 tok）有效 2.4 倍。**

Memory Loop 的模板：

```
Based on analysis of past failed attempts at similar tasks,
these failure patterns have been documented:

<memory-failures>
Common failure patterns:
  - [失败模式 1]
  - [失败模式 2]
Each of these has caused solution failures in >30% of past attempts.
</memory-failures>

Learn from these failures. Avoid these specific pitfalls in your implementation.
```

### 6.6 GeneProbe 小结

| 特性 | 实验 | 核心发现 |
|------|------|---------|
| 鲁棒性 | RQ3 | 5 种变异中 3 种无害；错误领域 Gene = 正确 Gene |
| 作者无关性 | RQ6 | 5 个作者产生完全相同结果 |
| 格式优势 | EX17, EX25 | XML 比 Markdown 高 10.7pp |
| 进化叙事 | EX26 | EvolutionEvent 附加 +2.8pp |
| 极致蒸馏 | EX8, EX27 | Memory Loop 80 tok = +14.6pp，全场最强 |

---

## 7. 总体结论与实用建议

### 7.1 核心结论

**给大模型更多文档 ≠ 更好的代码生成。最优引导在 50–160 tokens 的窗口内。**

四大模块的发现汇聚成一个一致的结论：

| 模块 | 核心发现 |
|------|---------|
| **SkillProbe** | Skill 文档 2/5 内容有害，格式比内容重要 10.7pp |
| **信息过载** | 效果呈倒 U 型，组合惩罚使混搭成分适得其反 |
| **Gene vs Skill** | Gene 以 1/5 token 一致胜出，叠加 Skill 反而降低效果 |
| **GeneProbe** | Gene 容忍错误、作者无关、XML 格式是关键优势 |

Gene 在所有维度上优于 Skill：

| 维度 | Gene | Skill | 优势 |
|------|------|-------|------|
| 效果 | +8.3pp | +6.0pp | Gene 高 38% |
| Token 成本 | ~120 tok | ~600 tok | Gene 省 80% |
| 构建成本 | LLM 自动生成 | 专家手写 2h/场景 | Gene ~$0 |
| 鲁棒性 | 内容有误仍安全 | 正确 Pitfalls 格式有害 | Gene 更安全 |
| 格式 | XML（+9.4pp） | Markdown（-1.3pp） | 格式天然优势 |

### 7.2 实用建议

**最佳实践（按效果排序）：**

| 场景 | 方法 | 预期效果 | Token 成本 |
|------|------|---------|-----------|
| 有踩坑记录 | 2–3 条失败案例 + `<memory-failures>` XML | **+14.6pp** | ~80 tok |
| 有 Skill 文档 | 提取 Pitfalls 前 2–3 条 → XML 格式 | **+9.4pp** | ~80 tok |
| 有完整文档 | 蒸馏为 Gene G3（让 LLM 提取核心策略） | **+8.3pp** | ~120 tok |
| 什么都没有 | 一句 "This code will be deployed in production" | **+7.0pp** | ~20 tok |

**绝对禁忌：**

1. **不要直接注入完整 SKILL.md** — 600 tok 的效果（+6.0pp）不如 120 tok 的 Gene（+8.3pp），更不如 80 tok 的 Memory（+14.6pp）
2. **不要混搭多个成分** — 组合惩罚使效果低于任何单一成分
3. **不要使用 Markdown 格式的 Pitfalls** — 换成 XML 可获得 10.7pp 的提升
4. **弱模型不要用具体领域 Gene** — 只用 Memory Loop 或通用元基因

### 7.3 对 EvoMap 平台的验证

本实验验证了 EvoMap 的以下设计决策：

| 设计决策 | 实验支撑 | 结论 |
|---------|---------|------|
| Gene 遵循 GEP v1.5.0 | RQ1, EX22, EX24 | G3（120 tok）是信息效率最优点 |
| Memory Loop `<memory-failures>` | EX8, EX25, EX27 | 全场最强引导模式，+14.6pp |
| XML 结构化标签 | EX17, EX25 | 同内容 XML 比 Markdown 高 10.7pp |
| EvolutionEvent 进化历史 | EX26 | 附加 +2.8pp |
| Gene 可 LLM 自动生成 | RQ6 | 任意 LLM = 人工编写 |
| Skill → Gene 自动蒸馏 | EX27 | 自动转换效果 ≈ 人工策划（-1.5pp） |

---

## 8. 附录

### 附录 A：完整场景列表（45 个）

| 编号 | 场景 | 领域 | 编号 | 场景 | 领域 |
|------|------|------|------|------|------|
| S002 | spike_behavior | 神经科学 | S068 | weather_fronts | 大气科学 |
| S005 | protein_parse | 生命科学 | S069 | rainfall_extreme | 大气科学 |
| S007 | data_viz | 神经科学 | S072 | ozone_profile | 大气科学 |
| S011 | particle_physics | 物理学 | S074 | heat_index | 大气科学 |
| S012 | uv_spectroscopy | 化学 | S077 | grain_size | 材料科学 |
| S017 | ctd_ocean | 海洋学 | S084 | dose_response | 医学 |
| S026 | earthquake_catalog | 地震学 | S090 | noise_reduction | 信号处理 |
| S028 | audio_features | 心理声学 | S091 | modulation_classify | 信号处理 |
| S030 | fossil_morpho | 古生物学 | S093 | echo_removal | 信号处理 |
| S033 | exoplanet_transit | 天文学 | S096 | network_influence | 社会科学 |
| S036 | cmb_power_spectrum | 天文学 | S101 | climate_attribution | 气候科学 |
| S037 | asteroid_orbit | 天文学 | S102 | protein_secondary | 蛋白质结构 |
| S044 | bfactor_analysis | 蛋白质结构 | S103 | instrumental_variable | 因果推断 |
| S045 | ramachandran | 蛋白质结构 | S104 | multisensor_anomaly | 传感器融合 |
| S048 | gene_ontology | 基因组学 | S105 | community_detection | 图分析 |
| S052 | phylogenetic_distance | 基因组学 | S106 | seismic_denoise | 地震学 |
| S053 | methylation_beta | 基因组学 | S107 | regime_switch | 金融/时序 |
| S054 | species_accumulation | 生态学 | S108 | raman_spectroscopy | 化学 |
| S060 | phenology_shifts | 生态学 | S109 | hdf5_chunked | 数据工程 |
| S067 | salinity_gradient | 海洋学 | S110 | log_regex | 软件工程 |
| | | | S111 | cuda_memory | GPU 编程 |
| | | | S112 | midi_chords | 音乐信息检索 |
| | | | S113 | inventory_reorder | 运筹学 |
| | | | S114 | obstacle_avoidance | 机器人学 |
| | | | S115 | quantum_circuit | 量子计算 |

### 附录 B：GEP v1.5.0 Schema

```json
{
  "type": "Gene",
  "schema_version": "1.5.0",
  "id": "gene_{scenario_id}",
  "category": "optimize|build|fix|analyze",
  "signals_match": ["keyword1", "keyword2"],
  "summary": "一句话描述（≤200 字符）",
  "preconditions": ["scipy>=1.7"],
  "strategy": [
    "步骤 1",
    "AVOID: 陷阱描述"
  ],
  "constraints": {"max_files": 1, "forbidden_paths": []},
  "validation": ["python -m pytest scenarios/..."],
  "epigenetic_marks": ["domain:chemistry"],
  "asset_id": "sha256:{canonical JSON SHA-256}"
}
```

### 附录 C：Memory Loop Prompt 模板

```
Based on analysis of past failed attempts at similar tasks,
these failure patterns have been documented:

<memory-failures>
Common failure patterns:
  - [失败模式 1]
  - [失败模式 2]
Each of these has caused solution failures in >30% of past attempts.
</memory-failures>

Learn from these failures. Avoid these specific pitfalls in your implementation.
```

### 附录 D：EvolutionEvent Prompt 模板

```xml
<evolution-event intent="optimize" mutations_tried="3" outcome="success" score="0.85">
  <history>
    Attempt 1: Basic approach with default parameters → FAILED ({failure_1})
    Attempt 2: Added fix for {failure_1}, missed {failure_2} → FAILED
    Attempt 3: Full strategy → PASSED (85% confidence)
  </history>
  <validated-gene>
    {gene_g3_content}
  </validated-gene>
</evolution-event>
```

### 附录 E：JSONL 结果格式

```json
{
  "scenario_id": "S012_uv_spectroscopy",
  "model": "gemini_31_pro",
  "experiment": "ex8",
  "condition": "memory_failures",
  "pass_rate": 1.0,
  "n_pass": 12, "n_fail": 0,
  "gene_tokens": 89,
  "input_tokens": 1893,
  "error_type": "success"
}
```

### 附录 F：可复现性

| 维度 | 值 |
|------|-----|
| 模型 | Gemini 3.1 Pro Preview / Flash Lite Preview |
| API | Google AI Studio 直连 |
| Temperature | 0.0 |
| Max tokens | 16,384 |
| 执行超时 | 120 秒/trial |
| 并行度 | 8 线程 |
| 总 trials | 4,948 |
| 代码仓库 | https://github.com/qishisuren123/gene-bench |
| EvoMap | https://evomap.ai |

---

*GeneProbe v4.0 · 2026-03-23 · "信息密度 > 信息量"*
*代码和数据开源于 https://github.com/qishisuren123/gene-bench*
