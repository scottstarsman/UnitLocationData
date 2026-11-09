# JSON-in-cell fields

Some CSV columns hold a JSON value inside one cell. This page lists every such column. The machine-readable definitions are in [`schema/json/`](../schema/json/): `fields.json` is the registry (table, column, schema file), and each column has its own JSON Schema (draft 2020-12). `scripts/check_json_fields.py` validates every non-blank cell against its schema, and `scripts/build.py` writes `build/all_claims.json`: the same rows and columns as `build/all_claims.csv`, values unchanged as strings, except that these cells appear as nested objects (`null` when blank). The CSV columns and values are not changed.

A survey of all tables under `data/` on 2 November 2026 found one such column: `strength_json`. No other column holds JSON (lists elsewhere, for example `composing_units` and `reference_ids`, are `;`-separated text, not JSON).

## strength_json

- **Where:** `data/claims/*/*.csv` (column `strength_json`); copied unchanged to `build/all_claims.csv`.
- **Purpose:** sourced strength figures (personnel, vehicles, qualitative status) for the unit on or near the claim date. Blank when no source gives figures (31 of 7,055 claims had a value on 2 November 2026).
- **Schema:** [`schema/json/strength_json.schema.json`](../schema/json/strength_json.schema.json).

| key | type | required | allowed values / rule |
|---|---|---|---|
| `basis` | string | yes | `reported_actual`, `authorized_organization`, `estimate` (vocabulary `strength_json_basis`) |
| `as_of` | string | yes | date `YYYY-MM-DD`; may differ from the row date |
| `source` | string | yes | non-empty; resolves through `data/references_meta.csv` |
| `personnel` | integer | one of personnel / vehicles / status | ≥ 0; needs `scope` |
| `vehicles` | object | one of personnel / vehicles / status | at least one key; vehicle type name → integer ≥ 0; needs `vehicle_count_type`; guns are not vehicles |
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

## theater in the JSON outputs (not a JSON cell)

`theater` is a plain vocabulary column, not JSON, but it appears in the JSON outputs: `build/all_claims.json` (one string per row) and the feature properties of `build/claims.geojson`. Since 9 November 2026 it is the row's own theater (values in `schema/vocabularies.json`, rules in `schema/README.md`, "Theater"), so one unit's rows may carry different values (for example `GER-INF-106D`: `home_germany` at Wahn in 1940, `eastern_front` 1941-1944, `western_europe` in 1942-1943 and 1945). A consumer that wants the Western Front only filters on `theater == "western_europe"`.

## Adding a JSON column

Add a schema file to `schema/json/`, an entry to `schema/json/fields.json`, and a section to this page in the same change.
