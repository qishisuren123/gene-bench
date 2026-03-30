Write a Python CLI script that detects overlapping communities in a network graph.

Input: An edge list CSV file with columns: source, target, weight (optional).

Requirements:
1. Use argparse: --input edge CSV, --output JSON, --method (choices: "label_propagation", "modularity", default "label_propagation")
2. Build an undirected graph from the edge list using adjacency lists (no networkx required)
3. For label_propagation: implement asynchronous label propagation
   - Initialize each node with unique label
   - Iteratively update: each node adopts the most frequent label among neighbors (random tie-breaking)
   - Allow overlapping: node belongs to community if >30% of neighbors share that label
   - Stop after convergence or max 100 iterations
4. For modularity: implement Louvain-like greedy modularity optimization
   - Start with each node as its own community
   - Greedily merge communities that maximize modularity gain
5. Compute per-community statistics: size, internal_edges, density
6. Compute global modularity score Q
7. Output JSON: n_nodes, n_edges, n_communities, modularity, communities (list of {id, members, size, density})
8. Print summary: number of communities, largest community size, modularity
