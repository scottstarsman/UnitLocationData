# Roadmap and known gaps

Status: Western Front, 6 June to 31 December 1944 for US Army army-group, army, corps and selected division milestones (Batch 3 added 1 October to 31 December); divisions are complete only for the milestones listed in the Batch 3 section. Batch 1 of the US Army fill-in (1 July to 30 September 1944: army group, army, corps and division level) is in, on top of the original 6-30 June proof of concept: 566 claims after Batch 3 and its review, 354 units; see `docs/coverage.md`.

## US Army fill-in: progress and plan

Scope (owner-approved): US Army ground units on the Western Front, 6 June 1944 to 8 May 1945, at army group, army, corps and division level; no Marines. Work goes by period with a spot-check gate between batches ([`review/spot_check_batch1.md`](review/spot_check_batch1.md) for Batch 1).

| batch | period | status |
|---|---|---|
| 1 | 1 July - 30 September 1944 | **Done, awaiting spot check.** 268 new claims (209 division, 43 corps, 14 army, 2 army group); 25 placeholders became active (12th and 6th Army Groups; Third, Seventh and Ninth Armies; VI, XII, XV, XX and XVIII Airborne Corps; 3rd, 5th, 8th, 26th, 28th, 35th, 36th, 44th, 45th, 80th and 94th Infantry and 4th to 7th Armored Divisions), and a stub `ALL-AFHQ-000H` was added as Seventh Army's parent until 15 September. |
| 2 | 25 July - 15 September 1944 command transitions (V, VII, VIII, XII, XV, XIX, XX Corps; First, Third, Ninth Army; 12th Army Group) | **Done, review corrections applied** ([`review/spot_check_batch2.md`](review/spot_check_batch2.md)): 33 new claims (C0483-C0515), relationship regeneration of 216 table-derived rows, 2 explained warnings added; see "Batch 2" and "Batch 2 review corrections" in [`review/review_changes.md`](review/review_changes.md) |
| 3 | 1 October - 31 December 1944 | **Done as a milestone pass; review corrections applied** ([`review/spot_check_batch3.md`](review/spot_check_batch3.md); see [`review/review_changes.md`](review/review_changes.md), "Batch 3 review corrections and temporal audit"): 51 claims (C0516-C0566; C0564-C0566 added by the review) for 6th and 12th Army Groups, First, Third, Seventh and Ninth Armies, ten corps and thirteen divisions (20 division rows); 13 units became active (III, XIII and XXI Corps; 10th Armored; 75th, 84th, 87th, 100th, 102nd, 103rd, 104th and 106th Infantry; Combat Command Reserve, 4th Armored); `build/command_relations.csv` now runs to 31 December 1944. Not covered: see "Batch 3" below. |
| 4 | 1 January - 31 March 1945 | not started |
| 5 | 1 April - 8 May 1945 | not started |

**Not covered in Batch 1 (known gaps):**
- Regiments, combat commands, separate battalions, cavalry groups and corps troops. Batch 1 is division level and up.
- Corps rows are milestones from the Green Books and Wikipedia, so they are sparse. Batch 2 (command transitions, 25 July to 15 September 1944) added rows for V, VII, VIII, XII, XV, XIX and XX Corps and for First Army on 1 August; outside that window the corps gaps remain, and the Seventh Army place on 15 September is still unlocated.
- Army and army group headquarters places are mostly not sourced; those rows use a representative point at 50 km and confidence 0.3 (see the Batch 1 rules in `docs/methodology.md`).
- CP-derived division rows use CMH command-post towns; towns that could not be geocoded safely were dropped, so some dates have no row (see [`review/review_changes.md`](review/review_changes.md)).
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
- LXXXIV Corps rows C0106, C0116, C0123 and C0128 (14-17 June) still use an unverified Cotentin placeholder point (49.52,-1.47, 25 km); no source read places the corps headquarters on those dates (CMH only says Rommel visited "LXXXIV Corps headquarters" on 16 June). The same placeholder on C0067 was replaced in the G004 fix (the conflict there was about the handover date, not the place; see [`review/review_changes.md`](review/review_changes.md)).
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
| Make `strength_json.scope` mandatory when `personnel` is present | whole-unit versus sub-force figures were confused (C0057); 12 existing rows lacked a scope | turn the validator warning into an error after backfilling those rows | **Done.** All rows now have a scope; `scripts/validate.py` reports an error for `personnel` without `scope` (schema README, methodology and CONTRIBUTING updated). Last two rows resolved: C0027 (4th Infantry Division) is now 20,000 with scope `sector`, because CMH counts everything landed at Utah Beach, not the division; for C0018 (6th Airborne Division) sources give 7,000, 8,500 and about 12,000 without saying what each covers, so the figure was removed (see [`review/review_changes.md`](review/review_changes.md)) |
| A `command_relations` table (unit, related unit, relationship, start, end, source) instead of the JSON cell | attachments are time-dependent and JSON in CSV is hard to query or review; `effective_from` is only a stop-gap | new table, claims keep a derived `parent_unit_id`; breaking | **Yes**, when the dataset grows beyond one campaign; not before |
| Optional `verification_status`, `reviewed_by`, `reviewed_on` columns on claims | to know which rows were independently checked and to sample the rest by risk | additive nullable columns | **Yes**, soon: cheap and it turns spot checks into coverage |
| Per-row `evidence` (quote or page reference) and `coordinate_source` columns | a reviewer re-checks a row faster, and a coordinate can be traced (already in the scale-up plan) | additive nullable columns | **Yes**, high value |
| Place table with a geometry type (point, line, area) and a representative point | a front line or sector (the Elle line) is not a point; midpoint plus radius is a workaround | new `places` table referenced by claims; breaking | **Yes at scale**; the midpoint rule is enough for now |
| Action-level rows (a separate `actions` table or structured `action_type` and `counterparty` fields) instead of free-text `current_activity` and `engaged_with` | free text let two actions blur into one (C0184) | new fields or table; breaking | **No for now**: one-row-one-action plus the warnings catches most cases; revisit if aggregation recurs |
| Make the coordinate bounding-box check an error and run the offline coordinate script in CI | catches typos and sign errors automatically | CI change, no data change | **Yes** for the bounding box (error); keep the other coordinate checks as warnings |
| Second-source rule for risky rows (attached relationships, strength figures, conflict groups) | these rows carried most of the review findings | process rule, no schema change | **Yes**: already described in the spot-check section; make it a release gate |
| Review the migrated `organic` corps links of divisions and brigades that were attached (found on the 82nd Airborne, C0131) | the migration copied the old `parent_formation` as `organic`, but the sources describe these as operational attachments | **Done** for the 82nd and 101st Airborne (VII Corps, VIII Corps), the 4th Armoured Brigade, the 31st Tank Brigade and the 79th Division (attached to VII Corps from 29 May, under VIII Corps from 28 June; standing parent Third Army, added as a `parent_only` unit): now `attached` or `operational_control`, with `effective_from` where a source gives a date (see [`review/review_changes.md`](review/review_changes.md)). Checked and left `organic` because the sources describe an assignment or a passing of control, not an attachment: the 90th Division (VII Corps from 27 March, VIII Corps from 19 June), the 29th Division (XIX Corps from 14 June; `effective_from` added), the 9th Division and the 1st and 2nd Infantry Divisions | **Remaining, next pass**: the 30th Division (CMH says XIX Corps became operational on 13 June "with the 30th Division attached", Wikipedia lists it as assigned to XIX Corps from 18 February; sources conflict, left `organic`); the 83rd Division (C0134, 18 June, parent `unknown`; sources give attached to VIII Corps only from 25 June); the 2nd and 3rd Armored Divisions and the 4th Infantry Division (not checked against an assignment source); the 6th Airborne Division (standing parent I Airborne Corps, operational parent I Corps); the 8th Armoured Brigade (sources say only "supported"). Change only where a source states the attachment |

## Batch 1 review proposals (25 October 2026)

A second reviewer checked the 15-row Batch 1 spot check. Their schema and process proposals, with what was done (details in [`review/review_changes.md`](review/review_changes.md), "Systemic changes"):

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
| Batch 2 (V, VII, XII, XV, XX Corps command transitions, 25 July to 15 September 1944; Brittany army transitions) | **Done** (authorised 25 October 2026); see the Batch 2 section below and [`review/review_changes.md`](review/review_changes.md). |

## Batch 2 review proposals (25 October 2026)

A third reviewer checked the 15-row Batch 2 spot check. Their findings were verified against the Green Books, the Third Army After Action Report and other sources before anything was applied ([`review/review_changes.md`](review/review_changes.md), "Batch 2 review corrections"). The design proposals and what was done:

| proposal | outcome |
|---|---|
| (a) Explicit validity intervals; a missing `effective_to` must not mean indefinitely valid; optional `ordered_date` | **Done** (additive, inside the relationship JSON): keys `ordered_date`, `effective_from_latest`, `effective_to_earliest`, `effective_to_basis`, validated; the validator prints a count of `attached`/`operational_control` entries with no end that the unit's next claim no longer lists, and the audit lists them (33 claims); explicit ends added where a source dates them (XV Corps, 2nd Armored, 6th Armored, VIII Corps' First Army attachment). The 33 open entries stay as snapshots: the derived table closes them at the next claim. Applied to C0425, C0426 and C0296 (order versus effect). |
| (b) Derived `command_relations` table | **Done, first version**: `build/command_relations.csv` (about 310 intervals, US units with a claim from 24 July to 31 December 1944; alternate and disputed rows do not feed it), built by `scripts/build.py`, queried with `scripts/who_controls.py`. Claims stay the evidence. **Not done**: other nations and periods, time of day, a numeric relationship confidence (the `support` column says documented, table or inferred instead). |
| (c) Separate event confidence and location confidence / `location_status` | **Declined again**, with the reasoning in `schema/README.md`: `confidence` already scores the location and its sources; a status column would repeat `location_basis`; a second numeric column would need a judged value for each of the 515 rows. Instead command rows from Batch 2 on carry `Event support:` and `Location support:` sentences (qualitative), the validator warns when a low-confidence command row lacks `Event support:`, and the derived table carries relationship support. Revisit if the derived table needs an event score as input. |
| (d) `composing_units` with effective dates, or derived from relationships | **Roadmap**: C0493 and C0487 now list dated, qualified entries as text; a derived composing view needs formation-to-corps rows for every component (the combat commands and cavalry groups are not all units yet). Derive it from `command_relations.csv` once component coverage is complete. |
| (e) `last_confirmed_hq_location` | **Roadmap**: needs the temporal reconstruction layer. Until then Lesneven is documented as the 18 August headquarters observation and the last confirmed place before the CMH list's St Aubin on 24 September; the VIII Corps 5 and 10 September rows keep Brest-sector points and say so. |
| Explained-exception mechanism for the coordinate checker | **Done**: `data/coordinate_exceptions.csv` (speed warnings only so far; five entries with sources), and the speed check now measures days between the dates the coordinates belong to (`location_date`). Three speed warnings that this made visible remain open and unchecked: C0253, C0419, C0480. |

## Generated files at scale

The combined outputs in `build/` (`all_claims.csv`, `claims.geojson`) are committed today because the proof of concept is small. The per-unit files in `data/claims/` are the master copy; there are deliberately no monthly or per-theater exports. Once the dataset grows (for example the whole war), stop committing the generated combined files and publish them as release assets instead (build them in CI on each tagged release), so the repository history stays small and diffs stay readable. At that point remove `build/` from version control, add it to `.gitignore`, and drop the "build is up to date" check from the workflow.

## Operations table (26 October 2026)

Done: `data/operations.csv` (36 rows: the Overlord umbrella, 9 campaigns of which 6 are CMH streamers, 12 operations, 12 battles and 2 phases), `operation_relations.csv`, `operation_exceptions.csv`, `operation_id` on every claim, derived `campaign` / `operation_name` / `sub_operation_name` / `operation_path` in `build/all_claims.csv`, validator rules. Open points: the operation boundaries listed in [`review/operations_backfill.md`](review/operations_backfill.md) (Cobra placement, Overlord end date, Cherbourg window, Brittany and Brest end dates, derived Pursuit dates, Bulge end date, Aachen and Siegfried Line start dates); 20 claims left on a campaign because no operation row fits (Le Mans, Loire, Seine, Alsace, early Pursuit and Roer rows); rows for the Hedgerows, Hurtgen Forest, Colmar Pocket, Nordwind and the Central Europe operations once claims need them; a `claim_operations` link table only if a claim is found that belongs to two operations at once (none yet).

## Claim-to-reference links stored on claims (26 October 2026)

Done: `reference_ids` and `source_locator` on every claim (566 claims; 158 with a locator taken from URL page fragments), `data/claim_reference_roles.csv` (619 rows: 564 location, 21 strength, 20 command_relationship, 12 date, 2 event; every other link is `general`), `source_family` on every reference, validator checks (ids exist, one reference per claim, URL citations resolve to the stored ids, role rows match the links, two source families at confidence 0.9 as a warning) and `scripts/migrate_claim_references.py`. Next: add roles by hand while checking sources (only 70 notes name what a source supports, so most links are `general`); add page numbers for the 408 claims without a locator when a source is next read; consider promoting the 0.9 family rule to an error after the next batch, and a rule that confidence 0.7 needs a second family (115 + 240 claims at 0.7 and 0.5 currently rest on one non-geocoder family).

## Open design questions

- Per-day interpolation versus pure event rows (currently pure events).
- Whether a unit's primary `theater` should be derived from its claims once several theaters exist (currently set by hand in `units.csv`).
- Whether `command_relationships` should become the master time-dependent relations table instead of a JSON cell (a derived version exists since the Batch 2 corrections: `build/command_relations.csv`); the open point is whether to hand-edit intervals once the derived table is used for queries.

## Batch 2: command transitions, 25 July - 15 September 1944 (25 October 2026)

Done: First/Third/Ninth Army and 12th Army Group handovers (1 August; 1 September; Ninth Army 5 and 10 September), V, VII, VIII, XII, XV, XIX and XX Corps command posts and transitions, the 2nd Armored/XIX Corps sequence, Cobra division rows (1st, 2nd Armored, 3rd Armored), the 6th Armored and 83rd Divisions under Ninth Army, and a regeneration of every table-derived relationship from the CMH tables (army and army-group columns now `assigned`/`attached`/`operational_control`; corps stays `unspecified_subordination` except where a Green Book page says attached).

Still open after Batch 2:
- Seventh Army headquarters place on 15 September 1944 (not found; row C0296 stays an unlocated representative point at confidence 0.3).
- VIII Corps headquarters on 5 and 10 September: only the 18 August move to Lesneven is documented; those two rows keep Brest-sector points.
- First Army 1-2 August headquarters: Vouilly (monument: stayed until 2 August) and Saint-Gilles (CMH list from 1 August) are 23 km apart and are now modelled as a move in sequence (C0484, C0485; conflict group G015 dissolved in the Batch 2 corrections); the order of events within 1-2 August is not documented.
- The 83rd Division's brief simultaneous attachment to VIII and XV Corps (Breakout p428) is not given a row: the table shows XV Corps on 1 August and VIII Corps on 3 August and no source dates the overlap.
- Regiment-level Cobra rows (the 4th Division's 8th Infantry at La Chapelle-en-Juger, the 9th and 30th Divisions on 25 July) were not added: the pages read here do not give a place and date together.
- The corps and army lists from World War II by Day are a secondary compilation; replace them with the CMH ETO-OB corps and army pages if those become reachable.
- 2nd French Armoured Division attachment to XV Corps (Breakout p496) is not recorded (French unit not yet active).

## Batch 3: Oct-Dec 1944 milestones (25 October 2026)

Done: 20 December command change (12th Army Group keeps Third Army; First and Ninth Armies to 21st Army Group with explicit ends from the CMH tables); First, Third, Seventh and Ninth Army milestones; the Aachen link-up (16 October) and surrender (21 October); the Roer offensive start (16 November) for VII and XIX Corps; XIII Corps (8 and 24 November) as a newly operational corps, III Corps (4 December table date, 18 December decision) and XXI Corps (27 December table date) first listed over divisions; Lorraine (XII and XX Corps 8-9 November, 10th Armored), Seventh Army (XV Corps 13 November, 100th and 103rd Divisions' first combat); the Bulge (28th and 106th Divisions, VIII Corps headquarters move and handover to Third Army, 82nd Airborne, XVIII Airborne Corps, 101st Airborne at Bastogne (a sequence since the Batch 3 review; G016 dissolved), 4th Armored and its Combat Command Reserve at Assenois, III Corps counterattack, XII Corps ordered to Luxembourg, 84th and 75th Divisions).

Not covered (no rows were added; the sources for them were not read in this batch): V and VI Corps command-post places and XX Corps places other than 9 November; the 1st, 2nd, 3rd, 9th and 30th Infantry Divisions after the dates already in the dataset; the 7th, 3rd and 9th Armored Divisions in the Bulge; the 9th, 11th, 12th and 14th Armored, 17th Airborne, 42nd, 78th, 95th and 99th Divisions (still placeholders); the Hurtgen Forest in detail (28th Division's Schmidt attack, 2 November, is not a row); the Colmar pocket beyond XXI Corps; Metz fall (22 November); Strasbourg (23 November); the French First Army and II Corps relationships to Seventh Army; the First Army headquarters move to Tongeren (atlas, 24 December). XVI, XXII and XXIII Corps and the Fifteenth Army have no source in the window (XVI Corps appears in the 75th Division table in December but has no Green Book or atlas entry before January). 13th Airborne, 13th, 16th and 20th Armored arrive in 1945; 8th Armored, 66th, 69th, 70th and 76th Divisions were in the United Kingdom or just landing.

Open points: the 101st / VIII Corps handover hour on 20 December (Green Book "during the 20th" against the CMH table's 17 December); the VIII Corps headquarters stays at Neufchâteau from 18 December while Middleton remains in Bastogne; First Army's own move to Chaudfontaine is dated 19 December (p423) while the atlas has no entry until Tongeren on 24 December; the XVIII Airborne Corps command post place is taken from the 82nd's.

## Ordered / effective / exercised states (proposed 25 October 2026, cheap form implemented)

A command change has up to four dates: intended (a plan or tentative selection), ordered, effective and exercised. Implemented cheaply: `ordered_date`, `effective_from` with optional `effective_time`, inclusive `effective_to` with `effective_to_time`, narrative rows as the exercised evidence, `other` rows for a decision that is not yet an order. Example motivating a state column: the 7th Armored Division's move to St. Vith. The 12th Army Group staff chose the division on the afternoon of 16 December (intended), General Hasbrouck was alerted by telephone at 1730 (ordered), the advance party went to VIII Corps at Bastogne for instructions, where Middleton outlined the mission and left the commitment of each combat command to Hasbrouck (effective and exercised on arrival; Ardennes p273-274). Roadmap, not done: a `command_state` value per relationship entry (intended / ordered / effective / exercised) and a derived view that answers "who could give this unit orders at this hour", which needs hour-level data the Green Books rarely give.

## Batch 3 review: corrections, declines and open points (25 October 2026)

Applied from the outside review of Batch 3 (verified against sources first): the 101st rows as a sequence (G016 dissolved); the 84th's XVIII Airborne Corps to VII Corps handover (the Green Book puts it between 22 and 23 December, later than the review assumed); event-type reclassifications (C0539, C0562, C0516); inferred and last-known location labels (C0560, C0552, C0522); the CCR component row (C0566) and a representative point for the 4th Armored Division; new rows for the 18 December III Corps decision (C0564) and the 23 December VII Corps front (C0565); the `campaign` column and operation_name dating; `who_controls.py` with an hour argument. Declined or not confirmed: C0544's date (the Green Book gives 18 November, not 19 November); a numeric event confidence (third time); `retained_nonoperational_responsibilities`, `engagement_area`, `inferred_from_nearby_unit_hq` and `valid_until_exclusive` (existing fields do the job, see `schema/README.md`).
Open: the 101st's rows for October and November 1944 (the first Batch 3 row after 20 September 1944 is 17 December); five German parent changes in June 1944 that no entry dates (Batch 1); the 4th Armored Division's landing against arrival date group G012 (different event types); the hour of VIII Corps' passage to Third Army (not documented); the VII Corps handover of the 84th Division (division-level date not documented).
