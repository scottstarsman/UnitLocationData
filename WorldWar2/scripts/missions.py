#!/usr/bin/env python3
"""The missions table (decision J1, Normandy chunk 5, approved by Scott on 17 November 2026): one row per mission of a flying unit.

Files: data/missions/<nationality folder>/<unit_id>.csv (one file per flying unit, like data/claims/), columns from schema/missions.schema.json;
data/retired_missions.csv lists removed mission ids (never reused). scripts/build.py writes build/missions.csv (every row, sorted by
date then mission_id, with the derived columns of DERIVED). A mission is not a location claim: it never feeds build/all_claims.csv, the command
relations or the who_controls grid. scripts/validate.py checks the rows (check_missions); scripts/check_mission_ids.py checks id reuse across revisions.
Standard library only.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common  # noqa: E402

MISSIONS_DIR = os.path.join(common.ROOT, 'data', 'missions')
RETIRED_CSV = os.path.join(common.ROOT, 'data', 'retired_missions.csv')
RETIRED_HEADER = ['mission_id', 'replaced_by_mission_id', 'reason']
FIELDS = common.load_schema('missions')['fields']
HEADER = [f['name'] for f in FIELDS]
# derived columns of build/missions.csv, after the stored ones (from data/units.csv, data/places.csv and data/aircraft_types.csv)
DERIVED = ['unit_name', 'nationality', 'target_place_name', 'target_latitude', 'target_longitude', 'target_country', 'aircraft_designation']
BUILD_HEADER = HEADER + DERIVED


def files():
    """All mission csv paths under data/missions, sorted."""
    out = []
    for dirpath, _dirs, fs in os.walk(MISSIONS_DIR):
        for fn in fs:
            if fn.endswith('.csv'):
                out.append(os.path.join(dirpath, fn))
    return sorted(out)


def sort_key(r):
    return (r['date'], int(r['mission_id'][3:]) if r['mission_id'][3:].isdigit() else 0, r['mission_id'])


def load():
    """Every mission row as a dict (stored columns only, plus _path), sorted by date then mission_id."""
    rows = []
    for p in files():
        _h, ds = common.read_dicts(p)
        for d in ds:
            d['_path'] = p
        rows.extend(ds)
    rows.sort(key=sort_key)
    return rows


def retired():
    return common.read_dicts(RETIRED_CSV)[1] if os.path.isfile(RETIRED_CSV) else []


def build_rows():
    """Rows (lists) of build/missions.csv."""
    units = {u['unit_id']: u for u in common.read_dicts(common.UNITS_CSV)[1]}
    places = {p['place_id']: p for p in common.read_dicts(os.path.join(common.ROOT, 'data', 'places.csv'))[1]}
    at_path = os.path.join(common.ROOT, 'data', 'aircraft_types.csv')
    types = {t['type_id']: t for t in common.read_dicts(at_path)[1]} if os.path.isfile(at_path) else {}
    out = []
    for r in load():
        u = units.get(r['unit_id'], {})
        p = places.get(r['target_place_id'], {})
        t = types.get(r['aircraft_type_id'], {})
        out.append([r.get(c, '') for c in HEADER] + [u.get('unit_name', ''), u.get('nationality', ''), p.get('name', ''), p.get('latitude', ''),
                                                       p.get('longitude', ''), p.get('country', ''), t.get('designation', '')])
    return out
