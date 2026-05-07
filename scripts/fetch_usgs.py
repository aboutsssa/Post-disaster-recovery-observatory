"""Fetch USGS event metadata for the Nepal 2015 Gorkha earthquake."""

from __future__ import annotations

import json
import pathlib
import urllib.request
from datetime import datetime, timezone

EVENT_ID = "us20002926"
OUTPUT = pathlib.Path("public/data/provenance/nepal-gorkha-2015/usgs_event.json")
URL = f"https://earthquake.usgs.gov/fdsnws/event/1/query?format=geojson&eventid={EVENT_ID}"


def fetch_json(url: str) -> dict:
    request = urllib.request.Request(url, headers={"User-Agent": "recovery-observatory/0.1"})
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def main() -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    payload = fetch_json(URL)
    props = payload.get("properties", {})
    geometry = payload.get("geometry", {})
    log = {
        "source": "USGS Earthquake Hazards Program FDSN Event Web Service",
        "url": URL,
        "event_id": EVENT_ID,
        "fetched_at_utc": datetime.now(timezone.utc).isoformat(),
        "data_quality": "api_verified",
        "event": {
            "title": props.get("title"),
            "time": props.get("time"),
            "magnitude": props.get("mag"),
            "magnitude_type": props.get("magType"),
            "place": props.get("place"),
            "source_url": props.get("url"),
            "geometry": geometry,
        },
    }
    OUTPUT.write_text(json.dumps(log, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {OUTPUT}")


if __name__ == "__main__":
    main()
