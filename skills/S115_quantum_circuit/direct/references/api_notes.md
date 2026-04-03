# Qubit state representation
- Single qubit: 2-element complex vector [alpha, beta], |alpha|^2 + |beta|^2 = 1
- |0> = [1, 0], |1> = [0, 1]
- n qubits: 2^n element state vector
- Two qubits: |00> = [1,0,0,0], |01> = [0,1,0,0], etc.

# Common gate matrices (2x2)
- Identity: I = [[1,0],[0,1]]
- Pauli-X (NOT): X = [[0,1],[1,0]]
- Pauli-Z: Z = [[1,0],[0,-1]]
- Hadamard: H = (1/sqrt(2)) * [[1,1],[1,-1]]

# Two-qubit gates
- CNOT (control=0, target=1): 4x4 matrix
  [[1,0,0,0],[0,1,0,0],[0,0,0,1],[0,0,1,0]]
- Gate on qubit i in n-qubit system: use tensor (Kronecker) products
  e.g., H on qubit 0 of 2-qubit: np.kron(H, I)
  e.g., X on qubit 1 of 2-qubit: np.kron(I, X)

# numpy.kron
np.kron(a, b)
- Kronecker product of two arrays
- For 2x2 matrices: returns 4x4 matrix
- Chain: np.kron(np.kron(A, B), C) for 3-qubit systems

# Measurement probabilities
- prob(state i) = |amplitude_i|^2
- Use np.abs(state)**2 to get probability distribution
- Collapse: after measuring outcome i, state becomes basis vector |i>

# Circuit simulation
- Apply gate: new_state = gate_matrix @ state_vector
- Sequential gates: multiply in order (left-to-right in circuit)
