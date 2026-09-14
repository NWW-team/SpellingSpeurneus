# SpellingSpeurneus

Zoekt spelfouten op [nederlandwereldwijd.nl](https://www.nederlandwereldwijd.nl),
wanneer de webredacteur daarom vraagt. Zie [STRATEGY.md](STRATEGY.md) voor het waarom.

**Resultaten bekijken:** https://nww-team.github.io/SpellingSpeurneus/ — geen account nodig.

## Hoe het werkt

1. Je drukt op **Run workflow** bij [de Crawl-workflow](../../actions/workflows/crawl.yml)
   en kiest een deel van de site plus een maximumaantal pagina's.
2. Een GitHub-runner leest de sitemap, haalt die pagina's op en pakt de tekst uit het
   `<main>`-element. Menu's en voetteksten blijven buiten beeld.
3. Elk woord wordt getoetst aan de OpenTaal-woordenlijst en aan onze eigen
   [`data/uitzonderingen.txt`](data/uitzonderingen.txt).
4. Het resultaat komt in `docs/resultaten.json` te staan en verschijnt op de pagina hierboven.

Er draait niets automatisch op de achtergrond. Een crawl gebeurt alleen als iemand erom vraagt.

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
```

Zonder `data/woordenlijst.txt` valt het script terug op `data/woordenlijst-demo.txt`. Dat is
een testlijst van ruim honderd woorden, alleen bedoeld voor `demo/`. De echte lijst haalt de
workflow per run op bij OpenTaal.

## Fatsoenlijk crawlen

`robots.txt` van de site staat crawlen toe, behalve `/zoeken?*` en `/api/*`; die paden slaan
we over en dat is terug te zien in het logboek van elke run. Verder: een herkenbare
User-Agent met een link naar deze repository, een halve seconde tussen twee pagina's, en
altijd een harde bovengrens op het aantal pagina's.

## Wat hier staat

| Pad | Wat het is |
|---|---|
| `scripts/crawl.py` | De crawler en de spellingtoets. Alleen de standaardbibliotheek van Python |
| `docs/index.html` | Het scherm. Eén bestand, geen buildstap |
| `docs/resultaten.json` | Uitkomst van de laatste crawl |
| `data/uitzonderingen.txt` | Goedgekeurde woorden die niet in de woordenlijst staan |
| `demo/` | Vijf fictieve pagina's met drie ingebouwde fouten, om op te testen |
| `.github/workflows/crawl.yml` | De knop die een crawl start |

## Gegevens

Deze app leest alleen openbare webpagina's en een openbare woordenlijst. Er gaat geen
interne informatie en geen persoonsgegeven doorheen, en er zijn geen wachtwoorden of
sleutels nodig. De resultaten staan in deze publieke repository, dus ze zijn voor iedereen
te zien: ze bevatten alleen citaten uit pagina's die toch al openbaar zijn.

## Bronvermelding

De spelling wordt getoetst aan de
[OpenTaal-woordenlijst](https://github.com/OpenTaal/opentaal-wordlist) van stichting
OpenTaal, die het Keurmerk Spelling van de Nederlandse Taalunie draagt. Licentie: Revised
BSD en/of CC BY 3.0.
