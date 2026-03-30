import sys, os, json, subprocess, tempfile
import numpy as np

def create_test_csv(path):
    np.random.seed(42)
    rows = []
    products = ["PROD_A", "PROD_B", "PROD_C"]
    demands = {"PROD_A": (50, 10), "PROD_B": (200, 40), "PROD_C": (10, 5)}
    lead_times = {"PROD_A": (5, 1), "PROD_B": (3, 0.5), "PROD_C": (10, 2)}

    for product in products:
        mean_d, std_d = demands[product]
        mean_lt, std_lt = lead_times[product]
        for day in range(365):
            date = f"2024-{(day//30)+1:02d}-{(day%30)+1:02d}"
            d = max(0, int(np.random.normal(mean_d, std_d)))
            lt = max(1, int(np.random.normal(mean_lt, std_lt)))
            rows.append((date, product, d, lt))

    with open(path, "w") as f:
        f.write("date,product_id,demand_quantity,lead_time_days\n")
        for date, pid, d, lt in rows:
            f.write(f"{date},{pid},{d},{lt}\n")

with tempfile.TemporaryDirectory() as tmpdir:
    csv_path = f"{tmpdir}/demand.csv"
    out_json = f"{tmpdir}/inventory.json"
    create_test_csv(csv_path)

    ran = False
    for args in [
        [sys.executable, "solution.py", "--input", csv_path, "--output", out_json],
        [sys.executable, "solution.py", "--input", csv_path, "--output", out_json, "--service-level", "0.95"],
    ]:
        r = subprocess.run(args, capture_output=True, text=True, timeout=60, cwd=os.getcwd())
        if r.returncode == 0 or os.path.exists(out_json):
            ran = True
            break

    print(f"{'PASS' if ran else 'FAIL'}:L1_runs")
    if not os.path.exists(out_json):
        print("FAIL:L1_output_exists")
        for t in ["L1_valid_json","L2_has_products","L2_has_eoq","L2_has_rop","L2_has_safety_stock","L2_eoq_reasonable","L2_three_products","L2_has_cost","L2_has_demand_stats"]:
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

    # 可能是列表或字典
    products = results if isinstance(results, list) else results.get("products", results.get("results", []))
    if isinstance(products, dict):
        products = list(products.values()) if products else []

    if len(products) >= 2:
        print(f"PASS:L2_has_products - {len(products)}")
    else:
        print(f"FAIL:L2_has_products - {len(products)}")

    # 有 EOQ
    has_eoq = any("eoq" in str(p).lower() for p in products) if products else False
    print(f"{'PASS' if has_eoq else 'FAIL'}:L2_has_eoq")

    # 有 reorder point
    has_rop = any("reorder" in str(p).lower() or "rop" in str(p).lower() for p in products) if products else False
    print(f"{'PASS' if has_rop else 'FAIL'}:L2_has_rop")

    # 有 safety stock
    has_ss = any("safety" in str(p).lower() for p in products) if products else False
    print(f"{'PASS' if has_ss else 'FAIL'}:L2_has_safety_stock")

    # EOQ 合理范围
    eoq_ok = False
    for p in products:
        eoq_val = p.get("eoq", p.get("EOQ", p.get("economic_order_quantity", None))) if isinstance(p, dict) else None
        if eoq_val is not None and isinstance(eoq_val, (int, float)) and 10 < eoq_val < 10000:
            eoq_ok = True
            break
    print(f"{'PASS' if eoq_ok else 'FAIL'}:L2_eoq_reasonable")

    # 3 个产品
    if len(products) >= 3:
        print(f"PASS:L2_three_products - {len(products)}")
    else:
        print(f"FAIL:L2_three_products - {len(products)}")

    # 有成本
    has_cost = any("cost" in str(p).lower() for p in products) if products else False
    print(f"{'PASS' if has_cost else 'FAIL'}:L2_has_cost")

    # 有需求统计
    has_stats = any("demand" in str(p).lower() and ("mean" in str(p).lower() or "avg" in str(p).lower() or "stat" in str(p).lower()) for p in products) if products else False
    if not has_stats:
        has_stats = any("demand_stats" in p or "statistics" in p for p in products if isinstance(p, dict))
    print(f"{'PASS' if has_stats else 'FAIL'}:L2_has_demand_stats")
