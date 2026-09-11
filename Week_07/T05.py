"""
Week_07 / T05.py -- Tutorial 7, Challenge
Miscalibrate the Hadamard gates by a small angle and measure how fast the
answer stops being trustworthy: exact error probabilities, sampled error
rates, the two closed-form curves they follow, and a bar chart.
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import binom
from qiskit import QuantumCircuit
from qiskit.circuit.library import HGate
from qiskit.quantum_info import Operator, Statevector
from qiskit_aer import AerSimulator

SHOTS = 4096
SEED = 7
DEGREES = [0, 2, 5, 10, 15, 20, 30, 45]

sim = AerSimulator(seed_simulator=SEED)

FUNCTIONS = {
    'constant_0': (0, 0),
    'constant_1': (1, 1),
    'balanced_id': (0, 1),
    'balanced_not': (1, 0),
}


def imperfect_h(qc, q, eps):
    """
    A Hadamard whose rotation angle is off by eps radians.

    H factorises as Ry(pi/2) . Z, so a miscalibrated H is Ry(pi/2 + eps) . Z.
    This is the realistic error: on hardware a Hadamard is a microwave pulse,
    and an amplitude or duration slightly off target rotates the qubit slightly
    too far. At eps = 0 the gate is exactly H, which the first check confirms.
    """
    qc.z(q)
    qc.ry(np.pi / 2 + eps, q)


def make_oracle(table):
    """Truth-table-driven oracle builder, same as T03. Assumed perfect here."""
    f0, f1 = table
    qc = QuantumCircuit(2)
    if f0 == 1:
        qc.x(0)
        qc.cx(0, 1)
        qc.x(0)
    if f1 == 1:
        qc.cx(0, 1)
    return qc


def deutsch(table, eps, model, measured=True):
    """
    Deutsch's circuit with miscalibrated Hadamards.

    model 'control' : only the two H gates on the input register are off,
                      the ancilla is prepared perfectly
    model 'all'     : all three H gates are off, so |-> is imperfect too
    """
    qc = QuantumCircuit(2, 1) if measured else QuantumCircuit(2)
    qc.x(1)
    imperfect_h(qc, 0, eps)
    imperfect_h(qc, 1, eps if model == 'all' else 0.0)
    qc.compose(make_oracle(table), inplace=True)
    imperfect_h(qc, 0, eps)
    if measured:
        qc.measure(0, 0)
    return qc


def exact_error(table, eps, model):
    """Probability of the wrong verdict, straight from the statevector."""
    probs = Statevector(deutsch(table, eps, model, measured=False)).probabilities([0])
    correct = 0 if table[0] == table[1] else 1
    return 1.0 - probs[correct]


def sampled_error(table, eps, model):
    """Same quantity estimated by counting shots, so shot noise is included."""
    counts = sim.run(deutsch(table, eps, model), shots=SHOTS).result().get_counts()
    correct = '0' if table[0] == table[1] else '1'
    return 1.0 - counts.get(correct, 0) / SHOTS


def majority_shots(p, target=1e-3, cap=999):
    """Odd number of repeats needed for a majority vote to be wrong below target."""
    if p >= 0.5:
        return None                       # voting cannot rescue a coin worse than a coin
    for k in range(1, cap + 1, 2):
        if binom.sf(k // 2, k, p) < target:
            return k
    return None


# 1. The gate is only a fair model of a miscalibration if it is exactly H when
#    nothing is wrong. Check that before drawing conclusions from it.
probe = QuantumCircuit(1)
imperfect_h(probe, 0, 0.0)
print("imperfect_h(eps=0) equals H :",
      np.allclose(Operator(probe).data, HGate().to_matrix()))

print("\nWhat the miscalibration does to |0>")
print("-" * 57)
print("   eps   | state after one imperfect H       | P(0)   P(1)")
print("-" * 57)
for deg in [0, 5, 15, 45]:
    step = QuantumCircuit(1)
    imperfect_h(step, 0, np.deg2rad(deg))
    sv = Statevector(step)
    p0, p1 = sv.probabilities()
    print(f" {deg:3d} deg | {sv.data[0].real:+.3f}|0> {sv.data[1].real:+.3f}|1>"
          f"              | {p0:.3f}  {p1:.3f}")
print("\nAt 0 degrees the split is exactly 50/50. The gate drifts smoothly from")
print("there -- no cliff edge, which is exactly why the failure is easy to miss.")

# 2. The sweep. Every function, every angle, exact and sampled.
print("\n" + "=" * 78)
print(f"Error probability by miscalibration angle ({SHOTS} shots per cell)")
print("=" * 78)

for model, caption in [('control', 'only the two input-register H gates are off'),
                       ('all', 'all three H gates are off')]:
    print(f"\nmodel '{model}' -- {caption}\n")
    print("   eps   | constant_0 | constant_1 | balanced_id | balanced_not | worst")
    print("-" * 72)
    for deg in DEGREES:
        eps = np.deg2rad(deg)
        cells = []
        for kind in FUNCTIONS:
            cells.append((exact_error(FUNCTIONS[kind], eps, model),
                          sampled_error(FUNCTIONS[kind], eps, model)))
        worst = max(e for e, _ in cells)
        body = ' | '.join(f"{s:.4f}" for _, s in cells)
        print(f" {deg:3d} deg |   {cells[0][1]:.4f}   |   {cells[1][1]:.4f}   |"
              f"   {cells[2][1]:.4f}    |    {cells[3][1]:.4f}    | {worst:.4f}")

# 3. Both patterns above have closed forms. Confirm the simulation matches them.
print("\n" + "=" * 78)
print("Closed forms, checked against the exact simulation")
print("=" * 78)
print("\n  constant f, either model : P(error) = 0                      exactly")
print("  balanced f, control only : P(error) = sin^2(eps)")
print("  balanced f, all three    : P(error) = 1 - (cos^2 eps + cos^3 eps) / 2")

print("\n   eps   | constant | balanced control |  sin^2  | balanced all |  formula")
print("-" * 74)
ok = True
for deg in DEGREES:
    eps = np.deg2rad(deg)
    e_const = exact_error(FUNCTIONS['constant_1'], eps, 'all')
    e_ctrl = exact_error(FUNCTIONS['balanced_id'], eps, 'control')
    e_all = exact_error(FUNCTIONS['balanced_id'], eps, 'all')
    f_ctrl = np.sin(eps) ** 2
    f_all = 1 - (np.cos(eps) ** 2 + np.cos(eps) ** 3) / 2
    ok = ok and abs(e_ctrl - f_ctrl) < 1e-9 and abs(e_all - f_all) < 1e-9 \
        and e_const < 1e-12
    print(f" {deg:3d} deg |  {e_const:.4f}  |      {e_ctrl:.4f}      | {f_ctrl:.4f}"
          f"  |    {e_all:.4f}    |  {f_all:.4f}")

print(f"\nSimulation agrees with both formulas to 1e-9 : {ok}")

print("\nWhy constant functions are immune. The input register meets the same")
print("miscalibrated H twice, and a constant oracle does nothing to it in")
print("between -- at most a global phase. The second rotation therefore undoes")
print("the first exactly, whatever eps is. That is a spin echo, and it is the")
print("reason error rates here are 0.0000 rather than merely small.")

print("\nWhy balanced functions are not. The oracle applies a Z between the two")
print("rotations, which flips the sign of the correction, so the errors add")
print("instead of cancelling and the answer drifts as sin^2(eps).")

print("\nWhat the ancilla adds. With all three gates off the ancilla is no longer")
print("exactly |->, so it is no longer an eigenstate of X. The oracle then")
print("entangles the two qubits instead of cleanly kicking a phase back, the")
print("input register is left in a mixed state, and the coherence that drives")
print("the interference is scaled by cos(eps). Expanding both formulas for")
print("small eps gives eps^2 against 1.25 eps^2 -- the imperfect ancilla costs")
print("an extra 25% on top of the rotation error it already shares.")

# 4. The practical question: when is the answer still worth trusting?
print("\n" + "=" * 78)
print("Reliability: single shot vs majority vote over repeats")
print("=" * 78)
print("\n   eps   | worst-case single-shot error | repeats for a vote below 0.001")
print("-" * 72)
for deg in DEGREES:
    eps = np.deg2rad(deg)
    p = max(exact_error(t, eps, 'all') for t in FUNCTIONS.values())
    k = majority_shots(p)
    note = f"{k:3d}" if k else "never -- see below"
    print(f" {deg:3d} deg |            {p:.4f}            |  {note}")

print("\nThe headline claim for Deutsch's algorithm is that one query gives a")
print("certain answer. That word 'certain' is the first casualty of imperfect")
print("gates: at 5 degrees off the algorithm is still right 99% of the time,")
print("but it is no longer a proof, and the only way back to high confidence is")
print("to run it repeatedly and vote -- which spends exactly the query advantage")
print("the algorithm was supposed to win.")
print("\nAt 45 degrees the balanced error passes 0.5, and majority voting stops")
print("helping altogether: the circuit is now more often wrong than right, so")
print("more repeats drive the vote confidently to the wrong answer. A biased")
print("measurement is worse than a coin flip, because a coin flip at least")
print("announces its own uselessness.")
print("\nOne more thing worth noticing: the failure is one-sided. A miscalibrated")
print("run never turns a constant function into a balanced verdict, only the")
print("reverse. So a reading of '1' stays trustworthy while a reading of '0'")
print("quietly absorbs every failed balanced run -- the asymmetry matters more")
print("than the average error rate when deciding what to do with the result.")

# 5. The chart.
angles = np.array(DEGREES)
const_bar = [sampled_error(FUNCTIONS['constant_1'], np.deg2rad(d), 'all') for d in DEGREES]
bal_bar = [sampled_error(FUNCTIONS['balanced_id'], np.deg2rad(d), 'all') for d in DEGREES]

fine = np.linspace(0, np.deg2rad(45), 200)
curve_ctrl = np.sin(fine) ** 2
curve_all = 1 - (np.cos(fine) ** 2 + np.cos(fine) ** 3) / 2

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4.8))

width = 0.38
pos = np.arange(len(DEGREES))
ax1.bar(pos - width / 2, const_bar, width, label='constant f', color='#2e8b57')
ax1.bar(pos + width / 2, bal_bar, width, label='balanced f', color='#b5432c')
ax1.set_xticks(pos)
ax1.set_xticklabels([f"{d}" for d in DEGREES])
ax1.set_xlabel('Hadamard miscalibration eps (degrees)')
ax1.set_ylabel(f'wrong answers out of {SHOTS} shots')
ax1.set_title('Measured error rate, all three H gates off')
ax1.axhline(0.5, color='grey', linestyle='--', linewidth=1)
ax1.text(5.3, 0.515, 'coin flip', fontsize=8, color='grey')
ax1.legend(loc='upper left')
ax1.grid(axis='y', alpha=0.3)
ax1.text(0.5, 0.40, 'the green bars are not missing --\n'
                    'constant f is wrong 0 times at every angle',
         fontsize=8.5, color='#2e8b57')

for x, v in zip(pos + width / 2, bal_bar):
    ax1.text(x, v + 0.012, f"{v:.3f}", ha='center', fontsize=7.5, color='#b5432c')

ax2.plot(np.rad2deg(fine), curve_all, '-', color='#b5432c',
         label='balanced, all three H off')
ax2.plot(np.rad2deg(fine), curve_ctrl, '-', color='#2c6fb5',
         label='balanced, input-register H only')
ax2.plot(angles, [exact_error(FUNCTIONS['balanced_id'], np.deg2rad(d), 'all')
                  for d in DEGREES], 'o', color='#b5432c', markersize=5)
ax2.plot(angles, [exact_error(FUNCTIONS['balanced_id'], np.deg2rad(d), 'control')
                  for d in DEGREES], 's', color='#2c6fb5', markersize=5)
ax2.axhline(0, color='#2e8b57', linewidth=2, label='constant, either model')
ax2.axhline(0.5, color='grey', linestyle='--', linewidth=1)
ax2.set_xlabel('Hadamard miscalibration eps (degrees)')
ax2.set_ylabel('P(wrong verdict)')
ax2.set_title('Exact error against the closed forms')
ax2.legend(fontsize=8, loc='upper left')
ax2.grid(alpha=0.3)

plt.tight_layout()
plt.show()
