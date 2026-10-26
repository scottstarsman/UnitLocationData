# Contributing

Thank you for helping. This project is only useful if every row can be checked, so the rules are strict.

## Rules

1. **Every row needs a source.** The `source` column must hold at least one URL (separate several with ` | `, and end with the coordinate source note, for example `; coords: Wikipedia`). Say in `notes` what the source says. Cite a page or chapter when you can. Then list the same sources in `reference_ids` (see "How to cite a new source").
2. **Conflicting claims become separate rows.** If two sources disagree (date, place, commander, anything in the row), do not average or pick silently. Add one row per claim, give them the same `conflict_group_id` (next free `G###`), and set `claim_status`: one `preferred` and the others `alternate`, or all `disputed` if no source is better. Explain the disagreement in `notes` on each row.
3. **Never invent.** If a value is not in a source, write `unknown` (for text fields such as `commander`; for a parent that is not verified leave `parent_unit_id` blank and record an `unknown` relationship entry) or leave the optional field blank. Do not guess numbers for `strength_json`. A gap is better than a plausible fabrication.
4. **One row is one claim** about one unit on one date. Rows are event-based; do not add filler rows for quiet days.
5. **Use the vocabularies** in `schema/vocabularies.json`. If you need a new value (for example a new nationality or theater), add it there and in `schema/README.md` in the same pull request, with a one-line definition.
6. **Keep ids stable.** `claim_id` and the command `relation_id` (CR0001...) are never reused or renumbered. New claims take the next free number (the highest existing id + 1). Do not delete a claim to "fix" it: correct it, or add a conflicting claim.
7. **Command, strength and wording rules** (details in [docs/methodology.md](docs/methodology.md)): `parent_unit_id` is the operational parent *on the row's date* and the standing parent goes in the command relations (`data/command_relations.csv`) as `assigned` (or `unspecified_subordination` when the source combines assigned and attached, as the CMH ETO-OB tables do; never turn that into `attached` without a source); `organic` is only for constituted components such as a battle group's own division; a temporary link is `attached` with the date it took effect (`valid_from`, optionally `valid_to` and `date_basis`; the claim's own statement goes in the `stated_*` columns of `data/command_relation_claims.csv`); other authority is `operational_control`, `administrative_control`, `supporting` or `coordinating`; a coordinate taken from another date needs `location_date`, `location_basis` and `location_temporal_offset_days`; a landing row's point is the landing area, not a headquarters; every `personnel` figure needs a `scope` (the validator errors without one), and a figure for a task force, line or sector gets `sub_force` or `sector`, not `whole_unit`; if no source says what a figure covers, leave it out; one row describes one documented action, in the sources' words, with no inferred direction or result.
8. **Licensing.** Do not copy text from copyrighted sources. Facts and short quotations with attribution are fine. Contributions are released under the data and code licences of this repository.

## Add a claim to an existing unit

1. Open `data/claims/<nationality>/<unit_id>.csv`.
2. Add a row with the next free `claim_id`, all columns filled as described in [schema/README.md](schema/README.md), and insert it in order (sorted by `date`, then `claim_id`).
3. Run `python scripts/validate.py`, then `python scripts/build.py`.
4. Commit both the data change and the regenerated `build/` files.

## Add a new unit

1. Add a row to `data/units.csv` (kept sorted by `unit_id`). Choose the `unit_id` as `NATION-TYPE-NUMBER+ECHELONLETTER`, for example `US-INF-029D` (see [schema/README.md](schema/README.md)). For a battle group use `NATION-KG-NAME` (for example `GER-KG-FREY`) or a similar descriptive id, `echelon` `regiment/battle_group`, and set `parent_unit_id` to its parent division (the organic parent; each claim row then lists it as an `organic` relation in `data/command_relation_claims.csv`).
2. If the unit has claims, set `record_status` to `active` and create `data/claims/<nationality>/<unit_id>.csv` with the exact header used by the other files. If the unit already exists as a placeholder, create the claim file and run `python scripts/promote_placeholders.py`. If the unit exists only so others can point to it (a placeholder), set `record_status` to `placeholder`, create no file, and add `formed_date` and `formed_date_source` only if a source states it (see "Placeholder units" in [docs/methodology.md](docs/methodology.md)).
3. Parents: a claim's `parent_unit_id` must be a unit in `units.csv` (blank for a top-level headquarters, or when no parent was verified: then the claim lists one `unknown` placeholder relation, a row of `data/command_relations.csv` with a blank `higher_unit_id` and a note; never the text `unknown`) and it must be the higher unit of one of the relations the claim lists. Command relations are rows of `data/command_relations.csv` (one interval per relation: subject, higher unit, relationship, `valid_from`, `valid_to`, bases) linked to the claim by `data/command_relation_claims.csv` (`relation_id, claim_id, seq, role` and what the claim itself stated about the dates in the `stated_*` columns); the formation's name comes from `units.csv`, never from the table (see [schema/README.md](schema/README.md#command-relations)). A claim file has no `command_relationships` column; `build/all_claims.csv` rebuilds it. Re-use an existing relation when the claim restates it (extend its link rows), add a new one when it starts a new interval, give an end only when a source dates it, and run `python scripts/validate.py` and `python scripts/build.py`. If a parent formation is not in the table yet, add it as a placeholder unit first (`record_status` `placeholder`).
4. A unit's `unit_name`, `nationality`, `echelon`, `branch` and `theater` in every claim row must equal the values in `units.csv`, and `nationality` must be the `name` of a row of `data/nationalities.csv` (a new nation is added to that table first, with its unit id code, adjective and alliance).
5. Add a claim row (above) and validate.

## Add an operation

1. Check `data/operations.csv` first: the operation may exist under another name (`alt_names`) or as a parent you can use.
2. Add a row (kept sorted by `operation_id`). `operation_id` is `OP-` plus upper-case words and is never renamed or reused. Set `op_type`, the `parent_operation_id` (the smallest enclosing row: a battle goes under its operation, an operation under its CMH campaign; leave blank for a row that spans two campaigns, such as Lorraine), inclusive `start_date` and `end_date`, `date_basis`, `theater`, and `nationality_scope` (a German codename is its own row with scope `German`).
3. Cite where the dates come from in `reference_ids` (add the URL to `data/references_meta.csv`: `python scripts/build_references.py --add URL`, then edit the skeleton row; see the pull request checklist below) and use the CMH campaign streamer dates or an official history for `date_basis` where one exists. Where sources disagree on a boundary, pick one, say so in `notes` and cite both. A row with no source needs a note saying why (`date_basis derived`).
4. If the dates fall outside the parent's, fill `parent_date_exception` with the reason. Add the non-parent links to `data/operation_relations.csv` (`follows`, `concurrent_with`, `supports`, `succeeded_by`, `related`).
5. Point claims at the new row (`operation_id` in the claim files). A claim dated just outside the operation's dates that you want to keep goes in `data/operation_exceptions.csv` with a reason.
6. Run `python scripts/validate.py` and `python scripts/build.py`, and commit the data and the regenerated `build/` files. Only add operations that a claim needs, plus their parent chain.

## Per-row review checklist

Use this for every new row, and for each row in a spot check (the reviewer should check against a source the author did not use). Answer each point from the source, not from the existing row.

1. **Date.** Does the source put this unit at this place and in this action on this date (not the day before or after, not the day an order was given or a transfer took effect)?
2. **Place.** Is the point the place the source names, within `precision_km`? If it stands for a line, sector or route, is it a midpoint with a radius that covers it? Is `location_represents` honest (headquarters, main body, front-line point, objective, ...)?
3. **Action.** Does `current_activity` say only what the source says (no inferred direction, aim or result)? Is it one action? If several were documented, did you split the row or say in `notes` what is not documented?
4. **Opponent.** Is every unit in `engaged_with` placed in this fight by a source (and not in a different action the same day)?
5. **Parent and relationships.** Is `parent_unit_id` the operational parent on this date? Is the standing parent listed as `assigned`, `unspecified_subordination` or `unknown` (not `organic` for a division, corps or army under a higher headquarters), and does every named higher headquarters have a `unit_id`? Is an `attached` entry dated by `effective_from` when a source gives the day, and is it in force on the row's date? Is an independent brigade or battle group not recorded as an organic part of the formation it fought under?
5a. **Location and date.** Is the coordinate documented for the row's date? If it comes from a CP list or source dated otherwise, are `location_date`, `location_temporal_offset_days` and `location_basis` set (and the precision and confidence wide enough)? Is a headquarters coordinate really the headquarters (not the sector or objective), a landing point the landing area, and a corps or army sector not an exact front-line point? Do the rows of a conflict group describe the same event, and if not does each carry an `Event definition:` sentence in `notes`? Are the sources for event date, relationship, location and coordinates kept apart in `notes` (`Event date:`, `Relationship:`, `Location:`, `Coordinates:`)?
6. **Strength.** Does each figure cover what `scope` says (whole unit, sub-force, sector)? Is `basis` right (reported count, establishment, estimate)? Are conflicting figures from other sources in `note`? Is `strength_status` justified for the whole unit?
7. **Source, confidence and conflicts.** Does every cited source support this row's own claim? Does `confidence` follow the rubric after any change? If a source disagrees on date or place, is it a conflict group, and are the group's rows consistent with each other (including their coordinates)?
8. **Record the result.** Note what was checked, what changed (before and after) and what was left alone and why, in the pull request or a review note. Change only what a source supports.

## Run the checks

```bash
python scripts/validate.py              # errors fail the check; WARNING lines are prompts to re-check a row
python scripts/check_coordinates.py    # warnings only; add --geocode (network, 1 request/second) before a release
python scripts/build.py
git diff --stat build/        # build outputs must be committed with your change
python scripts/build.py --check
python scripts/build_references.py --check-links   # optional, network: re-check reference URLs (writes link_status into data/references_meta.csv; rerun build.py after)
python scripts/audit_command_location.py   # review prompts: command and location-date patterns
python scripts/audit_temporal_relationships.py   # read-only; nine cross-claim temporal checks (overlaps, undated transfers, sequences recorded as conflicts); add --out FILE for a markdown report
```

## How to cite a new source

Each claim lists the references behind it in `reference_ids`; the `source` text stays as the human-readable citation. For every source a row relies on:

1. Put its URL in the claim's `source` (` | ` between URLs, the coordinate note last) and say in `notes` what it supports.
2. Find its row in `data/references.csv` (search the URL). If it has none, add one: `python scripts/build_references.py --add URL` appends a skeleton row to `data/references_meta.csv` with the next `R###` id and a `source_family`. Edit the skeleton: `short_title`, `full_citation`, `source_type`, `publisher`, `license_or_status`, `reliability_note`, `used_for`. Keep `source_family` equal to the family of an existing reference when the new source republishes it or is Wikipedia (see `schema/vocabularies.json`); otherwise leave the host name.
3. Add the id to the claim's `reference_ids` (`R398;R407`). If the source gives a page, chapter or section, add it to `source_locator` (`R398: p. 285, 289; R407: p. 36`). A page in the URL fragment (`#page285`) is not enough on its own; write the locator.
4. If the source supports one part of the claim only (the date, the place, the command relationship, a strength figure), add a row to `data/claim_reference_roles.csv` (`claim_id,reference_id,role,basis`; role `event`, `date`, `location`, `command_relationship` or `strength`; `basis` says why). Leave it out when the source supports the claim as a whole.
5. A claim at `confidence` 0.9 needs references from at least two source families (Wikipedia, in any language, counts as one; so does everything republished from a CMH publication). A coordinate service such as Nominatim does not make a claim independently sourced; do not raise confidence on that basis.
6. Run `python scripts/validate.py` (errors: an unknown id, a claim without a reference, a URL in `source` whose reference is not in `reference_ids`), then `python scripts/build.py`.

## Pull request checklist

- [ ] Every new or changed row has a source URL and a `notes` entry saying what the source supports.
- [ ] Conflicting information is kept as separate rows with a shared `conflict_group_id`; exactly one `preferred` or all `disputed`.
- [ ] Nothing is invented; unknowns are `unknown` or blank.
- [ ] New `claim_id`s are unique and follow the highest existing id; none were reused.
- [ ] New units are in `data/units.csv` and the file name matches `unit_id`.
- [ ] `python scripts/validate.py` passes, and any WARNING lines for rows you touched are fixed or explained in `notes`.
- [ ] `python scripts/audit_command_location.py` was run and its counts for the new rows were reviewed.
- [ ] `python scripts/audit_temporal_relationships.py` was run and any finding that involves a new or changed row was checked against the source (a finding is a prompt, not an error; say in the pull request which are real and which are expected patterns).
- [ ] Every new row has an `operation_id` that exists in `data/operations.csv` (the most specific operation whose dates contain the row's date; the campaign row when no named operation applies). A new operation has its own row, dates, a source or a note, and a reference row (see "Add an operation").
- [ ] The per-row review checklist above was applied to every new or changed row (a second person checks 15 rows or 10% of a large batch, chosen by risk as described in `docs/methodology.md`).
- [ ] Every new source URL has a row in `data/references_meta.csv` (`python scripts/build_references.py --add URL` adds a skeleton to edit; `validate.py` fails without it), and every new row lists its references in `reference_ids` (with `source_locator` where a page is known; a 0.9 row cites two source families).
- [ ] `python scripts/build.py` was run and the `build/` changes (including `data/references.csv`) are committed.
- [ ] New vocabulary values (if any) are documented in `schema/vocabularies.json` and `schema/README.md`.
- [ ] Confidence and precision follow the rubric in `docs/methodology.md`.

Be kind: see the [code of conduct](CODE_OF_CONDUCT.md).
