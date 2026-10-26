#!/usr/bin/env python3
"""Promote placeholder units that now have a claim file: set record_status=active in data/units.csv.

Run after adding data/claims/<nationality>/<unit_id>.csv for a unit that was a placeholder. Prints the units it changed.
Use --check to list them without writing (exit code 1 if any need promoting). Standard library only.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common  # noqa: E402


def main():
    check = '--check' in sys.argv[1:]
    header, rows = common.read_rows(common.UNITS_CSV)
    ix = {h: i for i, h in enumerate(header)}
    have = {os.path.basename(p)[:-4] for p in common.claim_files()}
    changed = []
    for r in rows:
        if r[ix['unit_id']] in have and r[ix['record_status']] == 'placeholder':
            changed.append(r[ix['unit_id']])
            if not check:
                r[ix['record_status']] = 'active'
    if changed and not check:
        with open(common.UNITS_CSV, 'wb') as f:
            f.write(common.csv_bytes(header, rows))
    print(('would promote' if check else 'promoted') + ' %d unit(s): %s' % (len(changed), ', '.join(changed) or '-'))
    return 1 if (check and changed) else 0


if __name__ == '__main__':
    sys.exit(main())
