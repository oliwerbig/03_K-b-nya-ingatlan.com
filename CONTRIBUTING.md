# Hozzájárulási és projektkonvenciós szabályzat

> Ez a fájl a projekt „alkotmánya": itt van rögzítve minden strukturális, elnevezési
> és munkafolyamat-szabály. Minden változtatásnak meg kell felelnie ezeknek; a
> géppel ellenőrizhető részét az `ingatlan_tdk.checks`, a `make check` és a CI
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
├── LICENSE                 # MIT licenc (a kódra)
├── src/ingatlan_tdk/       # az EGYETLEN kódcsomag (telepítés: pip install -e .)
│   ├── _utils.py           # adatbetöltés, formázás, térbeli konfiguráció
│   ├── data_io.py          # séma-validáló betöltő könyvtár
│   ├── verify.py, checks.py, cli.py, notebook_docs.py
│   └── report_engine/      # az elemző motor (full_analyzer, full_narrative, full_html_builder)
├── notebooks/              # interaktív elemző réteg: 00–16.ipynb (from ingatlan_tdk._utils import *)
├── scripts/                # adatbeszerző/eszköz szkriptek (fetch_*, enrich_*, preprocess_*)
├── tests/                  # pytest tesztek (tests/test_*.py)
├── docs/                   # ADATKONYV + decisions/ (ADR-ek)
├── data/
│   ├── raw/                # 1. réteg: kapart, ÉRINTETLEN adat
│   ├── processed/          # 2. réteg: generált, számított adat (tilos kézzel szerkeszteni)
│   ├── schema.yaml         # kanonikus adatséma
│   ├── areas.yaml          # területi regiszter (kobanya, wien_nordbahnhof, ...)
│   └── mappings/           # nyers → kanonikus oszlopleképezések (YAML)
├── html_reports/           # az EGYETLEN generált kimenet (publikációs portál)
└── .github/workflows/      # deploy-pages.yml + ci.yml
```

## 3. Adatréteg-szabályok (legfontosabb)

1. **Két réteg, szigorúan elválasztva:**
   - `data/raw/` — a kapart/alap adatok, **immutábilisak** (sose módosítjuk).
   - `data/processed/` — minden generált/számított állomány. **TILOS kézzel
     szerkeszteni** — kizárólag a generáló szkriptek (`scripts/`) írhatják.
2. **Kanonikus séma:** `data/schema.yaml` rögzíti a mezőket, típusokat és a
   kutatási sávokat (immissziós + izokrón). Minden betöltés a
   `ingatlan_tdk.data_io.load_and_validate()`-on át menjen.
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

1. Minden notebook az `ingatlan_tdk._utils`-ból importál (`from ingatlan_tdk._utils import *`); adatbetöltés
   `load_szamitott_master()` **argumentum nélkül** (az `areas.yaml` `active_area`-ját
   használja).
2. A 00–15 fejezetek a `report_engine/full_analyzer.py` moduljaival 1:1 szinkronban
   vannak: ha egy notebook számítása változik, a motorba is be kell vezetni.
3. A notebookok a kiadott riportokhoz vezető út dokumentációi; a kanonikus,
   publikált kimenet a `html_reports/` (a `report_engine` generálja).
4. Checkpoint-mappák (`.ipynb_checkpoints`) és `__pycache__` **nem kerülhetnek
   a repóba** (a `.gitignore` és az `ingatlan_tdk.checks` is védi).
5. A Google Drive által folyamatosan újraírt `desktop.ini`/`.DS_Store` fájlokat a
   `.gitignore` zárja ki a repóból; a struktúraellenőrzés nem jelzi őket
   (takarításuk: `make clean`).

## 7. Belépési pontok

| Parancs | Szerep |
|---|---|
| `python -m ingatlan_tdk build` (`tdk-build`) | **Az egyetlen hivatalos** teljes csővezeték: verify → riport → verify |
| `python -m ingatlan_tdk report --all` (`tdk-report`) | Elemző motor + HTML riportok (kobanya + wien) |
| `python -m ingatlan_tdk verify` (`tdk-verify`) | Hash- és szerkezeti integritás |
| `python -m ingatlan_tdk check` (`tdk-check`) | Repo-struktúra és konvenciók ellenőrzése |
| `make check` | Minden fenti egyben (ruff, compileall, verify, pytest, struktúra) |

A gyökérben nincsenek szkriptek: minden kód a `src/ingatlan_tdk/` csomagban él.
Elavult állományok a git historyban érhetők el.

## 8. Commit-konvenció (Conventional Commits)

- Formátum: `<type>: <rövid leírás>` — típusok: `feat`, `fix`, `docs`, `chore`,
  `refactor`, `test`.
- Kis, egy célt szolgáló commitok; a commit előtt `make check` kötelező.
- A commit-üzenet nyelve angol, a törzsben (ha van) magyar is lehet.

## 9. Definition of Done (minden változtatásra)

- [ ] `make check` zöld (ruff, compileall, verify, pytest, struktúra)
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
5. `python -m ingatlan_tdk verify --gen-sums` + `python -m ingatlan_tdk verify`.
6. `python -m ingatlan_tdk report --area <terulet>`.
7. `make check` + commit a fenti konvenciók szerint.

## 11. A szabályok betartatása

- **Lokálisan:** `make check`; egyszer: `pip install -r requirements-dev.txt` és
  `pre-commit install`.
- **CI:** `.github/workflows/ci.yml` minden push/PR-nál futtatja: ruff,
  `compileall`, `ingatlan_tdk verify`, `pytest`, `ingatlan_tdk check`.
- **A gépi tükör:** az `ingatlan_tdk.checks` a fenti strukturális szabályok
  végrehajtható formája. Ha szabályt változtatsz ebben a fájlban, a
  `src/ingatlan_tdk/checks.py`-t is frissíteni kell (és fordítva).
