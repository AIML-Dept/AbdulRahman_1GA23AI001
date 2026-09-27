# Tutorial 8 — Deutsch–Jozsa Algorithm: Exponential Speedup

## Q1. How does the promise (constant OR balanced, no other option) make a single-query guarantee possible?

Everything comes down to one formula. The oracle writes a phase `(-1)^f(x)` on
every input `x` (+1 where `f(x) = 0`, -1 where `f(x) = 1`), and the final
Hadamard gates put the **average** of those phases onto the all-zeros outcome:

```
amplitude of |00..0>  =  (1 / 2^n) * sum over all x of (-1)^f(x)
P('00..0')            =  (that average)^2
```

So the algorithm is really asking a single question: what is the average phase?
The promise leaves only two possible answers.

- **Constant:** every phase is the same, so the average is +1 or -1 and
  `P('00..0') = 1`. `T01.py` measured `000` on all 1024 shots, for both
  `f(x) = 0` and `f(x) = 1`.
- **Balanced:** half the phases are +1 and half are -1, so they cancel and the
  average is exactly 0, giving `P('00..0') = 0`. `T02.py` measured `111` on
  every shot, and `T05.py` never saw `000` for any of 100 randomly chosen
  balanced functions.

Probability 1 and probability 0 are the two extremes, so one measurement tells
them apart with no doubt: all zeros means constant, anything else means
balanced. That is what the promise buys — it guarantees the average is always
at one of the two extremes, and never somewhere in between. The two cases end
in states that are completely distinguishable (orthogonal), and that is the
condition for getting a certain answer from a single shot.

A classical computer cannot do this, because each query shows it only one value
of `f`. After `2^(n-1)` equal answers a balanced function is still possible —
the unseen half could all be the other value — so only the next equal answer
proves "constant". That is `2^(n-1) + 1` queries in the worst case. `T04.py`
ran that exact classical procedure and confirmed 513 queries at `n = 10`,
against 1 for Deutsch–Jozsa. The quantum computer never learns any single
`f(x)`; it only learns the one global number the promise made decisive.

One honest caveat, as in Week 7: the exponential gap is against a classical
method that must be **100% certain**. A classical method allowed to guess can
test `k` random inputs, and a balanced function fools it only if all `k` answers
agree, with probability `2 x (1/2)^k`. With 20 queries that is less than 1 in
500,000. So the promise problem shows a real exponential separation, but only
against deterministic classical algorithms.

## Q2. What would happen if a function were neither strictly constant nor balanced?

The circuit still runs and still outputs a bit string — but the guarantee is
gone. Using the same formula, if `f(x) = 1` on `k` of the `2^n` inputs:

```
average phase  =  (2^n - 2k) / 2^n
P('00..0')     =  ((2^n - 2k) / 2^n)^2
```

This is 1 only when `k = 0` or `k = 2^n` (constant), and 0 only when
`k = 2^(n-1)` (balanced). For every other `k` it is somewhere in between.
The extra section at the end of `T05.py` tested every `k` for `n = 3`:

| k (inputs with f = 1) | really is | P('000') theory | P('000') measured |
|:---------------------:|:---------:|:---------------:|:-----------------:|
| 0 | constant | 1.0000 | 1.0000 |
| 1 | neither  | 0.5625 | 0.5762 |
| 2 | neither  | 0.2500 | 0.2539 |
| 3 | neither  | 0.0625 | 0.0596 |
| 4 | balanced | 0.0000 | 0.0000 |
| 5 | neither  | 0.0625 | 0.0596 |
| 6 | neither  | 0.2500 | 0.2539 |
| 7 | neither  | 0.5625 | 0.5762 |
| 8 | constant | 1.0000 | 1.0000 |

Three things follow from this.

- **The answer becomes random.** With `k = 1` (the function is 1 on only one
  input), a single run says "constant" about 56% of the time and "balanced"
  about 44% of the time. Running it twice on the same function can give two
  different verdicts.
- **Neither verdict is right, and nothing warns you.** The algorithm has only
  two possible outputs and no way to say "the promise was broken". A `000`
  from a `k = 1` function looks exactly like a `000` from a truly constant one.
  It fails silently, like the damaged oracle in Week 6 that returned a
  confident wrong answer.
- **What it measures instead is how lopsided `f` is.** `P('00..0')` is close to
  1 when `f` is nearly constant and close to 0 when it is nearly balanced. You
  could estimate it by repeating the run many times, but every repeat is
  another query, so the one-query advantage is lost.

Repeating does give one useful check: a genuine constant function never
produces a non-zero string and a genuine balanced one never produces `00..0`,
so seeing **both** kinds of result proves the promise was broken. But it can
take a very long time to see. If `f` is constant except at one input, the chance
of a non-zero result is only about `4 / 2^n` per run, so noticing the odd input
takes around `2^n / 4` runs — exponential again, just like the classical
search. This is the real lesson of the question: without the promise, the
problem is hard for the quantum computer too. The exponential speedup belongs
to the promise problem, not to the general task of analysing a function.
