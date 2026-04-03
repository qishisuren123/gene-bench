# numpy.linalg.lstsq
lstsq(a, b, rcond=None)
- a: coefficient matrix (N, M)
- b: dependent variable (N,) or (N, K)
- Returns: (solution, residuals, rank, singular_values)
- solution shape: (M,) or (M, K)

# numpy.linalg.solve
solve(a, b)
- Solve a @ x = b for x
- a must be square and non-singular
- For Ridge: solve(X.T @ X + alpha * I, X.T @ y)

# scipy.stats.norm.ppf
ppf(q) — percent point function (inverse CDF)
- Returns z-score for given quantile

# Design matrix construction
- Add intercept column: X = np.column_stack([np.ones(n), forcing_columns])
- Or center data: X_centered = X - X.mean(axis=0)
