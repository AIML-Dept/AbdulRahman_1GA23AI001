"""
Week_06 / T01.py -- Tutorial 6, Easy
Build Simon's oracle for the secret string '110', run it on every possible
input and check the truth table really has the promised hidden period.
"""

from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator

SECRET = '110'          # convention: SECRET[0] lives on qubit 0, SECRET[1] on qubit 1, ...
N = len(SECRET)

sim = AerSimulator()


def xor(a, b):
    """Bitwise XOR of two equal-length bit strings, e.g. '101' ^ '110' = '011'."""
    return ''.join(str(int(x) ^ int(y)) for x, y in zip(a, b))


def simon_oracle(s):
    """
    Circuit on 2n qubits: qubits 0..n-1 hold the input x, qubits n..2n-1
    receive f(x). It is built so that f(x) and f(x ^ s) always come out equal.
    """
    n = len(s)
    qc = QuantumCircuit(2 * n)

    # 1. Copy the input onto the output register:  |x>|0> -> |x>|x>
    for i in range(n):
        qc.cx(i, n + i)

    # 2. Glue x and x ^ s together. Pick the first position j where s has a 1.
    #    Whenever the input bit x_j is 1, add s to the output. So one partner
    #    of the pair is sent to x, the other to x ^ s -- both land on the same
    #    value. If s is all zeros this step is skipped and f stays one-to-one.
    if '1' in s:
        j = s.index('1')
        for i, bit in enumerate(s):
            if bit == '1':
                qc.cx(j, n + i)

    return qc


def f(x):
    """Feed one input x into the oracle and read f(x) off the output register."""
    qc = QuantumCircuit(2 * N, N)

    for i, bit in enumerate(x):
        if bit == '1':
            qc.x(i)                       # prepare |x> in the input register

    qc.compose(simon_oracle(SECRET), inplace=True)
    qc.measure(range(N, 2 * N), range(N))

    key = sim.run(qc, shots=1).result().get_counts().popitem()[0]
    return key[::-1]                      # Qiskit prints c2c1c0, flip to c0c1c2


print("Oracle circuit for s =", SECRET)
print("qubits 0-2 = input x, qubits 3-5 = output f(x)")
print(simon_oracle(SECRET))

# 3. Query the oracle once for every one of the 2^n inputs.
table = {}
for value in range(2 ** N):
    x = format(value, f'0{N}b')
    table[x] = f(x)

print("\n   x   |  f(x)  |  partner x^s  |  f(x^s)  |  equal?")
print("-" * 56)

all_equal = True
for x in sorted(table):
    partner = xor(x, SECRET)
    same = table[x] == table[partner]
    all_equal = all_equal and same
    print(f"  {x}  |  {table[x]}   |     {partner}       |   {table[partner]}    |   {'yes' if same else 'NO'}")

# 4. A correct 2-to-1 oracle must send exactly two inputs to each output value.
print("\n f(x)  |  inputs that produce it")
print("-" * 40)
two_to_one = True
for out in sorted(set(table.values())):
    sources = sorted(x for x in table if table[x] == out)
    two_to_one = two_to_one and len(sources) == 2
    print(f" {out}  |  {', '.join(sources)}")

print(f"\nf(x) == f(x^s) for every x : {all_equal}")
print(f"every output hit exactly twice : {two_to_one}")
print("\nThe oracle never reveals s directly -- it only promises that inputs come")
print("in pairs {x, x^s}. Simon's algorithm is the trick for pulling s back out.")
