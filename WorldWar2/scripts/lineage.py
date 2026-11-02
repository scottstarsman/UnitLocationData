"""Unit lineage links (data/unit_lineage.csv, schema/unit_lineage.schema.json).

load() reads the table; check(rows, units, vocabs, ref_ids) returns a list of (where, message) problems;
neighbours(rows) gives {unit_id: (predecessor ids, successor ids)} for the build outputs.
"""
import csv
import datetime
import os
import re

import common

PATH = os.path.join(common.ROOT, 'data', 'unit_lineage.csv')
WHERE = 'data/unit_lineage.csv'


def header():
    return [f['name'] for f in common.load_schema('unit_lineage')['fields']]


def load(path=PATH):
    with open(path, newline='', encoding='utf-8') as fh:
        rd = csv.reader(fh)
        h = next(rd)
        return h, [dict(zip(h, r)) for r in rd if r]


def _date(s):
    m = re.fullmatch(r'(\d{4})(?:-(\d{2})(?:-(\d{2}))?)?', s or '')
    if not m:
        return None
    try:
        return datetime.date(int(m.group(1)), int(m.group(2) or 1), int(m.group(3) or 1))
    except ValueError:
        return None


def find_cycle(rows):
    """Return a list of unit ids forming a cycle in predecessor -> successor links, or None."""
    nxt = {}
    for r in rows:
        nxt.setdefault(r['predecessor_unit_id'], []).append(r['successor_unit_id'])
    state = {}

    def visit(u, path):
        state[u] = 1
        for v in nxt.get(u, []):
            if state.get(v) == 1:
                return path[path.index(v):] + [v] if v in path else [u, v]
            if not state.get(v):
                c = visit(v, path + [v])
                if c:
                    return c
        state[u] = 2
        return None

    for u in list(nxt):
        if not state.get(u):
            c = visit(u, [u])
            if c:
                return c
    return None


def check(h, rows, units, vocabs, ref_ids):
    out = []
    if h != header():
        out.append((WHERE, 'header %s != schema/unit_lineage.schema.json %s' % (h, header())))
        return out
    kinds = vocabs['lineage_kind']['values']
    bases = vocabs['relationship_date_basis']['values']
    ids, pairs = [], set()
    for i, r in enumerate(rows, start=2):
        w = '%s line %d' % (WHERE, i)
        lid = r['lineage_id']
        if not re.fullmatch(r'UL\d{3,}', lid):
            out.append((w, 'lineage_id %r does not match UL001' % lid))
        if lid in ids:
            out.append((w, 'duplicate lineage_id %s' % lid))
        ids.append(lid)
        p, s = r['predecessor_unit_id'], r['successor_unit_id']
        for col, u in (('predecessor_unit_id', p), ('successor_unit_id', s)):
            if u not in units:
                out.append((w, '%s %r is not a unit of data/units.csv' % (col, u)))
        if p == s:
            out.append((w, 'predecessor and successor are the same unit %s' % p))
        if (p, s) in pairs:
            out.append((w, 'duplicate link %s -> %s' % (p, s)))
        pairs.add((p, s))
        if r['kind'] not in kinds:
            out.append((w, 'kind %r not in vocabulary lineage_kind %s' % (r['kind'], sorted(kinds))))
        if r['date_basis'] not in bases:
            out.append((w, 'date_basis %r not in vocabulary relationship_date_basis' % r['date_basis']))
        d = _date(r['effective_date'])
        if d is None:
            out.append((w, 'effective_date %r is not a real YYYY, YYYY-MM or YYYY-MM-DD' % r['effective_date']))
        elif not datetime.date(1939, 1, 1) <= d <= datetime.date(1945, 12, 31):
            out.append((w, 'effective_date %s outside 1939-1945' % r['effective_date']))
        elif p in units:
            pf = _date(units[p].get('formed_date', ''))
            if pf and d < pf:
                out.append((w, 'effective_date %s is before the predecessor formed_date %s' % (r['effective_date'], units[p]['formed_date'])))
        refs = [x for x in r['reference_ids'].split(';') if x]
        if not refs:
            out.append((w, 'reference_ids is empty'))
        for x in refs:
            if x not in ref_ids:
                out.append((w, 'reference_ids: %s is not in data/references_meta.csv' % x))
        for a, b in ((p, s), (s, p)):
            if a in units and b in units and b not in units[a].get('unit_note', ''):
                out.append((w, 'unit_note of %s must name the linked record %s' % (a, b)))
    if ids != sorted(ids):
        out.append((WHERE, 'rows must be sorted by lineage_id'))
    c = find_cycle(rows)
    if c:
        out.append((WHERE, 'lineage links form a cycle: %s' % ' -> '.join(c)))
    return out


def neighbours(rows):
    nb = {}
    for r in sorted(rows, key=lambda r: (r['effective_date'], r['lineage_id'])):
        nb.setdefault(r['successor_unit_id'], ([], []))[0].append(r['predecessor_unit_id'])
        nb.setdefault(r['predecessor_unit_id'], ([], []))[1].append(r['successor_unit_id'])
    return nb
