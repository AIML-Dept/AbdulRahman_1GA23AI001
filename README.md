# AML23703 — Quantum Computing: Tutorials 1–9

Qiskit solutions for the hands-on exercises in Tutorials 1 to 9.

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

Week_04/   Tutorial 4 — Multi-Qubit Gates and Circuit Composition
  T01.py   [Easy]       CNOT with control in |1>, full truth table generated
  T02.py   [Medium]     Bell state, 1024 shots, only 00 and 11 verified
  T03.py   [Hard]       3-qubit GHZ state and its perfect three-way correlation
  T04.py   [Real-world] Reversible full adder from Toffoli and CNOT gates
  T05.py   [Challenge]  A non-Bell entangled state rebuilt by state tomography

Week_05/   Tutorial 5 — Quantum Measurement and Probability Analysis
  T01.py   [Easy]       100 / 1000 / 10000 shots: P(0) converging to 0.5
  T02.py   [Medium]     |+> and |-> measured in the X basis after an H
  T03.py   [Hard]       Partial measurement of a Bell pair collapses the partner
  T04.py   [Real-world] Recovering a hidden Ry angle from measurement counts
  T05.py   [Challenge]  Chi-square test: quantum RNG vs biased classical PRNG
  REFLECTIONS.md        Written answers to the reflection questions

Week_06/   Tutorial 6 — Simon's Algorithm: Concept and Implementation
  T01.py   [Easy]       Oracle for s = '110', truth table checked for the period
  T02.py   [Medium]     Full Simon circuit, n-1 independent equations collected
  T03.py   [Hard]       4-bit secret, GF(2) system solved in code to recover s
  T04.py   [Real-world] Query counts vs classical search to n = 20, speedup plotted
  T05.py   [Challenge]  Any secret recovered automatically, all-zero case handled
  REFLECTIONS.md        Written answers to the reflection questions

Week_07/   Tutorial 7 — Deutsch's Algorithm: Demonstrating Quantum Advantage
  T01.py   [Easy]       Constant oracle f(x) = 0, one query returns '0'
  T02.py   [Medium]     Balanced oracle f(x) = x, kickback traced statevector by statevector
  T03.py   [Hard]       make_oracle(kind) builds all four functions from their truth tables
  T04.py   [Real-world] Kickback read as a binary classification decision, with a slide
  T05.py   [Challenge]  Miscalibrated Hadamards: error curves, closed forms, bar chart
  REFLECTIONS.md        Written answers to the reflection questions

Week_08/   Tutorial 8 — Deutsch–Jozsa Algorithm: Exponential Speedup
  T01.py   [Easy]       Constant oracle on 3 qubits, '000' on every shot
  T02.py   [Medium]     Balanced parity oracle on 3 qubits, never '000' (always '111')
  T03.py   [Hard]       n = 2 to 5 as a parameter, oracles for both cases built automatically
  T04.py   [Real-world] Classical 2^(n-1)+1 vs 1 quantum query for n = 2 to 10, plotted
  T05.py   [Challenge]  Random oracles from ALL balanced functions, 100/100 classified
  REFLECTIONS.md        Written answers to the reflection questions

Week_09/   Tutorial 9 — Quantum Entanglement and Bell State Analysis
  T01.py   [Easy]       Phi+ from H + CNOT, only '00' and '11' in 1024 shots
  T02.py   [Medium]     All four Bell states tabulated, orthonormal, entropy 1 bit each
  T03.py   [Hard]       Bell pairs in the Hadamard basis vs a classical '00'/'11' source
  T04.py   [Real-world] Entanglement-based key exchange, Eve caught by QBER and CHSH
  T05.py   [Challenge]  GHZ vs W: one qubit measured or traced out, entanglement left
  REFLECTIONS.md        Written answers to the reflection questions
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
  `Week_02/T04.py`, `Week_03/T03.py`, `Week_04/T02.py`, `Week_04/T03.py`,
  `Week_04/T05.py`, and every script in `Week_06`, `Week_07`, `Week_08` and
  `Week_09`). Change the `SEED` constant for a fresh run.
- Qiskit labels a basis state as `|q2 q1 q0>`, so qubit 0 is the *rightmost*
  character. The Week_04 scripts print labels in that order and use
  `outcome[::-1][i]` wherever an individual qubit has to be read out. The
  Week_06, Week_08 and Week_09 scripts flip every measurement key with
  `key[::-1]` for the same reason, so that position `i` of a printed string
  always means qubit `i`.
- `Week_06/T04.py` opens a two-panel matplotlib window (query counts and
  speedup). Close it to let the script finish.
- `Week_07/T04.py` opens a three-panel explanatory slide and `Week_07/T05.py`
  a two-panel error chart. Close each window to let the script finish.
- `Week_07/T05.py` is the only script that needs `scipy`, for the binomial
  tail behind its majority-vote table.
- `Week_08/T04.py` opens a two-panel chart (normal scale and log scale). Close
  it to let the script finish.
- `Week_08/T05.py` builds its oracles from truth tables with multi-controlled X
  gates (`qc.mcx`), which `AerSimulator` runs directly. It takes a few seconds,
  because it checks all 100 random oracles input by input before running them.
- Every `Week_09` script opens one matplotlib window (`T04.py` and `T05.py`
  draw two panels in it). Close it to let the script finish.
- `Week_09` runs circuits that are compared side by side as ONE job,
  `sim.run([qc1, qc2, ...])`. Aer gives each circuit in a job its own seed
  derived from `SEED`; separate `run()` calls would all restart from `SEED`
  and give identical splits for states with the same probabilities.
- `Week_09/T04.py` lets the eavesdropper copy Bob's bit onto her own qubit
  with a CNOT instead of measuring mid-circuit. The statistics are the same
  (deferred measurement), and with every measurement at the end Aer samples
  the shots independently; with a mid-circuit measurement it seeds shot `i`
  as `SEED + i`, so runs with nearby seeds repeat each other.
- `Week_09/T05.py` uses `partial_trace`, `entropy` and `concurrence` from
  `qiskit.quantum_info`, which ship with Qiskit.
