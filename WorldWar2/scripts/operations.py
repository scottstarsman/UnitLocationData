#!/usr/bin/env python3
"""The operations tables: loading, the parent chain, derived labels and the checks used by validate.py and build.py.

Files (hand-maintained, under data/):
  operations.csv          one row per operation, battle, phase, campaign or umbrella; claims point at one row by operation_id;
                          optional primary_place_id is a sourced map pin (FK to data/places.csv)
  operation_relations.csv links between operations other than parent/child (follows, concurrent_with, supports, related)
  operation_exceptions.csv  claims dated outside the window of their operation, each with a reason
  operation_places.csv    sourced places of an operation (composite key operation_id + place_id; role from operation_place_role)

A claim carries ONE operation_id, the most specific operation it belongs to. The chain of parent_operation_id values above it
(battle > operation > campaign > umbrella) is derived here, together with the old-style labels (campaign, operation_name,
sub_operation_name) that build/all_claims.csv still carries for convenience:

  campaign            the CMH campaign streamer (date_basis = cmh_streamer) in the claim's chain whose dates contain the claim's date;
                      otherwise, for a claim whose operation sits in no streamer campaign or whose chain's streamer does not cover the
                      date, the earliest-starting streamer that does (Southern France and Ardennes-Alsace therefore only reach a claim
                      through its chain)
  operation_name      the topmost operation or umbrella in the chain (op_type operation or umbrella) whose dates contain the claim's date;
                      blank when none does (so Overlord never labels a claim after 30 August 1944)
  sub_operation_name  the claim's own operation (short_name) when it is not a streamer campaign, an umbrella or the operation_name itself
  operation_path      the full chain, outermost first, ' > ' separated

Standard library only.
"""
import csv
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common  # noqa: E402
import theaters  # noqa: E402

OPERATIONS_CSV = os.path.join(common.ROOT, 'data', 'operations.csv')
RELATIONS_CSV = os.path.join(common.ROOT, 'data', 'operation_relations.csv')
EXCEPTIONS_CSV = os.path.join(common.ROOT, 'data', 'operation_exceptions.csv')
PLACES_CSV = os.path.join(common.ROOT, 'data', 'operation_places.csv')

OP_HEADER = ['operation_id', 'name', 'short_name', 'alt_names', 'op_type', 'parent_operation_id', 'start_date', 'end_date',
             'date_basis', 'parent_date_exception', 'theater', 'sub_theater', 'nationality_scope', 'reference_ids', 'primary_place_id', 'notes']
REL_HEADER = ['from_operation_id', 'to_operation_id', 'relation', 'reference_ids', 'note']
EXC_HEADER = ['claim_id', 'operation_id', 'reason']
PLACES_HEADER = ['operation_id', 'place_id', 'role', 'reference_ids', 'note']

# Single source: schema/vocabularies.json (op_type, operation_date_basis, operation_relation) and data/nationalities.csv (scope)
OP_TYPES = common.vocab_descriptions('op_type')
DATE_BASES = common.vocab_descriptions('operation_date_basis')
RELATIONS = common.vocab_descriptions('operation_relation')
PLACE_ROLES = common.vocab_descriptions('operation_place_role')
# nationality_scope: the `name` of a row of data/nationalities.csv (Allied, Germany, ...) or All (neutral or both sides)
SCOPES = dict({'All': 'Neutral or both sides.'}, **{n['name']: 'Name or concept of %s.' % n['name'] for n in common.load_nationalities()})


def _read(path, header):
    if not os.path.isfile(path):
        return None, []
    h, rows = common.read_dicts(path)
    return h, rows


class Operations:
    """The operations tables in memory."""

    def __init__(self):
        self.header, self.rows = _read(OPERATIONS_CSV, OP_HEADER)
        self.rel_header, self.relations = _read(RELATIONS_CSV, REL_HEADER)
        self.exc_header, self.exceptions = _read(EXCEPTIONS_CSV, EXC_HEADER)
        self.places_header, self.places = _read(PLACES_CSV, PLACES_HEADER)
        self.by_id = {r['operation_id']: r for r in self.rows}
        self.exc_index = {(e['claim_id'], e['operation_id']) for e in self.exceptions}
        self.streamers = sorted((r for r in self.rows if r['op_type'] == 'campaign' and r['date_basis'] == 'cmh_streamer'),
                                key=lambda r: (r['start_date'], r['operation_id']))

    def chain(self, op_id):
        """The operation and its ancestors, most specific first. Stops at a missing parent or a cycle."""
        out, seen = [], set()
        while op_id and op_id in self.by_id and op_id not in seen:
            seen.add(op_id)
            out.append(self.by_id[op_id])
            op_id = self.by_id[op_id]['parent_operation_id']
        return out

    @staticmethod
    def contains(op, date):
        return bool(op['start_date'] and op['end_date'] and op['start_date'] <= date <= op['end_date'])

    def labels(self, op_id, date):
        """Derived labels for a claim: dict with operation, operation_type, campaign, operation_name, sub_operation_name, operation_path."""
        ch = self.chain(op_id)
        if not ch:
            return dict(operation='', operation_type='', campaign='', operation_name='', sub_operation_name='', operation_path='')
        leaf = ch[0]
        camp = next((c for c in ch if c['date_basis'] == 'cmh_streamer' and c['op_type'] == 'campaign' and self.contains(c, date)), None)
        if camp is None and leaf['theater'] == 'western_europe':   # the CMH streamers are European-African-Middle Eastern Western Front campaigns: no fallback for other theaters
            camp = next((c for c in self.streamers if self.contains(c, date)), None)
        ops = [c for c in ch if c['op_type'] in ('operation', 'umbrella') and self.contains(c, date)]
        top = ops[-1] if ops else None
        sub = ''
        if leaf['op_type'] not in ('umbrella',) and leaf['date_basis'] != 'cmh_streamer' and (top is None or leaf['operation_id'] != top['operation_id']):
            sub = leaf['short_name'] or leaf['name']
        return dict(operation=leaf['name'], operation_type=leaf['op_type'], campaign=camp['short_name'] if camp else '',
                    operation_name=(top['short_name'] or top['name']) if top else '', sub_operation_name=sub,
                    operation_path=' > '.join(c['name'] for c in reversed(ch)))

    def depth(self, op_id):
        return len(self.chain(op_id)) - 1

    def children(self, op_id):
        return [r for r in self.rows if r['parent_operation_id'] == op_id]


def load():
    return Operations()


# ---------------------------------------------------------------- checks

WAR_START = '1939-09-01'   # kept as the European default; per-theater floors live in schema/theaters.json
# (global earliest date 1937-07-07). Claim and mission date checks use theaters.date_floor().
ID_RE = re.compile(r'OP-[A-Z0-9]+(-[A-Z0-9]+)*')
ISO = re.compile(r'\d{4}-\d{2}-\d{2}')


def check(ops, claims, reference_ids, vocab_theaters, valid_iso, place_ids=None):
    """Return (errors, warnings), each a list of (where, message). `claims` is a list of claim dicts with `_where` set.
    `place_ids` is the set of data/places.csv place_id values (loaded here when omitted)."""
    E, W = [], []
    e = lambda w, m: E.append((w, m))  # noqa: E731
    w = lambda wh, m: W.append((wh, m))  # noqa: E731
    if place_ids is None:
        places_path = os.path.join(common.ROOT, 'data', 'places.csv')
        place_ids = {r['place_id'] for r in common.read_dicts(places_path)[1]} if os.path.isfile(places_path) else set()
    if ops.header is None:
        e('data/operations.csv', 'missing')
        return E, W
    if ops.header != OP_HEADER:
        e('data/operations.csv', 'header %s != %s' % (ops.header, OP_HEADER))
        return E, W
    seen = set()
    for i, r in enumerate(ops.rows, start=2):
        wh = 'data/operations.csv line %d (%s)' % (i, r['operation_id'])
        if not ID_RE.fullmatch(r['operation_id']):
            e(wh, 'operation_id must match OP-[A-Z0-9]+(-[A-Z0-9]+)*')
        if r['operation_id'] in seen:
            e(wh, 'duplicate operation_id')
        seen.add(r['operation_id'])
        for f in ('name', 'short_name', 'op_type', 'start_date', 'end_date', 'date_basis', 'theater', 'nationality_scope'):
            if not r[f].strip():
                e(wh, '%s is required' % f)
        if r['op_type'] not in OP_TYPES:
            e(wh, 'op_type %r not in %s' % (r['op_type'], sorted(OP_TYPES)))
        if r['date_basis'] not in DATE_BASES:
            e(wh, 'date_basis %r not in %s' % (r['date_basis'], sorted(DATE_BASES)))
        if r['nationality_scope'] not in SCOPES:
            e(wh, 'nationality_scope %r not in %s' % (r['nationality_scope'], sorted(SCOPES)))
        if r['theater'] and r['theater'] not in vocab_theaters:
            e(wh, 'theater %r not in the theater vocabulary' % r['theater'])
        msg = theaters.sub_theater_error(r.get('theater', ''), r.get('sub_theater', ''))
        if msg:
            e(wh, msg)
        for f in ('start_date', 'end_date'):
            if r[f] and not (ISO.fullmatch(r[f]) and valid_iso(r[f])):
                e(wh, '%s %r is not a valid YYYY-MM-DD date' % (f, r[f]))
        if r['start_date'] and r['end_date'] and r['start_date'] > r['end_date']:
            e(wh, 'start_date is after end_date')
        if r['date_basis'] == 'cmh_streamer' and r['op_type'] != 'campaign':
            e(wh, 'date_basis cmh_streamer is only for op_type campaign')
        refs = [x for x in r['reference_ids'].split(';') if x.strip()]
        for x in refs:
            if x.strip() not in reference_ids:
                e(wh, 'reference_id %s is not in data/references_meta.csv' % x.strip())
        if not refs and not r['notes'].strip():
            e(wh, 'needs a source (reference_ids) or a note that explains why there is none')
        if r['date_basis'] in ('derived',) and not r['notes'].strip():
            e(wh, 'date_basis derived needs a note that says how the dates were set')
        pid = (r.get('primary_place_id') or '').strip()
        if pid and pid not in place_ids:
            e(wh, 'primary_place_id %s is not in data/places.csv' % pid)
    ids = set(ops.by_id)
    for i, r in enumerate(ops.rows, start=2):
        wh = 'data/operations.csv line %d (%s)' % (i, r['operation_id'])
        p = r['parent_operation_id']
        if p:
            if p not in ids:
                e(wh, 'parent_operation_id %s does not exist' % p)
            else:
                par = ops.by_id[p]
                if p == r['operation_id']:
                    e(wh, 'an operation cannot be its own parent')
                if par['start_date'] and r['start_date'] and par['end_date'] and r['end_date'] \
                        and (r['start_date'] < par['start_date'] or r['end_date'] > par['end_date']) and not r['parent_date_exception'].strip():
                    w(wh, 'dates %s to %s fall outside the parent %s (%s to %s): fix the dates or explain in parent_date_exception'
                      % (r['start_date'], r['end_date'], p, par['start_date'], par['end_date']))
                if par['theater'] != r['theater']:
                    e(wh, 'theater %s differs from the parent %s (%s): an operation stays in its parent\'s theater' % (r['theater'], p, par['theater']))
                par_sub = (par.get('sub_theater') or '').strip()
                my_sub = (r.get('sub_theater') or '').strip()
                if par_sub and my_sub and par_sub != my_sub:
                    e(wh, 'sub_theater %s differs from the parent %s (%s): an operation stays in its parent\'s sub-theater when the parent has one' % (my_sub, p, par_sub))
                if par['op_type'] in ('battle', 'phase') and r['op_type'] in ('umbrella', 'campaign', 'operation'):
                    w(wh, 'a %s is a child of a %s (%s)' % (r['op_type'], par['op_type'], p))
        elif r['parent_date_exception'].strip():
            w(wh, 'parent_date_exception is set but there is no parent')
        # cycle check
        seen_c, cur = set(), r['parent_operation_id']
        while cur and cur in ids and cur not in seen_c:
            if cur == r['operation_id']:
                e(wh, 'parent chain is not acyclic (this operation is its own ancestor)')
                break
            seen_c.add(cur)
            cur = ops.by_id[cur]['parent_operation_id']
    if ops.rel_header is not None and ops.rel_header != REL_HEADER:
        e('data/operation_relations.csv', 'header %s != %s' % (ops.rel_header, REL_HEADER))
    seen_rel = set()
    for i, r in enumerate(ops.relations, start=2):
        wh = 'data/operation_relations.csv line %d' % i
        for f in ('from_operation_id', 'to_operation_id'):
            if r[f] not in ids:
                e(wh, '%s %r does not exist' % (f, r[f]))
        if r['from_operation_id'] == r['to_operation_id']:
            e(wh, 'an operation cannot be related to itself')
        if r['relation'] not in RELATIONS:
            e(wh, 'relation %r not in %s' % (r['relation'], sorted(RELATIONS)))
        for x in [x for x in r['reference_ids'].split(';') if x.strip()]:
            if x.strip() not in reference_ids:
                e(wh, 'reference_id %s is not in data/references_meta.csv' % x.strip())
        if not r['reference_ids'].strip() and not r['note'].strip():
            e(wh, 'needs a source (reference_ids) or a note')
        k = (r['from_operation_id'], r['to_operation_id'], r['relation'])
        if k in seen_rel:
            e(wh, 'duplicate relation')
        seen_rel.add(k)
    if ops.exc_header is not None and ops.exc_header != EXC_HEADER:
        e('data/operation_exceptions.csv', 'header %s != %s' % (ops.exc_header, EXC_HEADER))
    by_claim = {c['claim_id']: c for c in claims}
    for i, x in enumerate(ops.exceptions, start=2):
        wh = 'data/operation_exceptions.csv line %d' % i
        c = by_claim.get(x['claim_id'])
        if c is None:
            e(wh, 'claim %s does not exist' % x['claim_id'])
            continue
        if x['operation_id'] != c['operation_id']:
            e(wh, 'claim %s has operation_id %s, not %s' % (x['claim_id'], c['operation_id'], x['operation_id']))
        elif x['operation_id'] in ops.by_id and Operations.contains(ops.by_id[x['operation_id']], c['date']):
            w(wh, 'stale exception: claim %s is inside the dates of %s' % (x['claim_id'], x['operation_id']))
        if not x['reason'].strip():
            e(wh, 'reason is required')
    if ops.places_header is not None and ops.places_header != PLACES_HEADER:
        e('data/operation_places.csv', 'header %s != %s' % (ops.places_header, PLACES_HEADER))
    seen_pl, primary_of = set(), {}
    for i, r in enumerate(ops.places, start=2):
        wh = 'data/operation_places.csv line %d' % i
        if r['operation_id'] not in ids:
            e(wh, 'operation_id %r does not exist' % r['operation_id'])
        if not r['place_id'] or r['place_id'] not in place_ids:
            e(wh, 'place_id %r is not in data/places.csv' % r['place_id'])
        if r['role'] not in PLACE_ROLES:
            e(wh, 'role %r not in %s' % (r['role'], sorted(PLACE_ROLES)))
        refs = [x for x in r['reference_ids'].split(';') if x.strip()]
        if not refs:
            e(wh, 'reference_ids is required')
        for x in refs:
            if x.strip() not in reference_ids:
                e(wh, 'reference_id %s is not in data/references_meta.csv' % x.strip())
        k = (r['operation_id'], r['place_id'])
        if k in seen_pl:
            e(wh, 'duplicate (operation_id, place_id)')
        seen_pl.add(k)
        if r['role'] == 'primary':
            if r['operation_id'] in primary_of:
                e(wh, 'operation %s already has a primary place (%s)' % (r['operation_id'], primary_of[r['operation_id']]))
            primary_of[r['operation_id']] = r['place_id']
    for i, r in enumerate(ops.rows, start=2):
        wh = 'data/operations.csv line %d (%s)' % (i, r['operation_id'])
        pin = (r.get('primary_place_id') or '').strip()
        linked = primary_of.get(r['operation_id'], '')
        if pin and not linked:
            e(wh, 'primary_place_id %s has no matching role=primary row in data/operation_places.csv' % pin)
        elif linked and not pin:
            e(wh, 'data/operation_places.csv has primary place %s but primary_place_id is blank' % linked)
        elif pin and linked and pin != linked:
            e(wh, 'primary_place_id %s does not match the role=primary row (%s)' % (pin, linked))
    # claims
    for c in claims:
        wh = c['_where']
        oid = c['operation_id']
        if not oid:
            e(wh, 'operation_id is required')
            continue
        op = ops.by_id.get(oid)
        if op is None:
            e(wh, 'operation_id %s is not in data/operations.csv' % oid)
            continue
        if not Operations.contains(op, c['date']) and (c['claim_id'], oid) not in ops.exc_index:
            lab = 'an umbrella' if op['op_type'] == 'umbrella' else 'its operation'
            w(wh, 'dated %s, outside %s (%s %s to %s): choose the operation that covers the date (the campaign if none does) or add the claim to data/operation_exceptions.csv with a reason; %s must not label rows outside its dates'
              % (c['date'], oid, op['name'], op['start_date'], op['end_date'], lab))
        th = (c.get('theater') or '').strip()
        if not th:
            e(wh, 'theater is required')
        elif th != op['theater']:
            # theater decision (Scott, 9 November 2026): rows outside the Western Front keep their data under a per-front operation of their own theater
            e(wh, 'theater %s differs from the theater of its operation %s (%s): use the operation of the row\'s front (for example OP-FRONT-EASTERN or OP-HOME-GERMANY)' % (th, oid, op['theater']))
        c_sub = (c.get('sub_theater') or '').strip()
        op_sub = (op.get('sub_theater') or '').strip()
        msg = theaters.sub_theater_error(th, c_sub)
        if msg:
            e(wh, msg)
        if op_sub and c_sub and op_sub != c_sub:
            e(wh, 'sub_theater %s differs from the sub_theater of its operation %s (%s)' % (c_sub, oid, op_sub))
        floor = theaters.date_floor(th)
        if c['date'] and theaters.before_floor(c['date'], th):
            e(wh, 'dated %s, before the sanity bound %s for theater %s' % (c['date'], floor, th or '(none)'))
        elif th == 'western_europe' and not ops.labels(oid, c['date'])['campaign'] and not (ops.streamers and (c['date'] < ops.streamers[0]['start_date'] or c['date'] > max(s['end_date'] for s in ops.streamers))):
            # no streamer floor or ceiling: a claim dated before the first CMH streamer (6 June 1944) or after the last one ends (11 May 1945)
            # needs no campaign (decisions Scott, 4 November 2026: OP-PRE-INVASION and OP-POST-SURRENDER hold such rows); rows of other theaters need none either
            e(wh, 'no CMH campaign streamer covers the date %s' % c['date'])
    return E, W
