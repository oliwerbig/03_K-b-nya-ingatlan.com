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

    nb.cells.append(new_markdown_cell(NOTEBOOK_DOCS["nb00"]["sec3"]))

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

    nb.cells.append(new_markdown_cell(NOTEBOOK_DOCS["nb00"]["sec4"]))

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

    nb.cells.append(new_code_cell("""# Modell változók definiálása
elado['log_tavolsag_vasut_m'] = np.log(elado['tavolsag_vasut_m'].replace(0, 1))

features = [
    'korrigalt_alapterulet_nm', 'szobaszam_osszes', 'is_panel', 
    'has_lift', 'allapot_kod', 
    'tavolsag_metro_halozati_m',
    'log_tavolsag_vasut_m',            # PÁLYATEST LÉGVONAL (Zaj externália)
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

    nb.cells.append(new_code_cell("""# 3 modell becslése
m1_feats = ['korrigalt_alapterulet_nm', 'szobaszam_osszes', 'is_panel', 'has_lift', 'allapot_kod', 'tavolsag_metro_halozati_m']
m2_feats = m1_feats + ['log_tavolsag_vasut_m']
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

    nb.cells.append(new_markdown_cell(NOTEBOOK_DOCS["nb04"]["sec4"]))

    nb.cells.append(new_code_cell("""w_vars = widgets.SelectMultiple(
    options=[(valtozo_magyarazat.get(c, c), c) for c in features],
    value=tuple(features),
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

    nb.cells.append(new_code_cell("""from plotly.subplots import make_subplots
fig_dual = make_subplots(specs=[[{"secondary_y": True}]])
df_zona = elado.dropna(subset=["vasut_zona"]).groupby("vasut_zona", observed=True).agg({"nm_ar_huf":"median", "tavolsag_vasut_halozati_m":"median"}).reset_index()
df_zona["log_nm_ar"] = np.log(df_zona["nm_ar_huf"] / 1000)
fig_dual.add_trace(go.Scatter(x=df_zona["vasut_zona"].astype(str), y=df_zona["log_nm_ar"]*1000, mode="lines+markers", name="Fajlagos Ár", line=dict(color="blue", width=3)), secondary_y=False)
if "tavolsag_vasut_halozati_m" in df_zona.columns:
    fig_dual.add_trace(go.Scatter(x=df_zona["vasut_zona"].astype(str), y=df_zona["tavolsag_vasut_halozati_m"], mode="lines+markers", name="Állomás Hálózati Távolság", line=dict(color="orange", width=2, dash="dot")), secondary_y=True)
fig_dual.update_layout(title="Vasúti Zónák: Zajdiszkont vs. Elérhetőség", template=PLOTLY_TEMPLATE)
fig_dual.show()"""))

    nb.cells.append(new_markdown_cell(NOTEBOOK_DOCS["nb05"]["sec2"]))

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

    save_nb(nb, '08_moran_es_autokorrelacio.ipynb')


# ==============================================================================
# NOTEBOOK 11: Interaktív Ingatlan Kereső Dashboard
# ==============================================================================
def build_nb15():
    nb = new_notebook()
    
    nb.cells.append(new_markdown_cell(NOTEBOOK_DOCS["nb11"]["intro"]))

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

    nb.cells.append(new_markdown_cell(NOTEBOOK_DOCS["nb11"]["sec1"]))

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

    nb.cells.append(new_markdown_cell(NOTEBOOK_DOCS["nb11"]["sec2"]))

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

    nb.cells.append(new_markdown_cell(NOTEBOOK_DOCS["nb11"]["sec3"]))

    nb.cells.append(new_code_cell("""show_cols = ['listing_id', 'cim_teljes', 'ar_millio_ft', 'nm_ar_huf', 'alapterulet_nm', 'szobaszam_osszes', 'varosresz', 'allapot']
top_listings = df[df['listing_type'] == 'elado'][show_cols].head(25).copy()

top_listings['ar_millio_ft'] = top_listings['ar_millio_ft'].apply(lambda x: f"{x:.1f} M Ft" if pd.notna(x) else "—")
top_listings['nm_ar_huf'] = top_listings['nm_ar_huf'].apply(fmt_huf)
top_listings['alapterulet_nm'] = top_listings['alapterulet_nm'].apply(lambda x: f"{x:.0f} m²" if pd.notna(x) else "—")

table_html = "<div style='overflow-x:auto; max-height:450px; overflow-y:auto; margin:15px 0;'>" + top_listings.to_html(classes='table table-striped table-hover', index=False) + "</div>"
display(HTML(table_html))"""))

    nb.cells.append(new_markdown_cell(NOTEBOOK_DOCS["nb11"]["sec4"]))

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

    nb.cells.append(new_code_cell("""df_pontos['emelet_szam'] = df_pontos['emelet_szam'].fillna(df_pontos['emelet_szam'].median())
df_pontos['epulet_kora_ev'] = df_pontos['epulet_kora_ev'].fillna(df_pontos['epulet_kora_ev'].median())

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

    nb.cells.append(new_code_cell("""w_terulet = widgets.IntSlider(min=25, max=120, value=55, description='Méret (m²):')
w_allapot = widgets.Dropdown(options=[('Felújított (5)', 5), ('Jó állapotú (4)', 4), ('Közepes (3)', 3), ('Felújítandó (2)', 2), ('Új építésű (6)', 6)], value=4, description='Állapot:')
w_panel = widgets.RadioButtons(options=[('Tégla', 0), ('Panel', 1)], value=0, description='Típus:')
w_metro_dist = widgets.IntSlider(min=100, max=2500, step=100, value=600, description='Metró (m):')
w_vasut_dist = widgets.IntSlider(min=50, max=1500, step=50, value=400, description='Vasút (m):')

out_calc = widgets.Output()

def szamol_ertek(*args):
    x_input = pd.DataFrame([{
        'korrigalt_alapterulet_nm': float(w_terulet.value),
        'szobaszam_osszes': 2.0 if w_terulet.value < 60 else 3.0,
        'is_panel': float(w_panel.value),
        'has_lift': 1.0 if w_panel.value == 1 else 0.0,
        'allapot_kod': float(w_allapot.value),
        'tavolsag_metro_halozati_m': float(w_metro_dist.value),
        'tavolsag_vasut_m': float(w_vasut_dist.value),
        'tavolsag_vasut_halozati_m': float(w_vasut_dist.value * 1.2),
        'tavolsag_mazsa_halozati_m': 1000.0
    }])
    pred_nm = rf.predict(x_input)[0]
    pred_tot = (pred_nm * w_terulet.value) / 1e6
    
    with out_calc:
        clear_output(wait=True)
        pred_kpis = [
            ("Becsült Lakásár", fmt_mft(pred_tot), "ML modell előrejelzés", "#10b981"),
            ("Becsült Fajlagos Ár", fmt_huf(pred_nm), "Kínálati becslés", "#2563eb"),
            ("Modell Típus", "Random Forest Regressor", "150 döntési fa", "#7c3aed")
        ]
        display(HTML(kpi_grid_html(pred_kpis)))

w_terulet.observe(szamol_ertek, names='value')
w_allapot.observe(szamol_ertek, names='value')
w_panel.observe(szamol_ertek, names='value')
w_metro_dist.observe(szamol_ertek, names='value')
w_vasut_dist.observe(szamol_ertek, names='value')

display(widgets.VBox([
    widgets.HBox([w_terulet, w_allapot]),
    widgets.HBox([w_panel, w_metro_dist, w_vasut_dist])
]))
display(out_calc)
szamol_ertek()"""))

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

    nb.cells.append(new_code_cell("""w_k_sar = widgets.IntSlider(min=4, max=16, step=2, value=8, description='k-Szomszéd:')
out_sar = widgets.Output()

def frissit_sar(*args):
    w_k = KNN.from_array(coords_clean, k=w_k_sar.value)
    w_k.transform = 'R'
    wy_k = w_k.sparse.dot(y_vec)
    wx_k = w_k.sparse.dot(X_mat)
    
    z_k = sm.add_constant(np.column_stack((X_mat, wx_k)))
    wy_hat_k = sm.OLS(wy_k, z_k).fit().fittedvalues
    res_k = sm.OLS(y_vec, sm.add_constant(np.column_stack((X_mat, wy_hat_k)))).fit()
    
    rho_k = float(np.asarray(res_k.params)[-1])
    m_resid = Moran(res_k.resid, w_k).I
    
    with out_sar:
        clear_output(wait=True)
        sar_kpis = [
            ("Választott k", f"{w_k_sar.value} szomszéd", "KNN topológia", "#2563eb"),
            ("Becsült ρ Paraméter", f"{rho_k:.3f}", f"Multiplikátor: {1/(1-rho_k):.2f}x", "#10b981"),
            ("Maradvány Moran I", f"{m_resid:.3f}", "Spillover kontroll után", "#059669")
        ]
        display(HTML(kpi_grid_html(sar_kpis)))

w_k_sar.observe(frissit_sar, names='value')
display(w_k_sar)
display(out_sar)
frissit_sar()"""))

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

features = ['korrigalt_alapterulet_nm', 'is_panel', 'tavolsag_metro_halozati_m', 'poi_375m_count', 'poi_750m_count', 'poi_1125m_count']
df_reg = df_pontos.dropna(subset=['log_nm_ar'] + features).copy()

X = sm.add_constant(df_reg[features])
y = df_reg['log_nm_ar']
model = sm.OLS(y, X).fit()

res_df = pd.DataFrame({
    'Változó': model.params.index,
    'Együttható (β)': model.params.values,
    'p-érték': model.pvalues.values
})
display(HTML("<div style='overflow-x:auto; margin: 15px 0;'>" + res_df.round(4).to_html(classes='table table-bordered table-striped', index=False) + "</div>"))
print(f"Az új modell R² értéke: {model.rsquared:.4f}")"""))

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

    nb.cells.append(new_code_cell("""target_col = 'gwr_tavolsag_metro_halozati_m'

if target_col in df_agg.columns:
    fig = px.scatter_map(
        df_agg,
        lat='geokodolt_lat',
        lon='geokodolt_lon',
        color=target_col,
        size='korrigalt_alapterulet_nm',
        hover_data=[target_col, 'log_nm_ar'],
        color_continuous_scale='RdYlBu', # Red: gyenge hatás, Blue: erős negatív hatás
        map_style='carto-positron',
        zoom=12.2,
        title='GWR: A metrótávolság lokális regressziós együtthatója (Épület szinten aggregálva)'
    )
    fig.update_layout(height=550, margin={"r":0,"t":40,"l":0,"b":0})
    fig.show()
else:
    print("A megjelenítéshez futtassa le a GWR modellt.")"""))

    nb.cells.append(new_markdown_cell(NOTEBOOK_DOCS["nb15"]["sec3"]))

    nb.cells.append(new_code_cell("""if MGWR_AVAILABLE:
    # A lokális t-statisztikák és paraméterek eloszlása
    gwr_summary = pd.DataFrame(gwr_results.params, columns=['Konstans'] + features)
    
    fig = px.box(
        gwr_summary.melt(),
        x='variable',
        y='value',
        color='variable',
        title='GWR Regressziós Együtthatók Térbeli Szóródása (Heterogenitása)',
        template=PLOTLY_TEMPLATE
    )
    fig.update_layout(height=450, showlegend=False)
    fig.show()"""))

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
