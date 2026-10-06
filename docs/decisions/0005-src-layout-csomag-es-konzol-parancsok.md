# 0005 — src-layout Python-csomag és konzolparancsok

- Státusz: Elfogadva
- Dátum: 2026-10-06

## Kontextus
A lapos struktúrában a modulok `sys.path`-bootstrapolással érték el egymást,
ami törékeny volt, és a gyökér megtelt belépési szkriptekkel.

## Döntés
- Minden kód a `src/ingatlan_tdk/` csomagba kerül; telepítés: `pip install -e .`.
- Konzolparancsok: `tdk-build`, `tdk-report`, `tdk-verify`, `tdk-check`
  (ill. `python -m ingatlan_tdk <parancs>`).
- A gyökérből minden belépési szkript törölve; a notebookok
  `from ingatlan_tdk._utils import *` módon importálnak.

## Következmények
- Tiszta, telepíthető csomag; a path-bootstrap hackek és az E402 kivételek
  megszűntek.