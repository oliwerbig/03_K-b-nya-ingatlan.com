# -*- coding: utf-8 -*-
"""scripts/fetch_network_layers.py
F2: Overpass-letöltések a kanonikus pufferekkel (data/schema.yaml -> buffers).
- utcahálózat (network_buffer_m = 1250 m)
- vasút + tranzit megállók (rail_buffer_m = 2000 m)
Kőbánya + Bécs Nordbahnhof.
"""
import os
import json
import time
import urllib.request
import urllib.parse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "data", "raw")
UA = "IFK-TDK-2026-Rail-Study/1.0 (research; contact: github.com/oliwerbig)"

AREAS = {
    "kobanya": {
        "prop": (47.443, 19.103, 47.503, 19.178),   # S, W, N, E
        "streets": (47.432, 19.086, 47.514, 19.195),
        "transit": (47.425, 19.076, 47.521, 19.205),
    },
    "wien_nordbahnhof": {
        "prop": (48.194, 16.363, 48.250, 16.449),
        "streets": (48.183, 16.346, 48.261, 16.466),
        "transit": (48.176, 16.336, 48.268, 16.476),
    },
}

STREET_QUERY = """[out:json][timeout:120];
(
  way["highway"~"^(residential|tertiary|secondary|primary|service|living_street|footway|pedestrian|path|steps|cycleway|unclassified|track|platform|primary_link|secondary_link|tertiary_link|bridleway)$"]({bbox});
);
out body geom;
"""

TRANSIT_QUERY = """[out:json][timeout:120];
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

def fetch(name, query, bbox):
    s, w, n, e = bbox
    q = query.replace("{bbox}", f"{s:.4f},{w:.4f},{n:.4f},{e:.4f}")
    url = "https://overpass-api.de/api/interpreter?data=" + urllib.parse.quote(q)
    for attempt in (1, 2, 3):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=150) as res:
                data = json.loads(res.read().decode("utf-8"))
            n_elem = len(data.get("elements", []))
            out = os.path.join(OUT, name)
            with open(out, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False)
            print(f"[OK] {name}: {n_elem} elem", flush=True)
            return out
        except Exception as ex:
            print(f"[RETRY {attempt}] {name}: {ex}", flush=True)
            time.sleep(15 * attempt)
    raise SystemExit(f"[FAIL] {name}")

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for aid, cfg in AREAS.items():
        fetch(f"osm_streets_{aid}_1250m.json", STREET_QUERY, cfg["streets"])
        time.sleep(8)  # Overpass udvariassági szünet
        fetch(f"osm_{aid}_transit_2000m.json", TRANSIT_QUERY, cfg["transit"])
        time.sleep(8)
    print("MINDEN LETÖLTÉS KÉSZ")