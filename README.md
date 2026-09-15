# SpellingSpeurneus

Zoekt spelfouten op [nederlandwereldwijd.nl](https://www.nederlandwereldwijd.nl),
wanneer de webredacteur daarom vraagt. Zie [STRATEGY.md](STRATEGY.md) voor het waarom
en [OVERDRACHT.md](OVERDRACHT.md) voor de stand van zaken, de openstaande besluiten
en wat je moet weten als je hieraan verder werkt.

**Resultaten bekijken:** https://nww-team.github.io/SpellingSpeurneus/ — inloggen met een
account dat de beheerder vooraf heeft toegestaan. Zie [Toegang](#toegang).

## Hoe het werkt

1. Je drukt op **Run workflow** bij [de Crawl-workflow](../../actions/workflows/crawl.yml)
   en kiest een deel van de site plus een maximumaantal pagina's.
2. Een GitHub-runner leest de sitemap, haalt die pagina's op en pakt de tekst uit het
   `<main>`-element. Menu's en voetteksten blijven buiten beeld.
3. Elk woord wordt getoetst aan de OpenTaal-woordenlijst en aan onze eigen
   [`data/uitzonderingen.txt`](data/uitzonderingen.txt).
4. Wat overblijft wordt in tweeën gedeeld: **spelfouten** en **namen**. Zie hieronder.
5. Het resultaat gaat naar Supabase en verschijnt op de pagina hierboven, voor wie
   is ingelogd met een toegestaan account.

Er draait niets automatisch op de achtergrond. Een crawl gebeurt alleen als iemand erom vraagt.

## Spelfouten en namen

De woordenlijst kent geen plaats- en organisatienamen. Op reisadviespagina's staan die
overal, dus zonder scheiding verdrinken de echte fouten erin: de eerste crawl van 50
pagina's gaf 614 meldingen, waarvan er 8 een echte fout waren.

Daarom deelt de app elke melding in. **Een woord met een hoofdletter middenin een zin is
een naam**; aan het zinsbegin zegt een hoofdletter niets, dus daar toetsen we gewoon door.
Een vergeten spatie gaat voor: `III.Let op dat u` begint met een hoofdletter maar is een
echte fout. Dezelfde crawl levert zo 42 spelfouten op — met alle 8 echte fouten erbij — en
315 namen op een tweede tabblad.

Namen worden dus **niet weggegooid**. Ze staan er één keer per naam, met het aantal
pagina's erbij, zodat een verkeerd gespelde plaatsnaam op te zoeken blijft. De indeling
staat per bevinding in de kolom `soort`, dus wie de regel anders wil (hij staat in
`soort_van` in `scripts/crawl.py`) kan het scherm omgooien zonder opnieuw te crawlen.

Wat de app hierbij níét kan: beoordelen of een naam goed gespeld is. `Cochabamba` en een
verkeerd gespelde variant krijgen dezelfde melding, want geen van beide staat in de
woordenlijst. Dat nakijken blijft mensenwerk.

## Vals alarm wegwerken

Meldt de app een woord dat gewoon goed is? Klik op **Kopieer als uitzondering**, plak het
woord in [`data/uitzonderingen.txt`](data/uitzonderingen.txt) en draai de crawl opnieuw.
Die lijst hoort bij de webredactie, niet bij de techniek — hij groeit met het gebruik.

## Zelf draaien

Geen installatie nodig; alleen Python 3.

```bash
python3 scripts/crawl.py --bron demo --max-paginas 5     # fictieve pagina's, zonder netwerk
python3 scripts/crawl.py --bron reisadvies --max-paginas 10
python3 -m http.server --directory docs 8000             # scherm bekijken op localhost:8000
python3 scripts/test.py                                  # 42 controles; --offline slaat het netwerk over
```

Het scherm heeft Supabase nodig om iets te tonen; lokaal zie je zonder internet alleen
het inlogformulier. Het resultaat van een lokale crawl in Supabase zetten kan met:

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

De crawlresultaten zijn niet openbaar. Ze staan in Supabase en komen alleen vrij voor
een account dat op de allowlist staat.

**De controle zit in de database, niet in het scherm.** Op `crawls` en `bevindingen`
staat row level security aan, met één expliciete policy: lezen mag als je een sessie
hebt én je account op de allowlist staat. Zonder dat geeft de database nul rijen terug,
wat je in de browser ook probeert. Schrijven kan de browser helemaal niet.

**Zelf aanmelden kan niet.** Signups staan uit in de Auth-instellingen, dus de Auth-API
weigert elke registratiepoging. Dat er geen registratieknop in het scherm staat is niet
de maatregel — de maatregel is dat een onbekend account er domweg niet komt, en dat de
allowlist bepaalt wie gegevens ziet.

**De allowlist** is de tabel `toegestane_gebruikers`. Die draait op het gebruikers-id
uit `auth.users`, niet op het e-mailadres: een gebruiker kan zijn e-mailadres wijzigen,
zijn id niet. De tabel is vanuit de browser niet te lezen en niet te wijzigen, dus
niemand kan zichzelf toevoegen. Beheer gaat via het Supabase-dashboard.

**Wat hiermee níét is afgeschermd.** Dit scherm is een statisch bestand op GitHub Pages
en deze repository is publiek. `docs/index.html`, de crawler en de uitzonderingenlijst
blijven dus voor iedereen op te vragen — Supabase Auth schermt geen publieke HTML of
JavaScript af, en het inlogformulier in het scherm is geen toegangscontrole. Wie zonder
toegestaan account de pagina opent, ziet het formulier en verder niets. Wil je dat ook
de pagina zelf onbereikbaar is, dan is een andere hosting nodig: GitHub Pages kan geen
sessie controleren voordat het een bestand uitlevert.

Ook niet afgeschermd: **de git-geschiedenis**. `docs/resultaten.json` is uit de repository
gehaald, maar oude commits bevatten hem nog en die zijn publiek leesbaar. Het gaat om
citaten uit pagina's die al openbaar zijn; wil je dat weg, dan moet de geschiedenis
worden herschreven of de repository privé.

### Sleutels

| Wat | Waar | Waarom |
|---|---|---|
| Project-URL en **publishable key** | in `docs/index.html`, publiek | Daarvoor bedoeld. Verleent alleen wat de policies toestaan |
| **Service-role key** | alleen als GitHub Actions secret `SUPABASE_SERVICE_ROLE_KEY` | Zet RLS buiten werking. Nooit in de frontend, de repository of een prompt |
| Databasewachtwoord | nergens | Niet nodig |

De workflow heeft naast die twee secrets (`SUPABASE_URL` en `SUPABASE_SERVICE_ROLE_KEY`)
geen schrijfrecht op de repository meer nodig.

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
| `data/uitzonderingen.txt` | Goedgekeurde woorden die niet in de woordenlijst staan |
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
