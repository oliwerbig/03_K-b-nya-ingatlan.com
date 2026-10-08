# -*- coding: utf-8 -*-
"""scripts/fetch_osm_layers.py — OSM/POI rétegek letöltése, KONFIG-VEZÉRELTEN.

Minden terület-azonosító, középpont és puffer az data/areas.yaml-ből jön
(a kódban SEMMILYEN területnév nincs). A puffer MINDIG legalább 2000 m
(areas.yaml buffers + biztonsági margin), a kimeneti utak az areas.yaml
data.street_file / data.transit_file / data.poi_file mezői.
"""
import json
import math
import os
import time
import urllib.parse
import urllib.request

import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UA = "IFK-TDK-2026-Rail-Study/1.0 (research; contact: github.com/oliwerbig)"
MIN_BUFFER_M = 2000.0  # a kutatási szabály: MINDEN OSM/POI letöltés >= 2000 m
MARGIN_M = 200.0

STREET_QUERY = """[out:json][timeout:180];
(
  way["highway"~"^(residential|tertiary|secondary|primary|service|living_street|footway|pedestrian|path|steps|cycleway|unclassified|track|platform|primary_link|secondary_link|tertiary_link|bridleway)$"]({bbox});
);
out body geom;
"""

TRANSIT_QUERY = """[out:json][timeout:180];
(
  way["railway"~"^(rail|light_rail)$"]({bbox});
  node["railway"~"^(station|halt|tram_stop)$"]({bbox});
  way["railway"~"^(station|halt)$"]({bbox});
  node["station"="subway"]({bbox});
  node["railway"="subway_entrance"]({bbox});
  node["highway"="bus_stop"]({bbox});
  node["public_transport"="stop_position"]({bbox});
);
out body geom;
"""

POI_QUERY = """[out:json][timeout:180];
(
  node["amenity"~"^(school|kindergarten|pharmacy|doctors|clinic)$"]({bbox});
  node["shop"~"^(supermarket|convenience|bakery)$"]({bbox});
  node["leisure"~"^(park|garden|playground)$"]({bbox});
  way["leisure"~"^(park|garden)$"]({bbox});
  node["railway"~"^(station|halt)$"]({bbox});
  node["station"="subway"]({bbox});
);
out center;
"""


def bbox_for(center_lat, center_lon, buffer_m):
    """Középpont + puffer -> (S, W, N, E) fok-bbox (Web-Mercator közelítés a lokális skálán)."""
    buf = max(MIN_BUFFER_M, buffer_m) + MARGIN_M
    dlat = buf / 110540.0
    dlon = buf / (111320.0 * math.cos(math.radians(center_lat)))
    return (center_lat - dlat, center_lon - dlon, center_lat + dlat, center_lon + dlon)


ENDPOINTS = [
    "https://overpass-api.de/api/interpreter",
    "https://lz4.overpass-api.de/api/interpreter",
    "https://z.overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
]


def fetch(query, bbox, out_path, kind):
    s, w, n, e = bbox
    q = query.replace("{bbox}", f"{s:.4f},{w:.4f},{n:.4f},{e:.4f}")
    for attempt in range(1, 6):
        ep = ENDPOINTS[(attempt - 1) % len(ENDPOINTS)]
        url = ep + "?data=" + urllib.parse.quote(q)
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=240) as res:
                data = json.loads(res.read().decode("utf-8"))
            os.makedirs(os.path.dirname(out_path), exist_ok=True)
            with open(out_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False)
            print(f"[OK] {kind} -> {os.path.relpath(out_path, ROOT)}: {len(data.get('elements', []))} elem", flush=True)
            return
        except Exception as ex:
            print(f"[RETRY {attempt}] {kind} ({ep.split('/')[2]}): {ex}", flush=True)
            time.sleep(20 * attempt)
    raise SystemExit(f"[FAIL] {kind}")


def main():
    with open(os.path.join(ROOT, "data", "areas.yaml"), encoding="utf-8") as f:
        areas = yaml.safe_load(f)
    buffers = areas.get("buffers", {})
    for aid, cfg in (areas.get("areas") or {}).items():
        spatial = cfg.get("spatial", {})
        clat = float(spatial["center_lat"])
        clon = float(spatial["center_lon"])
        data = cfg["data"]
        print(f"=== {aid} (középpont {clat}, {clon}) ===")
        # 1) utcahálózat
        fetch(STREET_QUERY, bbox_for(clat, clon, buffers.get("network_buffer_m", MIN_BUFFER_M)),
              os.path.join(ROOT, data["street_file"]), "utcahálózat")
        time.sleep(8)
        # 2) vasút + tranzit
        fetch(TRANSIT_QUERY, bbox_for(clat, clon, buffers.get("rail_buffer_m", MIN_BUFFER_M)),
              os.path.join(ROOT, data["transit_file"]), "vasút+tranzit")
        time.sleep(8)
        # 3) POI-k
        fetch(POI_QUERY, bbox_for(clat, clon, buffers.get("poi_buffer_m", MIN_BUFFER_M)),
              os.path.join(ROOT, data["poi_file"]), "POI")
        time.sleep(8)
    print("MINDEN OSM/POI RÉTEG LETÖLTVE")


if __name__ == "__main__":
    main()