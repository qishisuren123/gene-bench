import sys, os, json, subprocess, tempfile
import random

def create_test_log(path, n_lines=500):
    random.seed(42)
    ips = ["192.168.1.1", "10.0.0.5", "172.16.0.10", "192.168.1.100", "10.0.0.1"]
    urls = ["/index.html", "/api/users", "/api/data", "/static/style.css", "/login", "/admin", "/api/upload", "/health"]
    methods = ["GET", "POST", "PUT", "DELETE"]
    statuses = [200, 200, 200, 200, 200, 301, 304, 400, 403, 404, 500]

    # 一个 IP 高频访问（异常检测用）
    with open(path, "w") as f:
        for i in range(n_lines):
            ip = "10.0.0.99" if i % 3 == 0 else random.choice(ips)
            method = random.choice(methods)
            url = random.choice(urls)
            status = random.choice(statuses)
            size = random.randint(100, 50000) if status == 200 else 0
            hour = random.randint(0, 23)
            minute = random.randint(0, 59)
            second = random.randint(0, 59)
            day = random.randint(1, 28)
            f.write(f'{ip} - - [15/Mar/2024:{hour:02d}:{minute:02d}:{second:02d} +0000] "{method} {url} HTTP/1.1" {status} {size}\n')
        # 一些解析失败的行
        f.write("malformed line without proper format\n")
        f.write("another broken log entry\n")

with tempfile.TemporaryDirectory() as tmpdir:
    log_path = f"{tmpdir}/access.log"
    out_json = f"{tmpdir}/metrics.json"
    create_test_log(log_path)

    ran = False
    for args in [
        [sys.executable, "solution.py", "--input", log_path, "--output", out_json],
        [sys.executable, "solution.py", "--input", log_path, "--output", out_json, "--format", "apache"],
    ]:
        r = subprocess.run(args, capture_output=True, text=True, timeout=60, cwd=os.getcwd())
        if r.returncode == 0 or os.path.exists(out_json):
            ran = True
            break

    print(f"{'PASS' if ran else 'FAIL'}:L1_runs")
    if not os.path.exists(out_json):
        print("FAIL:L1_output_exists")
        for t in ["L1_valid_json","L2_status_dist","L2_top_urls","L2_top_ips","L2_error_rate","L2_parse_stats","L2_anomaly_ip","L2_hourly_dist","L2_avg_size"]:
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

    # Status code distribution
    status_dist = results.get("status_distribution", results.get("status_codes", results.get("statuses", None)))
    if isinstance(status_dist, dict) and len(status_dist) >= 2:
        print(f"PASS:L2_status_dist - {len(status_dist)} codes")
    else:
        print("FAIL:L2_status_dist")

    # Top URLs
    top_urls = results.get("top_urls", results.get("top_paths", results.get("urls", None)))
    if isinstance(top_urls, (list, dict)) and len(top_urls) >= 3:
        print(f"PASS:L2_top_urls")
    else:
        print("FAIL:L2_top_urls")

    # Top IPs
    top_ips = results.get("top_ips", results.get("top_clients", results.get("ips", None)))
    if isinstance(top_ips, (list, dict)) and len(top_ips) >= 3:
        print(f"PASS:L2_top_ips")
    else:
        print("FAIL:L2_top_ips")

    # Error rate
    err_rate = results.get("error_rate", results.get("error_pct", None))
    if err_rate is not None:
        print(f"PASS:L2_error_rate - {err_rate}")
    else:
        print("FAIL:L2_error_rate")

    # Parse statistics
    parse_stats = results.get("parse_statistics", results.get("parse_stats", {}))
    total = parse_stats.get("total_lines", parse_stats.get("total", results.get("total_requests", results.get("total_lines", None))))
    if total is not None and int(total) > 400:
        print(f"PASS:L2_parse_stats - total={total}")
    else:
        print(f"FAIL:L2_parse_stats - total={total}")

    # 异常 IP 检测 (10.0.0.99 应出现在异常列表)
    anomalies = results.get("anomalies", results.get("suspicious", []))
    if isinstance(anomalies, (list, dict)):
        anomaly_str = json.dumps(anomalies)
        if "10.0.0.99" in anomaly_str or len(anomalies) > 0:
            print("PASS:L2_anomaly_ip")
        else:
            print("FAIL:L2_anomaly_ip")
    else:
        print("FAIL:L2_anomaly_ip")

    # Hourly distribution
    hourly = results.get("requests_per_hour", results.get("hourly", results.get("hourly_distribution", None)))
    if hourly is not None:
        print("PASS:L2_hourly_dist")
    else:
        print("FAIL:L2_hourly_dist")

    # Average size
    avg_size = results.get("average_response_size", results.get("avg_size", results.get("mean_size", None)))
    if avg_size is not None:
        print(f"PASS:L2_avg_size - {avg_size}")
    else:
        print("FAIL:L2_avg_size")
