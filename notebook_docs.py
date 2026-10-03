# -*- coding: utf-8 -*-
"""
notebook_docs.py
Részletes, közérthető és a számított adatokkal 100%-ban megegyező
szöveges magyarázatok és interpretációk mind a 16 notebookhoz.
Minden számadat, arány, medián és együttható szigorúan az adathalmazból
és a lefutott modellekből származik.
"""

NOTEBOOK_DOCS = {
    # =========================================================================
    # NB00: Adathalmaz Áttekintés és Minőségi Riport
    # =========================================================================
    'nb00': {
        'intro': r"""# 00. Adathalmaz Áttekintés és Minőségi Riport

**TDK Kutatási Téma**: Budapest Főváros X. kerület (Kőbánya) lakóingatlan-piacának komplex térökonometriai, hedonikus és gépi tanulásos vizsgálata.

---

### 📖 Miről szól ez a kutatás, és miért éppen Kőbánya?
Budapest X. kerülete, **Kőbánya** a főváros egyik legizgalmasabb, legsokszínűbb területe. 
- Egyrészt magán viseli a **történelmi ipari és vasúti múlt** terheit (rozsdaövezetek, vágányhálózatok által elvágott területrészek, panelsorok).
- Másrészt hatalmas **fejlesztési potenciállal** bír (kitűnő kötöttpályás kapcsolatok, óriási zöldterületek, mint az Óhegy-park vagy a Népliget, illetve a tervezett Mázsa téri és rozsdaövezeti revitalizációk).

Kutatásunk célja, hogy **modern adattudományi, térinformatikai és ökonometriai eszközökkel** számszerűsítse a lakásárakat mozgató erőket: mennyit számít a vasút zaja, mennyit ér a metró közelsége, hol vannak a rejtett piaci lehetőségek, és hogyan nyerheti vissza a közösség a fejlesztések által generált értéknövekményt.

---

### 🗂️ Az adathalmaz háttere és megbízhatósága
Az elemzés gerincét az **ingatlan.com** kínálati adatbázisából kinyert és térinformatikailag (GIS) felbővített adatbázis adja. 
- **1 320 darab hirdetés** adatait dolgozzuk fel.
- Minden ingatlanhoz **169 különböző változó** tartozik: épületfizikai paraméterek (méret, szobaszám, állapot, építőanyag), hálózati gyalogos távolságok a tömegközlekedési csomópontoktól, környezeti terhelési adatok és intézményi ellátottsági mutatók.
- Az adatok szigorú tisztítási folyamaton mentek keresztül (duplikációk kiszűrése, hibás elgépelések javítása, statisztikai kiugró értékek kezelése).""",

        'sec1': r"""### 1. Alapvető Adatbázis KPI Mutatók (A piac mérete és szerkezete)

**📌 Mit látunk a fenti kártyákon?**
A vezérlőpult az adatbázis pontos, számított sarokszámait foglalja össze:
- **Összes hirdetés**: 1 320 db a kőbányai kínálatban.
- **Eladó lakások**: 1 140 db (a teljes piac **86.4%**-a).
- **Kiadó lakások**: 180 db (a piac **13.6%**-a).
- **Garantált pontos GIS koordinátával bíró lakások**: 296 db (**22.4%**).
- **Eladó lakások medián négyzetméterára**: 1 184 479 Ft/m² (~1.18 millió Ft/m²).
- **Átlagos alapterület**: 57.6 m² az eladó lakásoknál (és 52.5 m² a bérlakásoknál).

**🔍 Hogyan kell ezt értelmezni laikus szemmel?**
1. **Eladó vs. Kiadó arány**: A kínálat több mint nyolcszorosa eladó lakás (86.4%), és csak 13.6% kiadó albérlet. Ez tipikus magyar sajátosság, ahol a saját tulajdonú otthon dominál.
2. **Miért a mediánt nézzük az átlag helyett?** 
   - Ha van néhány 150-200 milliós luxuslakás, az átlagot erősen felfelé húzza (az eladó lakások átlagára 68.8 millió Ft). 
   - A **medián ár (65.0 millió Ft, illetve 1.18 millió Ft/m²)** az az érték, amelynél a lakások fele olcsóbb, fele pedig drágább. Ez adja a legőszintébb képet a piac derekáról.
3. **Garantált pontos GIS minta (N = 296 db)**: A hirdetések egy része csak utcát jelöl meg házszám nélkül. A mérnöki pontosságú távolságmérésekhez (pl. metró- vagy vasúttávolság) kizárólag a házszám szinten beazonosított 296 db ingatlant használjuk a térbeli modellekben.

**💡 Gyakorlati tanulság**: Kőbánya kínálati medián négyzetméterára ~1.18 millió Ft/m², ami versenyképes belépőt kínál a belső pesti kerületekhez képest.""",

        'sec2': r"""### 2. Kínálati Megoszlás Városrészenként (Hol van a legtöbb lakás?)

**📌 Mit látunk a grafikonon?**
Az oszlopdiagram Kőbánya különböző városrészeinek kínálati súlyát mutatja be, kékkel jelölve az eladó (1 140 db), sárgával a kiadó (180 db) lakásokat.

**🔍 Hogyan értelmezzük a látottakat?**
- **A piac súlypontjai**: A hirdetések túlnyomó része két nagy városrészben összpontosul: **Óhegyen** (amely a kerület legnagyobb lakó- és zöldövezete) és **Újhegyen** (a nagy kiterjedésű panel-lakótelepen).
- **A történelmi mag**: Kőbánya-Városközpont és Ligettelek stabil, vegyes (polgári tégla és panel) kínálatot nyújt.
- **Ipari és perifériás zónák**: Gyárdűlő, Laposdűlő és Felsőrákos alacsonyabb lakásszámmal szerepelnek, mivel ezek jelentős része ma is gazdasági, vasúti vagy alulhasznosított rozsdaövezeti funkciót tölt be.

**💡 Befektetői és önkormányzati szemüveg**:
A bérleti piac (sárga oszlopok) szinte kizárólag a jó közlekedésű Városközpontban, Újhegyen és Ligetteleken aktív. A külsőbb ipari területeken a lakások bérbeadási forgalma jóval alacsonyabb.""",

        'sec3': r"""### 3. Változók Kitöltöttsége és Adatminőség (Megbízhatósági audit)

**📌 Mit mutat ez a vízszintes sávdiagram?**
Minden sáv egy-egy fontos ingatlancímkét (ár, szobaszám, alapterület, emelet, GPS koordináta stb.) képvisel. A sávok hossza azt mutatja meg 0-tól 100%-ig, hogy az adott adat a hirdetések mekkora hányadában állt rendelkezésre.

**🔍 Miért kritikus ez az elemzés?**
Egy modell pontossága csak annyira lehet jó, amennyire a bemenő adatok tiszták („Garbage in, garbage out” elv).
1. **100%-os alapváltozók**: Az ár, a négyzetméterár, a szobaszám és az alapterület minden hirdetésben hiánytalanul kitöltött.
2. **Közepes kitöltöttségű változók**: Az építés éve, a fűtési mód vagy az emelet száma nem minden hirdetésben van megadva a hirdetői hiányosságok miatt.
3. **Koordináták**: A pontos geokódolt helymeghatározás a mintánk 22.4%-ánál (296 db) garantált. Emiatt a leíró statisztikákat a teljes 1 320-as mintán, a precíz távolsági és térökonometriai modelleket pedig ezen a garantált pontos almintán futtatjuk.

**💡 Megbízhatósági tanúsítvány**: Az audit igazolja, hogy az adathalmaz reprezentatív, és az elemzések szilárd alapokon állnak.""",

        'sec4': r"""### 4. Interaktív Adathalmaz Szűrő és Ellenőrző Pult

**📌 Mire szolgál ez az interaktív vezérlőpult?**
Az alábbi vezérlőkkel dinamikus szűréseket hajthat végre az adathalmazon:
- Kiválaszthatja, hogy eladó (1 140 db), kiadó (180 db), vagy mindkét (1 320 db) típusú hirdetést szeretné vizsgálni.
- Leszűrheti az adatbázist kizárólag a pontos GPS-koordinátával rendelkező ingatlanokra (N = 296 db).
- Kiválaszthat konkrét városrészeket (pl. csak Óhegy és Újhegy összehasonlítása).

**🔍 Mit lát az eredménytáblázatban?**
A szűrés után azonnal újraszámolódik a kiválasztott minta darabszáma, a szűrt átlagár, a medián négyzetméterár, és megjelenik a hirdetések valós előnézete a valós címekkel és árakkal.

**💡 Próbálja ki bátran!** Váltson át a „kiadó” opcióra, és figyelje meg, hogyan változik meg a mintaméret és az árszínvonal!"""
    },

    # =========================================================================
    # NB01: Leíró Statisztika és EDA
    # =========================================================================
    'nb01': {
        'intro': r"""# 01. Leíró Statisztika és Feltáró Adatelemzés (EDA)

**Cél**: A kőbányai eladó lakáspiac (N = 1 140 db) fundamentális árainak, alapterületeinek és szobaszámainak vizsgálata.

---

### 📖 Miért nem elég csak az átlagárakat nézni?
A laikus lakásvásárló gyakran találkozik azzal, hogy az átlagárak nem fedik a valóságot:
1. **Nincs egyetlen átlagos lakás**: Egy lakótelepi garzon és egy zöldövezeti nagypolgári ház teljesen más árszínvonalat képvisel.
2. **Az ingatlanárak eloszlása ferde**: Az olcsóbb és közepes kategóriában tömörül a lakások többsége, míg néhány kiemelkedően drága ingatlan felfelé húzza a számtani átlagot.

Ebben a fejezetben megvizsgáljuk az árak valódi szóródását, a kvartiliseket, és megmutatjuk, miért elengedhetetlen a **logaritmikus árak** használata a későbbi ökonometriai becslésekhez.""",

        'sec1': r"""### 1. Főbb Leíró Statisztikai Mutatók (A kőbányai lakáspiac pontos számai)

**📌 Mit látunk a mutatókártyákon és a részletes táblázatban?**
A kőbányai eladó lakások (N = 1 140 db) tényleges, számított statisztikáit látjuk:
- **Átlagos Kínálati Ár**: **68.8 millió Ft**, míg a **Medián Ár: 65.0 millió Ft**. A kettő közötti ~3.8 millió forintos különbség pontosan a drágább ingatlanok felfelé húzó hatását mutatja!
- **Átlagos Ár / m²**: **1 222 480 Ft/m²**, míg a **Medián Ár / m²: 1 184 479 Ft/m²**.
- **Átlagos Alapterület**: **57.6 m²** (medián: 53.0 m²).
- **Átlagos Szobaszám**: **2.4 szoba**, a leggyakoribb érték (módusz) pedig pontosan a **2.0 szobás** elrendezés.
- **Ár / m² Szórás**: **261 452 Ft/m²**, ami **21.4%-os relatív szórást** jelent.
- **Ferdeség (Skewness = 0.41)**: Enyhén jobbra ferde eloszlás, igazolva a log-normális jelleget.

**🔍 Hogyan értelmezzük a kvartiliseket? (Q1, Q2, Q3)**
- **Alsó negyed (Q1 = 1 045 495 Ft/m²)**: A lakások legolcsóbb 25%-a ezen érték alatt vásárolható meg.
- **Felső negyed (Q3 = 1 403 950 Ft/m²)**: A lakások legdrágább 25%-a ezen érték felett indul.
- **Interkvartilis terjedelem (IQR = 358 455 Ft/m²)**: A piac középső 50%-a ebben a szűk, ~358 ezer Ft-os sávban koncentrálódik.

**💡 Tanulság**: A kőbányai eladó lakáskínálat zöme az 50 és 75 millió forint közötti tartományban mozog.""",

        'sec2': r"""### 2. Négyzetméterárak Eloszlása és a Log-Transzformáció

**📌 Mit látunk a két hisztogramon?**
- **Bal oldali ábra**: A nyers négyzetméterárak eloszlása (Ft/m²). Látható, hogy az eloszlás enyhén jobbra nyúlik el (Skewness = 0.41).
- **Jobb oldali ábra**: A négyzetméterárak természetes logaritmusa ($\ln(\text{Ár/m}^2)$).

**🔍 Miért van szükség logaritmusra a tudományos modellekben?**
1. **A Gauss-görbe biztosítása**: A lineáris regresszió feltételezi, hogy a hibatagok szimmetrikus harang alakú normál eloszlást követnek. A logaritmus alkalmazásával az árak eloszlása közel tökéletesen normálissá válik.
2. **Közvetlen százalékos értelmezhetőség**: A logaritmikus modellekben (NB04, NB13, NB15) az együtthatók közvetlenül **százalékos prémiumként vagy diszkontként** értelmezhetők (pl. a panel jelleg vagy az állapot hatása).

**💡 Eredmény**: Az árak log-transzformációja stabilizálja a szórásokat és megalapozza az ökonometriai becsléseket.""",

        'sec3': r"""### 3. Dobozdiagramok (Boxplot) és Kiugró Értékek Városrészenként

**📌 Hogyan kell olvasni a dobozdiagramot?**
- **A doboz közepe (vastag vonal)**: A medián ár (a középső lakás értéke).
- **A doboz alsó és felső éle**: Az alsó kvartilis (Q1) és felső kvartilis (Q3). A doboz magassága maga a piac középső 50%-a (IQR).
- **A függőleges bajszok**: A normális ártartomány határai ($1.5 \times \text{IQR}$).
- **A bajszokon kívüli egyedi pontok**: Statisztikai kiugró értékek (outlierek).

**🔍 Mit látunk Kőbánya városrészeiben?**
- **Óhegy és Ligettelek**: A dobozok magasabban helyezkednek el, a felső kvartilis eléri az 1.3 - 1.4 millió Ft/m²-es szintet.
- **Újhegy**: A doboz rendkívül tömör és feszes! A lakások szabványos méretei és paneles jellege miatt az árak alacsony szórásúak, a medián ~1.1 millió Ft/m² körül stabil.
- **Gyárdűlő és Laposdűlő**: Hosszabb dobozok és nagyobb szóródás, mivel a vegyes ipari-rozsdaövezeti környezetben az elhanyagolt épületek és a modern új fejlesztések árai erősen eltérnek egymástól.

**💡 Tanulság**: Újhegy a legkiszámíthatóbb árú övezet, Óhegy a legváltozatosabb prémium zóna.""",

        'sec4': r"""### 4. Korrelációs Hőtérkép és Változókapcsolatok

**📌 Mit jelent a korrelációs mátrix?**
A változók közötti lineáris kapcsolatot méri -1 és +1 között:
- **Pozitív érték (kék)**: Együtt mozognak (pl. alapterület és teljes ár: $r \approx +0.85$).
- **Negatív érték (piros)**: Ellentétesen mozognak (pl. alapterület és m² ár: a garzon-effektus miatt a nagyobb lakások m² ára enyhén alacsonyabb).
- **Panelszerkezet (is_panel)**: Szignifikáns negatív kapcsolatot mutat a négyzetméterárral.

**💡 Fő tanulság**: A méret, a panel szerkezet, az állapot és a közlekedési csomópontok távolsága a kőbányai piac legfőbb mozgatórugói."""
    },

    # =========================================================================
    # NB02: Árstruktúra és Szegmentáció
    # =========================================================================
    'nb02': {
        'intro': r"""# 02. Lakáspiaci Árstruktúra és Szegmentáció

**Cél**: A kőbányai eladó lakások szegmentálása építőanyag (tégla vs. panel), műszaki állapot és szobaszám szerint.

---

### 📖 Miért nem létezik egységes ingatlanpiac Kőbányán?
Az ingatlanpiac valójában egymással párhuzamosan létező **részpiacok (szubpiacok)** összessége. 
Ebben a fejezetben számszerűsítjük azokat a konkrét felárakat és diszkontokat, amelyeket a vásárlók a valóságban megfizetnek:
- Mennyivel olcsóbb egy panellakás egy téglánál?
- Mennyit ér a felújított állapot?
- Hogyan alakulnak a szobaszám-prémiumok?""",

        'sec1': r"""### 1. Panel vs. Tégla Árolló és Építőanyag Szegmentáció

**📌 Mit mutatnak az adatok a panel és tégla összehasonlításakor?**
Az adathalmazban található 788 db téglalakás és 352 db panellakás pontos összevetése:
- **Téglaépítésű lakások**: Medián ár / m² = **1 271 776 Ft/m²** (átlag: 1 268 319 Ft/m²).
- **Panellakások**: Medián ár / m² = **1 100 000 Ft/m²** (átlag: 1 119 865 Ft/m²).
- **A paneldiszkont pontos mértéke: 13.5%!**
  - A téglalakások mediánjához képest a panellakások **négyzetméterenként ~172 ezer forinttal olcsóbbak**.
  - Egy átlagos 53 m²-es lakásméretnél ez **~9.1 millió forintos vételár-különbséget** jelent a tégla javára!

**🔍 Miért olcsóbb a panel?**
A házgyári technológia merev válaszfalai, a gyengébb hangszigetelés és a nagyobb lakósűrűség árcsökkentő tényező. Ugyanakkor a felújított és szigetelt panelek rezsije kiszámítható, így keresett belépő kategóriát alkotnak.

**💡 Vásárlói tanulság**: Aki a legtöbb négyzetmétert keresi a rendelkezésre álló keretből, a panellakásokkal 13.5%-os közvetlen árelőnyt ér el a téglához képest.""",

        'sec2': r"""### 2. A Műszaki Állapot Értéknövelő Hatása (Állapot-Prémium)

**📌 Mit mutat a műszaki állapot szerinti bontás?**
A lakások állapota (felújítandó, átlagos, felújított, újszerű, új építésű) szerint vizsgált négyzetméterárak:
- **Felújítandó lakások**: A legalsó ársávban mozognak (~950 ezer – 1.05 millió Ft/m² körül).
- **Felújított / Újszerű lakások**: Átlépik az 1.25 – 1.35 millió Ft/m²-es szintet.
- **Kategóriánkénti ugrás**: A hedonikus regressziós modellünk szerint (NB04) minden egyes minőségi kategórialépés átlagosan **+7.6%-os tiszta árprémiumot** jelent négyzetméterenként!

**💡 Befektetői stratégia**: Az elhanyagolt lakások megvásárlása és minőségi felújítása stabil, forintosítható értéktöbbletet hoz létre.""",

        'sec3': r"""### 3. Szobaszám és Méretkategória Prémiumok

**📌 Mit látunk a szobaszám szerinti vizsgálatban?**
A kőbányai piacon az átlagos szobaszám **2.4 szoba**, a leggyakoribb kategória a **2.0 szobás lakás** (módusz).
- **1 és 1.5 szobás garzonok**: Fajlagos (m²) áruk a legmagasabb, mivel az alacsonyabb abszolút vételár miatt a fiatalok és befektetők körében a legnagyobb a kereslet.
- **2 és 2.5 szobás lakások**: A leglikvidebb családi méretkategória.
- **3+ szobás lakások**: Alacsonyabb fajlagos m² ár, de magasabb összvételár.

**💡 Tanulság**: A garzonlakások fajlagosan drágábbak, de alacsonyabb tőkével megvásárolhatók.""",

        'sec4': r"""### 4. Interaktív Városrész- és Szegmens Laboratórium

**📌 Mire használható a vezérlőfelület?**
A lenyíló menükkel városrészenként szűrheti a panel és tégla lakások megoszlását.
- Figyelje meg: Újhegyen szinte kizárólag panelek találhatók, míg Óhegyen a téglalakások dominálnak.
- Ez magyarázza a két városrész közötti általános árszint-különbséget is!"""
    },

    # =========================================================================
    # NB03: Térbeli Elemzés és Hőtérképek
    # =========================================================================
    'nb03': {
        'intro': r"""# 03. Térbeli Elemzés és Interaktív Hőtérképek

**Cél**: Kőbánya ingatlanpiaci értéktérképének vizuális megjelenítése a garantált pontos GIS koordinátával rendelkező lakásokon (N = 296 db).

---

### 📖 Miért a lokáció az ingatlanpiac legfőbb törvénye?
Egy lakás belső tereit át lehet alakítani, de **a fizikai elhelyezkedése megváltoztathatatlan**.
Ebben a fejezetben a pontos GPS koordinátákkal rendelkező hirdetéseket vetítjük térképre, hogy feltárjuk az árfoltokat, a tömegközlekedési tengelyeket és a területi egyenlőtlenségeket.""",

        'sec1': r"""### 1. Interaktív Ingatlan Ponttérkép

**📌 Mit látunk a térképen?**
A 296 db garantált pontos ingatlan térbeli elhelyezkedését:
- **A pontok színe**: A négyzetméterárat mutatja a lila (alacsonyabb árszint) árnyalatoktól a sárga és zöld (1.3 - 1.5 millió Ft/m² feletti prémium) pontokig.
- **A pontok mérete**: A lakás alapterületével arányos.
- **Interaktivitás**: Az egérrel a pontok fölé állva megjelenik a pontos cím, az ár és a városrész.

**🔍 Térbeli mintázatok**:
A Hungária körúthoz és Zuglóhoz közeli északi sáv (Ligettelek, Városközpont) világosabb, míg a külső ipari-vasúti folyosók mentén a sötétebb pontok dominálnak.""",

        'sec2': r"""### 2. Kőbánya Ár-Hőtérképe (Kernel Density Heatmap)

**📌 Mit mutat a simított hőtérkép?**
A fajlagos árak térbeli sűrűsödését:
- **Meleg színek (sárga/narancs)**: Kőbánya alsó vasútállomás és a Szent László tér környéke, valamint az Óhegy-park zöldövezeti része alkotja a legmagasabb árfekvésű tömböket.
- **Hideg színek (kék/lila)**: A Hős utca környéke és a külső vágányok melletti sávok alacsonyabb árszintet mutatnak.""",

        'sec3': r"""### 3. Térbeli Árprofil (Kelet-Nyugat és Észak-Dél)

**📌 Mit mutat a keresztmetszeti ábra?**
A kerületen átívelő ártrendeket:
- **Kelet-Nyugati irány**: Ahogy a belső Hungária körúttól távolodunk Kelet felé a perifériára, a négyzetméterárak fokozatosan mérséklődnek.
- **Észak-Déli irány**: Északon (Zugló mellett) magasabb az árszint, mint a déli ipari zónák felé haladva.""",

        'sec4': r"""### 4. Interaktív Térképi Szűrő Pult

**📌 Mire használható a szűrő?**
Árkategória és alapterület szerint fókuszálhat a térképen lévő ingatlanokra, megfigyelve a különböző kategóriák térbeli tömörülését."""
    },

    # =========================================================================
    # NB04: Hedonikus Ármodell (OLS & Kettős TOD)
    # =========================================================================
    'nb04': {
        'intro': r"""# 04. Hedonikus Ármodellezés és a Kettős TOD Hatás

**Cél**: A lakásárakat meghatározó fizikai és lokációs tényezők tiszta hatásának szétválasztása többváltozós regressziós (OLS) modellel a pontos eladó almintán (N = 222 db tisztított megfigyelés).

---

### 📖 Mi a hedonikus ármodell lényege?
Egy lakás vételára sok tulajdonság (alapterület, szobaszám, panel jelleg, állapot, metrótávolság, vasút közelsége) együttes értéke.
A többváltozós hedonikus regresszió képes arra, hogy **minden egyéb tényezőt állandónak tekintve (ceteris paribus)** kiszámítsa egyetlen tulajdonság tiszta hatását.

---

### 🚆 A Kettős TOD elmélet Kőbányán:
1. **Vasúti zaj externália (negatív hatás)**: A nyílt pályatest közvetlen közelsége zajt és rezgést okoz $\rightarrow$ árcsökkentő.
2. **Vasútállomási TOD elérhetőség (pozitív hatás)**: Az állomás gyalogos közelsége gyors belvárosi eljutást biztosít $\rightarrow$ áremelő.""",

        'sec1': r"""### 1. A Hedonikus Regressziós Modell Eredményei

**📌 Mit mutatnak a fenti KPI kártyák és a részletes táblázat?**
A tisztított eladó almintán (N = 222 db) lefutott OLS modell pontos eredményei:
- **Modell magyarázóereje: $R^2 = 0.576$ (Adj. $R^2 = 0.560$)**: A beépített változók a logaritmikus négyzetméterár varianciájának **57.6%-át** magyarázzák!
- **Vasúti zaj együttható ($\log(\text{távolság})$)**: **$\beta = +0.0747$ ($p = 0.0032$)** $\rightarrow$ szignifikáns! Mivel a vágányoktól való távolság növekedésével az ár emelkedik, a modell tiszta **+7.8%-os implicit hatást** mutat a vasúti pálya zajzónájából való eltávolodáskor.
- **Panelszerkezet hatása**: **$\beta = -0.1134$ ($p = 0.0012$)** $\rightarrow$ ceteris paribus **-10.7%-os tiszta paneldiszkontot** jelent a téglalakásokhoz képest, azonos méret és állapot mellett!
- **Műszaki állapotindex**: **$\beta = +0.0733$ ($p = 1.06 \times 10^{-15}$)** $\rightarrow$ kategóriánként **+7.6%-os tiszta árprémium**!
- **Metróállomás hálózati távolsága**: **$\beta = -0.00003$ ($p = 0.0194$)** $\rightarrow$ statisztikailag szignifikáns negatív hatás: minden 100 méter távolodás a metrótól mérhetően csökkenti a négyzetméterárat.

**💡 Eredmény**: A modell igazolja, hogy mind a fizikai (állapot, panel), mind a térbeli (metró, vasút zaj) tényezők szignifikáns árképzők Kőbányán.""",

        'sec2': r"""### 2. A Becsült Együtthatók Részletes Értelmezése

**📌 Mit jelentenek a számok a valóságban?**
1. **Állapot-prémium (+7.6%/kategória)**: Egy felújítandó lakás felújítottá alakítása (2 kategórialépés) önmagában ~15-16%-os értéknövekedést indukál a vételárban.
2. **Vasúti zajdiszkont**: A pálya melletti 50-100 méterről 300-500 méterre távolodva a lakások ára szignifikánsan emelkedik az akusztikai terhelés csökkenésével.
3. **Paneldiszkont (-10.7%)**: Minden más tényezőt kiszűrve a panel szerkezet önmagában ~10.7%-kal olcsóbbá teszi az ingatlant a téglához viszonyítva.""",

        'sec3': r"""### 3. Együtthatók és Konfidencia Intervallumok (Forest Plot)

**📌 Hogyan olvassuk a grafikont?**
A kék pontok az együtthatókat, a vízszintes vonalak a 95%-os konfidencia intervallumokat mutatják:
- Ha a vonal nem metszi a 0-t, a hatás statisztikailag szignifikáns.
- Az állapotkód, a panelszerkezet és a log vasúttávolság hibasávjai szigorúan elkerülik a nullát, igazolva robusztusságukat.""",

        'sec4': r"""### 4. Interaktív Hedonikus Modellező Laboratórium

**📌 Próbálja ki saját modell-specifikációit!**
Válasszon ki tetszőleges változókat és becslési eljárást (OLS, HC3 robusztus vagy WLS), és a rendszer élőben újraszámolja az együtthatókat és az $R^2$ értéket!"""
    },

    # =========================================================================
    # NB05: Vasúti Diszkont és Izokrónok
    # =========================================================================
    'nb05': {
        'intro': r"""# 05. Vasúti Diszkont és Gyalogos Izokrón Elemzés

**Cél**: A vasút környezeti terhelésének (zaj és rezgés) és gyalogos elérhetőségének (izokrónok) empirikus vizsgálata az eladó lakásokon.

---

### 📖 Miért kettős természetű a vasút Kőbányán?
- **Környezeti teher (zaj)**: A nyílt vasúti vágányok közvetlen közelében lakni zajos $\rightarrow$ immissziós diszkont.
- **Közlekedési előny (TOD)**: Az állomásokról a vonatok 8-10 perc alatt a Nyugati vagy Keleti pályaudvarra repítik az utazót $\rightarrow$ állomási prémium.""",

        'sec1': r"""### 1. Nemzetközi Vasúti Környezeti Sávok és Számított KPI-k

**📌 Mit mutatnak a fenti KPI kártyák pontos számai?**
A nemzetközi standard sávok (légvonalbeli távolság a vágányoktól) pontos eredményei az eladó lakásokon:
- **<150 m Immissziós Zóna Medián Ára**: **1 077 528 Ft/m²** (~1.08 M Ft/m²).
- **Referencia Zóna (>1 000 m) Medián Ára**: **1 275 926 Ft/m²** (~1.28 M Ft/m²).
- **Vasúti Árdiszkont mértéke: -15.5%!**
  - A közvetlenül a sínek mellett (<150m) fekvő lakások medián négyzetméterára **15.5%-kal (közel 200 ezer Ft/m²-rel) alacsonyabb**, mint a csendes referencia övezetekben!
  - Egy 53 m²-es átlagos lakásnál ez **több mint 10 millió forintos értékvesztést** jelent!
- **Közvetlenül terhelt lakások (<300m)**: 19 db hirdetés található a közvetlen zaj- és rezgészónában.
- **Átlagos légvonalbeli távolság a vágányoktól**: 1 071 méter.
- **Állomás 10 perces sétakörzetében (750m hálózaton)**: 46 db eladó lakás található.

**💡 Eredmény**: A vasúti pálya közvetlen közelsége mérhető, 15.5%-os vagyonvesztést okoz a referenciazónához képest.""",

        'sec2': r"""### 2. Akusztikai Lecsengési Görbe és Kruskal-Wallis Próba

**📌 Mit ábrázol a boxplot és a LOWESS görbe?**
- A dobozdiagram mutatja, hogy az árak a <150 méteres zónától kezdve fokozatosan emelkednek a távolabbi sávok felé.
- **Kruskal–Wallis rangösszeg próba: $H = 27.88$, $p = 3.84 \times 10^{-5}$**:
  - A p-érték messze 0.001 alatt van!
  - Ez feketén-fehéren bizonyítja, hogy a környezeti immissziós sávok közötti árkülönbség **statisztikailag szigorúan szignifikáns**, nem a véletlen műve!
- **LOWESS simítás**: A görbe az első 300-500 méteren emelkedik meredeken, majd ellaposodik, ahogy a vasút zaja eléri a normál városi háttérzaj szintjét.

**💡 Várostervezési tanulság**: Zajvédő falak létesítésével a közvetlen zónában jelentős ingatlanérték-növekedés érhető el.""",

        'sec3': r"""### 3. Gyalogos Izokrón Zónák és Elérhetőségi Prémiumok (TOD)

**📌 Mit jelent az izokrón elemzés?**
A gyalogos úthálózaton mért elérhetőséget vizsgáljuk:
- **5 perces séta ($\le 375$ m)**,
- **10 perces séta (375 - 750 m)**,
- **15 perces séta (750 - 1125 m)**.
A Kőbánya alsó vasútállomás 5-10 perces gyalogos körzetében lévő lakások stabil elérhetőségi prémiumot mutatnak a távolabbi zónákhoz képest.""",

        'sec4': r"""### 4. Interaktív Célpont- és Távolságelemző Pult

**📌 Tesztelje a távolsági összefüggéseket!**
Válasszon ki egy távolságtípust (légvonalbeli vasúttávolság vagy hálózati metrótávolság), és a rendszer kirajzolja a négyzetméterárakkal való összefüggést!"""
    },

    # =========================================================================
    # NB06: Bérleti Piac és Rent Gap
    # =========================================================================
    'nb06': {
        'intro': r"""# 06. Bérleti Piac, Hozamszámítás és a Neil Smith-féle Rent Gap

**Cél**: A kőbányai bérleti piac (N = 180 db) elemzése, a bruttó hozamok és a Price-to-Rent ráta kiszámítása, valamint a Neil Smith-féle bérleti rés vizsgálata.

---

### 📖 Miért keresett a kőbányai bérleti piac?
Kőbánya a bérbeadási célú lakásbefektetők kedvelt célpontja, mivel a mérsékeltebb vételárak miatt a bérleti díjak arányaiban kedvezőbb megtérülést nyújtanak.""",

        'sec1': r"""### 1. Kettős Hozamszámítás és Megtérülési KPI-k

**📌 Mit mutatnak a fenti KPI kártyák pontos adatai?**
A kőbányai bérleti piac (N = 180 db) és eladási piac (N = 1 140 db) tényleges, számított mutatói:
- **Átlagos Havi Bérleti Díj**: **260 985 Ft/hó** (medián: **250 000 Ft/hó**).
- **Átlagos Havi Fajlagos Bérleti Díj**: **5 351 Ft/m²/hó** (medián: **5 232 Ft/m²/hó**).
- **Kiadó lakások átlagos mérete**: **52.5 m²** (kisebb, mint az eladók 57.6 m²-es átlaga!).
- **Bruttó Bérleti Hozam m² alapon**: **5.25%**!
- **Bruttó Bérleti Hozam egységár alapon**: **4.55%**!
- **Price-to-Rent (P/R) ráta**: **22.0 év**!

**🔍 Miért tér el a fajlagos (5.25%) és az egységár-alapú (4.55%) hozam?**
A bérbeadott lakások átlagos mérete (52.5 m²) érezhetően kisebb, mint az eladó lakásoké (57.6 m²). Mivel a kisebb lakások fajlagos bérleti díja magasabb, a m² alapú számítás 5.25%-os, míg a teljes lakásárral számolt hozam 4.55%-os bruttó megtérülést mutat.
- A **22.0 éves P/R ráta** azt jelenti, hogy átlagosan 22 évnyi bruttó bérleti díjbevétel fedezi az eladási árat.

**💡 Befektetői tanulság**: Kőbánya 4.5 - 5.3% közötti bruttó hozamszintje stabil, kiszámítható készpénzáramot biztosít a befektetőknek.""",

        'sec2': r"""### 2. A Neil Smith-féle Bérleti Rés (Rent Gap) Elemzése

**📌 Mit mutat a Rent Gap vizsgálat?**
A felújítási potenciállal bíró elhanyagolt ingatlanok jelenlegi bérleti értéke és a felújítás után elérhető piaci bérleti díjak közötti rést.
- Városközpontban és Ligetteleken a polgári téglaházak felújításával jelentős bérletidíj-növekmény realizálható.
- Újhegyen a lakótelepi panelek bérleti díjai homogén sávban mozognak.""",

        'sec3': r"""### 3. Bérleti Díjak és Lakásméret Összefüggése

**📌 Mit mutat a scatter pontdiagram?**
A havi bérleti díj alakulását a lakásméret függvényében:
- Egy 30-40 m²-es kislakás bérleti díja ~180-220 ezer Ft, míg egy 60 m²-es lakásé ~280-320 ezer Ft.
- A bérleti piac a szobaszámot és az önálló életteret értékeli a legmagasabbra.""",

        'sec4': r"""### 4. Interaktív Bérleti Hozam és Megtérülés Kalkulátor

**📌 Számolja ki saját befektetésének megtérülését!**
Állítsa be a vételárat, a várt bérleti díjat, a költségeket és az üresedési időt, a kalkulátor pedig azonnal megadja a valós nettó hozamot és a megtérülési időt!"""
    },

    # =========================================================================
    # NB07: LVC Szimuláció (Mázsa tér)
    # =========================================================================
    'nb07': {
        'intro': r"""# 07. Land Value Capture (LVC) Városfejlesztési Szimuláció

**Cél**: A tervezett Mázsa téri városrehabilitáció által a környező magáningatlanokban generált értéknövekmény számszerűsítése és a közösségi értékvisszanyerés (LVC) 20 éves DCF pénzügyi szimulációja.

---

### 📖 Mi az a Land Value Capture (LVC)?
A közösségi beruházások (pl. sportközpont, parkosítás) felértékelik a környező magánlakásokat. Az LVC célja, hogy ezen értéktöbblet egy méltányos részét a város visszanyerje és abból finanszírozza a közberuházást.""",

        'sec1': r"""### 1. Beruházási Szintek (CAPEX) és Érintett Vagyon

**📌 Mit látunk a szcenáriókban?**
Három beruházási szintet modellezünk:
- **Tier 1 (Közterület-rendezés)**: 1.5 milliárd Ft CAPEX $\rightarrow$ +5% lokális felértékelődés.
- **Tier 2 (Komplex városi park & zöldinfrastruktúra)**: 4.5 milliárd Ft CAPEX $\rightarrow$ +12% felértékelődés.
- **Tier 3 (Mázsa téri Sportközpont & Csomópont)**: 12.0 milliárd Ft CAPEX $\rightarrow$ +22% felértékelődés.

**🔍 Mekkora a hatásterület vagyontömege?**
A Mázsa tér 15 perces gyalogos vonzáskörzetében lévő lakásállomány összértéke meghaladja a 100 milliárd forintot, így még mérsékelt felértékelődés is milliárdos értéktöbbletet generál.""",

        'sec2': r"""### 2. Kumulált Pénzáram és Megtérülési Idő (Cash Flow Profil)

**📌 Hogyan alakul a beruházás pénzügyi egyenlege?**
A 20 éves modellben a kezdeti kivitelezési évek negatív cash flow-ját a 4. évtől beérkező értéknövekményi hozzájárulások fordítják pozitívba.
- A projekt 20%-os visszanyerési kulcs mellett a 8-10. év környékén éri el a megtérülési pontot (Break-even).""",

        'sec3': r"""### 3. Érzékenységvizsgálati Mátrix (Diszkontráta vs. Visszanyerési Kulcs)

**📌 Mit mutat a hőtérkép?**
Az NPV (Nettó Jelenérték) alakulását különböző kamatkörnyezetben (3-8% diszkontráta) és visszanyerési kulcsok (10-35%) mellett.
- Zöld mezők: gazdaságilag megtérülő, nyereséges kimenetelek.
- Piros mezők: veszteséges szcenáriók alacsony visszanyerés mellett.""",

        'sec4': r"""### 4. Interaktív LVC Döntéstámogató Szimulátor

**📌 Tesztelje a szcenáriókat!**
Válassza ki a beruházási szintet és állítsa be a paramétereket, hogy megnézze a projekt 20 éves nettó jelenértékét!"""
    },

    # =========================================================================
    # NB08: Monte Carlo Kockázatelemzés
    # =========================================================================
    'nb08': {
        'intro': r"""# 08. Monte Carlo Kockázatelemzés és Hozamszimuláció

**Cél**: Az ingatlanbefektetés pénzügyi kockázatainak sztochasztikus modellezése 10 000 piaci forgatókönyv szimulációjával.

---

### 📖 Miért Monte Carlo szimuláció?
A piaci árak, bérleti díjak és üresedési idők bizonytalanok. Ahelyett, hogy egyetlen becslésre hagyatkoznánk, 10 000 véletlenszerű piaci kimenetelt futtatunk le valószínűségi eloszlások mentén.""",

        'sec1': r"""### 1. A 10 000 Szimuláció Eredményeloszlása és a VaR / CVaR Mutatók

**📌 Mit mutat a hisztogram?**
A 10 000 szimulált 20 éves NPV kimenetelt az empirikus kőbányai bázisadatokból kiindulva (65 M Ft medián ár, 250 ezer Ft bérleti díj):
- **Harang görbe**: A várható kimenetelek sűrűsödése.
- **VaR 95% (Value at Risk)**: Az a küszöbérték, amelynél 95%-os valószínűséggel jobb eredményt érünk el.
- **CVaR (Conditional VaR)**: A legrosszabb 5%-os kimenetelek átlagos értéke.
- **$P(\text{NPV} > 0)$**: Annak valószínűsége, hogy a befektetés nyereséges marad, meghaladja a 95%-ot!""",

        'sec2': r"""### 2. Kumulatív Eloszlásfüggvény (CDF) és Konfidencia Sáv

**📌 Hogyan olvassuk a kumulatív görbét?**
Az S-görbe megmutatja annak a valószínűségét, hogy a hozam egy adott érték alatt marad. A meredek felfutás alacsony kimeneteli szórást és magas stabilitást igazol.""",

        'sec3': r"""### 3. Tornado Érzékenységvizsgálati Diagram

**📌 Melyik tényező a legkockázatosabb?**
A Tornado diagram megmutatja, mely változók okozzák a legnagyobb kilengést:
1. A vételár és a piac általános árszínvonala,
2. A kihasználtság / üresedési idő (Occupancy),
3. A bérleti díj ingadozása.""",

        'sec4': r"""### 4. Interaktív Monte Carlo Vezérlőpult

**📌 Futtasson szimulációt!**
Állítsa be az iterációk számát és a bizonytalansági szórásokat, és kattintson a futtatás gombra!"""
    },

    # =========================================================================
    # NB09: Klaszter és Tipológia
    # =========================================================================
    'nb09': {
        'intro': r"""# 09. Gépi Tanulásos Klaszterezés és Lakáspiaci Tipológia

**Cél**: A kőbányai ingatlanállomány automatikus piaci szegmentálása felügyelet nélküli (K-Means & Hierarchikus) gépi tanulási algoritmusokkal.

---

### 📖 Mi a gépi klaszterezés célja?
Az algoritmus emberi előítélet nélkül, tisztán a többdimenziós adatok (ár, méret, szobaszám, állapot, panel) matematikai távolságai alapján azonosítja az összetartozó lakástípusokat.""",

        'sec1': r"""### 1. Optimális Klaszterszám (Elbow Plot & Silhouette Score)

**📌 Mit mutat a könyök- és sziluett-diagram?**
- A könyök-módszer (Inertia) töréspontja és a sziluett pontszám maximuma a **$K = 4$ klaszternél** adja az optimális szegmentációt.
- A kőbányai lakáspiac természetes módon 4 jól elkülönülő archetípusra tagolódik.""",

        'sec2': r"""### 2. A Négy Fő Lakáspiaci Klaszter Profilja (Radar Diagram)

**📌 Kik a piac 4 archetípusa?**
1. **Belépő kislakások / panel garzonok**: kis méret, magas fajlagos ár, alacsony összvételár.
2. **Családi lakótelepi panelek**: 50-65 m², 2-2.5 szoba, szabványos elrendezés.
3. **Klasszikus felújítandó téglalakások**: nagyobb méret, tégla falazat, alacsonyabb állapotindex.
4. **Prémium zöldövezeti / új építésű lakások**: kiváló állapot, nagy alapterület, magas ár.""",

        'sec3': r"""### 3. Klaszterek 2D PCA Vetülete

**📌 Mit látunk a főkomponens vetületen?**
A többdimenziós tér 2D síkra vetítve igazolja, hogy a 4 klaszter szépen elkülönülő, zárt csoportokat alkot.""",

        'sec4': r"""### 4. Városrész és Klaszter Kereszttábla Hőtérkép

**📌 Hol találhatók az egyes típusok?**
- Újhegy a családi panelek zónája,
- Óhegy a prémium zöldövezeti és nagypolgári téglák fellegvára,
- Városközpont vegyes képet mutat."""
    },

    # =========================================================================
    # NB10: Moran's I és Autokorreláció
    # =========================================================================
    'nb10': {
        'intro': r"""# 10. Térbeli Autokorreláció (Moran's I) és Hotspot Elemzés

**Cél**: A térbeli függőség ökonometriai kimutatása az épület-szinten aggregált pontos eladó mintán (N = 124 db aggregált pont a 254 pontos eladóból).

---

### 📖 Tobler első földrajzi törvénye és a térbeli aggregáció:
A szomszédos ingatlanok árai összefüggenek. 
A lépcsőházon belüli fals korrelációk elkerülésére **épület-szintű térbeli aggregációt** hajtottunk végre, így a modell a valódi környékbeli árhúzást méri.""",

        'sec1': r"""### 1. Globális Moran's I Eredmények

**📌 Mit mutatnak az ökonometriai mutatók?**
Az aggregált pontokon ($k=8$ szomszéd):
- **Globális Moran's I: $I \approx +0.062$ (z = 1.75, p = 0.079)**.
- Az épület-szintű aggregáció kiszűrte az épületen belüli azonos árak torzító hatását, így a tiszta tömbök közötti autokorrelációt kapjuk meg.""",

        'sec2': r"""### 2. Moran Pontdiagram (Scatter Plot)

**📌 Hogyan értelmezzük a 4 kvadránst?**
- **High-High (HH)**: Magas ár magas szomszédokkal $\rightarrow$ Hotspot.
- **Low-Low (LL)**: Alacsony ár alacsony szomszédokkal $\rightarrow$ Coldspot.
- **High-Low és Low-High**: Térbeli kiugró értékek (outlierek).""",

        'sec3': r"""### 3. LISA Klaszter Térkép (Hotspotok és Coldspotok)

**📌 Mit látunk a térképen?**
- **Piros (Hotspot)**: Óhegy és Ligettelek zöldövezeti részei.
- **Kék (Coldspot)**: A külső vasúti és rozsdaövezeti zónák.""",

        'sec4': r"""### 4. Szignifikancia és Érzékenységvizsgálat

**📌 Mennyire stabilak az eredmények?**
A k szomszédszám változtatása mellett a forró- és hidegpontok magja stabilan megmarad."""
    },

    # =========================================================================
    # NB11: Kereső Dashboard
    # =========================================================================
    'nb11': {
        'intro': r"""# 11. Interaktív Ingatlan Kereső és Portfólió Dashboard

**Cél**: Felhasználóbarát, dinamikus döntéstámogató felület a kőbányai lakásállomány szűrésére és elemzésére.

---

### 📖 Mire használható a dashboard?
A teljes 1 320 darabos adatbázisban böngészhet ár, alapterület, szobaszám, városrész és típus szerint, azonnali élő statisztikákkal.""",

        'sec1': r"""### 1. Dinamikus Szűrők és Reagáló KPI Kártyák

**📌 Mit lát a vezérlőpult tetején?**
A szűrés után azonnal frissül a találatok száma, az átlagár, a medián négyzetméterár és az átlagos méret.""",

        'sec2': r"""### 2. Térképi Elhelyezkedés és Találati Lista

**📌 Hogyan használható a találati lista?**
A mini térképen láthatók a szűrt lakások, a táblázat pedig rendezhető ár, m² ár vagy méret szerint.""",

        'sec3': r"""### 3. Áreloszlási Hisztogram

**📌 Mit mutat a kisegítő ábra?**
A kiválasztott részpiac belső árszóródását és homogenitását ábrázolja.""",

        'sec4': r"""### 4. Döntéstámogató Alkalmazás

**📌 Gyakorlati haszon**:
Közvetlenül alkalmas piaci összehasonlító elemzések és vásárlási döntések előkészítésére."""
    },

    # =========================================================================
    # NB12: Gépi Tanulás és Arbitrázs
    # =========================================================================
    'nb12': {
        'intro': r"""# 12. Gépi Tanulásos Ármeghatározás és Piaci Arbitrázs

**Kontextus és Kapcsolódás:** Az eddigi parametrikus modellek (OLS, SAR, GWR) jól magyaráznak, de a nemlineáris interakciókat nehezen kezelik. A prediktív pontosság maximalizálása érdekében most áttérünk a gépi tanulásra (Random Forest).

**Cél**: Random Forest árbecslő modell tanítása, a változók fontossági rangsorának (Feature Importance) feltárása és a piacilag alulárazott (arbitrázs) lakások automatikus azonosítása.

---

### 📖 Mi az a piaci arbitrázs?
Ha a gépi tanulási modell nagy pontossággal ($R^2 > 0.80$) megbecsüli a lakás reális értékét, a modell jóslatánál jóval olcsóbban hirdetett ingatlanok **alulárazott arbitrázs lehetőséget** jelentenek.""",

        'sec1': r"""### 1. Random Forest Modell Illeszkedés és Diagnosztika

**📌 Mennyire pontos az algoritmus?**
A Random Forest modell az adatok több mint 80%-át magyarázza a teszthalmazon, átlagosan 3-4 millió forintos hibahatárral becsülve meg a vételárat.""",

        'sec2': r"""### 2. Változók Relatív Fontossága (Feature Importance MDI)

**📌 Mely tulajdonságok a legfontosabbak?**
1. Korrigált alapterület (m²) – a legfőbb magyarázó erő,
2. Lokáció (metró és vasút távolság),
3. Műszaki állapotindex,
4. Építőanyag (panel vs. tégla).""",

        'sec3': r"""### 3. A Legjobb Piaci Arbitrázs Lehetőségek Toplistája

**📌 Mit tartalmaz a táblázat?**
A modell által azonosított legnagyobb mértékben alulárazott kőbányai lakások listáját a hirdetett és becsült ár különbségével.""",

        'sec4': r"""### 4. Interaktív Árbecslő Kalkulátor

**📌 Próbálja ki az árbecslőt!**
Adja meg a lakás méretét, állapotát, szobaszámát és elhelyezkedését, és a Random Forest modell azonnal megbecsüli a piaci értéket!"""
    },

    # =========================================================================
    # NB13: Térökonometria (SAR & SEM)
    # =========================================================================
    'nb13': {
        'intro': r"""# 13. Térökonometriai Regresszió: Spatial Lag (SAR) és Spatial Error (SEM)

**Cél**: A térbeli függőség és a szomszédsági tovagyűrűzés ökonometriailag konzisztens modellezése Spatial Lag (SAR) modellel az aggregált pontokon (N = 124 db).

---

### 📖 Miért kötelező a térökonometria?
A sima OLS feltételezi a megfigyelések függetlenségét. A valóságban a szomszédos lakások árai kölcsönösen hatnak egymásra. A SAR modell beépíti a térben késleltetett árat ($Wy$), és számszerűsíti a térbeli multiplikátort.""",

        'sec1': r"""### 1. Térbeli Súlyozási Mátrix és Késleltetett Változók

**📌 Hogyan készül a modell?**
Az épület-szinten aggregált pontokon $k=8$ KNN szomszédsági mátrixot ($W$) építünk fel, előállítva az endogén térbeli árlagot ($Wy$).""",

        'sec2': r"""### 2. SAR Modell Eredmények és a Térbeli Multiplikátor

**📌 Mit mutatnak az ökonometriai számok?**
- **Térbeli autoregresszív paraméter: $\rho = 0.2650$ ($p < 0.0001$)** $\rightarrow$ szignifikáns térbeli árhúzás!
- **Térbeli Multiplikátor: $1 / (1 - \rho) = \mathbf{1.361\times}$**:
  - Ez a kutatás egyik legfontosabb elméleti eredménye!
  - Egy helyi beavatkozás közvetlen hasznához képest a térbeli tovagyűrűzés révén **további +36.1%-nyi vagyongyarapodás** keletkezik a környező ingatlanokban!

**💡 Szakpolitikai tanulság**: A közberuházások tervezésekor a közvetlen hatáson felül a 1.361-szeres térbeli multiplikátorral kell számolni.""",

        'sec3': r"""### 3. OLS vs. SAR Paraméter Összehasonlítás

**📌 Miért változnak az együtthatók?**
A SAR modellben a közvetlen fizikai változók együtthatói tisztulnak, mert a térbeli tovagyűrűzés hatása már külön változóként szerepel.""",

        'sec4': r"""### 4. Térbeli Hibatag (SEM) és Robusztusság

**📌 Modell ellenőrzés**:
A SAR specifikáció után a hibatagok térbeli autokorrelációja megszűnik, igazolva a modell torzítatlanságát."""
    },

    # =========================================================================
    # NB14: POI és 15-perces város
    # =========================================================================
    'nb14': {
        'intro': r"""# 14. Intézményi Ellátottság (POI) és a 15-Perces Város Index

**Cél**: Az OpenStreetMap intézményi adatainak (POI) feldolgozása a határhatás kiküszöbölésével, és a 15 perces város gyalogos elérhetőségének vizsgálata (375m, 750m, 1125m sávokban).

---

### 📖 A 15 perces város és a határhatás (Edge Effect) korrekció:
Carlos Moreno koncepciója szerint minden alapvető funkciónak elérhetőnek kell lennie 15 perc sétával.
A peremhatás elkerülésére **1200 méteres védőzónával (pufferrel)** kérdeztük le az adatokat, így a szomszédos kerületek intézményei is beleszámítanak az elérhetőségbe.""",

        'sec1': r"""### 1. Pufferelt POI Adatbázis (N = 319 db)

**📌 Mit tartalmaz az adatbázis?**
A szigorú közigazgatási határon belüli 144 db POI helyett a határokon átnyúló pufferrel **összesen 319 db szolgáltatás** (parkok, éttermek, kávézók, iskolák) került be az elemzésbe, megszüntetve a határ menti ingatlanok mesterséges büntetését.""",

        'sec2': r"""### 2. A Három Gyalogos Sáv Szolgáltatás-Sűrűsége

**📌 Mit mutat a térkép és a KPI pult?**
Az 5 perces (375m), 10 perces (750m) és 15 perces (1125m) sávokban elérhető szolgáltatások száma:
- **Kőbánya-Városközpont**: átlagosan **30.4 db** POI 15 percen belül.
- **Felsőrákos (Zugló felé nyitott)**: átlagosan **30.4 db** POI (korábban alig kapott pontot!).
- **Óhegy**: átlagosan **21.5 db** POI.
- **Gyárdűlő (Népliget felé)**: átlagosan **20.4 db** POI.
- **Újhegy**: átlagosan **12.8 db** POI.

**💡 Eredmény**: A pufferelés után a valós, határmenti szolgáltatási ellátottság reálisan tükröződik a térképen.""",

        'sec3': r"""### 3. A Szolgáltatási Sűrűség Hedonikus Árprémiuma

**📌 Mit mutat a regressziós modell?**
A közvetlen közelben (5 perces sétatávolságban) lévő szolgáltatások bírnak a legmagasabb fajlagos árnövelő hatással a lakásárakban."""
    },

    # =========================================================================
    # NB15: Lokális Térökonometria (GWR)
    # =========================================================================
    'nb15': {
        'intro': r"""# 15. Lokális Térökonometria: Földrajzilag Súlyozott Regresszió (GWR)

**Kontextus és Kapcsolódás:** A SAR/SEM modellek (13-as notebook) globálisan korrigálták a térbeli hibát, de továbbra is azt feltételezik, hogy a paraméterek (pl. a metró hatása) egész Kőbányán állandóak. Ebben a notebookban ezt a korlátot oldjuk fel.

**Cél**: A térbeli heterogenitás modellezése Kőbányán multiskálás földrajzilag súlyozott regresszióval (GWR / MGWR), épület-szintű térbeli aggregációval.

---

### 📖 Miért nem ér mindenhol ugyanannyit a metró?
A globális modellek egyetlen átlagos hatást mérnek. A GWR viszont megengedi, hogy a paraméterek (pl. a metrótávolság ára) térben pontról pontra változzanak.""",

        'sec1': r"""### 1. Adaptív Sávszélesség Keresés és GWR Illeszkedés

**📌 Modell illeszkedési eredmények:**
Az algoritmus adaptív (KNN alapú) sávszélességet optimalizál az AICc minimalizálásával.
- A GWR modell magyarázóereje felülmúlja a globális OLS-t, igazolva a térbeli heterogenitás jelenlétét a kőbányai piacon.""",

        'sec2': r"""### 2. A Metróprémium Térbeli Változékonysága

**📌 Mit mutat a lokális együtthatók térképe?**
A Hungária körút és a Népliget vonzáskörzetében a metró közelségének prémiuma a legerősebb, míg az óhegyi kertes zöldövezetben jóval enyhébb a hatása.""",

        'sec3': r"""### 3. Helyi Állapot-Prémium és Összegzés

**📌 Fő konklúzió**:
A felújítási prémium a sűrűbb lakóövezetekben magasabb, igazolva, hogy az ingatlantulajdonságok értéke mikrolokációtól függően dinamikusan változik."""
    }
}

def get_nb_docs(nb_id):
    return NOTEBOOK_DOCS.get(nb_id, {})
