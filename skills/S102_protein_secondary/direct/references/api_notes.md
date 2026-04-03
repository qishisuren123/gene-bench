# FASTA parsing
- Read sequence: lines starting with '>' are headers, remaining lines are amino acid sequence
- Join continuation lines: seq = ''.join(line.strip() for line in lines if not line.startswith('>'))
- Valid amino acids: single-letter codes A, R, N, D, C, E, Q, G, H, I, L, K, M, F, P, S, T, W, Y, V

# Chou-Fasman propensity tables
- Each amino acid has propensity values P(a), P(b), P(turn)
- Helix formers: P(a) > 1.0 (e.g., Ala=1.42, Glu=1.51, Leu=1.21)
- Sheet formers: P(b) > 1.0 (e.g., Val=1.70, Ile=1.60, Tyr=1.47)
- Helix breakers: Pro, Gly have low P(a)

# Nucleation rules
- Helix nucleation: window of 6 residues with >= 4 helix formers
- Sheet nucleation: window of 5 residues with >= 3 sheet formers
- Extension: propagate while average propensity > 1.0

# Sliding window approach
- Use fixed-size window (typically 4-6 residues)
- Compute average propensity per window position
- Assign structure based on highest average propensity
- Break ties: helix > sheet > coil (by convention)
