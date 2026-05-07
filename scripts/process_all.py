"""Standardize provenance logs into chart-ready Nepal pilot outputs."""

from __future__ import annotations

import csv
import json
import pathlib
from collections import Counter
from datetime import datetime, timezone

CASE_ID = "nepal-gorkha-2015"
PROV = pathlib.Path("public/data/provenance") / CASE_ID
OUT = pathlib.Path("public/data/processed") / CASE_ID


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else None


def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def write_csv(path, rows, fields):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def iso_from_millis(value):
    return datetime.fromtimestamp(value / 1000, tz=timezone.utc).isoformat() if value else None


def event_profile(usgs):
    if not usgs:
        return {"data_quality": "not_available", "status_note": "Run scripts/fetch_usgs.py."}
    event = usgs.get("event", {})
    coords = (event.get("geometry") or {}).get("coordinates") or [None, None, None]
    return {
        "title": event.get("title"),
        "event_time_utc": iso_from_millis(event.get("time")),
        "magnitude": event.get("magnitude"),
        "magnitude_type": event.get("magnitude_type"),
        "depth_km": coords[2],
        "longitude": coords[0],
        "latitude": coords[1],
        "place": event.get("place"),
        "source": "USGS Earthquake Hazards Program",
        "source_url": event.get("source_url") or usgs.get("url"),
        "unit": "Mw, km, decimal degrees",
        "processing_method": "Direct extraction from USGS GeoJSON event properties and geometry.",
        "data_quality": usgs.get("data_quality", "api_verified"),
    }


def unit_for_indicator(indicator_id):
    return {
        "NY.GDP.MKTP.CD": "current US$",
        "NY.GDP.PCAP.CD": "current US$ per person",
        "SP.POP.TOTL": "people",
        "SP.URB.TOTL.IN.ZS": "percent",
    }.get(indicator_id, "not_available")


def worldbank_rows(worldbank):
    rows = []
    if not worldbank:
        return rows
    for indicator_id, record in worldbank.get("indicators", {}).items():
        for item in record.get("data", []):
            if item.get("value") is None:
                continue
            rows.append({
                "indicator_id": indicator_id,
                "indicator": record.get("label", indicator_id),
                "year": int(item.get("year")),
                "value": item.get("value"),
                "unit": unit_for_indicator(indicator_id),
                "source": "World Bank WDI API",
                "processing_method": "Fetched annual national indicator values for Nepal; sorted ascending by year.",
                "data_quality": "national_context_only",
            })
    return sorted(rows, key=lambda row: (row["indicator_id"], row["year"]))


def reliefweb_frequency(reliefweb):
    if not reliefweb:
        return [], "not_available"
    quality = reliefweb.get("data_quality", "not_available")
    counts = Counter()
    for item in (reliefweb.get("payload") or {}).get("data", []):
        fields = item.get("fields", {})
        created = ((fields.get("date") or {}).get("created") or "")[:7]
        if created:
            counts[created] += 1
    rows = [
        {
            "month": month,
            "value": count,
            "unit": "ReliefWeb report count",
            "source": "ReliefWeb Reports API",
            "processing_method": "Search query filtered to Nepal; monthly counts of returned report creation dates.",
            "data_quality": "api_search_results",
        }
        for month, count in sorted(counts.items())
    ]
    return rows, ("api_search_results" if rows else quality)


def manual_layer(title, source, unit, notes):
    return {
        "title": title,
        "status": "manual_required",
        "source": source,
        "unit": unit,
        "processing_method": "Documented source exists, but affected-area raster processing has not yet been run.",
        "data_quality": "manual_required",
        "points": [],
        "notes": notes,
    }


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    usgs = read_json(PROV / "usgs_event.json")
    reliefweb = read_json(PROV / "reliefweb_reports.json")
    worldbank = read_json(PROV / "worldbank_indicators.json")
    wb_rows = worldbank_rows(worldbank)
    relief_rows, relief_quality = reliefweb_frequency(reliefweb)

    write_csv(OUT / "worldbank_context.csv", wb_rows, ["indicator_id", "indicator", "year", "value", "unit", "source", "processing_method", "data_quality"])
    write_csv(OUT / "reliefweb_report_frequency.csv", relief_rows, ["month", "value", "unit", "source", "processing_method", "data_quality"])

    generated_at = datetime.now(timezone.utc).isoformat()
    ecological = manual_layer("Ecological recovery trend", "NASA LP DAAC MODIS MOD13Q1/MYD13Q1; ESA WorldCover/CCI", "NDVI, EVI, NBR, LULC class area, LST", "Define boundary, download raster products, apply QA masks, compute zonal statistics, then write chart-ready annual series.")
    ntl = manual_layer("Economic recovery proxy trend", "NASA Black Marble or NOAA VIIRS DNB", "radiance", "Night-time lights require raster processing before local recovery proxy values can be shown.")
    settlement = manual_layer("Population and settlement exposure", "JRC GHSL, WorldPop, affected-area boundary", "people, built-up area", "Exposure metrics require boundary-based gridded population and settlement aggregation.")

    observatory = {
        "case_id": CASE_ID,
        "case_name": "Nepal 2015 Gorkha Earthquake",
        "generated_at_utc": generated_at,
        "event_profile": event_profile(usgs),
        "ecological_recovery": ecological,
        "economic_recovery_proxy": {
            "night_time_lights": ntl,
            "worldbank_context": {
                "title": "National economic context",
                "status": "available_context_only" if wb_rows else "not_available",
                "source": "World Bank WDI API",
                "unit": "current US$, current US$ per person",
                "processing_method": "Annual national Nepal indicators; not a local recovery proxy.",
                "data_quality": "national_context_only" if wb_rows else "not_available",
                "series": [{k: row[k] for k in ["indicator_id", "indicator", "year", "value", "unit"]} for row in wb_rows if row["indicator_id"] in {"NY.GDP.MKTP.CD", "NY.GDP.PCAP.CD"}],
            },
        },
        "population_settlement": {
            "settlement_exposure": settlement,
            "worldbank_population_context": {
                "title": "National population context",
                "status": "available_context_only" if wb_rows else "not_available",
                "source": "World Bank WDI API",
                "unit": "people, percent urban",
                "processing_method": "Annual national Nepal indicators; not affected-area exposure.",
                "data_quality": "national_context_only" if wb_rows else "not_available",
                "series": [{k: row[k] for k in ["indicator_id", "indicator", "year", "value", "unit"]} for row in wb_rows if row["indicator_id"] in {"SP.POP.TOTL", "SP.URB.TOTL.IN.ZS"}],
            },
        },
        "social_sensing": {
            "title": "ReliefWeb report frequency",
            "status": "available" if relief_rows else "not_available",
            "source": "ReliefWeb Reports API",
            "unit": "monthly report count",
            "processing_method": "Search query filtered to Nepal; counts of returned report creation dates.",
            "data_quality": relief_quality,
            "points": relief_rows,
        },
        "policy_reconstruction_timeline": {
            "title": "Response and reconstruction timeline candidates",
            "status": "not_available",
            "source": "ReliefWeb Reports API",
            "unit": "report item",
            "processing_method": "Keyword-filtered ReliefWeb titles; human review required for official policy timeline.",
            "data_quality": relief_quality,
            "entries": [],
        },
    }
    write_json(OUT / "observatory.json", observatory)
    write_json(PROV / "processing_notes.json", {
        "case_id": CASE_ID,
        "generated_at_utc": generated_at,
        "principle": "No fabricated values. Missing or unprocessed indicators are marked manual_required or not_available.",
        "outputs": [str(OUT / "observatory.json"), str(OUT / "worldbank_context.csv"), str(OUT / "reliefweb_report_frequency.csv")],
    })
    print(f"Wrote {OUT / 'observatory.json'}")


if __name__ == "__main__":
    main()
