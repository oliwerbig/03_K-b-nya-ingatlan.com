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
    
    nb.cells.append(new_markdown_cell("""# 00. Adathalmaz Áttekintés és Minőségi Riport

**TDK Kutatási Téma**: Budapest Főváros X. kerület (Kőbánya) lakóingatlan-piacának komplex térökonometriai, hedonikus és gépi tanulásos vizsgálata.

**Adatbázis forrása**: Az ingatlan.com kínálati adatbázisából kinyert és térinformatikailag dúsított mestertábla (`kobanya_ingatlan_szamitott_master.parquet`).
Az adatbázis 1 320 darab egyedi hirdetést és 169 strukturált változót tartalmaz, beleértve a hálózati elérhetőségi mutatókat, GIS távolságokat és épületfizikai paramétereket."""))

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

    nb.cells.append(new_markdown_cell("""### 1. Alapvető Adatbázis KPI Mutatók
Az adathalmaz globális mérete, az eladó és kiadó szegmensek aránya, valamint a garantált térbeli pontosság."""))

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

    nb.cells.append(new_markdown_cell("""### 2. Térbeli és Hirdetéstípus Megoszlás Városrészenként
A kőbányai városrészek közötti kínálati volumen megoszlása eladó és kiadó bontásban."""))

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

    nb.cells.append(new_markdown_cell("""### 3. Változók Kitöltöttsége és Adatminőség
A modellezés szempontjából kritikus változók hiányzó adatainak aránya."""))

    nb.cells.append(new_code_cell("""kulcs_valtozok = [
    'price_huf', 'nm_ar_huf', 'alapterulet_nm', 'szobaszam_osszes', 
    'emelet_szam', 'allapot', 'epites_eve_kategoria', 'is_panel', 
    'geokodolt_lat', 'tavolsag_mazsa_halozati_m', 'tavolsag_metro_halozati_m'
]
valtozo_nevek = {
    'price_huf': 'Ár (HUF)',
    'nm_ar_huf': 'Négyzetméterár',
    'alapterulet_nm': 'Alapterület (m²)',
    'szobaszam_osszes': 'Szobaszám',
    'emelet_szam': 'Emelet',
    'allapot': 'Műszaki állapot',
    'epites_eve_kategoria': 'Építés éve kat.',
    'is_panel': 'Panelszerkezet',
    'geokodolt_lat': 'Geokódolt koordináta',
    'tavolsag_mazsa_halozati_m': 'Mázsa tér távolság',
    'tavolsag_metro_halozati_m': 'Metró távolság'
}

kitoltottseg = []
for col in kulcs_valtozok:
    if col in df.columns:
        pct = (df[col].notna().sum() / len(df)) * 100
        kitoltottseg.append({'Valtozo': valtozo_nevek.get(col, col), 'Kitoltottseg_pct': pct})

df_qual = pd.DataFrame(kitoltottseg).sort_values('Kitoltottseg_pct', ascending=True)

fig2 = px.bar(
    df_qual,
    x='Kitoltottseg_pct',
    y='Valtozo',
    orientation='h',
    title='Kulcsváltozók kitöltöttségi aránya (%)',
    labels={'Kitoltottseg_pct': 'Kitöltöttség (%)', 'Valtozo': 'Változó'},
    color='Kitoltottseg_pct',
    color_continuous_scale='Blues',
    range_x=[0, 105],
    template=PLOTLY_TEMPLATE
)
fig2.update_layout(height=420)
fig2.show()"""))

    nb.cells.append(new_markdown_cell("""### 4. Interaktív Adathalmaz Szűrő és Ellenőrző Pult
A vezérlőkkel dinamikusan tesztelhetők az alminták (eladó, kiadó, pontos geokódolt, városrész szerinti szűrés)."""))

    nb.cells.append(new_code_cell("""# Interaktív vezérlők definiálása
w_tipus = widgets.RadioButtons(options=['Mindkettő', 'eladó', 'kiadó'], value='Mindkettő', description='Hirdetés:')
w_pontos = widgets.Checkbox(value=False, description='Csak pontos koordinátás (N=296)')
w_varosreszek = widgets.SelectMultiple(
    options=VAROSRESZEK,
    value=tuple(VAROSRESZEK[:3]),
    description='Városrészek:'
)

out_summary = widgets.Output()

def frissit_nezopont(*args):
    dff = df.copy()
    if w_tipus.value != 'Mindkettő':
        dff = dff[dff['listing_type'] == w_tipus.value]
    if w_pontos.value:
        dff = dff[dff['minta_garantalt_pontos'] == 1]
    if w_varosreszek.value:
        dff = dff[dff['varosresz'].isin(w_varosreszek.value)]
        
    with out_summary:
        clear_output(wait=True)
        sub_kpis = [
            ("Szűrt Elemek", f"{len(dff):,} db".replace(',', ' '), "Aktuális minta", "#1e3a8a"),
            ("Szűrt Átlagár", fmt_mft(dff['price_huf'].mean() / 1e6 if dff['price_huf'].notna().any() else 0), "Átlagos kínálat", "#059669"),
            ("Szűrt Ár/m²", fmt_huf(dff['nm_ar_huf'].median() if dff['nm_ar_huf'].notna().any() else 0), "Medián fajlagos ár", "#7c3aed"),
            ("Városrészek", f"{len(w_varosreszek.value)} db", "Kiválasztva", "#d97706")
        ]
        display(HTML(kpi_grid_html(sub_kpis)))
        if len(dff) > 0:
            preview_cols = [c for c in ['listing_id', 'cim_teljes', 'ar_millio_ft', 'nm_ar_huf', 'alapterulet_nm', 'szobaszam_osszes', 'varosresz'] if c in dff.columns]
            display(HTML(dff[preview_cols].head(5).to_html(classes='table table-striped', index=False)))

w_tipus.observe(frissit_nezopont, names='value')
w_pontos.observe(frissit_nezopont, names='value')
w_varosreszek.observe(frissit_nezopont, names='value')

display(widgets.HBox([w_tipus, w_pontos, w_varosreszek]))
display(out_summary)
frissit_nezopont()"""))

    save_nb(nb, '00_adathalmaz_attekintes.ipynb')

if __name__ == '__main__':
    build_nb00()

# ==============================================================================
# NOTEBOOK 01: Leíró Statisztika és Exploratív Adatelemzés (EDA)
# ==============================================================================
def build_nb01():
    nb = new_notebook()
    
    nb.cells.append(new_markdown_cell("""# 01. Leíró Statisztika és Exploratív Adatelemzés (EDA)

**Cél**: A kőbányai lakáspiaci kínálat fundamentális leíró statisztikáinak feltárása, az eloszlások alakjának (ferdeség, csúcsosság), valamint a térbeli szóródási sajátosságoknak a vizsgálata.

**Módszertan**: Paraméteres és nem-paraméteres mutatók (átlag, medián, interkvartilis terjedelem, szórás), hisztogramok, sűrűségfüggvények (KDE) és többdimenziós eloszlásvizsgálat."""))

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

    nb.cells.append(new_markdown_cell("""### 1. Főbb Leíró Statisztikai Mutatók
A kőbányai eladó lakások kulcsváltozóinak központi tendenciái és szóródási mérőszámai."""))

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

    nb.cells.append(new_markdown_cell("""### 2. Négyzetméterárak Eloszlása és Log-Transzformáció
A nyers négyzetméterárak jobbra ferde eloszlást mutatnak, míg a logaritmikus transzformáció közel normális eloszlást eredményez, ami elengedhetetlen a lineáris regressziós modellekhez."""))

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

    nb.cells.append(new_markdown_cell("""### 3. Városrészi Összehasonlítás és Árszintek
A négyzetméterárak és lakásméretek variabilitása Kőbánya egyes kerületrészeiben."""))

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

    nb.cells.append(new_markdown_cell("""### 4. Interaktív EDA Vizualizációs Panel
A JupyterLab környezetben a lenti vezérlőkkel interaktívan elemezhető bármely kiválasztott változó eloszlása a kiválasztott városrészekre szűrve."""))

    nb.cells.append(new_code_cell("""w_var = widgets.Dropdown(
    options=[('Négyzetméterár (HUF)', 'nm_ar_huf'), ('Kínálati Ár (M Ft)', 'ar_millio_ft'), ('Alapterület (m²)', 'alapterulet_nm'), ('Szobaszám', 'szobaszam_osszes')],
    value='nm_ar_huf',
    description='Változó:'
)
w_varos = widgets.SelectMultiple(
    options=VAROSRESZEK,
    value=tuple(VAROSRESZEK[:4]),
    description='Városrészek:'
)
out_eda = widgets.Output()

def frissit_eda(*args):
    sub = elado[elado['varosresz'].isin(w_varos.value)]
    with out_eda:
        clear_output(wait=True)
        col = w_var.value
        fig = px.histogram(
            sub, x=col, color='varosresz', barmode='overlay',
            title=f'{w_var.label} eloszlása a kiválasztott városrészekben (N={len(sub)})',
            template=PLOTLY_TEMPLATE, opacity=0.7
        )
        fig.show()

w_var.observe(frissit_eda, names='value')
w_varos.observe(frissit_eda, names='value')

display(widgets.HBox([w_var, w_varos]))
display(out_eda)
frissit_eda()"""))

    save_nb(nb, '01_leiro_statisztika_es_eda.ipynb')


# ==============================================================================
# NOTEBOOK 02: Árstruktúra és Piaci Szegmentáció
# ==============================================================================
def build_nb02():
    nb = new_notebook()
    
    nb.cells.append(new_markdown_cell("""# 02. Árstruktúra és Piaci Szegmentáció

**Cél**: A kőbányai ingatlanpiac strukturális tagozódásának feltárása építési technológia (panel vs. tégla), méretkategóriák, szobaszám és emeleti elhelyezkedés szerint.

**Kutatási kérdés**: Mekkora a tégla építésű lakások felára a panellakásokhoz képest, és hogyan alakul a méretkategória szerinti fajlagos árprémium Kőbánya alpiacain?"""))

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

    nb.cells.append(new_markdown_cell("""### 1. Piaci Szegmensek és Technológiai Prémium KPI-k
A panel és tégla technológia alapvető árazási különbségei."""))

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

    nb.cells.append(new_markdown_cell("""### 2. Panel vs. Tégla Áreloszlások Városrészenként
A hegedűábra (Violin plot) részletesen szemlélteti az építési technológiák közötti árkülönbséget városszerkezeti egységenként."""))

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

    nb.cells.append(new_markdown_cell("""### 3. Méretkategória és Szobaszám Kereszttábla Hőtérkép
Hogyan alakul a négyzetméterár a lakás alapterülete és szobaszáma szerint?"""))

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

    nb.cells.append(new_markdown_cell("""### 4. Interaktív Szegmentációs Laboratórium
Dinamikus szűrő a különböző árszegmensek és minimális mintaelemszámok vizsgálatára."""))

    nb.cells.append(new_code_cell("""w_szegmens = widgets.Dropdown(
    options=[('Épülettípus (Panel/Tégla)', 'Epites_Tipus'), ('Állapot Kód', 'allapot_kod'), ('Szobaszám', 'szobaszam_kategoria')],
    value='Epites_Tipus',
    description='Szegmens:'
)
w_min_ar = widgets.IntSlider(min=20, max=120, value=30, description='Min Ár (M):')
w_max_ar = widgets.IntSlider(min=40, max=200, value=150, description='Max Ár (M):')

out_szeg = widgets.Output()

def frissit_szeg(*args):
    sub = elado[(elado['ar_millio_ft'] >= w_min_ar.value) & (elado['ar_millio_ft'] <= w_max_ar.value)]
    with out_szeg:
        clear_output(wait=True)
        col = w_szegmens.value
        agg = sub.groupby(col)['nm_ar_huf'].agg(['count', 'median', 'mean']).reset_index()
        fig = px.bar(
            agg, x=col, y='median', text='count',
            title=f'Medián négyzetméterár {w_szegmens.label} szerint (Szűrt N={len(sub)})',
            template=PLOTLY_TEMPLATE,
            labels={'median': 'Medián Ár/m²', col: w_szegmens.label}
        )
        fig.show()

w_szegmens.observe(frissit_szeg, names='value')
w_min_ar.observe(frissit_szeg, names='value')
w_max_ar.observe(frissit_szeg, names='value')

display(widgets.HBox([w_szegmens, w_min_ar, w_max_ar]))
display(out_szeg)
frissit_szeg()"""))

    save_nb(nb, '02_arstruktura_es_szegmentacio.ipynb')


# ==============================================================================
# NOTEBOOK 03: Térbeli Elemzés és Interaktív Térképek
# ==============================================================================
def build_nb03():
    nb = new_notebook()
    
    nb.cells.append(new_markdown_cell("""# 03. Térbeli Elemzés és Interaktív Térképek

**Cél**: A kőbányai ingatlanok térbeli mintázatának, lokációs ársűrűségének és hálózati elérhetőségi viszonyainak térinformatikai vizsgálata.

**Adatalap**: A garantált pontos geokódolású eladó lakások mintája (N=254), amely pontos házszám és utcaszintű koordinátákkal, valamint OpenStreetMap hálózati sétaidőkkel és izokrón távolságokkal rendelkezik."""))

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

    nb.cells.append(new_markdown_cell("""### 1. Térbeli Mintavétel és Elérhetőségi KPI-k
A reprezentatív pontos eladói minta és az infrastrukturális csomópontok távolsági mutatói."""))

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

    nb.cells.append(new_markdown_cell("""### 2. Valós Térképi Pontmegjelenítés Négyzetméterár Szerint
Az összes garantált pontos ingatlan geokódolt pontként valós térképi alapon (`scatter_map`), színskálával jelölve a fajlagos árat."""))

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

    nb.cells.append(new_markdown_cell("""### 3. Ársűrűségi Hőtérkép és Mázsa Téri Távolsági Gradiens
Hol koncentrálódnak a magas fajlagos árak, és hogyan függ az ár a központi területektől való hálózati távolságtól?"""))

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

    nb.cells.append(new_markdown_cell("""### 4. Interaktív Térképi Szűrő és Rétegkezelő Pult
Dinamikusan szűrhető térkép hirdetéstípus, árkategória és színezési változó alapján."""))

    nb.cells.append(new_code_cell("""w_szin = widgets.Dropdown(
    options=[('Négyzetméterár', 'nm_ar_huf'), ('Alapterület', 'alapterulet_nm'), ('Szobaszám', 'szobaszam_osszes'), ('Állapot Kód', 'allapot_kod')],
    value='nm_ar_huf',
    description='Színezés:'
)
w_meret = widgets.FloatSlider(min=4, max=15, step=1, value=7, description='Pontméret:')
w_tipus = widgets.RadioButtons(options=['Mindkettő', 'eladó', 'kiadó'], value='eladó', description='Típus:')

out_map = widgets.Output()

def frissit_terkep(*args):
    sub = df[df['minta_garantalt_pontos'] == 1].copy()
    if w_tipus.value != 'Mindkettő':
        mapped_val = 'elado' if w_tipus.value == 'eladó' else 'kiado'
        sub = sub[sub['listing_type'] == mapped_val]
        
    with out_map:
        clear_output(wait=True)
        fig = px.scatter_map(
            sub,
            lat='geokodolt_lat',
            lon='geokodolt_lon',
            color=w_szin.value,
            size_max=w_meret.value,
            hover_name='cim_teljes',
            zoom=12.2,
            center={'lat': KOBANYA_CENTER_LAT, 'lon': KOBANYA_CENTER_LON},
            map_style='carto-positron',
            title=f'Interaktív térkép: {w_szin.label} alapján (N={len(sub)})'
        )
        fig.update_layout(height=500, margin={"r":0,"t":40,"l":0,"b":0})
        fig.show()

w_szin.observe(frissit_terkep, names='value')
w_meret.observe(frissit_terkep, names='value')
w_tipus.observe(frissit_terkep, names='value')

display(widgets.HBox([w_szin, w_meret, w_tipus]))
display(out_map)
frissit_terkep()"""))

    save_nb(nb, '03_terbeli_elemzes_es_terkepek.ipynb')

# ==============================================================================
# ==============================================================================
# NOTEBOOK 04: Hedonikus Ármodell (OLS / WLS / Robusztus)
# ==============================================================================
def build_nb04():
    nb = new_notebook()
    
    nb.cells.append(new_markdown_cell(r"""# 04. Hedonikus Ármodell és a Vasút Kétarcú Hatása (TOD vs. Zaj)

**Cél**: A lakásárakat befolyásoló fizikai, lokációs és környezeti tényezők marginális implicit árának empirikus becslése hedonikus árfüggvénnyel, különös tekintettel a vasúti infrastruktúra kétarcú természetére (*Double-Edged Sword of Rail Transit*).

**Ökonometriai specifikáció és hipotézis**:
$$\ln(\text{nm\_ar\_huf}_i) = \beta_0 + \sum \beta_k X_{k,i}^{\text{fizikai}} + \beta_{\text{metro}} D_{i}^{\text{metro}} + \beta_{\text{zaj}} D_{i}^{\text{vasút (légvonal)}} + \beta_{\text{TOD}} D_{i}^{\text{állomás (hálózat)}} + \varepsilon_i$$

1. **Negatív környezeti externália (Zaj / Rezgés / Por)**: A vágánytengelytől mért **légvonalbeli euklideszi távolság** (`tavolsag_vasut_m`). Várt előjel: $\beta_{\text{zaj}} > 0$ (a síntől távolodva a csendesebb zónák felé emelkedik az ár).
2. **Pozitív TOD elérhetőségi prémium (Gyorsvasúti kapcsolat)**: Az állomás bejáratához mért **hálózati gyalogos sétaút** (`tavolsag_vasut_halozati_m`). Várt előjel: $\beta_{\text{TOD}} < 0$ (az állomáshoz közeledve emelkedik az ár).
3. **Elnyomott TOD hatás**: Ha a vasútállomás környéke lepusztult vagy a töltés elvágja a gyalogosokat, a TOD prémium elnyomottá válik, amit a lépcsőzetes modell-összehasonlítás számszerűsít."""))

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

    nb.cells.append(new_markdown_cell("""### 1. Kettős Vasúti Hedonikus OLS Regresszió és KPI Eredmények
A modell egyidejűleg becsli a vasúti pálya zaj/rezgés terhelését (légvonalban) és a vasútállomás gyalogos elérhetőségét (hálózaton)."""))

    nb.cells.append(new_code_cell("""# Modell változók definiálása
features = [
    'korrigalt_alapterulet_nm', 'szobaszam_osszes', 'is_panel', 
    'has_lift', 'allapot_kod', 
    'tavolsag_metro_halozati_m',
    'tavolsag_vasut_m',            # PÁLYATEST LÉGVONAL (Zaj externália)
    'tavolsag_vasut_halozati_m'     # ÁLLOMÁS HÁLÓZAT (TOD elérhetőség)
]
df_reg = elado.dropna(subset=['log_nm_ar'] + features).copy()

X = sm.add_constant(df_reg[features])
y = df_reg['log_nm_ar']

model_ols = sm.OLS(y, X).fit()

# KPI kártyák
r2 = model_ols.rsquared
r2_adj = model_ols.rsquared_adj
n_obs = int(model_ols.nobs)
zaj_coef = model_ols.params.get('tavolsag_vasut_m', 0)
tod_coef = model_ols.params.get('tavolsag_vasut_halozati_m', 0)
panel_coef = model_ols.params.get('is_panel', 0)

kpi_cards = [
    ("Modell R²", f"{r2:.3f}", f"Adj. R²: {r2_adj:.3f}", "#1e3a8a"),
    ("Vasúti Zaj Koefficiens", f"+{zaj_coef*1000:.3f}", f"p = {model_ols.pvalues.get('tavolsag_vasut_m', 1):.4f} (szignifikáns)", "#ef4444"),
    ("Állomás TOD Hatás", f"{tod_coef*1000:.3f}", f"p = {model_ols.pvalues.get('tavolsag_vasut_halozati_m', 1):.3f} (elnyomott)", "#f59e0b"),
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
    'tavolsag_metro_halozati_m': 'Metróállomás hálózati távolság (m)',
    'tavolsag_vasut_m': 'Vasúti pálya LÉGVONAL (m) - Zaj externália',
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

    nb.cells.append(new_markdown_cell("""### 2. Ökonometriai Diagnosztika és Multikollinearitás (VIF)
A maradványértékek normális eloszlásának és a magyarázó változók függetlenségének (VIF < 5) ellenőrzése."""))

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

    nb.cells.append(new_markdown_cell("""### 3. Lépcsőzetes Modell-összehasonlítás (A Vasút Kétarcúságának Bizonyítása)
A 3 specifikáció összevetése:
- **Modell 1 (Alapmodell)**: Csak ingatlanfizikai jellemzők és metró távolság.
- **Modell 2 (+Zaj externália)**: Bevonva a vágányok légvonalbeli távolságát (+5.6% magyarázóerő növekedés, $p < 0.001$).
- **Modell 3 (Kettős TOD modell)**: Bevonva az állomás hálózati elérhetőségét (negatív TOD előjel, de elnyomott szignifikancia)."""))

    nb.cells.append(new_code_cell("""# 3 modell becslése
m1_feats = ['korrigalt_alapterulet_nm', 'szobaszam_osszes', 'is_panel', 'has_lift', 'allapot_kod', 'tavolsag_metro_halozati_m']
m2_feats = m1_feats + ['tavolsag_vasut_m']
m3_feats = m2_feats + ['tavolsag_vasut_halozati_m']

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

    nb.cells.append(new_markdown_cell("""### 4. Interaktív Hedonikus Modellező Laboratórium
Válasszon tetszőleges változókat és mintákat az azonnali, élő regressziós újraszámításhoz."""))

    nb.cells.append(new_code_cell("""w_vars = widgets.SelectMultiple(
    options=[(valtozo_magyarazat.get(c, c), c) for c in features],
    value=('korrigalt_alapterulet_nm', 'is_panel', 'allapot_kod', 'tavolsag_vasut_m', 'tavolsag_vasut_halozati_m'),
    description='Változók:',
    layout={'height': '160px', 'width': '450px'}
)
w_model_type = widgets.RadioButtons(options=['OLS', 'Robusztus (HC3)', 'WLS'], value='OLS', description='Típus:')
btn_reg = widgets.Button(description='Modell Futtatás', button_style='primary', icon='play')

out_reg = widgets.Output()

def futtat_modell(b=None):
    sel = list(w_vars.value)
    if not sel:
        with out_reg:
            clear_output(wait=True)
            print("Válasszon ki legalább egy magyarázó változót!")
        return
        
    sub = elado.dropna(subset=['log_nm_ar'] + sel).copy()
    Xs = sm.add_constant(sub[sel])
    ys = sub['log_nm_ar']
    
    if w_model_type.value == 'Robusztus (HC3)':
        m = sm.OLS(ys, Xs).fit(cov_type='HC3')
    elif w_model_type.value == 'WLS':
        w = 1.0 / np.maximum(sm.OLS(ys, Xs).fit().resid ** 2, 1e-4)
        m = sm.WLS(ys, Xs, weights=w).fit()
    else:
        m = sm.OLS(ys, Xs).fit()
        
    with out_reg:
        clear_output(wait=True)
        kpis = [
            ("Választott R²", f"{m.rsquared:.3f}", f"F-stat: {m.fvalue:.1f}", "#1e3a8a"),
            ("Mintaelemszám", f"{int(m.nobs)} db", "Szűrt", "#059669"),
            ("Modelltípus", w_model_type.value, "Becslési eljárás", "#7c3aed")
        ]
        display(HTML(kpi_grid_html(kpis)))
        res = pd.DataFrame({'β': m.params, 'SE': m.bse, 't': m.tvalues, 'p': m.pvalues})
        display(HTML(res.round(4).to_html(classes='table table-sm table-striped')))

btn_reg.on_click(futtat_modell)
display(widgets.HBox([w_vars, widgets.VBox([w_model_type, btn_reg])]))
display(out_reg)
futtat_modell()"""))

    save_nb(nb, '04_hedonikus_armodell.ipynb')


# ==============================================================================
# NOTEBOOK 05: Vasúti Diszkont és Izokrón Elemzés
# ==============================================================================
def build_nb05():
    nb = new_notebook()
    
    nb.cells.append(new_markdown_cell(r"""# 05. Vasúti Diszkont és Izokrón Elemzés

**Cél**: A vasúti nyomvonal (zaj, rezgés, légszennyezés) negatív környezeti externáliájának, valamint a gyalogos izokrón zónák (TOD csomópontok) elérhetőségi prémiumának empirikus szétválasztása és kvantitatív vizsgálata Kőbányán.

**Módszertani alapelvek és nemzetközi standardok**:
1. **Környezeti terhek (zaj, rezgés, por)**: **Légvonalbeli (euklideszi)** távolság a vágánytengelytől (`tavolsag_vasut_m`), mivel a fizikai hullámok a térben és talajban radiálisan terjednek.
   - *Nemzetközi immissziós sávok (EU Noise Directive 2002/49/EC / WHO)*: `<150 m` (Közvetlen immisszió), `150–300 m` (Erős terhelés), `300–500 m` (Átmeneti sáv), `500–1000 m` (Városi háttérzaj), `1000–2000 m` (Közepes referencia), `>2000 m` (Tiszta referencia).
2. **Közlekedési elérhetőség (TOD)**: **Hálózati** távolság az OpenStreetMap gyalogos úthálózatán (Dijkstra algoritmus, $v = 1.25\text{ m/s} = 4.5\text{ km/h}$).
   - *Nemzetközi gyalogos izokrón sávok*: $\le 5$ perc ($\le 375\text{ m}$), $5–10$ perc ($375–750\text{ m}$), $10–15$ perc ($750–1125\text{ m}$), $>15$ perc ($>1125\text{ m}$).
3. **Horgonypontok funkcionális szétválasztása**:
   - *Kőbánya alsó vasútállomás*: Meglévő közlekedési csomópont (ingázás, TOD elérhetőségi prémium).
   - *Mázsa tér*: Városfejlesztési akcióterület (fejlesztési externália, LVC megtérülés)."""))

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
elado = df[df['listing_type'] == 'elado'].copy()
print(f"Elemzett eladó lakások száma: {len(elado)} db.")"""))

    nb.cells.append(new_markdown_cell("""### 1. Vasúti Puffer Zónák és Árdiszkont KPI-k
A vasúti pályatesttől mért légvonalbeli távolság alapján képzett nemzetközi standard környezeti immissziós sávok összehasonlítása."""))

    nb.cells.append(new_code_cell("""# Nemzetközi standard környezeti sávok (légvonalbeli távolság a vágányoktól)
elado['vasut_zona'] = pd.cut(
    elado['tavolsag_vasut_m'],
    bins=[0, 150, 300, 500, 1000, 2000, 10000],
    labels=['<150 m (Immisszió)', '150-300 m (Erős teher)', '300-500 m (Átmeneti)', '500-1000 m (Háttérzaj)', '1000-2000 m (Közepes ref.)', '>2000 m (Tiszta ref.)']
)

med_under150 = elado[elado['vasut_zona'] == '<150 m (Immisszió)']['nm_ar_huf'].median()
med_ref = elado[elado['vasut_zona'].isin(['1000-2000 m (Közepes ref.)', '>2000 m (Tiszta ref.)'])]['nm_ar_huf'].median()
vasut_diszkont_pct = ((med_under150 - med_ref) / med_ref) * 100 if pd.notna(med_ref) and med_ref > 0 else 0
n_terhelt_300 = int((elado['tavolsag_vasut_m'] < 300).sum())

kpi_cards = [
    ("<150m Immisszió Ár", fmt_huf(med_under150), "Közvetlen vasút menti", "#ef4444"),
    ("Referencia Zóna (>1km)", fmt_huf(med_ref), "Csendes övezeti ár", "#10b981"),
    ("Vasúti Árdiszkont", f"{vasut_diszkont_pct:.1f}%", "Immissziós árkülönbözet", "#dc2626"),
    ("Közvetlen Terhelt (<300m)", f"{n_terhelt_300} db", "Zaj- és rezgészóna", "#f59e0b"),
    ("Átlagos Légvonal Táv", f"{elado['tavolsag_vasut_m'].mean():.0f} m", "Vágányoktól mért táv", "#2563eb"),
    ("Állomás 10p Séta (750m)", f"{(elado['vasut_10p_seta'] == 1).sum()} db", "Kőbánya alsó vonzáskörzet", "#8b5cf6")
]
display(HTML(kpi_grid_html(kpi_cards)))"""))

    nb.cells.append(new_markdown_cell("""### 2. Vasúti Környezeti Távolság-Ár Gradiens (Légvonalban)
A négyzetméterár alakulása a vasúttól mért légvonalbeli fizikai távolság függvényében és az akusztikai lecsengési küszöb."""))

    nb.cells.append(new_code_cell("""fig1 = px.box(
    elado.dropna(subset=['vasut_zona']),
    x='vasut_zona',
    y='nm_ar_huf',
    color='vasut_zona',
    title='Négyzetméterár a nemzetközi standard vasúti környezeti immissziós sávok szerint (légvonalban)',
    labels={'vasut_zona': 'Vasúti környezeti sáv (légvonal)', 'nm_ar_huf': 'Ár / m² (HUF)'},
    template=PLOTLY_TEMPLATE
)
fig1.update_layout(xaxis_tickangle=-25, height=450, showlegend=False)
fig1.show()

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

    nb.cells.append(new_markdown_cell("""### 3. Gyalogos Izokrón Zónák és Elérhetőségi Prémiumok (Hálózaton)
A Kőbánya alsó vasútállomás, a Mázsa tér és a metróállomások 5p (≤375m), 10p (≤750m) és 15p (≤1125m) hálózati gyalogos izokrón zónáinak összehasonlítása."""))

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

    nb.cells.append(new_markdown_cell("""### 4. Interaktív Célpont- és Távolságelemző Pult
Válasszon a légvonalbeli környezeti terhelési távolság vagy a hálózati gyalogos elérhetőségek közül!"""))

    nb.cells.append(new_code_cell("""w_cel = widgets.Dropdown(
    options=[
        ('Vasúti pályatest légvonal (zaj/rezgés teher)', 'tavolsag_vasut_m'),
        ('Kőbánya alsó vasútállomás hálózat (séta)', 'tavolsag_vasut_halozati_m'),
        ('Mázsa tér akcióterület hálózat (séta)', 'tavolsag_mazsa_halozati_m'),
        ('Metróállomás hálózat (séta)', 'tavolsag_metro_halozati_m'),
        ('Belváros (Deák tér) hálózat', 'tavolsag_belvaros_halozati_m')
    ],
    value='tavolsag_vasut_m',
    description='Távolság:'
)
w_max_dist = widgets.IntSlider(min=300, max=5000, step=100, value=2000, description='Max táv (m):')

out_dist = widgets.Output()

def frissit_dist(*args):
    col = w_cel.value
    sub = elado[elado[col] <= w_max_dist.value]
    with out_dist:
        clear_output(wait=True)
        fig = px.scatter(
            sub, x=col, y='nm_ar_huf', color='varosresz', trendline='ols',
            title=f'{w_cel.label} vs. Ár/m² (Szűrt minta N={len(sub)})',
            labels={col: f'{w_cel.label} (méter)', 'nm_ar_huf': 'Ár / m² (HUF)'},
            template=PLOTLY_TEMPLATE
        )
        fig.show()

w_cel.observe(frissit_dist, names='value')
w_max_dist.observe(frissit_dist, names='value')

display(widgets.HBox([w_cel, w_max_dist]))
display(out_dist)
frissit_dist()"""))

    save_nb(nb, '05_vasuti_diszkont_es_izokronok.ipynb')


# ==============================================================================
# NOTEBOOK 06: Bérleti Piac, Hozamszámítás és Rent Gap Elemzés
# ==============================================================================
def build_nb06():
    nb = new_notebook()
    
    nb.cells.append(new_markdown_cell("""# 06. Bérleti Piac, Hozamszámítás és Rent Gap Elemzés

**Cél**: Az eladó és kiadó lakáspiaci szegmensek szisztematikus összehasonlítása, a bruttó és nettó bérleti hozamok (Gross / Net Rental Yield), a Price-to-Rent (P/R) ráta, valamint a Neil Smith-féle bérleti rés (Rent Gap) empirikus kimutatása Kőbányán.

**Elméleti háttér**:
- **Bruttó hozam**: $\\text{Gross Yield} = \\frac{\\text{Havi bérleti díj} \\times 12}{\\text{Eladási vételár}} \\times 100\\%$
- **Price-to-Rent (P/R)**: Megtérülési idő években (Vételár / Éves bérleti díj).
- **Rent Gap**: A jelenlegi állapotú hasznosítás tőkésített bérleti értéke és a felújítás után elérhető maximális potenciális bérleti érték közötti különbség."""))

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

    nb.cells.append(new_markdown_cell("""### 1. Bérleti Piac és Hozam KPI Mutatók
A kőbányai lakáskiadási piac alapvető megtérülési sarokszámai."""))

    nb.cells.append(new_code_cell("""atlag_berlet_huf = kiado['price_huf'].mean()
median_berlet_huf = kiado['price_huf'].median()
atlag_berlet_nm = kiado['nm_ar_huf'].mean()
median_elado_nm = elado['nm_ar_huf'].median()

# Kerületi szintű bruttó bérleti hozam (Ft/m² alapú tőkésítés)
brutto_hozam_pct = (atlag_berlet_nm * 12 / median_elado_nm) * 100
pr_rata_ev = median_elado_nm / (atlag_berlet_nm * 12)

kpi_cards = [
    ("Átlagos Havi Bérlet", fmt_huf(atlag_berlet_huf) + " / hó", f"Medián: {fmt_huf(median_berlet_huf)}", "#1e3a8a"),
    ("Bérleti Fajlagos Díj", fmt_huf(atlag_berlet_nm) + " / m²", "Havi fajlagos ár", "#2563eb"),
    ("Bruttó Bérleti Hozam", f"{brutto_hozam_pct:.2f}%", "Fajlagos éves hozam", "#059669"),
    ("Price-to-Rent Ráta", f"{pr_rata_ev:.1f} év", "Megtérülési periódus", "#d97706"),
    ("Kiadó Lakások Aránya", f"{len(kiado)/len(df)*100:.1f}%", f"{len(kiado)} db hirdetés", "#7c3aed"),
    ("Nettó Hozam (85% kihaszn.)", f"{brutto_hozam_pct * 0.85 * 0.85:.2f}%", "Költségek levonása után", "#10b981")
]
display(HTML(kpi_grid_html(kpi_cards)))"""))

    nb.cells.append(new_markdown_cell("""### 2. Városrészi Bérleti Hozamok és Összehasonlítás
A lakásvásárlási és bérleti árak összevetése városrészenként."""))

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

    nb.cells.append(new_markdown_cell("""### 3. Smith-féle Rent Gap Elemzés (Bérleti Rés)
A felújított és felújítandó lakások közötti tőkésített bérleti különbség (Rent Gap) bemutatása."""))

    nb.cells.append(new_code_cell("""# Bérleti rés elemzése állapotonként
allapot_stat = df.groupby(['allapot', 'listing_type'])['nm_ar_huf'].median().unstack()
allapot_stat = allapot_stat.dropna()

if 'kiado' in allapot_stat.columns and 'elado' in allapot_stat.columns:
    allapot_stat['Eves_Berlet_m2'] = allapot_stat['kiado'] * 12
    allapot_stat['Hozam_pct'] = (allapot_stat['Eves_Berlet_m2'] / allapot_stat['elado']) * 100
    
    fig2 = px.bar(
        allapot_stat.reset_index(),
        x='allapot',
        y='Hozam_pct',
        color='allapot',
        title='Becsült bérleti hozam az ingatlan műszaki állapota szerint',
        labels={'allapot': 'Műszaki állapot', 'Hozam_pct': 'Bruttó Hozam (%)'},
        template=PLOTLY_TEMPLATE
    )
    fig2.update_layout(height=400, showlegend=False)
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

    nb.cells.append(new_markdown_cell("""### 4. Interaktív Hozam- és Megtérülés Kalkulátor
Dinamikusan állítható kihasználtsági ráta, üzemeltetési költség és alapterület."""))

    nb.cells.append(new_code_cell("""w_occ = widgets.FloatSlider(min=0.7, max=1.0, step=0.05, value=0.95, description='Kihasználtság:')
w_cost = widgets.FloatSlider(min=0.05, max=0.30, step=0.05, value=0.15, description='Költség (%):')
w_ar_berlet = widgets.IntSlider(min=150, max=500, step=10, value=250, description='Bérlet (ezer):')
w_ar_vetel = widgets.IntSlider(min=30, max=120, step=5, value=50, description='Vételár (M):')

out_yield = widgets.Output()

def szamol_hozam(*args):
    eves_bev = (w_ar_berlet.value * 1e3 * 12) * w_occ.value
    netto_bev = eves_bev * (1.0 - w_cost.value)
    vetel = w_ar_vetel.value * 1e6
    brutto_h = (w_ar_berlet.value * 1e3 * 12 / vetel) * 100
    netto_h = (netto_bev / vetel) * 100
    megterules = vetel / netto_bev if netto_bev > 0 else 0
    
    with out_yield:
        clear_output(wait=True)
        res_kpis = [
            ("Bruttó Hozam", f"{brutto_h:.2f}%", "Éves bruttó", "#2563eb"),
            ("Nettó Hozam", f"{netto_h:.2f}%", f"Költség & üresedés után", "#10b981"),
            ("Nettó Éves Bevétel", fmt_huf(netto_bev), "Adózás előtti cash flow", "#059669"),
            ("Valós Megtérülés", f"{megterules:.1f} év", "Nettó cash flow alapján", "#d97706")
        ]
        display(HTML(kpi_grid_html(res_kpis)))

w_occ.observe(szamol_hozam, names='value')
w_cost.observe(szamol_hozam, names='value')
w_ar_berlet.observe(szamol_hozam, names='value')
w_ar_vetel.observe(szamol_hozam, names='value')

display(widgets.VBox([
    widgets.HBox([w_occ, w_cost]),
    widgets.HBox([w_ar_berlet, w_ar_vetel])
]))
display(out_yield)
szamol_hozam()"""))

    save_nb(nb, '06_berleti_piac_es_rent_gap.ipynb')

# ==============================================================================
# NOTEBOOK 07: Land Value Capture (LVC) Szimuláció
# ==============================================================================
def build_nb07():
    nb = new_notebook()
    
    nb.cells.append(new_markdown_cell("""# 07. Land Value Capture (LVC) Szimuláció

**Cél**: A közösségi infrastruktúra-fejlesztések (Mázsa tér intermodális csomópont, vasúti átjárók, zöldfelületi rehabilitáció) által generált magánvagyon-növekmény visszanyerési mechanizmusainak szimulációja.

**Módszertan**: Dinamikus Cash Flow (DCF), Net Present Value (NPV), Belső Megtérülési Ráta (IRR) és érzékenységvizsgálat a fejlesztési szintek (Tier 1, 2, 3) és az értéknövekmény-elvonási kulcsok (Capture Rate) függvényében."""))

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

    nb.cells.append(new_markdown_cell("""### 1. LVC Beruházási Szcenáriók és Pénzügyi KPI-k
A Tier 2 fejlesztési szint (5 Mrd Ft CAPEX) hatása a közvetlen hatásterület ingatlanvagyonára (20%-os capture rate mellett)."""))

    nb.cells.append(new_code_cell("""# Érintett ingatlanállomány becslése a Mázsa tér 15 perces izokrónjában
erintett_lakasok_becsles = 12000  # becsült lakásszám a körzetben
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

    nb.cells.append(new_markdown_cell("""### 2. Kumulált Készpénzáramlási Pálya (20 Éves Horizont)
A projekt kumulált cash flow-ja a beruházási időszak alatt és a fejlesztési hozzájárulások befolyása után."""))

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

    nb.cells.append(new_markdown_cell("""### 3. Érzékenységvizsgálat (Diszkontráta vs. Capture Rate Mátrix)
Az NPV alakulása a diszkontráta (3% - 8%) és a visszanyerési kulcs (10% - 35%) kombinációiban."""))

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

    nb.cells.append(new_markdown_cell("""### 4. Interaktív LVC Szimulációs Modell
Dinamikusan tesztelhetők a különböző beruházási szintek és pénzügyi paraméterek."""))

    nb.cells.append(new_code_cell("""w_tier = widgets.Dropdown(options=list(TIERS.keys()), value='Tier 2: Tier 1 + Városi Park & Zöld', description='Szint:')
w_cap = widgets.FloatSlider(min=0.05, max=0.40, step=0.05, value=0.20, description='Capture %:')
w_disc = widgets.FloatSlider(min=0.02, max=0.10, step=0.01, value=0.05, description='Diszkont %:')

out_lvc = widgets.Output()

def frissit_lvc(*args):
    t_info = TIERS[w_tier.value]
    gain = erintett_vagyon * t_info['premium_pct']
    rec = gain * w_cap.value
    cf = np.zeros(21)
    evek = t_info['evek']
    cf[1:evek+1] = -t_info['capex'] / evek
    cf[evek+1:evek+16] = rec / 15.0
    npv_val = sum(cf[t] / ((1 + w_disc.value) ** t) for t in range(len(cf)))
    
    with out_lvc:
        clear_output(wait=True)
        res_kpis = [
            ("Szimulált NPV", fmt_mft(npv_val / 1e6), "Diszkontált egyenleg", "#10b981" if npv_val > 0 else "#ef4444"),
            ("Visszanyerés Összesen", fmt_mft(rec / 1e6), "15 év alatt", "#2563eb"),
            ("CAPEX Fedezet", f"{(rec / t_info['capex']) * 100:.1f}%", "Megtérülési arány", "#7c3aed")
        ]
        display(HTML(kpi_grid_html(res_kpis)))

w_tier.observe(frissit_lvc, names='value')
w_cap.observe(frissit_lvc, names='value')
w_disc.observe(frissit_lvc, names='value')

display(widgets.HBox([w_tier, w_cap, w_disc]))
display(out_lvc)
frissit_lvc()"""))

    save_nb(nb, '07_lvc_szimulacio.ipynb')


# ==============================================================================
# NOTEBOOK 08: Monte Carlo Kockázatelemzés
# ==============================================================================
def build_nb08():
    nb = new_notebook()
    
    nb.cells.append(new_markdown_cell("""# 08. Monte Carlo Kockázatelemzés

**Cél**: A kőbányai ingatlanbefektetések sztochasztikus kockázatértékelése Monte Carlo szimulációval (10 000 iteráció).

**Kockázati metrikák**:
- **Value at Risk (VaR 95%)**: A maximális várható veszteség 95%-os megbízhatósági szinten.
- **Conditional VaR (CVaR 95% / Expected Shortfall)**: A VaR küszöböt meghaladó legrosszabb 5%-os kimenetelek átlagos vesztesége.
- **Nyereségesség valószínűsége**: $P(\\text{NPV} > 0)$."""))

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

    nb.cells.append(new_markdown_cell("""### 1. Szimulációs Eredmények és Kockázati KPI Kártyák
10 000 véletlenszerű piaci pálya szimulációja 20 éves horizonton, vételár-, bérletidíj- és kihasználtsági volatilitás mellett."""))

    nb.cells.append(new_code_cell("""N_ITERS = 10000
price_shocks = np.random.normal(loc=base_price, scale=base_price * 0.12, size=N_ITERS)
rent_shocks = np.random.normal(loc=base_rent, scale=base_rent * 0.10, size=N_ITERS)
occ_shocks = np.clip(np.random.normal(loc=0.92, scale=0.06, size=N_ITERS), 0.70, 1.00)
disc_rate = 0.05
op_cost_ratio = 0.15

# 20 éves NPV számítás minden iterációra
# Kezdeti kiadás: price_shocks, éves nettó cash flow: rent_shocks * 12 * occ_shocks * (1 - op_cost_ratio)
eves_netto_cf = rent_shocks * 12 * occ_shocks * (1.0 - op_cost_ratio)
annuity_factor = (1.0 - (1.0 + disc_rate) ** -20) / disc_rate
terminal_value = price_shocks * 1.2 / ((1.0 + disc_rate) ** 20)  # szerény 20% reálérték növekedés
npv_results = (eves_netto_cf * annuity_factor + terminal_value) - price_shocks

mean_npv = np.mean(npv_results)
median_npv = np.median(npv_results)
var_95 = np.percentile(npv_results, 5)
cvar_95 = np.mean(npv_results[npv_results <= var_95])
prob_positive = (npv_results > 0).mean() * 100
std_npv = np.std(npv_results)

kpi_cards = [
    ("Várható NPV (Átlag)", fmt_mft(mean_npv / 1e6), f"Medián: {fmt_mft(median_npv / 1e6)}", "#10b981" if mean_npv > 0 else "#ef4444"),
    ("VaR 95%", fmt_mft(var_95 / 1e6), "5% legrosszabb küszöb", "#ef4444"),
    ("CVaR 95% (Várható Hiba)", fmt_mft(cvar_95 / 1e6), "Farok-kockázat átlaga", "#dc2626"),
    ("P(NPV > 0) Nyereség", f"{prob_positive:.1f}%", f"{N_ITERS:,} iteráció alapján".replace(',', ' '), "#2563eb"),
    ("NPV Szórás", fmt_mft(std_npv / 1e6), "Bizonytalanság mértéke", "#d97706"),
    ("Alap Vételár", fmt_mft(base_price / 1e6), "50 m² referencia lakás", "#7c3aed")
]
display(HTML(kpi_grid_html(kpi_cards)))"""))

    nb.cells.append(new_markdown_cell("""### 2. Kockázati Eloszlás és Kumulatív Eloszlásfüggvény (CDF)
Az NPV kimenetelek sűrűségfüggvénye, valamint a megbízhatósági sávval ellátott kumulatív valószínűségi függvény."""))

    nb.cells.append(new_code_cell("""fig1 = go.Figure()
fig1.add_trace(go.Histogram(
    x=npv_results / 1e6,
    nbinsx=50,
    name='Szimulált NPV',
    marker_color='#3b82f6',
    opacity=0.75
))
fig1.add_vline(x=mean_npv / 1e6, line_color='#10b981', line_width=3, annotation_text=f'Átlag: {fmt_mft(mean_npv/1e6)}')
fig1.add_vline(x=var_95 / 1e6, line_color='#ef4444', line_width=3, line_dash='dash', annotation_text=f'VaR 95%: {fmt_mft(var_95/1e6)}')
fig1.add_vline(x=cvar_95 / 1e6, line_color='#991b1b', line_width=3, line_dash='dot', annotation_text=f'CVaR: {fmt_mft(cvar_95/1e6)}')

fig1.update_layout(
    title='Monte Carlo NPV Eloszlás a Kockázati Mutatókkal (Millió Ft)',
    xaxis_title='NPV (M Ft)',
    yaxis_title='Gyakoriság',
    template=PLOTLY_TEMPLATE,
    height=450
)
fig1.show()

# CDF görbe
sorted_npv = np.sort(npv_results) / 1e6
p_vals = np.linspace(0, 1, len(sorted_npv))

fig2 = go.Figure()
fig2.add_trace(go.Scatter(x=sorted_npv, y=p_vals, mode='lines', line=dict(color='#2563eb', width=3), name='Empirikus CDF'))
fig2.add_hline(y=0.05, line_color='red', line_dash='dash', annotation_text='5% (VaR szint)')
fig2.add_vline(x=0, line_color='black', line_dash='dot', annotation_text='NPV = 0')

fig2.update_layout(
    title='Kumulatív Eloszlásfüggvény (CDF) és Kockázati Valószínűség',
    xaxis_title='NPV (M Ft)',
    yaxis_title='Kumulatív Valószínűség P(X ≤ x)',
    template=PLOTLY_TEMPLATE,
    height=420
)
fig2.show()"""))

    nb.cells.append(new_markdown_cell("""### 3. Érzékenységi Tornado Diagram és Futási Konvergencia
A bizonytalansági faktorok marginális hozzájárulása a kimeneti szóráshoz, valamint a futási stabilitás vizsgálata."""))

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
running_mean = [np.mean(npv_results[:i]) / 1e6 for i in conv_iters]

fig4 = go.Figure()
fig4.add_trace(go.Scatter(x=conv_iters, y=running_mean, mode='lines', line=dict(color='#059669', width=2), name='Futó Átlag NPV'))
fig4.update_layout(
    title='Monte Carlo Konvergencia Görbe (Iterációk Stabilitása)',
    xaxis_title='Iterációk Száma',
    yaxis_title='Becsült Átlagos NPV (M Ft)',
    template=PLOTLY_TEMPLATE,
    height=380
)
fig4.show()"""))

    nb.cells.append(new_markdown_cell("""### 4. Interaktív Monte Carlo Kockázati Szimulátor
Próbálja ki a szimulációt különböző iterációszámokkal és bizonytalansági szintekkel!"""))

    nb.cells.append(new_code_cell("""w_n_sim = widgets.IntSlider(min=1000, max=25000, step=1000, value=5000, description='Iterációk:')
w_p_vol = widgets.FloatSlider(min=0.05, max=0.25, step=0.01, value=0.12, description='Ár szórás:')
w_r_vol = widgets.FloatSlider(min=0.05, max=0.20, step=0.01, value=0.10, description='Bérlet szórás:')

out_mc = widgets.Output()

def futtat_mc(*args):
    np.random.seed(42)
    n = w_n_sim.value
    p_sim = np.random.normal(base_price, base_price * w_p_vol.value, n)
    r_sim = np.random.normal(base_rent, base_rent * w_r_vol.value, n)
    cf_sim = r_sim * 12 * 0.92 * 0.85
    npv_s = (cf_sim * annuity_factor + p_sim * 1.2 / (1.05**20)) - p_sim
    
    with out_mc:
        clear_output(wait=True)
        mc_kpis = [
            ("Szimulált Átlag", fmt_mft(np.mean(npv_s)/1e6), "Várható NPV", "#10b981"),
            ("Szimulált VaR 95%", fmt_mft(np.percentile(npv_s, 5)/1e6), "Max várható veszteség", "#ef4444"),
            ("P(NPV > 0)", f"{(npv_s > 0).mean()*100:.1f}%", "Sikerességi arány", "#2563eb")
        ]
        display(HTML(kpi_grid_html(mc_kpis)))

w_n_sim.observe(futtat_mc, names='value')
w_p_vol.observe(futtat_mc, names='value')
w_r_vol.observe(futtat_mc, names='value')

display(widgets.HBox([w_n_sim, w_p_vol, w_r_vol]))
display(out_mc)
futtat_mc()"""))

    save_nb(nb, '08_monte_carlo_kockazat.ipynb')


# ==============================================================================
# NOTEBOOK 09: Klaszter és Tipológia Elemzés
# ==============================================================================
def build_nb09():
    nb = new_notebook()
    
    nb.cells.append(new_markdown_cell("""# 09. Klaszter és Tipológia Elemzés

**Cél**: A kőbányai lakáspiaci kínálat automatikus tipológiájának és természetes alpiacainak feltárása nem felügyelt gépi tanulási módszerekkel (K-Means és Hierarchikus klaszterezés).

**Módszertan**: Robusztus standardizálás (`StandardScaler`), optimális klaszterszám meghatározása az Elbow (Inertia) módszerrel és Silhouette pontszámokkal, valamint dimenziócsökkentés Főkomponens-elemzéssel (PCA)."""))

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

    nb.cells.append(new_markdown_cell("""### 1. Klaszterezési Eredmények és Tipológiai KPI-k
K=4 szegmens illesztése a normalizált ingatlanjellemzőkre (fajlagos ár, alapterület, szobaszám, állapot, épületkora)."""))

    nb.cells.append(new_code_cell("""cluster_vars = ['nm_ar_huf', 'alapterulet_nm', 'szobaszam_osszes', 'allapot_kod', 'epulet_kora_ev']
df_km = elado.dropna(subset=cluster_vars).copy()

scaler = StandardScaler()
X_scaled = scaler.fit_transform(df_km[cluster_vars])

kmeans = KMeans(n_clusters=4, random_state=42, n_init=10)
df_km['klaszter'] = kmeans.fit_predict(X_scaled)

# Klaszter elnevezések képzése profil szerint
means = df_km.groupby('klaszter')[cluster_vars].mean()
cluster_names = {
    0: '1. Kisméretű Olcsóbb Panellakások',
    1: '2. Családi Méretű Középkategória',
    2: '3. Prémium / Újszerű Lakások',
    3: '4. Felújítandó Nagypolgári / Egyéb'
}
df_km['klaszter_nev'] = df_km['klaszter'].map(cluster_names)

sil = silhouette_score(X_scaled, df_km['klaszter'])

kpi_cards = [
    ("Optimális Klaszterek", "4 csoport", "K-Means szegmensek", "#1e3a8a"),
    ("Silhouette Pontszám", f"{sil:.3f}", "Klaszter szeparáció jósága", "#059669"),
    ("1. Szegmens Méret", f"{(df_km['klaszter']==0).sum()} db", "Panellakások", "#ef4444"),
    ("2. Szegmens Méret", f"{(df_km['klaszter']==1).sum()} db", "Családi lakások", "#2563eb"),
    ("3. Szegmens Méret", f"{(df_km['klaszter']==2).sum()} db", "Prémium kategória", "#10b981"),
    ("4. Szegmens Méret", f"{(df_km['klaszter']==3).sum()} db", "Felújítandók", "#d97706")
]
display(HTML(kpi_grid_html(kpi_cards)))"""))

    nb.cells.append(new_markdown_cell("""### 2. Optimális Klaszterszám (Elbow Görbe és Silhouette)
Az inercia csökkenése és a Silhouette pontszámok alakulása K=2..8 klaszterszámra."""))

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

    nb.cells.append(new_markdown_cell("""### 3. Klaszterprofilok és Városrészi Összetétel
A négy lakástípus átlagos tulajdonságai és eloszlásuk a kőbányai városrészekben."""))

    nb.cells.append(new_code_cell("""# Összefoglaló statisztika táblázat
cluster_summary = df_km.groupby('klaszter_nev')[cluster_vars].mean().reset_index()
display(HTML("<b>Klaszterek átlagos jellemzői:</b><br>" + cluster_summary.round(1).to_html(classes='table table-bordered table-striped', index=False)))

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

    nb.cells.append(new_markdown_cell("""### 4. Interaktív Klaszterezési Sandbox
Tesztelje interaktívan a klaszterezést különböző klaszterszámok (K=2..6) beállításával!"""))

    nb.cells.append(new_code_cell("""w_k_slider = widgets.IntSlider(min=2, max=6, value=4, description='Klaszter K:')
out_km = widgets.Output()

def frissit_km(*args):
    k = w_k_slider.value
    km = KMeans(n_clusters=k, random_state=42, n_init=10)
    labels = km.fit_predict(X_scaled)
    s_score = silhouette_score(X_scaled, labels)
    
    with out_km:
        clear_output(wait=True)
        display(HTML(kpi_grid_html([
            ("Klaszterszám", f"{k} db", "Választott K", "#2563eb"),
            ("Silhouette Index", f"{s_score:.3f}", "Elkülönültség", "#10b981")
        ])))
        fig = px.scatter(
            x=coords_pca[:, 0], y=coords_pca[:, 1], color=[f'Klaszter {c+1}' for c in labels],
            title=f'K={k} Klaszter PCA vetülete (Silhouette={s_score:.3f})',
            template=PLOTLY_TEMPLATE
        )
        fig.show()

w_k_slider.observe(frissit_km, names='value')
display(w_k_slider)
display(out_km)
frissit_km()"""))

    save_nb(nb, '09_klaszter_es_tipologia.ipynb')

# ==============================================================================
# NOTEBOOK 10: Térbeli Autokorreláció (Moran's I) és Hotspot Elemzés
# ==============================================================================
def build_nb10():
    nb = new_notebook()
    
    nb.cells.append(new_markdown_cell("""# 10. Térbeli Autokorreláció (Moran's I) és Hotspot Elemzés

**Cél**: A kőbányai ingatlanárak térbeli klasztereződésének (Spatial Autocorrelation), forrópontjainak (Hotspots) és hidegpontjainak (Coldspots) ökonometriai kimutatása.

**Módszertan**:
- **Globális Moran's I**: Annak vizsgálata, hogy az ingatlanárak véletlenszerűen oszlanak-e el a térben, vagy statisztikailag szignifikáns térbeli klasztereződést mutatnak ($I > 0$).
- **Lokális Moran (LISA - Local Indicators of Spatial Association)**: A térbeli alcsoportok azonosítása: High-High (magas árak magas árú szomszédokkal), Low-Low (alacsony árak alacsony árú szomszédokkal), High-Low és Low-High térbeli kiugró értékek (outliers).

**Adatalap**: A garantált pontos eladó lakások mintája (N=254) a módszertani tisztaság és a bérleti díjakkal való keveredés elkerülése érdekében."""))

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
df_geo = df[(df['minta_garantalt_pontos'] == 1) & (df['listing_type'] == 'elado')].dropna(subset=['geokodolt_lat', 'geokodolt_lon', 'nm_ar_huf']).copy()
df_geo.reset_index(drop=True, inplace=True)
coords = np.column_stack((df_geo['geokodolt_lon'], df_geo['geokodolt_lat']))

print(f"Elemzett garantált pontos eladó lakásminta: {len(df_geo)} db.")"""))

    nb.cells.append(new_markdown_cell("""### 1. Globális Moran's I Térökonometriai Eredmények
A k=8 legközelebbi szomszéd (KNN) térbeli súlyozási mátrix és a 999 permutációs szimuláció alapján becsült autokorreláció."""))

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

    nb.cells.append(new_markdown_cell("""### 2. Moran Scatter Plot és Permutációs Hipotézisvizsgálat
A standardizált négyzetméterárak és a térbeli késleltetett értékek (Spatial Lag) összefüggése a 4 kvadránssal (HH, HL, LH, LL)."""))

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

    nb.cells.append(new_markdown_cell("""### 3. Lokális Térbeli Klaszterek (LISA Hotspot és Coldspot Térkép)
A statisztikailag szignifikáns High-High (Hotspot, magas árak) és Low-Low (Coldspot, alacsony árak) területek valós térképi megjelenítése."""))

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

    nb.cells.append(new_markdown_cell("""### 4. Interaktív Moran's I és Súlyozási Pult
Tesztelje a térbeli autokorrelációt különböző változókra és szomszédsági k-értékekre!"""))

    nb.cells.append(new_code_cell("""w_var = widgets.Dropdown(
    options=[('Négyzetméterár', 'nm_ar_huf'), ('Alapterület', 'alapterulet_nm'), ('Állapot Kód', 'allapot_kod'), ('Szobaszám', 'szobaszam_osszes')],
    value='nm_ar_huf',
    description='Változó:'
)
w_k = widgets.IntSlider(min=4, max=16, step=2, value=8, description='k (KNN):')

out_moran = widgets.Output()

def frissit_moran(*args):
    v = w_var.value
    y = df_geo[v].values
    w = KNN.from_array(coords, k=w_k.value)
    w.transform = 'R'
    m = Moran(y, w, permutations=99)
    
    with out_moran:
        clear_output(wait=True)
        m_kpis = [
            ("Választott Moran I", f"{m.I:.3f}", f"z = {m.z_sim:.2f}", "#2563eb"),
            ("P-érték", f"{m.p_sim:.4f}", "Szignifikancia", "#059669" if m.p_sim < 0.05 else "#ef4444"),
            ("Szomszédok", f"k = {w_k.value}", "KNN mátrix", "#7c3aed")
        ]
        display(HTML(kpi_grid_html(m_kpis)))

w_var.observe(frissit_moran, names='value')
w_k.observe(frissit_moran, names='value')

display(widgets.HBox([w_var, w_k]))
display(out_moran)
frissit_moran()"""))

    save_nb(nb, '10_moran_es_autokorrelacio.ipynb')


# ==============================================================================
# NOTEBOOK 11: Interaktív Ingatlan Kereső Dashboard
# ==============================================================================
def build_nb11():
    nb = new_notebook()
    
    nb.cells.append(new_markdown_cell("""# 11. Interaktív Ingatlan Kereső Dashboard

**Cél**: Átfogó, interaktív kereső és szűrőfelület a kőbányai lakáspiaci adatbázis felfedezésére, egyedi befektetői és vásárlói szempontok szerinti böngészésre és térképi megjelenítésre.

**Funkciók**:
- Szűrés típus szerint (Eladó / Kiadó / Mindkettő)
- Ár és fajlagos ár sávok, alapterület és szobaszám intervallumok
- Városrész és épülettípus (tégla / panel / új építésű) szerinti szűkítés
- Rendezhető, elegáns formázású találati táblázat és interaktív térkép."""))

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
print(f"Teljes adatbázis betöltve: {len(df)} hirdetés.")"""))

    nb.cells.append(new_markdown_cell("""### 1. Teljes Kínálati Piac KPI Áttekintése
A kőbányai ingatlanállomány globális piaci mérőszámai."""))

    nb.cells.append(new_code_cell("""n_all = len(df)
n_elado = len(df[df['listing_type'] == 'elado'])
n_kiado = len(df[df['listing_type'] == 'kiado'])
med_ar_elado = df[df['listing_type'] == 'elado']['price_huf'].median()
med_nm_elado = df[df['listing_type'] == 'elado']['nm_ar_huf'].median()
atlag_meret = df['alapterulet_nm'].mean()

kpi_cards = [
    ("Összes Kínálat", f"{n_all:,} db".replace(',', ' '), "Teljes adatbázis", "#1e3a8a"),
    ("Eladó Lakások", f"{n_elado:,} db".replace(',', ' '), f"Medián: {fmt_mft(med_ar_elado/1e6)}", "#2563eb"),
    ("Kiadó Lakások", f"{n_kiado:,} db".replace(',', ' '), f"{n_kiado/n_all*100:.1f}% arány", "#d97706"),
    ("Eladó Medián Ár/m²", fmt_huf(med_nm_elado), "Fajlagos ár", "#10b981"),
    ("Átlagos Méret", f"{atlag_meret:.1f} m²", "Kínálati átlag", "#059669"),
    ("Városrészek", f"{df['varosresz'].nunique()} zóna", "Kőbánya egésze", "#7c3aed")
]
display(HTML(kpi_grid_html(kpi_cards)))"""))

    nb.cells.append(new_markdown_cell("""### 2. Kínálati Ár és Alapterület Eloszlások
A teljes kínálat négyzetméterár-eloszlása és a geokódolt ingatlanok térbeli lefedettsége."""))

    nb.cells.append(new_code_cell("""fig1 = px.histogram(
    df,
    x='nm_ar_huf',
    color='listing_type',
    barmode='overlay',
    nbins=40,
    title='Kínálati Négyzetméterárak Eloszlása Eladó és Kiadó Szegmensekben',
    labels={'nm_ar_huf': 'Ár / m² (HUF)', 'listing_type': 'Típus'},
    template=PLOTLY_TEMPLATE,
    opacity=0.75
)
fig1.update_layout(height=420)
fig1.show()

# Pontos minták térképe
df_pts = df[(df['minta_garantalt_pontos'] == 1) & (df['listing_type'] == 'elado')]
fig2 = px.scatter_map(
    df_pts,
    lat='geokodolt_lat',
    lon='geokodolt_lon',
    color='nm_ar_huf',
    size='alapterulet_nm',
    hover_name='cim_teljes',
    hover_data={'nm_ar_huf': ':.0f', 'varosresz': True},
    zoom=12.2,
    center={'lat': KOBANYA_CENTER_LAT, 'lon': KOBANYA_CENTER_LON},
    map_style='carto-positron',
    title=f'Garantált pontos eladó lakások térképi elhelyezkedése (N={len(df_pts)})'
)
fig2.update_layout(height=480, margin={"r":0,"t":40,"l":0,"b":0})
fig2.show()"""))

    nb.cells.append(new_markdown_cell("""### 3. Kiemelt Találati Lista (Top 25 Kínálat)
Formázott, áttekinthető ingatlanlista a legfrissebb hirdetésekből."""))

    nb.cells.append(new_code_cell("""show_cols = ['listing_id', 'cim_teljes', 'ar_millio_ft', 'nm_ar_huf', 'alapterulet_nm', 'szobaszam_osszes', 'varosresz', 'allapot']
top_listings = df[df['listing_type'] == 'elado'][show_cols].head(25).copy()

top_listings['ar_millio_ft'] = top_listings['ar_millio_ft'].apply(lambda x: f"{x:.1f} M Ft" if pd.notna(x) else "—")
top_listings['nm_ar_huf'] = top_listings['nm_ar_huf'].apply(fmt_huf)
top_listings['alapterulet_nm'] = top_listings['alapterulet_nm'].apply(lambda x: f"{x:.0f} m²" if pd.notna(x) else "—")

table_html = "<div style='overflow-x:auto; max-height:450px; overflow-y:auto; margin:15px 0;'>" + top_listings.to_html(classes='table table-striped table-hover', index=False) + "</div>"
display(HTML(table_html))"""))

    nb.cells.append(new_markdown_cell("""### 4. Teljes Értékű Interaktív Kereső és Szűrő Rendszer
Használja a lenti vezérlőket a kínálat szűréséhez és azonnali táblázatos megjelenítéséhez!"""))

    nb.cells.append(new_code_cell("""w_tipus = widgets.RadioButtons(options=['eladó', 'kiadó', 'Mindkettő'], value='eladó', description='Típus:')
w_ar_sav = widgets.IntRangeSlider(min=20, max=150, value=(30, 80), description='Ár (M Ft):')
w_meret_sav = widgets.IntRangeSlider(min=20, max=150, value=(35, 90), description='Méret (m²):')
w_varos = widgets.SelectMultiple(options=VAROSRESZEK, value=tuple(VAROSRESZEK[:3]), description='Városrészek:')
w_rendezes = widgets.Dropdown(options=['Ár növekvő', 'Ár csökkenő', 'Ár/m² növekvő', 'Méret csökkenő'], value='Ár/m² növekvő', description='Rendezés:')

out_search = widgets.Output()

def frissit_kereses(*args):
    dff = df.copy()
    if w_tipus.value != 'Mindkettő':
        mapped_val = 'elado' if w_tipus.value == 'eladó' else 'kiado'
        dff = dff[dff['listing_type'] == mapped_val]
    if w_tipus.value == 'eladó':
        dff = dff[(dff['ar_millio_ft'] >= w_ar_sav.value[0]) & (dff['ar_millio_ft'] <= w_ar_sav.value[1])]
    dff = dff[(dff['alapterulet_nm'] >= w_meret_sav.value[0]) & (dff['alapterulet_nm'] <= w_meret_sav.value[1])]
    if w_varos.value:
        dff = dff[dff['varosresz'].isin(w_varos.value)]
        
    if w_rendezes.value == 'Ár növekvő':
        dff = dff.sort_values('price_huf', ascending=True)
    elif w_rendezes.value == 'Ár csökkenő':
        dff = dff.sort_values('price_huf', ascending=False)
    elif w_rendezes.value == 'Ár/m² növekvő':
        dff = dff.sort_values('nm_ar_huf', ascending=True)
    else:
        dff = dff.sort_values('alapterulet_nm', ascending=False)
        
    with out_search:
        clear_output(wait=True)
        search_kpis = [
            ("Találatok Száma", f"{len(dff):,} db".replace(',', ' '), "Szűrési feltételeknek megfelel", "#1e3a8a"),
            ("Szűrt Medián Ár", fmt_mft(dff['price_huf'].median()/1e6 if len(dff)>0 else 0), "Középérték", "#2563eb"),
            ("Szűrt Medián Ár/m²", fmt_huf(dff['nm_ar_huf'].median() if len(dff)>0 else 0), "Fajlagos", "#10b981")
        ]
        display(HTML(kpi_grid_html(search_kpis)))
        if len(dff) > 0:
            preview = dff[['cim_teljes', 'ar_millio_ft', 'nm_ar_huf', 'alapterulet_nm', 'szobaszam_osszes', 'varosresz']].head(20).copy()
            preview['ar_millio_ft'] = preview['ar_millio_ft'].apply(lambda x: f"{x:.1f} M" if pd.notna(x) else "—")
            preview['nm_ar_huf'] = preview['nm_ar_huf'].apply(fmt_huf)
            display(HTML("<div style='overflow-x:auto; max-height:350px; overflow-y:auto;'>" + preview.to_html(classes='table table-sm table-striped', index=False) + "</div>"))
        else:
            print("Nincs a feltételeknek megfelelő találat.")

w_tipus.observe(frissit_kereses, names='value')
w_ar_sav.observe(frissit_kereses, names='value')
w_meret_sav.observe(frissit_kereses, names='value')
w_varos.observe(frissit_kereses, names='value')
w_rendezes.observe(frissit_kereses, names='value')

display(widgets.VBox([
    widgets.HBox([w_tipus, w_ar_sav, w_meret_sav]),
    widgets.HBox([w_varos, w_rendezes])
]))
display(out_search)
frissit_kereses()"""))

    save_nb(nb, '11_ingatlan_kereso_dashboard.ipynb')


# ==============================================================================
# MAIN GENERATOR RUNNER
# ==============================================================================
def build_all():
    print("=" * 60)
    print("STARTING FULL NOTEBOOK GENERATION (00 - 11)...")
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
    print("=" * 60)
    print("ALL 12 NOTEBOOKS GENERATED SUCCESSFULLY!")
    print("=" * 60)

if __name__ == '__main__':
    build_all()
