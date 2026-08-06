"""
AML23703 Quantum Computing -- Tutorial 3, Exercise 1  [EASY]
============================================================
Task : Implement the X, Y and Z gates individually on separate qubits and
       print the resulting statevectors.

Approach
--------
Applying all three to |0> in one circuit hides a surprise: Z appears to do
nothing. So this script shows each gate's 2x2 matrix and its action on BOTH
basis states, then runs the combined 3-qubit circuit.

The three Pauli gates are all 180-degree rotations of the Bloch sphere, about
the x, y and z axes respectively. Z|0> = |0> is not a bug -- |0> lies ON the
z-axis, and rotating a point about the axis it already sits on moves nothing.
"""

import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import Operator, Statevector


def to_dirac(statevector, n_qubits=1):
    terms = []
    for index, amplitude in enumerate(statevector.data):
        if abs(amplitude) < 1e-9:
            continue
        label = format(index, f"0{n_qubits}b")
        if abs(amplitude.imag) < 1e-9:
            coefficient = f"{amplitude.real:+.4f}"
        else:
            coefficient = f"+({amplitude.real:.4f}{amplitude.imag:+.4f}j)"
        terms.append(f"{coefficient}|{label}>")
    return " ".join(terms) if terms else "0"


GATES = {
    "X": lambda qc: qc.x(0),
    "Y": lambda qc: qc.y(0),
    "Z": lambda qc: qc.z(0),
}

# ---------------------------------------------------------------------
# 1. Each gate on its own, acting on both basis states
# ---------------------------------------------------------------------
for name, apply_gate in GATES.items():
    print("\n" + "=" * 60)
    print(f"PAULI-{name} GATE")
    print("=" * 60)

    qc = QuantumCircuit(1)
    apply_gate(qc)
    matrix = Operator(qc).data
    print("  Matrix:")
    for row in matrix:
        formatted = "  ".join(f"{value.real:+.0f}{value.imag:+.0f}j" for value in row)
        print(f"     [ {formatted} ]")

    for start_label in ("0", "1"):
        initial = Statevector.from_label(start_label)
        final = initial.evolve(Operator(qc))
        print(f"  {name}|{start_label}> = {np.round(final.data, 4)}  =  {to_dirac(final)}")

# ---------------------------------------------------------------------
# 2. What each gate actually does
# ---------------------------------------------------------------------
print("\n" + "=" * 60)
print("SUMMARY")
print("=" * 60)
print("  X : bit flip.    Swaps |0> and |1>.  180 deg rotation about x.")
print("  Y : bit + phase. |0> -> i|1>, |1> -> -i|0>.  180 deg about y.")
print("  Z : phase flip.  Leaves |0> alone, sends |1> -> -|1>.  180 deg about z.")
print("\n  Z looks inert on |0> because |0> sits on the rotation axis itself.")
print("  Apply Z to a SUPERPOSITION and its effect is immediately visible:")

plus = Statevector.from_label("+")
z_circuit = QuantumCircuit(1)
z_circuit.z(0)
minus = plus.evolve(Operator(z_circuit))
print(f"    |+>       = {np.round(plus.data, 4)}  =  {to_dirac(plus)}")
print(f"    Z|+> = |-> = {np.round(minus.data, 4)}  =  {to_dirac(minus)}")

# ---------------------------------------------------------------------
# 3. All three gates together on three separate qubits
# ---------------------------------------------------------------------
print("\n" + "=" * 60)
print("COMBINED 3-QUBIT CIRCUIT (one gate per qubit)")
print("=" * 60)

combined = QuantumCircuit(3)
combined.x(0)      # qubit 0 -> |1>
combined.y(1)      # qubit 1 -> i|1>
combined.z(2)      # qubit 2 -> stays |0>
print(combined.draw(output="text"))

state = Statevector(combined)
print(f"\n  Full statevector : {np.round(state.data, 4)}")
print(f"  Dirac notation   : {to_dirac(state, n_qubits=3)}")
print("\n  Qiskit orders qubits little-endian, so the ket reads q2 q1 q0.")
print("  q0 = |1> (X), q1 = |1> (Y, with an i out front), q2 = |0> (Z did")
print("  nothing) -- giving the single term i|011>.")

probabilities = np.abs(state.data) ** 2
print(f"\n  Only non-zero probability : |011> with P = {probabilities[3]:.4f}")
print("  The factor i is a global phase here, so it is undetectable by")
print("  measurement -- the outcome '011' is certain.")
