# -*- coding: utf-8 -*-
"""scripts/canonize_schema.py — a kanonikus séma végrehajtása az adatrétegen.

- átnevezés (city->varos, van_erkely->has_erkely, price_million_huf->ar_millio_ft)
- fókusz (mazsa) és nem-kanonikus oszlopok eldobása
- hiányzók levezetése (szobaszam_kategoria, vasut_zona, immissziós dummy, korszakok, logok)
- VALÓDI hálózati távolságok + POI-sávok újraszámítása (network_metrics)
- az összes export újraírása (parquet, db, csv, xlsx, geojson)
"""
import os
import sys
import sqlite3

import numpy as np
import pandas as pd
import yaml

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from network_metrics import compute_area, WALK_M_PER_MIN  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROC = os.path.join(ROOT, "data", "processed")
RAW = os.path.join(ROOT, "data", "raw")
DATA = os.path.join(ROOT, "data")

CATS = ["vasut", "metro", "villamos", "busz", "park", "iskola", "ovoda", "bolt", "gyogyszertar", "orvos"]

RENAME = {"city": "varos", "van_erkely": "has_erkely", "price_million_huf": "ar_millio_ft"}

def load_schema():
    with open(os.path.join(DATA, "schema.yaml"), encoding="utf-8") as f:
        s = yaml.safe_load(f)
    return list(s["required"].keys()), list(s["optional"].keys())

def derive_core(df):
    """Levezethető kanonikus oszlopok (mindkét területre)."""
    df = df.copy()
    if "szobaszam_kategoria" not in df.columns or df["szobaszam_kategoria"].isna().all():
        if "szobaszam_osszes" in df.columns:
            df["szobaszam_kategoria"] = pd.cut(
                df["szobaszam_osszes"], bins=[0, 1.5, 2.5, 3.5, 99],
                labels=["1 szoba", "2 szoba", "3 szoba", "4+ szoba"],
            ).astype("object")
    if "epulet_kora_ev" in df.columns:
        df["epites_eve_kategoria"] = pd.cut(
            df["epulet_kora_ev"], bins=[-0.1, 10, 30, 60, np.inf],
            labels=["0-10 év (új)", "10-30 év (rendszerváltás utáni)",
                    "30-60 év (panel-korszak)", "60+ év (háború előtti)"],
        ).astype("object")
    if "log_ar" not in df.columns:
        df["log_ar"] = np.log(df["price_huf"].replace(0, np.nan))
    if "log_nm_ar" not in df.columns:
        df["log_nm_ar"] = np.log(df["nm_ar_huf"].replace(0, np.nan))
    if "is_magas_emelet_lift_nelkul" not in df.columns:
        df["is_magas_emelet_lift_nelkul"] = (
            (df.get("emelet_szam", pd.Series(np.nan, index=df.index)) >= 3)
            & (df.get("has_lift", pd.Series(0, index=df.index)) == 0)
        ).astype("int64")
    return df

def apply_network(df, area_id, street_file, transit_file, poi_file):
    """Hálózati oszlopok újraszámítása + levezetések (menetidő, dummyk, kötöttpálya)."""
    net = compute_area(area_id, df, street_file, transit_file, poi_file)
    df = df.copy()
    for c, s in net.items():
        df[c] = s
    # tavolsag_vasut_m -> vasut_zona + immissziós dummy (a 6 diszjunkt sáv)
    bins = [0.0, 150.0, 300.0, 500.0, 1000.0, 2000.0, np.inf]
    labels = ["<150 m", "150-300 m", "300-500 m", "500-1000 m", "1000-2000 m", ">2000 m (referencia)"]
    df["vasut_zona"] = pd.cut(df["tavolsag_vasut_m"], bins=bins, labels=labels).astype("object")
    df["is_vasut_immisszio_150m"] = (df["tavolsag_vasut_m"] < 150.0).astype("int64")
    # menetidő + izokrón dummyk
    for c in CATS:
        d = df.get(f"tavolsag_{c}_halozati_m")
        df[f"menetido_{c}_gyalog_perc"] = (d / WALK_M_PER_MIN).round(1)
        for p, lim in (("5p", 375.0), ("10p", 750.0), ("15p", 1125.0)):
            df[f"{c}_{p}_seta"] = (d <= lim).astype("int64")
    # kötöttpálya index
    kp = df[["tavolsag_metro_halozati_m", "tavolsag_vasut_halozati_m",
             "tavolsag_villamos_halozati_m"]].min(axis=1)
    df["tavolsag_kotottpalya_halozati_m"] = kp.round(1)
    df["menetido_kotottpalya_gyalog_perc"] = (kp / WALK_M_PER_MIN).round(1)
    for p, lim in (("5p", 375.0), ("10p", 750.0), ("15p", 1125.0)):
        df[f"kotottpalya_{p}_seta"] = (kp <= lim).astype("int64")
    tip = pd.Series("", index=df.index, dtype="object")
    for c in ("metro", "vasut", "villamos"):
        col = f"tavolsag_{c}_halozati_m"
        m = (df[col] == kp) & df[col].notna()
        tip = tip.mask(m, c)
    df["legkozelebbi_kotottpalya_tipus"] = tip
    # legkozelebbi park név: a POI-parkokból (ha nincs, marad a network-motor értéke)
    return df

def coerce(df, req, opt):
    """Sématípusok + oszlopsorrend + hiányzó optional pótlása."""
    schema = dict(yaml.safe_load(open(os.path.join(DATA, "schema.yaml"), encoding="utf-8")))
    types = {**schema.get("required", {}), **schema.get("optional", {})}
    for c in opt:
        if c not in df.columns:
            df[c] = np.nan
    for c, t in types.items():
        if c not in df.columns:
            continue
        if t == "int64":
            df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0).astype("int64")
        elif t == "float64":
            df[c] = pd.to_numeric(df[c], errors="coerce").astype("float64")
        else:
            df[c] = df[c].astype("object")
    order = [c for c in req if c in df.columns] + [c for c in opt if c in df.columns]
    return df[order]

def write_exports(area_id, df):
    os.makedirs(PROC, exist_ok=True)
    base = f"{area_id}_szamitott_master" if area_id == "kobanya" else f"{area_id}_szamitott_master"
    mparquet = os.path.join(PROC, f"kobanya_ingatlan_szamitott_master.parquet" if area_id == "kobanya"
                            else f"{area_id}_szamitott_master.parquet")
    df.to_parquet(mparquet, index=False)
    print(f"[{area_id}] parquet: {len(df)} sor, {len(df.columns)} oszlop")

    if area_id == "kobanya":
        with sqlite3.connect(os.path.join(PROC, "kobanya_ingatlan_szamitott_master.db")) as con:
            df.to_sql("master", con, if_exists="replace", index=False)
        el = df[df["listing_type"] == "elado"]
        ki = df[df["listing_type"] == "kiado"]
        el.to_csv(os.path.join(PROC, "kobanya_elado_szamitott.csv"), index=False, encoding="utf-8")
        ki.to_csv(os.path.join(PROC, "kobanya_kiado_szamitott.csv"), index=False, encoding="utf-8")
        df.to_excel(os.path.join(PROC, "kobanya_ingatlan_szamitott_modellezes_1320db.xlsx"), index=False)
        _write_geojson(df, os.path.join(PROC, "kobanya_ingatlan_szamitott_pontos.geojson"), tipus="mind")
        _write_geojson(df, os.path.join(PROC, "kobanya_elado_pontos.geojson"), tipus="elado")
        _write_geojson(df, os.path.join(PROC, "kobanya_kiado_pontos.geojson"), tipus="kiado")
    else:
        _write_geojson(df, os.path.join(PROC, f"{area_id}_pontos.geojson"), tipus="mind")

def _write_geojson(df, path, tipus="mind"):
    import geopandas as gpd
    sub = df[df["minta_garantalt_pontos"] == 1].copy()
    if tipus == "elado":
        sub = sub[sub["listing_type"] == "elado"]
    elif tipus == "kiado":
        sub = sub[sub["listing_type"] == "kiado"]
    sub = sub.dropna(subset=["geokodolt_lat", "geokodolt_lon"])
    gdf = gpd.GeoDataFrame(
        sub, geometry=gpd.points_from_xy(sub["geokodolt_lon"], sub["geokodolt_lat"]),
        crs="EPSG:4326",
    )
    gdf.to_file(path, driver="GeoJSON")
    print(f"   geojson {os.path.basename(path)}: {len(gdf)} pont")

def main():
    req, opt = load_schema()
    print("Kánon mezők:", len(req), "kötelező,", len(opt), "opcionális")

    # ---------------- Kőbánya ----------------
    k = pd.read_parquet(os.path.join(PROC, "kobanya_ingatlan_szamitott_master.parquet"))
    k = k.rename(columns=RENAME)
    k = k.loc[:, ~k.columns.duplicated()]
    k = derive_core(k)
    k = apply_network(
        k, "kobanya",
        os.path.join(RAW, "osm_streets_kobanya_1250m.json"),
        os.path.join(RAW, "osm_kobanya_transit_2000m.json"),
        os.path.join(DATA, "poi_kobanya_buffered.geojson"),
    )
    k = coerce(k, req, opt)
    write_exports("kobanya", k)

    # ---------------- Bécs ----------------
    w = pd.read_parquet(os.path.join(PROC, "wien_nordbahnhof_szamitott_master.parquet"))
    w = w.rename(columns=RENAME)
    w = w.loc[:, ~w.columns.duplicated()]
    w = derive_core(w)
    w = apply_network(
        w, "wien_nordbahnhof",
        os.path.join(RAW, "osm_streets_wien_nordbahnhof_1250m.json"),
        os.path.join(RAW, "osm_wien_nordbahnhof_transit_2000m.json"),
        os.path.join(DATA, "poi_wien_nordbahnhof_buffered.geojson"),
    )
    w = coerce(w, req, opt)
    write_exports("wien_nordbahnhof", w)

    print("\nKÁNONIZÁLÁS KÉSZ")

if __name__ == "__main__":
    main()