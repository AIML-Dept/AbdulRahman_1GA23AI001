"""
AML23703 Quantum Computing -- Tutorial 2, Exercise 3  [HARD]
============================================================
Task : Construct a 2-qubit statevector representing an equal superposition of
       all four basis states and verify the amplitudes sum to unity.

Approach
--------
"Verify" is done three independent ways so the result is not just taken on
trust from one API call:

  1. Direct arithmetic  -- sum |amplitude|^2 computed by hand with numpy
  2. Qiskit's own check -- Statevector.is_valid()
  3. First principles   -- rebuild the state as the tensor product
                           |+> (x) |+> using numpy.kron and compare

Point 3 is the important one for the viva: a 2-qubit uniform superposition is
not a new object, it is just two independent single-qubit superpositions
combined with a tensor product. Note that (a) 'amplitudes sum to unity' means
the sum of their SQUARED MAGNITUDES is 1 -- the raw amplitudes here sum to 2 --
and (b) this state is a product state, NOT entangled.
"""

import matplotlib.pyplot as plt
import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector
from qiskit.visualization import plot_histogram, plot_state_qsphere

N_QUBITS = 2

# ---------------------------------------------------------------------
# 1. Build the state
# ---------------------------------------------------------------------
qc = QuantumCircuit(N_QUBITS)
qc.h(0)
qc.h(1)

state = Statevector(qc)
amplitudes = state.data

print("--- Circuit Diagram ---")
print(qc.draw(output="text"))

# ---------------------------------------------------------------------
# 2. Amplitude / probability table
# ---------------------------------------------------------------------
print("\n--- Amplitudes and probabilities ---")
print(f"{'Basis':<10}{'Amplitude':>22}{'|amp|':>10}{'|amp|^2':>11}{'Cumulative':>13}")

running_total = 0.0
for index, amplitude in enumerate(amplitudes):
    label = format(index, f"0{N_QUBITS}b")
    probability = abs(amplitude) ** 2
    running_total += probability
    print(f"|{label}>{'':<5}{amplitude:>22.6f}{abs(amplitude):>10.4f}"
          f"{probability:>11.4f}{running_total:>13.4f}")

# ---------------------------------------------------------------------
# 3. Verification 1 -- direct arithmetic
# ---------------------------------------------------------------------
norm = np.sum(np.abs(amplitudes) ** 2)
raw_sum = np.sum(amplitudes)

print("\n--- Verification 1: direct arithmetic ---")
print(f"  Sum of squared magnitudes : {norm:.10f}")
print(f"  Equals 1 (within 1e-9)?   : {np.isclose(norm, 1.0)}")
print(f"  Sum of raw amplitudes     : {raw_sum:.4f}   <-- NOT 1, and it should not be.")
print("  Normalisation constrains the squared magnitudes (total probability),")
print("  never the amplitudes themselves.")

# ---------------------------------------------------------------------
# 4. Verification 2 -- Qiskit's built-in validity check
# ---------------------------------------------------------------------
print("\n--- Verification 2: Qiskit's own check ---")
print(f"  Statevector.is_valid() : {state.is_valid()}")
pretty = ", ".join(f"|{k}>: {float(v):.4f}" for k, v in state.probabilities_dict().items())
print(f"  Probabilities          : {pretty}")

# ---------------------------------------------------------------------
# 5. Verification 3 -- rebuild from first principles
# ---------------------------------------------------------------------
plus = np.array([1, 1]) / np.sqrt(2)          # |+> = H|0>
manual = np.kron(plus, plus)                   # |+> (x) |+>

print("\n--- Verification 3: tensor product from first principles ---")
print(f"  |+>                     : {np.round(plus, 4)}")
print(f"  |+> (x) |+> via kron    : {np.round(manual, 4)}")
print(f"  Qiskit statevector      : {np.round(amplitudes, 4)}")
print(f"  Identical?              : {np.allclose(manual, amplitudes)}")
print("\n  Because the state factorises into a product of two single-qubit")
print("  states, it is NOT entangled -- measuring qubit 0 tells you nothing")
print("  about qubit 1. Each amplitude is 1/2 = (1/sqrt(2)) x (1/sqrt(2)).")

# ---------------------------------------------------------------------
# 6. Scaling check: the pattern for n qubits
# ---------------------------------------------------------------------
print("\n--- Scaling ---")
print(f"{'Qubits':>8}{'Basis states':>15}{'Amplitude each':>18}{'Probability each':>19}")
for n in range(1, 6):
    size = 2 ** n
    print(f"{n:>8}{size:>15}{1 / np.sqrt(size):>18.6f}{1 / size:>19.6f}")
print("\n  n qubits hold 2^n amplitudes at once. That exponential growth is the")
print("  resource quantum algorithms exploit -- and the reason simulating them")
print("  classically becomes impossible past roughly 50 qubits.")

# ---------------------------------------------------------------------
# 7. Visualisations: probability histogram and Q-sphere
# ---------------------------------------------------------------------
plot_histogram(state.probabilities_dict(), title="Equal superposition of all 4 basis states")
plt.tight_layout()
plt.show()

plot_state_qsphere(state)
plt.suptitle("Q-sphere: 4 equal amplitudes, all with phase 0")
plt.show()
