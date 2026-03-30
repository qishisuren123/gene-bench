Write a Python CLI script that predicts protein secondary structure (helix, sheet, coil) from amino acid sequence.

Input: A FASTA file containing one or more protein sequences.

Requirements:
1. Use argparse: --input for FASTA file, --output for CSV results, --method (choices: "chou_fasman", "gор", default "chou_fasman")
2. Parse FASTA file to extract sequence IDs and amino acid sequences
3. For Chou-Fasman method: use propensity tables for alpha-helix and beta-sheet prediction
   - Helix propensity > 1.0 for: A(1.42), E(1.51), L(1.21), M(1.45), K(1.16), R(0.98), Q(1.11), H(1.00)
   - Sheet propensity > 1.0 for: V(1.70), I(1.60), Y(1.47), F(1.28), W(1.19), L(1.30), T(1.19)
   - Use sliding window of size 6 for helix nucleation, size 5 for sheet nucleation
4. For GOR method: use information theory-based single residue statistics (simplified)
5. Assign each residue: H (helix), E (sheet), or C (coil)
6. Calculate per-sequence statistics: %helix, %sheet, %coil
7. Output CSV with columns: sequence_id, length, helix_pct, sheet_pct, coil_pct, structure_string
8. Print summary: average secondary structure composition across all sequences
