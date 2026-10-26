#!/usr/bin/env python3
"""Pattern audit of command relationships and coordinate provenance (read-only; standard library only).

Prints, for all claims and for the rows added in US Batch 1 (claim_id > C0212), how many rows show each pattern a reviewer
flagged: coordinates from a different date, town-centroid headquarters at corps level or above, 'organic' used for a division,
corps or army under a higher headquarters, exact front-line points at corps or army level, landing rows whose coordinate is
a headquarters or town centroid, named higher headquarters without a unit id, and conflict groups whose rows have different
event types. Exit code is always 0: it lists review prompts, it does not fail the build.

Usage: python scripts/audit_command_location.py [--ids]    (--ids lists the claim ids for each pattern)
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common  # noqa: E402

HI = ('corps', 'army', 'army_group')


def main():
    _h, rows = common.load_all_claims()
    _uh, urows = common.read_rows(common.UNITS_CSV)
    units = {r[0]: dict(zip(_uh, r)) for r in urows}
    pats = {}

    def hit(name, r):
        lst = pats.setdefault(name, [])
        if r['claim_id'] not in lst:
            lst.append(r['claim_id'])

    for r in rows:
        if r['location_date'] and r['location_date'] != r['date']:
            hit('coordinate taken from a different date (location_date != date)', r)
        if not r['location_basis']:
            hit('location_basis blank (not yet reviewed)', r)
        if r['location_represents'] == 'headquarters' and r['location_basis'] == 'town_centroid':
            hit('headquarters coordinate is a town centroid', r)
            if r['echelon'] in HI:
                hit('corps/army/army-group headquarters is a town centroid', r)
        if r['echelon'] in HI and r['location_represents'] == 'front_line_point' and r['precision_km'] in ('1', '3', '5'):
            hit('corps/army sector recorded as an exact front_line_point', r)
        if r['event_type'] == 'landing' and (r['location_represents'] == 'headquarters' or r['location_basis'] in (
                'town_centroid', 'nearest_later_command_post', 'nearest_earlier_command_post')):
            hit('landing row whose coordinate is a headquarters or town centroid', r)
        if r['location_basis'] == 'inferred':
            hit('coordinate inferred or unresolved', r)
        if r['command_relationships'] != '':
            for e in json.loads(r['command_relationships']):
                u = units.get(e.get('unit_id') or '')
                if e['relationship'] == 'organic' and u and r['echelon'] in ('division', 'corps', 'army') and u['echelon'] in ('corps', 'army', 'army_group', 'other'):
                    hit("'organic' used for a formation under a higher headquarters", r)
                if e.get('unit_id') is None and e['relationship'] != 'unknown':
                    hit('named higher headquarters without a unit id', r)
                if e['relationship'] == 'unspecified_subordination':
                    hit('relationship unspecified_subordination (source does not say assigned or attached)', r)
    for r in rows:
        if r['location_represents'] == 'objective' and r['event_type'] == 'attack' and r['location_basis'] == 'documented_on_date' \
                and 'Objective check' not in r['notes']:
            hit('attack row whose point is an objective marked documented_on_date (confirm the unit or event was there on the date)', r)
        if r['event_type'] in ('command_change', 'activation') and r['confidence'] and float(r['confidence']) <= 0.3 \
                and 'Event support:' not in r['notes'] and int(r['claim_id'][1:]) >= 483:
            hit('low-confidence command row without an Event support sentence (Batch 2 on)', r)
    by_unit = {}
    for r in rows:
        by_unit.setdefault(r['unit_id'], []).append(r)
    for rs in by_unit.values():
        rs.sort(key=lambda r: (r['date'], r['claim_id']))
        for i, r in enumerate(rs):
            later = [x for x in rs[i + 1:] if x['date'] > r['date']]
            if not later or r['command_relationships'] == '':
                continue
            nxt = later[0]
            nk = {(f.get('unit_id'), f.get('relationship')) for f in json.loads(nxt['command_relationships'])} \
                if nxt['command_relationships'] != '' else set()
            for e in json.loads(r['command_relationships']):
                if e['relationship'] in common.relationship_group('active') and 'effective_to' not in e and (e.get('unit_id'), e['relationship']) not in nk:
                    hit('attached/operational_control entry with no effective_to, not listed by the next claim (derived end)', r)
    groups = {}
    for r in rows:
        if r['conflict_group_id']:
            groups.setdefault(r['conflict_group_id'], []).append(r)
    for g, rs in groups.items():
        if len({x['event_type'] for x in rs}) > 1:
            for x in rs:
                hit('conflict group with different event types (needs "Event definition:" notes)', x)
    ids = '--ids' in sys.argv
    new = lambda cid: int(cid[1:]) > 212  # noqa: E731
    print('%-90s %5s %7s' % ('pattern', 'all', 'batch1'))
    for name in sorted(pats):
        a = pats[name]
        print('%-90s %5d %7d' % (name, len(a), len([c for c in a if new(c)])))
        if ids:
            print('    ' + ' '.join(a))
    print('\n%d claims; batch 1 = %d rows (claim_id > C0212)' % (len(rows), len([r for r in rows if new(r['claim_id'])])))
    return 0


if __name__ == '__main__':
    sys.exit(main())
