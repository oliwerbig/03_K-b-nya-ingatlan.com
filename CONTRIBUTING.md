# Hozzájárulási és projektkonvenciós szabályzat

> Ez a fájl a projekt „alkotmánya": itt van rögzítve minden strukturális, elnevezési
> és munkafolyamat-szabály. Minden változtatásnak meg kell felelnie ezeknek; a
> géppel ellenőrizhető részét a `check_structure.py`, a `make check` és a CI
> (`.github/workflows/ci.yml`) kényszeríti ki.

## 1. Projektcél és vízió (röviden)

Adatalapú ingatlanpiaci és térökonometriai TDK-kutatás Budapest X. kerületéről
(Kőbánya), nemzetközi benchmarkkal (Bécs 2. kerület, Nordbahnhof). A keretrendszer
**konfiguráció-vezérelt**: új terület felvétele csak konfiguráció (és adat), kód
nélkül. Az adatbázisok hash-hitelesített „frozen baseline"-ként viselkednek.
Részletes leírás: [`README.md`](README.md).

## 2. Kanonikus mappatérkép

```
gyökér/
├── README.md, CONTRIBUTING.md, AGENTS.md, CHANGELOG.md   # dokumentáció (bejárat + szabályzat)
├── Makefile, pyproject.toml, .editorconfig               # build- és stíluskonfig
├── requirements.txt, requirements-dev.txt                # függőségek (futtatás / fejlesztés)
├── SHA256SUMS.txt                                        # frozen baseline hash-manifest
├── build_all.py            # AZ EGYETLEN hivatalos belépési pont
├── generate_area_report.py # elemző motor CLI
├── verify_master_data.py   # adatintegritás-ellenőrzés
├── check_structure.py      # struktúra-/konvenció-ellenőrzés
├── data_ingestion.py       # séma-validáló betöltő könyvtár
├── Start_JupyterLab.bat    # interaktív Jupyter-indító (Windows)
├── docs/                   # adatszótár és módszertani dokumentáció (ADATKONYV)
├── data/
│   ├── raw/                # 1. réteg: kapart, ÉRINTETLEN adat
│   ├── processed/          # 2. réteg: generált, számított adat (tilos kézzel szerkeszteni)
│   ├── schema.yaml         # kanonikus adatséma
│   ├── areas.yaml          # területi regiszter (kobanya, wien_nordbahnhof, ...)
│   └── mappings/           # nyers → kanonikus oszlopleképezések (YAML)
├── notebooks/              # interaktív elemző réteg: 00–16.ipynb + _utils.py
├── report_engine/          # az elemző motor (full_analyzer, full_narrative, full_html_builder, notebook_docs)
├── scripts/                # adatbeszerző/eszköz szkriptek (fetch_*, enrich_*, preprocess_*)
├── tests/                  # pytest tesztek (tests/test_*.py)
├── html_reports/           # az EGYETLEN generált kimenet (publikációs portál)
├── archive/                # minden elavult, nem aktív állomány
└── .github/workflows/      # deploy-pages.yml + ci.yml
```

## 3. Adatréteg-szabályok (legfontosabb)

1. **Két réteg, szigorúan elválasztva:**
   - `data/raw/` — a kapart/alap adatok, **immutábilisak** (sose módosítjuk).
   - `data/processed/` — minden generált/számított állomány. **TILOS kézzel
     szerkeszteni** — kizárólag a generáló szkriptek (`scripts/`) írhatják.
2. **Kanonikus séma:** `data/schema.yaml` rögzíti a mezőket, típusokat és a
   kutatási sávokat (immissziós + izokrón). Minden betöltés a
   `data_ingestion.load_and_validate()`-on át menjen.
3. **Területi regiszter:** `data/areas.yaml` — új területet CSAK itt és adatfájlokkal
   lehet felvenni (lásd 10. szakasz), kódmódosítás nélkül.
4. **Frozen baseline:** a mester adatfájlok SHA-256 hash-e a `SHA256SUMS.txt`-ben.
   Ha egy `data/` fájl változik: `python verify_master_data.py --gen-sums`, majd
   `python verify_master_data.py` kötelező.
5. **Oszlopleképezések:** az idegen források oszlopait a `data/mappings/*_mapping.yaml`
   írja le (a `scripts/preprocess_new_data.py` generálja és használja).

## 4. Elnevezési konvenciók

- **Fájlok és mappák:** `snake_case`, csak ASCII kisbetű/számjegy/aláhúzás.
  Kivételek: a rögzített konvenciónevek (`README.md`, `CONTRIBUTING.md`,
  `AGENTS.md`, `CHANGELOG.md`, `Makefile`, `SHA256SUMS.txt`).
- **Notebookok:** `NN_tema_nev.ipynb`, ahol `NN` kétszámjegyű sorszám (00–16),
  **szinkronban a `report_engine` fejezeteivel** (00–15). Új notebook = új fejezet
  a motorban is, ellenkező esetben tilos.
- **Szkriptek:** igei prefix az eszközöknek (`fetch_`, `enrich_`, `preprocess_`);
  a gyökérben csak a 2. szakaszban felsorolt belépési pontok élhetnek.
- **Oszlopnevek:** a `data/schema.yaml`-ban rögzítettek szerint; boolean dummy-k
  `is_*` (tulajdonság) vagy `has_*` (felszereltség) prefixszel; távolság/idő
  mezők `tavolsag_*_m`, `menetido_*_perc` utótaggal.
- **Tesztek:** `tests/test_*.py`, függvénynevek `test_*`.

## 5. Nyelvi politika

- **Magyar:** a felhasználó felé néző dokumentáció és szöveg (README, CONTRIBUTING,
  ADATKONYV, notebook-markdownok, CHANGELOG).
- **Angol:** a commit-üzenetek (Conventional Commits — a history ezt követi).
- **Kód:** a meglévő magyar domain- és adatnevek **maradnak** (`load_szamitott_master`,
  `tavolsag_vasut_m`, `varosresz` — ezek az adatséma részei, átnevezésük tilos).
  Új, nem-domain kötött technikai kód (scriptek, tesztek, segédfüggvények)
  preferáltan angolul íródik.

## 6. Notebook-szabályok

1. Minden notebook a `notebooks/_utils.py`-ból importál; adatbetöltés
   `load_szamitott_master()` **argumentum nélkül** (az `areas.yaml` `active_area`-ját
   használja).
2. A 00–15 fejezetek a `report_engine/full_analyzer.py` moduljaival 1:1 szinkronban
   vannak: ha egy notebook számítása változik, a motorba is be kell vezetni.
3. A notebookok a kiadott riportokhoz vezető út dokumentációi; a kanonikus,
   publikált kimenet a `html_reports/` (a `report_engine` generálja).
4. Checkpoint-mappák (`.ipynb_checkpoints`) és `__pycache__` **nem kerülhetnek
   a repóba** (a `.gitignore` és a `check_structure.py` is védi).

## 7. Belépési pontok

| Parancs | Szerep |
|---|---|
| `python build_all.py` | **Az egyetlen hivatalos** teljes csővezeték: verify → riport → verify |
| `python generate_area_report.py --all` | Elemző motor + HTML riportok (kobanya + wien) |
| `python verify_master_data.py` | Hash- és szerkezeti integritás |
| `python check_structure.py` | Repo-struktúra és konvenciók ellenőrzése |
| `make check` | Minden fenti egyben (ruff, compileall, verify, pytest, struktúra) |

Minden más, a gyökérben található szkript legacy státuszú, és az `archive/` mappába
tartozik.

## 8. Commit-konvenció (Conventional Commits)

- Formátum: `<type>: <rövid leírás>` — típusok: `feat`, `fix`, `docs`, `chore`,
  `refactor`, `test`.
- Kis, egy célt szolgáló commitok; a commit előtt `make check` kötelező.
- A commit-üzenet nyelve angol, a törzsben (ha van) magyar is lehet.

## 9. Definition of Done (minden változtatásra)

- [ ] `make check` zöld (ruff, compileall, verify_master_data, pytest, check_structure)
- [ ] ha adatfájl változott: `SHA256SUMS.txt` frissítve (`--gen-sums`) és verify zöld
- [ ] az érintett dokumentáció frissítve (README / ADATKONYV / CHANGELOG)
- [ ] a commit Conventional Commits szerint készül

## 10. Új vizsgálati terület felvétele (checklist)

1. Nyers adat behelyezése: `data/raw/<terulet>_ingatlan_adatbazis.xlsx` (vagy CSV).
2. Oszlopleképezés előállítása: `scripts/preprocess_new_data.py` →
   `data/mappings/<terulet>_mapping.yaml`.
3. Számított master generálása → `data/processed/<terulet>_szamitott_master.parquet`
   (+ pontos geojson).
4. `data/areas.yaml` bejegyzés: `id`, `role`, `currency`, `spatial`, `metadata`.
5. `python verify_master_data.py --gen-sums` + `python verify_master_data.py`.
6. `python generate_area_report.py --area <terulet>`.
7. `make check` + commit a fenti konvenciók szerint.

## 11. A szabályok betartatása

- **Lokálisan:** `make check`; egyszer: `pip install -r requirements-dev.txt` és
  `pre-commit install`.
- **CI:** `.github/workflows/ci.yml` minden push/PR-nál futtatja: ruff,
  `compileall`, `verify_master_data.py`, `pytest`, `check_structure.py`.
- **A gépi tükör:** a `check_structure.py` a fenti strukturális szabályok
  végrehajtható formája. Ha szabályt változtatsz ebben a fájlban, a
  `check_structure.py`-t is frissíteni kell (és fordítva).
