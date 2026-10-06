# -*- coding: utf-8 -*-
"""scripts/preprocess_new_data.py
IFK-TDK 2026 Kutatási Adatelőkészítő és Térbeli Elemző Pipeline

Fő képességek:
1. Tetszőleges nyers adatformátum fogadása (Excel .xlsx/.xls, CSV, JSON).
2. Automatikus oszlopillesztés (Auto-Mapping & normalizálás alias szótárral).
3. Teljes körű Feature Engineering (állapotkód 1-6, korrigált alapterület, log árak, dummyk).
4. Ingyenes Nominatim geokódolás permanens helyi gyorsítótárral (data/raw/geocode_cache.json).
5. Szigorúan rögzített kutatási sávrendszerek automatikus számítása:
   - Sáv 1 (Immissziós sávok): 0 - 150 - 300 - 500 - 1000 - 2000 m (és >2000 m), plusz is_vasut_immisszio_150m dummy.
   - Sáv 2 (Gyalogos izokrónok, v = 1.25 m/s): 0 - 375 - 750 - 1125 m (vasut_5p_seta, 10p, 15p).
6. Sémavalidáció a data/schema.yaml alapján és kimenetek generálása:
   - data/processed/{name}_szamitott_master.parquet
   - data/processed/{name}_pontos.geojson
"""

import os
import sys
import json
import logging
import time
import argparse
import unicodedata
import re
from typing import Dict, List, Optional, Tuple


import numpy as np
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point, LineString
import yaml

# Geocoding
try:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

try:
    from geopy.geocoders import Nominatim

    HAS_GEOPY = True
except ImportError:
    HAS_GEOPY = False

# Logger konfiguráció
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s", datefmt="%H:%M:%S"
)
logger = logging.getLogger("preprocess_pipeline")


# ==============================================================================
# Szigorúan rögzített kánoni sávrendszerek
# ==============================================================================
VASUT_IMMISSZIO_BINS = [0.0, 150.0, 300.0, 500.0, 1000.0, 2000.0, np.inf]
VASUT_IMMISSZIO_LABELS = [
    "<150 m (Immisszió)",
    "150-300 m (Erős teher)",
    "300-500 m (Átmeneti)",
    "500-1000 m (Háttérzaj)",
    "1000-2000 m (Közepes ref.)",
    ">2000 m (Tiszta ref.)",
]

IZOKRON_BINS = [0.0, 375.0, 750.0, 1125.0]
DETOUR_FACTOR = 1.25  # Hálózati gyalogos kerülő faktor (Dijkstra korrekció)
WALK_SPEED_M_PER_MIN = 75.0  # 1.25 m/s * 60 s = 75 m/perc

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCHEMA_PATH = os.path.join(PROJECT_ROOT, "data", "schema.yaml")
CACHE_PATH = os.path.join(PROJECT_ROOT, "data", "raw", "geocode_cache.json")


def load_schema(path: str = SCHEMA_PATH) -> dict:
    """Kanonikus séma beolvasása YAML fájlból."""
    if not os.path.exists(path):
        raise FileNotFoundError(f"Sémafájl nem található: {path}")
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def strip_accents(text: str) -> str:
    """Ékezetek és speciális karakterek eltávolítása az összehasonlításhoz."""
    if not isinstance(text, str):
        return str(text)
    nfkd = unicodedata.normalize("NFKD", text)
    return "".join([c for c in nfkd if not unicodedata.combining(c)]).lower().strip()


# ==============================================================================
# 1. Beolvasás és Automatikus Oszlopillesztés (Auto-Mapping)
# ==============================================================================
COLUMN_SYNONYMS = {
    "listing_id": [
        "listing_id",
        "id",
        "hirdetes_id",
        "hirdetes_azonosito",
        "external_id",
        "azonosito",
    ],
    "listing_type": ["listing_type", "tipus", "hirdetes_tipus", "kinalat_tipus", "offer_type"],
    "price_huf": [
        "price_huf",
        "price",
        "ar",
        "ar_huf",
        "vetelar",
        "vetelar_huf",
        "iranyar",
        "berleti_dij",
        "price_raw",
    ],
    "price_million_huf": ["price_million_huf", "ar_millio_ft", "ar_mft", "price_mft", "ar_m"],
    "alapterulet_nm": [
        "alapterulet_nm",
        "alapterulet",
        "area_m2",
        "m2",
        "nm",
        "meret",
        "terulet",
        "size_sqm",
        "area",
    ],
    "szobaszam_osszes": [
        "szobaszam_osszes",
        "szobaszam",
        "szoba",
        "rooms",
        "szobak",
        "szobak_szama",
        "room_count",
    ],
    "cim_teljes": [
        "cim_teljes",
        "cim",
        "address",
        "full_address",
        "street_address",
        "utca_hazszam",
        "ingatlan_cime",
        "helyszin",
    ],
    "utca": ["utca", "street", "kozterulet", "kozterulet_neve", "utcanev", "kozterulet_nev"],
    "hazszam": [
        "hazszam",
        "hazszam_vegleges",
        "hazszam_eredeti",
        "house_number",
        "szam",
        "hazszam_nlp",
    ],
    "kerulet": ["kerulet", "district", "district_roman"],
    "varos": ["varos", "city", "telepules"],
    "leiras": ["leiras", "description", "megjegyzes", "details", "hirdetes_szovege", "reszletek"],
    "title": ["title", "cimke", "hirdetes_cime", "megnevezes", "fejlec"],
    "varosresz": ["varosresz", "subdistrict", "telepulesresz", "varos_resz"],
    "allapot": ["allapot", "condition", "allapota", "ingatlan_allapota"],
    "allapot_kod": ["allapot_kod", "condition_code"],
    "ingatlan_altipus": ["ingatlan_altipus", "altipus", "property_subtype", "epites_modja"],
    "erkely_nm": ["erkely_nm", "erkely", "balcony_m2", "erkely_meret", "loggia_nm"],
    "epites_eve": ["epites_eve", "epitesiev", "year_built", "epites_ev", "epult"],
    "lift": ["lift", "has_lift", "lift_van"],
    "klima": ["klima", "has_klima", "legkondi", "air_conditioner"],
    "emelet": ["emelet", "floor", "emelet_raw"],
    "emelet_szam": ["emelet_szam"],
    "epulet_szintjei_szam": ["epulet_szintjei_szam"],
    "futes": ["futes", "heating", "futestipus"],
    "geokodolt_lat": ["geokodolt_lat", "lat_jsonld", "lat", "latitude", "szelesseg", "y"],
    "geokodolt_lon": ["geokodolt_lon", "lon_jsonld", "lon", "lng", "longitude", "hosszusag", "x"],
    "minta_garantalt_pontos": ["minta_garantalt_pontos", "pontos", "is_exact", "is_precise"],
    "url": ["url", "link", "hirdetes_link"],
    "postal_code": ["postal_code", "plz", "zip", "iranyitoszam"],
    "kozos_koltseg_eur": ["kozos_koltseg_eur"],
    "rezsikoltseg_eur": ["rezsikoltseg_eur"],
    "kaucio_eur": ["kaucio_eur"],
    "epites_eve_kategoria": ["epites_eve_kategoria"],
}


def load_raw_data(file_path: str, input_type: Optional[str] = None) -> pd.DataFrame:
    """Nyers adatállomány beolvasása támogatott formátumokból."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"A megadott bemeneti fájl nem létezik: {file_path}")

    ext = os.path.splitext(file_path)[1].lower() if not input_type else f".{input_type.lower()}"
    logger.info(f"Fájl betöltése: {file_path} (formátum: {ext})")

    if ext in [".xlsx", ".xls", ".excel"]:
        xls = pd.ExcelFile(file_path, engine="openpyxl")
        if len(xls.sheet_names) > 1:
            logger.info(f"Több munkalap észlelve ({xls.sheet_names}), összesítés...")
            dfs = []
            for s in xls.sheet_names:
                sub_df = pd.read_excel(xls, sheet_name=s)
                if not sub_df.empty:
                    dfs.append(sub_df)
            if dfs:
                return pd.concat(dfs, ignore_index=True)
        return pd.read_excel(xls, sheet_name=0)
    elif ext in [".csv", ".txt"]:
        for enc in ["utf-8-sig", "utf-8", "latin1", "cp1250"]:
            try:
                return pd.read_csv(file_path, encoding=enc)
            except Exception:
                continue
        return pd.read_csv(file_path)
    elif ext in [".json"]:
        return pd.read_json(file_path)
    elif ext in [".parquet"]:
        return pd.read_parquet(file_path)
    else:
        raise ValueError(f"Nem támogatott fájlformátum: {ext}")


def auto_map_columns(
    df: pd.DataFrame, custom_mapping: Optional[Dict[str, str]] = None
) -> pd.DataFrame:
    """Oszlopok intelligens megfeleltetése a kanonikus elnevezésekre duplikációmentesen."""
    mapping = {}
    used_targets = set()

    # Ha a forrásban már szerepelnek kanonikus nevek, azokat fenntartjuk
    for canon in COLUMN_SYNONYMS.keys():
        if canon in df.columns:
            used_targets.add(canon)

    # 1. Egyéni mapping érvényesítése
    if custom_mapping:
        for src, canon in custom_mapping.items():
            if src in df.columns and canon not in used_targets:
                mapping[src] = canon
                used_targets.add(canon)

    # 2. Heurisztikus megfeleltetés a szinonima-szótárból
    cleaned_src_cols = {col: strip_accents(col).replace(" ", "_") for col in df.columns}
    for src_orig, src_clean in cleaned_src_cols.items():
        if src_orig in mapping or src_orig in used_targets:
            continue
        for canon, synonyms in COLUMN_SYNONYMS.items():
            if canon in used_targets:
                continue
            for syn in synonyms:
                syn_clean = strip_accents(syn).replace(" ", "_")
                if src_clean == syn_clean:
                    mapping[src_orig] = canon
                    used_targets.add(canon)
                    break
            if src_orig in mapping:
                break

    logger.info(
        f"Oszlopmegfeleltetés sikeres ({len(mapping)} oszlop átnevezve, {len(used_targets)} kanonikus oszlop lefedve):"
    )
    for s, c in mapping.items():
        logger.info(f"  '{s}' -> '{c}'")

    renamed_df = df.rename(columns=mapping).copy()
    # Duplikált oszlopnevek kiszűrése ha mégis előfordulna
    renamed_df = renamed_df.loc[:, ~renamed_df.columns.duplicated()].copy()
    return renamed_df


# ==============================================================================
# 2. Feature Engineering Motor (Számított Mezők Képzése)
# ==============================================================================
def parse_condition_to_code(val) -> int:
    """Szöveges állapot leképezése a szigorú 1..6 rendezett skálára (magyar és német nyelvű támogatással)."""
    if pd.isna(val):
        return 3  # Átlagos/jó állapot default
    s = strip_accents(str(val)).lower()
    if any(
        k in s
        for k in ["felujitando", "bontando", "rossz", "romos", "sanierungsbedurftig", "abbruchreif"]
    ):
        return 1
    if any(k in s for k in ["kozepes", "atlagos", "lakhato", "nach vereinbarung"]):
        return 2
    if any(k in s for k in ["jo allapotu", "jo", "rendben", "gut", "gepflegt"]):
        return 3
    if any(
        k in s
        for k in ["felujitott", "frissen felujitott", "saniert", "renoviert", "generalsaniert"]
    ):
        return 4
    if any(k in s for k in ["ujszeru", "ujszeru allapotu", "sehr gut", "neuwertig"]):
        return 5
    if any(
        k in s for k in ["uj epitesu", "uj", "epites alatt", "tervezett", "erstbezug", "neubau"]
    ):
        return 6
    return 3


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """Minden szükséges derivált, pénzügyi és strukturális mutató előállítása."""
    df = df.copy()

    # 1. Alapazonosítók
    if "listing_id" not in df.columns:
        df["listing_id"] = [f"GEN_{i + 1:05d}" for i in range(len(df))]
    else:
        df["listing_id"] = df["listing_id"].astype(str)

    if "listing_type" not in df.columns:
        df["listing_type"] = "elado"
    else:
        df["listing_type"] = (
            df["listing_type"]
            .astype(str)
            .str.lower()
            .apply(lambda x: "kiado" if "kiad" in x or "rent" in x else "elado")
        )

    # 2. Alapterület és szobák
    if "alapterulet_nm" not in df.columns:
        raise KeyError("Hiányzó kötelező mező: alapterület (alapterulet_nm) nem azonosítható!")
    df["alapterulet_nm"] = pd.to_numeric(df["alapterulet_nm"], errors="coerce")
    df = df[df["alapterulet_nm"] > 5].copy()  # Érvénytelen sorok szűrése

    if "erkely_nm" in df.columns:
        df["erkely_nm"] = pd.to_numeric(df["erkely_nm"], errors="coerce").fillna(0.0)
    else:
        df["erkely_nm"] = 0.0

    df["van_erkely"] = (df["erkely_nm"] > 0).astype(int)
    # Hedonikus korrigált alapterület: alapterület + 0.5 * erkély
    df["korrigalt_alapterulet_nm"] = df["alapterulet_nm"] + 0.5 * df["erkely_nm"]

    if "szobaszam_osszes" in df.columns:
        df["szobaszam_osszes"] = pd.to_numeric(df["szobaszam_osszes"], errors="coerce").fillna(2.0)
    else:
        df["szobaszam_osszes"] = 2.0
    df["atlagos_szobameret_nm"] = df["alapterulet_nm"] / np.maximum(1.0, df["szobaszam_osszes"])

    # 3. Pénzügyi mutatók (Ár, Ár/m², Log transzformációk)
    if "price_huf" not in df.columns and "price_million_huf" in df.columns:
        df["price_million_huf"] = pd.to_numeric(df["price_million_huf"], errors="coerce")
        df["price_huf"] = df["price_million_huf"] * 1e6
    elif "price_huf" in df.columns:
        df["price_huf"] = pd.to_numeric(df["price_huf"], errors="coerce")
        # Ha véletlenül millióban adták meg
        if df["price_huf"].median() < 1000:
            df["price_huf"] = df["price_huf"] * 1e6
        df["price_million_huf"] = df["price_huf"] / 1e6
    else:
        raise KeyError(
            "Hiányzó kötelező mező: ár (price_huf / price_million_huf) nem azonosítható!"
        )

    df["ar_millio_ft"] = df["price_huf"] / 1e6
    df["ar_ezer_ft_ho"] = df["price_huf"] / 1000.0
    df["nm_ar_huf"] = df["price_huf"] / df["alapterulet_nm"]
    df["log_ar"] = np.log(np.maximum(1.0, df["price_huf"]))
    df["log_nm_ar"] = np.log(np.maximum(1.0, df["nm_ar_huf"]))

    # Ár outlier dummy: adaptív a piac árszintjéhez (Budapest vs Bécs / nemzetközi)
    med_nm_ar = (
        df[df["listing_type"] == "elado"]["nm_ar_huf"].median()
        if (df["listing_type"] == "elado").any()
        else 1000000.0
    )
    if med_nm_ar > 1800000.0:  # Bécsi / magas árszintű piac (400 HUF/EUR esetén)
        min_cutoff, max_cutoff = 800000.0, 6500000.0
    else:  # Budapesti / hazai piac
        min_cutoff, max_cutoff = 350000.0, 2500000.0

    df["is_ar_outlier"] = (
        (df["listing_type"] == "elado")
        & ((df["nm_ar_huf"] < min_cutoff) | (df["nm_ar_huf"] > max_cutoff))
    ).astype(int)

    # 4. Állapotkód (1..6) és dummyk
    if "allapot_kod" not in df.columns:
        if "allapot" in df.columns:
            df["allapot_kod"] = df["allapot"].apply(parse_condition_to_code)
        else:
            df["allapot_kod"] = 3
    else:
        df["allapot_kod"] = pd.to_numeric(df["allapot_kod"], errors="coerce").fillna(3).astype(int)

    df["is_felujitando"] = (df["allapot_kod"] <= 2).astype(int)
    df["is_ujszeru_vagy_uj"] = (df["allapot_kod"] >= 5).astype(int)

    # 5. Épületfizikai dummyk
    if "ingatlan_altipus" not in df.columns or df["ingatlan_altipus"].isna().all():
        if "epites_eve_kategoria" in df.columns:
            df["ingatlan_altipus"] = df["epites_eve_kategoria"]

    altipus_str = (
        df["ingatlan_altipus"].astype(str).str.lower() if "ingatlan_altipus" in df.columns else ""
    )
    df["is_panel"] = altipus_str.str.contains("panel", na=False).astype(int)
    df["is_tegla"] = altipus_str.str.contains("tegla|tégla|altbau|neubau|ziegel", na=False).astype(
        int
    )
    if (df["is_tegla"] == 0).all() and (df["is_panel"] == 0).all():
        df["is_tegla"] = 1
    elif "is_panel" in df.columns and (df["is_panel"] == 1).any() and (df["is_tegla"] == 0).all():
        df["is_tegla"] = (df["is_panel"] == 0).astype(int)

    lift_str = df["lift"].astype(str).str.lower() if "lift" in df.columns else ""
    df["has_lift"] = lift_str.str.contains("van|igen|1|ja", na=False).astype(int)

    klima_str = df["klima"].astype(str).str.lower() if "klima" in df.columns else ""
    df["has_klima"] = klima_str.str.contains("van|igen|1|ja", na=False).astype(int)

    # 5/b. Fűtés dummyk és költségmutatók
    futes_str = df["futes"].astype(str).str.lower() if "futes" in df.columns else ""
    df["has_tavfutes"] = futes_str.str.contains("fernw|tavfutes|távfűtés", na=False).astype(int)
    df["has_konvektor"] = futes_str.str.contains("gas|gaz|gáz|konvektor", na=False).astype(int)
    df["has_megujulo"] = futes_str.str.contains(
        "waermepumpe|wärmepumpe|erdwaerme|erdwärme|szolar|solar|megujulo|megújuló|hoszivattyu|hőszivattyú",
        na=False,
    ).astype(int)

    if "kozos_koltseg_eur" in df.columns and (
        "kozos_koltseg_huf" not in df.columns or df["kozos_koltseg_huf"].isna().all()
    ):
        df["kozos_koltseg_huf"] = pd.to_numeric(df["kozos_koltseg_eur"], errors="coerce") * 400.0
    if "rezsikoltseg_eur" in df.columns and (
        "rezsikoltseg_huf" not in df.columns or df["rezsikoltseg_huf"].isna().all()
    ):
        df["rezsikoltseg_huf"] = pd.to_numeric(df["rezsikoltseg_eur"], errors="coerce") * 400.0

    # Emelet dummyk
    emelet_str = df["emelet"].astype(str).str.lower() if "emelet" in df.columns else ""
    emelet_sz = (
        pd.to_numeric(df["emelet_szam"], errors="coerce")
        if "emelet_szam" in df.columns
        else pd.Series(np.nan, index=df.index)
    )
    szintek_sz = (
        pd.to_numeric(df["epulet_szintjei_szam"], errors="coerce")
        if "epulet_szintjei_szam" in df.columns
        else pd.Series(np.nan, index=df.index)
    )

    df["is_foldszint"] = (
        emelet_str.str.contains("foldszint|fsz|erdgeschoss|\\beg\\b", na=False) | (emelet_sz == 0)
    ).astype(int)

    df["is_zaroszint"] = (
        emelet_str.str.contains("zaroszint|tetoter|legfelso|dg|dachgeschoss", na=False)
        | ((emelet_sz >= szintek_sz) & (emelet_sz > 1) & szintek_sz.notna())
    ).astype(int)

    # 6. Épület kora 2026-ban
    if "epites_eve" in df.columns:
        df["epites_eve"] = pd.to_numeric(df["epites_eve"], errors="coerce")
        df["epulet_kora_ev"] = np.maximum(0, 2026 - df["epites_eve"].fillna(1980)).astype(int)
    else:
        df["epites_eve"] = np.nan
        df["epulet_kora_ev"] = 45  # Medián épületkor becslés

    # 7. Városrész fallback
    if "varosresz" not in df.columns or df["varosresz"].isna().all():
        df["varosresz"] = "Központi körzet"
    else:
        df["varosresz"] = df["varosresz"].fillna("Egyéb")

    # 8. Cím automatikus összeállítása és kinyerése ha hiányos
    if "cim_teljes" not in df.columns:
        df["cim_teljes"] = ""
    else:
        df["cim_teljes"] = df["cim_teljes"].fillna("").astype(str)

    needs_addr = (df["cim_teljes"].str.strip() == "") | (
        df["cim_teljes"].str.lower().isin(["nan", "none"])
    )
    if needs_addr.any():
        if "utca" in df.columns and not df["utca"].isna().all():
            v_series = (
                df["varos"].fillna("Budapest").astype(str)
                if "varos" in df.columns
                else pd.Series("Budapest", index=df.index)
            )
            k_series = (
                df["kerulet"]
                .fillna("")
                .astype(str)
                .apply(
                    lambda k: (
                        f"{k}. kerület"
                        if k and not any(w in str(k).lower() for w in ["ker", "district"])
                        else str(k)
                    )
                )
                if "kerulet" in df.columns
                else pd.Series("", index=df.index)
            )
            u_series = df["utca"].fillna("").astype(str)
            h_series = (
                df["hazszam"].fillna("").astype(str)
                if "hazszam" in df.columns
                else pd.Series("", index=df.index)
            )

            synth = (
                v_series
                + ", "
                + k_series.apply(lambda x: x + ", " if x else "")
                + u_series
                + " "
                + h_series
            )
            synth = (
                synth.str.strip()
                .str.replace(r"\s+", " ", regex=True)
                .str.replace(r",\s*,", ",", regex=True)
            )
            df.loc[needs_addr, "cim_teljes"] = synth[needs_addr]
            logger.info(
                f"Címek automatikusan összeállítva komponensekből ({needs_addr.sum()} sor)."
            )
        elif "leiras" in df.columns or "title" in df.columns:
            text_src = (
                (df["title"].fillna("") if "title" in df.columns else "")
                + " "
                + (df["leiras"].fillna("") if "leiras" in df.columns else "")
            ).astype(str)
            street_pat = re.compile(
                r"([A-ZÁÉÍÓÖŐÚÜŰ][a-záéíóöőúüűA-ZÁÉÍÓÖŐÚÜŰ\s\.\-]{2,25}(?:utca|út|útja|tér|tere|körút|krt|fasor|sétány|sor|köz|rakpart)(?:\s+\d+[a-zA-Z\/\-]*)?)",
                re.IGNORECASE,
            )
            extracted = [
                street_pat.search(str(t)).group(1).strip() if street_pat.search(str(t)) else ""
                for t in text_src
            ]
            if any(extracted):
                synth_nlp = [
                    f"Budapest, {e}" if e and "budapest" not in e.lower() else e for e in extracted
                ]
                synth_s = pd.Series(synth_nlp, index=df.index)
                can_fill = needs_addr & (synth_s != "")
                df.loc[can_fill, "cim_teljes"] = synth_s[can_fill]
                logger.info(
                    f"Címek automatikusan kinyerve szövegből regex-szel ({can_fill.sum()} sor)."
                )

        still_needs = (df["cim_teljes"].str.strip() == "") | (
            df["cim_teljes"].str.lower().isin(["nan", "none"])
        )
        if still_needs.any():
            def_varos = (
                df["varos"].fillna("Wien" if "varos" in df.columns else "Budapest").astype(str)
                if "varos" in df.columns
                else pd.Series("Település", index=df.index)
            )
            def_vr = (
                df["varosresz"].fillna("").astype(str)
                if "varosresz" in df.columns
                else pd.Series("", index=df.index)
            )
            fallback_addr = (def_varos + ", " + def_vr).str.strip(", ")
            df.loc[still_needs, "cim_teljes"] = fallback_addr[still_needs]

    logger.info("Feature Engineering sikeresen lefutott.")
    return df


# ==============================================================================
# 3. Geokódolás és Gyorsítótár (Nominatim + geocode_cache.json)
# ==============================================================================
def load_geocode_cache(cache_path: str = CACHE_PATH) -> dict:
    """Helyi geokódolási gyorsítótár beolvasása."""
    if os.path.exists(cache_path):
        try:
            with open(cache_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Nem sikerült betölteni a geokódolási cache-t: {e}")
    return {}


def save_geocode_cache(cache: dict, cache_path: str = CACHE_PATH):
    """Geokódolási gyorsítótár tartós mentése lemezre."""
    os.makedirs(os.path.dirname(cache_path), exist_ok=True)
    try:
        with open(cache_path, "w", encoding="utf-8") as f:
            json.dump(cache, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"Hiba a cache mentésekor: {e}")


def normalize_addr_for_cache(addr: str) -> List[str]:
    """Címváltozatok előállítása a gyorsítótárban való robusztus kereséshez."""
    candidates = [addr.strip()]
    c1 = re.sub(
        r"Budapest\s+[IVXLCDM]+\.\s*kerület,?\s*", "Budapest, ", addr, flags=re.IGNORECASE
    ).strip()
    candidates.append(c1)
    c2 = re.sub(r"\s*[IVXLCDM]+\.\s*kerület,?\s*", " ", addr, flags=re.IGNORECASE).strip()
    candidates.append(c2)
    return list(dict.fromkeys(candidates))


def geocode_listings(
    df: pd.DataFrame, address_col: str = "cim_teljes", cache_path: str = CACHE_PATH
) -> pd.DataFrame:
    """Ingatlanok geokódolása helyi gyorsítótárral és Nominatim fallbackkel."""
    df = df.copy()
    cache = load_geocode_cache(cache_path)

    if "geokodolt_lat" not in df.columns:
        df["geokodolt_lat"] = np.nan
    if "geokodolt_lon" not in df.columns:
        df["geokodolt_lon"] = np.nan
    if "minta_garantalt_pontos" not in df.columns:
        df["minta_garantalt_pontos"] = 0

    geolocator = None
    if HAS_GEOPY:
        geolocator = Nominatim(user_agent="ifk-tdk-real-estate-pipeline-2026", timeout=10)

    # 1. Koordináták feltöltése meglévő értékekből és cache-ből
    cache_hits = 0
    to_query = []

    for idx, row in df.iterrows():
        # Ha már van érvényes koordinátája
        if pd.notna(row["geokodolt_lat"]) and pd.notna(row["geokodolt_lon"]):
            df.at[idx, "minta_garantalt_pontos"] = 1
            continue

        addr = str(row.get(address_col, "")).strip()
        if not addr or addr.lower() in ["nan", "none", ""]:
            continue

        # Címváltozatok ellenőrzése a cache-ben
        found_entry = None
        for cand in normalize_addr_for_cache(addr):
            if cand in cache:
                found_entry = cache[cand]
                break

        if found_entry:
            df.at[idx, "geokodolt_lat"] = found_entry["lat"]
            df.at[idx, "geokodolt_lon"] = found_entry["lon"]
            # Házszám precizitás: ha a cím tartalmaz számot, garantált pontos tetőpont
            has_house_num = bool(re.search(r"\d+", addr))
            df.at[idx, "minta_garantalt_pontos"] = 1 if has_house_num else 0
            cache_hits += 1
        else:
            to_query.append((idx, addr))

    logger.info(
        f"Geokódolás státusz: {cache_hits} találat a helyi cache-ből. Lekérdezendő új címek: {len(to_query)} db."
    )

    # 2. Új címek lekérdezése Nominatim-mal (rate limited 1.1s)
    if to_query and geolocator:
        logger.info(
            f"Új címek geokódolása Nominatim-mal (várható idő: ~{len(to_query) * 1.1:.0f} mp)..."
        )
        updated_cache = False
        for i, (idx, addr) in enumerate(to_query):
            query_str = (
                addr
                if "budapest" in addr.lower() or "magyarorszag" in addr.lower()
                else f"Budapest, {addr}"
            )
            try:
                loc = geolocator.geocode(query_str)
                if loc:
                    df.at[idx, "geokodolt_lat"] = loc.latitude
                    df.at[idx, "geokodolt_lon"] = loc.longitude
                    has_house_num = bool(re.search(r"\d+", addr))
                    df.at[idx, "minta_garantalt_pontos"] = 1 if has_house_num else 0
                    cache[addr] = {
                        "lat": loc.latitude,
                        "lon": loc.longitude,
                        "display": loc.address,
                    }
                    updated_cache = True
            except Exception as e:
                logger.warning(f"Geokódolási hiba ennél: '{addr}' -> {e}")
            time.sleep(1.1)

            if (i + 1) % 10 == 0:
                logger.info(f"  Feldolgozva: {i + 1}/{len(to_query)} cím...")

        if updated_cache:
            save_geocode_cache(cache, cache_path)
            logger.info("Gyorsítótár (geocode_cache.json) frissítve.")

    pontos_n = int((df["minta_garantalt_pontos"] == 1).sum())
    logger.info(
        f"Összesen {pontos_n} db garantált pontos tetőpont (minta_garantalt_pontos=1) az N={len(df)} mintából."
    )
    return df


# ==============================================================================
# 4. Vasúti Térbeli Elemzés (A Két Szigorú Sávrendszer Számítása)
# ==============================================================================
def load_osm_railway_data(
    osm_rail_path: Optional[str] = None, df: Optional[pd.DataFrame] = None
) -> Tuple[Optional[gpd.GeoDataFrame], Optional[gpd.GeoDataFrame], Optional[gpd.GeoDataFrame]]:
    """OSM vasútvonalak, vasútállomások és metróállomások betöltése (intelligens Budapest / Bécs detektálással)."""
    rails_gdf = None
    stations_gdf = None
    metro_gdf = None

    # Automatikus fájlkiválasztás ha nincs explicit útvonal
    default_rail_file = os.path.join(PROJECT_ROOT, "data", "raw", "osm_rails.json")
    is_vienna = False
    if df is not None and "geokodolt_lon" in df.columns and df["geokodolt_lon"].notna().any():
        med_lon = df["geokodolt_lon"].median()
        if 15.0 <= med_lon < 18.0:
            is_vienna = True
            vienna_file = os.path.join(
                PROJECT_ROOT, "data", "raw", "osm_rails_wien_nordbahnhof.json"
            )
            if os.path.exists(vienna_file):
                default_rail_file = vienna_file

    rail_file = osm_rail_path or default_rail_file
    logger.info(f"Vasúti OSM hálózat betöltése: {rail_file}")

    if os.path.exists(rail_file):
        try:
            with open(rail_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            lines = []
            station_points = []
            station_names = []
            metro_points = []
            metro_names = []

            for el in data.get("elements", []):
                # Vonalak (vágányok)
                if el.get("type") == "way" and "geometry" in el and len(el["geometry"]) >= 2:
                    coords = [(p["lon"], p["lat"]) for p in el["geometry"]]
                    lines.append(LineString(coords))
                # Állomások
                tags = el.get("tags", {})
                if tags.get("railway") in ["station", "halt"]:
                    if (
                        tags.get("station") == "miniature"
                        or tags.get("railway") == "miniature"
                        or "liliput" in tags.get("name", "").lower()
                    ):
                        continue
                    pt = None
                    if el.get("type") == "node":
                        pt = Point(el["lon"], el["lat"])
                    elif el.get("type") == "way" and "geometry" in el:
                        pts = [(p["lon"], p["lat"]) for p in el["geometry"]]
                        pt = LineString(pts).centroid

                    if pt is not None:
                        st_name = tags.get("name", "Vasútállomás")
                        if (
                            tags.get("station") == "subway"
                            or tags.get("subway") == "yes"
                            or tags.get("operator") == "Wiener Linien"
                        ):
                            metro_points.append(pt)
                            metro_names.append(st_name)
                        else:
                            station_points.append(pt)
                            station_names.append(st_name)

            if lines:
                rails_gdf = gpd.GeoDataFrame(geometry=lines, crs="EPSG:4326")
            if station_points:
                stations_gdf = gpd.GeoDataFrame(
                    {"name": station_names}, geometry=station_points, crs="EPSG:4326"
                )
            if metro_points:
                metro_gdf = gpd.GeoDataFrame(
                    {"name": metro_names}, geometry=metro_points, crs="EPSG:4326"
                )
            logger.info(
                f"OSM vasúti elemek sikeresen betöltve: {len(lines)} vágányszakasz, {len(station_points)} vasútállomás, {len(metro_points)} metróállomás."
            )
        except Exception as e:
            logger.warning(f"Hiba az OSM vasúti fájl feldolgozásakor: {e}")

    # Fallback vasútállomások ha nem volt állomás a fájlban
    if stations_gdf is None or len(stations_gdf) == 0:
        if is_vienna:
            known_stations = [
                ("Wien Praterstern (Nordbahnhof)", 48.2188, 16.3924),
                ("Wien Traisengasse", 48.2325, 16.3881),
                ("Wien Handelskai", 48.2422, 16.3850),
                ("Wien Franz-Josefs-Bahnhof", 48.2267, 16.3611),
                ("Wien Mitte", 48.2056, 16.3842),
            ]
        else:
            known_stations = [
                ("Kőbánya felső vasútállomás", 47.4936, 19.1278),
                ("Kőbánya alsó vasútállomás", 47.4851, 19.1309),
                ("Kőbánya-Kispest vasútállomás", 47.4644, 19.1492),
                ("Rákos vasútállomás", 47.4997, 19.1678),
            ]
        pts = [Point(lon, lat) for _, lat, lon in known_stations]
        names = [n for n, _, _ in known_stations]
        stations_gdf = gpd.GeoDataFrame({"name": names}, geometry=pts, crs="EPSG:4326")

    return rails_gdf, stations_gdf, metro_gdf


def compute_railway_and_spatial_metrics(
    df: pd.DataFrame, osm_rail_path: Optional[str] = None
) -> pd.DataFrame:
    """A szigorúan rögzített két sávrendszer kiszámítása és csatolása."""
    df = df.copy()
    rails_gdf, stations_gdf, metro_gdf = load_osm_railway_data(osm_rail_path, df=df)

    # Inicializálás NaN / default értékekkel
    df["tavolsag_vasut_m"] = np.nan
    df["vasut_zona"] = pd.NA
    df["is_vasut_immisszio_150m"] = 0

    df["tavolsag_vasut_halozati_m"] = np.nan
    df["legkozelebbi_vasut"] = pd.NA
    df["menetido_vasut_gyalog_perc"] = np.nan
    df["vasut_5p_seta"] = 0
    df["vasut_10p_seta"] = 0
    df["vasut_15p_seta"] = 0

    # Csak a koordinátával rendelkező sorokra számolunk
    valid_mask = (
        (df["minta_garantalt_pontos"] == 1)
        & df["geokodolt_lat"].notna()
        & df["geokodolt_lon"].notna()
    )
    if not valid_mask.any():
        logger.warning(
            "Nincs koordinátával rendelkező ingatlan, a térbeli távolságok nem számolhatók!"
        )
        return df

    # Adaptív metrikus vetület kiválasztása (UTM 33N Bécsre, EOV Magyarországra)
    med_lon = float(df.loc[valid_mask, "geokodolt_lon"].median())
    med_lat = float(df.loc[valid_mask, "geokodolt_lat"].median())
    if 15.0 <= med_lon < 18.0 and 46.5 <= med_lat <= 49.5:
        metric_crs = "EPSG:32633"  # UTM Zone 33N (Ausztria / Bécs pontos metrikus vetület)
        logger.info(
            f"Osztrák/Bécsi lokáció észlelve ({med_lat:.3f}, {med_lon:.3f}) -> Metrikus vetület: {metric_crs} (UTM 33N)"
        )
    elif 16.0 <= med_lon <= 23.5 and 45.5 <= med_lat <= 48.8:
        metric_crs = "EPSG:23700"  # EOV (Magyarország)
        logger.info(
            f"Magyarországi lokáció észlelve ({med_lat:.3f}, {med_lon:.3f}) -> Metrikus vetület: {metric_crs} (EOV)"
        )
    else:
        metric_crs = "EPSG:3857"

    prop_points = gpd.points_from_xy(
        df.loc[valid_mask, "geokodolt_lon"], df.loc[valid_mask, "geokodolt_lat"], crs="EPSG:4326"
    )
    prop_gdf = gpd.GeoDataFrame(geometry=prop_points, index=df.loc[valid_mask].index).to_crs(
        metric_crs
    )

    # --------------------------------------------------------------------------
    # SÁV 1: Immissziós távolság a legközelebbi vasúti vágánytól (0-150-300-500-1000-2000m)
    # --------------------------------------------------------------------------
    if rails_gdf is not None and len(rails_gdf) > 0:
        rails_metric = rails_gdf.to_crs(metric_crs)
        # Egységesített geometriai unió a gyors minimum-távolság kereséshez
        rail_geom_union = (
            rails_metric.geometry.union_all()
            if hasattr(rails_metric.geometry, "union_all")
            else rails_metric.geometry.unary_union
        )
        distances_to_tracks = prop_gdf.geometry.distance(rail_geom_union)
        df.loc[valid_mask, "tavolsag_vasut_m"] = distances_to_tracks.round(1)
    else:
        # Fallback ha nincs síngeometria: állomásoktól mérjük
        stations_metric = stations_gdf.to_crs(metric_crs)
        st_union = (
            stations_metric.geometry.union_all()
            if hasattr(stations_metric.geometry, "union_all")
            else stations_metric.geometry.unary_union
        )
        df.loc[valid_mask, "tavolsag_vasut_m"] = prop_gdf.geometry.distance(st_union).round(1)

    # Kategorizálás a kánoni sávokba
    df.loc[valid_mask, "vasut_zona"] = pd.cut(
        df.loc[valid_mask, "tavolsag_vasut_m"],
        bins=VASUT_IMMISSZIO_BINS,
        labels=VASUT_IMMISSZIO_LABELS,
    )
    df.loc[valid_mask, "is_vasut_immisszio_150m"] = (
        df.loc[valid_mask, "tavolsag_vasut_m"] < 150.0
    ).astype(int)

    # --------------------------------------------------------------------------
    # SÁV 2: Gyalogos izokrónok az állomástól (0-375-750-1125m, 1.25 m/s)
    # --------------------------------------------------------------------------
    if stations_gdf is not None and len(stations_gdf) > 0:
        stations_metric = stations_gdf.to_crs(metric_crs)
        for idx in prop_gdf.index:
            pt = prop_gdf.loc[idx, "geometry"]
            dists = stations_metric.geometry.distance(pt)
            min_idx = dists.idxmin()
            euc_dist = dists.loc[min_idx]
            net_dist = euc_dist * DETOUR_FACTOR  # 1.25 kerülő faktor hálózati közelítéshez
            st_name = stations_metric.loc[min_idx, "name"]

            df.at[idx, "tavolsag_vasut_halozati_m"] = round(net_dist, 1)
            df.at[idx, "legkozelebbi_vasut"] = st_name
            df.at[idx, "menetido_vasut_gyalog_perc"] = round(net_dist / WALK_SPEED_M_PER_MIN, 1)
            df.at[idx, "vasut_5p_seta"] = 1 if net_dist <= 375.0 else 0
            df.at[idx, "vasut_10p_seta"] = 1 if net_dist <= 750.0 else 0
            df.at[idx, "vasut_15p_seta"] = 1 if net_dist <= 1125.0 else 0

    # Metró / U-Bahn izokrónok számítása ha elérhető
    if metro_gdf is not None and len(metro_gdf) > 0:
        metro_metric = metro_gdf.to_crs(metric_crs)
        df.loc[valid_mask, "tavolsag_metro_halozati_m"] = np.nan
        df.loc[valid_mask, "metro_5p_seta"] = 0
        df.loc[valid_mask, "metro_10p_seta"] = 0
        df.loc[valid_mask, "metro_15p_seta"] = 0
        for idx in prop_gdf.index:
            pt = prop_gdf.loc[idx, "geometry"]
            dists = metro_metric.geometry.distance(pt)
            min_dist = dists.min()
            net_dist = min_dist * DETOUR_FACTOR
            df.at[idx, "tavolsag_metro_halozati_m"] = round(net_dist, 1)
            df.at[idx, "metro_5p_seta"] = 1 if net_dist <= 375.0 else 0
            df.at[idx, "metro_10p_seta"] = 1 if net_dist <= 750.0 else 0
            df.at[idx, "metro_15p_seta"] = 1 if net_dist <= 1125.0 else 0

    logger.info("Vasúti térbeli sávok számítása sikeresen befejeződött:")
    logger.info(f"  <150m Immissziós ingatlanok: {(df['is_vasut_immisszio_150m'] == 1).sum()} db")
    logger.info(f"  5p séta (<=375m) ingatlanok: {(df['vasut_5p_seta'] == 1).sum()} db")
    logger.info(f"  10p séta (<=750m) ingatlanok: {(df['vasut_10p_seta'] == 1).sum()} db")
    logger.info(f"  15p séta (<=1125m) ingatlanok: {(df['vasut_15p_seta'] == 1).sum()} db")

    return df


# ==============================================================================
# 5. Sémavalidáció és Kimenet Mentése
# ==============================================================================
def validate_against_schema(df: pd.DataFrame, schema: dict) -> pd.DataFrame:
    """DataFrame ellenőrzése és formázása a data/schema.yaml előírásai szerint."""
    df = df.copy()
    req_fields = schema.get("required", {})
    opt_fields = schema.get("optional", {})

    # Kötelező mezők ellenőrzése
    missing = set(req_fields.keys()) - set(df.columns)
    if missing:
        raise ValueError(f"Sémavalidációs hiba! Hiányzó kötelező mezők: {missing}")

    # Opcionális mezők feltöltése NA-val ha nincsenek
    for col in opt_fields.keys():
        if col not in df.columns:
            df[col] = pd.NA

    # Típuskonverziók végrehajtása
    all_fields = {**req_fields, **opt_fields}
    for col, expected_type in all_fields.items():
        if col not in df.columns:
            continue
        try:
            if expected_type == "float64":
                df[col] = pd.to_numeric(df[col], errors="coerce").astype("float64")
            elif expected_type == "int64":
                df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype("int64")
            elif expected_type == "object":
                df[col] = df[col].astype("object")
        except Exception as e:
            logger.warning(f"Figyelmeztetés a(z) '{col}' típuskonverziójánál: {e}")

    return df


def save_processed_outputs(
    df: pd.DataFrame, name: str, output_dir: str = "data/processed"
) -> Tuple[str, str]:
    """Számított Parquet és pontos GeoJSON mentése."""
    os.makedirs(output_dir, exist_ok=True)
    parquet_path = os.path.join(output_dir, f"{name}_szamitott_master.parquet")
    geojson_path = os.path.join(output_dir, f"{name}_pontos.geojson")

    df_save = df.copy()
    # Parquet kompatibilitás: vegyes típusú objektumoszlopok egységesítése stringgé
    for col in df_save.columns:
        if df_save[col].dtype == "object" or str(df_save[col].dtype) == "category":
            df_save[col] = df_save[col].apply(lambda x: str(x) if pd.notna(x) else None)

    # 1. Parquet mentés
    df_save.to_parquet(parquet_path, index=False)
    logger.info(
        f"[OK] Számított master Parquet elmentve: {parquet_path} ({len(df_save)} sor, {len(df_save.columns)} oszlop)"
    )

    # 2. GeoJSON mentés (csak garantált koordinátával bíró tetőpontok)
    pontos_df = df_save[
        (df_save["minta_garantalt_pontos"] == 1)
        & df_save["geokodolt_lat"].notna()
        & df_save["geokodolt_lon"].notna()
    ].copy()
    if len(pontos_df) > 0:
        gdf = gpd.GeoDataFrame(
            pontos_df,
            geometry=gpd.points_from_xy(pontos_df["geokodolt_lon"], pontos_df["geokodolt_lat"]),
            crs="EPSG:4326",
        )
        gdf.to_file(geojson_path, driver="GeoJSON")
        logger.info(f"[OK] Pontos mintavételi GeoJSON elmentve: {geojson_path} ({len(gdf)} pont)")
    else:
        logger.warning("Nem volt pontos koordinátával rendelkező ingatlan, GeoJSON nem készült.")

    return parquet_path, geojson_path


def parse_mapping_arg(arg_val: Optional[str]) -> Optional[dict]:
    """Mapping argumentum feloldása (JSON string, vagy YAML/JSON fájl útvonal)."""
    if not arg_val:
        return None
    if os.path.exists(arg_val):
        if arg_val.endswith((".yaml", ".yml")):
            with open(arg_val, "r", encoding="utf-8") as f:
                return yaml.safe_load(f)
        with open(arg_val, "r", encoding="utf-8") as f:
            return json.load(f)
    return json.loads(arg_val)


def inspect_mapping(
    raw_df: pd.DataFrame, custom_mapping: Optional[dict] = None, name: str = "uj_terulet"
) -> pd.DataFrame:
    """Oszlopok felülvizsgálata: részletes ellenőrző táblázat és YAML sablon generálása."""
    print(f"\n{'=' * 75}")
    print(f"[INFO] OSZLOPBESOROLAS ES ELOZETES FELULVIZSGALAT: [{name}]")
    print(f"{'=' * 75}")

    # Heurisztika futtatása
    _ = auto_map_columns(raw_df, custom_mapping)

    # Jelentés összeállítása
    report_rows = []

    # Megkeressük, melyik forrás oszlop hova került
    cleaned_src_cols = {col: strip_accents(col).replace(" ", "_") for col in raw_df.columns}
    for col in raw_df.columns:
        # Minták kinyerése
        samples = [str(x) for x in raw_df[col].dropna().unique()[:3]]
        sample_str = ", ".join(samples) if samples else "(ures)"

        # Cél oszlop megállapítása
        target = None
        if custom_mapping and col in custom_mapping:
            target = custom_mapping[col]
            status = "[OK] Egyeni Mapping (YAML/JSON)"
        else:
            for canon, synonyms in COLUMN_SYNONYMS.items():
                for syn in synonyms:
                    if cleaned_src_cols[col] == strip_accents(syn).replace(" ", "_"):
                        target = canon
                        break
                if target:
                    break
            status = "[AUTO] Automata Felismeres" if target else "[SKIP] Nem besorolt (kihagyva)"

        report_rows.append(
            {
                "Forras Oszlop (Excel)": col,
                "Besorolt Kanonikus Nev": target or "-",
                "Statusz": status,
                "Mintaertekek": sample_str[:40],
            }
        )

    rep_df = pd.DataFrame(report_rows)
    print(rep_df.to_string(index=False))

    # YAML sablon generálása mappings/ mappába
    mappings_dir = os.path.join(PROJECT_ROOT, "data", "mappings")
    os.makedirs(mappings_dir, exist_ok=True)
    yaml_template_path = os.path.join(mappings_dir, f"{name}_mapping.yaml")

    yaml_content = {}
    for r in report_rows:
        if r["Besorolt Kanonikus Nev"] != "-":
            yaml_content[r["Forras Oszlop (Excel)"]] = r["Besorolt Kanonikus Nev"]

    with open(yaml_template_path, "w", encoding="utf-8") as f:
        yaml.dump(yaml_content, f, allow_unicode=True, default_flow_style=False)

    print(f"\n{'=' * 75}")
    print("[FILE] Szerkesztheto felulbiralati sablon elmentve:")
    print(f"   -> {yaml_template_path}")
    print(
        "Ha barmit modositani szeretnel, szerkeszd ezt a YAML fajlt, majd futtasd a pipeline-t igy:"
    )
    print(
        f"   python scripts/preprocess_new_data.py -i <fajl> -n {name} -m data/mappings/{name}_mapping.yaml"
    )
    print(f"{'=' * 75}\n")
    return rep_df


# ==============================================================================
# Fő Belépési Pont (CLI Orchestration)
# ==============================================================================
def run_pipeline(
    input_path: str,
    name: str,
    input_type: Optional[str] = None,
    custom_mapping: Optional[dict] = None,
    osm_rail_path: Optional[str] = None,
    dry_run: bool = False,
) -> Tuple[Optional[str], Optional[str]]:
    """Teljes előfeldolgozási folyamat futtatása."""
    logger.info(f"=== IFK-TDK 2026 Adatelőkészítési Pipeline Indítása: [{name}] ===")

    # 1. Beolvasás
    raw_df = load_raw_data(input_path, input_type)

    # 2. Ha csak felülvizsgálat (--dry-run)
    if dry_run:
        inspect_mapping(raw_df, custom_mapping, name)
        logger.info("Dry-run / Felülvizsgálat befejeződött, feldolgozás nem történt.")
        return None, None

    # 3. Oszlopillesztés
    mapped_df = auto_map_columns(raw_df, custom_mapping)

    # 4. Feature engineering
    feat_df = engineer_features(mapped_df)

    # 5. Geokódolás
    geo_df = geocode_listings(feat_df)

    # 6. Vasúti térbeli számítások (A 2 szigorú sávrendszer)
    spatial_df = compute_railway_and_spatial_metrics(geo_df, osm_rail_path)

    # 7. Sémavalidáció
    schema = load_schema()
    validated_df = validate_against_schema(spatial_df, schema)

    # 8. Mentés
    out_dir = os.path.join(PROJECT_ROOT, "data", "processed")
    parquet_p, geojson_p = save_processed_outputs(validated_df, name, out_dir)

    logger.info(f"=== Pipeline sikeresen befejeződött: [{name}] ===")
    return parquet_p, geojson_p


def main():
    parser = argparse.ArgumentParser(
        description="IFK-TDK 2026 Ingatlanpiaci Adatelőkészítő és Vasúti Elemző Pipeline"
    )
    parser.add_argument(
        "-i", "--input", required=True, help="Bemeneti nyers fájl útvonala (.xlsx, .csv, .json)"
    )
    parser.add_argument(
        "-n", "--name", required=True, help="Terület azonosítója (pl. 'ujhegy', 'zuglo', 'kobanya')"
    )
    parser.add_argument(
        "-t",
        "--input_type",
        choices=["excel", "csv", "json"],
        help="Bemeneti formátum felülbírálása",
    )
    parser.add_argument(
        "-m",
        "--mapping",
        help="Opcionális JSON string VAGY YAML/JSON mapping fájl útvonala felülbíráláshoz",
    )
    parser.add_argument("--osm_rails", help="Opcionális helyi OSM vasúti fájl útvonala")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Csak oszlopbesorolás ellenőrzése és YAML sablon generálása futtatás nélkül",
    )

    args = parser.parse_args()
    mapping_dict = parse_mapping_arg(args.mapping)

    run_pipeline(
        input_path=args.input,
        name=args.name,
        input_type=args.input_type,
        custom_mapping=mapping_dict,
        osm_rail_path=args.osm_rails,
        dry_run=args.dry_run,
    )


if __name__ == "__main__":
    main()
