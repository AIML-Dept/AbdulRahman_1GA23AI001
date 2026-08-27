"""
Week_06 / T03.py -- Tutorial 6, Hard
Extend Simon's algorithm to a 4-bit secret and finish the job: solve the
system of linear equations over GF(2) in code to recover the hidden string.
"""

from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator

SECRET = '1011'         # SECRET[0] lives on qubit 0, SECRET[1] on qubit 1, ...
N = len(SECRET)
SEED = 6

sim = AerSimulator(seed_simulator=SEED)


def xor(a, b):
    """Bitwise XOR of two equal-length bit strings, e.g. '101' ^ '110' = '011'."""
    return ''.join(str(int(x) ^ int(y)) for x, y in zip(a, b))


def dot(a, b):
    """Dot product of two bit strings over GF(2): multiply, add, keep parity."""
    return sum(int(x) * int(y) for x, y in zip(a, b)) % 2


def simon_oracle(s):
    """Same 2-to-1 oracle as T01, now on 4 + 4 qubits."""
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
        lead = b.index('1')               # the column this basis row owns
        if v[lead] == '1':
            v = xor(v, b)
    if '1' not in v:
        return False                      # no new information in y
    lead = v.index('1')
    basis[:] = [xor(b, v) if b[lead] == '1' else b for b in basis]
    basis.append(v)
    return True


def solve(basis, n):
    """
    Return every non-zero s satisfying all collected equations. Each basis row
    'owns' one column (its leading 1). Columns nobody owns are free: switch one
    on and the owned columns are then forced, which reads straight off the rows.
    """
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


# 1. The full Simon circuit, exactly as in T02 but four bits wide.
qc = QuantumCircuit(2 * N, N)
qc.h(range(N))
qc.compose(simon_oracle(SECRET), inplace=True)
qc.h(range(N))
qc.measure(range(N), range(N))

# memory=True hands back the shots one by one instead of as a summary, which
# lets us watch the equations pile up sample by sample.
samples = sim.run(qc, shots=40, memory=True).result().get_memory()

print(f"Hidden secret is {N} bits long. We need n-1 = {N - 1} independent equations.\n")
print(" run |   y    | y.s | new information? | equations held")
print("-" * 58)

basis = []
runs = 0
for key in samples:
    y = key[::-1]                         # Qiskit prints c3c2c1c0, flip it
    runs += 1
    new = add_equation(basis, y)
    print(f" {runs:3d} |  {y}  |  {dot(y, SECRET)}  |       {'yes' if new else 'no ':3s}        |       {len(basis)}")
    if len(basis) == N - 1:
        break

print("\nReduced system (each row is one equation y.s = 0):")
for b in basis:
    terms = ' + '.join(f"s{i}" for i, bit in enumerate(b) if bit == '1')
    print(f"   {b}    ->   {terms}  =  0")

# 2. Solve it. With n-1 independent equations only one non-zero string survives.
answers = solve(basis, N)
recovered = answers[0]

print(f"\nSolutions of the system : {['0' * N] + answers}")
print(f"Discarding the all-zero string leaves : {recovered}")
print(f"True secret                           : {SECRET}")
print(f"Match : {recovered == SECRET}")


# 3. Independent check -- query the oracle classically at 0 and at s.
def f(x):
    circ = QuantumCircuit(2 * N, N)
    for i, bit in enumerate(x):
        if bit == '1':
            circ.x(i)
    circ.compose(simon_oracle(SECRET), inplace=True)
    circ.measure(range(N, 2 * N), range(N))
    return sim.run(circ, shots=1).result().get_counts().popitem()[0][::-1]


zero = '0' * N
print(f"\nOracle check:  f({zero}) = {f(zero)}   f({recovered}) = {f(recovered)}")
print(f"They collide, so {recovered} really is the period : {f(zero) == f(recovered)}")

print(f"\n{runs} quantum runs were enough, and that number grows only like n.")
print("A classical search must keep querying random inputs until two of them")
print("collide, which needs about 2^(n/2) queries. At n = 4 both are tiny, but")
print("the quantum cost grows in a straight line while the classical one doubles")
print("every two extra bits. T04 measures that gap.")
