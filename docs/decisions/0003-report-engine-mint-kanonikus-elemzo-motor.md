# 0003 — A report_engine mint kanonikus elemző motor

- Státusz: Elfogadva
- Dátum: 2026-10-06

## Kontextus
Három párhuzamos generáció élt a repóban (kódgenerátor, notebook-csővezeték,
riportmotor), egymásnak ellentmondó kimenetekkel.

## Döntés
- Az `ingatlan_tdk.report_engine` (FullAreaAnalyzer, FullNarrativeGenerator,
  FullHTMLReportBuilder) a számítások és a publikált riportok EGYETLEN forrása.
- A notebookok (00–15) a motor fejezeteivel 1:1 szinkronban maradnak
  (interaktív réteg); a `html_reports/` az egyetlen generált kimenet.
- A korábbi generátorok és futtatók törlésre kerültek (a git history megőrzi).

## Következmények
- Egyetlen, reprodukálható publikációs út; a notebookok és a riportok nem
  térhetnek el egymástól.