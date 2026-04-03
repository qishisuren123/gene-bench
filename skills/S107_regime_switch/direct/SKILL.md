# Financial Regime Switch Detection

## Overview
This skill detects volatility regime switches (structural breaks) in financial time series by computing rolling statistics on log returns and classifying periods into low-volatility, high-volatility, and crisis regimes.

## Workflow
1. Parse command-line arguments for input CSV, output JSON, window-size (default 60), and min-regime-length (default 20)
2. Load CSV with date, price, volume columns; compute log returns as log(P_t / P_{t-1})
3. Calculate rolling mean return and rolling volatility (std of log returns) with specified window size
4. Detect change points: timestamps where rolling volatility changes by more than 2× between adjacent non-overlapping windows
5. Segment time series at change points into regimes; merge short regimes below min-regime-length with neighbors
6. Classify each regime: low_vol (volatility < median), high_vol (> median), crisis (> 2× median overall volatility)
7. Compute per-regime statistics: start_date, end_date, duration_days, mean_return, volatility, sharpe_ratio
8. Build transition matrix counting regime-to-regime transitions; output JSON with regimes, transitions, and overall stats

## Common Pitfalls
- **Log returns, not simple returns**: Use log(P_t/P_{t-1}), not (P_t - P_{t-1})/P_{t-1}; log returns have better statistical properties for volatility estimation
- **Rolling window warmup**: First `window_size` observations produce NaN — start regime detection only after full window is available
- **Annualization**: Sharpe ratio = (mean_daily_return × 252) / (daily_volatility × √252); using wrong scaling gives meaningless ratios
- **Short regime merging**: Regimes shorter than min-regime-length should be merged with the preceding regime, not discarded
- **Zero-volume days**: Skip or forward-fill days with zero volume to avoid log(0) errors

## Error Handling
- Validate that price column has no zero or negative values before computing log returns
- Handle missing dates by forward-filling or marking gaps
- Check that window_size is less than total number of data points

## Quick Reference
- Log returns: `np.log(prices[1:] / prices[:-1])`
- Rolling volatility: `pd.Series(returns).rolling(window).std()`
- Sharpe ratio: `(mean_return * 252) / (volatility * np.sqrt(252))`
- Change point: `abs(vol[t] - vol[t-window]) / vol[t-window] > 1.0` (2× change)
- Transition matrix: count occurrences of regime_i → regime_j transitions
