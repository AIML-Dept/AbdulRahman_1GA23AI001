"""
Week_08 / T02.py -- Tutorial 8, Medium
Build a balanced oracle for 3 input qubits -- the parity function
f(x) = x0 XOR x1 XOR x2 -- check it is balanced, then run Deutsch-Jozsa once
and confirm the result is NOT all zeros.
"""

from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator

N = 3                   # input qubits q0, q1, q2. The output qubit is q3.
SHOTS = 1024
SEED = 8

sim = AerSimulator(seed_simulator=SEED)


def parity_oracle(n):
    """
    U_f for f(x) = x0 XOR x1 XOR ... XOR x(n-1).
    One CNOT from each input qubit onto the output: each CNOT XORs one bit
    into the output, so after all n of them the output holds the parity.
    Parity is balanced: exactly half of all inputs have an odd number of 1s.
    """
    qc = QuantumCircuit(n + 1, name='parity')
    for i in range(n):
        qc.cx(i, n)
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
    """Same circuit as T01: H on all, one oracle query, H on inputs, measure."""
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


oracle = parity_oracle(N)
print("Balanced oracle f(x) = x0 XOR x1 XOR x2   (q0-q2 = input, q3 = output)")
print(oracle)

# 1. Check the box really is balanced: four 0s and four 1s.
inputs = [format(v, f'0{N}b') for v in range(2 ** N)]
print("  x  | f(x) | phase (-1)^f(x)")
print("-" * 30)
outputs, phases = [], []
for x in inputs:
    fx = query(oracle, x)
    outputs.append(fx)
    phases.append((-1) ** fx)
    print(f" {x} |  {fx}   |  {phases[-1]:+d}")

print(f"number of 0s = {outputs.count(0)}, number of 1s = {outputs.count(1)}"
      f"  ->  balanced : {outputs.count(0) == outputs.count(1)}")
print(f"average phase = {sum(phases)}/{2 ** N} = {sum(phases) / 2 ** N:.0f}"
      f"  ->  this becomes the amplitude on |000>")

# 2. One quantum query.
qc = deutsch_jozsa(oracle)
print("\nDeutsch-Jozsa circuit")
print(qc)

raw = sim.run(qc, shots=SHOTS).result().get_counts()
counts = {key[::-1]: c for key, c in raw.items()}        # position i = qubit i
zeros_seen = '0' * N in counts

print(f"Counts over {SHOTS} shots : {counts}")
print(f"'000' ever measured     : {zeros_seen}  ->  verdict: "
      f"{'CONSTANT' if zeros_seen else 'BALANCED'}")

print("\nWhy '000' never appears: the final H gates put the AVERAGE phase onto")
print("|000>, and four +1s with four -1s average to exactly 0. So |000> has")
print("probability 0 on every shot, not just a small one.")
print("\nWhy it is exactly '111': the parity phase splits into one factor per")
print("qubit, (-1)^(x0+x1+x2) = (-1)^x0 * (-1)^x1 * (-1)^x2, so each input")
print("qubit ends up in |-> on its own, and H turns every |-> into |1>.")
print("Any non-zero string means 'balanced'; for the parity function it is 111.")
