# Schema reference

The machine-readable definitions live next to this file and are what `scripts/validate.py` enforces:

- [`claims.schema.json`](claims.schema.json): column order, types and constraints of every file under `data/claims/` (Frictionless Table Schema style; `vocabulary` is a custom property pointing at a key in `vocabularies.json`).
- [`units.schema.json`](units.schema.json): the same for `data/units.csv`.
- [`vocabularies.json`](vocabularies.json): controlled vocabularies and the confidence rubric.

All CSV files are UTF-8, LF line endings, comma separated, with a header row, minimal quoting (fields with commas, quotes or newlines are quoted). Missing values are empty strings. Dates are `YYYY-MM-DD`. Booleans are lowercase `true`/`false`. Coordinates are decimal degrees (WGS84). The column order is the same in every claim file; `theater` follows `date`.

When you change a column or vocabulary, edit the JSON files and this page together.

## claims columns (`data/claims/<nationality>/<unit_id>.csv`, `build/all_claims.csv`)

| column | type | required | meaning | constraints |
|---|---|---|---|---|
| `claim_id` | string | yes | Unique id of the claim, C0001 onward. One row is one claim ("this unit was here on this date"). Never reused. | pattern `^C\d{4,}$` |
| `conflict_group_id` | string | no | Shared by rows that make competing claims about the same unit and event (G001...). Blank if no known conflict. | pattern `^G\d{3,}$` |
| `claim_status` | string | yes | preferred, alternate or disputed (see vocabulary). | vocabulary `claim_status` |
| `unit_id` | string | yes | Stable unit key, NATION-TYPE-NUMBER+ECHELONLETTER (for example US-INF-029D). Must exist in data/units.csv and match the file name. | pattern `^[A-Z]{2,4}(-[A-Z0-9]+)+$` |
| `date` | date | yes | Date of the claim, YYYY-MM-DD. |  |
| `theater` | string | yes | Primary theater of the claim (see vocabulary). | vocabulary `theater` |
| `nationality` | string | yes | Nationality of the unit: US, UK, Canada, Germany (extend as needed). Matches the data/claims/<nationality>/ folder in lowercase. | vocabulary `nationality` |
| `unit_name` | string | yes | Unit name only, for example "29th Infantry Division". |  |
| `echelon` | string | yes | Organisational level (see vocabulary). | vocabulary `echelon` |
| `branch` | string | yes | Service or arm (see vocabulary). | vocabulary `branch` |
| `parent_unit_id` | string | no | Unit id (from `data/units.csv`) of the operational parent on that row's date: the formation the unit was attached to or operating under, otherwise its standing parent. Blank if the unit has no parent (top-level headquarters); `unknown` if not verified. The organic parent, when different, is in `command_relationships`. | pattern `^([A-Z]{2,4}(-[A-Z0-9]+)+\|unknown)$` |
| `command_relationships` | string (JSON) | no | JSON list of command relationships on that date, see [command_relationships](#command_relationships). `unknown` (plain text, not JSON) or blank if nothing is known. | valid JSON list, or `unknown` |
| `commander` | string | yes | Commander on that date, rank and name as given by sources; "unknown" if not verified. |  |
| `latitude` | number | yes | Decimal degrees WGS84. | -90 to 90 |
| `longitude` | number | yes | Decimal degrees WGS84. | -180 to 180 |
| `location_name` | string | yes | Name of the place the coordinate refers to. |  |
| `location_represents` | string | yes | What the point stands for (see vocabulary). | vocabulary `location_represents` |
| `precision_km` | number | yes | Judgment estimate of the radius in km within which the unit probably was (banded). | vocabulary `precision_km` |
| `operation_name` | string | yes | Parent operation, for example Overlord. |  |
| `sub_operation_name` | string | no | Sub-operation(s), semicolon-separated (Neptune, Epsom, Perch, ...). Blank for plain parent-operation rows. |  |
| `composing_units` | string | no | Subordinate units, listed when first given or when they change; blank means unchanged from the unit's previous row; "unknown" means no data. |  |
| `established` | boolean | yes | True on the row where the source says the unit was formed. | `true`/`false` |
| `disestablished` | boolean | yes | True on the row where the source says the unit was disbanded. | `true`/`false` |
| `destroyed` | boolean | yes | True on the row where the source says the unit was destroyed. | `true`/`false` |
| `confidence` | number | yes | Numeric 0-1 confidence by rubric (see vocabulary). | vocabulary `confidence`; 0 to 1 |
| `source` | string | yes | URLs separated by " \| " ending with the coordinate source note. Every row needs at least one URL. |  |
| `event_type` | string | yes | One primary event type (see vocabulary). | vocabulary `event_type` |
| `current_activity` | string | yes | Short phrase saying what the unit is doing on that date at that place; lower-case, free text. |  |
| `engaged_with` | string | no | Enemy units fought on that date, nationality first, separated by "; ". Blank = no combat that day; "unknown" = combat with no opponent identified. |  |
| `strength_status` | string | yes | Qualitative strength (see vocabulary). | vocabulary `strength_status` |
| `strength_json` | string | no | Optional JSON object with sourced strength figures: {"basis","as_of","personnel","vehicles","vehicle_count_type","source","note"}. See docs/methodology.md. Blank where no source gives figures. |  |
| `notes` | string | yes | Free text: what the source says, caveats, source conflicts, change history. |  |
| `location_date` | date | no | Optional. The date the coordinate is actually documented for, when it differs from `date` (for example the date of the command post list the point was taken from). Blank where the coordinate is for the claim's own date or the date is unknown (older rows not yet reviewed). | valid date |
| `location_basis` | string | no | Optional. How the coordinate relates in time and place to `date` (see vocabulary `location_basis`). Blank on rows not yet reviewed. | vocabulary `location_basis` |
| `location_temporal_offset_days` | number | no | Optional integer: `location_date` minus `date` in days (positive = the coordinate is from a later date). Blank when `location_date` is blank. | pattern `^-?\d+$`; must equal `location_date - date` |

Primary key: `claim_id` (unique across the whole repository). Rows in each file are sorted by `date`, then `claim_id`.

## units columns (`data/units.csv`)

| column | type | required | meaning | constraints |
|---|---|---|---|---|
| `unit_id` | string | yes | Stable unit key. Primary key. | pattern `^[A-Z]{2,4}(-[A-Z0-9]+)+$` |
| `unit_name` | string | yes | Unit name only. |  |
| `nationality` | string | yes | Nationality (US, UK, Canada, Germany, Poland, France, Belgium, Netherlands, Czechoslovakia, Allied ...). | vocabulary `nationality` |
| `echelon` | string | yes | Organisational level (see vocabulary). | vocabulary `echelon` |
| `branch` | string | yes | Service or arm (see vocabulary). | vocabulary `branch` |
| `theater` | string | yes | Primary theater of the unit (single value; claim rows carry their own theater). | vocabulary `theater` |
| `parent_unit_id` | string | no | Fixed organic parent unit, used for battle groups and combat commands (their parent division). Blank for units whose parent changes with time; use the claim columns `parent_unit_id` and `command_relationships` for time-dependent parents. | pattern `^[A-Z]{2,4}(-[A-Z0-9]+)+$` |
| `parent_only` | boolean | yes | true if the unit has no claim rows of its own (it exists only so that other rows can point to it, or it is a placeholder); false if data/claims/<nationality>/<unit_id>.csv exists. True exactly when `record_status` is `placeholder`. | `true`/`false` |
| `record_status` | string | yes | `placeholder` (identity only, no claim file; not a claim about location), `partial` (claim file known to be incomplete) or `active` (claim file exists). | vocabulary `record_status` |
| `formed_date` | string | no | Formation or activation date of the unit, or of the designation the record uses (see `unit_note`), as given by `formed_date_source`: `YYYY-MM-DD`, `YYYY-MM` or `YYYY`; blank if unknown. It is not the date the unit arrived in the theater. | pattern `^[0-9]{4}(-[0-9]{2}(-[0-9]{2})?)?$`; must be a real date |
| `formed_date_source` | string | no | URL of the page that gives `formed_date`. Required when `formed_date` is set. | URL |
| `initial_parent_unit_id` | string | no | Placeholder-level hint: the formation the unit is listed under in `initial_parent_source` as of `initial_parent_as_of`. Blank where no source clearly gives it. Not an organic-versus-attached statement and not a claim: time-dependent parents of claim rows go in the claim columns `parent_unit_id` and `command_relationships`. Different from `parent_unit_id` (fixed organic parent of battle groups). | pattern `^[A-Z]{2,4}(-[A-Z0-9]+)+$`; must resolve |
| `initial_parent_as_of` | string | no | Date the listing applies to, `YYYY-MM-DD` or `YYYY-MM` (for example `1944-06-06` for the German 6 June 1944 order of battle). Set together with the two other `initial_parent_*` columns or not at all. | real date |
| `initial_parent_source` | string | no | Source token for the listing. | vocabulary `source_token` |
| `component_of_note` | string | no | Free text on the placeholder parent link, for example why it is blank or that the source lists the unit under two formations. |  |
| `unit_note` | string | no | Free text on the unit's identity: renames, reconstitutions, lineage caveats, uncertain Western Front service. |  |
| `listing_source` | string | no | Semicolon-separated source tokens naming where the unit was found when the placeholder was created. A listing is not evidence of a date or place. | tokens from vocabulary `source_token` |

Rows are sorted by `unit_id`. `parent_only = true` units (`record_status = placeholder`) have no claim file; they exist so that `parent_unit_id`, `command_relationships` and `engaged_with` names resolve and so that coverage can be tracked (see "Placeholder units" in `docs/methodology.md`). A placeholder is not a claim about where the unit was. When a claim file is added for a placeholder, run `python scripts/promote_placeholders.py` (sets `record_status = active` and `parent_only = false`). `scripts/validate.py` checks every parent id against `units.csv`, that `record_status` agrees with `parent_only` and the existence of a claim file, that `formed_date` is a real date with a source URL, and that `unit_name` is unique within a nationality. `python scripts/build.py` writes `build/coverage.csv` and `docs/coverage.md`.

## unit_id pattern

`NATION-TYPE-NUMBER+ECHELONLETTER`, all upper case.

- Nation: `US`, `UK`, `CAN`, `GER`, `POL`, `FR`, `BEL`, `NL`, `CZ`, `ALL` (combined Allied headquarters such as SHAEF).
- Type: `INF`, `ARM`, `ABN` (airborne), `TNK` (tank brigade), `PZ` (panzer), `SSPZ` (SS panzer), `SSPG` (SS panzergrenadier), `FJ` (Fallschirmjaeger, also Fallschirmjaeger corps), `LL` (Luftlande), `COR`, `ARMY`, `AG`, `PZG` (panzer group), `OBW` (OB West), `OKW`, `SHAEF`; placeholder additions: `VG` (Volksgrenadier division), `PG` (panzergrenadier), `SSGEB` (SS mountain), `SSGR` (SS grenadier), `LFD` (Luftwaffe field division), `RES` (reserve division), `DIV` (numbered or z.b.V. division), `PZB` (Panzer-Brigade), `PZA` (panzer army), `FJA` (parachute army), `AA` (Armee-Abteilung), `PZ`/`SSCOR`/`LFC` for panzer, SS and Luftwaffe field corps, `VAK` (Volks-Artillerie-Korps), `OBNW`/`WBN` (other HQs), `CDO` (commando brigade).
- Echelon letter: `G` army group, `A` army, `C` corps, `D` division, `B` brigade, `H` other HQ.
- Examples: `US-INF-029D`, `GER-PZ-021D`, `UK-ARM-011D`, `CAN-INF-003D`, `GER-SSPZ-001C` (I SS Panzer Corps), `GER-SSPZ-001D` (1st SS Panzer Division).
- Units without a number use a word: `GER-PZ-LEHRD` (Panzer Lehr), `UK-ARM-GRDD` (Guards Armoured), `GER-PZG-WESTA` (Panzer Group West), `GER-AG-00BG` (Army Group B).
- Battle groups and combat commands: `GER-KG-<NAME>` for a Kampfgruppe (for example `GER-KG-FREY`; unnamed ones use a number or parent code, for example `GER-KG-265`, `GER-KG-002PZ`) and `US-CCA-002D` for Combat Command A of the 2nd Armored Division. Their `echelon` is `regiment/battle_group` and the units.csv `parent_unit_id` points at the parent division (the organic parent).
- The id is the same on every row of the unit and equals the claim file name.

## Free-text conventions

- `composing_units`: listed when first given or when it changes; blank means unchanged from that unit's previous row; `unknown` means no data. Items are separated by `; `.
- `engaged_with`: enemy units, nationality first, separated by `; ` (for example `German 352nd Infantry Division; German 716th Static Infantry Division`). Blank = no combat that day; `unknown` = combat with no opponent identified.
- `commander`: rank and name as given by the sources; command changes are written like `X (killed 12 June); Y from that evening`.
- `source`: URLs separated by ` | `, ending with a coordinate source note after ` ; ` (for example `; coords: Wikipedia`).
- `sub_operation_name`: semicolon-separated if several (`Martlet; Epsom`).
- `current_activity`: short lower-case phrase (about 120 characters at most), no trailing period; free text, not a vocabulary. Describe the one action the sources document on that date at that place, in the sources' own terms (who did what, where). Do not state a direction, aim or result the sources do not give (for example "attacking from the bridgehead" when the source says the attack was postponed or contained), and do not join several actions with `;`: use `notes` for the rest. `scripts/validate.py` warns on long or hedged activities.

## command_relationships

A JSON list written on one line (CSV-quoted like `strength_json`), or the plain text `unknown`, or blank. Each element:

```json
[{"unit_id":"GER-SSPZ-002D","name":"German 2nd SS Panzer Division Das Reich","relationship":"assigned"},{"unit_id":"GER-PZ-LEHRD","name":"German Panzer Lehr Division","relationship":"attached","note":"Placed under Panzer Lehr on arrival"}]
```

Keys: `unit_id` (required; a unit id from `data/units.csv`; `null` only for a formation that is not a unit, such as the placeholder "standing parent not identified"), `name` (required), `relationship` (required, see the `relationship` vocabulary below), `effective_from` and `effective_to` (optional dates `YYYY-MM-DD`: the first and last day the relationship held, when a source gives them; an entry that takes effect after the row's date, or ended before it, draws a validator warning), `date_basis` (optional: `order`, `assignment_table`, `narrative` or `inferred`, see the `relationship_date_basis` vocabulary: where the dates come from; a table date may differ from the day command actually passed) and `note` (optional string). No other keys.

`parent_unit_id` is the **operational parent on the row's date**: the formation the unit was attached to or operating under that day, otherwise its standing parent. It must also appear in the list. The **standing parent is recorded only here**, as an `organic`, `assigned` or `unspecified_subordination` entry: when an `attached` or `operational_control` entry exists, `parent_unit_id` must be that entry and the standing parent stays in the list (an independent brigade attached to a division for an assault is `attached` to the division and `assigned` to the army or corps that holds it). If the standing parent is not known, say so with an entry of relationship `unknown`. An entry never describes a relationship that only started on a later date: use `effective_from` and let the row's date decide which entries apply. For a battle group, the `parent_unit_id` in `data/units.csv` must be listed here as `organic`. Add a formation to `data/units.csv` (as a `parent_only` unit if it has no claims) rather than using `null`: the validator warns about a named higher headquarters without a unit id.

How to choose the value (the full definitions are in the table below):

- `organic` is only for a constituted component: a regiment or battle group of its own division, a battalion of its own regiment. A division, corps or army under a higher headquarters is never `organic`; the validator warns when it is.
- `assigned` when the source says assigned, or names the unit as a standing member of the headquarters' order of battle without attachment language. Army to army group and corps to army links from narrative histories are normally `assigned`.
- `attached` only where the source says attached or shows a temporary tasking.
- `unspecified_subordination` when the source shows the subordination but does not distinguish assigned from attached, for example the CMH ETO-OB assignment tables, whose columns are combined. Never convert it to `assigned` or `attached` without a source.
- `operational_control`, `administrative_control`, `supporting` and `coordinating` describe a different kind of authority and can sit beside a standing entry (for example SHAEF with operational control and AFHQ with administrative control over 6th Army Group on 15 September 1944; 21st Army Group coordinating 12th Army Group until 31 August 1944).
- Entries written before 25 October 2026 used `organic` for every standing parent; they were converted by the Batch 1 review (`review_changes.md`, "Systemic changes"): table-derived links became `unspecified_subordination`, other formation-to-higher-HQ links became `assigned`.

A row has one entry per higher headquarters. When the kind of authority changes during the row's period (for example 21st Army Group's coordination ending on 31 August), use `effective_to` and say so in the `note`; put the change history in `notes`.

## Location provenance: location_date, location_basis, location_temporal_offset_days

`latitude`/`longitude` answer "where", `date` answers "when". Many Batch 1 coordinates are command posts that a source lists on a different date from the claim, or town centres standing for a headquarters. Three optional columns record that:

- `location_date`: the date the coordinate is documented for. Set it equal to `date` when a source places the unit there on the claim's date.
- `location_temporal_offset_days`: `location_date - date` in days (the validator checks it).
- `location_basis`: one value of the `location_basis` vocabulary below. Temporal bases come first: if the coordinate is from another date use `nearest_later_command_post` or `nearest_earlier_command_post`; otherwise say whether the point is a `town_centroid` (a named town standing for a headquarters whose site is not given), a `representative_point`, an `operational_area` point (sector, landing area, bridgehead), `documented_on_date` (a named site or event place for that date), or `inferred`.
- There is no separate location confidence column: `confidence`, `precision_km` and the basis together say how far the coordinate can be trusted. A coordinate from another date or a town centroid should carry a wider `precision_km` and, where the row's own date is not documented, `confidence` 0.5 or 0.3. Older rows (before Batch 1) are left blank unless their notes say where the coordinate came from.

Validator checks: error when `location_date` and the offset disagree, when the offset is set without a date, when a temporal basis has no date, and for a `landing` row whose coordinate is a `town_centroid` or a command post from another date; warning when `location_date` differs from `date` but the basis is blank or `documented_on_date`, when a corps, army or army-group headquarters is only a town centroid with `precision_km` under 5, and when a corps or army sector is recorded as an exact `front_line_point`. `python scripts/audit_command_location.py` lists the counts per pattern.

### Notes convention

Use short labelled sentences in `notes` so the sources for each kind of statement stay separate: `Event date:` (the source for the date), `Event definition:` (what event this row means, needed when rows in a conflict group differ in event type or definition, for example a landing against an arrival), `Relationship:` (the source for the command relationship), `Location:` (what the point stands for and which source places it), `Coordinates:` (how the numbers were obtained). Not every row needs all labels; the reviewed Batch 1 rows use them.

## strength_json

A JSON object (blank if no source gives figures):

```json
{"basis":"reported_actual","as_of":"1944-06-16","vehicles":{"tanks":85},"vehicle_count_type":"operational","source":"Wikipedia Operation Perch","note":"optional caveat"}
```

Keys: `basis` (required), `as_of` (required, `YYYY-MM-DD`, may differ from the row date), `personnel` (integer), `vehicles` (object name -> integer count), `vehicle_count_type` (required when `vehicles` is present), `scope` (`whole_unit`, `sub_force` or `sector`, see the `strength_json_scope` vocabulary; required whenever `personnel` is given, and the validator reports an error when it is missing; if no source says what a figure covers, leave the figure out), `source` (required), `note` (optional). A figure that a source gives for a task force, a line or a sector (for example "for the defense of the new line he had 2,500 men") is not the strength of the whole unit: mark it `sub_force` or `sector` and say so in `note`. At least one of `personnel` or `vehicles` must be present. Guns are not vehicles. Details and basis rules: [../docs/methodology.md](../docs/methodology.md).

## Vocabularies

### theater

Primary theater of operations the claim belongs to. One value per claim row; a unit's primary theater is recorded once in data/units.csv.

| value | meaning |
|---|---|
| `western_europe` | Northwest Europe and France, from the Normandy landings through the end of the war in the West (also Netherlands, Belgium, Luxembourg, Germany west of the Elbe), and southern France from the Dragoon landings (15 August 1944) on, because the project's Western Front scope includes the Riviera-to-Rhine campaign. |
| `mediterranean` | Italy, Sicily, the Balkans and Greece, and the Mediterranean Sea (southern France only before the Dragoon landing, for example staging in Italy or Corsica; from 15 August 1944 southern France is western_europe). |
| `north_africa` | Libya, Egypt, Tunisia, Algeria and Morocco campaigns (1940-1943). |
| `eastern_front` | Germany/Axis versus the USSR (Soviet Union, Poland, Baltic, Romania, Hungary, Finland). |
| `pacific` | Pacific Ocean areas and Southwest Pacific, including Japan, the Philippines and the Dutch East Indies. |
| `cbi` | China-Burma-India theater (China, Burma, India, Indochina). |
| `atlantic` | Atlantic Ocean, Arctic convoys and other naval or air units whose operations are mainly at sea. |
| `other` | Anything that does not fit above (for example East Africa, Middle East, home-front units). Explain in notes. |

### nationality

Nation of the unit. The lowercase value is the folder name under data/claims/. Add a nation here before adding its first unit. Further nations (Italy, USSR, Japan, ...) are added when their theaters are started.

| value | meaning |
|---|---|
| `US` | United States (folder us). |
| `UK` | United Kingdom and Commonwealth formations serving in British armies except those with their own entry (folder uk). |
| `Canada` | Canada (folder canada). |
| `Germany` | Germany, including Waffen-SS and Luftwaffe ground formations (folder germany). |
| `Allied` | Combined Allied headquarters that belong to no single nation, for example SHAEF (folder allied; no claim files yet, only placeholder or parent_only units). |
| `Poland` | Poland: Polish formations serving under British or Allied command (folder poland). |
| `France` | France: Free French and French Army formations (folder france). |
| `Belgium` | Belgium: Belgian formations (folder belgium). |
| `Netherlands` | Netherlands: Dutch formations (folder netherlands). |
| `Czechoslovakia` | Czechoslovakia: Czechoslovak formations (folder czechoslovakia). |

### relationship

Meaning of the `relationship` field in each object of `command_relationships`.

| value | meaning |
|---|---|
| `organic` | A constituted component of the formation: its own regiments, battalions or battle groups, or a unit that is part of the parent's table of organisation. Do not use for a division, corps or army that is assigned to a higher headquarters (use assigned or unspecified_subordination). |
| `assigned` | The unit was assigned to this formation: the source says 'assigned', or names the unit as a standing member of the headquarters' order of battle for a period not described as temporary, with no attachment language. Includes army to army group and corps to army. |
| `attached` | The unit was attached to this formation (a temporary or task-organised subordination) on the row's date; use only where the source says attached or shows a temporary tasking. |
| `unspecified_subordination` | The source shows the unit subordinate to this formation on the date but does not distinguish assigned from attached (for example the CMH ETO-OB assignment tables, whose columns are combined). Never convert to attached or assigned without a source. |
| `operational_control` | This formation exercised operational (tactical) control over the unit, whether or not the unit was one of its assigned or attached components. |
| `administrative_control` | This formation held administrative, supply or personnel responsibility for the unit while another formation had operational control. |
| `supporting` | The unit was in direct support of this formation without being part of it. |
| `coordinating` | This formation coordinated the unit's operations with others without commanding it (for example 21st Army Group's coordination of both army groups until 1 September 1944). |
| `reserve` | The unit was held in this formation's (or the high command's) reserve. |
| `unknown` | A formation is named by the source but how it relates to the unit is not stated. |

### relationship_date_basis

Where the `effective_from` / `effective_to` dates of a command relationship come from (`date_basis` key).

| value | meaning |
|---|---|
| `order` | A named order or message gives the date. |
| `assignment_table` | A dated assignment table such as CMH ETO-OB. The table date may differ from the day command actually passed. |
| `narrative` | A narrative history or reference work states the date. |
| `inferred` | The date is inferred from other rows; treat as approximate. |

### location_basis

How the coordinate relates in time and place to the claim's date (`location_basis` column).

| value | meaning |
|---|---|
| `documented_on_date` | A source places the unit, event or headquarters at this location on the claim's date. |
| `nearest_later_command_post` | The coordinate is the nearest command post listed after the claim's date; the position on the date itself is not documented. |
| `nearest_earlier_command_post` | The coordinate is the nearest command post listed before the claim's date; the position on the date itself is not documented. |
| `representative_point` | A point chosen to stand for an area or front (not a documented position). |
| `town_centroid` | The coordinate is the centre of a named town or commune; the source does not locate the headquarters or event more precisely. |
| `operational_area` | A point inside the area of operations (sector, landing area, bridgehead) rather than a headquarters or exact position. |
| `inferred` | Inferred from the unit's movements or other rows rather than stated. |

### claim_status

How a row relates to competing claims. Rows with a conflict_group_id must use preferred, alternate or disputed as below; rows with no conflict are always preferred.

| value | meaning |
|---|---|
| `preferred` | A non-conflicted claim, or the best-supported claim in a conflict group. |
| `alternate` | A competing claim judged less likely than the preferred one in the same conflict group. |
| `disputed` | One of several competing claims where no source is judged better; a group with no preferred row has all rows disputed. |

### echelon

Organisational level of the unit.

| value | meaning |
|---|---|
| `army_group` | Army group or equivalent theater command (for example 21st Army Group, Army Group B). |
| `army` | Army or panzer group. |
| `corps` | Corps. |
| `division` | Division. |
| `brigade` | Independent brigade. |
| `regiment/battle_group` | Regiment-sized or smaller ad hoc formation such as a Kampfgruppe or an Allied combat command. |
| `other` | Higher or special headquarters that fit no level above (for example OB West). |
| `air_force` | Reserved for later: air force, air fleet or air army headquarters (not yet used). |
| `air_formation` | Reserved for later: air corps, air division, wing, group or squadron (not yet used). |
| `fleet` | Reserved for later: naval fleet, task force or flotilla headquarters (not yet used). |
| `naval_unit` | Reserved for later: ship, squadron or other naval unit (not yet used). |

### branch

Service or arm, assigned from the unit name.

| value | meaning |
|---|---|
| `Army` | Regular army (including infantry and static divisions). |
| `Armoured` | Armoured and panzer formations. |
| `Airborne` | Allied airborne formations. |
| `Waffen-SS` | Waffen-SS formations. |
| `Luftwaffe` | Luftwaffe ground formations (for example Fallschirmjaeger and Luftwaffe field divisions); also reserved for Luftwaffe flying units. |
| `Marines` | Marine ground formations (reserved; none served on the Western Front 1944-45). |
| `Air Force` | Reserved for later: air forces (RAF, USAAF, Luftwaffe flying units). |
| `Navy` | Reserved for later: naval forces. |

### location_represents

What the latitude/longitude stands for.

| value | meaning |
|---|---|
| `headquarters` | The unit's headquarters. |
| `main_body` | Where the main body of the unit was. |
| `sector_center` | The centre of the sector or landing zone the unit held or used. |
| `front_line_point` | A representative point on the unit's front line or point of contact. |
| `objective` | The place the unit captured, attacked or defended. |
| `approach_route` | A point on the unit's march or approach route. |

### precision_km

Judgment estimate, in kilometres, of the radius within which the unit (or its main body) probably was. Not a surveyed error. Banded values.

| value | meaning |
|---|---|
| `1` | Exact named place tied to the date; division or smaller. |
| `3` | Village-scale point; manual override used once in the proof of concept (C0034). |
| `5` | Named town or village, approximate; or exact for corps and above. |
| `10` | Sector or beach centre (beaches are 8-10 km wide), or inferred for division or smaller. |
| `25` | Inferred for corps, or approximate for army and above; approach routes within one region. |
| `50` | Inferred for army and above, or long approach routes (for example a move from Brittany). |

### confidence

Numeric 0-1 score applied by rule from location quality and source families. Only these four levels are used.

| value | meaning |
|---|---|
| `0.9` | Exact location and two independent source families agree (Wikipedia, CMH/HyperWar and each other domain count as separate families; several Wikipedia pages count as one). |
| `0.7` | Exact location with one authoritative source (for example the US Army CMH); or approximate location with two source families. |
| `0.5` | Exact location with one secondary source (Wikipedia, local-history page); or approximate location with one source family. |
| `0.3` | Position inferred or a representative point (HQ not tied to the date, unverified beach, front-line representative point), or the date itself is approximate. |

- Caps for conflicts: the preferred row of a conflict group is at most 0.7; alternate and disputed rows are at most 0.5.

- A manual override is allowed when the date itself is approximate (use 0.3) and must be explained in notes.

### event_type

One primary event per row.

| value | meaning |
|---|---|
| `landing` | Seaborne or airborne landing, including D-Day assault landings. |
| `arrival` | Reaching the front or the beachhead after the landing phase. |
| `attack` | Offensive action. |
| `defense` | Defensive action. |
| `counterattack` | Counterattack. |
| `relocation` | March or move. |
| `withdrawal` | Withdrawal or retreat. |
| `surrender` | Surrender. |
| `capture` | Taking a named place or position. |
| `destruction` | Unit destroyed. |
| `command_change` | Commander or command responsibility changes. |
| `hq_move` | Headquarters moves. |
| `regroup` | Assembly, reorganisation, relief in place. |
| `activation` | A formation becomes operational, or is activated or constituted as a headquarters or unit (for example 12th Army Group becoming operational on 1 August 1944). |
| `redesignation` | The same formation takes a new designation (identity continues; for example XVIII Corps becoming XVIII Airborne Corps). |
| `other` | Headquarters decisions, air attack on a headquarters, units at their station. |

### strength_status

Qualitative strength. Default unknown; set only when a source states strength or losses.

| value | meaning |
|---|---|
| `full` | A source describes the unit as at full strength. |
| `reduced` | Source states significant losses or reduced combat power. |
| `heavily_depleted` | Source states the unit was a small fraction of its strength. |
| `destroyed` | Unit destroyed or ceased to exist as a fighting formation. |
| `unknown` | No source states the strength. |

### strength_json_basis

Meaning of the basis field inside strength_json.

| value | meaning |
|---|---|
| `reported_actual` | A unit report or operational count relayed by the source (for example working-order tank returns). |
| `authorized_organization` | Establishment or table-of-organisation strength, not an actual count. |
| `estimate` | Rounded, approximate or retrospective figure, or a landing tally. |

### strength_json_vehicle_count_type

What the numbers in strength_json.vehicles mean.

| value | meaning |
|---|---|
| `operational` | Vehicles in working order. |
| `on_hand` | Vehicles on hand, working order not stated. |
| `unknown` | The source does not say what the count means (for example vehicles committed in one action). |

### strength_json_scope

What part of the unit the figures in strength_json describe. Required whenever personnel is given (the validator reports an error if it is missing).

| value | meaning |
|---|---|
| `whole_unit` | The figure covers the whole unit (division, brigade, ...) as the source states it. |
| `sub_force` | The figure covers only part of the unit: a battle group, a detachment or the force available for one task or line. |
| `sector` | The figure covers the forces in a sector or area that is not the unit's own organisation (for example the defenders of a line or beach, or all the forces landed on a beach). |

### boolean

Boolean fields (established, disestablished, destroyed, parent_only) use lowercase text.

| value | meaning |
|---|---|
| `true` | True. |
| `false` | False. |

### record_status

Research state of a unit record in data/units.csv.

| value | meaning |
|---|---|
| `placeholder` | Identity only: the unit exists in the table so that other records can point to it. No claim file; parent_only is true. Not a claim about its location. |
| `partial` | A claim file exists but coverage is known to be incomplete (for example only some operations are done). parent_only is false. |
| `active` | A claim file exists. parent_only is false. |

### source_token

Short tokens used in listing_source and initial_parent_source. See docs/sources.md and docs/methodology.md (Placeholder units).

| value | meaning |
|---|---|
| `LEX` | Lexikon der Wehrmacht (lexikon-wehrmacht.de), the unit's own page or its timeline tables. |
| `DEW6` | de.wikipedia 'Schematische Kriegsgliederung der Wehrmacht fuer die Operation Overlord' (German order of battle for 6 June 1944). |
| `WP12AG` | en.wikipedia 'Twelfth United States Army Group' (order of battle, 8 May 1945). |
| `WP6AG` | en.wikipedia 'Sixth United States Army Group' (order of battle, 8 May 1945). |
| `WP21AG` | en.wikipedia '21st Army Group'. |
| `WPNORM` | en.wikipedia 'List of Allied forces in the Normandy campaign'. |
| `WPMG` | en.wikipedia 'Operation Market Garden order of battle'. |
| `WPBULGE` | en.wikipedia 'Battle of the Bulge order of battle'. |
| `WPDRAGOON` | en.wikipedia 'Operation Dragoon order of battle'. |
| `WPNORDWIND` | en.wikipedia 'Operation Nordwind'. |
| `WPUNIT` | The unit's own en.wikipedia article (no Wikipedia order-of-battle page above links to it). |
