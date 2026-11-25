# Contributing

Thank you for helping. This dataset is only useful if every row can be checked, so the rules are strict — but the path from a fork to a pull request is straightforward.

Work inside the `WorldWar2/` folder (the dataset, scripts and schema live there). Contributions are released under the same [CC BY-SA 4.0](../LICENSE) licence as the rest of the repository. Be kind: see the [code of conduct](CODE_OF_CONDUCT.md).

## Open a pull request

1. Fork [scottstarsman/UnitLocationData](https://github.com/scottstarsman/UnitLocationData) on GitHub, then clone your fork.
2. Keep your `main` up to date with the upstream repository, and cut a branch from it:
   ```bash
   git remote add upstream https://github.com/scottstarsman/UnitLocationData.git   # once
   git fetch upstream
   git checkout main
   git merge --ff-only upstream/main
   git checkout -b a-short-name-for-your-change
   ```
3. Add or edit rows under `WorldWar2/` (see the worked example and the sections below).
4. From `WorldWar2/`, run the full check set and regenerate the build:
   ```bash
   bash scripts/run_checks.sh
   python scripts/build.py
   git add data schema docs build
   ```
   Commit the data change and the regenerated `build/` files together. If `run_checks.sh` reports a problem, see [Run the checks](#run-the-checks).
5. Push the branch to your fork and open a pull request against `scottstarsman/UnitLocationData`, branch `main`. Use the [pull request checklist](#pull-request-checklist). CI will run a subset of the same checks on the pull request, including from forks.

If two open pull requests pick the same new identifiers, rebase onto the updated `main` and run `python scripts/renumber_new_ids.py` (dry-run, then `--apply`) so only the unpublished ids on this branch are remapped (see [Identifiers](#identifiers)). Maintainers may do that on merge.

## Rules

1. **Every row needs a source.** The claim's `source` column must hold at least one URL (separate several with ` | `). The coordinate source belongs to the place, not this column (see [Add a place](#add-a-place)). In `notes`, say what the source supports, and cite a page or chapter when you can. List the same sources in `reference_ids` (see [How to cite a new source](#how-to-cite-a-new-source)).
2. **Conflicting claims become separate rows.** If two sources disagree (date, place, commander, or anything else in the row), do not average or pick silently. Add one row per claim, give them the same `conflict_group_id` (next free `G###`), and set `claim_status`: one `preferred` and the others `alternate`, or all `disputed` if no source is better. Explain the disagreement in `notes` on each row.
3. **Never invent.** If a value is not in a source, write `unknown` (for text fields such as `commander`; for a parent that is not verified, leave `parent_unit_id` blank and record an `unknown` relationship) or leave the optional field blank. Do not guess numbers for `strength_json`. A gap is better than a plausible fabrication.
4. **One row is one claim** about one unit on one date. Rows are event-based; do not add filler rows for quiet days.
5. **Use the vocabularies** in `schema/vocabularies.json`. If you need a new value (for example a new country code), add it there and in `schema/README.md` in the same pull request, with a one-line definition. Theater values already cover the main fronts; see [How to add a new theater](#how-to-add-a-new-theater) before inventing a code.
6. **Keep ids stable.** Once an id has been on `main` it is never reused or renumbered. New rows take the next free number (the highest id in use, including retired ids, plus one). Do not delete a claim to "fix" it: correct it, or add a conflicting claim. A claim that has to leave the data is retired in `data/retired_claims.csv`.
7. **Command, strength and wording** are spelled out in [docs/methodology.md](docs/methodology.md). In short: `parent_unit_id` is the operational parent *on the row's date*; the standing parent goes in `data/command_relations.csv` as `assigned` (or `unspecified_subordination` when the source combines assigned and attached, as the CMH ETO-OB tables do — never turn that into `attached` without a source). `organic` is only for constituted components such as a battle group's own division. Do not write "attached" in `composing_text` or `engaged_note`; record the link as a command relation (or in `docs/deferred_relations.md` if the formation is not a unit of the table). A temporary link is `attached`, with `valid_from` and the claim's own statement in the `stated_*` columns of `data/command_relation_claims.csv`. A coordinate taken from another date needs `location_date` and `location_basis`. Every `personnel` figure needs a `scope`. One row describes one documented action, in the sources' words, with no inferred direction or result.
8. **Licensing.** Do not copy text from copyrighted sources. Facts and short quotations with attribution are fine.
9. **Note labels are a closed set.** A sentence of `notes` that starts with `Label: ` must use a label from the vocabulary `note_label` (`Event date`, `Event definition`, `Location`, `Relationship`, `Coordinates`, and the others listed in [schema/README.md](schema/README.md), "Note labels"). Lead-ins that name a source (`CMH ETO-OB chronology:`, `Wikipedia:`) are ordinary prose.
10. **Keep notes from copyrighted sources out of the repository.** Research notes or quote extracts stay private and are never committed. `.gitignore` already excludes `**/sources/*_notes.md`, `docs/sources/` and `private_notes/`. Cite the source by reference and page, with short quotes only.

## Sources and confidence

Prefer free, original-language sources (official histories, contemporary documents, published primary material) over later summaries. Wikipedia is useful for leads and coordinates, but **it is not a source family of its own** in the sense of "two families agree": every Wikipedia language counts as one family, and a Wikipedia page that summarises another work is not a second family next to that work.

Confidence is a 0–1 score for how well the sources support the date and the place, not a verdict on whether the event happened. Only four values are used; the full rubric is in [docs/methodology.md](docs/methodology.md):

| value | when to use it |
|---|---|
| 0.3 | A single source is enough to add a row, especially if the position is inferred or representative, or the date itself is approximate. A single source is also enough to create a unit. |
| 0.5 | An exact place with one secondary source, or an approximate place with one source family. A day-level date from one solid source often sits here when the place is exact. |
| 0.7 | An exact place with one authoritative source (for example a US Army official history), or an approximate place with two source families. The preferred claim of a conflict group is at most 0.7. |
| 0.9 | An exact place, and two independent source families agree. Alternate and disputed claims are at most 0.5, so they never reach 0.9. |

A gazetteer or geocoder (Nominatim, Wikipedia coordinates) does not make a claim independently sourced.

If you infer, extrapolate or change a value, say so in `notes`: the old value, the new value, and the reason (and record the same in the pull request or in `docs/changelog.md` when the change is structural). Do not leave an inferred start date or parent looking like a sourced fact.

## Identifiers

Public ids are unique, never reused, and not renumbered once they have been on `main`. New ids are the highest number already in use (including retired ids) plus one. Gaps left by an abandoned branch are skipped; nobody fills them later.

| Kind | Pattern | Next free |
|---|---|---|
| Claim | `C####` | `python scripts/check_claim_ids.py` |
| Mission | `MSN####` | `python scripts/check_mission_ids.py` |
| Person / tenure | `PE####` / `UC####` | `python scripts/check_commander_ids.py` |
| Reference | `R###` | `python scripts/build_references.py --add URL` assigns it |
| Command relation, place, reference, conflict group, TO&E, aircraft type, ship class, lineage | `CR####`, `PL####`, `R###`, `G###`, `TT####`, `UT####`, `AT###`, `SC###`, `UL###` | `python scripts/check_other_ids.py` (also prints the next free id of each, except lineage; `renumber_new_ids.py` covers `UL###`) |
| Operation | `OP-` plus upper-case words | Choose a unique name; never rename or reuse one |

`python scripts/check_claim_ids.py`, `check_mission_ids.py`, `check_commander_ids.py` and `check_other_ids.py` compare your branch with `origin/main`. `run_checks.sh` runs them when `origin/main` is available, and CI runs them on every pull request (including from forks) after fetching the base `main`. If two branches took the same new numbers, rebase onto the updated `main`: the id checks will fail until the unpublished ids on the second branch are remapped. Run `python scripts/renumber_new_ids.py` to see the mapping, then commit your work (the tree must be clean) and run `python scripts/renumber_new_ids.py --apply`. `--apply` remaps on a temporary copy, runs the id and foreign-key checks, and writes the files only if those checks pass; otherwise the work tree is left unchanged. It rewrites references in the new or changed rows, and in lines this branch adds to the changelog, docs and semantic tests. Ids already on `main` are never changed. Then run `python scripts/build.py` and commit `build/`. If this branch meant to add members to a conflict group that already exists on `main`, pass `--keep-group G###` so that group is not split.

**The identity of a claim is its `claim_id`.** A claim keeps its id when it is corrected. The combination `(unit_id, date, event_type)` is a guard against entering the same claim twice. A unit has at most one claim per date and event type, unless the sources disagree (put both rows in one conflict group) or the unit really did two actions of the same kind on the same day (list the pair with a reason in `data/claim_key_exceptions.csv`). The validator names both claim ids when this fails.

A claim that has to leave the data is removed from its file in the same change that adds a row to `data/retired_claims.csv`. Correct a wrong claim, or contradict it with a conflicting claim; do not retire it only because it is incomplete.

## Worked example

The rows below are a **teaching example**. They show the shape of a new unit, a place, a source, a command relation and a claim. **Do not add these rows to the dataset.** The identifiers (`Cxxxx`, `PLxxxx`, `Rxxxx`, `CRxxxx`, `IT-INF-EXAMD`) are not real and must not be copied. When you add a real unit, take the next free ids from the scripts above, and use the exact column headers already in the files (leave unused optional columns blank).

Suppose a source places an Italian infantry division at a named town in Sicily on 10 July 1943, under a named corps. The claim belongs in theater `mediterranean`, under the existing umbrella `OP-FRONT-MEDITERRANEAN` until a more specific Sicily operation exists.

1. **Source.** Add a reference (or reuse one that is already in `data/references_meta.csv`):

   ```bash
   python scripts/build_references.py --add https://example.example/official-history
   ```

   Then edit the new skeleton in `data/references_meta.csv`: `short_title`, `full_citation`, `source_type`, `publisher`, `license_or_status`, `used_for`. Keep `source_family` equal to an existing family when the work republishes one; otherwise leave the host name.

2. **Unit.** Append a row to `data/units.csv` (kept sorted by `unit_id`) and create an empty claim file with the standard header:

   - `unit_id`: `IT-INF-EXAMD` (nation code `IT`, type `INF`, a number, echelon letter `D` for division — see [schema/README.md](schema/README.md#unit_id-pattern))
   - `unit_name`, `nationality` `Italy`, `echelon` `division`, `branch`, primary `theater` `mediterranean`, `domain` `ground`, `scope` `in_scope`, `record_status` `active`
   - File: `data/claims/italy/IT-INF-EXAMD.csv`

   If the parent corps is not in the table yet, add it first as a `placeholder` unit (no claim file).

3. **Place.** If the town is not already in `data/places.csv`, append a place (`PLxxxx`), with coordinates from a gazetteer, `coord_reference_id` (often `R002` for Nominatim), `country` `IT`, and a `kind` of `point`.

4. **Command relation.** Add an interval to `data/command_relations.csv` (`CRxxxx`: subject `IT-INF-EXAMD`, higher unit the parent corps, `relationship` `assigned`, `valid_from` the sourced date, `valid_from_basis` as the source supports, `valid_to` blank if the end is not sourced). Link it to the claim in `data/command_relation_claims.csv` (`relation_id`, `claim_id`, `seq` `1`, `role`).

5. **Claim.** Add one row to the unit's claim file, sorted by `date` then `claim_id`. The important fields look like this (every other header column is present and may be blank):

   | field | example value |
   |---|---|
   | `claim_id` | `Cxxxx` (next free, not this token) |
   | `claim_status` | `preferred` |
   | `unit_id` | `IT-INF-EXAMD` |
   | `date` | `1943-07-10` |
   | `theater` | `mediterranean` (the theater of *this row*, which must match the operation; it may differ from the unit's primary theater) |
   | `nationality` / `unit_name` / `echelon` / `branch` | same as `data/units.csv` |
   | `parent_unit_id` | the corps, which must be the higher unit of a relation listed on this claim |
   | `place_id` / `latitude` / `longitude` | the place's id and its exact coordinates |
   | `location_represents` | `headquarters` or whatever the source actually describes |
   | `precision_km` | a radius the source supports |
   | `operation_id` | `OP-FRONT-MEDITERRANEAN` |
   | `confidence` | `0.5` or `0.3` for a single source, following the rubric above |
   | `source` | the source URL |
   | `reference_ids` / `source_locator` | `Rxxxx` and a page, for example `Rxxxx: p. 12` |
   | `event_type` / `current_activity` | only what the source says happened |
   | `notes` | what the source supports, labelled where useful (`Event date:`, `Location:`, …) |

6. **Checks.** From `WorldWar2/`:

   ```bash
   bash scripts/run_checks.sh
   python scripts/build.py
   ```

   Commit the new and edited files under `data/` together with the regenerated `build/` outputs. Then push and open the pull request.

## Add a claim to an existing unit

1. Open `data/claims/<nationality>/<unit_id>.csv`.
2. Add a row with the next free `claim_id`, all columns filled as described in [schema/README.md](schema/README.md), and insert it in order (sorted by `date`, then `claim_id`).
3. Place: find the place in `data/places.csv` (search the name and the `alt_names`) and put its `place_id` in the row; put the claim-specific words ("vicinity", "division HQ") in `location_qualifier`, not in a new name. Use the place's `latitude` and `longitude` exactly. If the place is not in the table, add it (see below). Never write a free-text place name in a claim.
4. Run `bash scripts/run_checks.sh`, then `python scripts/build.py`. Commit both the data change and the regenerated `build/` files.

## Add a place

1. Append a row to `data/places.csv` with the next free `place_id` (`PL####`, sorted; ids are never reused). `name` is the canonical name, unique ignoring case ("Name, administrative area" for a settlement); other spellings go in `alt_names` separated by `; ` (an alias must not be another place's name).
2. `kind`: `point` for a named settlement or site; `area` for a named area, sector, beach, zone or bridgehead; `line` for a front, axis or route. A sector represented by the centre of a town is its own place, not an alias of the town.
3. `latitude` and `longitude` are the point every claim at the place uses. Read them from the coordinate service and set `coord_reference_id` to it (`R001` Wikipedia article coordinates, `R002` OpenStreetMap Nominatim) with the article or query in `coord_source_note`. A point worked out by hand has a blank `coord_reference_id` and says how in `coord_source_note`. `country` and `region` come from where the point lies (vocabulary `country`; add a code there when you add a place in a new country).
4. A claim whose own point differs from the place's keeps its point and gives the reason in `coord_override`. The validator requires the point to equal the place's exactly when `coord_override` is blank, and to be within 5 km when it is set. Farther than that is a different place.
5. Run `python scripts/validate.py` and `python scripts/check_coordinates.py` (its `--duplicates` option lists point-places within 1 km of each other), then `python scripts/build.py`.

## Add a new unit

Flak units and coastal artillery are domain `ground` whatever service owned them (Luftwaffe flak, Kriegsmarine coastal batteries); the `branch` column records the service. Use `air` only for flying units and air commands, and `naval` only for ships and naval commands. Air and naval id patterns, echelons and class/type tables are in [schema/README.md](schema/README.md) and [docs/air_naval_pilot.md](docs/air_naval_pilot.md) section 8.

A claim for a unit outside the current surveyed focus (any domain, front or period) is still recorded when a source gives it. It follows every normal claim rule and stays in the unified `build/` files. In this release every unit is `scope` `in_scope`; incidental other-front rows are distinguished by the claim's `theater` (and sometimes `operation_id`), not by marking the unit `out_of_scope`. A later pass may mark a unit `out_of_scope` if the unit itself lies outside the surveyed set; the who_controls grid still defaults to in-scope ground subjects. Coverage figures for incidental rows should be labelled incidental, not surveyed.

Resistance groups, partisan bands and other irregular forces get unit entries only once they are organised into formal military units with a command chain. Loose cells and networks are not entered as units. Formal units still follow the small-unit rule in [schema/README.md](schema/README.md) (units below regiment size need a traced parent).

1. Add a row to `data/units.csv` (kept sorted by `unit_id`). Choose the `unit_id` as `NATION-TYPE-NUMBER+ECHELONLETTER`, for example `US-INF-029D` (see [schema/README.md](schema/README.md#unit_id-pattern)). Regiments, battle groups and battalions have no echelon letter. The validator rejects an id that ends in an echelon letter that does not match the echelon. For a battle group use `NATION-KG-NAME` (for example `GER-KG-FREY`), `echelon` `regiment/battle_group`, and set `parent_unit_id` to its parent division (the organic parent).
2. If the unit has claims, set `record_status` to `active` and create `data/claims/<nationality>/<unit_id>.csv` with the exact header used by the other files. If the unit already exists as a placeholder, create the claim file and run `python scripts/promote_placeholders.py`. If the unit exists only so others can point to it, set `record_status` to `placeholder`, create no file, and add `formed_date` only if a source states it.
3. Parents: a claim's `parent_unit_id` must be a unit in `units.csv` (blank for a top-level headquarters, or when no parent was verified: then the claim lists one `unknown` relation — a row of `data/command_relations.csv` with a blank `higher_unit_id` and a note). It must be the higher unit of one of the relations the claim lists. Command relations are rows of `data/command_relations.csv`, linked to the claim by `data/command_relation_claims.csv`. The formation's name comes from `units.csv`. A claim file has no `command_relationships` column; `build/all_claims.csv` rebuilds it. If a parent formation is not in the table yet, add it as a placeholder first.
4. On every claim row, `unit_name`, `nationality`, `echelon` and `branch` must equal the values in `units.csv`. `nationality` must be the `name` of a row of `data/nationalities.csv` (add a new nation to that table first, with its unit-id code and adjective, and its dated sides in `data/nation_allegiance.csv`). **`theater` is per claim:** it is the front of that row's place and date, and it must equal the `theater` of the row's `operation_id`. It may differ from the unit's primary `theater` in `units.csv`.
5. Add a claim row (above) and run the checks.

## Add an operation

1. Check `data/operations.csv` first: the operation may exist under another name (`alt_names`) or as a parent you can use.
2. Add a row (kept sorted by `operation_id`). `operation_id` is `OP-` plus upper-case words and is never renamed or reused. Set `op_type`, the `parent_operation_id` (the smallest enclosing row: a battle goes under its operation, an operation under its campaign; leave blank for a row that spans two campaigns, such as Lorraine), inclusive `start_date` and `end_date`, `date_basis`, `theater`, and `nationality_scope`. `nationality_scope` is a `name` from `data/nationalities.csv` (for example `Germany`, `Allied`) or `All`. A German codename is its own row with scope `Germany`.
3. Cite where the dates come from in `reference_ids` (add the URL with `python scripts/build_references.py --add URL`, then edit the skeleton). Use official campaign dates or an official history for `date_basis` where one exists. Where sources disagree on a boundary, pick one, say so in `notes` and cite both. A row with no source needs a note saying why (`date_basis derived`).
4. If the dates fall outside the parent's, fill `parent_date_exception` with the reason. Add non-parent links to `data/operation_relations.csv` (`follows`, `concurrent_with`, `supports`, `succeeded_by`, `related`).
5. Point claims at the new row. A claim dated just outside the operation's dates that you want to keep goes in `data/operation_exceptions.csv` with a reason.
6. Run the checks and commit the data and the regenerated `build/` files. Only add operations that a claim needs, plus their parent chain.

## How to add a new theater

The surveyed focus of this release is the Western Front, 6 June 1944 to 8 May 1945, but other fronts are welcome. The two-level list of theaters and sub-theaters, with bounding boxes, date floors and official equivalents, is [`schema/theaters.json`](schema/theaters.json), described in [docs/theaters.md](docs/theaters.md). **Do not invent a new code until you have checked that list.** Most new work uses an existing theater (and, if it helps, a sub-theater) rather than adding a code.

**Theater and sub-theater fields.** Each claim row has its own required `theater`: the front or rear area where the unit was on that date. The unit table also has a `theater`, which is only the unit's primary theater and may differ from a given claim. The claim's `operation_id` must have the same `theater` as the claim (the validator errors otherwise). An optional `sub_theater` names a child of that theater (for example `italy` under `mediterranean`). Existing rows may leave it blank. If both the claim and the operation set `sub_theater`, they must be equal; a claim may fill in a sub-theater when the holding umbrella does not have one.

**Current top-level theaters:** `western_europe`, `mediterranean`, `eastern_front`, `pacific`, `cbi`, `atlantic`, `arctic`, `home_front`, `other`. Four older codes remain valid in the `theater` column because they are already used in published rows; they are now classified as sub-theaters: `north_africa` (parent `mediterranean`), `balkans` (parent `mediterranean`), `scandinavia` (parent `arctic`), `home_germany` (parent `home_front`). New rows may keep those legacy values, or use the parent theater plus `sub_theater`. Use `other` only when nothing else fits, and explain in `notes`. The full child list is in [docs/theaters.md](docs/theaters.md).

**Holding umbrellas** (operations of type `umbrella`, `date_basis` `derived`) give a home to claims that are not yet under a named campaign:

- `OP-PRE-INVASION` and `OP-POST-SURRENDER` are `western_europe` only.
- Other fronts: `OP-FRONT-EASTERN`, `OP-FRONT-MEDITERRANEAN`, `OP-FRONT-BALKANS`, `OP-FRONT-SCANDINAVIA`, `OP-FRONT-NORTH-AFRICA`, `OP-HOME-GERMANY`, `OP-FRONT-PACIFIC`, `OP-FRONT-CBI`, `OP-FRONT-ATLANTIC`, `OP-FRONT-ARCTIC`, `OP-FRONT-HOME`, `OP-FRONT-OTHER`.

A child operation keeps its parent's theater. Official campaign streamers in this release are Western Front campaigns; rows of other theaters do not need one.

**If you need a new sub-theater** (for example a named island group that is not already in the list): add it to `schema/theaters.json` with `level` `sub_theater`, its parent, a loose bounding box, a date floor, an official span and a cited source, and add the same code to the `sub_theater` vocabulary in `schema/vocabularies.json` and a one-line definition in `schema/README.md`. Do not put a new sub-theater code in the `theater` column.

**If you need a new top-level theater** (rare): do the same with `level` `theater` and `allowed_as_theater` true, add the code to the `theater` vocabulary, add a holding umbrella `OP-FRONT-…` in `data/operations.csv` in the same pull request, and add any new nation or country codes you actually use. Open an issue with the new-theater form first if you can.

**Identifiers** are global, not per theater: take the next free `C####`, `PL####`, `CR####` and so on, as in [Identifiers](#identifiers). There is no theater-specific number range. If your pull request lands after another that used the same new numbers, maintainers may renumber your unpublished ids. Search `units.csv` before inventing a `unit_id`; if two pull requests propose the same unpublished unit id, the later one changes it.

**Date floors** are per theater, from `schema/theaters.json`. The global earliest date is 7 July 1937 (China / CBI, the Marco Polo Bridge incident). Most European theaters accept claims from 1 September 1939; `atlantic` from 3 September 1939; `pacific` from 1 July 1941 (so pre-Pearl Harbor garrison rows are allowed). A China row dated 7 July 1937 is accepted; a Western Europe row on that date is an error.

**Checks and tests.** `scripts/check_coordinates.py` uses the bounding boxes in `schema/theaters.json`, including `atlantic` and `other` and both sides of the Pacific antimeridian. A mid-Atlantic point in theater `atlantic` is expected and is not treated as a typo. A known, sourced exception still goes in `data/coordinate_exceptions.csv`. `scripts/semantic_tests.py` pins the expected answers for many existing units; adding a new theater's rows should not fail it unless you also change a unit those tests already cover. If you change such a unit on purpose, change the expectation in the same commit and say why.

## How to cite a new source

1. Put its URL in the claim's `source` (` | ` between URLs) and say in `notes` what it supports.
2. Find its row in `data/references.csv` (search the URL). If it has none, add one: `python scripts/build_references.py --add URL` appends a skeleton row to `data/references_meta.csv` with the next `R###` id and a `source_family`. Edit the skeleton as in the worked example.
3. Add the id to the claim's `reference_ids` (`R398;R407`). If the source gives a page, chapter or section, add it to `source_locator` (`R398: p. 285, 289`). A page in the URL fragment (`#page285`) is not enough on its own.
4. If the source supports one part of the claim only (the date, the place, the command relationship, a strength figure), add a row to `data/claim_reference_roles.csv`. Leave it out when the source supports the claim as a whole. Do not add a row for a coordinate service (`R001`, `R002`): its `location` role is derived.
5. A claim at `confidence` 0.9 needs references from at least two source families. The validator ignores `gazetteer_geocoder` references when it counts families.
6. Run the checks, then `python scripts/build.py`.

## Run the checks

From `WorldWar2/`, start with the one-command set:

```bash
bash scripts/run_checks.sh
```

That is the set to run before you open a pull request. It is read-only aside from writing to `/tmp`. It stops with `CHECKS FAILED` and a list of steps if something is wrong, or prints `ALL CHECKS PASSED`.

| Step | What it does | If it fails |
|---|---|---|
| `python scripts/validate.py` | Schema, vocabularies, foreign keys, claim identity, sources, operations, and many consistency rules. Errors fail the check. `WARNING` lines are prompts to re-check a row, not automatic failures. Some warnings are already open on `main`; do not add a new warning for a row you touched unless the pull request explains why. | Read the `ERROR` line: it usually names the file, the id and what to fix (for example two claims with the same unit, date and event type). |
| `python scripts/check_json_fields.py` | JSON-in-cell fields (`strength_json` and others) match the schemas in `schema/json/`. | Fix the JSON in that cell so it matches the schema. |
| `python scripts/semantic_tests.py` | Pins expected answers of `who_controls.py` and other fixtures for a large set of existing units (not just a handful of scenarios). Fails CI. | If you did not mean to change that unit, revert the accidental edit. If you changed it on purpose, update the expectation in the same commit and say why. |
| `python scripts/build.py --check` | The committed `build/` files match a fresh build. | Run `python scripts/build.py` and commit the result (including `docs/coverage.md` and `data/references.csv` when they change). |
| `python scripts/build_references.py --check` | Reference rows are complete and consistent. | Fill the missing citation fields, or add the reference the claim cites. |
| `python scripts/review_sample.py --check` | The committed review sample is up to date. | Only relevant if you changed the review-sample inputs; regenerate it as the script says. |
| `python scripts/check_coordinates.py` | Offline coordinate sanity (theater bounding box, speed, and others). Warnings only; it does not fail `run_checks.sh` on warnings. | Re-check the point or date. A known, sourced exception goes in `data/coordinate_exceptions.csv` with a reason. `--geocode` (network) is optional and should not be run in CI. |
| `python scripts/audit_command_location.py` and `python scripts/audit_temporal_relationships.py` | Read-only review prompts (command patterns, overlaps, undated transfers). | A finding is a prompt, not an error. In the pull request, say which findings on rows you touched are real and which are expected. |
| `python scripts/check_claim_ids.py`, `check_mission_ids.py`, `check_commander_ids.py`, `check_other_ids.py` | Ids (claims, missions, people, tenures, command relations, places, references, conflict groups, TO&E, aircraft types, ship classes) were not reused or dropped since `origin/main`. Skipped if `origin/main` is not available. They also print the next free ids. | You dropped or reused a published id: restore or retire it. If the only problem is a collision with `main`, rebase onto the updated `main` and run `python scripts/renumber_new_ids.py` (then `--apply`), or take unused ids by hand. |

After the script passes, run `python scripts/build.py` if you have not already, and commit `build/`. Optional, needs network: `python scripts/build_references.py --check-links` re-checks reference URLs (then run `build.py` again).

GitHub Actions runs on every pull request, including from forks (`validate.py`, `check_json_fields.py`, `build.py --check`, `semantic_tests.py`, and the id-collision checks against the pull request's base `main`; coordinate and temporal audits run but do not fail the job). The workflow uses the `pull_request` event, a read-only token and no secrets. Please still run `bash scripts/run_checks.sh` locally when you can, so you see a failure before you push.

## Per-row review checklist

Use this for every new row, and for each row in a spot check (the reviewer should check against a source the author did not use). Answer each point from the source, not from the existing row.

1. **Date.** Does the source put this unit at this place and in this action on this date (not the day before or after, not the day an order was given or a transfer took effect)?
2. **Place.** Is the point the place the source names, within `precision_km`? If it stands for a line, sector or route, is it a midpoint with a radius that covers it? Is `location_represents` honest (headquarters, main body, front-line point, objective, …)?
3. **Action.** Does `current_activity` say only what the source says (no inferred direction, aim or result)? Is it one action?
4. **Opponent.** Is every unit in `engaged_with` placed in this fight by a source? Use unit ids; a named unit that is not in `data/units.csv` is added there as a placeholder first. Formations that cannot be a unit go in `engaged_note`.
5. **Parent and relationships.** Is `parent_unit_id` the operational parent on this date? Is the standing parent listed as `assigned`, `unspecified_subordination` or `unknown` (not `organic` for a division, corps or army under a higher headquarters)?
5a. **Location and date.** Is the coordinate documented for the row's date? If it comes from a list dated otherwise, are `location_date` and `location_basis` set? Do the rows of a conflict group describe the same event?
6. **Strength.** Does each figure cover what `scope` says? Are conflicting figures from other sources noted?
7. **Source, confidence and conflicts.** Does every cited source support this row? Does `confidence` follow the rubric? If a source disagrees, is it a conflict group?
8. **Record the result.** Note what was checked, what changed (old value, new value, reason) and what was left alone and why, in the pull request. Change only what a source supports.

A second person should check 15 rows, or 10% of a large batch, chosen by risk as described in `docs/methodology.md`.

## Pull request checklist

- [ ] Every new or changed row has a source URL and a `notes` entry saying what the source supports.
- [ ] Conflicting information is kept as separate rows with a shared `conflict_group_id`; exactly one `preferred` or all `disputed`.
- [ ] Nothing is invented; unknowns are `unknown` or blank. Inferred or changed values give the old value, the new value and the reason.
- [ ] New ids are unique and follow the highest id in use (including retired ids); none were reused; a removed claim has a row in `data/retired_claims.csv`; `python scripts/check_claim_ids.py` passes.
- [ ] No new row repeats a unit's date and event type unless it is in a conflict group with the existing claim or listed with a reason in `data/claim_key_exceptions.csv`.
- [ ] Every sentence of `notes` that starts with `Label: ` uses a label of the vocabulary `note_label`.
- [ ] New units are in `data/units.csv` and the file name matches `unit_id`. Claim `theater` matches the row's operation (and may differ from the unit's primary theater).
- [ ] `bash scripts/run_checks.sh` passes, and any `WARNING` lines for rows you touched are fixed or explained in `notes` or the pull request.
- [ ] The command-location and temporal audits were looked at for new or changed rows (a finding is a prompt; say in the pull request which are real).
- [ ] Every new row has an `operation_id` that exists in `data/operations.csv`. A new operation has dates, a source or a note, and a reference row.
- [ ] Every new source URL has a row in `data/references_meta.csv`, and every new row lists its references in `reference_ids`.
- [ ] `python scripts/build.py` was run and the `build/` changes are committed.
- [ ] New vocabulary values (if any) are documented in `schema/vocabularies.json` and `schema/README.md`.
- [ ] Confidence and precision follow the rubric above and in `docs/methodology.md`.
