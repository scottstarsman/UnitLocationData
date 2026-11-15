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
CONFLICT_SPAN = {'WW2': (datetime.date(1939, 9, 1), datetime.date(1945, 9, 2))}


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
