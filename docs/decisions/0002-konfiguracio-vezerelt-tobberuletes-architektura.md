# 0002 — Konfiguráció-vezérelt, többterületes architektúra

- Státusz: Elfogadva
- Dátum: 2026-10-06

## Kontextus
A kutatás Kőbánya mellett nemzetközi benchmarkot (Bécs Nordbahnhof) és további
kontrollterületeket vizsgál. A területek felvétele nem igényelhet egyedi kódot.

## Döntés
- `data/areas.yaml` regisztrál minden területet (adatútvonalak, valuta, térbeli
  középpont, metaadatok).
- Az elemző motor és a riportgenerátor kizárólag ebből a regiszterből dolgozik.
- Új terület = adatfájlok + `areas.yaml` bejegyzés + `data/mappings/` leképezés.

## Következmények
- Egy terület felvétele kód nélkül, checklist alapján lehetséges; a kód
  terület-független marad.