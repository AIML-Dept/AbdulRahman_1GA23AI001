"""
Week_09 / T01.py -- Tutorial 9, Easy
Build the Bell state |Phi+> = (|00> + |11>)/sqrt(2), check its amplitudes,
then confirm over 1024 shots that only '00' and '11' ever occur, even though
each qubit on its own behaves like a fair coin.
"""

import matplotlib.pyplot as plt
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector
from qiskit_aer import AerSimulator

SHOTS = 1024
SEED = 9
OUTCOMES = ['00', '01', '10', '11']     # written q0 q1: position i = qubit i

sim = AerSimulator(seed_simulator=SEED)


def phi_plus():
    """
      q0 : |0> --H--*--      H puts q0 into (|0> + |1>)/sqrt(2)
                    |
      q1 : |0> -----X--      CNOT copies q0's value onto q1, in both branches

    |00>  ->  (|0> + |1>)|0>/sqrt(2)  ->  (|00> + |11>)/sqrt(2)
    """
    qc = QuantumCircuit(2, name='Phi+')
    qc.h(0)
    qc.cx(0, 1)
    return qc


def amplitude(state, label):
    """Amplitude of |label>, label written q0 q1. Qiskit's index reads q1 q0."""
    return state.data[int(label[::-1], 2)]


bell = phi_plus()
print("Bell circuit for |Phi+>")
print(bell)

# 1. Theory: the exact state, before any measurement.
state = Statevector(bell)
print("outcome | amplitude | probability")
print("-" * 36)
for label in OUTCOMES:
    amp = amplitude(state, label)
    print(f"  {label}    |  {amp.real:+.4f}  |   {abs(amp) ** 2:.4f}")

# 2. Could this be two separate qubits?  A product state
#    (a0|0> + a1|1>)(b0|0> + b1|1>) has amplitudes a0b0, a0b1, a1b0, a1b1, so
#    amp(00)*amp(11) - amp(01)*amp(10) = a0b0*a1b1 - a0b1*a1b0 = 0, always.
d = (amplitude(state, '00') * amplitude(state, '11')
     - amplitude(state, '01') * amplitude(state, '10'))
print(f"\namp(00)*amp(11) - amp(01)*amp(10) = {d.real:+.4f}   (0 for ANY product state)")
print(f"concurrence C = 2 x |that| = {2 * abs(d):.4f}      "
      f"(0 = product, 1 = maximally entangled)")

# 3. Practice: measure both qubits, 1024 shots.
qc = QuantumCircuit(2, 2)
qc.compose(bell, inplace=True)
qc.measure([0, 1], [0, 1])
print("\nMeasured circuit")
print(qc)

raw = sim.run(qc, shots=SHOTS).result().get_counts()
counts = {key[::-1]: c for key, c in raw.items()}        # position i = qubit i

print("outcome | expected | counts | measured")
print("-" * 40)
for label in OUTCOMES:
    expected = abs(amplitude(state, label)) ** 2
    n = counts.get(label, 0)
    print(f"  {label}    |  {expected:.3f}   |  {n:4d}  |  {n / SHOTS:.3f}")

print(f"\nOutcomes seen           : {sorted(counts)}")
print(f"Only '00' and '11' seen : {set(counts) <= {'00', '11'}}")
print(f"'01' or '10' seen       : {counts.get('01', 0) + counts.get('10', 0)} times")

# 4. Each qubit on its own, then the two together.
print()
for q in (0, 1):
    ones = sum(c for key, c in counts.items() if key[q] == '1')
    print(f"qubit {q} alone : P(0) = {1 - ones / SHOTS:.3f}, P(1) = {ones / SHOTS:.3f}"
          f"   -> a fair coin")
agree = sum(c for key, c in counts.items() if key[0] == key[1])
print(f"both qubits   : same value on {agree} of {SHOTS} shots")

print("\nEach qubit alone is a 50/50 coin, yet the two coins land the same way")
print("on every shot. Neither qubit holds a value of its own before it is")
print("measured: the only definite fact is the relation 'q0 = q1'. The amplitude")
print("test says the same thing -- no pair of single-qubit states multiplies out")
print("to (|00> + |11>)/sqrt(2), so the pair has one state vector, not two.")

# 5. Histogram, with the expected 512 marked.
values = [counts.get(label, 0) for label in OUTCOMES]
fig, ax = plt.subplots(figsize=(6.5, 4))
bars = ax.bar(OUTCOMES, values, color=['tab:blue', 'tab:red', 'tab:red', 'tab:blue'])
ax.axhline(SHOTS / 2, color='gray', linestyle='--', label=f'expected {SHOTS // 2}')
ax.bar_label(bars, padding=6)
ax.set_ylim(0, SHOTS * 0.62)
ax.set_xlabel('outcome (q0 q1)')
ax.set_ylabel('counts')
ax.set_title(f'|Phi+> measured {SHOTS} times: only 00 and 11 occur')
ax.legend(loc='upper center')
ax.grid(axis='y', alpha=0.3)
plt.tight_layout()
plt.show()
