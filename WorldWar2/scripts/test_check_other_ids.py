#!/usr/bin/env python3
"""Regression tests for scripts/check_other_ids.py conflict-group coverage.

G318 exists only on commander tenures (UC0074/UC0075). A claims-only scan
used to report the next free id as G318. The checker must also count
missions and tenures.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import check_other_ids as c  # noqa: E402


def test_tenure_only_group_is_counted():
    claims = c.groups_from_text(
        'conflict_group_id,claim_id\nG317,C0001\n', 'claim_id')
    tens = c.groups_from_text(
        'conflict_group_id,tenure_id\nG318,UC0001\nG318,UC0002\n', 'tenure_id')
    groups = c.merge_groups(claims, tens)
    assert 'G318' in groups and 'G317' in groups
    assert c.next_free_group_id(groups) == 'G319'
    assert c.next_free_group_id(claims) == 'G318'  # the old, incorrect scan


def test_empty_map():
    assert c.next_free_group_id({}) == 'G001'


def test_live_next_free_is_unused():
    groups = c.all_conflict_groups_from_files()
    nxt = c.next_free_group_id(groups)
    assert nxt not in groups, 'next free %s is already used: %s' % (nxt, groups.get(nxt))
    assert 'G318' in groups, 'expected tenure-only group G318 to be counted'
    assert c.num(nxt) > 318


def main():
    tests = [
        test_tenure_only_group_is_counted,
        test_empty_map,
        test_live_next_free_is_unused,
    ]
    failed = 0
    for fn in tests:
        try:
            fn()
            print('OK', fn.__name__)
        except AssertionError as e:
            failed += 1
            print('FAIL', fn.__name__ + ':', e)
    if failed:
        print('%d test(s) failed' % failed)
        return 1
    print('ALL CHECK_OTHER_IDS TESTS PASSED (%d)' % len(tests))
    return 0


if __name__ == '__main__':
    sys.exit(main())
