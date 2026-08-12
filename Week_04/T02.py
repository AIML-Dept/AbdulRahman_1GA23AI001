"""
AML23703 Quantum Computing -- Tutorial 4, Exercise 2  [MEDIUM]
=============================================================
Task : Build a Bell state circuit, run it for 1024 shots, and verify that
       the only outcomes observed are 00 and 11.

Approach
--------
"Only 00 and 11" is a claim about two separate things, so both are checked.
The statevector shows that the amplitudes on |01> and |10> are exactly
zero, which is the theoretical statement, and the 1024-shot histogram shows
that neither ever appears in practice. The split between 00 and 11 is then
compared against the expected 512 each, since a fair 50/50 state still
produces a small statistical wobble away from an exact half.
"""

import matplotlib.pyplot as plt
import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit.quantum_info import Statevector
from qiskit.visualization import plot_histogram
from qiskit_aer import AerSimulator

SHOTS = 1024
SEED = 4321

# ---------------------------------------------------------------------
# 1. Build the Bell state |Phi+> = (|00> + |11>) / sqrt(2)
# ---------------------------------------------------------------------
bell = QuantumCircuit(2)
bell.h(0)                # put the control into an equal superposition
bell.cx(0, 1)            # copy that superposition onto the target

print("--- Circuit Diagram ---")
print(bell.draw(output="text"))

# ---------------------------------------------------------------------
# 2. Theory: read the exact amplitudes before any measurement
# ---------------------------------------------------------------------
state = Statevector(bell)
print("\n--- Statevector (exact, no shots involved) ---")
for index, amplitude in enumerate(state.data):
    label = format(index, "02b")
    probability = abs(amplitude) ** 2
    print(f"  |{label}> : amplitude {amplitude.real:+.4f}   "
          f"probability {probability:.4f}")
print(f"  Amplitude on |01> and |10> is exactly zero : "
      f"{np.isclose(abs(state.data[1]), 0) and np.isclose(abs(state.data[2]), 0)}")
print(f"  Norm check : sum of |amplitude|^2 = {np.sum(np.abs(state.data) ** 2):.6f}")

# ---------------------------------------------------------------------
# 3. Practice: measure both qubits, 1024 shots
# ---------------------------------------------------------------------
measured = bell.copy()
measured.measure_all()

simulator = AerSimulator(seed_simulator=SEED)
job = simulator.run(transpile(measured, simulator), shots=SHOTS)
counts = job.result().get_counts()

print(f"\n--- Measurement results ({SHOTS} shots) ---")
for outcome in sorted(counts):
    share = 100 * counts[outcome] / SHOTS
    print(f"  {outcome} : {counts[outcome]:4d} shots  ({share:5.2f} %)")

# ---------------------------------------------------------------------
# 4. Verify the claim
# ---------------------------------------------------------------------
forbidden = {"01", "10"}
observed = set(counts)
print("\n--- Verification ---")
print(f"  Outcomes observed              : {sorted(observed)}")
print(f"  Forbidden outcomes 01 / 10 seen: {sorted(observed & forbidden) or 'none'}")
print(f"  Only 00 and 11 appeared        : {observed <= {'00', '11'}}")
print(f"  Total shots accounted for      : {sum(counts.values())} of {SHOTS}")

expected = SHOTS / 2
deviation = abs(counts.get("00", 0) - expected)
print(f"  Expected split                 : {expected:.0f} / {expected:.0f}")
percent = 100 * deviation / SHOTS
print(f"  Deviation from an even split   : {deviation:.0f} shots ({percent:.2f} %)")
print("  A small deviation is ordinary sampling noise, not a fault in the circuit.")

# ---------------------------------------------------------------------
# 5. Histogram
# ---------------------------------------------------------------------
plot_histogram(counts, title=f"Bell state |Phi+> -- {SHOTS} shots")
plt.show()
