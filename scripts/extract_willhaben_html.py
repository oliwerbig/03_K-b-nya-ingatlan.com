# -*- coding: utf-8 -*-
"""scripts/extract_willhaben_html.py — 2. réteg: willhaben.at HTML-ek kinyerése.

Források egy hirdetés-lapon belül:
  1. __NEXT_DATA__ JSON (props.pageProps.advertDetails) — a teljes strukturált
     attribútum-szótár; MINDEN {name: values} pár oszlop lesz (eredeti nevek,
     pl. ESTATE_SIZE/LIVING_AREA, BUILDING_TYPE, COORDINATES).
  2. Product JSON-LD (name, image, sku, offers).
  3. Leírás-szöveg — a pontos cím gyakran CSAK itt szerepel (pl. "Alliiertenstraße 13"),
     ezért innen is kinyerjük az utca/házszámot (szöveges fallback).

A kimenet KIZÁRÓLAG az eredeti adatforrás szerkezete — semmi levezetett érték.
Determinizmus: rendezett feldolgozás.
"""
import argparse
import io
import json
import os
import re
import sys

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _extract_utils import (  # noqa: E402
    build_inventory,
    list_html_files,
    load_manifest,
    manifest_date,
    parse_address_at,
    strip_html,
)

CORE_COLS = [
    "listing_id", "listing_type", "url", "cim_teljes", "iranyitoszam", "varos",
    "utca", "hazszam", "cim_minoseg", "leiras", "fenykepek_szama",
    "crawl_datuma", "forras_fajl", "seo_title", "published_date",
]


def extract_one(path, folder, manifest):
    fname = os.path.basename(path)
    out = {c: None for c in CORE_COLS}
    out["forras_fajl"] = fname
    out["crawl_datuma"] = manifest_date(manifest, fname)
    out["title"] = (manifest.get(fname, {}).get("title") or "").strip() or None

    with io.open(path, encoding="utf-8", errors="replace") as f:
        raw = f.read()
    if "Seite wurde nicht gefunden" in raw:
        out["oldal_allapot"] = "404"
    elif "advertDetails" in raw:
        out["oldal_allapot"] = "hirdetes"
    else:
        out["oldal_allapot"] = "egyeb"

    # --- 1) __NEXT_DATA__ ---
    ad = {}
    m = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', raw, re.S)
    if m:
        try:
            data = json.loads(m.group(1))
            ad = data.get("props", {}).get("pageProps", {}).get("advertDetails", {}) or {}
        except Exception:
            ad = {}

    attrs = {}
    attr_list = (ad.get("attributes") or {}).get("attribute", []) or []
    for a in attr_list:
        if isinstance(a, dict) and "name" in a:
            vals = a.get("values") or []
            attrs[a["name"]] = " || ".join(str(v) for v in vals if v is not None)
    for k, v in attrs.items():
        out[k] = v or None

    addr = ad.get("advertAddressDetails") or {}
    lines = ((addr.get("addressLines") or {}).get("value") or []) if isinstance(addr.get("addressLines"), dict) else []
    post_code = str(addr.get("postCode") or "").strip()
    city = (addr.get("municipality") or "Wien").strip()
    postal_name = ((addr.get("postalName") or "").strip()
                   or (lines[0] if lines else "")
                   or (attrs.get("LOCATION/ADDRESS_2") or "").strip()
                   or f"{post_code} Wien")

    # --- 2) Product JSON-LD ---
    pld = {}
    for mm in re.finditer(r'<script[^>]*application/ld\+json[^>]*>(.*?)</script>', raw, re.S):
        try:
            d = json.loads(mm.group(1))
            if isinstance(d, dict) and d.get("@type") == "Product":
                pld = d
                break
        except Exception:
            continue
    offers = pld.get("offers", {}) or {}

    out["listing_id"] = str(ad.get("id") or pld.get("sku") or os.path.splitext(fname)[0])
    out["url"] = pld.get("url") or ad.get("seoMetaData", {}).get("canonicalUrl")
    out["seo_title"] = (ad.get("seoMetaData") or {}).get("title")
    out["published_date"] = ad.get("publishedDate")
    out["iranyitoszam"] = post_code or None
    out["varos"] = city or None

    # --- 3) Leírás + szöveges címkinyerés ---
    # A pontos cím a hosszú DESCRIPTION / Lage attribútumban szerepel (a rövid
    # description mező csak kivonat) — a címet ezek UNIÓJÁBÓL keressük.
    desc_parts = [
        strip_html(ad.get("description") or ""),
        strip_html(attrs.get("DESCRIPTION") or ""),
        strip_html(attrs.get("GENERAL_TEXT_ADVERT/Lage") or ""),
    ]
    desc_full = " ".join(p for p in desc_parts if p)
    out["leiras"] = desc_full or None
    cim, zipc, city2, utca, hazszam, minoseg = parse_address_at(desc_full, postal_name, post_code)
    out["cim_teljes"] = cim or None
    out["iranyitoszam"] = out["iranyitoszam"] or (zipc or None)
    out["varos"] = out["varos"] or city2
    out["utca"] = utca or None
    out["hazszam"] = hazszam or None
    out["cim_minoseg"] = minoseg

    # --- 4) Fotók ---
    il = ad.get("advertImageList") or {}
    imgs = il.get("advertImage") or []
    out["fenykepek_szama"] = len(imgs) or None

    # --- listing_type: OWNAGETYPE (Kauf/Miete) -> a mappa csak fallback ---
    own = attrs.get("OWNAGETYPE", "")
    if re.search(r"\bMiete\b", own, re.I):
        out["listing_type"] = "kiado"
    elif re.search(r"\bKauf\b", own, re.I):
        out["listing_type"] = "elado"
    else:
        out["listing_type"] = folder

    n_fields = sum(1 for v in out.values() if v not in (None, "", 0))
    return out, f"ok:{n_fields}"


def main():
    ap = argparse.ArgumentParser(description="willhaben.at HTML -> 2. rétegű Excel")
    ap.add_argument("--raw-dir", required=True)
    ap.add_argument("--out-xlsx", required=True)
    ap.add_argument("--out-log", required=True)
    ap.add_argument("--out-inventory", required=True)
    args = ap.parse_args()

    manifest = load_manifest(args.raw_dir)
    files = list_html_files(args.raw_dir, manifest)
    rows, log = [], []
    for folder, path, fname in files:
        row, status = extract_one(path, folder, manifest)
        rows.append(row)
        log.append({"fajl": fname, "status": status,
                    "cim_minoseg": row.get("cim_minoseg", ""),
                    "listing_type": row.get("listing_type", "")})
    df = pd.DataFrame(rows)
    os.makedirs(os.path.dirname(args.out_xlsx), exist_ok=True)
    df.to_excel(args.out_xlsx, index=False)
    pd.DataFrame(log).to_csv(args.out_log, index=False, encoding="utf-8")
    pd.DataFrame(build_inventory(df)).to_csv(args.out_inventory, index=False, encoding="utf-8")
    print(f"[extract willhaben.at] {len(df)} hirdetés, {len(df.columns)} forrás-oszlop "
          f"-> {os.path.basename(args.out_xlsx)}")


if __name__ == "__main__":
    main()