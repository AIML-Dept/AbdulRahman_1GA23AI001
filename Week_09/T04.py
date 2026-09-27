"""
Week_09 / T04.py -- Tutorial 9, Real-world
Entanglement-based key distribution (the idea behind E91 / BBM92). Alice and
Bob share Phi+ pairs, measure in random bases (Z or X) and keep the pairs whose
bases matched as a secret key. An eavesdropper who copies Bob's bits breaks the
entanglement: about 25% key errors, and CHSH falls from 2.83 to below 2.
"""

import random
import numpy as np
import matplotlib.pyplot as plt
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator

N_PAIRS = 2000                  # pairs sent for the key exchange
SHOTS = 4096                    # pairs per setting for the CHSH check
SEED = 9
BASIS = {'Z': 0, 'X': 90}       # measuring direction in degrees from the Z axis
CHSH = [(0, 45, +1), (0, 135, -1), (90, 45, +1), (90, 135, +1)]   # (a, b, sign)

random.seed(SEED)
sim = AerSimulator(seed_simulator=SEED)


def pair_circuit(a_deg, b_deg, eve=None):
    """
      q0 (Alice) : |0> --H--*----------------Ry(-a)--M
                            |
      q1 (Bob)   : |0> -----X--[ Eve ]--*----Ry(-b)--M
      q2 (Eve)   : |0> -----------------X------------M

    Ry(-angle) turns the measuring direction onto Z (0 deg = Z basis, 90 = X).
    With eve = 'Z' or 'X', Eve copies Bob's bit in that basis into her qubit
    with a CNOT (H before and after for X). Copying a basis VALUE is all anyone
    can do -- a state cannot be cloned -- and it acts like measure-and-resend.
    """
    qc = QuantumCircuit(3, 3)
    qc.h(0)
    qc.cx(0, 1)                                   # the shared Phi+ pair
    qc.barrier()
    if eve is not None:
        if eve == 'X':
            qc.h(1)
        qc.cx(1, 2)                               # Eve's copy of Bob's bit
        if eve == 'X':
            qc.h(1)
    for qubit, angle in ((0, a_deg), (1, b_deg)):
        if angle:
            qc.ry(-np.radians(angle), qubit)
    qc.measure([0, 1, 2], [0, 1, 2])
    return qc


def exchange(eve_present):
    """
    Random bases for every pair (Alice, Bob, and Eve if present). Each setting
    runs once, all in ONE job with memory=True (every shot listed in order), and
    each pair takes the next shot of its own setting. Returns one record per
    pair: (basis_a, basis_b, basis_eve, bit_a, bit_b, bit_eve).
    """
    settings = [(random.choice('ZX'), random.choice('ZX'),
                 random.choice('ZX') if eve_present else None) for _ in range(N_PAIRS)]
    groups = sorted(set(settings), key=str)
    jobs = [pair_circuit(BASIS[a], BASIS[b], e) for a, b, e in groups]
    result = sim.run(jobs, shots=N_PAIRS, memory=True).result()
    stream = {g: iter(result.get_memory(k)) for k, g in enumerate(groups)}
    records = []
    for s in settings:
        bits = next(stream[s])[::-1]               # position i = qubit i
        records.append((*s, bits[0], bits[1], bits[2]))
    return records


def correlation(counts):
    """E = P(same) - P(different) for Alice's and Bob's bits."""
    same = sum(c for key, c in counts.items() if key[::-1][0] == key[::-1][1])
    return (2 * same - sum(counts.values())) / sum(counts.values())


print("One pair with Eve listening (Alice and Bob in X, Eve copies in Z)")
print(pair_circuit(90, 90, 'Z'))

# 1. The key exchange, without and then with an eavesdropper.
qber = {}
for eve_present in (False, True):
    records = exchange(eve_present)
    kept = [r for r in records if r[0] == r[1]]    # sifting: same basis only
    alice = ''.join(r[3] for r in kept)
    bob = ''.join(r[4] for r in kept)
    errors = sum(x != y for x, y in zip(alice, bob))
    qber[eve_present] = errors / len(kept)

    print(f"\nKey exchange, {'Eve copies EVERY bit' if eve_present else 'no eavesdropper'}")
    print(" pair | Alice | Bob  | Eve  | same basis? | key bit")
    print("-" * 52)
    for i, (ba, bb, be, xa, xb, xe) in enumerate(records[:8], start=1):
        key = '-' if ba != bb else xa if xa == xb else 'ERROR'
        eve = f"{be} {xe}" if be else ' -'
        print(f"  {i:2d}  |  {ba} {xa}  | {bb} {xb}  | {eve:4s} |"
              f"     {'yes' if ba == bb else 'no '}     | {key}")
    print(f"kept {len(kept)} of {N_PAIRS} pairs ({len(kept) / N_PAIRS:.0%}), "
          f"{errors} errors  ->  QBER = {qber[eve_present]:.1%}")
    print(f"Alice's key : {alice[:48]}...")
    print(f"Bob's key   : {bob[:48]}...")
    if eve_present:
        eve_right = sum(r[5] == r[3] for r in kept) / len(kept)
        print(f"Eve's copy matches Alice's key bit {eve_right:.1%} of the time, "
              f"at the cost of those errors")

# 2. CHSH check on extra pairs: four settings, with and without Eve.
jobs = [pair_circuit(a, b, eve) for eve in (None, 'Z', 'X') for a, b, _ in CHSH]
result = sim.run(jobs, shots=SHOTS).result()
E = [correlation(result.get_counts(k)) for k in range(len(jobs))]
E_honest = E[0:4]
E_eve = [(z + x) / 2 for z, x in zip(E[4:8], E[8:12])]   # Eve picks Z or X at random

print(f"\nCHSH check: Alice a = 0 or 90, Bob b = 45 or 135 (degrees), {SHOTS} pairs each")
print(" a, b (deg) | sign | E no Eve | E with Eve | theory cos(a - b)")
print("-" * 62)
for (a, b, sign), e1, e2 in zip(CHSH, E_honest, E_eve):
    print(f"  {a:2d}, {b:3d}   |  {'+' if sign > 0 else '-'}   |  {e1:+.3f}  |"
          f"   {e2:+.3f}   |      {np.cos(np.radians(a - b)):+.3f}")
S = {False: sum(s * e for (_, _, s), e in zip(CHSH, E_honest)),
     True: sum(s * e for (_, _, s), e in zip(CHSH, E_eve))}
print("S = E(0,45) - E(0,135) + E(90,45) + E(90,135)")
print(f"  no Eve   : S = {S[False]:.3f}   (above 2: still entangled)")
print(f"  with Eve : S = {S[True]:.3f}   (at most 2: only classical correlation left)")
print(f"  classical limit 2, quantum maximum 2*sqrt(2) = {2 * np.sqrt(2):.3f}")

print("\nHow entanglement secures the channel")
print(" 1. No key bit exists until Alice and Bob measure, so there is nothing on")
print("    the channel for Eve to copy in advance.")
print(" 2. Eve cannot clone Bob's qubit (no-cloning). Copying its value in ONE basis")
print("    turns the pair into ordinary bits, random in the other basis (T03).")
print(" 3. That costs about 25% key errors and pulls S down to about 1.41. Alice and")
print("    Bob compare a sample in public: errors near 0 and S near 2.83 mean")
print("    nobody listened; otherwise they throw the key away.")

# 3. What the eavesdropper changes, in two panels.
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))
labels, colors = ['no Eve', 'Eve listening'], ['tab:green', 'tab:red']
bars = ax1.bar(labels, [100 * qber[False], 100 * qber[True]], color=colors)
ax1.bar_label(bars, fmt='%.1f%%', padding=3)
ax1.axhline(25, color='gray', linestyle='--', label='theory with Eve: 25%')
ax1.set(ylim=(0, 35), ylabel='errors in the sifted key (%)', title='Key error rate (QBER)')
ax1.legend(loc='upper left')
bars = ax2.bar(labels, [S[False], S[True]], color=colors)
ax2.bar_label(bars, fmt='%.2f', padding=3)
ax2.axhline(2, color='black', linestyle='--', label='classical limit 2')
ax2.axhline(2 * np.sqrt(2), color='tab:blue', linestyle=':', label='quantum max 2.83')
ax2.set(ylim=(0, 3.4), ylabel='CHSH value S', title='Entanglement check (CHSH)')
ax2.legend(loc='upper right', fontsize=9)
for ax in (ax1, ax2):
    ax.grid(axis='y', alpha=0.3)
plt.tight_layout()
plt.show()
