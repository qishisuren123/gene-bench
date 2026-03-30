import sys, os, json, subprocess, tempfile
import numpy as np

def create_test_csv(path, n_years=50):
    """创建模拟气候归因数据"""
    np.random.seed(42)
    years = np.arange(1970, 1970 + n_years)

    # 各 forcing 分量
    ghg = np.linspace(0, 1.5, n_years) + np.random.normal(0, 0.05, n_years)
    solar = 0.1 * np.sin(2 * np.pi * np.arange(n_years) / 11) + np.random.normal(0, 0.02, n_years)
    volcanic = np.zeros(n_years)
    volcanic[15] = -0.3  # 模拟火山事件
    volcanic[30] = -0.2
    aerosol = np.linspace(0, -0.4, n_years) + np.random.normal(0, 0.03, n_years)
    natural = np.random.normal(0, 0.1, n_years)

    # 观测温度 = 真实线性组合 + 噪声
    observed = 0.8 * ghg + 0.3 * solar + 1.0 * volcanic + 0.5 * aerosol + 0.2 * natural + np.random.normal(0, 0.05, n_years)

    with open(path, "w") as f:
        f.write("year,observed_temp_anomaly,solar_forcing,volcanic_forcing,ghg_forcing,aerosol_forcing,natural_variability\n")
        for i in range(n_years):
            f.write(f"{years[i]},{observed[i]:.4f},{solar[i]:.4f},{volcanic[i]:.4f},{ghg[i]:.4f},{aerosol[i]:.4f},{natural[i]:.4f}\n")

with tempfile.TemporaryDirectory() as tmpdir:
    csv_path = f"{tmpdir}/climate_data.csv"
    out_json = f"{tmpdir}/results.json"
    create_test_csv(csv_path)

    # 尝试运行
    ran = False
    for args in [
        [sys.executable, "solution.py", "--input", csv_path, "--output", out_json],
        [sys.executable, "solution.py", "--input", csv_path, "--output", out_json, "--method", "ridge"],
        [sys.executable, "solution.py", csv_path, "--output", out_json],
    ]:
        r = subprocess.run(args, capture_output=True, text=True, timeout=60, cwd=os.getcwd())
        if r.returncode == 0 or os.path.exists(out_json):
            ran = True
            break

    if ran or os.path.exists(out_json):
        print("PASS:L1_runs")
    else:
        print(f"FAIL:L1_runs - {r.stderr[-200:]}")

    if os.path.exists(out_json):
        print("PASS:L1_output_exists")
    else:
        print("FAIL:L1_output_exists")
        for t in ["L1_valid_json", "L2_has_method", "L2_has_coefficients", "L2_has_attribution", "L2_has_r_squared", "L2_attribution_sums", "L2_ghg_dominant", "L2_reasonable_r2"]:
            print(f"FAIL:{t} - no output")
        sys.exit(0)

    # 验证 JSON
    try:
        with open(out_json) as f:
            results = json.load(f)
        print("PASS:L1_valid_json")
    except Exception as e:
        print(f"FAIL:L1_valid_json - {e}")
        for t in ["L2_has_method", "L2_has_coefficients", "L2_has_attribution", "L2_has_r_squared", "L2_attribution_sums", "L2_ghg_dominant", "L2_reasonable_r2"]:
            print(f"FAIL:{t} - invalid json")
        sys.exit(0)

    # L2: 有 method 字段
    if "method" in results:
        print(f"PASS:L2_has_method - {results['method']}")
    else:
        print("FAIL:L2_has_method")

    # L2: 有 coefficients
    coeffs = results.get("coefficients", results.get("coeff", results.get("betas", {})))
    if isinstance(coeffs, dict) and len(coeffs) >= 3:
        print(f"PASS:L2_has_coefficients - {len(coeffs)} factors")
    else:
        print(f"FAIL:L2_has_coefficients - got {type(coeffs)}")

    # L2: 有 attribution fractions
    attr = results.get("attribution_fractions", results.get("attribution", results.get("fractions", {})))
    if isinstance(attr, dict) and len(attr) >= 3:
        print(f"PASS:L2_has_attribution - {len(attr)} factors")
    else:
        print(f"FAIL:L2_has_attribution - got {type(attr)}")

    # L2: 有 r_squared
    r2 = results.get("r_squared", results.get("r2", results.get("R2", None)))
    if r2 is not None:
        print(f"PASS:L2_has_r_squared - {r2}")
    else:
        print("FAIL:L2_has_r_squared")

    # L2: attribution 百分比合理（接近 100%）
    if isinstance(attr, dict) and len(attr) >= 3:
        total_attr = sum(abs(v) for v in attr.values())
        residual = results.get("residual_fraction", results.get("residual", 0))
        if isinstance(residual, (int, float)):
            total_attr += abs(residual)
        if 0.5 < total_attr < 2.0:  # 宽松范围
            print(f"PASS:L2_attribution_sums - total={total_attr:.3f}")
        else:
            print(f"FAIL:L2_attribution_sums - total={total_attr:.3f}")
    else:
        print("FAIL:L2_attribution_sums - no attribution data")

    # L2: GHG 应该是主导 forcing
    if isinstance(attr, dict):
        ghg_keys = [k for k in attr if "ghg" in k.lower() or "greenhouse" in k.lower()]
        if ghg_keys:
            ghg_val = attr[ghg_keys[0]]
            max_val = max(abs(v) for v in attr.values())
            if abs(ghg_val) >= max_val * 0.5:
                print(f"PASS:L2_ghg_dominant - ghg={ghg_val:.3f}")
            else:
                print(f"FAIL:L2_ghg_dominant - ghg={ghg_val:.3f}, max={max_val:.3f}")
        else:
            print("FAIL:L2_ghg_dominant - no ghg key found")
    else:
        print("FAIL:L2_ghg_dominant")

    # L2: R² 合理（应 > 0.5 对于这个人造数据）
    if r2 is not None and isinstance(r2, (int, float)):
        if 0.3 < r2 <= 1.0:
            print(f"PASS:L2_reasonable_r2 - R²={r2:.3f}")
        else:
            print(f"FAIL:L2_reasonable_r2 - R²={r2:.3f}")
    else:
        print("FAIL:L2_reasonable_r2")

    # 测试其他 method
    for method in ["ols", "bayesian"]:
        out2 = f"{tmpdir}/results_{method}.json"
        r2 = subprocess.run(
            [sys.executable, "solution.py", "--input", csv_path, "--output", out2, "--method", method],
            capture_output=True, text=True, timeout=60, cwd=os.getcwd()
        )
        if r2.returncode == 0 and os.path.exists(out2):
            print(f"PASS:L2_method_{method}")
        else:
            print(f"FAIL:L2_method_{method}")
