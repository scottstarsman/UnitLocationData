#!/usr/bin/env python3
"""Check that mission ids were not reused or silently dropped since a base revision (the history half of the mission-id rule; decision J1,
17 November 2026; the same rule as scripts/check_claim_ids.py for claims).

  python scripts/check_mission_ids.py                  compare with origin/main
  python scripts/check_mission_ids.py --base <rev>     compare with any revision

It reads build/other_domains/missions.csv and data/retired_missions.csv at <rev> and in the working tree (both may be absent at <rev>: the table is
new), and fails (exit 1) when
  * a mission id of <rev> is no longer a mission and is not listed in data/retired_missions.csv (a mission row was deleted without a record);
  * a mission id of <rev> now belongs to a different unit (the id was reused);
  * an id of the retired list at <rev> is missing from it now or is a mission again.
New ids since <rev> are listed, with the next free id. Standard library only.
"""
import argparse
import csv
import io
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common  # noqa: E402
from check_claim_ids import git, show  # noqa: E402

BUILT = os.path.join('build', 'other_domains', 'missions.csv')
RETIRED = os.path.join('data', 'retired_missions.csv')


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--base', default='origin/main', help='revision to compare with (default origin/main)')
    a = ap.parse_args()
    rc, prefix, _ = git('rev-parse', '--show-prefix')
    if rc:
        raise SystemExit('not inside a git work tree')
    prefix = prefix.strip()
    old_txt = show(a.base, prefix, BUILT, optional=True)
    old = {r['mission_id']: r['unit_id'] for r in csv.DictReader(io.StringIO(old_txt))} if old_txt else {}
    old_ret_txt = show(a.base, prefix, RETIRED, optional=True)
    old_ret = {r['mission_id'] for r in csv.DictReader(io.StringIO(old_ret_txt))} if old_ret_txt else set()
    path = os.path.join(common.ROOT, BUILT)
    new = {r['mission_id']: r['unit_id'] for r in common.read_dicts(path)[1]} if os.path.isfile(path) else {}
    rp = os.path.join(common.ROOT, RETIRED)
    new_ret = {r['mission_id'] for r in common.read_dicts(rp)[1]} if os.path.isfile(rp) else set()
    problems = []
    for mid in sorted(old):
        if mid not in new and mid not in new_ret:
            problems.append('%s (unit %s) was a mission at %s and is gone without a row in %s' % (mid, old[mid], a.base, RETIRED))
        elif mid in new and new[mid] != old[mid]:
            problems.append('%s was a mission of %s at %s and is now one of %s: an id is never reused' % (mid, old[mid], a.base, new[mid]))
    for mid in sorted(old_ret):
        if mid not in new_ret:
            problems.append('%s was retired at %s and is not in %s now: a retired id is never forgotten' % (mid, a.base, RETIRED))
        if mid in new:
            problems.append('%s was retired at %s and is a mission again: a retired id is never reused' % (mid, a.base))
    added = sorted(set(new) - set(old), key=lambda x: int(x[3:]))
    top = max([int(m[3:]) for m in list(new) + list(new_ret)] or [0])
    print('missions at %s: %d; now: %d; new ids: %s; retired now: %d; next free id: MSN%04d' % (
        a.base, len(old), len(new), (added[0] + '..' + added[-1] + ' (%d)' % len(added)) if added else 'none', len(new_ret), top + 1))
    for p in problems:
        print('PROBLEM:', p)
    if not problems:
        print('OK: no mission id was reused or dropped since %s' % a.base)
    return 1 if problems else 0


if __name__ == '__main__':
    sys.exit(main())
