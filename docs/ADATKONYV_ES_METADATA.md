# KŐBÁNYA (BUDAPEST X. KERÜLET) INGATLANPIACI ADATKÖNYV ÉS MÓDSZERTANI DOKUMENTÁCIÓ
**Projekt:** IFK-TDK 2026 Tudományos Diákköri Konferencia Kutatás
**Dátum:** 2026. szeptember 26.
**Adatgyűjtés időpontja:** 2026. szeptember 26. 10:00 – 12:30 (ingatlan.com teljes census)
**Adatállomány mérete:** 1 320 db egyedi hirdetés (1 140 db eladó, 180 db kiadó lakás)
**Státusz:** **VÉGLEGESÍTETT ÉS LEZÁRT MESTER ADATBÁZIS (FROZEN BASELINE)**

---

## 1. RENDSZERARCHITEKTÚRA ÉS A KÉT-RÉTEGŰ ADATSTRUKTÚRA

A kutatási reprodukálhatóság és a legmagasabb szintű tudományos adatintegritás biztosítása érdekében az adathalmaz **két független, szigorúan elválasztott rétegre** oszlik:

```
                                  [ INGATLAN.COM TELJES CENSUS ]
                                      (1 320 db HTML forrás)
                                                 │
                                                 ▼
             ┌───────────────────────────────────┴───────────────────────────────────┐
             │                                                                       │
             ▼                                                                       ▼
   ┌───────────────────────────────────┐                   ┌───────────────────────────────────┐
   │         1. RÉTEG (LAYER 1)        │                   │         2. RÉTEG (LAYER 2)        │
   │      NYERS / ALAP ADATHALMAZ      │                   │     SZÁMÍTOTT / MODELLEZÉSI       │
   │    (Tisztán kapart alapadatok)    │                   │   (Térbeli és hedonikus motor)    │
   ├───────────────────────────────────┤                   ├───────────────────────────────────┤
   │ • Kizárólag kapart attribútumok   │                   │ • Pontos geokódolás (N=296 tető)  │
   │ • 0 db koordináta, 0 db távolság  │                   │ • Fals precizitás szűrés (1024 NULL│
   │ • Érintetlen szöveges leírások    │                   │ • OSM Dijkstra gyalogos hálózat   │
   │ • Javított építési évek (szocial.)│                   │ • 5, 10, 15 perces sétaizokrónok  │
   │ • Cél: Referencia alapforrás      │                   │ • Villamos (75) és Busz (281)     │
   │                                   │                   │ • Integrált kötöttpályás index    │
   │ Fájlok:                           │                   │ • Hedonikus log-transzformációk   │
   │  - kobanya_ingatlan_nyers_master  │                   │ • Korrigált alapterület, dummyk   │
   │    (.db, .parquet, .csv, .xlsx)   │                   │ Fájlok:                           │
   │                                   │                   │  - kobanya_ingatlan_szamitott     │
   │                                   │                   │    (.db, .parquet, .csv, .xlsx,   │
   │                                   │                   │     .geojson)                     │
   └───────────────────────────────────┘                   └───────────────────────────────────┘
```

---

## 2. A MESTER ADATBÁZISOK FÁJLJEGYZÉKE ÉS SHA-256 HASH ELLENŐRZŐ ÖSSZEGEK

Minden fájl kriptográfiai SHA-256 hash ellenőrző összeggel van rögzítve, garantálva, hogy a kutatás során az adatok nem sérülnek és nem módosulnak:

| Réteg | Fájlnév | Formátum | Méret | Leírás |
|---|---|---|---|---|
| **1. Nyers** | `data/raw/kobanya_parsed_raw_corpus.json` | JSON | 5.65 MB | Tisztított JSON korpusz (alapforrás) |
| **1. Nyers** | `data/raw/kobanya_ingatlan_nyers_master.db` | SQLite3 | 7.57 MB | Relációs adatbázis FTS5 keresővel |
| **1. Nyers** | `data/raw/kobanya_elado_nyers.csv` | CSV (UTF-8-BOM)| 0.78 MB | 1 140 eladó lakás táblázata |
| **1. Nyers** | `data/raw/kobanya_kiado_nyers.csv` | CSV (UTF-8-BOM)| 0.13 MB | 180 kiadó lakás táblázata |
| **1. Nyers** | `data/raw/kobanya_ingatlan_nyers_alap_1320db.xlsx` | Excel (XLSX) | 0.44 MB | 4 munkalapos professzionális Excel |
| **2. Számított** | `data/processed/kobanya_ingatlan_szamitott_master.db` | SQLite3 | 7.95 MB | Számított SQLite adatbázis FTS5-tel |
| **2. Számított** | `data/processed/kobanya_ingatlan_szamitott_master.parquet`| Parquet | 0.29 MB | Számított oszlopos adattároló |
| **2. Számított** | `data/processed/kobanya_elado_szamitott.csv` | CSV (UTF-8-BOM)| 0.77 MB | 1 140 eladó lakás (133 változó) |
| **2. Számított** | `data/processed/kobanya_kiado_szamitott.csv` | CSV (UTF-8-BOM)| 0.13 MB | 180 kiadó lakás (140 változó) |
| **2. Számított** | `data/processed/kobanya_ingatlan_szamitott_pontos.geojson`| GeoJSON | 1.41 MB | 296 db pontos épület tetőpont (QGIS) |
| **2. Számított** | `data/processed/kobanya_elado_pontos.geojson` | GeoJSON | 1.21 MB | 254 db pontos eladó tetőpont |
| **2. Számított** | `data/processed/kobanya_kiado_pontos.geojson` | GeoJSON | 0.20 MB | 42 db pontos kiadó tetőpont |
| **2. Számított** | `data/processed/kobanya_ingatlan_szamitott_modellezes_1320db.xlsx`| Excel (XLSX)| 0.81 MB | Modellezési munkafüzet izokrón KPI-kkal |

*(A pontos hexadecimális ellenőrző kódokat a gyökérben lévő `SHA256SUMS.txt` tartalmazza, és a `verify_master_data.py` ellenőrzi.)*

---

## 3. TÉRBELI MÓDSZERTAN ÉS A FALSIFIKÁCIÓ-MENTES PRECÍZIÓ ELVE

### 3.1. A fals precizitás kizárása (No False Precision)
Az ingatlanhirdetési portálokon a hirdetések jelentős része (~77%) nem tartalmaz házszámot az eladói diszkréció miatt. A magyar ingatlanpiaci kutatások gyakori módszertani hibája, hogy az utcanév közepét vagy a kerület súlypontját rendelik hozzá koordinátaként, majd abból számolnak méterre pontos távolságokat.
Ez az adathalmaz **szigorúan kizárja a fals precizitást**:
- **Pontos minta ($N = 296$, 22.4%):** Kizárólag ott határozunk meg koordinátát és távolságot, ahol ingatlanügynökségi JSON-LD pontos koordináta ($N=292$) vagy szövegből bányászott házszámszintű OSM épület-tetőpont ($N=4$) áll rendelkezésre.
- **Tágabb minta ($N = 1 024$, 77.6%):** Minden térbeli mező (`geokodolt_lat`, `tavolsag_*`, `menetido_*`, `*_5p_seta`, `log_tavolsag_*`) szigorúan **`NULL`**. Ezek az ingatlanok a kerületi szintű panel/tégla, szobaszám, alapterület és ár-ökonometriai elemzésekhez használhatók.
- **Szűrő flag:** `minta_garantalt_pontos = 1` (azonnal leválogatja a térbeli almintát).

### 3.2. Topológiai hálózati távolság (OpenStreetMap & Dijkstra)
A légvonalbeli (euklidészi) távolság szisztematikusan alábecsüli a valós elérhetőséget, különösen Kőbányán, ahol a vasúti töltések (Ceglédi és Újszászi vonalak), ipari telephelyek és a Kőbányai Sörgyár átjárhatatlan gátakat képeznek.
- **Gyalogos hálózat:** Kőbánya és környéke teljes gyalogos úthálózata (18 650 csomópont, 20 883 él).
- **Algoritmus:** Single-source Dijkstra legrövidebb útkeresés a lakás csomópontjából a célpontokig.
- **Gyaloglási sebesség:** $v = 1.25\text{ m/s} = 4.5\text{ km/h}$ (nemzetközi közlekedéstervezési és GIS standard).
- **Menetidő képlet:**
  $$\text{menetido\_gyalog\_perc} = \frac{\text{tavolsag\_halozati\_m}}{1.25 \times 60} = \frac{\text{tavolsag\_halozati\_m}}{75}$$
- **Kerülő faktor (Detour Index):**
  $$\text{kerulo\_faktor} = \frac{\text{tavolsag\_halozati\_m}}{\text{tavolsag\_euklideszi\_m}}$$

### 3.3. Sétaizokrónok (5, 10, 15 perc) a fix méteres pufferek helyett
A kutatási terv és a bírálói elvárások szerint nem absztrakt 500m/1000m-es köröket használunk, hanem valós emberi időráfordítást tükröző izokrón dummykat:
- **`*_5p_seta`:** $\le 5.0\text{ perc}$ gyaloglás ($\le 375\text{ m}$ valós sétaút) – közvetlen kényelmi zóna.
- **`*_10p_seta`:** $\le 10.0\text{ perc}$ gyaloglás ($\le 750\text{ m}$ valós sétaút) – standard gyalogos vonzáskörzet.
- **`*_15p_seta`:** $\le 15.0\text{ perc}$ gyaloglás ($\le 1125\text{ m}$ valós sétaút) – elérhetőségi határérték.

### 3.4. Közlekedési módok és POI-k Kőbányán
1. **Villamosmegállók (75 db OSM megálló):** Az 1-es, 3-as, 28-as, 37-es és 62-es villamosok megállói. Kőbánya legfontosabb felszíni kötöttpályás gerinchálózata.
2. **Metróállomások (8 db állomás):** M3 déli szakasz (Kőbánya-Kispest, Határ út, Pöttyös utca, Ecseri út, Népliget) és M2 kelet-pesti szakasz (Örs vezér tere, Pillangó utca, Puskás Ferenc Stadion).
3. **Vasútállomások (4 db állomás):** Kőbánya alsó, Kőbánya felső, Kőbánya-Kispest, Rákos. (A belső kerületi MÁV vonalak S-Bahn jellegű gyorsvasúti kapcsolatot adnak a Nyugati és Keleti pályaudvarokhoz BKK bérlettel).
4. **Buszmegállók (281 db OSM megálló):** A kerület sűrű hálózata (95.6%-os elérhetőség 5 percen belül).
5. **Integrált Kötöttpályás Index:**
   $$\text{tavolsag\_kotottpalya\_halozati\_m} = \min(\text{metro}, \text{vasut}, \text{villamos})$$
6. **Jelentős közparkok (5 db):** Óhegy park, Népliget, Rottenbiller park, Sportliget / Újhegyi tó, Csajkovszkij park.

---

## 4. RÉSZLETES ADATSZÓTÁR (VARIABLE CODEBOOK)

> **Kánon:** a változók kanonikus neveit, típusait és a rögzített sávhatárokat
> a `data/schema.yaml` rögzíti — ez az egyetlen hivatkozás. A fókuszterületi
> (Mázsa tér) és CBD (belváros) változók kikerültek a kánonból.

### 4.1. Alapvető azonosítók és címadatok
| Változónév | Típus | Nyers | Számított | Leírás és értelmezés |
|---|---|:---:|:---:|---|
| `listing_id` | TEXT (PK) | ✓ | ✓ | Az ingatlan.com egyedi, megismételhetetlen hirdetésazonosítója |
| `url` | TEXT | ✓ | ✓ | Közvetlen webes elérési út |
| `cim_teljes` | TEXT | ✓ | ✓ | Tisztított teljes cím (pl. "Budapest X. kerület, Kőrösi Csoma Sándor út 12.") |
| `utca` | TEXT | ✓ | ✓ | Utcanév a X. kerületben |
| `hazszam_vegleges` | TEXT | ✓ | ✓ | Épület házszáma (ha elérhető, különben üres) |
| `postal_code` | TEXT | ✓ | ✓ | Négyjegyű irányítószám (1101 - 1108 Kőbánya) |
| `varosresz` | TEXT | ✓ | ✓ | Hivatalos városrész (Óhegy, Újhegy, Gyárdűlő, Kőbánya központ, Felsőrákos, Kőbánya-Kertváros) |

### 4.2. Ár és Pénzügyi mutatók
| Változónév | Típus | Nyers | Számított | Mértékegység / Képlet | Leírás |
|---|---|:---:|:---:|---|---|
| `price_huf` | INTEGER | ✓ | ✓ | HUF | Hirdetési vételár vagy havi bérleti díj |
| `ar_millio_ft` | REAL | ✓ | ✓ | Millió Ft | Vételár millió forintban (`price_huf / 1e6`) |
| `ar_ezer_ft_ho` | REAL | ✓ | ✓ | ezer Ft/hó | Bérleti díj ezer Ft/hóban (`price_huf / 1000`) |
| `nm_ar_huf` | INTEGER | ✓ | ✓ | Ft/m² | Fajlagos négyzetméterár (`price_huf / alapterulet_nm`) |
| `log_ar` | REAL | ✗ | ✓ | - | $\ln(\text{price\_huf})$ – Hedonikus árfüggvény bal oldala |
| `log_nm_ar` | REAL | ✗ | ✓ | - | $\ln(\text{nm\_ar\_huf})$ – Logaritmikus fajlagos ár |
| `kozos_koltseg_huf`| INTEGER | ✓ | ✓ | HUF/hó | Társasházi havi közös költség |
| `rezsikoltseg_huf` | INTEGER | ✓ | ✓ | HUF/hó | Havi átlagos rezsiköltség |
| `is_ar_outlier` | INTEGER (0/1)| ✗ | ✓ | dummy | 1 ha nm ár < 350 000 Ft/m² vagy > 2 500 000 Ft/m² |

### 4.3. Ingatlanfizikai és műszaki jellemzők
| Változónév | Típus | Nyers | Számított | Leírás és kategóriák |
|---|---|:---:|:---:|---|
| `ingatlan_altipus` | TEXT | ✓ | ✓ | Tégla lakás, Panel lakás, Csúsztatott zsalus, Új építésű projekt |
| `is_panel` | INTEGER (0/1)| ✗ | ✓ | 1 ha az ingatlan iparosított technológiájú panel |
| `is_tegla` | INTEGER (0/1)| ✗ | ✓ | 1 ha az ingatlan hagyományos téglafalazatú |
| `allapot` | TEXT | ✓ | ✓ | Eredeti szöveges állapot (új építésű, újszerű, felújított, jó, közepes, felújítandó) |
| `allapot_kod` | INTEGER (1-6)| ✗ | ✓ | Rendezett skála: 1=felújítandó, 2=közepes, 3=jó, 4=felújított, 5=újszerű, 6=új |
| `is_felujitando` | INTEGER (0/1)| ✗ | ✓ | 1 ha állapot kódja $\le 2$ |
| `is_ujszeru_vagy_uj`| INTEGER (0/1)| ✗ | ✓ | 1 ha állapot kódja $\ge 5$ |
| `alapterulet_nm` | REAL | ✓ | ✓ | Hivatalos nettó hasznos lakóterület ($m^2$) |
| `log_alapterulet` | REAL | ✗ | ✓ | $\ln(\text{alapterulet\_nm})$ |
| `erkely_nm` | REAL | ✓ | ✓ | Erkély mérete $m^2$-ben (NULL ha nincs) |
| `has_erkely` | INTEGER (0/1)| ✗ | ✓ | 1 ha van erkély vagy loggia (kanonikus név; korábban: `van_erkely`) |
| `korrigalt_alapterulet_nm`| REAL | ✗ | ✓ | **Hedonikus korrigált terület:** $\text{alapterület} + 0.5 \times \text{erkély}$ |
| `szobaszam_egesz` | INTEGER | ✓ | ✓ | Egész szobák száma ($\ge 12\text{ m}^2$) |
| `szobaszam_fel` | INTEGER | ✓ | ✓ | Félszobák száma ($< 12\text{ m}^2$) |
| `szobaszam_osszes` | REAL | ✓ | ✓ | Összes szobaszám: $\text{egész} + 0.5 \times \text{fél}$ |
| `atlagos_szobameret_nm`| REAL | ✗ | ✓ | $\text{alapterület} / \text{szobaszám}$ ($m^2$/helyiség) |
| `szobaszam_kategoria`| TEXT | ✗ | ✓ | '1 szoba', '1.5-2 szoba', '2.5-3 szoba', '4+ szoba' |
| `emelet` | TEXT | ✓ | ✓ | Szöveges emelet ("földszint", "3", "félemelet", "10 felett") |
| `emelet_szam` | REAL | ✓ | ✓ | Numerikus emelet (földszint=0.0) |
| `epulet_szintjei_szam`| REAL | ✓ | ✓ | Épület összes emeletszáma |
| `is_foldszint` | INTEGER (0/1)| ✗ | ✓ | 1 ha a lakás földszinti (földszinti árhátrány vizsgálatához) |
| `is_zaroszint` | INTEGER (0/1)| ✗ | ✓ | 1 ha a legfelső emeleten található (beázási kockázat) |
| `is_magas_emelet_lift_nelkul`| INTEGER (0/1)| ✗ | ✓ | 1 ha $\ge 3$. emelet és nincs lift |
| `lift` | TEXT | ✓ | ✓ | "van" / "nincs" |
| `has_lift` | INTEGER (0/1)| ✗ | ✓ | Lift dummy (1=van lift az épületben) |
| `klima` | TEXT | ✓ | ✓ | "van" / "nincs" |
| `has_klima` | INTEGER (0/1)| ✗ | ✓ | Légkondicionáló felszereltség dummy |
| `futes` | TEXT | ✓ | ✓ | Részletes hirdetési fűtéstípus |
| `futes_kategoria` | TEXT | ✗ | ✓ | Standardizált fűtéskategória (Távfűtés egyedi méréssel, Hagyományos távfűtés, Gáz-cirkó, Gázkonvektor, Hőszivattyú, Elektromos) |
| `has_tavfutes` | INTEGER (0/1)| ✗ | ✓ | Távfűtés dummy (panel és szocialista lakótelepek) |
| `has_konvektor` | INTEGER (0/1)| ✗ | ✓ | Gázkonvektor dummy (régi polgári bérházak) |
| `has_megujulo` | INTEGER (0/1)| ✗ | ✓ | Hőszivattyú / megújuló energia dummy |
| `parkolas` | TEXT | ✓ | ✓ | Eredeti szöveges parkolási leírás |
| `has_garazs_vagy_beallo`| INTEGER (0/1)| ✗ | ✓ | 1 ha saját garázs, teremgarázs-hely vagy udvari beálló jár a lakáshoz |
| `panelprogram` | TEXT | ✓ | ✓ | "részt vett", "nem vett részt" |
| `epites_eve` | INTEGER | ✓ | ✓ | Pontos építési év (ahol a hirdetés megadta) |
| `epites_eve_kategoria`| TEXT | ✓ | ✓ | Építési korszak (1950 előtt, 1950-1979, 1980-1999, 2000-2019, 2020 után) |
| `epites_eve_becsult`| INTEGER | ✓ | ✓ | Imputált év korszak-középértékekkel (1930, 1965, 1990, 2010, 2023) |
| `epulet_kora_ev` | INTEGER | ✗ | ✓ | Épület kora 2026-ban: $\max(0, 2026 - \text{epites\_eve\_becsult})$ |

### 4.4. Térinformatikai és Geokódolási jellemzők
| Változónév | Típus | Nyers | Számított | Érvényes N | Leírás |
|---|---|:---:|:---:|:---:|---|
| `geokodolt_lat` | REAL | ✗ | ✓ | 296 | WGS84 szélességi koordináta (EPSG:4326) |
| `geokodolt_lon` | REAL | ✗ | ✓ | 296 | WGS84 hosszúsági koordináta (EPSG:4326) |
| `eov_y` | REAL | ✗ | ✓ | 296 | EOV Keleti koordináta méterben (EPSG:23700) |
| `eov_x` | REAL | ✗ | ✓ | 296 | EOV Északi koordináta méterben (EPSG:23700) |
| `geokodolas_modszere`| TEXT | ✗ | ✓ | 1 320 | `jsonld_agency_exact` (292), `exact_building_rooftop` (4), `nincs_pontos_hazszam` (1024) |
| `geokodolas_pontossag`| TEXT | ✗ | ✓ | 1 320 | `A_agency_exact`, `A_building_rooftop`, `N_nincs_koordinata` |
| `minta_garantalt_pontos`| INTEGER (0/1)| ✗ | ✓ | 1 320 | **Szigorú szűrő:** 1 ha pontos épületpont (296 db), 0 ha házszám nélküli |

### 4.5. Térbeli hálózati elérhetőség és sétaizokrónok (N=296 almintán)
*(A táblázatban szereplő összes távolsági változó a pontos mintán érvényes, a többi 1 024 rekordnál szigorúan NULL.)*

| Célpont / Kategória | Változónév | Mértékegység | Leírás és Módszertan |
|---|---|---|---|
| **Metróállomások** | `tavolsag_metro_halozati_m`| méter | Hálózati távolság a legközelebbi metróig |
| **Metróállomások** | `legkozelebbi_metro_halozati`| szöveg | Legközelebbi M2 vagy M3 állomás neve |
| **Metróállomások** | `menetido_metro_gyalog_perc`| perc | Gyaloglási idő a legközelebbi metróhoz |
| **Metró Izokrón** | `metro_5p_seta`, `10p`, `15p`| dummy (0/1) | 5, 10, 15 perces metró sétaizokrónok |
| **Vasútállomások** | `tavolsag_vasut_halozati_m`| méter | Legközelebbi vasútállomás (Kőbánya alsó/felső/Köki/Rákos) |
| **Vasútállomások** | `legkozelebbi_vasut_halozati`| szöveg | Legközelebbi vasútállomás neve |
| **Vasút Izokrón** | `vasut_5p_seta`, `10p`, `15p`| dummy (0/1) | 5, 10, 15 perces vasútállomás sétaizokrónok |
| **Villamosmegállók**| `tavolsag_villamos_halozati_m`| méter | Hálózati távolság a legközelebbi villamoshoz (75 megálló) |
| **Villamosmegállók**| `legkozelebbi_villamos` | szöveg | Legközelebbi villamosmegálló hivatalos neve |
| **Villamosmegállók**| `menetido_villamos_gyalog_perc`| perc | Menetidő a legközelebbi villamoshoz |
| **Villamos Izokrón**| `villamos_5p_seta`, `10p`, `15p`| dummy (0/1) | 5, 10, 15 perces villamosmegálló sétaizokrónok ($N_{5p}=78$) |
| **Buszmegállók** | `tavolsag_busz_halozati_m`| méter | Hálózati távolság a legközelebbi buszhoz (281 megálló) |
| **Buszmegállók** | `legkozelebbi_busz` | szöveg | Legközelebbi buszmegálló neve |
| **Busz Izokrón** | `busz_5p_seta`, `busz_10p_seta`| dummy (0/1) | 5 és 10 perces buszmegálló sétaizokrónok ($N_{5p}=243$) |
| **Kötöttpálya Index**| `tavolsag_kotottpalya_halozati_m`| méter | **Integrált kötöttpályás távolság:** $\min(\text{metró}, \text{vasút}, \text{villamos})$ |
| **Kötöttpálya Index**| `legkozelebbi_kotottpalya_tipus`| szöveg | "metro", "vasut" vagy "villamos" |
| **Kötöttpálya Izokrón**| `kotottpalya_5p_seta`, `10p`, `15p`| dummy (0/1) | Bármely kötöttpályás gyors tranzit 5, 10, 15p izokrónja |
| **Közparkok** | `tavolsag_park_halozati_m` | méter | Legközelebbi közpark hálózati távolsága |
| **Közparkok** | `legkozelebbi_park_halozati`| szöveg | Legközelebbi park neve (Óhegy park, Népliget, stb.) |
| **Közpark Izokrón** | `park_5p_seta`, `10p`, `15p` | dummy (0/1) | 5, 10, 15 perces park-elérhetőségi izokrónok |

---

## 5. AUDIT ÉS INTEGRITÁSI STATISZTIKÁK

A `verify_master_data.py` rendszerellenőrző futása során az alábbi kulcsfontosságú integritási tesztek zárultak **100.0%-os sikerrel**:

1. **Rekordszám egyezés:**
   - Összes hirdetés: **1 320 db**
   - Eladó lakás: **1 140 db**
   - Kiadó lakás: **180 db**
   - Szöveges leírások: **1 320 db** (FTS5 indexelve)
2. **Koordináta és precizitás arányok:**
   - Garantált pontos tetőpont: **296 db** (Level 1 ügynökségi: 292, Level 2 házszám: 4)
   - Fals precizitás kizárása miatt üres: **1 024 db**
   - Nem található egyetlen hiányzó ár vagy érvénytelen alapterület sem.
3. **Fizikai útvonal-integritás:**
   - $\text{Hálózati távolság} < \text{Euklidészi távolság}$ hibák száma: **0 db** (fizikailag lehetetlen útvonal kizárva).
   - $\text{Kötöttpálya távolság} > \min(\text{metró}, \text{vasút}, \text{villamos})$ ellentmondások: **0 db**.
4. **Hedonikus logikai konzisztencia:**
   - Korrigált alapterület $<$ Nettó alapterület: **0 db**.
   - Negatív épületkor: **0 db** (a 2027/2028-ban átadandó tervezett új építések kora egységesen 0 év).
   - Izokrón hierarchia: $\text{5p} \le \text{10p} \le \text{15p}$ minden célpontra teljesül (kivéve 1 ismert, rögzített vasúti anomáliát: `listing_id` 35461173, ahol `vasut_5p_seta=1` és `vasut_10p_seta=0` — adatgenerálási szinten javítandó).

---

## 6. AJÁNLOTT KUTATÁSI ÉS ÖKONOMETRIAI FELHASZNÁLÁS

### 6.1. Hedonikus árregresszió specifikációja (OLS / WLS)
$$\ln(P_i) = \alpha + \sum_{k} \beta_k X_{ki} + \sum_{m} \gamma_m Z_{mi} + \sum_{j} \delta_j \cdot \text{Vasút\_Zóna}_{ji} + \sum_{l} \theta_l \cdot \text{Vasút\_Izokrón}_{li} + \varepsilon_i$$
- **Függő változó:** `log_ar` (vagy `log_nm_ar`)
- **Fizikai kontrollváltozók ($X_k$):** `korrigalt_alapterulet_nm`, `szobaszam_osszes`, `is_foldszint`, `is_zaroszint`, `has_lift`, `has_klima`, `allapot_kod`, `is_panel`, `epulet_kora_ev`, `has_tavfutes`
- **Környezeti és tranzit kontrollok ($Z_m$):** `kotottpalya_5p_seta`, `park_10p_seta`, `poi_15p_count`, `varosresz` (fix hatások / dummyk)
- **Fő tesztváltozók ($\delta_j$, $\theta_l$):** `vasut_zona` (6 diszjunkt immissziós sáv, referencia: >2000 m) és `vasut_5p_seta` / `vasut_10p_seta` / `vasut_15p_seta` (hálózati TOD izokrónok; referencia: >1125 m). A folytonos `log_tavolsag_vasut_m` robusztusságvizsgálatként.

### 6.2. Mintaválasztási ajánlás
- **Alminta A (Térbeli és Izokrón Elemzés):** `WHERE minta_garantalt_pontos = 1` ($N = 254$ eladó lakás). Ezen a mintán futtatható le a legmagasabb precizitású térbeli ökonometria és hálózati elérhetőségi vizsgálat.
- **Alminta B (Teljes Kerületi Hedonika):** `WHERE kinalat_tipus = 'elado'` ($N = 1 140$ eladó lakás). Ezen a mintán a városrészi fix hatásokkal és épülettípusokkal becsülhetők az alapvető kőbányai árugorások.

---

## 7. TÖBBTERÜLETES KITERJESZTÉS (MULTI-AREA EXTENSION)

A „frozen baseline" kőbányai minta mellett a kutatás egy **nemzetközi benchmarkkal**
bővült, és a keretrendszer tetszőleges számú terület kezelésére alkalmas
(`data/areas.yaml`):

| Terület | Szerepkör | Minta | Garantált pontos | Valuta |
|---|---|---|---|---|
| Budapest X. kerület (Kőbánya) | fő mintaterület | 1 320 db (1 140 eladó / 180 kiadó) | 296 db | HUF |
| Bécs 2. kerület (Nordbahnhof) | nemzetközi benchmark | 1 037 db (868 eladó / 169 kiadó) | 1 037 db | EUR |
| Kontroll 1 (pl. Ferencváros) | kontroll (előkészítve) | — | — | — |
| Kontroll 2 (pl. Zugló) | kontroll (előkészítve) | — | — | — |

A bécsi mester adathalmaz (`data/processed/wien_nordbahnhof_szamitott_master.parquet`)
és pontos geokódolt réteg (`data/processed/wien_nordbahnhof_pontos.geojson`) ugyanazt a
kanonikus sémát követi, mint Kőbánya. A teljes elemzési csővezetéket a
`report_engine/` csomag futtatja (`python generate_area_report.py --all`), a kimeneti
többterületes portál pedig a `html_reports/index.html`.

## Adatrétegezési szabály (nyers vs. származtatott)

- `data/raw/` — KIZÁRÓLAG a scrape-elt nyers adat, változtatás nélkül.
- `data/processed/` — a **kanonikus séma** (`data/schema.yaml`): azonosítók, árak,
  fizikai jellemzők + a pipeline által DEFINÍCIÓ SZERINT számolt származtatott
  változók (térbeli távolságok, hálózati mutatók, izokrón-dummyk, log-árak,
  kategóriák). Minden képlet itt és a `scripts/`-ben dokumentált; a processed
  fájlokat tilos kézzel szerkeszteni.
- A notebookok kizárólag elemzés-specifikus átalakításokat számolnak
  (pl. interakciók, modell-dummyk), és SOHA nem írnak vissza a processed-be.

## Bécsi adat-őszinteség (2026-10-07 óta)

- **Koordináta-precizitás:** a willhaben a magánszféra miatt szórja a
  koordinátákat (1037 hirdetésből 324 egyedi koordinátapár). A
  `minta_garantalt_pontos` bécsi kritériuma: **egyedi koordinátapár** (1) vs.
  megosztott, körzeti szintű pont (0); `geokodolas_pontossag`:
  `A_egyedi_koordinata` / `B_megosztott_koordinata`.
- **Panel-proxy:** bécsi `is_panel = 1` az `ingatlan_altipus == '1945-1990'`
  korszak esetén (az iparosított technológiájú korszak közelítése — NEM
  épületszintű azonosítás, hanem dokumentált proxy; 68 hirdetés).
