"""
Week_06 / T04.py -- Tutorial 6, Real-world
Count how many oracle queries Simon's algorithm actually needs versus a
classical brute-force search, for secrets of growing length, and plot
the speedup.
"""

import random
import matplotlib.pyplot as plt
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator

LENGTHS = [2, 4, 6, 8, 10, 12, 14, 16, 18, 20]
Q_TRIALS = 40           # repeats of the quantum run
C_TRIALS = 200          # repeats of the classical search
SEED = 6

random.seed(SEED)


def xor(a, b):
    """Bitwise XOR of two equal-length bit strings."""
    return ''.join(str(int(x) ^ int(y)) for x, y in zip(a, b))


def simon_oracle(s):
    """Same 2-to-1 oracle as T01, for any length of s."""
    n = len(s)
    qc = QuantumCircuit(2 * n)
    for i in range(n):
        qc.cx(i, n + i)
    if '1' in s:
        j = s.index('1')
        for i, bit in enumerate(s):
            if bit == '1':
                qc.cx(j, n + i)
    return qc


def add_equation(basis, y):
    """Gaussian elimination over GF(2), where adding is just XOR."""
    v = y
    for b in basis:
        lead = b.index('1')
        if v[lead] == '1':
            v = xor(v, b)
    if '1' not in v:
        return False
    lead = v.index('1')
    basis[:] = [xor(b, v) if b[lead] == '1' else b for b in basis]
    basis.append(v)
    return True


def quantum_queries(n):
    """Average number of circuit runs needed to reach n-1 independent equations."""
    secret = format(random.randrange(1, 2 ** n), f'0{n}b')

    qc = QuantumCircuit(2 * n, n)
    qc.h(range(n))
    qc.compose(simon_oracle(secret), inplace=True)
    qc.h(range(n))
    qc.measure(range(n), range(n))

    # One simulator call supplies the shots for every trial. Each shot is one
    # query to the oracle, so counting shots is counting queries.
    budget = 6 * n + 20
    sim = AerSimulator(seed_simulator=SEED + n)
    stream = sim.run(qc, shots=Q_TRIALS * budget, memory=True).result().get_memory()

    totals, pos = [], 0
    for _ in range(Q_TRIALS):
        basis, used = [], 0
        while len(basis) < n - 1:
            add_equation(basis, stream[pos][::-1])
            pos, used = pos + 1, used + 1
        totals.append(used)
    return sum(totals) / len(totals)


def classical_queries(n):
    """
    Average queries a classical attacker needs. With only a black box, the one
    clue about s is a collision f(x) = f(x'), because then s = x ^ x'. So the
    attacker keeps trying fresh inputs until two of them land on the same value.
    """
    totals = []
    for _ in range(C_TRIALS):
        s = random.randrange(1, 2 ** n)
        j = (s & -s).bit_length() - 1           # lowest position where s has a 1

        seen, tried, used = {}, set(), 0
        while True:
            x = random.randrange(2 ** n)
            if x in tried:
                continue                        # already paid for this one
            tried.add(x)
            used += 1

            fx = x if not (x >> j) & 1 else x ^ s
            if fx in seen:
                break                           # collision found -> s = x ^ seen[fx]
            seen[fx] = x
        totals.append(used)
    return sum(totals) / len(totals)


print(f"Averages over {Q_TRIALS} quantum trials and {C_TRIALS} classical trials\n")
print("  n  |  secret space  |  quantum queries |  classical queries |  speedup")
print("-" * 76)

quantum, classical = [], []
for n in LENGTHS:
    q = quantum_queries(n)
    c = classical_queries(n)
    quantum.append(q)
    classical.append(c)
    print(f" {n:2d}  | {2 ** n:14d} |      {q:6.2f}      |       {c:8.2f}     |  {c / q:6.2f}x")

print("\nQuantum cost grows in a straight line -- about n queries, because every")
print("run buys one equation and n-1 equations are enough to pin s down.")
print("Classical cost grows like 2^(n/2): that is the birthday bound for bumping")
print("into a collision, and it is the only clue a black box ever gives you.")
print(f"\nAt n = {LENGTHS[0]} the two are neck and neck ({classical[0] / quantum[0]:.2f}x). "
      f"At n = {LENGTHS[-1]} it is {classical[-1] / quantum[-1]:.2f}x,")
print("and the ratio keeps doubling for every two bits added. For a 128-bit")
print("secret the classical search would need about 2^64 queries -- roughly 600")
print("years at a billion queries a second -- while Simon's needs about 127.")
print("\nThis was the first proven exponential separation between quantum and")
print("classical, and it is what inspired Shor's factoring algorithm: RSA breaks")
print("because finding a hidden period is exactly this kind of problem.")

# Plot: raw query counts on the left, the speedup ratio on the right.
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.5))

ax1.plot(LENGTHS, classical, 'o-', label='classical brute force')
ax1.plot(LENGTHS, quantum, 's-', label="Simon's algorithm")
ax1.set_yscale('log')
ax1.set_xticks(LENGTHS)
ax1.set_xlabel('secret length n (bits)')
ax1.set_ylabel('oracle queries (log scale)')
ax1.set_title('Queries needed to find s')
ax1.legend()
ax1.grid(alpha=0.3)

ax2.plot(LENGTHS, [c / q for c, q in zip(classical, quantum)], 'd-', color='green')
ax2.axhline(1, color='grey', linestyle='--', linewidth=1)
ax2.set_xticks(LENGTHS)
ax2.set_xlabel('secret length n (bits)')
ax2.set_ylabel('classical queries / quantum queries')
ax2.set_title('Speedup')
ax2.grid(alpha=0.3)

plt.tight_layout()
plt.show()
