# Example 1: Basic 2SLS without confounders
import numpy as np
import pandas as pd

df = pd.read_csv('iv_data.csv')
Y = df['outcome'].values
X = df['treatment'].values
Z = df['instrument'].values
n = len(Y)

# Stage 1: regress X on Z
Z_mat = np.column_stack([np.ones(n), Z])
beta1 = np.linalg.lstsq(Z_mat, X, rcond=None)[0]
X_hat = Z_mat @ beta1

# First-stage F-statistic
ss_res1 = np.sum((X - X_hat)**2)
ss_tot1 = np.sum((X - X.mean())**2)
r2_first = 1 - ss_res1 / ss_tot1
f_stat = (r2_first / 1) / ((1 - r2_first) / (n - 2))
print(f"First-stage F = {f_stat:.1f}, Weak instrument: {f_stat < 10}")

# Stage 2: regress Y on X_hat
X2 = np.column_stack([np.ones(n), X_hat])
beta_iv = np.linalg.lstsq(X2, Y, rcond=None)[0]

# Correct SE using original X
residuals = Y - np.column_stack([np.ones(n), X]) @ beta_iv
sigma2 = np.sum(residuals**2) / (n - 2)
cov = sigma2 * np.linalg.inv(X2.T @ X2)
se_iv = np.sqrt(np.diag(cov))

print(f"IV estimate: {beta_iv[1]:.4f} (SE: {se_iv[1]:.4f})")

# OLS for comparison
X_ols = np.column_stack([np.ones(n), X])
beta_ols = np.linalg.lstsq(X_ols, Y, rcond=None)[0]
print(f"OLS estimate: {beta_ols[1]:.4f}")
