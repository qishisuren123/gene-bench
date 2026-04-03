# Climate Change Attribution Analysis

## Overview
This skill enables detection and attribution of climate change by regressing observed temperature anomalies against individual forcing factors (GHG, solar, volcanic, aerosol) to quantify each factor's contribution percentage.

## Workflow
1. Parse command-line arguments for input CSV, output JSON, and regression method (OLS, Ridge, Bayesian)
2. Load CSV with year, observed temperature anomaly, and forcing factor columns; validate required columns and handle NaN
3. Set up design matrix X from forcing columns and response vector y from observed anomaly
4. Fit regression: OLS via numpy.linalg.lstsq, Ridge via closed-form (X'X + αI)^{-1}X'y, Bayesian via analytical posterior mean
5. Compute attribution fractions: for each forcing factor, its contribution = |coef_i * mean(X_i)| / sum(|coef_j * mean(X_j)|)
6. Calculate R² = 1 - SS_res/SS_tot and residual fraction = 1 - sum(attribution_fractions)
7. Output JSON results with coefficients, attribution fractions, R², and residual fraction; print dominant forcing

## Common Pitfalls
- **Multicollinearity**: Forcing factors (especially GHG and aerosol) are often highly correlated, making OLS coefficients unstable — use Ridge or Bayesian to regularize
- **Attribution fraction calculation**: Must use absolute coefficient contributions (|coef * mean_forcing|), not raw coefficients, to get meaningful percentages
- **Missing intercept**: Always include an intercept term in the regression or center the data first; omitting it biases all coefficient estimates
- **Normalization**: If forcing factors have different scales, coefficients are not directly comparable — normalize or use standardized coefficients for attribution
- **Residual fraction**: Compute as 1 minus the sum of positive attribution fractions; can be negative if model overfits

## Error Handling
- Validate that all required CSV columns exist before processing
- Handle missing values by dropping rows with NaN in any forcing or response column
- Check for singular matrix in OLS (use lstsq which handles rank-deficient matrices)
- Ensure Ridge alpha > 0 to guarantee invertibility

## Quick Reference
- OLS: `np.linalg.lstsq(X, y, rcond=None)[0]`
- Ridge: `np.linalg.solve(X.T @ X + alpha * np.eye(p), X.T @ y)`
- Bayesian: posterior mean = `(X.T @ X + prior_precision * np.eye(p))^{-1} @ X.T @ y`
- R²: `1 - np.sum((y - X @ coef)**2) / np.sum((y - y.mean())**2)`
