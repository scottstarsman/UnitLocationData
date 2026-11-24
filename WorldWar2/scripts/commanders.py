"""People and unit-commander tenures (data/people.csv, data/unit_commanders.csv,
data/unit_commander_claims.csv).

load_*() read the tables; check(...) returns a list of (where, message) problems
for scripts/validate.py; attach_person_ids(rows) fills commander_person_id on
claim dicts; derived_people / derived_tenures build the unified build/ exports.
"""
import csv
import datetime
import os
import re

import common

PEOPLE_CSV = os.path.join(common.ROOT, 'data', 'people.csv')
TENURE_CSV = os.path.join(common.ROOT, 'data', 'unit_commanders.csv')
LINK_CSV = os.path.join(common.ROOT, 'data', 'unit_commander_claims.csv')
PEOPLE_WHERE = 'data/people.csv'
TENURE_WHERE = 'data/unit_commanders.csv'
LINK_WHERE = 'data/unit_commander_claims.csv'

PERSON_RE = re.compile(r'^PE\d{4,}$')
TENURE_RE = re.compile(r'^UC\d{4,}$')
CLAIM_RE = re.compile(r'^C\d{4,}$')
GROUP_RE = re.compile(r'^G\d{3,}$')
TIME_RE = re.compile(r'^([01]\d|2[0-3]):[0-5]\d$')

# Columns of the unified build/unit_commanders.csv (data columns plus derived names).
TENURE_BUILD_HEADER = [
    'tenure_id', 'unit_id', 'unit_name', 'nationality', 'domain', 'echelon',
    'person_id', 'canonical_name', 'sort_name', 'role', 'rank', 'rank_disputed',
    'valid_from', 'valid_from_latest', 'valid_from_time', 'valid_from_basis',
    'valid_to', 'valid_to_earliest', 'valid_to_time', 'valid_to_basis',
    'end_unknown', 'change_undated', 'date_basis', 'status', 'conflict_group_id',
    'reference_ids', 'source_claim_ids', 'note',
]
PEOPLE_BUILD_HEADER = [
    'person_id', 'canonical_name', 'sort_name', 'given_names', 'surname',
    'name_particles', 'generation', 'alt_names', 'nationality', 'name_completeness',
    'notes', 'tenures_count', 'units_count',
]


def people_header():
    return [f['name'] for f in common.load_schema('people')['fields']]


def tenure_header():
    return [f['name'] for f in common.load_schema('unit_commanders')['fields']]


def link_header():
    return [f['name'] for f in common.load_schema('unit_commander_claims')['fields']]


def _load(path):
    if not os.path.isfile(path):
        return None, []
    with open(path, newline='', encoding='utf-8') as fh:
        rd = csv.reader(fh)
        h = next(rd)
        return h, [dict(zip(h, r)) for r in rd if r]


def load_people(path=PEOPLE_CSV):
    return _load(path)


def load_tenures(path=TENURE_CSV):
    return _load(path)


def load_links(path=LINK_CSV):
    return _load(path)


def parse_ids(s):
    return [x.strip() for x in (s or '').split(';') if x.strip()]


def _date(s):
    if not s:
        return None
    try:
        return datetime.datetime.strptime(s, '%Y-%m-%d').date()
    except ValueError:
        return None


def domain_of(unit):
    if not unit:
        return 'ground'
    return (unit.get('domain') or '').strip() or 'ground'


def person_ids_for_claim(links_by_claim, cid):
    """Distinct person_ids linked to a claim, in stable person_id order.

    The caller must pass a map of claim_id -> list of (tenure, link) or we
    resolve via a precomputed claim -> person_ids map.
    """
    return links_by_claim.get(cid, [])


def attach_person_ids(rows, tenures=None, links=None):
    """Set commander_person_id on each claim dict (';'-separated PE####, sorted)."""
    if tenures is None:
        _h, tenures = load_tenures()
    if links is None:
        _h, links = load_links()
    by_tenure = {t['tenure_id']: t for t in tenures or []}
    by_claim = {}
    for l in links or []:
        t = by_tenure.get(l['tenure_id'])
        if t and t.get('person_id'):
            by_claim.setdefault(l['claim_id'], set()).add(t['person_id'])
    for r in rows:
        ids = sorted(by_claim.get(r.get('claim_id'), []), key=lambda x: int(x[2:]))
        r['commander_person_id'] = ';'.join(ids)


def derived_people(people, tenures):
    """Rows of build/people.csv (header PEOPLE_BUILD_HEADER)."""
    counts = {}
    units = {}
    for t in tenures:
        pid = t['person_id']
        counts[pid] = counts.get(pid, 0) + 1
        units.setdefault(pid, set()).add(t['unit_id'])
    rows = []
    for p in people:
        pid = p['person_id']
        rows.append([p.get(c, '') for c in people_header()] + [
            str(counts.get(pid, 0)),
            str(len(units.get(pid, ()))),
        ])
    return rows


def derived_tenures(tenures, people, links, units):
    """Rows of build/unit_commanders.csv (header TENURE_BUILD_HEADER), all statuses, all domains."""
    by_person = {p['person_id']: p for p in people}
    by_tenure_claims = {}
    for l in links:
        by_tenure_claims.setdefault(l['tenure_id'], []).append(l['claim_id'])
    rows = []
    for t in sorted(tenures, key=lambda r: (r['unit_id'], r['valid_from'], r['tenure_id'])):
        u = units.get(t['unit_id'], {})
        p = by_person.get(t['person_id'], {})
        cids = sorted(set(by_tenure_claims.get(t['tenure_id'], [])), key=lambda x: int(x[1:]))
        rows.append([
            t['tenure_id'], t['unit_id'], u.get('unit_name', ''), u.get('nationality', ''),
            domain_of(u), u.get('echelon', ''),
            t['person_id'], p.get('canonical_name', ''), p.get('sort_name', ''),
            t['role'], t.get('rank', ''), t.get('rank_disputed', ''),
            t.get('valid_from', ''), t.get('valid_from_latest', ''), t.get('valid_from_time', ''), t.get('valid_from_basis', ''),
            t.get('valid_to', ''), t.get('valid_to_earliest', ''), t.get('valid_to_time', ''), t.get('valid_to_basis', ''),
            t.get('end_unknown', ''), t.get('change_undated', ''), t.get('date_basis', ''),
            t.get('status', ''), t.get('conflict_group_id', ''),
            t.get('reference_ids', ''), ';'.join(cids), t.get('note', ''),
        ])
    return rows


def _id_num(s, prefix):
    return int(s[len(prefix):]) if s.startswith(prefix) and s[len(prefix):].isdigit() else None


def check(people_h, people, tenure_h, tenures, link_h, links, units, claims, vocabs, ref_ids, nat_names):
    """Return a list of (where, message) problems. claims is a list of claim dicts."""
    out = []
    want_p, want_t, want_l = people_header(), tenure_header(), link_header()
    if people_h is None:
        out.append((PEOPLE_WHERE, 'missing'))
        return out
    if people_h != want_p:
        out.append((PEOPLE_WHERE, 'header %s != schema/people.schema.json %s' % (people_h, want_p)))
        return out
    if tenure_h is None:
        out.append((TENURE_WHERE, 'missing'))
        return out
    if tenure_h != want_t:
        out.append((TENURE_WHERE, 'header %s != schema/unit_commanders.schema.json %s' % (tenure_h, want_t)))
        return out
    if link_h is None:
        out.append((LINK_WHERE, 'missing'))
        return out
    if link_h != want_l:
        out.append((LINK_WHERE, 'header %s != schema/unit_commander_claims.schema.json %s' % (link_h, want_l)))
        return out

    roles = vocabs['commander_role']['values']
    completeness = vocabs['name_completeness']['values']
    claim_roles = vocabs['commander_claim_role']['values']
    start_bases = vocabs['relation_start_basis']['values']
    end_bases = vocabs['relation_end_basis']['values']
    date_bases = vocabs['relationship_date_basis']['values']
    statuses = vocabs['claim_status']['values']
    booleans = vocabs['boolean']['values']

    # ---- people ----
    people_ids = []
    seen_people = set()
    used_people = {t['person_id'] for t in tenures}
    for i, p in enumerate(people, start=2):
        w = '%s line %d' % (PEOPLE_WHERE, i)
        pid = p.get('person_id', '')
        if not PERSON_RE.fullmatch(pid):
            out.append((w, 'person_id %r does not match PE0001' % pid))
        if pid in seen_people:
            out.append((w, 'duplicate person_id %s' % pid))
        seen_people.add(pid)
        people_ids.append(pid)
        if not (p.get('canonical_name') or '').strip():
            out.append((w, 'canonical_name is blank'))
        if not (p.get('sort_name') or '').strip():
            out.append((w, 'sort_name is blank'))
        if not (p.get('surname') or '').strip():
            out.append((w, 'surname is blank'))
        nc = p.get('name_completeness', '')
        if nc not in completeness:
            out.append((w, 'name_completeness %r not in vocabulary name_completeness' % nc))
        if nc == 'full' and not (p.get('given_names') or '').strip():
            out.append((w, 'name_completeness is full but given_names is blank'))
        if nc in ('surname_only', 'incomplete') and (p.get('given_names') or '').strip():
            out.append((w, 'name_completeness is %s but given_names is set' % nc))
        nat = (p.get('nationality') or '').strip()
        if nat and nat not in nat_names:
            out.append((w, 'nationality %r is not a name in data/nationalities.csv' % nat))
        if pid and pid not in used_people:
            out.append((w, 'person_id %s is not used in data/unit_commanders.csv' % pid))
    if people_ids != sorted(people_ids, key=lambda x: int(x[2:]) if PERSON_RE.fullmatch(x) else x):
        out.append((PEOPLE_WHERE, 'rows must be sorted by person_id'))
    nums = [_id_num(x, 'PE') for x in people_ids]
    nums = [n for n in nums if n is not None]
    if nums:
        gaps = sorted(set(range(1, max(nums) + 1)) - set(nums))
        if gaps:
            out.append((PEOPLE_WHERE, 'person id(s) below the highest are unused (ids are assigned without gaps): %s' %
                        (', '.join('PE%04d' % g for g in gaps[:20]) + (' ...' if len(gaps) > 20 else ''))))

    # ---- tenures ----
    tenure_ids = []
    seen_tenures = set()
    by_tenure = {}
    unique_keys = {}
    claims_by_id = {c['claim_id']: c for c in claims}
    links_by_tenure = {}
    for l in links:
        links_by_tenure.setdefault(l['tenure_id'], []).append(l)

    for i, t in enumerate(tenures, start=2):
        w = '%s line %d' % (TENURE_WHERE, i)
        tid = t.get('tenure_id', '')
        if not TENURE_RE.fullmatch(tid):
            out.append((w, 'tenure_id %r does not match UC0001' % tid))
        if tid in seen_tenures:
            out.append((w, 'duplicate tenure_id %s' % tid))
        seen_tenures.add(tid)
        tenure_ids.append(tid)
        by_tenure[tid] = t
        uid, pid = t.get('unit_id', ''), t.get('person_id', '')
        if uid not in units:
            out.append((w, 'unit_id %r is not a unit of data/units.csv' % uid))
        if pid not in seen_people:
            out.append((w, 'person_id %r is not in data/people.csv' % pid))
        if t.get('role') not in roles:
            out.append((w, 'role %r not in vocabulary commander_role' % t.get('role')))
        for col in ('rank_disputed', 'end_unknown', 'change_undated'):
            if t.get(col) not in booleans:
                out.append((w, '%s %r is not a boolean (true or false)' % (col, t.get(col))))
        if t.get('valid_from_basis') not in start_bases:
            out.append((w, 'valid_from_basis %r not in vocabulary relation_start_basis' % t.get('valid_from_basis')))
        if t.get('valid_to_basis') not in end_bases:
            out.append((w, 'valid_to_basis %r not in vocabulary relation_end_basis' % t.get('valid_to_basis')))
        if t.get('date_basis') not in date_bases:
            out.append((w, 'date_basis %r not in vocabulary relationship_date_basis' % t.get('date_basis')))
        if t.get('status') not in statuses:
            out.append((w, 'status %r not in vocabulary claim_status' % t.get('status')))
        cg = (t.get('conflict_group_id') or '').strip()
        if t.get('status') in ('alternate', 'disputed') and not cg:
            out.append((w, 'status %s requires a conflict_group_id' % t.get('status')))
        if cg and not GROUP_RE.fullmatch(cg):
            out.append((w, 'conflict_group_id %r is not a conflict group (G001 onward)' % cg))
        vf, vt = _date(t.get('valid_from')), _date(t.get('valid_to'))
        vfl, vte = _date(t.get('valid_from_latest')), _date(t.get('valid_to_earliest'))
        if not t.get('valid_from') or vf is None:
            if t.get('valid_from'):
                out.append((w, 'valid_from %r is not a valid date YYYY-MM-DD' % t.get('valid_from')))
            else:
                out.append((w, 'valid_from is blank'))
        if t.get('valid_to') and vt is None:
            out.append((w, 'valid_to %r is not a valid date YYYY-MM-DD' % t.get('valid_to')))
        if t.get('valid_from_latest') and vfl is None:
            out.append((w, 'valid_from_latest %r is not a valid date YYYY-MM-DD' % t.get('valid_from_latest')))
        if t.get('valid_to_earliest') and vte is None:
            out.append((w, 'valid_to_earliest %r is not a valid date YYYY-MM-DD' % t.get('valid_to_earliest')))
        if vf and vt and vt < vf:
            out.append((w, 'valid_to %s is before valid_from %s' % (t.get('valid_to'), t.get('valid_from'))))
        if vf and vfl and vfl < vf:
            out.append((w, 'valid_from_latest %s is before valid_from %s' % (t.get('valid_from_latest'), t.get('valid_from'))))
        if vt and vte and vte > vt:
            out.append((w, 'valid_to_earliest %s is after valid_to %s' % (t.get('valid_to_earliest'), t.get('valid_to'))))
        if vte and not t.get('valid_to'):
            out.append((w, 'valid_to_earliest needs valid_to (the latest possible end)'))
        if bool(t.get('valid_to')) != (t.get('valid_to_basis') != 'open_at_last_claim'):
            out.append((w, 'valid_to %r and valid_to_basis %s disagree (blank valid_to <=> open_at_last_claim)' % (
                t.get('valid_to'), t.get('valid_to_basis'))))
        if t.get('valid_to_basis') == 'inferred_from_next_claim' and not t.get('valid_to_earliest'):
            out.append((w, 'inferred_from_next_claim needs valid_to_earliest (the last claim date that names the person)'))
        for tk, dk in (('valid_from_time', 'valid_from'), ('valid_to_time', 'valid_to')):
            if t.get(tk):
                if not t.get(dk):
                    out.append((w, '%s needs %s' % (tk, dk)))
                if not TIME_RE.fullmatch(t.get(tk)):
                    out.append((w, '%s %r is not HH:MM' % (tk, t.get(tk))))
        refs = parse_ids(t.get('reference_ids', ''))
        if not refs:
            out.append((w, 'reference_ids is empty'))
        for x in refs:
            if x not in ref_ids:
                out.append((w, 'reference_ids: %s is not in data/references_meta.csv' % x))
        uk = (uid, pid, t.get('role'), t.get('valid_from'), t.get('valid_to'), t.get('status'))
        if uk in unique_keys:
            out.append((w, 'duplicate tenure key (unit_id, person_id, role, valid_from, valid_to, status) already used by %s' % unique_keys[uk]))
        unique_keys[uk] = tid
        ls = links_by_tenure.get(tid, [])
        if not ls:
            out.append((w, 'no row in data/unit_commander_claims.csv: a tenure needs evidence'))
        else:
            lc = [claims_by_id[l['claim_id']] for l in ls if l['claim_id'] in claims_by_id]
            # A preferred tenure in a commander-identity conflict group needs preferred evidence.
            # A preferred tenure may rest only on an alternate-dated claim when the disagreement is
            # about the event date, not about who commanded (e.g. C8380 / G066, commander cell unknown on the preferred sibling).
            if (t.get('status') == 'preferred' and t.get('conflict_group_id') and lc and not any(
                    c.get('claim_status') == 'preferred' or (c.get('commander') or '').strip() == 'unknown' for c in lc)):
                out.append((w, 'a preferred tenure needs a preferred claim as evidence'))
            if t.get('valid_from_basis') == 'claim_date' and lc:
                first = min(c['date'] for c in lc)
                if t.get('valid_from') != first:
                    out.append((w, 'valid_from_basis claim_date but valid_from %s is not the date of the first linked claim %s' % (
                        t.get('valid_from'), first)))
            if t.get('valid_to_basis') == 'inferred_from_next_claim' and t.get('valid_to_earliest') and t.get('valid_to_earliest') not in {c['date'] for c in lc}:
                out.append((w, 'valid_to_earliest %s must be the date of a linked claim (the last one that names the person before the inferred end)' % t.get('valid_to_earliest')))

    if tenure_ids != sorted(tenure_ids, key=lambda x: int(x[2:]) if TENURE_RE.fullmatch(x) else x):
        out.append((TENURE_WHERE, 'rows must be sorted by tenure_id'))
    tnums = [_id_num(x, 'UC') for x in tenure_ids]
    tnums = [n for n in tnums if n is not None]
    if tnums:
        gaps = sorted(set(range(1, max(tnums) + 1)) - set(tnums))
        if gaps:
            out.append((TENURE_WHERE, 'tenure id(s) below the highest are unused (ids are assigned without gaps): %s' %
                        (', '.join('UC%04d' % g for g in gaps[:20]) + (' ...' if len(gaps) > 20 else ''))))

    # Preferred commander-vs-commander overlaps (except sourced same-day handover,
    # a shared conflict group, or incidental naming of a different officer).
    # acting_commander / temporary_commander may overlap commander (official still in post).
    # deputy_commander and embarked_commander are not exclusive slots.
    from collections import defaultdict
    by_unit_role = defaultdict(list)
    for t in tenures:
        if t.get('status') == 'preferred' and t.get('role') == 'commander':
            by_unit_role[(t.get('unit_id'), t.get('role'))].append(t)

    def interval(t):
        a = _date(t.get('valid_from'))
        b = _date(t.get('valid_to')) if t.get('valid_to') else datetime.date(9999, 12, 31)
        return a, b

    def only_observed(t):
        ls = links_by_tenure.get(t.get('tenure_id'), [])
        return bool(ls) and all(l.get('role') == 'observed_during' for l in ls)

    for key, ts in by_unit_role.items():
        for i, a in enumerate(ts):
            a0, a1 = interval(a)
            if not a0:
                continue
            for b in ts[i + 1:]:
                b0, b1 = interval(b)
                if not b0:
                    continue
                start, end = max(a0, b0), min(a1, b1)
                if start > end:
                    continue
                # Allowed: sourced same-day handover.
                if start == end:
                    continue
                # Allowed: disputed handover window in the same conflict group.
                ag, bg = (a.get('conflict_group_id') or '').strip(), (b.get('conflict_group_id') or '').strip()
                if ag and ag == bg:
                    continue
                # Allowed: incidental naming (one tenure is only observed_during and sits inside the other).
                if (only_observed(a) and a0 >= b0 and a1 <= b1) or (only_observed(b) and b0 >= a0 and b1 <= a1):
                    continue
                out.append((TENURE_WHERE, 'preferred tenures %s and %s overlap on %s (%s %s)' % (
                    a['tenure_id'], b['tenure_id'], key[0], key[1],
                    start.isoformat() if start == end else '%s to %s' % (start, end))))

    # ---- links ----
    seen_links = set()
    named_linked = set()
    unknown_bad = []
    for i, l in enumerate(links, start=2):
        w = '%s line %d' % (LINK_WHERE, i)
        tid, cid, role = l.get('tenure_id', ''), l.get('claim_id', ''), l.get('role', '')
        if not TENURE_RE.fullmatch(tid):
            out.append((w, 'tenure_id %r does not match UC0001' % tid))
        elif tid not in seen_tenures:
            out.append((w, 'tenure_id %s is not in data/unit_commanders.csv' % tid))
        if not CLAIM_RE.fullmatch(cid):
            out.append((w, 'claim_id %r is not a claim id' % cid))
        elif cid not in claims_by_id:
            out.append((w, 'claim_id %s is not a claim' % cid))
        if role not in claim_roles:
            out.append((w, 'role %r not in vocabulary commander_claim_role' % role))
        if (tid, cid) in seen_links:
            out.append((w, 'duplicate link %s + %s' % (tid, cid)))
        seen_links.add((tid, cid))
        c = claims_by_id.get(cid)
        if c is not None:
            cmd = (c.get('commander') or '').strip()
            if cmd == 'unknown':
                if role != 'asserts_end':
                    out.append((w, 'claim %s has commander unknown but is linked as %s (only asserts_end is allowed, for a sourced vacancy)' % (cid, role)))
            else:
                named_linked.add(cid)
            t = by_tenure.get(tid)
            if t and c.get('unit_id') and c['unit_id'] != t['unit_id'] and role != 'asserts_end':
                # Embarked commanders are still on the ship's claim (same unit). A vacancy end is on the same unit too.
                # No cross-unit links expected in Phase 1.
                if c['unit_id'] != t['unit_id']:
                    out.append((w, 'link to %s belongs to unit %s but tenure %s is for %s' % (cid, c['unit_id'], tid, t['unit_id'])))

    got = [(l['tenure_id'], l['claim_id']) for l in links]
    want = sorted(got, key=lambda p: (int(p[0][2:]) if TENURE_RE.fullmatch(p[0]) else p[0],
                                      int(p[1][1:]) if CLAIM_RE.fullmatch(p[1]) else p[1]))
    if got != want:
        out.append((LINK_WHERE, 'rows must be sorted by tenure_id then claim_id'))

    for c in claims:
        cmd = (c.get('commander') or '').strip()
        if cmd and cmd != 'unknown' and c['claim_id'] not in named_linked:
            out.append(('data/claims %s' % c['claim_id'],
                        'named commander %r is not linked in data/unit_commander_claims.csv' % cmd[:80]))

    return out
