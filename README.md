# AML23703 — Quantum Computing: Tutorials 1–3

Qiskit solutions for the hands-on exercises in Tutorials 1, 2 and 3.

## Repository layout

```
Week_01/   Tutorial 1 — Introduction to Quantum Computing and Qiskit Setup
  T01.py   [Easy]       Verify the Qiskit install: versions, backends, self-test
  T02.py   [Medium]     1-qubit Hadamard, 1024 shots, histogram
  T03.py   [Hard]       3-qubit equal superposition vs the theoretical 1/8
  T04.py   [Real-world] Quantum RNG for OTP generation vs Python's PRNG
  T05.py   [Challenge]  Ideal simulator vs real IBM hardware / noise model

Week_02/   Tutorial 2 — Qubits, State Vectors and Superposition Visualisation
  T01.py   [Easy]       |0> -> X -> statevector, Dirac notation, Bloch sphere
  T02.py   [Medium]     H then S, tracked stage by stage on the Bloch sphere
  T03.py   [Hard]       2-qubit equal superposition, normalisation verified 3 ways
  T04.py   [Real-world] Dephasing channel: random phase noise and decoherence
  T05.py   [Challenge]  State builder from (theta, phi), with the global-phase trap

Week_03/   Tutorial 3 — Single-Qubit Quantum Gates
  T01.py   [Easy]       Pauli X, Y, Z: matrices, action on |0> and |1>
  T02.py   [Medium]     Building |-> with H and Z, verified in the X basis
  T03.py   [Hard]       5 random gates: analytic vs statevector vs sampled
  T04.py   [Real-world] A quantum coin-flip betting game and the house edge
  T05.py   [Challenge]  Proving HZH = X five different ways

REFLECTIONS.md          Written answers to the reflection questions
```

## Setup

```bash
python -m venv qiskit_env
source qiskit_env/bin/activate        # Windows: qiskit_env\Scripts\activate
pip install qiskit qiskit-aer matplotlib numpy scipy pylatexenc
```

`pylatexenc` is only needed for `qc.draw(output="mpl")`. Every script here prints
text circuit diagrams, so it is optional.

Optional, for Week_01/T05.py on real hardware:

```bash
pip install qiskit-ibm-runtime
python -c "from qiskit_ibm_runtime import QiskitRuntimeService; \
    QiskitRuntimeService.save_account(channel='ibm_quantum_platform', \
    token='YOUR_API_TOKEN', overwrite=True)"
```

Get a free token at https://quantum.cloud.ibm.com/. **T05 runs without an account** —
it falls back to a fake backend, then to a hand-built Aer noise model.

## Running

Each script is standalone:

```bash
cd Week_01
python T01.py
```

Scripts that plot will open a matplotlib window; close it to let the script finish.

## Tested with

| Package     | Version |
|-------------|---------|
| Python      | 3.12    |
| qiskit      | 2.5.1   |
| qiskit-aer  | 0.17.2  |
| numpy       | 2.x     |
| scipy       | 1.x     |

The Qiskit 1.0 release removed `execute()`; these scripts use the current
`AerSimulator().run(...)` pattern throughout, so they will not run on Qiskit 0.x.

## Notes

- Console output is ASCII-only (`|0>` rather than `|0⟩`) so it renders correctly in
  Windows terminals, which otherwise raise `UnicodeEncodeError` on the ket character.
- Random seeds are fixed where reproducibility helps (`Week_01/T04.py`,
  `Week_02/T04.py`, `Week_03/T03.py`). Change the `SEED` constant for a fresh run.
