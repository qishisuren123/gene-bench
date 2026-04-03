# collections.defaultdict
defaultdict(list) — adjacency list representation
- adj[u].append(v) and adj[v].append(u) for undirected edges

# collections.Counter
Counter(labels).most_common(1) — find most frequent label among neighbors
- Returns [(label, count)] — use [0][0] for the label
- For tie-breaking: shuffle candidates before selecting

# random.shuffle
shuffle(x) — shuffle list in-place
- Use for random node processing order in asynchronous label propagation

# Modularity formula (Newman-Girvan)
Q = (1/2m) * sum_ij [(A_ij - k_i*k_j/2m) * delta(c_i, c_j)]
- m = total edge count (sum of all weights / 2 for undirected)
- k_i = degree of node i
- delta(c_i, c_j) = 1 if same community, 0 otherwise
