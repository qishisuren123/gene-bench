Write a Python CLI script that detects regime switches (structural breaks) in financial time series data.

Input: A CSV file with columns: date, price, volume (daily financial data).

Requirements:
1. Use argparse: --input CSV, --output JSON, --min-regime-length (default 20 days), --n-regimes (default 0 for auto-detect)
2. Compute log returns from price series
3. Implement regime detection using rolling statistics:
   - Compute rolling mean and volatility (std) of returns with window = min_regime_length
   - Detect change points where rolling volatility changes by >2x between adjacent windows
4. Classify regimes: "low_vol" (volatility < median), "high_vol" (volatility > median), "crisis" (volatility > 2x median)
5. For each regime: compute start_date, end_date, duration_days, mean_return, volatility, sharpe_ratio (annualized)
6. Compute transition matrix: probability of switching between regime types
7. Output JSON: n_regimes, regimes (list), transition_matrix, overall_stats
8. Print summary: number of regimes, longest regime, current regime type
