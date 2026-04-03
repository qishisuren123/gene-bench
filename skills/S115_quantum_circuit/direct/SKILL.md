# Quantum Circuit Simulation

## Overview
This skill simulates quantum circuits by applying gate unitary matrices to a state vector and computing measurement probabilities for each computational basis state, supporting common gates (H, X, Y, Z, CNOT, CZ, RX, RY, RZ, SWAP, T, S).

## Workflow
1. Parse command-line arguments for input JSON (circuit description), output JSON, and shots (default 1024)
2. Load circuit: n_qubits and list of gates, each with gate type, target qubit(s), and optional angle parameter
3. Initialize state vector: 2^n complex array with |0...0⟩ state (first element = 1.0, rest = 0.0)
4. For each gate: build full 2^n × 2^n unitary by tensoring single-qubit gate with identity matrices at appropriate positions; for controlled gates, use projector construction |0⟩⟨0|⊗I + |1⟩⟨1|⊗U
5. Apply gate: state_vector = unitary @ state_vector
6. Compute measurement probabilities: P(outcome) = |amplitude|² for each basis state
7. Sample measurements: draw `shots` samples according to probability distribution; record counts per bitstring
8. Output JSON with n_qubits, state_vector (real and imaginary parts), probabilities (bitstring → probability), measurement_counts, circuit_depth

## Common Pitfalls
- **Qubit ordering convention**: Decide if qubit 0 is most-significant or least-significant bit and be consistent — mismatched ordering produces wrong tensor products
- **Controlled gate construction**: For non-adjacent control-target pairs, must either use SWAP to make them adjacent or directly construct the sparse controlled unitary with proper indexing
- **Numerical precision**: Probabilities must sum to 1.0; accumulated floating-point errors may cause small deviations — normalize after all gates are applied
- **Rotation gate angles**: RX(θ), RY(θ), RZ(θ) use θ/2 in the matrix entries, not θ directly

## Error Handling
- Validate that qubit indices in gates are within [0, n_qubits-1]
- Check that controlled gates have distinct control and target qubits
- Handle unknown gate types by raising clear error with supported gate list

## Quick Reference
- H gate: `1/√2 × [[1, 1], [1, -1]]`
- X gate: `[[0, 1], [1, 0]]`
- CNOT: `|0⟩⟨0| ⊗ I + |1⟩⟨1| ⊗ X` (control, target)
- RX(θ): `[[cos(θ/2), -i·sin(θ/2)], [-i·sin(θ/2), cos(θ/2)]]`
- Full unitary: `I ⊗ ... ⊗ Gate ⊗ ... ⊗ I` (Gate at target qubit position)
- Probability: `probs = np.abs(state_vector)**2`
- Sampling: `np.random.choice(basis_states, size=shots, p=probs)`
- Bell state: H on q0 → CNOT(q0,q1) → |00⟩ and |11⟩ each with probability 0.5
