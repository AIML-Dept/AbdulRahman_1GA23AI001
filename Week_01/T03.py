"""
AML23703 Quantum Computing -- Tutorial 1, Exercise 3  [HARD]
============================================================
Task : Extend the circuit to 3 qubits in an equal superposition state and
       verify that the probability distribution matches the theoretical
       expectation (uniform 1/8).

Approach
--------
"Matches" needs a definition. A single run at one shot count can only ever
say "close enough, I think". So this script does two things instead:

  1. Sweeps the shot count and shows the maximum deviation from 0.125
     shrinking like 1/sqrt(N) -- i.e. it demonstrates that the mismatch is
     sampling noise, not a wrong circuit.
  2. Runs a chi-square goodness-of-fit test at each shot count, which gives
     a p-value: a formal yes/no on "is this consistent with uniform?".
"""

import matplotlib.pyplot as plt
import numpy as np
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator
from scipy.stats import chisquare

N_QUBITS = 3
N_STATES = 2 ** N_QUBITS          # 8 basis states
IDEAL_P = 1 / N_STATES            # 0.125
SHOT_SWEEP = [64, 256, 1024, 4096, 16384]

# ---------------------------------------------------------------------
# 1. Build the equal-superposition circuit
# ---------------------------------------------------------------------
qc = QuantumCircuit(N_QUBITS, N_QUBITS)
qc.h(range(N_QUBITS))                              # H on every qubit
qc.measure(range(N_QUBITS), range(N_QUBITS))

print("--- Circuit Diagram ---")
print(qc.draw(output="text"))
print(f"\nH on all {N_QUBITS} qubits creates an equal superposition of")
print(f"{N_STATES} basis states, each with theoretical probability {IDEAL_P:.4f}.")

simulator = AerSimulator()
labels = [format(i, f"0{N_QUBITS}b") for i in range(N_STATES)]

# ---------------------------------------------------------------------
# 2. Shot sweep -- does the deviation actually shrink?
# ---------------------------------------------------------------------
print("\n--- Convergence sweep ---")
print(f"{'Shots':>7}{'Max |dev|':>12}{'Chi-square':>13}{'p-value':>10}   Verdict")

max_devs = []
final_counts = None

for shots in SHOT_SWEEP:
    counts = simulator.run(qc, shots=shots).result().get_counts()
    observed = np.array([counts.get(label, 0) for label in labels])
    probs = observed / shots

    expected = np.full(N_STATES, shots / N_STATES)
    chi2, p_value = chisquare(observed, f_exp=expected)

    max_dev = np.max(np.abs(probs - IDEAL_P))
    max_devs.append(max_dev)
    final_counts = counts

    verdict = "consistent with uniform" if p_value > 0.05 else "deviation is significant"
    print(f"{shots:>7}{max_dev:>12.4f}{chi2:>13.3f}{p_value:>10.3f}   {verdict}")

print("\nThe chi-square test compares observed counts against 8 equal bins.")
print("p > 0.05 means we cannot reject the hypothesis that the distribution")
print("is uniform -- which is exactly what we want to see here.")

# ---------------------------------------------------------------------
# 3. Per-state breakdown for the largest run
# ---------------------------------------------------------------------
biggest = SHOT_SWEEP[-1]
print(f"\n--- Per-state breakdown at {biggest} shots ---")
print(f"{'State':<9}{'Counts':>9}{'Observed':>12}{'Theory':>10}{'Deviation':>12}")

for label in labels:
    hits = final_counts.get(label, 0)
    observed_p = hits / biggest
    print(f"|{label}>{'':<3}{hits:>9}{observed_p:>11.4f}{IDEAL_P:>10.4f}{observed_p - IDEAL_P:>+12.4f}")

total = sum(final_counts.values())
print(f"\nTotal shots accounted for : {total} / {biggest}")
print(f"Sum of probabilities      : {sum(final_counts.values()) / biggest:.4f}")

# ---------------------------------------------------------------------
# 4. Plots: measured distribution + convergence curve
# ---------------------------------------------------------------------
fig, axes = plt.subplots(1, 2, figsize=(13, 4.5))

heights = [final_counts.get(label, 0) / biggest for label in labels]
axes[0].bar([f"|{s}>" for s in labels], heights, color="steelblue", alpha=0.85)
axes[0].axhline(IDEAL_P, color="crimson", linestyle="--", label="Theory = 1/8")
axes[0].set_title(f"3-qubit superposition ({biggest} shots)")
axes[0].set_ylabel("Probability")
axes[0].legend()

axes[1].loglog(SHOT_SWEEP, max_devs, "o-", color="darkorange", label="Measured max deviation")
reference = max_devs[0] * np.sqrt(SHOT_SWEEP[0]) / np.sqrt(np.array(SHOT_SWEEP))
axes[1].loglog(SHOT_SWEEP, reference, "k--", alpha=0.6, label="1/sqrt(N) reference")
axes[1].set_title("Deviation from 1/8 shrinks as shots increase")
axes[1].set_xlabel("Number of shots")
axes[1].set_ylabel("Max |observed - 0.125|")
axes[1].legend()
axes[1].grid(True, which="both", alpha=0.3)

plt.tight_layout()
plt.show()
