"""
AML23703 Quantum Computing -- Tutorial 4, Exercise 5  [CHALLENGE]
================================================================
Task : Design a circuit producing a chosen arbitrary 2-qubit entangled
       state, other than the four standard Bell states, and verify it by
       state tomography (statevector inspection).

Approach
--------
The state chosen is the partially entangled |psi> = cos(t)|00> + sin(t)|11>
with t = 30 degrees, giving amplitudes 0.8660 and 0.5000. It is built by
replacing the Hadamard of the Bell recipe with RY(2t), so the control qubit
starts off unevenly weighted and the CNOT then carries that imbalance
across to the second qubit.

Three things are then checked. The state is confirmed to be entangled, it
is confirmed not to be any of the four Bell states, and the full density
matrix is reconstructed from the sixteen Pauli expectation values, which is
what state tomography actually computes.
"""

import matplotlib.pyplot as plt
import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit.quantum_info import (
    DensityMatrix, Pauli, Statevector, partial_trace, state_fidelity
)
from qiskit.visualization import plot_histogram
from qiskit_aer import AerSimulator

THETA = np.pi / 6        # 30 degrees
SHOTS = 1024
SEED = 4321

# ---------------------------------------------------------------------
# 1. Build the state
# ---------------------------------------------------------------------
qc = QuantumCircuit(2)
qc.ry(2 * THETA, 0)      # 0.8660|0> + 0.5000|1> on the control
qc.cx(0, 1)              # carry the imbalance across

print("--- Circuit Diagram ---")
print(qc.draw(output="text"))
print(f"\n  Chosen angle t = {np.degrees(THETA):.0f} degrees")
print(f"  Target state   : {np.cos(THETA):.4f}|00> + {np.sin(THETA):.4f}|11>")

state = Statevector(qc)
target = np.array([np.cos(THETA), 0, 0, np.sin(THETA)])

print("\n--- Statevector produced ---")
for index, amplitude in enumerate(state.data):
    probability = abs(amplitude) ** 2
    print(f"  |{format(index, '02b')}> : amplitude {amplitude.real:+.4f}   "
          f"probability {probability:.4f}")
print(f"  Matches the target amplitudes : {np.allclose(state.data, target)}")

# ---------------------------------------------------------------------
# 2. Is it entangled, and how strongly?
# ---------------------------------------------------------------------
a, b, c, d = state.data
concurrence = 2 * abs(a * d - b * c)
reduced = partial_trace(state, [1])
purity = np.real(np.trace(reduced.data @ reduced.data))

print("\n--- Entanglement check ---")
print(f"  Concurrence            : {concurrence:.4f}   (0 = separable, 1 = maximal)")
print(f"  Purity of qubit 0 alone: {purity:.4f}   (below 1 means entangled)")
print(f"  Entangled              : {concurrence > 1e-9}")
print(f"  Maximally entangled    : {np.isclose(concurrence, 1.0)}")

# ---------------------------------------------------------------------
# 3. Confirm it is not one of the four standard Bell states
# ---------------------------------------------------------------------
r2 = 1 / np.sqrt(2)
bell_states = {
    "|Phi+> = (|00>+|11>)/sqrt2": [r2, 0, 0, r2],
    "|Phi-> = (|00>-|11>)/sqrt2": [r2, 0, 0, -r2],
    "|Psi+> = (|01>+|10>)/sqrt2": [0, r2, r2, 0],
    "|Psi-> = (|01>-|10>)/sqrt2": [0, r2, -r2, 0],
}
print("\n--- Fidelity against the four Bell states ---")
for name, vector in bell_states.items():
    print(f"  {name} : {state_fidelity(state, Statevector(vector)):.4f}")
print("  None reaches 1.0, so the state is entangled but is not a Bell state.")

# ---------------------------------------------------------------------
# 4. State tomography -- rebuild the density matrix from Pauli measurements
# ---------------------------------------------------------------------
# Any 2-qubit density matrix can be written as
#     rho = (1/4) * sum over all 16 Pauli pairs of <P> * P
# so measuring those 16 expectation values determines the state completely.
labels = [first + second for first in "IXYZ" for second in "IXYZ"]
expectations = {label: state.expectation_value(Pauli(label)).real for label in labels}

print("\n--- Pauli expectation values (the tomography data) ---")
for label in labels:
    if abs(expectations[label]) > 1e-9:
        print(f"  <{label}> = {expectations[label]:+.4f}")
print(f"  {sum(abs(v) > 1e-9 for v in expectations.values())} of 16 are non-zero; "
      "the rest are exactly zero.")

terms = (expectations[label] * Pauli(label).to_matrix() for label in labels)
reconstructed = sum(terms) / 4
true_rho = DensityMatrix(state).data

print("\n--- Reconstruction ---")
print("  Reconstructed density matrix (real part):")
for row in np.round(np.real(reconstructed), 4):
    print("    " + "  ".join(f"{value:+.4f}" for value in row))
print(f"  Max difference from the true density matrix : "
      f"{np.max(np.abs(reconstructed - true_rho)):.2e}")
print(f"  Fidelity of reconstruction : "
      f"{state_fidelity(DensityMatrix(reconstructed), state):.6f}")
print("  The two off-diagonal corners are the entanglement; a separable state")
print("  would have zeros there while keeping the same diagonal.")

# ---------------------------------------------------------------------
# 5. Sanity check against 1024 actual shots
# ---------------------------------------------------------------------
measured = qc.copy()
measured.measure_all()
simulator = AerSimulator(seed_simulator=SEED)
job = simulator.run(transpile(measured, simulator), shots=SHOTS)
counts = job.result().get_counts()

print(f"\n--- Measured counts ({SHOTS} shots) ---")
for outcome in sorted(counts):
    observed = counts[outcome] / SHOTS
    theory = abs(state.data[int(outcome, 2)]) ** 2
    print(f"  {outcome} : {counts[outcome]:4d}   observed {observed:.4f}   "
          f"theory {theory:.4f}")
print(f"  Only |00> and |11> appeared : {set(counts) <= {'00', '11'}}")
print("  The correlation is still perfect; only the 50/50 split is gone.")

plot_histogram(counts, title="Partially entangled state -- 1024 shots")
plt.show()
