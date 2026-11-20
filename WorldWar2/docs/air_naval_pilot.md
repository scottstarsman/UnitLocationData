# Air and naval pilot (branch `air-naval-pilot`, 13 November 2026)

Scott asked on 13 November 2026 for a small air and naval pilot before the data is opened up, to find out whether the data structures need changes. This note is the result. It is a proposal for Scott's approval; only the minimum needed to store the pilot rows was changed (section 3).

## 1. What was entered

34 real, cited claims (`C9405`-`C9438`), 18 units (13 active, 5 placeholders; two more placeholders were dropped, see 2.9), 17 places (`PL4160`-`PL4176`), 16 references (`R896`-`R911`), 11 command relations (`CR1292`-`CR1305`; `CR1296`, `CR1299` and `CR1300` were dropped for lack of evidence claims, see 2.9, so those three ids are unused), 1 lineage row (`UL020`), 2 conflict groups (`G126`, `G127`) and 1 claim-key exception.

| Part | Units | Claims |
|---|---|---|
| Luftwaffe | Luftflotte 3 (existing), II Jagdkorps, JG 26, II./JG 26, III./JG 26 | `C9405`-`C9415` (bases Chantilly, Flammersfeld, Cormeilles, Guyancourt, Villacoublay, Creil; D-Day strafing of Sword) |
| USAAF | 366th Fighter Group, 390th Fighter Squadron, IX TAC (placeholder) | `C9416`-`C9422` (RAF Thruxton, ALG A-1, A-41, A-70) |
| Naval | USS Texas, USS Satterlee, HMS Warspite, HMS Bedale / ORP Ślązak, 5. Torpedobootsflottille, task groups (placeholders) | `C9423`-`C9436` |
| Coastal artillery | Marine-Artillerie-Abteilung 260 (ground by function, decided, see 4) | `C9437`-`C9438` |

No RAF or RCAF unit was entered (optional in the brief; the source work was kept small).

## 2. Where the design strains

### Confirmed (hit while entering the rows)

1. **Build crash on a relation whose subject is not ground.** `scripts/build.py` passed only ground units to `command_relations.derived_rows`, so any relation with an air or naval subject raised `KeyError`; `validate.py` and the semantic tests did not catch it. A higher unit of another domain would also have been shown with a blank name. *Fixed* (3.1).
2. **No place for a ship at sea.** A place has to be a point, area or line with a nearest-coast country. Texas (12,000 yd off Pointe du Hoc) and Satterlee (1,500 yd) needed two hand-worked offshore area places (`PL4170`, `PL4171`) whose bearing (due north) is assumed. Every such place is a small invention. Proposal: a `kind` value or a place flag `at_sea` with the anchor place and distance in the place note, and a rule that such points never rise above 0.5.
3. **A range without a bearing.** Warspite is "26,000 yards offshore" of the Villerville battery; no point can be worked out. The row uses the battery as `objective` at 0.3 (`C9426`). Same for the mine "28 miles off Harwich" (`C9430`, Harwich, precision 50 km, 0.3).
4. **Base against target for flying units.** `location_represents` has no `base` value: the 366th on D-Day is at its station (`main_body`, `C9416`) while JG 26 on D-Day is known only over Sword Beach (`objective` at 0.3, `C9410`). A flying unit has two answers a day; the schema holds one. Proposal: add `base` (airfield or port) to `location_represents`.
5. **One unit on two airfields on the same day.** III./JG 26 arrived at Guyancourt and Villacoublay together (`C9412`, `C9413`). The claim key `(unit, date, event_type)` rejected it; a `claim_key_exceptions` row was needed. For air units this is routine, not an exception. Proposal: allow a second row when `place_id` differs and both rows say `main_body` is split (a `location_represents` value `main_body_part`).
6. **No event type for launch, commissioning, mine strike or sortie.** `other` was used for `C9416`, `C9430`, `C9432` and `C9435`. Proposal: add `commissioning` and `sortie`.
7. **Echelon vocabulary is used in two ways.** Existing air units (II Fliegerkorps `corps`, Luftflotte 3 `army`) use ground-equivalent echelons, while `air_force`, `air_formation`, `fleet` and `naval_unit` are reserved and unused. The pilot used ground equivalents for air units (corps, regiment/battle_group for a Geschwader or fighter group, battalion for a Gruppe or squadron) and the reserved `naval_unit` and `fleet` for ships and task groups. The validator accepted all of them. Decision for Scott: keep the mixed convention, or use the reserved air values for air units too (then `echelon_rank` needs entries, 5.1).
8. **Airfield naming.** Airfields have station codes (A-1, A-41, AAF-407, Y-29) and the commune name is often not the airfield's (Cormeilles in the Oise, in the Eure and Cormeilles-en-Vexin). Places carry only a name; the station code was put in the place name and note. The Cormeilles reading of the JG 26 article (`PL4162`) follows the article's own link and is uncertain (`C9411` at 0.3).
9. **Evidence rule for relations.** A relation needs a linked claim, and a `narrative` start needs a `stated_effective_from` on a linked claim. The 366th's assignments to XXIX TAC (1 October 1944) and back to IX TAC (22 October), and II Jagdkorps under Luftwaffenkommando West from 26 September 1944, are dated in the sources but no pilot claim falls in those intervals, so they could not be stored (the two placeholders `GER-LKW-000H` and `US-TAC-029C` were removed again). Air and naval units, which have few claims, are hit harder than ground units.
10. **Missing intermediate level.** JG 26 sat in 5. Jagddivision in II. Jagdkorps; the division is not a unit, so `CR1293` skips it (`unspecified_subordination`).
11. **Lineage has no alternates.** HMS Bedale / ORP Ślązak: the commissioning is 17 April 1942 (Wikipedia) or 30 April (Polish Navy Museum). `UL020` records the month and the two dates in its note. The note is enough for the pilot; an alternates column would be needed only if such conflicts become frequent.
12. **Hard-coded test.** Scenario 172 listed the exact other-domain claims; it was changed to ignore ids from `C9000` up. Every future other-domain claim would have broken it.
13. **Unit-naming convention.** The README has no convention for air and naval ids. The pilot used `GER-JGK-002C`, `GER-JG-026`, `GER-JGGR-026-2` (Gruppe), `US-FG-366`, `US-FS-390`, `US-TAC-009C`, `US-BB-035`, `US-DD-626`, `UK-BB-WARSPITE`, `POL-DD-L26`, `GER-TBF-005`, `UK-TF-S`, `US-TG-124-9`. Proposal: write these down in `schema/README.md` before opening the data.

14. **`check_claim_ids.py` does not see air and naval claims.** On this branch it reported "claims at origin/main 9393, now 9395, new ids C9437..C9438": the 32 air and naval claims `C9405`-`C9436` are invisible to it, so a reused or dropped other-domain claim id would go undetected, and its "next free id" is correct here only because the ground claims `C9437`-`C9438` come last. The next free id of the pilot (`C9439`) was checked by hand against all claim files. Proposal (not made): read `build/other_domains/claims.csv` as well.
15. **Existing derived counts move when a new ground unit is added.** `PL0089` Cherbourg in `build/places.csv` changed from 9 to 10 claims because `C9438` is a ground row; every other main-output difference is an added row (`GER-MAA-260`, `CR1305`, `C9437`, `C9438`, the new places). Nothing about an existing unit's answer changed.

### Theoretical (not hit)

- **Echelon rank.** `echelon_rank` has no entry for the reserved values; the validator ranks an unlisted echelon 0 and the audits rank it 8. No pilot row triggered a disagreement, but a ship above a division would.
- **Multinational formations.** The id prefix must equal the nationality code; a combined Anglo-American task force has no code.
- **Embarked or attached units** (a squadron on a carrier, aircraft attached to an army) have no representation except relations that stay in `other_domains`; a ground unit's air support never shows in the main outputs.
- **Time of day.** Naval and air events are dated to the hour (05:52, 06:30) but claims carry a date only.
- **Strength.** `strength_json` has no vocabulary for aircraft or ship counts.
- **Several bases per unit.** A Gruppe's Staffeln on different fields (one row per field is the only way).
- **Domain per unit, not per period.** A unit changing domain (a naval unit turned into infantry) cannot be shown.
- **Captured or renamed vessels** beyond one rename (a change of flag mid-war would need two unit records, as UL020 does, and a different id prefix).

## 3. Changes made (minimum)

1. `scripts/build.py` and `scripts/command_relations.py`: `derived_rows` takes an optional `subjects` set; the main `command_relations.csv` is still limited to ground subjects, and a new `build/other_domains/command_relations.csv` carries the air and naval ones (names of higher units of any domain kept). Main outputs are unchanged for existing data.
2. `data/units.csv`: 18 new units (listed in the changelog); the reserved echelons `fleet` and `naval_unit` are now used, so the "not yet used" wording in the vocabulary is stale (left for Scott's decision, 5.1).
3. `scripts/semantic_tests.py`: scenario 172 relaxed; scenarios 244-247 added.
4. `docs/review/` regenerated (relations changed).
5. One sentence in `schema/README.md` (the new other-domain output file). No change to `schema/vocabularies.json` or the validator.

## 4. Decision: Marine-Artillerie-Abteilung 260 (closed 13 November 2026)

A Kriegsmarine coastal artillery battalion fights on land. It was entered as `ground` (like flak, Scott 4 November 2026) with branch `Navy`, so it appears in the main outputs and in `who_controls` (new keys only). Flipping it to `naval` is one cell in `data/units.csv` and moves `C9437`, `C9438` and `CR1305` to `build/other_domains/`. **Decided by Scott, 13 November 2026: ground.** `GER-MAA-260` stays ground, as a general rule for flak and coastal artillery whatever service owned them (the `branch` column records the service); standing rule 23 in `docs/HANDOFF.md`.

## 5. Recommended next steps (for Scott's approval)

1. Decide the echelon convention (2.7) and add `echelon_rank` entries for the reserved values.
2. Add `base` to `location_represents` and `commissioning` and `sortie` to `event_type` (2.4, 2.6).
3. Add a rule and a place flag for sea positions (2.2, 2.3).
4. Allow a second same-day row when the place differs (2.5), or document the exception route.
5. Write the air and naval id conventions into `schema/README.md` (2.13).
6. Roadmap 375 keeps the leftovers (II Jagdkorps from August 1944 in Rochefort; the 366th's later stations; the 5. Jagddivision; RAF/RCAF and further ships).

## 6. Follow-up proposals: ships (13 November 2026)

Scott agreed to these in principle (13 November 2026) and decided two further points the same day: submarines and the other hull codes are in scope (6.1, 6.3), and claims are recorded even when a unit is outside the current scope (section 7, standing rule 22). **Proposals only: nothing below is implemented.** No schema, vocabulary, validator or data file was changed for this section; the pilot rows keep the values described in sections 1-3 until Scott approves the implementation separately.

### 6.1 Granularity

- Every **commissioned combatant of destroyer-escort size or larger** gets its own unit: battleships, carriers, cruisers, destroyers, destroyer escorts and their national equivalents, including German torpedo boats, frigates and corvettes, and **every commissioned submarine** (U-boats, British, American and other Allied boats; decided 13 November 2026).
- **Smaller craft** are entered at flotilla or squadron level: MTB, S-boat and minesweeper flotillas, LST groups, landing-craft flotillas.
- A **single small craft** gets its own unit only when a source singles it out (a famous LCT or S-boat, say), and only if it traces to a parent flotilla or squadron (the same rule as for companies).

### 6.2 Naval echelon ladder

A ladder of its own, not forced onto army ranks:

| Level | Proposed `echelon` value | Examples | Today in the pilot |
|---|---|---|---|
| ship | `naval_unit` (existing reserved value, narrowed to a single vessel) | Texas, Warspite, Satterlee, Ślązak | `naval_unit` (unchanged) |
| division or flotilla | `naval_division` (new) | destroyer division, S-boat flotilla, minesweeping flotilla, 5. Torpedobootsflottille | `GER-TBF-005` is `fleet`; would change to `naval_division` |
| squadron | `naval_squadron` (new) | destroyer squadron, cruiser squadron | none |
| task unit, task group, task force | `task_group` (new; the sub-label task unit, task group or task force goes in the unit note) | `US-TG-124-9` (Task Group 124.9), `UK-BF-D` (Bombarding Force D), `UK-TF-S` (Force S) | all three are `fleet`; would change to `task_group` |
| fleet | `fleet` (existing reserved value, narrowed to numbered fleets and naval commands) | Home Fleet, Seventh Fleet, Marinegruppe West | `GER-MGW-000H` is `other` (older entry); would change to `fleet` |

How it maps onto the reserved values: `naval_unit` keeps its meaning but only for a single vessel (its vocabulary text "ship, squadron or other naval unit" would be corrected); `fleet` stops meaning "task force or flotilla headquarters" and means a numbered fleet or a naval command. Three values are new: `naval_division`, `naval_squadron`, `task_group`. `air_force` and `air_formation` stay reserved and are not touched.

**Proposed `echelon_rank` values** (a separate range so naval ranks never collide with ground ranks): `naval_unit` 10, `naval_division` 11, `naval_squadron` 12, `task_group` 13, `fleet` 14. The hierarchy check (a parent must outrank its child) would apply within the naval ladder only; links between a naval unit and a ground unit are `supporting` or `coordinating` relations, not standing subordination. None of the new values takes an id letter (they would be added to the `no_letter` list of `echelon_id_letter`), so ids such as `UK-TF-S` and `GER-MGW-000H` stay as they are.

**Task organisations hold command relations only.** A task unit, group or force is a shifting organisation; it normally gets no location claim of its own, and its ships carry the locations. Such units would stay `record_status: placeholder` permanently, which means the validator rule "only a placeholder has no claim file" and `promote_placeholders.py` need one clarifying sentence (a task organisation with relations is complete without claims).

### 6.3 New unit columns

- **`ship_type`**: a fixed list based on US hull classification codes, each with a plain-English label in a new vocabulary `ship_type`. National terms (Torpedoboot, escort destroyer, Panzerschiff, frigate in the Royal Navy sense) stay in the unit note.

| Code | Label |
|---|---|
| BB | battleship |
| BC | battlecruiser |
| CV | fleet aircraft carrier |
| CVE | escort carrier |
| CA | heavy cruiser (also the German Panzerschiff, noted) |
| CL | light cruiser |
| DD | destroyer |
| DE | destroyer escort (also the Royal Navy escort destroyer, for example the Hunt class) |
| PF | frigate |
| TB | torpedo boat |
| CORV | corvette |
| CVL | light aircraft carrier |
| SS | submarine (any navy; U-boats, British and US boats; midget submarines too, noted) |
| PG | gunboat or sloop (Royal Navy sloops, patrol gunboats) |
| CM | minelayer |
| AM | minesweeper (fleet minesweepers entered singly; flotillas of small minesweepers stay at flotilla level, 6.1) |

  **Closed 13 November 2026:** submarines and the other hull codes are in scope; the list above (including SS, CVL, PG, CM and AM) is the proposed full set for the entries of 6.1. No code for the 1990s `SSK` (not a WWII type; every WWII submarine is `SS`). Auxiliaries (oilers, transports, depot ships) are not combatants and have no code. The column is blank for non-ships and for flotillas and task groups.
- **Submarine types are handled through `ship_classes`, not through `ship_type`:** a U-boat is `SS` and its class row carries the German type, for example Type VIIC (sub-type rows such as VIIC/41 point to it through `parent_class_id`), Type IXC and its IXC/40 sub-type, Type XXI. The same for British (T class, S class) and US (Gato, Balao) boats. Hull number is the boat's number (`U-505`). U-boat flotillas (for example 2. U-Flottille) are `naval_division`, and a submarine at sea has the same sea-position problem as a surface ship (2.2, 2.3).
- **`hull_number`**: free text as the sources give it (`BB-35`, `DD-626`, `L26`, `03`). It is not a key: pennant numbers were reused and changed, so uniqueness is checked only within a nationality and a period, and as a warning at most.

### 6.4 A `ship_classes` table

New file `data/ship_classes.csv` (output in `build/other_domains/ship_classes.csv`), with its own schema file, validator checks and README section.

| Column | Meaning |
|---|---|
| `class_id` | its own id, `SC001` and up; never the lead ship's id |
| `class_name` | for example Hunt class Type II, New York class, Type 1934A destroyer, Type 1939 torpedo boat |
| `parent_class_id` | blank for a class; set for a sub-type (a Type II row points at the Hunt class row) |
| `sub_type` | the sub-type label (Type I-IV) or blank |
| `nationality` | the nation that designed and built the class, which can differ from a ship's flag (Hunt Type II is British; Ślązak flew the Polish flag) |
| `ship_type` | the code of 6.3 |
| `lead_ship_name` | name only, as text; the lead ship need not be in the dataset (HMS Hunt never existed as such; German classes named by year have none) |
| `capabilities_json` | nominal **as-designed** capabilities, with a source on every figure (below) |
| `reference_ids` | the references the class row rests on |
| `class_note` | free text |

`capabilities_json` follows the pattern of `strength_json`: an object whose keys are `standard_displacement`, `speed`, `main_armament`, `secondary_armament`, `anti_aircraft`, `torpedo_tubes`, `aircraft`, `complement`, each `{"value": ..., "unit": ..., "reference_id": "R###", "note": ...}`. A key is simply absent when no source gives it (nothing is guessed). `check_json_fields.py` would validate the shape. Capabilities live on the most specific row; a sub-type row repeats only what differs from its parent family row, and a missing key on a sub-type means "as the family row".

**Reasons for a table of its own:** lead ships are often absent from the dataset; some classes are named by year; some have sub-types; a transferred ship keeps its class (Bedale and Ślązak are both Hunt Type II). A unit links to its class through a new `ship_class_id` column in `units.csv` (blank for non-ships and for formations; the validator checks that it exists and that the unit's `ship_type` equals the class's).

### 6.5 Refits and reclassification

- **Refits override the class figures as dated, sourced records**, the way `strength_json` works on a claim: a naval claim row may carry a `capabilities_json` with `as_of` (the date of the refit), `basis: refit` and a `source`, holding only the figures that changed (for example a battleship's anti-aircraft fit or radar after a refit). The ship's answer for a date is the latest refit record on or before that date, else the class row. Nothing from a refit is copied into the class.
- **Reclassification** (for example DD to DMS) is recorded as a `redesignation` claim (an existing event type) with old and new type in the notes; the unit's `ship_type` holds the type in force on the ship's first claim. A change of flag or name that creates a new unit record is still a lineage row (`UL020`).

### 6.6 Example under the proposed fields

Values marked "to be sourced" are not entered here; the class figures would come from a cited reference before any row is written.

| Unit | `echelon` | `ship_type` | `hull_number` | `ship_class_id` | Class row |
|---|---|---|---|---|---|
| `US-BB-035` USS Texas | `naval_unit` | BB | BB-35 | `SC001` | New York class, US; lead ship USS New York; main armament ten 14-inch guns (to be sourced) |
| `UK-BB-WARSPITE` HMS Warspite | `naval_unit` | BB | 03 | `SC002` | Queen Elizabeth class, UK; lead ship HMS Queen Elizabeth; main armament eight 15-inch guns (to be sourced) |
| `US-DD-626` USS Satterlee | `naval_unit` | DD | DD-626 | `SC003` | Gleaves class, US; lead ship USS Gleaves; main armament five 5-inch guns (to be sourced) |
| `UK-DD-BEDALE` HMS Bedale (to `POL-DD-L26`, `UL020`) | `naval_unit` | DE | pennant to be sourced | `SC005` | see below |
| `POL-DD-L26` ORP Ślązak | `naval_unit` | DE | L26 | `SC005` | Hunt class Type II (sub-type row `SC005`, parent family row `SC004` Hunt class, UK; lead ship named by the source, to be sourced) |

Bedale and Ślązak share `SC005` although the flag changed; the class nationality is British. A refit example: a Texas or Warspite claim could carry `{"as_of": "...", "basis": "refit", "anti_aircraft": {...}}` once a source dates the fit. Illustration only (not a pilot unit): a U-boat such as U-505 would be `ship_type` SS, `hull_number` `U-505`, class Type IXC/40 (sub-type row under the Type IX family row). Task groups such as `US-TG-124-9` (`task_group`) would carry no `ship_type`, no class and no claims, only the relations of the ships in them.

### 6.7 What implementation would touch (for Scott's approval)

`schema/vocabularies.json` (echelon, `echelon_rank`, `echelon_id_letter` `no_letter`, new `ship_type`), `schema/units.schema.json` and the README (`ship_type`, `hull_number`, `ship_class_id`), a new `ship_classes` schema and file, `scripts/validate.py` (class links, type match, naval rank check), `scripts/build.py` (class output), `scripts/check_json_fields.py`, and data changes to the pilot rows: the echelons of `GER-TBF-005`, `UK-BF-D`, `UK-TF-S`, `US-TG-124-9` and `GER-MGW-000H`, and the new columns and class rows for the five ships. Each change would be annotated old value, new value, reason, in the record and the changelog.

## 7. Out-of-scope claims (standing rule 22, 13 November 2026)

Scott decided on 13 November 2026 that a claim is recorded even when its unit is outside the current scope (any domain, front or period), because it will help as scope grows. It is written up in `docs/HANDOFF.md` as standing rule 22, in `CONTRIBUTING.md` and `docs/methodology.md`, and builds on rule 19 (read every source for all fronts and periods).

- Out-of-scope claims follow every normal claim rule and stay **out of the main outputs and the grid**, the way `build/other_domains/` keeps air and naval claims today.
- **Coverage and source-balance figures for out-of-scope areas are labelled incidental, not surveyed:** they show what the sources happened to give, not a systematic search, and are not compared with the surveyed Western Front figures.
- **Not built yet.** Today only the unit `domain` separates claims. Nothing separates a ground unit on another front or in another period; the existing before-6-June-1944 rows under `OP-PRE-INVASION` are in the main outputs and stay as they are. A proposal for implementation (Scott to approve): a `scope` marker (`in_scope`, `out_of_scope`) on the unit record, with `build.py` writing out-of-scope units and claims to `build/other_domains/` (or a sibling folder) and the coverage and balance tools adding an "incidental" label. Until then, only rows that the unit `domain` already keeps out of the main outputs are entered under the new rule; other out-of-scope facts stay where rule 19 puts them (private notes). Roadmap 375 (k).


## 8. Implementation (air-naval schema pass, 13 November 2026)

Scott approved building the section 5 and 6 proposals ("Let's do the schema pass now", 13 November 2026). Branch `air-naval-schema`. What was built, where, and what differs from the proposal:

| # | Item | Built |
|---|---|---|
| 1 | Scope marker | `units.scope` (vocabulary `scope`: `in_scope`, `out_of_scope`; blank is `in_scope`). `build.py` routes a unit that is air or naval **or** `out_of_scope` (helper `common.other_output_unit_ids()`) with its claims and relations to `build/other_domains/`; `coverage.csv` and the main `units.*` leave it out, and the five columns `domain`, `scope`, `ship_type`, `hull_number`, `ship_class_id` are dropped from the main `units.*` so its columns are unchanged. `other_domains/units.csv` lists them. No unit of the data is marked `out_of_scope` yet. Coverage and balance figures for out-of-scope areas are labelled "incidental, not surveyed" (rule 22). Scenario 248. |
| 2 | Ship columns | `units.ship_type` (vocabulary `ship_type`, US hull codes: BB, BC, CV, CVL, CVE, CA, CL, DD, DE, PF, CORV, TB, PG, CM, AM, SS, each with a plain-English label; national terms stay in the note), `units.hull_number` (free text, not a key), `units.ship_class_id`. Only on echelon `naval_unit`; the validator checks class existence and that the `ship_type` equals the class `ship_type`. The five pilot ships carry them. Scenario 249. |
| 3 | `data/ship_classes.csv` | Schema `schema/ship_classes.schema.json`; validator `check_ship_classes`; `check_json_fields.py` validates `capabilities_json` (`schema/json/capabilities_json.schema.json`); build output `build/other_domains/ship_classes.csv`. Seeded with 200 rows (SC001-SC200): US 65, UK 64, Germany 39, France 18, Netherlands 7, Poland 6, Canada 1. See 8.2. Scenario 250. |
| 4 | Refits and reclassification | A refit is a dated `capabilities` object inside the existing `strength_json` column of a naval claim (`basis` `refit`, `as_of`, `source`, only the figures that changed, each with its own `reference_id`; the new `strength_json_basis` value `refit`). **Deviation from the proposal:** the proposal said a new `capabilities_json` claim column; that would rewrite all 444 claim files for a column that is blank on all but a few rows, so the object lives in `strength_json` instead (same sourcing and dating rules, no migration). A reclassification is a `redesignation` claim of a ship stated as "Reclassified from <old> to <new>" in the notes (warning when missing). Scenario 251. |
| 5 | Naval echelon ladder | `naval_unit` 10, `naval_division` 11, `naval_squadron` 12, `task_group` 13, `fleet` 14 in `echelon_rank`; no id letter (vocabulary `echelon_id_letter` `naval_exempt`; a final letter on such an id is not an echelon letter). Naval-ladder echelons need domain `naval`. The hierarchy check applies within the naval ladder only (`naval_hierarchy_problem`). A task organisation is a placeholder that holds relations (as the higher unit) and has no claim file. Pilot units re-echeloned: `GER-TBF-005` to `naval_division`, `UK-BF-D`, `UK-TF-S` and `US-TG-124-9` to `task_group`, `GER-MGW-000H` to `fleet`. `GER-KSN-000H` (a coastal-defence command, not a fleet) stays `other`. `display_order` lists ground echelons only. Scenario 252. |
| 6 | Sea positions, `base`, event types | Place kind `sea_position` (claims capped at confidence 0.5, a `coord_source_note` is required); `location_represents` `base` (airfield, port or anchorage a unit operates from); event types `commissioning` and `sortie`. Scenario 253; the revisited pilot rows are listed in the changelog. |
| 7 | `check_claim_ids.py` | Reads `build/other_domains/claims.csv` at the base revision and in the working tree as well as `build/all_claims.csv`. Scenario 254. |
| 8 | Id convention | 8.1 below. |

### 8.1 Id-naming convention for air and naval units

`NATION-TYPE-NUMBER-OR-NAME`, upper case, the nation code of `nationalities.csv`, as for ground units; ids are opaque, stable and never renamed. Naval-ladder units and ships carry **no echelon letter**.

- **Ships:** `NATION-<ship_type>-<hull number as 3 digits>` where the navy numbers hulls (`US-BB-035`, `US-DD-626`); a Royal Navy ship by name in capitals (`UK-BB-WARSPITE`, `UK-DD-BEDALE`); a ship known by its pennant keeps the pennant (`POL-DD-L26`); a U-boat `GER-SS-U<number as 3 digits>` (`GER-SS-U047`, not yet used). A ship that changes flag or name gets a new unit and a lineage row (`UL020`), not a renamed id.
- **Naval formations:** flotilla or squadron `NATION-<type code>-<number>` (`GER-TBF-005`); task group or task force `US-TG-<group number with dashes>` (`US-TG-124-9`), `UK-TF-<letter>` and `UK-BF-<letter>` for Royal Navy forces; fleets and naval commands as headquarters (`GER-MGW-000H`).
- **Air units:** `NATION-<unit type code>-<number>`: Geschwader `GER-JG-026`, Gruppe `GER-JGGR-026-2` (wing number, Gruppe number), fighter corps `GER-JGK-002C`, air fleet `GER-LFL-003A`; US group `US-FG-366`, squadron `US-FS-390`. The echelon letter on the pilot air ids (`A`, `C`) is kept because ids never change; a new air id has no letter unless its echelon is a ground echelon with a letter.
- **Ship classes:** `SC001` onward, never the lead ship's id, never reused.

### 8.2 Ship class seeding

200 class rows from the English Wikipedia pages of the classes (184 references `R912`-`R1095`, family `wikipedia`, accessed 13 November 2026), for the US, UK, Germany, France, Netherlands, Poland and Canada: battleships, battlecruisers, carriers (CV, CVL, CVE), cruisers, destroyers, destroyer escorts and frigates, corvettes, torpedo boats, sloops, minelayers and minesweepers, and submarines including the Hunt sub-types (Type I-IV) and the U-boat sub-types VIIA-VIIF, VIIC/41, IXA-IXD2, IXC/40, plus the Types XXI, XXIII and II. Each figure is the infobox text as written, with its own `reference_id`; no figure is entered that a page does not give (a missing key means the page gave nothing for it). The armament lines are sorted by keyword into main, secondary, anti-aircraft and torpedo (class note says so), depth-charge and mine lines are left out, and where a page lists several configurations the first is used (the `note` of the figure or the class note names it). The three family rows with figures only on their sub-type rows (Hunt, Type VII, Type IX) hold no figures. What is not seeded is in roadmap 375 (l).

## 9. Air schema pass (13 November 2026, branch `air-naval-schema`, added to PR #90)

Scott approved an air schema pass before the Normandy pass ("Yes", 13 November 2026): the bomber groups need the echelon ladder, the aircraft table, aircraft strength and the operational/administrative distinction together. Built as separate commits on the open `air-naval-schema` branch. This section supersedes the earlier statement (section 2, item 7) that air units use ground-equivalent echelons.

### 9.1 Air echelon ladder

Ranks 20-25, outside the ground (0-8) and naval (10-14) ranges. The brief suggested "1-9", which collides with the ground ranks (`battalion` is 1, `division` 4, `army_group` 7), so the 20s are used. The rank is the **level**, not the national name. A RAF wing is the level of a US group and a RAF group the level of a US combat wing; the table below is the source of truth and the hierarchy check reads the rank only.

| rank | echelon | Luftwaffe | USAAF | RAF |
|---|---|---|---|---|
| 19 | `air_flight` (added 19 November 2026, chunk 8a) | (a Staffel is `air_squadron`) | flight or detachment organised as a unit | flight, servicing echelon, communication flight, development unit, glider or parachute servicing unit, forward staging post |
| 20 | `air_squadron` | Staffel | squadron | squadron |
| 21 | `air_group` | Gruppe | group | **wing** |
| 22 | `air_wing` | Geschwader | combat wing (bomb, fighter, troop carrier wing) | **group** |
| 23 | `air_division` | Jagddivision, Fliegerdivision | air division, bomb division, command (IX Bomber Command, IX Fighter Command), tactical air command (IX TAC, XXIX TAC) | (no standing level; a tactical group such as No. 83 Group is `air_wing`) |
| 24 | `air_corps` | Fliegerkorps, Jagdkorps | (none in the 1944-45 theater) | (none) |
| 25 | `air_force` | Luftflotte | numbered air force (Eighth, Ninth) | command (Bomber Command, Fighter Command), Second Tactical Air Force |

No id letter (`echelon_id_letter` `air_exempt`); `air_formation` and the reserved description of `air_force` are replaced. `validate.air_hierarchy_problem`: within the ladder a higher unit must outrank its subject (a Geschwader under a Jagdkorps is fine, a Jagdkorps under a Gruppe is an error); `supporting`, `coordinating` and `unknown` are not checked, and a relation across ladders (a flak regiment under a Fliegerkorps, a group under an army) is not. An air-ladder echelon needs domain `air`; a domain-air unit with a ground echelon is a warning. Scenario 255.

**Re-echeloned pilot units** (old value, new value, reason; `units.csv`, the repeated `echelon` column of the claim files, and a `Review:` line in each `unit_note`; ids unchanged):

| unit | old | new | reason |
|---|---|---|---|
| GER-LFL-003A Luftflotte 3 | `army` | `air_force` | top of the air ladder |
| GER-FLK-002C II Fliegerkorps | `corps` | `air_corps` | Fliegerkorps |
| GER-JGK-002C II Jagdkorps | `corps` | `air_corps` | Jagdkorps |
| GER-JG-026 JG 26 | `regiment/battle_group` | `air_wing` | Geschwader |
| GER-JGGR-026-2, GER-JGGR-026-3 | `battalion` | `air_group` | Gruppe |
| US-TAC-009C IX Tactical Air Command | `corps` | `air_division` | tactical air command |
| US-FG-366 366th Fighter Group | `regiment/battle_group` | `air_group` | US group |
| US-FS-390 390th Fighter Squadron | `battalion` | `air_squadron` | squadron |

### 9.2 `aircraft_types`

`data/aircraft_types.csv`, a table like `ship_classes` (`AT001` onward; family row plus variant rows, one level). Columns: `type_id`, `designation`, `nationality`, `role` (vocabulary `aircraft_role`), `manufacturer`, `parent_type_id`, `variant`, `performance_json` (`max_speed`, `range`, `service_ceiling`, `armament`, `bomb_load`, `crew`, each with its own `reference_id`; never estimated), `reference_ids`, `type_note`. Validator `check_aircraft_types` (header, ids sorted, designation unique per nationality, `parent_type_id` and `variant` together, parent is a family row, references exist and are listed, a variant repeating a family figure warns); JSON schema `performance_json.schema.json`; build output `build/other_domains/aircraft_types.csv`. Scenario 256.

**Seeding.** 102 rows (AT001-AT102) from the Specifications section of the English Wikipedia page of each type (52 references `R1096`-`R1147`, family `wikipedia`, accessed 13 November 2026), in four commits: US 28 rows (P-47, P-51, P-38, P-61, B-17, B-24, B-26, A-20, A-26, B-25, C-47, C-46, CG-4, L-4, L-5), UK 29 (Spitfire Mk Vb and Mk XIV, Typhoon, Tempest, Hurricane, Mosquito, Lancaster, Halifax, Stirling, Wellington, Meteor, Beaufighter, Auster, Horsa, Hamilcar, Sunderland), Germany 42 (Bf 109, Fw 190, Me 262, Me 163, Ar 234, Ju 88, Ju 87, Me 410, Bf 110, He 219, Do 217, He 111, He 177, Ju 52, Fi 156, Hs 129, Ju 188, Do 335, Go 242, Fw 189, He 162), and Canada 3 (Lancaster X, Mosquito B Mk XX, Hurricane Mk XII: Canadian-built variants named on the pages of the types; no figures, the pages give specifications for other variants). A figure is the page's own for **one named variant** (the section heading, repeated in the row's note); the family row carries none. Where a page gives no figure for a key the key is absent (the gliders have no maximum speed; the L-4 page describes the civil Cub, so the L-4 is a family row only).

**1944-45 variants** (13 November 2026, same branch, Scott: "Go ahead and add those variants to this branch"). 32 rows `AT103`-`AT134` and 11 references `R1148`-`R1158`. Already present and not repeated: Spitfire Mk XIV, Beaufighter TF Mk X, Sunderland III, C-47 / C-47B-DK, C-46 / C-46A, CG-4A, Horsa / Horsa Mk II, Hamilcar, Fw 190A-8. Added with named-variant figures: Spitfire LF Mk IXe (specifications table, `R1148`); Spitfire Mk XVI armament (`R1149`); P-51B and Mustang Mk III (`R1150`; Mustang Mk III uses the page's P-51B figures, annotated); Bf 109G-14, G-14/AS and K-4 (`R1151`); Fw 190D-9 (Rechlin report, `R1157`); Fw 190F-8 armament (`R1152`); Ju 88G armament (`R1131`); Mosquito FB Mk VI (A&AEE HX.809 speed, `R1156`; museum armament, `R1158`) and FB Mk XVIII armament (`R1115`); PBY-5A (`R1153`); Warwick ASR Mk I (`R1154`); Albemarle ST Mk I (`R1155`). Added without figures (the family page specifies another mark, which was not copied): P-51C, P-51K, P-47D-25, Wellington GR Mk XIV, Halifax GR.V / A.V / A.VII, Stirling Mk IV, Liberator GR Mk V / GR Mk VI / C Mk IX, Dakota III / IV, Catalina IIIA, plus the Catalina, Warwick and Albemarle family rows. Dakota III and IV are the RAF names of the C-47A and C-47B (the C-47 page says so).

**What is left** (roadmap 375): Fw 190G, other unseeded German night-fighter and reconnaissance types, Me 410 and Ju 188 sub-variants, remaining Coastal and Transport Command marks not listed above, the Fieseler and Arado liaison types, Polish and French distinct types (none flew a type of their own in the West in 1944-45: the Polish and French squadrons flew British and American types, and the post-war French production of the Fi 156 and the Ju 52 falls after the period), and stronger sources than Wikipedia for the figures that still rest only on Wikipedia (Jane's, Air Ministry pilot's notes, USAAF Standard Aircraft Characteristics).

### 9.3 How a unit links to its aircraft, and aircraft strength

A unit's equipment is a **dated fact**: groups converted often (the 366th flew P-47s throughout, but most fighter groups changed type once or twice). Three designs were weighed: (a) an `aircraft_type_id` column on `units`, which cannot carry dates; (b) an `aircraft_type_id` plus `as_of` pair on the claims table, a migration of all claim files and the build for one domain; (c) an `aircraft` object inside the existing `strength_json`, which already carries `as_of`, `basis`, `scope` and a source, and which the refit record (section 8, item 4) already uses the same way. **(c) was built.** The claim's `as_of` is the date the equipment or return applies to.

`strength_json.aircraft` = `{"on_hand": n, "serviceable": n, "by_type": {"AT004": {"on_hand": n, "serviceable": n}}}`.

- `on_hand` is the aircraft held (Luftwaffe *Iststärke* of the Quartermaster-General returns, USAAF aircraft assigned or possessed); `serviceable` those ready for operations (*einsatzbereit*, operational or in commission). These are the figures the standard Luftwaffe and USAAF returns give; every number is the source's own.
- `by_type` is keyed by a `type_id` of `aircraft_types` (the family row when the source gives no variant). A `by_type` row without counts records only the equipment link. A source may leave types unlisted, so the by_type counts may add up to **less** than the totals, never more; `serviceable` never exceeds `on_hand` (totals or by type).
- `scope` is required (what part the figures cover: a whole Geschwader, one Gruppe, a detachment); `basis` is `reported_actual` for a return and `authorized_organization` for an establishment (*Soll*) figure.
- Only a unit of domain air may carry it. Validator `check_aircraft_strength`; JSON schema extended with the `scope` dependency. Scenario 257. No claim yet carries aircraft figures: the first will come from the Normandy pass, with a source for each.

### 9.4 Operational and administrative chains

US air units are *assigned* to one command (administrative: supply, personnel, discipline) and *attached* to another (operational), and RAF units are administered by their own group or command while being operationally controlled elsewhere. The vocabulary already has the kinds: `assigned` (standing), `attached` and `operational_control` (active), `administrative_control`, `supporting` and `coordinating`. **No new relation value was added**: the use is fixed instead.

- Record the administrative parent as `assigned` when the source says assigned, or `administrative_control` when it says so; record the operational parent as `attached` or `operational_control`. Use the source's word.
- `command_relations.contradictory_overlaps` flags an overlap only between relations of the **same class** (`standing`, or the same other value) naming different higher units of one echelon, so `assigned` to one command with `attached` to another, or `administrative_control` with `operational_control`, are not conflicts; two overlapping `assigned` relations to different commands of one echelon, or two overlapping `operational_control` relations, still are. Scenario 258 tests all four.
- `who_controls.py` picks the operational chain from the active relations (else the standing ones) by rank, as before. For an air or naval unit (not in the main table) it reads `build/other_domains/command_relations.csv` and adds an **administrative chain** block (an `administrative_control` relation, or an `assigned` relation while another command holds the operational one); ground output is byte-for-byte what it was, because the fallback runs only when the main table has no row for the subject, and the grid compare shows 0 changed cells (9.7).
- `audit_temporal_relationships.py` still treats `administrative_control` without a sourced end as end-unknown; the pair is not an error there.

### 9.5 The 366th Fighter Group (the pilot's source, now stored)

The pilot could not store the XXIX TAC assignments for lack of an evidence claim. The same source (Wikipedia, 366th Fighter Group, after Maurer, `R896`) dates them, so five claims were added (`C9439` 1 October 1944, `C9440` 22 October, `C9441` 19 November, `C9442` 28 January 1945, `C9443` 11 April 1945; stations A-70, Asch Y-29 `PL4177`, Münster-Handorf Y-94 `PL4178`) and four relations: `CR1306` assigned to XXIX TAC (Provisional) 1-21 October 1944, `CR1307` assigned to IX TAC again 22 October 1944 - 27 January 1945, `CR1308` assigned to IX Fighter Command from 28 January 1945 (administrative), `CR1309` attached to XXIX TAC 28 January - 21 June 1945 (operational). `CR1298` (IX TAC from 5 May 1944) now ends 30 September 1944 (old value open_at_last_claim, new value 1944-09-30, reason: the dates are stored). New placeholders `US-TAC-029C` and `US-FTRCMD-009` (echelon `air_division`). Confidence 0.3 on the three assignment rows (the position is the station of the period, inferred) and 0.5 on the two station moves. Three warnings are new and expected: the claim that states a relation's end is dated the day after it.

### 9.6 Checks and conventions

Standing rule 25 (`docs/HANDOFF.md`) and `CONTRIBUTING.md` carry the conventions. Next free ids: claim `C9444`, place `PL4179`, reference `R1159`, relation `CR1310`, aircraft type `AT135`, ship class `SC201`, scenario 259.

### 9.7 Grid

The standard grid (50 dates, 18,590 answers) compared against the state of the branch before this pass (identical to main): result: 18,590 answers, 0 changed, 0 new keys (the grid asks about ground units; the air and naval units are not in it). `who_controls.py` now reads `build/other_domains/command_relations.csv` for air and naval subjects, which adds answers for those units only; none of them is in the grid's unit list, so the grid shows no new key.
