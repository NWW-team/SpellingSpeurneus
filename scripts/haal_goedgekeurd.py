#!/usr/bin/env python3
"""Haalt de in het scherm goedgekeurde woorden en namen uit Supabase.

Schrijft goedgekeurd.json, dat crawl.py leest. Draait op de GitHub-runner vlak
voor de crawl. Alleen de standaardbibliotheek van Python.

Een mislukte aanroep is geen reden om de crawl te stoppen: dan staat er een lege
lijst en komen goedgekeurde woorden opnieuw voorbij. Dat zeggen we hardop.
"""

import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

WORTEL = Path(__file__).resolve().parent.parent
BLOK = 1000  # PostgREST geeft er standaard niet meer dan duizend per verzoek


def haal(basis, sleutel):
    rijen = []
    for van in range(0, 10**9, BLOK):
        aanvraag = urllib.request.Request(
            f"{basis}/rest/v1/goedgekeurd?select=woord,soort&ingetrokken_op=is.null"
            f"&order=id&limit={BLOK}&offset={van}",
            headers={"apikey": sleutel, "Authorization": f"Bearer {sleutel}"})
        with urllib.request.urlopen(aanvraag, timeout=60) as antwoord:
            blok = json.loads(antwoord.read().decode("utf-8"))
        rijen.extend(blok)
        if len(blok) < BLOK:
            return rijen


def main():
    uit = Path(sys.argv[1]) if len(sys.argv) > 1 else WORTEL / "goedgekeurd.json"
    basis = os.environ.get("SUPABASE_URL", "").rstrip("/")
    sleutel = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "").strip()
    rijen = []
    if not basis or not sleutel:
        print("::warning::SUPABASE_URL of SUPABASE_SERVICE_ROLE_KEY ontbreekt; "
              "ik haal geen goedgekeurde woorden op.")
    else:
        try:
            rijen = haal(basis, sleutel)
        except (urllib.error.URLError, TimeoutError, ValueError) as fout:
            print(f"::warning::Goedgekeurde woorden ophalen mislukte ({fout}). "
                  f"De crawl gaat door zonder; goedgekeurde woorden komen opnieuw voorbij.")
    uit.write_text(json.dumps(rijen, ensure_ascii=False), encoding="utf-8")
    woorden = sum(1 for r in rijen if r["soort"] == "woord")
    print(f"{len(rijen)} goedgekeurd ({woorden} woorden, {len(rijen) - woorden} namen) -> {uit}")


if __name__ == "__main__":
    main()
