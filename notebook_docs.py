# -*- coding: utf-8 -*-
"""
notebook_docs.py
Univerzális, területfüggetlen tudományos narratívákat, elméleti hátteret és módszertani 
magyarázatokat tartalmazó szótár.
A szövegek kizárólag az egzakt eredményekre, a módszertanra, az ok-okozati összefüggésekre
és a változók jelentőségére fókuszálnak. Helyspecifikus megállapításokat nem tartalmaznak.
"""

NOTEBOOK_DOCS = {
    # ===========================================================================
    # NB00
    # ===========================================================================
    'nb00': {
        'intro': r"""# 00. Adathalmaz Áttekintés és Minőségi Riport

**TDK Kutatási Téma**: {short_name} lakóingatlan-piacának komplex térökonometriai, hedonikus és gépi tanulásos vizsgálata.

---

### 📖 A kutatás célja és módszertani alapvetése
A modern városszerkezet és a lakóingatlan-piac vizsgálata során kulcsfontosságú megérteni, hogy az árakat nem csupán az ingatlanok fizikai paraméterei (méret, szobaszám, állapot) határozzák meg, hanem azok térbeli elhelyezkedése és környezeti beágyazottsága is. 

Kutatásunk célja, hogy **modern adattudományi, térinformatikai (GIS) és ökonometriai eszközökkel** számszerűsítse a lakásárakat mozgató erőket. A vizsgálat különös hangsúlyt fektet a hálózati (gyalogos) távolságokra, a közösségi közlekedés (TOD) árfelhajtó hatására, a környezeti terhelések (pl. vasúti zaj) értékcsökkentő szerepére, valamint a közösségi infrastrukturális beruházások által generált értéknövekmény visszanyerési lehetőségeire (Land Value Capture - LVC).

---

### 🗂️ Az adathalmaz felépítése és megbízhatósága
Az elemzés fundamentumát egy nyílt piaci (kínálati) adatbázisból származó, majd térinformatikai adatokkal (pl. OpenStreetMap POI-k, vasúti hálózatok) felbővített komplex mátrix adja.
- A vizsgálat **{n_total} darab ingatlanhirdetés** adatain alapszik.
- Minden megfigyeléshez **számos (akár 150+) változó** tartozik: épületfizikai paraméterek, hálózati gyalogos távolságok, környezeti terhelési mutatók és intézményi ellátottsági indexek.
- Az adatok szigorú tisztítási folyamaton (adattisztítás, duplikáció-szűrés, outlier-kezelés, geokódolás) mentek keresztül az elemzés torzítatlansága érdekében.""",

        'sec1': r"""### 1. Alapvető Adatbázis KPI Mutatók és a Piac Szerkezete

**📌 Módszertani útmutató a mutatókhoz:**
A vezérlőpult az adatbázis legfontosabb, validált sarokszámait foglalja össze a vizsgált területre vonatkozóan:
- **Összes megfigyelés**: {n_total} db a vizsgált kínálatban.
- **Tulajdonjog-átruházás (Eladó)**: {n_elado} db (a piac **{pct_elado}%**-a).
- **Bérleti piac (Kiadó)**: {n_kiado} db (a piac **{pct_kiado}%**-a).
- **Garantált GIS pontosság**: {n_pontos} db (**{pct_pontos}%**).
- **Eladó lakások medián négyzetméterára**: {median_nm_ar} Ft/m² (~{median_ar_millio} millió Ft/m²).
- **Átlagos alapterület**: {mean_area_elado} m² (eladó) és {mean_area_kiado} m² (kiadó).

**🔍 Tudományos interpretáció:**
1. **Tulajdoni szerkezet**: Az eladó és kiadó ingatlanok aránya ({pct_elado}% vs. {pct_kiado}%) megmutatja a terület lakáspiaci funkcióját. A dominánsan eladó piacok a saját tulajdonú otthonok túlsúlyára, míg a magas bérleti arányok befektetési/tranzit zónákra utalnak.
2. **Középértékek robusztussága**: Az ingatlanpiaci áreloszlások szinte mindig jobbra ferdék (log-normálisak) a kiugróan magas árú luxusingatlanok miatt. Ezért az elemzések során a számtani átlag ({mean_ar_millio} M Ft) helyett a **medián árat ({median_ar_millio} M Ft)** tekintjük a piac valódi, torzítatlan középértékének.
3. **Térbeli (GIS) pontosság**: A precíz hálózati távolságmérésekhez és térökonometriai súlymátrixokhoz kizárólag a háztömb szinten garantáltan beazonosított ({n_pontos} db) almintát használjuk fel.""",

        'sec2': r"""### 2. Kínálati Megoszlás Térségi Szegmensek Szerint

**📌 Elemzési szempontok:**
A diagram a vizsgált terület belső mikrokörzeteinek vagy városrészeinek kínálati súlyát mutatja be, elkülönítve az eladó ({n_elado} db) és kiadó ({n_kiado} db) állományt.

**🔍 Ok-okozati összefüggések:**
- **Koncentráció**: A magas hirdetésszámú zónák általában a sűrű beépítésű (pl. lakótelepi) vagy intenzív fluktuációjú területeket jelölik.
- **Funkcionális elkülönülés**: A bérleti piac aktivitása (sárga oszlopok) jellemzően a kiváló közlekedési kapcsolatokkal rendelkező központokban, illetve az egyetemek/irodafolyosók közelében a legmagasabb. A zöldövezeti vagy periférikus zónákban a bérbeadási forgalom strukturálisan alacsonyabb.""",

        'sec3': r"""### 3. Változók Kitöltöttsége (Adatminőségi Audit)

**📌 A minőségbiztosítás elvei:**
A vízszintes sávdiagram a kutatásba bevont változók (ár, alapterület, állapot, koordináta stb.) adatelérhetőségét (fill rate) ábrázolja 0-tól 100%-ig.

**🔍 Miért kritikus ez az ökonometriában?**
- **Fundamentális változók**: Az ár, a szobaszám és az alapterület 100%-os kitöltöttsége alapfeltétele a hedonikus árbecslésnek.
- **Információs aszimmetria**: A közepes kitöltöttségű paraméterek (pl. építés éve, rezsiköltség) hiánya gyakran nem véletlenszerű (Missing Not At Random - MNAR). A rossz energetikai besorolású ingatlanok hirdetői hajlamosak elhallgatni ezeket az adatokat.
- **Modellezési stratégia**: A térbeli modelleket csak a hiánytalan geokódolással rendelkező ({pct_pontos}%) mintán futtatjuk, biztosítva a szigorú geometriai topológiát.""",

        'sec4': r"""### 4. Interaktív Adatszűrő és Validációs Panel

**📌 Cél és funkció:**
Az interaktív táblázat lehetőséget biztosít az adathalmaz nyers szintű (sormintás) ellenőrzésére.
- Szűrési lehetőségek: eladó/kiadó tranzakciótípusok, GIS-pontosság.
- Az alapadatok (cím, ár, alapterület, szobaszám) dinamikusan validálhatók a statisztikai aggregációk megkezdése előtt. A szűrt nézet azonnal újraszámolja a lokális átlag- és mediánárakat, lehetővé téve a mikroszegmensek ad hoc vizsgálatát."""
    },

    # ===========================================================================
    # NB01
    # ===========================================================================
    'nb01': {
        'intro': r"""# 01. Leíró Statisztika és Feltáró Adatelemzés (EDA)

**Cél**: A vizsgált eladó lakáspiac (N = {n_elado} db) fundamentális ár-, méret- és elrendezési struktúrájának statisztikai vizsgálata.

---

### 📖 A nyers átlagárak torzító hatása
A lakáspiaci elemzések gyakori hibája a számtani átlagárak kizárólagos használata. A valóságban a lakáspiac extrém módon heterogén:
1. **Termék-differenciáció**: A kínálatban egyaránt szerepelnek standardizált garzonok és egyedi árazású luxusingatlanok.
2. **Aszimmetrikus eloszlás**: A piac alsó és középső árszegmense sűrű, míg a felső szegmens hosszú, elnyúló "farkat" képez, amely a számtani átlagot felfelé torzítja.

A fejezet az árak valódi eloszlását, a robusztus kvartiliseket, és a statisztikai modellezéshez elengedhetetlen logaritmikus transzformáció indokoltságát mutatja be.""",

        'sec1': r"""### 1. Középértékek és Szóródási Mutatók

**📌 Az eredmények értelmezése:**
A táblázat a teljes eladó állomány (N = {n_elado} db) aggregált statisztikáit mutatja:
- **Átlagár vs. Medián ár**: A {mean_ar_millio} millió Ft-os átlagár és a {median_ar_millio} millió Ft-os medián közötti eltérés pontosan számszerűsíti a felső árszegmens torzító hatását.
- **Fajlagos ár (Ft/m²)**: A piac valódi árszintjét a **{median_nm_ar} Ft/m²** medián érték reprezentálja a leginkább.
- **Relatív szórás**: A négyzetméterárak szórása a heterogenitás mértékfoka. A magas (>20%) relatív szórás arra utal, hogy az árakat dominánsan a lokáció és az épületminőség diverzitása magyarázza, nem csupán az alapterület.

**🔍 A kvartilisek jelentősége (Q1, Q2, Q3)**
A kvartilisek az árazási sávokat jelölik ki:
- **Q1 (Alsó negyed)**: A piac "belépő" szintje.
- **Q3 (Felső negyed)**: A prémium szegmens határa.
- **IQR (Interkvartilis terjedelem)**: A piac középső 50%-ának sávszélessége, amely mentes a szélsőértékektől.""",

        'sec2': r"""### 2. Áreloszlás és Logaritmikus Transzformáció

**📌 A hisztogramok összehasonlítása:**
- **Bal ábra (Nyers árak)**: A fajlagos árak (Ft/m²) eloszlása tipikusan jobbra ferde (skewness > 0).
- **Jobb ábra (Log-árak)**: A természetes logaritmus ($\ln(	ext{Ár/m}^2)$) alkalmazásával kapott eloszlás.

**🔍 Ökonometriai és elméleti indoklás:**
1. **Normál eloszlás (Gauss-görbe)**: Az OLS (Ordinary Least Squares) lineáris regresszió egyik alapfeltétele a hibatagok normál eloszlása. A nyers árak aszimmetriája sérti ezt a feltételt, míg a log-transzformáció "kisimítja" azt.
2. **Közvetlen elaszticitás és százalékos hatás**: A hedonikus ármodellekben a logaritmikus függő változó ($\ln Y$) alkalmazása lehetővé teszi, hogy a magyarázó változók ($X$) becsült együtthatóit ($eta$) közvetlenül **százalékos prémiumként vagy diszkontként** (marginal willingness to pay) értelmezzük."""
    },

    # ===========================================================================
    # NB02
    # ===========================================================================
    'nb02': {
        'intro': r"""# 02. Árstruktúra és Piaci Szegmentáció

**Cél**: A lakáspiac belső tagozódásának és az épületfizikai attribútumok (állapot, építőanyag, felszereltség) izolált árazási hatásának feltárása.

---

### 📖 A piac strukturális heterogenitása
A városi ingatlanpiac nem egyetlen homogén termék piaca, hanem számtalan részpiac (szegmens) halmaza. Egy ingatlan értékét alapvetően meghatározza:
1. **Épülettípus**: A technológia (panel vs. tégla) eltérő avulási rátával és társadalmi megítéléssel rendelkezik.
2. **Műszaki állapot**: A felújított és a felújítandó lakások közötti árrés a "rent gap" (újratermelési potenciál) indikátora.
3. **Kényelmi funkciók**: Az erkély, a lift vagy a parkolóhely megléte a modern életminőség szűk keresztmetszeteit árazza be.""",

        'sec1': r"""### 1. Panel Diszkont és Építőanyag-specifikus Árazás

**📌 Megfigyelések (Boxplot analízis):**
A dobozdiagramok (boxplot) az építési technológiák szerinti fajlagos árak eloszlását vizualizálják. A doboz a piac középső 50%-át (IQR), a középső vonal a mediánt mutatja.

**🔍 Tudományos értelmezés:**
- **A Panel Diszkont**: A házgyári technológiával épült (panel) lakások szinte minden urbanizált környezetben rendszerszintű negatív áreltérést (diszkontot) mutatnak a téglaépítésű lakásokhoz képest. Ennek okai az alacsonyabb energetikai hatékonyság, a kötött alaprajz és a magasabb amortizációs kockázat.
- **Szóráskülönbségek**: A panellakások dobozai jellemzően "feszesebbek" (kisebb árszórás), mivel erősen standardizált termékek. A téglalakások nagyobb szórása a minőség, az életkor és az elhelyezkedés extrém diverzitásából fakad.""",

        'sec2': r"""### 2. Kényelmi Funkciók Marginális Prémiuma

**📌 Értékvezérlő paraméterek:**
- **Erkély/Terasz hatás**: A sűrű beépítésű városrészekben a privát kültér (outdoor tér) szűkössége miatt az erkélyek felára kifejezetten mérhető (marginal willingness to pay).
- **Lift jelenléte**: Az akadálymentesítés, az elöregedő társadalom és a magasabb emeleti (panorámás) lakások jobb megközelíthetősége miatt a lift kiemelt értékvezérlő paraméter az adathalmazban.""",

        'sec3': r"""### 3. Állapot-alapú Értékcsökkenés (Amortizációs Görbe)

**📌 A műszaki állapot árazása:**
A grafikon a lakások műszaki és esztétikai állapota (pl. felújított, jó, közepes, felújítandó) szerinti medián négyzetméterárakat ábrázolja.

**🔍 Rent Gap (Különbözeti Járadék) elmélet:**
A "felújított" és a "felújítandó" lakások közötti fajlagos árkülönbség elméletileg megegyezik a felújítás átlagos négyzetméter-költségével, plusz a befektetői kockázati prémiummal. Ha az árrés (diszkont) jelentősen meghaladja a reális kivitelezési költségeket, az **térbeli arbitrázs-lehetőséget** jelez: a tőke beáramlása (dzsentrifikáció) várható az adott szegmensben."""
    },

    # ===========================================================================
    # NB03
    # ===========================================================================
    'nb03': {
        'intro': r"""# 03. Térbeli Elemzés és Interaktív GIS Térképek

**Cél**: Az ingatlanárak makrotérbeli eloszlásának, a lokációs gócpontoknak és az urbánus térszerkezetnek a vizualizációja.

---

### 📖 A lokáció elsődlegessége ("Location, location, location")
Az ingatlanok árazásában az elsődleges tényező nem az épület, hanem az általa elfoglalt tér (a telek) értéke. Az urbánus tér nem izotróp (nem egyenletes): a központok, közlekedési tengelyek és zöldterületek körül "érték-hegyek" (hotspotok), míg az ipari, barnamezős vagy zajterhelt zónák körül "érték-völgyek" alakulnak ki.

A térinformatikai (GIS) vizualizációk célja, hogy ezeket az összefüggéseket láthatóvá tegyék a garantált pontosságú ({n_pontos} db) almintán.""",

        'sec1': r"""### 1. Ponttérkép és Fajlagos Árak Térbeli Eloszlása

**📌 Interpretációs útmutató:**
A térképen minden pont egyedi ingatlant jelöl, ahol a színskála (sötétkéktől a sárgáig) a fajlagos árat (Ft/m²) kódolja. 
- A térbeli klasztereződés vizuálisan is azonosítható: a hasonló árú ingatlanok csoportosulása egyértelműen bizonyítja a **térbeli autokorreláció** jelenlétét (amelyet a 08. fejezetben statisztikailag is tesztelünk Tobler első földrajzi törvénye alapján).""",

        'sec2': r"""### 2. Fajlagos Árak Sűrűségtérképe (Kernel Density Heatmap)

**📌 A Heatmap (hőtérkép) logikája:**
Az egyedi pontok zaját egy simított, folytonos felületté (KDE - Kernel Density Estimation) alakítjuk, amely megmutatja a piac regionális ársúlypontjait.
- **Meleg színek (sárga/piros)**: A prémium árazású, magas presztízsű területeket jelölik (pl. zöldövezetek, történelmi mag).
- **Hideg színek (kék/lila)**: Az alulárazott, gyakran infrastrukturális deficittel vagy környezeti terheléssel küzdő zónákat (perifériák, rozsdaövezetek) mutatják.

**🔍 Városfejlesztési konklúzió:**
A hőtérkép gradiens vonalai (ahol a meleg színek hirtelen hidegbe csapnak át) jelölik a városszövet fizikai törésvonalait (pl. vágányhálózatok, autópályák, ipari zónák), amelyek hermetikusan elszigetelik a különböző értékű lakózónákat."""
    },

    # ===========================================================================
    # NB04
    # ===========================================================================
    'nb04': {
        'intro': r"""# 04. Környezeti Terhelés és a Vasúti Paradoxon

**Cél**: A hálózati infrastuktúrák (kötöttpálya) kettős – értéknövelő és értékcsökkentő – hatásának izolálása gyalogos izokrónok és távolsági pufferek segítségével.

---

### 📖 Miért "kettős természetű" a vasút az ingatlanpiacon?
A lineáris közlekedési infrastruktúrák klasszikus paradoxont generálnak a városi térben:
- **Környezeti teher (Zaj- és Immissziós hatás)**: A nyílt vágányok és teherpályaudvarok közvetlen környezetében a zaj, a rezgés, a por és a vizuális szennyezés rontja az életminőséget. Ez az ingatlanárakban **negatív externáliaként (diszkont)** csapódik le.
- **Elérhetőségi prémium (Transit-Oriented Development - TOD)**: Az állomások gyalogos vonzáskörzetében élők számára a gyors, dugómentes közlekedés értékes időmegtakarítást jelent, ami megemeli az ingatlanok értékét.

Ebben a fejezetben ezt a két egymásnak feszülő erőt választjuk szét térinformatikai eszközökkel.""",

        'sec1': r"""### 1. Vasúti Vágányok Távolsága (Immissziós Sávok)

**📌 A Vasúti Diszkont Kvantifikálása:**
A lakások lineáris (légvonalbeli) távolságát mértük a legközelebbi aktív felszíni vágánytól. A mintát zajterhelési zónákra osztottuk:
- **Közvetlen immisszió (<150m)**: Súlyos zaj- és rezgésterhelés.
- **Erős teher (150-300m)**: Szignifikáns, de csökkenő hatásterület.
- **Háttérzaj (300-1000m)**: Átmeneti zóna.
- **Referencia zóna (>1000m)**: Vasúti tehertől mentes, tiszta terület.

**🔍 Egzakt Statisztikai Eredmények:**
- A közvetlen immissziós sávban (<150 m) fekvő ingatlanok ára **{vasuti_diszkont}%-os relatív eltérést** mutat a >1000 m-es referencia sávhoz képest. (Medián ár: {vasuti_immisszio_ar} Ft/m² vs {vasuti_ref_ar} Ft/m²).
- **Szignifikancia**: A két független minta eloszlásának azonosságát vizsgáló Mann-Whitney U teszt (p = {mw_pvalue}) és a többcsoportos Kruskal-Wallis H próba (Statisztika: {kw_stat}, p = {kw_pvalue}) alapján az árcsökkenés statisztikailag szignifikáns. A vasút negatív externáliája bizonyítottan beépül az árakba.""",

        'sec2': r"""### 2. Vasútállomások Elérhetősége (Hálózati Izokrónok)

**📌 A TOD (Transit-Oriented Development) Hatás:**
A vágányok távolsága (légvonal) önmagában csak a terhelést méri. Az elérhetőségi prémiumhoz a vasútállomások tényleges **gyalogos hálózati távolságát (izokrónokat)** kell vizsgálni.

**🔍 Ok-okozati struktúra:**
- Egy ingatlan lehet 500 méterre a vágányoktól (mérsékelt zaj), de 15 perces sétára az állomástól (alacsony TOD prémium).
- Ugyanakkor lehet 100 méterre az állomástól (magas zaj, de extrém magas TOD prémium).
- A modern ingatlanpiaci modellekben ez a két hatás (zajdiszkont és TOD prémium) algebrailag összeadódik, meghatározva a nettó hatást. Ezt a kettősséget a 07. fejezet hedonikus OLS regressziója fogja a parciális együtthatókkal izolálni."""
    },

    # ===========================================================================
    # NB05 - NB15 (General methodological blocks without specific geo)
    # ===========================================================================
    'nb05': {
        'intro': r"""# 05. Közösségi Infrastruktúra és a 15 Perces Város

**Cél**: Az ingatlanok intézményi és kereskedelmi ellátottságának (POI - Points of Interest) mérése a "15 perces város" urbanisztikai koncepció tükrében.

---

### 📖 A 15 perces város elmélete
Carlos Moreno (2016) koncepciója szerint az ideális városi szövetben a lakosok minden alapvető funkciót (oktatás, egészségügy, kiskereskedelem, rekreáció) elérnek 15 perces aktív közlekedéssel (séta vagy kerékpár). Az ilyen területeken az ingatlanok "walkability" (sétálhatósági) prémiummal rendelkeznek.""",
        'sec1': r"""### 1. POI Sűrűség és Ellátottsági Térképek

**📌 Kiszámítási módszertan (KDE sűrűség):**
Az OpenStreetMap (OSM) adatbázisából kinyert több száz funkció (boltok, orvosi rendelők, iskolák, parkok) térbeli sűrűségét vizsgáljuk. A sűrűsödési magok (hotspotok) jelölik a 15 perces város lokális centrumait. 

**🔍 Városgazdasági hatás:**
A magas intézményi sűrűség redukálja a lakosok közlekedési tranzakciós költségeit (idő és pénz), ami tőkésedik az ingatlanárakban. A szolgáltatási sivatagokban fekvő ingatlanok ezzel szemben strukturális érték-hátrányt szenvednek.""",
        'sec2': r"""### 2. Pufferelt Hálózati Index

**📌 A határhatások (Edge Effect) korrekciója:**
Ha egy ingatlan a vizsgált adminisztratív terület határán (pl. kerülethatár) fekszik, a szigorúan közigazgatási határon belül végzett POI-számolás torzít (hiszen a lakó átmehet a szomszédos adminisztratív terület szolgáltatóihoz is). Ezt hálózati pufferezéssel és szélesebb (bounding box) lekérdezéssel küszöböljük ki, reális képet adva a peremzónák valós ellátottságáról."""
    },

    'nb06': {
        'intro': r"""# 06. Klaszteranalízis és Városi Tipológiák (Unsupervised ML)

**Cél**: A lakáspiac rejtett szerkezetének és természetes szegmenseinek (archetípusok) feltárása K-Means gépi tanulási algoritmussal.

---

### 📖 Felügyelet Nélküli Gépi Tanulás az Ingatlanpiacon
Míg az emberi agy adminisztratív egységekben gondolkodik, az adatvezérelt algoritmusok (K-Means) többdimenziós térben keresnek hasonlóságokat az ingatlanok között. Az algoritmus úgy csoportosítja a lakásokat, hogy a csoportokon belüli szórás minimális, a csoportok közötti eltérés maximális legyen.""",
        'sec1': r"""### 1. A K-Means Algoritmus Eredményei

**📌 Bemeneti (Feature) tér:**
Az algoritmus nem ismeri az ingatlanok árát vagy koordinátáit! Kizárólag a fizikai paramétereket (méret, szobaszám, állapot, építőanyag) kapja meg.

**🔍 A kialakult Archetípusok (Klaszterek):**
Az adatok alapján organikusan létrejött klaszterek jellemzően felismerhető városi ingatlantípusokat rajzolnak ki (pl. homogén panelek, felújított prémium lakások). Ezek a klaszterek a későbbiekben nominális (dummy) változóként segítik a regressziós modellek magyarázóerejének (R²) növelését."""
    },

    'nb07': {
        'intro': r"""# 07. Hedonikus Ármodell (OLS Regresszió)

**Cél**: Az ingatlanárakat alkotó paraméterek (szobaszám, állapot, vasút távolság) izolált (ceteris paribus) értékének matematikai meghatározása.

---

### 📖 A Hedonikus Árelmélet alapjai (Rosen, 1974)
Egy lakás nem egyetlen termék, hanem hasznosságot hordozó tulajdonságok (attribútumok) "csomagja". Amikor a vevő kifizeti a vételárat, valójában megvásárol x négyzetmétert, y szobát, bizonyos infrastrukturális adottságokat és z méter távolságot a közlekedési hálózattól. A hedonikus regresszió (OLS) képes ezen tulajdonságok "rejtett (implicit) árát" egyenként, a többi tényező változatlansága mellett meghatározni.""",
        'sec1': r"""### 1. Az OLS Modell Eredményei és az Együtthatók

**📌 A modell specifikációja:**
Függő változó: A fajlagos négyzetméterár természetes logaritmusa ($\ln(	ext{Ár/m}^2)$). Ennek köszönhetően a becsült együtthatók (Coefficients) közvetlenül százalékos prémiumként (vagy diszkontként) értelmezhetők.

**🔍 Egzakt Eredmények (p-érték és t-statisztika):**
- Csak azokat a változókat tekintjük érvényesnek, ahol a $P>|t|$ érték kisebb, mint 0.05 (95%-os szignifikancia).
- A modell determinációs együtthatója ($R^2$) mutatja meg, hogy a beépített változók együttesen a lakásárak varianciájának hány százalékát képesek megmagyarázni. A megmagyarázatlan rész (hibatag) az egyedi, nem számszerűsíthető jellemzőket (pl. kilátás, szomszédok) és a térbeli autokorrelációt tartalmazza."""
    },

    'nb08': {
        'intro': r"""# 08. Térbeli Autokorreláció és Moran-I Teszt

**Cél**: A térbeli függőség (Tobler törvénye) matematikai bizonyítása és a klasszikus OLS modell torzításának feltárása.

---

### 📖 Tobler Első Földrajzi Törvénye (1970)
*"Minden dolog összefügg minden más dologgal, de a közeli dolgok jobban összefüggnek, mint a távoliak."*
Az ingatlanpiacon ez azt jelenti, hogy egy drága lakás mellett nagyobb eséllyel áll egy másik drága lakás (spillover hatás). Ha ez a térbeli összefüggés fennáll, az sérti az OLS regresszió egyik alapfeltételét (a hibatagok függetlenségét). Ezt a jelenséget hívják térbeli autokorrelációnak.""",
        'sec1': r"""### 1. Súlyozott Térbeli Hálózat és a Globális Moran-I

**📌 Módszertan:**
Először egy K-legközelebbi szomszéd (KNN) térbeli súlymátrixot ($W$) építünk fel, amely definiálja, hogy mely ingatlanok tekinthetők egymás szomszédainak. Ezt követően kiszámítjuk a Globális Moran-I statisztikát az OLS modell maradéktagjaira (reziduumokra).

**🔍 Egzakt Eredmény:**
Ha a Moran-I statisztika szignifikánsan pozitív (p < 0.05), az matematikailag igazolja, hogy az OLS modell nem képes kezelni a térbeli struktúrákat, így térökonometriai (SAR/SEM) modellek alkalmazása szükséges."""
    },

    'nb09': {
        'intro': r"""# 09. Térökonometria (SAR és SEM Modellek)

**Cél**: Az árbecslés pontosságának javítása és a szomszédsági (spillover) hatások beépítése fejlett térbeli modellekkel (Spatial Autoregressive & Spatial Error Model).

---

### 📖 Miért kellenek a Térökonometriai modellek?
Mivel a 08. fejezet bebizonyította a térbeli autokorreláció jelenlétét, az egyszerű OLS becslés együtthatói torzítottak lehetnek. 
- **SAR (Spatial Autoregressive Model)**: Feltételezi, hogy az ingatlan árát közvetlenül befolyásolja a szomszédos ingatlanok ára (pl. "presztízs" hatás).
- **SEM (Spatial Error Model)**: Feltételezi, hogy a térbeli összefüggés nem az árak között, hanem a mérhetetlen, kimaradt változók (pl. levegőminőség, lokális közbiztonság) között áll fenn, amelyek beépülnek a hibatagba.""",
        'sec1': r"""### 1. SAR Modell és a Térbeli Multiplikátor

**📌 Az eredmények értelmezése:**
- **Rho ($ho$) paraméter**: A térbeli késleltetés (spatial lag) együtthatója. Szignifikáns jelenléte igazolja, hogy a szomszédos lakások árai hatnak egymásra.
- **Térbeli Multiplikátor**: A SAR modell legfontosabb tulajdonsága! Értéke **{spatial_multiplier}x**, ami azt jelenti, hogy ha egy ingatlan drágul, az az árnövekmény hullámszerűen továbbterjed a szomszédos ingatlanokra is.
- **Modell illeszkedés**: A SAR modell $R^2$ értéke (**{sar_r2}**) jellemzően magasabb az OLS-nél, bizonyítva a térbeli modellezés fölényét."""
    },

    'nb10': {
        'intro': r"""# 10. Lokális Térökonometria (GWR)

**Cél**: A térbeli stacionaritás feloldása, és annak bizonyítása, hogy a lakáspiaci jellemzők árazása nem állandó a városon belül.

---

### 📖 A Geographically Weighted Regression (GWR) elve
A hagyományos modellek (OLS, SAR) egyetlen globális együtthatót számolnak ki a teljes területre. A valóságban azonban egy adott tulajdonság értéke a sűrű, zajos belvárosban sokkal eltérőbb lehet, mint a zöldövezeti peremeken. A GWR algoritmus minden egyes ingatlannál egy lokális regressziót futtat a környező szomszédok súlyozásával, így térképként vizualizálhatóvá teszi a paraméterek térbeli változását.""",
        'sec1': r"""### 1. Térben Változó Együtthatók Vizualizációja

**📌 Térképi interpretáció:**
A GWR hőtérképei az együtthatók (pl. a felújított állapot prémiumának) térbeli intenzitását mutatják. A piros/meleg zónákban az adott tulajdonság felára extrém magas, míg a hideg zónákban a piac alig hajlandó fizetni érte."""
    },

    'nb11': {
        'intro': r"""# 11. Gépi Tanulás és Térbeli Arbitrázs (Random Forest)

**Cél**: Nem-lineáris lakásár-előrejelző algoritmus betanítása, és a piacon jelenleg "alulárazott" (arbitrázs) ingatlanok azonosítása.

---

### 📖 A Random Forest (Véletlen Erdő) előnye a regressziókkal szemben
A hagyományos ökonometriai modellek merev algebrai szabályokat követnek. A Random Forest algoritmus azonban döntési fák százait építi fel, így képes felismerni az emberi szem számára láthatatlan, **nem-lineáris és komplex interakciós szabályokat** (pl. ha X tulajdonság fennáll, ÉS Y távolság adott, akkor az ár eltérő ívet ír le).""",
        'sec1': r"""### 1. Modellpontosság és Kiemelkedő Változók (Feature Importance)

**📌 Teljesítmény-metrikák:**
A betanított Random Forest modell a variancia **{rf_r2}** ($R^2$) részét képes megmagyarázni a teszthalmazon. A Feature Importance grafikon megmutatja, hogy a gép számára mely változók hordozták a legnagyobb prediktív erőt az árazásban.

**🔍 Térbeli Arbitrázs (Kereskedési Lehetőség):**
Az arbitrázs-szűrés a predikált (modell által indokoltnak tartott) és a valós hirdetési árat hasonlítja össze. Ha egy ingatlant a modell jóval magasabbra értékel, mint a kiírt hirdetési ár, az **szubjektív alulárazottságot (vételi lehetőséget)** jelezhet."""
    },

    'nb12': {
        'intro': r"""# 12. Bérleti Piac és Rent Gap Elemzés

**Cél**: A bérleti díjak fajlagos elemzése, a bruttó bérleti hozamok (Yield) kiszámítása, valamint a befektetői tőkeallokáció optimalizálása.

---

### 📖 A Bruttó Bérleti Hozam (Gross Rental Yield)
A lakásvásárlás egyszerre lakhatási megoldás és tőkebefektetés. A befektetők számára a legfontosabb iránymutató a bruttó bérleti hozam, amely megmutatja, hogy az éves bérleti díjbevételek a vételár hány százalékát teszik ki. Magasabb hozam jellemzően a kockázatosabb, alacsonyabb tőkeértékű piacokon érhető el, míg a prémium lokációk hozama a magas vételár miatt általában alacsonyabb (presztízs felár).""",
        'sec1': r"""### 1. Bérleti Díjak és Hozamok Eloszlása

**📌 Makro-statisztikák:**
Az aggregált adatok alapján a vizsgált bérleti piacon az elérhető átlagos bruttó bérleti hozam **{brutto_hozam}%**. A hozamok térbeli szóródása a Rent Gap (különbözeti járadék) meglétét bizonyítja: a felújítandó, alulhasznosított ingatlanok megvásárlása és modernizációja (fix beruházási költség mellett) jelentősen megugró bérleti díjakat és arbitrázs-nyereséget generálhat."""
    },

    'nb13': {
        'intro': r"""# 13. Monte Carlo Szimuláció és Kockázatelemzés

**Cél**: A lakásvásárlási befektetésekhez kapcsolódó jövőbeli pénzügyi kockázatok (hozamingadozás, üresedés, kamatkockázat) kvantifikálása sztochasztikus modellezéssel.

---

### 📖 Miért nem elég a determinisztikus hozamszámítás?
A klasszikus "excel-táblás" befektetési számítások statikusak: feltételezik, hogy a lakás mindig ki van adva, és a hitelkamatok fixek. A valóságban a gazdasági környezet sztochasztikus (véletlenszerű). A Monte Carlo szimuláció több ezer független, valószínűségi eloszlásokkal terhelt jövőbeli forgatókönyvet generál, hogy feltérképezze az extrém kockázatokat (fekete hattyú események).""",
        'sec1': r"""### 1. Kockázati Metrikák: VaR és CVaR

**📌 A Value at Risk (VaR) értelmezése:**
A kockázatkezelés aranystandardja.
- **VaR 95%**: **{var_95}%** $ightarrow$ 95% a valószínűsége annak, hogy a befektetés éves hozama ennél *nem lesz rosszabb*.
- **VaR 99%**: **{var_99}%** $ightarrow$ Az extrém stressz-forgatókönyv határa. 

**🔍 Gyakorlati konklúzió:**
A szimuláció rávilágít, hogy a magasabb bruttó hozammal kecsegtető szegmensek (pl. túlkínálatos peremkerületek) volatilitása (üresedési kockázata) aszimmetrikusan magasabb lehet, így a kockázattal súlyozott nettó jelenérték (NPV) gyakran a stabil, diverzifikált portfóliók felé billenti a mérleget."""
    },

    'nb14': {
        'intro': r"""# 14. Közösségi Értékmegosztás (Land Value Capture - LVC)

**Cél**: A nagyléptékű közberuházások (pl. közlekedés, parkfejlesztés) által generált magáningatlan-értéknövekmény számszerűsítése és a visszanyerési mechanizmusok (LVC) szimulációja.

---

### 📖 A Land Value Capture (LVC) közgazdaságtana
Amikor a közszféra adófizetői pénzből új infrastrukturális beruházást hajt végre, a környező magáningatlanok ára jelentősen (akár 15-25%-kal) megugrik. Ez egy **nem kiérdemelt jövedelem (unearned increment)** a tulajdonosok számára. Az LVC (Közösségi Értékmegosztás) olyan modern várostervezési és adózási mechanizmusok összessége (pl. Településrendezési Szerződések - TRSZ), amelyek célja ezen értéknövekmény egy részének visszacsatornázása a közösség felé.""",
        'sec1': r"""### 1. Interaktív Szimulátor és Pénzáram

**📌 A modell dinamikája:**
Az interaktív vezérlőpulton a felhasználó szabadon szimulálhatja a közberuházások paramétereit (Beruházási Költség / CAPEX, Hatásterület lakásszáma).
- A **Makro-modell** kiszámítja, hogy a vizsgált hatásterület ({median_ar_millio} millió Ft-os medián árakkal számolt) összvagyona mekkora nominális értékugrást szenved el a beállított felértékelődés hatására.
- A **Cash Flow (Pénzáram) görbe** bemutatja, hogy ha az állam a keletkezett értéktöbblet egy részét (LVC Kulcs) visszanyeri, a beruházás hány év alatt hozza vissza az árát (Megtérülési idő - ROI)."""
    },

    'nb15': {
        'intro': r"""# 15. Integrált Ingatlan Kereső és Döntéstámogató Vezérlőpult

**Cél**: A korábbi fejezeteken át épített adatbázis és prediktív modellek szintetizálása egyetlen, végfelhasználó-központú, interaktív térképes és táblázatos dashboard formájában.

---

### 📖 Az Elmélettől a Gyakorlatig
A kutatás végső fázisa a transzparencia és a gyakorlati hasznosíthatóság. A feltárt térökonometriai összefüggések, a környezeti terhelések (vasúti diszkontok), a szolgáltatási hálózatok és a Random Forest által predikált valós értékek itt egyetlen dinamikus szűrőrendszerben találkoznak.

A dashboard bizonyítja a **Data-Driven Real Estate (Adatvezérelt Ingatlanpiac)** létjogosultságát: a racionális, arbitrázst kereső befektetői döntések többé nem intuíciókra, hanem mérnöki pontosságú, többdimenziós prediktív analitikára támaszkodhatnak.""",
        'sec1': r""
    }
}


from collections import defaultdict

class DefaultDictProxy:
    def __init__(self, data):
        self.data = data
    def __getitem__(self, key):
        if key not in self.data:
            return ''
        return self.data[key]
    def keys(self):
        return self.data.keys()
    def get(self, key, default=''):
        return self.data.get(key, default)

for k in NOTEBOOK_DOCS:
    NOTEBOOK_DOCS[k] = DefaultDictProxy(NOTEBOOK_DOCS[k])
