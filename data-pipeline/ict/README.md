# ICT data pipeline

Source data and scripts behind the page at `/portfolio/cis-internet/`.

Two Ookla products are used, each for one purpose only:

- **Speedtest Global Index** (public, monthly): the comparison of CIS countries.
- **Ookla Open Data** (public tiles, quarterly, CC BY-NC-SA 4.0): Azerbaijan's cities and districts.

No licensed Speedtest Intelligence data is used.
Jekyll does not publish this folder; the page reads the JSON files that
`export_json.py` writes to `assets/data/ict/`.

| File | Role |
|---|---|
| `archive/global_index.csv` | Speedtest Global Index, monthly, from 2023-06. **The only copy of months older than Ookla's 13-month window. Only ever append to it.** |
| `archive/azerbaijan_regions.csv` | Ookla Open Data, quarterly, for Azerbaijan's 78 cities and districts from 2019 Q1 |
| `archive/apnic_ipv6.csv` | APNIC Labs IPv6 capability, monthly, CIS countries and the world (re-use with attribution) |
| `archive/owid/*.csv` | ITU / World Bank adoption series via Our World in Data |
| `geo/cis_countries.geojson` | Natural Earth 1:10m country outlines, for the CIS map |
| `geo/azerbaijan_adm2.geojson` | geoBoundaries ADM2 outlines of Azerbaijan (CC BY-SA 3.0), for tile assignment and the city map |
| `update_global_index.py` | Appends the latest Global Index window (keyed on month) |
| `update_owid.py` | Replaces the OWID files |
| `update_apnic_ipv6.py` | Rebuilds the monthly IPv6 series from APNIC's daily data |
| `build_azerbaijan_regions.py` | Adds new Open Data quarters for Azerbaijan (run quarterly) |
| `verify.py` | Refuses a refresh in which any country loses months |
| `export_json.py` | Writes the four JSON files in `assets/data/ict/` |

The monthly job is `.github/workflows/update-ict-data.yml`.

To run by hand:

```
pip install -r data-pipeline/ict/requirements.txt
python data-pipeline/ict/update_global_index.py
python data-pipeline/ict/update_owid.py
python data-pipeline/ict/update_apnic_ipv6.py
python data-pipeline/ict/verify.py
python data-pipeline/ict/export_json.py
```

Known gaps: May and June 2025 are missing from the Global Index archive and
cannot be recovered. Belarus and Russia were removed from the index by Ookla;
their series end in April 2025.

The history was carried over from the `CIS_Internet` repository in
September 2026.
