#!/usr/bin/env python3
"""Build the references table from the citations in the claims and the unit table.

Inputs
  data/claims/**.csv     source (URLs separated by ' | ', then ' ; coords: <note>'), strength_json.source
  data/units.csv         formed_date_source (URL), listing_source and initial_parent_source (tokens)
  data/references_meta.csv   HAND-MAINTAINED metadata, one row per reference: stable reference_id, URL,
                         title, citation, type, publisher, licence, reliability, link status, ...

Outputs (deterministic; the claims stay the evidence, these tables are derived):
  data/references.csv        one row per reference: the metadata plus claims_count, units_count, first_claim_id
  build/claim_references.csv claim_id, reference_id, role (source | coordinates | strength), locator (URL fragment, e.g. page285)
  build/unit_references.csv  unit_id, field (formed_date_source | listing_source | initial_parent_source), reference_id

A cited URL is normalised (fragment removed, ibiblio.org -> www.ibiblio.org) and must match the url of a row in
references_meta.csv. A reference may instead be matched by a regular expression on the coordinate note
(match_pattern, for services such as Nominatim), by a unit source token (source_token) or by the text of a
strength_json source (strength_alias, ';'-separated). Rows keep their reference_id forever; new ones are appended.

Usage
  python scripts/build_references.py                 write data/references.csv, build/claim_references.csv, build/unit_references.csv
  python scripts/build_references.py --check         exit 1 if those files are stale or a cited URL has no metadata row
  python scripts/build_references.py --seed          append skeleton metadata rows for cited URLs that have none (then edit them)
  python scripts/build_references.py --check-links   HTTP-check every reference URL (polite, one request at a time) and record
                                                     link_status / link_checked in references_meta.csv; page titles are cached
                                                     in .cache/links.json
(build.py also writes and checks these files.)
"""
import argparse
import csv
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from urllib.parse import quote, urlsplit, urlunsplit

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common  # noqa: E402

META_CSV = os.path.join(common.ROOT, 'data', 'references_meta.csv')
REFERENCES_CSV = os.path.join(common.ROOT, 'data', 'references.csv')
LINK_CACHE = os.path.join(common.ROOT, '.cache', 'links.json')

META_HEADER = ['reference_id', 'url', 'match_pattern', 'source_token', 'strength_alias', 'short_title', 'full_citation', 'source_type',
               'publisher', 'accessed_date', 'license_or_status', 'reliability_note', 'used_for', 'link_status', 'link_checked']
REF_HEADER = ['reference_id', 'short_title', 'full_citation', 'source_type', 'publisher', 'url', 'original_url', 'accessed_date',
              'license_or_status', 'reliability_note', 'claims_count', 'units_count', 'first_claim_id', 'used_for', 'link_status',
              'link_checked']
CLAIM_REF_HEADER = ['claim_id', 'reference_id', 'role', 'locator']
UNIT_REF_HEADER = ['unit_id', 'field', 'reference_id']
UA = 'ww2-unit-locations-reference-check/1.0 (https://github.com/scottstarsman/UnitLocationData)'


def norm_url(u):
    """Normalised key of a cited URL: no fragment, one host spelling for ibiblio.org. Returns (url, fragment)."""
    u = u.strip()
    s = urlsplit(u)
    host = s.netloc
    if host == 'ibiblio.org':
        host = 'www.ibiblio.org'
    return urlunsplit((s.scheme, host, s.path, s.query, '')), s.fragment


def original_url(u):
    """For Wayback Machine copies, the address that was archived; blank otherwise."""
    m = re.match(r'https?://web\.archive\.org/web/\d+[a-z_]*/(https?://.+)$', u)
    return m.group(1) if m else ''


def split_source(source):
    """URLs of a claim's source column and the coordinate note (text after ' ; ')."""
    urls, note = [], ''
    for part in source.split(' | '):
        head, _sep, tail = part.partition(' ; ')
        head = head.strip()
        if head:
            urls.append(head)
        if tail:
            note = tail.strip()
    return urls, note


def read_meta():
    if not os.path.isfile(META_CSV):
        return [], []
    return common.read_dicts(META_CSV)


def strength_sources(row):
    s = row.get('strength_json', '')
    if not s:
        return []
    try:
        src = json.loads(s).get('source', '')
    except ValueError:
        return []
    out, prefix = [], ''
    for part in src.split(';'):
        part = re.sub(r'\s*\(.*?\)\s*$', '', part.strip())
        if not part:
            continue
        m = re.match(r'(Wikipedia|CMH)\s', part)
        if m:
            prefix = m.group(1) + ' '
        else:
            part = prefix + part
        out.append(part)
    return out


def derive():
    """Return (claim_refs, unit_refs, per-reference stats, missing) from the data and the metadata file."""
    _h, meta = read_meta()
    by_url = {m['url']: m for m in meta if m['url']}
    patterns = [(re.compile(m['match_pattern']), m) for m in meta if m['match_pattern']]
    tokens = {m['source_token']: m for m in meta if m['source_token']}
    aliases = {}
    for m in meta:
        for a in m['strength_alias'].split(';'):
            if a.strip():
                aliases[a.strip()] = m
    missing = {}   # url -> first claim/unit
    claim_refs, unit_refs = set(), set()
    stats = {m['reference_id']: {'claims': set(), 'units': set()} for m in meta}

    _hh, claims = common.load_all_claims()
    claims = sorted(claims, key=lambda r: r['claim_id'])
    for r in claims:
        urls, note = split_source(r['source'])
        for pos, raw in enumerate(urls):
            url, frag = norm_url(raw)
            m = by_url.get(url)
            if m is None:
                missing.setdefault(url, r['claim_id'])
                continue
            claim_refs.add((r['claim_id'], m['reference_id'], 'source', frag))
            stats[m['reference_id']]['claims'].add(r['claim_id'])
        for rx, m in patterns:
            if note and rx.search(note):
                claim_refs.add((r['claim_id'], m['reference_id'], 'coordinates', ''))
                stats[m['reference_id']]['claims'].add(r['claim_id'])
        for a in strength_sources(r):
            m = aliases.get(a)
            if m is None:
                missing.setdefault('strength source: ' + a, r['claim_id'])
                continue
            claim_refs.add((r['claim_id'], m['reference_id'], 'strength', ''))
            stats[m['reference_id']]['claims'].add(r['claim_id'])

    _uh, units = common.read_dicts(common.UNITS_CSV)
    for u in units:
        if u['formed_date_source']:
            url, _frag = norm_url(u['formed_date_source'])
            m = by_url.get(url)
            if m is None:
                missing.setdefault(url, u['unit_id'])
            else:
                unit_refs.add((u['unit_id'], 'formed_date_source', m['reference_id']))
                stats[m['reference_id']]['units'].add(u['unit_id'])
        for field in ('listing_source', 'initial_parent_source'):
            for t in u[field].split(';'):
                t = t.strip()
                if not t:
                    continue
                m = tokens.get(t)
                if m is None:
                    if t != 'WPUNIT':   # WPUNIT = the unit's own Wikipedia article, listed individually as formed_date_source
                        missing.setdefault('token: ' + t, u['unit_id'])
                    continue
                unit_refs.add((u['unit_id'], field, m['reference_id']))
                stats[m['reference_id']]['units'].add(u['unit_id'])
    return sorted(claim_refs), sorted(unit_refs), stats, missing, meta


def outputs():
    """Return {path relative to the repository root: bytes}."""
    claim_refs, unit_refs, stats, missing, meta = derive()
    if missing:
        raise SystemExit('cited but not in data/references_meta.csv (run scripts/build_references.py --seed, then edit the new rows):\n'
                         + '\n'.join('  %s (first cited by %s)' % kv for kv in sorted(missing.items())))
    rows = []
    for m in sorted(meta, key=lambda m: m['reference_id']):
        st = stats[m['reference_id']]
        rows.append([m['reference_id'], m['short_title'], m['full_citation'], m['source_type'], m['publisher'], m['url'],
                     original_url(m['url']), m['accessed_date'], m['license_or_status'], m['reliability_note'],
                     str(len(st['claims'])), str(len(st['units'])), min(st['claims']) if st['claims'] else '', m['used_for'],
                     m['link_status'] or 'unchecked', m['link_checked']])
    return {
        'data/references.csv': common.csv_bytes(REF_HEADER, rows),
        'build/claim_references.csv': common.csv_bytes(CLAIM_REF_HEADER, [list(r) for r in claim_refs]),
        'build/unit_references.csv': common.csv_bytes(UNIT_REF_HEADER, [list(r) for r in unit_refs]),
    }


# ---------------------------------------------------------------- seeding

GREEN = {
    'USA-E-XChannel': ('Harrison, Gordon A.', 'Cross-Channel Attack', '1951'),
    'USA-E-Breakout': ('Blumenson, Martin', 'Breakout and Pursuit', '1961'),
    'USA-E-Lorraine': ('Cole, Hugh M.', 'The Lorraine Campaign', '1950'),
    'USA-E-Siegfried': ('MacDonald, Charles B.', 'The Siegfried Line Campaign', '1963'),
    'USA-E-Riviera': ('Clarke, Jeffrey J., and Robert Ross Smith', 'Riviera to the Rhine', '1993'),
    'USA-E-Ardennes': ('Cole, Hugh M.', 'The Ardennes: Battle of the Bulge', '1965'),
    'USA-E-Supreme': ('Pogue, Forrest C.', 'The Supreme Command', '1954'),
    'USA-A-Utah': ('Historical Division, War Department', 'Utah Beach to Cherbourg', '1948'),
}


def seed_row(url):
    """Skeleton metadata for a URL with none; the title and citation are refined by hand or by the one-off title pass."""
    s = urlsplit(url)
    host, path = s.netloc, s.path
    last = re.sub(r'\.html?$', '', path.rstrip('/').rsplit('/', 1)[-1])
    d = dict.fromkeys(META_HEADER, '')
    d['url'] = url
    d['short_title'] = last
    if host.endswith('ibiblio.org') and '/hyperwar/USA/' in path:
        series = path.split('/hyperwar/USA/')[1].split('/')[0]
        author, title, year = GREEN.get(series, ('US Army Center of Military History', series, ''))
        chap = re.search(r'-(\d+)$', last)
        d.update(source_type='official_history', publisher='HyperWar Foundation (ibiblio), mirror of US Army Center of Military History',
                 license_or_status='Public domain (US government work); HyperWar is a mirror',
                 reliability_note='primary/official history, High for dates and places the text states',
                 short_title='%s ch. %s' % (title, chap.group(1)) if chap else title,
                 full_citation='%s, %s (US Army in World War II, Washington: Center of Military History, %s), chapter %s.' % (author, title, year, chap.group(1) if chap else '?'),
                 used_for='dated unit moves and command changes')
    elif host == 'en.wikipedia.org' or host == 'de.wikipedia.org' or host == 'fr.wikipedia.org':
        lang = {'en.wikipedia.org': 'English', 'de.wikipedia.org': 'German', 'fr.wikipedia.org': 'French'}[host]
        from urllib.parse import unquote
        title = unquote(path.split('/wiki/', 1)[-1]).replace('_', ' ')
        d.update(source_type='encyclopedia', publisher='Wikimedia Foundation (%s Wikipedia)' % lang,
                 license_or_status='CC BY-SA 4.0 (Wikipedia text)', reliability_note='secondary, medium; a finding aid',
                 short_title='Wikipedia: ' + title, full_citation='Wikipedia contributors, "%s", %s Wikipedia.' % (title, lang),
                 used_for='unit details, formation dates, order of battle')
    elif host.endswith('lexikon-wehrmacht.de'):
        d.update(source_type='reference_compilation', publisher='Lexikon der Wehrmacht', license_or_status='All rights reserved by the site; only short facts (dates, names) are used',
                 reliability_note='secondary compilation, medium-high for formation dates and subordination', used_for='German formation dates and subordination')
    elif host.endswith('ww2byday.com'):
        d.update(source_type='reference_compilation', publisher='World War II by Day', license_or_status='Copyrighted web page; only facts and the URL are used',
                 reliability_note='secondary compilation of the CMH ETO order of battle, medium', used_for='command-post lists (places)')
    elif host == 'web.archive.org':
        d.update(source_type='assignment_table', publisher='US Army Center of Military History, via Internet Archive Wayback Machine',
                 license_or_status='Public domain (US government work); archive copy', reliability_note='primary/official table, High for dates and CP towns as tabulated',
                 used_for='division arrival and assignment dates, command posts')
    else:
        d.update(source_type='other', publisher=host, license_or_status='Copyrighted web page: only facts and the URL are used',
                 reliability_note='secondary')
    return d


def do_seed():
    meta_header, meta = read_meta()
    _c, _u, _s, missing, _m = derive()
    urls = sorted(k for k in missing if k.startswith('http'))
    nxt = max([int(m['reference_id'][1:]) for m in meta] or [0]) + 1
    for u in urls:
        d = seed_row(u)
        d['reference_id'] = 'R%03d' % nxt
        nxt += 1
        meta.append(d)
    write_meta(meta)
    print('added %d skeleton rows to data/references_meta.csv' % len(urls))
    rest = [k for k in missing if not k.startswith('http')]
    if rest:
        print('still unmapped (add a token / alias row by hand):')
        for k in rest:
            print('  ' + k)


def write_meta(meta):
    meta = sorted(meta, key=lambda m: m['reference_id'])
    with open(META_CSV, 'wb') as f:
        f.write(common.csv_bytes(META_HEADER, [[m[c] for c in META_HEADER] for m in meta]))


# ---------------------------------------------------------------- link checking

def fetch(url, delay):
    time.sleep(delay)
    url = quote(url, safe=":/?&=%#@!$'()*+,;~")   # non-ASCII characters in a cited URL must be percent-encoded to be sent
    req = urllib.request.Request(url, headers={'User-Agent': UA, 'Accept': 'text/html,*/*;q=0.5'})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            body = r.read(120000)
            code = r.status
    except urllib.error.HTTPError as e:
        return e.code, ''
    except Exception as e:   # timeouts, DNS, TLS
        return 0, str(e)[:80]
    title = ''
    m = re.search(rb'<title[^>]*>(.*?)</title>', body, re.I | re.S)
    if m:
        title = re.sub(r'\s+', ' ', m.group(1).decode('utf-8', 'replace')).strip()
    return code, title


def status_of(code):
    if 200 <= code < 400:
        return 'ok'
    if code in (401, 403, 429):
        return 'blocked_403'
    if code in (404, 410):
        return 'not_found'
    return 'error'


def do_check_links(delay, only_unchecked):
    meta_header, meta = read_meta()
    os.makedirs(os.path.dirname(LINK_CACHE), exist_ok=True)
    cache = json.load(open(LINK_CACHE, encoding='utf-8')) if os.path.isfile(LINK_CACHE) else {}
    today = time.strftime('%Y-%m-%d')
    n = 0
    for m in sorted(meta, key=lambda m: m['reference_id']):
        if not m['url'] or (only_unchecked and m['link_status'] in ('ok', 'blocked_403', 'not_found')):
            continue
        code, title = fetch(m['url'], delay)
        if code == 0:   # one retry for transient errors
            code, title = fetch(m['url'], delay * 4)
        cache[m['url']] = {'code': code, 'title': title if code else '', 'error': title if not code else ''}
        m['link_status'] = status_of(code)
        m['link_checked'] = today
        n += 1
        if n % 25 == 0:
            print('  checked %d' % n, flush=True)
            json.dump(cache, open(LINK_CACHE, 'w', encoding='utf-8'), indent=0, ensure_ascii=False)
            write_meta(meta)
    json.dump(cache, open(LINK_CACHE, 'w', encoding='utf-8'), indent=0, ensure_ascii=False)
    write_meta(meta)
    from collections import Counter
    print('checked %d URLs:' % n, dict(Counter(m['link_status'] for m in meta)))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--check', action='store_true')
    ap.add_argument('--seed', action='store_true')
    ap.add_argument('--check-links', action='store_true')
    ap.add_argument('--only-unchecked', action='store_true', help='with --check-links: skip rows that already have a status')
    ap.add_argument('--delay', type=float, default=0.6, help='seconds between requests (default 0.6)')
    a = ap.parse_args()
    if a.seed:
        do_seed()
        return 0
    if a.check_links:
        do_check_links(a.delay, a.only_unchecked)
        return 0
    out = outputs()
    bad = []
    for rel, data in out.items():
        p = os.path.join(common.ROOT, rel)
        if a.check:
            if not os.path.isfile(p) or open(p, 'rb').read() != data:
                bad.append('missing or out of date: ' + rel)
        else:
            with open(p, 'wb') as f:
                f.write(data)
    if a.check:
        if bad:
            print('\n'.join(bad))
            print('run python scripts/build_references.py and commit the result')
            return 1
        print('references are up to date (%d files)' % len(out))
        return 0
    print('wrote %d files (data/references.csv, build/claim_references.csv, build/unit_references.csv)' % len(out))
    return 0


if __name__ == '__main__':
    sys.exit(main())
