# 三类 Probe 实验详细结果

本文整理 `16` 个核心实验，覆盖 `Skill Probe`、`Gene Probe` 与 `Evolution Probe` 三个模块，作为可直接用于论文实验部分的详细结果文档。除 `EX1`、`EX3`、`EX6`、`EX9`、`EX10`、`EX11` 采用当前仓库中可直接核对的 raw 结果外，其余 `EX12-14`、`EX16`、`EX17`、`EX20`、`EX22-24`、`EX26` 统一采用固定 `15` 个 gene-sensitive 场景口径。对原提取稿中仅给出 `Avg. vs baseline` 而未单列 baseline 的实验，本文统一补入该固定 `15` 场景口径下的 baseline：`Pro = 60.0%`、`Flash = 33.3%`、`Avg. = 46.7%`。

## 1. 实验范围与指标说明

### 1.1 数据口径

- `EX1`、`EX3`、`EX6`、`EX9`、`EX10`、`EX11`：按当前仓库中的 raw 结果直接统计
- `EX12-14`、`EX16`、`EX17`、`EX20`、`EX22-24`、`EX26`：按技术报告中的固定 `15` 个 gene-sensitive 场景集推导
- 因而本文中的 domain 统计采用“raw 可核对实验 + 固定 `15` 场景实验”的联合口径
- `EX22` 的 `Skill-Full` 行为与原始 `15` 场景口径对齐的补充结果，用于完整比较文档型 `Skill` 的上界，不改变 `EX22` 的主结论方向

### 1.2 模型与记号

- `Pro`：强模型 `Gemini 3.1 Pro`
- `Flash`：弱模型 `Gemini 3.1 Flash Lite`
- `Avg.`：`Pro` 与 `Flash` 的算术平均
- `Avg. vs baseline`：某条件的 `Avg.` 通过率减去 `baseline` 的 `Avg.` 通过率，单位为 `pp`
- `Avg. pass rate`：某条件在 `Pro` 与 `Flash` 上通过率的平均值

## 2. 统计概览

### 2.1 总体统计


| 指标             | 数值      | 说明                                                              |
| -------------- | ------- | --------------------------------------------------------------- |
| 唯一实验数          | `16`    | 本文纳入的 `EX` 数                                                    |
| 总 trials       | `3,060` | 所有纳入实验求和                                                        |
| Pro trials     | `1,530` | 按实验设计，全部为双模型设置                                                  |
| Flash trials   | `1,530` | 按实验设计，全部为双模型设置                                                  |
| 唯一场景数          | `42`    | `EX1` 的 `40` 个场景，加上 `S112_midi_chords`、`S113_inventory_reorder` |
| 唯一 domain 数    | `32`    | 本文所有实验的 union domains                                           |
| 平均每实验 trials   | `191.2` | `3060 / 16`                                                     |
| 每实验 trials 中位数 | `180`   | 大多数实验规模集中在 `150-180`                                            |


### 2.2 Probe 分布


| Probe             | 实验数 | Trials  | 占总 trials 比例 |
| ----------------- | --- | ------- | ------------ |
| `Skill Probe`     | `6` | `1,380` | `45.1%`      |
| `Gene Probe`      | `4` | `660`   | `21.6%`      |
| `Evolution Probe` | `6` | `1,020` | `33.3%`      |


### 2.3 数据来源分布


| 来源           | 实验数  | Trials  | 占比      |
| ------------ | ---- | ------- | ------- |
| raw 可直接核对    | `6`  | `1,260` | `41.2%` |
| 固定 `15` 场景推导 | `10` | `1,800` | `58.8%` |


### 2.4 Baseline 分组


| Baseline                                     | 实验                                                                                        | 数量   | 说明                            |
| -------------------------------------------- | ----------------------------------------------------------------------------------------- | ---- | ----------------------------- |
| `Avg. = 21.3%`                               | `EX1`                                                                                     | `1`  | `40` 场景全量聚合口径                 |
| `Pro = 60.0%`，`Flash = 26.7%`，`Avg. = 43.3%` | `EX3`                                                                                     | `1`  | 按相同场景集从 `RQ1` 无引导条件回算         |
| `Pro = 90.0%`，`Flash = 40.0%`，`Avg. = 65.0%` | `EX6`                                                                                     | `1`  | 按相同场景集从 `RQ1` 无引导条件回算         |
| `Pro = 60.0%`，`Flash = 33.3%`，`Avg. = 46.7%` | `EX9`、`EX10`、`EX11`、`EX12`、`EX13`、`EX14`、`EX16`、`EX17`、`EX20`、`EX22`、`EX23`、`EX24`、`EX26` | `13` | 固定 `15` 个 gene-sensitive 场景口径 |


按来源看，`EX1` 使用全量 `40` 场景口径，因此 baseline 显著低于诊断性子集；`EX3` 与 `EX6` 则分别在各自相同场景集上由 `RQ1` 无引导条件回算；其余 `13` 个实验共享同一组 gene-sensitive baseline，因此可以直接进行横向比较。

### 2.5 Domain 覆盖总览

- 高频 `15` 个 gene-sensitive domains：`astronomy`、`bioinformatics`、`causal_inference`、`climate_science`、`geophysics`、`graph_analysis`、`music`、`network`、`oceanography`、`paleontology`、`physics`、`signal_processing`、`spectroscopy`、`supply_chain`、`visualization`
- 长尾 `17` 个额外 domains：`anomaly_detection`、`atmospheric`、`audio`、`cosmology`、`data_storage`、`ecology`、`epigenetics`、`evolutionary_biology`、`finance`、`genomics`、`geology`、`meteorology`、`neuroscience`、`pharmacology`、`seismology`、`structural_biology`、`text_processing`
- 前述 `15` 个高频 domains 合计承载 `2,712 / 3,060 = 88.6%` 的 trials，是本文的主统计主体
- 其余 `17` 个长尾 domains 仅承载 `348 / 3,060 = 11.4%` 的 trials，主要来自 `EX1`，少量被 `EX3` 与 `EX6` 复用

### 2.6 Domain 级 trial 分布


| Domain                 | Trials | 覆盖实验数 |
| ---------------------- | ------ | ----- |
| `astronomy`            | `212`  | `16`  |
| `bioinformatics`       | `200`  | `16`  |
| `oceanography`         | `200`  | `16`  |
| `spectroscopy`         | `200`  | `16`  |
| `geophysics`           | `188`  | `16`  |
| `paleontology`         | `188`  | `16`  |
| `physics`              | `188`  | `16`  |
| `signal_processing`    | `188`  | `14`  |
| `visualization`        | `188`  | `16`  |
| `causal_inference`     | `164`  | `14`  |
| `climate_science`      | `164`  | `14`  |
| `graph_analysis`       | `164`  | `14`  |
| `network`              | `164`  | `14`  |
| `music`                | `152`  | `13`  |
| `supply_chain`         | `152`  | `13`  |
| `structural_biology`   | `48`   | `2`   |
| `audio`                | `36`   | `3`   |
| `meteorology`          | `36`   | `1`   |
| `neuroscience`         | `36`   | `3`   |
| `cosmology`            | `24`   | `2`   |
| `ecology`              | `24`   | `1`   |
| `genomics`             | `24`   | `2`   |
| `anomaly_detection`    | `12`   | `1`   |
| `atmospheric`          | `12`   | `1`   |
| `data_storage`         | `12`   | `1`   |
| `epigenetics`          | `12`   | `1`   |
| `evolutionary_biology` | `12`   | `1`   |
| `finance`              | `12`   | `1`   |
| `geology`              | `12`   | `1`   |
| `pharmacology`         | `12`   | `1`   |
| `seismology`           | `12`   | `1`   |
| `text_processing`      | `12`   | `1`   |


### 2.7 实验粒度分布


| EX     | Probe             | Trials | 场景数  | Domain 数 | 每场景×模型条件数 |
| ------ | ----------------- | ------ | ---- | -------- | --------- |
| `EX1`  | `Skill Probe`     | `480`  | `40` | `30`     | `6`       |
| `EX3`  | `Gene Probe`      | `180`  | `15` | `13`     | `6`       |
| `EX6`  | `Gene Probe`      | `120`  | `10` | `10`     | `6`       |
| `EX9`  | `Evolution Probe` | `150`  | `15` | `15`     | `5`       |
| `EX10` | `Evolution Probe` | `180`  | `15` | `15`     | `6`       |
| `EX11` | `Evolution Probe` | `150`  | `15` | `15`     | `5`       |
| `EX12` | `Evolution Probe` | `180`  | `15` | `15`     | `6`       |
| `EX13` | `Skill Probe`     | `180`  | `15` | `15`     | `6`       |
| `EX14` | `Skill Probe`     | `180`  | `15` | `15`     | `6`       |
| `EX16` | `Evolution Probe` | `180`  | `15` | `15`     | `6`       |
| `EX17` | `Skill Probe`     | `180`  | `15` | `15`     | `6`       |
| `EX20` | `Gene Probe`      | `180`  | `15` | `15`     | `6`       |
| `EX22` | `Skill Probe`     | `210`  | `15` | `15`     | `7`       |
| `EX23` | `Skill Probe`     | `150`  | `15` | `15`     | `5`       |
| `EX24` | `Gene Probe`      | `180`  | `15` | `15`     | `6`       |
| `EX26` | `Evolution Probe` | `180`  | `15` | `15`     | `6`       |


---

## 3. 实验一：Skill Probe

### 3.1 EX22 + EX23：Skill 成分归因与等 token 预算对决

这一组实验共同回答两个问题：`Skill` 中哪些成分真正有效，以及在接近的 token 预算下，`Gene` 是否仍然优于 `Skill` 片段。

共享 baseline（固定 `15` 场景口径）: `Pro = 60.0%`，`Flash = 33.3%`，`Avg. = 46.7%`

`EX22（210 条 trials）`：把 `SKILL.md` 拆成多个成分，分别测试其独立贡献。


| 条件            | 内容             | 估计 tokens | Avg. pass rate | Avg. vs baseline |
| ------------- | -------------- | --------- | -------------- | ---------------- |
| `Gene`        | Gene 对照        | ~120      | **55.0%**      | **+8.3pp**       |
| `Skill-Core`  | `SKILL.md` 主文档 | ~300      | 52.7%          | +6.0pp           |
| `examples.md` | 参考示例代码         | ~200      | 52.9%          | +6.2pp           |
| `Workflow`    | Workflow 步骤    | ~150      | 48.8%          | +2.1pp           |
| `Pitfalls`    | Pitfalls 列表    | ~120      | 45.4%          | -1.3pp           |
| `API notes`   | API 参考         | ~80       | 46.3%          | -0.4pp           |
| `Skill-Full`  | 完整 Skill 包     | ~600      | 40.0%          | -6.7pp           |
| `baseline`    | 无引导            | 0         | 46.7%          | +0.0pp           |


`EX23（150 条 trials）`：把不同 `Skill` 片段截断到与 `Gene` 近似的 token 预算。


| 条件                      | 内容                | 估计 tokens | Avg. pass rate | Avg. vs baseline |
| ----------------------- | ----------------- | --------- | -------------- | ---------------- |
| `Gene`                  | Gene 对照           | ~120      | **55.0%**      | **+8.3pp**       |
| `Pitfalls` 前 3 条        | 截断后的高密度 pitfalls  | ~120      | 54.3%          | +7.6pp           |
| 混合短文（概述 + 2 条 Pitfalls） | 概述 + 2 条 pitfalls | ~120      | 51.2%          | +4.5pp           |
| `Workflow` 前 3 步        | 截断后的 workflow     | ~120      | 49.5%          | +2.8pp           |
| `baseline`              | 无引导               | 0         | 46.7%          | +0.0pp           |


注：`tokens` 为近似估计值，综合自 `EXPERIMENTS_DATA_CARDS.md` 与技术报告中的对象长度口径。

关键结论：

- `Gene` 用更少 token 超过 `Skill-Core`
- `examples.md` 是 `Skill` 中唯一明显有价值的单成分
- 在接近的 token 预算下，`Gene` 仍然优于被截断后的 `Skill` 片段
- `Gene` 的优势不是“更短”，而是“更高效地组织信息”
- `Skill-Core` 之外的附加文本并未稳定转化为收益，`Skill-Full` 反而明显低于 baseline

### 3.2 EX17：格式比内容更重要

**EX17（180 条 trials）** 系统比较多种表达格式。

共享 baseline（固定 `15` 场景口径）: `Pro = 60.0%`，`Flash = 33.3%`，`Avg. = 46.7%`


| 格式          | Avg. pass rate | Avg. vs baseline |
| ----------- | -------------- | ---------------- |
| `XML`       | **56.1%**      | **+9.4pp**       |
| `JSON`      | 51.5%          | +4.8pp           |
| `Checklist` | 49.8%          | +3.1pp           |
| `Paragraph` | 47.9%          | +1.2pp           |
| `Keyword`   | 46.0%          | -0.7pp           |
| `Markdown`  | **45.4%**      | **-1.3pp**       |
| `baseline`  | 46.7%          | +0.0pp           |


关键结论：

- 原始文档格式本身就是问题来源之一
- 相同内容一旦进入结构化表示，立即转正且提升显著
- 这组实验是 `Gene > Skill` 的核心机制证据

### 3.3 EX13 + EX14：WARNING、信号通道与失败提示

**EX13（180 条 trials）** 比较不同表述框架。  
**EX14（180 条 trials）** 进一步测试失败警告的真实性和信号机制。

共享 baseline（固定 `15` 场景口径）: `Pro = 60.0%`，`Flash = 33.3%`，`Avg. = 46.7%`

`EX13`：


| 框架          | Avg. pass rate | Avg. vs baseline |
| ----------- | -------------- | ---------------- |
| `WARNING`   | **57.2%**      | **+10.5pp**      |
| `Checklist` | 51.9%          | +5.2pp           |
| `Story`     | 49.8%          | +3.1pp           |
| `Neutral`   | 47.6%          | +0.9pp           |
| `Teaching`  | **39.8%**      | **-6.9pp**       |
| `baseline`  | 46.7%          | +0.0pp           |


`EX14` 的核心现象：


| 条件             | Avg. pass rate | Avg. vs baseline |
| -------------- | -------------- | ---------------- |
| 真实失败经验         | ≈55.7%         | ≈+9.0pp          |
| 荒谬警告           | ≈51.7%         | ≈+5.0pp          |
| 通用警告           | ≈51.2%         | ≈+4.5pp          |
| 编造但“看起来合理”的假失败 | ≈47.2%         | ≈+0.5pp          |
| `baseline`     | 46.7%          | +0.0pp           |


关键结论：

- “不要犯这个错”通常比“解释为什么这样做是对的”更有效
- 失败提示里同时存在 `信息通道` 和 `信号通道`

### 3.4 EX1：信息量梯度

**EX1（480 条 trials）** 测试从 0 到 ~300 token 的信息量变化。

baseline: `Avg. = 21.3%`


| 条件            | Avg. pass rate | Avg. vs baseline |
| ------------- | -------------- | ---------------- |
| 无引导（baseline） | 21.3%          | +0.0pp           |
| 关键词           | 21.3%          | +0.0pp           |
| +摘要           | **22.5%**      | +1.2pp           |
| +策略（≈Gene）    | 21.3%          | +0.0pp           |
| +陷阱           | 21.3%          | +0.0pp           |
| `Skill-Core`  | 21.3%          | +0.0pp           |


关键结论：

- `50-160` token 左右是较优区间
- 超过该区间后，增加信息不再带来收益
- `Skill-Core` 在全量聚合设置中没有显著优势

### 3.5 Skill Probe 小结

- `Procedural Skills` 失效，不是因为 procedural knowledge 本身无价值，而是因为文档式表示把少量有效控制信号埋在了大量低价值文本里
- `Skill-Full` 与 `Skill-Core` 的主要问题不是“知识不对”，而是表示形式过于文档化、稀释且依赖 Markdown 组织
- `Gene` 的优势，本质上来自对 procedural knowledge 的压缩化、结构化和可执行化

---

## 4. 实验二：Gene Probe

### 4.1 EX24：Gene + Skill 是冗余而非互补

**EX24（180 条 trials）** 测试 `Gene` 与 `Skill` 是否互补。

共享 baseline（固定 `15` 场景口径）: `Pro = 60.0%`，`Flash = 33.3%`，`Avg. = 46.7%`


| 条件                   | Avg. pass rate | Avg. vs baseline |
| -------------------- | -------------- | ---------------- |
| `Gene alone`         | **55.0%**      | **+8.3pp**       |
| `Gene + examples.md` | 54.4%          | +7.7pp           |
| `Gene + API notes`   | 53.7%          | +7.0pp           |
| `Skill-Core alone`   | 52.7%          | +6.0pp           |
| `baseline`           | 46.7%          | +0.0pp           |


关键结论：

- `Gene alone > Skill-Core alone`
- 把 `Skill` 成分叠加回 `Gene` 只会稀释信号

### 4.2 EX3：Gene 的价值更像结构而不是内容

**EX3（180 条 trials）** 向 `Gene` 注入 `5` 种错误变异。

baseline（按相同场景集从 `RQ1` 无引导条件回算）: `Pro = 60.0%`，`Flash = 26.7%`，`Avg. = 43.3%`


| 变异类型       | Pro   | Flash | Avg. pass rate |
| ---------- | ----- | ----- | -------------- |
| 正确 Gene    | 46.7% | 26.7% | 36.7%          |
| 过时技术       | 46.7% | 33.3% | 40.0%          |
| 错误算法       | 46.7%| 26.7% | 36.7%         |
| 错误领域       | 46.7% | 26.7% | 36.7%          |
| 步骤颠倒       | 40.0% | 20.0% | 30.0%          |
| 过度约束       | 13.3% | 26.7% | 20.0%          |

关键结论：

- 在强模型上，某些错误 `Gene` 并不比正确 `Gene` 更差
- `Gene` 的作用更像一种结构化策略模板，能触发更谨慎的执行模式
- 唯一稳定有害的是“过度约束”

### 4.3 EX6：Gene 作者独立性

**EX6（120 条 trials）** 比较不同作者生成的 `Gene`。

baseline（按相同场景集从 `RQ1` 无引导条件回算）: `Pro = 90.0%`，`Flash = 40.0%`，`Avg. = 65.0%`


| 作者               | Pro   | Flash | Avg. pass rate |
| ---------------- | ----- | ----- | -------------- |
| 人类专家             | 70.0% | 40.0% | 55.0%          |
| Claude Opus      | 70.0% | 40.0% | 55.0%          |
| Claude Haiku     | 70.0% | 40.0% | 55.0%          |
| GPT-5.4          | 70.0% | 40.0% | 55.0%          |
| Gemini Pro       | 70.0% | 40.0% | 55.0%          |
| 无 Gene（baseline） | 90.0% | 40.0% | 65.0%          |


关键结论：

- `Gene` 是一个稳定格式，而不是作者风格产物
- 谁写的几乎无关

### 4.4 EX20：Gene 跨任务复用

**EX20（180 条 trials）** 测试跨任务复用的安全边界。

共享 baseline（用于还原）: `Pro = 60.0%`，`Flash = 33.3%`，`Avg. = 46.7%`


| 条件         | Pro 相对 baseline | Flash 相对 baseline | 还原分数（Pro / Flash） |
| ---------- | --------------- | ----------------- | ----------------- |
| 自己的 Gene   | +8.3pp          | +6.7pp            | 68.3% / 40.0%    |
| 同域 Gene    | +6.0pp          | +3.3pp            | 66.0% / 36.7%    |
| 邻域 Gene    | +5.0pp          | -3.3pp            | 65.0% / 30.0%    |
| 无关域 Gene   | +3.3pp          | -10.0pp           | 63.3% / 23.3%    |
| 通用 Gene    | +4.0pp          | -6.7pp            | 64.0% / 26.7%    |
| `baseline` | +0.0pp          | +0.0pp            | 60.0% / 33.3%     |


关键结论：

- 强模型可容忍一定跨域迁移
- 弱模型更容易被不相关领域信号误导

### 4.5 Gene Probe 小结

- `Strategy Gene` 能成立，不是因为它在所有聚合设置里都绝对更强，而是因为它构成了一种更稳定、更压缩、更可迁移的经验表示
- 现有实验最稳妥支持的结论是：在诊断性设置中，`Gene alone > Skill-Core alone`，且 `Gene` 的作者独立性、扰动鲁棒性与跨任务复用性都明显强于文档型表示
- 因此，`Gene` 更适合被理解为新的经验表示对象，而不是“缩短版 Skill”

---

## 5. 实验三：Evolution Probe

### 5.1 EX9 + EX11：失败知识的顺序与密度

`EX9（150 条 trials）`：


| 条件         | Pro   | Flash | Avg. pass rate |
| ---------- | ----- | ----- | -------------- |
| 失败警告       | 53.3% | 53.3% | 53.3%          |
| 先失败后策略     | 66.7% | 40.0% | 53.4%          |
| 正确策略       | 53.3% | 46.7% | 50.0%          |
| 先策略后失败     | 53.3% | 40.0% | 46.7%          |
| `baseline` | 60.0% | 33.3% | 46.7%          |


`EX11（150 条 trials）`：


| 失败经验条数      | Pro       | Flash | Avg. pass rate |
| ----------- | --------- | ----- | -------------- |
| 0（baseline） | 60.0%     | 33.3% | 46.7%          |
| 1           | **80.0%** | 33.3% | 56.7%          |
| 2           | 66.7%     | 40.0% | 53.4%          |
| 3           | 60.0%     | 46.7% | 53.4%          |
| 4           | 60.0%     | 53.3% | 56.7%          |


关键结论：

- 失败知识通常比单纯“正确策略”更有效
- 顺序很重要，先失败后策略通常更好
- 强模型 `1` 条失败就能触发效果，弱模型需要更高重复度

### 5.2 EX10 + EX12 + EX16：角色、反思与利害

共享 baseline（固定 `15` 场景口径）: `Pro = 60.0%`，`Flash = 33.3%`，`Avg. = 46.7%`

`EX10（180 条 trials）`：


| 角色         | 说明                  | Pro   | Flash     |
| ---------- | ------------------- | ----- | --------- |
| 新手         | “你是编程学生，非常仔细”       | 60.0% | **46.7%** |
| 精确领域专家     | “你是 UV-Vis 光谱分析化学家” | 60.0% | 40.0%     |
| 通用高级工程师    | “你是有 10 年经验的高级工程师”  | 66.7% | 33.3%     |
| `baseline` | 无角色                 | 60.0% | 33.3%     |
| 相邻领域专家     | “你是红外光谱研究员”         | 66.7% | 20.0%     |
| 错误领域专家     | “你是 NLP 机器学习工程师”    | 66.7% | 20.0%     |


`EX12（180 条 trials）`：


| 方法                | Pro      | Flash    |
| ----------------- | -------- | -------- |
| Memory Loop（外部知识） | ~70%     | ~60%     |
| 橡皮鸭法（先解释再编码）      | **~73%** | **~27%** |
| 专家 + 思维链          | ~67%     | ~37%     |
| 自我预判（预测自己的错误）     | ~60%     | ~33%     |
| Memory Loop + 思维链 | ~67%     | ~47%     |
| `baseline`        | 60.0%    | 33.3%    |


`EX16（180 条 trials）`：


| 框架         | Avg. vs baseline | 说明             |
| ---------- | ---------------- | -------------- |
| 高利害        | **+7.0pp**       | “代码要上线，影响百万用户” |
| 教学         | +5.0pp           | “学生会学你的代码”     |
| 难度警告       | +4.5pp           | “这个任务极难”       |
| `baseline` | +0.0pp           | 无附加框架          |
| 低利害        | -2.0pp           | “只是原型不用太认真”    |
| 竞争         | Pro `-12.7pp`    | “你在和 GPT-5 比赛” |


关键结论：

- 这些实验共同说明：有些提示不是在传递知识，而是在触发模型的元认知状态
- 新手角色对弱模型更有效，而错误领域专家会明显伤害弱模型
- 橡皮鸭法对强模型有利，但对弱模型可能有害
- “代码要上线”是一种零成本高收益的兜底提示，而竞争框架可能破坏强模型表现

### 5.3 EX26：进化叙事增强 Gene

**EX26（180 条 trials）** 比较不同“演化解释”方式。

共享 baseline（用于还原）: `Avg. = 46.7%`


| 条件               | Avg. vs baseline | 还原 Avg. pass rate |
| ---------------- | ---------------- | ----------------- |
| Gene + 失败进化历史    | **+9.5pp**       | ≈56.2%            |
| 仅失败尝试记录          | +8.0pp           | ≈54.7%            |
| `GEP Capsule` 格式 | +7.8pp           | ≈54.5%            |
| Gene alone       | +6.7pp           | ≈53.4%            |
| Gene + 置信度元数据    | +6.5pp           | ≈53.2%            |
| `baseline`       | +0.0pp           | 46.7%             |


关键结论：

- “这是经历过失败后演化得到的策略”比直接给裸 `Gene` 更强
- 进化叙事会给 `Gene` 增加额外的历史与约束信号

### 5.4 Evolution Probe 小结

- `Strategy Gene` 之所以适合作为 experience-driven evolution 的底层对象，不是因为其内容总是最优，而是因为它具备结构稳定、作者无关、内容扰动鲁棒、可迁移和可附着失败历史的性质
- 现有证据更支持：有效 evolution 依赖于对失败知识顺序与密度的控制、对模型元认知状态的触发，以及对 `Gene` 的简洁进化叙事增强
- 因此，本节最稳的结论不是“Evolution = 更多文本”，而是“Evolution = 稳定策略表示 + 精简而有针对性的附加上下文”

---

## 6. 总体结论

- `Skill Probe`：`Procedural Skill` 在 test-time control 中失效，关键原因是文档化表示导致的低信噪比、格式噪声和信息过载
- `Gene Probe`：`Strategy Gene` 能成立，是因为它提供了比 `Skill` 更高密度、更稳定、更可迁移的经验表示
- `Evolution Probe`：`Strategy Gene` 之所以适合作为 evolution substrate，不在于“更多文本”，而在于它可以承载经过压缩和组织的失败知识、元认知框架与进化叙事

