# IFK-TDK 2026 — kényelmi parancsok (GNU make; Windows-on Git Bash-ból).
# Telepítés előfeltétele: pip install -e . (a konzolparancsok és a csomag elérhetősége).
PY := python

.PHONY: check lint format verify test structure report build clean

## A teljes ellenőrző lánc (commit előtt kötelező)
check: lint verify test structure
	@echo "[OK] make check sikeres."

## Lint: ruff + szintaxisellenőrzés
lint:
	$(PY) -m compileall -q src scripts tests
	$(PY) -m ruff check src scripts tests

## Automatikus formázás/javítás
format:
	$(PY) -m ruff check --fix src scripts tests
	$(PY) -m ruff format src scripts tests

## Adatintegritás (hash + szerkezeti invariánsok)
verify:
	$(PY) -m ingatlan_tdk verify

## Tesztek
test:
	$(PY) -m pytest tests/ -q

## Repo-struktúra és konvenciók
structure:
	$(PY) -m ingatlan_tdk check

## Teljes riportgenerálás (kobanya + wien)
report:
	$(PY) -m ingatlan_tdk report --all

## Teljes csővezeték (verify -> report -> verify)
build:
	$(PY) -m ingatlan_tdk build

## Takarítás: __pycache__ és Google Drive desktop.ini-k
clean:
	@powershell -NoProfile -Command "Get-ChildItem -Recurse -Force -Directory -Filter __pycache__ | Where-Object { $$_.FullName -notmatch '\.venv' } | Remove-Item -Recurse -Force; Get-ChildItem -Recurse -Force -Filter desktop.ini | Where-Object { $$_.FullName -notmatch '\.venv' } | Remove-Item -Force"
