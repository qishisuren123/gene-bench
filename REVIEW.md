# Gene-Bench 完整审查文件

> 更新日期：2026-04-02
> 状态：所有 45 场景已通过验证，Gene 已转换为 GEP v1.5.0，SKILL.md 全部补齐

---

## 一、项目三大目标

| # | 目标 | 核心思路 | 对应实验 |
|---|------|----------|----------|
| 1 | **Skill 引子** | 展示 Skill 的有趣发现（章节归因、截断效应、格式重包装等），吸引读者关注，同时暴露 Skill 的缺点（冗长、格式次优），自然引出 Gene 概念 | EX22, EX23, EX25, EX10, EX13, EX16 |
| 2 | **Skill vs Gene 对比** | 直接对比 Skill 和 Gene 在多种维度上的表现，证明轻量 Gene 可以匹敌甚至超越冗长 Skill | EX1, EX2, EX19, EX21, EX24 |
| 3 | **纯 Gene 实验 + evomap 推广** | 深入探索 Gene 的特性（鲁棒性、可组合、可迁移、可进化），连接 evomap 平台概念（Gene/Capsule/EvolutionEvent/Memory） | EX3-EX9, EX11, EX12, EX14, EX15, EX17, EX18, EX20, EX26, EX27 |

---

## 二、45 场景详情

### 分类概览

| 领域 | 场景 | 数量 |
|------|------|------|
| 神经科学 | S002, S007 | 2 |
| 生物/蛋白质 | S005, S044, S045, S048, S052, S053, S102 | 7 |
| 物理/天文 | S011, S033, S036, S037, S115 | 5 |
| 光谱/化学 | S012, S108 | 2 |
| 海洋/地球 | S017, S026, S067, S077, S106 | 5 |
| 生态/环境 | S030, S054, S060 | 3 |
| 气象/气候 | S068, S069, S072, S074, S101 | 5 |
| 信号/音频 | S028, S090, S091, S093, S112 | 5 |
| 生物医学 | S053, S084 | 2 |
| 网络/社会 | S096, S105 | 2 |
| 金融 | S107 | 1 |
| 工程/CS | S109, S110, S111, S113, S114 | 5 |
| 因果推断 | S103 | 1 |
| 多传感器 | S104 | 1 |

### A 批：L1/L2 分级场景（10 个，来自 pilot）

| # | 场景ID | 任务概述 | PASS数 | L1 | L2 | 关键检查点 |
|---|--------|----------|:------:|:--:|:--:|-----------|
| 1 | S002_spike_behavior | 将神经 spike 时间戳和行为速度数据标准化为 trial-based HDF5，需要 spike binning 和速度重采样 | 10 | 3 | 7 | HDF5结构、spike时间排序、bin宽度、插值精度、元数据完整性 |
| 2 | S005_protein_parse | 解析 SwissProt JSON 提取蛋白质结构化信息(accession/gene/organism/GO terms)输出 TSV | 11 | 2 | 9 | 列结构、序列长度匹配、GO注释解析、EC号提取、特征计数 |
| 3 | S007_data_viz | 可视化神经群体活动：trial-averaged 热图 + population PSTH with SEM | 8 | 1 | 7 | PNG生成、子图数量、颜色映射、热图排序、时间轴标注、SEM区间 |
| 4 | S011_particle_physics | 分析粒子碰撞事件：质量窗口筛选、信号/背景分类、信噪比和统计显著性 | 16 | 2 | 14 | 不变质量计算、Z-boson窗口、横动量分布、截面归一化、显著性估计 |
| 5 | S012_uv_spectroscopy | 检测 UV-Vis 吸收光谱峰：波长、高度、FWHM、面积，识别主峰 | 12 | 2 | 10 | 峰检测灵敏度、FWHM计算、波长精度、多样品处理、主峰识别 |
| 6 | S017_ctd_ocean | 处理 CTD 温盐深剖面数据：深度插值、位密度计算、温跃层和混合层深度识别 | 13 | 2 | 11 | 深度网格插值、密度公式、温跃层梯度阈值、混合层判定、站点汇总 |
| 7 | S026_earthquake_catalog | 分析地震目录：Haversine 距离余震识别、Gutenberg-Richter b 值最大似然估计 | 15 | 2 | 13 | b值MLE计算、Haversine距离、余震窗口、震级-频率分布、完整性检查 |
| 8 | S028_audio_features | 从合成音频提取 STFT 频谱图和手工实现的 MFCC(numpy 三角滤波器组) | 17 | 2 | 15 | mel滤波器组实现、MFCC系数数、频谱图维度、窗函数、帧移/帧长 |
| 9 | S030_fossil_morpho | 化石形态计量分析：elongation/flatness/sphericity/椭球体积，按 taxon 统计 | 16 | 2 | 14 | 形状指数公式、椭球体积估计、taxon分组、描述统计、异常值处理 |
| 10 | S101_climate_attribution | 气候变化归因：将观测温度异常回归到太阳/火山/GHG/气溶胶强迫，输出归因百分比 | 11 | 3 | 8 | OLS/Ridge回归、归因分数计算、多重共线性处理、置信区间、残差分析 |

### B 批：PASS/FAIL 简单评分场景（20 个，来自 pilot）

| # | 场景ID | 任务概述 | PASS数 | 关键检查点 |
|---|--------|----------|:------:|-----------|
| 11 | S033_exoplanet_transit | 检测凌星信号并拟合周期/深度/持续时间，输出 JSON | 17 | 凌星检测、周期估计、深度拟合、持续时间、诊断图 |
| 12 | S036_cmb_power_spectrum | 从 HEALPix 温度图计算角功率谱 C_l，球谐分解 | ~21 | 球谐系数、多极值、功率谱形状、统计分析、误差估计 |
| 13 | S037_asteroid_orbit | 从 2D 位置观测计算轨道要素(半长轴/离心率/周期) | 14 | 轨道要素计算、Kepler定律、能量守恒、角动量、周期估计 |
| 14 | S044_bfactor_analysis | 分析蛋白质 B 因子分布识别柔性区域 | 15 | 统计量(均值/中位数/标准差)、四分位数、高柔性区域识别、残基分类 |
| 15 | S045_ramachandran | 生成 Ramachandran 图并用 Z-score 识别结构异常值 | 13 | 二面角计算、散点图生成、Z-score阈值、异常值标记、结构分类 |
| 16 | S048_gene_ontology | 基因本体富集分析：映射 GO 术语、计算 p 值和 fold enrichment | 12 | Fisher精确检验、多重检验校正、fold enrichment、GO分类、排序 |
| 17 | S052_phylogenetic_distance | 多序列比对系统发育距离：Hamming/Jukes-Cantor/Kimura | ~10 | 三种距离度量、矩阵格式、成对输出、距离公式正确性 |
| 18 | S053_methylation_beta | DNA 甲基化 β 值差异分析：识别 DMR、delta-beta 计算 | 14 | delta-beta计算、DMR识别算法、CpG统计、case/control分组 |
| 19 | S054_species_accumulation | 物种累积曲线：样本随机化稀疏化、置信区间、丰富度估计 | 15 | 累积算法、随机化次数、置信区间、Chao1估计、收敛判断 |
| 20 | S060_phenology_shifts | 物候变化检测：PELT 变点检测 + Mann-Kendall 趋势检验 | ~16 | 变点检测、趋势检验、气候协变量、物候日期提取、统计显著性 |
| 21 | S067_salinity_gradient | 河口盐度梯度：检测盐跃层、Simpson 分层参数、分层分类 | 13 | 盐跃层识别、Simpson参数计算、分层分类(well-mixed/partial/stratified) |
| 22 | S068_weather_fronts | 温度梯度锋面检测：空间梯度分析、最小长度阈值过滤 | 12 | 梯度计算、阈值过滤、锋面长度、JSON输出、PNG可视化 |
| 23 | S069_rainfall_extreme | 降雨重现期：年最大序列法 + GEV 分布拟合 | 13 | GEV拟合(shape/loc/scale)、重现水平计算、极端事件统计 |
| 24 | S072_ozone_profile | 臭氧廓线：温度递减率对流层顶、对流层/平流层臭氧柱浓度 | ~13 | 对流层顶识别、臭氧柱积分、温度递减率计算、廓线可视化 |
| 25 | S074_heat_index | 热指数计算 + 热浪检测：百分位阈值 + 最短持续时间 | 16 | 热指数公式(Rothfusz)、百分位阈值、最短天数、事件识别、CSV输出 |
| 26 | S077_grain_size | 粒径分布分析：统计量、百分位数、粒径分级 | 12 | 基本统计、D10/D50/D90、粒径分类标准、频率分布 |
| 27 | S084_dose_response | 4PL 剂量-反应曲线拟合：IC50/EC50、Hill slope | 16 | 4参数拟合(top/bottom/IC50/slope)、R²、曲线图、置信区间 |
| 28 | S090_noise_reduction | LMS 自适应噪声消除：输出清洁信号 + SNR 改善指标 | 15 | LMS算法实现、步长选择、SNR计算、收敛验证、信号质量 |
| 29 | S091_modulation_classify | IQ 样本调制分类(BPSK/QPSK/8PSK/16QAM/64QAM)：6+ 特征 + 交叉验证 | 13 | 特征提取(≥6个)、分类器训练、交叉验证、混淆矩阵、准确率 |
| 30 | S093_echo_removal | 自相关回声检测 + 自适应回声消除 | 16 | 延迟检测(自相关)、回声消除算法、性能指标、对比图 |

### C 批：新场景（15 个，L1/L2 分级，全部已补齐 SKILL）

| # | 场景ID | 任务概述 | PASS数 | L1 | L2 | 关键检查点 |
|---|--------|----------|:------:|:--:|:--:|-----------|
| 31 | S102_protein_secondary | Chou-Fasman/GOR 蛋白质二级结构预测(helix/sheet/coil) | 12 | 3 | 9 | 倾向性表实现、滑动窗口、结构分配规则、预测精度、FASTA解析 |
| 32 | S103_instrumental_variable | 2SLS 工具变量回归因果推断，对比 naive OLS | 9 | 2 | 7 | 第一阶段回归、第二阶段估计、标准误差、weak IV检验、OLS对比 |
| 33 | S104_multisensor_anomaly | 多传感器时序异常检测：rolling z-score + 相关性 + Mahalanobis | 5 | 2 | 3 | z-score计算、相关性检查、Mahalanobis距离、异常分类(point/collective/contextual) |
| 34 | S105_community_detection | 图网络重叠社区检测：异步标签传播/模块度优化 | 7 | 2 | 5 | 社区划分、模块度计算、重叠节点处理、边列表解析 |
| 35 | S106_seismic_denoise | 地震波 Butterworth 带通滤波 + STA/LTA P 波到时检测 | 7 | 2 | 5 | 带通设计、STA/LTA比值、P波识别、SNR改善、三分量处理 |
| 36 | S107_regime_switch | 金融时序政体转换：滚动波动率变点 + low_vol/high_vol/crisis 分类 | 5 | 2 | 3 | 变点检测、政体分类、Sharpe ratio、滚动窗口、统计摘要 |
| 37 | S108_raman_spectroscopy | 拉曼光谱分析：基线校正(多项式/ALS) + 峰检测 + 高斯拟合 | 4 | 2 | 2 | 基线校正方法、突出度阈值、高斯FWHM/面积、化合物匹配 |
| 38 | S109_hdf5_chunked | 大 CSV → 分块压缩 HDF5：类型自动检测、可配置压缩(gzip/lzf) | 4 | 2 | 2 | 分块策略、压缩选择、类型推断、属性存储、读取效率 |
| 39 | S110_log_regex | 服务器日志正则解析：状态码分布、响应时间、Top URL、错误率 | 10 | 2 | 8 | 正则模式匹配、多格式支持、状态码统计、响应时间百分位 |
| 40 | S111_cuda_memory | CUDA 显存事件日志分析：时间线重建、峰值、碎片化、优化建议 | 9 | 2 | 7 | 内存时间线、峰值计算、碎片率、提前释放检测、张量生命周期 |
| 41 | S112_midi_chords | MIDI 和弦检测：时间窗口分组 + 和弦类型识别(major/minor/dim/aug/7th) | 6 | 2 | 4 | 音符分组算法、和弦分类、调性检测、间隔计算 |
| 42 | S113_inventory_reorder | 库存优化：需求预测(Normal/Poisson) + EOQ + 安全库存 + 再订购点 | 4 | 2 | 2 | EOQ公式、安全库存计算、服务水平参数、需求分布拟合 |
| 43 | S114_obstacle_avoidance | 2D 机器人避障：RRT/势场法 + 线-圆碰撞检测 + 间隙指标 | 8 | 2 | 6 | 路径规划算法、碰撞检测、最小间隙、路径平滑、JSON输出 |
| 44 | S115_quantum_circuit | 量子电路模拟：状态向量 + 门操作(H/X/Y/Z/CNOT/CZ/RX/RY/RZ) + 测量 | 6 | 2 | 4 | 状态向量维护、张量积、门矩阵正确性、测量概率、shot采样 |

### 检查点统计汇总

| 批次 | 场景数 | 总 PASS 数 | 平均 PASS/场景 | 评分方式 |
|------|:------:|:---------:|:-------------:|----------|
| A 批 (S002-S101) | 10 | 129 | 12.9 | L1/L2 分级 |
| B 批 (S033-S096) | 20 | ~277 | ~13.9 | PASS/FAIL |
| C 批 (S102-S115) | 15 | 92 | 6.1 | L1/L2 分级 |
| **合计** | **45** | **~498** | **~11.1** | — |

---

## 三、实验体系总览

### 按目标分组

```
目标一：Skill 引子（6 个实验）
├── EX22  Skill 章节归因     → 哪个 Skill 章节贡献最大？
├── EX23  截断效应           → Skill 截断到 3 行还有用吗？
├── EX25  格式重包装         → 同样的 Skill 内容换个格式就变好？
├── EX10  角色定位谱系       → 角色精度对效果有多大影响？
├── EX13  框架效应           → 相同信息不同说法效果差多少？
└── EX16  利害框架           → "高风险" vs "快速原型" 影响代码质量？

目标二：Skill vs Gene 对比（5 个实验）
├── EX1   Gene 完整度梯度   → G0→G1→G2→G3→G4→L1 单调递增？
├── EX2   Gene vs Skill     → G3 能否匹敌 L1/L4？
├── EX19  对比 PE 方法       → Gene vs ChatGPT提示/CoT/SO/Skill
├── EX21  生态对比           → Skill/Skill+例子/Gene/Memory/全套 evomap
└── EX24  互补性             → Gene + 代码示例/API笔记能否超越 Skill？

目标三：纯 Gene 实验 + evomap 推广（16 个实验）
├── Gene 核心特性
│   ├── EX3   变异容忍度     → Gene 对错误信息有多鲁棒？
│   ├── EX4   跨领域迁移     → Gene 能跨域复用吗？
│   ├── EX5   组合效应       → 多 Gene 组合 > 单 Gene？
│   ├── EX6   自生成 Gene    → 模型能自己写有效的 Gene？
│   └── EX7   接种效应       → "疫苗提示"能防御错误 Gene？
├── evomap Memory 概念
│   ├── EX8   记忆 vs 探索   → 过去经验(signals/failures) vs 未来导向(persona/objective)
│   ├── EX9   失败引导学习   → 负面知识("别这样做") vs 正面知识("这样做")
│   ├── EX11  失败密度       → 0→4 条失败警告的剂量-反应关系
│   └── EX14  失败真实性     → 真实/编造/跨域/荒谬 失败警告效果差异
├── evomap Evolution 概念
│   ├── EX18  进化循环       → 失败→重试 的进化循环是否提升？evomap 引导重试 vs 盲重试
│   ├── EX26  进化叙事       → "这个 Gene 经过多轮进化" 的来源叙事是否增强效果？
│   └── EX20  Gene 复用       → exact→sibling→cousin→generic 退化曲线
├── 信号与格式
│   ├── EX17  格式对比       → XML结构化 vs 纯文本 vs 要点 vs Markdown vs 关键词
│   └── EX27  记忆来源       → 人工策展 vs 自动提取 vs 模型自预测
├── 交互效应
│   ├── EX12  自我预判       → 元认知提示(预判错误/橡皮鸭/测试先行) vs 策展知识
│   └── EX15  组合饱和       → 多种负面信号叠加：饱和还是叠加？
```

---

## 四、27 个实验详细设置

### ═══ 目标一：Skill 引子 ═══

---

#### EX10 — 角色定位谱系 (Persona Spectrum)

**核心问题**：角色精度对任务完成质量的影响有多大？精确领域专家 vs 相邻领域 vs 错误领域 vs 通用高级工程师 vs 新手。

**预期亮点**：展示角色提示的有趣效果（如"新手角色"可能反而激发更仔细的编码），同时引出"Gene 天然包含领域 signals，比角色提示更精准"。

| 条件 | 系统提示内容 |
|------|-------------|
| `none` | 空白基线 |
| `expert_exact` | "You are a {精确领域专家，如 analytical chemist specializing in UV-Vis}" |
| `expert_adjacent` | "You are a {相邻领域专家，如 infrared spectroscopy researcher}" |
| `expert_wrong` | "You are a {错误领域专家，如 ML engineer working on NLP}" |
| `generic_senior` | "You are a senior software engineer with 20 years of experience" |
| `novice` | "You are a programming student learning {domain} for the first time" |

- 条件数：6
- 场景数：45
- 每模型 trials：270

---

#### EX13 — 框架效应 (Framing Effect)

**核心问题**：**完全相同的策略内容**，用不同语气（命令/建议/警告/教学/苏格拉底式提问）表达，效果差异多大？

**预期亮点**：证明"怎么说"和"说什么"同样重要，而 Skill 只关注内容不关注表达方式 → Gene 的 strategy 字段天然就是经过优化的表达。

| 条件 | 框架风格 | 提示模式 |
|------|---------|---------|
| `none` | 空白 | — |
| `imperative` | 命令式 | "DO the following steps exactly: 1. {step1} 2. {step2}..." |
| `suggestive` | 建议式 | "You might find helpful: - Consider: {step1}..." |
| `warning` | 警告式 | "WARNING — Past solutions failed due to: ⚠ {failure1}..." |
| `teaching` | 教学式 | "Let me teach you the correct approach. The key insight is: {summary}..." |
| `socratic` | 提问式 | "Before coding, ask yourself: What domain concepts? What's the core challenge? (Hint: {summary})" |

- 条件数：6
- 场景数：45
- 每模型 trials：270

---

#### EX16 — 利害框架 (Stakes Framing)

**核心问题**：任务框架（生产部署 vs 快速原型 vs 竞赛 vs 难度标注）如何影响代码质量？

**预期亮点**：发现"竞争框架"或"高难度标注"的有趣效应，暴露 Skill 缺乏这种元认知引导 → Gene 可以通过 category 字段(repair/optimize/innovate)提供任务定位。

| 条件 | 框架 | 核心消息 |
|------|------|---------|
| `none` | 空白 | — |
| `high_stakes` | 高风险 | "This code will be deployed in production... errors cause incorrect research conclusions" |
| `easy_explicit` | 标注简单 | "This is a straightforward task most competent developers can solve quickly" |
| `hard_explicit` | 标注困难 | "This is a challenging task requiring deep expertise in {domain}" |
| `competitive` | 竞赛 | "You are competing against GPT-5, Claude, and Gemini. Aim for highest test pass rate" |
| `low_stakes` | 低风险 | "Just a quick prototype — don't worry about edge cases" |

- 条件数：6
- 场景数：45
- 每模型 trials：270

---

#### EX22 — Skill 章节归因 (Skill Attribution)

**核心问题**：Skill 文档的哪个章节（overview/workflow/pitfalls/error_handling/quick_reference）贡献最大？Gene G3 能否超越任何单独章节？

**预期亮点**：这是目标一的**核心实验**。如果某个章节（如 pitfalls）主导了 Skill 的价值，说明 Skill 大部分内容是浪费 → Gene 用更少的 token 就能抓住核心。

| 条件 | 内容来源 | 注入方式 |
|------|---------|---------|
| `none` | 空白基线 | — |
| `skill_overview` | SKILL.md overview 章节 | `inject_skill_section()` |
| `skill_workflow` | SKILL.md workflow 章节 | 同上 |
| `skill_pitfalls` | SKILL.md pitfalls 章节 | 同上 |
| `skill_error_handling` | SKILL.md error_handling 章节 | 同上 |
| `skill_quick_ref` | SKILL.md quick_reference 章节 | 同上 |
| `gene_g3` | Gene G3（对照） | `inject_gene()` |

- 条件数：7
- 场景数：45
- 每模型 trials：315

---

#### EX23 — 截断效应 (Truncation Effect)

**核心问题**：Skill 章节截断到仅 3 行后是否还保留大部分引导价值？与 Gene G3 相比如何？

**预期亮点**：如果截断后效果相近，说明 Skill 严重冗余 → Gene 是信息压缩的正确方向。

| 条件 | 内容 | 说明 |
|------|------|------|
| `none` | 空白 | — |
| `pitfalls_short` | pitfalls 截断 3 行 | `inject_skill_truncated(skill_dir, "pitfalls", 3)` |
| `workflow_short` | workflow 截断 3 行 | 同上 |
| `mixed_short` | pitfalls 2行 + workflow 2行 | 混合截断 |
| `gene_g3` | Gene G3（对照） | 完整 Gene |

- 条件数：5
- 场景数：45
- 每模型 trials：225

---

#### EX25 — 格式重包装 (Format Repackaging)

**核心问题**：将 Skill pitfalls 内容从原始 Markdown 重新包装为 XML/警告框架/策展记忆等格式，效果是否改善？

**预期亮点**：证明 Skill 的原始 Markdown 格式并非最优 → evomap Gene 的结构化 XML 格式是更好的选择。

| 条件 | 来源 | 格式 |
|------|------|------|
| `none` | — | 空白 |
| `pitfalls_raw` | Skill pitfalls 原文 | 原始 Markdown |
| `pitfalls_as_xml` | Skill pitfalls | XML 结构化 (`inject_pitfalls_as_xml()`) |
| `pitfalls_warning` | Skill pitfalls | 警告框架 ("⚠ CRITICAL WARNINGS") |
| `memory_curated` | DOMAIN_INFO + gene | 策展记忆风格 |

- 条件数：5
- 场景数：45
- 每模型 trials：225

---

### ═══ 目标二：Skill vs Gene 对比 ═══

---

#### EX1 — Gene 完整度梯度 (Gene Completeness Gradient)

**核心问题**：从 G0(空白) 到 G4(最完整 Gene) 到 L1(Skill overview) 的信息梯度中，性能如何变化？是否单调递增？

**预期亮点**：**本项目最重要的实验**。如果 G3 已经接近 L1，说明 Gene 以 1/10 的 token 量达到了相近效果 → 核心卖点。

| 条件 | Gene 级别 | Token 量 (估计) | 信息内容 |
|------|----------|:--------------:|---------|
| `ex1_G0` | G0 | 0 | 空白（无任何上下文） |
| `ex1_G1` | G1 | ~50 | 仅 signals_match 关键词列表 |
| `ex1_G2` | G2 | ~150 | keywords + summary |
| `ex1_G3` | G3 | ~400 | keywords + summary + strategy |
| `ex1_G4` | G4 | ~600 | 完整 Gene（含 pitfalls/preconditions） |
| `ex1_L1` | L1 | ~2000 | SKILL.md overview 章节 |

- 条件数：6
- 场景数：45
- 每模型 trials：270

---

#### EX2 — Gene vs Skill 正面对决 (Head-to-Head)

**核心问题**：Gene G3 vs Skill L1(overview) vs Skill L4(完整 Skill 包) 的直接对比。

**预期亮点**：如果 Gene G3 ≈ Skill L1 > G0，同时 Skill L4 相对 L1 提升有限，则证明 Gene 的效率优势。

| 条件 | 级别 | 说明 |
|------|------|------|
| `ex2_no_context` | G0 | 空白基线 |
| `ex2_gene_g3` | G3 | 标准 Gene |
| `ex2_skill_l1` | L1 | SKILL.md overview |
| `ex2_skill_l4` | L4 | 完整 Skill 包（含 api_notes, examples） |

- 条件数：4
- 场景数：45
- 每模型 trials：180

---

#### EX19 — 对比 Prompt Engineering 方法 (vs PE Methods)

**核心问题**：Gene 与主流 Prompt Engineering 技术（系统提示、CoT、专家 CoT、StackOverflow 风格提示、完整 Skill）的横向对比。

**预期亮点**：定位 Gene 在 PE 方法谱系中的位置。如果 Gene 超越 ChatGPT 系统提示和 CoT → 证明领域知识压缩的价值。

| 条件 | 方法来源 | 提示内容 |
|------|---------|---------|
| `none` | 空白 | — |
| `chatgpt_system` | 标准系统提示 | "You are a helpful assistant that writes Python code..." |
| `careful_prompt` | CoT | "Think step by step. Break down the problem. Consider edge cases." |
| `expert_cot` | 专家 CoT | "You are a {expert}. Think through: 1. identify core {domain} challenge..." |
| `stackoverflow_hints` | SO 风格 | "Common SO answers for [{keywords}] tasks suggest: > step1 > step2..." |
| `skill_full` | 完整 Skill | `inject_skill_full()` |
| `evomap_optimized` | Gene + 失败记忆 | Gene G3 + memory_failures（evomap 最优组合） |

- 条件数：7
- 场景数：45
- 每模型 trials：315

---

#### EX21 — 生态对比 (Ecology Comparison)

**核心问题**：完整生态系统对比：Skill 单独 vs Skill+示例 vs Gene 单独 vs Memory 单独 vs evomap 全套（Gene+失败+信号）。

**预期亮点**：展示 evomap 生态（Gene + 失败记忆 + 信号）的组合优势，同时分解各组件的贡献。

| 条件 | 组件 | 说明 |
|------|------|------|
| `none` | 空白 | — |
| `skill_raw` | Skill L1 | 原始 SKILL.md overview |
| `skill_plus_examples` | Skill + 示例 | SKILL.md + references/examples.md |
| `evomap_gene_only` | Gene G3 | 纯 Gene |
| `evomap_memory_only` | Memory 信号 | 仅 domain signals（无策略） |
| `evomap_curated` | 全套 evomap | Gene G3 + memory_failures + memory_signals |

- 条件数：6
- 场景数：45
- 每模型 trials：270

---

#### EX24 — 互补性 (Complementarity)

**核心问题**：Gene G3 搭配 Skill 的代码示例或 API 笔记是否能超越单独使用？哪种补充材料最有效？

**预期亮点**：如果 Gene + examples > Gene alone ≈ Skill full → Gene 可以精准选择需要补充的知识，比完整 Skill 更灵活。

| 条件 | 组件 | 说明 |
|------|------|------|
| `none` | 空白 | — |
| `gene_alone` | Gene G3 | 纯 Gene |
| `gene_plus_examples` | Gene + 代码示例 | Gene G3 + references/examples.md |
| `gene_plus_api_notes` | Gene + API 笔记 | Gene G3 + references/api_notes.md |
| `skill_full` | 完整 Skill（上界） | `inject_skill_full()` |

- 条件数：5
- 场景数：45
- 每模型 trials：225

---

### ═══ 目标三：纯 Gene 实验 + evomap 推广 ═══

---

#### EX3 — Gene 变异容忍度 (Mutation Tolerance)

**核心问题**：Gene 被"变异"（错误算法/错误领域/优先级反转/过时范式/过度约束）后，性能下降多少？哪种变异最致命？

**evomap 连接**：对应 evomap 的 Gene 突变与进化概念——在进化过程中，Gene 必须容忍一定程度的噪声。

| 条件 | 变异类型 | 说明 |
|------|---------|------|
| `ex3_clean_g3` | 无 | 干净 Gene G3（对照） |
| `ex3_mutated_wrong_algorithm` | 错误算法 | 策略中替换为错误的算法建议 |
| `ex3_mutated_wrong_domain` | 错误领域 | 将领域上下文替换为无关领域 |
| `ex3_mutated_inverted_priority` | 优先级反转 | 颠倒策略步骤的优先顺序 |
| `ex3_mutated_stale_paradigm` | 过时范式 | 使用已淘汰的方法论 |
| `ex3_mutated_overconstrained` | 过度约束 | 添加不必要的限制条件 |

- 条件数：6
- 场景数：45
- 每模型 trials：270

---

#### EX4 — 跨领域 Gene 迁移 (Cross-Domain Transfer)

**核心问题**：Gene 能否从一个领域迁移到另一个领域？exact_match → same_domain → analogous_task → unrelated 的迁移效果如何退化？

**evomap 连接**：对应 evomap 的 Gene 复用/迁移概念——跨节点的 Gene 共享是 evomap 网络的核心价值。

| 迁移对 | 源场景 | 目标场景 | 迁移类型 |
|--------|--------|---------|---------|
| 1 | S090_noise_reduction | S106_seismic_denoise | analogous_task |
| 2 | S068_weather_fronts | S107_regime_switch | analogous_task |
| 3 | S012_uv_spectroscopy | S108_raman_spectroscopy | analogous_task |
| 4 | S084_dose_response | S113_inventory_reorder | unrelated |
| 5 | S002_spike_behavior | S112_midi_chords | unrelated |
| 6 | S033_exoplanet_transit | S111_cuda_memory | unrelated |
| 7-10 | 各自自身 | 各自自身 | exact_match |
| 11 | S090_noise_reduction | S093_echo_removal | same_domain |
| 12 | S012_uv_spectroscopy | S077_grain_size | same_domain |

- 条件数：5 (analogous_task/unrelated/exact_match/same_domain/none)
- 场景数：12 对（非全部 45）
- 每模型 trials：~60（特殊结构）

---

#### EX5 — Gene 组合效应 (Combination Effect)

**核心问题**：组合多个 Gene（互补/冲突）比单个 Gene 更好还是更差？

**evomap 连接**：对应 evomap 的 Gene 组合与合成——Agent 可以从多个 Gene 资产中选择并组合策略。

| 条件 | 组合方式 | 说明 |
|------|---------|------|
| `ex5_none` | 空白 | — |
| `ex5_single` | 单 Gene G3 | 标准单 Gene |
| `ex5_2x_complementary` | 2个互补 Gene | 同域不同场景的 Gene 合并 |
| `ex5_3x_complementary` | 3个互补 Gene | 同上，3个 |
| `ex5_2x_conflicting` | 2个冲突 Gene | 来自不同领域的 Gene 合并 |

- 条件数：5
- 场景数：45
- 每模型 trials：225

---

#### EX6 — 自生成 Gene (Self-Generated Gene)

**核心问题**：模型能否为自己生成有效的 Gene？作者身份（哪个模型写的）是否影响效果？

**evomap 连接**：对应 evomap 的自动 Gene 发现——如果模型能自生成有效 Gene，evomap 平台可以实现自动化 Gene 挖掘。

| 条件 | Gene 作者 | 说明 |
|------|----------|------|
| `ex6_none` | — | 空白基线 |
| `ex6_author_opus` | Claude Opus | Opus 写的 Gene |
| `ex6_author_haiku` | Claude Haiku | Haiku 写的 Gene |
| `ex6_author_gpt5_4` | GPT-5.4 | GPT-5.4 写的 Gene |
| `ex6_author_gemini_pro` | Gemini Pro | Gemini Pro 写的 Gene |
| `ex6_human_gene` | 人工策展 | 手工 Gene（对照） |

- 条件数：6
- 场景数：45
- 每模型 trials：270
- **前置步骤**：Phase 1 需要 4 个作者模型各生成 45 个 Gene = 180 次生成调用

---

#### EX7 — Gene 接种效应 (Vaccination Effect)

**核心问题**：提前"接种"（告知模型 Gene 可能有错）能否保护性能不受错误 Gene 的损害？

**evomap 连接**：对应 evomap 的 Gene 质量控制——在 Gene 置信度低时，平台可以通过"疫苗提示"保护 Agent。

| 条件 | Gene | 接种 | 说明 |
|------|------|------|------|
| `ex7_none` | 无 | 否 | 空白基线 |
| `ex7_clean_gene` | 干净 G3 | 否 | 正常 Gene |
| `ex7_wrong_gene` | 错误(wrong_algorithm) | 否 | 变异 Gene，无保护 |
| `ex7_vaccinated_clean` | 干净 G3 | **是** | 正常 Gene + 疫苗提示 |
| `ex7_vaccinated_wrong` | 错误 | **是** | 变异 Gene + 疫苗提示 |

- 条件数：5
- 场景数：45
- 每模型 trials：225

---

#### EX8 — 记忆 vs 探索 (Memory vs Exploration)

**核心问题**：面向过去的"记忆"信号（经验积累、失败教训）vs 面向未来的"探索"提示（角色定位、目标设定），哪个更有效？

**evomap 连接**：直接对应 evomap 的 Memory 系统——记忆是 evomap Agent 的核心能力之一。

| 条件 | 时间导向 | 内容 |
|------|---------|------|
| `none` | — | 空白 |
| `memory_signals` | 过去 | 领域信号/关键词列表 |
| `memory_failures` | 过去 | 失败模式（过去失败的教训） |
| `memory_experience` | 过去 | 综合：信号 + 成功策略 + 失败模式 |
| `exploration_persona` | 未来 | "{expert} with 15 years experience" |
| `exploration_objective` | 未来 | 明确的成功标准和边界条件 |
| `exploration_direction` | 未来 | Gene summary 作为探索方向 |
| `exploration_full` | 未来 | 完整探索档案(XML `<exploration-profile>`) |
| `gene_g3` | 对照 | 标准 Gene G3 |

- 条件数：9
- 场景数：45
- 每模型 trials：405

---

#### EX9 — 失败引导学习 (Failure-Guided Learning)

**核心问题**：负面知识（"别这样做"）vs 正面知识（"这样做"），哪个更有效？顺序（先失败再策略 vs 先策略再失败）是否重要？

**evomap 连接**：evomap 的 failure_patterns 字段——失败记忆是 Gene 进化的重要输入。

| 条件 | 内容 |
|------|------|
| `none` | 空白 |
| `correct_strategy` | 仅正确策略步骤 |
| `failure_warnings` | 仅失败警告 |
| `failure_first` | 先失败后策略 |
| `strategy_first` | 先策略后失败 |

- 条件数：5
- 场景数：45
- 每模型 trials：225

---

#### EX11 — 失败密度 (Failure Density)

**核心问题**：0→1→2→3→4 条失败警告的剂量-反应关系。是否存在饱和点或过载点？

**evomap 连接**：Gene 的 failure_patterns 数量设计——evomap 标准建议 4 条失败模式，这个实验验证这个设计。

| 条件 | 失败数 |
|------|-------|
| `0_failures` | 0 |
| `1_failure` | 1 |
| `2_failures` | 2 |
| `3_failures` | 3 |
| `4_failures` | 4 |

- 条件数：5
- 场景数：45
- 每模型 trials：225

---

#### EX12 — 自我预判 (Self-Anticipation)

**核心问题**：元认知提示（预判错误/橡皮鸭解释/测试先行）vs 外部策展知识，效果对比。

**evomap 连接**：如果模型自我预判不如策展知识 → 证明 evomap 外部知识资产的不可替代性。

| 条件 | 方法 |
|------|------|
| `none` | 空白 |
| `self_anticipation` | "预判你可能犯的 3-5 个错误，然后再编码" |
| `rubber_duck` | "向一个不懂 {domain} 的同事解释你的方法" |
| `test_first` | "先写 3-5 个断言测试，再实现代码" |
| `curated_failures` | 策展的失败模式（DOMAIN_INFO 2条 + gene pitfalls 2条） |
| `gene_g3` | Gene G3（对照） |

- 条件数：6
- 场景数：45
- 每模型 trials：270

---

#### EX14 — 失败真实性 (Failure Authenticity)

**核心问题**：失败警告的质量是否重要？真实 vs 似是而非的假的 vs 通用编码警告 vs 跨域 vs 荒谬 → 效果差异。

**evomap 连接**：验证 evomap 策展质量的价值——如果荒谬警告也有用，则"小心"的信号比内容更重要。

| 条件 | 失败类型 | 内容 |
|------|---------|------|
| `none` | — | 空白 |
| `real_failures` | 真实 | DOMAIN_INFO 中的实际失败模式 |
| `plausible_fake` | 似是而非 | "normalize to [0,1]", "use float32 not float64"... |
| `generic_warnings` | 通用编码 | "not handling edge cases", "off-by-one errors"... |
| `cross_domain` | 跨域 | 来自完全不同领域的 DOMAIN_INFO |
| `absurd_warnings` | 荒谬 | "function may reverse variable names", ">3 list comprehensions corrupts output"... |

- 条件数：6
- 场景数：45
- 每模型 trials：270

---

#### EX15 — 组合饱和 (Combination Saturation)

**核心问题**：多种"负面信号"（新手角色 + 警告框架 + 失败模式）叠加是饱和还是累加？

**evomap 连接**：evomap 组合策略设计——告知用户多少信号是最优的。

| 条件 | 组件 |
|------|------|
| `none` | 空白 |
| `novice_only` | 仅新手角色 |
| `warning_only` | 仅警告框架 |
| `failures_only` | 仅失败记忆 |
| `novice_warning` | 新手 + 警告 |
| `novice_failures` | 新手 + 失败 |
| `warning_failures` | 警告 + 失败 |
| `novice_warning_failures` | 全部三种 |

- 条件数：8
- 场景数：45
- 每模型 trials：360

---

#### EX17 — 格式对比 (Format Comparison)

**核心问题**：**完全相同的信息**（keywords + summary + strategy + failures），用不同格式（XML/纯文本/要点/Markdown/关键词）呈现，效果差异。

**evomap 连接**：验证 evomap 的 XML 结构化 Gene 格式是否优于其他格式。

| 条件 | 格式 |
|------|------|
| `none` | 空白 |
| `evomap_structured` | XML (`<evomap-gene format="structured" version="2.0">`) |
| `raw_paragraph` | 纯文本段落 |
| `bullet_list` | 要点列表 |
| `markdown_sections` | Markdown 分节 |
| `keyword_dump` | 仅关键词 ("Relevant: kw1 \| kw2 \| ...") |

- 条件数：6
- 场景数：45
- 每模型 trials：270

---

#### EX18 — 进化循环 (Evolution Loop)

**核心问题**：失败后重试（进化循环）是否提升性能？evomap 引导的重试 vs 盲重试 vs 带错误信息的重试。

**evomap 连接**：直接对应 evomap 的 EvolutionEvent 概念——Gene 进化需要反馈循环。

| 条件 | 轮次 | 重试策略 |
|------|------|---------|
| `none` | 1 | 空白，单次 |
| `single_shot_evomap` | 1 | Gene G3，单次 |
| `retry_blind` | 最多2 | 失败后盲重试："Try again with a different approach" |
| `retry_errors` | 最多2 | 失败后带错误信息重试 |
| `retry_evomap` | 最多2 | 失败后 Gene 引导重试："Use the strategic gene to guide your retry" |

- 条件数：5
- 场景数：45
- 每模型 trials：225（重试条件可能消耗 2× API 调用）

---

#### EX20 — Gene 复用 (Gene Reuse)

**核心问题**：Gene 从 exact → sibling(同域) → cousin(类比域) → generic(脱域) 的复用退化曲线。

**evomap 连接**：evomap 网络中的 Gene 共享/推荐——不同"距离"的 Gene 推荐效果如何？

| 条件 | Gene 来源 | 框架 |
|------|----------|------|
| `none` | 空白 | — |
| `exact_gene` | 目标场景自身 Gene | `<strategy-gene>` |
| `sibling_gene` | 同域不同场景 | `<strategy-gene source="sibling">` + "Adapt the strategy" |
| `cousin_gene` | 不同域结构类比 | `<strategy-gene source="cousin">` + "Extract transferable patterns" |
| `generic_gene` | 目标 Gene 脱域化 | 替换领域术语为通用词 |
| `skill_exact` | 目标 Skill L1 | 对照 |

- 条件数：6
- 场景数：45
- 每模型 trials：270

---

#### EX26 — 进化叙事 (Evolution Narrative)

**核心问题**：给 Gene 附加"进化来源故事"（多轮进化、置信度分数、浓缩胶囊、失败日志）是否改变效果？

**evomap 连接**：直接对应 evomap 的 EvolutionEvent 和 Capsule 概念——Gene 的来源叙事是否有价值？

| 条件 | 叙事风格 | 说明 |
|------|---------|------|
| `none` | 空白 | — |
| `evolution_full` | 完整进化事件 | `inject_evolution_event()` — 包含进化历史、适应度变化 |
| `gene_with_confidence` | 置信度标注 | "fitness: 0.85/1.0, high-confidence strategies" |
| `capsule_style` | 胶囊压缩 | "[GENE] {summary} \| Key: kw1, kw2, kw3" — 极限压缩 |
| `failed_attempts_only` | 仅失败日志 | "Evolution log — failed attempts (no successful strategy found yet)" |

- 条件数：5
- 场景数：45
- 每模型 trials：225

---

#### EX27 — 记忆来源 (Memory Source)

**核心问题**：失败知识的**来源身份**（人工策展 / 自动提取 Skill / 模型自预测）是否影响效果？

**evomap 连接**：验证 evomap 人工策展的价值 vs 自动化知识提取。

| 条件 | 知识来源 |
|------|---------|
| `none` | 空白 |
| `memory_curated` | 人工策展（DOMAIN_INFO + gene） |
| `pitfalls_auto_xml` | 自动提取 Skill pitfalls（XML） |
| `model_self_predict` | 模型自预测（"predict 3 most likely mistakes"） |

- 条件数：4
- 场景数：45
- 每模型 trials：180

---

## 五、模型配置

### 12 个模型

| 短名 | 模型 ID | 厂商 | 价格层 |
|------|---------|------|:------:|
| opus | claude-opus-4-6 | Anthropic | expensive |
| sonnet | claude-sonnet-4-6 | Anthropic | medium |
| haiku | claude-haiku-4-5 | Anthropic | cheap |
| gpt5_4 | gpt-5.4 | OpenAI | medium |
| gpt5_mini | gpt-5-mini | OpenAI | cheap |
| gpt5_nano | gpt-5-nano | OpenAI | free |
| gemini_pro | gemini-3.1-pro-preview | Google | free |
| gemini_flash | gemini-3.1-flash-lite-preview | Google | free |
| qwen_moe | qwen3.5-397b-a17b | Alibaba | cheap |
| qwen_coder | qwen3-coder | Alibaba | expensive |
| ds_v3 | deepseek-v3.2-exp | DeepSeek | medium |
| ds_r1 | deepseek-r1 | DeepSeek | expensive |

---

## 六、实验数量统计

### 按实验统计（每模型）

| 实验 | 目标 | 条件数 | 场景数 | 每模型trials | 说明 |
|------|:----:|:------:|:------:|:-----------:|------|
| EX1 | 2 | 6 | 45 | 270 | |
| EX2 | 2 | 4 | 45 | 180 | |
| EX3 | 3 | 6 | 45 | 270 | |
| EX4 | 3 | 5 | 12对 | ~60 | 特殊结构，expensive模型仅6对 |
| EX5 | 3 | 5 | 45 | 225 | |
| EX6 | 3 | 6 | 45 | 270 | +Phase1: 180次生成 |
| EX7 | 3 | 5 | 45 | 225 | |
| EX8 | 3 | 9 | 45 | 405 | |
| EX9 | 3 | 5 | 45 | 225 | |
| EX10 | 1 | 6 | 45 | 270 | |
| EX11 | 3 | 5 | 45 | 225 | |
| EX12 | 3 | 6 | 45 | 270 | |
| EX13 | 1 | 6 | 45 | 270 | |
| EX14 | 3 | 6 | 45 | 270 | |
| EX15 | 3 | 8 | 45 | 360 | |
| EX16 | 1 | 6 | 45 | 270 | |
| EX17 | 3 | 6 | 45 | 270 | |
| EX18 | 3 | 5 | 45 | 225 | 重试条件消耗2×API调用 |
| EX19 | 2 | 7 | 45 | 315 | |
| EX20 | 3 | 6 | 45 | 270 | |
| EX21 | 2 | 6 | 45 | 270 | |
| EX22 | 1 | 7 | 45 | 315 | |
| EX23 | 1 | 5 | 45 | 225 | |
| EX24 | 2 | 5 | 45 | 225 | |
| EX25 | 1 | 5 | 45 | 225 | |
| EX26 | 3 | 5 | 45 | 225 | |
| EX27 | 3 | 4 | 45 | 180 | |
| **合计** | | **153** | | **6,855** | |

### 按目标汇总

| 目标 | 实验数 | 每模型trials | 12模型总trials |
|------|:------:|:-----------:|:-------------:|
| 目标一：Skill引子 | 6 | 1,575 | 18,900 |
| 目标二：Skill vs Gene | 5 | 1,260 | 15,120 |
| 目标三：纯Gene+evomap | 16 | 4,020 | 48,240 |
| **总计** | **27** | **6,855** | **82,260** |

### 不同模型规模方案

| 方案 | 模型数 | 模型选择 | 总trials | 估计API调用 |
|------|:------:|---------|:--------:|:----------:|
| **精简版** | 2 | sonnet + gemini_flash | 13,710 | ~15,000 |
| **标准版** | 4 | sonnet + haiku + gpt5_mini + gemini_flash | 27,420 | ~30,000 |
| **扩展版** | 6 | +opus + gpt5_4 | 41,130 | ~45,000 |
| **完整版** | 12 | 全部 | 82,260 | ~90,000 |

---

## 七、实验设计调整建议

### 调整 1：为目标一增加"Skill 信息密度分析"

**理由**：当前目标一的实验可以更尖锐地暴露 Skill 的冗余问题。

**建议**：在 EX22/EX23 结果分析时增加 **token 效率指标**：
```
效率 = PASS_rate / token_count
```
这样可以直观展示 Gene G3 用 ~400 tokens 达到的效果 vs Skill L1 用 ~2000 tokens 达到的效果 → **5× token 效率**。

### 调整 2：为目标三强化 evomap 概念映射

当前实验名称需要在论文中明确映射到 evomap 术语：

| 实验 | evomap 概念 | 论文叙事 |
|------|-----------|---------|
| EX3 变异容忍度 | Gene Mutation | "Gene 作为进化策略模板的鲁棒性" |
| EX4 跨域迁移 | Gene Transfer / A2A Protocol | "跨节点 Gene 共享的可行性" |
| EX5 组合效应 | Gene Composition | "多 Gene 合成的涌现效应" |
| EX6 自生成 Gene | Automated Gene Discovery | "Agent 自主发现和发布 Gene 资产" |
| EX7 接种效应 | Gene Quality Control | "低置信度 Gene 的安全使用" |
| EX8 记忆 vs 探索 | Memory System | "过去经验 vs 未来探索的平衡" |
| EX18 进化循环 | EvolutionEvent | "反馈驱动的 Gene 进化循环" |
| EX26 进化叙事 | Capsule + EvolutionEvent | "Gene 的来源追溯与置信度" |

### 调整 3：精简冗余实验

以下实验存在一定重叠，可考虑合并或降低优先级：

| 重叠组 | 实验 | 建议 |
|--------|------|------|
| 失败知识系列 | EX9 + EX11 + EX14 | EX9 和 EX14 有重叠（都测试失败警告效果），可合并为一个 |
| 角色/框架系列 | EX10 + EX13 + EX16 | EX13 和 EX16 都测试"框架效应"，可合并 |
| 复用/迁移系列 | EX4 + EX20 | EX4 和 EX20 都测试跨域 Gene 复用，结构不同但主题一致 |

**保守建议**：保留全部 27 实验但分优先级执行：
- **P0（必做）**：EX1, EX2, EX3, EX22, EX19, EX21 — 6 个实验覆盖三个目标的核心
- **P1（推荐）**：EX4, EX6, EX8, EX13, EX17, EX23, EX24 — 7 个实验深化发现
- **P2（补充）**：其余 14 个实验提供完整性

### 调整 4：推荐执行顺序

```
Phase 0 (验证): 1 场景 × 1 模型 × 全部 27 实验 → smoke test
Phase 1 (P0):   EX1 + EX2 + EX3 + EX22 + EX19 + EX21 → 核心发现
Phase 2 (P1):   EX4 + EX6 + EX8 + EX13 + EX17 + EX23 + EX24 → 深化
Phase 3 (P2):   剩余实验 → 完整性
Phase 4 (扩模型): 从精简版 → 标准版 → 完整版 逐步扩展
```

---

## 八、论文叙事结构建议

基于三大目标的论文架构：

```
1. Introduction
   - Skill 在 LLM 代码生成中的价值（EX22/EX10/EX13 的有趣发现作为 hook）
   - Skill 的问题：冗长、格式次优、无法迁移（EX23/EX25 暴露的问题）
   - 引出 Gene 概念和 evomap 平台

2. Background: evomap 与 GEP 协议
   - Gene/Capsule/EvolutionEvent 三元组
   - GEP v1.5.0 Gene 结构
   - Gene 信息梯度 G0-G4

3. Gene-Bench: 实验设计
   - 45 场景 × 12 模型 × 27 实验

4. Results - Part A: Skill 的启示
   - Skill 章节归因（EX22）: 哪个章节最有用？
   - 截断效应（EX23）: 信息冗余度
   - 角色与框架（EX10/EX13）: 表达方式的影响

5. Results - Part B: Gene vs Skill
   - 完整度梯度（EX1）: Gene 以 1/5 token 达到相近效果
   - 正面对决（EX2）: Gene G3 ≈ Skill L1
   - PE方法对比（EX19）: Gene 在 PE 谱系中的位置
   - 生态对比（EX21）: evomap 全套 > 单独任何方法

6. Results - Part C: Gene 的独特能力
   - 鲁棒性（EX3）: 容忍变异
   - 可迁移性（EX4/EX20）: 跨域复用
   - 可进化性（EX18/EX26）: 反馈进化循环
   - 可组合性（EX5）: 多 Gene 合成
   - 可自生成（EX6）: Agent 自主发现

7. Discussion: evomap 生态的意义
   - Gene 作为轻量知识传播单元
   - 自动化 Gene 发现与进化
   - 跨 Agent 的 Gene 共享网络

8. Conclusion
```

---

## 九、当前状态确认

| 项目 | 状态 |
|------|------|
| 45 场景 task.md + test_script.py | ✅ 全部就绪 |
| 45 个 Gene (GEP v1.5.0 格式) | ✅ 已转换 |
| 45 个 SKILL.md | ✅ 全部补齐（含 10 个新建） |
| 45 个 DOMAIN_INFO | ✅ 全部覆盖（含 30 个新增） |
| EX1-EX7 代码 (run_gene_bench.py) | ✅ 已更新（RQ→EX, 45 场景） |
| EX8-EX27 代码 (run_evomap_experiments.py) | ✅ 已实现 |
| validate_setup.py 验证通过 | ✅ 45/45 全通过 |
| 实验数据 | ❌ 需要全部重跑（旧数据仅 15 场景、2 模型） |
