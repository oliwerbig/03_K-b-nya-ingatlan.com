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


# Szöveges fájlok, amelyeknél a hash-számítás CRLF->LF normalizálással történik.
# (Windows checkouton CRLF, Linux CI-n LF van — így a hash platformfüggetlen.)
TEXT_EXTS = {".json", ".csv"}


def sha256(path):
    h = hashlib.sha256()
    ext = os.path.splitext(path)[1].lower()
    if ext in TEXT_EXTS:
        with open(path, "rb") as f:
            data = f.read()
        h.update(data.replace(b"\r\n", b"\n"))
        return h.hexdigest()
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
    check("kobanya garantált pontos == 295", int((kob["minta_garantalt_pontos"] == 1).sum()) == 295)

    # 2. Ár/alapterület integritás
    check("kobanya nincs hiányzó ár", int(kob["price_huf"].isna().sum()) == 0)
    check("kobanya nincs érvénytelen alapterület", int((kob["alapterulet_nm"] <= 0).sum()) == 0)

    # 3. Fizikai útvonal-integritás: kötöttpálya = min(metró, vasút, villamos)
    kp_cols = ["tavolsag_kotottpalya_halozati_m", "tavolsag_metro_halozati_m",
               "tavolsag_vasut_halozati_m", "tavolsag_villamos_halozati_m"]
    if set(kp_cols).issubset(kob.columns):
        m = kob.dropna(subset=kp_cols)
        min3 = m[["tavolsag_metro_halozati_m", "tavolsag_vasut_halozati_m",
                  "tavolsag_villamos_halozati_m"]].min(axis=1)
        bad = int(((m["tavolsag_kotottpalya_halozati_m"] - min3).abs() > 1.0).sum())
        check("kobanya kötöttpálya == min(metró, vasút, villamos)", bad == 0)
    # A hálózati sétatávolságok 0-tól indulnak és 1125 m felett is lehetnek
    if "tavolsag_vasut_halozati_m" in kob.columns:
        m = kob.dropna(subset=["tavolsag_vasut_halozati_m"])
        check("kobanya nincs negatív hálózati távolság", int((m["tavolsag_vasut_halozati_m"] < 0).sum()) == 0)

    # 4. Hedonikus logikai konzisztencia
    if {"korrigalt_alapterulet_nm", "alapterulet_nm"}.issubset(kob.columns):
        m = kob.dropna(subset=["korrigalt_alapterulet_nm", "alapterulet_nm"])
        bad = int((m["korrigalt_alapterulet_nm"] < m["alapterulet_nm"]).sum())
        check("kobanya korrigált < nettó alapterület == 0", bad == 0)
    if "epulet_kora_ev" in kob.columns:
        check("kobanya negatív épületkor == 0", int((kob["epulet_kora_ev"] < 0).sum()) == 0)

    # 5. Izokrón-hierarchia: 5p <= 10p <= 15p (a kánon szerint tranzitív dummyk)
    for prefix in ("vasut", "metro", "villamos", "busz", "park", "kotottpalya",
                   "iskola", "ovoda", "bolt", "gyogyszertar", "orvos"):
        c5, c10, c15 = f"{prefix}_5p_seta", f"{prefix}_10p_seta", f"{prefix}_15p_seta"
        if {c5, c10, c15}.issubset(kob.columns):
            m = kob.dropna(subset=[c5, c10, c15])
            bad = int(((m[c5] > m[c10]) | (m[c10] > m[c15])).sum())
            check(f"kobanya {prefix} izokrón-hierarchia == 0 hiba", bad == 0)

    # 6. Bécsi benchmark
    wien_path = _abs("data/processed/wien_nordbahnhof_szamitott_master.parquet")
    if os.path.exists(wien_path):
        w = pd.read_parquet(wien_path)
        check("wien összes rekord == 1037", len(w) == 1037)
        # A bécsi „pontos" kritérium az EGYEDI koordinátapár (a willhaben szórja a
        # koordinátákat — a megosztott pontok körzeti szintűek, lásd ADATKONYV).
        check(
            "wien garantált pontos == 324", int((w["minta_garantalt_pontos"] == 1).sum()) == 324
        )
        check(
            "wien panel-proxy == 68", int((w["is_panel"] == 1).sum()) == 68
        )
        for prefix in ("vasut", "metro", "villamos", "busz", "kotottpalya"):
            c5, c10, c15 = f"{prefix}_5p_seta", f"{prefix}_10p_seta", f"{prefix}_15p_seta"
            if {c5, c10, c15}.issubset(w.columns):
                m = w.dropna(subset=[c5, c10, c15])
                bad = int(((m[c5] > m[c10]) | (m[c10] > m[c15])).sum())
                check(f"wien {prefix} izokrón-hierarchia == 0 hiba", bad == 0)

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
