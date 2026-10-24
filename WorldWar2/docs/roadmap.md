# Roadmap and known gaps

Status: proof of concept covering the Western Front, 6-30 June 1944 (212 claims, 81 units).

## Known gaps in the current data

**Coverage left out (no verified dates or too thin sources):**
- British XII Corps (arrival date not found), II Canadian Corps and First Canadian Army (July); 12th Army Group (operational 1 August, HQ unknown).
- Free French, 1st Special Service Brigade and the 2nd Canadian Armoured Brigade after D-Day.
- German Fifteenth Army, Luftwaffe units, the 319th Division (Channel Islands), 85th, 89th and 116th Panzer (arrive July).
- US 5th, 8th, 28th and 35th Divisions and 4th Armored (July).
- Battle groups: Hellmich (formed about 9-10 June), Hoffmann, Keil and Mueller (Cotentin, undated in the source), and the US 4th Division task forces are sourced but not yet added because the date or place was too vague.
- Roughly 40-60 German units that fought in the sector (regiments, Kampfgruppen, Ost battalions) are only partially represented.

**Data quality:**
- Rows are event-based; quiet days are absent, so positions between rows are unknown.
- Many corps, army and panzer-corps headquarters positions are not tied to a dated source (inferred or approximate). HQ moves are poorly covered by free web sources.
- Composition lists are the standard organisation checked against Wikipedia unit pages, not the exact attachments each day. Not verified: US 2nd and 3rd Armored combat commands, 21st Panzer "Panzer Regiment 22", 79th Armoured and independent brigades (marked `unknown`).
- `parent_formation` is time-dependent and some links are only supported in outline (for example I SS Panzer Corps under Seventh Army or Panzer Group West; II SS Panzer Corps on 28-29 June). Where no link was found it is `unknown` (18 rows in v4).
- `precision_km` and `confidence` are rule-derived (see methodology); they are consistent but not independent measurements.
- `strength_json` is sparse (21 rows) and rests on secondary sources; no row uses `authorized_organization` yet.
- Date conflicts between sources are open (Dollmann's death, Schlieben's capture, Choltitz replacing Fahrmbacher, Montgomery's HQ moves, 82nd Airborne at Pont-l'Abbe): see the 11 conflict groups.
- Wikipedia is a first-pass source; many rows should be re-verified against primary or semi-primary sources.

## Scale-up plan

1. **Stable unit and place tables.** Keep `data/units.csv` as the unit authority (add formation and disbandment dates, alternative names, higher parent chain) and add a place table with coordinates, historical names and source, referenced by claims.
2. **Better sources for order of battle**: US Army Green Books (CMH), Joslen's *Orders of Battle* (British), the Canadian official history, German OOB references (Tessin, *Lexikon der Wehrmacht*, axishistory), and Soviet *Boevoi sostav* lists. Use Wikipedia as a first pass only.
3. **Per-row evidence**: add a quote or page reference (not only a URL) and a separate `coordinate_source` column, plus a coordinate precision type (point / town / sector), so a coordinate can be re-checked.
4. **Batch geocoding with a cache** (GeoNames or Wikidata with Nominatim as a fallback) and a gazetteer with historical names (places change names, for example Octeville / Cherbourg-Octeville).
5. **Split by theater and month**: new theaters get their own `theater` value and folders stay by nationality, so contributors can work independently. Crawl each campaign page and its OOB page, then run a verification pass that checks date, place, unit and echelon against two sources before a row is accepted.
6. **Weaker source bases**: the Eastern Front and the Pacific need Russian and Japanese-language sources and atlases (Glantz-type), so expect lower confidence and more conflict groups.
7. **Tooling**: a dataset browser (map and timeline) generated from `build/claims.geojson`, CSV and GeoJSON releases with a changelog, a Frictionless data package descriptor, and unit tests for the scripts.
8. **Community**: issue and PR templates, a review rota for source checking, and tagged releases with a changelog.

## Open design questions

- Per-day interpolation versus pure event rows (currently pure events).
- Whether a unit's primary `theater` should be derived from its claims once several theaters exist (currently set by hand in `units.csv`).
- Whether `parent_formation` should become a separate time-dependent relations table instead of free text.
