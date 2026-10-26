# Earlier review notes

Working notes from the review passes on the dataset. They record what each reviewer
claimed, what the sources say, what was changed and what was declined, so a row's history
can be traced.

- [review_changes.md](review_changes.md): the change log for every review and batch (start here)
- [spot_check_15.md](spot_check_15.md): the first 15-row sample (June 1944, before the parent/command split)
- [parent_split_sample.md](parent_split_sample.md): before/after examples of the parent_formation split
- [spot_check_batch1.md](spot_check_batch1.md), [spot_check_batch2.md](spot_check_batch2.md), [spot_check_batch3.md](spot_check_batch3.md): the review samples for the three US batches, in their post-review state
- [temporal_audit.md](temporal_audit.md): output and triage of `scripts/audit_temporal_relationships.py`
- [operations_backfill.md](operations_backfill.md): how the old campaign / operation_name / sub_operation_name columns were migrated to `operation_id`, the claims left on a campaign, and the contested operation boundaries

The spot-check files show `parent_formation` or the command columns as they were when each
sample was drawn. For the current values see `data/claims/` and `build/all_claims.csv`.
