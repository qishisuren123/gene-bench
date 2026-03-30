import sys, os, json, subprocess, tempfile
import numpy as np

def create_test_csv(path, duration=30.0, fs=100.0):
    np.random.seed(42)
    n = int(duration * fs)
    t = np.arange(n) / fs
    noise = np.random.normal(0, 0.1, (n, 3))
    signal = np.zeros((n, 3))
    # P-wave arrival at t=10s
    arrival = int(10.0 * fs)
    wave = np.exp(-np.arange(200) / 50) * np.sin(2 * np.pi * 5 * np.arange(200) / fs)
    for c in range(3):
        amp = [1.0, 0.8, 1.2][c]
        signal[arrival:arrival+200, c] = amp * wave
    # 第二个事件 at t=20s
    arrival2 = int(20.0 * fs)
    wave2 = np.exp(-np.arange(150) / 40) * np.sin(2 * np.pi * 8 * np.arange(150) / fs)
    for c in range(3):
        amp = [0.6, 0.5, 0.7][c]
        signal[arrival2:arrival2+150, c] = amp * wave2
    data = signal + noise
    with open(path, "w") as f:
        f.write("time_s,velocity_north,velocity_east,velocity_vertical\n")
        for i in range(n):
            f.write(f"{t[i]:.4f},{data[i,0]:.6f},{data[i,1]:.6f},{data[i,2]:.6f}\n")

with tempfile.TemporaryDirectory() as tmpdir:
    csv_path = f"{tmpdir}/seismic.csv"
    out_dir = f"{tmpdir}/output"
    os.makedirs(out_dir, exist_ok=True)
    create_test_csv(csv_path)

    ran = False
    for args in [
        [sys.executable, "solution.py", "--input", csv_path, "--output-dir", out_dir],
        [sys.executable, "solution.py", "--input", csv_path, "--output-dir", out_dir, "--lowcut", "1.0", "--highcut", "20.0"],
    ]:
        r = subprocess.run(args, capture_output=True, text=True, timeout=60, cwd=os.getcwd())
        if r.returncode == 0:
            ran = True
            break

    print(f"{'PASS' if ran else 'FAIL'}:L1_runs")

    # 检查输出文件
    out_files = os.listdir(out_dir) if os.path.exists(out_dir) else []
    has_csv = any(f.endswith(".csv") for f in out_files)
    has_json = any(f.endswith(".json") for f in out_files)

    if has_csv or has_json:
        print("PASS:L1_output_exists")
    else:
        print("FAIL:L1_output_exists")
        for t in ["L2_filtered_data","L2_detections","L2_snr_improvement","L2_arrival_near_10s","L2_two_events","L2_filter_params","L2_has_components"]:
            print(f"FAIL:{t}")
        sys.exit(0)

    # 检查 JSON 结果
    json_files = [f for f in out_files if f.endswith(".json")]
    results = {}
    if json_files:
        try:
            with open(os.path.join(out_dir, json_files[0])) as f:
                results = json.load(f)
            print("PASS:L1_valid_json")
        except:
            print("FAIL:L1_valid_json")

    # 有过滤后的数据
    print(f"{'PASS' if has_csv else 'FAIL'}:L2_filtered_data")

    # 有检测结果
    detections = results.get("arrivals", results.get("detections", results.get("events", [])))
    if isinstance(detections, list) and len(detections) >= 1:
        print(f"PASS:L2_detections - {len(detections)} events")
    else:
        print("FAIL:L2_detections")

    # SNR 改善
    snr = results.get("snr_improvements", results.get("snr", results.get("SNR", None)))
    if snr is not None:
        print(f"PASS:L2_snr_improvement")
    else:
        print("FAIL:L2_snr_improvement")

    # 第一个到达时间接近 10s
    if detections:
        first_time = None
        for d in detections:
            t_val = d.get("time", d.get("arrival_time", d.get("time_s", None)))
            if t_val is not None:
                first_time = float(t_val)
                break
        if first_time is not None and 8.0 < first_time < 12.0:
            print(f"PASS:L2_arrival_near_10s - t={first_time:.2f}s")
        else:
            print(f"FAIL:L2_arrival_near_10s - t={first_time}")
    else:
        print("FAIL:L2_arrival_near_10s")

    # 检测到 2 个事件
    if len(detections) >= 2:
        print(f"PASS:L2_two_events - {len(detections)}")
    else:
        print(f"FAIL:L2_two_events - {len(detections)}")

    # 有滤波参数
    params = results.get("filter_parameters", results.get("parameters", results.get("filter", None)))
    if params is not None:
        print("PASS:L2_filter_params")
    else:
        print("FAIL:L2_filter_params")

    # 三分量都处理了
    csv_files = [f for f in out_files if f.endswith(".csv")]
    if csv_files:
        with open(os.path.join(out_dir, csv_files[0])) as f:
            header = f.readline().lower()
        has_3 = sum(1 for c in ["north", "east", "vertical", "n", "e", "z"] if c in header) >= 3
        print(f"{'PASS' if has_3 else 'FAIL'}:L2_has_components")
    else:
        print("FAIL:L2_has_components")
