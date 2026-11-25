# Maintainer notes

This page is for people who run the checks, review a pull request, or cut a release. The rules for adding data are in [CONTRIBUTING.md](../CONTRIBUTING.md). Internal operating notes used by the project owner are kept privately and are not in this repository.

## Checks

Run the scripts from the `WorldWar2/` directory. One command runs the full set:

```bash
bash scripts/run_checks.sh
```

That runs `validate.py`, `check_json_fields.py`, `semantic_tests.py`, `build.py --check`, `build_references.py --check`, `review_sample.py --check`, `check_coordinates.py`, the two audit scripts, and (when `origin/main` is available) `check_claim_ids.py`, `check_mission_ids.py`, `check_commander_ids.py` and `check_other_ids.py`.

The GitHub Actions workflow in `.github/workflows/validate.yml` runs on every push and pull request, including pull requests from forks: `validate.py`, `check_json_fields.py`, `check_coordinates.py` and `audit_temporal_relationships.py` (the last two do not fail the job), `build.py`, `build.py --check` (fails if `build/` is stale), `semantic_tests.py`, and the id-collision checks against the pull request's base `main` (or `origin/main` on a push). It uses the `pull_request` event, a read-only token and no secrets.

`validate.py` and `check_coordinates.py` also print warnings. A warning is a prompt to re-check a row, not an automatic failure. Some warnings on `main` are already known and left open; a change should not add a warning for a row it touches unless the pull request explains why.

## Releases

- `schema_version` and `data_version` are recorded in `build/manifest.json`, which `scripts/build.py` writes and `scripts/build.py --check` verifies.
- Public identifiers (`C####`, `CR####`, `PL####`, `R####`, `G####`, and the others listed in the README) are never reused or renumbered once they have been on `main`.
- Tags and GitHub releases are created only by the project owner. Do not add a tag or rebuild a distribution zip unless the owner asks.
- The whole repository is licensed under [CC BY-SA 4.0](../../LICENSE). Do not commit notes or extracts from copyrighted sources (see CONTRIBUTING, rule 10).

## Reviewing a contribution

- Every new or changed row has a source, and conflicting claims stay as separate rows.
- New identifiers must not collide with ids already on `main`. If two branches took the same new numbers, rebase the second branch onto the updated `main` and run `python scripts/renumber_new_ids.py` (dry-run), then `--apply`, so only its unpublished ids are remapped (see CONTRIBUTING, "Identifiers"). Then run `python scripts/build.py` and commit `build/`. Use `--keep-group G###` when the branch meant to add members to a group already on `main`. The script also remaps colliding scenario and roadmap numbers on lines the branch adds.
- Regenerated `build/` files are committed with the data change and pass `python scripts/build.py --check`.
- A contribution must not add copyrighted extracts, private research notes, or credentials.
