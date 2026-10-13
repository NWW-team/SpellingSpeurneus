# Overdracht

Wat een volgende sessie of collega moet weten om hier verder te kunnen. Voor hoe de app werkt voor
wie hem gebruikt: zie [README.md](README.md). Voor het waarom: [STRATEGY.md](STRATEGY.md).

Laatst bijgewerkt: **13 oktober 2026**.

Op 5 oktober is dit document helemaal herschreven; op 13 oktober is het bijgewerkt voor wat er sindsdien
veranderd is (zie [Wat er sinds 5 oktober is veranderd](#wat-er-sinds-5-oktober-is-veranderd)). **Er is ook
een Engelstalige zusterapp bijgekomen: TypoTapir** (zie [TypoTapir](#typotapir-de-engelstalige-zusterapp)).
Wil je in een nieuwe chat met Claude doorwerken? Begin dan bij
[Verder werken in een nieuwe chat](#verder-werken-in-een-nieuwe-chat).

## In het kort

SpellingSpeurneus zoekt spelfouten op [nederlandwereldwijd.nl](https://www.nederlandwereldwijd.nl),
wanneer de webredacteur daarom vraagt. Het scherm staat op
**https://nww-team.github.io/SpellingSpeurneus/**, zonder inlog. De redacteur kiest de tab van een deel van de site,
drukt op **Crawl starten**, volgt de voortgang, en loopt daarna de spelfouten en de namen na. Wat goed is
keurt hij goed; een naam die fout is, verplaatst hij naar de spelfouten; en de spelfouten kan hij als Excel
downloaden. Er draait niets vanzelf.

**Stand op 13 oktober.** Drie van de vier delen zijn gecrawld; Ambassades en consulaten nog niet.

| Deel | Laatste crawl | Pagina's | Spelfouten | Namen |
|---|---|---|---|---|
| Reisadviezen | 8 oktober | 236 | 43 | 1.801 |
| Visum voor Nederland | 9 oktober | 1.015 | 2.679 | 1.279 |
| Visum voor Caribische Koninkrijksdelen | 12 oktober | 452 | 46 | 564 |

In de database staan 11 crawls (25.878 bevindingen), 924 actieve goedgekeurde woorden en namen en 60 namen die
als spelfout zijn aangewezen. Het scherm toont per deel de laatste crawl.

**Wat die cijfers betekenen.** De 2.679 spelfouten bij Visum voor Nederland zijn grotendeels
valse meldingen: goede Nederlandse samenstellingen die OpenTaal niet kent (`inwilligingsbrief` 864 keer,
`luchthaventransitvisum`, `afspraakbevestiging`, `houderpagina`, `aanvraaglocatie`, `aanvraagcentrum`,
`vervoersticket`, `garantstellingsformulier`). Ze verdwijnen met **Goedkeuren**; dat is nog niet gedaan. Echte
fouten daartussen zijn bijvoorbeeld `officeel`. Bij reisadviezen is het beeld schoon: op 5 oktober waren
**13 van de 24 echte fouten die op 15 september waren gevonden, op de site gecorrigeerd** (`nieet`,
`Registeer`, `undefined`, `doen.n`, `III.Let`); de 11 die toen nog stonden (`autorisation`, `Bijvoorbeeldc`,
`invullen.n`, `meenenemen`, `metrologisch`, `motorvoortuigen`, `plaatvinden`, `prvincie`, `vande`,
`veiilgheidsrisico's`, `ZDe`) zijn sindsdien niet opnieuw nagekeken. Dat het verdwijnt uit de lijst door een
correctie op de site, en niet door Goedkeuren, is het doel van de app.

## Wat er sinds 5 oktober is veranderd

- **Tabs per deel van de site.** Het scherm toont per deel de laatste crawl, met eigen cijfers (spelfouten,
  namen, pagina's, laatste crawl), eigen spelfouten en namen. Bij het openen staat Reisadviezen open, ook
  als een ander deel de nieuwste crawl heeft (bewuste keuze). Een deel zonder crawl zegt dat. De lijst met
  delen staat als `DEEL_INFO` in `docs/index.html`.
- **Crawl starten zit in de tab.** Geen keuzelijst meer: de knop crawlt het deel van de actieve tab. De limiet
  van één crawl per dag geldt voor alle delen samen. De voortgangstekst noemt het deel.
- **De Excel** (alleen bij Spelfouten) heeft de kolommen Pagina, Zin, Woord, Suggestie, Opmerking; de laatste
  twee blijven leeg voor de redacteur. In de Zin staat de spelfout vet. De download bij Namen is weggehaald.
  Op 12 oktober door de redactie in Excel bekeken: werkt, vet staat goed.
- **Cache.** `xlsx.js` en de iconen worden met een versienummer geladen (`xlsx.js?v=2`, `icoon.png?v=2`). Een
  oude kopie in de browser of in de cache van GitHub Pages gaf een Excel met `[object Object]` in de zin; een
  harde refresh hielp niet, het versienummer wel. **Wijzig je `xlsx.js` of een icoon, verhoog dan het
  versienummer in `docs/index.html`.**
- **Teksten en kolommen opgeschoond:** maand voluit ("12 oktober 2026"), tijd zonder voorloopnul ("8.57 uur";
  de browser zet er zelf een nul voor, die haalt `tijd()` eraf), "Maximaal 1 crawl per dag.", Namen heeft
  een kortere uitleg, Goedgekeurd heeft geen uitleg, geen URL-filter en geen kolom "Goedgekeurd op".
- **Opgeruimd:** een dode CSS-regel, de exportcode van twee downloads naar één, README en OVERDRACHT
  bijgewerkt, de standaardwaarde van `--uit` in `crawl.py` is nu `resultaten.json` (zoals de workflow doet).
- **Controles:** 133 (`python3 scripts/test.py --offline`).

## Hoe het in elkaar zit

```
 Redacteur ── browser ── docs/index.html (GitHub Pages, statisch, supabase-js)
                              │ leest met de publieke key          │ schrijft nooit zelf
                              ▼                                    ▼
                       Supabase (Postgres, RLS)  ◄──── Edge Functions (service-role, met limieten)
                              ▲                          goedkeuren · naam-verplaatsen
                              │ schrijft                 crawl-starten ──► GitHub Actions
                              │                          crawl-stoppen ──► (annuleert de run)
                 GitHub Actions: .github/workflows/crawl.yml
                 haalt woordenlijst + goedgekeurd + GeoNames, crawlt, publiceert
```

| Onderdeel | Waar | Wat |
|---|---|---|
| Scherm | `docs/index.html`, `docs/xlsx.js`, `docs/icoon*.png` | Eén bestand, geen buildstap. `xlsx.js` maakt de Excel-download. Versienummers in `index.html` (zie hierboven) |
| Crawler en toets | `scripts/crawl.py` | Sitemaps lezen, pagina's ophalen, spelling toetsen, namen scheiden. Alleen standaardbibliotheek |
| Plaatsnamen | `scripts/plaatsnamen.py` | Beoordeelt namen tegen GeoNames |
| Lijsten ophalen | `scripts/haal_goedgekeurd.py` | Haalt `goedgekeurd` en `naam_is_spelfout` op voor de crawl; **stopt de run als dat mislukt** |
| Voortgang | `scripts/voortgang.py` | Meldt de stand van een crawl aan `crawl_aanvragen` |
| Publiceren | `scripts/publiceer.py` | Zet het resultaat in `crawls` en `bevindingen` |
| Controles | `scripts/test.py` | 133 controles, `python3 scripts/test.py --offline` (draait ook in de workflow) |
| Workflow | `.github/workflows/crawl.yml` | Invoer: `bron`, `aanvraag_id`, `opentaal_ref` |
| Database | `supabase/migrations/` | Tien migraties, **met de hand toegepast** (zie "Zo werk je eraan") |
| Edge Functions | `supabase/functions/` | Vier, allemaal `verify_jwt = false`, **met de hand gedeployd** |

### Supabase

Project `riwznqurcluudvyrkwxe` (eu-west-2). Tabellen: alle lezen is open voor `anon`, schrijven kan alleen
met de service-role key (RLS aan, plus `grant select` en de schrijfrechten weggehaald).

| Tabel | Inhoud |
|---|---|
| `crawls`, `bevindingen` | Elke crawl en zijn meldingen. `bevindingen.soort` is `spelfout` of `naam`; bij namen staan `plaats_status` (`bekend`, `twijfel`, `onbekend`) en `suggestie` |
| `goedgekeurd` | **De enige lijst met goedgekeurde woorden en namen** (924 actief op 13 oktober). Intrekken zet `ingetrokken_op`, er wordt niets verwijderd |
| `naam_is_spelfout` | Namen die de redactie als verkeerd gespeld heeft aangewezen (apart van `goedgekeurd`, bewust). Terugzetten zet `teruggezet_op` |
| `crawl_aanvragen` | Elke gestarte crawl, met status (`aangevraagd`, `crawlen`, `publiceren`, `klaar`, `mislukt`, `gestopt`, `onbekend`), voortgang en de link naar de run. Een unieke index op de datum (Nederlandse tijd) maakt het "één per dag"; mislukte en gestopte aanvragen tellen niet mee |
| `toegestane_gebruikers`, `is_toegestaan()` | **Niet meer in gebruik** (de inlog is weg); mogen weg |

Edge Functions: `goedkeuren` (woorden en namen goedkeuren en intrekken), `naam-verplaatsen`,
`crawl-starten` (start de workflow, hooguit één per dag), `crawl-stoppen` (annuleert de run; stoppen kan niet
tijdens het opslaan). `goedkeuren` en `naam-verplaatsen` laten maximaal 300 wijzigingen per uur toe.

Secrets: **GitHub** (Actions): `SUPABASE_SERVICE_ROLE_KEY`. **Supabase** (Edge Functions): `GITHUB_TOKEN`,
een fine-grained token met alleen *Actions: read and write* op deze repository. **Dat token verloopt**,
na de duur die bij het maken is gekozen; zie "Open punten". De publieke Supabase-key staat bewust in
`docs/index.html`. De service-role key mag nergens anders staan dan als secret.

### De delen van de site

Een deel is een pad; alles daarachter hoort erbij. De pagina's staan verspreid over de sitemaps van de
site (de visumpagina's zitten in de grote `paginas`-sitemap), dus de crawler leest ze allemaal en filtert
op het pad (`DELEN` in `crawl.py`).

| Deel | Pad | Pagina's (±) | Gecrawld |
|---|---|---|---|
| Reisadviezen | `/reisadvies` | 236 | ja (8 oktober) |
| Visum voor Nederland | `/visum-nederland` | 1.015 | ja (9 oktober) |
| Visum voor Caribische Koninkrijksdelen | `/caribisch-visum` | 452 | ja (12 oktober) |
| Ambassades en consulaten | `/contact/ambassades-consulaten-generaal` | 219 | nog niet |

Een crawl pakt altijd het hele deel (er is geen maximumaantal; `crawl.py --max-paginas` bestaat nog voor
lokaal testen, standaard 5000). "Overige pagina's" (de rest van de ±4.900) is geen keuze. Een deel
toevoegen: `DELEN` in `crawl.py`, dezelfde naam in de workflow, in `crawl-starten`, in de controle op
`crawl_aanvragen.bron` en in `DEEL_INFO` in `docs/index.html`.

## Zo werk je eraan

**Normaal verloop.** Branch maken vanaf `main`, aanpassen, `python3 scripts/test.py --offline`, pushen, PR,
mergen. Mergen naar `main` publiceert het scherm via GitHub Pages (een minuut of twee, daarna hard
verversen). In het dagelijks gebruik betekent "deploy" hier: de pull request mergen naar `main`, en
voor Supabase de migratie of de Edge Function zelf toepassen (zie hieronder).

**Git in Claude Code op het web.** De ontwikkelbranch heet `claude/serene-allen-blqd14`. Na een squash-merge
loopt die achter op `main`; zet hem voor een nieuwe wijziging opnieuw op vanaf `main`
(`git fetch origin main && git checkout -B claude/serene-allen-blqd14 origin/main`) en push met
`--force-with-lease`. Een stophook meldt anders "onuitgepushte commits" die al op `main` staan; een ondiepe clone
volgt bovendien alleen `main` (`git remote set-branches --add origin <branch>`). **Wat niet vanzelf gaat:**
- **Migraties** worden niet door een pipeline toegepast. Plak ze in de SQL Editor van het Supabase-dashboard,
  of draai ze via de MCP. Alle tien zijn toegepast (gecontroleerd op 5 oktober). Controleer na een nieuwe tabel altijd de
  *policy én de grants*, en toets als `anon` (`begin; set local role anon; select …; rollback;`): een policy
  zonder `grant select` geeft "permission denied for table" (zo ging het mis bij de eerste inlogloze versie).
- **Edge Functions** worden niet door een pipeline gedeployd. Deploy via het dashboard (Edge Functions) of via
  de MCP (`deploy_edge_function`), met **Verify JWT uit**, en neem de bestanden uit `supabase/functions/`
  over. De map en wat live staat kunnen uit de pas lopen; vergelijk met `get_edge_function`.
- **Volgorde bij een wijziging aan de workflow-invoer:** eerst de workflow mergen, dan de functie die hem
  aanroept deployen. GitHub weigert een invoer die de workflow niet kent.

**Werken in Claude Code op het web.** De omgeving heeft beperkte netwerktoegang; dat is beleid, geen storing.

| Wel bereikbaar | Niet bereikbaar |
|---|---|
| www.nederlandwereldwijd.nl (en netherlandsworldwide.nl, als die onder *Allowed domains* van de omgeving staat) | github.com, raw.githubusercontent.com en de eigen Pages-link |
| Supabase en GitHub, alleen via de MCP-koppelingen | `*.supabase.co` rechtstreeks, poort 5432 |
| | **download.geonames.org** (de plaatsnamenlijst), PyPI, het npm-register, CDN's |

- De OpenTaal-woordenlijst en GeoNames zijn dus **niet lokaal te downloaden**; de echte spelling- en
  plaatsnamentoets draait alleen in de workflow. Lokaal valt `crawl.py` terug op een testlijst
  (`data/woordenlijst-demo.txt`).
- De Pages-link, het inloggen en een echte crawl via de knop zijn hier niet te zien; dat moet iemand in een
  gewone browser doen.
- **Supabase via de MCP:** lezen werkt altijd; schrijven werkt meestal. Een `DROP INDEX` loopt er steeds
  vast (time-out na 60 s, ook met `lock_timeout` en `concurrently`, terwijl niets de tabel vasthoudt):
  draai zo'n opdracht in de SQL Editor. Meerdere statements in één opdracht lopen soms vast; doe ze dan
  los. Na een time-out: controleer eerst wat er is toegepast, want de opdracht kan half geslaagd zijn.
- De tools staan toe zonder vragen te stellen via `.claude/settings.local.json` (in `.gitignore`, dus
  niet in de repository): `execute_sql`, `apply_migration`, `deploy_edge_function` en wat leesopdrachten.
  In een nieuwe omgeving ontbreekt dat bestand en komen de toestemmingsvragen terug.
- **Testen in een browser:** Chromium staat op `/opt/pw-browsers/chromium-1194/chrome-linux/chrome`
  (`--headless --dump-dom`). Voor een echte schermbreedte (kleiner dan 500 pixels laat `--window-size`
  niet toe) is Playwright via Node beschikbaar. De pagina laadt supabase-js van een CDN die dicht staat;
  vervang die in een testkopie door een nagemaakte cliënt en `fetch`. Zo zijn alle knoppen getoetst.
- **Node** (22.18 of nieuwer) draait de TypeScript-tests van de Edge Functions
  (`supabase/functions/*/…test.ts`); `test.py` slaat ze over als Node te oud is, zodat een crawl er nooit
  door strandt. Een echte **Excel** of LibreOffice met rekenblad is er niet.

## Open punten

In volgorde van belang.

1. **Het GitHub-token verloopt.** Zonder werken Crawl starten en Crawl stoppen niet meer (de foutmelding
   zegt "GitHub weigerde …"). Kijk onder GitHub › Settings › Developer settings › Fine-grained tokens
   wanneer het afloopt, zet een herinnering, maak dan een nieuw token (zelfde rechten) en vervang het
   Supabase-secret `GITHUB_TOKEN`. Een organisatie kan een nieuw token eerst moeten goedkeuren.
2. **De sitebeheerder van nederlandwereldwijd.nl inlichten (besluit 2).** We houden ons aan `robots.txt`,
   een halve seconde tussen pagina's en een herkenbare User-Agent, maar het is netjes dat ze het van ons
   horen. Dit is dringender geworden: er zijn meer en grotere crawls (Visum voor Nederland is 1.015
   pagina's, ruim 20 minuten aanhoudend verkeer), en iedereen met de link kan er één per dag starten.
3. ~~Een Excel-download één keer in Excel openen.~~ **Gedaan op 12 oktober**: opent goed, het vette woord
   staat goed. De structuurcontrole in `test.py` blijft zinvol bij elke wijziging aan `xlsx.js`.
4. **De plaatsnamencheck bijstellen** (voorstel, nog niet gedaan; zie "Plaatsnamen" hieronder). Verwacht:
   Nederlandse woorden in een naam overslaan en suggesties beperken tot plaatsen vanaf ±100.000
   inwoners, wat een groot deel van de valse twijfel wegneemt.
5. **De visumcrawls zijn gedraaid, maar nog niet nagelopen.** Visum voor Nederland gaf 2.679 spelfouten, grotendeels
   goede samenstellingen die OpenTaal niet kent (zie "In het kort"). Goedkeuren van de top van de
   lijst (`inwilligingsbrief` alleen al 864 keer) haalt het grootste deel weg. Daarna Ambassades en
   consulaten crawlen, en een nieuwe crawl van de visumdelen om te zien wat er echt overblijft.
6. **De 11 echte fouten die op 5 oktober nog op de site stonden** (zie "In het kort") opnieuw nakijken en naar
   de webredactie sturen. De sjabloonfout
   `undefined` op `reisadvies/estland`, die bij de sitebeheerder hoorde en niet bij de redactie, is
   inmiddels verdwenen. Wie dit oppakt, is nog niet aangewezen.
7. **Opruimen** (geen haast): `toegestane_gebruikers` en `is_toegestaan()` zijn ongebruikt;
   `crawl_aanvragen.max_paginas` staat sinds 5 oktober altijd op 5000; `docs/resultaten.json` zit nog in de
   git-geschiedenis van de publieke repository (citaten uit openbare pagina's); oude crawls worden nooit
   opgeruimd (16.805 bevindingen in 7 crawls; bij elke crawl komen er duizenden bij).
8. **TypoTapir** (zie hieronder) heeft eigen open punten; ze staan in `OVERDRACHT.md` van die repository.
9. **Een eigenaar bij de webredactie.** Zonder eigenaar verdwijnt zo'n prototype. Die beheert de lijst
   met goedgekeurde woorden (`goedgekeurd`), loopt de namen na, en start de crawl.

## TypoTapir, de Engelstalige zusterapp

Op 12 oktober is een kopie van deze app gemaakt voor [netherlandsworldwide.nl](https://www.netherlandsworldwide.nl):
**TypoTapir**, repository [NWW-team/TypoTapir](https://github.com/NWW-team/TypoTapir), eigen Supabase-project
(`zasfgsgmbapnhfsnqsrp`, eu-west-1), eigen secrets en eigen Pages-link. Het is bewust een **kopie** en geen
taaloptie in deze app: de goedgekeurde woorden zijn één lijst zonder taal, en de woordenlijst, de teksten en de
regels voor namen en apostrofs zijn Nederlands. Wat anders is: Brits Engels met -ise (Debian-pakket `wbritish`,
SCOWL), één deel (`visa-the-netherlands`), vertalingen (`.fr`, `.es`, `.de`, `/fr`, `/es`, `/de`) worden niet
gecrawld, en het logo is een tapir. Alles wat hier staat over de werking geldt daar ook. De stand en de open
punten staan in de `OVERDRACHT.md` van TypoTapir. **Een wijziging die in beide apps hoort, moet je twee keer
doen.** Pas een deel van de code pas aan als je bedoelt dat het alleen hier moet.

## Verder werken in een nieuwe chat

Alles wat Claude nodig heeft staat in de repository en in dit document. Zet in de nieuwe chat de volgende
dingen klaar:

1. **Toegang.** De GitHub-koppeling met de repositories `NWW-team/SpellingSpeurneus` (en `NWW-team/TypoTapir`)
   en de Supabase-koppeling. Zonder koppelingen kan Claude de code wel lezen, maar geen pull request maken of
   iets in de database doen. Zet de sites onder *Allowed domains* van de omgeving als Claude de site moet
   kunnen bekijken (nederlandwereldwijd.nl en netherlandsworldwide.nl).
2. **Een eerste bericht**, bijvoorbeeld:

   > Lees `OVERDRACHT.md` en `README.md` in NWW-team/SpellingSpeurneus (dit is de Nederlandse app; er is ook
   > een Engelstalige zusterapp, NWW-team/TypoTapir). Daarna wil ik: …

3. **Werkafspraken** die tot nu toe golden en die Claude uit dit document niet kan raden:
   - Antwoorden in het Nederlands, kort, met erbij wat is gecontroleerd en wat niet (een echte browser, Excel
     en de live site zijn vaak niet te testen).
   - Een wijziging per verzoek, gecommit en gepusht op `claude/serene-allen-blqd14`. **Een pull request, mergen
     en deployen gebeuren pas na een uitdrukkelijk verzoek**; Claude vraagt dat na elke wijziging.
   - Schrijven in Supabase (migratie, Edge Function, gegevens verwijderen) alleen na akkoord, en liefst met
     de telling van wat er verandert vooraf.
   - Sleutels en tokens nooit in de chat: de service-role key zet de redacteur zelf als GitHub-secret, het
     GitHub-token als Supabase-secret. De publishable key mag wel in de code.
   - Na het mergen van `docs/` een minuut of twee wachten en hard verversen; Claude kan de Pages-link zelf niet
     openen.
4. **Checklist bij een nieuwe wijziging aan het scherm:** `python3 scripts/test.py --offline`; het script in
   `docs/index.html` op syntaxis (`node --check`); versienummer van `xlsx.js` of het icoon verhogen als je die
   wijzigt; README en dit document bijwerken als het gedrag of de kolommen veranderen.

## Besluiten

De nummers staan in code en commentaar (`besluit 6` en dergelijke); ze zijn dus niet opgeschoond.

**1. De eigennamen: gescheiden, niet weggegooid.** (14 september) Van de 614 meldingen op de eerste crawl
waren er 573 een plaatsnaam, organisatie of anderstalige bronnaam middenin een zin, en daarin zat geen
enkele verkeerd gespelde plaatsnaam. OpenTaal kent geen namen, dus de app kon een foute naam niet
herkennen. Gekozen is voor twee lijsten in hetzelfde resultaat: **spelfouten** (open bij binnenkomst)
en **namen** (ontdubbeld, met aantal pagina's). De regel: een hoofdletter middenin een zin is een naam
(`soort_van` in `crawl.py`); een vergeten spatie (`III.Let`) gaat voor. Sinds 5 oktober beoordeelt GeoNames
de namen (zie hieronder) en kan de redactie namen goedkeuren of naar de spelfouten verplaatsen.

**2. De sitebeheerder inlichten.** Open: zie Open punten.

**3. De bevindingen achter een inlog.** (15 september) **Teruggedraaid door besluit 6.** De inlog zat in
Supabase Auth met een allowlist; hij schermde de gegevens af, niet de pagina.

**4. Moet de pagina zelf ook privé?** Vervallen met besluit 6. Voor wie het ooit wil: GitHub Pages kan geen
toegangscontrole; dan is andere hosting nodig (bijvoorbeeld Cloudflare Access ervoor).

**5. Wie beheert de allowlist?** Vervallen met besluit 6.

**6. De inlog gaat weer weg.** (2 oktober) Op verzoek van de redactie is er geen inlogscherm meer en zijn
de bevindingen leesbaar voor iedereen met de publishable key, die in `docs/index.html` in een publieke
repository staat. De pagina is via een link bereikbaar die niet wordt aangekondigd, maar **dat is geen
toegangscontrole**: wie de repository leest, vindt de link en de key. Bewust gekozen, met het risico erbij.
Gevolgen die je moet kennen:
- Iedereen met de key kan **woorden en namen goedkeuren, namen verplaatsen, een crawl starten en een
  lopende crawl stoppen**. De bescherming is een limiet (300 wijzigingen per uur; één crawl per dag),
  een bevestigingsvraag bij starten en stoppen, en dat alles terug te draaien is en wordt bewaard. Een
  kwaadwillende kan echte fouten wegwerken met Goedkeuren, of de dagelijkse crawl opmaken. Kijk af en toe
  op het tabblad Goedgekeurd.
- Wil de redactie dit ooit dichtzetten, dan is een inlog of een code de weg, en dat vraagt andere hosting
  dan GitHub Pages voor het scherm.

## Hoe de toets werkt, en wat we ervan weten

- Een woord wordt getoetst aan de **OpenTaal-woordenlijst** (413.000 vormen, vastgelegd met een sha256 in
  `data/opentaal.sha256`; de workflow waarschuwt als hij verandert) en aan de lijst `goedgekeurd`.
- **De hoofdletterregel is alleen op reisadviezen geijkt.** Reken op de eerste crawl over onbekend terrein
  op ~2,2 valse meldingen per pagina (gemeten: 0,84 op de al opgeschoonde eerste 50, 2,19 op de 176 die
  daarna voor het eerst langskwamen). Dat is de aard van zo'n lijst, geen fout.
- **Sjabloonresten** (`undefined`, `[object Object]`, `{{titel}}`, `&nbsp;`) worden altijd gemeld, bovenaan.
  Het scherm toont ze met een eigen vakje; `SJABLOONRESTEN` in `crawl.py` en `SJABLOONREST` in
  `docs/index.html` moeten gelijk blijven.
- **Anderstalige woorden zonder hoofdletter** (`and`, `for`, `travel`) staan bij de spelfouten. Ze zijn op
  15 september door de redactie goedgekeurd, met als gevolg dat een Engels woord middenin een Nederlandse
  zin nooit meer opvalt; dat is hun keuze. Voor nieuwe gevallen geldt hetzelfde.
- **`persoons-`** uit "persoons- en bagagecontrole" wordt getoetst als `persoons`: bij een weglatingsstreepje
  is niet vast te stellen wat het hele woord is.
- **Huisstijl:** `lhbtiq+` altijd met de plus (zonder plus meldt de app het); `mpox` en `apenpokken` staan
  allebei goed omdat de site beide gebruikt; `etc` is goed (de zinsopdeling haalt de punt weg).
- **De lijst met goedgekeurde woorden** is op 2 oktober uit `data/uitzonderingen.txt` (280 woorden, in vijf
  rondes gegroeid, de laatste twee van de redactie) in de database ingeladen en uit de repository
  gehaald. De geschiedenis staat in git. Wat de redactie nu goedkeurt is er direct, en de volgende crawl
  slaat het over.

### Plaatsnamen (GeoNames)

Elke naam krijgt een oordeel (`scripts/plaatsnamen.py`): **bekend** (staat in GeoNames, accenten tellen niet
mee), **twijfel** (staat er niet in maar lijkt op een bekende plaats, met suggestie) of **onbekend**. Alleen
buitenland. Het matchen is Damerau-Levenshtein met de grens 1 (woorden van 5 tot 8 letters) of 2 (vanaf
9); woorden korter dan 5 letters krijgen geen suggestie; de eerste letter moet gelijk zijn. Suggesties komen
uit plaatsen vanaf 15.000 inwoners (`MIN_INWONERS_SUGGESTIE`), regio's en landen; "bekend" telt alle plaatsen
vanaf 1.000 inwoners met alle alternatieve namen. De workflow haalt GeoNames per run op (CC BY 4.0, vermeld
in README en voettekst); mislukt dat, dan krijgen namen geen oordeel en gaat de crawl door.

**Eerste meting (5 oktober, 236 reisadviezen):** 1.380 unieke namen: 884 bekend, 98 "lijkt op", 398 zonder
oordeel. De 98 zijn door mij doorgelezen, **niet door de redactie nagelopen**: ongeveer een kwart zijn
echte tikfouten of afwijkende schrijfwijzen (`Bahamar`, `Guyaquil`, `Hairi`, `Mauritus`, `Noukachott`,
`Snedai`, `Karakalkpakstan`). De rest is valse twijfel, in vier soorten:
1. **Een Nederlands woord als deel van een naam**: `EHIC-kaart` en `Express-kaart` ~ `Kaarst`,
   `Paleski-reservaat` ~ `Reserva`, `Chaambi-gebergte`, `Gedeo-zone`, `Khamsin-wind`.
   Oplossing: delen die in de woordenlijst staan overslaan.
2. **Gewone Engelse, Franse of Spaanse woorden**: `Survey` ~ `Surrey`, `Waiver` ~ `Waver`, `Campaign`,
   `Danger`, `Local`, `Markets`, `Prefectural`, `Observatory`, `Meteo`. Oplossing: een hogere
   inwonersgrens voor suggesties.
3. **Echte plaatsen die ontbreken** (kleiner dan 1.000 inwoners, of geen stad): `Tikal`, `Sinabung`, `Marapi`,
   `Wagah`, `Moorea`. Goedkeuren lost het blijvend op.
4. **Landnamen in een andere taal of met trema**: `Transnistrië` ~ `Transnistria`, `Polynésie`, `Latvija`.

Beperkingen: een naam die alleen in het buitenland bestaat maar op de pagina iets anders bedoelt, valt niet
op; `Cordoba` naast `Córdoba` zijn beide "bekend", dus een accentverschil tussen pagina's wordt niet
gemeld; een suggestie is een hint, geen oordeel.

## Risico's en bekende beperkingen

- **Een gestopte crawl laat niets achter**, maar wat tot dan toe is gevonden gaat verloren: de crawl
  publiceert pas aan het eind. Stoppen kan niet tijdens het opslaan. Er blijft een gat van een seconde
  tussen de controle en het annuleren; valt een klik daar precies in, dan staat er een onvolledige crawl
  in `crawls`: verwijder die dan met de hand.
- **Het Supabase-project was op 2 oktober tijdelijk "COMING_UP"** en toonde even een lege database (de
  tabellen kwamen daarna terug). De oorzaak is niet vastgesteld. Het gratis niveau pauzeert een project
  na een tijd zonder gebruik; dat is een aanname. Controleer bij vreemd gedrag eerst de projectstatus.
- **Alleen de tekst in `<main>`** wordt gelezen. Menu's, voetteksten en cookiemeldingen blijven buiten
  beeld. Verandert de site van structuur, dan is dit de aanname die als eerste breekt. Eén taal: komen er
  anderstalige pagina's, dan meldt de app ze als één grote fout.
- **Een crawl over een deel waar de sitemaps geen enkele URL meer voor hebben** stopt met een foutmelding,
  in plaats van stil niets te doen.
- Een late melding van de runner kan een gestopte of mislukte aanvraag niet meer op "crawlen" zetten (de
  update werkt alleen op lopende aanvragen).
- **Het scherm** is getoetst in Chromium met nagemaakte gegevens, niet in Safari of Firefox, en de pagina
  schuift niet zijwaarts van 280 tot 1.200 pixels breed (gemeten).

## Wat er bewust niet in zit

Grammatica, stijl en d/t-fouten · alle pagina's van de site in één run (alleen de vier delen) · continu of
gepland scannen · meerdere talen · terugschrijven naar het CMS · inloggen, rollen of rechten per gebruiker ·
bevindingen bewaren om trends over tijd te zien (de oude crawls staan er wel, maar het scherm toont alleen de
nieuwste) · afgeschermde of interne pagina's · een maximumaantal pagina's per crawl.

## Vormgeving

Het scherm benadert de Rijkshuisstijl in de **kleuren** (donkerblauw, hemelblauw, geel markeerveld), elke
tekstkleur op WCAG AA-contrast getoetst, in de lichte en de donkere stand. Er zit bewust **geen logo,
woordmerk of Rijksoverheid-lettertype** in, zodat de pagina niet voor een officiële pagina van de
Rijksoverheid wordt aangezien; het icoon is de eigen hond van de app. Wie het verder officieel wil maken,
moet dat eerst met de huisstijlbeheerder bij BZ afstemmen. Zie "Vormgeving" in [README.md](README.md).
