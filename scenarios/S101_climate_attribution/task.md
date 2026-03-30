Write a Python CLI script that performs climate change attribution analysis on temperature time series data.

Input: A CSV file with columns: year, observed_temp_anomaly, solar_forcing, volcanic_forcing, ghg_forcing, aerosol_forcing, natural_variability.

Requirements:
1. Use argparse: --input for CSV file, --output for JSON results, --method (choices: "ols", "ridge", "bayesian"; default "ridge")
2. Load and validate the CSV data (check for required columns, handle missing values)
3. Perform attribution analysis: regress observed temperature anomaly against individual forcing factors
4. For OLS: use ordinary least squares via numpy.linalg.lstsq
5. For Ridge: use L2-regularized regression with alpha=1.0
6. For Bayesian: use simple analytical Bayesian linear regression with prior precision=0.1
7. Compute attribution fractions: each forcing's contribution as percentage of total explained warming
8. Compute residual (unexplained) fraction
9. Output JSON with: method, coefficients (dict), attribution_fractions (dict), r_squared, residual_fraction
10. Print summary: dominant forcing factor and its attribution percentage
