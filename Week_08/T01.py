"""
Week_08 / T01.py -- Tutorial 8, Easy
Build a constant-function oracle for 3 input qubits, check its truth table,
then run Deutsch-Jozsa once and confirm the result is all zeros ('000').
"""

from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator

N = 3                   # input qubits q0, q1, q2. The output qubit is q3.
SHOTS = 1024
SEED = 8

sim = AerSimulator(seed_simulator=SEED)


def constant_oracle(n, value):
    """
    U_f for a constant function:  |x>|y>  ->  |x>|y XOR value>
      value = 0 : the output never changes, so the box is empty
      value = 1 : the output flips for EVERY input, which is one X gate
    The input qubits are never touched, because a constant f ignores x.
    """
    qc = QuantumCircuit(n + 1, name=f'f(x)={value}')
    if value == 1:
        qc.x(n)
    else:
        qc.id(n)                          # placeholder so the empty box shows
    return qc


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


def deutsch_jozsa(oracle):
    """
      inputs q0..q2 : |0> --H--[     ]--H--M
      output q3     : |1> --H--[ U_f ]-----      (parked in |->)

    The H gates put all 8 inputs into superposition. Because the output qubit
    is |->, every flip becomes a phase (-1)^f(x) on the inputs (phase
    kickback, as in Week 7). The final H gates make those phases interfere.
    """
    n = oracle.num_qubits - 1
    qc = QuantumCircuit(n + 1, n)
    qc.x(n)                               # output qubit to |1>
    qc.h(range(n + 1))                    # inputs to |+>, output to |->
    qc.barrier()
    qc.compose(oracle, inplace=True)      # the ONE oracle query
    qc.barrier()
    qc.h(range(n))
    qc.measure(range(n), range(n))
    return qc


inputs = [format(v, f'0{N}b') for v in range(2 ** N)]

for value in (0, 1):
    oracle = constant_oracle(N, value)
    print("=" * 52)
    print(f"Constant oracle f(x) = {value}")
    print("=" * 52)

    # 1. Check the box really is constant by querying all 8 inputs.
    print("  x  | f(x) | phase (-1)^f(x)")
    print("-" * 30)
    phases = []
    for x in inputs:
        fx = query(oracle, x)
        phases.append((-1) ** fx)
        print(f" {x} |  {fx}   |  {phases[-1]:+d}")
    print(f"average phase = {sum(phases)}/{2 ** N} = {sum(phases) / 2 ** N:+.0f}"
          f"  ->  this becomes the amplitude on |000>")

    # 2. Now ask the quantum computer, with a single query.
    qc = deutsch_jozsa(oracle)
    print("\nDeutsch-Jozsa circuit (q0-q2 = input, q3 = output)")
    print(qc)

    raw = sim.run(qc, shots=SHOTS).result().get_counts()
    counts = {key[::-1]: c for key, c in raw.items()}    # position i = qubit i
    all_zero = counts == {'0' * N: SHOTS}

    print(f"Counts over {SHOTS} shots : {counts}")
    print(f"All zeros on every shot : {all_zero}  ->  verdict: "
          f"{'CONSTANT' if all_zero else 'BALANCED'}\n")

print("Why '000' every time: the final H gates put the AVERAGE of the 8 phases")
print("onto |000>. A constant f gives every input the SAME phase (+1 for f=0,")
print("-1 for f=1), so the average is +1 or -1: |000> gets probability 1 and")
print("every other outcome gets exactly 0. The -1 is only a global phase, which")
print("cannot be measured.")

print(f"\nQueries to be certain for n = {N}")
print(f"  classical worst case : 2^({N}-1) + 1 = {2 ** (N - 1) + 1}")
print("  Deutsch-Jozsa        : 1")
