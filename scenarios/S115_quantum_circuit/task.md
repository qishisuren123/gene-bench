Write a Python CLI script that simulates small quantum circuits and computes measurement probabilities.

Input: A JSON file describing a quantum circuit: {n_qubits: int, gates: [{type, target, control (optional), angle (optional)}, ...]}.

Requirements:
1. Use argparse: --input JSON, --output JSON, --shots (default 1024 for sampling)
2. Load circuit definition. Supported gates: H (Hadamard), X (Pauli-X/NOT), Y, Z, CNOT, CZ, RX(angle), RY(angle), RZ(angle), SWAP, T, S
3. Represent quantum state as a complex state vector of length 2^n_qubits
4. Initialize to |00...0> state
5. Apply gates sequentially by constructing the full 2^n × 2^n unitary (via tensor products and controlled-gate expansion)
6. Single-qubit gate matrices: H=1/sqrt(2)[[1,1],[1,-1]], X=[[0,1],[1,0]], RX(θ)=[[cos(θ/2),-i*sin(θ/2)],[-i*sin(θ/2),cos(θ/2)]]
7. For multi-qubit gates: use tensor product with identity matrices, swap qubits if non-adjacent
8. Compute measurement probabilities: P(outcome) = |amplitude|^2 for each basis state
9. Sample `shots` measurements according to probabilities
10. Output JSON: n_qubits, state_vector (real+imag), probabilities (dict mapping bitstring to probability), measurement_counts (from sampling), circuit_depth
11. Print summary: most probable states, entanglement indicator (if any qubit pair has non-product state)
