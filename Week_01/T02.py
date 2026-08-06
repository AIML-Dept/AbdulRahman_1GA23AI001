"""
AML23703 Quantum Computing -- Tutorial 1, Exercise 2  [MEDIUM]
==============================================================
Task : Create a 1-qubit circuit, apply a Hadamard gate, measure it, run
       1024 shots on the simulator and plot the histogram.

Approach
--------
The interesting part of this exercise is NOT that we get roughly 50/50 --
it is that we almost never get exactly 512/512. So instead of just printing
the counts, we also print the size of the sampling error we should EXPECT,
which is 1-sigma = sqrt(p(1-p)/N). That turns "the numbers look about right"
into a statement we can actually defend in the viva.
"""

import matplotlib.pyplot as plt
import numpy as np
from qiskit import QuantumCircuit
from qiskit.visualization import plot_histogram
from qiskit_aer import AerSimulator

SHOTS = 1024

# ---------------------------------------------------------------------
# 1. Build the circuit
# ---------------------------------------------------------------------
qc = QuantumCircuit(1, 1)
qc.h(0)                 # |0>  ->  (|0> + |1>) / sqrt(2)
qc.measure(0, 0)        # collapse onto the computational basis

print("--- Circuit Diagram ---")
print(qc.draw(output="text"))

# ---------------------------------------------------------------------
# 2. Execute on the Aer simulator
# ---------------------------------------------------------------------
simulator = AerSimulator()
counts = simulator.run(qc, shots=SHOTS).result().get_counts()

# ---------------------------------------------------------------------
# 3. Observed vs theoretical
# ---------------------------------------------------------------------
print(f"\n--- Measurement results over {SHOTS} shots ---")
print("Raw counts:", counts)
print()
print(f"{'Outcome':<10}{'Counts':>9}{'Observed':>12}{'Theory':>10}{'Deviation':>12}")

for outcome in ("0", "1"):
    hits = counts.get(outcome, 0)
    observed = hits / SHOTS
    print(f"|{outcome}>{'':<8}{hits:>9}{observed:>11.2%}{0.5:>10.2%}{observed - 0.5:>+12.2%}")

# 1-sigma sampling noise for a fair coin measured N times
sigma = np.sqrt(0.5 * 0.5 / SHOTS)
worst_dev = max(abs(counts.get(o, 0) / SHOTS - 0.5) for o in ("0", "1"))

print(f"\nExpected 1-sigma sampling noise : +/- {sigma:.2%}  ({sigma * SHOTS:.0f} shots)")
print(f"Largest deviation seen          : {worst_dev:.2%}  ({worst_dev / sigma:.2f} sigma)")
print("\nA deviation of one or two sigma is ordinary statistical noise, not a bug.")
print("The Hadamard gate produces an exactly 50/50 state; the finite shot count")
print("is what introduces the wobble.")

# ---------------------------------------------------------------------
# 4. Histogram
# ---------------------------------------------------------------------
plot_histogram(counts, title=f"Hadamard on |0>  --  {SHOTS} shots")
plt.tight_layout()
plt.show()
