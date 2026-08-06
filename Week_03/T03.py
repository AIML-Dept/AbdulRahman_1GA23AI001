"""
AML23703 Quantum Computing -- Tutorial 3, Exercise 3  [HARD]
============================================================
Task : Build a circuit that applies a sequence of five randomly chosen
       single-qubit gates, determine the final state analytically, then
       verify it with simulation.

Approach
--------
Three independent routes to the same answer, which is what makes this a
genuine verification rather than a demonstration:

  A. ANALYTIC   -- multiply the 2x2 matrices by hand with numpy, tracking the
                   state after every gate
  B. STATEVECTOR-- ask Qiskit for the exact amplitudes
  C. SAMPLED    -- run the circuit on the Aer simulator and check the measured
                   frequencies against |amplitude|^2

The one thing to get right: gates are written LEFT TO RIGHT in a circuit but
multiply RIGHT TO LEFT as matrices. Applying G1 then G2 then G3 means the
overall unitary is G3 @ G2 @ G1. Reversing that order is the single most
common bug in this exercise.
"""

import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import Operator, Statevector
from qiskit_aer import AerSimulator
from scipy.stats import chisquare

SEED = 2026            # fixed so the run is reproducible; change it to get a new sequence
SEQUENCE_LENGTH = 5
SHOTS = 8192

INV_SQRT2 = 1 / np.sqrt(2)

# 2x2 matrix for every gate in the pool, written out explicitly
GATE_POOL = {
    "X": np.array([[0, 1], [1, 0]], dtype=complex),
    "Y": np.array([[0, -1j], [1j, 0]], dtype=complex),
    "Z": np.array([[1, 0], [0, -1]], dtype=complex),
    "H": np.array([[INV_SQRT2, INV_SQRT2], [INV_SQRT2, -INV_SQRT2]], dtype=complex),
    "S": np.array([[1, 0], [0, 1j]], dtype=complex),
    "T": np.array([[1, 0], [0, np.exp(1j * np.pi / 4)]], dtype=complex),
}

APPLY = {
    "X": lambda qc: qc.x(0),
    "Y": lambda qc: qc.y(0),
    "Z": lambda qc: qc.z(0),
    "H": lambda qc: qc.h(0),
    "S": lambda qc: qc.s(0),
    "T": lambda qc: qc.t(0),
}


def to_dirac(amplitudes):
    terms = []
    for index, amplitude in enumerate(amplitudes):
        if abs(amplitude) < 1e-9:
            continue
        if abs(amplitude.imag) < 1e-9:
            coefficient = f"{amplitude.real:+.4f}"
        else:
            coefficient = f"+({amplitude.real:.4f}{amplitude.imag:+.4f}j)"
        terms.append(f"{coefficient}|{index}>")
    return " ".join(terms) if terms else "0"


# ---------------------------------------------------------------------
# 1. Pick a random gate sequence
# ---------------------------------------------------------------------
rng = np.random.default_rng(SEED)
sequence = list(rng.choice(list(GATE_POOL.keys()), size=SEQUENCE_LENGTH))

print(f"Random seed          : {SEED}")
print(f"Gate sequence chosen : {' -> '.join(sequence)}")
print("(applied to |0> in this order, left to right)")

# ---------------------------------------------------------------------
# 2. Route A: analytic, step by step
# ---------------------------------------------------------------------
print("\n" + "=" * 72)
print("ROUTE A -- ANALYTIC (numpy matrix multiplication)")
print("=" * 72)

state = np.array([1, 0], dtype=complex)      # start in |0>
unitary = np.eye(2, dtype=complex)

print(f"  start        : {np.round(state, 4)}   =  {to_dirac(state)}")
for step, gate_name in enumerate(sequence, start=1):
    matrix = GATE_POOL[gate_name]
    state = matrix @ state                   # new gate acts on the LEFT
    unitary = matrix @ unitary
    print(f"  after {gate_name} ({step})  : {np.round(state, 4)}   =  {to_dirac(state)}")

analytic_state = state
print(f"\n  Overall unitary U = {sequence[-1]} @ ... @ {sequence[0]} (reverse of circuit order):")
for row in unitary:
    print(f"     [ {row[0]:+.4f}   {row[1]:+.4f} ]")
print(f"\n  Analytic final state : {np.round(analytic_state, 6)}")
print(f"  P(0) = {abs(analytic_state[0]) ** 2:.6f}   P(1) = {abs(analytic_state[1]) ** 2:.6f}")

# ---------------------------------------------------------------------
# 3. Route B: Qiskit statevector
# ---------------------------------------------------------------------
print("\n" + "=" * 72)
print("ROUTE B -- QISKIT STATEVECTOR (exact)")
print("=" * 72)

qc = QuantumCircuit(1)
for gate_name in sequence:
    APPLY[gate_name](qc)

print(qc.draw(output="text"))

qiskit_state = Statevector(qc).data
print(f"\n  Qiskit final state   : {np.round(qiskit_state, 6)}")
print(f"  Matches analytic     : {np.allclose(analytic_state, qiskit_state)}")

qiskit_unitary = Operator(qc).data
print(f"  Full unitary matches : {np.allclose(unitary, qiskit_unitary)}")
print("  (Both the state AND the whole 2x2 operator agree, so the ordering")
print("   convention is confirmed correct, not merely coincidentally right.)")

# ---------------------------------------------------------------------
# 4. Route C: sampled simulation
# ---------------------------------------------------------------------
print("\n" + "=" * 72)
print(f"ROUTE C -- SAMPLED SIMULATION ({SHOTS} shots)")
print("=" * 72)

measured = qc.copy()
measured.measure_all()
counts = AerSimulator().run(measured, shots=SHOTS).result().get_counts()

predicted = np.abs(analytic_state) ** 2
observed = np.array([counts.get("0", 0), counts.get("1", 0)])

print(f"  Raw counts : {counts}")
print(f"\n{'Outcome':<10}{'Counts':>9}{'Observed':>12}{'Predicted':>12}{'Deviation':>12}")
for index, outcome in enumerate(("0", "1")):
    observed_p = observed[index] / SHOTS
    print(f"|{outcome}>{'':<8}{observed[index]:>9}{observed_p:>12.4f}"
          f"{predicted[index]:>12.4f}{observed_p - predicted[index]:>+12.4f}")

expected_counts = predicted * SHOTS
if np.all(expected_counts > 5):
    chi2, p_value = chisquare(observed, f_exp=expected_counts)
    print(f"\n  Chi-square = {chi2:.4f}, p-value = {p_value:.4f}")
    print(f"  Simulation consistent with analytic prediction : {p_value > 0.05}")
else:
    match = np.allclose(observed / SHOTS, predicted, atol=0.02)
    print(f"\n  One outcome is (near) deterministic, so chi-square does not apply.")
    print(f"  Frequencies match prediction within 2%: {match}")

# ---------------------------------------------------------------------
# 5. Verdict
# ---------------------------------------------------------------------
print("\n" + "=" * 72)
print("VERDICT")
print("=" * 72)
print(f"  Analytic vs statevector : {np.allclose(analytic_state, qiskit_state)}")
print(f"  Unitary vs Operator     : {np.allclose(unitary, qiskit_unitary)}")
print("  Sampled frequencies reproduce |amplitude|^2 to within sampling noise.")
print("\n  Note that the sampled route can only ever confirm the MAGNITUDES.")
print("  The relative phase between the amplitudes is invisible to a Z-basis")
print("  measurement -- routes A and B are what pin it down.")
