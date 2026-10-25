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

Primary key: `claim_id` (unique across the whole repository). Rows in each file are sorted by `date`, then `claim_id`.

## units columns (`data/units.csv`)

| column | type | required | meaning | constraints |
|---|---|---|---|---|
| `unit_id` | string | yes | Stable unit key. Primary key. | pattern `^[A-Z]{2,4}(-[A-Z0-9]+)+$` |
| `unit_name` | string | yes | Unit name only. |  |
| `nationality` | string | yes | Nationality (US, UK, Canada, Germany ...). | vocabulary `nationality` |
| `echelon` | string | yes | Organisational level (see vocabulary). | vocabulary `echelon` |
| `branch` | string | yes | Service or arm (see vocabulary). | vocabulary `branch` |
| `theater` | string | yes | Primary theater of the unit (single value; claim rows carry their own theater). | vocabulary `theater` |
| `parent_unit_id` | string | no | Fixed organic parent unit, used for battle groups and combat commands (their parent division). Blank for units whose parent changes with time; use the claim columns `parent_unit_id` and `command_relationships` for time-dependent parents. | pattern `^[A-Z]{2,4}(-[A-Z0-9]+)+$` |
| `parent_only` | boolean | yes | true if the unit has no claim rows of its own (it exists only so that other rows can point to it); false if data/claims/<nationality>/<unit_id>.csv exists. | `true`/`false` |

Rows are sorted by `unit_id`. `parent_only = true` units have no claim file; they exist so `parent_unit_id` and `command_relationships` ids resolve (for example SHAEF, OKW and the German Fifteenth Army). `scripts/validate.py` checks every parent id against `units.csv`.

## unit_id pattern

`NATION-TYPE-NUMBER+ECHELONLETTER`, all upper case.

- Nation: `US`, `UK`, `CAN`, `GER`, `ALL` (combined Allied headquarters such as SHAEF).
- Type: `INF`, `ARM`, `ABN` (airborne), `TNK` (tank brigade), `PZ` (panzer), `SSPZ` (SS panzer), `SSPG` (SS panzergrenadier), `FJ` (Fallschirmjaeger), `LL` (Luftlande), `COR`, `ARMY`, `AG`, `PZG` (panzer group), `OBW` (OB West), `OKW`, `SHAEF`.
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
- `current_activity`: short lower-case phrase, no trailing period; free text, not a vocabulary.

## command_relationships

A JSON list written on one line (CSV-quoted like `strength_json`), or the plain text `unknown`, or blank. Each element:

```json
[{"unit_id":"GER-SSPZ-002D","name":"German 2nd SS Panzer Division Das Reich","relationship":"organic"},{"unit_id":"GER-PZ-LEHRD","name":"German Panzer Lehr Division","relationship":"attached","note":"Placed under Panzer Lehr on arrival"}]
```

Keys: `unit_id` (required; a unit id from `data/units.csv`, or `null` if the formation is not in the table), `name` (required), `relationship` (required, see the `relationship` vocabulary below) and `note` (optional string). No other keys. `parent_unit_id` is the operational parent: the formation the unit was attached to or operating under on that date, otherwise its standing parent. It must also appear in the list. In the example the row's `parent_unit_id` is `GER-PZ-LEHRD` and the organic parent stays in the list. For a battle group, the `parent_unit_id` in `data/units.csv` must be listed here as `organic`. Add a formation to `data/units.csv` (as a `parent_only` unit if it has no claims) rather than using `null`. The original free text and how it was converted are documented in `scripts/migrate_parent_formation.py`.

## strength_json

A JSON object (blank if no source gives figures):

```json
{"basis":"reported_actual","as_of":"1944-06-16","vehicles":{"tanks":85},"vehicle_count_type":"operational","source":"Wikipedia Operation Perch","note":"optional caveat"}
```

Keys: `basis` (required), `as_of` (required, `YYYY-MM-DD`, may differ from the row date), `personnel` (integer), `vehicles` (object name -> integer count), `vehicle_count_type` (required when `vehicles` is present), `source` (required), `note` (optional). At least one of `personnel` or `vehicles` must be present. Guns are not vehicles. Details and basis rules: [../docs/methodology.md](../docs/methodology.md).

## Vocabularies

### theater

Primary theater of operations the claim belongs to. One value per claim row; a unit's primary theater is recorded once in data/units.csv.

| value | meaning |
|---|---|
| `western_europe` | Northwest Europe and France, from the Normandy landings through the end of the war in the West (also Netherlands, Belgium, Luxembourg, Germany west of the Elbe). |
| `mediterranean` | Italy, Sicily, southern France (Dragoon), the Balkans and Greece, and the Mediterranean Sea. |
| `north_africa` | Libya, Egypt, Tunisia, Algeria and Morocco campaigns (1940-1943). |
| `eastern_front` | Germany/Axis versus the USSR (Soviet Union, Poland, Baltic, Romania, Hungary, Finland). |
| `pacific` | Pacific Ocean areas and Southwest Pacific, including Japan, the Philippines and the Dutch East Indies. |
| `cbi` | China-Burma-India theater (China, Burma, India, Indochina). |
| `atlantic` | Atlantic Ocean, Arctic convoys and other naval or air units whose operations are mainly at sea. |
| `other` | Anything that does not fit above (for example East Africa, Middle East, home-front units). Explain in notes. |

### nationality

Nation of the unit. The lowercase value is the folder name under data/claims/. Add a nation here before adding its first unit.

| value | meaning |
|---|---|
| `US` | United States (folder us). |
| `UK` | United Kingdom and Commonwealth formations serving in British armies except those with their own entry (folder uk). |
| `Canada` | Canada (folder canada). |
| `Germany` | Germany, including Waffen-SS and Luftwaffe ground formations (folder germany). |
| `Allied` | Combined Allied headquarters that belong to no single nation, for example SHAEF (folder allied; no claim files yet, only parent_only units). |

### relationship

Meaning of the `relationship` field in each object of `command_relationships`.

| value | meaning |
|---|---|
| `organic` | The standing parent: the formation the original source names as the unit's parent without an attachment qualifier, or a battle group's own division. Not a claim that the link was permanent. |
| `attached` | The unit was attached to this formation on the row's date (the operational parent). |
| `operational_control` | This formation controlled the unit operationally without it being a standing or attached part of it. |
| `reserve` | The unit was held in this formation's (or the high command's) reserve. |
| `unknown` | A formation is named by the source but how it relates to the unit is not stated. |

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

### branch

Service or arm, assigned from the unit name.

| value | meaning |
|---|---|
| `Army` | Regular army (including infantry and static divisions). |
| `Armoured` | Armoured and panzer formations. |
| `Airborne` | Allied airborne formations. |
| `Waffen-SS` | Waffen-SS formations. |
| `Luftwaffe` | Luftwaffe ground formations (for example Fallschirmjaeger). |

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

### boolean

Boolean fields (established, disestablished, destroyed, parent_only) use lowercase text.

| value | meaning |
|---|---|
| `true` | True. |
| `false` | False. |

