import sys, os, json, subprocess, tempfile
import numpy as np

def create_test_csv(path, n_rows=50000, n_numeric=5, n_string=2):
    np.random.seed(42)
    with open(path, "w") as f:
        headers = [f"num_{i}" for i in range(n_numeric)] + [f"str_{i}" for i in range(n_string)]
        f.write(",".join(headers) + "\n")
        labels = ["alpha", "beta", "gamma", "delta", "epsilon"]
        for row in range(n_rows):
            nums = ",".join(f"{np.random.normal(0, 1):.6f}" for _ in range(n_numeric))
            strs = ",".join(labels[np.random.randint(0, len(labels))] for _ in range(n_string))
            f.write(f"{nums},{strs}\n")
    return n_rows

with tempfile.TemporaryDirectory() as tmpdir:
    csv_path = f"{tmpdir}/large_data.csv"
    out_h5 = f"{tmpdir}/output.h5"
    n_rows = create_test_csv(csv_path)

    ran = False
    for args in [
        [sys.executable, "solution.py", "--input", csv_path, "--output", out_h5],
        [sys.executable, "solution.py", "--input", csv_path, "--output", out_h5, "--chunk-rows", "10000", "--compression", "gzip"],
    ]:
        r = subprocess.run(args, capture_output=True, text=True, timeout=120, cwd=os.getcwd())
        if r.returncode == 0 or os.path.exists(out_h5):
            ran = True
            break

    print(f"{'PASS' if ran else 'FAIL'}:L1_runs")
    if not os.path.exists(out_h5):
        print("FAIL:L1_output_exists")
        for t in ["L1_valid_h5","L2_has_datasets","L2_chunked","L2_compressed","L2_has_metadata","L2_correct_rows","L2_numeric_data","L2_roundtrip"]:
            print(f"FAIL:{t}")
        sys.exit(0)
    print("PASS:L1_output_exists")

    import h5py
    try:
        f = h5py.File(out_h5, "r")
        print("PASS:L1_valid_h5")
    except Exception as e:
        print(f"FAIL:L1_valid_h5 - {e}")
        sys.exit(0)

    # 有数据集
    all_keys = list(f.keys())
    datasets = [k for k in all_keys if isinstance(f[k], h5py.Dataset)]
    groups = [k for k in all_keys if isinstance(f[k], h5py.Group)]
    # 也检查子目录
    def collect_datasets(grp, prefix=""):
        ds = []
        for k in grp:
            path = f"{prefix}/{k}" if prefix else k
            if isinstance(grp[k], h5py.Dataset):
                ds.append(path)
            elif isinstance(grp[k], h5py.Group):
                ds.extend(collect_datasets(grp[k], path))
        return ds
    all_datasets = collect_datasets(f)

    if len(all_datasets) >= 5:
        print(f"PASS:L2_has_datasets - {len(all_datasets)}")
    else:
        print(f"FAIL:L2_has_datasets - {len(all_datasets)}")

    # 检查 chunking
    chunked = False
    for ds_path in all_datasets:
        ds = f[ds_path]
        if ds.chunks is not None:
            chunked = True
            break
    print(f"{'PASS' if chunked else 'FAIL'}:L2_chunked")

    # 检查压缩
    compressed = False
    for ds_path in all_datasets:
        ds = f[ds_path]
        if ds.compression is not None:
            compressed = True
            break
    print(f"{'PASS' if compressed else 'FAIL'}:L2_compressed")

    # 有 metadata
    has_meta = "_metadata" in f or "metadata" in f or any("meta" in k.lower() for k in all_keys)
    if not has_meta:
        # 检查 root attributes
        has_meta = len(f.attrs) > 0
    print(f"{'PASS' if has_meta else 'FAIL'}:L2_has_metadata")

    # 行数正确
    correct_rows = False
    for ds_path in all_datasets:
        ds = f[ds_path]
        if hasattr(ds, 'shape') and len(ds.shape) >= 1:
            if ds.shape[0] == n_rows:
                correct_rows = True
                break
    print(f"{'PASS' if correct_rows else 'FAIL'}:L2_correct_rows")

    # 数值数据可读
    numeric_ok = False
    for ds_path in all_datasets:
        ds = f[ds_path]
        if hasattr(ds, 'dtype') and np.issubdtype(ds.dtype, np.floating):
            sample = ds[:10]
            if not np.any(np.isnan(sample)):
                numeric_ok = True
                break
    print(f"{'PASS' if numeric_ok else 'FAIL'}:L2_numeric_data")

    # 压缩比（H5 < CSV）
    csv_size = os.path.getsize(csv_path)
    h5_size = os.path.getsize(out_h5)
    if h5_size < csv_size:
        print(f"PASS:L2_roundtrip - compression ratio={csv_size/h5_size:.1f}x")
    else:
        print(f"FAIL:L2_roundtrip - h5={h5_size} >= csv={csv_size}")

    f.close()
