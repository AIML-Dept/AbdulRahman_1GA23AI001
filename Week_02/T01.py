"""
AML23703 Quantum Computing -- Tutorial 2, Exercise 1  [EASY]
============================================================
Task : Create a qubit in state |0>, apply an X gate, and print/visualise the
       resulting statevector.

Approach
--------
The same physical state is written three different ways in this course, so
this script prints all three side by side for BOTH the before and after
state: the raw amplitude vector, Dirac (bra-ket) notation, and the Bloch
vector. Seeing |0> = [1,0] = north pole simultaneously is what makes the
Bloch sphere click.
"""

import matplotlib.pyplot as plt
import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import Pauli, Statevector
from qiskit.visualization import plot_bloch_multivector


def to_dirac(statevector, n_qubits=1):
    """Format a statevector as readable bra-ket notation, e.g. '0.7071|0> + 0.7071|1>'."""
    terms = []
    for index, amplitude in enumerate(statevector.data):
        if abs(amplitude) < 1e-9:
            continue
        label = format(index, f"0{n_qubits}b")
        if abs(amplitude.imag) < 1e-9:
            coefficient = f"{amplitude.real:+.4f}"
        else:
            coefficient = f"+({amplitude.real:.4f}{amplitude.imag:+.4f}j)"
        terms.append(f"{coefficient}|{label}>")
    return " ".join(terms) if terms else "0"


def bloch_vector(statevector):
    """Bloch coordinates = expectation values of the three Pauli operators."""
    return np.array([
        statevector.expectation_value(Pauli("X")).real,
        statevector.expectation_value(Pauli("Y")).real,
        statevector.expectation_value(Pauli("Z")).real,
    ])


def describe(title, statevector):
    print(f"\n{title}")
    print(f"  Amplitude vector : {np.round(statevector.data, 4)}")
    print(f"  Dirac notation   : {to_dirac(statevector)}")
    for index, amplitude in enumerate(statevector.data):
        print(f"     |{index}> : amplitude {amplitude:+.4f}   probability {abs(amplitude) ** 2:.4f}")
    x, y, z = bloch_vector(statevector)
    print(f"  Bloch vector     : (x={x:+.4f}, y={y:+.4f}, z={z:+.4f})")
    print(f"  Norm check       : sum of |amplitude|^2 = {np.sum(np.abs(statevector.data) ** 2):.6f}")


# ---------------------------------------------------------------------
# 1. Start in |0> -- a fresh QuantumCircuit is always initialised there
# ---------------------------------------------------------------------
qc = QuantumCircuit(1)
state_before = Statevector(qc)

# ---------------------------------------------------------------------
# 2. Apply the X (NOT / bit-flip) gate
# ---------------------------------------------------------------------
qc.x(0)
state_after = Statevector(qc)

print("--- Circuit Diagram ---")
print(qc.draw(output="text"))

describe("BEFORE the X gate  -- the qubit is in |0>", state_before)
describe("AFTER the X gate   -- the qubit is in |1>", state_after)

# ---------------------------------------------------------------------
# 3. Confirm what the gate did
# ---------------------------------------------------------------------
print("\n--- Summary ---")
print("X swaps the two amplitudes: [1, 0] becomes [0, 1].")
print("On the Bloch sphere this is a 180-degree rotation about the x-axis,")
print("so z flips from +1 (north pole, |0>) to -1 (south pole, |1>).")
print(f"Applying X twice returns the original state: {Statevector(QuantumCircuit(1).compose(qc).compose(qc)).equiv(state_before)}")

# ---------------------------------------------------------------------
# 4. Visualise both states on Bloch spheres
# ---------------------------------------------------------------------
plot_bloch_multivector(state_before, title="Before X  --  |0> (north pole)")
plt.show()

plot_bloch_multivector(state_after, title="After X  --  |1> (south pole)")
plt.show()
