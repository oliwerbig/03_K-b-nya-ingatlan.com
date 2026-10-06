# 0004 — Kanonikus projektstruktúra és gépi betartatás

- Státusz: Elfogadva
- Dátum: 2026-10-06

## Kontextus
A szabályok csak akkor tartanak, ha géppel ellenőrizhetők; a markdown szabályzat
önmagában nem kényszerít.

## Döntés
- A `CONTRIBUTING.md` a szabályzat egyetlen forrása; az `AGENTS.md` az
  AI-asszisztenseknek szól.
- Gépi tükör: `ingatlan_tdk.checks` (gyökér-fehérlista, elnevezések, tiltott
  fájlok, manifest-konzisztencia), ruff (`pyproject.toml`), `.editorconfig`,
  `Makefile`, pre-commit hookok, CI (`.github/workflows/ci.yml`).
- A `make check` (ruff + compileall + verify + pytest + struktúra) zöld nélkül
  nincs commit.

## Következmények
- Minden szabályváltozásnál a gépi tükröt is frissíteni kell; a CI minden
  push-nál ellenőriz.