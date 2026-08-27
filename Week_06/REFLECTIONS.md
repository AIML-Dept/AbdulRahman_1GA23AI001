# Tutorial 6 — Simon's Algorithm: Concept and Implementation

## Q1. What made solving the classical linear system straightforward once the quantum measurements were obtained?

Because of what each measurement hands you. One run of the circuit does not
return the secret `s`. It returns a string `y` that is guaranteed to satisfy

```
y . s  =  0   (mod 2)
```

and that is a plain linear equation in the unknown bits of `s`. So the quantum
part quietly changes the whole shape of the problem: instead of hunting through
`2^n` candidate strings, you are now just solving `n-1` equations in `n`
unknowns. Search became algebra.

The algebra is then easy for three separate reasons.

- **Only 0 and 1 exist.** All the arithmetic happens over GF(2), where adding is
  the same as XOR and the only non-zero number is 1. There is no division step,
  no fractions, no decimals and no rounding error, so the answer is exact.
- **Gaussian elimination collapses into XOR.** The `add_equation` function used
  in `T02.py`, `T03.py` and `T05.py` is about ten lines long, and every step in
  it is "if this row owns that column, XOR it out".
- **The system is tiny.** For a 4-bit secret it is 3 equations in 4 unknowns.
  Even for a 20-bit secret it is 19 equations in 20 unknowns, which a laptop
  finishes instantly.

The last piece is why the answer comes out unique. With `n-1` independent
equations exactly two strings survive: the all-zero string and `s` itself.
Throw away the all-zero one and what is left has to be the secret. `T03.py`
prints both solutions to make that visible.

Two honest caveats. First, "straightforward" is not the same as "free": the
equations have to be **independent**, and since each `y` arrives at random, some
runs repeat information you already have. `T04.py` measures the real cost — a
20-bit secret needed about 21 runs to collect 19 useful equations, not 19.
Second, this all assumes the measurements are correct. On a perfect simulator
they are. On noisy hardware a single flipped bit produces an equation that is
simply false, and because GF(2) elimination has no notion of "nearly right",
one bad row quietly corrupts the entire answer. Real implementations therefore
repeat runs and take majority votes before trusting an equation.

## Q2. How would the algorithm behave if the oracle were implemented incorrectly?

The uncomfortable answer is that it usually keeps running and still prints
something. Simon's algorithm has no way to check the promise it was handed. It
was tested by deliberately damaging the `s = 1011` oracle, and three clearly
different behaviours showed up.

- **A stray extra CNOT.** The function stopped being 2-to-1 and became 4-to-1 —
  four inputs sharing each output instead of two. The promise was broken, so
  the rank stopped climbing at `n-2` and never reached `n-1`. Here the code
  cannot produce an answer at all, and `simon()` in `T05.py` returns `None`
  rather than guessing. This is the *good* kind of failure: loud and visible.
- **One CNOT left out.** This is the dangerous one. The function was still a
  perfectly valid 2-to-1 function, just with a different period, so the
  algorithm confidently returned `1010` instead of `1011`. Nothing looked
  wrong. The rank was right, the equations were consistent, the output was
  clean — and the answer was incorrect. The algorithm was not actually wrong;
  it correctly solved the oracle it was *given*, which was not the oracle that
  was *intended*.
- **An oracle with no period at all** (a one-to-one function). Then `y` comes
  out uniformly random over every string, the rank climbs all the way to `n`,
  and the honest conclusion is "there is no hidden string". This is the same
  path `T05.py` uses to handle the all-zero secret, so a badly broken oracle
  and a genuinely empty secret can look identical from the outside.

Two smaller mistakes are worth naming because they are easy to make in Qiskit.
Leaving out the final layer of Hadamard gates removes the interference step
entirely, so `y` becomes uniformly random and every run is wasted. And reading
the measurement string in the wrong direction returns `s` reversed — Qiskit
prints counts as `c3c2c1c0`, which is why every script here flips the key with
`key[::-1]`.

The lesson from all of this is that the algorithm cannot police its own input,
so the check has to be added by hand. It costs two ordinary oracle queries:
compute `f(000...0)` and `f(s)` and confirm they collide, exactly as `T03.py`
and `T05.py` do at the end. Two queries is nothing next to the `n` runs already
spent, and it converts the silent wrong-answer case into a visible one.
