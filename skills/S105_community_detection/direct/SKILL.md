# Community Detection in Networks

## Overview
This skill detects overlapping communities in undirected networks using label propagation or greedy modularity optimization, computing per-community statistics without requiring external graph libraries.

## Workflow
1. Parse arguments for input edge CSV, output JSON, and detection method (label_propagation or modularity)
2. Build adjacency list representation from edge list; compute node degrees and total edge count m
3. For label_propagation: initialize unique labels, iterate asynchronous updates with random node order
4. For modularity: start each node as own community, greedily merge pairs that maximize modularity gain ΔQ
5. Handle overlapping membership: assign node to community if >30% of neighbors share that label
6. Compute per-community statistics: size, internal_edges, density = 2*internal_edges / (size*(size-1))
7. Compute global modularity Q = (1/2m) * Σ[(A_ij - k_i*k_j/2m) * δ(c_i, c_j)]
8. Output JSON with community list, modularity, and node/edge counts

## Common Pitfalls
- **Synchronous update oscillation**: Label propagation with synchronous updates causes flip-flopping between two states — use asynchronous (random node order each iteration)
- **Modularity normalization**: The 1/2m factor is critical; forgetting it gives wrong modularity values
- **Disconnected components**: Each connected component should be treated as a separate initial community
- **Convergence criterion**: Stop when no node changes label for a full iteration, but cap at max iterations to prevent infinite loops
- **Density for size-1 communities**: Define density as 1.0 for single-node communities to avoid division by zero

## Error Handling
- Handle self-loops by ignoring them in community assignment
- Handle isolated nodes (degree 0) as single-node communities
- Validate edge list format and handle missing weight column (default weight = 1)
- Cap iterations at 100 to prevent non-convergence

## Quick Reference
- Modularity: `Q = sum((A[i][j] - deg[i]*deg[j]/(2*m)) for i,j in same_community) / (2*m)`
- ΔQ for merging communities c1, c2: `2*(e_c1c2/2m - sum_c1*sum_c2/(2m)²)`
- Label update: `new_label = mode(neighbor_labels)` with random tie-breaking
- Density: `2 * internal_edges / (size * (size - 1))` for size > 1
