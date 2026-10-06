# 0001 — Kétrétegű adatstruktúra és hash-hitelesített frozen baseline

- Státusz: Elfogadva
- Dátum: 2026-10-06

## Kontextus
Az ingatlan.com kaparásból származó nyers adatokat és az abból számított
(térbeli, hedonikus) mezőket szigorúan el kell választani, hogy a kutatás
reprodukálható és ellenőrizhető legyen a TDK-bírálók számára.

## Döntés
- Két réteg: `data/raw/` (immutábilis kapart adat) és `data/processed/`
  (generált; kézzel tilos szerkeszteni).
- A mester fájlok SHA-256 hash-e a `SHA256SUMS.txt`-ben, a
  `verify_master_data.py` (ma `ingatlan_tdk.verify`) ellenőrzi a hash-eket és
  a szerkezeti invariánsokat.
- Kanonikus séma: `data/schema.yaml`.

## Következmények
- Minden adatváltozás ellenőrzött és naplózható; a „frozen baseline" állítás
  géppel igazolható.