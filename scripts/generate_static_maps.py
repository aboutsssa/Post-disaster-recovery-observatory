import json
import math
import os
import urllib.request


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WENCHUAN_DIR = os.path.join(ROOT, "public", "data", "processed", "wenchuan-2008")
WORLD_OUT = os.path.join(ROOT, "src", "data", "worldMapPaths.js")
COUNTY_OUT = os.path.join(WENCHUAN_DIR, "county_spatial_summary.json")
METRIC_PATH = os.path.join(WENCHUAN_DIR, "county_metric_summary.json")


def fetch_json(url):
    req = urllib.request.Request(url, headers={"User-Agent": "recovery-observatory-build/1.0"})
    with urllib.request.urlopen(req, timeout=45) as response:
        return json.loads(response.read().decode("utf-8"))


def rdp(points, epsilon):
    if len(points) <= 2:
        return points
    sx, sy = points[0]
    ex, ey = points[-1]
    dx = ex - sx
    dy = ey - sy
    denom = dx * dx + dy * dy
    max_dist = -1
    split_at = 0
    for index, (x, y) in enumerate(points[1:-1], 1):
        if denom == 0:
            dist = (x - sx) ** 2 + (y - sy) ** 2
        else:
            t = max(0, min(1, ((x - sx) * dx + (y - sy) * dy) / denom))
            px = sx + t * dx
            py = sy + t * dy
            dist = (x - px) ** 2 + (y - py) ** 2
        if dist > max_dist:
            max_dist = dist
            split_at = index
    if max_dist > epsilon * epsilon:
        return rdp(points[: split_at + 1], epsilon)[:-1] + rdp(points[split_at:], epsilon)
    return [points[0], points[-1]]


def write_world_paths():
    url = "https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_110m_admin_0_countries.geojson"
    geojson = fetch_json(url)
    width = 1000
    height = 500

    def project(point):
        lon, lat = point[0], point[1]
        return ((lon + 180.0) / 360.0 * width, (90.0 - lat) / 180.0 * height)

    def fmt(number):
        value = f"{number:.1f}"
        return value.rstrip("0").rstrip(".")

    def ring_path(ring):
        points = [project(point) for point in ring]
        if len(points) > 1 and points[0] == points[-1]:
            points = points[:-1]
        points = rdp(points, 0.9)
        if len(points) < 3:
            return ""
        parts = [f"M{fmt(points[0][0])},{fmt(points[0][1])}"]
        parts.extend(f"L{fmt(x)},{fmt(y)}" for x, y in points[1:])
        parts.append("Z")
        return "".join(parts)

    paths = []
    for feature in geojson.get("features", []):
        geometry = feature.get("geometry")
        if not geometry:
            continue
        if geometry["type"] == "Polygon":
            polygons = [geometry["coordinates"]]
        elif geometry["type"] == "MultiPolygon":
            polygons = geometry["coordinates"]
        else:
            continue
        path = "".join(ring_path(polygon[0]) for polygon in polygons if polygon)
        if path:
            paths.append(path)

    os.makedirs(os.path.dirname(WORLD_OUT), exist_ok=True)
    with open(WORLD_OUT, "w", encoding="utf-8", newline="\n") as handle:
        handle.write("// Generated from Natural Earth 1:110m admin-0 countries.\n")
        handle.write("export const worldMapPaths = ")
        json.dump(paths, handle, separators=(",", ":"))
        handle.write(";\n")


def write_wenchuan_counties():
    with open(METRIC_PATH, encoding="utf-8") as handle:
        metric_summary = json.load(handle)

    columns = metric_summary["columns"]
    metrics_by_name = {row[0]: dict(zip(columns, row[1:])) for row in metric_summary["rows"]}
    aliases = metric_summary.get("aliases", {})

    features = []
    for city_code, city_name in metric_summary["city_codes"]:
        url = f"https://geo.datav.aliyun.com/areas_v3/bound/{city_code}_full.json"
        city_geojson = fetch_json(url)
        for feature in city_geojson.get("features", []):
            properties = feature.get("properties", {})
            source_name = properties.get("name", "")
            panel_name = aliases.get(f"{source_name}|{city_name}") or aliases.get(source_name) or source_name
            if panel_name not in metrics_by_name:
                continue
            properties["parent_city"] = city_name
            properties["panel_name"] = panel_name
            features.append(feature)

    width = 760
    height = 620
    coordinates = []

    def walk_coordinates(obj):
        if obj and isinstance(obj[0], (int, float)):
            coordinates.append(obj[:2])
        else:
            for item in obj:
                walk_coordinates(item)

    for feature in features:
        walk_coordinates(feature["geometry"]["coordinates"])

    min_lon = min(point[0] for point in coordinates)
    max_lon = max(point[0] for point in coordinates)
    min_lat = min(point[1] for point in coordinates)
    max_lat = max(point[1] for point in coordinates)
    pad = 18
    scale = min((width - pad * 2) / (max_lon - min_lon), (height - pad * 2) / (max_lat - min_lat))
    used_width = (max_lon - min_lon) * scale
    used_height = (max_lat - min_lat) * scale
    offset_x = (width - used_width) / 2
    offset_y = (height - used_height) / 2

    def project(point):
        lon, lat = point[0], point[1]
        return (offset_x + (lon - min_lon) * scale, offset_y + (max_lat - lat) * scale)

    def fmt(number):
        return str(int(round(number)))

    def ring_path(ring):
        points = [project(point) for point in ring]
        if len(points) > 1 and points[0] == points[-1]:
            points = points[:-1]
        points = rdp(points, 2.6)
        if len(points) < 3:
            points = [project(point) for point in ring[:-1]][:3]
        return "M" + fmt(points[0][0]) + "," + fmt(points[0][1]) + "".join(
            "L" + fmt(x) + "," + fmt(y) for x, y in points[1:]
        ) + "Z"

    def geometry_path(geometry):
        if geometry["type"] == "Polygon":
            polygons = [geometry["coordinates"]]
        elif geometry["type"] == "MultiPolygon":
            polygons = geometry["coordinates"]
        else:
            return ""
        return "".join(ring_path(polygon[0]) for polygon in polygons if polygon)

    county_features = []
    for feature in features:
        properties = feature["properties"]
        panel_name = properties["panel_name"]
        county_features.append(
            {
                "name": panel_name,
                "source_name": properties.get("name", panel_name),
                "city": properties.get("parent_city", ""),
                "adcode": properties.get("adcode"),
                "path": geometry_path(feature["geometry"]),
                "metrics": metrics_by_name[panel_name],
            }
        )
    county_features.sort(key=lambda item: (item["city"], item["name"]))

    summary = {
        "case_id": "wenchuan-2008",
        "title": "Wenchuan county-level spatial indicators",
        "projection": "Local SVG vector fitted from county boundary coordinates",
        "viewBox": [0, 0, width, height],
        "feature_count": len(county_features),
        "source": "Sichuan county boundary GeoJSON from DataV GeoAtlas; indicators from the Wenchuan county panel dataset.",
        "matching_note": metric_summary["matching_note"],
        "metrics": metric_summary["metrics"],
        "features": county_features,
    }
    with open(COUNTY_OUT, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(summary, handle, ensure_ascii=False, separators=(",", ":"))


def main():
    write_world_paths()
    write_wenchuan_counties()
    print("Generated static vector map assets.")


if __name__ == "__main__":
    main()
