#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""build_all.py — egybelépéses teljes csővezeték.

Sorrend: adatintegritás-ellenőrzés -> elemzés/narratíva/HTML -> ellenőrzés.

Használat:
  python build_all.py                # mindkét aktív terület (kobanya + wien)
  python build_all.py --area kobanya # csak egy terület
  python build_all.py --skip-verify  # integritás-ellenőrzés kihagyása
"""
import argparse
import subprocess
import sys


def main():
    ap = argparse.ArgumentParser(description="IFK-TDK 2026 teljes csővezeték")
    ap.add_argument("--area", help="Csak egy terület (pl. 'kobanya', 'wien_nordbahnhof')")
    ap.add_argument("--skip-verify", action="store_true", help="Integritás-ellenőrzés kihagyása")
    args = ap.parse_args()

    py = sys.executable

    steps = []
    if not args.skip_verify:
        steps.append(["verify_master_data.py"])

    gen = ["generate_area_report.py"]
    if args.area:
        gen += ["--area", args.area]
    else:
        gen += ["--all"]
    steps.append(gen)

    if not args.skip_verify:
        steps.append(["verify_master_data.py"])

    for step in steps:
        print(">>> " + " ".join([py] + step), flush=True)
        rc = subprocess.call([py] + step)
        if rc != 0:
            print(f"[!] A lépés sikertelen (exit {rc}): {' '.join(step)}")
            sys.exit(rc)

    print("[OK] Teljes csővezeték sikeresen lefutott.")


if __name__ == "__main__":
    main()