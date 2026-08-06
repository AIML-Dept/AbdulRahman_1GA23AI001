"""
AML23703 Quantum Computing -- Tutorial 1, Exercise 5  [CHALLENGE]
=================================================================
Task : Configure IBM Quantum account credentials and submit the same circuit
       to a real quantum backend (or a noise-model simulator), then compare
       the results with the ideal simulator.

Approach
--------
The script tries three backends in order and uses the best one available, so
it runs on any machine -- with or without an IBM Quantum account:

  1. REAL HARDWARE   -- qiskit-ibm-runtime installed AND credentials saved
  2. FAKE BACKEND    -- qiskit-ibm-runtime installed (a noise snapshot of a
                        real device; no account or queue needed)
  3. CUSTOM NOISE    -- always works: depolarising + readout error built by
                        hand in Aer

Test circuit: a 3-qubit GHZ state (|000> + |111>)/sqrt(2). It is the ideal
stress test because ONLY '000' and '111' should ever appear -- so every
other bitstring in the output is unambiguously hardware error.

To use real hardware, run this ONCE beforehand:
    pip install qiskit-ibm-runtime
    python -c "from qiskit_ibm_runtime import QiskitRuntimeService; \
        QiskitRuntimeService.save_account(channel='ibm_quantum_platform', \
        token='YOUR_API_TOKEN', overwrite=True)"
Get the token free from https://quantum.cloud.ibm.com/
"""

import matplotlib.pyplot as plt
import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel, ReadoutError, depolarizing_error

SHOTS = 4096

# ---------------------------------------------------------------------
# 1. The test circuit: a 3-qubit GHZ state
# ---------------------------------------------------------------------
ghz = QuantumCircuit(3, 3)
ghz.h(0)
ghz.cx(0, 1)
ghz.cx(1, 2)
ghz.measure([0, 1, 2], [0, 1, 2])

print("--- Test circuit: 3-qubit GHZ state ---")
print(ghz.draw(output="text"))
print("\nIdeal output: only '000' and '111', each with probability 0.5.")
print("Anything else that appears is caused by hardware noise.\n")


# ---------------------------------------------------------------------
# 2. Pick the best available noisy backend
# ---------------------------------------------------------------------
def build_manual_noise_model():
    """A hand-built noise model, roughly matching a small superconducting device."""
    noise = NoiseModel()
    noise.add_all_qubit_quantum_error(depolarizing_error(0.002, 1), ["h", "x", "rz", "sx", "id"])
    noise.add_all_qubit_quantum_error(depolarizing_error(0.02, 2), ["cx"])
    # 2.5% chance a measured 0 is reported as 1 and vice versa
    noise.add_all_qubit_readout_error(ReadoutError([[0.975, 0.025], [0.025, 0.975]]))
    return noise


def select_noisy_backend():
    """Return (backend, description, is_real_hardware)."""
    # --- Attempt 1: real IBM Quantum hardware -------------------------
    try:
        from qiskit_ibm_runtime import QiskitRuntimeService

        service = QiskitRuntimeService()
        device = service.least_busy(operational=True, simulator=False, min_num_qubits=3)
        return device, f"REAL IBM QUANTUM HARDWARE: {device.name}", True
    except Exception as exc:
        print(f"[1] Real hardware unavailable  -> {type(exc).__name__}: {exc}")

    # --- Attempt 2: a fake backend (real calibration data, run locally) ---
    try:
        from qiskit_ibm_runtime.fake_provider import FakeManilaV2

        fake = FakeManilaV2()
        return AerSimulator.from_backend(fake), f"FAKE BACKEND (noise snapshot of {fake.name})", False
    except Exception as exc:
        print(f"[2] Fake backend unavailable   -> {type(exc).__name__}: {exc}")

    # --- Attempt 3: hand-built noise model (always available) ---------
    print("[3] Falling back to a hand-built Aer noise model.")
    return AerSimulator(noise_model=build_manual_noise_model()), "CUSTOM AER NOISE MODEL", False


noisy_backend, description, is_real = select_noisy_backend()
print(f"\nSelected noisy backend: {description}\n")

# ---------------------------------------------------------------------
# 3. Run on the ideal simulator
# ---------------------------------------------------------------------
ideal_counts = AerSimulator().run(ghz, shots=SHOTS).result().get_counts()

# ---------------------------------------------------------------------
# 4. Run the SAME circuit on the noisy backend
# ---------------------------------------------------------------------
transpiled = transpile(ghz, noisy_backend, optimization_level=1)
print(f"Circuit depth after transpilation : {transpiled.depth()} "
      f"(was {ghz.depth()} before mapping to the device's native gate set)")

if is_real:
    from qiskit_ibm_runtime import SamplerV2

    print("Submitting to the queue -- this can take several minutes...")
    sampler = SamplerV2(mode=noisy_backend)
    result = sampler.run([transpiled], shots=SHOTS).result()
    noisy_counts = result[0].data.c.get_counts()
else:
    noisy_counts = noisy_backend.run(transpiled, shots=SHOTS).result().get_counts()

# ---------------------------------------------------------------------
# 5. Compare the two distributions
# ---------------------------------------------------------------------
all_states = sorted(set(ideal_counts) | set(noisy_counts))

print(f"\n--- Ideal vs noisy over {SHOTS} shots ---")
print(f"{'State':<9}{'Ideal':>9}{'Noisy':>9}{'Ideal P':>11}{'Noisy P':>11}")

for state in all_states:
    i_hits = ideal_counts.get(state, 0)
    n_hits = noisy_counts.get(state, 0)
    print(f"|{state}>{'':<3}{i_hits:>9}{n_hits:>9}{i_hits / SHOTS:>11.4f}{n_hits / SHOTS:>11.4f}")

# Total variation distance: the standard "how far apart are two distributions"
tvd = 0.5 * sum(
    abs(ideal_counts.get(s, 0) / SHOTS - noisy_counts.get(s, 0) / SHOTS) for s in all_states
)

# Every shot outside {000, 111} is a state that physics forbids here
leaked = sum(n for s, n in noisy_counts.items() if s not in ("000", "111"))

print(f"\nTotal variation distance   : {tvd:.4f}   (0 = identical, 1 = no overlap)")
print(f"Shots in forbidden states  : {leaked} / {SHOTS}  ({leaked / SHOTS:.2%})")
print(f"GHZ fidelity (crude)       : {1 - leaked / SHOTS:.4f}")

print("\nInterpretation")
print("--------------")
print("The ideal simulator solves the maths exactly, so it only ever returns")
print("'000' or '111'. The noisy backend leaks probability into states such as")
print("'001' and '110' because each gate is slightly imperfect and the readout")
print("occasionally misreports a qubit. The two-qubit CX gate is the dominant")
print("error source -- it is roughly an order of magnitude noisier than the")
print("single-qubit gates, which is why deep circuits degrade so quickly on")
print("today's NISQ hardware.")

# ---------------------------------------------------------------------
# 6. Side-by-side plot
# ---------------------------------------------------------------------
x = np.arange(len(all_states))
width = 0.38

fig, ax = plt.subplots(figsize=(10, 4.5))
ax.bar(x - width / 2, [ideal_counts.get(s, 0) / SHOTS for s in all_states],
       width, label="Ideal simulator", color="steelblue")
ax.bar(x + width / 2, [noisy_counts.get(s, 0) / SHOTS for s in all_states],
       width, label=description.split(":")[0].strip(), color="indianred")

ax.set_xticks(x)
ax.set_xticklabels([f"|{s}>" for s in all_states])
ax.set_ylabel("Probability")
ax.set_title(f"3-qubit GHZ: ideal vs noisy  (TVD = {tvd:.4f})")
ax.legend()

plt.tight_layout()
plt.show()
