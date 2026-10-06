# -*- coding: utf-8 -*-
"""scripts/enrich_poi_distances.py
Számítja a 15 perces város kulcsfontosságú intézményeinek (iskola, óvoda, bolt, gyógyszertár,
orvos, park, metró, vasútállomás) hálózati sétaútját és elérhetőségi mutatóit a pufferelt
POI adatbázisok alapján.
"""

import os
import pandas as pd
import geopandas as gpd
import numpy as np
from scipy.spatial import cKDTree
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("POI_Enricher")

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
PROCESSED_DIR = os.path.join(DATA_DIR, "processed")

DETOUR_FACTOR = 1.30  # Manhattan / városi úthálózati kerülő szorzó
WALK_SPEED_M_PER_MIN = 75.0  # 4.5 km/h átlagos gyalogos sebesség


def enrich_area_poi(area_id: str):
    master_path = os.path.join(PROCESSED_DIR, f"{area_id}_szamitott_master.parquet")
    if not os.path.exists(master_path):
        cand = os.path.join(PROCESSED_DIR, f"{area_id}_ingatlan_szamitott_master.parquet")
        if os.path.exists(cand):
            master_path = cand
        else:
            logger.error(f"Master parquet nem található: {master_path}")
            return

    poi_path = os.path.join(DATA_DIR, f"poi_{area_id}_buffered.geojson")
    if not os.path.exists(poi_path):
        logger.error(f"Pufferelt POI GeoJSON nem található: {poi_path}")
        return

    logger.info(f"[{area_id}] Adatok betöltése: {master_path} és {poi_path}...")
    df = pd.read_parquet(master_path)
    poi_gdf = gpd.read_file(poi_path)

    # Valid koordinátával rendelkező ingatlanok
    valid_mask = df['geokodolt_lat'].notna() & df['geokodolt_lon'].notna()
    if not valid_mask.any():
        logger.warning(f"[{area_id}] Nincsenek geokódolt koordináták!")
        return

    # Metrikus vetület kiválasztása (EPSG:3857 vagy lokális)
    metric_crs = "EPSG:3857"
    poi_proj = poi_gdf.to_crs(metric_crs)

    prop_gdf = gpd.GeoDataFrame(
        geometry=gpd.points_from_xy(df.loc[valid_mask, 'geokodolt_lon'], df.loc[valid_mask, 'geokodolt_lat']),
        crs="EPSG:4326"
    ).to_crs(metric_crs)

    prop_coords = np.column_stack((prop_gdf.geometry.x, prop_gdf.geometry.y))

    # Kategóriák és oszlopnevek hozzárendelése
    poi_categories = {
        'iskola': 'tavolsag_iskola_halozati_m',
        'ovoda': 'tavolsag_ovoda_halozati_m',
        'elelmiszer_bolt': 'tavolsag_bolt_halozati_m',
        'gyogyszertar': 'tavolsag_gyogyszertar_halozati_m',
        'orvos_egeszsegugy': 'tavolsag_orvos_halozati_m',
        'park_zoldterulet': 'tavolsag_park_halozati_m',
        'metroallomas': 'tavolsag_metro_halozati_m',
        'vasutallomas': 'tavolsag_vasut_halozati_m'
    }

    # Ha a GeoJSON-ban nincs category mező, próbáljuk kinyerni amenity/shop/leisure alapján
    if 'category' not in poi_proj.columns:
        poi_proj['category'] = 'egyeb'
        if 'amenity' in poi_proj.columns:
            poi_proj.loc[poi_proj['amenity'] == 'school', 'category'] = 'iskola'
            poi_proj.loc[poi_proj['amenity'] == 'kindergarten', 'category'] = 'ovoda'
            poi_proj.loc[poi_proj['amenity'] == 'pharmacy', 'category'] = 'gyogyszertar'
            poi_proj.loc[poi_proj['amenity'].isin(['doctors', 'clinic', 'hospital']), 'category'] = 'orvos_egeszsegugy'
        if 'shop' in poi_proj.columns:
            poi_proj.loc[poi_proj['shop'].isin(['supermarket', 'convenience', 'bakery']), 'category'] = 'elelmiszer_bolt'
        if 'leisure' in poi_proj.columns:
            poi_proj.loc[poi_proj['leisure'].isin(['park', 'playground']), 'category'] = 'park_zoldterulet'

    valid_indices = df.loc[valid_mask].index

    for cat, col_name in poi_categories.items():
        cat_sub = poi_proj[poi_proj['category'] == cat]
        if len(cat_sub) == 0:
            logger.info(f"   [{area_id}] Nincs '{cat}' a POI adatokban, átugorva.")
            continue

        cat_centroids = cat_sub.geometry.centroid
        cat_coords = np.column_stack((cat_centroids.x, cat_centroids.y))
        tree = cKDTree(cat_coords)
        dists, _ = tree.query(prop_coords, k=1)
        net_dists = np.round(dists * DETOUR_FACTOR, 1)

        df.loc[valid_indices, col_name] = net_dists
        # 10 és 15 perces dummyk
        base_cat = col_name.replace('tavolsag_', '').replace('_halozati_m', '')
        df.loc[valid_indices, f"{base_cat}_10p_seta"] = (net_dists <= 750.0).astype(int)
        df.loc[valid_indices, f"{base_cat}_15p_seta"] = (net_dists <= 1125.0).astype(int)
        logger.info(f"   [{area_id}] {col_name} kiszámítva (N={len(cat_sub)} db POI, Medián sétaút: {np.median(net_dists):.0f} m).")

    # Összesített 15 perces város POI lefedettség száma ingatlanonként
    all_centroids = poi_proj.geometry.centroid
    all_poi_coords = np.column_stack((all_centroids.x, all_centroids.y))
    all_tree = cKDTree(all_poi_coords)
    counts_15p = all_tree.query_ball_point(prop_coords, r=(1125.0 / DETOUR_FACTOR))
    df.loc[valid_indices, 'poi_15p_osszes_count'] = [len(c) for c in counts_15p]
    logger.info(f"   [{area_id}] Átlagos 15 percen belüli elérhető POI-k száma: {df.loc[valid_indices, 'poi_15p_osszes_count'].mean():.1f} db.")

    # Mentés vissza a master parquetbe
    df.to_parquet(master_path, index=False)
    logger.info(f"[{area_id}] Frissített adathalmaz sikeresen elmentve: {master_path}")


if __name__ == "__main__":
    enrich_area_poi("wien_nordbahnhof")
    enrich_area_poi("kobanya")
