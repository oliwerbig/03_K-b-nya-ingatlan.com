# 0008 — Háromrétegű adatfolyam, séma v2 és cím-alapú geokódolás

Dátum: 2026-10-08 | Státusz: elfogadva

## Kontextus
A friss scrape-ek nyers HTML-eket hoznak (`data/raw/<dataset>/{elado,kiado}/*.html`).
A korábbi adat-előkészítés egyedi, részben kézi lépésekből állt; a cél egy
**megismételhető, determinisztikus, programatikus** folyamat, amely bármikor
új adathalmaz érkezésekor azonos elveken fut le.

## Döntések
1. **Három réteg**:
   - `data/raw/` — csak a scraper-output (HTML + index.csv; a HTML-ek NINCSENEK a gitben, az index.csv-k igen).
   - `data/extracted/` — forrás-specifikus Excel, **eredeti változónevekkel**, semmi levezetett érték (extractorok: `scripts/extract_ingatlancom_html.py`, `scripts/extract_willhaben_html.py` + oszlop-inventár és extract-log).
   - `data/processed/` — a kánonnak megfelelő master (parquet + **emberi Excel** + geojson), a mapping + a sémavezérelt kanonizáló kimenete.
2. **Mapping v2**: `data/mappings/<dataset>.yaml` — név- ÉS típus-transzformáció
   (`to: string|float|int|bool`, `parse_number`, `map`, `regex_replace`, `split_take`, `contains`…).
   A levezetéseket NEM a mapping számolja, hanem a közös `canonize_schema.py`.
3. **Cím-alapú geokódolás**: a kanonikus pozíció KIZÁRÓLAG címből (Nominatim, permanens,
   verziózott cache). A portál-koordináták (ingatlan.com JSON-LD geo, willhaben COORDINATES)
   a magánszféra-védelem miatt szándékosan szórtak → CSAK nyers mellékinformációként
   (`lat_portal`, `lon_portal`, `portal_pozicio_sugar_m`). `minta_garantalt_pontos = 1`
   ⇔ hazszám-szintű címgeokódolás.
4. **Séma v2** (`data/schema.yaml`): adatforrás-agnosztikus kánon (47 required + optional
   univerzum), a sávrendszerek változatlanok; típusdöntések: szöveg / float (NaN-honest
   épületkor) / int-ordinális (`allapot_kod`) / bináris 0-1 dummyk / küszöb-kategorikus.
   Új mezők: `ingatlan_tipus`, `kaucio_huf`, `is_duplikalt_gyanus`, `geokodolas_pontossag`,
   portál-pozíció-mezők, Budapest-specifikus paraméterek stb.
5. **≥2000 m puffer** MINDEN OSM/POI letöltésre (`data/schema.yaml buffers` + `fetch_osm_layers.py`).
6. **Semmi beégetett területnév a kódban**: minden az `data/areas.yaml`-ből jön
   (azonosítók, útvonalak, extractor, pénznem + rögzített crawl-napi ECB-árfolyam 366.25 HUF/EUR,
   középpontok, fallback-állomások). A `leopoldstadt` a bécsi terület kanonikus azonosítója.
7. **EUR→HUF**: rögzített, dokumentált crawl-napi árfolyam (ECB, 2026-10-08: 366.25) — nem soronkénti.
8. **Duplikátumok**: törlés helyett `is_duplikalt_gyanus` jelölő; a reklám-frame-ek (adverticum)
   kiszűrése az extractorban; a scrape vegyes ingatlantípusait az `ingatlan_tipus` őrzi meg,
   az elemzések lakóingatlan-szűréssel (`is_residential_tipus`) dolgoznak.

## Következmények
- A `verify.py` invariáns-alapú (nincs beégetett darabszám); a SHA256SUMS a friss kimenetekre.
- A pipeline CLI: `python -m ingatlan_tdk pipeline` (extract → geocode → canonize → verify → report).
- A régi, törölt adatokra semmi nem épül; minden N frissen számolódik.