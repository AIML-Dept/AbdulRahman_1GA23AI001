"""
Week_07 / T03.py -- Tutorial 7, Hard
One make_oracle() that takes a function type as a parameter and builds the
matching U_f on the fly, covering all four single-bit functions, then runs
Deutsch's algorithm on each of them from the same code path.
"""

from qiskit import QuantumCircuit
from qiskit.quantum_info import Operator
from qiskit_aer import AerSimulator

SHOTS = 1024
SEED = 7

sim = AerSimulator(seed_simulator=SEED)

# There are exactly four functions from one bit to one bit, listed here as the
# pair (f(0), f(1)). Two are constant, two are balanced -- no other case exists.
FUNCTIONS = {
    'constant_0': (0, 0),       # f(x) = 0
    'constant_1': (1, 1),       # f(x) = 1
    'balanced_id': (0, 1),      # f(x) = x
    'balanced_not': (1, 0),     # f(x) = NOT x
}


def make_oracle(kind):
    """
    Build U_f for the named function. Rather than hard-coding four circuits,
    read the truth table and place gates from it:

      f(0) = 1  ->  the output must flip when x = 0, so wrap an X around the
                    control to make a CNOT that fires on |0> instead of |1>
      f(1) = 1  ->  the output must flip when x = 1, an ordinary CNOT

    Applying both rules to a constant function gives two flips that combine
    into a plain X on the ancilla, which is correct: f(x) = 1 flips y for
    every x. Applying neither leaves the empty circuit, which is f(x) = 0.
    """
    if kind not in FUNCTIONS:
        raise ValueError(f"unknown function type {kind!r}, "
                         f"expected one of {list(FUNCTIONS)}")

    f0, f1 = FUNCTIONS[kind]
    qc = QuantumCircuit(2, name=kind)

    if f0 == 1:
        qc.x(0)                           # temporarily relabel |0> as |1>
        qc.cx(0, 1)
        qc.x(0)                           # put the input back as it was
    if f1 == 1:
        qc.cx(0, 1)

    if len(qc.data) == 0:
        qc.id(0)                          # keep the empty box visible
        qc.id(1)

    return qc


def is_unitary_and_reversible(oracle):
    """
    A valid oracle has to be a unitary matrix -- every quantum gate is. This
    checks the built circuit against that requirement rather than assuming it.
    """
    return Operator(oracle).is_unitary()


def query(oracle, x):
    """Classical call: prepare |x>, apply U_f, read f(x) off the ancilla."""
    qc = QuantumCircuit(2, 1)
    if x == 1:
        qc.x(0)
    qc.compose(oracle, inplace=True)
    qc.measure(1, 0)
    return int(sim.run(qc, shots=1).result().get_counts().popitem()[0])


def deutsch(oracle):
    """Same circuit as T01 and T02, now fed whatever make_oracle() produced."""
    qc = QuantumCircuit(2, 1)
    qc.x(1)
    qc.h([0, 1])
    qc.barrier()
    qc.compose(oracle, inplace=True)
    qc.barrier()
    qc.h(0)
    qc.measure(0, 0)
    return qc


def classify(kind):
    """
    Run the algorithm once on the named function and return everything worth
    printing: the truth table read back from the box, the quantum verdict, and
    whether it agrees with the truth.
    """
    oracle = make_oracle(kind)
    table = (query(oracle, 0), query(oracle, 1))

    counts = sim.run(deutsch(oracle), shots=SHOTS).result().get_counts()
    measured = max(counts, key=counts.get)
    verdict = 'constant' if measured == '0' else 'balanced'

    truth = 'constant' if table[0] == table[1] else 'balanced'
    unanimous = len(counts) == 1
    return table, measured, verdict, truth, unanimous, oracle


# 1. Show that the builder really produces four different circuits.
print("make_oracle() output for each function type")
print("=" * 60)
for kind in FUNCTIONS:
    f0, f1 = FUNCTIONS[kind]
    print(f"\n{kind}   f(0) = {f0}, f(1) = {f1}")
    print(make_oracle(kind))

print("\nconstant_1 comes out as four gates because both rules fired. The two")
print("CNOTs together flip the ancilla whichever value x has, so the circuit is")
print("a plain X on qubit 1 written the long way. Left unsimplified on purpose:")
print("the builder follows the truth table blindly, which is what lets the same")
print("two rules work for any function without special cases.")

# 2. Run the algorithm on all four, from one loop.
print("\n" + "=" * 82)
print(" function     | f(0) f(1) | truth table read back | measured | verdict  | correct?")
print("-" * 82)

all_ok = True
all_unanimous = True
for kind in FUNCTIONS:
    table, measured, verdict, truth, unanimous, _ = classify(kind)
    ok = verdict == truth
    all_ok = all_ok and ok
    all_unanimous = all_unanimous and unanimous
    print(f" {kind:12s} | {FUNCTIONS[kind][0]:^4d} {FUNCTIONS[kind][1]:^4d} |"
          f"     f(0)={table[0]}, f(1)={table[1]}    |    {measured}     |"
          f" {verdict:8s} |   {'yes' if ok else 'NO'}")

print(f"\nAll four classified correctly : {all_ok}")
print(f"Every run unanimous over {SHOTS} shots : {all_unanimous}")

# 3. Guard rails: the oracles must be unitary, and an unknown name must fail
#    loudly rather than silently building the wrong box.
print("\nSanity checks on the builder")
print("-" * 44)
for kind in FUNCTIONS:
    print(f"  {kind:12s} unitary : {is_unitary_and_reversible(make_oracle(kind))}")

try:
    make_oracle('balanced_maybe')
except ValueError as err:
    print(f"  unknown name    : rejected -- {err}")

# 4. Cost comparison, which is the whole point of the exercise.
print("\nQueries needed to decide constant vs balanced")
print("-" * 52)
print("  classical, worst case : 2   (f(0) alone tells you nothing)")
print("  Deutsch's algorithm   : 1")
print("  speedup               : 2x, and it is exact, not probabilistic")

print("\nBuilding the oracle from its truth table instead of writing four fixed")
print("circuits is what makes the code extend. The same two rules -- flip the")
print("ancilla on the inputs where f is 1 -- generalise straight to n input")
print("qubits, which is the Deutsch-Jozsa oracle. There the classical worst")
print("case is 2^(n-1) + 1 queries and the quantum cost is still 1, so the 2x")
print("here is the smallest instance of an exponential separation.")

print("\nOne caveat worth stating plainly: make_oracle() is handed the answer.")
print("It reads FUNCTIONS to place its gates. That is fine for a demonstration,")
print("but it means the speedup measured here is about query COUNT, not about")
print("total work -- a real oracle is a black box someone else supplies, and")
print("nobody gets to look inside it.")

print("\nT04 turns this constant-vs-balanced test into a classification analogy.")
