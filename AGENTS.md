# AGENTS.md — utasítások AI-asszisztenseknek

Ez a repó az IFK-TDK 2026 ingatlanpiaci és térökonometriai kutatása
(Kőbánya + bécsi benchmark). Mielőtt bármit módosítasz, olvasd el a
[`README.md`](README.md)-t és a [`CONTRIBUTING.md`](CONTRIBUTING.md)-t —
minden ottani szabály rád is kötelező.

## Tilos

- a `data/processed/` bármely fájlját **kézzel szerkeszteni** (csak generálással);
- a `data/raw/` tartalmát módosítani;
- új szkriptet a **gyökérbe** tenni (csak `scripts/`, vagy legacy esetén `archive/`);
- a notebookok számozását/elnevezését a `report_engine` fejezeteivel való szinkron
  nélkül változtatni;
- a `data/schema.yaml` és `data/areas.yaml` formátumát kódmódosítás nélkül átírni.

## Kötelező minden változtatás után

1. `python -m compileall <érintett fájlok>`
2. `python -m ingatlan_tdk verify` (adatazonosító-változásnál előtte `--gen-sums`)
3. `python tests/test_integrity.py` (vagy `pytest`)
4. `python -m ingatlan_tdk check`
5. mind zöld legyen, mielőtt commitolsz.

## Commitok és futtatás

- Commit-üzenet **angolul**, Conventional Commits (`feat:`, `fix:`, `docs:`, `chore:`…).
- Telepítés: `pip install -e .`; teljes csővezeték: `python -m ingatlan_tdk build`; ellenőrzőcsomag: `make check`.
- Ha adatfájl változik: frissítsd a `SHA256SUMS.txt`-et és a `CHANGELOG.md`-t is.

## Nyelv

- A felhasználónak szóló magyarázat, dokumentáció és kérdés **magyarul**.
- Commit-üzenetek és új, nem-domain kötött kód **angolul**.
- A meglévő magyar domain-nevek (`load_szamitott_master`, `tavolsag_vasut_m`)
  részei az adatsémának — tilos őket átnevezni.
