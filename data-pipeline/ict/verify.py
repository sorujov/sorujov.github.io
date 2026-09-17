"""Checks run before the scheduled job is allowed to commit anything.

The failure worth guarding against is a quiet one: a partial fetch or a change
in the source's format replacing good history with less of it.  Each check is a
floor that a healthy refresh passes easily.

The decisive check compares the Global Index archive with the version already
committed: no country may lose months, and no country may disappear.
"""

from __future__ import annotations

import io
import os
import subprocess
import sys
from datetime import datetime, timezone

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ARCHIVE = os.path.join(HERE, "archive")
REPO_PATH = "data-pipeline/ict/archive/global_index.csv"

MIN_COUNTRIES = 9
MAX_AGE_MONTHS = 4

problems: list[str] = []
notes: list[str] = []


def committed_global_index() -> pd.DataFrame | None:
    try:
        blob = subprocess.run(
            ["git", "show", f"HEAD:{REPO_PATH}"],
            cwd=HERE, capture_output=True, check=True,
        ).stdout
    except Exception:
        return None
    return pd.read_csv(io.BytesIO(blob), dtype={"month": str})


def check_global_index() -> None:
    path = os.path.join(ARCHIVE, "global_index.csv")
    if not os.path.exists(path):
        problems.append("global_index.csv is missing")
        return
    frame = pd.read_csv(path, dtype={"month": str})

    if frame.duplicated(["country", "network", "statistic", "month"]).any():
        problems.append("global_index.csv has duplicate keys")
    if (frame["download_mbps"] <= 0).any():
        problems.append("global_index.csv has non-positive download speeds")
    if frame["country"].nunique() < MIN_COUNTRIES:
        problems.append(f"only {frame['country'].nunique()} countries in global_index.csv")

    previous = committed_global_index()
    if previous is None:
        notes.append("no committed version to compare with")
    else:
        now_counts = frame.groupby(["country", "network", "statistic"])["month"].nunique()
        was_counts = previous.groupby(["country", "network", "statistic"])["month"].nunique()
        for key, was in was_counts.items():
            now = now_counts.get(key)
            if now is None:
                problems.append(f"{'/'.join(key)} disappeared from the archive")
            elif now < was:
                problems.append(f"{'/'.join(key)}: months fell from {was} to {now}")

    newest = frame["month"].max()
    year, month = (int(p) for p in newest.split("-"))
    today = datetime.now(timezone.utc)
    age = (today.year - year) * 12 + today.month - month
    notes.append(f"Global Index: {len(frame)} rows, newest month {newest}")
    if age > MAX_AGE_MONTHS:
        problems.append(f"newest Global Index month is {age} months old; the fetch is probably broken")


def check_regions() -> None:
    path = os.path.join(ARCHIVE, "azerbaijan_regions.csv")
    frame = pd.read_csv(path)
    if frame.duplicated(["region_id", "type", "year", "quarter"]).any():
        problems.append("azerbaijan_regions.csv has duplicate rows")
    if (frame["download_mbps"] <= 0).any():
        problems.append("azerbaijan_regions.csv has non-positive download speeds")
    latest = frame[(frame["type"] == "fixed")].sort_values(["year", "quarter"]).tail(1)
    if not latest.empty:
        y, q = int(latest["year"].iloc[0]), int(latest["quarter"].iloc[0])
        units = frame[(frame["type"] == "fixed") & (frame["year"] == y) & (frame["quarter"] == q)]
        if len(units) < 60:
            problems.append(f"only {len(units)} Azerbaijani units in fixed {y}Q{q}")
        notes.append(f"Azerbaijan regions: {len(frame)} rows, newest fixed quarter {y}Q{q} with {len(units)} units")


def check_ipv6() -> None:
    frame = pd.read_csv(os.path.join(ARCHIVE, "apnic_ipv6.csv"), dtype={"month": str})
    if frame["iso3"].nunique() < 10:
        problems.append(f"IPv6 series for only {frame['iso3'].nunique()} economies")
    if not frame["capable_pct"].between(0, 100).all():
        problems.append("IPv6 shares outside 0-100")
    notes.append(f"APNIC IPv6: {len(frame)} rows, newest month {frame['month'].max()}")


def check_owid() -> None:
    folder = os.path.join(ARCHIVE, "owid")
    files = [f for f in os.listdir(folder) if f.endswith(".csv")]
    if len(files) < 4:
        problems.append(f"only {len(files)} OWID files present")
    for name in files:
        if pd.read_csv(os.path.join(folder, name)).empty:
            problems.append(f"OWID file {name} is empty")
    notes.append(f"OWID: {len(files)} files")


def main() -> int:
    check_global_index()
    check_regions()
    check_ipv6()
    check_owid()
    for line in notes:
        print(f"  {line}")
    if problems:
        print("\nVerification FAILED:", file=sys.stderr)
        for line in problems:
            print(f"  - {line}", file=sys.stderr)
        return 1
    print("All checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
