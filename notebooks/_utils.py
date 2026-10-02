# -*- coding: utf-8 -*-
"""
_utils.py — Közös segédmodul a TDK kutatási notebookok számára.
Minden notebook innen importálja az adatbetöltő és formázó függvényeket.
"""
import os
import warnings
import pandas as pd
import numpy as np

warnings.filterwarnings('ignore', category=FutureWarning)
warnings.filterwarnings('ignore', category=UserWarning)

# === Útvonalak ===
_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(_THIS_DIR)

# Keresés a felállított struktúrában: data/processed, data/raw
DATA_DIR_PROCESSED = os.path.join(_PROJECT_ROOT, 'data', 'processed')
if not os.path.exists(DATA_DIR_PROCESSED):
    for cand in [os.path.join(_PROJECT_ROOT, 'data'), os.path.join(_PROJECT_ROOT, '01_data', 'processed'), os.path.join(_PROJECT_ROOT, 'Adathalmaz', 'data')]:
        if os.path.exists(cand):
            DATA_DIR_PROCESSED = cand
            break

DATA_DIR_RAW = os.path.join(_PROJECT_ROOT, 'data', 'raw')
if not os.path.exists(DATA_DIR_RAW):
    for cand in [os.path.join(_PROJECT_ROOT, 'data'), os.path.join(_PROJECT_ROOT, '01_data', 'raw')]:
        if os.path.exists(cand):
            DATA_DIR_RAW = cand
            break

ADATHALMAZ_DIR = DATA_DIR_PROCESSED
GIS_DIR = os.path.join(_PROJECT_ROOT, 'gis')
if not os.path.exists(GIS_DIR):
    GIS_DIR = os.path.join(_PROJECT_ROOT, '03_gis')

# === Adatbetöltő függvények ===

def load_szamitott_master():
    """A teljes számított master adathalmaz (1320 sor, 169 oszlop)."""
    path = os.path.join(DATA_DIR_PROCESSED, 'kobanya_ingatlan_szamitott_master.parquet')
    if not os.path.exists(path):
        path = os.path.join(ADATHALMAZ_DIR, 'kobanya_ingatlan_szamitott_master.parquet')
    return pd.read_parquet(path)

def load_nyers_master():
    """A nyers (kapart) master adathalmaz."""
    path = os.path.join(DATA_DIR_RAW, 'kobanya_ingatlan_nyers_master.db')
    import sqlite3
    conn = sqlite3.connect(path)
    df = pd.read_sql("SELECT * FROM listings", conn)
    conn.close()
    return df

def load_elado(szamitott=True):
    """Eladó lakások CSV."""
    prefix = 'kobanya_elado_szamitott' if szamitott else 'kobanya_elado_nyers'
    d = DATA_DIR_PROCESSED if szamitott else DATA_DIR_RAW
    return pd.read_csv(os.path.join(d, f'{prefix}.csv'), encoding='utf-8-sig')

def load_kiado(szamitott=True):
    """Kiadó lakások CSV."""
    prefix = 'kobanya_kiado_szamitott' if szamitott else 'kobanya_kiado_nyers'
    d = DATA_DIR_PROCESSED if szamitott else DATA_DIR_RAW
    return pd.read_csv(os.path.join(d, f'{prefix}.csv'), encoding='utf-8-sig')

def load_pontos_geojson(tipus='mind'):
    """Pontos geokódolt minta GeoJSON-ból (N=296)."""
    import geopandas as gpd
    if tipus == 'elado':
        fn = 'kobanya_elado_szamitott_pontos.geojson'
    elif tipus == 'kiado':
        fn = 'kobanya_kiado_szamitott_pontos.geojson'
    else:
        fn = 'kobanya_ingatlan_szamitott_pontos.geojson'
    path = os.path.join(DATA_DIR_PROCESSED, fn)
    if not os.path.exists(path):
        path = os.path.join(ADATHALMAZ_DIR, fn)
    return gpd.read_file(path)

def load_gis_layer(name):
    """GIS réteg betöltése a 03_gis mappából."""
    import geopandas as gpd
    path = os.path.join(GIS_DIR, f'{name}.geojson')
    if not os.path.exists(path):
        path = os.path.join(GIS_DIR, f'qgis_{name}_3857.geojson')
    if not os.path.exists(path):
        path = os.path.join(ADATHALMAZ_DIR, f'qgis_{name}_3857.geojson')
    return gpd.read_file(path)

# === Szűrő segédfüggvények ===

def filter_df(df, listing_type='mind', pontos_only=False, varosreszek=None):
    """Általános DataFrame szűrő."""
    result = df.copy()
    if listing_type == 'elado':
        result = result[result['listing_type'] == 'elado']
    elif listing_type == 'kiado':
        result = result[result['listing_type'] == 'kiado']
    if pontos_only:
        result = result[result['minta_garantalt_pontos'] == 1]
    if varosreszek and len(varosreszek) > 0:
        result = result[result['varosresz'].isin(varosreszek)]
    return result

# === Konstansok ===

VAROSRESZEK = ['Óhegy', 'Újhegy', 'Gyárdűlő', 'Kőbánya központ', 'Felsőrákos', 'Kőbánya-Kertváros']

COLORS = {
    'panel': '#FF6B6B', 'tegla': '#4ECDC4', 'uj': '#45B7D1',
    'elado': '#2196F3', 'kiado': '#FF9800',
    'mazsa_ter': '#E91E63', 'vasut': '#795548',
    'metro': '#0D47A1', 'villamos': '#FFC107', 'busz': '#4CAF50',
    'park': '#66BB6A', 'belvaros': '#9C27B0',
}

PLOTLY_TEMPLATE = 'plotly_white'

# Mázsa tér koordináták
MAZSA_TER_LAT = 47.4866
MAZSA_TER_LON = 19.1294

# Kőbánya középpont (térképekhez)
KOBANYA_CENTER_LAT = 47.475
KOBANYA_CENTER_LON = 19.12

# Magyar feliratok
ALLAPOT_SORREND = ['felújítandó', 'közepes', 'jó állapotú', 'felújított', 'újszerű', 'új építésű']

def fmt_huf(v):
    """Forint formázás (pl. 68 500 000 Ft)."""
    if pd.isna(v): return '—'
    return f"{v:,.0f} Ft".replace(',', ' ')

def fmt_mft(v):
    """Millió Ft formázás."""
    if pd.isna(v): return '—'
    return f"{v:.1f} M Ft"

def fmt_pct(v):
    """Százalék formázás."""
    if pd.isna(v): return '—'
    return f"{v:.1f}%"

def setup_plotly():
    """Plotly alapbeállítások nbviewer és JupyterLab támogatással."""
    import plotly.io as pio
    pio.templates.default = PLOTLY_TEMPLATE
    pio.renderers.default = "notebook_connected"

def kpi_card_html(title, value, subtitle="", color="#1e3a8a"):
    """HTML KPI kártya generálása konzisztens vizuális megjelenéshez."""
    sub = f'<div style="font-size: 11px; color: #64748b; margin-top: 4px;">{subtitle}</div>' if subtitle else ''
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
            rendered.append(kpi_card_html(c.get('title', ''), c.get('value', ''), c.get('subtitle', ''), c.get('color', '#1e3a8a')))
        elif isinstance(c, (tuple, list)):
            title = c[0]
            val = c[1]
            sub = c[2] if len(c) > 2 else ''
            col = c[3] if len(c) > 3 else '#1e3a8a'
            rendered.append(kpi_card_html(title, val, sub, col))
    return f"""<div style="display: flex; flex-wrap: wrap; gap: 14px; margin: 16px 0 24px 0;">{"".join(rendered)}</div>"""

def setup_widgets_style():
    """IPyWidgets stílus beállítások."""
    from IPython.display import display, HTML
    display(HTML("""
    <style>
    .widget-label { min-width: 180px !important; font-weight: 600; }
    .widget-readout { min-width: 80px !important; }
    .output_area { border: 1px solid #e0e0e0; border-radius: 8px; padding: 12px; margin-top: 8px; }
    </style>
    """))

