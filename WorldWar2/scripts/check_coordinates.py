#!/usr/bin/env python3
"""Coordinate sanity checks. WARNINGS ONLY: this script always exits 0 unless --strict is given.

It exists because a coordinate can pass every schema check and still be wrong (a point 10 km from
the place the row names, or a point at one end of a front line). Standard library only.

Offline checks (always run):
  1. bbox      the point lies inside a loose bounding box for the row's theater
  2. same-name rows that share a location_name but whose points are more than 3 km apart
  3. conflict  claims in one conflict group whose points are farther apart than their precision radii
               add up (a real place disagreement is allowed, but it should be deliberate and noted)
  4. speed     a unit's consecutive preferred rows imply more than 80 km/day (a likely wrong point or date). The days are counted
               between the dates the coordinates belong to (location_date when set, otherwise the row date), so a point taken from
               a command-post list nine days earlier is not compared as if it were the position on the row date.

Explained exceptions: data/coordinate_exceptions.csv lists warnings that were checked and are correct (columns: check,
claim_id, other_claim_id, reason, source). A listed warning is printed as EXPLAINED and counted separately; it is not an open
warning and does not fail --strict. An entry that no longer matches any warning is reported as STALE so the file does not rot.
Keys: speed = the later claim_id and the earlier one; conflict = the group's first claim_id and the other; same-name = the first
claim_id and the other. Add an entry only with a reason that cites a source.

Optional online check (--geocode, needs network, uses OpenStreetMap Nominatim at 1 request/second):
  5. geocode   no geocode candidate for the place named in location_name lies within max(15 km, 2 x precision_km)
               of the point. Up to 10 candidates are fetched per name (many French place names exist more than once)
               and the nearest counts. Add --country fr to restrict candidates to one country (ISO code).
               Results are cached in .cache/geocode.json. Use --limit N to try a few rows first.
               Respect the Nominatim usage policy; do not run this in CI.

Usage: python scripts/check_coordinates.py [--geocode [--country fr] [--limit N]] [--strict]
"""
import json
import math
import os
import re
import sys
import time
import urllib.parse
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common  # noqa: E402

BBOX = {  # theater -> (lat_min, lat_max, lon_min, lon_max); loose, only to catch typos and sign errors
    'western_europe': (35.0, 62.0, -12.0, 25.0),
    'mediterranean': (28.0, 48.0, -10.0, 40.0),
    'north_africa': (15.0, 38.0, -20.0, 40.0),
    'eastern_front': (40.0, 72.0, 10.0, 70.0),
    'pacific': (-50.0, 60.0, 90.0, 180.0),
    'cbi': (0.0, 40.0, 60.0, 125.0),
}
SAME_NAME_KM = 3.0
SPEED_KM_PER_DAY = 80.0
CACHE = os.path.join(common.ROOT, '.cache', 'geocode.json')
EXCEPTIONS_CSV = os.path.join(common.ROOT, 'data', 'coordinate_exceptions.csv')


def load_exceptions():
    """Return {(check, claim_id, other_claim_id): (reason, source)} from data/coordinate_exceptions.csv (empty if absent)."""
    out = {}
    if os.path.isfile(EXCEPTIONS_CSV):
        _h, rows = common.read_dicts(EXCEPTIONS_CSV)
        for r in rows:
            if not r['reason'].strip():
                print('WARNING [exceptions] %s %s/%s has no reason; it is ignored' % (r['check'], r['claim_id'], r['other_claim_id']))
                continue
            out[(r['check'], r['claim_id'], r['other_claim_id'])] = (r['reason'], r['source'])
    return out


def km(a_lat, a_lon, b_lat, b_lon):
    r = 6371.0
    p1, p2 = math.radians(a_lat), math.radians(b_lat)
    dp, dl = p2 - p1, math.radians(b_lon - a_lon)
    h = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(h))


def pt(r):
    return float(r['latitude']), float(r['longitude'])


def place_query(name):
    """Pick the place to geocode from a location_name: the '(point = X)' part, else the first segment."""
    m = re.search(r'point\s*=\s*([^);]+)', name)
    if m:
        q = m.group(1)
    else:
        q = re.split(r'[/(]', name)[0]
    return q.strip(' ,;')


def geocode(q, cache, country=None):
    """Return a list of [lat, lon] candidates for place name q (cached; empty list if none)."""
    key = q + '|' + (country or '')
    if key in cache:
        return cache[key]
    params = {'q': q, 'format': 'json', 'limit': 10}
    if country:
        params['countrycodes'] = country
    url = 'https://nominatim.openstreetmap.org/search?' + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={'User-Agent': 'ww2-unit-locations-coordinate-check/1.0'})
    try:
        with urllib.request.urlopen(req, timeout=20) as f:
            data = json.load(f)
    except Exception as e:  # network trouble is not a data problem
        print('  (geocode failed for %r: %s)' % (q, e))
        return None
    cache[key] = [[float(d['lat']), float(d['lon'])] for d in data]
    time.sleep(1.1)
    return cache[key]


def main(argv):
    do_geo = '--geocode' in argv
    strict = '--strict' in argv
    limit = None
    if '--limit' in argv:
        limit = int(argv[argv.index('--limit') + 1])
    country = argv[argv.index('--country') + 1] if '--country' in argv else None
    _h, rows = common.load_all_claims()
    warns = []
    explained = []
    exceptions = load_exceptions()
    used = set()

    def warn(kind, r, msg, other=None):
        key = (kind, r['claim_id'], other or '')
        if key in exceptions:
            used.add(key)
            explained.append((kind, '%s %s: %s [%s]' % (r['claim_id'], r['unit_id'], msg, exceptions[key][0])))
            return
        warns.append((kind, '%s %s: %s' % (r['claim_id'], r['unit_id'], msg)))

    for r in rows:
        lat, lon = pt(r)
        b = BBOX.get(r['theater'])
        if b and not (b[0] <= lat <= b[1] and b[2] <= lon <= b[3]):
            warn('bbox', r, 'point %.4f,%.4f is outside the bounding box for theater %s' % (lat, lon, r['theater']))

    by_name = {}
    for r in rows:
        by_name.setdefault(r['location_name'], []).append(r)
    for name, rs in by_name.items():
        for i in range(len(rs)):
            for j in range(i + 1, len(rs)):
                d = km(*pt(rs[i]), *pt(rs[j]))
                if d > SAME_NAME_KM:
                    warn('same-name', rs[i], 'location_name %r also used by %s %.1f km away' % (name, rs[j]['claim_id'], d), rs[j]['claim_id'])

    groups = {}
    for r in rows:
        if r['conflict_group_id']:
            groups.setdefault(r['conflict_group_id'], []).append(r)
    for g, rs in groups.items():
        for i in range(len(rs)):
            for j in range(i + 1, len(rs)):
                d = km(*pt(rs[i]), *pt(rs[j]))
                reach = float(rs[i]['precision_km']) + float(rs[j]['precision_km'])
                if d > reach:
                    warn('conflict', rs[i], 'group %s: %s is %.1f km away, more than the %.0f km the two precision radii allow' % (
                        g, rs[j]['claim_id'], d, reach), rs[j]['claim_id'])

    by_unit = {}
    for r in rows:
        if r['claim_status'] == 'preferred':
            by_unit.setdefault(r['unit_id'], []).append(r)
    import datetime
    for uid, rs in by_unit.items():
        rs.sort(key=lambda r: (r['date'], r['claim_id']))
        for a, b in zip(rs, rs[1:]):
            da, db = a['location_date'] or a['date'], b['location_date'] or b['date']
            days = (datetime.date.fromisoformat(db) - datetime.date.fromisoformat(da)).days
            if days <= 0:
                continue
            d = km(*pt(a), *pt(b))
            if d / days > SPEED_KM_PER_DAY:
                warn('speed', b, '%.0f km from %s in %d day(s) = %.0f km/day' % (d, a['claim_id'], days, d / days), a['claim_id'])

    if do_geo:
        cache = {}
        if os.path.isfile(CACHE):
            cache = json.load(open(CACHE, encoding='utf-8'))
        n = 0
        notfound = set()
        for r in rows:
            q = place_query(r['location_name'])
            if not q:
                continue
            if limit is not None and n >= limit:
                break
            n += 1
            cands = geocode(q, cache, country)
            if cands:
                d = min(km(*pt(r), c[0], c[1]) for c in cands)
                if d > max(15.0, 2 * float(r['precision_km'])):
                    warn('geocode', r, 'nearest of %d geocode candidates for %r is %.1f km from the point; location_name or coordinates may be wrong' % (len(cands), q, d))
            elif cands is not None:
                notfound.add(q)
        if notfound:
            print('Not geocoded (no candidates, not checked): %s' % ', '.join(sorted(notfound)))
        os.makedirs(os.path.dirname(CACHE), exist_ok=True)
        json.dump(cache, open(CACHE, 'w', encoding='utf-8'), indent=1, ensure_ascii=False)

    for kind, msg in sorted(explained):
        print('EXPLAINED [%s] %s' % (kind, msg))
    for key in sorted(set(exceptions) - used):
        print('STALE [exceptions] %s %s/%s matches no current warning; remove it from data/coordinate_exceptions.csv' % key)
    for kind, msg in sorted(warns):
        print('WARNING [%s] %s' % (kind, msg))
    print('\n%d coordinate warning(s) and %d explained exception(s) over %d rows%s. Warnings are prompts to check a row, not errors.' % (
        len(warns), len(explained), len(rows), ' (with geocode)' if do_geo else ' (offline checks only)'))
    return 1 if (strict and warns) else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
