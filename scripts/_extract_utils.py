# -*- coding: utf-8 -*-
"""scripts/_extract_utils.py — közös segédek a 2. réteg (extracted) generálásához.

Irányelvek:
- A 2. réteg KIZÁRÓLAG az eredeti adatforrás szerkezetét tartalmazza (eredeti nevek),
  semmilyen levezetett/számított értéket.
- Determinizmus: a fájlokat rendezett sorrendben dolgozzuk fel; az outputokban
  nincs időbélyeg (a crawl-dátum a manifestből jön).
"""
import csv
import io
import os
import re
import unicodedata


def load_manifest(raw_dir):
    """Az index.csv manifest betöltése: {local_file: {id, title, url, ...}}.

    A manifest az almappákban él (elado/index.csv, kiado/index.csv). A scrapelt
    manifest fejléce és a sorok mezőszáma adathalmazonként eltérhet (a Bécsi
    manifest sorai 7 mezőt tartalmaznak, a fejléc 5 nevet) — ezért a mezőket
    TARTALOM alapján azonosítjuk: url = http-vel kezdődő érték, local_file =
    .html végű érték, download_timestamp = dátum-mintázatú érték."""
    out = {}
    for cand in [os.path.join(raw_dir, "index.csv"),
                 os.path.join(raw_dir, "elado", "index.csv"),
                 os.path.join(raw_dir, "kiado", "index.csv")]:
        if not os.path.exists(cand):
            continue
        _folder = os.path.basename(os.path.dirname(cand)) if "index.csv" in os.path.basename(cand) else os.path.basename(os.path.dirname(cand))
        with io.open(cand, encoding="utf-8", newline="") as f:
            for row in csv.DictReader(f):
                vals = []
                for k, v in row.items():
                    if k is None:
                        vals += list(v)
                    else:
                        vals.append(v)
                vals = [(str(v) if v is not None else "").strip() for v in vals]
                rid = vals[0] if vals else ""
                url = next((v for v in vals if v.startswith("http")), "")
                lf = next((v for v in vals if v.endswith(".html")), "")
                ts = next((v for v in vals if re.match(r"\d{4}-\d{2}-\d{2}", v)), "")
                title = vals[1] if len(vals) > 1 else ""
                fname = lf or f"{rid}.html"
                out[fname] = {"id": rid, "title": title, "url": url,
                              "local_file": fname, "download_timestamp": ts,
                              "folder": _folder}
    return out


def list_html_files(raw_dir, manifest=None):
    """Rendezett .html fájllista az elado/ és kiado/ almappákból.

    Ha manifest van megadva (index.csv), CSAK a manifestben szereplő fájlokat
    dolgozzuk fel — az elavult (pl. régi scrape-ből maradt 404-es) fájlok kiesnek."""
    files = []
    for sub in ("elado", "kiado"):
        d = os.path.join(raw_dir, sub)
        if os.path.isdir(d):
            for name in sorted(os.listdir(d)):
                if not name.lower().endswith(".html"):
                    continue
                if manifest is not None:
                    _m = manifest.get(name)
                    if _m is None:
                        continue
                    # a manifest almappája dönt (ugyanaz az id lehet mindkét mappában)
                    if _m.get("folder") and _m["folder"] not in ("", "elado", "kiado"):
                        pass
                    if _m.get("folder") in ("elado", "kiado") and _m["folder"] != sub:
                        continue
                files.append((sub, os.path.join(d, name), name))
    return files


def manifest_date(manifest, fname):
    """A crawl-dátum a manifest download_timestamp mezőjéből (YYYY-MM-DD)."""
    ts = (manifest.get(fname) or {}).get("download_timestamp", "")
    m = re.match(r"(\d{4}-\d{2}-\d{2})", ts)
    return m.group(1) if m else ""


def is_ad_frame(url):
    """Reklám-frame kiszűrése (adverticum stb. átirányítások)."""
    return bool(re.search(r"adverticum|adserv|doubleclick|googlesyndication", url or "", re.I))


def sanitize_col(name):
    """Oszlopnév-szanitizálás a forrás-címkékből (ékezetek MEGMARADNAK)."""
    n = unicodedata.normalize("NFKD", name)
    n = "".join(c for c in n if c.isalnum() or c in " _/.-")
    n = re.sub(r"\s+", "_", n).strip("_.")
    return n or "ismeretlen_mezo"


def strip_html(text):
    """HTML-tag eltávolítás + entitás-feloldás (leírásokhoz)."""
    if not text:
        return ""
    t = re.sub(r"<[^>]+>", " ", text)
    t = t.replace("&nbsp;", " ").replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
    t = re.sub(r"\s+", " ", t)
    return t.strip()


def parse_address_hu(street_address, locality="", postal_code=""):
    """Magyar cím felbontása utca/házszámra a strukturált címmezőből.
    Visszaad: (cim_teljes, iranyitoszam, varos, utca, hazszam)."""
    full = (street_address or "").strip()
    city = (locality or "").strip()
    zipc = (postal_code or "").strip()
    utca, hazszam = "", ""
    # a "Budapest X. kerület, " előtag levágása
    m = re.match(r"^(Budapest\s+[IVXLC]+\.?\s*ker[^,]*|Budapest|Debrecen|Szeged|Miskolc|Pécs|Győr)\s*,\s*(.*)$", full)
    if m:
        rest = m.group(2).strip()
    else:
        rest = full
    # utca + házszám a végén
    m2 = re.match(r"^(.*?)(?:(\d+[a-zA-Z]?(?:[/\-.]\d+)?)\s*\.?\s*)$", rest)
    if m2:
        utca = m2.group(1).strip(" ,.")
        hazszam = m2.group(2).strip(" .")
    else:
        utca = rest.strip(" ,.") if rest else ""
    if not city and full.startswith("Budapest"):
        city = "Budapest"
    return full, zipc, city, utca, hazszam


def parse_address_at(description, postal_name="", post_code=""):
    """Bécsi cím kinyerése a leírásból/szövegből (a willhaben a pontos címet
    nem adja strukturáltan — a szöveg a forrás). Visszaad:
    (cim_teljes, iranyitoszam, varos, utca, hazszam, minoseg)."""
    text = strip_html(description or "")
    pn = (postal_name or "").strip()
    zipc = (post_code or "").strip()
    city = "Wien"
    # konzervatív minta: <Utca-név> <házszám> (pl. "Alliiertenstraße 13", "Am Tabor 4-6")
    pat = re.compile(
        r"\b([A-ZÄÖÜ][\wäöüß]*(?:straße|strasse|gasse|platz|weg|allee|ring|kai|promenade|steig))"
        r"\s+(\d{1,4}[a-z]?(?:\s*[/-]\s*\d{1,4})?)",
        re.I,
    )
    m = pat.search(text)
    if m:
        utca = m.group(1).strip()
        hazszam = m.group(2).strip()
        full = f"{utca} {hazszam}, {zipc or '1020'} {city}" if zipc else f"{utca} {hazszam}, {city}"
        return full, zipc, city, utca, hazszam, "szoveges"
    return pn, zipc, city, "", "", "korzet"


def build_inventory(df):
    """Oszlop-inventár: név, típus, kitöltöttség, példaértékek (determinisztikus)."""
    rows = []
    for c in df.columns:
        s = df[c]
        nonnull = int(s.notna().sum())
        samples = [str(v) for v in s.dropna().unique()[:3]]
        rows.append({
            "oszlop": c,
            "tipus": str(s.dtype),
            "kitoltott": nonnull,
            "kitoltottseg_pct": round(100.0 * nonnull / max(1, len(df)), 1),
            "peldaertekek": " | ".join(samples)[:200],
        })
    return rows