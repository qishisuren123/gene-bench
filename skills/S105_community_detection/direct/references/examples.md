# Example 1: Asynchronous label propagation
import random
from collections import defaultdict, Counter

def build_graph(edges):
    adj = defaultdict(list)
    for u, v in edges:
        adj[u].append(v)
        adj[v].append(u)
    return adj

def label_propagation(adj, max_iter=100):
    labels = {node: node for node in adj}
    nodes = list(adj.keys())
    for _ in range(max_iter):
        random.shuffle(nodes)
        changed = False
        for node in nodes:
            if not adj[node]:
                continue
            neighbor_labels = [labels[n] for n in adj[node]]
            counts = Counter(neighbor_labels)
            max_count = max(counts.values())
            candidates = [l for l, c in counts.items() if c == max_count]
            new_label = random.choice(candidates)
            if new_label != labels[node]:
                labels[node] = new_label
                changed = True
        if not changed:
            break
    return labels

# Example 2: Modularity computation
def compute_modularity(adj, labels):
    m = sum(len(neighbors) for neighbors in adj.values()) / 2
    if m == 0:
        return 0.0
    Q = 0.0
    deg = {n: len(adj[n]) for n in adj}
    for i in adj:
        for j in adj[i]:
            if labels[i] == labels[j]:
                Q += 1 - deg[i] * deg[j] / (2 * m)
    return Q / (2 * m)
