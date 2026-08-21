# Tutorial 5 — Quantum Measurement and Probability Analysis

## Q1. Why does increasing the number of shots improve the estimate?

One measurement gives one bit, not a probability. The probability has to be
rebuilt by running the same circuit many times and counting, so the estimate is
just the observed frequency `n/N`.

That estimate is already unbiased at any N. What more shots reduce is its
spread, `sqrt(p(1-p)/N)`, which falls as `1/sqrt(N)`:

- 100 shots → error around 0.05
- 1000 shots → around 0.016
- 10000 shots → around 0.005

T01.py shows exactly this. Two caveats: the square root means 100x the shots
buys only 10x the precision, and more shots fix sampling noise only — a device
with a readout bias would converge just as smoothly onto the wrong value.

## Q2. What real-world applications rely on true quantum randomness?

- **Cryptographic keys** — TLS session keys, nonces, IVs. A classical PRNG is
  deterministic, so anyone who knows the seed knows every bit.
- **Quantum key distribution (BB84)** — basis choices must be unpredictable, or
  an eavesdropper can anticipate them.
- **Lotteries and certified gaming** — unpredictability has to be provable to a
  regulator.
- **Monte Carlo simulation** — hidden patterns in a PRNG can quietly bias
  results in finance and physics.
- **QRNG hardware and beacons** — e.g. ID Quantique chips, NIST Randomness
  Beacon.

The point: a PRNG only looks random and is fixed by its seed, while quantum
outcomes are unpredictable in principle. T05.py detects bias, but bias is only
one failure mode — an unbiased yet predictable PRNG would pass that test, which
is why strong certification uses Bell tests instead.
