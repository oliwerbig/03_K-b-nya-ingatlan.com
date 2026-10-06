# Kőbánya Ingatlanpiaci Elemzés 2026 - TDK Kutatás

Ez a repozitórium egy átfogó, **17 modulból** álló, adatalapú ingatlanpiaci és térökonometriai kutatást tartalmaz Budapest X. kerületéről (Kőbánya), kiegészítve egy **nemzetközi benchmarkkal** (Bécs 2. kerület, Nordbahnhof). A kutatás célja az árazási dinamikák, a térbeli heterogenitás és a környezeti externáliák (vasút, tranzit, szolgáltatások) hatásának feltárása, valamint predikciós modellekkel az arbitrázslehetőségek és befektetési kockázatok azonosítása.

## Architektúra

A projekt egy **notebook-vezérelt, kanonizált riportpipeline**:

| Réteg | Hely | Szerep |
|---|---|---|
| **Elemző gerinc** | `notebooks/00–16.ipynb` | MINDEN számítás + módszertani dokumentáció, területfüggetlenül |
| Nyers adatok | `data/raw/` | Kapart alapadatok (érintetlen) |
| Számított adatok | `data/processed/` | Geokódolt + hálózati távolságok + hedonikus dummyk |
| Kanonikus séma | `data/schema.yaml` | Rögzített mezők és kutatási sávok (immissziós + izokrón) |
| Területi konfig | `data/areas.yaml` | Kőbánya (fő), Bécs Nordbahnhof (benchmark), további kontrollok |
| Kódcsomag | `src/ingatlan_tdk/` | Betöltés (`_utils`), séma (`data_io`), integritás (`verify`), CLI |
| Riportkimenet | `html_reports/` | „Baked" HTML-riportok területenként (a CI generálja) |
| Adatintegritás | `SHA256SUMS.txt` | Hash-hitelesített „frozen baseline" |

## Gyors indítás

```bash
# Függőségek telepítése (ajánlott virtuális környezetben)
pip install -r requirements.txt
pip install -e .   # a csomag és a tdk-* konzolparancsok

# Adatintegritás-ellenőrzés (SHA-256 hash + szerkezeti invariánsok)
python -m ingatlan_tdk verify

# Riportok generálása a notebookokból (területenként „baked" HTML + index)
python -m ingatlan_tdk report --area kobanya   # egy terület
python -m ingatlan_tdk report --all            # az összes regisztrált terület

# Fejlesztői ellenőrzések (ruff + tesztek + struktúra) — make nélkül is fut:
#   pip install -r requirements-dev.txt
#   make check   (vagy: python -m ruff check . / python tests/test_integrity.py / python check_structure.py)
```

A generált többterületes HTML-portál a [`html_reports/index.html`](html_reports/index.html) fájlban nyílik meg.

## A Kutatás Logikai Felépítése (Storyline)

A projekt nem 17 különálló elemzés, hanem egy egymásra épülő, szorosan integrált **modell-evolúciós narratíva**. A cél a klasszikus „tankönyvi" modellektől indulva, az abban rejlő hibákat feltárva eljutni a legmodernebb térökonometriai és gépi tanulási predikciókig.

### I. Adatfeltárás és Alapozás
1. **[00. Adathalmaz áttekintése](html_reports/kobanya/chapters/00_adathalmaz_attekintes.html):** Adatmegismerés és kritikus adattisztítás, fókuszban a geokódolás pontosságával.
2. **[01. Leíró statisztika és EDA](html_reports/kobanya/chapters/01_leiro_statisztika_es_eda.html):** Az árak és alapterületek alapvető eloszlásai (átlagárak, szórások, outlierek).
3. **[02. Árstruktúra és szegmentáció](html_reports/kobanya/chapters/02_arstruktura_es_szegmentacio.html):** A fő kategóriák izolálása, pl. a tényleges paneldiszkont (13.5%).
4. **[03. Térbeli Elemzés és Térképek](html_reports/kobanya/chapters/03_terbeli_elemzes_es_terkepek.html):** Árrobbanási gócok és sűrűségi hotspotok hőtérképeken.

### II. Városszerkezet és Környezeti Externáliák
5. **[04. Vasúti Paradoxon és Izokrónok](html_reports/kobanya/chapters/04_vasuti_paradoxon_es_izokronok.html):** A vasút negatív externáliájának (zaj, elvágó hatás) és a pozitív TOD-hatás szétválasztása (-15.5% értékvesztés a közvetlen zónában).
6. **[05. POI hálózat és 15-perces város](html_reports/kobanya/chapters/05_poi_es_15_perces_varos.html):** A pozitív externáliák vizsgálata: gyalogos sétatávon belüli szolgáltatássűrűség.
7. **[06. Klaszter és Tipológia](html_reports/kobanya/chapters/06_klaszter_es_tipologia.html):** Nem felügyelt gépi tanulással a lakáspiac rejtett típusokra bontása.

### III. Az Árazási Modellek Evolúciója
8. **[07. Hedonikus Ármodell (OLS)](html_reports/kobanya/chapters/07_hedonikus_armodell.html):** A klasszikus lineáris alapmodell.
9. **[08. Térbeli Autokorreláció (Moran's I)](html_reports/kobanya/chapters/08_moran_es_autokorrelacio.html):** *Kritika:* a szomszédok árai korrelálnak, az OLS függetlenségi feltétele sérül.
10. **[09. Térökonometria (SAR és SEM)](html_reports/kobanya/chapters/09_terokonometria_sar_sem.html):** *Javítás 1:* globális térbeli modellek szomszédsági súlymátrixszal.
11. **[10. Lokális Térökonometria (GWR)](html_reports/kobanya/chapters/10_lokalis_terokonometria_gwr.html):** *Javítás 2:* lokális térbeli heterogenitás (a metró közelsége máshogy hat Újhegyen, mint a Gyárdűlőn).
12. **[11. Gépi Tanulás és Arbitrázs](html_reports/kobanya/chapters/11_gepi_tanulas_es_arbitrazs.html):** *Paradigmaváltás:* XGBoost-predikció az alulárazott (arbitrázs) lakások azonosítására.

### IV. Beruházási Dinamika és Kockázat
13. **[12. Bérleti Piac és Rent Gap](html_reports/kobanya/chapters/12_berleti_piac_es_rent_gap.html):** Bérleti hozamok, Price-to-Rent és felújítási potenciál (Rent Gap).
14. **[13. Monte Carlo Kockázatelemzés](html_reports/kobanya/chapters/13_monte_carlo_kockazat.html):** Sztochasztikus modellezés a veszteség valószínűségéről (VaR).
15. **[14. LVC (Land Value Capture) Szimuláció](html_reports/kobanya/chapters/14_lvc_szimulacio.html):** Egy infrastrukturális beruházás okozta értéknövekedés és az „érték-visszanyerés" szimulációja.

### V. Felhasználói Alkalmazás és Nemzetközi Összehasonlítás
16. **[15. Interaktív Ingatlan Kereső Dashboard](html_reports/kobanya/chapters/15_ingatlan_kereso_dashboard.html):** A kutatási adatbázisra épülő, bárki által használható interaktív szűrési felület.
17. **[16. Komparatív Háromterületes Elemzés](notebooks/16_komparativ_harom_terulet_elemzes.ipynb):** Kőbánya összehasonlítása a bécsi Nordbahnhof benchmarkkal és a kontrollterületekkel. A összesítő eredmények a [központi portálon](html_reports/index.html) is láthatók.

## Adatintegritás és reprodukálhatóság

- A „frozen baseline" mester adatfájljainak SHA-256 ellenőrző összegei a `SHA256SUMS.txt`-ben.
- A `verify_master_data.py` ellenőrzi a hash-eket és a szerkezeti invariánsokat (rekordszám, precizitási arányok, útvonal-integritás, izokrón-hierarchia).
- A részletes adatszótár és módszertan: [`docs/ADATKONYV_ES_METADATA.md`](docs/ADATKONYV_ES_METADATA.md).
- A kapart forrás-HTML-ek nincsenek archiválva a repóban; az elsődleges nyers forrás a `data/raw/kobanya_parsed_raw_corpus.json` (tisztított JSON korpusz).

## Konvenciók és fejlesztés

A projekt teljes strukturális, elnevezési és munkafolyamat-szabályzata egy helyen,
**géppel ellenőrizhetően** van rögzítve:

- [`CONTRIBUTING.md`](CONTRIBUTING.md) — a projekt „alkotmánya": mappatérkép, adatszabályok, elnevezések, commit-konvenció, Definition of Done.
- [`AGENTS.md`](AGENTS.md) — utasítások AI-asszisztenseknek.
- [`CHANGELOG.md`](CHANGELOG.md) — változásnapló (Keep a Changelog formátum).
- Döntésnapló: [`docs/decisions/`](docs/decisions/) — Architecture Decision Records (ADR).
- Licenc: [`LICENSE`](LICENSE) (MIT, a kódra).
- A szabályok betartatása: a `.github/workflows/ci.yml` (verify + pytest) és a `deploy-pages.yml` (verify → riport → Pages).
