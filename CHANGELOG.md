## [Unreleased]
- fix: bécsi koordináta-precizitás (egyedi koordinátapár = pontos), panel-proxy (1945-1990 korszak)
- feat: kanonikus hedonikus specifikáció (_utils.fit_canonical_hedonic) — a 04/07/15 azonos számokat ad
- feat: párhuzamos riportépítés (tdk-report --parallel), GWR interval-keresés, karcsúsított CV
- fix: kötöttpálya-index dummyk a folytonos metrótáv helyett a főmodellekben

# Changelog

Minden érdemi változás itt van rögzítve, emberi nyelven, dátumozva.
Formátum: [Keep a Changelog](https://keepachangelog.com/hu/1.1.0/).

## [Nem kiadott] — Kanonikus újjászervezés és konvenciós rendszer

### Hozzáadva
- `CONTRIBUTING.md` — a projekt konvenciós szabályzata (struktúra, adatszabályok, elnevezések, DoD).
- `AGENTS.md` — utasítások AI-asszisztenseknek.
- `CHANGELOG.md` — ez a napló.
- `check_structure.py` — a struktúra- és konvenciószabályok gépi ellenőrzése.
- `Makefile` — `check` / `lint` / `format` / `verify` / `test` / `report` / `clean` célok.
- `pyproject.toml` — ruff konfiguráció és projektmetadata.
- `.editorconfig` — egységes kódolás (UTF-8, LF, 4 szóköz).
- `.pre-commit-config.yaml` — commit előtti automatikus ellenőrzések.
- `.github/workflows/ci.yml` — CI: ruff + compileall + verify + pytest + struktúra.
- `requirements-dev.txt`: `pytest`, `ruff`, `pre-commit`.

### Megváltoztatva
- `data/processed/ADATKONYV_ES_METADATA.md` → `docs/ADATKONYV_ES_METADATA.md`.
- `mappings/` → `data/mappings/` (+ `scripts/preprocess_new_data.py` útvonal-frissítés).
- `notebook_docs.py` → `report_engine/notebook_docs.py` (+ relatív import a `full_narrative.py`-ban).
- `README.md` — Konvenciók szekció és frissített hivatkozások.

### Hozzáadva / Megváltoztatva
- **Kanonikus adatséma** (`data/schema.yaml`): egységes változókészlet minden területre
  (127 oszlop), adatalapú sávhatárok (méret-kvantilisek 44/53/68 m², építési korszakok
  0-10/10-30/30-60/60+ év), rétegenkénti letöltési pufferek (vasút 2000 m, POI 1125 m,
  úthálózat 1250 m). Átnevezések: `city`→`varos`, `van_erkely`→`has_erkely`,
  `price_million_huf`→`ar_millio_ft`.
- **Fókuszmentesítés:** minden Mázsa-tér/belváros (CBD) változó, hivatkozás és konfig
  törölve (adatok, notebookok előkészítve, `areas.yaml`, `_utils`, `verify`, ADATKONYV).
- **Valódi hálózati távolságok:** az euklidészi × kerülőfaktor közelítést Dijkstra
  alapú OSM-úthálózati legrövidebb utak váltják (medián kerülőfaktor 1,75 a régi 1,25
  helyett); POI-sávok (`poi_5p/10p/15p_count`) hálózati elérhetőségen; a kőbányai
  vasúti réteg 2000 m-es pufferrel újratöltve (a korábbi alulméretezett volt),
  bécsi úthálózat + tranzit letöltve.
- Új szkriptek: `scripts/fetch_network_layers.py`, `scripts/network_metrics.py`,
  `scripts/canonize_schema.py`.
### Hozzáadva / Megváltoztatva (módszertani felülvizsgálat)
- **A 17 notebook teljes módszertani felülvizsgálata:** a fókusz (Mázsa/belváros)
  referenciák teljes eltávolítása; hardkódolt eredmény-számok megszüntetése (minden
  KPI a futtatott modellekből); doc–code konzisztencia; seed minden véletlenhez;
  a kanonikus sávok mindenhol a `_utils` konstansokból.
- **nb04:** Mann–Whitney U + Dunn post-hoc (Bonferroni), kontrollált zóna-diszkont
  (HC1), diszjunkt sáv-dummyk, immissziós dózis-válasz görbe bootstrap CI-vel,
  a 150 m-es küszöb placebo-vizsgálata, Chow-töréspont-teszt.
- **nb05:** a POI-sávok a kanonikus HÁLÓZATI `poi_5p/10p/15p_count` oszlopokból
  (a Web Mercator-légvonalas számítás törölve); POI-modellek F-teszttel, HC1-gyel.
- **nb07:** HC1 SE-k, helyes implicit-hatás értelmezés (dummy/log/folytonos),
  Breusch–Pagan + RESET, a JS-kalkulátor a TÉNYLEGES becsült együtthatókból.
- **nb09:** valódi SEM (ML_Error), SAR GM_Lag, Anselin LM-tesztek, permutációs
  Moran p-értékek, vetületi KNN.
- **nb10:** a szintetikus GWR-fallback törölve; 07/09-cel azonos kontrollok;
  t-szűrt (|t|≥1.96) β-térképek; VIF-diagnosztika; jitter az egybeeső pontokra.
- **nb11:** ismételt + TÉRBELI blokk-CV, out-of-sample arbitrázs, permutációs
  fontosság, kvantilis GB predikciós intervallumok, a fókusz-változó kivétele.
- **nb12:** hedonikusan párosított hozam, cap-rate érzékenység, térbeli rent gap
  (immissziós sáv × állapot), javított JS-kalkulátor.
- **nb13:** a volatilitások/korreláció a hedonikus reziduumokból kalibrálva;
  a tornado a szimulációból számolva; MC-SE jelentése.
- **nb14:** becslés-alapú felértékelődési potenciál (kontrollált sávdiszkontok),
  a Mázsa-szcenárió átnevezése, dinamikus medián a JS-presetekben.
- **nb15:** minden KPI a futtatott modellekből (hedonikus, SAR, rent gap, RF CV);
  a hatásgörbe a becsült együtthatókból.
- **nb16:** pooled hedonikus regresszió terület×immissziós sáv interakciókkal,
  EUR-normalizálás, CI-sávok, elemszám-küszöbök (N≥5/10).
### Javítva
- **Notebookok terület-univerzálissá tétele:** a kőbánya-specifikus oszlopokra
  (`tavolsag_mazsa_halozati_m`, `tavolsag_belvaros_halozati_m`, `szobaszam_kategoria`)
  való hivatkozások védettek — hiányzó oszlopnál a notebook leszármaztatja vagy kihagyja;
  a POI-betöltés területfüggő (`poi_{area}_buffered.geojson`) + `geopandas` import;
  a GWR együttható-kinyerés és a Random Forest szcenárió-mátrix a tényleges oszlopokhoz igazodik.
- `tdk-report`: a notebookok **returncode-ja valóban hibának számít** (korábban a
  sikertelen notebookok is „hibás notebook: 0"-ként jelentek meg) — a CI mostantól
  hangosan elhasal hiányos riport esetén.
### Hozzáadva / Megváltoztatva
- **Kanonikus adatséma** (`data/schema.yaml`): egységes változókészlet minden területre
  (127 oszlop), adatalapú sávhatárok (méret-kvantilisek 44/53/68 m², építési korszakok
  0-10/10-30/30-60/60+ év), rétegenkénti letöltési pufferek (vasút 2000 m, POI 1125 m,
  úthálózat 1250 m). Átnevezések: `city`→`varos`, `van_erkely`→`has_erkely`,
  `price_million_huf`→`ar_millio_ft`.
- **Fókuszmentesítés:** minden Mázsa-tér/belváros (CBD) változó, hivatkozás és konfig
  törölve (adatok, notebookok előkészítve, `areas.yaml`, `_utils`, `verify`, ADATKONYV).
- **Valódi hálózati távolságok:** az euklidészi × kerülőfaktor közelítést Dijkstra
  alapú OSM-úthálózati legrövidebb utak váltják (medián kerülőfaktor 1,75 a régi 1,25
  helyett); POI-sávok (`poi_5p/10p/15p_count`) hálózati elérhetőségen; a kőbányai
  vasúti réteg 2000 m-es pufferrel újratöltve (a korábbi alulméretezett volt),
  bécsi úthálózat + tranzit letöltve.
- Új szkriptek: `scripts/fetch_network_layers.py`, `scripts/network_metrics.py`,
  `scripts/canonize_schema.py`.
### Hozzáadva / Megváltoztatva (módszertani felülvizsgálat)
- **A 17 notebook teljes módszertani felülvizsgálata:** a fókusz (Mázsa/belváros)
  referenciák teljes eltávolítása; hardkódolt eredmény-számok megszüntetése (minden
  KPI a futtatott modellekből); doc–code konzisztencia; seed minden véletlenhez;
  a kanonikus sávok mindenhol a `_utils` konstansokból.
- **nb04:** Mann–Whitney U + Dunn post-hoc (Bonferroni), kontrollált zóna-diszkont
  (HC1), diszjunkt sáv-dummyk, immissziós dózis-válasz görbe bootstrap CI-vel,
  a 150 m-es küszöb placebo-vizsgálata, Chow-töréspont-teszt.
- **nb05:** a POI-sávok a kanonikus HÁLÓZATI `poi_5p/10p/15p_count` oszlopokból
  (a Web Mercator-légvonalas számítás törölve); POI-modellek F-teszttel, HC1-gyel.
- **nb07:** HC1 SE-k, helyes implicit-hatás értelmezés (dummy/log/folytonos),
  Breusch–Pagan + RESET, a JS-kalkulátor a TÉNYLEGES becsült együtthatókból.
- **nb09:** valódi SEM (ML_Error), SAR GM_Lag, Anselin LM-tesztek, permutációs
  Moran p-értékek, vetületi KNN.
- **nb10:** a szintetikus GWR-fallback törölve; 07/09-cel azonos kontrollok;
  t-szűrt (|t|≥1.96) β-térképek; VIF-diagnosztika; jitter az egybeeső pontokra.
- **nb11:** ismételt + TÉRBELI blokk-CV, out-of-sample arbitrázs, permutációs
  fontosság, kvantilis GB predikciós intervallumok, a fókusz-változó kivétele.
- **nb12:** hedonikusan párosított hozam, cap-rate érzékenység, térbeli rent gap
  (immissziós sáv × állapot), javított JS-kalkulátor.
- **nb13:** a volatilitások/korreláció a hedonikus reziduumokból kalibrálva;
  a tornado a szimulációból számolva; MC-SE jelentése.
- **nb14:** becslés-alapú felértékelődési potenciál (kontrollált sávdiszkontok),
  a Mázsa-szcenárió átnevezése, dinamikus medián a JS-presetekben.
- **nb15:** minden KPI a futtatott modellekből (hedonikus, SAR, rent gap, RF CV);
  a hatásgörbe a becsült együtthatókból.
- **nb16:** pooled hedonikus regresszió terület×immissziós sáv interakciókkal,
  EUR-normalizálás, CI-sávok, elemszám-küszöbök (N≥5/10).
### Javítva
- `tdk-report` időtúllépés-védelem: notebookonként `--ExecutePreprocessor.timeout` és
  szubprocessz-timeout, plusz BLAS-thread limit (`OMP/OPENBLAS/MKL_NUM_THREADS=1`) a
  CI-holtpontok ellen; a Pages build-job `timeout-minutes: 180`.
- A Plotly renderer `notebook`-ra állítva: az exportált HTML önálló (CDN plotly.js-re
  épülő) ábrákat tartalmaz a GitHub Pages-hez.
### Hozzáadva / Megváltoztatva
- **Kanonikus adatséma** (`data/schema.yaml`): egységes változókészlet minden területre
  (127 oszlop), adatalapú sávhatárok (méret-kvantilisek 44/53/68 m², építési korszakok
  0-10/10-30/30-60/60+ év), rétegenkénti letöltési pufferek (vasút 2000 m, POI 1125 m,
  úthálózat 1250 m). Átnevezések: `city`→`varos`, `van_erkely`→`has_erkely`,
  `price_million_huf`→`ar_millio_ft`.
- **Fókuszmentesítés:** minden Mázsa-tér/belváros (CBD) változó, hivatkozás és konfig
  törölve (adatok, notebookok előkészítve, `areas.yaml`, `_utils`, `verify`, ADATKONYV).
- **Valódi hálózati távolságok:** az euklidészi × kerülőfaktor közelítést Dijkstra
  alapú OSM-úthálózati legrövidebb utak váltják (medián kerülőfaktor 1,75 a régi 1,25
  helyett); POI-sávok (`poi_5p/10p/15p_count`) hálózati elérhetőségen; a kőbányai
  vasúti réteg 2000 m-es pufferrel újratöltve (a korábbi alulméretezett volt),
  bécsi úthálózat + tranzit letöltve.
- Új szkriptek: `scripts/fetch_network_layers.py`, `scripts/network_metrics.py`,
  `scripts/canonize_schema.py`.
### Hozzáadva / Megváltoztatva (módszertani felülvizsgálat)
- **A 17 notebook teljes módszertani felülvizsgálata:** a fókusz (Mázsa/belváros)
  referenciák teljes eltávolítása; hardkódolt eredmény-számok megszüntetése (minden
  KPI a futtatott modellekből); doc–code konzisztencia; seed minden véletlenhez;
  a kanonikus sávok mindenhol a `_utils` konstansokból.
- **nb04:** Mann–Whitney U + Dunn post-hoc (Bonferroni), kontrollált zóna-diszkont
  (HC1), diszjunkt sáv-dummyk, immissziós dózis-válasz görbe bootstrap CI-vel,
  a 150 m-es küszöb placebo-vizsgálata, Chow-töréspont-teszt.
- **nb05:** a POI-sávok a kanonikus HÁLÓZATI `poi_5p/10p/15p_count` oszlopokból
  (a Web Mercator-légvonalas számítás törölve); POI-modellek F-teszttel, HC1-gyel.
- **nb07:** HC1 SE-k, helyes implicit-hatás értelmezés (dummy/log/folytonos),
  Breusch–Pagan + RESET, a JS-kalkulátor a TÉNYLEGES becsült együtthatókból.
- **nb09:** valódi SEM (ML_Error), SAR GM_Lag, Anselin LM-tesztek, permutációs
  Moran p-értékek, vetületi KNN.
- **nb10:** a szintetikus GWR-fallback törölve; 07/09-cel azonos kontrollok;
  t-szűrt (|t|≥1.96) β-térképek; VIF-diagnosztika; jitter az egybeeső pontokra.
- **nb11:** ismételt + TÉRBELI blokk-CV, out-of-sample arbitrázs, permutációs
  fontosság, kvantilis GB predikciós intervallumok, a fókusz-változó kivétele.
- **nb12:** hedonikusan párosított hozam, cap-rate érzékenység, térbeli rent gap
  (immissziós sáv × állapot), javított JS-kalkulátor.
- **nb13:** a volatilitások/korreláció a hedonikus reziduumokból kalibrálva;
  a tornado a szimulációból számolva; MC-SE jelentése.
- **nb14:** becslés-alapú felértékelődési potenciál (kontrollált sávdiszkontok),
  a Mázsa-szcenárió átnevezése, dinamikus medián a JS-presetekben.
- **nb15:** minden KPI a futtatott modellekből (hedonikus, SAR, rent gap, RF CV);
  a hatásgörbe a becsült együtthatókból.
- **nb16:** pooled hedonikus regresszió terület×immissziós sáv interakciókkal,
  EUR-normalizálás, CI-sávok, elemszám-küszöbök (N≥5/10).
### Javítva
- **Notebookok terület-univerzálissá tétele:** a kőbánya-specifikus oszlopokra
  (`tavolsag_mazsa_halozati_m`, `tavolsag_belvaros_halozati_m`, `szobaszam_kategoria`)
  való hivatkozások védettek — hiányzó oszlopnál a notebook leszármaztatja vagy kihagyja;
  a POI-betöltés területfüggő (`poi_{area}_buffered.geojson`) + `geopandas` import;
  a GWR együttható-kinyerés és a Random Forest szcenárió-mátrix a tényleges oszlopokhoz igazodik.
- `tdk-report`: a notebookok **returncode-ja valóban hibának számít** (korábban a
  sikertelen notebookok is „hibás notebook: 0"-ként jelentek meg) — a CI mostantól
  hangosan elhasal hiányos riport esetén.
### Hozzáadva / Megváltoztatva
- **Kanonikus adatséma** (`data/schema.yaml`): egységes változókészlet minden területre
  (127 oszlop), adatalapú sávhatárok (méret-kvantilisek 44/53/68 m², építési korszakok
  0-10/10-30/30-60/60+ év), rétegenkénti letöltési pufferek (vasút 2000 m, POI 1125 m,
  úthálózat 1250 m). Átnevezések: `city`→`varos`, `van_erkely`→`has_erkely`,
  `price_million_huf`→`ar_millio_ft`.
- **Fókuszmentesítés:** minden Mázsa-tér/belváros (CBD) változó, hivatkozás és konfig
  törölve (adatok, notebookok előkészítve, `areas.yaml`, `_utils`, `verify`, ADATKONYV).
- **Valódi hálózati távolságok:** az euklidészi × kerülőfaktor közelítést Dijkstra
  alapú OSM-úthálózati legrövidebb utak váltják (medián kerülőfaktor 1,75 a régi 1,25
  helyett); POI-sávok (`poi_5p/10p/15p_count`) hálózati elérhetőségen; a kőbányai
  vasúti réteg 2000 m-es pufferrel újratöltve (a korábbi alulméretezett volt),
  bécsi úthálózat + tranzit letöltve.
- Új szkriptek: `scripts/fetch_network_layers.py`, `scripts/network_metrics.py`,
  `scripts/canonize_schema.py`.
### Hozzáadva / Megváltoztatva (módszertani felülvizsgálat)
- **A 17 notebook teljes módszertani felülvizsgálata:** a fókusz (Mázsa/belváros)
  referenciák teljes eltávolítása; hardkódolt eredmény-számok megszüntetése (minden
  KPI a futtatott modellekből); doc–code konzisztencia; seed minden véletlenhez;
  a kanonikus sávok mindenhol a `_utils` konstansokból.
- **nb04:** Mann–Whitney U + Dunn post-hoc (Bonferroni), kontrollált zóna-diszkont
  (HC1), diszjunkt sáv-dummyk, immissziós dózis-válasz görbe bootstrap CI-vel,
  a 150 m-es küszöb placebo-vizsgálata, Chow-töréspont-teszt.
- **nb05:** a POI-sávok a kanonikus HÁLÓZATI `poi_5p/10p/15p_count` oszlopokból
  (a Web Mercator-légvonalas számítás törölve); POI-modellek F-teszttel, HC1-gyel.
- **nb07:** HC1 SE-k, helyes implicit-hatás értelmezés (dummy/log/folytonos),
  Breusch–Pagan + RESET, a JS-kalkulátor a TÉNYLEGES becsült együtthatókból.
- **nb09:** valódi SEM (ML_Error), SAR GM_Lag, Anselin LM-tesztek, permutációs
  Moran p-értékek, vetületi KNN.
- **nb10:** a szintetikus GWR-fallback törölve; 07/09-cel azonos kontrollok;
  t-szűrt (|t|≥1.96) β-térképek; VIF-diagnosztika; jitter az egybeeső pontokra.
- **nb11:** ismételt + TÉRBELI blokk-CV, out-of-sample arbitrázs, permutációs
  fontosság, kvantilis GB predikciós intervallumok, a fókusz-változó kivétele.
- **nb12:** hedonikusan párosított hozam, cap-rate érzékenység, térbeli rent gap
  (immissziós sáv × állapot), javított JS-kalkulátor.
- **nb13:** a volatilitások/korreláció a hedonikus reziduumokból kalibrálva;
  a tornado a szimulációból számolva; MC-SE jelentése.
- **nb14:** becslés-alapú felértékelődési potenciál (kontrollált sávdiszkontok),
  a Mázsa-szcenárió átnevezése, dinamikus medián a JS-presetekben.
- **nb15:** minden KPI a futtatott modellekből (hedonikus, SAR, rent gap, RF CV);
  a hatásgörbe a becsült együtthatókból.
- **nb16:** pooled hedonikus regresszió terület×immissziós sáv interakciókkal,
  EUR-normalizálás, CI-sávok, elemszám-küszöbök (N≥5/10).
### Javítva
- `report_engine/full_narrative.py` — 5 fejezetépítő hiányzó mértékegység-definíciója
  javítva (nb02, nb04, nb06, nb12, nb14; ezek `NameError`-rel elszálltak volna friss
  riportgenerálásnál).
- `scripts/preprocess_new_data.py` — a `mapped_df` hivatkozás helyreállítva a
  `run_pipeline`-ben (a lint-ellenőrzés tárta fel).
- Lint: ruff bevezetése (`E4/E7/E9/F`), a kódbázis 62 szabálysértésről 0-ra hozva;
  az `E402` a szándékos útvonal-bootstrap mintánál engedélyezve (dokumentálva).

### Hozzáadva / Megváltoztatva
- **Kanonikus adatséma** (`data/schema.yaml`): egységes változókészlet minden területre
  (127 oszlop), adatalapú sávhatárok (méret-kvantilisek 44/53/68 m², építési korszakok
  0-10/10-30/30-60/60+ év), rétegenkénti letöltési pufferek (vasút 2000 m, POI 1125 m,
  úthálózat 1250 m). Átnevezések: `city`→`varos`, `van_erkely`→`has_erkely`,
  `price_million_huf`→`ar_millio_ft`.
- **Fókuszmentesítés:** minden Mázsa-tér/belváros (CBD) változó, hivatkozás és konfig
  törölve (adatok, notebookok előkészítve, `areas.yaml`, `_utils`, `verify`, ADATKONYV).
- **Valódi hálózati távolságok:** az euklidészi × kerülőfaktor közelítést Dijkstra
  alapú OSM-úthálózati legrövidebb utak váltják (medián kerülőfaktor 1,75 a régi 1,25
  helyett); POI-sávok (`poi_5p/10p/15p_count`) hálózati elérhetőségen; a kőbányai
  vasúti réteg 2000 m-es pufferrel újratöltve (a korábbi alulméretezett volt),
  bécsi úthálózat + tranzit letöltve.
- Új szkriptek: `scripts/fetch_network_layers.py`, `scripts/network_metrics.py`,
  `scripts/canonize_schema.py`.
### Hozzáadva / Megváltoztatva (módszertani felülvizsgálat)
- **A 17 notebook teljes módszertani felülvizsgálata:** a fókusz (Mázsa/belváros)
  referenciák teljes eltávolítása; hardkódolt eredmény-számok megszüntetése (minden
  KPI a futtatott modellekből); doc–code konzisztencia; seed minden véletlenhez;
  a kanonikus sávok mindenhol a `_utils` konstansokból.
- **nb04:** Mann–Whitney U + Dunn post-hoc (Bonferroni), kontrollált zóna-diszkont
  (HC1), diszjunkt sáv-dummyk, immissziós dózis-válasz görbe bootstrap CI-vel,
  a 150 m-es küszöb placebo-vizsgálata, Chow-töréspont-teszt.
- **nb05:** a POI-sávok a kanonikus HÁLÓZATI `poi_5p/10p/15p_count` oszlopokból
  (a Web Mercator-légvonalas számítás törölve); POI-modellek F-teszttel, HC1-gyel.
- **nb07:** HC1 SE-k, helyes implicit-hatás értelmezés (dummy/log/folytonos),
  Breusch–Pagan + RESET, a JS-kalkulátor a TÉNYLEGES becsült együtthatókból.
- **nb09:** valódi SEM (ML_Error), SAR GM_Lag, Anselin LM-tesztek, permutációs
  Moran p-értékek, vetületi KNN.
- **nb10:** a szintetikus GWR-fallback törölve; 07/09-cel azonos kontrollok;
  t-szűrt (|t|≥1.96) β-térképek; VIF-diagnosztika; jitter az egybeeső pontokra.
- **nb11:** ismételt + TÉRBELI blokk-CV, out-of-sample arbitrázs, permutációs
  fontosság, kvantilis GB predikciós intervallumok, a fókusz-változó kivétele.
- **nb12:** hedonikusan párosított hozam, cap-rate érzékenység, térbeli rent gap
  (immissziós sáv × állapot), javított JS-kalkulátor.
- **nb13:** a volatilitások/korreláció a hedonikus reziduumokból kalibrálva;
  a tornado a szimulációból számolva; MC-SE jelentése.
- **nb14:** becslés-alapú felértékelődési potenciál (kontrollált sávdiszkontok),
  a Mázsa-szcenárió átnevezése, dinamikus medián a JS-presetekben.
- **nb15:** minden KPI a futtatott modellekből (hedonikus, SAR, rent gap, RF CV);
  a hatásgörbe a becsült együtthatókból.
- **nb16:** pooled hedonikus regresszió terület×immissziós sáv interakciókkal,
  EUR-normalizálás, CI-sávok, elemszám-küszöbök (N≥5/10).
### Javítva
- **Notebookok terület-univerzálissá tétele:** a kőbánya-specifikus oszlopokra
  (`tavolsag_mazsa_halozati_m`, `tavolsag_belvaros_halozati_m`, `szobaszam_kategoria`)
  való hivatkozások védettek — hiányzó oszlopnál a notebook leszármaztatja vagy kihagyja;
  a POI-betöltés területfüggő (`poi_{area}_buffered.geojson`) + `geopandas` import;
  a GWR együttható-kinyerés és a Random Forest szcenárió-mátrix a tényleges oszlopokhoz igazodik.
- `tdk-report`: a notebookok **returncode-ja valóban hibának számít** (korábban a
  sikertelen notebookok is „hibás notebook: 0"-ként jelentek meg) — a CI mostantól
  hangosan elhasal hiányos riport esetén.
### Hozzáadva / Megváltoztatva
- **Kanonikus adatséma** (`data/schema.yaml`): egységes változókészlet minden területre
  (127 oszlop), adatalapú sávhatárok (méret-kvantilisek 44/53/68 m², építési korszakok
  0-10/10-30/30-60/60+ év), rétegenkénti letöltési pufferek (vasút 2000 m, POI 1125 m,
  úthálózat 1250 m). Átnevezések: `city`→`varos`, `van_erkely`→`has_erkely`,
  `price_million_huf`→`ar_millio_ft`.
- **Fókuszmentesítés:** minden Mázsa-tér/belváros (CBD) változó, hivatkozás és konfig
  törölve (adatok, notebookok előkészítve, `areas.yaml`, `_utils`, `verify`, ADATKONYV).
- **Valódi hálózati távolságok:** az euklidészi × kerülőfaktor közelítést Dijkstra
  alapú OSM-úthálózati legrövidebb utak váltják (medián kerülőfaktor 1,75 a régi 1,25
  helyett); POI-sávok (`poi_5p/10p/15p_count`) hálózati elérhetőségen; a kőbányai
  vasúti réteg 2000 m-es pufferrel újratöltve (a korábbi alulméretezett volt),
  bécsi úthálózat + tranzit letöltve.
- Új szkriptek: `scripts/fetch_network_layers.py`, `scripts/network_metrics.py`,
  `scripts/canonize_schema.py`.
### Hozzáadva / Megváltoztatva (módszertani felülvizsgálat)
- **A 17 notebook teljes módszertani felülvizsgálata:** a fókusz (Mázsa/belváros)
  referenciák teljes eltávolítása; hardkódolt eredmény-számok megszüntetése (minden
  KPI a futtatott modellekből); doc–code konzisztencia; seed minden véletlenhez;
  a kanonikus sávok mindenhol a `_utils` konstansokból.
- **nb04:** Mann–Whitney U + Dunn post-hoc (Bonferroni), kontrollált zóna-diszkont
  (HC1), diszjunkt sáv-dummyk, immissziós dózis-válasz görbe bootstrap CI-vel,
  a 150 m-es küszöb placebo-vizsgálata, Chow-töréspont-teszt.
- **nb05:** a POI-sávok a kanonikus HÁLÓZATI `poi_5p/10p/15p_count` oszlopokból
  (a Web Mercator-légvonalas számítás törölve); POI-modellek F-teszttel, HC1-gyel.
- **nb07:** HC1 SE-k, helyes implicit-hatás értelmezés (dummy/log/folytonos),
  Breusch–Pagan + RESET, a JS-kalkulátor a TÉNYLEGES becsült együtthatókból.
- **nb09:** valódi SEM (ML_Error), SAR GM_Lag, Anselin LM-tesztek, permutációs
  Moran p-értékek, vetületi KNN.
- **nb10:** a szintetikus GWR-fallback törölve; 07/09-cel azonos kontrollok;
  t-szűrt (|t|≥1.96) β-térképek; VIF-diagnosztika; jitter az egybeeső pontokra.
- **nb11:** ismételt + TÉRBELI blokk-CV, out-of-sample arbitrázs, permutációs
  fontosság, kvantilis GB predikciós intervallumok, a fókusz-változó kivétele.
- **nb12:** hedonikusan párosított hozam, cap-rate érzékenység, térbeli rent gap
  (immissziós sáv × állapot), javított JS-kalkulátor.
- **nb13:** a volatilitások/korreláció a hedonikus reziduumokból kalibrálva;
  a tornado a szimulációból számolva; MC-SE jelentése.
- **nb14:** becslés-alapú felértékelődési potenciál (kontrollált sávdiszkontok),
  a Mázsa-szcenárió átnevezése, dinamikus medián a JS-presetekben.
- **nb15:** minden KPI a futtatott modellekből (hedonikus, SAR, rent gap, RF CV);
  a hatásgörbe a becsült együtthatókból.
- **nb16:** pooled hedonikus regresszió terület×immissziós sáv interakciókkal,
  EUR-normalizálás, CI-sávok, elemszám-küszöbök (N≥5/10).
### Javítva
- `tdk-report` időtúllépés-védelem: notebookonként `--ExecutePreprocessor.timeout` és
  szubprocessz-timeout, plusz BLAS-thread limit (`OMP/OPENBLAS/MKL_NUM_THREADS=1`) a
  CI-holtpontok ellen; a Pages build-job `timeout-minutes: 180`.
- A Plotly renderer `notebook`-ra állítva: az exportált HTML önálló (CDN plotly.js-re
  épülő) ábrákat tartalmaz a GitHub Pages-hez.
### Hozzáadva / Megváltoztatva
- **Kanonikus adatséma** (`data/schema.yaml`): egységes változókészlet minden területre
  (127 oszlop), adatalapú sávhatárok (méret-kvantilisek 44/53/68 m², építési korszakok
  0-10/10-30/30-60/60+ év), rétegenkénti letöltési pufferek (vasút 2000 m, POI 1125 m,
  úthálózat 1250 m). Átnevezések: `city`→`varos`, `van_erkely`→`has_erkely`,
  `price_million_huf`→`ar_millio_ft`.
- **Fókuszmentesítés:** minden Mázsa-tér/belváros (CBD) változó, hivatkozás és konfig
  törölve (adatok, notebookok előkészítve, `areas.yaml`, `_utils`, `verify`, ADATKONYV).
- **Valódi hálózati távolságok:** az euklidészi × kerülőfaktor közelítést Dijkstra
  alapú OSM-úthálózati legrövidebb utak váltják (medián kerülőfaktor 1,75 a régi 1,25
  helyett); POI-sávok (`poi_5p/10p/15p_count`) hálózati elérhetőségen; a kőbányai
  vasúti réteg 2000 m-es pufferrel újratöltve (a korábbi alulméretezett volt),
  bécsi úthálózat + tranzit letöltve.
- Új szkriptek: `scripts/fetch_network_layers.py`, `scripts/network_metrics.py`,
  `scripts/canonize_schema.py`.
### Hozzáadva / Megváltoztatva (módszertani felülvizsgálat)
- **A 17 notebook teljes módszertani felülvizsgálata:** a fókusz (Mázsa/belváros)
  referenciák teljes eltávolítása; hardkódolt eredmény-számok megszüntetése (minden
  KPI a futtatott modellekből); doc–code konzisztencia; seed minden véletlenhez;
  a kanonikus sávok mindenhol a `_utils` konstansokból.
- **nb04:** Mann–Whitney U + Dunn post-hoc (Bonferroni), kontrollált zóna-diszkont
  (HC1), diszjunkt sáv-dummyk, immissziós dózis-válasz görbe bootstrap CI-vel,
  a 150 m-es küszöb placebo-vizsgálata, Chow-töréspont-teszt.
- **nb05:** a POI-sávok a kanonikus HÁLÓZATI `poi_5p/10p/15p_count` oszlopokból
  (a Web Mercator-légvonalas számítás törölve); POI-modellek F-teszttel, HC1-gyel.
- **nb07:** HC1 SE-k, helyes implicit-hatás értelmezés (dummy/log/folytonos),
  Breusch–Pagan + RESET, a JS-kalkulátor a TÉNYLEGES becsült együtthatókból.
- **nb09:** valódi SEM (ML_Error), SAR GM_Lag, Anselin LM-tesztek, permutációs
  Moran p-értékek, vetületi KNN.
- **nb10:** a szintetikus GWR-fallback törölve; 07/09-cel azonos kontrollok;
  t-szűrt (|t|≥1.96) β-térképek; VIF-diagnosztika; jitter az egybeeső pontokra.
- **nb11:** ismételt + TÉRBELI blokk-CV, out-of-sample arbitrázs, permutációs
  fontosság, kvantilis GB predikciós intervallumok, a fókusz-változó kivétele.
- **nb12:** hedonikusan párosított hozam, cap-rate érzékenység, térbeli rent gap
  (immissziós sáv × állapot), javított JS-kalkulátor.
- **nb13:** a volatilitások/korreláció a hedonikus reziduumokból kalibrálva;
  a tornado a szimulációból számolva; MC-SE jelentése.
- **nb14:** becslés-alapú felértékelődési potenciál (kontrollált sávdiszkontok),
  a Mázsa-szcenárió átnevezése, dinamikus medián a JS-presetekben.
- **nb15:** minden KPI a futtatott modellekből (hedonikus, SAR, rent gap, RF CV);
  a hatásgörbe a becsült együtthatókból.
- **nb16:** pooled hedonikus regresszió terület×immissziós sáv interakciókkal,
  EUR-normalizálás, CI-sávok, elemszám-küszöbök (N≥5/10).
### Javítva
- **Notebookok terület-univerzálissá tétele:** a kőbánya-specifikus oszlopokra
  (`tavolsag_mazsa_halozati_m`, `tavolsag_belvaros_halozati_m`, `szobaszam_kategoria`)
  való hivatkozások védettek — hiányzó oszlopnál a notebook leszármaztatja vagy kihagyja;
  a POI-betöltés területfüggő (`poi_{area}_buffered.geojson`) + `geopandas` import;
  a GWR együttható-kinyerés és a Random Forest szcenárió-mátrix a tényleges oszlopokhoz igazodik.
- `tdk-report`: a notebookok **returncode-ja valóban hibának számít** (korábban a
  sikertelen notebookok is „hibás notebook: 0"-ként jelentek meg) — a CI mostantól
  hangosan elhasal hiányos riport esetén.
### Hozzáadva / Megváltoztatva
- **Kanonikus adatséma** (`data/schema.yaml`): egységes változókészlet minden területre
  (127 oszlop), adatalapú sávhatárok (méret-kvantilisek 44/53/68 m², építési korszakok
  0-10/10-30/30-60/60+ év), rétegenkénti letöltési pufferek (vasút 2000 m, POI 1125 m,
  úthálózat 1250 m). Átnevezések: `city`→`varos`, `van_erkely`→`has_erkely`,
  `price_million_huf`→`ar_millio_ft`.
- **Fókuszmentesítés:** minden Mázsa-tér/belváros (CBD) változó, hivatkozás és konfig
  törölve (adatok, notebookok előkészítve, `areas.yaml`, `_utils`, `verify`, ADATKONYV).
- **Valódi hálózati távolságok:** az euklidészi × kerülőfaktor közelítést Dijkstra
  alapú OSM-úthálózati legrövidebb utak váltják (medián kerülőfaktor 1,75 a régi 1,25
  helyett); POI-sávok (`poi_5p/10p/15p_count`) hálózati elérhetőségen; a kőbányai
  vasúti réteg 2000 m-es pufferrel újratöltve (a korábbi alulméretezett volt),
  bécsi úthálózat + tranzit letöltve.
- Új szkriptek: `scripts/fetch_network_layers.py`, `scripts/network_metrics.py`,
  `scripts/canonize_schema.py`.
### Hozzáadva / Megváltoztatva (módszertani felülvizsgálat)
- **A 17 notebook teljes módszertani felülvizsgálata:** a fókusz (Mázsa/belváros)
  referenciák teljes eltávolítása; hardkódolt eredmény-számok megszüntetése (minden
  KPI a futtatott modellekből); doc–code konzisztencia; seed minden véletlenhez;
  a kanonikus sávok mindenhol a `_utils` konstansokból.
- **nb04:** Mann–Whitney U + Dunn post-hoc (Bonferroni), kontrollált zóna-diszkont
  (HC1), diszjunkt sáv-dummyk, immissziós dózis-válasz görbe bootstrap CI-vel,
  a 150 m-es küszöb placebo-vizsgálata, Chow-töréspont-teszt.
- **nb05:** a POI-sávok a kanonikus HÁLÓZATI `poi_5p/10p/15p_count` oszlopokból
  (a Web Mercator-légvonalas számítás törölve); POI-modellek F-teszttel, HC1-gyel.
- **nb07:** HC1 SE-k, helyes implicit-hatás értelmezés (dummy/log/folytonos),
  Breusch–Pagan + RESET, a JS-kalkulátor a TÉNYLEGES becsült együtthatókból.
- **nb09:** valódi SEM (ML_Error), SAR GM_Lag, Anselin LM-tesztek, permutációs
  Moran p-értékek, vetületi KNN.
- **nb10:** a szintetikus GWR-fallback törölve; 07/09-cel azonos kontrollok;
  t-szűrt (|t|≥1.96) β-térképek; VIF-diagnosztika; jitter az egybeeső pontokra.
- **nb11:** ismételt + TÉRBELI blokk-CV, out-of-sample arbitrázs, permutációs
  fontosság, kvantilis GB predikciós intervallumok, a fókusz-változó kivétele.
- **nb12:** hedonikusan párosított hozam, cap-rate érzékenység, térbeli rent gap
  (immissziós sáv × állapot), javított JS-kalkulátor.
- **nb13:** a volatilitások/korreláció a hedonikus reziduumokból kalibrálva;
  a tornado a szimulációból számolva; MC-SE jelentése.
- **nb14:** becslés-alapú felértékelődési potenciál (kontrollált sávdiszkontok),
  a Mázsa-szcenárió átnevezése, dinamikus medián a JS-presetekben.
- **nb15:** minden KPI a futtatott modellekből (hedonikus, SAR, rent gap, RF CV);
  a hatásgörbe a becsült együtthatókból.
- **nb16:** pooled hedonikus regresszió terület×immissziós sáv interakciókkal,
  EUR-normalizálás, CI-sávok, elemszám-küszöbök (N≥5/10).
### Javítva
- `ingatlan_tdk.verify` — a szöveges adatfájlok (.json/.csv) hash-számítása mostantól
  CRLF->LF normalizálással történik, így a Windows és Linux (CI) checkout ugyanazt a
  hash-t adja; a `SHA256SUMS.txt` az új, platformfüggetlen hash-ekkel frissítve.
- `deploy-pages.yml` — `actions/configure-pages` lépés visszatéve a Pages telepítés elé.

### Eltávolítva (archiválva)
- `run_and_export_all.py`, `notebooks/precalculate_all.py`, `final_deploy.ps1` (a `build_all.py`/CI váltja).
- `get_exact_stats.py`, `extract_all_numbers.py`, `restructure_project.py` (egyszeri eszközök).

### Hozzáadva
- `LICENSE` (MIT) és `docs/decisions/` — 7 Architecture Decision Record.
- `src/ingatlan_tdk/` src-layout csomag + konzolparancsok: `tdk-build`, `tdk-report`,
  `tdk-verify`, `tdk-check` (`pip install -e .`); `python -m ingatlan_tdk <parancs>`.

### Megváltoztatva
- Minden modul a csomagba költözött (`_utils`, `data_io`, `verify`, `checks`,
  `report_engine`, `notebook_docs`, `cli`); a gyökérből minden szkript törölve.
- A 17 notebook importja: `from ingatlan_tdk._utils import *`.
- `pyproject.toml`: csomagdefiníció, konzolparancsok, ruff (az E402-kivétel megszűnt).
- `Makefile`, `ci.yml`, `deploy-pages.yml`: a csomagparancsokra állítva.

### Hozzáadva / Megváltoztatva
- **Kanonikus adatséma** (`data/schema.yaml`): egységes változókészlet minden területre
  (127 oszlop), adatalapú sávhatárok (méret-kvantilisek 44/53/68 m², építési korszakok
  0-10/10-30/30-60/60+ év), rétegenkénti letöltési pufferek (vasút 2000 m, POI 1125 m,
  úthálózat 1250 m). Átnevezések: `city`→`varos`, `van_erkely`→`has_erkely`,
  `price_million_huf`→`ar_millio_ft`.
- **Fókuszmentesítés:** minden Mázsa-tér/belváros (CBD) változó, hivatkozás és konfig
  törölve (adatok, notebookok előkészítve, `areas.yaml`, `_utils`, `verify`, ADATKONYV).
- **Valódi hálózati távolságok:** az euklidészi × kerülőfaktor közelítést Dijkstra
  alapú OSM-úthálózati legrövidebb utak váltják (medián kerülőfaktor 1,75 a régi 1,25
  helyett); POI-sávok (`poi_5p/10p/15p_count`) hálózati elérhetőségen; a kőbányai
  vasúti réteg 2000 m-es pufferrel újratöltve (a korábbi alulméretezett volt),
  bécsi úthálózat + tranzit letöltve.
- Új szkriptek: `scripts/fetch_network_layers.py`, `scripts/network_metrics.py`,
  `scripts/canonize_schema.py`.
### Hozzáadva / Megváltoztatva (módszertani felülvizsgálat)
- **A 17 notebook teljes módszertani felülvizsgálata:** a fókusz (Mázsa/belváros)
  referenciák teljes eltávolítása; hardkódolt eredmény-számok megszüntetése (minden
  KPI a futtatott modellekből); doc–code konzisztencia; seed minden véletlenhez;
  a kanonikus sávok mindenhol a `_utils` konstansokból.
- **nb04:** Mann–Whitney U + Dunn post-hoc (Bonferroni), kontrollált zóna-diszkont
  (HC1), diszjunkt sáv-dummyk, immissziós dózis-válasz görbe bootstrap CI-vel,
  a 150 m-es küszöb placebo-vizsgálata, Chow-töréspont-teszt.
- **nb05:** a POI-sávok a kanonikus HÁLÓZATI `poi_5p/10p/15p_count` oszlopokból
  (a Web Mercator-légvonalas számítás törölve); POI-modellek F-teszttel, HC1-gyel.
- **nb07:** HC1 SE-k, helyes implicit-hatás értelmezés (dummy/log/folytonos),
  Breusch–Pagan + RESET, a JS-kalkulátor a TÉNYLEGES becsült együtthatókból.
- **nb09:** valódi SEM (ML_Error), SAR GM_Lag, Anselin LM-tesztek, permutációs
  Moran p-értékek, vetületi KNN.
- **nb10:** a szintetikus GWR-fallback törölve; 07/09-cel azonos kontrollok;
  t-szűrt (|t|≥1.96) β-térképek; VIF-diagnosztika; jitter az egybeeső pontokra.
- **nb11:** ismételt + TÉRBELI blokk-CV, out-of-sample arbitrázs, permutációs
  fontosság, kvantilis GB predikciós intervallumok, a fókusz-változó kivétele.
- **nb12:** hedonikusan párosított hozam, cap-rate érzékenység, térbeli rent gap
  (immissziós sáv × állapot), javított JS-kalkulátor.
- **nb13:** a volatilitások/korreláció a hedonikus reziduumokból kalibrálva;
  a tornado a szimulációból számolva; MC-SE jelentése.
- **nb14:** becslés-alapú felértékelődési potenciál (kontrollált sávdiszkontok),
  a Mázsa-szcenárió átnevezése, dinamikus medián a JS-presetekben.
- **nb15:** minden KPI a futtatott modellekből (hedonikus, SAR, rent gap, RF CV);
  a hatásgörbe a becsült együtthatókból.
- **nb16:** pooled hedonikus regresszió terület×immissziós sáv interakciókkal,
  EUR-normalizálás, CI-sávok, elemszám-küszöbök (N≥5/10).
### Javítva
- **Notebookok terület-univerzálissá tétele:** a kőbánya-specifikus oszlopokra
  (`tavolsag_mazsa_halozati_m`, `tavolsag_belvaros_halozati_m`, `szobaszam_kategoria`)
  való hivatkozások védettek — hiányzó oszlopnál a notebook leszármaztatja vagy kihagyja;
  a POI-betöltés területfüggő (`poi_{area}_buffered.geojson`) + `geopandas` import;
  a GWR együttható-kinyerés és a Random Forest szcenárió-mátrix a tényleges oszlopokhoz igazodik.
- `tdk-report`: a notebookok **returncode-ja valóban hibának számít** (korábban a
  sikertelen notebookok is „hibás notebook: 0"-ként jelentek meg) — a CI mostantól
  hangosan elhasal hiányos riport esetén.
### Hozzáadva / Megváltoztatva
- **Kanonikus adatséma** (`data/schema.yaml`): egységes változókészlet minden területre
  (127 oszlop), adatalapú sávhatárok (méret-kvantilisek 44/53/68 m², építési korszakok
  0-10/10-30/30-60/60+ év), rétegenkénti letöltési pufferek (vasút 2000 m, POI 1125 m,
  úthálózat 1250 m). Átnevezések: `city`→`varos`, `van_erkely`→`has_erkely`,
  `price_million_huf`→`ar_millio_ft`.
- **Fókuszmentesítés:** minden Mázsa-tér/belváros (CBD) változó, hivatkozás és konfig
  törölve (adatok, notebookok előkészítve, `areas.yaml`, `_utils`, `verify`, ADATKONYV).
- **Valódi hálózati távolságok:** az euklidészi × kerülőfaktor közelítést Dijkstra
  alapú OSM-úthálózati legrövidebb utak váltják (medián kerülőfaktor 1,75 a régi 1,25
  helyett); POI-sávok (`poi_5p/10p/15p_count`) hálózati elérhetőségen; a kőbányai
  vasúti réteg 2000 m-es pufferrel újratöltve (a korábbi alulméretezett volt),
  bécsi úthálózat + tranzit letöltve.
- Új szkriptek: `scripts/fetch_network_layers.py`, `scripts/network_metrics.py`,
  `scripts/canonize_schema.py`.
### Hozzáadva / Megváltoztatva (módszertani felülvizsgálat)
- **A 17 notebook teljes módszertani felülvizsgálata:** a fókusz (Mázsa/belváros)
  referenciák teljes eltávolítása; hardkódolt eredmény-számok megszüntetése (minden
  KPI a futtatott modellekből); doc–code konzisztencia; seed minden véletlenhez;
  a kanonikus sávok mindenhol a `_utils` konstansokból.
- **nb04:** Mann–Whitney U + Dunn post-hoc (Bonferroni), kontrollált zóna-diszkont
  (HC1), diszjunkt sáv-dummyk, immissziós dózis-válasz görbe bootstrap CI-vel,
  a 150 m-es küszöb placebo-vizsgálata, Chow-töréspont-teszt.
- **nb05:** a POI-sávok a kanonikus HÁLÓZATI `poi_5p/10p/15p_count` oszlopokból
  (a Web Mercator-légvonalas számítás törölve); POI-modellek F-teszttel, HC1-gyel.
- **nb07:** HC1 SE-k, helyes implicit-hatás értelmezés (dummy/log/folytonos),
  Breusch–Pagan + RESET, a JS-kalkulátor a TÉNYLEGES becsült együtthatókból.
- **nb09:** valódi SEM (ML_Error), SAR GM_Lag, Anselin LM-tesztek, permutációs
  Moran p-értékek, vetületi KNN.
- **nb10:** a szintetikus GWR-fallback törölve; 07/09-cel azonos kontrollok;
  t-szűrt (|t|≥1.96) β-térképek; VIF-diagnosztika; jitter az egybeeső pontokra.
- **nb11:** ismételt + TÉRBELI blokk-CV, out-of-sample arbitrázs, permutációs
  fontosság, kvantilis GB predikciós intervallumok, a fókusz-változó kivétele.
- **nb12:** hedonikusan párosított hozam, cap-rate érzékenység, térbeli rent gap
  (immissziós sáv × állapot), javított JS-kalkulátor.
- **nb13:** a volatilitások/korreláció a hedonikus reziduumokból kalibrálva;
  a tornado a szimulációból számolva; MC-SE jelentése.
- **nb14:** becslés-alapú felértékelődési potenciál (kontrollált sávdiszkontok),
  a Mázsa-szcenárió átnevezése, dinamikus medián a JS-presetekben.
- **nb15:** minden KPI a futtatott modellekből (hedonikus, SAR, rent gap, RF CV);
  a hatásgörbe a becsült együtthatókból.
- **nb16:** pooled hedonikus regresszió terület×immissziós sáv interakciókkal,
  EUR-normalizálás, CI-sávok, elemszám-küszöbök (N≥5/10).
### Javítva
- `tdk-report` időtúllépés-védelem: notebookonként `--ExecutePreprocessor.timeout` és
  szubprocessz-timeout, plusz BLAS-thread limit (`OMP/OPENBLAS/MKL_NUM_THREADS=1`) a
  CI-holtpontok ellen; a Pages build-job `timeout-minutes: 180`.
- A Plotly renderer `notebook`-ra állítva: az exportált HTML önálló (CDN plotly.js-re
  épülő) ábrákat tartalmaz a GitHub Pages-hez.
### Hozzáadva / Megváltoztatva
- **Kanonikus adatséma** (`data/schema.yaml`): egységes változókészlet minden területre
  (127 oszlop), adatalapú sávhatárok (méret-kvantilisek 44/53/68 m², építési korszakok
  0-10/10-30/30-60/60+ év), rétegenkénti letöltési pufferek (vasút 2000 m, POI 1125 m,
  úthálózat 1250 m). Átnevezések: `city`→`varos`, `van_erkely`→`has_erkely`,
  `price_million_huf`→`ar_millio_ft`.
- **Fókuszmentesítés:** minden Mázsa-tér/belváros (CBD) változó, hivatkozás és konfig
  törölve (adatok, notebookok előkészítve, `areas.yaml`, `_utils`, `verify`, ADATKONYV).
- **Valódi hálózati távolságok:** az euklidészi × kerülőfaktor közelítést Dijkstra
  alapú OSM-úthálózati legrövidebb utak váltják (medián kerülőfaktor 1,75 a régi 1,25
  helyett); POI-sávok (`poi_5p/10p/15p_count`) hálózati elérhetőségen; a kőbányai
  vasúti réteg 2000 m-es pufferrel újratöltve (a korábbi alulméretezett volt),
  bécsi úthálózat + tranzit letöltve.
- Új szkriptek: `scripts/fetch_network_layers.py`, `scripts/network_metrics.py`,
  `scripts/canonize_schema.py`.
### Hozzáadva / Megváltoztatva (módszertani felülvizsgálat)
- **A 17 notebook teljes módszertani felülvizsgálata:** a fókusz (Mázsa/belváros)
  referenciák teljes eltávolítása; hardkódolt eredmény-számok megszüntetése (minden
  KPI a futtatott modellekből); doc–code konzisztencia; seed minden véletlenhez;
  a kanonikus sávok mindenhol a `_utils` konstansokból.
- **nb04:** Mann–Whitney U + Dunn post-hoc (Bonferroni), kontrollált zóna-diszkont
  (HC1), diszjunkt sáv-dummyk, immissziós dózis-válasz görbe bootstrap CI-vel,
  a 150 m-es küszöb placebo-vizsgálata, Chow-töréspont-teszt.
- **nb05:** a POI-sávok a kanonikus HÁLÓZATI `poi_5p/10p/15p_count` oszlopokból
  (a Web Mercator-légvonalas számítás törölve); POI-modellek F-teszttel, HC1-gyel.
- **nb07:** HC1 SE-k, helyes implicit-hatás értelmezés (dummy/log/folytonos),
  Breusch–Pagan + RESET, a JS-kalkulátor a TÉNYLEGES becsült együtthatókból.
- **nb09:** valódi SEM (ML_Error), SAR GM_Lag, Anselin LM-tesztek, permutációs
  Moran p-értékek, vetületi KNN.
- **nb10:** a szintetikus GWR-fallback törölve; 07/09-cel azonos kontrollok;
  t-szűrt (|t|≥1.96) β-térképek; VIF-diagnosztika; jitter az egybeeső pontokra.
- **nb11:** ismételt + TÉRBELI blokk-CV, out-of-sample arbitrázs, permutációs
  fontosság, kvantilis GB predikciós intervallumok, a fókusz-változó kivétele.
- **nb12:** hedonikusan párosított hozam, cap-rate érzékenység, térbeli rent gap
  (immissziós sáv × állapot), javított JS-kalkulátor.
- **nb13:** a volatilitások/korreláció a hedonikus reziduumokból kalibrálva;
  a tornado a szimulációból számolva; MC-SE jelentése.
- **nb14:** becslés-alapú felértékelődési potenciál (kontrollált sávdiszkontok),
  a Mázsa-szcenárió átnevezése, dinamikus medián a JS-presetekben.
- **nb15:** minden KPI a futtatott modellekből (hedonikus, SAR, rent gap, RF CV);
  a hatásgörbe a becsült együtthatókból.
- **nb16:** pooled hedonikus regresszió terület×immissziós sáv interakciókkal,
  EUR-normalizálás, CI-sávok, elemszám-küszöbök (N≥5/10).
### Javítva
- **Notebookok terület-univerzálissá tétele:** a kőbánya-specifikus oszlopokra
  (`tavolsag_mazsa_halozati_m`, `tavolsag_belvaros_halozati_m`, `szobaszam_kategoria`)
  való hivatkozások védettek — hiányzó oszlopnál a notebook leszármaztatja vagy kihagyja;
  a POI-betöltés területfüggő (`poi_{area}_buffered.geojson`) + `geopandas` import;
  a GWR együttható-kinyerés és a Random Forest szcenárió-mátrix a tényleges oszlopokhoz igazodik.
- `tdk-report`: a notebookok **returncode-ja valóban hibának számít** (korábban a
  sikertelen notebookok is „hibás notebook: 0"-ként jelentek meg) — a CI mostantól
  hangosan elhasal hiányos riport esetén.
### Hozzáadva / Megváltoztatva
- **Kanonikus adatséma** (`data/schema.yaml`): egységes változókészlet minden területre
  (127 oszlop), adatalapú sávhatárok (méret-kvantilisek 44/53/68 m², építési korszakok
  0-10/10-30/30-60/60+ év), rétegenkénti letöltési pufferek (vasút 2000 m, POI 1125 m,
  úthálózat 1250 m). Átnevezések: `city`→`varos`, `van_erkely`→`has_erkely`,
  `price_million_huf`→`ar_millio_ft`.
- **Fókuszmentesítés:** minden Mázsa-tér/belváros (CBD) változó, hivatkozás és konfig
  törölve (adatok, notebookok előkészítve, `areas.yaml`, `_utils`, `verify`, ADATKONYV).
- **Valódi hálózati távolságok:** az euklidészi × kerülőfaktor közelítést Dijkstra
  alapú OSM-úthálózati legrövidebb utak váltják (medián kerülőfaktor 1,75 a régi 1,25
  helyett); POI-sávok (`poi_5p/10p/15p_count`) hálózati elérhetőségen; a kőbányai
  vasúti réteg 2000 m-es pufferrel újratöltve (a korábbi alulméretezett volt),
  bécsi úthálózat + tranzit letöltve.
- Új szkriptek: `scripts/fetch_network_layers.py`, `scripts/network_metrics.py`,
  `scripts/canonize_schema.py`.
### Hozzáadva / Megváltoztatva (módszertani felülvizsgálat)
- **A 17 notebook teljes módszertani felülvizsgálata:** a fókusz (Mázsa/belváros)
  referenciák teljes eltávolítása; hardkódolt eredmény-számok megszüntetése (minden
  KPI a futtatott modellekből); doc–code konzisztencia; seed minden véletlenhez;
  a kanonikus sávok mindenhol a `_utils` konstansokból.
- **nb04:** Mann–Whitney U + Dunn post-hoc (Bonferroni), kontrollált zóna-diszkont
  (HC1), diszjunkt sáv-dummyk, immissziós dózis-válasz görbe bootstrap CI-vel,
  a 150 m-es küszöb placebo-vizsgálata, Chow-töréspont-teszt.
- **nb05:** a POI-sávok a kanonikus HÁLÓZATI `poi_5p/10p/15p_count` oszlopokból
  (a Web Mercator-légvonalas számítás törölve); POI-modellek F-teszttel, HC1-gyel.
- **nb07:** HC1 SE-k, helyes implicit-hatás értelmezés (dummy/log/folytonos),
  Breusch–Pagan + RESET, a JS-kalkulátor a TÉNYLEGES becsült együtthatókból.
- **nb09:** valódi SEM (ML_Error), SAR GM_Lag, Anselin LM-tesztek, permutációs
  Moran p-értékek, vetületi KNN.
- **nb10:** a szintetikus GWR-fallback törölve; 07/09-cel azonos kontrollok;
  t-szűrt (|t|≥1.96) β-térképek; VIF-diagnosztika; jitter az egybeeső pontokra.
- **nb11:** ismételt + TÉRBELI blokk-CV, out-of-sample arbitrázs, permutációs
  fontosság, kvantilis GB predikciós intervallumok, a fókusz-változó kivétele.
- **nb12:** hedonikusan párosított hozam, cap-rate érzékenység, térbeli rent gap
  (immissziós sáv × állapot), javított JS-kalkulátor.
- **nb13:** a volatilitások/korreláció a hedonikus reziduumokból kalibrálva;
  a tornado a szimulációból számolva; MC-SE jelentése.
- **nb14:** becslés-alapú felértékelődési potenciál (kontrollált sávdiszkontok),
  a Mázsa-szcenárió átnevezése, dinamikus medián a JS-presetekben.
- **nb15:** minden KPI a futtatott modellekből (hedonikus, SAR, rent gap, RF CV);
  a hatásgörbe a becsült együtthatókból.
- **nb16:** pooled hedonikus regresszió terület×immissziós sáv interakciókkal,
  EUR-normalizálás, CI-sávok, elemszám-küszöbök (N≥5/10).
### Javítva
- **GitHub Actions hiba:** `requirements.txt` — a `pywinpty` Windows-only csomag
  platform-markerrel (`sys_platform == "win32"`), így a Linux CI telepítés már nem száll el.

### Eltávolítva
- `archive/` teljes törlése (a git history megőrzi); felesleges, hivatkozatlan
  fájlok: `kobanya_ingatlan_piac_teljes_1320db.xlsx`, `fresh_deep_analysis_metrics.json`,
  `belvaros_network_cache.json`, `kobanya_test_mapping.yaml`.

## [Nem kiadott] — Notebook-vezérelt minimális architektúra

### Megváltoztatva
- **A notebookok a gerinc:** a `NOTEBOOK_DOCS` módszertani szövegei (általános,
  területfüggetlen, placeholder-mentes formában) beolvasztva a 00–16 notebookokba
  markdown cellákként; a 16. notebook kapott komparatív bevezetőt.
- **Riportpipeline:** az új `tdk-report` a notebookokat futtatja (`nbconvert --execute`)
  és területenként exportálja a HTML-riportokat + index-oldalt generál;
  a terület a `TDK_ACTIVE_AREA` env-változóval választható.
- A véletlent használó notebookok determinisztikusak (seed-ek rögzítve; a GWR-jitter
  seeded RNG-re cserélve).

### Eltávolítva
- `report_engine/` (~2 800 sor), `notebook_docs.py`, `report_cli.py` — a párhuzamos
  elemző motor megszüntetve (ADR-0008).
- `checks.py`, `Makefile`, pre-commit, ruff-konfig — a betartatás a verify + pytest + CI
  magra szűkül.
- `html_reports/` kikerült a gitből (a Pages-CI generálja).

### Dokumentáció
- `CONTRIBUTING.md`, `AGENTS.md`, `README.md` az új architektúrához igazítva;
  `docs/decisions/0008-*.md` hozzáadva, az ADR-0003 felülírt státuszú.
## [2026-10-06] — Többterületes motor és bécsi benchmark

### Hozzáadva
- `report_engine/` — teljes elemző motor (FullAreaAnalyzer, FullNarrativeGenerator, FullHTMLReportBuilder).
- `generate_area_report.py`, `build_all.py`, `data_ingestion.py`.
- `data/areas.yaml`, `data/schema.yaml`, `data/mappings/`.
- Bécs Nordbahnhof adatok (1 037 hirdetés), `scripts/` beszerző/eszköz szkriptek.
- `verify_master_data.py`, `SHA256SUMS.txt` (14 mester fájl), `tests/test_integrity.py`.
- `html_reports/` többterületes portál, `notebooks/16_komparativ_harom_terulet_elemzes.ipynb`.

### Hozzáadva / Megváltoztatva
- **Kanonikus adatséma** (`data/schema.yaml`): egységes változókészlet minden területre
  (127 oszlop), adatalapú sávhatárok (méret-kvantilisek 44/53/68 m², építési korszakok
  0-10/10-30/30-60/60+ év), rétegenkénti letöltési pufferek (vasút 2000 m, POI 1125 m,
  úthálózat 1250 m). Átnevezések: `city`→`varos`, `van_erkely`→`has_erkely`,
  `price_million_huf`→`ar_millio_ft`.
- **Fókuszmentesítés:** minden Mázsa-tér/belváros (CBD) változó, hivatkozás és konfig
  törölve (adatok, notebookok előkészítve, `areas.yaml`, `_utils`, `verify`, ADATKONYV).
- **Valódi hálózati távolságok:** az euklidészi × kerülőfaktor közelítést Dijkstra
  alapú OSM-úthálózati legrövidebb utak váltják (medián kerülőfaktor 1,75 a régi 1,25
  helyett); POI-sávok (`poi_5p/10p/15p_count`) hálózati elérhetőségen; a kőbányai
  vasúti réteg 2000 m-es pufferrel újratöltve (a korábbi alulméretezett volt),
  bécsi úthálózat + tranzit letöltve.
- Új szkriptek: `scripts/fetch_network_layers.py`, `scripts/network_metrics.py`,
  `scripts/canonize_schema.py`.
### Hozzáadva / Megváltoztatva (módszertani felülvizsgálat)
- **A 17 notebook teljes módszertani felülvizsgálata:** a fókusz (Mázsa/belváros)
  referenciák teljes eltávolítása; hardkódolt eredmény-számok megszüntetése (minden
  KPI a futtatott modellekből); doc–code konzisztencia; seed minden véletlenhez;
  a kanonikus sávok mindenhol a `_utils` konstansokból.
- **nb04:** Mann–Whitney U + Dunn post-hoc (Bonferroni), kontrollált zóna-diszkont
  (HC1), diszjunkt sáv-dummyk, immissziós dózis-válasz görbe bootstrap CI-vel,
  a 150 m-es küszöb placebo-vizsgálata, Chow-töréspont-teszt.
- **nb05:** a POI-sávok a kanonikus HÁLÓZATI `poi_5p/10p/15p_count` oszlopokból
  (a Web Mercator-légvonalas számítás törölve); POI-modellek F-teszttel, HC1-gyel.
- **nb07:** HC1 SE-k, helyes implicit-hatás értelmezés (dummy/log/folytonos),
  Breusch–Pagan + RESET, a JS-kalkulátor a TÉNYLEGES becsült együtthatókból.
- **nb09:** valódi SEM (ML_Error), SAR GM_Lag, Anselin LM-tesztek, permutációs
  Moran p-értékek, vetületi KNN.
- **nb10:** a szintetikus GWR-fallback törölve; 07/09-cel azonos kontrollok;
  t-szűrt (|t|≥1.96) β-térképek; VIF-diagnosztika; jitter az egybeeső pontokra.
- **nb11:** ismételt + TÉRBELI blokk-CV, out-of-sample arbitrázs, permutációs
  fontosság, kvantilis GB predikciós intervallumok, a fókusz-változó kivétele.
- **nb12:** hedonikusan párosított hozam, cap-rate érzékenység, térbeli rent gap
  (immissziós sáv × állapot), javított JS-kalkulátor.
- **nb13:** a volatilitások/korreláció a hedonikus reziduumokból kalibrálva;
  a tornado a szimulációból számolva; MC-SE jelentése.
- **nb14:** becslés-alapú felértékelődési potenciál (kontrollált sávdiszkontok),
  a Mázsa-szcenárió átnevezése, dinamikus medián a JS-presetekben.
- **nb15:** minden KPI a futtatott modellekből (hedonikus, SAR, rent gap, RF CV);
  a hatásgörbe a becsült együtthatókból.
- **nb16:** pooled hedonikus regresszió terület×immissziós sáv interakciókkal,
  EUR-normalizálás, CI-sávok, elemszám-küszöbök (N≥5/10).
### Javítva
- **Notebookok terület-univerzálissá tétele:** a kőbánya-specifikus oszlopokra
  (`tavolsag_mazsa_halozati_m`, `tavolsag_belvaros_halozati_m`, `szobaszam_kategoria`)
  való hivatkozások védettek — hiányzó oszlopnál a notebook leszármaztatja vagy kihagyja;
  a POI-betöltés területfüggő (`poi_{area}_buffered.geojson`) + `geopandas` import;
  a GWR együttható-kinyerés és a Random Forest szcenárió-mátrix a tényleges oszlopokhoz igazodik.
- `tdk-report`: a notebookok **returncode-ja valóban hibának számít** (korábban a
  sikertelen notebookok is „hibás notebook: 0"-ként jelentek meg) — a CI mostantól
  hangosan elhasal hiányos riport esetén.
### Hozzáadva / Megváltoztatva
- **Kanonikus adatséma** (`data/schema.yaml`): egységes változókészlet minden területre
  (127 oszlop), adatalapú sávhatárok (méret-kvantilisek 44/53/68 m², építési korszakok
  0-10/10-30/30-60/60+ év), rétegenkénti letöltési pufferek (vasút 2000 m, POI 1125 m,
  úthálózat 1250 m). Átnevezések: `city`→`varos`, `van_erkely`→`has_erkely`,
  `price_million_huf`→`ar_millio_ft`.
- **Fókuszmentesítés:** minden Mázsa-tér/belváros (CBD) változó, hivatkozás és konfig
  törölve (adatok, notebookok előkészítve, `areas.yaml`, `_utils`, `verify`, ADATKONYV).
- **Valódi hálózati távolságok:** az euklidészi × kerülőfaktor közelítést Dijkstra
  alapú OSM-úthálózati legrövidebb utak váltják (medián kerülőfaktor 1,75 a régi 1,25
  helyett); POI-sávok (`poi_5p/10p/15p_count`) hálózati elérhetőségen; a kőbányai
  vasúti réteg 2000 m-es pufferrel újratöltve (a korábbi alulméretezett volt),
  bécsi úthálózat + tranzit letöltve.
- Új szkriptek: `scripts/fetch_network_layers.py`, `scripts/network_metrics.py`,
  `scripts/canonize_schema.py`.
### Hozzáadva / Megváltoztatva (módszertani felülvizsgálat)
- **A 17 notebook teljes módszertani felülvizsgálata:** a fókusz (Mázsa/belváros)
  referenciák teljes eltávolítása; hardkódolt eredmény-számok megszüntetése (minden
  KPI a futtatott modellekből); doc–code konzisztencia; seed minden véletlenhez;
  a kanonikus sávok mindenhol a `_utils` konstansokból.
- **nb04:** Mann–Whitney U + Dunn post-hoc (Bonferroni), kontrollált zóna-diszkont
  (HC1), diszjunkt sáv-dummyk, immissziós dózis-válasz görbe bootstrap CI-vel,
  a 150 m-es küszöb placebo-vizsgálata, Chow-töréspont-teszt.
- **nb05:** a POI-sávok a kanonikus HÁLÓZATI `poi_5p/10p/15p_count` oszlopokból
  (a Web Mercator-légvonalas számítás törölve); POI-modellek F-teszttel, HC1-gyel.
- **nb07:** HC1 SE-k, helyes implicit-hatás értelmezés (dummy/log/folytonos),
  Breusch–Pagan + RESET, a JS-kalkulátor a TÉNYLEGES becsült együtthatókból.
- **nb09:** valódi SEM (ML_Error), SAR GM_Lag, Anselin LM-tesztek, permutációs
  Moran p-értékek, vetületi KNN.
- **nb10:** a szintetikus GWR-fallback törölve; 07/09-cel azonos kontrollok;
  t-szűrt (|t|≥1.96) β-térképek; VIF-diagnosztika; jitter az egybeeső pontokra.
- **nb11:** ismételt + TÉRBELI blokk-CV, out-of-sample arbitrázs, permutációs
  fontosság, kvantilis GB predikciós intervallumok, a fókusz-változó kivétele.
- **nb12:** hedonikusan párosított hozam, cap-rate érzékenység, térbeli rent gap
  (immissziós sáv × állapot), javított JS-kalkulátor.
- **nb13:** a volatilitások/korreláció a hedonikus reziduumokból kalibrálva;
  a tornado a szimulációból számolva; MC-SE jelentése.
- **nb14:** becslés-alapú felértékelődési potenciál (kontrollált sávdiszkontok),
  a Mázsa-szcenárió átnevezése, dinamikus medián a JS-presetekben.
- **nb15:** minden KPI a futtatott modellekből (hedonikus, SAR, rent gap, RF CV);
  a hatásgörbe a becsült együtthatókból.
- **nb16:** pooled hedonikus regresszió terület×immissziós sáv interakciókkal,
  EUR-normalizálás, CI-sávok, elemszám-küszöbök (N≥5/10).
### Javítva
- `tdk-report` időtúllépés-védelem: notebookonként `--ExecutePreprocessor.timeout` és
  szubprocessz-timeout, plusz BLAS-thread limit (`OMP/OPENBLAS/MKL_NUM_THREADS=1`) a
  CI-holtpontok ellen; a Pages build-job `timeout-minutes: 180`.
- A Plotly renderer `notebook`-ra állítva: az exportált HTML önálló (CDN plotly.js-re
  épülő) ábrákat tartalmaz a GitHub Pages-hez.
### Hozzáadva / Megváltoztatva
- **Kanonikus adatséma** (`data/schema.yaml`): egységes változókészlet minden területre
  (127 oszlop), adatalapú sávhatárok (méret-kvantilisek 44/53/68 m², építési korszakok
  0-10/10-30/30-60/60+ év), rétegenkénti letöltési pufferek (vasút 2000 m, POI 1125 m,
  úthálózat 1250 m). Átnevezések: `city`→`varos`, `van_erkely`→`has_erkely`,
  `price_million_huf`→`ar_millio_ft`.
- **Fókuszmentesítés:** minden Mázsa-tér/belváros (CBD) változó, hivatkozás és konfig
  törölve (adatok, notebookok előkészítve, `areas.yaml`, `_utils`, `verify`, ADATKONYV).
- **Valódi hálózati távolságok:** az euklidészi × kerülőfaktor közelítést Dijkstra
  alapú OSM-úthálózati legrövidebb utak váltják (medián kerülőfaktor 1,75 a régi 1,25
  helyett); POI-sávok (`poi_5p/10p/15p_count`) hálózati elérhetőségen; a kőbányai
  vasúti réteg 2000 m-es pufferrel újratöltve (a korábbi alulméretezett volt),
  bécsi úthálózat + tranzit letöltve.
- Új szkriptek: `scripts/fetch_network_layers.py`, `scripts/network_metrics.py`,
  `scripts/canonize_schema.py`.
### Hozzáadva / Megváltoztatva (módszertani felülvizsgálat)
- **A 17 notebook teljes módszertani felülvizsgálata:** a fókusz (Mázsa/belváros)
  referenciák teljes eltávolítása; hardkódolt eredmény-számok megszüntetése (minden
  KPI a futtatott modellekből); doc–code konzisztencia; seed minden véletlenhez;
  a kanonikus sávok mindenhol a `_utils` konstansokból.
- **nb04:** Mann–Whitney U + Dunn post-hoc (Bonferroni), kontrollált zóna-diszkont
  (HC1), diszjunkt sáv-dummyk, immissziós dózis-válasz görbe bootstrap CI-vel,
  a 150 m-es küszöb placebo-vizsgálata, Chow-töréspont-teszt.
- **nb05:** a POI-sávok a kanonikus HÁLÓZATI `poi_5p/10p/15p_count` oszlopokból
  (a Web Mercator-légvonalas számítás törölve); POI-modellek F-teszttel, HC1-gyel.
- **nb07:** HC1 SE-k, helyes implicit-hatás értelmezés (dummy/log/folytonos),
  Breusch–Pagan + RESET, a JS-kalkulátor a TÉNYLEGES becsült együtthatókból.
- **nb09:** valódi SEM (ML_Error), SAR GM_Lag, Anselin LM-tesztek, permutációs
  Moran p-értékek, vetületi KNN.
- **nb10:** a szintetikus GWR-fallback törölve; 07/09-cel azonos kontrollok;
  t-szűrt (|t|≥1.96) β-térképek; VIF-diagnosztika; jitter az egybeeső pontokra.
- **nb11:** ismételt + TÉRBELI blokk-CV, out-of-sample arbitrázs, permutációs
  fontosság, kvantilis GB predikciós intervallumok, a fókusz-változó kivétele.
- **nb12:** hedonikusan párosított hozam, cap-rate érzékenység, térbeli rent gap
  (immissziós sáv × állapot), javított JS-kalkulátor.
- **nb13:** a volatilitások/korreláció a hedonikus reziduumokból kalibrálva;
  a tornado a szimulációból számolva; MC-SE jelentése.
- **nb14:** becslés-alapú felértékelődési potenciál (kontrollált sávdiszkontok),
  a Mázsa-szcenárió átnevezése, dinamikus medián a JS-presetekben.
- **nb15:** minden KPI a futtatott modellekből (hedonikus, SAR, rent gap, RF CV);
  a hatásgörbe a becsült együtthatókból.
- **nb16:** pooled hedonikus regresszió terület×immissziós sáv interakciókkal,
  EUR-normalizálás, CI-sávok, elemszám-küszöbök (N≥5/10).
### Javítva
- **Notebookok terület-univerzálissá tétele:** a kőbánya-specifikus oszlopokra
  (`tavolsag_mazsa_halozati_m`, `tavolsag_belvaros_halozati_m`, `szobaszam_kategoria`)
  való hivatkozások védettek — hiányzó oszlopnál a notebook leszármaztatja vagy kihagyja;
  a POI-betöltés területfüggő (`poi_{area}_buffered.geojson`) + `geopandas` import;
  a GWR együttható-kinyerés és a Random Forest szcenárió-mátrix a tényleges oszlopokhoz igazodik.
- `tdk-report`: a notebookok **returncode-ja valóban hibának számít** (korábban a
  sikertelen notebookok is „hibás notebook: 0"-ként jelentek meg) — a CI mostantól
  hangosan elhasal hiányos riport esetén.
### Hozzáadva / Megváltoztatva
- **Kanonikus adatséma** (`data/schema.yaml`): egységes változókészlet minden területre
  (127 oszlop), adatalapú sávhatárok (méret-kvantilisek 44/53/68 m², építési korszakok
  0-10/10-30/30-60/60+ év), rétegenkénti letöltési pufferek (vasút 2000 m, POI 1125 m,
  úthálózat 1250 m). Átnevezések: `city`→`varos`, `van_erkely`→`has_erkely`,
  `price_million_huf`→`ar_millio_ft`.
- **Fókuszmentesítés:** minden Mázsa-tér/belváros (CBD) változó, hivatkozás és konfig
  törölve (adatok, notebookok előkészítve, `areas.yaml`, `_utils`, `verify`, ADATKONYV).
- **Valódi hálózati távolságok:** az euklidészi × kerülőfaktor közelítést Dijkstra
  alapú OSM-úthálózati legrövidebb utak váltják (medián kerülőfaktor 1,75 a régi 1,25
  helyett); POI-sávok (`poi_5p/10p/15p_count`) hálózati elérhetőségen; a kőbányai
  vasúti réteg 2000 m-es pufferrel újratöltve (a korábbi alulméretezett volt),
  bécsi úthálózat + tranzit letöltve.
- Új szkriptek: `scripts/fetch_network_layers.py`, `scripts/network_metrics.py`,
  `scripts/canonize_schema.py`.
### Hozzáadva / Megváltoztatva (módszertani felülvizsgálat)
- **A 17 notebook teljes módszertani felülvizsgálata:** a fókusz (Mázsa/belváros)
  referenciák teljes eltávolítása; hardkódolt eredmény-számok megszüntetése (minden
  KPI a futtatott modellekből); doc–code konzisztencia; seed minden véletlenhez;
  a kanonikus sávok mindenhol a `_utils` konstansokból.
- **nb04:** Mann–Whitney U + Dunn post-hoc (Bonferroni), kontrollált zóna-diszkont
  (HC1), diszjunkt sáv-dummyk, immissziós dózis-válasz görbe bootstrap CI-vel,
  a 150 m-es küszöb placebo-vizsgálata, Chow-töréspont-teszt.
- **nb05:** a POI-sávok a kanonikus HÁLÓZATI `poi_5p/10p/15p_count` oszlopokból
  (a Web Mercator-légvonalas számítás törölve); POI-modellek F-teszttel, HC1-gyel.
- **nb07:** HC1 SE-k, helyes implicit-hatás értelmezés (dummy/log/folytonos),
  Breusch–Pagan + RESET, a JS-kalkulátor a TÉNYLEGES becsült együtthatókból.
- **nb09:** valódi SEM (ML_Error), SAR GM_Lag, Anselin LM-tesztek, permutációs
  Moran p-értékek, vetületi KNN.
- **nb10:** a szintetikus GWR-fallback törölve; 07/09-cel azonos kontrollok;
  t-szűrt (|t|≥1.96) β-térképek; VIF-diagnosztika; jitter az egybeeső pontokra.
- **nb11:** ismételt + TÉRBELI blokk-CV, out-of-sample arbitrázs, permutációs
  fontosság, kvantilis GB predikciós intervallumok, a fókusz-változó kivétele.
- **nb12:** hedonikusan párosított hozam, cap-rate érzékenység, térbeli rent gap
  (immissziós sáv × állapot), javított JS-kalkulátor.
- **nb13:** a volatilitások/korreláció a hedonikus reziduumokból kalibrálva;
  a tornado a szimulációból számolva; MC-SE jelentése.
- **nb14:** becslés-alapú felértékelődési potenciál (kontrollált sávdiszkontok),
  a Mázsa-szcenárió átnevezése, dinamikus medián a JS-presetekben.
- **nb15:** minden KPI a futtatott modellekből (hedonikus, SAR, rent gap, RF CV);
  a hatásgörbe a becsült együtthatókból.
- **nb16:** pooled hedonikus regresszió terület×immissziós sáv interakciókkal,
  EUR-normalizálás, CI-sávok, elemszám-küszöbök (N≥5/10).
### Javítva
- `notebooks/_utils.py` — `area=None` alapértelmezések (a notebookok újra futtathatók).
- `requirements.txt` — `spreg`, `mgwr`, `markdown` pótlása (SAR/SEM és GWR reprodukálható).
- `load_pontos_geojson` fájlnevek a tényleges geojsonokhoz igazítva.
- GitHub Actions: a Pages a `html_reports/`-ból épül és deployol.

### Ismert anomália
- 1 rekord vasúti izokrón-inkonzisztenciája (`listing_id 35461173`) — rögzített
  kivételként dokumentálva a `verify_master_data.py`-ban és az ADATKONYV-ban.
