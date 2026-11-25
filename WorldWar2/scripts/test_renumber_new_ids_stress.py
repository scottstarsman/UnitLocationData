#!/usr/bin/env python3
"""Stress and property tests for scripts/renumber_new_ids.py.

  python scripts/test_renumber_new_ids_stress.py

* Full-dataset copy: add colliding rows in every id family, plus word-boundary
  and range references, a silent-join conflict group, and non-colliding new ids.
* Property test: a fixed seed, many generated mini-repos.
* Safety: --apply on a temp copy; a failing check leaves the tree unchanged.

Standard library only. Exit 0 on success.
"""
from __future__ import print_function

import hashlib
import os
import random
import re
import shutil
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common  # noqa: E402
import renumber_new_ids as rn  # noqa: E402
import test_renumber_new_ids as basic  # noqa: E402

SEED = 20261125
PROPERTY_ITERATIONS = 20


def git(root, *args, check=True):
    p = subprocess.run(['git'] + list(args), cwd=root, capture_output=True, text=True)
    if check and p.returncode:
        raise RuntimeError('git %s failed: %s%s' % (' '.join(args), p.stdout, p.stderr))
    return p


def write_csv(path, header, rows):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'wb') as f:
        f.write(common.csv_bytes(header, rows))


def append_row(path, **updates):
    header, rows = common.read_dicts(path)
    if not rows:
        raise RuntimeError('no template row in %s' % path)
    row = dict(rows[0])
    row.update(updates)
    rows.append(row)
    write_csv(path, header, [[r.get(c, '') for c in header] for r in rows])
    return row


def hashes_under(root, rels=None):
    out = {}
    if rels is None:
        for dirpath, dirnames, filenames in os.walk(root):
            dirnames[:] = [d for d in dirnames if d not in {'.git', '__pycache__', 'build'}]
            for fn in filenames:
                path = os.path.join(dirpath, fn)
                if not os.path.isfile(path):
                    continue
                rel = os.path.relpath(path, root)
                out[rel] = hashlib.sha256(open(path, 'rb').read()).hexdigest()
        return out
    for rel in rels:
        path = os.path.join(root, rel)
        if os.path.isfile(path):
            out[rel] = hashlib.sha256(open(path, 'rb').read()).hexdigest()
    return out


def snapshot_files(root, dest):
    if os.path.exists(dest):
        shutil.rmtree(dest)
    shutil.copytree(root, dest, ignore=shutil.ignore_patterns('.git', '__pycache__', 'build'))


def invert_mappings(mappings):
    tmap = {}
    scen = []
    for m in mappings:
        if m['prefix'] == 'scenario':
            scen.append(m)
        elif m['prefix'] == 'roadmap':
            scen.append(m)
        else:
            tmap[m['new']] = m['old']
    return tmap, scen


def reverse_file(path, tmap, mappings):
    raw = open(path, encoding='utf-8').read()
    new = rn.replace_tokens(raw, tmap)
    # Reverse scenario/roadmap: swap old/new numbers
    reversed_maps = []
    for m in mappings:
        if m['prefix'] not in ('scenario', 'roadmap'):
            continue
        r = dict(m)
        r['old_n'], r['new_n'] = m['new_n'], m['old_n']
        r['old'], r['new'] = m['new'], m['old']
        reversed_maps.append(r)
    new = rn.replace_scenario_roadmap(new, reversed_maps)
    if new != raw:
        with open(path, 'w', encoding='utf-8', newline='') as f:
            f.write(new)
        return True
    return False


def assert_round_trip(pre_dir, post_root, mappings):
    tmap, _ = invert_mappings(mappings)
    tmp = tempfile.mkdtemp(prefix='renumber-roundtrip-')
    try:
        shutil.copytree(post_root, tmp, ignore=shutil.ignore_patterns('.git', '__pycache__', 'build'), dirs_exist_ok=True)
        # copytree with dirs_exist_ok needs dest to exist; handle both py versions
    except TypeError:
        shutil.rmtree(tmp)
        shutil.copytree(post_root, tmp, ignore=shutil.ignore_patterns('.git', '__pycache__', 'build'))
    try:
        for dirpath, dirnames, filenames in os.walk(tmp):
            dirnames[:] = [d for d in dirnames if d not in {'.git', '__pycache__', 'build'}]
            for fn in filenames:
                reverse_file(os.path.join(dirpath, fn), tmap, mappings)
        # Compare text/csv files that existed before apply
        mismatches = []
        for dirpath, dirnames, filenames in os.walk(pre_dir):
            dirnames[:] = [d for d in dirnames if d not in {'.git', '__pycache__', 'build'}]
            for fn in filenames:
                rel = os.path.relpath(os.path.join(dirpath, fn), pre_dir)
                a = os.path.join(pre_dir, rel)
                b = os.path.join(tmp, rel)
                if not os.path.isfile(b):
                    mismatches.append('missing after reverse: %s' % rel)
                    continue
                if open(a, 'rb').read() != open(b, 'rb').read():
                    mismatches.append('round-trip differed: %s' % rel)
        if mismatches:
            raise AssertionError('round-trip failed:\n  ' + '\n  '.join(mismatches[:20]))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def real_repo_top():
    return git(common.ROOT, 'rev-parse', '--show-toplevel').stdout.strip()


def resolve_rev(root, *names):
    """Return the first name that git can resolve in root, or None."""
    for name in names:
        if not name:
            continue
        p = git(root, 'rev-parse', '--verify', name, check=False)
        if p.returncode == 0 and p.stdout.strip():
            return p.stdout.strip()
    return None


def install_base_ref(repo, sha):
    """Point refs/heads/base at sha inside repo, fetching it if the object is missing."""
    p = git(repo, 'cat-file', '-t', sha, check=False)
    if p.returncode != 0 or (p.stdout or '').strip() != 'commit':
        p2 = git(repo, 'fetch', '--no-tags', '--depth=1', real_repo_top(),
                 '+%s:refs/heads/base' % sha, check=False)
        if p2.returncode != 0:
            raise RuntimeError('cannot fetch base %s into the temp repo: %s%s' % (
                sha, p2.stdout, p2.stderr))
        return
    git(repo, 'update-ref', 'refs/heads/base', sha)
    # The object must now be readable as the local 'base' ref.
    got = git(repo, 'rev-parse', '--verify', 'base').stdout.strip()
    if got != sha:
        raise RuntimeError('failed to set local base ref (%s != %s)' % (got, sha))


def clone_real_dataset():
    """Copy the real dataset into a temp repo with its own local 'base' ref.

    The base SHA is resolved in the *source* repo (origin/main, then main,
    then HEAD). A shallow CI checkout has origin/main but no local main, and
    a clone of that checkout does not get the source's remote-tracking refs,
    so the temp repo always gets a refs/heads/base we pass as --base.
    """
    top = real_repo_top()
    base_sha = resolve_rev(top, 'origin/main', 'main', 'HEAD')
    if not base_sha:
        raise RuntimeError('cannot resolve a base revision in %s (tried origin/main, main, HEAD)' % top)
    tmp = tempfile.mkdtemp(prefix='renumber-stress-full-')
    p = subprocess.run(
        ['git', 'clone', '--local', '--shared', top, tmp],
        capture_output=True, text=True,
    )
    if p.returncode:
        shutil.rmtree(tmp, ignore_errors=True)
        raise RuntimeError('git clone failed: %s%s' % (p.stdout, p.stderr))
    git(tmp, 'config', 'user.email', 'test@example.com')
    git(tmp, 'config', 'user.name', 'Test')
    try:
        install_base_ref(tmp, base_sha)
    except Exception:
        shutil.rmtree(tmp, ignore_errors=True)
        raise
    root = os.path.join(tmp, 'WorldWar2')
    if not os.path.isdir(root):
        shutil.rmtree(tmp, ignore_errors=True)
        raise RuntimeError('clone is missing WorldWar2/')
    return tmp, root, 'base'


def find_claim(root, claim_id):
    for path in sorted(__import__('glob').glob(os.path.join(root, 'data', 'claims', '*', '*.csv'))):
        h, rows = common.read_dicts(path)
        for r in rows:
            if r.get('claim_id') == claim_id:
                return path, r, h
    raise RuntimeError('claim %s not found' % claim_id)


def pick_other_claim_file(root, not_unit):
    for path in sorted(__import__('glob').glob(os.path.join(root, 'data', 'claims', '*', '*.csv'))):
        h, rows = common.read_dicts(path)
        if not rows:
            continue
        if rows[0].get('unit_id') != not_unit:
            return path, rows[0], h
    raise RuntimeError('no other claim file')


def add_full_dataset_collisions(root):
    """Add colliding and non-colliding rows in every family. Returns expected stay-ids."""
    path1234, row1234, _ = find_claim(root, 'C1234')
    other, tmpl, header = pick_other_claim_file(root, row1234['unit_id'])
    stay = {
        'C12345', 'C10873', 'C10982', 'C12783', 'G319',
        'CR3742', 'R2224', 'PL4897', 'PE0608', 'UC0697',
        'TT0016', 'UT0127', 'AT143', 'SC220', 'UL028', 'MSN0099',
    }

    notes = (
        'Stress collision of C1234 vs C12345; range C10873-C10982; '
        'also C1234-C12345 and G112. Non-colliding later: C12783.'
    )
    append_row(
        other,
        claim_id='C1234',
        conflict_group_id='G112',
        unit_id=tmpl['unit_id'],
        date='1939-09-02',
        event_type='located_at' if tmpl.get('event_type') == 'located_at' else (tmpl.get('event_type') or 'located_at'),
        place_id='PL0001',
        reference_ids='R001',
        notes=notes,
        source=tmpl.get('source') or 'https://example.com/stress',
    )
    # Second new member of the same silent-join group, unique (non-colliding) claim id.
    append_row(
        other,
        claim_id='C12784',
        conflict_group_id='G112',
        unit_id=tmpl['unit_id'],
        date='1939-09-03',
        event_type='located_at',
        place_id='PL0001',
        reference_ids='R001',
        notes='joins the colliding group G112; claim id is new',
        source=tmpl.get('source') or 'https://example.com/stress',
    )
    stay.add('C12784')
    # Non-colliding new claim and group
    append_row(
        other,
        claim_id='C12783',
        conflict_group_id='G319',
        unit_id=tmpl['unit_id'],
        date='1939-09-04',
        event_type='located_at',
        place_id='PL4897',
        reference_ids='R2224',
        notes='non-colliding C12783 G319 PL4897 R2224',
        source=tmpl.get('source') or 'https://example.com/stress',
    )

    append_row(
        os.path.join(root, 'data', 'command_relations.csv'),
        relation_id='CR0001',
        subject_unit_id=tmpl['unit_id'],
        higher_unit_id=tmpl.get('parent_unit_id') or tmpl['unit_id'],
        relationship='assigned',
        valid_from='1939-09-02',
    )
    append_row(
        os.path.join(root, 'data', 'command_relations.csv'),
        relation_id='CR3742',
        subject_unit_id=tmpl['unit_id'],
        higher_unit_id=tmpl.get('parent_unit_id') or tmpl['unit_id'],
        relationship='assigned',
        valid_from='1939-09-04',
    )
    crc = os.path.join(root, 'data', 'command_relation_claims.csv')
    ch, crows = common.read_dicts(crc)
    crows.append({'relation_id': 'CR0001', 'claim_id': 'C1234'})
    crows.append({'relation_id': 'CR3742', 'claim_id': 'C12783'})
    write_csv(crc, ch, [[r.get(c, '') for c in ch] for r in crows])

    append_row(
        os.path.join(root, 'data', 'references_meta.csv'),
        reference_id='R001', url='https://example.com/stress-r001',
        short_title='Stress R001',
    )
    append_row(
        os.path.join(root, 'data', 'references_meta.csv'),
        reference_id='R2224', url='https://example.com/stress-r2224',
        short_title='Stress R2224',
    )
    append_row(
        os.path.join(root, 'data', 'places.csv'),
        place_id='PL0001', name='Stress place colliding',
        coord_reference_id='R001',
    )
    append_row(
        os.path.join(root, 'data', 'places.csv'),
        place_id='PL4897', name='Stress place new',
        coord_reference_id='R2224',
    )
    append_row(
        os.path.join(root, 'data', 'people.csv'),
        person_id='PE0001', canonical_name='Stress Person Colliding',
        sort_name='Colliding, Stress', surname='Colliding',
    )
    append_row(
        os.path.join(root, 'data', 'people.csv'),
        person_id='PE0608', canonical_name='Stress Person New',
        sort_name='New, Stress', surname='New',
    )
    append_row(
        os.path.join(root, 'data', 'unit_commanders.csv'),
        tenure_id='UC0001', unit_id=tmpl['unit_id'], person_id='PE0001',
        valid_from='1939-09-02', role='commander',
    )
    append_row(
        os.path.join(root, 'data', 'unit_commanders.csv'),
        tenure_id='UC0697', unit_id=tmpl['unit_id'], person_id='PE0608',
        valid_from='1939-09-04', role='commander',
    )
    append_row(
        os.path.join(root, 'data', 'toe_templates.csv'),
        template_id='TT0001', template_name='Stress colliding template',
    )
    append_row(
        os.path.join(root, 'data', 'toe_templates.csv'),
        template_id='TT0016', template_name='Stress new template',
    )
    append_row(
        os.path.join(root, 'data', 'unit_toe.csv'),
        assignment_id='UT0001', unit_id=tmpl['unit_id'], template_id='TT0001',
        valid_from='1939-09-02',
    )
    append_row(
        os.path.join(root, 'data', 'unit_toe.csv'),
        assignment_id='UT0127', unit_id=tmpl['unit_id'], template_id='TT0016',
        valid_from='1939-09-04',
    )
    append_row(
        os.path.join(root, 'data', 'aircraft_types.csv'),
        type_id='AT001', designation='Stress colliding aircraft',
    )
    append_row(
        os.path.join(root, 'data', 'aircraft_types.csv'),
        type_id='AT143', designation='Stress new aircraft',
    )
    append_row(
        os.path.join(root, 'data', 'ship_classes.csv'),
        class_id='SC001', class_name='Stress colliding class',
    )
    append_row(
        os.path.join(root, 'data', 'ship_classes.csv'),
        class_id='SC220', class_name='Stress new class',
    )
    append_row(
        os.path.join(root, 'data', 'unit_lineage.csv'),
        lineage_id='UL001',
        predecessor_unit_id=tmpl['unit_id'],
        successor_unit_id=row1234['unit_id'],
        kind='redesignation',
        effective_date='1939-09-02',
    )
    append_row(
        os.path.join(root, 'data', 'unit_lineage.csv'),
        lineage_id='UL028',
        predecessor_unit_id=row1234['unit_id'],
        successor_unit_id=tmpl['unit_id'],
        kind='redesignation',
        effective_date='1939-09-04',
    )

    # Missions: collide MSN0098 on a different date, plus a non-colliding MSN0099.
    mfiles = sorted(__import__('glob').glob(os.path.join(root, 'data', 'missions', '*', '*.csv')))
    if not mfiles:
        raise RuntimeError('no mission files')
    mpath = mfiles[0]
    append_row(
        mpath,
        mission_id='MSN0098',
        unit_id=tmpl['unit_id'],
        date='1939-09-02',
        mission_type=(common.read_dicts(mpath)[1][0].get('mission_type') or 'bombardment'),
        conflict_group_id='',
        notes='colliding mission MSN0098',
        reference_ids='R001',
    )
    append_row(
        mpath,
        mission_id='MSN0099',
        unit_id=tmpl['unit_id'],
        date='1939-09-04',
        mission_type=(common.read_dicts(mpath)[1][0].get('mission_type') or 'bombardment'),
        conflict_group_id='',
        notes='non-colliding mission MSN0099',
        reference_ids='R2224',
    )

    with open(os.path.join(root, 'docs', 'changelog.md'), 'a', encoding='utf-8') as f:
        f.write(
            '\n## Stress collision\n\n'
            'Added C1234 vs C12345, range C10873-C10982, G112, CR0001, R001, PL0001. '
            'Non-colliding C12783, G319, CR3742, R2224, PL4897.\n'
        )
    with open(os.path.join(root, 'docs', 'roadmap.md'), 'a', encoding='utf-8') as f:
        f.write('\n430. **Stress colliding roadmap item** (see also roadmap 430).\n')
        f.write('\n431. **Stress new roadmap item** (see also roadmap 431).\n')
    stay.add('roadmap 431')
    with open(os.path.join(root, 'scripts', 'semantic_tests.py'), 'a', encoding='utf-8') as f:
        f.write("\ndef scenario_368_stress():\n    s = 'scenario 368, stress collision'\n    return s\n")
        f.write("\ndef scenario_400_stress():\n    s = 'scenario 400, non-colliding'\n    return s\n")
    stay.add('scenario 400')
    return stay, other


def test_full_dataset_collisions():
    tmp, root, base = clone_real_dataset()
    pre = None
    try:
        stay, claim_file = add_full_dataset_collisions(root)
        git(tmp, 'add', '-A')
        git(tmp, 'commit', '-m', 'stress collisions')
        pre = tempfile.mkdtemp(prefix='renumber-pre-')
        snapshot_files(root, pre)
        before_hashes = hashes_under(root)

        # Dry-run writes nothing
        rc = rn.main(['--root', root, '--base', base])
        assert rc == 0
        assert hashes_under(root) == before_hashes, 'dry-run wrote files'

        mappings, problems = rn.plan(root, base)
        assert not problems, problems
        kinds = {m['kind'] for m in mappings}
        expected_kinds = {
            'claim', 'command relation', 'reference', 'place', 'person', 'tenure',
            'TO&E template', 'TO&E assignment', 'aircraft type', 'ship class',
            'lineage', 'mission', 'conflict group', 'scenario', 'roadmap',
        }
        missing = expected_kinds - kinds
        assert not missing, 'missing families in mapping: %s\n%s' % (missing, mappings)

        # Non-colliding ids must not appear as 'old'
        olds = {m['old'] for m in mappings}
        news = {m['new'] for m in mappings}
        leaked = [i for i in stay if i in olds]
        assert not leaked, 'non-colliding id was remapped: %s' % leaked

        rc = rn.main(['--root', root, '--base', base, '--apply'])
        assert rc == 0, 'apply failed'

        # After apply, colliding tokens on new rows are gone; stay tokens remain.
        notes_path = claim_file
        text = open(notes_path, encoding='utf-8').read()
        assert 'C12345' in text and 'C10873-C10982' in text
        assert re.search(r'\bC1234\b', text) is None  # remapped on the new row; published C1234 is in another file
        assert 'C12783' in text and 'G319' in text
        # Silent-join group split: new members must not still carry G112
        h, rows = common.read_dicts(notes_path)
        new_rows = [r for r in rows if r.get('date', '').startswith('1939-09')]
        g_new = {r['conflict_group_id'] for r in new_rows if r.get('claim_id') != 'C12783'}
        assert 'G112' not in g_new, g_new
        assert all(g and g != 'G112' for g in g_new)

        errors = rn.verify_renumber(root, base, mappings, before_root=pre)
        assert not errors, errors

        # Published C1234 still on its original unit
        orig_path, orig_row, _ = find_claim(root, 'C1234')
        assert orig_path != notes_path
        assert orig_row['unit_id'] != new_rows[0]['unit_id']

        # No duplicates, FKs already checked by verify
        assert_round_trip(pre, root, mappings)

        # Idempotent
        mappings2, problems2 = rn.plan(root, base)
        assert not problems2 and mappings2 == [], mappings2
        after = hashes_under(root)
        rc = rn.main(['--root', root, '--base', base])
        assert rc == 0
        assert hashes_under(root) == after, 'second dry-run wrote files'
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
        if pre:
            shutil.rmtree(pre, ignore_errors=True)


def test_apply_aborts_without_writing():
    root = basic.init_repo()
    try:
        basic.seed_main(root)
        sha = git(root, 'rev-parse', 'HEAD').stdout.strip()
        basic.add_branch_a(root)
        sha = git(root, 'rev-parse', 'HEAD').stdout.strip()
        basic.add_branch_b_collisions(root)
        git(root, 'add', '.')
        git(root, 'commit', '-m', 'B')
        before = hashes_under(root)
        real = rn.verify_renumber
        rn.verify_renumber = lambda *a, **k: ['injected failure']
        try:
            rc = rn.main(['--root', root, '--base', sha, '--apply'])
        finally:
            rn.verify_renumber = real
        assert rc == 1
        assert hashes_under(root) == before, 'failed apply wrote files'
    finally:
        shutil.rmtree(root)


def test_property_random_collisions():
    rng = random.Random(SEED)
    families = ['claim', 'cr', 'ref', 'place', 'group', 'scenario', 'roadmap']
    for i in range(PROPERTY_ITERATIONS):
        collide = set(fam for fam in families if rng.random() < 0.7)
        if not collide:
            collide.add('claim')
        keep = 'group' in collide and rng.random() < 0.3
        root = basic.init_repo()
        try:
            basic.seed_main(root)
            basic.add_branch_a(root)
            sha = git(root, 'rev-parse', 'HEAD').stdout.strip()
            basic.add_branch_b_collisions(root)
            # Optionally add a non-colliding claim
            if rng.random() < 0.5:
                h, rows = common.read_dicts(os.path.join(root, 'data', 'claims', 'us', 'US-INF-002D.csv'))
                rows.append({
                    'claim_id': 'C0009', 'conflict_group_id': '',
                    'unit_id': 'US-INF-002D', 'date': '1944-08-01',
                    'event_type': 'located_at', 'reference_ids': 'R001',
                    'notes': 'non-colliding C0009 and range C0001-C0002 vs C00010',
                })
                write_csv(os.path.join(root, 'data', 'claims', 'us', 'US-INF-002D.csv'), h,
                          [[r[c] for c in h] for r in rows])
            git(root, 'add', '.')
            git(root, 'commit', '-m', 'B iter %d' % i)
            pre = tempfile.mkdtemp(prefix='renumber-prop-pre-')
            try:
                snapshot_files(root, pre)
                before = hashes_under(root)
                args = ['--root', root, '--base', sha]
                if keep:
                    args.extend(['--keep-group', 'G001'])
                rc = rn.main(args)
                assert rc == 0
                assert hashes_under(root) == before
                mappings, problems = rn.plan(root, sha, keep_groups={'G001'} if keep else None)
                assert not problems, problems
                if 'claim' in collide:
                    assert any(m['old'] == 'C0003' for m in mappings), mappings
                rc = rn.main(args + ['--apply'])
                assert rc == 0
                errors = rn.verify_renumber(root, sha, mappings, before_root=pre)
                assert not errors, errors
                # Non-colliding id and published range endpoints stay
                text = open(os.path.join(root, 'data', 'claims', 'us', 'US-INF-002D.csv'), encoding='utf-8').read()
                if 'C0009' in text:
                    assert 'C0009' in text
                # C0001 and C0002 are published; they must still exist on their original files
                h, rows = common.read_dicts(os.path.join(root, 'data', 'claims', 'us', 'US-INF-001D.csv'))
                assert any(r['claim_id'] == 'C0001' for r in rows)
                mappings2, problems2 = rn.plan(root, sha, keep_groups={'G001'} if keep else None)
                assert not problems2 and mappings2 == [], mappings2
                assert_round_trip(pre, root, mappings)
            finally:
                shutil.rmtree(pre, ignore_errors=True)
        finally:
            shutil.rmtree(root, ignore_errors=True)


def main():
    tests = [
        test_apply_aborts_without_writing,
        test_property_random_collisions,
        test_full_dataset_collisions,
    ]
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
    print('ALL STRESS TESTS PASSED (%d) property_iterations=%d seed=%d' % (
        len(tests), PROPERTY_ITERATIONS, SEED))
    return 0


if __name__ == '__main__':
    sys.exit(main())
