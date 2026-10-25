# Roadmap and known gaps

Status: Western Front, 6 June to 30 September 1944. Batch 1 of the US Army fill-in (1 July to 30 September 1944: army group, army, corps and division level) is in, on top of the original 6-30 June proof of concept: 514 claims after the Batch 1 review and the command-transitions pass (called Batch 2 below), 353 units of which 101 are active; see `docs/coverage.md`.

## US Army fill-in: progress and plan

Scope (owner-approved): US Army ground units on the Western Front, 6 June 1944 to 8 May 1945, at army group, army, corps and division level; no Marines. Work goes by period with a spot-check gate between batches (`review samples/spot_check_batch1.md` for Batch 1).

| batch | period | status |
|---|---|---|
| 1 | 1 July - 30 September 1944 | **Done, awaiting spot check.** 268 new claims (209 division, 43 corps, 14 army, 2 army group); 25 placeholders became active (12th and 6th Army Groups; Third, Seventh and Ninth Armies; VI, XII, XV, XX and XVIII Airborne Corps; 3rd, 5th, 8th, 26th, 28th, 35th, 36th, 44th, 45th, 80th and 94th Infantry and 4th to 7th Armored Divisions), and a stub `ALL-AFHQ-000H` was added as Seventh Army's parent until 15 September. |
| 2 | 25 July - 15 September 1944 command transitions (V, VII, VIII, XII, XV, XIX, XX Corps; First, Third, Ninth Army; 12th Army Group) | **Done, awaiting spot check** (`review samples/spot_check_batch2.md`): 32 new claims, relationship regeneration of 213 table-derived rows, 2 explained warnings added; see "Batch 2" in `review_changes.md` |
| 3 | 1 October - 31 December 1944 | not started (Aachen, Hurtgen, Lorraine/Metz, Alsace, the Bulge) |
| 4 | 1 January - 31 March 1945 | not started |
| 5 | 1 April - 8 May 1945 | not started |

**Not covered in Batch 1 (known gaps):**
- Regiments, combat commands, separate battalions, cavalry groups and corps troops. Batch 1 is division level and up.
- Corps rows are milestones from the Green Books and Wikipedia, so they are sparse. Batch 2 (command transitions, 25 July to 15 September 1944) added rows for V, VII, VIII, XII, XV, XIX and XX Corps and for First Army on 1 August; outside that window the corps gaps remain, and the Seventh Army place on 15 September is still unlocated.
- Army and army group headquarters places are mostly not sourced; those rows use a representative point at 50 km and confidence 0.3 (see the Batch 1 rules in `docs/methodology.md`).
- CP-derived division rows use CMH command-post towns; towns that could not be geocoded safely were dropped, so some dates have no row (see `review_changes.md`).
- The 39 US units still placeholders (III, XIII, XVI, XXI, XXII and XXIII Corps; Fifteenth Army; 17th Airborne; 8th to 14th, 16th and 20th Armored; 42nd and 63rd to 106th Infantry as listed in `docs/coverage.md`) arrive after September 1944 or were not in Batch 1's divisions; the 26th and 44th Divisions have only their arrival rows here.
- The 82nd and 101st Airborne rows cover England and Market Garden's first days only; the later fighting in Holland is Batch 2.
- German opponents are named only where a Green Book page states them; most US rows have an empty `engaged_with`.

## Known gaps in the current data

**Coverage left out (no verified dates or too thin sources):**
- British XII Corps (arrival date not found), II Canadian Corps and First Canadian Army (July); 12th Army Group HQ place (operational 1 August; Batch 1 gives a representative point only).
- Free French, 1st Special Service Brigade and the 2nd Canadian Armoured Brigade after D-Day.
- German Fifteenth Army, Luftwaffe units, the 319th Division (Channel Islands), 85th, 89th and 116th Panzer (arrive July).
- (US 5th, 8th, 28th and 35th Divisions and 4th Armored were covered in Batch 1.)
- Battle groups: Hellmich (formed about 9-10 June), Hoffmann, Keil and Mueller (Cotentin, undated in the source), and the US 4th Division task forces are sourced but not yet added because the date or place was too vague.
- Roughly 40-60 German units that fought in the sector (regiments, Kampfgruppen, Ost battalions) are only partially represented.

**Data quality:**
- Rows are event-based; quiet days are absent, so positions between rows are unknown.
- Many corps, army and panzer-corps headquarters positions are not tied to a dated source (inferred or approximate). HQ moves are poorly covered by free web sources.
- Composition lists are the standard organisation checked against Wikipedia unit pages, not the exact attachments each day. Not verified: US 2nd and 3rd Armored combat commands, 21st Panzer "Panzer Regiment 22", 79th Armoured and independent brigades (marked `unknown`).
- `parent_unit_id` and `command_relationships` are time-dependent and some links are only supported in outline (for example I SS Panzer Corps under Seventh Army or Panzer Group West; II SS Panzer Corps on 28-29 June). Where no link was found both are `unknown` (16 rows). Plain parents are recorded as `organic` because the sources do not say whether a corps or army link was a standing one; attachments are marked only where a source says so.
- `precision_km` and `confidence` are rule-derived (see methodology); they are consistent but not independent measurements.
- `strength_json` is sparse (20 rows) and rests on secondary sources; no row uses `authorized_organization` yet.
- LXXXIV Corps rows C0106, C0116, C0123 and C0128 (14-17 June) still use an unverified Cotentin placeholder point (49.52,-1.47, 25 km); no source read places the corps headquarters on those dates (CMH only says Rommel visited "LXXXIV Corps headquarters" on 16 June). The same placeholder on C0067 was replaced in the G004 fix (the conflict there was about the handover date, not the place; see `review_changes.md`).
- Date conflicts between sources are open (Dollmann's death, Schlieben's capture, Choltitz replacing Fahrmbacher, Montgomery's HQ moves, 82nd Airborne at Pont-l'Abbe): see the 11 conflict groups.
- Wikipedia is a first-pass source; many rows should be re-verified against primary or semi-primary sources.

## Placeholder units: what is not in the table yet

The placeholder pass (see "Placeholder units" in `docs/methodology.md`) is a first, source-listed set; it is not a complete order of battle.

**Left out on purpose (to do next):**
- Air and naval units (the vocabularies reserve `air_force`, `air_formation`, `fleet`, `naval_unit` and the branches `Air Force`, `Navy` and `Marines`), then the other theaters and Italy.
- Regiments, battalions, separate US tank, tank destroyer, artillery and engineer groups, British Army Groups Royal Artillery and Armoured Brigades beyond those listed, Special Air Service brigade, First Allied Airborne Army and the Atlantic-pocket commands (Detachment of the Army of the Atlantic), the French Detachment of the Army of the Alps, the 13th Airborne and 98th Infantry Divisions (not found in the listing sources), Polish I Corps (role in the West to be checked).
- German: naval ground units, Volkswerfer, assault gun and Heeres artillery brigades, Sicherungs and fortress units, the Schnelle Brigaden 20 and 30, Panzer-Brigaden 109 and 110, 20th and 21st Fallschirmjaeger Divisions and the 12th Army and Armeegruppe Student (service in the West uncertain or only a name for another record), III Flak Corps, and Divisions in Denmark and Norway.

**Ambiguities recorded in `unit_note` or `component_of_note`:**
- German reorganisations: Reserve Corps renamed Armeekorps on 5 August 1944 (LXII, LXIV, LXVI); Korpsgruppe/Generalkommando Kniess becoming LXXXV Corps; Panzer Group West becoming Fifth Panzer Army (separate records); Infantry divisions destroyed and re-formed as Volksgrenadier divisions (separate records); the 19th Luftwaffe Field Division / Luftwaffen-Sturm-Division and the later 19th Volksgrenadier Division; Fuehrer-Begleit and Fuehrer-Grenadier brigades becoming divisions in January 1945; the Lexikon lists a "4. Armee" in Army Group B in November 1944, which looks like an error and is not used.
- French 1st Division naming (1st Free French Division / 1re Division de Marche d'Infanterie), the 11th Army (Western Front only in April 1945), the 24th Army (a skeleton at the Swiss frontier) and Armee-Abteilung von Luettwitz.
- 1st Airborne Task Force and 1st Special Service Force (provisional, mixed-nationality formations) are not in the table.
- The 6 June 1944 German list shows the 326th Division under two corps, and the 271st, 272nd and 277th after Korpsgruppe Kniess without a corps heading; they have no 6 June parent, and the parent shown is the first matching Lexikon timeline entry (see `component_of_note`).

**Next steps for the unit table:** reconcile Allied formation dates against CMH lineage and the British Joslen volumes (many Allied dates are blank because the Wikipedia infobox starts with a First World War lineage); add the Allied parent chain by dated sources; add regiments and Kampfgruppen as claims need them; extend `listing_source` tokens when new sources are used.

## Scale-up plan

1. **Stable unit and place tables.** Keep `data/units.csv` as the unit authority (add formation and disbandment dates, alternative names, higher parent chain) and add a place table with coordinates, historical names and source, referenced by claims.
2. **Better sources for order of battle**: US Army Green Books (CMH), Joslen's *Orders of Battle* (British), the Canadian official history, German OOB references (Tessin, *Lexikon der Wehrmacht*, axishistory), and Soviet *Boevoi sostav* lists. Use Wikipedia as a first pass only.
3. **Per-row evidence**: add a quote or page reference (not only a URL) and a separate `coordinate_source` column, plus a coordinate precision type (point / town / sector), so a coordinate can be re-checked.
4. **Batch geocoding with a cache** (GeoNames or Wikidata with Nominatim as a fallback) and a gazetteer with historical names (places change names, for example Octeville / Cherbourg-Octeville).
5. **New theaters and campaigns**: new theaters get their own `theater` value and folders stay by nationality, so contributors can work independently. Crawl each campaign page and its OOB page, then run a verification pass that checks date, place, unit and echelon against two sources before a row is accepted.
6. **Weaker source bases**: the Eastern Front and the Pacific need Russian and Japanese-language sources and atlases (Glantz-type), so expect lower confidence and more conflict groups.
7. **Tooling**: a dataset browser (map and timeline) generated from `build/claims.geojson`, CSV and GeoJSON releases with a changelog, a Frictionless data package descriptor, and unit tests for the scripts.
8. **Community**: issue and PR templates, a review rota for source checking, and tagged releases with a changelog.

## Proposed changes after the first spot check (not implemented: they change the schema or the process)

The review guardrails in `docs/methodology.md` (rules, `scope`, `effective_from`, validator warnings, `scripts/check_coordinates.py`, the per-row checklist) are in place and are additive. These larger changes were considered and left as proposals; each has a recommendation.

| proposal | why | change | recommendation |
|---|---|---|---|
| Make `strength_json.scope` mandatory when `personnel` is present | whole-unit versus sub-force figures were confused (C0057); 12 existing rows lacked a scope | turn the validator warning into an error after backfilling those rows | **Done.** All rows now have a scope; `scripts/validate.py` reports an error for `personnel` without `scope` (schema README, methodology and CONTRIBUTING updated). Last two rows resolved: C0027 (4th Infantry Division) is now 20,000 with scope `sector`, because CMH counts everything landed at Utah Beach, not the division; for C0018 (6th Airborne Division) sources give 7,000, 8,500 and about 12,000 without saying what each covers, so the figure was removed (see `review_changes.md`) |
| A `command_relations` table (unit, related unit, relationship, start, end, source) instead of the JSON cell | attachments are time-dependent and JSON in CSV is hard to query or review; `effective_from` is only a stop-gap | new table, claims keep a derived `parent_unit_id`; breaking | **Yes**, when the dataset grows beyond one campaign; not before |
| Optional `verification_status`, `reviewed_by`, `reviewed_on` columns on claims | to know which rows were independently checked and to sample the rest by risk | additive nullable columns | **Yes**, soon: cheap and it turns spot checks into coverage |
| Per-row `evidence` (quote or page reference) and `coordinate_source` columns | a reviewer re-checks a row faster, and a coordinate can be traced (already in the scale-up plan) | additive nullable columns | **Yes**, high value |
| Place table with a geometry type (point, line, area) and a representative point | a front line or sector (the Elle line) is not a point; midpoint plus radius is a workaround | new `places` table referenced by claims; breaking | **Yes at scale**; the midpoint rule is enough for now |
| Action-level rows (a separate `actions` table or structured `action_type` and `counterparty` fields) instead of free-text `current_activity` and `engaged_with` | free text let two actions blur into one (C0184) | new fields or table; breaking | **No for now**: one-row-one-action plus the warnings catches most cases; revisit if aggregation recurs |
| Make the coordinate bounding-box check an error and run the offline coordinate script in CI | catches typos and sign errors automatically | CI change, no data change | **Yes** for the bounding box (error); keep the other coordinate checks as warnings |
| Second-source rule for risky rows (attached relationships, strength figures, conflict groups) | these rows carried most of the review findings | process rule, no schema change | **Yes**: already described in the spot-check section; make it a release gate |
| Review the migrated `organic` corps links of divisions and brigades that were attached (found on the 82nd Airborne, C0131) | the migration copied the old `parent_formation` as `organic`, but the sources describe these as operational attachments | **Done** for the 82nd and 101st Airborne (VII Corps, VIII Corps), the 4th Armoured Brigade, the 31st Tank Brigade and the 79th Division (attached to VII Corps from 29 May, under VIII Corps from 28 June; standing parent Third Army, added as a `parent_only` unit): now `attached` or `operational_control`, with `effective_from` where a source gives a date (see `review_changes.md`). Checked and left `organic` because the sources describe an assignment or a passing of control, not an attachment: the 90th Division (VII Corps from 27 March, VIII Corps from 19 June), the 29th Division (XIX Corps from 14 June; `effective_from` added), the 9th Division and the 1st and 2nd Infantry Divisions | **Remaining, next pass**: the 30th Division (CMH says XIX Corps became operational on 13 June "with the 30th Division attached", Wikipedia lists it as assigned to XIX Corps from 18 February; sources conflict, left `organic`); the 83rd Division (C0134, 18 June, parent `unknown`; sources give attached to VIII Corps only from 25 June); the 2nd and 3rd Armored Divisions and the 4th Infantry Division (not checked against an assignment source); the 6th Airborne Division (standing parent I Airborne Corps, operational parent I Corps); the 8th Armoured Brigade (sources say only "supported"). Change only where a source states the attachment |

## Batch 1 review proposals (25 October 2026)

A second reviewer checked the 15-row Batch 1 spot check. Their schema and process proposals, with what was done (details in `review_changes.md`, "Systemic changes"):

| proposal | outcome |
|---|---|
| Relationship vocabulary: add `assigned`, `administrative_control`, `supporting`, `coordinating`, `unspecified_subordination`; narrow `organic`; optional `effective_to` and `date_basis` | **Done** (additive). Validator warns when `organic` is used for a division, corps or army under a higher headquarters. All 482 claims were passed through the rule: table-derived links became `unspecified_subordination`, other standing links `assigned`. |
| Systematic pass of army-to-army-group, corps-to-army, division-to-corps and division-to-army links | **Done by rule**, not row by row: sources were only re-read for the 15 spot-checked rows and the rows named in the review. Links that a narrative source states as a standing assignment are `assigned`; the CMH tables are `unspecified_subordination`. Whether individual older division-to-corps links are really attachments remains the to-do already listed above. |
| `location_date`, `location_basis`, `location_temporal_offset_days` columns | **Done** (optional, additive; schema, README, build, validator, all claim files and the GeoJSON). A separate `location_confidence` column was **not** added: `confidence`, `precision_km` and the basis already carry it, and a fifth location field would be bloat. |
| Backfill of CP-derived rows | **Done** for the Batch 1 rows (49 rows have a coordinate from a different date; 128 are same-day CP lists). **Not done** for older rows: their notes do not say where the coordinate came from, so they stay blank. |
| Validator checks (date mismatch, landing with unrelated point, centroid HQ at corps+, front-line point at corps/army, organic misuse, HQ without id, different event definitions in a conflict group) | **Done**, as warnings except the two errors (offset mismatch, landing from a town centroid or CP of another date). The reviewer's check "confidence shared by rows with different evidence" was **not** implemented: it has no clear, testable definition. |
| `event_definition` | **Done as a notes convention** (`Event definition:`), no new column. |
| Notes convention for separate sources | **Done** (`Event date:`, `Relationship:`, `Location:`, `Coordinates:`); applied to the 15 reviewed rows only. |
| Scripted audit of the 268 new rows | **Done**: `scripts/audit_command_location.py`. Its geocoding check found a wrong place (Mesnil-St-Martin) that three rows used. |
| Batch 2 (V, VII, XII, XV, XX Corps command transitions, 25 July to 15 September 1944; Brittany army transitions) | **Done** (authorised 25 October 2026); see the Batch 2 section below and `review_changes.md`. |

## Generated files at scale

The combined outputs in `build/` (`all_claims.csv`, `claims.geojson`) are committed today because the proof of concept is small. The per-unit files in `data/claims/` are the master copy; there are deliberately no monthly or per-theater exports. Once the dataset grows (for example the whole war), stop committing the generated combined files and publish them as release assets instead (build them in CI on each tagged release), so the repository history stays small and diffs stay readable. At that point remove `build/` from version control, add it to `.gitignore`, and drop the "build is up to date" check from the workflow.

## Open design questions

- Per-day interpolation versus pure event rows (currently pure events).
- Whether a unit's primary `theater` should be derived from its claims once several theaters exist (currently set by hand in `units.csv`).
- Whether `command_relationships` should become a separate time-dependent relations table (one row per unit, formation and date range) instead of a JSON cell, for example once whole-war data makes the cell awkward to query.

## Batch 2: command transitions, 25 July - 15 September 1944 (25 October 2026)

Done: First/Third/Ninth Army and 12th Army Group handovers (1 August; 1 September; Ninth Army 5 and 10 September), V, VII, VIII, XII, XV, XIX and XX Corps command posts and transitions, the 2nd Armored/XIX Corps sequence, Cobra division rows (1st, 2nd Armored, 3rd Armored), the 6th Armored and 83rd Divisions under Ninth Army, and a regeneration of every table-derived relationship from the CMH tables (army and army-group columns now `assigned`/`attached`/`operational_control`; corps stays `unspecified_subordination` except where a Green Book page says attached).

Still open after Batch 2:
- Seventh Army headquarters place on 15 September 1944 (not found; row C0296 stays an unlocated representative point at confidence 0.3).
- VIII Corps headquarters on 5 and 10 September: only the 18 August move to Lesneven is documented; those two rows keep Brest-sector points.
- First Army 1 August headquarters: Vouilly (monument) or Saint-Gilles (CMH list as compiled by World War II by Day) differ by about 23 km (group G015).
- The 83rd Division's brief simultaneous attachment to VIII and XV Corps (Breakout p428) is not given a row: the table shows XV Corps on 1 August and VIII Corps on 3 August and no source dates the overlap.
- Regiment-level Cobra rows (the 4th Division's 8th Infantry at La Chapelle-en-Juger, the 9th and 30th Divisions on 25 July) were not added: the pages read here do not give a place and date together.
- The corps and army lists from World War II by Day are a secondary compilation; replace them with the CMH ETO-OB corps and army pages if those become reachable.
- 2nd French Armoured Division attachment to XV Corps (Breakout p496) is not recorded (French unit not yet active).
