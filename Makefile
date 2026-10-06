# IFK-TDK 2026 — kényelmi parancsok (GNU make; Windows-on Git Bash-ból).
# Ha a make nem érhető el, a célok egyenként is futtathatók pythonnal.
PY := python

.PHONY: check lint format verify test structure report clean

## A teljes ellenőrző lánc (commit előtt kötelező)
check: lint verify test structure
	@echo "[OK] make check sikeres."

## Lint: ruff + szintaxisellenőrzés
lint:
	$(PY) -m compileall -q build_all.py generate_area_report.py verify_master_data.py check_structure.py data_ingestion.py report_engine scripts notebooks/_utils.py tests
	$(PY) -m ruff check build_all.py generate_area_report.py verify_master_data.py check_structure.py data_ingestion.py report_engine scripts notebooks/_utils.py tests

## Automatikus formázás/javítás
format:
	$(PY) -m ruff check --fix build_all.py generate_area_report.py verify_master_data.py check_structure.py data_ingestion.py report_engine scripts notebooks/_utils.py tests
	$(PY) -m ruff format build_all.py generate_area_report.py verify_master_data.py check_structure.py data_ingestion.py report_engine scripts notebooks/_utils.py tests

## Adatintegritás (hash + szerkezeti invariánsok)
verify:
	$(PY) verify_master_data.py

## Tesztek
test:
	$(PY) tests/test_integrity.py

## Repo-struktúra és konvenciók
structure:
	$(PY) check_structure.py

## Teljes riportgenerálás (kobanya + wien)
report:
	$(PY) generate_area_report.py --all

## __pycache__ takarítás
clean:
	@powershell -NoProfile -Command "Get-ChildItem -Recurse -Force -Directory -Filter __pycache__ | Where-Object { $$_.FullName -notmatch '\.venv' } | Remove-Item -Recurse -Force"
