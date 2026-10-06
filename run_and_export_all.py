# -*- coding: utf-8 -*-
"""run_and_export_all.py
IFK-TDK 2026: Automatizált Notebook Végrehajtó és Területalapú HTML Exportáló

Használat:
  python run_and_export_all.py --area kobanya
  python run_and_export_all.py --area kontroll_1
"""

import os
import glob
import subprocess
import sys
import time
import argparse
import shutil

def main():
    parser = argparse.ArgumentParser(description="Notebookok futtatása és HTML exportálása területalapon")
    parser.add_argument("--area", default="kobanya", help="Célterület azonosítója (pl. 'kobanya', 'kontroll_1', 'kontroll_2')")
    parser.add_argument("--timeout", type=int, default=300, help="Maximális másodperc egy notebook futtatásához")
    args = parser.parse_args()

    area = args.area.strip()
    notebooks = sorted(glob.glob("notebooks/*.ipynb"))
    print(f"=== IFK-TDK 2026 Automatizált Export: [{area}] ===")
    print(f"Megtalált elemző notebookok száma: {len(notebooks)} db.")

    python_exe = sys.executable
    
    # Területalapú célkönyvtárak kialakítása
    area_docs_dir = os.path.join("docs", area)
    area_html_dir = os.path.join("html_exports", area)
    os.makedirs(area_docs_dir, exist_ok=True)
    os.makedirs(area_html_dir, exist_ok=True)

    # Környezeti változó az aktív terület átadásához
    env = os.environ.copy()
    env["TDK_ACTIVE_AREA"] = area

    start_total = time.time()

    for i, nb in enumerate(notebooks):
        nb_name = os.path.basename(nb)
        print(f"\n[{i+1}/{len(notebooks)}] Futtatás és exportálás: {nb_name} (Terület: {area})...")
        t0 = time.time()

        # 1. Notebook végrehajtása az aktív terület környezetével
        cmd_exec = [
            python_exe, "-m", "nbconvert",
            "--to", "notebook",
            "--execute",
            "--inplace",
            f"--ExecutePreprocessor.timeout={args.timeout}",
            nb
        ]
        res = subprocess.run(cmd_exec, capture_output=True, text=True, env=env)
        if res.returncode != 0:
            print(f"  [!] Hiba a(z) {nb_name} futtatásakor:")
            print(res.stderr[:400])
        else:
            print(f"  [+] Sikeres futás: {nb_name} ({time.time()-t0:.1f}s)")

        # 2. HTML exportálás a területi mappákba
        target_dirs = [area_docs_dir, area_html_dir]
        # Ha Kőbánya, tükrözzük a gyökér docs/ és html_exports/ alá is a visszafelé kompatibilitásért
        if area == "kobanya":
            target_dirs.extend(["docs", "html_exports"])

        for target_dir in set(target_dirs):
            os.makedirs(target_dir, exist_ok=True)
            html_filename = nb_name.replace(".ipynb", ".html")
            html_out = os.path.join(target_dir, html_filename)
            cmd_html = [
                python_exe, "-m", "nbconvert",
                "--to", "html",
                nb,
                "--output", html_filename,
                "--output-dir", target_dir
            ]
            res_html = subprocess.run(cmd_html, capture_output=True, text=True, env=env)
            if res_html.returncode == 0:
                print(f"  -> HTML elmentve: {html_out}")
            else:
                print(f"  [!] Hiba a HTML exportáláskor ({html_out}): {res_html.stderr[:300]}")

    print(f"\n==========================================")
    print(f"EXPORTÁLÁS BEFEJEZŐDÖTT: [{area}] ({time.time()-start_total:.1f}s)")
    print(f"Kimeneti könyvtár: {area_html_dir}")
    print(f"==========================================")

if __name__ == "__main__":
    main()
