# Kőbánya Lakáspiaci Elemzés és Mázsa Téri Értéknövekmény-vizsgálat (IFK-TDK 2026)

## 📌 A Kutatás Célja és Rendszerstruktúrája
A kutatás Budapest X. kerület (Kőbánya) teljes online lakáspiaci kínálatát ($N = 1320$ hirdetés) elemzi mikro-ökonometriai, térinformatikai és pénzügyi modellekkel. A projekt központi hipotézise a vasúti infrastruktúra kétarcú hatásának (*Double-Edged Sword of Rail Transit*) kimutatása, valamint a tervezett Mázsa téri közösségi városmegújítás által generált magánpiaci értéknövekmény közösségi visszanyerésének (*Land Value Capture – LVC*) szimulációja.

A projekt szigorúan két fő pillérre támaszkodik:
1. **`data/`**: Fix, fagyasztott kiindulási adatbázis (ingatlan.com webkapart adatok, geokódolt koordináták, OSM gyalogos hálózati metrikák).
2. **`notebooks/`**: 12 db egymásra épülő, determinisztikusan futtatható és interaktív JupyterLab kutatási notebook.

Emellett a **`html_exports/`** mappa tartalmazza mind a 12 notebook böngészőben közvetlenül (Python nélkül) megnyitható, beágyazott Plotly grafikonokkal ellátott interaktív HTML változatát.

---

## 📐 Módszertani Standardok és Elméleti Keret

1. **Infrastrukturális horgonypontok funkciója**:
   - **Kőbánya alsó vasútállomás**: Meglévő közösségi közlekedési gyorsvasúti csomópont $\rightarrow$ **TOD (Transit-Oriented Development)** gyalogos elérhetőségi prémium mérése.
   - **Mázsa tér**: Fejlesztés alatt álló barnamezős akcióterület $\rightarrow$ **Városmegújítási hatás és LVC** szimulációja.

2. **Távolságmetrikák és sávok**:
   - **Környezeti terhek (zaj, rezgés, por)**: **Légvonalbeli (euklideszi)** távolság a vágánytengelytől (`tavolsag_vasut_m`).
     - *Nemzetközi immissziós sávok (EU Noise Directive / WHO)*: `<150 m` (Immisszió), `150–300 m` (Erős teher), `300–500 m` (Átmeneti), `500–1000 m` (Háttérzaj), `1000–2000 m` (Közepes ref.), `>2000 m` (Tiszta ref.).
   - **Gyalogos elérhetőség (TOD)**: **Hálózati** távolság OpenStreetMap gyalogos úthálózaton ($v = 1.25\text{ m/s} = 4.5\text{ km/h}$).
     - *Gyalogos izokrónák*: $\le 375\text{ m}$ (5 perc), $375–750\text{ m}$ (10 perc), $750–1125\text{ m}$ (15 perc).

3. **A vasút kétarcú hatása a hedonikus ármodellben (NB 04)**:
   - A vasúti sín közelsége erősen szignifikáns negatív externália ($\beta = +0.000107$, $p = 0.0061$, azaz 100 méterenként $+1.07\%$ árnövekmény a távolodással).
   - A Kőbánya alsó vasútállomás TOD elérhetőségi prémiuma elméletileg helyes negatív előjelű ($\beta < 0$), de statisztikailag jelenleg elnyomott ($p = 0.808$), amelyet a Mázsa téri aluljárók és intermodális fejlesztés tud felszabadítani.

---

## 📚 A 12 Kutatási Notebook Jegyzéke

| Sorszám | Notebook Fájl | Téma és Módszertan |
| :---: | :--- | :--- |
| **00** | [`00_adathalmaz_attekintes.ipynb`](notebooks/00_adathalmaz_attekintes.ipynb) | Adatminőség-ellenőrzés, adatszótár, hiányzó értékek és lefedettségi KPI-k ($N=1320$). |
| **01** | [`01_leiro_statisztika_es_eda.ipynb`](notebooks/01_leiro_statisztika_es_eda.ipynb) | Feltáró adatelemzés (EDA), eloszlások ferdesége, városrészi ár- és alapterület-összehasonlítások. |
| **02** | [`02_arstruktura_es_szegmentacio.ipynb`](notebooks/02_arstruktura_es_szegmentacio.ipynb) | Árképzés szerkezet szerint (panel vs. tégla diszkont, állapotindex, emeleti gradiens). |
| **03** | [`03_terbeli_elemzes_es_terkepek.ipynb`](notebooks/03_terbeli_elemzes_es_terkepek.ipynb) | Interaktív térképi pontmegjelenítés (`scatter_map`), ársűrűségi hőtérkép (`density_map`) és távolsági gradiens. |
| **04** | [`04_hedonikus_armodell.ipynb`](notebooks/04_hedonikus_armodell.ipynb) | Hedonikus regresszió (OLS, WLS, Robusztus HC3), VIF multikollinearitás, 3 modell lépcsőzetes ökonometriai tesztje. |
| **05** | [`05_vasuti_diszkont_es_izokronok.ipynb`](notebooks/05_vasuti_diszkont_es_izokronok.ipynb) | Nemzetközi immissziós sávok és 5–10–15 perces gyalogos izokrónák kvantitatív prémiumvizsgálata. |
| **06** | [`06_berleti_piac_es_rent_gap.ipynb`](notebooks/06_berleti_piac_es_rent_gap.ipynb) | Bérleti piac, bruttó/nettó hozamszámítás, Price-to-Rent ráta és Neil Smith-féle Rent Gap. |
| **07** | [`07_lvc_szimulacio.ipynb`](notebooks/07_lvc_szimulacio.ipynb) | Land Value Capture (LVC) dinamikus Cash Flow, 20 éves NPV és érzékenységi mátrix. |
| **08** | [`08_monte_carlo_kockazat.ipynb`](notebooks/08_monte_carlo_kockazat.ipynb) | 10 000 futásos Monte Carlo szimuláció, VaR (95%), CVaR és Tornado érzékenység. |
| **09** | [`09_klaszter_es_tipologia.ipynb`](notebooks/09_klaszter_es_tipologia.ipynb) | Gépi tanulásos piaci szegmentáció (K-Means, Hierarchikus), könyök-módszer, Silhouette és PCA. |
| **10** | [`10_moran_es_autokorrelacio.ipynb`](notebooks/10_moran_es_autokorrelacio.ipynb) | Térbeli autokorreláció (Globális Moran's I), permutációs teszt és LISA hotspot klaszterek. |
| **11** | [`11_ingatlan_kereso_dashboard.ipynb`](notebooks/11_ingatlan_kereso_dashboard.ipynb) | Teljes funkciós interaktív ingatlan- és adatszűrő dashboard dinamikus KPI kártyákkal és térképpel. |

---

## 🚀 Futtatás és Használat

### Helyi környezet indítása
1. Klónozd a repót:
   ```bash
   git clone <repo_url>
   cd 03_Kőbánya-ingatlan.com
   ```
2. Hozz létre virtuális környezetet és telepítsd a függőségeket:
   ```bash
   python -m venv .venv
   .\.venv\Scripts\pip install -r requirements.txt
   ```
3. Indítsd el a JupyterLab felületet a `Start_JupyterLab.bat` futtatásával vagy terminálból:
   ```bash
   .\.venv\Scripts\jupyter lab
   ```

### Notebookok újragenerálása és előszámítása
- Notebook struktúra generálása: `python build_all_notebooks.py`
- Kimenetek előszámítása és HTML export: `python notebooks/precalculate_all.py`

### Megtekintés nbviewer.org-on
A repó GitHubra való feltöltése után a notebookok közvetlenül megtekinthetők interaktív böngészős formában:
`https://nbviewer.org/github/<FELHASZNÁLÓNÉV>/<REPO_NÉV>/tree/main/notebooks/`
