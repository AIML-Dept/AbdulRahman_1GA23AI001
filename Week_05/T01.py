"""
Week_05 / T01.py -- Tutorial 5, Easy
Measure a Hadamard-superposition qubit at 100, 1000 and 10000 shots and
tabulate how the measured probability converges to 0.5.
"""

from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator

# 1. Circuit: |0> --H--> (|0> + |1>)/sqrt(2), then measure in the Z basis.
qc = QuantumCircuit(1, 1)
qc.h(0)
qc.measure(0, 0)
print(qc)

sim = AerSimulator()

# 2. Run the SAME circuit with three different shot counts.
print("\n shots  | counts(0)  counts(1) |   P(0)   |  |P(0) - 0.5|")
print("-" * 58)

for shots in [100, 1000, 10000]:
    counts = sim.run(qc, shots=shots).result().get_counts()
    n0 = counts.get('0', 0)
    n1 = counts.get('1', 0)
    p0 = n0 / shots
    print(f"{shots:6d}  | {n0:8d}  {n1:9d} |  {p0:.4f}  |    {abs(p0 - 0.5):.4f}")

print("\nTheoretical P(0) = 0.5")
print("More shots -> smaller error. Shot noise falls off as 1/sqrt(shots).")
