# -*- coding: utf-8 -*-
"""scripts/geocode_addresses.py v2 — cím-alapú geokódolás FALLBACK-LÁNCCAL.

Elv: a kanonikus pozíció KIZÁRÓLAG címből származik (a portál-koordináták soha
nem pontosak). Minden házszámos sorhoz a lehető legpontosabb, VALÓS adaton
alapuló pontot keresünk:

  1. Nominatim (alapkérdés + variánsok, limit=5 — a házszámos találat lehet a 2-3.)
  2. Photon (photon.komoot.io — ingyenes, kulcs nélküli OSM-alapú geokódoló)
  3. Overpass címadat: addr:housenumber node-ok/épületek + addr:interpolation
  4. LEGKÖZELEBBI HÁZSZÁM interpoláció: ha a cél-házszám nincs az OSM-ben, az
     ugyanazon utcán felvett, számszerűen legközelebbi házszám VALÓS épületpontja
     (pl. 9 → 12) — 'hazszam_interpolalt' pontossági osztály, dokumentált közelítés
  5. Ha az utcán egyetlen házszám sincs -> utcaszintű találat

Determinizmus: a sikeres találatok cache-elődnek; a SIKERTELEN (átmeneti hibás)
találatok NEM — újrafuttatáskor újrapróbálkoznak.
"""
import argparse
import io
import json
import math
import os
import re
import sys
import time
import unicodedata
import urllib.parse
import urllib.request

import numpy as np
import pandas as pd

try:
    from geopy.geocoders import Nominatim

    HAS_GEOPY = True
except ImportError:
    HAS_GEOPY = False

UA = {"User-Agent": "IFK-TDK-2026-Research/1.0 (educational research; contact: github.com/oliwerbig)"}
NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
PHOTON_URL = "https://photon.komoot.io/api/"
OVERPASS_ENDPOINTS = [
    "https://overpass-api.de/api/interpreter",
    "https://lz4.overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
]


def norm(s):
    """Normalizálás az utca-összevetéshez (ékezetmentes, kisbetűs)."""
    if not s:
        return ""
    nf = unicodedata.normalize("NFKD", str(s))
    t = "".join(c for c in nf if not unicodedata.combining(c)).lower()
    return re.sub(r"[^a-z0-9]+", " ", t).strip()


def _s(v):
    if v is None:
        return ""
    if isinstance(v, float) and np.isnan(v):
        return ""
    t = str(v).strip()
    return "" if t.lower() in ("nan", "none", "nincs") else t


def build_query(row):
    utca = _s(row.get("utca")).strip(" .")
    hazszam = _s(row.get("hazszam")).strip(" .")
    irsz = _s(row.get("iranyitoszam")).split(".")[0]
    varos = _s(row.get("varos"))
    teljes = _s(row.get("cim_teljes"))
    if hazszam and utca:
        return f"{hazszam} {utca}, {irsz} {varos}".strip(" ,"), "hazszam"
    if utca:
        return f"{utca}, {irsz} {varos}".strip(" ,"), "utca"
    if teljes:
        t = re.sub(r"^(Budapest\s+[IVXLC]+\.?\s*ker[^,]*,\s*)", "", teljes)
        return f"{t}, {varos}".strip(" ,"), "korzet"
    return "", "nincs"


def _get_json(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=25) as res:
        return json.loads(res.read().decode("utf-8"))


def _expected_country(q):
    """A kérdés szövege alapján az elvárt ország-kód (hu/at)."""
    if re.search(r"budapest|magyar|kerület|kerulet", q, re.I):
        return "hu"
    if re.search(r"wien|österreich|oesterreich|bezirk", q, re.I):
        return "at"
    return None


def nominatim_candidates(q):
    """Nominatim-találatok (limit=5, addressdetails), ország-validációval
    (a rossz országba ugró találatok — pl. az USA-beli „Wien” — kiesnek)."""
    out = []
    exp = _expected_country(q)
    for extra in ("", "&countrycodes=hu,at"):
        url = (NOMINATIM_URL + "?format=jsonv2&limit=5&addressdetails=1"
               + extra + "&q=" + urllib.parse.quote(q))
        try:
            for r in _get_json(url):
                a = r.get("address") or {}
                cc = (a.get("country_code") or "").lower()
                if exp and cc and cc != exp:
                    continue
                out.append({
                    "lat": float(r["lat"]), "lon": float(r["lon"]),
                    "hn": a.get("house_number"),
                    "road": a.get("road") or a.get("pedestrian") or a.get("square") or "",
                    "suburb": a.get("suburb") or a.get("city_district") or a.get("borough") or a.get("quarter") or "",
                    "display": r.get("display_name", ""),
                })
            break
        except Exception:
            time.sleep(1.5)
    return out


def photon_candidates(q):
    out = []
    exp = _expected_country(q)
    try:
        d = _get_json(PHOTON_URL + "?limit=5&q=" + urllib.parse.quote(q))
        for f in d.get("features", []):
            p = f.get("properties") or {}
            cc = (p.get("countrycode") or "").lower()
            if exp and cc and cc != exp:
                continue
            c = (f.get("geometry") or {}).get("coordinates") or [None, None]
            out.append({
                "lat": c[1], "lon": c[0],
                "hn": p.get("housenumber"),
                "road": p.get("street") or "",
                "suburb": p.get("district") or "",
                "display": p.get("name", ""),
            })
    except Exception:
        pass
    return out


def overpass_street_numbers(utca, irsz, lat, lon):
    """Az utca házszám-térképe az OSM-ből: [(szám, lat, lon), ...] + interpoláció-jel.
    Visszaad: (lista, volt-e találat)."""
    street_q = norm(utca).replace(" ", "|")
    if not street_q:
        return [], False
    q = ('[out:json][timeout:60];'
         f'(node["addr:housenumber"]["addr:street"~"{street_q}"](around:1200,{lat:.5f},{lon:.5f});'
         f' way["addr:housenumber"]["addr:street"~"{street_q}"](around:1200,{lat:.5f},{lon:.5f});'
         f' way["addr:interpolation"](around:1200,{lat:.5f},{lon:.5f}););'
         'out center 200;')
    for ep in OVERPASS_ENDPOINTS:
        try:
            d = _get_json(ep + "?data=" + urllib.parse.quote(q))
            nums = []
            has_interp = False
            for e in d.get("elements", []):
                tags = e.get("tags") or {}
                if "addr:interpolation" in tags:
                    has_interp = True
                    continue
                hn = tags.get("addr:housenumber")
                st = tags.get("addr:street") or ""
                if not hn or norm(st) != norm(utca):
                    continue
                c = e.get("center") or {}
                la, lo = (c.get("lat"), c.get("lon")) if c else (e.get("lat"), e.get("lon"))
                if la is None or lo is None:
                    continue
                m = re.search(r"\d+", hn)
                if m:
                    nums.append((int(m.group(0)), float(la), float(lo)))
            return nums, has_interp or len(nums) > 0
        except Exception:
            time.sleep(2.0)
    return [], False


def geocode_one(row, street_cache):
    """Egy sor geokódolása a fallback-lánccal. Vissza: rec dict + cache-frissítés."""
    q, level = build_query(row)
    utca = _s(row.get("utca")).strip(" .")
    hazszam = _s(row.get("hazszam")).strip(" .")
    irsz = _s(row.get("iranyitoszam")).split(".")[0]
    varos = _s(row.get("varos"))
    if not q:
        return {"lat": None, "lon": None, "precision": "nincs", "query": q, "display": None,
                "provider": None, "ref_hazszam": None, "suburb": None}, street_cache

    # --- 1-2) Nominatim + Photon ---
    target = None
    if hazszam:
        m = re.search(r"\d+", hazszam)
        target = int(m.group(0)) if m else None
    cands = nominatim_candidates(q) + photon_candidates(q)
    for c in cands:
        if c.get("hn"):
            c_hn = re.search(r"\d+", str(c["hn"]))
            if target is not None and c_hn and int(c_hn.group(0)) == target and c.get("lat"):
                return {"lat": c["lat"], "lon": c["lon"], "precision": "hazszam", "query": q,
                        "display": c["display"], "provider": "nominatim/photon",
                        "ref_hazszam": target, "suburb": c.get("suburb")}, street_cache
    street_point = next((c for c in cands if c.get("lat")), None)

    # --- 3-4) Overpass + legközelebbi házszám ---
    if target is not None and street_point:
        skey = f"{norm(utca)}|{irsz}"
        if skey in street_cache:
            nums, found = street_cache[skey]
        else:
            nums, found = overpass_street_numbers(utca, irsz, street_point["lat"], street_point["lon"])
            street_cache[skey] = (nums, found)
        if nums:
            exact = [n for n in nums if n[0] == target]
            pick = exact[0] if exact else min(nums, key=lambda n: abs(n[0] - target))
            if exact:
                return {"lat": pick[1], "lon": pick[2], "precision": "hazszam", "query": q,
                        "display": f"{target} {utca} (Overpass)", "provider": "overpass",
                        "ref_hazszam": target, "suburb": None}, street_cache
            return {"lat": pick[1], "lon": pick[2], "precision": "hazszam_interpolalt", "query": q,
                    "display": f"{target} {utca} (legközelebbi házszám: {pick[0]})", "provider": "overpass",
                    "ref_hazszam": pick[0], "suburb": None}, street_cache

    # --- 5) utca/korzet szint ---
    if street_point:
        return {"lat": street_point["lat"], "lon": street_point["lon"],
                "precision": level if level in ("utca", "korzet") else "utca",
                "query": q, "display": street_point["display"], "provider": "nominatim/photon",
                "ref_hazszam": None, "suburb": street_point.get("suburb")}, street_cache
    return {"lat": None, "lon": None, "precision": "nincs", "query": q, "display": None,
            "provider": None, "ref_hazszam": None, "suburb": None}, street_cache


def main():
    ap = argparse.ArgumentParser(description="Cím-alapú geokódolás fallback-lánccal")
    ap.add_argument("--extracted-xlsx", required=True)
    ap.add_argument("--cache-json", required=True)
    ap.add_argument("--user-agent", required=True)
    ap.add_argument("--rate-limit-s", type=float, default=1.1)
    ap.add_argument("--area-center", default=None, help="lat,lon — a cache szanitálásához")
    args = ap.parse_args()

    if not HAS_GEOPY:
        print("[HIBA] geopy nincs telepítve")
        return 2

    df = pd.read_excel(args.extracted_xlsx)
    cache = {}
    if os.path.exists(args.cache_json):
        with io.open(args.cache_json, encoding="utf-8") as f:
            cache = json.load(f)
    # a régi formátumú cache (lat=None bejegyzések) tisztítása — a sikertelenek újrapróbálódnak
    cache = {k: v for k, v in cache.items()
             if isinstance(v, dict) and v.get("lat") is not None}
    if args.area_center:
        _clat, _clon = [float(x) for x in args.area_center.split(",")]
        before = len(cache)
        cache = {k: v for k, v in cache.items()
                 if abs(v.get("lat", 999) - _clat) < 0.3 and abs(v.get("lon", 999) - _clon) < 0.4}
        if len(cache) != before:
            print(f"  [cache-szanitas] {before - len(cache)} rossz orszagba ugro talalat torolve", flush=True)
    street_cache = {k: (v.get("nums", []), v.get("found", False))
                    for k, v in cache.items() if k.startswith("street:")}
    cache = {k: v for k, v in cache.items() if not k.startswith("street:")}

    geolocator = Nominatim(user_agent=args.user_agent, timeout=12)
    rows = []
    n_haz, n_interp, n_utca, n_new = 0, 0, 0, 0
    for i, (_, r) in enumerate(df.iterrows(), 1):
        q, _ = build_query(r)
        if q in cache:
            rec = cache[q]
        else:
            time.sleep(args.rate_limit_s)
            rec, street_cache = geocode_one(r, street_cache)
            if rec.get("lat") is not None:
                cache[q] = rec
            n_new += 1
        rows.append({
            "listing_id": r.get("listing_id"),
            "cim_query": q,
            "geokodolt_lat": rec.get("lat"),
            "geokodolt_lon": rec.get("lon"),
            "geokodolas_pontossag": rec.get("precision"),
            "geokodolt_cim": rec.get("display"),
            "geokodolas_szolgaltato": rec.get("provider"),
            "felhasznalt_hazszam": rec.get("ref_hazszam"),
            "varosresz_geokodolt": rec.get("suburb"),
        })
        p = rec.get("precision")
        if p == "hazszam":
            n_haz += 1
        elif p == "hazszam_interpolalt":
            n_interp += 1
        elif p in ("utca", "korzet"):
            n_utca += 1
        if n_new and n_new % 50 == 0:
            for k, (nums, found) in street_cache.items():
                cache[f"street:{k}"] = {"nums": nums, "found": found}
            os.makedirs(os.path.dirname(args.cache_json), exist_ok=True)
            with io.open(args.cache_json, "w", encoding="utf-8") as _f:
                json.dump(cache, _f, ensure_ascii=False)
            print(f"  ... {i}/{len(df)} sor; cache mentve", flush=True)

    for k, (nums, found) in street_cache.items():
        cache[f"street:{k}"] = {"nums": nums, "found": found}
    os.makedirs(os.path.dirname(args.cache_json), exist_ok=True)
    with io.open(args.cache_json, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False)
    out_csv = args.cache_json.replace("_geocode_cache.json", "_geocode_eredmeny.csv")
    pd.DataFrame(rows).to_csv(out_csv, index=False, encoding="utf-8")
    print(f"[geocode] {len(rows)} sor | hazszam: {n_haz} | interpolalt: {n_interp} | "
          f"utca/korzet: {n_utca} | uj lekérdezés: {n_new}")


if __name__ == "__main__":
    main()