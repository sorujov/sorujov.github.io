"""Quarterly internet speeds for every city and district of Azerbaijan.

Reads Ookla Open Data (the public, tile-level release on S3; no licensed
Speedtest Intelligence data is used), keeps the tiles inside Azerbaijan,
assigns each tile to one of the 78 second-level units -- cities such as Baku,
Ganja and Sumqayit, and the districts -- by the position of its centre, and
aggregates per unit, quarter and connection type.

For each unit the output carries
  * download, upload and latency averaged over tiles with the number of tests
    as weights (the same statistic as the country panel), and
  * the median download over tiles, which is less affected by a handful of
    very fast tiles,
together with the number of tiles, tests and devices behind the figures.

Boundaries: geoBoundaries ADM2 for Azerbaijan (source: Wikipedia, licensed
CC BY-SA 3.0), stored in geo/azerbaijan_adm2.geojson.

Usage
-----
    python data-pipeline/ict/build_azerbaijan_regions.py            # incremental
    python data-pipeline/ict/build_azerbaijan_regions.py --rebuild
"""

from __future__ import annotations

import argparse
import math
import os
import sys
import time
import xml.etree.ElementTree as ET

import numpy as np
import pandas as pd
import requests

HERE = os.path.dirname(os.path.abspath(__file__))
GEOJSON = os.path.join(HERE, "geo", "azerbaijan_adm2.geojson")
OUT_CSV = os.path.join(HERE, "archive", "azerbaijan_regions.csv")

WEST, SOUTH, EAST, NORTH = 44.70, 38.35, 50.70, 41.95
BBOX_SQL = f"tile_x BETWEEN {WEST} AND {EAST} AND tile_y BETWEEN {SOUTH} AND {NORTH}"

AGGREGATE = """
SELECT
    r.region_id,
    r.name,
    r.kind,
    count(*)                                               AS tiles,
    sum(t.tests)                                           AS tests,
    sum(t.devices)                                         AS devices,
    sum(t.avg_d_kbps * t.tests) / sum(t.tests) / 1000.0    AS download_mbps,
    sum(t.avg_u_kbps * t.tests) / sum(t.tests) / 1000.0    AS upload_mbps,
    sum(t.avg_lat_ms * t.tests) / sum(t.tests)             AS latency_ms,
    median(t.avg_d_kbps) / 1000.0                          AS tile_median_download_mbps
FROM tiles t
JOIN regions r
  ON ST_Within(ST_Point(t.tile_x, t.tile_y), r.geom)
GROUP BY 1, 2, 3
"""

COLUMNS = [
    "region_id", "name", "kind", "type", "year", "quarter",
    "download_mbps", "upload_mbps", "latency_ms", "tile_median_download_mbps",
    "tests", "devices", "tiles",
]


# ---------------------------------------------------------------- Open Data files

BUCKET = "https://ookla-open-data.s3.amazonaws.com"
TYPES = ("fixed", "mobile")


def list_quarters(kind: str) -> list[tuple[int, int, str]]:
    """List every (year, quarter, url) available for one connection type."""
    quarters, token = [], None
    while True:
        url = f"{BUCKET}/?list-type=2&prefix=parquet/performance/type={kind}/"
        if token:
            url += f"&continuation-token={requests.utils.quote(token, safe='')}"
        response = requests.get(url, timeout=60)
        response.raise_for_status()
        root = ET.fromstring(response.text)
        ns = {"s3": "http://s3.amazonaws.com/doc/2006-03-01/"}
        for contents in root.findall("s3:Contents", ns):
            key = contents.find("s3:Key", ns).text
            if not key.endswith(".parquet"):
                continue
            try:
                year = int(key.split("year=")[1].split("/")[0])
                quarter = int(key.split("quarter=")[1].split("/")[0])
            except (IndexError, ValueError):
                continue
            quarters.append((year, quarter, f"{BUCKET}/{key}"))
        truncated = root.find("s3:IsTruncated", ns)
        if truncated is not None and truncated.text == "true":
            token = root.find("s3:NextContinuationToken", ns).text
        else:
            break
    return sorted(set(quarters))


def has_coordinates(con, url: str) -> bool:
    """Whether this file carries tile_x / tile_y columns.

    Ookla's schema is not consistent across releases (the 2019 files and
    2021 Q3 lack them), so ask the file rather than assuming.
    """
    columns = con.execute(
        f"DESCRIBE SELECT * FROM read_parquet('{url}')"
    ).fetchall()
    return "tile_x" in {row[0] for row in columns}


def _lonlat_to_tile(lon: float, lat: float, zoom: int) -> tuple[int, int]:
    lat = max(min(lat, 85.05112878), -85.05112878)
    n = 2 ** zoom
    x = int((lon + 180.0) / 360.0 * n)
    sin_lat = math.sin(math.radians(lat))
    y = int((0.5 - math.log((1 + sin_lat) / (1 - sin_lat)) / (4 * math.pi)) * n)
    return min(max(x, 0), n - 1), min(max(y, 0), n - 1)


def _tile_to_quadkey(x: int, y: int, zoom: int) -> str:
    digits = []
    for i in range(zoom, 0, -1):
        digit, mask = 0, 1 << (i - 1)
        if x & mask:
            digit += 1
        if y & mask:
            digit += 2
        digits.append(str(digit))
    return "".join(digits)


def decode_quadkeys(quadkeys: pd.Series) -> tuple[np.ndarray, np.ndarray]:
    """Vectorised quadkey -> tile-centre longitude/latitude."""
    zoom = len(quadkeys.iloc[0])
    digits = (
        np.frombuffer("".join(quadkeys).encode("ascii"), dtype="S1")
        .view(np.uint8)
        .reshape(-1, zoom)
        - ord("0")
    )
    weights = (1 << np.arange(zoom - 1, -1, -1)).astype(np.int64)
    x = ((digits & 1) * weights).sum(axis=1)
    y = (((digits >> 1) & 1) * weights).sum(axis=1)
    n = float(1 << zoom)
    lon = (x + 0.5) / n * 360.0 - 180.0
    lat = np.degrees(np.arctan(np.sinh(np.pi * (1.0 - 2.0 * (y + 0.5) / n))))
    return lon, lat


# ------------------------------------------------------------------ aggregation

def connect():
    import duckdb

    con = duckdb.connect()
    con.execute("INSTALL httpfs; LOAD httpfs;")
    con.execute("INSTALL spatial; LOAD spatial;")
    con.execute("SET enable_progress_bar=false;")
    con.execute(
        "CREATE TABLE regions AS "
        f"SELECT region_id, name, kind, geom FROM ST_Read('{GEOJSON}')"
    )
    return con


def quadkey_clause(zoom: int = 8) -> str:
    """Quadkey ranges covering Azerbaijan, for files without coordinates."""
    x0, y0 = _lonlat_to_tile(WEST, NORTH, zoom)
    x1, y1 = _lonlat_to_tile(EAST, SOUTH, zoom)
    prefixes = sorted(
        _tile_to_quadkey(x, y, zoom)
        for x in range(x0, x1 + 1) for y in range(y0, y1 + 1)
    )
    return " OR ".join(f"(quadkey >= '{p}' AND quadkey < '{p}4')" for p in prefixes)


def one_quarter(con, url: str) -> pd.DataFrame:
    if has_coordinates(con, url):
        con.execute(
            "CREATE OR REPLACE TEMP TABLE tiles AS "
            "SELECT tile_x, tile_y, avg_d_kbps, avg_u_kbps, avg_lat_ms, tests, devices "
            f"FROM read_parquet(?) WHERE {BBOX_SQL} AND tests > 0",
            [url],
        )
    else:
        raw = con.execute(
            "SELECT quadkey, avg_d_kbps, avg_u_kbps, avg_lat_ms, tests, devices "
            f"FROM read_parquet(?) WHERE tests > 0 AND ({quadkey_clause()})",
            [url],
        ).fetchdf()
        if raw.empty:
            return raw
        lon, lat = decode_quadkeys(raw["quadkey"])
        raw = raw.assign(tile_x=lon, tile_y=lat).drop(columns=["quadkey"])
        keep = (raw.tile_x.between(WEST, EAST) & raw.tile_y.between(SOUTH, NORTH)).to_numpy()
        legacy = raw.loc[keep]  # noqa: F841 -- read by the SQL below
        con.execute("CREATE OR REPLACE TEMP TABLE tiles AS SELECT * FROM legacy")
    return con.execute(AGGREGATE).fetchdf()


def build(rebuild: bool = False, since: int = 0) -> None:
    existing = pd.DataFrame(columns=COLUMNS)
    if os.path.exists(OUT_CSV) and not rebuild:
        existing = pd.read_csv(OUT_CSV)
    done = set(zip(existing["type"], existing["year"], existing["quarter"]))

    con = connect()
    frames = [existing]
    for kind in TYPES:
        for year, quarter, url in list_quarters(kind):
            if year < since or (kind, year, quarter) in done:
                continue
            started = time.time()
            try:
                frame = one_quarter(con, url)
            except Exception as exc:
                print(f"  {kind} {year}Q{quarter}: FAILED ({exc})")
                continue
            if frame.empty:
                print(f"  {kind} {year}Q{quarter}: no rows")
                continue
            frame = frame.assign(type=kind, year=year, quarter=quarter)
            frames.append(frame)
            print(f"  {kind} {year}Q{quarter}: {len(frame)} units, "
                  f"{int(frame['tests'].sum()):,} tests, {time.time() - started:.0f}s")

    out = pd.concat(frames, ignore_index=True)
    out = out.drop_duplicates(["region_id", "type", "year", "quarter"], keep="last")
    out = out[COLUMNS].sort_values(["type", "year", "quarter", "region_id"])
    for col in ("download_mbps", "upload_mbps", "tile_median_download_mbps"):
        out[col] = out[col].astype(float).round(3)
    out["latency_ms"] = out["latency_ms"].astype(float).round(2)
    out.to_csv(OUT_CSV, index=False)
    print(f"Wrote {len(out)} rows to {OUT_CSV}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rebuild", action="store_true")
    parser.add_argument("--since", type=int, default=0)
    args = parser.parse_args(argv)
    if not os.path.exists(GEOJSON):
        print(f"Missing boundaries at {GEOJSON}", file=sys.stderr)
        return 2
    build(rebuild=args.rebuild, since=args.since)
    return 0


if __name__ == "__main__":
    sys.exit(main())
