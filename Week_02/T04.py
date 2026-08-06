"""
AML23703 Quantum Computing -- Tutorial 2, Exercise 4  [REAL-WORLD]
==================================================================
Task : Model a noisy communication channel by adding a small random phase
       error to a qubit state and observe the effect on the Bloch sphere.

Real-world framing: DEPHASING in a fibre-optic quantum link.
-----------------------------------------------------------
Alice encodes a bit in the X basis (|+> = 0, |-> = 1) and sends it to Bob.
The channel applies an unknown random phase rotation RZ(delta), with delta
drawn from a Gaussian of width sigma. Bob measures in the X basis.

The striking result: for any SINGLE transmission the Bloch vector merely
rotates -- it stays on the surface of the sphere and the state is still pure.
But Bob does not know delta, so from his point of view the state is the
AVERAGE over all possible delta, and that average vector shrinks INTO the
sphere. That shrinkage is decoherence.

Theory to check against: for Gaussian phase noise the averaged Bloch vector
length is exactly exp(-sigma^2 / 2), and Bob's bit error rate is
(1 - exp(-sigma^2 / 2)) / 2.
"""

import matplotlib.pyplot as plt
import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import Pauli, Statevector
from qiskit.visualization import plot_bloch_vector
from qiskit_aer import AerSimulator

rng = np.random.default_rng(seed=7)

SIGMAS = [0.0, 0.25, 0.5, 1.0, 1.5, 2.5]   # channel noise strength, radians
TRIALS = 300                                # independent transmissions per sigma
SHOTS = 64                                  # Bob's measurements per transmission

simulator = AerSimulator()


def bloch_vector(statevector):
    return np.array([
        statevector.expectation_value(Pauli("X")).real,
        statevector.expectation_value(Pauli("Y")).real,
        statevector.expectation_value(Pauli("Z")).real,
    ])


# ---------------------------------------------------------------------
# 1. Show one single noisy transmission first
# ---------------------------------------------------------------------
demo_delta = 0.6
demo = QuantumCircuit(1)
demo.h(0)                       # Alice prepares |+>
demo.rz(demo_delta, 0)          # the channel kicks the phase

print("--- One transmission through the noisy channel ---")
print(demo.draw(output="text"))

alice = Statevector.from_label("+")   # what Alice launched into the channel
bob = Statevector(demo)               # what arrived at the far end

print(f"\nAlice sent   : {np.round(alice.data, 4)}   Bloch {np.round(bloch_vector(alice), 4)}")
print(f"Bob received : {np.round(bob.data, 4)}   Bloch {np.round(bloch_vector(bob), 4)}")
print(f"Phase kick   : delta = {demo_delta:.3f} rad ({np.degrees(demo_delta):.1f} deg)")
print(f"Vector length: {np.linalg.norm(bloch_vector(bob)):.6f}  <-- still 1, still a PURE state")
print("A single known phase error is not information loss -- it is a rotation,")
print("and Bob could undo it exactly if he knew delta.")

# ---------------------------------------------------------------------
# 2. Sweep the noise strength
# ---------------------------------------------------------------------
print(f"\n--- Sweeping channel noise ({TRIALS} transmissions x {SHOTS} shots each) ---")
print(f"{'sigma':>7}{'|avg Bloch|':>14}{'theory':>10}{'error rate':>13}{'theory':>10}")

averaged_vectors = []
measured_lengths = []
theory_lengths = []
error_rates = []
theory_errors = []

for sigma in SIGMAS:
    deltas = rng.normal(0.0, sigma, TRIALS)

    # --- (a) exact Bloch vectors, averaged over the unknown phase ---
    vectors = []
    circuits = []
    for delta in deltas:
        qc = QuantumCircuit(1)
        qc.h(0)                        # Alice: prepare |+>
        qc.rz(delta, 0)                # channel: random phase
        vectors.append(bloch_vector(Statevector(qc)))

        # --- (b) Bob's X-basis measurement: H maps |+>/|-> onto |0>/|1> ---
        meas = qc.copy()
        meas.h(0)
        meas.measure_all()
        circuits.append(meas)

    average_vector = np.mean(vectors, axis=0)
    averaged_vectors.append(average_vector)
    length = np.linalg.norm(average_vector)
    measured_lengths.append(length)
    theory_lengths.append(np.exp(-sigma ** 2 / 2))

    # Bob's errors: Alice sent "0", so any '1' Bob records is a bit flip
    results = simulator.run(circuits, shots=SHOTS).result()
    all_counts = results.get_counts()
    if isinstance(all_counts, dict):
        all_counts = [all_counts]
    errors = sum(counts.get("1", 0) for counts in all_counts)
    rate = errors / (TRIALS * SHOTS)
    error_rates.append(rate)
    theory_errors.append((1 - np.exp(-sigma ** 2 / 2)) / 2)

    print(f"{sigma:>7.2f}{length:>14.4f}{theory_lengths[-1]:>10.4f}"
          f"{rate:>13.4f}{theory_errors[-1]:>10.4f}")

print("\nThe measured averaged-vector length tracks exp(-sigma^2/2) and the bit")
print("error rate tracks (1 - exp(-sigma^2/2))/2, confirming the model.")

# ---------------------------------------------------------------------
# 3. Interpretation
# ---------------------------------------------------------------------
print("\n--- Interpretation ---")
print("Each individual qubit stays pure: |Bloch| = 1 for every transmission.")
print("But averaging over an UNKNOWN phase shrinks the vector towards the")
print("centre of the sphere. At the centre the state is maximally mixed and")
print("Bob's measurement is a coin toss -- the message is completely lost.")
print("\nCritically, this noise is invisible in the Z basis: the phase never")
print("changes P(0) or P(1) there. It only destroys information encoded in")
print("the PHASE, which is exactly what X-basis encoding relies on. This is")
print("why real quantum links need active phase stabilisation, and why")
print("phase-flip error correction exists alongside bit-flip correction.")

# ---------------------------------------------------------------------
# 4. Plots
# ---------------------------------------------------------------------
fig = plt.figure(figsize=(13, 4.5))

# Row 1: averaged Bloch vector shrinking, at three noise levels
for position, index in enumerate([0, 2, 4]):
    ax = fig.add_subplot(1, 3, position + 1, projection="3d")
    plot_bloch_vector(
        list(averaged_vectors[index]),
        title=f"sigma = {SIGMAS[index]:.2f}\n|v| = {measured_lengths[index]:.3f}",
        ax=ax,
    )

plt.tight_layout()
plt.show()

# Figure 2: the two quantitative curves
fig2, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4.5))
ax1.plot(SIGMAS, measured_lengths, "o-", color="steelblue", label="Simulated")
ax1.plot(SIGMAS, theory_lengths, "k--", alpha=0.7, label="Theory exp(-s^2/2)")
ax1.set_xlabel("Channel noise sigma (radians)")
ax1.set_ylabel("Averaged Bloch vector length")
ax1.set_title("Coherence decays with phase noise")
ax1.grid(alpha=0.3)
ax1.legend()

ax2.plot(SIGMAS, error_rates, "o-", color="indianred", label="Simulated")
ax2.plot(SIGMAS, theory_errors, "k--", alpha=0.7, label="Theory")
ax2.axhline(0.5, color="grey", linestyle=":", label="Coin toss (no information)")
ax2.set_xlabel("Channel noise sigma (radians)")
ax2.set_ylabel("Bob's bit error rate")
ax2.set_title("Bit error rate saturates at 50%")
ax2.grid(alpha=0.3)
ax2.legend()

plt.tight_layout()
plt.show()
