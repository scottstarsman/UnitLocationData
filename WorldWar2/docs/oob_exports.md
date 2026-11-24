# Order-of-battle exports

`scripts/export_oob.py` builds a point-in-time order-of-battle tree from the live `data/` and `build/` tables. `scripts/build.py` writes six flagship dates under `build/oob/` on every build (Task 2, OB9–OB15). Do not hand-edit those files.

## Command line

```
python scripts/export_oob.py 1944-06-06
    [--time HH:MM]
    [--root-unit UNIT-ID]
    [--side Allied|Axis]
    [--domain ground|air|naval]          # repeatable
    [--operation OP-…]
    [--include relations|located|both|intersection]
    [--near-days 14]
    [--include-placeholders|--no-include-placeholders]
    [--format json,csv,markdown]
    [--out DIR_OR_FILE]
```

`--include relations` (the default, and the canonical flagship JSON/CSV) keeps every unit whose command relation covers the date, including a `possible` 90-day carry-forward. `--include intersection` (the flagship `*-located.csv`) keeps only units that also have a preferred location claim within `--near-days`. `--include located` and `both` are for ad-hoc use. Units with a nearby claim but no covering relation appear only in `located` / `both`, as roots with `parent_reason=no_covering_relation`.

`--operation` restricts the tree to units that already appear in `build/operation_units.csv` for that operation (direct or rolled from a descendant). It does not invent participation from the command hierarchy.

## Tree rules

The primary parent is the `scripts/who_controls.py` answer: the lowest-echelon holder of `operational_control` or `attached`, otherwise the lowest-echelon holder of `assigned` or `unspecified_subordination`, otherwise the organic parent (labelled `organic_fallback`). Per-relation overrides in `data/who_controls_overrides.csv` are honoured. On a handover day where two intervals cover the date and no hour is recorded, the exporter does not guess: `handover` is true, there is no primary parent, and both candidates are listed as additional parents.

Every other covering relation is listed as an additional parent. This is how a D-Day ship that is `assigned` both to a flotilla and to a task group is shown: the flotilla (lower echelon) is the primary parent; the task group appears beside it. There is no special “prefer task group” rule in v1 (OB10).

An `open_at_last_claim` interval is `certain` only through `last_listed_date` and `possible` for at most 90 days after that. The 90-day cutoff is a reading rule, not a new end date, and is not lengthened to keep June 1944 air and naval listings alive into the winter snapshots (OB11). Late-war flagship trees therefore have few air or naval units until more relations are listed after June 1944.

## Location, commanders, strength, authorized TO&E and symbols

A unit’s location is its nearest **preferred** claim to the snapshot date. Ties prefer a claim on or before the date, then higher `confidence`, then `claim_id`. The offset (negative = before) and `location_in_window` are always published; the location is never inherited from a parent headquarters (OB13). `strength_json` is taken from that same claim when the cell is filled (it is rare) and is never overwritten with an authorized total. Authorized TO&E columns (`authorized_template_id`, `authorized_template_name`, `authorized_personnel`, `authorized_strength_json`) come from that unit's own `data/unit_toe.csv` assignment covering the date. They are left blank when the unit has no assignment, and they are never inherited from a parent headquarters (TE6, TE14). Commanders are preferred tenures that contain the date. The `sidc` comes from `build/unit_symbols.csv` (and `build/other_domains/unit_symbols.csv` until Task 4) for a period that covers the date.

Placeholder units are included by default and carry `record_status`. Units marked `out_of_scope` are omitted unless `--include-out-of-scope` is passed. A `destruction` or `surrender` claim does not drop the unit; it remains visible as `event_type` on the location claim.

Side is resolved through `allegiance.Resolver` (nationality name → code via `data/nationalities.csv`, then `data/nation_allegiance.csv`, with the four Allied-headquarters rows in `data/unit_allegiance_overrides.csv`).

## Flagship files

Each of 6 June, 18 July, 15 August and 16 December 1944, and 24 March and 7 May 1945, is written as:

- `build/oob/YYYY-MM-DD.json` and `.csv` — all domains, `--include relations`
- `build/oob/YYYY-MM-DD-ground.md` — ground units only, same include mode, as a readable tree
- `build/oob/YYYY-MM-DD-located.csv` — `--include intersection --near-days 14`, for map use

`build/oob/README.md` (generated) restates the 90-day rule, the dual-parent display rule, and the late-war air/naval coverage gap. `scripts/run_checks.sh` includes `python scripts/build.py --check`, which fails if any flagship file is missing or out of date.
