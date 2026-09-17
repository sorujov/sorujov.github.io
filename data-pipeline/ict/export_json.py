"""Write the compact JSON files that the ICT data page reads in the browser.

Output (all under assets/data/ict/):
    ict.json        Global Index speeds, ITU adoption and APNIC IPv6 series for the CIS countries
    countries.json  simplified country outlines for the CIS map
    az_regions.json quarterly Open Data figures for Azerbaijan's cities and districts
    az_map.json     simplified outlines of those cities and districts
"""

from __future__ import annotations

import json
import os
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
ARCHIVE = os.path.join(HERE, "archive")
OUT = os.path.join(ROOT, "assets", "data", "ict")

COUNTRIES = {  # slug -> (display name, ISO3)
    "armenia": ("Armenia", "ARM"),
    "azerbaijan": ("Azerbaijan", "AZE"),
    "belarus": ("Belarus", "BLR"),
    "georgia": ("Georgia", "GEO"),
    "kazakhstan": ("Kazakhstan", "KAZ"),
    "kyrgyzstan": ("Kyrgyzstan", "KGZ"),
    "moldova": ("Moldova", "MDA"),
    "russia": ("Russia", "RUS"),
    "tajikistan": ("Tajikistan", "TJK"),
    "turkmenistan": ("Turkmenistan", "TKM"),
    "ukraine": ("Ukraine", "UKR"),
    "uzbekistan": ("Uzbekistan", "UZB"),
}
DISCONTINUED = {"belarus", "russia"}

OWID = {  # file stem -> (value column, label, unit)
    "internet_share": ("it_net_user_zs", "Individuals using the internet", "% of population"),
    "fixed_broadband_per100": ("it_net_bbnd_p2", "Fixed broadband subscriptions", "per 100 people"),
    "mobile_subscriptions_per100": ("it_cel_sets_p2", "Mobile cellular subscriptions", "per 100 people"),
}
AGGREGATES = {"World": "WLD", "Europe and Central Asia (WB)": "ECA"}


def r(x, nd=2):
    return None if pd.isna(x) else round(float(x), nd)


def global_index() -> tuple[dict, str]:
    gi = pd.read_csv(os.path.join(ARCHIVE, "global_index.csv"), dtype={"month": str})
    out: dict = {}
    for (country, network, statistic), frame in gi.groupby(["country", "network", "statistic"]):
        iso = COUNTRIES[country][1]
        rows = [
            [m, r(d), r(u), r(l, 0), None if pd.isna(k) else int(k)]
            for m, d, u, l, k in frame.sort_values("month")[
                ["month", "download_mbps", "upload_mbps", "latency_ms", "global_rank"]
            ].itertuples(index=False)
        ]
        out.setdefault(iso, {}).setdefault(network, {})[statistic] = rows
    # First month reported as a rolling three-month figure.
    rolling = gi.loc[gi["period_type"] == "rolling_quarter", "month"]
    return out, (rolling.min() if len(rolling) else None), gi["month"].max()


MIN_TESTS = 30  # below this a unit's quarterly figure is shown as too uncertain


def azerbaijan_regions() -> dict:
    df = pd.read_csv(os.path.join(ARCHIVE, "azerbaijan_regions.csv"))
    df["period"] = df["year"].astype(str) + "-Q" + df["quarter"].astype(str)
    df = df.sort_values(["year", "quarter"])
    regions = (
        df[["region_id", "name", "kind"]].drop_duplicates("region_id")
        .sort_values(["kind", "name"])
        .rename(columns={"region_id": "id"}).to_dict("records")
    )
    series: dict = {}
    for (rid, kind), part in df.groupby(["region_id", "type"]):
        series.setdefault(rid, {})[kind] = [
            [p, r(d, 1), r(u, 1), r(l, 0), r(m, 1), int(t)]
            for p, d, u, l, m, t in part[[
                "period", "download_mbps", "upload_mbps", "latency_ms",
                "tile_median_download_mbps", "tests",
            ]].itertuples(index=False)
        ]
    national, quarters = {}, {}
    for kind, part in df.groupby("type"):
        w = part.assign(wd=part["download_mbps"] * part["tests"])
        agg = w.groupby(["year", "quarter", "period"], as_index=False).agg(wd=("wd", "sum"), tests=("tests", "sum"))
        national[kind] = [[p, r(wd / t, 1), int(t)] for p, wd, t in agg[["period", "wd", "tests"]].itertuples(index=False)]
        quarters[kind] = agg["period"].tolist()
    return {"min_tests": MIN_TESTS, "quarters": quarters, "regions": regions,
            "national": national, "series": series}


def owid() -> dict:
    out: dict = {}
    isos = {iso for _, iso in COUNTRIES.values()}
    for stem, (column, label, unit) in OWID.items():
        frame = pd.read_csv(os.path.join(ARCHIVE, "owid", f"{stem}.csv"))
        series = {}
        for entity, part in frame.groupby("entity"):
            code = AGGREGATES.get(entity, part["code"].iloc[0])
            if code not in isos and code not in AGGREGATES.values():
                continue
            part = part[part["year"] >= 2000].sort_values("year")
            series[code] = [[int(y), r(v)] for y, v in part[["year", column]].itertuples(index=False)]
        out[stem] = {"label": label, "unit": unit, "series": series}
    return out


def ipv6() -> dict:
    df = pd.read_csv(os.path.join(ARCHIVE, "apnic_ipv6.csv"), dtype={"month": str})
    return {
        iso: [[m, r(c), r(p)] for m, c, p in part[["month", "capable_pct", "preferred_pct"]].itertuples(index=False)]
        for iso, part in df.sort_values("month").groupby("iso3")
    }


def simplified_map(filename: str, id_key: str, name_key: str, tolerance: float, digits: int) -> dict:
    """Simplify outlines for the browser and round their coordinates."""
    from shapely.geometry import mapping, shape
    from shapely.geometry.polygon import orient

    with open(os.path.join(HERE, "geo", filename), encoding="utf-8") as fh:
        geo = json.load(fh)
    features = []
    for feat in geo["features"]:
        geom = shape(feat["geometry"]).simplify(tolerance, preserve_topology=True)
        # d3-geo expects clockwise exterior rings (the opposite of RFC 7946)
        if geom.geom_type == "Polygon":
            geom = orient(geom, sign=-1.0)
        else:
            geom = type(geom)([orient(g, sign=-1.0) for g in geom.geoms])
        gj = json.loads(json.dumps(mapping(geom)), parse_float=lambda x: round(float(x), digits))
        features.append({"type": "Feature", "id": feat["properties"][id_key],
                         "properties": {"name": feat["properties"][name_key]}, "geometry": gj})
    return {"type": "FeatureCollection", "features": features}


def main() -> None:
    os.makedirs(OUT, exist_ok=True)
    gi, rolling_from, newest = global_index()
    payload = {
        "latest_month": newest,
        "rolling_from": rolling_from,
        "countries": [
            {"iso3": iso, "name": name, "discontinued": slug in DISCONTINUED}
            for slug, (name, iso) in COUNTRIES.items()
        ],
        "global_index": gi,
        "adoption": owid(),
        "ipv6": ipv6(),
    }
    with open(os.path.join(OUT, "ict.json"), "w", encoding="utf-8") as fh:
        json.dump(payload, fh, separators=(",", ":"))
    outputs = {
        "countries.json": simplified_map("cis_countries.geojson", "iso3", "country", 0.05, 2),
        "az_map.json": simplified_map("azerbaijan_adm2.geojson", "region_id", "name", 0.004, 3),
        "az_regions.json": azerbaijan_regions(),
    }
    for name, content in outputs.items():
        with open(os.path.join(OUT, name), "w", encoding="utf-8") as fh:
            json.dump(content, fh, separators=(",", ":"))
    for name in ["ict.json", *outputs]:
        print(f"  {name}: {os.path.getsize(os.path.join(OUT, name)) / 1024:.0f} KB")


if __name__ == "__main__":
    main()
