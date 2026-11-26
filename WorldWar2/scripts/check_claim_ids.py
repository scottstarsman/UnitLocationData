#!/usr/bin/env python3
"""Check that claim ids were not reused or silently dropped since a base revision (the history half of the claim-id rule; see CONTRIBUTING.md, "Claim ids").

  python scripts/check_claim_ids.py                  compare with origin/main (the branch point of a pull request)
  python scripts/check_claim_ids.py --base <rev>     compare with any revision

scripts/validate.py checks what a single checkout can show (ids are unique and well formed, data/retired_claims.csv is consistent, no retired id is a claim).
This script needs git history, which a shallow CI checkout does not have, so it is run by hand before a pull request (and by whoever merges one). It reads
build/all_claims.csv (every domain; the next-free id is only current after python scripts/build.py; older revisions may still have a separate build/other_domains/claims.csv, which is also read at <rev>
so an id there cannot be reused unseen) and data/retired_claims.csv at <rev> and the working tree, and fails (exit 1) when
  * a claim id of <rev> is no longer a claim and is not listed in data/retired_claims.csv (a claim was deleted without a record);
  * a claim id of <rev> now belongs to a different unit (the id was reused for another claim);
  * an id of the retired list at <rev> is missing from it now (a retired id may not be forgotten) or is a claim again (reused).
Ids that are new since <rev> are listed (the highest id + 1 is the next free one). Standard library only.
"""
import argparse
import csv
import io
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common  # noqa: E402

RETIRED = os.path.join('data', 'retired_claims.csv')


def git(*args):
    p = subprocess.run(['git'] + list(args), capture_output=True, text=True, cwd=common.ROOT)
    return p.returncode, p.stdout, p.stderr


def show(rev, prefix, path, optional=False):
    rc, out, e = git('show', '%s:%s%s' % (rev, prefix, path.replace(os.sep, '/')))
    if rc:
        if optional:
            return None
        raise SystemExit('cannot read %s at %s: %s' % (path, rev, e.strip()))
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--base', default='origin/main', help='revision to compare with (default origin/main)')
    a = ap.parse_args()
    rc, prefix, _ = git('rev-parse', '--show-prefix')
    if rc:
        raise SystemExit('not inside a git work tree')
    prefix = prefix.strip()
    old_txt = show(a.base, prefix, os.path.join('build', 'all_claims.csv'))
    old = {r['claim_id']: r['unit_id'] for r in csv.DictReader(io.StringIO(old_txt))}
    old_other = show(a.base, prefix, os.path.join('build', 'other_domains', 'claims.csv'), optional=True)
    if old_other:
        old.update({r['claim_id']: r['unit_id'] for r in csv.DictReader(io.StringIO(old_other))})
    old_ret_txt = show(a.base, prefix, RETIRED, optional=True)
    old_ret = {r['claim_id'] for r in csv.DictReader(io.StringIO(old_ret_txt))} if old_ret_txt else set()
    new = {}
    for fn in (os.path.join('build', 'all_claims.csv'), os.path.join('build', 'other_domains', 'claims.csv')):
        path = os.path.join(common.ROOT, fn)
        if os.path.isfile(path):
            new.update({r['claim_id']: r['unit_id'] for r in common.read_dicts(path)[1]})
    rp = os.path.join(common.ROOT, RETIRED)
    new_ret = {r['claim_id'] for r in common.read_dicts(rp)[1]} if os.path.isfile(rp) else set()
    problems = []
    for cid in sorted(old):
        if cid not in new and cid not in new_ret:
            problems.append('%s (unit %s) was a claim at %s and is gone without a row in %s: a deleted claim is retired, not dropped' % (cid, old[cid], a.base, RETIRED))
        elif cid in new and new[cid] != old[cid]:
            problems.append('%s was a claim of %s at %s and is now a claim of %s: an id is never reused for another claim' % (cid, old[cid], a.base, new[cid]))
    for cid in sorted(old_ret):
        if cid not in new_ret:
            problems.append('%s was retired at %s and is not in %s now: a retired id is never forgotten' % (cid, a.base, RETIRED))
        if cid in new:
            problems.append('%s was retired at %s and is a claim again: a retired id is never reused' % (cid, a.base))
    added = sorted(set(new) - set(old), key=lambda x: int(x[1:]))
    top = max([int(c[1:]) for c in list(new) + list(new_ret)] or [0])
    print('claims at %s: %d; now: %d; new ids: %s; retired now: %d; next free id: C%04d' % (
        a.base, len(old), len(new), (added[0] + '..' + added[-1] + ' (%d)' % len(added)) if added else 'none', len(new_ret), top + 1))
    print('next-free claim id is from build/all_claims.csv; run python scripts/build.py after adding claims before relying on it')
    for p in problems:
        print('PROBLEM:', p)
    if not problems:
        print('OK: no id was reused or dropped since %s' % a.base)
    return 1 if problems else 0


if __name__ == '__main__':
    sys.exit(main())
