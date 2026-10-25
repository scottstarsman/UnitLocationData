#!/usr/bin/env python3
"""Migration: split the free-text `parent_formation` column into `parent_unit_id` and `command_relationships`.

This documents (and performs) the one-off transformation that replaced

    parent_formation   free text, e.g. "German 2nd SS Panzer Division Das Reich (GER-SSPZ-002D); attached to German Panzer Lehr Division (GER-PZ-LEHRD)"

with two columns in the same position:

    parent_unit_id        one unit_id from data/units.csv: the operational parent on the row's date
                          (the formation the unit was attached to / operating under); blank = none
                          (top-level HQ), "unknown" = not verified.
    command_relationships JSON list of {"unit_id", "name", "relationship", "note"?}; "unknown" or blank
                          if nothing is known. Relationship values: see schema/vocabularies.json.

Conversion rules (applied to the old text; nothing is added that the old text or the row's notes do not say):
  * "unknown"                           -> parent_unit_id "unknown", command_relationships "unknown".
  * "A (id)"                            -> parent A, relationship "organic" (the standing parent named by the old text).
  * "A (id); attached to B (id)"        -> parent B (operational), relationships: A organic, B attached.
  * "A (id); B (id) (corps reserve)"    -> parent B, relationships: A organic, B reserve.
  * "OKW (central mobile reserve)"      -> parent OKW, relationship reserve.
  * "A (id); B (id)" (no qualifier)     -> parent A; B is recorded with relationship "unknown", except the rows in
                                           OVERRIDES where the row's notes show who controlled the unit.
  * Parents named without an id in the old text (Fifteenth Army, OKW, SHAEF) were added to data/units.csv as
    parent_only units (ids in NEW_UNITS).
  * US First Army under 21st Army Group is recorded as operational_control (it was never a permanent part of it).

The script works on a repository root and rewrites data/claims/**/*.csv and data/units.csv in place.
It refuses to run on files that already have the new columns. scripts/split_from_flat.py calls it so that the
archive flat v5 files still reproduce data/ exactly.

Usage:  python scripts/migrate_parent_formation.py [--root DIR]
"""
import argparse
import csv
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common  # noqa: E402

UNIT_HEADER = ['unit_id', 'unit_name', 'nationality', 'echelon', 'branch', 'theater', 'parent_unit_id', 'parent_only']

# (unit_id, unit_name, nationality, echelon, branch): parents that the old text named without an id.
NEW_UNITS = [
    ('ALL-SHAEF-000H', 'Supreme Headquarters Allied Expeditionary Force (SHAEF)', 'Allied', 'other', 'Army'),
    ('GER-ARMY-015A', 'Fifteenth Army', 'Germany', 'army', 'Army'),
    ('GER-OKW-000H', 'Oberkommando der Wehrmacht (OKW)', 'Germany', 'other', 'Army'),
]
BY_NAME = {'SHAEF': 'ALL-SHAEF-000H', 'Fifteenth Army': 'GER-ARMY-015A', 'OKW': 'GER-OKW-000H'}

# Rows whose old text has two unqualified parents; the notes say who controlled the battle group.
OVERRIDES = {
    'C0035': ('operational_control', 'Seventh Army (Dollmann) ordered the 265th Kampfgruppe forward, per the claim notes'),
    'C0050': ('operational_control', 'Seventh Army (Dollmann) sent Kampfgruppe Heintz from Brittany, per the claim notes'),
}
# Notes copied from the claim notes for specific (claim_id, unit_id of the entry).
NOTES = {
    ('C0122', 'GER-INF-352D'): 'CMH ch. IX: attached to the 352nd Division',
    ('C0172', 'GER-PZ-LEHRD'): 'Placed under Panzer Lehr on arrival',
    ('C0198', 'GER-SSPZ-002C'): 'Transferred to II SS Panzer Corps on 29 June',
    ('C0183', 'GER-SSPZ-012D'): 'Vanguard attached to the 12th SS Panzer Division',
    ('C0212', 'US-ABN-101D'): 'CMH ch. IX: Combat Command A was still attached to the 101st Airborne Division',
    ('C0034', 'GER-INF-709D'): 'Formed by the 709th Division commander (Schlieben) from the 922nd Grenadier Regiment (243rd Division) and a battalion of the 919th',
}
FIRST_ARMY_NOTE = 'US First Army served under 21st Army Group until 12th Army Group became operational (1 August 1944)'

SEG = re.compile(r'^(?P<att>attached to )?(?P<name>.*?)(?: \((?P<id>[A-Z]{2,4}-[A-Z0-9-]+)\))?(?: \((?P<qual>[^()]*)\))?$')
CHANGED = ('parent_unit_id', 'command_relationships')


def parse(text):
    segs = []
    for part in text.split('; '):
        m = SEG.match(part)
        name, uid, qual = m.group('name'), m.group('id'), m.group('qual')
        if uid is None and name in BY_NAME:
            uid = BY_NAME[name]
            name = [u[1] for u in NEW_UNITS if u[0] == uid][0]
        segs.append({'attached': bool(m.group('att')), 'name': name, 'id': uid, 'qual': qual or ''})
    return segs


def entry(seg, rel, note=None, claim_id=None):
    note = NOTES.get((claim_id, seg['id']), note)
    e = {'unit_id': seg['id'], 'name': seg['name'], 'relationship': rel}
    if note:
        e['note'] = note
    return e


def convert(claim_id, unit_id, text):
    """Return (parent_unit_id, command_relationships) for one row."""
    if text == 'unknown':
        return 'unknown', 'unknown'
    segs = parse(text)
    for s in segs:
        if s['id'] is None:
            return 'unknown', json.dumps([{'unit_id': None, 'name': s['name'], 'relationship': 'unknown'}], ensure_ascii=False, separators=(',', ':'))
    first = segs[0]
    if len(segs) == 1:
        if 'reserve' in first['qual']:
            rels = [entry(first, 'reserve', claim_id=claim_id)]
        elif first['id'] == 'UK-AG-021G' and unit_id == 'US-ARMY-001A':
            rels = [entry(first, 'operational_control', FIRST_ARMY_NOTE, claim_id)]
        else:
            rels = [entry(first, 'organic', claim_id=claim_id)]
        parent = first['id']
    elif len(segs) == 2 and segs[1]['attached']:
        rels = [entry(first, 'organic', claim_id=claim_id), entry(segs[1], 'attached', claim_id=claim_id)]
        parent = segs[1]['id']
    elif len(segs) == 2 and 'reserve' in segs[1]['qual']:
        rels = [entry(first, 'organic', claim_id=claim_id), entry(segs[1], 'reserve', claim_id=claim_id)]
        parent = segs[1]['id']
    elif len(segs) == 2 and claim_id in OVERRIDES:
        rel, note = OVERRIDES[claim_id]
        rels = [entry(first, 'organic', claim_id=claim_id), entry(segs[1], rel, note, claim_id)]
        parent = segs[1]['id']
    elif len(segs) == 2:
        rels = [entry(first, 'organic', claim_id=claim_id),
                entry(segs[1], 'unknown', 'Higher formation listed with the parent in the original text; its relationship to the unit is not stated', claim_id)]
        parent = first['id']
    else:
        raise ValueError('cannot convert %r' % text)
    return parent, json.dumps(rels, ensure_ascii=False, separators=(',', ':'))


def migrate(root):
    claims_dir = os.path.join(root, 'data', 'claims')
    units_csv = os.path.join(root, 'data', 'units.csv')
    n = 0
    for dp, _d, fs in os.walk(claims_dir):
        for fn in sorted(fs):
            if not fn.endswith('.csv'):
                continue
            path = os.path.join(dp, fn)
            header, rows = common.read_rows(path)
            if 'parent_formation' not in header:
                sys.exit('%s already migrated (no parent_formation column)' % path)
            i = header.index('parent_formation')
            new_header = header[:i] + list(CHANGED) + header[i + 1:]
            ci, ui = header.index('claim_id'), header.index('unit_id')
            out = []
            for r in rows:
                parent, rels = convert(r[ci], r[ui], r[i])
                out.append(r[:i] + [parent, rels] + r[i + 1:])
                n += 1
            with open(path, 'wb') as f:
                f.write(common.csv_bytes(new_header, out))
    uheader, urows = common.read_rows(units_csv)
    have = {r[0] for r in urows}
    for uid, name, nat, ech, branch in NEW_UNITS:
        if uid not in have:
            urows.append([uid, name, nat, ech, branch, 'western_europe', '', 'true'])
    urows.sort(key=lambda r: r[0])
    with open(units_csv, 'wb') as f:
        f.write(common.csv_bytes(uheader, urows))
    return n


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--root', default=common.ROOT, help='repository root to migrate in place (default: this repository)')
    args = ap.parse_args()
    print('migrated %d claim rows' % migrate(args.root))


if __name__ == '__main__':
    main()
