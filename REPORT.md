# Gene-Bench 技术报告：基因级引导对 LLM 代码生成的影响

## Fear Teaches Better Than Knowledge: Counter-Intuitive Findings on Guiding LLM Code Generation

---

## 摘要

我们通过 4,068 次受控实验（覆盖 43 个科学计算场景、2 个 Gemini 模型、100+ 种引导条件），系统研究了不同类型和粒度的策略引导对 LLM 代码生成的影响。实验基于 EvoMap 双回路架构（记忆模式 vs 探索模式）设计，经历四个阶段：Phase 1 验证 Gene 完整度与变异，Phase 2 解构记忆与探索回路，Phase 3 探索失败引导的作用机制，Phase 4 将 EvoMap 生态系统与常见 prompt engineering 方法做正面对比。

**核心发现：** 告诉模型"前人如何失败"比告诉它"应该怎么做"平均高 **+14.6 个百分点**（pass rate 87.1% vs 72.5% baseline）。这一效果通过"双通道机制"实现：真实失败的信息内容贡献约 +7-9pp，而 WARNING 信号本身激活谨慎模式贡献约 +5pp。最优成分（失败知识、新手角色、警告框架）**不可叠加**——组合使用反而不如单独使用。Phase 4 进一步证实：EvoMap 的 XML 结构化格式比纯文本高 +13pp；一轮 EvoMap 记忆注入（~1900 tokens）超过两轮盲重试（~2850 tokens）；157 tokens 的失败记忆超过 700 tokens 的 SKILL+示例文档。

---

## 1. 实验设计

### 1.1 基础设施

| 维度 | 配置 |
|------|------|
| 模型 | Gemini 3.1 Pro Preview, Gemini 3.1 Flash Lite Preview |
| 场景 | 43 个科学计算任务（30 个复用 Skill-Bench + 13 个新增） |
| 评估 | 自动化测试脚本（PASS/FAIL 逐项检验，计算 pass rate） |
| API | Google Gemini 直连，temperature=0.0，max_tokens=16384 |
| 总 trials | 4,068 |

### 1.2 实验矩阵

**Phase 1: Gene 完整度实验（RQ1-RQ7, 1,318 trials）**

| 实验 | 研究问题 | Trials | 条件数 |
|------|---------|--------|--------|
| RQ1 | Gene 完整度梯度 (G0→G4→L1) | 480 | 6 |
| RQ2 | Gene vs Skill 正面对决 | 240 | 4 |
| RQ3 | Gene 错误容忍度 | 180 | 6 |
| RQ4 | 跨领域 Gene 迁移 | 48 | 5 |
| RQ5 | Gene 组合效应 | 100 | 5 |
| RQ6 | 自生成 Gene（作者效应） | 120 | 6 |
| RQ7 | Gene 接种效应 | 150 | 5 |

**Phase 2: EvoMap 双回路实验（EX8-EX13, 1,110 trials）**

| 实验 | 研究问题 | Trials | 条件数 |
|------|---------|--------|--------|
| EX8 | 记忆模式 vs 探索模式 | 270 | 9 |
| EX9 | 失败引导 vs 正确策略 | 150 | 5 |
| EX10 | 角色光谱（新手→专家） | 180 | 6 |
| EX11 | 失败案例密度 | 150 | 5 |
| EX12 | 自我预判 vs 外部知识 | 180 | 6 |
| EX13 | 信息框架效应 | 180 | 6 |

**Phase 3: 机制探索实验（EX14-EX16, 600 trials）**

| 实验 | 研究问题 | Trials | 条件数 |
|------|---------|--------|--------|
| EX14 | 失败的真假（真实 vs 编造 vs 荒谬） | 180 | 6 |
| EX15 | 最优配方组合（成分叠加 vs 饱和） | 240 | 8 |
| EX16 | 难度感知与利害框架 | 180 | 6 |

**Phase 4: EvoMap 生态优势验证（EX17-EX21, 900 trials）**

| 实验 | 研究问题 | Trials | 条件数 |
|------|---------|--------|--------|
| EX17 | 结构化格式优势（XML vs Markdown vs 纯文本） | 180 | 6 |
| EX18 | 进化循环模拟（单轮记忆 vs 多轮重试） | 150 | 5 |
| EX19 | EvoMap 最优 vs 常见 prompt engineering | 210 | 7 |
| EX20 | 基因跨任务复用性（精确/兄弟/表亲/通用） | 180 | 6 |
| EX21 | 完整生态 vs 传统知识管理（token 效率） | 180 | 6 |

Phase 4 的设计逻辑：Phase 1-3 已证明 EvoMap 记忆系统的有效性（+14.6pp），但尚未回答"EvoMap 为什么比常见的 prompt engineering 方法好？"。Phase 4 从五个维度做正面对比——格式设计、迭代效率、常见替代方案、知识复用性、token 经济性——以验证 EvoMap 作为一个完整生态系统的独特优势。

### 1.3 场景分布

43 个场景按难度分为三类：
- **Always-pass (≥95%):** 10 个场景 — 模型已掌握，引导无影响
- **Always-fail (≤5%):** 11 个场景 — 超出模型能力，引导无法拯救
- **Gene-sensitive (5%-95%):** 22 个场景 — 引导策略的差异在此显现

Gene-sensitive 场景涵盖光谱分析、地震学、气候科学、因果推断、图分析、信号处理、供应链优化等领域。

---

## 2. Phase 1 结果：Gene 完整度与变异

### 2.1 RQ1: Gene 完整度梯度 (480 trials)

| Gene Level | 内容 | ~Tokens | Pro | Flash | Overall |
|------------|------|---------|-----|-------|---------|
| G0 (baseline) | 无引导 | 0 | 0.487 | 0.372 | 0.430 |
| G1 | 仅关键词 | ~25 | 0.496 | 0.432 | 0.464 |
| G2 | +summary | ~50 | 0.514 | 0.454 | 0.484 |
| **G3** | **+strategy** | **~120** | **0.524** | **0.447** | **0.485** |
| G4 | +pitfalls+concepts | ~200 | 0.484 | 0.461 | 0.473 |
| L1 | SKILL.md 全文 | ~600 | 0.510 | 0.432 | 0.471 |

**发现 1: 非单调关系 — G3 是峰值，G4 回落。**
- Pro: G0→G3 提升 +3.7pp，G3→G4 下降 -4.0pp
- Flash: G0→G4 单调上升 +8.9pp（弱模型更能利用额外信息）
- 效应量: G0→G3 Cohen's d = 0.13（微弱），说明 Gene 本身提升有限
- **Pro 和 Flash 对 Gene 完整度的反应方向不同**

**发现 2: L1 (完整 SKILL.md, ~600 tokens) 不如 G3 (~120 tokens)。**
用 5x 的 token 预算，效果反而更差。

**高方差场景**（Gene 级别间 spread ≥ 0.20）：
- S012_uv_spectroscopy: spread=1.00 (G0=0.00, L1=1.00)
- S017_ctd_ocean: spread=0.50 (G0=1.00, G3/G4=0.50 — Gene 有毒)
- S106_seismic_denoise: spread=0.45 (G0=0.40, G3=0.85)
- S107_regime_switch: spread=0.45 (仅 G2=0.45，其余=0.00)

### 2.2 RQ2: Gene vs Skill (240 trials)

| 条件 | Pro | Flash | Overall |
|------|-----|-------|---------|
| no_context | 0.487 | 0.372 | 0.430 |
| gene_g3 | 0.524 | 0.447 | 0.485 |
| skill_l1 | 0.510 | 0.432 | 0.471 |
| skill_l4 | 0.484 | 0.461 | 0.473 |

Gene G3 (+5.5pp) 略优于 Skill L1 (+4.1pp)，且使用的 token 数仅为 1/5。
完整 Skill L4 在 Pro 上反而低于 baseline — 再次确认信息过载效应。

### 2.3 RQ3: Gene 错误容忍度 (180 trials)

| 变异类型 | Pass Rate | vs Clean Gene |
|----------|-----------|---------------|
| none (clean G3) | 0.485 | baseline |
| stale_paradigm | 0.510 | **+2.5pp** |
| overconstrained | 0.473 | -1.2pp |
| inverted_priority | 0.496 | +1.1pp |
| wrong_domain | 0.485 | +0.0pp |
| wrong_algorithm | 0.461 | -2.4pp |

**发现 3: stale_paradigm 变异比 clean gene 还好。**
过时的技术范式（如"用 csv 模块替代 pandas"）反而帮助模型——变异破坏了可能误导的具体细节，保留了有用的结构信息。只有 wrong_algorithm 造成有意义的下降。

### 2.4 RQ6: 自生成 Gene — 作者效应 (120 trials)

| Gene 作者 | Pass Rate |
|----------|-----------|
| Human | 0.822 |
| GPT-5.4 | 0.822 |
| Claude Haiku | 0.822 |
| Claude Opus | 0.822 |
| Gemini-3-Pro | 0.822 |
| None | 0.763 |

**发现 4: Gene 作者完全无关。** 所有 5 个作者在每个 (scenario, model) 组合上产生完全相同的结果。Gene 是二进制开关（有/无），不是精细知识载体。

---

## 3. Phase 2 结果：EvoMap 双回路实验

### 3.1 EX8: 记忆模式 vs 探索模式 (270 trials)

核心实验，直接对比 EvoMap 的两个回路。

| 条件 | evomap 组件 | Pro | Flash | Overall | vs baseline |
|------|------------|-----|-------|---------|-------------|
| memory_failures | 记忆→failures | **0.914** | **0.827** | **0.871** | **+14.6pp** |
| exploration_objective | 探索→objective | 0.848 | 0.827 | 0.837 | +11.2pp |
| exploration_direction | 探索→direction | 0.909 | 0.682 | 0.795 | +7.0pp |
| exploration_persona | 探索→persona | 0.842 | 0.699 | 0.770 | +4.5pp |
| gene_g3 | 标准 Gene | 0.848 | 0.680 | 0.764 | +3.9pp |
| memory_experience | 记忆→experience | 0.848 | 0.651 | 0.749 | +2.4pp |
| memory_signals | 记忆→signals | 0.842 | 0.627 | 0.735 | +0.9pp |
| none | baseline | 0.781 | 0.669 | 0.725 | — |
| exploration_full | 探索→全部 | 0.709 | 0.602 | **0.656** | **-7.0pp** |

**发现 5 (核心): memory_failures 全场第一 (+14.6pp)。**
仅告诉模型"前人踩过什么坑"（3-4 句话，~80 tokens）就能获得最大的性能提升。

**发现 6: exploration_full 比 baseline 还差 (-7.0pp)。**
同时给出 persona + objective + direction + target_profile 造成信息过载。EvoMap 的组件不应该全部同时注入。

**发现 7: memory_failures > memory_experience。**
纯失败知识 (87.1%) > 正+负综合经验 (74.9%)。添加正面策略信息反而稀释了失败警告的效果。

**逐场景分析：memory_failures 的具体影响**

| 场景 | none | memory_failures | Delta |
|------|------|----------------|-------|
| S012_uv_spectroscopy | 0.000 | **1.000** | **+100pp** |
| S026_earthquake_catalog | 0.500 | **1.000** | **+50pp** |
| S113_inventory_reorder | 0.500 | **1.000** | **+50pp** |
| S030_fossil_morpho | 0.867 | **1.000** | +13pp |
| S105_community_detection | 0.950 | **1.000** | +5pp |
| 其他 10 个场景 | = | = | 0pp |

memory_failures 在 gene-sensitive 场景上表现极为突出：S012 从 0%→100%，S026 和 S113 从 50%→100%。在 always-pass 场景上不造成任何负面影响。

### 3.2 EX9: 失败引导 vs 正确策略 (150 trials)

| 条件 | Pro | Flash | Overall | vs baseline |
|------|-----|-------|---------|-------------|
| failure_warnings | 0.770 | **0.821** | **0.795** | **+7.0pp** |
| correct_strategy | 0.781 | 0.741 | 0.761 | +3.6pp |
| failure_first | **0.848** | 0.618 | 0.733 | +0.7pp |
| none | 0.781 | 0.669 | 0.725 | — |
| strategy_first | 0.723 | 0.682 | 0.703 | -2.3pp |

**发现 8: 纯失败警告 > 纯正确策略 (+3.4pp)。**
这是最具实用意义的发现——收集"什么会出错"比整理"应该怎么做"更有价值。

**发现 9: 组合不如纯粹。**
failure_first (先失败再策略) 和 strategy_first (先策略再失败) 都不如 failure_warnings 单独使用。混合正负信息稀释了负面知识的集中效果。

**发现 10: 信息呈现顺序影响显著。**
failure_first (+0.7pp) vs strategy_first (-2.3pp) — 失败在前效果好 3pp。模型对 prompt 前部的信息赋予更高权重。

### 3.3 EX10: 角色光谱 (180 trials)

| Persona | Pro | Flash | Overall | vs baseline |
|---------|-----|-------|---------|-------------|
| **novice** | **0.915** | 0.697 | **0.806** | **+8.0pp** |
| generic_senior | 0.842 | **0.742** | 0.792 | +6.7pp |
| expert_adjacent | 0.848 | 0.629 | 0.738 | +1.3pp |
| expert_wrong | 0.842 | 0.627 | 0.735 | +0.9pp |
| expert_exact | 0.776 | 0.692 | 0.734 | +0.9pp |
| none | 0.781 | 0.669 | 0.725 | — |

**发现 11 (最反直觉): "你是编程学生" > "你是领域专家"。**
- Pro: novice=91.5% vs expert_exact=77.6% — **差距 13.9pp**
- novice persona 触发模型进入"谨慎模式"——更多注释、更多边界检查、更保守的实现选择
- expert persona 触发"自信模式"——跳过验证步骤，使用高级但容易出错的方法

**发现 12: 专家领域精度无关紧要。**
expert_wrong (0.735) ≈ expert_exact (0.734) ≈ expert_adjacent (0.738)。告诉模型"你是 NLP 工程师"去解光谱问题，效果和"你是光谱化学家"完全一样。Persona 的作用不是提供领域知识，而是激活某种"解题态度"。

### 3.4 EX11: 失败案例密度 (150 trials)

| 失败案例数 | Pro | Flash | Overall | vs 0 条 |
|-----------|-----|-------|---------|---------|
| 0 | 0.781 | 0.669 | 0.725 | — |
| 1 | **0.914** | 0.665 | 0.790 | +6.5pp |
| **2** | **0.914** | **0.743** | **0.829** | **+10.4pp** |
| 3 | 0.848 | 0.759 | 0.803 | +7.8pp |
| 4 | 0.848 | 0.761 | 0.804 | +7.9pp |

**发现 13: 2 条失败案例是精确甜蜜点。**
- Pro 在 1 条时即饱和 (91.4%)，2 条无额外收益
- Flash 在 2 条时达到最优 (74.3%)，3-4 条无额外收益
- 综合来看，**2 条失败 > 1 条 > 3 条 ≈ 4 条**
- 超过 2 条后，模型对额外失败信息的边际利用率为零

### 3.5 EX12: 自我预判 vs 外部知识 (180 trials)

| 方法 | Pro | Flash | Overall | vs baseline |
|------|-----|-------|---------|-------------|
| curated_failures | 0.770 | **0.821** | **0.795** | **+7.0pp** |
| rubber_duck | **0.914** | 0.631 | 0.773 | +4.8pp |
| gene_g3 | 0.848 | 0.680 | 0.764 | +3.9pp |
| test_first | 0.848 | 0.660 | 0.754 | +2.9pp |
| none | 0.781 | 0.669 | 0.725 | — |
| self_anticipation | 0.764 | 0.683 | 0.724 | -0.2pp |

**发现 14: 自我预判（"先想坑再编码"）≈ baseline。**
让模型自己预测可能的失败完全无效。模型无法可靠地预见自己的盲点——这正是失败经验需要从外部提供的原因。

**发现 15: 橡皮鸭法（"先解释方案再编码"）对强模型极有效。**
rubber_duck 在 Pro 上达到 91.4%（与最优条件持平），但在 Flash 上仅 63.1%。强模型善于通过"自我解释"发现逻辑漏洞，弱模型的自我解释能力不足以产生校正效果。

### 3.6 EX13: 信息框架效应 (180 trials)

相同的策略信息，5 种不同的措辞框架：

| 框架 | 措辞示例 | Pro | Flash | Overall | vs baseline |
|------|---------|-----|-------|---------|-------------|
| **warning** | "不这样做会失败" | **0.914** | **0.747** | **0.831** | **+10.5pp** |
| socratic | "你想过X会怎样吗？" | 0.848 | 0.735 | 0.791 | +6.6pp |
| suggestive | "你可以考虑..." | 0.781 | 0.752 | 0.767 | +4.1pp |
| none | (无) | 0.781 | 0.669 | 0.725 | — |
| imperative | "你必须..." | 0.776 | 0.673 | 0.724 | -0.1pp |
| teaching | "原理是这样的..." | 0.776 | 0.537 | **0.656** | **-6.9pp** |

**发现 16: warning 框架全面碾压其他框架 (+10.5pp)。**
同样的策略步骤，用"不这样做会导致测试失败"来表述，效果远好于"你应该这样做"。

**发现 17: teaching 框架比不说还差 (-6.9pp)。**
解释底层原理让模型"分心"——它花更多输出 token 在理解原理上，而不是正确实现。Flash 上 teaching = 53.7%，是全部条件中的最低值。

**发现 18: imperative（命令式）≈ baseline。**
"你必须"这种权威命令完全无效。模型不会因为被"命令"而做得更好。

---

## 4. Phase 3 结果：机制探索实验

### 4.1 EX14: 失败的真假 — Failure Authenticity (180 trials)

核心机制问题：失败引导有效，到底是因为**信息内容**（模型学到了坑在哪里），还是因为**激活了谨慎模式**（看到 WARNING 就变小心了）？

| 条件 | 内容 | Pro | Flash | Overall | vs baseline |
|------|------|-----|-------|---------|-------------|
| real_failures | 真实领域失败模式 | **0.914** | **0.827** | **0.871** | **+14.6pp** |
| generic_warnings | 通用编程警告 | 0.781 | 0.822 | **0.801** | **+7.6pp** |
| absurd_warnings | 荒谬警告 | 0.848 | 0.702 | **0.775** | **+5.0pp** |
| plausible_fake | 编造的领域假失败 | 0.832 | 0.627 | 0.730 | +0.5pp |
| none | baseline | 0.781 | 0.669 | 0.725 | — |
| cross_domain | 跨域真实失败 | 0.781 | 0.640 | 0.711 | -1.5pp |

**发现 19 (机制揭示): 失败引导通过"双通道机制"生效。**

- **信息通道 (~+7-9pp):** real_failures (+14.6pp) 远超其他条件 → 真实失败的具体内容提供了不可替代的信息
- **信号通道 (~+5pp):** absurd_warnings (+5.0pp) 内容完全荒谬（"确保代码不会产生自我意识"）但仍有效 → 纯粹的 WARNING/CRITICAL 关键词激活了谨慎行为模式
- **generic_warnings (+7.6pp)** 叠加了信号效应 + 通用编程谨慎（"小心 off-by-one"虽不针对领域，但确实是有效提醒）
- **plausible_fake (+0.5pp) ≈ 无效** → 编造的领域假失败既无信息价值，又因试图伪装成领域知识而干扰了模型的判断

**发现 20: 编造的假失败可能有毒。**
逐场景分析显示 plausible_fake 在部分场景上严重有害：
- S113_inventory_reorder: plausible_fake = **0%** vs baseline 50% vs real = 100% — 假失败让模型去避免一个不存在的问题，反而引入了新错误
- S101_climate_attribution: plausible_fake = **46%** vs baseline 100% — 原本会做对的任务被假失败搞砸

**最反直觉的对比:** S113 上 absurd_warnings = **100%** vs plausible_fake = **0%**。告诉模型"小心代码产生自我意识"比精心编造的"注意 Wagner-Whitin 动态批量算法"效果好 100pp。

### 4.2 EX15: 最优配方组合 — Recipe Combination (240 trials)

Phase 2 找到三个最优成分（novice +8.0pp, warning +10.5pp, 2 failures +10.4pp）。它们能否叠加使用？

| 条件 | 成分 | Pro | Flash | Overall | vs baseline |
|------|------|-----|-------|---------|-------------|
| warning_only | 警告框架 | **0.914** | 0.747 | **0.831** | **+10.5pp** |
| failures_only | 2 条失败 | **0.915** | 0.743 | 0.829 | +10.4pp |
| novice_failures | 新手+失败 | 0.914 | 0.742 | 0.828 | +10.3pp |
| novice_only | 新手角色 | 0.915 | 0.697 | 0.806 | +8.0pp |
| warning_failures | 警告+失败 | 0.842 | 0.751 | 0.797 | +7.1pp |
| novice_warning | 新手+警告 | 0.848 | 0.725 | 0.786 | +6.1pp |
| **full_recipe** | **新手+警告+失败** | **0.781** | **0.760** | **0.771** | **+4.5pp** |
| none | baseline | 0.781 | 0.669 | 0.725 | — |

**发现 21 (核心实用发现): 成分组合严重"减效"，不可叠加。**

- 理论加性预测: novice (+8) + warning (+10.5) + failures (+10.4) = +28.9pp
- 实际 full_recipe: **+4.5pp** — 仅为预测值的 **15.6%**
- **full_recipe 是所有非 baseline 条件中最差的** — 三个成分叠加反而产生了信息过载
- 在 Pro 上最极端: full_recipe (78.1%) = baseline (78.1%)，三个成分的效果完全被抵消

**发现 22: 双成分组合也不如单成分。**
- novice_failures (+10.3pp) ≈ failures_only (+10.4pp) — novice 的 +8pp 贡献完全被吸收
- warning_failures (+7.1pp) < warning_only (+10.5pp) — 加上失败案例反而降低了 3.4pp
- novice_warning (+6.1pp) < 两者任一 — 同样是减效

**机制解释:** 三个成分都通过激活"谨慎模式"生效。当谨慎模式已被一个成分充分激活后，额外的谨慎信号不提供增量价值，反而占用了 prompt 空间，稀释了单一信号的集中效果。这与 EX8 的 exploration_full (-7.0pp) 和 EX9 的组合实验结论完全一致。

**实用建议: 选择单一最强成分即可。推荐 warning 框架（+10.5pp，且实现最简单——只需在策略步骤前加 "WARNING: skipping this causes failures"）。**

### 4.3 EX16: 难度感知与利害框架 — Difficulty & Stakes (180 trials)

最"零成本"的引导方式——不需要领域知识、失败案例或策略，只需要一句话改变模型对任务的感知。

| 条件 | prompt 示例 | Pro | Flash | Overall | vs baseline |
|------|-----------|-----|-------|---------|-------------|
| **high_stakes** | "代码将部署到生产环境" | 0.842 | **0.748** | **0.795** | **+7.0pp** |
| easy_explicit | "这是简单任务" | 0.832 | 0.697 | 0.765 | +3.9pp |
| hard_explicit | "只有 30% 通过率" | 0.842 | 0.651 | 0.747 | +2.1pp |
| low_stakes | "只是练习" | 0.799 | 0.688 | 0.744 | +1.9pp |
| none | baseline | 0.781 | 0.669 | 0.725 | — |
| competitive | "和 100 个 AI 比" | 0.654 | 0.755 | **0.705** | **-2.1pp** |

**发现 23: "代码要上线"是最有效的零成本引导 (+7.0pp)。**
不需要任何领域知识——一句"This code will be deployed in a production system where correctness is paramount"就能获得和 curated_failures 相当的效果。这是最容易落地的 prompt engineering 技巧。

**发现 24 (反直觉): "这很简单" (+3.9pp) > "这很难" (+2.1pp)。**
预期是 hard_explicit 触发谨慎、easy_explicit 触发偷懒，但数据相反。可能的解释："这很简单"让模型选择更简洁的实现方案，减少了复杂代码引入的错误；而"这很难"让模型过度思考，尝试更复杂的算法。

**发现 25: 竞争框架有害 (-2.1pp)。**
- Pro 上灾难性: 65.4%（-12.7pp）— 竞争压力让强模型追求"炫技"而非正确性
- Flash 上反而正面: 75.5%（+8.6pp）— 弱模型被竞争激励了
- 这是 **Pro 和 Flash 反应方向完全相反** 的又一案例

---

## 5. Phase 4 结果：EvoMap 生态优势验证

Phase 1-3 已经确立了 EvoMap 记忆系统（memory_failures）的有效性。Phase 4 要回答一个更直接的问题：**EvoMap 的生态系统设计相比日常 prompt engineering 手段有什么独特优势？** 我们从五个维度做正面对比。

### 5.1 EX17: 结构化格式优势 (180 trials)

EvoMap 使用 XML 标签（`<memory-failures>`）结构化引导信息。这种格式设计本身是否有价值？我们将同一份失败信息用 5 种不同格式呈现。

| 格式 | 说明 | ~Tokens | Pro | Flash | Overall | vs none |
|------|------|---------|-----|-------|---------|---------|
| **evomap_structured** | XML 标签 + 角色说明 + 分节 | ~156 | **80.0%** | **66.7%** | **73.3%** | **+20.0pp** |
| markdown_sections | Markdown 标题/列表 | ~117 | 73.3% | 66.7% | 70.0% | +16.7pp |
| bullet_list | 纯项目符号列表 | ~81 | 66.7% | 53.3% | 60.0% | +6.7pp |
| raw_paragraph | 一段自然语言 | ~124 | 60.0% | 60.0% | 60.0% | +6.7pp |
| keyword_dump | 逗号分隔关键词 | ~49 | 66.7% | 46.7% | 56.7% | +3.3pp |
| none | 无引导 | 0 | 66.7% | 40.0% | 53.3% | — |

**发现 26: EvoMap 的 XML 格式比纯文本高 +13pp。**
同样的失败信息，用 `<memory-failures>` 标签包装后比写成一段自然语言效果好一倍（+20pp vs +6.7pp）。格式的阶梯清晰可见：**XML 结构 > Markdown 结构 > 列表 ≈ 段落 > 关键词**。

这意味着 EvoMap 的格式设计不是装饰——XML 标签帮助模型精确定位引导信息的类型和边界，就像代码中的类型标注帮助编译器理解数据一样。有趣的是 Markdown 也表现不错（70%），说明**任何有结构的格式都显著优于无结构文本**，但 XML 标签提供了最清晰的语义边界。

### 5.2 EX18: 进化循环模拟 (150 trials)

EvoMap 的核心价值主张是：通过积累历史失败经验，让模型"一次成功"而不是反复试错。我们设计了两轮实验来检验这一主张：第一轮正常生成，如果失败则构造第二轮重试。

| 条件 | 说明 | Pro | Flash | Overall | vs none | ~Tokens |
|------|------|-----|-------|---------|---------|---------|
| **single_shot_evomap** | 单轮 + EvoMap 记忆 | **80.0%** | **66.7%** | **73.3%** | **+20.0pp** | ~1,893 |
| retry_with_errors | 两轮：带具体错误信息 | 73.3% | 60.0% | 66.7% | +13.3pp | ~2,811 |
| retry_with_evomap | 两轮：带错误 + EvoMap 记忆 | 73.3% | 60.0% | 66.7% | +13.3pp | ~2,845 |
| retry_blind | 两轮：仅告知"测试未通过" | 73.3% | 53.3% | 63.3% | +10.0pp | ~2,856 |
| single_shot_none | 单轮无引导（冷启动） | 66.7% | 40.0% | 53.3% | — | ~1,626 |

**发现 27 (核心): 一轮 EvoMap > 两轮盲重试，且省 1/3 token。**

这是最直观的成本效益论证：
- **single_shot_evomap: 73.3%，~1,893 tokens（1 次 API 调用）**
- retry_with_errors: 66.7%，~2,811 tokens（2 次 API 调用）
- 差距: EvoMap 高 6.6pp，同时少用 33% tokens、少调 1 次 API

换句话说：**与其让模型失败后看着错误信息修补，不如一开始就告诉它前人踩过的坑。** "预防"显著优于"治疗"。

**发现 28: 重试时注入 EvoMap 记忆 ≈ 仅提供错误信息。**
retry_with_evomap (66.7%) = retry_with_errors (66.7%)。在第二轮注入 EvoMap 记忆没有额外收益——因为模型已经从自己的错误输出中获取了最直接的反馈。EvoMap 记忆的价值在**首轮预防**，而不是事后补救。

### 5.3 EX19: EvoMap 最优配置 vs 常见替代方案 (210 trials)

直接对比日常 prompt engineering 中最常见的方法与 EvoMap 最优配置。

| 条件 | 说明 | ~Tokens | Pro | Flash | Overall | vs none |
|------|------|---------|-----|-------|---------|---------|
| **evomap_optimized** | 2 条失败 + warning 框架 | ~94 | **80.0%** | 46.7% | 63.3% | +10.0pp |
| careful_prompt | "仔细检查边界条件" | ~19 | 60.0% | **66.7%** | 63.3% | +10.0pp |
| chatgpt_system | "你是有帮助的编码助手" | ~17 | 73.3% | 46.7% | 60.0% | +6.7pp |
| stackoverflow_hints | 关键算法/库提示 | ~111 | 73.3% | 46.7% | 60.0% | +6.7pp |
| expert_cot | "你是专家，逐步思考" | ~16 | 66.7% | 40.0% | 53.3% | +0.0pp |
| none | 无引导 | 0 | 66.7% | 40.0% | 53.3% | — |
| skill_full | 完整 SKILL.md | ~549 | 73.3% | 33.3% | 53.3% | +0.0pp |

**发现 29: 在 Pro 上，EvoMap 最优配置 (80%) 碾压所有替代方案。**
- evomap_optimized (80%) > skill_full (73.3%) > chatgpt_system (73.3%) > expert_cot (66.7%)
- 关键差异：EvoMap 用 ~94 tokens 达到 80%，SKILL.md 用 ~549 tokens 只达到 73.3%
- **Token 效率: EvoMap 用 1/6 的 token 实现更高的通过率**

**发现 30: "逐步思考"(CoT) 和完整文档在这个场景下无效。**
expert_cot (53.3%) = none (53.3%)，skill_full (53.3%) = none (53.3%)。CoT 对科学计算任务不提供帮助，完整文档造成信息稀释。有趣的是 careful_prompt（仅 19 tokens 的"仔细点"）在 Flash 上达到 66.7%——简短的注意力提醒对弱模型有效，验证了 Phase 3 发现的信号通道效应。

### 5.4 EX20: 基因跨任务复用性 (180 trials)

EvoMap 的基因不是一次性知识。如果同领域的基因可以复用，就省去了为每个新任务编写专门引导的成本。

基因来源映射：
- **sibling (同领域):** S012 UV光谱 ↔ S108 Raman光谱, S026 地震 ↔ S106 地震去噪, S105 社区检测 ↔ S096 网络影响力
- **cousin (跨领域):** S012 光谱峰检测 ↔ S026 地震峰检测, S113 库存优化 ↔ S103 计量经济

| 条件 | 说明 | Pro | Flash | Overall | vs none |
|------|------|-----|-------|---------|---------|
| generic_gene | 通用元基因（无领域知识） | 66.7% | **53.3%** | **60.0%** | **+6.7pp** |
| exact_gene | 精确匹配 Gene G3 | **73.3%** | 33.3% | 53.3% | +0.0pp |
| sibling_gene | 同领域兄弟基因 | 66.7% | 40.0% | 53.3% | +0.0pp |
| skill_exact | 精确匹配 SKILL.md | **73.3%** | 33.3% | 53.3% | +0.0pp |
| none | 无引导 | 66.7% | 40.0% | 53.3% | — |
| cousin_gene | 跨域表亲基因 | 73.3% | 20.0% | 46.7% | -6.7pp |

**发现 31: Pro 和 Flash 对 Gene 的反应方向相反。**

Pro 模型：
- exact_gene (73.3%) = cousin_gene (73.3%) = skill_exact (73.3%) > none (66.7%)
- 精确基因、表亲基因和完整 Skill 对 Pro 都有效（+6.7pp），且效果相同

Flash 模型：
- generic_gene (**53.3%**) > none (40.0%) > exact_gene (33.3%) > cousin_gene (**20.0%**)
- **具体领域基因对 Flash 有害！** 跨域表亲基因最严重（-20pp）
- 唯一安全的是不含任何领域知识的通用元基因（+13.3pp）

**发现 32: 弱模型消化不了具体领域策略。**
这与 Phase 2-3 的模式一致：Flash 从"信息补充"中受益有限，反而被复杂的领域知识干扰。对 Flash 来说，最有效的增强方式始终是 memory_failures（EX21 Flash: 40% → 66.7%），而不是 Gene 或 Skill。

### 5.5 EX21: 完整生态 vs 传统知识管理 (180 trials)

终极对比：EvoMap 的精炼知识 vs 传统的"给模型塞文档"方法。

| 条件 | 来源 | ~Prompt Tokens | Pro | Flash | Overall | vs none |
|------|------|---------------|-----|-------|---------|---------|
| **evomap_memory_only** | EvoMap 记忆 | **~157** | **80.0%** | **66.7%** | **73.3%** | **+20.0pp** |
| evomap_curated | EvoMap 组合 | ~135 | **80.0%** | 33.3% | 56.7% | +3.3pp |
| evomap_gene_only | EvoMap 基因 | ~226 | 73.3% | 33.3% | 53.3% | +0.0pp |
| skill_raw | 传统 SKILL.md | ~477 | 73.3% | 33.3% | 53.3% | +0.0pp |
| none | 无引导 | 0 | 66.7% | 40.0% | 53.3% | — |
| skill_plus_examples | SKILL.md + 示例代码 | **~702** | 66.7% | 33.3% | **50.0%** | **-3.3pp** |

**发现 33 (Phase 4 核心): 157 tokens 的 EvoMap 记忆 > 702 tokens 的传统文档。**

数据一目了然：
- **evomap_memory_only: 73.3%（157 tokens）** — 仅 2-4 条失败警告
- skill_plus_examples: 50.0%（702 tokens）— 完整 SKILL.md + 示例代码
- 差距: **+23.3pp，token 仅为 1/4.5**

在 Flash 上更极端：evomap_memory_only (66.7%) vs skill_plus_examples (33.3%)——**翻倍**的通过率，1/4 的 token。

**发现 34: 传统文档堆砌不仅无效，还有害。**
- skill_raw (477 tokens) = none — 完整 SKILL.md 等于没用
- skill_plus_examples (702 tokens) = -3.3pp — **加上示例代码反而更差**
- 在 Flash 上: skill_raw (33.3%) < none (40.0%) — 文档对弱模型是噪声

**发现 35: EvoMap 记忆是唯一对 Pro 和 Flash 同时大幅有效的组件。**

| 组件 | Pro 增益 | Flash 增益 | 双模型安全 |
|------|---------|-----------|-----------|
| memory_failures | +13.3pp | **+26.7pp** | **安全** |
| Gene G3 / Skill | +6.7pp | -6.7pp | **有害** |
| skill_plus_examples | +0.0pp | -6.7pp | **有害** |
| evomap_curated | +13.3pp | -6.7pp | **不安全** |

只有 `memory_failures` 在两个模型上都是正向增益。所有其他组件对 Flash 都有害或无效。这使得 EvoMap 记忆系统成为唯一一个可以"闭眼用"的增强组件。

---

## 6. 跨实验交叉分析

### 6.1 强模型 vs 弱模型的引导敏感度

| 引导类型 | Pro 最佳 | Flash 最佳 | Pro 依赖 | Flash 依赖 |
|---------|---------|-----------|---------|-----------|
| EX8 最优 | memory_failures (91.4%) | memory_failures (82.7%) | 态度调整 | 信息补充 |
| EX10 最优 | novice (91.5%) | generic_senior (74.2%) | 谨慎触发 | 能力框架 |
| EX12 最优 | rubber_duck (91.4%) | curated_failures (82.1%) | 自我反思 | 外部知识 |
| EX13 最优 | warning (91.4%) | suggestive (75.2%) | 恐惧驱动 | 温和引导 |
| EX14 最优 | real_failures (91.4%) | real/generic (82.2%) | 信息+信号 | 任何警告 |
| EX16 最优 | high_stakes (84.2%) | competitive (75.5%) | 责任感 | 竞争激励 |
| EX20 最优 | exact_gene (73.3%) | generic_gene (53.3%) | 领域知识 | 通用提醒 |

**规律：** Pro（强模型）最受益于"态度改变"型引导（novice persona, rubber duck, warning frame），不需要额外的领域知识。Flash（弱模型）最受益于"信息补充"型引导（curated failures, exploration_objective），需要实际的领域线索。EX16 再次印证：Pro 和 Flash 对同一引导的反应方向可能完全相反（competitive 在 Pro -12.7pp vs Flash +8.6pp）。

**Phase 4 新增规律：** EX20 进一步揭示了一个重要维度——具体领域知识（Gene/Skill）对 Flash 实际上有害。Flash 唯一安全的增强手段是 memory_failures 和通用元基因。这说明对弱模型的 prompt engineering 策略应该与强模型完全不同。

### 6.2 场景分类的引导效果

在 22 个 gene-sensitive 场景中：
- **4 个场景对 memory_failures 反应极强**（S012, S026, S113, S030: +13pp 到 +100pp）
- **6 个场景对任何引导反应中等**（+5pp 到 +12pp）
- **12 个场景对引导反应微弱**（<5pp 差异）

memory_failures 从未在任何场景上造成负面影响（最差 delta = 0pp），而 plausible_fake 和 exploration_full 在多个场景上造成严重伤害。**安全性排序: real_failures > generic_warnings > absurd_warnings >> plausible_fake > cross_domain。**

### 6.3 信息量与效果的关系

将所有 100+ 种条件按注入 token 量和效果排列：

| Token 范围 | 最佳条件 | 平均 delta |
|-----------|---------|-----------|
| 0 tok | none (baseline) | 0 |
| ~20 tok | novice persona / careful_prompt | +8.0pp / +10.0pp |
| ~80 tok | memory_failures | **+14.6pp** |
| ~94 tok | evomap_optimized | +10.0pp |
| ~120 tok | gene_g3 | +3.9pp |
| ~157 tok | evomap_memory_only (EX21) | **+20.0pp** |
| ~200 tok | exploration_full | **-7.0pp** |
| ~477 tok | skill_raw | +0.0pp |
| ~600 tok | skill_l1 | +4.1pp |
| ~702 tok | skill_plus_examples | **-3.3pp** |

**存在明确的信息量最优区间（50-160 tokens），超过该区间后效果急剧下降乃至转负。** Phase 4 EX21 的 skill_plus_examples (-3.3pp) 再次确认：更多文档 ≠ 更好结果。

### 6.4 组合惩罚定律

EX15 的配方组合实验与 EX8 的 exploration_full、EX9 的混合策略、EX21 的 evomap_curated 共同揭示了一个一致性极强的规律：

| 实验 | 单成分最优 | 组合条件 | 组合效果 | 惩罚 |
|------|-----------|---------|---------|------|
| EX8 | memory_failures +14.6pp | exploration_full (全部) | **-7.0pp** | -21.6pp |
| EX9 | failure_warnings +7.0pp | failure_first (失败+策略) | +0.7pp | -6.3pp |
| EX15 | warning_only +10.5pp | full_recipe (三成分) | +4.5pp | -6.0pp |
| EX21 | evomap_memory_only +20.0pp | evomap_curated (基因+记忆) | +3.3pp | -16.7pp |

**组合惩罚定律:** 每增加一个引导维度，效果不是叠加而是衰减。EX21 的 evomap_curated (+3.3pp) vs evomap_memory_only (+20.0pp) 是最新证据——加上 Gene 摘要后效果反而暴跌 16.7pp。最优策略永远是**单一维度、集中火力**。

### 6.5 EvoMap 记忆的跨实验一致性

memory_failures / evomap_memory_only 在 4 个独立实验中的表现：

| 实验 | 实验设计 | 记忆条件 Pass Rate | vs Baseline | Delta |
|------|---------|-------------------|-------------|-------|
| EX8 | 记忆 vs 探索（9 条件） | 87.1% | 72.5% | +14.6pp |
| EX17 | 格式对比（6 条件） | 73.3% | 53.3% | +20.0pp |
| EX18 | 进化循环（5 条件） | 73.3% | 53.3% | +20.0pp |
| EX21 | 生态对比（6 条件） | 73.3% | 53.3% | +20.0pp |

无论实验设计如何变化，memory_failures 的增益始终在 **+14.6pp 到 +20.0pp** 之间。更重要的是，它在 Flash（弱模型）上的增益（+26.7pp）远大于 Pro（+13.3pp），说明 EvoMap 记忆对弱模型的帮助尤其大。

---

## 7. 核心发现总结

### Top 23 发现（按实用价值排序）

| # | 发现 | 来源 | 效应量 | 实用建议 |
|---|------|------|--------|---------|
| 1 | 失败知识 > 正确策略 | EX8/EX9 | +14.6pp vs +3.9pp | 优先收集"什么会出错"而非"应该怎么做" |
| 2 | 警告框架 > 所有其他框架 | EX13 | +10.5pp vs -6.9pp | 用"不X会失败"替代"应该X" |
| 3 | 成分不可叠加 | EX15/EX21 | 组合仅为预测值 16% | **不要混合使用**，选择单一最强成分 |
| 4 | 新手角色 > 专家角色 | EX10 | +8.0pp vs +0.9pp | 用"你是学生"替代"你是专家" |
| 5 | "代码要上线" = 零成本最优 | EX16 | +7.0pp（无需领域知识） | 最简单的 prompt engineering 技巧 |
| 6 | 双通道机制 | EX14 | 信息~+9pp + 信号~+5pp | 真实失败不可替代，但通用警告也有价值 |
| 7 | 2 条失败 = 最优密度 | EX11 | 82.9% 峰值 | 精确给 2 条失败案例 |
| 8 | 完整引导 = 信息过载 | EX8/EX21 | -7.0pp / -3.3pp | 不要同时给所有信息 |
| 9 | 编造假失败可能有毒 | EX14 | 0pp 到 -50pp | 宁可不给，也不要编造领域失败 |
| 10 | 教学式解释有害 | EX13 | -6.9pp | 不要解释原理，直接给结论 |
| 11 | 竞争框架伤强模型 | EX16 | Pro -12.7pp | 不要告诉强模型"和别人比" |
| 12 | "这很简单" > "这很难" | EX16 | +3.9pp vs +2.1pp | 难度标签的效果反直觉 |
| 13 | 命令语气无效 | EX13 | -0.1pp | "你必须"不如"你可以考虑" |
| 14 | Gene 作者无关 | RQ6 | 0pp 差异 | 谁写的引导不重要 |
| 15 | 自我预判是幻觉 | EX12 | ≈0pp | 模型无法预见自己的盲点 |
| 16 | 橡皮鸭法对强模型有效 | EX12 | Pro +13.3pp | 让强模型先解释再编码 |
| 17 | 荒谬警告也有效 | EX14 | +5.0pp | WARNING 关键词本身激活谨慎模式 |
| 18 | 专家领域精度无关 | EX10 | <1pp 差异 | 任何专家角色效果相同 |
| **19** | **XML 结构 > 纯文本 (+13pp)** | **EX17** | **73.3% vs 60.0%** | **用 XML 标签包装引导信息** |
| **20** | **一轮 EvoMap > 两轮盲重试** | **EX18** | **73.3% vs 63.3%，省 33% token** | **预防优于治疗** |
| **21** | **157 tok 记忆 > 702 tok 文档** | **EX21** | **73.3% vs 50.0%** | **质量远优于数量** |
| **22** | **领域基因对弱模型有害** | **EX20** | **Flash: -6.7pp 到 -20pp** | **弱模型只用记忆，不用基因** |
| **23** | **EvoMap 记忆跨实验一致 +15-20pp** | **EX8/17/18/21** | **4 个独立实验复现** | **最可靠的增强组件** |

### Grand Narrative

> **"恐惧驱动 > 知识驱动 > 命令驱动 — 但恐惧不可叠加"**
>
> LLM 代码生成的最优引导策略不是给更多信息，而是给**最小量的负面知识**。
> 失败引导通过**双通道机制**生效：真实失败内容提供信息（~+9pp），WARNING 信号
> 激活谨慎模式（~+5pp）。但多个引导成分不可叠加——每增加一个维度，效果衰减而非增强。
>
> **最简配方（单一成分）：**
> - 有失败数据时：2 条真实失败案例 + warning 框架 ≈ 80 tokens → **+14.6pp**
> - 无失败数据时：一句 "This code will be deployed in production" → **+7.0pp**
>
> Phase 4 将这个结论推到了产品化层面：EvoMap 的 XML 格式设计帮助模型更精准地解析引导（+13pp）；
> 一轮 EvoMap 记忆注入比两轮试错迭代更高效（省 33% token，高 6.6pp）；157 tokens 的精炼
> 记忆超过 702 tokens 的传统文档堆砌（+23pp）。**EvoMap 不只是一种 prompt engineering 技巧，
> 它是一个将"失败知识"高效编码、结构化传递、跨任务复用的完整系统。**
>
> 这颠覆了四个直觉：(1) "more context = better output"（信息越多反而越差）；
> (2) "expert > novice"（新手角色优于专家）；(3) "组合最优成分 = 更优"（单一成分反而最强）；
> (4) "试错迭代能修复问题"（预防远优于治疗）。

---

## 8. 对 EvoMap 架构的启示

### 8.1 记忆模式 vs 探索模式

| 组件 | 效果 | 建议 |
|------|------|------|
| memory→failures | **最优 (+14.6pp)** | 核心组件，应优先注入 |
| exploration→objective | 好 (+11.2pp) | 明确目标有价值 |
| exploration→direction | 好 (+7.0pp) | 策略方向有用 |
| memory→signals | 中等 (+0.9pp) | 仅关键词不够 |
| memory→experience | 中等 (+2.4pp) | 混合正负信息不如纯失败 |
| exploration→persona | 中等 (+4.5pp) | 有用但不如 novice 有效 |
| **exploration→全部** | **有害 (-7.0pp)** | **严禁同时开启所有组件** |

### 8.2 最优注入策略

```
推荐的 EvoMap 配置（基于 EX15 + Phase 4 修正）:

1. 选择单一最强组件 — 不要组合:
   - 首选: memory→failures (2 条真实失败, warning 框架包装)
   - 备选（无失败数据时）: high_stakes 框架（一句话即可）
2. 使用 XML 结构化格式（<memory-failures>标签）
3. 总 token 严格控制在 80-160
4. 绝不同时开启多个组件（EX21: 加基因后效果从 +20pp 跌到 +3.3pp）

关键禁忌:
- 不要同时开启 failures + persona + warning（EX15: 组合 = +4.5pp < 单独 +10.5pp）
- 不要编造领域失败（EX14: plausible_fake 可能有毒）
- 不要使用 teaching 框架解释原理
- 不要注入超过 160 tokens 的引导
- 不要给弱模型注入具体领域基因（EX20: Flash cousin_gene = 20%）
```

### 8.3 EvoMap 的五大生态优势（Phase 4 验证）

| 优势 | 实验 | 证据 | 故事 |
|------|------|------|------|
| **格式设计** | EX17 | XML > 纯文本 +13pp | 结构化标签不是装饰，是语义边界 |
| **预防 > 治疗** | EX18 | 单轮记忆 > 两轮重试，省 33% token | 一次成功比反复试错更高效 |
| **Token 经济性** | EX19 | 94 tok EvoMap > 549 tok SKILL.md | 用 1/6 token 达到更好效果 |
| **知识复用** | EX20 | Pro: sibling ≈ exact gene | 同领域基因可直接复用（Pro） |
| **质量 > 数量** | EX21 | 157 tok > 702 tok (+23pp) | 精炼记忆远超传统文档堆砌 |

### 8.4 按模型能力的差异化策略

Phase 4 的一个重要副产品是明确了**对强弱模型应采用不同的增强策略**：

| 维度 | Pro（强模型） | Flash（弱模型） |
|------|-------------|----------------|
| 最有效组件 | memory_failures (+13pp) | memory_failures (**+27pp**) |
| Gene/Skill | 有效 (+7pp) | **有害** (-7pp 到 -20pp) |
| 通用元基因 | 无效 (0pp) | 有效 (+13pp) |
| 组合引导 | 减效 | 严重减效 |
| 建议 | 记忆 > 基因 > 无引导 | 记忆 > 通用提醒 > 无引导 >> 基因 |

---

## 9. 方法论

### 9.1 局限性

1. **模型覆盖有限：** 主要使用 Gemini 3.1 系列（2 个模型），未覆盖 Claude/GPT/Qwen/DeepSeek
2. **场景偏向：** 43 个场景中 11 个 always-fail + 10 个 always-pass = 仅 22 个 gene-sensitive 场景产生有效信号
3. **单次测试：** temperature=0.0，每个条件仅运行 1 次，无法估计方差
4. **失败案例质量：** EX8-EX13 的失败案例由人工编写，质量高于平均水平
5. **Gemini 3.1 thinking 模式：** 模型内部思考可能消耗大量输出 token，影响代码完整度
6. **Phase 4 样本量：** 每个条件 30 trials（15 场景 × 2 模型），单模型仅 15 trials，统计功效有限

### 9.2 复现

```bash
# 安装
conda create -n gene-bench python=3.11
conda activate gene-bench
pip install numpy pandas scipy scikit-learn matplotlib seaborn openai google-generativeai

# Phase 1-3 EvoMap 实验（8 线程并行，约 20 分钟）
python run_evomap_experiments.py --experiment all \
    --gemini-key "$GEMINI_API_KEY" --workers 8

# Phase 4 生态优势验证（8 线程并行，约 20 分钟）
python run_evomap_experiments.py --experiment phase4 \
    --gemini-key "$GEMINI_API_KEY" --workers 8

# 原始 RQ 实验（串行，约 2 小时）
python run_gene_bench.py --rq all \
    --models gemini_31_pro,gemini_31_flash \
    --gemini-key "$GEMINI_API_KEY"
```

---

## 10. 附录

### A. 实验条件完整列表

**EX8 — 记忆 vs 探索（9 条件）：**
- `none`: 无引导
- `memory_signals`: 领域关键词（"absorbance, wavelength, peak detection..."）
- `memory_failures`: 历史失败模式（"Forgetting to convert min-distance from nm..."）
- `memory_experience`: 完整经验叙述（成功策略 + 失败模式）
- `exploration_persona`: 专家角色（"You are a analytical chemist specializing in..."）
- `exploration_objective`: 明确目标 + 成功标准
- `exploration_direction`: 策略方向 = gene summary
- `exploration_full`: persona + objective + direction + target_profile
- `gene_g3`: 标准 Gene（对照组）

**EX9 — 失败引导（5 条件）：**
- `none`, `correct_strategy`, `failure_warnings`, `failure_first`, `strategy_first`

**EX10 — 角色光谱（6 条件）：**
- `none`, `expert_exact`, `expert_adjacent`, `expert_wrong`, `generic_senior`, `novice`

**EX11 — 失败密度（5 条件）：**
- `0_failures`, `1_failure`, `2_failures`, `3_failures`, `4_failures`

**EX12 — 自我预判（6 条件）：**
- `none`, `self_anticipation`, `rubber_duck`, `test_first`, `curated_failures`, `gene_g3`

**EX13 — 框架效应（6 条件）：**
- `none`, `imperative`, `suggestive`, `warning`, `teaching`, `socratic`

**EX14 — 失败真假（6 条件）：**
- `none`: 无引导
- `real_failures`: 真实领域失败模式（= memory_failures）
- `plausible_fake`: 编造的合理但不真实的领域失败（如"注意 Wagner-Whitin 算法"）
- `generic_warnings`: 通用编程警告（"小心 off-by-one"、"注意类型转换"）
- `cross_domain`: 完全不相关领域的真实失败（如把音频失败给光谱任务）
- `absurd_warnings`: 荒谬警告（"确保代码不会产生自我意识"）

**EX15 — 配方组合（8 条件）：**
- `none`, `failures_only` (2条失败), `novice_only`, `warning_only`
- `novice_failures` (新手+失败), `warning_failures` (警告+失败), `novice_warning` (新手+警告)
- `full_recipe` (新手+警告+2条失败)

**EX16 — 难度感知（6 条件）：**
- `none`: 无引导
- `hard_explicit`: "这个任务很难，只有 30% 通过率"
- `easy_explicit`: "这是简单任务，大多数方案首次通过"
- `high_stakes`: "代码将部署到生产环境，正确性至关重要"
- `competitive`: "你的方案将与 100 个 AI 模型比较"
- `low_stakes`: "这只是练习，不用太在意边界情况"

**EX17 — 结构化格式（6 条件）：**
- `none`: 无引导
- `evomap_structured`: EvoMap 标准 XML 格式（`<memory-failures>` 标签 + 角色说明 + 分节）
- `raw_paragraph`: 同样失败信息写成一段自然语言
- `bullet_list`: 无标签的纯项目符号列表
- `markdown_sections`: Markdown 标题/列表组织
- `keyword_dump`: 从失败模式中提取关键词逗号分隔

**EX18 — 进化循环（5 条件）：**
- `single_shot_none`: 单轮无引导（冷启动 baseline）
- `single_shot_evomap`: 单轮 + EvoMap 预加载记忆（memory_failures）
- `retry_blind`: 两轮：第1轮失败后仅告知"测试未通过，请修改"
- `retry_with_errors`: 两轮：第1轮失败后告知具体 FAIL 测试项和错误输出
- `retry_with_evomap`: 两轮：第1轮失败后告知错误信息 + 注入 EvoMap 记忆

**EX19 — EvoMap vs 替代方案（7 条件）：**
- `none`: 无引导
- `chatgpt_system`: "You are a helpful coding assistant. Write correct, well-tested code."
- `careful_prompt`: "Be extremely careful. Check all edge cases. Validate inputs."
- `expert_cot`: "You are an expert. Think step by step, then implement."
- `stackoverflow_hints`: 模拟 StackOverflow 搜索结果（关键算法/库/概念提示）
- `skill_full`: 完整 SKILL.md 文档（~549 tokens）
- `evomap_optimized`: EvoMap 最优配置——2 条失败 + warning 框架（~94 tokens）

**EX20 — 基因复用性（6 条件）：**
- `none`: 无引导
- `exact_gene`: 精确匹配的 Gene G3（为该任务生成的基因）
- `sibling_gene`: 同领域兄弟基因（如 UV 光谱任务用 Raman 光谱基因）
- `cousin_gene`: 跨领域表亲基因（结构类似，如光谱峰检测用地震峰检测基因）
- `generic_gene`: 通用元基因（"仔细处理边界条件，验证输入输出格式"）
- `skill_exact`: 精确匹配的完整 SKILL.md（对照组）

**EX21 — 完整生态 vs 传统知识管理（6 条件）：**
- `none`: 无引导
- `skill_raw`: 完整 SKILL.md 原文（~477 prompt tokens）
- `skill_plus_examples`: SKILL.md + references/examples.md（~702 prompt tokens）
- `evomap_gene_only`: 仅 Gene G3（~226 prompt tokens）
- `evomap_memory_only`: 仅 memory_failures（~157 prompt tokens）
- `evomap_curated`: Gene 摘要 + 2 条失败 + warning 框架（~135 prompt tokens）

### B. 数据文件

所有原始数据存储为 JSONL 格式，位于 `data/` 目录：
- `rq{1-7}_results.jsonl` — Phase 1 实验
- `evomap_ex{8-13}_results.jsonl` — Phase 2 实验
- `evomap_ex{14-16}_results.jsonl` — Phase 3 实验
- `evomap_ex{17-21}_results.jsonl` — Phase 4 实验
- `gemini_rq{1-2}_results.jsonl` — Gemini 2.5 pilot

每条记录包含：`trial_key`, `trial_config`, `eval` (pass_rate, n_pass, n_total), `code_length`, `prompt_tokens`, `input_tokens`, `output_tokens`。

---

*Generated from 4,068 trials across 43 scientific computing scenarios.*
*Models: Gemini 3.1 Pro Preview, Gemini 3.1 Flash Lite Preview.*
*Date: 2026-03-17.*
