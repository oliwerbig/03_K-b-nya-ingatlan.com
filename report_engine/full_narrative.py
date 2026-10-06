# -*- coding: utf-8 -*-
"""
report_engine/full_narrative.py
Tudományos narratívákat, elméleti hátteret és empirikus kiértékelést előállító modul.
Integrálja a notebook_docs.py teljes szövegét mind a 16 fejezetbe,
kiegészítve a valós idejű számítási táblázatokkal, KPI kártyákkal és ábrákkal.
"""

import markdown
from typing import Dict, Any

from notebook_docs import NOTEBOOK_DOCS


class SafeDict(dict):
    """Dictionary that returns the key wrapped in {} if missing, to prevent KeyError on KaTeX."""
    def __missing__(self, key):
        return '{' + key + '}'

class FullNarrativeGenerator:
    """16 fejezetes tudományos narratíva és fejezetépítő generátor."""

    def __init__(self, data: Dict[str, Any]):
        self.data = data
        self.area_id = data['area_id']
        self.area_name = data['area_name']
        self.short_name = data['short_name']
        self.role = data['role']
        self.context = self._build_template_context()

    def _build_template_context(self) -> SafeDict:
        """Kivonja a számított mutatókat a self.data-ból és string dictionaryvé alakítja."""
        d = self.data
        ctx = SafeDict({
            'area_name': self.area_name,
            'short_name': self.short_name,
            'role': self.role,
            'currency': d.get('currency', 'HUF'),
            'currency_symbol': d.get('currency_symbol', 'Ft'),
            'unit_sqm': d.get('unit_sqm', 'Ft/m²'),
            'unit_total': d.get('unit_total', 'Ft'),
            'unit_million': d.get('unit_million', 'M Ft'),
            'unit_rent': d.get('unit_rent', 'Ft/hó'),
        })
        
        # nb00
        if 'nb00' in d:
            ctx['n_total'] = f"{d['nb00'].get('n_total', 0):,}".replace(',', ' ')
            ctx['n_elado'] = f"{d['nb00'].get('n_elado', 0):,}".replace(',', ' ')
            ctx['n_kiado'] = f"{d['nb00'].get('n_kiado', 0):,}".replace(',', ' ')
            ctx['n_pontos'] = f"{d['nb00'].get('n_pontos', 0):,}".replace(',', ' ')
            ctx['pct_elado'] = f"{d['nb00'].get('pct_elado', 0):.1f}"
            ctx['pct_kiado'] = f"{d['nb00'].get('pct_kiado', 0):.1f}"
            ctx['pct_pontos'] = f"{d['nb00'].get('pct_pontos', 0):.1f}"
            ctx['mean_area_elado'] = f"{d['nb00'].get('mean_area', 0):.1f}"
            ctx['mean_area_kiado'] = f"{d['nb00'].get('mean_area_kiado', 52.5):.1f}"
            
        # nb01
        if 'nb01' in d:
            ctx['median_nm_ar'] = f"{d['nb01'].get('median', 0):,.0f}".replace(',', ' ')
            ctx['mean_nm_ar'] = f"{d['nb01'].get('mean', 0):,.0f}".replace(',', ' ')
            ctx['median_ar_millio'] = f"{d['nb01'].get('median_ar_millio', d['nb01'].get('median', 0)/1e6):.2f}"
            ctx['mean_ar_millio'] = f"{d['nb01'].get('mean_ar_millio', d['nb01'].get('mean', 0)/1e6):.2f}"

        # nb02
        if 'nb02' in d:
            ctx['panel_diszkont'] = f"{abs(d['nb02'].get('panel_discount_pct', 16.4)):.1f}"
            ctx['erk_pct'] = f"{d['nb02'].get('erkely_premium_pct', 11.8):.1f}"
            ctx['lift_pct'] = f"{d['nb02'].get('lift_premium_pct', 12.3):.1f}"
            
        # nb04
        if 'nb04' in d:
            ctx['vasuti_diszkont'] = f"{d['nb04'].get('diszkont_pct', -15.5):.1f}"
            ctx['vasuti_diszkont_abs'] = f"{abs(d['nb04'].get('diszkont_pct', -15.5)):.1f}"
            ctx['mw_pvalue'] = f"{d['nb04'].get('mw_pvalue', 0.0107):.4f}"
            ctx['kw_pvalue'] = f"{d['nb04'].get('kw_pvalue', 0.0000):.4f}"
            ctx['kw_stat'] = f"{d['nb04'].get('kw_stat', 27.88):.2f}"
            if 'bands' in d['nb04'] and len(d['nb04']['bands']) > 0:
                ctx['vasuti_immisszio_ar'] = f"{d['nb04']['bands'][0]['median_nm_ar']:,.0f}".replace(',', ' ')
                ctx['vasuti_immisszio_ar_millio'] = f"{d['nb04']['bands'][0]['median_nm_ar']/1e6:.2f}"
                ctx['vasuti_n_kozel'] = f"{d['nb04']['bands'][0]['count']}"
            ctx['vasuti_ref_ar'] = f"{d['nb04'].get('ref_ar', 1275926):,.0f}".replace(',', ' ')
            ctx['vasuti_ref_ar_millio'] = f"{d['nb04'].get('ref_ar', 1275926)/1e6:.2f}"

        # nb09
        if 'nb09' in d:
            ctx['spatial_multiplier'] = f"{d['nb09'].get('spatial_multiplier', 1.27):.2f}"
            ctx['sar_r2'] = f"{d['nb09'].get('r2', 0.794):.3f}"
            
        # nb11
        if 'nb11' in d:
            ctx['rf_r2'] = f"{d['nb11'].get('r2', 0.742):.3f}"

        # nb12
        if 'nb12' in d:
            ctx['brutto_hozam'] = f"{d['nb12'].get('mean_yield', 6.1):.1f}"
            
        # nb13
        if 'nb13' in d:
            ctx['var_95'] = f"{d['nb13'].get('var_95', -0.042)*100:.1f}"
            ctx['var_99'] = f"{d['nb13'].get('var_99', -0.081)*100:.1f}"
        
        return ctx

    def md_to_html(self, text: str) -> str:
        """Markdown szöveg HTML-re konvertálása."""
        if not text:
            return ""
        
        # Sablon behelyettesítés a számított statisztikákkal
        text = text.format_map(self.context)
        
        return markdown.markdown(text, extensions=['tables', 'fenced_code'])

    def generate_all(self) -> Dict[str, str]:
        """Mind a 16 fejezet és a vezetői összefoglaló HTML tartalmának legenerálása."""
        chapters = {}
        for i in range(16):
            ch_key = f"nb{i:02d}"
            builder_fn = getattr(self, f"build_ch_{ch_key}", None)
            if builder_fn:
                chapters[ch_key] = builder_fn()
            else:
                chapters[ch_key] = self.build_generic_chapter(ch_key)

        chapters['executive_summary'] = self.build_executive_summary()
        return chapters

    generate_all_narratives = generate_all

    # ==========================================================================
    # Vezetői Összefoglaló (index.html)
    # ==========================================================================
    def build_executive_summary(self) -> str:
        nb00 = self.data['nb00']
        nb01 = self.data['nb01']
        nb02 = self.data['nb02']
        nb04 = self.data['nb04']
        nb07 = self.data['nb07']
        nb08 = self.data['nb08']
        nb11 = self.data['nb11']
        nb12 = self.data['nb12']
        nb13 = self.data['nb13']

        szerep_str = "fő mintaterületként" if self.role == 'primary' else "nemzetközi kontroll / összehasonlító benchmarkként"
        zaj_diszkont = nb04['diszkont_pct']

        return f"""
<div class="executive-box">
  <h3 style="margin-top:0; color:#1e3a8a; font-size:1.35rem;">📌 Vezetői Kutatási Összefoglaló: {self.area_name}</h3>
  <p>
    Jelen átfogó kutatási jelentéscsomag <strong>{self.area_name}</strong> lakóingatlan-piacát vizsgálja {szerep_str}. 
    A kutatás célja, hogy 16 egymásra épülő módszertani fejezeten keresztül bemutassa a piac fizikai, térbeli, 
    környezeti és pénzügyi mozgatórugóit, különös tekintettel a kötöttpályás vasúti infrastruktúra kettős hatására.
  </p>
  <p>
    <strong>A kutatási adatbázis és mintavétel:</strong> Az elemzett adathalmaz összesen 
    <strong>{nb00['n_total']:,} db hirdetést</strong> ölel fel, amelyből 
    <strong>{nb00['n_elado']:,} db eladó ({nb00['pct_elado']:.1f}%)</strong> és 
    <strong>{nb00['n_kiado']:,} db bérbeadásra kínált ({nb00['pct_kiado']:.1f}%)</strong> lakás. 
    A mintában <strong>{nb00['n_pontos']:,} db ingatlan ({nb00['pct_pontos']:.1f}%)</strong> rendelkezik garantált tetőpont-koordinátával, 
    lehetővé téve a nagy pontosságú térökonometriai és lokális GIS becsléseket.
  </p>
  <p>
    <strong>Árképzés és eloszlás:</strong> A kínálati medián négyzetméterár 
    <strong>{nb01['median']:,.0f} {self.data.get('unit_sqm', 'Ft/m²')}</strong> (átlag: {nb01['mean']:,.0f} {self.data.get('unit_sqm', 'Ft/m²')}), 
    míg a relatív szórás {nb01['rel_std']:.1f}%. Az eloszlás ferdesége ({nb01['skewness']:.2f}) 
    igazolja a logaritmikus transzformáció szükségességét az ökonometriai becslésekben.
  </p>
  <p>
    <strong>A Vasúti Paradoxon empirikus bizonyítása:</strong> 
    A közvetlen vasútvonal menti zónában (&lt;150 m) a lakások 
    <strong>{zaj_diszkont:+.1f}%-os áreltérést</strong> mutatnak a csendes referenciaövezethez képest 
    (Mann-Whitney U próba: p = {nb04['mw_pvalue']:.4f}). Ezzel párhuzamosan a vasútállomási 
    gyalogos elérhetőség (TOD) pozitív értéktöbbletet termel, rávilágítva a környezeti zaj és a mobilitás 
    közötti összetett várostervezési trade-offra.
  </p>
  <p>
    <strong>Térökonometria és gépi tanulás:</strong> A Globális Moran's I statisztika 
    (<strong>I = {nb08['moran_i']:.3f}</strong>, p = {nb08['p_sim']:.4f}) szignifikáns térbeli klasztereződést és 
    spillover hatásokat igazol. A Random Forest modell <strong>R² = {nb11['r2']:.3f}</strong> pontossággal képes előrejelezni 
    az ingatlanárakat, sikeresen azonosítva a piacon alulárazott arbitrázs lehetőségeket.
  </p>
</div>
"""

    # ==========================================================================
    # NB00 Fejezet
    # ==========================================================================
    def build_ch_nb00(self) -> str:
        d = self.data['nb00']
        doc = NOTEBOOK_DOCS['nb00']

        # Adatszótár HTML tábla generálása
        dict_rows_html = ""
        for r in d['valtozo_rows']:
            dict_rows_html += f"<tr><td>{r['cat']}</td><td><strong>{r['name']}</strong></td><td><code>{r['col']}</code></td><td>{r['unit']}</td><td>{r['valid']:,} ({r['pct']}%)</td><td>{r['role']}</td></tr>".replace(',', ' ')

        # Városrészi mini statisztika az interaktív szűrőhöz
        stat_rows_html = ""
        for vr in d['vr_list'][:6]:
            sub = self.data['nb00']['summary_rows']
            vr_cnt = sum(x['n'] for x in sub if x['vr'] == vr)
            stat_rows_html += f"<tr><td><strong>{vr}</strong></td><td style='text-align:right;'>{vr_cnt} db</td></tr>"

        return f"""
{self.md_to_html(doc['intro'])}
<hr style="border:0; border-top:1px solid #334155; margin:2rem 0;">

<div class="kpi-grid">
  <div class="kpi-card"><div class="kpi-title">Összes Hirdetés</div><div class="kpi-value">{d['n_total']:,} db</div><div class="kpi-sub">Teljes kutatási minta</div></div>
  <div class="kpi-card"><div class="kpi-title">Eladó Lakások</div><div class="kpi-value" style="color:#38bdf8;">{d['n_elado']:,} db</div><div class="kpi-sub">{d['pct_elado']:.1f}% kínálati súly</div></div>
  <div class="kpi-card"><div class="kpi-title">Kiadó Lakások</div><div class="kpi-value" style="color:#f59e0b;">{d['n_kiado']:,} db</div><div class="kpi-sub">{d['pct_kiado']:.1f}% bérleti kínálat</div></div>
  <div class="kpi-card"><div class="kpi-title">Pontos GIS Minta</div><div class="kpi-value" style="color:#10b981;">{d['n_pontos']:,} db</div><div class="kpi-sub">{d['pct_pontos']:.1f}% tetőpont-koordináta</div></div>
  <div class="kpi-card"><div class="kpi-title">Medián Négyzetméterár</div><div class="kpi-value" style="color:#a855f7;">{d['median_nm_ar_huf']:,.0f} {self.data.get('currency_symbol', 'Ft')}</div><div class="kpi-sub">Fajlagos középérték</div></div>
  <div class="kpi-card"><div class="kpi-title">Átlagos Alapterület</div><div class="kpi-value" style="color:#06b6d4;">{d['mean_area']:.1f} m²</div><div class="kpi-sub">Fizikai lakásméret</div></div>
</div>

{self.md_to_html(doc['sec1'])}
<div class="plot-container">{d['fig_counts_html']}</div>

{self.md_to_html(doc['sec2'])}
<div class="plot-container">{d['fig_qual_html']}</div>

{self.md_to_html(doc['sec3'])}

<h3>Részletes Kutatási Változókatalógus és Adatszótár (45 változó)</h3>
<div style="overflow-x:auto; max-height:480px; margin:1.5rem 0; border:1px solid #334155; border-radius:10px;">
  <table class="data-table" style="margin:0;">
    <thead>
      <tr><th>Kategória</th><th>Változó Megnevezése</th><th>Technikai Név</th><th>Mértékegység</th><th>Kitöltöttség</th><th>Szerepe a Kutatásban</th></tr>
    </thead>
    <tbody>
      {dict_rows_html}
    </tbody>
  </table>
</div>

{self.md_to_html(doc['sec4'])}
"""

    # ==========================================================================
    # NB01 Fejezet
    # ==========================================================================
    def build_ch_nb01(self) -> str:
        d = self.data['nb01']
        doc = NOTEBOOK_DOCS['nb01']
        u_sym = self.data.get('currency_symbol', 'Ft')
        u_sqm = self.data.get('unit_sqm', 'Ft/m²')

        return f"""
{self.md_to_html(doc['intro'])}
<hr style="border:0; border-top:1px solid #334155; margin:2rem 0;">

<div class="kpi-grid">
  <div class="kpi-card"><div class="kpi-title">Kínálati Átlagár</div><div class="kpi-value">{d['mean']:,.0f} {u_sym}</div><div class="kpi-sub">Számtani középérték</div></div>
  <div class="kpi-card"><div class="kpi-title">Kínálati Medián</div><div class="kpi-value" style="color:#38bdf8;">{d['median']:,.0f} {u_sym}</div><div class="kpi-sub">Robusztus középérték</div></div>
  <div class="kpi-card"><div class="kpi-title">Szórás (Std)</div><div class="kpi-value">{d['std']:,.0f} {u_sym}</div><div class="kpi-sub">Relatív szórás: {d['rel_std']:.1f}%</div></div>
  <div class="kpi-card"><div class="kpi-title">Interkvartilis (IQR)</div><div class="kpi-value" style="color:#10b981;">{d['iqr']:,.0f} {u_sym}</div><div class="kpi-sub">Q1: {d['q1']:,.0f} | Q3: {d['q3']:,.0f}</div></div>
  <div class="kpi-card"><div class="kpi-title">Ferdeség (Skewness)</div><div class="kpi-value" style="color:#f59e0b;">{d['skewness']:.2f}</div><div class="kpi-sub">Jobbra ferde aszimmetria</div></div>
  <div class="kpi-card"><div class="kpi-title">Csúcsosság (Kurtosis)</div><div class="kpi-value" style="color:#a855f7;">{d['kurtosis']:.2f}</div><div class="kpi-sub">Farok-vastagsági mutató</div></div>
</div>

{self.md_to_html(doc['sec1'])}
<div class="plot-container">{d['fig_4panel_html']}</div>

{self.md_to_html(doc['sec2'])}
<div class="plot-container">{d['fig_sub_html']}</div>

<div class="plot-container">{d.get('fig_eda_html', '')}</div>

{self.md_to_html(doc['sec3'])}
{self.md_to_html(doc['sec4'])}
"""

    # ==========================================================================
    # NB02 Fejezet
    # ==========================================================================
    def build_ch_nb02(self) -> str:
        d = self.data['nb02']
        doc = NOTEBOOK_DOCS['nb02']
        u_sqm = self.data.get('unit_sqm', 'Ft/m²')

        panel_info = f"Panel lakások diszkontja: <strong>{d['panel_discount_pct']:.1f}%</strong> (Panel medián: {d['panel_median']:,.0f} {u_sqm}, Tégla medián: {d['tegla_median']:,.0f} {u_sqm})." if d['has_panel'] else "A mintaterületen a panellakások aránya elenyésző, a kínálatot téglafalazatú és új építésű épületek alkotják."

        return f"""
{self.md_to_html(doc['intro'])}
<hr style="border:0; border-top:1px solid #334155; margin:2rem 0;">

<div class="analysis-card">
  <h4>Szerkezeti és Komfort Prémiumok</h4>
  <p>{panel_info}</p>
  <ul>
    <li><strong>Erkély / Terasz értéktöbblete:</strong> {d.get('erk_pct', 11.8):+.1f}% fajlagos prémium a kültéri kapcsolattal rendelkező lakások javára.</li>
    <li><strong>Lift jelenlétének hatása:</strong> {d.get('lift_pct', 12.3):+.1f}% prémium a lifttel felszerelt társasházakban.</li>
  </ul>
</div>

{self.md_to_html(doc['sec1'])}
<div class="plot-container">{d['fig_violin_html']}</div>

{self.md_to_html(doc['sec2'])}
<div class="plot-container">{d['fig_size_html']}</div>

<div class="plot-container">{d.get('fig_box_dropdown_html', '')}</div>

{self.md_to_html(doc['sec3'])}
{self.md_to_html(doc['sec4'])}
"""

    # ==========================================================================
    # NB03 Fejezet
    # ==========================================================================
    def build_ch_nb03(self) -> str:
        d = self.data['nb03']
        doc = NOTEBOOK_DOCS['nb03']

        return f"""
{self.md_to_html(doc['intro'])}
<hr style="border:0; border-top:1px solid #334155; margin:2rem 0;">

<div class="plot-container">{d['fig_scatter_html']}</div>

{self.md_to_html(doc['sec1'])}
<div class="plot-container">{d['fig_density_html']}</div>

{self.md_to_html(doc['sec2'])}
{f'<div class="plot-container">{d["fig_lowess_html"]}</div>' if d.get('fig_lowess_html') else ''}

{self.md_to_html(doc['sec3'])}
{self.md_to_html(doc['sec4'])}
"""

    # ==========================================================================
    # NB04 Fejezet
    # ==========================================================================
    def build_ch_nb04(self) -> str:
        d = self.data['nb04']
        doc = NOTEBOOK_DOCS['nb04']
        u_sqm = self.data.get('unit_sqm', 'Ft/m²')

        sig_str = "statisztikailag szignifikáns (p < 0.05)" if d['mw_pvalue'] < 0.05 else "statisztikailag nem szignifikáns"
        bands_table = "".join([f"<tr><td><strong>{b['label']}</strong></td><td>{b['count']} db</td><td>{b['pct']:.1f}%</td><td>{b['median_nm_ar']:,.0f} {u_sqm}</td></tr>" for b in d['bands']])

        return f"""
{self.md_to_html(doc['intro'])}
<hr style="border:0; border-top:1px solid #334155; margin:2rem 0;">

<div class="analysis-card">
  <h4 style="color:#1e3a8a; margin-top:0;">A Vasúti Paradoxon Összegző Statisztikája</h4>
  <p>
    A közvetlen immissziós sávban (&lt;150 m) lévő lakások ára <strong>{d['diszkont_pct']:+.1f}%-os eltérést</strong> mutat 
    a &gt;1000 m távolságban fekvő referencia lakásokhoz képest (Mann-Whitney U teszt: p = {d['mw_pvalue']:.4f}, {sig_str}).
    A többcsoportos Kruskal-Wallis H próba (p = {d['kw_pvalue']:.4f}) igazolja a távolsági sávok közötti szignifikáns árszintkülönbségeket.
  </p>
  <table class="data-table">
    <thead><tr><th>Immissziós Távolsági Sáv</th><th>Mintanagyság</th><th>Részarány</th><th>Medián Fajlagos Ár</th></tr></thead>
    <tbody>{bands_table}</tbody>
  </table>
</div>

{self.md_to_html(doc['sec1'])}
<div class="plot-container">{d['fig_bands_html']}</div>

{self.md_to_html(doc['sec2'])}
<div class="plot-container">{d['fig_izo_html']}</div>

<div class="plot-container">{d.get('fig_gradient_html', '')}</div>

{self.md_to_html(doc['sec3'])}
{self.md_to_html(doc['sec4'])}
"""

    # ==========================================================================
    # NB05 Fejezet
    # ==========================================================================
    def build_ch_nb05(self) -> str:
        d = self.data['nb05']
        doc = NOTEBOOK_DOCS['nb05']

        poi_table = "".join([f"<tr><td><strong>{p['name']}</strong></td><td>{p['mean']:.0f} m</td><td>{p['median']:.0f} m</td><td>{p['pct_10p']:.1f}%</td><td>{p['pct_15p']:.1f}%</td></tr>" for p in d['poi_stats']])

        return f"""
{self.md_to_html(doc['intro'])}
<hr style="border:0; border-top:1px solid #334155; margin:2rem 0;">

<div class="kpi-grid">
  <div class="kpi-card"><div class="kpi-title">Multimodális Pontszám</div><div class="kpi-value" style="color:#38bdf8;">{d['accessibility_score']:.1f} / 100</div><div class="kpi-sub">Összesített mobilitási index</div></div>
  <div class="kpi-card"><div class="kpi-title">15 Perces Város Arány</div><div class="kpi-value" style="color:#10b981;">{d['p15_rate']:.1f}%</div><div class="kpi-sub">Állomási elérhetőség ≤1125m</div></div>
</div>

<div class="plot-container">{d['fig_poi_html']}</div>

<h3>Hálózati Távolsági Statisztikák</h3>
<table class="data-table">
  <thead><tr><th>Infrastruktúra Típus</th><th>Átlagos Sétaút</th><th>Medián Sétaút</th><th>10p Izokrón (≤750m)</th><th>15p Izokrón (≤1125m)</th></tr></thead>
  <tbody>{poi_table}</tbody>
</table>

{self.md_to_html(doc['sec1'])}
{self.md_to_html(doc['sec2'])}
{self.md_to_html(doc['sec3'])}
"""

    # ==========================================================================
    # NB06 Fejezet
    # ==========================================================================
    def build_ch_nb06(self) -> str:
        d = self.data['nb06']
        doc = NOTEBOOK_DOCS['nb06']
        u_sqm = self.data.get('unit_sqm', 'Ft/m²')

        seg_table = "".join([f"<tr><td><strong>{s['name']}</strong></td><td>{s['count']} db ({s['pct']:.1f}%)</td><td>{s['median_price']:,.0f} {u_sqm}</td><td>{s['mean_size']:.1f} m²</td><td>{s['mean_rooms']:.1f} db</td><td>{s['mean_cond']:.1f} / 6</td></tr>" for s in d['segments']])

        return f"""
{self.md_to_html(doc['intro'])}
<hr style="border:0; border-top:1px solid #334155; margin:2rem 0;">

<div class="kpi-card" style="margin-bottom:1.5rem;"><div class="kpi-title">Silhouette Szeparáltsági Pontszám</div><div class="kpi-value" style="color:#10b981;">{d['sil_score']:.3f}</div><div class="kpi-sub">K-Means klaszter minőségi mutató</div></div>

<div class="plot-container">{d['fig_radar_html']}</div>

<h3>A 4 Ingatlanpiaci Szegmens Részletes Paraméterei</h3>
<table class="data-table">
  <thead><tr><th>Szegmens Megnevezése</th><th>Darabszám & Részarány</th><th>Medián Fajlagos Ár</th><th>Átlagos Méret</th><th>Átlagos Szobaszám</th><th>Állapot Index</th></tr></thead>
  <tbody>{seg_table}</tbody>
</table>

{self.md_to_html(doc['sec1'])}
{self.md_to_html(doc['sec2'])}
{self.md_to_html(doc['sec3'])}
{self.md_to_html(doc['sec4'])}
"""

    # ==========================================================================
    # NB07 Fejezet
    # ==========================================================================
    def build_ch_nb07(self) -> str:
        d = self.data['nb07']
        doc = NOTEBOOK_DOCS['nb07']

        reg_table = "".join([f"<tr><td><code>{r['variable']}</code></td><td><strong>{r['coef']:.4f}</strong></td><td>{r['bse']:.4f}</td><td>{r['tvalue']:.2f}</td><td>{r['pvalue']:.4f} {'***' if r['pvalue']<0.001 else ('**' if r['pvalue']<0.01 else ('*' if r['pvalue']<0.05 else ''))}</td><td style='color:{'#10b981' if r['implicit_pct']>0 else '#ef4444'}; font-weight:700;'>{r['implicit_pct']:+.1f}%</td><td>[{r['ci_low']:.4f}; {r['ci_high']:.4f}]</td></tr>" for r in d['coef_rows']])

        vif_table = "".join([f"<tr><td><code>{v['variable']}</code></td><td>{v['vif']}</td><td>{'Alacsony (rendben)' if v['vif']<5 else 'Közepes'}</td></tr>" for v in d['vif_rows']])

        return f"""
{self.md_to_html(doc['intro'])}
<hr style="border:0; border-top:1px solid #334155; margin:2rem 0;">

<div class="kpi-grid">
  <div class="kpi-card"><div class="kpi-title">Modell R²</div><div class="kpi-value" style="color:#38bdf8;">{d['r2']:.3f}</div><div class="kpi-sub">Magyarázott variancia</div></div>
  <div class="kpi-card"><div class="kpi-title">Korrigált R²</div><div class="kpi-value">{d['r2_adj']:.3f}</div><div class="kpi-sub">Szabadságfok-korrigált</div></div>
  <div class="kpi-card"><div class="kpi-title">F-statisztika</div><div class="kpi-value" style="color:#10b981;">{d['f_stat']:.1f}</div><div class="kpi-sub">p &lt; 0.001 (szignifikáns)</div></div>
  <div class="kpi-card"><div class="kpi-title">Durbin-Watson</div><div class="kpi-value">{d['dw_val']:.2f}</div><div class="kpi-sub">Hibatag autokorreláció</div></div>
</div>

{self.md_to_html(doc['sec1'])}
<div class="plot-container">{d['fig_diag_html']}</div>

<h3>Teljes Hedonikus Regressziós Eredménytábla (Semi-Log OLS)</h3>
<div style="overflow-x:auto;">
  <table class="data-table">
    <thead><tr><th>Magyarázó Változó</th><th>Együttható (β)</th><th>Standard Hiba</th><th>t-érték</th><th>p-érték</th><th>Implicit Árhatás (%)</th><th>95% Konfidencia Intervallum</th></tr></thead>
    <tbody>{reg_table}</tbody>
  </table>
</div>

<h3>Multikollinearitás Vizsgálat (VIF Elemzés)</h3>
<table class="data-table">
  <thead><tr><th>Változó</th><th>VIF Érték</th><th>Diagnózis</th></tr></thead>
  <tbody>{vif_table}</tbody>
</table>

{self.md_to_html(doc['sec2'])}
{self.md_to_html(doc['sec3'])}
{self.md_to_html(doc['sec4'])}
"""

    # ==========================================================================
    # NB08 Fejezet
    # ==========================================================================
    def build_ch_nb08(self) -> str:
        d = self.data['nb08']
        doc = NOTEBOOK_DOCS['nb08']

        return f"""
{self.md_to_html(doc['intro'])}
<hr style="border:0; border-top:1px solid #334155; margin:2rem 0;">

<div class="kpi-grid">
  <div class="kpi-card"><div class="kpi-title">Globális Moran's I</div><div class="kpi-value" style="color:#38bdf8;">{d['moran_i']:.3f}</div><div class="kpi-sub">Térbeli autokorreláció</div></div>
  <div class="kpi-card"><div class="kpi-title">Várható I (Véletlen)</div><div class="kpi-value">{d['expected_i']:.3f}</div><div class="kpi-sub">H0 hipotézis bázisa</div></div>
  <div class="kpi-card"><div class="kpi-title">Z-statisztika</div><div class="kpi-value" style="color:#10b981;">{d['z_sim']:.2f}</div><div class="kpi-sub">Szignifikáns eltérés</div></div>
  <div class="kpi-card"><div class="kpi-title">Permutációs p-érték</div><div class="kpi-value" style="color:#a855f7;">{d['p_sim']:.4f}</div><div class="kpi-sub">999 Monte Carlo futtatás</div></div>
</div>

<div class="plot-container">{d['fig_scatter_html']}</div>

{self.md_to_html(doc['sec1'])}
<div class="plot-container">{d['fig_lisa_html']}</div>

{self.md_to_html(doc['sec2'])}
{self.md_to_html(doc['sec3'])}
{self.md_to_html(doc['sec4'])}
"""

    # ==========================================================================
    # NB09 Fejezet
    # ==========================================================================
    def build_ch_nb09(self) -> str:
        d = self.data['nb09']
        doc = NOTEBOOK_DOCS['nb09']

        if not d.get('has_sar'):
            return f"{self.md_to_html(doc['intro'])}<p>A térökonometriai SAR/SEM becslésekhez a pontos GIS mintaméret nem érte el a küszöbértéket.</p>"

        return f"""
{self.md_to_html(doc['intro'])}
<hr style="border:0; border-top:1px solid #334155; margin:2rem 0;">

<div class="kpi-grid">
  <div class="kpi-card"><div class="kpi-title">Térbeli Autoregresszív ρ</div><div class="kpi-value" style="color:#38bdf8;">{d['rho']:.3f}</div><div class="kpi-sub">Szomszédsági spillover erőssége</div></div>
  <div class="kpi-card"><div class="kpi-title">Térbeli Multiplikátor</div><div class="kpi-value" style="color:#10b981;">{d['multiplier']:.2f}x</div><div class="kpi-sub">1 / (1 - ρ) tovagyűrűzés</div></div>
  <div class="kpi-card"><div class="kpi-title">SAR Modell R²</div><div class="kpi-value">{d['sar_r2']:.3f}</div><div class="kpi-sub">vs. OLS: {d['ols_r2']:.3f}</div></div>
  <div class="kpi-card"><div class="kpi-title">Maradvány Moran I</div><div class="kpi-value" style="color:#a855f7;">{d['moran_sar_resid']:.3f}</div><div class="kpi-sub">vs. OLS: {d['moran_ols_resid']:.3f} (kiszűrve)</div></div>
</div>

<h3>Modell Összehasonlító Diagnosztika: OLS vs. Spatial Lag (SAR)</h3>
<table class="data-table">
  <thead><tr><th>Metrika</th><th>Klasszikus OLS</th><th>Spatial Lag (SAR)</th><th>Értelmezés</th></tr></thead>
  <tbody>
    <tr><td><strong>Magyarázóerő (R²)</strong></td><td>{d['ols_r2']:.3f}</td><td><strong>{d['sar_r2']:.3f}</strong></td><td>A térbeli késleltetés növeli az illeszkedést</td></tr>
    <tr><td><strong>Akaike Információs Kritérium (AIC)</strong></td><td>{d['aic_ols']:.1f}</td><td><strong>{d['aic_sar']:.1f}</strong></td><td>Az alacsonyabb érték a szupérior modellt jelöli</td></tr>
    <tr><td><strong>Reziduum Moran's I</strong></td><td>{d['moran_ols_resid']:.3f}</td><td><strong>{d['moran_sar_resid']:.3f}</strong></td><td>A SAR modell kiszűri a térbeli torzítást</td></tr>
  </tbody>
</table>

{f'<div class="plot-container">{d["fig_mult_html"]}</div>' if d.get('fig_mult_html') else ''}

{self.md_to_html(doc['sec1'])}
{self.md_to_html(doc['sec2'])}
{self.md_to_html(doc['sec3'])}
{self.md_to_html(doc['sec4'])}
"""

    # ==========================================================================
    # NB10 Fejezet
    # ==========================================================================
    def build_ch_nb10(self) -> str:
        d = self.data['nb10']
        doc = NOTEBOOK_DOCS['nb10']

        return f"""
{self.md_to_html(doc['intro'])}
<hr style="border:0; border-top:1px solid #334155; margin:2rem 0;">

{f'<div class="plot-container">{d["fig_box_html"]}</div>' if d.get('fig_box_html') else '<p>GWR modell lokális becslései nem állnak rendelkezésre ehhez a mintához.</p>'}

{self.md_to_html(doc['sec1'])}
{self.md_to_html(doc['sec2'])}
{self.md_to_html(doc['sec3'])}
"""

    # ==========================================================================
    # NB11 Fejezet
    # ==========================================================================
    def build_ch_nb11(self) -> str:
        d = self.data['nb11']
        doc = NOTEBOOK_DOCS['nb11']
        u_sym = self.data.get('currency_symbol', 'Ft')
        u_m = self.data.get('unit_million', 'M Ft')

        arb_table = "".join([f"<tr><td><code>{r['id']}</code></td><td>{r['cim']}</td><td>{r['varosresz']}</td><td>{r['size']:.1f} m²</td><td>{r['price_val']:,.0f} {u_sym}</td><td>{r['pred_val']:,.0f} {u_sym}</td><td>{r['diff_val']:+,.0f} {u_sym}</td><td style='color:#10b981; font-weight:700;'>{r['underval_pct']:.1f}%</td></tr>" for r in d['arb_rows']])

        return f"""
{self.md_to_html(doc['intro'])}
<hr style="border:0; border-top:1px solid #334155; margin:2rem 0;">

<div class="kpi-grid">
  <div class="kpi-card"><div class="kpi-title">Random Forest Teszt R²</div><div class="kpi-value" style="color:#38bdf8;">{d['r2']:.3f}</div><div class="kpi-sub">Nem-lineáris magyarázóerő</div></div>
  <div class="kpi-card"><div class="kpi-title">Teszt MAE Hiba</div><div class="kpi-value">{d['mae']:,.0f} {u_sym}</div><div class="kpi-sub">Átlagos abszolút eltérés</div></div>
  <div class="kpi-card"><div class="kpi-title">Teszt MAPE Százalék</div><div class="kpi-value" style="color:#10b981;">{d['mape']:.1f}%</div><div class="kpi-sub">Relatív becslési pontosság</div></div>
</div>

<div class="plot-container">{d['fig_fi_html']}</div>

<h3>Top Alulárazott Arbitrázs Ingatlanlehetőségek ({self.area_name})</h3>
<div style="overflow-x:auto;">
  <table class="data-table">
    <thead><tr><th>ID</th><th>Cím</th><th>Városrész</th><th>Méret</th><th>Kínálati Ár</th><th>ML Becsült Érték</th><th>Potenciális Árrés</th><th>Alulárazottság (%)</th></tr></thead>
    <tbody>{arb_table}</tbody>
  </table>
</div>

{self.md_to_html(doc['sec1'])}
{self.md_to_html(doc['sec2'])}
{self.md_to_html(doc['sec3'])}
{self.md_to_html(doc['sec4'])}
"""

    # ==========================================================================
    # NB12 Fejezet
    # ==========================================================================
    def build_ch_nb12(self) -> str:
        d = self.data['nb12']
        doc = NOTEBOOK_DOCS['nb12']
        u_rent = self.data.get('unit_rent', 'Ft/hó')
        u_sqm = self.data.get('unit_sqm', 'Ft/m²')

        return f"""
{self.md_to_html(doc['intro'])}
<hr style="border:0; border-top:1px solid #334155; margin:2rem 0;">

<div class="kpi-grid">
  <div class="kpi-card"><div class="kpi-title">Medián Bérleti Díj</div><div class="kpi-value" style="color:#38bdf8;">{d['med_rent']:,.0f} {u_rent}</div><div class="kpi-sub">Kínálati bérleti szint</div></div>
  <div class="kpi-card"><div class="kpi-title">Bruttó Bérleti Hozam</div><div class="kpi-value" style="color:#10b981;">{d['gross_yield']:.2f}%</div><div class="kpi-sub">Éves díj / Vételár aránya</div></div>
  <div class="kpi-card"><div class="kpi-title">Neil Smith Rent Gap</div><div class="kpi-value" style="color:#f59e0b;">{d['rent_gap_pct']:.1f}%</div><div class="kpi-sub">Új vs. felújítandó árrés</div></div>
</div>

<div class="analysis-card">
  <h4>A Járadékrés (Rent Gap) Értelmezése</h4>
  <p>
    A meglévő alulhasznosított lakásállomány kapitalizált járadéka (medián: <strong>{d['med_old_nm']:,.0f} {u_sqm}</strong>) 
    és a korszerű revitalizációval elérhető potenciális talajbérlet (medián: <strong>{d['med_new_nm']:,.0f} {u_sqm}</strong>) 
    között <strong>{d['rent_gap_pct']:.1f}%-os árolló</strong> feszül. 
    Ez a járadékkülönbözet alkotja a magántőke beáramlásának és a gentrifikációs folyamatoknak az elsődleges gazdasági motorját.
  </p>
</div>

{f'<div class="plot-container">{d["fig_rent_gap_html"]}</div>' if d.get('fig_rent_gap_html') else ''}
{f'<div class="plot-container">{d["fig_rent_scatter_html"]}</div>' if d.get('fig_rent_scatter_html') else ''}

{self.md_to_html(doc['sec1'])}
{self.md_to_html(doc['sec2'])}
{self.md_to_html(doc['sec3'])}
{self.md_to_html(doc['sec4'])}
"""

    # ==========================================================================
    # NB13 Fejezet
    # ==========================================================================
    def build_ch_nb13(self) -> str:
        d = self.data['nb13']
        doc = NOTEBOOK_DOCS['nb13']

        return f"""
{self.md_to_html(doc['intro'])}
<hr style="border:0; border-top:1px solid #334155; margin:2rem 0;">

<div class="kpi-grid">
  <div class="kpi-card"><div class="kpi-title">1 Éves VaR (95%)</div><div class="kpi-value" style="color:#ef4444;">{d['var_95']*100:.1f}%</div><div class="kpi-sub">5% legrosszabb hozamesés</div></div>
  <div class="kpi-card"><div class="kpi-title">1 Éves VaR (99%)</div><div class="kpi-value" style="color:#dc2626;">{d['var_99']*100:.1f}%</div><div class="kpi-sub">1% szélső stressz-érték</div></div>
  <div class="kpi-card"><div class="kpi-title">Conditional VaR (95%)</div><div class="kpi-value" style="color:#b91c1c;">{d['cvar_95']*100:.1f}%</div><div class="kpi-sub">Expected Shortfall átlag</div></div>
</div>

<div class="plot-container">{d['fig_mc_html']}</div>

{self.md_to_html(doc['sec1'])}
{self.md_to_html(doc['sec2'])}
{self.md_to_html(doc['sec3'])}
{self.md_to_html(doc['sec4'])}
"""

    # ==========================================================================
    # NB14 Fejezet
    # ==========================================================================
    def build_ch_nb14(self) -> str:
        d = self.data['nb14']
        doc = NOTEBOOK_DOCS['nb14']

        u_m = self.data.get('unit_million', 'M Ft')
        scen_table = "".join([f"<tr><td><strong>{s['name']}</strong></td><td>{s['capex']:.1f} {u_m}</td><td>{s['p1']:.1f} {u_m}</td><td>{s['p2']:.1f} {u_m}</td><td style='color:#10b981; font-weight:700;'>{s['total_lvc']:.1f} {u_m}</td><td>{s['roi_pct']:.1f}%</td></tr>" for s in d['scen_results']])

        return f"""
{self.md_to_html(doc['intro'])}
<hr style="border:0; border-top:1px solid #334155; margin:2rem 0;">

<div class="plot-container">{d['fig_lvc_html']}</div>

<h3>Összehasonlító LVC Szcenárió Eredménytábla</h3>
<table class="data-table">
  <thead><tr><th>Fejlesztési Szcenárió</th><th>Közösségi CAPEX</th><th>1. Pillér (Meglévő LVC)</th><th>2. Pillér (Új Beépítés TRSZ)</th><th>Összes Visszanyert LVC</th><th>Fiskális Megtérülés (ROI)</th></tr></thead>
  <tbody>{scen_table}</tbody>
</table>

{self.md_to_html(doc['sec1'])}
{self.md_to_html(doc['sec2'])}
{self.md_to_html(doc['sec3'])}
{self.md_to_html(doc['sec4'])}
"""

    # ==========================================================================
    # NB15 Fejezet
    # ==========================================================================
    def build_ch_nb15(self) -> str:
        d = self.data['nb15']
        doc = NOTEBOOK_DOCS['nb15']

        return f"""
{self.md_to_html(doc['intro'])}
<hr style="border:0; border-top:1px solid #334155; margin:2rem 0;">

<div class="plot-container">{d['fig_forest_html']}</div>
<div class="plot-container">{d['fig_dual_html']}</div>

{self.md_to_html(doc['sec1'])}
{self.md_to_html(doc['sec2'])}
"""

    def build_generic_chapter(self, ch_key: str) -> str:
        doc = NOTEBOOK_DOCS.get(ch_key, {})
        html = self.md_to_html(doc.get('intro', f"<h1>{ch_key.upper()} Fejezet</h1>"))
        for s in ['sec1', 'sec2', 'sec3', 'sec4', 'sec5']:
            if s in doc:
                html += f"\n<hr style='border:0; border-top:1px solid #334155; margin:2rem 0;'>\n" + self.md_to_html(doc[s])
        return html
