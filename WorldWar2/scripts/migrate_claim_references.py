#!/usr/bin/env python3
"""One-off migration: store the claim -> reference links on the claims.

NOTE (places-table): Historical, one-off: it was written for claim files that still had `location_name`, `strength_status`, `location_temporal_offset_days` and the `; coords:` tail of `source`; since `places-table` those are a place (data/places.csv, scripts/migrate_places.py) and derived values (scripts/places.py), so it cannot be run on the current layout.

NOTE: Historical, one-off: it read the `command_relationships` cell of the claim files; since `command-relations-table` that text is rebuilt from the relation tables by `common.load_all_claims()`, the claim files no longer have the column.

Before, build/claim_references.csv was DERIVED by matching the URLs of each claim's `source` column (and the coordinate note and the
strength_json source) to data/references_meta.csv. This script writes that match into the claim files, so the links are data:

  data/claims/**.csv                 new columns after `source`:
                                       reference_ids   ';'-separated reference_ids (R###), in citation order: source URLs, the coordinate service,
                                                       strength sources. The source of truth for which references support the claim.
                                       source_locator  'R398: p. 285, 289; R407: p. 36': page of a reference, taken only from a URL fragment
                                                       (#page285) of the old citation; blank where the citation gives none (nothing is guessed)
  data/claim_reference_roles.csv     claim_id, reference_id, role, basis: the role(s) of a link, inferred conservatively (see ROLE RULES);
                                     a link with no row has the role 'general'
  data/references_meta.csv           new column source_family (Wikipedia, any language, is one family; the US Army CMH and sites that
                                     republish it, one) used by the independent-source rubric

ROLE RULES (a role is recorded only where the claim's own text gives evidence)
  location              the reference is the coordinate service named by the coordinate note ('coords: Wikipedia ...'), or the reference is
                        named in the Location / Coordinates / Location caveat sentence of `notes`
  strength              the reference is a strength_json source
  event, date           named in the 'Event definition' / 'Event date' sentence of `notes`
  command_relationship  named in the 'Relationship' sentence of `notes`, or in the text of the command_relationships cell
  general               everything else (no row)
A reference is 'named' when the note contains its key: the HyperWar chapter code (Breakout-15), the Wikipedia article title, 'World War II by Day',
'Lexikon', or 'CMH assignment table'. Notes without those sentences give no role evidence and the link stays general.

Usage
  python scripts/migrate_claim_references.py [--dry-run] [--report FILE]
Idempotent: files that already have a reference_ids column are skipped.
"""
import argparse
import os
import re
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common  # noqa: E402
import build_references as br  # noqa: E402

SECTION_ROLE = {'Event date': 'date', 'Event definition': 'event', 'Location': 'location', 'Coordinates': 'location', 'Location caveat': 'location',
                'Location approximate': 'location', 'Relationship': 'command_relationship'}
LABEL_RE = re.compile(r'(?:(?<=^)|(?<=[.\]\)] ))(Event date|Event definition|Location caveat|Location approximate|Location support fallback|Location support|'
                      r'Event support|Command support|Coordinates|Coordinate check|Location|Relationship|Opponents|Objective check|Commander|Context|Later|Search):')


def sections(notes):
    """{label: text} of the labelled sentences of a notes cell (text up to the next label)."""
    marks = [(m.start(), m.end(), m.group(1)) for m in LABEL_RE.finditer(notes)]
    out = {}
    for i, (_s, e, lab) in enumerate(marks):
        end = marks[i + 1][0] if i + 1 < len(marks) else len(notes)
        out[lab] = out.get(lab, '') + ' ' + notes[e:end]
    return out


def keys_of(m):
    """Strings that name this reference in a note."""
    url, title = m['url'], m['short_title']
    ks = []
    mm = re.search(r'/hyperwar/USA/USA-[EA]-([A-Za-z]+-\d+)\.html?$', url)
    if mm:
        ks.append(mm.group(1))
    if title.startswith('Wikipedia: '):
        t = title[len('Wikipedia: '):]
        if len(t) >= 8:
            ks.append(t)
    if 'ww2byday.com' in url:
        ks.append('World War II by Day')
    if 'lexikon-wehrmacht.de' in url:
        ks.append('Lexikon')
    if 'web.archive.org' in url and 'ETO-OB' in url:
        ks.append('CMH assignment table')
    return ks


def infer_roles(row, links, meta_by_id):
    """[(reference_id, role, basis)] for one claim."""
    out = []
    secs = sections(row['notes'])
    for rid, kind, _frag in links:
        if kind == 'coordinates':
            out.append((rid, 'location', 'coordinate note names the service'))
        elif kind == 'strength':
            out.append((rid, 'strength', 'strength_json source'))
        else:
            ks = keys_of(meta_by_id[rid])
            for lab, role in SECTION_ROLE.items():
                if lab in secs and any(k in secs[lab] for k in ks):
                    out.append((rid, role, 'named in the %s sentence of notes' % lab))
            if any(k in row['command_relationships'] for k in ks):
                out.append((rid, 'command_relationship', 'named in command_relationships'))
    seen, res = set(), []
    for t in out:
        if (t[0], t[1]) not in seen:
            seen.add((t[0], t[1]))
            res.append(t)
    return res


def migrate_meta(dry):
    """Add source_family to references_meta.csv (idempotent). Returns the number of rows set."""
    header, meta = common.read_dicts(br.META_CSV)
    if 'source_family' in header:
        return 0
    for m in meta:
        m['source_family'] = br.default_family(m['url'])
    if not dry:
        br.write_meta(meta)
    return len(meta)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--dry-run', action='store_true')
    ap.add_argument('--report', help='write a short markdown summary here')
    a = ap.parse_args()
    set_family = migrate_meta(a.dry_run)
    _h, meta = common.read_dicts(br.META_CSV)
    for m in meta:   # a dry run before the column exists derives it in memory
        m.setdefault('source_family', br.default_family(m['url']))
    meta_by_id = {m['reference_id']: m for m in meta}
    new_cols = ['reference_ids', 'source_locator']
    out_files, role_rows = [], []
    n_claims = n_loc = 0
    nrefs = Counter()
    for p in common.claim_files():
        header, rows = common.read_rows(p)
        if 'reference_ids' in header:
            continue
        i = header.index('source')
        new_header = header[:i + 1] + new_cols + header[i + 1:]
        dicts = [dict(zip(header, r)) for r in rows]
        cl, missing = br.cited_links(dicts, meta)
        if missing:
            raise SystemExit('citations with no metadata row: %s' % missing)
        new_rows = []
        for r, d in zip(rows, dicts):
            links = cl[d['claim_id']]
            ids, locs = [], {}
            for rid, _k, frag in links:
                if rid not in ids:
                    ids.append(rid)
                lt = br.fragment_locator(frag)
                if lt:
                    pages = locs.setdefault(rid, [])
                    num = lt[3:]
                    if num not in pages:
                        pages.append(num)
            if not ids:
                raise SystemExit('%s has no resolvable citation' % d['claim_id'])
            loc = '; '.join('%s: p. %s' % (rid, ', '.join(locs[rid])) for rid in ids if rid in locs)
            n_claims += 1
            nrefs[len(ids)] += 1
            n_loc += bool(loc)
            for rid, role, basis in infer_roles(d, links, meta_by_id):
                role_rows.append([d['claim_id'], rid, role, basis])
            new_rows.append(r[:i + 1] + [';'.join(ids), loc] + r[i + 1:])
        out_files.append((p, common.csv_bytes(new_header, new_rows)))
    role_rows.sort(key=lambda x: (x[0], x[1], br.ROLES.index(x[2])))
    rc = Counter(r[2] for r in role_rows)
    print('claims %d, %d with a locator, source_family set on %d references; links per claim %s; role rows %d %s'
          % (n_claims, n_loc, set_family, dict(sorted(nrefs.items())), len(role_rows), dict(rc)))
    if a.dry_run:
        return 0
    for p, data in out_files:
        with open(p, 'wb') as f:
            f.write(data)
    if role_rows or not os.path.isfile(br.ROLES_CSV):
        with open(br.ROLES_CSV, 'wb') as f:
            f.write(common.csv_bytes(br.ROLE_HEADER, role_rows))
    print('rewrote %d claim files%s' % (len(out_files), ' and data/claim_reference_roles.csv (%d rows)' % len(role_rows) if role_rows else ' (nothing to do: already migrated)'))
    return 0


if __name__ == '__main__':
    sys.exit(main())
