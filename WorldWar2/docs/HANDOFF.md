# HANDOFF: WWII unit-locations dataset

Written 26 October 2026 for a new assistant with no memory of the earlier work. Read this file first, then follow section 8 before you touch anything. It holds no secrets and must never be given any (no tokens, passwords or keys, in this file, in commits, in logs, or in messages).

Owner and only decision-maker: **Scott Starsman** (`scott@starsman.com`; commits are authored as **Raymond Scott Starsman**, same address). You work *for* Scott. You propose; he decides; he merges.

---

## 1. Purpose, scope and current state

**Purpose.** An open, claim-based dataset of where World War II units were, when, and how sure we are. One row = one sourced claim (this unit, this place, this date, this activity, these sources). Competing claims stay as separate rows. Command relationships (who a unit was assigned, attached or under operational control of) are dated intervals in their own tables, with evidence links back to claims.

**Scope (owner-approved).** US Army ground units on the **Western Front, 6 June 1944 to 8 May 1945**, at army-group, army, corps and division level. No Marines. No air or naval units (the vocabularies reserve them; nothing uses them).

**Where the work stands (26 October 2026).**

| item | value |
|---|---|
| Claims | **712** (`C0001` to `C0712`), dated 6 June 1944 to 8 May 1945. By nation: US 573, Germany 75, UK 60, Canada 4 (on the branch `batch5-apr-may-1945`; `main` has 646, `C0001` to `C0646`, US 507) |
| Claims by month | Jun 212, Jul 58, Aug 140, Sep 109, Oct 8, Nov 15, Dec 32, Jan 1945 22, Feb 15, Mar 35, Apr 1945 48, May 18 |
| Units in `data/units.csv` | **356**: 141 active (US 84, Germany 34, UK 21, Canada 2), **215 placeholders** (identity only, no claims; none is a US unit) |
| Command relations | 557 (`CR0001` to `CR0558`; `CR0037` was removed), 1,468 evidence links, 24 documented overlaps |
| Places / references / operations | 503 / 575 (ids to `R581`; `R548`, `R550` and `R554` unused and not to be reused) / 45 |
| Conflict groups | 14 (30 claims in groups; 626 preferred, 10 alternate, 10 disputed overall; `G017` is the newest, the 89th Division's Moselle date) |
| Retired claim ids | 0. Next free claim id: **C0713** (next relation `CR0559`, next place `PL0510`, next reference `R582`, next conflict group `G018`) |
| Done | June 1944 proof of concept (US, UK, Canadian and German units); US Army Batches 1 to 3 (1 July to 31 December 1944) |
| Done on the branch `batch4-jan-mar-1945` (merged into `main`, 26 October 2026) | **Batch 4 (1 January to 31 March 1945)**, 68 claims; see `docs/roadmap.md`, "Batch 4" and the `docs/changelog.md` entries |
| Done on the branch `corps-xxii-xxiii` (merged into `main`, 26 October 2026) | **XXII and XXIII Corps** activated: 5 claims (`C0642` to `C0646`), 7 command relations (`CR0472` to `CR0478`), 1 existing relation closed (`CR0097`); see `docs/roadmap.md`, "XXII and XXIII Corps" and the `docs/changelog.md` entry |
| Done on the branch `corps-followups` (merged into `main` with PR #17, 26 October 2026) | **Follow-ups to the corps task:** `formed_date` of XXII and XXIII Corps set to 1944-01-15 (activation); `CR0447` (95th Division to XIX Corps) closed on 1945-03-30 (table-based end); no claim added (646). See the `docs/changelog.md` entries and `docs/roadmap.md`, open points 1, 2 and 6 |
| Done on the branch `batch5-apr-may-1945` (**pushed, not merged**; awaiting the spot check, Scott's review and merge) | **Batch 5 (1 April to 8 May 1945)**, 66 claims (`C0647` to `C0712`), 6 placeholders activated (13th, 16th and 20th Armored; 71st, 86th and 97th Infantry), 80 relations (`CR0479` to `CR0558`), 41 earlier relations closed, 3 operations, 16 references, country codes `AT` and `CZ`; see `docs/roadmap.md`, "Batch 5" (including what it does not cover) and the `docs/changelog.md` entries |
| **Not started** | A commanders table, `event_support` and `position` columns, F-004 and F-005, XXII and XXIII Corps rows for April and May, and the gaps listed under "What Batch 5 does NOT cover" in the roadmap |

**What is and is not covered.**
- **US Army, 1 July to 31 December 1944:** army groups, armies, corps and *selected division milestones*. Rows are event-based (a row on days when something substantial happened). A position between two rows is unknown, not unchanged.
- **German, British, Canadian units:** only the **June 1944** proof of concept (German 75 claims in 34 active units, all June 1944; UK and Canadian 64 claims, all June 1944). They appear after June only as higher headquarters in relations, never as claim subjects. German coverage is partial: only units that were in the June 1944 pass, with 52 command relations (mostly the June parent changes of the panzer units). 177 German units are placeholders.
- **French:** 13 placeholder units, no claims. Polish, Belgian, Czechoslovak, Dutch: placeholders only.
- **Not covered in Batch 3** (full list in `docs/roadmap.md`, section "Batch 3"): Hurtgen Forest detail, Metz and Strasbourg falls, Colmar beyond XXI Corps, French First Army relations, the 7th, 3rd and 9th Armored in the Bulge, and more.
- Licence terms in the repo (CC BY-SA 4.0 data, MIT code) are *recommendations*; Scott has not confirmed them, and the copyright holder is still to be filled in `LICENSE-CODE` and `CITATION.cff`.

---

## 2. Where everything lives

**Principle:** the box is **one persistent Linux machine shared by all of Scott's agents.** Files you create stay; other agents' files are also there. Everything outside the paths below belongs to other projects: do not touch it.

| what | where |
|---|---|
| **GitHub repo** | `scottstarsman/UnitLocationData` (**private**). The dataset sits under `WorldWar2/`; the repo root has the publish README, `LICENSE`, and `.github/workflows/validate.yml` (CI runs inside `WorldWar2/`). Default branch `main`. |
| **Working copy (where you edit)** | `/workspace/ww2-unit-locations` (git repo, **no remote**; it is the source that is synced to Drive and replayed to the prep clone). Tree has no `WorldWar2/` prefix. |
| **Prep clone (publishing)** | `/workspace/UnitLocationData-prep` (clone of the GitHub repo; this is the only place that pushes). Commits replayed here have **different hashes** from the working copy's. |
| **Tools (not in the repo)** | `/workspace/UnitLocationData-tools`: `sync_to_github_prep.py` (replays working-copy commits into the prep clone; never pushes), `publish_transforms.py` (licences, citation, root README, workflow), `run_checks.sh` (whole verification set), `wc_grid.py` and `cmp_grid.py` (who_controls grid comparison). Its `README.md` lists them. |
| **Review notes outside the repo** | `/workspace/ww2-locations` (`NOTES_DIR` of the sync tool): `review_changes.md`, `spot_check_batch1/2/3.md`, `temporal_audit.md`, `operations_backfill.md` and the older build scripts. Copied into the publish clone on each replay. |
| **Drive, primary copy** | Folder **`WWII Unit Locations`** (`1GYCx0u3PEUgl4GACgMZioTFBdpVedjyg`). Inside: **`repo`** (`1e9_bE40eqOgX9477sz4FC_tcFdwDG2Bi`, a file-by-file mirror of the working-copy tree; `docs` is `1SUf51I8OLpdBCtqQuyd7sZdKoHXlJ_t9`, `docs/review` is `1sZj5aIr03qF-EOy9-NHGZCYNM7w2yWp2`), **`review samples`** (`1ZN4bARpJtWvpOcxkjJMsNDB67txqpmzp`: the notes from `/workspace/ww2-locations`), `earlier versions`, and an old `ww2-unit-locations.zip` (**do not rebuild or replace it**). This file is at `repo/docs/HANDOFF.md`. |
| **Copy of this file** | `/workspace/export/HANDOFF.md` |
| Scratch from past verification rounds | `/workspace/verify/` (not needed; may be deleted by Scott) |

**Git identity for every commit:** `Raymond Scott Starsman <scott@starsman.com>` (set `GIT_AUTHOR_*` and `GIT_COMMITTER_*`; the sync script already does this).
**GitHub access:** the box's `gh` CLI is logged in as `scottstarsman` with HTTPS git. Never print or store the token.

**State of branches at handoff.**
- GitHub `main` = merge commit `965acfd` (PR #13, Scott merged `open-items-oct26`). Main holds everything described here.
- `open-items-oct26` is **merged but still exists** locally in both clones and on GitHub. Standing rule: delete the task branch (remote and local) after the merge and tell Scott. Not yet done at handoff; do it only after Scott confirms (it is his branch, and deleting a remote branch is not undoable by you).
- `handoff-doc` is the branch that added this file (Scott merges it).
- Older local branches `command-relations-table` and `unit-ids-in-text-columns` exist in the working copy (history only).

---

## 3. STANDING RULES from Scott (follow exactly)

1. **One branch per task.** Create it from current `main`. First make sure the working copy and the prep clone are both on up-to-date `main` (fast-forward only; if the previous task's branch is not merged yet, base on that branch, because `sync.lastsrc` is one marker for the whole prep clone).
2. **Push the branch only.** Never push to or merge `main` without Scott's explicit go-ahead. **Scott merges.** No PR, no zip, unless he asks. The sync tool refuses to commit on `main` without `--allow-main`; never use that flag without his approval.
3. **After he merges:** fast-forward both clones' `main`, delete the task branch remote and local, and **tell him**.
4. **Author identity** on every commit: Raymond Scott Starsman <scott@starsman.com>.
5. **Each logical item in its own commit** when he asks for it ("in their own commit"). A commit carrying data also carries the regenerated `build/` files and its changelog entry.
6. **Annotate every extrapolated, inferred or changed value:** old value, new value, reason, in the record's `notes`/`note` **and** in `docs/changelog.md`. Delete nothing from `data/` without noting it (a removed relation keeps its old row in the changelog; a removed claim goes into `data/retired_claims.csv`).
7. **Never rebuild or upload a zip** unless Scott asks.
8. **Sync Drive in place at the end of every task**, no duplicates: list the folder first; update an existing file with `update_file_content` (same file id); create a new file only if none exists; never create a second `WWII Unit Locations` folder. Keep the working copy, the prep clone and Drive consistent.
9. **Pasted reviews are unverified.** When Scott pastes an outside review or someone else's claims, check each point against the sources (and the data) first; record what you confirmed, declined and why. Correct overclaims in your own commits (amend before pushing, or add a correcting commit).
10. **Run the full verification set (section 5) before you report.** Report results, not hopes.
11. **Keep replies short and warm.** Plain language, no walls of tables in chat; put detail in files and link them.
12. **Email only Scott** (`scott@starsman.com`). Do not contact outside parties (reviewers, archives, contributors) without his explicit go-ahead naming who and what. **Never expose secrets.**
13. **Do not start unapproved work.** At handoff, Scott had *not* approved: Batch 4 or 5, a commanders table, `event_support` or `position` columns, F-004 or F-005 work, or sending the outside-review questions.
14. **Anything external and irreversible** (sending, posting, deleting outside the box, merging, pushing main) needs his explicit approval for that specific action.
15. **The dataset's own rules** (`CONTRIBUTING.md`): every row needs a source; conflicting claims become separate rows; never invent (`unknown` or blank); ids are never reused; vocabularies are closed; edit `data/` only, never hand-edit `build/`.

---

## 4. Architecture, data model and conventions

Read `README.md` (layout, data model, how to interpret the data), `CONTRIBUTING.md`, `docs/methodology.md` and `schema/README.md` for detail. The essentials:

**Tables (all under `data/`).**
- `claims/<nation>/<UNIT_ID>.csv`: master claim files, one per unit, sorted by `date` then `claim_id`.
- `units.csv` (one row per unit; `record_status` placeholder/partial/active), `nationalities.csv`, `operations.csv` (+ `operation_relations.csv`, `operation_exceptions.csv`), `places.csv` (+ `place_merges.csv`, `coordinate_exceptions.csv`).
- `command_relations.csv` (one dated interval per subject, higher unit and relationship), `command_relation_claims.csv` (evidence links with what each claim stated), `command_relation_overlaps.csv` (documented contradictory overlaps).
- `references.csv` (**generated**; curated metadata in `references_meta.csv`), `claim_reference_roles.csv`, `retired_claims.csv`, `claim_key_exceptions.csv`.
- `build/` and `docs/coverage.md` are **generated** by `scripts/build.py`. Commit them with the data.

**Ids (never reused, never renumbered once on `main`).**
- Claims `C0001...` (next = highest of claims and retired + 1; `check_claim_ids.py` prints it). Relations `CR####`. Places `PL####`. References `R###`. Conflict groups `G###`. Gaps are allowed. A claim that must leave is retired in `data/retired_claims.csv` (`claim_id,replaced_by_claim_id,reason`). There is **no retired-relation mechanism**: a removed relation (e.g. `CR0037`) is recorded with its full old row in `docs/changelog.md`.
- Unit ids: `NATION-TYPE-NUMBER` plus an echelon letter (`US-INF-004D` = 4th Infantry Division; `A` army, `C` corps, `D` division). The id is an opaque stable key: it is never renamed when the unit is redesignated (XVIII Corps becoming XVIII Airborne Corps stays `US-ABN-018C`).
- **Claim identity is `claim_id` only.** `(unit_id, date, event_type)` is a duplicate guard (validator error); legitimate repeats go in a conflict group or in `claim_key_exceptions.csv` (0 rows today).

**Notes labels (closed set of 19).** A `notes` sentence of the form `Label: text` must use one of: Event date, Event definition, Event support, Location, Location support, Location support fallback, Location caveat, Location approximate, Coordinates, Coordinate check, Relationship, Command support, Opponents, Objective check, Commander, Context, Later, Search, Review. The validator rejects any other `Word: ` lead. Lead-ins that name a source, batch or id (`Breakout-28 p577:`, `Wikipedia:`) are prose. **Do not write `Old:`, `New:`, `Reason:` at the start of a claim note**; put an annotation inside a `Review` sentence, e.g. `Review (open item 7, 26 October 2026, decided by Scott; inferred value): ...`. Adding a label means changing `schema/vocabularies.json`, `schema/README.md` and the changelog in one commit.

**Confidence rubric** (date and place only, not event likelihood): 0.9 exact place and two independent source families; 0.7 exact place and one authoritative source (CMH), or approximate place and two families; 0.5 exact place with one secondary source, or approximate place and one family; 0.3 inferred position, representative point, or approximate date. Only these four values. Caps: preferred claim in a conflict group at most 0.7; alternate and disputed at most 0.5. Wikipedia pages count as one family; everything republished from CMH counts as one. Representative points for headquarters use precision 50 km and confidence 0.3.

**Conflict groups.** Same unit, same event, disagreeing sources: one `preferred`, others `alternate`, or all `disputed`; each row explains the disagreement. Rows that are really *different events* (a landing and an arrival; a table observation and an order) are **not** a conflict: dissolve the group, give each row an `Event definition:` sentence (G016, 101st Airborne; G012, 4th Armored).

**Command relations (`data/command_relations.csv`).**
- Relationship values: organic, assigned, attached, unspecified_subordination (used when a CMH table combines assigned and attached; never turn it into `attached` without a source), operational_control, administrative_control, supporting, coordinating, reserve, unknown.
- Interval: `valid_from`, `valid_to`, each with a basis (start: order, assignment_table, narrative, inferred, claim_date; end: order, assignment_table, narrative, inferred, inferred_from_next_claim, open_at_last_claim), plus `valid_to_earliest`, `valid_from_latest`, `last_listed_date`, `change_undated`, `end_unknown`. A relationship is evidenced only up to the last claim that lists it. A standing relationship (assigned, unspecified_subordination, unknown, organic) has no expected end; a temporary one (attached, operational/administrative control) does.
- Evidence links (`command_relation_claims.csv`) have a role: asserts_start, asserts_end, asserts_start_and_end, observed_during, listed_by_higher_unit, and `stated_*` fields recording what that claim itself said. The role must agree with the stated dates (the validator checks it).
- **Standard table-end rule:** the end is the day before the first CMH table row that no longer lists the unit.
- **Option C (start-date convention, decided by Scott 26 October 2026, finding V-013):** for `assignment_table` relations, `valid_from` is **the date of the CMH table row in which the entry began**, not the table row in force at the unit's first claim. Basis stays `assignment_table`; the evidence link's `stated_effective_from` follows; the claim keeps its own date. Applied to all 157 comparable relations and 53 of the 54 others that could be read; each note records old start, new start, table row, page. Use it for every new table-based relation. If a start rests on a plan or narrative, use basis `narrative`; if it is a guess, `inferred`, annotated.
- **Same-unit splits (V-014, documented, nothing merged):** a subject can have two relations to the same higher unit that touch in time because the source wording changed (assigned vs unspecified_subordination). The corps did not change. Each of the 16 relations names its partner in its `note`; read the pair as one continuous interval. Do not merge them; do not treat them as a parent change.
- **`transfer_dates_differ` overlaps:** two consecutive relations of the same class whose intervals overlap on some days (sources date the change differently, or one end is only inferred) must be listed in `command_relation_overlaps.csv` with an *accurate* explanation (the validator rejects an unlisted or stale overlap). In the item 8 review 19 of 24 generic "sources do not agree" explanations were wrong: usually the table dates the change and only the earlier end was inferred. Say which it is. `concurrent_by_source` is for a source that states both at once.
- **Staleness rule (`scripts/who_controls.py`):** a relationship is `certain` only up to its `last_listed_date`; after that, if its end is `open_at_last_claim`, the answer is `possible` (carried forward, with how many days since last listed); an inferred end after `valid_to_earliest` is `possible`; a documented overlap of two transfer dates is `possible`; an hour of change with no record is `UNKNOWN`. No day threshold, because any threshold would invent a fact.

**Other conventions to remember.**
- Inferred or extrapolated values are labelled with the `inferred` basis (or `claim_date`, `inferred_from_next_claim`, `open_at_last_claim`) and annotated; never leave a guess looking like a source.
- Places: claims point at `place_id`; coordinates come from the place (Wikipedia coordinates first, Nominatim second; a hand-worked point has a blank `coord_reference_id` and says how). A claim point that differs needs `coord_override` and must be within 5 km of the place.
- Sources: every `source` URL needs a `references_meta.csv` row (`python scripts/build_references.py --add URL`), listed in `reference_ids`, with `source_locator` when a page is known. A 0.9 claim needs two source families. CMH is public domain; Wikipedia is CC BY-SA.
- `parent_unit_id` is the operational parent on the row's date; the standing parent goes in the relations table. The word "attached" is rejected in `composing_text` and `engaged_note`.
- Rows sorted; files named by `unit_id`; the unit's identity columns in every claim row must equal `units.csv`.

---

## 5. Tooling: how to run each check and what "good" looks like

Run from `/workspace/ww2-unit-locations` (standard-library Python 3 only). One command runs all except the id and grid checks: `/workspace/UnitLocationData-tools/run_checks.sh`.

| check | command | good baseline on 26 October 2026 |
|---|---|---|
| Validator | `python3 scripts/validate.py` | `OK: 141 claim files, 712 claims, 356 units, 14 conflict groups` (Batch 5; `main` before it: 135 claim files, 646 claims); exit 0; **3 known WARNINGs** (GER-COR-084C line 2: more than three opponents; US-ABN-082D line 9: US-COR-008C ended 12 July before the 13 July row; US-ABN-101D line 7: attached entry without a standing parent). Any new ERROR or a new WARNING must be fixed or explained in the row's `notes`. |
| Semantic tests | `python3 scripts/semantic_tests.py` | `OK: 68 expectations hold`. If you change data on purpose, change the expectation in the same commit and say why. |
| Build check | `python3 scripts/build.py --check` (after `build.py`) | `build/ and docs/coverage.md are up to date (12 files)` |
| References | `python3 scripts/build_references.py --check` | `references are up to date (4 files)` |
| Review sample | `python3 scripts/review_sample.py --check` | `OK: docs/review sample and counts are up to date`. If it fails after a data change, run `review_sample.py` to regenerate; verdicts are carried over **by relation id**, so a removed or new relation needs a re-read of its sample row. `docs/review/README.md` counts are generated. |
| Coordinates | `python3 scripts/check_coordinates.py` | exit 0; **3 known warnings** (speed C0253, C0419, C0480); 6 explained exceptions. Offline only; `--geocode` needs network. |
| Audits | `python3 scripts/audit_command_location.py` and `python3 scripts/audit_temporal_relationships.py` | exit 0; findings are prompts, not errors. Check every finding that involves a row you touched; the temporal audit lists 3 `change_flagged` (CR0053/54, CR0040/41, CR0049/50) as expected. |
| Claim ids | `cd /workspace/UnitLocationData-prep/WorldWar2 && python3 scripts/check_claim_ids.py` (compares with `origin/main`; in the working copy use `--base <rev>`) | `OK: no id was reused or dropped since origin/main`; prints `next free id: C0574` until new claims land. |
| **who_controls grid** | see below | 5,020 answers; every change must be explained |
| GitHub Actions | `gh run list --repo scottstarsman/UnitLocationData --branch <branch>` after pushing | `validate` completes with success. CI runs validate, coordinates (non-failing), temporal audit (non-failing), build, build `--check` and a clean `git status` of generated files, semantic tests. |

**who_controls grid, before/after method** (proves a data change moved only the answers you intended):
1. On the task branch **before** your first edit: `cd /workspace/ww2-unit-locations && python3 /workspace/UnitLocationData-tools/wc_grid.py /tmp/before.json` (needs current `build/`; ~10 s; 5,020 answers = every subject unit in `build/command_relations.csv` on 40 weekly dates from 5 June 1944, plus daily answers 5 June to 31 December for US-ABN-082D, GER-PZ-LEHRD, US-ARM-002D).
2. After the final edit and `python3 scripts/build.py`: same command to `/tmp/after.json`.
3. `python3 /workspace/UnitLocationData-tools/cmp_grid.py /tmp/before.json /tmp/after.json 20` prints totals changed, new keys and diffs of the first 20 changed answers.
4. Report the count and the **reason for every kind of change** (a relation, or its `certain` status, appears earlier; a chain gains a line; etc.). A change you cannot explain means a defect. Zero changes is the right answer for notes-only commits. If the set of subject units grows, new keys are expected; say so.

**Publishing sequence** (replay the working-copy commits into the prep clone, run the checks there, push the branch):
```
cd /workspace/ww2-unit-locations && git status          # clean, all work committed
python3 /workspace/UnitLocationData-tools/sync_to_github_prep.py --branch TASK --base main --dry-run
python3 /workspace/UnitLocationData-tools/sync_to_github_prep.py --branch TASK --base main
cd /workspace/UnitLocationData-prep/WorldWar2 && python3 scripts/validate.py && python3 scripts/build.py --check && python3 scripts/check_claim_ids.py
git -C /workspace/UnitLocationData-prep push -u origin TASK     # branch only
gh run list --repo scottstarsman/UnitLocationData --branch TASK # wait for green
```
Compare link for the report: `https://github.com/scottstarsman/UnitLocationData/compare/main...TASK`.
Working copy and prep clone must carry the same content (the sync tool replays; the publish clone adds only the licence, citation, root README and workflow). Never edit the prep clone by hand.

---

## 6. Decision log (what was decided, and why)

All dates 2026. "Scott decided" = approved by him in chat.

**Design findings from the outside reviews (`docs/review/responses.md`, `docs/review/verification_results.md`)**
- **R1-F-004 (claim key `(unit_id, date, event_type)`): deferred, error kept.** `claim_id` is the identity; the key only catches double entry. `CONTRIBUTING.md` heading changed to "The duplicate guard". Reason: no case needs an exception yet (0 exceptions), and the guard is most valuable during the 1945 batches when hundreds of rows are added. Revisit only at a real need (many same-day, same-type events, or air and naval work).
- **R1-F-005 (field-level conflicting assertions / `claim_evidence` table): deferred.** Disagreement is handled by splitting rows (conflict groups, sequences, `stated_*` on relation links, overlaps). Trigger to build the table: a real claim whose sources disagree on one field and cannot be split without a false row.
- **R1-Q5 (ids, branch and echelon):** already the policy: ids are opaque and stable; a redesignation keeps the id.
- **Commanders table, `event_support` and position columns: deferred, and not approved to start.** `commander` stays free text; `Event support:` stays a notes sentence (R1-Q6, R1-F-006). A position query (five statuses: observed, carried forward, interpolated, conflicted, unknown) does not exist and is deferred until Scott wants one.
- **V-013 option C (start of table-based intervals)**: decided and applied: all 157 of the 157 comparable table-based relations, and 53 of the other 54 that could be read, now start on their table row (CR0366 was already on its date; see section 4).
- **V-014 same-unit splits: document only**, nothing merged; **V-009 CR0041** (Panzer Lehr to I SS Panzer Corps, placeholder end 12 June, the day before claim C0092): documented in its note (it is one of 22 placeholders and the only one with the same higher unit on both sides); no data change.

**Source conflicts kept and flagged (no data change)**
- **C0181 (First US Army, 27 June, 21st Army Group control):** `CR0166` ends operational control on 31 July (12th Army Group operational 1 August, Breakout and Pursuit ch. 18); R445 says 21st Army Group kept over-all control until 1 September, and `CR0116` records the August coordination. Scott decided: keep the data and the flagged note.
- **C0505 (XII Corps, 7 August):** claim names Major General Gilbert Cook; R475 gives Eddy from 1 August; R155 (Wikipedia) and the C0320/C0321 sequence give Cook until 18 August. Scott decided: keep Cook and the flagged note.

**Placeholders and places**
- **PL0195 (Logis de la Bocage, 1st Division, August 1944):** searched again on 26 October (IGN, Nominatim, CMH, 90th Division report, Breakout and Pursuit ch. 23): not found. Stand-in kept (Juvigny-le-Tertre, 25 km, confidence 0.3). Alternative (Mortain-Bocage) rejected as a guess. Wait for the 1st Division's G-3 journal (Eisenhower Library, accession 64-3, not online).
- **LXXXIV Corps, 14 to 17 June (C0106, C0116, C0123, C0128):** the Cotentin placeholder PL0102 was replaced by Saint-Lô (PL0333, 10 km, `nearest_earlier_command_post`, 0.3); PL0102 removed and recorded in the changelog. Where the HQ really was after 12 June is unresolved.

**Relation labels (26 October)**
- **CR0105** (101st Airborne to I Airborne Corps, 17 to 19 September): basis `assignment_table` to `narrative` (it rests on the Market Garden plan); dates kept.
- **CR0200 and CR0201** (36th Division to a corps, 27 December): basis `assignment_table` to `inferred`; dates kept (the table does not establish the corps assignment; no corps-level source dates it).
- **CR0156:** note only (the 5 Aug table row is printed after "11 Aug 44", probably a misprint); start unchanged.
- **101st Airborne, September to December:** ends of `CR0106` (8 November) and `CR0107` (20 September) moved from inferred to the table's dates; new relations `CR0376` to `CR0380`; claims C0567 to C0573 (command-post rows and table observations); places PL0384, PL0385. Open: the table keeps the Canadian corps and army to 16 December although the CMH command-post list has the division at Mourmelon from 1 December.

**The three decisions of 26 October (applied on `open-items-oct26`, merged)**
- **21st Panzer Division:** it was under I SS Panzer Corps from 7 or 8 June (Cross-Channel Attack ch. 8 p. 333, ch. 9 p. 347 and 372), not from 28 June. `CR0038` now starts 8 June (basis `inferred`), `CR0036` (Seventh Army) ends 7 June (`inferred`), `change_undated` false for both, placeholder `CR0037` (13 to 27 June) removed (old row in the changelog), `C0090` gets parent `GER-SSPZ-001C`. The date is an inference (the change may have come on 7 June).
- **G012 dissolved:** C0243 (4th Armored landing, Utah Beach, 11 July) and C0244 (arrival, 13 July) are two events, both `preferred`, no group; conflict groups 14 to 13. PL0222 (Mesnil-St-Martin) could not be identified in the IGN gazetteer.
- **30th Infantry Division one-day V Corps row (4 August):** left unchanged; no relation. The overlap of `CR0266` and `CR0267` on 5 August is documented with the table's dates.
- **Still open from the review:** event type `attack` of C0048 (part of the claim key). The commander and handover dates of conflict group G003 (LXXXIV Corps) were not touched.
- **Item 8:** 19 of the 24 overlap explanations were rewritten after reading the tables (see section 4).

**Process decisions**
- **Quarterly batch split (Batch 4 January to March, Batch 5 April to 8 May 1945):** the roadmap states no reason. The reasoning I give: one batch per quarter keeps the spot-check gate and review round at Batch 3's size (51 claims for October to December), and January to May as one batch would be roughly 110 to 170 claims (my estimate from Batch 3's pace) with 20 or more newly active units. The earlier phrase "US January to May 1945" in `docs/review/questions.md` (question 8) is the whole remainder, not a batch. **Scott has not confirmed the split.** Ask him.
- **Event-based rows, milestone passes:** a batch is a milestone pass, not a daily record. Batch 3 listed what it did *not* cover; do the same.

---

## 7. Open items and next steps (my recommendations)

**First, small housekeeping (ask Scott):**
1. Merge `handoff-doc`; then delete it and `open-items-oct26` (remote and local) and tell him.
2. Fix leftover stale counts when a branch next touches those files: `docs/roadmap.md` header was fixed by `handoff-doc`; the snapshot documents `normalization_review.md`, `places_review.md`, `unit_references_review.md` and "41 of 566" in `docs/methodology.md` deliberately keep the old numbers.
3. Licence choice (CC BY-SA 4.0 and MIT) and the copyright holder are unconfirmed.

**Batch 4 (1 January to 31 March 1945) and Batch 5 (1 April to 8 May 1945).** Scope: US Army ground units, army group to division. **Batch 4 was done on 26 October 2026 on the branch `batch4-jan-mar-1945` (awaiting the spot check, Scott's review and merge); the text of this section below describes it as planned.** Batch 5 was approved by Scott on 26 October 2026 and done on 27 October 2026 on the branch `batch5-apr-may-1945` (see the table above and `docs/roadmap.md`, "Batch 5"); all six US placeholders are now active.

*Expected content.* Batch 4: end of the Bulge (January), Colmar pocket, Roer and Rur crossings, Operation Grenade (Ninth Army), Remagen (7 March) and the Rhine crossings, Saar and Palatinate, and the corps and divisions arriving. Batch 5: Ruhr pocket, advance to the Elbe, Bavaria, Austria and Czechoslovakia, the surrenders (7 and 8 May). Claim types: position and event rows (attack, capture, arrival, relocation, hq_move), command relations from the CMH tables, and activations of the new corps and divisions.

*The 27 US placeholders still unfilled (proposed batch from general knowledge of first combat; **confirm each against its CMH ETO-OB table before relying on it**).*
- **Army and corps (4):** Fifteenth Army (activated January 1945; Batch 4 or 5), XVI Corps (Ninth Army from December; Batch 4), XXII and XXIII Corps (arrive early 1945; Batch 4 or 5, no source read yet).
- **Armored (8):** 8th, 9th, 11th, 12th, 13th and 14th Armored (Batch 4; the 13th also fights in Batch 5); **16th and 20th Armored (mostly Batch 5)**.
- **Airborne (1):** 17th Airborne (Bulge to Rhine, Batch 4). The 13th Airborne is **not in the unit table** (it never entered combat); add it only if a source needs it.
- **Infantry (14):** 42nd, 63rd, 66th, 69th, 70th, 76th, 78th, 89th, 95th, 97th, 99th (Batch 4); **65th, 71st, 86th (mostly Batch 5)**. Several of these (95th, 99th, 78th, 42nd, 70th) fought in late 1944 and Batch 3 left them out.

*Other nations.* Not in scope as subjects today. They appear as higher headquarters (21st Army Group, British Second Army, Canadian First Army, French First Army, 6th Army Group relations). Scott must decide whether to give them rows (below).

*Pace and effort (estimates, not commitments).* Batch 3 produced 51 claims for a quarter (including 3 added by its review). Expect about 60 to 90 for Batch 4 and 50 to 80 for Batch 5 (my estimate), with roughly 10 to 15 units becoming active in each. Each batch is a long working session or two, plus the review round and the spot-check gate.

*Key sources.* CMH ETO-OB assignment tables (archived `history.army.mil` pages through the Wayback Machine) and CP lists; the CMH Green Books already used (*The Siegfried Line Campaign*, *The Ardennes*, *The Lorraine Campaign*, *The Riviera to the Rhine*) and *The Last Offensive* (not yet in `docs/sources.md`; add it with `build_references.py --add`); `ww2byday.com` command-post lists (secondary, one compilation); Wikipedia operation and unit pages (CC BY-SA); the Army after-action material where available online.

*Process.* New branch from `main` (`batch4-jan-mar-1945` or similar); milestone pass; per-row checklist from `CONTRIBUTING.md`; the claim-id and checks above; the spot-check gate: draw a sample (`review_sample.py` and a `spot_check_batchN.md` kept in `/workspace/ww2-locations` and Drive `review samples`), verify against sources the author did not use, record corrections; then a review round with Scott. Do not start Batch 5 before Scott accepts Batch 4.

*Known risks.* (a) the table-start convention: use option C from the start and annotate every other start; (b) same-unit splits when a source changes wording; (c) transfers whose hour is undocumented (use overlaps, do not invent the hour); (d) the new corps and divisions have claims dated *after* their first listing in the tables; (e) units entering mid-March with only one table row; (f) French First Army and British/Canadian higher units that are placeholders; (g) fast-moving April: many one-day rows, keep to milestones; (h) fetch limits: `history.army.mil` blocks automated fetches, use the Wayback snapshots as before; (i) ids and the duplicate guard get their stress test here.

**Decisions Scott still has to make before or during Batch 4:**
1. Confirm the quarterly split (Batch 4 January to March, Batch 5 April to 8 May).
2. **Division level only, or add combat commands** (for example CCB of the 9th Armored at Remagen). Today only two combat commands exist (`US-CCA-002D`, `US-CCR-004D`).
3. **Whether French, German and British/Canadian units get rows** in 1945. **My advice: finish the US first (Batches 4 and 5), then do the German coverage of June to December 1944**, so the opponents of the US rows have history. German-first is the alternative.
4. Whether to start the **commanders table** (R1-Q6) and the `event_support`/position columns now or after the US work: my advice is after the US work.
5. Whether and when to send the **outside-review questions** (`docs/review/questions.md`, ten questions; question 8 is the scaling to 1945). **Not yet sent.** Sending is Scott's call; draft the cover note for him, do not send.
6. Licence choice and copyright holder.

**Open data points (no decision needed unless Scott asks):** LXXXIV Corps HQ after 12 June; 101st Canadian entries to 16 December versus Mourmelon on 1 December; C0048 `attack` event type; PL0195 and PL0222 sites; six relations still `change_undated` true (the three German pairs CR0040/41 Panzer Lehr, CR0049/50 II SS Panzer Corps, CR0053/54 12th SS); the 3 validator and 3 coordinate warnings above.

---

## 8. Startup checklist for the new assistant

Do these in order. Do not change any file, branch or Drive item until step 5 is done.

1. **Read, in this order:** this file; `README.md`; `docs/roadmap.md` (status, batch table, "Batch 3" and "Batch 3 review" sections); `CONTRIBUTING.md`; `docs/methodology.md`; `schema/README.md` (sections "Reading a command interval", "What confidence means", "Same-unit splits", "Note labels"); `docs/review/verification_results.md` (sections 4 and 5, "Decisions pending"); `docs/review/responses.md` (index table); the top three entries of `docs/changelog.md`; `/workspace/UnitLocationData-tools/README.md`.
2. **Check state:** `git -C /workspace/ww2-unit-locations status -sb` and `git -C /workspace/UnitLocationData-prep status -sb`; `git -C /workspace/UnitLocationData-prep fetch origin` and compare `origin/main` with the local `main`; ask whether `handoff-doc` and `open-items-oct26` are merged.
3. **Run the verification baseline** (`run_checks.sh`, then `check_claim_ids.py` in the prep clone and the grid baseline) and compare each result with the "good baseline" column in section 5. Anything different from the baseline is a finding to report, not a thing to fix silently.
4. **Check Drive:** list the `WWII Unit Locations` folder and `repo/docs`; confirm `HANDOFF.md` is present once and that no duplicate files exist.
5. **Confirm understanding back to Scott** in a short, warm message: the scope and state in two lines; the standing rules in section 3 (branch only, he merges, author identity, annotate inferred values, no zip, Drive in place, verification before reporting, email only him); the open decisions in section 7; and ask what he wants first. Wait for his answer.
6. When he approves a task: new branch from `main`, grid baseline first, work in separate commits, changelog entries, full checks, sync and push the branch, wait for Actions, sync Drive, then report (branch, head, compare link, per-item outcome, grid changes, checks, Drive sync).

---

## 9. Working style

- **Delegate big work to background workers** (long source-reading, table parsing, big edits, verification runs). Give each worker the rules of section 3 and a precise brief; **verify its output yourself** before you commit (read the diffs, run the checks). A worker's summary is not evidence.
- **Keep Scott informed with short updates:** what you are doing, what you found, what you need from him. One question at a time, with a recommendation. Plain language; no jargon; no tables in chat unless asked.
- **Be honest about limits:** say "no source read places this" instead of guessing; say what you did not check. Prefer a note over a new value; prefer an inferred basis with an annotation over an unmarked estimate.
- **Verify before you assert:** open the source page (or the archived CMH table) and read the row yourself; cite page and chapter; do not trust a pasted review or a summary, including this handoff, where it conflicts with the data (the data and `CONTRIBUTING.md` win).
- **Never** include secrets, tokens or private keys anywhere; never email anyone but Scott; never act outside the approved task.

*End of handoff.*
