# Overdracht

Wat een volgende sessie of collega moet weten om hier verder te kunnen.
Voor hoe de app werkt: zie [README.md](README.md). Voor het waarom:
[STRATEGY.md](STRATEGY.md).

Laatst bijgewerkt: 14 september 2026.

## Stand van zaken

De app werkt en staat op https://nww-team.github.io/SpellingSpeurneus/.
Alle zes acceptatiecriteria uit het bouwplan zijn gehaald:

| Criterium | Uitkomst |
|---|---|
| Crawl van 50 pagina's binnen 10 minuten | 80 seconden |
| Collega zonder account ziet de resultaten | Bevestigd in een privévenster |
| De drie ingebouwde fouten in `demo/` worden gevonden | 3 van 3 |
| Een woord op de uitzonderingenlijst verdwijnt | Vastgelegd in de controles |
| robots.txt wordt gevolgd, herkenbare User-Agent | Getoetst tegen de echte site |
| Geen sleutels of wachtwoorden in de repo | Er zijn er ook geen nodig |

Op 50 reisadviespagina's vond de app **acht echte redactionele fouten**:
`nieet`, `Registeer`, `doodstaf`, `metrologisch`, `doen.n.`, `III.Let`,
`demonstraties.Volg` en `autorisation`.

Sinds besluit 1 staan die acht in een lijst van 42 meldingen in plaats van 614:
namen zijn naar een tweede tabblad verhuisd. Zie "Spelfouten en namen" in
[README.md](README.md) voor de regel, en `soort_van` in `scripts/crawl.py` voor
de code.

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
blijven na te lopen. De indeling staat per bevinding in `resultaten.json`,
dus de keuze is terug te draaien zonder opnieuw te crawlen.

Wat nog niet is besloten: of de redactie een **lijst met goedgekeurde namen**
wil gaan bijhouden, zoals `uitzonderingen.txt` nu voor woorden doet. Dan
krimpt het namentabblad per crawl tot alleen nieuwe namen. Bewust uitgesteld
tot duidelijk is of iemand dat onderhoud echt gaat doen.

## Openstaande besluiten

**2. De sitebeheerder inlichten.** `robots.txt` van
www.nederlandwereldwijd.nl staat crawlen toe, en we houden ons aan de
verboden paden, een halve seconde tussen pagina's en een herkenbare
User-Agent. Toch is het netjes om de beheerder te laten weten dat dit
draait. Dat is nog niet gebeurd.

**3. Mogen de bevindingen publiek blijven staan?** De repository is publiek,
dus `docs/resultaten.json` en de Pages-link zijn voor iedereen zichtbaar.
Het gaat alleen om citaten uit pagina's die al openbaar zijn, maar het is
wel een bewuste keuze. Zodra iemand hier interne pagina's of conceptteksten
in wil, klopt deze opzet niet meer.

## Bekende beperkingen

- **`persoons-` uit "persoons- en bagagecontrole"** wordt getoetst als
  `persoons`, en dat is geen los woord. Bij een weglatingsstreepje valt niet
  vast te stellen wat het hele woord had moeten zijn.
- **Anderstalige woorden zonder hoofdletter** blijven bij de spelfouten
  staan: `and` uit "US Customs and Border Protection", `viajeros` uit "Para
  viajeros", `floods`, `travel`. Na besluit 1 zijn dit de 34 meldingen die
  naast de 8 echte fouten overblijven — dus veruit de grootste rest-ruis.
  Ze staan bewust niet op de uitzonderingenlijst en vallen bewust niet onder
  de naam-regel: zie de toelichting onderaan `data/uitzonderingen.txt`. Ze
  goedkeuren zou betekenen dat een Engels woord middenin een Nederlandse zin
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
| | nww-team.github.io (de eigen Pages-link) |
| | npm en PyPI (dus geen pakketten installeren) |

Gevolgen:

- De OpenTaal-woordenlijst kun je **niet lokaal downloaden**. Draai
  `scripts/crawl.py` lokaal en hij valt terug op `data/woordenlijst-demo.txt`,
  een testlijst van ruim honderd woorden die alleen voor `demo/` deugt. De
  echte spellingtoets draait alleen in de workflow.
- De Pages-link kun je **niet zelf controleren**. Dat moet iemand in een
  gewone browser doen.
- `scripts/crawl.py` en `scripts/test.py` gebruiken daarom alleen de
  standaardbibliotheek van Python. Houd dat zo.
- Chromium staat wel voorgeïnstalleerd op
  `/opt/pw-browsers/chromium-1194/chrome-linux/chrome` en is bruikbaar met
  `--headless --dump-dom` om `docs/index.html` echt in een browser te testen.

## Ontwerppunt voor later

`docs/resultaten.json` staat in de repository en wordt door de workflow
teruggeschreven. Dat botst zodra er op twee branches een crawl draait — dat
gebeurde op 14 september en leverde een merge-conflict op. Werkbaar voor een
prototype, maar zodra er twee mensen aan werken moet het resultaat als los
artefact gepubliceerd worden in plaats van gecommit.

## Beheer

**De app heeft een eigenaar nodig bij de webredactie** — de persoon uit
STRATEGY.md die de kwaliteit van de website bewaakt. Zonder eigenaar
verdwijnt zo'n prototype.

Twee dingen zijn licht, maar wel echt werk:

- **De uitzonderingenlijst** (`data/uitzonderingen.txt`) groeit met elk vals
  alarm en hoort bij de redactie, niet bij de techniek. Er staan
  huisstijlkeuzes in, zoals dat NederlandWereldwijd altijd `lhbtiq+` schrijft.
  Wie daar een woord aan toevoegt, beslist wat "goed" is.
- **Iemand start de crawl** wanneer dat nodig is. Er gebeurt niets vanzelf.

**Voordat collega's hierop kunnen vertrouwen:**

1. Het percentage vals alarm moet bekend zijn over meer dan 50 pagina's.
   Na besluit 1 weten we: 8 echte fouten op 42 spelfoutmeldingen. Dat is één
   op de vijf en dus na te lopen, maar het is één crawl. Een tweede crawl over
   een ander deel van de site moet dat bevestigen — en laten zien of de
   hoofdletterregel daar net zo goed uitpakt als op reisadviezen.
2. Afspraak met de beheerder van de website (besluit 2).
3. Besluit over publiek publiceren (besluit 3).
4. Iemand die het onderhoudt als de website van structuur verandert.

## Wat er bewust niet in zit

Grammatica, stijl en d/t-fouten · alle 4.660 pagina's in één run · continu of
gepland scannen · meerdere talen · terugschrijven naar het CMS · inloggen of
rollen · een startknop in de app zelf · bevindingen bewaren om trends over
tijd te zien · afgeschermde of interne pagina's.
