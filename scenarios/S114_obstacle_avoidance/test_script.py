import sys, os, json, subprocess, tempfile
import math

def create_test_env(path):
    env = {
        "start": [1.0, 1.0],
        "goal": [9.0, 9.0],
        "obstacles": [
            {"center": [3.0, 3.0], "radius": 1.0},
            {"center": [5.0, 5.0], "radius": 1.5},
            {"center": [7.0, 3.0], "radius": 0.8},
            {"center": [3.0, 7.0], "radius": 1.2},
        ],
        "bounds": [0.0, 0.0, 10.0, 10.0],
    }
    with open(path, "w") as f:
        json.dump(env, f, indent=2)
    return env

def point_in_obstacle(x, y, obstacles):
    for obs in obstacles:
        cx, cy = obs["center"]
        r = obs["radius"]
        if math.sqrt((x-cx)**2 + (y-cy)**2) < r:
            return True
    return False

with tempfile.TemporaryDirectory() as tmpdir:
    env_path = f"{tmpdir}/env.json"
    out_json = f"{tmpdir}/trajectory.json"
    env = create_test_env(env_path)

    ran = False
    for args in [
        [sys.executable, "solution.py", "--input", env_path, "--output", out_json],
        [sys.executable, "solution.py", "--input", env_path, "--output", out_json, "--method", "rrt"],
        [sys.executable, "solution.py", "--input", env_path, "--output", out_json, "--method", "potential_field"],
    ]:
        r = subprocess.run(args, capture_output=True, text=True, timeout=120, cwd=os.getcwd())
        if r.returncode == 0 or os.path.exists(out_json):
            ran = True
            break

    print(f"{'PASS' if ran else 'FAIL'}:L1_runs")
    if not os.path.exists(out_json):
        print("FAIL:L1_output_exists")
        for t in ["L1_valid_json","L2_has_path","L2_path_starts","L2_path_ends","L2_no_collision","L2_has_metrics","L2_path_length","L2_success","L2_has_clearance"]:
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

    path = results.get("path", results.get("trajectory", results.get("waypoints", [])))
    if isinstance(path, list) and len(path) >= 3:
        print(f"PASS:L2_has_path - {len(path)} waypoints")
    else:
        print(f"FAIL:L2_has_path - {len(path) if isinstance(path, list) else 0}")
        path = []

    # 起点接近 start
    if path:
        sx, sy = path[0] if isinstance(path[0], list) else (path[0].get("x", 0), path[0].get("y", 0))
        dist_start = math.sqrt((sx - 1.0)**2 + (sy - 1.0)**2)
        print(f"{'PASS' if dist_start < 1.0 else 'FAIL'}:L2_path_starts - dist={dist_start:.2f}")
    else:
        print("FAIL:L2_path_starts")

    # 终点接近 goal
    if path:
        ex, ey = path[-1] if isinstance(path[-1], list) else (path[-1].get("x", 0), path[-1].get("y", 0))
        dist_goal = math.sqrt((ex - 9.0)**2 + (ey - 9.0)**2)
        print(f"{'PASS' if dist_goal < 1.5 else 'FAIL'}:L2_path_ends - dist={dist_goal:.2f}")
    else:
        print("FAIL:L2_path_ends")

    # 路径不穿过障碍物
    collision_free = True
    for pt in path:
        if isinstance(pt, list):
            px, py = pt[0], pt[1]
        else:
            px, py = pt.get("x", 0), pt.get("y", 0)
        if point_in_obstacle(px, py, env["obstacles"]):
            collision_free = False
            break
    print(f"{'PASS' if collision_free else 'FAIL'}:L2_no_collision")

    # 有 metrics
    metrics = results.get("metrics", {})
    if isinstance(metrics, dict) and len(metrics) >= 1:
        print("PASS:L2_has_metrics")
    elif any(k in results for k in ["total_length", "path_length", "n_waypoints"]):
        print("PASS:L2_has_metrics")
    else:
        print("FAIL:L2_has_metrics")

    # 路径长度合理 (直线距离 ~11.3, 应 < 30)
    total_len = 0
    if len(path) >= 2:
        for i in range(1, len(path)):
            if isinstance(path[i], list):
                dx = path[i][0] - path[i-1][0]
                dy = path[i][1] - path[i-1][1]
            else:
                dx = path[i].get("x", 0) - path[i-1].get("x", 0)
                dy = path[i].get("y", 0) - path[i-1].get("y", 0)
            total_len += math.sqrt(dx**2 + dy**2)
    if 10 < total_len < 50:
        print(f"PASS:L2_path_length - {total_len:.2f}")
    else:
        print(f"FAIL:L2_path_length - {total_len:.2f}")

    # success 字段
    success = results.get("success", results.get("found", None))
    if success is True or success == "true" or (success is None and len(path) > 0):
        print("PASS:L2_success")
    else:
        print(f"FAIL:L2_success - {success}")

    # clearance
    clearance = metrics.get("min_obstacle_clearance", metrics.get("clearance", results.get("min_clearance", None)))
    if clearance is not None:
        print(f"PASS:L2_has_clearance - {clearance}")
    else:
        print("FAIL:L2_has_clearance")
