# JSON-in-cell fields

Some CSV columns hold a JSON value inside one cell. This page lists every such column. The machine-readable definitions are in [`schema/json/`](../schema/json/): `fields.json` is the registry (table, column, schema file), and each column has its own JSON Schema (draft 2020-12). `scripts/check_json_fields.py` validates every non-blank cell against its schema, and `scripts/build.py` writes `build/all_claims.json`: the same rows and columns as `build/all_claims.csv`, values unchanged as strings, except that these cells appear as nested objects (`null` when blank). The CSV columns and values are not changed.

A survey of all tables under `data/` on 2 November 2026 found one such column: `strength_json`. Later work added other JSON cells registered in `schema/json/fields.json`, including `aircraft` and `capabilities` on claims (see the strength_json schema) and, from 24 November 2026, `authorized_strength_json` on `data/toe_templates.csv`. Lists such as `composing_units` and `reference_ids` remain `;`-separated text, not JSON.

## strength_json

- **Where:** `data/claims/*/*.csv` (column `strength_json`); copied unchanged to `build/all_claims.csv`.
- **Purpose:** sourced strength figures (personnel, vehicles, qualitative status) for the unit on or near the claim date. Blank when no source gives figures (39 of 12,770 claims had a value on 24 November 2026).
- **Schema:** [`schema/json/strength_json.schema.json`](../schema/json/strength_json.schema.json).

| key | type | required | allowed values / rule |
|---|---|---|---|
| `basis` | string | yes | `reported_actual`, `authorized_organization`, `estimate` (vocabulary `strength_json_basis`) |
| `as_of` | string | yes | date `YYYY-MM-DD`; may differ from the row date |
| `source` | string | yes | non-empty; resolves through `data/references_meta.csv` |
| `personnel` | integer | one of personnel / vehicles / status | ≥ 0; needs `scope` |
| `vehicles` | object | one of personnel / vehicles / status | at least one key from the closed snake_case list (`tanks`, `medium_tanks`, `assault_guns`, `tank_destroyers`, `armored_cars`, `half_tracks`, `panzer_iv`, `panther`, `tanks_and_assault_guns`) → integer ≥ 0; needs `vehicle_count_type`; guns are not vehicles; adding a key is a schema MINOR |
| `vehicle_count_type` | string | with `vehicles` only | `operational`, `on_hand`, `unknown` |
| `scope` | string | with `personnel` | `whole_unit`, `sub_force`, `sector` |
| `status` | string | no | `full`, `reduced`, `heavily_depleted` (`destroyed` is derived from the claim's `destroyed` flag, never stored here) |
| `note` | string | no | free-text caveat |

No other keys are allowed. The enumerations must equal the vocabularies in `schema/vocabularies.json`; the checker fails if they drift apart.

Examples:

```json
{"basis":"reported_actual","as_of":"1944-06-16","vehicles":{"tanks":85},"vehicle_count_type":"operational","status":"reduced","source":"Wikipedia Operation Perch","note":"division reported 85 tanks operational on 16 June"}
{"basis":"estimate","as_of":"1944-06-10","personnel":15976,"scope":"whole_unit","status":"full","source":"Wikipedia 3rd Parachute Division"}
{"basis":"estimate","as_of":"1944-06-18","status":"heavily_depleted","source":"CMH Cross-Channel Attack ch. X"}
```


## authorized_strength_json

- **Where:** `data/toe_templates.csv` (column `authorized_strength_json`); copied to `build/toe_templates.csv` and joined onto `build/unit_toe.csv` and the flagship OOB authorized columns.
- **Purpose:** high-level authorized strength of one official table of organization. These figures are authorized, not actual, and must not be copied onto claims. A key is omitted when the official table does not give that figure.
- **Schema:** [`schema/json/authorized_strength_json.schema.json`](../schema/json/authorized_strength_json.schema.json).

| key | type | required | allowed values / rule |
|---|---|---|---|
| `personnel` | integer | no | ≥ 0; authorized whole-unit personnel total when the official table gives one |
| `counts` | object | no | keys from vocabulary `authorized_count_key` (including `tanks` for an undifferentiated tank total) → integer ≥ 0 |
| `structure` | object | no | keys from vocabulary `authorized_structure_key` → integer ≥ 0; a high-level subordinate count, not a list of unit ids |

No other keys are allowed. There is no `basis` or qualitative `status` field; the figures are authorized by definition, and the template's `reference_ids` cover the object. The enumerations must equal the vocabularies in `schema/vocabularies.json`.

Example:

```json
{"personnel":10937,"counts":{"tanks":263},"structure":{"tank_battalions":3,"armored_infantry_battalions":3}}
```

`strength_json` vehicle keys are frozen (Task 4, 24 November 2026) to the snake_case list above. Five claims were remapped and annotated (C0004, C0038, C0158, C0173, C0184); the five cells that already used `tanks` needed no rename. Authorized figures stay on templates, not on claims. Do not fill `basis=authorized_organization` on claims to stand in for a TO&E template.

## theater in the JSON outputs (not a JSON cell)

`theater` is a plain vocabulary column, not JSON, but it appears in the JSON outputs: `build/all_claims.json` (one string per row) and the feature properties of `build/claims.geojson`. Since 9 November 2026 it is the row's own theater (values in `schema/vocabularies.json`, rules in `schema/README.md`, "Theater"), so one unit's rows may carry different values (for example `GER-INF-106D`: `home_germany` at Wahn in 1940, `eastern_front` 1941-1944, `western_europe` in 1942-1943 and 1945). A consumer that wants the Western Front only filters on `theater == "western_europe"`.

## commander_person_id in the JSON and GeoJSON outputs (not a JSON cell)

`commander_person_id` is a plain derived column, not a JSON object. It appears on `build/all_claims.csv`, `build/all_claims.json`, and as a feature property on `build/claims.geojson` (which also now carries the source-stated `commander` string). The value is the `PE####` id(s) of the people linked to that claim in `data/unit_commander_claims.csv`. When a claim names more than one person (a handover cell, or embarked officers on a ship), the distinct ids are joined with `;` in ascending id order. The column is blank when `commander` is `unknown` and the claim is not a sourced vacancy end.

## commander_on_date columns in the JSON and GeoJSON outputs (not JSON cells)

`commander_on_date`, `commander_on_date_person_id`, `commander_on_date_source` and `commander_on_date_basis` are plain derived columns, not JSON objects. They appear on `build/all_claims.csv`, `build/all_claims.json`, and as feature properties on `build/claims.geojson`. They are not stored in `data/claims/`. The source-stated `commander` field is unchanged.

- `commander_on_date_source` is `claim` when the claim itself names a commander, `tenure` when the name is looked up from a preferred `unit_commanders` tenure that covers the claim date, and blank when no commander is known for that date (including a sourced vacancy such as C0862).
- `commander_on_date` is the claim's commander string when the source is `claim`, or the person's `canonical_name` (several names joined with `;` when more than one preferred tenure covers the date) when the source is `tenure`.
- `commander_on_date_basis` is `stated` for a claim-named commander. For a tenure lookup it is `narrative` when neither boundary is inferred, `inferred_start` when `valid_from_basis` is `claim_date` or `inferred` (often the first sourced claim, not the historical appointment), `inferred_end` when only the end is `inferred` or `inferred_from_next_claim`, and `inferred_start_end` when both are inferred. An open end (`open_at_last_claim`) is not treated as inferred.

See "People and commanders" in `schema/README.md` for the lookup and tie rules.

## Adding a JSON column

Add a schema file to `schema/json/`, an entry to `schema/json/fields.json`, and a section to this page in the same change.
