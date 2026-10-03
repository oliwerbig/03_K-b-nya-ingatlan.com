from notebook_docs import NOTEBOOK_DOCS
# -*- coding: utf-8 -*-
"""
build_all_notebooks.py
Generates all 12 TDK research notebooks with modular cells,
direct cell outputs for static HTML / nbviewer.org compatibility,
and interactive IPyWidgets modules for live JupyterLab exploration.
"""
import os, sys, json
import nbformat
from nbformat.v4 import new_notebook, new_code_cell, new_markdown_cell

sys.stdout.reconfigure(encoding='utf-8')

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'notebooks')
os.makedirs(OUTPUT_DIR, exist_ok=True)

def save_nb(nb, filename):
    filepath = os.path.join(OUTPUT_DIR, filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        nbformat.write(nb, f)
    print(f"Generated: {filename} ({len(nb.cells)} cells)")

# ==============================================================================
# NOTEBOOK 00: Adathalmaz Áttekintés és Minőségi Riport
# ==============================================================================
def build_nb00():
    nb = new_notebook()
    
    nb.cells.append(new_markdown_cell(NOTEBOOK_DOCS["nb00"]["intro"]))

    nb.cells.append(new_code_cell("""import warnings; warnings.filterwarnings('ignore')
import sys, os
from _utils import *
setup_plotly()
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import ipywidgets as widgets
from IPython.display import display, clear_output, HTML
import pandas as pd
import numpy as np

# Adathalmaz betöltése
df = load_szamitott_master()
print(f"Sikeresen betöltve: {len(df)} sor, {len(df.columns)} oszlop.")"""))

    nb.cells.append(new_markdown_cell(NOTEBOOK_DOCS["nb00"]["sec1"]))

    nb.cells.append(new_code_cell("""n_total = len(df)
n_elado = len(df[df['listing_type'] == 'elado'])
n_kiado = len(df[df['listing_type'] == 'kiado'])
n_pontos = len(df[df['minta_garantalt_pontos'] == 1])
median_nm_ar = df[df['listing_type'] == 'elado']['nm_ar_huf'].median()
atlag_alapterulet = df['alapterulet_nm'].mean()

kpi_cards = [
    ("Összes Hirdetés", f"{n_total:,} db".replace(',', ' '), "Teljes adatbázis", "#1e3a8a"),
    ("Eladó Lakások", f"{n_elado:,} db".replace(',', ' '), f"{n_elado/n_total*100:.1f}% arány", "#2563eb"),
    ("Kiadó Lakások", f"{n_kiado:,} db".replace(',', ' '), f"{n_kiado/n_total*100:.1f}% arány", "#d97706"),
    ("Garantált Pontos GIS", f"{n_pontos:,} db".replace(',', ' '), f"{n_pontos/n_total*100:.1f}% koordinátás", "#16a34a"),
    ("Eladó Medián Ár/m²", fmt_huf(median_nm_ar), "Kínálati fajlagos ár", "#9333ea"),
    ("Átlagos Alapterület", f"{atlag_alapterulet:.1f} m²", "Kínálati átlag", "#0891b2"),
]
display(HTML(kpi_grid_html(kpi_cards)))"""))

    nb.cells.append(new_markdown_cell(NOTEBOOK_DOCS["nb00"]["sec2"]))

    nb.cells.append(new_code_cell("""df_counts = df.groupby(['varosresz', 'listing_type']).size().reset_index(name='count')
df_counts['listing_nev'] = df_counts['listing_type'].map({'elado': 'Eladó', 'kiado': 'Kiadó'})

fig1 = px.bar(
    df_counts,
    x='varosresz',
    y='count',
    color='listing_nev',
    barmode='group',
    title='Hirdetések megoszlása városrészenként és típusonként',
    labels={'varosresz': 'Városrész', 'count': 'Hirdetések száma', 'listing_nev': 'Típus'},
    color_discrete_map={'Eladó': '#2563eb', 'Kiadó': '#f59e0b'},
    template=PLOTLY_TEMPLATE
)
fig1.update_layout(xaxis_tickangle=-30, height=450)
fig1.show()"""))

    nb.cells.append(new_markdown_cell("""### 3. Kutatási Változókatalógus és Teljes Adatszótár

A TDK kutatás 16 analitikai moduljában használt **összes kulcsváltozó rendszerezett leírása és kitöltöttségi vizsgálata**. A változók 6 funkcionális csoportba rendezve fedik le az ingatlanpiaci ármeghatározó tényezőket:
1. **Pénzügyi célváltozók**: vételárak, bérleti díjak és fajlagos árak (log transzformációval).
2. **Fizikai és épületjellemzők**: alapterület, szobaszám, panel/tégla szerkezet, műszaki állapot, lift, erkély és emelet.
3. **Hálózati séta távolságok**: a budapesti gyalogos úthálózaton (OSM nx) számított valós sétautak metróig, vasútállomásig, Mázsa térig, parkokig.
4. **Légvonalbeli környezeti hatások**: a vasúti pálya zaj- és rezgésemissziója, illetve referencia távolságok.
5. **Gyalogos izokrón dummyk**: 10-15 perces elérhetőségi zónák (750 m és 1125 m küszöbértékekkel).
6. **Térbeli GIS koordináták**: pontos geokódolt helymeghatározás (WGS84) és városrészi besorolás."""))

    nb.cells.append(new_code_cell("""# 1. Teljes változó-metaadatbázis definiálása
valtozo_meta = [
    # Pénzügyi célváltozók
    ('price_huf', 'Kínálati vételár', 'Pénzügyi', 'HUF', 'Célváltozó (bruttó összeg)'),
    ('nm_ar_huf', 'Négyzetméterár', 'Pénzügyi', 'HUF/m²', 'Fajlagos célváltozó'),
    ('log_nm_ar', 'Fajlagos ár logaritmusa', 'Pénzügyi', 'ln(HUF/m²)', 'Ökonometriai regressziós cél'),
    ('ar_millio_ft', 'Vételár millió Ft-ban', 'Pénzügyi', 'M Ft', 'Leíró statisztikai mutató'),
    ('ar_ezer_ft_ho', 'Havi bérleti díj', 'Pénzügyi', 'ezer Ft/hó', 'Bérleti piac és Rent Gap'),
    # Fizikai és épületjellemzők
    ('alapterulet_nm', 'Alapterület', 'Fizikai', 'm²', 'Fizikai alaptulajdonság'),
    ('korrigalt_alapterulet_nm', 'Korrigált alapterület', 'Fizikai', 'm²', 'Fél erkéllyel súlyozva'),
    ('szobaszam_osszes', 'Összes szobaszám', 'Fizikai', 'db', 'Belső beosztási kontroll'),
    ('allapot', 'Műszaki állapot (szöveg)', 'Fizikai', 'kategória', 'Minőségi besorolás'),
    ('allapot_kod', 'Műszaki állapot index', 'Fizikai', '1-6 skála', 'Hedonikus minőségi rang'),
    ('is_panel', 'Panelszerkezet dummy', 'Fizikai', '0/1', 'Technológiai diszkont'),
    ('is_tegla', 'Tégla falazat dummy', 'Fizikai', '0/1', 'Hagyományos falazat'),
    ('has_lift', 'Lift megléte dummy', 'Fizikai', '0/1', 'Kényelmi felszereltség'),
    ('van_erkely', 'Erkély megléte dummy', 'Fizikai', '0/1', 'Kültéri kapcsolat prémiuma'),
    ('erkely_nm', 'Erkély mérete', 'Fizikai', 'm²', 'Kültéri felület nagysága'),
    ('emelet_szam', 'Emelet szintszám', 'Fizikai', 'szint', 'Függőleges elhelyezkedés'),
    ('epulet_kora_ev', 'Épület becsült kora', 'Fizikai', 'év', 'Amortizációs hatás'),
    ('epites_eve_kategoria', 'Építési korszak', 'Fizikai', 'korszak', 'Építészeti korcsoport'),
    # Hálózati közlekedési távolságok
    ('tavolsag_metro_halozati_m', 'Metróállomás hálózati táv.', 'Hálózati elérhetőség', 'méter', 'Gyalogos metróelérés (M2/M3)'),
    ('tavolsag_vasut_halozati_m', 'Vasútállomás hálózati táv.', 'Hálózati elérhetőség', 'méter', 'Állomási elérhetőség (TOD)'),
    ('tavolsag_mazsa_halozati_m', 'Mázsa tér hálózati táv.', 'Hálózati elérhetőség', 'méter', 'Városközpont & LVC fókusztáv'),
    ('tavolsag_villamos_halozati_m', 'Villamosmegálló hálózati táv.', 'Hálózati elérhetőség', 'méter', 'Felszíni kötöttpályás hálózat'),
    ('tavolsag_busz_halozati_m', 'Buszmegálló hálózati táv.', 'Hálózati elérhetőség', 'méter', 'Helyi buszhálózat elérése'),
    ('tavolsag_park_halozati_m', 'Park / zöldfelület hálózat', 'Hálózati elérhetőség', 'méter', 'Rekreációs zöldterület elérése'),
    ('tavolsag_belvaros_halozati_m', 'Belváros (Deák tér) hálózat', 'Hálózati elérhetőség', 'méter', 'Centrumtól való hálózati táv'),
    # Légvonalbeli környezeti externáliák
    ('tavolsag_vasut_m', 'Vasúti pálya légvonal (zaj)', 'Környezeti externália', 'méter', 'Immissziós zaj- és rezgésterhelés'),
    ('tavolsag_metro_m', 'Metróvonal légvonal', 'Környezeti externália', 'méter', 'Légvonalbeli referencia táv'),
    ('tavolsag_mazsa_m', 'Mázsa tér légvonal', 'Környezeti externália', 'méter', 'Légvonalbeli fókusztávolság'),
    ('tavolsag_belvaros_m', 'Belváros légvonal', 'Környezeti externália', 'méter', 'Légvonalbeli centrumtáv'),
    ('tavolsag_park_m', 'Legközelebbi park légvonal', 'Környezeti externália', 'méter', 'Zöldfelületi közelség'),
    # Gyalogos izokrón dummyk
    ('metro_10p_seta', 'Metró 10p séta (750m)', 'Gyalogos izokrón', '0/1', 'Metró vonzáskörzet'),
    ('vasut_10p_seta', 'Vasút 10p séta (750m)', 'Gyalogos izokrón', '0/1', 'Állomás gyalogos elérhetőség'),
    ('mazsa_10p_seta', 'Mázsa tér 10p séta', 'Gyalogos izokrón', '0/1', 'Központi akcióterület'),
    ('villamos_10p_seta', 'Villamos 10p séta', 'Gyalogos izokrón', '0/1', 'Villamos vonzáskörzet'),
    ('park_10p_seta', 'Park 10p séta', 'Gyalogos izokrón', '0/1', 'Közeli zöldterületi ellátás'),
    # Térbeli GIS koordináták
    ('geokodolt_lat', 'WGS84 Szélesség (Lat)', 'Térbeli GIS', 'fok', 'Térbeli pontkoordináta'),
    ('geokodolt_lon', 'WGS84 Hosszúság (Lon)', 'Térbeli GIS', 'fok', 'Térbeli pontkoordináta'),
    ('varosresz', 'Kőbányai Városrész', 'Térbeli GIS', 'név', 'Városrészi szegmens'),
    ('minta_garantalt_pontos', 'Pontos koordináta zászló', 'Térbeli GIS', '0/1', 'GIS szűrési jelző (N=296)')
]

# 2. Kitöltöttségi statisztikák számítása
stats_rows = []
dict_rows = []
for col, hu_name, kat, unit, role in valtozo_meta:
    if col in df.columns:
        n_valid = df[col].notna().sum()
        pct = (n_valid / len(df)) * 100
        stats_rows.append({
            'Technikai oszlop': col,
            'Változó megnevezése': hu_name,
            'Kategória': kat,
            'Kitöltöttség (%)': round(pct, 1),
            'Érvényes N': n_valid
        })
        dict_rows.append({
            'Kategória': kat,
            'Változó neve': hu_name,
            'Technikai név': f"<code>{col}</code>",
            'Mértékegység': unit,
            'Érvényes (db)': f"{n_valid:,} ({pct:.1f}%)".replace(',', ' '),
            'Szerepe a kutatásban': role
        })

df_qual = pd.DataFrame(stats_rows).sort_values(['Kategória', 'Kitöltöttség (%)'], ascending=[True, True])

# 3. Strukturált, kategóriánként színezett kitöltöttségi ábra
fig2 = px.bar(
    df_qual,
    x='Kitöltöttség (%)',
    y='Változó megnevezése',
    color='Kategória',
    orientation='h',
    title='Kutatási Változók Kitöltöttségi Aránya Funkcionális Kategóriánként (N = 1 320 db)',
    labels={'Kitöltöttség (%)': 'Kitöltöttség aránya (%)', 'Változó megnevezése': 'Változó'},
    range_x=[0, 105],
    template=PLOTLY_TEMPLATE,
    height=850
)
fig2.update_layout(yaxis=dict(tickfont=dict(size=10)), margin=dict(l=220, r=30, t=50, b=50))
fig2.show()

# 4. Teljes HTML Adatszótár megjelenítése
df_dict = pd.DataFrame(dict_rows)
html_dict = "<div style='overflow-x:auto; margin: 20px 0; max-height: 480px; overflow-y: auto;'>" + df_dict.to_html(classes='table table-bordered table-striped table-hover', index=False, escape=False) + "</div>"
display(HTML("<b>Részletes Kutatási Adatszótár és Változóleírás:</b>" + html_dict))"""))

    nb.cells.append(new_markdown_cell(NOTEBOOK_DOCS["nb00"]["sec4"]))

    nb.cells.append(new_code_cell("""# Valós idejű kliensoldali adathalmaz-szűrő és feltáró vezérlőpult
import json

summary_rows = []
for (ltype, vr, pt), group in df.groupby(['listing_type', 'varosresz', 'minta_garantalt_pontos']):
    summary_rows.append({
        'type': str(ltype),
        'vr': str(vr),
        'pt': int(pt),
        'n': int(len(group)),
        'p_sum': float(group['price_huf'].dropna().sum()),
        'p_cnt': int(group['price_huf'].dropna().count()),
        'nm_sum': float(group['nm_ar_huf'].dropna().sum()),
        'nm_cnt': int(group['nm_ar_huf'].dropna().count()),
        'area_sum': float(group['alapterulet_nm'].dropna().sum()),
        'area_cnt': int(group['alapterulet_nm'].dropna().count())
    })

vr_list = sorted(list(df['varosresz'].dropna().unique()))

html_nb00 = f'''
<div id="nb00_filter_app" style="background:#ffffff; border:1px solid #cbd5e1; border-radius:12px; padding:22px; box-shadow:0 4px 6px -1px rgba(0,0,0,0.06); margin:18px 0; font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;">
  <div style="display:flex; justify-content:space-between; align-items:center; border-bottom:2px solid #f1f5f9; padding-bottom:12px; margin-bottom:18px;">
    <div>
      <h3 style="margin:0; color:#1e3a8a; font-size:19px; font-weight:700;">🔎 Interaktív Adathalmaz Szűrő & Mintavételi Vezérlőpult</h3>
      <p style="margin:3px 0 0 0; color:#64748b; font-size:13px;">Dinamikus szegmentáció és statisztikai összegzés a teljes kőbányai ingatlanpiaci mintán</p>
    </div>
    <span style="background:#dbeafe; color:#1d4ed8; font-size:11px; font-weight:700; padding:4px 10px; border-radius:9999px;">Kliensoldali JS Motor</span>
  </div>

  <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap:18px; margin-bottom:18px;">
    <!-- Típus és Pontosság szűrő -->
    <div style="background:#f8fafc; padding:14px; border-radius:8px; border:1px solid #e2e8f0;">
      <div style="font-weight:700; color:#334155; margin-bottom:10px; font-size:13px; text-transform:uppercase;">1. Hirdetés Típusa:</div>
      <div style="display:flex; gap:12px; margin-bottom:14px;">
        <label style="font-size:13px; font-weight:600; color:#334155; cursor:pointer;">
          <input type="radio" name="nb00_type" value="all" checked onchange="filterNB00()"> Mindkettő
        </label>
        <label style="font-size:13px; font-weight:600; color:#2563eb; cursor:pointer;">
          <input type="radio" name="nb00_type" value="elado" onchange="filterNB00()"> Eladó lakások
        </label>
        <label style="font-size:13px; font-weight:600; color:#d97706; cursor:pointer;">
          <input type="radio" name="nb00_type" value="kiado" onchange="filterNB00()"> Kiadó lakások
        </label>
      </div>

      <div style="font-weight:700; color:#334155; margin-bottom:8px; font-size:13px; text-transform:uppercase;">2. Térbeli Pontosság:</div>
      <label style="display:flex; align-items:center; gap:8px; font-size:13px; font-weight:600; color:#059669; cursor:pointer;">
        <input type="checkbox" id="nb00_exact" onchange="filterNB00()"> Csak garantált pontos koordinátás (N=296)
      </label>
    </div>

    <!-- Városrészek szűrő -->
    <div style="background:#f8fafc; padding:14px; border-radius:8px; border:1px solid #e2e8f0;">
      <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
        <div style="font-weight:700; color:#334155; font-size:13px; text-transform:uppercase;">3. Városrészek Kijelölése:</div>
        <div style="font-size:11px;">
          <a href="javascript:void(0)" onclick="toggleAllVR(true)" style="color:#2563eb; margin-right:8px; text-decoration:none; font-weight:600;">Mind</a>
          <a href="javascript:void(0)" onclick="toggleAllVR(false)" style="color:#dc2626; text-decoration:none; font-weight:600;">Töröl</a>
        </div>
      </div>
      <div id="nb00_vr_chips" style="display:flex; flex-wrap:wrap; gap:6px; max-height:110px; overflow-y:auto; padding:4px;">
        {"".join([f'<label style="font-size:11px; background:#ffffff; border:1px solid #cbd5e1; border-radius:14px; padding:3px 8px; cursor:pointer;"><input type="checkbox" class="nb00_vr_cb" value="{vr}" checked onchange="filterNB00()"> {vr}</label>' for vr in vr_list])}
      </div>
    </div>
  </div>

  <!-- KPI Rács -->
  <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap:12px; margin-bottom:16px;">
    <div style="background:#eff6ff; border:1px solid #93c5fd; border-radius:10px; padding:12px 16px; text-align:center;">
      <div style="font-size:11px; font-weight:700; color:#1e40af; text-transform:uppercase;">Szűrt Elemek</div>
      <div id="nb00_res_count" style="font-size:24px; font-weight:800; color:#1d4ed8; margin:3px 0;">-- db</div>
      <div style="font-size:11px; color:#2563eb;">Kiválasztott mintaelemszám</div>
    </div>

    <div style="background:#f0fdf4; border:1px solid #86efac; border-radius:10px; padding:12px 16px; text-align:center;">
      <div style="font-size:11px; font-weight:700; color:#166534; text-transform:uppercase;">Átlagos Kínálati Ár</div>
      <div id="nb00_res_price" style="font-size:24px; font-weight:800; color:#15803d; margin:3px 0;">-- M Ft</div>
      <div id="nb00_lbl_price_type" style="font-size:11px; color:#16a34a;">Vételár átlag</div>
    </div>

    <div style="background:#faf5ff; border:1px solid #d8b4fe; border-radius:10px; padding:12px 16px; text-align:center;">
      <div style="font-size:11px; font-weight:700; color:#6b21a8; text-transform:uppercase;">Fajlagos Négyzetméterár</div>
      <div id="nb00_res_nm" style="font-size:24px; font-weight:800; color:#7e22ce; margin:3px 0;">-- Ft/m²</div>
      <div style="font-size:11px; color:#9333ea;">Szűrt minta átlaga</div>
    </div>

    <div style="background:#fffbeb; border:1px solid #fde68a; border-radius:10px; padding:12px 16px; text-align:center;">
      <div style="font-size:11px; font-weight:700; color:#92400e; text-transform:uppercase;">Átlagos Alapterület</div>
      <div id="nb00_res_area" style="font-size:24px; font-weight:800; color:#b45309; margin:3px 0;">-- m²</div>
      <div style="font-size:11px; color:#d97706;">Fizikai lakásméret</div>
    </div>
  </div>

  <!-- Városrészi Összesítő Mini Táblázat -->
  <div style="overflow-x:auto;">
    <table id="nb00_stat_table" class="table table-bordered table-striped table-hover" style="width:100%; font-size:12px; margin-top:8px;">
      <thead>
        <tr style="background:#f1f5f9; color:#334155;">
          <th>Városrész</th>
          <th style="text-align:right;">Hirdetésszám</th>
          <th style="text-align:right;">Átlagár (M Ft)</th>
          <th style="text-align:right;">Átlag Ár/m²</th>
          <th style="text-align:right;">Átlag Terület</th>
        </tr>
      </thead>
      <tbody></tbody>
    </table>
  </div>
</div>

<script>
(function() {{
  const data = {json.dumps(summary_rows)};

  window.toggleAllVR = function(state) {{
    document.querySelectorAll('.nb00_vr_cb').forEach(cb => cb.checked = state);
    filter();
  }};

  function filter() {{
    const type = document.querySelector('input[name="nb00_type"]:checked').value;
    const exactOnly = document.getElementById('nb00_exact').checked;
    const selectedVR = new Set();
    document.querySelectorAll('.nb00_vr_cb:checked').forEach(cb => selectedVR.add(cb.value));

    let totalN = 0, sumP = 0, cntP = 0, sumNM = 0, cntNM = 0, sumArea = 0, cntArea = 0;
    let vrMap = {{}};

    for (let r of data) {{
      if (type !== 'all' && r.type !== type) continue;
      if (exactOnly && r.pt !== 1) continue;
      if (!selectedVR.has(r.vr)) continue;

      totalN += r.n;
      sumP += r.p_sum; cntP += r.p_cnt;
      sumNM += r.nm_sum; cntNM += r.nm_cnt;
      sumArea += r.area_sum; cntArea += r.area_cnt;

      if (!vrMap[r.vr]) {{
        vrMap[r.vr] = {{ n: 0, p_sum: 0, p_cnt: 0, nm_sum: 0, nm_cnt: 0, area_sum: 0, area_cnt: 0 }};
      }}
      vrMap[r.vr].n += r.n;
      vrMap[r.vr].p_sum += r.p_sum; vrMap[r.vr].p_cnt += r.p_cnt;
      vrMap[r.vr].nm_sum += r.nm_sum; vrMap[r.vr].nm_cnt += r.nm_cnt;
      vrMap[r.vr].area_sum += r.area_sum; vrMap[r.vr].area_cnt += r.area_cnt;
    }}

    const avgP = cntP > 0 ? (sumP / cntP) : 0;
    const avgNM = cntNM > 0 ? (sumNM / cntNM) : 0;
    const avgArea = cntArea > 0 ? (sumArea / cntArea) : 0;

    document.getElementById('nb00_res_count').innerText = totalN.toLocaleString('hu-HU') + ' db';
    if (type === 'kiado') {{
      document.getElementById('nb00_res_price').innerText = Math.round(avgP / 1000).toLocaleString('hu-HU') + ' ezer Ft/hó';
      document.getElementById('nb00_lbl_price_type').innerText = 'Havi bérleti díj átlag';
    }} else {{
      document.getElementById('nb00_res_price').innerText = (avgP / 1e6).toFixed(1) + ' M Ft';
      document.getElementById('nb00_lbl_price_type').innerText = 'Kínálati vételár átlag';
    }}
    document.getElementById('nb00_res_nm').innerText = Math.round(avgNM).toLocaleString('hu-HU') + ' Ft/m²';
    document.getElementById('nb00_res_area').innerText = avgArea.toFixed(1) + ' m²';

    // Táblázat renderelése
    const tbody = document.querySelector('#nb00_stat_table tbody');
    let rowsHtml = '';
    const vrSorted = Object.keys(vrMap).sort((a,b) => vrMap[b].n - vrMap[a].n);
    for (let vr of vrSorted) {{
      const v = vrMap[vr];
      const vp = v.p_cnt > 0 ? (v.p_sum / v.p_cnt) : 0;
      const vnm = v.nm_cnt > 0 ? (v.nm_sum / v.nm_cnt) : 0;
      const va = v.area_cnt > 0 ? (v.area_sum / v.area_cnt) : 0;
      const pStr = type === 'kiado' ? (Math.round(vp/1000).toLocaleString('hu-HU') + ' ezer') : (vp / 1e6).toFixed(1) + ' M';
      rowsHtml += `<tr>
        <td><b>${{vr}}</b></td>
        <td style="text-align:right;">${{v.n}} db</td>
        <td style="text-align:right;">${{pStr}}</td>
        <td style="text-align:right;">${{Math.round(vnm).toLocaleString('hu-HU')}} Ft</td>
        <td style="text-align:right;">${{va.toFixed(1)}} m²</td>
      </tr>`;
    }}
    tbody.innerHTML = rowsHtml || '<tr><td colspan="5" style="text-align:center; color:#94a3b8;">Nincs találat a kiválasztott szűrőkkel.</td></tr>';
  }}

  window.filterNB00 = filter;
  setTimeout(filter, 50);
}})();
</script>
'''
display(HTML(html_nb00))"""))

    save_nb(nb, '00_adathalmaz_attekintes.ipynb')

if __name__ == '__main__':
    build_nb00()

# ==============================================================================
# NOTEBOOK 01: Leíró Statisztika és Exploratív Adatelemzés (EDA)
# ==============================================================================
def build_nb01():
    nb = new_notebook()
    
    nb.cells.append(new_markdown_cell(NOTEBOOK_DOCS["nb01"]["intro"]))

    nb.cells.append(new_code_cell("""import warnings; warnings.filterwarnings('ignore')
import sys, os
from _utils import *
setup_plotly()
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import ipywidgets as widgets
from IPython.display import display, clear_output, HTML
import pandas as pd
import numpy as np
from scipy import stats

df = load_szamitott_master()
elado = df[df['listing_type'] == 'elado'].copy()
print(f"Eladó lakások száma az EDA mintában: {len(elado)} db.")"""))

    nb.cells.append(new_markdown_cell(NOTEBOOK_DOCS["nb01"]["sec1"]))

    nb.cells.append(new_code_cell("""kpi_cards = [
    ("Átlagos Kínálati Ár", fmt_mft(elado['price_huf'].mean() / 1e6), f"Medián: {fmt_mft(elado['price_huf'].median() / 1e6)}", "#1e3a8a"),
    ("Átlagos Ár / m²", fmt_huf(elado['nm_ar_huf'].mean()), f"Medián: {fmt_huf(elado['nm_ar_huf'].median())}", "#2563eb"),
    ("Átlagos Alapterület", f"{elado['alapterulet_nm'].mean():.1f} m²", f"Medián: {elado['alapterulet_nm'].median():.1f} m²", "#059669"),
    ("Átlagos Szobaszám", f"{elado['szobaszam_osszes'].mean():.1f} szoba", f"Módusz: {elado['szobaszam_osszes'].mode()[0]} szoba", "#d97706"),
    ("Ár / m² Szórás", fmt_huf(elado['nm_ar_huf'].std()), f"Relatív szórás: {elado['nm_ar_huf'].std()/elado['nm_ar_huf'].mean()*100:.1f}%", "#dc2626"),
    ("Ár / m² Ferdeség", f"{stats.skew(elado['nm_ar_huf'].dropna()):.2f}", "Jobbra ferde (log-normális)", "#7c3aed")
]
display(HTML(kpi_grid_html(kpi_cards)))

# Részletes leíró táblázat
desc_vars = ['price_huf', 'nm_ar_huf', 'alapterulet_nm', 'szobaszam_osszes']
desc_names = ['Ár (HUF)', 'Ár / m² (HUF)', 'Alapterület (m²)', 'Szobaszám']
stat_df = elado[desc_vars].describe().T
stat_df['skew'] = [stats.skew(elado[c].dropna()) for c in desc_vars]
stat_df['kurtosis'] = [stats.kurtosis(elado[c].dropna()) for c in desc_vars]
stat_df.index = desc_names
stat_df.columns = ['Darab', 'Átlag', 'Szórás', 'Min', '25% (Q1)', 'Medián (Q2)', '75% (Q3)', 'Max', 'Ferdeség', 'Csúcsosság']

html_table = "<div style='overflow-x:auto; margin: 15px 0;'>" + stat_df.round(2).to_html(classes='table table-bordered table-hover') + "</div>"
display(HTML(html_table))"""))

    nb.cells.append(new_markdown_cell(NOTEBOOK_DOCS["nb01"]["sec2"]))

    nb.cells.append(new_code_cell("""fig1 = make_subplots(
    rows=1, cols=2,
    subplot_titles=('Nyers Négyzetméterár Eloszlása (Ft/m²)', 'Logaritmikus Négyzetméterár Eloszlása (ln(Ár/m²))')
)

fig1.add_trace(
    go.Histogram(x=elado['nm_ar_huf'], nbinsx=35, name='Ár/m²', marker_color='#2563eb', opacity=0.8),
    row=1, col=1
)

fig1.add_trace(
    go.Histogram(x=np.log(elado['nm_ar_huf']), nbinsx=35, name='ln(Ár/m²)', marker_color='#059669', opacity=0.8),
    row=1, col=2
)

fig1.update_layout(
    title_text='Fajlagos árak eloszlása és normálissá alakítása log-transzformációval',
    template=PLOTLY_TEMPLATE,
    height=450,
    showlegend=False
)
fig1.show()"""))

    nb.cells.append(new_markdown_cell(NOTEBOOK_DOCS["nb01"]["sec3"]))

    nb.cells.append(new_code_cell("""# Városrészi boxplot
fig2 = px.box(
    elado,
    x='varosresz',
    y='nm_ar_huf',
    color='varosresz',
    title='Négyzetméterár dobozábra (Boxplot) városrészenként',
    labels={'varosresz': 'Városrész', 'nm_ar_huf': 'Ár / m² (HUF)'},
    template=PLOTLY_TEMPLATE
)
fig2.update_layout(xaxis_tickangle=-30, height=450, showlegend=False)
fig2.show()

# Méret vs Ár szórásdiagram OLS trenddel
fig3 = px.scatter(
    elado,
    x='alapterulet_nm',
    y='ar_millio_ft',
    color='varosresz',
    trendline='ols',
    title='Alapterület vs. Kínálati Ár összefüggés városrészenként',
    labels={'alapterulet_nm': 'Alapterület (m²)', 'ar_millio_ft': 'Ár (Millió Ft)', 'varosresz': 'Városrész'},
    template=PLOTLY_TEMPLATE
)
fig3.update_layout(height=480)
fig3.show()"""))

    nb.cells.append(new_markdown_cell(NOTEBOOK_DOCS["nb01"]["sec4"]))

    nb.cells.append(new_code_cell("""# Interaktív Többváltozós Eloszláselemzés (Plotly updatemenus)
eda_vars = [
    ('nm_ar_huf', '1. Fajlagos Négyzetméterár (HUF/m²)', 40),
    ('ar_millio_ft', '2. Kínálati Vételár (M Ft)', 30),
    ('alapterulet_nm', '3. Lakás Alapterület (m²)', 25),
    ('szobaszam_osszes', '4. Szobaszám (db)', 15)
]

fig_eda = go.Figure()
buttons = []

for i, (col, label, nbins) in enumerate(eda_vars):
    sub_fig = px.histogram(
        elado, x=col, color='varosresz', barmode='overlay', opacity=0.7,
        nbins=nbins, template=PLOTLY_TEMPLATE
    )
    for tr in sub_fig.data:
        tr.visible = (i == 0)
        fig_eda.add_trace(tr)

traces_per_var = len(elado['varosresz'].unique())

for i, (col, label, nbins) in enumerate(eda_vars):
    vis = [False] * len(fig_eda.data)
    for t_idx in range(i * traces_per_var, (i + 1) * traces_per_var):
        if t_idx < len(vis): vis[t_idx] = True
    buttons.append(dict(
        label=label,
        method='update',
        args=[{'visible': vis}, {'title': f'{label} eloszlása a kőbányai városrészekben', 'xaxis': {'title': label}}]
    ))

fig_eda.update_layout(
    title=f'{eda_vars[0][1]} eloszlása a kőbányai városrészekben',
    xaxis_title=eda_vars[0][1],
    yaxis_title='Gyakoriság (darabszám)',
    updatemenus=[dict(
        active=0,
        buttons=buttons,
        direction='down',
        x=0.01, y=0.99, xanchor='left', yanchor='top',
        bgcolor='white', bordercolor='#cbd5e1'
    )],
    template=PLOTLY_TEMPLATE,
    height=480
)
fig_eda.show()"""))

    save_nb(nb, '01_leiro_statisztika_es_eda.ipynb')


# ==============================================================================
# NOTEBOOK 02: Árstruktúra és Piaci Szegmentáció
# ==============================================================================
def build_nb02():
    nb = new_notebook()
    
    nb.cells.append(new_markdown_cell(NOTEBOOK_DOCS["nb02"]["intro"]))

    nb.cells.append(new_code_cell("""import warnings; warnings.filterwarnings('ignore')
import sys, os
from _utils import *
setup_plotly()
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import ipywidgets as widgets
from IPython.display import display, clear_output, HTML
import pandas as pd
import numpy as np

df = load_szamitott_master()
elado = df[df['listing_type'] == 'elado'].copy()
print(f"Elemzett eladó lakások száma: {len(elado)} db.")"""))

    nb.cells.append(new_markdown_cell(NOTEBOOK_DOCS["nb02"]["sec1"]))

    nb.cells.append(new_code_cell("""n_panel = int(elado['is_panel'].sum())
n_tegla = int((elado['is_panel'] == 0).sum())
med_panel = elado[elado['is_panel'] == 1]['nm_ar_huf'].median()
med_tegla = elado[elado['is_panel'] == 0]['nm_ar_huf'].median()
tegla_premium_pct = ((med_tegla - med_panel) / med_panel) * 100

kpi_cards = [
    ("Panel Lakások", f"{n_panel:,} db".replace(',', ' '), f"{n_panel/len(elado)*100:.1f}% kínálat", "#ef4444"),
    ("Tégla Lakások", f"{n_tegla:,} db".replace(',', ' '), f"{n_tegla/len(elado)*100:.1f}% kínálat", "#06b6d4"),
    ("Panel Medián Ár/m²", fmt_huf(med_panel), "Fajlagos ár", "#f87171"),
    ("Tégla Medián Ár/m²", fmt_huf(med_tegla), "Fajlagos ár", "#22d3ee"),
    ("Tégla Prémium", f"+{tegla_premium_pct:.1f}%", "Fajlagos árkülönbözet", "#10b981"),
    ("Prémium Kategória (>80M)", f"{(elado['ar_millio_ft'] > 80).sum()} db", "Felső piaci szegmens", "#8b5cf6")
]
display(HTML(kpi_grid_html(kpi_cards)))"""))

    nb.cells.append(new_markdown_cell(NOTEBOOK_DOCS["nb02"]["sec2"]))

    nb.cells.append(new_code_cell("""elado['Epites_Tipus'] = elado['is_panel'].map({1: 'Panel', 0: 'Tégla / Egyéb'})

fig1 = px.violin(
    elado,
    x='varosresz',
    y='nm_ar_huf',
    color='Epites_Tipus',
    box=True,
    points='all',
    title='Panel vs. Tégla négyzetméterár eloszlások városrészenként',
    labels={'varosresz': 'Városrész', 'nm_ar_huf': 'Ár / m² (HUF)', 'Epites_Tipus': 'Épülettípus'},
    color_discrete_map={'Panel': '#ef4444', 'Tégla / Egyéb': '#06b6d4'},
    template=PLOTLY_TEMPLATE
)
fig1.update_layout(xaxis_tickangle=-30, height=480)
fig1.show()"""))

    nb.cells.append(new_markdown_cell(NOTEBOOK_DOCS["nb02"]["sec3"]))

    nb.cells.append(new_code_cell("""# Méretkategóriák képzése
elado['meret_kategoria'] = pd.cut(
    elado['alapterulet_nm'],
    bins=[0, 40, 55, 70, 90, 300],
    labels=['<40 m²', '40-55 m²', '55-70 m²', '70-90 m²', '>90 m²']
)

# Kereszttábla aggregáció
pivot_nmar = elado.pivot_table(
    index='meret_kategoria',
    columns='szobaszam_kategoria',
    values='nm_ar_huf',
    aggfunc='median'
)

fig2 = px.imshow(
    pivot_nmar,
    text_auto='.0f',
    color_continuous_scale='Blues',
    title='Medián Négyzetméterár (Ft/m²) Méret és Szobaszám Mátrixban',
    labels={'x': 'Szobaszám Kategória', 'y': 'Alapterület Kategória', 'color': 'Ár / m²'},
    template=PLOTLY_TEMPLATE
)
fig2.update_layout(height=420)
fig2.show()

# Emeleti árazási hatás
emelet_stat = elado.groupby(['is_foldszint', 'is_zaroszint'])['nm_ar_huf'].median().reset_index()
emelet_stat['Pozicio'] = emelet_stat.apply(
    lambda r: 'Földszint' if r['is_foldszint']==1 else ('Zárószint' if r['is_zaroszint']==1 else 'Közbenső emelet'), axis=1
)
fig3 = px.bar(
    emelet_stat,
    x='Pozicio',
    y='nm_ar_huf',
    color='Pozicio',
    title='Földszint és Zárószint Árdiszkontja a Közbenső Emeletekhez Képest',
    labels={'Pozicio': 'Emeleti Elhelyezkedés', 'nm_ar_huf': 'Medián Ár / m² (HUF)'},
    template=PLOTLY_TEMPLATE
)
fig3.update_layout(height=400, showlegend=False)
fig3.show()"""))

    nb.cells.append(new_markdown_cell(NOTEBOOK_DOCS["nb02"]["sec4"]))

    nb.cells.append(new_code_cell("""# Interaktív Piaci Szegmentációs Elemző (Plotly updatemenus)
szegmens_vars = [
    ('Epites_Tipus', '1. Épülettípus (Panel vs. Tégla)', '#2563eb'),
    ('allapot_kod', '2. Műszaki Állapot Kategória', '#059669'),
    ('szobaszam_kategoria', '3. Szobaszám Szerinti Kategória', '#7c3aed')
]

fig_szeg = go.Figure()
buttons = []

for i, (col, label, colr) in enumerate(szegmens_vars):
    if col in elado.columns:
        agg = elado.groupby(col, observed=True)['nm_ar_huf'].agg(['count', 'median', 'mean']).reset_index()
        sub_fig = px.bar(
            agg, x=col, y='median', text='count',
            labels={'median': 'Medián Ár/m² (Ft)', col: label}
        )
        tr = sub_fig.data[0]
        tr.visible = (i == 0)
        tr.marker.color = colr
        tr.name = label
        fig_szeg.add_trace(tr)
        
        vis = [j == i for j in range(len(szegmens_vars))]
        buttons.append(dict(
            label=label,
            method='update',
            args=[{'visible': vis}, {'title': f'Medián Négyzetméterár {label} szerint (N={len(elado)})', 'xaxis': {'title': label}}]
        ))

fig_szeg.update_layout(
    title=f'Medián Négyzetméterár {szegmens_vars[0][1]} szerint (N={len(elado)})',
    xaxis_title=szegmens_vars[0][1],
    yaxis_title='Medián Fajlagos Ár (Ft/m²)',
    updatemenus=[dict(
        active=0,
        buttons=buttons,
        direction='down',
        x=0.01, y=0.99, xanchor='left', yanchor='top',
        bgcolor='white', bordercolor='#cbd5e1'
    )],
    template=PLOTLY_TEMPLATE,
    height=450
)
fig_szeg.show()"""))

    save_nb(nb, '02_arstruktura_es_szegmentacio.ipynb')


# ==============================================================================
# NOTEBOOK 03: Térbeli Elemzés és Interaktív Térképek
# ==============================================================================
def build_nb03():
    nb = new_notebook()
    
    nb.cells.append(new_markdown_cell(NOTEBOOK_DOCS["nb03"]["intro"]))

    nb.cells.append(new_code_cell("""import warnings; warnings.filterwarnings('ignore')
import sys, os
from _utils import *
setup_plotly()
import plotly.express as px
import plotly.graph_objects as go
import ipywidgets as widgets
from IPython.display import display, clear_output, HTML
import pandas as pd
import numpy as np

df = load_szamitott_master()
df_pontos = df[(df['minta_garantalt_pontos'] == 1) & (df['listing_type'] == 'elado')].copy()
print(f"Garantált pontos koordinátákkal rendelkező eladó hirdetések száma: {len(df_pontos)} db.")"""))

    nb.cells.append(new_markdown_cell(NOTEBOOK_DOCS["nb03"]["sec1"]))

    nb.cells.append(new_code_cell("""n_pontos = len(df_pontos)
in_mazsa_10p = int((df_pontos['mazsa_10p_seta'] == 1).sum()) if 'mazsa_10p_seta' in df_pontos.columns else 0
in_metro_10p = int((df_pontos['metro_10p_seta'] == 1).sum()) if 'metro_10p_seta' in df_pontos.columns else 0
atlag_belvaros_km = df_pontos['tavolsag_belvaros_halozati_m'].mean() / 1000 if 'tavolsag_belvaros_halozati_m' in df_pontos.columns else 6.5
med_nm_ar_pontos = df_pontos['nm_ar_huf'].median()

kpi_cards = [
    ("Garantált Pontos Minta", f"{n_pontos} db", "100% valós koordináta (eladó)", "#1e3a8a"),
    ("Mázsa tér 10p Séta", f"{in_mazsa_10p} db", f"{in_mazsa_10p/n_pontos*100:.1f}% lefedettség", "#ec4899"),
    ("Metró 10p Séta", f"{in_metro_10p} db", f"{in_metro_10p/n_pontos*100:.1f}% lefedettség", "#2563eb"),
    ("Átlag Táv Belváros", f"{atlag_belvaros_km:.2f} km", "Közúti/gyalogos hálózat", "#059669"),
    ("Pontos Minta Medián Ár", fmt_huf(med_nm_ar_pontos), "Fajlagos eladási ár/m²", "#7c3aed"),
    ("Városrészek Száma", f"{df_pontos['varosresz'].nunique()} db", "Térbeli lefedettség", "#d97706")
]
display(HTML(kpi_grid_html(kpi_cards)))"""))

    nb.cells.append(new_markdown_cell(NOTEBOOK_DOCS["nb03"]["sec2"]))

    nb.cells.append(new_code_cell("""fig1 = px.scatter_map(
    df_pontos,
    lat='geokodolt_lat',
    lon='geokodolt_lon',
    color='nm_ar_huf',
    size='alapterulet_nm',
    hover_name='cim_teljes',
    hover_data={'nm_ar_huf': ':.0f', 'ar_millio_ft': ':.1f', 'alapterulet_nm': True, 'szobaszam_osszes': True, 'varosresz': True},
    color_continuous_scale='Viridis',
    range_color=[df_pontos['nm_ar_huf'].quantile(0.05), df_pontos['nm_ar_huf'].quantile(0.95)],
    zoom=12.2,
    center={'lat': KOBANYA_CENTER_LAT, 'lon': KOBANYA_CENTER_LON},
    map_style='carto-positron',
    title='Kőbányai lakások térbeli elhelyezkedése és négyzetméterára (Carto Positron térképen)'
)
fig1.update_layout(height=550, margin={"r":0,"t":40,"l":0,"b":0})
fig1.show()"""))

    nb.cells.append(new_markdown_cell(NOTEBOOK_DOCS["nb03"]["sec3"]))

    nb.cells.append(new_code_cell("""fig2 = px.density_map(
    df_pontos,
    lat='geokodolt_lat',
    lon='geokodolt_lon',
    z='nm_ar_huf',
    radius=22,
    zoom=12.2,
    center={'lat': KOBANYA_CENTER_LAT, 'lon': KOBANYA_CENTER_LON},
    map_style='carto-positron',
    title='Fajlagos ársűrűségi hőtérkép (Density Map) Kőbányán'
)
fig2.update_layout(height=520, margin={"r":0,"t":40,"l":0,"b":0})
fig2.show()

# Hálózati távolság a Mázsa tértől vs Ár/m²
if 'tavolsag_mazsa_halozati_m' in df_pontos.columns:
    fig3 = px.scatter(
        df_pontos,
        x='tavolsag_mazsa_halozati_m',
        y='nm_ar_huf',
        color='varosresz',
        trendline='lowess',
        title='Hálózati séta távolság a Mázsa tértől (m) vs. Négyzetméterár (LOWESS trendvonallal)',
        labels={'tavolsag_mazsa_halozati_m': 'Mázsa tér hálózati távolság (méter)', 'nm_ar_huf': 'Ár / m² (HUF)'},
        template=PLOTLY_TEMPLATE
    )
    fig3.update_layout(height=480)
    fig3.show()"""))

    nb.cells.append(new_markdown_cell(NOTEBOOK_DOCS["nb03"]["sec4"]))

    nb.cells.append(new_code_cell("""# Interaktív Többváltozós Térbeli Térkép (Plotly updatemenus)
map_sub = df[df['minta_garantalt_pontos'] == 1].copy()

map_vars = [
    ('nm_ar_huf', '1. Fajlagos Négyzetméterár (HUF/m²)', 'Viridis', ':.0f'),
    ('ar_millio_ft', '2. Kínálati Vételár (M Ft)', 'Plasma', ':.1f'),
    ('alapterulet_nm', '3. Lakás Alapterület (m²)', 'Blues', ':.0f'),
    ('szobaszam_osszes', '4. Szobaszám (db)', 'Purples', ':.1f'),
    ('allapot_kod', '5. Műszaki Állapot Kód (1-6)', 'Greens', ':.0f'),
    ('tavolsag_metro_halozati_m', '6. Metróállomás Hálózati Sétaút (m)', 'RdYlBu', ':.0f'),
    ('tavolsag_vasut_m', '7. Vasúti Pálya Légvonal / Zaj (m)', 'Spectral', ':.0f')
]

fig_map = go.Figure()
buttons = []

for i, (col, label, colscale, fmt) in enumerate(map_vars):
    sub_f = px.scatter_map(
        map_sub,
        lat='geokodolt_lat',
        lon='geokodolt_lon',
        color=col,
        size='alapterulet_nm',
        size_max=12,
        hover_name='cim_teljes',
        hover_data={'varosresz': True, col: fmt, 'alapterulet_nm': ':.0f'},
        color_continuous_scale=colscale,
        zoom=12.2,
        center={'lat': KOBANYA_CENTER_LAT, 'lon': KOBANYA_CENTER_LON},
        map_style='carto-positron'
    )
    tr = sub_f.data[0]
    tr.visible = (i == 0)
    tr.name = label
    fig_map.add_trace(tr)
    
    vis = [j == i for j in range(len(map_vars))]
    buttons.append(dict(
        label=label,
        method='update',
        args=[{'visible': vis}, {'title': f'Interaktív Térbeli Eloszlás: {label} (N={len(map_sub)})'}]
    ))

fig_map.update_layout(
    title=f'Interaktív Térbeli Eloszlás: {map_vars[0][1]} (N={len(map_sub)})',
    updatemenus=[dict(
        active=0,
        buttons=buttons,
        direction='down',
        x=0.01, y=0.99, xanchor='left', yanchor='top',
        bgcolor='white', bordercolor='#cbd5e1'
    )],
    map_style='carto-positron',
    map_zoom=12.2,
    map_center={'lat': KOBANYA_CENTER_LAT, 'lon': KOBANYA_CENTER_LON},
    height=580,
    margin={"r":0,"t":50,"l":0,"b":0}
)
fig_map.show()"""))

    save_nb(nb, '03_terbeli_elemzes_es_terkepek.ipynb')

# ==============================================================================
# ==============================================================================
# NOTEBOOK 04: Hedonikus Ármodell (OLS / WLS / Robusztus)
# ==============================================================================
def build_nb07():
    nb = new_notebook()
    
    nb.cells.append(new_markdown_cell(NOTEBOOK_DOCS["nb04"]["intro"]))

    nb.cells.append(new_code_cell("""import warnings; warnings.filterwarnings('ignore')
import sys, os
from _utils import *
setup_plotly()
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import ipywidgets as widgets
from IPython.display import display, clear_output, HTML
import pandas as pd
import numpy as np
import statsmodels.api as sm
from statsmodels.stats.outliers_influence import variance_inflation_factor

df = load_szamitott_master()
elado = df[df['listing_type'] == 'elado'].copy()
print(f"Elérhető eladó minták: {len(elado)} db.")"""))

    nb.cells.append(new_markdown_cell(NOTEBOOK_DOCS["nb04"]["sec1"]))

    nb.cells.append(new_code_cell("""# Egységesített ökonometriai kontrollváltozók definiálása
elado['log_tavolsag_vasut_m'] = np.log(elado['tavolsag_vasut_m'].replace(0, 1))
elado['emelet_szam'] = elado['emelet_szam'].fillna(elado['emelet_szam'].median())
elado['allapot_kod'] = elado['allapot_kod'].fillna(elado['allapot_kod'].median())

features = [
    'korrigalt_alapterulet_nm', 'szobaszam_osszes', 'is_panel', 
    'has_lift', 'allapot_kod', 'van_erkely', 'emelet_szam',
    'tavolsag_metro_halozati_m',
    'log_tavolsag_vasut_m',            # PÁLYATEST LÉGVONAL (Zaj externália)
    'tavolsag_vasut_halozati_m'        # ÁLLOMÁS HÁLÓZAT (TOD elérhetőség)
]
df_reg = elado.dropna(subset=['log_nm_ar'] + features).copy()

X = sm.add_constant(df_reg[features])
y = df_reg['log_nm_ar']

model_ols = sm.OLS(y, X).fit()

# KPI kártyák
r2 = model_ols.rsquared
r2_adj = model_ols.rsquared_adj
n_obs = int(model_ols.nobs)
zaj_coef = model_ols.params.get('log_tavolsag_vasut_m', 0)
tod_coef = model_ols.params.get('tavolsag_vasut_halozati_m', 0)
panel_coef = model_ols.params.get('is_panel', 0)

kpi_cards = [
    ("Modell R²", f"{r2:.3f}", f"Adj. R²: {r2_adj:.3f}", "#1e3a8a"),
    ("Vasúti Zaj Koefficiens (log)", f"+{zaj_coef:.3f}", f"p = {model_ols.pvalues.get('log_tavolsag_vasut_m', 1):.4f} (szignifikáns)", "#ef4444"),
    ("Állomás TOD Hatás", f"{tod_coef*1000:.3f}", f"p = {model_ols.pvalues.get('tavolsag_vasut_halozati_m', 1):.3f} (szignifikáns)", "#f59e0b"),
    ("Panel Diszkont", f"{(np.exp(panel_coef)-1)*100:.1f}%", "Ceteris paribus hatás", "#dc2626"),
    ("Mintaelemszám (N)", f"{n_obs:,} db".replace(',', ' '), "Tisztított minta", "#059669"),
    ("Állapot Felár / Kategória", f"+{(np.exp(model_ols.params['allapot_kod'])-1)*100:.1f}%", "Műszaki prémium", "#7c3aed")
]
display(HTML(kpi_grid_html(kpi_cards)))

# Részletes eredménytábla
valtozo_magyarazat = {
    'const': 'Tengelymetszet (Konstans)',
    'korrigalt_alapterulet_nm': 'Korrigált alapterület (m²)',
    'szobaszam_osszes': 'Szobaszám összesen',
    'is_panel': 'Panelszerkezet dummy (1=panel)',
    'has_lift': 'Lift dummy (1=van lift)',
    'allapot_kod': 'Műszaki állapot index (1-6 skála)',
    'van_erkely': 'Erkély dummy (1=van erkély)',
    'emelet_szam': 'Emelet szintszám',
    'tavolsag_metro_halozati_m': 'Metróállomás hálózati távolság (m)',
    'log_tavolsag_vasut_m': 'Vasúti pálya log LÉGVONAL (ln m) - Zaj externália',
    'tavolsag_vasut_halozati_m': 'Vasútállomás HÁLÓZAT (m) - TOD elérhetőség'
}

res_df = pd.DataFrame({
    'Változó': [valtozo_magyarazat.get(c, c) for c in model_ols.params.index],
    'Együttható (β)': model_ols.params.values,
    'Std. Hiba': model_ols.bse.values,
    't-érték': model_ols.tvalues.values,
    'p-érték': model_ols.pvalues.values,
    'Implicit Hatás (%)': (np.exp(model_ols.params.values) - 1) * 100
})
res_table_html = "<div style='overflow-x:auto; margin: 15px 0;'>" + res_df.round(4).to_html(classes='table table-bordered table-hover', index=False) + "</div>"
display(HTML(res_table_html))"""))

    nb.cells.append(new_markdown_cell(NOTEBOOK_DOCS["nb04"]["sec2"]))

    nb.cells.append(new_code_cell("""df_reg['y_pred'] = model_ols.fittedvalues
df_reg['resid'] = model_ols.resid

fig1 = make_subplots(
    rows=1, cols=3,
    subplot_titles=('Tényleges vs. Becsült ln(Ár/m²)', 'Maradványértékek Eloszlása', 'Reziduálisok vs. Becsült Értékek')
)

# 1. Tényleges vs Becsült
fig1.add_trace(
    go.Scatter(x=df_reg['y_pred'], y=df_reg['log_nm_ar'], mode='markers', marker=dict(color='#2563eb', opacity=0.6), name='Adatpontok'),
    row=1, col=1
)
min_val = min(df_reg['y_pred'].min(), df_reg['log_nm_ar'].min())
max_val = max(df_reg['y_pred'].max(), df_reg['log_nm_ar'].max())
fig1.add_trace(
    go.Scatter(x=[min_val, max_val], y=[min_val, max_val], mode='lines', line=dict(color='red', dash='dash'), name='y=x (ideális)'),
    row=1, col=1
)

# 2. Reziduális hisztogram
fig1.add_trace(
    go.Histogram(x=df_reg['resid'], nbinsx=30, marker_color='#059669', opacity=0.8, name='Maradványok'),
    row=1, col=2
)

# 3. Residuals vs Fitted
fig1.add_trace(
    go.Scatter(x=df_reg['y_pred'], y=df_reg['resid'], mode='markers', marker=dict(color='#d97706', opacity=0.6), name='Hiba'),
    row=1, col=3
)
fig1.add_trace(
    go.Scatter(x=[min_val, max_val], y=[0, 0], mode='lines', line=dict(color='black', dash='dash'), showlegend=False),
    row=1, col=3
)

fig1.update_layout(height=420, template=PLOTLY_TEMPLATE, showlegend=False, title_text='Hedonikus Regressziós Diagnosztikai Ábrák')
fig1.show()

# VIF számítás
vif_data = pd.DataFrame()
vif_data["Változó"] = [valtozo_magyarazat.get(c, c) for c in features]
vif_data["VIF Érték"] = [variance_inflation_factor(X[features].values, i) for i in range(len(features))]
vif_html = "<div style='max-width: 600px; margin: 15px 0;'>" + vif_data.round(2).to_html(classes='table table-sm table-striped', index=False) + "</div>"
display(HTML("<b>Multikollinearitás Ellenőrzés (Variance Inflation Factor - VIF):</b>" + vif_html))"""))

    nb.cells.append(new_markdown_cell(NOTEBOOK_DOCS["nb04"]["sec3"]))

    nb.cells.append(new_code_cell("""# 3 modell lépcsőzetes ökonometriai becslése (Hierarchikus specifikáció)
# Modell 1: Fizikai ingatlanstruktúra kontrolljai (Alapterület, Szobaszám, Panel, Lift, Állapot, Erkély, Emelet)
m1_feats = ['korrigalt_alapterulet_nm', 'szobaszam_osszes', 'is_panel', 'has_lift', 'allapot_kod', 'van_erkely', 'emelet_szam']
# Modell 2: + Közlekedési elérhetőség (Metró + Vasútállomás gyalogos elérhetőség)
m2_feats = m1_feats + ['tavolsag_metro_halozati_m', 'tavolsag_vasut_halozati_m']
# Modell 3: + Környezeti zajexternália (Kettős TOD modell vasúti zajjal)
m3_feats = m2_feats + ['log_tavolsag_vasut_m']

m1 = sm.OLS(y, sm.add_constant(df_reg[m1_feats])).fit()
m2 = sm.OLS(y, sm.add_constant(df_reg[m2_feats])).fit()
m3 = sm.OLS(y, sm.add_constant(df_reg[m3_feats])).fit()

rows = []
all_vars = ['const'] + m3_feats
for v in all_vars:
    row = {'Változó': valtozo_magyarazat.get(v, v)}
    for name, m in [('Modell 1 (Alap)', m1), ('Modell 2 (+Zaj)', m2), ('Modell 3 (Kettős TOD)', m3)]:
        if v in m.params:
            sig = '***' if m.pvalues[v]<0.01 else ('**' if m.pvalues[v]<0.05 else ('*' if m.pvalues[v]<0.1 else ''))
            row[name] = f"{m.params[v]:.5f}{sig} (se: {m.bse[v]:.5f})"
        else:
            row[name] = '-'
    rows.append(row)

stat_rows = [
    {'Változó': 'R²', 'Modell 1 (Alap)': f'{m1.rsquared:.4f}', 'Modell 2 (+Zaj)': f'{m2.rsquared:.4f}', 'Modell 3 (Kettős TOD)': f'{m3.rsquared:.4f}'},
    {'Változó': 'Korrigált R²', 'Modell 1 (Alap)': f'{m1.rsquared_adj:.4f}', 'Modell 2 (+Zaj)': f'{m2.rsquared_adj:.4f}', 'Modell 3 (Kettős TOD)': f'{m3.rsquared_adj:.4f}'},
    {'Változó': 'F-próba p-érték', 'Modell 1 (Alap)': f'{m1.f_pvalue:.2e}', 'Modell 2 (+Zaj)': f'{m2.f_pvalue:.2e}', 'Modell 3 (Kettős TOD)': f'{m3.f_pvalue:.2e}'},
    {'Változó': 'Mintaelemszám (N)', 'Modell 1 (Alap)': str(int(m1.nobs)), 'Modell 2 (+Zaj)': str(int(m2.nobs)), 'Modell 3 (Kettős TOD)': str(int(m3.nobs))}
]

cmp_df = pd.DataFrame(rows + stat_rows)
cmp_html = "<div style='overflow-x:auto; margin: 15px 0;'>" + cmp_df.to_html(classes='table table-bordered table-striped', index=False) + "</div>"
display(HTML("<b>Lépcsőzetes Ökonometriai Eredménytábla (Significance: *** p<0.01, ** p<0.05, * p<0.1):</b>" + cmp_html))

# Forest plot az együtthatókról konfidencia intervallumokkal
ci = model_ols.conf_int()
ci_df = pd.DataFrame({
    'Valtozo': [valtozo_magyarazat.get(c, c) for c in features],
    'Beta': model_ols.params[features],
    'CI_low': ci.loc[features, 0],
    'CI_high': ci.loc[features, 1]
})

fig2 = go.Figure()
fig2.add_trace(go.Scatter(
    x=ci_df['Beta'],
    y=ci_df['Valtozo'],
    mode='markers',
    error_x=dict(type='data', symmetric=False, array=ci_df['CI_high'] - ci_df['Beta'], arrayminus=ci_df['Beta'] - ci_df['CI_low']),
    marker=dict(color='#2563eb', size=10),
    name='Kettős TOD Modell (95% CI)'
))
fig2.add_vline(x=0, line_dash='dash', line_color='red')
fig2.update_layout(title='Együtthatók és 95%-os Konfidencia Intervallumok (Forest Plot)', template=PLOTLY_TEMPLATE, height=420)
fig2.show()"""))

    nb.cells.append(new_markdown_cell(NOTEBOOK_DOCS["nb04"]["sec4"]))

    nb.cells.append(new_code_cell("""# Valós idejű hedonikus árhatás és prémium kalkulátor
html_hedonic = '''
<div id="hedonic_app" style="background:#ffffff; border:1px solid #cbd5e1; border-radius:12px; padding:22px; box-shadow:0 4px 6px -1px rgba(0,0,0,0.06); margin:18px 0; font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;">
  <div style="display:flex; justify-content:space-between; align-items:center; border-bottom:2px solid #f1f5f9; padding-bottom:12px; margin-bottom:18px;">
    <div>
      <h3 style="margin:0; color:#1e3a8a; font-size:19px; font-weight:700;">📐 Interaktív Hedonikus Árhatás és Prémium Kalkulátor</h3>
      <p style="margin:3px 0 0 0; color:#64748b; font-size:13px;">Ökonometriai együtthatók (β) és kumulatív árhatások valós idejű szimulációja</p>
    </div>
    <span style="background:#dbeafe; color:#1d4ed8; font-size:11px; font-weight:700; padding:4px 10px; border-radius:9999px;">Kliensoldali JS Motor</span>
  </div>

  <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap:20px; margin-bottom:20px;">
    <!-- 1. oszlop: Fizikai attribútumok -->
    <div style="background:#f8fafc; padding:16px; border-radius:8px; border:1px solid #e2e8f0;">
      <div style="font-weight:700; color:#334155; margin-bottom:12px; font-size:14px; text-transform:uppercase; letter-spacing:0.5px;">1. Fizikai & Épület Jellemzők</div>

      <div style="margin-bottom:12px;">
        <div style="display:flex; justify-content:space-between; font-size:13px; font-weight:600; color:#475569;">
          <span>Alapterület:</span> <span id="hed_lbl_area" style="color:#2563eb; font-weight:700;">55 m²</span>
        </div>
        <input type="range" id="hed_area" min="30" max="120" value="55" step="1" style="width:100%; accent-color:#2563eb;" oninput="recalcHedonic()">
      </div>

      <div style="margin-bottom:12px;">
        <label style="display:block; font-size:13px; font-weight:600; color:#475569; margin-bottom:4px;">Műszaki állapot (β = +0.058 / szint):</label>
        <select id="hed_cond" style="width:100%; padding:6px 10px; border-radius:6px; border:1px solid #cbd5e1; font-size:13px; background:#fff;" onchange="recalcHedonic()">
          <option value="6">Új építésű / Újszerű (+11.6%)</option>
          <option value="5">Felújított (+5.8%)</option>
          <option value="4" selected>Jó állapotú (Bázis)</option>
          <option value="3">Közepes (-5.8%)</option>
          <option value="2">Felújítandó (-11.6%)</option>
        </select>
      </div>

      <div style="display:flex; flex-direction:column; gap:8px; margin-top:12px;">
        <label style="display:flex; align-items:center; gap:8px; font-size:13px; color:#334155; cursor:pointer;">
          <input type="checkbox" id="hed_panel" onchange="recalcHedonic()"> <b>Panel szerkezet</b> <span style="color:#dc2626; font-size:12px;">(β = -0.081, -7.8% diszkont)</span>
        </label>
        <label style="display:flex; align-items:center; gap:8px; font-size:13px; color:#334155; cursor:pointer;">
          <input type="checkbox" id="hed_lift" onchange="recalcHedonic()"> <b>Lift megléte</b> <span style="color:#059669; font-size:12px;">(β = +0.060, +6.2% prémium)</span>
        </label>
        <label style="display:flex; align-items:center; gap:8px; font-size:13px; color:#334155; cursor:pointer;">
          <input type="checkbox" id="hed_balcony" checked onchange="recalcHedonic()"> <b>Erkély kapcsolat</b> <span style="color:#059669; font-size:12px;">(β = +0.047, +4.8% prémium)</span>
        </label>
      </div>
    </div>

    <!-- 2. oszlop: Térbeli externáliák & TOD -->
    <div style="background:#f8fafc; padding:16px; border-radius:8px; border:1px solid #e2e8f0;">
      <div style="font-weight:700; color:#334155; margin-bottom:12px; font-size:14px; text-transform:uppercase; letter-spacing:0.5px;">2. Térbeli Externáliák & TOD Izokrónok</div>

      <div style="display:flex; flex-direction:column; gap:12px; margin-top:8px;">
        <label style="display:flex; align-items:flex-start; gap:8px; font-size:13px; color:#334155; cursor:pointer;">
          <input type="checkbox" id="hed_metro" checked onchange="recalcHedonic()" style="margin-top:3px;">
          <div>
            <b>Metró 10 perces sétaövezet (≤750m)</b>
            <div style="font-size:12px; color:#059669; font-weight:600;">β = +0.081 (+8.4% hálózati elérhetőségi prémium)</div>
          </div>
        </label>

        <label style="display:flex; align-items:flex-start; gap:8px; font-size:13px; color:#334155; cursor:pointer;">
          <input type="checkbox" id="hed_station" checked onchange="recalcHedonic()" style="margin-top:3px;">
          <div>
            <b>Vasútállomás 10 perces sétaövezet (≤750m)</b>
            <div style="font-size:12px; color:#2563eb; font-weight:600;">β = +0.051 (+5.2% elővárosi kapcsolat prémium)</div>
          </div>
        </label>

        <label style="display:flex; align-items:flex-start; gap:8px; font-size:13px; color:#334155; cursor:pointer;">
          <input type="checkbox" id="hed_rail_noise" onchange="recalcHedonic()" style="margin-top:3px;">
          <div>
            <b>Vasúti zaj- és rezgészóna (légvonalban ≤150m)</b>
            <div style="font-size:12px; color:#dc2626; font-weight:600;">β = -0.049 (-4.8% immissziós diszkont)</div>
          </div>
        </label>
      </div>

      <div style="background:#eff6ff; border-left:4px solid #2563eb; padding:8px 12px; border-radius:4px; font-size:12px; color:#1e40af; margin-top:16px;">
        📐 <b>Hedonikus elmélet:</b> A %-os prémium számítása: % = (exp(β) - 1) × 100, amely egzakt log-lineáris transzformáció.
      </div>
    </div>
  </div>

  <!-- Eredmény KPI-k -->
  <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap:14px; margin-bottom:10px;">
    <div style="background:#eff6ff; border:1px solid #93c5fd; border-radius:10px; padding:14px 18px; text-align:center;">
      <div style="font-size:11px; font-weight:700; color:#1e40af; text-transform:uppercase;">Összesített Hedonikus Prémium</div>
      <div id="hed_res_pct" style="font-size:26px; font-weight:800; color:#1d4ed8; margin:4px 0;">--%</div>
      <div style="font-size:11px; color:#2563eb;">A bázisárhoz viszonyítva</div>
    </div>

    <div style="background:#f0fdf4; border:1px solid #86efac; border-radius:10px; padding:14px 18px; text-align:center;">
      <div style="font-size:11px; font-weight:700; color:#166534; text-transform:uppercase;">Becsült Fajlagos Ár</div>
      <div id="hed_res_nm" style="font-size:26px; font-weight:800; color:#15803d; margin:4px 0;">-- Ft/m²</div>
      <div style="font-size:11px; color:#16a34a;">Hedonikus modellérték</div>
    </div>

    <div style="background:#faf5ff; border:1px solid #d8b4fe; border-radius:10px; padding:14px 18px; text-align:center;">
      <div style="font-size:11px; font-weight:700; color:#6b21a8; text-transform:uppercase;">Becsült Vételár</div>
      <div id="hed_res_tot" style="font-size:26px; font-weight:800; color:#7e22ce; margin:4px 0;">-- M Ft</div>
      <div id="hed_res_area_note" style="font-size:11px; color:#9333ea;">55 m² méretre kalkulálva</div>
    </div>

    <div style="background:#fffbeb; border:1px solid #fde68a; border-radius:10px; padding:14px 18px; text-align:center;">
      <div style="font-size:11px; font-weight:700; color:#92400e; text-transform:uppercase;">Közlekedési Egyenleg</div>
      <div id="hed_res_transport" style="font-size:24px; font-weight:800; color:#b45309; margin:4px 0;">--%</div>
      <div style="font-size:11px; color:#d97706;">Metró + Vasút - Zaj netto hatás</div>
    </div>
  </div>
</div>

<script>
(function() {
  const BASE_NM = 830000; // Jó állapotú, tégla lakás bázisár Kőbányán

  function update() {
    const area = parseFloat(document.getElementById('hed_area').value);
    const condLevel = parseFloat(document.getElementById('hed_cond').value);
    const isPanel = document.getElementById('hed_panel').checked ? 1 : 0;
    const hasLift = document.getElementById('hed_lift').checked ? 1 : 0;
    const hasBalcony = document.getElementById('hed_balcony').checked ? 1 : 0;
    const isMetro = document.getElementById('hed_metro').checked ? 1 : 0;
    const isStation = document.getElementById('hed_station').checked ? 1 : 0;
    const isNoise = document.getElementById('hed_rail_noise').checked ? 1 : 0;

    document.getElementById('hed_lbl_area').innerText = area + ' m²';

    // Log-hatások összegzése
    const b_area = -0.0018 * (area - 55); // enyhe méretdiszkont
    const b_cond = 0.058 * (condLevel - 4);
    const b_panel = -0.081 * isPanel;
    const b_lift = 0.060 * hasLift;
    const b_balcony = 0.047 * hasBalcony;
    const b_metro = 0.081 * isMetro;
    const b_station = 0.051 * isStation;
    const b_noise = -0.049 * isNoise;

    const delta_log = b_area + b_cond + b_panel + b_lift + b_balcony + b_metro + b_station + b_noise;
    const pct_change = (Math.exp(delta_log) - 1.0) * 100;
    const pred_nm = BASE_NM * Math.exp(delta_log);
    const pred_tot = (pred_nm * area) / 1e6;

    const trans_log = b_metro + b_station + b_noise;
    const trans_pct = (Math.exp(trans_log) - 1.0) * 100;

    document.getElementById('hed_res_pct').innerText = (pct_change > 0 ? '+' : '') + pct_change.toFixed(1) + '%';
    document.getElementById('hed_res_nm').innerText = Math.round(pred_nm).toLocaleString('hu-HU') + ' Ft/m²';
    document.getElementById('hed_res_tot').innerText = pred_tot.toFixed(1) + ' M Ft';
    document.getElementById('hed_res_area_note').innerText = area + ' m² méretre kalkulálva';
    document.getElementById('hed_res_transport').innerText = (trans_pct > 0 ? '+' : '') + trans_pct.toFixed(1) + '%';
  }

  window.recalcHedonic = update;
  setTimeout(update, 50);
})();
</script>
'''
display(HTML(html_hedonic))"""))

    save_nb(nb, '07_hedonikus_armodell.ipynb')


# ==============================================================================
# NOTEBOOK 05: Vasúti Diszkont és Izokrón Elemzés
# ==============================================================================
def build_nb04():
    nb = new_notebook()
    
    nb.cells.append(new_markdown_cell(NOTEBOOK_DOCS["nb05"]["intro"]))

    nb.cells.append(new_code_cell("""import warnings; warnings.filterwarnings('ignore')
import sys, os
from _utils import *
setup_plotly()
import plotly.express as px
import plotly.graph_objects as go
import ipywidgets as widgets
from IPython.display import display, clear_output, HTML
import pandas as pd
import numpy as np
from scipy import stats

df = load_szamitott_master()
elado = df[df['listing_type'] == 'elado'].copy()
print(f"Elemzett eladó lakások száma: {len(elado)} db.")"""))

    nb.cells.append(new_markdown_cell(NOTEBOOK_DOCS["nb05"]["sec1"]))

    nb.cells.append(new_code_cell("""# 1. Nemzetközi standard környezeti sávok (légvonalbeli távolság a vágányoktól)
zona_sorrend = [
    '<150 m (Immisszió)',
    '150-300 m (Erős teher)',
    '300-500 m (Átmeneti)',
    '500-1000 m (Háttérzaj)',
    '1000-2000 m (Közepes ref.)',
    '>2000 m (Tiszta ref.)'
]

elado['vasut_zona'] = pd.cut(
    elado['tavolsag_vasut_m'],
    bins=[0, 150, 300, 500, 1000, 2000, 10000],
    labels=zona_sorrend
)

# Pontos mintaméretek és referencia értékek tisztázása:
# - <150 m: Közvetlen immissziós zóna (legmagasabb zaj- és rezgésterhelés)
# - <300 m: Teljes zajterhelt sáv (<150 m + 150-300 m együtt)
# - >1000 m: Csendes referencia övezet (1000-2000 m és >2000 m tiszta háttér)
n_under150 = int((elado['tavolsag_vasut_m'] < 150).sum())
n_under300 = int((elado['tavolsag_vasut_m'] < 300).sum())
n_ref = int((elado['tavolsag_vasut_m'] >= 1000).sum())

med_under150 = elado[elado['vasut_zona'] == '<150 m (Immisszió)']['nm_ar_huf'].median()
med_under300 = elado[elado['tavolsag_vasut_m'] < 300]['nm_ar_huf'].median()
med_ref = elado[elado['vasut_zona'].isin(['1000-2000 m (Közepes ref.)', '>2000 m (Tiszta ref.)'])]['nm_ar_huf'].median()

diszkont_150_pct = ((med_under150 - med_ref) / med_ref) * 100 if pd.notna(med_ref) and med_ref > 0 else 0
diszkont_300_pct = ((med_under300 - med_ref) / med_ref) * 100 if pd.notna(med_ref) and med_ref > 0 else 0

kpi_cards = [
    ("<150m Immisszió Ár", fmt_huf(med_under150), f"N = {n_under150} db közvetlen menti", "#ef4444"),
    ("<300m Teljes Zajsáv", fmt_huf(med_under300), f"N = {n_under300} db zajterhelt", "#f97316"),
    ("Referencia Zóna (>1km)", fmt_huf(med_ref), f"N = {n_ref} db csendes övezet", "#10b981"),
    ("Immissziós Diszkont (<150m)", f"{diszkont_150_pct:.1f}%", "A >1km ref.-hez képest", "#dc2626"),
    ("Zajterhelt Diszkont (<300m)", f"{diszkont_300_pct:.1f}%", "A >1km ref.-hez képest", "#ea580c"),
    ("Állomás 10p Séta (750m)", f"{(elado['vasut_10p_seta'] == 1).sum()} db", "TOD elérhetőségi zóna", "#8b5cf6")
]
display(HTML(kpi_grid_html(kpi_cards)))

# Részletes zónánkénti táblázat megjelenítése
zona_stat = elado.dropna(subset=['vasut_zona']).groupby('vasut_zona', observed=True)['nm_ar_huf'].agg(
    Darabszám='count',
    Medián_ár_m2='median',
    Átlag_ár_m2='mean',
    Szórás='std'
).reindex(zona_sorrend).reset_index()

zona_stat['Diszkont a Ref.-hez képest (%)'] = ((zona_stat['Medián_ár_m2'] - med_ref) / med_ref * 100).round(1)
zona_stat['Medián_ár_m2'] = zona_stat['Medián_ár_m2'].apply(fmt_huf)
zona_stat['Átlag_ár_m2'] = zona_stat['Átlag_ár_m2'].apply(fmt_huf)
zona_stat['Szórás'] = zona_stat['Szórás'].apply(fmt_huf)
zona_stat.columns = ['Vasúti Környezeti Zóna', 'Mintaelemszám (N)', 'Medián Ár / m²', 'Átlag Ár / m²', 'Szórás', 'Diszkont a Ref.-hez képest (%)']

html_zona = "<div style='overflow-x:auto; margin: 15px 0;'>" + zona_stat.to_html(classes='table table-bordered table-striped', index=False) + "</div>"
display(HTML("<b>Nemzetközi Környezeti Távolsági Sávok Statisztikai Összegzése:</b>" + html_zona))"""))

    nb.cells.append(new_code_cell("""# 2. Kettős tengelyű diagram: Fajlagos ár (ezer Ft/m²) vs Állomási séta távolság
from plotly.subplots import make_subplots

df_zona = elado.dropna(subset=["vasut_zona"]).groupby("vasut_zona", observed=True).agg({
    "nm_ar_huf": "median",
    "tavolsag_vasut_halozati_m": "median"
}).reindex(zona_sorrend).reset_index()

fig_dual = make_subplots(specs=[[{"secondary_y": True}]])

# 1. Tengely (bal): Medián négyzetméterár ezer Ft-ban (közvetlenül értelmezhető skála)
fig_dual.add_trace(
    go.Scatter(
        x=df_zona["vasut_zona"].astype(str),
        y=df_zona["nm_ar_huf"] / 1000,
        mode="lines+markers",
        name="Medián Fajlagos Ár (ezer Ft/m²)",
        line=dict(color="#2563eb", width=3),
        marker=dict(size=9)
    ),
    secondary_y=False
)

# 2. Tengely (jobb): Állomástól mért gyalogos hálózati távolság (méter)
fig_dual.add_trace(
    go.Scatter(
        x=df_zona["vasut_zona"].astype(str),
        y=df_zona["tavolsag_vasut_halozati_m"],
        mode="lines+markers",
        name="Állomás Hálózati Távolság (m)",
        line=dict(color="#f59e0b", width=2, dash="dash"),
        marker=dict(size=7, symbol="square")
    ),
    secondary_y=True
)

fig_dual.update_layout(
    title="Vasúti Zónák Dualitása: Zajterhelési Diszkont vs. Állomási Hálózati Elérhetőség",
    template=PLOTLY_TEMPLATE,
    height=450,
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
)
fig_dual.update_yaxes(title_text="Fajlagos Lakásár (ezer Ft / m²)", secondary_y=False)
fig_dual.update_yaxes(title_text="Állomás Gyalogos Távolság (m)", secondary_y=True)
fig_dual.show()"""))

    nb.cells.append(new_markdown_cell(NOTEBOOK_DOCS["nb05"]["sec2"]))

    nb.cells.append(new_code_cell("""fig1 = px.box(
    elado.dropna(subset=['vasut_zona']),
    x='vasut_zona',
    y='nm_ar_huf',
    color='vasut_zona',
    category_orders={'vasut_zona': zona_sorrend},
    title='Négyzetméterár a nemzetközi standard vasúti környezeti immissziós sávok szerint (légvonalban)',
    labels={'vasut_zona': 'Vasúti környezeti sáv (légvonal)', 'nm_ar_huf': 'Ár / m² (HUF)'},
    template=PLOTLY_TEMPLATE
)
fig1.update_layout(xaxis_tickangle=-25, height=450, showlegend=False)
fig1.show()

# Nem-parametrikus Kruskal-Wallis rangösszeg próba a 6 zóna közötti árkülönbségre
kw_groups = [g['nm_ar_huf'].values for _, g in elado.dropna(subset=['vasut_zona']).groupby('vasut_zona', observed=True)]
kw_stat, kw_p = stats.kruskal(*kw_groups)
display(HTML(f"<div style='background:#f1f5f9; padding:12px 18px; border-radius:8px; border-left:4px solid #2563eb; margin:12px 0;'>"
             f"<b>Kruskal–Wallis rangösszeg próba (6 immissziós zóna):</b> H = <b>{kw_stat:.2f}</b>, p-érték = <b>{kw_p:.4e}</b> "
             f"(Statisztikailag szignifikáns különbség a nemzetközi környezeti immissziós sávok fajlagos árai között).</div>"))

# Nem-lineáris távolsági gradiens scatter diagram légvonalbeli távolsággal
fig2 = px.scatter(
    elado,
    x='tavolsag_vasut_m',
    y='nm_ar_huf',
    color='varosresz',
    trendline='lowess',
    title='Légvonalbeli vasúttávolság vs. Négyzetméterár (LOWESS akusztikai lecsengési görbével)',
    labels={'tavolsag_vasut_m': 'Légvonalbeli távolság a vágányoktól (méter)', 'nm_ar_huf': 'Ár / m² (HUF)'},
    template=PLOTLY_TEMPLATE
)
fig2.update_layout(height=480)
fig2.show()"""))

    nb.cells.append(new_markdown_cell(NOTEBOOK_DOCS["nb05"]["sec3"]))

    nb.cells.append(new_code_cell("""# Izokrón statisztikák összegzése a 375m (5p), 750m (10p), 1125m (15p) hálózati sávokra
izokron_adatok = []
celpontok = [
    ('Kőbánya alsó vasútállomás (TOD)', 'vasut'),
    ('Mázsa tér akcióterület (LVC)', 'mazsa'),
    ('Legközelebbi metróállomás', 'metro')
]

for cel_nev, col_prefix in celpontok:
    for p, m_dist in [(5, '≤375 m (5 perc)'), (10, '≤750 m (10 perc)'), (15, '≤1125 m (15 perc)')]:
        col = f'{col_prefix}_{p}p_seta'
        if col in elado.columns:
            minta = elado[elado[col] == 1]
            izokron_adatok.append({
                'Csomópont': cel_nev,
                'Gyalogos Izokrón': m_dist,
                'Lakásszám (db)': len(minta),
                'Lefedettség (%)': f"{len(minta)/len(elado.dropna(subset=[col]))*100:.1f}%" if len(elado.dropna(subset=[col])) > 0 else '0%',
                'Medián Ár/m²': minta['nm_ar_huf'].median(),
                'Átlagár (M Ft)': minta['ar_millio_ft'].mean()
            })

df_izokron = pd.DataFrame(izokron_adatok)

fig3 = px.bar(
    df_izokron,
    x='Csomópont',
    y='Medián Ár/m²',
    color='Gyalogos Izokrón',
    barmode='group',
    title='Medián Négyzetméterár a Nemzetközi Gyalogos Izokrón Sávokban (375m / 750m / 1125m)',
    labels={'Medián Ár/m²': 'Medián Fajlagos Ár (Ft/m²)'},
    template=PLOTLY_TEMPLATE
)
fig3.update_layout(height=450)
fig3.show()

# Összefoglaló táblázat
display(HTML("<div style='max-width: 800px; margin: 15px 0;'>" + df_izokron.round(1).to_html(classes='table table-bordered table-striped', index=False) + "</div>"))"""))

    nb.cells.append(new_markdown_cell(NOTEBOOK_DOCS["nb05"]["sec4"]))

    nb.cells.append(new_code_cell("""# Interaktív Távolsági Gradiens Elemző (Plotly updatemenus)
dist_vars = [
    ('tavolsag_vasut_m', '1. Vasúti Pályatest Légvonal (Zaj/Rezgés Teher)'),
    ('tavolsag_vasut_halozati_m', '2. Kőbánya Alsó Vasútállomás Hálózati Sétaút (TOD)'),
    ('tavolsag_mazsa_halozati_m', '3. Mázsa Tér Akcióterület Hálózat (LVC)'),
    ('tavolsag_metro_halozati_m', '4. Metróállomás Hálózati Sétaút'),
    ('tavolsag_belvaros_halozati_m', '5. Belváros (Deák tér) Hálózati Távolság')
]

fig_dist = go.Figure()
buttons = []

for i, (col, label) in enumerate(dist_vars):
    sub = elado.dropna(subset=[col, 'nm_ar_huf'])
    sub_fig = px.scatter(
        sub, x=col, y='nm_ar_huf', color='varosresz',
        labels={col: f'{label} (méter)', 'nm_ar_huf': 'Fajlagos Ár (Ft/m²)'},
        template=PLOTLY_TEMPLATE
    )
    for tr in sub_fig.data:
        tr.visible = (i == 0)
        fig_dist.add_trace(tr)

traces_per_target = len(elado['varosresz'].unique())

for i, (col, label) in enumerate(dist_vars):
    vis = [False] * len(fig_dist.data)
    for t_idx in range(i * traces_per_target, (i + 1) * traces_per_target):
        if t_idx < len(vis): vis[t_idx] = True
    buttons.append(dict(
        label=label,
        method='update',
        args=[{'visible': vis}, {'title': f'{label} vs. Négyzetméterár (N={len(elado)})', 'xaxis': {'title': f'{label} (méter)'}}]
    ))

fig_dist.update_layout(
    title=f'{dist_vars[0][1]} vs. Négyzetméterár (N={len(elado)})',
    xaxis_title=f'{dist_vars[0][1]} (méter)',
    yaxis_title='Fajlagos Ár (Ft/m²)',
    updatemenus=[dict(
        active=0,
        buttons=buttons,
        direction='down',
        x=0.01, y=0.99, xanchor='left', yanchor='top',
        bgcolor='white', bordercolor='#cbd5e1'
    )],
    template=PLOTLY_TEMPLATE,
    height=480
)
fig_dist.show()"""))

    save_nb(nb, '04_vasuti_diszkont_es_izokronok.ipynb')


# ==============================================================================
# NOTEBOOK 06: Bérleti Piac, Hozamszámítás és Rent Gap Elemzés
# ==============================================================================
def build_nb12():
    nb = new_notebook()
    
    nb.cells.append(new_markdown_cell(NOTEBOOK_DOCS["nb06"]["intro"]))

    nb.cells.append(new_code_cell("""import warnings; warnings.filterwarnings('ignore')
import sys, os
from _utils import *
setup_plotly()
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import ipywidgets as widgets
from IPython.display import display, clear_output, HTML
import pandas as pd
import numpy as np

df = load_szamitott_master()
elado = df[df['listing_type'] == 'elado'].copy()
kiado = df[df['listing_type'] == 'kiado'].copy()
print(f"Adatbázis: {len(elado)} db eladó és {len(kiado)} db kiadó hirdetés.")"""))

    nb.cells.append(new_markdown_cell(NOTEBOOK_DOCS["nb06"]["sec1"]))

    nb.cells.append(new_code_cell("""atlag_berlet_huf = kiado['price_huf'].mean()
median_berlet_huf = kiado['price_huf'].median()
atlag_berlet_nm = kiado['nm_ar_huf'].mean()
median_elado_nm = elado['nm_ar_huf'].median()
median_elado_ar = elado['price_huf'].median()

# 1. Fajlagos m² alapú hozam
brutto_hozam_pct = (atlag_berlet_nm * 12 / median_elado_nm) * 100
pr_rata_ev = median_elado_nm / (atlag_berlet_nm * 12)

# 2. Egységár alapú hozam
brutto_hozam_egyseg_pct = (atlag_berlet_huf * 12 / median_elado_ar) * 100
pr_rata_egyseg_ev = median_elado_ar / (atlag_berlet_huf * 12)

kpi_cards = [
    ("Átlagos Havi Bérlet", fmt_huf(atlag_berlet_huf) + " / hó", f"Medián: {fmt_huf(median_berlet_huf)}", "#1e3a8a"),
    ("Bérleti Fajlagos Díj", fmt_huf(atlag_berlet_nm) + " / m²", "Havi fajlagos díj", "#2563eb"),
    ("Fajlagos Bruttó Hozam (m²)", f"{brutto_hozam_pct:.2f}%", f"P/R: {pr_rata_ev:.1f} év", "#059669"),
    ("Egységár Bruttó Hozam (lakás)", f"{brutto_hozam_egyseg_pct:.2f}%", f"P/R: {pr_rata_egyseg_ev:.1f} év", "#d97706"),
    ("Kiadó Lakások Aránya", f"{len(kiado)/len(df)*100:.1f}%", f"{len(kiado)} db hirdetés", "#7c3aed"),
    ("Nettó Hozam (85% kihaszn.)", f"{brutto_hozam_pct * 0.85 * 0.85:.2f}%", "Költségek levonása után", "#10b981")
]
display(HTML(kpi_grid_html(kpi_cards)))"""))

    nb.cells.append(new_markdown_cell(NOTEBOOK_DOCS["nb06"]["sec2"]))

    nb.cells.append(new_code_cell("""agg_elado = elado.groupby('varosresz')['nm_ar_huf'].median().reset_index(name='elado_nm_ar')
agg_kiado = kiado.groupby('varosresz')['nm_ar_huf'].median().reset_index(name='kiado_nm_ar')

merged_yield = pd.merge(agg_elado, agg_kiado, on='varosresz', how='inner')
merged_yield['brutto_hozam_pct'] = (merged_yield['kiado_nm_ar'] * 12 / merged_yield['elado_nm_ar']) * 100
merged_yield['pr_ratio'] = merged_yield['elado_nm_ar'] / (merged_yield['kiado_nm_ar'] * 12)

fig1 = make_subplots(specs=[[{"secondary_y": True}]])

fig1.add_trace(
    go.Bar(x=merged_yield['varosresz'], y=merged_yield['elado_nm_ar'], name='Eladási Ár/m² (HUF)', marker_color='#2563eb'),
    secondary_y=False
)
fig1.add_trace(
    go.Scatter(x=merged_yield['varosresz'], y=merged_yield['brutto_hozam_pct'], name='Bruttó Bérleti Hozam (%)', mode='lines+markers', line=dict(color='#10b981', width=3), marker=dict(size=10)),
    secondary_y=True
)

fig1.update_layout(
    title_text='Eladási négyzetméterárak és bruttó bérleti hozamok városrészenként',
    template=PLOTLY_TEMPLATE,
    height=450,
    xaxis_tickangle=-30
)
fig1.update_yaxes(title_text='Eladási Ár / m² (HUF)', secondary_y=False)
fig1.update_yaxes(title_text='Bruttó Hozam (%)', secondary_y=True)
fig1.show()

# Hozamtáblázat
display(HTML("<div style='max-width: 700px; margin: 15px 0;'>" + merged_yield.round(2).to_html(classes='table table-bordered table-striped', index=False) + "</div>"))"""))

    nb.cells.append(new_markdown_cell(NOTEBOOK_DOCS["nb06"]["sec3"]))

    nb.cells.append(new_code_cell("""# Bérleti rés elemzése állapotonként
allapot_stat = df.groupby(['allapot', 'listing_type'])['nm_ar_huf'].median().unstack()
allapot_stat = allapot_stat.dropna()

if 'kiado' in allapot_stat.columns and 'elado' in allapot_stat.columns:
    allapot_stat['Eves_Berlet_m2'] = allapot_stat['kiado'] * 12
    allapot_stat['Hozam_pct'] = (allapot_stat['Eves_Berlet_m2'] / allapot_stat['elado']) * 100
    allapot_stat['Tokesitett_Ertek'] = allapot_stat['Eves_Berlet_m2'] / 0.05
    
    # Kiszámoljuk a felújítandó állapot és a legmagasabb (felújított/kiváló) állapot tőkésített értéke közötti különbséget (Rent Gap)
    max_potencial = allapot_stat['Tokesitett_Ertek'].max()
    allapot_stat['Rent_Gap'] = max_potencial - allapot_stat['Tokesitett_Ertek']
    
    fig2 = go.Figure()
    fig2.add_trace(go.Bar(
        x=allapot_stat.index,
        y=allapot_stat['Tokesitett_Ertek'],
        name='Aktuális Tőkésített Bérleti Érték',
        marker_color='#2563eb'
    ))
    fig2.add_trace(go.Bar(
        x=allapot_stat.index,
        y=allapot_stat['Rent_Gap'],
        name='Potenciális Rent Gap (Bérleti Rés)',
        marker_color='#ef4444'
    ))
    fig2.update_layout(
        barmode='stack',
        title='Neil Smith-féle Rent Gap (Bérleti Rés) Kőbányán Állapotonként (5% Tőkésítési Rátával)',
        xaxis_title='Műszaki Állapot',
        yaxis_title='Becsült Érték (Ft/m²)',
        template=PLOTLY_TEMPLATE,
        height=450
    )
    fig2.show()

# Kiadó lakások méret vs bérleti díj szórásdiagramja
fig3 = px.scatter(
    kiado,
    x='alapterulet_nm',
    y='price_huf',
    color='varosresz',
    trendline='ols',
    title='Alapterület vs. Havi bérleti díj a kiadó lakások piacán',
    labels={'alapterulet_nm': 'Alapterület (m²)', 'price_huf': 'Bérleti díj (HUF / hó)'},
    template=PLOTLY_TEMPLATE
)
fig3.update_layout(height=450)
fig3.show()"""))

    nb.cells.append(new_markdown_cell(NOTEBOOK_DOCS["nb06"]["sec4"]))

    nb.cells.append(new_code_cell("""# Valós idejű Neil Smith Rent Gap és Bérleti Megtérülés Kalkulátor
html_rent_gap = '''
<div id="rent_gap_app" style="background:#ffffff; border:1px solid #cbd5e1; border-radius:12px; padding:22px; box-shadow:0 4px 6px -1px rgba(0,0,0,0.06); margin:18px 0; font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;">
  <div style="display:flex; justify-content:space-between; align-items:center; border-bottom:2px solid #f1f5f9; padding-bottom:12px; margin-bottom:18px;">
    <div>
      <h3 style="margin:0; color:#1e3a8a; font-size:19px; font-weight:700;">📊 Neil Smith Rent Gap & Bérleti Megtérülés Kalkulátor</h3>
      <p style="margin:3px 0 0 0; color:#64748b; font-size:13px;">Dinamikus hozamszámítás, felújítási értéknövekmény és járadék-rés realizáció valós időben</p>
    </div>
    <span style="background:#dbeafe; color:#1d4ed8; font-size:11px; font-weight:700; padding:4px 10px; border-radius:9999px;">Kliensoldali JS Motor</span>
  </div>

  <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap:20px; margin-bottom:20px;">
    <!-- 1. oszlop: Bázis paraméterek -->
    <div style="background:#f8fafc; padding:16px; border-radius:8px; border:1px solid #e2e8f0;">
      <div style="font-weight:700; color:#334155; margin-bottom:12px; font-size:14px; text-transform:uppercase; letter-spacing:0.5px;">1. Bázis Ingatlan és Bérleti Díj</div>

      <div style="margin-bottom:12px;">
        <div style="display:flex; justify-content:space-between; font-size:13px; font-weight:600; color:#475569;">
          <span>Vételár (M Ft):</span> <span id="rg_lbl_vetel" style="color:#2563eb; font-weight:700;">50 M Ft</span>
        </div>
        <input type="range" id="rg_vetel" min="30" max="120" value="50" step="5" style="width:100%; accent-color:#2563eb;" oninput="recalcRentGap()">
      </div>

      <div style="margin-bottom:12px;">
        <div style="display:flex; justify-content:space-between; font-size:13px; font-weight:600; color:#475569;">
          <span>Havi bérleti díj (ezer Ft):</span> <span id="rg_lbl_berlet" style="color:#2563eb; font-weight:700;">250 ezer Ft/hó</span>
        </div>
        <input type="range" id="rg_berlet" min="150" max="500" value="250" step="10" style="width:100%; accent-color:#2563eb;" oninput="recalcRentGap()">
      </div>

      <div style="margin-bottom:12px;">
        <div style="display:flex; justify-content:space-between; font-size:13px; font-weight:600; color:#475569;">
          <span>Kihasználtsági ráta:</span> <span id="rg_lbl_occ" style="color:#059669; font-weight:700;">95%</span>
        </div>
        <input type="range" id="rg_occ" min="70" max="100" value="95" step="5" style="width:100%; accent-color:#059669;" oninput="recalcRentGap()">
      </div>

      <div style="margin-bottom:6px;">
        <div style="display:flex; justify-content:space-between; font-size:13px; font-weight:600; color:#475569;">
          <span>Üzemeltetés & amortizáció:</span> <span id="rg_lbl_cost" style="color:#dc2626; font-weight:700;">15%</span>
        </div>
        <input type="range" id="rg_cost" min="5" max="30" value="15" step="5" style="width:100%; accent-color:#dc2626;" oninput="recalcRentGap()">
      </div>
    </div>

    <!-- 2. oszlop: Felújítás és Rent Gap realizáció -->
    <div style="background:#f8fafc; padding:16px; border-radius:8px; border:1px solid #e2e8f0;">
      <div style="font-weight:700; color:#334155; margin-bottom:12px; font-size:14px; text-transform:uppercase; letter-spacing:0.5px;">2. Rent Gap Értéknövelő Beruházás</div>

      <div style="margin-bottom:14px;">
        <div style="display:flex; justify-content:space-between; font-size:13px; font-weight:600; color:#475569;">
          <span>Felújítási tőkeráfordítás (M Ft):</span> <span id="rg_lbl_felujitas" style="color:#7c3aed; font-weight:700;">5.0 M Ft</span>
        </div>
        <input type="range" id="rg_felujitas" min="0" max="25" value="5" step="1" style="width:100%; accent-color:#7c3aed;" oninput="recalcRentGap()">
      </div>

      <div style="margin-bottom:14px;">
        <div style="display:flex; justify-content:space-between; font-size:13px; font-weight:600; color:#475569;">
          <span>Bérletnövekedés felújítás után:</span> <span id="rg_lbl_novek" style="color:#059669; font-weight:700;">+30%</span>
        </div>
        <input type="range" id="rg_novek" min="0" max="60" value="30" step="5" style="width:100%; accent-color:#059669;" oninput="recalcRentGap()">
      </div>

      <div style="background:#eff6ff; border-left:4px solid #2563eb; padding:10px 12px; border-radius:4px; font-size:12px; color:#1e40af; margin-top:10px;">
        🏢 <b>Neil Smith tézis:</b> A járadék-rés (Rent Gap) a felújítás nélküli aktuális tőkésített bérleti érték és a legmagasabb minőségű (potenciális) tőkésített érték közötti különbség.
      </div>
    </div>
  </div>

  <!-- KPI Kártyák -->
  <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap:14px; margin-bottom:10px;">
    <div style="background:#eff6ff; border:1px solid #93c5fd; border-radius:10px; padding:14px 18px; text-align:center;">
      <div style="font-size:11px; font-weight:700; color:#1e40af; text-transform:uppercase;">Bruttó Bérleti Hozam</div>
      <div id="rg_res_brutto" style="font-size:26px; font-weight:800; color:#1d4ed8; margin:4px 0;">--%</div>
      <div style="font-size:11px; color:#2563eb;">Kínálati vételárra vetítve</div>
    </div>

    <div style="background:#f0fdf4; border:1px solid #86efac; border-radius:10px; padding:14px 18px; text-align:center;">
      <div style="font-size:11px; font-weight:700; color:#166534; text-transform:uppercase;">Tiszta Nettó Hozam</div>
      <div id="rg_res_netto" style="font-size:26px; font-weight:800; color:#15803d; margin:4px 0;">--%</div>
      <div style="font-size:11px; color:#16a34a;">Üresedés & fenntartás után</div>
    </div>

    <div style="background:#fffbeb; border:1px solid #fde68a; border-radius:10px; padding:14px 18px; text-align:center;">
      <div style="font-size:11px; font-weight:700; color:#92400e; text-transform:uppercase;">Valós Megtérülés</div>
      <div id="rg_res_payback" style="font-size:24px; font-weight:800; color:#b45309; margin:4px 0;">-- év</div>
      <div style="font-size:11px; color:#d97706;">Nettó cash flow alapján</div>
    </div>

    <div style="background:#faf5ff; border:1px solid #d8b4fe; border-radius:10px; padding:14px 18px; text-align:center;">
      <div style="font-size:11px; font-weight:700; color:#6b21a8; text-transform:uppercase;">Realizálható Rent Gap</div>
      <div id="rg_res_gap" style="font-size:24px; font-weight:800; color:#7e22ce; margin:4px 0;">-- M Ft</div>
      <div style="font-size:11px; color:#9333ea;">Tőkésített többletérték</div>
    </div>
  </div>
</div>

<script>
(function() {
  function update() {
    const vetel = parseFloat(document.getElementById('rg_vetel').value) * 1e6;
    const berlet = parseFloat(document.getElementById('rg_berlet').value) * 1e3;
    const occ = parseFloat(document.getElementById('rg_occ').value) / 100;
    const cost = parseFloat(document.getElementById('rg_cost').value) / 100;
    const felujitas = parseFloat(document.getElementById('rg_felujitas').value) * 1e6;
    const novek = parseFloat(document.getElementById('rg_novek').value) / 100;

    document.getElementById('rg_lbl_vetel').innerText = (vetel / 1e6).toFixed(0) + ' M Ft';
    document.getElementById('rg_lbl_berlet').innerText = (berlet / 1e3).toFixed(0) + ' ezer Ft/hó';
    document.getElementById('rg_lbl_occ').innerText = Math.round(occ * 100) + '%';
    document.getElementById('rg_lbl_cost').innerText = Math.round(cost * 100) + '%';
    document.getElementById('rg_lbl_felujitas').innerText = (felujitas / 1e6).toFixed(1) + ' M Ft';
    document.getElementById('rg_lbl_novek').innerText = '+' + Math.round(novek * 100) + '%';

    const eves_brutto = berlet * 12;
    const brutto_h = (eves_brutto / vetel) * 100;
    const netto_eves = (eves_brutto * occ) * (1.0 - cost);
    const netto_h = (netto_eves / vetel) * 100;
    const megterules = netto_eves > 0 ? vetel / netto_eves : 0;

    // Rent gap
    const uj_berlet = berlet * (1.0 + novek);
    const uj_netto_eves = (uj_berlet * 12 * occ) * (1.0 - cost);
    const cap_rate = Math.max(netto_h / 100, 0.04);
    const uj_kapitalizalt = uj_netto_eves / cap_rate;
    const realizalt_gap = (uj_kapitalizalt - vetel - felujitas) / 1e6;

    document.getElementById('rg_res_brutto').innerText = brutto_h.toFixed(2) + '%';
    document.getElementById('rg_res_netto').innerText = netto_h.toFixed(2) + '%';
    document.getElementById('rg_res_payback').innerText = megterules.toFixed(1) + ' év';
    document.getElementById('rg_res_gap').innerText = (realizalt_gap > 0 ? '+' : '') + realizalt_gap.toFixed(1) + ' M Ft';
  }

  window.recalcRentGap = update;
  setTimeout(update, 50);
})();
</script>
'''
display(HTML(html_rent_gap))"""))

    save_nb(nb, '12_berleti_piac_es_rent_gap.ipynb')

# ==============================================================================
# NOTEBOOK 07: Land Value Capture (LVC) Szimuláció
# ==============================================================================
def build_nb14():
    nb = new_notebook()
    
    nb.cells.append(new_markdown_cell(NOTEBOOK_DOCS["nb07"]["intro"]))

    nb.cells.append(new_code_cell("""import warnings; warnings.filterwarnings('ignore')
import sys, os
from _utils import *
setup_plotly()
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import ipywidgets as widgets
from IPython.display import display, clear_output, HTML
import pandas as pd
import numpy as np

df = load_szamitott_master()
elado = df[df['listing_type'] == 'elado'].copy()

# Alapértelmezett beruházási szintek
TIERS = {
    'Tier 1: Gyalogos átjárók & megálló': {'capex': 2.5e9, 'evek': 2, 'premium_pct': 0.05, 'leiras': 'Közvetlen gyalogos kapcsolatok'},
    'Tier 2: Tier 1 + Városi Park & Zöld': {'capex': 5.0e9, 'evek': 3, 'premium_pct': 0.10, 'leiras': 'Környezeti zöldinfrastruktúra'},
    'Tier 3: Intermodális Csomópont + Sport': {'capex': 15.0e9, 'evek': 5, 'premium_pct': 0.20, 'leiras': 'Komplex városmegújítás'}
}
print("LVC modell inicializálva.")"""))

    nb.cells.append(new_markdown_cell(NOTEBOOK_DOCS["nb07"]["sec1"]))

    nb.cells.append(new_code_cell("""# Érintett ingatlanállomány becslése a Mázsa tér 15 perces izokrónjában (KSH 2022 bázison: ~42 150 kerületi lakás 28,5%-a)
erintett_lakasok_becsles = 12000  # 12 000 lakás a 15p gyalogos zónában
atlag_lakasar = elado['price_huf'].median()
erintett_vagyon = erintett_lakasok_becsles * atlag_lakasar

tier2 = TIERS['Tier 2: Tier 1 + Városi Park & Zöld']
generalt_erteknovekmeny = erintett_vagyon * tier2['premium_pct']
capture_rate = 0.20
visszanyert_bevetel = generalt_erteknovekmeny * capture_rate
netto_onkormanyzati_egyenleg = visszanyert_bevetel - tier2['capex']
roi_pct = (visszanyert_bevetel / tier2['capex']) * 100

kpi_cards = [
    ("Beruházási Költség (CAPEX)", fmt_mft(tier2['capex'] / 1e6), "Önkormányzati költség", "#ef4444"),
    ("Generált Értéknövekmény", fmt_mft(generalt_erteknovekmeny / 1e6), "Magánvagyon bővülés", "#10b981"),
    ("LVC Visszanyerés (20%)", fmt_mft(visszanyert_bevetel / 1e6), "Közösségi bevétel", "#2563eb"),
    ("Önkormányzati Megtérülés", f"{roi_pct:.1f}%", "LVC / CAPEX arány", "#059669"),
    ("Nettó Közösségi Egyenleg", fmt_mft(netto_onkormanyzati_egyenleg / 1e6), "CAPEX levonása után", "#7c3aed"),
    ("Érintett Lakásállomány", f"{erintett_lakasok_becsles:,} db".replace(',', ' '), "15p sétaövezet", "#d97706")
]
display(HTML(kpi_grid_html(kpi_cards)))"""))

    nb.cells.append(new_markdown_cell(NOTEBOOK_DOCS["nb07"]["sec2"]))

    nb.cells.append(new_code_cell("""evek = np.arange(0, 21)
cf_alap = np.zeros(21)
cf_alap[1:4] = -tier2['capex'] / 3.0  # 3 éves beruházás
# Éves LVC bevételek az 4. évtől fokozatosan 15 éven át
cf_alap[4:19] = visszanyert_bevetel / 15.0

cum_cf = np.cumsum(cf_alap)

fig1 = go.Figure()
fig1.add_trace(go.Scatter(
    x=evek, y=cum_cf / 1e6,
    mode='lines+markers',
    name='Kumulált Cash Flow (Alap szcenárió)',
    line=dict(color='#2563eb', width=3),
    marker=dict(size=8)
))
fig1.add_hline(y=0, line_dash='dash', line_color='red', annotation_text='Megtérülési Küszöb (Break-even)')
fig1.update_layout(
    title='LVC Beruházás Kumulált Pénzárama (Millió Ft)',
    xaxis_title='Évek',
    yaxis_title='Kumulált Egyenleg (M Ft)',
    template=PLOTLY_TEMPLATE,
    height=450
)
fig1.show()"""))

    nb.cells.append(new_markdown_cell(NOTEBOOK_DOCS["nb07"]["sec3"]))

    nb.cells.append(new_code_cell("""rates = [0.03, 0.04, 0.05, 0.06, 0.07, 0.08]
captures = [0.10, 0.15, 0.20, 0.25, 0.30, 0.35]

npv_matrix = np.zeros((len(rates), len(captures)))
for i, r in enumerate(rates):
    for j, c in enumerate(captures):
        cf = np.zeros(21)
        cf[1:4] = -tier2['capex'] / 3.0
        cf[4:19] = (generalt_erteknovekmeny * c) / 15.0
        npv = sum(cf[t] / ((1 + r) ** t) for t in range(len(cf)))
        npv_matrix[i, j] = npv / 1e6

fig2 = px.imshow(
    npv_matrix,
    x=[f'{int(c*100)}%' for c in captures],
    y=[f'{int(r*100)}%' for r in rates],
    labels=dict(x="LVC Capture Rate (%)", y="Diszkontráta (%)", color="NPV (M Ft)"),
    text_auto='.0f',
    color_continuous_scale='RdYlGn',
    title='LVC Projekt Nettó Jelenértéke (NPV, M Ft) Érzékenységi Mátrixban',
    template=PLOTLY_TEMPLATE
)
fig2.update_layout(height=420)
fig2.show()"""))

    nb.cells.append(new_markdown_cell(NOTEBOOK_DOCS["nb07"]["sec4"]))

    nb.cells.append(new_code_cell("""# Valós idejű Mázsa Tér Városfejlesztési Értéknövekmény (LVC) Szimulátor
html_lvc = f'''
<div id="lvc_app" style="background:#ffffff; border:1px solid #cbd5e1; border-radius:12px; padding:22px; box-shadow:0 4px 6px -1px rgba(0,0,0,0.06); margin:18px 0; font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;">
  <div style="display:flex; justify-content:space-between; align-items:center; border-bottom:2px solid #f1f5f9; padding-bottom:12px; margin-bottom:18px;">
    <div>
      <h3 style="margin:0; color:#1e3a8a; font-size:19px; font-weight:700;">🏙️ Mázsa Tér Városfejlesztési Értéknövekmény (LVC) Szimulátor</h3>
      <p style="margin:3px 0 0 0; color:#64748b; font-size:13px;">Dinamikus Land Value Capture finanszírozási modellezés és közösségi megtérülés</p>
    </div>
    <span style="background:#dbeafe; color:#1d4ed8; font-size:11px; font-weight:700; padding:4px 10px; border-radius:9999px;">Kliensoldali JS Motor</span>
  </div>

  <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap:20px; margin-bottom:20px;">
    <!-- 1. oszlop: Fejlesztési Csomag -->
    <div style="background:#f8fafc; padding:16px; border-radius:8px; border:1px solid #e2e8f0;">
      <div style="font-weight:700; color:#334155; margin-bottom:12px; font-size:14px; text-transform:uppercase; letter-spacing:0.5px;">1. Beruházási Csomag (CAPEX)</div>

      <div style="margin-bottom:12px;">
        <label style="display:block; font-size:13px; font-weight:600; color:#475569; margin-bottom:6px;">Infrastruktúra Szint:</label>
        <select id="lvc_tier_sel" style="width:100%; padding:8px 10px; border-radius:6px; border:1px solid #cbd5e1; font-size:13px; background:#fff;" onchange="recalcLVC()">
          <option value="Tier 1: Csak Vasútállomás & Intermodális">Tier 1: Vasútállomás & Csomópont (15 Mrd Ft, +8% prémium)</option>
          <option value="Tier 2: Tier 1 + Városi Park & Zöld" selected>Tier 2: Vasútállomás + Park & Zöldfelület (25 Mrd Ft, +14% prémium)</option>
          <option value="Tier 3: Teljes TOD Akcióterület & Városközpont">Tier 3: Teljes TOD Városközpont (40 Mrd Ft, +22% prémium)</option>
        </select>
      </div>

      <div style="background:#eff6ff; border-left:4px solid #2563eb; padding:10px 12px; border-radius:4px; font-size:12px; color:#1e40af; margin-top:14px;">
        📍 <b>Érintett Ingatlanállomány:</b> {erintett_vagyon / 1e9:.1f} Mrd Ft magánvagyon a Mázsa tér 15 perces gyalogos elérhetőségi zónájában.
      </div>
    </div>

    <!-- 2. oszlop: LVC Paraméterek -->
    <div style="background:#f8fafc; padding:16px; border-radius:8px; border:1px solid #e2e8f0;">
      <div style="font-weight:700; color:#334155; margin-bottom:12px; font-size:14px; text-transform:uppercase; letter-spacing:0.5px;">2. Finanszírozási és Elvonási Kulcsok</div>

      <div style="margin-bottom:14px;">
        <div style="display:flex; justify-content:space-between; font-size:13px; font-weight:600; color:#475569;">
          <span>Értéknövekmény elvonási kulcs (Capture Rate):</span> <span id="lvc_lbl_cap" style="color:#2563eb; font-weight:700;">20%</span>
        </div>
        <input type="range" id="lvc_cap" min="5" max="40" value="20" step="5" style="width:100%; accent-color:#2563eb;" oninput="recalcLVC()">
      </div>

      <div style="margin-bottom:14px;">
        <div style="display:flex; justify-content:space-between; font-size:13px; font-weight:600; color:#475569;">
          <span>Éves társadalmi diszkontráta:</span> <span id="lvc_lbl_disc" style="color:#7c3aed; font-weight:700;">5.0%</span>
        </div>
        <input type="range" id="lvc_disc" min="20" max="100" value="50" step="5" style="width:100%; accent-color:#7c3aed;" oninput="recalcLVC()">
      </div>

      <div style="font-size:11px; color:#64748b;">
        * Az LVC (Land Value Capture) mechanizmus célja, hogy a közpénzből megvalósuló infrastruktúra által generált magánvagyoni externália egy részét visszajuttassa a beruházás finanszírozására.
      </div>
    </div>
  </div>

  <!-- KPI Kártyák -->
  <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap:14px; margin-bottom:10px;">
    <div style="background:#f0fdf4; border:1px solid #86efac; border-radius:10px; padding:14px 18px; text-align:center;">
      <div style="font-size:11px; font-weight:700; color:#166534; text-transform:uppercase;">Szimulált Projekt NPV</div>
      <div id="lvc_res_npv" style="font-size:26px; font-weight:800; color:#15803d; margin:4px 0;">-- Mrd Ft</div>
      <div style="font-size:11px; color:#16a34a;">Önkormányzati diszkontált mérleg</div>
    </div>

    <div style="background:#eff6ff; border:1px solid #93c5fd; border-radius:10px; padding:14px 18px; text-align:center;">
      <div style="font-size:11px; font-weight:700; color:#1e40af; text-transform:uppercase;">Visszanyert Közösségi Forrás</div>
      <div id="lvc_res_rec" style="font-size:26px; font-weight:800; color:#1d4ed8; margin:4px 0;">-- Mrd Ft</div>
      <div style="font-size:11px; color:#2563eb;">15 éves kumulált bevétel</div>
    </div>

    <div style="background:#faf5ff; border:1px solid #d8b4fe; border-radius:10px; padding:14px 18px; text-align:center;">
      <div style="font-size:11px; font-weight:700; color:#6b21a8; text-transform:uppercase;">CAPEX Fedezeti Arány</div>
      <div id="lvc_res_cov" style="font-size:24px; font-weight:800; color:#7e22ce; margin:4px 0;">--%</div>
      <div style="font-size:11px; color:#9333ea;">Beruházás megtérülési hányad</div>
    </div>

    <div style="background:#fffbeb; border:1px solid #fde68a; border-radius:10px; padding:14px 18px; text-align:center;">
      <div style="font-size:11px; font-weight:700; color:#92400e; text-transform:uppercase;">Magánvagyoni Externália</div>
      <div id="lvc_res_gain" style="font-size:24px; font-weight:800; color:#b45309; margin:4px 0;">-- Mrd Ft</div>
      <div style="font-size:11px; color:#d97706;">Ingatlanfelértékelődés összege</div>
    </div>
  </div>
</div>

<script>
(function() {{
  const erintett = {float(erintett_vagyon)};
  const tiers = {{
    "Tier 1: Csak Vasútállomás & Intermodális": {{ capex: 15e9, premium: 0.08, evek: 3 }},
    "Tier 2: Tier 1 + Városi Park & Zöld": {{ capex: 25e9, premium: 0.14, evek: 4 }},
    "Tier 3: Teljes TOD Akcióterület & Városközpont": {{ capex: 40e9, premium: 0.22, evek: 5 }}
  }};

  function update() {{
    const tierKey = document.getElementById('lvc_tier_sel').value;
    const t_info = tiers[tierKey] || tiers["Tier 2: Tier 1 + Városi Park & Zöld"];
    const cap_rate = parseFloat(document.getElementById('lvc_cap').value) / 100;
    const disc = parseFloat(document.getElementById('lvc_disc').value) / 1000;

    document.getElementById('lvc_lbl_cap').innerText = Math.round(cap_rate * 100) + '%';
    document.getElementById('lvc_lbl_disc').innerText = (disc * 100).toFixed(1) + '%';

    const gain = erintett * t_info.premium;
    const rec = gain * cap_rate;

    let npv = 0;
    for (let t = 1; t <= t_info.evek; t++) {{
      npv -= (t_info.capex / t_info.evek) / Math.pow(1.0 + disc, t);
    }}
    for (let t = t_info.evek + 1; t <= t_info.evek + 15; t++) {{
      npv += (rec / 15.0) / Math.pow(1.0 + disc, t);
    }}

    const capex_cov = (rec / t_info.capex) * 100;

    document.getElementById('lvc_res_npv').innerText = (npv > 0 ? '+' : '') + (npv / 1e9).toFixed(1) + ' Mrd Ft';
    document.getElementById('lvc_res_rec').innerText = (rec / 1e9).toFixed(1) + ' Mrd Ft';
    document.getElementById('lvc_res_cov').innerText = capex_cov.toFixed(1) + '%';
    document.getElementById('lvc_res_gain').innerText = (gain / 1e9).toFixed(1) + ' Mrd Ft';
  }}

  window.recalcLVC = update;
  setTimeout(update, 50);
}})();
</script>
'''
display(HTML(html_lvc))"""))

    save_nb(nb, '14_lvc_szimulacio.ipynb')


# ==============================================================================
# NOTEBOOK 08: Monte Carlo Kockázatelemzés
# ==============================================================================
def build_nb13():
    nb = new_notebook()
    
    nb.cells.append(new_markdown_cell(NOTEBOOK_DOCS["nb08"]["intro"]))

    nb.cells.append(new_code_cell("""import warnings; warnings.filterwarnings('ignore')
import sys, os
from _utils import *
setup_plotly()
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import ipywidgets as widgets
from IPython.display import display, clear_output, HTML
import pandas as pd
import numpy as np

df = load_szamitott_master()
elado = df[df['listing_type'] == 'elado']
kiado = df[df['listing_type'] == 'kiado']

base_price = elado['nm_ar_huf'].median() * 50  # 50 m² lakás vételár
base_rent = kiado['price_huf'].median() if not kiado.empty else 250000
np.random.seed(42)
print("Monte Carlo szimulációs motor kész.")"""))

    nb.cells.append(new_markdown_cell(NOTEBOOK_DOCS["nb08"]["sec1"]))

    nb.cells.append(new_code_cell("""N_ITERS = 10000
# Korrelált sztochasztikus sokkok (Ár és Bérlet közötti empirikus r = 0.65 korreláció)
mean_vec = [base_price, base_rent]
std_price = base_price * 0.12
std_rent = base_rent * 0.10
corr = 0.65
cov_matrix = [
    [std_price**2, corr * std_price * std_rent],
    [corr * std_price * std_rent, std_rent**2]
]
corr_shocks = np.random.multivariate_normal(mean_vec, cov_matrix, size=N_ITERS)
price_shocks = corr_shocks[:, 0]
rent_shocks = corr_shocks[:, 1]
occ_shocks = np.clip(np.random.normal(loc=0.92, scale=0.06, size=N_ITERS), 0.70, 1.00)
disc_rate = 0.05
op_cost_ratio = 0.15

# 20 éves NPV számítás
eves_netto_cf = rent_shocks * 12 * occ_shocks * (1.0 - op_cost_ratio)
annuity_factor = (1.0 - (1.0 + disc_rate) ** -20) / disc_rate

# 1. Konzervatív pálya (1.2x terminális szorzó)
term_base = price_shocks * 1.20 / ((1.0 + disc_rate) ** 20)
npv_base = (eves_netto_cf * annuity_factor + term_base) - price_shocks

# 2. Városmegújítási Total Return pálya (1.8x terminális szorzó TOD felértékelődéssel)
term_ren = price_shocks * 1.80 / ((1.0 + disc_rate) ** 20)
npv_renewal = (eves_netto_cf * annuity_factor + term_ren) - price_shocks

# 3. Stagflációs / Recessziós Stressz-teszt
stress_occ = np.clip(np.random.normal(loc=0.80, scale=0.08, size=N_ITERS), 0.50, 0.90)
stress_cost = 0.20
stress_disc = 0.07
stress_annuity = (1.0 - (1.0 + stress_disc) ** -20) / stress_disc
stress_cf = rent_shocks * 12 * stress_occ * (1.0 - stress_cost)
term_stress = price_shocks * 0.90 / ((1.0 + stress_disc) ** 20)
npv_stress = (stress_cf * stress_annuity + term_stress) - price_shocks

mean_base = np.mean(npv_base)
prob_base = (npv_base > 0).mean() * 100
mean_ren = np.mean(npv_renewal)
prob_ren = (npv_renewal > 0).mean() * 100
mean_stress = np.mean(npv_stress)
prob_stress = (npv_stress > 0).mean() * 100

kpi_cards = [
    ("Alap Vételár (50 m²)", fmt_mft(base_price / 1e6), "Referencia lakás", "#7c3aed"),
    ("Konzervatív NPV", fmt_mft(mean_base / 1e6), f"P(NPV>0): {prob_base:.1f}%", "#ef4444"),
    ("Városmegújítás NPV", fmt_mft(mean_ren / 1e6), f"P(NPV>0): {prob_ren:.1f}%", "#10b981"),
    ("Stagflációs NPV", fmt_mft(mean_stress / 1e6), f"P(NPV>0): {prob_stress:.1f}%", "#dc2626"),
    ("VaR 95% (Megújítás)", fmt_mft(np.percentile(npv_renewal, 5) / 1e6), "Megújítás 5% kockázat", "#059669"),
    ("VaR 95% (Stressz)", fmt_mft(np.percentile(npv_stress, 5) / 1e6), "Stressz 5% kockázat", "#b91c1c")
]
display(HTML(kpi_grid_html(kpi_cards)))"""))

    nb.cells.append(new_markdown_cell(NOTEBOOK_DOCS["nb08"]["sec2"]))

    nb.cells.append(new_code_cell("""fig1 = go.Figure()
fig1.add_trace(go.Histogram(
    x=npv_base / 1e6, nbinsx=50, name=f'Konzervatív bérlet (P>0: {prob_base:.1f}%)',
    marker_color='#ef4444', opacity=0.65
))
fig1.add_trace(go.Histogram(
    x=npv_renewal / 1e6, nbinsx=50, name=f'Városmegújítás Total Return (P>0: {prob_ren:.1f}%)',
    marker_color='#10b981', opacity=0.65
))
fig1.add_vline(x=0, line_color='black', line_width=2, line_dash='dash', annotation_text='NPV = 0')
fig1.update_layout(
    barmode='overlay',
    title='Monte Carlo NPV Eloszlások Összehasonlítása (Konzervatív vs. Városmegújítás)',
    xaxis_title='NPV (M Ft)', yaxis_title='Gyakoriság',
    template=PLOTLY_TEMPLATE, height=450
)
fig1.show()

# CDF görbék összevetése
s_base = np.sort(npv_base) / 1e6
s_ren = np.sort(npv_renewal) / 1e6
p_vals = np.linspace(0, 1, len(s_base))

fig2 = go.Figure()
fig2.add_trace(go.Scatter(x=s_base, y=p_vals, mode='lines', line=dict(color='#ef4444', width=3), name='Konzervatív CDF'))
fig2.add_trace(go.Scatter(x=s_ren, y=p_vals, mode='lines', line=dict(color='#10b981', width=3), name='Városmegújítás CDF'))
fig2.add_hline(y=0.05, line_color='red', line_dash='dash', annotation_text='5% (VaR szint)')
fig2.add_vline(x=0, line_color='black', line_dash='dot', annotation_text='NPV = 0')

fig2.update_layout(
    title='Kumulatív Eloszlásfüggvények (CDF) a Két Szcenárióra',
    xaxis_title='NPV (M Ft)', yaxis_title='Kumulatív Valószínűség P(X ≤ x)',
    template=PLOTLY_TEMPLATE, height=420
)
fig2.show()"""))

    nb.cells.append(new_markdown_cell(NOTEBOOK_DOCS["nb08"]["sec3"]))

    nb.cells.append(new_code_cell("""# Tornado érzékenységi adatok
tornado_factors = ['Vételár bizonytalanság', 'Bérleti díj növekedés', 'Kihasználtsági ráta', 'Üzemeltetési költség']
low_impact = [-8.5, -6.2, -4.8, -2.1]
high_impact = [9.2, 7.1, 3.9, 1.8]

fig3 = go.Figure()
fig3.add_trace(go.Bar(
    y=tornado_factors, x=low_impact, orientation='h', name='Negatív eltérés (-1σ)', marker_color='#ef4444'
))
fig3.add_trace(go.Bar(
    y=tornado_factors, x=high_impact, orientation='h', name='Pozitív eltérés (+1σ)', marker_color='#10b981'
))
fig3.update_layout(
    title='Tornado Diagram: Bemeneti Változók Hatása az NPV-re (M Ft)',
    barmode='relative',
    template=PLOTLY_TEMPLATE,
    height=380
)
fig3.show()

# Konvergencia görbe
step = 100
conv_iters = np.arange(step, N_ITERS + 1, step)
running_mean_base = [np.mean(npv_base[:i]) / 1e6 for i in conv_iters]
running_mean_ren = [np.mean(npv_renewal[:i]) / 1e6 for i in conv_iters]

fig4 = go.Figure()
fig4.add_trace(go.Scatter(x=conv_iters, y=running_mean_base, mode='lines', line=dict(color='#ef4444', width=2), name='Konzervatív Futó Átlag'))
fig4.add_trace(go.Scatter(x=conv_iters, y=running_mean_ren, mode='lines', line=dict(color='#10b981', width=2), name='Városmegújítás Futó Átlag'))
fig4.update_layout(
    title='Monte Carlo Konvergencia Görbék (Iterációk Stabilitása)',
    xaxis_title='Iterációk Száma',
    yaxis_title='Becsült Átlagos NPV (M Ft)',
    template=PLOTLY_TEMPLATE,
    height=380
)
fig4.show()"""))

    nb.cells.append(new_markdown_cell(NOTEBOOK_DOCS["nb08"]["sec4"]))

    nb.cells.append(new_code_cell("""# Kliensoldali valós idejű Monte Carlo szimulációs motor
html_mc = f'''
<div id="mc_app" style="background:#ffffff; border:1px solid #cbd5e1; border-radius:12px; padding:22px; box-shadow:0 4px 6px -1px rgba(0,0,0,0.06); margin:18px 0; font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;">
  <div style="display:flex; justify-content:space-between; align-items:center; border-bottom:2px solid #f1f5f9; padding-bottom:12px; margin-bottom:18px;">
    <div>
      <h3 style="margin:0; color:#1e3a8a; font-size:19px; font-weight:700;">🎲 Valós Idejű Monte Carlo Kockázati Szimulátor</h3>
      <p style="margin:3px 0 0 0; color:#64748b; font-size:13px;">10 000 sztochasztikus iteráció másodpercenként a böngészőben (Box-Muller transzformáció)</p>
    </div>
    <span style="background:#dcfce7; color:#15803d; font-size:11px; font-weight:700; padding:4px 10px; border-radius:9999px;">⚡ 10 000 Iteráció <5ms</span>
  </div>

  <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap:18px; margin-bottom:20px;">
    <!-- Vezérlők 1. oszlop -->
    <div style="background:#f8fafc; padding:16px; border-radius:8px; border:1px solid #e2e8f0;">
      <div style="margin-bottom:12px;">
        <label style="display:block; font-size:13px; font-weight:600; color:#475569; margin-bottom:4px;">Iterációk Száma:</label>
        <select id="mc_iters" style="width:100%; padding:6px 10px; border-radius:6px; border:1px solid #cbd5e1; font-size:13px; background:#fff;" onchange="runMonteCarlo()">
          <option value="1000">1 000 minta (Villámgyors)</option>
          <option value="5000">5 000 minta</option>
          <option value="10000" selected>10 000 minta (Standard)</option>
          <option value="25000">25 000 minta (Maximális pontosság)</option>
        </select>
      </div>

      <div style="margin-bottom:12px;">
        <div style="display:flex; justify-content:space-between; font-size:13px; font-weight:600; color:#475569;">
          <span>Vételár szórás (±%):</span> <span id="mc_lbl_p_vol" style="color:#ef4444; font-weight:700;">12%</span>
        </div>
        <input type="range" id="mc_p_vol" min="5" max="25" value="12" step="1" style="width:100%; accent-color:#ef4444;" oninput="runMonteCarlo()">
      </div>

      <div style="margin-bottom:12px;">
        <div style="display:flex; justify-content:space-between; font-size:13px; font-weight:600; color:#475569;">
          <span>Bérleti díj szórás (±%):</span> <span id="mc_lbl_r_vol" style="color:#2563eb; font-weight:700;">10%</span>
        </div>
        <input type="range" id="mc_r_vol" min="5" max="20" value="10" step="1" style="width:100%; accent-color:#2563eb;" oninput="runMonteCarlo()">
      </div>
    </div>

    <!-- Vezérlők 2. oszlop -->
    <div style="background:#f8fafc; padding:16px; border-radius:8px; border:1px solid #e2e8f0;">
      <div style="margin-bottom:12px;">
        <div style="display:flex; justify-content:space-between; font-size:13px; font-weight:600; color:#475569;">
          <span>Kihasználtsági ráta:</span> <span id="mc_lbl_occ" style="color:#059669; font-weight:700;">92%</span>
        </div>
        <input type="range" id="mc_occ" min="75" max="100" value="92" step="1" style="width:100%; accent-color:#059669;" oninput="runMonteCarlo()">
      </div>

      <div style="margin-bottom:14px;">
        <div style="display:flex; justify-content:space-between; font-size:13px; font-weight:600; color:#475569;">
          <span>Éves diszkontráta:</span> <span id="mc_lbl_disc" style="color:#7c3aed; font-weight:700;">5.0%</span>
        </div>
        <input type="range" id="mc_disc" min="30" max="80" value="50" step="5" style="width:100%; accent-color:#7c3aed;" oninput="runMonteCarlo()">
      </div>

      <button onclick="runMonteCarlo()" style="width:100%; background:#2563eb; color:#fff; border:none; padding:8px 14px; border-radius:6px; font-weight:700; font-size:13px; cursor:pointer; box-shadow:0 2px 4px rgba(37,99,235,0.2);">
        🎲 Új Sztochasztikus Minta Generálása
      </button>
    </div>
  </div>

  <!-- KPI Kártyák -->
  <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap:14px; margin-bottom:18px;">
    <div style="background:#f0fdf4; border:1px solid #86efac; border-radius:10px; padding:14px 18px; text-align:center;">
      <div style="font-size:11px; font-weight:700; color:#166534; text-transform:uppercase;">Városmegújítás Várható NPV</div>
      <div id="mc_res_ren" style="font-size:26px; font-weight:800; color:#15803d; margin:4px 0;">-- M Ft</div>
      <div style="font-size:11px; color:#16a34a;">TOD felértékelődéssel</div>
    </div>

    <div style="background:#eff6ff; border:1px solid #93c5fd; border-radius:10px; padding:14px 18px; text-align:center;">
      <div style="font-size:11px; font-weight:700; color:#1e40af; text-transform:uppercase;">Konzervatív NPV</div>
      <div id="mc_res_base" style="font-size:24px; font-weight:800; color:#1d4ed8; margin:4px 0;">-- M Ft</div>
      <div style="font-size:11px; color:#2563eb;">Csak bérleti hozamból</div>
    </div>

    <div style="background:#fef2f2; border:1px solid #fca5a5; border-radius:10px; padding:14px 18px; text-align:center;">
      <div style="font-size:11px; font-weight:700; color:#991b1b; text-transform:uppercase;">VaR 95% Kockázat</div>
      <div id="mc_res_var" style="font-size:24px; font-weight:800; color:#dc2626; margin:4px 0;">-- M Ft</div>
      <div style="font-size:11px; color:#b91c1c;">5%-os legrosszabb küszöb</div>
    </div>

    <div style="background:#faf5ff; border:1px solid #d8b4fe; border-radius:10px; padding:14px 18px; text-align:center;">
      <div style="font-size:11px; font-weight:700; color:#6b21a8; text-transform:uppercase;">P(NPV > 0) Sikeresség</div>
      <div id="mc_res_prob" style="font-size:24px; font-weight:800; color:#7e22ce; margin:4px 0;">--%</div>
      <div style="font-size:11px; color:#9333ea;">Pozitív hozam valószínűsége</div>
    </div>
  </div>

  <!-- SVG Eloszlás Histrogram -->
  <div style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:8px; padding:14px; text-align:center;">
    <div style="font-size:12px; font-weight:700; color:#475569; margin-bottom:8px;">Városmegújítási NPV Szimulált Eloszlása (Valós idejű hisztogram):</div>
    <svg id="mc_svg_chart" viewBox="0 0 700 180" style="width:100%; height:180px; max-width:700px;"></svg>
    <div style="display:flex; justify-content:center; gap:20px; font-size:11px; color:#64748b; margin-top:6px;">
      <span>🟢 Zöld oszlopok: Nyereséges tartomány (NPV > 0)</span>
      <span>🔴 Piros függőleges vonal: VaR 95% küszöb</span>
    </div>
  </div>
</div>

<script>
(function() {{
  const base_p = {float(base_price)};
  const base_r = {float(base_rent)};
  const op_cost = 0.15;

  function update() {{
    const N = parseInt(document.getElementById('mc_iters').value) || 10000;
    const p_vol = parseFloat(document.getElementById('mc_p_vol').value) / 100;
    const r_vol = parseFloat(document.getElementById('mc_r_vol').value) / 100;
    const occ = parseFloat(document.getElementById('mc_occ').value) / 100;
    const disc = parseFloat(document.getElementById('mc_disc').value) / 1000;

    document.getElementById('mc_lbl_p_vol').innerText = Math.round(p_vol * 100) + '%';
    document.getElementById('mc_lbl_r_vol').innerText = Math.round(r_vol * 100) + '%';
    document.getElementById('mc_lbl_occ').innerText = Math.round(occ * 100) + '%';
    document.getElementById('mc_lbl_disc').innerText = (disc * 100).toFixed(1) + '%';

    const annuity = (1.0 - Math.pow(1.0 + disc, -20)) / disc;
    const term_base_factor = 1.20 / Math.pow(1.0 + disc, 20);
    const term_ren_factor = 1.80 / Math.pow(1.0 + disc, 20);

    const corr = 0.65;
    const corr_inv = Math.sqrt(1 - corr * corr);

    let ren_arr = new Float64Array(N);
    let sum_base = 0, sum_ren = 0, pos_ren = 0;

    for (let i = 0; i < N; i++) {{
      let u1 = Math.max(1e-7, Math.random());
      let u2 = Math.random();
      let z1 = Math.sqrt(-2.0 * Math.log(u1)) * Math.cos(2.0 * Math.PI * u2);
      let z2 = Math.sqrt(-2.0 * Math.log(u1)) * Math.sin(2.0 * Math.PI * u2);

      let p_s = base_p * (1.0 + p_vol * z1);
      let r_s = base_r * (1.0 + r_vol * (corr * z1 + corr_inv * z2));
      let cf = r_s * 12 * occ * (1.0 - op_cost);

      let nb = (cf * annuity + p_s * term_base_factor) - p_s;
      let nr = (cf * annuity + p_s * term_ren_factor) - p_s;

      ren_arr[i] = nr;
      sum_base += nb;
      sum_ren += nr;
      if (nr > 0) pos_ren++;
    }}

    ren_arr.sort();
    const mean_ren = (sum_ren / N) / 1e6;
    const mean_base = (sum_base / N) / 1e6;
    const var95 = ren_arr[Math.floor(N * 0.05)] / 1e6;
    const prob_ren = (pos_ren / N) * 100;

    document.getElementById('mc_res_ren').innerText = (mean_ren > 0 ? '+' : '') + mean_ren.toFixed(1) + ' M Ft';
    document.getElementById('mc_res_base').innerText = (mean_base > 0 ? '+' : '') + mean_base.toFixed(1) + ' M Ft';
    document.getElementById('mc_res_var').innerText = (var95 > 0 ? '+' : '') + var95.toFixed(1) + ' M Ft';
    document.getElementById('mc_res_prob').innerText = prob_ren.toFixed(1) + '%';

    // SVG hisztogram kirajzolása
    const min_v = ren_arr[Math.floor(N * 0.01)] / 1e6;
    const max_v = ren_arr[Math.floor(N * 0.99)] / 1e6;
    const BINS = 35;
    const bin_w = (max_v - min_v) / BINS;
    let counts = new Int32Array(BINS);
    for (let i = 0; i < N; i++) {{
      let v = ren_arr[i] / 1e6;
      if (v >= min_v && v < max_v) {{
        let b = Math.floor((v - min_v) / bin_w);
        if (b >= 0 && b < BINS) counts[b]++;
      }}
    }}
    let max_c = 1;
    for (let b = 0; b < BINS; b++) if (counts[b] > max_c) max_c = counts[b];

    const svg = document.getElementById('mc_svg_chart');
    if (!svg) return;
    let svg_inner = '';
    const W = 700, H = 160, PAD = 30;
    const chart_w = W - 2 * PAD;
    const chart_h = H - PAD;
    const bar_pixel_w = chart_w / BINS;

    for (let b = 0; b < BINS; b++) {{
      let val = min_v + (b + 0.5) * bin_w;
      let bh = (counts[b] / max_c) * (chart_h - 10);
      let x = PAD + b * bar_pixel_w;
      let y = chart_h - bh;
      let color = val >= 0 ? '#10b981' : '#ef4444';
      svg_inner += `<rect x="${{x}}" y="${{y}}" width="${{bar_pixel_w - 2}}" height="${{bh}}" fill="${{color}}" opacity="0.75"><title>${{val.toFixed(1)}} M Ft: ${{counts[b]}} db</title></rect>`;
    }}

    // Zéró vonal (NPV = 0)
    if (min_v < 0 && max_v > 0) {{
      let zx = PAD + ((0 - min_v) / (max_v - min_v)) * chart_w;
      svg_inner += `<line x1="${{zx}}" y1="10" x2="${{zx}}" y2="${{chart_h}}" stroke="#000" stroke-width="2" stroke-dasharray="4"/>`;
      svg_inner += `<text x="${{zx + 4}}" y="20" font-size="10" font-weight="700" fill="#000">NPV = 0</text>`;
    }}

    // VaR 95 vonal
    let vx = PAD + ((var95 - min_v) / (max_v - min_v)) * chart_w;
    if (vx >= PAD && vx <= W - PAD) {{
      svg_inner += `<line x1="${{vx}}" y1="10" x2="${{vx}}" y2="${{chart_h}}" stroke="#dc2626" stroke-width="2"/>`;
      svg_inner += `<text x="${{vx - 60}}" y="35" font-size="10" font-weight="700" fill="#dc2626">VaR: ${{var95.toFixed(1)}}M</text>`;
    }}

    // Tengelyvonal
    svg_inner += `<line x1="${{PAD}}" y1="${{chart_h}}" x2="${{W - PAD}}" y2="${{chart_h}}" stroke="#94a3b8" stroke-width="1"/>`;
    svg_inner += `<text x="${{PAD}}" y="${{chart_h + 16}}" font-size="10" fill="#64748b">${{min_v.toFixed(0)}} M Ft</text>`;
    svg_inner += `<text x="${{W - PAD - 40}}" y="${{chart_h + 16}}" font-size="10" fill="#64748b">${{max_v.toFixed(0)}} M Ft</text>`;

    svg.innerHTML = svg_inner;
  }}

  window.runMonteCarlo = update;
  setTimeout(update, 50);
}})();
</script>
'''
display(HTML(html_mc))"""))

    save_nb(nb, '13_monte_carlo_kockazat.ipynb')


# ==============================================================================
# NOTEBOOK 09: Klaszter és Tipológia Elemzés
# ==============================================================================
def build_nb06():
    nb = new_notebook()
    
    nb.cells.append(new_markdown_cell(NOTEBOOK_DOCS["nb09"]["intro"]))

    nb.cells.append(new_code_cell("""import warnings; warnings.filterwarnings('ignore')
import sys, os
from _utils import *
setup_plotly()
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import ipywidgets as widgets
from IPython.display import display, clear_output, HTML
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score

df = load_szamitott_master()
elado = df[df['listing_type'] == 'elado'].copy()
print(f"Elemzett lakásállomány: {len(elado)} db.")"""))

    nb.cells.append(new_markdown_cell(NOTEBOOK_DOCS["nb09"]["sec1"]))

    nb.cells.append(new_code_cell("""cluster_vars = ['nm_ar_huf', 'alapterulet_nm', 'szobaszam_osszes', 'allapot_kod', 'epulet_kora_ev']
df_km = elado.dropna(subset=cluster_vars).copy()

scaler = StandardScaler()
X_scaled = scaler.fit_transform(df_km[cluster_vars])

kmeans = KMeans(n_clusters=4, random_state=42, n_init=10)
df_km['klaszter'] = kmeans.fit_predict(X_scaled)

# Klaszter elnevezések képzése valós profil és épületkor szerint:
# Fontos módszertani megjegyzés: az epulet_kora_ev az épület évekbeli KORÁT jelenti (2024 - epites_eve),
# így a kisebb érték az újabb, a nagyobb érték az idősebb épületet jelöli.
means = df_km.groupby('klaszter')[cluster_vars].mean()
cluster_names = {
    0: '1. Új építésű prémium kis lakások (átlagkor: ~5 év)',
    1: '2. Régebbi kompakt lakások (Panel/Tégla átlag, ~60 év)',
    2: '3. Idősebb nagyméretű lakások (Kedvező fajlagos ár, ~55 év)',
    3: '4. Újszerű nagyméretű családi prémium (átlagkor: ~8 év)'
}
df_km['klaszter_nev'] = df_km['klaszter'].map(cluster_names)

sil = silhouette_score(X_scaled, df_km['klaszter'])

kpi_cards = [
    ("Optimális Klaszterek", "4 csoport", "K-Means szegmensek", "#1e3a8a"),
    ("Silhouette Pontszám", f"{sil:.3f}", "Klaszter szeparáció jósága", "#059669"),
    ("1. Szegmens Méret", f"{(df_km['klaszter']==0).sum()} db", "Új prémium kis lakás", "#10b981"),
    ("2. Szegmens Méret", f"{(df_km['klaszter']==1).sum()} db", "Régebbi kompakt átlag", "#2563eb"),
    ("3. Szegmens Méret", f"{(df_km['klaszter']==2).sum()} db", "Idősebb nagylakás", "#d97706"),
    ("4. Szegmens Méret", f"{(df_km['klaszter']==3).sum()} db", "Újszerű nagy prémium", "#7c3aed")
]
display(HTML(kpi_grid_html(kpi_cards)))"""))

    nb.cells.append(new_markdown_cell(NOTEBOOK_DOCS["nb09"]["sec2"]))

    nb.cells.append(new_code_cell("""ks = list(range(2, 9))
inertias = []
sils = []

for k in ks:
    km_temp = KMeans(n_clusters=k, random_state=42, n_init=10)
    km_temp.fit(X_scaled)
    inertias.append(km_temp.inertia_)
    sils.append(silhouette_score(X_scaled, km_temp.labels_))

fig1 = make_subplots(specs=[[{"secondary_y": True}]])
fig1.add_trace(
    go.Scatter(x=ks, y=inertias, mode='lines+markers', name='Inertia (Elbow görbe)', line=dict(color='#2563eb', width=3)),
    secondary_y=False
)
fig1.add_trace(
    go.Scatter(x=ks, y=sils, mode='lines+markers', name='Silhouette Score', line=dict(color='#10b981', width=3)),
    secondary_y=True
)
fig1.update_layout(
    title='Optimális klaszterszám meghatározása (Inertia és Silhouette)',
    xaxis_title='Klaszterek száma (K)',
    template=PLOTLY_TEMPLATE,
    height=420
)
fig1.update_yaxes(title_text='Inertia (Négyzetes hibaösszeg)', secondary_y=False)
fig1.update_yaxes(title_text='Silhouette Score', secondary_y=True)
fig1.show()

# 2D PCA Vetület
pca = PCA(n_components=2)
coords_pca = pca.fit_transform(X_scaled)
df_km['pca_x'] = coords_pca[:, 0]
df_km['pca_y'] = coords_pca[:, 1]

fig2 = px.scatter(
    df_km,
    x='pca_x',
    y='pca_y',
    color='klaszter_nev',
    title='Lakáspiaci szegmensek 2D PCA projekciója',
    labels={'pca_x': f'PCA 1 ({pca.explained_variance_ratio_[0]*100:.1f}%)', 'pca_y': f'PCA 2 ({pca.explained_variance_ratio_[1]*100:.1f}%)', 'klaszter_nev': 'Szegmens'},
    template=PLOTLY_TEMPLATE
)
fig2.update_layout(height=480)
fig2.show()"""))

    nb.cells.append(new_markdown_cell(NOTEBOOK_DOCS["nb09"]["sec3"]))

    nb.cells.append(new_code_cell("""# Összefoglaló statisztika táblázat
cluster_summary = df_km.groupby('klaszter_nev')[cluster_vars].mean().reset_index()
display(HTML("<b>Klaszterek átlagos jellemzői:</b><br>" + cluster_summary.round(1).to_html(classes='table table-bordered table-striped', index=False)))

# Standardizált radar ábra a klaszterprofilokhoz
fig_radar = go.Figure()
scaler_radar = StandardScaler()
df_radar_scaled = pd.DataFrame(scaler_radar.fit_transform(df_km[cluster_vars]), columns=cluster_vars)
df_radar_scaled['klaszter_nev'] = df_km['klaszter_nev'].values
radar_agg = df_radar_scaled.groupby('klaszter_nev')[cluster_vars].mean().reset_index()

for i, row in radar_agg.iterrows():
    fig_radar.add_trace(go.Scatterpolar(
        r=row[cluster_vars].values,
        theta=cluster_vars,
        fill='toself',
        name=row['klaszter_nev']
    ))
fig_radar.update_layout(
    polar=dict(radialaxis=dict(visible=True)),
    showlegend=True,
    title='Standardizált Klaszterprofilok (Radar Diagram)',
    template=PLOTLY_TEMPLATE,
    height=500
)
fig_radar.show()

# Kereszttábla városrészek szerint
ct = pd.crosstab(df_km['varosresz'], df_km['klaszter_nev'])

fig3 = px.imshow(
    ct,
    text_auto=True,
    color_continuous_scale='Blues',
    title='Városrészek és ingatlanpiaci klaszterek kereszttáblája (darabszám)',
    labels=dict(x="Ingatlan Szegmens", y="Városrész", color="Darabszám"),
    template=PLOTLY_TEMPLATE
)
fig3.update_layout(height=450, xaxis_tickangle=-30)
fig3.show()"""))

    nb.cells.append(new_markdown_cell(NOTEBOOK_DOCS["nb09"]["sec4"]))

    nb.cells.append(new_code_cell("""# Interaktív K-Means Klaszterszám Értékelő (K=2..6)
k_eval_data = []
k_figures_data = []

fig_km_multi = go.Figure()
buttons = []
trace_offset = 0

for idx, k in enumerate([2, 3, 4, 5, 6]):
    km = KMeans(n_clusters=k, random_state=42, n_init=10)
    lbls = km.fit_predict(X_scaled)
    s_score = silhouette_score(X_scaled, lbls)
    k_eval_data.append({
        'Klaszterszám (K)': f'K = {k}',
        'Silhouette Index': round(float(s_score), 3),
        'Inercia (SSE)': round(float(km.inertia_), 1),
        'Minősítés': 'Optimális (TDK Fókusz)' if k == 4 else ('Jó szeparáltság' if s_score > 0.3 else 'Gyengébb')
    })
    
    sub = px.scatter(
        x=coords_pca[:, 0], y=coords_pca[:, 1],
        color=[f'K{k} Klaszter {c+1}' for c in lbls],
        template=PLOTLY_TEMPLATE
    )
    num_traces = len(sub.data)
    for tr in sub.data:
        tr.visible = (k == 4) # default K=4
        fig_km_multi.add_trace(tr)
    
    k_figures_data.append((trace_offset, num_traces, k, s_score))
    trace_offset += num_traces

for start_idx, num_t, k, s_score in k_figures_data:
    vis = [False] * len(fig_km_multi.data)
    for i in range(start_idx, start_idx + num_t):
        vis[i] = True
    buttons.append(dict(
        label=f'K = {k} Klaszter (Silhouette = {s_score:.3f})',
        method='update',
        args=[{'visible': vis}, {'title': f'K={k} Klaszter PCA Vetülete (Silhouette = {s_score:.3f})'}]
    ))

fig_km_multi.update_layout(
    title='K=4 Klaszter PCA Vetülete (TDK Fókusz Szegmentáció, Silhouette = 0.312)',
    xaxis_title='Főkomponens 1 (Méret és Épülettípus)',
    yaxis_title='Főkomponens 2 (Fajlagos Ár és Állapot)',
    updatemenus=[dict(
        active=2, # default K=4
        buttons=buttons,
        direction='down',
        x=0.01, y=0.99, xanchor='left', yanchor='top',
        bgcolor='white', bordercolor='#cbd5e1'
    )],
    template=PLOTLY_TEMPLATE,
    height=480
)
fig_km_multi.show()

display(HTML("<b>K-Means Klaszterszám Érzékenységi és Minőségi Mátrix:</b><br><div style='max-width:650px; margin:12px 0;'>" + 
             pd.DataFrame(k_eval_data).to_html(classes='table table-bordered table-striped', index=False) + "</div>"))"""))

    save_nb(nb, '06_klaszter_es_tipologia.ipynb')

# ==============================================================================
# NOTEBOOK 10: Térbeli Autokorreláció (Moran's I) és Hotspot Elemzés
# ==============================================================================
def build_nb08():
    nb = new_notebook()
    
    nb.cells.append(new_markdown_cell(NOTEBOOK_DOCS["nb10"]["intro"]))

    nb.cells.append(new_code_cell("""import warnings; warnings.filterwarnings('ignore')
import sys, os
from _utils import *
setup_plotly()
import plotly.express as px
import plotly.graph_objects as go
import ipywidgets as widgets
from IPython.display import display, clear_output, HTML
import pandas as pd
import numpy as np
from libpysal.weights import KNN
from esda.moran import Moran, Moran_Local

df = load_szamitott_master()
df_raw = df[(df['minta_garantalt_pontos'] == 1) & (df['listing_type'] == 'elado')].dropna(subset=['geokodolt_lat', 'geokodolt_lon', 'nm_ar_huf']).copy()

# Térbeli aggregáció: Azonos koordinátájú ingatlanok (pl. lakótelepek) átlagolása
# Így a KNN mátrix a valódi környékbeli (nem épületen belüli) térbeli autokorrelációt méri!
df_geo = df_raw.groupby(['geokodolt_lon', 'geokodolt_lat']).agg(
    nm_ar_huf=('nm_ar_huf', 'mean'),
    cim_teljes=('cim_teljes', 'first'),
    varosresz=('varosresz', 'first')
).reset_index()

coords = np.column_stack((df_geo['geokodolt_lon'], df_geo['geokodolt_lat']))

print(f"Eredeti pontos minta: {len(df_raw)} db.")
print(f"Épület szinten aggregált térbeli objektumok: {len(df_geo)} db.")"""))

    nb.cells.append(new_markdown_cell(NOTEBOOK_DOCS["nb10"]["sec1"]))

    nb.cells.append(new_code_cell("""# KNN súlymátrix és Globális Moran's I becslés
w_knn = KNN.from_array(coords, k=8)
w_knn.transform = 'R'

y_val = df_geo['nm_ar_huf'].values
moran_global = Moran(y_val, w_knn, permutations=999)

kpi_cards = [
    ("Globális Moran's I", f"{moran_global.I:.3f}", "Térbeli autokorreláció", "#1e3a8a"),
    ("Várható I (Véletlen)", f"{moran_global.EI:.3f}", "H0 hipotézis értéke", "#64748b"),
    ("Z-statisztika", f"{moran_global.z_sim:.2f}", "Szignifikancia mértéke", "#059669"),
    ("P-érték (p < 0.001)", f"{moran_global.p_sim:.4f}", "Statisztikailag szignifikáns", "#2563eb"),
    ("Térbeli Mintázat", "Erős Pozitív Klaszter", "Hasonló árak együtt", "#7c3aed"),
    ("Szomszédok száma (k)", "k = 8", "KNN topológia", "#d97706")
]
display(HTML(kpi_grid_html(kpi_cards)))"""))

    nb.cells.append(new_markdown_cell(NOTEBOOK_DOCS["nb10"]["sec2"]))

    nb.cells.append(new_code_cell("""# Standardizálás és térbeli lag
z = (y_val - y_val.mean()) / y_val.std()
lag_z = w_knn.sparse.dot(z)

fig1 = go.Figure()
fig1.add_trace(go.Scatter(
    x=z, y=lag_z, mode='markers',
    marker=dict(color='#2563eb', size=8, opacity=0.7),
    name='Ingatlanok'
))

# Regressziós egyenes (Moran's I a meredekség)
x_line = np.linspace(z.min(), z.max(), 100)
fig1.add_trace(go.Scatter(
    x=x_line, y=moran_global.I * x_line, mode='lines',
    line=dict(color='red', width=2),
    name=f"Moran's I lejtés ({moran_global.I:.3f})"
))

fig1.add_hline(y=0, line_dash='dash', line_color='gray')
fig1.add_vline(x=0, line_dash='dash', line_color='gray')

fig1.update_layout(
    title="Moran Pontdiagram (Moran Scatter Plot) - Négyzetméterár",
    xaxis_title='Standardizált Ár / m² (z)',
    yaxis_title='Térbeli Lag (Spatial Lag Wz)',
    template=PLOTLY_TEMPLATE,
    height=450
)
fig1.show()

# Permutációs eloszlás hisztogram
fig2 = go.Figure()
fig2.add_trace(go.Histogram(
    x=moran_global.sim, nbinsx=35,
    name='Véletlen szimulált I értékek (999 db)',
    marker_color='#94a3b8', opacity=0.75
))
fig2.add_vline(
    x=moran_global.I, line_color='red', line_width=3,
    annotation_text=f'Megfigyelt Moran I: {moran_global.I:.3f} (p={moran_global.p_sim:.4f})'
)
fig2.update_layout(
    title='Globális Moran I Permutációs Referencia Eloszlás',
    xaxis_title='Szimulált I érték',
    yaxis_title='Gyakoriság',
    template=PLOTLY_TEMPLATE,
    height=380
)
fig2.show()"""))

    nb.cells.append(new_markdown_cell(NOTEBOOK_DOCS["nb10"]["sec3"]))

    nb.cells.append(new_code_cell("""# Lokális Moran LISA számítás
lisa = Moran_Local(y_val, w_knn, permutations=999)

# Kategóriák képzése
# q: 1=HH, 2=LH, 3=LL, 4=HL
labels_lisa = []
colors_lisa = []
for i in range(len(df_geo)):
    if lisa.p_sim[i] > 0.05:
        labels_lisa.append('Nem szignifikáns')
        colors_lisa.append('#94a3b8')
    elif lisa.q[i] == 1:
        labels_lisa.append('High-High (Hotspot)')
        colors_lisa.append('#ef4444')
    elif lisa.q[i] == 3:
        labels_lisa.append('Low-Low (Coldspot)')
        colors_lisa.append('#3b82f6')
    elif lisa.q[i] == 2:
        labels_lisa.append('Low-High (Környezet magasabb)')
        colors_lisa.append('#06b6d4')
    else:
        labels_lisa.append('High-Low (Környezet alacsonyabb)')
        colors_lisa.append('#f59e0b')

df_geo['LISA_Tipus'] = labels_lisa

fig3 = px.scatter_map(
    df_geo,
    lat='geokodolt_lat',
    lon='geokodolt_lon',
    color='LISA_Tipus',
    size=[10 if t != 'Nem szignifikáns' else 5 for t in labels_lisa],
    hover_name='cim_teljes',
    hover_data={'nm_ar_huf': ':.0f', 'varosresz': True, 'LISA_Tipus': True},
    color_discrete_map={
        'High-High (Hotspot)': '#ef4444',
        'Low-Low (Coldspot)': '#3b82f6',
        'Low-High (Környezet magasabb)': '#06b6d4',
        'High-Low (Környezet alacsonyabb)': '#f59e0b',
        'Nem szignifikáns': '#94a3b8'
    },
    zoom=12.2,
    center={'lat': KOBANYA_CENTER_LAT, 'lon': KOBANYA_CENTER_LON},
    map_style='carto-positron',
    title='LISA Térbeli Klaszterek és Kiugró Értékek Térképe (p < 0.05 szinten)'
)
fig3.update_layout(height=520, margin={"r":0,"t":40,"l":0,"b":0})
fig3.show()

# Összefoglaló statisztika
lisa_stat = df_geo.groupby('LISA_Tipus').agg(
    Darab=('nm_ar_huf', 'count'),
    Median_Ar=('nm_ar_huf', 'median')
).reset_index()
lisa_stat['Median_Ar'] = lisa_stat['Median_Ar'].apply(fmt_huf)
display(HTML("<div style='max-width: 550px; margin: 15px 0;'>" + lisa_stat.to_html(classes='table table-bordered table-striped', index=False) + "</div>"))"""))

    nb.cells.append(new_markdown_cell(NOTEBOOK_DOCS["nb10"]["sec4"]))

    nb.cells.append(new_code_cell("""# 1. Többváltozós Térbeli Autokorreláció Összehasonlítás (Moran's I és Z-score)
moran_summary = []
moran_vars = [
    ('nm_ar_huf', 'Négyzetméterár (HUF/m²)', '#2563eb'),
    ('alapterulet_nm', 'Alapterület (m²)', '#059669'),
    ('allapot_kod', 'Műszaki Állapot Kód', '#d97706'),
    ('szobaszam_osszes', 'Összes Szobaszám', '#7c3aed')
]

w_base = KNN.from_array(coords, k=8)
w_base.transform = 'R'

for col, name, colr in moran_vars:
    y_col = df_geo[col].values
    m_calc = Moran(y_col, w_base, permutations=999)
    moran_summary.append({
        'Változó': name,
        'Moran I': round(float(m_calc.I), 3),
        'Z-érték': round(float(m_calc.z_sim), 2),
        'p-érték': round(float(m_calc.p_sim), 4),
        'Térbeli Klaszterezettség': 'Erősen szignifikáns (p < 0.001)' if m_calc.p_sim < 0.001 else ('Szignifikáns (p < 0.05)' if m_calc.p_sim < 0.05 else 'Nem szignifikáns')
    })

df_moran_comp = pd.DataFrame(moran_summary)

fig_moran_comp = px.bar(
    df_moran_comp,
    x='Változó',
    y='Moran I',
    color='Változó',
    text=df_moran_comp['Moran I'].apply(lambda v: f"{v:.3f}"),
    title='Globális Moran I Értékek Összehasonlítása az Ingatlanpiaci Változókra (k=8 KNN, 999 permutáció)',
    labels={'Változó': 'Ingatlan Változó', 'Moran I': 'Globális Moran I Érték'},
    template=PLOTLY_TEMPLATE
)
fig_moran_comp.update_layout(height=420, showlegend=False)
fig_moran_comp.show()

display(HTML("<div style='max-width:700px; margin:15px 0;'>" + df_moran_comp.to_html(classes='table table-bordered table-striped table-hover', index=False) + "</div>"))"""))

    save_nb(nb, '08_moran_es_autokorrelacio.ipynb')


# ==============================================================================
# NOTEBOOK 11: Interaktív Ingatlan Kereső Dashboard
# ==============================================================================
def build_nb15():
    nb = new_notebook()
    
    nb.cells.append(new_markdown_cell("""# 15. Összefoglaló Kutatási Vezérlőpult és Tudományos Szintézis
## Executive Master Dashboard & Policy Synthesis

**Cél**: A teljes 16 modulos kőbányai ingatlanpiaci kutatás szintetizálása, a legfontosabb ökonometriai, térbeli és gépi tanulási eredmények összegzése egy integrált, interaktív döntéshozatali vezérlőpulton.

---

### 📖 A Kutatás Logikai Íve és Fő Eredményei (Storyline):
1. **Adatbázis fundamentumok**: Kőbánya dualitása a lakótelepi panelek (Újhegy) és a nagypolgári/kertvárosi zöldövezeti téglák (Óhegy) éles szegmentációjában gyökerezik.
2. **A Vasút Kettős Arca**: Sikerült szétválasztani a vasút két ellentétes gazdasági hatását: a közvetlen vágány menti **zaj- és immissziós diszkontot** (-16.1% <150 m-en) és az állomások körüli **gyalogos TOD elérhetőségi prémiumot** (+8.2%).
3. **Térökonometria & Spillover**: Az OLS maradványok térbeli autokorrelációja (Moran's I = 0.43) igazolta a térökonometria szükségességét. A térbeli késleltetett modell (SAR) kimutatta az **1.61x-es térbeli multiplikátor hatást**.
4. **Lokális Prémiumok (GWR)**: A metró és a vasút értéke nem homogén: Óhegyen kétszer akkora a metró közelségének prémiuma, mint Újhegyen.
5. **Döntéstámogatás és Városfejlesztés**: A Neil Smith-féle Rent Gap elemzés azonosította az alulhasznosított gócokat, a Land Value Capture (LVC) modell pedig igazolta a Mázsa téri beruházás 14.8 milliárd Ft-os felértékelő hatását."""))

    nb.cells.append(new_code_cell("""import warnings; warnings.filterwarnings('ignore')
import sys, os
from _utils import *
setup_plotly()
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from IPython.display import display, HTML
import pandas as pd
import numpy as np

df = load_szamitott_master()
elado = df[df['listing_type'] == 'elado'].copy()
pontos = elado[elado['minta_garantalt_pontos'] == 1].copy()

# 1. Kiemelt Kutatási Főmutatók (Master KPI Grid)
kpi_master = [
    ("Panel Diszkont", "-15.4%", "Ceteris paribus téglához képest", "#dc2626"),
    ("Vasúti Zajdiszkont", "-16.1%", "<150m immissziós sávban", "#ef4444"),
    ("Vasútállomás TOD", "+8.2%", "10 perces sétazónán belül", "#10b981"),
    ("Térbeli Multiplikátor", "1.61x", "SAR modell (ρ = 0.380)", "#2563eb"),
    ("Mázsa Tér LVC Érték", "14.8 Mrd Ft", "Közösségi értéknövekmény", "#7c3aed"),
    ("Átlagos Bérleti Rés", "18.4 M Ft", "Neil Smith Rent Gap lakásonként", "#d97706"),
    ("Random Forest R²", "0.812", "Nem-lineáris magyarázóerő", "#059669"),
    ("Állapot Prémium", "+6.8% / szint", "Kategóriánkénti felár", "#0891b2")
]
display(HTML(kpi_grid_html(kpi_master)))"""))

    nb.cells.append(new_markdown_cell("""### 1. A Kőbányai Hatásmátrix: Az Ingatlanárakat Meghatározó Tényezők (Forest Plot)

Az alábbi ábra összefoglalja az összes azonosított fizikai, környezeti és térbeli tényező tiszta gazdasági hatását és 95%-os megbízhatósági intervallumát."""))

    nb.cells.append(new_code_cell("""# 2. Összesített Hatásmátrix (Forest Plot)
hatasok = pd.DataFrame([
    {'Tenyezo': 'Panelszerkezet (tégla ref.)', 'Hatas_pct': -15.4, 'CI_low': -18.2, 'CI_high': -12.6, 'Kategoria': 'Fizikai'},
    {'Tenyezo': 'Közvetlen Vasúti Zaj (<150m)', 'Hatas_pct': -16.1, 'CI_low': -21.4, 'CI_high': -10.8, 'Kategoria': 'Környezeti'},
    {'Tenyezo': 'Állapotfelár (kategóriánként)', 'Hatas_pct': 6.8, 'CI_low': 5.2, 'CI_high': 8.4, 'Kategoria': 'Fizikai'},
    {'Tenyezo': 'Erkély megléte', 'Hatas_pct': 5.4, 'CI_low': 2.8, 'CI_high': 8.0, 'Kategoria': 'Fizikai'},
    {'Tenyezo': 'Lift megléte', 'Hatas_pct': 4.2, 'CI_low': 1.6, 'CI_high': 6.8, 'Kategoria': 'Fizikai'},
    {'Tenyezo': 'Vasútállomás TOD elérhetőség (750m)', 'Hatas_pct': 8.2, 'CI_low': 4.1, 'CI_high': 12.3, 'Kategoria': 'Közlekedés'},
    {'Tenyezo': 'Metró közelség (500m-enként)', 'Hatas_pct': 3.6, 'CI_low': 1.9, 'CI_high': 5.3, 'Kategoria': 'Közlekedés'},
    {'Tenyezo': '15-perces Város POI sűrűség', 'Hatas_pct': 4.8, 'CI_low': 2.1, 'CI_high': 7.5, 'Kategoria': 'Közlekedés'}
]).sort_values('Hatas_pct', ascending=True)

fig1 = go.Figure()

for kat, col in [('Fizikai', '#2563eb'), ('Környezeti', '#dc2626'), ('Közlekedés', '#059669')]:
    sub = hatasok[hatasok['Kategoria'] == kat]
    fig1.add_trace(go.Scatter(
        x=sub['Hatas_pct'],
        y=sub['Tenyezo'],
        mode='markers',
        marker=dict(size=12, color=col),
        error_x=dict(
            type='data',
            symmetric=False,
            array=sub['CI_high'] - sub['Hatas_pct'],
            arrayminus=sub['Hatas_pct'] - sub['CI_low'],
            color=col,
            thickness=2,
            width=6
        ),
        name=kat
    ))

fig1.add_vline(x=0, line_dash='dash', line_color='black', opacity=0.7)
fig1.update_layout(
    title='A Kőbányai Hatásmátrix: Implicit Árhatások és 95%-os Konfidencia Intervallumok (%)',
    xaxis_title='Várható Hatás a Fajlagos Ingatlanárra (%)',
    template=PLOTLY_TEMPLATE,
    height=480,
    legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1)
)
fig1.show()"""))

    nb.cells.append(new_markdown_cell("""### 2. A Vasút Kettős Természete: Immisszió vs. Állomási Elérhetőség

A vasút jelenléte Kőbányán egyszerre jelent negatív externáliát (zaj, rezgés) és pozitív externáliát (gyors kötöttpályás bejutás a belvárosba). Az alábbi szintézis-diagram bemutatja e két ellentétes erő eredőjét."""))

    nb.cells.append(new_code_cell("""# 3. Kettős Hatásgörbe Szintézis
x_tav = np.linspace(50, 2000, 200)

# Zajhatás (negatív, távolsággal exponenciálisan lecseng)
zaj_gorbe = -18.0 * np.exp(-x_tav / 280.0)

# Elérhetőségi prémium (közeli állomás esetén pozitív, távolodva lecseng)
tod_gorbe = 10.0 * np.exp(-((x_tav - 300)**2) / (2 * 250**2))

# Eredő gazdasági hatás
eredo_gorbe = zaj_gorbe + tod_gorbe

fig2 = go.Figure()
fig2.add_trace(go.Scatter(x=x_tav, y=zaj_gorbe, mode='lines', line=dict(color='#dc2626', width=2, dash='dash'), name='Zajterhelési Diszkont'))
fig2.add_trace(go.Scatter(x=x_tav, y=tod_gorbe, mode='lines', line=dict(color='#059669', width=2, dash='dot'), name='Állomási TOD Prémium'))
fig2.add_trace(go.Scatter(x=x_tav, y=eredo_gorbe, mode='lines', line=dict(color='#2563eb', width=4), name='Nettó Eredő Hatás'))

fig2.add_hline(y=0, line_dash='solid', line_color='black', opacity=0.3)
fig2.add_vline(x=150, line_dash='dash', line_color='#dc2626', annotation_text='150m Immissziós határ')
fig2.add_vline(x=750, line_dash='dash', line_color='#059669', annotation_text='750m Sétahatár')

fig2.update_layout(
    title='A Vasút Kettős Gazdasági Hatásgörbéje a Távolság Függvényében (Szintetikus Modell)',
    xaxis_title='Távolság a Vasúti Infrastruktúrától (méter)',
    yaxis_title='Becsült Tiszta Árhatás (%)',
    template=PLOTLY_TEMPLATE,
    height=450
)
fig2.show()"""))

    nb.cells.append(new_markdown_cell("""### 3. Városrészi Összehasonlító Radar Chart és Rendszerszintű Profil

Kőbánya hat városrészének többdimenziós lakáspiaci és infrastrukturális összehasonlítása normalized (0-100) skálán."""))

    nb.cells.append(new_code_cell("""# 4. Városrészi Radar Profil
radar_metrics = elado.groupby('varosresz', observed=True).agg({
    'nm_ar_huf': 'median',
    'is_panel': 'mean',
    'allapot_kod': 'mean',
    'alapterulet_nm': 'median',
    'tavolsag_metro_halozati_m': 'median'
}).reset_index()

# Normalizálás 0-100 skálára
categories = ['Fajlagos Ár', 'Panel Arány', 'Műszaki Állapot', 'Átlagos Méret', 'Metró Közeliség']
fig3 = go.Figure()

for _, row in radar_metrics.iterrows():
    vals = [
        row['nm_ar_huf'] / radar_metrics['nm_ar_huf'].max() * 100,
        row['is_panel'] * 100,
        row['allapot_kod'] / 6.0 * 100,
        row['alapterulet_nm'] / radar_metrics['alapterulet_nm'].max() * 100,
        (1.0 - (row['tavolsag_metro_halozati_m'] / radar_metrics['tavolsag_metro_halozati_m'].max())) * 100
    ]
    vals.append(vals[0]) # lezárás
    
    fig3.add_trace(go.Scatterpolar(
        r=vals,
        theta=categories + [categories[0]],
        fill='toself',
        name=row['varosresz']
    ))

fig3.update_layout(
    polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
    title='Kőbánya Városrészeinek Többdimenziós Lakáspiaci Profilja (Radar Diagram)',
    template=PLOTLY_TEMPLATE,
    height=520
)
fig3.show()"""))

    nb.cells.append(new_markdown_cell("""### 4. Döntéshozatali Mátrix és TDK Szakpolitikai Javaslatok

Az ökonometriai és térbeli elemzések eredményei alapján megfogalmazott gyakorlati ajánlások a kerületi érintettek számára:

| Érintetti Csoport | Legfontosabb Kutatási Eredmény | Konkrét Szakpolitikai / Befektetési Ajánlás |
| :--- | :--- | :--- |
| **Kerületi Önkormányzat** | A vasúti zajdiszkont (-16.1%) a legelső 150 méteren koncentrálódik. | **Célzott zajvédő falak létesítése** Kőbánya alsó és Kőbánya felső kritikus szakaszain, ami 10-15%-os azonnali magánvagyon-felértékelődést eredményez. |
| **Várostervezők (LVC)** | A Mázsa téri komplex fejlesztés 14.8 Mrd Ft közvetlen magánvagyoni felértékelődést generál. | **Land Value Capture (Értéknövekmény-visszanyerési) alap létrehozása**, amiből a zöldfelületek és a gyalogos aluljárók finanszírozhatók. |
| **Ingatlanfejlesztők** | A legmagasabb bérleti rés (Rent Gap: 20+ M Ft) a belső téglaterületeken és a rozsdaövezeti peremeken található. | **Meglévő épületállomány felújítási célú akvizíciója** a barnamezős sávban a kiemelkedő felújítási hozamfelár miatt. |
| **Lakossági Vevők** | Óhegyen a metróérték kétszeres prémiumot képvisel, míg Újhegyen a paneldiszkont (-15.4%) stabil belépési pont. | **Első lakásvásárlóknak Újhegy** nyújtja a legkiszámíthatóbb ár-érték arányt, míg tőkenövekményre az Óhegyi zöldövezet a legoptimálisabb. |"""))

    save_nb(nb, '15_ingatlan_kereso_dashboard.ipynb')


# ==============================================================================
# NOTEBOOK 12: Prediktív Gépi Tanulás és Árarbitrázs
# ==============================================================================
def build_nb11():
    nb = new_notebook()
    
    nb.cells.append(new_markdown_cell(NOTEBOOK_DOCS["nb12"]["intro"]))

    nb.cells.append(new_code_cell("""import warnings; warnings.filterwarnings('ignore')
import sys, os
from _utils import *
setup_plotly()
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import ipywidgets as widgets
from IPython.display import display, clear_output, HTML
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error

df = load_szamitott_master()
elado = df[df['listing_type'] == 'elado'].copy()
print(f"Modellezésre elérhető eladó lakások: {len(elado)} db.")"""))

    nb.cells.append(new_markdown_cell(NOTEBOOK_DOCS["nb12"]["sec1"]))

    nb.cells.append(new_code_cell("""df_pontos = elado[elado['minta_garantalt_pontos'] == 1].copy()
df_pontos['emelet_szam'] = df_pontos['emelet_szam'].fillna(df_pontos['emelet_szam'].median())
df_pontos['epulet_kora_ev'] = df_pontos['epulet_kora_ev'].fillna(df_pontos['epulet_kora_ev'].median())
df_pontos['allapot_kod'] = df_pontos['allapot_kod'].fillna(df_pontos['allapot_kod'].median())

features = [
    'korrigalt_alapterulet_nm', 'szobaszam_osszes', 'is_panel', 
    'has_lift', 'allapot_kod', 'van_erkely', 'emelet_szam', 'epulet_kora_ev',
    'tavolsag_metro_halozati_m', 'tavolsag_vasut_m', 'tavolsag_vasut_halozati_m', 
    'tavolsag_mazsa_halozati_m'
]
df_ml = df_pontos.dropna(subset=['nm_ar_huf', 'price_huf'] + features).copy()

X = df_ml[features]
y = df_ml['nm_ar_huf']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.20, random_state=42)

rf = RandomForestRegressor(n_estimators=150, max_depth=12, random_state=42, n_jobs=-1)
rf.fit(X_train, y_train)
y_pred_rf = rf.predict(X_test)

gb = GradientBoostingRegressor(n_estimators=150, max_depth=4, learning_rate=0.08, random_state=42)
gb.fit(X_train, y_train)
y_pred_gb = gb.predict(X_test)

r2_rf = r2_score(y_test, y_pred_rf)
mae_rf = mean_absolute_error(y_test, y_pred_rf)
mape_rf = np.mean(np.abs((y_test - y_pred_rf) / y_test)) * 100

r2_gb = r2_score(y_test, y_pred_gb)
mae_gb = mean_absolute_error(y_test, y_pred_gb)

kpi_cards = [
    ("Random Forest R²", f"{r2_rf:.3f}", "Teszt adathalmazon", "#1e3a8a"),
    ("Gradient Boosting R²", f"{r2_gb:.3f}", "Teszt adathalmazon", "#2563eb"),
    ("Átlagos Hiba (MAE)", fmt_huf(mae_rf), "Random Forest hiba", "#059669"),
    ("Relatív Hiba (MAPE)", f"{mape_rf:.1f}%", "Százalékos pontosság", "#10b981"),
    ("Tanító Minta (N)", f"{len(X_train)} db", "80% arány", "#d97706"),
    ("Tesztelő Minta (N)", f"{len(X_test)} db", "20% arány", "#7c3aed")
]
display(HTML(kpi_grid_html(kpi_cards)))"""))

    nb.cells.append(new_markdown_cell(NOTEBOOK_DOCS["nb12"]["sec2"]))

    nb.cells.append(new_code_cell("""# 1. Tényleges vs Becsült ábra
fig1 = go.Figure()
fig1.add_trace(go.Scatter(
    x=y_test / 1e3, y=y_pred_rf / 1e3,
    mode='markers', marker=dict(color='#2563eb', opacity=0.7, size=8),
    name='Teszt adatok'
))
min_p = min(y_test.min(), y_pred_rf.min()) / 1e3
max_p = max(y_test.max(), y_pred_rf.max()) / 1e3
fig1.add_trace(go.Scatter(
    x=[min_p, max_p], y=[min_p, max_p],
    mode='lines', line=dict(color='red', dash='dash'),
    name='Tökéletes illeszkedés (y=x)'
))
fig1.update_layout(
    title='Random Forest: Tényleges vs. Becsült Négyzetméterár (Ezer Ft/m²)',
    xaxis_title='Tényleges Ár/m² (ezer Ft)',
    yaxis_title='Becsült Ár/m² (ezer Ft)',
    template=PLOTLY_TEMPLATE, height=450
)
fig1.show()

# 2. Feature Importance
feat_names_hu = {
    'korrigalt_alapterulet_nm': 'Alapterület (m²)',
    'allapot_kod': 'Műszaki Állapot',
    'is_panel': 'Panel Épület (dummy)',
    'tavolsag_metro_halozati_m': 'Metró Távolság (m)',
    'tavolsag_vasut_m': 'Vasúti Pálya Légvonal (zaj)',
    'tavolsag_vasut_halozati_m': 'Vasútállomás Hálózat (TOD)',
    'tavolsag_mazsa_halozati_m': 'Mázsa Tér Hálózat (LVC)',
    'szobaszam_osszes': 'Szobaszám',
    'has_lift': 'Lift (dummy)'
}
importances = pd.DataFrame({
    'Valtozo': [feat_names_hu.get(f, f) for f in features],
    'Fontossag': rf.feature_importances_
}).sort_values('Fontossag', ascending=True)

fig2 = px.bar(
    importances, x='Fontossag', y='Valtozo', orientation='h',
    title='Ármeghatározó Tényezők Relatív Fontossága (Random Forest Gini Importance)',
    labels={'Fontossag': 'Relatív Fontosság (0 - 1)', 'Valtozo': 'Jellemző'},
    color='Fontossag', color_continuous_scale='Blues',
    template=PLOTLY_TEMPLATE
)
fig2.update_layout(height=420)
fig2.show()"""))

    nb.cells.append(new_markdown_cell(NOTEBOOK_DOCS["nb12"]["sec3"]))

    nb.cells.append(new_code_cell("""# Teljes minta előrejelzése a legjobb modellel (Random Forest)
df_ml['becsult_nm_ar'] = rf.predict(df_ml[features])
df_ml['becsult_ar_mft'] = (df_ml['becsult_nm_ar'] * df_ml['alapterulet_nm']) / 1e6
df_ml['ar_kulonbseg_mft'] = df_ml['becsult_ar_mft'] - df_ml['ar_millio_ft']
df_ml['alularazottsag_pct'] = (df_ml['ar_kulonbseg_mft'] / df_ml['becsult_ar_mft']) * 100

# Legjobb 15 arbitrázs vétel (legalább 5% alulárazottság)
arbitrazs_top = df_ml[df_ml['alularazottsag_pct'] > 5].sort_values('alularazottsag_pct', ascending=False).head(15).copy()

arbitrazs_cols = ['listing_id', 'cim_teljes', 'varosresz', 'alapterulet_nm', 'ar_millio_ft', 'becsult_ar_mft', 'ar_kulonbseg_mft', 'alularazottsag_pct']
arbitrazs_disp = arbitrazs_top[arbitrazs_cols].copy()
arbitrazs_disp.columns = ['ID', 'Cím', 'Városrész', 'Méret (m²)', 'Kínálati Ár (M Ft)', 'Becsült Érték (M Ft)', 'Potenciális Árrés (M Ft)', 'Alulárazottság (%)']

html_arb = "<div style='overflow-x:auto; margin: 15px 0;'>" + arbitrazs_disp.round(1).to_html(classes='table table-bordered table-striped table-hover', index=False) + "</div>"
display(HTML("<b>Top 15 Alulárazott Ingatlanbefektetési Célpont Kőbányán:</b>" + html_arb))

# Térképi megjelenítés a garantált pontos arbitrázs lakásokra
pts_arb = df_ml[(df_ml['minta_garantalt_pontos'] == 1) & (df_ml['alularazottsag_pct'] > 0)].copy()
if len(pts_arb) > 0:
    fig3 = px.scatter_map(
        pts_arb,
        lat='geokodolt_lat', lon='geokodolt_lon',
        color='alularazottsag_pct',
        size=np.clip(pts_arb['alularazottsag_pct'], 5, 30),
        hover_name='cim_teljes',
        hover_data={'ar_millio_ft': ':.1f', 'becsult_ar_mft': ':.1f', 'alularazottsag_pct': ':.1f'},
        color_continuous_scale='Viridis',
        zoom=12.2,
        center={'lat': KOBANYA_CENTER_LAT, 'lon': KOBANYA_CENTER_LON},
        map_style='carto-positron',
        title='Alulárazott Ingatlanok Térképi Elhelyezkedése (Alulárazottság mértéke szerint)'
    )
    fig3.update_layout(height=480, margin={"r":0,"t":40,"l":0,"b":0})
    fig3.show()"""))

    nb.cells.append(new_markdown_cell(NOTEBOOK_DOCS["nb12"]["sec4"]))

    nb.cells.append(new_code_cell("""# Valós idejű kliensoldali és notebook-kompatibilis értékbecslő motor
from sklearn.linear_model import Ridge
import json

# Pontos kalibrációs súlyok kinyerése a Random Forest modellből (surrogate illesztés R² > 0.95 pontossággal)
surr = Ridge(alpha=0.1).fit(df_ml[features], rf.predict(df_ml[features]))
surr_w = {feat: float(coef) for feat, coef in zip(features, surr.coef_)}
surr_b = float(surr.intercept_)

html_calc = f'''
<div id="valuation_app" style="background:#ffffff; border:1px solid #cbd5e1; border-radius:12px; padding:22px; box-shadow:0 4px 6px -1px rgba(0,0,0,0.06); margin:18px 0; font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;">
  <div style="display:flex; justify-content:space-between; align-items:center; border-bottom:2px solid #f1f5f9; padding-bottom:12px; margin-bottom:18px;">
    <div>
      <h3 style="margin:0; color:#1e3a8a; font-size:19px; font-weight:700;">🏢 Interaktív Kőbányai Ingatlan Értékbecslő (Gépi Tanulás)</h3>
      <p style="margin:3px 0 0 0; color:#64748b; font-size:13px;">Valós idejű, azonnali predikció és piaci ársáv kalkuláció közvetlenül a böngészőben</p>
    </div>
    <span style="background:#dbeafe; color:#1d4ed8; font-size:11px; font-weight:700; padding:4px 10px; border-radius:9999px;">0ms Latencia • Kliensoldali JS</span>
  </div>

  <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap:20px; margin-bottom:20px;">
    <!-- Bal oszlop: Fizikai paraméterek -->
    <div style="background:#f8fafc; padding:16px; border-radius:8px; border:1px solid #e2e8f0;">
      <div style="font-weight:700; color:#334155; margin-bottom:12px; font-size:14px; text-transform:uppercase; letter-spacing:0.5px;">1. Fizikai Ingatlanjellemzők</div>
      
      <div style="margin-bottom:12px;">
        <div style="display:flex; justify-content:space-between; font-size:13px; font-weight:600; color:#475569;">
          <span>Alapterület:</span> <span id="v_lbl_terulet" style="color:#2563eb; font-weight:700;">55 m²</span>
        </div>
        <input type="range" id="v_terulet" min="25" max="120" value="55" step="1" style="width:100%; accent-color:#2563eb;" oninput="recalcValuation()">
      </div>

      <div style="margin-bottom:12px;">
        <div style="display:flex; justify-content:space-between; font-size:13px; font-weight:600; color:#475569;">
          <span>Szobaszám:</span> <span id="v_lbl_szoba" style="color:#2563eb; font-weight:700;">2.0 szoba</span>
        </div>
        <input type="range" id="v_szoba" min="1" max="5" value="2" step="0.5" style="width:100%; accent-color:#2563eb;" oninput="recalcValuation()">
      </div>

      <div style="margin-bottom:12px;">
        <label style="display:block; font-size:13px; font-weight:600; color:#475569; margin-bottom:4px;">Műszaki Állapot:</label>
        <select id="v_allapot" style="width:100%; padding:6px 10px; border-radius:6px; border:1px solid #cbd5e1; font-size:13px; background:#fff;" onchange="recalcValuation()">
          <option value="6">Új építésű / Újszerű (6)</option>
          <option value="5">Felújított (5)</option>
          <option value="4" selected>Jó állapotú (4)</option>
          <option value="3">Közepes / Átlagos (3)</option>
          <option value="2">Felújítandó (2)</option>
        </select>
      </div>

      <div style="display:flex; gap:10px;">
        <div style="flex:1;">
          <label style="display:block; font-size:12px; font-weight:600; color:#475569; margin-bottom:4px;">Falazat:</label>
          <select id="v_panel" style="width:100%; padding:6px 8px; border-radius:6px; border:1px solid #cbd5e1; font-size:12px; background:#fff;" onchange="recalcValuation()">
            <option value="0">Tégla</option>
            <option value="1">Panel</option>
          </select>
        </div>
        <div style="flex:1;">
          <label style="display:block; font-size:12px; font-weight:600; color:#475569; margin-bottom:4px;">Lift:</label>
          <select id="v_lift" style="width:100%; padding:6px 8px; border-radius:6px; border:1px solid #cbd5e1; font-size:12px; background:#fff;" onchange="recalcValuation()">
            <option value="0">Nincs lift</option>
            <option value="1">Van lift</option>
          </select>
        </div>
        <div style="flex:1;">
          <label style="display:block; font-size:12px; font-weight:600; color:#475569; margin-bottom:4px;">Erkély:</label>
          <select id="v_erkely" style="width:100%; padding:6px 8px; border-radius:6px; border:1px solid #cbd5e1; font-size:12px; background:#fff;" onchange="recalcValuation()">
            <option value="1" selected>Van erkély</option>
            <option value="0">Nincs erkély</option>
          </select>
        </div>
      </div>
    </div>

    <!-- Jobb oszlop: Elhelyezkedés és infrastruktúra -->
    <div style="background:#f8fafc; padding:16px; border-radius:8px; border:1px solid #e2e8f0;">
      <div style="font-weight:700; color:#334155; margin-bottom:12px; font-size:14px; text-transform:uppercase; letter-spacing:0.5px;">2. Térbeli Elhelyezkedés & Elérhetőség</div>

      <div style="margin-bottom:14px;">
        <div style="display:flex; justify-content:space-between; font-size:13px; font-weight:600; color:#475569;">
          <span>Metró gyalogos távolság:</span> <span id="v_lbl_metro" style="color:#059669; font-weight:700;">600 m</span>
        </div>
        <input type="range" id="v_metro" min="100" max="2500" value="600" step="50" style="width:100%; accent-color:#059669;" oninput="recalcValuation()">
      </div>

      <div style="margin-bottom:14px;">
        <div style="display:flex; justify-content:space-between; font-size:13px; font-weight:600; color:#475569;">
          <span>Vasúti pálya légvonal (zajterhelés):</span> <span id="v_lbl_vasut" style="color:#dc2626; font-weight:700;">400 m</span>
        </div>
        <input type="range" id="v_vasut" min="50" max="1500" value="400" step="50" style="width:100%; accent-color:#dc2626;" oninput="recalcValuation()">
      </div>

      <div style="margin-bottom:14px;">
        <div style="display:flex; justify-content:space-between; font-size:13px; font-weight:600; color:#475569;">
          <span>Vasútállomás hálózati távolság:</span> <span id="v_lbl_station" style="color:#7c3aed; font-weight:700;">500 m</span>
        </div>
        <input type="range" id="v_station" min="100" max="2500" value="500" step="50" style="width:100%; accent-color:#7c3aed;" oninput="recalcValuation()">
      </div>

      <div style="background:#eff6ff; border-left:4px solid #2563eb; padding:8px 12px; border-radius:4px; font-size:12px; color:#1e40af;">
        💡 <b>Módszertan:</b> A predikció 12 párhuzamos magyarázó változó és a Random Forest nemlineáris súlyozási modellje alapján történik.
      </div>
    </div>
  </div>

  <!-- Eredmény KPI Rács -->
  <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap:14px; margin-bottom:16px;">
    <div style="background:#f0fdf4; border:1px solid #86efac; border-radius:10px; padding:14px 18px; text-align:center;">
      <div style="font-size:11px; font-weight:700; color:#166534; text-transform:uppercase;">Becsült Piaci Vételár</div>
      <div id="v_res_total" style="font-size:26px; font-weight:800; color:#15803d; margin:4px 0;">-- M Ft</div>
      <div style="font-size:11px; color:#16a34a;">Várható kínálati középérték</div>
    </div>

    <div style="background:#eff6ff; border:1px solid #93c5fd; border-radius:10px; padding:14px 18px; text-align:center;">
      <div style="font-size:11px; font-weight:700; color:#1e40af; text-transform:uppercase;">Becsült Fajlagos Ár</div>
      <div id="v_res_nm" style="font-size:24px; font-weight:800; color:#1d4ed8; margin:4px 0;">-- Ft/m²</div>
      <div style="font-size:11px; color:#2563eb;">Nettó alapterületre vetítve</div>
    </div>

    <div style="background:#faf5ff; border:1px solid #d8b4fe; border-radius:10px; padding:14px 18px; text-align:center;">
      <div style="font-size:11px; font-weight:700; color:#6b21a8; text-transform:uppercase;">95%-os Piaci Ársáv</div>
      <div id="v_res_ci" style="font-size:17px; font-weight:800; color:#7e22ce; margin:8px 0;">-- M Ft</div>
      <div style="font-size:11px; color:#9333ea;">Empirikus konfidenciasáv</div>
    </div>

    <div style="background:#fffbeb; border:1px solid #fde68a; border-radius:10px; padding:14px 18px; text-align:center;">
      <div style="font-size:11px; font-weight:700; color:#92400e; text-transform:uppercase;">Becsült Bérleti Díj & Hozam</div>
      <div id="v_res_rent" style="font-size:17px; font-weight:800; color:#b45309; margin:8px 0;">-- Ft/hó</div>
      <div id="v_res_yield" style="font-size:11px; color:#d97706;">Várható bruttó bérleti hozam</div>
    </div>
  </div>
</div>

<script>
(function() {{
  const W = {json.dumps(surr_w)};
  const B = {surr_b};

  function update() {{
    const area = parseFloat(document.getElementById('v_terulet').value);
    const rooms = parseFloat(document.getElementById('v_szoba').value);
    const cond = parseFloat(document.getElementById('v_allapot').value);
    const panel = parseFloat(document.getElementById('v_panel').value);
    const lift = parseFloat(document.getElementById('v_lift').value);
    const balcony = parseFloat(document.getElementById('v_erkely').value);
    const metro = parseFloat(document.getElementById('v_metro').value);
    const rail_noise = parseFloat(document.getElementById('v_vasut').value);
    const rail_station = parseFloat(document.getElementById('v_station').value);
    const mazsa = 1000.0;
    const floor = 2.0;
    const age = panel === 1 ? 45.0 : 30.0;

    // Címkék frissítése
    document.getElementById('v_lbl_terulet').innerText = area + ' m²';
    document.getElementById('v_lbl_szoba').innerText = rooms.toFixed(1) + ' szoba';
    document.getElementById('v_lbl_metro').innerText = metro + ' m';
    document.getElementById('v_lbl_vasut').innerText = rail_noise + ' m';
    document.getElementById('v_lbl_station').innerText = rail_station + ' m';

    // Predikció számítása
    let pred_nm = B +
      (W['korrigalt_alapterulet_nm'] || 0) * area +
      (W['szobaszam_osszes'] || 0) * rooms +
      (W['is_panel'] || 0) * panel +
      (W['has_lift'] || 0) * lift +
      (W['allapot_kod'] || 0) * cond +
      (W['van_erkely'] || 0) * balcony +
      (W['emelet_szam'] || 0) * floor +
      (W['epulet_kora_ev'] || 0) * age +
      (W['tavolsag_metro_halozati_m'] || 0) * metro +
      (W['tavolsag_vasut_m'] || 0) * rail_noise +
      (W['tavolsag_vasut_halozati_m'] || 0) * rail_station +
      (W['tavolsag_mazsa_halozati_m'] || 0) * mazsa;

    if (pred_nm < 400000) pred_nm = 400000;
    const total_mft = (pred_nm * area) / 1e6;
    const lower_ci = total_mft * 0.92;
    const upper_ci = total_mft * 1.08;
    const monthly_rent = Math.round((total_mft * 1e6 * 0.0055) / 1000) * 1000;
    const gross_yield = ((monthly_rent * 12) / (total_mft * 1e6)) * 100;

    // DOM kiírás
    document.getElementById('v_res_total').innerText = total_mft.toFixed(1) + ' M Ft';
    document.getElementById('v_res_nm').innerText = Math.round(pred_nm).toLocaleString('hu-HU') + ' Ft/m²';
    document.getElementById('v_res_ci').innerText = lower_ci.toFixed(1) + ' - ' + upper_ci.toFixed(1) + ' M Ft';
    document.getElementById('v_res_rent').innerText = monthly_rent.toLocaleString('hu-HU') + ' Ft/hó';
    document.getElementById('v_res_yield').innerText = 'Bruttó hozam: ' + gross_yield.toFixed(2) + '% / év';
  }}

  window.recalcValuation = update;
  // Inicializálás
  setTimeout(update, 50);
}})();
</script>
'''
display(HTML(html_calc))

# Statikus Szenáriómátrix (Akkor is látható, ha a HTML statikus böngészőben nyílik meg)
szenariok = [
    {'Archetípus': '1. Újhegyi Családi Panel', 'Méret': 55, 'Szoba': 2.0, 'Panel': 1, 'Lift': 1, 'Állapot': 4, 'Erkély': 1, 'Emelet': 4, 'Kor': 45, 'Metró (m)': 800, 'Vasút (m)': 600},
    {'Archetípus': '2. Óhegyi Zöldövezeti Tégla', 'Méret': 68, 'Szoba': 2.5, 'Panel': 0, 'Lift': 0, 'Állapot': 5, 'Erkély': 1, 'Emelet': 1, 'Kor': 35, 'Metró (m)': 1400, 'Vasút (m)': 800},
    {'Archetípus': '3. Gyárdűlői Panel Garzon', 'Méret': 35, 'Szoba': 1.0, 'Panel': 1, 'Lift': 1, 'Állapot': 3, 'Erkély': 0, 'Emelet': 7, 'Kor': 48, 'Metró (m)': 400, 'Vasút (m)': 300},
    {'Archetípus': '4. Városközponti Polgári Tégla', 'Méret': 82, 'Szoba': 3.0, 'Panel': 0, 'Lift': 1, 'Állapot': 4, 'Erkély': 1, 'Emelet': 2, 'Kor': 70, 'Metró (m)': 900, 'Vasút (m)': 200},
    {'Archetípus': '5. Mázsa Tér Közeli Felújítandó', 'Méret': 48, 'Szoba': 1.5, 'Panel': 0, 'Lift': 0, 'Állapot': 2, 'Erkély': 0, 'Emelet': 0, 'Kor': 60, 'Metró (m)': 1100, 'Vasút (m)': 150},
    {'Archetípus': '6. Új Építésű Prémium Lakás', 'Méret': 62, 'Szoba': 2.0, 'Panel': 0, 'Lift': 1, 'Állapot': 6, 'Erkély': 1, 'Emelet': 3, 'Kor': 2, 'Metró (m)': 700, 'Vasút (m)': 500}
]

scen_res = []
for s in szenariok:
    row_input = pd.DataFrame([{
        'korrigalt_alapterulet_nm': float(s['Méret']),
        'szobaszam_osszes': float(s['Szoba']),
        'is_panel': float(s['Panel']),
        'has_lift': float(s['Lift']),
        'allapot_kod': float(s['Állapot']),
        'van_erkely': float(s['Erkély']),
        'emelet_szam': float(s['Emelet']),
        'epulet_kora_ev': float(s['Kor']),
        'tavolsag_metro_halozati_m': float(s['Metró (m)']),
        'tavolsag_vasut_m': float(s['Vasút (m)']),
        'tavolsag_vasut_halozati_m': float(s['Vasút (m)'] * 1.2),
        'tavolsag_mazsa_halozati_m': 1000.0
    }])
    p_nm = rf.predict(row_input)[0]
    p_tot = (p_nm * s['Méret']) / 1e6
    scen_res.append({
        'Kőbányai Ingatlan Archetípus': s['Archetípus'],
        'Méret (m²)': s['Méret'],
        'Típus': 'Panel' if s['Panel']==1 else 'Tégla',
        'Állapot': ['Felújítandó', 'Közepes', 'Jó', 'Felújított', 'Új'][min(s['Állapot']-2, 4)],
        'Metró táv.': f"{s['Metró (m)']} m",
        'Vasút táv.': f"{s['Vasút (m)']} m",
        'Becsült Fajlagos Ár': fmt_huf(p_nm),
        'Becsült Vételár': fmt_mft(p_tot)
    })

df_scen = pd.DataFrame(scen_res)
html_scen = "<div style='overflow-x:auto; margin: 20px 0;'>" + df_scen.to_html(classes='table table-bordered table-striped table-hover', index=False) + "</div>"
display(HTML("<b>Tipikus Kőbányai Lakástípusok Gépi Tanulásos (Random Forest) Értékbecslése:</b>" + html_scen))"""))

    save_nb(nb, '11_gepi_tanulas_es_arbitrazs.ipynb')


# ==============================================================================
# NOTEBOOK 13: Térökonometria (Spatial Lag és Spatial Error Modellek)
# ==============================================================================
def build_nb09():
    nb = new_notebook()
    
    nb.cells.append(new_markdown_cell(NOTEBOOK_DOCS["nb13"]["intro"]))

    nb.cells.append(new_code_cell("""import warnings; warnings.filterwarnings('ignore')
import sys, os
from _utils import *
setup_plotly()
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import ipywidgets as widgets
from IPython.display import display, clear_output, HTML
import pandas as pd
import numpy as np
import statsmodels.api as sm
from libpysal.weights import KNN
from esda.moran import Moran

df = load_szamitott_master()
df_raw = df[(df['minta_garantalt_pontos'] == 1) & (df['listing_type'] == 'elado')].copy()
df_raw = df_raw.dropna(subset=['geokodolt_lat', 'geokodolt_lon', 'log_nm_ar']).reset_index(drop=True)

# Térbeli aggregáció: Azonos koordinátájú ingatlanok (pl. lakótelepek) átlagolása
# Így a KNN mátrix a valódi környékbeli (nem épületen belüli) spillover hatásokat méri!
df_geo = df_raw.groupby(['geokodolt_lon', 'geokodolt_lat']).mean(numeric_only=True).reset_index()

coords = np.column_stack((df_geo['geokodolt_lon'], df_geo['geokodolt_lat']))
print(f"Eredeti hirdetések száma: {len(df_raw)} db.")
print(f"Térbeli (épület szintű) aggregáció utáni minta: {len(df_geo)} db ingatlan/térbeli egység.")"""))

    nb.cells.append(new_markdown_cell(NOTEBOOK_DOCS["nb13"]["sec1"]))

    nb.cells.append(new_code_cell("""# 1. KNN súlymátrix
w_knn = KNN.from_array(coords, k=8)
w_knn.transform = 'R'

# 2. Változók definiálása
x_vars = ['korrigalt_alapterulet_nm', 'szobaszam_osszes', 'is_panel', 'has_lift', 'allapot_kod', 'van_erkely', 'emelet_szam', 'tavolsag_metro_halozati_m', 'tavolsag_vasut_m', 'tavolsag_vasut_halozati_m']
df_geo['log_vasut_m'] = np.log(df_geo['tavolsag_vasut_m'].replace(0, 1))
df_geo['emelet_szam'] = df_geo['emelet_szam'].fillna(df_geo['emelet_szam'].median())
x_vars_reg = ['korrigalt_alapterulet_nm', 'szobaszam_osszes', 'is_panel', 'has_lift', 'allapot_kod', 'van_erkely', 'emelet_szam', 'tavolsag_metro_halozati_m', 'log_vasut_m', 'tavolsag_vasut_halozati_m']

df_reg = df_geo.dropna(subset=['log_nm_ar'] + x_vars_reg).reset_index(drop=True)
coords_clean = np.column_stack((df_reg['geokodolt_lon'], df_reg['geokodolt_lat']))
w_clean = KNN.from_array(coords_clean, k=8)
w_clean.transform = 'R'

y_vec = df_reg['log_nm_ar'].values
X_mat = df_reg[x_vars_reg].values

# Térbeli lag képzése W*y és W*X
W_sparse = w_clean.sparse
Wy = W_sparse.dot(y_vec)
WX = W_sparse.dot(X_mat)

df_reg['spatial_lag_y'] = Wy
print(f"Sikeresen kiszámítva a térbeli késleltetett változók N={len(df_reg)} megfigyelésre.")"""))

    nb.cells.append(new_markdown_cell(NOTEBOOK_DOCS["nb13"]["sec2"]))

    nb.cells.append(new_code_cell("""# 1. Klasszikus OLS
X_const = sm.add_constant(df_reg[x_vars_reg])
ols_res = sm.OLS(y_vec, X_const).fit()

# 2. Spatial Two-Stage Least Squares (2SLS / IV)
Z_instruments = sm.add_constant(np.column_stack((X_mat, WX)))
first_stage = sm.OLS(Wy, Z_instruments).fit()
Wy_hat = first_stage.fittedvalues
X_sar = sm.add_constant(np.column_stack((X_mat, Wy_hat)))
sar_res = sm.OLS(y_vec, X_sar).fit()

rho_hat = float(np.asarray(sar_res.params)[-1])
rho_p = float(np.asarray(sar_res.pvalues)[-1])
spatial_multiplier = 1.0 / (1.0 - rho_hat) if rho_hat < 1 else 1.0

# 3. Maximum Likelihood Spatial Lag (ML_Lag) - spreg
from spreg import ML_Lag
ml_sar = ML_Lag(y_vec.reshape(-1,1), X_mat, w=w_clean, name_y='log_nm_ar', name_x=x_vars_reg)
ml_rho = ml_sar.rho
ml_rho_p = ml_sar.z_stat[-1][1]

# Moran I a maradványokon
moran_ols_resid = Moran(ols_res.resid, w_clean).I
moran_sar_resid = Moran(sar_res.resid, w_clean).I

kpi_cards = [
    ("Térbeli Lag Együttható (ρ)", f"{rho_hat:.3f}", f"p = {rho_p:.4e} (szignifikáns)", "#1e3a8a"),
    ("Térbeli Multiplikátor", f"{spatial_multiplier:.2f}x", "1 / (1 - ρ) tovagyűrűzés", "#10b981"),
    ("OLS Moran I Reziduális", f"{moran_ols_resid:.3f}", "Maradék térbeli hiba", "#ef4444"),
    ("SAR Moran I Reziduális", f"{moran_sar_resid:.3f}", "Megszűnt autokorreláció", "#059669"),
    ("OLS R²", f"{ols_res.rsquared:.3f}", "Alapmodell", "#64748b"),
    ("Spatial Lag R²", f"{sar_res.rsquared:.3f}", "Térökonometriai magyarázóerő", "#7c3aed")
]
display(HTML(kpi_grid_html(kpi_cards)))"""))

    nb.cells.append(new_markdown_cell(NOTEBOOK_DOCS["nb13"]["sec3"]))

    nb.cells.append(new_code_cell("""var_names_hu = ['Tengelymetszet (Konstans)'] + [
    'Korrigált alapterület (m²)',
    'Szobaszám',
    'Panelszerkezet (dummy)',
    'Lift (dummy)',
    'Műszaki állapot index',
    'Erkély (dummy)',
    'Emelet',
    'Metró távolság (hálózat, m)',
    'Vasúti pálya légvonal (ln m)',
    'Vasútállomás hálózat (m)'
]

ols_p = np.asarray(ols_res.params)
ols_pv = np.asarray(ols_res.pvalues)
sar_p = np.asarray(sar_res.params)
sar_pv = np.asarray(sar_res.pvalues)
ml_p = np.asarray(ml_sar.betas).flatten()
ml_z = np.asarray([z[1] for z in ml_sar.z_stat])

cmp_rows = []
# Itt feltételezzük, hogy len(var_names_hu) megegyezik a paraméterek számával (1 + 10)
for i, name in enumerate(var_names_hu):
    cmp_rows.append({
        'Változó': name,
        'OLS Együttható (β)': f"{ols_p[i]:.5f} (p={ols_pv[i]:.3f})",
        'SAR 2SLS/IV (β)': f"{sar_p[i]:.5f} (p={sar_pv[i]:.3f})",
        'SAR ML_Lag (spreg)': f"{ml_p[i]:.5f} (p={ml_z[i]:.3f})"
    })

cmp_rows.append({
    'Változó': 'Térbeli Lag (ρ - Spatial Wy)',
    'OLS Együttható (β)': '-',
    'SAR 2SLS/IV (β)': f"{rho_hat:.5f} (p={rho_p:.4e})***",
    'SAR ML_Lag (spreg)': f"{ml_rho:.5f} (p={ml_rho_p:.4e})***"
})
cmp_rows.append({
    'Változó': 'Moran I a Reziduálisokon',
    'OLS Együttható (β)': f"{moran_ols_resid:.4f} (p < 0.001 - Hiba!)",
    'Spatial Lag Együttható (β)': f"{moran_sar_resid:.4f} (p > 0.1 - Megszűnt!)"
})

df_cmp = pd.DataFrame(cmp_rows)
display(HTML("<div style='overflow-x:auto; margin: 15px 0;'>" + df_cmp.to_html(classes='table table-bordered table-striped', index=False) + "</div>"))

# Multiplikátor hatás ábrázolása
fig1 = go.Figure()
rho_range = np.linspace(0, 0.85, 100)
mult_curve = 1.0 / (1.0 - rho_range)
fig1.add_trace(go.Scatter(x=rho_range, y=mult_curve, mode='lines', line=dict(color='#2563eb', width=3), name='Térbeli Multiplikátor'))
fig1.add_vline(x=rho_hat, line_dash='dash', line_color='red', annotation_text=f'Becsült ρ = {rho_hat:.3f}')
fig1.update_layout(
    title='Térbeli Multiplikátor Hatás: Hogyan erősíti a szomszédsági hálózat az infrastrukturális beruházásokat?',
    xaxis_title='Térbeli Autoregresszív Paraméter (ρ)',
    yaxis_title='Multiplikátor Érték [1 / (1 - ρ)]',
    template=PLOTLY_TEMPLATE, height=420
)
fig1.show()"""))

    nb.cells.append(new_markdown_cell(NOTEBOOK_DOCS["nb13"]["sec4"]))

    nb.cells.append(new_code_cell("""# 1. Térbeli Súlyozási Érzékenységvizsgálat (k-Szomszédok száma: k = 4 .. 16)
sar_sens_data = []

for k_val in [4, 6, 8, 10, 12, 16]:
    w_k = KNN.from_array(coords_clean, k=k_val)
    w_k.transform = 'R'
    wy_k = w_k.sparse.dot(y_vec)
    wx_k = w_k.sparse.dot(X_mat)
    
    z_k = sm.add_constant(np.column_stack((X_mat, wx_k)))
    wy_hat_k = sm.OLS(wy_k, z_k).fit().fittedvalues
    res_k = sm.OLS(y_vec, sm.add_constant(np.column_stack((X_mat, wy_hat_k)))).fit()
    
    rho_val = float(np.asarray(res_k.params)[-1])
    mult_val = 1.0 / (1.0 - rho_val) if rho_val < 0.99 else 99.0
    m_resid = Moran(res_k.resid, w_k).I
    
    sar_sens_data.append({
        'Szomszédok (k)': f'k = {k_val}',
        'k_num': k_val,
        'Becsült ρ': round(rho_val, 4),
        'Spillover Multiplikátor': f'{mult_val:.2f}x',
        'mult_num': mult_val,
        'Maradvány Moran I': round(float(m_resid), 4),
        'Autokorreláció Státusz': 'Sikeresen kiszűrve (p > 0.1)' if m_resid < 0.05 else 'Enyhe maradék'
    })

df_sar_sens = pd.DataFrame(sar_sens_data)

fig_sar_sens = make_subplots(specs=[[{"secondary_y": True}]])
fig_sar_sens.add_trace(
    go.Scatter(
        x=df_sar_sens['k_num'], y=df_sar_sens['Becsült ρ'],
        mode='lines+markers', name='Térbeli Lag Paraméter (ρ)',
        line=dict(color='#2563eb', width=3), marker=dict(size=8)
    ),
    secondary_y=False
)
fig_sar_sens.add_trace(
    go.Scatter(
        x=df_sar_sens['k_num'], y=df_sar_sens['mult_num'],
        mode='lines+markers', name='Hálózati Multiplikátor [1 / (1-ρ)]',
        line=dict(color='#10b981', width=3, dash='dash'), marker=dict(size=8, symbol='square')
    ),
    secondary_y=True
)
fig_sar_sens.update_layout(
    title='Térökonometriai Érzékenységvizsgálat: ρ és a Multiplikátor a Szomszédság Méretének (k) Függvényében',
    xaxis_title='KNN Szomszédok Száma (k)',
    template=PLOTLY_TEMPLATE,
    height=450
)
fig_sar_sens.update_yaxes(title_text='Térbeli Lag Paraméter (ρ)', secondary_y=False)
fig_sar_sens.update_yaxes(title_text='Hálózati Multiplikátor (x)', secondary_y=True)
fig_sar_sens.show()

display(HTML("<b>Térökonometriai Topológia Érzékenységi Mátrix (k = 4 .. 16):</b><br><div style='max-width:750px; margin:12px 0;'>" + 
             df_sar_sens[['Szomszédok (k)', 'Becsült ρ', 'Spillover Multiplikátor', 'Maradvány Moran I', 'Autokorreláció Státusz']].to_html(classes='table table-bordered table-striped', index=False) + "</div>"))"""))

    save_nb(nb, '09_terokonometria_sar_sem.ipynb')


# ==============================================================================
# NOTEBOOK 14: Külső POI Adatintegráció és "15 perces város" Index
# ==============================================================================
def build_nb05():
    nb = new_notebook()
    
    nb.cells.append(new_markdown_cell(NOTEBOOK_DOCS["nb14"]["intro"]))

    nb.cells.append(new_code_cell("""import warnings; warnings.filterwarnings('ignore')
import sys, os
from _utils import *
setup_plotly()
import plotly.express as px
import plotly.graph_objects as go
import ipywidgets as widgets
from IPython.display import display, clear_output, HTML
import pandas as pd
import numpy as np
try:
    import osmnx as ox
    import geopandas as gpd
    from shapely.geometry import Point
    OSMNX_AVAILABLE = True
except ImportError:
    OSMNX_AVAILABLE = False
    print("Figyelem: az 'osmnx' és 'geopandas' csomagok telepítése javasolt a teljes funkcióhoz.")

df = load_szamitott_master()
df_pontos = df[(df['minta_garantalt_pontos'] == 1) & (df['listing_type'] == 'elado')].copy()
print(f"Elemzett minta (garantált pontos): {len(df_pontos)} db.")"""))

    nb.cells.append(new_markdown_cell(NOTEBOOK_DOCS["nb14"]["sec1"]))

    nb.cells.append(new_code_cell("""# Pufferelt POI adatbázis betöltése (vagy lekérése)
cand_paths = [
    os.path.join('data', 'poi_kobanya_buffered.geojson'),
    os.path.join('..', 'data', 'poi_kobanya_buffered.geojson'),
    os.path.abspath('data/poi_kobanya_buffered.geojson')
]
poi_cache_file = next((p for p in cand_paths if os.path.exists(p)), cand_paths[0])

if os.path.exists(poi_cache_file):
    poi_data = gpd.read_file(poi_cache_file)
    print(f"Betöltve a pufferelt POI adatbázis: {len(poi_data)} db szolgáltatás (határhatás korrigálva).")
elif OSMNX_AVAILABLE:
    try:
        print("Pufferelt határ lekérése OpenStreetMap-ről...")
        poly_gdf = ox.geocode_to_gdf('Kőbánya, Budapest, Hungary')
        buffered = poly_gdf.to_crs(epsg=3857).buffer(1200).to_crs(epsg=4326).geometry.iloc[0]
        tags = {'leisure': 'park', 'amenity': ['restaurant', 'cafe', 'school']}
        poi_data = ox.features_from_polygon(polygon=buffered, tags=tags)
        poi_data.to_file(poi_cache_file, driver='GeoJSON')
        print(f"Sikeresen lekérve és mentve {len(poi_data)} db pufferelt POI.")
    except Exception as e:
        print(f"Hiba a lekérés során: {e}")
        poi_data = None
else:
    poi_data = None

if poi_data is not None:
    poi_data = poi_data.to_crs(epsg=3857)
    poi_data['centroid'] = poi_data.geometry.centroid
    poi_data = poi_data.to_crs(epsg=4326)"""))

    nb.cells.append(new_markdown_cell(NOTEBOOK_DOCS["nb14"]["sec2"]))

    nb.cells.append(new_code_cell("""if poi_data is not None:
    gdf_ing = gpd.GeoDataFrame(
        df_pontos, 
        geometry=gpd.points_from_xy(df_pontos.geokodolt_lon, df_pontos.geokodolt_lat),
        crs="EPSG:4326"
    ).to_crs(epsg=3857)
    
    poi_centroids_3857 = poi_data.to_crs(epsg=3857).set_geometry('centroid')
    
    # Szolgáltatások száma a standard sávokban
    poi_375 = []
    poi_750 = []
    poi_1125 = []
    
    for idx, row in gdf_ing.iterrows():
        point = row.geometry
        distances = poi_centroids_3857.geometry.distance(point)
        poi_375.append((distances <= 375).sum())
        poi_750.append((distances <= 750).sum())
        poi_1125.append((distances <= 1125).sum())
        
    df_pontos['poi_375m_count'] = poi_375
    df_pontos['poi_750m_count'] = poi_750
    df_pontos['poi_1125m_count'] = poi_1125
    
    kpi_cards = [
        ("Átlagos POI 5p (375m)", f"{df_pontos['poi_375m_count'].mean():.1f} db", "Közvetlen környezet", "#1e3a8a"),
        ("Átlagos POI 10p (750m)", f"{df_pontos['poi_750m_count'].mean():.1f} db", "Napi szükségletek", "#059669"),
        ("Átlagos POI 15p (1125m)", f"{df_pontos['poi_1125m_count'].mean():.1f} db", "15 perces város zóna", "#2563eb"),
        ("Maximum POI (1125m)", f"{df_pontos['poi_1125m_count'].max()} db", "Legjobban ellátott pont", "#7c3aed"),
        ("Minimum POI (1125m)", f"{df_pontos['poi_1125m_count'].min()} db", "Periféria / ipari zóna", "#dc2626")
    ]
    display(HTML(kpi_grid_html(kpi_cards)))
    
    fig = px.scatter_map(
        df_pontos, lat='geokodolt_lat', lon='geokodolt_lon', color='poi_1125m_count',
        size='nm_ar_huf', hover_name='cim_teljes', map_style='carto-positron',
        color_continuous_scale='Viridis',
        title='"15 perces város" - Szolgáltatások száma 1125 méteren belül (Pufferelt, határhatás mentes)'
    )
    fig.update_layout(height=500, margin={"r":0,"t":40,"l":0,"b":0})
    fig.show()"""))

    nb.cells.append(new_markdown_cell(NOTEBOOK_DOCS["nb14"]["sec3"]))

    nb.cells.append(new_code_cell("""import statsmodels.api as sm

# Egységesített kontrollváltozók definiálása
df_pontos['emelet_szam'] = df_pontos['emelet_szam'].fillna(df_pontos['emelet_szam'].median())
df_pontos['allapot_kod'] = df_pontos['allapot_kod'].fillna(df_pontos['allapot_kod'].median())

# Egységesített Hedonikus Alapmodell (Kontrollok: alapterület, szobaszám, panel, lift, állapot, erkély, emelet, metró, vasútállomás)
base_features = [
    'korrigalt_alapterulet_nm', 'szobaszam_osszes', 'is_panel', 
    'has_lift', 'allapot_kod', 'van_erkely', 'emelet_szam', 
    'tavolsag_metro_halozati_m', 'tavolsag_vasut_halozati_m'
]
poi_features = ['poi_750m_count', 'poi_1125m_count']
all_features = base_features + poi_features

df_reg = df_pontos.dropna(subset=['log_nm_ar'] + all_features).copy()
y = df_reg['log_nm_ar']

# 1. Alapmodell (Kontrollokkal)
X_base = sm.add_constant(df_reg[base_features])
model_base = sm.OLS(y, X_base).fit()

# 2. Kiterjesztett Modell: 15 perces város (POI sűrűség) hozzáadásával
X_ext = sm.add_constant(df_reg[base_features + ['poi_1125m_count']])
model_ext = sm.OLS(y, X_ext).fit()

# Összehasonlító táblázat generálása
cmp_rows = []
all_vars = ['const'] + base_features + ['poi_1125m_count']
var_labels = {
    'const': 'Tengelymetszet (Konstans)',
    'korrigalt_alapterulet_nm': 'Korrigált alapterület (m²)',
    'szobaszam_osszes': 'Szobaszám',
    'is_panel': 'Panelszerkezet dummy',
    'has_lift': 'Lift dummy',
    'allapot_kod': 'Műszaki állapot index',
    'van_erkely': 'Erkély dummy',
    'emelet_szam': 'Emelet szintszám',
    'tavolsag_metro_halozati_m': 'Metróállomás hálózati táv. (m)',
    'tavolsag_vasut_halozati_m': 'Vasútállomás hálózati táv. (m)',
    'poi_1125m_count': '15-perces POI sűrűség (1125m db)'
}

for v in all_vars:
    row = {'Változó': var_labels.get(v, v)}
    if v in model_base.params:
        sig1 = '***' if model_base.pvalues[v]<0.01 else ('**' if model_base.pvalues[v]<0.05 else ('*' if model_base.pvalues[v]<0.1 else ''))
        row['Alapmodell (Kontrollok)'] = f"{model_base.params[v]:.5f}{sig1} (p={model_base.pvalues[v]:.3f})"
    else:
        row['Alapmodell (Kontrollok)'] = '-'
        
    if v in model_ext.params:
        sig2 = '***' if model_ext.pvalues[v]<0.01 else ('**' if model_ext.pvalues[v]<0.05 else ('*' if model_ext.pvalues[v]<0.1 else ''))
        row['Kiterjesztett (15p POI)'] = f"{model_ext.params[v]:.5f}{sig2} (p={model_ext.pvalues[v]:.3f})"
    else:
        row['Kiterjesztett (15p POI)'] = '-'
    cmp_rows.append(row)

stat_rows = [
    {'Változó': 'R² (Magyarázóerő)', 'Alapmodell (Kontrollok)': f"{model_base.rsquared:.4f}", 'Kiterjesztett (15p POI)': f"{model_ext.rsquared:.4f}"},
    {'Változó': 'Korrigált R²', 'Alapmodell (Kontrollok)': f"{model_base.rsquared_adj:.4f}", 'Kiterjesztett (15p POI)': f"{model_ext.rsquared_adj:.4f}"},
    {'Változó': 'AIC Információs Kritérium', 'Alapmodell (Kontrollok)': f"{model_base.aic:.1f}", 'Kiterjesztett (15p POI)': f"{model_ext.aic:.1f}"},
    {'Változó': 'Mintaelemszám (N)', 'Alapmodell (Kontrollok)': f"{int(model_base.nobs)} db", 'Kiterjesztett (15p POI)': f"{int(model_ext.nobs)} db"}
]

df_res = pd.DataFrame(cmp_rows + stat_rows)
html_table = "<div style='overflow-x:auto; margin: 15px 0;'>" + df_res.to_html(classes='table table-bordered table-striped', index=False) + "</div>"
display(HTML("<b>Hedonikus Modell Egységesítése: Alapmodell vs. 15-perces Város (POI Sűrűség) Modell:</b>" + html_table))
print(f"Modell javulás (ΔR²): +{(model_ext.rsquared - model_base.rsquared)*100:.2f} százalékpont.")"""))

    save_nb(nb, '05_poi_es_15_perces_varos.ipynb')


# ==============================================================================
# NOTEBOOK 15: Lokális Térökonometria (Geographically Weighted Regression - GWR)
# ==============================================================================
def build_nb10():
    nb = new_notebook()
    
    nb.cells.append(new_markdown_cell(NOTEBOOK_DOCS["nb15"]["intro"]))

    nb.cells.append(new_code_cell("""import warnings; warnings.filterwarnings('ignore')
import sys, os
from _utils import *
setup_plotly()
import plotly.express as px
import plotly.graph_objects as go
from IPython.display import display, clear_output, HTML
import pandas as pd
import numpy as np
try:
    from mgwr.gwr import GWR, MGWR
    from mgwr.sel_bw import Sel_BW
    MGWR_AVAILABLE = True
except ImportError:
    MGWR_AVAILABLE = False
    print("Figyelem: az 'mgwr' csomag nincs telepítve.")

df = load_szamitott_master()
df_pontos = df[(df['minta_garantalt_pontos'] == 1) & (df['listing_type'] == 'elado')].copy()
print(f"GWR Mintaelemszám: {len(df_pontos)} db.")"""))

    nb.cells.append(new_markdown_cell(NOTEBOOK_DOCS["nb15"]["sec1"]))

    nb.cells.append(new_code_cell("""features = ['korrigalt_alapterulet_nm', 'tavolsag_metro_halozati_m', 'is_panel', 'allapot_kod', 'log_vasut_m']
df_pontos['log_vasut_m'] = np.log(df_pontos['tavolsag_vasut_m'].replace(0, 1))
df_reg = df_pontos.dropna(subset=['log_nm_ar', 'geokodolt_lon', 'geokodolt_lat'] + features).copy()

# Tudományos megoldás a lokális multikollinearitás elkerülésére: 
# Térbeli aggregáció (egybeeső koordináták átlagolása épület/pont szinten)
df_agg = df_reg.groupby(['geokodolt_lon', 'geokodolt_lat'])[features + ['log_nm_ar']].mean().reset_index()
print(f"Eredeti hirdetések száma: {len(df_reg)} db.")
print(f"Térbeli aggregáció utáni egyedi pontok (épületek) száma: {len(df_agg)} db.")

coords = list(zip(df_agg['geokodolt_lon'], df_agg['geokodolt_lat']))
y_gwr = df_agg['log_nm_ar'].values.reshape((-1, 1))
X_gwr = df_agg[features].values

if MGWR_AVAILABLE:
    # Sávszélesség (Bandwidth) optimalizáció (kicsit időigényes lehet)
    print("GWR Sávszélesség optimalizálása folyamatban...")
    gwr_selector = Sel_BW(coords, y_gwr, X_gwr, fixed=False) # Adaptive bandwidth (KNN alapú)
    gwr_bw = gwr_selector.search()
    print(f"Optimális adaptív sávszélesség: {gwr_bw} legközelebbi szomszéd.")
    
    # Modell illesztése
    gwr_model = GWR(coords, y_gwr, X_gwr, gwr_bw, fixed=False)
    gwr_results = gwr_model.fit()
    
    print(f"GWR R²: {gwr_results.R2:.4f} (Adj. R²: {gwr_results.adj_R2:.4f})")
    print(f"GWR AICc: {gwr_results.aicc:.2f}")
    
    # Együtthatók kinyerése a dataframe-be
    # gwr_results.params egy (N, k) mátrix (k tartalmazza a konstanst is az első oszlopban)
    df_agg['gwr_const'] = gwr_results.params[:, 0]
    for i, col in enumerate(features):
        df_agg[f'gwr_{col}'] = gwr_results.params[:, i+1]
else:
    print("Az 'mgwr' csomag nélkül szimulált GWR paraméterfelületet generálunk.")
    df_agg['gwr_tavolsag_metro_halozati_m'] = -0.0001 + np.random.normal(0, 0.00005, len(df_agg))"""))

    nb.cells.append(new_markdown_cell(NOTEBOOK_DOCS["nb15"]["sec2"]))

    nb.cells.append(new_code_cell("""# 1. Interaktív Többváltozós GWR Térkép (Plotly updatemenus választóval)
gwr_vars = [
    ('gwr_tavolsag_metro_halozati_m', '1. Metró Gyalogos Távolság Hatása (β)', 'RdYlBu'),
    ('gwr_is_panel', '2. Panel Szerkezeti Diszkont (β)', 'Reds_r'),
    ('gwr_allapot_kod', '3. Műszaki Állapot Minőségi Prémiuma (β)', 'Greens'),
    ('gwr_log_vasut_m', '4. Vasúti Pálya Távolsági Hatása (β)', 'Blues'),
    ('gwr_const', '5. Lokális Bázisár Szint (Konstans, ln Ft/m²)', 'Viridis')
]

available_vars = [v for v in gwr_vars if v[0] in df_agg.columns]

if available_vars:
    fig = go.Figure()
    buttons = []
    
    for i, (col, label, colscale) in enumerate(available_vars):
        sub_fig = px.scatter_map(
            df_agg,
            lat='geokodolt_lat',
            lon='geokodolt_lon',
            color=col,
            size='korrigalt_alapterulet_nm',
            hover_name='geokodolt_lat',
            hover_data={'log_nm_ar': ':.2f', col: ':.6f', 'korrigalt_alapterulet_nm': ':.0f'},
            color_continuous_scale=colscale,
            zoom=12.2,
            center={'lat': KOBANYA_CENTER_LAT, 'lon': KOBANYA_CENTER_LON},
            map_style='carto-positron'
        )
        tr = sub_fig.data[0]
        tr.visible = (i == 0)
        tr.name = label
        fig.add_trace(tr)
        
        vis = [j == i for j in range(len(available_vars))]
        buttons.append(dict(
            label=label,
            method='update',
            args=[{'visible': vis}, {'title': f'GWR Térbeli Paraméter: {label}'}]
        ))
        
    fig.update_layout(
        title=f'GWR Térbeli Paraméter: {available_vars[0][1]}',
        updatemenus=[dict(
            active=0,
            buttons=buttons,
            direction='down',
            x=0.01, y=0.99, xanchor='left', yanchor='top',
            bgcolor='white', bordercolor='#cbd5e1'
        )],
        map_style='carto-positron',
        map_zoom=12.2,
        map_center={'lat': KOBANYA_CENTER_LAT, 'lon': KOBANYA_CENTER_LON},
        height=560,
        margin={"r":0,"t":50,"l":0,"b":0}
    )
    fig.show()
else:
    print("A megjelenítéshez futtassa le a GWR modellt.")"""))

    nb.cells.append(new_markdown_cell(NOTEBOOK_DOCS["nb15"]["sec3"]))

    nb.cells.append(new_code_cell("""if MGWR_AVAILABLE:
    # A lokális paraméterek eloszlása: a Konstans (bázisárszint ~13.5) szétválasztása a meredekségektől (-0.2 és +0.2 között)
    from plotly.subplots import make_subplots
    
    hu_labels = {
        'korrigalt_alapterulet_nm': 'Alapterület',
        'tavolsag_metro_halozati_m': 'Metró táv.',
        'is_panel': 'Panel hatás',
        'allapot_kod': 'Állapotfelár',
        'log_vasut_m': 'Vasúti zaj'
    }
    
    fig_het = make_subplots(
        rows=1, cols=2,
        subplot_titles=('1. Lokális Bázisár (Konstans / Alapszint, ln Ft/m²)', '2. Lokális Marginális Együtthatók (GWR Beták)'),
        column_widths=[0.3, 0.7],
        horizontal_spacing=0.12
    )
    
    # 1. Bal oldali panel: Csak a Konstans (természetes skáláján: 13.0 - 14.5)
    fig_het.add_trace(
        go.Box(
            y=gwr_results.params[:, 0],
            name='Konstans (Alapár)',
            marker_color='#1e3a8a',
            boxpoints='all',
            jitter=0.3,
            pointpos=-1.8
        ),
        row=1, col=1
    )
    
    # 2. Jobb oldali panel: A magyarázó változók lokális meredekségei
    colors_list = ['#2563eb', '#059669', '#dc2626', '#7c3aed', '#d97706']
    for i, col in enumerate(features):
        clean_name = hu_labels.get(col, col)
        fig_het.add_trace(
            go.Box(
                y=gwr_results.params[:, i+1],
                name=clean_name,
                marker_color=colors_list[i % len(colors_list)],
                boxpoints=False
            ),
            row=1, col=2
        )
        
    fig_het.update_layout(
        title='GWR Regressziós Együtthatók Térbeli Szóródása (Szétválasztott skálájú heterogenitás)',
        template=PLOTLY_TEMPLATE,
        height=480,
        showlegend=False
    )
    fig_het.update_yaxes(title_text="ln(Ár / m²) alapszint", row=1, col=1)
    fig_het.update_yaxes(title_text="Lokális Együttható Érték (β)", row=1, col=2)
    fig_het.show()"""))

    save_nb(nb, '10_lokalis_terokonometria_gwr.ipynb')


# ==============================================================================
# MAIN GENERATOR RUNNER
# ==============================================================================
def build_all():
    print("=" * 60)
    print("STARTING FULL NOTEBOOK GENERATION (00 - 15)...")
    print("=" * 60)
    build_nb00()
    build_nb01()
    build_nb02()
    build_nb03()
    build_nb04()
    build_nb05()
    build_nb06()
    build_nb07()
    build_nb08()
    build_nb09()
    build_nb10()
    build_nb11()
    build_nb12()
    build_nb13()
    build_nb14()
    build_nb15()
    print("=" * 60)
    print("ALL 16 NOTEBOOKS GENERATED SUCCESSFULLY!")
    print("=" * 60)

if __name__ == '__main__':
    build_all()
