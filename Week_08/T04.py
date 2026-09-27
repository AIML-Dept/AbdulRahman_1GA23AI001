"""
Week_08 / T04.py -- Tutorial 8, Real-world
Classical worst-case query count 2^(n-1) + 1 versus the single Deutsch-Jozsa
query, for n = 2 to 10: counted, checked by simulation, and plotted to show
the exponential gap.
"""

import matplotlib.pyplot as plt
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator

N_VALUES = list(range(2, 11))
SEED = 8

sim = AerSimulator(seed_simulator=SEED)


def classical_decide(f, n):
    """
    The best a deterministic classical algorithm can do: query inputs one by
    one and stop as soon as two answers differ (that proves 'balanced').
    If 2^(n-1) + 1 answers in a row agree, f cannot be balanced -- a balanced
    function only has 2^(n-1) of each value -- so it must be constant.
    Returns (verdict, number of queries used).
    """
    answers = []
    for x in range(2 ** (n - 1) + 1):
        answers.append(f(x))
        if answers[-1] != answers[0]:
            return 'balanced', len(answers)
    return 'constant', len(answers)


def deutsch_jozsa_one_shot(oracle, n):
    """Deutsch-Jozsa run with shots=1, i.e. exactly ONE call to the oracle."""
    qc = QuantumCircuit(n + 1, n)
    qc.x(n)
    qc.h(range(n + 1))
    qc.compose(oracle, inplace=True)
    qc.h(range(n))
    qc.measure(range(n), range(n))
    result = sim.run(qc, shots=1).result().get_counts().popitem()[0]
    return 'constant' if result == '0' * n else 'balanced'


classical, quantum = [], []
formula_ok, quantum_ok = True, True

print("Queries needed to decide constant vs balanced WITH CERTAINTY\n")
print("  n  | inputs 2^n | classical worst case | Deutsch-Jozsa | gap")
print("-" * 64)

for n in N_VALUES:
    # The two classical worst cases: a constant function, and an 'unlucky'
    # balanced one that answers 0 on the whole first half of the inputs.
    constant_f = lambda x: 0
    unlucky_f = lambda x: 1 if x >= 2 ** (n - 1) else 0
    worst = max(classical_decide(constant_f, n)[1], classical_decide(unlucky_f, n)[1])
    formula_ok = formula_ok and worst == 2 ** (n - 1) + 1

    # The same two functions as quantum oracles, each decided with 1 shot.
    constant_oracle = QuantumCircuit(n + 1)                  # f(x) = 0: empty box
    unlucky_oracle = QuantumCircuit(n + 1)
    unlucky_oracle.cx(n - 1, n)                              # f(x) = top bit of x
    quantum_ok = (quantum_ok
                  and deutsch_jozsa_one_shot(constant_oracle, n) == 'constant'
                  and deutsch_jozsa_one_shot(unlucky_oracle, n) == 'balanced')

    classical.append(worst)
    quantum.append(1)
    print(f" {n:2d}  | {2 ** n:10d} | {worst:20d} | {1:13d} | {worst:4d}x")

print(f"\nSimulated classical worst case equals 2^(n-1) + 1 for every n : {formula_ok}")
print(f"Deutsch-Jozsa right with a single query for every n          : {quantum_ok}")

# Real-world meaning: say each query to the black box takes 1 microsecond.
print("\nIf one query takes 1 microsecond, the classical worst case costs:")
for n in (10, 20, 40, 64):
    seconds = (2 ** (n - 1) + 1) * 1e-6
    if seconds < 1:
        time = f"{seconds * 1000:.3f} milliseconds"
    elif seconds < 86400:
        time = f"{seconds:.3f} seconds"
    elif seconds < 86400 * 365.25:
        time = f"{seconds / 86400:.1f} days"
    else:
        time = f"{seconds / (86400 * 365.25):,.0f} years"
    print(f"  n = {n:2d} : {2 ** (n - 1) + 1:>26,} queries  ->  {time}")
print("Deutsch-Jozsa needs 1 query (1 microsecond) at every one of these sizes.")

print("\nEach extra input bit DOUBLES the classical cost and leaves the quantum")
print("cost at 1 -- that is what an exponential gap means. (The comparison is")
print("with a classical method that must be 100% sure; REFLECTIONS.md covers")
print("the random-guessing alternative.)")

# Plot: normal scale on the left, log scale on the right.
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.5))

ax1.plot(N_VALUES, classical, 'o-', color='tab:red', label='classical worst case  2^(n-1)+1')
ax1.plot(N_VALUES, quantum, 's-', color='tab:blue', label='Deutsch-Jozsa  (always 1)')
ax1.fill_between(N_VALUES, quantum, classical, color='tab:red', alpha=0.1)
ax1.annotate(f"{classical[-1]} vs 1", (N_VALUES[-1], classical[-1]),
             textcoords='offset points', xytext=(-70, -5))
ax1.set_xticks(N_VALUES)
ax1.set_xlabel('number of input bits n')
ax1.set_ylabel('oracle queries')
ax1.set_title('Queries needed to be certain')
ax1.legend()
ax1.grid(alpha=0.3)

ax2.plot(N_VALUES, classical, 'o-', color='tab:red', label='classical worst case')
ax2.plot(N_VALUES, quantum, 's-', color='tab:blue', label='Deutsch-Jozsa')
for n, c in zip(N_VALUES, classical):
    ax2.annotate(str(c), (n, c), textcoords='offset points', xytext=(-8, 7), fontsize=8)
ax2.set_yscale('log', base=2)
ax2.set_yticks([1, 4, 16, 64, 256, 1024], ['1', '4', '16', '64', '256', '1024'])
ax2.set_ylim(0.7, 1500)                   # headroom for the top label
ax2.set_xticks(N_VALUES)
ax2.set_xlabel('number of input bits n')
ax2.set_ylabel('oracle queries (log scale)')
ax2.set_title('Same data on a log scale: a straight line = exponential')
ax2.legend()
ax2.grid(alpha=0.3)

plt.tight_layout()
plt.show()
