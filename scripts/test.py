#!/usr/bin/env python3
"""Controles voor SpellingSpeurneus.

    python3 scripts/test.py          # alles, inclusief robots.txt (netwerk nodig)
    python3 scripts/test.py --offline  # alleen de controles zonder netwerk
"""

import json
import os
import subprocess
import sys
import tempfile
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from voortgang import meld  # noqa: E402
from crawl import (SITE, is_bekend, lees_goedgekeurd,  # noqa: E402
                   maak_robots_controle, naar_patroon, soort_van, tekst_uit_main,
                   zoek_fouten)

WORTEL = Path(__file__).resolve().parent.parent
uitkomsten = []


def controle(naam, gelukt, toelichting=""):
    uitkomsten.append(gelukt)
    print(f"  {'OK  ' if gelukt else 'FOUT'} {naam}" + (f" — {toelichting}" if toelichting else ""))


def _faalt(functie):
    """True als de functie een fout gooit (hier: een ongeldig id)."""
    try:
        functie()
    except Exception:
        return True
    return False


def draai_crawl(uitvoer, goedgekeurd=None):
    # Zonder --goedgekeurd zoekt crawl.py naar een goedgekeurd.json in de wortel
    # van de repository. Wijs daarom altijd een bestand aan, zodat een los
    # achtergebleven bestand de controles niet beinvloedt.
    opdracht = [sys.executable, str(WORTEL / "scripts" / "crawl.py"),
                "--bron", "demo", "--max-paginas", "5", "--uit", str(uitvoer),
                "--goedgekeurd", str(goedgekeurd or "bestaat-niet.json")]
    subprocess.run(opdracht, check=True, capture_output=True)
    return json.loads(Path(uitvoer).read_text(encoding="utf-8"))


def main():
    offline = "--offline" in sys.argv
    tijdelijk = Path(tempfile.mkdtemp())

    def woorden_in(zin):
        return [b["woord"] for b in zoek_fouten(zin, set())]

    def woorden_in_met(zin, toegestaan):
        return [b["woord"] for b in zoek_fouten(zin, toegestaan)]


    print("De drie ingebouwde fouten in demo/")
    resultaat = draai_crawl(tijdelijk / "demo.json")
    gevonden = {b["woord"] for b in resultaat["bevindingen"]}
    for fout in ("aanvraeg", "gelegenhied", "buitenladn"):
        controle(f"{fout} gevonden", fout in gevonden)
    controle("geen andere meldingen", len(gevonden) == 3, f"gevonden: {sorted(gevonden)}")
    controle("alle drie gelden als spelfout, niet als naam",
             all(b["soort"] == "spelfout" for b in resultaat["bevindingen"]))

    print("\nAlleen <main> wordt gelezen")
    for nepwoord in ("kwaliteitt", "navigatiefoutt", "voetfoutt"):
        controle(f"{nepwoord} uit menu/voettekst genegeerd", nepwoord not in gevonden)

    print("\nIn het scherm goedgekeurd")
    gk = tijdelijk / "goedgekeurd.json"
    gk.write_text(json.dumps([{"woord": "aanvraeg", "soort": "woord"},
                              {"woord": "Cochabamba", "soort": "naam"}]), encoding="utf-8")
    na_goedkeuren = draai_crawl(tijdelijk / "gk.json", goedgekeurd=gk)
    over = {b["woord"] for b in na_goedkeuren["bevindingen"]}
    controle("goedgekeurd woord verdwijnt", "aanvraeg" not in over)
    controle("de rest blijft staan", over == {"gelegenhied", "buitenladn"}, f"over: {sorted(over)}")
    toegestaan = lees_goedgekeurd(gk) | {"reis", "naar", "of"}
    controle("goedgekeurde naam verdwijnt, ook met andere hoofdletters",
             woorden_in_met("Reis naar Cochabamba of COCHABAMBA.", toegestaan) == [])
    controle("een andere naam blijft gemeld",
             woorden_in_met("Reis naar Cochabambo.", toegestaan) == ["Cochabambo"])
    controle("zonder bestand is er niets goedgekeurd",
             lees_goedgekeurd(tijdelijk / "bestaat-niet.json") == set())

    print("\nVoortgang melden")
    ontvangen = []

    class Nepsupabase(BaseHTTPRequestHandler):
        def do_PATCH(self):
            lengte = int(self.headers.get("Content-Length", 0))
            ontvangen.append((self.path, json.loads(self.rfile.read(lengte)),
                              self.headers.get("apikey")))
            self.send_response(204)
            self.end_headers()

        def log_message(self, *args):
            pass

    server = HTTPServer(("127.0.0.1", 0), Nepsupabase)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    oud_omgeving = {k: os.environ.get(k) for k in ("SUPABASE_URL", "SUPABASE_SERVICE_ROLE_KEY")}
    try:
        os.environ["SUPABASE_URL"] = f"http://127.0.0.1:{server.server_port}"
        os.environ["SUPABASE_SERVICE_ROLE_KEY"] = "sleutel"
        controle("een melding geeft True", meld("12", status="crawlen", paginas_klaar=5) is True)
        pad, lichaam, apikey = ontvangen[-1]
        controle("de melding gaat naar de juiste rij", pad.endswith("/crawl_aanvragen?id=eq.12"), pad)
        controle("de velden komen aan, plus een tijdstip",
                 lichaam["status"] == "crawlen" and lichaam["paginas_klaar"] == 5
                 and "bijgewerkt_op" in lichaam)
        controle("de sleutel gaat mee als apikey", apikey == "sleutel")
        voor = len(ontvangen)
        controle("zonder aanvraag-id wordt niets gemeld",
                 meld("", status="klaar") is False and len(ontvangen) == voor)
        controle("een id met rommel wordt geweigerd, niet doorgegeven",
                 _faalt(lambda: meld("1;drop", status="klaar")) and len(ontvangen) == voor)
        # Een crawl met aanvraag-id draait door en meldt zijn tellingen
        ontvangen.clear()
        subprocess.run([sys.executable, str(WORTEL / "scripts" / "crawl.py"), "--bron", "demo",
                        "--max-paginas", "5", "--uit", str(tijdelijk / "v.json"),
                        "--goedgekeurd", "bestaat-niet.json", "--aanvraag-id", "7"],
                       check=True, capture_output=True, env=os.environ.copy())
        statussen = [m[1] for m in ontvangen]
        controle("de crawl meldt eerst het totaal",
                 statussen and statussen[0].get("status") == "crawlen"
                 and statussen[0].get("paginas_totaal") == 5, f"{statussen[:1]}")
        controle("de crawl meldt zijn laatste stand",
                 statussen[-1].get("paginas_klaar") == 5, f"{statussen[-1:]}")
        os.environ["SUPABASE_URL"] = "http://127.0.0.1:1"
        controle("een onbereikbare server stopt niets, het geeft False",
                 meld("12", status="crawlen") is False)
    finally:
        server.shutdown()
        for k, v in oud_omgeving.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v

    print("\nGoedgekeurde woorden ophalen")
    # Dit is de enige lijst. Lukt het ophalen niet, dan moet de run stoppen en geen
    # leeg bestand achterlaten waarmee de crawl stilletjes doorgaat.
    uit = tijdelijk / "gk-ophalen.json"
    omgeving = {**os.environ, "SUPABASE_URL": "http://127.0.0.1:1",
                "SUPABASE_SERVICE_ROLE_KEY": "sleutel"}
    mislukt_run = subprocess.run([sys.executable, str(WORTEL / "scripts" / "haal_goedgekeurd.py"),
                                  str(uit)], capture_output=True, env=omgeving)
    controle("onbereikbaar Supabase laat de run stoppen", mislukt_run.returncode != 0)
    controle("en laat geen leeg bestand achter", not uit.exists())
    zonder = {k: v for k, v in os.environ.items() if not k.startswith("SUPABASE_")}
    mislukt_run = subprocess.run([sys.executable, str(WORTEL / "scripts" / "haal_goedgekeurd.py"),
                                  str(uit)], capture_output=True, env=zonder)
    controle("een ontbrekende sleutel laat de run ook stoppen", mislukt_run.returncode != 0)

    print("\nGoedgekeurde woorden met een apostrof")
    uitz = {"natuurrisico's", "radiotaxi"}
    zin = "Let op natuurrisico\u2019s en radiotaxi\u2019s in het land."
    over = [b["woord"] for b in zoek_fouten(zin, uitz)]
    controle("gekrulde apostrof telt als rechte", "natuurrisico's" not in over, f"over: {over}")
    controle("goedgekeurd woord dekt het meervoud", "radiotaxi's" not in over, f"over: {over}")

    print("\nHuisstijl met een plus")
    huis = {"lhbtiq+", "vriendelijke"}
    controle("lhbtiq+ wordt goedgekeurd", "lhbtiq+" not in woorden_in_met("Een lhbtiq+ persoon.", huis))
    controle("lhbtiq zonder plus wordt gemeld", "lhbtiq" in woorden_in_met("Een lhbtiq persoon.", huis))
    controle("samenstelling over beide lijsten",
             "lhbtiq+-vriendelijke" not in woorden_in_met("Een lhbtiq+-vriendelijke stad.", huis))

    print("\nSpelfout of naam")
    # Deze indeling haalt ruim 90% van de meldingen uit beeld, dus hij moet
    # kloppen op precies de gevallen waarop het besluit is genomen.
    controle("hoofdletter middenin een zin is een naam",
             soort_van("Cochabamba", "Zoals de steden La Paz en Cochabamba.") == "naam")
    controle("hoofdletter aan het zinsbegin blijft een spelfout",
             soort_van("Registeer", "Registeer u bij de ambassade.") == "spelfout")
    controle("kleine letter middenin blijft een spelfout",
             soort_van("nieet", "Reis nieet naar dit gebied.") == "spelfout")
    controle("aanhalingsteken voor het zinsbegin telt niet mee",
             soort_van("Registeer", "\u2018Registeer u,\u2019 zegt de ambassade.") == "spelfout")
    controle("vergeten spatie gaat voor de hoofdletterregel",
             soort_van("III.Let", "De koers van segmento III.Let op dat u wisselt.") == "spelfout")
    controle("vergeten spatie na een klein woord",
             soort_van("demonstraties.Volg", "Vermijd demonstraties.Volg het nieuws.") == "spelfout")
    controle("webadres is geen vergeten spatie",
             soort_van("Windy.com", "Bekijk de windkaart op Windy.com vandaag.") == "naam")
    controle("afkorting met punten is geen vergeten spatie",
             soort_van("U.S", "Lees dit op de website van het U.S Department.") == "naam")
    controle("de soort staat in elke bevinding",
             all(b["soort"] in ("spelfout", "naam")
                 for b in zoek_fouten("Reis nieet naar Cochabamba.", set())))

    print("\nSjabloonresten (rommel uit het CMS)")
    # "undefined" stond zichtbaar boven aan reisadvies/estland. Deze meldingen
    # mogen nooit wegvallen: een bezoeker ziet ze wel.
    schoon = {"reist", "u", "naar", "voor", "het", "reisadvies", "is", "geel",
              "de", "grens", "bij", "aankomst", "en", "aantal", "nul",
              "nulmeting", "object", "gedaan", "zijn", "terrorisme", "er", "niet"}
    def resten(zin):
        return [b["woord"] for b in zoek_fouten(zin, schoon)]
    controle("undefined wordt gemeld",
             "undefined" in resten("undefined Terrorisme is er niet."))
    controle("[object Object] wordt heel gemeld, niet stukgeknipt",
             resten("Reist u naar [object Object] voor het reisadvies.") == ["[object Object]"])
    controle("onvervangen sjabloonveld met accolades",
             "{{land}}" in resten("Het reisadvies voor {{land}} is geel."))
    controle("onvervangen sjabloonveld met dollarteken",
             "${land}" in resten("Het reisadvies voor ${land} is geel."))
    controle("dubbel ontsnapte HTML",
             resten("De grens bij&nbsp;aankomst.") == ["&nbsp;"])
    controle("de rest wordt niet dubbel gemeld",
             resten("De grens bij&nbsp;aankomst.").count("&nbsp;") == 1)
    controle("de zin blijft ongewijzigd als context",
             all(b["context"] == "Het reisadvies voor {{land}} is geel."
                 for b in zoek_fouten("Het reisadvies voor {{land}} is geel.", schoon)))
    controle("gewoon Nederlands blijft met rust",
             resten("De nul en de nulmeting zijn gedaan.") == [])
    controle("een sjabloonrest telt als spelfout, niet als naam",
             all(b["soort"] == "spelfout"
                 for b in zoek_fouten("Reist u naar [object Object] voor het reisadvies.", schoon)))

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

    print("\nWoordvormen")
    woordjes = {"radiotaxi", "consulaat", "generaal", "nood", "bus", "chauffeur"}
    controle("meervoud met apostrof", is_bekend("radiotaxi's", woordjes))
    controle("samenstelling met koppelteken", is_bekend("consulaat-generaal", woordjes))
    controle("onzin blijft onbekend", not is_bekend("radiotaxy's", woordjes))

    print("\nWoorden uit een zin halen")
    def woorden_in(zin):
        return [b["woord"] for b in zoek_fouten(zin, set())]

    def woorden_in_met(zin, toegestaan):
        return [b["woord"] for b in zoek_fouten(zin, toegestaan)]
    controle("weglatingsstreepje", "Nood" in woorden_in("Nood- of crisissituatie."))
    controle("schuine streep splitst",
             woorden_in("Laat familie/vrienden weten.")[1:3] == ["familie", "vrienden"])
    controle("haakje middenin splitst", "chauffeur" in woorden_in("Wijs de (bus)chauffeur erop."))
    controle("koppelteken blijft heel", "e-mail" in woorden_in("Stuur een e-mail."))
    controle("e-mailadres wordt overgeslagen",
             not any("@" in w for w in woorden_in("Mail naar iemand@voorbeeld.nl vandaag.")))
    controle("onzichtbare tekens weg", "adres" in woorden_in("Het a\u200bdres."))

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
