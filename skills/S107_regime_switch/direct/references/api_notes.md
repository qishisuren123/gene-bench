# Log returns
- r_t = log(P_t / P_{t-1}) = log(P_t) - log(P_{t-1})
- Use np.log(prices[1:] / prices[:-1]) or np.diff(np.log(prices))
- Approximately equal to simple returns for small values

# Rolling statistics
- Rolling mean: pd.Series.rolling(window).mean()
- Rolling std (volatility): pd.Series.rolling(window).std()
- Typical windows: 20 (monthly), 60 (quarterly), 252 (annual)
- Annualized volatility: rolling_std * sqrt(252)

# Change point detection
- CUSUM: cumulative sum of deviations from target mean
  S_t = max(0, S_{t-1} + (x_t - mu) - k), trigger when S_t > h
- Variance-based: detect shifts in rolling variance
- Simple approach: compare adjacent window statistics with t-test

# Regime classification
- Low volatility: annualized vol < threshold_1 (e.g., 15%)
- Medium volatility: threshold_1 <= vol < threshold_2 (e.g., 25%)
- High volatility / crisis: vol >= threshold_2
- Use quantiles of historical volatility to set thresholds dynamically

# numpy.diff
np.diff(a, n=1)
- First-order difference: a[1:] - a[:-1]
- For log returns: np.diff(np.log(prices))
