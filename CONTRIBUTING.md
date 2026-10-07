# Hozzájárulási és projektkonvenciós szabályzat

> A projekt „alkotmánya": strukturális, elnevezési és munkafolyamat-szabályok.
> A gépi betartatást a CI végzi (`.github/workflows/ci.yml`: verify + pytest).

## 1. Projektcél (röviden)

**Notebook-alapú, kanonizált riportpipeline.** A `notebooks/01–06.ipynb` notebookok
tartalmazzák az ÖSSZES számítást és a módszertani dokumentációt, **területfüggetlenül**
(bármely regisztrált adathalmazra futtathatók). A `tdk-report` parancs a kiválasztott
területre lefuttatja a notebookokat, és „baked" HTML-riportokat exportál — ezek a
GitHub Pages-en jelennek meg, és az AI-szövegelemzés (tézisek, következtetések) bemenetei.
Részletek: [`README.md`](README.md), döntések: [`docs/decisions/`](docs/decisions/).

## 2. Kanonikus mappatérkép

```
gyökér/
├── README.md, CONTRIBUTING.md, AGENTS.md, CHANGELOG.md   # dokumentáció
├── LICENSE, pyproject.toml                               # licenc + csomagdefiníció
├── requirements.txt, requirements-dev.txt                # függőségek (futtatás / fejlesztés)
├── SHA256SUMS.txt                                        # frozen baseline hash-manifest
├── src/ingatlan_tdk/                                     # az EGYETLEN kódcsomag (pip install -e .)
│   ├── _utils.py          # adatbetöltés, formázás, területi konfiguráció
│   ├── data_io.py         # séma-validáló betöltő (új adathalmazokhoz)
│   ├── verify.py          # adatintegritás (hash + invariánsok)
│   └── cli.py             # tdk-report / tdk-verify parancsok
├── notebooks/              # 01–06.ipynb — 6 narratív fejezet (számítások: src/ingatlan_tdk/analyses.py)
├── scripts/                # adatbeszerző/eszköz szkriptek (fetch_*, enrich_*, preprocess_*)
├── tests/                  # pytest tesztek
├── docs/                   # ADATKONYV + decisions/ (ADR-ek)
├── data/
│   ├── raw/                # 1. réteg: kapart, ÉRINTETLEN adat
│   ├── processed/          # 2. réteg: generált (tilos kézzel szerkeszteni)
│   ├── schema.yaml         # kanonikus adatséma
│   ├── areas.yaml          # területi regiszter
│   └── mappings/           # nyers → kanonikus oszlopleképezések
├── html_reports/           # generált kimenet (NEM része a gitnek; a CI állítja elő)
└── .github/workflows/      # ci.yml (verify + pytest) + deploy-pages.yml
```

## 3. Adatréteg-szabályok (legfontosabb)

1. **Két réteg:** `data/raw/` immutábilis kapart adat; `data/processed/` generált —
   **tilos kézzel szerkeszteni**, csak a `scripts/` generálhatja.
2. **Kanonikus séma:** `data/schema.yaml`; minden betöltés az
   `ingatlan_tdk.data_io.load_and_validate()`-on át.
3. **Területi regiszter:** `data/areas.yaml` — új terület = adatfájlok + bejegyzés +
   `data/mappings/` leképezés, **kódmódosítás nélkül**.
4. **Frozen baseline:** adatváltozás után kötelező:
   `python -m ingatlan_tdk verify --gen-sums`, majd `python -m ingatlan_tdk verify`.

## 4. Elnevezési konvenciók

- Fájlok/mappák: `snake_case`; kivételek a rögzített konvenciónevek (README.md, LICENSE, …).
- Notebookok: `NN_tema_nev.ipynb` (NN kétszámjegyű, 01–06). A számozás a fejezetek
  logikai sorrendje — átszámozás tilos tartalmi indok nélkül.
- Scriptek: igei prefix (`fetch_`, `enrich_`, `preprocess_`).
- Oszlopnevek: a `data/schema.yaml`-ban rögzítettek; boolean dummy-k `is_*`/`has_*`.
- Tesztek: `tests/test_*.py`, függvénynevek `test_*`.

## 5. Nyelvi politika

- **Magyar:** dokumentáció, notebook-szövegek, magyarázatok.
- **Angol:** commit-üzenetek (Conventional Commits).
- **Kód:** a meglévő magyar domain-nevek (`load_szamitott_master`, `tavolsag_vasut_m`)
  az adatséma részei — tilos átnevezni; új, nem-domain kötött kód angolul.

## 6. Notebook-szabályok (a gerinc)

1. A notebookok az `ingatlan_tdk._utils`-ból importálnak
   (`from ingatlan_tdk._utils import *`); az adatbetöltés `load_szamitott_master()`
   argumentum nélkül — a területet a `TDK_ACTIVE_AREA` környezeti változó (vagy az
   `areas.yaml` `active_area`) határozza meg.
2. **Minden számítás az `ingatlan_tdk.analyses` modulban él, pontosan egyszer** (a notebookok a `cached_compute` cache-elt eredményeit jelenítik meg — párhuzamos modelkód tilos). Új módszertan = új függvény az analyses.py-ban + új/bővített
   notebook-fejezet (markdown + kód együtt), nincs külön „motor".
3. A véletlent használó számításoknak **determinisztikusnak** kell lenniük
   (`random_state`/seed rögzítve), hogy a riportok reprodukálhatók legyenek.
4. Checkpoint-mappák (`.ipynb_checkpoints`) és `__pycache__` nem kerülhetnek a repóba
   (a `.gitignore` védi).

## 7. Belépési pontok

| Parancs | Szerep |
|---|---|
| `python -m ingatlan_tdk report --area X` / `--all` (`tdk-report`) | Notebookok futtatása + „baked" HTML-riportok + index |
| `python -m ingatlan_tdk verify` (`tdk-verify`) | Hash- és szerkezeti adatintegritás |
| `pytest tests/` | Adat- és séma-tesztek |

Telepítés: `pip install -e .` (a `requirements.txt` után).

## 8. Commit-konvenció (Conventional Commits)

- Formátum: `<type>: <rövid leírás>` — `feat`, `fix`, `docs`, `chore`, `refactor`, `test`.
- Kis, egy célú commitok; angol üzenet.

## 9. Definition of Done (minden változtatásra)

- [ ] `python -m ingatlan_tdk verify` zöld
- [ ] `pytest tests/` zöld
- [ ] adatváltozásnál: `--gen-sums` + verify + CHANGELOG
- [ ] az érintett dokumentáció frissítve (README / ADATKONYV / CHANGELOG)
- [ ] commit Conventional Commits szerint

## 10. Új vizsgálati terület felvétele (checklist)

1. Nyers adat: `data/raw/<terulet>_ingatlan_adatbazis.xlsx` (vagy CSV).
2. Oszlopleképezés: `scripts/preprocess_new_data.py` → `data/mappings/<terulet>_mapping.yaml`.
3. Számított master generálása → `data/processed/<terulet>_szamitott_master.parquet`.
4. `data/areas.yaml` bejegyzés (id, role, currency, spatial, metadata).
5. `python -m ingatlan_tdk verify --gen-sums` + `verify`.
6. `python -m ingatlan_tdk report --area <terulet>`.
7. `pytest tests/` + commit.

## 11. A szabályok betartatása

- **CI:** `.github/workflows/ci.yml` minden push/PR-nál: verify + pytest.
- **Pages:** `.github/workflows/deploy-pages.yml`: verify → `tdk-report --all` → deploy.
- A `html_reports/` kimenet nincs a gitben — a CI generálja.