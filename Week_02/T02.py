"""
AML23703 Quantum Computing -- Tutorial 2, Exercise 2  [MEDIUM]
==============================================================
Task : Apply a Hadamard gate followed by a phase (S) gate and plot the
       resulting state on the Bloch sphere.

Approach
--------
Plotting only the final state hides the most important fact about the S
gate: it changes NOTHING that a normal measurement can see. So this script
snapshots the qubit at all three stages and prints the polar angle theta and
azimuthal angle phi at each step.

  |0>      -> theta = 0    (north pole)
  after H  -> theta = 90   phi = 0     (+x axis)
  after S  -> theta = 90   phi = 90    (+y axis)

theta controls the measurement probabilities; phi does not. S moves only phi,
so the 50/50 split is untouched -- the phase is "invisible" until we
interfere the qubit with something else.
"""

import matplotlib.pyplot as plt
import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import Pauli, Statevector
from qiskit.visualization import plot_bloch_vector


def bloch_vector(statevector):
    return np.array([
        statevector.expectation_value(Pauli("X")).real,
        statevector.expectation_value(Pauli("Y")).real,
        statevector.expectation_value(Pauli("Z")).real,
    ])


def spherical_angles(vector):
    """Convert a Bloch vector to (theta, phi) in degrees."""
    x, y, z = vector
    theta = np.degrees(np.arccos(np.clip(z, -1.0, 1.0)))
    phi = np.degrees(np.arctan2(y, x)) % 360
    return theta, phi


# ---------------------------------------------------------------------
# 1. Capture the state at each stage
# ---------------------------------------------------------------------
stages = []

qc = QuantumCircuit(1)
stages.append(("Stage 0: initial |0>", Statevector(qc)))

qc.h(0)                                   # superposition
stages.append(("Stage 1: after H", Statevector(qc)))

qc.s(0)                                   # S = phase gate, adds i to the |1> amplitude
stages.append(("Stage 2: after S", Statevector(qc)))

print("--- Circuit Diagram ---")
print(qc.draw(output="text"))

# ---------------------------------------------------------------------
# 2. Report every stage
# ---------------------------------------------------------------------
vectors = []
for title, state in stages:
    vector = bloch_vector(state)
    vectors.append(vector)
    theta, phi = spherical_angles(vector)
    probabilities = np.abs(state.data) ** 2

    print(f"\n{title}")
    print(f"  Statevector   : {np.round(state.data, 4)}")
    print(f"  Bloch vector  : (x={vector[0]:+.4f}, y={vector[1]:+.4f}, z={vector[2]:+.4f})")
    print(f"  Angles        : theta = {theta:6.2f} deg   phi = {phi:6.2f} deg")
    print(f"  P(measure 0)  : {probabilities[0]:.4f}      P(measure 1) : {probabilities[1]:.4f}")

# ---------------------------------------------------------------------
# 3. The point of the exercise
# ---------------------------------------------------------------------
theta_after_h, phi_after_h = spherical_angles(vectors[1])
theta_after_s, phi_after_s = spherical_angles(vectors[2])

print("\n--- What each gate actually did ---")
print(f"H : moved the state off the north pole, theta 0 -> {theta_after_h:.0f} deg.")
print("    This is what creates the 50/50 measurement split.")
print(f"S : rotated the state around the equator, phi {phi_after_h:.0f} -> {phi_after_s:.0f} deg,")
print(f"    while theta stayed at {theta_after_s:.0f} deg.")
print("\nBecause the measurement probabilities depend only on theta, the S gate")
print("leaves them completely unchanged -- both stages read 0.5 / 0.5 above.")
print("The phase is real and physical, but it only becomes observable once")
print("the state interferes with another path (e.g. a second Hadamard).")

# ---------------------------------------------------------------------
# 4. All three stages on one figure
# ---------------------------------------------------------------------
fig = plt.figure(figsize=(13, 4.5))
for i, ((title, _), vector) in enumerate(zip(stages, vectors)):
    ax = fig.add_subplot(1, 3, i + 1, projection="3d")
    plot_bloch_vector(list(vector), title=title.split(":")[1].strip(), ax=ax)

plt.tight_layout()
plt.show()
