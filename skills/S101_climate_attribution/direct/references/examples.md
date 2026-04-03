# Example 1: Basic Ridge attribution
import numpy as np
import pandas as pd

df = pd.read_csv('climate_data.csv')
forcing_cols = ['solar_forcing', 'volcanic_forcing', 'ghg_forcing', 'aerosol_forcing']
X = df[forcing_cols].values
y = df['observed_temp_anomaly'].values

# Add intercept
X_design = np.column_stack([np.ones(len(y)), X])
alpha = 1.0
p = X_design.shape[1]
coef = np.linalg.solve(X_design.T @ X_design + alpha * np.eye(p), X_design.T @ y)

# Attribution fractions (skip intercept)
contributions = np.abs(coef[1:] * X.mean(axis=0))
fractions = contributions / contributions.sum()
print(dict(zip(forcing_cols, fractions)))

# Example 2: R-squared calculation
y_pred = X_design @ coef
ss_res = np.sum((y - y_pred)**2)
ss_tot = np.sum((y - y.mean())**2)
r_squared = 1 - ss_res / ss_tot
print(f"R² = {r_squared:.4f}")
