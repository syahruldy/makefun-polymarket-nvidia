# Polymarket NVIDIA CEO forecaster

Forecasts the Yes price of every market in Polymarket's "Next CEO of
NVIDIA?" event, minute by minute, 4 hours ahead, as five quantiles
(5/25/50/75/95%) per minute.

## Model

- **Median = last price.** No drift: both momentum and mean-reversion
  drift terms made the practice score worse.
- **Spread from a robust per-market volatility:** the mean absolute
  1-minute move over the last 1h and 4h, blended 50/50, scaled by 1.2533
  (the normal mean-absolute-deviation conversion). Plain standard
  deviation is dominated by rare huge jumps (88% of minutes are flat)
  and scores far worse.
- **Spread grows as h^0.45**, slower than a random walk, because jumps
  partly revert.
- **Outer quantiles widened x1.3** for jump risk.
- Sigma floored at 0.0003, capped at 0.012 per window.

## Results (local scorer, practice cases p00-p05)

The local scorer reproduces the house baseline exactly (0.363589), so
the practice answers and scoring are verified. This entry scores
**0.276848** on the practice, beating the baseline on all six cases.

## Run

`python3 main.py` reads `$MAKEFUN_INPUT_DIR` (else `/input`) `*.in`
cases and writes `$MAKEFUN_OUTPUT_DIR` (else `/output`) `*.out`
forecasts. Deterministic, stdlib only, no network.
