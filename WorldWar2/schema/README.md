# Schema reference

The machine-readable definitions live next to this file and are what `scripts/validate.py` enforces:

- [`claims.schema.json`](claims.schema.json): column order, types and constraints of every file under `data/claims/` (Frictionless Table Schema style; `vocabulary` is a custom property pointing at a key in `vocabularies.json`).
- [`units.schema.json`](units.schema.json): the same for `data/units.csv`.
- [`relations.schema.json`](relations.schema.json): primary keys and foreign keys of the side tables that have no column schema of their own (`nationalities`, `operations`, `operation_relations`, `operation_exceptions`, `coordinate_exceptions`, `claim_key_exceptions`, `place_merges`, `references_meta`, `claim_reference_roles`).
- [`places.schema.json`](places.schema.json): columns, primary key and foreign key of `data/places.csv`.
- [`vocabularies.json`](vocabularies.json): controlled vocabularies and the confidence rubric.

All CSV files are UTF-8, LF line endings, comma separated, with a header row, minimal quoting (fields with commas, quotes or newlines are quoted). Missing values are empty strings. Dates are `YYYY-MM-DD`. Booleans are lowercase `true`/`false`. Coordinates are decimal degrees (WGS84). The column order is the same in every claim file; `theater` follows `date`.

When you change a column or vocabulary, edit the JSON files and this page together.

## claims columns (`data/claims/<nationality>/<unit_id>.csv`, `build/all_claims.csv`)

| column | type | required | meaning | constraints |
|---|---|---|---|---|
| `claim_id` | string | yes | Unique id of the claim, C0001 onward. One row is one claim ("this unit was here on this date"). Never reused. | pattern `^C\d{4,}$` |
| `conflict_group_id` | string | no | Shared by rows that make competing claims about the same unit and event (G001...). Blank if no known conflict. | pattern `^G\d{3,}$` |
| `claim_status` | string | yes | preferred, alternate or disputed (see vocabulary). | vocabulary `claim_status` |
| `unit_id` | string | yes | Stable unit key, NATION-TYPE-NUMBER+ECHELONLETTER (for example US-INF-029D). Must exist in data/units.csv and match the file name. | pattern `^[A-Z]{2,4}(-[A-Z0-9]+)+$` |
| `date` | date | yes | Date of the claim, YYYY-MM-DD. |  |
| `theater` | string | yes | Theater of this row: the front or rear area where the unit was on the claim date (see vocabulary and "Theater" below). Not repeated from `data/units.csv`: a row may differ from the unit's primary theater. Must equal the `theater` of the row's `operation_id`. | vocabulary `theater` |
| `nationality` | string | yes | Nationality of the unit: US, UK, Canada, Germany (extend as needed). Matches the data/claims/<nationality>/ folder in lowercase. | vocabulary `nationality` |
| `unit_name` | string | yes | Unit name only, for example "29th Infantry Division". |  |
| `echelon` | string | yes | Organisational level (see vocabulary). | vocabulary `echelon` |
| `branch` | string | yes | Service or arm (see vocabulary). | vocabulary `branch` |
| `parent_unit_id` | string | no | Unit id (from `data/units.csv`) of the operational parent on that row's date: the formation the unit was attached to or operating under, otherwise its standing parent. It must be the higher unit of one of the relations the claim lists (see [Command relations](#command-relations)). Blank if the unit has no parent (top-level headquarters) or if none was verified; in the second case the claim lists one `unknown` placeholder relation (`higher_unit_id` blank, with a note). The text `unknown` is not a value. The organic parent, when different, is another relation of the claim. | pattern `^[A-Z]{2,4}(-[A-Z0-9]+)+$`; foreign key to `units` |
| `commander` | string | yes | Commander on that date, rank and name as given by sources; "unknown" if not verified. |  |
| `latitude` | number | yes | Decimal degrees WGS84. | -90 to 90 |
| `longitude` | number | yes | Decimal degrees WGS84. | -180 to 180 |
| `place_id` | string | yes | The place the coordinate refers to: a row of data/places.csv (a named settlement or site, an area, sector or beach, or a front or axis). Replaces the free-text location_name, which is rebuilt in build/all_claims.csv from the place name and location_qualifier. | foreign key places.`place_id`; pattern `^PL\d{4,}$` |
| `location_qualifier` | string | no | Optional. What is specific to this claim about the place, as the sources word it: a context note ('division HQ Le Molay-Littry', 'point = Cheux') or the reserved first token `vicinity` (the claim says "vicinity of <place>"; further text follows after '; '). Blank when the claim is simply at the place. Never a place name that is not in places.csv. |  |
| `coord_override` | string | no | Optional. A reason, set only when this claim's latitude/longitude differ from the place's (another geocoder read of the same place, an approximate point). It names the coordinate source of the claim's own point and the distance to the place point ('OpenStreetMap Nominatim (Utah Beach, Manche, France); 290 m from the place point'). Blank when the claim uses the place's point: the validator requires the point to equal the place's exactly when this is blank and to differ when it is set. |  |
| `location_represents` | string | yes | What the point stands for (see vocabulary). | vocabulary `location_represents` |
| `precision_km` | number | yes | Judgment estimate of the radius in km within which the unit probably was (banded). | vocabulary `precision_km` |
| `operation_id` | string | yes | Key of the most specific operation, battle, phase or campaign the row belongs to, in `data/operations.csv` (for example `OP-EPSOM`; `OP-CAMP-NORTHERN-FRANCE` when no named operation applies). The parent chain gives the campaign, the umbrella (Overlord) and the named operation; `build/all_claims.csv` carries them as derived columns. The date should lie inside the operation's dates. See "Operations" below. | pattern `^OP-[A-Z0-9]+(-[A-Z0-9]+)*$` |
| `composing_units` | string | no | Subordinate units that are a unit of `data/units.csv`: `;` list of `unit_id`s (foreign key), listed when first given or when they change. Blank (with `composing_text` blank) means unchanged from the unit's previous row; "unknown" means no data. |  |
| `composing_text` | string | no | Free text for the composition that is not a unit of the table (regiments, battalions, companies, remarks), `;` list (a `;` inside parentheses does not split). `<unit_id> (<qualifier>)` is the qualifier of a unit in `composing_units`. The word "attach" in any form (attached, attachment, ...) is rejected, in the entries and in the qualifiers (use `data/command_relations.csv`, or `docs/deferred_relations.md` for a formation that is not a unit); never the name of a unit that has an id, and no id inside a free-text entry. |  |
| `established` | boolean | yes | True on the row where the source says the unit was formed. | `true`/`false` |
| `disestablished` | boolean | yes | True on the row where the source says the unit was disbanded. | `true`/`false` |
| `destroyed` | boolean | yes | True on the row where the source says the unit was destroyed. | `true`/`false` |
| `confidence` | number | yes | Numeric 0-1 confidence by rubric (see vocabulary). | vocabulary `confidence`; 0 to 1 |
| `source` | string | yes | The readable citation: URLs separated by " \| ". Every row needs at least one URL, and each URL must resolve to an id in `reference_ids`. The coordinate source is not part of it: it is the place's `coord_reference_id` and `coord_source_note` (data/places.csv), or `coord_override` for a claim with its own point. |  |
| `reference_ids` | string | yes | The references that support the row: `;`-separated `reference_id`s from `data/references_meta.csv`, in citation order. The source of truth for the claim-to-reference links; the URLs in `source` must resolve to them. A row at confidence 0.9 should cite two source families (warning). See the References section below. | `R###` ids separated by `;` |
| `source_locator` | string | no | Page, chapter or section per reference: `R398: p. 285, 289; R407: p. 36`. Only ids that are in `reference_ids`; blank when the citation gives no page. | `R###: text` separated by `; ` |
| `event_type` | string | yes | One primary event type (see vocabulary). | vocabulary `event_type` |
| `current_activity` | string | yes | Short phrase saying what the unit is doing on that date at that place; lower-case, free text. |  |
| `engaged_with` | string | no | Enemy units fought on that date: `;` list of `unit_id`s (foreign key). Blank = no combat that day; "unknown" = combat with no opponent identified (the only sentinel). |  |
| `engaged_note` | string | no | Free text for an opponent that cannot be a unit id (an air force, naval forces, an unnamed formation), `;` list. Never the name of a unit that has an id. |  |
| `strength_json` | string | no | Optional JSON object with sourced strength figures: {"basis","as_of","personnel","vehicles","vehicle_count_type","scope","status","source","note"}; scope (whole_unit, sub_force, sector) says what the figure covers and is required whenever personnel is present. `status` (full, reduced or heavily_depleted; vocabulary strength_json_status) is the qualitative strength a source states; a record with a status needs no personnel or vehicles figure. build/all_claims.csv derives `strength_status` from it (destroyed when the destroyed flag is true, unknown when there is no status). See docs/methodology.md. Blank where no source gives figures or a status. |  |
| `notes` | string | yes | Free text: what the source says, caveats, source conflicts, change history. |  |
| `location_date` | date | no | Optional. The date the coordinate is actually documented for, when it differs from `date` (for example the date of the command post list the point was taken from). Blank where the coordinate is for the claim's own date or the date is unknown (older rows not yet reviewed). | valid date |
| `location_basis` | string | no | Optional. How the coordinate relates in time and place to `date` (see vocabulary `location_basis`). Blank on rows not yet reviewed. | vocabulary `location_basis` |
| `activity_status` | string | no | Pilot (October 2026). in_line, reserve, refitting, garrison or transit (vocabulary `activity_status`); blank = not reviewed for activity. | vocabulary `activity_status` |
| `activity_basis` | string | with activity_status | stated or inferred; an inferred activity is read at a confidence of at most 0.3. | vocabulary `activity_basis` |
| `activity_span` | string | with activity_status | start, end or point (vocabulary `activity_span`); see `docs/activity_status_design.md`. | vocabulary `activity_span` |

Primary key: `claim_id` (unique across the whole repository). Rows in each file are sorted by `date`, then `claim_id`.

**Claim key.** A unit has at most one claim per `date` and `event_type`: `(unit_id, date, event_type)` is unique across the repository (`uniqueTogether` in `claims.schema.json`; `scripts/validate.py` enforces it). `claim_id` stays the primary key; the key says what the claim is about, so the same event is not entered twice. Two claims may share the key in two cases only:

1. **The sources disagree.** Both claims are in the same conflict group (same `conflict_group_id`, one `preferred` and the others `alternate`, or all `disputed`; see CONTRIBUTING rule 2). Nothing else is needed.
2. **They are different actions of one kind on one day** (for example two attacks by one division at different places, written as one row per action, see "One row, one action" in `docs/methodology.md`). The pair is listed with a reason in `data/claim_key_exceptions.csv`.

### data/claim_key_exceptions.csv (hand-maintained)

| column | description |
|---|---|
| `claim_id` | The claim with the lower id of the pair. |
| `other_claim_id` | The other claim. Together with `claim_id` the primary key; both are foreign keys to claims.`claim_id`. Rows sorted by the pair. |
| `reason` | Why the two are different actions and not duplicates (what differs: the place, the opponent, the objective), with the source if it is not in the claims' notes. |

Validator checks: header, sorted, both ids are claims, the pair really shares `unit_id`, `date` and `event_type` and is not already in one conflict group (an exception that is not needed is an error: remove it), the reason is not blank. A repeated key that is neither in one conflict group nor listed is an error that names both claims. The table is empty today: when the rule was added no claim shared a key (566 claims, 566 distinct keys); the 14 conflict groups differ in date or event type.

### data/retired_claims.csv (hand-maintained)

Claim ids are never reused. A claim that has to leave the data (it was entered by mistake, or it duplicated another claim; a claim that is merely wrong is corrected or contradicted by a conflicting claim, see CONTRIBUTING rule 2 and 6) has its row removed from the claim file and one row added here, so the id stays accounted for. The table is empty today: no id is missing from C0001 to C0566.

| column | description |
|---|---|
| `claim_id` | The retired id (primary key). Never a claim again. Rows sorted by `claim_id`. |
| `replaced_by_claim_id` | The claim that carries on the retired one (foreign key to claims.`claim_id`), or blank when none does. |
| `reason` | Why the claim was removed, and by whom or in which change. |

Validator checks (`scripts/validate.py`): header, sorted, no repeated id, the id is not a claim, the replacement is a claim, the reason is not blank; a gap in the numbering that is not retired is printed as a NOTE (a gap is allowed when the id was never used). `scripts/check_claim_ids.py` compares with an earlier revision (default `origin/main`) and fails when an id of that revision is gone without a row here, belongs to another unit now, or when a retired id was forgotten or reused; it needs git history, so it is run by hand before a pull request.

## places columns (`data/places.csv`)

One row per place; claims point at it with `place_id`. Primary key `place_id`; rows sorted by `place_id`; `name` unique ignoring case; no alias equals another place's name or its own; foreign key `coord_reference_id` -> references_meta.`reference_id` (a `gazetteer_geocoder` reference, or blank for a hand-worked point). Machine-readable: [`places.schema.json`](places.schema.json). `build/places.csv` adds `claim_count` and `build/places.geojson` maps the places.

| column | type | required | description |
|---|---|---|---|
| `place_id` | string | yes | Stable key PL0001 onward. Never reused. |
| `name` | string | yes | Canonical name, unique (ignoring case) across the table. Settlements are written 'Name, administrative area' as the sources give them. |
| `alt_names` | string | no | Other spellings and names under which claims named the place, separated by '; '. No alias may equal another place's name. |
| `kind` | string | yes | point (a named settlement or site), area (a named area, sector, beach, zone or bridgehead, represented by one point) or line (a front, axis or route, represented by one point on it). |
| `latitude` | number | yes | Decimal degrees WGS84 of the place's point. |
| `longitude` | number | yes | Decimal degrees WGS84 of the place's point. |
| `precision_km` | number | yes | The finest radius (banded, vocabulary precision_km) with which any claim has used this point when the place was created; a guide for new claims, not a measured error. A claim keeps its own precision_km. |
| `country` | string | yes | ISO 3166-1 alpha-2 code of the country the point lies in today (vocabulary country). Assigned once from the nearest GeoNames populated place; check border places by hand. `IT` (Italy) was added to the vocabulary on 12 November 2026 (Scott approved), for places on the Italian front and for French and other Allied rows in Italy and Elba. |
| `region` | string | yes | First-level administrative area of the point as GeoNames names it (for example Lower Normandy, Wallonia, Limburg). |
| `coord_reference_id` | string | no | The coordinate service that gave the point: a reference of source_type gazetteer_geocoder in data/references_meta.csv (R001 Wikipedia article coordinates, R002 OpenStreetMap Nominatim). Blank for a point worked out by hand (then coord_source_note says how). |
| `coord_source_note` | string | yes | How the point was obtained, as the claims recorded it: the Wikipedia article ('Wikipedia (en): Brest, France') or the Nominatim query, or for a hand-worked point (blank reference id) the explanation (midpoint of two towns, commune centroid). |

Validator checks: unique ids and names, an alias is not another place's name or alias, sorted, vocabulary for `kind` and `country`, alias rules, `coord_reference_id` is a geocoder and appears in the `reference_ids` of at least one claim at the place, every place has at least one claim (warning), and for every claim the point equals the place's point exactly unless `coord_override` is set (then it must differ and be within 5 km). `check_coordinates.py` also warns for a place or claim point in the open Atlantic and, with `--duplicates`, lists places of kind point within 1 km of each other.

### data/place_merges.csv (hand-maintained)

A place id is never reused. When two places turn out to be one, the survivor keeps its id and the other id is retired: its row leaves `data/places.csv`, every claim that pointed at it points at the survivor (the context that made it a separate place moves to the claim's `location_qualifier`, and a name worth finding goes to the survivor's `alt_names`), and one row here says where the id went, so an old reference (a published copy, a note) can be resolved with `places.resolve()`.

| column | description |
|---|---|
| `retired_place_id` | The retired id (primary key). Never a row of `data/places.csv` again; no claim may use it. Rows sorted by this column. |
| `merged_into_place_id` | The survivor: a live row of `data/places.csv` (foreign key `places.place_id`; a retired id is not a survivor). |
| `retired_name` | The name the retired place had. |
| `note` | Why the two are one place and the source for that. |

Validator checks: header, sorted, no repeated or blank value, the retired id is not in `places.csv`, the survivor is, and no claim uses a retired id (the error names the survivor). `build/` does not carry the table; it is part of `data/`.

## Derived values

Not stored in the claim files; rebuilt by `common.load_all_claims()` and carried in `build/all_claims.csv` (the place and value columns have the same names and values as before the places table; the two name columns are new next to the id columns that replaced the old text):

| column | derived from |
|---|---|
| `location_name` | place name and `location_qualifier` (`scripts/places.py`, `display_name`): qualifier token `vicinity` -> `vicinity of NAME`; other qualifier text -> `NAME (text)` |
| `place_name`, `country`, `region`, `coord_reference_id`, `coord_source_note` | the place row (new columns) |
| `location_temporal_offset_days` | `location_date` minus `date` in days; blank when `location_date` is blank |
| `strength_status` | `destroyed` when the `destroyed` flag is true, else `strength_json.status`, else `unknown` |
| `engaged_with_names` | the display name of each unit in `engaged_with` (`<adjective> <unit_name>`, `common.display_name`), then the entries of `engaged_note` (`scripts/unit_refs.py`) |
| `composing_units_names` | the unit name of each unit in `composing_units` (the display name when the unit's nation differs from the claiming unit's), each followed by its qualifiers from `composing_text`, then the other `composing_text` entries |
| role `location` of a `gazetteer_geocoder` reference | `build_references.derive()`; not stored in `claim_reference_roles.csv` |

The flags `established`, `disestablished` and `destroyed` are kept, because they are not derivable from other columns.

## units columns (`data/units.csv`)

| column | type | required | meaning | constraints |
|---|---|---|---|---|
| `unit_id` | string | yes | Stable unit key. Primary key. | pattern `^[A-Z]{2,4}(-[A-Z0-9]+)+$` |
| `unit_name` | string | yes | Unit name only. |  |
| `nationality` | string | yes | Nationality: the `name` of a row of [`data/nationalities.csv`](#nationalities-columns-datanationalitiescsv) (US, UK, Canada, Germany, Poland, France, Belgium, Netherlands, Czechoslovakia, Allied ...). | foreign key to `nationalities.name` |
| `echelon` | string | yes | Organisational level (see vocabulary). | vocabulary `echelon` |
| `branch` | string | yes | Service or arm (see vocabulary). | vocabulary `branch` |
| `theater` | string | yes | Primary theater of the unit (single value). Claim rows carry their own theater, which may differ (since 9 November 2026). | vocabulary `theater` |
| `parent_unit_id` | string | no | Fixed organic parent unit, used for battle groups and combat commands (their parent division). Blank for units whose parent changes with time; use the claim column `parent_unit_id` and the command relations (`data/command_relations.csv`) for time-dependent parents. | pattern `^[A-Z]{2,4}(-[A-Z0-9]+)+$`; foreign key to `units` |
| `record_status` | string | yes | `placeholder` (identity only, no claim file; not a claim about location), `partial` (claim file known to be incomplete) or `active` (claim file exists). Exactly the placeholders have no claim file (the validator checks it). The former column `parent_only` said the same and was removed. | vocabulary `record_status` |
| `formed_date` | string | no | Formation or activation date of the unit, or of the designation the record uses (see `unit_note`), as given by `formed_date_source`: `YYYY-MM-DD`, `YYYY-MM` or `YYYY`; blank if unknown. It is not the date the unit arrived in the theater. | pattern `^[0-9]{4}(-[0-9]{2}(-[0-9]{2})?)?$`; must be a real date |
| `formed_date_source` | string | no | URL of the page that gives `formed_date`. Required when `formed_date` is set. | URL |
| `initial_parent_unit_id` | string | no | Placeholder-level hint: the formation the unit is listed under in `initial_parent_source` as of `initial_parent_as_of`. Blank where no source clearly gives it. Not an organic-versus-attached statement and not a claim: time-dependent parents of claim rows go in the claim column `parent_unit_id` and the command relations (`data/command_relations.csv`). Different from `parent_unit_id` (fixed organic parent of battle groups). | pattern `^[A-Z]{2,4}(-[A-Z0-9]+)+$`; foreign key to `units` |
| `initial_parent_as_of` | string | no | Date the listing applies to, `YYYY-MM-DD` or `YYYY-MM` (for example `1944-06-06` for the German 6 June 1944 order of battle). Set together with the two other `initial_parent_*` columns or not at all. | real date |
| `initial_parent_source` | string | no | Source token for the listing. | vocabulary `source_token` |
| `component_of_note` | string | no | Free text on the placeholder parent link, for example why it is blank or that the source lists the unit under two formations. |  |
| `unit_note` | string | no | Free text on the unit's identity: renames, reconstitutions, lineage caveats, uncertain Western Front service. |  |
| `listing_source` | string | no | Semicolon-separated source tokens naming where the unit was found when the placeholder was created. A listing is not evidence of a date or place. | tokens from vocabulary `source_token` |

`domain` (added 4 November 2026, Scott's decision to collect air units and ships where sources give them): blank or `ground` (the default), `air` or `naval` (vocabulary `domain`). Only ground units feed the main outputs (`build/all_claims.*`, `claims.geojson`, `units.*`, coverage, places counts, operations, command relations); air and naval units and their claims are written to `build/other_domains/units.csv` and `build/other_domains/claims.csv` (same columns as `all_claims.csv`) and are not used yet; command relations whose subject is an air or naval unit are written to `build/other_domains/command_relations.csv` (air-naval pilot, 13 November 2026; see `docs/air_naval_pilot.md`). The main `build/units.csv` keeps its columns (no `domain`). `scripts/validate.py` checks the value; the claim files of air and naval units follow every claim rule. Flak units (Luftwaffe flak corps, divisions, regiments and battle groups) are domain ground (Scott, 4 November 2026). Places used only by air or naval claims stay in `build/places.*` with 0 claims; a place with no claims is acceptable (Scott, 4 November 2026).

**Units below division level** (Scott, 4 November 2026): Units below division level (Scott, 4 November 2026): record regiments, battalions, brigades and companies only when a source traces them up the chain to a parent division or higher (for example H Company, 116th Infantry, 29th Division); leave out small units that cannot be traced (a bare "H Company"). Divisions and above stay the focus. The link to the parent is recorded without breaking the blank-parent rule for claims: a fixed organic parent goes in `units.csv` `parent_unit_id` with an `organic` relation in `data/command_relations.csv`; an attachment (for example an army assault-gun brigade) is an `attached` relation only; the claim column `parent_unit_id` stays blank. The schema already allows `regiment/battle_group` and `battalion` (no echelon letter in the id); companies use echelon `company` (added 4 November 2026 with Scott's approval; rank 0, no echelon letter in the id). **Independent units (Scott, 4 November 2026, 08:53):** independent units of regiment size or larger (regiments, brigades, Kampfgruppen, improvised corps and deputy corps commands) get their own unit entries even with no parent (units.csv `parent_unit_id` blank); units smaller than a regiment still need a traceable parent chain (so heavy Panzer Battalion 506, a battalion with no traced parent, stays out, while Fallschirmjäger-Regiment 9 goes in under the 3rd Fallschirmjäger Division). Old rule: every unit below division level needed a traced parent; new rule: only units below regiment size do. **Irregular forces (Scott, 12 November 2026):** resistance groups, partisan bands and other irregular forces get unit entries only once they are organised into formal military units with a command chain (for example the Dutch Stoottroepen); loose cells and networks (for example the Dutch KP, OD and RVV) are not entered as units. Record their existence, dates and strength in the private notes. The small-unit rule above still applies to the formal units. See `docs/HANDOFF.md` standing rule 21.

Rows are sorted by `unit_id`. Units with `record_status = placeholder` have no claim file; they exist so that `parent_unit_id`, command relations, `engaged_with` and `composing_units` ids resolve and so that coverage can be tracked (see "Placeholder units" in `docs/methodology.md`). A placeholder is not a claim about where the unit was. When a claim file is added for a placeholder, run `python scripts/promote_placeholders.py` (sets `record_status = active`). `scripts/validate.py` checks every parent id against `units.csv`, that `record_status` agrees with the existence of a claim file, that the nationality is a row of `data/nationalities.csv` and the unit id starts with that row's code, that `formed_date` is a real date with a source URL, and that `unit_name` is unique within a nationality. `python scripts/build.py` writes `build/coverage.csv` and `docs/coverage.md`.

### data/unit_lineage.csv (hand-maintained; `schema/unit_lineage.schema.json`)

Lineage links between unit records. A renamed, rebuilt or merged formation keeps its own record in `data/units.csv` (see [../docs/methodology.md](../docs/methodology.md), "One record per lineage page"); a row here says that the successor record continues the predecessor record, from when, of what kind and on what source. It is not a command relation and never changes a claim.

| column | type | required | meaning | constraints |
|---|---|---|---|---|
| `lineage_id` | string | yes | Stable key `UL001` onward. Never reused. | pattern `^UL\d{3,}$`, unique |
| `predecessor_unit_id` | string | yes | The earlier unit record. | a `unit_id` of `data/units.csv` |
| `successor_unit_id` | string | yes | The later unit record. | a `unit_id`, not the predecessor |
| `kind` | string | yes | How the successor continues the predecessor. | vocabulary `lineage_kind` |
| `effective_date` | string | yes | When the successor takes over the lineage. | `YYYY`, `YYYY-MM` or `YYYY-MM-DD`, 1939-1945; not before the predecessor's `formed_date` |
| `date_basis` | string | yes | Where the date comes from. | vocabulary `relationship_date_basis` |
| `reference_ids` | string | yes | `;`-separated reference ids. | each in `data/references_meta.csv` |
| `note` | string | no | What the source says (paraphrased) and any conflicting date. |  |

Rules checked by `scripts/validate.py` (through `scripts/lineage.py`): unique ids, sorted by `lineage_id`; no duplicate predecessor-successor pair; the links form no cycle (a unit cannot be its own ancestor); both ends exist. Both linked units carry a `unit_note` that names the other record. Build outputs `build/units.csv` and `build/units.json` repeat `data/units.csv` and add `predecessor_unit_ids` and `successor_unit_ids` (`;`-separated in the CSV, lists in the JSON), derived from this table.

### Coverage outputs (`build/coverage_by_unit.csv`, `build/coverage_by_month.csv`, `build/review_queue.csv`)

Derived by `scripts/coverage.py` during `scripts/build.py`; columns and ranking are defined in [../docs/coverage_report.md](../docs/coverage_report.md). They read the claims, units and reference families and change nothing.

## nationalities columns (`data/nationalities.csv`)

Lookup table, hand-maintained, sorted by `code`. It is the single list of nations: `units.nationality`, `claims.nationality` and `operations.nationality_scope` are foreign keys to its `name`, and the adjective used in names (the derived display names of `engaged_with_names`, `composing_units_names` and the `higher_name` of `build/command_relations.csv`) comes from here instead of from code.

| column | meaning | constraints |
|---|---|---|
| `code` | Primary key: the prefix of every `unit_id` of this nation (GER, US, CAN, ...). | 2 to 4 capital letters; unique |
| `name` | The value used in the `nationality` columns and the lowercase folder under `data/claims/` (Germany, US, UK, Canada, ..., Allied). | unique; not `All` (reserved for operation scopes) |
| `adjective` | Adjective used in display names ("German", "British", "US"). | required |
| `alt_adjectives` | Further adjectives accepted when matching opponent and component names (the migration and the validator's name check), `;`-separated (US: American). | optional |
| `alliance` | Side: `Allied` or `Axis` (vocabulary `alliance`). | vocabulary |
| `kind` | `nation`, or `multinational` for combined headquarters (vocabulary `nationality_kind`). | vocabulary |
| `note` | Scope of the row, folder and id conventions. | required |

How the former spellings map: the unit id prefix is `GER`, the nationality value is `Germany` (units, claims, folder `germany`) and the operation scope is now also `Germany` (it was `German`); "German" is only the adjective in names. The three `Allied` units (AFHQ, SHAEF, First Allied Airborne Army) keep the explicit value `Allied` of kind `multinational`: no source in the table says which nation staffed them, so no nationality was assigned.

## Foreign keys

The references between tables are declared as `foreignKeys` (Frictionless Table Schema style) in `claims.schema.json`, `units.schema.json` and `relations.schema.json`, and enforced by `scripts/validate.py` (a blank value is allowed; a `separator` marks a column that holds a list of keys; `alsoAllowed` names accepted extra values):

| from | column | to |
|---|---|---|
| claims | `unit_id`, `parent_unit_id` | units.`unit_id` |
| claims | `engaged_with`, `composing_units` (`;` lists; `unknown` also allowed) | units.`unit_id` |
| claims | `nationality` | nationalities.`name` |
| claims | `operation_id` | operations.`operation_id` |
| claims | `reference_ids` (`;` list) | references_meta.`reference_id` |
| units | `parent_unit_id`, `initial_parent_unit_id` | units.`unit_id` |
| units | `nationality` | nationalities.`name` |
| operations | `parent_operation_id` | operations.`operation_id` |
| operations | `nationality_scope` | nationalities.`name` (or `All`) |
| operations, operation_relations | `reference_ids` (`;` list) | references_meta.`reference_id` |
| operation_relations | `from_operation_id`, `to_operation_id` | operations.`operation_id` |
| operation_exceptions | `claim_id` / `operation_id` | claims.`claim_id` / operations.`operation_id` |
| coordinate_exceptions | `claim_id`, `other_claim_id` | claims.`claim_id` |
| claim_key_exceptions | `claim_id`, `other_claim_id` | claims.`claim_id` |
| retired_claims | `replaced_by_claim_id` | claims.`claim_id` |
| claims | `place_id` | places.`place_id` |
| places | `coord_reference_id` (blank for a hand-worked point) | references_meta.`reference_id` |
| place_merges | `merged_into_place_id` | places.`place_id` |
| claim_reference_roles | `claim_id` / `reference_id` | claims.`claim_id` / references_meta.`reference_id` |
| command_relations | `subject_unit_id`, `higher_unit_id` (blank only for an `unknown` placeholder) | units.`unit_id` |
| command_relation_claims | `relation_id` / `claim_id` | command_relations.`relation_id` / claims.`claim_id` |
| command_relation_overlaps | `relation_id_a`, `relation_id_b` | command_relations.`relation_id` |

Not foreign keys: `conflict_group_id` (a group exists as the set of claims that share the id), `engaged_note` and `composing_text` (free text; the validator checks they do not repeat the name of a unit that has an id). `claims.schema.json` also declares `repeatedColumns`: the columns repeated from the unit table on every claim (`unit_name`, `nationality`, `echelon`, `branch`) must equal `data/units.csv` (`theater` was repeated too until 9 November 2026; it is now per row, see "Theater" under Vocabularies). The primary keys of the side tables, and the natural keys declared as `uniqueTogether` (the command-relation tables), are checked for uniqueness.

## unit_id pattern

`NATION-TYPE-NUMBER+ECHELONLETTER`, all upper case.

- Nation: the `code` of the unit's row in `data/nationalities.csv`: `US`, `UK`, `CAN`, `GER`, `POL`, `FR`, `BEL`, `NL`, `CZ`, `ALL` (combined Allied headquarters such as SHAEF). The validator requires the prefix to equal the code of the unit's nationality. The id is an opaque stable key: the attributes it spells (nation, type, echelon letter) are not re-derived and the id is never renamed when they change.
- Type: `INF`, `ARM`, `ABN` (airborne), `TNK` (tank brigade), `PZ` (panzer), `SSPZ` (SS panzer), `SSPG` (SS panzergrenadier), `FJ` (Fallschirmjaeger, also Fallschirmjaeger corps), `LL` (Luftlande), `COR`, `ARMY`, `AG`, `PZG` (panzer group), `OBW` (OB West), `OKW`, `SHAEF`; placeholder additions: `VG` (Volksgrenadier division), `PG` (panzergrenadier), `SSGEB` (SS mountain), `SSGR` (SS grenadier), `LFD` (Luftwaffe field division), `RES` (reserve division), `DIV` (numbered or z.b.V. division), `PZB` (Panzer-Brigade), `PZA` (panzer army), `FJA` (parachute army), `AA` (Armee-Abteilung), `PZ`/`SSCOR`/`LFC` for panzer, SS and Luftwaffe field corps, `VAK` (Volks-Artillerie-Korps), `OBNW`/`WBN` (other HQs), `CDO` (commando brigade).
- Echelon letter: `G` army group, `A` army, `C` corps, `D` division, `B` brigade, `H` other HQ (vocabulary `echelon_id_letter`). A regiment, a regiment-sized battle group (Kampfgruppe) and a battalion have **no** echelon letter: they are identified by the type code and the name or number (`GER-FJR-006`, `GER-KG-FREY`, `GER-SSHPZ-101`). The validator checks one direction: an id that ends in a digit and one of the six letters must have the matching echelon (so `...D` is a division). Divisions and larger formations that are only a placeholder may also be without a letter (for example `GER-DIV-172`; ids are never renamed). The one exception is the combat command: `US-CCA-002D` and `US-CCR-004D` end in the `D` of the division they belong to, and their echelon is `regiment/battle_group` (pattern `combat_command_pattern`).
- Examples: `US-INF-029D`, `GER-PZ-021D`, `UK-ARM-011D`, `CAN-INF-003D`, `GER-SSPZ-001C` (I SS Panzer Corps), `GER-SSPZ-001D` (1st SS Panzer Division).
- Units without a number use a word: `GER-PZ-LEHRD` (Panzer Lehr), `UK-ARM-GRDD` (Guards Armoured), `GER-PZG-WESTA` (Panzer Group West), `GER-AG-00BG` (Army Group B).
- Battle groups and combat commands: `GER-KG-<NAME>` for a Kampfgruppe (for example `GER-KG-FREY`; unnamed ones use a number or parent code, for example `GER-KG-265`, `GER-KG-002PZ`) and `US-CCA-002D` for Combat Command A of the 2nd Armored Division. Their `echelon` is `regiment/battle_group` and the units.csv `parent_unit_id` points at the parent division (the organic parent).
- A regiment or battalion that is only an opponent or a component has no echelon letter and the type names the arm: `GER-FJR-006` (6th Fallschirmjäger Regiment, echelon `regiment/battle_group`, the one value for a regiment and a regiment-sized battle group), `GER-SSHPZ-101` (SS Heavy Panzer Battalion 101, echelon `battalion`). Both placeholders keep their letterless ids because that is the convention, not an omission (review item 6).
- The id is the same on every row of the unit and equals the claim file name.

## Free-text conventions

- `composing_units`: unit ids, listed when first given or when they change; blank (and `composing_text` blank) means unchanged from that unit's previous row; `unknown` means no data. Items are separated by `; `. `composing_text` holds what is not a unit of the table, with the qualifier form `<unit_id> (<qualifier>)` for a listed unit (`GER-PZ-002D (elements)`).
- `engaged_with`: enemy unit ids separated by `; ` (for example `GER-INF-352D; GER-INF-716D`). Blank = no combat that day; `unknown` = combat with no opponent identified. `engaged_note` holds an opponent that is not a unit, as written.
- `commander`: rank and name as given by the sources; command changes are written like `X (killed 12 June); Y from that evening`.
- `source`: URLs separated by ` | `. The coordinate source is not in it: it is on the place (`coord_reference_id`, `coord_source_note`) or, for a claim with its own point, in `coord_override`.
- `location_qualifier`: what is specific to the claim about the place, in the sources' words (`division HQ Le Molay-Littry`, `point = Cheux`); the first token `vicinity` means the claim says "vicinity of" the place.
- `operation_id`: one value. A row that two operations both claim (an operation and the operation it supported) takes the more specific or the larger one and the other is linked in `data/operation_relations.csv`.
- `current_activity`: short lower-case phrase (about 120 characters at most), no trailing period; free text, not a vocabulary. Describe the one action the sources document on that date at that place, in the sources' own terms (who did what, where). Do not state a direction, aim or result the sources do not give (for example "attacking from the bridgehead" when the source says the attack was postponed or contained), and do not join several actions with `;`: use `notes` for the rest. `scripts/validate.py` warns on long or hedged activities.

## Command relations

Command is not stored in the claim files. It is a table of intervals, with the claims as evidence:

- **`data/command_relations.csv`** (master, one row per relation, ids `CR0001`...): one interval of one relationship between a subordinate unit and a higher unit. Columns: `relation_id`; `subject_unit_id`; `higher_unit_id` (blank only for an explicit `unknown` placeholder, with a `note` saying what is unknown); `relationship` (vocabulary below); `valid_from` / `valid_to` (first and last day, inclusive; blank `valid_to` = no end recorded), with `valid_from_latest` and `valid_to_earliest` when only a range is known, optional `valid_from_time` / `valid_to_time` (`HH:MM`); `valid_from_basis` (vocabulary `relation_start_basis`: a sourced basis, or `claim_date` when nothing dates the start and `valid_from` is the first claim that lists the relation); `valid_to_basis` (vocabulary `relation_end_basis`: a sourced basis, `inferred_from_next_claim`, or `open_at_last_claim`); `end_unknown`; `change_undated`; `date_basis` (where the evidence comes from; feeds the `support` column of the derived table); `ordered_date` (the day the order was issued, never after `valid_from`); `status` (`preferred`, or `alternate` / `disputed` for a relation known only from competing claims); `note`. The natural key (`subject_unit_id`, `higher_unit_id`, `relationship`, `valid_from`, `valid_to`, `status`) is unique, and one (subject, higher, relationship) can have several intervals (it ended and came back).
- **`data/command_relation_claims.csv`** (evidence, one row per claim-relation link): `relation_id`, `claim_id`, `seq` (position in the claim's list), `role` (`asserts_start`, `asserts_end`, `asserts_start_and_end`, `observed_during`: what a claim of the subject unit says about the dates, which must agree with the stated columns; `listed_by_higher_unit`: the claim belongs to the HIGHER unit and lists the subject as a component, so it is evidence for the relation but not one of its own relationships, see below) and the `stated_*` columns, which keep exactly what the claim itself stated for that relation (`stated_effective_from`, `stated_effective_from_latest`, `stated_effective_time`, `stated_ordered_date`, `stated_effective_to`, `stated_effective_to_earliest`, `stated_effective_to_time`, `stated_effective_to_basis`, `stated_date_basis`, `stated_note`). The master interval is the merge of what its claims stated; the `stated_*` columns are the audit trail. A link of role `listed_by_higher_unit` (the claim is the higher unit's, for example a corps claim whose `composing_units` names a division attached to it) needs a `stated_note` (what the claim said about the unit), states a date only if the claim gave one, does not appear in the listing claim's rebuilt `command_relationships`, takes the next `seq` after the claim's own relations, and requires the subject to be listed in the claim's `composing_units`; a relation whose subject has no claim of its own (a placeholder unit) is evidenced this way. Relationships whose subordinate formation is not a unit of the table at all are kept in [`docs/deferred_relations.md`](../docs/deferred_relations.md). References stay with the claim (`reference_ids`, `data/claim_reference_roles.csv` role `command_relationship`).
- **`data/command_relation_overlaps.csv`**: every contradictory overlap, documented. Two preferred relations of one subject contradict each other when they have the same relationship class (`assigned` and `unspecified_subordination` count as one class), different higher units of the same echelon and overlapping intervals. Such an overlap is accepted only if listed here (`kind`: `transfer_dates_differ` or `concurrent_by_source`, with an explanation); an unlisted or stale entry is a validator error. Concurrency across echelons (a division assigned to an army and attached to a corps) is by design and not an overlap. Nothing is resolved here: the two intervals stay as the sources give them.

**`build/command_relations.csv`** is derived from the master table (preferred relations except `organic`): it adds `subject_name`, `higher_name`, `support` (`documented`, `table` or `inferred`), `source_claim_ids` (the preferred claims that list the relation, oldest first) and `last_listed_date` (the date of the latest of those claims; the last observation, see "Reading a command interval"). `python scripts/build.py --check` fails if the file differs from what the tables give.

A claim's **list of relationships is rebuilt** from these tables: `common.load_all_claims()` (and the validator and the audits) add the former `command_relationships` text to every claim, and `build/all_claims.csv` carries it as a derived column after `parent_unit_id` (compact JSON list of `{"unit_id", "relationship", effective_from, effective_from_latest, effective_time, ordered_date, effective_to, effective_to_earliest, effective_to_time, effective_to_basis, note, date_basis}` in that key order; `unit_id` null for a placeholder; blank when the claim lists no relation). It is not a column of the claim files. To record a claim's command situation: add the relations it lists to the master table (extend the interval of an existing relation, or add a new one), add one row per relation to `data/command_relation_claims.csv` with the `stated_*` values the claim gives, and set `parent_unit_id`; `scripts/validate.py` checks the links, roles, intervals and overlaps, and `python scripts/build.py` regenerates `build/`. `scripts/migrate_command_relations.py` (run once) moved the former JSON cells into the tables and can re-check the migration (`--verify REF`).

Flags: `end_unknown` is `true` for a relationship that is temporary by nature (anything but `organic`, `assigned`, `unspecified_subordination` and `unknown`: `attached`, `operational_control`, `administrative_control`, `reserve`, `supporting`, `coordinating`) whose end no source dates, so `valid_to` is only inferred from the unit's next claim or still open. A standing relationship without a sourced end is `false`: it ends when another one replaces it. `change_undated` is `true` on both relations of a parent change that no source dates (five German changes of June 1944); the change fell between `valid_to_earliest` of the outgoing relation and `valid_from` of the incoming one, and nothing is guessed inside that range.

`parent_unit_id` is the **operational parent on the row's date**: the formation the unit was attached to or operating under that day, otherwise its standing parent. It must also be the higher unit of one of the claim's relations. The **standing parent is recorded only as a relation**, `organic`, `assigned` or `unspecified_subordination`: when an `attached` or `operational_control` relation exists, `parent_unit_id` must be that relation's higher unit and the standing parent stays a relation of the claim (an independent brigade attached to a division for an assault is `attached` to the division and `assigned` to the army or corps that holds it). If the standing parent is not known, say so with a relation of relationship `unknown` (no higher unit, a note). A claim never lists a relation that only started on a later date: `valid_from` (and `stated_effective_from`) says when it began and the claim date decides what applies. For a battle group, the `parent_unit_id` in `data/units.csv` must be a relation of every claim as `organic`. Add a formation to `data/units.csv` (as a placeholder unit if it has no claims) rather than leaving `higher_unit_id` blank: the validator rejects a blank higher unit for any relationship except `unknown`.

How to choose the value (the full definitions are in the table below):

- `organic` is only for a constituted component: a regiment or battle group of its own division, a battalion of its own regiment. A division, corps or army under a higher headquarters is never `organic`; the validator warns when it is.
- `assigned` when the source says assigned, or names the unit as a standing member of the headquarters' order of battle without attachment language. Army to army group and corps to army links from narrative histories are normally `assigned`.
- `attached` only where the source says attached or shows a temporary tasking.
- `unspecified_subordination` when the source shows the subordination but does not distinguish assigned from attached, for example the CMH ETO-OB assignment tables' single corps column (the army and army-group columns are separate and are recorded as assigned or attached). Never convert it to `assigned` or `attached` without a source.
- `operational_control`, `administrative_control`, `supporting` and `coordinating` describe a different kind of authority and can sit beside a standing entry (for example SHAEF with operational control over 6th Army Group on 15 September 1944; 21st Army Group coordinating 12th Army Group until 31 August 1944). A retained theater or territorial function is not an `administrative_control` link: AFHQ kept supply, administration and civil affairs "in the area overrun" on 15 September 1944, which the source does not state as control of the army group or of Seventh Army, so AFHQ is listed as `unknown` with a scoped note.
- Entries written before 25 October 2026 used `organic` for every standing parent; they were converted by the Batch 1 review ([`docs/review/review_changes.md`](../docs/review/review_changes.md), "Systemic changes"): table-derived links became `unspecified_subordination`, other formation-to-higher-HQ links became `assigned`.

A claim lists one relation per higher headquarters. When the kind of authority changes during the claim's period (for example 21st Army Group's coordination ending on 31 August), give the relation a `valid_to` and say so in its `note`; put the change history in the claim's `notes`.

### Validity of a relationship

A claim's list of relations is a statement about one dated claim row, not a standing fact; the master interval says how long the relation held. `valid_from` and `valid_to` bound it when a source gives them. **A missing end never means the relationship held indefinitely**: it means no source records one. Wherever a source dates an end, give it, especially for `attached` and `operational_control` (temporary by definition). Where none does, the master table closes the interval on the day before the unit's next claim that no longer lists the relation (`valid_to_basis` = `inferred_from_next_claim`, with `valid_to_earliest` the last claim that lists it) and sets `end_unknown` to `true`; a relation still listed by the unit's latest claim stays open (`open_at_last_claim`). The validator prints a count of the claim entries behind such inferred ends, and `scripts/audit_command_location.py` lists their claim ids. `build/command_relations.csv` (derived by `scripts/build.py` from the master table: names, a `support` column and the evidence claim ids added; every preferred relation except `organic`, all nationalities and dates, explicit `unknown` placeholders included with a blank higher unit) is the table `scripts/who_controls.py` reads. Its `support` column says `documented` (narrative or order dates), `table` (CMH assignment table dates) or `inferred`. The claims stay the evidence; the master table is an interpretation of them and the derived table is rebuilt, never edited. `python scripts/who_controls.py US-ARM-002D 1944-08-28` answers "who held this unit on this date" from it; where only an `unknown` placeholder covers the date it says no higher headquarters is recorded.

Order and effect can differ: the 35th Division was attached to V Corps by an order on the evening of 27 July and V Corps took control on 28 July; the relation keeps both (`ordered_date` 27 July, `valid_from` 28 July). Where a table date and a narrative date differ, the relation keeps the one it states in `date_basis` and the other goes in the `note`.


### Reading a command interval

A relation says that a subject unit stood in a relationship to a higher unit from `valid_from` to `valid_to`. Not every day of that interval is evidenced: the claims that list the relation are observations (`data/command_relation_claims.csv`), and the interval joins them. The columns separate what a source says from what the table infers:

| what a reader wants to know | where it is |
|---|---|
| Is the start sourced? | `valid_from_basis`: `order`, `assignment_table` or `narrative` are sourced; `claim_date` means no source dates the start and `valid_from` is the first claim that lists the relation; `inferred` is an inference |
| Is the end sourced? | `valid_to_basis`: `order`, `assignment_table` or `narrative` are sourced; `inferred_from_next_claim` (the day before the unit's next claim that no longer lists the relation) and `open_at_last_claim` (still listed by the unit's latest claim, blank `valid_to`) are not |
| The earliest and the latest plausible transition | `valid_from_latest` (start between `valid_from` and this date) and `valid_to_earliest` (end between this date and `valid_to`); both blank when a single date is given |
| The last date on which a claim lists the relation (the last observation) | `last_listed_date` in `build/command_relations.csv` (derived, not a master-table column): the date of the latest preferred claim that lists the relation; for an inferred end it equals `valid_to_earliest` |
| The date through which the relationship is evidenced | `last_listed_date`; after it the relationship is a carry-forward, not an observation |
| Is a temporary relationship's end unknown? | `end_unknown` true (kinds that are temporary by nature, see "Flags") |
| Is a parent change undated? | `change_undated` true (both relations of the change) |
| How good is the evidence overall? | `support` in `build/command_relations.csv`: `documented` (narrative or order dates), `table` (CMH assignment-table dates) or `inferred` |

**How the end counts relate.** On 26 October 2026 the master table has 379 relations (375 on `main`, plus five added and one removed on branch `open-items-oct26`: CR0376 to CR0380 added, the placeholder CR0037 removed). By end basis: 200 `open_at_last_claim`, 137 `inferred_from_next_claim`, 30 `assignment_table`, 11 `narrative`, 1 `inferred` (CR0036). `end_unknown` is true on 54 of them: 17 of the 200 open ends and 37 of the 137 inferred-from-next-claim ends. The two sets measure different things:

- A **temporary** relationship (`attached`, `operational_control`, `administrative_control`, `reserve`, `supporting`, `coordinating`) normally has an end, so a missing sourced end is a real gap: `end_unknown` is true. These are the 54 (open 17, inferred 37).
- A **standing** relationship (`assigned`, `unspecified_subordination`, `unknown`, `organic`) has no expected end: it lasts until another standing relationship replaces it, so a missing end is not a gap and `end_unknown` is false. These are the other 283 open or inferred-from-next-claim ends (open 183, inferred 100).
- For both, `open_at_last_claim` and `inferred_from_next_claim` say how long the *evidence* reaches, not how long the relationship lasted. A standing relationship that is open at its last claim is read as "no replacement recorded", not as "confirmed through the end of the data".
- The 114 starts with basis `claim_date` have the same limit on the other side: the relationship may have begun earlier.

**The staleness rule (`scripts/who_controls.py`).** A relationship is read as certain only up to its `last_listed_date`. For a date *after* the last listing of a relationship whose end basis is `open_at_last_claim`, the answer is `possible`, at any distance from the last listing, and the reason says when it was last listed and how many days earlier. A standing relationship is carried forward until a replacement is recorded, so the answer says "carried forward"; a temporary one has no recorded end. This is the rule that already applied to an end inferred from the next claim (a date after `valid_to_earliest` is `possible`); there is no day threshold, because any threshold would be an invented fact about how long an assignment lasted. Every interval without a sourced end also prints a label with its `last_listed_date` and end basis, whatever its status; an interval with a sourced end (order, assignment table, narrative) is not capped. In the reader's terms: `certain` is observed on that date or between two observations; `possible` is carried forward from the last listing, or an inferred or undated boundary, or a documented overlap of two transfer dates; `UNKNOWN` is a level at which the sources give two candidates and none is observed on the date (or the hour of the change is undocumented). The operational chain applies the same rule at each level, so a chain built on a stale relationship is `possible` at that level and above it.

A hypothetical example: a corps listed as assigned to an army by the unit's claims of 1 October and 20 October, and not by the next one: the relation is evidenced on 1 and 20 October, and everything between them is carried by the interval; the end is the day before the next claim and is an inference (`inferred_from_next_claim`, `valid_to_earliest` 20 October).

### Same-unit splits

A subject unit can have two relations to the same higher unit that touch or overlap in time. This is not a change of parent and not a contradiction; it happens in two ways:

- **One corps, two wordings.** The CMH assignment tables have one corps column, so a corps link from the table is `unspecified_subordination`, while a narrative or an earlier claim may call the same link `assigned`. Where both are stored, the rows share the subject and the higher unit and differ only in the relationship word and the dates their evidence supports. On 26 October 2026 there are 8 such pairs: CR0083/CR0084, CR0091/CR0092, CR0103/CR0104, CR0206/CR0209, CR0218/CR0220, CR0236/CR0237, CR0251/CR0254 and CR0344/CR0345.
- **A placeholder in the middle.** When a claim lists the parent as unknown (a placeholder relation with no higher unit) between two intervals of the same higher unit, the first interval ends the day before the placeholder (`inferred_from_next_claim`), which is a date the evidence reaches and not a date a source gives. On 26 October 2026 this happens once: CR0041, CR0042 and CR0043 (Panzer Lehr and I SS Panzer Corps, 13 to 26 June 1944). There are 22 placeholder relations in all; the other 21 do not have the same higher unit on both sides.

**How to read them.** Treat the rows of a split as one continuous interval from the earliest start to the latest end of the rows (each pair note states it); the corps did not change. A same-unit split is never a contradictory overlap (the higher unit is the same), so `data/command_relation_overlaps.csv` has no row for it and the validator does not ask for one. `who_controls` names the same corps for every date of such a pair; where the two rows overlap it prints both lines. No rows were merged and the split itself changed no date: each row keeps the wording and the evidence of its own source (CR0209 and CR0254 later moved to the start the CMH table gives, see "Start of a table-based interval" below, and the pair note of CR0206 and CR0209 states the interval that results). The `note` of every relation in a pair contains a sentence that starts "Same-unit split:"; the note of CR0041 contains one that starts "Placeholder end" and the placeholder CR0042 keeps its own note, because `who_controls` prints a placeholder's note in its answer. Merging the pairs, or ending the earlier row where the later one ends, is a possible later change and needs a decision (docs/review/verification_results.md, "Decisions pending", item 2).

### Start of a table-based interval (`valid_from_basis` `assignment_table`)

**Convention.** When `valid_from_basis` is `assignment_table`, `valid_from` is the date of the CMH ETO-OB assignment-table row in which the entry began: the first row of the unbroken run of rows that list the higher unit in the column that matches the relationship (corps column for a corps link, Army or Army Group Assigned or Attached for an army or army-group link). It is not the date of the first claim that lists the relation. The table is the source of the date; a claim only carries the table row it cites, and the link row of that claim states the table date in `stated_effective_from`, while the claim keeps its own date.

**Consequence for `who_controls` and for any reader.** A relation can therefore start before the first claim of its unit (or before the first claim that lists it). For the days in between the dataset has no claim for the unit, only the table, and `who_controls` reports the relation for those days with the certainty of a table date. This is intended: the table says the unit stood under that headquarters from that row, and leaving the start at the first claim would say that the relation began on the day the dataset first observed it, which is not what the basis `assignment_table` claims. Each relation moved this way says so in its `note` (the old and the new start, the table row, the unit's first claim, and the days that rest on the table alone). Such an interval can be long (up to 284 days in the full set of candidates); the table records an assignment, not the presence of the unit in a theatre or at a place.

**Where it applies on 26 October 2026 (decision V-013, Scott, 26 October 2026: option C, first for the firm cases only).** Applied first to 8 relations: CR0162 (10th Armored Division to Third Army, 23 October to 10 October 1944), CR0164 (to First Army, attached, 17 to 16 December), CR0209 (2nd Infantry Division to V Corps, 1 August to 14 April), CR0223 (5th Infantry Division to XV Corps, 31 January 1944 to 24 December 1943), CR0254 (29th Infantry Division to XIX Corps, 1 August to 14 June), CR0292 (45th Infantry Division to Seventh Army, administrative control, 13 to 1 July), CR0313 (80th Infantry Division to XII Corps, 1 August to 11 June) and CR0353 (94th Infantry Division to XIII Corps, 28 August to 27 July 1944). Batch (a), decided by Scott the same day, applied the convention to the 7 army and army-group relations of the same units: CR0161 (10th Armored Division to 12th Army Group, 23 October to 5 September 1944), CR0208 (2nd Infantry Division to First Army, 1 August to 14 April), CR0227 (5th Infantry Division to 12th Army Group, 4 to 1 August), CR0228 (to Third Army, 4 to 1 August), CR0253 (29th Infantry Division to First Army, 1 August 1944 to 22 October 1943), CR0312 (80th Infantry Division to Third Army, 1 August to 11 June) and CR0352 (94th Infantry Division to Ninth Army, 28 August to 11 July). CR0228 now overlaps CR0225 (First Army, assigned, ending on 3 August, an end inferred from the next claim) on 1 to 3 August; the table lists First Army as attached from 1 August; the overlap is a documented `transfer_dates_differ` row in `data/command_relation_overlaps.csv`, and CR0225 is unchanged. Batch (b), decided by Scott the same day, applied it to the 13 relations that started 1 to 7 days after their table row: CR0096 (82nd Airborne Division to First Army, attached, 18 to 17 December 1944), CR0144 (5th Armored Division to First Army, 29 to 26 August), CR0235 (9th Infantry Division to First Army, 25 November to 20 November 1943), CR0278 (35th Infantry Division to 12th Army Group, 6 to 1 August), CR0288 (44th Infantry Division to 12th Army Group, 5 September to 30 August), CR0305 (79th Infantry Division to 12th Army Group, 3 to 1 August), CR0307 (79th Infantry Division to First Army, 29 to 26 August), CR0325 (83rd Infantry Division to 12th Army Group, 3 to 1 August), CR0326 (83rd Infantry Division to Ninth Army, 10 to 5 September), CR0332 and CR0333 (84th Infantry Division to 12th Army Group and to Ninth Army, 11 to 4 November), CR0360 and CR0361 (103rd Infantry Division to 6th Army Group and to Seventh Army, 6 to 1 November). Three of them overlap the earlier army of the same unit for the days between the table row and the end of that relation (CR0144 with CR0140, 26 to 28 August; CR0307 with CR0301, 26 to 28 August; CR0326 with CR0322, 5 to 9 September); each is a documented `transfer_dates_differ` row in `data/command_relation_overlaps.csv`, and the earlier relation is unchanged. Batch (c), decided by Scott the same day, applied it to the 17 relations that started 8 or more days after their table row: CR0203 (1st Infantry Division to First Army, 15 July 1944 to 1 November 1943), CR0120 (2nd Armored Division to First Army, 18 July 1944 to 24 November 1943), CR0219 (4th Infantry Division to First Army, 19 July 1944 to 10 January 1944), CR0264 (30th Infantry Division to First Army, 15 July to 8 February 1944), CR0343 (90th Infantry Division to Third Army, 19 June to 5 March 1944), CR0322 (83rd Infantry Division to Third Army, 1 July to 4 April 1944), CR0342 (90th Infantry Division to First Army, attached, 19 June to 23 March 1944), CR0140 (5th Armored Division to Third Army, 17 June to 29 March 1944), CR0275 (35th Infantry Division to Third Army, 8 July to 26 April 1944), CR0303 (79th Infantry Division to First Army, attached, 1 July to 29 May 1944), CR0297 (75th Infantry Division to 12th Army Group, 22 to 9 December 1944), CR0214 (3rd Infantry Division to Seventh Army, attached, 13 to 1 July 1944), CR0240 (26th Infantry Division to Ninth Army, 5 September to 24 August 1944), CR0244 (28th Infantry Division to Third Army, 24 to 14 April 1944), CR0289 (44th Infantry Division to Ninth Army, 5 September to 26 August 1944), CR0339 (87th Infantry Division to Third Army, 4 December to 25 November 1944) and CR0239 (26th Infantry Division to 12th Army Group, 5 to 28 August 1944). CR0366 (104th Infantry Division to Ninth Army, `administrative_control`, from 15 October 1944) was left as it is: the "(Admin)" mark first appears in the table row of 15 October, so that row is where this relationship began; the earlier rows list Ninth Army without the mark, which is a different relationship. Five of the 17 start more than 100 days before their first claim (CR0203, CR0120, CR0219, CR0264, CR0343); the stretch before 6 June 1944 is the unit's pre-D-Day period in the European theater and rests on the table alone, and their notes say so. A start moved this way can change the operational chain that `who_controls` prints: an army link that now exists earlier can be chosen as the unit's chain in place of a corps link recorded from a narrative (US-INF-090D on 12 June 1944), and an army whose own parent is not yet recorded for those days ends the chain (US-INF-044D on 4 September 1944). After batch (c) every one of the 157 relations that could be compared started on its table row. Batch (d), decided by Scott on 26 October 2026, covers the other 57: CR0130 (3rd Armored Division to First Army, 15 July 1944 to 20 November 1943), CR0133 (4th Armored Division to Third Army, 20 April to 1 February 1944), CR0157 (7th Armored Division to Third Army, 10 to 5 August 1944), CR0213, CR0283 and CR0291 (3rd, 36th and 45th Infantry Divisions to Allied Force Headquarters, 13 July to 1 July 1944), CR0284 (36th Infantry Division to Seventh Army, attached, 13 July to 1 July 1944), and CR0357 and CR0358 (102nd Infantry Division to 12th Army Group and to Ninth Army, 7 November to 28 August 1944). CR0130 starts more than 100 days before its first claim and says so in its `note`. 44 of the 57 were already on their table row. Four are left as they are and are open items for Scott: CR0105 (101st Airborne Division to I Airborne Corps) and CR0200 and CR0201 (XXI Corps to 6th Army Group and Seventh Army), whose `assignment_table` basis does not match their source, and CR0156 (7th Armored Division to 12th Army Group), whose table row is printed out of order (docs/review/verification_results.md, item 1a). With these four excepted, every `assignment_table` relation now starts on its table row, so the basis `assignment_table` means the date the table entry began and the `note` of each of the 54 relations moved says what the earlier date was. Batches (c) and (d) created no new overlap; the four existing `transfer_dates_differ` explanations that quoted a moved start (CR0140/CR0144, CR0240/CR0242, CR0244/CR0246, CR0322/CR0326) now quote the new one. For a start that is moved to an AFHQ row (CR0213, CR0283, CR0291) `who_controls` now prints AFHQ as a second assigned line for 1 to 12 July 1944, and for the 45th Infantry Division it is the only operational chain on those days, because the Seventh Army link of that division is administrative control.

### Intervals are inclusive; sequences, handovers and the ordered / effective / exercised states

- **`valid_to` is the last day the relationship held (inclusive).** On the day one relationship ends and the next begins, both relations cover the day. Which of the two held at a given hour of that boundary day is unknown unless an hour is recorded: `valid_from_time` and `valid_to_time` (optional `HH:MM`, 24-hour; each needs its date; say in the `note` which clock the source uses; the claim's `stated_effective_time` and `stated_effective_to_time` say what the claim gave) carry it into `build/command_relations.csv`. `python scripts/who_controls.py US-ABN-101D 1944-12-20 12:00` reports UNKNOWN for a level where two headquarters meet on a boundary day and no hour is documented, rather than choosing. There is no `valid_until_exclusive` key: a second convention would make every end date ambiguous.
- **A table observation and an operational transfer are different rows.** A CMH assignment table that lists a unit under a headquarters from a date is a `subordinate_assignment` row (or an `effective_from` with `date_basis` `assignment_table` on a later row); the dated narrative transfer is a `command_change` row. The two are a sequence, not a conflict group, and the table row does not assert control by a headquarters the narrative has not yet reached (101st Airborne Division: CMH table 17 December, VIII Corps operational control from 18 December, VIII Corps to Third Army during 20 December). A conflict group is for two claims that cannot both hold.
- **The immediate operational parent is `parent_unit_id`; higher headquarters follow by hierarchy.** A division under a corps that passes from one army to another has the corps as `parent_unit_id` before and after; the army appears in the corps' own rows. Do not put the army on the division's row only because a table lists it.
- **A temporary attachment that overlaps a table date is modelled with a range.** The 84th Infantry Division was "temporarily attached" to the XVIII Airborne Corps from 20 December (Ardennes p426) while the CMH table lists VII Corps from the same day; the Green Book has the XVIII Airborne Corps still giving orders on 21 and 22 December and the VII Corps officially assuming its front at 1630 on 23 December (p433). The XVIII entry is `attached` with `effective_to` 23 December and `effective_to_earliest` 22 December; the VII Corps entry is `unspecified_subordination` with `effective_from` 20 December and `effective_from_latest` 23 December.
- **Where a location stands for a later or nearby place, say so.** A headquarters row whose coordinate is the nearest later command post (84th Division at Marche on 20 December, the command post being documented there on 21 December) keeps `nearest_later_command_post`; a headquarters place taken from a neighbouring unit's command post is `inferred` (XVIII Airborne Corps, 19 December). A place that is the last listed one rather than the position on the date (Ninth Army at Maastricht, 20 December) is `nearest_earlier_command_post` and the note says "last-known".
- **Ordered, effective and exercised.** Four states can have different dates: *intended* (a plan or tentative selection), *ordered* (an order or alert is given), *effective* (the order takes effect) and *exercised* (the headquarters is shown commanding). The model today keeps them cheaply: `ordered_date` is the order, `effective_from` (with `effective_time`) is the effective date, a narrative row that shows the headquarters acting is the exercised evidence, and an intended-only fact is an `other` row whose `Event definition:` says it is a decision (III Corps, 18 December: Bradley and Patton agree to move the headquarters from Metz to Arlon and earmark three divisions; the attack opens on 22 December). A separate state column is on the roadmap (`docs/roadmap.md`, "Ordered / effective / exercised states"), with the 7th Armored Division's move to St. Vith as the motivating case.
- **Declined, with reasons.** A numeric event confidence beside the location confidence is declined for the third time: `confidence` already scores the location and its sources, the `Event support:` and `Location support:` sentences carry the event side in words, and a second number would repeat `location_basis` and the notes. A `retained_nonoperational_responsibilities` relationship is not added: `unknown` with a scoped note does the job (AFHQ, 15 September 1944). An `engagement_area` location kind is not added: `objective` with `representative_point` says it. An `inferred_from_nearby_unit_hq` basis is not added: `inferred` plus a note naming the neighbour does.

## Location provenance: location_date, location_basis

`latitude`/`longitude` answer "where", `date` answers "when". Many Batch 1 coordinates are command posts that a source lists on a different date from the claim, or town centres standing for a headquarters. Three optional columns record that:

- `location_date`: the date the coordinate is documented for. Set it equal to `date` when a source places the unit there on the claim's date.
- The offset `location_date - date` in days is not stored; `build/all_claims.csv` derives `location_temporal_offset_days`.
- `location_basis`: one value of the `location_basis` vocabulary below. Temporal bases come first: if the coordinate is from another date use `nearest_later_command_post` or `nearest_earlier_command_post`; otherwise say whether the point is a `town_centroid` (a named town standing for a headquarters whose site is not given), a `representative_point`, an `operational_area` point (sector, landing area, bridgehead), `documented_on_date` (a named site or event place for that date), or `inferred`.
- There is no separate location confidence column, and the Batch 2 corrections reconsidered one and again declined it: `confidence` is by definition the score for the location and its sources (see the rubric), `precision_km` and `location_basis` already carry the rest, and a location status column such as confirmed / last_known / interpolated / representative would repeat `location_basis` (documented_on_date, nearest earlier or later command post, operational_area or representative_point, inferred). How well a command event itself is documented is stated in the notes of command_change and activation rows from Batch 2 on, in the sentences `Event support:` and `Location support:` (high, moderate or low, with the reason); the validator warns when a command row with confidence 0.3 or less lacks `Event support:`. The relationship-level support is in `build/command_relations.csv` (`support`). `confidence`, `precision_km` and the basis together say how far the coordinate can be trusted. A coordinate from another date or a town centroid should carry a wider `precision_km` and, where the row's own date is not documented, `confidence` 0.5 or 0.3. Older rows (before Batch 1) are left blank unless their notes say where the coordinate came from.

Validator checks: error when a temporal basis has no date, and for a `landing` row whose coordinate is a `town_centroid` or a command post from another date; warning when `location_date` differs from `date` but the basis is blank or `documented_on_date`, when a corps, army or army-group headquarters is only a town centroid with `precision_km` under 5, and when a corps or army sector is recorded as an exact `front_line_point`. `python scripts/audit_command_location.py` lists the counts per pattern.

### What `confidence` means

`confidence` is the score of the claim's **date and place**: how exactly the location is documented, how many independent source families support it, and (for 0.3) whether the date itself is approximate. The levels are rules, not probabilities, and they are comparable across rows only in that sense.

- It **is not** the probability that the event happened, and it **is not** a measure of how well the event is documented. A command change with a precisely documented date and an approximate headquarters place (a town centre, a representative point) scores 0.3 or 0.5.
- The effect is large: of the 96 `command_change` claims, 12 score 0.7 or more, 63 score 0.5 and 21 score 0.3. A filter `confidence >= 0.7` would remove 84 of them (88%), 16 of which carry an `Event support: high` sentence in `notes`.
- How well the event itself is documented is said in words, in the `notes` sentence `Event support:` (high, moderate or low, with the source; 70 of the 566 claims have one, from Batch 2 on, and the validator asks for it on command rows at 0.3 or less). How well the command relationship is documented is the `support` column of `build/command_relations.csv`.
- For a conflict group the cap applies: the preferred claim is at most 0.7, an alternate or disputed claim at most 0.5, whatever the quality of the sources.
- The column keeps its name for compatibility. A separate numeric event confidence was declined three times (see "Location provenance" and the roadmap); the documented meaning is date and place.

### What a location point can mean

`latitude` and `longitude` are what the claim's point stands for (`location_represents`), and `location_basis` and `precision_km` say how it was fixed and how far to trust it. A point is **usually a place's centre, not the unit's measured position**. As guidance (not a stored column), the two columns classify the 566 claims on 26 October 2026 as follows:

| the point is | rule | claims |
|---|---|---|
| an objective | `location_represents` objective | 68 |
| representative of an area, a line or a route | `location_represents` sector_center (130), main_body (21), front_line_point (62) or approach_route (6), whatever the basis | 219 |
| a headquarters documented on the claim's date | headquarters with basis `documented_on_date` | 38 |
| a headquarters taken from another date or inferred | headquarters with basis `nearest_earlier_command_post` (38), `nearest_later_command_post` (40), `inferred` (3) or `operational_area` (1) | 82 |
| a town centre standing for a headquarters | headquarters with basis `town_centroid` | 142 |
| undetermined without reading the row | headquarters with a blank basis | 17 |

(211 claims have a blank `location_basis`: 194 of them are classified by `location_represents` alone, the 17 headquarters are not.) The mapping of the groups to "observed", "inferred" or "representative" in a given use is the user's choice; the table says which facts are available.

Using the points: plot a point as "the unit was here" only for a headquarters documented on the date, or a main body whose precision is small. A distance between two claim points is the distance between two units only when both points are of that kind, and the sum of the two `precision_km` radii is smaller than the distance. For everything else a point is an indication of the area of operations, with `precision_km` as its radius.

### Note labels

Use short labelled sentences in `notes` so the sources for each kind of statement stay separate: `Event date: ...`, `Location: ...`, `Relationship: ...`. Not every row needs all labels; the reviewed Batch 1 rows use them. The labels are a **controlled vocabulary** (`note_label` in `vocabularies.json`), frozen on 26 October 2026 at the set the data used then (19 labels, 632 uses in 118 of the 566 rows); the validator rejects any other label. The number in each description is how often the label was used when the set was frozen.

| label | what the sentence says |
|---|---|
| `Event date:` | The source for the date of the event, and how the date was fixed (108 uses at the time the set was frozen). |
| `Event definition:` | What event this row means, needed when rows in a conflict group differ in event type or definition, for example a landing against an arrival (106). |
| `Event support:` | How well the event itself is documented, in words (high, moderate, low) with the source; `confidence` scores the location, this sentence the event (70). |
| `Location:` | What the point stands for and which source places it (100). |
| `Location support:` | How well the location is documented, in words, with the source (70). |
| `Location support fallback:` | The location support when the point is only a fallback such as a sector point (1). |
| `Location caveat:` | A doubt about the place name or the point that the row's coordinates do not remove (3). |
| `Location approximate:` | The point is approximate and says how (1). |
| `Coordinates:` | How the numbers were obtained: gazetteer, centroid, measured on a map (55). |
| `Coordinate check:` | The outcome of a coordinate or speed check against another claim (1). |
| `Relationship:` | The source for the command relationship of the row (102). |
| `Command support:` | How well the command event (start of command, hour, date) is documented (1). |
| `Opponents:` | What is and is not covered by `engaged_with` (1). |
| `Objective check:` | Why `location_represents` objective holds on the row date (8). |
| `Commander:` | The source for the commander named in the row (1). |
| `Context:` | Background that explains the row but does not belong to it (1). |
| `Later:` | What later sources or rows show about the same fact (1). |
| `Activity:` | The basis of the row's `activity_status` and, for a change to an existing row, the old value, the new value and the reason (pilot, October 2026; see `docs/activity_status_design.md`). |
| `Search:` | What was searched and not found, and where (1). |
| `Review:` | A later review's correction of the row and what it changed (1). |

**What counts as a label.** The validator looks at the start of every sentence of `notes` (the start of the cell, or after `. `, `; `, `] ` or `) `) for `Phrase: ` or `Phrase (qualifier): `. When the phrase has the shape of a label (a capital letter, then at most two more words, all lower case) it must be one of the labels above, spelled exactly (`Location support:`, not `Location Support:` or `location support:`), otherwise the row fails with `unknown label`. A qualifier in parentheses is free text and does not change the label (`Relationship (sequence):`, `Objective check (Batch 2 review):`). Lead-ins that name a source, a batch or an id are prose and are not checked: `CMH ETO-OB chronology:`, `Breakout-28 p577:`, `Batch 2 review:`, `Wikipedia:` (a capital letter after the first word, a digit or a hyphen makes a phrase prose; `Wikipedia` is the one source name that has label shape and is exempted by name). Labels in the middle of a sentence and the other columns are not checked.

**Adding a label.** Do it in one change (one pull request, one commit): (1) add the label to `note_label` in `schema/vocabularies.json` with a one-line definition (what the sentence says, and when to use it instead of an existing label); (2) add it to the table above (and change the count in the first paragraph); (3) add a line to `docs/changelog.md`; (4) use it in at least one row in the same change, or say why none yet; (5) run `python scripts/validate.py`. If a `scripts/` check needs to read the new label (as `Event support:` and `Event definition:` are read by the validator and the audits), change it in the same commit. A label is not renamed or removed while a note uses it; rewrite the notes in the same change. Before inventing a label, check whether an existing one fits.

## Operations (`data/operations.csv`, `data/operation_relations.csv`, `data/operation_exceptions.csv`)

Claims point at one operation row through `operation_id`. The operations table replaces the earlier free-text columns `campaign`, `operation_name` and `sub_operation_name` (migration: `scripts/migrate_operations.py`; how each claim was moved: `docs/review/operations_backfill.md`).

### data/operations.csv (hand-maintained)

| column | meaning |
|---|---|
| `operation_id` | Stable key, `OP-` plus upper-case words (`OP-EPSOM`, `OP-CAMP-RHINELAND`). Never renamed or reused. |
| `name` | Full name (`Operation Epsom`, `Rhineland campaign`). |
| `short_name` | The short label used by the derived columns and the old data (`Epsom`, `Rhineland`). |
| `alt_names` | `;`-separated other names, including the other side's codename (`Anvil`; `Watch on the Rhine`). |
| `op_type` | `umbrella`, `campaign`, `operation`, `battle` or `phase` (see the table below). |
| `parent_operation_id` | The operation this one is part of (blank for a top-level row). Parent/child is the only containment link; it must be acyclic. |
| `start_date`, `end_date` | Inclusive `YYYY-MM-DD`. |
| `date_basis` | `cmh_streamer`, `official_history`, `secondary` or `derived` (a note says how). |
| `parent_date_exception` | Why the row's dates fall outside its parent's (blank when they do not). Without it the validator warns. |
| `theater` | A `theater` vocabulary value. A child operation has its parent's theater, and a claim has its operation's theater (validator errors). One holding umbrella per front labels rows outside the Western Front operations: `OP-FRONT-EASTERN`, `OP-FRONT-MEDITERRANEAN`, `OP-FRONT-BALKANS`, `OP-FRONT-SCANDINAVIA`, `OP-FRONT-NORTH-AFRICA`, `OP-HOME-GERMANY` (all `date_basis derived`, dates in their notes). |
| `nationality_scope` | A nationality `name` from `data/nationalities.csv` (`Allied`, `Germany`, ...) or `All`: whose name or concept the row is (a German codename is its own row, linked to the Allied battle). Foreign key to `nationalities.name` (also allowing `All`). |
| `reference_ids` | `;`-separated `reference_id`s from `data/references.csv` that source the name and dates. |
| `notes` | Contested boundaries, placement decisions, what the row is for. Required when `reference_ids` is empty or the dates are `derived`. |

`op_type`: `umbrella` is a planning or command umbrella that contains campaigns (Overlord), or a holding umbrella for dates no campaign covers (`OP-PRE-INVASION`, 1 September 1939-5 June 1944: a claim dated before the first CMH streamer needs no campaign; a claim dated before 1 September 1939 is an error; `OP-POST-SURRENDER`, 12 May-31 December 1945 (end a working bound): a claim dated after the last streamer ends needs no campaign; both are `western_europe`; rows of other theaters use the per-front umbrellas `OP-FRONT-*` and `OP-HOME-GERMANY`, which need no campaign at any date); `campaign` is a CMH campaign streamer (`date_basis cmh_streamer`: Normandy, Northern France, Southern France, Rhineland, Ardennes-Alsace, Central Europe) or a named campaign of the official histories (Brittany, Lorraine, Siegfried Line); `operation` is a named operation (Cobra, Epsom, Market Garden); `battle` a battle or siege; `phase` a stretch of a larger operation without a name of its own. The CMH streamers are the only rows that give a claim its derived `campaign`; the others sit in the tree for context.

Examples of the tree: Operation Overlord > Normandy campaign > Operation Neptune > Operation Tonga; Operation Overlord > Northern France campaign > Operation Cobra; Northern France > Brittany campaign > Siege of Brest; Ardennes-Alsace campaign > Battle of the Bulge > Siege of Bastogne; Southern France campaign > Operation Dragoon. Rows that span two campaigns (Lorraine, Siegfried Line) have no parent.

### data/operation_relations.csv (hand-maintained)

`from_operation_id, to_operation_id, relation, reference_ids, note`. Relations other than parent/child: `follows`, `concurrent_with`, `supports`, `succeeded_by`, `related` (vocabulary `operation_relation`). A German and an Allied name of one battle are `related`. Endpoints must exist; a source or a note is required.

### data/operation_exceptions.csv (hand-maintained)

`claim_id, operation_id, reason`: a claim dated outside its operation's dates (a preparation or aftermath row) that is kept on the operation. The validator warns about a claim outside its operation's dates unless it is listed here, and warns about a listed claim that is in fact inside.

### Derived columns (`build/all_claims.csv`, `build/claims.geojson`, `build/operations.csv`)

`build/all_claims.csv` repeats the schema columns, inserts the derived `command_relationships` after `parent_unit_id` (rebuilt from the command-relation tables, see [Command relations](#command-relations)) and appends: `operation` (name of the claim's operation), `operation_type`, `campaign` (the CMH streamer in the chain that covers the claim's date; for a claim whose operation sits in no streamer, or whose streamer does not cover the date, the earliest-starting streamer that does), `operation_name` (the topmost operation or umbrella in the chain whose dates cover the claim's date, blank otherwise, so Overlord never labels a claim after 30 August 1944), `sub_operation_name` (the claim's own operation when it is below that) and `operation_path` (the chain, outermost first, ` > `-separated). `build/operations.csv` lists every operation with its path, depth and claim counts.

Rules checked by `scripts/validate.py`: `operation_id` exists; the chain is acyclic; a child lies inside its parent's dates (warning, silenced by `parent_date_exception`); relation endpoints exist; every row has a source or a note; a claim lies inside its operation's dates (warning, silenced by an exception row); some CMH campaign covers every claim's date (error).

To add an operation: see CONTRIBUTING.md.

## References (`data/references.csv`, `data/references_meta.csv`, `data/claim_reference_roles.csv`, `build/claim_references.csv`, `build/unit_references.csv`)

**Claims point at references directly.** Each claim file has two columns after `source`:

| column | content |
|---|---|
| `reference_ids` | `;`-separated `reference_id`s (`R398;R407;R001`) in `data/references_meta.csv`, in citation order. **The source of truth** for which references support the claim. At least one is required. |
| `source_locator` | where in a reference: `R398: p. 285, 289; R407: p. 36` (reference id, then page, chapter or section; `;` between references). Only ids that are in `reference_ids`. Blank where the citation gives no page. Nothing is guessed: the 158 values were taken from `#pageNNN` fragments of the original URLs. |

The `source` text (URLs separated by ` | `) stays as the readable citation and `strength_json.source` stays as it was. `validate.py` checks that every URL and strength source in them resolves (through `data/references_meta.csv`) to an id in `reference_ids` (error), and warns when an id is listed that no citation text mentions.

**Roles.** What a reference supports is stored in the side table `data/claim_reference_roles.csv` (`claim_id, reference_id, role, basis`), not in the claim file, so that per-unit files stay one-line-per-claim readable. A link has no row (role `general`) unless there is evidence for a more specific role; a link can have several rows. Vocabulary `reference_role`: `event` (what happened), `date`, `location` (the place or the coordinates), `command_relationship`, `strength`, `general`. `basis` says why: `strength_json source`, `named in the Event date sentence of notes` (also Event definition, Location, Relationship) or `named in command_relationships`. The `location` role of a `gazetteer_geocoder` reference is derived, not stored (`build_references.derive()`; 561 rows removed when the places table was introduced), so the file holds only judgments. Roles are inferred conservatively from the claim's own text; most links are `general` and a reviewer may add a row when a source is checked for one part of a claim.

**Independent sources.** `source_family` (in `references_meta.csv` and `references.csv`) groups references that are not independent: every Wikipedia article, in any language, and the Wikipedia API are one family `wikipedia`; the US Army Center of Military History publications and the sites that republish them are `us_army_cmh`; OpenStreetMap/Nominatim is `openstreetmap`; any other site is its host name. A claim with `confidence` 0.9 should cite at least two families (`validate.py` warning). The count ignores references of `source_type` `gazetteer_geocoder` (a geocoder shows where a place is, not that the unit was there); the numbers are in `docs/methodology.md`.

Every URL in a claim's `source` column, every `formed_date_source` URL in `units.csv`, every unit source token (`listing_source`, `initial_parent_source`, for example `LEX`, `WP12AG`) and every `strength_json.source` text maps to one row of `data/references_meta.csv`; `scripts/validate.py` reports an error for a citation that does not.

`data/references_meta.csv` is hand-maintained and holds the stable `reference_id` (`R001`, never reused or renumbered), the normalised `url` (no `#fragment`, `www.ibiblio.org`), the curated `short_title`, `full_citation`, `source_type`, `source_family`, `publisher`, `license_or_status`, `reliability_note`, `used_for`, `accessed_date`, and `link_status` / `link_checked` (written by `build_references.py --check-links`). Optional matching columns: `source_token` (unit source token) and `strength_alias` (`;`-separated strength source texts). `data/references.csv` is generated from it and adds `original_url` (the archived address of a Wayback Machine link), `claims_count` (claims whose stored `reference_ids` list it), `units_count` and `first_claim_id` (the lowest claim_id listing it). `build/claim_references.csv` (columns `claim_id`, `reference_id`, `role`, `locator`) has one row per link and role, built from the stored `reference_ids`, `source_locator` and the roles table; it replaces the earlier derived roles `source` and `coordinates` (now `general` and `location`).

`source_type`: `official_history`, `unit_history`, `assignment_table`, `reference_compilation`, `encyclopedia`, `gazetteer_geocoder`, `monument_or_memorial`, `archive_document`, `news_or_web_article`, `other`. `link_status`: `ok`, `blocked_403` (the server refuses automated requests, as `history.army.mil` does), `not_found`, `error` (timeout or other failure), `unchecked`. A link status records the day of the last check only; web pages move.

To cite a new source: see CONTRIBUTING.md ("How to cite a new source").

## strength_json

Machine-readable schema: [json/strength_json.schema.json](json/strength_json.schema.json); all JSON-in-cell columns: [../docs/json_fields.md](../docs/json_fields.md).

A JSON object (blank if no source gives figures):

```json
{"basis":"reported_actual","as_of":"1944-06-16","vehicles":{"tanks":85},"vehicle_count_type":"operational","source":"Wikipedia Operation Perch","note":"optional caveat"}
```

Keys: `basis` (required), `as_of` (required, `YYYY-MM-DD`, may differ from the row date), `personnel` (integer), `vehicles` (object name -> integer count), `vehicle_count_type` (required when `vehicles` is present), `scope` (`whole_unit`, `sub_force` or `sector`, see the `strength_json_scope` vocabulary; required whenever `personnel` is given, and the validator reports an error when it is missing; if no source says what a figure covers, leave the figure out), `source` (required), `note` (optional). A figure that a source gives for a task force, a line or a sector (for example "for the defense of the new line he had 2,500 men") is not the strength of the whole unit: mark it `sub_force` or `sector` and say so in `note`. At least one of `personnel` or `vehicles` must be present. Guns are not vehicles. Details and basis rules: [../docs/methodology.md](../docs/methodology.md). `status` (`full`, `reduced`, `heavily_depleted`, see the `strength_json_status` vocabulary): the qualitative strength a source states; a record may hold a status alone (basis, as_of and source are then still required). `build/all_claims.csv` derives the column `strength_status` from it.

## Vocabularies

### theater

Theater of the claim row: the front or rear area where the unit was on the claim date (a row may differ from the unit's primary theater in data/units.csv; see the Theater section of schema/README.md). The claim's operation must carry the same theater.

| value | meaning |
|---|---|
| `western_europe` | Northwest Europe and France: the 1940 campaign in the West, the 1940-1944 occupation of France, Belgium, the Netherlands, Luxembourg and the Channel Islands, staging in Great Britain, and the campaign from the Normandy landings to the end of the war in the West (including Germany, Austria and Czechoslovakia as the Western Allies advanced), plus southern France from the Dragoon landings (15 August 1944) on, because the project's Western Front scope includes the Riviera-to-Rhine campaign. |
| `mediterranean` | Italy, Sicily, Sardinia, Corsica and the Mediterranean Sea (southern France only before the Dragoon landing, for example staging in Italy or Corsica; from 15 August 1944 southern France is western_europe). |
| `north_africa` | Libya, Egypt, Tunisia, Algeria and Morocco campaigns (1940-1943). |
| `eastern_front` | Germany/Axis versus the USSR (Soviet Union, Poland, Baltic, Romania, Hungary, Slovakia, Finland), including German territory as the Red Army reached it (East Prussia, Silesia, Pomerania, the Oder front, Berlin). |
| `balkans` | Yugoslavia, Albania, Greece, Bulgaria and the Aegean islands (German occupation, anti-partisan operations and the 1941 and 1944-1945 campaigns). |
| `scandinavia` | Norway and Denmark (the 1940 invasion and the occupation to May 1945). Finland is eastern_front. |
| `home_germany` | Germany as then constituted (the 1937 Reich plus annexed Austria, the Sudetenland, the Protectorate of Bohemia and Moravia and the annexed Polish areas) as a rear or home area: forming, training, refitting and the replacement army (BdE), at places that were not then in a combat zone. Rows in Germany in the path of the Western Allies are western_europe; rows in the path of the Red Army are eastern_front. |
| `pacific` | Pacific Ocean areas and Southwest Pacific, including Japan, the Philippines and the Dutch East Indies. |
| `cbi` | China-Burma-India theater (China, Burma, India, Indochina). |
| `atlantic` | Atlantic Ocean, Arctic convoys and other naval or air units whose operations are mainly at sea. |
| `other` | Anything that does not fit above (for example East Africa or the Middle East). Explain in notes. |

**Theater (decision Scott, 9 November 2026: keep out-of-theater data, each row with its own theater).** Until 9 November 2026 `theater` was one of the columns repeated from `data/units.csv`, so every claim of a unit had the unit's primary theater and rows on other fronts could not be told apart. Now each claim row carries the theater of its own place and date; the unit's `theater` stays its primary theater. Rules: (1) the claim's operation has the same theater (`scripts/operations.py`, error); (2) the CMH campaign streamers are Western Front campaigns, so only `western_europe` rows dated 6 June 1944-11 May 1945 need one (rows of other theaters are filed under their front's holding umbrella and get a blank derived `campaign`); (3) `scripts/check_coordinates.py` has a loose bounding box for each theater. Choosing the value: `western_europe` for the 1940 campaign in the West, the occupation of France and the Low Countries, staging in Britain and the 1944-1945 campaign (also inside Germany, Austria and Czechoslovakia as the Western Allies advanced); `eastern_front` for Poland 1939, the USSR, the Baltic, Romania, Hungary, Slovakia and German territory once the Red Army reached it; `home_germany` for forming, training, refitting and the replacement army inside the Reich of the time at places not then in a combat zone; `scandinavia` for Norway and Denmark; `balkans` and `mediterranean` as in the table. The backfill of 9 November 2026 is described in `docs/methodology.md` ("Theater").

### nationality

Defined by the lookup table `data/nationalities.csv` (see "nationalities columns" below), not by `vocabularies.json`. The `name` is the value used in `units.nationality`, `claims.nationality` and `operations.nationality_scope`; its lowercase form is the folder under `data/claims/`; the `code` is the prefix of every `unit_id` of that nation (GER for Germany, CAN for Canada, ...). Add a row to the table before adding the first unit of a new nation (Italy, USSR, Japan, ...). `Allied` is an explicit value of kind `multinational` for combined headquarters (AFHQ, SHAEF, First Allied Airborne Army); the unit records do not say which nation staffed them, so it was not replaced.

### relationship

Meaning of the `relationship` column of `data/command_relations.csv` (and of the `relationship` key of the entries rebuilt for `build/all_claims.csv`).

| value | meaning |
|---|---|
| `organic` | A constituted component of the formation: its own regiments, battalions or battle groups, or a unit that is part of the parent's table of organisation. Do not use for a division, corps or army that is assigned to a higher headquarters (use assigned or unspecified_subordination). |
| `assigned` | The unit was assigned to this formation: the source says 'assigned', or names the unit as a standing member of the headquarters' order of battle for a period not described as temporary, with no attachment language. Includes army to army group and corps to army. |
| `attached` | The unit was attached to this formation (a temporary or task-organised subordination) on the row's date; use only where the source says attached or shows a temporary tasking. |
| `unspecified_subordination` | The source shows the unit subordinate to this formation on the date but does not distinguish assigned from attached (for example the CMH ETO-OB assignment tables' single corps column). Never convert to attached or assigned without a source. |
| `operational_control` | This formation exercised operational (tactical) control over the unit, whether or not the unit was one of its assigned or attached components. |
| `administrative_control` | This formation held administrative, supply or personnel responsibility for the unit while another formation had operational control. |
| `supporting` | The unit was in direct support of this formation without being part of it. |
| `coordinating` | This formation coordinated the unit's operations with others without commanding it (for example 21st Army Group's coordination of both army groups until 1 September 1944). |
| `reserve` | The unit was held in this formation's (or the high command's) reserve. |
| `unknown` | A formation is named by the source but how it relates to the unit is not stated (for example AFHQ's retained supply, administration and civil-affairs responsibility in the area overrun on 15 September 1944, a theater function not stated as control of the unit). |

### lineage_kind

Meaning of the kind column of data/unit_lineage.csv: how a successor unit record continues a predecessor record. Each unit record stays separate; a lineage row only links them.

| value | meaning |
|---|---|
| `redesignation` | The same formation takes a new designation; personnel and organisation continue (for example the 462nd Infantry Division becoming the 462nd Volksgrenadier Division). |
| `reconstitution_from_remnants` | The predecessor was destroyed or broken up and the successor was formed with its remnants (usually together with a new or forming formation), as the source states. |
| `absorbed_into` | The predecessor (for example a division still forming) was merged into or renamed as the successor and ceased to exist on its own. |
| `formed_from_remnants` | A different kind of formation was formed from the remnants of the predecessor (for example a panzer brigade formed from the remnants of a panzergrenadier division). |

### relationship_date_basis

Where the start and end dates of a command relation come from (`date_basis`, `stated_date_basis` and `stated_effective_to_basis` columns; `valid_from_basis` and `valid_to_basis` take these values plus `claim_date`, `inferred_from_next_claim` and `open_at_last_claim`, see the `relation_start_basis` and `relation_end_basis` vocabularies in `vocabularies.json`).

| value | meaning |
|---|---|
| `order` | A named order or message gives the date. |
| `assignment_table` | A dated assignment table such as CMH ETO-OB. The table date may differ from the day command actually passed. For a relation start it is the date of the table row in which the entry began (see "Start of a table-based interval"). |
| `narrative` | A narrative history or reference work states the date. |
| `inferred` | The date is inferred from other rows; treat as approximate. |

### relation_start_basis, relation_end_basis, relation_claim_role, relation_overlap_kind

Vocabularies of the command-relation tables (see [Command relations](#command-relations)); the meanings are in `vocabularies.json`.

| vocabulary | column | values |
|---|---|---|
| `relation_start_basis` | `command_relations.valid_from_basis` | the values of `relationship_date_basis`, plus `claim_date` (no source dates the start: `valid_from` is the first claim that lists the relation) |
| `relation_end_basis` | `command_relations.valid_to_basis` | the values of `relationship_date_basis`, plus `inferred_from_next_claim` (end = the day before the next claim that no longer lists it, `valid_to_earliest` = the last claim that does) and `open_at_last_claim` (still listed at the unit's latest claim, `valid_to` blank) |
| `relation_claim_role` | `command_relation_claims.role` | `asserts_start`, `asserts_end`, `asserts_start_and_end`, `observed_during` |
| `relation_overlap_kind` | `command_relation_overlaps.kind` | `transfer_dates_differ`, `concurrent_by_source` |

### location_basis

How the coordinate relates in time and place to the claim's date (`location_basis` column).

| value | meaning |
|---|---|
| `documented_on_date` | A source places the unit, event or headquarters at this location on the claim's date. |
| `nearest_later_command_post` | The coordinate is the nearest command post listed after the claim's date; the position on the date itself is not documented. |
| `nearest_earlier_command_post` | The coordinate is the nearest command post listed before the claim's date; the position on the date itself is not documented. |
| `representative_point` | A point chosen to stand for an area, front or named objective (not a documented position). Use it when `location_represents` is `objective` and the unit or headquarters was not at that place on the date. |
| `town_centroid` | The coordinate is the centre of a named town or commune; the source does not locate the headquarters or event more precisely. |
| `operational_area` | A point inside the area of operations (sector, landing area, bridgehead) rather than a headquarters or exact position. |
| `inferred` | Inferred from the unit's movements or other rows rather than stated. |

### claim_status

How a row relates to competing claims. Rows with a conflict_group_id must use preferred, alternate or disputed as below; rows with no conflict are always preferred.

| value | meaning |
|---|---|
| `preferred` | A non-conflicted claim, or the best-supported claim in a conflict group. |
| `alternate` | A competing claim judged less likely than the preferred one in the same conflict group. |
| `disputed` | One of several competing claims where no source is judged better; a group with no preferred row has all rows disputed. |

### echelon

Organisational level of the unit.

| value | meaning |
|---|---|
| `army_group` | Army group or equivalent theater command (for example 21st Army Group, Army Group B). |
| `army` | Army or panzer group. |
| `corps` | Corps. |
| `division` | Division. |
| `brigade` | Independent brigade. |
| `regiment/battle_group` | Regiment-sized or smaller ad hoc formation such as a Kampfgruppe or an Allied combat command. |
| `battalion` | Battalion-sized or smaller formation that is only an opponent or a component of a larger unit (for example a heavy tank battalion); rank 1. Regiments and regiment-sized battle groups keep `regiment/battle_group`. |
| `other` | Higher or special headquarters that fit no level above (for example OB West). |
| `air_force` | Reserved for later: air force, air fleet or air army headquarters (not yet used). |
| `air_formation` | Reserved for later: air corps, air division, wing, group or squadron (not yet used). |
| `fleet` | Reserved for later: naval fleet, task force or flotilla headquarters (not yet used). |
| `naval_unit` | Reserved for later: ship, squadron or other naval unit (not yet used). |

### branch

Service or arm, assigned from the unit name.

| value | meaning |
|---|---|
| `Army` | Regular army (including infantry and static divisions). |
| `Armoured` | Armoured and panzer formations. |
| `Airborne` | Allied airborne formations. |
| `Waffen-SS` | Waffen-SS formations. |
| `Luftwaffe` | Luftwaffe ground formations (for example Fallschirmjaeger and Luftwaffe field divisions); also reserved for Luftwaffe flying units. |
| `Marines` | Marine ground formations (reserved; none served on the Western Front 1944-45). |
| `Air Force` | Reserved for later: air forces (RAF, USAAF, Luftwaffe flying units). |
| `Navy` | Reserved for later: naval forces. |

### location_represents

What the latitude/longitude stands for.

| value | meaning |
|---|---|
| `headquarters` | The unit's headquarters. |
| `main_body` | Where the main body of the unit was. |
| `sector_center` | The centre of the sector or landing zone the unit held or used. |
| `front_line_point` | A representative point on the unit's front line or point of contact. |
| `objective` | The place the unit captured, attacked or defended. |
| `approach_route` | A point on the unit's march or approach route. |

### precision_km

Judgment estimate, in kilometres, of the radius within which the unit (or its main body) probably was. Not a surveyed error. Banded values.

| value | meaning |
|---|---|
| `1` | Exact named place tied to the date; division or smaller. |
| `3` | Village-scale point; manual override used once in the proof of concept (C0034). |
| `5` | Named town or village, approximate; or exact for corps and above. |
| `10` | Sector or beach centre (beaches are 8-10 km wide), or inferred for division or smaller. |
| `25` | Inferred for corps, or approximate for army and above; approach routes within one region. |
| `50` | Inferred for army and above, or long approach routes (for example a move from Brittany). |

### confidence

Numeric 0-1 score applied by rule from location quality and source families. Only these four levels are used.

| value | meaning |
|---|---|
| `0.9` | Exact location and two independent source families agree (Wikipedia, CMH/HyperWar and each other domain count as separate families; several Wikipedia pages count as one). |
| `0.7` | Exact location with one authoritative source (for example the US Army CMH); or approximate location with two source families. |
| `0.5` | Exact location with one secondary source (Wikipedia, local-history page); or approximate location with one source family. |
| `0.3` | Position inferred or a representative point (HQ not tied to the date, unverified beach, front-line representative point), or the date itself is approximate. |

- Caps for conflicts: the preferred row of a conflict group is at most 0.7; alternate and disputed rows are at most 0.5.

- A manual override is allowed when the date itself is approximate (use 0.3) and must be explained in notes.

### Operation vocabularies

`op_type`, `operation_date_basis` and `operation_relation` (the values of `op_type`, `date_basis` and `relation`) are defined in `schema/vocabularies.json` and described under "Operations" above (`scripts/operations.py` reads them from there); `nationality_scope` takes the names of `data/nationalities.csv` plus `All`. The CMH campaign streamers and the other operations are rows of `data/operations.csv`, not vocabulary values.

### event_type

One primary event per row.

| value | meaning |
|---|---|
| `landing` | Seaborne or airborne landing, including D-Day assault landings. |
| `arrival` | Reaching the front or the beachhead after the landing phase. |
| `attack` | Offensive action. |
| `defense` | Defensive action. |
| `counterattack` | Counterattack. |
| `relocation` | March or move. |
| `withdrawal` | Withdrawal or retreat. |
| `surrender` | Surrender. |
| `capture` | Taking a named place or position. |
| `destruction` | Unit destroyed. |
| `command_change` | Commander or command responsibility changes. |
| `hq_move` | Headquarters moves. |
| `hq_observation` | A source (a command-post list, situation map or report) records the headquarters at a place on the date; it does not state that the headquarters moved on that date (use `hq_move` where a dated movement source exists). |
| `regroup` | Assembly, reorganisation, relief in place. |
| `activation` | A formation becomes operational, or is activated or constituted as a headquarters or unit (for example 12th Army Group becoming operational on 1 August 1944). |
| `subordinate_assignment` | A source (a CMH assignment table or an order) lists the unit under a higher headquarters, or lists a headquarters' first subordinate unit, from this date; it says nothing about when command was first exercised or when a headquarters became operational. Use `activation` only where a source documents the operational start (taking a sector, command or mission). |
| `redesignation` | The same formation takes a new designation (identity continues; for example XVIII Corps becoming XVIII Airborne Corps). |
| `other` | Headquarters decisions, air attack on a headquarters, units at their station. |

### strength_status (derived)

Qualitative strength in `build/all_claims.csv`; derived, not stored: `destroyed` when the claim's `destroyed` flag is true, else `strength_json.status` (`full`, `reduced`, `heavily_depleted`; vocabulary `strength_json_status`), else `unknown`.

| value | meaning |
|---|---|
| `full` | A source describes the unit as at full strength. |
| `reduced` | Source states significant losses or reduced combat power. |
| `heavily_depleted` | Source states the unit was a small fraction of its strength. |
| `destroyed` | Unit destroyed or ceased to exist as a fighting formation. |
| `unknown` | No source states the strength. |

### strength_json_basis

Meaning of the basis field inside strength_json.

| value | meaning |
|---|---|
| `reported_actual` | A unit report or operational count relayed by the source (for example working-order tank returns). |
| `authorized_organization` | Establishment or table-of-organisation strength, not an actual count. |
| `estimate` | Rounded, approximate or retrospective figure, or a landing tally. |

### strength_json_vehicle_count_type

What the numbers in strength_json.vehicles mean.

| value | meaning |
|---|---|
| `operational` | Vehicles in working order. |
| `on_hand` | Vehicles on hand, working order not stated. |
| `unknown` | The source does not say what the count means (for example vehicles committed in one action). |

### strength_json_scope

What part of the unit the figures in strength_json describe. Required whenever personnel is given (the validator reports an error if it is missing).

| value | meaning |
|---|---|
| `whole_unit` | The figure covers the whole unit (division, brigade, ...) as the source states it. |
| `sub_force` | The figure covers only part of the unit: a battle group, a detachment or the force available for one task or line. |
| `sector` | The figure covers the forces in a sector or area that is not the unit's own organisation (for example the defenders of a line or beach, or all the forces landed on a beach). |

### boolean

Boolean fields (established, disestablished, destroyed) use lowercase text.

| value | meaning |
|---|---|
| `true` | True. |
| `false` | False. |

### record_status

Research state of a unit record in data/units.csv.

| value | meaning |
|---|---|
| `placeholder` | Identity only: the unit exists in the table so that other records can point to it. No claim file. Not a claim about its location. |
| `partial` | A claim file exists but coverage is known to be incomplete (for example only some operations are done). |
| `active` | A claim file exists. |

### source_token

Short tokens used in listing_source and initial_parent_source. See docs/sources.md and docs/methodology.md (Placeholder units).

| value | meaning |
|---|---|
| `LEX` | Lexikon der Wehrmacht (lexikon-wehrmacht.de), the unit's own page or its timeline tables. |
| `DEW6` | de.wikipedia 'Schematische Kriegsgliederung der Wehrmacht fuer die Operation Overlord' (German order of battle for 6 June 1944). |
| `WP12AG` | en.wikipedia 'Twelfth United States Army Group' (order of battle, 8 May 1945). |
| `WP6AG` | en.wikipedia 'Sixth United States Army Group' (order of battle, 8 May 1945). |
| `WP21AG` | en.wikipedia '21st Army Group'. |
| `WPNORM` | en.wikipedia 'List of Allied forces in the Normandy campaign'. |
| `WPMG` | en.wikipedia 'Operation Market Garden order of battle'. |
| `WPBULGE` | en.wikipedia 'Battle of the Bulge order of battle'. |
| `WPDRAGOON` | en.wikipedia 'Operation Dragoon order of battle'. |
| `WPNORDWIND` | en.wikipedia 'Operation Nordwind'. |
| `WPUNIT` | The unit's own en.wikipedia article (no Wikipedia order-of-battle page above links to it). |

### Vocabularies read by the scripts

These entries of `vocabularies.json` are not field vocabularies; they hold values that used to be copied into the scripts, and the scripts read them through `scripts/common.py`:

- `echelon_rank`: `values` maps each echelon (and the smaller levels squad, platoon, company, battalion) to a rank (higher = larger formation; `other` = 8) for the hierarchy checks of `validate.py`, `audit_temporal_relationships.py` and `who_controls.py`; `display_order` is the order of echelons in `build/coverage.csv` and `docs/coverage.md`.
- `echelon_id_letter`: the letter of each echelon that ends a `unit_id` (`values`), the echelons that never carry one (`no_letter`: `regiment/battle_group`, `battalion`) and the pattern of the combat-command exception; read by the unit check of `validate.py`.
- `relationship_groups`: `standing` (organic, assigned, unspecified_subordination, unknown) and `active` (operational_control, attached); `standing` is also what decides `end_unknown` of a command relation.
- `higher_than_organic`: for each echelon, the higher echelons whose headquarters cannot be an `organic` parent.
- `source_type`: the allowed `source_type` values of `data/references_meta.csv`.
- `alliance` and `nationality_kind`: the allowed `alliance` and `kind` values of `data/nationalities.csv`.
