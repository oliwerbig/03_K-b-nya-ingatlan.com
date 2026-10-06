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
            if clean_name.startswith("kobanya"):
                clean_name = "kobanya"
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
    "<150 m (Immisszió)",
    "150-300 m (Erős teher)",
    "300-500 m (Átmeneti)",
    "500-1000 m (Háttérzaj)",
    "1000-2000 m (Közepes ref.)",
    ">2000 m (Tiszta ref.)",
]

IZOKRON_BINS = [0.0, 375.0, 750.0, 1125.0]
IZOKRON_LABELS = ["≤375 m (5 perc)", "≤750 m (10 perc)", "≤1125 m (15 perc)"]

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
    pio.renderers.default = "notebook_connected"


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
        "focus_project_name": spatial.get("focus_project_name", "Fókusz Akcióterület"),
        "focus_lat": spatial.get("focus_lat", 47.4866),
        "focus_lon": spatial.get("focus_lon", 19.1294),
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
