Write a Python CLI script that detects anomalies in multi-sensor time series data using ensemble methods.

Input: A CSV file with columns: timestamp, sensor_1, sensor_2, ..., sensor_N (numeric readings from N sensors).

Requirements:
1. Use argparse: --input CSV, --output JSON, --window-size (default 50), --threshold (default 3.0 for z-score)
2. Load CSV and auto-detect sensor columns (all numeric columns except timestamp)
3. For each sensor independently: compute rolling z-score anomalies using the window size
4. Cross-sensor correlation check: flag timestamps where >50% of sensors show anomalies simultaneously
5. Implement Mahalanobis distance for multivariate anomaly detection across all sensors
6. Classify anomalies into types: "point" (single spike), "collective" (sustained), "contextual" (cross-sensor disagreement)
7. Output JSON with: n_sensors, n_timestamps, anomalies (list of {timestamp, type, sensors_affected, score}), summary_stats
8. Print summary: total anomalies by type, most anomalous sensor
