"""Dated nation allegiance (data/nation_allegiance.csv, schema/nation_allegiance.schema.json).

load() reads the table; check(h, rows, nationalities, vocabs, ref_ids) returns a list of (where, message) problems;
side_on(rows, nation, date) answers which side a nation was on at a date (None in a gap or outside every row).
"""
import csv
import datetime
import os
import re

import common

PATH = os.path.join(common.ROOT, 'data', 'nation_allegiance.csv')
WHERE = 'data/nation_allegiance.csv'
CONFLICT_SPAN = {'WW2': (datetime.date(1939, 9, 1), datetime.date(1945, 9, 2)),
                 'SJW2': (datetime.date(1937, 7, 7), datetime.date(1945, 9, 2))}


def header():
    return [f['name'] for f in common.load_schema('nation_allegiance')['fields']]


def load(path=PATH):
    with open(path, newline='', encoding='utf-8') as fh:
        rd = csv.reader(fh)
        h = next(rd)
        return h, [dict(zip(h, r)) for r in rd if r]


def _date(s):
    m = re.fullmatch(r'(\d{4})-(\d{2})-(\d{2})', s or '')
    if not m:
        return None
    try:
        return datetime.date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
    except ValueError:
        return None


def check(h, rows, nationalities, vocabs, ref_ids):
    """nationalities: {code: row of data/nationalities.csv}."""
    out = []
    if h != header():
        out.append((WHERE, 'header %s != schema/nation_allegiance.schema.json %s' % (h, header())))
        return out
    sides = vocabs['allegiance_side']['values']
    conflicts = vocabs['allegiance_conflict']['values']
    keys, spans = [], {}
    for i, r in enumerate(rows, start=2):
        w = '%s line %d' % (WHERE, i)
        n = r['nation']
        if n not in nationalities:
            out.append((w, 'nation %r is not a code of data/nationalities.csv' % n))
        elif nationalities[n].get('kind') != 'nation':
            out.append((w, 'nation %s is not of kind nation (a multinational headquarters code has no allegiance)' % n))
        if r['side'] not in sides:
            out.append((w, 'side %r not in vocabulary allegiance_side %s' % (r['side'], sorted(sides))))
        if r['conflict'] not in conflicts:
            out.append((w, 'conflict %r not in vocabulary allegiance_conflict %s' % (r['conflict'], sorted(conflicts))))
        f, t = _date(r['valid_from']), _date(r['valid_to']) if r['valid_to'] else None
        if f is None:
            out.append((w, 'valid_from %r is not a real YYYY-MM-DD' % r['valid_from']))
        if r['valid_to'] and t is None:
            out.append((w, 'valid_to %r is not a real YYYY-MM-DD' % r['valid_to']))
        if f and t and t < f:
            out.append((w, 'valid_to %s is before valid_from %s' % (r['valid_to'], r['valid_from'])))
        span = CONFLICT_SPAN.get(r['conflict'])
        if span:
            if f and f < span[0]:
                out.append((w, 'valid_from %s is before the start of %s (%s)' % (r['valid_from'], r['conflict'], span[0])))
            if (t or f) and (t or f) > span[1]:
                out.append((w, 'the row runs past the end of %s (%s)' % (r['conflict'], span[1])))
        key = (n, r['valid_from'])
        if key in keys:
            out.append((w, 'duplicate key %s' % (key,)))
        keys.append(key)
        refs = [x for x in r['reference_ids'].split(';') if x]
        if not refs:
            out.append((w, 'reference_ids is empty'))
        for x in refs:
            if x not in ref_ids:
                out.append((w, 'reference_ids: %s is not in data/references_meta.csv' % x))
        if f:
            spans.setdefault((n, r['conflict']), []).append((f, t, w))
    if keys != sorted(keys):
        out.append((WHERE, 'rows must be sorted by nation, then valid_from'))
    for (n, c), lst in spans.items():
        lst.sort(key=lambda x: x[0])
        for (f1, t1, w1), (f2, t2, w2) in zip(lst, lst[1:]):
            if t1 is None:
                out.append((w2, 'row %s is open-ended, so %s overlaps it (nation %s, %s)' % (w1, w2, n, c)))
            elif f2 <= t1:
                out.append((w2, 'overlaps the row before it: valid_from %s is not after valid_to %s (nation %s, %s)' % (f2, t1, n, c)))
    covered = {r['nation'] for r in rows}
    for code, row in nationalities.items():
        if row.get('kind') == 'nation' and code not in covered:
            out.append((WHERE, 'nation %s has no allegiance row' % code))
    return out


def side_on(rows, nation, date, conflict='WW2'):
    """Side of a nation on a date (datetime.date or YYYY-MM-DD), or None where no row covers it."""
    d = _date(date) if isinstance(date, str) else date
    for r in rows:
        if r['nation'] != nation or r['conflict'] != conflict:
            continue
        f, t = _date(r['valid_from']), _date(r['valid_to']) if r['valid_to'] else None
        if f <= d and (t is None or d <= t):
            return r['side']
    return None


# ---- unit-level overrides (data/unit_allegiance_overrides.csv, schema/unit_allegiance_overrides.schema.json; 15 November 2026) ----
OVERRIDES_PATH = os.path.join(common.ROOT, 'data', 'unit_allegiance_overrides.csv')
OVERRIDES_WHERE = 'data/unit_allegiance_overrides.csv'


def overrides_header():
    return [f['name'] for f in common.load_schema('unit_allegiance_overrides')['fields']]


def load_overrides(path=OVERRIDES_PATH):
    return load(path)


def check_overrides(h, rows, units, vocabs, ref_ids):
    """units: {unit_id: row of data/units.csv}. Returns (where, message) problems."""
    out = []
    if h != overrides_header():
        out.append((OVERRIDES_WHERE, 'header %s != schema/unit_allegiance_overrides.schema.json %s' % (h, overrides_header())))
        return out
    sides = vocabs['allegiance_side']['values']
    lo, hi = CONFLICT_SPAN['WW2']
    keys, spans = [], {}
    for i, r in enumerate(rows, start=2):
        w = '%s line %d' % (OVERRIDES_WHERE, i)
        u = r['unit_id']
        if u not in units:
            out.append((w, 'unit_id %r is not a unit of data/units.csv' % u))
        if r['side'] not in sides:
            out.append((w, 'side %r not in vocabulary allegiance_side %s' % (r['side'], sorted(sides))))
        f, t = _date(r['valid_from']), _date(r['valid_to']) if r['valid_to'] else None
        if f is None:
            out.append((w, 'valid_from %r is not a real YYYY-MM-DD' % r['valid_from']))
        if r['valid_to'] and t is None:
            out.append((w, 'valid_to %r is not a real YYYY-MM-DD' % r['valid_to']))
        if f and t and t < f:
            out.append((w, 'valid_to %s is before valid_from %s' % (r['valid_to'], r['valid_from'])))
        if f and not lo <= f <= hi:
            out.append((w, 'valid_from %s is outside WW2 (%s to %s)' % (r['valid_from'], lo, hi)))
        if t and not lo <= t <= hi:
            out.append((w, 'valid_to %s is outside WW2 (%s to %s)' % (r['valid_to'], lo, hi)))
        key = (u, r['valid_from'])
        if key in keys:
            out.append((w, 'duplicate key %s' % (key,)))
        keys.append(key)
        refs = [x for x in r['reference_ids'].split(';') if x]
        if not refs:
            out.append((w, 'reference_ids is empty (an override needs a source)'))
        for x in refs:
            if x not in ref_ids:
                out.append((w, 'reference_ids: %s is not in data/references_meta.csv' % x))
        if f:
            spans.setdefault(u, []).append((f, t, w))
    if keys != sorted(keys):
        out.append((OVERRIDES_WHERE, 'rows must be sorted by unit_id, then valid_from'))
    for u, lst in spans.items():
        lst.sort(key=lambda x: x[0])
        for (f1, t1, w1), (f2, t2, w2) in zip(lst, lst[1:]):
            if t1 is None:
                out.append((w2, 'row %s is open-ended, so %s overlaps it (unit %s)' % (w1, w2, u)))
            elif f2 <= t1:
                out.append((w2, 'overlaps the row before it: valid_from %s is not after valid_to %s (unit %s)' % (f2, t1, u)))
    return out


class Resolver:
    """Side of a unit on a date: unit override, then the nation's allegiance, then None (a gap or an unknown nation).

    Built from the three tables (nationality name -> code through data/nationalities.csv). side(unit_id, date)
    takes a datetime.date or YYYY-MM-DD; camp(...) folds the side into 'Allied' (Allied and co-belligerent), 'Axis' or None
    (neutral, a gap) for the checks that ask whether two units fought on opposite sides.
    """

    def __init__(self, units, nationalities, nation_rows, override_rows):
        self.units = units
        self.code = {n['name']: n['code'] for n in nationalities}
        self.nation_rows = nation_rows
        self.over = {}
        for r in override_rows:
            self.over.setdefault(r['unit_id'], []).append(r)

    @classmethod
    def load(cls):
        units = {u['unit_id']: u for u in common.read_dicts(common.UNITS_CSV)[1]}
        return cls(units, common.load_nationalities(), load()[1], load_overrides()[1])

    def side(self, unit_id, date, conflict='WW2'):
        d = _date(date) if isinstance(date, str) else date
        if d is None:
            return None
        for r in self.over.get(unit_id, []):
            f, t = _date(r['valid_from']), _date(r['valid_to']) if r['valid_to'] else None
            if f <= d and (t is None or d <= t):
                return r['side']
        u = self.units.get(unit_id)
        code = self.code.get(u['nationality']) if u else None
        return side_on(self.nation_rows, code, d, conflict) if code else None

    def side_of_nationality(self, nationality, date, conflict='WW2'):
        d = _date(date) if isinstance(date, str) else date
        code = self.code.get(nationality)
        return side_on(self.nation_rows, code, d, conflict) if code and d else None

    @staticmethod
    def camp(side):
        return {'Allied': 'Allied', 'co-belligerent': 'Allied', 'Axis': 'Axis'}.get(side)
