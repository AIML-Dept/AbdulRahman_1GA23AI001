"""
Week_05 / T02.py -- Tutorial 5, Medium
Prepare |+> and |->, measure them in the X basis (apply H before the
measurement) and interpret the results.
"""

from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator

sim = AerSimulator()
SHOTS = 1000


def measure(state, basis):
    """Prepare |+> or |->, then measure in the Z or X basis."""
    qc = QuantumCircuit(1, 1)

    if state == '+':
        qc.h(0)             # |+> = H|0>
    else:
        qc.x(0)
        qc.h(0)             # |-> = H X|0>

    if basis == 'X':
        qc.h(0)             # basis change: H maps |+>->|0> and |->->|1>

    qc.measure(0, 0)
    return sim.run(qc, shots=SHOTS).result().get_counts()


print(f"{SHOTS} shots per experiment\n")
print(" state | basis |        counts")
print("-" * 45)

for state in ['+', '-']:
    for basis in ['Z', 'X']:
        counts = measure(state, basis)
        print(f"  |{state}>  |   {basis}   |  {counts}")

print("\nZ basis: both states look 50/50 random -- the measurement cannot tell them apart.")
print("X basis: |+> always gives 0 and |-> always gives 1 -- fully deterministic.")
print("Randomness is not in the state alone, it depends on the basis you measure in.")
