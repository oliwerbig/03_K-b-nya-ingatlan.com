# -*- coding: utf-8 -*-
"""scripts/fetch_buffered_pois.py
Overpass API lekérdező a mintaterületek és környezetük (pufferelt) POI infrastruktúrájához.
A lekérdezés jelentős térbeli puffert használ (kb. 1500 m ráhagyás a határokra), hogy megakadályozza a térbeli
határhibát (edge effect) a 15 perces város és hálózati elérhetőségi számításoknál.
"""

import os
import json
import urllib.request
import urllib.parse
import geopandas as gpd
from shapely.geometry import Point
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("POI_Fetcher")

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(PROJECT_ROOT, "data")

AREA_BBOXES = {
    "wien_nordbahnhof": {
        # Leopoldstadt / Nordbahnhof és szomszédos kerületek (Innere Stadt, Brigittenau, stb.)
        "min_lat": 48.200,
        "min_lon": 16.360,
        "max_lat": 48.242,
        "max_lon": 16.445
    },
    "kobanya": {
        # Kőbánya és közvetlen szomszédsága (Zugló, Józsefváros, Ferencváros szélek)
        "min_lat": 47.440,
        "min_lon": 19.090,
        "max_lat": 47.510,
        "max_lon": 19.190
    }
}

ENDPOINTS = [
    "https://overpass-api.de/api/interpreter",
    "https://lz4.overpass-api.de/api/interpreter",
    "https://z.overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter"
]


def build_overpass_query(bbox: dict) -> str:
    lat_min, lon_min = bbox["min_lat"], bbox["min_lon"]
    lat_max, lon_max = bbox["max_lat"], bbox["max_lon"]
    bbox_str = f"{lat_min},{lon_min},{lat_max},{lon_max}"

    query = f"""[out:json][timeout:60];
(
  node["amenity"~"school|kindergarten|pharmacy|doctors|clinic"]({bbox_str});
  node["shop"~"supermarket|convenience|bakery"]({bbox_str});
  node["leisure"~"park|garden|playground"]({bbox_str});
  way["leisure"~"park|garden"]({bbox_str});
  node["railway"~"station|halt"]({bbox_str});
  node["station"="subway"]({bbox_str});
);
out center;
"""
    return query


def fetch_and_save_pois(area_id: str, force_download: bool = False) -> str:
    if area_id not in AREA_BBOXES:
        raise ValueError(f"Ismeretlen terület: {area_id}. Elérhető: {list(AREA_BBOXES.keys())}")

    out_path = os.path.join(DATA_DIR, f"poi_{area_id}_buffered.geojson")
    if os.path.exists(out_path) and not force_download:
        logger.info(f"Pufferelt POI fájl már létezik: {out_path}")
        return out_path

    bbox = AREA_BBOXES[area_id]
    query = build_overpass_query(bbox)
    data = None

    for ep in ENDPOINTS:
        url = ep + "?data=" + urllib.parse.quote(query)
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "IFK-TDK-2026-Vienna-Study/1.0"}
        )
        try:
            logger.info(f"[{area_id}] Lekérdezés megkísérlése a(z) {ep} szerverről...")
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            if data and "elements" in data:
                logger.info(f"[{area_id}] Sikeres lekérdezés a(z) {ep} szerverről!")
                break
        except Exception as e:
            logger.warning(f"[{area_id}] Hiba a(z) {ep} elérésekor: {e}")

    if not data or "elements" not in data:
        raise RuntimeError(f"Nem sikerült lekérni a POI-kat a megadott végpontokról a(z) '{area_id}' területhez.")

    elements = data.get("elements", [])
    logger.info(f"[{area_id}] Nyers letöltött POI elemek száma: {len(elements)} db.")

    # GeoJSON formátumba transzformálás
    features = []
    for el in elements:
        lat = el.get("lat") or (el.get("center", {}).get("lat") if "center" in el else None)
        lon = el.get("lon") or (el.get("center", {}).get("lon") if "center" in el else None)
        if lat is None or lon is None:
            continue

        tags = el.get("tags", {})
        amenity = tags.get("amenity", "")
        shop = tags.get("shop", "")
        leisure = tags.get("leisure", "")
        railway = tags.get("railway", "")
        station = tags.get("station", "")

        # Fő kategória meghatározása
        category = "egyeb"
        if amenity == "school":
            category = "iskola"
        elif amenity == "kindergarten":
            category = "ovoda"
        elif amenity == "pharmacy":
            category = "gyogyszertar"
        elif amenity in ["doctors", "clinic", "hospital"]:
            category = "orvos_egeszsegugy"
        elif shop in ["supermarket", "convenience", "bakery"]:
            category = "elelmiszer_bolt"
        elif leisure in ["park", "playground"]:
            category = "park_zoldterulet"
        elif station == "subway" or (railway == "station" and "u-bahn" in tags.get("name", "").lower()):
            category = "metroallomas"
        elif railway in ["station", "halt"]:
            category = "vasutallomas"
        elif railway == "tram_stop":
            category = "villamosmegallo"

        name = tags.get("name") or tags.get("brand") or category.capitalize()

        features.append({
            "type": "Feature",
            "geometry": Point(lon, lat),
            "properties": {
                "id": el.get("id"),
                "osm_type": el.get("type"),
                "category": category,
                "name": name,
                "amenity": amenity,
                "shop": shop,
                "leisure": leisure,
                "railway": railway
            }
        })

    gdf = gpd.GeoDataFrame.from_features(features, crs="EPSG:4326")
    logger.info(f"[{area_id}] Kategóriák megoszlása ({len(gdf)} db POI):")
    for cat, count in gdf["category"].value_counts().items():
        logger.info(f"   - {cat}: {count} db")

    gdf.to_file(out_path, driver="GeoJSON")
    logger.info(f"[{area_id}] Pufferelt POI adatbázis sikeresen elmentve: {out_path}")
    return out_path


if __name__ == "__main__":
    import sys
    target = sys.argv[1] if len(sys.argv) > 1 else "all"
    if target == "all":
        for a in AREA_BBOXES:
            fetch_and_save_pois(a, force_download=True)
    else:
        fetch_and_save_pois(target, force_download=True)
