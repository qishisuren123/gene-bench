# Example 1: Define basic quantum gates
import numpy as np

I = np.eye(2, dtype=complex)
X = np.array([[0, 1], [1, 0]], dtype=complex)
Z = np.array([[1, 0], [0, -1]], dtype=complex)
H = np.array([[1, 1], [1, -1]], dtype=complex) / np.sqrt(2)
CNOT = np.array([
    [1, 0, 0, 0],
    [0, 1, 0, 0],
    [0, 0, 0, 1],
    [0, 0, 1, 0],
], dtype=complex)

# Example 2: Create Bell state |Phi+> = (|00> + |11>) / sqrt(2)
# Start with |00>
state = np.array([1, 0, 0, 0], dtype=complex)

# Apply Hadamard to qubit 0
H_I = np.kron(H, I)
state = H_I @ state
print("After H on q0:", state)
# Expected: [1/sqrt(2), 0, 1/sqrt(2), 0]

# Apply CNOT (control=q0, target=q1)
state = CNOT @ state
print("After CNOT:", state)
# Expected: [1/sqrt(2), 0, 0, 1/sqrt(2)] = Bell state

# Example 3: Measurement probabilities
probs = np.abs(state) ** 2
labels = ['00', '01', '10', '11']
for label, p in zip(labels, probs):
    if p > 1e-10:
        print(f"  |{label}>: {p:.4f}")

# Example 4: Simulate measurement (sample outcomes)
def measure(state, n_shots=1000):
    probs = np.abs(state) ** 2
    n_qubits = int(np.log2(len(state)))
    outcomes = np.random.choice(len(state), size=n_shots, p=probs)
    counts = {}
    for o in outcomes:
        label = format(o, f'0{n_qubits}b')
        counts[label] = counts.get(label, 0) + 1
    return counts

results = measure(state, n_shots=1000)
print("Measurement results:", results)
