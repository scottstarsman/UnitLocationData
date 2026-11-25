#!/usr/bin/env python3
"""Point-in-time order-of-battle trees (Task 2, OB9-OB15).

Usage:
  python scripts/export_oob.py 1944-06-06
      [--time HH:MM] [--root-unit UNIT-ID] [--side Allied|Axis]
      [--domain ground|air|naval]  (repeatable)
      [--operation OP-…] [--include relations|located|both|intersection]
      [--near-days 14] [--include-placeholders|--no-include-placeholders]
      [--format json,csv,markdown] [--out DIR_OR_FILE]

The operational parent is the who_controls.py rule (lowest-echelon active
relation, else lowest-echelon standing, else organic fallback). Every other
covering relation is listed as an additional parent; there is no task-group
nesting exception (OB9, OB10). Open intervals stay possible for at most 90
days after last_listed_date (OB11). Locations are the nearest preferred claim
(ties prefer on or before the date) and are never inherited from a parent HQ
(OB13). Authorized TO&E columns come from the unit's own unit_toe assignment on the date and are never inherited from a parent (TE6, TE14). build.py writes flagship snapshots under build/oob/ on every build
(OB14). Standard library only.
"""
import argparse
import csv
import io
import json
import os
import sys
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import allegiance  # noqa: E402
import common  # noqa: E402
import commanders as commandersmod  # noqa: E402
import toe as toemod  # noqa: E402
import operations  # noqa: E402
import who_controls  # noqa: E402

# Flagship snapshot dates for this release are Western Front events (D-Day through the
# German surrender in the west). They will stay that way until a later release adds
# flagship dates for other theaters; they are not a limit on what the dataset may contain.
FLAGSHIP_DATES = [
    '1944-06-06',  # D-Day / Neptune
    '1944-07-18',  # Goodwood and Atlantic open
    '1944-08-15',  # Dragoon and the breakout week
    '1944-12-16',  # Bulge / Wacht am Rhein
    '1945-03-24',  # Plunder / Varsity
    '1945-05-07',  # eve of the German surrender in the west
]
NEAR_DAYS_DEFAULT = 14
INCLUDE_MODES = ('relations', 'located', 'both', 'intersection')
OOB_DIR = 'oob'

# CSV columns (flat). additional_parents is higher_unit_id:relationship:status, semicolon-separated.
CSV_HEADER = [
    'unit_id', 'unit_name', 'domain', 'nationality', 'side', 'echelon', 'branch', 'record_status',
    'primary_parent_unit_id', 'primary_parent_name', 'primary_relationship', 'primary_relation_status',
    'primary_relation_id', 'primary_relation_why', 'additional_parents', 'handover', 'parent_reason',
    'location_claim_id', 'location_date', 'location_offset_days', 'location_in_window',
    'place_id', 'place_name', 'lat', 'lon', 'location_represents', 'activity_status', 'activity_basis',
    'event_type', 'strength_json',
    'authorized_template_id', 'authorized_template_name', 'authorized_personnel', 'authorized_strength_json',
    'commander_tenure_ids', 'commander_person_ids', 'commander_names', 'commander_roles',
    'sidc', 'standard_identity', 'symbol_side',
]


def is_preferred(row):
    return (row.get('claim_status') or 'preferred') == 'preferred'


def _conf(c):
    try:
        return float(c.get('confidence') or 0)
    except (TypeError, ValueError):
        return 0.0


def nearest_preferred(claims, date, near_days):
    """Closest preferred claim to date. Ties prefer on-or-before, then higher confidence, then claim_id (OB13)."""
    best = None
    best_key = None
    for c in claims:
        if not is_preferred(c) or not c.get('date'):
            continue
        off = _date_off(c['date'], date)  # claim - snapshot; negative = before
        key = (abs(off), 0 if off <= 0 else 1, -_conf(c), c.get('claim_id') or '')
        if best_key is None or key < best_key:
            best, best_key = c, key
    if best is None:
        return None
    off = _date_off(best['date'], date)
    return {
        'location_claim_id': best.get('claim_id') or '',
        'location_date': best['date'],
        'location_offset_days': off,
        'location_in_window': abs(off) <= near_days,
        'place_id': best.get('place_id') or '',
        'place_name': best.get('place_name') or '',
        'lat': best.get('latitude') or '',
        'lon': best.get('longitude') or '',
        'location_represents': best.get('location_represents') or '',
        'activity_status': best.get('activity_status') or '',
        'activity_basis': best.get('activity_basis') or '',
        'event_type': best.get('event_type') or '',
        'strength_json': (best.get('strength_json') or '').strip(),
    }


def _date_off(claim_date, snapshot):
    """claim_date - snapshot as whole days; negative means the claim is before the snapshot."""
    import datetime
    return (datetime.date.fromisoformat(claim_date) - datetime.date.fromisoformat(snapshot)).days


class Context:
    """Indexed relations, units, claims, commanders, symbols and sides, built once per export or build."""

    def __init__(self, nonorg_rows, organic_rows, overrides, units, claims, tenures, people, symbols, resolver,
                 operation_unit_pairs=None):
        self.nonorg = defaultdict(list)
        for r in nonorg_rows:
            self.nonorg[r['subject_unit_id']].append(r)
        self.organic = defaultdict(list)
        for r in organic_rows:
            self.organic[r['subject_unit_id']].append(r)
        self.overrides = overrides or {}
        self.units = units
        self.ech = {u: (units[u].get('echelon') or 'other') for u in units}
        self.claims = defaultdict(list)
        for c in claims:
            self.claims[c['unit_id']].append(c)
        self.tenures = defaultdict(list)
        for t in tenures or []:
            if (t.get('status') or 'preferred') == 'preferred':
                self.tenures[t['unit_id']].append(t)
        self.people = {p['person_id']: p for p in (people or [])}
        self.symbols = defaultdict(list)
        for s in symbols or []:
            self.symbols[s['unit_id']].append(s)
        self.resolver = resolver
        self.operation_units = operation_unit_pairs or set()
        self.templates = {t['template_id']: t for t in (toemod.load_templates()[1] or [])}
        self.assignments = defaultdict(list)
        for a in (toemod.load_assignments()[1] or []):
            self.assignments[a['unit_id']].append(a)

    @classmethod
    def from_build_dir(cls):
        """CLI path: read the current build/ tables (run build.py first)."""
        def load(rel):
            p = os.path.join(common.BUILD_DIR, rel)
            return common.read_dicts(p)[1] if os.path.isfile(p) else []
        nonorg = load('command_relations.csv')
        organic = load('organic_relations.csv')
        ov_rows = load('who_controls_overrides.csv')
        overrides = {o['relation_id']: o for o in ov_rows}
        units = {u['unit_id']: u for u in common.read_dicts(common.UNITS_CSV)[1]}
        _h, claims = common.load_all_claims()
        people = commandersmod.load_people()[1] or []
        tenures = commandersmod.load_tenures()[1] or []
        symbols = load('unit_symbols.csv')
        resolver = allegiance.Resolver.load()
        pairs = set()
        ou = load('operation_units.csv')
        for r in ou:
            pairs.add((r['operation_id'], r['unit_id']))
        return cls(nonorg, organic, overrides, units, claims, tenures, people, symbols, resolver, pairs)


def _hits(rows, uid, date, time, overrides):
    """Covering non-placeholder relations for one subject, honouring defer_to_organic_parent overrides."""
    hits, set_aside, holes = [], [], []
    for r in rows:
        st, why = who_controls.status(r, date, time)
        if st == 'no':
            continue
        if not r.get('higher_unit_id'):
            holes.append((r, st, why))
            continue
        ov = overrides.get(r['relation_id'])
        if ov and ov.get('effect') == 'defer_to_organic_parent':
            set_aside.append((r, st, why))
            continue
        hits.append((r, st, why))
    return hits, set_aside, holes


def pick_primary(hits, fallback_hits, ech):
    """who_controls operational parent: lowest-echelon ACTIVE, else STANDING, else organic fallback.

    When two parents of the same winning class cover the date and none is certain (a handover
    with no recorded hour), return ambiguous=True and no pick (OB9: do not guess).
    """
    if hits:
        pool = [h for h in hits if h[0]['relationship'] in who_controls.ACTIVE] or [
            h for h in hits if h[0]['relationship'] in who_controls.STANDING]
        fallback = False
    else:
        pool = list(fallback_hits)
        fallback = bool(pool)
    if not pool:
        return None, fallback, []
    low = min(who_controls.RANK.get(ech.get(h[0]['higher_unit_id'], 'other'), 8) for h in pool)
    pool = [h for h in pool if who_controls.RANK.get(ech.get(h[0]['higher_unit_id'], 'other'), 8) == low]
    ids = sorted({h[0]['higher_unit_id'] for h in pool})
    sure = [i for i in ids if any(h[0]['higher_unit_id'] == i and h[1] == 'yes' for h in pool)]
    if len(ids) > 1 and not sure:
        return None, fallback, ids
    pick_id = sure[0] if sure else ids[0]
    hit = sorted((h for h in pool if h[0]['higher_unit_id'] == pick_id),
                 key=lambda h: (h[1] != 'yes', h[0].get('relation_id') or ''))[0]
    return hit, fallback, []


def parents_on(ctx, uid, date, time=''):
    """Primary parent plus additional covering relations for one unit on date."""
    hits, set_aside, holes = _hits(ctx.nonorg.get(uid, []), uid, date, time, ctx.overrides)
    fallback_hits, _, _ = _hits(ctx.organic.get(uid, []), uid, date, time, {})
    # organic fallback only when no non-organic relation covers the date
    use_fallback = not hits
    pick, is_fb, ambiguous = pick_primary(hits, fallback_hits if use_fallback else [], ctx.ech)
    additional = []
    primary_id = pick[0]['higher_unit_id'] if pick else None
    for h in hits:
        if pick and h[0]['relation_id'] == pick[0]['relation_id']:
            continue
        additional.append(_parent_rec(h, organic_fallback=False))
    if not is_fb:
        for h in fallback_hits:
            additional.append(_parent_rec(h, organic_fallback=True))
    # on a handover, every candidate is an additional parent and there is no primary
    if ambiguous:
        for h in (hits or fallback_hits):
            if h[0]['higher_unit_id'] in ambiguous:
                rec = _parent_rec(h, organic_fallback=is_fb)
                if rec not in additional and (not pick or rec['relation_id'] != (pick[0].get('relation_id') if pick else '')):
                    additional.append(rec)
    additional.sort(key=lambda r: (r['higher_unit_id'], r['relationship'], r['relation_id']))
    if pick:
        rel = who_controls.ORGANIC_FALLBACK if is_fb else pick[0]['relationship']
        primary = {
            'primary_parent_unit_id': pick[0]['higher_unit_id'],
            'primary_parent_name': pick[0].get('higher_name') or '',
            'primary_relationship': rel,
            'primary_relation_status': 'certain' if pick[1] == 'yes' else 'possible',
            'primary_relation_id': pick[0].get('relation_id') or '',
            'primary_relation_why': '; '.join(pick[2]) if pick[2] else '',
        }
        covered = True
        handover = False
        parent_reason = ''
    elif ambiguous:
        primary = _empty_primary()
        covered = True
        handover = True
        parent_reason = 'handover_hour_undocumented'
    else:
        primary = _empty_primary()
        covered = bool(hits or (use_fallback and fallback_hits))
        handover = False
        parent_reason = 'no_covering_relation' if not covered else ''
    return {
        **primary,
        'additional_parents': additional,
        'handover': handover,
        'parent_reason': parent_reason,
        'covered': covered,
        'set_aside': [_parent_rec(h, organic_fallback=False) for h in set_aside],
        'unknown_placeholder': bool(holes),
    }


def _empty_primary():
    return dict(primary_parent_unit_id='', primary_parent_name='', primary_relationship='',
                primary_relation_status='', primary_relation_id='', primary_relation_why='')


def _parent_rec(hit, organic_fallback=False):
    r, st, why = hit
    return {
        'higher_unit_id': r.get('higher_unit_id') or '',
        'higher_name': r.get('higher_name') or '',
        'relationship': who_controls.ORGANIC_FALLBACK if organic_fallback else r['relationship'],
        'status': 'certain' if st == 'yes' else 'possible',
        'relation_id': r.get('relation_id') or '',
        'why': '; '.join(why) if why else '',
    }


def _sidc_on(ctx, uid, date):
    rows = ctx.symbols.get(uid) or []
    hit = None
    for s in rows:
        frm, to = s.get('valid_from') or '', s.get('valid_to') or ''
        if frm and date < frm:
            continue
        if to and date > to:
            continue
        if hit is None or (s.get('valid_from') or '') > (hit.get('valid_from') or ''):
            hit = s
    if not hit:
        return '', '', ''
    return hit.get('sidc') or '', hit.get('standard_identity') or '', hit.get('side') or ''


def _toe_on(ctx, uid, date):
    """The unit's own covering TO&E assignment on date. Never inherited from a parent."""
    asg, conflicts = toemod.assignment_on(ctx.assignments, uid, date)
    if conflicts or not asg:
        return {
            'authorized_template_id': '',
            'authorized_template_name': '',
            'authorized_personnel': '',
            'authorized_strength_json': '',
        }
    tmpl = ctx.templates.get(asg['template_id']) or {}
    return {
        'authorized_template_id': asg.get('template_id') or '',
        'authorized_template_name': tmpl.get('template_name') or '',
        'authorized_personnel': toemod.personnel_of(tmpl),
        'authorized_strength_json': tmpl.get('authorized_strength_json') or '',
    }


def _commander_display(cdrs):
    """CSV and markdown columns: every tenure id, each person once (roles merged)."""
    tenure_ids = [c.get('tenure_id') or '' for c in cdrs]
    seen = {}
    order = []
    for c in cdrs:
        pid = c.get('person_id') or ''
        if pid not in seen:
            seen[pid] = {
                'person_id': pid,
                'canonical_name': c.get('canonical_name') or '',
                'roles': [],
            }
            order.append(pid)
        role = c.get('role') or ''
        if role and role not in seen[pid]['roles']:
            seen[pid]['roles'].append(role)
    pids = [seen[pid]['person_id'] for pid in order]
    names = [seen[pid]['canonical_name'] for pid in order]
    roles = [';'.join(seen[pid]['roles']) for pid in order]
    return tenure_ids, pids, names, roles



def _commanders_on(ctx, uid, date):
    out = []
    for t in ctx.tenures.get(uid, []):
        frm, to = t.get('valid_from') or '', t.get('valid_to') or ''
        if frm and date < frm:
            continue
        if to and date > to:
            continue
        p = ctx.people.get(t['person_id']) or {}
        out.append({
            'tenure_id': t['tenure_id'],
            'person_id': t['person_id'],
            'canonical_name': p.get('canonical_name') or '',
            'role': t.get('role') or '',
            'rank': t.get('rank') or '',
        })
    out.sort(key=lambda r: (r['tenure_id'],))
    return out


def _unit_record(ctx, uid, date, time, near_days, parents):
    u = ctx.units.get(uid) or {}
    loc = nearest_preferred(ctx.claims.get(uid, []), date, near_days) or {
        'location_claim_id': '', 'location_date': '', 'location_offset_days': '',
        'location_in_window': False, 'place_id': '', 'place_name': '', 'lat': '', 'lon': '',
        'location_represents': '', 'activity_status': '', 'activity_basis': '', 'event_type': '',
        'strength_json': '',
    }
    cdrs = _commanders_on(ctx, uid, date)
    sidc, ident, sym_side = _sidc_on(ctx, uid, date)
    toe = _toe_on(ctx, uid, date)
    return {
        'unit_id': uid,
        'unit_name': u.get('unit_name') or '',
        'domain': common.unit_domain(u),
        'nationality': u.get('nationality') or '',
        'side': ctx.resolver.side(uid, date) or '',
        'echelon': u.get('echelon') or '',
        'branch': u.get('branch') or '',
        'record_status': u.get('record_status') or '',
        'primary_parent_unit_id': parents['primary_parent_unit_id'],
        'primary_parent_name': parents['primary_parent_name'],
        'primary_relationship': parents['primary_relationship'],
        'primary_relation_status': parents['primary_relation_status'],
        'primary_relation_id': parents['primary_relation_id'],
        'primary_relation_why': parents['primary_relation_why'],
        'additional_parents': parents['additional_parents'],
        'handover': parents['handover'],
        'parent_reason': parents['parent_reason'],
        **loc,
        **toe,
        'commanders': cdrs,
        'sidc': sidc,
        'standard_identity': ident,
        'symbol_side': sym_side,
    }


def included_unit_ids(ctx, date, time, include, near_days, domains, side, operation, include_placeholders, include_out_of_scope):
    """The set of unit_ids that belong in this snapshot (OB12, OB15)."""
    # relation coverage and location window, evaluated for every in-scope (or opted-in) unit
    candidates = []
    for uid, u in ctx.units.items():
        if not include_out_of_scope and common.unit_scope(u) == 'out_of_scope':
            continue
        if not include_placeholders and (u.get('record_status') or '') == 'placeholder':
            continue
        if domains and common.unit_domain(u) not in domains:
            continue
        candidates.append(uid)

    covered, located = set(), set()
    parent_cache = {}
    for uid in candidates:
        pars = parents_on(ctx, uid, date, time)
        parent_cache[uid] = pars
        if pars['covered']:
            covered.add(uid)
        loc = nearest_preferred(ctx.claims.get(uid, []), date, near_days)
        if loc and loc['location_in_window']:
            located.add(uid)

    if include == 'relations':
        chosen = set(covered)
    elif include == 'located':
        chosen = set(located)
    elif include == 'both':
        chosen = covered | located
    elif include == 'intersection':
        chosen = covered & located
    else:
        raise ValueError('unknown include mode %r' % include)

    if side:
        chosen = {uid for uid in chosen if (ctx.resolver.side(uid, date) or '') == side}
    if operation:
        # ancestors and the operation itself: a unit that appears on a descendant is in operation_units for the ancestor too
        allowed = {uid for (oid, uid) in ctx.operation_units if oid == operation}
        # also include descendants of the named operation (operation_units already has rolled rows on the ancestor)
        chosen = {uid for uid in chosen if uid in allowed}

    # located-only units (no covering relation) keep parent_reason=no_covering_relation
    return chosen, parent_cache


def _subtree(chosen, root, parent_cache):
    """root plus units whose primary-parent chain leads to root, staying inside chosen."""
    children = defaultdict(list)
    for uid in chosen:
        p = (parent_cache.get(uid) or {}).get('primary_parent_unit_id') or ''
        if p and p in chosen and p != uid:
            children[p].append(uid)
    keep = set()
    stack = [root]
    while stack:
        cur = stack.pop()
        if cur in keep:
            continue
        keep.add(cur)
        stack.extend(children.get(cur, []))
    return keep


def build_snapshot(ctx, date, time='', include='relations', near_days=NEAR_DAYS_DEFAULT,
                   domains=None, side=None, root_unit=None, operation=None,
                   include_placeholders=True, include_out_of_scope=False):
    """Return {meta, units (flat, sorted), trees (forest of nested nodes)}."""
    domains = list(domains) if domains else None
    chosen, parent_cache = included_unit_ids(
        ctx, date, time, include, near_days, domains, side, operation,
        include_placeholders, include_out_of_scope)
    if root_unit:
        if root_unit not in ctx.units:
            raise SystemExit('unknown --root-unit %s' % root_unit)
        if root_unit not in chosen:
            # still emit the requested root so a subtree query is not empty just because
            # the headquarters has no covering relation of its own
            chosen.add(root_unit)
            parent_cache[root_unit] = parents_on(ctx, root_unit, date, time)
        chosen = _subtree(chosen, root_unit, parent_cache)
        # drop units not under this root
    records = []
    for uid in chosen:
        rec = _unit_record(ctx, uid, date, time, near_days, parent_cache[uid])
        if rec['parent_reason'] == '' and include in ('located', 'both') and uid not in (
                {i for i, p in parent_cache.items() if p.get('covered')} ):
            rec['parent_reason'] = 'no_covering_relation'
        records.append(rec)
    records.sort(key=lambda r: r['unit_id'])
    trees = _forest(records)
    meta = {
        'date': date,
        'time': time or '',
        'include': include,
        'near_days': near_days,
        'domains': domains or ['ground', 'air', 'naval'],
        'side': side or '',
        'root_unit': root_unit or '',
        'operation': operation or '',
        'include_placeholders': include_placeholders,
        'n_units': len(records),
        'n_roots': len(trees),
        'n_by_domain': _count(records, 'domain'),
        'n_by_side': _count(records, 'side'),
    }
    return {'meta': meta, 'units': records, 'trees': trees}


def _count(records, key):
    out = {}
    for r in records:
        out[r.get(key) or '(blank)'] = out.get(r.get(key) or '(blank)', 0) + 1
    return out


def _forest(records):
    by_id = {r['unit_id']: r for r in records}
    children = defaultdict(list)
    roots = []
    for r in records:
        p = r['primary_parent_unit_id']
        if p and p in by_id and p != r['unit_id']:
            children[p].append(r['unit_id'])
        else:
            roots.append(r['unit_id'])
    visited = set()

    def node(uid):
        visited.add(uid)
        rec = dict(by_id[uid])
        kids = []
        for cid in sorted(children.get(uid, [])):
            if cid in visited:
                continue
            kids.append(node(cid))
        rec['children'] = kids
        return rec

    trees = [node(uid) for uid in sorted(roots)]
    leftover = [uid for uid in sorted(by_id) if uid not in visited]
    for uid in leftover:
        by_id[uid]['parent_reason'] = by_id[uid]['parent_reason'] or 'cycle'
        trees.append(node(uid))
    return trees


def snapshot_json(snap):
    return (json.dumps({'meta': snap['meta'], 'trees': snap['trees']}, ensure_ascii=False, indent=1) + '\n').encode('utf-8')


def snapshot_csv(snap):
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator='\n')
    w.writerow(CSV_HEADER)
    for r in snap['units']:
        w.writerow(_csv_row(r))
    return buf.getvalue().encode('utf-8')


def _csv_row(r):
    add = ';'.join('%s:%s:%s' % (p['higher_unit_id'], p['relationship'], p['status'])
                   for p in r.get('additional_parents') or [])
    cdrs = r.get('commanders') or []
    loc_off = r.get('location_offset_days')
    loc_win = r.get('location_in_window')
    cdr_tenures, cdr_pids, cdr_names, cdr_roles = _commander_display(cdrs)
    return [
        r['unit_id'], r['unit_name'], r['domain'], r['nationality'], r['side'], r['echelon'], r['branch'], r['record_status'],
        r['primary_parent_unit_id'], r['primary_parent_name'], r['primary_relationship'], r['primary_relation_status'],
        r['primary_relation_id'], r['primary_relation_why'], add,
        'true' if r.get('handover') else 'false', r.get('parent_reason') or '',
        r.get('location_claim_id') or '', r.get('location_date') or '',
        '' if loc_off == '' or loc_off is None else str(loc_off),
        'true' if loc_win else 'false',
        r.get('place_id') or '', r.get('place_name') or '', r.get('lat') or '', r.get('lon') or '',
        r.get('location_represents') or '', r.get('activity_status') or '', r.get('activity_basis') or '',
        r.get('event_type') or '', r.get('strength_json') or '',
        r.get('authorized_template_id') or '', r.get('authorized_template_name') or '',
        r.get('authorized_personnel') or '', r.get('authorized_strength_json') or '',
        ';'.join(cdr_tenures),
        ';'.join(cdr_pids),
        ';'.join(cdr_names),
        ';'.join(cdr_roles),
        r.get('sidc') or '', r.get('standard_identity') or '', r.get('symbol_side') or '',
    ]


def snapshot_markdown(snap, title=None):
    """Indented tree. Used for the ground-only flagship page."""
    meta = snap['meta']
    lines = []
    lines.append('# Order of battle, %s' % meta['date'])
    if title:
        lines.append('')
        lines.append(title)
    lines.append('')
    lines.append('Inclusion: `%s`. Near window: %d days. Placeholders included: %s. Units: %d. Roots: %d.'
                 % (meta['include'], meta['near_days'], 'yes' if meta['include_placeholders'] else 'no',
                    meta['n_units'], meta['n_roots']))
    lines.append('')
    lines.append('The primary parent follows `scripts/who_controls.py`. Additional parents (for example a ship assigned to both a flotilla and a task group) are listed in parentheses. A `possible` link is an open interval carried at most 90 days past its last listing, or a ranged/undated start or end; it is not a new sourced end date.')
    lines.append('')

    def walk(node, depth):
        pad = '  ' * depth
        rel = node['primary_relationship'] or 'no parent'
        st = node['primary_relation_status']
        rel_s = rel if not st else '%s, %s' % (rel, st)
        add = node.get('additional_parents') or []
        add_s = ''
        if add:
            add_s = ' (also ' + '; '.join('%s %s (%s)' % (p['relationship'], p['higher_name'] or p['higher_unit_id'], p['status']) for p in add) + ')'
        cdrs = node.get('commanders') or []
        cdr_s = ''
        if cdrs:
            _t, _pids, _names, _roles = _commander_display(cdrs)
            parts = []
            for name, pid, role_s in zip(_names, _pids, _roles):
                label = name or pid
                role_list = [x for x in role_s.split(';') if x]
                if role_list and role_list != ['commander']:
                    label += ' (%s)' % ', '.join(role_list)
                parts.append(label)
            cdr_s = ' Cdr: ' + '; '.join(parts) + '.'
        loc = ''
        if node.get('place_name') or node.get('location_claim_id'):
            off = node.get('location_offset_days')
            off_s = 'offset %+d days' % off if off not in ('', None) else 'no offset'
            loc = ' At %s (%s).' % (node.get('place_name') or node.get('place_id') or node.get('location_claim_id'), off_s)
        auth = ''
        if node.get('authorized_personnel') or node.get('authorized_template_name'):
            who = node.get('authorized_template_name') or node.get('authorized_template_id') or 'TO&E'
            if node.get('authorized_personnel'):
                auth = ' Authorized: %s (%s).' % (node['authorized_personnel'], who)
            else:
                auth = ' Authorized: %s.' % who
        lines.append('%s- **%s** (`%s`) — %s%s.%s%s%s' % (
            pad, node['unit_name'] or node['unit_id'], node['unit_id'], rel_s, add_s, cdr_s, loc, auth))
        for ch in node.get('children') or []:
            walk(ch, depth + 1)

    for t in snap['trees']:
        walk(t, 0)
        lines.append('')
    return ('\n'.join(lines).rstrip() + '\n').encode('utf-8')


def flagship_readme():
    text = '''# Flagship order-of-battle snapshots

These files are generated by `scripts/export_oob.py` on every `scripts/build.py` run. Do not hand-edit them. To rebuild one date, or a different date, filter, or format, run the script directly (see `docs/oob_exports.md`).

## Dates

- `1944-06-06` — D-Day / Operation Neptune. Dense same-day air and naval locations.
- `1944-07-18` — Opening of Operations Goodwood and Atlantic.
- `1944-08-15` — Operation Dragoon and the breakout / Falaise week.
- `1944-12-16` — Opening of the Battle of the Bulge / Operation Wacht am Rhein.
- `1945-03-24` — Operations Plunder and Varsity.
- `1945-05-07` — Eve of the German surrender in the west.

## Files per date

- `YYYY-MM-DD.json` and `YYYY-MM-DD.csv` — every unit whose command relation covers the date (all domains, `--include relations`). A `possible` parent is an open interval carried at most 90 days past its last listing, not a sourced end date.
- `YYYY-MM-DD-ground.md` — the same include mode, ground units only, as a readable tree.
- `YYYY-MM-DD-located.csv` — units that both have a covering relation and a preferred location claim within 14 days (`--include intersection`). The safer file to plot, because it drops 90-day-stale air and naval pins.

## How to read a tree

The primary parent is the `who_controls.py` answer: the lowest-echelon `operational_control` or `attached` holder, otherwise the lowest-echelon `assigned` or `unspecified_subordination` holder, otherwise the organic parent (labelled `organic_fallback`). Other relations that cover the date (including a second `assigned` parent, which is common for D-Day ships that belong to a flotilla and a task group) are listed as additional parents; the task group is not promoted over the flotilla in v1.

A unit's location is its nearest preferred claim to the snapshot date (ties prefer a claim on or before the date). It is never inherited from a parent headquarters.

Authorized strength (`authorized_template_id`, `authorized_template_name`, `authorized_personnel`, `authorized_strength_json`) comes from that unit's own `data/unit_toe.csv` assignment covering the date. It is kept separate from `strength_json` (a sourced actual or estimated figure on a claim) and is never inherited from a parent.

Late-war snapshots (from mid-December 1944) have few air and naval units because most of those relations were last listed in June 1944 and the 90-day reading cutoff has expired. That is a coverage gap in the relations, not a reason to lengthen the window.
'''
    return text.encode('utf-8')


def flagship_outputs(ctx):
    """{path relative to build/: bytes} for the six flagship dates (OB14)."""
    out = {('%s/README.md' % OOB_DIR): flagship_readme()}
    for date in FLAGSHIP_DATES:
        full = build_snapshot(ctx, date, include='relations', near_days=NEAR_DAYS_DEFAULT, include_placeholders=True)
        out['%s/%s.json' % (OOB_DIR, date)] = snapshot_json(full)
        out['%s/%s.csv' % (OOB_DIR, date)] = snapshot_csv(full)
        ground = build_snapshot(ctx, date, include='relations', near_days=NEAR_DAYS_DEFAULT,
                                domains=['ground'], include_placeholders=True)
        out['%s/%s-ground.md' % (OOB_DIR, date)] = snapshot_markdown(
            ground, title='Ground units only. The all-domain picture is in the JSON and CSV files of the same date.')
        located = build_snapshot(ctx, date, include='intersection', near_days=NEAR_DAYS_DEFAULT, include_placeholders=True)
        out['%s/%s-located.csv' % (OOB_DIR, date)] = snapshot_csv(located)
    return out


def context_from_build_outputs(nonorg_rows, organic_rows, override_rows, units, claims, tenures, people, symbols, operation_unit_rows=None):
    """Used by scripts/build.py so flagship files are generated from the in-memory derived tables of this run."""
    overrides = {o['relation_id']: o for o in (override_rows or [])}
    resolver = allegiance.Resolver(units, common.load_nationalities(), allegiance.load()[1], allegiance.load_overrides()[1])
    pairs = set()
    for r in operation_unit_rows or []:
        if isinstance(r, dict):
            pairs.add((r['operation_id'], r['unit_id']))
        else:
            pairs.add((r[0], r[1]))
    return Context(nonorg_rows, organic_rows, overrides, units, claims, tenures, people, symbols, resolver, pairs)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('date', help='Snapshot date, YYYY-MM-DD')
    ap.add_argument('--time', default='', help='Optional HH:MM (24-hour), passed to who_controls.status')
    ap.add_argument('--root-unit', dest='root_unit', default='', help='Restrict the tree to this unit and its descendants')
    ap.add_argument('--side', default='', choices=['', 'Allied', 'Axis', 'Neutral'])
    ap.add_argument('--domain', action='append', dest='domains', default=[], choices=['ground', 'air', 'naval'],
                    help='Repeatable. Default: all domains')
    ap.add_argument('--operation', default='', help='Restrict to units in build/operation_units.csv for this operation_id')
    ap.add_argument('--include', default='relations', choices=list(INCLUDE_MODES))
    ap.add_argument('--near-days', dest='near_days', type=int, default=NEAR_DAYS_DEFAULT)
    ap.add_argument('--include-placeholders', dest='include_placeholders', action='store_true', default=True)
    ap.add_argument('--no-include-placeholders', dest='include_placeholders', action='store_false')
    ap.add_argument('--include-out-of-scope', dest='include_out_of_scope', action='store_true', default=False)
    ap.add_argument('--format', default='json', help='Comma-separated: json, csv, markdown')
    ap.add_argument('--out', default='', help='Output directory, or a single file if only one format is requested')
    args = ap.parse_args(argv)
    ctx = Context.from_build_dir()
    snap = build_snapshot(
        ctx, args.date, time=args.time, include=args.include, near_days=args.near_days,
        domains=args.domains or None, side=args.side or None, root_unit=args.root_unit or None,
        operation=args.operation or None, include_placeholders=args.include_placeholders,
        include_out_of_scope=args.include_out_of_scope)
    formats = [f.strip().lower() for f in args.format.split(',') if f.strip()]
    writers = {'json': snapshot_json, 'csv': snapshot_csv, 'markdown': snapshot_markdown}
    for fmt in formats:
        if fmt not in writers:
            raise SystemExit('unknown format %r (json, csv, markdown)' % fmt)
    if not args.out:
        # write to stdout when a single format is asked for
        if len(formats) != 1:
            raise SystemExit('pass --out DIR when writing more than one format')
        sys.stdout.buffer.write(writers[formats[0]](snap))
        return 0
    out = args.out
    if len(formats) == 1 and not os.path.isdir(out) and not out.endswith(os.sep):
        os.makedirs(os.path.dirname(os.path.abspath(out)) or '.', exist_ok=True)
        with open(out, 'wb') as f:
            f.write(writers[formats[0]](snap))
        print('wrote', out, '(%d units)' % snap['meta']['n_units'])
        return 0
    os.makedirs(out, exist_ok=True)
    ext = {'json': '.json', 'csv': '.csv', 'markdown': '.md'}
    for fmt in formats:
        path = os.path.join(out, args.date + ext[fmt])
        with open(path, 'wb') as f:
            f.write(writers[fmt](snap))
        print('wrote', path)
    print('%d units, %d roots' % (snap['meta']['n_units'], snap['meta']['n_roots']))
    return 0


if __name__ == '__main__':
    sys.exit(main())
