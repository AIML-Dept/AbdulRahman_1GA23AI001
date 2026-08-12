"""
AML23703 Quantum Computing -- Tutorial 4, Exercise 1  [EASY]
===========================================================
Task : Implement a CNOT gate circuit with the control qubit in state |1>
       and verify that the target qubit flips.

Approach
--------
One run only shows one row of the truth table, so the script does two
things. It runs the asked-for case (control = |1>) and prints the state
before and after, and it then sweeps all four basis inputs so the full
truth table is produced by the circuit itself rather than copied from the
notes. Qiskit labels basis states as |q1 q0>, i.e. the rightmost character
is qubit 0, so every label below is printed in that order.
"""

import matplotlib.pyplot as plt
import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import Operator, Statevector

CONTROL, TARGET = 0, 1


def label_of(statevector):
    """Return the basis-state label of a state that sits on one basis vector."""
    index = int(np.argmax(np.abs(statevector.data)))
    return format(index, "02b")          # "q1q0"


def build(control_bit, target_bit, apply_cnot=True):
    """Prepare |control, target>, then optionally apply CNOT(q0 -> q1)."""
    qc = QuantumCircuit(2)
    if control_bit:
        qc.x(CONTROL)
    if target_bit:
        qc.x(TARGET)
    if apply_cnot:
        qc.cx(CONTROL, TARGET)
    return qc

# ---------------------------------------------------------------------
# 1. The gate itself -- CNOT as a 4x4 matrix
# ---------------------------------------------------------------------
print("--- CNOT matrix (control q0, target q1) ---")
print(np.real(Operator(build(0, 0)).data).astype(int))

# ---------------------------------------------------------------------
# 2. The asked-for case: control = |1>, target = |0>
# ---------------------------------------------------------------------
before = Statevector(build(1, 0, apply_cnot=False))
after = Statevector(build(1, 0, apply_cnot=True))

qc = build(1, 0)
print("\n--- Circuit Diagram ---")
print(qc.draw(output="text"))

def report(tag, statevector):
    amplitudes = np.round(statevector.data.real, 3)
    print(f"  {tag} : |q1 q0> = |{label_of(statevector)}>   amplitudes {amplitudes}")

first, second = label_of(before), label_of(after)
print("\n--- Control in |1> ---")
report("Before CNOT", before)
report("After  CNOT", after)
print(f"  Control q0  : {first[1]} -> {second[1]}   (unchanged, as expected)")
print(f"  Target  q1  : {first[0]} -> {second[0]}   (flipped, as expected)")
print(f"  Target flipped : {first[0] != second[0]}")

# ---------------------------------------------------------------------
# 3. The complete truth table, generated from the circuit
# ---------------------------------------------------------------------
print("\n--- CNOT truth table (generated, not quoted) ---")
print("  control  target  ->  control' target'   matches XOR rule")
all_correct = True
for control_bit in (0, 1):
    for target_bit in (0, 1):
        out = label_of(Statevector(build(control_bit, target_bit)))
        out_control, out_target = int(out[1]), int(out[0])
        expected = control_bit ^ target_bit
        ok = (out_control == control_bit) and (out_target == expected)
        all_correct &= ok
        print(f"     {control_bit}       {target_bit}     ->     {out_control}"
              f"        {out_target}            {ok}")

print(f"\n  All four rows match target' = control XOR target : {all_correct}")
twice = Operator(build(0, 0).compose(build(0, 0)))
print(f"  CNOT applied twice is the identity              : "
      f"{twice.equiv(Operator(np.eye(4)))}")

# ---------------------------------------------------------------------
# 4. Circuit diagram figure
# ---------------------------------------------------------------------
qc.draw(output="mpl")
plt.show()
