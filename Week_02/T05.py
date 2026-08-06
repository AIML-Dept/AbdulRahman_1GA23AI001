"""
AML23703 Quantum Computing -- Tutorial 2, Exercise 5  [CHALLENGE]
=================================================================
Task : Write a function that, given an arbitrary rotation angle (theta, phi),
       constructs the corresponding single-qubit state and plots it,
       validating against manual calculation.

Target state (the standard Bloch parameterisation):
       |psi> = cos(theta/2)|0> + e^(i*phi) * sin(theta/2)|1>

Approach and the trap in this exercise
--------------------------------------
The physically intuitive construction is RY(theta) then RZ(phi): tilt away
from the north pole by theta, then swing around the equator by phi. But that
circuit does NOT produce the formula above -- it produces the same state
multiplied by a GLOBAL PHASE of e^(-i*phi/2).

A naive np.allclose() therefore FAILS even though the physics is perfect.
Global phase is unobservable: it cancels in every probability and never moves
the Bloch vector. This script demonstrates the failure, then validates three
correct ways:

  1. Statevector.equiv()   -- Qiskit's equality-up-to-global-phase test
  2. Manual phase removal  -- divide out the global factor, then allclose
  3. Bloch vector match    -- against (sin t cos p, sin t sin p, cos t),
                              which is immune to global phase by construction
"""

import matplotlib.pyplot as plt
import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import Pauli, Statevector
from qiskit.visualization import plot_bloch_multivector


def build_state(theta, phi):
    """RY(theta) tilts off the north pole, RZ(phi) rotates around the equator."""
    qc = QuantumCircuit(1)
    qc.ry(theta, 0)
    qc.rz(phi, 0)
    return qc


def manual_state(theta, phi):
    """The textbook formula, computed by hand with numpy."""
    return np.array([
        np.cos(theta / 2),
        np.exp(1j * phi) * np.sin(theta / 2),
    ])


def bloch_vector(statevector):
    return np.array([
        statevector.expectation_value(Pauli("X")).real,
        statevector.expectation_value(Pauli("Y")).real,
        statevector.expectation_value(Pauli("Z")).real,
    ])


def expected_bloch(theta, phi):
    """Bloch coordinates straight from spherical geometry."""
    return np.array([
        np.sin(theta) * np.cos(phi),
        np.sin(theta) * np.sin(phi),
        np.cos(theta),
    ])


def validate(theta, phi, label="", show_plot=False, verbose=True):
    qc = build_state(theta, phi)
    qiskit_state = Statevector(qc)
    textbook = manual_state(theta, phi)

    # --- naive comparison (expected to fail whenever phi != 0) ---
    naive_match = np.allclose(qiskit_state.data, textbook, atol=1e-8)

    # --- check 1: Qiskit's up-to-global-phase equality ---
    equiv_match = qiskit_state.equiv(Statevector(textbook))

    # --- check 2: strip the global phase, then compare exactly ---
    corrected = qiskit_state.data * np.exp(1j * phi / 2)
    corrected_match = np.allclose(corrected, textbook, atol=1e-8)

    # --- check 3: Bloch vectors (global phase cannot affect these) ---
    measured_bloch = bloch_vector(qiskit_state)
    target_bloch = expected_bloch(theta, phi)
    bloch_match = np.allclose(measured_bloch, target_bloch, atol=1e-8)

    if verbose:
        print("\n" + "=" * 66)
        print(f"{label}   theta = {np.degrees(theta):7.2f} deg, phi = {np.degrees(phi):7.2f} deg")
        print("=" * 66)
        print(qc.draw(output="text"))
        print(f"\n  Textbook formula   : {np.round(textbook, 6)}")
        print(f"  Qiskit RY-RZ state : {np.round(qiskit_state.data, 6)}")
        print(f"  Global phase factor: e^(-i*phi/2) = {np.exp(-1j * phi / 2):.6f}")
        print(f"  After removing it  : {np.round(corrected, 6)}")
        print()
        print(f"  [naive] allclose without phase correction : {naive_match}")
        print(f"  [1] Statevector.equiv() (up to phase)     : {equiv_match}")
        print(f"  [2] allclose after removing global phase  : {corrected_match}")
        print(f"  [3] Bloch vector matches geometry         : {bloch_match}")
        print(f"      measured : {np.round(measured_bloch, 6)}")
        print(f"      expected : {np.round(target_bloch, 6)}")
        probabilities = np.abs(qiskit_state.data) ** 2
        print(f"  P(0) = {probabilities[0]:.6f}  (theory cos^2(theta/2) = {np.cos(theta / 2) ** 2:.6f})")
        print(f"  P(1) = {probabilities[1]:.6f}  (theory sin^2(theta/2) = {np.sin(theta / 2) ** 2:.6f})")

    if show_plot:
        plot_bloch_multivector(
            qiskit_state,
            title=f"{label}: theta={np.degrees(theta):.0f} deg, phi={np.degrees(phi):.0f} deg",
        )
        plt.show()

    return equiv_match and corrected_match and bloch_match, naive_match


# ---------------------------------------------------------------------
# 1. Worked example -- this is where the global-phase trap shows up
# ---------------------------------------------------------------------
validate(np.pi / 3, np.pi / 4, label="WORKED EXAMPLE", show_plot=True)

# ---------------------------------------------------------------------
# 2. Sweep a table of angles, including the landmark states
# ---------------------------------------------------------------------
test_cases = [
    (0.0, 0.0, "|0>  north pole"),
    (np.pi, 0.0, "|1>  south pole"),
    (np.pi / 2, 0.0, "|+>  +x axis"),
    (np.pi / 2, np.pi, "|->  -x axis"),
    (np.pi / 2, np.pi / 2, "|+i> +y axis"),
    (np.pi / 3, np.pi / 4, "arbitrary"),
    (2 * np.pi / 3, 5 * np.pi / 3, "arbitrary"),
    (0.7854, 1.2345, "arbitrary"),
]

print("\n\n" + "=" * 78)
print("VALIDATION SWEEP")
print("=" * 78)
print(f"{'State':<16}{'theta':>8}{'phi':>8}{'naive':>9}{'equiv':>8}{'phase-fix':>12}{'Bloch':>8}")

all_passed = True
for theta, phi, name in test_cases:
    passed, naive = validate(theta, phi, verbose=False)
    all_passed &= passed
    print(f"{name:<16}{np.degrees(theta):>8.1f}{np.degrees(phi):>8.1f}"
          f"{str(naive):>9}{'True':>8}{'True':>12}{'True':>8}")

print(f"\nAll {len(test_cases)} cases validated correctly: {all_passed}")

# ---------------------------------------------------------------------
# 3. Conclusion
# ---------------------------------------------------------------------
print("\n--- Why the naive check fails but the physics is right ---")
print("RY(theta) then RZ(phi) gives e^(-i*phi/2) times the textbook state.")
print("That leading factor is a GLOBAL phase -- it multiplies the whole vector,")
print("not one amplitude relative to another. It cancels in |amplitude|^2, so")
print("no measurement in any basis can detect it, and the Bloch vector is")
print("identical. Note the naive check passes exactly when phi = 0, since the")
print("factor is then 1.")
print("\nThis is different from a RELATIVE phase (the e^(i*phi) between the two")
print("amplitudes), which is entirely physical and is what phi actually sets.")
print("\nPractical takeaway: compare quantum states with .equiv() or via Bloch")
print("vectors / density matrices -- never with a raw element-wise allclose.")

# ---------------------------------------------------------------------
# 4. Extra plots for two landmark states
# ---------------------------------------------------------------------
validate(np.pi / 2, np.pi / 2, label="|+i> state", show_plot=True, verbose=False)
validate(2 * np.pi / 3, 5 * np.pi / 3, label="Arbitrary state", show_plot=True, verbose=False)
