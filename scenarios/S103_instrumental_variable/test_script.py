import sys, os, json, subprocess, tempfile
import numpy as np

def create_test_csv(path, n=500):
    """创建带内生性的 IV 测试数据"""
    np.random.seed(42)
    # 真实因果效应 = 2.0
    # Z → X → Y, 但 X 和 Y 共享混杂因子 U
    Z = np.random.normal(0, 1, n)
    U = np.random.normal(0, 1, n)  # 混杂
    C1 = np.random.normal(0, 1, n)
    X = 0.8 * Z + 0.5 * U + 0.3 * C1 + np.random.normal(0, 0.5, n)
    Y = 2.0 * X + 0.7 * U + 0.2 * C1 + np.random.normal(0, 1, n)

    with open(path, "w") as f:
        f.write("outcome,treatment,instrument,C1\n")
        for i in range(n):
            f.write(f"{Y[i]:.4f},{X[i]:.4f},{Z[i]:.4f},{C1[i]:.4f}\n")

with tempfile.TemporaryDirectory() as tmpdir:
    csv_path = f"{tmpdir}/iv_data.csv"
    out_json = f"{tmpdir}/results.json"
    create_test_csv(csv_path)

    ran = False
    for args in [
        [sys.executable, "solution.py", "--input", csv_path, "--output", out_json,
         "--outcome", "outcome", "--treatment", "treatment", "--instrument", "instrument"],
        [sys.executable, "solution.py", "--input", csv_path, "--output", out_json,
         "--outcome", "outcome", "--treatment", "treatment", "--instrument", "instrument",
         "--confounders", "C1"],
    ]:
        r = subprocess.run(args, capture_output=True, text=True, timeout=60, cwd=os.getcwd())
        if r.returncode == 0 or os.path.exists(out_json):
            ran = True
            break

    print(f"{'PASS' if ran else 'FAIL'}:L1_runs")

    if not os.path.exists(out_json):
        print("FAIL:L1_output_exists")
        for t in ["L1_valid_json","L2_has_iv_estimate","L2_has_ols_estimate","L2_has_f_stat","L2_iv_close_to_true","L2_ols_biased","L2_strong_instrument","L2_has_n_obs"]:
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

    # IV estimate 存在
    iv_est = results.get("iv_estimate", results.get("iv_coef", results.get("beta_iv", None)))
    if iv_est is not None:
        print(f"PASS:L2_has_iv_estimate - {iv_est}")
    else:
        print("FAIL:L2_has_iv_estimate")

    # OLS estimate 存在
    ols_est = results.get("ols_estimate", results.get("ols_coef", results.get("beta_ols", None)))
    if ols_est is not None:
        print(f"PASS:L2_has_ols_estimate - {ols_est}")
    else:
        print("FAIL:L2_has_ols_estimate")

    # F-statistic 存在
    f_stat = results.get("first_stage_f", results.get("f_statistic", results.get("f_stat", None)))
    if f_stat is not None:
        print(f"PASS:L2_has_f_stat - F={f_stat}")
    else:
        print("FAIL:L2_has_f_stat")

    # IV estimate 应接近真实值 2.0
    if iv_est is not None and isinstance(iv_est, (int, float)):
        if 1.0 < iv_est < 3.5:
            print(f"PASS:L2_iv_close_to_true - IV={iv_est:.3f} (true=2.0)")
        else:
            print(f"FAIL:L2_iv_close_to_true - IV={iv_est:.3f} (expected ~2.0)")
    else:
        print("FAIL:L2_iv_close_to_true")

    # OLS 应有向上偏差（因为 U 的混杂）
    if ols_est is not None and isinstance(ols_est, (int, float)):
        if ols_est > 2.0:
            print(f"PASS:L2_ols_biased - OLS={ols_est:.3f} > true=2.0 (upward bias)")
        else:
            print(f"FAIL:L2_ols_biased - OLS={ols_est:.3f} (expected upward bias)")
    else:
        print("FAIL:L2_ols_biased")

    # F > 10 (强工具变量)
    if f_stat is not None and isinstance(f_stat, (int, float)):
        if f_stat > 10:
            print(f"PASS:L2_strong_instrument - F={f_stat:.1f} > 10")
        else:
            print(f"FAIL:L2_strong_instrument - F={f_stat:.1f}")
    else:
        print("FAIL:L2_strong_instrument")

    # n_observations
    n_obs = results.get("n_observations", results.get("n", results.get("n_obs", None)))
    if n_obs is not None:
        print(f"PASS:L2_has_n_obs - n={n_obs}")
    else:
        print("FAIL:L2_has_n_obs")
