# Methodology

This page explains how the claims in `data/claims/` were built and how to read them. The column definitions are in [../schema/README.md](../schema/README.md).

## Claims and event-based rows

One row is one claim: *unit X was at place P on date D, doing A, and here is the source.* Rows are **event-based**, not daily. A unit gets a row on days when something substantial happened (landing, arrival, capture of a place, a major attack or counterattack, a command change, a headquarters move, a surrender, destruction). Quiet days are intentionally absent, so a unit's position between two rows is unknown, not unchanged. Do not interpolate unless you say so.

Each row has:

- **Who**: `unit_id` (stable key, one file per unit), plus `unit_name`, `echelon`, `branch` copied from `data/units.csv`.
- **When / where**: `date`, `theater`, coordinates, `location_name`, `location_represents` (headquarters, main body, sector centre, front-line point, objective, approach route), `precision_km`.
- **What**: `event_type` (one of 14 values), `current_activity` (short free-text phrase), `engaged_with` (opponents fought that day).
- **Command**: `parent_formation` and `commander` on that date (time-dependent), `composing_units` (listed when first given or when it changes).
- **Strength**: `strength_status` (qualitative) and optional `strength_json` (numbers).
- **Quality**: `confidence`, `claim_status`, `source`, `notes`.

Rows were built by reading the sources in [sources.md](sources.md), writing one claim per unit-date, geocoding the place (Wikipedia coordinates first, OpenStreetMap Nominatim for gaps), then assigning precision, confidence and the other fields by the rules below.

## Units, battle groups and parents

Every unit has one `unit_id` and one row in `data/units.csv`. Battle groups (Kampfgruppen) and combat commands are units of their own (`echelon` = `regiment/battle_group`) with a fixed `parent_unit_id` (the division) and a time-dependent `parent_formation` on each claim (for example "attached to Panzer Lehr"). Brigades stay brigades. When all of a division's rows were really about its battle group, the division has no claim file and is a `parent_only` unit so that parent links still resolve. A claim is never duplicated between a division and its battle group.

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
- `source`: short source reference. `note`: optional caveat or a conflicting figure from another source.
- Only fields with sourced numbers are included. Where sources conflict, the row's `notes` or the `note` field names the other figure.
- `strength_status` (`full`, `reduced`, `heavily_depleted`, `destroyed`, `unknown`) is set only when a source states strength or losses; it is deliberately sparse.

In the proof of concept 21 of 212 rows carry figures (16 estimate, 5 reported_actual, 0 authorized_organization), mostly operational tank counts for panzer divisions and landing tallies for Allied formations. This is a sparse, sourced field, not a full order-of-battle strength table.

## Dates, time and places

- Dates are calendar dates in local historical time; no time of day is recorded (put it in `notes`).
- Place names follow the source; historical names and later renamings are noted in `notes` where known.
- Coordinates are WGS84. A coordinate may be a representative point (see `location_represents` and the "(point = X)" convention in `location_name`) rather than the exact position of the unit.

## Provenance of the first import

The proof of concept was built in five iterations (v1 to v5): v1 flat claims; v2 added unit-name/nationality/echelon split, operation and sub-operation names, `precision_km`, numeric `confidence` and conflict groups; v3 added `current_activity`; v4 added `unit_id`, `parent_formation`, `commander`, `event_type`, `engaged_with` and `strength_status`; v5 added battle groups as units and `strength_json`; this repository adds `theater` and splits the data by unit. The flat v5 CSVs are kept in `archive/v5_flat/`, and `scripts/split_from_flat.py` reproduces `data/` from them. `claim_id`s are identical in every version.
