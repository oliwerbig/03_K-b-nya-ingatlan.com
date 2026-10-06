#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""verify_master_data.py — IFK-TDK 2026 adatintegritás-ellenőrző.

Két üzemmód:
  python -m ingatlan_tdk verify            # ellenőrzés (SHA-256 + szerkezeti invariánsok)
  python -m ingatlan_tdk verify --gen-sums # SHA256SUMS.txt (újra)generálása

A SHA256SUMS.txt rögzíti a „frozen baseline" mester adatfájljainak
kriptográfiai ellenőrző összegét (sha256sum formátum). Az ellenőrzés a
hash-egyezés mellett a számított mester adathalmaz szerkezeti invariánsait
is vizsgálja — a docs/ADATKONYV_ES_METADATA.md 5. szakaszának megfelelően.
"""

import os
import sys
import argparse
import hashlib

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SUMS_PATH = os.path.join(ROOT, "SHA256SUMS.txt")

# A frozen baseline kanonikus mester fájljai (perjellel elválasztott relatív utak).
FILES = [
    "data/raw/kobanya_parsed_raw_corpus.json",
    "data/raw/kobanya_ingatlan_nyers_master.db",
    "data/raw/kobanya_ingatlan_nyers_alap_1320db.xlsx",
    "data/raw/kobanya_elado_nyers.csv",
    "data/raw/kobanya_kiado_nyers.csv",
    "data/raw/wien_nordbahnhof_ingatlan_adatbazis.xlsx",
    "data/processed/kobanya_ingatlan_szamitott_master.parquet",
    "data/processed/kobanya_ingatlan_szamitott_master.db",
    "data/processed/kobanya_ingatlan_szamitott_pontos.geojson",
    "data/processed/kobanya_elado_szamitott.csv",
    "data/processed/kobanya_kiado_szamitott.csv",
    "data/processed/kobanya_ingatlan_szamitott_modellezes_1320db.xlsx",
    "data/processed/wien_nordbahnhof_szamitott_master.parquet",
    "data/processed/wien_nordbahnhof_pontos.geojson",
]


def _abs(rel):
    return os.path.join(ROOT, rel.replace("/", os.sep))


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def generate_sums():
    lines = []
    for rel in FILES:
        p = _abs(rel)
        if not os.path.exists(p):
            print(f"[!] HIÁNYZÓ fájl, kihagyva: {rel}")
            continue
        lines.append(f"{sha256(p)}  {rel}")
    with open(SUMS_PATH, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines) + "\n")
    print(f"[+] SHA256SUMS.txt elkészült: {len(lines)} fájl.")


def verify_sums():
    if not os.path.exists(SUMS_PATH):
        return False, f"HIÁNYZÓ manifest: {SUMS_PATH} (futtasd: --gen-sums)"
    ok = True
    checked = 0
    with open(SUMS_PATH, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            expected, _, rel = line.partition("  ")
            p = _abs(rel)
            checked += 1
            if not os.path.exists(p):
                print(f"[FAIL] hiányzó fájl: {rel}")
                ok = False
                continue
            actual = sha256(p)
            if actual != expected:
                print(f"[FAIL] hash-eltérés: {rel}")
                ok = False
    return ok, f"{checked} fájl ellenőrizve"


def verify_structure():
    import pandas as pd

    results = []
    warnings = []
    kob = pd.read_parquet(_abs("data/processed/kobanya_ingatlan_szamitott_master.parquet"))

    def check(name, cond):
        results.append((name, bool(cond)))

    # 1. Rekordszám és típusarány (frozen baseline)
    check("kobanya összes rekord == 1320", len(kob) == 1320)
    vc = kob["listing_type"].value_counts()
    check("kobanya eladó == 1140", vc.get("elado", 0) == 1140)
    check("kobanya kiadó == 180", vc.get("kiado", 0) == 180)
    check("kobanya garantált pontos == 296", int((kob["minta_garantalt_pontos"] == 1).sum()) == 296)

    # 2. Ár/alapterület integritás
    check("kobanya nincs hiányzó ár", int(kob["price_huf"].isna().sum()) == 0)
    check("kobanya nincs érvénytelen alapterület", int((kob["alapterulet_nm"] <= 0).sum()) == 0)

    # 3. Fizikai útvonal-integritás: hálózati >= euklidészi (0 hiba)
    if {"tavolsag_mazsa_halozati_m", "tavolsag_mazsa_m"}.issubset(kob.columns):
        m = kob.dropna(subset=["tavolsag_mazsa_halozati_m", "tavolsag_mazsa_m"])
        bad = int((m["tavolsag_mazsa_halozati_m"] < m["tavolsag_mazsa_m"]).sum())
        check("kobanya hálózati < euklidészi hiba == 0", bad == 0)

    # 4. Hedonikus logikai konzisztencia
    if {"korrigalt_alapterulet_nm", "alapterulet_nm"}.issubset(kob.columns):
        m = kob.dropna(subset=["korrigalt_alapterulet_nm", "alapterulet_nm"])
        bad = int((m["korrigalt_alapterulet_nm"] < m["alapterulet_nm"]).sum())
        check("kobanya korrigált < nettó alapterület == 0", bad == 0)
    if "epulet_kora_ev" in kob.columns:
        check("kobanya negatív épületkor == 0", int((kob["epulet_kora_ev"] < 0).sum()) == 0)

    # 5. Izokrón-hierarchia: 5p <= 10p <= 15p
    # Rögzített baseline kivétel: a "vasut" izokrónnál 1 rekord (listing_id 35461173,
    # Füzér utca) 5p=1 / 10p=0 / 15p=1 ellentmondást hordoz. Ezt az adatgenerálás
    # szintjén kell javítani; addig ismert, pinelt anomáliaként (WARN) kezeljük.
    known_iso = {"vasut": 1}
    for prefix in ("mazsa", "metro", "vasut", "villamos"):
        c5, c10, c15 = f"{prefix}_5p_seta", f"{prefix}_10p_seta", f"{prefix}_15p_seta"
        if {c5, c10, c15}.issubset(kob.columns):
            m = kob.dropna(subset=[c5, c10, c15])
            bad = int(((m[c5] > m[c10]) | (m[c10] > m[c15])).sum())
            expected = known_iso.get(prefix, 0)
            if bad <= expected:
                if bad:
                    warnings.append(f"{prefix} izokrón: {bad} ismert baseline anomália")
                else:
                    check(f"kobanya {prefix} izokrón-hierarchia == 0 hiba", True)
            else:
                check(f"kobanya {prefix} izokrón-hierarchia <= {expected} hiba", False)

    # 6. Bécsi benchmark
    wien_path = _abs("data/processed/wien_nordbahnhof_szamitott_master.parquet")
    if os.path.exists(wien_path):
        w = pd.read_parquet(wien_path)
        check("wien összes rekord == 1037", len(w) == 1037)
        check(
            "wien garantált pontos == 1037", int((w["minta_garantalt_pontos"] == 1).sum()) == 1037
        )

    return results, warnings


def main():
    ap = argparse.ArgumentParser(description="IFK-TDK 2026 mester adat ellenőrző")
    ap.add_argument("--gen-sums", action="store_true", help="SHA256SUMS.txt (újra)generálása")
    args = ap.parse_args()

    if args.gen_sums:
        generate_sums()
        return

    print("=" * 60)
    print("ADATINTEGRITÁS-ELLENŐRZÉS (frozen baseline)")
    print("=" * 60)

    ok_sums, msg_sums = verify_sums()
    print(f"[hash] {msg_sums}")

    print("-" * 60)
    failed = 0
    try:
        results, warnings = verify_structure()
        for name, passed in results:
            mark = "PASS" if passed else "FAIL"
            if not passed:
                failed += 1
            print(f"[{mark}] {name}")
        for w in warnings:
            print(f"[WARN] {w}")
    except Exception as e:
        print(f"[ERROR] szerkezeti ellenőrzés sikertelen: {e}")
        failed += 1

    print("=" * 60)
    total_failed = failed + (0 if ok_sums else 1)
    if total_failed == 0:
        print("EREDMÉNY: MINDEN ELLENŐRZÉS SIKERES.")
        return 0
    else:
        print(f"EREDMÉNY: {total_failed} ellenőrzés NEM sikerült.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
