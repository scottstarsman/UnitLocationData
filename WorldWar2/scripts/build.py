#!/usr/bin/env python3
"""Generate the combined outputs in build/ from the per-unit master files in data/claims/.

Outputs (deterministic: rows sorted by date then claim_id, LF line endings, UTF-8):
  build/all_claims.csv                  every claim: the columns of the schema plus the derived columns that are no longer stored in the claim files:
                                        command_relationships (rebuilt from data/command_relations.csv and data/command_relation_claims.csv),
                                        place_name, location_name (place name + location_qualifier), country, region, coord_reference_id and
                                        coord_source_note (from data/places.csv), strength_status (destroyed flag, else strength_json status, else unknown)
                                        and location_temporal_offset_days (location_date - date); see scripts/places.py
  build/claims.geojson                  one Point feature per claim (lon, lat; the claim's own point, which equals its place's unless coord_override) with main properties
  build/places.csv                      derived view of data/places.csv: the place columns plus claims_count, units_count, first and last claim date
  build/places.geojson                  one Point feature per place with its main properties and claims_count
  build/coverage.csv                    one row per unit in data/units.csv: record_status, formed_date, whether it has a
                                        claim file, number of claim rows and their first and last date
  docs/coverage.md                      summary counts of the same, by nationality and echelon (generated; do not edit)
  build/operations.csv                  derived view of data/operations.csv: operation path, depth, claim counts (direct and including child operations);
                                        all_claims.csv also carries the derived columns operation, operation_type, campaign, operation_name,
                                        sub_operation_name, operation_path (see scripts/operations.py)
  build/command_relations.csv           the master data/command_relations.csv with names, a support column (documented | table | inferred)
                                        and the evidence claim ids; every preferred relation except `organic` (the placeholders with no
                                        higher unit included), all nationalities and dates; see schema/README.md, "Validity of a relationship"
                                        (the claims stay the evidence; scripts/who_controls.py reads this file)
  data/references.csv                   the references table (one row per distinct source cited; derived from the claims and
                                        data/references_meta.csv by scripts/build_references.py, which build.py calls)
  build/claim_references.csv            claim_id -> reference_id links, one row per link and role (role event | date | location | command_relationship | strength | general; locator = page or section), built from the claims' stored reference_ids
  build/unit_references.csv             unit_id -> reference_id links (formed_date_source, listing_source, initial_parent_source)

Do not hand-edit anything in build/: edit data/claims/, data/command_relations.csv or data/command_relation_claims.csv and re-run this script.

Usage: python scripts/build.py            write the outputs (removes stale files in build/)
       python scripts/build.py --check    do not write; exit 1 if build/ is not up to date
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common  # noqa: E402
import build_references  # noqa: E402
import command_relations  # noqa: E402
import operations  # noqa: E402
import places as placesmod  # noqa: E402

GEO_PROPS = ['claim_id', 'conflict_group_id', 'claim_status', 'unit_id', 'unit_name', 'nationality', 'theater',
             'echelon', 'branch', 'date', 'place_id', 'location_name', 'location_represents', 'precision_km', 'confidence',
             'event_type', 'current_activity', 'operation_id', 'operation', 'operation_type', 'campaign', 'operation_name', 'sub_operation_name', 'strength_status', 'location_date', 'location_basis',
             'location_temporal_offset_days', 'reference_ids', 'source_locator']
DERIVED = ['operation', 'operation_type', 'campaign', 'operation_name', 'sub_operation_name', 'operation_path']   # appended to all_claims.csv from data/operations.csv
NUMERIC = {'precision_km', 'confidence', 'location_temporal_offset_days'}
PLACES_OUT_HEADER = placesmod.HEADER + ['claims_count', 'units_count', 'first_claim_date', 'last_claim_date']


def all_claims_header(stored):
    """Header of build/all_claims.csv: the claim-file columns with the derived ones at the place the stored column used to have (or next to the
    column they come from), then the derived operation columns."""
    after = {'parent_unit_id': ['command_relationships'], 'place_id': ['place_name', 'location_name'],
             'coord_override': ['country', 'region', 'coord_reference_id', 'coord_source_note'], 'engaged_note': ['engaged_with_names', 'strength_status'], 'composing_text': ['composing_units_names'],
             'location_basis': ['location_temporal_offset_days']}
    h = []
    for c in stored:
        h.append(c)
        h.extend(after.get(c, []))
    return h + DERIVED


def places_outputs(rows):
    """build/places.csv, build/places.geojson and the text of the places section of docs/coverage.md."""
    places = placesmod.load()
    per = {}
    for r in rows:
        per.setdefault(r['place_id'], []).append(r)
    out, feats = [], []
    kinds, countries = {}, {}
    for p in places.rows:
        rs = per.get(p['place_id'], [])
        ds = sorted(r['date'] for r in rs)
        row = [p[c] for c in placesmod.HEADER] + [str(len(rs)), str(len({r['unit_id'] for r in rs})), ds[0] if ds else '', ds[-1] if ds else '']
        out.append(row)
        props = {'place_id': p['place_id'], 'name': p['name'], 'alt_names': p['alt_names'] or None, 'kind': p['kind'], 'precision_km': num(p['precision_km']),
                 'country': p['country'], 'region': p['region'], 'claims_count': len(rs)}
        feats.append({'type': 'Feature', 'geometry': {'type': 'Point', 'coordinates': [float(p['longitude']), float(p['latitude'])]}, 'properties': props})
        k = kinds.setdefault(p['kind'], [0, 0])
        k[0] += 1
        k[1] += len(rs)
        c = countries.setdefault(p['country'], [0, 0])
        c[0] += 1
        c[1] += len(rs)
    names = placesmod.load()
    alias_n = sum(len([a for a in p['alt_names'].split(';') if a.strip()]) for p in names.rows)
    md = ['', '## Places', '',
          'Generated from `data/places.csv` and the claims\' `place_id`. Per-place detail (aliases, claim and unit counts, first and last claim date) is in `build/places.csv`; '
          '`build/places.geojson` has one point per place. %d places and %d alias names for %d claims.' % (len(places.rows), alias_n, len(rows)), '',
          '| kind | Places | Claims |', '|---|---:|---:|']
    for k in common.vocab_values('place_kind'):
        if k in kinds:
            md.append('| %s | %d | %d |' % (k, kinds[k][0], kinds[k][1]))
    md += ['', '| country | Places | Claims |', '|---|---:|---:|']
    cn = common.vocab_descriptions('country')
    for c in sorted(countries, key=lambda c: (-countries[c][1], c)):
        md.append('| %s (%s) | %d | %d |' % (cn.get(c, c), c, countries[c][0], countries[c][1]))
    gj = {'type': 'FeatureCollection', 'features': feats}
    return out, (json.dumps(gj, ensure_ascii=False, indent=1) + '\n').encode('utf-8'), ('\n'.join(md) + '\n').encode('utf-8')


def num(s):
    f = float(s)
    return int(f) if f == int(f) else f


ECHELON_ORDER = common.echelon_display_order()   # schema/vocabularies.json, vocabulary echelon_rank (display_order)
COVERAGE_HEADER = ['unit_id', 'unit_name', 'nationality', 'echelon', 'branch', 'record_status', 'formed_date', 'has_claim_file',
                   'claim_rows', 'first_claim_date', 'last_claim_date', 'initial_parent_unit_id']


def ech_rank(e):
    return ECHELON_ORDER.index(e) if e in ECHELON_ORDER else len(ECHELON_ORDER)


def coverage(claim_rows):
    """Return (rows for coverage.csv, text of docs/coverage.md)."""
    _h, units = common.read_dicts(common.UNITS_CSV)
    per = {}
    for r in claim_rows:
        d = per.setdefault(r['unit_id'], [])
        d.append(r['date'])
    rows = []
    for u in units:
        ds = sorted(per.get(u['unit_id'], []))
        rows.append([u['unit_id'], u['unit_name'], u['nationality'], u['echelon'], u['branch'], u['record_status'], u['formed_date'],
                     'true' if ds else 'false', str(len(ds)), ds[0] if ds else '', ds[-1] if ds else '', u['initial_parent_unit_id']])
    rows.sort(key=lambda r: (r[2], ech_rank(r[3]), r[0]))
    tally = {}
    for r in rows:
        t = tally.setdefault((r[2], r[3]), {'placeholder': 0, 'partial': 0, 'active': 0, 'claims': 0, 'dated': 0})
        t[r[5]] += 1
        t['claims'] += int(r[8])
        t['dated'] += 1 if r[6] else 0
    out = ['# Coverage', '',
           'Generated by `python scripts/build.py` from `data/units.csv` and `data/claims/`. Do not edit by hand. '
           'Per-unit detail is in `build/coverage.csv`.', '',
           'A **placeholder** is a unit that exists in the table (identity, echelon, sometimes a formation date) but has no '
           'claim file: it says nothing about where the unit was. **active** units have a claim file; **partial** is reserved '
           'for claim files known to be incomplete. See "Placeholder units" in `docs/methodology.md`.', '',
           '| Nationality | Echelon | Placeholder | Partial | Active | Total | With formed_date | Claim rows |',
           '|---|---|---:|---:|---:|---:|---:|---:|']
    tot = {'placeholder': 0, 'partial': 0, 'active': 0, 'claims': 0, 'dated': 0}
    for (nat, ech) in sorted(tally, key=lambda k: (k[0], ech_rank(k[1]))):
        t = tally[(nat, ech)]
        out.append('| %s | %s | %d | %d | %d | %d | %d | %d |' % (nat, ech, t['placeholder'], t['partial'], t['active'],
                                                                 t['placeholder'] + t['partial'] + t['active'], t['dated'], t['claims']))
        for k in tot:
            tot[k] += t[k]
    out.append('| **All** | | **%d** | **%d** | **%d** | **%d** | **%d** | **%d** |' % (
        tot['placeholder'], tot['partial'], tot['active'], tot['placeholder'] + tot['partial'] + tot['active'], tot['dated'], tot['claims']))
    return rows, ('\n'.join(out) + '\n').encode('utf-8')


OPERATIONS_HEADER = ['operation_id', 'name', 'short_name', 'alt_names', 'op_type', 'parent_operation_id', 'operation_path', 'depth', 'start_date',
                     'end_date', 'date_basis', 'nationality_scope', 'claims_direct', 'claims_including_children', 'first_claim_date',
                     'last_claim_date', 'reference_ids']


def operations_table(ops, rows):
    """Rows of build/operations.csv and the text of the operations section of docs/coverage.md."""
    direct, sub = {}, {}
    for r in rows:
        direct.setdefault(r['operation_id'], []).append(r['date'])
        for c in ops.chain(r['operation_id']):
            sub.setdefault(c['operation_id'], []).append(r['date'])
    out = []
    for o in sorted(ops.rows, key=lambda o: o['operation_id']):
        i = o['operation_id']
        ds = sorted(sub.get(i, []))
        path = ' > '.join(c['name'] for c in reversed(ops.chain(i)))
        out.append([i, o['name'], o['short_name'], o['alt_names'], o['op_type'], o['parent_operation_id'], path, str(ops.depth(i)),
                    o['start_date'], o['end_date'], o['date_basis'], o['nationality_scope'], str(len(direct.get(i, []))), str(len(ds)),
                    ds[0] if ds else '', ds[-1] if ds else '', o['reference_ids']])
    by_type = {}
    for o in ops.rows:
        by_type.setdefault(o['op_type'], [0, 0, 0])[0] += 1
    for r in rows:
        t = ops.by_id[r['operation_id']]['op_type']
        by_type.setdefault(t, [0, 0, 0])[1] += 1
    for o in ops.rows:
        if direct.get(o['operation_id']):
            by_type[o['op_type']][2] += 1
    md = ['', '## Operations', '',
          'Generated from `data/operations.csv` and the claims\' `operation_id`. Per-operation detail (path, dates, claim counts) is in `build/operations.csv`. '
          'A claim points at the most specific operation row it belongs to; rows with no named operation point at their campaign row.', '',
          '| op_type | Operation rows | Rows used by a claim | Claims whose operation_id is of this type |', '|---|---:|---:|---:|']
    for t in operations.OP_TYPES:
        if t in by_type:
            md.append('| %s | %d | %d | %d |' % (t, by_type[t][0], by_type[t][2], by_type[t][1]))
    md.append('| **All** | **%d** | **%d** | **%d** |' % (len(ops.rows), sum(v[2] for v in by_type.values()), len(rows)))
    return out, ('\n'.join(md) + '\n').encode('utf-8')


def json_columns():
    """Columns of build/all_claims.csv that hold JSON in a cell (registry schema/json/fields.json)."""
    reg = json.load(open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'schema', 'json', 'fields.json')))
    return [f['column'] for f in reg['fields'] if 'build/all_claims.csv' in f.get('also_in', [])]


def all_claims_json(header, rows):
    """build/all_claims.json: the rows and columns of build/all_claims.csv, values unchanged as strings, except that
    JSON-in-cell columns (docs/json_fields.md) are parsed into nested objects (null when blank). One claim per line."""
    jc = set(json_columns())
    lines = []
    for r in rows:
        o = {c: ((json.loads(r[c]) if r[c] != '' else None) if c in jc else r[c]) for c in header}
        lines.append(json.dumps(o, ensure_ascii=False, separators=(',', ':')))
    return ('{"description":"Typed export of build/all_claims.csv; JSON-in-cell columns are nested objects (see docs/json_fields.md)",'
            '"json_columns":' + json.dumps(sorted(jc)) + ',"claims":[\n' + ',\n'.join(lines) + '\n]}\n').encode('utf-8')


def outputs():
    """Return {relative path: bytes} for every generated file (paths under docs/ are relative to the repository root)."""
    header, rows = common.load_all_claims()
    ops = operations.load()
    for r in rows:
        r.update(ops.labels(r['operation_id'], r['date']))
    header = all_claims_header(header)   # the derived columns (command_relationships, place and derived-value columns, operations) are not claim-file columns
    table = lambda rs: common.csv_bytes(header, [[r[c] for c in header] for r in rs])  # noqa: E731
    out = {'all_claims.csv': table(rows)}
    out['all_claims.json'] = all_claims_json(header, rows)
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
    cov_rows, cov_md = coverage(rows)
    out['coverage.csv'] = common.csv_bytes(COVERAGE_HEADER, cov_rows)
    units = {u['unit_id']: u for u in common.read_dicts(common.UNITS_CSV)[1]}
    out['command_relations.csv'] = common.csv_bytes(command_relations.DERIVED_HEADER, command_relations.derived_rows(command_relations.load(), units, rows))
    op_rows, op_md = operations_table(ops, rows)
    out['operations.csv'] = common.csv_bytes(OPERATIONS_HEADER, op_rows)
    pl_rows, pl_geo, pl_md = places_outputs(rows)
    out['places.csv'] = common.csv_bytes(PLACES_OUT_HEADER, pl_rows)
    out['places.geojson'] = pl_geo
    out['../docs/coverage.md'] = cov_md + op_md + pl_md
    # references: data/references.csv (metadata + counts) and the claim/unit -> reference links (see build_references.py)
    for k, data in build_references.outputs().items():
        out[k[len('build/'):] if k.startswith('build/') else '../' + k] = data
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
            if k.startswith('../'):
                p = os.path.normpath(os.path.join(common.BUILD_DIR, k))
                if not os.path.isfile(p) or open(p, 'rb').read() != data:
                    bad.append('missing or out of date: ' + os.path.relpath(p, common.ROOT))
            elif k not in have:
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
        print('build/ and docs/coverage.md are up to date (%d files)' % len(out))
        return 0
    for k, p in have.items():
        if k not in out:
            os.remove(p)
    for dp, ds, fs in os.walk(common.BUILD_DIR, topdown=False):
        if not os.listdir(dp) and dp != common.BUILD_DIR:
            os.rmdir(dp)
    for k, data in out.items():
        p = os.path.normpath(os.path.join(common.BUILD_DIR, k))
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, 'wb') as f:
            f.write(data)
    print('wrote %d files (build/ and docs/coverage.md)' % len(out))
    return 0


if __name__ == '__main__':
    sys.exit(main())
