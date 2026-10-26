#!/usr/bin/env python3
"""Losslessness check for the five place merges of item 8 (branch place-merges).

  python scripts/verify_place_merges.py --base <rev>     <rev> = the commit before the branch (it has the old build/ files)

Compares the build/ files of <rev> (read with git show) with the working tree and fails (exit 1) unless exactly the expected cells changed:
  * build/all_claims.csv: only the claims of EXPECTED changed, and in them only place_id, place_name, location_name, location_qualifier and the place columns
    (country, region, coord_reference_id, coord_source_note, which now come from the survivor); the new place_id and location_qualifier are the listed ones;
    the survivor's values fill the place columns; latitude, longitude, precision_km and coord_override never change; every other claim is identical;
  * build/claims.geojson: the same features in the same order with identical coordinates (properties may differ only in the claims above);
  * build/places.csv: the old table minus the retired ids; a survivor differs only in alt_names and the counts and dates of its claims; every other place is identical;
  * data/place_merges.csv has exactly the retired ids; no claim points at a retired id.
The merges applied so far are those whose retired id is gone from build/places.csv (a partial branch is checked against the merges made). Standard library only.
"""
import argparse
import csv
import io
import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common  # noqa: E402

# merge: retired, survivor, {claim: (new qualifier)}, alias added (or None)
MERGES = [
    ('PL0070', 'PL0071', {'C0104': "left of First Army line"}, 'Caumont'),
    ('PL0208', 'PL0209', {'C0330': 'Mantes-Gassicourt, Seine crossing', 'C0451': 'Mantes-Gassicourt, Seine crossing'}, 'Mantes-Gassicourt'),
    ('PL0294', 'PL0045', {'C0408': 'Recouvrance district'}, 'Recouvrance'),
    ('PL0259', 'PL0258', {'C0006': 'division HQ Le Molay-Littry'}, None),
    ('PL0174', 'PL0173', {'C0196': 'Odon salient'}, None),
]
PLACE_COLS = ['place_id', 'place_name', 'location_name', 'location_qualifier', 'country', 'region', 'coord_reference_id', 'coord_source_note']
FIXED = ['latitude', 'longitude', 'precision_km', 'coord_override']
SURV_COLS = ['alt_names', 'claims_count', 'units_count', 'first_claim_date', 'last_claim_date']


def git_csv(rev, path):
    out = subprocess.run(['git', 'show', '%s:%s' % (rev, path)], capture_output=True, text=True, cwd=common.ROOT)
    if out.returncode:
        raise SystemExit(out.stderr)
    return out.stdout


def rows(text):
    return list(csv.DictReader(io.StringIO(text)))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--base', required=True)
    base = ap.parse_args().base
    root = common.ROOT
    problems = []

    def read(p):
        return open(os.path.join(root, p), encoding='utf-8').read()

    old_pl = {r['place_id']: r for r in rows(git_csv(base, 'build/places.csv'))}
    new_pl = {r['place_id']: r for r in rows(read('build/places.csv'))}
    done = [m for m in MERGES if m[0] in old_pl and m[0] not in new_pl]
    todo = [m for m in MERGES if m[0] in new_pl]
    retired = {m[0]: m[1] for m in done}
    surv = {m[1]: m for m in done}
    expected = {c: (m[1], q) for m in done for c, q in m[2].items()}

    # ---- all_claims.csv
    old = {r['claim_id']: r for r in rows(git_csv(base, 'build/all_claims.csv'))}
    new = {r['claim_id']: r for r in rows(read('build/all_claims.csv'))}
    if list(old) != list(new):
        problems.append('claim ids or their order differ')
    cells, changed = 0, set()
    for cid in old:
        o, n = old[cid], new[cid]
        for col in o:
            if o[col] != n[col]:
                cells += 1
                changed.add(cid)
                print('%s %s\n    was: %r\n    now: %r' % (cid, col, o[col], n[col]))
                if cid not in expected:
                    problems.append('%s %s changed but the claim is not at a retired place' % (cid, col))
                elif col not in PLACE_COLS:
                    problems.append('%s %s changed (only %s may)' % (cid, col, PLACE_COLS))
    for cid, (sid, q) in expected.items():
        n = new[cid]
        if n['place_id'] != sid:
            problems.append('%s place_id is %s, expected %s' % (cid, n['place_id'], sid))
        if n['location_qualifier'] != q:
            problems.append('%s location_qualifier is %r, expected %r' % (cid, n['location_qualifier'], q))
        p = new_pl[sid]
        for c in ('country', 'region', 'coord_reference_id', 'coord_source_note'):
            if n[c] != p[c]:
                problems.append('%s %s is %r, the survivor has %r' % (cid, c, n[c], p[c]))
        if n['place_name'] != p['name']:
            problems.append('%s place_name %r != %r' % (cid, n['place_name'], p['name']))
        for c in FIXED:
            if old[cid][c] != n[c]:
                problems.append('%s %s changed' % (cid, c))
        if old[cid]['place_id'] not in retired:
            problems.append('%s was not at a retired place (%s)' % (cid, old[cid]['place_id']))
        if cid not in changed:
            problems.append('%s was expected to change and did not' % cid)
    for cid in changed - set(expected):
        problems.append('%s changed without being expected' % cid)
    for cid, r in new.items():
        if r['place_id'] in retired:
            problems.append('%s still points at the retired %s' % (cid, r['place_id']))

    # ---- claims.geojson
    og = json.loads(git_csv(base, 'build/claims.geojson'))['features']
    ng = json.loads(read('build/claims.geojson'))['features']
    if len(og) != len(ng):
        problems.append('claims.geojson has %d features, was %d' % (len(ng), len(og)))
    else:
        moved = 0
        for a, b in zip(og, ng):
            if a['geometry'] != b['geometry']:
                moved += 1
            if a['properties'].get('claim_id') != b['properties'].get('claim_id'):
                problems.append('claims.geojson order differs at %s' % a['properties'].get('claim_id'))
            elif a['properties'] != b['properties'] and a['properties']['claim_id'] not in expected:
                problems.append('claims.geojson properties of %s changed' % a['properties']['claim_id'])
        if moved:
            problems.append('%d claims.geojson positions changed' % moved)
        print('claims.geojson: %d features, positions identical: %s' % (len(ng), 'yes' if not moved else 'NO'))

    # ---- places
    for pid, r in old_pl.items():
        if pid in retired:
            continue
        n = new_pl.get(pid)
        if n is None:
            problems.append('place %s disappeared' % pid)
            continue
        for col in r:
            if r[col] != n[col]:
                if pid in surv and col in SURV_COLS:
                    continue
                problems.append('place %s %s changed: %r -> %r' % (pid, col, r[col], n[col]))
    for pid in new_pl:
        if pid not in old_pl:
            problems.append('place %s is new' % pid)
    for rid, sid in retired.items():
        m = surv[sid]
        alts = [a.strip() for a in new_pl[sid]['alt_names'].split(';') if a.strip()]
        olds = [a.strip() for a in old_pl[sid]['alt_names'].split(';') if a.strip()]
        want = olds + ([m[3]] if m[3] else [])
        if alts != want:
            problems.append('%s alt_names %s != %s' % (sid, alts, want))
        if old_pl[rid]['coord_reference_id'] != old_pl[sid]['coord_reference_id']:
            problems.append('%s and %s had different coord_reference_id' % (rid, sid))
        if (old_pl[rid]['latitude'], old_pl[rid]['longitude']) != (old_pl[sid]['latitude'], old_pl[sid]['longitude']):
            problems.append('%s and %s were not on the same point' % (rid, sid))
        gain = len([c for c in expected if expected[c][0] == sid and old[c]['place_id'] == rid])
        if int(new_pl[sid]['claims_count']) != int(old_pl[sid]['claims_count']) + gain:
            problems.append('%s claims_count %s, expected %d' % (sid, new_pl[sid]['claims_count'], int(old_pl[sid]['claims_count']) + gain))
    # ---- place_merges
    mrows = rows(read('data/place_merges.csv'))
    if {r['retired_place_id']: r['merged_into_place_id'] for r in mrows} != retired:
        problems.append('data/place_merges.csv does not list exactly %s' % retired)
    print('%d of 5 merges applied (%s); %d changed cells in %d claims; places %d -> %d' % (
        len(done), ', '.join('%s->%s' % (m[0], m[1]) for m in done), cells, len(changed), len(old_pl), len(new_pl)))
    if todo:
        print('not yet merged: %s' % ', '.join('%s->%s' % (m[0], m[1]) for m in todo))
    for p in problems:
        print('PROBLEM:', p)
    return 1 if problems else 0


if __name__ == '__main__':
    sys.exit(main())
