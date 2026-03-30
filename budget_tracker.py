#!/usr/bin/env python3
"""
预算追踪模块：实时成本估算和预警。

支持 yunwu.ai 代理（Claude/GPT/Qwen/DeepSeek）和 Gemini 直连两种计费方式。
"""

import json
import time
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional

# ── 模型价格表 ──
# yunwu.ai 单价已乘以 0.6 折扣，单位：$/1M tokens
# 格式：(input_price, output_price) per 1M tokens
MODEL_PRICING = {
    # Claude 系列（yunwu.ai × 0.6）
    "claude-opus-4-6":              (9.0,  45.0),     # 原价 15+75 → ×0.6
    "claude-sonnet-4-6":            (1.8,  5.4),      # 原价 3+9 → ×0.6 (已废弃实际约 0.9/call)
    "claude-haiku-4-5":             (0.48, 1.5),      # 原价 0.8+2.5 → ×0.6

    # GPT 系列（yunwu.ai × 0.6）
    "gpt-5.4":                      (1.5,  6.0),      # 估算
    "gpt-5-mini":                   (0.15, 0.6),
    "gpt-5-nano":                   (0.03, 0.12),

    # Gemini 系列（直连免费）
    "gemini-3-pro":                 (0.0,  0.0),
    "gemini-2.5-flash":             (0.0,  0.0),

    # Qwen 系列（yunwu.ai × 0.6）
    "qwen3.5-397b-a17b":           (0.72, 2.16),
    "qwen3-coder":                  (3.6,  10.8),

    # DeepSeek 系列（yunwu.ai × 0.6）
    "deepseek-v3.2-exp":            (0.6,  1.2),     # 估算
    "deepseek-r1":                  (1.2,  3.6),
}

# 模型分层（用于预算控制）
MODEL_TIERS = {
    "free":     ["gemini-3-pro", "gemini-2.5-flash"],
    "cheap":    ["gpt-5-nano", "gpt-5-mini", "claude-haiku-4-5"],
    "medium":   ["claude-sonnet-4-6", "gpt-5.4", "qwen3.5-397b-a17b", "deepseek-v3.2-exp"],
    "expensive":["claude-opus-4-6", "qwen3-coder", "deepseek-r1"],
}


@dataclass
class TrialCost:
    """单次 trial 的成本记录"""
    model: str
    input_tokens: int
    output_tokens: int
    cost: float
    rq: str
    scenario: str
    timestamp: float = field(default_factory=time.time)


class BudgetTracker:
    """
    预算追踪器。

    用法:
        tracker = BudgetTracker(budget=500.0)
        tracker.record("claude-opus-4-6", 500, 3000, rq="rq2", scenario="S002")
        tracker.report()
    """

    def __init__(self, budget: float = 500.0, log_path: Optional[Path] = None):
        self.budget = budget
        self.log_path = log_path or Path("data/budget_log.jsonl")
        self.trials: list[TrialCost] = []
        self._load_existing()

    def _load_existing(self):
        """从已有日志恢复"""
        if self.log_path.exists():
            for line in self.log_path.read_text().strip().split("\n"):
                if line:
                    try:
                        d = json.loads(line)
                        self.trials.append(TrialCost(**d))
                    except (json.JSONDecodeError, TypeError):
                        pass

    def estimate_cost(self, model: str, input_tokens: int, output_tokens: int) -> float:
        """估算单次调用成本"""
        pricing = MODEL_PRICING.get(model, (1.0, 3.0))  # 默认中等价格
        input_cost = (input_tokens / 1_000_000) * pricing[0]
        output_cost = (output_tokens / 1_000_000) * pricing[1]
        return input_cost + output_cost

    def record(self, model: str, input_tokens: int, output_tokens: int,
               rq: str = "", scenario: str = "") -> float:
        """记录一次调用的成本"""
        cost = self.estimate_cost(model, input_tokens, output_tokens)
        trial = TrialCost(
            model=model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost=cost,
            rq=rq,
            scenario=scenario,
        )
        self.trials.append(trial)

        # 追加到日志
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.log_path, "a") as f:
            f.write(json.dumps({
                "model": model,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "cost": cost,
                "rq": rq,
                "scenario": scenario,
                "timestamp": trial.timestamp,
            }) + "\n")

        return cost

    @property
    def total_spent(self) -> float:
        return sum(t.cost for t in self.trials)

    @property
    def remaining(self) -> float:
        return self.budget - self.total_spent

    @property
    def n_trials(self) -> int:
        return len(self.trials)

    def by_rq(self) -> dict[str, float]:
        """按 RQ 汇总成本"""
        costs = {}
        for t in self.trials:
            costs[t.rq] = costs.get(t.rq, 0) + t.cost
        return costs

    def by_model(self) -> dict[str, float]:
        """按模型汇总成本"""
        costs = {}
        for t in self.trials:
            costs[t.model] = costs.get(t.model, 0) + t.cost
        return costs

    def by_tier(self) -> dict[str, float]:
        """按模型层级汇总成本"""
        tier_map = {}
        for tier, models in MODEL_TIERS.items():
            for m in models:
                tier_map[m] = tier

        costs = {}
        for t in self.trials:
            tier = tier_map.get(t.model, "unknown")
            costs[tier] = costs.get(tier, 0) + t.cost
        return costs

    def check_budget(self, warn_threshold: float = 0.8) -> tuple[bool, str]:
        """
        检查预算状态。

        Returns:
            (is_ok, message)
            is_ok=False 表示已超预算
        """
        spent = self.total_spent
        ratio = spent / self.budget if self.budget > 0 else 1.0

        if ratio >= 1.0:
            return False, f"BUDGET EXCEEDED: ${spent:.2f} / ${self.budget:.2f} ({ratio:.0%})"
        elif ratio >= warn_threshold:
            return True, f"WARNING: ${spent:.2f} / ${self.budget:.2f} ({ratio:.0%}) - approaching limit"
        else:
            return True, f"OK: ${spent:.2f} / ${self.budget:.2f} ({ratio:.0%})"

    def report(self) -> str:
        """生成预算报告"""
        lines = [
            "=" * 50,
            "  Gene-Bench Budget Report",
            "=" * 50,
            f"  Total trials:  {self.n_trials}",
            f"  Total spent:   ${self.total_spent:.2f}",
            f"  Budget:        ${self.budget:.2f}",
            f"  Remaining:     ${self.remaining:.2f}",
            "",
            "  By RQ:",
        ]
        for rq, cost in sorted(self.by_rq().items()):
            n = sum(1 for t in self.trials if t.rq == rq)
            lines.append(f"    {rq:10s}  {n:5d} trials  ${cost:8.2f}")

        lines.append("")
        lines.append("  By Model:")
        for model, cost in sorted(self.by_model().items(), key=lambda x: -x[1]):
            n = sum(1 for t in self.trials if t.model == model)
            lines.append(f"    {model:30s}  {n:5d} trials  ${cost:8.2f}")

        lines.append("")
        lines.append("  By Tier:")
        for tier, cost in sorted(self.by_tier().items()):
            lines.append(f"    {tier:12s}  ${cost:8.2f}")

        ok, status = self.check_budget()
        lines.append("")
        lines.append(f"  Status: {status}")
        lines.append("=" * 50)

        return "\n".join(lines)

    def estimate_remaining_cost(self, n_trials: int, avg_model: str = "claude-sonnet-4-6",
                                 avg_input: int = 800, avg_output: int = 4000) -> float:
        """估算剩余实验成本"""
        per_trial = self.estimate_cost(avg_model, avg_input, avg_output)
        return n_trials * per_trial


def get_model_tier(model: str) -> str:
    """获取模型的价格层级"""
    for tier, models in MODEL_TIERS.items():
        if model in models:
            return tier
    return "unknown"
