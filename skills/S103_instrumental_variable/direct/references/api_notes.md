# numpy.linalg.lstsq
lstsq(a, b, rcond=None)
- Solves min ||a @ x - b||² for x
- Returns: (solution, residuals, rank, singular_values)
- Handles rank-deficient matrices gracefully

# numpy.column_stack
column_stack(tup)
- Stack 1-D arrays as columns into a 2-D array
- Useful for building design matrices: np.column_stack([np.ones(n), Z, C])

# scipy.stats.f
f.sf(x, dfn, dfd) — survival function (1 - CDF) for F-distribution
- dfn: numerator degrees of freedom
- dfd: denominator degrees of freedom
- Use for computing p-value of F-statistic

# Standard error formula
SE(coef) = sqrt(diag(sigma² * (X'X)^{-1}))
where sigma² = sum(residuals²) / (n - p)
