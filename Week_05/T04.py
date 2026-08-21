"""
Week_05 / T04.py -- Tutorial 5, Real-world
An unknown rotation Ry(theta) is applied to |0>. Recover theta using only
measurement statistics (simple single-qubit state tomography).
"""

import numpy as np
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator

# The hidden angle -- the "experimenter" is not allowed to look at it.
SECRET = np.random.uniform(0, np.pi)

# Ry(t)|0> = cos(t/2)|0> + sin(t/2)|1>   =>   P(1) = sin^2(t/2)
# Inverting that formula gives:          t = 2 * arcsin(sqrt(P(1)))

sim = AerSimulator()
print("shots  |  P(1) measured |  estimated theta  |  error (rad)")
print("-" * 60)

for shots in [100, 1000, 10000]:
    qc = QuantumCircuit(1, 1)
    qc.ry(SECRET, 0)
    qc.measure(0, 0)

    counts = sim.run(qc, shots=shots).result().get_counts()
    p1 = counts.get('1', 0) / shots
    theta = 2 * np.arcsin(np.sqrt(p1))

    print(f"{shots:6d} |     {p1:.4f}     |      {theta:.4f}       |    {abs(theta - SECRET):.4f}")

print(f"\nTrue theta = {SECRET:.4f} rad ({np.degrees(SECRET):.2f} deg)")
print("The angle is never observed directly -- it is inferred from how often '1' appears.")
print("Error shrinks on average as 1/sqrt(shots); one individual row can still wobble.")
print("This is how real hardware is calibrated and how qubit states are characterised.")
