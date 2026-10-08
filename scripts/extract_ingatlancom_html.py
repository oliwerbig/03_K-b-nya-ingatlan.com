# -*- coding: utf-8 -*-
"""scripts/extract_ingatlancom_html.py — 2. réteg: ingatlan.com HTML-ek kinyerése.

Források egy hirdetés-lapon belül:
  1. JSON-LD <script type="application/ld+json"> RealEstateListing — a strukturált mag
     (cím, koordináta NYERS mellékinformációként, szobák, m², építési év, ár, pénznem).
  2. Paraméter-táblázat (<tr><td>Label</td><td>Value</td></tr>) — az összes további
     jellemző, forrás-specifikus címkékkel (param_ előtaggal).
  3. Leírás-szöveg a "Leírás" fejléc után.

A kimenet KIZÁRÓLAG az eredeti adatforrás szerkezete — semmi levezetett érték.
A reklám-frame-ek (adverticum URL-ek) kimaradnak. Determinizmus: rendezett feldolgozás.
"""
import argparse
import io
import json
import os
import re
import sys

import pandas as pd
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _extract_utils import (  # noqa: E402
    build_inventory,
    is_ad_frame,
    list_html_files,
    load_manifest,
    manifest_date,
    parse_address_hu,
    sanitize_col,
    strip_html,
)

CORE_COLS = [
    "listing_id", "listing_type", "url", "cim_teljes", "iranyitoszam", "varos",
    "utca", "hazszam", "cim_minoseg", "lat_jsonld", "lon_jsonld", "szobak_szama",
    "alapterulet_nm", "epites_eve", "ar", "penznem", "leiras", "fenykepek_szama",
    "crawl_datuma", "forras_fajl",
]


def extract_one(path, folder, manifest):
    fname = os.path.basename(path)
    mrow = manifest.get(fname, {})
    url = mrow.get("url", "")
    out = {c: None for c in CORE_COLS}
    out["forras_fajl"] = fname
    out["crawl_datuma"] = manifest_date(manifest, fname)
    out["title"] = (mrow.get("title") or "").strip() or None
    if is_ad_frame(url):
        return None, "ad_frame"

    with io.open(path, encoding="utf-8", errors="replace") as f:
        raw = f.read()
    out["oldal_allapot"] = "hirdetes" if "RealEstateListing" in raw else "404"

    # --- 1) JSON-LD RealEstateListing ---
    jsonld = {}
    for m in re.finditer(r'<script[^>]*application/ld\+json[^>]*>(.*?)</script>', raw, re.S):
        try:
            d = json.loads(m.group(1))
            if isinstance(d, dict) and d.get("@type") == "RealEstateListing":
                jsonld = d
                break
        except Exception:
            continue

    me = jsonld.get("mainEntity", {}) or {}
    if not isinstance(me, dict):
        me = {}
    addr = me.get("address", {}) or {}
    geo = me.get("geo", {}) or {}
    offers = me.get("offers", {}) or {}
    size = me.get("floorSize", {}) or {}

    cim, zipc, city, utca, hazszam = parse_address_hu(
        addr.get("streetAddress") or jsonld.get("name") or "",
        addr.get("addressLocality") or "",
        addr.get("postalCode") or "",
    )
    out.update({
        "listing_id": str(jsonld.get("url", "")).rstrip("/").split("/")[-1] if jsonld.get("url") else mrow.get("id"),
        "url": jsonld.get("url") or url,
        "cim_teljes": cim or None,
        "iranyitoszam": zipc or None,
        "varos": city or None,
        "utca": utca or None,
        "hazszam": hazszam or None,
        "cim_minoseg": "strukturalt" if (utca and hazszam) else ("utca" if utca else "hianyzo"),
        "lat_jsonld": geo.get("latitude"),
        "lon_jsonld": geo.get("longitude"),
        "szobak_szama": me.get("numberOfRooms"),
        "alapterulet_nm": size.get("value") if isinstance(size, dict) else None,
        "epites_eve": me.get("yearBuilt"),
        "ar": (offers.get("price")
               or (offers.get("priceSpecification") or {}).get("price")) if isinstance(offers, dict) else None,
        "penznem": (offers.get("priceCurrency")
                    or (offers.get("priceSpecification") or {}).get("priceCurrency")) if isinstance(offers, dict) else None,
    })
    if not out["listing_id"]:
        out["listing_id"] = os.path.splitext(fname)[0]
    # listing_type a lap URL-jéből (a mappa csak fallback)
    lt_url = re.search(r"/(elado|kiado)", out["url"] or "")
    out["listing_type"] = lt_url.group(1) if lt_url else folder

    # --- 2) Paraméter-táblázat ---
    soup = BeautifulSoup(raw, "html.parser")
    params = {}
    for tr in soup.find_all("tr"):
        tds = tr.find_all("td")
        if len(tds) < 2:
            continue
        label = tds[0].get_text(" ", strip=True)
        val = tds[1].get_text(" ", strip=True)
        if label and len(label) <= 40:
            # minden címkét felveszünk, ütközésmentes param_ előtaggal
            col = "param_" + sanitize_col(label)
            if col in params and params[col] != val:
                params[col] = f"{params[col]} || {val}"
            else:
                params[col] = val
    for k, v in params.items():
        out[k] = v or None

    # --- 3) Leírás ---
    desc = ""
    h = soup.find(lambda t: t.name in ("h2", "h3", "div") and t.get_text(strip=True) == "Leírás")
    if h is not None:
        node = h.find_next_sibling()
        if node is not None:
            desc = strip_html(str(node))
    out["leiras"] = desc or None

    # --- 4) Fotók (beágyazott data:image képek) ---
    out["fenykepek_szama"] = len(re.findall(r"data:image/(?:png|jpe?g|webp);base64", raw)) or None

    n_fields = sum(1 for v in out.values() if v not in (None, "", 0))
    return out, f"ok:{n_fields}"


def main():
    ap = argparse.ArgumentParser(description="ingatlan.com HTML -> 2. rétegű Excel")
    ap.add_argument("--raw-dir", required=True)
    ap.add_argument("--out-xlsx", required=True)
    ap.add_argument("--out-log", required=True)
    ap.add_argument("--out-inventory", required=True)
    args = ap.parse_args()

    manifest = load_manifest(args.raw_dir)
    files = list_html_files(args.raw_dir)
    rows, log, skipped = [], [], 0
    for folder, path, fname in files:
        row, status = extract_one(path, folder, manifest)
        if row is None:
            skipped += 1
            log.append({"fajl": fname, "status": status})
            continue
        rows.append(row)
        log.append({"fajl": fname, "status": status,
                    "cim_minoseg": row.get("cim_minoseg", ""),
                    "listing_type": row.get("listing_type", "")})
    df = pd.DataFrame(rows)
    os.makedirs(os.path.dirname(args.out_xlsx), exist_ok=True)
    df.to_excel(args.out_xlsx, index=False)
    pd.DataFrame(log).to_csv(args.out_log, index=False, encoding="utf-8")
    pd.DataFrame(build_inventory(df)).to_csv(args.out_inventory, index=False, encoding="utf-8")
    print(f"[extract ingatlan.com] {len(df)} hirdetés, {skipped} kihagyott frame, "
          f"{len(df.columns)} forrás-oszlop -> {os.path.basename(args.out_xlsx)}")


if __name__ == "__main__":
    main()