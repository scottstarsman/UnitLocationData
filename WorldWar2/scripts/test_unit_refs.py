#!/usr/bin/env python3
"""Regression tests for unit name resolution in composing_text.

A trailing parenthesis is a valid disambiguator ("16th Infantry Regiment (IJA)").
The index also stores the name with that parenthesis stripped so a same-nation
claim can use the short form. The short form must not be treated as a unique
name across all nations, or a published Western Front composing_text entry
("16th Infantry Regiment" on C0025) is rejected when a Japanese unit is added.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import unit_refs  # noqa: E402


def _units(*rows):
    """Install a temporary units table and rebuild the name index."""
    unit_refs.reset()
    by_id = {}
    for r in rows:
        u = {
            'unit_id': r[0], 'unit_name': r[1], 'nationality': r[2],
        }
        by_id[u['unit_id']] = u
    # Pin path to UNITS_CSV so load_units() does not reload the real table.
    import common
    unit_refs._cache['units'] = by_id
    unit_refs._cache['path'] = common.UNITS_CSV
    unit_refs._cache.pop('index', None)
    return by_id


def _clash(entry, nat='US', name='1st Infantry Division'):
    return unit_refs._name_clash(entry, nat, name)


def test_trailing_paren_does_not_clash_across_nations():
    _units(
        ('JPN-INF-016', '16th Infantry Regiment (IJA)', 'Japan'),
        ('US-INF-001D', '1st Infantry Division', 'US'),
    )
    # The C0025 shape: a US claim lists the short regiment name in composing_text.
    assert _clash('16th Infantry Regiment', 'US', '1st Infantry Division') == []
    # The full disambiguated name is still exactly one unit.
    assert _clash('16th Infantry Regiment (IJA)', 'US', '1st Infantry Division') == ['JPN-INF-016']


def test_same_nation_short_form_still_resolves():
    _units(
        ('JPN-INF-016', '16th Infantry Regiment (IJA)', 'Japan'),
        ('JPN-INF-002D', 'IJA 2nd Division (Sendai)', 'Japan'),
    )
    assert _clash('16th Infantry Regiment', 'Japan', 'IJA 2nd Division (Sendai)') == ['JPN-INF-016']


def test_ambiguous_exact_names_are_not_a_clash():
    _units(
        ('US-INF-106D', '106th Infantry Division', 'US'),
        ('GER-INF-106D', '106th Infantry Division', 'Germany'),
    )
    assert _clash('106th Infantry Division', 'UK', 'Some Corps') == []
    # Same-nation is unambiguous.
    assert _clash('106th Infantry Division', 'US', 'First Army') == ['US-INF-106D']


def test_unique_exact_name_still_clashes_across_nations():
    _units(
        ('JPN-DET-ICHIKI', 'Ichiki Detachment', 'Japan'),
    )
    assert _clash('Ichiki Detachment', 'US', '1st Marine Division') == ['JPN-DET-ICHIKI']


def test_live_c0025_is_not_flagged():
    """The published 1st Infantry Division composing_text must stay valid."""
    unit_refs.reset()
    import common
    path = os.path.join(common.ROOT, 'data', 'claims', 'us', 'US-INF-001D.csv')
    rows = common.read_dicts(path)[1]
    row = next(r for r in rows if r['claim_id'] == 'C0025')
    errs, _warns = unit_refs.check(row)
    name_errs = [e for e in errs if '16th Infantry Regiment' in e]
    assert not name_errs, name_errs


def main():
    tests = [
        test_trailing_paren_does_not_clash_across_nations,
        test_same_nation_short_form_still_resolves,
        test_ambiguous_exact_names_are_not_a_clash,
        test_unique_exact_name_still_clashes_across_nations,
        test_live_c0025_is_not_flagged,
    ]
    failed = 0
    try:
        for fn in tests:
            try:
                fn()
                print('OK', fn.__name__)
            except AssertionError as e:
                failed += 1
                print('FAIL', fn.__name__ + ':', e)
    finally:
        unit_refs.reset()
    if failed:
        print('%d test(s) failed' % failed)
        return 1
    print('ALL UNIT_REFS TESTS PASSED (%d)' % len(tests))
    return 0


if __name__ == '__main__':
    sys.exit(main())
