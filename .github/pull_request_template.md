Thank you. Please run the checks from `WorldWar2/` and fill this in. The [contributor guide](WorldWar2/CONTRIBUTING.md) has the rules, a worked example, and what to do when a check fails.

- [ ] I ran `bash scripts/run_checks.sh` (or the CI equivalent) and the errors are resolved.
- [ ] Every new or changed row has a source URL, and a page, chapter or section in `source_locator` or `notes` when the source has one.
- [ ] Confidence follows the rubric in CONTRIBUTING (a single source is 0.3 or 0.5; 0.7 when an authoritative source or two families support the place; Wikipedia is one family).
- [ ] Inferred or changed values give the old value, the new value and the reason, in `notes` (and in the changelog when the change is structural).
- [ ] Each new claim has a `theater` that matches its `operation_id` (it may differ from the unit's primary theater).
- [ ] New ids are the next free numbers and do not reuse an id already on `main`.
- [ ] No copyrighted extracts, private research notes or credentials are in this pull request.
- [ ] `python scripts/build.py` was run and the `build/` changes are committed.

If a check printed warnings or audit findings for rows I touched, I have explained them here:

