# Data review for the Web UI

Reviewed November 1, 2026. This is a discovery note; interface design and technology choices remain to be discussed with Scott. WebUI was empty at review time. No app has been scaffolded and no dataset files have been changed.

## Repository map

- `../WorldWar2/build/`: generated, committed consumption files; use these as the app's primary inputs. Never hand-edit them.
- `../WorldWar2/data/`: master CSVs, including one claim file per unit under `claims/<nationality>/`, unit identities, source metadata, places, operations, and command evidence.
- `../WorldWar2/schema/`: JSON schemas, foreign keys, vocabulary descriptions and display ordering. `vocabularies.json` is the vocabulary authority.
- `../WorldWar2/scripts/`: Python standard-library build, validation, temporal queries, audits and migrations.
- `../WorldWar2/docs/`: methodology, source and attribution guidance, coverage, review history and handoff. Historical narrative counts can lag the actual files.
- `../WorldWar2/archive/`: older flat exports; not an app input.

## Current build inventory

Counts below were measured from the actual CSVs, rather than copied from overview documentation.

| File | Rows/features | Purpose |
| --- | ---: | --- |
| `all_claims.csv` | 2,280 | Full claim records; 57 columns; about 4.34 MB |
| `claims.geojson` | 2,280 | Claim points with selected properties; about 2.76 MB |
| `coverage.csv` | 388 | Unit directory and coverage summary: 319 active, 69 placeholder |
| `places.csv` | 1,129 | Canonical places, aliases, coordinate provenance and usage counts |
| `places.geojson` | 1,129 | Place points with selected properties; about 0.41 MB |
| `operations.csv` | 67 | Operation hierarchy, dates, scope and direct/descendant counts |
| `command_relations.csv` | 1,048 | Preferred non-organic command intervals with evidence and uncertainty |
| `claim_references.csv` | 5,563 | Claim-to-source links by role and locator |
| `unit_references.csv` | 916 | Unit-to-source links by field |
| `operation_references.csv` | 97 | Operation-to-source links |

Claims cover 319 distinct units from 1944-06-06 through 1945-05-10. The latest date exceeds the overview's nominal May 8 scope; derive UI date bounds from the loaded data. There are 2,239 preferred, 25 alternate and 16 disputed claims across 30 nonblank conflict groups. Activity fields are populated on 881 rows for 186 units. There are 22 claim coordinate overrides.

## Entities and joins

- `claim_id` is the stable claim identity. Use it for detail selection, links and joining GeoJSON to full CSV records. `(unit_id, date, event_type)` is a validation guard with documented exceptions, not the primary key.
- `unit_id` connects claims, coverage, command subjects/higher units, unit references, composition and opponents. `coverage.csv` supplies the basic unit directory, including units with no claims. Full unit metadata (organic parent, source fields, notes, formation metadata) exists in `data/units.csv`, not in a separate build units export.
- `place_id` connects claims to places. `location_name` is already derived from the canonical name and the claim's qualifier. Use claim coordinates when mapping claims: an override can differ from the place point.
- `operation_id` connects claims to their most specific operation. Follow `parent_operation_id` in the operations table for ancestors. Claims also carry ready-made labels: `operation`, `operation_type`, `campaign`, `operation_name`, `sub_operation_name`, `operation_path`. Hierarchy filters should include descendants when intended. Operation counts distinguish direct claims from claims including children.
- `conflict_group_id` groups competing claims; blank means no known conflict. A group can have no preferred member when all its members are disputed.
- `relation_id` identifies a command interval. `subject_unit_id` and `higher_unit_id` connect its units; `source_claim_ids` connects evidence claims.
- `reference_id` connects the three build reference-link files to `data/references.csv`. The build folder has no full reference metadata export. Rich source cards require that additional generated table, or a later app packaging step that includes it. Claim `source` URLs are available directly for a simpler first version.
- `data/nationalities.csv` supplies nationality adjectives and alliance; this lookup also has no build export. `schema/vocabularies.json` supplies controlled values and rank/display ordering.

These additional inputs are integration decisions to discuss, not authorization to modify the dataset or its build pipeline.

## Full claim record

The full CSV carries identity and unit descriptors; dated place and provenance; event/activity text; command parent and JSON relationships; commander; component and opponent IDs plus display names; formation/destruction flags; sourced strength JSON and derived strength status; confidence, citations and notes; location date/basis/offset; activity status/basis/span; and derived operation labels.

CSV ingestion must handle quoted commas, quotes and potential multiline fields. Read columns by name. Explicitly convert numeric values and the literal strings `true`/`false` (JavaScript Boolean('false') is true). Empty cells, `unknown` sentinels and numeric zero have different meanings. Parse `command_relationships` as a JSON array and nonblank `strength_json` as an object. Semicolon lists include unit/reference IDs; narrative fields and source locators require their own conventions, not a universal split rule. `source` URLs are separated by ` | `.

Keep date-only values as calendar dates. Avoid browser timezone conversion shifting a claim onto the previous date. Sort dated events by date, then claim ID as the dataset does; do not assume IDs are chronological.

## GeoJSON limitations

All geometries in both GeoJSON files are Points, in WGS84 `[longitude, latitude]` order. A place whose kind is area or line is still represented by a point; no historical boundaries or route geometry are provided.

`claims.geojson` has 29 properties: claim/conflict identity and status; unit identity, nationality, theater, echelon and branch; date/place/location meaning/precision/confidence; event and current activity; operation labels; strength status; location date/basis/offset; reference IDs and source locator.

It omits commander, notes, parent/command relationships, detailed strength, opponent/composition data, flags, coordinate provenance, operation path, and all three structured activity fields. A rich UI should join it to `all_claims.csv` by claim ID, or derive its own map features from the CSV after parsing. Do not assume the GeoJSON is the complete dataset.

## Interpretation requirements for the UI discussion

1. Claims are event-based sourced observations. Missing dates do not establish a stationary unit, inactivity or absence. Connecting points or carrying a location forward would introduce a reconstruction and must be an explicit design choice with visible uncertainty.
2. A point can mean headquarters, main body, sector center, front-line point, objective or approach route. Show `location_represents` and `precision_km`; a precision radius is an estimate, not a boundary or a measured error. Distances between representative points are not necessarily distances between units.
3. Confidence uses four rubric values (0.3, 0.5, 0.7, 0.9), scoring support for date and location. It is not a probability or event truth score. Filtering out low confidence can hide well-supported events whose locations are approximate.
4. Preserve alternate/disputed claims and their group context. Preferred means the dataset's selection, not certainty. Default visibility and conflict presentation remain to be chosen.
5. `parent_unit_id` on a claim is its operational parent on that date. A unit's standing, organic, assigned and temporary links are distinct. The build command table excludes organic and nonpreferred relations, so it is not a complete representation of every relationship in the master data.
6. Command intervals are inclusive, can have uncertain date ranges or times, and can overlap. Blank end dates do not establish indefinite command. Preserve boundary bases, `last_listed_date`, `end_unknown`, `change_undated`, support and evidence. `scripts/who_controls.py` implements possible/certain answers, same-day handover ambiguity, staleness and parent precedence; consult it before implementing a date-specific command tree.
7. Structured activity is distinct from event type, narrative `current_activity` and strength. Blank activity means not reviewed, not idle. `scripts/activity.py` implements start/end/point semantics: points take precedence on their day, an explicit end is inclusive, a different start implicitly closes a span the day before, and an otherwise open span is possible for at most 30 days. Inferred activity answers have confidence capped at 0.3. A location itself is not carried forward by these activity rules.
8. Strength can concern a whole unit, sub-force or sector and can have its own `as_of` date. Preserve scope, basis, source and vehicle count type. `unknown` strength is not zero strength.
9. Placeholder units have an identity but no mapped location claims. Coverage is uneven even for active units; active does not mean complete daily coverage.
10. Keep source links and locators accessible. Role-specific source links distinguish event, date, location, command relationship, strength and general support. Coordinate sourcing is a separate concern from historical event support.

## Attribution and scope

The whole repository (data, documentation, scripts and this viewer) is CC BY-SA 4.0 (root `LICENSE`). Review `WorldWar2/docs/reuse_and_attribution.md` and `CITATION.cff` when implementing public credit and downloads. Carry provenance and interpretation fields with mapped/exported claims; include the repository's specified coordinate attribution where applicable. No historical source websites were researched for this structural review.

Potential discussion topics: primary audience and questions; map versus timeline versus unit browsing; exact-day versus date-window behavior; filters and conflict visibility; uncertainty presentation; command hierarchy and activity queries; detail/source panels; data refresh and packaging; hosting and framework preferences. These are open decisions, not selected features.

## Review verification and environment

PowerShell successfully parsed every build CSV and the claims GeoJSON. Inventories, column names, sample records, schema guidance, build implementation and temporal query implementations were inspected. The Python build freshness check could not run: `python` resolves to an inaccessible WindowsApps alias and `py -3` reports no installed Python. Build freshness and full dataset validation are therefore unverified; do not claim they passed. No Python was installed for this review.

The only task file added is this note in WebUI. A pre-existing staged `.idea/.gitignore` was observed and left untouched. No commits, pushes, dependency installation or app generation were performed.

Later update during UI development: an existing Python 3.14 installation was found by its absolute executable path, despite the broken alias/launcher. Dataset validation, build freshness and all 590 semantic expectations subsequently passed; see `DEVELOPMENT_NOTES.md` for results and the validator's warnings. The statements above describe the initial discovery review.
