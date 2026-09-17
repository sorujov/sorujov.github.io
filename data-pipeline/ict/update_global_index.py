"""Append the latest Speedtest Global Index figures to the stored archive.

Each country page on speedtest.net/global-index embeds a ``var data = {...}``
object holding roughly the last thirteen months.  Ookla keeps no longer public
history, so ``archive/global_index.csv`` is the only record of earlier months:
this script must only ever add to it.

Rows are keyed on (country, network, statistic, month).  For a key present in
both the archive and the fresh page, the fresh figure wins, since Ookla revises
recent months.  Nothing is ever removed.  Running the script twice in a month
changes nothing except such revisions.

Usage
-----
    python data-pipeline/ict/update_global_index.py
    python data-pipeline/ict/update_global_index.py --dry-run
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time

import pandas as pd
import requests

HERE = os.path.dirname(os.path.abspath(__file__))
ARCHIVE = os.path.join(HERE, "archive", "global_index.csv")

#: Countries the Global Index still publishes.
COUNTRIES = [
    "armenia", "azerbaijan", "georgia", "kazakhstan", "kyrgyzstan",
    "moldova", "tajikistan", "turkmenistan", "ukraine", "uzbekistan",
]

#: Countries Ookla removed from the index (their pages return 404).  Their
#: stored history is kept as it is and never fetched again.
DISCONTINUED = {"belarus": "2025-04", "russia": "2025-04"}

SERIES = {
    "fixedMean": ("fixed", "mean"),
    "mobileMean": ("mobile", "mean"),
    "fixedMedian": ("fixed", "median"),
    "mobileMedian": ("mobile", "median"),
}

KEY = ["country", "network", "statistic", "month"]
COLUMNS = KEY + [
    "download_mbps", "upload_mbps", "latency_ms", "jitter_ms", "global_rank",
    "period_type", "aggregate_start", "index_date",
]

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
)
_DATA_RE = re.compile(r"var data = (\{.*?\});", re.DOTALL)


def fetch(country: str, session: requests.Session, retries: int = 3) -> dict | None:
    url = f"https://www.speedtest.net/global-index/{country}"
    for attempt in range(1, retries + 1):
        try:
            response = session.get(url, headers={"User-Agent": USER_AGENT}, timeout=30)
            response.raise_for_status()
        except requests.RequestException as exc:
            print(f"  [{country}] attempt {attempt}/{retries} failed: {exc}")
            time.sleep(3 * attempt)
            continue
        match = _DATA_RE.search(response.text)
        if not match:
            print(f"  [{country}] data object not found in the page")
            return None
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError as exc:
            print(f"  [{country}] could not parse data object: {exc}")
            return None
    return None


def to_rows(country: str, payload: dict) -> list[dict]:
    rows = []
    for key, (network, statistic) in SERIES.items():
        for entry in payload.get(key) or []:
            month = entry.get("month")
            if not month:
                continue
            rows.append({
                "country": country,
                "network": network,
                "statistic": statistic,
                "month": str(month),
                "download_mbps": float(entry["download_mbps"]),
                "upload_mbps": float(entry["upload_mbps"]),
                "latency_ms": entry.get("latency_ms"),
                "jitter_ms": entry.get("jitter"),
                "global_rank": entry.get("rank"),
                "period_type": entry.get("time_period_type"),
                "aggregate_start": str(entry.get("aggregate_date", ""))[:10],
                "index_date": entry.get("global_index_date"),
            })
    return rows


def merge(old: pd.DataFrame, new: pd.DataFrame) -> pd.DataFrame:
    """Union of both frames; for duplicate keys the row from ``new`` is kept."""
    both = pd.concat([old, new], ignore_index=True)
    both = both.drop_duplicates(subset=KEY, keep="last")
    return both.sort_values(KEY).reset_index(drop=True)[COLUMNS]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--countries", nargs="*", default=COUNTRIES)
    args = parser.parse_args(argv)

    old = pd.read_csv(ARCHIVE, dtype={"month": str}) if os.path.exists(ARCHIVE) \
        else pd.DataFrame(columns=COLUMNS)
    print(f"Archive: {len(old)} rows, {old['country'].nunique()} countries")

    session = requests.Session()
    fresh, failures = [], []
    for country in args.countries:
        if country in DISCONTINUED:
            continue
        print(f"Fetching {country} ...")
        payload = fetch(country, session)
        if payload:
            fresh.extend(to_rows(country, payload))
        else:
            failures.append(country)
        time.sleep(1.0)

    if not fresh:
        print("Nothing could be fetched; the archive is left untouched.")
        return 1

    merged = merge(old, pd.DataFrame(fresh))
    added = len(merged) - len(old)
    print(f"\nRows added: {added}")
    for country, frame in merged.groupby("country"):
        months = sorted(frame["month"].unique())
        note = f"  (frozen, removed from the index)" if country in DISCONTINUED else ""
        print(f"  {country:<13}{len(months):>3} months  {months[0]} to {months[-1]}{note}")
    if failures:
        print(f"Could not refresh: {', '.join(failures)}")

    if args.dry_run:
        print("Dry run: nothing written.")
        return 0
    merged.to_csv(ARCHIVE, index=False)
    print(f"Written to {ARCHIVE}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
