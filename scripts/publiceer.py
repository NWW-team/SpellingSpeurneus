#!/usr/bin/env python3
"""Zet het resultaat van een crawl in Supabase, achter de toegangscontrole.

Vervangt het oude gedrag waarbij docs/resultaten.json in deze publieke
repository werd gecommit en dus voor iedereen te lezen was.

Draait op de GitHub-runner, niet in de browser. De sleutel komt uit de
omgeving en hoort in een GitHub Actions secret:

    SUPABASE_URL                de project-URL, bijvoorbeeld
                                https://xxxxxxxx.supabase.co
    SUPABASE_SERVICE_ROLE_KEY   de service-role key

Die key zet RLS buiten werking en mag daarom nergens anders staan: niet in de
frontend, niet in deze repository en niet in een prompt. Alleen de
standaardbibliotheek van Python, zoals de rest van dit project.
"""

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

WORTEL = Path(__file__).resolve().parent.parent

# Per verzoek uploaden we een blok bevindingen. Groot genoeg om niet honderden
# verzoeken te doen, klein genoeg om niet op een limiet te stuiten.
BLOK = 500

# Deze velden komen één-op-één uit resultaten.json in de tabel crawls. De
# aantallen (aantal_bevindingen en zo) staan er niet bij: die zijn uit de
# bevindingen zelf te tellen, en twee keer opslaan levert alleen de kans op dat
# ze ooit niet meer overeenkomen.
CRAWL_VELDEN = ("gestart_op", "bron", "woordenlijst", "user_agent",
                "aantal_paginas", "overgeslagen_urls")


def verzoek(basis, sleutel, pad, lichaam, extra_kop=None):
    data = json.dumps(lichaam, ensure_ascii=False).encode("utf-8")
    kop = {
        "apikey": sleutel,
        "Authorization": f"Bearer {sleutel}",
        "Content-Type": "application/json",
    }
    if extra_kop:
        kop.update(extra_kop)
    aanvraag = urllib.request.Request(f"{basis}/rest/v1/{pad}", data=data,
                                      headers=kop, method="POST")
    try:
        with urllib.request.urlopen(aanvraag, timeout=60) as antwoord:
            rauw = antwoord.read().decode("utf-8")
            return json.loads(rauw) if rauw.strip() else None
    except urllib.error.HTTPError as fout:
        # De melding van Supabase erbij, anders sta je naar een 400 te kijken
        # zonder te weten welk veld er niet klopt. De sleutel zelf staat niet in
        # de melding, en die mag ook niet in een logboek belanden.
        melding = fout.read().decode("utf-8", "replace")[:800]
        sys.exit(f"Supabase gaf {fout.code} op {pad}: {melding}")
    except urllib.error.URLError as fout:
        sys.exit(f"Kan {basis} niet bereiken: {fout.reason}")


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--in", dest="bestand",
                        default=str(WORTEL / "resultaten.json"),
                        help="het JSON-bestand dat crawl.py heeft geschreven")
    argumenten = parser.parse_args()

    basis = os.environ.get("SUPABASE_URL", "").rstrip("/")
    sleutel = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")
    if not basis or not sleutel:
        sys.exit("SUPABASE_URL en SUPABASE_SERVICE_ROLE_KEY moeten in de "
                 "omgeving staan. Zet ze als GitHub Actions secret.")

    pad = Path(argumenten.bestand)
    if not pad.exists():
        sys.exit(f"{pad} bestaat niet. Draai eerst scripts/crawl.py.")
    resultaat = json.loads(pad.read_text(encoding="utf-8"))

    bevindingen = resultaat.get("bevindingen", [])
    if not bevindingen:
        print("Geen bevindingen in het bestand; er wordt niets gepubliceerd.")
        return

    crawl_rij = {veld: resultaat[veld] for veld in CRAWL_VELDEN if veld in resultaat}
    gemaakt = verzoek(basis, sleutel, "crawls", crawl_rij,
                      {"Prefer": "return=representation"})
    crawl_id = gemaakt[0]["id"]
    print(f"Crawl aangemaakt: {crawl_id} ({crawl_rij.get('bron')}, "
          f"{crawl_rij.get('aantal_paginas')} pagina's)")

    verstuurd = 0
    for begin in range(0, len(bevindingen), BLOK):
        blok = [{
            "crawl_id": crawl_id,
            "url": b["url"],
            "titel": b.get("titel"),
            "woord": b["woord"],
            # Een oudere crawl kende het onderscheid nog niet; die bevindingen
            # zijn spelfouten, want zo stonden ze toen ook in het scherm.
            "soort": b.get("soort", "spelfout"),
            "context": b.get("context"),
        } for b in bevindingen[begin:begin + BLOK]]
        verzoek(basis, sleutel, "bevindingen", blok,
                {"Prefer": "return=minimal"})
        verstuurd += len(blok)
        print(f"  {verstuurd}/{len(bevindingen)} bevindingen geplaatst")

    print(f"\nKlaar. {verstuurd} bevindingen staan in Supabase, alleen "
          f"leesbaar voor toegestane accounts.")


if __name__ == "__main__":
    main()
