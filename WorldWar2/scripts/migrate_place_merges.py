#!/usr/bin/env python3
"""One-off migration for item 8 of docs/unit_references_review.md: the five place merges (branch place-merges); applied once, kept as the record.

  python scripts/migrate_place_merges.py --merge 1    PL0070 Caumont -> PL0071 Caumont-l'Eventé
  python scripts/migrate_place_merges.py --merge 2    PL0208 Mantes-Gassicourt, Yvelines -> PL0209 Mantes-la-Jolie, Yvelines
  python scripts/migrate_place_merges.py --merge 3    PL0294 Recouvrance, Brest -> PL0045 Brest, Finistère
  python scripts/migrate_place_merges.py --merge 4    PL0259 Omaha Beach sector -> PL0258 Omaha Beach
  python scripts/migrate_place_merges.py --merge 5    PL0174 Hill 112 / Odon salient -> PL0173 Hill 112

A merge keeps the survivor's id, point, precision and coordinate reference; every claim at the retired place moves to the survivor and keeps its
own precision_km, coord_override and point; what made the retired place separate goes to the claim's location_qualifier (or, for a name of the
time, to the survivor's alt_names). The retired id leaves data/places.csv and is recorded in data/place_merges.csv (never reused). The text in
docs/places_review.md follows. Every edit asserts the old value, so a second run stops at the first change that was already made.
After a run: python scripts/build.py && python scripts/validate.py. Standard library only.
"""
import argparse
import collections
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common  # noqa: E402
import places as placesmod  # noqa: E402

REVIEW = os.path.join(common.ROOT, 'docs', 'places_review.md')

# retired id, survivor id, alias added to the survivor (or None), {claim_id: (old qualifier, new qualifier)} for the claims that move,
# the note of data/place_merges.csv, the paragraph for places_review.md section 7, the table row prefix of section 2, the close-pair prefix of section 4
MERGES = {
    1: dict(retired='PL0070', survivor='PL0071', alias='Caumont',
            quals={'C0104': ('left of First Army line', 'left of First Army line')},
            note="The same commune: both rows use the point of the English Wikipedia article Caumont-l'Éventé (https://en.wikipedia.org/wiki/Caumont-l%27%C3%89vent%C3%A9, 49.0911 N 0.8039 W). 'Caumont' is the short name the V Corps claim used.",
            text="**PL0070 Caumont -> PL0071 Caumont-l'Éventé.** The same commune (Caumont-l'Éventé, Calvados): both places used the point of the Wikipedia article Caumont-l'Éventé, 0 m apart. `Caumont` is now an alias of PL0071. One claim moved (C0104, V Corps, 13 June 1944); it keeps its qualifier `left of First Army line` and its own `precision_km` 10.",
            row="| PL0070 Caumont / PL0071", pair='- PL0070 Caumont and PL0071'),
    2: dict(retired='PL0208', survivor='PL0209', alias='Mantes-Gassicourt',
            quals={'C0330': ('', 'Mantes-Gassicourt, Seine crossing'), 'C0451': ('', 'Mantes-Gassicourt, Seine crossing')},
            note="Gassicourt is a district of Mantes-la-Jolie: the former village of Gassicourt, west of the old centre, was annexed to Mantes in 1930, the merged commune was called Mantes-Gassicourt until it was renamed Mantes-la-Jolie on 7 May 1953, and Gassicourt is one of the four districts of the city today (https://en.wikipedia.org/wiki/Mantes-la-Jolie; https://fr.wikipedia.org/wiki/Mantes-la-Jolie). A Nominatim read of the district centre lies 1.85 km west of the shared point, inside the commune; the 1944 claims name the whole town (Mantes-Gassicourt was its name then).",
            text="**PL0208 Mantes-Gassicourt, Yvelines -> PL0209 Mantes-la-Jolie, Yvelines.** Checked first: Gassicourt is a district of Mantes-la-Jolie, not a separate commune. The English Wikipedia article Mantes-la-Jolie says the commune absorbed Gassicourt in 1930 (the merged commune was called Mantes-Gassicourt until it was renamed Mantes-la-Jolie on 7 May 1953) and lists Gassicourt among the four districts of the city; the French article describes Gassicourt as the former village west of the historic centre, annexed in 1930, now a residential district. A Nominatim read of the district (https://nominatim.openstreetmap.org/search?q=Gassicourt,+Mantes-la-Jolie) lies 1.85 km west of the shared point, inside the commune, under the 2 km limit set for this merge. In 1944 `Mantes-Gassicourt` was the name of the whole town, so it is kept as an alias of PL0209. Two claims moved (C0330 XV Corps and C0451 79th Infantry Division, both 19 August 1944: the 79th Division started across the Seine near Mantes that evening); they keep their precision (10 and 5 km) and get the qualifier `Mantes-Gassicourt, Seine crossing`. PL0207 (the bridgehead area on the same point) is a different kind of place and stays.",
            row="| PL0208 Mantes-Gassicourt / PL0209", pair='- PL0208 Mantes-Gassicourt and PL0209'),
    3: dict(retired='PL0294', survivor='PL0045', alias='Recouvrance',
            quals={'C0408': ('', 'Recouvrance district')},
            note="Recouvrance is a historic district (quartier) of Brest on the Penfeld, with the arsenal (https://fr.wikipedia.org/wiki/Recouvrance_(Brest)); both rows used the Wikipedia point of Brest, France. A Nominatim read of the district lies 1.2 km from that point.",
            text="**PL0294 Recouvrance, Brest -> PL0045 Brest, Finistère.** Recouvrance is a historic district of Brest on the Penfeld (https://fr.wikipedia.org/wiki/Recouvrance_(Brest)); both places used the Wikipedia point of Brest, 0 m apart (a Nominatim read of the district is 1.2 km away). `Recouvrance` is now an alias of PL0045. One claim moved (C0408, 29th Infantry Division, 18 September 1944: Von der Mosel surrendered the troops in Recouvrance); it gets the qualifier `Recouvrance district` and keeps its `precision_km` 3.",
            row="| PL0045 Brest, Finistère / PL0294", pair='- PL0045 Brest and PL0294'),
    4: dict(retired='PL0259', survivor='PL0258', alias=None,
            quals={'C0006': ('division HQ Le Molay-Littry', 'division HQ Le Molay-Littry')},
            note="The beach and its sector were the same area on one point (both areas, 49.3689 N 0.8686 W, reference R001); the retired place held one claim.",
            text="**PL0259 Omaha Beach sector -> PL0258 Omaha Beach.** The beach and its sector were two areas on the same point (reference R001). One claim moved (C0006, 352nd Infantry Division, 6 June 1944); it keeps its qualifier `division HQ Le Molay-Littry` and its `precision_km` 10. No alias was added (the sector name is kept as `retired_name` in `data/place_merges.csv`). **Open: C0006.** Its notes say the division defended Omaha Beach with its headquarters at Le Molay-Littry, which is inland; the claim sits on the beach point (represents `sector_center`). The headquarters may deserve its own place and point later; the coordinates were not changed.",
            row="| PL0258 Omaha Beach / PL0259", pair=None),
    5: dict(retired='PL0174', survivor='PL0173', alias=None,
            quals={'C0196': ('', 'Odon salient')},
            note="Same point (49.1236 N 0.4605 W, reference R002); the retired place was the wider Odon salient (kind area) around the hill and held one claim. The survivor is the point Hill 112.",
            text="**PL0174 Hill 112 / Odon salient -> PL0173 Hill 112.** Same point (reference R002). The survivor is the point Hill 112; the salient (the retired area) becomes context on the claim. One claim moved (C0196, 10th SS Panzer Division, 29 June 1944: the counter-attack on the west flank of the British salient); it gets the qualifier `Odon salient` and keeps its `precision_km` 5. C0189 already had the qualifier `Odon salient`. No alias was added (the retired name is kept in `data/place_merges.csv`).",
            row="| PL0173 Hill 112 / PL0174", pair=None),
}
SECTION7 = '## 7. Place merges made (item 8, branch `place-merges`)'
SECTION7_INTRO = ("Item 8 of `docs/unit_references_review.md`: the five likely merge candidates of section 2 were decided and merged, one commit each, with "
                  "`scripts/migrate_place_merges.py`. The survivor keeps its id and point; the retired id is listed in `data/place_merges.csv` and never reused; every moved claim "
                  "keeps its own `precision_km`, `coord_override` and point, so no position in `build/claims.geojson` changed; the derived `location_name` of the moved claims changed "
                  "(the survivor's name plus the qualifier). The `coord_reference_id` of each pair was the same, so nothing changed there. The other co-located places of section 2 "
                  "are unchanged: where a group lost a place it is shown in its new form, the other groups are as before.\n")


def read_places():
    return common.read_rows(placesmod.PLACES_CSV)


def claim_counts():
    c = collections.Counter()
    for p in common.claim_files():
        h, rows = common.read_rows(p)
        for r in rows:
            c[r[h.index('place_id')]] += 1
    return c


def sub1(text, old, new):
    assert text.count(old) == 1, 'expected exactly one %r' % old[:60]
    return text.replace(old, new, 1)


def merge(n):
    m = MERGES[n]
    ret, sur = m['retired'], m['survivor']
    # ---- claims
    files = {}
    moved = []
    for p in common.claim_files():
        h, rows = common.read_rows(p)
        ip, iq = h.index('place_id'), h.index('location_qualifier')
        changed = False
        for r in rows:
            if r[ip] == ret:
                cid = r[h.index('claim_id')]
                assert cid in m['quals'], 'claim %s at %s is not in the plan' % (cid, ret)
                old, new = m['quals'][cid]
                assert r[iq] == old, '%s location_qualifier: expected %r, found %r' % (cid, old, r[iq])
                r[ip], r[iq] = sur, new
                moved.append(cid)
                changed = True
        if changed:
            files[p] = (h, rows)
    assert sorted(moved) == sorted(m['quals']), (moved, m['quals'])
    for p, (h, rows) in files.items():
        open(p, 'wb').write(common.csv_bytes(h, rows))
    # ---- places
    h, rows = read_places()
    ids = [r[0] for r in rows]
    assert ret in ids and sur in ids
    row = {r[0]: r for r in rows}
    rname = row[ret][h.index('name')]
    assert row[ret][h.index('coord_reference_id')] == row[sur][h.index('coord_reference_id')]
    assert (row[ret][h.index('latitude')], row[ret][h.index('longitude')]) == (row[sur][h.index('latitude')], row[sur][h.index('longitude')])
    if m['alias']:
        ia = h.index('alt_names')
        alts = [a.strip() for a in row[sur][ia].split(';') if a.strip()]
        assert m['alias'] not in alts
        row[sur][ia] = '; '.join(alts + [m['alias']])
    rows = [r for r in rows if r[0] != ret]
    open(placesmod.PLACES_CSV, 'wb').write(common.csv_bytes(h, rows))
    # ---- place_merges
    mh, mrows = common.read_rows(placesmod.MERGES_CSV)
    assert ret not in {r[0] for r in mrows}
    mrows.append([ret, sur, rname, m['note']])
    mrows.sort(key=lambda r: r[0])
    open(placesmod.MERGES_CSV, 'wb').write(common.csv_bytes(mh, mrows))
    review(n, m, h, rows)
    print('merge %d: %s %r -> %s; claims moved: %s' % (n, ret, rname, sur, ', '.join(sorted(moved))))


def review(n, m, h, rows):
    """docs/places_review.md: section 7 paragraph, the table row of section 2, the group lines, the counts, the close-pair line."""
    t = open(REVIEW, encoding='utf-8').read()
    ret = m['retired']
    # section 2 table row
    lines = t.split('\n')
    i = [k for k, l in enumerate(lines) if l.startswith(m['row'])]
    assert len(i) == 1, m['row']
    cells = lines[i[0]].split(' | ')
    lines[i[0]] = '%s | **Merged** into %s (see section 7); %s |' % (cells[0], m['survivor'], cells[1].rstrip(' |').rstrip())
    # close pairs
    if m['pair']:
        k = [k for k, l in enumerate(lines) if l.startswith(m['pair'])]
        assert len(k) == 1 and lines[k[0]].endswith('(merge candidate)'), m['pair']
        lines[k[0]] = lines[k[0]].replace('(merge candidate)', '(merged, see section 7)')
    # group lines
    byid = {r[0]: dict(zip(h, r)) for r in rows}
    cnt = claim_counts()
    for k, l in enumerate(lines):
        if l.startswith('(') and ' PL' in l and ret in l:
            prefix, rest = l.split(') ', 1)
            keep = [x for x in re.findall(r'PL\d{4}', rest) if x != ret]
            if len(keep) < 2:
                lines[k] = None
            else:
                lines[k] = prefix + ') ' + ' | '.join('%s %s "%s" (%d)' % (x, byid[x]['kind'], byid[x]['name'], cnt[x]) for x in keep)
    lines = [l for l in lines if l is not None]
    t = '\n'.join(lines)
    # section 2 lead-in and counts, from the data
    groups = [l for l in t.split('\n') if l.startswith('(') and ' PL' in l]
    gplaces = sum(len(re.findall(r'PL\d{4}', l)) for l in groups)
    t = re.sub(r'\d+ groups, \d+ places; the full list follows\. Likely merge candidates, which Scott should decide \(still open after the `unit-ids-in-text-columns` work, which did not touch places; none of the five has been ruled on\):',
               '%d groups, %d places after the merges of section 7; the full list follows. The five likely merge candidates were decided (item 8); the table shows what was done to each:' % (len(groups), gplaces), t) \
        if 'Likely merge candidates' in t else re.sub(r'\d+ groups, \d+ places after the merges', '%d groups, %d places after the merges' % (len(groups), gplaces), t)
    kinds = collections.Counter(r[h.index('kind')] for r in rows)
    bullet = '- After the place merges of item 8 (section 7): %d places (%d point, %d area, %d line); %d places have been retired in `data/place_merges.csv`.' % (
        len(rows), kinds['point'], kinds['area'], kinds['line'], len(common.read_rows(placesmod.MERGES_CSV)[1]))
    if '- After the place merges of item 8' in t:
        t = re.sub(r'- After the place merges of item 8[^\n]*', lambda _: bullet, t)
    else:
        i = t.index('- 566 claims:')
        j = t.index('\n', i) + 1
        t = t[:j] + bullet + '\n' + t[j:]
    # section 7
    if SECTION7 not in t:
        t = t.rstrip('\n') + '\n\n' + SECTION7 + '\n\n' + SECTION7_INTRO + '\n'
    t = t.rstrip('\n') + '\n\n- ' + m['text'] + '\n'
    open(REVIEW, 'w', encoding='utf-8').write(t)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--merge', type=int, choices=sorted(MERGES), required=True)
    merge(ap.parse_args().merge)


if __name__ == '__main__':
    main()
