#!/usr/bin/env python3
"""Derived spatial metadata and all-domain claim counts for operations (Task 2, OB1, OB4, OB5).

build/operations.csv is the derived view of data/operations.csv: path, depth, all-domain claim and
mission counts (with preferred and per-domain breakdowns), the sourced primary_place_id, and a
computed extent (median, bbox, 80th-percentile radius, quality). Centroids are published only when
extent_quality is focal or compact. build/operations.geojson carries a Point for those rows
(primary place if set, otherwise the centroid) and null geometry for broad or empty extents.
Standard library only.
"""
import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common  # noqa: E402
import operations  # noqa: E402

# Preferred claims only. HQ rows and points 200 km or more from the first median are dropped
# before the published median, radius and bbox are recomputed (OB5).
OUTLIER_KM = 200.0
FOCAL_RADIUS_KM = 50.0
BROAD_RADIUS_KM = 100.0
FOCAL_PLACE_SHARE = 0.40
EARTH_KM = 6371.0
HQ_REPRESENTS = frozenset({'headquarters', 'headquarters_area'})
HQ_EVENTS = frozenset({'hq_observation', 'hq_move'})

BUILD_HEADER = [
    'operation_id', 'name', 'short_name', 'alt_names', 'op_type', 'parent_operation_id', 'operation_path', 'depth',
    'start_date', 'end_date', 'date_basis', 'nationality_scope',
    'claims_direct', 'claims_direct_preferred',
    'claims_direct_ground', 'claims_direct_air', 'claims_direct_naval',
    'claims_including_children', 'claims_including_children_preferred',
    'claims_including_children_ground', 'claims_including_children_air', 'claims_including_children_naval',
    'missions_direct', 'missions_including_children',
    'units_direct', 'units_including_children',
    'first_claim_date', 'last_claim_date',
    'primary_place_id', 'primary_place_name',
    'centroid_lat', 'centroid_lon',
    'bbox_south', 'bbox_west', 'bbox_north', 'bbox_east',
    'extent_n_points', 'extent_radius_80_km', 'extent_quality', 'extent_note',
    'reference_ids',
]


def is_preferred(row):
    return (row.get('claim_status') or 'preferred') == 'preferred'


def haversine_km(lat1, lon1, lat2, lon2):
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlamb = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dlamb / 2) ** 2
    return 2 * EARTH_KM * math.asin(min(1.0, math.sqrt(a)))


def _f(s):
    try:
        return float(s)
    except (TypeError, ValueError):
        return None


def _median(vals):
    vals = sorted(vals)
    n = len(vals)
    if n == 0:
        return None
    if n % 2:
        return vals[n // 2]
    return (vals[n // 2 - 1] + vals[n // 2]) / 2.0


def _pct(vals, p):
    if not vals:
        return None
    if len(vals) == 1:
        return 0.0
    s = sorted(vals)
    idx = int(round(p * (len(s) - 1)))
    idx = max(0, min(len(s) - 1, idx))
    return s[idx]


def is_hq(claim):
    return (claim.get('location_represents') or '') in HQ_REPRESENTS or (claim.get('event_type') or '') in HQ_EVENTS


def coord_of(claim):
    lat, lon = _f(claim.get('latitude')), _f(claim.get('longitude'))
    if lat is None or lon is None:
        return None
    return lat, lon


def extent_of(claims):
    """Return a dict of extent fields for one operation's preferred, coordinated claims (any domain)."""
    pts = []
    for c in claims:
        xy = coord_of(c)
        if not xy:
            continue
        pts.append({'lat': xy[0], 'lon': xy[1], 'place_id': c.get('place_id') or '', 'hq': is_hq(c)})
    empty = dict(centroid_lat='', centroid_lon='', bbox_south='', bbox_west='', bbox_north='', bbox_east='',
                 extent_n_points='0', extent_radius_80_km='', extent_quality='none', extent_note='')
    if len(pts) < 2:
        if pts:
            empty['extent_n_points'] = '1'
            empty['extent_note'] = 'n_preferred_coords=1'
        return empty
    mlat, mlon = _median([p['lat'] for p in pts]), _median([p['lon'] for p in pts])
    n_hq = sum(1 for p in pts if p['hq'])
    n_out = 0
    kept = []
    for p in pts:
        if p['hq']:
            continue
        if haversine_km(mlat, mlon, p['lat'], p['lon']) >= OUTLIER_KM:
            n_out += 1
            continue
        kept.append(p)
    notes = []
    if n_hq:
        notes.append('excluded_n_hq=%d' % n_hq)
    if n_out:
        notes.append('excluded_n_outlier_%dkm=%d' % (int(OUTLIER_KM), n_out))
    if len(kept) < 2:
        empty['extent_n_points'] = str(len(kept))
        empty['extent_note'] = ';'.join(notes) if notes else ''
        return empty
    clat, clon = _median([p['lat'] for p in kept]), _median([p['lon'] for p in kept])
    dists = [haversine_km(clat, clon, p['lat'], p['lon']) for p in kept]
    r80 = _pct(dists, 0.80)
    south, north = min(p['lat'] for p in kept), max(p['lat'] for p in kept)
    west, east = min(p['lon'] for p in kept), max(p['lon'] for p in kept)
    by_place = {}
    for p in kept:
        if p['place_id']:
            by_place[p['place_id']] = by_place.get(p['place_id'], 0) + 1
    top_share = (max(by_place.values()) / len(kept)) if by_place else 0.0
    return dict(
        centroid_lat='%.4f' % clat, centroid_lon='%.4f' % clon,
        bbox_south='%.4f' % south, bbox_west='%.4f' % west, bbox_north='%.4f' % north, bbox_east='%.4f' % east,
        extent_n_points=str(len(kept)), extent_radius_80_km='' if r80 is None else '%.1f' % r80,
        top_share=top_share, r80=r80, notes=notes,
    )


def quality_of(op, ext):
    """focal / compact / broad / none (OB5). Campaigns and umbrellas are always broad when they have points."""
    n = int(ext.get('extent_n_points') or '0')
    if n < 2:
        return 'none', ext.get('extent_note') or ext.get('notes') and ';'.join(ext['notes']) or ''
    r80 = ext.get('r80')
    typ = op.get('op_type') or ''
    notes = list(ext.get('notes') or [])
    if typ in ('campaign', 'umbrella') or (r80 is not None and r80 > BROAD_RADIUS_KM):
        q = 'broad'
        if typ in ('campaign', 'umbrella'):
            notes.append('quality=broad_because_%s' % typ)
        elif r80 is not None:
            notes.append('quality=broad_because_r80')
    elif (r80 is not None and r80 <= FOCAL_RADIUS_KM) or (ext.get('top_share') or 0) >= FOCAL_PLACE_SHARE:
        q = 'focal'
    else:
        q = 'compact'
    # Centroids are withheld for broad and none (OB4, OB5).
    if q in ('broad', 'none'):
        ext['centroid_lat'] = ''
        ext['centroid_lon'] = ''
    return q, ';'.join(notes)


def _domain(units, uid):
    u = units.get(uid) or {}
    return common.unit_domain(u)


def _bucket():
    return {'all': [], 'preferred': [], 'ground': [], 'air': [], 'naval': []}


def operations_table(ops, claims, missions, units, places):
    """Rows of build/operations.csv and the operations section of docs/coverage.md.

    `claims` is every claim (all domains). Counts that were previously ground-only are now all-domain
    (OB1); breakdown columns keep the ground/air/naval split.
    """
    descendants = {}
    for o in ops.rows:
        descendants[o['operation_id']] = {c['operation_id'] for c in ops.chain(o['operation_id'])}

    direct, rolled = {}, {}
    for oid in descendants:
        direct[oid] = _bucket()
        rolled[oid] = _bucket()

    def add_claim(store, oid, c, pref):
        b = store[oid]
        b['all'].append(c)
        if pref:
            b['preferred'].append(c)
        d = _domain(units, c['unit_id'])
        if d in b:
            b[d].append(c)

    for c in claims:
        oid = c.get('operation_id') or ''
        if oid not in direct:
            continue
        pref = is_preferred(c)
        add_claim(direct, oid, c, pref)
        for anc in descendants[oid]:
            add_claim(rolled, anc, c, pref)

    miss_d, miss_r = {i: [] for i in descendants}, {i: [] for i in descendants}
    for m in missions or []:
        oid = (m.get('operation_id') or '').strip()
        if oid not in direct:
            continue
        miss_d[oid].append(m)
        for anc in descendants[oid]:
            miss_r[anc].append(m)

    def dates_of(oid):
        ds = [c['date'] for c in rolled[oid]['all'] if c.get('date')]
        ds += [m['date'] for m in miss_r[oid] if m.get('date')]
        ds = sorted(ds)
        return (ds[0], ds[-1]) if ds else ('', '')

    def units_of(clist, mlist):
        return {c['unit_id'] for c in clist if c.get('unit_id')} | {m['unit_id'] for m in mlist if m.get('unit_id')}

    out = []
    quality_counts = {'focal': 0, 'compact': 0, 'broad': 0, 'none': 0}
    for o in sorted(ops.rows, key=lambda r: r['operation_id']):
        i = o['operation_id']
        path = ' > '.join(c['name'] for c in reversed(ops.chain(i)))
        first, last = dates_of(i)
        pin = (o.get('primary_place_id') or '').strip()
        pin_name = places[pin]['name'] if pin and pin in places else ''
        ext = extent_of(direct[i]['preferred'])
        quality, note = quality_of(o, ext)
        quality_counts[quality] += 1
        ext['extent_quality'] = quality
        ext['extent_note'] = note
        # withhold centroid for broad/none already handled in quality_of
        d, r = direct[i], rolled[i]
        out.append([
            i, o['name'], o['short_name'], o['alt_names'], o['op_type'], o['parent_operation_id'], path, str(ops.depth(i)),
            o['start_date'], o['end_date'], o['date_basis'], o['nationality_scope'],
            str(len(d['all'])), str(len(d['preferred'])),
            str(len(d['ground'])), str(len(d['air'])), str(len(d['naval'])),
            str(len(r['all'])), str(len(r['preferred'])),
            str(len(r['ground'])), str(len(r['air'])), str(len(r['naval'])),
            str(len(miss_d[i])), str(len(miss_r[i])),
            str(len(units_of(d['all'], miss_d[i]))), str(len(units_of(r['all'], miss_r[i]))),
            first, last,
            pin, pin_name,
            ext.get('centroid_lat') or '', ext.get('centroid_lon') or '',
            ext.get('bbox_south') or '', ext.get('bbox_west') or '', ext.get('bbox_north') or '', ext.get('bbox_east') or '',
            ext.get('extent_n_points') or '0', ext.get('extent_radius_80_km') or '', quality, ext.get('extent_note') or '',
            o['reference_ids'],
        ])

    # coverage.md: all-domain claim totals, with a note that earlier builds counted ground only
    by_type = {}
    for o in ops.rows:
        by_type.setdefault(o['op_type'], [0, 0, 0])[0] += 1
    for c in claims:
        t = ops.by_id.get(c.get('operation_id'), {}).get('op_type')
        if t:
            by_type.setdefault(t, [0, 0, 0])[1] += 1
    for o in ops.rows:
        if direct[o['operation_id']]['all']:
            by_type[o['op_type']][2] += 1
    md = ['', '## Operations', '',
          'Generated from `data/operations.csv` and every claim\'s `operation_id` (all domains: ground, air and naval). '
          'Per-operation detail (path, dates, claim and mission counts, sourced pin, derived extent) is in `build/operations.csv`. '
          'A claim points at the most specific operation row it belongs to; rows with no named operation point at their campaign row. '
          'Before 24 November 2026 the claim counts in this section and in `build/operations.csv` counted ground claims only; '
          'the totals below and the `claims_direct` / `claims_including_children` columns are now all-domain, with ground/air/naval breakdowns.',
          '',
          '| op_type | Operation rows | Rows used by a claim | Claims whose operation_id is of this type |',
          '|---|---:|---:|---:|']
    for t in operations.OP_TYPES:
        if t in by_type:
            md.append('| %s | %d | %d | %d |' % (t, by_type[t][0], by_type[t][2], by_type[t][1]))
    md.append('| **All** | **%d** | **%d** | **%d** |' % (len(ops.rows), sum(v[2] for v in by_type.values()), len(claims)))
    md.append('')
    md.append('Derived extent quality (preferred coordinates, headquarters rows and points 200 km from the median excluded): '
              'focal %d, compact %d, broad %d, none %d. A map pin (`primary_place_id`) is a sourced place, not this centroid.'
              % (quality_counts['focal'], quality_counts['compact'], quality_counts['broad'], quality_counts['none']))
    return out, ('\n'.join(md) + '\n').encode('utf-8'), quality_counts


def operations_geojson(op_rows, places):
    """FeatureCollection. Point geometry only when extent_quality is focal or compact (OB4)."""
    by_place = places
    feats = []
    header = BUILD_HEADER
    for row in op_rows:
        rec = dict(zip(header, row))
        q = rec['extent_quality']
        geom = None
        if q in ('focal', 'compact'):
            lat = lon = None
            pin = rec.get('primary_place_id') or ''
            if pin and pin in by_place:
                lat, lon = _f(by_place[pin].get('latitude')), _f(by_place[pin].get('longitude'))
            if lat is None or lon is None:
                lat, lon = _f(rec.get('centroid_lat')), _f(rec.get('centroid_lon'))
            if lat is not None and lon is not None:
                geom = {'type': 'Point', 'coordinates': [lon, lat]}
        feats.append({'type': 'Feature', 'geometry': geom, 'properties': _geo_props(rec)})
    gj = {'type': 'FeatureCollection', 'features': feats}
    return (json.dumps(gj, ensure_ascii=False, indent=1) + '\n').encode('utf-8')


def _geo_props(rec):
    int_keys = {
        'depth', 'claims_direct', 'claims_direct_preferred', 'claims_direct_ground', 'claims_direct_air', 'claims_direct_naval',
        'claims_including_children', 'claims_including_children_preferred',
        'claims_including_children_ground', 'claims_including_children_air', 'claims_including_children_naval',
        'missions_direct', 'missions_including_children', 'units_direct', 'units_including_children', 'extent_n_points',
    }
    float_keys = {
        'centroid_lat', 'centroid_lon', 'bbox_south', 'bbox_west', 'bbox_north', 'bbox_east', 'extent_radius_80_km',
    }
    props = {}
    for k, v in rec.items():
        if v == '' or v is None:
            props[k] = None
        elif k in int_keys:
            props[k] = int(v)
        elif k in float_keys:
            props[k] = float(v)
        else:
            props[k] = v
    return props
