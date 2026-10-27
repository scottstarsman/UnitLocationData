# WWII Unit Locations

An open, claim-based dataset of where World War II units were, when, and how sure we are. Each row is one sourced claim: *this unit was at this place on this date*, with coordinates, a precision radius, a confidence score, an event type, what the unit was doing, and the sources. Competing claims are kept as separate rows instead of being averaged away.

**Status: work in progress.** The dataset covers the **Western Front, 6 June 1944 to 8 May 1945**: 932 claims about 193 units out of 359 in the unit table (the rest are placeholders). Coverage is uneven. June 1944 (Normandy landings through the fall of Cherbourg and Operation Epsom) covers US, British, Canadian and German units, including battle groups (Kampfgruppen) and a combat command; July 1944 to 8 May 1945 covers US Army army groups, armies, corps and selected division milestones; German Batch 1 (merged into `main`) adds 52 German claims for 2 July to 20 August 1944 (headquarters from OB West to corps, panzer, parachute and infantry divisions in the Mortain counterattack and the Falaise pocket); German Batch 1b (merged into `main`) adds 57 German claims for 1 to 19 July 1944 (the Caen front, Operations Charnwood and Goodwood, the Cotentin and Vire sectors), including 19 month-level or area-only rows at confidence 0.3. German Batch 2 (on the branch `german-batch2-sep-oct-1944`, branched from `main`) adds 111 German claims for 1 September to 31 October 1944 (OB West, Army Groups B and G, the armies, corps and divisions in the Aachen, Lorraine, Netherlands and Scheldt fighting; 54 of the rows are month-level or inferred at confidence 0.3). Rows are event-based, not daily: a unit has a row on days when something substantial happened, so its position between rows is unknown. See [docs/roadmap.md](docs/roadmap.md) for known gaps and the scale-up plan, and [docs/coverage.md](docs/coverage.md) for current counts.

> **Licensing.** Data: CC BY-SA 4.0 (`LICENSE-DATA`). Code: MIT (`LICENSE-CODE`). Wikipedia-derived facts are CC BY-SA, which is the main reason for the share-alike data licence; US Army Center of Military History volumes are public domain in the United States. Source-by-source notes: [docs/sources.md](docs/sources.md).

## Layout

```
data/claims/<nationality>/<unit_id>.csv   master copy: one file per unit, all claim columns
data/units.csv                            unit table (one row per unit, including placeholder and parent-only units)
data/nationalities.csv                    hand-maintained lookup table of nationalities (code = unit_id prefix, name, adjective, alliance); units, claims and operations refer to it
data/operations.csv                       hand-maintained table of operations, battles, phases and campaigns (parent chain, dates, sources); claims point at it through operation_id. Also operation_relations.csv (follows / concurrent_with / supports / related links) and operation_exceptions.csv
data/places.csv                           hand-maintained table of places (ids PL0001...: canonical name, aliases, kind point / area / line, coordinates, country, region, coordinate source); every claim points at one with place_id
data/command_relations.csv              hand-maintained master table of command relations (one dated interval per subject unit, higher unit and relationship; ids CR0001...); data/command_relation_claims.csv links each relation to the claims that list it (with what each claim stated), data/command_relation_overlaps.csv documents contradictory overlaps
data/claim_reference_roles.csv         hand-maintained role of a claim-to-reference link where a source supports one part of a claim (event, date, location, command_relationship, strength; the role of a coordinate service is derived, not stored); the links themselves are `reference_ids` in the claim files
data/references.csv                       GENERATED table of every source cited (one row per reference, with a link, licence and claim count and source family); curated metadata in data/references_meta.csv. Each claim lists its references in reference_ids (+ source_locator)
schema/                                   machine-readable schema (columns, foreign keys) + vocabularies + human-readable README
scripts/                                  validate.py, places.py, unit_refs.py and command_relations.py (libraries), migrate_places.py, migrate_command_relations.py, migrate_unit_ids.py, verify_unit_ids.py and migrate_review_items.py and verify_review_items.py (one-off), check_coordinates.py, audit_command_location.py, audit_temporal_relationships.py, who_controls.py, build.py, build_references.py, operations.py (library), promote_placeholders.py, migrate_operations.py, migrate_campaign.py (obsolete), split_from_flat.py, migrate_parent_formation.py, review_sample.py (the review packet's sample and counts) (standard library only)
build/                                    GENERATED combined outputs (all_claims.csv, claims.geojson, places.csv, places.geojson, coverage.csv, command_relations.csv, operations.csv, claim_references.csv, unit_references.csv, operation_references.csv; docs/coverage.md and data/references.csv are generated too)
docs/                                     methodology, sources, roadmap, coverage (generated); docs/review/ is the independent-review packet (brief, checklist, sample, questions) and the earlier review notes
archive/v5_flat/                          the flat CSVs the per-unit files were first split from
(repository root) .github/workflows/validate.yml   CI for pull requests and pushes to any branch; runs the commands below inside WorldWar2/
```

**Edit `data/` only. Never hand-edit `build/`**: it is generated by `scripts/build.py` and committed so people can download the combined files without running anything.

## Data model

- **Claim** (a row in `data/claims/...`): `claim_id` (never reused), optional `conflict_group_id`, `claim_status` (preferred / alternate / disputed), `unit_id`, `date`, `theater`, place (`place_id` pointing at `data/places.csv`, `location_qualifier`, the claim's own `latitude` and `longitude`, `coord_override` when that point differs from the place's, `location_represents`, `precision_km`), `event_type` and `current_activity`, `engaged_with` (opponent `unit_id`s; `engaged_note` for an opponent that is not a unit), command (`parent_unit_id` for the operational parent; the claim's organic, assigned, attached, operational-control or reserve relations are rows of `data/command_relations.csv` linked by `data/command_relation_claims.csv`, and `build/all_claims.csv` rebuilds them as `command_relationships`; `commander`, `composing_units` as unit ids with `composing_text` for the rest), optional `strength_json` (figures and, where a source states it, a qualitative `status`), `confidence`, `source`, `notes`. Values that follow from other data are not stored: `location_name`, `location_temporal_offset_days` and `strength_status` are derived into `build/all_claims.csv` (see [schema/README.md](schema/README.md), "Derived values"). Full column definitions: [schema/README.md](schema/README.md).
- **Unit** (a row in `data/units.csv`): `unit_id`, `unit_name`, `nationality`, `echelon`, `branch`, `theater` (primary), `parent_unit_id` (organic parent of battle groups), `record_status` (placeholder / partial / active), optional `formed_date` and `initial_parent_*` listing columns (see [docs/methodology.md](docs/methodology.md), "Placeholder units"). Most of the table is placeholders; [docs/coverage.md](docs/coverage.md) shows what has claims.
- **Operation** (a row in `data/operations.csv`): `operation_id` (`OP-EPSOM`), `name`, `short_name`, `op_type` (umbrella / campaign / operation / battle / phase), `parent_operation_id`, dates with a `date_basis`, `reference_ids` and `notes`. A claim's `operation_id` is the most specific row it belongs to; the parent chain gives the campaign and the umbrella, and `build/all_claims.csv` carries the derived `operation`, `campaign`, `operation_name`, `sub_operation_name` and `operation_path`. See [schema/README.md](schema/README.md#operations-dataoperationscsv-dataoperation_relationscsv-dataoperation_exceptionscsv).
- **Conflict group**: claims that disagree about the same unit and event (for example two sources dating a commander's death differently). One may be preferred; the others are alternate or disputed.
- **theater**: controlled vocabulary (`western_europe`, `mediterranean`, `north_africa`, `eastern_front`, `pacific`, `cbi`, `atlantic`, `other`). All current rows are `western_europe`.

## How to interpret the data

The dataset is a set of **sourced observations**, not a continuous reconstruction of where every unit was. Read each row with these points (the details and the counts are in [schema/README.md](schema/README.md), "Reading a command interval", "What `confidence` means" and "What a location point can mean"; the reuse terms are in [docs/reuse_and_attribution.md](docs/reuse_and_attribution.md)):

- **A claim is a sourced assertion** that a source puts this unit at this place on this date doing this. It is not a verified unit state for the days around it.
- **No row for a date does not mean no activity, and does not mean the unit stayed put.** Rows are event-based; quiet days are absent on purpose, so a position between two rows is unknown, not unchanged. Do not interpolate unless you say so.
- **A point is not always where the unit was.** It can stand for a headquarters, a main body, the centre of a sector, a point on a front line, an objective, a march route or a town centre (`location_represents`, `location_basis`, `precision_km`). A distance between two claim points is not a distance between two units.
- **`confidence` scores the date and the place** (how exactly the location is documented and by how many independent source families); it is not a probability, and it says nothing about whether the event happened. A command change with a well-documented date and an approximate headquarters place scores 0.3 or 0.5. Do not filter events by it (84 of the 96 command-change claims are below 0.7); the notes sentence `Event support:` says how well an event is documented, where there is one.
- **A command relationship is an interval, and its boundaries may be inferred.** `valid_to_basis` says whether an end is sourced, inferred from the unit's next claim, or open at the last claim that lists it; a missing end never means the relationship held indefinitely. A relationship is evidenced up to the last claim that lists it.
- **The `preferred` claim is the dataset's selection, not a fact.** In a conflict group it is the best-supported of competing claims; the alternates are kept and say what the other sources say.
- **`claim_id` is the identity of a claim.** `(unit_id, date, event_type)` is only a guard against entering the same claim twice.

Three examples. **C0001** (2nd Canadian Armoured Brigade, 6 June 1944, landing): the point is the centre of the Juno Beach sector (`sector_center`, 10 km), not the position of the brigade's units. **CR0106** (the 101st Airborne Division attached to British Second Army from 18 September 1944): its end, 8 November, is read from the table (the Army Attached column lists Second Army until the row of 9 November, `assignment_table`; before 26 October 2026 the end was inferred as 16 December), and the claims C0567 to C0573 evidence the corps changes that follow. **C0244** (4th Armored Division arrives on the Continent, 13 July 1944; confidence 0.3): its separate event row **C0243** (landing at Utah Beach, 11 July, from other sources) is a different event, not a rival date; the two were a conflict group (G012) until 26 October 2026, when the group was dissolved; the place is the vicinity of an unresolved CMH place name (50 km).

## Quick start

Requires Python 3.8+ and nothing else (standard library only). Run the commands from this directory (`WorldWar2/` in the repository).

```bash
python scripts/validate.py          # exit code 0 = data is valid
python scripts/build.py             # regenerate build/ (all_claims.csv, claims.geojson)
python scripts/build.py --check     # exit code 1 if build/ is stale (used by CI)
python scripts/semantic_tests.py    # what who_controls.py answers for four command scenarios; exit code 1 on a changed answer (used by CI, run build.py first)
python scripts/check_coordinates.py # coordinate warnings only (add --geocode and --places before a release to fill the geocoder cache)
```

Use the data directly: `build/all_claims.csv` (all claims, one file) or `build/claims.geojson` (Point features for GIS tools, `geojson.io`, QGIS, Leaflet).

Example (Python, no libraries):

```python
import csv
rows = list(csv.DictReader(open("build/all_claims.csv", encoding="utf-8")))
d13 = [r for r in rows if r["date"] == "1944-06-13" and r["claim_status"] == "preferred"]
print(len(d13), "preferred claims on 13 June 1944")
```

## Contributing

Every row needs a source, conflicting claims become separate rows, and nothing is invented. Read [CONTRIBUTING.md](CONTRIBUTING.md) (how to add a unit or a claim, the PR checklist) and the [code of conduct](CODE_OF_CONDUCT.md). Pull requests run `scripts/validate.py` and check that `build/` is up to date.

## Documentation

- [docs/methodology.md](docs/methodology.md): how claims are built, precision, confidence, conflicts, strength figures
- [docs/sources.md](docs/sources.md): sources used, reliability, licensing; the full list of references is [data/references.csv](data/references.csv)
- [docs/reuse_and_attribution.md](docs/reuse_and_attribution.md): what to credit and what applies when you reuse a derived file, by source family and by export
- [docs/roadmap.md](docs/roadmap.md): scale-up plan and known gaps
- [docs/HANDOFF.md](docs/HANDOFF.md): handoff for whoever maintains the dataset next (state, locations, standing rules, conventions, checks, decision log, next steps)
- [docs/coverage.md](docs/coverage.md): generated coverage of the unit table (placeholder vs active)
- [docs/review/README.md](docs/review/README.md): the brief for an independent reviewer (scope, tables, rules, known limitations), with a checklist, a seeded sample to check against the sources, and ten design questions
- [schema/README.md](schema/README.md): column and vocabulary reference

## Licence and citation

Data: CC BY-SA 4.0 (see `LICENSE-DATA`). Code: MIT (see `LICENSE-CODE`). Citation metadata: `CITATION.cff`. Copyright holder: Raymond Scott Starsman.
