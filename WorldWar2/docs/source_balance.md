# Source nationality balance (survey, 10 November 2026)

Survey and plan, then a re-measure after the first recommended step. The tables in this page are the baseline from `data/references.csv` and `build/all_claims.csv` on main `a8b9509` (8,963 claims, of which 8,814 preferred, 133 alternate, 16 disputed), taken on branch `source-balance` when no claims were added or changed. After the Ellis leftover-entry pass the same script was run again; those shares are in [Ellis leftover-entry pass (re-measured 10 November 2026)](#ellis-leftover-entry-pass-re-measured-10-november-2026).

The review queue already hints at own-nation official histories by unit nationality (`docs/coverage_report.md`). This page measures how far the citations actually go, names the thinnest areas, and lists free non-US sources worth reading next.

## How sources were classified

References have **no nationality field**. Each reference was classified from its `source_family`, with publisher or author as a fallback when the family name is ambiguous. Gazetteer and geocoder references (OpenStreetMap, GeoNames, and Wikipedia coordinates `R001`) are excluded, as in `scripts/coverage.py`: they place a point, not the unit.

Authorship, not the holding archive, decides nationality:

- FMS manuscripts (German officers, US Army Historical Division / Fold3) and NARA captured German records count as **German**.
- The 12th Army Group situation maps (`R781`) count as **US**.
- Stacey and Veterans Affairs Canada count as **Canadian official**; Ellis as **British official**; de Lattre as **French**; de Jong (`niod_dejong_koninkrijk`) as **Dutch official history**, counted as Dutch own-nation.
- Wikipedia (any language) is its own bucket and is **never** treated as an own-nation source.
- `thesecondwar_pl` is a Polish website used for two US corps pages; it is counted as Other, not as a Polish official history.
- French local-history sites (Ouest-France, D-Day Overlord, Wikimanche and the like) are a weak French group, used mainly for headquarters places, not official campaign histories.

A claim may cite several families, so the bucket percentages below are multi-label and sum to more than 100%. "Exclusive" means every supporting source on the claim is from that nationality (or Wikipedia, or Other).

## Claims citing each source group

| Source group | Refs | Claims citing | Share of all | Preferred citing | Share of preferred |
|---|---:|---:|---:|---:|---:|
| US official histories (CMH) | 242 | 1,502 | 16.8% | 1,492 | 16.9% |
| US maps (12th Army Group situation maps) | 1 | 4,831 | 53.9% | 4,744 | 53.8% |
| US unit histories | 8 | 25 | 0.3% | 24 | 0.3% |
| US other (compilations, popular, memorials, archives) | 44 | 125 | 1.4% | 125 | 1.4% |
| British official (Ellis) | 2 | 229 | 2.6% | 229 | 2.6% |
| British other (unit/web histories) | 6 | 4 | 0.0% | 4 | 0.0% |
| Canadian official (Stacey / VAC) | 2 | 774 | 8.6% | 772 | 8.8% |
| German (FMS manuscripts) | 75 | 1,285 | 14.3% | 1,263 | 14.3% |
| German (Lexikon / Tessin) | 215 | 460 | 5.1% | 449 | 5.1% |
| German (NARA captured records) | 20 | 100 | 1.1% | 100 | 1.1% |
| German (Schramm / OKW KTB) | 1 | 25 | 0.3% | 23 | 0.3% |
| German (Bundesarchiv / EHRI and other) | 2 | 3 | 0.0% | 2 | 0.0% |
| French (de Lattre) | 1 | 69 | 0.8% | 68 | 0.8% |
| French (archives and local history) | 9 | 9 | 0.1% | 6 | 0.1% |
| Dutch (local history) | 3 | 2 | 0.0% | 2 | 0.0% |
| Wikipedia | 236 | 459 | 5.1% | 437 | 5.0% |
| Other (web, memorials) | 4 | 7 | 0.1% | 6 | 0.1% |

Rolled up by source nationality (multi-label, then exclusive):

| Source nationality | Claims citing | Share | Exclusive claims | Share exclusive |
|---|---:|---:|---:|---:|
| US | 6,355 | 70.9% | 5,915 | 66.0% |
| Germany | 1,793 | 20.0% | 1,457 | 16.3% |
| Canada | 774 | 8.6% | 564 | 6.3% |
| Wikipedia | 459 | 5.1% | 197 | 2.2% |
| UK | 233 | 2.6% | 122 | 1.4% |
| France | 77 | 0.9% | 45 | 0.5% |
| Other | 7 | 0.1% | 0 | 0.0% |
| Netherlands | 2 | 0.0% | 0 | 0.0% |
| Poland | 0 | 0.0% | 0 | 0.0% |

Two facts stand out. First, the 12th Army Group maps alone are cited by 53.9% of all claims (4,826 of them cite that family and no other supporting source). Second, there is **no Polish-authored reference** in the table at all.

## Own-nation support, by the unit's nationality

"Own-nation" means a supporting source of that unit's nationality, as classified above. "Only US or Wikipedia" means every supporting source is US and/or Wikipedia (including map-only rows).

| Unit nationality | Claims | With an own-nation source | Only US sources | Only Wikipedia | Only US or Wikipedia |
|---|---:|---:|---:|---:|---:|
| US | 3,072 | 2,933 (95.5%) | 2,820 | 89 | 89 (2.9%) |
| Germany | 4,020 | 1,732 (43.1%) | 2,079 | 24 | 2,152 (53.5%) |
| UK | 1,030 | 187 (18.2%) | 631 | 56 | 692 (67.2%) |
| Canada | 498 | 311 (62.4%) | 183 | 0 | 184 (36.9%) |
| France | 235 | 42 (17.9%) | 164 | 11 | 190 (80.9%) |
| Poland | 81 | 0 (0.0%) | 35 | 2 | 37 (45.7%) |
| Belgium | 14 | 0 (0.0%) | 3 | 8 | 11 (78.6%) |
| Netherlands | 8 | 0 (0.0%) | 0 | 6 | 6 (75.0%) |
| Czechoslovakia | 5 | 0 (0.0%) | 0 | 1 | 1 (20.0%) |

The other Polish, Dutch, Belgian and Czechoslovak claims are supported by Stacey and/or Ellis, not by a source of the unit's own nationality. British claims already cite Ellis on 185 rows and Stacey on 188; most of the rest are 12th Army Group map rows (627 of 1,030 UK claims, 60.9%, are map-only).

Map-only shares for comparison: US 67.7%, France 64.3%, UK 60.9%, Germany 43.5%, Poland 43.2%, Canada 36.7%.

## Thinnest areas

### Units with no own-nation source at all

Fourteen non-German, non-US units have no own-nation citation on any row:

| Unit | Claims | Map-only | Dates | What supports them now |
|---|---:|---:|---|---|
| 1st Polish Armoured Division (`POL-ARM-001D`) | 76 | 35 | Aug 1944 – May 1945 | Stacey, Ellis, a few FMS and Wikipedia rows; 35 map-only |
| French First Army (`FR-ARMY-001A`) | 26 | 21 | Aug 1944 – May 1945 | CMH and maps only (no de Lattre row on the army itself) |
| French II Corps (`FR-COR-002C`) | 25 | 23 | Sep 1944 – May 1945 | CMH and maps |
| Brigade Piron (`BEL-INF-001B`) | 14 | 3 | Aug 1944 – Apr 1945 | Wikipedia, maps, Stacey, Ellis |
| Princess Irene Brigade (`NL-INF-IRNEB`) | 8 | 0 | Aug 1944 – Apr 1945 | Wikipedia (6), Ellis/Stacey (2) |
| French I Corps (`FR-COR-001C`) | 6 | 3 | Sep 1944 – May 1945 | Wikipedia and maps |
| Czechoslovak Armoured Brigade (`CZ-ARM-001B`) | 5 | 0 | Aug 1944 – May 1945 | Stacey, Ellis, Wikipedia |
| Polish Parachute Brigade (`POL-ABN-001B`) | 5 | 0 | Sep 1944 | Ellis, Stacey, Wikipedia |
| 14th DI (`FR-INF-014D`) | 4 | 2 | Feb–May 1945 | Wikipedia and maps |
| 10th DI (`FR-INF-010D`) | 2 | 0 | Oct 1944, Feb 1945 | Wikipedia, CMH |
| Atlantic Army Detachment, 27th Alpine, Gironde marching division | 1 each | 0 | 1944–45 | Wikipedia |
| 79th Armoured Division (`UK-ARM-079D`) | 1 | 0 | 6 June 1944 | Wikipedia only |

French divisions that *do* have de Lattre still have most of their later rows from maps (for example the 3rd DIA, 39 claims, 31 map-only; the 2d Armored Division, 50 claims, 34 map-only).

British divisions and corps almost all have some Ellis rows, but own-nation share stays low because the maps fill the calendar. The weakest months for British own-nation support are October 1944 (3.9% of UK claims cite a British source), November 1944 (8.1%) and December 1944 (5.1%). May 1945 is also thin (20.0%), which matches the leftover from official-history pass 1: Ellis gives no 8 May positions.

Canadian own-nation support is stronger (62.4%) because Stacey was read cover to cover, but December 1944 (23.1%) and January 1945 (16.7%) are mostly map rows. Those are the months where a second Canadian family would help most.

French March 1945 is entirely without a French source (24 claims, all US or Wikipedia). December 1944, January and February 1945, and May 1945 are also above 88% US or Wikipedia.

Every Polish month has 0% own-nation support. The 35 map-only rows of the 1st Armoured Division (October 1944 to February 1945 especially) are the largest single hole for a non-US, non-German unit.

Germany is better served than the smaller Allies (43.1% of claims have a German source: FMS, Lexikon, NARA or Schramm), but 2,152 German claims (53.5%) are still only US or Wikipedia, and 32 German units have no German source at all. Nine of those have five or more claims, led by the 344th Infantry Division (12, mostly maps), Panzer-Brigades 112 and 113, XIV SS Corps, and the 18th VGD. Mid-war German ends and the 66 units of unknown end type in roadmap 372 remain source-limited; they are not the first target of this balance pass.

## How far existing non-US official sources have been read

These four are already references. How they were read is taken from `docs/sources.md`, the roadmap, the changelog, and (for coverage only, not quotations) the private notes.

**Stacey, *The Victory Campaign* (`R668`, family `canada_ca`).** Canadian official history, Vol. III, 1960. Free PDF from DND/DHH, confirmed live (HTTP 200): [canada.ca official-histories page](https://www.canada.ca/en/department-national-defence/services/military-history/history-heritage/official-military-history-lineages/official-histories/book-1960-army-ww2-3.html) and the file `book-1960-army-ww2-3-en.pdf`. Cited by 773 claims. Canadian Batches 1 and 2, the allied-contingents batch, and a cover-to-cover pass on branch `stacey-victory-campaign` (3 November 2026) already used it. A new cover-to-cover reading is not the first need; a second Canadian family would help the remaining map-only Canadian rows.

**Ellis, *Victory in the West*, vol. I (`R670`) and vol. II (`R671`, family `uk_official_history`).** British official history, HMSO 1962 and 1968. Free full-text scans on the Internet Archive: [vol. I](https://archive.org/details/victory-west-vol-1) and [vol. II](https://archive.org/details/victory-west-vol-2). Cited by 89 and 140 claims (229 claims cite one or both) on main `a8b9509`. After the leftover-entry pass: 140 and 184 (324 claims cite one or both). British Batches 1 and 2 and the official-history passes used selected pages. Private notes from 30 October 2026 record a cover-to-cover reading of both volumes (narrative, appendices and maps). Compared with an earlier state of `main`, those notes marked on the order of 350 (vol. I) and 610 (vol. II) facts as not then in the dataset, plus many units then absent. Some of those facts may have been entered since; a leftover-entry pass should re-check against current `main` before writing rows. This is the largest unused pool of already-read, free, official non-US material.

**de Lattre, *The History of the French First Army* (`R686`).** Army commander's account, English translation 1952 (French original Plon 1949). Internet Archive copies are borrow-only / print-disabled (the cited item is `bwb_W7-ADK-972`; another scan, `historyoffrenchf0000latt`, is the same). In copyright. Cited by 69 claims (42 of 235 French unit claims). Private notes already exist; compared with an earlier `main` they marked on the order of 140 facts as not then entered. The French First Army, I and II Corps, and March 1945 still have no de Lattre row.


## Ellis leftover-entry pass (re-measured 10 November 2026)

The first recommended step — entering leftover facts already noted from Ellis, *Victory in the West*, vols I and II — was completed on branch `ellis-leftovers` (PR #84) on 10 November 2026, in six chunks (`C8975`–`C9017`). The method is unchanged: the same survey script, run on `build/all_claims.csv` of that branch (9,006 claims, of which 8,856 preferred, 134 alternate, 16 disputed). The tables above remain the baseline on main `a8b9509`.

### Shares before and after

| Measure | On main `a8b9509` | After the leftover pass |
|---|---|---|
| Claims (preferred / alternate / disputed) | 8,963 (8,814 / 133 / 16) | 9,006 (8,856 / 134 / 16) |
| US sources, citing / exclusive | 70.9% / 66.0% | 70.6% / 65.7% |
| 12th Army Group maps, share of all claims | 53.9% | 53.6% |
| British official (Ellis), claims citing | 229 (2.6%) | 324 (3.6%) |
| Ellis vol. I / vol. II (`R670` / `R671`) | 89 / 140 | 140 / 184 |
| UK sources, citing / exclusive | 2.6% / 1.4% | 3.6% / 1.8% |
| Canadian official (Stacey), claims citing | 774 (8.6%) | 774 (8.6%) |
| Canada sources, exclusive | 6.3% | 5.9% |
| UK units, own-nation / only US or Wikipedia | 18.2% (187 of 1,030) / 67.2% (692) | 23.1% (247 of 1,071) / 63.9% (684) |
| Canadian units, own-nation / only US or Wikipedia | 62.4% (311 of 498) / 36.9% | 62.3% (311 of 499) / 36.9% |
| Polish units, own-nation | 0.0% (0 of 81) | 0.0% (0 of 81) |
| German units, own-nation | 43.1% | 43.1% |
| US units, own-nation | 95.5% | 95.5% |
| Non-US, non-German units with no own-nation source | 14 | 13 |

Canadian exclusive-source share fell (6.3% to 5.9%) because Ellis was added as a supporting official citation on existing Stacey rows; those claims now cite two source nationalities. Canadian own-nation support is almost unchanged: Ellis is not treated as a second independent family for Canadian-unit facts, and the one new Canadian claim (`C9013`) cites only Ellis, so the own-nation count stayed at 311 while the denominator rose by one. Polish own-nation support stays at zero: there is still no Polish-authored reference. Two existing Polish rows gained an Ellis citation in chunk 1; leftover notes for later Polish named places were re-checked and were not entered where the Ellis text does not confirm the same place and date.

British own-nation support rose from 18.2% to 23.1% (187 to 247 claims). The 79th Armoured Division, which had a single Wikipedia-only D-Day row, now has 16 Ellis-supported claims and has left the no-own-nation list. October and November 1944 improved (3.9% to 19.3%, and 8.1% to 15.7%); December 1944 is still thin (5.1% to 6.7%). May 1945 is unchanged at 20.0%, which still matches the leftover from official-history pass 1: Ellis gives no 8 May positions.

US citing and exclusive shares dipped only because 43 new claims that do not cite a US source were added; the absolute US counts are unchanged (6,355 citing, 5,915 exclusive).

The remaining recommended steps (CMHQ/AHQ reports, de Lattre leftovers, de Jong, Joslen, and a Polish-authored source) are unchanged.

## CMHQ/AHQ reports pass (re-measured 11 November 2026)

The second recommended step — reading the free DHH CMHQ/AHQ reports as a second Canadian family — was done on branch `cmhq-ahq-reports` (PR #85) on 11 November 2026, in twelve chunks: CMHQ Reports 173, 186, 155, 188, 183, 184 and 181 and AHQ Reports 39, 32, 19, 65 and 58 (`R882`-`R893`, family `canada_dhh_reports`). 548 existing rows gained a supporting citation (49 confidence raises), 226 claims were added (`C9018`-`C9243`) and 73 places (`PL4017`-`PL4089`). The same survey script was run on `build/all_claims.csv` of `main` `dbdfffe` (after PR #84) and of the branch, with one change: the new family `canada_dhh_reports` is classified as Canadian official and counts as own-nation for Canadian units (it is not own-nation for Polish, British or German units).

### Shares before and after

| Measure | On main `dbdfffe` (after the Ellis pass) | After the CMHQ/AHQ pass |
|---|---|---|
| Claims | 9,006 | 9,232 |
| Claims citing a DHH report (`canada_dhh_reports`) | 0 | 749 (8.1%) |
| Canada sources, citing / exclusive | 8.6% (774) / 5.9% | 12.3% (1,136) / 8.2% |
| Canadian units, own-nation / only US or Wikipedia | 62.3% (311 of 499) / 36.9% (184) | 76.4% (450 of 589) / 23.3% (137) |
| Canadian units, December 1944 / January 1945 own-nation | 23.1% / 16.7% | 69.0% / 56.8% |
| Polish units, own-nation / only US or Wikipedia | 0.0% (0 of 81) / 45.7% (37) | 0.0% (0 of 90) / 32.2% (29) |
| UK units, own-nation | 23.1% (247 of 1,071) | 21.8% (247 of 1,135) |
| German units, own-nation | 43.1% | 42.5% |
| US sources, citing / exclusive | 70.6% / 65.7% | 68.8% / 63.1% |
| 12th Army Group maps, share of all claims | 53.6% | 52.3% |
| Non-US, non-German units with no own-nation source | 13 | 13 |

Canadian own-nation support rose from 62.3% to 76.4%, and the two thin months named above, December 1944 and January 1945, rose from 23.1% and 16.7% to 69.0% and 56.8% (mostly CMHQ Report No. 173, *The Watch on the Maas*). The baseline figure of 62.4% in the tables above is on main `a8b9509`; on `dbdfffe` it was 62.3%. Polish own-nation support stays at zero, because the reports are Canadian-authored; but the Polish division gained 9 report-based rows and its map-only rows fell from 35 to 27. British own-nation share fell slightly because the new British rows of First Canadian Army formations cite the Canadian reports, not Ellis. The remaining recommended steps (de Lattre leftovers, de Jong, Joslen, and a Polish-authored source) are unchanged.


## De Lattre leftovers pass (re-measured 12 November 2026)

The third recommended step was done on branch `delattre-leftovers` on 12 November 2026, in six chunks. The source book (`R686`, borrow-only on the Internet Archive) could not be re-opened (401, not bypassed), so every entry came from the private pass-2 reading notes (printed pages cited, paraphrase only). 17 existing rows gained a supporting citation (4 raises), 108 claims were added (`C9244`-`C9351`) and 57 places (`PL4090`-`PL4146`). The same survey script was run on `build/all_claims.csv` of `main` `9f6dce1` and of the branch.

| Measure | On main `9f6dce1` | After the de Lattre pass |
|---|---|---|
| Claims | 9,232 | 9,340 |
| Claims citing de Lattre (`delattre_french_first_army`) | 69 (0.7%) | 194 (2.1%) |
| French sources, citing / exclusive | 0.8% (77) / 0.5% | 2.2% (202) / 1.6% |
| French units, own-nation / only US or Wikipedia | 17.9% (42 of 235) / 80.9% (190) | 46.1% (152 of 330) / 53.0% (175) |
| French units, own-nation by month | Oct 1944 14.3%, Dec 6.2%, Jan 1945 11.4%, Feb 9.4%, Mar 0.0%, May 8.7% | Oct 20.0%, Dec 28.6%, Jan 40.0%, Feb 37.2%, Mar 21.4%, May 27.6% |
| Focus units with no own-nation source | 13 | 9 (French 8 to 4) |
| US sources, citing / exclusive | 68.8% / 63.1% | 68.0% / 62.3% |
| 12th Army Group maps, share of all claims | 52.3% | 51.7% |

French own-nation support rose from 17.9% to 46.1% and March 1945, which had none, to 21.4%. The French First Army, I Corps, II Corps and the 10th Division now have an own-nation source; the 14th and 27th Divisions, the Atlantic Army and the Gironde detachment still have none. De Lattre's own wording is partisan on the disputes with Devers and SHAEF, and the German rows record his reading of the enemy, so they enter at 0.3. Chunk 6 added `IT` to the `places.csv` country vocabulary (Scott approved, 12 November 2026) and entered the four Italy and Elba rows (theater `mediterranean`, `C9348`-`C9351`, places `PL4143`-`PL4146`). Remaining recommended steps: de Jong, Joslen, and a Polish-authored source.

## de Jong deel 10a-1 pass (re-measured 12 November 2026)

The fourth recommended step was started on branch `dejong-10a1` on 12 November 2026, in four chunks, from NIOD's CC-BY edition of L. de Jong, *Het Koninkrijk der Nederlanden in de Tweede Wereldoorlog*, deel 10a part 1 (`R894`, chapters 1-7, printed pp. 1-531; family `niod_dejong_koninkrijk`, new bucket "Dutch official history"). 29 existing rows gained a supporting citation (5 raises), 27 claims were added (`C9352`-`C9378`) and 2 places (`PL4147`-`PL4148`). The same survey script was run on `build/all_claims.csv` of `main` `e8deff6` and of the branch.

| Measure | On main `e8deff6` | After the de Jong pass |
|---|---|---|
| Claims | 9,340 | 9,367 |
| Claims citing de Jong (`niod_dejong_koninkrijk`) | 0 | 56 (0.6%) |
| Dutch sources, citing / exclusive | 0.0% (2) / 0.0% | 0.6% (57) / 0.3% (27) |
| Dutch units, own-nation / only US or Wikipedia | 0.0% (0 of 14) / 42.9% (6) | 38.9% (7 of 18) / 27.8% (5) |
| Dutch units, September 1944 own-nation | 0.0% (0 of 5) | 42.9% (3 of 7); off the high US-or-Wikipedia-only month list |
| US sources, citing / exclusive | 68.0% / 62.3% | 67.8% / 62.1% |

Own-nation support for the Princess Irene Brigade, the only Dutch unit in the table, rose from none to 7 of its 18 rows (Beeringen, Grave, the Maas-Waal canal bridges, Tilburg, Walcheren). De Jong is an official history, but his military narrative leans on MacDonald, Ellis and Stacey: where the page names a Dutch source (the Eindhoven municipal diary, local historians such as de Groot and Boeree, the Albrecht archive, Nauta's letter, Dutch Commando recollections, Rauter's report) or a German document, the row counts him as an independent family; where he follows the Allied histories the row is cited without a raise (24 of the 29 citations). The Dutch share is still small in absolute terms (57 claims): volume 10a part 2 and volume 10b, and the Dutch-resistance units, are the remaining Dutch work. Remaining recommended steps: de Jong 10a-2 and 10b, Joslen, and a Polish-authored source.

## Candidate sources not yet in the references

Checked for a free official or openly released text, 10 November 2026.

| Source | Nationality | Covers | Already a reference? | Availability | Estimated value |
|---|---|---|---|---|---|
| Canadian Military Headquarters (CMHQ) reports, 1940–1948, and Army Headquarters (AHQ) reports, 1948–1959 | Canadian official (preliminary narratives that fed Stacey) | Day-level Canadian operations in NW Europe, plus several reports from German sources | No | Free official PDFs from DHH. Index: [CMHQ](https://www.canada.ca/en/department-national-defence/services/military-history/history-heritage/official-military-history-lineages/reports/military-headquarters-1940-1948.html), [AHQ](https://www.canada.ca/en/department-national-defence/services/military-history/history-heritage/official-military-history-lineages/reports/army-headquarters-1948-1959.html). Example files confirmed live: CMHQ 152, AHQ 54. | High. A second Canadian family for the 184 claims that are still only US or Wikipedia (especially Dec 1944 and Jan 1945), more HQ and day-level detail than Stacey, and German opposition (AHQ 50, 69, 77). Start with the NW Europe operational set: CMHQ 147, 162, 169, 183, 184, 188, 154, 173, 185, 186, 152, 181; AHQ 54, 58, 65, 32, 39, 19, 50, 69, 77. |
| Joslen, *Orders of Battle: United Kingdom and Colonial Formations and Units in the Second World War, 1939–1945* (HMSO, 1960, 2 vols) | British official | Formation dates, brigade composition, command changes, units in and out of the theatre | No (already named in the roadmap as a needed British OOB source) | Free PDFs are listed on the [General Staff UK official histories page](https://www.generalstaff.org/WW2/Hist_UK/UK_Official_Histories.htm). UK Crown copyright in published works lasts 50 years from the end of the year of publication, so the 1960 volumes are past that term; this is not legal advice. That host has blocked automated requests from this box (HTTP 403), as it has for Nafziger, so a copy may need to be saved in a browser or taken from an Internet Archive scan. | Medium-high for `formed_date`, independent brigades and relation dates; thin on day-to-day places. (The 79th Armoured Division now has Ellis text rows from the leftover-entry pass, but Joslen is still the better source for its composition and attachments.) |
| Loe de Jong, *Het Koninkrijk der Nederlanden in de Tweede Wereldoorlog*, deel 10a and 10b (*Het laatste jaar*) | Dutch official | The last year of occupation and the liberation of the Netherlands, 1944–1945 | No | Free from the [NIOD digital library](https://niod.contentdm.oclc.org/digital/collection/p21083coll6). Text is offered for download under CC BY 4.0 (photographs omitted). | Medium. Gives the Princess Irene Brigade (8 claims, no Dutch source) an own-nation history and adds Dutch-theatre detail for Canadian and British units. |
| *Les grandes unités françaises: historiques succincts*, tomes 5.1–5.3 (campagnes de France et d'Allemagne, 1944–1945) and tome 6 (FFI, Atlantic and Alps) | French official (SHAT / Service historique de la Défense) | Succinct official histories of French armies, corps and divisions, 1944–1945 | No | Catalogue entries exist at SHD and in departmental archives; no free full-text PDF was found. | High if a copy can be obtained: would cover the French First Army, I and II Corps, and the divisions that de Lattre does not date in March 1945. Needs Scott (library or purchase). |
| IPN, *Pancerz i odwaga. Szlak 1 Dywizji Pancernej gen. Stanisława Maczka* (2024) | Polish (Institute of National Remembrance) | The route of the 1st Polish Armoured Division | No | [IPN book page](https://ipn.gov.pl/pl/wydawnictwo/ksiazki/217316,Pancerz-i-odwaga-Szlak-1-Dywizji-Pancernej-gen-Stanislawa-Maczka.html): table of contents is free; the book itself is a paid e-book, not a free full PDF. | High for the 76-claim division with no Polish source, if Scott is willing to buy it. |
| Official *Polskie Siły Zbrojne w drugiej wojnie światowej* (Sikorski Institute, London), Tom II *Kampanie na obczyźnie* | Polish official | Polish forces in exile. The 1975 część 2 volume runs only to June 1944, so it does not cover the NW Europe campaign of the 1st Armoured Division. | No | No legal free PDF of a volume covering August 1944 – May 1945 was found. | Potentially high, but not freely available from this check; would need Scott to obtain a copy if a later part exists. |
| Maczek, *Od podwody do czołga* (1961) | Polish memoir | Commander's account of the 1st Armoured Division | No | In copyright (author died 1994). No authorised free full text relied on here. | High if a legitimate copy can be read; needs Scott (purchase or library). |
| E. A. Parthemore, *Od Normandii do Ypres* (PhD, Poznań 2011) | Unofficial (US Army officer dissertation) | Combat of the 1st Armoured Division in France, 1944 | No | Free PDF on [generalmaczek.pl](https://generalmaczek.pl/wp-content/uploads/2016/12/E.-A.-Parthemore-dysertacja-Maczek-we-Francji.compressed.pdf). | Medium, and only for France 1944; a Polish official or memoir source is preferable. |
| NIMH collection 466 (Prinses Irene Brigade) and *Van brigade en garderegiment "Prinses Irene"* (de Kort, 1983) | Dutch archive / unit history | Princess Irene Brigade | No | NIMH holds the brigade archive ([collection guide](https://www.nimh.nl/militaire-geschiedenis-van-nederland/webthemas/bevrijding-van-nederland-1944-1945/zelf-onderzoek-doen)); it is not a published PDF. The 1983 unit history is a library book, not found as a free PDF. | Medium, but needs a research request or a library copy. Prefer de Jong first. |
| British commercial divisional histories (for example Essame, *The 43rd Wessex Division at War, 1944–1945*; Martin, *The History of the 15th Scottish Division 1939–1945*) | British unit histories | Day-by-day division locations, often below what Ellis records | No | In copyright; sold commercially; not found as public-domain or official open releases. | High for individual British divisions, but each book needs a purchase or library loan. |
| Marcel Vigneras, *Rearming the French* (US CMH Green Book) | US official (about the French Army) | French rearmament and organisation, not a campaign narrative | No | Public-domain US government work, free from CMH / HyperWar. | Low for nationality balance (it is still a US source). Useful later as a second family for organisation dates. |
| *North-West Europe, 1944–5: Achievement of 21st Army Group* (HMSO short official history, 1953) | British official (short series) | Summary of 21st Army Group | No | Past the UK Crown-copyright term; listed on the same General Staff page as Joslen. | Low–medium. Much thinner than Ellis, which is already read. |
| Association site [brigade-piron.be](https://brigade-piron.be/accueil_fr.html) and the Belgium WWII portal | Belgian secondary / veterans | Brigade Piron | No | Free web pages, not an official history. | Low–medium stopgap for the 14 Belgian claims; a Belgian official history would be better if one can be obtained. |

## Recommended order (first five steps)

Favour the biggest gaps and free access. Entering leftover facts from sources already read comes before opening a new book.

1. **Ellis leftover-entry pass** (vols I and II, `R670` and `R671`) — **done, 10 November 2026**, on branch `ellis-leftovers` (PR #84), in six chunks (`C8975`–`C9017`). Own-nation support for UK units rose from 18.2% to 23.1%; claims that cite Ellis rose from 229 to 324. Polish own-nation support is still 0% (no Polish-authored reference was added; leftover Polish notes were re-checked and only facts the Ellis text confirms were entered). See the re-measure section below. Remaining British map-only rows, especially December 1944 and May 1945, need a later source (Joslen for order of battle, or a divisional history).

2. **Canadian CMHQ and AHQ reports** for North-West Europe (the operational set listed above) — **done, 11 November 2026**, on branch `cmhq-ahq-reports` (PR #85): twelve reports, `R882`-`R893`; Canadian own-nation support 62.3% → 76.4%. See the re-measure section above. Free official PDFs, not yet cited. Best second family for the 184 Canadian claims that remain US-or-Wikipedia-only, and for headquarters places Stacey does not give (roadmap leftover from Canadian Batch 2). Also useful for German units facing First Canadian Army.

3. **de Lattre leftover-entry pass** (`R686`). Notes already exist. Aim at the French First Army, I and II Corps, and March 1945 (currently no French source that month). Access stays the existing Internet Archive lending copy (borrow-only, in copyright). No purchase if that copy still opens.

4. **de Jong, deel 10a and 10b**, from the NIOD library (10a part 1, chapters 1-7, done on `dejong-10a1`, 12 November 2026; 10a part 2 and 10b remain). Free, official, openly licensed. First own-nation source for the Princess Irene Brigade, and Dutch-theatre context for Canadian and British units in the Netherlands.

5. **Joslen, *Orders of Battle***. Free official British OOB, already on the roadmap. Use it for formation dates, independent brigades and relation dates, not as a place source. The 79th Armoured Division now has Ellis-supported place rows; Joslen is still wanted for composition and attachments. May need Scott to save the PDFs if the General Staff host remains blocked from this box.

## What would need Scott

- **Purchase or library loan:** the IPN *Pancerz i odwaga* volume (or the Sikorski Institute official history, or Maczek's memoir) if a Polish-authored source for the 1st Armoured Division is wanted; *Les grandes unités françaises* for a French official series; British commercial divisional histories if a deeper pass on one British division is wanted after the Ellis leftovers.
- **Access help:** a local copy of Joslen if the General Staff host stays blocked; a research request or visit for NIMH collection 466.
- **Already in force:** Fold3 remains Scott-signed-in, no printing, no DevTools, no bulk export. Further FMS reading is German source work, not the first move in this balance pass.
- **Not recommended for this pass:** paying for a new British official history (Ellis is already in hand); treating Vigneras as a French source; scraping or APIs.

Private reading notes, if any, stay in the private source notes folder and in Drive `WWII Unit Locations/source notes/`. They are never committed.
