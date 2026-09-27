"""
Week_09 / T05.py -- Tutorial 9, Challenge
Build a 3-qubit GHZ state and a 3-qubit W state, then compare how their
entanglement is structured: measure one qubit, or lose it (trace it out), and
check what is left between the other two.
"""

import numpy as np
import matplotlib.pyplot as plt
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector, concurrence, entropy, partial_trace
from qiskit_aer import AerSimulator

SHOTS = 1024
SEED = 9

sim = AerSimulator(seed_simulator=SEED)


def ghz_state():
    """
      q0 : |0> --H--*------      H, then two CNOTs copy q0's value along:
      q1 : |0> -----X--*---      (|000> + |111>)/sqrt(2)
      q2 : |0> --------X---
    """
    qc = QuantumCircuit(3, name='GHZ')
    qc.h(0)
    qc.cx(0, 1)
    qc.cx(1, 2)
    return qc


def w_state():
    """
    (|100> + |010> + |001>)/sqrt(3): exactly one qubit is 1. Start with the 1
    on q0 and pass it along like a relay. Each CRy + CNOT step decides how much
    of it moves on to the next qubit:
      q0 -> q1 : stays on q0 with probability 1/3, moves on with 2/3
      q1 -> q2 : of that, half stays on q1 and half moves on to q2
    """
    qc = QuantumCircuit(3, name='W')
    qc.x(0)
    qc.cry(2 * np.arccos(np.sqrt(1 / 3)), 0, 1)
    qc.cx(1, 0)
    qc.cry(2 * np.arccos(np.sqrt(1 / 2)), 1, 2)
    qc.cx(2, 1)
    return qc


def measured(prep, basis):
    """q0 is always measured in Z; q1 and q2 in the Z or the X basis (H first)."""
    qc = QuantumCircuit(3, 3)
    qc.compose(prep, inplace=True)
    if basis == 'X':
        qc.h([1, 2])
    qc.measure([0, 1, 2], [0, 1, 2])
    return qc


def pair_given_q0(counts, m):
    """Only the shots where q0 gave m: (fraction of shots, E of the pair q1 q2)."""
    kept = {key: c for key, c in counts.items() if key[0] == m}
    n = sum(kept.values())
    same = sum(c for key, c in kept.items() if key[1] == key[2])
    return n / SHOTS, (2 * same - n) / n


def pair_state_given_q0(state, m):
    """Exact state of q1 q2 after q0 is measured as m: keep that part, renormalise."""
    amps = np.array([state.data[(j << 1) | int(m)] for j in range(4)])  # bit 0 = q0
    return Statevector(amps / np.linalg.norm(amps))


preps = {'GHZ': ghz_state(), 'W': w_state()}
states = {name: Statevector(qc) for name, qc in preps.items()}
for name, qc in preps.items():
    print(f"{name} circuit")
    print(qc)

# One job: each state with q1 q2 measured in Z, and again in X.
# Every key is flipped so that position i = qubit i.
keys = [(name, basis) for name in preps for basis in 'ZX']
result = sim.run([measured(preps[n], b) for n, b in keys], shots=SHOTS).result()
counts = {k: {key[::-1]: c for key, c in result.get_counts(i).items()}
          for i, k in enumerate(keys)}

print("All three qubits measured in Z (q0 q1 q2)")
for name in preps:
    print(f"  {name:3s}: {dict(sorted(counts[(name, 'Z')].items()))}")

# 1. MEASURE q0, then test the pair q1 q2 with T03's check: a pair without
#    entanglement has |E_ZZ| + |E_XX| <= 1, a Bell pair reaches 2.
print("\nstate | q0 gave | P(q0) | pair q1 q2: E_ZZ   E_XX | |E_ZZ|+|E_XX| | C exact")
print("-" * 78)
witness, C_meas = {}, {}
for name in preps:
    for m in '01':
        p, ezz = pair_given_q0(counts[(name, 'Z')], m)
        _, exx = pair_given_q0(counts[(name, 'X')], m)
        witness[(name, m)] = abs(ezz) + abs(exx)
        C_meas[(name, m)] = concurrence(pair_state_given_q0(states[name], m))
        print(f" {name:3s}  |    {m}    | {p:.3f} |           {ezz:+.2f}  {exx:+.2f} |"
              f"      {witness[(name, m)]:.2f}     |  {C_meas[(name, m)]:.3f}")

# 2. LOSE q0 (trace it out) -- and, by symmetry, check every other pair too.
print("\nstate | one qubit vs rest | concurrence of each pair left behind")
print("      |  entropy (bits)   |   q1 q2    q0 q2    q0 q1")
print("-" * 60)
C_lost = {}
for name, state in states.items():
    s = entropy(partial_trace(state, [1, 2]), base=2)          # q0 alone
    pairs = [concurrence(partial_trace(state, [q])) for q in (0, 1, 2)]
    C_lost[name] = pairs[0]
    print(f" {name:3s}  |       {s:.3f}       |   " + "    ".join(f"{c:.3f}" for c in pairs))

print("\nGHZ is all-or-nothing: each qubit is fully entangled with the rest (1 bit),")
print("yet no two qubits share any entanglement on their own (C = 0). Measure or")
print("lose one qubit and the other two are left as plain '00'-or-'11' bits:")
print("correlated in Z, unrelated in X, so the check stays at 1 (plus shot noise).")
print("\nW spreads its entanglement over the pairs: after losing a qubit every pair")
print("keeps C = 0.667, and measuring q0 = 0 (probability 2/3) leaves q1 q2 in the")
print("Bell state Psi+ (C = 1, |E_ZZ|+|E_XX| = 2). Losing a qubit does not destroy it.")

# 3. What is left between q1 and q2: measured check (left), exact values (right).
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.2))
labels = ['GHZ\nq0 = 0', 'GHZ\nq0 = 1', 'W\nq0 = 0', 'W\nq0 = 1']
colors = ['tab:blue', 'tab:blue', 'tab:orange', 'tab:orange']
bars = ax1.bar(labels, [witness[(n, m)] for n in preps for m in '01'], color=colors)
ax1.bar_label(bars, fmt='%.2f', padding=3)
ax1.axhline(1, color='black', linestyle='--',
            label='limit without entanglement (+ shot noise)')
ax1.set(ylim=(0, 2.4), ylabel='|E_ZZ| + |E_XX| of q1 q2 (measured)',
        title='After MEASURING q0')
ax1.legend(loc='upper left')

x = np.arange(3)
for k, name in enumerate(preps):
    values = [C_meas[(name, '0')], C_meas[(name, '1')], C_lost[name]]
    bars = ax2.bar(x + (k - 0.5) * 0.4, values, 0.4, color=colors[2 * k], label=name)
    ax2.bar_label(bars, fmt='%.2f', padding=3)
ax2.set_xticks(x, ['q0 measured = 0', 'q0 measured = 1', 'q0 lost (traced out)'])
ax2.set(ylim=(0, 1.2), ylabel='concurrence of q1 q2 (exact)',
        title='Entanglement left between q1 and q2')
ax2.legend(loc='upper right')
plt.tight_layout()
plt.show()
