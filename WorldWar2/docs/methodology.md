# Methodology

This page explains how the claims in `data/claims/` were built and how to read them. The column definitions are in [../schema/README.md](../schema/README.md).

## Claims and event-based rows

One row is one claim: *unit X was at place P on date D, doing A, and here is the source.* Rows are **event-based**, not daily. A unit gets a row on days when something substantial happened (landing, arrival, capture of a place, a major attack or counterattack, a command change, a headquarters move, a surrender, destruction). Quiet days are intentionally absent, so a unit's position between two rows is unknown, not unchanged. Do not interpolate unless you say so.

Each row has:

- **Who**: `unit_id` (stable key, one file per unit), plus `unit_name`, `echelon`, `branch` copied from `data/units.csv`.
- **When / where**: `date`, `theater`, coordinates, `location_name`, `location_represents` (headquarters, main body, sector centre, front-line point, objective, approach route), `precision_km`.
- **What**: `event_type` (one of 14 values), `current_activity` (short free-text phrase), `engaged_with` (opponents fought that day).
- **Command**: `parent_unit_id` (operational parent on that date), `command_relationships` (JSON list of organic, attached, operational-control and reserve links), `commander` on that date (time-dependent), `composing_units` (listed when first given or when it changes).
- **Strength**: `strength_status` (qualitative) and optional `strength_json` (numbers).
- **Quality**: `confidence`, `claim_status`, `source`, `notes`.

Rows were built by reading the sources in [sources.md](sources.md), writing one claim per unit-date, geocoding the place (Wikipedia coordinates first, OpenStreetMap Nominatim for gaps), then assigning precision, confidence and the other fields by the rules below.

## Units, battle groups and parents

Every unit has one `unit_id` and one row in `data/units.csv`. Battle groups (Kampfgruppen) and combat commands are units of their own (`echelon` = `regiment/battle_group`) with a fixed `parent_unit_id` in `data/units.csv` (the organic parent division) and, on each claim, a time-dependent `parent_unit_id` and `command_relationships` (for example attached to Panzer Lehr, with the organic parent division kept in the list). Brigades stay brigades. When all of a division's rows were really about its battle group, the division has no claim file and is a `parent_only` unit so that parent links still resolve. A claim is never duplicated between a division and its battle group.

## Parents and command relationships

`parent_unit_id` is the **operational parent** on the row's date, as one unit id from `data/units.csv`: the formation the unit was attached to or operating under, otherwise its standing parent. It is blank for a top-level headquarters and `unknown` if no source was checked. `command_relationships` is a JSON list that also holds the organic parent (relationship `organic`), attachments (`attached`), formations that controlled the unit without owning it (`operational_control`), and reserves (`reserve`); see the `relationship` vocabulary. Rules used when the free text of v5 was converted (details in `scripts/migrate_parent_formation.py`):

- A plain parent in the old text becomes an `organic` entry. This records the standing parent the source names, not a claim that the link was permanent (corps and armies reshuffled divisions constantly).
- "attached to X" makes X the operational parent and the named parent an `organic` entry (battle groups attached to another division or corps).
- A corps or high-command reserve becomes `reserve`. US First Army under 21st Army Group is `operational_control`.
- Where the old text listed a battle group's division and a higher formation without saying how they relate, the division stays the parent unless the row's notes show who controlled the group; the higher formation is kept with relationship `unknown`.
- Parents named without an id (Fifteenth Army, OKW, SHAEF) were added to `units.csv` as `parent_only` units; SHAEF is nationality `Allied`.
- `unknown` is kept where the source did not give a parent; the migration adds no relationship that the old text or the row's notes do not support.

**Operational parent versus organic parent (rule).** `parent_unit_id` answers "who commanded this unit **on this row's date**"; the standing (organic) parent is never put only in `parent_unit_id`: it is recorded in `command_relationships` as `organic`, and a temporary parent as `attached` (or `operational_control`, `reserve`). So a row for an independent brigade that landed under a division's command has the division as `parent_unit_id` (relationship `attached`) and the army or corps that holds the brigade as the `organic` entry; it is not an organic part of the division (review finding, C0001). Three further rules:

- **Dates decide.** An attachment applies from the day a source says it took effect, not from the day of the event it enabled. Put that day in the entry's optional `effective_from`, and keep a row's relationship in line with its own date: the 82nd Airborne's bridgehead attack was ordered for 17 June under VII Corps, and control passed to VIII Corps on 19 June (C0131, C0141).
- **Record "unknown", do not guess.** If a source gives the attachment but not the standing parent, add an entry with relationship `unknown` (the validator warns about an `attached` entry with no `organic` or `unknown` entry beside it).
- **A relationship is not an organisation chart.** "Under command for the assault" or "attached" does not make the unit part of the other formation; `organic` is reserved for the standing parent a source names without an attachment qualifier.

## precision_km

`precision_km` is a **judgment estimate of the radius, in kilometres, within which the unit (or its main body) probably was**. It is not a surveyed error. Values are banded: 1, 5, 10, 25, 50 (and 3 once, as a manual override for a village-scale point). Starting rules (then reviewed row by row):

| location quality | division or smaller | corps | army and above |
|---|---|---|---|
| exact (named place tied to the date) | 1 | 5 | 5 |
| approximate | 5 | 10 | 25 |
| inferred | 10 | 25 | 50 |

Special cases: headquarters rows are 1 (exact), 5 (named town or village, approximate) or 25 (inferred); beach `sector_center` rows are at least 10 because the beaches are 8-10 km wide; `approach_route` rows are 25 (a march within a region) or 50 (a long move such as from Brittany or Chartres). Manual overrides are explained in the row's `notes`.

## Confidence rubric

`confidence` is a number applied by rule from location quality and the number of independent source families (Wikipedia, the US Army CMH/HyperWar volumes, and each other website count as separate families; several Wikipedia pages count as one family):

| value | rule |
|---|---|
| 0.9 | exact location and two independent source families agree |
| 0.7 | exact location with one authoritative source (for example CMH), or approximate location with two source families |
| 0.5 | exact location with one secondary source (Wikipedia, local-history page), or approximate location with one source family |
| 0.3 | position inferred or a representative point (HQ not tied to the date, unverified beach, front-line representative point), or the date itself is approximate |

Caps: the preferred claim of a conflict group is at most 0.7; alternate and disputed claims at most 0.5. Confidence measures the claim's date/place support, not the importance of the unit. Only these four levels are used, so scores are comparable.

## Conflict policy

Sources disagree. The dataset keeps every competing claim as its own row with its own source, rather than choosing silently:

- Rows share a `conflict_group_id` (`G001`, ...). A group has at least two claims about the **same unit**.
- `claim_status = preferred`: a non-conflicted claim, or the best-supported claim of a group (exactly one per group).
- `alternate`: a competing claim judged less likely than the preferred one.
- `disputed`: no source is judged better. A group with no preferred row is all disputed.
- Every non-conflicted row is `preferred`. `scripts/validate.py` enforces these rules.
- Each row's `notes` explains the disagreement and cites only the sources that support that row's own claim.

Minor source disagreements that do not change a row's date or place (for example a rank spelling) are recorded in `notes`, not as a conflict group. A few of these are listed in the roadmap's known-gaps section.

## strength_json

An optional JSON object with sourced strength numbers. Never estimate numbers yourself; leave it blank where no source gives figures.

```json
{"basis":"reported_actual","as_of":"1944-06-16","vehicles":{"tanks":85},"vehicle_count_type":"operational","source":"Wikipedia Operation Perch","note":"..."}
```

(`personnel` is omitted when the source gives no personnel figure; the example is illustrative and shows the 21st Panzer Division row C0090.)

- `basis`: `reported_actual` = a unit report or an operational count relayed by the source (for example working-order tank returns); `authorized_organization` = establishment / table-of-organisation strength; `estimate` = rounded, approximate or retrospective figures, and landing tallies.
- `as_of`: the date the figure applies to, which can differ from the row date.
- `personnel`: integer number of people, as stated by the source.
- `vehicles`: object of vehicle name to integer count. Only counted vehicles (tanks, assault guns, half-tracks). Guns are not vehicles and are left out.
- `vehicle_count_type`: `operational` (working order), `on_hand` (on hand, working order not stated) or `unknown` (the source does not say what the count means). Required when `vehicles` is present.
- `scope` (optional, recommended with `personnel`): `whole_unit`, `sub_force` or `sector`. A figure given for a line, a task force or a sector (CMH: Kraiss "had 2,500 men, 14 guns ... 5 tanks" for the new Elle line, C0057) is **not** the strength of the whole division: mark it `sub_force` or `sector`, say so in `note`, and do not set `strength_status` as if it were a whole-unit count unless a source says so. Do not subtract it from, or compare it with, an establishment figure.
- `source`: short source reference. `note`: optional caveat or a conflicting figure from another source (for example 17,200 on paper versus 12,000 for D-Day).
- Only fields with sourced numbers are included. Where sources conflict, the row's `notes` or the `note` field names the other figure.
- `strength_status` (`full`, `reduced`, `heavily_depleted`, `destroyed`, `unknown`) is set only when a source states strength or losses; it is deliberately sparse.

In the proof of concept 21 of 212 rows carry figures (16 estimate, 5 reported_actual, 0 authorized_organization), mostly operational tank counts for panzer divisions and landing tallies for Allied formations. This is a sparse, sourced field, not a full order-of-battle strength table.

## Writing a row: one action, documented wording

- **One row, one action.** A row says what a unit is documented as doing on one date at one place. If the sources describe several actions on that date at different places or against different opponents, write one row per action (new `claim_id`s are allowed; ids are never reused) or, when the pieces cannot be separated, describe the connected action and say in `notes` what is and is not documented. Do not put a day's whole story in `current_activity` (review finding, C0184: a company of Panzer IVs was documented in a three-part fight).
- **Say only what the sources say.** `current_activity` uses the sources' own terms; it does not add a direction, aim or outcome the source does not give. "Attacking from the Orne bridgehead" was overstated for I Corps on 12 June, when the attack was postponed, limited and contained, and the bridgehead itself was under German attack (C0084). Words such as "probably", "likely" or "inferred" belong in `notes`, not in `current_activity`; the validator warns about them and about activities over 120 characters.
- **Name the real opponent.** `engaged_with` lists units a source places in the fight at that place and time, not the formation next door that a source mentions in a different action (C0184: the Mouen fight was against 11th Armoured Division elements, the Grainville attack by the 15th (Scottish) Division was a different action). More than three opponents is a prompt to check whether the row mixes actions.
- **Organisational level.** When a sub-unit did the fighting (a company, a battle group), the row for the parent unit records that element's part and says so in `notes`.
- **Coordinates.** A coordinate must lie within `precision_km` of what the row says it represents. A line or sector is represented by a midpoint with a radius that covers it, not by one end (C0057), and the two rows of a conflict group should not be farther apart than their radii unless the disagreement is about place and says so (C0131 was left near La Haye-du-Puits while C0141 had been corrected to Etienville).

## Dates, time and places

- Dates are calendar dates in local historical time; no time of day is recorded (put it in `notes`).
- Place names follow the source; historical names and later renamings are noted in `notes` where known.
- Coordinates are WGS84. A coordinate may be a representative point (see `location_represents` and the "(point = X)" convention in `location_name`) rather than the exact position of the unit.

## Review guardrails

`python scripts/validate.py` checks structure and, since the first spot check, also prints **warnings** (never errors; exit code unchanged): `strength_json` with `personnel` but no `scope`; an `attached` or `operational_control` entry that is not the `parent_unit_id`; an `attached` entry without an `organic`/`unknown` entry; a relationship whose `effective_from` is after the row's date; a `current_activity` over 120 characters or with a hedge word; more than three opponents in `engaged_with`. Existing rows that trigger a warning are a to-do list for the next review pass, not a defect in the check.

`python scripts/check_coordinates.py` prints coordinate warnings (it exits 0): points outside a theater bounding box, the same `location_name` at points more than 3 km apart, conflict-group claims farther apart than their precision radii, and a unit that moves more than 80 km/day between preferred rows. With `--geocode` (add `--country fr` for a French campaign) it also fetches up to ten geocode candidates (OpenStreetMap Nominatim, one request per second, cached in `.cache/`) for the place named in `location_name` and warns when even the nearest candidate is farther than max(15 km, twice `precision_km`) from the point. Run it before a release and after adding many rows; it is not run in CI. In its first full run (212 rows) the geocode check flagged 4 rows, all false positives caused by name matching (a place written without accents, short names such as Vire and Caumont, an ambiguous Pont-l'Abbe), and could not geocode about 45 sector, line and axis names at all, so treat it as a prompt only and read each warning against the row; the offline conflict check, in the same run, found the C0131/C0141 disagreement. A warning means "look at this row", and a deliberate place disagreement or an `approach_route` row can be a correct reason to keep the data.

## Spot-check review

Spot checks (sampling about 15 rows, ideally by someone who did not write them) find different problems from the validator. Choose the sample by risk, not at random only: all rows with an `attached` or `operational_control` entry, rows with `strength_json`, rows in a conflict group, rows whose `current_activity` is long, and rows near the end of a long march. For each sampled row, apply the per-row checklist in [CONTRIBUTING.md](../CONTRIBUTING.md#per-row-review-checklist) against a source that was **not** used to write the row, record the outcome (confirmed / corrected / disputed) and the change in a review note, and fix only what the sources support. The first review (five of 15 rows corrected) is the origin of the rules above.

## Provenance of the first import

The proof of concept was built in five iterations (v1 to v5): v1 flat claims; v2 added unit-name/nationality/echelon split, operation and sub-operation names, `precision_km`, numeric `confidence` and conflict groups; v3 added `current_activity`; v4 added `unit_id`, `parent_formation`, `commander`, `event_type`, `engaged_with` and `strength_status`; v5 added battle groups as units and `strength_json`; this repository adds `theater`, splits the data by unit and replaces the free-text `parent_formation` by `parent_unit_id` + `command_relationships` (`scripts/migrate_parent_formation.py`). The flat v5 CSVs are kept in `archive/v5_flat/`, and `scripts/split_from_flat.py` reproduces `data/` from them, including that last step (the flat files keep the original `parent_formation` text). `claim_id`s are identical in every version.
