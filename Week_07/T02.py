"""
Week_07 / T02.py -- Tutorial 7, Medium
Build the oracle for the balanced function f(x) = x, confirm the single query
returns '1', and trace the statevector stage by stage to watch the phase
kickback put a minus sign on the input register.
"""

from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector
from qiskit_aer import AerSimulator

SHOTS = 1024
SEED = 7

sim = AerSimulator(seed_simulator=SEED)


def balanced_id_oracle():
    """
    U_f for f(x) = x. The rule |x>|y> -> |x>|y XOR f(x)> becomes
    |x>|y> -> |x>|y XOR x>, which is exactly a CNOT with qubit 0 controlling
    qubit 1. One gate, and it is balanced: f(0) = 0, f(1) = 1.
    """
    qc = QuantumCircuit(2, name='f(x)=x')
    qc.cx(0, 1)
    return qc


def query(x):
    """Call the oracle classically on one input and read f(x) off qubit 1."""
    qc = QuantumCircuit(2, 1)
    if x == 1:
        qc.x(0)
    qc.compose(balanced_id_oracle(), inplace=True)
    qc.measure(1, 0)
    return int(sim.run(qc, shots=1).result().get_counts().popitem()[0])


def deutsch(oracle):
    """Same circuit as T01: X and H on the ancilla, H on the input, U_f, H, measure."""
    qc = QuantumCircuit(2, 1)
    qc.x(1)
    qc.h([0, 1])
    qc.barrier()
    qc.compose(oracle, inplace=True)
    qc.barrier()
    qc.h(0)
    qc.measure(0, 0)
    return qc


def ket(state):
    """Print a 2-qubit statevector in Dirac notation, ASCII only, tiny terms dropped."""
    terms = []
    for i, amp in enumerate(state.data):
        if abs(amp) < 1e-9:
            continue
        label = format(i, '02b')          # Qiskit orders this as q1q0
        sign = '-' if amp.real < 0 else '+'
        terms.append(f"{sign} {abs(amp):.3f}|{label}>")
    text = ' '.join(terms)
    return text[2:] if text.startswith('+ ') else text


# 1. Confirm the box is balanced. Classically this needs both queries.
print("Oracle circuit for f(x) = x")
print(balanced_id_oracle())

print("\n x | f(x)")
print("-" * 12)
table = {x: query(x) for x in (0, 1)}
for x in (0, 1):
    print(f" {x} |  {table[x]}")

is_balanced = table[0] != table[1]
print(f"\nf(0) != f(1) : {is_balanced}  ->  the function is "
      f"{'balanced' if is_balanced else 'constant'}")

# 2. Run the algorithm.
qc = deutsch(balanced_id_oracle())
print("\nDeutsch's circuit")
print(qc)

counts = sim.run(qc, shots=SHOTS).result().get_counts()

print(f"\n{SHOTS} shots\n")
print(" outcome | counts | fraction")
print("-" * 32)
for key in sorted(counts):
    print(f"    {key}    | {counts[key]:6d} |  {counts[key] / SHOTS:.3f}")

measured = max(counts, key=counts.get)
verdict = 'constant' if measured == '0' else 'balanced'

print(f"\nMeasured  : {measured}")
print(f"Verdict   : {verdict}")
print(f"Expected  : balanced")
print(f"Correct   : {verdict == ('balanced' if is_balanced else 'constant')}")
print(f"Every shot agreed : {len(counts) == 1}")

# 3. Where the '1' comes from. Rebuild the circuit without measurement and
#    stop after each stage. Qiskit labels basis states |q1 q0>, so the LEFT
#    character is the ancilla and the right one is the input register.
print("\nStatevector after each stage   (labels are |q1 q0> = |ancilla input>)")
print("-" * 70)

stages = [
    ("start                 ", []),
    ("X on ancilla          ", ['x1']),
    ("H on both             ", ['x1', 'h']),
    ("oracle (CNOT)         ", ['x1', 'h', 'cx']),
    ("H on input            ", ['x1', 'h', 'cx', 'h0']),
]

for name, ops in stages:
    step = QuantumCircuit(2)
    for op in ops:
        if op == 'x1':
            step.x(1)
        elif op == 'h':
            step.h([0, 1])
        elif op == 'cx':
            step.cx(0, 1)
        elif op == 'h0':
            step.h(0)
    print(f"{name}: {ket(Statevector(step))}")

# 4. The kickback made explicit: factor the post-oracle state and read off the
#    phase sitting on each branch of the input register.
probe = QuantumCircuit(2)
probe.x(1)
probe.h([0, 1])
probe.cx(0, 1)
after = Statevector(probe)

print("\nPhase picked up by each input branch")
print("-" * 44)
print("  x  | f(x) | (-1)^f(x) | amplitude on |x>")
print("-" * 44)
for x in (0, 1):
    # amplitude of |x> paired with the ancilla's |0> component, i.e. index x
    amp = after.data[x]
    print(f"  {x}  |  {table[x]}   |    {(-1) ** table[x]:+d}     |     {amp.real:+.3f}")

print("\nThe ancilla started in |-> and came back in |-> -- unchanged, unmeasured,")
print("and carrying no record of anything. All the oracle did was multiply the")
print("input branch |x> by (-1)^f(x). That is phase kickback.")
print("\nBecause f is balanced the two branches got OPPOSITE signs, so the input")
print("register sat in |-> rather than |+>. The final H maps |-> to |1>, which")
print("is why every shot reads 1. A constant f would have given the same sign")
print("twice, leaving |+>, which the final H maps to |0> -- the T01 result.")
print("\nNote that the measured bit answers 'constant or balanced?' and nothing")
print("else. It never reveals whether f was x or NOT x, and no rearrangement of")
print("this circuit could, because a single query only ever buys one bit.")
print("\nT03 wraps all four single-bit functions behind one oracle builder.")
