"""
AML23703 Quantum Computing -- Tutorial 4, Exercise 3  [HARD]
===========================================================
Task : Implement a 3-qubit GHZ state and confirm perfect three-way
       correlation in the measurement results.

Approach
--------
"Perfect three-way correlation" means that in every single shot all three
qubits agree, so the script checks it shot by shot rather than only looking
at the totals. Two further checks are added because the shot totals alone
would not distinguish a GHZ state from an ordinary classical coin that is
copied onto three bits: the pairwise correlation <ZiZj> is computed for all
three pairs, and each qubit is shown to be individually random even though
the three together are perfectly locked to one another.
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
# 1. Build the GHZ state (|000> + |111>) / sqrt(2)
# ---------------------------------------------------------------------
ghz = QuantumCircuit(3)
ghz.h(0)                 # one qubit into superposition
ghz.cx(0, 1)             # entangle it with the second
ghz.cx(0, 2)             # and with the third -- one shared superposition

print("--- Circuit Diagram ---")
print(ghz.draw(output="text"))
print(f"\n  Circuit depth : {ghz.depth()}    Gate count : {dict(ghz.count_ops())}")

# ---------------------------------------------------------------------
# 2. Exact state before measurement
# ---------------------------------------------------------------------
state = Statevector(ghz)
print("\n--- Statevector ---")
for index, amplitude in enumerate(state.data):
    if abs(amplitude) > 1e-9:
        print(f"  |{format(index, '03b')}> : amplitude {amplitude.real:+.4f}   "
              f"probability {abs(amplitude) ** 2:.4f}")
print(f"  Non-zero amplitudes : {int(np.sum(np.abs(state.data) > 1e-9))} out of 8")
print(f"  Norm check          : {np.sum(np.abs(state.data) ** 2):.6f}")

# ---------------------------------------------------------------------
# 3. Measure all three qubits, 1024 shots
# ---------------------------------------------------------------------
measured = ghz.copy()
measured.measure_all()

simulator = AerSimulator(seed_simulator=SEED)
job = simulator.run(transpile(measured, simulator), shots=SHOTS)
counts = job.result().get_counts()

print(f"\n--- Measurement results ({SHOTS} shots) ---")
for outcome in sorted(counts):
    share = 100 * counts[outcome] / SHOTS
    print(f"  {outcome} : {counts[outcome]:4d} shots  ({share:5.2f} %)")

# ---------------------------------------------------------------------
# 4. Three-way correlation, checked shot by shot
# ---------------------------------------------------------------------
agreeing = sum(n for outcome, n in counts.items() if len(set(outcome)) == 1)
print("\n--- Three-way correlation ---")
print(f"  Shots where all three qubits agree : {agreeing} of {SHOTS} "
      f"({100 * agreeing / SHOTS:.2f} %)")
print(f"  Mixed outcomes (001, 010, ... 110) : {SHOTS - agreeing}")
print(f"  Perfect three-way correlation      : {agreeing == SHOTS}")

# Bit i of the label counted from the right is qubit i (Qiskit ordering).
def correlation(first, second):
    """<Zi Zj> estimated from the counts: +1 if the pair always agrees."""
    total = 0
    for outcome, n in counts.items():
        bit_i = int(outcome[::-1][first])
        bit_j = int(outcome[::-1][second])
        total += n * (1 if bit_i == bit_j else -1)
    return total / SHOTS

print("\n  Pairwise correlation <Zi Zj>:")
for first, second in ((0, 1), (0, 2), (1, 2)):
    print(f"     q{first} with q{second} : {correlation(first, second):+.4f}")

# ---------------------------------------------------------------------
# 5. Each qubit on its own is still completely random
# ---------------------------------------------------------------------
print("\n--- Each qubit taken individually ---")
for qubit in range(3):
    ones = sum(n for outcome, n in counts.items() if outcome[::-1][qubit] == "1")
    print(f"  q{qubit} : P(1) = {ones / SHOTS:.4f}   (a fair coin on its own)")
print("  Knowing one qubit fixes the other two, yet no qubit is predictable alone.")
print("  That is the part a classical shared random bit cannot reproduce in full.")

# ---------------------------------------------------------------------
# 6. Histogram
# ---------------------------------------------------------------------
plot_histogram(counts, title=f"GHZ state -- {SHOTS} shots")
plt.show()
