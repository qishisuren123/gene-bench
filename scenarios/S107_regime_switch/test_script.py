import sys, os, json, subprocess, tempfile
import numpy as np

def create_test_csv(path, n_days=300):
    np.random.seed(42)
    dates = [f"2023-{(i//30)+1:02d}-{(i%30)+1:02d}" for i in range(n_days)]
    price = [100.0]
    volumes = []
    # 3 个 regime: low_vol (0-100), high_vol (100-200), crisis (200-250), low_vol (250-300)
    for i in range(1, n_days):
        if i < 100:
            ret = np.random.normal(0.001, 0.01)
            vol = np.random.randint(1000, 3000)
        elif i < 200:
            ret = np.random.normal(0.0005, 0.03)
            vol = np.random.randint(3000, 8000)
        elif i < 250:
            ret = np.random.normal(-0.002, 0.06)
            vol = np.random.randint(8000, 20000)
        else:
            ret = np.random.normal(0.001, 0.01)
            vol = np.random.randint(1000, 3000)
        price.append(price[-1] * (1 + ret))
        volumes.append(vol)
    volumes.append(np.random.randint(1000, 3000))

    with open(path, "w") as f:
        f.write("date,price,volume\n")
        for i in range(n_days):
            f.write(f"{dates[i]},{price[i]:.2f},{volumes[i]}\n")

with tempfile.TemporaryDirectory() as tmpdir:
    csv_path = f"{tmpdir}/financial.csv"
    out_json = f"{tmpdir}/regimes.json"
    create_test_csv(csv_path)

    ran = False
    for args in [
        [sys.executable, "solution.py", "--input", csv_path, "--output", out_json],
        [sys.executable, "solution.py", "--input", csv_path, "--output", out_json, "--min-regime-length", "20"],
    ]:
        r = subprocess.run(args, capture_output=True, text=True, timeout=60, cwd=os.getcwd())
        if r.returncode == 0 or os.path.exists(out_json):
            ran = True
            break

    print(f"{'PASS' if ran else 'FAIL'}:L1_runs")
    if not os.path.exists(out_json):
        print("FAIL:L1_output_exists")
        for t in ["L1_valid_json","L2_has_regimes","L2_regime_count","L2_has_volatility","L2_has_transition","L2_crisis_detected","L2_has_dates","L2_has_sharpe"]:
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

    regimes = results.get("regimes", [])
    if isinstance(regimes, list) and len(regimes) >= 2:
        print(f"PASS:L2_has_regimes - {len(regimes)}")
    else:
        print(f"FAIL:L2_has_regimes")

    n_reg = results.get("n_regimes", len(regimes))
    if 2 <= n_reg <= 15:
        print(f"PASS:L2_regime_count - {n_reg}")
    else:
        print(f"FAIL:L2_regime_count - {n_reg}")

    # 有 volatility 字段
    has_vol = any("volatility" in r or "vol" in r for r in regimes) if regimes else False
    print(f"{'PASS' if has_vol else 'FAIL'}:L2_has_volatility")

    # 有 transition matrix
    tm = results.get("transition_matrix", results.get("transitions", None))
    if tm is not None:
        print("PASS:L2_has_transition")
    else:
        print("FAIL:L2_has_transition")

    # 检测到 crisis regime
    crisis_found = any("crisis" in str(r.get("type", r.get("regime_type", ""))).lower() or "high" in str(r.get("type", r.get("regime_type", ""))).lower() for r in regimes)
    print(f"{'PASS' if crisis_found else 'FAIL'}:L2_crisis_detected")

    # 有日期字段
    has_dates = any("start_date" in r or "start" in r for r in regimes) if regimes else False
    print(f"{'PASS' if has_dates else 'FAIL'}:L2_has_dates")

    # 有 sharpe ratio
    has_sharpe = any("sharpe" in r for r in regimes) if regimes else False
    print(f"{'PASS' if has_sharpe else 'FAIL'}:L2_has_sharpe")
