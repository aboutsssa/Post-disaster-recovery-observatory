"""Fetch World Bank national socioeconomic context for Nepal."""

from __future__ import annotations

import json
import pathlib
import urllib.request
from datetime import datetime, timezone

COUNTRY = "NPL"
START_YEAR = 2010
END_YEAR = 2023
INDICATORS = {
    "NY.GDP.MKTP.CD": "GDP, current US$",
    "NY.GDP.PCAP.CD": "GDP per capita, current US$",
    "SP.POP.TOTL": "Population, total",
    "SP.URB.TOTL.IN.ZS": "Urban population (% of total population)",
}
OUTPUT = pathlib.Path("public/data/provenance/nepal-gorkha-2015/worldbank_indicators.json")


def fetch_json(url: str):
    request = urllib.request.Request(url, headers={"User-Agent": "recovery-observatory/0.1"})
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def main() -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    results = {}
    for indicator_id, label in INDICATORS.items():
        url = (
            f"https://api.worldbank.org/v2/country/{COUNTRY}/indicator/{indicator_id}"
            f"?format=json&date={START_YEAR}:{END_YEAR}&per_page=100"
        )
        payload = fetch_json(url)
        observations = payload[1] if isinstance(payload, list) and len(payload) > 1 else []
        results[indicator_id] = {
            "label": label,
            "url": url,
            "data": [
                {
                    "year": item.get("date"),
                    "value": item.get("value"),
                    "country": (item.get("country") or {}).get("value"),
                    "indicator": (item.get("indicator") or {}).get("value"),
                }
                for item in observations or []
            ],
        }

    log = {
        "source": "World Bank World Development Indicators API",
        "country": COUNTRY,
        "fetched_at_utc": datetime.now(timezone.utc).isoformat(),
        "data_quality": "national_context_only",
        "indicators": results,
    }
    OUTPUT.write_text(json.dumps(log, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {OUTPUT}")


if __name__ == "__main__":
    main()
