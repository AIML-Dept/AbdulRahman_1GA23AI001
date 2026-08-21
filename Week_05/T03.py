"""
Week_05 / T03.py -- Tutorial 5, Hard
Measure only ONE qubit of a 2-qubit Bell pair and analyse the state of the
qubit that was never measured.
"""

from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator
from qiskit.quantum_info import Statevector

sim = AerSimulator()

# 1. Bell pair (|00> + |11>)/sqrt(2) -- BEFORE any measurement.
bell = QuantumCircuit(2)
bell.h(0)
bell.cx(0, 1)
before = Statevector(bell).probabilities([1])       # qubit 1 only
print("Before measurement -> qubit 1:  P(0) = %.2f , P(1) = %.2f  (unknown)" %
      (before[0], before[1]))


# 2. Same Bell pair, but now qubit 0 alone is measured.
def partial_measurement():
    qc = QuantumCircuit(2, 1)
    qc.h(0)
    qc.cx(0, 1)
    qc.measure(0, 0)          # only qubit 0 -- qubit 1 is left untouched
    qc.save_statevector()     # state of the pair right after the collapse

    result = sim.run(qc, shots=1).result()
    bit = list(result.get_counts().keys())[0]
    probs = result.get_statevector().probabilities([1])   # qubit 1 only
    return bit, probs


print("\nAfter measuring qubit 0 only:")
print(" trial | qubit 0 | qubit 1: P(0), P(1) | qubit 1 state")
print("-" * 55)

for trial in range(1, 6):
    bit, p = partial_measurement()
    print(f"   {trial}   |    {bit}    |     {p[0]:.2f}, {p[1]:.2f}       |     |{bit}>")

print("\nQubit 1 was 50/50 before, but becomes certain the instant qubit 0 is read.")
print("Measuring half of an entangled pair collapses the whole pair.")
