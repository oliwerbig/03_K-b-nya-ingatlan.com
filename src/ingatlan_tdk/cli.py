# -*- coding: utf-8 -*-
"""ingatlan_tdk.cli — konzolos belépési pontok.

  python -m ingatlan_tdk report --area kobanya | --all
  python -m ingatlan_tdk verify [--gen-sums]
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def _chapter_title(filename):
    name = filename[len("00_"):-len(".ipynb")] if filename.startswith("0") else filename[:-len(".ipynb")]
    return name.replace("_", " ").capitalize()


def verify_main() -> int:
    from .verify import main

    return main()


def report_main() -> int:
    import argparse
    import glob
    import subprocess

    from ._utils import list_available_areas

    ap = argparse.ArgumentParser(description="Notebook-alapú területi riportgenerálás")
    ap.add_argument("--area", help="Csak egy terület (pl. 'kobanya', 'wien_nordbahnhof')")
    ap.add_argument("--all", action="store_true", help="Az összes elérhető terület")
    ap.add_argument("--output-dir", default="html_reports", help="Kimeneti könyvtár")
    args = ap.parse_args()

    areas = list_available_areas()
    targets = [args.area] if args.area else areas
    if not targets:
        print("[!] Nincs elérhető terület (data/processed/*_szamitott_master.parquet).")
        return 1

    py = sys.executable
    notebooks_dir = os.path.join(ROOT, "notebooks")
    env = os.environ.copy()
    failures = 0

    for area in targets:
        out = os.path.join(args.output_dir, area)
        os.makedirs(out, exist_ok=True)
        env["TDK_ACTIVE_AREA"] = area
        print(f"=== RIPORT: [{area}] -> {out} ===", flush=True)
        for i in range(16):
            matches = sorted(glob.glob(os.path.join(notebooks_dir, f"{i:02d}_*.ipynb")))
            if not matches:
                continue
            nb = matches[0]
            cmd = [py, "-m", "nbconvert", "--to", "html", "--execute", nb, "--output-dir", out]
            rc = subprocess.run(cmd, env=env).returncode
            if rc != 0:
                failures += 1
                print(f"  [!] Hiba: {os.path.basename(nb)} (exit {rc})", flush=True)

    # 16. komparatív notebook: egyszer, területfüggetlenül
    cmp = sorted(glob.glob(os.path.join(notebooks_dir, "16_*.ipynb")))
    if cmp:
        cmd = [py, "-m", "nbconvert", "--to", "html", "--execute", cmp[0], "--output-dir", args.output_dir]
        rc = subprocess.run(cmd).returncode
        if rc != 0:
            failures += 1
            print(f"  [!] Hiba: {os.path.basename(cmp[0])} (exit {rc})", flush=True)

    _build_index(args.output_dir, targets)
    print(f"[OK] Riportgenerálás kész (hibás notebook: {failures}).", flush=True)
    return 1 if failures else 0


def _build_index(output_dir: str, areas: list) -> None:
    from ._utils import get_area_metadata

    cards = []
    for area in areas:
        meta = get_area_metadata(area)
        name = meta.get("name", area)
        desc = meta.get("description", "")
        badge = "Fő mintaterület" if meta.get("role") == "primary" else "Kontroll / benchmark"
        a_dir = os.path.join(output_dir, area)
        items = []
        if os.path.isdir(a_dir):
            for f in sorted(os.listdir(a_dir)):
                if f.endswith(".html") and f != "index.html":
                    items.append(f'<li><a href="{area}/{f}">{_chapter_title(f)}</a></li>')
        cards.append(
            f'<section class="area"><h2>{name} <span class="badge">{badge}</span></h2>'
            f'<p class="desc">{desc}</p><ul class="chapters">{"".join(items)}</ul></section>'
        )
    cmp = ""
    if os.path.isdir(output_dir):
        for f in sorted(os.listdir(output_dir)):
            if f.startswith("16_") and f.endswith(".html"):
                cmp = f'<p><a href="{f}">Komparatív többterületes elemzés</a></p>'

    html = f"""<!DOCTYPE html>
<html lang="hu">
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>IFK-TDK 2026 — Területi riportok</title>
<style>
body{{font-family:system-ui,'Segoe UI',Roboto,sans-serif;max-width:900px;margin:2rem auto;padding:0 1rem;color:#1e293b;background:#f8fafc}}
h1{{color:#1e3a8a}} .badge{{background:#dbeafe;color:#1d4ed8;font-size:.75rem;padding:.2rem .6rem;border-radius:999px;vertical-align:middle}}
.area{{background:#fff;border:1px solid #e2e8f0;border-radius:12px;padding:1.2rem 1.5rem;margin:1.2rem 0}}
.desc{{color:#64748b;font-size:.9rem}} ul.chapters{{columns:2;list-style:none;padding:0}}
ul.chapters li{{margin:.25rem 0}} a{{color:#2563eb;text-decoration:none}} a:hover{{text-decoration:underline}}
</style></head>
<body>
<h1>🏘️ IFK-TDK 2026 — Területi ingatlanpiaci riportok</h1>
<p>A riportok a kutatási notebookok (00–16) futtatott exportjai, területenként. A vasúti infrastruktúra
ingatlanpiaci hatásának vizsgálatához készült elemzések.</p>
{cmp}
{"".join(cards)}
</body></html>"""
    with open(os.path.join(output_dir, "index.html"), "w", encoding="utf-8") as f:
        f.write(html)


def main() -> int:
    a = sys.argv[1:]
    if not a or a[0] in ("-h", "--help"):
        print("Használat: python -m ingatlan_tdk {report|verify} [opciók]")
        return 0 if a else 2
    cmd, rest = a[0], a[1:]
    if cmd == "report":
        fn = report_main
    elif cmd == "verify":
        fn = verify_main
    else:
        print(f"Ismeretlen parancs: {cmd} (report|verify)")
        return 2
    sys.argv = [sys.argv[0]] + rest
    return fn() or 0


if __name__ == "__main__":
    sys.exit(main())