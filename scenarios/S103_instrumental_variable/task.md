Write a Python CLI script that performs instrumental variable (IV) regression to estimate causal effects.

Input: A CSV file with columns: outcome (Y), treatment (X), instrument (Z), and optional confounders (C1, C2, ...).

Requirements:
1. Use argparse: --input CSV, --output JSON, --outcome (column name), --treatment (column name), --instrument (column name), --confounders (optional comma-separated)
2. Load CSV and validate columns exist
3. Implement two-stage least squares (2SLS):
   - Stage 1: Regress X on Z (and confounders if provided) → get predicted X_hat
   - Stage 2: Regress Y on X_hat (and confounders) → get IV estimate
4. Also compute naive OLS estimate of Y on X for comparison
5. Compute standard errors for both estimates using appropriate formulas
6. Compute first-stage F-statistic (instrument relevance test, weak instrument if F < 10)
7. Output JSON with: iv_estimate, iv_std_error, ols_estimate, ols_std_error, first_stage_f, weak_instrument (bool), n_observations
8. Print summary comparing IV and OLS estimates
