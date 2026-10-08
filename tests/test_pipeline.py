# -*- coding: utf-8 -*-
"""tests/test_pipeline.py — a 3-rétegű adatfolyam determinizmus- és konzisztencia-tesztjei.

Fixture-alapú: apró, szintetikus HTML-ek a két adatforrás valós szerkezetével.
A tesztek SEMMILYEN konkrét adathalmaz-nevet vagy darabszámot nem tartalmaznak.
"""
import io
import os
import shutil
import sys

import pandas as pd
import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS = os.path.join(ROOT, "scripts")
sys.path.insert(0, SCRIPTS)
sys.path.insert(0, os.path.join(ROOT, "src"))

from _extract_utils import parse_address_hu, parse_address_at, strip_html  # noqa: E402
import extract_ingatlancom_html as ext_hu  # noqa: E402
import extract_willhaben_html as ext_at  # noqa: E402
from canonize_schema import apply_mapping, coerce, derive_core, load_schema, parse_number  # noqa: E402

INGATLAN_HTML = """<html><head>
<script type="application/ld+json">
{"@context":"https://schema.org","@type":"RealEstateListing",
 "name":"Budapest X. kerület, Gyógyszergyári utca 8.",
 "url":"https://ingatlan.com/x-ker/elado+lakas/tegla-lakas/35513622",
 "mainEntity":{"@type":"Apartment",
   "address":{"@type":"PostalAddress","streetAddress":"Budapest X. kerület, Gyógyszergyári utca 8.",
              "addressLocality":"Budapest","postalCode":"1106","addressCountry":"HU"},
   "geo":{"@type":"GeoCoordinates","latitude":47.49801,"longitude":19.142693},
   "numberOfRooms":3,
   "floorSize":{"@type":"QuantitativeValue","value":66,"unitCode":"MTK"},
   "yearBuilt":2026,
   "offers":{"@type":"Offer","price":89900000,"priceCurrency":"HUF"}}}
</script></head><body>
<table><tbody><tr><td><span>Ingatlan állapota</span></td><td>újszerű</td></tr>
<tr><td><span>Lift</span></td><td>van</td></tr>
<tr><td><span>Közös költség</span></td><td>3 000 Ft/hó</td></tr></tbody></table>
<h2>Leírás</h2><div>Próba leírás szöveg.</div>
</body></html>"""

WILLHABEN_HTML = """<html><head>
<script type="application/ld+json">
{"@context":"https://schema.org","@type":"Product","name":"Test 2-Zimmer","sku":"123456",
 "offers":{"@type":"Offer","price":"528900","priceCurrency":"EUR"}}
</script>
<script id="__NEXT_DATA__" type="application/json">
{"props":{"pageProps":{"advertDetails":{
 "id":"123456","description":"Wohnung in der Testgasse 13 im 2. Bezirk.",
 "advertAddressDetails":{"postCode":"1020","postalName":"Wien, 02. Bezirk, Leopoldstadt",
   "municipality":"Wien","addressLines":{"value":["Wien, 02. Bezirk, Leopoldstadt"]}},
 "attributes":{"attribute":[
   {"name":"NO_OF_ROOMS","values":["2"]},
   {"name":"ESTATE_SIZE/LIVING_AREA","values":["71,23"]},
   {"name":"BUILDING_TYPE","values":["Altbau"]},
   {"name":"OWNAGETYPE","values":["Kauf"]},
   {"name":"PRICE","values":["528900"]}]},
 "advertImageList":{"advertImage":[{"x":1},{"x":2}]}
}}}}
</script></head><body></body></html>"""


@pytest.fixture()
def hu_file(tmp_path):
    p = tmp_path / "elado" / "35513622.html"
    p.parent.mkdir(parents=True)
    p.write_text(INGATLAN_HTML, encoding="utf-8")
    return str(p)


@pytest.fixture()
def at_file(tmp_path):
    p = tmp_path / "elado" / "123456.html"
    p.parent.mkdir(parents=True)
    p.write_text(WILLHABEN_HTML, encoding="utf-8")
    return str(p)


# --- Egységtesztek a segédfüggvényekre ---

def test_parse_number():
    assert parse_number("3 000 Ft/hó") == 3000.0
    assert parse_number("71,23", decimal_comma=True) == 71.23
    assert parse_number("€ 528.900") == 528900.0
    assert pd.isna(parse_number("nincs megadva"))


def test_parse_address_hu():
    cim, zipc, city, utca, hazszam = parse_address_hu(
        "Budapest X. kerület, Gyógyszergyári utca 8.", "Budapest", "1106")
    assert utca == "Gyógyszergyári utca"
    assert hazszam == "8"
    assert zipc == "1106" and city == "Budapest"


def test_parse_address_at():
    cim, zipc, city, utca, hazszam, minoseg = parse_address_at(
        "Die Testgasse 13 befindet sich im 2. Bezirk.", "Wien, 02. Bezirk, Leopoldstadt", "1020")
    assert "Testgasse" in (utca or "")
    assert hazszam == "13"
    assert minoseg == "szoveges"


# --- Extractor-determinizmus ---

def test_ingatlancom_extract_and_determinism(hu_file):
    r1, _ = ext_hu.extract_one(hu_file, "elado", {})
    r2, _ = ext_hu.extract_one(hu_file, "elado", {})
    assert r1 == r2
    assert r1["listing_id"] == "35513622"
    assert r1["listing_type"] == "elado"
    assert r1["hazszam"] == "8"
    assert r1["alapterulet_nm"] == 66
    assert r1["param_Ingatlan_allapota"] == "újszerű"
    assert r1["param_Kozos_koltseg"] == "3 000 Ft/hó"


def test_willhaben_extract_and_determinism(at_file):
    r1, _ = ext_at.extract_one(at_file, "elado", {})
    r2, _ = ext_at.extract_one(at_file, "elado", {})
    assert r1 == r2
    assert r1["listing_id"] == "123456"
    assert r1["listing_type"] == "elado"
    assert r1["NO_OF_ROOMS"] == "2"
    assert r1["BUILDING_TYPE"] == "Altbau"
    assert r1["fenykepek_szama"] == 2
    assert "Testgasse" in (r1["utca"] or "")


# --- Mapping + séma konzisztencia ---

def test_mapping_targets_exist_in_schema():
    import glob
    import yaml

    schema = load_schema()
    known = set(schema["required"]) | set(schema["optional"])
    for mp in glob.glob(os.path.join(ROOT, "data", "mappings", "*.yaml")):
        m = yaml.safe_load(open(mp, encoding="utf-8"))
        for canon in (m.get("columns") or {}):
            assert canon in known, f"{os.path.basename(mp)}: {canon} nincs a sémában"


def test_canonizer_covers_required(tmp_path):
    """A mapping + levezetések a required oszlopok mindegyikét előállítják."""
    import yaml

    schema = load_schema()
    # minimális szintetikus forrás a mappingen át
    src = pd.DataFrame({
        "listing_id": ["1"], "listing_type": ["elado"], "cim_teljes": ["Teszt utca 1."],
        "iranyitoszam": ["1100"], "varos": ["Budapest"], "utca": ["Teszt utca"],
        "hazszam": ["1"], "cim_minoseg": ["strukturalt"], "url": ["http://x/1"],
        "title": ["t"], "crawl_datuma": ["2026-10-08"], "ar": [30000000.0],
        "szobak_szama": [2.0], "alapterulet_nm": [50.0], "epites_eve": [1990.0],
        "leiras": ["szöveg"], "fenykepek_szama": [1.0],
    })
    mapping = {
        "vocab": {},
        "columns": {
            "listing_id": {"from": "listing_id", "to": "string"},
            "price_huf": {"from": "ar", "to": "float"},
            "cim_teljes": {"from": "cim_teljes", "to": "string"},
            "iranyitoszam": {"from": "iranyitoszam", "to": "string"},
            "varos": {"from": "varos", "to": "string"},
            "utca": {"from": "utca", "to": "string"},
            "hazszam": {"from": "hazszam", "to": "string"},
            "cim_forras": {"from": "cim_minoseg", "to": "string"},
            "url": {"from": "url", "to": "string"},
            "title": {"from": "title", "to": "string"},
            "gyujtes_datuma": {"from": "crawl_datuma", "to": "string"},
            "alapterulet_nm": {"from": "alapterulet_nm", "to": "float"},
            "szobaszam_osszes": {"from": "szobak_szama", "to": "float"},
            "epites_eve": {"from": "epites_eve", "to": "float"},
            "leiras": {"from": "leiras", "to": "string"},
            "fenykepek_szama": {"from": "fenykepek_szama", "to": "float"},
        },
    }
    mapped = apply_mapping(src, mapping)
    derived = derive_core(mapped, {"eur_huf_rate": None, "metadata": {"crawl_year": 2026}}, mapping)
    derived["geokodolt_lat"] = 47.5
    derived["geokodolt_lon"] = 19.1
    derived["geokodolas_pontossag"] = "hazszam"
    derived["geokodolas_modszere"] = "cim_nominatim"
    derived["minta_garantalt_pontos"] = 1
    out = coerce(derived, schema)
    missing = [c for c in schema["required"] if c not in out.columns]
    assert not missing, f"hiányzó required: {missing}"


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))