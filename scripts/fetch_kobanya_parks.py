import urllib.request
import urllib.parse
import json
import geopandas as gpd
from shapely.geometry import Point
import pandas as pd

bbox = "47.440,19.090,47.510,19.190"
query = f"""[out:json][timeout:45];
(
  way["leisure"="park"]({bbox});
  node["leisure"="park"]({bbox});
);
out center;
"""

endpoints = [
    "https://overpass.kumi.systems/api/interpreter",
    "https://z.overpass-api.de/api/interpreter",
    "https://lz4.overpass-api.de/api/interpreter",
    "https://overpass-api.de/api/interpreter"
]

data = None
for ep in endpoints:
    url = ep + "?data=" + urllib.parse.quote(query)
    req = urllib.request.Request(url, headers={"User-Agent": "TDK-Kobanya-Parks/1.0"})
    try:
        print(f"Próbálkozás: {ep}...")
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            if data and "elements" in data:
                print(f"Sikeres válasz innen: {ep}!")
                break
    except Exception as e:
        print(f"Hiba innen ({ep}):", e)

if data and "elements" in data:
    elements = data.get("elements", [])
    print(f"Lekért parkok száma: {len(elements)} db.")

    # Meglévő POI fájl betöltése
    existing_gdf = gpd.read_file("data/poi_kobanya_buffered.geojson")
    # Eltávolítjuk a régi egyetlen hibás parkot ha volt
    existing_gdf = existing_gdf[existing_gdf['category'] != 'park_zoldterulet']

    new_features = []
    for el in elements:
        tags = el.get("tags", {})
        name = tags.get("name", "Névtelen zöldfelület / park")
        if "center" in el:
            lat = el["center"]["lat"]
            lon = el["center"]["lon"]
        elif "lat" in el:
            lat = el["lat"]
            lon = el["lon"]
        else:
            continue

        new_features.append({
            "geometry": Point(lon, lat),
            "name": name,
            "category": "park_zoldterulet",
            "amenity_type": "leisure:park"
        })

    parks_gdf = gpd.GeoDataFrame(new_features, crs="EPSG:4326")
    combined_gdf = gpd.GeoDataFrame(pd.concat([existing_gdf, parks_gdf], ignore_index=True), crs="EPSG:4326")
    combined_gdf.to_file("data/poi_kobanya_buffered.geojson", driver="GeoJSON")
    print(f"Sikeres mentés! Összesített Kőbánya POI-k száma: {len(combined_gdf)} db.")
    print(combined_gdf['category'].value_counts())
else:
    print("Nem sikerült lekérni a park adatokat.")
