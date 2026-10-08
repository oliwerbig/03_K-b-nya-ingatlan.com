# -*- coding: utf-8 -*-
"""
_utils.py — Közös segédmodul a TDK kutatási notebookok számára.
Minden notebook innen importálja az adatbetöltő és formázó függvényeket.
"""

import os
import sys
import warnings
import pandas as pd
import numpy as np


warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)

# === Útvonalak ===
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Keresés a felállított struktúrában: data/processed, data/raw
DATA_DIR_PROCESSED = os.path.join(_PROJECT_ROOT, "data", "processed")
if not os.path.exists(DATA_DIR_PROCESSED):
    for cand in [
        os.path.join(_PROJECT_ROOT, "data"),
        os.path.join(_PROJECT_ROOT, "01_data", "processed"),
        os.path.join(_PROJECT_ROOT, "Adathalmaz", "data"),
    ]:
        if os.path.exists(cand):
            DATA_DIR_PROCESSED = cand
            break

DATA_DIR_RAW = os.path.join(_PROJECT_ROOT, "data", "raw")
if not os.path.exists(DATA_DIR_RAW):
    for cand in [
        os.path.join(_PROJECT_ROOT, "data"),
        os.path.join(_PROJECT_ROOT, "01_data", "raw"),
    ]:
        if os.path.exists(cand):
            DATA_DIR_RAW = cand
            break

ADATHALMAZ_DIR = DATA_DIR_PROCESSED
GIS_DIR = os.path.join(_PROJECT_ROOT, "gis")
if not os.path.exists(GIS_DIR):
    GIS_DIR = os.path.join(_PROJECT_ROOT, "03_gis")

# === Többterületes Támogatás (Multi-Area Support) ===
AREAS_CONFIG_PATH = os.path.join(_PROJECT_ROOT, "data", "areas.yaml")


def load_areas_config() -> dict:
    """A data/areas.yaml konfigurációs állomány beolvasása."""
    import yaml

    if os.path.exists(AREAS_CONFIG_PATH):
        with open(AREAS_CONFIG_PATH, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    return {"areas": {}}


def _resolve_area(area=None):
    """area=None esetén az areas.yaml ``active_area`` értékét adja vissza.

    Visszafelé kompatibilitást biztosít a régi, egyterületes notebook-hívásokkal
    (pl. ``load_szamitott_master()``, ``get_map_center()``, ``render_area_header_html(df=...)``).
    """
    if area is not None:
        return area
    env_area = os.environ.get("TDK_ACTIVE_AREA")
    if env_area:
        return env_area
    cfg = load_areas_config()
    return cfg.get("active_area", "kobanya")


def list_available_areas() -> list:
    """Elérhető, feldolgozott területek listázása a data/processed mappából."""
    if not os.path.exists(DATA_DIR_PROCESSED):
        return []
    areas = []
    for f in os.listdir(DATA_DIR_PROCESSED):
        if f.endswith("_szamitott_master.parquet"):
            clean_name = f.replace("_szamitott_master.parquet", "")
            areas.append(clean_name)
    cfg = load_areas_config()
    for aid in cfg.get("areas", {}).keys():
        if aid not in areas and os.path.exists(
            os.path.join(DATA_DIR_PROCESSED, f"{aid}_szamitott_master.parquet")
        ):
            areas.append(aid)
    return sorted(list(set(areas))) if areas else []


def get_area_metadata(area: str = None) -> dict:
    """Az adott terület metaadatainak lekérdezése az areas.yaml konfigurációból."""
    area = _resolve_area(area)
    cfg = load_areas_config()
    return cfg.get("areas", {}).get(area, {"name": area, "id": area})


def load_all_areas_comparison(areas: list = None) -> pd.DataFrame:
    """Az összes elérhető (vagy megadott) terület számított adatainak összefűzése komparatív elemzéshez."""
    target_areas = areas or list_available_areas()
    frames = []
    for a in target_areas:
        try:
            df = load_szamitott_master(a).copy()
            meta = get_area_metadata(a)
            df["area_id"] = a
            df["area_name"] = meta.get("name", a)
            df["area_role"] = meta.get("role", "control" if a != "kobanya" else "primary")
            frames.append(df)
        except Exception as e:
            warnings.warn(f"Nem sikerült betölteni a(z) '{a}' területet: {e}")
    if not frames:
        raise ValueError("Egyetlen terület adathalmazát sem sikerült betölteni!")
    return pd.concat(frames, ignore_index=True)


def create_area_selector_widget(on_change_callback=None, default_area=None):
    """Interaktív IPyWidgets dropdown területválasztó a notebookok tetejére."""
    try:
        import ipywidgets as widgets

        avail = list_available_areas()
        val = default_area if default_area in avail else (avail[0] if avail else None)
        dd = widgets.Dropdown(
            options=avail,
            value=val,
            description="Aktív Terület:",
            style={"description_width": "110px"},
            layout=widgets.Layout(width="280px"),
        )

        def _on_change(change):
            if change.get("type") == "change" and change.get("name") == "value":
                if on_change_callback:
                    on_change_callback(change["new"])

        dd.observe(_on_change)
        return dd
    except ImportError:
        return None


def preview_mapping(file_path: str, custom_mapping: dict = None) -> pd.DataFrame:
    """Új nyers adathalmaz oszlopbesorolásának interaktív felülvizsgálata és sablongenerálás."""
    scripts_dir = os.path.join(_PROJECT_ROOT, "scripts")
    if scripts_dir not in sys.path:
        sys.path.append(scripts_dir)
    try:
        from preprocess_new_data import load_raw_data, inspect_mapping

        raw_df = load_raw_data(file_path)
        base_name = os.path.splitext(os.path.basename(file_path))[0]
        return inspect_mapping(raw_df, custom_mapping, name=base_name)
    except Exception as e:
        print(f"Hiba az oszlopok ellenőrzésekor: {e}")
        return pd.DataFrame()


# === Adatbetöltő függvények ===


def load_szamitott_master(area: str = None):
    """A számított master adathalmaz betöltése a megadott területről."""
    target_area = _resolve_area(area)
    cfg = load_areas_config()
    target_path = None
    if cfg and "areas" in cfg and target_area in cfg["areas"]:
        rel_p = cfg["areas"][target_area].get("data", {}).get("master_parquet")
        if rel_p:
            cand = os.path.join(_PROJECT_ROOT, rel_p)
            if os.path.exists(cand):
                target_path = cand
    if not target_path:
        for fname in [
            f"{target_area}_szamitott_master.parquet",
            f"{target_area}_ingatlan_szamitott_master.parquet",
        ]:
            for d in [DATA_DIR_PROCESSED, ADATHALMAZ_DIR]:
                cand = os.path.join(d, fname)
                if os.path.exists(cand):
                    target_path = cand
                    break
            if target_path:
                break
    if not target_path:
        raise FileNotFoundError(
            f"Nem található számított adathalmaz a(z) '{target_area}' területhez!"
        )
    df = pd.read_parquet(target_path)
    if "vasut_zona" not in df.columns and "tavolsag_vasut_m" in df.columns:
        df["vasut_zona"] = pd.cut(
            df["tavolsag_vasut_m"], bins=VASUT_IMMISSZIO_BINS, labels=VASUT_IMMISSZIO_LABELS
        )
    return df


def load_nyers_master(area: str = None):
    """A nyers (kapart) master adathalmaz."""
    target_area = _resolve_area(area)
    if target_area == "kobanya":
        path = os.path.join(DATA_DIR_RAW, "kobanya_ingatlan_nyers_master.db")
        import sqlite3

        conn = sqlite3.connect(path)
        df = pd.read_sql("SELECT * FROM listings", conn)
        conn.close()
        return df
    # Új területeknél nyers excel/csv keresése
    for cand in [
        f"{target_area}_nyers.xlsx",
        f"{target_area}_nyers.csv",
        f"{target_area}.xlsx",
        f"{target_area}.csv",
    ]:
        cp = os.path.join(DATA_DIR_RAW, cand)
        if os.path.exists(cp):
            return pd.read_excel(cp) if cp.endswith(".xlsx") else pd.read_csv(cp)
    raise FileNotFoundError(f"Nyers adathalmaz nem található ehhez: '{target_area}'")


def load_elado(area: str = None, szamitott=True):
    """Eladó lakások szűrése az aktív masterből vagy CSV-ből."""
    df = load_szamitott_master(area)
    if "listing_type" in df.columns:
        return df[df["listing_type"] == "elado"].copy()
    return df


def load_kiado(area: str = None, szamitott=True):
    """Kiadó lakások szűrése az aktív masterből vagy CSV-ből."""
    df = load_szamitott_master(area)
    if "listing_type" in df.columns:
        return df[df["listing_type"] == "kiado"].copy()
    return df


def load_pontos_geojson(area: str = None, tipus="mind"):
    """Pontos geokódolt minta GeoJSON-ból."""
    import geopandas as gpd

    target_area = _resolve_area(area)
    if target_area == "kobanya":
        if tipus == "elado":
            fn = "kobanya_elado_pontos.geojson"
        elif tipus == "kiado":
            fn = "kobanya_kiado_pontos.geojson"
        else:
            fn = "kobanya_ingatlan_szamitott_pontos.geojson"
    else:
        fn = f"{target_area}_pontos.geojson"

    path = os.path.join(DATA_DIR_PROCESSED, fn)
    if not os.path.exists(path):
        path = os.path.join(ADATHALMAZ_DIR, fn)
    if not os.path.exists(path):
        raise FileNotFoundError(f"Nem található GeoJSON fájl a(z) '{target_area}' területhez: {fn}")
    return gpd.read_file(path)


def load_gis_layer(name):
    """GIS réteg betöltése a 03_gis mappából."""
    import geopandas as gpd

    path = os.path.join(GIS_DIR, f"{name}.geojson")
    if not os.path.exists(path):
        path = os.path.join(GIS_DIR, f"qgis_{name}_3857.geojson")
    if not os.path.exists(path):
        path = os.path.join(ADATHALMAZ_DIR, f"qgis_{name}_3857.geojson")
    return gpd.read_file(path)


# === Szűrő segédfüggvények ===


def filter_df(df, listing_type="mind", pontos_only=False, varosreszek=None):
    """Általános DataFrame szűrő."""
    result = df.copy()
    if listing_type == "elado":
        result = result[result["listing_type"] == "elado"]
    elif listing_type == "kiado":
        result = result[result["listing_type"] == "kiado"]
    if pontos_only and "minta_garantalt_pontos" in result.columns:
        result = result[result["minta_garantalt_pontos"] == 1]
    if varosreszek and len(varosreszek) > 0 and "varosresz" in result.columns:
        result = result[result["varosresz"].isin(varosreszek)]
    return result


# === Szigorúan rögzített kutatási sávrendszerek konstansai ===

VASUT_IMMISSZIO_BINS = [0.0, 150.0, 300.0, 500.0, 1000.0, 2000.0, np.inf]
VASUT_IMMISSZIO_LABELS = [
    "<150 m",
    "150-300 m",
    "300-500 m",
    "500-1000 m",
    "1000-2000 m",
    ">2000 m (referencia)",
]

IZOKRON_BINS = [0.0, 375.0, 750.0, 1125.0]
# Diszjunkt sávok: a modellekben a referencia-kategória a >1125 m (kívül)
IZOKRON_LABELS = ["0-375 m (5 perc)", "375-750 m (10 perc)", "750-1125 m (15 perc)"]

# === Adatalapú leíró sávok (kánon: data/schema.yaml) ===
# Méretkategóriák — CSAK leíró ábrákhoz (a modellekben folytonos log-méret)
MERET_BINS = [0.0, 44.0, 53.0, 68.0, np.inf]
MERET_LABELS = ["<44 m²", "44-53 m²", "53-68 m²", "≥68 m²"]

# Építési korszakok az epulet_kora_ev (év) alapján
EPITES_EVE_BINS = [0.0, 10.0, 30.0, 60.0, np.inf]
EPITES_EVE_LABELS = [
    "0-10 év (új)",
    "10-30 év (rendszerváltás utáni)",
    "30-60 év (panel-korszak)",
    "60+ év (háború előtti)",
]

# POI-sávok (hálózati elérhetőség)
POI_BINS = [0.0, 375.0, 750.0, 1125.0]
POI_LABELS = ["5p (0-375 m)", "10p (375-750 m)", "15p (750-1125 m)"]

# === A sávhatárok EGYETLEN forrása a data/schema.yaml (importkor felülírja a fentieket) ===
try:
    import yaml as _yaml

    _sc = _yaml.safe_load(open(os.path.join(_PROJECT_ROOT, "data", "schema.yaml"), encoding="utf-8"))
    VASUT_IMMISSZIO_BINS = [float(b) for b in _sc["immission_bands"]["bins"]] + [np.inf]
    VASUT_IMMISSZIO_LABELS = list(_sc["immission_bands"]["labels"])
    IZOKRON_BINS = [float(b) for b in _sc["isochrone_bands"]["bins"]]
    IZOKRON_LABELS = list(_sc["isochrone_bands"]["labels"])
    POI_BINS = [float(b) for b in _sc["poi_bands"]["bins"]]
    if "labels" in _sc.get("poi_bands", {}):
        POI_LABELS = list(_sc["poi_bands"]["labels"])
    EPITES_EVE_BINS = [float(b) for b in _sc["era_bands"]["bins"]] + [np.inf]
    EPITES_EVE_LABELS = list(_sc["era_bands"]["labels"])
except Exception:
    pass

# === Kanonikus sáv-dummy építők (robusztus, üres kategória-biztos) ===


def build_immission_dummies(df, min_ref_n=20):
    """Immissziós sáv-dummyk a kanonikus 0-150-300-500-1000-2000 m sávokból.

    - Az ÜRES kategóriákat eldobja (különben a dummy-mátrix degenerált lesz).
    - Referencia: a legtávolabbi sáv, amelyben legalább min_ref_n megfigyelés van;
      ha ilyen nincs, a legtávolabbi nemüres sáv.

    Visszatér: (dummies DataFrame, referencia sáv neve).
    """
    z = df["vasut_zona"].astype(str)
    counts = z.value_counts()
    ordered = [lbl for lbl in VASUT_IMMISSZIO_LABELS if lbl in counts.index and counts[lbl] > 0]
    if not ordered:
        raise ValueError("Nincs nemüres immissziós sáv a mintában.")
    ref = None
    for lbl in reversed(ordered):
        if counts[lbl] >= min_ref_n:
            ref = lbl
            break
    if ref is None:
        ref = ordered[-1]
    dummies = pd.get_dummies(z)
    keep = [lbl for lbl in ordered if lbl != ref]
    return dummies[keep], ref


def build_tod_dummies(df, prefix="vasut", min_ref_n=20):
    """Diszjunkt TOD (gyalogos izokrón) dummyk: 0-375 / 375-750 / 750-1125 m,
    referencia: >1125 m (a *_seta oszlopok kumulatívak, ezért diszjunkt dummykat
    képzünk belőlük). Visszatér: (dummies DataFrame, referencia neve)."""
    c5, c10, c15 = f"{prefix}_5p_seta", f"{prefix}_10p_seta", f"{prefix}_15p_seta"
    d = pd.DataFrame(index=df.index)
    d[f"{prefix}_0_375"] = df[c5].astype(int)
    d[f"{prefix}_375_750"] = (df[c10] - df[c5]).clip(lower=0).astype(int)
    d[f"{prefix}_750_1125"] = (df[c15] - df[c10]).clip(lower=0).astype(int)
    # ha az egyik sáv üres, ejtsük (degenerált dummy elkerülése)
    for col in list(d.columns):
        if d[col].sum() == 0:
            d = d.drop(columns=col)
    ref = ">1125 m (kívül)"
    return d, ref


def drop_constant_columns(X):
    """Konstans oszlopok eldobása (pl. Bécsben is_panel ≡ 0) — különben a
    design-mátrix ranghiányos, az együtthatók nem azonosíthatók.
    A 'const' (tengelymetszet) oszlopot SOHA nem dobjuk el."""
    keep = [c for c in X.columns if c == 'const' or X[c].nunique(dropna=False) > 1]
    dropped = [c for c in X.columns if c not in keep]
    if dropped:
        print(f"[modell] konstans oszlopok eldobva (ranghiány elkerülése): {dropped}")
    return X[keep]


# === API-kulcsok (env-ből; SOHA nem kerülnek a repóba) ===


def _load_dotenv():
    """Helyi .env betöltése (gitignore-olt) — a környezeti változók elsőbbségével."""
    import os as _os
    root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    p = _os.path.join(root, ".env")
    if not _os.path.exists(p):
        return
    try:
        for line in open(p, encoding="utf-8"):
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            _os.environ.setdefault(k.strip(), v.strip())
    except Exception:
        pass


def carto_key():
    """Carto API-kulcs az env-ből (CARTO_API_KEY); üres string, ha nincs beállítva."""
    _load_dotenv()
    return os.environ.get("CARTO_API_KEY", "").strip()


def carto_tile_url(style="voyager", z="{z}", x="{x}", y="{y}"):
    """Carto raszter-csempe URL. A kulcsot a `key` paraméterben kell megadni
    (a Carto NEM `api_key`-et vár — lásd docs.carto.com/faqs/carto-basemaps)."""
    base = f"https://a.basemaps.cartocdn.com/rastertiles/{style}/{z}/{x}/{y}.png"
    k = carto_key()
    return base + (f"?key={k}" if k else "")


def carto_style_url(style="positron"):
    """Carto vektoros stílus-URL a plotly mapbox/maplibre alaptérképhez (a kulcs `key` paraméter)."""
    base = f"https://basemaps.cartocdn.com/gl/{style}-gl-style/style.json"
    k = carto_key()
    return base + (f"?key={k}" if k else "")


# === Számítási cache: minden elemzés pontosan egyszer fut ===

RESULTS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))), "data", "derived", "results")


def data_fingerprint(area):
    """A master-parquet SHA256-ujjlenyomata — a cache érvényességének alapja."""
    import hashlib
    base_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(
        os.path.abspath(__file__)))), "data", "processed")
    f = None
    for cand in [f"{area}_szamitott_master.parquet",
                 f"{area}_ingatlan_szamitott_master.parquet"]:
        if os.path.exists(os.path.join(base_dir, cand)):
            f = os.path.join(base_dir, cand)
            break
    if f is None:
        return "nincs-adat"
    with open(f, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()[:16]


def cached_compute(area, key, fn, force=False):
    """Számítás EGYSZER: dict -> base/<kulcs>.parquet; DataFrame -> base.parquet.
    A cache a data-ujjlenyomat + függvényverzió alapján érvénytelenítődik."""
    import hashlib
    import json as _json
    area = area or os.environ.get("TDK_ACTIVE_AREA", "kobanya")
    os.makedirs(os.path.join(RESULTS_DIR, area), exist_ok=True)
    fp = data_fingerprint(area)
    fn_version = hashlib.sha256(fn.__code__.co_code).hexdigest()[:8] if hasattr(fn, '__code__') else '0'
    base = os.path.join(RESULTS_DIR, area, key)
    meta_p = base + ".meta.json"

    def _valid():
        if not os.path.exists(meta_p):
            return False
        try:
            meta = _json.load(open(meta_p, encoding='utf-8'))
            return meta.get('fp') == fp and meta.get('fn') == fn_version
        except Exception:
            return False

    def _save_meta():
        with open(meta_p, 'w', encoding='utf-8') as fh:
            _json.dump({'fp': fp, 'fn': fn_version}, fh)

    if not force and _valid():
        if os.path.isdir(base):
            out = {}
            for f in sorted(os.listdir(base)):
                if f.endswith('.parquet'):
                    out[f[:-len('.parquet')]] = pd.read_parquet(os.path.join(base, f))
            if out:
                return out
        elif os.path.exists(base + '.parquet'):
            return pd.read_parquet(base + '.parquet')

    res = fn()
    if isinstance(res, dict):
        # NORMALIZÁLÁS: a skalárokat MINDIG DataFrame{'ertek'}-be csomagoljuk,
        # hogy az első számítás és a cache-betöltés AZONOS szerkezetet adjon.
        norm = {}
        for k, v in res.items():
            if isinstance(v, pd.DataFrame):
                norm[k] = v
            elif isinstance(v, pd.Series):
                norm[k] = v.to_frame('ertek')
            elif isinstance(v, (int, float, str, bool)) or v is None:
                norm[k] = pd.DataFrame({'ertek': [v]})
            else:
                norm[k] = v
        os.makedirs(base, exist_ok=True)
        for k, v in norm.items():
            p2 = os.path.join(base, k + '.parquet')
            if isinstance(v, pd.DataFrame):
                v.to_parquet(p2)
        _save_meta()
        return norm
    if isinstance(res, pd.DataFrame):
        res.to_parquet(base + '.parquet')
        _save_meta()
        return res
    return res


# === Kanonikus hedonikus specifikáció (F8: egységes számok 04/07/15 között) ===

CANON_PHYSICAL = [
    'korrigalt_alapterulet_nm', 'szobaszam_osszes', 'is_panel',
    'has_lift', 'allapot_kod', 'has_erkely', 'emelet_szam', 'epulet_kora_ev',
]


def canonical_rail_dummies(df):
    """Vasúti TOD- (tod_*) és kötöttpálya- (kp_*) dummyk: 0-375 / 375-750 /
    750-1125 m, referencia: >1125 m. Az üres sávok kiesnek."""
    out = pd.DataFrame(index=df.index)
    for col, base in [('tavolsag_vasut_halozati_m', 'tod'),
                      ('tavolsag_kotottpalya_halozati_m', 'kp')]:
        d = df[col]
        out[f'{base}_0_375'] = (d <= 375).astype(int)
        out[f'{base}_375_750'] = ((d > 375) & (d <= 750)).astype(int)
        out[f'{base}_750_1125'] = ((d > 750) & (d <= 1125)).astype(int)
    # üres VAGY közel-konstans (2%-98% közötti részarány) dummyk kiszűrése
    keep = [c for c in out.columns if 0.02 < out[c].mean() < 0.98]
    return out[keep]


def fit_canonical_hedonic(df):
    """A KANONIKUS hedonikus specifikáció — a 04/07/15 notebookok ezt futtatják,
    így a főmutatók (zajdiszkont, TOD-prémium) MINDENHOL azonosak.

    df: eladó minta (a hálózati változókkal; a pontos alminta használata a hívó dolga).
    Visszatér: dict(model, phys, tod_cols, kp_cols, zone_cols, ref_zone, X, y, n).
    """
    import statsmodels.api as sm
    # Épületkor-imputáció ELŐSZÖR: a hiányzó építési évű sorok (Ismeretlen korszak)
    # kora a minta mediánjával pótlódik — dokumentált közelítés, a minta megtartása miatt.
    if 'epulet_kora_ev' in df.columns and df['epulet_kora_ev'].isna().any():
        df = df.copy()
        df['epulet_kora_ev'] = df['epulet_kora_ev'].fillna(df['epulet_kora_ev'].median())
    _need = ['log_nm_ar', 'tavolsag_vasut_halozati_m', 'tavolsag_kotottpalya_halozati_m'] + \
        [c for c in CANON_PHYSICAL if c in df.columns]
    d = df.dropna(subset=_need).copy()
    phys = [c for c in CANON_PHYSICAL if c in d.columns and d[c].nunique(dropna=False) > 1]
    rail = canonical_rail_dummies(d)
    zones, ref_zone = build_immission_dummies(d)
    # VÁROSRÉSZ-FIXED EFFECTEK: a városrészi minőség (Óhegy-prémium stb.)
    # elnyelése nélkül a sáv-együtthatók összetételi torzítást kapnak
    # (a referencia-zóna a prémium városrészekkel esik egybe).
    _vr = pd.get_dummies(d['varosresz'].fillna('Ismeretlen'), drop_first=True)
    vr_cols = [c for c in _vr.columns if 0.02 < _vr[c].mean() < 0.98]
    vr = _vr[vr_cols]
    # FŐ MODELL: fizikai + VASÚTÁLLOMÁS TOD-dummyk + immissziós sávok + városrész-FE EGYÜTT
    # (a sáv–TOD kollinearitás mérsékelt: max VIF ~3,6 — a kettős hatás
    # egyetlen modellben azonosítható; ez a kutatás központi specifikációja).
    tod_cols = [c for c in rail.columns if c.startswith('tod')]
    X = sm.add_constant(pd.concat([d[phys], rail[tod_cols], zones, vr], axis=1).astype(float))
    y = d['log_nm_ar']
    model = sm.OLS(y, X).fit(cov_type='HC1')
    # ROBUSZTUSSÁG A: fizikai + sávok + városrész-FE (TOD nélkül)
    Xz = sm.add_constant(pd.concat([d[phys], zones, vr], axis=1).astype(float))
    model_zones = sm.OLS(y, Xz).fit(cov_type='HC1')
    # ROBUSZTUSSÁG B: fizikai + kötöttpálya-dummyk + sávok + városrész-FE
    kp_cols = [c for c in rail.columns if c.startswith('kp')]
    Xk = sm.add_constant(pd.concat([d[phys], rail[kp_cols], zones, vr], axis=1).astype(float))
    model_kp = sm.OLS(y, Xk).fit(cov_type='HC1')
    return {
        'model': model,
        'model_zones': model_zones,
        'model_kp': model_kp,
        'phys': phys,
        'tod_cols': tod_cols,   # vasútállomás TOD (5/10/15p sávok)
        'kp_cols': kp_cols,     # kötöttpálya (robusztusság)
        'zone_cols': list(zones.columns),
        'vr_cols': vr_cols,
        'ref_zone': ref_zone,
        'X': X, 'y': y, 'n': int(model.nobs),
    }


# === Városrészek és stílusok ===

VAROSRESZEK_KOBANYA = [
    "Óhegy",
    "Újhegy",
    "Gyárdűlő",
    "Kőbánya központ",
    "Felsőrákos",
    "Kőbánya-Kertváros",
]
VAROSRESZEK = VAROSRESZEK_KOBANYA


def get_varosreszek(df=None) -> list:
    """Városrészek listája: ha van df, abból nyeri ki, egyébként Kőbánya default."""
    if df is not None and "varosresz" in df.columns:
        vreszek = df["varosresz"].dropna().unique().tolist()
        if vreszek:
            return sorted(vreszek)
    return VAROSRESZEK_KOBANYA


COLORS = {
    "panel": "#FF6B6B",
    "tegla": "#4ECDC4",
    "uj": "#45B7D1",
    "elado": "#2196F3",
    "kiado": "#FF9800",
    "vasut": "#795548",
    "metro": "#0D47A1",
    "villamos": "#FFC107",
    "busz": "#4CAF50",
    "park": "#66BB6A",
    "belvaros": "#9C27B0",
}

PLOTLY_TEMPLATE = "plotly_white"


# Kőbánya középpont (térképekhez)
KOBANYA_CENTER_LAT = 47.475
KOBANYA_CENTER_LON = 19.12

# Magyar feliratok
ALLAPOT_SORREND = ["felújítandó", "közepes", "jó állapotú", "felújított", "újszerű", "új építésű"]


def fmt_huf(v):
    """Forint formázás (pl. 68 500 000 Ft)."""
    if pd.isna(v):
        return "—"
    return f"{v:,.0f} Ft".replace(",", " ")


def fmt_mft(v):
    """Millió Ft formázás."""
    if pd.isna(v):
        return "—"
    return f"{v:.1f} M Ft"


def fmt_pct(v):
    """Százalék formázás."""
    if pd.isna(v):
        return "—"
    return f"{v:.1f}%"


def setup_plotly():
    """Plotly alapbeállítások nbviewer és JupyterLab támogatással."""
    import plotly.io as pio

    pio.templates.default = PLOTLY_TEMPLATE
    pio.renderers.default = "notebook"
# "notebook" renderer: interaktívan is működik, az nbconvert-exportban pedig
    # önálló (CDN plotly.js-re épülő) ábrákat állít elő — a GitHub Pages-re ez kell.


def kpi_card_html(title, value, subtitle="", color="#1e3a8a"):
    """HTML KPI kártya generálása konzisztens vizuális megjelenéshez."""
    sub = (
        f'<div style="font-size: 11px; color: #64748b; margin-top: 4px;">{subtitle}</div>'
        if subtitle
        else ""
    )
    return f"""<div style="flex: 1; min-width: 170px; background: #ffffff; border: 1px solid #e2e8f0; border-radius: 10px; padding: 14px 18px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;">
      <div style="font-size: 11px; font-weight: 700; color: #64748b; text-transform: uppercase; letter-spacing: 0.5px;">{title}</div>
      <div style="font-size: 24px; font-weight: 800; color: {color}; margin-top: 4px;">{value}</div>
      {sub}
    </div>"""


def kpi_grid_html(cards):
    """HTML KPI rács generálása tetszőleges kártyalistából."""
    rendered = []
    for c in cards:
        if isinstance(c, dict):
            rendered.append(
                kpi_card_html(
                    c.get("title", ""),
                    c.get("value", ""),
                    c.get("subtitle", ""),
                    c.get("color", "#1e3a8a"),
                )
            )
        elif isinstance(c, (tuple, list)):
            title = c[0]
            val = c[1]
            sub = c[2] if len(c) > 2 else ""
            col = c[3] if len(c) > 3 else "#1e3a8a"
            rendered.append(kpi_card_html(title, val, sub, col))
    return f"""<div style="display: flex; flex-wrap: wrap; gap: 14px; margin: 16px 0 24px 0;">{"".join(rendered)}</div>"""


def setup_widgets_style():
    """IPyWidgets stílus beállítások."""
    from IPython.display import display, HTML

    display(
        HTML("""
    <style>
    .widget-label { min-width: 180px !important; font-weight: 600; }
    .widget-readout { min-width: 80px !important; }
    .output_area { border: 1px solid #e0e0e0; border-radius: 8px; padding: 12px; margin-top: 8px; }
    </style>
    """)
    )


def get_area_spatial_config(area: str = None) -> dict:
    """Terület térbeli középpont és fókuszprojekt konfigurációja."""
    target_area = _resolve_area(area)
    cfg = load_areas_config()
    area_cfg = cfg.get("areas", {}).get(target_area, {})
    spatial = area_cfg.get("spatial", {})
    return {
        "center_lat": spatial.get("center_lat", 47.475),
        "center_lon": spatial.get("center_lon", 19.120),
        "main_station": spatial.get("main_station", "Központi Vasútállomás"),
    }


def get_map_center(area: str = None) -> dict:
    """Térképek középpontja az aktív terület konfigurációjából."""
    cfg = get_area_spatial_config(area)
    return {"lat": cfg.get("center_lat", 47.475), "lon": cfg.get("center_lon", 19.120)}


def fmt_eur(v):
    """Euró formázás (pl. 2 450 €)."""
    if pd.isna(v):
        return "—"
    return f"{v:,.0f} €".replace(",", " ")


def fmt_price_dual(val_huf, val_eur=None):
    """Kétpénznemes intelligens ármegjelenítő."""
    if pd.isna(val_huf):
        return "—"
    if val_eur is not None and pd.notna(val_eur):
        return f"{fmt_huf(val_huf)} ({fmt_eur(val_eur)})"
    # Ha nincs euró megadva, 400 HUF/EUR átváltással mutatjuk
    eur_approx = val_huf / 400.0
    return f"{fmt_huf(val_huf)} (~{fmt_eur(eur_approx)})"


def render_area_header_html(area: str = None, df: pd.DataFrame = None) -> str:
    """Professzionális dinamikus fejléc banner a notebookokhoz."""
    target_area = _resolve_area(area)
    meta = get_area_metadata(target_area)
    name = meta.get("name", target_area)
    role = meta.get("role", "primary")
    desc = meta.get("description", "")

    n_total = len(df) if df is not None else meta.get("metadata", {}).get("n_total", "—")
    role_badge = (
        '<span style="background: #1e3a8a; color: #93c5fd; padding: 3px 10px; border-radius: 999px; font-size: 11px; font-weight: 700; text-transform: uppercase;">Fő Mintaterület</span>'
        if role == "primary"
        else '<span style="background: #065f46; color: #a7f3d0; padding: 3px 10px; border-radius: 999px; font-size: 11px; font-weight: 700; text-transform: uppercase;">Nemzetközi Benchmark / Kontroll</span>'
    )

    return f"""<div style="background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%); color: #f8fafc; border-radius: 12px; padding: 18px 22px; margin-bottom: 20px; border: 1px solid #334155; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;">
      <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px;">
        <div>
          <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 6px;">
            {role_badge}
            <span style="font-size: 12px; color: #94a3b8; font-weight: 600;">IFK-TDK 2026 Kutatási Keretrendszer</span>
          </div>
          <h2 style="margin: 0; font-size: 22px; font-weight: 800; color: #ffffff;">{name}</h2>
          <p style="margin: 4px 0 0 0; font-size: 13px; color: #cbd5e1; max-width: 750px;">{desc}</p>
        </div>
        <div style="background: rgba(255,255,255,0.06); padding: 10px 16px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.1); text-align: right;">
          <div style="font-size: 11px; color: #94a3b8; text-transform: uppercase; font-weight: 700;">Aktív Minta</div>
          <div style="font-size: 20px; font-weight: 800; color: #38bdf8;">{n_total:,} db</div>
        </div>
      </div>
    </div>""".replace(",", " ")
