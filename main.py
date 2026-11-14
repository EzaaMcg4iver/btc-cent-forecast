"""btc-cent-forecast-01 entry (Python 3.13, standard library only).

Point forecast of BTC/USDC 240 minutes ahead, one number per case.

Method (tuned on the kit's five locally scoreable practice cases, kept
deliberately simple and robust -- five cases cannot support anything fancy):
  * Start from the checkpoint close (the persistence baseline).
  * Add a damped slice of the recent move: 25% of the last 60 minutes'
    change plus 15% of the last 240 minutes' change. BTC's 4-hour returns
    show short-horizon momentum in the practice: extrapolating a quarter
    of the last hour's move beats standing still.
  * Pull 5% of the way back toward the trailing 24-hour mean, a mild
    mean-reversion stabiliser for a 4-hour horizon.
  * Nothing depends on the date, the case id, or any outside data: only the
    case file's own prices. Deterministic: no clock, no randomness, inputs
    read in name order.

Backtest (local, 5 of 6 practice cases -- p05's answer is the close at
2026-11-11T06:00Z, not shipped in the kit; answers for p00..p04 are the
next case's checkpoint close):
  * this entry:  MAE 41,633 cents (mean error $416.33)
  * persistence: MAE 47,055 cents (mean error $470.55) on the same 5 cases
  * kit-stated 6-case persistence baseline: 44,521.576667 cents
  * halves are balanced (first 3 cases 41,029; last 2 cases 42,540), so the
    edge is not one lucky case; the top-scoring variant on all 5 (39,927)
    was NOT picked, to avoid overfitting five cases.

Usage: MAKEFUN_INPUT_DIR=<dir> MAKEFUN_OUTPUT_DIR=<dir> python3 main.py
(defaults /input and /output).
"""

import json
import os
from os import path

INPUT_DIR = os.environ.get("MAKEFUN_INPUT_DIR", "/input")
OUTPUT_DIR = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")

MIN_PRICE = 0.00001
MAX_PRICE = 9_999_999.99999

REVERT_24H = 0.05    # pull toward the trailing 24-hour mean
MOM_60M = 0.25       # slice of the last 60 minutes' move kept
MOM_240M = 0.15      # slice of the last 240 minutes' move kept


def price5(x):
    """Clamp to (0, 10,000,000) and round to the grid's 5 decimals."""
    if x < MIN_PRICE:
        x = MIN_PRICE
    elif x > MAX_PRICE:
        x = MAX_PRICE
    return round(x, 5) + 0.0


def forecast(prices):
    """One price, 240 minutes after the last close in `prices`."""
    n = len(prices)
    if n == 0:
        return price5(1.0)
    last = float(prices[-1])
    if n == 1:
        return price5(last)
    k24 = 1440 if n >= 1440 else n
    mean24 = sum(float(p) for p in prices[n - k24:]) / k24
    k60 = 60 if n - 1 >= 60 else n - 1
    move60 = last - float(prices[n - 1 - k60])
    k240 = 240 if n - 1 >= 240 else n - 1
    move240 = last - float(prices[n - 1 - k240])
    guess = (
        last
        - REVERT_24H * (last - mean24)
        + MOM_60M * move60
        + MOM_240M * move240
    )
    return price5(guess)


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    inputs = sorted(f for f in os.listdir(INPUT_DIR) if f.endswith(".in"))
    for fname in inputs:
        case_id = fname[: -len(".in")]
        with open(path.join(INPUT_DIR, fname), "r", encoding="utf-8") as fh:
            case = json.load(fh)
        markets = case.get("markets") or []
        if not markets or not isinstance(markets[0].get("prices"), list):
            continue  # malformed case: skip it instead of crashing mid-run
        market = markets[0]
        out = json.dumps(
            {"forecasts": [{"case": case_id, "price": forecast(market["prices"])}]},
            separators=(",", ":"),
        ) + "\n"
        with open(path.join(OUTPUT_DIR, case_id + ".out"), "w", encoding="utf-8") as fh:
            fh.write(out)


if __name__ == "__main__":
    main()
