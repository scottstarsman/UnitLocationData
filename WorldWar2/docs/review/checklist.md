# Review checklist

Work through the areas in any order. Each item says what to look at and, where useful, how to test it. For each problem write a finding ([findings_template.md](findings_template.md)); for each item you could not check, say so. Item ids (A1, C3, ...) can be used in findings. Read [README.md](README.md) first (scope, table map, known limitations).

Commands run from the dataset folder (`WorldWar2/` in the GitHub repository), Python 3.8+, standard library only. A reader without Python can use the CSV files in `build/` and `data/` directly.

## A. Schema and normalization

- A1. Does every table have a clear grain (what one row is) and a key? Are there tables that mix two grains? (`schema/README.md`, `schema/*.schema.json`)
- A2. Is any fact stored twice, so that two copies could disagree? Candidates: the place's point and the claim's own `latitude` / `longitude`; `parent_unit_id` and the command relations; `source` (URLs) and `reference_ids`; `build/` against `data/`.
- A3. Is any column doing two jobs, or holding a list or structured text in a cell (`engaged_with`, `composing_units`, `reference_ids`, `source`, `strength_json`, the free-text `notes` with labelled sentences)? Is each such choice documented, and is it the right trade-off for a CSV-first dataset?
- A4. Are the keys stable and meaningful? `unit_id` encodes nationality, type, number and echelon letter; `claim_id` and `relation_id` are opaque counters; `place_id` is a counter with a retired list. Are these rules consistent (`CONTRIBUTING.md`, "Claim identity")?
- A5. Is the claim key `(unit_id, date, event_type)` the right natural key? Look for pairs that are different events with the same key, and the same event under two keys.
- A6. Are empty values, `unknown` and not-applicable used consistently (`schema/README.md`, "Free-text conventions")?
- A7. Are the CSV conventions followed in every file (UTF-8, LF, header, quoting, ISO dates, lowercase booleans)? Try `python scripts/validate.py` and open two or three files in a tool of your choice.

## B. Referential integrity

- B1. Does every foreign key resolve? The keys are listed in `schema/README.md`, "Foreign keys", and enforced by `python scripts/validate.py` (expect 0 errors, 3 warnings). Beyond what the validator checks: do any ids appear in free text (`notes`, `composing_text`, `engaged_note`, `docs/`) that are not in the tables?
- B2. Retired ids: are `data/place_merges.csv` and `data/retired_claims.csv` consistent with the data? (No retired place id is used by a claim; the survivors exist; no claim id is reused.)
- B3. Are the derived files faithful? `python scripts/build.py --check` and `python scripts/build_references.py --check` should pass; compare a few rows of `build/all_claims.csv` with the claim file they come from.
- B4. Does every unit that has claims have a row in `units.csv`, and every claim file belong to the unit named in it? Are there units that should be active (they have claims) or placeholders that are referred to as parents or opponents without being in the table?
- B5. Are the placeholder units a sound design (a unit exists in the table, with an `initial_parent_*` listing, before it has any claim)?

## C. Evidence and provenance quality

This is the most useful check and the one that needs the sample: see "Sampled rows" below.

- C1. Does each cited source support the claim it is attached to: the unit, the date, the place, the event, the command relationship, the commander, the strength figure, the opponent?
- C2. Where a claim cites several sources, does each support the part it is cited for? (`data/claim_reference_roles.csv` records the role only where a source supports one part.) Is any source cited that does not mention the unit at all?
- C3. Is the page or locator enough to find the passage? (`source_locator` and `reference_ids`; `references.csv` has the link, the type, the licence and a reliability note.)
- C4. Does `notes` say only what the sources say? Look for inference stated as fact (direction of movement, aim, result, a headquarters place taken from a neighbouring unit) and for wording that is not marked as inferred. Are the labelled sentences (`Event support:`, `Location support:`, `Relationship:` ...) accurate about what is documented and what is not?
- C5. Are source families counted correctly for the confidence rubric (several Wikipedia pages are one family; a compilation of the CMH table is not independent of it)?
- C6. Do the links work, and do the archive copies show the cited text? (Some sites block automated readers; 10 links are known unreadable; say so rather than reporting a dead link.)
- C7. Are conflict groups real disagreements between sources? Is the preferred claim the better supported one, and does the note say why? (`docs/methodology.md`, "Conflict policy".)

## D. Geography and coordinates

- D1. Is each claim's point the place it names, within `precision_km`? Check on a map (the `build/claims.geojson` file opens in geojson.io or QGIS; `build/places.geojson` for the places).
- D2. Is `location_represents` honest for the row (a headquarters point, a sector centre, a front-line point, an objective)? Are representative points marked as such and kept at low confidence?
- D3. The place model: places with kind point, area or line; `location_qualifier`; `coord_override`; retired and merged places. Is it sufficient to answer "where was this unit" without inventing precision? (`schema/README.md`, "places columns"; `docs/places_review.md`.)
- D4. Same place under several names, different places under one name, wrong country or region, a name that does not match its point (known: PL0285, PL0314, C0006; see the brief). Search for more with `python scripts/check_coordinates.py` and by sorting `data/places.csv` by coordinates.
- D5. Does a coordinate document the row's date? (`location_date`, `location_basis`, and the derived offset in days.) Is a headquarters point really the headquarters at that date?
- D6. Is the time between consecutive claims of one unit consistent with its movement (the speed check)?

## E. Command relations and dates

- E1. Is the relations model coherent: one row per subject, higher unit and relationship with a dated interval; evidence as links to claims; contradictions kept as documented overlaps, not resolved? (`schema/README.md`, "Command relations"; `docs/methodology.md`.)
- E2. Pick a unit and a date and ask `python scripts/who_controls.py <unit_id> <date>`; check the answer against a source. Does the tool say "possible" or "unknown" where the data cannot decide?
- E3. Are the relationship values used the way their definitions say (`attached` against `operational_control` against `assigned`; `unspecified_subordination` where a table does not say)? Is `organic` used only where a unit belongs to a parent by its own organisation?
- E4. Start and end dates: are the `valid_from` / `valid_to` bases (order, assignment table, narrative, inferred, claim date, inferred from next claim, open at last claim) honest? Is a table observation ever treated as an operational transfer date?
- E5. Inclusive end dates and same-day changes: are two relations that meet on one day handled consistently? Look at the documented overlaps (19) and at the `parent_unit_id` of claims on the day of a change.
- E6. Is `parent_unit_id` on a claim consistent with the relation in force on the claim's date? (`python scripts/audit_temporal_relationships.py` lists what it finds.)
- E7. The deferred relations (D01 to D11): is it right to keep them outside the table until their subordinates become units?

## F. Confidence rubric consistency

- F1. For each sampled claim, recompute the confidence from the rubric (`docs/methodology.md`, "Confidence rubric"; `schema/vocabularies.json`, `confidence`) using what the row cites: is the exactness of the location, and the number of independent source families, what the rubric needs for the level given?
- F2. Are the caps applied (a preferred claim of a conflict group at most 0.7; alternate and disputed at most 0.5)?
- F3. Is confidence about the claim's date and place only (as stated), and is that clear to a user? Does any row mix in the event or the importance of the unit?
- F4. Four levels, applied by rule: is this sufficient and comparable across nationalities and sources of different kinds (a CMH table, a Wikipedia article, a memorial)?
- F5. Do the confidence levels correlate with `precision_km` and `location_basis` in a sensible way? (Sort `build/all_claims.csv` by confidence.)

## G. Vocabulary and controlled lists

- G1. For each vocabulary in `schema/vocabularies.json`: are the values mutually exclusive and complete for the scope? Are the definitions enough to apply them without asking the authors? Are values defined but unused, or used with a different meaning than defined?
- G2. `event_type`: is it one concept (what happened) or several (a landing, an arrival, a command change, a headquarters move)? Is `other` used as a dumping ground (32 claims)?
- G3. `echelon` and `branch`: is the split between size and kind clean (an `Armoured` division is `echelon` division, `branch` Armoured)? Do the values scale to air and naval units?
- G4. The note labels: 19 labels, a closed set. Are the labels used consistently by the sentences that carry them? Is a closed set of labels in free text a good design, or should those be columns or a table?
- G5. Do the validators reject what the documents say they reject? (Try editing a scratch copy.)

## H. Documentation clarity

- H1. Can a new reader find out what a row means from `README.md`, `schema/README.md` and `docs/methodology.md` alone? Which terms are used before they are defined?
- H2. Are the documents consistent with each other and with the data (numbers, column names, rules)? Please report contradictions with both places quoted.
- H3. Is `CONTRIBUTING.md` enough to add a claim correctly (the per-row checklist; the claim key; claim ids; note labels)?
- H4. Are the limits of the data stated where a user will see them (the scope, the nature of the coordinates, the nature of confidence)?
- H5. Is `docs/changelog.md` useful as a history, and are the open items findable?

## I. Usability for researchers

- I1. Try three real questions with only `build/all_claims.csv` or `build/claims.geojson` (and a spreadsheet, SQL, pandas or QGIS): where was a named division on a date; which units were near a place in a week; who commanded a corps in September 1944. Which are easy, which hard, which impossible?
- I2. Is the claim-based form (several rows for one unit-date when sources disagree, a preferred / alternate / disputed status) easy to use correctly, or does a naive query double count?
- I3. Are the joins needed for a typical question documented, and do they work (claims to units, places, operations, relations, references)?
- I4. Is the dataset citable and reusable: identifiers, a stable format, the licence and the terms of each source per row?
- I5. Is there anything a researcher would expect (a coordinate reference system note, an uncertainty field, a unit history, a gazetteer link) that is missing?

## J. Reproducibility

- J1. Can you rebuild the derived files and get identical bytes? `python scripts/build.py` then `git status` should show no change; `python scripts/build.py --check` and `python scripts/build_references.py --check` pass.
- J2. Does the validator run with the standard library only, on a clean checkout, on your Python version? Does the pull-request workflow (`.github/workflows/validate.yml`) run the same checks?
- J3. Can the sample be redrawn? `python scripts/review_sample.py --check` passes; `python scripts/review_sample.py --seed 7` writes another draw (to a scratch copy; do not commit it).
- J4. Are all scripts either documented in `README.md` and used, or marked as one-off migrations? Could anyone reproduce a migration from its script and the commit it ran on?
- J5. Is it possible to see why a value changed? (git history, `docs/changelog.md`, the retired lists.)

## Sampled rows

[sample.md](sample.md) lists 40 claims (S01 to S40) and 20 command relations (R01 to R20) that were drawn by `scripts/review_sample.py` with a fixed seed (see its header and the script's docstring for the draw). The same rows are in `sample_claims.csv` and `sample_relations.csv` with `reviewer_verdict` and `reviewer_comment` columns for your answers. The columns are filled in with our own verification of 26 October 2026 ([verification_results.md](verification_results.md)); a reviewer can use them as a second opinion to compare with, or check the rows again.

For each sampled **claim**, with the cited source open:

1. **Unit.** Does the source name this unit (and not a neighbour with a similar number or name)?
2. **Date.** Does the source give this event on this date (not the day before or after; not the date of an order against the date it took effect)?
3. **Place.** Does the source name this place, and is the point within `precision_km` of it? If the point is a representative point, is that said?
4. **Event.** Is `event_type` right, and does `current_activity` say only what the source says?
5. **Command relationships and commander.** Do the stated relationships and the commander field match the source?
6. **Support.** Does every cited source support something the row says? Is any claimed fact unsupported by all of them?
7. **Confidence.** Recompute it from the rubric (F1, F2). Is it the level given?

Give a verdict per row: `supported` (all of the above), `partly supported` (say which item fails), `not supported` (the source contradicts), or `unverifiable` (the source cannot be opened or does not cover it). `unverifiable` is not a finding against the row.

For each sampled **relation**: does a source say this subject was under this higher unit in this relationship, from the start date to the end date? Check the start and end `basis`; check `end_unknown` against the sources; and check that the evidence claims do state what the table says they stated.

Please report the numbers: how many of 40 claims and 20 relations were `supported`, `partly supported`, `not supported`, `unverifiable`. The sample is built to reveal kinds of problems (small nationalities and rare values are over-sampled); it does not give an error rate for the whole dataset.
