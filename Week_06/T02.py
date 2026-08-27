"""
Week_06 / T02.py -- Tutorial 6, Medium
Run the complete Simon circuit for a 3-bit secret, confirm every measured
string y satisfies y.s = 0 (mod 2), and collect n-1 independent equations.
"""

from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator

SECRET = '110'          # SECRET[0] lives on qubit 0, SECRET[1] on qubit 1, ...
N = len(SECRET)
SHOTS = 1024
SEED = 6

sim = AerSimulator(seed_simulator=SEED)


def xor(a, b):
    """Bitwise XOR of two equal-length bit strings, e.g. '101' ^ '110' = '011'."""
    return ''.join(str(int(x) ^ int(y)) for x, y in zip(a, b))


def dot(a, b):
    """Dot product of two bit strings over GF(2): multiply, add, keep parity."""
    return sum(int(x) * int(y) for x, y in zip(a, b)) % 2


def simon_oracle(s):
    """Same 2-to-1 oracle as T01: f(x) = f(x ^ s) for every input x."""
    n = len(s)
    qc = QuantumCircuit(2 * n)
    for i in range(n):
        qc.cx(i, n + i)                   # copy x into the output register
    if '1' in s:
        j = s.index('1')
        for i, bit in enumerate(s):
            if bit == '1':
                qc.cx(j, n + i)           # add s whenever the input bit x_j is 1
    return qc


def add_equation(basis, y):
    """
    Try to add y to a growing set of independent equations. Over GF(2) there
    are no fractions, so Gaussian elimination is nothing but XOR: cancel the
    columns the basis already owns and see whether anything is left.
    """
    v = y
    for b in basis:
        lead = b.index('1')               # the column this basis row owns
        if v[lead] == '1':
            v = xor(v, b)                 # cancel that column out of v
    if '1' not in v:
        return False                      # v collapsed to zeros -> nothing new
    lead = v.index('1')
    basis[:] = [xor(b, v) if b[lead] == '1' else b for b in basis]
    basis.append(v)
    return True


# 1. The full Simon circuit: H, oracle, H, then measure the INPUT register.
qc = QuantumCircuit(2 * N, N)
qc.h(range(N))                            # every x at once, in superposition
qc.barrier()
qc.compose(simon_oracle(SECRET), inplace=True)
qc.barrier()
qc.h(range(N))                            # interference: bad answers cancel out
qc.measure(range(N), range(N))

print(f"Simon's circuit for a hidden {N}-bit secret")
print(qc)

# 2. Every shot is one query to the oracle and yields one equation y.s = 0.
counts = sim.run(qc, shots=SHOTS).result().get_counts()
results = {key[::-1]: n for key, n in counts.items()}   # flip c2c1c0 -> c0c1c2

print(f"\n{SHOTS} shots\n")
print("   y   | counts |  y.s mod 2 | allowed?")
print("-" * 46)

for y in sorted(results):
    d = dot(y, SECRET)
    print(f"  {y}  | {results[y]:6d} |     {d}      | {'yes' if d == 0 else 'NO'}")

valid = all(dot(y, SECRET) == 0 for y in results)
print(f"\nDistinct outcomes seen: {len(results)} out of {2 ** N} possible")
print(f"Every outcome satisfies y.s = 0 : {valid}")
print("The measurement never gives s. It gives strings PERPENDICULAR to s.")

# 3. Not every y is useful. '000' is always allowed but says nothing, and a y
#    that is the XOR of ones already collected adds no new information either.
basis = []
print("\n   y   | new information? | equations held")
print("-" * 46)
for y in sorted(results, key=lambda k: -results[k]):
    new = add_equation(basis, y)
    print(f"  {y}  |       {'yes' if new else 'no ':3s}        |       {len(basis)}")

print(f"\nIndependent equations collected: {len(basis)} (need n-1 = {N - 1})")
print("Equations kept:", ', '.join(basis))
print("\nn-1 equations pin s down to exactly two possibilities: the all-zero")
print("string and s itself. T03 finishes the job by solving that system.")
