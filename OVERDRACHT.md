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
`demonstraties.Volg` en `autorisation`. Naast die acht staan er ongeveer 600
meldingen die geen fout zijn — zie het openstaande besluit hieronder.

## Openstaande besluiten

**1. De eigennamen.** Van de 614 meldingen zijn er 573 een plaatsnaam,
organisatie of anderstalige bronnaam middenin een zin. Op reisadviespagina's
is dat onvermijdelijk veel. Hoofdletterwoorden middenin een zin overslaan
neemt ruim 70% van de ruis weg, maar dan valt een verkeerd gespelde
plaatsnaam niet meer op — en juist op reisadviezen zijn plaatsnamen
belangrijk. Dit is een keuze voor de webredactie, niet voor de techniek.
Het is te bouwen als schakelaar per crawl.

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
- **Anderstalige eigennamen** worden gemeld: `and` uit "US Customs and
  Border Protection", `viajeros` uit "Para viajeros". Die staan bewust niet
  op de uitzonderingenlijst — zie de toelichting onderaan
  `data/uitzonderingen.txt`. Ze goedkeuren zou betekenen dat een Engels
  woord middenin een Nederlandse zin nooit meer opvalt, en dat kostte bijna
  de vondst van `autorisation`.
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
   Nu weten we: 8 echte fouten op 614 meldingen, waarvan 573 eigennamen.
   Besluit 1 hierboven bepaalt of dat werkbaar is.
2. Afspraak met de beheerder van de website (besluit 2).
3. Besluit over publiek publiceren (besluit 3).
4. Iemand die het onderhoudt als de website van structuur verandert.

## Wat er bewust niet in zit

Grammatica, stijl en d/t-fouten · alle 4.660 pagina's in één run · continu of
gepland scannen · meerdere talen · terugschrijven naar het CMS · inloggen of
rollen · een startknop in de app zelf · bevindingen bewaren om trends over
tijd te zien · afgeschermde of interne pagina's.
