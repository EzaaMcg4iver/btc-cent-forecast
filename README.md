# btc-cent-forecast-01

Point forecast of BTC/USDC 240 minutes ahead (make.fun btc-cent-forecast-01).

`main.py` (Python 3.13, stdlib only) reads each case in `/input` and writes
one price guess to `/output/<id>.out`. Method: checkpoint close plus a damped
slice of the recent move (25% of the last 60 minutes, 15% of the last 240)
minus a 5% pull toward the trailing 24-hour mean.

Local backtest on the kit practice cases p00..p04 (p05 answer not shipped):
MAE 41,633 cents vs persistence baseline 47,055 cents on the same cases.
