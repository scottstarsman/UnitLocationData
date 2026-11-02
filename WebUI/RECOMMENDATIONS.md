# Recommendations for data structures and analysis

Prepared November 1, 2026, from the current repository, build files, schemas, validation code, semantic tests and audit scripts. These are proposals for discussion; no dataset or application changes have been implemented.

The existing claim-based model is a good foundation. Stable IDs, separate unit/place/operation entities, preserved conflicts, dated command relations, role-based citations, controlled vocabularies and existing validators should be retained. Most near-term improvements can be generated exports or reports rather than changes to master records.

## Priority overview

| Priority | Recommendation | Expected benefit |
| --- | --- | --- |
| High | 1. Publish a complete, versioned web data package | A reproducible, self-contained app input |
| High | 2. Define typed exports and field semantics | Consistent parsing and fewer interpretation errors |
| High | 3. Reuse temporal logic with shared examples | Command/activity answers agree across tools and UI |
| High | 4. Generate coverage and evidence-quality reports | Makes gaps visible and guides research |
| Medium | 5. Create a focused source-review queue | Improves the most consequential uncertain records first |
| Medium | 6. Expand automated cross-export checks | Prevents a valid dataset from producing incomplete app data |
| Medium | 7. Record conflict subjects explicitly | Explains what sources actually disagree about |
| Medium | 8. Represent uncertain event dates explicitly | Supports honest date filtering and timelines |
| Later | 9. Add sourced unit names and lineage links | Better search and continuity across reorganizations |
| Later | 10. Add selected gazetteer identifiers or geometry | Better place matching and carefully sourced spatial detail |

## 1. Publish a complete, versioned web data package

**Observed:** `build/` contains eight CSVs and two GeoJSON files, but no full unit table, source metadata table, nationalities lookup or vocabulary export. Source links in the build files refer to records in `data/references.csv`. `coverage.csv` gives a basic unit directory but omits full unit notes and formation/source metadata. The GeoJSON is deliberately a subset of the claims CSV.

**Recommendation:** Add a deterministic publication step that packages the existing outputs with the additional lookup tables required by the UI. It could live in the app's data preparation code or the dataset build pipeline; choose ownership before implementation. Include a manifest describing:

- Data schema/export version and source revision identifier.
- Files, row counts and content hashes.
- Observed minimum and maximum claim dates, separately from the intended historical scope.
- Coordinate system, date conventions, dataset citation and attribution information.
- Which exports are subsets, and which fields or relationship classes they omit.

Keep reproducible data files deterministic. If a deployment timestamp is useful, store it as release metadata rather than making every build differ. If embedding a Git revision, define it as the input/source revision so generating and committing the exports does not create a self-referencing revision problem.

**Success criterion:** The app can load a single published package without reading arbitrary files from `data/` or guessing which revision its components represent. Historical scope and observed bounds are distinguishable: the current claims extend to May 10, 1945, while the overview describes a May 8 endpoint.

## 2. Define typed exports and field semantics

**Observed:** The full claims CSV has 57 columns. Some cells contain JSON, some contain semicolon-delimited IDs, and booleans/numbers arrive as strings. Blank and `unknown` have field-specific meanings; blank composition can mean unchanged from the previous record. The claims GeoJSON omits structured activity, notes, commander, command relationships, detailed strength and other fields.

**Recommendation:** Keep CSV as an accessible exchange format and provide a generated typed JSON export or one well-defined app ingestion layer. Use arrays for ID lists and relationships, objects for strength, and actual booleans/numbers. Document missing-value semantics per field, particularly composition, activity, opponents, strength and location provenance. Preserve original raw values and provenance when deriving an interpreted value.

Specify a field contract for both full and map exports. Either join map features to full claims by `claim_id`, or generate map features from the typed full records. Include structured activity in any map export that supports activity filtering. Keep date-only values as calendar dates and define stable ordering for events on the same day.

**Success criterion:** One parsing policy produces consistent values in maps, tables, filters and downloads. No component treats `"false"` as true, missing strength as zero, blank activity as idle, or blank composition as an empty formation.

## 3. Reuse temporal logic with shared examples

**Observed:** `scripts/who_controls.py` and `scripts/activity.py` already implement meaningful temporal rules, and `scripts/semantic_tests.py` already tests many command and activity scenarios. Reimplementing them independently in the browser would create a second interpretation of the dataset.

**Recommendation:** Agree on a reusable result contract for temporal queries: value, certain/possible/unknown result, support, relevant interval, evidence claim IDs and explanation. Retain the scripts' existing meaning of certainty; it describes support under the query rules, not historical infallibility. Extract shared query functions where useful, or port them with machine-readable examples whose expected answers come from reviewed cases.

Cover inclusive boundaries, same-day handovers with and without times, uncertain starts/ends, overlapping command holders, organic versus operational parents, stale open command intervals, activity point precedence, inferred closures and the 30-day horizon for otherwise open activity spans. That activity horizon must not become a location carry-forward rule.

**Success criterion:** The same unit/date/time produces the same answer and explanation in the Python tools and UI. Unknown location between observations remains unknown.

## 4. Generate coverage and evidence-quality reports

**Observed baseline:** 2,280 claims cover 319 of 388 listed units; 69 units are placeholders. There are 881 activity annotations across 186 units, 250 claims with blank `location_basis`, 530 claims at confidence 0.3, 31 nonblank strength records, and 1,844 claims with nonblank `source_locator`. These measure different things and should not be combined into one quality score.

**Recommendation:** Generate a small analysis report and machine-readable summary with:

- Claims and distinct observed dates by unit, nationality, echelon, month and operation.
- First/last observations and gaps between dated observations, explicitly labeled as observation gaps rather than absence or stationary periods.
- Location basis, precision band, temporal offset and point meaning distributions.
- Activity annotation coverage, distinguishing points, closed spans and open spans; blank does not mean a reviewed negative finding.
- Citation locator coverage, independent source-family counts, source-role coverage, and source link-check age/status.
- Conflict counts by group and subject, with counts of preferred versus all claims shown separately.

Use denominators appropriate to the question: distinct units or dates for coverage, conflict groups for disputed events, source families for corroboration. Report both numerators and denominators. Coordinate services should not count as independent corroboration of a historical event. A locator is useful evidence access, not proof that a claim is correct.

**Success criterion:** The report identifies where additional research will improve the dataset. Map density and event counts are described as documentation density, not force density, operational intensity or strength. No completeness percentage is reported without a defined expected population and time window.

## 5. Create a focused source-review queue

**Observed:** The repository already has coordinate and temporal audits. Many citation links use the `general` role, while only a small number have explicit event/date/command roles; coordinate-derived location links are a different category. Some location support and uncertainty remain in narrative notes.

**Recommendation:** Combine existing audit findings into a review queue keyed by claim/relation ID, with reason, evidence links, priority, review outcome and resolution revision. Start with the 250 blank location bases, large location-date offsets, uncertain command transitions that affect hierarchy answers, and conflicts likely to change a user's interpretation. Add missing source locators where the underlying source supports them. Split citation roles only after reviewing what each source supports.

Prioritize consequence and uncertainty together. Confidence 0.3 is not by itself a defect: a representative point may correctly receive that score. Preserve unresolved records and their caveats instead of assigning precision or support merely to complete a field.

**Success criterion:** Each reviewed item has a documented confirmed/corrected/unresolved outcome. Research adds traceable evidence and clearer limits rather than mechanically increasing confidence.

## 6. Expand automated cross-export checks

**Observed:** CI already validates the master data, builds exports, checks committed output freshness and runs extensive semantic scenarios. Coordinate and temporal audits are intentionally non-failing review prompts. Extend this system rather than duplicating it.

**Recommendation:** When the publication package is implemented, check that every claim appears once in full and map exports, IDs and coordinates agree, lookup joins resolve, required UI fields survive export, and operation direct/descendant counts match their definitions. Check subset policies explicitly: the current command export excludes organic and nonpreferred relations. Verify typed JSON values and preservation of uncertainty/provenance through an export/import round trip.

Give audit findings stable codes and a machine-readable output, alongside the human report. Separate accepted/documented findings from newly introduced ones. Promote only unambiguous invariants to blocking failures; leave historically plausible anomalies as source-review prompts.

**Success criterion:** A missing lookup, dropped activity field or export mismatch fails publication. A legitimate uncertain historical relationship is preserved and explained rather than rejected merely for being uncertain.

## 7. Record conflict subjects explicitly

**Observed:** `conflict_group_id` and `claim_status` preserve competing claims, but the columns do not say whether a group concerns date, location, commander, event interpretation or another subject. Notes contain context, and the existing audit already looks for sequences mistakenly grouped as conflicts.

**Recommendation:** If conflict explanations are part of the UI, add a small conflict-group table with ID, one or more disputed fields, summary, review status, and a sourced rationale for the current preference or lack of preference. Keep member claims and their original evidence. Retain the existing per-claim status unless a reviewed migration deliberately changes it.

**Success criterion:** A user can distinguish an agreed event with a disputed date from a disputed location or event. Settled groups retain a documented history without silently losing alternative evidence.

## 8. Represent uncertain event dates explicitly

**Observed:** Claim `date` is required as a single day. Documentation describes month-level and approximate dates, whose limitations may be expressed in notes and confidence. Command relations already have date ranges and boundary bases, but claims do not have equivalent event-date fields.

**Recommendation:** First audit actual use of approximate event dates. If filtering/timeline behavior requires it, introduce optional earliest/latest event dates and a controlled date precision/basis. Preserve the existing date as an explicitly documented sorting/display anchor during migration. Keep event-date uncertainty separate from `location_date` and `location_basis`, which concern the coordinate's provenance.

Define filtering semantics before migration: an exact-date observation differs from an event whose possible range intersects that date. Backfill only where reviewed evidence supports a range; do not infer a full-month range from a note without checking its meaning. New columns such as these or separate event-support fields require Scott's approval before implementation.

**Success criterion:** A month-level event can appear as approximate without being counted or presented as an exact occurrence on the first day of the month.

## 9. Add sourced unit names and lineage links when needed

**Observed:** Place aliases already exist. Unit naming/reorganization ambiguities are documented in unit notes, and some predecessor/successor formations intentionally have separate IDs.

**Recommendation:** As search and lineage requirements emerge, add sourced unit aliases with optional date validity and language. Model predecessor/successor, redesignation, split and merger links separately from command relations. Preserve existing unit IDs; a name resemblance is not evidence of identity or continuity.

**Success criterion:** Searching a historical or translated name finds the intended unit, and related formations can be navigated without merging their distinct claims or inventing command links. A commanders table is a separate potential project and is not recommended as a prerequisite for the first UI.

## 10. Add selected gazetteer identifiers or geometry when justified

**Observed:** Places have names, aliases, point/area/line kinds and coordinate provenance, but both GeoJSON exports contain only Point geometries. Gazetteer IDs are already mentioned as a future improvement in the roadmap.

**Recommendation:** Add verified external place identifiers selectively, recording provenance and historical naming context. Add sourced lines/polygons only for a concrete use case and with their date, meaning and precision documented. Keep representative points available for current consumers. A precision-radius circle is a visualization of an estimate, not a historical sector boundary or confidence contour.

**Success criterion:** External IDs improve matching without merging different historical places. Any nonpoint geometry is traceable to a source and appropriate period; modern administrative boundaries are not silently substituted for wartime unit areas.

## Suggested implementation order and limits

Begin with the publication contract, typed ingestion and generated coverage report. Then implement the specific temporal queries and evidence review needed for the agreed UI. Consider schema additions only after those needs reveal a concrete limitation.

At this dataset size, a generated static package is a reasonable initial option. A database, vector tiles, search service or additional formats should follow measured requirements for editing, query volume or scale. Avoid adding parallel authoritative stores or speculative normalization that increases maintenance without answering a user question.

This review inspected files and calculated descriptive counts with PowerShell. It did not verify historical sources or run the Python validators: `python` resolves to an inaccessible WindowsApps alias and `py -3` reports no installed Python. Existing CI configuration was reviewed, but its latest run status was not checked. No claim is made that the current build is fresh or that all checks pass. Only this recommendations document was added for this request.

## Repository references

Implementation update: the later UI task found an existing Python executable by absolute path and verified the dataset's validator, build freshness and semantic expectations. See [development notes](DEVELOPMENT_NOTES.md); the earlier execution limit above describes this recommendations review, not the current verification state.

- [Data review notes](DATA_NOTES.md)
- [Schema reference](../WorldWar2/schema/README.md) and [vocabularies](../WorldWar2/schema/vocabularies.json)
- [Build implementation](../WorldWar2/scripts/build.py)
- [Command query rules](../WorldWar2/scripts/who_controls.py) and [activity query rules](../WorldWar2/scripts/activity.py)
- [Semantic scenarios](../WorldWar2/scripts/semantic_tests.py)
- [Temporal audit](../WorldWar2/scripts/audit_temporal_relationships.py) and [command/location audit](../WorldWar2/scripts/audit_command_location.py)
- [CI validation workflow](../.github/workflows/validate.yml)
- [Methodology](../WorldWar2/docs/methodology.md), [roadmap](../WorldWar2/docs/roadmap.md) and [reuse guidance](../WorldWar2/docs/reuse_and_attribution.md)
