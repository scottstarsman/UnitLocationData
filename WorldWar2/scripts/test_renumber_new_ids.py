#!/usr/bin/env python3
"""Simulate two branches taking the same new ids, then check that
scripts/renumber_new_ids.py remaps only the unpublished collisions.

  python scripts/test_renumber_new_ids.py

Creates a temporary git repo with a minimal dataset (not the real tree).
Standard library only. Exit 0 on success.
"""
import csv
import io
import os
import shutil
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common  # noqa: E402
import renumber_new_ids as rn  # noqa: E402


def write_csv(path, header, rows):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'wb') as f:
        f.write(common.csv_bytes(header, rows))


def git(root, *args, check=True):
    p = subprocess.run(['git'] + list(args), cwd=root, capture_output=True, text=True)
    if check and p.returncode:
        raise RuntimeError('git %s failed: %s%s' % (' '.join(args), p.stdout, p.stderr))
    return p


def init_repo():
    tmp = tempfile.mkdtemp(prefix='renumber-ids-')
    git(tmp, 'init', '-b', 'main')
    git(tmp, 'config', 'user.email', 'test@example.com')
    git(tmp, 'config', 'user.name', 'Test')
    return tmp


CLAIMS_H = ['claim_id', 'conflict_group_id', 'unit_id', 'date', 'event_type', 'reference_ids', 'notes']
CR_H = ['relation_id', 'subject_unit_id', 'higher_unit_id', 'relationship', 'valid_from']
CRC_H = ['relation_id', 'claim_id']
PL_H = ['place_id', 'name', 'coord_reference_id']
REF_H = ['reference_id', 'url']
UNITS_H = ['unit_id', 'unit_name']


def seed_main(root):
    write_csv(os.path.join(root, 'data', 'units.csv'), UNITS_H, [
        ['US-INF-001D', '1st Infantry Division'],
        ['US-INF-002D', '2nd Infantry Division'],
        ['US-CORPS-007', 'VII Corps'],
    ])
    write_csv(os.path.join(root, 'data', 'claims', 'us', 'US-INF-001D.csv'), CLAIMS_H, [
        ['C0001', '', 'US-INF-001D', '1944-06-06', 'located_at', 'R001', 'on main'],
    ])
    write_csv(os.path.join(root, 'data', 'claims', 'us', 'US-INF-002D.csv'), CLAIMS_H, [
        ['C0002', '', 'US-INF-002D', '1944-06-07', 'located_at', 'R001', 'on main'],
    ])
    write_csv(os.path.join(root, 'data', 'command_relations.csv'), CR_H, [
        ['CR0001', 'US-INF-001D', 'US-CORPS-007', 'assigned', '1944-06-06'],
    ])
    write_csv(os.path.join(root, 'data', 'command_relation_claims.csv'), CRC_H, [
        ['CR0001', 'C0001'],
    ])
    write_csv(os.path.join(root, 'data', 'places.csv'), PL_H, [
        ['PL0001', 'Omaha Beach', 'R001'],
    ])
    write_csv(os.path.join(root, 'data', 'references_meta.csv'), REF_H, [
        ['R001', 'https://example.com/main'],
    ])
    os.makedirs(os.path.join(root, 'docs'), exist_ok=True)
    os.makedirs(os.path.join(root, 'scripts'), exist_ok=True)
    with open(os.path.join(root, 'docs', 'changelog.md'), 'w', encoding='utf-8') as f:
        f.write('# Changelog\n\n## Base\n\nClaim C0001 is on main.\n')
    with open(os.path.join(root, 'docs', 'roadmap.md'), 'w', encoding='utf-8') as f:
        f.write('# Roadmap\n\n1. **First item** already on main.\n\n2. **Second item** already on main.\n')
    with open(os.path.join(root, 'scripts', 'semantic_tests.py'), 'w', encoding='utf-8') as f:
        f.write('def scenario_1_first():\n    s = \'scenario 1, first\'\n    return s\n')
    git(root, 'add', '.')
    git(root, 'commit', '-m', 'main seed')


def add_branch_a(root):
    """Merged first: takes the next free ids C0003, G001, CR0002, PL0002, R002, scenario 2, roadmap 3."""
    h, rows = common.read_dicts(os.path.join(root, 'data', 'claims', 'us', 'US-INF-001D.csv'))
    rows.append({
        'claim_id': 'C0003', 'conflict_group_id': 'G001', 'unit_id': 'US-INF-001D',
        'date': '1944-06-08', 'event_type': 'located_at', 'reference_ids': 'R002',
        'notes': 'A claims C0003 in G001',
    })
    write_csv(os.path.join(root, 'data', 'claims', 'us', 'US-INF-001D.csv'), h,
              [[r[c] for c in h] for r in rows])
    h, rows = common.read_dicts(os.path.join(root, 'data', 'command_relations.csv'))
    rows.append({
        'relation_id': 'CR0002', 'subject_unit_id': 'US-INF-001D',
        'higher_unit_id': 'US-CORPS-007', 'relationship': 'assigned', 'valid_from': '1944-06-08',
    })
    write_csv(os.path.join(root, 'data', 'command_relations.csv'), h,
              [[r[c] for c in h] for r in rows])
    h, rows = common.read_dicts(os.path.join(root, 'data', 'command_relation_claims.csv'))
    rows.append({'relation_id': 'CR0002', 'claim_id': 'C0003'})
    write_csv(os.path.join(root, 'data', 'command_relation_claims.csv'), h,
              [[r[c] for c in h] for r in rows])
    h, rows = common.read_dicts(os.path.join(root, 'data', 'places.csv'))
    rows.append({'place_id': 'PL0002', 'name': "A's place", 'coord_reference_id': 'R002'})
    write_csv(os.path.join(root, 'data', 'places.csv'), h, [[r[c] for c in h] for r in rows])
    h, rows = common.read_dicts(os.path.join(root, 'data', 'references_meta.csv'))
    rows.append({'reference_id': 'R002', 'url': 'https://example.com/a'})
    write_csv(os.path.join(root, 'data', 'references_meta.csv'), h, [[r[c] for c in h] for r in rows])
    with open(os.path.join(root, 'docs', 'changelog.md'), 'a', encoding='utf-8') as f:
        f.write('\n## Branch A\n\nAdded C0003, G001, CR0002, PL0002, R002.\n')
    with open(os.path.join(root, 'docs', 'roadmap.md'), 'a', encoding='utf-8') as f:
        f.write('\n3. **A item** (see also roadmap 3).\n')
    with open(os.path.join(root, 'scripts', 'semantic_tests.py'), 'a', encoding='utf-8') as f:
        f.write("\ndef scenario_2_a():\n    s = 'scenario 2, branch A'\n    return s\n")
    git(root, 'add', '.')
    git(root, 'commit', '-m', 'branch A')


def add_branch_b_collisions(root):
    """Second branch, already rebased in the working tree: same new ids, different rows."""
    # C0003 on a different unit, same token as A's published claim
    h, rows = common.read_dicts(os.path.join(root, 'data', 'claims', 'us', 'US-INF-002D.csv'))
    rows.append({
        'claim_id': 'C0003', 'conflict_group_id': 'G001', 'unit_id': 'US-INF-002D',
        'date': '1944-06-09', 'event_type': 'located_at', 'reference_ids': 'R002',
        'notes': 'B claims C0003 in G001; see also CR0002',
    })
    write_csv(os.path.join(root, 'data', 'claims', 'us', 'US-INF-002D.csv'), h,
              [[r[c] for c in h] for r in rows])
    h, rows = common.read_dicts(os.path.join(root, 'data', 'command_relations.csv'))
    rows.append({
        'relation_id': 'CR0002', 'subject_unit_id': 'US-INF-002D',
        'higher_unit_id': 'US-CORPS-007', 'relationship': 'assigned', 'valid_from': '1944-06-09',
    })
    write_csv(os.path.join(root, 'data', 'command_relations.csv'), h,
              [[r[c] for c in h] for r in rows])
    h, rows = common.read_dicts(os.path.join(root, 'data', 'command_relation_claims.csv'))
    rows.append({'relation_id': 'CR0002', 'claim_id': 'C0003'})
    write_csv(os.path.join(root, 'data', 'command_relation_claims.csv'), h,
              [[r[c] for c in h] for r in rows])
    h, rows = common.read_dicts(os.path.join(root, 'data', 'places.csv'))
    rows.append({'place_id': 'PL0002', 'name': "B's place", 'coord_reference_id': 'R002'})
    write_csv(os.path.join(root, 'data', 'places.csv'), h, [[r[c] for c in h] for r in rows])
    h, rows = common.read_dicts(os.path.join(root, 'data', 'references_meta.csv'))
    rows.append({'reference_id': 'R002', 'url': 'https://example.com/b'})
    write_csv(os.path.join(root, 'data', 'references_meta.csv'), h, [[r[c] for c in h] for r in rows])
    with open(os.path.join(root, 'docs', 'changelog.md'), 'a', encoding='utf-8') as f:
        f.write('\n## Branch B\n\nAdded C0003, G001, CR0002, PL0002, R002.\n')
    with open(os.path.join(root, 'docs', 'roadmap.md'), 'a', encoding='utf-8') as f:
        f.write('\n3. **B item** (see also roadmap 3).\n')
    with open(os.path.join(root, 'scripts', 'semantic_tests.py'), 'a', encoding='utf-8') as f:
        f.write("\ndef scenario_2_b():\n    s = 'scenario 2, branch B'\n    return s\n")


def ids_in(path, col):
    if not os.path.isfile(path):
        return []
    return [(r.get(col) or '') for r in common.read_dicts(path)[1]]


def test_collision_and_apply():
    root = init_repo()
    try:
        seed_main(root)
        add_branch_a(root)
        main_sha = git(root, 'rev-parse', 'HEAD').stdout.strip()
        add_branch_b_collisions(root)

        # Dry-run must not write
        before = open(os.path.join(root, 'data', 'claims', 'us', 'US-INF-002D.csv'), 'rb').read()
        mappings, problems = rn.plan(root, main_sha)
        assert not problems, problems
        kinds = {m['kind']: m for m in mappings}
        by_kind = {}
        for m in mappings:
            by_kind.setdefault(m['kind'], []).append(m)
        assert 'claim' in by_kind, mappings
        assert by_kind['claim'][0]['old'] == 'C0003' and by_kind['claim'][0]['new'] == 'C0004', by_kind['claim']
        assert by_kind['command relation'][0]['old'] == 'CR0002' and by_kind['command relation'][0]['new'] == 'CR0003', by_kind['command relation']
        assert by_kind['place'][0]['old'] == 'PL0002' and by_kind['place'][0]['new'] == 'PL0003', by_kind['place']
        assert by_kind['reference'][0]['old'] == 'R002' and by_kind['reference'][0]['new'] == 'R003', by_kind['reference']
        assert by_kind['conflict group'][0]['old'] == 'G001' and by_kind['conflict group'][0]['new'] == 'G002', by_kind['conflict group']
        assert by_kind['scenario'][0]['old'] == 'scenario 2' and by_kind['scenario'][0]['new'] == 'scenario 3', by_kind['scenario']
        assert by_kind['roadmap'][0]['old'] == 'roadmap 3' and by_kind['roadmap'][0]['new'] == 'roadmap 4', by_kind['roadmap']
        rc = rn.main(['--root', root, '--base', main_sha])
        assert rc == 0
        after = open(os.path.join(root, 'data', 'claims', 'us', 'US-INF-002D.csv'), 'rb').read()
        assert after == before, 'dry-run wrote files'

        # --apply remaps B's rows and leaves A's published ids alone
        rc = rn.main(['--root', root, '--base', main_sha, '--apply'])
        assert rc == 0

        h, rows = common.read_dicts(os.path.join(root, 'data', 'claims', 'us', 'US-INF-001D.csv'))
        by_id = {r['claim_id']: r for r in rows}
        assert 'C0001' in by_id and 'C0003' in by_id and 'C0004' not in by_id, by_id.keys()
        assert by_id['C0003']['conflict_group_id'] == 'G001'
        assert by_id['C0003']['notes'] == 'A claims C0003 in G001'

        h, rows = common.read_dicts(os.path.join(root, 'data', 'claims', 'us', 'US-INF-002D.csv'))
        by_id = {r['claim_id']: r for r in rows}
        assert 'C0002' in by_id and 'C0004' in by_id and 'C0003' not in by_id, by_id.keys()
        b = by_id['C0004']
        assert b['conflict_group_id'] == 'G002', b
        assert b['reference_ids'] == 'R003', b
        assert 'C0004' in b['notes'] and 'G001' not in b['notes'] and 'CR0003' in b['notes'], b['notes']

        rels = {r['relation_id']: r for r in common.read_dicts(os.path.join(root, 'data', 'command_relations.csv'))[1]}
        assert 'CR0001' in rels and 'CR0002' in rels and 'CR0003' in rels, rels.keys()
        assert rels['CR0002']['subject_unit_id'] == 'US-INF-001D'
        assert rels['CR0003']['subject_unit_id'] == 'US-INF-002D'

        links = [(r['relation_id'], r['claim_id']) for r in common.read_dicts(os.path.join(root, 'data', 'command_relation_claims.csv'))[1]]
        assert ('CR0001', 'C0001') in links
        assert ('CR0002', 'C0003') in links  # A's published link
        assert ('CR0003', 'C0004') in links  # B's remapped link
        assert ('CR0002', 'C0003') in links
        assert ('CR0002', 'C0004') not in links

        places = {r['place_id']: r for r in common.read_dicts(os.path.join(root, 'data', 'places.csv'))[1]}
        assert places['PL0002']['name'] == "A's place" and places['PL0002']['coord_reference_id'] == 'R002'
        assert places['PL0003']['name'] == "B's place" and places['PL0003']['coord_reference_id'] == 'R003'

        refs = {r['reference_id']: r for r in common.read_dicts(os.path.join(root, 'data', 'references_meta.csv'))[1]}
        assert refs['R002']['url'] == 'https://example.com/a'
        assert refs['R003']['url'] == 'https://example.com/b'

        changelog = open(os.path.join(root, 'docs', 'changelog.md'), encoding='utf-8').read()
        assert 'Added C0003, G001, CR0002, PL0002, R002.' in changelog  # A's published entry
        assert 'Added C0004, G002, CR0003, PL0003, R003.' in changelog  # B's added lines remapped
        assert changelog.count('Branch A') == 1 and changelog.count('Branch B') == 1

        roadmap = open(os.path.join(root, 'docs', 'roadmap.md'), encoding='utf-8').read()
        assert '3. **A item** (see also roadmap 3).' in roadmap
        assert '4. **B item** (see also roadmap 4).' in roadmap

        scen = open(os.path.join(root, 'scripts', 'semantic_tests.py'), encoding='utf-8').read()
        assert 'def scenario_2_a():' in scen and "scenario 2, branch A" in scen
        assert 'def scenario_3_b():' in scen and "scenario 3, branch B" in scen
        assert 'def scenario_2_b():' not in scen

        # Second dry-run against the same base: still reports collisions if we didn't... we did apply, so
        # a new plan should find nothing (ids no longer collide).
        mappings2, problems2 = rn.plan(root, main_sha)
        assert not problems2, problems2
        assert mappings2 == [], mappings2
    finally:
        shutil.rmtree(root)


def test_keep_group():
    root = init_repo()
    try:
        seed_main(root)
        add_branch_a(root)
        main_sha = git(root, 'rev-parse', 'HEAD').stdout.strip()
        # B only adds a new claim C0004 that joins A's G001 on purpose
        h, rows = common.read_dicts(os.path.join(root, 'data', 'claims', 'us', 'US-INF-002D.csv'))
        rows.append({
            'claim_id': 'C0004', 'conflict_group_id': 'G001', 'unit_id': 'US-INF-002D',
            'date': '1944-06-09', 'event_type': 'located_at', 'reference_ids': 'R001',
            'notes': 'joins G001 on purpose',
        })
        write_csv(os.path.join(root, 'data', 'claims', 'us', 'US-INF-002D.csv'), h,
                  [[r[c] for c in h] for r in rows])
        mappings, problems = rn.plan(root, main_sha)
        assert not problems
        assert any(m['kind'] == 'conflict group' and m['old'] == 'G001' for m in mappings), mappings
        mappings_k, problems_k = rn.plan(root, main_sha, keep_groups={'G001'})
        assert not problems_k
        assert not any(m['kind'] == 'conflict group' for m in mappings_k), mappings_k
    finally:
        shutil.rmtree(root)


def test_no_collision():
    root = init_repo()
    try:
        seed_main(root)
        sha = git(root, 'rev-parse', 'HEAD').stdout.strip()
        mappings, problems = rn.plan(root, sha)
        assert mappings == [] and problems == []
    finally:
        shutil.rmtree(root)


def main():
    tests = [test_collision_and_apply, test_keep_group, test_no_collision]
    failed = 0
    for fn in tests:
        try:
            fn()
            print('OK', fn.__name__)
        except Exception as e:
            failed += 1
            print('FAIL', fn.__name__ + ':', type(e).__name__ + ':', e)
            import traceback
            traceback.print_exc()
    if failed:
        print('%d test(s) failed' % failed)
        return 1
    print('ALL RENUMBER TESTS PASSED (%d)' % len(tests))
    return 0


if __name__ == '__main__':
    sys.exit(main())
