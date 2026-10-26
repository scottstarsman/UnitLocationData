"""Places table (data/places.csv) and the values derived from it and from other claim columns. Standard library only.

A place is a named location that claims point at (`claims.place_id`): a settlement or site (kind point), a named area, sector, beach or zone
(kind area) or a front, axis or route (kind line). Its coordinate is the one point every claim at the place uses; a claim that uses a different
point (another geocoder read of the same place, an approximate point) says so in `coord_override`. See schema/README.md, "places columns".
A place id is never reused. When two places turn out to be one, the survivor keeps its id and the other id is retired: it leaves data/places.csv, no
claim may use it, and data/place_merges.csv records which place it became (`load_merges`, `resolve`), so an old reference to the id can be resolved.

Values that used to be claim columns and are now derived (never stored in the claim files):
  location_name                   the place name with the claim's `location_qualifier` (see display_name)
  location_temporal_offset_days   location_date minus date, in days (blank when location_date is blank)
  strength_status                 destroyed when the claim's `destroyed` flag is true, else the `status` key of strength_json, else unknown
  coordinate source               the claim's `source` no longer ends with '; coords: <note>': the place carries coord_reference_id and
                                  coord_source_note; a claim with coord_override carries its own note there
  claim_reference_roles rows for gazetteer_geocoder references: role `location` (see build_references.py)
"""
import datetime
import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common  # noqa: E402

PLACES_CSV = os.path.join(common.ROOT, 'data', 'places.csv')
MERGES_CSV = os.path.join(common.ROOT, 'data', 'place_merges.csv')
MERGES_HEADER = ['retired_place_id', 'merged_into_place_id', 'retired_name', 'note']
HEADER = ['place_id', 'name', 'alt_names', 'kind', 'latitude', 'longitude', 'precision_km', 'country', 'region', 'coord_reference_id', 'coord_source_note']
VICINITY = 'vicinity'   # reserved first token of a location_qualifier: the claim says "vicinity of <place>"
DERIVED_PLACE = ['place_name', 'country', 'region', 'coord_reference_id', 'coord_source_note']   # place columns carried to build/all_claims.csv
DERIVED_CLAIM = ['location_name', 'location_temporal_offset_days', 'strength_status']


def km(a_lat, a_lon, b_lat, b_lon):
    r = 6371.0
    p1, p2 = math.radians(a_lat), math.radians(b_lat)
    dp, dl = p2 - p1, math.radians(b_lon - a_lon)
    h = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(h))


class Places:
    def __init__(self, rows):
        self.rows = rows
        self.by_id = {r['place_id']: r for r in rows}


def load():
    if not os.path.isfile(PLACES_CSV):
        return Places([])
    return Places(common.read_dicts(PLACES_CSV)[1])


def load_merges():
    """Rows of data/place_merges.csv as dicts (empty when the file is absent): the place ids that were retired by merging two places."""
    if not os.path.isfile(MERGES_CSV):
        return []
    return common.read_dicts(MERGES_CSV)[1]


def resolve(place_id, merges=None):
    """The place id a (possibly retired) id now stands for: follows data/place_merges.csv until an id that was not merged away."""
    m = {r['retired_place_id']: r['merged_into_place_id'] for r in (load_merges() if merges is None else merges)}
    seen = set()
    while place_id in m and place_id not in seen:
        seen.add(place_id)
        place_id = m[place_id]
    return place_id


def display_name(place_name, qualifier):
    """The old free-text location_name: 'vicinity of <place>' when the qualifier starts with the reserved token `vicinity`, then the rest of the
    qualifier in parentheses ('Brest, Finistère (departure area)')."""
    q = qualifier or ''
    pre = ''
    if q == VICINITY or q.startswith(VICINITY + '; '):
        pre = 'vicinity of '
        q = q[len(VICINITY) + 2:] if q != VICINITY else ''
    s = pre + place_name
    if q:
        s += ' (%s)' % q
    return s


def temporal_offset(row):
    """location_date - date in whole days as text, '' when location_date is blank or either date is invalid."""
    ld = row.get('location_date', '')
    if not ld:
        return ''
    try:
        return str((datetime.date.fromisoformat(ld) - datetime.date.fromisoformat(row['date'])).days)
    except ValueError:
        return ''


def strength_status(row):
    """destroyed when the destroyed flag is true; else the status key of strength_json (full, reduced, heavily_depleted); else unknown."""
    if row.get('destroyed') == 'true':
        return 'destroyed'
    s = row.get('strength_json', '')
    if s:
        try:
            d = json.loads(s)
        except ValueError:
            return 'unknown'
        if isinstance(d, dict) and d.get('status'):
            return d['status']
    return 'unknown'


def attach(rows, places=None):
    """Add the derived keys to every claim dict: location_name, location_temporal_offset_days, strength_status and the place columns
    (place_name, country, region, coord_reference_id, coord_source_note; blank when place_id does not resolve). Returns rows."""
    places = places or load()
    for r in rows:
        p = places.by_id.get(r.get('place_id', ''))
        r['place_name'] = p['name'] if p else ''
        for k in ('country', 'region', 'coord_reference_id', 'coord_source_note'):
            r[k] = p[k] if p else ''
        r['location_name'] = display_name(r['place_name'], r.get('location_qualifier', '')) if p else ''
        r['location_temporal_offset_days'] = temporal_offset(r)
        r['strength_status'] = strength_status(r)
    return rows
