#!/usr/bin/env python3
"""One-time migration: places table (F2) and removal of derived claim columns (F6). Standard library; the country/region lookup also needs
`pip install reverse_geocoder` (offline GeoNames, used only when --apply writes a new places.csv).

What it does (all from the claims as they were at the commit it is run on; see docs/changelog.md):
  1. data/places.csv           one place per (folded first name segment, point within 3 km): same name and same point (or a point within 3 km that
                               is another read of the same place) = one place with alias names; different named places that merely share a geocoded
                               point stay separate places (an area or sector is its own place of kind area/line). Canonical coordinate = the pair used by
                               most claims of the place.
  2. data/claims/**            location_name -> place_id + location_qualifier (the text that was a prefix `vicinity of` or a trailing parenthesis),
                               coord_override (reason) on a claim whose point differs from its place; the coordinate note leaves `source`
                               (it is now places.coord_source_note, or coord_override for a claim that has its own); location_temporal_offset_days
                               and strength_status are dropped (derived, see scripts/places.py); strength_json gets a `status` key where a status was
                               stored without a figure to carry it (see STATUS_ONLY below).
  3. data/claim_reference_roles.csv   rows that only say "the coordinate service" for a gazetteer_geocoder reference are removed (derived by build_references.py).

Usage: python scripts/migrate_places.py --dry-run        print the plan and the lists for review, write nothing
       python scripts/migrate_places.py --apply          write data/places.csv, the claim files and the roles table
       python scripts/migrate_places.py --verify REF     regenerate the old values from the new data and diff them against git ref REF
"""
import argparse
import collections
import csv
import io
import json
import os
import re
import subprocess
import sys
import unicodedata

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common  # noqa: E402
import places as pl  # noqa: E402
import build_references as br  # noqa: E402

MERGE_KM = 3.0
OLD_EXTRA = ['location_name', 'location_temporal_offset_days', 'strength_status']
NEW_COLS = ['place_id', 'location_qualifier', 'coord_override']
# Canonical name to use where the most-used or most-complete form is not the right one (key: fold() of the first segment)
CANON = {'mons': 'Mons, Hainaut', 'omahabeach': 'Omaha Beach', 'utahbeach': 'Utah Beach'}
# kind of a place: explicit decisions after review of the rule output; the rule is in kind_of()
KIND_FIX = {'Meuse crossings between Verdun and Commercy': 'line', 'Corisy-la-Foret, Manche': 'point'}
# A status that was stored on a row without any strength figure to carry it: the claim's own notes say what the source reports, the strength_json
# source is a reference the claim already cites (alias in data/references_meta.csv strength_alias). Nothing is estimated.
STATUS_ONLY = {
    'C0132': ('heavily_depleted', 'CMH Cross-Channel Attack ch. X', 'division artillery almost wholly lost; elements attempting to withdraw south were blocked 17-18 June (from the claim notes)'),
    'C0127': ('heavily_depleted', 'CMH Cross-Channel Attack ch. IX', 'by 16-17 June only a Kampfgruppe of about regimental strength, losing about 500 men to 29th Division attacks (from the claim notes)'),
    'C0189': ('reduced', 'Wikipedia Operation Epsom', 'the division lost nearly 40 tanks on Hill 112 slopes by the end of the day and was surrounded on three sides (from the claim notes)'),
}
AREA_RE = re.compile(r'\b(area|areas|sector|zone|zones|bridgehead|beachhead|valley|coast|beach|beaches|gap|box|landing|assembly|defences|salient|forest|'
                     r'foret|region|approaches|approach|flank|staging|objective|midpoint|representative|brittany|cotentin|drop|harbour|canal)\b', re.I)
LINE_RE = re.compile(r'\b(line|axis|route|front)\b', re.I)
DIR_RE = re.compile(r'^(north|south|east|west|northwest|northeast|southwest|southeast|southern|northern|eastern|western|central|coast)\b', re.I)
COUNTRY_NAMES = {'FR': 'France', 'BE': 'Belgium', 'LU': 'Luxembourg', 'NL': 'Netherlands', 'DE': 'Germany', 'GB': 'United Kingdom'}


def fold(s):
    s = unicodedata.normalize('NFKD', s)
    s = ''.join(c for c in s if not unicodedata.combining(c)).lower()
    s = re.sub(r'\b(saint|sainte)\b', lambda m: 'st' if m.group(1) == 'saint' else 'ste', s)
    s = re.sub(r'[^a-z0-9 ]', ' ', s)
    s = re.sub(r'^(le|la|les|l) ', '', s.strip())
    return re.sub(r'\s+', '', s)


def split_name(n):
    """(base name, qualifier) of an old location_name: a leading 'vicinity of ' becomes the reserved qualifier token, a trailing parenthesis the rest."""
    q, s = [], n
    m = re.match(r'^vicinity of (.+)$', s)
    if m:
        s = m.group(1)
        q.append(pl.VICINITY)
    m = re.match(r'^(.*\S)\s*\(([^()]*)\)$', s)
    if m:
        s = m.group(1)
        q.append(m.group(2))
    return s.strip(), '; '.join(q)


def kind_of(base):
    f = unicodedata.normalize('NFKD', base)
    f = ''.join(c for c in f if not unicodedata.combining(c))
    if LINE_RE.search(f):
        return 'line'
    if AREA_RE.search(f) or DIR_RE.search(f) or re.search(r'\w/\w| / |\u2013| - ', f):
        return 'area'
    return 'point'


def tail_of(source):
    m = re.search(r' ; (coords?: .*)$', source)
    return m.group(1) if m else ''


def tail_text(source):
    return re.sub(r'^coords?:\s*', '', tail_of(source))


def read_old(ref=None):
    """Old claim files as {path: (header, rows)}; from the working tree or from git ref."""
    out = {}
    if ref is None:
        for p in common.claim_files():
            out[os.path.relpath(p, common.ROOT)] = common.read_rows(p)
        return out
    names = subprocess.run(['git', '-C', common.ROOT, 'ls-tree', '-r', '--name-only', ref, 'data/claims'], capture_output=True, text=True, check=True).stdout.split()
    for n in names:
        txt = subprocess.run(['git', '-C', common.ROOT, 'show', '%s:%s' % (ref, n)], capture_output=True, check=True).stdout.decode('utf-8')
        rd = csv.reader(io.StringIO(txt, newline=''))
        h = next(rd)
        out[n] = (h, [r for r in rd])
    return out


def plan(old):
    """Group the claims into places. Returns (places (list of dicts, without ids), assign {claim_id: place index})."""
    rows = []
    for path, (h, rs) in old.items():
        for r in rs:
            d = dict(zip(h, r))
            d['_path'] = path
            rows.append(d)
    rows.sort(key=lambda d: d['claim_id'])
    groups = collections.defaultdict(list)
    for d in rows:
        d['_base'], d['_qual'] = split_name(d['location_name'])
        groups[fold(re.split(r',', d['_base'])[0])].append(d)
    clusters = []
    for _k, rs in sorted(groups.items()):
        cl = []
        for d in rs:
            p = (float(d['latitude']), float(d['longitude']))
            hit = next((c for c in cl if any(pl.km(*p, *q) <= MERGE_KM for q in c['pts'])), None)
            if hit:
                hit['rows'].append(d)
                hit['pts'].append(p)
            else:
                cl.append({'rows': [d], 'pts': [p], 'key': _k})
        clusters.extend(cl)
    out = []
    for c in clusters:
        rs = c['rows']
        cnt = collections.Counter(d['_base'] for d in rs)
        cands = sorted(cnt, key=lambda b: (',' in b, any(ord(ch) > 127 for ch in b), not re.match(r'^St[- ]', b), cnt[b], len(b), b), reverse=True)
        name = CANON.get(c['key']) if len(cnt) > 1 and c['key'] in CANON else cands[0]
        if c['key'] in CANON and CANON[c['key']] in cnt:
            name = CANON[c['key']]
        elif c['key'] in CANON and len(cnt) > 1:
            name = CANON[c['key']]
        alts = sorted(b for b in cnt if b != name)
        coords = collections.Counter((d['latitude'], d['longitude']) for d in rs)
        best = sorted(coords, key=lambda k: (-coords[k], min(d['claim_id'] for d in rs if (d['latitude'], d['longitude']) == k)))[0]
        at = [d for d in rs if (d['latitude'], d['longitude']) == best]
        tails = collections.Counter(tail_text(d['source']) for d in at if tail_text(d['source']))
        note = sorted(tails, key=lambda t: (-(':' in t or '(' in t), -tails[t], -len(t), t))[0] if tails else ''
        refs = collections.Counter(x for d in at for x in br.parse_ids(d['reference_ids']) if x in ('R001', 'R002'))
        out.append({'name': name, 'alts': alts, 'kind': KIND_FIX.get(name) or kind_of(name), 'lat': best[0], 'lon': best[1],
                    'prec': min(float(d['precision_km']) for d in rs), 'refs': refs, 'note': note, 'rows': rs, 'key': c['key']})
    # two different places must not share a name: the one with fewer claims keeps the whole old location_name as its name (qualifier included)
    byname = collections.defaultdict(list)
    for p in out:
        byname[fold(p['name'])].append(p)
    for _n, ps in byname.items():
        if len(ps) > 1:
            ps.sort(key=lambda p: (-len(p['rows']), min(d['claim_id'] for d in p['rows'])))
            for p in ps[1:]:
                cnt = collections.Counter(d['location_name'] for d in p['rows'])
                p['alts'] = []
                p['name'] = sorted(cnt, key=lambda n: (-cnt[n], n))[0]
                p['full'] = True
                p['kind'] = KIND_FIX.get(p['name']) or kind_of(p['name'])
    return out


def geo_lookup(pts):
    try:
        import reverse_geocoder as rg
    except ImportError:
        raise SystemExit('pip install reverse_geocoder (one-time country/region lookup for the new places.csv)')
    res = rg.search(pts, mode=1)
    return [(r['cc'], r['admin1']) for r in res]


def fmt_prec(x):
    return str(int(x)) if x == int(x) else str(x)


def build_places(pls):
    pls.sort(key=lambda p: (fold(p['name']), float(p['lat']), float(p['lon'])))
    geo = geo_lookup([(float(p['lat']), float(p['lon'])) for p in pls])
    rows = []
    for i, (p, (cc, adm)) in enumerate(zip(pls, geo), start=1):
        p['id'] = 'PL%04d' % i
        ref = p['refs'].most_common(1)[0][0] if p['refs'] else ''
        rows.append({'place_id': p['id'], 'name': p['name'], 'alt_names': '; '.join(p['alts']), 'kind': p['kind'], 'latitude': p['lat'], 'longitude': p['lon'],
                     'precision_km': fmt_prec(p['prec']), 'country': cc, 'region': adm, 'coord_reference_id': ref,
                     'coord_source_note': p['note'] if p['note'] else ''})
    return rows


def new_claim_rows(old, pls):
    """Return {path: (new_header, new_rows)} and the report data."""
    place_of = {}
    for p in pls:
        for d in p['rows']:
            place_of[d['claim_id']] = p
    meta = {m['reference_id']: m for m in br.read_meta()[1]}
    aliases = {}
    for m in meta.values():
        for a in m['strength_alias'].split(';'):
            if a.strip():
                aliases[a.strip()] = m['reference_id']
    out, overrides = {}, []
    for path, (h, rs) in old.items():
        nh = []
        for c in h:
            if c == 'location_name':
                nh.extend(NEW_COLS)
            elif c not in OLD_EXTRA:
                nh.append(c)
        nrs = []
        for r in rs:
            d = dict(zip(h, r))
            p = place_of[d['claim_id']]
            _b, q = split_name(d['location_name'])
            if p.get('full'):
                q = ''
            d['place_id'], d['location_qualifier'] = p['id'], q
            d['coord_override'] = ''
            if (float(d['latitude']), float(d['longitude'])) != (float(p['lat']), float(p['lon'])):
                dist = pl.km(float(d['latitude']), float(d['longitude']), float(p['lat']), float(p['lon'])) * 1000
                d['coord_override'] = '%s; %d m from the place point' % (tail_text(d['source']) or 'coordinate read differs from the place point', int(round(dist, -1)) if dist >= 100 else int(round(dist)))
                overrides.append((d['claim_id'], p['id'], p['name'], d['latitude'], d['longitude'], p['lat'], p['lon'], int(dist)))
            # the coordinate note leaves `source` (the place, or coord_override, carries it)
            if tail_of(d['source']):
                d['source'] = d['source'][:d['source'].rindex(' ; ' + tail_of(d['source']))]
            # strength status -> strength_json status
            st = d['strength_status']
            if d['strength_json']:
                sj = json.loads(d['strength_json'])
                if st not in ('unknown', 'destroyed'):
                    new = {}
                    for k, v in sj.items():
                        if k == 'source':
                            new['status'] = st
                        new[k] = v
                    d['strength_json'] = json.dumps(new, ensure_ascii=False, separators=(',', ':'))
            elif d['claim_id'] in STATUS_ONLY:
                s, alias, note = STATUS_ONLY[d['claim_id']]
                assert s == st and alias in aliases
                d['strength_json'] = json.dumps({'basis': 'estimate', 'as_of': d['date'], 'status': s, 'source': alias, 'note': note}, ensure_ascii=False, separators=(',', ':'))
            elif st not in ('unknown', 'destroyed'):
                raise SystemExit('%s has strength_status %s and no strength_json' % (d['claim_id'], st))
            if st == 'destroyed':
                assert d['destroyed'] == 'true', d['claim_id']
            off = d['location_temporal_offset_days']
            assert off == pl.temporal_offset(d), (d['claim_id'], off)
            nrs.append([d[c] for c in nh])
        out[path] = (nh, nrs)
    return out, overrides, place_of


def only_status_added(cid, old, new):
    """True when strength_json changed only by the added `status` key (or is the new status-only record of STATUS_ONLY)."""
    if not old:
        return cid in STATUS_ONLY
    a, b = json.loads(old), json.loads(new)
    b.pop('status', None)
    return a == b


def check_no_loss(old, new, pls, rows_places):
    """Regenerate every dropped value from the new data and compare with the old claim rows; returns {topic: [diffs]}."""
    pbyid = {r['place_id']: r for r in rows_places}
    diffs = collections.defaultdict(list)
    for path, (h, rs) in old.items():
        nh, nrs = new[path]
        for r, nr in zip(rs, nrs):
            d, n = dict(zip(h, r)), dict(zip(nh, nr))
            p = pbyid[n['place_id']]
            n.update({'location_name': pl.display_name(p['name'], n['location_qualifier']), 'location_temporal_offset_days': pl.temporal_offset(n),
                      'strength_status': pl.strength_status(n)})
            for c in OLD_EXTRA:
                if d[c] != n[c]:
                    diffs[c].append((d['claim_id'], d[c], n[c]))
            for c in h:
                if c not in OLD_EXTRA and c != 'source' and d[c] != n[c]:
                    if c == 'strength_json' and only_status_added(d['claim_id'], d[c], n[c]):
                        diffs['strength_json (status key added)'].append((d['claim_id'], d[c], n[c]))
                    else:
                        diffs['other:' + c].append((d['claim_id'], d[c], n[c]))
            tail = n['coord_override'].rsplit('; ', 1)[0] if n['coord_override'] else p['coord_source_note']
            back = n['source'] + (' ; coords: ' + tail if tail else '')
            if back != d['source']:
                diffs['source'].append((d['claim_id'], tail_of(d['source']), 'coords: ' + tail))
    return diffs


def write_files(rows_places, new):
    with open(pl.PLACES_CSV, 'wb') as f:
        f.write(common.csv_bytes(pl.HEADER, [[r[c] for c in pl.HEADER] for r in rows_places]))
    for path, (nh, nrs) in new.items():
        with open(os.path.join(common.ROOT, path), 'wb') as f:
            f.write(common.csv_bytes(nh, nrs))
    h, rs = br.read_roles()
    keep = [r for r in rs if not (r['reference_id'] in ('R001', 'R002') and r['role'] == 'location' and r['basis'] == 'coordinate note names the service')]
    with open(br.ROLES_CSV, 'wb') as f:
        f.write(common.csv_bytes(h, [[r[c] for c in h] for r in keep]))
    return len(rs), len(keep)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--dry-run', action='store_true')
    ap.add_argument('--apply', action='store_true')
    ap.add_argument('--verify', metavar='REF')
    a = ap.parse_args()
    if a.verify:
        return verify(a.verify)
    old = read_old()
    pls = plan(old)
    print('%d places for %d claims' % (len(pls), sum(len(p['rows']) for p in pls)))
    if not a.apply:
        for p in sorted(pls, key=lambda p: fold(p['name'])):
            print('%-5s %-6s %s %s | %s | n=%d refs=%s' % (p['kind'], fmt_prec(p['prec']), p['lat'], p['lon'], p['name'], len(p['rows']), dict(p['refs'])))
        return 0
    rows_places = build_places(pls)
    new, overrides, _po = new_claim_rows(old, pls)
    diffs = check_no_loss(old, new, pls, rows_places)
    for k, v in diffs.items():
        print('%s: %d differences' % (k, len(v)))
    bad = [k for k in diffs if k.startswith('other:') or k in ('location_temporal_offset_days', 'strength_status')]
    if bad:
        raise SystemExit('unexpected differences in %s' % bad)
    n_old, n_new = write_files(rows_places, new)
    print('wrote data/places.csv (%d places), %d claim files, roles %d -> %d rows, %d claims with coord_override' % (len(rows_places), len(new), n_old, n_new, len(overrides)))
    return 0


def verify(ref):
    """Regenerate the dropped / reshaped values from the working tree and diff them against git ref REF."""
    old = read_old(ref)
    new = read_old()
    pbyid = {r['place_id']: r for r in pl.load().rows}
    diffs = collections.defaultdict(list)
    n = 0
    for path, (h, rs) in old.items():
        nh, nrs = new[path]
        assert len(rs) == len(nrs), path
        for r, nr in zip(rs, nrs):
            n += 1
            d, w = dict(zip(h, r)), dict(zip(nh, nr))
            p = pbyid[w['place_id']]
            w.update({'location_name': pl.display_name(p['name'], w['location_qualifier']), 'location_temporal_offset_days': pl.temporal_offset(w),
                      'strength_status': pl.strength_status(w)})
            for c in OLD_EXTRA:
                if d[c] != w[c]:
                    diffs[c].append((d['claim_id'], d[c], w[c]))
            for c in h:
                if c not in OLD_EXTRA and c != 'source' and d[c] != w[c]:
                    if c == 'strength_json' and only_status_added(d['claim_id'], d[c], w[c]):
                        diffs['strength_json (status key added)'].append((d['claim_id'], d[c], w[c]))
                    else:
                        diffs['other:' + c].append((d['claim_id'], d[c], w[c]))
            tail = w['coord_override'].rsplit('; ', 1)[0] if w['coord_override'] else p['coord_source_note']
            back = w['source'] + (' ; coords: ' + tail if tail else '')
            if back != d['source']:
                diffs['source'].append((d['claim_id'], tail_of(d['source']), 'coords: ' + tail))
            if (d['latitude'], d['longitude']) != (w['latitude'], w['longitude']):
                diffs['coordinates'].append(d['claim_id'])
    print('compared %d claims against %s' % (n, ref))
    # the 18 rows where strength_status and strength_json disagreed (status without a figure, or a figure without a status): how each is resolved
    print('strength_status / strength_json disagreement in %s, and how each row is resolved now:' % ref)
    k = 0
    for path, (h, rs) in old.items():
        nh, nrs = new[path]
        for r, nr in zip(rs, nrs):
            d, w = dict(zip(h, r)), dict(zip(nh, nr))
            if (d['strength_status'] != 'unknown') != bool(d['strength_json']):
                k += 1
                if d['strength_json']:
                    how = 'figures only, no status stated: stays unknown (no status key added)'
                elif d['destroyed'] == 'true':
                    how = 'derived from the destroyed flag (true)'
                else:
                    how = 'status-only strength_json record added (status %s, source %s)' % (json.loads(w['strength_json'])['status'], json.loads(w['strength_json'])['source'])
                print('  %s %s: old status %-16s strength_json %-7s -> derived %-16s %s' % (d['claim_id'], d['unit_id'], d['strength_status'], 'present' if d['strength_json'] else 'blank', pl.strength_status(w), how))
    print('  %d rows' % k)
    # the claim -> reference roles: stored judgments plus the derived coordinate-service role must give back the old table exactly
    meta = {m['reference_id']: m for m in br.read_meta()[1]}
    geo = {i for i, m in meta.items() if m['source_type'] == 'gazetteer_geocoder'}
    old_roles = subprocess.run(['git', '-C', common.ROOT, 'show', '%s:data/claim_reference_roles.csv' % ref], capture_output=True, text=True, check=True).stdout
    orr = {(x['claim_id'], x['reference_id'], x['role']) for x in csv.DictReader(io.StringIO(old_roles))}
    nrr = {(x['claim_id'], x['reference_id'], x['role']) for x in br.read_roles()[1]}
    for path, (h, rs) in new.items():
        for r in rs:
            d = dict(zip(h, r))
            for rid in br.parse_ids(d['reference_ids']):
                if rid in geo:
                    nrr.add((d['claim_id'], rid, 'location'))
    print('claim_reference_roles: %d old rows, %d stored now + derived = %d; %d old rows missing, %d new rows added' % (len(orr), len(br.read_roles()[1]), len(nrr), len(orr - nrr), len(nrr - orr)))
    for k in ['location_name', 'location_temporal_offset_days', 'strength_status', 'source', 'coordinates', 'strength_json (status key added)']:
        v = diffs.get(k, [])
        print('%-32s %d difference(s)' % (k, len(v)))
    others = [k for k in diffs if k.startswith('other:')]
    print('other columns                    %s' % ('none differ' if not others else others))
    return 0 if not others and not diffs.get('coordinates') and not diffs.get('location_temporal_offset_days') and not diffs.get('strength_status') else 1


if __name__ == '__main__':
    sys.exit(main())
