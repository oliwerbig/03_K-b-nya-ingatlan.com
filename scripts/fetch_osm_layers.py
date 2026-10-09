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


def listing_extent_bbox(area_cfg, buffer_m=2000.0):
    """A HIRDETÉSEK tényleges koordináta-kiterjedéséből számolt bbox + puffer.

    A hirdetések (főleg a kerületszéli címek) túlnyúlhatnak a fix középpont körüli
    bboxon — akkor az úthálózat hiányos lenne és a hálózati távolságok kimaradnának.
    Ezért a letöltési bbox a geokódolt címek szélső értékeiből + legalább 2000 m pufferből
    számolódik."""
    import pandas as _pd
    rel = area_cfg.get("data", {}).get("extracted_xlsx")
    lat0 = lon0 = lat1 = lon1 = None
    if rel:
        xp = os.path.join(ROOT, rel)
        if os.path.exists(xp):
            try:
                d = _pd.read_excel(xp)
                if {"lat_jsonld", "lon_jsonld"}.issubset(d.columns):
                    d = d.dropna(subset=["lat_jsonld", "lon_jsonld"])
                g = _pd.read_csv(os.path.join(ROOT, "data", "geocoding",
                                              area_cfg["id"] + "_geocode_eredmeny.csv"),
                                 dtype={"listing_id": str})
                g = g.dropna(subset=["geokodolt_lat", "geokodolt_lon"])
                # a geokódolási outlierek (rossz országba ugró találatok) kizárása:
                # csak a terület-középpont 30 km-es környezetében lévő pontok számítanak
                clat = float((area_cfg.get("spatial") or {}).get("center_lat", 48.0))
                clon = float((area_cfg.get("spatial") or {}).get("center_lon", 16.0))
                g = g[(g["geokodolt_lat"] - clat).abs() < 0.30]
                g = g[(g["geokodolt_lon"] - clon).abs() < 0.40]
                if len(g) >= 5:
                    lat0, lat1 = float(g["geokodolt_lat"].quantile(0.02)), float(g["geokodolt_lat"].quantile(0.98))
                    lon0, lon1 = float(g["geokodolt_lon"].quantile(0.02)), float(g["geokodolt_lon"].quantile(0.98))
            except Exception:
                pass
    spatial = area_cfg.get("spatial", {})
    if lat0 is None:
        clat, clon = float(spatial["center_lat"]), float(spatial["center_lon"])
        return bbox_for(clat, clon, buffer_m)
    buf = max(MIN_BUFFER_M, buffer_m) + MARGIN_M
    dlat = buf / 110540.0
    dlon_mid = buf / (111320.0 * math.cos(math.radians((lat0 + lat1) / 2)))
    return (lat0 - dlat, lon0 - dlon_mid, lat1 + dlat, lon1 + dlon_mid)


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


POI_CAT_MAP = [
    ("amenity", "school", "iskola"), ("amenity", "kindergarten", "ovoda"),
    ("shop", "supermarket", "elelmiszer_bolt"), ("shop", "convenience", "elelmiszer_bolt"),
    ("shop", "bakery", "elelmiszer_bolt"),
    ("amenity", "pharmacy", "gyogyszertar"),
    ("amenity", "doctors", "orvos_egeszsegugy"), ("amenity", "clinic", "orvos_egeszsegugy"),
    ("leisure", "park", "park_zoldterulet"), ("leisure", "garden", "park_zoldterulet"),
    ("leisure", "playground", "park_zoldterulet"),
    ("railway", "station", "vasutallomas"), ("railway", "halt", "vasutallomas"),
    ("station", "subway", "metroallomas"),
]


def pois_to_geojson(data):
    """Overpass-elemek -> GeoJSON (a network_metrics elvárt category/name sémája)."""
    feats = []
    for e in data.get("elements", []):
        tags = e.get("tags") or {}
        cat = None
        for key, val, c in POI_CAT_MAP:
            if tags.get(key) == val:
                cat = c
                break
        if cat is None:
            continue
        if e.get("type") == "node":
            lat, lon = e.get("lat"), e.get("lon")
        else:
            ctr = e.get("center") or {}
            lat, lon = ctr.get("lat"), ctr.get("lon")
        if lat is None or lon is None:
            continue
        feats.append({"type": "Feature",
                      "geometry": {"type": "Point", "coordinates": [lon, lat]},
                      "properties": {"category": cat, "name": tags.get("name", "")}})
    return {"type": "FeatureCollection", "features": feats}


def main():
    with open(os.path.join(ROOT, "data", "areas.yaml"), encoding="utf-8") as f:
        areas = yaml.safe_load(f)
    buffers = areas.get("buffers", {})
    for aid, cfg in (areas.get("areas") or {}).items():
        spatial = cfg.get("spatial", {})
        data = cfg["data"]
        _bbox = listing_extent_bbox(cfg, buffers.get("network_buffer_m", MIN_BUFFER_M))
        print(f"=== {aid} (hirdetés-kiterjedés + {MIN_BUFFER_M} m puffer: "
              f"{_bbox[0]:.4f}, {_bbox[1]:.4f} .. {_bbox[2]:.4f}, {_bbox[3]:.4f}) ===")
        # 1) utcahálózat
        fetch(STREET_QUERY, _bbox,
              os.path.join(ROOT, data["street_file"]), "utcahálózat")
        time.sleep(8)
        # 2) vasút + tranzit
        fetch(TRANSIT_QUERY, _bbox,
              os.path.join(ROOT, data["transit_file"]), "vasút+tranzit")
        time.sleep(8)
        # 3) POI-k (GeoJSON-lá konvertálva)
        _poi_path = os.path.join(ROOT, data["poi_file"])
        _s, _w, _n, _e = _bbox
        _q = POI_QUERY.replace("{bbox}", f"{_s:.4f},{_w:.4f},{_n:.4f},{_e:.4f}")
        _raw = None
        for _attempt in range(1, 6):
            _ep = ENDPOINTS[(_attempt - 1) % len(ENDPOINTS)]
            try:
                _req = urllib.request.Request(_ep + "?data=" + urllib.parse.quote(_q), headers={"User-Agent": UA})
                with urllib.request.urlopen(_req, timeout=240) as _res:
                    _raw = json.loads(_res.read().decode("utf-8"))
                break
            except Exception as _ex:
                print(f"[RETRY {_attempt}] POI: {_ex}", flush=True)
                time.sleep(20 * _attempt)
        if _raw is None:
            raise SystemExit("[FAIL] POI")
        os.makedirs(os.path.dirname(_poi_path), exist_ok=True)
        _gj = pois_to_geojson(_raw)
        with open(_poi_path, "w", encoding="utf-8") as _f:
            json.dump(_gj, _f, ensure_ascii=False)
        print(f"[OK] POI -> {os.path.relpath(_poi_path, ROOT)}: {len(_gj['features'])} pont", flush=True)
        time.sleep(8)
    print("MINDEN OSM/POI RÉTEG LETÖLTVE")


if __name__ == "__main__":
    main()