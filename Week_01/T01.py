"""
AML23703 Quantum Computing -- Tutorial 1, Exercise 1  [EASY]
============================================================
Task : Install Qiskit and verify the installation by printing the Qiskit
       version and the available backends.

Approach
--------
Printing a version string only proves that the *import* worked. It does not
prove that the simulator can actually execute a circuit. So this script ends
with a DETERMINISTIC self-test: an X gate on |0> must produce '1' on every
single shot. If even one shot returns '0', the install is broken.
"""

import platform

import qiskit
import qiskit_aer
from qiskit import QuantumCircuit
from qiskit_aer import Aer, AerSimulator


def rule(title):
    """Small helper so the terminal output is easy to read in a screenshot."""
    print("\n" + "-" * 62)
    print(title)
    print("-" * 62)


# ---------------------------------------------------------------------
# 1. Environment report
# ---------------------------------------------------------------------
rule("1. ENVIRONMENT REPORT")

environment = {
    "Python version": platform.python_version(),
    "Operating system": f"{platform.system()} ({platform.machine()})",
    "Qiskit SDK": qiskit.__version__,
    "Qiskit Aer": qiskit_aer.__version__,
}
for label, value in environment.items():
    print(f"  {label:<18}: {value}")

# ---------------------------------------------------------------------
# 2. Backends this machine can reach
# ---------------------------------------------------------------------
rule("2. AVAILABLE LOCAL BACKENDS (Aer)")

for backend in Aer.backends():
    print(f"  - {backend.name}")

rule("3. SIMULATION METHODS SUPPORTED BY AerSimulator")

print("  " + ", ".join(AerSimulator().available_methods()))
print("\n  Note: these are all LOCAL simulators. Real IBM Quantum hardware")
print("  requires the qiskit-ibm-runtime package plus an API token")
print("  (that is handled in Exercise 5).")

# ---------------------------------------------------------------------
# 4. Deterministic self-test  --  X|0> = |1>
# ---------------------------------------------------------------------
rule("4. INSTALLATION SELF-TEST: X|0> must measure as '1' on EVERY shot")

qc = QuantumCircuit(1, 1)
qc.x(0)             # bit-flip: |0> -> |1>
qc.measure(0, 0)

print(qc.draw(output="text"))

SHOTS = 512
counts = AerSimulator().run(qc, shots=SHOTS).result().get_counts()

print(f"\n  Counts over {SHOTS} shots : {counts}")

passed = counts.get("1", 0) == SHOTS
print(f"  Verdict               : {'PASS - Qiskit is installed and executing correctly' if passed else 'FAIL - check the installation'}")
