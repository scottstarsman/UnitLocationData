#!/usr/bin/env python3
"""Derived unit participation in operations (Task 2, OB7, OB8).

build/operation_units.csv has one row per (operation_id, unit_id) that has at least one claim or
mission whose operation_id is this operation or a descendant, and whose date falls in that operation's start_date..end_date window (a blank bound is open; an undated claim or mission still counts). Participation is never rolled up
the command hierarchy. most_specific_op_type records the most specific op_type among the unit's
tags in this chain so campaign-default tags stay distinguishable from a named battle. Standard library only.

Commanders: preferred tenures that overlap the operation window are listed.
commander_tenure_ids keeps every matching tenure; commander_person_ids and
commander_names list each person once (first tenure in valid_from, tenure_id
order). Same-person role overlaps (acting then confirmed commander, and similar)
are allowed by schema CM5 and are not closed automatically.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import allegiance  # noqa: E402
import common  # noqa: E402
import commanders as commandersmod  # noqa: E402

BUILD_HEADER = [
    'operation_id', 'unit_id', 'unit_name', 'domain', 'nationality', 'side', 'side_note',
    'echelon', 'branch', 'record_status',
    'participation_scope', 'most_specific_op_type',
    'claims_direct', 'claims_direct_preferred',
    'claims_including_children', 'claims_including_children_preferred',
    'missions_direct', 'missions_including_children',
    'first_date', 'last_date',
    'commander_tenure_ids', 'commander_person_ids', 'commander_names',
]

OP_TYPE_RANK = {'battle': 0, 'phase': 1, 'operation': 2, 'campaign': 3, 'umbrella': 4}
DOMAIN_RANK = {'ground': 0, 'air': 1, 'naval': 2}


def is_preferred(row):
    return (row.get('claim_status') or 'preferred') == 'preferred'


def _most_specific(types):
    if not types:
        return ''
    return min(types, key=lambda t: OP_TYPE_RANK.get(t, 99))


def _in_window(date, start, end):
    """True if date is inside [start, end] (inclusive). A blank bound is open; a blank date counts."""
    if not date:
        return True
    if start and date < start:
        return False
    if end and date > end:
        return False
    return True



def _unique_people(tenures_and_names):
    """Keep every tenure id; list each person_id and name once, first seen wins.

    tenures_and_names is a list of (tenure_id, person_id, name).
    """
    c_ids, p_ids, names = [], [], []
    seen = set()
    for tid, pid, name in tenures_and_names:
        c_ids.append(tid)
        if pid in seen:
            continue
        if pid:
            seen.add(pid)
        p_ids.append(pid)
        names.append(name)
    return c_ids, p_ids, names



def _overlaps(from_s, to_s, start, end):
    """True if [from_s, to_s] (blank to_s = open) overlaps inclusive [start, end]."""
    if not from_s or not start or not end:
        return False
    if from_s > end:
        return False
    if to_s and to_s < start:
        return False
    return True


def _side_note(resolver, unit_id, start, end, side0):
    """If the unit's side changes inside the operation window, say so; otherwise blank."""
    if not start or not end or start == end:
        return ''
    # check the end date; mid-span changes are rare and this catches a change by the close
    side1 = resolver.side(unit_id, end)
    if side1 and side0 and side1 != side0:
        return 'side on start_date is %s, on end_date is %s' % (side0, side1)
    return ''


def operation_unit_rows(ops, claims, missions, units, people=None, tenures=None, resolver=None):
    """List-of-lists rows for build/operation_units.csv, sorted by operation_id, domain, unit_id."""
    if resolver is None:
        resolver = allegiance.Resolver.load()
    if people is None:
        people = {r['person_id']: r for r in commandersmod.load_people()[1] or []}
    else:
        people = {r['person_id']: r for r in people} if people and not isinstance(people, dict) else (people or {})
    if tenures is None:
        tenures = commandersmod.load_tenures()[1] or []
    preferred_tenures = [t for t in tenures if (t.get('status') or 'preferred') == 'preferred']
    tenures_by_unit = {}
    for t in preferred_tenures:
        tenures_by_unit.setdefault(t['unit_id'], []).append(t)

    # ancestors including self, for each operation
    chain_ids = {o['operation_id']: [c['operation_id'] for c in ops.chain(o['operation_id'])] for o in ops.rows}
    typ_of = {o['operation_id']: o['op_type'] for o in ops.rows}

    # (operation_id, unit_id) -> accumulator
    acc = {}

    def bucket(oid, uid):
        k = (oid, uid)
        if k not in acc:
            acc[k] = {
                'direct': 0, 'direct_pref': 0, 'rolled': 0, 'rolled_pref': 0,
                'missions_direct': 0, 'missions_rolled': 0,
                'dates': [], 'direct_flag': False, 'types': set(),
            }
        return acc[k]

    for c in claims:
        oid = c.get('operation_id') or ''
        uid = c.get('unit_id') or ''
        if oid not in chain_ids or not uid:
            continue
        pref = is_preferred(c)
        typ = typ_of.get(oid, '')
        for anc in chain_ids[oid]:
            op_anc = ops.by_id.get(anc) or {}
            if not _in_window(c.get('date') or '', op_anc.get('start_date') or '', op_anc.get('end_date') or ''):
                continue
            b = bucket(anc, uid)
            b['rolled'] += 1
            if pref:
                b['rolled_pref'] += 1
            if c.get('date'):
                b['dates'].append(c['date'])
            if typ:
                b['types'].add(typ)
            if anc == oid:
                b['direct'] += 1
                if pref:
                    b['direct_pref'] += 1
                b['direct_flag'] = True

    for m in missions or []:
        oid = (m.get('operation_id') or '').strip()
        uid = m.get('unit_id') or ''
        if oid not in chain_ids or not uid:
            continue
        typ = typ_of.get(oid, '')
        for anc in chain_ids[oid]:
            op_anc = ops.by_id.get(anc) or {}
            if not _in_window(m.get('date') or '', op_anc.get('start_date') or '', op_anc.get('end_date') or ''):
                continue
            b = bucket(anc, uid)
            b['missions_rolled'] += 1
            if m.get('date'):
                b['dates'].append(m['date'])
            if typ:
                b['types'].add(typ)
            if anc == oid:
                b['missions_direct'] += 1
                b['direct_flag'] = True

    rows = []
    for (oid, uid), b in acc.items():
        u = units.get(uid) or {}
        domain = common.unit_domain(u)
        op = ops.by_id.get(oid) or {}
        start, end = op.get('start_date') or '', op.get('end_date') or ''
        side = resolver.side(uid, start) if start else resolver.side(uid, (sorted(b['dates']) or [''])[0])
        side_s = side or ''
        note = _side_note(resolver, uid, start, end, side)
        dates = sorted(d for d in b['dates'] if d)
        # commanders whose preferred tenure overlaps the operation window
        covering = []
        for t in sorted(tenures_by_unit.get(uid, []), key=lambda r: (r.get('valid_from') or '', r.get('tenure_id') or '')):
            if _overlaps(t.get('valid_from') or '', t.get('valid_to') or '', start, end):
                covering.append((
                    t['tenure_id'],
                    t['person_id'],
                    (people.get(t['person_id']) or {}).get('canonical_name') or '',
                ))
        c_ids, p_ids, names = _unique_people(covering)
        rows.append([
            oid, uid, u.get('unit_name') or '', domain, u.get('nationality') or '', side_s, note,
            u.get('echelon') or '', u.get('branch') or '', u.get('record_status') or '',
            'direct' if b['direct_flag'] else 'rolled_only',
            _most_specific(b['types']),
            str(b['direct']), str(b['direct_pref']),
            str(b['rolled']), str(b['rolled_pref']),
            str(b['missions_direct']), str(b['missions_rolled']),
            dates[0] if dates else '', dates[-1] if dates else '',
            ';'.join(c_ids), ';'.join(p_ids), ';'.join(names),
        ])
    rows.sort(key=lambda r: (r[0], DOMAIN_RANK.get(r[3], 9), r[1]))
    return rows
