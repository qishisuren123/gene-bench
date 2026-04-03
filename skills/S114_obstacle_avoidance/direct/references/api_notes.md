# RRT (Rapidly-exploring Random Tree) algorithm
1. Initialize tree with start node
2. Sample random point in configuration space
3. Find nearest node in tree to sample
4. Steer from nearest toward sample by step_size
5. Check if new edge is collision-free
6. If valid, add new node and edge to tree
7. Check if new node is within goal_radius of goal
8. Repeat until goal reached or max_iterations

# Collision detection
- Point-in-obstacle: check if point lies inside any obstacle
- Edge collision: discretize edge into small steps, check each
- For circular obstacles: distance(point, center) < radius
- For rectangular obstacles: check x,y bounds
- Step size for edge check: typically obstacle_radius / 2

# Distance metrics
- Euclidean: np.linalg.norm(a - b)
- For nearest neighbor: brute force O(n) or use scipy.spatial.KDTree

# scipy.spatial.KDTree
tree = KDTree(points)
- query(x, k=1): find k nearest neighbors
- Returns (distances, indices)

# Path extraction
- Maintain parent dict: parent[new_node] = nearest_node
- Backtrack from goal to start via parent pointers
- Reverse to get start-to-goal path

# Key parameters
- step_size: max extension distance per iteration (tune for map scale)
- goal_radius: distance threshold to consider goal reached
- max_iter: 1000-10000 depending on complexity
- goal_bias: probability of sampling goal directly (0.05-0.1)
