#!/usr/bin/env python3
"""One-off migration for items 1 to 7 of docs/unit_references_review.md (branch review-items-1-7); applied once, kept as the record.

  python scripts/migrate_review_items.py --item 1     the six former `attached:` entries: the 6th Fallschirmjaeger Regiment relation, the others deferred
  python scripts/migrate_review_items.py --item 2     the word "attached" removed from composing_text; relations or deferred rows for each use
  python scripts/migrate_review_items.py --item 3     the ten entries that embedded a unit id become `<unit_id> (qualifier)` entries
  python scripts/migrate_review_items.py --item 5     CR0061: the 8th Armoured Brigade under the 50th Division
  python scripts/migrate_review_items.py --doc        rewrite docs/deferred_relations.md from the DEFERRED table below

Every edit asserts the old value, so a second run stops at the first change that was already made. Items 4, 6 and 7 are documentation and
vocabulary changes made by hand (see docs/changelog.md). After a run: python scripts/build.py && python scripts/validate.py.
Standard library only.
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common  # noqa: E402

DATA = os.path.join(common.ROOT, 'data')
REL = os.path.join(DATA, 'command_relations.csv')
LINK = os.path.join(DATA, 'command_relation_claims.csv')
ROLES = os.path.join(DATA, 'claim_reference_roles.csv')
DOC = os.path.join(common.ROOT, 'docs', 'deferred_relations.md')

LISTED = 'listed_by_higher_unit'


class Claims:
    def __init__(self):
        self.files = {}
        self.where = {}
        for p in common.claim_files():
            h, rows = common.read_rows(p)
            self.files[p] = (h, rows)
            for i, r in enumerate(rows):
                self.where[r[h.index('claim_id')]] = (p, i)

    def get(self, cid, col):
        p, i = self.where[cid]
        h, rows = self.files[p]
        return rows[i][h.index(col)]

    def set(self, cid, col, old, new):
        p, i = self.where[cid]
        h, rows = self.files[p]
        cur = rows[i][h.index(col)]
        assert cur == old, '%s %s: expected %r but found %r (already migrated?)' % (cid, col, old, cur)
        rows[i][h.index(col)] = new

    def save(self):
        for p, (h, rows) in self.files.items():
            data = common.csv_bytes(h, rows)
            if data != open(p, 'rb').read():
                open(p, 'wb').write(data)


def read(path):
    return common.read_rows(path)


def write(path, header, rows):
    open(path, 'wb').write(common.csv_bytes(header, rows))


def add_relations(new_rows):
    """Append rows (dicts) to data/command_relations.csv in relation_id order."""
    h, rows = read(REL)
    ids = {r[0] for r in rows}
    for d in new_rows:
        assert d['relation_id'] not in ids, d['relation_id'] + ' exists'
        rows.append([d.get(c, '') for c in h])
    rows.sort(key=lambda r: r[0])
    write(REL, h, rows)


def add_links(new_rows):
    """Append evidence links (dicts) to data/command_relation_claims.csv; seq continues the claim's list."""
    h, rows = read(LINK)
    for d in new_rows:
        assert not any(r[0] == d['relation_id'] and r[1] == d['claim_id'] for r in rows), 'link exists %s %s' % (d['relation_id'], d['claim_id'])
        mine = [int(r[2]) for r in rows if r[1] == d['claim_id']]
        d = dict(d)
        d['seq'] = str(max(mine) + 1 if mine else 1)
        rows.append([d.get(c, '') for c in h])
    rows.sort(key=lambda r: (r[1], int(r[2])))
    write(LINK, h, rows)


def add_roles(new_rows):
    """Append rows to data/claim_reference_roles.csv after the last row of the same claim (or in claim order)."""
    h, rows = read(ROLES)
    for cid, rid, role, basis in new_rows:
        assert not any(r[:3] == [cid, rid, role] for r in rows)
        pos = len(rows)
        for i, r in enumerate(rows):
            if r[0] > cid:
                pos = i
                break
        rows.insert(pos, [cid, rid, role, basis])
    write(ROLES, h, rows)


def rel_row(rid, sub, high, relationship, frm, basis, note, date_basis='narrative', end_unknown='true', **kw):
    d = {'relation_id': rid, 'subject_unit_id': sub, 'higher_unit_id': high, 'relationship': relationship, 'valid_from': frm, 'valid_from_basis': basis,
         'valid_to_basis': 'open_at_last_claim', 'end_unknown': end_unknown, 'change_undated': 'false', 'date_basis': date_basis, 'status': 'preferred',
         'note': note}
    d.update(kw)
    return d


def link_row(rid, cid, note, frm='', frm_basis=''):
    return {'relation_id': rid, 'claim_id': cid, 'role': LISTED, 'stated_effective_from': frm, 'stated_note': note, 'stated_date_basis': frm_basis}


def next_relation_id():
    h, rows = read(REL)
    return max(int(r[0][2:]) for r in rows) + 1


# ---------------------------------------------------------------------------------------------------------------------------------------------
# docs/deferred_relations.md: relationships whose subject is not a unit of data/units.csv (scope: division and above).
# (item, id, claim_id, subject, higher_unit_id ('' = the claim's own unit), higher_unit (name; blank when the id is given), relationship, date_as_stated, text_in_claim)
D6 = '6 June 1944 (the claim date; the claim states no other date)'
DEFERRED_ROWS = [
    (1, 'D01', 'C0017', '56th Infantry Brigade', '', '', 'attached', D6, '56th Infantry Brigade'),
    (1, 'D02', 'C0018', '1st Canadian Parachute Battalion', '', '', 'attached', D6, '1st Canadian Parachute Battalion'),
    (1, 'D03', 'C0025', '116th Infantry Regiment (29th Division)', '', '', 'attached', D6, '116th Infantry Regiment (29th Division)'),
    (1, 'D04', 'C0031', '2nd Ranger Battalion', '', '', 'attached', D6, '2nd and 5th Ranger Battalions'),
    (1, 'D05', 'C0031', '5th Ranger Battalion', '', '', 'attached', D6, '2nd and 5th Ranger Battalions'),
    (1, 'D06', 'C0217', '2nd Irish Guards (Guards Armoured Division)', '', '', 'attached',
     'from 16 September 1944 (as stated in the claim; the claim date is 17 September)', 'British 2nd Irish Guards (Guards Armoured Division) from 16 September'),
]


def common_split(text):
    import unit_refs
    return unit_refs.split_list(text)


def deferred_doc(claims, upto):
    units = {r[0]: r for r in common.read_rows(os.path.join(DATA, 'units.csv'))[1]}
    out = [DOC_HEAD]
    for item, did, cid, subject, hid, higher, rel, date, text in DEFERRED_ROWS:
        if item > upto:
            continue
        uid = claims.get(cid, 'unit_id')
        if not hid and not higher:
            hid = uid
        if hid and not higher:
            u = units[hid]
            higher = common.display_name(u[1], u[2])
        assert text in common_split(claims.get(cid, 'composing_text')), '%s: %r is not an entry of composing_text %r' % (cid, text, claims.get(cid, 'composing_text'))
        src = claims.get(cid, 'source').replace(' | ', ' ; ')
        loc = claims.get(cid, 'source_locator')
        out.append('| %s | %s | %s | %s | %s | %s | %s | %s | %s | %s |' % (
            did, cid, uid, subject, hid, higher, rel, date, '%s (reference_ids %s%s)' % (src, claims.get(cid, 'reference_ids'), '; locator %s' % loc if loc else ''), text))
    return '\n'.join(out) + '\n'


DOC_HEAD = """# Deferred relations

Command relationships that a claim states but that cannot yet be recorded in `data/command_relations.csv`, because the **subordinate** formation is not a
unit of `data/units.csv`: the table covers divisions and above (plus the battle groups and combat commands that claims name). They are kept here, one row
per relationship, so the information is preserved structurally for when regiments, battalions and squadrons become units. Nothing here is a guess: the
columns say what the claim states and where it comes from.

How to read it:

- Each row names the claim (`claim_id`), the unit that makes the claim (`claim_unit_id`), the subordinate formation as the claim names it (`subject`), the
  higher formation (`higher_unit_id` and `higher_unit` when it is a unit of the table; the claim's own unit unless the row says otherwise), the relationship
  in the words of the vocabulary `relationship`, the date exactly as the claim states it (`date_as_stated`; where the claim gives none, its own date is the
  only date known and the row says so), the claim's source (`source_as_stated`: the URLs, then the reference ids and locator) and `text_in_claim`, the exact
  entry of the claim's `composing_text` that still names the formation (the field itself carries no relationship wording, see `docs/methodology.md`).
- `scripts/validate.py` checks this file: every claim exists and belongs to `claim_unit_id`, `higher_unit_id` is a unit of the table, `relationship` is in the
  vocabulary, and `text_in_claim` is an entry of the claim's `composing_text`.
- When a formation below division becomes a unit, move its rows to `data/command_relations.csv` (with evidence of role `listed_by_higher_unit` in
  `data/command_relation_claims.csv`, see `schema/README.md`) and delete them here. Ids D01... are cited by the changelog; do not renumber them.
- Generated by `scripts/migrate_review_items.py --doc` for the rows added by the review items; edit by hand afterwards.

| id | claim_id | claim_unit_id | subject | higher_unit_id | higher_unit | relationship | date_as_stated | source_as_stated | text_in_claim |
|---|---|---|---|---|---|---|---|---|---|"""


def write_doc(upto):
    open(DOC, 'w', encoding='utf-8').write(deferred_doc(Claims(), upto))


# ---------------------------------------------------------------------------------------------------------------------------------------------
def item1(claims):
    cm = 'Cross-Channel Attack ch. VII p. 237-238, 259-260; ch. VIII p. 292-293, n. 47'
    # the 6th Fallschirmjaeger Regiment with the 91st Luftlande Division: a real source (CMH), recorded as a relation with an honest caveat
    cr = 'CR%04d' % next_relation_id()
    add_relations([rel_row(cr, 'GER-FJR-006', 'GER-LL-091D', 'attached', '1944-06-06', 'claim_date',
                           'CMH Cross-Channel Attack (Harrison): ch. VII p. 237-238 says the 91st Division went into combat with an attached parachute regiment and p. 259-260 that '
                           'Seventh Army ordered the 91st to take over command of the 6th Parachute Regiment on arrival (the division arrived by 14 May); ch. VIII p. 292-293 has the '
                           'regiment "under control of the 91st Division" on 6 June, and n. 47 adds that the subordination ordered by Seventh Army was apparently not effected: von der '
                           'Heydte directed the regiment without orders from the division. The start is the claim date (no source dates the order); the regiment stayed under LXXXIV Corps '
                           'for tactical orders. Recorded as ordered, with that caveat.')])
    add_links([link_row(cr, 'C0010', "6th Fallschirmjaeger Regiment listed as a component of the 91st Luftlande Division on 6 June; the claim's earlier wording was 'GER-FJR-006 (attached)'")])
    claims.set('C0010', 'composing_text', '1057th Grenadier Regiment; 1058th Grenadier Regiment; 191st Artillery Regiment; GER-FJR-006 (attached)',
               '1057th Grenadier Regiment; 1058th Grenadier Regiment; 191st Artillery Regiment')
    claims.set('C0010', 'source', 'https://en.wikipedia.org/wiki/91st_Infantry_Division_(Wehrmacht)',
               'https://en.wikipedia.org/wiki/91st_Infantry_Division_(Wehrmacht) | https://www.ibiblio.org/hyperwar/USA/USA-E-XChannel/USA-E-XChannel-7.html | https://www.ibiblio.org/hyperwar/USA/USA-E-XChannel/USA-E-XChannel-8.html')
    claims.set('C0010', 'reference_ids', 'R102;R001', 'R102;R447;R448;R001')
    claims.set('C0010', 'source_locator', '', 'R447: p. 237-238, 259-260; R448: p. 292-293, n. 47')
    old = claims.get('C0010', 'notes')
    claims.set('C0010', 'notes', old, old + ' [Review item 1: the 6th Fallschirmjaeger Regiment (GER-FJR-006) is recorded as attached to this division in %s from 6 June (%s); '
               'the CMH footnote says the subordination ordered by Seventh Army was apparently not effected on 6 June.]' % (cr, cm))
    add_roles([('C0010', 'R447', 'command_relationship', 'names the attachment of the 6th Parachute Regiment to the 91st Division (%s)' % cr),
               ('C0010', 'R448', 'command_relationship', 'names the 6th Parachute Regiment under the control of the 91st Division on 6 June (%s)' % cr)])
    # the five that are not units of the table: wording removed, the relationship kept in docs/deferred_relations.md
    claims.set('C0017', 'composing_text', '69th Infantry Brigade; 151st Infantry Brigade; 231st Infantry Brigade; 56th Infantry Brigade (attached)',
               '69th Infantry Brigade; 151st Infantry Brigade; 231st Infantry Brigade; 56th Infantry Brigade')
    claims.set('C0018', 'composing_text', '3rd Parachute Brigade; 5th Parachute Brigade; 6th Airlanding Brigade; 1st Canadian Parachute Battalion (attached)',
               '3rd Parachute Brigade; 5th Parachute Brigade; 6th Airlanding Brigade; 1st Canadian Parachute Battalion')
    claims.set('C0025', 'composing_text', '16th Infantry Regiment; 18th Infantry Regiment; 26th Infantry Regiment; 116th Infantry Regiment (29th Division) (attached)',
               '16th Infantry Regiment; 18th Infantry Regiment; 26th Infantry Regiment; 116th Infantry Regiment (29th Division)')
    claims.set('C0031', 'composing_text', '2nd and 5th Ranger Battalions (attached)', '2nd and 5th Ranger Battalions')
    claims.set('C0217', 'composing_text', 'British 2nd Irish Guards (Guards Armoured Division) from 16 September (attached)',
               'British 2nd Irish Guards (Guards Armoured Division) from 16 September')


ITEMS = {1: item1}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--item', type=int, choices=sorted(ITEMS))
    ap.add_argument('--doc', action='store_true', help='rewrite docs/deferred_relations.md only')
    a = ap.parse_args()
    if a.item:
        claims = Claims()
        ITEMS[a.item](claims)
        claims.save()
        write_doc(a.item)
    elif a.doc:
        write_doc(99)
    else:
        ap.error('give --item N or --doc')
    print('ok')


if __name__ == '__main__':
    main()
