#!/usr/bin/env python3
"""source_tree_sha256 hashes only tracked, non-generated WorldWar2 files.

Untracked and gitignored files must not change the hash (the function uses
git ls-files). The committed manifest must match the current tree; otherwise
CI's 'build.py' then 'git status' step fails even when --check follows a
fresh write.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build  # noqa: E402
import common  # noqa: E402

REPO = os.path.dirname(common.ROOT)
MANIFEST = os.path.join(common.ROOT, 'build', 'manifest.json')


def test_untracked_and_ignored_files_do_not_change_hash():
    before = build.source_tree_sha256()
    untracked = os.path.join(common.ROOT, 'source_tree_sha256_probe_untracked.txt')
    ignored_dir = os.path.join(common.ROOT, 'scripts', '__pycache__')
    ignored = os.path.join(ignored_dir, 'source_tree_sha256_probe.txt')
    os.makedirs(ignored_dir, exist_ok=True)
    created = []
    try:
        with open(untracked, 'w', encoding='utf-8') as f:
            f.write('untracked probe; must not enter source_tree_sha256\n')
        created.append(untracked)
        with open(ignored, 'w', encoding='utf-8') as f:
            f.write('gitignored probe; must not enter source_tree_sha256\n')
        created.append(ignored)
        after = build.source_tree_sha256()
    finally:
        for p in created:
            try:
                os.remove(p)
            except OSError:
                pass
    assert after == before, 'source_tree_sha256 changed when untracked or gitignored files were added'
    assert after == build.source_tree_sha256()


def test_hashed_paths_are_tracked_and_skip_generated():
    paths = build.source_tree_paths()
    assert paths, 'expected tracked source paths'
    assert all(p.startswith('WorldWar2/') for p in paths)
    for p in paths:
        assert not p.startswith(build.GENERATED_SKIP_PREFIX), p
        assert p not in build.GENERATED_SKIP, p
    for skipped in (
        'WorldWar2/docs/coverage.md',
        'WorldWar2/data/references.csv',
        'WorldWar2/build/manifest.json',
    ):
        assert skipped not in paths, skipped
    # a file we just proved is not hashed should also not appear
    assert 'WorldWar2/source_tree_sha256_probe_untracked.txt' not in paths


def test_committed_manifest_matches_current_tree():
    with open(MANIFEST, encoding='utf-8') as f:
        man = json.load(f)
    got = build.source_tree_sha256()
    assert man['source_tree_sha256'] == got, (
        'build/manifest.json source_tree_sha256 is %s but the current source tree hashes to %s; '
        'run python scripts/build.py and commit the result' % (man['source_tree_sha256'], got)
    )


def main():
    tests = [
        test_untracked_and_ignored_files_do_not_change_hash,
        test_hashed_paths_are_tracked_and_skip_generated,
        test_committed_manifest_matches_current_tree,
    ]
    failed = 0
    for fn in tests:
        try:
            fn()
            print('OK', fn.__name__)
        except Exception as e:
            failed += 1
            print('FAIL', fn.__name__, e)
    if failed:
        print('FAILED: %d of %d source_tree_sha256 tests' % (failed, len(tests)))
        return 1
    print('ALL SOURCE_TREE_SHA256 TESTS PASSED (%d)' % len(tests))
    return 0


if __name__ == '__main__':
    sys.exit(main())
