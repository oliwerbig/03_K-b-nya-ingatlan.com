# AGENTS.md — utasítások AI-asszisztenseknek

Ez a repó az IFK-TDK 2026 vasúti-ingatlanpiaci kutatása. Mielőtt bármit módosítasz,
olvasd el a [`README.md`](README.md)-t és a [`CONTRIBUTING.md`](CONTRIBUTING.md)-t —
minden ottani szabály rád is kötelező.

## Alapelv: a notebookok a gerinc

- **Minden számítás és módszertani dokumentáció a `notebooks/00–16.ipynb`-ben él.**
- A riportok a notebookok futtatott exportjai (`python -m ingatlan_tdk report`),
  nincs külön elemző motor — párhuzamos kódot TILOS létrehozni.

## Tilos

- a `data/processed/` bármely fájlját **kézzel szerkeszteni** (csak generálással);
- a `data/raw/` tartalmát módosítani;
- új szkriptet a **gyökérbe** tenni (csak `scripts/`);
- a notebookok számozását tartalmi indok nélkül átállítani;
- a `data/schema.yaml` és `data/areas.yaml` formátumát kódmódosítás nélkül átírni;
- véletlent használó számítást seed nélkül hagyni.

## Kötelező minden változtatás után

1. `python -m compileall <érintett fájlok>`
2. `python -m ingatlan_tdk verify` (adatazonosító-változásnál előtte `--gen-sums`)
3. `pytest tests/` (vagy `python tests/test_integrity.py`)
4. mind zöld legyen, mielőtt commitolsz.

## Commitok és futtatás

- Commit-üzenet **angolul**, Conventional Commits (`feat:`, `fix:`, `docs:`, `chore:`…).
- Telepítés: `pip install -e .`; riport: `python -m ingatlan_tdk report --area X|--all`.
- Ha adatfájl változik: frissítsd a `SHA256SUMS.txt`-et és a `CHANGELOG.md`-t is.

## Nyelv

- A felhasználónak szóló magyarázat, dokumentáció és kérdés **magyarul**.
- Commit-üzenetek és új, nem-domain kötött kód **angolul**.
- A meglévő magyar domain-nevek (`load_szamitott_master`, `tavolsag_vasut_m`)
  részei az adatsémának — tilos őket átnevezni.