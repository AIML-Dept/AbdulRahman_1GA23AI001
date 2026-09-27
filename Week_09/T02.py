"""
Week_09 / T02.py -- Tutorial 9, Medium
Build all four Bell states with one circuit, tabulate their measurement
distributions side by side (1024 shots each), and verify their properties:
the four states are orthonormal, and each one is maximally entangled.
"""

import matplotlib.pyplot as plt
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector, entropy, partial_trace
from qiskit_aer import AerSimulator

SHOTS = 1024
SEED = 9
OUTCOMES = ['00', '01', '10', '11']                      # written q0 q1
BELL_INPUTS = {'Phi+': '00', 'Phi-': '10', 'Psi+': '01', 'Psi-': '11'}

sim = AerSimulator(seed_simulator=SEED)


def bell_state(name):
    """
    One circuit makes all four Bell states; only the input bits (a b) change.

      q0 : |a> --H--*--      a = 1 : H gives (|0> - |1>)/sqrt(2), a MINUS sign
                    |
      q1 : |b> -----X--      b = 1 : the CNOT makes the qubits DISagree

      (a b) = 00 -> Phi+ = (|00> + |11>)/sqrt(2)
              10 -> Phi- = (|00> - |11>)/sqrt(2)
              01 -> Psi+ = (|01> + |10>)/sqrt(2)
              11 -> Psi- = (|01> - |10>)/sqrt(2)
    """
    a, b = BELL_INPUTS[name]
    qc = QuantumCircuit(2, name=name)
    if a == '1':
        qc.x(0)
    if b == '1':
        qc.x(1)
    qc.h(0)
    qc.cx(0, 1)
    return qc


def dirac(state):
    """The non-zero amplitudes as text, e.g. '+0.707|00> +0.707|11>'."""
    terms = []
    for label in OUTCOMES:
        amp = state.data[int(label[::-1], 2)]            # Qiskit's index reads q1 q0
        if abs(amp) > 1e-9:
            terms.append(f"{amp.real:+.3f}|{label}>")
    return ' '.join(terms)


def measure_all(preps):
    """
    Measure every prepared pair SHOTS times, all in ONE simulator job. Aer gives
    each circuit in a job its own seed (derived from SEED), so the runs are
    independent but reproducible; separate run() calls would all restart from
    SEED and give identical splits. Keys flipped so position i = qubit i.
    """
    jobs = []
    for prep in preps:
        qc = QuantumCircuit(2, 2)
        qc.compose(prep, inplace=True)
        qc.measure([0, 1], [0, 1])
        jobs.append(qc)
    result = sim.run(jobs, shots=SHOTS).result()
    return [{key[::-1]: c for key, c in result.get_counts(i).items()}
            for i in range(len(jobs))]


circuits = {name: bell_state(name) for name in BELL_INPUTS}
states = {name: Statevector(qc) for name, qc in circuits.items()}
counts = dict(zip(BELL_INPUTS, measure_all(circuits.values())))

print("Psi- needs both X gates, so its circuit shows every part (a = b = 1)")
print(circuits['Psi-'])

# 1. The comparison table: exact amplitudes next to the measured counts.
print("state | a b | amplitudes (q0 q1)    |   00   01   10   11 | qubits")
print("-" * 71)
for name in BELL_INPUTS:
    c = [counts[name].get(label, 0) for label in OUTCOMES]
    relation = 'agree' if c[1] + c[2] == 0 else 'disagree' if c[0] + c[3] == 0 else 'mixed'
    print(f" {name} | {' '.join(BELL_INPUTS[name])} | {dirac(states[name])} |"
          f" {c[0]:4d} {c[1]:4d} {c[2]:4d} {c[3]:4d} | {relation}")

# 2. Property 1: orthonormal. |<A|B>|^2 is 1 for a state with itself and 0 for
#    two different Bell states, so one measurement could tell them apart.
names = list(BELL_INPUTS)
print("\n|<A|B>|^2  " + "  ".join(f"{n:>4s}" for n in names))
for a in names:
    row = [abs(states[a].inner(states[b])) ** 2 for b in names]
    print(f"   {a}   " + "  ".join(f"{v:4.2f}" for v in row))

# 3. Property 2: maximally entangled. Trace out q1 and look at what is left
#    of q0 alone. The entropy of that leftover state is the entanglement entropy.
print("\nstate | q0 alone: P(0)  P(1)  coherence | purity | entanglement entropy")
print("-" * 71)
for name in BELL_INPUTS:
    rho = partial_trace(states[name], [1]).data          # forget qubit 1
    purity = (rho @ rho).trace().real
    s = entropy(partial_trace(states[name], [1]), base=2)
    print(f" {name} |           {rho[0, 0].real:.2f}  {rho[1, 1].real:.2f}     "
          f"{abs(rho[0, 1]):.2f}   |  {purity:.2f}  |      {s:.3f} bit")

print("\nAll four states are orthonormal, so they form a basis for two qubits (the")
print("Bell basis). Each leaves q0 as a 50/50 mixture with NO coherence, purity 0.5")
print("and entropy 1 bit, the most two qubits can share. That is not |+>: |+> is")
print("also 50/50 in Z, but its coherence is 0.50 and its entropy is 0.")
print("\nWhat the Z-basis table cannot show: it only reveals WHETHER the qubits agree.")
print("Phi+ and Phi- give the same kind of counts, and so do Psi+ and Psi-. The")
print("+/- sign is a relative phase, invisible here -- T03 measures in the X basis.")

# 4. The four distributions side by side.
fig, axes = plt.subplots(1, 4, figsize=(13, 3.6), sharey=True)
for ax, name in zip(axes, BELL_INPUTS):
    values = [counts[name].get(label, 0) for label in OUTCOMES]
    color = 'tab:blue' if name.startswith('Phi') else 'tab:orange'
    bars = ax.bar(OUTCOMES, values, color=color)
    ax.bar_label(bars, padding=6, fontsize=8)
    ax.axhline(SHOTS / 2, color='gray', linestyle='--', linewidth=1)
    ax.set_title(f"{name}\n{dirac(states[name])}", fontsize=10)
    ax.set_xlabel('outcome (q0 q1)')
    ax.grid(axis='y', alpha=0.3)
axes[0].set_ylabel('counts')
axes[0].set_ylim(0, SHOTS * 0.62)
fig.suptitle(f'The four Bell states measured in the Z basis, {SHOTS} shots each')
plt.tight_layout()
plt.show()
