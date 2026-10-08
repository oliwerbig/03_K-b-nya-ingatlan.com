# -*- coding: utf-8 -*-
"""ingatlan_tdk.cli — konzolos belépési pontok.

  python -m ingatlan_tdk report --area <azonosito> | --all
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
    ap.add_argument("--area", help="Csak egy terület (a data/areas.yaml-ben regisztrált azonosító)")
    ap.add_argument("--all", action="store_true", help="Az összes elérhető terület")
    ap.add_argument("--output-dir", default="html_reports", help="Kimeneti könyvtár")
    ap.add_argument("--parallel", type=int, default=0,
                    help="Párhuzamos notebook-végrehajtás (alapértelmezés: CPU-magok - 1, max 6)")
    args = ap.parse_args()
    if args.parallel <= 0:
        import multiprocessing
        args.parallel = max(1, min(6, multiprocessing.cpu_count() - 1))
        # CI-n 2 magon ez 1 lenne — legalább 2-t hagyunk, a BLAS-szálak úgyis 1-re vannak fogva

    areas = list_available_areas()
    targets = [args.area] if args.area else areas
    if not targets:
        print("[!] Nincs elérhető terület (data/processed/*_szamitott_master.parquet).")
        return 1

    py = sys.executable
    notebooks_dir = os.path.join(ROOT, "notebooks")
    env = os.environ.copy()
    # CI-stabilizálás: a 2-magos runneren a párhuzamos BLAS/loky túlvállalás holtpontot okozhat
    env.setdefault("OMP_NUM_THREADS", "1")
    env.setdefault("OPENBLAS_NUM_THREADS", "1")
    env.setdefault("MKL_NUM_THREADS", "1")
    failures = 0

    def _execute(nb, out_dir, area=None):
        local = env.copy()
        if area:
            local["TDK_ACTIVE_AREA"] = area
        cmd = [
            py, "-m", "nbconvert", "--to", "html", "--execute", nb,
            "--output-dir", out_dir,
            "--ExecutePreprocessor.timeout=900",
            "--ExecutePreprocessor.kernel_name=python3",
        ]
        try:
            r = subprocess.run(cmd, env=local, timeout=1200, check=False)
        except subprocess.TimeoutExpired:
            print(f"  [!] IDŐTÚLLÉPÉS: {os.path.basename(nb)} (>1200 s)", flush=True)
            return False
        if r.returncode != 0:
            print(f"  [!] HIBA: {os.path.basename(nb)} (exit {r.returncode})", flush=True)
            return False
        return True

    # Tisztítás: az elavult korábbi riportok törlése a rebuild előtt
    # (a notebook-átnevezések/eltávolítások után nem maradhat holt oldal a Pages-en).
    import shutil
    for area in targets:
        shutil.rmtree(os.path.join(args.output_dir, area), ignore_errors=True)
    for _old in glob.glob(os.path.join(args.output_dir, "*.html")):
        os.remove(_old)

    from concurrent.futures import ThreadPoolExecutor, as_completed

    jobs = []
    for area in targets:
        out = os.path.join(args.output_dir, area)
        os.makedirs(out, exist_ok=True)
        print(f"=== RIPORT: [{area}] -> {out} (párhuzamos: {args.parallel}) ===", flush=True)
        for nb in sorted(glob.glob(os.path.join(notebooks_dir, "0[1-5]_*.ipynb"))):
            jobs.append((nb, out, area))

    # 06. komparatív notebook: egyszer, területfüggetlenül (legvégén)
    cmp = sorted(glob.glob(os.path.join(notebooks_dir, "06_*.ipynb")))

    if jobs:
        with ThreadPoolExecutor(max_workers=args.parallel) as pool:
            futures = {pool.submit(_execute, nb, out, area): nb
                       for nb, out, area in jobs}
            for fut in as_completed(futures):
                nb = futures[fut]
                ok = fut.result()
                print(f"  [{'OK ' if ok else 'HIBA'}] {os.path.basename(nb)}", flush=True)
                if not ok:
                    failures += 1

    if cmp:
        if not _execute(cmp[0], args.output_dir):
            failures += 1

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
<p>A riportok a kutatás <b>6 fejezetből álló logikai láncát</b> követik — minden számítás egyszer,
egy közös elemző modulban készül, a fejezetek egymásra épülnek:</p>
<ol style="color:#334155;line-height:1.7">
<li><b>Adatok és leíró statisztika</b> — megbízható-e az adat, és mit tudunk róla?</li>
<li><b>Térbeli mérések</b> — hogyan mérjük a vasutat (immissziós sávok, izokrónok, POI)?</li>
<li><b>Vasúti árhatás</b> — mekkora és hol a hatás (nyers → kontrollált → térbeli modellek)?</li>
<li><b>Robusztusság és következmények</b> — ML-ellenőrzés, rent gap, kockázat, felértékelődés.</li>
<li><b>Összefoglaló dashboard</b> — a számok egy helyen, interaktív galériával.</li>
<li><b>Területek összevetése</b> — pooled regresszió terület×sáv interakciókkal.</li>
</ol>
{cmp}
{"".join(cards)}
</body></html>"""
    with open(os.path.join(output_dir, "index.html"), "w", encoding="utf-8") as f:
        f.write(html)


def pipeline_main() -> int:
    """A 3-rétegű adatfolyam vezérlése: extract -> geocode -> canonize -> verify -> report.

    Determinizmus: rögzített fázissorrend, rendezett feldolgozás; a geokódolás
    a permanens cache-ből dolgozik (új címeket csak egyszer kérdez le).
    """
    import argparse
    import subprocess

    import yaml

    ap = argparse.ArgumentParser(description="3-rétegű adatfolyam (extract→geocode→canonize→verify→report)")
    ap.add_argument("--dataset", help="Csak egy adathalmaz")
    ap.add_argument("--all", action="store_true", help="Az összes regisztrált adathalmaz")
    ap.add_argument("--stage", nargs="+", choices=["extract", "geocode", "canonize", "verify", "report"],
                    default=["extract", "geocode", "canonize", "verify"],
                    help="Fázisok (alap: extract geocode canonize verify)")
    ap.add_argument("--skip-report", action="store_true", help="A riportgenerálás kihagyása")
    args = ap.parse_args()

    with open(os.path.join(ROOT, "data", "areas.yaml"), encoding="utf-8") as f:
        areas = yaml.safe_load(f)
    ids = list(areas["areas"].keys()) if args.all else ([args.dataset] if args.dataset else [areas.get("active_area") or next(iter(areas["areas"]))])
    if args.dataset:
        ids = [i for i in ids if i == args.dataset]
    if not ids:
        print("Nincs feldolgozandó adathalmaz.")
        return 2

    py = sys.executable
    scripts = os.path.join(ROOT, "scripts")
    geo_cfg = areas.get("geocoding", {})

    def run(cmd_list):
        print("  ->", " ".join(cmd_list))
        return subprocess.run(cmd_list, cwd=ROOT).returncode

    rc = 0
    for aid in ids:
        cfg = areas["areas"][aid]
        print(f"=== ADATHALMAZ: {aid} ({cfg['source']}) ===")
        if "extract" in args.stage:
            ext = os.path.join(scripts, f"{cfg['extractor']}.py")
            rc |= run([py, ext,
                       "--raw-dir", os.path.join(ROOT, cfg["data"]["raw_dir"]),
                       "--out-xlsx", os.path.join(ROOT, cfg["data"]["extracted_xlsx"]),
                       "--out-log", os.path.join(ROOT, cfg["data"]["extract_log"]),
                       "--out-inventory", os.path.join(ROOT, cfg["data"]["inventory"])])
        if "geocode" in args.stage:
            rc |= run([py, os.path.join(scripts, "geocode_addresses.py"),
                       "--extracted-xlsx", os.path.join(ROOT, cfg["data"]["extracted_xlsx"]),
                       "--cache-json", os.path.join(ROOT, geo_cfg["cache_dir"], f"{aid}_geocode_cache.json"),
                       "--user-agent", geo_cfg["user_agent"],
                       "--rate-limit-s", str(geo_cfg.get("rate_limit_s", 1.1))])
        if "canonize" in args.stage:
            rc |= run([py, "-m", "ingatlan_tdk", "canonize", "--dataset", aid])
        if "verify" in args.stage:
            rc |= run([py, "-m", "ingatlan_tdk", "verify", "--gen-sums"])
    if "report" in args.stage and not args.skip_report:
        rc |= run([py, "-m", "ingatlan_tdk", "report", "--all"])
    return rc


def canonize_main() -> int:
    """python -m ingatlan_tdk canonize --dataset X | --all — a 3. réteg generálása."""
    import argparse
    import subprocess

    ap = argparse.ArgumentParser(description="Kánonizálás (mapping + levezetések + export)")
    ap.add_argument("--dataset", help="Csak egy adathalmaz")
    ap.add_argument("--all", action="store_true")
    a = ap.parse_args()
    cmd = [sys.executable, os.path.join(ROOT, "scripts", "canonize_schema.py")]
    if a.all:
        cmd.append("--all")
    elif a.dataset:
        cmd += ["--dataset", a.dataset]
    return subprocess.run(cmd, cwd=ROOT).returncode


def main() -> int:
    a = sys.argv[1:]
    if not a or a[0] in ("-h", "--help"):
        print("Használat: python -m ingatlan_tdk {pipeline|report|verify|canonize} [opciók]")
        return 0 if a else 2
    cmd, rest = a[0], a[1:]
    if cmd == "report":
        fn = report_main
    elif cmd == "verify":
        fn = verify_main
    elif cmd == "pipeline":
        fn = pipeline_main
    elif cmd == "canonize":
        fn = canonize_main
    else:
        print(f"Ismeretlen parancs: {cmd} (pipeline|report|verify|canonize)")
        return 2
    sys.argv = [sys.argv[0]] + rest
    return fn() or 0


if __name__ == "__main__":
    sys.exit(main())