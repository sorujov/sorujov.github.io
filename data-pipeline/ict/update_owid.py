"""Download the annual ICT adoption series published by Our World in Data.

The figures originate with the ITU and the World Bank; OWID republishes them
under CC BY 4.0 with a stable CSV endpoint per chart.  Each file is replaced
whole, because OWID revises past years.
"""

from __future__ import annotations

import io
import os
import sys

import pandas as pd
import requests

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(HERE, "archive", "owid")

#: file stem -> OWID grapher slug
DATASETS = {
    "internet_share": "share-of-individuals-using-the-internet",
    "internet_users": "number-of-internet-users",
    "fixed_broadband_per100": "broadband-penetration-by-country",
    "mobile_subscriptions_per100": "mobile-cellular-subscriptions-per-100-people",
}

ENTITIES = {
    "Armenia", "Azerbaijan", "Belarus", "Georgia", "Kazakhstan", "Kyrgyzstan",
    "Moldova", "Russia", "Tajikistan", "Turkmenistan", "Ukraine", "Uzbekistan",
    "World", "Europe and Central Asia (WB)",
}

HEADERS = {"User-Agent": "Our World In Data data fetch/1.0"}


def main() -> int:
    os.makedirs(OUT_DIR, exist_ok=True)
    failures = []
    for stem, slug in DATASETS.items():
        url = (f"https://ourworldindata.org/grapher/{slug}.csv"
               "?v=1&csvType=full&useColumnShortNames=true")
        try:
            response = requests.get(url, headers=HEADERS, timeout=60)
            response.raise_for_status()
            frame = pd.read_csv(io.StringIO(response.text))
        except Exception as exc:  # keep the previous file on any failure
            print(f"  {stem}: failed ({exc})")
            failures.append(stem)
            continue
        frame = frame[frame["entity"].isin(ENTITIES)]
        if frame.empty:
            print(f"  {stem}: no rows for the region; previous file kept")
            failures.append(stem)
            continue
        frame.to_csv(os.path.join(OUT_DIR, f"{stem}.csv"), index=False)
        print(f"  {stem}: {len(frame)} rows, {frame['year'].min()}-{frame['year'].max()}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
