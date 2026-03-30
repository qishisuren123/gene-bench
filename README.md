# Gene-Bench

**当给模型更多信息反而有害时——4,948 次受控实验的发现**

Gene-Bench 是一个系统化的 benchmark，用于测试 LLM 代码生成引导策略的有效性。通过 4,948 次受控实验，我们发现：

- 完整专家文档（600 tok）效果不如 80 tok 的精炼失败经验
- 同一内容换个格式（XML vs Markdown）效果差 10.7pp
- 好东西叠加在一起效果反而更差（组合惩罚高达 84.4%）

## 核心概念

| 概念 | 说明 | ~Tokens |
|------|------|---------|
| **Skill** | 完整专家文档（SKILL.md + api_notes + examples） | ~600 |
| **Gene** | 从 Skill 蒸馏的策略模板（EvoMap GEP v1.5.0） | ~120 |
| **Memory Loop** | 2-4 条失败经验，XML 标签封装 | ~80 |

## 快速开始

### 环境要求

- Python 3.8+
- 依赖：`pip install -r requirements.txt`
- Google Gemini API Key

### 运行实验

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 设置 API Key
export GEMINI_API_KEY=your-api-key-here

# 3. 如果需要代理访问 Google API
export https_proxy=http://your-proxy:port
export http_proxy=http://your-proxy:port

# 4. 运行基准实验（RQ1-7，约 1,318 trials）
python run_gene_bench.py --gemini-key "$GEMINI_API_KEY" --workers 8

# 5. 运行 EvoMap 扩展实验（EX8-11，约 750 trials）
python run_evomap_experiments.py --experiment all --gemini-key "$GEMINI_API_KEY" --workers 8

# 6. Dry-run 查看实验计划（不实际调用 API）
python run_gene_bench.py --dry-run
python run_evomap_experiments.py --experiment all --dry-run
```

### 查看结果

实验结果保存在 `data/` 目录下的 JSONL 文件中：

```bash
# 查看 trial 数量
wc -l data/*.jsonl

# 查看单个 trial 结果
head -1 data/evomap_ex8_results.jsonl | python -m json.tool
```

## 项目结构

```
gene-bench/
├── run_gene_bench.py          # 主实验脚本（RQ1-7）
├── run_evomap_experiments.py   # EvoMap 扩展实验（EX8-11+）
├── gene_builder.py            # Gene 构建与变异逻辑
├── gene_injector.py           # Gene → prompt 注入
├── budget_tracker.py          # API 预算追踪
├── distill_genes.py           # 从 SKILL.md 蒸馏 Gene
├── create_new_genes.py        # 为新场景生成 Gene
├── scenarios/                 # 45 个科学计算场景
│   └── S012_uv_spectroscopy/
│       ├── scenario.yaml      # 场景配置
│       ├── task.md            # 任务描述（user prompt）
│       └── test_script.py     # 评估用单元测试
├── skills/                    # 30 个 Skill 文档包
│   └── S012_uv_spectroscopy/
│       ├── direct/
│       │   ├── SKILL.md       # 主文档
│       │   ├── references/    # api_notes.md, examples.md
│       │   └── scripts/       # 参考实现
│       └── pipeline/          # 管道式变体
├── genes/                     # 45 个 Gene JSON 文件
│   └── S012_uv_spectroscopy.json
├── data/                      # 实验结果（JSONL）
├── analysis/                  # 分析脚本
├── REPORT_V3.md               # 完整技术报告
└── requirements.txt           # Python 依赖
```

## 场景列表（45 个）

覆盖 15 个科学领域：

| 领域 | 场景数 | 示例 |
|------|--------|------|
| 化学/光谱 | 3 | UV-Vis 光谱峰检测、拉曼光谱分析 |
| 天文学 | 3 | 系外行星凌日、CMB 功率谱、小行星轨道 |
| 生物信息学 | 5 | 蛋白质解析、基因本体、系统发育距离 |
| 信号处理 | 3 | 噪声降低、调制分类、回声消除 |
| 气候/海洋 | 4 | 气候归因、CTD 海洋剖面 |
| ... | ... | 共 45 个场景 |

## 评估方法

每个 trial 的流程：

1. 将场景 `task.md` + 引导 prompt 发送给模型
2. 模型生成 Python 代码
3. 在沙盒中执行（超时 120s）
4. 运行预设单元测试（通常 12 个 test case）
5. 全部通过 → PASS，否则 → FAIL

所有实验使用 `temperature=0.0`（确定性输出）。

## 报告

详细实验发现请阅读 [REPORT_V3.md](REPORT_V3.md)。

## 引用

```
@misc{gene-bench-2026,
  title={Gene-Bench: When More Information Hurts — Findings from 4,948 Controlled Experiments},
  author={Gene-Bench Team},
  year={2026},
  url={https://github.com/qishisuren123/gene-bench}
}
```

## 相关链接

- [EvoMap](https://evomap.ai) — Gene/Memory Loop 的知识管理平台
- GEP v1.5.0 — Gene 的结构化协议（详见 `genes/` 目录下的 JSON 文件）
