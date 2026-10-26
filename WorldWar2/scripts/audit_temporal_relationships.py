#!/usr/bin/env python3
"""Cross-claim temporal audit of command relationships, rows and event types. Read-only: it never edits data and always exits 0.

Usage: python scripts/audit_temporal_relationships.py                 (prints the report)
       python scripts/audit_temporal_relationships.py --out FILE      (writes the report as markdown)

validate.py checks one row at a time; this script reads all claims together and looks for temporal patterns that a single-row
check cannot see. Every finding is a prompt for a human check against the sources, not an error: the report states how many
findings each check made and lists them. The claims' relationship entries are rebuilt from the master tables (data/command_relations.csv,
data/command_relation_claims.csv; see scripts/command_relations.py); checks 10 to 12 read the master table directly. Twelve checks:

 1 overlap            two different headquarters of the same echelon hold operational_control or attached over one subject
                      for more than the boundary day (a change on one day is expected, the day is inclusive on both sides)
 2 parent_in_force    a row's parent_unit_id has no entry on the row, or its entry does not cover the row date
 3 start_disagree     the same (subject, higher, relationship) pair is restated with effective_from dates 2 days or more apart where at
                      least one comes from a narrative, order or inferred date (a table date against a narrative date, or two
                      readings of one order); table-against-table differences are only the table's own row starts and are not listed
 4 relisted_after_end a pair closed by effective_to is listed again by a later row (a closed relationship that came back or an end
                      that was set too early)
 5 parent_change      a unit's parent_unit_id changes between consecutive preferred rows and no entry of either row carries a date in
                      the gap (the change is not dated by the data)
 6 echelon_skip       parent_unit_id is an army or army group while the row lists an active operational_control/attached entry at
                      an intermediate corps or division echelon above the unit
 7 change_undated     a command_change/subordinate_assignment row whose own activity says the unit passes or transfers to a headquarters
                      but no entry carries a date within one day of the row date (commander changes and rows about a headquarters
                      taking over other units are not covered)
 8 same_day_place     one unit has two preferred rows on the same date whose coordinates differ by 25 km or more (a place conflict not
                      in a conflict group)
 9 group_date_spread  a conflict group whose rows are dated more than one day apart AND differ in event_type (a sequence recorded as
                      a conflict; a plain disagreement over one event's date keeps one event_type and is not listed)
10 master_overlap     two preferred relations of one subject that contradict each other (same relationship class, different higher units of
                      one echelon) over more than the boundary day, as documented in data/command_relation_overlaps.csv (validate.py makes
                      sure every such overlap is listed); a one-day overlap is the boundary day
11 end_unknown        an attached/operational_control/reserve/administrative_control relation with no sourced end (end_unknown true in the
                      master table): valid_to is only inferred from the unit's next claim, or still open at its last claim
12 change_flagged     the parent changes whose date no source gives (change_undated true): the change lies between the two dates shown

Standard library only.
"""
import argparse
import datetime
import json
import math
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common  # noqa: E402
import command_relations  # noqa: E402

RANK = common.echelon_rank()                    # schema/vocabularies.json, vocabulary echelon_rank
ACTIVE = common.relationship_group('active')    # schema/vocabularies.json, vocabulary relationship_groups
MAX_LIST = 40


def d(s):
    return datetime.date.fromisoformat(s)


def km(a, b):
    la1, lo1, la2, lo2 = map(math.radians, (a[0], a[1], b[0], b[1]))
    h = math.sin((la2 - la1) / 2) ** 2 + math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2
    return 12742 * math.asin(math.sqrt(h))


def entries(row):
    v = row['command_relationships']
    if v == '':
        return []
    try:
        return [e for e in json.loads(v) if isinstance(e, dict)]
    except ValueError:
        return []


def load():
    _h, rows = common.load_all_claims()
    _uh, units = common.read_dicts(common.UNITS_CSV)
    return rows, {u['unit_id']: u for u in units}


def runs(rows):
    """(subject, higher, relationship) -> list of runs {start, end, ends_explicit, claims}; end = effective_to or the last row listing it."""
    by = {}
    for r in rows:
        if r['claim_status'] not in ('preferred', ''):
            continue
        by.setdefault(r['unit_id'], []).append(r)
    out = []
    for uid, rs in by.items():
        rs.sort(key=lambda r: (r['date'], r['claim_id']))
        cur = {}
        for r in rs:
            keys = set()
            for e in entries(r):
                if not e.get('unit_id') or e['relationship'] == 'organic':
                    continue
                k = (e['unit_id'], e['relationship'])
                keys.add(k)
                start = e.get('effective_from') or r['date']
                if k not in cur:
                    cur[k] = {'subject': uid, 'higher': e['unit_id'], 'rel': e['relationship'], 'start': start, 'end': r['date'],
                              'explicit': False, 'claims': [r['claim_id']], 'name': r['unit_name']}
                else:
                    cur[k]['claims'].append(r['claim_id'])
                    cur[k]['end'] = max(cur[k]['end'], r['date'])
                    cur[k]['start'] = min(cur[k]['start'], start)
                if e.get('effective_to'):
                    cur[k]['end'] = e['effective_to']
                    cur[k]['explicit'] = True
                    out.append(cur.pop(k))
            for k in list(cur):
                if k not in keys and r['date'] > cur[k]['end']:
                    out.append(cur.pop(k))
        out.extend(cur.values())
    return out


def check_overlap(rows, units, rn):
    f = []
    by = {}
    for x in rn:
        if x['rel'] in ACTIVE and x['higher'] in units:
            by.setdefault(x['subject'], []).append(x)
    for sub, xs in by.items():
        for i, a in enumerate(xs):
            for b in xs[i + 1:]:
                if a['higher'] == b['higher']:
                    continue
                if RANK.get(units[a['higher']]['echelon'], 8) != RANK.get(units[b['higher']]['echelon'], 8):
                    continue
                lo, hi = max(a['start'], b['start']), min(a['end'], b['end'])
                if lo <= hi and (d(hi) - d(lo)).days >= 1:
                    f.append((lo, '%s: %s %s (%s..%s, %s) and %s %s (%s..%s, %s) overlap %s..%s' % (
                        sub, a['rel'], a['higher'], a['start'], a['end'], ','.join(a['claims'][:3]), b['rel'], b['higher'], b['start'], b['end'],
                        ','.join(b['claims'][:3]), lo, hi)))
    return f


def check_parent_in_force(rows, units, rn):
    f = []
    for r in rows:
        p = r['parent_unit_id']
        if p == '' or r['claim_status'] not in ('preferred', ''):
            continue
        es = [e for e in entries(r) if e.get('unit_id') == p]
        if not es:
            f.append((r['date'], '%s %s %s: parent %s has no entry' % (r['claim_id'], r['unit_id'], r['date'], p)))
            continue
        e = es[0]
        a, b = e.get('effective_from'), e.get('effective_to')
        if (a and a > r['date']) or (b and b < r['date']):
            f.append((r['date'], '%s %s %s: parent %s entry runs %s..%s and does not cover the row date' % (r['claim_id'], r['unit_id'], r['date'], p, a or '-', b or '-')))
    return f


def check_start_disagree(rows, units, rn):
    """Same pair, different effective_from where at least one is not an assignment-table row start (table rows restate the date
    their own table line begins, so table-against-table differences are a restatement pattern, not a disagreement)."""
    f = []
    starts = {}
    for r in rows:
        if r['claim_status'] not in ('preferred', ''):
            continue
        for e in entries(r):
            if e.get('unit_id') and e.get('effective_from') and e['relationship'] != 'organic':
                cls = 'table' if e.get('date_basis') == 'assignment_table' else 'other'
                starts.setdefault((r['unit_id'], e['unit_id'], e['relationship']), {}).setdefault((e['effective_from'], cls), []).append(r['claim_id'])
    for k, v in starts.items():
        other = sorted(x for x, c in v if c == 'other')
        table = sorted(x for x, c in v if c == 'table')
        hit = (len(other) > 1 and (d(other[-1]) - d(other[0])).days >= 2) or \
              any(abs((d(o) - d(t)).days) >= 2 for o in other for t in table)
        if hit:
            allv = sorted(v)
            f.append((allv[0][0], '%s -> %s %s: effective_from %s' % (k[0], k[1], k[2], '; '.join('%s %s (%s)' % (x, c, ','.join(v[(x, c)][:3])) for x, c in allv))))
    return f


def check_relisted(rows, units, rn):
    f = []
    by = {}
    for x in rn:
        by.setdefault((x['subject'], x['higher'], x['rel']), []).append(x)
    for k, xs in by.items():
        xs.sort(key=lambda x: x['start'])
        for a, b in zip(xs, xs[1:]):
            if a['explicit'] and b['start'] > a['end'] and (d(b['start']) - d(a['end'])).days >= 2:
                f.append((a['end'], '%s -> %s %s: ended %s (%s) and relisted from %s (%s)' % (k[0], k[1], k[2], a['end'], ','.join(a['claims'][:2]), b['start'], ','.join(b['claims'][:2]))))
    return f


def check_parent_change(rows, units, rn):
    f = []
    by = {}
    for r in rows:
        if r['claim_status'] in ('preferred', '') and r['parent_unit_id'] != '':
            by.setdefault(r['unit_id'], []).append(r)
    for uid, rs in by.items():
        rs.sort(key=lambda r: (r['date'], r['claim_id']))
        for a, b in zip(rs, rs[1:]):
            if a['parent_unit_id'] == b['parent_unit_id']:
                continue
            dated = False
            for r in (a, b):
                for e in entries(r):
                    if e.get('unit_id') in (a['parent_unit_id'], b['parent_unit_id']):
                        for k in ('effective_from', 'effective_to', 'ordered_date'):
                            if e.get(k) and a['date'] <= e[k] <= b['date']:
                                dated = True
            if not dated:
                f.append((a['date'], '%s %s: parent %s (%s %s) -> %s (%s %s), no entry dated between' % (
                    uid, a['unit_name'], a['parent_unit_id'], a['claim_id'], a['date'], b['parent_unit_id'], b['claim_id'], b['date'])))
    return f


def check_echelon_skip(rows, units, rn):
    f = []
    for r in rows:
        p = r['parent_unit_id']
        if r['claim_status'] not in ('preferred', '') or p not in units or r['unit_id'] not in units:
            continue
        if RANK.get(units[p]['echelon'], 8) < 6:
            continue
        mine = RANK.get(units[r['unit_id']]['echelon'], 8)
        for e in entries(r):
            u = units.get(e.get('unit_id'))
            if not u or e['relationship'] not in ACTIVE:
                continue
            if mine < RANK.get(u['echelon'], 8) < RANK.get(units[p]['echelon'], 8):
                a, b = e.get('effective_from'), e.get('effective_to')
                if (not a or a <= r['date']) and (not b or b >= r['date']):
                    f.append((r['date'], '%s %s %s: parent %s (%s) but %s %s is active at %s level' % (
                        r['claim_id'], r['unit_id'], r['date'], p, units[p]['echelon'], e['relationship'], e['unit_id'], u['echelon'])))
    return f


def check_change_undated(rows, units, rn):
    """Rows whose own activity says the unit passes or transfers to a headquarters (the subject's own relationship changes) but no
    entry carries a date within a day of the row. Commander changes and rows about a headquarters taking over other units are not
    covered (their relationship change belongs to the other units' rows)."""
    f = []
    for r in rows:
        if r['claim_status'] not in ('preferred', '') or r['event_type'] not in ('command_change', 'subordinate_assignment'):
            continue
        if not re.match(r'(passing|passes|transferring|transfers|transferred)\b', r['current_activity'].strip().lower()):
            continue
        ok = False
        for e in entries(r):
            for k in ('effective_from', 'effective_to', 'ordered_date'):
                if e.get(k) and abs((d(e[k]) - d(r['date'])).days) <= 1:
                    ok = True
        if not ok:
            f.append((r['date'], '%s %s %s: %s ("%s") with no entry dated within a day of the row' % (
                r['claim_id'], r['unit_id'], r['date'], r['event_type'], r['current_activity'][:60])))
    return f


def check_same_day_place(rows, units, rn):
    f = []
    by = {}
    for r in rows:
        if r['claim_status'] in ('preferred', ''):
            by.setdefault(r['unit_id'], []).append(r)
    for uid, rs in by.items():
        rs.sort(key=lambda r: (r['date'], r['claim_id']))
        for a, b in zip(rs, rs[1:]):
            if b['date'] == a['date'] and a['conflict_group_id'] == '' and b['conflict_group_id'] == '':
                try:
                    dist = km((float(a['latitude']), float(a['longitude'])), (float(b['latitude']), float(b['longitude'])))
                except ValueError:
                    continue
                if dist >= 25:
                    f.append((a['date'], '%s: %s (%s, %s) and %s (%s, %s) are %d km apart' % (
                        uid, a['claim_id'], a['date'], a['location_name'], b['claim_id'], b['date'], b['location_name'], dist)))
    return f


def check_group_spread(rows, units, rn):
    f = []
    g = {}
    for r in rows:
        if r['conflict_group_id']:
            g.setdefault(r['conflict_group_id'], []).append(r)
    for gid, rs in sorted(g.items()):
        ds = sorted(r['date'] for r in rs)
        types = sorted({r['event_type'] for r in rs})
        if (d(ds[-1]) - d(ds[0])).days > 1 and len(types) > 1:
            f.append((ds[0], '%s: %s dated %s, event types %s' % (gid, ','.join(r['claim_id'] for r in rs), ' / '.join(ds), ' / '.join(types))))
    return f


def check_master_overlap(rows, units, rn):
    rel = command_relations.load(True)
    f = []
    for o in rel.overlaps:
        if o['overlap_to'] and o['overlap_to'] == o['overlap_from']:
            continue   # the boundary day
        f.append((o['overlap_from'], '%s / %s %s to %s: %s' % (o['relation_id_a'], o['relation_id_b'], o['overlap_from'], o['overlap_to'] or 'open', o['explanation'])))
    return f


def check_end_unknown(rows, units, rn):
    f = []
    for r in command_relations.load(True).rows:
        if r['end_unknown'] == 'true' and r['status'] == 'preferred':
            f.append((r['valid_from'], '%s %s -> %s %s from %s: %s' % (r['relation_id'], r['subject_unit_id'], r['higher_unit_id'], r['relationship'], r['valid_from'],
                      ('end inferred between %s and %s' % (r['valid_to_earliest'], r['valid_to'])) if r['valid_to'] else 'still listed at the unit\'s last claim')))
    return f


def check_change_flagged(rows, units, rn):
    """One finding per undated transition: an outgoing relation (end inferred) followed by an incoming one (start = its first claim), both flagged."""
    f = []
    flagged = sorted((r for r in command_relations.load(True).rows if r['change_undated'] == 'true'),
                     key=lambda r: (r['subject_unit_id'], r['valid_from'], r['relation_id']))
    for a, b in zip(flagged, flagged[1:]):
        if a['subject_unit_id'] == b['subject_unit_id'] and a['valid_to_basis'] == 'inferred_from_next_claim' and b['valid_from_basis'] == 'claim_date' \
                and b['valid_from'] > a['valid_to_earliest']:
            f.append((a['valid_to_earliest'], '%s -> %s (%s / %s): the parent changed from %s to %s some time between %s (last listing) and %s (first listing); no source dates it' % (
                a['subject_unit_id'], b['higher_unit_id'], a['relation_id'], b['relation_id'], a['higher_unit_id'], b['higher_unit_id'], a['valid_to_earliest'], b['valid_from'])))
    return f


CHECKS = [
    ('overlap', 'Two headquarters of one echelon over one subject for more than the boundary day', check_overlap),
    ('parent_in_force', "Row's parent has no entry on the row or its entry does not cover the row date", check_parent_in_force),
    ('start_disagree', 'The same pair restated with effective_from dates two days or more apart, at least one not a table row start', check_start_disagree),
    ('relisted_after_end', 'A pair closed by effective_to is listed again later', check_relisted),
    ('parent_change', 'parent_unit_id changes between consecutive rows and no entry dates the change', check_parent_change),
    ('echelon_skip', 'Parent is an army or army group while an intermediate HQ is active in the row', check_echelon_skip),
    ('change_undated', 'A row whose activity says the unit passes or transfers to a headquarters, with no entry dated within a day', check_change_undated),
    ('same_day_place', 'Two preferred rows of one unit on one date, 25 km or more apart, outside a conflict group', check_same_day_place),
    ('group_date_spread', 'Conflict group more than a day apart whose rows differ in event_type', check_group_spread),
    ('master_overlap', 'Contradictory relations of one subject overlapping by more than the boundary day (documented in data/command_relation_overlaps.csv)', check_master_overlap),
    ('end_unknown', 'Temporary relation with no sourced end (end_unknown true in data/command_relations.csv)', check_end_unknown),
    ('change_flagged', 'Parent change that no source dates (change_undated true in data/command_relations.csv)', check_change_flagged),
]


def run():
    rows, units = load()
    rn = runs(rows)
    return len(rows), [(n, desc, sorted(fn(rows, units, rn))) for n, desc, fn in CHECKS]


def render(nrows, results):
    out = ['# Temporal audit of command relationships', '',
           'Generated by `scripts/audit_temporal_relationships.py` (read-only) over %d claims. Every finding is a prompt for a check against the sources, not an error.' % nrows, '',
           '| check | findings | what it looks for |', '|---|---:|---|']
    for n, desc, fs in results:
        out.append('| `%s` | %d | %s |' % (n, len(fs), desc))
    for n, desc, fs in results:
        out += ['', '## %s (%d)' % (n, len(fs)), '', desc + '.', '']
        for _k, line in fs[:MAX_LIST]:
            out.append('- ' + line)
        if len(fs) > MAX_LIST:
            out.append('- ... %d more (run the script to list them)' % (len(fs) - MAX_LIST))
        if not fs:
            out.append('- none')
    return '\n'.join(out) + '\n'


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--out', help='write the markdown report to this file instead of printing it')
    ap.add_argument('--full', action='store_true', help='list every finding (no per-check cap)')
    args = ap.parse_args(argv)
    global MAX_LIST
    if args.full:
        MAX_LIST = 10 ** 9
    nrows, results = run()
    text = render(nrows, results)
    if args.out:
        with open(args.out, 'w', encoding='utf-8') as fh:
            fh.write(text)
        print('wrote %s: %s' % (args.out, ', '.join('%s %d' % (n, len(fs)) for n, _d, fs in results)))
    else:
        sys.stdout.write(text)
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
