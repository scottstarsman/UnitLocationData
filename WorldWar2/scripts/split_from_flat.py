#!/usr/bin/env python3
"""Show how the per-unit master files were made from the flat v5 CSV (reproducibility).

Input : archive/v5_flat/ww2_west_1944-06_v5.csv   (flat claims, 212 rows, 30 columns)
        archive/v5_flat/units_v5.csv              (unit table from the proof of concept)
Output: data/claims/<nationality>/<unit_id>.csv   (one file per unit that has claims)
        data/units.csv

Changes made on the way (everything else is copied unchanged):
  * adds the `theater` column after `date` (every row is western_europe in this import)
  * writes one file per unit, rows sorted by date then claim_id, same header everywhere
  * builds data/units.csv: adds theater, parent_unit_id (from parent_division_unit_id),
    parent_only (true for units with no rows left), drops v5-only bookkeeping columns

Usage:  python scripts/split_from_flat.py [--out DIR]
By default it writes into the repository (overwriting data/). Use --out to write elsewhere,
for example to check that the committed data/ is reproducible:
    python scripts/split_from_flat.py --out /tmp/check && diff -r /tmp/check/data data
"""
import argparse
import csv
import os
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common  # noqa: E402

FLAT = os.path.join(common.ROOT, 'archive', 'v5_flat', 'ww2_west_1944-06_v5.csv')
UNITS_FLAT = os.path.join(common.ROOT, 'archive', 'v5_flat', 'units_v5.csv')
THEATER = 'western_europe'
UNIT_HEADER = ['unit_id', 'unit_name', 'nationality', 'echelon', 'branch', 'theater', 'parent_unit_id', 'parent_only']


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--out', default=common.ROOT, help='output root (default: repository root)')
    args = ap.parse_args()

    header_flat, flat = common.read_dicts(FLAT)
    header = common.field_names(common.load_schema('claims'))
    expected = [c for c in header if c != 'theater']
    if header_flat != expected:
        sys.exit('flat header does not match schema minus theater')

    claims_dir = os.path.join(args.out, 'data', 'claims')
    if os.path.isdir(claims_dir):
        shutil.rmtree(claims_dir)
    by_unit = {}
    for r in flat:
        r['theater'] = THEATER
        by_unit.setdefault(r['unit_id'], []).append(r)
    for uid, rows in by_unit.items():
        rows.sort(key=common.sort_key)
        nat = rows[0]['nationality'].lower()
        d = os.path.join(claims_dir, nat)
        os.makedirs(d, exist_ok=True)
        with open(os.path.join(d, uid + '.csv'), 'wb') as f:
            f.write(common.csv_bytes(header, [[r[c] for c in header] for r in rows]))

    _h, units = common.read_dicts(UNITS_FLAT)
    out = []
    for u in sorted(units, key=lambda x: x['unit_id']):
        out.append([u['unit_id'], u['unit_name'], u['nationality'], u['echelon'], u['branch'], THEATER,
                    u['parent_division_unit_id'], 'true' if u['kind'].startswith('parent_only') else 'false'])
    os.makedirs(os.path.join(args.out, 'data'), exist_ok=True)
    with open(os.path.join(args.out, 'data', 'units.csv'), 'wb') as f:
        f.write(common.csv_bytes(UNIT_HEADER, out))
    print('wrote %d claim files, %d units, %d claims' % (len(by_unit), len(out), len(flat)))


if __name__ == '__main__':
    main()
