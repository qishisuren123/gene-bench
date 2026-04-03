# Rolling z-score
- z_i = (x_i - mean_window) / std_window
- Use pandas: df.rolling(window).mean(), df.rolling(window).std()
- Flag anomaly when |z| > threshold (typically 2.5 or 3.0)
- Handle edge: first `window-1` points have NaN, fill or skip

# Mahalanobis distance
- D = sqrt((x - mu)^T @ Sigma_inv @ (x - mu))
- mu: mean vector of training data (p,)
- Sigma: covariance matrix (p, p), use np.cov(X.T)
- Sigma_inv: np.linalg.inv(cov) or scipy.spatial.distance.mahalanobis
- Threshold: chi-squared distribution with p degrees of freedom, ppf(0.975)

# scipy.spatial.distance.mahalanobis
mahalanobis(u, v, VI)
- u, v: 1-D arrays (observation, mean)
- VI: inverse covariance matrix
- Returns scalar distance

# Ensemble anomaly detection
- Combine multiple detectors: z-score per sensor + Mahalanobis on joint
- Voting: flag as anomaly if >= k out of n detectors agree
- Score fusion: average normalized scores, threshold on combined score

# numpy.cov
np.cov(m, rowvar=True)
- m: data array, each row is a variable (transpose if needed)
- Returns covariance matrix (p, p)
