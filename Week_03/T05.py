"""
AML23703 Quantum Computing -- Tutorial 3, Exercise 5  [CHALLENGE]
=================================================================
Task : Prove gate equivalence -- show that HZH (Hadamard-Z-Hadamard) is
       equivalent to the X gate, both analytically and via circuit simulation.

Approach
--------
"Equivalent" for quantum gates means the two unitaries act identically on
EVERY input state, not just on |0>. A circuit that agreed on |0> alone would
prove nothing -- so this script checks four increasingly strict conditions:

  1. Matrix algebra   -- multiply H @ Z @ H by hand and compare with X
  2. Operator level   -- Qiskit's Operator.equiv(), which covers all inputs
  3. Basis states     -- act on |0> and |1> and compare statevectors
  4. Superposition    -- act on |+>, |->, |+i>, which is where a wrong answer
                         would finally show up
  5. Measurement      -- 8192 shots, confirming it behaves as X in practice

The underlying reason it works: H is the gate that swaps the x- and z-axes of
the Bloch sphere. Conjugating by H therefore turns a rotation about z into the
same rotation about x -- and X, Y, Z are all 180-degree rotations. So HZH = X
is not a coincidence, it is a change of coordinates.
"""

import numpy as np
from qiskit import QuantumCircuit
from qiskit.circuit.library import XGate, YGate, ZGate
from qiskit.quantum_info import Operator, Statevector
from qiskit_aer import AerSimulator

SHOTS = 8192
INV_SQRT2 = 1 / np.sqrt(2)

H = np.array([[INV_SQRT2, INV_SQRT2], [INV_SQRT2, -INV_SQRT2]], dtype=complex)
X = np.array([[0, 1], [1, 0]], dtype=complex)
Y = np.array([[0, -1j], [1j, 0]], dtype=complex)
Z = np.array([[1, 0], [0, -1]], dtype=complex)


def show_matrix(name, matrix):
    print(f"  {name} =")
    for row in matrix:
        print(f"      [ {row[0]:+.4f}   {row[1]:+.4f} ]")


# ---------------------------------------------------------------------
# PROOF 1 -- matrix algebra
# ---------------------------------------------------------------------
print("=" * 70)
print("PROOF 1 -- ANALYTIC MATRIX MULTIPLICATION")
print("=" * 70)
print("  Circuit order H then Z then H means the product is H @ Z @ H")
print("  (rightmost matrix acts first). H is its own inverse, so no")
print("  dagger is needed here.\n")

product = H @ Z @ H
show_matrix("H @ Z @ H", product)
print()
show_matrix("X        ", X)

print(f"\n  Element-wise equal : {np.allclose(product, X)}")
print(f"  H is self-inverse  : {np.allclose(H @ H, np.eye(2))}")

# ---------------------------------------------------------------------
# PROOF 2 -- operator equivalence in Qiskit
# ---------------------------------------------------------------------
print("\n" + "=" * 70)
print("PROOF 2 -- QISKIT OPERATOR EQUIVALENCE")
print("=" * 70)

hzh = QuantumCircuit(1)
hzh.h(0)
hzh.z(0)
hzh.h(0)

print(hzh.draw(output="text"))

hzh_operator = Operator(hzh)
print(f"\n  Operator(HZH) matrix :\n")
show_matrix("  ", hzh_operator.data)
print(f"\n  Operator.equiv(XGate())          : {hzh_operator.equiv(Operator(XGate()))}")
print(f"  Exact matrix match (no phase fix): {np.allclose(hzh_operator.data, X)}")
print("\n  .equiv() allows a global phase; here the match is exact even without")
print("  that leniency, so the equivalence is as strong as it gets.")

# ---------------------------------------------------------------------
# PROOF 3 & 4 -- action on a full set of test states
# ---------------------------------------------------------------------
print("\n" + "=" * 70)
print("PROOF 3 & 4 -- ACTION ON BASIS AND SUPERPOSITION STATES")
print("=" * 70)
print("  Agreeing on |0> alone proves nothing. A genuine equivalence must")
print("  hold for superpositions too, so those are included.\n")

x_circuit = QuantumCircuit(1)
x_circuit.x(0)

test_labels = ["0", "1", "+", "-", "r", "l"]
readable = {"0": "|0>", "1": "|1>", "+": "|+>", "-": "|->", "r": "|+i>", "l": "|-i>"}

print(f"{'Input':<8}{'HZH result':>26}{'X result':>26}{'Match':>8}")
all_match = True
for label in test_labels:
    initial = Statevector.from_label(label)
    via_hzh = initial.evolve(hzh_operator)
    via_x = initial.evolve(Operator(x_circuit))
    match = np.allclose(via_hzh.data, via_x.data)
    all_match &= match
    print(f"{readable[label]:<8}{str(np.round(via_hzh.data, 4)):>26}"
          f"{str(np.round(via_x.data, 4)):>26}{str(match):>8}")

print(f"\n  Identical on all {len(test_labels)} test states : {all_match}")

# ---------------------------------------------------------------------
# PROOF 5 -- measurement in simulation
# ---------------------------------------------------------------------
print("\n" + "=" * 70)
print(f"PROOF 5 -- SIMULATED MEASUREMENT ({SHOTS} shots)")
print("=" * 70)

simulator = AerSimulator()
print(f"{'Input':<8}{'Circuit':<10}{'Counts':>28}")

for start in ("0", "1"):
    for name, gates in (("HZH", ["h", "z", "h"]), ("X", ["x"])):
        qc = QuantumCircuit(1, 1)
        if start == "1":
            qc.x(0)                       # prepare |1> first
        for gate in gates:
            getattr(qc, gate)(0)
        qc.measure(0, 0)
        counts = simulator.run(qc, shots=SHOTS).result().get_counts()
        print(f"|{start}>{'':<5}{name:<10}{str(counts):>28}")

print("\n  HZH flips |0> to '1' and |1> to '0' on every single shot, exactly")
print("  like X. Deterministic outcomes, so there is no sampling noise to")
print("  argue about.")

# ---------------------------------------------------------------------
# BONUS -- the general rule
# ---------------------------------------------------------------------
print("\n" + "=" * 70)
print("BONUS -- THE PATTERN BEHIND THE RESULT")
print("=" * 70)

print(f"  H @ Z @ H == X   : {np.allclose(H @ Z @ H, X)}")
print(f"  H @ X @ H == Z   : {np.allclose(H @ X @ H, Z)}")
print(f"  H @ Y @ H == -Y  : {np.allclose(H @ Y @ H, -Y)}")

print("\n  H swaps the x- and z-axes of the Bloch sphere and reverses y.")
print("  Conjugating any gate by H therefore relabels its rotation axis:")
print("  a 180-degree rotation about z becomes a 180-degree rotation about x.")
print("\n  Practical consequence: this is precisely how a Z-basis measurement")
print("  is turned into an X-basis measurement (put an H in front of it), and")
print("  it is the standard trick for rewriting a circuit into whatever native")
print("  gate set a given piece of hardware actually supports.")

verdict = (np.allclose(product, X) and hzh_operator.equiv(Operator(XGate())) and all_match)
print("\n" + "=" * 70)
print(f"FINAL VERDICT -- HZH is equivalent to X : {verdict}")
print("=" * 70)
