"""Validate processed observatory data and provenance.

This validator is intentionally strict about fabricated placeholders in
processed outputs. It permits `manual_required` and `not_available*` statuses,
but rejects placeholder values such as TBD in chart-ready data.
"""

from __future__ import annotations

import csv
import json
import pathlib
import sys
from typing import Any


CASE_ID = "nepal-gorkha-2015"
ROOT = pathlib.Path(".")
PROCESSED = ROOT / "public" / "data" / "processed" / CASE_ID
PROVENANCE = ROOT / "public" / "data" / "provenance" / CASE_ID
ALLOWED_QUALITY = {
    "api_verified", "api_search_results", "api_search_results_manual_review_required",
    "national_context_only", "manual_required", "manual_review_required",
    "available", "available_context_only", "not_available",
    "not_available_missing_secret", "not_available_api_forbidden", "not_available_api_error",
}
BAD_PLACEHOLDERS = {"TBD", "TODO", "FAKE", "DUMMY", "PLACEHOLDER_VALUE"}


def fail(errors: list[str], message: str) -> None:
    errors.append(message)


def read_json(path: pathlib.Path, errors: list[str]) -> dict[str, Any]:
    if not path.exists():
        fail(errors, f"Missing JSON file: {path}")
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        fail(errors, f"Invalid JSON in {path}: {exc}")
        return {}


def scan_placeholders(path: pathlib.Path, errors: list[str]) -> None:
    if not path.exists():
        return
    text = path.read_text(encoding="utf-8", errors="ignore")
    for marker in BAD_PLACEHOLDERS:
        if marker in text:
            fail(errors, f"Forbidden placeholder marker {marker!r} in {path}")


def require_quality(errors: list[str], context: str, value: str | None) -> None:
    if value not in ALLOWED_QUALITY:
        fail(errors, f"{context} has invalid data_quality/status: {value!r}")


def validate_measure(errors: list[str], name: str, section: dict[str, Any]) -> None:
    for key in ("source", "unit", "processing_method", "data_quality"):
        if not section.get(key):
            fail(errors, f"{name} missing {key}")
    require_quality(errors, name, section.get("data_quality"))


def validate_series(errors: list[str], name: str, section: dict[str, Any], series_key: str) -> None:
    validate_measure(errors, name, section)
    status = section.get("status")
    if status:
        require_quality(errors, f"{name}.status", status)
    rows = section.get(series_key, [])
    if status in {"manual_required", "not_available", "not_available_missing_secret", "not_available_api_forbidden"} and rows:
        fail(errors, f"{name} has status {status!r} but contains values")
    for index, row in enumerate(rows):
        if row.get("value") is None:
            fail(errors, f"{name}[{index}] missing value")
        if not row.get("unit"):
            fail(errors, f"{name}[{index}] missing unit")


def validate_observatory(errors: list[str]) -> None:
    data = read_json(PROCESSED / "observatory.json", errors)
    if not data:
        return
    if data.get("case_id") != CASE_ID:
        fail(errors, "observatory.json case_id mismatch")
    event = data.get("event_profile", {})
    validate_measure(errors, "event_profile", event)
    for key in ("magnitude", "depth_km", "longitude", "latitude"):
        if event.get(key) is None:
            fail(errors, f"event_profile missing {key}")
    validate_series(errors, "ecological_recovery", data.get("ecological_recovery", {}), "points")
    econ = data.get("economic_recovery_proxy", {})
    validate_series(errors, "night_time_lights", econ.get("night_time_lights", {}), "points")
    validate_series(errors, "worldbank_context", econ.get("worldbank_context", {}), "series")
    pop = data.get("population_settlement", {})
    validate_series(errors, "settlement_exposure", pop.get("settlement_exposure", {}), "points")
    validate_series(errors, "worldbank_population_context", pop.get("worldbank_population_context", {}), "series")
    validate_series(errors, "social_sensing", data.get("social_sensing", {}), "points")
    timeline = data.get("policy_reconstruction_timeline", {})
    validate_measure(errors, "policy_reconstruction_timeline", timeline)
    require_quality(errors, "policy_reconstruction_timeline.status", timeline.get("status"))


def validate_csv(errors: list[str], path: pathlib.Path, required_fields: set[str]) -> None:
    if not path.exists():
        fail(errors, f"Missing CSV file: {path}")
        return
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        fields = set(reader.fieldnames or [])
        missing = required_fields - fields
        if missing:
            fail(errors, f"{path} missing fields: {sorted(missing)}")
        for index, row in enumerate(reader):
            if "data_quality" in row:
                require_quality(errors, f"{path} row {index}", row.get("data_quality"))
            if "value" in row and row.get("value") in BAD_PLACEHOLDERS:
                fail(errors, f"{path} row {index} contains placeholder value")


def validate_provenance(errors: list[str]) -> None:
    required = {
        "usgs_event.json": {"source", "url", "event_id", "fetched_at_utc", "data_quality", "event"},
        "reliefweb_reports.json": {"source", "query", "country_iso3", "fetched_at_utc", "data_quality", "payload"},
        "worldbank_indicators.json": {"source", "country", "fetched_at_utc", "data_quality", "indicators"},
        "processing_notes.json": {"case_id", "generated_at_utc", "principle", "inputs", "outputs"},
    }
    for filename, fields in required.items():
        data = read_json(PROVENANCE / filename, errors)
        missing = fields - set(data.keys())
        if missing:
            fail(errors, f"{filename} missing provenance fields: {sorted(missing)}")
        if data.get("data_quality"):
            require_quality(errors, filename, data.get("data_quality"))
        if filename == "reliefweb_reports.json":
            quality = data.get("data_quality")
            if quality == "api_search_results" and not data.get("url"):
                fail(errors, "ReliefWeb success provenance must include request URL")
            if str(quality).startswith("not_available") and not data.get("error"):
                fail(errors, "ReliefWeb unavailable provenance must include error details")


def main() -> int:
    errors: list[str] = []
    for path in [PROCESSED / "observatory.json", PROCESSED / "worldbank_context.csv", PROCESSED / "reliefweb_report_frequency.csv"]:
        scan_placeholders(path, errors)
    validate_observatory(errors)
    validate_csv(errors, PROCESSED / "worldbank_context.csv", {"indicator_id", "indicator", "year", "value", "unit", "source", "processing_method", "data_quality"})
    validate_csv(errors, PROCESSED / "reliefweb_report_frequency.csv", {"month", "value", "unit", "source", "processing_method", "data_quality"})
    validate_provenance(errors)
    if errors:
        print("Data validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print("Data validation passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
