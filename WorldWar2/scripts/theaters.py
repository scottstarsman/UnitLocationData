#!/usr/bin/env python3
"""Two-level WWII theater vocabulary (schema/theaters.json).

This module is the single place scripts should go for theater codes, sub-theater
codes, per-theater date floors, and bounding boxes. The allowed values of the
`theater` column remain the `theater` vocabulary in schema/vocabularies.json;
the allowed values of the optional `sub_theater` column are the `sub_theater`
vocabulary. Both must stay in sync with this file (validate_vocab checks that).

Standard library only.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common  # noqa: E402

THEATERS_JSON = os.path.join(common.SCHEMA_DIR, 'theaters.json')

_CACHE = None


def load():
    """Return the theaters.json document (cached for the process)."""
    global _CACHE
    if _CACHE is None:
        _CACHE = common.load_json(THEATERS_JSON)
    return _CACHE


def clear_cache():
    """Drop the cached document (for tests that rewrite the file)."""
    global _CACHE
    _CACHE = None


def entries():
    return load()['theaters']


def by_code():
    return {t['code']: t for t in entries()}


def get(code):
    """Return the vocabulary entry for code, or None."""
    if not code:
        return None
    return by_code().get(code)


def global_date_floor():
    return load()['global_date_floor']


def global_date_ceiling():
    return load()['global_date_ceiling']


def theater_codes():
    """Codes allowed in the `theater` column, in file order."""
    return [t['code'] for t in entries() if t.get('allowed_as_theater')]


def split_theater_codes(value):
    """Split a theater cell into codes. A single code is a one-item list; pipes separate multiple codes.

    This does not validate tokens (see theater_list_error). Empty input yields an empty list.
    """
    if not value:
        return []
    return value.split('|')


def theater_list_error(value):
    """Error message if a units.csv theater cell is not one or more valid pipe-separated theater codes, else None.

    Empty is left to the required-field check. Tokens must be non-empty, unique, free of surrounding
    whitespace, and in the theater vocabulary. A single allowed code remains valid.
    """
    if not value:
        return None
    parts = value.split('|')
    if any(p == '' for p in parts):
        return 'theater has an empty token (do not write a leading, trailing or doubled pipe)'
    if any(p != p.strip() for p in parts):
        return 'theater tokens must not have spaces around the pipe'
    allowed = set(theater_codes())
    seen = set()
    for p in parts:
        if p not in allowed:
            return 'theater token %r not in the theater vocabulary' % p
        if p in seen:
            return 'theater lists %r more than once' % p
        seen.add(p)
    return None


def sub_theater_codes():
    """Codes allowed in the optional `sub_theater` column, in file order."""
    return [t['code'] for t in entries() if t['level'] == 'sub_theater']


def top_level_codes():
    return [t['code'] for t in entries() if t['level'] == 'theater']


def parent_of(code):
    t = get(code)
    return t['parent'] if t else None


def top_level(code):
    """The top-level theater of a theater or sub-theater code; None if unknown."""
    t = get(code)
    if t is None:
        return None
    if t['level'] == 'theater':
        return t['code']
    return t['parent']


def is_under(code, ancestor):
    """True if code is ancestor, or a sub-theater of ancestor."""
    if not code or not ancestor:
        return False
    if code == ancestor:
        return True
    return top_level(code) == ancestor or parent_of(code) == ancestor


def date_floor(code):
    """Earliest YYYY-MM-DD accepted for a row in this theater or sub-theater.

    Unknown or blank codes fall back to the global floor (7 July 1937).
    A pipe-separated units.csv theater list uses the earliest (most permissive) floor among its codes.
    """
    if code and '|' in code:
        floors = [date_floor(c) for c in code.split('|') if c]
        return min(floors) if floors else global_date_floor()
    t = get(code)
    if t and t.get('date_floor'):
        return t['date_floor']
    return global_date_floor()


def before_floor(date, code):
    """True if date (YYYY, YYYY-MM or YYYY-MM-DD) is earlier than the floor for code."""
    if not date:
        return False
    floor = date_floor(code)
    return date < floor[:len(date)]


def bboxes(code):
    """List of [lat_min, lat_max, lon_min, lon_max] boxes for typo checks.

    A sub-theater uses its own boxes. A top-level theater uses its own boxes
    (which may already be a union, including both sides of the antimeridian).
    A pipe-separated units.csv theater list is the union of its codes' boxes.
    Unknown codes return an empty list (the caller skips the bbox check).
    """
    if code and '|' in code:
        boxes = []
        for c in code.split('|'):
            boxes.extend(bboxes(c))
        return boxes
    t = get(code)
    if not t:
        return []
    return list(t.get('bboxes') or [])


def in_bboxes(lat, lon, boxes):
    for b in boxes:
        if b[0] <= lat <= b[1] and b[2] <= lon <= b[3]:
            return True
    return False


def is_open_water_theater(code):
    """True if a mid-ocean point is expected (skip the Atlantic typo check)."""
    if not code:
        return False
    if '|' in code:
        return any(is_open_water_theater(c) for c in code.split('|') if c)
    return is_under(code, 'atlantic') or is_under(code, 'arctic')


def sub_theater_error(theater, sub):
    """Return an error message if theater/sub_theater are inconsistent, else None.

    Blank sub_theater is always allowed. A set sub_theater must be a vocabulary
    sub-theater. If theater is a top-level code, sub must be a child of it. If
    theater is itself a legacy sub-theater code (north_africa, balkans,
    scandinavia, home_germany), sub must be blank or equal to theater.
    A pipe-separated units.csv theater list is valid when the sub-theater is
    consistent with at least one listed theater code.
    """
    if not sub:
        return None
    st = get(sub)
    if st is None or st['level'] != 'sub_theater':
        return 'sub_theater %r is not in the sub-theater vocabulary' % sub
    if not theater:
        return 'sub_theater %s is set but theater is blank' % sub
    if '|' in theater:
        codes = [c for c in theater.split('|') if c]
        if any(sub_theater_error(c, sub) is None for c in codes):
            return None
        return ('sub_theater %s is not a sub-theater of any theater in %s'
                % (sub, theater))
    th = get(theater)
    if th is None:
        return 'theater %r is not in the theater vocabulary' % theater
    if th['level'] == 'sub_theater':
        if sub != theater:
            return ('sub_theater %s does not match theater %s (a legacy sub-theater '
                    'used as theater leaves sub_theater blank, or equal to the theater code)'
                    % (sub, theater))
        return None
    if st['parent'] != theater:
        return 'sub_theater %s is not a sub-theater of theater %s (parent is %s)' % (
            sub, theater, st['parent'])
    return None


def vocab_sync_errors():
    """Errors if vocabularies.json is out of sync with theaters.json."""
    vocabs = common.load_vocabularies()
    errs = []
    have_th = set(vocabs['theater']['values'])
    want_th = set(theater_codes())
    if have_th != want_th:
        errs.append('vocabulary theater values %s != theaters.json allowed_as_theater codes %s'
                    % (sorted(have_th), sorted(want_th)))
    have_sub = set(vocabs.get('sub_theater', {}).get('values', []))
    want_sub = set(sub_theater_codes())
    if have_sub != want_sub:
        errs.append('vocabulary sub_theater values %s != theaters.json sub-theater codes %s'
                    % (sorted(have_sub), sorted(want_sub)))
    return errs


def structure_errors():
    """Structural checks of theaters.json itself."""
    doc = load()
    errs = []
    if doc.get('global_date_floor') != '1937-07-07':
        errs.append('global_date_floor is %r, expected 1937-07-07' % doc.get('global_date_floor'))
    seen = set()
    by = {}
    for t in entries():
        code = t.get('code')
        if not code:
            errs.append('a theater entry has no code')
            continue
        if code in seen:
            errs.append('duplicate theater code %s' % code)
        seen.add(code)
        by[code] = t
        if t.get('level') not in ('theater', 'sub_theater'):
            errs.append('%s: level %r' % (code, t.get('level')))
        if t.get('level') == 'theater' and t.get('parent'):
            errs.append('%s: a top-level theater must have a blank parent' % code)
        if t.get('level') == 'sub_theater' and not t.get('parent'):
            errs.append('%s: a sub-theater must have a parent' % code)
        if not t.get('bboxes'):
            errs.append('%s: missing bboxes' % code)
        else:
            for b in t['bboxes']:
                if len(b) != 4 or not (b[0] < b[1] and b[2] < b[3]):
                    errs.append('%s: bad bbox %s' % (code, b))
        if not t.get('date_floor') or not t.get('start_date'):
            errs.append('%s: missing date_floor or start_date' % code)
        elif t['date_floor'] > t['start_date']:
            errs.append('%s: date_floor %s is after start_date %s' % (code, t['date_floor'], t['start_date']))
        if t.get('allowed_as_theater') is None:
            errs.append('%s: allowed_as_theater is required' % code)
    for t in entries():
        p = t.get('parent')
        if p:
            if p not in by:
                errs.append('%s: parent %s is not in the vocabulary' % (t['code'], p))
            elif by[p].get('level') != 'theater':
                errs.append('%s: parent %s is not a top-level theater (only two levels are used)'
                            % (t['code'], p))
    return errs


def validate_vocab():
    """All vocabulary errors (structure + sync with vocabularies.json)."""
    return structure_errors() + vocab_sync_errors()
