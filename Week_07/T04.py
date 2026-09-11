"""
Week_07 / T04.py -- Tutorial 7, Real-world
Read Deutsch's problem as a binary classification question -- is this feature
useless or is it a perfect separator? -- run all four decision rules through
the algorithm, and draw a slide explaining how phase kickback carries the
answer.
"""

import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator

SHOTS = 1024
SEED = 7

sim = AerSimulator(seed_simulator=SEED)

# A toy spam filter with a single binary feature: does the email contain a
# link? A decision rule maps that one bit to a label, 0 = ham, 1 = spam.
# There are four such rules, and every one of them is a Deutsch function.
RULES = {
    'always ham': {
        'table': (0, 0),
        'meaning': 'label every email ham, whatever the feature says',
    },
    'always spam': {
        'table': (1, 1),
        'meaning': 'label every email spam, whatever the feature says',
    },
    'link -> spam': {
        'table': (0, 1),
        'meaning': 'a link means spam, no link means ham',
    },
    'link -> ham': {
        'table': (1, 0),
        'meaning': 'a link means ham, no link means spam',
    },
}

LABEL = {0: 'ham ', 1: 'spam'}


def make_oracle(table):
    """Same truth-table-driven builder as T03: flip the ancilla wherever f = 1."""
    f0, f1 = table
    qc = QuantumCircuit(2)
    if f0 == 1:
        qc.x(0)
        qc.cx(0, 1)
        qc.x(0)
    if f1 == 1:
        qc.cx(0, 1)
    if len(qc.data) == 0:
        qc.id(0)
        qc.id(1)
    return qc


def deutsch_verdict(table):
    """
    One query. Returns 'useless' when the rule ignores the feature (constant)
    and 'separator' when the rule is driven entirely by it (balanced).
    """
    qc = QuantumCircuit(2, 1)
    qc.x(1)
    qc.h([0, 1])
    qc.compose(make_oracle(table), inplace=True)
    qc.h(0)
    qc.measure(0, 0)

    bit = max(counts := sim.run(qc, shots=SHOTS).result().get_counts(),
              key=counts.get)
    return ('useless' if bit == '0' else 'separator'), bit


# 1. Run the classifier audit. One oracle query per rule, no training data.
print("Toy spam filter: one binary feature (does the email contain a link?)")
print("and one binary label (ham / spam). Four decision rules are possible.\n")

print(" decision rule | no link -> | link ->  | queries | verdict   | information")
print("-" * 78)

for name, spec in RULES.items():
    f0, f1 = spec['table']
    verdict, bit = deutsch_verdict(spec['table'])
    info = 'none' if verdict == 'useless' else 'complete'
    print(f" {name:13s} |    {LABEL[f0]}    |   {LABEL[f1]}   |    1    | "
          f"{verdict:9s} | {info}")

print("\nThe question answered here is not 'what label does this email get'.")
print("It is 'does this feature carry any signal at all' -- a property of the")
print("whole rule rather than of any single input. That is the kind of question")
print("phase kickback is good at, because the phase is attached to the entire")
print("superposition rather than to one sample.")

# 2. The mapping, stated explicitly.
print("\nHow the two vocabularies line up")
print("-" * 66)
pairs = [
    ('feature value x', 'the input register, held in superposition'),
    ('label f(x)', 'the oracle output, kicked back as a phase'),
    ('rule ignores the feature', 'constant f  ->  measure 0'),
    ('rule tracks the feature', 'balanced f  ->  measure 1'),
    ('labelled samples needed', '2 classically, 1 with Deutsch'),
]
for left, right in pairs:
    print(f"  {left:26s} ->  {right}")

# 3. The honest limits of the analogy, which matter more than the analogy.
print("\nWhere the analogy stops")
print("-" * 66)
print("  - Real features are not one bit, real labels are noisy, and real rules")
print("    are almost never exactly constant or exactly balanced. Deutsch needs")
print("    that promise; drop it and the single query stops being decisive.")
print("  - The 'query' is a call to a reversible circuit that already encodes")
print("    the labelling rule. Nobody hands you your dataset in that form, and")
print("    building the oracle from raw data can cost more than the search saved.")
print("  - Deutsch-Jozsa, the n-bit version, is where this shape actually pays:")
print("    one query against 2^(n-1) + 1 classical ones. Even there the promise")
print("    is the catch -- allow the function to be merely 'mostly constant' and")
print("    a randomised classical algorithm gets close for a handful of samples.")
print("\nSo the honest claim is narrow: kickback lets one query report a GLOBAL")
print("property of a labelling rule. That is a real primitive, and it reappears")
print("inside Grover and Shor. It is not a spam filter.")

# 4. The slide.
fig = plt.figure(figsize=(13, 7.6))
fig.suptitle("Phase kickback as a binary classification decision",
             fontsize=15, fontweight='bold', y=0.97)

grid = fig.add_gridspec(2, 2, height_ratios=[1.25, 1], hspace=0.22, wspace=0.12,
                        left=0.04, right=0.96, top=0.88, bottom=0.05)

BLUE, GREEN, GREY = '#2c6fb5', '#2e8b57', '#5a5a5a'


def box(ax, x, y, w, h, text, colour, fontsize=9.5, bold=False, opaque=False):
    """
    A rounded label box, used for every node in the slide. `opaque` lays a
    white patch underneath first, so circuit wires stop at the gate instead of
    being visible straight through it.
    """
    style = "round,pad=0.012"
    if opaque:
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle=style,
                                    linewidth=0, facecolor='white', zorder=2))
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle=style,
                                linewidth=1.4, edgecolor=colour,
                                facecolor=colour, alpha=0.10,
                                zorder=3 if opaque else 1))
    ax.text(x + w / 2, y + h / 2, text, ha='center', va='center',
            fontsize=fontsize, color=colour, zorder=4,
            fontweight='bold' if bold else 'normal')


def arrow(ax, start, end, colour, style='-|>', lw=1.6, dashed=False, zorder=5):
    ax.add_patch(FancyArrowPatch(start, end, arrowstyle=style,
                                 mutation_scale=13, linewidth=lw,
                                 color=colour, zorder=zorder,
                                 linestyle='--' if dashed else '-'))


# -- panel A: the four rules, sorted into the two classes ---------------------
axA = fig.add_subplot(grid[0, 0])
axA.set_xlim(0, 1)
axA.set_ylim(0, 1)
axA.axis('off')
axA.set_title("The question a classifier asks", fontsize=11.5, fontweight='bold',
              color=GREY, pad=6)

axA.text(0.5, 0.93, "one binary feature  ->  one binary label\nfour rules exist",
         ha='center', va='center', fontsize=9.5, color=GREY)

box(axA, 0.04, 0.46, 0.44, 0.34, "", GREEN)
axA.text(0.26, 0.755, "IGNORES the feature", ha='center', fontsize=10,
         fontweight='bold', color=GREEN)
axA.text(0.26, 0.63, "always ham    (0, 0)\nalways spam  (1, 1)",
         ha='center', va='center', fontsize=9.5, color=GREEN, family='monospace')
axA.text(0.26, 0.51, "constant  ->  no signal", ha='center', fontsize=9, color=GREEN)

box(axA, 0.52, 0.46, 0.44, 0.34, "", BLUE)
axA.text(0.74, 0.755, "TRACKS the feature", ha='center', fontsize=10,
         fontweight='bold', color=BLUE)
axA.text(0.74, 0.63, "link -> spam  (0, 1)\nlink -> ham   (1, 0)",
         ha='center', va='center', fontsize=9.5, color=BLUE, family='monospace')
axA.text(0.74, 0.51, "balanced  ->  full signal", ha='center', fontsize=9, color=BLUE)

axA.text(0.5, 0.34, "Which pile is this rule in?", ha='center', fontsize=10.5,
         fontweight='bold', color='black')
axA.text(0.5, 0.22,
         "classical audit : label both feature values  ->  2 queries\n"
         "one value alone settles nothing, so neither can be skipped",
         ha='center', va='center', fontsize=9, color=GREY)
box(axA, 0.16, 0.03, 0.68, 0.13, "Deutsch's algorithm : 1 query", '#b5432c',
    fontsize=11, bold=True)

# -- panel B: the circuit, with the kickback marked --------------------------
axB = fig.add_subplot(grid[0, 1])
axB.set_xlim(0, 1)
axB.set_ylim(0, 1)
axB.axis('off')
axB.set_title("Where the answer is carried", fontsize=11.5, fontweight='bold',
              color=GREY, pad=6)

y_in, y_anc = 0.66, 0.34
axB.plot([0.12, 0.92], [y_in, y_in], color='black', lw=1.1, zorder=1)
axB.plot([0.12, 0.92], [y_anc, y_anc], color='black', lw=1.1, zorder=1)

axB.text(0.08, y_in, "|0>", ha='center', va='center', fontsize=10.5,
         family='monospace')
axB.text(0.08, y_anc, "|1>", ha='center', va='center', fontsize=10.5,
         family='monospace')
axB.text(0.03, y_in + 0.09, "feature\nregister", ha='center', va='center',
         fontsize=8.5, color=BLUE)
axB.text(0.03, y_anc - 0.10, "ancilla", ha='center', va='center',
         fontsize=8.5, color=GREEN)

for x, row in [(0.22, y_in), (0.22, y_anc), (0.78, y_in)]:
    box(axB, x - 0.045, row - 0.055, 0.09, 0.11, "H", GREY,
        fontsize=11, bold=True, opaque=True)

box(axB, 0.42, y_anc - 0.07, 0.16, 0.40, "", '#b5432c', opaque=True)
axB.text(0.50, 0.755, "U_f", ha='center', fontsize=12,
         fontweight='bold', color='#b5432c')
axB.text(0.50, 0.225, "the labelling rule, sealed in a box", ha='center',
         va='center', fontsize=8.5, color='#b5432c')

box(axB, 0.87, y_in - 0.055, 0.09, 0.11, "M", GREY,
    fontsize=11, bold=True, opaque=True)

axB.text(0.325, y_in + 0.09, "|+>", ha='center', fontsize=10, color=BLUE,
         family='monospace')
axB.text(0.325, y_anc + 0.075, "|->", ha='center', fontsize=10, color=GREEN,
         family='monospace')
axB.text(0.755, y_anc + 0.075, "|->  unchanged", ha='center', fontsize=9,
         color=GREEN)

arrow(axB, (0.50, y_anc + 0.055), (0.50, y_in - 0.055), '#b5432c', dashed=True)
axB.text(0.638, 0.505, "kickback\n(-1)^f(x)", ha='center', va='center',
         fontsize=9, color='#b5432c', fontweight='bold')

axB.text(0.5, 0.145,
         "The ancilla is never read and learns nothing. The oracle only\n"
         "stamps a sign onto each branch of the feature register.",
         ha='center', va='center', fontsize=9, color=GREY)
axB.text(0.5, 0.035,
         "same sign twice  ->  measure 0  ->  feature is useless\n"
         "opposite signs   ->  measure 1  ->  feature separates perfectly",
         ha='center', va='center', fontsize=9.5, color='black',
         family='monospace')

# -- panel C: the vocabulary map --------------------------------------------
axC = fig.add_subplot(grid[1, :])
axC.set_xlim(0, 1)
axC.set_ylim(0, 1)
axC.axis('off')
axC.set_title("Reading one vocabulary in the other", fontsize=11.5,
              fontweight='bold', color=GREY, pad=6)

rows = [
    ("classification", "Deutsch"),
    ("feature value x", "input register in superposition"),
    ("label f(x)", "oracle output, kicked back as a phase"),
    ("rule ignores the feature", "constant f  ->  measured bit 0"),
    ("rule is driven by the feature", "balanced f  ->  measured bit 1"),
    ("labelled samples needed", "2 classically, 1 with one query"),
]

top, step = 0.90, 0.155
for i, (left, right) in enumerate(rows):
    y = top - i * step
    header = i == 0
    axC.text(0.30, y, left, ha='right', va='center',
             fontsize=10.5 if header else 10,
             fontweight='bold' if header else 'normal',
             color=BLUE if header else 'black')
    axC.text(0.40, y, right, ha='left', va='center',
             fontsize=10.5 if header else 10,
             fontweight='bold' if header else 'normal',
             color='#b5432c' if header else 'black')
    if not header:
        arrow(axC, (0.325, y), (0.385, y), GREY, lw=1.1)
    else:
        axC.plot([0.03, 0.97], [y - 0.06, y - 0.06], color=GREY, lw=0.9)

axC.text(0.985, 0.06,
         "Caveat: the promise that f is exactly constant or exactly balanced\n"
         "is what makes one query enough. Real labelling rules are neither.",
         ha='right', va='center', fontsize=8.5, color=GREY, style='italic')

plt.show()
