import sys, os, json, subprocess, tempfile
import numpy as np

def create_test_csv(path, n_sensors=4, n_timestamps=200):
    np.random.seed(42)
    timestamps = [f"2024-01-01T{h:02d}:{m:02d}:00" for h in range(n_timestamps // 60 + 1) for m in range(60)][:n_timestamps]

    data = np.random.normal(0, 1, (n_timestamps, n_sensors))
    # 注入 point anomaly (单点异常)
    data[50, 0] = 8.0
    data[51, 0] = -7.0
    # 注入 collective anomaly (持续异常)
    data[100:110, 1] = 5.0 + np.random.normal(0, 0.3, 10)
    # 注入 cross-sensor anomaly (多传感器同时)
    data[150, :] = 6.0

    with open(path, "w") as f:
        headers = ["timestamp"] + [f"sensor_{i+1}" for i in range(n_sensors)]
        f.write(",".join(headers) + "\n")
        for i in range(n_timestamps):
            vals = ",".join(f"{data[i,j]:.4f}" for j in range(n_sensors))
            f.write(f"{timestamps[i]},{vals}\n")

with tempfile.TemporaryDirectory() as tmpdir:
    csv_path = f"{tmpdir}/sensors.csv"
    out_json = f"{tmpdir}/anomalies.json"
    create_test_csv(csv_path)

    ran = False
    for args in [
        [sys.executable, "solution.py", "--input", csv_path, "--output", out_json],
        [sys.executable, "solution.py", "--input", csv_path, "--output", out_json, "--window-size", "50", "--threshold", "3.0"],
    ]:
        r = subprocess.run(args, capture_output=True, text=True, timeout=60, cwd=os.getcwd())
        if r.returncode == 0 or os.path.exists(out_json):
            ran = True
            break

    print(f"{'PASS' if ran else 'FAIL'}:L1_runs")
    if not os.path.exists(out_json):
        print("FAIL:L1_output_exists")
        for t in ["L1_valid_json","L2_has_anomalies","L2_detected_point","L2_detected_collective","L2_has_n_sensors","L2_has_types","L2_anomaly_count_reasonable","L2_has_scores"]:
            print(f"FAIL:{t}")
        sys.exit(0)
    print("PASS:L1_output_exists")

    try:
        with open(out_json) as f:
            results = json.load(f)
        print("PASS:L1_valid_json")
    except:
        print("FAIL:L1_valid_json")
        sys.exit(0)

    anomalies = results.get("anomalies", results.get("detected", []))
    if isinstance(anomalies, list) and len(anomalies) > 0:
        print(f"PASS:L2_has_anomalies - {len(anomalies)} detected")
    else:
        print("FAIL:L2_has_anomalies")
        anomalies = []

    # 检测到 point anomaly (在 index 50 附近)
    point_found = False
    for a in anomalies:
        ts = str(a.get("timestamp", a.get("index", "")))
        if "00:50" in ts or "50" in str(a.get("index", "")):
            point_found = True
            break
    # 宽松检查：只要有 point 类型
    if not point_found:
        point_found = any("point" in str(a.get("type", "")).lower() for a in anomalies)
    print(f"{'PASS' if point_found else 'FAIL'}:L2_detected_point")

    # 检测到 collective anomaly
    collective_found = any("collective" in str(a.get("type", "")).lower() or "sustained" in str(a.get("type", "")).lower() for a in anomalies)
    if not collective_found:
        collective_found = len(anomalies) >= 5  # 至少检测到多个
    print(f"{'PASS' if collective_found else 'FAIL'}:L2_detected_collective")

    # n_sensors
    ns = results.get("n_sensors", results.get("num_sensors", None))
    if ns is not None:
        print(f"PASS:L2_has_n_sensors - {ns}")
    else:
        print("FAIL:L2_has_n_sensors")

    # anomaly 有 type 字段
    has_types = any("type" in a for a in anomalies) if anomalies else False
    print(f"{'PASS' if has_types else 'FAIL'}:L2_has_types")

    # 合理的异常数量 (3-50)
    if 2 <= len(anomalies) <= 100:
        print(f"PASS:L2_anomaly_count_reasonable - {len(anomalies)}")
    else:
        print(f"FAIL:L2_anomaly_count_reasonable - {len(anomalies)}")

    # 有 score 字段
    has_scores = any("score" in a or "z_score" in a or "distance" in a for a in anomalies) if anomalies else False
    print(f"{'PASS' if has_scores else 'FAIL'}:L2_has_scores")
