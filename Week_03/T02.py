"""
AML23703 Quantum Computing -- Tutorial 3, Exercise 2  [MEDIUM]
==============================================================
Task : Combine H and Z gates to construct the |-> state and verify it
       experimentally through simulation.

Approach
--------
Verification here is subtler than it looks. If you build |-> and measure it
in the usual Z basis you get 50/50 -- but so does |+>. A Z-basis measurement
literally CANNOT tell the two apart, so it verifies nothing.

The honest experiment is a 2x2 matrix: prepare both |+> and |->, measure each
in both the Z and the X basis, and show that only the X basis separates them.
That is also the practical meaning of "measuring in the X basis": apply H
first (it maps |+> -> |0> and |-> -> |1>), then measure normally.
"""

import matplotlib.pyplot as plt
import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector
from qiskit.visualization import plot_histogram
from qiskit_aer import AerSimulator

SHOTS = 4096
simulator = AerSimulator()


def prepare(which):
    """|+> = H|0>;  |-> = Z H |0>."""
    qc = QuantumCircuit(1)
    qc.h(0)
    if which == "-":
        qc.z(0)
    return qc


# ---------------------------------------------------------------------
# 1. Build |-> and inspect it exactly
# ---------------------------------------------------------------------
minus_circuit = prepare("-")
print("--- Circuit for |-> : H then Z ---")
print(minus_circuit.draw(output="text"))

minus_state = Statevector(minus_circuit)
plus_state = Statevector(prepare("+"))

print(f"\n  |+> statevector : {np.round(plus_state.data, 4)}")
print(f"  |-> statevector : {np.round(minus_state.data, 4)}")
print(f"  Target |->      : {np.round(Statevector.from_label('-').data, 4)}")
print(f"  Matches target  : {minus_state.equiv(Statevector.from_label('-'))}")
print("\n  H put the qubit into an equal superposition; Z then flipped the sign")
print("  of the |1> amplitude only. The magnitudes are untouched, so the two")
print("  states differ purely by a RELATIVE phase of -1.")

# ---------------------------------------------------------------------
# 2. The 2x2 experiment
# ---------------------------------------------------------------------
def measure(which, basis):
    qc = prepare(which)
    if basis == "X":
        qc.h(0)               # rotate the X basis onto the Z basis
    qc.measure_all()
    return simulator.run(qc, shots=SHOTS).result().get_counts()


results = {}
print(f"\n--- Experiment: both states, both bases, {SHOTS} shots each ---")
print(f"{'State':<8}{'Basis':<8}{'counts 0':>10}{'counts 1':>10}{'P(0)':>9}{'P(1)':>9}")

for which in ("+", "-"):
    for basis in ("Z", "X"):
        counts = measure(which, basis)
        results[(which, basis)] = counts
        zeros, ones = counts.get("0", 0), counts.get("1", 0)
        print(f"|{which}>{'':<5}{basis:<8}{zeros:>10}{ones:>10}"
              f"{zeros / SHOTS:>9.4f}{ones / SHOTS:>9.4f}")

# ---------------------------------------------------------------------
# 3. Read the table
# ---------------------------------------------------------------------
z_plus = results[("+", "Z")].get("1", 0) / SHOTS
z_minus = results[("-", "Z")].get("1", 0) / SHOTS
x_plus = results[("+", "X")].get("0", 0) / SHOTS
x_minus = results[("-", "X")].get("1", 0) / SHOTS

print("\n--- Reading the results ---")
print(f"  Z basis: |+> gives P(1) = {z_plus:.4f}, |-> gives P(1) = {z_minus:.4f}")
print("           Both are 50/50. The Z basis is BLIND to the relative phase,")
print("           so it cannot confirm we built |-> rather than |+>.")
print(f"  X basis: |+> gives '0' {x_plus:.2%} of the time")
print(f"           |-> gives '1' {x_minus:.2%} of the time")
print("           Both are deterministic and opposite. This is the proof.")

verified = x_minus > 0.99 and x_plus > 0.99
print(f"\n  |-> construction verified experimentally : {verified}")

print("\n  Mechanism: the second H interferes the two paths. For |-> the |0>")
print("  branches cancel and the |1> branches reinforce, so the outcome is")
print("  forced. A phase that was invisible one moment becomes a certainty")
print("  the next -- that interference is the engine behind every quantum")
print("  algorithm that beats its classical counterpart.")

# ---------------------------------------------------------------------
# 4. Plot the four histograms
# ---------------------------------------------------------------------
fig, axes = plt.subplots(2, 2, figsize=(11, 7))
for row, which in enumerate(("+", "-")):
    for col, basis in enumerate(("Z", "X")):
        plot_histogram(results[(which, basis)], ax=axes[row][col])
        axes[row][col].set_title(f"|{which}> measured in the {basis} basis")

plt.tight_layout()
plt.show()
