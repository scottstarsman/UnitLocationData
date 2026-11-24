#!/usr/bin/env python3
"""Generate the combined outputs in build/ from the per-unit master files in data/claims/.

Outputs (deterministic: rows sorted by date then claim_id, LF line endings, UTF-8):
  build/all_claims.csv                  every claim of every domain (ground, air and naval), with a domain column: the columns of the schema plus the derived columns that are no longer stored in the claim files:
                                        command_relationships (rebuilt from data/command_relations.csv and data/command_relation_claims.csv),
                                        place_name, location_name (place name + location_qualifier), country, region, coord_reference_id and
                                        coord_source_note (from data/places.csv), strength_status (destroyed flag, else strength_json status, else unknown)
                                        and location_temporal_offset_days (location_date - date); see scripts/places.py;
                                        commander_on_date, commander_on_date_person_id, commander_on_date_source and
                                        commander_on_date_basis (derived from the source-stated commander or from a
                                        preferred covering tenure; scripts/commanders.py); and, last, sidc: the
                                        MIL-STD-2525D military symbol code of the unit on the claim date (scripts/sidc.py, roadmap 410)
  build/claims.geojson                  one Point feature per claim (lon, lat; the claim's own point, which equals its place's unless coord_override) with main properties
  build/places.csv                      derived view of data/places.csv: the place columns plus claims_count, units_count, first and last claim date
  build/places.geojson                  one Point feature per place with its main properties and claims_count
  build/coverage.csv                    one row per unit in data/units.csv (every domain), with a domain column: record_status, formed_date, whether it has a
                                        claim file, number of claim rows and their first and last date
  docs/coverage.md                      summary counts of the same, by nationality and echelon (generated; do not edit)
  build/operations.csv                  derived view of data/operations.csv: operation path, depth, all-domain claim and mission counts
                                        (direct and including child operations, with preferred and ground/air/naval breakdowns),
                                        sourced primary_place_id, and a derived extent (median, bbox, quality; scripts/operation_extent.py).
                                        Earlier builds counted ground claims only in claims_direct / claims_including_children.
  build/operations.geojson              one Feature per operation: a Point (primary place, else centroid) when extent_quality is focal or compact,
                                        otherwise null geometry (broad campaigns, umbrellas and sparse extents)
  build/operation_units.csv             one row per (operation_id, unit_id) derived from claims and missions (direct or via a descendant
                                        operation; no command-hierarchy roll-up; scripts/operation_units.py)
  build/oob/                            flagship order-of-battle snapshots (scripts/export_oob.py) for 6 June, 18 July, 15 August,
                                        16 December 1944, 24 March 1945 and 7 May 1945: JSON, CSV, a ground Markdown tree, and a
                                        14-day located CSV; regenerated on every build. Authorized TO&E columns are filled from
                                        unit_toe for that date only (never inherited from a parent) and kept separate from strength_json.
  build/command_relations.csv           the master data/command_relations.csv with names, a domain column (the subject unit), a support column
                                        (documented | table | inferred) and the evidence claim ids; every preferred relation except `organic`
                                        (the placeholders with no higher unit included), all domains, nationalities and dates; see schema/README.md,
                                        "Validity of a relationship" (the claims stay the evidence; scripts/who_controls.py reads this file). The
                                        who_controls grid still defaults to in-scope ground subjects.
  data/references.csv                   the references table (one row per distinct source cited; derived from the claims and
                                        data/references_meta.csv by scripts/build_references.py, which build.py calls)
  build/claim_references.csv            claim_id -> reference_id links, one row per link and role (role event | date | location | command_relationship | strength | general; locator = page or section), built from the claims' stored reference_ids
  build/people.csv                      data/people.csv plus tenures_count and units_count
  build/unit_commanders.csv             data/unit_commanders.csv (all domains and statuses) with unit_name, nationality,
                                        domain, echelon, canonical_name, sort_name and source_claim_ids
  build/toe_templates.csv               copy of data/toe_templates.csv (authorized TO&E tables, TT####)
  build/unit_toe.csv                    data/unit_toe.csv with the template name, nationality, designation, formation_type,
                                        authorized personnel total and authorized_strength_json joined on
  build/ship_classes.csv                data/ship_classes.csv: the ship classes (class_id SC###) that naval units link to through ship_class_id
  build/aircraft_types.csv              data/aircraft_types.csv: the aircraft types (type_id AT###) that air units link to through the aircraft object of strength_json
  build/missions.csv                    every mission row of data/missions/<nationality>/<unit_id>.csv (one row per mission of a flying unit; decision J1, 17 November
                                        2026), sorted by date then mission_id, with unit_name, nationality, target place name, latitude, longitude and country, and the
                                        aircraft designation added (scripts/missions.py). Missions are not claims and never reach the command relations or the
                                        who_controls grid; build/operation_units.csv counts a mission that carries an operation_id as participation
  build/who_controls_overrides.csv      verbatim copy of data/who_controls_overrides.csv (per-relation exceptions to the who_controls.py precedence)
  build/organic_relations.csv           the preferred `organic` relations only (same columns as command_relations.csv including domain, all domains); read by scripts/who_controls.py for
                                        the organic fallback and by nothing else (command_relations.csv keeps excluding `organic`)
  build/unit_references.csv             unit_id -> reference_id links (formed_date_source, listing_source, initial_parent_source)
  build/unit_symbols.csv                one row per unit and allegiance period: valid_from, valid_to (blank = open: a later date keeps the last side), side,
                                        standard_identity (Allied viewpoint) and the sidc for that period (status present), with the function rule
                                        (scripts/sidc.py, roadmap 410); one file covers every domain
  build/manifest.json                   release metadata written by this script (schema/release.json): schema_version, data_version,
                                        generated_at (the release date at 00:00:00 UTC, not the wall clock), source_tree_sha256 of the
                                        tracked non-generated WorldWar2 files, license, a CITATION.cff pointer, and per-file path, rows or
                                        features, sha256 and bytes. The manifest does not list itself. --check compares the whole file.

Do not hand-edit anything in build/: edit data/claims/, data/command_relations.csv or data/command_relation_claims.csv and re-run this script.

Usage: python scripts/build.py            write the outputs (removes stale files in build/)
       python scripts/build.py --check    do not write; exit 1 if build/ is not up to date
"""
import argparse
import hashlib
import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common  # noqa: E402
import build_references  # noqa: E402
import command_relations  # noqa: E402
import operations  # noqa: E402
import places as placesmod  # noqa: E402
import lineage  # noqa: E402
import coverage as coveragemod  # noqa: E402
import missions as missionsmod  # noqa: E402
import sidc as sidcmod  # noqa: E402
import commanders as commandersmod  # noqa: E402
import toe as toemod  # noqa: E402
import operation_extent  # noqa: E402
import operation_units  # noqa: E402
import export_oob  # noqa: E402

GEO_PROPS = ['claim_id', 'conflict_group_id', 'claim_status', 'unit_id', 'unit_name', 'nationality', 'domain', 'theater',
             'echelon', 'branch', 'date', 'commander', 'commander_person_id', 'commander_on_date', 'commander_on_date_person_id', 'commander_on_date_source', 'commander_on_date_basis', 'place_id', 'location_name', 'location_represents', 'precision_km', 'confidence',
             'event_type', 'current_activity', 'operation_id', 'operation', 'operation_type', 'campaign', 'operation_name', 'sub_operation_name', 'strength_status', 'location_date', 'location_basis',
             'location_temporal_offset_days', 'reference_ids', 'source_locator', 'sidc']
DERIVED = ['operation', 'operation_type', 'campaign', 'operation_name', 'sub_operation_name', 'operation_path']   # appended to all_claims.csv from data/operations.csv
NUMERIC = {'precision_km', 'confidence', 'location_temporal_offset_days'}
PLACES_OUT_HEADER = placesmod.HEADER + ['claims_count', 'units_count', 'claims_ground', 'claims_air', 'claims_naval', 'first_claim_date', 'last_claim_date']


def all_claims_header(stored):
    """Header of build/all_claims.csv: the claim-file columns with the derived ones at the place the stored column used to have (or next to the
    column they come from), then the derived operation columns."""
    after = {'nationality': ['domain'], 'parent_unit_id': ['command_relationships'], 'commander': ['commander_person_id', 'commander_on_date', 'commander_on_date_person_id', 'commander_on_date_source', 'commander_on_date_basis'], 'place_id': ['place_name', 'location_name'],
             'coord_override': ['country', 'region', 'coord_reference_id', 'coord_source_note'], 'engaged_note': ['engaged_with_names', 'strength_status'], 'composing_text': ['composing_units_names'],
             'location_basis': ['location_temporal_offset_days']}
    h = []
    for c in stored:
        h.append(c)
        h.extend(after.get(c, []))
    return h + DERIVED + ['sidc']   # sidc: derived by scripts/sidc.py (roadmap 410)


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
        cg = sum(1 for r in rs if r.get('domain') == 'ground')
        ca = sum(1 for r in rs if r.get('domain') == 'air')
        cn_ = sum(1 for r in rs if r.get('domain') == 'naval')
        row = [p[c] for c in placesmod.HEADER] + [str(len(rs)), str(len({r['unit_id'] for r in rs})), str(cg), str(ca), str(cn_), ds[0] if ds else '', ds[-1] if ds else '']
        out.append(row)
        props = {'place_id': p['place_id'], 'name': p['name'], 'alt_names': p['alt_names'] or None, 'kind': p['kind'], 'precision_km': num(p['precision_km']),
                 'country': p['country'], 'region': p['region'], 'claims_count': len(rs),
                 'claims_ground': cg, 'claims_air': ca, 'claims_naval': cn_}
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
          '`build/places.geojson` has one point per place. %d places and %d alias names for %d claims (all domains; claims_ground / claims_air / claims_naval are on each place row).' % (len(places.rows), alias_n, len(rows)), '',
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
COVERAGE_HEADER = ['unit_id', 'unit_name', 'nationality', 'domain', 'echelon', 'branch', 'record_status', 'formed_date', 'has_claim_file',
                   'claim_rows', 'first_claim_date', 'last_claim_date', 'initial_parent_unit_id']


def ech_rank(e):
    return ECHELON_ORDER.index(e) if e in ECHELON_ORDER else len(ECHELON_ORDER)


def coverage(claim_rows):
    """Return (rows for coverage.csv, text of docs/coverage.md). One row per unit, every domain."""
    _h, units = common.read_dicts(common.UNITS_CSV)
    per = {}
    for r in claim_rows:
        d = per.setdefault(r['unit_id'], [])
        d.append(r['date'])
    rows = []
    for u in units:
        ds = sorted(per.get(u['unit_id'], []))
        dom = common.unit_domain(u)
        rows.append([u['unit_id'], u['unit_name'], u['nationality'], dom, u['echelon'], u['branch'], u['record_status'], u['formed_date'],
                     'true' if ds else 'false', str(len(ds)), ds[0] if ds else '', ds[-1] if ds else '', u['initial_parent_unit_id']])
    rows.sort(key=lambda r: (r[3], r[2], ech_rank(r[4]), r[0]))
    by_dom = {}
    tally = {}
    for r in rows:
        t = tally.setdefault((r[3], r[2], r[4]), {'placeholder': 0, 'partial': 0, 'active': 0, 'claims': 0, 'dated': 0})
        t[r[6]] += 1
        t['claims'] += int(r[9])
        t['dated'] += 1 if r[7] else 0
        d = by_dom.setdefault(r[3], {'placeholder': 0, 'partial': 0, 'active': 0, 'claims': 0, 'dated': 0})
        d[r[6]] += 1
        d['claims'] += int(r[9])
        d['dated'] += 1 if r[7] else 0
    out = ['# Coverage', '',
           'Generated by `python scripts/build.py` from `data/units.csv` and `data/claims/`. Do not edit by hand. '
           'Per-unit detail is in `build/coverage.csv`. The table covers every domain (ground, air and naval); filter `domain` to recover a single-domain survey.', '',
           'A **placeholder** is a unit that exists in the table (identity, echelon, sometimes a formation date) but has no '
           'claim file: it says nothing about where the unit was. **active** units have a claim file; **partial** is reserved '
           'for claim files known to be incomplete. See "Placeholder units" in `docs/methodology.md`.', '',
           '| Domain | Placeholder | Partial | Active | Total | With formed_date | Claim rows |',
           '|---|---:|---:|---:|---:|---:|---:|']
    tot = {'placeholder': 0, 'partial': 0, 'active': 0, 'claims': 0, 'dated': 0}
    for dom in ('ground', 'air', 'naval'):
        t = by_dom.get(dom, tot)
        n = t['placeholder'] + t['partial'] + t['active']
        out.append('| %s | %d | %d | %d | %d | %d | %d |' % (dom, t['placeholder'], t['partial'], t['active'], n, t['dated'], t['claims']))
        for k in tot:
            tot[k] += t[k]
    out.append('| **All** | **%d** | **%d** | **%d** | **%d** | **%d** | **%d** |' % (
        tot['placeholder'], tot['partial'], tot['active'], tot['placeholder'] + tot['partial'] + tot['active'], tot['dated'], tot['claims']))
    out += ['',
            '| Domain | Nationality | Echelon | Placeholder | Partial | Active | Total | With formed_date | Claim rows |',
            '|---|---|---|---:|---:|---:|---:|---:|---:|']
    for (dom, nat, ech) in sorted(tally, key=lambda k: (('ground', 'air', 'naval').index(k[0]) if k[0] in ('ground', 'air', 'naval') else 9, k[1], ech_rank(k[2]))):
        t = tally[(dom, nat, ech)]
        out.append('| %s | %s | %s | %d | %d | %d | %d | %d | %d |' % (dom, nat, ech, t['placeholder'], t['partial'], t['active'],
                                                                     t['placeholder'] + t['partial'] + t['active'], t['dated'], t['claims']))
    out.append('| **All** | | | **%d** | **%d** | **%d** | **%d** | **%d** | **%d** |' % (
        tot['placeholder'], tot['partial'], tot['active'], tot['placeholder'] + tot['partial'] + tot['active'], tot['dated'], tot['claims']))
    return rows, ('\n'.join(out) + '\n').encode('utf-8')


def units_outputs(units_table):
    """build/units.csv and build/units.json: every unit in data/units.csv (all domains), with domain and scope filled (never blank),
    plus predecessor_unit_ids and successor_unit_ids from data/unit_lineage.csv (';'-separated in the CSV, lists in the JSON; ordered by effective date)."""
    uheader, urows = units_table
    nb = lineage.neighbours(lineage.load()[1])
    header = list(uheader) + ['predecessor_unit_ids', 'successor_unit_ids']
    rows, objs = [], []
    for u in urows:
        pre, suc = nb.get(u['unit_id'], ([], []))
        rows.append([u[c] for c in uheader] + [';'.join(pre), ';'.join(suc)])
        o = {c: u[c] for c in uheader}
        o['predecessor_unit_ids'], o['successor_unit_ids'] = list(pre), list(suc)
        objs.append(json.dumps(o, ensure_ascii=False, separators=(',', ':')))
    js = ('{"description":"data/units.csv with predecessor_unit_ids and successor_unit_ids from data/unit_lineage.csv",'
          '"units":[\n' + ',\n'.join(objs) + '\n]}\n').encode('utf-8')
    return common.csv_bytes(header, rows), js


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


def ship_classes_output():
    """build/ship_classes.csv: data/ship_classes.csv with every class row (naval; the classes are the table that ships link to)."""
    h, rows = common.read_rows(os.path.join(common.ROOT, 'data', 'ship_classes.csv'))
    return common.csv_bytes(h, rows)


def aircraft_types_output():
    """build/aircraft_types.csv: data/aircraft_types.csv with every type row (air; the types are the table that units link to through strength_json aircraft)."""
    h, rows = common.read_rows(os.path.join(common.ROOT, 'data', 'aircraft_types.csv'))
    return common.csv_bytes(h, rows)



RELEASE_JSON = os.path.join(common.ROOT, 'schema', 'release.json')
GENERATED_SKIP_PREFIX = 'WorldWar2/build/'
GENERATED_SKIP = {'WorldWar2/docs/coverage.md', 'WorldWar2/data/references.csv'}


def load_release():
    """schema_version, data_version and date_released from schema/release.json."""
    with open(RELEASE_JSON, encoding='utf-8') as f:
        return json.load(f)


def source_tree_sha256():
    """SHA-256 of tracked WorldWar2 files excluding generated build outputs (and coverage.md / references.csv).

    Used instead of git rev-parse HEAD so a committed manifest stays stable under --check: the
    manifest is itself a generated file, so including HEAD would always be stale after the commit
    that adds it.
    """
    repo = os.path.dirname(common.ROOT)
    proc = subprocess.run(['git', 'ls-files', '-z', 'WorldWar2'], cwd=repo, capture_output=True, check=True)
    paths = [p.decode() for p in proc.stdout.split(b'\0') if p]
    h = hashlib.sha256()
    for rel in sorted(paths):
        if rel.startswith(GENERATED_SKIP_PREFIX) or rel in GENERATED_SKIP:
            continue
        h.update(rel.encode('utf-8'))
        h.update(b'\0')
        with open(os.path.join(repo, rel), 'rb') as f:
            h.update(f.read())
        h.update(b'\n')
    return h.hexdigest()


def citation_pointer(release):
    """Short pointer at CITATION.cff; version follows schema/release.json data_version."""
    title = 'WWII Unit Locations: a claim-based dataset of unit positions (Western Front, 1944–1945)'
    author = 'Raymond Scott Starsman'
    path = os.path.join(common.ROOT, 'CITATION.cff')
    if os.path.isfile(path):
        fields = {}
        for line in open(path, encoding='utf-8'):
            if line.startswith('title:'):
                fields['title'] = line.split(':', 1)[1].strip().strip('"')
            elif line.startswith('  family-names:'):
                fields['family-names'] = line.split(':', 1)[1].strip().strip('"')
            elif line.startswith('  given-names:'):
                fields['given-names'] = line.split(':', 1)[1].strip().strip('"')
        if fields.get('title'):
            title = fields['title']
        names = (fields.get('given-names', '') + ' ' + fields.get('family-names', '')).strip()
        if names:
            author = names
    return {'file': 'CITATION.cff', 'title': title, 'version': release['data_version'], 'author': author}


def file_stats(key, data):
    """One files[] entry for an outputs() item. Paths are relative to WorldWar2/."""
    path = key[3:] if key.startswith('../') else 'build/' + key
    entry = {'path': path, 'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()}
    if path.endswith('.md'):
        return entry
    if path.endswith('.csv'):
        entry['rows'] = max(data.count(b'\n') - 1, 0)
        return entry
    if not (path.endswith('.geojson') or path.endswith('.json')):
        return entry
    obj = json.loads(data)
    if path.endswith('.geojson'):
        entry['features'] = len(obj.get('features', []))
        return entry
    if isinstance(obj, list):
        entry['rows'] = len(obj)
    elif isinstance(obj, dict):
        if isinstance(obj.get('claims'), list):
            entry['rows'] = len(obj['claims'])
        elif isinstance(obj.get('units'), list):
            entry['rows'] = len(obj['units'])
        elif isinstance(obj.get('trees'), list):
            entry['rows'] = len(obj['trees'])
        elif isinstance(obj.get('features'), list):
            entry['features'] = len(obj['features'])
    return entry


def manifest_bytes(out):
    """Deterministic build/manifest.json for the files already in *out* (does not list itself)."""
    release = load_release()
    man = {
        'schema_version': release['schema_version'],
        'data_version': release['data_version'],
        'generated_at': release['date_released'] + 'T00:00:00Z',
        'source_tree_sha256': source_tree_sha256(),
        'license': 'CC-BY-SA-4.0',
        'citation': citation_pointer(release),
        'files': [file_stats(k, out[k]) for k in sorted(out)],
    }
    return (json.dumps(man, ensure_ascii=False, indent=2) + '\n').encode('utf-8')


def outputs():
    """Return {relative path: bytes} for every generated file (paths under docs/ are relative to the repository root)."""
    header, rows = common.load_all_claims()
    uh, urows = common.read_dicts(common.UNITS_CSV)
    for u in urows:
        u['domain'] = common.unit_domain(u)
        u['scope'] = common.unit_scope(u)
    all_units_rows = {u['unit_id']: u for u in urows}
    for r in rows:
        r['domain'] = all_units_rows[r['unit_id']]['domain']
    ops = operations.load()
    for r in rows:
        r.update(ops.labels(r['operation_id'], r['date']))
    coder = sidcmod.Coder()
    for r in rows:
        r['sidc'] = coder.claim_sidc(all_units_rows[r['unit_id']], r)
    ph, people_rows = commandersmod.load_people()
    th, tenure_rows = commandersmod.load_tenures()
    lh, commander_links = commandersmod.load_links()
    people_rows = people_rows or []
    tenure_rows = tenure_rows or []
    commander_links = commander_links or []
    commandersmod.attach_person_ids(rows, tenure_rows, commander_links)
    commandersmod.attach_commander_on_date(rows, tenure_rows, commander_links, people_rows)
    header = all_claims_header(header)   # the derived columns (command_relationships, place and derived-value columns, operations, domain) are not claim-file columns
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
    out.update(coveragemod.outputs(urows, rows))
    all_units = all_units_rows
    out['units.csv'], out['units.json'] = units_outputs((uh, urows))
    symbol_rows = coder.unit_rows(urows)
    out['unit_symbols.csv'] = common.csv_bytes(sidcmod.UNIT_SYMBOLS_HEADER, symbol_rows)
    out['ship_classes.csv'] = ship_classes_output()
    out['aircraft_types.csv'] = aircraft_types_output()
    out['missions.csv'] = common.csv_bytes(missionsmod.BUILD_HEADER, missionsmod.build_rows())   # data/missions (J1); never part of the claims or relations
    crel = command_relations.load()
    all_rel = command_relations.derived_rows(crel, all_units, rows, None)
    organic_rel = command_relations.derived_rows(crel, all_units, rows, None, organic=True)
    out['command_relations.csv'] = common.csv_bytes(command_relations.DERIVED_HEADER, all_rel)
    out['organic_relations.csv'] = common.csv_bytes(command_relations.DERIVED_HEADER, organic_rel)
    out['who_controls_overrides.csv'] = open(command_relations.OVERRIDE_CSV, 'rb').read() if os.path.isfile(command_relations.OVERRIDE_CSV) else common.csv_bytes(['relation_id'], [])   # verbatim copy of data/who_controls_overrides.csv; read by scripts/who_controls.py
    out['people.csv'] = common.csv_bytes(commandersmod.PEOPLE_BUILD_HEADER, commandersmod.derived_people(people_rows, tenure_rows))
    out['unit_commanders.csv'] = common.csv_bytes(commandersmod.TENURE_BUILD_HEADER, commandersmod.derived_tenures(tenure_rows, people_rows, commander_links, all_units_rows))
    toe_templates = toemod.load_templates()[1] or []
    toe_assignments = toemod.load_assignments()[1] or []
    out.update(toemod.build_outputs(toe_templates, toe_assignments))
    places_rows = {p['place_id']: p for p in common.read_dicts(os.path.join(common.ROOT, 'data', 'places.csv'))[1]}
    mission_rows = missionsmod.load()
    op_rows, op_md, _qc = operation_extent.operations_table(ops, rows, mission_rows, all_units_rows, places_rows)
    out['operations.csv'] = common.csv_bytes(operation_extent.BUILD_HEADER, op_rows)
    out['operations.geojson'] = operation_extent.operations_geojson(op_rows, places_rows)
    ou_rows = operation_units.operation_unit_rows(ops, rows, mission_rows, all_units_rows,
                                                  people=people_rows, tenures=tenure_rows)
    out['operation_units.csv'] = common.csv_bytes(operation_units.BUILD_HEADER, ou_rows)
    as_dicts = lambda header, rels: [dict(zip(header, r)) for r in rels]
    oob_ctx = export_oob.context_from_build_outputs(
        as_dicts(command_relations.DERIVED_HEADER, all_rel),
        as_dicts(command_relations.DERIVED_HEADER, organic_rel),
        common.read_dicts(command_relations.OVERRIDE_CSV)[1] if os.path.isfile(command_relations.OVERRIDE_CSV) else [],
        all_units_rows, rows, tenure_rows, people_rows,
        as_dicts(sidcmod.UNIT_SYMBOLS_HEADER, symbol_rows),
        ou_rows)
    out.update(export_oob.flagship_outputs(oob_ctx))
    pl_rows, pl_geo, pl_md = places_outputs(rows)
    out['places.csv'] = common.csv_bytes(PLACES_OUT_HEADER, pl_rows)
    out['places.geojson'] = pl_geo
    out['../docs/coverage.md'] = cov_md + op_md + pl_md
    # references: data/references.csv (metadata + counts) and the claim/unit -> reference links (see build_references.py)
    for k, data in build_references.outputs().items():
        out[k[len('build/'):] if k.startswith('build/') else '../' + k] = data
    out['manifest.json'] = manifest_bytes(out)
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
