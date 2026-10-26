"""Losslessness check for scripts/migrate_unit_ids.py --verify REF: regenerate the old engaged_with / composing_units strings from the new data (the
derived engaged_with_names / composing_units_names) and diff them against git ref REF, entry by entry. Prints every difference with its reason and
exits 1 only when something other than a known, explained difference is found (a changed other column, a lost entry, a changed unit row)."""
import collections
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common  # noqa: E402
import unit_refs as ur  # noqa: E402
import migrate_unit_ids as mig  # noqa: E402


def entries(s):
    return ur.split_list(s)


def run(ref):
    ur.reset()
    old = mig.old_rows(ref)
    new_header, new_rows = common.load_all_claims()
    newd = {r['claim_id']: r for r in new_rows}
    problems = []
    diffs = collections.OrderedDict()
    n_cells = collections.Counter()
    total = 0
    for path, (h, rs) in old.items():
        for d in rs:
            total += 1
            n = newd.get(d['claim_id'])
            if n is None:
                problems.append('%s: claim missing in the new data' % d['claim_id'])
                continue
            for c in h:
                if c in ('engaged_with', 'composing_units'):
                    continue
                if d[c] != n[c]:
                    problems.append('%s: column %s changed: %r -> %r' % (d['claim_id'], c, d[c][:60], n[c][:60]))
            for old_col, new_col in (('engaged_with', 'engaged_with_names'), ('composing_units', 'composing_units_names')):
                o, nw = d[old_col], n[new_col]
                n_cells[old_col] += 1 if o else 0
                if o == nw:
                    continue
                oe, ne = entries(o), entries(nw)
                oo, nn = list(oe), list(ne)
                for e in list(oo):
                    if e in nn:
                        nn.remove(e)
                        oo.remove(e)
                if not oo and not nn:
                    reason = 'order only'
                else:
                    reason = 'wording'
                diffs.setdefault((old_col, reason), []).append((d['claim_id'], oo, nn, o, nw))
                # an entry may change wording but not disappear: counts must agree
                if len(oe) != len(ne):
                    problems.append('%s %s: %d entries before, %d after (%r -> %r)' % (d['claim_id'], old_col, len(oe), len(ne), o, nw))
    # unit table: old rows unchanged, only the two placeholders added
    ou = {u['unit_id']: u for u in mig.old_units(ref)}
    nu = {u['unit_id']: u for u in mig.old_units()}
    for uid, u in ou.items():
        if nu.get(uid) != u:
            problems.append('unit row %s changed' % uid)
    added = sorted(set(nu) - set(ou))
    print('claims compared: %d; non-blank old engaged_with cells %d, composing_units cells %d' % (total, n_cells['engaged_with'], n_cells['composing_units']))
    print('units added: %s' % added)
    for (col, reason), items in diffs.items():
        print('\n== %s: %d cells differ (%s)' % (col, len(items), reason))
        agg = collections.Counter()
        for cid, oo, nn, o, nw in items:
            if reason == 'order only':
                print('  %s: same entries, different order: %r -> %r' % (cid, o, nw))
            else:
                agg[(tuple(oo), tuple(nn))] += 1
                print('  %s: %s => %s' % (cid, oo, nn))
        if agg:
            print('  distinct wording changes: %d' % len(agg))
    cnt = collections.Counter((c, r) for (c, r), items in diffs.items() for _ in items)
    print('\nsummary:', {'%s %s' % k: v for k, v in cnt.items()})
    print('problems: %d' % len(problems))
    for p in problems:
        print('  PROBLEM', p)
    return 1 if problems else 0
