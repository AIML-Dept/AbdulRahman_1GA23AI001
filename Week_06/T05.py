"""
Week_06 / T05.py -- Tutorial 6, Challenge
One general simon() function that takes ANY secret bit string, works out
what it is on its own, and correctly handles the all-zero edge case where
the oracle is one-to-one and there is no period to find.
"""

from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator

SEED = 6
CONFIRM = 15            # uninformative runs in a row before the rank is called final


def xor(a, b):
    """Bitwise XOR of two equal-length bit strings."""
    return ''.join(str(int(x) ^ int(y)) for x, y in zip(a, b))


def simon_oracle(s):
    """
    Same 2-to-1 oracle as T01. If s is all zeros the second loop is skipped,
    f(x) = x, and the oracle is one-to-one instead of two-to-one.
    """
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


def solve(basis, n):
    """Every non-zero string satisfying all the collected equations."""
    pivots = [b.index('1') for b in basis]
    free = [c for c in range(n) if c not in pivots]

    answers = []
    for c in free:
        s = ['0'] * n
        s[c] = '1'
        for b, p in zip(basis, pivots):
            s[p] = b[c]
        answers.append(''.join(s))
    return answers


def simon(secret):
    """
    Run Simon's algorithm on an oracle hiding `secret` and return
    (recovered string, runs used, rank reached). The secret is only used to
    BUILD the oracle -- the recovery below never looks at it.
    """
    n = len(secret)
    sim = AerSimulator(seed_simulator=SEED + n)

    qc = QuantumCircuit(2 * n, n)
    qc.h(range(n))
    qc.compose(simon_oracle(secret), inplace=True)
    qc.h(range(n))
    qc.measure(range(n), range(n))

    # Keep sampling past n-1 equations. That extra headroom is exactly what
    # makes the all-zero case detectable.
    stream = sim.run(qc, shots=8 * n + 60, memory=True).result().get_memory()

    basis, runs, stale = [], 0, 0
    for key in stream:
        runs += 1
        if add_equation(basis, key[::-1]):
            stale = 0
        else:
            stale += 1                         # this run told us nothing new

        if len(basis) == n:                    # full rank, cannot do better
            break
        # Stuck at n-1. If s really were zero, each fresh run would have a 1-in-2
        # chance of breaking the deadlock, so CONFIRM failures in a row means
        # s = 0 is wrong with probability under 1 in 2^CONFIRM.
        if len(basis) == n - 1 and stale >= CONFIRM:
            break

    rank = len(basis)

    # The whole edge case lives in these three lines.
    #   rank n    -> y came out uniformly random over ALL strings, which only
    #                happens when f is one-to-one, so there is no period: s = 0.
    #   rank n-1  -> y was trapped in the half-space perpendicular to s, and
    #                exactly one non-zero string survives the equations.
    if rank == n:
        return '0' * n, runs, rank
    if rank == n - 1:
        return solve(basis, n)[0], runs, rank
    return None, runs, rank                    # unlucky run, would need more shots


def f(x, secret):
    """Query the oracle once, classically, to double-check an answer."""
    n = len(secret)
    qc = QuantumCircuit(2 * n, n)
    for i, bit in enumerate(x):
        if bit == '1':
            qc.x(i)
    qc.compose(simon_oracle(secret), inplace=True)
    qc.measure(range(n, 2 * n), range(n))
    sim = AerSimulator(seed_simulator=SEED)
    return sim.run(qc, shots=1).result().get_counts().popitem()[0][::-1]


TESTS = ['1', '0', '11', '110', '1011', '0000', '10101', '000000', '1101101']

print("  secret  | n | oracle is  | runs | rank | recovered | correct?")
print("-" * 68)

all_ok = True
for secret in TESTS:
    n = len(secret)
    recovered, runs, rank = simon(secret)
    kind = '2-to-1' if '1' in secret else '1-to-1'
    ok = recovered == secret
    all_ok = all_ok and ok
    print(f" {secret:8s} |{n:2d} |   {kind}   |  {runs:3d} |  {rank:2d}  |  {str(recovered):8s} |   {'yes' if ok else 'NO'}")

print(f"\nAll secrets recovered correctly : {all_ok}")

# A closer look at the two cases that behave differently.
print("\nWhy the all-zero case needs separate handling")
print("-" * 68)

for secret in ['1011', '0000']:
    n = len(secret)
    recovered, runs, rank = simon(secret)
    zero = '0' * n
    print(f"\ns = {secret}")
    print(f"  f pairs up inputs?      {'yes, f(x) = f(x^s)' if '1' in secret else 'no, every input has its own output'}")
    print(f"  measured y ranges over  {2 ** (n - 1) if '1' in secret else 2 ** n} strings")
    print(f"  highest rank reachable  {n - 1 if '1' in secret else n}")
    print(f"  rank actually reached   {rank}  ->  conclusion: s = {recovered}")
    print(f"  oracle check f({zero}) = {f(zero, secret)}, f({recovered}) = {f(recovered, secret)}")

print("\nA program that blindly stops at n-1 equations would report a wrong,")
print("made-up secret for the all-zero oracle. Letting the rank climb to n and")
print("reading rank == n as 'no period exists' is what makes this version general.")
print(f"\nThe price is the {CONFIRM} extra runs spent confirming the rank has really")
print(f"stopped growing, which leaves under a 1 in {2 ** CONFIRM} chance of calling it")
print("wrong. Detecting that nothing is hidden costs more than finding something.")
print("\nNote on n = 1 with s = '1': n-1 = 0 equations are needed, so there is no")
print("system to solve at all -- the answer comes purely from the rank rule, and")
print("every run is spent confirming rank 0 is the ceiling. The same code handles")
print("it, which is a good sign the logic is not special-cased by hand.")
