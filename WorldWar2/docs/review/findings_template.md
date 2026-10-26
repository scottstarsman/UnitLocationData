# Findings template and response protocol

## For the reviewer: how to write a finding

One finding per row. Copy the table below, or use the CSV header at the end. Please keep each finding about one issue, with the row id and the evidence, so that it can be checked on its own. Findings from a reviewer are treated as unverified feedback: we check each one against the sources before anything changes, so say how you know.

| field | what to put |
|---|---|
| **id** | `F-001`, `F-002`, ... (your numbering) |
| **area** | the checklist item, for example `C1`, `E4`, or `Q3` for a question, or `general` |
| **table** | `claims`, `units`, `places`, `command_relations`, `command_relation_claims`, `command_relation_overlaps`, `references`, `claim_reference_roles`, `nationalities`, `operations`, `place_merges`, `retired_claims`, `claim_key_exceptions`, `schema`, `vocabularies`, `docs`, `scripts` or `design` |
| **row id** | `claim_id`, `relation_id`, `place_id`, `unit_id`, `reference_id`, or file and section for a document; a sample id (S07, R03) is welcome as well. Several ids: separate with a space |
| **severity** | `1 error`: a row says something a source contradicts, or the data break a rule that the documents state. `2 weak`: a row is not supported by the sources it cites, or a source cannot show it. `3 design`: a modelling choice that will mislead or cost a user. `4 suggestion`: clarity, naming, an optional improvement. |
| **issue** | what is wrong, in one or two sentences; say what you expected instead |
| **evidence / source** | a link and the page, chapter or quotation (a few words) that supports your point; for a design issue, the rows or documents that show it; if you checked nothing outside the repository, say `from the repository only` |
| **how verified** | `checked in the cited source`, `checked in another source` (say which), `checked in the repository only`, or `not verified (reasoning only)` |
| **suggested fix** | the change you would make (a value, a rule, a column, a sentence); optional |

Example:

| id | area | table | row id | severity | issue | evidence / source | how verified | suggested fix |
|---|---|---|---|---|---|---|---|---|
| F-001 | C1 | claims | C0000 | 2 weak | The cited page does not mention the unit on this date | `https://example.org/page`, p. 12: the unit is first named on 14 June | checked in the cited source | Move the date to 14 June or cite another page |

Please also send, if you used the sample: the counts of `supported`, `partly supported`, `not supported` and `unverifiable` rows (claims and relations separately), and the completed `sample_claims.csv` and `sample_relations.csv`.

CSV header for findings:

```
id,area,table,row_id,severity,issue,evidence_source,how_verified,suggested_fix
```

## For us: how a finding is handled

1. **Record.** Every finding is copied unchanged into [responses.md](responses.md) with its id (prefix the reviewer and the date: `R1-F-001`), so nothing is lost or reworded.
2. **Verify against the sources.** We open the cited source and, where the reviewer's source differs, the source the row cites, and we read the passage. A finding is never accepted because of who made it or how sure it sounds. We write down what we read (link, page) in the response. Where a source cannot be opened we say so and try a second source.
3. **Triage.** One of these outcomes, with the reason in a sentence or two:
   - **accepted**: the finding is right (or the row is not supported). The change is made on a branch, one commit per finding or per group of the same kind, and the commit message and `docs/changelog.md` cite the finding id. The response says what changed (before and after).
   - **accepted in part**: part is right; the response says which part and what was left alone.
   - **declined**: the finding is wrong or the current choice stands. The response gives the reason with a source, or the rule or documented decision that decides it. A declined finding that shows a documentation gap still gets the documentation fixed.
   - **deferred**: right, but not now (needs a source we cannot read, a table that does not exist yet, or a design decision for later). The response says what is needed and the item is added to `docs/roadmap.md`.
   - **known**: already listed in the brief's "Known limitations" or in `docs/roadmap.md`; the response points to it and adds anything new.
   - **needs information**: we cannot reproduce it; the response says what we asked.
4. **Change only what a source supports.** No row changes without a source, whatever the severity. A design finding is decided in a separate step: we write the options and the cost, and the owner decides before anything is changed.
5. **Check.** After a change `python scripts/validate.py` (0 errors, no new warnings), `python scripts/build.py --check`, the other checks of the brief, and `python scripts/review_sample.py --check` must pass; a change to a sampled row regenerates the sample files in the same commit.
6. **Respond.** The status and the reason are added to [responses.md](responses.md) (one block per finding, in the format below), and the reviewer gets the list. A reviewer may reply to a declined finding; a reply is a new finding that cites the old one.

Format of an entry in `responses.md`:

```
### R1-F-001 (claims, C0000, severity 2): <one-line summary>
- **Status:** accepted | accepted in part | declined | deferred | known | needs information
- **Checked:** what we read, with link and page
- **Decision and reason:** ...
- **Change:** commit and files, or "none"; the roadmap line for a deferred item
- **Date:** YYYY-MM-DD
```
