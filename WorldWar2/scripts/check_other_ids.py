#!/usr/bin/env python3
"""Check that published ids other than claims, missions, people and tenures were not reused
or silently dropped since a base revision.

  python scripts/check_other_ids.py                  compare with origin/main
  python scripts/check_other_ids.py --base <rev>     compare with any revision

scripts/validate.py already rejects a duplicate id inside one checkout. This script is the
history half: it compares the working tree with <rev> (default origin/main) so two pull
requests that took the same next-free id fail on the second branch once it is rebased.
It covers command relations (CR), places (PL), references (R), conflict groups (G, from claims, missions and commander tenures),
TO&E templates and assignments (TT, UT), aircraft types (AT) and ship classes (SC).
Claim, mission, person and tenure ids are checked by check_claim_ids.py,
check_mission_ids.py and check_commander_ids.py.

It fails (exit 1) when an id that existed at <rev> is missing now (a place may leave
data/places.csv only with a row in data/place_merges.csv), or now identifies a different
row. A conflict group id that existed at <rev> may gain members; it is a problem only
when none of its original claims still carry it and a disjoint set of claims uses it.
Needs git access to <rev> (CI fetches origin/main). Standard library only.
"""
import argparse
import csv
import glob
import io
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common  # noqa: E402
from check_claim_ids import git, show  # noqa: E402


def num(s):
    i = 0
    while i < len(s) and s[i].isalpha():
        i += 1
    return int(s[i:]) if i < len(s) else 0


def span(added):
    if not added:
        return 'none'
    added = list(added)
    return added[0] + '..' + added[-1] + ' (%d)' % len(added)


def read_map(txt, id_col, value_cols):
    if not txt:
        return {}
    out = {}
    for r in csv.DictReader(io.StringIO(txt)):
        i = (r.get(id_col) or '').strip()
        if not i:
            continue
        out[i] = '|'.join((r.get(c) or '').strip() for c in value_cols)
    return out


def file_map(path, id_col, value_cols):
    if not os.path.isfile(path):
        return {}
    out = {}
    for r in common.read_dicts(path)[1]:
        i = (r.get(id_col) or '').strip()
        if not i:
            continue
        out[i] = '|'.join((r.get(c) or '').strip() for c in value_cols)
    return out


def groups_from_rows(rows, member_col):
    """conflict_group_id -> set of member ids (claim_id, mission_id or tenure_id)."""
    groups = {}
    for r in rows:
        g = (r.get('conflict_group_id') or '').strip()
        mid = (r.get(member_col) or '').strip()
        if g and mid:
            groups.setdefault(g, set()).add(mid)
    return groups


def groups_from_text(txt, member_col):
    if not txt:
        return {}
    return groups_from_rows(csv.DictReader(io.StringIO(txt)), member_col)


def merge_groups(*dicts):
    out = {}
    for d in dicts:
        for g, members in d.items():
            out.setdefault(g, set()).update(members)
    return out


def groups_from_glob(pattern, member_col):
    groups = {}
    for path in sorted(glob.glob(pattern)):
        groups = merge_groups(groups, groups_from_rows(common.read_dicts(path)[1], member_col))
    return groups


def claim_groups_from_text(txt):
    """Claim members only (kept for the disjoint-set reuse check)."""
    return groups_from_text(txt, 'claim_id')


def claim_groups_from_files():
    pattern = os.path.join(common.ROOT, 'data', 'claims', '*', '*.csv')
    return groups_from_glob(pattern, 'claim_id')


def all_conflict_groups_from_files():
    """Every G#### used on claims, missions or commander tenures in the working tree."""
    return merge_groups(
        claim_groups_from_files(),
        groups_from_glob(os.path.join(common.ROOT, 'data', 'missions', '*', '*.csv'), 'mission_id'),
        groups_from_rows(common.read_dicts(os.path.join(common.ROOT, 'data', 'unit_commanders.csv'))[1], 'tenure_id')
        if os.path.isfile(os.path.join(common.ROOT, 'data', 'unit_commanders.csv')) else {},
    )


def next_free_group_id(groups):
    """First unused G#### after the highest id in the map (G001 if the map is empty)."""
    top = max([num(i) for i in groups] or [0])
    return 'G%03d' % (top + 1)


def all_conflict_groups_from_base(rev, prefix):
    """Every G#### used on claims, missions or commander tenures at <rev>."""
    old_claims = show(rev, prefix, os.path.join('build', 'all_claims.csv'), optional=True)
    if old_claims is None:
        old_claims = show(rev, prefix, os.path.join('build', 'other_domains', 'claims.csv'), optional=True)
    groups = groups_from_text(old_claims or '', 'claim_id')
    tens = show(rev, prefix, os.path.join('data', 'unit_commanders.csv'), optional=True)
    groups = merge_groups(groups, groups_from_text(tens or '', 'tenure_id'))
    # cwd is WorldWar2/; ls-tree of a revision lists paths relative to this prefix, so
    # "data/missions/..." (not "WorldWar2/data/missions/..."). The pathspec -- form is
    # reliable; "rev:WorldWar2/data/missions" is empty from this cwd.
    rc, listing, err = git('ls-tree', '-r', '--name-only', rev, '--', 'data/missions')
    if rc == 0 and listing.strip():
        for rel in listing.strip().splitlines():
            txt = show(rev, prefix, rel, optional=True)
            groups = merge_groups(groups, groups_from_text(txt or '', 'mission_id'))
    return groups


def check_table(name, old, new, problems, dropped_ok=None):
    """Compare id -> identity maps. dropped_ok(id) is True when a missing id is explained."""
    for i in sorted(old, key=num):
        if i not in new:
            if dropped_ok and dropped_ok(i):
                continue
            problems.append('%s %s was present at the base revision and is gone: an id is never dropped or reused' % (name, i))
        elif new[i] != old[i]:
            problems.append('%s %s was %s at the base revision and is now %s: an id is never reused' % (name, i, old[i], new[i]))
    added = sorted(set(new) - set(old), key=num)
    top = max([num(i) for i in new] or [0])
    return added, top


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--base', default='origin/main', help='revision to compare with (default origin/main)')
    a = ap.parse_args()
    rc, prefix, err = git('rev-parse', '--show-prefix')
    if rc:
        raise SystemExit('not inside a git work tree: %s' % (err or '').strip())
    prefix = prefix.strip()
    problems = []

    tables = [
        ('command relations', 'data/command_relations.csv', 'relation_id',
         ['subject_unit_id', 'higher_unit_id', 'relationship'], 'CR', 4),
        ('references', 'data/references_meta.csv', 'reference_id', ['url'], 'R', 3),
        ('places', 'data/places.csv', 'place_id', ['name'], 'PL', 4),
        ('TO&E templates', 'data/toe_templates.csv', 'template_id', ['template_name'], 'TT', 4),
        ('TO&E assignments', 'data/unit_toe.csv', 'assignment_id', ['unit_id', 'template_id'], 'UT', 4),
        ('aircraft types', 'data/aircraft_types.csv', 'type_id', ['designation'], 'AT', 3),
        ('ship classes', 'data/ship_classes.csv', 'class_id', ['class_name'], 'SC', 3),
    ]

    merges_txt = show(a.base, prefix, os.path.join('data', 'place_merges.csv'), optional=True)
    old_merges = set()
    if merges_txt:
        old_merges = {r['retired_place_id'] for r in csv.DictReader(io.StringIO(merges_txt)) if r.get('retired_place_id')}
    new_merges_path = os.path.join(common.ROOT, 'data', 'place_merges.csv')
    new_merges = set()
    if os.path.isfile(new_merges_path):
        new_merges = {r['retired_place_id'] for r in common.read_dicts(new_merges_path)[1] if r.get('retired_place_id')}
    for pid in sorted(old_merges, key=num):
        if pid not in new_merges:
            problems.append('retired place id %s was in data/place_merges.csv at %s and is gone: a retired id is never forgotten' % (pid, a.base))

    for label, path, id_col, value_cols, prefix_code, width in tables:
        old = read_map(show(a.base, prefix, path, optional=True), id_col, value_cols)
        new = file_map(os.path.join(common.ROOT, path), id_col, value_cols)
        dropped_ok = (lambda i, _new_merges=new_merges: i in _new_merges) if path.endswith('places.csv') else None
        added, top = check_table(label, old, new, problems, dropped_ok=dropped_ok)
        print('%s at %s: %d; now: %d; new ids: %s; next free id: %s%0*d' % (
            label, a.base, len(old), len(new), span(added), prefix_code, width, top + 1))

    old_claims = show(a.base, prefix, os.path.join('build', 'all_claims.csv'), optional=True)
    if old_claims is None:
        old_claims = show(a.base, prefix, os.path.join('build', 'other_domains', 'claims.csv'), optional=True)
    old_claim_g = claim_groups_from_text(old_claims or '')
    new_claim_g = claim_groups_from_files()
    for g in sorted(old_claim_g, key=num):
        if g not in new_claim_g:
            # A group may be dissolved when a conflict is withdrawn; that is allowed.
            continue
        if old_claim_g[g].isdisjoint(new_claim_g[g]):
            problems.append('conflict group %s was claims %s at %s and is now a disjoint set %s: an id is never reused' % (
                g, ','.join(sorted(old_claim_g[g], key=num)), a.base, ','.join(sorted(new_claim_g[g], key=num))))
    old_g = all_conflict_groups_from_base(a.base, prefix)
    new_g = all_conflict_groups_from_files()
    added_g = sorted(set(new_g) - set(old_g), key=num)
    print('conflict groups at %s: %d; now: %d; new ids: %s; next free id: %s' % (
        a.base, len(old_g), len(new_g), span(added_g), next_free_group_id(new_g)))

    for p in problems:
        print('PROBLEM:', p)
    if not problems:
        print('OK: no command-relation, place, reference, conflict-group, TO&E, aircraft-type or ship-class id was reused or dropped since %s' % a.base)
    return 1 if problems else 0


if __name__ == '__main__':
    sys.exit(main())
