# Example 1: Rolling z-score anomaly detection per sensor
import numpy as np
import pandas as pd

# Simulated multi-sensor data (3 sensors, 500 timesteps)
np.random.seed(42)
data = np.random.randn(500, 3)
data[200, 0] = 8.0  # inject anomaly
data[350, 1] = -7.5

df = pd.DataFrame(data, columns=['sensor_0', 'sensor_1', 'sensor_2'])
window = 50
threshold = 3.0

z_scores = (df - df.rolling(window).mean()) / df.rolling(window).std()
anomalies_z = (z_scores.abs() > threshold).any(axis=1)
print(f"Z-score anomalies at indices: {list(anomalies_z[anomalies_z].index)}")

# Example 2: Mahalanobis distance on joint sensor readings
from scipy.spatial.distance import mahalanobis

# Fit on clean training data (first 100 points)
train = data[:100]
mu = train.mean(axis=0)
cov = np.cov(train.T)
cov_inv = np.linalg.inv(cov)

# Compute Mahalanobis distance for all points
distances = np.array([mahalanobis(row, mu, cov_inv) for row in data])
chi2_thresh = 3.5  # approximate threshold for 3 sensors
anomalies_mah = np.where(distances > chi2_thresh)[0]
print(f"Mahalanobis anomalies at indices: {anomalies_mah}")

# Example 3: Ensemble voting
ensemble_flags = np.zeros(len(data), dtype=bool)
z_flags = anomalies_z.values
m_flags = distances > chi2_thresh
# Flag if both methods agree
ensemble_flags = z_flags & m_flags
print(f"Ensemble anomalies: {np.where(ensemble_flags)[0]}")
