#!/usr/bin/env python3
"""Losslessness check for review items 1 to 7 (branch review-items-1-7): composing_units, composing_text, engaged_with and engaged_note.

  python scripts/verify_review_items.py --base <rev>     <rev> = the commit before the branch (the one that has build/all_claims.csv without these changes)

Compares build/all_claims.csv of <rev> (read with git show) with the working tree, claim by claim, and prints every changed cell with the reason (REASONS: item, what
happened to the relationship wording). It fails (exit 1) if
  * a claim changed that has no entry in REASONS, or REASONS names a claim that did not change;
  * engaged_with or engaged_note changed anywhere;
  * a word of the old composing_units_names (the text a reader sees) is missing from the new one, other than `attached` and the words listed in ALLOWED_DROPPED
    (the raw unit id that is now carried by composing_units, and the prepositions of the removed relationship wording).
Standard library only; one-off, kept as the record next to migrate_review_items.py.
"""
import argparse
import csv
import io
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common  # noqa: E402

CHECKED = ['engaged_with', 'engaged_note', 'composing_units', 'composing_text']
ALLOWED_DROPPED = {'attached', 'to', 'with', 'ger', 'kg', 'us', 'cca', '002d', 'vonluck'}

REASONS = {
    # item 1 and item 2: the word removed; the relationship is a relation (R) or a row of docs/deferred_relations.md (D)
    'C0002': 'item 1: `attached:` prefix removed (already relation CR0001)',
    'C0010': 'item 1: 6th Fallschirmjaeger Regiment is relation CR0372',
    'C0017': 'item 1: 56th Infantry Brigade, deferred D01',
    'C0018': 'item 1: 1st Canadian Parachute Battalion, deferred D02',
    'C0025': 'item 1: 116th Infantry Regiment, deferred D03',
    'C0031': 'item 1: 2nd and 5th Ranger Battalions, deferred D04 and D05',
    'C0032': 'item 1: `attached:` prefix removed (already relation CR0087)',
    'C0217': 'item 1: 2nd Irish Guards, deferred D06',
    'C0105': 'item 2: 30th Division with XIX Corps, relation CR0373',
    'C0120': 'item 2: 101st Airborne Division with VIII Corps, evidence of CR0100',
    'C0490': 'item 2: 35th Infantry Division with V Corps, evidence of CR0277',
    'C0037': 'item 2: Panzer Lehr only planned, no relation',
    'C0030': 'item 2: 82nd and 101st Airborne with VII Corps, reworded (relations exist)',
    'C0506': 'item 2: Combat Command B, deferred D07',
    'C0507': 'item 2: 22nd Infantry Regiment, deferred D08',
    'C0094': 'item 2: 4th Armoured Brigade, id added (relation CR0059 starts later), reworded',
    'C0164': 'item 2: C Squadron, 2nd County of London Yeomanry, deferred D10',
    'C0161': 'item 2: Kampfgruppe Weidinger, id added, evidence of CR0032',
    'C0493': 'item 2: Combat Command A with the 22nd Infantry, id added, evidence of CR0177, deferred D09',
    'C0211': 'item 2: 2nd Battalion, 915th Regiment, deferred D11',
    'C0089': 'items 2 and 3: Kampfgruppe Heintz, relation CR0374, id added',
    'C0100': 'items 2 and 3: Combat Command A, qualified entry',
    'C0127': 'items 2 and 3: Kampfgruppe Meyer and Boehm, ids added, evidence of CR0020',
    'C0170': 'items 2 and 3: Kampfgruppe Frey, id added, evidence of CR0023',
    'C0173': 'items 2 and 3: Kampfgruppe Weidinger, id added, evidence of CR0030',
    'C0006': 'item 3: Kampfgruppe Meyer, id added',
    'C0126': 'item 3: Kampfgruppe Rohrbach, id added',
    'C0145': 'item 3: Kampfgruppe Rohrbach, id added',
    'C0184': 'item 3: Kampfgruppe von Luck, id added',
}
# C0002 and C0032 were converted by the unit-ids branch itself (their old cells are the same in <rev> as now), so they need no reason here
IGNORE_UNCHANGED = {'C0002', 'C0032'}


def words(s):
    return set(re.findall(r'[a-z0-9]+', s.lower()))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--base', required=True)
    a = ap.parse_args()
    out = subprocess.run(['git', 'show', '%s:build/all_claims.csv' % a.base], capture_output=True, text=True, cwd=common.ROOT)
    if out.returncode:
        raise SystemExit(out.stderr)
    old = {r['claim_id']: r for r in csv.DictReader(io.StringIO(out.stdout))}
    new = {r['claim_id']: r for r in csv.DictReader(open(os.path.join(common.ROOT, 'build', 'all_claims.csv'), encoding='utf-8'))}
    problems = []
    if set(old) != set(new):
        problems.append('claim ids differ: %s' % sorted(set(old) ^ set(new)))
    changed, cells = set(), 0
    for cid in sorted(set(old) & set(new)):
        for col in CHECKED:
            if old[cid][col] != new[cid][col]:
                cells += 1
                changed.add(cid)
                print('%s %s\n    was: %r\n    now: %r\n    why: %s' % (cid, col, old[cid][col], new[cid][col], REASONS.get(cid, '??? NO REASON')))
                if col in ('engaged_with', 'engaged_note'):
                    problems.append('%s %s changed (it must not)' % (cid, col))
        dropped = words(old[cid]['composing_units_names']) - words(new[cid]['composing_units_names']) - ALLOWED_DROPPED
        if dropped:
            problems.append('%s: words of the old composing_units_names are missing now: %s' % (cid, sorted(dropped)))
    for cid in sorted(changed - set(REASONS)):
        problems.append('%s changed without a reason' % cid)
    for cid in sorted(set(REASONS) - changed - IGNORE_UNCHANGED):
        problems.append('%s has a reason but did not change' % cid)
    print('\n%d changed cells in %d claims (of %d); engaged_with and engaged_note unchanged: %s' % (
        cells, len(changed), len(new), 'yes' if not any('engaged' in p for p in problems) else 'NO'))
    for p in problems:
        print('PROBLEM:', p)
    return 1 if problems else 0


if __name__ == '__main__':
    sys.exit(main())
