"""
Week_07 / T01.py -- Tutorial 7, Easy
Build the oracle for the constant function f(x) = 0, check its truth table,
then run Deutsch's algorithm on it and confirm the single query returns '0'.
"""

from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator

SHOTS = 1024
SEED = 7

sim = AerSimulator(seed_simulator=SEED)


def constant_zero_oracle():
    """
    U_f for f(x) = 0 on 2 qubits: qubit 0 holds the input x, qubit 1 is the
    output. The rule is |x>|y> -> |x>|y XOR f(x)>, and here f(x) is always 0,
    so y never changes and the oracle is the empty circuit.

    An empty circuit still counts as one oracle query -- the algorithm is not
    allowed to look inside the box, only to call it.
    """
    qc = QuantumCircuit(2, name='f(x)=0')
    qc.id(0)                              # identity placeholders, so the box
    qc.id(1)                              # is visible in the printed diagram
    return qc


def query(x):
    """Call the oracle classically on one input and read f(x) off qubit 1."""
    qc = QuantumCircuit(2, 1)
    if x == 1:
        qc.x(0)                           # prepare |x> in the input register
    qc.compose(constant_zero_oracle(), inplace=True)
    qc.measure(1, 0)                      # qubit 1 now holds 0 XOR f(x) = f(x)
    return int(sim.run(qc, shots=1).result().get_counts().popitem()[0])


def deutsch(oracle):
    """
    The full Deutsch circuit.

      q0 : |0> --H--[   ]--H--M      the input register, and the answer
      q1 : |1> --H--[U_f]-----       the ancilla, parked in |->

    Starting the ancilla in |1> and applying H puts it in |->, which is the
    eigenstate of X with eigenvalue -1. The oracle flips the ancilla when
    f(x) = 1, and flipping |-> just multiplies it by -1. So the phase (-1)^f(x)
    is kicked back onto the input register instead of being written anywhere.
    """
    qc = QuantumCircuit(2, 1)
    qc.x(1)                               # ancilla to |1>
    qc.h([0, 1])                          # input to |+>, ancilla to |->
    qc.barrier()
    qc.compose(oracle, inplace=True)
    qc.barrier()
    qc.h(0)                               # interference: the two paths recombine
    qc.measure(0, 0)
    return qc


# 1. Check the box really is constant before trusting any quantum result.
print("Oracle circuit for f(x) = 0")
print(constant_zero_oracle())

print("\n x | f(x)")
print("-" * 12)
table = {x: query(x) for x in (0, 1)}
for x in (0, 1):
    print(f" {x} |  {table[x]}")

is_constant = table[0] == table[1]
print(f"\nf(0) == f(1) : {is_constant}  ->  the function is "
      f"{'constant' if is_constant else 'balanced'}")
print("That check cost 2 classical queries. Deutsch's algorithm needs 1.")

# 2. Run the algorithm. One shot is enough; 1024 only proves it is not a fluke.
qc = deutsch(constant_zero_oracle())
print("\nDeutsch's circuit")
print(qc)

counts = sim.run(qc, shots=SHOTS).result().get_counts()

print(f"\n{SHOTS} shots\n")
print(" outcome | counts | fraction")
print("-" * 32)
for key in sorted(counts):
    print(f"    {key}    | {counts[key]:6d} |  {counts[key] / SHOTS:.3f}")

# 3. Read the answer. The measured bit IS the verdict, not a probability.
measured = max(counts, key=counts.get)
verdict = 'constant' if measured == '0' else 'balanced'

print(f"\nMeasured  : {measured}")
print(f"Verdict   : {verdict}")
print(f"Expected  : constant")
print(f"Correct   : {verdict == ('constant' if is_constant else 'balanced')}")
print(f"Every shot agreed : {len(counts) == 1}")

print("\nWhy the answer is certain rather than likely: for a constant f the two")
print("branches |0> and |1> of the input register pick up the SAME phase, so")
print("after the final H they interfere constructively on |0> and destructively")
print("on |1>. The amplitude on |1> is exactly zero, so '1' can never appear.")
print("\nT02 does the same with a balanced function, where the two branches pick")
print("up opposite phases and the interference lands on '1' instead.")
