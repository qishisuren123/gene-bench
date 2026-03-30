import sys, os, json, subprocess, tempfile
import numpy as np

def create_test_csv(path):
    np.random.seed(42)
    wn = np.arange(200, 3501, 1.0)
    # 基线（荧光背景）
    baseline = 0.5 * np.exp(-(wn - 1500)**2 / (2 * 800**2))
    # 拉曼峰
    peaks_params = [
        (1000, 0.8, 15),   # C-C stretch
        (1700, 0.6, 20),   # C=O stretch
        (2900, 1.2, 25),   # C-H stretch
        (3400, 0.4, 30),   # O-H stretch
        (1450, 0.3, 12),   # C-H bend
    ]
    signal = np.zeros_like(wn)
    for center, amp, width in peaks_params:
        signal += amp * np.exp(-(wn - center)**2 / (2 * width**2))
    intensity = baseline + signal + np.random.normal(0, 0.02, len(wn))
    intensity = np.maximum(intensity, 0)

    with open(path, "w") as f:
        f.write("wavenumber_cm1,intensity\n")
        for i in range(len(wn)):
            f.write(f"{wn[i]:.1f},{intensity[i]:.6f}\n")

with tempfile.TemporaryDirectory() as tmpdir:
    csv_path = f"{tmpdir}/raman.csv"
    out_json = f"{tmpdir}/peaks.json"
    create_test_csv(csv_path)

    ran = False
    for args in [
        [sys.executable, "solution.py", "--input", csv_path, "--output", out_json],
        [sys.executable, "solution.py", "--input", csv_path, "--output", out_json, "--baseline-method", "polynomial"],
    ]:
        r = subprocess.run(args, capture_output=True, text=True, timeout=60, cwd=os.getcwd())
        if r.returncode == 0 or os.path.exists(out_json):
            ran = True
            break

    print(f"{'PASS' if ran else 'FAIL'}:L1_runs")
    if not os.path.exists(out_json):
        print("FAIL:L1_output_exists")
        for t in ["L1_valid_json","L2_has_peaks","L2_peak_count","L2_ch_stretch","L2_co_stretch","L2_has_fwhm","L2_has_assignment","L2_has_area"]:
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

    peaks = results.get("peaks", [])
    if isinstance(peaks, list) and len(peaks) >= 3:
        print(f"PASS:L2_has_peaks - {len(peaks)}")
    else:
        print(f"FAIL:L2_has_peaks - {len(peaks) if isinstance(peaks, list) else 0}")

    # 峰数量合理 (3-10)
    if 3 <= len(peaks) <= 15:
        print(f"PASS:L2_peak_count - {len(peaks)}")
    else:
        print(f"FAIL:L2_peak_count - {len(peaks)}")

    # 检测到 C-H stretch (~2900)
    positions = [p.get("position", p.get("wavenumber", p.get("center", 0))) for p in peaks]
    ch_found = any(2800 < pos < 3000 for pos in positions)
    print(f"{'PASS' if ch_found else 'FAIL'}:L2_ch_stretch")

    # 检测到 C=O (~1700)
    co_found = any(1650 < pos < 1750 for pos in positions)
    print(f"{'PASS' if co_found else 'FAIL'}:L2_co_stretch")

    # 有 FWHM
    has_fwhm = any("fwhm" in p or "width" in p or "FWHM" in p for p in peaks) if peaks else False
    print(f"{'PASS' if has_fwhm else 'FAIL'}:L2_has_fwhm")

    # 有 assignment
    has_assign = any("assignment" in p or "label" in p or "band" in p for p in peaks) if peaks else False
    print(f"{'PASS' if has_assign else 'FAIL'}:L2_has_assignment")

    # 有 area
    has_area = any("area" in p for p in peaks) if peaks else False
    print(f"{'PASS' if has_area else 'FAIL'}:L2_has_area")
