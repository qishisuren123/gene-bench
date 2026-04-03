# Protein Secondary Structure Prediction

## Overview
This skill predicts protein secondary structure (helix H, sheet E, coil C) from amino acid sequences using residue propensity tables (Chou-Fasman method) with sliding window nucleation and extension.

## Workflow
1. Parse command-line arguments for input FASTA file, output CSV path, and prediction method (chou-fasman or gor)
2. Read FASTA file; extract sequence_id and amino acid sequence for each entry
3. Build propensity lookup tables: helix-formers (A=1.42, E=1.51, L=1.21, M=1.45) and sheet-formers (V=1.70, I=1.60, Y=1.47, F=1.28)
4. Scan sequence with sliding windows: 6-residue window for helix nucleation (average helix propensity > 1.0), 5-residue window for sheet nucleation
5. Extend nucleation sites along the sequence while average propensity exceeds threshold; resolve helix/sheet overlaps by higher propensity
6. Assign remaining residues as coil (C); compute per-sequence composition: helix_pct, sheet_pct, coil_pct
7. Output CSV with columns: sequence_id, length, helix_pct, sheet_pct, coil_pct, structure_string

## Common Pitfalls
- **Window size matters**: Helix nucleation uses 6-residue windows, sheet uses 5-residue windows — using wrong sizes dramatically affects prediction accuracy
- **Sequence edge handling**: Window extends beyond bounds at N/C termini — pad or truncate the scanning range to avoid index errors
- **Propensity table completeness**: Must include all 20 standard amino acids; missing residues default to coil propensity (~0.7)
- **Overlap resolution**: When both helix and sheet are nucleated at same position, compare average propensities — higher wins
- **Short sequences**: Sequences shorter than window size cannot form secondary structures — assign entirely as coil

## Error Handling
- Validate FASTA format: sequences must contain only standard amino acid letters (ACDEFGHIKLMNPQRSTVWY)
- Handle empty sequences by outputting zero percentages and empty structure string
- Check for non-standard amino acids (B, J, O, U, X, Z) and treat as coil-formers

## Quick Reference
- Helix propensity cutoff: average over 6-residue window > 1.0
- Sheet propensity cutoff: average over 5-residue window > 1.0
- Extension: continue while average propensity > threshold (typically 1.0)
- `structure_string`: concatenation of H/E/C per residue position
- Percentages: `helix_pct = count('H') / length * 100`
