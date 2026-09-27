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
