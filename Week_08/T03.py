"""
Week_08 / T03.py -- Tutorial 8, Hard
One Deutsch-Jozsa implementation that takes n as a parameter. For each
n = 2 to 5 it automatically builds both constant oracles and a random
balanced oracle, checks each against its truth table, then classifies them.
"""

import random
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator

N_VALUES = [2, 3, 4, 5]
KINDS = ['constant_0', 'constant_1', 'balanced']
SHOTS = 1024
SEED = 8

random.seed(SEED)
sim = AerSimulator(seed_simulator=SEED)


def constant_oracle(n, value):
    """f(x) = value for every x: an empty box (value 0) or one X (value 1)."""
    qc = QuantumCircuit(n + 1)
    if value == 1:
        qc.x(n)
    return qc


def balanced_oracle(n, s, flip):
    """
    f(x) = (s0*x0 XOR s1*x1 XOR ... XOR s(n-1)*x(n-1)) XOR flip
    One CNOT from every input qubit i where s has a '1', plus an X on the
    output if flip = 1. T02's parity function is the case s = '111', flip = 0.

    It is balanced whenever s is not all zeros: pick a position where s has
    a 1; flipping that input bit always flips f, so the inputs pair up into
    (one gives 0, one gives 1) -- exactly half and half.
    """
    qc = QuantumCircuit(n + 1)
    for i, bit in enumerate(s):
        if bit == '1':
            qc.cx(i, n)
    if flip == 1:
        qc.x(n)
    return qc


def make_oracle(n, kind):
    """
    Automatically build U_f for n input qubits.
      'constant_0', 'constant_1' : the only two constant functions there are
      'balanced'                 : a random balanced one (random s and flip)
    """
    if kind == 'constant_0':
        return constant_oracle(n, 0), "f(x) = 0"
    if kind == 'constant_1':
        return constant_oracle(n, 1), "f(x) = 1"
    if kind == 'balanced':
        s = format(random.randrange(1, 2 ** n), f'0{n}b')    # never all zeros
        flip = random.randint(0, 1)
        label = f"f(x) = s.x{' XOR 1' if flip else ''}, s = {s}"
        return balanced_oracle(n, s, flip), label
    raise ValueError(f"unknown kind {kind!r}, expected one of {KINDS}")


def query(oracle, x):
    """One classical query: prepare |x>, apply U_f, read f(x) off the output."""
    n = oracle.num_qubits - 1
    qc = QuantumCircuit(n + 1, 1)
    for i, bit in enumerate(x):
        if bit == '1':
            qc.x(i)                       # character i of x goes on qubit i
    qc.compose(oracle, inplace=True)
    qc.measure(n, 0)
    return int(sim.run(qc, shots=1).result().get_counts().popitem()[0])


def true_kind(oracle, n):
    """Ask the oracle about all 2^n inputs (the slow classical way) to label it."""
    ones = sum(query(oracle, format(v, f'0{n}b')) for v in range(2 ** n))
    if ones in (0, 2 ** n):
        return 'constant', ones
    if ones == 2 ** (n - 1):
        return 'balanced', ones
    return 'neither', ones


def deutsch_jozsa(oracle, n):
    """The same circuit as T01 and T02, now for any number of input qubits n."""
    qc = QuantumCircuit(n + 1, n)
    qc.x(n)
    qc.h(range(n + 1))
    qc.barrier()
    qc.compose(oracle, inplace=True)      # the ONE oracle query
    qc.barrier()
    qc.h(range(n))
    qc.measure(range(n), range(n))
    return qc


def classify(oracle, n):
    """Run Deutsch-Jozsa. All zeros -> constant, anything else -> balanced."""
    raw = sim.run(deutsch_jozsa(oracle, n), shots=SHOTS).result().get_counts()
    counts = {key[::-1]: c for key, c in raw.items()}    # position i = qubit i
    measured = max(counts, key=counts.get)
    verdict = 'constant' if measured == '0' * n else 'balanced'
    return verdict, measured, len(counts) == 1


print(f"Each oracle is checked on all 2^n inputs, then classified with ONE query "
      f"({SHOTS} shots)\n")
print(" n | oracle built                  | f(x)=1 on | really is | measured | verdict  | correct")
print("-" * 92)

all_correct, all_unanimous = True, True
example = None
for n in N_VALUES:
    for kind in KINDS:
        oracle, label = make_oracle(n, kind)
        truth, ones = true_kind(oracle, n)                # slow classical check
        verdict, measured, unanimous = classify(oracle, n)  # one quantum query

        expected = 'constant' if kind.startswith('constant') else 'balanced'
        correct = (truth == expected) and (verdict == expected)
        all_correct = all_correct and correct
        all_unanimous = all_unanimous and unanimous
        print(f" {n} | {label:29s} | {ones:2d} of {2 ** n:2d}  | {truth:9s} |"
              f" {measured:>8s} | {verdict:8s} | {'yes' if correct else 'NO'}")

        if n == N_VALUES[-1] and kind == 'balanced':     # keep one to print
            example = (label, deutsch_jozsa(oracle, n))
    print("-" * 92)

print(f"All {len(KINDS) * len(N_VALUES)} oracles classified correctly : {all_correct}")
print(f"Every run gave the same answer on all {SHOTS} shots : {all_unanimous}")

print(f"\nExample: the circuit built automatically for n = {N_VALUES[-1]}, {example[0]}")
print(example[1])

print("Nothing in deutsch_jozsa() changes with n -- only the size of the")
print("registers. The number of oracle queries stays at 1, while a classical")
print(f"algorithm needs up to 2^(n-1) + 1 of them "
      f"({2 ** (N_VALUES[-1] - 1) + 1} at n = {N_VALUES[-1]}).")
print("\nFor these balanced oracles the measured string is exactly s. That is")
print("a bonus (the Bernstein-Vazirani idea): for Deutsch-Jozsa only 'all zeros")
print("or not' matters, and any non-zero string means balanced.")
