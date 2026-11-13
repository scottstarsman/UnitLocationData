# Air and naval pilot (branch `air-naval-pilot`, 13 November 2026)

Scott asked on 13 November 2026 for a small air and naval pilot before the data is opened up, to find out whether the data structures need changes. This note is the result. It is a proposal for Scott's approval; only the minimum needed to store the pilot rows was changed (section 3).

## 1. What was entered

34 real, cited claims (`C9405`-`C9438`), 18 units (13 active, 5 placeholders; two more placeholders were dropped, see 2.9), 17 places (`PL4160`-`PL4176`), 16 references (`R896`-`R911`), 11 command relations (`CR1292`-`CR1305`; `CR1296`, `CR1299` and `CR1300` were dropped for lack of evidence claims, see 2.9, so those three ids are unused), 1 lineage row (`UL020`), 2 conflict groups (`G126`, `G127`) and 1 claim-key exception.

| Part | Units | Claims |
|---|---|---|
| Luftwaffe | Luftflotte 3 (existing), II Jagdkorps, JG 26, II./JG 26, III./JG 26 | `C9405`-`C9415` (bases Chantilly, Flammersfeld, Cormeilles, Guyancourt, Villacoublay, Creil; D-Day strafing of Sword) |
| USAAF | 366th Fighter Group, 390th Fighter Squadron, IX TAC (placeholder) | `C9416`-`C9422` (RAF Thruxton, ALG A-1, A-41, A-70) |
| Naval | USS Texas, USS Satterlee, HMS Warspite, HMS Bedale / ORP Ślązak, 5. Torpedobootsflottille, task groups (placeholders) | `C9423`-`C9436` |
| Coastal artillery | Marine-Artillerie-Abteilung 260 (ground by function, see 4) | `C9437`-`C9438` |

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
5. No change to `schema/vocabularies.json`, the validator or the schema documents.

## 4. Open decision: Marine-Artillerie-Abteilung 260

A Kriegsmarine coastal artillery battalion fights on land. It was entered as `ground` (like flak, Scott 4 November 2026) with branch `Navy`, so it appears in the main outputs and in `who_controls` (new keys only). Flipping it to `naval` is one cell in `data/units.csv` and moves `C9437`, `C9438` and `CR1305` to `build/other_domains/`. Recommended: keep it ground (it holds ground positions, like the 2nd Marine Infantry Division).

## 5. Recommended next steps (for Scott's approval)

1. Decide the echelon convention (2.7) and add `echelon_rank` entries for the reserved values.
2. Add `base` to `location_represents` and `commissioning` and `sortie` to `event_type` (2.4, 2.6).
3. Add a rule and a place flag for sea positions (2.2, 2.3).
4. Allow a second same-day row when the place differs (2.5), or document the exception route.
5. Write the air and naval id conventions into `schema/README.md` (2.13).
6. Roadmap 375 keeps the leftovers (II Jagdkorps from August 1944 in Rochefort; the 366th's later stations; the 5. Jagddivision; RAF/RCAF and further ships).
