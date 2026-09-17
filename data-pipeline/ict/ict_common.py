"""Helpers shared by the export and forecast scripts."""

from __future__ import annotations

import os

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ARCHIVE = os.path.join(HERE, "archive")

KEY = ["country", "network", "statistic"]
MAX_GAP = 3
VALUES = ["download_mbps", "upload_mbps", "latency_ms", "jitter_ms", "global_rank"]


def global_index_filled() -> pd.DataFrame:
    """The Global Index archive with interior monthly gaps filled.

    The archive itself is left exactly as collected.  For display and for the
    forecasts, months missing *inside* a country's series (May and June 2025)
    are filled by linear interpolation between the neighbouring months.  Only
    gaps of at most ``MAX_GAP`` months are filled; a longer break (Tajikistan's
    mobile series skips two years) is left open, and a series is never
    extended past its first or last observation.
    """
    gi = pd.read_csv(os.path.join(ARCHIVE, "global_index.csv"), dtype={"month": str})
    parts = []
    for key, part in gi.groupby(KEY):
        part = part.sort_values("month").copy()
        idx = pd.PeriodIndex(part["month"], freq="M")
        part.index = idx
        full = pd.period_range(idx.min(), idx.max(), freq="M")
        filled = part.reindex(full)
        missing = filled["month"].isna()
        run_id = (~missing).cumsum()
        run_len = missing.groupby(run_id).transform("sum")
        fillable = missing & (run_len <= MAX_GAP)
        interpolated = filled[VALUES].astype(float).interpolate(method="linear", limit_area="inside")
        filled.loc[fillable, VALUES] = interpolated.loc[fillable, VALUES]
        filled["global_rank"] = filled["global_rank"].round()
        filled["interpolated"] = fillable
        filled = filled[~missing | fillable]
        filled["month"] = filled.index.strftime("%Y-%m")
        for col, value in zip(KEY, key):
            filled[col] = value
        parts.append(filled.reset_index(drop=True))
    return pd.concat(parts, ignore_index=True)
