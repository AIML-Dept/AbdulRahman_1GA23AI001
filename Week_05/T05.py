"""
Week_05 / T05.py -- Tutorial 5, Challenge
Tell a genuine quantum random bit generator apart from a biased classical
PRNG using a chi-square test: H0 is that the source is unbiased, rejected
when chi2 > 3.841 (1 degree of freedom, 5% significance).
"""

import random
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator

N = 2000            # bits drawn from each source
CRITICAL = 3.841    # chi-square critical value, df = 1, alpha = 0.05

# --- Source A: quantum. H puts the qubit in an equal superposition. -------
qc = QuantumCircuit(1, 1)
qc.h(0)
qc.measure(0, 0)
counts = AerSimulator().run(qc, shots=N).result().get_counts()
source_A = [counts.get('0', 0), counts.get('1', 0)]

# --- Source B: classical PRNG, secretly biased to 55% zeros. -------------
bits = [0 if random.random() < 0.55 else 1 for _ in range(N)]
source_B = [bits.count(0), bits.count(1)]


def chi_square(observed):
    """Compare observed [n0, n1] with the fair expectation N/2 each."""
    expected = sum(observed) / 2
    return sum((o - expected) ** 2 / expected for o in observed)


print(f"{N} bits per source, alpha = 0.05, reject H0 if chi2 > {CRITICAL}\n")
print("source |  n(0)   n(1)  |  chi2   |  verdict")
print("-" * 62)

for name, obs in [("  A   ", source_A), ("  B   ", source_B)]:
    x2 = chi_square(obs)
    verdict = "BIASED (reject H0)" if x2 > CRITICAL else "consistent with fair"
    print(f"{name} | {obs[0]:5d}  {obs[1]:5d}  | {x2:6.2f}  |  {verdict}")

print("\nReveal: A = quantum (H + measure), B = classical PRNG biased at p=0.55.")
print("The test flags B because a 5% bias over 2000 bits is far larger than shot noise.")
print("Note 1: a fair source still fails ~5% of runs -- that is the Type-I error rate.")
print("Note 2: this test only catches BIAS. An unbiased but predictable PRNG would")
print("        pass, so real certification also tests correlations and, for true")
print("        quantum randomness, uses Bell-inequality violation.")
