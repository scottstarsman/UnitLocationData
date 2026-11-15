#!/usr/bin/env python3
"""One-off migration "normalize-cheap-fixes" (already applied; kept for the record).

NOTE (places-table): Historical, one-off: it was written for claim files that still had `location_name`, `strength_status`, `location_temporal_offset_days` and the `; coords:` tail of `source`; since `places-table` those are a place (data/places.csv, scripts/migrate_places.py) and derived values (scripts/places.py), so it cannot be run on the current layout.
NOTE (unit-ids-in-text-columns): Historical, one-off: it predates the claim columns `engaged_note` and `composing_text` and the unit ids in `engaged_with` / `composing_units`; do not run it on the current files (its output is checked by the validator, which now expects the new layout).

NOTE: Historical, one-off: it edited the `command_relationships` column of the claim files; since `command-relations-table` the column no longer exists (see scripts/migrate_command_relations.py). It cannot be run on the current layout.

1. data/claims/*: command_relationships entries lose their redundant display `name` (the unit's name comes from data/units.csv).
   An entry with unit_id null (a formation that is not a unit) keeps its explanation as the `note`. The sentinel `unknown` in
   parent_unit_id (and the plain-text `unknown` in command_relationships) becomes blank plus one explicit entry
   {"unit_id": null, "relationship": "unknown", "note": "parent not verified"}.
2. data/units.csv: the `parent_only` column is dropped (it was identical to record_status == placeholder on every row).
3. data/nationalities.csv: new lookup table (code, name, adjective, alt_adjectives, alliance, kind, note).
4. data/operations.csv: nationality_scope `German` becomes `Germany` (the nationality name; `Allied` and `All` are unchanged).

Usage: python scripts/migrate_normalize.py [--dry-run]
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common  # noqa: E402

NAT_HEADER = ['code', 'name', 'adjective', 'alt_adjectives', 'alliance', 'kind', 'note']   # historic one-off migration; the live table no longer has `alliance` (retired 15 November 2026)
NATIONALITIES = [
    ['ALL', 'Allied', 'Allied', '', 'Allied', 'multinational',
     'Combined Allied headquarters that belong to no single nation, for example SHAEF and AFHQ (folder allied; no claim files yet). Kept as an explicit value; the unit records do not say which nation staffed them.'],
    ['BEL', 'Belgium', 'Belgian', '', 'Allied', 'nation', 'Belgian formations (folder belgium).'],
    ['CAN', 'Canada', 'Canadian', '', 'Allied', 'nation', 'Canada (folder canada).'],
    ['CZ', 'Czechoslovakia', 'Czechoslovak', '', 'Allied', 'nation', 'Czechoslovak formations (folder czechoslovakia).'],
    ['FR', 'France', 'French', '', 'Allied', 'nation', 'Free French and French Army formations (folder france).'],
    ['GER', 'Germany', 'German', '', 'Axis', 'nation', 'Germany, including Waffen-SS and Luftwaffe ground formations (folder germany). The unit id prefix is GER; the nationality value is Germany; the adjective used in names is German.'],
    ['NL', 'Netherlands', 'Dutch', '', 'Allied', 'nation', 'Dutch formations (folder netherlands).'],
    ['POL', 'Poland', 'Polish', '', 'Allied', 'nation', 'Polish formations serving under British or Allied command (folder poland).'],
    ['UK', 'UK', 'British', '', 'Allied', 'nation', 'United Kingdom and Commonwealth formations serving in British armies except those with their own entry (folder uk).'],
    ['US', 'US', 'US', 'American', 'Allied', 'nation', 'United States (folder us).'],
]
UNKNOWN_NOTE = 'parent not verified'


def clean_entries(s):
    """Return (new command_relationships text, counts) for one cell."""
    if s == '':
        return s, {}
    cnt = {}
    if s == 'unknown':
        cnt['sentinel_cell'] = 1
        return json.dumps([{'unit_id': None, 'relationship': 'unknown', 'note': UNKNOWN_NOTE}], ensure_ascii=False, separators=(',', ':')), cnt
    out = []
    for e in json.loads(s):
        new = {}
        for k, v in e.items():
            if k == 'name':
                cnt['name_dropped'] = cnt.get('name_dropped', 0) + 1
                if e.get('unit_id') is None:
                    label = v
                    note = e.get('note')
                    new['note'] = (label + ': ' + note) if note else label
                    cnt['null_id'] = cnt.get('null_id', 0) + 1
                continue
            if k == 'note' and e.get('unit_id') is None and 'name' in e:
                continue  # merged above
            new[k] = v
        if e.get('unit_id') is None and 'name' in e and 'note' not in new:
            new['note'] = e['name']
        out.append(new)
    return json.dumps(out, ensure_ascii=False, separators=(',', ':')), cnt


def main():
    dry = '--dry-run' in sys.argv[1:]
    total = {}
    # 1. claims
    for p in common.claim_files():
        h, rows = common.read_rows(p)
        ix = {c: i for i, c in enumerate(h)}
        changed = False
        for r in rows:
            if r[ix['parent_unit_id']] == 'unknown':
                r[ix['parent_unit_id']] = ''
                total['parent_sentinel'] = total.get('parent_sentinel', 0) + 1
                changed = True
            new, cnt = clean_entries(r[ix['command_relationships']])
            if new != r[ix['command_relationships']]:
                r[ix['command_relationships']] = new
                changed = True
            for k, v in cnt.items():
                total[k] = total.get(k, 0) + v
        if changed and not dry:
            with open(p, 'wb') as f:
                f.write(common.csv_bytes(h, rows))
    # 2. units
    h, rows = common.read_rows(common.UNITS_CSV)
    if 'parent_only' in h:
        i = h.index('parent_only')
        total['units_parent_only_dropped'] = len(rows)
        h = h[:i] + h[i + 1:]
        rows = [r[:i] + r[i + 1:] for r in rows]
        if not dry:
            with open(common.UNITS_CSV, 'wb') as f:
                f.write(common.csv_bytes(h, rows))
    # 3. nationalities
    path = os.path.join(common.ROOT, 'data', 'nationalities.csv')
    if not os.path.isfile(path):
        total['nationalities_rows'] = len(NATIONALITIES)
        if not dry:
            with open(path, 'wb') as f:
                f.write(common.csv_bytes(NAT_HEADER, NATIONALITIES))
    # 4. operations scope
    path = os.path.join(common.ROOT, 'data', 'operations.csv')
    h, rows = common.read_rows(path)
    j = h.index('nationality_scope')
    for r in rows:
        if r[j] == 'German':
            r[j] = 'Germany'
            total['scope_german'] = total.get('scope_german', 0) + 1
    if total.get('scope_german') and not dry:
        with open(path, 'wb') as f:
            f.write(common.csv_bytes(h, rows))
    print(('would change: ' if dry else 'changed: ') + json.dumps(total, sort_keys=True))
    return 0


if __name__ == '__main__':
    sys.exit(main())
