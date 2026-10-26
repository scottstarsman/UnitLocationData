#!/usr/bin/env python3
"""Migration: claims' `command_relationships` JSON cell -> data/command_relations.csv + data/command_relation_claims.csv.

Run once on the layout before this change (claim files that still have the `command_relationships` column):
    python scripts/migrate_command_relations.py [--dry-run]
It
  * derives one relation row per interval with the same run logic that built build/command_relations.csv until now (a run is the
    consecutive preferred claims of one unit that list the same (higher unit, relationship); valid_from is the earliest start any entry
    states, else the first claim date; valid_to is the entry's effective_to, else the day before the unit's next claim that no longer lists the
    pair (valid_to_basis inferred_from_next_claim, valid_to_earliest = the last claim that lists it), else blank (open_at_last_claim));
    unlike before it also keeps `organic` entries and entries with unit_id null (explicit `unknown` placeholders);
  * links every entry of every claim to its relation (data/command_relation_claims.csv) and keeps what the claim itself stated
    (stated_* columns) so that the old cell can be rebuilt exactly (key order aside);
  * puts entries of alternate and disputed claims on the preferred relation that covers the claim date, else on a relation of their own with
    that status (never shown in build/command_relations.csv);
  * sets end_unknown (a temporary relationship, i.e. not organic/assigned/unspecified_subordination/unknown, whose end no source dates) and
    change_undated (five German parent changes of June 1944 that no entry dates; see below);
  * removes the `command_relationships` column from every claim file.
    python scripts/migrate_command_relations.py --verify <git-ref-before-the-migration>
rebuilds every claim's old cell from the new tables and compares it with the claim files of that commit, and compares the derived
build/command_relations.csv rows of the window 1944-07-24..1944-12-31 with the old ones. Standard library only.

Undated changes: for I SS Panzer Corps, II SS Panzer Corps, 21st Panzer, 12th SS Panzer and Panzer Lehr the parent changes between two
claim dates and no entry dates the change (scripts/audit_temporal_relationships.py, check parent_change). The outgoing relation (valid_to
inferred_from_next_claim, valid_to_earliest = its last listing) and the incoming relation (valid_from = its first listing) get change_undated
true: the change happened somewhere between those two claim dates and no source says when. No date is invented and no date is moved.
"""
import argparse
import datetime
import json
import os
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common  # noqa: E402
import command_relations as cr  # noqa: E402

UNDATED_SUBJECTS = ('GER-SSPZ-001C', 'GER-SSPZ-002C', 'GER-PZ-021D', 'GER-SSPZ-012D', 'GER-PZ-LEHRD')
WINDOW = ('1944-07-24', '1944-12-31')   # the window of the old derived table


def addday(iso, n):
    return (datetime.date.fromisoformat(iso) + datetime.timedelta(days=n)).isoformat()


def run_intervals(claims, ivs, emap):
    """The old run logic over `claims` = [(claim row, [(index, entry), ...])]; appends intervals to ivs, entry -> interval to emap."""
    by = {}
    for r, ents in claims:
        by.setdefault(r['unit_id'], []).append((r, ents))
    for uid, rs in by.items():
        rs.sort(key=lambda x: (x[0]['date'], x[0]['claim_id']))
        open_iv = {}

        def close(key, iv, date_next, last_listed):
            iv['valid_to'] = addday(date_next, -1)
            iv['valid_to_earliest'] = last_listed
            iv['valid_to_basis'] = 'inferred_from_next_claim'
            ivs.append(iv)
            del open_iv[key]
        for r, ents in rs:
            keys = set()
            for i, e in ents:
                key = (e.get('unit_id'), e['relationship'])
                keys.add(key)
                start = e.get('effective_from') or r['date']
                if key in open_iv:
                    iv = open_iv[key]
                    iv['last_listed'] = r['date']
                    if start < iv['valid_from']:
                        iv['valid_from'] = start
                    if e.get('date_basis') and iv['date_basis'] == 'inferred' and e['date_basis'] != 'inferred':
                        iv['date_basis'] = e['date_basis']
                else:
                    iv = {'subject_unit_id': uid, 'higher_unit_id': e.get('unit_id') or '', 'relationship': e['relationship'],
                          'valid_from': start, 'valid_from_latest': e.get('effective_from_latest', ''), 'valid_from_time': e.get('effective_time', ''),
                          'valid_from_basis': e.get('date_basis', 'inferred') if 'effective_from' in e else 'claim_date',
                          'valid_to': '', 'valid_to_earliest': '', 'valid_to_time': '', 'valid_to_basis': '',
                          'end_unknown': 'false', 'change_undated': 'false', 'date_basis': e.get('date_basis', 'inferred'),
                          'ordered_date': e.get('ordered_date', ''), 'status': r['claim_status'] or 'preferred', 'note': e.get('note', ''),
                          'last_listed': r['date']}
                    open_iv[key] = iv
                emap[(r['claim_id'], i)] = iv
                if e.get('effective_to'):
                    iv = open_iv.pop(key)
                    iv['valid_to'] = e['effective_to']
                    iv['valid_to_earliest'] = e.get('effective_to_earliest', '')
                    iv['valid_to_time'] = e.get('effective_to_time', '')
                    iv['valid_to_basis'] = e.get('effective_to_basis') or e.get('date_basis', 'inferred')
                    twin = [o for o in ivs if (o['subject_unit_id'], o['higher_unit_id'], o['relationship'], o['valid_to'], o['status']) ==
                            (uid, iv['higher_unit_id'], iv['relationship'], iv['valid_to'], iv['status'])]
                    if twin:   # the same interval restated by another claim (same end): one row, earliest start
                        twin[0]['valid_from'] = min(twin[0]['valid_from'], iv['valid_from'])
                        for k, v in list(emap.items()):
                            if v is iv:
                                emap[k] = twin[0]
                    else:
                        ivs.append(iv)
            for key in list(open_iv):
                if key not in keys and r['date'] > open_iv[key]['last_listed']:
                    close(key, open_iv[key], r['date'], open_iv[key]['last_listed'])
        for key, iv in open_iv.items():
            iv['valid_to_basis'] = 'open_at_last_claim'
            ivs.append(iv)


def build(claims):
    """claims: all claim rows (dicts with command_relationships text). Returns (relation rows, link rows)."""
    ivs, emap = [], {}
    pref, other = [], []
    for r in claims:
        ents = list(enumerate(json.loads(r['command_relationships'])))
        (pref if r['claim_status'] in ('preferred', '') else other).append((r, ents))
    run_intervals(pref, ivs, emap)
    # alternate / disputed claims: onto the preferred relation of the same pair that covers the date, else their own relation
    orphan = []
    for r, ents in other:
        rest = []
        for i, e in ents:
            hit = [iv for iv in ivs if iv['status'] == 'preferred' and (iv['subject_unit_id'], iv['higher_unit_id'], iv['relationship']) ==
                   (r['unit_id'], e.get('unit_id') or '', e['relationship']) and iv['valid_from'] <= r['date'] and (not iv['valid_to'] or r['date'] <= iv['valid_to'])]
            if hit:
                emap[(r['claim_id'], i)] = hit[0]
            else:
                rest.append((i, e))
        if rest:
            orphan.append((r, rest))
    for status in ('alternate', 'disputed'):
        run_intervals([(r, es) for r, es in orphan if r['claim_status'] == status], ivs, emap)
    standing = common.relationship_group('standing')
    ranked = sorted(ivs, key=lambda iv: (iv['subject_unit_id'], iv['valid_from'], iv['higher_unit_id'], iv['relationship'], iv['valid_to'], iv['status']))
    for n, iv in enumerate(ranked, start=1):
        iv['relation_id'] = 'CR%04d' % n
        if iv['valid_to_basis'] in cr.END_INFERRED and iv['relationship'] not in standing:
            iv['end_unknown'] = 'true'
    # five undated parent changes (see the module docstring)
    flagged = []
    for s in UNDATED_SUBJECTS:
        named = [iv for iv in ranked if iv['subject_unit_id'] == s and iv['status'] == 'preferred' and iv['higher_unit_id'] and iv['relationship'] != 'organic']
        for a, b in zip(named, named[1:]):
            if a['higher_unit_id'] != b['higher_unit_id'] and a['valid_to_basis'] == 'inferred_from_next_claim' and b['valid_from_basis'] == 'claim_date' \
                    and b['valid_from'] > a['valid_to_earliest']:
                a['change_undated'] = b['change_undated'] = 'true'
                flagged.append((s, a['relation_id'], b['relation_id']))
    links = []
    for r, ents in [(r, list(enumerate(json.loads(r['command_relationships'])))) for r in claims]:
        for i, e in ents:
            stated = {k: e[k] for k, _c in cr.STATED if k in e}
            links.append({'relation_id': emap[(r['claim_id'], i)]['relation_id'], 'claim_id': r['claim_id'], 'seq': str(i + 1), 'role': cr.role_of(stated),
                          **{c: stated.get(k, '') for k, c in cr.STATED}})
    links.sort(key=lambda l: (l['claim_id'], int(l['seq'])))
    rows = [{c: iv[c] for c in cr.REL_HEADER} for iv in ranked]
    return rows, links, flagged


def git_claims(ref):
    """Claim rows (with the old command_relationships column) of git commit `ref`, read from a temporary export."""
    tmp = tempfile.mkdtemp(prefix='crbase')
    subprocess.run('git archive %s data/claims | tar -x -C %s' % (ref, tmp), shell=True, check=True, cwd=common.ROOT)
    rows = []
    for dp, _d, fs in os.walk(os.path.join(tmp, 'data', 'claims')):
        for fn in fs:
            rows.extend(common.read_dicts(os.path.join(dp, fn))[1])
    return rows


def git_file(ref, path):
    return subprocess.run(['git', 'show', '%s:%s' % (ref, path)], capture_output=True, check=True, cwd=common.ROOT).stdout


def verify(ref):
    old = {r['claim_id']: r for r in git_claims(ref)}
    cr.load(force=True)
    rel = cr.load()
    same_text = same_sem = diff = 0
    order_only, bad = [], []
    for cid, r in sorted(old.items()):
        new_text = rel.entries_json(cid)
        if new_text == r['command_relationships']:
            same_text += 1
        elif json.loads(new_text) == json.loads(r['command_relationships']) or \
                [sorted(e.items()) for e in json.loads(new_text)] == [sorted(e.items()) for e in json.loads(r['command_relationships'])]:
            same_sem += 1
            order_only.append(cid)
        else:
            diff += 1
            bad.append(cid)
    print('claims compared: %d' % len(old))
    print('  old cell rebuilt byte-for-byte: %d' % same_text)
    print('  rebuilt with the same entries in the same order but a different key order inside entries (canonical order): %d' % same_sem)
    print('  rebuilt differently (a real difference): %d %s' % (diff, bad[:20]))
    extra = set(rel.by_claim) - set(old)
    print('  links to claims that do not exist: %d' % len(extra))
    entries_old = sum(len(json.loads(r['command_relationships'])) for r in old.values())
    print('  entries before: %d, link rows now: %d' % (entries_old, len(rel.links)))
    # derived table: the rows that overlap the old window must equal the old build/command_relations.csv rows (old columns only)
    import csv
    import io
    _h, units = common.read_dicts(common.UNITS_CSV)
    units = {u['unit_id']: u for u in units}
    new_rows = [dict(zip(cr.DERIVED_HEADER, r)) for r in cr.derived_rows(rel, units, list(old.values()))]
    lo, hi = WINDOW
    in_window = [r for r in new_rows if r['higher_unit_id'] and (r['valid_to'] or '9999-12-31') >= lo and r['valid_from'] <= hi]
    old_rows = list(csv.DictReader(io.StringIO(git_file(ref, 'build/command_relations.csv').decode('utf-8'))))
    cols = list(old_rows[0].keys())
    key = lambda r: tuple(r[c] for c in cols if c != 'source_claim_ids')   # noqa: E731
    old_by, new_by = {}, {}
    for r in old_rows:
        old_by.setdefault(key(r), []).append(r)
    for r in in_window:
        new_by.setdefault(key(r), []).append(r)
    only_old = [k for k in old_by if k not in new_by]
    only_new = [k for k in new_by if k not in old_by]
    print('derived build/command_relations.csv: old rows %d, new rows overlapping the old window %d' % (len(old_rows), len(in_window)))
    print('  rows only in the old table: %d %s' % (len(only_old), only_old[:3]))
    print('  rows only in the new table: %d %s' % (len(only_new), only_new[:3]))
    ids_same = ids_order = ids_diff = 0
    for k, olds in old_by.items():
        if k in new_by:
            o, n = olds[0]['source_claim_ids'], new_by[k][0]['source_claim_ids']
            if o == n:
                ids_same += 1
            elif sorted(o.split()) == sorted(n.split()):
                ids_order += 1
            else:
                ids_diff += 1
    print('  source_claim_ids: identical %d, same ids in another order %d, different ids %d' % (ids_same, ids_order, ids_diff))
    return diff == 0 and not only_old and not only_new


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--dry-run', action='store_true')
    ap.add_argument('--verify', metavar='REF', help='git ref of the layout before the migration')
    ap.add_argument('--overlaps', action='store_true', help='write data/command_relation_overlaps.csv (documented contradictory overlaps) from the current tables')
    args = ap.parse_args()
    if args.overlaps:
        units = {u['unit_id']: u for u in common.read_dicts(common.UNITS_CSV)[1]}
        rows = cr.default_overlap_rows(cr.load(True).rows, units)
        with open(cr.OVERLAP_CSV, 'wb') as f:
            f.write(common.csv_bytes(cr.OVERLAP_HEADER, [[r[c] for c in cr.OVERLAP_HEADER] for r in rows]))
        print('wrote %d documented overlaps to %s' % (len(rows), cr.OVERLAP_CSV))
        return 0
    if args.verify:
        return 0 if verify(args.verify) else 1
    files = common.claim_files()
    first_header = common.read_rows(files[0])[0]
    if 'command_relationships' not in first_header:
        print('claim files have no command_relationships column: already migrated')
        return 1
    claims, per_file = [], []
    for p in files:
        h, rows = common.read_rows(p)
        d = [dict(zip(h, r)) for r in rows]
        claims.extend(d)
        per_file.append((p, h, rows))
    rel_rows, links, flagged = build(claims)
    print('relations: %d, link rows: %d, flagged undated changes: %s' % (len(rel_rows), len(links), flagged))
    if args.dry_run:
        return 0
    with open(cr.REL_CSV, 'wb') as f:
        f.write(common.csv_bytes(cr.REL_HEADER, [[r[c] for c in cr.REL_HEADER] for r in rel_rows]))
    with open(cr.LINK_CSV, 'wb') as f:
        f.write(common.csv_bytes(cr.LINK_HEADER, [[l[c] for c in cr.LINK_HEADER] for l in links]))
    for p, h, rows in per_file:
        ix = h.index('command_relationships')
        with open(p, 'wb') as f:
            f.write(common.csv_bytes(h[:ix] + h[ix + 1:], [r[:ix] + r[ix + 1:] for r in rows]))
    print('wrote %s, %s and %d claim files without command_relationships' % (cr.REL_CSV, cr.LINK_CSV, len(per_file)))
    return 0


if __name__ == '__main__':
    sys.exit(main())
