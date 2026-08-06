"""
AML23703 Quantum Computing -- Tutorial 1, Exercise 4  [REAL-WORLD]
==================================================================
Task : Simulate a simple random-number generator using qubit superposition
       and compare its statistical randomness with Python's pseudo-random
       generator.

Real-world framing: generating a one-time password (OTP).
-------------------------------------------------------
Banking OTPs need digits 0-9. Four qubits give us 0-15, so naively taking
value % 10 would make the digits 0-5 more likely than 6-9 -- the classic
"modulo bias" bug. We instead use REJECTION SAMPLING: throw away any raw
value of 10-15 and keep the rest. That is precisely what a real hardware
RNG driver does.

We then compare the quantum digits against Python's Mersenne Twister on
three fronts: frequency, entropy, and -- the one that actually matters --
REPRODUCIBILITY.
"""

import random

import matplotlib.pyplot as plt
import numpy as np
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator
from scipy.stats import chisquare

N_QUBITS = 4          # 4 qubits -> raw values 0..15
RAW_SHOTS = 8192      # about 5/8 of these survive rejection
OTP_LENGTH = 6

simulator = AerSimulator()


# ---------------------------------------------------------------------
# 1. The quantum random digit source
# ---------------------------------------------------------------------
def quantum_digits(n_shots):
    """Return a list of uniformly distributed digits 0-9 from qubit measurement."""
    qc = QuantumCircuit(N_QUBITS, N_QUBITS)
    qc.h(range(N_QUBITS))                              # equal superposition of 0..15
    qc.measure(range(N_QUBITS), range(N_QUBITS))

    # memory=True keeps every individual shot instead of only the tallies
    result = simulator.run(qc, shots=n_shots, memory=True).result()
    raw_values = [int(bits, 2) for bits in result.get_memory()]

    kept = [v for v in raw_values if v < 10]           # rejection sampling
    return kept, raw_values


print("--- Quantum RNG circuit ---")
demo = QuantumCircuit(N_QUBITS, N_QUBITS)
demo.h(range(N_QUBITS))
demo.measure(range(N_QUBITS), range(N_QUBITS))
print(demo.draw(output="text"))

q_digits, raw = quantum_digits(RAW_SHOTS)
rejected = len(raw) - len(q_digits)

print(f"\nRaw 4-bit samples drawn : {len(raw)}")
print(f"Rejected (values 10-15) : {rejected}  ({rejected / len(raw):.1%}, theory 37.5%)")
print(f"Usable digits 0-9       : {len(q_digits)}")

# ---------------------------------------------------------------------
# 2. Classical comparison sample of the same size
# ---------------------------------------------------------------------
random.seed(1729)
p_digits = [random.randint(0, 9) for _ in range(len(q_digits))]


# ---------------------------------------------------------------------
# 3. Statistical comparison
# ---------------------------------------------------------------------
def analyse(name, digits):
    counts = np.array([digits.count(d) for d in range(10)])
    n = len(digits)
    probs = counts / n

    chi2, p_value = chisquare(counts)
    entropy = -np.sum(probs[probs > 0] * np.log2(probs[probs > 0]))

    print(f"\n=== {name} ===")
    print(f"  Sample size      : {n}")
    print(f"  Mean digit       : {np.mean(digits):.3f}   (theory 4.500)")
    print(f"  Shannon entropy  : {entropy:.4f} / {np.log2(10):.4f} bits")
    print(f"  Chi-square       : {chi2:.3f}")
    print(f"  p-value          : {p_value:.4f}  ({'uniform' if p_value > 0.05 else 'biased'})")
    return counts


counts_q = analyse("QUANTUM RNG (qubit superposition)", q_digits)
counts_p = analyse("CLASSICAL PRNG (Mersenne Twister)", p_digits)

print("\nBoth pass the uniformity test. Statistically they are indistinguishable")
print("-- which is the point: a PRNG is *statistically* excellent. The real")
print("difference shows up next.")

# ---------------------------------------------------------------------
# 4. The difference that matters: reproducibility
# ---------------------------------------------------------------------
print("\n--- Reproducibility test ---")

random.seed(2026)
prng_run_1 = [random.randint(0, 9) for _ in range(10)]
random.seed(2026)                      # same seed
prng_run_2 = [random.randint(0, 9) for _ in range(10)]

qrng_run_1 = quantum_digits(64)[0][:10]
qrng_run_2 = quantum_digits(64)[0][:10]

print(f"  PRNG with seed 2026, run 1 : {prng_run_1}")
print(f"  PRNG with seed 2026, run 2 : {prng_run_2}")
print(f"  Identical?                 : {prng_run_1 == prng_run_2}  <-- fully predictable if the seed leaks")
print()
print(f"  QRNG run 1                 : {qrng_run_1}")
print(f"  QRNG run 2                 : {qrng_run_2}")
print(f"  Identical?                 : {qrng_run_1 == qrng_run_2}  <-- no seed exists to steal")

print("\nA PRNG is deterministic: anyone who learns the seed and the algorithm")
print("can regenerate every OTP you will ever issue. True quantum randomness")
print("comes from measurement collapse, so there is no internal state to guess.")
print("(On a simulator the randomness is still classical underneath -- only")
print("real hardware or a QRNG device gives genuine quantum entropy.)")

# ---------------------------------------------------------------------
# 5. Deliverable: an actual OTP
# ---------------------------------------------------------------------
otp = "".join(str(d) for d in quantum_digits(64)[0][:OTP_LENGTH])
print(f"\n--- Generated {OTP_LENGTH}-digit quantum OTP: {otp} ---")

# ---------------------------------------------------------------------
# 6. Visual comparison
# ---------------------------------------------------------------------
fig, axes = plt.subplots(1, 2, figsize=(12, 4), sharey=True)
expected_line = len(q_digits) / 10

axes[0].bar(range(10), counts_q, color="mediumpurple", alpha=0.85)
axes[0].axhline(expected_line, color="black", linestyle="--", label="Expected")
axes[0].set_title("Quantum RNG digit frequency")
axes[0].set_xlabel("Digit")
axes[0].set_ylabel("Frequency")
axes[0].set_xticks(range(10))
axes[0].legend()

axes[1].bar(range(10), counts_p, color="crimson", alpha=0.85)
axes[1].axhline(expected_line, color="black", linestyle="--", label="Expected")
axes[1].set_title("Python PRNG digit frequency")
axes[1].set_xlabel("Digit")
axes[1].set_xticks(range(10))
axes[1].legend()

plt.tight_layout()
plt.show()
