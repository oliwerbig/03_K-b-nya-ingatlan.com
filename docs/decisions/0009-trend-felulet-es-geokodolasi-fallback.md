# 0009 — Trend-felület a kanonikus specifikációban; geokódolási fallback-lánc

Dátum: 2026-10-09 | Státusz: elfogadva

## Kontextus
A friss, cím-alapú geokódolásra átállt adatokon a városrész-fixed effectek
gyakorlatilag inertek lettek (a kinyerhető városrész-mező konstans/közel konstans),
nagyobb területnél pedig dummy-explóziót okoznának. A felülvizsgálat ezt a
skálázhatósági aggályt megalapozottnak találta.

## Döntések
1. **A kanonikus hedonikus specifikáció lokációkontrollja a térbeli trend-felület**
   (`x, y, x², y², xy` vetített koordinátákon, km-ben) — dummymentes, tetszőleges
   területméretre azonos struktúra. A városrész-FE **alternatív robusztusság-
   specifikációként** fut (ha van varianciája), a két modell együtt jelenik meg a 03-ban.
2. **Geokódolási fallback-lánc**: Nominatim (kérdés-variánsokkal, limit=5) → Photon
   (kulcs nélküli) → Overpass címadat (`addr:housenumber` + `addr:interpolation`) →
   **legközelebbi házszám interpoláció** (a cél-házszám hiányában a számszerűen
   legközelebbi felvett házszám VALÓS épületpontja). A pontossági osztályok:
   `hazszam`, `hazszam_interpolalt`, `utca`, `korzet`, `nincs`.
3. **`minta_garantalt_pontos = 1`** a `hazszam` ÉS a `hazszam_interpolalt` osztályokra;
   a közelítés hatását a `geokodolas_erzekenyseg` elemzés ellenőrzi (csak-exakt vs.
   interpoláltat-is-tartalmazó minta). A sikertelen (átmeneti hibás) találatok NEM
   cache-elődnek.
4. **Hálózati/POI-számítás minden geokódolt sorra** (nem csak a pontos almintára),
   snapping-sugár 300 m-re növelve.
5. **ML-jellemzőkészlet**: egy hatás = egy változó (a folytonos hálózati távolságok
   szerepelnek, a belőlük képzett 15p dummyk nem).
6. A városrész a Nominatim `suburb`/`city_district`/`borough` mezőjéből származik.

## Következmények
- A 03. fejezet fő specifikáció-táblái a trend-felület modelljét mutatják, a városrész-FE
  táblája alternatívaként jelenik meg; minden eredmény mellett feltüntetve az N.
- A pontos minta a fallback-lánccal bővült (interpolált házszámokkal), ezt a leíró
  statisztikák és a geokódolási riport is mutatja.