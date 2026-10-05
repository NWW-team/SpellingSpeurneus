# Overdracht

Wat een volgende sessie of collega moet weten om hier verder te kunnen.
Voor hoe de app werkt: zie [README.md](README.md). Voor het waarom:
[STRATEGY.md](STRATEGY.md).

Laatst bijgewerkt: 15 september 2026.

## Stand van zaken

De app werkt en staat op https://nww-team.github.io/SpellingSpeurneus/.
Alle zes acceptatiecriteria uit het bouwplan zijn gehaald:

| Criterium | Uitkomst |
|---|---|
| Crawl van 50 pagina's binnen 10 minuten | 80 seconden |
| ~~Collega zonder account ziet de resultaten~~ | **Met opzet omgedraaid, zie besluit 3** |
| De drie ingebouwde fouten in `demo/` worden gevonden | 3 van 3 |
| Een woord op de uitzonderingenlijst verdwijnt | Vastgelegd in de controles |
| robots.txt wordt gevolgd, herkenbare User-Agent | Getoetst tegen de echte site |
| Geen sleutels of wachtwoorden in de repo | Er zijn er ook geen nodig |

Op 50 reisadviespagina's vond de app **acht echte redactionele fouten**:
`nieet`, `Registeer`, `doodstaf`, `metrologisch`, `doen.n`, `III.Let`,
`demonstraties.Volg` en `autorisation`.

Bij de crawl van 15 september staan er nog **zeven** van: `doodstaf` is van de
pagina `reisadvies/congo-de-republiek` verdwenen, terwijl die pagina wel
opnieuw is gecrawld. Daar is dus iets gerepareerd. Dat is de eerste keer dat
aantoonbaar een melding van deze app tot een correctie heeft geleid — of in
elk geval dat een gemelde fout weg is.

Die crawl gaf 613 bevindingen (41 spelfouten, 572 namen, 315 uniek) tegen 614
op 14 september. De site wijzigt dus tussen crawls; reken niet op exact
gelijke aantallen.

Sinds besluit 1 staan die acht in een lijst van 42 meldingen in plaats van 614:
namen zijn naar een tweede tabblad verhuisd. Zie "Spelfouten en namen" in
[README.md](README.md) voor de regel, en `soort_van` in `scripts/crawl.py` voor
de code.

## Alle 226 reisadviezen (15 september)

3.376 bevindingen: **427 spelfouten en 2.949 naammeldingen** (1.398 unieke
namen), over 226 pagina's in 4 min 47 s. Besluit 1 houdt stand op 4,5× de
steekproef: 87% van de meldingen gaat naar het namentabblad.

**24 echte redactionele fouten**, stuk voor stuk in hun zin nagekeken. Naast de
zeven bekende: `plaatvinden`, `prvincie`, `meenenemen`, `veiilgheidsrisico's`,
`veiligsheidsrisico's`, `motorvoortuigen`, `niet-Ecudoraans`, `Vor`, `vande`,
`ZDe`, `zoalsCruz`, `visumnodig`, `doenals`, `Bijvoorbeeldc`, `invullen.n`,
`aardbevingcentrum` en `undefined`.

Twee daarvan zijn geen spelfout maar iets anders, en die horen bij de
sitebeheerder in plaats van bij de redactie:

- **`undefined` staat letterlijk boven aan `reisadvies/estland`.** Dat is een
  sjabloonfout in het CMS die zichtbaar is voor bezoekers.
- Op `reisadvies/mali` staat "opgenomen in het ziekenhuisopname". Grammatica
  vangt deze app niet; dit kwam boven water naast de tikfout `Bijvoorbeeldc`.

### Let op bij het lezen van de ruiscijfers

De 0,84 valse meldingen per pagina uit de eerste crawl was geflatteerd.
`data/uitzonderingen.txt` is op 14 september in twee rondes gevuld met precies
de ruis van díé 50 pagina's (zie de commits "Ruis wegnemen na de eerste echte
crawl" en "Tweede ronde ruis"). De 176 pagina's die daarna voor het eerst
langskwamen gaven **2,19 per pagina**.

Reken dus met ~2,2 per ongeziene pagina, niet met 0,84. Elke nieuwe crawl over
onbekend terrein begint hoog en zakt zodra de uitzonderingenlijst is
bijgewerkt. Dat is geen fout in de app; het is de aard van zo'n lijst.

De derde ronde uitzonderingen (30 woorden, 15 september) haalt 87 van de 427
meldingen weg. Niet meer, omdat de Engelse woorden — het grootste blok, 81
meldingen — er bewust buiten blijven.

**Bevestigd door de tweede crawl van 15 september (12:25):** 340 spelfouten
(255 unieke woorden) en 2.946 naammeldingen. Precies de voorspelde 427 − 87.
Alle 24 echte fouten staan er nog — nagekeken, want een uitzondering die per
ongeluk een echte fout wegneemt, merk je anders pas als iemand hem mist.

De sjabloondetectie vond in die crawl één rest: de al bekende `undefined` op
Estland. Geen `[object Object]` of `{{titel}}` op de reisadviezen. Het is dus
verzekering geworden, geen vondst; op de 4.436 `paginas` kan dat anders liggen.

Reken niet op exact gelijke aantallen tussen crawls: 2.946 namen tegen 2.949
's ochtends. De site verandert gewoon tussendoor.

## Wat er nu ligt

Drie dingen, geen van alle techniek. Dit is wat er moet gebeuren voordat dit
project iets heeft opgeleverd in plaats van alleen iets te hebben gevonden.

**1. De 24 fouten naar de webredactie.** Dit is het enige stuk dat nog een mens
nodig heeft om waarde op te leveren: de app heeft ze gevonden, maar niemand
heeft ze gecorrigeerd. Zonder deze stap heeft de hele crawl niets veranderd
aan de website.

De woorden staan hierboven. Wie ze per land wil zien, mét de zin en een link
naar de pagina: dat is precies het spelfoutentabblad in de app zelf. De
bevindingen staan bewust niet in deze repository (besluit 3), dus er is geen
lijst om hier in te plakken — je haalt hem uit het scherm.

**2. `undefined` op `reisadvies/estland` naar de sitebeheerder.** Dat is geen
tikfout maar een sjabloonfout in het CMS, zichtbaar voor bezoekers. Hoort niet
bij de redactie thuis. Laat meteen nakijken of het op meer pagina's voorkomt —
wij zien alleen de reisadviezen.

**3. Besluit 2 (de sitebeheerder inlichten) is dringender geworden.** Op 15
september zijn er twee volledige crawls van 226 pagina's overheen gegaan. Dat
staat netjes in hun logboek, met onze User-Agent erbij, en het is beter dat ze
het van ons horen dan dat ze het zelf ontdekken. Zeker als er ooit een crawl
over de 4.436 `paginas` komt: dat is ruim twee uur aanhoudend verkeer. (Sinds 5 oktober zijn de delen kleiner: de grootste, `/visum-nederland`, is ±1.015 pagina's.)

## Genomen besluiten

**1. De eigennamen — gescheiden, niet weggegooid.** (14 september 2026)

Van de 614 meldingen waren er 573 een plaatsnaam, organisatie of anderstalige
bronnaam middenin een zin. Drie dingen gaven de doorslag:

- In die 573 zat **geen enkele verkeerd gespelde plaatsnaam**. Alle acht echte
  fouten waren gewone woorden. De prijs van doorzoeken was gemeten, de
  opbrengst bleef theoretisch.
- De app kán een foute plaatsnaam niet herkennen: OpenTaal bevat geen namen,
  dus `Cochabamba` en een verkeerd gespelde variant krijgen dezelfde melding.
  Ze allemaal melden levert de redacteur dus geen signaal op — hij zou ze
  stuk voor stuk moeten natrekken.
- Er bleek geen uit te leggen middenweg. Filteren op frequentie haalde maar
  161 van de 614 weg; filteren op naamreeksen (`USGS Earthquake Hazards
  Program`) liet losse correcte plaatsnamen in opsommingen gewoon staan.

Gekozen is niet voor een schakelaar per crawl maar voor **twee lijsten in
hetzelfde resultaat**, met spelfouten open bij binnenkomst. Namen staan er
ontdubbeld (315 in plaats van 573) met het aantal pagina's erbij, dus ze
blijven na te lopen. De indeling staat per bevinding in de kolom `soort`,
dus de keuze is terug te draaien zonder opnieuw te crawlen.

Wat toen nog niet was besloten, is sinds 2 oktober wel geregeld: de redactie kan namen
(en woorden) in het scherm goedkeuren, zie besluit 6. Het namentabblad krimpt daarmee per
crawl tot alleen nieuwe namen. Wie dat bijhoudt, is nog niet aangewezen.

**3. De bevindingen gaan achter een inlog.** *(teruggedraaid door besluit 6)* (15 september 2026)

Dit was het openstaande besluit hieronder; nu beslist. De resultaten stonden als
`docs/resultaten.json` in deze publieke repository en op de Pages-link. Ze zijn
een werklijst van de redactie, dus ze horen niet openbaar.

Ze staan nu in Supabase, met row level security en een allowlist. **Let op wat
dit wel en niet doet:** het schermt de gegevens af, niet het scherm. `docs/`
staat op GitHub Pages in een publieke repository en blijft voor iedereen op te
vragen. Een inlogformulier in een statisch bestand is geen toegangscontrole; die
zit in de policies. Zie "Toegang" in [README.md](README.md).

Hiermee vervalt het tweede acceptatiecriterium uit het bouwplan ("collega zonder
account ziet de resultaten"). Dat was een bewuste keuze en geen regressie: zonder
account zie je nu het inlogformulier. Wie het oude gedrag terug wil, moet besluit
3 heropenen.

Wat nog niet is opgelost: `docs/resultaten.json` zit nog in de git-geschiedenis en
is daar publiek leesbaar. Het bestand is verwijderd, de geschiedenis niet
herschreven. Het gaat om al openbare citaten, dus het is bewust zo gelaten — maar
het is een keuze, niet een oplossing.

**6. De inlog gaat weer weg.** (2 oktober 2026)

Besluit 3 is teruggedraaid op verzoek van de redactie. Er is geen inlogscherm meer en
de bevindingen zijn leesbaar voor iedereen met de publishable key, die in
`docs/index.html` en dus in een publieke repository staat. De pagina is bereikbaar via
een link die niet wordt aangekondigd, maar dat is **geen toegangscontrole**: wie de
repository leest, vindt de link en de key.

Dit is bewust zo gekozen, met het risico erbij. De migratie staat in
`supabase/migrations/20261002000000_open_lezen.sql`. Daarmee vervallen besluit 4 en 5
(pagina privé, beheer van de allowlist). De tabel `toegestane_gebruikers` en de functie
`is_toegestaan()` blijven staan, ongebruikt, tot iemand ze opruimt.

Gevolg: goedkeuren en een crawl starten schrijven vanuit een open pagina. Ze lopen daarom
via een Edge Function met limieten, en elke goedkeuring is terug te draaien en vastgelegd.

**Let op bij RLS (2 oktober).** Een policy alleen is niet genoeg: de rol heeft ook het
recht op de tabel nodig (`grant select`). Stap 1 zette alleen policies, waardoor het scherm
"permission denied for table crawls" gaf tot het recht voor `anon` erbij kwam
(`20261002040000_rechten.sql`). Controleer na een nieuwe tabel altijd beide: de policy én de
grants, en toets als `anon` (`set local role anon`) in plaats van alleen te lezen wat er staat.

**Crawl starten (2 oktober).** Knop in het scherm, Edge Function `crawl-starten`, tabel
`crawl_aanvragen` (migratie `20261002020000_crawl_aanvragen.sql`): één crawl per dag, afgedwongen
door een unieke index. Het token staat als Supabase-secret `GITHUB_TOKEN` (fine-grained, alleen
*Actions: read and write* op deze repository). **Risico:** iedereen met de publieke key kan
de dagelijkse crawl "opmaken", bijvoorbeeld met een grote bron, of de redactie ervan afhouden.
Een crawl over `paginas` is ruim twee uur aanhoudend verkeer naar de site; zie besluit 2.

**Geen maximumaantal pagina's meer (5 oktober).** Het veld is uit het scherm gehaald: een crawl pakt
altijd het hele gekozen deel. De Edge Function `crawl-starten` zet het aantal zelf op de grens van
5000 (boven het grootste deel, ±1.015) en negeert een aantal in het verzoek; de kolom
`crawl_aanvragen.max_paginas` blijft bestaan en staat dus altijd op 5000. De knop "Run workflow" in
GitHub heeft het veld nog, met standaard 50: wie die gebruikt, moet het zelf verhogen.

**Delen van de site (5 oktober).** De keuzelijst is nu: Reisadviezen (`/reisadvies`), Visum voor
Nederland (`/visum-nederland`), Visum voor Caribische Koninkrijksdelen (`/caribisch-visum`) en
Ambassades en consulaten (`/contact/ambassades-consulaten-generaal`), telkens met alles daarachter.
"Overige pagina's" (`paginas`) is geen keuze meer. De visumpagina's staan in de grote
`paginas`-sitemap, dus een deel is een pad-voorvoegsel over alle sitemaps samen (`DELEN` in
`crawl.py`). Gevolg: Reisadviezen telt nu 236 pagina's (de 226 landen plus tien overzichtspagina's
uit de grote sitemap) en begint met die overzichtspagina's. Een crawl over een deel waar de site
geen enkele URL meer voor heeft, stopt met een foutmelding. Migratie
`20261002070000_delen_van_de_site.sql`.

**De spellingtoets is alleen op reisadviezen geijkt.** Op visumpagina's (veel formulieren,
afkortingen en landnamen) kan de ruis anders liggen: reken bij de eerste crawls op veel valse
meldingen, en loop ze door met de redactie voordat je de aantallen vertrouwt. Een crawl over
`/visum-nederland` is ruim een kwartier verkeer naar de site (1015 pagina's); zie besluit 2.

**Plaatsnamen (2 oktober).** Elke naam krijgt een oordeel uit GeoNames (`scripts/plaatsnamen.py`,
migratie `20261002060000_plaatsnamen.sql`): `bekend`, `twijfel` (lijkt op een bekende plaats,
met suggestie) of `onbekend`. Alleen buitenland, zoals gekozen. Het matchen is Damerau-
Levenshtein met de grens 1 fout (woorden van 5 tot 8 letters) of 2 (vanaf 9 letters); woorden
korter dan 5 letters krijgen geen suggestie. Suggesties komen alleen uit plaatsen vanaf 15.000
inwoners, regio's en landen; "bekend" telt alle plaatsen vanaf 1000 inwoners, met alle
alternatieve namen. Het scherm zet de twijfelgevallen bovenaan en heeft een keuzelijst per groep.

**Nog niet gemeten op echte data.** De sandbox waarin dit is gebouwd mag
`download.geonames.org` niet bereiken, dus de drempels zijn getoetst op een nagemaakt bestand
in het GeoNames-formaat en op willekeurige data (snelheid: 140.000 plaatsen laden duurt 5
seconden, 1500 namen beoordelen 16 seconden, 156 MB). Na de eerste echte crawl met deze versie
staat in het logboek van de stap "Crawlen en spelling toetsen" een regel `Plaatsnamen (unieke
namen): …` met de eerste 40 twijfelgevallen. **Kijk die na** voordat je de uitkomst vertrouwt:
- te veel valse twijfel (gewone Engelse of Spaanse woorden die op een plaats lijken, zoals
  `Health` ~ `Heath`)? Verhoog `MIN_INWONERS_SUGGESTIE` of verlaag `toegestane_afstand`;
- echte tikfouten die niet worden gevonden? Verlaag de drempel van 5 letters, of laat de eerste
  letter ook mogen verschillen (nu moet die gelijk zijn).

Bekende beperking: een naam die alleen in het buitenland bestaat maar op de pagina een andere
plaats bedoelt, valt niet op. En `Cordoba` naast `Córdoba` zijn beide "bekend": een verschil
in accenten tussen pagina's meldt de app niet.

**Eén lijst (2 oktober).** `data/uitzonderingen.txt` (280 woorden) is in `goedgekeurd` ingeladen
(`20261002050000_uitzonderingen_importeren.sql`) en uit de repository gehaald. De crawler leest
alleen nog Supabase en de run stopt als dat ophalen mislukt. De toelichting uit het bestand,
voor wie een woord wil nalopen:

- **Rondes.** Eerste en tweede ronde (14 september) haalden de ruis van de eerste 50 reisadviezen
  weg; de derde ronde (15 september) alleen woorden die op meer dan één reisadvies voorkwamen:
  woorden van één pagina bleven bewust staan, want daar zitten de echte tikfouten. De vierde en
  vijfde ronde kwamen van de redactie.
- **Huisstijl.** `lhbtiq+` altijd met de plus; zonder plus is het fout en meldt de app dat. `mpox`
  en `apenpokken` staan allebei erin omdat de site beide gebruikt ("Mpox-virus (apenpokken)").
- **Engelse en andere vreemde woorden** zoals `and`, `for`, `travel`, `female`, `control` zijn
  op 15 september door de redactie goedgekeurd. Gevolg: ze vallen nergens meer op, ook niet los
  in een Nederlandse zin. Voor vergelijkbare nieuwe gevallen geldt nog steeds: goedkeuren betekent
  dat zo'n woord middenin een Nederlandse zin nooit meer opvalt; dat is aan de redactie.
- **`etc`** is goed: de zinsopdeling haalt de laatste punt van "etc." weg. `o.a.` valt buiten
  de lijst, omdat die maar op één pagina stond.
- `motodop` werd op 15 september verwijderd en op uitdrukkelijk verzoek van de redactie weer
  toegevoegd.

**Goedkeuren (2 oktober).** Tabel `goedgekeurd` (migratie
`20261002010000_goedgekeurd.sql`), Edge Function `goedkeuren` (maximaal 300 wijzigingen per
uur, `verify_jwt = false`). De workflow haalt de lijst vlak voor de crawl op
(`scripts/haal_goedgekeurd.py`); lukt dat niet, dan crawlt hij door zonder. Een goedgekeurde
naam wordt overal toegelaten, ook aan het zinsbegin. **Risico:** iedereen met de publieke key kan
woorden goedkeuren en zo echte fouten uit beeld halen. Terugdraaien kan, en niets wordt
verwijderd, maar controleer het tabblad Goedgekeurd af en toe.

## Openstaande besluiten

**2. De sitebeheerder inlichten.** `robots.txt` van
www.nederlandwereldwijd.nl staat crawlen toe, en we houden ons aan de
verboden paden, een halve seconde tussen pagina's en een herkenbare
User-Agent. Toch is het netjes om de beheerder te laten weten dat dit
draait. Dat is nog niet gebeurd — zie punt 3 onder "Wat er nu ligt": er zijn
inmiddels twee volledige crawls van 226 pagina's overheen gegaan.

**4. Moet de pagina zelf ook privé?** Besluit 3 schermt de gegevens af, niet
het scherm. Wil je dat een onbevoegde de pagina helemaal niet kan openen, dan
kan GitHub Pages dat niet: het levert statische bestanden uit zonder enige
voorwaarde, en Pages met beperkte zichtbaarheid bestaat alleen bij GitHub
Enterprise Cloud met een privérepo. Dan is andere hosting nodig — bijvoorbeeld
Cloudflare Access ervoor, of het scherm laten uitleveren door een Edge Function
die eerst de sessie controleert. Nog niet nodig geacht, wel goed om te weten
voordat iemand aanneemt dat de hele site dicht zit.

**5. Wie beheert de allowlist?** Iemand moet accounts aanmaken en op
`toegestane_gebruikers` zetten, en eraf halen als iemand weggaat. Dat is nu
niemand. Hoort bij dezelfde eigenaar als de uitzonderingenlijst.

Besluit 3 werd op 15 september scherper doordat het scherm de kleuren van
de Rijkshuisstijl kreeg. Logo, woordmerk en het Rijksoverheid-lettertype zitten er
bewust níét in, juist om te voorkomen dat een publieke pagina voor een
officiële pagina van de Rijksoverheid wordt aangezien. Wie de vormgeving
verder officieel wil maken, moet dit eerst met de huisstijlbeheerder bij BZ
afstemmen. Zie "Vormgeving" in [README.md](README.md). Dat de pagina zelf publiek
blijft (besluit 4) maakt dit punt niet kleiner.

## Bekende beperkingen

- **Uitloggen trekt een al uitgegeven token niet in.** Getoetst over HTTP: na een
  `logout`-verzoek (dat netjes 204 teruggeeft) blijft hetzelfde access token nog
  werken en levert het gewoon de bevindingen op. Dat is hoe JWT's werken —
  PostgREST controleert de signatuur zelf en kijkt niet of de sessie nog bestaat.

  Wat dit **niet** betekent: dat uitloggen niet werkt. De browser gooit het token
  weg, dus de app kan na uitloggen niets meer ophalen; dat is getoetst. Wat het
  **wel** betekent: wie het token vóór het uitloggen uit de browser heeft
  gekopieerd, kan daarmee nog tot een uur lezen. De levensduur is 3600 seconden.

  Wil je dat venster kleiner, dan kan de access-tokenlevensduur omlaag in
  Authentication → Sessions in het dashboard. Korter betekent vaker verversen.
  Voor een werklijst met citaten uit openbare pagina's is een uur verdedigbaar;
  voor iets vertrouwelijkers niet.

- **`persoons-` uit "persoons- en bagagecontrole"** wordt getoetst als
  `persoons`, en dat is geen los woord. Bij een weglatingsstreepje valt niet
  vast te stellen wat het hele woord had moeten zijn.
- **Anderstalige woorden zonder hoofdletter** blijven bij de spelfouten
  staan: `and` uit "US Customs and Border Protection", `viajeros` uit "Para
  viajeros", `floods`, `travel`. Over alle 226 reisadviezen zijn dit 81 van de
  427 spelfoutmeldingen — veruit de grootste rest-ruis, met `and` (34×) voorop.
  Ze stonden bewust niet op de lijst met goedgekeurde woorden en vallen bewust niet
  onder de naam-regel. Ze goedkeuren zou betekenen dat een Engels woord middenin een Nederlandse zin
  nooit meer opvalt, en dat kostte bijna de vondst van `autorisation`.
- **Alleen de tekst in `<main>`** wordt gelezen. Menu's, voetteksten en
  cookiemeldingen blijven buiten beeld. Verandert de site van structuur, dan
  is dit de aanname die als eerste breekt.
- **Eén taal.** De paginasitemap bevat geen anderstalige pagina's; komen die
  er wel, dan meldt de app ze als één grote fout.

## Werken in Claude Code op het web

De codeeromgeving heeft **beperkte netwerktoegang**. Dit is geen storing
maar beleid, en het kost tijd als je het niet weet:

| Wel bereikbaar | Niet bereikbaar |
|---|---|
| www.nederlandwereldwijd.nl | github.com en raw.githubusercontent.com |
| De Supabase Management API (via MCP) | nww-team.github.io (de eigen Pages-link) |
| | de project-URL `*.supabase.co` en poort 5432 |
| | npm, PyPI en cdn.jsdelivr.net |

Gevolgen:

- De OpenTaal-woordenlijst kun je **niet lokaal downloaden**. Draai
  `scripts/crawl.py` lokaal en hij valt terug op `data/woordenlijst-demo.txt`,
  een testlijst van ruim honderd woorden die alleen voor `demo/` deugt. De
  echte spellingtoets draait alleen in de workflow.
- De Pages-link kun je **niet zelf controleren**. Dat moet iemand in een
  gewone browser doen.
- `scripts/crawl.py`, `scripts/test.py` en `scripts/publiceer.py` gebruiken daarom
  alleen de standaardbibliotheek van Python. Houd dat zo.
- **Inloggen is hier niet te testen.** `*.supabase.co` is onbereikbaar en
  supabase-js komt van een CDN dat ook dicht staat. Het schema en de policies
  zijn wel te toetsen via MCP, met `set role` en een nagebootst
  `request.jwt.claims`. De frontend-logica is te toetsen door supabase-js te
  vervangen door een nagemaakte cliënt en `docs/index.html` in Chromium te
  laden. Het echte inloggen moet iemand in een gewone browser doen.
- Chromium staat wel voorgeïnstalleerd op
  `/opt/pw-browsers/chromium-1194/chrome-linux/chrome` en is bruikbaar met
  `--headless --dump-dom` om `docs/index.html` echt in een browser te testen.

## Ontwerppunt: opgelost

`docs/resultaten.json` stond in de repository en werd door de workflow
teruggeschreven. Dat botste zodra er op twee branches een crawl draaide — dat
gebeurde op 14 september en leverde een merge-conflict op.

Dat is met besluit 3 verdwenen: het resultaat gaat nu naar Supabase in plaats
van de repository in. Elke crawl maakt een nieuwe rij in `crawls` met zijn eigen
bevindingen; het scherm toont de nieuwste. Twee crawls botsen dus niet meer, en
de workflow heeft geen schrijfrecht op de repository meer nodig.

Wat er voor terugkomt: oude crawls blijven staan en worden nooit opgeruimd. Bij
tienduizenden bevindingen per crawl is dat iets om naar te kijken.

## Beheer

**De app heeft een eigenaar nodig bij de webredactie** — de persoon uit
STRATEGY.md die de kwaliteit van de website bewaakt. Zonder eigenaar
verdwijnt zo'n prototype.

Twee dingen zijn licht, maar wel echt werk:

- **De allowlist en de accounts.** Wie mag de resultaten zien? Accounts maak je
  aan in het Supabase-dashboard en zet je daarna op `toegestane_gebruikers`.
  Gaat iemand weg, dan moet hij eraf. Zie besluit 5.
- **De lijst met goedgekeurde woorden** (tabel `goedgekeurd`, tabblad Goedgekeurd) groeit
  met elk vals alarm en hoort bij de redactie, niet bij de techniek. Er staan
  huisstijlkeuzes in, zoals dat NederlandWereldwijd altijd `lhbtiq+` schrijft.
  Wie daar een woord aan toevoegt, beslist wat "goed" is.
- **Iemand start de crawl** wanneer dat nodig is. Er gebeurt niets vanzelf.

**Voordat collega's hierop kunnen vertrouwen:**

1. ~~Het percentage vals alarm over meer dan 50 pagina's~~ — gemeten op alle
   226 reisadviezen: 24 echte fouten op 427 spelfoutmeldingen, ofwel één op de
   18. Dat is na te lopen, maar minder gunstig dan de één-op-vijf van de eerste
   crawl deed vermoeden; zie "Let op bij het lezen van de ruiscijfers".
   Wat nog open staat: de hoofdletterregel is **alleen op reisadviezen geijkt**.
   Een plak van ~200 `paginas` (visum, paspoort, consulair) moet laten zien of
   hij op ander taalgebruik net zo goed uitpakt.
2. Afspraak met de beheerder van de website (besluit 2).
3. ~~Besluit over publiek publiceren~~ — genomen, zie besluit 3.
4. Iemand die het onderhoudt als de website van structuur verandert.
5. Iemand die de accounts en de allowlist beheert (besluit 5).

## Wat er bewust niet in zit

Grammatica, stijl en d/t-fouten · alle 4.660 pagina's in één run · continu of
gepland scannen · meerdere talen · terugschrijven naar het CMS · **rollen of
rechten per gebruiker** (toegang is alles of niets) · zelf aanmelden ·
wachtwoord vergeten ·  bevindingen bewaren om
trends over tijd te zien · afgeschermde of interne pagina's.

Inloggen zat tot 15 september in dit lijstje. Zie besluit 3.
