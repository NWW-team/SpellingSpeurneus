#!/usr/bin/env python3
"""Meldt de voortgang van een crawl aan Supabase, zodat het scherm een balk kan tonen.

Werkt de rij in `crawl_aanvragen` bij die de Edge Function `crawl-starten` heeft
gemaakt. Een crawl die niet via het scherm is gestart (de knop "Run workflow" in
GitHub) heeft geen aanvraag-id en meldt dus niets.

Een mislukte melding mag de crawl nooit stoppen: dan blijft de balk achter, maar
de resultaten komen er wel. Alleen de standaardbibliotheek van Python.

Als programma, voor de workflow:

    python3 scripts/voortgang.py --id 12 --status mislukt
"""

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone


def meld(aanvraag_id, **velden):
    """Werkt de rij bij. Geeft True als dat gelukt is, anders False; gooit nooit."""
    basis = os.environ.get("SUPABASE_URL", "").rstrip("/")
    sleutel = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "").strip()
    if not (aanvraag_id and basis and sleutel):
        return False
    velden["bijgewerkt_op"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    aanvraag = urllib.request.Request(
        f"{basis}/rest/v1/crawl_aanvragen?id=eq.{int(aanvraag_id)}",
        data=json.dumps(velden).encode("utf-8"), method="PATCH",
        headers={"apikey": sleutel, "Authorization": f"Bearer {sleutel}",
                 "Content-Type": "application/json", "Prefer": "return=minimal"})
    try:
        with urllib.request.urlopen(aanvraag, timeout=15):
            return True
    except (urllib.error.URLError, TimeoutError, ValueError) as fout:
        print(f"::warning::Voortgang melden mislukte ({fout}). De crawl gaat gewoon door.")
        return False


def run_url():
    """De link naar deze run in GitHub, of None buiten GitHub Actions."""
    server = os.environ.get("GITHUB_SERVER_URL")
    repo = os.environ.get("GITHUB_REPOSITORY")
    run = os.environ.get("GITHUB_RUN_ID")
    return f"{server}/{repo}/actions/runs/{run}" if server and repo and run else None


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--id", required=True)
    parser.add_argument("--status", required=True,
                        choices=["crawlen", "publiceren", "klaar", "mislukt"])
    argumenten = parser.parse_args()
    if not argumenten.id:
        return  # een crawl zonder aanvraag meldt niets
    meld(argumenten.id, status=argumenten.status)


if __name__ == "__main__":
    sys.exit(main())
