#!/usr/bin/env python3
"""Validate every claim file and the unit table against the schema. Standard library only.

Checks: header and field count of every file, field types, booleans, lat/long ranges,
controlled vocabularies, unique claim_ids across the repository, unit_id matches both the
file name and data/units.csv, rows sorted by date then claim_id, conflict-group integrity,
strength_json structure, parent_unit_id resolves, command_relationships is valid JSON with allowed keys,
relationship values and resolving unit_ids, every row has a source URL.

Usage: python scripts/validate.py        (exit code 0 = OK, 1 = problems found)
"""
import datetime
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common  # noqa: E402

errors = []


def err(where, msg):
    errors.append('%s: %s' % (where, msg))


def rel(path):
    return os.path.relpath(path, common.ROOT)


def is_number(s):
    try:
        float(s)
        return s.strip() == s and s.lower() not in ('nan', 'inf', '-inf', 'infinity', '-infinity')
    except ValueError:
        return False


def check_type(where, f, value):
    """Check one non-empty value against its schema field (type, format, constraints, vocabulary)."""
    t = f['type']
    c = f.get('constraints', {})
    if t == 'date':
        try:
            datetime.datetime.strptime(value, f.get('format', '%Y-%m-%d'))
            if not re.fullmatch(r'\d{4}-\d{2}-\d{2}', value):
                raise ValueError
        except ValueError:
            err(where, '%s: %r is not a valid date YYYY-MM-DD' % (f['name'], value))
    elif t == 'number':
        if not is_number(value):
            err(where, '%s: %r is not a number' % (f['name'], value))
        else:
            x = float(value)
            if 'minimum' in c and x < c['minimum']:
                err(where, '%s: %s below minimum %s' % (f['name'], value, c['minimum']))
            if 'maximum' in c and x > c['maximum']:
                err(where, '%s: %s above maximum %s' % (f['name'], value, c['maximum']))
    elif t == 'boolean':
        if value not in f.get('trueValues', ['true']) + f.get('falseValues', ['false']):
            err(where, '%s: %r must be lowercase true or false' % (f['name'], value))
    if 'pattern' in c and not re.fullmatch(c['pattern'], value):
        err(where, '%s: %r does not match pattern %s' % (f['name'], value, c['pattern']))


def check_vocab(where, f, value, vocabs):
    name = f.get('vocabulary')
    if name:
        allowed = vocabs[name]['values']
        if value not in allowed:
            err(where, '%s: %r not in vocabulary %s %s' % (f['name'], value, name, sorted(allowed)))


def check_row(where, row, fields, vocabs):
    for f in fields:
        v = row.get(f['name'], '')
        if v == '':
            if f.get('constraints', {}).get('required'):
                err(where, '%s is required but empty' % f['name'])
            continue
        if v != v.strip():
            err(where, '%s has leading or trailing whitespace' % f['name'])
        check_type(where, f, v)
        check_vocab(where, f, v, vocabs)


def check_strength_json(where, s, vocabs):
    if s == '':
        return
    try:
        d = json.loads(s)
    except ValueError as e:
        err(where, 'strength_json is not valid JSON (%s)' % e)
        return
    if not isinstance(d, dict):
        err(where, 'strength_json must be a JSON object')
        return
    allowed = {'basis', 'as_of', 'personnel', 'vehicles', 'vehicle_count_type', 'source', 'note'}
    for k in d:
        if k not in allowed:
            err(where, 'strength_json: unknown key %r' % k)
    if d.get('basis') not in vocabs['strength_json_basis']['values']:
        err(where, 'strength_json: basis %r invalid' % d.get('basis'))
    try:
        datetime.datetime.strptime(str(d.get('as_of')), '%Y-%m-%d')
    except ValueError:
        err(where, 'strength_json: as_of must be YYYY-MM-DD')
    if not isinstance(d.get('source'), str) or not d.get('source'):
        err(where, 'strength_json: source is required')
    if 'note' in d and not isinstance(d['note'], str):
        err(where, 'strength_json: note must be a string')
    if 'personnel' in d and (not isinstance(d['personnel'], int) or isinstance(d['personnel'], bool) or d['personnel'] < 0):
        err(where, 'strength_json: personnel must be a non-negative integer')
    if 'vehicles' in d:
        v = d['vehicles']
        if not isinstance(v, dict) or not v:
            err(where, 'strength_json: vehicles must be a non-empty object')
        else:
            for k, n in v.items():
                if not isinstance(n, int) or isinstance(n, bool) or n < 0:
                    err(where, 'strength_json: vehicles[%r] must be a non-negative integer' % k)
        if d.get('vehicle_count_type') not in vocabs['strength_json_vehicle_count_type']['values']:
            err(where, 'strength_json: vehicle_count_type required with vehicles and must be in the vocabulary')
    elif 'vehicle_count_type' in d:
        err(where, 'strength_json: vehicle_count_type without vehicles')
    if 'personnel' not in d and 'vehicles' not in d:
        err(where, 'strength_json: needs personnel and/or vehicles')


REL_KEYS = {'unit_id', 'name', 'relationship', 'note'}


def check_command_relationships(where, row, units, vocabs):
    """parent_unit_id is a unit id (resolves), blank or 'unknown'; command_relationships is a JSON list."""
    pid, s = row['parent_unit_id'], row['command_relationships']
    if pid not in ('', 'unknown'):
        if pid not in units:
            err(where, 'parent_unit_id %s not in units.csv' % pid)
        if pid == row['unit_id']:
            err(where, 'parent_unit_id is the unit itself')
    if s in ('', 'unknown'):
        if pid not in ('', 'unknown'):
            err(where, 'parent_unit_id %s needs a command_relationships entry for it' % pid)
        return
    try:
        d = json.loads(s)
    except ValueError as e:
        err(where, 'command_relationships is not valid JSON or "unknown" (%s)' % e)
        return
    if not isinstance(d, list) or not d:
        err(where, 'command_relationships must be a non-empty JSON list')
        return
    ids = []
    for e in d:
        if not isinstance(e, dict):
            err(where, 'command_relationships entries must be objects')
            continue
        for k in e:
            if k not in REL_KEYS:
                err(where, 'command_relationships: unknown key %r' % k)
        for k in ('unit_id', 'name', 'relationship'):
            if k not in e:
                err(where, 'command_relationships: entry missing %r' % k)
        uid = e.get('unit_id')
        if uid is not None:
            if not isinstance(uid, str) or uid not in units:
                err(where, 'command_relationships: unit_id %r not in units.csv' % (uid,))
            elif uid == row['unit_id']:
                err(where, 'command_relationships: the unit is listed as its own parent')
            ids.append(uid)
        if not isinstance(e.get('name'), str) or not e.get('name'):
            err(where, 'command_relationships: name must be a non-empty string')
        if e.get('relationship') not in vocabs['relationship']['values']:
            err(where, 'command_relationships: relationship %r not in vocabulary relationship' % e.get('relationship'))
        if 'note' in e and not isinstance(e['note'], str):
            err(where, 'command_relationships: note must be a string')
    if len(ids) != len(set(ids)):
        err(where, 'command_relationships lists the same unit_id twice')
    if pid not in ('', 'unknown') and pid not in ids:
        err(where, 'parent_unit_id %s is not listed in command_relationships' % pid)
    u = units.get(row['unit_id'])
    if u and u['parent_unit_id'] and not any(
            isinstance(e, dict) and e.get('unit_id') == u['parent_unit_id'] and e.get('relationship') == 'organic' for e in d):
        err(where, 'units.csv parent_unit_id %s must appear as an organic entry in command_relationships' % u['parent_unit_id'])


def main():
    claims_schema = common.load_schema('claims')
    units_schema = common.load_schema('units')
    vocabs = common.load_vocabularies()
    cfields = claims_schema['fields']
    cheader = [f['name'] for f in cfields]
    ufields = units_schema['fields']
    uheader = [f['name'] for f in ufields]

    # ---- units.csv ----
    units = {}
    if not os.path.isfile(common.UNITS_CSV):
        err('data/units.csv', 'missing')
    else:
        header, rows = common.read_rows(common.UNITS_CSV)
        if header != uheader:
            err('data/units.csv', 'header %s != schema %s' % (header, uheader))
        for i, r in enumerate(rows, start=2):
            where = 'data/units.csv line %d' % i
            if len(r) != len(uheader):
                err(where, 'expected %d fields, found %d' % (len(uheader), len(r)))
                continue
            row = dict(zip(header, r))
            check_row(where, row, ufields, vocabs)
            if row['unit_id'] in units:
                err(where, 'duplicate unit_id %s' % row['unit_id'])
            units[row['unit_id']] = row
        ids = list(units)
        if ids != sorted(ids):
            err('data/units.csv', 'rows must be sorted by unit_id')
        for uid, u in units.items():
            p = u['parent_unit_id']
            if p and p not in units:
                err('data/units.csv', 'parent_unit_id %s of %s not in units' % (p, uid))
            if p == uid:
                err('data/units.csv', '%s is its own parent' % uid)

    # ---- claim files ----
    files = common.claim_files()
    if not files:
        err('data/claims', 'no claim files found')
    seen_ids = {}
    all_rows = []
    unit_with_file = set()
    for path in files:
        r_path = rel(path)
        parts = r_path.split(os.sep)
        if len(parts) != 4 or parts[:2] != ['data', 'claims']:
            err(r_path, 'claim files must be data/claims/<nationality>/<unit_id>.csv')
            continue
        folder, stem = parts[2], parts[3][:-4]
        if folder != folder.lower():
            err(r_path, 'nationality folder must be lowercase')
        header, rows = common.read_rows(path)
        if header != cheader:
            err(r_path, 'header does not match schema/claims.schema.json (expected %s)' % cheader)
            continue
        if stem not in units:
            err(r_path, 'unit_id %s (file name) not in data/units.csv' % stem)
        else:
            unit_with_file.add(stem)
            if units[stem]['parent_only'] == 'true':
                err(r_path, 'unit is marked parent_only in units.csv but has a claim file')
            if units[stem]['nationality'].lower() != folder:
                err(r_path, 'folder %s does not match unit nationality %s' % (folder, units[stem]['nationality']))
        if not rows:
            err(r_path, 'file has no rows')
        prev = None
        for i, r in enumerate(rows, start=2):
            where = '%s line %d' % (r_path, i)
            if len(r) != len(cheader):
                err(where, 'expected %d fields, found %d' % (len(cheader), len(r)))
                continue
            row = dict(zip(header, r))
            check_row(where, row, cfields, vocabs)
            cid = row['claim_id']
            if cid in seen_ids:
                err(where, 'duplicate claim_id %s (also in %s)' % (cid, seen_ids[cid]))
            seen_ids[cid] = r_path
            if row['unit_id'] != stem:
                err(where, 'unit_id %s does not match file name %s' % (row['unit_id'], stem))
            u = units.get(row['unit_id'])
            if u:
                for col in ('unit_name', 'nationality', 'echelon', 'branch'):
                    if row[col] != u[col]:
                        err(where, '%s %r differs from units.csv %r' % (col, row[col], u[col]))
            k = (row['date'], row['claim_id'])
            if prev and k < prev:
                err(where, 'rows must be sorted by date then claim_id')
            prev = k
            if not re.search(r'https?://', row['source']):
                err(where, 'source must contain at least one URL')
            if row['claim_status'] != 'preferred' and not row['conflict_group_id']:
                err(where, 'claim_status %s requires a conflict_group_id' % row['claim_status'])
            check_strength_json(where, row['strength_json'], vocabs)
            check_command_relationships(where, row, units, vocabs)
            row['_where'] = where
            all_rows.append(row)

    for uid, u in units.items():
        if u['parent_only'] == 'false' and uid not in unit_with_file:
            err('data/units.csv', '%s has parent_only=false but no claim file' % uid)

    # ---- conflict groups ----
    groups = {}
    for r in all_rows:
        if r['conflict_group_id']:
            groups.setdefault(r['conflict_group_id'], []).append(r)
    for g, rs in sorted(groups.items()):
        where = 'conflict group %s' % g
        if len(rs) < 2:
            err(where, 'a conflict group needs at least two claims')
        if len({r['unit_id'] for r in rs}) != 1:
            err(where, 'all claims of a group must be about the same unit_id')
        st = [r['claim_status'] for r in rs]
        if st.count('preferred') > 1:
            err(where, 'more than one preferred claim')
        if 'preferred' in st and 'disputed' in st:
            err(where, 'a group with a preferred claim cannot also contain disputed claims')
        if 'preferred' not in st and any(s != 'disputed' for s in st):
            err(where, 'a group with no preferred claim must be all disputed')
        if len({r['date'] for r in rs}) < 2 and len({r['latitude'] + r['longitude'] for r in rs}) < 2:
            err(where, 'competing claims should differ in date or place')

    if errors:
        for e in errors:
            print('ERROR', e)
        print('\nFAILED: %d problem(s) in %d claim file(s)' % (len(errors), len(files)))
        return 1
    print('OK: %d claim files, %d claims, %d units, %d conflict groups' % (len(files), len(all_rows), len(units), len(groups)))
    return 0


if __name__ == '__main__':
    sys.exit(main())
