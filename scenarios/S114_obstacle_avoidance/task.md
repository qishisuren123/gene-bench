Write a Python CLI script that plans obstacle-avoidance trajectories for a 2D robot using potential field or RRT methods.

Input: A JSON file describing the environment: {start: [x,y], goal: [x,y], obstacles: [{center: [x,y], radius: r}, ...], bounds: [xmin, ymin, xmax, ymax]}.

Requirements:
1. Use argparse: --input JSON, --output JSON, --method (choices: "potential_field", "rrt", default "rrt"), --step-size (default 0.5), --max-iterations (default 5000)
2. Load environment definition and validate
3. For RRT (Rapidly-exploring Random Tree):
   - Initialize tree with start node
   - Randomly sample points in bounds, find nearest tree node, extend toward sample
   - Check collision with obstacles (line-circle intersection)
   - When a node is within step_size of goal, connect to goal
   - Smooth path by attempting to shortcut intermediate waypoints
4. For Potential Field:
   - Attractive force toward goal: F_att = -k_att * (pos - goal)
   - Repulsive force from obstacles: F_rep = k_rep * (1/d - 1/d0) * 1/d^2 * gradient(d)
   - Gradient descent with step size, max iterations, local minima detection
5. Compute path metrics: total_length, n_waypoints, min_obstacle_clearance, smoothness (curvature integral)
6. Output JSON: path (list of [x,y] waypoints), method, metrics, success (bool)
7. Print summary: path found (yes/no), length, clearance, number of waypoints
