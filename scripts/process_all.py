"""Standardize provenance logs into chart-ready Nepal pilot outputs."""

from __future__ import annotations

import csv
import json
import pathlib
import re
from collections import Counter
from datetime import datetime, timezone


CASE_ID = "nepal-gorkha-2015"
PROVENANCE = pathlib.Path("public/data/provenance") / CASE_ID
PROCESSED = pathlib.Path("public/data/processed") / CASE_ID


def read_json(path: pathlib.Path) -> dict | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: pathlib.Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def write_csv(path: pathlib.Path, rows: list[dict], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def iso_from_millis(value: int | float | None) -> str | None:
    if value is None:
        return None
    return datetime.fromtimestamp(value / 1000, tz=timezone.utc).isoformat()


def event_profile(usgs: dict | None) -> dict:
    if not usgs:
        return {"data_quality": "not_available", "status_note": "Run scripts/fetch_usgs.py to retrieve USGS event metadata."}
    event = usgs.get("event")
    if event:
        coords = (event.get("geometry") or {}).get("coordinates") or [None, None, None]
        return {
            "title": event.get("title"), "event_time_utc": iso_from_millis(event.get("time")),
            "magnitude": event.get("magnitude"), "magnitude_type": event.get("magnitude_type"),
            "depth_km": coords[2], "longitude": coords[0], "latitude": coords[1], "place": event.get("place"),
            "source": "USGS Earthquake Hazards Program", "source_url": event.get("source_url") or usgs.get("url"),
            "unit": "Mw, km, decimal degrees", "processing_method": "Direct extraction from USGS GeoJSON event properties and geometry.",
            "data_quality": usgs.get("data_quality", "api_verified"),
        }
    payload = usgs.get("payload", {})
    props = payload.get("properties", {})
    coords = (payload.get("geometry") or {}).get("coordinates") or [None, None, None]
    return {
        "title": props.get("title"), "event_time_utc": iso_from_millis(props.get("time")),
        "magnitude": props.get("mag"), "magnitude_type": props.get("magType"),
        "depth_km": coords[2], "longitude": coords[0], "latitude": coords[1], "place": props.get("place"),
        "source": "USGS Earthquake Hazards Program", "source_url": props.get("url") or usgs.get("url"),
        "unit": "Mw, km, decimal degrees", "processing_method": "Direct extraction from USGS GeoJSON event properties and geometry.",
        "data_quality": usgs.get("data_quality", "api_verified"),
    }


def unit_for_indicator(indicator_id: str) -> str:
    return {
        "NY.GDP.MKTP.CD": "current US$",
        "NY.GDP.PCAP.CD": "current US$ per person",
        "SP.POP.TOTL": "people",
        "SP.URB.TOTL.IN.ZS": "percent",
    }.get(indicator_id, "not_available")


def worldbank_series(worldbank: dict | None) -> list[dict]:
    if not worldbank:
        return []
    rows = []
    for indicator_id, record in worldbank.get("indicators", {}).items():
        label = record.get("label", indicator_id)
        observations = record.get("data")
        if observations is None:
            payload = record.get("payload") or []
            observations = payload[1] if isinstance(payload, list) and len(payload) > 1 else []
        for item in observations or []:
            if item.get("value") is None:
                continue
            year = item.get("date") or item.get("year")
            rows.append({
                "indicator_id": indicator_id, "indicator": label, "year": int(year), "value": item["value"],
                "unit": unit_for_indicator(indicator_id), "source": "World Bank WDI API",
                "processing_method": "Fetched annual national indicator values for Nepal; sorted ascending by year.",
                "data_quality": "national_context_only",
            })
    return sorted(rows, key=lambda row: (row["indicator_id"], row["year"]))


def reliefweb_outputs(reliefweb: dict | None) -> tuple[list[dict], list[dict]]:
    if not reliefweb:
        return [], []
    reports = []
    keywords = re.compile(r"reconstruction|recovery|rebuild|housing|shelter|appeal|response|plan", re.I)
    for item in (reliefweb.get("payload") or {}).get("data", []):
        fields = item.get("fields", {})
        created = ((fields.get("date") or {}).get("created") or "")[:10]
        title = fields.get("title") or "Untitled ReliefWeb report"
        sources = fields.get("source") or []
        source_name = "; ".join(source.get("name", "") for source in sources if source.get("name"))
        reports.append({
            "date": created, "month": created[:7] if created else "not_available", "title": title,
            "source_name": source_name or "not_available", "url": fields.get("url") or f"https://reliefweb.int/report/{item.get('id')}",
            "is_timeline_candidate": bool(keywords.search(title)),
        })
    counts = Counter(report["month"] for report in reports if report["month"] != "not_available")
    frequency = [{
        "month": month, "value": count, "unit": "ReliefWeb report count", "source": "ReliefWeb Reports API",
        "processing_method": "Search query filtered to Nepal; monthly counts of returned report creation dates.", "data_quality": "api_search_results",
    } for month, count in sorted(counts.items())]
    timeline = []
    for report in reports:
        if report["is_timeline_candidate"]:
            timeline.append({
                "date": report["date"], "title": report["title"], "source": report["source_name"], "url": report["url"],
                "unit": "documented report event",
                "processing_method": "Keyword-filtered ReliefWeb report title; requires human review before being treated as official policy chronology.",
                "data_quality": "api_search_results_manual_review_required",
            })
    return frequency, timeline[:12]


def manual_required_layers() -> dict:
    method = "Documented source exists, but affected-area raster processing has not yet been run."
    return {
        "ecological_recovery": {"title": "Ecological recovery trend", "status": "manual_required", "source": "NASA LP DAAC MODIS MOD13Q1/MYD13Q1; ESA WorldCover/CCI", "unit": "NDVI, EVI, NBR, LULC class area, LST", "processing_method": method, "data_quality": "manual_required", "points": [], "notes": "Define boundary, download raster products, apply QA masks, compute zonal statistics, then write chart-ready annual series."},
        "night_time_lights": {"title": "Economic recovery proxy trend", "status": "manual_required", "source": "NASA Black Marble or NOAA VIIRS DNB", "unit": "radiance", "processing_method": method, "data_quality": "manual_required", "points": [], "notes": "Night-time lights require raster processing before local recovery proxy values can be shown."},
        "settlement_exposure": {"title": "Population and settlement exposure", "status": "manual_required", "source": "JRC GHSL, WorldPop, affected-area boundary", "unit": "people, built-up area", "processing_method": method, "data_quality": "manual_required", "points": [], "notes": "Exposure metrics require boundary-based gridded population and settlement aggregation."},
    }


def reliefweb_quality(reliefweb: dict | None, has_values: bool) -> str:
    if has_values:
        return "api_search_results"
    if reliefweb and reliefweb.get("data_quality"):
        return reliefweb["data_quality"]
    return "not_available"


def require_provenance(name: str, data: dict | None, fields: set[str]) -> None:
    if not data:
        raise RuntimeError(f"Missing provenance input: {name}")
    missing = fields - set(data.keys())
    if missing:
        raise RuntimeError(f"Malformed provenance input {name}; missing {sorted(missing)}")


def main() -> None:
    PROCESSED.mkdir(parents=True, exist_ok=True)
    usgs = read_json(PROVENANCE / "usgs_event.json")
    reliefweb = read_json(PROVENANCE / "reliefweb_reports.json")
    worldbank = read_json(PROVENANCE / "worldbank_indicators.json")
    require_provenance("usgs_event.json", usgs, {"source", "url", "event_id", "data_quality"})
    require_provenance("reliefweb_reports.json", reliefweb, {"source", "data_quality", "payload"})
    require_provenance("worldbank_indicators.json", worldbank, {"source", "country", "data_quality", "indicators"})

    wb_rows = worldbank_series(worldbank)
    relief_frequency, policy_timeline = reliefweb_outputs(reliefweb)
    relief_quality = reliefweb_quality(reliefweb, bool(relief_frequency))
    policy_quality = "api_search_results_manual_review_required" if policy_timeline else reliefweb_quality(reliefweb, False)
    manual_layers = manual_required_layers()

    write_csv(PROCESSED / "worldbank_context.csv", wb_rows, ["indicator_id", "indicator", "year", "value", "unit", "source", "processing_method", "data_quality"])
    write_csv(PROCESSED / "reliefweb_report_frequency.csv", relief_frequency, ["month", "value", "unit", "source", "processing_method", "data_quality"])

    observatory = {
        "case_id": CASE_ID,
        "case_name": "Nepal 2015 Gorkha Earthquake",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "event_profile": event_profile(usgs),
        "ecological_recovery": manual_layers["ecological_recovery"],
        "economic_recovery_proxy": {
            "night_time_lights": manual_layers["night_time_lights"],
            "worldbank_context": {
                "title": "National economic context", "status": "available_context_only" if wb_rows else "not_available",
                "source": "World Bank WDI API", "unit": "current US$, current US$ per person",
                "processing_method": "Annual national Nepal indicators; not a local recovery proxy.",
                "data_quality": "national_context_only" if wb_rows else "not_available",
                "series": [{"indicator_id": row["indicator_id"], "indicator": row["indicator"], "year": row["year"], "value": row["value"], "unit": row["unit"]} for row in wb_rows if row["indicator_id"] in {"NY.GDP.MKTP.CD", "NY.GDP.PCAP.CD"}],
            },
        },
        "population_settlement": {
            "settlement_exposure": manual_layers["settlement_exposure"],
            "worldbank_population_context": {
                "title": "National population context", "status": "available_context_only" if wb_rows else "not_available",
                "source": "World Bank WDI API", "unit": "people, percent urban",
                "processing_method": "Annual national Nepal indicators; not affected-area exposure.",
                "data_quality": "national_context_only" if wb_rows else "not_available",
                "series": [{"indicator_id": row["indicator_id"], "indicator": row["indicator"], "year": row["year"], "value": row["value"], "unit": row["unit"]} for row in wb_rows if row["indicator_id"] in {"SP.POP.TOTL", "SP.URB.TOTL.IN.ZS"}],
            },
        },
        "social_sensing": {"title": "ReliefWeb report frequency", "status": "available" if relief_frequency else "not_available", "source": "ReliefWeb Reports API", "unit": "monthly report count", "processing_method": "Search query filtered to Nepal; counts of returned report creation dates.", "data_quality": relief_quality, "points": relief_frequency},
        "policy_reconstruction_timeline": {"title": "Response and reconstruction timeline candidates", "status": "manual_review_required" if policy_timeline else "not_available", "source": "ReliefWeb Reports API", "unit": "report item", "processing_method": "Keyword-filtered ReliefWeb titles; human review required for official policy timeline.", "data_quality": policy_quality, "entries": policy_timeline},
    }
    write_json(PROCESSED / "observatory.json", observatory)
    notes = {
        "case_id": CASE_ID,
        "generated_at_utc": observatory["generated_at_utc"],
        "principle": "No fabricated values. Missing or unprocessed indicators are marked manual_required or not_available.",
        "inputs": {"usgs_event": str(PROVENANCE / "usgs_event.json"), "reliefweb_reports": str(PROVENANCE / "reliefweb_reports.json"), "worldbank_indicators": str(PROVENANCE / "worldbank_indicators.json")},
        "outputs": {"observatory": str(PROCESSED / "observatory.json"), "worldbank_context": str(PROCESSED / "worldbank_context.csv"), "reliefweb_report_frequency": str(PROCESSED / "reliefweb_report_frequency.csv")},
    }
    write_json(PROVENANCE / "processing_notes.json", notes)
    print(f"Wrote {PROCESSED / 'observatory.json'}")


if __name__ == "__main__":
    main()
