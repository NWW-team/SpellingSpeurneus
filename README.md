# SpellingSpeurneus

Zoekt spelfouten op [nederlandwereldwijd.nl](https://www.nederlandwereldwijd.nl),
wanneer de webredacteur daarom vraagt. Zie [STRATEGY.md](STRATEGY.md) voor het waarom
en [OVERDRACHT.md](OVERDRACHT.md) voor de stand van zaken, de openstaande besluiten
en wat je moet weten als je hieraan verder werkt.

**Resultaten bekijken:** https://nww-team.github.io/SpellingSpeurneus/ — zonder inlog. Zie [Toegang](#toegang).

## Hoe het werkt

1. Je drukt in het scherm op **Crawl starten** en kiest een deel van de site plus een
   maximumaantal pagina's. Er mag één crawl per dag. (De knop **Run workflow** bij
   [de Crawl-workflow](../../actions/workflows/crawl.yml) in GitHub werkt nog steeds, voor wie
   daar een account voor heeft; die valt buiten de limiet van één per dag.)
2. Een GitHub-runner leest de sitemap, haalt die pagina's op en pakt de tekst uit het
   `<main>`-element. Menu's en voetteksten blijven buiten beeld.
3. Elk woord wordt getoetst aan de OpenTaal-woordenlijst en aan onze eigen
   [`data/uitzonderingen.txt`](data/uitzonderingen.txt).
4. Wat overblijft wordt in tweeën gedeeld: **spelfouten** en **namen**. Zie hieronder.
5. Het resultaat gaat naar Supabase en verschijnt op de pagina hierboven.

Er draait niets automatisch op de achtergrond. Een crawl gebeurt alleen als iemand erom vraagt.

De knop roept de Edge Function [`crawl-starten`](supabase/functions/crawl-starten/index.ts)
aan, die de workflow in GitHub start. Het GitHub-token staat als secret `GITHUB_TOKEN` in
Supabase en heeft alleen *Actions: read and write* op deze repository. De limiet van één per
dag zit in de database (tabel `crawl_aanvragen`, unieke index op de datum in Nederlandse
tijd), dus twee gelijktijdige aanvragen komen er niet allebei door. Mislukt het starten bij
GitHub, dan wordt de aanvraag weer verwijderd en blijft de dag beschikbaar.

## Spelfouten en namen

De woordenlijst kent geen plaats- en organisatienamen. Op reisadviespagina's staan die
overal, dus zonder scheiding verdrinken de echte fouten erin: de crawl over alle 226
reisadviezen gaf 3.376 meldingen, waarvan er 2.949 een naam waren.

Daarom deelt de app elke melding in. **Een woord met een hoofdletter middenin een zin is
een naam**; aan het zinsbegin zegt een hoofdletter niets, dus daar toetsen we gewoon door.
Een vergeten spatie gaat voor: `III.Let op dat u` begint met een hoofdletter maar is een
echte fout. Dezelfde crawl levert zo 427 spelfouten op en 1.398 namen op een tweede
tabblad: 87% van de meldingen verdwijnt uit beeld zonder verloren te gaan.

Namen worden dus **niet weggegooid**. Ze staan er één keer per naam, met een voorbeeldzin
en een link naar het reisadvies waar die zin staat — en als de naam op meer pagina's
voorkomt, staat erbij op hoeveel. Zo blijft een verkeerd gespelde plaatsnaam op te zoeken. De indeling
staat per bevinding in de kolom `soort`, dus wie de regel anders wil (hij staat in
`soort_van` in `scripts/crawl.py`) kan het scherm omgooien zonder opnieuw te crawlen.

Wat de app hierbij níét kan: beoordelen of een naam goed gespeld is. `Cochabamba` en een
verkeerd gespelde variant krijgen dezelfde melding, want geen van beide staat in de
woordenlijst. Dat nakijken blijft mensenwerk.

## Vals alarm wegwerken

Meldt de app een woord of naam die gewoon goed is? Klik op **Goedkeuren**. Het verdwijnt uit
de lijst en komt op het tabblad **Goedgekeurd** te staan; de volgende crawl slaat het over.
Een vergissing maak je daar ongedaan met **Intrekken**. Goedkeuringen staan in de Supabase-tabel
`goedgekeurd` en worden nooit verwijderd, alleen met een datum ingetrokken.

Goedkeuren en intrekken gaan via de Edge Function
[`supabase/functions/goedkeuren`](supabase/functions/goedkeuren/index.ts) en zijn begrensd tot
300 wijzigingen per uur. Zie [Toegang](#toegang): omdat er geen inlog is, kan iedereen met de
link dit doen. De basislijst in [`data/uitzonderingen.txt`](data/uitzonderingen.txt) blijft
gelden naast wat in het scherm is goedgekeurd.

Eén ding om te weten bij het lezen van de cijfers: die lijst wordt bijgewerkt op basis van
de pagina's die al gecrawld zijn. Op **nieuwe** pagina's ligt het aantal valse meldingen
daarom hoger. Gemeten: 0,84 per pagina op de al opgeschoonde eerste 50, tegen 2,19 op de
176 pagina's die daarna voor het eerst langskwamen. Reken met het hoogste getal.

## Zelf draaien

Geen installatie nodig; alleen Python 3.

```bash
python3 scripts/crawl.py --bron demo --max-paginas 5     # fictieve pagina's, zonder netwerk
python3 scripts/crawl.py --bron reisadvies --max-paginas 10
python3 -m http.server --directory docs 8000             # scherm bekijken op localhost:8000
python3 scripts/test.py                                  # 42 controles; --offline slaat het netwerk over
```

Het scherm heeft Supabase nodig om iets te tonen; lokaal zie je zonder internet niets. Het resultaat van een lokale crawl in Supabase zetten kan met:

```bash
export SUPABASE_URL=https://xxxxxxxx.supabase.co
export SUPABASE_SERVICE_ROLE_KEY=...        # uit het dashboard, niet in een bestand
python3 scripts/crawl.py --bron demo --max-paginas 5 --uit resultaten.json
python3 scripts/publiceer.py --in resultaten.json
```

De workflow haalt per run de OpenTaal-lijst op (ruim 413.000 woorden) en vergelijkt de
sha256 met [`data/opentaal.sha256`](data/opentaal.sha256). Wijkt die af, dan waarschuwt de
run: je toetst dan aan een andere lijst dan de vorige keer.

Zonder `data/woordenlijst.txt` valt het script terug op `data/woordenlijst-demo.txt`. Dat is
een testlijst van ruim honderd woorden, alleen bedoeld voor `demo/`. De echte lijst haalt de
workflow per run op bij OpenTaal.

## Toegang

**Er is geen inlog meer.** De resultaten staan in Supabase en zijn leesbaar voor iedereen
die de publishable key heeft. Die staat in `docs/index.html`, in een publieke repository.
De "geheime link" naar de pagina is dus **geen toegangscontrole**: wie de repository leest,
kan de bevindingen ophalen. Dat is een bewuste keuze van de redactie (besluit 3 in
[OVERDRACHT.md](OVERDRACHT.md) is teruggedraaid). Schrijven kan de browser nog niet: alleen
de crawl-workflow, met de service-role key.

De migratie die dit instelt staat in
[`supabase/migrations/`](supabase/migrations/20261002000000_open_lezen.sql).

### Sleutels

| Wat | Waar | Waarom |
|---|---|---|
| Project-URL en **publishable key** | in `docs/index.html` en in de workflow, publiek | Daarvoor bedoeld. Verleent alleen wat de policies toestaan |
| **Service-role key** | alleen als GitHub Actions secret `SUPABASE_SERVICE_ROLE_KEY` | Zet RLS buiten werking. Nooit in de frontend, de repository of een prompt |
| Databasewachtwoord | nergens | Niet nodig |

Dat is dus **één** secret om te beheren. De project-URL staat gewoon in de
workflow, want die is niet geheim. De workflow heeft verder geen schrijfrecht op
de repository meer nodig.

## Fatsoenlijk crawlen

`robots.txt` van de site staat crawlen toe, behalve `/zoeken?*` en `/api/*`; die paden slaan
we over en dat is terug te zien in het logboek van elke run. Verder: een herkenbare
User-Agent met een link naar deze repository, een halve seconde tussen twee pagina's, en
altijd een harde bovengrens op het aantal pagina's.

## Wat hier staat

| Pad | Wat het is |
|---|---|
| `scripts/crawl.py` | De crawler en de spellingtoets. Alleen de standaardbibliotheek van Python |
| `scripts/test.py` | Controles: vindt de app de ingebouwde fouten, en volgt hij robots.txt |
| `docs/index.html` | Het scherm. Eén bestand, geen buildstap |
| `scripts/publiceer.py` | Zet het resultaat in Supabase, achter de toegangscontrole |
| `data/uitzonderingen.txt` | Basislijst van goedgekeurde woorden. Wat in het scherm wordt goedgekeurd staat in Supabase |
| `supabase/` | Migraties (in de SQL Editor te plakken) en de Edge Function `goedkeuren` |
| `scripts/haal_goedgekeurd.py` | Haalt de in het scherm goedgekeurde woorden op, vlak voor de crawl |
| `data/opentaal.sha256` | De versie van de woordenlijst waarop wij ons baseren |
| `demo/` | Vijf fictieve pagina's met drie ingebouwde fouten, om op te testen |
| `OVERDRACHT.md` | Stand van zaken, openstaande besluiten, beperkingen en beheer |
| `.github/workflows/crawl.yml` | De knop die een crawl start |

## Vormgeving

Het scherm benadert de Rijkshuisstijl in de **kleuren**: donkerblauw `#154273` voor de
kopbalk en de links, hemelblauw `#007BC7` als accent, lichtblauw `#8FCAE7` op donkere
vlakken en een geel markeerveld. Elke tekstkleur is tegen zijn achtergrond op WCAG
AA-contrast getoetst, in de lichte én de donkere stand.

Het is met opzet een benadering en geen kopie. Er zit **geen logo, woordmerk of het
Rijksoverheid-lettertype** in: dit is een hulpmiddel voor de redactie en moet niet voor
een officiële pagina van de Rijksoverheid worden aangezien — zeker niet zolang de
resultaten publiek staan (zie besluit 3 in [OVERDRACHT.md](OVERDRACHT.md)).

De echte tokens staan in
[nl-design-system/rijkshuisstijl-community](https://github.com/nl-design-system/rijkshuisstijl-community).
Die zijn hier niet uit overgenomen: dat pakket komt via npm en dit scherm is bewust één
bestand zonder buildstap. Wil je het exact maken, neem dan de tokenwaarden over in de
CSS-variabelen bovenaan `docs/index.html`; alles hangt aan die variabelen.

## Gegevens

Deze app leest alleen openbare webpagina's en een openbare woordenlijst. Er gaat geen
interne informatie doorheen en de bevindingen bevatten alleen citaten uit pagina's die
toch al openbaar zijn.

Toch staan de resultaten niet meer publiek: ze zijn een werklijst van de redactie en
horen bij de redactie. Zie [Toegang](#toegang) voor wat dat wel en niet afschermt.

Er zijn nu wél sleutels in het spel. Persoonsgegevens: Supabase Auth bewaart per
testaccount een e-mailadres en een wachtwoordhash. Deze app slaat zelf geen wachtwoorden
op en vergelijkt er geen.

## Bronvermelding

De spelling wordt getoetst aan de
[OpenTaal-woordenlijst](https://github.com/OpenTaal/opentaal-wordlist) van stichting
OpenTaal, die het Keurmerk Spelling van de Nederlandse Taalunie draagt. Licentie: Revised
BSD en/of CC BY 3.0.
