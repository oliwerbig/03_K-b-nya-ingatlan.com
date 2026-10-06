# -*- coding: utf-8 -*-
"""
IFK-TDK 2026: Automatizált Területi Riport és Elemzés Generátor CLI.

Használat:
  python -m ingatlan_tdk report --area kobanya
  python -m ingatlan_tdk report --area wien_nordbahnhof
  python -m ingatlan_tdk report --all
"""

import os
import sys
import argparse
import time

from .report_engine import AreaAnalyzer, NarrativeGenerator, HTMLReportBuilder
from ._utils import list_available_areas

try:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass


def build_central_hub(all_area_results: dict, output_dir: str = "html_reports") -> str:
    """Központi többterületes navigációs portál (html_reports/index.html) összeállítása."""
    os.makedirs(output_dir, exist_ok=True)
    hub_path = os.path.join(output_dir, "index.html")

    area_cards = []
    table_rows = []

    for area_id, data in all_area_results.items():
        eda = data["eda"]
        rail = data["railway_paradox"]
        meta = data["metadata"]
        name = data["area_name"]
        role = data["role"]

        badge_cls = "badge-primary" if role == "primary" else "badge-control"
        badge_lbl = "Fő Mintaterület" if role == "primary" else "Nemzetközi Benchmark"

        diszkont = rail["diszkont_150_pct"]
        diszkont_col = "#ef4444" if diszkont < 0 else "#10b981"

        n_total_str = f"{eda['n_total']:,}".replace(",", " ")
        curr_sym = data.get("currency_symbol", "Ft")
        med_val = data["nb01"]["median"]
        med_str = f"{med_val:,.0f} {curr_sym}".replace(",", " ")
        if curr_sym == "€" or data.get("currency") == "EUR":
            med_sub_str = f"{med_val:,.0f} €"
        else:
            med_sub_str = f"{med_val:,.0f} Ft (~{med_val / 400.0:,.0f} €)"

        card = f"""
        <div class="area-card">
          <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.75rem;">
            <span class="badge {badge_cls}">{badge_lbl}</span>
            <span style="font-size:0.8rem; color:#64748b; font-weight:700;">ID: {area_id}</span>
          </div>
          <h3 style="font-size:1.35rem; margin-bottom:0.5rem; color:#ffffff;">{name}</h3>
          <p style="font-size:0.88rem; color:#94a3b8; min-height:45px; margin-bottom:1rem;">{meta.get("description", "")}</p>

          <div class="mini-kpi-grid">
            <div class="mini-kpi">
              <span class="lbl">Kínálat</span>
              <span class="val">{n_total_str} db</span>
            </div>
            <div class="mini-kpi">
              <span class="lbl">Medián Ár/m²</span>
              <span class="val" style="color:#38bdf8;">{med_str}</span>
            </div>
            <div class="mini-kpi">
              <span class="lbl">Vasúti Hatás</span>
              <span class="val" style="color:{diszkont_col};">{diszkont:+.1f}%</span>
            </div>
            <div class="mini-kpi">
              <span class="lbl">5p Állomás</span>
              <span class="val" style="color:#f59e0b;">{rail["isochrones"][0]["pct"]:.1f}%</span>
            </div>
          </div>

          <div style="margin-top:1.25rem;">
            <a href="{area_id}/index.html" class="btn-primary">📖 Riport Megnyitása &rarr;</a>
          </div>
        </div>
        """
        area_cards.append(card)

        # Összehasonlító tábla sora
        table_rows.append(f"""
        <tr>
          <td><strong>{name}</strong></td>
          <td><span class="badge {badge_cls}">{badge_lbl}</span></td>
          <td>{n_total_str} db</td>
          <td>{eda["pct_pontos"]:.1f}%</td>
          <td><strong>{med_sub_str}</strong></td>
          <td>{eda["mean_area"]:.1f} m²</td>
          <td style="color:{diszkont_col}; font-weight:700;">{diszkont:+.1f}%</td>
          <td>{rail["isochrones"][0]["pct"]:.1f}% ({rail["isochrones"][0]["count"]} db)</td>
          <td><a href="{area_id}/index.html" style="color:#38bdf8; text-decoration:none; font-weight:600;">Megtekintés &rarr;</a></td>
        </tr>
        """)

    html = f"""<!DOCTYPE html>
<html lang="hu">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>IFK-TDK 2026: Területalapú Ingatlanpiaci Riport Portál</title>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
  <style>
    :root {{
      --primary: #2563eb;
      --bg: #0b0f19;
      --card-bg: #151c2e;
      --card-border: #222f49;
      --text-main: #f8fafc;
      --text-muted: #94a3b8;
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: 'Inter', sans-serif;
      background-color: var(--bg);
      color: var(--text-main);
      padding: 2rem 1rem;
      line-height: 1.6;
    }}
    .container {{ max-width: 1240px; margin: 0 auto; }}
    header {{
      text-align: center;
      padding: 2.5rem 1rem;
      background: linear-gradient(180deg, rgba(37,99,235,0.15) 0%, rgba(15,23,42,0) 100%);
      border-radius: 16px;
      border: 1px solid var(--card-border);
      margin-bottom: 2.5rem;
    }}
    .badge {{
      padding: 0.25rem 0.65rem;
      border-radius: 999px;
      font-size: 0.72rem;
      font-weight: 700;
      text-transform: uppercase;
    }}
    .badge-primary {{ background: rgba(37,99,235,0.25); color: #60a5fa; border: 1px solid rgba(37,99,235,0.4); }}
    .badge-control {{ background: rgba(16,185,129,0.25); color: #34d399; border: 1px solid rgba(16,185,129,0.4); }}
    h1 {{ font-size: 2.4rem; font-weight: 800; margin-bottom: 0.75rem; }}
    p.sub {{ color: var(--text-muted); font-size: 1.1rem; max-width: 800px; margin: 0 auto; }}
    .grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(360px, 1fr));
      gap: 1.5rem;
      margin-bottom: 3rem;
    }}
    .area-card {{
      background: var(--card-bg);
      border: 1px solid var(--card-border);
      border-radius: 14px;
      padding: 1.75rem;
      box-shadow: 0 4px 14px rgba(0,0,0,0.25);
      display: flex;
      flex-direction: column;
      justify-content: space-between;
    }}
    .mini-kpi-grid {{
      display: grid;
      grid-template-columns: repeat(2, 1fr);
      gap: 0.75rem;
      background: rgba(0,0,0,0.2);
      padding: 0.85rem;
      border-radius: 10px;
      border: 1px solid rgba(255,255,255,0.05);
    }}
    .mini-kpi {{ display: flex; flex-direction: column; }}
    .mini-kpi .lbl {{ font-size: 0.72rem; color: #64748b; font-weight: 600; text-transform: uppercase; }}
    .mini-kpi .val {{ font-size: 1.15rem; font-weight: 800; color: #ffffff; margin-top: 2px; }}
    .btn-primary {{
      display: block;
      text-align: center;
      background: var(--primary);
      color: #ffffff;
      text-decoration: none;
      font-weight: 700;
      font-size: 0.92rem;
      padding: 0.65rem 1rem;
      border-radius: 8px;
      transition: background 0.2s;
    }}
    .btn-primary:hover {{ background: #1d4ed8; }}
    .comp-table {{
      width: 100%;
      border-collapse: collapse;
      margin-top: 1rem;
      font-size: 0.92rem;
      background: var(--card-bg);
      border-radius: 12px;
      overflow: hidden;
      border: 1px solid var(--card-border);
    }}
    .comp-table th, .comp-table td {{
      padding: 0.85rem 1rem;
      border-bottom: 1px solid var(--card-border);
      text-align: left;
    }}
    .comp-table th {{ background: rgba(255,255,255,0.04); color: #93c5fd; font-weight: 600; }}
    .comp-table tr:hover td {{ background: rgba(255,255,255,0.02); }}
    footer {{
      text-align: center;
      padding: 3rem 0 1rem 0;
      color: var(--text-muted);
      font-size: 0.85rem;
      border-top: 1px solid var(--card-border);
      margin-top: 3rem;
    }}
  </style>
</head>
<body>
<div class="container">
  <header>
    <div style="margin-bottom:0.75rem;">
      <span class="badge badge-primary">IFK-TDK 2026 Kutatási Keretrendszer</span>
    </div>
    <h1>Területalapú Ingatlanpiaci és Térökonometriai Riport Portál</h1>
    <p class="sub">Univerzális elemző notebookokból automatikusan generált interaktív HTML riportcsomagok és komparatív benchmarkok.</p>
  </header>

  <h2 style="font-size:1.5rem; margin-bottom:1.25rem; color:#ffffff;">📍 Elemzett Kutatási Területek</h2>
  <div class="grid">
    {"".join(area_cards)}
  </div>

  <h2 style="font-size:1.5rem; margin:2.5rem 0 1rem 0; color:#ffffff;">⚖️ Komparatív Területi Összehasonlító Táblázat</h2>
  <table class="comp-table">
    <thead>
      <tr>
        <th>Terület</th>
        <th>Szerepkör</th>
        <th>Minta</th>
        <th>GIS Pontosság</th>
        <th>Medián Ár / m²</th>
        <th>Átlag Méret</th>
        <th>Vasúti Hatás (&lt;150m)</th>
        <th>5p Állomáselérés</th>
        <th>Riport</th>
      </tr>
    </thead>
    <tbody>
      {"".join(table_rows)}
    </tbody>
  </table>

  <footer>
    <p>IFK-TDK 2026 Kutatási Keretrendszer | Automatizált Elemző és Riport Generátor Motor</p>
    <p style="font-size: 0.78rem; color: #64748b; margin-top: 4px;">Budapesti Műszaki és Gazdaságtudományi Egyetem</p>
  </footer>
</div>
</body>
</html>
"""

    with open(hub_path, "w", encoding="utf-8") as f:
        f.write(html)
    return hub_path


def generate_for_area(area_id: str, output_base_dir: str = "html_reports") -> dict:
    """Egy adott terület teljes riportgenerálásának végrehajtása."""
    t0 = time.time()
    print(f"\n{'=' * 70}")
    print(f"[>] RIPORT GENERALASA: [{area_id}]")
    print(f"{'=' * 70}")

    # 1. Analitikai modulok futtatása
    print("  [1/4] Adathalmaz feldolgozasa es analitikai modulok futtatasa...")
    analyzer = AreaAnalyzer(area_id)
    analysis_results = analyzer.run_all_analyses()
    print(
        f"        -> Mintameret: {analysis_results['eda']['n_total']:,} db hirdetes ({analysis_results['eda']['pct_pontos']:.1f}% pontos GIS).".replace(
            ",", " "
        )
    )
    curr_s = analysis_results.get("currency_symbol", "Ft")
    med_v = analysis_results["nb01"]["median"]
    print(f"        -> Median ar/m2: {med_v:,.0f} {curr_s}.".replace(",", " "))
    print(
        f"        -> Vasuti immisszios hatas (<150m): {analysis_results['railway_paradox']['diszkont_150_pct']:+.1f}%."
    )

    # 2. Szöveges értékelés és konklúziók generálása
    print("  [2/4] Tudomanyos narrativa es varostervezesi konkluziok szintezise...")
    narrative_gen = NarrativeGenerator(analysis_results)
    narratives = narrative_gen.generate_all_narratives()

    # 3. HTML fájlcsomag összeállítása
    print("  [3/4] HTML fajlcsomag generalasa es Plotly widgetek beagyazasa...")
    builder = HTMLReportBuilder(analysis_results, narratives, output_base_dir=output_base_dir)
    created_files = builder.build_all_reports()

    dt = time.time() - t0
    print(f"  [4/4] Sikeres generalas! ({len(created_files)} HTML fajl elkeszult, {dt:.1f}s)")
    for cf in created_files:
        print(f"        [OK] {cf}")
    print(f"{'=' * 70}\n")

    return analysis_results


def main():
    parser = argparse.ArgumentParser(
        description="IFK-TDK 2026 Automatizalt Teruleti Riport Generator"
    )
    parser.add_argument("--area", help="Celterulet azonositoja (pl. 'kobanya', 'wien_nordbahnhof')")
    parser.add_argument(
        "--all", action="store_true", help="Az osszes elerheto terulet feldolgozasa"
    )
    parser.add_argument("--output_dir", default="html_reports", help="Kimeneti HTML konyvtar")
    args = parser.parse_args()

    available = list_available_areas()

    target_areas = []
    if args.all:
        target_areas = [
            a
            for a in available
            if a in ["kobanya", "wien_nordbahnhof"]
            or os.path.exists(os.path.join("data", "processed", f"{a}_szamitott_master.parquet"))
        ]
    elif args.area:
        target_areas = [args.area.strip()]
    else:
        # Default: ha mindkettő megvan, mindkettőt generáljuk
        target_areas = ["kobanya", "wien_nordbahnhof"]

    all_results = {}
    for aid in target_areas:
        try:
            res = generate_for_area(aid, output_base_dir=args.output_dir)
            all_results[aid] = res
        except Exception as e:
            print(f"[!] Hiba a(z) '{aid}' terulet generalasakor: {e}")
            import traceback

            traceback.print_exc()

    # Központi portál (hub) generálása
    if all_results:
        hub_path = build_central_hub(all_results, output_dir=args.output_dir)
        print(f"\n[*] KOZPONTI PORTAL ELKESZULT: {hub_path}")


if __name__ == "__main__":
    main()
