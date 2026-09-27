"""
Week_08 / T05.py -- Tutorial 8, Challenge
A random oracle generator that picks a balanced function uniformly from ALL
balanced functions on n bits, builds its oracle from the truth table, and
checks that Deutsch-Jozsa classifies every one of them correctly.
"""

import random
from math import comb
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator

N_VALUES = [2, 3, 4, 5]
TRIALS = 25             # random balanced functions tested for each n
SHOTS = 1024
SEED = 8

random.seed(SEED)
sim = AerSimulator(seed_simulator=SEED)


def all_inputs(n):
    """Every n-bit input as a string; character i goes on qubit i."""
    return [format(v, f'0{n}b') for v in range(2 ** n)]


def random_balanced_function(n):
    """
    Choose WHICH half of the 2^n inputs output 1, completely at random.
    Every half is equally likely, so this picks uniformly from ALL
    C(2^n, 2^(n-1)) balanced functions -- not just the tidy ones like the
    parity function of T02. Returned as a truth table {x: f(x)}.
    """
    inputs = all_inputs(n)
    ones = random.sample(inputs, 2 ** (n - 1))
    return {x: (1 if x in ones else 0) for x in inputs}


def oracle_from_table(table, n):
    """
    Build U_f for ANY truth table. For every input x with f(x) = 1, flip the
    output qubit only when the input register holds exactly x:
      1. X on each input qubit where x has a '0' (now the pattern x reads 11..1)
      2. a multi-controlled X: all n inputs are controls, the output is target
      3. the same X gates again, to put the inputs back
    """
    qc = QuantumCircuit(n + 1)
    for x, fx in table.items():
        if fx == 1:
            zeros = [i for i, bit in enumerate(x) if bit == '0']
            for i in zeros:
                qc.x(i)
            qc.mcx(list(range(n)), n)
            for i in zeros:
                qc.x(i)
    return qc


def query(oracle, x):
    """One classical query: prepare |x>, apply U_f, read f(x) off the output."""
    n = oracle.num_qubits - 1
    qc = QuantumCircuit(n + 1, 1)
    for i, bit in enumerate(x):
        if bit == '1':
            qc.x(i)
    qc.compose(oracle, inplace=True)
    qc.measure(n, 0)
    return int(sim.run(qc, shots=1).result().get_counts().popitem()[0])


def deutsch_jozsa_counts(oracle, n):
    """Run Deutsch-Jozsa and return the counts, flipped so position i = qubit i."""
    qc = QuantumCircuit(n + 1, n)
    qc.x(n)
    qc.h(range(n + 1))
    qc.compose(oracle, inplace=True)      # the ONE oracle query
    qc.h(range(n))
    qc.measure(range(n), range(n))
    raw = sim.run(qc, shots=SHOTS).result().get_counts()
    return {key[::-1]: c for key, c in raw.items()}


# 1. One example in full, for n = 3.
n = 3
table = random_balanced_function(n)
oracle = oracle_from_table(table, n)

print(f"Example: a random balanced function for n = {n}")
print("  x  | f(x) wanted | f(x) read back from the oracle")
print("-" * 50)
for x in all_inputs(n):
    print(f" {x} |      {table[x]}      |      {query(oracle, x)}")

print(f"\nIts oracle: one multi-controlled X for each of the {2 ** (n - 1)} inputs "
      f"where f(x) = 1")
print(oracle)

counts = deutsch_jozsa_counts(oracle, n)
print(f"Deutsch-Jozsa counts : {dict(sorted(counts.items()))}")
print(f"'000' ever measured  : {'000' in counts}  ->  verdict: "
      f"{'CONSTANT' if '000' in counts else 'BALANCED'}")
print("A messy function gives a spread of outcomes -- but never '000'.")

# 2. The real test: many random balanced functions for every n.
print(f"\n{TRIALS} random balanced functions per n, {SHOTS} shots each\n")
print(" n | balanced functions | tested | different | oracle matches | classified")
print("   |   that exist       |        | functions | truth table    | balanced")
print("-" * 75)

grand_total, grand_correct = 0, 0
for n in N_VALUES:
    seen = set()
    oracles_ok, correct = 0, 0
    for _ in range(TRIALS):
        table = random_balanced_function(n)
        oracle = oracle_from_table(table, n)
        seen.add(tuple(table.values()))

        # Check the circuit really computes the table it was built from.
        if all(query(oracle, x) == table[x] for x in table):
            oracles_ok += 1

        # Balanced is right exactly when '00..0' NEVER comes up.
        if '0' * n not in deutsch_jozsa_counts(oracle, n):
            correct += 1

    grand_total += TRIALS
    grand_correct += correct
    print(f" {n} | {comb(2 ** n, 2 ** (n - 1)):18,} | {TRIALS:6d} | {len(seen):9d} |"
          f" {oracles_ok:3d} / {TRIALS:<3d}      | {correct:3d} / {TRIALS}")

print(f"\nClassified correctly: {grand_correct} / {grand_total} random balanced functions")
print("Each oracle needs 2^(n-1) multi-controlled gates, so the BOX grows with n,")
print("but Deutsch-Jozsa still opens it exactly once.")

# 3. Extra, for Reflection Q2: break the promise on purpose.
#    Same builder, n = 3, with f(x) = 1 on k inputs for every k from 0 to 8.
#    Theory: P('000') = (average phase)^2 = ((8 - 2k) / 8)^2.
n = 3
print("\nExtra: what if f is NEITHER constant NOR balanced?  (n = 3)")
print(" k = inputs with f=1 | really is | P('000') theory | P('000') measured")
print("-" * 70)
for k in range(2 ** n + 1):
    ones = random.sample(all_inputs(n), k)
    table = {x: (1 if x in ones else 0) for x in all_inputs(n)}
    counts = deutsch_jozsa_counts(oracle_from_table(table, n), n)

    kind = 'constant' if k in (0, 2 ** n) else 'balanced' if k == 2 ** (n - 1) else 'NEITHER'
    theory = ((2 ** n - 2 * k) / 2 ** n) ** 2
    measured = counts.get('000', 0) / SHOTS
    print(f"          {k}          | {kind:9s} |      {theory:.4f}     |      {measured:.4f}")

print("\nOnly k = 0, 4 and 8 give a certain answer. For every other k the")
print("algorithm still prints SOMETHING, but it is a weighted coin flip: with")
print("k = 1 it says 'constant' about 56% of the time and 'balanced' 44%.")
print("It cannot tell you the promise was broken -- see REFLECTIONS.md, Q2.")
