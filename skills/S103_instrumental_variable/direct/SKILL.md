# Instrumental Variable Regression (2SLS)

## Overview
This skill enables causal effect estimation using two-stage least squares (2SLS) to overcome endogeneity bias in observational data where treatment is correlated with unobserved confounders.

## Workflow
1. Parse arguments for input CSV, output JSON, column names for outcome (Y), treatment (X), instrument (Z), and optional confounders
2. Load CSV and validate that specified columns exist; handle missing values
3. Stage 1: Regress treatment X on instrument Z (and confounders C) using OLS → obtain predicted treatment X_hat
4. Compute first-stage F-statistic on the instrument coefficient to test instrument relevance
5. Stage 2: Regress outcome Y on X_hat (and confounders C) → the coefficient on X_hat is the IV estimate of causal effect
6. Compute correct standard errors using original X (not X_hat) in the residual calculation
7. Also compute naive OLS estimate of Y on X for comparison
8. Output JSON with IV estimate, OLS estimate, standard errors, F-statistic, weak instrument flag

## Common Pitfalls
- **Standard error correction**: Stage 2 residuals must be computed using original X, not predicted X_hat — using X_hat underestimates standard errors
- **Weak instruments**: F-statistic < 10 on the first-stage instrument coefficient indicates weak instruments, making IV more biased than OLS
- **Exclusion restriction**: Cannot be tested statistically — must argue theoretically that Z affects Y only through X
- **Confounders in both stages**: If including confounders, they must appear in BOTH Stage 1 and Stage 2 regressions
- **Overidentification**: With more instruments than endogenous variables, use Sargan test for instrument validity

## Error Handling
- Validate column existence and data types before regression
- Check for perfect collinearity between instrument and confounders
- Handle case where first-stage F is near zero (instrument has no predictive power)
- Report warning when weak_instrument flag is True

## Quick Reference
- Stage 1: `X_hat = Z @ np.linalg.lstsq(Z, X, rcond=None)[0]` where Z includes confounders
- Stage 2: `coef_iv = np.linalg.lstsq(np.column_stack([X_hat, C]), Y, rcond=None)[0]`
- Correct SE: Use residuals from `Y - [X, C] @ coef_iv` (original X, not X_hat)
- F-stat: `(R²_first / k) / ((1 - R²_first) / (n - k - 1))` on instrument coefficient
