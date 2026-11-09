#!/usr/bin/env python3
"""Coordinate sanity checks. WARNINGS ONLY: this script always exits 0 unless --strict is given.

It exists because a coordinate can pass every schema check and still be wrong (a point 10 km from
the place the row names, or a point at one end of a front line). Standard library only.

Offline checks (always run):
  1. bbox      the point lies inside a loose bounding box for the row's theater
  1b. atlantic the point (a claim's or a place's) lies in open water west of Brittany, Cornwall and the Bay of Biscay (ATLANTIC boxes below; a typo or sign error)
  2. same-place claims of one place (place_id) whose points are more than 3 km from the place's point (the validator already requires equality or a
               coord_override within 5 km; this flags overrides that are far enough to deserve a look)
  3. conflict  claims in one conflict group whose points are farther apart than their precision radii
               add up (a real place disagreement is allowed, but it should be deliberate and noted)
  4. speed     a unit's consecutive preferred rows imply more than 80 km/day (a likely wrong point or date). The days are counted
               between the dates the coordinates belong to (location_date when set, otherwise the row date), so a point taken from
               a command-post list nine days earlier is not compared as if it were the position on the row date.

  6. override  a claim point that does not match its place (place_id): a claim with a coord_override whose point is farther from the place point than the claim's own
               precision_km (the override is meant to refine the point inside its precision, not to move it), or a claim without a coord_override whose point is
               not the place point at all (more than 50 m; the validator also rejects that, this keeps the script useful alone). Offline, always run.
  7. place-geocoder  a place point that is farther than max(15 km, 2 x precision_km) from EVERY geocoder candidate already stored for its name in the cache
               (.cache/geocode.json, written by --geocode and --places; keys are the place name and the country code of the place, for example 'Sées, Orne|fr').
               Offline: it reads the cache and never fetches, so on a machine without the cache (CI) it checks nothing and prints how many places had a stored result.
               It is what finds a point that is a street, a shop or the wrong town of the same name (V-003, V-004, V-015 to V-017 of docs/review/verification_results.md).
               A place with no stored result is not checked. --places fills the cache for every place (needs network).

Explained exceptions: data/coordinate_exceptions.csv lists warnings that were checked and are correct (columns: check,
claim_id, other_claim_id, reason, source). A listed warning is printed as EXPLAINED and counted separately; it is not an open
warning and does not fail --strict. An entry that no longer matches any warning is reported as STALE so the file does not rot.
Keys: speed = the later claim_id and the earlier one; conflict = the group's first claim_id and the other; same-place = the claim_id
and blank; atlantic = the claim_id (or the place_id for a place) and blank; place-geocoder = the lowest claim_id of a claim at the place, given twice (both key columns are foreign keys to claims, and the table has no column for a place id). Add an entry only with a reason that cites a source.

Optional online check (--geocode, needs network, uses OpenStreetMap Nominatim at 1 request/second):
  5. geocode   no geocode candidate for the place named in location_name (the place name and qualifier, derived) lies within max(15 km, 2 x precision_km)
               of the point. Up to 10 candidates are fetched per name (many French place names exist more than once)
               and the nearest counts. Add --country fr to restrict candidates to one country (ISO code).
               Results are cached in .cache/geocode.json. Use --limit N to try a few rows first.
               Respect the Nominatim usage policy; do not run this in CI.

--duplicates lists pairs of places of kind point within 1 km of each other (possible duplicates: one town under two names); it is
informational, never a warning, and is how the review list of ambiguous merges in docs/changelog.md was produced.

The three speed warnings that remain open (C0253, C0419, C0480) are single-day moves of 127 to 225 km that are not explained in data/coordinate_exceptions.csv:
they are prompts to re-check the two dates or the two points of each pair, not known errors; they were already open before checks 6 and 7 were added.

Usage: python scripts/check_coordinates.py [--geocode [--country fr] [--limit N]] [--places [--limit N]] [--cache PATH] [--strict] [--duplicates]
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
import places as placesmod  # noqa: E402

BBOX = {  # theater -> (lat_min, lat_max, lon_min, lon_max); loose, only to catch typos and sign errors
    'western_europe': (35.0, 62.0, -12.0, 25.0),
    'mediterranean': (28.0, 48.0, -10.0, 40.0),
    'north_africa': (15.0, 38.0, -20.0, 40.0),
    'eastern_front': (40.0, 72.0, 10.0, 70.0),
    'balkans': (34.0, 47.5, 13.0, 30.0),
    'scandinavia': (54.0, 72.0, 4.0, 32.0),
    'home_germany': (45.5, 56.0, 5.5, 24.0),   # the Reich of 1937 plus Austria, the Sudetenland, the Protectorate and the annexed Polish areas
    'pacific': (-50.0, 60.0, 90.0, 180.0),
    'cbi': (0.0, 40.0, 60.0, 125.0),
}
# (lat_min, lat_max, lon_min, lon_max) of open Atlantic: west of Brittany and the Bay of Biscay, and west of Cornwall / the Scilly Isles.
# Loose on purpose: it must not touch Brittany (west tip 4.8 W), Cornwall (5.7 W) or Ireland (north of 51 N).
ATLANTIC = [(43.0, 48.9, -20.0, -5.3), (48.9, 50.7, -20.0, -6.4)]
SAME_PLACE_KM = 3.0
SPEED_KM_PER_DAY = 80.0
CACHE = os.path.join(common.ROOT, '.cache', 'geocode.json')
OVERRIDE_TOLERANCE_KM = 0.05   # a claim without coord_override must sit on its place point (50 m for the rounding of the coordinates)
PLACE_GEOCODER_MIN_KM = 15.0   # a place point is far from the stored geocoder candidates beyond max(this, 2 x precision_km)
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
    do_places = '--places' in argv
    cache_path = argv[argv.index('--cache') + 1] if '--cache' in argv else CACHE
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

    places = placesmod.load()
    for r in rows:
        lat, lon = pt(r)
        if any(b[0] <= lat <= b[1] and b[2] <= lon <= b[3] for b in ATLANTIC):
            warn('atlantic', r, 'point %.4f,%.4f is in the open Atlantic' % (lat, lon))
        p = places.by_id.get(r['place_id'])
        if p:
            d = km(lat, lon, float(p['latitude']), float(p['longitude']))
            if d > SAME_PLACE_KM:
                warn('same-place', r, 'place %s %r: the claim point is %.1f km from the place point' % (p['place_id'], p['name'], d))
            if r['coord_override'].strip():
                if d > float(r['precision_km']):
                    warn('override', r, 'place %s %r: the coord_override point is %.2f km from the place point, more than the claim precision of %s km' % (
                        p['place_id'], p['name'], d, r['precision_km']))
            elif d > OVERRIDE_TOLERANCE_KM:
                warn('override', r, 'place %s %r: the claim point is %.2f km from the place point and there is no coord_override' % (p['place_id'], p['name'], d))
    for p in places.rows:
        lat, lon = float(p['latitude']), float(p['longitude'])
        if any(b[0] <= lat <= b[1] and b[2] <= lon <= b[3] for b in ATLANTIC):
            warns.append(('atlantic', '%s %s: place point %.4f,%.4f is in the open Atlantic' % (p['place_id'], p['name'], lat, lon)))

    # 7. place-geocoder: places whose point is far from every stored geocoder candidate (cache only, no network unless --places)
    gcache = {}
    if os.path.isfile(cache_path):
        gcache = json.load(open(cache_path, encoding='utf-8'))
    checked = 0
    fetched = 0
    compared = set()   # exception keys of the places that had a stored result (an exception for another place is not stale, only unchecked)
    for p in places.rows:
        if p['kind'] != 'point':   # the name of a line or an area ('Vire / Elle front near Airel') is not a place a geocoder knows
            continue
        q = place_query(p['name'])
        cc = (p.get('country') or '').lower()
        cands = None
        for key in (q + '|' + cc, q + '|'):
            if gcache.get(key):
                cands = gcache[key]
                break
        if cands is None and do_places and p['kind'] == 'point' and q and (limit is None or fetched < limit):
            fetched += 1
            cands = geocode(q, gcache, cc or None)
            if cands is not None:
                json.dump(gcache, open(cache_path, 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
        if not cands:
            continue
        checked += 1
        lat, lon = float(p['latitude']), float(p['longitude'])
        d = min(km(lat, lon, c[0], c[1]) for c in cands)
        at_place = sorted(r['claim_id'] for r in rows if r['place_id'] == p['place_id'])
        key = ('place-geocoder', at_place[0] if at_place else '', at_place[0] if at_place else '')
        compared.add(key)
        if d > max(PLACE_GEOCODER_MIN_KM, 2 * float(p['precision_km'])):
            msg = '%s %s: the place point is %.1f km from the nearest of %d stored geocoder candidates for %r (precision %s km); the point or the name may be wrong' % (
                p['place_id'], p['name'], d, len(cands), q, p['precision_km'])
            if key in exceptions:
                used.add(key)
                explained.append(('place-geocoder', '%s [%s]' % (msg, exceptions[key][0])))
            else:
                warns.append(('place-geocoder', msg))

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
        if os.path.isfile(cache_path):
            cache = json.load(open(cache_path, encoding='utf-8'))
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
        os.makedirs(os.path.dirname(cache_path), exist_ok=True)
        json.dump(cache, open(cache_path, 'w', encoding='utf-8'), indent=1, ensure_ascii=False)

    if '--duplicates' in argv:
        pts = [p for p in places.rows if p['kind'] == 'point']
        for i in range(len(pts)):
            for j in range(i + 1, len(pts)):
                d = km(float(pts[i]['latitude']), float(pts[i]['longitude']), float(pts[j]['latitude']), float(pts[j]['longitude']))
                if d <= 1.0:
                    print('DUPLICATE? %s %r and %s %r are %.0f m apart' % (pts[i]['place_id'], pts[i]['name'], pts[j]['place_id'], pts[j]['name'], d * 1000))
    for kind, msg in sorted(explained):
        print('EXPLAINED [%s] %s' % (kind, msg))
    for key in sorted(set(exceptions) - used):
        if key[0] == 'place-geocoder' and key not in compared:
            continue   # no stored geocoder result for this place on this machine (no cache): not checked, not stale
        print('STALE [exceptions] %s %s/%s matches no current warning; remove it from data/coordinate_exceptions.csv' % key)
    for kind, msg in sorted(warns):
        print('WARNING [%s] %s' % (kind, msg))
    print('place-geocoder: %d of %d places had a stored geocoder result to compare with%s.' % (
        checked, len(places.rows), '' if checked else ' (no cache: run with --places to fill it)'))
    print('\n%d coordinate warning(s) and %d explained exception(s) over %d rows%s. Warnings are prompts to check a row, not errors.' % (
        len(warns), len(explained), len(rows), ' (with geocode)' if (do_geo or do_places) else ' (offline checks only)'))
    return 1 if (strict and warns) else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
