# Contributing

Thank you for helping. This project is only useful if every row can be checked, so the rules are strict.

## Rules

1. **Every row needs a source.** The `source` column must hold at least one URL (separate several with ` | `, and end with the coordinate source note, for example `; coords: Wikipedia`). Say in `notes` what the source says. Cite a page or chapter when you can.
2. **Conflicting claims become separate rows.** If two sources disagree (date, place, commander, anything in the row), do not average or pick silently. Add one row per claim, give them the same `conflict_group_id` (next free `G###`), and set `claim_status`: one `preferred` and the others `alternate`, or all `disputed` if no source is better. Explain the disagreement in `notes` on each row.
3. **Never invent.** If a value is not in a source, write `unknown` (for text fields such as `commander`, or `parent_unit_id` and `command_relationships`) or leave the optional field blank. Do not guess numbers for `strength_json`. A gap is better than a plausible fabrication.
4. **One row is one claim** about one unit on one date. Rows are event-based; do not add filler rows for quiet days.
5. **Use the vocabularies** in `schema/vocabularies.json`. If you need a new value (for example a new nationality or theater), add it there and in `schema/README.md` in the same pull request, with a one-line definition.
6. **Keep ids stable.** `claim_id` is never reused or renumbered. New claims take the next free number (the highest existing id + 1). Do not delete a claim to "fix" it: correct it, or add a conflicting claim.
7. **Licensing.** Do not copy text from copyrighted sources. Facts and short quotations with attribution are fine. Contributions are released under the data and code licences of this repository.

## Add a claim to an existing unit

1. Open `data/claims/<nationality>/<unit_id>.csv`.
2. Add a row with the next free `claim_id`, all columns filled as described in [schema/README.md](schema/README.md), and insert it in order (sorted by `date`, then `claim_id`).
3. Run `python scripts/validate.py`, then `python scripts/build.py`.
4. Commit both the data change and the regenerated `build/` files.

## Add a new unit

1. Add a row to `data/units.csv` (kept sorted by `unit_id`). Choose the `unit_id` as `NATION-TYPE-NUMBER+ECHELONLETTER`, for example `US-INF-029D` (see [schema/README.md](schema/README.md)). For a battle group use `NATION-KG-NAME` (for example `GER-KG-FREY`) or a similar descriptive id, `echelon` `regiment/battle_group`, and set `parent_unit_id` to its parent division (the organic parent; each claim row then lists it as an `organic` entry in `command_relationships`).
2. If the unit has claims, set `parent_only` to `false` and create `data/claims/<nationality>/<unit_id>.csv` with the exact header used by the other files. If the unit exists only so others can point to it as a parent, set `parent_only` to `true` and create no file.
3. Parents: a claim's `parent_unit_id` must be a unit in `units.csv` (blank for a top-level headquarters, `unknown` if not verified) and `command_relationships` is a JSON list (see [schema/README.md](schema/README.md#command_relationships)). If a parent formation is not in the table yet, add it as a `parent_only` unit first.
4. A unit's `unit_name`, `nationality`, `echelon` and `branch` in every claim row must equal the values in `units.csv`.
5. Add a claim row (above) and validate.

## Run the checks

```bash
python scripts/validate.py
python scripts/build.py
git diff --stat build/        # build outputs must be committed with your change
python scripts/build.py --check
```

## Pull request checklist

- [ ] Every new or changed row has a source URL and a `notes` entry saying what the source supports.
- [ ] Conflicting information is kept as separate rows with a shared `conflict_group_id`; exactly one `preferred` or all `disputed`.
- [ ] Nothing is invented; unknowns are `unknown` or blank.
- [ ] New `claim_id`s are unique and follow the highest existing id; none were reused.
- [ ] New units are in `data/units.csv` and the file name matches `unit_id`.
- [ ] `python scripts/validate.py` passes.
- [ ] `python scripts/build.py` was run and the `build/` changes are committed.
- [ ] New vocabulary values (if any) are documented in `schema/vocabularies.json` and `schema/README.md`.
- [ ] Confidence and precision follow the rubric in `docs/methodology.md`.

Be kind: see the [code of conduct](CODE_OF_CONDUCT.md).
