import sys, os, json, subprocess, tempfile
import random

def create_test_edgelist(path):
    """创建有明显社区结构的测试图"""
    random.seed(42)
    edges = []
    # 社区 1: 节点 0-9 (密集连接)
    for i in range(10):
        for j in range(i+1, 10):
            if random.random() < 0.7:
                edges.append((i, j, round(random.uniform(0.5, 1.0), 2)))
    # 社区 2: 节点 10-19
    for i in range(10, 20):
        for j in range(i+1, 20):
            if random.random() < 0.7:
                edges.append((i, j, round(random.uniform(0.5, 1.0), 2)))
    # 社区 3: 节点 20-29
    for i in range(20, 30):
        for j in range(i+1, 30):
            if random.random() < 0.6:
                edges.append((i, j, round(random.uniform(0.5, 1.0), 2)))
    # 社区间稀疏连接
    for _ in range(5):
        a = random.randint(0, 9)
        b = random.randint(10, 19)
        edges.append((a, b, 0.1))
    for _ in range(3):
        a = random.randint(10, 19)
        b = random.randint(20, 29)
        edges.append((a, b, 0.1))

    with open(path, "w") as f:
        f.write("source,target,weight\n")
        for s, t, w in edges:
            f.write(f"{s},{t},{w}\n")
    return 30, len(edges), 3

with tempfile.TemporaryDirectory() as tmpdir:
    csv_path = f"{tmpdir}/edges.csv"
    out_json = f"{tmpdir}/communities.json"
    n_nodes, n_edges, expected_communities = create_test_edgelist(csv_path)

    ran = False
    for args in [
        [sys.executable, "solution.py", "--input", csv_path, "--output", out_json],
        [sys.executable, "solution.py", "--input", csv_path, "--output", out_json, "--method", "label_propagation"],
    ]:
        r = subprocess.run(args, capture_output=True, text=True, timeout=120, cwd=os.getcwd())
        if r.returncode == 0 or os.path.exists(out_json):
            ran = True
            break

    print(f"{'PASS' if ran else 'FAIL'}:L1_runs")
    if not os.path.exists(out_json):
        print("FAIL:L1_output_exists")
        for t in ["L1_valid_json","L2_has_communities","L2_community_count","L2_all_nodes_assigned","L2_has_modularity","L2_has_density","L2_reasonable_structure","L2_has_sizes"]:
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

    communities = results.get("communities", [])
    if isinstance(communities, list) and len(communities) >= 2:
        print(f"PASS:L2_has_communities - {len(communities)}")
    else:
        print(f"FAIL:L2_has_communities - got {len(communities) if isinstance(communities, list) else type(communities)}")

    # 社区数量合理 (2-10)
    n_comm = results.get("n_communities", len(communities) if isinstance(communities, list) else 0)
    if 2 <= n_comm <= 10:
        print(f"PASS:L2_community_count - {n_comm}")
    else:
        print(f"FAIL:L2_community_count - {n_comm} (expected 2-10)")

    # 所有节点都被分配
    all_members = set()
    for c in communities:
        members = c.get("members", c.get("nodes", []))
        if isinstance(members, list):
            all_members.update(members)
    if len(all_members) >= n_nodes * 0.8:
        print(f"PASS:L2_all_nodes_assigned - {len(all_members)}/{n_nodes}")
    else:
        print(f"FAIL:L2_all_nodes_assigned - {len(all_members)}/{n_nodes}")

    # modularity 存在
    mod = results.get("modularity", results.get("Q", None))
    if mod is not None:
        print(f"PASS:L2_has_modularity - Q={mod}")
    else:
        print("FAIL:L2_has_modularity")

    # density 字段
    has_density = any("density" in c for c in communities) if communities else False
    print(f"{'PASS' if has_density else 'FAIL'}:L2_has_density")

    # 合理结构：最大社区不超过总节点的 60%
    sizes = [c.get("size", len(c.get("members", c.get("nodes", [])))) for c in communities]
    if sizes:
        max_size = max(sizes)
        if max_size <= n_nodes * 0.6:
            print(f"PASS:L2_reasonable_structure - max_community={max_size}")
        else:
            print(f"FAIL:L2_reasonable_structure - max_community={max_size}")
    else:
        print("FAIL:L2_reasonable_structure")

    # 有 size 字段
    has_sizes = any("size" in c for c in communities) if communities else False
    print(f"{'PASS' if has_sizes else 'FAIL'}:L2_has_sizes")
