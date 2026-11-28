# Independent review packet

You are asked to assess the design and the data quality of this dataset. You need nothing but read access to the repository: this page is the brief, and every file it points to is in the repository. (In the GitHub repository the dataset sits in the `WorldWar2/` folder; every path below is relative to that folder.) You may be a person or another AI system. Please do not assume anything that is not written here or in the files.

**If you only have the documents.** The checks in section 6 and the counts in section 4 need the whole dataset folder, not only this packet: without `data/`, `build/`, `schema/*.json` and `scripts/` you cannot run `validate.py`, `build.py --check` or `review_sample.py --check`, and you cannot confirm a count or a validator result. You can still judge the design, the documents and the questions, and check the sampled rows against their sources (the sample files carry the links and locators). Please say in your findings which of the two situations you were in. The packet can be handed over in two forms:

- **Option A, the whole dataset folder** (`data/`, `build/`, `schema/`, `scripts/`, `docs/` and the files at the top of the folder; about 5.2 MB unpacked, without `archive/`). Every command in this brief works.
- **Option B, documentation plus read-only data**: this packet (`docs/review/`), `schema/` including the JSON files, `docs/`, the tables of `data/` and `build/all_claims.csv`. The counts and the sample can be checked against the tables, but no script can be run.

Your findings are checked against the sources before anything changes; they are treated as unverified feedback, so a finding that carries its evidence (a link and a page) is worth far more than an opinion. See [findings_template.md](findings_template.md) for the format and for what happens to a finding.

| file | what it is |
|---|---|
| [README.md](README.md) | this brief |
| [checklist.md](checklist.md) | what to check, area by area, and how to check a sampled row |
| [sample.md](sample.md), [sample_claims.csv](sample_claims.csv), [sample_relations.csv](sample_relations.csv) | a seeded sample of 40 claims and 20 command relations with the sources they cite, to check against the sources |
| [questions.md](questions.md) | ten design questions on which an outside view is most wanted |
| [findings_template.md](findings_template.md) | the format of a finding, and the response protocol |
| [responses.md](responses.md) | our recorded responses to findings (empty until a review comes back) |
| [verification_results.md](verification_results.md) | our own source verification of the sample: verdicts, findings, rough error rates by field |
| `earlier_reviews.md` (GitHub repository only) | an index of the notes from earlier review passes (history; not needed for this review) |

**Suggested paths.** About one hour: this brief, `schema/README.md`, ten sampled claims and five sampled relations, then the questions. About half a day: the whole checklist, the full sample, and the validator and audits run locally.

## 1. What the dataset is

A claim-based dataset of where World War II units were, when, and how sure we are, covering ground, air and naval formations (including US Marines). A row (a *claim*) says: this unit was at this place on this date, doing this (an `event_type` and a `current_activity`), with coordinates, a precision radius, a `confidence` score from a four-level rubric, and the sources. Claims are event-based (a row for a landing, an arrival, an attack, a headquarters move, a command change, a base or station, or a ship's position), not a daily position track. Flying-unit sorties are recorded as missions, not as location claims. Where sources disagree the competing claims are kept as separate rows in a conflict group instead of being averaged or silently resolved.

**Scope as it stands.** The surveyed focus is the Western Front, 6 June 1944 to 8 May 1945, at army group, army, corps and division level and, where sources trace them, smaller formations, together with air and naval units in that theater. That window includes 1945 (through late May: occupation and post-surrender rows). A first Pacific increment covers the Guadalcanal campaign (August 1942–February 1943) and related South Pacific rows. Claim dates in the files run from 16 September 1939 to 31 May 1945: earlier Western Front rows are mostly pre-invasion positions under `OP-PRE-INVASION`; a smaller number are incidental other-front or home-area rows. Coverage is uneven and event-based, not a daily plot. The unit table still has placeholder units (identity but no claim file): see the counts in section 4.

**Method in one paragraph.** Rows are written by hand from published sources (the US Army Center of Military History "Green Book" volumes and order-of-battle tables, official British, Canadian, Navy and Marine histories, Wikipedia, the Lexikon der Wehrmacht, and others; see `docs/sources.md` and `data/references.csv`), with coordinates from Wikipedia, official lists or OpenStreetMap place coordinates, so a point is usually the place's centre, not the unit's measured position. Confidence follows a rule (see section 3). Everything in `build/` is generated from `data/` by `scripts/build.py`.

## 2. Table map

All tables are CSV files under `data/` (UTF-8, comma separated). Column definitions: `schema/README.md` (human) and `schema/*.json` (machine-readable, enforced by `scripts/validate.py`).

| table | file | one row is | key |
|---|---|---|---|
| claims | `data/claims/<nationality>/<unit_id>.csv`; combined in `build/all_claims.csv` | one sourced claim about one unit on one date | `claim_id` (`C0001`...); also unique: `(unit_id, date, event_type)` |
| units | `data/units.csv` | one unit (active or placeholder): name, nationality, `echelon`, `branch`, operational parent | `unit_id` (nationality prefix, type, number, echelon letter) |
| nationalities | `data/nationalities.csv` | one nationality (code, name, adjective, kind; the sides are in `nation_allegiance.csv`) | `code` |
| nation_allegiance | `data/nation_allegiance.csv` | one period in which a nation was Allied, Axis, neutral or co-belligerent in WW2 | `(nation, valid_from)` |
| unit_allegiance_overrides | `data/unit_allegiance_overrides.csv` | one period in which a unit stood on another side from its nation (wins over the nation table; currently the four combined Allied headquarters whose nationality code `ALL` has no nation-allegiance row) | `(unit_id, valid_from)` |
| places | `data/places.csv` | one named place: canonical name, aliases, kind (point / area / line), coordinates, country, region, coordinate source | `place_id` (`PL0001`...) |
| place_merges | `data/place_merges.csv` | one place id that was retired by a merge into a surviving place | `retired_place_id` |
| operations | `data/operations.csv` (+ `operation_relations.csv`, `operation_exceptions.csv`) | one operation, battle, phase, campaign or umbrella with a parent chain and dates | `operation_id` (`OP-...`) |
| command_relations | `data/command_relations.csv` (derived view with names: `build/command_relations.csv`) | one dated interval of one relationship between a subject unit and a higher unit | `relation_id` (`CR0001`...) |
| command_relation_claims | `data/command_relation_claims.csv` | the evidence link: a claim that lists a relation, and what it stated (start, end, wording) | `(relation_id, claim_id)` |
| command_relation_overlaps | `data/command_relation_overlaps.csv` | a documented contradictory overlap of two relations of one subject | `(relation_id_a, relation_id_b)` |
| references | `data/references.csv` (generated) from `data/references_meta.csv` and the claims | one source: title, citation, type, family, publisher, link, licence, reliability note, counts | `reference_id` (`R001`...) |
| claim_reference_roles | `data/claim_reference_roles.csv` | the role of one claim-to-source link where a source supports one part of a claim (event, date, location, command relationship, strength) | `(claim_id, reference_id, role)` |
| retired_claims | `data/retired_claims.csv` | a claim id that was removed and must never be reused | `claim_id` |
| claim_key_exceptions | `data/claim_key_exceptions.csv` | a pair of claims that legitimately share `(unit_id, date, event_type)` | `(claim_id, other_claim_id)` |
| coordinate_exceptions | `data/coordinate_exceptions.csv` | an explained exception to a coordinate check | `(check, claim_id, other_claim_id)` |
| missions | `data/missions/<nationality>/<unit_id>.csv` | one sourced sortie or mission of a flying unit | `mission_id` (`MSN####`) |
| retired_missions | `data/retired_missions.csv` | a mission id that was removed and must never be reused | `mission_id` |
| people | `data/people.csv` | one person who held a sourced command | `person_id` (`PE####`) |
| unit_commanders | `data/unit_commanders.csv` | one dated tenure of a person in command of a unit | `tenure_id` (`UC####`) |
| unit_commander_claims | `data/unit_commander_claims.csv` | the evidence link: a claim that supports a tenure | `(tenure_id, claim_id)` |
| unit_lineage | `data/unit_lineage.csv` | one succession between two unit records (redesignation, absorption, reconstitution) | `lineage_id` (`UL###`) |
| toe_templates / unit_toe | `data/toe_templates.csv`, `data/unit_toe.csv` | an official table of organization, and a unit's assignment to one | `template_id` (`TT####`) / `(unit_id, template_id, valid_from)` |
| ship_classes / aircraft_types | `data/ship_classes.csv`, `data/aircraft_types.csv` | one ship class or aircraft type | `ship_class_id` (`SC###`) / `aircraft_type_id` (`AT###`) |

The claim-to-source links themselves are the `reference_ids` (and `source_locator`) columns of the claim files. A claim does not store its command relationships: they are in `command_relations` with `command_relation_claims` as evidence and are put back into `build/all_claims.csv` as text for convenience. Commanders are stored in `people.csv` and `unit_commanders.csv`, with `unit_commander_claims` as evidence; the claim's `commander` field is the name the source gave on that row, and derived `commander_on_date` columns appear on the build claims export. Flying-unit sorties are in `data/missions/`, not location claims. Deferred relations (formations below division that are not yet units) are kept in `docs/deferred_relations.md`. The evidence of a claim is its `reference_ids` plus `claim_reference_roles`.

## 3. Rules and vocabularies

The rules that the validator enforces are in `CONTRIBUTING.md` ("Rules", "Claim identity") and `docs/methodology.md`. In short:

- **Every row needs a source**; conflicting claims are separate rows with a shared `conflict_group_id`; nothing is invented (`unknown` or blank instead of a guess).
- **Claim key.** `(unit_id, date, event_type)` is unique; a repeat is allowed only inside a conflict group or through an entry in `claim_key_exceptions`.
- **Claim ids** are unique, never reused and never renumbered once published; gaps are allowed; a removed claim is recorded in `retired_claims`.
- **Confidence** has four levels: 0.9 exact location and two independent source families agree; 0.7 exact location with one authoritative source, or approximate with two families; 0.5 exact with one secondary source, or approximate with one family; 0.3 inferred position or representative point, or approximate date. A preferred claim of a conflict group is capped at 0.7, an alternate or disputed claim at 0.5 (`docs/methodology.md`, "Confidence rubric").
- **Places.** A claim points to a place with `place_id`; `location_qualifier` says what part or vicinity; the claim's own point may differ from the place's point only through `coord_override` (within 5 km); `location_represents` says what the point stands for (headquarters, main body, sector centre, front-line point, objective, route); `precision_km` is one of 1, 3, 5, 10, 25, 50.
- **Command relations.** Ten relationship values (`organic`, `assigned`, `attached`, `unspecified_subordination`, `operational_control`, `administrative_control`, `supporting`, `coordinating`, `reserve`, `unknown`); intervals are inclusive; a start and an end each have a `basis` (order, assignment table, narrative, inferred, claim date, ...); `end_unknown` marks a temporary relationship with no sourced end; a table observation and an operational transfer are different rows (`schema/README.md`, "Command relations").
- **Controlled vocabularies** are in `schema/vocabularies.json` (`event_type`, `echelon`, `branch`, `relationship`, `confidence`, `claim_status`, `location_represents`, `location_basis`, `note_label`, `source_type`, ... see the count below). The labels that may start a sentence of `notes` (`Event date:`, `Location support:`, ...) are a closed set of 19; a new label needs a documentation change and a validator change in one commit.
- **Derived data.** `build/` and `data/references.csv` are generated; `docs/coverage.md` too. `python scripts/build.py --check` fails when they are stale.

## 4. Current counts

Computed from the data by `python scripts/review_sample.py --counts`; the block is rewritten by `python scripts/review_sample.py` and `python scripts/review_sample.py --check` fails when it is out of date.

<!-- counts:begin (generated by scripts/review_sample.py) -->

| what | count |
|---|---|
| claims (rows of `data/claims/`, `build/all_claims.csv`) | 13687, dated 1939-09-01 to 1945-05-31 |
| units in `data/units.csv` | 3125: 3014 active (have claims), 109 placeholders |
| claim files (one per active unit) | 3006 |
| conflict groups / claims in a group | 299 / 636 |
| places (`data/places.csv`) / retired in `data/place_merges.csv` | 5028 / 9 |
| operations / operation relations | 92 / 15 |
| command relations (`data/command_relations.csv`) | 4072 |
| relation-to-claim evidence links (`data/command_relation_claims.csv`) | 7245 |
| documented relation overlaps (`data/command_relation_overlaps.csv`) | 35 |
| deferred relations (`docs/deferred_relations.md`, ids D01 onward) | 10 |
| references (`data/references.csv`, generated) | 2268, of which 1745 cited by at least one claim (the others are cited by units or operations) |
| claim-reference roles (`data/claim_reference_roles.csv`) | 82 |
| nationalities / retired claim ids / claim-key exceptions | 43 / 7 / 15 |
| controlled vocabularies in `schema/vocabularies.json` | 64 |

Claims by nationality: Germany 4935, US 4480, UK 2577, Canada 716, France 356, Japan 242, Poland 218, Netherlands 51, Czechoslovakia 27, Belgium 24, Norway 19, Australia 17, New Zealand 9, Soviet Union 8, Slovakia 5, Greece 2, Allied 1.

Claims by echelon: division 6542, corps 1785, air_squadron 1351, naval_unit 752, army 733, air_group 628, naval_division 340, brigade 319, air_flight 301, regiment/battle_group 246, air_wing 165, battalion 140, army_group 138, naval_squadron 52, company 45, other 44, task_group 36, air_division 31, air_force 14, air_corps 13, task_force 10, fleet 2.

Claims by branch: Army 6878, Air Force 1947, Armoured 1315, Navy 1313, Luftwaffe 949, Armored 525, Waffen-SS 370, Airborne 238, Marines 152.

Claims by event type: other 6372, hq_observation 1837, attack 1175, relocation 921, defense 845, hq_move 458, capture 405, arrival 349, command_change 235, withdrawal 224, subordinate_assignment 209, regroup 193, landing 138, counterattack 87, surrender 81, activation 68, destruction 49, redesignation 31, sortie 9, commissioning 1.

Claims by status: preferred 13343, alternate 328, disputed 16. Claims by confidence: 0.3 4159, 0.5 7902, 0.7 1548, 0.9 78.

Placeholder units by nationality: UK 37, US 28, Germany 21, Japan 11, Allied 3, Poland 3, Soviet Union 2, Australia 1, Canada 1, Netherlands 1, Slovakia 1.

Command relations by relationship: assigned 2670, organic 694, unspecified_subordination 313, attached 257, operational_control 79, unknown 28, administrative_control 14, reserve 14, supporting 2, coordinating 1.

Command relations: start basis claim_date 2517, narrative 1013, assignment_table 515, inferred 23, order 4; end basis open_at_last_claim 2850, inferred_from_next_claim 568, narrative 320, assignment_table 254, inferred 80; `end_unknown` true 207; `change_undated` true 36; status preferred 4064, alternate 8.

Evidence roles of relation links: observed_during 4234, asserts_start 2079, asserts_start_and_end 532, asserts_end 237, listed_by_higher_unit 163.

References by source family: wikipedia 1041, historyofwar_org 281, us_army_cmh 245, lexikon_wehrmacht_de 216, ww2_dk 92, fms_german_manuscript 77, rafweb_org 64, ww2byday_com 33, us_navy_nhhc 21, nara_captured_german_records 20, us_dept_state_frus 20, avalon_law_yale_edu 13, canada_dhh_reports 13, jacar 11, geonames 6, niehorster_org 6, uk_official_history 6, nafziger_naf 5, secondary_history 5, netherlands_defence 3, thesecondwar_pl 3, usaf_historical_division 3, bg387_association 2, dday_overlord_com 2, erenow_org 2, niod_dejong_koninkrijk 2, ownv_nl 2, pegasusarchive_org 2, pism_org_uk 2, trailblazersww2_org 2, uk_hansard 2, us_army_unit_history 2, usmc_history 2, uswarmemorials_org 2, wwiiaircraftperformance_org 2, 69th_infantry_division_org 1, 6juin1944_com 1, actu_fr 1, afhra_unit_records 1, airborneinnormandy_com 1, anciens_aerodromes_com 1, army_mil 1, army_mod_uk 1, battle_of_arnhem_com 1, bevrijdingsmuseumzeeland_nl 1, bigpigeon_us 1, britishmilitaryhistory_co_uk 1, bundesarchiv_de 1, bundesarchiv_ehri 1, canada_ca 1, cgsc_contentdm_oclc_org 1, dehavillandmuseum_co_uk 1, delattre_french_first_army 1, delefosse_v1 1, en_kilroytrip_fr 1, encyclopedia_ushmm_org 1, eucmh_com 1, europeremembers_com 1, fleetairarmarchive_net 1, francearchives_gouv_fr 1, globalsecurity_org 1, historynet 1, ibiblio_pha 1, jacar_go_jp 1, junobeach_org 1, konfliktlandschaften 1, loc_12ag_situation_maps 1, mexico_diputados 1, militaire_spectator 1, militera_lib_ru 1, morison_us_naval_operations 1, muzeummw_pl 1, normandie1944_jimdoweb_com 1, normandie44lamemoire_com 1, okw_kriegstagebuch_schramm 1, oocities_sturmvogel 1, openstreetmap 1, ouest_france_fr 1, pattonthirdarmy_com 1, projectoverlord_co_uk 1, przystanekhistoria_pl 1, tracesofwar_com 1, un_treaty_collection 1, unithistories_com 1, us_war_department 1, usaf_historical_research_center 1, usaf_station_list_anderson 1, ussbs 1, valka_cz 1, veterans_gc_ca 1, warfarehistorynetwork_com 1, wartimes_ca 1, wikimanche_fr 1; by type: encyclopedia 1041, reference_compilation 664, official_history 226, archive_document 173, assignment_table 80, unit_history 36, news_or_web_article 30, gazetteer_geocoder 8, monument_or_memorial 6, other 4.

Places by kind: point 4831, area 117, sea_position 52, line 28.

<!-- counts:end -->

## 5. Known limitations and open items

These are known. Please do not report them as new findings unless you have a fix, a source, or a different view of how they should be handled. Where a row or a pair is named, you can look it up by id.

**Coverage**
- Only the period and units described in section 1. 242 of the units in the table are placeholders; the US Army coverage after June is milestones only (command changes, new headquarters places, first combat, arrivals), with regiments, combat commands, separate battalions, cavalry groups and corps troops left out (`docs/roadmap.md`, "Known gaps").
- The 101st Airborne Division has no *claim* for October and November 1944 (the first claim after 20 September 1944 is 17 December). Since 26 October 2026 its corps and army changes of 18 September to 16 December are carried by relations read from the CMH table (CR0106 to CR0108 and CR0376 to CR0380), with the claims C0567 to C0573 as evidence; there is still no position claim for those weeks.
- Corps and army headquarters places are often not sourced; those rows use a representative point (`location_represents` `sector_center`, 50 km, confidence 0.3). `location_basis` is blank on 211 claims (not yet reviewed).
- A source for corps and army lists (World War II by Day) is a secondary compilation of the CMH order of battle; the CMH pages themselves are blocked to automated readers.

**Command relations** (`docs/methodology.md`, "Command relations table"; `docs/deferred_relations.md`; `scripts/audit_temporal_relationships.py`)
- **Deferred relations D01 to D11**: a claim states a relationship (nearly all `attached`) for a formation below division that is not a unit of the table; each is kept as a row of `docs/deferred_relations.md` with the claim's own words, and is not in the relations table.
- **Undated German parent changes (June 1944)**: five parent changes of German units (21st Panzer, 12th SS Panzer, Panzer Lehr, I SS Panzer Corps, II SS Panzer Corps) that no source dates; they are marked `change_undated` true on six relations (CR0040, CR0041, CR0049, CR0050, CR0053, CR0054); the I SS Panzer Corps change (CR0047, CR0048) was dated on 26 October 2026 as a range (7 to 9 June 1944, narrative) and the 21st Panzer Division change (CR0036, CR0038) as an inferred 8 June (the placeholder CR0037 was removed). The 101st Airborne's corps and army changes are dated from the table since 26 October 2026 (above).
- **`end_unknown`**: 57 relations of temporary kinds (attached, operational control, reserve, administrative control, ...) have no sourced end; their end is inferred from the unit's next claim (39) or open at the last claim (18). A missing end never means "indefinitely".
- **19 documented overlaps** (`command_relation_overlaps.csv`, all of kind `transfer_dates_differ`): two relations of one subject cover the same days because sources disagree on the date of a transfer. Nothing is resolved; each needs a source review (14 of them overlap by more than the boundary day).
- `unspecified_subordination` is used where an assignment table lists a corps for a division without saying assigned or attached (85 relations).
- 39 `attached` or `operational_control` entries of claims are not listed by the unit's next claim (a validator NOTE), and the validator prints three warnings (engaged-with list over three opponents at GER-COR-084C; attached entries without a standing parent at US-ABN-082D and US-ABN-101D).
- Open timing points on the Ardennes rows: the hour of the 101st Airborne / VIII Corps handover on 20 December (Green Book "during the 20th" against the CMH table's 17 December); the hour of VIII Corps' passage to Third Army; the VII Corps handover of the 84th Division (`docs/roadmap.md`, "Batch 3").

**Places and coordinates** (`docs/places_review.md`)
- **PL0285 "Pont Herbert, Manche"** (claim C0225) and **PL0314 "St Anthonis, Nort Brabant"** had wrong points (27 km and 127 km off; the second was in Belgium). Both were re-geocoded on the `sample-verification` branch; see `verification_results.md`.
- **C0006** (352nd Infantry Division, 6 June 1944): the notes put the division headquarters at Le Molay-Littry, inland, but the claim sits on the Omaha Beach point; the qualifier `division HQ Le Molay-Littry` is the only trace of it.
- Five places were merged (retired ids in `data/place_merges.csv`); the other groups of places that share a point were reviewed and kept (`docs/places_review.md`, sections 2 and 4).
- `scripts/check_coordinates.py` prints 3 warnings (speed between consecutive rows of US-ARM-004D, US-INF-030D, US-INF-094D) and lists 5 explained exceptions. Points are place-centre geocodes (Wikipedia, OpenStreetMap), not unit positions; `precision_km` is the honest radius, not a measured error.

**Evidence and sources**
- **C0039** (21st Army Group, 7 June 1944) names "First Army" in `composing_text`; the cited pages do not say which army; the name could be the US, the German or the Canadian First Army. It is kept as text and not guessed (`docs/unit_references_review.md`, item 4).
- The sources are mostly secondary: of the references, Wikipedia pages and the Lexikon der Wehrmacht are the two largest families, followed by the US Army CMH volumes (see the counts). Several Wikipedia pages count as one family for the confidence rubric. 10 reference links are recorded as not readable by an automated check (9 `blocked_403`, 1 `error`).
- `strength_json` (a figure for personnel, vehicles) is filled on 23 claims only; `strength_status` is `unknown` on 554.
- `commander` is free text (named in the source, or `unknown`); there is no commanders table and no check that a name is spelled the same way in every row.
- Dates are days (YYYY-MM-DD); times appear only in command relations, where a source gives an hour. A date range or an approximate date is expressed in `notes` and the confidence, not in a field.

## 6. Running the checks

Python 3.8 or later, standard library only; run from the dataset folder (`WorldWar2/` in the GitHub repository).

```
python scripts/validate.py                       # schema, references, vocabularies, rules: expect 0 errors and 3 warnings
python scripts/build.py --check                  # generated files up to date (build/, docs/coverage.md, data/references.csv)
python scripts/build_references.py --check       # references table matches the claims
python scripts/check_coordinates.py              # coordinate warnings (3) and explained exceptions (5)
python scripts/audit_command_location.py         # pattern audit of command relationships and coordinate provenance
python scripts/audit_temporal_relationships.py   # temporal audit of command relations (twelve patterns)
python scripts/who_controls.py US-ARM-004D 1944-12-19      # which higher headquarters held a unit on a date
python scripts/check_claim_ids.py --base <revision>        # claim ids not reused or dropped since a revision (needs git history)
python scripts/review_sample.py --check          # this packet's sample and counts match the data
```

A pull request runs `validate.py`, the coordinate and temporal audits, and `build.py --check` (`.github/workflows/validate.yml`). The audits print review prompts; they do not fail.

## 7. What we do not want reviewed

- The licence (the whole repository is CC BY-SA 4.0; confirmed by Scott, 24 November 2026) and the repository's publication format; the choice is made. A question on whether the licensing and terms of each source are recorded clearly enough is welcome (question 10).
- The `zip` or any packaged download of the data; only the repository is in scope.
- Style of the prose and spelling, unless it makes a rule ambiguous.
- Coverage you wish existed (other months, other theaters, other armies). Whether the design would carry them is welcome (questions 8 and 9); which units to add next is not.
- Anything already listed under "Known limitations" above, unless you can resolve it with a source.

## 8. How to send findings

Use [findings_template.md](findings_template.md): one finding per row, with the table, the row id, a severity, the issue, the evidence (link and page) and a suggested fix. Say plainly when you could not verify something. Answers to the ten questions can be short.
