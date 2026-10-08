# -*- coding: utf-8 -*-
"""scripts/geocode_addresses.py — CÍM-ALAPÚ geokódolás (Nominatim) permanens cache-szel.

KUTATÁSI ELV: a kanonikus pozíció KIZÁRÓLAG címből geokódolódik. A portálok által
megadott koordináták (ingatlan.com JSON-LD geo, willhaben COORDINATES) a magánszféra
védelme miatt szándékosan szórtak — SOHA nem tekintendők pontosnak, ezért az elemzési
pozíció nem belőlük származik.

Determinizmus: a cache (data/geocoding/<dataset>_geocode_cache.json) verziózott —
újrafuttatáskor a már kikódolt címek nem generálnak új hálózati kérést.
"""
import argparse
import io
import json
import os
import re
import sys
import time

import pandas as pd

try:
    from geopy.geocoders import Nominatim

    HAS_GEOPY = True
except ImportError:
    HAS_GEOPY = False

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")


def build_query(row):
    """Nominatim-kérdés a címmezőkből (pontosság szerint csökkenő sorrendben)."""
    utca = (str(row.get("utca") or "").strip())
    hazszam = (str(row.get("hazszam") or "").strip().strip("."))
    irsz = (str(row.get("iranyitoszam") or "").strip())
    varos = (str(row.get("varos") or "").strip())
    teljes = (str(row.get("cim_teljes") or "").strip())
    if hazszam and utca:
        return f"{hazszam} {utca}, {irsz} {varos}".strip(), "hazszam"
    if utca:
        return f"{utca}, {irsz} {varos}".strip(), "utca"
    if teljes:
        return teljes, "korzet"
    return "", "nincs"


def precision_of(raw_addr, query_level):
    """Pontossági osztály a Nominatim válaszából."""
    if not raw_addr:
        return "nincs"
    if query_level == "hazszam" and "house_number" in raw_addr:
        return "hazszam"
    if "road" in raw_addr or "pedestrian" in raw_addr or "footway" in raw_addr:
        return "utca"
    if "suburb" in raw_addr or "city_district" in raw_addr or "city" in raw_addr:
        return "korzet"
    return "nincs"


def main():
    ap = argparse.ArgumentParser(description="Cím-alapú geokódolás cache-sel")
    ap.add_argument("--extracted-xlsx", required=True)
    ap.add_argument("--cache-json", required=True)
    ap.add_argument("--user-agent", required=True)
    ap.add_argument("--rate-limit-s", type=float, default=1.1)
    args = ap.parse_args()

    if not HAS_GEOPY:
        print("[HIBA] geopy nincs telepítve")
        return 2

    df = pd.read_excel(args.extracted_xlsx)
    cache = {}
    if os.path.exists(args.cache_json):
        with io.open(args.cache_json, encoding="utf-8") as f:
            cache = json.load(f)

    geolocator = Nominatim(user_agent=args.user_agent, timeout=30)
    rows = []
    n_new, n_cached, n_skipped = 0, 0, 0
    for _, r in df.iterrows():
        q, level = build_query(r)
        if not q:
            n_skipped += 1
            continue
        if q in cache:
            rec = cache[q]
            n_cached += 1
        else:
            time.sleep(args.rate_limit_s)
            try:
                loc = geolocator.geocode(q, addressdetails=True, language="hu")
            except Exception:
                loc = None
                time.sleep(2.0)
                try:
                    loc = geolocator.geocode(q, addressdetails=True, language="hu")
                except Exception:
                    loc = None
            if loc is None:
                rec = {"lat": None, "lon": None, "precision": "nincs", "query": q, "display": None}
            else:
                raw = loc.raw or {}
                rec = {
                    "lat": loc.latitude,
                    "lon": loc.longitude,
                    "precision": precision_of(raw.get("address", {}), level),
                    "query": q,
                    "display": loc.address,
                }
            cache[q] = rec
            n_new += 1
        rows.append({
            "listing_id": r.get("listing_id"),
            "cim_query": q,
            "geokodolt_lat": rec.get("lat"),
            "geokodolt_lon": rec.get("lon"),
            "geokodolas_pontossag": rec.get("precision"),
            "geokodolt_cim": rec.get("display"),
        })

    os.makedirs(os.path.dirname(args.cache_json), exist_ok=True)
    with io.open(args.cache_json, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False, indent=1)
    out_csv = args.cache_json.replace("_geocode_cache.json", "_geocode_eredmeny.csv")
    pd.DataFrame(rows).to_csv(out_csv, index=False, encoding="utf-8")
    print(f"[geocode] {len(rows)} sor: {n_cached} cache-ből, {n_new} új lekérdezés, "
          f"{n_skipped} cím nélkül -> {os.path.basename(args.cache_json)}")


if __name__ == "__main__":
    main()