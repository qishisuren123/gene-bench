# Multi-Sensor Anomaly Detection

## Overview
This skill detects anomalies in multi-sensor time series data using an ensemble of rolling z-score, cross-sensor correlation, and Mahalanobis distance methods, classifying each anomaly as point, collective, or contextual.

## Workflow
1. Parse command-line arguments for input CSV, output JSON, window-size (default 50), and threshold (default 3.0)
2. Load CSV with timestamp and sensor_1..sensor_N columns; infer number of sensors from columns
3. Compute per-sensor rolling z-scores: (x - rolling_mean) / rolling_std for each sensor independently
4. Flag point anomalies: single timestamps where any sensor z-score exceeds threshold
5. Cross-validate: timestamps where >50% of sensors are anomalous simultaneously → classify as collective anomaly
6. Compute Mahalanobis distance across all sensors for each timestamp; flag multivariate anomalies where distance exceeds chi-squared threshold
7. Classify anomaly types: point (single sensor, single timestamp), collective (multiple sensors or sustained), contextual (cross-sensor disagreement)
8. Output JSON with n_sensors, n_timestamps, total anomalies, and per-anomaly details (timestamp, type, sensors_affected, score)

## Common Pitfalls
- **Rolling window warmup**: First `window_size` timestamps have insufficient data for stable statistics — skip or use expanding window
- **Covariance singularity**: Mahalanobis distance requires invertible covariance matrix — add small regularization (1e-6 × I) for near-singular cases
- **Anomaly flooding**: Very noisy sensors trigger too many individual anomalies — use cross-sensor consensus to filter false positives
- **Collective detection**: Need minimum duration (e.g., 3+ consecutive timestamps) to distinguish collective from coincidental point anomalies

## Error Handling
- Validate that CSV has at least 2 sensor columns beyond timestamp
- Handle NaN/missing values by forward-filling or interpolation before z-score computation
- Check that window_size < total timestamps to ensure meaningful rolling statistics

## Quick Reference
- Rolling z-score: `(x - pd.rolling(w).mean()) / pd.rolling(w).std()`
- Mahalanobis: `sqrt((x - μ)ᵀ Σ⁻¹ (x - μ))`
- Cross-sensor consensus: `sum(abs(z_i) > threshold) / n_sensors > 0.5`
- Point anomaly: single spike in one sensor
- Collective anomaly: sustained across multiple timestamps or sensors
