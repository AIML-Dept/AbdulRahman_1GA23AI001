# Tutorial 7 — Deutsch's Algorithm: Demonstrating Quantum Advantage

## Q1. Why is Deutsch's algorithm historically significant despite its limited practical use?

Because it was the first time anyone could point at a specific task, write down
a specific circuit, and say: this machine finishes in one step and no classical
machine can. Before 1985 the case for quantum computing was an intuition.
Feynman had argued that simulating quantum systems on classical hardware looked
hopelessly expensive, and Deutsch had defined a universal quantum Turing
machine, but neither produced a problem where the advantage could be counted.
Deutsch's algorithm produced one. It turned a plausible idea into a theorem.

What makes it convincing is that the advantage is **exact**, not statistical.
`T01.py` and `T02.py` do not measure 0 or 1 *usually* — the amplitude on the
wrong outcome is zero, so all 1024 shots agree and the wrong answer is not
merely unlikely but impossible. A deterministic classical algorithm genuinely
needs both queries: `f(0)` on its own eliminates nothing, because every value
of `f(0)` is consistent with one constant and one balanced function. So the
comparison is 1 against 2, with no hedging on either side.

The larger legacy is the shape of the circuit rather than the result.

- **Superpose, query once, interfere, measure.** Every algorithm in this course
  since has that skeleton. Deutsch-Jozsa is the same circuit widened to `n`
  input qubits. Bernstein-Vazirani reads a hidden string out of the phases.
  Simon's algorithm in Week 6 is the same idea with a two-to-one oracle, and
  Shor's factoring algorithm came directly out of Simon's.
- **The oracle model.** Counting queries to a black box is what makes a
  separation provable at all. Without it you are comparing implementations,
  not algorithms.
- **Interference as the resource.** The point is not that superposition
  evaluates `f` at both inputs — that part is free and useless on its own,
  since measuring would collapse to one random branch. The point is that the
  final Hadamard makes the unwanted branch cancel. `T02.py` shows the two
  branches arriving with opposite signs and the amplitude on `|0>` going to
  exactly zero.

The honest limits are worth stating just as plainly, because overselling this
result is the standard way of getting quantum computing wrong.

- **The problem is invented.** Nobody needs to know whether a one-bit function
  is constant. `T04.py` stretches it into a classification analogy and the
  analogy breaks as soon as the labelling rule is allowed to be anything other
  than exactly constant or exactly balanced.
- **The promise does the work.** Drop the guarantee that `f` is one of those
  two kinds and the single query decides nothing.
- **Against randomised classical algorithms the gap largely closes.** This is
  the caveat that gets left out most often. Deutsch-Jozsa beats *deterministic*
  classical algorithms exponentially, but a classical algorithm allowed to
  guess can sample a handful of random inputs and be right with overwhelming
  probability, because a balanced function disagrees with itself on half its
  inputs. So the exponential separation is against a restricted opponent.
  Simon's algorithm, in Week 6, was the first to beat randomised classical
  algorithms too — which is exactly why it, and not this, is what Shor built on.
- **On real hardware the certainty is the first thing to go.** `T05.py`
  miscalibrates the Hadamard gates by a few degrees and the guarantee turns
  into a 99% success rate, recoverable only by repeating the run and voting —
  which spends the query saving the algorithm was supposed to earn.

So the fair summary is that Deutsch's algorithm is a proof of concept that
stayed important because the concept was right, not because the problem was.
It is the first entry in a line of reasoning that ends at Shor.

## Q2. How does phase kickback allow information about f(x) to appear in the control qubit's phase?

Start from what the oracle is allowed to do. Quantum gates have to be
reversible, so `f` cannot simply be applied to the input — it is applied as

```
U_f |x> |y>  =  |x> |y XOR f(x)>
```

which leaves the input register alone and XORs the answer into an ancilla.
Written that way, the oracle looks like it only ever touches the ancilla.

The trick is the state the ancilla is put in. `T01.py` and `T02.py` set it to
`|1>` and apply a Hadamard, giving

```
|->  =  ( |0> - |1> ) / sqrt(2)
```

Now watch what XOR-ing `f(x)` into that state does. If `f(x) = 0`, nothing
happens. If `f(x) = 1`, the two components swap:

```
( |1> - |0> ) / sqrt(2)  =  - ( |0> - |1> ) / sqrt(2)  =  - |->
```

The state comes back **identical apart from a minus sign**. In other words
`|->` is an eigenvector of the flip operation with eigenvalue `-1`, so the
oracle cannot change it — all it can do is multiply it by `(-1)^f(x)`. And a
scalar factor does not belong to any particular qubit, so it can be written on
whichever register is convenient. Collecting both cases:

```
U_f |x> |->  =  (-1)^f(x) |x> |->
```

The ancilla is exactly where it started. The sign has landed on the input
register. That is phase kickback: the oracle was aimed at the ancilla, the
ancilla refused to change, and the eigenvalue bounced onto the control qubit.

The reason this is useful rather than a curiosity is that the input register is
in superposition when it happens. Starting from `|+>`, one query gives

```
( |0> + |1> ) / sqrt(2)   ->   ( (-1)^f(0) |0> + (-1)^f(1) |1> ) / sqrt(2)
```

so **both** values of `f` are now encoded, in a single call, as the relative
sign between the two branches. `T02.py` prints exactly this: the amplitude on
`|0>` stays `+0.5` and the amplitude on `|1>` turns to `-0.5`.

Two things still have to be true for that to become an answer.

- **A relative phase is not directly measurable.** Measuring immediately would
  give 0 or 1 with probability one half either way, identically for all four
  functions. The final Hadamard is what converts the phase pattern into an
  amplitude pattern: same signs make `|+>`, which `H` sends to `|0>`; opposite
  signs make `|->`, which `H` sends to `|1>`. The phase has to be turned into
  a population before it can be read.
- **The ancilla must learn nothing.** This is the part that is easy to miss.
  Because `|->` comes back unchanged, the two qubits stay unentangled and the
  input register stays in a pure, coherent superposition. If the ancilla were
  altered — if it recorded which branch it was in — the registers would be
  entangled, the input register would be left mixed, and the interference would
  wash out. `T05.py` measures precisely this: with a miscalibrated Hadamard the
  ancilla is no longer exactly `|->`, no longer an exact eigenstate, and the
  coherence driving the interference is scaled by `cos(eps)`, costing an extra
  25% error on top of the rotation error the input register already suffers.

It is also worth being clear about what the phase does *not* buy. One query
produces one bit. The sign pattern distinguishes "same" from "different" and
nothing else — `T03.py` confirms that `f(x) = x` and `f(x) = NOT x` return an
identical result. Kickback gives cheap access to a **global** property of `f`,
never to `f` itself, and only when a later interference step can be arranged to
separate the possible phase patterns into distinguishable outcomes. Deutsch's
case is the easiest possible version, since two patterns map onto two
orthogonal states. Grover needs the marking step repeated about `sqrt(N)` times
before the phases accumulate into something measurable, and phase estimation
needs an inverse Fourier transform to read a phase written across many qubits.
The kickback is the same primitive in all three; the work is in what gets built
on top of it.
