#!/usr/bin/env python3
"""Controles voor SpellingSpeurneus.

    python3 scripts/test.py          # alles, inclusief robots.txt (netwerk nodig)
    python3 scripts/test.py --offline  # alleen de controles zonder netwerk
"""

import json
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from crawl import SITE, maak_robots_controle, naar_patroon, tekst_uit_main  # noqa: E402

WORTEL = Path(__file__).resolve().parent.parent
uitkomsten = []


def controle(naam, gelukt, toelichting=""):
    uitkomsten.append(gelukt)
    print(f"  {'OK  ' if gelukt else 'FOUT'} {naam}" + (f" — {toelichting}" if toelichting else ""))


def draai_crawl(uitvoer, uitzonderingen=None):
    opdracht = [sys.executable, str(WORTEL / "scripts" / "crawl.py"),
                "--bron", "demo", "--max-paginas", "5", "--uit", str(uitvoer)]
    if uitzonderingen:
        opdracht += ["--uitzonderingen", str(uitzonderingen)]
    subprocess.run(opdracht, check=True, capture_output=True)
    return json.loads(Path(uitvoer).read_text(encoding="utf-8"))


def main():
    offline = "--offline" in sys.argv
    tijdelijk = Path(tempfile.mkdtemp())

    print("De drie ingebouwde fouten in demo/")
    resultaat = draai_crawl(tijdelijk / "demo.json")
    gevonden = {b["woord"] for b in resultaat["bevindingen"]}
    for fout in ("aanvraeg", "gelegenhied", "buitenladn"):
        controle(f"{fout} gevonden", fout in gevonden)
    controle("geen andere meldingen", len(gevonden) == 3, f"gevonden: {sorted(gevonden)}")

    print("\nAlleen <main> wordt gelezen")
    for nepwoord in ("kwaliteitt", "navigatiefoutt", "voetfoutt"):
        controle(f"{nepwoord} uit menu/voettekst genegeerd", nepwoord not in gevonden)

    print("\nUitzonderingenlijst")
    lijst = tijdelijk / "uitzonderingen.txt"
    lijst.write_text("gelegenhied\n", encoding="utf-8")
    met_uitzondering = draai_crawl(tijdelijk / "uitz.json", lijst)
    woorden = {b["woord"] for b in met_uitzondering["bevindingen"]}
    controle("uitgezonderd woord verdwijnt", "gelegenhied" not in woorden)
    controle("de rest blijft staan", len(woorden) == 2, f"over: {sorted(woorden)}")

    print("\nPatronen uit robots.txt")
    for patroon, pad, verwacht in [
        ("/api/*", "/api/iets", True), ("/api/*", "/apart", False),
        ("/zoeken?*", "/zoeken?q=a", True), ("/zoeken?*", "/zoekenlijst", False),
        ("/x$", "/x", True), ("/x$", "/xy", False),
    ]:
        controle(f"{patroon} tegen {pad}", bool(naar_patroon(patroon).match(pad)) == verwacht)

    print("\nTekst uit een pagina halen")
    controle("geen <main> geeft lege tekst", tekst_uit_main("<p>hoi</p>") == "")
    controle("script wordt overgeslagen",
             "verstopt" not in tekst_uit_main("<main><script>verstopt</script>tekst</main>"))
    controle("entiteiten worden vertaald",
             tekst_uit_main("<main>caf&eacute;</main>") == "café")

    if offline:
        print("\n(robots.txt tegen de echte site overgeslagen: --offline)")
    else:
        print("\nrobots.txt van de echte site")
        mag = maak_robots_controle()
        controle("gewone pagina mag", mag(SITE + "/reisadvies/albanie"))
        controle("/zoeken? geblokkeerd", not mag(SITE + "/zoeken?q=paspoort"))
        controle("/api/ geblokkeerd", not mag(SITE + "/api/iets"))

    mislukt = uitkomsten.count(False)
    print(f"\n{len(uitkomsten) - mislukt} van {len(uitkomsten)} controles goed.")
    return 1 if mislukt else 0


if __name__ == "__main__":
    sys.exit(main())
