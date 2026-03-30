import sys, os, json, subprocess, tempfile
import math

def create_test_circuits(tmpdir):
    """创建测试量子电路"""
    circuits = {}

    # Bell state: H on q0, CNOT q0->q1 → |00>+|11> / sqrt(2)
    circuits["bell"] = {
        "n_qubits": 2,
        "gates": [
            {"type": "H", "target": 0},
            {"type": "CNOT", "control": 0, "target": 1},
        ]
    }

    # GHZ state: H + CNOT chain → |000>+|111> / sqrt(2)
    circuits["ghz3"] = {
        "n_qubits": 3,
        "gates": [
            {"type": "H", "target": 0},
            {"type": "CNOT", "control": 0, "target": 1},
            {"type": "CNOT", "control": 1, "target": 2},
        ]
    }

    # Simple: X gate on q0 → |1>
    circuits["x_gate"] = {
        "n_qubits": 1,
        "gates": [
            {"type": "X", "target": 0},
        ]
    }

    for name, circ in circuits.items():
        path = f"{tmpdir}/{name}.json"
        with open(path, "w") as f:
            json.dump(circ, f, indent=2)

    return circuits

with tempfile.TemporaryDirectory() as tmpdir:
    circuits = create_test_circuits(tmpdir)

    # 测试 Bell state
    bell_path = f"{tmpdir}/bell.json"
    out_json = f"{tmpdir}/bell_result.json"

    ran = False
    for args in [
        [sys.executable, "solution.py", "--input", bell_path, "--output", out_json],
        [sys.executable, "solution.py", "--input", bell_path, "--output", out_json, "--shots", "1024"],
    ]:
        r = subprocess.run(args, capture_output=True, text=True, timeout=60, cwd=os.getcwd())
        if r.returncode == 0 or os.path.exists(out_json):
            ran = True
            break

    print(f"{'PASS' if ran else 'FAIL'}:L1_runs")
    if not os.path.exists(out_json):
        print("FAIL:L1_output_exists")
        for t in ["L1_valid_json","L2_has_probabilities","L2_bell_state","L2_has_counts","L2_probs_sum_one","L2_has_state_vector","L2_x_gate","L2_ghz_state"]:
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

    # 有 probabilities
    probs = results.get("probabilities", results.get("probs", {}))
    if isinstance(probs, dict) and len(probs) >= 1:
        print(f"PASS:L2_has_probabilities - {len(probs)} states")
    else:
        print("FAIL:L2_has_probabilities")

    # Bell state: |00> 和 |11> 各 ~0.5
    bell_ok = False
    if isinstance(probs, dict):
        p00 = probs.get("00", probs.get("|00>", probs.get("0", 0)))
        p11 = probs.get("11", probs.get("|11>", probs.get("3", 0)))
        if isinstance(p00, (int, float)) and isinstance(p11, (int, float)):
            if abs(p00 - 0.5) < 0.15 and abs(p11 - 0.5) < 0.15:
                bell_ok = True
    print(f"{'PASS' if bell_ok else 'FAIL'}:L2_bell_state")

    # 有 measurement counts
    counts = results.get("measurement_counts", results.get("counts", results.get("samples", None)))
    if counts is not None and isinstance(counts, dict):
        print(f"PASS:L2_has_counts - {sum(counts.values())} shots")
    else:
        print("FAIL:L2_has_counts")

    # 概率求和 ~1.0
    if isinstance(probs, dict) and probs:
        total_p = sum(float(v) for v in probs.values())
        if abs(total_p - 1.0) < 0.05:
            print(f"PASS:L2_probs_sum_one - sum={total_p:.4f}")
        else:
            print(f"FAIL:L2_probs_sum_one - sum={total_p:.4f}")
    else:
        print("FAIL:L2_probs_sum_one")

    # 有 state vector
    sv = results.get("state_vector", results.get("statevector", results.get("amplitudes", None)))
    if sv is not None:
        print("PASS:L2_has_state_vector")
    else:
        print("FAIL:L2_has_state_vector")

    # 测试 X gate
    x_path = f"{tmpdir}/x_gate.json"
    x_out = f"{tmpdir}/x_result.json"
    r2 = subprocess.run(
        [sys.executable, "solution.py", "--input", x_path, "--output", x_out],
        capture_output=True, text=True, timeout=60, cwd=os.getcwd()
    )
    x_ok = False
    if os.path.exists(x_out):
        try:
            with open(x_out) as f:
                x_results = json.load(f)
            x_probs = x_results.get("probabilities", x_results.get("probs", {}))
            p1 = x_probs.get("1", x_probs.get("|1>", 0))
            if isinstance(p1, (int, float)) and p1 > 0.9:
                x_ok = True
        except:
            pass
    print(f"{'PASS' if x_ok else 'FAIL'}:L2_x_gate")

    # 测试 GHZ state
    ghz_path = f"{tmpdir}/ghz3.json"
    ghz_out = f"{tmpdir}/ghz_result.json"
    r3 = subprocess.run(
        [sys.executable, "solution.py", "--input", ghz_path, "--output", ghz_out],
        capture_output=True, text=True, timeout=60, cwd=os.getcwd()
    )
    ghz_ok = False
    if os.path.exists(ghz_out):
        try:
            with open(ghz_out) as f:
                ghz_results = json.load(f)
            ghz_probs = ghz_results.get("probabilities", ghz_results.get("probs", {}))
            p000 = ghz_probs.get("000", ghz_probs.get("|000>", 0))
            p111 = ghz_probs.get("111", ghz_probs.get("|111>", 0))
            if isinstance(p000, (int, float)) and isinstance(p111, (int, float)):
                if abs(p000 - 0.5) < 0.15 and abs(p111 - 0.5) < 0.15:
                    ghz_ok = True
        except:
            pass
    print(f"{'PASS' if ghz_ok else 'FAIL'}:L2_ghz_state")
