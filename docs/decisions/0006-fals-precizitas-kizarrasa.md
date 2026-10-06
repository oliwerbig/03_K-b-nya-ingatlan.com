# 0006 — A fals precizitás kizárásának elve

- Státusz: Elfogadva
- Dátum: 2026-09-26

## Kontextus
Az ingatlanhirdetések ~77%-a nem tartalmaz házszámot; az utcanév-középpontból
számolt méter-pontos távolságok módszertani hibát jelentenének.

## Döntés
- Koordináta és hálózati távolság kizárólag a garantáltan pontos mintán
  (N=296) kerül kiszámításra; minden más rekord térbeli mezője NULL
  (`minta_garantalt_pontos = 0`).
- Hálózati (OSM/Dijkstra) távolságok és sétaizokrónok (1,25 m/s) a légvonal
  helyett; kerülőfaktor-kontroll.

## Következmények
- A térbeli állítások csak a pontos almintán érvényesek; az adatkonyv ezt
  szigorú szűrőflaggel garantálja.