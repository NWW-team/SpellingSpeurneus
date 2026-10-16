-- Het deel "Afspraak maken" (pad /afspraak-maken) erbij als keuze voor een crawl. 'ambassades' blijft
-- in de lijst staan, zodat oude aanvragen met die bron geldig blijven; het scherm biedt hem niet meer aan.

alter table public.crawl_aanvragen drop constraint crawl_aanvragen_bron_check;
alter table public.crawl_aanvragen
  add constraint crawl_aanvragen_bron_check
  check (bron in ('reisadvies', 'visum-nederland', 'caribisch-visum', 'afspraak-maken', 'ambassades'));
