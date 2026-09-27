# Tutorial 9 — Quantum Entanglement and Bell State Analysis

## Q1. Why can neither qubit of a Bell pair be described by an independent state vector?

Because the pair's state does not split into "a state for q0" times "a state
for q1". If each qubit had its own state vector, `a0|0> + a1|1>` and
`b0|0> + b1|1>`, the pair would be their product, and a product always passes
one simple test:

```
(a0|0> + a1|1>)(b0|0> + b1|1>)  =  a0b0|00> + a0b1|01> + a1b0|10> + a1b1|11>
amp(00)*amp(11) - amp(01)*amp(10)  =  a0b0*a1b1 - a0b1*a1b0  =  0     (always)
```

For `|Phi+> = (|00> + |11>)/sqrt(2)` the same combination is `1/2 - 0 = 1/2`.
`T01.py` computes it and prints `+0.5000`, which makes the concurrence
`C = 2 x 0.5 = 1`, the largest possible value. In plain terms: to produce `|00>`
the factors need `a0` and `b0`, to produce `|11>` they need `a1` and `b1`, and
then `a0b1` puts weight on `|01>`, which a Bell pair never has. No choice of
four numbers works, so there is no state vector for either qubit on its own.

What each qubit does have is a **reduced state** — what is left once the
partner is ignored. `T02.py` computed it for all four Bell states:

| description of q0 alone | P(0) | P(1) | coherence | purity | entropy |
|:------------------------|:----:|:----:|:---------:|:------:|:-------:|
| any of the four Bell states | 0.50 | 0.50 | 0.00 | 0.50 | 1 bit |
| the single-qubit state `\|+>` | 0.50 | 0.50 | 0.50 | 1.00 | 0 |

Every genuine state vector has purity 1. The reduced state has purity 0.5: it
is the 50/50 **mixture** `I/2`, not a superposition. It is also not `|+>`, even
though both give 50/50 in the Z basis — `|+>` gives `+` on every shot in the X
basis, while one half of a Bell pair gives `+` or `-` at random (in `T03.py`
the X-basis counts of Phi+ were `525` and `499`, with each qubit's own result a
fair coin).

So where did the information go? Into the relation between the qubits. In
`T01.py` each qubit alone behaved like a fair coin (`P(0) = 0.503`), yet the two
agreed on **1024 of 1024** shots, and `T03.py` found them perfectly correlated in
the X basis as well (`E = +1` in both bases). "q0 = q1, in whichever basis you
ask" is a fact about the pair, not about either qubit. The entropy of 1 bit
measures this exactly: the pair as a whole is known completely (a pure state,
nothing uncertain), while each part on its own is maximally uncertain.
Classically that never happens — knowing everything about a whole always means
knowing everything about its parts.

This is also why measuring one qubit "collapses" the other (Week 5, `T03.py`):
only the joint state exists, so updating it updates both qubits at once. No
message travels with that update, because the measured result is itself random
and the partner's own statistics stay 50/50 until the results are compared.

## Q2. In what way does entanglement differ fundamentally from classical statistical correlation?

A classical correlation is shared information that existed all along: two
sealed envelopes holding cards of the same colour. Opening one tells you about
the other only because each card had its colour from the start. `T03.py` built
exactly this — a "classical source" where a fair coin decides `00` or `11` —
and measured it next to `|Phi+>`:

| source | Z basis (00 01 10 11) | E_ZZ | X basis (00 01 10 11) | E_XX | abs(E_ZZ) + abs(E_XX) |
|:-------|:---------------------:|:----:|:---------------------:|:----:|:---------------------:|
| Phi+ | 515 / 0 / 0 / 509 | +1.000 | 525 / 0 / 0 / 499 | +1.000 | 2.00 |
| classical `00` or `11` | 512 / 0 / 0 / 512 | +1.000 | 261 / 254 / 275 / 234 | -0.033 | 1.03 |

In the computational basis the two cannot be told apart. The difference
appears as soon as a second basis is used, and three things follow from it.

- **Entanglement is correlation in every basis, not a stored value.** A pair
  without entanglement obeys `|E_ZZ| + |E_XX| <= 1`: each qubit's Bloch vector
  has length at most 1, so it cannot point along Z and along X at the same
  time. The classical source sits on that limit (1.03 is 1 plus shot noise);
  all four Bell states reach 2. Their correlation is a relation that holds
  whichever question is asked, not an answer written down in advance.
- **It beats any list of pre-agreed answers.** One could try to save the
  envelope picture by giving each qubit a hidden answer for every possible
  basis. The CHSH test in `T04.py` rules that out: any such local scheme gives
  `S <= 2`, and the Phi+ pairs gave `S = 2.803` (theory `2*sqrt(2) = 2.828`).
  That is a violation of a classical limit, not merely a strong correlation.
- **It cannot be copied, and trying destroys it.** Classical correlation can
  be photocopied and handed to anyone. In `T04.py` Eve copied Bob's bit with a
  CNOT — the most any copier can do, since an unknown state cannot be cloned —
  and the pair turned classical: 229 errors in 993 key bits (23.1%, theory
  25%) and `S` fell to 1.428. Entanglement cannot be shared out freely either:
  in `T05.py` no pair inside the GHZ state holds any (`C = 0`), and each pair
  inside the W state gets only `C = 0.667`, never the `C = 1` of a Bell pair.
  A maximally entangled pair has no correlation left over for a third party,
  which is exactly why Eve cannot learn the key without being noticed.

One point has to be stated precisely, because it is where entanglement is
most often overstated: it does not let anyone send a message. Each qubit's own
results stay 50/50 whatever is done to its partner (`T01.py`: `P(0) = 0.503`
for both qubits), so the correlation only appears when the two lists of
results are brought together over an ordinary channel. Entanglement is a
resource that works together with classical communication, not instead of it
— which is the starting point for teleportation and superdense coding.
