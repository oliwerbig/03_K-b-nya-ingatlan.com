# -*- coding: utf-8 -*-
"""scripts/canonize_schema.py v2 — a 3. réteg (processed) generálása.

Folyamat adathalmazonként:
  1. mapping alkalmazása (forrás-oszlopok -> kanonikus nevek + típus-transzformációk)
  2. sémavezérelt levezetések (log-árak, korrigált terület, épületkor, dummy-k, kategóriák)
  3. cím-alapú geokódolás becsatolása (a cache/eredmény CSV-ből — a portál-koordináták SOHA)
  4. hálózati réteg (network_metrics — ha a hálózati fájlok elérhetők)
  5. sémakoercíció (típusok + oszlopsorrend + hiányzó optional pótlás)
  6. export: parquet + emberi Excel (Master/Adatszótár/Statisztikák) + geojson

A kód SEMMILYEN területnevet nem tartalmaz — minden az areas.yaml-ből jön.
"""
import io
import json
import os
import re
import sys
import unicodedata

import numpy as np
import pandas as pd
import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
PROC = os.path.join(DATA, "processed")
RAW = os.path.join(DATA, "raw")
WALK_M_PER_MIN = 75.0

CATS = ["vasut", "metro", "villamos", "busz", "park", "iskola", "ovoda", "bolt", "gyogyszertar", "orvos"]


def load_schema():
    with io.open(os.path.join(DATA, "schema.yaml"), encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_areas():
    with io.open(os.path.join(DATA, "areas.yaml"), encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_mapping(path):
    if not os.path.exists(path):
        raise FileNotFoundError(f"Mapping hiányzik: {path}")
    with io.open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


# ==============================================================================
# 1. Mapping-motor (név + típus-transzformáció)
# ==============================================================================

def strip_accents(text):
    if not isinstance(text, str):
        return text
    nfkd = unicodedata.normalize("NFKD", text)
    return "".join(c for c in nfkd if not unicodedata.combining(c)).lower().strip()


def parse_number(value, decimal_comma=False):
    """Szám-elemzés: ezres-elválasztó, pénznem-csíkozás, tizedes-vessző opció."""
    if value is None or (isinstance(value, float) and np.isnan(value)):
        return np.nan
    if isinstance(value, (int, float)):
        return float(value)
    s = str(value).strip()
    if not s or s.lower() in ("nincs megadva", "n/a", "na", "-", "megállapodás szerint"):
        return np.nan
    s = s.replace("\u00a0", " ").replace("Ft/hó", "").replace("Ft", "").replace("€", "").replace("EUR", "")
    s = s.replace("HUF", "").replace("m²", "").replace("m2", "").strip()
    if decimal_comma:
        s = s.replace(".", "").replace(",", ".")
    else:
        s = s.replace(" ", "")
        if "," in s:
            s = s.replace(",", "")          # vessző: ezres-elválasztó (HUF-stílus)
        elif re.search(r"\.\d{3}(?!\d)", s):
            s = s.replace(".", "")          # pont + pontosan 3 jegy: ezres-elválasztó
    m = re.search(r"-?\d+(?:\.\d+)?", s)
    return float(m.group(0)) if m else np.nan


def _map_value(value, rules):
    """Szabályok alkalmazása egy cellára. rules: mapping-oszlop specifikáció."""
    if rules.get("empty_to_nan", True) and (value is None or (isinstance(value, str) and not value.strip())):
        return np.nan
    v = value
    if rules.get("regex_replace"):
        v = re.sub(rules["regex_replace"][0], rules["regex_replace"][1], str(v))
    if rules.get("split_take") is not None:
        _parts = str(v).split(rules.get("split_sep", ","))
        _idx = rules["split_take"]
        v = _parts[_idx] if _idx < len(_parts) else np.nan
    to = rules.get("to", "string")
    if to in ("float", "int"):
        v = parse_number(v, decimal_comma=bool(rules.get("decimal_comma")))
        if not np.isnan(v):
            if rules.get("min") is not None and v < rules["min"]:
                v = np.nan
            if rules.get("max") is not None and v > rules["max"]:
                v = np.nan
        if to == "int" and not np.isnan(v):
            v = int(round(v))
        return v
    if to == "bool":
        mp = rules.get("map") or {}
        if mp:
            norm = {strip_accents(k): int(val) for k, val in mp.items()}
            hit = norm.get(strip_accents(str(v)))
            if hit is not None:
                return hit
        if rules.get("contains"):
            return 1 if rules["contains"] in str(v) else 0
        return 1 if (v not in (None, "") and str(v).strip() not in ("nincs", "nem", "nincs megadva")) else 0
    if to == "string":
        mp = rules.get("map") or {}
        if mp:
            norm = {strip_accents(k): str(val) for k, val in mp.items()}
            hit = norm.get(strip_accents(str(v)))
            if hit is not None:
                return hit
        return str(v) if v not in (None, "") else np.nan
    if to == "ordinal_map":
        mp = rules.get("map") or {}
        norm = {strip_accents(k): int(val) for k, val in mp.items()}
        hit = norm.get(strip_accents(str(v)))
        return hit if hit is not None else np.nan
    return v


def apply_mapping(df_src, mapping):
    """A forrás-DataFrame -> kanonikus nevű, transzformált DataFrame."""
    out = pd.DataFrame(index=df_src.index)
    for canon, spec in (mapping.get("columns") or {}).items():
        src = spec.get("from")
        if src is None:
            continue
        if isinstance(src, list):
            present = [c for c in src if c in df_src.columns]
            if not present:
                out[canon] = np.nan
                continue
            series = df_src[present[0]]
            for c in present[1:]:
                series = series.combine_first(df_src[c])
        else:
            if src not in df_src.columns:
                out[canon] = np.nan
                continue
            series = df_src[src]
        out[canon] = series.map(lambda x: _map_value(x, spec))
    out["listing_type"] = df_src["listing_type"].map(
        lambda x: "elado" if str(x).lower() in ("elado", "kauf") else ("kiado" if str(x).lower() in ("kiado", "miete") else str(x))
    )
    return out


# ==============================================================================
# 2. Sémavezérelt levezetések
# ==============================================================================

def _num(d, col):
    """Numerikus Series hiányzó oszlop esetén is (NaN-sorozat)."""
    v = d.get(col)
    return pd.Series(np.nan, index=d.index) if v is None else pd.to_numeric(v, errors="coerce")


def derive_core(df, area_cfg, mapping):
    d = df.copy()
    crawl_year = None
    if "gyujtes_datuma" in d.columns:
        years = pd.to_numeric(d["gyujtes_datuma"].astype(str).str[:4], errors="coerce")
        if years.notna().any():
            crawl_year = int(years.max())
    if crawl_year is None:
        crawl_year = int((area_cfg.get("metadata") or {}).get("crawl_year", 2026))

    # pénznem: EUR-területen price_eur -> price_huf (rögzített, dokumentált árfolyam)
    rate = area_cfg.get("eur_huf_rate")
    if rate and "price_eur" in d.columns:
        if "price_huf" not in d.columns or d["price_huf"].isna().all():
            d["price_huf"] = d["price_eur"] * float(rate)
        if "nm_ar_eur" not in d.columns:
            d["nm_ar_eur"] = d["price_eur"] / d["alapterulet_nm"].replace(0, np.nan)
        if "nm_ar_huf" not in d.columns or d["nm_ar_huf"].isna().all():
            d["nm_ar_huf"] = d["price_huf"] / d["alapterulet_nm"].replace(0, np.nan)
    else:
        if "nm_ar_huf" not in d.columns:
            d["nm_ar_huf"] = d["price_huf"] / d["alapterulet_nm"].replace(0, np.nan)

    d["ar_millio_ft"] = d["price_huf"] / 1e6
    d["ar_ezer_ft_ho"] = np.where(d["listing_type"] == "kiado", d["price_huf"] / 1000.0, np.nan)
    d["log_ar"] = np.log(d["price_huf"].replace(0, np.nan))
    d["log_nm_ar"] = np.log(d["nm_ar_huf"].replace(0, np.nan))

    # építési év: becsült -> végleges, majd épületkor (NaN-honest)
    if "epites_eve_becsult" in d.columns:
        d["epites_eve"] = d["epites_eve"].fillna(d["epites_eve_becsult"])
    if "epites_eve" in d.columns:
        year = pd.to_numeric(d["epites_eve"], errors="coerce")
        d["epulet_kora_ev"] = np.where(year.isna(), np.nan,
                                       np.where(year >= crawl_year, 0.0,
                                                np.maximum(0, crawl_year - year))).astype(float)
        d["epites_eve_kategoria"] = pd.cut(
            d["epulet_kora_ev"], bins=[-0.1, 10, 30, 60, np.inf],
            labels=["0-10 év (új)", "10-30 év (rendszerváltás utáni)",
                    "30-60 év (panel-korszak)", "60+ év (háború előtti)"]
        ).astype("object")
        d["epites_eve_kategoria"] = d["epites_eve_kategoria"].where(
            d["epulet_kora_ev"].notna(), "Ismeretlen")

    # szobák
    if "szobaszam_osszes" in d.columns:
        d["szobaszam_kategoria"] = pd.cut(
            d["szobaszam_osszes"], bins=[0, 1.5, 2.5, 3.5, 999],
            labels=["1 szoba", "2 szoba", "3 szoba", "4+ szoba"]).astype("object")
        d["szobaszam_egesz"] = np.floor(d["szobaszam_osszes"])
        d["szobaszam_fel"] = d["szobaszam_osszes"] - np.floor(d["szobaszam_osszes"])

    # korrigált alapterület
    erk = d.get("erkely_nm")
    erk = pd.Series(np.nan, index=d.index) if erk is None else pd.to_numeric(erk, errors="coerce").fillna(0)
    d["korrigalt_alapterulet_nm"] = d["alapterulet_nm"] + 0.5 * np.maximum(erk, 0)

    if "alapterulet_nm" in d.columns and "szobaszam_osszes" in d.columns:
        d["atlagos_szobameret_nm"] = d["korrigalt_alapterulet_nm"] / d["szobaszam_osszes"].replace(0, np.nan)

    # állapot dummyk
    if "allapot_kod" in d.columns:
        kod = pd.to_numeric(d["allapot_kod"], errors="coerce")
        d["is_felujitando"] = (kod <= 2).astype("int64")
        d["is_ujszeru_vagy_uj"] = (kod >= 5).astype("int64")

    # panel/tegla az altipus szókincséből (a mapping adja a regexeket)
    alt = d.get("ingatlan_altipus")
    alt = pd.Series("", index=d.index) if alt is None else alt.fillna("").astype(str)
    panel_re = (mapping.get("vocab") or {}).get("panel_re", r"panel|plattenbau|iparositott|1945-1990")
    tegla_re = (mapping.get("vocab") or {}).get("tegla_re", r"tegla|altbau|neubau|1991-2000")
    if "is_panel" not in d.columns or d["is_panel"].isna().all():
        d["is_panel"] = alt.str.contains(panel_re, flags=re.I, na=False).astype("int64")
    if "is_tegla" not in d.columns or d["is_tegla"].isna().all():
        d["is_tegla"] = alt.str.contains(tegla_re, flags=re.I, na=False).astype("int64")

    # erkély
    if "has_erkely" not in d.columns:
        d["has_erkely"] = (pd.Series(erk).fillna(0) > 0).astype("int64")

    # emelet
    em = d.get("emelet")
    em = pd.Series("", index=d.index) if em is None else em.fillna("").astype(str)
    d["is_foldszint"] = (em.str.contains("földszint|foldszint|emelet 0", flags=re.I, na=False)
                         | (_num(d, "emelet_szam") == 0)).astype("int64")
    # zárószint: a portál már nem ad kategóriát — dokumentált proxy:
    # a lakás a legfelső emeleten van (emelet_szam == epulet_szintjei_szam)
    d["is_zaroszint"] = (em.str.contains("záró|zaro|legfelső|legfelso", flags=re.I, na=False)
                         | ((_num(d, "emelet_szam") == _num(d, "epulet_szintjei_szam"))
                            & _num(d, "emelet_szam").notna() & _num(d, "epulet_szintjei_szam").notna())).astype("int64")
    # tetőtér: a DEDIKÁLT tetőtér-mezőből (param_Tetoter / bécsi Dachgeschoss típus)
    tt = d.get("tetoter")
    tt = pd.Series("", index=d.index) if tt is None else tt.fillna("").astype(str)
    # a "nem tetőtéri" negációt kizárjuk
    d["is_tetoter"] = ((tt.str.contains("tető|teto", flags=re.I, na=False)
                        & ~tt.str.contains("nem tető|nem teto|nemtető", flags=re.I, na=False))
                       | alt.str.contains("dachgeschoss|dachgeschoß|dachgeschosswohnung", flags=re.I, na=False)).astype("int64")
    if "is_magas_emelet_lift_nelkul" not in d.columns:
        emelet_szam = _num(d, "emelet_szam")
        lift = _num(d, "has_lift").fillna(0)
        d["is_magas_emelet_lift_nelkul"] = ((emelet_szam >= 3) & (lift == 0)).astype("int64")

    # fűtés-kategória (a mapping adja a szókincset)
    fut = d.get("futes")
    fut = pd.Series("", index=d.index) if fut is None else fut.fillna("").astype(str)
    vocab = mapping.get("vocab") or {}
    d["futes_kategoria"] = "egyeb"
    for cat, pat in vocab.get("futes_categories", {}).items():
        d.loc[fut.str.contains(pat, flags=re.I, na=False), "futes_kategoria"] = cat
    d.loc[fut == "", "futes_kategoria"] = np.nan
    d["has_tavfutes"] = fut.str.contains(vocab.get("tavfutes_re", r"távfűtés|tavfutes"), flags=re.I, na=False).astype("int64")
    d["has_konvektor"] = fut.str.contains(vocab.get("konvektor_re", r"konvektor|villany"), flags=re.I, na=False).astype("int64")
    d["has_megujulo"] = fut.str.contains(vocab.get("megujulo_re", r"hőszivattyú|hoszivattyu|napelem|geoterm"), flags=re.I, na=False).astype("int64")

    # garázs/beálló a parkolás szövegből
    if "has_garazs_vagy_beallo" not in d.columns:
        park = d.get("parkolas")
        park = pd.Series("", index=d.index) if park is None else park.fillna("").astype(str)
        d["has_garazs_vagy_beallo"] = park.str.contains(
            vocab.get("garazs_re", r"garázs|garazs|beálló|beallo|teremgarázs"), flags=re.I, na=False).astype("int64")

    # ár-outlier (robusztus IQR a log nm-áron)
    logp = d["log_nm_ar"].dropna()
    if len(logp) >= 10:
        q1, q3 = logp.quantile(0.25), logp.quantile(0.75)
        iqr = q3 - q1
        d["is_ar_outlier"] = ((d["log_nm_ar"] < q1 - 3 * iqr) | (d["log_nm_ar"] > q3 + 3 * iqr)).astype("int64")
    else:
        d["is_ar_outlier"] = 0

    # leírás-hossz
    if "leiras_hossz" not in d.columns:
        _lr = d.get("leiras")
        _lr = pd.Series("", index=d.index) if _lr is None else _lr.fillna("")
        d["leiras_hossz"] = _lr.astype(str).str.len()

    # duplikátum-jelölő (cím + terület + kerekített ár; listing_id szerint rendezve)
    key = (d.get("cim_teljes").fillna("").astype(str) + "|"
           + d["alapterulet_nm"].round(0).astype(str) + "|"
           + d["price_huf"].round(-3).astype(str))
    d["is_duplikalt_gyanus"] = key.duplicated().astype("int64")

    return d


# ==============================================================================
# 3. Cím-alapú geokódolás becsatolása
# ==============================================================================

def join_geocode(df, area_id):
    csv_path = os.path.join(DATA, "geocoding", f"{area_id}_geocode_eredmeny.csv")
    if not os.path.exists(csv_path):
        print(f"  [!] geokódolási eredmény hiányzik: {csv_path} (futtasd a geocode lépést)")
        df["geokodolt_lat"] = np.nan
        df["geokodolt_lon"] = np.nan
        df["geokodolas_pontossag"] = "nincs"
        df["geokodolas_modszere"] = "cim_nominatim"
        df["minta_garantalt_pontos"] = 0
        return df
    g = pd.read_csv(csv_path, dtype={"listing_id": str})
    df["listing_id"] = df["listing_id"].astype(str)
    g = g.drop_duplicates(subset=["listing_id"], keep="first")
    df = df.merge(g[["listing_id", "geokodolt_lat", "geokodolt_lon", "geokodolas_pontossag",
                     "varosresz_geokodolt", "geokodolas_szolgaltato", "felhasznalt_hazszam"]],
                  on="listing_id", how="left")
    df["geokodolas_modszere"] = "cim_nominatim"
    df["geokodolas_pontossag"] = df["geokodolas_pontossag"].fillna("nincs")
    # városrész a geokódolásból (a portál slug-ja helyett)
    _vr_geo = df.get("varosresz_geokodolt")
    if _vr_geo is not None:
        df["varosresz"] = _vr_geo.where(_vr_geo.notna() & (_vr_geo.astype(str) != ""), df.get("varosresz"))
    # pontos: hazszam (exakt) VAGY hazszam_interpolalt (legközelebbi házszám, dokumentált közelítés)
    df["minta_garantalt_pontos"] = (df["geokodolas_pontossag"].isin(["hazszam", "hazszam_interpolalt"])).astype("int64")
    return df


# ==============================================================================
# 4. Hálózati réteg
# ==============================================================================

def apply_network(df, area_id, street_file, transit_file, poi_file):
    if not (street_file and os.path.exists(street_file) and transit_file and os.path.exists(transit_file)):
        print(f"  [!] hálózati fájlok hiányoznak — a hálózati oszlopok üresen maradnak")
        return df
    sys.path.insert(0, os.path.join(ROOT, "scripts"))
    from network_metrics import compute_area  # noqa: E402

    net = compute_area(area_id, df, street_file, transit_file, poi_file)
    d = df.copy()
    for c, s in net.items():
        d[c] = s
    bins = [0.0, 150.0, 300.0, 500.0, 1000.0, 2000.0, np.inf]
    labels = ["<150 m", "150-300 m", "300-500 m", "500-1000 m", "1000-2000 m", ">2000 m (referencia)"]
    d["vasut_zona"] = pd.cut(d["tavolsag_vasut_m"], bins=bins, labels=labels).astype("object")
    d["is_vasut_immisszio_150m"] = (d["tavolsag_vasut_m"] < 150.0).astype("int64")
    for c in CATS:
        dist = d.get(f"tavolsag_{c}_halozati_m")
        if dist is not None:
            d[f"menetido_{c}_gyalog_perc"] = (dist / WALK_M_PER_MIN).round(1)
            for p, lim in (("5p", 375.0), ("10p", 750.0), ("15p", 1125.0)):
                d[f"{c}_{p}_seta"] = (dist <= lim).astype("int64")
    kp_cols = [c for c in ("tavolsag_metro_halozati_m", "tavolsag_vasut_halozati_m", "tavolsag_villamos_halozati_m") if c in d.columns]
    if kp_cols:
        kp = d[kp_cols].min(axis=1)
        d["tavolsag_kotottpalya_halozati_m"] = kp.round(1)
        d["menetido_kotottpalya_gyalog_perc"] = (kp / WALK_M_PER_MIN).round(1)
        for p, lim in (("5p", 375.0), ("10p", 750.0), ("15p", 1125.0)):
            d[f"kotottpalya_{p}_seta"] = (kp <= lim).astype("int64")
        tip = pd.Series("", index=d.index, dtype="object")
        for c in ("metro", "vasut", "villamos"):
            col = f"tavolsag_{c}_halozati_m"
            if col in d.columns:
                m = (d[col] == kp) & d[col].notna()
                tip = tip.mask(m, c)
        d["legkozelebbi_kotottpalya_tipus"] = tip
    return d


# ==============================================================================
# 5. Sémakoercíció
# ==============================================================================

def coerce(df, schema):
    types = {**schema.get("required", {}), **schema.get("optional", {})}
    d = df.copy()
    for c in list(types.keys()):
        if c not in d.columns:
            d[c] = np.nan
    for c, t in types.items():
        if c not in d.columns:
            continue
        if t == "int64":
            if c == "epulet_kora_ev":
                d[c] = pd.to_numeric(d[c], errors="coerce").astype("float64")
            else:
                d[c] = pd.to_numeric(d[c], errors="coerce").fillna(0).astype("int64")
        elif t == "float64":
            d[c] = pd.to_numeric(d[c], errors="coerce").astype("float64")
        else:
            d[c] = d[c].astype("object")
    order = [c for c in schema["required"] if c in d.columns] + [c for c in schema["optional"] if c in d.columns]
    extra = [c for c in d.columns if c not in order]
    return d[order + extra]


# ==============================================================================
# 6. Exportok
# ==============================================================================

def _geojson(df, path, tipus="mind"):
    import geopandas as gpd
    sub = df[df["minta_garantalt_pontos"] == 1].copy()
    if tipus in ("elado", "kiado"):
        sub = sub[sub["listing_type"] == tipus]
    sub = sub.dropna(subset=["geokodolt_lat", "geokodolt_lon"])
    if len(sub) == 0:
        print(f"   geojson {os.path.basename(path)}: 0 pont (kihagyva)")
        return
    gdf = gpd.GeoDataFrame(sub, geometry=gpd.points_from_xy(sub["geokodolt_lon"], sub["geokodolt_lat"]), crs="EPSG:4326")
    gdf.to_file(path, driver="GeoJSON")
    print(f"   geojson {os.path.basename(path)}: {len(gdf)} pont")


def write_exports(area_id, df, cfg, schema):
    os.makedirs(PROC, exist_ok=True)
    data_cfg = cfg["data"]
    parquet_p = os.path.join(ROOT, data_cfg["master_parquet"])
    human_p = os.path.join(ROOT, data_cfg["human_xlsx"])
    geojson_p = os.path.join(ROOT, data_cfg["pontos_geojson"])

    df.to_parquet(parquet_p, index=False)
    print(f"[{area_id}] parquet: {len(df)} sor, {len(df.columns)} oszlop")

    # --- Ember által olvasható Excel: Master + Adatszótár + Statisztikák ---
    with pd.ExcelWriter(human_p, engine="openpyxl") as xw:
        df.to_excel(xw, sheet_name="Master", index=False)
        dict_rows = []
        for c, t in {**schema.get("required", {}), **schema.get("optional", {})}.items():
            dict_rows.append({"oszlop": c, "tipus": t,
                              "szerep": "kotelezo" if c in schema.get("required", {}) else "opcionalis"})
        pd.DataFrame(dict_rows).to_excel(xw, sheet_name="Adatszotar", index=False)
        stats = []
        for c in df.columns:
            s = df[c]
            if pd.api.types.is_numeric_dtype(s):
                stats.append({"oszlop": c, "tipus": "numeric", "n": int(s.notna().sum()),
                              "min": round(float(s.min()), 2) if s.notna().any() else None,
                              "median": round(float(s.median()), 2) if s.notna().any() else None,
                              "max": round(float(s.max()), 2) if s.notna().any() else None})
            else:
                vc = s.astype(str).value_counts().head(5)
                stats.append({"oszlop": c, "tipus": "kategorikus", "n": int(s.notna().sum()),
                              "min": None, "median": None, "max": None,
                              "leggyakoribb": " | ".join(f"{k}:{v}" for k, v in vc.items())[:200]})
        pd.DataFrame(stats).to_excel(xw, sheet_name="Statisztikak", index=False)
    print(f"[{area_id}] emberi excel: {os.path.basename(human_p)}")

    _geojson(df, geojson_p, "mind")
    base, ext = os.path.splitext(geojson_p)
    _geojson(df, f"{base}_elado{ext}", "elado")
    _geojson(df, f"{base}_kiado{ext}", "kiado")


# ==============================================================================
# Fő belépő
# ==============================================================================

def canonize_area(area_id):
    areas = load_areas()
    cfg = areas["areas"][area_id]
    schema = load_schema()
    mapping = load_mapping(os.path.join(ROOT, cfg["data"]["mapping"]))
    print(f"=== KÁNONIZÁLÁS: [{area_id}] ({cfg['source']}) ===")

    src = pd.read_excel(os.path.join(ROOT, cfg["data"]["extracted_xlsx"]))
    df = apply_mapping(src, mapping)
    df = derive_core(df, cfg, mapping)
    df = join_geocode(df, area_id)
    df = apply_network(df, area_id,
                       os.path.join(ROOT, cfg["data"].get("street_file", "")),
                       os.path.join(ROOT, cfg["data"].get("transit_file", "")),
                       os.path.join(ROOT, cfg["data"].get("poi_file", "")))
    df = coerce(df, schema)
    write_exports(area_id, df, cfg, schema)
    return df


def main():
    import argparse
    ap = argparse.ArgumentParser(description="Kánonizálás (3. réteg)")
    ap.add_argument("--dataset", help="Csak egy adathalmaz")
    ap.add_argument("--all", action="store_true")
    args = ap.parse_args()
    areas = load_areas()
    ids = list(areas["areas"].keys()) if args.all else ([args.dataset] if args.dataset else [areas.get("active_area", "kobanya")])
    for aid in ids:
        canonize_area(aid)
    print("\nKÁNONIZÁLÁS KÉSZ")


if __name__ == "__main__":
    main()