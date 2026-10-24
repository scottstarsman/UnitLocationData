#!/usr/bin/env python3
"""Generate the combined outputs in build/ from the per-unit master files in data/claims/.

Outputs (deterministic: rows sorted by date then claim_id, LF line endings, UTF-8):
  build/all_claims.csv                  every claim, same columns as the schema
  build/by_month/<YYYY-MM>.csv          claims by month of `date`
  build/by_theater/<theater>.csv        claims by theater
  build/claims.geojson                  one Point feature per claim (lon, lat) with main properties

Do not hand-edit anything in build/: edit data/claims/ and re-run this script.

Usage: python scripts/build.py            write the outputs (removes stale files in build/)
       python scripts/build.py --check    do not write; exit 1 if build/ is not up to date
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common  # noqa: E402

GEO_PROPS = ['claim_id', 'conflict_group_id', 'claim_status', 'unit_id', 'unit_name', 'nationality', 'theater',
             'echelon', 'branch', 'date', 'location_name', 'location_represents', 'precision_km', 'confidence',
             'event_type', 'current_activity', 'operation_name', 'sub_operation_name', 'strength_status']
NUMERIC = {'precision_km', 'confidence'}


def num(s):
    f = float(s)
    return int(f) if f == int(f) else f


def outputs():
    """Return {relative path: bytes} for every generated file."""
    header, rows = common.load_all_claims()
    table = lambda rs: common.csv_bytes(header, [[r[c] for c in header] for r in rs])  # noqa: E731
    out = {'all_claims.csv': table(rows)}
    months, theaters = {}, {}
    for r in rows:
        months.setdefault(r['date'][:7], []).append(r)
        theaters.setdefault(r['theater'], []).append(r)
    for k in sorted(months):
        out['by_month/%s.csv' % k] = table(months[k])
    for k in sorted(theaters):
        out['by_theater/%s.csv' % k] = table(theaters[k])
    feats = []
    for r in rows:
        props = {}
        for p in GEO_PROPS:
            v = r[p]
            props[p] = num(v) if p in NUMERIC and v != '' else (v if v != '' else None)
        feats.append({'type': 'Feature', 'geometry': {'type': 'Point', 'coordinates': [float(r['longitude']), float(r['latitude'])]},
                      'properties': props})
    gj = {'type': 'FeatureCollection', 'features': feats}
    out['claims.geojson'] = (json.dumps(gj, ensure_ascii=False, indent=1) + '\n').encode('utf-8')
    return out


def existing():
    found = {}
    for dp, _d, fs in os.walk(common.BUILD_DIR):
        for fn in fs:
            p = os.path.join(dp, fn)
            found[os.path.relpath(p, common.BUILD_DIR).replace(os.sep, '/')] = p
    return found


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--check', action='store_true', help='verify build/ is up to date without writing')
    args = ap.parse_args()
    out = outputs()
    have = existing()
    if args.check:
        bad = []
        for k, data in out.items():
            if k not in have:
                bad.append('missing: build/' + k)
            elif open(have[k], 'rb').read() != data:
                bad.append('out of date: build/' + k)
        for k in have:
            if k not in out:
                bad.append('stale: build/' + k)
        if bad:
            print('\n'.join(bad))
            print('build/ is not up to date; run python scripts/build.py and commit the result')
            return 1
        print('build/ is up to date (%d files)' % len(out))
        return 0
    for k, p in have.items():
        if k not in out:
            os.remove(p)
    for dp, ds, fs in os.walk(common.BUILD_DIR, topdown=False):
        if not os.listdir(dp) and dp != common.BUILD_DIR:
            os.rmdir(dp)
    for k, data in out.items():
        p = os.path.join(common.BUILD_DIR, k)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, 'wb') as f:
            f.write(data)
    print('wrote %d files to build/' % len(out))
    return 0


if __name__ == '__main__':
    sys.exit(main())
