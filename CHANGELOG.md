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

### Javítva
- `report_engine/full_narrative.py` — 5 fejezetépítő hiányzó mértékegység-definíciója
  javítva (nb02, nb04, nb06, nb12, nb14; ezek `NameError`-rel elszálltak volna friss
  riportgenerálásnál).
- `scripts/preprocess_new_data.py` — a `mapped_df` hivatkozás helyreállítva a
  `run_pipeline`-ben (a lint-ellenőrzés tárta fel).
- Lint: ruff bevezetése (`E4/E7/E9/F`), a kódbázis 62 szabálysértésről 0-ra hozva;
  az `E402` a szándékos útvonal-bootstrap mintánál engedélyezve (dokumentálva).

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

### Javítva
- **GitHub Actions hiba:** `requirements.txt` — a `pywinpty` Windows-only csomag
  platform-markerrel (`sys_platform == "win32"`), így a Linux CI telepítés már nem száll el.

### Eltávolítva
- `archive/` teljes törlése (a git history megőrzi); felesleges, hivatkozatlan
  fájlok: `kobanya_ingatlan_piac_teljes_1320db.xlsx`, `fresh_deep_analysis_metrics.json`,
  `belvaros_network_cache.json`, `kobanya_test_mapping.yaml`.

## [2026-10-06] — Többterületes motor és bécsi benchmark

### Hozzáadva
- `report_engine/` — teljes elemző motor (FullAreaAnalyzer, FullNarrativeGenerator, FullHTMLReportBuilder).
- `generate_area_report.py`, `build_all.py`, `data_ingestion.py`.
- `data/areas.yaml`, `data/schema.yaml`, `data/mappings/`.
- Bécs Nordbahnhof adatok (1 037 hirdetés), `scripts/` beszerző/eszköz szkriptek.
- `verify_master_data.py`, `SHA256SUMS.txt` (14 mester fájl), `tests/test_integrity.py`.
- `html_reports/` többterületes portál, `notebooks/16_komparativ_harom_terulet_elemzes.ipynb`.

### Javítva
- `notebooks/_utils.py` — `area=None` alapértelmezések (a notebookok újra futtathatók).
- `requirements.txt` — `spreg`, `mgwr`, `markdown` pótlása (SAR/SEM és GWR reprodukálható).
- `load_pontos_geojson` fájlnevek a tényleges geojsonokhoz igazítva.
- GitHub Actions: a Pages a `html_reports/`-ból épül és deployol.

### Ismert anomália
- 1 rekord vasúti izokrón-inkonzisztenciája (`listing_id 35461173`) — rögzített
  kivételként dokumentálva a `verify_master_data.py`-ban és az ADATKONYV-ban.
