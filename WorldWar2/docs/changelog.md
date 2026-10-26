# Changelog of the data structures

Changes to the tables, schemas and scripts (not to individual claims). Newest first.

## normalize-cheap-fixes (26 October 2026)

Follows the review in [normalization_review.md](normalization_review.md) (items F1 small step, and the "cheap fixes" of its recommendation 4). Applied with `scripts/migrate_normalize.py`.

- **Command relationships.** The redundant `name` is dropped from all 1,061 `command_relationships` entries (the name comes from `units.csv`). The 16 entries with `unit_id` null (formations that are not units: "standing parent not identified" 14, "Army not shown in CMH table" 2) keep their wording as `note`; `unit_id` null is now only allowed with relationship `unknown` and a note. The `unknown` sentinel is gone from `parent_unit_id` (15 claims, now blank) and from `command_relationships` (the same 15 claims, now one entry `{"unit_id": null, "relationship": "unknown", "note": "parent not verified"}`).
- **units.csv.** The column `parent_only` (identical to `record_status = placeholder` on 354 of 354 rows) is removed; 16 columns remain.
- **Nationalities.** New `data/nationalities.csv` (10 rows: code, name, adjective, alt_adjectives, alliance, kind, note). Units, claims and operations refer to its `name`; the validator checks the references and that each unit id starts with the nation's code. The 3 `Allied` units keep the explicit multinational value. `operations.nationality_scope` `German` (2 rows) is now `Germany`.
- **Single-source vocabularies.** Echelon rank and display order, relationship groups (standing, active), `higher_than_organic` and `source_type` are new entries of `schema/vocabularies.json`; `validate.py`, `build.py`, `audit_temporal_relationships.py` and `who_controls.py` read them through `scripts/common.py`. `operations.py` and `build_references.py` read their vocabularies from the same file; the `nationality` and `operation_scope` entries were removed (the table replaces them).
- **Foreign keys.** `foreignKeys` in `claims.schema.json` and `units.schema.json`, the new `relations.schema.json` for the side tables, enforced by `validate.py`; `theater` is now one of the repeated unit columns checked on every claim.
- **Derived outputs.** `build/all_claims.csv`: columns `command_relationships` (all 566 rows) and `parent_unit_id` (15 rows) changed. `build/command_relations.csv`: `higher_name` normalised to `<adjective> <unit_name>` in 64 of 315 rows (it was inconsistent between claims, for example "First Army" and "US First Army"); no other column changed. `build/operations.csv`: `nationality_scope` in 2 rows. All other generated files are byte-identical.
