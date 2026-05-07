"""Fetch ReliefWeb report search results for Nepal earthquake recovery.

The output is a provenance log, not a definitive event chronology. Report
frequency and candidate timeline entries are derived in process_all.py.
"""

from __future__ import annotations

import json
import os
import pathlib
import urllib.parse
import urllib.request
import urllib.error
from datetime import datetime, timezone


OUTPUT = pathlib.Path("public/data/provenance/nepal-gorkha-2015/reliefweb_reports.json")
BASE_URL = "https://api.reliefweb.int/v2/reports"


def get_appname() -> str | None:
    value = os.environ.get("RELIEFWEB_APPNAME", "").strip()
    return value or None


def build_url(appname: str, limit: int = 100) -> str:
    params = {
        "appname": appname,
        "profile": "list",
        "limit": str(limit),
        "query[value]": "Nepal earthquake reconstruction recovery housing",
        "filter[field]": "country.iso3",
        "filter[value]": "NPL",
        "sort[]": "date.created:asc",
        "fields[include][]": [
            "id",
            "title",
            "date.created",
            "source.name",
            "url",
            "primary_country.name",
        ],
    }
    return f"{BASE_URL}?{urllib.parse.urlencode(params, doseq=True)}"


def fetch_json(url: str) -> dict:
    request = urllib.request.Request(url, headers={"User-Agent": "recovery-observatory/0.1"})
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def main() -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    appname = get_appname()
    data_quality = "api_search_results"
    error = None
    if not appname:
        url = None
        payload = {"data": []}
        data_quality = "not_available_missing_secret"
        error = {
            "type": "MissingEnvironmentVariable",
            "name": "RELIEFWEB_APPNAME",
            "note": "ReliefWeb API v2 requires a pre-approved appname. Add RELIEFWEB_APPNAME as a GitHub Actions secret to fetch reports.",
        }
    else:
        url = build_url(appname)
        try:
            payload = fetch_json(url)
        except urllib.error.HTTPError as exc:
            payload = {"data": []}
            data_quality = "not_available_api_forbidden" if exc.code == 403 else "not_available_api_error"
            error = {
                "type": "HTTPError",
                "status_code": exc.code,
                "reason": exc.reason,
                "note": "ReliefWeb API v2 requires a pre-approved appname; no values were fabricated.",
            }
    log = {
        "source": "ReliefWeb Reports API",
        "url": url,
        "appname_source": "RELIEFWEB_APPNAME" if appname else "missing",
        "query": "Nepal earthquake reconstruction recovery housing",
        "country_iso3": "NPL",
        "fetched_at_utc": datetime.now(timezone.utc).isoformat(),
        "data_quality": data_quality,
        "error": error,
        "payload": payload,
    }
    OUTPUT.write_text(json.dumps(log, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {OUTPUT}")


if __name__ == "__main__":
    main()
