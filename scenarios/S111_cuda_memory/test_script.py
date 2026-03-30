import sys, os, json, subprocess, tempfile

def create_test_json(path):
    events = []
    # 模拟 GPU 内存分配事件
    # Phase 1: 加载模型参数 (t=0-100ms)
    events.append({"timestamp_ms": 0, "operation": "alloc", "size_bytes": 500_000_000, "tensor_name": "model.weights", "dtype": "float32"})
    events.append({"timestamp_ms": 10, "operation": "alloc", "size_bytes": 200_000_000, "tensor_name": "model.bias", "dtype": "float32"})
    # Phase 2: Forward pass (t=100-300ms)
    events.append({"timestamp_ms": 100, "operation": "alloc", "size_bytes": 800_000_000, "tensor_name": "activations.layer1", "dtype": "float32"})
    events.append({"timestamp_ms": 150, "operation": "alloc", "size_bytes": 600_000_000, "tensor_name": "activations.layer2", "dtype": "float32"})
    events.append({"timestamp_ms": 200, "operation": "alloc", "size_bytes": 400_000_000, "tensor_name": "activations.layer3", "dtype": "float32"})
    # 一个 float64 tensor（可优化）
    events.append({"timestamp_ms": 250, "operation": "alloc", "size_bytes": 100_000_000, "tensor_name": "loss.grad_buffer", "dtype": "float64"})
    # Phase 3: 释放一些
    events.append({"timestamp_ms": 300, "operation": "free", "size_bytes": 800_000_000, "tensor_name": "activations.layer1", "dtype": "float32"})
    events.append({"timestamp_ms": 310, "operation": "free", "size_bytes": 600_000_000, "tensor_name": "activations.layer2", "dtype": "float32"})
    # Phase 4: Backward pass
    events.append({"timestamp_ms": 400, "operation": "alloc", "size_bytes": 500_000_000, "tensor_name": "gradients.layer3", "dtype": "float32"})
    events.append({"timestamp_ms": 500, "operation": "free", "size_bytes": 400_000_000, "tensor_name": "activations.layer3", "dtype": "float32"})
    events.append({"timestamp_ms": 510, "operation": "free", "size_bytes": 500_000_000, "tensor_name": "gradients.layer3", "dtype": "float32"})
    events.append({"timestamp_ms": 520, "operation": "free", "size_bytes": 100_000_000, "tensor_name": "loss.grad_buffer", "dtype": "float64"})

    with open(path, "w") as f:
        json.dump(events, f, indent=2)
    return events

with tempfile.TemporaryDirectory() as tmpdir:
    json_path = f"{tmpdir}/gpu_events.json"
    out_json = f"{tmpdir}/analysis.json"
    events = create_test_json(json_path)

    ran = False
    for args in [
        [sys.executable, "solution.py", "--input", json_path, "--output", out_json],
        [sys.executable, "solution.py", "--input", json_path, "--output", out_json, "--gpu-memory-gb", "16.0"],
    ]:
        r = subprocess.run(args, capture_output=True, text=True, timeout=60, cwd=os.getcwd())
        if r.returncode == 0 or os.path.exists(out_json):
            ran = True
            break

    print(f"{'PASS' if ran else 'FAIL'}:L1_runs")
    if not os.path.exists(out_json):
        print("FAIL:L1_output_exists")
        for t in ["L1_valid_json","L2_peak_memory","L2_peak_timestamp","L2_efficiency","L2_n_allocations","L2_suggestions","L2_fragmentation","L2_peak_reasonable"]:
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

    # Peak memory
    peak = results.get("peak_memory_bytes", results.get("peak_memory", results.get("peak_usage", None)))
    if peak is not None and isinstance(peak, (int, float)) and peak > 1_000_000_000:
        print(f"PASS:L2_peak_memory - {peak/1e9:.2f} GB")
    else:
        print(f"FAIL:L2_peak_memory - {peak}")

    # Peak timestamp
    peak_ts = results.get("peak_timestamp", results.get("peak_time", None))
    if peak_ts is not None:
        print(f"PASS:L2_peak_timestamp - {peak_ts}ms")
    else:
        print("FAIL:L2_peak_timestamp")

    # Efficiency
    eff = results.get("efficiency", results.get("memory_efficiency", None))
    if eff is not None and isinstance(eff, (int, float)):
        print(f"PASS:L2_efficiency - {eff:.3f}")
    else:
        print("FAIL:L2_efficiency")

    # N allocations
    n_alloc = results.get("n_allocations", results.get("total_allocations", None))
    if n_alloc is not None:
        print(f"PASS:L2_n_allocations - {n_alloc}")
    else:
        print("FAIL:L2_n_allocations")

    # Optimization suggestions
    suggestions = results.get("optimization_suggestions", results.get("suggestions", results.get("optimizations", [])))
    if isinstance(suggestions, list) and len(suggestions) >= 1:
        print(f"PASS:L2_suggestions - {len(suggestions)} suggestions")
    else:
        print("FAIL:L2_suggestions")

    # Fragmentation
    frag = results.get("fragmentation_ratio", results.get("fragmentation", None))
    if frag is not None:
        print(f"PASS:L2_fragmentation - {frag}")
    else:
        print("FAIL:L2_fragmentation")

    # Peak 合理范围 (应在 2-3 GB 左右)
    if peak is not None and isinstance(peak, (int, float)):
        peak_gb = peak / 1e9
        if 1.5 < peak_gb < 5.0:
            print(f"PASS:L2_peak_reasonable - {peak_gb:.2f} GB")
        else:
            print(f"FAIL:L2_peak_reasonable - {peak_gb:.2f} GB (expected 1.5-5.0)")
    else:
        print("FAIL:L2_peak_reasonable")
