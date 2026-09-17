"""Monthly IPv6 capability for the CIS countries, from APNIC Labs.

APNIC measures, through online advertisements, the share of users whose
browser can fetch an object over IPv6 ("capable") and the share that prefers
IPv6 when both are offered ("preferred").  The daily country series are
published as JSON, copyright APNIC, with re-use permitted on attribution.

The monthly figure is a ratio estimator over the month: the number of
IPv6-capable samples divided by the number of samples seen.  Months with
fewer than 20 days of data are dropped.  The whole series is rebuilt each run,
because APNIC republishes its full history.
"""

from __future__ import annotations

import os
import sys
import time

import pandas as pd
import requests

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "archive", "apnic_ipv6.csv")
BASE = "https://data1.labs.apnic.net/v6stats"

SOURCES = {  # ISO3 -> path under BASE
    "ARM": "v6economy/AM", "AZE": "v6economy/AZ", "BLR": "v6economy/BY",
    "GEO": "v6economy/GE", "KAZ": "v6economy/KZ", "KGZ": "v6economy/KG",
    "MDA": "v6economy/MD", "RUS": "v6economy/RU", "TJK": "v6economy/TJ",
    "TKM": "v6economy/TM", "UKR": "v6economy/UA", "UZB": "v6economy/UZ",
    "WLD": "v6region/XA",
}
START = "2015-01"
MIN_DAYS = 20


def fetch(path: str) -> pd.DataFrame:
    for attempt in range(3):
        try:
            response = requests.get(f"{BASE}/{path}.json", timeout=120)
            response.raise_for_status()
            rows = response.json()["data"]
            break
        except Exception as exc:  # noqa: BLE001
            print(f"  {path}: attempt {attempt + 1} failed ({exc})")
            time.sleep(5 * (attempt + 1))
    else:
        return pd.DataFrame()
    frame = pd.DataFrame(
        {
            "date": [r["date"] for r in rows],
            "seen": [r["raw"]["seen"] for r in rows],
            "capable": [r["raw"]["capable"] for r in rows],
            "preferred": [r["raw"]["preferred"] for r in rows],
        }
    )
    frame["month"] = frame["date"].str.slice(0, 7)
    return frame[frame["month"] >= START]


def monthly(frame: pd.DataFrame) -> pd.DataFrame:
    g = frame[frame["seen"] > 0].groupby("month").agg(
        days=("date", "nunique"), seen=("seen", "sum"),
        capable=("capable", "sum"), preferred=("preferred", "sum"),
    )
    g = g[g["days"] >= MIN_DAYS]
    return pd.DataFrame({
        "month": g.index,
        "capable_pct": (100 * g["capable"] / g["seen"]).round(2).values,
        "preferred_pct": (100 * g["preferred"] / g["seen"]).round(2).values,
        "samples": g["seen"].round().astype("int64").values,
    })


def main() -> int:
    previous = pd.read_csv(OUT) if os.path.exists(OUT) else pd.DataFrame()
    frames, failures = [], []
    for iso, path in SOURCES.items():
        raw = fetch(path)
        if raw.empty:
            failures.append(iso)
            if not previous.empty:  # keep what we had rather than lose the country
                frames.append(previous[previous["iso3"] == iso])
            continue
        m = monthly(raw)
        m.insert(0, "iso3", iso)
        frames.append(m)
        print(f"  {iso}: {len(m)} months, latest {m['month'].iloc[-1]} = {m['capable_pct'].iloc[-1]}% capable")
    out = pd.concat(frames, ignore_index=True).sort_values(["iso3", "month"])
    out.to_csv(OUT, index=False)
    print(f"Wrote {len(out)} rows to {OUT}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
