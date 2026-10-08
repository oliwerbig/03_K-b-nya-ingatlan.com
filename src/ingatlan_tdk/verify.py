#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""verify_master_data.py — IFK-TDK 2026 adatintegritás-ellenőrző (v2, invariáns-alapú).

Nincs beégetett darabszám és nincs beégetett területnév — minden ellenőrzés
a data/schema.yaml és a data/areas.yaml alapján, a friss processed kimenetekre.
A SHA256SUMS.txt a frozen baseline hash-manifest (--gen-sums-szal újragenerálható).
"""

import argparse
import hashlib
import os

import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SUMS_PATH = os.path.join(ROOT, "SHA256SUMS.txt")
TEXT_EXTS = {".json", ".csv", ".geojson"}


def load_cfg():
    with open(os.path.join(ROOT, "data", "areas.yaml"), encoding="utf-8") as f:
        areas = yaml.safe_load(f)
    with open(os.path.join(ROOT, "data", "schema.yaml"), encoding="utf-8") as f:
        schema = yaml.safe_load(f)
    return areas, schema


def tracked_files():
    """A verifikálandó fájlok az areas.yaml-ből (dinamikusan, semmi beégetés)."""
    areas, _ = load_cfg()
    files = []
    for aid, cfg in (areas.get("areas") or {}).items():
        for key in ("extracted_xlsx", "extract_log", "inventory",
                    "master_parquet", "human_xlsx", "pontos_geojson"):
            rel = (cfg.get("data") or {}).get(key)
            if rel:
                files.append(rel)
                if key == "pontos_geojson":
                    base, ext = os.path.splitext(rel)
                    files += [f"{base}_elado{ext}", f"{base}_kiado{ext}"]
    files.append("data/schema.yaml")
    files.append("data/areas.yaml")
    return sorted(set(files))


def _abs(rel):
    return os.path.join(ROOT, rel.replace("/", os.sep))


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
    for rel in tracked_files():
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
        return False, "HIÁNYZÓ manifest (futtasd: --gen-sums)"
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
            if sha256(p) != expected:
                print(f"[FAIL] hash-eltérés: {rel}")
                ok = False
    return ok, f"{checked} fájl ellenőrizve"


def verify_structure():
    import numpy as np
    import pandas as pd

    areas, schema = load_cfg()
    results = []

    def check(name, cond):
        results.append((name, bool(cond)))

    for aid, cfg in (areas.get("areas") or {}).items():
        parquet = _abs(cfg["data"]["master_parquet"])
        if not os.path.exists(parquet):
            results.append((f"{aid}: master parquet létezik", False))
            continue
        df = pd.read_parquet(parquet)
        tag = aid

        # séma-követés
        check(f"{tag}: minden required oszlop létezik", set(schema["required"]) <= set(df.columns))
        check(f"{tag}: nincs duplikált listing_id",
              int(df["listing_id"].duplicated().sum()) == 0)
        check(f"{tag}: listing_type ⊆ {elado, kiado}",
              set(df["listing_type"].dropna().unique()) <= {"elado", "kiado"})
        check(f"{tag}: nincs hiányzó ár", int(df["price_huf"].isna().sum()) == 0)
        check(f"{tag}: nincs érvénytelen (<=0) ár/alapterület",
              int(((df["price_huf"] <= 0) | (df["alapterulet_nm"] <= 0)).sum()) == 0)
        check(f"{tag}: korrigált >= nettó alapterület",
              int((df["korrigalt_alapterulet_nm"] < df["alapterulet_nm"]).sum()) == 0)
        check(f"{tag}: negatív épületkor == 0",
              int((df["epulet_kora_ev"] < 0).sum()) == 0)
        check(f"{tag}: minta_garantalt_pontos ∈ {0,1}",
              set(df["minta_garantalt_pontos"].dropna().unique()) <= {0, 1})
        check(f"{tag}: pontos ⇔ hazszam-szintű geokódolás",
              int(((df["minta_garantalt_pontos"] == 1) & (df["geokodolas_pontossag"] != "hazszam")).sum()) == 0)

        # dummy-k binárisak
        for c in df.columns:
            if c.startswith(("is_", "has_")) or c.endswith("_seta"):
                vals = df[c].dropna().unique()
                check(f"{tag}: {c} ∈ {{0,1}}", set(vals) <= {0, 1})

        # izokrón-hierarchia (5p <= 10p <= 15p)
        for prefix in ("vasut", "metro", "villamos", "busz", "park", "kotottpalya",
                       "iskola", "ovoda", "bolt", "gyogyszertar", "orvos"):
            c5, c10, c15 = f"{prefix}_5p_seta", f"{prefix}_10p_seta", f"{prefix}_15p_seta"
            if {c5, c10, c15}.issubset(df.columns):
                m = df.dropna(subset=[c5, c10, c15])
                bad = int(((m[c5] > m[c10]) | (m[c10] > m[c15])).sum())
                check(f"{tag}: {prefix} izokrón-hierarchia == 0 hiba", bad == 0)

        # kötöttpálya = min(metró, vasút, villamos)
        kp_cols = ["tavolsag_kotottpalya_halozati_m", "tavolsag_metro_halozati_m",
                   "tavolsag_vasut_halozati_m", "tavolsag_villamos_halozati_m"]
        if set(kp_cols).issubset(df.columns):
            m = df.dropna(subset=kp_cols)
            min3 = m[["tavolsag_metro_halozati_m", "tavolsag_vasut_halozati_m",
                      "tavolsag_villamos_halozati_m"]].min(axis=1)
            bad = int(((m["tavolsag_kotottpalya_halozati_m"] - min3).abs() > 1.0).sum())
            check(f"{tag}: kötöttpálya == min(3 mód)", bad == 0)
        if "tavolsag_vasut_halozati_m" in df.columns:
            check(f"{tag}: nincs negatív hálózati távolság",
                  int((df["tavolsag_vasut_halozati_m"].dropna() < 0).sum()) == 0)

        # statisztikai riport (a friss N-ek — nem ellenőrzés, csak kimutatás)
        print(f"  [{tag}] N={len(df)}, eladó={int((df['listing_type']=='elado').sum())}, "
              f"kiadó={int((df['listing_type']=='kiado').sum())}, "
              f"pontos={int((df['minta_garantalt_pontos']==1).sum())}")
    return results


def main():
    ap = argparse.ArgumentParser(description="Adatintegritás-ellenőrző (invariáns-alapú)")
    ap.add_argument("--gen-sums", action="store_true", help="SHA256SUMS.txt (újra)generálása")
    args = ap.parse_args()
    if args.gen_sums:
        generate_sums()
        return 0

    print("=" * 60)
    print("ADATINTEGRITÁS-ELLENŐRZÉS (sémavezérelt invariánsok)")
    print("=" * 60)
    ok_sums, msg_sums = verify_sums()
    print(f"[hash] {msg_sums}")
    print("-" * 60)
    failed = 0
    try:
        results = verify_structure()
        for name, passed in results:
            if not passed:
                failed += 1
            print(f"[{'PASS' if passed else 'FAIL'}] {name}")
    except Exception as e:
        print(f"[ERROR] szerkezeti ellenőrzés sikertelen: {e}")
        failed += 1
    print("=" * 60)
    total = failed + (0 if ok_sums else 1)
    print("EREDMÉNY: MINDEN ELLENŐRZÉS SIKERES." if total == 0 else f"EREDMÉNY: {total} ellenőrzés NEM sikerült.")
    return 1 if total else 0


if __name__ == "__main__":
    raise SystemExit(main())