# Military symbol codes (SIDCs) for units: proposal (roadmap 410)

Status: proposal for Scott's approval, branch `symbol-codes-410` (from main `62e65fd7`), 23 November 2026. Nothing here changes `units.csv`, the claims or the build: this step adds only this page, the two mapping tables `data/sidc_function_map.csv` and `data/sidc_echelon_map.csv`, and the coverage report [`symbol_codes_coverage.md`](symbol_codes_coverage.md). The derivation script, the build output and the validator check come after approval.

## 1. Decisions already taken (Scott, 23 November 2026: "I agree with all of that. Please proceed")

- **Standard:** MIL-STD-2525D / NATO APP-6D 20-digit numeric SIDC (the same code serves both), with a later move to 2525E (only the version digits change for the codes used here; see question 15). Rendering target: the milsymbol JavaScript library.
- **Derived, not entered:** the code is a build output plus a check, never a column typed into `units.csv`.
- **Function from a mapping table:** unit-name keywords plus domain, echelon and ship type (section 4).
- **No-exact-symbol cases** handled as in section 6.
- **Affiliation follows the date** through the allegiance table (section 5).

## 2. The 20-digit SIDC and the values used

| digits | field | values used | source |
|---|---|---|---|
| 1-2 | Version | `10` (2525D / APP-6D base version) | JMSML Base.xml `VersionCode 10`; milsymbol reads 10-12 as edition D, 13-14 as E |
| 3 | Context | `0` Reality, always | JMSML Base.xml Contexts (0 Reality, 1 Exercise, 2 Simulation) |
| 4 | Standard identity | `3` Friend, `6` Hostile, `4` Neutral, `1` Unknown, from the allegiance table on the date (section 5) | JMSML Base.xml StandardIdentities (0 Pending, 1 Unknown, 2 Assumed Friend, 3 Friend, 4 Neutral, 5 Suspect/Joker, 6 Hostile/Faker) |
| 5-6 | Symbol set | `10` Land Unit (ground and air units), `30` Sea Surface (ships, naval formations), `35` Sea Subsurface (submarines, U-boat flotillas) | JMSML instance files `Land_Unit`, `Sea_Surface`, `Sea_Subsurface`. Symbol set `01` Air is for aircraft, not formations, so air units use the land fixed-wing aviation unit (Scott's decision) |
| 7 | Status | `0` Present (question 16 proposes `4` Present/Destroyed on a claim whose `destroyed` flag is true) | JMSML Base.xml Statuses (0 Present, 1 Planned/Anticipated, 2 Fully Capable, 3 Damaged, 4 Destroyed, 5 Full to Capacity) |
| 8 | HQ / Task Force / Dummy | `0` none; `2` Headquarters (top, territorial and naval command headquarters); `4` Task Force (Kampfgruppen, combat commands, named task forces); `6` Task Force Headquarters (not used yet) | JMSML Base.xml HQTFDummy (1 Feint/Dummy, 2 HQ, 3 Feint HQ, 4 TF, 5 Feint TF, 6 TF HQ, 7 Feint TF HQ) |
| 9-10 | Amplifier (echelon) | from `data/sidc_echelon_map.csv` (section 3); `00` for symbol sets 30 and 35 | JMSML Base.xml AmplifierGroups 1 and 2; milsymbol reads 11-26 as echelons |
| 11-16 | Entity / type / subtype | from `data/sidc_function_map.csv` (section 4) | JMSML instance files; milsymbol number-SIDC icon tables |
| 17-18 | Modifier 1 | from the function map, `00` when blank | as above |
| 19-20 | Modifier 2 | from the function map, `00` when blank | as above |

Examples (Allied viewpoint, 1 July 1944): 3rd Panzergrenadier Division `10061000211211020000` (hostile, land unit, division, infantry armored/mechanized); US 29th Infantry Division `10031000211211000000`; British XXX Corps `10031000221210000000` (combined arms); OKW `10061002261100000000` (C2 with the HQ staff, echelon Command); Kampfgruppe Peiper `10061004171210000000` (combined arms, Task Force); USS Arkansas `10033000001202010000` (battleship); U 1191 `10063500001101000002` (submarine, diesel-electric); No. 1 Squadron RAF `10031000161208000000` (fixed-wing aviation, squadron).

### Sources and verification

- **JMSML:** the Joint Military Symbology Markup Language instance files of MIL-STD-2525D (Esri, `github.com/Esri/joint-military-symbology-xml`, branch `dev`, latest commit `094e7647f0bd` of 19 September 2024): `instance/Base.xml`, `Land_Unit.xml`, `Sea_Surface.xml`, `Sea_Subsurface.xml`, read on 23 November 2026. Base.xml labels its version "No changes to APP-6(C)/2525D".
- **milsymbol:** `github.com/spatialillusions/milsymbol`, `master`, files `src/numbersidc/` (land unit, sea, subsurface icon tables and `metadata.js`), latest release v3.0.6 of 18 November 2026, read on 23 November 2026.
- Every entity and modifier code in the function map was looked up in both; the table is in the coverage report. All are present in both, with two remarks: `10` `000000` (Unspecified) has no milsymbol icon entry because it is the empty frame (used only by the fall-through rule, which maps no unit today); milsymbol names the icon part of the 2525D cruiser `120202` "CRUISER, GUIDED MISSILE" (to be checked visually at the code step, question 15).
- **Not verified:** the APP-6D document itself is not freely published, so the claim that each code means the same in APP-6D rests on the shared 2525D/APP-6D number-SIDC structure as milsymbol implements it, not on the APP-6D text. The 2525E equivalents (question 15) are not checked yet.

## 3. Echelon amplifier for all 21 echelon values (`data/sidc_echelon_map.csv`)

| echelon | amplifier | 2525D label | fit |
|---|---|---|---|
| army_group | 24 | Army Group/Front | exact |
| army | 23 | Army | exact |
| corps | 22 | Corps/MEF | exact (Volks-Artillerie-Korps overridden to 18, question 6) |
| division | 21 | Division | exact |
| brigade | 18 | Brigade | exact |
| regiment/battle_group | 17 | Regiment/Group | exact |
| battalion | 16 | Battalion/Squadron | exact |
| company | 15 | Company/Battery/Troop | exact (includes RAF Regiment squadrons) |
| other | 25 | Region/Theater | nearest (OKW overridden to 26 Command, fortress garrisons to 00 Unknown; question 8) |
| air_flight | 14 | Platoon/Detachment | nearest |
| air_squadron | 16 | Battalion/Squadron | nearest |
| air_group | 17 | Regiment/Group | nearest |
| air_wing | 18 | Brigade | nearest |
| air_division | 21 | Division | nearest |
| air_corps | 22 | Corps/MEF | nearest |
| air_force | 23 | Army | nearest |
| naval_unit | 00 | none | sea symbol sets have no echelon |
| naval_division | 00 | none | surface group symbol, no echelon |
| naval_squadron | 00 | none | as above |
| task_group | 00 | none | task force / group / unit entity |
| fleet | 00 | none | as above |

The air rows follow the level the data already records (the RAF wing is an `air_group`, the RAF group an `air_wing`, per the echelon vocabulary), so a RAF group draws as a brigade and a RAF wing as a regiment/group.

## 4. Function: the mapping table (`data/sidc_function_map.csv`)

One row per rule. Columns: `rule_id`; `kind` (`function` or `addon`); conditions `domain` (blank = any; a blank domain in `units.csv` counts as ground), `echelon`, `ship_type`, `name_pattern` (a case-insensitive regular expression searched in `unit_name`); outputs `symbol_set`, `entity`, `modifier1`, `modifier2`, `hq_tf_dummy`, `amplifier_override`; and `entity_label`, `case` (exact, nearest, no-exact, default, default-infantry, addon) and `note`.

How a unit is coded: the first `function` row (in file order) whose conditions all hold gives the symbol set, entity, modifiers, HQ digit and any echelon override; for land units the two `addon` rows then add modifier 2 Airborne (when still blank) and the Task Force digit. The order is: top headquarters; ships by `ship_type`; naval formations; air defense and V-1; air units (services, rescue, staging posts, naval aviation, reconnaissance, then the fixed-wing default); land units (fortresses, artillery, engineers, signals, antitank, assault guns, panzergrenadiers, airborne, Kampfgruppen and task forces, armour, reconnaissance, mountain, commandos, police, RAF Regiment, infantry, unnamed-arm formations, higher formations); and the unspecified fall-through.

Coverage (details and every default or ambiguous unit in the [coverage report](symbol_codes_coverage.md)): all 2,635 units are mapped and none falls through to the unspecified default. By kind: 694 exact, 188 nearest, 410 no-exact cases, 1,328 domain defaults (1,007 fixed-wing flying units, 321 naval formations; both are the intended symbols), 15 land units with no arm in their name drawn as infantry. Largest rules: fixed-wing default 1,007, naval-formation default 321, infantry 172, servicing units 165, mine sweepers 102, destroyers 92, combined-arms higher formations 81.

### Ships (symbol set 30, submarines 35)

| ship_type | entity | modifiers | fit |
|---|---|---|---|
| BB | 120201 Battleship | | exact |
| BC | 120201 Battleship | | nearest (no unit yet) |
| BM (monitor) | 120200 Surface Combatant, Line | | nearest |
| CA | 120202 Cruiser | m2 02 Heavy | exact |
| CL | 120202 Cruiser | m2 03 Light | exact |
| CV, CVL, CVE | 120100 Carrier | CVL m2 03 Light; CVE m1 04 Escort | exact / nearest (no unit yet) |
| DD | 120203 Destroyer | | exact |
| DE | 120203 Destroyer | m1 04 Escort | nearest (question 13) |
| PF | 120204 Frigate | | exact |
| CORV | 120205 Corvette | | exact |
| TB | 120203 Destroyer | m1 17 Torpedo | nearest (question 13) |
| PG | 120502 Patrol Ship, General | | nearest |
| CM | 120401 Mine Layer | | exact |
| AM | 120402 Mine Sweeper | | exact |
| AGC | 120301 Amphibious Command Ship | | exact |
| APA | 120300 Amphibious Warfare Ship | | nearest (question 13) |
| AV | 130100 Auxiliary Ship | | nearest (question 13) |
| SS | 35 / 110100 Submarine | m2 02 Diesel Electric, General | exact |

## 5. Affiliation (standard identity, digit 4) follows the date

Computed with the existing resolver, `scripts/allegiance.py` `Resolver.side(unit_id, date)`: a unit override in `data/unit_allegiance_overrides.csv` first, then the nation's row in `data/nation_allegiance.csv` (nationality name to code through `data/nationalities.csv`). The side becomes the standard identity from the chosen viewpoint (question 1):

| side on the date | Allied viewpoint (proposed default) | Axis viewpoint |
|---|---|---|
| Allied | 3 Friend | 6 Hostile |
| co-belligerent | 3 Friend (question 4) | 6 Hostile |
| Axis | 6 Hostile | 3 Friend |
| neutral, non-aligned-belligerent | 4 Neutral | 4 Neutral |
| no side (gap or unknown nation) | 1 Unknown | 1 Unknown |

Where it is computed (question 2): (a) per claim, on the claim's date, as a `sidc` column of `build/all_claims.csv` (and later missions); and (b) per unit per allegiance period, as a new `build/unit_symbols.csv` with one row per unit and side period (`unit_id`, `valid_from`, `valid_to`, `sidc`), because 2,139 of the 2,635 units (mostly air and naval) have no claims. The function digits (5-6, 9-20) do not depend on the date; only digit 4 (and digit 7 if question 16 is accepted) does. Italy's switch in 1943, Vichy (`VIC`, neutral) against Free France (`FR`, Allied) and the other changes in the allegiance table follow automatically.

Measured on today's claims (Allied viewpoint): 5,351 claims Friend, 4,140 Hostile, 0 Neutral, and 8 Unknown: German claims dated after 8 May 1945, where Germany's allegiance row ends (question 3). Seven German units therefore change identity over their claims: the fortresses Dunkirk, Lorient and Saint-Nazaire, XXV Corps, the 265th Infantry Division, the 6th Fallschirmjäger Division and Army Blumentritt. The four `Allied` (multinational) headquarters (SHAEF, AFHQ, AEAF, First Allied Airborne Army) have no allegiance row and resolve to no side (question 3).

## 6. Cases with no exact symbol

| case | proposed symbol | units |
|---|---|---|
| Kampfgruppen, combat commands, Task Force Butler | 121000 Combined Arms, Task Force digit 4, echelon from the data (17) | 29 (+ Task Force A and 1st Airborne Task Force keep their arm and get digit 4) |
| Fortress garrisons | 121100 Infantry, echelon 00 Unknown (recommended over 000000 Unspecified; question 7) | 4 |
| Top headquarters | 110000 Command and Control with the HQ digit 2; OKW echelon 26 Command; SHAEF, AFHQ, AEAF, USSTAF, OB West, OB Nordwest, Wehrmachtbefehlshaber Niederlande echelon 25 Region/Theater (question 8) | 8 |
| Territorial commands (Wehrkreis XI, the two Luftgau-Kommandos, Netherlands District) | 110000 C2 with the HQ digit 2, echelon from the data (22 corps; 25 for the District) | 4 |
| Higher land formations with no single arm (army groups, armies, corps, Armee-Abteilungen) | 121000 Combined Arms; panzer, parachute/airborne and mountain formations take their arm instead | 81 |
| Volks-Artillerie-Korps | 130300 Field Artillery, echelon 18 Brigade instead of the data's corps (question 6) | 12 |
| Flak-Regiment 155 (W) and its four battalions (V-1) | 130700 Missile (question 5) | 5 |
| Other Flak, Flak-Sturm, Fallschirm-Flak, ADGB, IX Air Defense Command | 130100 Air Defense | 25 |
| RAF Regiment squadrons | 121100 Infantry (all 41 are "airfield ground defence" squadrons; no source in the data says which were field and which LAA, so none is drawn as air defense; question 10) | 41 |
| Air units | 120800 Aviation Fixed Wing (reconnaissance, photographic, weather units 120801); naval aviation with modifier 1 Naval; echelon from the air rows of section 3 (question 9) | 1,073 |
| Air ground units | servicing echelons, sections, glider and parachute servicing units 161100 Maintenance with modifier 1 Aviation; Air Force Service Command 160000 Sustainment with modifier 1 Aviation; marine craft units 141800 Search and Rescue with modifier 1 Naval; forward staging posts 120200 Air Traffic Services/Airfield Operations (question 10) | 230 |
| Ships without an exact entity | see the ship table (BM, DE, TB, PG, APA, AV; question 13) | 56 |
| Naval formations | 121000 Navy Task Organization, no echelon; "Task Force", "Task Group", "Task Unit"/"Sweep Unit" in the name give 121002, 121003, 121004; flotillas by role take modifier 1: mine countermeasures 07 (Minensuch-, Räumboot-, minesweeping), torpedo 17 (S-boat, MTB, PT, MGB), escort 04 (Sicherung, Vorposten, escort groups), anti-submarine 03 (U-Bootsjagd); U-boat flotillas 35 / 110000 subsurface Military; naval command headquarters (Marinegruppenkommando West, Admirals, Seeverteidigung commands, Führer der Schnellboote/Unterseeboote, K-Stab) with the HQ digit 2 (question 14) | 449 |
| Commandos and 1st Special Service Force | 121100 Infantry with modifier 1 Ranger (question 18) | 3 |
| Polizei-Regiment Mönchengladbach | 141700 Security (question 18) | 1 |

## 7. What the code step will add (after approval)

- `scripts/sidc.py`: reads the two maps and the allegiance tables and computes the codes as above; `build.py` writes `build/unit_symbols.csv` and the `sidc` column of `build/all_claims.csv` (and `all_claims.json`, `claims.geojson`).
- A validator check: every map row's codes exist in a pinned code list (the entity and modifier table of the coverage report), every unit matches a rule, no unit falls through to GZ99 without a warning, every echelon value has an amplifier row, and the build output matches a fresh derivation.
- A schema entry for the two maps and documentation in `schema/README.md`.

## 8. Questions for Scott, with recommendations

1. **Viewpoint.** Which side is "friend"? Recommendation: store the Allied viewpoint (Allied blue, Axis red) and let a viewer swap digit 4 (3 and 6) for an Axis view; the swap is mechanical, so storing one viewpoint is enough.
2. **Where the code is stored.** Recommendation: both a per-claim `sidc` column (date of the claim) and `build/unit_symbols.csv` (one row per unit per allegiance period), because 2,139 units have no claims.
3. **No side on the date.** Eight German claims (fortresses Dunkirk, Lorient and Saint-Nazaire and four other units) fall after 8 May 1945, and the four multinational `Allied` headquarters have no allegiance row. Recommendation: (a) a claim after its nation's last allegiance row keeps the last side (these units surrendered after the general surrender came into force; no data row changes); (b) add one `nation_allegiance.csv` row `ALL, Allied, 1939-09-03, 1945-09-02` at the code step (a data change, annotated). Alternative: leave both Unknown (yellow frames).
4. **Co-belligerents** (Italy from October 1943, Romania, Bulgaria, Finland late in the war; no unit today). Recommendation: Friend (3), as `Resolver.camp` already folds them into the Allied camp; alternative Assumed Friend (2, dashed frame).
5. **Flak-Regiment 155 (W).** Recommendation: 130700 Missile (it launched V-1s); alternative 130100 Air Defense following its Flak name.
6. **Volks-Artillerie-Korps echelon.** Recommendation: amplifier 18 Brigade (a VAK was brigade-sized), keeping `corps` in the data; alternative 22 Corps as recorded.
7. **Fortress garrisons.** Recommendation: 121100 Infantry with echelon 00 Unknown; alternative 000000 Unspecified.
8. **Top headquarters.** Recommendation: 110000 C2 with the HQ digit; OKW 26 Command; the theater headquarters 25 Region/Theater; territorial commands from their echelon. Alternative: echelon blank (00) for all.
9. **Air units.** Recommendation: the echelon rows of section 3 as they stand, and no role modifier for bombers, fighters and transports (2525D's land modifiers have none that fits; 120801 only for reconnaissance). Alternative: modifier 2 "Attack" (54) for fighter-bomber and Schlacht units and "Utility" (56) for transport.
10. **Air ground units and the RAF Regiment.** Recommendation: as in section 6 (Maintenance + Aviation, SAR + Naval, Airfield Operations, RAF Regiment as infantry); a RAF Regiment squadron becomes air defense only when a source names it LAA.
11. **Units whose role changed on a date** (363rd Fighter Group and 380th-382nd Fighter Squadrons became reconnaissance in August-September 1944; the 155th Photographic Squadron was a night fighter squadron until 22 June 1944). Recommendation: one function per unit (reconnaissance, from the name) for now, and a roadmap item for a small dated override table if more such cases appear; alternative: add the dated override in the code step.
12. **Individual calls.** Recommendation: Armeegruppe Lüttwitz stays armour (like the panzer armies); Task Force A (1st Tank Destroyer Brigade) stays antitank with the Task Force digit; Führer-Begleit-Brigade gets a name rule for 121102 Infantry, Armored/Mechanized (its id token is `PG`) instead of the infantry default.
13. **Ships with no exact entity.** Recommendation: DE as Destroyer + Escort; TB (German Torpedoboot) as Destroyer + Torpedo; BM (monitor) as generic Line combatant; PG as Patrol Ship; APA as generic Amphibious Warfare Ship (alternative 120307 Landing Ship); AV as Auxiliary Ship (alternative 120100 Carrier).
14. **Naval formations.** Recommendation: as in section 6, including the role modifier 1 on flotillas, the subsurface symbol for U-boat flotillas and the HQ digit on naval command headquarters. Alternative: plain 121000 for every formation.
15. **Version and rendering.** Recommendation: version `10` (2525D) now; when moving to 2525E, change the version digits to `13` after checking every code in the map against the 2525E tables; check the cruiser icon (milsymbol's "CRUISER, GUIDED MISSILE") when rendering.
16. **Status digit.** Recommendation: `0` Present, and `4` Present/Destroyed on a claim whose `destroyed` flag is true (per claim only); placeholders stay `0`. Alternative: always `0`.
17. **Kampfgruppen, combat commands and higher formations.** Recommendation: 121000 Combined Arms with the Task Force digit for Kampfgruppen, combat commands and named task forces, and plain 121000 for army groups, armies and corps with no arm in the name. Alternative: infantry for generic corps and armies.
18. **Commandos and police.** Recommendation: commando brigades and 1st Special Service Force as Infantry + Ranger (alternative 121800 SOF or 121700 Special Forces); Polizei-Regiment as Security (alternative 141200 Military Police).
19. **File location and names.** Recommendation: the two maps stay in `data/` next to the other reference tables, with a schema entry in the code step.
