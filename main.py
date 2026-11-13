#!/usr/bin/env python3
"""Polymarket Next-NVIDIA-CEO forecaster (make.fun polymarket-nvidia-ceo-forecast-01).

Model (tuned on the 6 practice cases, local scorer reproducing the house
baseline exactly at 0.363589):
  - Median = last price (no drift: momentum and mean-reversion both hurt).
  - Spread from a ROBUST per-market volatility: mean absolute 1-minute move
    over the last 1h and 4h (blended 50/50), x1.2533 (normal conversion).
    Plain std is dominated by rare huge jumps (88% of minutes are flat) and
    scores far worse; the mean-absolute estimator is jump-robust.
  - Spread grows as h**0.45 (slower than a random walk: jumps partly revert).
  - Outer quantiles (5%/95%) widened x1.3 for jump risk.
  - Sigma floored at 0.0003, capped at 0.012.
Practice loss: 0.2768 vs house baseline 0.3636 (beats it on all 6 cases).
Deterministic, stdlib only, no network.
"""
import json
import math
import os

Z = (-1.644854, -0.674490, 0.0, 0.674490, 1.644854)
SIGMA_FLOOR = 0.0003
SIGMA_CAP = 0.012
ALPHA = 0.45
TAIL_WIDE = 1.3


def sigma_meanabs(prices, window):
    n = len(prices)
    start = max(1, n - window)
    if n - start < 2:
        return SIGMA_FLOOR
    total = 0.0
    for i in range(start, n):
        total += abs(prices[i] - prices[i - 1])
    s = total / (n - start) * 1.2533
    return min(SIGMA_CAP, max(SIGMA_FLOOR, s))


def market_sigma(prices):
    return 0.5 * sigma_meanabs(prices, 60) + 0.5 * sigma_meanabs(prices, 240)


def forecast_market(prices, horizon):
    x = prices[-1]
    s = market_sigma(prices)
    rows = []
    for h in range(1, horizon + 1):
        sp = s * (h ** ALPHA)
        spt = sp * TAIL_WIDE
        row = []
        for zi, z in enumerate(Z):
            w = spt if zi in (0, 4) else sp
            v = x + z * w
            row.append(round(min(1.0, max(0.0, v)), 6))
        rows.append(row)
    return rows


def forecast_case(case):
    horizon = case.get("horizon_minutes", 240)
    out = []
    for m in case["markets"]:
        out.append({"id": m["id"], "q": forecast_market(m["prices"], horizon)})
    return {"forecasts": out}


def main():
    in_dir = os.environ.get("MAKEFUN_INPUT_DIR", "/input")
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    for name in sorted(os.listdir(in_dir)):
        if not name.endswith(".in"):
            continue
        with open(os.path.join(in_dir, name), "r", encoding="utf-8") as f:
            case = json.load(f)
        result = forecast_case(case)
        out_name = name[:-3] + ".out"
        with open(os.path.join(out_dir, out_name), "w", encoding="utf-8") as f:
            json.dump(result, f, separators=(",", ":"), sort_keys=True)


if __name__ == "__main__":
    main()
