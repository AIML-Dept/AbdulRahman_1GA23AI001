"""
AML23703 Quantum Computing -- Tutorial 3, Exercise 4  [REAL-WORLD]
==================================================================
Task : Use single-qubit gates to model a simple quantum coin-flip game and
       calculate win probabilities.

Real-world framing: a casino with a TUNABLE coin.
-------------------------------------------------
A fair classical coin gives no edge to anyone. But a qubit rotated by RY(theta)
is a coin whose bias is a continuous dial:

        RY(theta)|0>  =  cos(theta/2)|0> + sin(theta/2)|1>
        P(heads) = cos^2(theta/2)

theta = 0 is a two-headed coin, theta = pi is two-tailed, theta = pi/2 is
exactly fair. The house sets theta a hair past pi/2 -- imperceptible to a
player watching a handful of flips, but mathematically decisive over
thousands of rounds.

This models the real economics of a casino: the house edge, not luck, and
why the law of large numbers is the house's most reliable employee.
"""

import matplotlib.pyplot as plt
import numpy as np
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator

SHOTS = 8192
STAKE = 1.0            # player bets 1 unit per round on HEADS, even-money payout

simulator = AerSimulator()


def coin_circuit(theta):
    """A single quantum coin flip. Outcome '0' = heads, '1' = tails."""
    qc = QuantumCircuit(1, 1)
    qc.ry(theta, 0)
    qc.measure(0, 0)
    return qc


def flip_many(theta, shots=SHOTS, memory=False):
    result = simulator.run(coin_circuit(theta), shots=shots, memory=memory).result()
    return (result.get_counts(), result.get_memory()) if memory else result.get_counts()


def theory_heads(theta):
    return np.cos(theta / 2) ** 2


print("--- The quantum coin ---")
print(coin_circuit(np.pi / 2).draw(output="text"))
print("\nRY(theta) tilts the qubit off the north pole. The tilt angle sets the")
print("bias; measurement collapses it to a definite heads or tails.\n")

# ---------------------------------------------------------------------
# 1. Sweep the bias dial
# ---------------------------------------------------------------------
angles = [0.0, np.pi / 6, np.pi / 4, np.pi / 3, np.pi / 2,
          2 * np.pi / 3, 3 * np.pi / 4, np.pi]
names = ["two-headed", "", "", "", "FAIR", "", "", "two-tailed"]

print(f"--- Win probability vs bias angle ({SHOTS} flips each) ---")
print(f"{'theta':>8}{'deg':>7}{'P(heads) th':>14}{'P(heads) sim':>15}"
      f"{'player EV':>12}{'house edge':>13}   ")

for theta, note in zip(angles, names):
    counts = flip_many(theta)
    simulated = counts.get("0", 0) / SHOTS
    theoretical = theory_heads(theta)
    expected_value = STAKE * (2 * theoretical - 1)      # +1 on win, -1 on loss
    house_edge = -expected_value

    print(f"{theta:>8.4f}{np.degrees(theta):>7.0f}{theoretical:>14.4f}{simulated:>15.4f}"
          f"{expected_value:>+12.4f}{house_edge:>+12.2%}   {note}")

print("\nAt theta = 90 deg the game is exactly fair: the player's expected value")
print("is zero and neither side profits in the long run.")

# ---------------------------------------------------------------------
# 2. The house chooses its edge
# ---------------------------------------------------------------------
TARGET_EDGE = 0.027                       # 2.7%, the same as European roulette
p_needed = (1 - TARGET_EDGE) / 2
theta_house = 2 * np.arccos(np.sqrt(p_needed))

print("\n" + "=" * 68)
print("THE HOUSE SETS ITS DIAL")
print("=" * 68)
print(f"  Target house edge      : {TARGET_EDGE:.1%}")
print(f"  Required P(heads)      : {p_needed:.4f}")
print(f"  Required theta         : {theta_house:.6f} rad = {np.degrees(theta_house):.3f} deg")
print(f"  Tilt away from fair    : {np.degrees(theta_house - np.pi / 2):.3f} deg")
print("\n  That is under two degrees off fair. No player could detect it by eye,")
print("  and over 100 flips the difference is well inside normal noise.")

# ---------------------------------------------------------------------
# 3. A short session -- luck dominates
# ---------------------------------------------------------------------
SESSION_ROUNDS = 20
_, outcomes = flip_many(theta_house, shots=SESSION_ROUNDS, memory=True)

balance = 0.0
history = []
print(f"\n--- A short session of {SESSION_ROUNDS} rounds (stake {STAKE:.0f} per round) ---")
print(f"{'Round':>6}{'Outcome':>10}{'Result':>9}{'Balance':>10}")
for round_number, bit in enumerate(outcomes, start=1):
    won = bit == "0"
    balance += STAKE if won else -STAKE
    history.append(balance)
    print(f"{round_number:>6}{'HEADS' if won else 'TAILS':>10}"
          f"{'+1' if won else '-1':>9}{balance:>+10.0f}")

print(f"\n  Session result: {balance:+.0f} units.")
print("  Over 20 rounds the outcome is dominated by luck -- a player can")
print("  easily walk away ahead. That is exactly what keeps them playing.")

# ---------------------------------------------------------------------
# 4. The long run -- the edge dominates
# ---------------------------------------------------------------------
LONG_RUN = 500_000
counts = flip_many(theta_house, shots=LONG_RUN)
wins = counts.get("0", 0)
losses = counts.get("1", 0)
net = STAKE * (wins - losses)

print(f"\n--- The long run: {LONG_RUN:,} rounds ---")
print(f"  Player wins            : {wins:,}  ({wins / LONG_RUN:.4f})")
print(f"  Player losses          : {losses:,}  ({losses / LONG_RUN:.4f})")
print(f"  Player net             : {net:+,.0f} units")
print(f"  Loss per unit staked   : {-net / (LONG_RUN * STAKE):.4%}")
sampling_error = 2 * 0.5 / np.sqrt(LONG_RUN)
print(f"  Predicted house edge   : {TARGET_EDGE:.4%}")
print(f"  1-sigma sampling noise : +/-{sampling_error:.4%}")
print("\n  The measured loss converges on the designed edge. The house never")
print("  needs to win any particular round -- it only needs enough rounds.")

# ---------------------------------------------------------------------
# 5. Plots
# ---------------------------------------------------------------------
fine_angles = np.linspace(0, np.pi, 200)
sample_angles = np.linspace(0, np.pi, 13)
sampled = [flip_many(t, shots=2048).get("0", 0) / 2048 for t in sample_angles]

fig, axes = plt.subplots(1, 2, figsize=(13, 4.5))

axes[0].plot(np.degrees(fine_angles), theory_heads(fine_angles),
             "-", color="steelblue", label="Theory cos^2(theta/2)")
axes[0].plot(np.degrees(sample_angles), sampled, "o",
             color="indianred", label="Simulated (2048 flips)")
axes[0].axhline(0.5, color="grey", linestyle=":", label="Fair game")
axes[0].axvline(np.degrees(theta_house), color="darkgreen", linestyle="--",
                label=f"House setting ({np.degrees(theta_house):.1f} deg)")
axes[0].set_xlabel("Rotation angle theta (degrees)")
axes[0].set_ylabel("P(heads) = player wins")
axes[0].set_title("The bias dial")
axes[0].legend(fontsize=8)
axes[0].grid(alpha=0.3)

axes[1].plot(range(1, SESSION_ROUNDS + 1), history, "o-", color="darkorange")
axes[1].axhline(0, color="black", linewidth=0.8)
axes[1].set_xlabel("Round")
axes[1].set_ylabel("Player balance (units)")
axes[1].set_title(f"A {SESSION_ROUNDS}-round session: luck beats the edge, briefly")
axes[1].grid(alpha=0.3)

plt.tight_layout()
plt.show()
