"""ARIMA projections of the Global Index series, precomputed for the page.

For every country, network (fixed, mobile), statistic (median,
mean) and measure (download, upload, latency) the script fits the ARIMA model
with a deterministic linear trend that has the lowest AIC among
p in 0..3, d in 0..1, q in 0..3, and projects it 24 months ahead from its last observation (for Belarus and
Russia, which left the index, that is April 2025) with 80, 90
and 95 per cent intervals.  This is the model of the original CIS_Internet
forecast page, moved from the browser session into the monthly job.

The series is the display series: the archive with the two missing months of
2025 filled by linear interpolation.  The intervals are the model's own; with
about three years of monthly data, the uncertainty about the model itself is
larger than they show.

Output: assets/data/ict/forecast.json
"""

from __future__ import annotations

import json
import os
import time
from concurrent.futures import ProcessPoolExecutor

# One BLAS thread per process: the pool already uses every core.
for _var in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_var, "1")
import sys
import warnings

import numpy as np
import pandas as pd
from statsmodels.tsa.arima.model import ARIMA

from ict_common import global_index_filled

warnings.filterwarnings("ignore")

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(os.path.dirname(os.path.dirname(HERE)), "assets", "data", "ict", "forecast.json")

ISO = {
    "armenia": "ARM", "azerbaijan": "AZE", "belarus": "BLR", "russia": "RUS", "georgia": "GEO", "kazakhstan": "KAZ",
    "kyrgyzstan": "KGZ", "moldova": "MDA", "tajikistan": "TJK", "turkmenistan": "TKM",
    "ukraine": "UKR", "uzbekistan": "UZB",
}
MEASURES = {"download": "download_mbps", "upload": "upload_mbps", "latency": "latency_ms"}
HORIZON = 24
LEVELS = (80, 90, 95)
MIN_OBS = 12


def fit(series: pd.Series) -> dict | None:
    """Select and fit the ARIMA-with-trend model; return the projection."""
    y = series.astype(float).to_numpy()
    n = len(y)
    trend = np.arange(n, dtype=float)
    best = None
    for p in range(4):
        for d in range(2):
            for q in range(4):
                if p == q == d == 0:
                    continue
                try:
                    res = ARIMA(y, order=(p, d, q), exog=trend).fit()
                except Exception:  # noqa: BLE001
                    continue
                if np.isfinite(res.aic) and (best is None or res.aic < best[0]):
                    best = (res.aic, (p, d, q), res)
    if best is None:
        return None
    aic, order, res = best
    future = np.arange(n, n + HORIZON, dtype=float)
    pred = res.get_forecast(steps=HORIZON, exog=future)
    mean = np.asarray(pred.predicted_mean)
    bands = {lvl: np.asarray(pred.conf_int(alpha=1 - lvl / 100)) for lvl in LEVELS}
    params = np.asarray(res.params)
    slope = float(params[res.model.param_names.index("x1")]) if "x1" in res.model.param_names else None
    return {"order": order, "aic": float(aic), "slope": slope, "mean": mean, "bands": bands}


def jobs():
    """Yield (key, series, first month, last month) for every projection."""
    gi = global_index_filled()
    for (country, network, statistic), part in gi.groupby(["country", "network", "statistic"]):
        if country not in ISO:
            continue
        part = part.sort_values("month")
        # Forecast only from the unbroken run that reaches the latest month.
        months = pd.PeriodIndex(part["month"], freq="M")
        breaks = np.where(np.diff(months.asi8) != 1)[0]
        if len(breaks):
            part = part.iloc[breaks[-1] + 1:]
        if len(part) < MIN_OBS:
            continue
        for measure, column in MEASURES.items():
            key = f"{ISO[country]}|{network}|{statistic}|{measure}"
            yield key, part[column].to_numpy(), part["month"].iloc[0], part["month"].iloc[-1]


def run(job):
    key, values, first, last = job
    started = time.time()
    result = fit(pd.Series(values))
    print(f"  {key}: {time.time() - started:.1f}s", flush=True)
    if result is None:
        return key, None
    end = pd.Period(last, freq="M")
    rows = []
    for i in range(HORIZON):
        row = [(end + i + 1).strftime("%Y-%m"), round(max(0.0, result["mean"][i]), 2)]
        for lvl in LEVELS:
            lo, hi = result["bands"][lvl][i]
            row += [round(max(0.0, lo), 2), round(max(0.0, hi), 2)]
        rows.append(row)
    return key, {
        "order": list(result["order"]),
        "aic": round(result["aic"], 1),
        "slope": None if result["slope"] is None else round(result["slope"], 3),
        "obs": int(len(values)),
        "start": first,
        "forecast": rows,
    }


def main() -> int:
    out = {"horizon": HORIZON, "levels": list(LEVELS), "series": {}}
    todo = list(jobs())
    failures = 0
    with ProcessPoolExecutor() as pool:
        for key, value in pool.map(run, todo):
            if value is None:
                failures += 1
                print(f"  {key}: no model could be fitted")
                continue
            out["series"][key] = value
    out["series"] = dict(sorted(out["series"].items()))
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(out, fh, separators=(",", ":"))
    print(f"Wrote {len(out['series'])} projections to {OUT} ({os.path.getsize(OUT) / 1024:.0f} KB)")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
