#!/usr/bin/env python3
"""Answer "which higher headquarters held this unit on this date?" from the derived build/command_relations.csv.

Usage: python scripts/who_controls.py US-ARM-002D 1944-08-28
       python scripts/who_controls.py "2nd Armored" 1944-08-28   (matches a substring of the subject name)

Prints every interval that covers the date, with its support (documented / table / inferred) and how its end was fixed.
Intervals whose end is inferred from the next claim, or whose start or end is a range, are marked. The table covers US units
with a claim between 1944-07-24 and 1944-09-20 only; run python scripts/build.py first. Standard library only.
"""
import csv
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common  # noqa: E402


def main(argv):
    if len(argv) != 2:
        print(__doc__)
        return 2
    who, date = argv
    path = os.path.join(common.BUILD_DIR, 'command_relations.csv')
    _h, rows = common.read_dicts(path)
    hits = [r for r in rows if (r['subject_unit_id'] == who or who.lower() in r['subject_name'].lower())
            and r['valid_from'] <= date and (not r['valid_to'] or date <= r['valid_to'])]
    if not hits:
        print('no relationship interval covers %s on %s in %s' % (who, date, os.path.relpath(path, common.ROOT)))
        return 1
    for r in sorted(hits, key=lambda r: (r['relationship'], r['higher_unit_id'])):
        flags = []
        if r['valid_from_latest']:
            flags.append('start between %s and %s' % (r['valid_from'], r['valid_from_latest']))
        if r['valid_to_basis'] == 'inferred_from_next_claim':
            flags.append('end inferred from next claim (last listed %s)' % r['valid_to_earliest'])
        if r['valid_to_basis'] == 'open_at_last_claim':
            flags.append('no end recorded; latest claim lists it')
        print('%s -> %s: %s, %s to %s, support %s (%s) [%s]%s' % (
            r['subject_unit_id'], r['higher_name'], r['relationship'], r['valid_from'], r['valid_to'] or 'open', r['support'],
            r['valid_to_basis'] or r['valid_from_basis'], r['source_claim_ids'], ('; ' + '; '.join(flags)) if flags else ''))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
