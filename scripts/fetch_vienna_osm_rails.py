# -*- coding: utf-8 -*-
"""scripts/fetch_vienna_osm_rails.py
Overpass API lekérdező Bécs 2. kerület (Leopoldstadt / Nordbahnhof) és környezete vasúti hálózatához.
"""
import os
import json
import urllib.request
import urllib.parse

def fetch_vienna_rails():
    # Bbox: Leopoldstadt és vonzáskörzete (Praterstern, Traisengasse, Nordbahnhof)
    # lat: 48.19 -> 48.26, lon: 16.36 -> 16.45
    query = """[out:json][timeout:45];
(
  way["railway"="rail"](48.19,16.36,48.26,16.45);
  node["railway"="station"](48.19,16.36,48.26,16.45);
  node["railway"="halt"](48.19,16.36,48.26,16.45);
  way["railway"="station"](48.19,16.36,48.26,16.45);
);
out body geom;
"""
    url = "https://overpass-api.de/api/interpreter?data=" + urllib.parse.quote(query)
    req = urllib.request.Request(url, headers={"User-Agent": "IFK-TDK-2026-Vienna-Study/1.0"})
    print("OSM vasúti adatok letöltése Overpass API-ból (Bécs, Leopoldstadt / Nordbahnhof)...")
    with urllib.request.urlopen(req, timeout=35) as res:
        data = json.loads(res.read().decode("utf-8"))
    
    elements = data.get("elements", [])
    print(f"Sikeres letöltés! {len(elements)} db elem érkezett.")
    
    out_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "raw")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "osm_rails_wien_nordbahnhof.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Elmentve ide: {out_path}")
    return out_path

if __name__ == "__main__":
    fetch_vienna_rails()
