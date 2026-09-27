"""
Week_09 / T03.py -- Tutorial 9, Hard
Measure Bell pairs in the Hadamard (X) basis instead of the computational (Z)
basis. Phi+ stays perfectly correlated, the X basis reveals the sign the Z
basis could not see, and a classical source of '00'/'11' pairs -- identical
to Phi+ in the Z basis -- loses all of its correlation in the X basis.
"""

import matplotlib.pyplot as plt
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector
from qiskit_aer import AerSimulator

SHOTS = 1024
SEED = 9
BELL_INPUTS = {'Phi+': '00', 'Phi-': '10', 'Psi+': '01', 'Psi-': '11'}
OUTCOMES = ['00', '01', '10', '11']                      # written q0 q1

sim = AerSimulator(seed_simulator=SEED)


def bell_state(name):
    """Same circuit as T02: X gates for the input bits (a b), then H and CNOT."""
    a, b = BELL_INPUTS[name]
    qc = QuantumCircuit(2, name=name)
    if a == '1':
        qc.x(0)
    if b == '1':
        qc.x(1)
    qc.h(0)
    qc.cx(0, 1)
    return qc


def plain_pair(bits):
    """No entanglement at all: two qubits simply set to '00' or '11'."""
    qc = QuantumCircuit(2, name=bits)
    for i, bit in enumerate(bits):
        if bit == '1':
            qc.x(i)
    return qc


def with_measurement(prep, basis):
    """
    Z basis: measure straight away.
    X basis: one H on each qubit first. H turns |+> into |0> and |-> into |1>,
    so the ordinary measurement then reads the X basis: '0' = +, '1' = -.
    """
    qc = QuantumCircuit(2, 2)
    qc.compose(prep, inplace=True)
    if basis == 'X':
        qc.h([0, 1])
    qc.measure([0, 1], [0, 1])
    return qc


def run(circuits, shots):
    """All circuits in ONE job (each gets its own seed); position i = qubit i."""
    result = sim.run(circuits, shots=shots).result()
    return [{key[::-1]: c for key, c in result.get_counts(i).items()}
            for i in range(len(circuits))]


def correlation(counts):
    """E = P(same) - P(different): +1 always agree, -1 always disagree, 0 unrelated."""
    same = counts.get('00', 0) + counts.get('11', 0)
    total = sum(counts.values())
    return (2 * same - total) / total


# Every Bell state in both bases, in one job.
keys = [(name, basis) for name in BELL_INPUTS for basis in 'ZX']
jobs = [with_measurement(bell_state(name), basis) for name, basis in keys]
counts = dict(zip(keys, run(jobs, SHOTS)))

# The classical source: a fair coin picks '00' or '11', so half the shots
# come from each. It is NOT entangled -- just correlated bits.
for basis in 'ZX':
    a, b = run([with_measurement(plain_pair(bits), basis) for bits in ('00', '11')],
               SHOTS // 2)
    counts[('classical', basis)] = {k: a.get(k, 0) + b.get(k, 0) for k in OUTCOMES}

# 1. The question asked: Phi+ measured in the Hadamard basis.
print("Phi+ measured in the Hadamard (X) basis")
print(with_measurement(bell_state('Phi+'), 'X'))
for basis in 'ZX':
    c = counts[('Phi+', basis)]
    print(f"{basis} basis : {dict(sorted(c.items()))}   -> E = {correlation(c):+.3f}")

# 2. Why: H on both qubits leaves Phi+ exactly as it was.
hh = QuantumCircuit(2)
hh.h([0, 1])
before = Statevector(bell_state('Phi+'))
print(f"\nPhi+ unchanged by H on both qubits : {before.evolve(hh).equiv(before)}")
print("so (|00> + |11>)/sqrt(2) = (|++> + |-->)/sqrt(2): in the X basis the qubits")
print("again come out equal, both + or both -, on every shot.")

# 3. The full pattern: every Bell state and the classical source, both bases.
print("\nsource    | basis |   00   01   10   11 | correlation E")
print("-" * 56)
E = {}
for name in list(BELL_INPUTS) + ['classical']:
    for basis in 'ZX':
        c = counts[(name, basis)]
        E[(name, basis)] = correlation(c)
        label = name if basis == 'Z' else ''
        row = " ".join(f"{c.get(k, 0):4d}" for k in OUTCOMES)
        print(f"{label:9s} |   {basis}   | {row} |    {E[(name, basis)]:+.3f}")

print("\nsource    |  E_ZZ   E_XX | |E_ZZ| + |E_XX|")
print("-" * 42)
for name in list(BELL_INPUTS) + ['classical']:
    ezz, exx = E[(name, 'Z')], E[(name, 'X')]
    print(f"{name:9s} | {ezz:+.2f}  {exx:+.2f} |      {abs(ezz) + abs(exx):.2f}")

print("\nThe X basis shows the sign the Z basis hid. Phi+ and Phi- both agree in Z,")
print("but in X Phi+ still agrees while Phi- always DISagrees; Psi+ and Psi- split")
print("the same way. So the two signs (E_ZZ, E_XX) identify each Bell state.")
print("\nThe classical source copies Phi+ perfectly in the Z basis, yet in the X")
print("basis its qubits are unrelated (E_XX close to 0). Any pair WITHOUT")
print("entanglement obeys |E_ZZ| + |E_XX| <= 1 (up to shot noise): it can be")
print("perfectly correlated in one basis at most. Every Bell state reaches 2.")

# 4. Correlation in both bases for every source.
names = list(BELL_INPUTS) + ['classical']
x = range(len(names))
fig, ax = plt.subplots(figsize=(8.5, 4.2))
z_bars = ax.bar([i - 0.2 for i in x], [E[(n, 'Z')] for n in names], 0.4,
                color='tab:blue', label='Z basis (computational)')
x_bars = ax.bar([i + 0.2 for i in x], [E[(n, 'X')] for n in names], 0.4,
                color='tab:orange', label='X basis (Hadamard)')
for bars in (z_bars, x_bars):
    ax.bar_label(bars, fmt='%+.2f', padding=3, fontsize=8)
ax.axhline(0, color='black', linewidth=0.8)
ax.set_xticks(list(x), ['Phi+', 'Phi-', 'Psi+', 'Psi-', "classical\n'00' or '11'"])
ax.set_ylim(-1.3, 1.3)
ax.set_ylabel('correlation E = P(same) - P(different)')
ax.set_title('Bell pairs are correlated in BOTH bases; the classical pairs only in Z')
ax.legend(loc='lower left', fontsize=9)
ax.grid(axis='y', alpha=0.3)
plt.tight_layout()
plt.show()
