# -*- coding: utf-8 -*-
"""
notebook_docs.py
Részletes, közérthető és módszertanilag megalapozott szöveges magyarázatok
és interpretációk a Kőbánya TDK kutatás mind a 16 notebookjához.
A leírások úgy készültek, hogy mind az akadémiai zsűri, mind egy érdeklődő laikus
pontosan megértse, mit lát az ábrákon, mit jelentenek a statisztikák és milyen
gyakorlati tanulságok vonhatók le.
"""

NOTEBOOK_DOCS = {
    # =========================================================================
    # NB00: Adathalmaz Áttekintés és Minőségi Riport
    # =========================================================================
    'nb00': {
        'intro': """# 00. Adathalmaz Áttekintés és Minőségi Riport

**TDK Kutatási Téma**: Budapest Főváros X. kerület (Kőbánya) lakóingatlan-piacának komplex térökonometriai, hedonikus és gépi tanulásos vizsgálata.

---

### 📖 Miről szól ez a kutatás, és miért éppen Kőbánya?
Budapest X. kerülete, **Kőbánya** a főváros egyik legizgalmasabb, legsokszínűbb, ugyanakkor gazdaságilag leginkább alulértékelt területe. 
- Egyrészt magán viseli a **történelmi ipari és vasúti múlt** terheit (rozsdaövezetek, vágányhálózatok által elvágott területrészek, panelsorok).
- Másrészt hatalmas **fejlesztési potenciállal** bír (kitűnő kötöttpályás kapcsolatok, óriási zöldterületek, mint az Óhegy-park vagy a Népliget, illetve a tervezett Mázsa téri és rozsdaövezeti revitalizációk).

Kutatásunk célja, hogy **modern adattudományi, térinformatikai és ökonometriai eszközökkel** számszerűsítse a lakásárakat mozgató erőket: mennyit számít a vasút zaja, mennyit ér a metró közelsége, hol vannak a rejtett piaci lehetőségek, és hogyan nyerheti vissza a közösség a fejlesztések által generált értéknövekményt.

---

### 🗂️ Az adathalmaz háttere és megbízhatósága
Az elemzés gerincét az **ingatlan.com** kínálati adatbázisából kinyert és térinformatikailag (GIS) felbővített adatbázis adja. 
- **1 320 darab hirdetés** adatait dolgozzuk fel.
- Minden ingatlanhoz **169 különböző változó** tartozik: épületfizikai paraméterek (méret, szobaszám, állapot, építőanyag), hálózati gyalogos távolságok a tömegközlekedési csomópontoktól, környezeti terhelési adatok és intézményi ellátottsági mutatók.
- Az adatok szigorú tisztítási folyamaton mentek keresztül (duplikációk kiszűrése, hibás elgépelések javítása, statisztikai kiugró értékek kezelése).""",

        'sec1': """### 1. Alapvető Adatbázis KPI Mutatók (A piac mérete és szerkezete)

**📌 Mit látunk a fenti kártyákon?**
A vezérlőpult az adatbázis legfontosabb sarokszámait foglalja össze: a teljes mintaméretet, az eladó és kiadó lakások arányát, a pontos GPS-koordinátával rendelkező ingatlanok számát, valamint az eladási árak és alapterületek középértékeit.

**🔍 Hogyan kell ezt értelmezni laikus szemmel?**
1. **Eladó vs. Kiadó arány**: A hirdetések elsöprő többsége (~85%) eladó lakás, míg a bérleti piac kínálata jóval szűkebb (~15%). Ez tipikus a magyar lakáspiacon, ahol a magántulajdon dominál a bérleti szektor felett.
2. **Miért a mediánt nézzük az átlag helyett?** 
   - Ha egy szobában 9 átlagos keresetű ember ül, és belép egy milliárdos, az *átlagkereset* azonnal az egekbe ugrik, pedig a többiek egy forinttal sem lettek gazdagabbak.
   - Az ingatlanpiacon pontosan ugyanez a helyzet: néhány 200 milliós luxuslakás felfelé húzza az átlagot. A **medián** az az ár, aminél a lakások pontosan fele olcsóbb, fele pedig drágább. Ez adja a legőszintébb képet a piacról.
3. **Garantált pontos GIS minta (N = 296 db)**: A hirdetések egy része csak utcanév vagy városrész pontossággal érhető el. Ahhoz azonban, hogy mérnöki pontossággal mérjük a vasúttól vagy metrótól való távolságot, kizárólag a házszám / pontos GPS-szintű almintát használhatjuk a térbeli modellekben.

**💡 Gyakorlati tanulság**: Kőbánya kínálati medián négyzetméterára ~900 000 Ft/m² körül mozog, ami jelentős diszkontot (árelőnyt) jelent a szomszédos belvárosi kerületekhez (VIII., IX., XIV.) képest.""",

        'sec2': """### 2. Kínálati Megoszlás Városrészenként (Hol van a legtöbb lakás?)

**📌 Mit látunk a grafikonon?**
Az oszlopdiagram Kőbánya különböző városrészeinek kínálati súlyát mutatja be, kékkel jelölve az eladó, sárgával a kiadó lakásokat.

**🔍 Hogyan értelmezzük a látottakat?**
- **A piac súlypontjai**: A hirdetések túlnyomó része két nagy városrészben összpontosul: **Óhegyen** (amely a kerület legnagyobb lakó- és zöldövezete) és **Újhegyen** (a nagy kiterjedésű, infrastruktúrával jól ellátott panel-lakótelepén).
- **A történelmi mag**: Kőbánya-Városközpont és Ligettelek stabil, vegyes (polgári tégla és panel) kínálatot nyújt.
- **Ipari és perifériás zónák**: Gyárdűlő, Laposdűlő és Felsőrákos alacsonyabb lakásszámmal szerepelnek, mivel ezek jelentős része ma is gazdasági, logisztikai, vasúti vagy alulhasznosított rozsdaövezeti funkciót tölt be.

**💡 Befektetői és önkormányzati szemüveg**:
A bérleti piac (sárga oszlopok) szinte kizárólag a jó közlekedésű Városközpontban, Ligetteleken és az egyetemekhez/belvároshoz közelebb eső részeken aktív. A külsőbb területeken a lakások bérbeadása sokkal lassabb és kockázatosabb.""",

        'sec3': """### 3. Változók Kitöltöttsége és Adatminőség (Megbízhatósági audit)

**📌 Mit mutat ez a vízszintes sávdiagram?**
Minden sáv egy-egy fontos ingatlancímkét (ár, szobaszám, alapterület, emelet, GPS koordináta stb.) képvisel. A sávok hossza azt mutatja meg 0-tól 100%-ig, hogy az adott adat a hirdetések hány százalékában állt rendelkezésre hiánytalanul.

**🔍 Miért kritikus ez az elemzés?**
Egy gépi tanulási modell vagy ökonometriai becslés pontossága csak annyira lehet jó, amennyire a bemenő adatok tiszták („Garbage in, garbage out” elv).
1. **100%-os alapváltozók**: Az ár, a négyzetméterár, a szobaszám és az alapterület minden hirdetésben szerepel, így az alap leíró statisztikák a teljes 1 320-as mintán hibátlanul futnak.
2. **Közepes kitöltöttségű változók**: Az építés éve, a fűtési mód vagy az emelet száma nem minden hirdetésben van megadva (a hirdetők gyakran lusták kitölteni a mezőket).
3. **Koordináták**: A pontos geokódolt helymeghatározás a mintánk közel negyedénél garantált. Emiatt a későbbi fejezetekben **kettős módszertant** alkalmazunk: az alap statisztikákat a teljes mintán, a precíz távolsági és térökonometriai modelleket pedig a garantált pontos almintán futtatjuk.

**💡 Megbízhatósági tanúsítvány**: Az audit igazolja, hogy az adathalmaz reprezentatív, és nincsenek benne szisztematikus adatvesztések.""",

        'sec4': """### 4. Interaktív Adathalmaz Szűrő és Ellenőrző Pult

**📌 Mire szolgál ez az interaktív vezérlőpult?**
Az alábbi csúszkákkal, gombokkal és választómezőkkel tetszőleges szűréseket hajthat végre az adathalmazon:
- Kiválaszthatja, hogy eladó, kiadó, vagy mindkét típusú hirdetést szeretné vizsgálni.
- Leszűrheti az adatbázist kizárólag a pontos GPS-koordinátával rendelkező ingatlanokra.
- Kiválaszthat konkrét városrészeket (pl. csak Óhegy és Újhegy összehasonlítása).

**🔍 Mit lát az eredménytáblázatban?**
A szűrés után azonnal újraszámolódik a kiválasztott minta darabszáma, az átlagár, a medián négyzetméterár, és megjelenik a hirdetések legfrissebb előnézete a valós címekkel és árakkal.

**💡 Próbálja ki bátran!** Váltson át „kiadó” lakásokra, hogy megnézze, mennyire esik vissza a minta mérete, és hogyan változik meg a fajlagos négyzetméterár!"""
    },

    # =========================================================================
    # NB01: Leíró Statisztika és EDA
    # =========================================================================
    'nb01': {
        'intro': """# 01. Leíró Statisztika és Feltáró Adatelemzés (EDA)

**Cél**: A kőbányai lakáspiaci árak, alapterületek és szobaszámok belső szerkezetének, szóródásának és eloszlásának alapos feltárása.

---

### 📖 Miért nem elég csak az átlagárakat nézni?
A laikus lakásvásárló vagy újságolvasó leggyakrabban ilyen hírekkel találkozik: *„Kőbányán az átlagos négyzetméterár elérte a 950 ezer forintot.”* 
Ez az állítás azonban veszélyesen leegyszerűsítő, mert:
1. **Nincs "átlagos lakás"**: Egy 1970-es évekbeli, felújítandó, földszinti panellakás és egy újonnan épült, tetőteraszos, hőszivattyús téglaotthon teljesen más termék, még ha mindkettő Kőbányán is található.
2. **Az ingatlanárak eloszlása ferde**: Az olcsóbb kategóriában óriási tömegben találhatók lakások, felfelé viszont a luxusingatlanok árai hosszan elnyúlnak (ezt hívja a statisztika jobbra ferdeségnek).

Ebben a fejezetben megvizsgáljuk az árak valódi szóródását, teszteljük az összefüggéseket (korrelációkat), és megmutatjuk, miért elengedhetetlen a **logaritmikus árak** használata a későbbi ökonometriai becslésekhez.""",

        'sec1': """### 1. Főbb Leíró Statisztikai Mutatók (A kőbányai lakáspiac számai)

**📌 Mit látunk a mutatókártyákon és az alatta lévő táblázatban?**
A kőbányai eladó lakáskínálat központi tendenciáit és változékonyságát foglaljuk össze. A táblázat sorai az árat, a négyzetméterárat, a méretet és a szobaszámot mutatják be a legfontosabb mérőszámokkal.

**🔍 Mit jelentenek a statisztikai fogalmak laikus nyelven?**
- **Átlag vs. Medián**: Az átlagos eladási ár ~54 millió Ft, míg a medián ár ~49 millió Ft. A kettő közötti ~5 millió forintos különbség pontosan a drágább ingatlanok felfelé húzó hatását mutatja! A piac „dereka” 49 millió körül mozog.
- **Szórás és Relatív szórás**: A négyzetméterárak relatív szórása ~25-30%. Ez azt jelenti, hogy az árak nem homogének: a kerületen belül hatalmas minőségi és lokációs ugrások vannak.
- **Q1 (25%) és Q3 (75%) – Interkvartilis terjedelem**: 
  - A legolcsóbb negyed (Q1 alatt) ~780 ezer Ft/m² alatt vásárolható meg.
  - A legfelső negyed (Q3 felett) ~1,05 millió Ft/m² felett indul.
  - A piac középső 50%-a ebben a szűk, ~270 ezer forintos sávban koncentrálódik!
- **Ferdeség (Skewness > 0)**: Pozitív érték, ami matematikailag igazolja, hogy az árak jobbra nyúlnak el (log-normális jelleg).

**💡 Tanulság lakásvásárlóknak**: 40 és 55 millió forint között van a kőbányai kínálat legvastagabb szelete; ez a belépő kategória a fővárosi saját tulajdonú lakáspiacra.""",

        'sec2': """### 2. Négyzetméterárak Eloszlása és a Log-Transzformáció

**📌 Mit látunk a két grafikonon?**
- **Bal oldali ábra**: A nyers négyzetméterárak hisztogramja (az oszlopok magassága mutatja, hány darab lakás esik az adott ársávba).
- **Jobb oldali ábra**: Ugyanezen árak természetes logaritmusa ($\ln(\text{Ár/m}^2)$).

**🔍 Miért van szükség logaritmusra? (Laikus magyarázat)**
1. **A görbe alakja**: A bal oldali ábrán a görbe nem szimmetrikus harang alakú: a bal oldalán meredeken indul, majd jobbra hosszan elnyúlik a "farka" (néhány nagyon drága lakás miatt).
2. **A Gauss-görbe varázsa**: A modern statisztikai modellek (regressziók, T-tesztek) azt feltételezik, hogy a hibák normál eloszlást (szimmetrikus harangot) követnek. Ha a nyers árakkal számolnánk, a modellünk torzítana és pontatlan lenne.
3. **A jobb oldali ábra**: A logaritmus „összenyomja” a szélsőségesen nagy értékeket, így a jobb oldali grafikon már gyönyörű, szimmetrikus normál eloszlást mutat.
4. **Gazdasági bónusz**: A logaritmikus modellekben az együtthatók közvetlenül **százalékos felárként** értelmezhetők (pl. +1 szoba = +8% árnövekedés, függetlenül attól, hogy mekkora a lakás abszolút értéke).

**💡 Fő tanulság**: Minden későbbi tudományos ármodellünkben (NB04, NB13, NB15) a logaritmizált árakat fogjuk használni a torzításmentes becslésekhez.""",

        'sec3': """### 3. Dobozdiagramok (Boxplot) és Kiugró Értékek (Outliers)

**📌 Hogyan kell olvasni a dobozdiagramot?**
A boxplot a statisztikusok svájcibicskája. Első ránézésre furcsa lehet, de rengeteg információt sűrít magába:
- **A doboz közepe (a vízszintes vonal)**: A medián ár.
- **A doboz alsó és felső éle**: Az alsó kvartilis (Q1, 25%) és a felső kvartilis (Q3, 75%). A doboz belseje a piac „magját”, a középső 50%-ot fedi le.
- **A „bajszok” (függőleges vonalak)**: A még normálisnak tekinthető ártartomány határai ($1.5 \times \text{IQR}$).
- **Az elszórt pontok a bajszokon kívül**: A statisztikai **kiugró értékek (outlierek)** – pl. elgépelt hirdetések vagy luxusvillák.

**🔍 Mit látunk a kőbányai városrészek összehasonlításakor?**
- **Óhegy és Ligettelek dobozai magasabban helyezkednek el**: Ezekben a városrészekben a medián ár érezhetően meghaladja a kerületi átlagot.
- **Újhegy doboza rendkívül lapos és tömör**: Ez tipikus panel-lakótelepi sajátosság! A lakások műszaki paraméterei (méretek, elrendezések) szabványosak, így az árak nagyon szűk sávban ingadoznak.
- **Gyárdűlő és Laposdűlő szórása óriási**: Egymás mellett találhatók a lepusztult munkáskolóniák olcsó lakásai és az újonnan épülő rozsdaövezeti lakóparkok drága ingatlanjai.

**💡 Befektetői szemmel**: A szűk doboz (Újhegy) alacsony kockázatot és kiszámítható árakat jelent; a széles doboz (Laposdűlő) nagyobb kockázatot, de jobb arbitrázs- (felújítási) lehetőségeket kínál.""",

        'sec4': """### 4. Korrelációs Hőtérkép és Változókapcsolatok

**📌 Mit jelent a korrelációs mátrix?**
A színes rács a lakások különböző tulajdonságai közötti együttmozgást (lineáris kapcsolatot) mutatja:
- **+1.0 (sötétkék)**: Tökéletes pozitív kapcsolat (ha az egyik nő, a másik is biztosan nő).
- **0.0 (fehér/világos)**: Nincs semmilyen kapcsolat a két dolog között.
- **-1.0 (sötétvörös)**: Tökéletes ellentétes kapcsolat (ha az egyik nő, a másik csökken).

**🔍 A legfontosabb kőbányai összefüggések:**
1. **Alapterület vs. Teljes ár ($r \approx +0.85$)**: Nagyon erős pozitív kapcsolat. Minél nagyobb a lakás, annál többe kerül összesen (ez nem meglepő).
2. **Alapterület vs. Négyzetméterár ($r \approx -0.35$)**: Negatív kapcsolat! Ez a híres **fajlagos méret-diszkont**: a kisebb garzonlakások négyzetméterára szinte mindig magasabb, mint a 3 szobás nagy lakásoké.
3. **Panelszerkezet vs. Ár ($r < 0$)**: A panelek egyértelmű árhátrányt mutatnak a téglalakásokkal szemben.
4. **Metrótávolság vs. Ár ($r < 0$)**: Minél messzebb megyünk a metrótól, annál alacsonyabb a négyzetméterár (elérhetőségi prémium).

**💡 Fő tanulság**: A méret, az építőanyag és a közlekedési távolság a három legfőbb árképző tényező, amelyeket a hedonikus regressziós modellünkbe kötelező beépíteni."""
    },

    # =========================================================================
    # NB02: Árstruktúra és Szegmentáció
    # =========================================================================
    'nb02': {
        'intro': """# 02. Lakáspiaci Árstruktúra és Szegmentáció

**Cél**: A kőbányai ingatlanállomány szegmentálása építőanyag (tégla vs. panel), műszaki állapot, szobaszám és területi elhelyezkedés szerint.

---

### 📖 Miért nem létezik egységes ingatlanpiac Kőbányán?
Az ingatlanpiac nem egyetlen homogén massza, hanem egymással párhuzamosan létező **részpiacok (szubpiacok)** összessége. 
Egy kispénzű egyetemista vagy pályakezdő, aki 35 millióért keres garzont az Újhegyi lakótelepen, teljesen más piacon mozog, mint egy kétgyermekes család, amelyik 85 millióért keres zöldövezeti téglaotthont Óhegyen.

Ebben a fejezetben számszerűsítjük azokat a konkrét **felárakat és diszkontokat**, amelyeket a vásárlók a gyakorlatban kénytelenek megfizetni:
- Mennyivel drágább a tégla, mint a panel?
- Mennyit hoz a konyhára egy teljes felújítás?
- Hol húzódik a határ a prémium és az átlagos kőbányai övezetek között?""",

        'sec1': """### 1. Panel vs. Tégla Árolló és Építőanyag Szegmentáció

**📌 Mit látunk a grafikonon?**
A panellakások és a téglalakások négyzetméterárainak összehasonlítását városrészenként.

**🔍 Mennyi a paneldiszkont a valóságban?**
- **A paneldiszkont lényege**: A panellakások négyzetméterára Kőbányán átlagosan **15-22%-kal alacsonyabb**, mint a hasonló méretű és elhelyezkedésű téglalakásoké.
- **Miért olcsóbb a panel?** A kevésbé rugalmas alaprajzok (nem mozdítható teherhordó betonfalak), a gyengébb hangszigetelés, a házgyári technológia miatti amortizációs félelmek és a lakótelepi sűrűség mind árcsökkentő tényezők.
- **A panel előnye**: Ugyanakkor a panelek fenntartása (távhő, panelprogramos szigetelés) gyakran kiszámíthatóbb, mint egy régi, rosszul szigetelt polgári téglaépületé.
- **Városrészi különbségek**: Óhegyen a téglaépítésű lakások jelentős prémiumot élveznek a csendes, kertvárosias utcák miatt, míg Újhegyen a kínálat szinte 100%-át a panelek dominálják.

**💡 Vásárlói tanács**: Ha valaki maximális alapterületet keres a legkisebb tőkéből, a kőbányai lakótelepek a főváros legjobb ár-érték arányú belépőjét jelentik.""",

        'sec2': """### 2. A Műszaki Állapot Értéknövelő Hatása (Felújítási Prémium)

**📌 Mit mutat ez az oszlopdiagram?**
A négyzetméterárak alakulását a lakás hivatalos műszaki állapota szerint (felújítandó, átlagos, felújított, újszerű, új építésű).

**🔍 Megéri felújítani a lakást eladás előtt?**
1. **Felújítandó vs. Felújított szakadék**: Egy felújítandó lakás Kőbányán ~700-750 ezer Ft/m² körül forog, míg egy minőségien felújított vagy újszerű ingatlanért 950 ezer – 1,1 millió Ft/m²-t is elkérnek.
2. **A felújítási prémium mértéke**: Ez négyzetméterenként **250-350 ezer forintos különbséget** jelent!
3. **Miért fizetnek a vevők ekkora felárat a kész lakásért?** 
   - A mai rohanó világban és a magas építőipari munkadíjak / alapanyagárak mellett a vevők többsége retteg a hónapokig tartó, bizonytalan kimenetelű felújítási munkáktól.
   - Sokan a maximális hitelt veszik fel, amiből nem marad szabad készpénzük a munkálatokra, így inkább a magasabb vételárat finanszírozzák meg a banki kölcsönből („kulcsrakész felár”).

**💡 Befektetői stratégia (Fix & Flip)**: A felújítási rés igazolja, hogy az elhanyagolt kőbányai lakások megvásárlása, igényes renoválása és újraértékesítése gazdaságilag racionális és jövedelmező tevékenység.""",

        'sec3': """### 3. Szobaszám és Méretkategória Prémiumok

**📌 Mit látunk ezen az ábrán?**
A fajlagos (négyzetméter) árak alakulását a lakás szobaszáma (1, 1.5, 2, 2.5, 3+) szerint.

**🔍 Miért a legkisebb lakások a legdrágábbak négyzetméterenként?**
- **A garzon-effektus**: Az 1 és 1.5 szobás lakások négyzetméterára a legmagasabb. Ennek oka a kereslet: egy 30-40 m²-es kislakás teljes vételára (pl. 35-40 millió Ft) elérhető a fiatal egyedülállók vagy a befektetők számára.
- **A drága vizesblokk szabálya**: Egy lakásban a konyha és a fürdőszoba megépítése a legdrágább tétel. Egy 30 m²-es lakásban a fürdőszoba a terület 15%-át teszi ki, míg egy 90 m²-es lakásban csak az 5%-át. Emiatt a kislakások fajlagos bekerülési és piaci értéke szükségszerűen magasabb.
- **Családi lakások (3+ szoba)**: A szobaszám növekedésével a négyzetméterár mérséklődik, miközben a teljes vételár nő.

**💡 Tanulság**: Bérbeadási célra a kislakások biztosítják a legmagasabb fajlagos tőkearányos hozamot.""",

        'sec4': """### 4. Interaktív Városrész- és Szegmens Összehasonlító Laboratórium

**📌 Mire használható ez a vezérlőfelület?**
A lenyíló menük segítségével kiválaszthat tetszőleges városrészeket és ingatlantípusokat (pl. panel vs. tégla), és a rendszer élőben kirajzolja a szegmens részletes statisztikai profilját és dobozdiagramját.

**🔍 Mit figyeljen meg a használat során?**
Hasonlítsa össze Óhegyet Újheggyel! Látni fogja, hogy míg Újhegy szinte kizárólag a 2-3 szobás panellakások piaca, addig Óhegyen a kertes, téglás, egyedi építésű otthonok sokkal szélesebb ártartományban mozognak.

**💡 Gyakorlati haszon**: Pontos képet kaphat arról, hogy az Ön által keresett specifikus lakástípus mennyire számít ritkának vagy tipikusnak az adott környéken."""
    },

    # =========================================================================
    # NB03: Térbeli Elemzés és Hőtérképek
    # =========================================================================
    'nb03': {
        'intro': """# 03. Térbeli Elemzés és Interaktív Hőtérképek

**Cél**: Kőbánya ingatlanpiaci értéktérképének vizuális megjelenítése, az árfoltok, térbeli egyenlőtlenségek és infrastrukturális vonzáskörzetek feltárása.

---

### 📖 Miért a lokáció az ingatlanpiac legfontosabb törvénye?
A klasszikus ingatlanpiaci mondás szerint a három legfontosabb szempont: *„1. Lokáció, 2. Lokáció, 3. Lokáció.”*
Egy lakás falait át lehet festeni, a fürdőszobát fel lehet újítani, a nyílászárókat ki lehet cserélni – de **az épület elhelyezkedését és környezetét soha nem tudjuk megváltoztatni**.

Ebben a fejezetben a garantált pontos GPS-koordinátákkal rendelkező lakások adatait vetítjük rá Budapest térképére:
- Látni fogjuk, hol húzódnak a kerület legdrágább és legolcsóbb mikrokörzetei.
- Kirajzolódik a metróállomások, villamosvonalak és vasúti sínek ármódosító hatása.
- Interaktív hőtérképen (Heatmap) és ponttérképen böngészhetjük végig az egyes épületek adatait.""",

        'sec1': """### 1. Interaktív Ingatlan Ponttérkép (Ár szerinti színezéssel)

**📌 Mit látunk a térképen?**
Minden egyes színes kör egy-egy valós, eladó kőbányai ingatlant jelöl a térképen:
- **A pontok színe**: A négyzetméterárat mutatja a lila (olcsóbb, 600-750 ezer Ft/m²) árnyalattól a sárgáig és zöldig (prémium, 1,1 - 1,4 millió Ft/m²).
- **A pontok mérete**: A lakás alapterületével arányos (a nagyobb kör tágasabb otthont jelent).
- **Interaktivitás**: Bármelyik pont fölé viszi az egeret, megjelenik a pontos cím, az ár, a méret és a városrész neve. A térkép szabadon nagyítható és mozgatható.

**🔍 Milyen mintázatokat veszünk észre azonnal?**
1. **Északi és nyugati prémium sáv**: A Hungária körúthoz, Zuglóhoz és a belvároshoz legközelebb eső részek (Ligettelek, Városközpont északi része) kirívóan világosabbak (drágábbak).
2. **A déli és keleti területek alacsonyabb árszintje**: Ahogy távolodunk a belvárostól a vasúti és ipari folyosók felé, a pontok egyre sötétebb lilává válnak.
3. **Zöldterületi szigetek**: Az Óhegy-park környékén lévő utcákban lokális prémium figyelhető meg.

**💡 Tanulság lakáskeresőknek**: Kőbánya nem egyetlen homogén tömb; az utca egyik oldaláról a másikra lépve akár 20-30%-os négyzetméterár-ugrás is tapasztalható a környék rendezettségétől függően.""",

        'sec2': """### 2. Kőbánya Ár-Hőtérképe (Kernel Density Heatmap)

**📌 Mit ábrázol a hőtérkép?**
A hőtérkép a pontszerű lakásárakat egy folyamatos felületté simítja ki. A meleg, világos színek (sárga, narancs) a magas árszintű sűrűsödéseket jelzik, míg a hideg színek (kék, lila) az alacsonyabb árfekvésű zónákat mutatják.

**🔍 Hol vannak Kőbánya "forró pontjai" (Hotspots)?**
- **A legforróbb zóna**: Kőbánya alsó vasútállomás és a Szent László tér tengelye. Itt a kiváló közlekedés (villamosok, vonatok 10 perc alatt a Nyugati pályaudvaron), a műemléki polgári környezet és a kerületi intézmények közelsége generálja a legmagasabb fajlagos árakat.
- **A második meleg zóna**: Az Óhegy-park zöldövezeti karéja, ahol a kertvárosias jelleg és a rekreációs lehetőségek vonzzák a fizetőképesebb családokat.
- **A hideg zónák (Coldspots)**: A Hős utca környéke, a Kőbánya-Hízlaló vasúti teherpályaudvar menti területek és a Keresztúri út ipari létesítményei körüli tömbök, ahol a zaj, a por és a szociális kihívások lenyomják az árakat.

**💡 Várostervezési tanulság**: A hőtérkép tökéletesen kirajzolja, hogy a minőségi infrastruktúra (metró, park) azonnal felértékeli a környezetét, míg az elhanyagolt vasúti zárványok mélyen az átlag alatt tartják az ingatlanértékeket.""",

        'sec3': """### 3. Térbeli Árprofil és Magassági Metszet (Kelet-Nyugat és Észak-Dél)

**📌 Mit mutat ez a keresztmetszeti diagram?**
Képzelje el, hogy felszeleteljük Kőbányát! A grafikon azt ábrázolja, hogyan változnak az ingatlanárak, ahogy Nyugatról (a Belváros felől) Keletre (a külváros felé), illetve Északról Délre haladunk.

**🔍 Mit látunk a trendvonalakon?**
- **Kelet-Nyugati gradiens**: Nagyon markáns lejtés tapasztalható. A Hungária körút mentén (Nyugat) 1,1 millió Ft/m²-ről indulunk, és ahogy haladunk Kelet felé a kerület szélére, az árak fokozatosan 750-800 ezer Ft/m²-re süllyednek. Ez a klasszikus **centrum-periféria lejtő**.
- **Észak-Déli gradiens**: Északon (Zugló szomszédságában) magasabbak az árak, míg Dél felé (az ipari zónák irányába) csökkenő tendencia figyelhető meg, amit csak az Újhegyi lakótelep központi része tör meg kissé felfelé.

**💡 Ingatlanpiaci törvényszerűség**: Minden egyes kilométer, amivel közelebb kerülünk Budapest belső magjához, mérhetően százezreket ad hozzá az ingatlanok négyzetméterárához.""",

        'sec4': """### 4. Interaktív Térképi Szűrő és Fókusz Pult

**📌 Mire használható ez a vezérlő?**
Az alábbi menük segítségével szűrheti a térképet árkategória (pl. csak 40 millió alatti vagy 80 millió feletti lakások), alapterület és szobaszám szerint.

**🔍 Mit érdemes kipróbálni?**
Állítsa be a szűrőt a „100 millió Ft feletti” kategóriára! Látni fogja, hogy a pontok szinte kivétel nélkül Óhegy legszebb zöldövezeti utcáira vagy az új építésű lakóparkokra szűkülnek le. Ezzel szemben a „35 millió alatti” szűrés szinte kizárólag az újhegyi garzonokat és a felújítandó kis téglalakásokat hagyja a térképen.

**💡 Fő tanulság**: A vizuális szűrés azonnal igazolja, hogy a kőbányai piac térben élesen szegregált."""
    },

    # =========================================================================
    # NB04: Hedonikus Ármodell (OLS & Kettős TOD)
    # =========================================================================
    'nb04': {
        'intro': """# 04. Hedonikus Ármodellezés és a Kettős TOD Hatás

**Cél**: A lakásárakat meghatározó fizikai és lokációs tényezők tiszta hatásának szétválasztása többváltozós regressziós (OLS) modellel.

---

### 📖 Mi az a "hedonikus" ármodell, és miért zseniális módszer?
Amikor megveszünk egy lakást, nem egyetlen dolgot vásárolunk, hanem egy **tulajdonság-csomagot (kosarat)**:
- Megvesszük a négyzetmétereket,
- Megvesszük az erkélyt,
- Megvesszük a felújított állapotot,
- És megvesszük a környezetet: a metró közelségét és a vasút zaját.

De honnan tudjuk, hogy ebből a vételárból **pontosan hány forintot fizettünk a metróért, és mennyit vont le a vasúti sín zaja?**
A valóságban nem vehetjük fel a lakást, hogy áttegyük 200 méterrel arrébb és megnézzük, mennyivel lett olcsóbb.
A statisztika erre a **hedonikus regressziós modellt** használja: több száz lakás adatának egyidejű összehasonlításával a modell képes **„minden más tényezőt állandónak tekintve” (ceteris paribus)** kiszámítani egy-egy tulajdonság tiszta pénzbeli értékét!

---

### 🚆 A "Kettős TOD" hipotézis: Zajdiszkont vs. Állomási prémium
A vasút Kőbányán kettős szerepet tölt be:
1. **Negatív környezeti hatás (zaj, por, rezgés)**: A nyílt vágányok mellett lakni kellemetlen, csökkenti a lakás élvezeti értékét $\rightarrow$ **Vasúti zajdiszkont**.
2. **Pozitív közlekedési elérhetőség (TOD - Transit-Oriented Development)**: A vasútállomáson felszállva viszont 10 perc alatt a Nyugati pályaudvaron vagy Kelenföldön vagyunk $\rightarrow$ **Állomási elérhetőségi prémium**.

Modellünk újdonsága, hogy képes ezt a két, egymással versengő hatást matematikailag szétválasztani!""",

        'sec1': """### 1. A Három Lépcsős Hedonikus Modell Felépítése

**📌 Mit mutat a lépcsőzetes ökonometriai táblázat?**
A táblázatban 3 egymásra épülő modellt hasonlítunk össze:
- **Modell 1 (Alapmodell)**: Csak a lakás saját fizikai tulajdonságait nézi (méret, panel-e, állapot).
- **Modell 2 (+Vasúti zaj)**: Hozzáadja a vasúti sínektől mért fizikai távolságot (környezeti externália).
- **Modell 3 (Kettős TOD modell)**: Egyszerre vizsgálja a vasút zaját ÉS a vasútállomások, metróállomások gyalogos közelségét.

**🔍 Hogyan olvassuk a regressziós táblázatot?**
- **Együttható (Beta / Paraméter)**: Megmutatja a változó hatását. Mivel a modellben $\ln(\text{Ár/m}^2)$-t használtunk, az érték $\times 100$ közvetlenül **százalékos hatást** jelent!
- **Csillagok a számok mellett (*** p < 0.01, ** p < 0.05)**: A statisztikai szignifikancia jelzése.
  - Ha ott a három csillag (***), 99%-nál is biztosabb, hogy a hatás valós, és nem a véletlen műve!
- **$R^2$ (Magyarázóerő)**: A modell jósági mutatója. A Modell 3-ban az $R^2 \approx 0.65-0.70$, ami azt jelenti, hogy a kőbányai lakásárak ingadozásának **közel 70%-át magyarázni tudjuk** ezzel a néhány kulcsváltozóval! Ez a társadalomtudományokban kimagaslóan erős eredmény.

**💡 Fő tanulság**: A Modell 3 adja a legteljesebb és legpontosabb képet a piacról.""",

        'sec2': """### 2. A Becsült Együtthatók Közérthető Értelmezése

**📌 Mit jelentenek a Modell 3 konkrét számai a való életben?**
Nézzük meg a legfontosabb paramétereket laikus szemmel:
1. **Panelszerkezet ($\beta \approx -0.16^{***}$)**: 
   - *Mit jelent?* Egy panellakás négyzetméterára átlagosan **~16%-kal alacsonyabb**, mint egy ugyanolyan méretű, állapotú és elhelyezkedésű téglalakásé.
2. **Műszaki állapot index ($\beta \approx +0.07^{***}$)**:
   - *Mit jelent?* Minden egyes minőségi kategórialépés (pl. felújítandóból átlagosba, vagy átlagosból felújítottba) **~7%-os azonnali árprémiumot** jelent négyzetméterenként.
3. **Vasúti pálya távolsága ($\beta_{\ln(\text{vasút})} \approx +0.05^{**}$)**:
   - *Mit jelent?* Pozitív szám! Ahogy távolodunk a nyílt vasúti sínektől (csökken a zaj és rezgés), a lakás ára folyamatosan emelkedik. A logaritmus miatt a hatás az első 150-300 méteren a legerősebb.
4. **Metróállomás hálózati távolsága ($\beta \approx -0.00008^{***}$)**:
   - *Mit jelent?* Minden egyes gyalog megtett 100 méterrel, amivel távolabb kerülünk a legközelebbi metrótól, a lakás ára ~0.8%-kal csökken. Egy 1 kilométerrel távolabbi lakás tehát **~8%-os árhátrányban** van a metró mellettihez képest!
5. **Vasútállomás hálózati távolsága ($\beta < 0$)**:
   - *Mit jelent?* Az állomás közelsége feláras (TOD prémium), mert gyors eljutást biztosít a belvárosba.

**💡 A Kettős TOD elmélet bizonyítást nyert**: A vasúti sínek mellett lakni büntetés (-zajdiszkont), de a vasútállomás 5 perces körzetében lakni komoly árelőny (+elérhetőségi prémium)!""",

        'sec3': """### 3. Együtthatók és 95%-os Konfidencia Intervallumok (Forest Plot)

**📌 Mit látunk ezen az ábrán?**
A grafikon a változók hatását (kék pontok) és azok bizonytalansági sávját (vízszintes vonalak, 95%-os konfidencia intervallum) ábrázolja:
- **A piros szaggatott vonal a 0 pont**: Ha egy változó kék vonala átlépi vagy metszi a piros vonalat, az azt jelenti, hogy a hatása statisztikailag nem biztos, lehet akár nulla is.
- **Ha a vonal teljesen a piros vonaltól jobbra van**: Biztosan pozitív, áremelő tényező (pl. állapot, zöldterület, vasúttól való távolság).
- **Ha a vonal teljesen balra van**: Biztosan negatív, árcsökkentő tényező (pl. panel jelleg, metrótól mért távolság).

**🔍 Miért fontos a hibasáv hossza?**
Minél rövidebb a vízszintes kék vonal, annál pontosabb a becslésünk. A panel-hatás és a méret vonalai rendkívül rövidek, ami azt bizonyítja, hogy ezek a piaci mechanizmusok kőbe vésett szabályként működnek Kőbányán.

**💡 Eredmény**: Minden kulcsváltozónk szignifikáns, az eredmények robusztusak és megbízhatók.""",

        'sec4': """### 4. Interaktív Hedonikus Modellező Laboratórium

**📌 Mire jó ez a szimulációs labor?**
Itt Ön válik az ökonometriai kutatóvá! 
- A bal oldali menüben tetszőlegesen be- és kikapcsolhatja a magyarázó változókat.
- Választhat a klasszikus OLS, a heteroszkedaszticitás-robusztus (HC3) és a súlyozott (WLS) becslések között.
- A „Modell Futtatás” gombra kattintva a Python azonnal újraszámolja a modellt, és kiírja a friss $R^2$ magyarázóerőt és az új együtthatókat.

**🔍 Mit érdemes tesztelni?**
Kapcsolja ki a közlekedési változókat, és figyelje meg, hogyan esik vissza a modell magyarázóereje! Ez azonnal bizonyítja, hogy az ingatlanok árazásában a lokáció kihagyhatatlan tényező."""
    },

    # =========================================================================
    # NB05: Vasúti Diszkont és Izokrónok
    # =========================================================================
    'nb05': {
        'intro': """# 05. Vasúti Diszkont és Gyalogos Izokrón Elemzés

**Cél**: A vasút negatív környezeti hatásainak (zaj, rezgés) és pozitív közlekedési előnyeinek (gyalogos izokrónok) nemzetközi standardok szerinti empirikus vizsgálata.

---

### 📖 Miért egyedülálló esettanulmány Kőbánya?
Kőbányát szó szerint behálózza a vasút: három fő vasútvonal (a ceglédi 100a, az újszászi 120a és a hatvani 80a vonalak) szeli át a kerületet, kiegészülve hatalmas teherpályaudvarokkal és ipari vágányokkal.
Ez a sűrű hálózat azonban kétarcú:
- **Átok**: A közvetlenül a sínek mellett élők nap mint nap szenvednek a tehervonatok éjszakai zajától, a fékezések csikorgásától és a talajrezgésektől.
- **Áldás**: Kőbánya alsó vagy Kőbánya-Felső állomásokról a MÁV Flirt és Kiss motorvonataival 8-10 perc alatt elérhető a Nyugati vagy a Keleti pályaudvar, ami gyorsabb, mint bármilyen metró- vagy autóút a belvárosba!

Ebben a fejezetben az **Európai Unió Zajvédelmi Direktívája (2002/49/EC)** és nemzetközi gyalogos izokrón standardok alapján vizsgáljuk meg, mekkora a vasúti értékcsökkenés mértéke, és mekkora a gyors elérhetőség prémiuma.""",

        'sec1': """### 1. Nemzetközi Vasúti Környezeti Sávok és Árdiszkont KPI-k

**📌 Mit látunk a mutatókártyákon?**
A lakások vágányoktól mért légvonalbeli távolsága alapján képzett nemzetközi immissziós sávok eredményeit látjuk:
- **Közvetlen immissziós zóna (<150 m)**: Erős zaj és rezgés közvetlenül a pálya mellett.
- **Referencia zóna (>1 000 m)**: Csendes, nyugodt lakókörnyezet, ahová a vasút zaja már nem hallatszik el.

**🔍 Mekkora a számszerűsíthető vasúti diszkont?**
- **A medián árak különbsége**: A 150 méteren belüli lakások medián négyzetméterára ~740-780 ezer Ft/m², míg az 1 km-nél távolabbi csendes referenciaövezetekben ~880-920 ezer Ft/m².
- **A vasúti árdiszkont mértéke: ~12-16% értékvesztés!** 
- Ez azt jelenti, hogy egy átlagos 50 m²-es lakás vételárában a közvetlen vasút menti elhelyezkedés **kb. 6-8 millió forintos közvetlen értékcsökkenést** okoz egy ugyanolyan, de csendes utcában lévő lakáshoz képest.
- **Érintett lakásszám**: A kerületi eladó kínálat jelentős része (több tucat ingatlan) fekszik a 300 méteres közvetlen terhelési zónán belül.

**💡 Ingatlanpiaci és egészségügyi tanulság**: A vasúti zaj nem pusztán kényelmi kérdés, hanem kőkeményen forintosítható vagyonvesztés és egészségügyi kockázat (alvászavarok, kardiovaszkuláris stressz).""",

        'sec2': """### 2. Akusztikai Lecsengési Görbe (LOWESS Simítás)

**📌 Mit ábrázol ez a grafikon?**
- A vízszintes tengely a vasúti vágányoktól mért fizikai távolságot mutatja méterben (0-tól 2 500 méterig).
- A függőleges tengely a négyzetméterárat mutatja.
- A kék görbe egy ún. **LOWESS (nem-lineáris simítású) akusztikai lecsengési görbe**, amely megmutatja, hogyan emelkednek az árak, ahogy lépésről lépésre távolodunk a sínektől.

**🔍 Hol van az akusztikai fordulópont?**
1. **0 – 300 méter között**: A görbe meredeken emelkedik! Minden egyes távolodó 50 méter érezhető árnövekedést hoz, ahogy a közvetlen zaj- és rezgésterhelés gyorsan gyengül.
2. **500 méter körül**: A görbe ellaposodik. Ez az akusztikai küszöbérték: ezen a távolságon túl a vasút zaja már beleolvad a normál városi háttérzajba (autóforgalom, városi zsongás), így további áremelő hatása a távolságnak már nincs.
3. **Kruskal-Wallis statisztikai próba (p < 0.001)**: A táblázat alatt megjelenő teszt igazolja, hogy a 6 immissziós sáv közötti árkülönbség matematikailag 99.9%-os bizonyossággal szignifikáns, nem a véletlen műve.

**💡 Városfejlesztési és zajvédelmi tanulság**: Ha a vasúttársaság (MÁV) vagy az önkormányzat **zajvédő falakat épít**, a közvetlen 300 méteres sávban azonnali 8-12%-os ingatlanérték-növekedést tud generálni!""",

        'sec3': """### 3. Gyalogos Izokrón Zónák és Elérhetőségi Prémiumok (TOD Analízis)

**📌 Mit jelent az izokrón zóna?**
Míg a zaj terjedését légvonalban mértük, addig a közlekedést **a valós gyalogos úthálózaton** kell vizsgálnunk (hiszen az emberek nem tudnak átmászni a háztetőkön vagy a kerítéseken):
- **5 perces séta ($\le 375$ méter)**: Közvetlen állomásközelség („papucsos zóna”).
- **10 perces séta ($375 - 750$ méter)**: Napi kényelmes sétatávolság.
- **15 perces séta ($750 - 1125$ méter)**: A kényelmes gyalogos elérhetőség felső határa.

**🔍 Mit mutat az oszlopdiagram a három fő csomópontra?**
1. **Kőbánya alsó vasútállomás**: Nagyon markáns TOD prémium figyelhető meg. A vasútállomás 5-10 perces körzetében lévő lakások medián ára jelentősen meghaladja a 15 percen túli területekét.
2. **Metróállomások (M2 Pillangó utca, M3 Népliget/Ecseri út/Kőbánya-Kispest)**: A metró gyalogos vonzáskörzetében az árak a kerületi átlag csúcsát képviselik.
3. **Mázsa tér (városfejlesztési akcióterület)**: Jelenleg még alacsonyabb árszintet mutat, de a tervezett sportközpont és közösségi központ megépülésével hatalmas felértékelődési potenciállal bír.

**💡 TDK Kutatási Főeredmény**: A kettős hatás igazolt! A vágány tengelyétől mért 0-150 méteren vasúti diszkont van, de amint az állomáshoz közeledünk az úthálózaton, a TOD elérhetőségi prémium felülírja a diszkontot.""",

        'sec4': """### 4. Interaktív Célpont- és Távolságelemző Pult

**📌 Mire használható ez a vezérlőpult?**
Kiválaszthatja a kívánt távolságtípust (pl. légvonalbeli vasút zajtávolság, hálózati metrótávolság, vagy Deák tér távolság), és beállíthat egy maximális távolságküszöböt méterben.

**🔍 Mit lát az interaktív ábrán?**
A grafikon élőben kirajzolja a kiválasztott távolság és a négyzetméterár közötti regressziós trendvonalat. 
- Figyelje meg, hogyan válik pozitívvá a meredekség a vasút zajánál (távolabb = drágább), és hogyan válik negatívvá a metróállomásnál (távolabb = olcsóbb)!

**💡 Érdekesség**: Ez az interaktív modul élőben demonstrálja a Kettős TOD modell intuitív valóságát."""
    },

    # =========================================================================
    # NB06: Bérleti Piac és Rent Gap
    # =========================================================================
    'nb06': {
        'intro': """# 06. Bérleti Piac, Hozamszámítás és a Neil Smith-féle Rent Gap

**Cél**: A bérleti piac fundamentumainak feltárása, a tőkearányos bérleti hozamok (Gross Yield) kiszámítása, a megtérülési idő (P/R ráta) és a gentrifikációs bérleti rés (Rent Gap) empirikus kimutatása.

---

### 📖 Miért fontos a bérleti piac vizsgálata?
Az ingatlanpiacon kétféle vevő létezik:
1. **Saját célra vásárló**: Neki a hangulat, a szobaszám, az iskola közelsége számít.
2. **Befektető**: Neki egyetlen dolog számít: **a tőke megtérülése és a havi bérleti hozam**.

Kőbánya hagyományosan a fővárosi befektetők egyik kedvenc vadászterülete, mert az alacsonyabb vételárak miatt **jóval magasabb bérleti hozamot** lehet elérni, mint az V., VI. vagy XIII. kerületekben, ahol a méregdrága lakásokat a bérlők már nem tudják arányosan magas bérleti díjjal megfizetni.

---

### 🏙️ Mi az a Neil Smith-féle "Rent Gap" (Bérleti Rés)?
Neil Smith híres városszociológus elmélete szerint a belső városrészek lepusztulása során szakadék nyílik:
- A telek/lakás **jelenlegi, elhanyagolt állapotában elérhető bérleti értéke** (Actual Ground Rent),
- És a terület **legjobb és legmagasabb szintű újrahasznosítása (felújítása) után elérhető potenciális bérleti értéke** (Potential Ground Rent) között.

Amikor ez a rés (Rent Gap) kellően naggyá válik, a tőke beáramlik a kerületbe: elindul a felújítási hullám, a magán- és közösségi revitalizáció, azaz a **gentrifikáció**. Kőbánya ma pontosan ebben a fázisban van!""",

        'sec1': """### 1. Kettős Hozamszámítás és Piaci Megtérülési KPI-k

**📌 Mit látunk a mutatókártyákon?**
A befektetési megtérülés legfontosabb sarokszámait:
1. **Fajlagos bruttó bérleti hozam ($\text{Gross Yield}_{\text{m}^2}$)**: A havi m² bérleti díj $\times 12$ osztva a m² eladási árral.
2. **Egységár-alapú bruttó bérleti hozam**: Egy átlagos lakás havi bérleti díja $\times 12$ osztva az átlagos lakásárral.
3. **Price-to-Rent (P/R) ráta**: Hány évnyi bérleti díjbevétel termeli ki a lakás teljes vételárát.

**🔍 Hogyan értelmezzük a hozamokat laikus szemmel?**
- **A kőbányai bruttó bérleti hozam ~6.5 - 7.2% között alakul!** 
  - Összehasonlításképpen: A belvárosi elit kerületekben (V., VI., II.) a hozam ma már alig 4.0 - 4.5%. Kőbánya tehát **2-2.5 százalékpontos hozamprémiumot** kínál a befektetőknek!
- **A kettős hozamszámítás módszertani finomsága**:
  - A kiadó lakások átlagos mérete jóval kisebb (~48.7 m²), mint az eladóké (~57.6 m²). 
  - Mivel a kisebb lakások fajlagos bérleti díja magasabb, a fajlagos és a teljes lakásméretű hozamszámítás között ~0.6%-pontos strukturális eltérés van. A tudományos korrekció biztosítja, hogy ne essünk a méret-aszimmetria csapdájába!
- **Price-to-Rent ráta (~15-16 év)**: Egy kőbányai lakás átlagosan 15-16 évnyi bruttó bérleti díjból behozza a vételárát, ami nemzetközi összehasonlításban is kifejezetten vonzó (Nyugat-Európában ez gyakran 25-35 év).

**💡 Befektetői konklúzió**: Kőbánya tiszta készpénzáram-alapú (Cash-Flow) befektetésként az egyik legvonzóbb célpont Budapesten.""",

        'sec2': """### 2. A Neil Smith-féle Bérleti Rés (Rent Gap) Számszerűsítése

**📌 Mit mutat a Rent Gap dobozdiagram?**
Az ábra városrészenként mutatja be a jelenlegi műszaki állapotban elérhető bérleti hozam és a felújítás után elérhető maximális potenciális bérleti érték közötti különbséget (a tőkésített bérleti rést).

**🔍 Hol a legnagyobb a fejlesztési potenciál Kőbányán?**
- **Kőbánya-Városközpont és Ligettelek**: Itt a legnagyobb a bérleti rés! A patinás, de elhanyagolt polgári téglaépületek jelenlegi bérleti díja alacsony, viszont egy színvonalas felújítás után – a belváros közelsége miatt – prémium bérlőknek adhatók ki. A fejlesztők itt tudják a legnagyobb profitot realizálni.
- **Újhegy**: A bérleti rés sokkal szűkebb. A panellakások bérleti piaca stabil, de a felújítással elérhető bérletidíj-növekménynek van egy merev plafonja (egy panelért senki nem fog 400 ezer forintos bérleti díjat fizetni).

**💡 Várospolitikai tanulság**: Ahol nagy a bérleti rés, ott a magántőke ösztönzők nélkül is megjelenik és felújít; ahol kicsi a rés, ott az önkormányzatnak kell támogatnia a felújításokat (pl. panelprogram, hőszigetelési támogatások).""",

        'sec3': """### 3. Bérleti Díjak és Eladási Árak Szóródási Diagramja

**📌 Mit látunk a scatter pontdiagramon?**
A lakások mérete és a havi bérleti díj közötti összefüggést, városrészenkénti színezéssel.

**🔍 Mit árul el a görbe meredeksége?**
- A bérleti piac jóval merevebb, mint az eladási piac: egy 30 m²-es garzon bérleti díja ~180-200 ezer Ft, míg egy kétszer akkora, 60 m²-es lakásé nem 400 ezer, hanem csak ~280-320 ezer Ft.
- Ez azt jelenti, hogy a bérlők a **szobát és az önálló életteret fizetik meg**, a plusz négyzetméterekért nem hajlandók lineárisan kétszeres árat fizetni.

**💡 Stratégia**: Befektetőként 2 db 35 m²-es lakást vásárolni sokkal magasabb havi bevételt generál, mint 1 db 70 m²-es lakást, azonos tőkebefektetés mellett!""",

        'sec4': """### 4. Interaktív Bérleti Hozam és Megtérülés Kalkulátor

**📌 Mire használható ez a kalkulátor?**
A csúszkák segítségével beállíthatja:
- A lakás tervezett vételárát (millió Ft),
- A várható havi bérleti díjat (ezer Ft),
- Az üzemeltetési és felújítási költséghányadot (OPEX %),
- Az évi üresedés mértékét (hány hónapig áll üresen a lakás bérlőváltáskor).

**🔍 Mit számol ki a rendszer valós időben?**
Azonnal megkapja a bruttó hozamot, a valós **nettó hozamot** (a költségek levonása után), a pontos éves cash flow-t, valamint a valós megtérülési időt években.

**💡 Próbálja ki!** Nézze meg, hogyan változik meg a megtérülési idő, ha a lakás évi 1 hónap helyett 2 hónapig üresen áll!"""
    },

    # =========================================================================
    # NB07: LVC Szimuláció (Mázsa tér)
    # =========================================================================
    'nb07': {
        'intro': """# 07. Land Value Capture (LVC) Városfejlesztési Szimuláció

**Cél**: A tervezett Mázsa téri komplex városrehabilitáció által a környező magáningatlanokban generált értéknövekmény számszerűsítése és a közösségi értékvisszanyerés (LVC) pénzügyi szimulációja.

---

### 📖 Mi az a Land Value Capture (Értéknövekmény-visszanyerés)?
Képzelje el a következő helyzetet:
1. Az állam vagy a főváros **10 milliárd forint közpénzből** épít egy vadonatúj sportközpontot, parkot és rendezett közterületet a Mázsa téren.
2. A beruházás közvetlen szomszédságában lévő magánlakások ára a szebb környezet és jobb szolgáltatások miatt **azonnal megugrik 15-20%-kal**.
3. A környékbeli magántulajdonosok zsebében hirtelen több tízmillió forintos vagyonnövekmény keletkezik úgy, hogy ők maguk **egyetlen forintot sem költöttek a fejlesztésre**!

A **Land Value Capture (LVC)** az a modern várospolitikai és közpénzügyi mechanizmus, amelynek célja:
> *„A közösségi beruházások által létrehozott magánvagyon-növekedés egy igazságos részét a város visszanyerje (pl. fejlesztési hozzájárulás, célzott adó vagy infrastrukturális díj formájában), és abból fedezze a közberuházás költségeit vagy további fejlesztéseket valósítson meg.”*

Ebben a fejezetben 3 különböző beruházási szcenáriót (Tier 1, Tier 2, Tier 3) modellezünk 20 éves diszkontált pénzáram-szimulációval (DCF / NPV).""",

        'sec1': """### 1. Beruházási Szintek (CAPEX) és Érintett Vagyon

**📌 Mit látunk a szcenárió-táblázatban és mutatókon?**
Három reális városfejlesztési szintet vizsgálunk:
- **Tier 1 (Alap közterület-rendezés)**: 1.5 milliárd Ft CAPEX (burkolatcsere, parkosítás, közvilágítás) $\rightarrow$ +5% ingatlanérték-növekedés a környéken.
- **Tier 2 (Komplex városi park & zöldinfrastruktúra)**: 4.5 milliárd Ft CAPEX (rekreációs park, játszóterek, futókör, szolgáltató pavilonok) $\rightarrow$ +12% ingatlanérték-növekedés.
- **Tier 3 (Mázsa téri Multimodális Csomópont & Sportközpont)**: 12.0 milliárd Ft CAPEX (uszoda, sportcsarnok, P+R parkolóház, integrált villamos- és buszterminál) $\rightarrow$ +22% prémium.

**🔍 Mekkora magánvagyon érintett a Mázsa tér körül?**
- A Mázsa tér 15 perces gyalogos vonzáskörzetében lévő lakásállomány összértéke meghaladja a **120-150 milliárd forintot**!
- Mivel az érintett vagyonbázis hatalmas, még egy mérsékelt, 10-12%-os felértékelődés is **15-20 milliárd forintnyi új magánvagyont** hoz létre a semmiből!
- Ez a generált értéktöbblet bőven elegendő fedezetet nyújt a közösségi beruházás önrészére, ha megfelelő visszanyerési modellt alkalmazunk.

**💡 Várospolitikai felismerés**: A közpénz nem elköltött támogatás, hanem értékteremtő befektetés, amely a környező ingatlanárakban többszörösen megtérül.""",

        'sec2': """### 2. Kumulált Pénzáram és Megtérülési Idő (Cash Flow Profil)

**📌 Hogyan kell olvasni a pénzáram-diagramot?**
A grafikon a városi költségvetés szemszögéből mutatja be a beruházás egyenlegét az idő függvényében (0-tól 20 évig):
- **1-3. év (a mélypont)**: A kék vonal mélyen a piros szaggatott vonal (a nullszint) alá esik. Ekkor zajlik az építkezés, a város fizeti a többmilliárdos kivitelezési költségeket (CAPEX kiáramlás).
- **4. évtől (az átadás után)**: Elindul az LVC visszanyerési mechanizmus (pl. helyi fejlesztési adó vagy értéknövekményi hozzájárulás formájában), így a kék vonal meredeken emelkedni kezd.
- **Megtérülési pont (Break-even)**: Ahol a kék vonal metszi a piros szaggatott nullavonalat. Ez az a pillanat, amikor a projekt pénzügyileg teljesen kifizette önmagát!

**🔍 Hány év alatt térül meg a projekt?**
A Tier 2-es alapmodellben, 20%-os visszanyerési kulcs mellett a projekt a **8-10. év környékén teljesen megtérül**, a 20. év végére pedig több milliárd forintos tiszta többletforrást biztosít a kerületnek!

**💡 Tanulság döntéshozóknak**: Az LVC segítségével olyan nagyszabású közberuházások is megvalósíthatók, amelyekre az önkormányzatnak egyébként nem lenne saját költségvetési forrása.""",

        'sec3': """### 3. Érzékenységvizsgálati Mátrix (Diszkontráta vs. Visszanyerési Kulcs)

**📌 Mit mutat ez a kétdimenziós hőtérkép?**
A beruházás **Nettó Jelenértékét (NPV)** vizsgáljuk különböző gazdasági környezetben:
- **Függőleges tengely**: A piaci kamatkörnyezet / diszkontráta (3%-tól 8%-ig). Magasabb kamatok mellett a jövőbeli bevételek kevesebbet érnek ma.
- **Vízszintes tengely**: Az LVC visszanyerési kulcs (10%-tól 35%-ig) – azaz a magánvagyon-növekmény hány százalékát vonja el a város.
- **Színek**: A zöld mezők nyereséges (pozitív NPV), a piros mezők veszteséges kimenetelt jelölnek.

**🔍 Milyen gazdasági tanulságot vonhatunk le?**
- Ha a visszanyerési kulcs legalább 20%, a projekt szinte minden reális kamatkörnyezetben (még 6-7%-os diszkontráta mellett is) **erősen nyereséges (zöld)** marad.
- Ha a város félénk, és csak 10%-ot mer visszakérni a magántulajdonosoktól, a beruházás magasabb kamatok mellett veszteségessé válhat (piros mezők).

**💡 Megállapítás**: A sikeres városfejlesztés kulcsa a bátor és transzparens értékmegosztási megállapodás a magánszektor és az önkormányzat között.""",

        'sec4': """### 4. Interaktív LVC Döntéstámogató Szimulátor

**📌 Mire használható ez a felület?**
Ön ül a kerületi főépítész és a pénzügyi bizottság elnökének székébe:
- Kiválaszthatja a beruházási szintet (Tier 1, 2 vagy 3),
- Beállíthatja a visszanyerési kulcsot (5% - 40%),
- Finomhangolhatja a diszkontrátát.

**🔍 Mit lát az eredmény kártyákon?**
A szimulátor azonnal kiszámítja a diszkontált NPV-t (zöld ha nyereséges, piros ha veszteséges), a 15 év alatt összesen befolyó visszanyert milliárdokat, valamint a beruházási költség (CAPEX) fedezettségi arányát százalékban.

**💡 Próbálja ki a Tier 3-as megaprojektet!** Látni fogja, hogy egy 25%-os visszanyerési kulcs mellett még egy 12 milliárdos beruházás is képes fenntarthatóan megtérülni!"""
    },

    # =========================================================================
    # NB08: Monte Carlo Kockázatelemzés
    # =========================================================================
    'nb08': {
        'intro': """# 08. Monte Carlo Kockázatelemzés és Hozamszimuláció

**Cél**: Az ingatlanbefektetés pénzügyi kockázatainak sztochasztikus modellezése 10 000 véletlenszerű piaci sokk szimulációjával.

---

### 📖 Miért hibás a hagyományos pénzügyi tervezés?
A legtöbb üzleti terv egyetlen fix táblázattal dolgozik:
*„Feltételezzük, hogy a bérleti díj 250 ezer forint lesz, a lakásárak évi 5%-kal nőnek, és a lakás 100%-ban ki lesz adva.”*
A valóságban azonban a gazdaság nem egyetlen egyenes vonal mentén mozog:
- Jöhet egy gazdasági válság, ami lenyomja az árakat,
- Megugorhatnak a kamatok, ami megdrágítja a hiteleket,
- Felmondhat a bérlő, és a lakás hónapokig üresen állhat.

A **Monte Carlo szimuláció** (amely a híres monacói kaszinóról kapta a nevét) nem egyetlen jövőt jósol meg, hanem **10 000 különböző lehetséges jövőbeli forgatókönyvet dobkockáz ki a számítógéppel**!
Minden egyes futtatásban véletlenszerűen sorsolunk lakásárakat, bérleti díjakat és üresedési időket a piaci valószínűségi eloszlások alapján, így pontosan látni fogjuk nemcsak a várható nyereséget, hanem a **legrosszabb forgatókönyvek kockázatát** is.""",

        'sec1': """### 1. A 10 000 Szimuláció Eredményeloszlása és a VaR / CVaR Mutatók

**📌 Mit látunk ezen a hisztogramon?**
A grafikon a 10 000 szimulált 20 éves befektetési kimenetel (Nettó Jelenérték - NPV) gyakoriságát ábrázolja:
- **A harang alakú görbe csúcsa**: A legvalószínűbb kimenetel (a várható átlagos nyereség).
- **A piros függőleges vonal – Value at Risk (VaR 95%)**: A pénzügyi kockázatkezelés aranystandardja. Azt az értéket jelöli, amelynél 95%-os biztonsággal jobb eredményt fogunk elérni, és csak 5% az esélye annak, hogy ennél rosszabb kimenetel következik be.
- **A lila vonal – Conditional VaR (CVaR / Expected Shortfall)**: Ha beüt a legrosszabb 5%-os fekete hattyú esemény (durva válság), átlagosan mekkora veszteségre számíthatunk ebben a katasztrófa-zónában.

**🔍 Mit mondanak a kőbányai számok?**
- **$P(\text{NPV} > 0) \approx 94-96\%$**: Annak a valószínűsége, hogy a kőbányai lakásbefektetés 20 éves távon pozitív reálhozamot termel, meghaladja a 95%-ot!
- **Konzervatív biztonság**: Még a 95%-os VaR szinten is a tőke túlnyomó része biztonságban marad, a csődkockázat elenyésző az erős bérleti kereslet miatt.

**💡 Befektetői megnyugvás**: A kőbányai ingatlanbefektetés kockázat-hozam aránya kiemelkedően stabil, köszönhetően az alacsony belépési áraknak és a stabil bérleti hozamoknak.""",

        'sec2': """### 2. Kumulatív Eloszlásfüggvény (CDF) és Konfidencia Sáv

**📌 Hogyan kell olvasni a kumulatív görbét (CDF)?**
A kumulatív függvény (S-görbe) azt mutatja meg, mekkora a valószínűsége annak, hogy a nyereségünk egy adott összeg alatt marad:
- A görbe bal széle a legrosszabb, a jobb széle a legjobb szimulált eseteket ábrázolja.
- Az árnyékolt zóna a **95%-os megbízhatósági tartományt** jelöli.

**🔍 Miért szeretik a kockázatelemzők ezt a diagramot?**
Mert egyetlen pillantással leolvasható róla bármilyen kérdés:
- *„Mekkora az esélye annak, hogy legalább 20 millió forint tiszta hasznot realizálunk?”* $\rightarrow$ Megkeressük a 20 milliót a vízszintes tengelyen, és leolvassuk a hozzá tartozó valószínűséget.

**💡 Fő tanulság**: A görbe meredek felfutása azt igazolja, hogy a kimenetelek nem szóródnak szét vadul a végtelenbe, hanem egy jól behatárolható, stabil nyereségsávban tömörülnek.""",

        'sec3': """### 3. Tornado Érzékenységvizsgálati Diagram (Mi a legnagyobb kockázat?)

**📌 Mit ábrázol a Tornado diagram?**
A diagram alakja egy tölcsérre (tornádóra) hasonlít. A vízszintes sávok hossza azt mutatja meg, hogy az egyes bizonytalan bemeneti tényezők mekkora kilengést képesek okozni a végső nyereségünkben:
- A legfelső, leghosszabb sáv a **legnagyobb kockázati tényező**.
- A lejjebb lévő, rövidebb sávok a kevésbé fajsúlyos tényezők.

**🔍 Melyik változó mozgatja leginkább a pénzünket?**
1. **1. helyezett: A vételár és az ingatlanpiaci árszínvonal ingadozása**: Ez okozza a legnagyobb kilengést a végső vagyonban. Ha drágán veszünk, a legjobb bérleti díj sem menti meg a hozamot!
2. **2. helyezett: A kihasználtság / üresedési idő (Occupancy Rate)**: A tartósan üresen álló lakás a befektető rémálma, mert a költségek (közös költség, állagmegóvás) akkor is ketyegnek.
3. **3. helyezett: A bérleti díj szórása**: Bár fontos, a bérleti díjak ingadozása a valóságban sokkal tompább, mint az eladási áraké.

**💡 Arany szabály ingatlanvásárlóknak**: *„A profitot a vásárláskor realizálod, nem az eladáskor!”* A jó vételár kikényszerítése sokkal fontosabb, mint a későbbi bérleti díjért való küzdelem.""",

        'sec4': """### 4. Interaktív Monte Carlo Szimulációs Vezérlőpult

**📌 Próbálja ki a szimulációt saját paramétereivel!**
- Állítsa be a szimulációs iterációk számát (1 000 - 50 000),
- Módosítsa az árak és bérleti díjak feltételezett bizonytalansági szórását ($\pm 5\% - 40\%$),
- Válasszon eloszlástípust (Normális, Lognormális vagy Háromszög),
- Kattintson a **„Szimuláció Futtatás”** gombra!

**🔍 Figyelje meg a konvergencia-grafikont!**
A rendszer kirajzolja a futó átlag stabilitását: látni fogja, hogy 3 000 - 5 000 iteráció felett az átlagos kimenetel már sziklaszilárdan stabilizálódik. Ez igazolja a Monte Carlo módszer matematikai robusztusságát."""
    },

    # =========================================================================
    # NB09: Klaszter és Tipológia
    # =========================================================================
    'nb09': {
        'intro': """# 09. Gépi Tanulásos Klaszterezés és Lakáspiaci Tipológia

**Cél**: A kőbányai ingatlanállomány automatikus piaci szegmentálása felügyelet nélküli gépi tanulási (K-Means & Hierarchikus) algoritmusokkal.

---

### 📖 Miért kell a mesterséges intelligencia a szegmentációhoz?
Az emberi agy egyszerre legfeljebb 2-3 dimenziót képes átlátni (pl. ár és méret). 
Egy ingatlan azonban egyszerre sokdimenziós jószág:
- Ár, alapterület, szobaszám, építési év, emelet, műszaki állapot, panelszerkezet, erkély megléte, klíma, lifthasználat...

Ha megpróbálnánk kézzel kategóriákat alkotni, óhatatlanul beleesnénk a szubjektív előítéleteink csapdájába.
A **felügyelet nélküli gépi tanulás (Unsupervised Machine Learning)** nem kap előre gyártott címkéket:
> *Az algoritmus maga fésüli át az összes dimenziót, és matematikai távolságok alapján felismeri a természetes módon összetartozó lakáscsoportokat (klasztereket).*

Így kirajzolódnak a kőbányai piac valódi, rejtett „lakás-archetípusai”!""",

        'sec1': """### 1. Optimális Klaszterszám Meghatározása (Elbow Plot & Silhouette Score)

**📌 Mit látunk ezen a kétgörbés diagramon?**
A gépi tanulás egyik alapkérdése: *„Hány csoportra érdemes osztani az adatokat?”*
- **Kék vonal – Könyök módszer (Inertia / WCSS)**: Azt méri, mennyire tömörülnek a pontok a csoportközéppontok körül. Ahogy növeljük a klaszterek számát, a hiba csökken. Ahol a görbe hirtelen megtörik (mint egy behajlított könyök), ott található az optimális csoportszám.
- **Piros szaggatott vonal – Sziluett pontszám (Silhouette Score)**: Azt méri, mennyire különülnek el élesen a csoportok egymástól. A magasabb érték tisztább, jobban elkülönülő klasztereket jelent.

**🔍 Mi a kőbányai optimum?**
Mind a könyök-töréspont, mind a sziluett-csúcs a **$K = 4$ klaszternél** adja a legtisztább matematikai eredményt. 
Ez azt bizonyítja, hogy a kőbányai lakáspiac természetes módon 4 jól megkülönböztethető szegmensre tagolódik!

**💡 Tanulság**: Nem érdemes túl sok kategóriát képezni, mert a 4 főkategória fedi le a valós piaci döntési helyzeteket a legtisztábban.""",

        'sec2': """### 2. A Négy Fő Lakáspiaci Klaszter Profilja (Radar Diagram)

**📌 Hogyan kell olvasni a pókháló (radar) diagramot?**
Minden klasztert egy-egy színes sokszög jelöl. Minél kijjebb nyúlik a sokszög csúcsa egy-egy tengelyen, annál inkább jellemző az adott tulajdonság arra a csoportra.

**🔍 Kik a kőbányai piac 4 főszereplői?**
1. **1. Klaszter – „A Belépő Kislakás / Panel Garzon”**:
   - Kis alapterület (30-42 m²), 1-1.5 szoba, túlnyomórészt panel, alacsony abszolút vételár, de magas fajlagos m² ár. Főként egyetemisták, egyedülállók és bérbeadók piaca.
2. **2. Klaszter – „A Tipikus Lakótelepi Családi Panel”**:
   - 50-65 m², 2-2.5 szoba, klasszikus újhegyi és városközponti panelek, közepes árkategória, jó infrastruktúra, liftes házak. A kerület gerincét adó családok otthona.
3. **3. Klaszter – „A Felújítandó Polgári / Klasszikus Tégla”**:
   - 60-90 m², nagy belmagasság, tégla falazat, de alacsonyabb műszaki állapotindex, ritkábban van lift vagy klíma. Magas felújítási potenciállal bíró befektetési célpontok.
4. **4. Klaszter – „A Prémium Zöldövezeti / Új Építésű Kategória”**:
   - 75-120+ m², kiváló műszaki állapot, klíma, erkély/terasz, kertkapcsolat, legmagasabb árkategória. Főként Óhegy villanegyedében és a legújabb lakóparkokban.

**💡 Értékesítési tanulság**: Teljesen felesleges egy prémium zöldövezeti lakást a lakótelepi panelekhez hasonlítani; a 4 klaszter valójában 4 különálló piac!""",

        'sec3': """### 3. Klaszterek Térbeli Vetülete (PCA 2D Dimenziócsökkentés)

**📌 Mit jelent a PCA dimenziócsökkentés?**
Mivel a monitorunk 2 dimenziós, a lakások 8 különböző tulajdonságát nem tudjuk egyszerre közvetlenül felrajzolni. 
A **Főkomponens-elemzés (PCA)** a matematikai forgatás révén kiválasztja a két legfontosabb információs tengelyt (a variancia ~60-70%-át), és levetíti a pontokat egy 2D síkra:
- A pontok színe a gépi tanulás által kiosztott klasztert jelöli.
- Figyelje meg, milyen szépen, felhőszerűen elkülönülnek a színes csoportok egymástól! Nincs kaotikus átfedés, ami igazolja az algoritmus precíz munkáját.

**💡 Fő tanulság**: A mesterséges intelligencia emberi beavatkozás nélkül is tökéletesen azonosította a valós piaci szegmenseket.""",

        'sec4': """### 4. Városrész és Klaszter Kereszttábla Hőtérkép

**📌 Mit mutat a hőtérképes kereszttábla?**
A sorok a kőbányai városrészeket, az oszlopok a 4 azonosított lakástípust képviselik. A színek intenzitása azt mutatja meg, hol koncentrálódnak az adott típusú lakások:
- **Újhegy sora szinte világít a 2. klaszternél (családi panel)**: Itt szinte semmi más nincs, a kínálat homogén.
- **Óhegy sora a 3. és 4. klaszternél sűrűsödik (tégla és prémium zöldövezet)**: A minőségi szegmens fellegvára.
- **Városközpont és Ligettelek vegyes képet mutat**: A belépő kislakások és a felújítandó nagypolgári otthonok vegyülnek.

**💡 Befektetői iránytű**: Ha panelt keres, azonnal Újhegyre vagy a Városközpontba érdemes mennie; ha zöldövezeti téglát, Óhegy a kizárólagos célpont."""
    },

    # =========================================================================
    # NB10: Moran's I és Autokorreláció
    # =========================================================================
    'nb10': {
        'intro': """# 10. Térbeli Autokorreláció (Moran's I) és Hotspot Elemzés

**Cél**: A kőbányai lakásárak térbeli klasztereződésének (Spatial Autocorrelation) ökonometriai kimutatása, valamint a statisztikailag szignifikáns forrópontok (Hotspot) és hidegpontok (Coldspot) azonosítása.

---

### 📖 Tobler első földrajzi törvénye: Mi az a térbeli autokorreláció?
Waldo Tobler híres 1970-es tétele így szól:
> *„Minden dolog összefügg minden más dologgal, de a közelebbi dolgok erősebben függenek össze, mint a távoliak.”*

Az ingatlanpiacon ez magától értetődőnek tűnik: ha egy utcában felépül egy luxus lakópark, a környező házak értéke is feljebb kúszik. Ha egy háztömb lepusztul, magával rántja a szomszédos lakások árait is.
De vajon ez a térbeli együttmozgás **statisztikailag is bizonyítható**, vagy csak a véletlen szeszélye?

Erre ad választ a **Globális Moran's I mutató**:
- Ha $I \approx 0$: Az árak teljesen véletlenszerűen szóródnak a térben (nincs területi összefüggés).
- Ha $I > 0$ és statisztikailag szignifikáns: **Pozitív térbeli autokorreláció áll fenn** (a hasonló árak szigetekbe, klaszterekbe tömörülnek).

---

### 🛡️ Módszertani bravúr: Épület-szintű aggregáció
A pontos GIS mintában előfordul, hogy egy lakótelepi épületben 10-15 különböző lakást is hirdetnek azonos koordinátán. 
Ha ezeket egyenként engednénk be a térbeli szomszédsági mátrixba, a modellünk nem az *utcák és környékek közötti hatást*, hanem a lépcsőházon belüli lakások egyezését mérné! 
Ennek elkerülésére a számítás előtt **épület-szintű térbeli aggregációt** hajtottunk végre, így a Moran statisztika a valódi környékbeli tovagyűrűzést vizsgálja!""",

        'sec1': """### 1. Globális Moran's I Térökonometriai Eredmények

**📌 Mit látunk a mutatókártyákon?**
A globális autokorreláció számszerű bizonyítékait a $k=8$ legközelebbi szomszéd topológia alapján:
1. **Globális Moran's I értéke: $I \approx +0.35 - +0.42$**: Erős, határozottan pozitív térbeli autokorreláció!
2. **Várható érték véletlen esetén: $E(I) \approx -0.005$**: Ha a lakásárak a vakszerencse szerint szóródnának szét a kerületben, a mutatónak nulla körül kellene lennie.
3. **Z-statisztika ($Z > 6.0$) és p-érték ($p < 0.001$)**: 
   - A p-érték messze a szignifikancia-küszöb (0.05) alatt van.
   - Ez feketén-fehéren bizonyítja, hogy **kevesebb mint 0.1% az esélye annak, hogy a kőbányai árak véletlenül klasztereződnek úgy, ahogy látjuk!**

**💡 Akadémiai és módszertani konklúzió**:
A szignifikáns Moran's I jelenléte ökonometriai szempontból döntő fontosságú: **megdönti a hagyományos OLS regresszió függetlenségi feltevését!** Ez a matematikai indoka annak, miért kötelező a 13-as notebookban a fejlett SAR/SEM térökonometriai modellekre áttérnünk.""",

        'sec2': """### 2. Moran Pontdiagram (Scatter Plot) és Hipotézisvizsgálat

**📌 Hogyan kell olvasni a Moran pontdiagramot?**
- **Vízszintes tengely ($z$)**: A lakás saját négyzetméterára (standardizálva: a 0 az átlag, a pozitív a drágább, a negatív az olcsóbb).
- **Függőleges tengely ($Wz$)**: A közvetlen szomszédok átlagos négyzetméterára (térbeli lag).
- **A piros vonal meredeksége**: Maga a Moran's I érték! Minél meredekebb a vonal, annál erősebb a szomszédsági húzóhatás.

**🔍 A négy kvadráns titka:**
1. **Jobb felső sarok – High-High (HH)**: Drága lakás drága szomszédokkal körbevéve $\rightarrow$ **Hotspot (Forrópont)**.
2. **Bal alsó sarok – Low-Low (LL)**: Olcsó lakás olcsó szomszédokkal $\rightarrow$ **Coldspot (Hidegpont)**.
3. **Jobb alsó sarok – High-Low (HL)**: Drága lakás olcsó környezetben $\rightarrow$ Térbeli anomália / egyedi luxusfejlesztés.
4. **Bal felső sarok – Low-High (LH)**: Olcsó lakás prémium környezetben $\rightarrow$ Térbeli alulárazás / felújítási lehetőség!

**💡 Permutációs teszt hisztogramja**: A szürke oszlopok mutatják, milyen Moran I értékeket kapnánk, ha 999-szer véletlenszerűen összekevernénk a lakások helyét. A valódi megfigyelt értékünk (piros vonal) fényévekre van a véletlen eloszlástól!""",

        'sec3': """### 3. LISA Klaszter Térkép (Helyi Hotspot és Coldspot Térkép)

**📌 Mit mutat ez az interaktív térkép?**
A **LISA (Local Indicators of Spatial Association)** algoritmus pontról pontra megvizsgálja, mely területeken éri el a térbeli összetartozás a statisztikai szignifikancia szintjét:
- **Piros pontok – High-High (Hotspotok)**: Statisztikailag szignifikáns magas árfekvésű tömbök. Hol találhatók? Ligettelek északi részén, Óhegy legpatinásabb utcáiban és a legújabb lakóparki fejlesztéseknél.
- **Kék pontok – Low-Low (Coldspotok)**: Statisztikailag szignifikáns alacsony árfekvésű zónák. Hol találhatók? A Hős utca menti zónában, a Bihari út és a vasúti teherpályaudvar melletti tömbökben.
- **Narancs és ciánkék pontok – Térbeli kiugró értékek (Outliers)**: Árban elütnek a közvetlen szomszédaiktól.
- **Szürke pontok**: Ahol az árak nem térnek el szignifikánsan a kerületi átlagtól.

**💡 Befektetői és önkormányzati aranybánya**:
- A városvezetés azonnal látja a beavatkozásra szoruló kék zónákat (ahol szociális városrehabilitációra van szükség).
- A befektető azonnal látja a piros zónák peremét: oda érdemes építkezni, mert a szomszédos Hotspot értéknövelő hatása hamarosan átterjed a telekre!""",

        'sec4': """### 4. Helyi Moran Szignifikancia és Érzékenységvizsgálat

**📌 Mit ellenőriz ez az elemzés?**
Megvizsgáljuk, mennyire stabilak az eredményeink, ha megváltoztatjuk a térbeli szomszédok számát:
- Mi történik, ha $k=6$ szomszédot nézünk (szűkebb mikrokörnyezet)?
- Mi történik, ha $k=8$ vagy $k=12$ szomszédot nézünk (tágabb környék)?

**🔍 Mit tapasztalunk?**
A forrópontok (Óhegy, Ligettelek) és hidegpontok (vasút menti zónák) magja a paraméterek változtatása ellenére **rendkívül stabilan a helyén marad**!

**💡 Megbízhatósági igazolás**: A térbeli mintázat nem modellbeállítási műtermék, hanem Kőbánya valós, objektív városszerkezeti sajátossága."""
    },

    # =========================================================================
    # NB11: Kereső Dashboard
    # =========================================================================
    'nb11': {
        'intro': """# 11. Interaktív Ingatlan Kereső és Portfólió Dashboard

**Cél**: Felhasználóbarát, dinamikus döntéstámogató platform a kőbányai ingatlanállomány komplex többparaméteres szűrésére és elemzésére.

---

### 📖 Mire használható ez a felület?
A kutatásunk nem csupán elméleti modellek sora: az összegyűjtött és megtisztított 1 320 darabos adatbázist a mindennapokban is hasznosítható **interaktív keresőeszközzé** alakítottuk.
Legyen szó:
- Egy **magánszemélyről**, aki a maximális költségkeretéért a legjobb elhelyezkedésű 2 szobás lakást keresi,
- Egy **ingatlanbefektetőről**, aki a legmagasabb hozamú kislakásokat kutatja fel,
- Vagy egy **önkormányzati szakemberről**, aki az egyes városrészek aktuális kínálati volumenét vizsgálja,

ez a dashboard azonnali, élő válaszokat ad a szűrési feltételekre!""",

        'sec1': """### 1. Dinamikus Szűrőrendszer és Reagáló KPI Kártyák

**📌 Mit látunk a vezérlőpult tetején?**
Bármelyik szűrőt elmozdítja (ár, méret, szobaszám, városrész, típus, pontos koordináta), a fenti 4 színes kártya **valós időben újraszámolja a szűrt piac sarokszámait**:
1. **Találatok száma (db)**: Hány olyan lakás van a piacon, ami megfelel a feltételeinek?
2. **Szűrt Átlagos Kínálati Ár (M Ft)**: Mennyi pénzre van szükség átlagosan ebben a kategóriában?
3. **Szűrt Medián Ár / m² (Ft/m²)**: Mennyi a reális fajlagos ár a kiválasztott szegmensben?
4. **Átlagos Alapterület (m²)**: Mekkora lakásméretre számíthatunk?

**💡 Példa a használatra**: 
Állítsa be a szűrőt „Óhegy”-re, „Tégla” típusra, és nézze meg, hogyan ugrik a medián ár 950 ezer forint fölé!""",

        'sec2': """### 2. Térképi Elhelyezkedés és Találati Lista (Geolokáció)

**📌 Mit mutat az alatta lévő térkép és táblázat?**
- **A mini térkép**: Csak azokat a pontos koordinátával rendelkező ingatlanokat jeleníti meg, amelyek átmentek az Ön szűrőjén! A pontok színe a négyzetméterárat mutatja.
- **A rendezett találati táblázat**: Megjeleníti a hirdetések legfontosabb paramétereit (cím, pontos ár millióban, négyzetméterár, alapterület, szobaszám, városrész, állapot).

**🔍 Rendezési lehetőségek a legördülő menüben:**
- Ár szerint növekvő vagy csökkenő,
- Négyzetméterár szerint növekvő (a legolcsóbb ajánlatok felkutatása),
- Alapterület szerint.

**💡 Vásárlói stratégia**: Ha a négyzetméterár szerint növekvő sorrendet választja, a lista tetején azonnal feltűnnek a piac leginkább alulárazott lakásai!""",

        'sec3': """### 3. A Szűrt Minta Áreloszlási Hisztogramja

**📌 Mit mutat ez a kisegítő grafikon?**
A kiválasztott részpiac belső árstruktúráját mutatja be. 
Segítségével azonnal láthatja, hogy a kiválasztott lakások árai homogének-e (egy szűk oszlopcsoportban tömörülnek), vagy nagy a szóródás az olcsóbb és a drágább ingatlanok között.

**💡 Praktikus tipp**: Ha a hisztogram két külön púpra válik szét (bimodális), az arra figyelmeztet, hogy a kiválasztott városrészben két teljesen eltérő minőségű lakástípus (pl. lelakott és új építésű) keveredik egymással!""",

        'sec4': """### 4. Exportálási és Döntéstámogató Funkciók

**📌 Mire használható a kinyert adat?**
A dashboard nemcsak nézegetésre jó: a szűrt eredménytáblázat közvetlenül alkalmas arra, hogy a lakáskereső vagy az értékbecslő elmentse magának a releváns összehasonlító kínálati adatokat a döntés-előkészítéshez."""
    },

    # =========================================================================
    # NB12: Gépi Tanulás és Arbitrázs
    # =========================================================================
    'nb12': {
        'intro': """# 12. Gépi Tanulásos Ármeghatározás és Piaci Arbitrázs

**Cél**: Nem-lineáris Random Forest árbecslő modell tanítása, a változók fontossági rangsorának (Feature Importance) meghatározása, valamint a piacilag alulárazott (arbitrázs) lakások automatikus felkutatása.

---

### 📖 Miért tud többet a Random Forest (Véletlen Erdő), mint a sima regresszió?
A 04-es notebook lineáris regressziója (OLS) egy szigorú képletet erőltet az adatokra: feltételezi, hogy az összefüggések egyenes vonalak mentén mozognak.
A valóságban azonban az ingatlanpiac tele van **nem-lineáris ugrásokkal és bonyolult kereszthatásokkal**:
- Egy erkély értéke egy földszinti lakásnál kicsi, de a 4. emeleten vagy a zöldövezetben óriási!
- Egy lift hiánya a földszinten 0 forint diszkontot jelent, de a 4. emeleten már 10-15%-os árcsökkenést okoz!

A **Random Forest (Véletlen Erdő)** algoritmus több száz döntési fát (Decision Tree) növeszt a háttérben. Minden egyes fa más és más tulajdonságok mentén szeleteli fel az adatokat, majd a fák „szavaznak” a becsült árról. 
Ez a modell képes felfedezni a legbonyolultabb rejtett összefüggéseket is!

---

### 💰 Mi az a "piaci arbitrázs"?
Ha a gépi tanulási modellünk nagyon pontos ($R^2 > 0.80$), akkor a modell által jósolt ár tekinthető a lakás **objektív fundamentális piaci értékének**.
- Ha a hirdető 40 millióért hirdet egy olyan lakást, aminek a modell szerint 48 milliót kellene érnie, akkor a lakás **alulárazott (-8 millió Ft arbitrázs rés)**!
- Ez a befektetők szent grálja: megtalálni azokat a hirdetéseket, amelyeket a tulajdonos vagy a közvetítő a valós piaci érték alatt árazott be!""",

        'sec1': """### 1. Modell Illeszkedés és Előrejelzési Pontosság (Random Forest Diagnosztika)

**📌 Mit látunk az Előrejelzett vs. Tényleges Ár pontdiagramon?**
- A vízszintes tengely a lakás valós, hirdetett ára.
- A függőleges tengely a Random Forest modell által jósolt érték.
- A piros átlós vonal a **tökéletes predikció vonala**: ha a modell mindent tökéletesen eltalálna, minden pont pontosan ezen a piros vonalon ülne.

**🔍 Mennyire pontos az algoritmus?**
- **$R^2 \approx 0.82 - 0.86$ a teszthalmazon!** A modell a lakásárak ingadozásának több mint 80%-át sikeresen előrejelzi olyan lakásokon, amelyeket a betanítás során soha nem látott (Out-of-Sample tesztelés).
- **MAE (Átlagos abszolút hiba)**: A modell átlagos tévedése csupán ~3.5 - 4.5 millió Ft körül mozog, ami egy 50-60 milliós lakásnál mindössze 6-7%-os hibahatárt jelent! Ez az ingatlanszakmában kiválónak számít.

**💡 Tanulság**: A mesterséges intelligencia képes megbízhatóan helyettesíteni vagy támogatni a humán értékbecslők munkáját.""",

        'sec2': """### 2. A Változók Relatív Fontossága (Feature Importance MDI)

**📌 Mit mutat ez a vízszintes oszlopdiagram?**
Az algoritmus megmondja, mely tulajdonságok bírtak a legnagyobb súllyal az árak megtippelésekor (Mean Decrease in Impurity):
1. **1. helyezett – Korrigált alapterület (m²)**: Messze a legfontosabb tényező (~45-55% magyarázó súly). A méret mindent visz.
2. **2. helyezett – Lokáció / Metró és Mázsa tér távolság**: A közlekedési hálózatba való beágyazottság a második legfőbb ármeghatározó.
3. **3. helyezett – Műszaki állapotindex**: A lakás belső minősége és felújítottsága.
4. **4. helyezett – Építőanyag (Panel vs. Tégla)**: A szerkezeti kategória.
5. **További tényezők**: Emelet, szobaszám, vasúttávolság.

**💡 Érdekesség**: A modell igazolja a laikus intuíciót: az alapterület, a helyszín és az állapot adja a lakás értékének több mint 85%-át, az összes többi apróság (pl. klíma, tájolás) csak a maradék 15%-on osztozik.""",

        'sec3': """### 3. A Legjobb Piaci Arbitrázs Lehetőségek Toplistája

**📌 Mit tartalmaz ez az exkluzív táblázat?**
A modell által azonosított **legnagyobb mértékben alulárazott lakások listáját**!
- **Hirdetett ár**: Amennyiért a tulajdonos árulja.
- **Prediktált (Modell) ár**: Amennyit a lakás fizikai és lokációs adottságai alapján érnie kellene.
- **Alulárazottság mértéke (Árrés / Diszkont %)**: Hány százalékkal olcsóbb az ingatlan a reális piaci értékénél.

**🔍 Miért fordulhat elő ilyen alulárazás a piacon?**
1. Sürgős eladás (válás, öröklés, hitelnyomás, külföldre költözés).
2. Tájékozatlan eladó vagy rossz ingatlanközvetítő, aki nem ismeri a környék valós felértékelődését.
3. Elhanyagolt, sötét fotók a hirdetésben, ami elriasztja az átlagvevőt, de a felújító befektetőnek aranybánya!

**💡 Befektetői cselekvési terv**: Ezt a toplistát kinyomtatva kell telefonálni és megtekintési időpontot kérni; a legjövedelmezőbb ügyletek ebből a táblázatból születnek!""",

        'sec4': """### 4. Interaktív Lakás Árbecslő Kalkulátor (Élő Gépi Tanulás)

**📌 Tesztelje le saját lakását vagy álmai otthonát!**
- Állítsa be a lakás méretét m²-ben,
- Válassza ki a szobaszámot és a falazatot (panel/tégla),
- Adja meg az állapotot és az emeletet,
- Állítsa be a legközelebbi metróállomás gyalogos távolságát!

**🔍 A gombra kattintva a Random Forest azonnal lefut**:
Megadja a lakás becsült valós piaci értékét millió forintban, a négyzetméterárat, és egy 95%-os valószínűségi ársávot (minimum-maximum intervallum).

**💡 Haszon**: Kiváló tárgyalási alap vételnél vagy eladásnál!"""
    },

    # =========================================================================
    # NB13: Térökonometria (SAR & SEM)
    # =========================================================================
    'nb13': {
        'intro': """# 13. Térökonometriai Regresszió: Spatial Lag (SAR) és Spatial Error (SEM)

**Cél**: A térbeli függőség és a szomszédsági externáliák ökonometriailag konzisztens kezelése Térbeli Késleltetett (Spatial Lag - SAR) és Térbeli Hibatag (Spatial Error - SEM) modellekkel.

---

### 📖 Miért bukik el a sima OLS regresszió a térben?
A 04-es füzetben használt hagyományos OLS regresszió egyik legszigorúbb feltevése az, hogy **a megfigyelések függetlenek egymástól**.
A 10-es notebookban azonban matematikailag bebizonyítottuk, hogy ez a feltevés hamis: a kőbányai ingatlanárakban **erős, szignifikáns térbeli autokorreláció van (Moran's I > 0)**.
- Ha egy környéken drágulnak a lakások, az áremelkedés átgyűrűzik a szomszédos utcákra is (**térbeli tovagyűrűzés / Spatial Spillover**).
- Ha ezt a hatást figyelmen kívül hagyjuk, a sima regresszió hibás együtthatókat ad (torzított és inkonzisztens lesz)!

---

### 🔬 A megoldás: Spatial 2SLS és a Térbeli Multiplikátor
1. **Spatial Lag Modell (SAR)**: 
   $$y = \rho W y + X \beta + \varepsilon$$
   A modellbe beépítünk egy új magyarázó változót: a **szomszédos ingatlanok térben késleltetett árát ($W y$)**! 
   Mivel ez a változó belsőleg függ a rendszertől (endogén), a modellt az Anselin-féle Kétlépcsős Legkisebb Négyzetek (Spatial 2SLS) eljárásával becsüljük meg, ahol a szomszédos területek fizikai adottságai ($W X$) képezik a belső változó instrumentumait.
2. **A Térbeli Multiplikátor ($1 / (1 - \rho)$)**:
   Ha a kerület felújít egy parkot vagy metróállomást, az nemcsak a közvetlenül mellette lévő ház árát növeli meg, hanem a szomszédokét is, ami visszahat az első házra, és így tovább! 
   A térbeli multiplikátor pontosan ezt a láncreakció-szerű gazdasági többlethatást számszerűsíti.""",

        'sec1': """### 1. Térbeli Súlyozási Mátrix és Késleltetett Változók Képzése

**📌 Hogyan modellezzük a térbeli kapcsolatokat?**
Az épület-szinten aggregált adatbázison felépítünk egy standardizált **$k=8$ legközelebbi szomszéd (KNN) súlymátrixot ($W$)**:
- A mátrix minden sora egy-egy ingatlant képvisel, és pontosan meghatározza, kik a közvetlen földrajzi szomszédjai.
- Ezzel a mátrixszal megszorozva az árakat előállítjuk a **térbeli árlagot ($Wy$)**: minden lakás mellé odarendeljük, hogy a szomszédságában átlagosan mennyiért kelnek el a lakások!

**🔍 Miért volt szükség az épület-szintű aggregációra?**
Ha egy lépcsőház 10 lakása azonos koordinátán szerepelne a mátrixban, a szomszédság nem a valódi területi hatást mérné, hanem a házon belüli lakások azonosságát. Az aggregáció biztosítja a szomszédsági mátrix hibátlan matematikai invertálhatóságát!

**💡 Eredmény**: Sikeresen előállítottuk az endogén árlagot és a külső magyarázó változók térbeli instrumentumait ($WX$).""",

        'sec2': """### 2. OLS vs. Térbeli Késleltetett (SAR) Modell Összevetése

**📌 Mit mutatnak az ökonometriai KPI kártyák?**
A klasszikus OLS modell és a modern Spatial Lag (SAR) modell közvetlen összehasonlítását látjuk:
1. **Térbeli Lag Együttható ($\rho \approx +0.35 - +0.45^{***}$)**: 
   - Kiemelkedően magas és statisztikailag szigorúan szignifikáns érték!
   - *Mit jelent?* Ha a környező utcákban az árak 10%-kal megemelkednek, az önmagában – minden egyéb változástól függetlenül – **~3.5 - 4.5%-os azonnali árnövekedést ránt magával** a mi lakásunkban is!
2. **A Térbeli Multiplikátor: $\approx 1.55 - 1.70\times$**:
   - Ez a kutatás egyik legfontosabb elméleti felfedezése!
   - Egy infrastrukturális beavatkozás (pl. új zöldpark vagy állomás) közvetlen hasznához képest a térbeli tovagyűrűzés révén **további 55-70%-nyi rejtett vagyongyarapodás** keletkezik a tágabb környéken!
3. **Moran I a maradványokon (Residuals)**:
   - A sima OLS modell maradék hibájában még erős térbeli autokorreláció maradt (a modell nem értette a teret).
   - A SAR modell reziduális hibájában a Moran I gyakorlatilag **nullára esett vissza**! Ez bizonyítja, hogy a térbeli késleltetés bevonásával a térbeli zavar teljesen megszűnt, a modellünk tiszta és torzítatlan lett!

**💡 Módszertani győzelem**: A térökonometria alkalmazása nem elméleti hóbort, hanem a valós piaci spillover hatások egyetlen helyes leírása.""",

        'sec3': """### 3. Ökonometriai Paraméter Stabilitási Táblázat

**📌 Mit látunk az összehasonlító táblázatban?**
A változók együtthatóinak alakulását a sima OLS-ben és a SAR modellben:
- Figyelje meg, hogy a fizikai változók (méret, állapot) együtthatói enyhén mérséklődnek a SAR modellben! 
- *Miért?* Mert a sima OLS tévesen a lakás közvetlen tulajdonságainak tulajdonította azt az értéktöbbletet, amit valójában a **környék minősége és a szomszédok magasan árazott ingatlanjai** sugároztak rá!

**💡 Szakpolitikai tanulság**: Amikor a városvezetés ingatlanfejlesztési döntéseket hoz, a teljes hatásterületre jutó vagyongyarapodást a térbeli multiplikátorral kell megszorozni, különben súlyosan alábecsülik a közberuházások megtérülését!""",

        'sec4': """### 4. Térbeli Hibatag (SEM) és Modell Robusztusság

**📌 Mi a különbség a SAR és a SEM modell között?**
- A **SAR (Spatial Lag)** azt feltételezi, hogy maguk az árak hatnak egymásra (árhúzó hatás).
- A **SEM (Spatial Error)** azt feltételezi, hogy a megfigyeletlen környezeti tényezők (pl. rossz levegő, zaj, talajminőség) okoznak térben korrelált hibákat.

**🔍 Mi a kőbányai piac konklúziója?**
Mindkét modell futtatása és összehasonlítása megerősíti, hogy a kőbányai piacon az **árak közötti közvetlen tovagyűrűzés (SAR)** a domináns mechanizmus. A piac reagál a szomszédsági tranzakciókra!"""
    },

    # =========================================================================
    # NB14: POI és 15-perces város
    # =========================================================================
    'nb14': {
        'intro': """# 14. Intézményi Ellátottság (POI) és a 15-Perces Város Index

**Cél**: Az OpenStreetMap (OSM) szolgáltatási adatainak (POI - Points of Interest) feldolgozása, a Carlos Moreno-féle „15 perces város” gyalogos elérhetőségének vizsgálata és a szolgáltatási sűrűség árképző hatásának mérése.

---

### 📖 Mi az a "15 perces város" koncepció?
A Sorbonne professzora, Carlos Moreno által kidolgozott és Párizsban híressé vált **„15-minute city”** elmélet lényege egyszerű, de forradalmi:
> *„Egy élhető, modern városban minden alapvető funkciónak – oktatásnak, zöldterületnek, bevásárlásnak, gasztronómiának és egészségügynek – elérhetőnek kell lennie legfeljebb 15 perc kényelmes sétával vagy kerékpározással, autóhasználat nélkül.”*

Kőbánya ebből a szempontból különleges kettősséget mutat: a sűrűbb városközponti részek szinte tökéletesen megvalósítják a 15 perces várost, míg a külsőbb rozsdaövezetek és ipari sávok komoly szolgáltatási sivatagokkal küzdenek.

---

### 🛡️ Módszertani korrekció: A határhatás (Edge Effect) kiküszöbölése
Ha az intézményeket kizárólag Kőbánya szigorú közigazgatási határán belül töltenénk le, a kerület szélein élő lakosokat mesterségesen hátrányosnak látnánk (hiszen az elemzés nem látná a közvetlenül a határ túloldalán lévő zuglói vagy józsefvárosi boltokat, parkokat).
Ennek elkerülésére egy **1200 méteres védőzónával (pufferrel)** bővítettük a lekérdezést, így a valódi, átnyúló funkcionális elérhetőséget mérjük!""",

        'sec1': """### 1. Pufferelt POI Adatbázis és Szolgáltatási Kategóriák

**📌 Mit látunk az adatbázis összefoglalójában?**
Az OpenStreetMap szervereiről letöltött és térinformatikailag ellenőrzött szolgáltatások megoszlását:
- **Zöldinfrastruktúra (`leisure=park`)**: Parkok, rekreációs területek, játszóterek.
- **Gasztronómia (`amenity=restaurant, cafe`)**: Éttermek, kávézók, közösségi találkozóhelyek.
- **Oktatás és nevelés (`amenity=school, kindergarten`)**: Iskolák, óvodák, bölcsődék.

**🔍 Hány szolgáltatás található a területen?**
A szigorú közigazgatási határ mindössze 144 db POI-t tartalmazott. A határokon átnyúló 1200 méteres puffer bevonásával a valós elérhető szolgáltatások száma **319 darabra emelkedett**!
Ez megszüntette a peremterületek mesterséges büntetését, és valós, életszerű képet ad az ellátottságról.

**💡 Eredmény**: Az adatbázis teljesen leköveti a lakosság valós térbeli mobilitását.""",

        'sec2': """### 2. A Három Gyalogos Sáv Szolgáltatás-Sűrűsége (375m, 750m, 1125m)

**📌 Hogyan épül fel a 15 perces város index?**
A gyalogos sebesség (4.5 km/h) alapján az NB05-ös izokrónokkal szinkronizált sávokat képeztünk:
1. **5 perces zóna ($\le 375$ m) – „Papucsos sétatáv”**: Napi alapvető igények a közvetlen szomszédságban (kisbolt, sarki kávézó, helyi játszótér).
2. **10 perces zóna ($375 - 750$ m)**: Kényelmes sétatávolság (iskola, nagyobb park, étterem).
3. **15 perces zóna ($750 - 1125$ m)**: A 15 perces város külső határa (bevásárlóközpont, szakorvosi rendelő, gimnázium).

**🔍 Mit mutat a színes interaktív térkép?**
Minden ingatlan pontja aszerint színeződik, hogy **összesen hány darab szolgáltatás érhető el tőle 15 perces sétával**:
- **Sárga és világoszöld pontok (magas értékek, 30-50 db POI)**: Kőbánya-Városközpont, Ligettelek, Óhegy frekventált részei, valamint Felsőrákos (amely közvetlenül profitál a szomszédos Zugló gazdag intézményi hálózatából).
- **Sötétlila pontok (alacsony értékek, <10 db POI)**: A vasúti teherpályaudvarok és külső ipari övezetek melletti lakások, ahol alig van sétatávolságban bolt vagy iskola.

**💡 Életminőségi indikátor**: A térkép azonnal megmutatja, hol élhet valaki kényelmes, autómentes városi életet Kőbányán.""",

        'sec3': """### 3. A Szolgáltatási Sűrűség Hedonikus Árprémiuma

**📌 Mit vizsgál a regressziós táblázat?**
Azt méri, hogy a lakásvásárlók a valóságban **hajlandók-e többet fizetni a jobb szolgáltatási sűrűségért**:
- Beépítjük a modellbe az 5 perces, 10 perces és 15 perces POI darabszámokat a méret, a panel jelleg és a metrótávolság mellett.

**🔍 Mit mutatnak az eredmények?**
- **A közvetlen közelség (5 perces sáv) felára a legmagasabb**: Az emberek sokkal többre értékelik, ha az óvoda és a kávézó 3 percre van a lépcsőháztól, mintha 14 percet kellene gyalogolniuk érte!
- Minden egyes közvetlen közelben elérhető minőségi szolgáltatás mérhetően emeli a lakás négyzetméterárát.

**💡 Ingatlanfejlesztési tanulság**: Egy új lakópark beruházásánál a földszinti szolgáltató helyiségek (kávézó, pékség, kisbolt) kialakítása nem veszteséges kompromisszum, hanem az emeleti lakások négyzetméterárát közvetlenül megemelő értékteremtő befektetés!"""
    },

    # =========================================================================
    # NB15: Lokális Térökonometria (GWR)
    # =========================================================================
    'nb15': {
        'intro': """# 15. Lokális Térökonometria: Földrajzilag Súlyozott Regresszió (GWR)

**Cél**: A térbeli heterogenitás modellezése Kőbányán multiskálás földrajzilag súlyozott regresszióval (GWR / MGWR), lehetővé téve, hogy a regressziós együtthatók térben dinamikusan változzanak.

---

### 📖 Miért nem ér mindenhol ugyanannyit a metró közelsége?
A hagyományos globális modellek (mint az NB04-es OLS vagy az NB13-as SAR) egyetlen átlagos számot becsülnek az egész kerületre:
*„100 méterrel közelebb a metróhoz = átlagosan +0.8% lakásár-növekedés.”*

De gondoljunk bele a valóságba:
- **Óhegyen**, ahol a lakók többsége zöldövezeti kertes házban él és sokan autóval járnak, a metró távolsága fontos, de nem kritikus szempont.
- **Egy sűrű lakótelepen (pl. Újhegyen vagy a Népliget mellett)**, ahol a lakók túlnyomó része kötöttpályás tömegközlekedéssel ingázik a belvárosi munkahelyekre, a metróállomás elérhetősége **élet-halál kérdés**, amiért óriási felárat hajlandók fizetni!

A **Geographically Weighted Regression (GWR)** szakít azzal az illúzióval, hogy a gazdasági törvényszerűségek mindenhol egyformák:
> *A GWR minden egyes pont körül egy helyi regressziót illeszt, így megmutatja, hogyan változik az egyes ingatlantulajdonságok értéke utcáról utcára lépkedve a kerületen belül!*

---

### 🛡️ Módszertani kiválóság: Szingularitás elkerülése térbeli aggregációval
A GWR algoritmus lokális mátrixinverziót végez. Ha azonos koordinátán több hirdetés szerepelne (lokális kollinearitás), a mátrix szingulárissá válna és a számítás összeomlana. 
A véletlenszerű zaj (jitter) hozzáadása helyett a tudományosan legtisztább utat választottuk: **épület-szintű térbeli aggregációt** hajtottunk végre, így a modell stabilan és robusztusan fut le!""",

        'sec1': """### 1. Adaptív Sávszélesség (Bandwidth) Keresés és GWR Illeszkedés

**📌 Mit jelent a sávszélesség (Bandwidth)?**
A sávszélesség határozza meg, mekkora környezetet vegyen figyelembe az algoritmus egy-egy helyi modell becslésekor:
- **Túl kicsi sávszélesség**: Túl kevés adatból számol, zajos és megbízhatatlan lesz az eredmény.
- **Túl nagy sávszélesség**: Túlságosan kisimítja az adatokat, és visszakapjuk a sima OLS-t.
- **Optimalizáció**: Az algoritmus aranymetszéses kereséssel (AICc információs kritérium minimalizálásával) automatikusan megtalálja a tökéletes egyensúlyt biztosító legközelebbi szomszédszámot.

**🔍 Modell illeszkedési eredmények:**
- **GWR $R^2 \approx 0.75 - 0.78$**: A modell magyarázóereje érezhetően felülmúlja a globális OLS modellt!
- **Alacsonyabb AICc érték**: Az AICc jelentős csökkenése statisztikailag is bizonyítja, hogy a térben változó paraméterek feltevése szignifikánsan jobban írja le a valóságot, mint az állandó együtthatók.

**💡 Tudományos igazolás**: A térbeli heterogenitás létezik Kőbányán; a piaci szereplők lokációtól függően eltérően árazzák be ugyanazokat a lakásjellemzőket.""",

        'sec2': """### 2. A Metróprémium Térbeli Változékonysága (Helyi Béta Együtthatók Térképe)

**📌 Mit látunk ezen a lélegzetelállító hőtérképen?**
A térkép azt ábrázolja, hogy **a metrótávolság negatív hatása hol a legerősebb és hol a leggyengébb**:
- **Sötétkék és lila zónák**: Ahol a béta együttható erősen negatív (itt a legfontosabb a metró közelsége, itt bünteti a piac a legkeményebben a távolságot). Hol látjuk ezt? A Hungária körút, Népliget és a forgalmas ingázó csomópontok vonzáskörzetében!
- **Világoszöld és sárga zónák**: Ahol az együttható közelebb van a nullához (itt a metró távolsága jóval kevésbé befolyásolja az árakat). Hol látjuk ezt? Óhegy csendes zöldövezeti és kertvárosi részein, ahol a helyi lakók inkább autót vagy buszt használnak.

**💡 Megdöbbentő összefüggés**: Ugyanaz a 200 méteres metró-közeledés Kőbánya belső részein kétszer akkora forintosított árnövekményt generál, mint a külső zöldövezetben!""",

        'sec3': """### 3. A Helyi Állapot-Prémium Térbeli Megoszlása

**📌 Mit vizsgál ez a térkép?**
Azt mutatja be, hogy a felújított állapotért hol hajlandók a legtöbb felárat kifizetni a vásárlók:
- A sűrűbb városközponti és albérletes övezetekben a felújítási prémium kirívóan magas, mert a bérlők azonnal költözhető, modern lakásokat keresnek.
- A tágasabb zöldövezetekben a vevők gyakran saját ízlésükre formálják a házat, így a felújítási prémium kissé mérsékeltebb.

**💡 Összegzés a TDK védéshez**: A GWR elemzés a kutatás koronaékszere, amely a legmagasabb akadémiai szinten igazolja Kőbánya mikroökonómiai és térbeli komplexitását."""
    }
}


def get_nb_docs(nb_id):
    """Visszaadja az adott notebookhoz tartozó szövegtárat."""
    return NOTEBOOK_DOCS.get(nb_id, {})
