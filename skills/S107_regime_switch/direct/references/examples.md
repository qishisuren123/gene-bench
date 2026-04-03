# Example 1: Compute log returns and rolling volatility
import numpy as np
import pandas as pd

np.random.seed(42)
# Simulate price series with regime change
returns_low = np.random.normal(0.0005, 0.01, 200)
returns_high = np.random.normal(-0.001, 0.035, 100)
returns_low2 = np.random.normal(0.0003, 0.012, 200)
all_returns = np.concatenate([returns_low, returns_high, returns_low2])
prices = 100 * np.exp(np.cumsum(all_returns))

log_ret = np.diff(np.log(prices))
sr = pd.Series(log_ret)
rolling_vol = sr.rolling(20).std() * np.sqrt(252)
print(f"Mean annualized vol: {rolling_vol.mean():.3f}")

# Example 2: Regime classification by volatility thresholds
def classify_regimes(vol_series, low_q=0.33, high_q=0.67):
    """Classify into low/medium/high volatility regimes."""
    thresh_low = vol_series.quantile(low_q)
    thresh_high = vol_series.quantile(high_q)
    regimes = pd.Series('medium', index=vol_series.index)
    regimes[vol_series < thresh_low] = 'low'
    regimes[vol_series > thresh_high] = 'high'
    return regimes

regimes = classify_regimes(rolling_vol.dropna())
print(regimes.value_counts())

# Example 3: Simple change point via variance ratio
def detect_change_points(returns, window=30, threshold=2.0):
    """Detect points where variance shifts significantly."""
    changes = []
    for i in range(window, len(returns) - window):
        var_before = np.var(returns[i-window:i])
        var_after = np.var(returns[i:i+window])
        ratio = max(var_after, 1e-10) / max(var_before, 1e-10)
        if ratio > threshold or ratio < 1.0 / threshold:
            changes.append(i)
    return changes

cps = detect_change_points(log_ret, window=30, threshold=3.0)
print(f"Change points detected at indices: {cps[:5]}")
