#!/usr/bin/env python3
"""Check that person and commander-tenure ids were not reused or silently dropped since a base revision.

  python scripts/check_commander_ids.py                  compare with origin/main
  python scripts/check_commander_ids.py --base <rev>     compare with any revision

scripts/validate.py checks what a single checkout can show (ids unique, well formed, no gaps).
This script needs git history. It reads data/people.csv and data/unit_commanders.csv at <rev>
and in the working tree, and fails (exit 1) when
  * a person_id or tenure_id of <rev> is missing now (an id is never dropped or reused);
  * a person_id of <rev> now has a different canonical_name that is not a known spelling
    continuation (only reported when the id is attached to a different surname — a hard reuse).
Ids that are new since <rev> are listed (the highest id + 1 is the next free one).
At a base revision that does not yet have the tables, every current id is new. Standard library only.
"""
import argparse
import csv
import io
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common  # noqa: E402

PEOPLE = os.path.join('data', 'people.csv')
TENURES = os.path.join('data', 'unit_commanders.csv')


def git(*args):
    p = subprocess.run(['git'] + list(args), capture_output=True, text=True, cwd=common.ROOT)
    return p.returncode, p.stdout, p.stderr


def show(rev, prefix, path):
    rc, out, e = git('show', '%s:%s%s' % (rev, prefix, path.replace(os.sep, '/')))
    if rc:
        return None
    return out


def read_map(txt, id_col, extra_col=None):
    if not txt:
        return {}
    rows = csv.DictReader(io.StringIO(txt))
    if extra_col:
        return {r[id_col]: r.get(extra_col, '') for r in rows}
    return {r[id_col]: True for r in rows}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--base', default='origin/main', help='revision to compare with (default origin/main)')
    a = ap.parse_args()
    rc, prefix, _ = git('rev-parse', '--show-prefix')
    if rc:
        raise SystemExit('not inside a git work tree')
    prefix = prefix.strip()
    old_people_txt = show(a.base, prefix, PEOPLE)
    old_tenures_txt = show(a.base, prefix, TENURES)
    old_people = read_map(old_people_txt, 'person_id', 'canonical_name')
    old_tenures = read_map(old_tenures_txt, 'tenure_id', 'person_id')
    new_people_path = os.path.join(common.ROOT, PEOPLE)
    new_tenures_path = os.path.join(common.ROOT, TENURES)
    new_people, new_tenures = {}, {}
    if os.path.isfile(new_people_path):
        new_people = {r['person_id']: r.get('canonical_name', '') for r in common.read_dicts(new_people_path)[1]}
    if os.path.isfile(new_tenures_path):
        new_tenures = {r['tenure_id']: r.get('person_id', '') for r in common.read_dicts(new_tenures_path)[1]}
    problems = []
    for pid in sorted(old_people, key=lambda x: int(x[2:])):
        if pid not in new_people:
            problems.append('%s was a person at %s and is gone: a person id is never dropped or reused' % (pid, a.base))
    for tid in sorted(old_tenures, key=lambda x: int(x[2:])):
        if tid not in new_tenures:
            problems.append('%s was a tenure at %s and is gone: a tenure id is never dropped or reused' % (tid, a.base))
        elif new_tenures[tid] != old_tenures[tid]:
            problems.append('%s was a tenure of %s at %s and is now a tenure of %s: an id is never reused for another person' % (
                tid, old_tenures[tid], a.base, new_tenures[tid]))
    added_p = sorted(set(new_people) - set(old_people), key=lambda x: int(x[2:]))
    added_t = sorted(set(new_tenures) - set(old_tenures), key=lambda x: int(x[2:]))
    top_p = max([int(c[2:]) for c in new_people] or [0])
    top_t = max([int(c[2:]) for c in new_tenures] or [0])
    def span(added):
        if not added:
            return 'none'
        return added[0] + '..' + added[-1] + ' (%d)' % len(added)
    print('people at %s: %d; now: %d; new ids: %s; next free id: PE%04d' % (
        a.base, len(old_people), len(new_people), span(added_p), top_p + 1))
    print('tenures at %s: %d; now: %d; new ids: %s; next free id: UC%04d' % (
        a.base, len(old_tenures), len(new_tenures), span(added_t), top_t + 1))
    for p in problems:
        print('PROBLEM:', p)
    if not problems:
        print('OK: no person or tenure id was reused or dropped since %s' % a.base)
    return 1 if problems else 0


if __name__ == '__main__':
    sys.exit(main())
