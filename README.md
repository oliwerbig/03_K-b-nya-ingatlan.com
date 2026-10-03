# Kőbánya Ingatlanpiaci Elemzés 2026 - TDK Kutatás

Ez a repozitórium egy átfogó, 16 modulból álló adatalapú ingatlanpiaci és térökonometriai kutatást tartalmaz Budapest X. kerületéről (Kőbánya). A kutatás célja, hogy feltárja az árazási dinamikákat, a térbeli heterogenitást, a környezeti externáliák (pl. vasút, szolgáltatások) hatását, és predikciós modellek segítségével azonosítsa a lakáspiaci arbitrázslehetőségeket és befektetési kockázatokat.

## A Kutatás Logikai Felépítése (Storyline)

A projekt nem 16 különálló elemzés, hanem egy egymásra épülő, szorosan integrált **modell-evolúciós narratíva**. A célunk az volt, hogy a klasszikus "tankönyvi" modellektől indulva, az abban rejlő hibákat feltárva jussunk el a legmodernebb térökonometriai és gépi tanulási predikciókig.

### I. Adatfeltárás és Alapozás
1. **[00. Adathalmaz áttekintése](docs/00_adathalmaz_attekintes.html):** Megismerkedünk az adatokkal, és elvégezzük a kritikus adattisztításokat, fókuszálva a geokódolás pontosságára.
2. **[01. Leíró statisztika és EDA](docs/01_leiro_statisztika_es_eda.html):** Feltárjuk az árak és alapterületek alapvető eloszlásait (átlagárak, szórások, outlierek).
3. **[02. Árstruktúra és szegmentáció](docs/02_arstruktura_es_szegmentacio.html):** Izoláljuk a legfőbb kategóriákat, például kiszámítjuk a tényleges paneldiszkont mértékét Kőbányán (13.5%).
4. **[03. Térbeli Elemzés és Térképek](docs/03_terbeli_elemzes_es_terkepek.html):** Vizualizáljuk az árrobbanási gócokat és a sűrűségi hotspotokat hőtérképeken.

### II. Városszerkezet és Környezeti Externáliák
*Mielőtt árazási modelleket építenénk, számszerűsíteni kell azokat a térbeli adottságokat, amik Kőbánya specifikumai.*
5. **[04. Vasúti diszkont és Izokrónok](docs/04_vasuti_diszkont_es_izokronok.html):** Kőbányát átszeli a vasút. Bebizonyítjuk és számszerűsítjük a zaj és az elvágó hatás okozta negatív externáliát (-15.5% értékvesztés).
6. **[05. POI hálózat és 15-perces város](docs/05_poi_es_15_perces_varos.html):** A pozitív externáliák vizsgálata: kiszámítjuk minden egyes lakásra a gyalogos sétatávon belüli szolgáltatások (POI-k) sűrűségét.
7. **[06. Klaszter és Tipológia](docs/06_klaszter_es_tipologia.html):** Unsupervised (nem felügyelt) gépi tanulással, a fenti környezeti paramétereket is felhasználva szegmentáljuk a lakáspiacot rejtett típusokra.

### III. Az Árazási Modellek Evolúciója
*Elérkeztünk a kutatás gerincéhez: a "mitől ennyi az ár?" és a "mennyi lesz az ár?" kérdések tudományos megválaszolásához.*
8. **[07. Hedonikus Ármodell (OLS)](docs/07_hedonikus_armodell.html):** Felállítjuk a klasszikus alapmodellt, ami lineárisan próbálja magyarázni az árakat a paraméterekből.
9. **[08. Térbeli Autokorreláció (Moran's I)](docs/08_moran_es_autokorrelacio.html):** *Kritika:* Az OLS feltételezi a lakások függetlenségét. A Moran-teszttel bebizonyítjuk, hogy ez hamis, a szomszédok árai erősen korrelálnak.
10. **[09. Térökonometria (SAR és SEM)](docs/09_terokonometria_sar_sem.html):** *Javítás 1:* A globális térbeli modellekkel egy szomszédsági súlymátrix (Spatial Weights) bevezetésével korrigáljuk az OLS hibáját.
11. **[10. Lokális Térökonometria (GWR)](docs/10_lokalis_terokonometria_gwr.html):** *Javítás 2:* A SAR csak globálisan korrigál. A GWR megmutatja a **lokális térbeli heterogenitást**: bebizonyítjuk, hogy pl. a metró közelsége máshogy hat Újhegyen, mint a Gyárdűlőn.
12. **[11. Gépi Tanulás és Arbitrázs](docs/11_gepi_tanulas_es_arbitrazs.html):** *Paradigmaváltás:* Ha nem a magyarázat (ok-okozat), hanem a kőkemény predikció a cél, akkor az XGBoost algoritmust vetjük be. Mivel ez a legpontosabb, ezzel keressük meg a piacon jelenleg alulárazott (felújítandó/arbitrázs) lakásokat.

### IV. Beruházási Dinamika és Kockázat
*Mit jelentenek a fenti eredmények a befektetőknek és a várospolitikának?*
13. **[12. Bérleti Piac és Rent Gap](docs/12_berleti_piac_es_rent_gap.html):** Kiszámítjuk a bérleti hozamokat (Yield) és a megtérülési rátákat (Price-to-Rent), valamint vizualizáljuk a felújítási potenciált (Rent Gap).
14. **[13. Monte Carlo Kockázatelemzés](docs/13_monte_carlo_kockazat.html):** Sztochasztikus modellezéssel mutatjuk be, mekkora a veszteség valószínűsége (VaR) egy ingatlanfejlesztési/felújítási projektben, ha az árak és hozamok véletlenszerűen ingadoznak.
15. **[14. LVC (Land Value Capture) Szimuláció](docs/14_lvc_szimulacio.html):** Egy fiktív (vagy tervezett) infrastrukturális beruházás (pl. új villamosmegálló) okozta ingatlan-értéknövekedést szimuláljuk, bemutatva a várospolitikai "érték-visszanyerés" lehetőségét.

### V. Felhasználói Alkalmazás
16. **[15. Interaktív Ingatlan Kereső Dashboard](docs/15_ingatlan_kereso_dashboard.html):** A kutatási adatbázisra épülő, bárki által használható interaktív szűrési és elemzési felület.
