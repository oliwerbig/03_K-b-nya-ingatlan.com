# -*- coding: utf-8 -*-
"""
report_engine/full_html_builder.py
16 fejezetes reszponzív HTML riportcsomagot és vezetői portált építő motor.
"""

import os
from typing import Dict, Any, List

CHAPTERS_META = [
    ("00_adathalmaz_attekintes", "00. Adathalmaz & Adatminőség", "nb00", "🗂️"),
    ("01_leiro_statisztika_es_eda", "01. Leíró Statisztika & EDA", "nb01", "📊"),
    ("02_arstruktura_es_szegmentacio", "02. Árstruktúra & Szegmentáció", "nb02", "🏢"),
    ("03_terbeli_elemzes_es_terkepek", "03. Térbeli Elemzés & GIS Térképek", "nb03", "🗺️"),
    ("04_vasuti_paradoxon_es_izokronok", "04. Vasúti Paradoxon & Izokrónok", "nb04", "🚆"),
    ("05_poi_es_15_perces_varos", "05. POI Ellátottság & 15p Város", "nb05", "🚶"),
    ("06_klaszter_es_tipologia", "06. Klaszteranalízis & Tipológiák", "nb06", "🧩"),
    ("07_hedonikus_armodell", "07. Hedonikus Ármodell (OLS)", "nb07", "📐"),
    ("08_moran_es_autokorrelacio", "08. Térbeli Autokorreláció & Moran", "nb08", "🌐"),
    ("09_terokonometria_sar_sem", "09. Térökonometria (SAR & SEM)", "nb09", "🔗"),
    ("10_lokalis_terokonometria_gwr", "10. Lokális Térökonometria (GWR)", "nb10", "📍"),
    ("11_gepi_tanulas_es_arbitrazs", "11. Gépi Tanulás & Arbitrázs", "nb11", "🤖"),
    ("12_berleti_piac_es_rent_gap", "12. Bérleti Piac & Rent Gap", "nb12", "🔑"),
    ("13_monte_carlo_kockazat", "13. Monte Carlo Kockázatelemzés", "nb13", "🎲"),
    ("14_lvc_szimulacio", "14. Közösségi Értékmegosztás (LVC)", "nb14", "🏛️"),
    ("15_ingatlan_kereso_dashboard", "15. Ingatlan Kereső Dashboard", "nb15", "🎯"),
]


class FullHTMLReportBuilder:
    """Teljes, 16 fejezetes HTML jelentéscsomagot összeállító és mentő osztály."""

    def __init__(
        self,
        analysis_data: Dict[str, Any],
        narratives: Dict[str, str],
        output_base_dir: str = "html_reports",
    ):
        self.data = analysis_data
        self.narratives = narratives
        self.area_id = analysis_data["area_id"]
        self.area_name = analysis_data["area_name"]
        self.short_name = analysis_data["short_name"]
        self.role = analysis_data["role"]
        self.out_dir = os.path.join(output_base_dir, self.area_id)
        self.chapters_dir = os.path.join(self.out_dir, "chapters")
        os.makedirs(self.chapters_dir, exist_ok=True)

    def get_base_css(self) -> str:
        return """
    :root {
      --primary: #2563eb;
      --primary-light: #60a5fa;
      --accent-green: #10b981;
      --accent-red: #ef4444;
      --accent-purple: #8b5cf6;
      --bg: #0b0f19;
      --card-bg: #151c2e;
      --card-border: #222f49;
      --text-main: #f8fafc;
      --text-muted: #94a3b8;
    }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
      background-color: var(--bg);
      color: var(--text-main);
      line-height: 1.65;
      padding: 1.5rem 1rem;
    }
    .container { max-width: 1260px; margin: 0 auto; }
    header {
      margin-bottom: 2rem;
      padding-bottom: 1.25rem;
      border-bottom: 1px solid var(--card-border);
    }
    .nav-bar {
      display: flex;
      flex-wrap: wrap;
      gap: 0.5rem;
      margin-bottom: 2rem;
      padding: 0.85rem;
      background: var(--card-bg);
      border-radius: 12px;
      border: 1px solid var(--card-border);
    }
    .nav-link {
      color: var(--text-muted);
      text-decoration: none;
      font-size: 0.82rem;
      font-weight: 600;
      padding: 0.4rem 0.75rem;
      border-radius: 8px;
      transition: all 0.15s;
    }
    .nav-link:hover, .nav-link.active {
      background: var(--primary);
      color: #ffffff;
    }
    .badge {
      display: inline-block;
      padding: 0.25rem 0.75rem;
      border-radius: 999px;
      font-size: 0.72rem;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      margin-bottom: 0.5rem;
    }
    .badge-primary { background: rgba(37,99,235,0.25); color: #60a5fa; border: 1px solid rgba(37,99,235,0.4); }
    .badge-control { background: rgba(16,185,129,0.25); color: #34d399; border: 1px solid rgba(16,185,129,0.4); }
    h1 { font-size: 2.1rem; font-weight: 800; margin-bottom: 0.5rem; color: #ffffff; }
    h2 { font-size: 1.5rem; font-weight: 700; margin: 2rem 0 1rem 0; color: #ffffff; border-bottom: 1px solid var(--card-border); padding-bottom: 0.5rem; }
    h3 { font-size: 1.2rem; font-weight: 600; margin: 1.5rem 0 0.75rem 0; color: #93c5fd; }
    p { color: #cbd5e1; margin-bottom: 1rem; font-size: 0.98rem; }
    ul, ol { margin: 0 0 1.25rem 1.5rem; color: #cbd5e1; }
    li { margin-bottom: 0.4rem; }
    .kpi-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
      gap: 1rem;
      margin: 1.5rem 0 2rem 0;
    }
    .kpi-card {
      background: var(--card-bg);
      border: 1px solid var(--card-border);
      border-radius: 12px;
      padding: 1.25rem 1rem;
      box-shadow: 0 2px 8px rgba(0,0,0,0.2);
    }
    .kpi-title { font-size: 0.75rem; font-weight: 700; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.05em; }
    .kpi-value { font-size: 1.65rem; font-weight: 800; color: #ffffff; margin: 0.3rem 0; }
    .kpi-sub { font-size: 0.78rem; color: #64748b; }
    .analysis-card {
      background: var(--card-bg);
      border: 1px solid var(--card-border);
      border-radius: 14px;
      padding: 1.75rem;
      margin: 1.5rem 0;
      box-shadow: 0 4px 12px rgba(0,0,0,0.2);
    }
    .executive-box {
      background: linear-gradient(135deg, rgba(30,58,138,0.25) 0%, rgba(15,23,42,0.6) 100%);
      border-left: 4px solid var(--primary);
      border-radius: 12px;
      padding: 1.5rem 1.75rem;
      margin: 1.5rem 0;
    }
    .data-table {
      width: 100%;
      border-collapse: collapse;
      margin: 1rem 0 1.5rem 0;
      font-size: 0.88rem;
    }
    .data-table th, .data-table td {
      padding: 0.75rem 0.9rem;
      text-align: left;
      border-bottom: 1px solid var(--card-border);
    }
    .data-table th { background: rgba(255,255,255,0.04); color: #93c5fd; font-weight: 600; }
    .data-table tr:hover td { background: rgba(255,255,255,0.02); }
    .plot-container {
      background: var(--card-bg);
      border: 1px solid var(--card-border);
      border-radius: 14px;
      padding: 1.25rem;
      margin: 1.5rem 0;
    }
    .chap-nav-footer {
      display: flex;
      justify-content: space-between;
      margin-top: 3rem;
      padding-top: 1.5rem;
      border-top: 1px solid var(--card-border);
    }
    .btn-nav {
      background: var(--card-bg);
      border: 1px solid var(--card-border);
      color: var(--text-main);
      text-decoration: none;
      padding: 0.65rem 1.25rem;
      border-radius: 8px;
      font-weight: 600;
      font-size: 0.9rem;
      transition: all 0.2s;
    }
    .btn-nav:hover { background: var(--primary); color: #ffffff; border-color: var(--primary); }
    footer {
      text-align: center;
      padding: 2.5rem 0 1.5rem 0;
      color: var(--text-muted);
      font-size: 0.82rem;
      border-top: 1px solid var(--card-border);
      margin-top: 3rem;
    }
"""

    def render_header(self, current_title: str, is_chapter: bool = False) -> str:
        role_badge = (
            '<span class="badge badge-primary">Fő Mintaterület</span>'
            if self.role == "primary"
            else '<span class="badge badge-control">Nemzetközi Benchmark / Kontroll</span>'
        )
        root_portal = "../../index.html" if is_chapter else "../index.html"
        return f"""
<header>
  <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:10px;">
    <div>
      {role_badge}
      <h1>{current_title}</h1>
      <p style="color:#94a3b8; font-size:0.95rem; margin:0;">{self.area_name} • IFK-TDK 2026 Kutatási Keretrendszer</p>
    </div>
    <div>
      <a href="{root_portal}" style="color:#38bdf8; text-decoration:none; font-weight:700; font-size:0.9rem; background:rgba(56,189,248,0.1); padding:6px 14px; border-radius:8px; border:1px solid rgba(56,189,248,0.3);">🌐 Területi Portál Kezdőlap</a>
    </div>
  </div>
</header>
"""

    def render_nav_bar(self, active_key: str, is_chapter: bool = False) -> str:
        prefix = "" if is_chapter else "chapters/"
        idx_href = "../index.html" if is_chapter else "index.html"

        links = [
            f'<a href="{idx_href}" class="nav-link {"active" if active_key == "index" else ""}">🏠 Vezetői Dashboard</a>'
        ]
        for fname, title, key, icon in CHAPTERS_META:
            act = "active" if active_key == key else ""
            href = f"{fname}.html" if is_chapter else f"{prefix}{fname}.html"
            links.append(f'<a href="{href}" class="nav-link {act}">{icon} {title}</a>')

        return f'<nav class="nav-bar">{"".join(links)}</nav>'

    def build_index_page(self) -> str:
        """A terület fő Vezetői Index összefoglalójának generálása."""
        exec_html = self.narratives.get("executive_summary", "")

        # 16 fejezet kártyarácsa
        cards_html = ""
        for fname, title, key, icon in CHAPTERS_META:
            cards_html += f"""
<div class="kpi-card" style="display:flex; flex-direction:column; justify-content:space-between;">
  <div>
    <div style="font-size:1.5rem; margin-bottom:6px;">{icon}</div>
    <div class="kpi-title">{title}</div>
  </div>
  <div style="margin-top:12px;">
    <a href="chapters/{fname}.html" class="btn-nav" style="display:block; text-align:center; padding:6px 10px; font-size:0.82rem;">Megnyitás &rarr;</a>
  </div>
</div>
"""

        nb00 = self.data["nb00"]
        nb01 = self.data["nb01"]
        nb04 = self.data["nb04"]
        nb11 = self.data["nb11"]

        n_total_str = f"{nb00['n_total']:,}".replace(",", " ")
        med_str = f"{nb01['median']:,.0f}".replace(",", " ")
        u_sqm = self.data.get("unit_sqm", "Ft/m²")

        content = f"""<!DOCTYPE html>
<html lang="hu">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Kutatási Jelentés: {self.area_name}</title>
  <script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.8/dist/katex.min.css">
  <script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.8/dist/katex.min.js"></script>
  <script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.8/dist/contrib/auto-render.min.js" onload="renderMathInElement(document.body, {{delimiters: [{{left: '$$', right: '$$', display: true}}, {{left: '$', right: '$', display: false}}], throwOnError: false, strict: false}});"></script>
  <style>{self.get_base_css()}</style>
</head>
<body>
<div class="container">
  {self.render_header(f"Vezetői Riport: {self.area_name}", is_chapter=False)}
  {self.render_nav_bar("index", is_chapter=False)}

  <div class="kpi-grid">
    <div class="kpi-card"><div class="kpi-title">Mintaelemszám</div><div class="kpi-value">{n_total_str} db</div><div class="kpi-sub">{nb00["pct_pontos"]:.1f}% pontos GIS</div></div>
    <div class="kpi-card"><div class="kpi-title">Kínálati Medián Ár</div><div class="kpi-value" style="color:#38bdf8;">{med_str} {u_sqm}</div><div class="kpi-sub">Fajlagos középérték</div></div>
    <div class="kpi-card"><div class="kpi-title">Vasúti Hatás (&lt;150m)</div><div class="kpi-value" style="color:{"#ef4444" if nb04["diszkont_pct"] < 0 else "#10b981"};">{nb04["diszkont_pct"]:+.1f}%</div><div class="kpi-sub">Immissziós eltérés</div></div>
    <div class="kpi-card"><div class="kpi-title">Random Forest R²</div><div class="kpi-value" style="color:#10b981;">{nb11["r2"]:.3f}</div><div class="kpi-sub">Gépi tanulási pontosság</div></div>
  </div>

  {exec_html}

  <h2>📚 Részletes Fejezetek és Elemző Modulok (00 - 15)</h2>
  <div class="kpi-grid" style="grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));">
    {cards_html}
  </div>

  <footer>
    <p>IFK-TDK 2026 Kutatási Keretrendszer | Automatizált Elemző és Riport Generátor Motor</p>
    <p style="font-size:0.75rem; color:#64748b; margin-top:4px;">Budapesti Műszaki és Gazdaságtudományi Egyetem</p>
  </footer>
</div>
</body>
</html>
"""

        idx_path = os.path.join(self.out_dir, "index.html")
        with open(idx_path, "w", encoding="utf-8") as f:
            f.write(content)
        return idx_path

    def build_all_chapters(self) -> List[str]:
        """Mind a 16 fejezet HTML állományának legenerálása."""
        created = [self.build_index_page()]

        for idx, (fname, title, key, icon) in enumerate(CHAPTERS_META):
            ch_html = self.narratives.get(key, f"<h1>{title}</h1><p>Fejezet előkészítés alatt.</p>")

            # Előző / Következő linkek
            prev_btn = ""
            if idx > 0:
                p_fname, p_title, _, _ = CHAPTERS_META[idx - 1]
                prev_btn = f'<a href="{p_fname}.html" class="btn-nav">&larr; Előző: {p_title}</a>'
            else:
                prev_btn = '<a href="../index.html" class="btn-nav">&larr; Vissza a Főoldalra</a>'

            next_btn = ""
            if idx < len(CHAPTERS_META) - 1:
                n_fname, n_title, _, _ = CHAPTERS_META[idx + 1]
                next_btn = (
                    f'<a href="{n_fname}.html" class="btn-nav">Következő: {n_title} &rarr;</a>'
                )
            else:
                next_btn = '<a href="../index.html" class="btn-nav">Vezetői Összefoglaló &rarr;</a>'

            page_code = f"""<!DOCTYPE html>
<html lang="hu">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title} | {self.area_name}</title>
  <script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.8/dist/katex.min.css">
  <script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.8/dist/katex.min.js"></script>
  <script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.8/dist/contrib/auto-render.min.js" onload="renderMathInElement(document.body, {{delimiters: [{{left: '$$', right: '$$', display: true}}, {{left: '$', right: '$', display: false}}], throwOnError: false, strict: false}});"></script>
  <style>{self.get_base_css()}</style>
</head>
<body>
<div class="container">
  {self.render_header(title, is_chapter=True)}
  {self.render_nav_bar(key, is_chapter=True)}

  <main>
    {ch_html}
  </main>

  <div class="chap-nav-footer">
    <div>{prev_btn}</div>
    <div>{next_btn}</div>
  </div>

  <footer>
    <p>IFK-TDK 2026 Kutatási Keretrendszer | Automatizált Elemző és Riport Generátor Motor</p>
    <p style="font-size:0.75rem; color:#64748b; margin-top:4px;">Budapesti Műszaki és Gazdaságtudományi Egyetem</p>
  </footer>
</div>
</body>
</html>
"""
            out_file = os.path.join(self.chapters_dir, f"{fname}.html")
            with open(out_file, "w", encoding="utf-8") as f:
                f.write(page_code)
            created.append(out_file)

        return created

    build_all_reports = build_all_chapters
