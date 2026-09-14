#!/usr/bin/env python3
"""SpellingSpeurneus - zoekt spelfouten op een website, op verzoek.

Draait op de standaardbibliotheek van Python. Geen pip install nodig.

    python3 scripts/crawl.py --bron demo --max-paginas 5
    python3 scripts/crawl.py --bron reisadvies --max-paginas 10
"""

import argparse
import html
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

SITE = "https://www.nederlandwereldwijd.nl"
PROJECT_URL = "https://github.com/NWW-team/SpellingSpeurneus"
USER_AGENT = f"SpellingSpeurneus/0.1 (+{PROJECT_URL})"

SITEMAPS = {
    "paginas": f"{SITE}/paginas/sitemap.xml",
    "reisadvies": f"{SITE}/reisadvies/sitemap.xml",
    "ambassades": f"{SITE}/contact/ambassades-consulaten-generaal/sitemap.xml",
}

WORTEL = Path(__file__).resolve().parent.parent
LEESTEKENS = " \t\n\r.,;:!?()[]{}<>\"'“”‘’„…*•·|/\\&%+=–—@#$^~`"


# --- ophalen ---------------------------------------------------------------

def haal_op(url, pauze=0.0):
    """Haalt een URL op met een herkenbare User-Agent."""
    if pauze:
        time.sleep(pauze)
    verzoek = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(verzoek, timeout=30) as antwoord:
        ruw = antwoord.read()
    return ruw.decode("utf-8", errors="replace")


def lees_sitemap(url, pauze):
    """Geeft de URL's uit een sitemap terug, in volgorde van het bestand."""
    xml = haal_op(url, pauze)
    return re.findall(r"<loc>\s*([^<\s]+)\s*</loc>", xml)


def naar_patroon(pad):
    """Zet een robots-pad ('/api/*', '/zoeken?*') om in een reguliere expressie."""
    patroon = re.escape(pad).replace(r"\*", ".*")
    if patroon.endswith(r"\$"):
        patroon = patroon[:-2] + "$"
    return re.compile("^" + patroon)


def maak_robots_controle():
    """Leest robots.txt en geeft een functie terug die zegt of een URL mag.

    Dit doen we zelf en niet met urllib.robotparser: die behandelt de ster in
    'Disallow: /api/*' als een gewoon teken, waardoor zo'n regel niets blokkeert.
    """
    try:
        tekst = haal_op(f"{SITE}/robots.txt")
    except Exception as fout:  # zonder robots.txt crawlen we niet
        sys.exit(f"Kan robots.txt niet lezen ({fout}). Gestopt uit voorzorg.")

    regels = []  # (lengte, mag_wel, patroon)
    geldt_voor_ons = False
    for regel in tekst.splitlines():
        regel = regel.split("#")[0].strip()
        sleutel, _, waarde = regel.partition(":")
        sleutel, waarde = sleutel.strip().lower(), waarde.strip()
        if sleutel == "user-agent":
            geldt_voor_ons = waarde == "*"
        elif geldt_voor_ons and sleutel in ("disallow", "allow") and waarde:
            regels.append((len(waarde), sleutel == "allow", naar_patroon(waarde)))

    verboden = [w for lengte, mag, w in regels if not mag]
    print(f"robots.txt: {len(verboden)} verboden pad(en) voor iedereen.")

    def mag_ophalen(url):
        onderdelen = urllib.parse.urlsplit(url)
        pad = onderdelen.path + (f"?{onderdelen.query}" if onderdelen.query else "")
        # De langste regel die past, wint; bij gelijke lengte wint 'Allow'.
        passend = [(lengte, mag) for lengte, mag, patroon in regels if patroon.match(pad)]
        if not passend:
            return True
        return max(passend, key=lambda r: (r[0], r[1]))[1]

    return mag_ophalen


# --- tekst uit de pagina halen ---------------------------------------------

def tekst_uit_main(pagina_html):
    """Haalt de leesbare tekst uit het <main>-element.

    Alles buiten <main> (menu, voettekst, cookiemelding) blijft buiten beeld:
    dat is geen redactionele content en zou alleen ruis opleveren.
    """
    treffer = re.search(r"<main\b[^>]*>(.*?)</main>", pagina_html, re.S | re.I)
    if not treffer:
        return ""
    inhoud = treffer.group(1)
    inhoud = re.sub(r"<(script|style|noscript)\b.*?</\1>", " ", inhoud, flags=re.S | re.I)
    inhoud = re.sub(r"<[^>]+>", " ", inhoud)
    inhoud = html.unescape(inhoud)
    return re.sub(r"\s+", " ", inhoud).strip()


def titel_uit(pagina_html):
    treffer = re.search(r"<title[^>]*>(.*?)</title>", pagina_html, re.S | re.I)
    if not treffer:
        return ""
    return re.sub(r"\s+", " ", html.unescape(treffer.group(1))).strip()


# --- spelling toetsen ------------------------------------------------------

def lees_woordenlijst(pad):
    woorden = set()
    with open(pad, encoding="utf-8") as bestand:
        for regel in bestand:
            woord = regel.strip()
            if woord and not woord.startswith("#"):
                woorden.add(woord)
                woorden.add(woord.lower())
    return woorden


def is_bekend(woord, woorden):
    """Bekend als het woord in de lijst staat, of als alle delen dat doen.

    Het tweede geval vangt samenstellingen met een koppelteken of apostrof
    ('consulaat-generaal', 'euro's') die niet altijd los in de lijst staan.
    """
    if woord in woorden or woord.lower() in woorden:
        return True
    delen = [deel for deel in re.split(r"[-'’]", woord) if deel]
    if len(delen) > 1 and all(deel.lower() in woorden for deel in delen):
        return True
    return False


def zoek_fouten(tekst, woorden, uitzonderingen):
    """Geeft per onbekend woord een bevinding met de zin eromheen."""
    bevindingen = []
    gezien = set()
    for zin in re.split(r"(?<=[.!?])\s+", tekst):
        for ruw in zin.split():
            woord = ruw.strip(LEESTEKENS)
            if not woord or not any(teken.isalpha() for teken in woord):
                continue
            if any(teken.isdigit() for teken in woord):
                continue  # versienummers, jaartallen, codes
            if woord.lower() in uitzonderingen:
                continue
            if is_bekend(woord, woorden):
                continue
            sleutel = (woord, zin)
            if sleutel in gezien:
                continue
            gezien.add(sleutel)
            bevindingen.append({"woord": woord, "context": kort(zin)})
    return bevindingen


def kort(zin, lengte=200):
    return zin if len(zin) <= lengte else zin[: lengte - 1].rstrip() + "…"


# --- de crawl zelf ---------------------------------------------------------

def verzamel_paginas(bron, max_paginas, pauze):
    """Geeft (naam, html) per pagina, plus de URL's die we hebben overgeslagen."""
    overgeslagen = []

    if bron == "demo":
        for pad in sorted((WORTEL / "demo").glob("*.html"))[:max_paginas]:
            yield f"demo/{pad.name}", pad.read_text(encoding="utf-8")
        return overgeslagen

    mag_ophalen = maak_robots_controle()
    urls = lees_sitemap(SITEMAPS[bron], 0)
    print(f"Sitemap {bron}: {len(urls)} URL's gevonden.")

    opgehaald = 0
    for url in urls:
        if opgehaald >= max_paginas:
            break
        if not mag_ophalen(url):
            overgeslagen.append(url)
            print(f"  overgeslagen (robots.txt): {url}")
            continue
        try:
            yield url, haal_op(url, pauze)
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError) as fout:
            overgeslagen.append(url)
            print(f"  overgeslagen (fout: {fout}): {url}")
            continue
        opgehaald += 1
        print(f"  [{opgehaald}/{max_paginas}] {url}")

    return overgeslagen


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bron", default="demo",
                        choices=["demo", *SITEMAPS], help="welk deel van de site")
    parser.add_argument("--max-paginas", type=int, default=50,
                        help="harde bovengrens op het aantal pagina's")
    parser.add_argument("--woordenlijst", default=str(WORTEL / "data" / "woordenlijst.txt"))
    parser.add_argument("--uitzonderingen", default=str(WORTEL / "data" / "uitzonderingen.txt"))
    parser.add_argument("--uit", default=str(WORTEL / "docs" / "resultaten.json"))
    parser.add_argument("--pauze", type=float, default=0.5,
                        help="seconden wachten tussen twee pagina's")
    argumenten = parser.parse_args()

    lijst_pad = Path(argumenten.woordenlijst)
    if not lijst_pad.exists():
        reserve = WORTEL / "data" / "woordenlijst-demo.txt"
        print(f"LET OP: {lijst_pad} ontbreekt. Ik gebruik de kleine testlijst "
              f"{reserve.name}; die is alleen bedoeld voor de demo-pagina's.")
        lijst_pad = reserve
    woorden = lees_woordenlijst(lijst_pad)
    uitzonderingen = {woord.lower() for woord in lees_woordenlijst(argumenten.uitzonderingen)}
    print(f"Woordenlijst: {lijst_pad.name} ({len(woorden)} vormen), "
          f"{len(uitzonderingen)} uitzonderingen.")

    bevindingen = []
    aantal_paginas = 0
    paginas = verzamel_paginas(argumenten.bron, argumenten.max_paginas, argumenten.pauze)
    overgeslagen = []
    while True:
        try:
            url, pagina_html = next(paginas)
        except StopIteration as einde:
            overgeslagen = einde.value or []
            break
        aantal_paginas += 1
        tekst = tekst_uit_main(pagina_html)
        if not tekst:
            print(f"  geen <main> gevonden: {url}")
            continue
        titel = titel_uit(pagina_html)
        for bevinding in zoek_fouten(tekst, woorden, uitzonderingen):
            bevindingen.append({"url": url, "titel": titel, **bevinding})

    resultaat = {
        "gestart_op": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "bron": argumenten.bron,
        "woordenlijst": lijst_pad.name,
        "user_agent": USER_AGENT,
        "aantal_paginas": aantal_paginas,
        "aantal_bevindingen": len(bevindingen),
        "overgeslagen_urls": overgeslagen,
        "bevindingen": bevindingen,
    }
    uit = Path(argumenten.uit)
    uit.parent.mkdir(parents=True, exist_ok=True)
    uit.write_text(json.dumps(resultaat, ensure_ascii=False, indent=2) + "\n",
                   encoding="utf-8")
    print(f"\n{aantal_paginas} pagina's bekeken, {len(bevindingen)} bevindingen -> {uit}")


if __name__ == "__main__":
    main()
