# 2D Robot Obstacle Avoidance Path Planning

## Overview
This skill plans collision-free robot trajectories in 2D environments using RRT (Rapidly-exploring Random Trees) or Potential Field methods, with collision detection against circular obstacles and post-processing path smoothing.

## Workflow
1. Parse command-line arguments for input JSON (environment definition), output JSON, method (rrt/potential_field), step-size (0.5), max-iterations (5000)
2. Load environment: start position, goal position, obstacles (circular: center_x, center_y, radius), workspace bounds
3. For RRT: initialize tree with start node; iteratively sample random points, find nearest tree node, extend toward sample with step_size, check collision along segment
4. Collision check: for line segment vs circular obstacle, compute closest point on segment to circle center; collision if distance < radius
5. When tree node reaches within step_size of goal, connect to goal; extract path by backtracking through parent pointers
6. Post-process: attempt shortcutting between non-adjacent waypoints; if shortcut segment is collision-free, remove intermediate waypoints
7. Compute metrics: total_path_length, n_waypoints, min_obstacle_clearance (minimum distance from any waypoint to any obstacle boundary), smoothness (sum of angle changes)
8. Output JSON with path (list of [x,y] waypoints), method, success flag, and metrics

## Common Pitfalls
- **Step size tuning**: Too large skips narrow passages between obstacles; too small makes tree grow slowly — scale step_size with environment dimensions (~5% of workspace diagonal)
- **Potential field local minima**: Purely gradient-based methods get stuck between obstacles — add random perturbation or switch to RRT when progress stalls
- **Line-circle collision**: Must check closest point on segment (not just endpoints); use perpendicular projection clamped to segment bounds
- **Goal bias**: Pure random sampling is slow to reach goal — sample goal directly with 5-10% probability for faster convergence

## Error Handling
- Validate that start and goal positions are within workspace bounds and not inside any obstacle
- Handle max-iterations timeout: return best partial path with success=false
- Check for degenerate obstacles (zero or negative radius)

## Quick Reference
- Nearest node: `min(tree, key=lambda n: distance(n, sample))`
- Extend: `new_pos = nearest + step_size * (sample - nearest) / distance(nearest, sample)`
- Line-circle collision: project circle center onto line segment, check `dist < radius`
- Path length: `sum(distance(path[i], path[i+1]) for i in range(len(path)-1))`
- Smoothness: `sum(abs(angle(p[i-1], p[i], p[i+1])) for i in range(1, len(path)-1))`
- Min clearance: `min(distance(waypoint, obstacle_center) - obstacle_radius for all pairs)`
