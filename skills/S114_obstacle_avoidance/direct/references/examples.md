# Example 1: Basic RRT path planner
import numpy as np

def rrt(start, goal, obstacles, bounds, step_size=0.5,
        max_iter=5000, goal_radius=0.5, goal_bias=0.05):
    """RRT planner with circular obstacles."""
    nodes = [np.array(start, dtype=float)]
    parent = {0: -1}

    def is_collision_free(p1, p2, n_checks=20):
        for t in np.linspace(0, 1, n_checks):
            pt = p1 + t * (p2 - p1)
            for (cx, cy, r) in obstacles:
                if np.hypot(pt[0] - cx, pt[1] - cy) < r:
                    return False
        return True

    for _ in range(max_iter):
        # Sample with goal bias
        if np.random.rand() < goal_bias:
            sample = np.array(goal, dtype=float)
        else:
            sample = np.array([
                np.random.uniform(bounds[0], bounds[1]),
                np.random.uniform(bounds[2], bounds[3]),
            ])

        # Find nearest node
        dists = [np.linalg.norm(n - sample) for n in nodes]
        nearest_idx = int(np.argmin(dists))
        nearest = nodes[nearest_idx]

        # Steer toward sample
        direction = sample - nearest
        dist = np.linalg.norm(direction)
        if dist < 1e-6:
            continue
        new_node = nearest + (direction / dist) * min(step_size, dist)

        # Check collision
        if not is_collision_free(nearest, new_node):
            continue

        # Add to tree
        new_idx = len(nodes)
        nodes.append(new_node)
        parent[new_idx] = nearest_idx

        # Check goal
        if np.linalg.norm(new_node - np.array(goal)) < goal_radius:
            path = [new_node, np.array(goal)]
            idx = new_idx
            while parent[idx] != -1:
                idx = parent[idx]
                path.append(nodes[idx])
            return path[::-1]
    return None  # No path found

# Example 2: Run planner
obstacles = [(3, 3, 1.0), (5, 7, 1.5), (8, 4, 1.0)]
bounds = [0, 10, 0, 10]  # xmin, xmax, ymin, ymax
path = rrt((1, 1), (9, 9), obstacles, bounds)
if path:
    print(f"Path found with {len(path)} waypoints")
    for p in path:
        print(f"  ({p[0]:.2f}, {p[1]:.2f})")
