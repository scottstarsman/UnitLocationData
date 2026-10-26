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
    (2, 'D07', 'C0506', 'Combat Command B, 3rd Armored Division', '', '', 'attached', '26 July 1944 (the claim date; the claim notes say "for Cobra")',
     'Combat Command B, 3rd Armored Division'),
    (2, 'D08', 'C0507', '22nd Infantry Regiment, 4th Infantry Division', '', '', 'attached',
     '26 July 1944 (the claim date; the claim notes say the 22nd and Combat Command A passed to XIX Corps by 28 July, Breakout-16 p304)', '22nd Infantry Regiment, 4th Infantry Division'),
    (2, 'D09', 'C0493', '22nd Infantry Regiment (4th Infantry Division)', 'US-CCA-002D', '', 'attached', 'temporary, from noon 28 July 1944 (as stated in the claim)',
     'US-CCA-002D (reinforced by the 22nd Infantry; temporary, from noon 28 July)'),
    (2, 'D10', 'C0164', 'C Squadron, 2nd County of London Yeomanry', '', '', 'attached', '26 June 1944 (the claim date; the claim names Operation Epsom)',
     '(C Sqn 2nd County of London Yeomanry)'),
    (2, 'D11', 'C0211', '2nd Battalion, 915th Grenadier Regiment', '', '916th Grenadier Regiment (352nd Infantry Division; not a unit of the table)', 'attached',
     'at midday on 6 June 1944 (as stated in the claim)', 'its 2nd Bn was split off at midday and went to the 916th Regiment'),
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


def item2(claims):
    """The word "attached" out of composing_text: a relation where the subject is a unit of the table, a deferred row where it is not."""
    nid = next_relation_id()
    rels, links, roles = [], [], []
    # 30th Infantry Division with XIX Corps on 13 June (CMH Cross-Channel Attack ch. IX): the corps became operational with the division attached
    cr30 = 'CR%04d' % nid
    rels.append(rel_row(cr30, 'US-INF-030D', 'US-COR-019C', 'attached', '1944-06-13', 'narrative',
                        'CMH Cross-Channel Attack ch. IX p. 376-377: XIX Corps became operational with the 30th Division attached (the claim date, 13 June). '
                        'No source dates the end: the interval is closed the day before the division\'s next claim (15 June, assigned to the corps, CR0262).',
                        valid_to='1944-06-14', valid_to_earliest='1944-06-13', valid_to_basis='inferred_from_next_claim'))
    links.append(link_row(cr30, 'C0105', "30th Infantry Division listed as a component of XIX Corps; the claim's earlier wording was 'US-INF-030D (attached)'",
                          '1944-06-13', 'narrative'))
    nid += 1
    # Kampfgruppe Heintz with the 17th SS Panzergrenadier Division (CMH ch. IX)
    crh = 'CR%04d' % nid
    rels.append(rel_row(crh, 'GER-KG-HEINTZ', 'GER-SSPG-017D', 'attached', '1944-06-13', 'claim_date',
                        'CMH Cross-Channel Attack ch. IX p. 378-379: after a road march of three to five days (the troops were unloaded on 9 June) Kampfgruppe Heintz, the mobile group of the 275th Division, '
                        'was attached to the 17th SS Panzer Grenadier Division and put into the line southeast of Carentan; n. 78 adds that it was attached to the 352nd Division for supply. '
                        'The source gives no day, so the start is the date of the claim that lists it.'))
    links.append(link_row(crh, 'C0089', "Kampfgruppe Heintz listed as a component of the 17th SS Panzergrenadier Division 'after its arrival (CMH ch. IX)'; the claim's earlier wording was "
                          "'attached battle group from the 275th Division: Kampfgruppe Heintz (GER-KG-HEINTZ)'"))
    # relations that already exist: the claim of the higher unit is added as evidence (what it said, and the dates it gave)
    links += [
        link_row('CR0100', 'C0120', "101st Airborne Division listed as a component of VIII Corps; the claim's earlier wording was 'US-ABN-101D (attached)'"),
        link_row('CR0277', 'C0490', "35th Infantry Division listed as a component of V Corps; the claim's earlier wording was 'US-INF-035D (attached)'", '1944-07-28', 'narrative'),
        link_row('CR0032', 'C0161', "Kampfgruppe Weidinger listed as a component of II SS Panzer Corps; the claim's earlier wording was '(2nd SS Kampfgruppe Weidinger attached 29 June)'",
                 '1944-06-29', 'narrative'),
        link_row('CR0177', 'C0493', "Combat Command A listed as a component of XIX Corps with the 22nd Infantry reinforcing it; the claim's earlier wording was "
                 "'Combat Command A, 2nd Armored Division, with the 22nd Infantry attached (temporary, from noon 28 July)'", '1944-07-28', 'narrative'),
        link_row('CR0020', 'C0127', "Kampfgruppe Boehm listed as a component of the 352nd Infantry Division; the claim's earlier wording was "
                 "'attached battle group from the 353rd Division: Kampfgruppe Boehm (GER-KG-BOEHM; from evening 16 June)'", '1944-06-16', 'narrative'),
        link_row('CR0023', 'C0170', "Kampfgruppe Frey listed as a component of the 12th SS Panzer Division; the claim's earlier wording was "
                 "'attached battle group from the 1st SS Division: Kampfgruppe Frey (GER-KG-FREY; from 28 June)'", '1944-06-28', 'narrative'),
        link_row('CR0030', 'C0173', "Kampfgruppe Weidinger listed as a component of Panzer Lehr; the claim's earlier wording was "
                 "'attached battle group from the 2nd SS Division: Kampfgruppe Weidinger (GER-KG-WEIDINGER; 27-28 June)'", '1944-06-27', 'narrative'),
    ]
    add_relations(rels)
    add_links(links)
    # references for the two new relations (R449 = CMH ch. IX)
    claims.set('C0105', 'source_locator', '', 'R449: p. 376-377')
    roles.append(('C0105', 'R449', 'command_relationship', 'names the 30th Division attached to XIX Corps from 13 June (%s)' % cr30))
    claims.set('C0089', 'source', 'https://en.wikipedia.org/wiki/Battle_of_Bloody_Gulch | https://en.wikipedia.org/wiki/Battle_of_Carentan',
               'https://en.wikipedia.org/wiki/Battle_of_Bloody_Gulch | https://en.wikipedia.org/wiki/Battle_of_Carentan | https://www.ibiblio.org/hyperwar/USA/USA-E-XChannel/USA-E-XChannel-9.html')
    claims.set('C0089', 'reference_ids', 'R109;R111;R001', 'R109;R111;R449;R001')
    claims.set('C0089', 'source_locator', '', 'R449: p. 378-379')
    roles.append(('C0089', 'R449', 'command_relationship', 'names Kampfgruppe Heintz attached to the 17th SS Panzer Grenadier Division (%s)' % crh))
    add_roles(roles)
    old = claims.get('C0105', 'notes')
    claims.set('C0105', 'notes', old, old + ' [Review item 2: the attachment of the 30th Division to XIX Corps from 13 June is relation %s (CMH ch. IX p. 376-377).]' % cr30)
    old = claims.get('C0089', 'notes')
    claims.set('C0089', 'notes', old, old + ' [Review item 2: the attachment of Kampfgruppe Heintz to this division is relation %s (CMH ch. IX p. 378-379).]' % crh)

    # composing_text: the word removed (the relationship now lives in a relation, or in docs/deferred_relations.md)
    claims.set('C0105', 'composing_text', 'US-INF-030D (attached); US-INF-029D (from 14 June)', 'US-INF-029D (from 14 June)')
    claims.set('C0120', 'composing_text', 'US-ABN-101D (attached); US-ABN-082D (from 17\u201319 June)', 'US-ABN-082D (from 17\u201319 June)')
    claims.set('C0490', 'composing_text', 'US-INF-035D (attached)', '')
    claims.set('C0037', 'composing_text', 'GER-INF-716D (remnant); GER-PZ-LEHRD (attached, planned)', 'GER-INF-716D (remnant); GER-PZ-LEHRD (planned)')
    claims.set('C0030', 'composing_text', 'US-COR-007C (82nd and 101st Airborne attached to VII Corps)', 'US-COR-007C (with the 82nd and 101st Airborne Divisions)')
    claims.set('C0506', 'composing_text', 'Combat Command B, 3rd Armored Division (attached)', 'Combat Command B, 3rd Armored Division')
    claims.set('C0507', 'composing_text', '22nd Infantry Regiment, 4th Infantry Division (attached)', '22nd Infantry Regiment, 4th Infantry Division')
    claims.set('C0094', 'composing_units', '', 'UK-ARM-004B')
    claims.set('C0094', 'composing_text', '29th Armoured Brigade; 159th Infantry Brigade; (4th Armoured Brigade attached for Epsom)',
               '29th Armoured Brigade; 159th Infantry Brigade; UK-ARM-004B (for Operation Epsom)')
    claims.set('C0164', 'composing_text', '7th Royal Tank Regiment; 9th Royal Tank Regiment; (C Sqn 2nd County of London Yeomanry attached)',
               '7th Royal Tank Regiment; 9th Royal Tank Regiment; (C Sqn 2nd County of London Yeomanry)')
    claims.set('C0161', 'composing_units', 'GER-SSPZ-009D; GER-SSPZ-010D', 'GER-SSPZ-009D; GER-SSPZ-010D; GER-KG-WEIDINGER')
    claims.set('C0161', 'composing_text', '(2nd SS Kampfgruppe Weidinger attached 29 June)', 'GER-KG-WEIDINGER (2nd SS; from 29 June)')
    claims.set('C0493', 'composing_units', 'US-INF-030D', 'US-INF-030D; US-CCA-002D')
    claims.set('C0493', 'composing_text',
               'US-INF-030D (from noon 28 July); Combat Command A, 2nd Armored Division, with the 22nd Infantry attached (temporary, from noon 28 July); 113th Cavalry Group (from noon 28 July); 29th and 28th Infantry Divisions (displacing into the zone, control not dated)',
               'US-INF-030D (from noon 28 July); US-CCA-002D (reinforced by the 22nd Infantry; temporary, from noon 28 July); 113th Cavalry Group (from noon 28 July); 29th and 28th Infantry Divisions (displacing into the zone, control not dated)')
    claims.set('C0211', 'composing_text', 'reinforced 915th Grenadier Regiment (352nd Division); its 2nd Bn was split off at midday and attached to the 916th Regiment',
               'reinforced 915th Grenadier Regiment (352nd Division); its 2nd Bn was split off at midday and went to the 916th Regiment')
    # the five that also embed a unit id (item 3 turns them into id entries): only the word goes now
    claims.set('C0089', 'composing_text', 'SS-Panzergrenadier Regiment 37; SS-Panzergrenadier Regiment 38; attached battle group from the 275th Division: Kampfgruppe Heintz (GER-KG-HEINTZ) after its arrival (CMH ch. IX)',
               'SS-Panzergrenadier Regiment 37; SS-Panzergrenadier Regiment 38; battle group from the 275th Division: Kampfgruppe Heintz (GER-KG-HEINTZ) after its arrival (CMH ch. IX)')
    claims.set('C0100', 'composing_text', 'Combat Command B; 41st Armored Infantry Regiment; 66th Armored Regiment; 67th Armored Regiment; Combat Command A (US-CCA-002D) attached to the 101st Airborne Division at Carentan on 13 June',
               'Combat Command B; 41st Armored Infantry Regiment; 66th Armored Regiment; 67th Armored Regiment; Combat Command A (US-CCA-002D) with the 101st Airborne Division at Carentan on 13 June')
    claims.set('C0127', 'composing_text', '914th Grenadier Regiment; 915th Grenadier Regiment; 916th Grenadier Regiment; 352nd Artillery Regiment; battle group formed from this division: Kampfgruppe Meyer (GER-KG-MEYER; reinforced 915th Regiment, 6 June); attached battle group from the 353rd Division: Kampfgruppe Boehm (GER-KG-BOEHM; from evening 16 June)',
               '914th Grenadier Regiment; 915th Grenadier Regiment; 916th Grenadier Regiment; 352nd Artillery Regiment; battle group formed from this division: Kampfgruppe Meyer (GER-KG-MEYER; reinforced 915th Regiment, 6 June); battle group from the 353rd Division: Kampfgruppe Boehm (GER-KG-BOEHM; from evening 16 June)')
    claims.set('C0170', 'composing_text', 'SS-Panzer Regiment 12; SS-Panzergrenadier Regiment 25; SS-Panzergrenadier Regiment 26; SS-Panzer Artillery Regiment 12; SS-Reconnaissance Battalion 12; attached battle group from the 1st SS Division: Kampfgruppe Frey (GER-KG-FREY; from 28 June)',
               'SS-Panzer Regiment 12; SS-Panzergrenadier Regiment 25; SS-Panzergrenadier Regiment 26; SS-Panzer Artillery Regiment 12; SS-Reconnaissance Battalion 12; battle group from the 1st SS Division: Kampfgruppe Frey (GER-KG-FREY; from 28 June)')
    claims.set('C0173', 'composing_text', 'Panzergrenadier Regiment 901; Panzergrenadier Regiment 902; Panzer Regiment 130; attached battle group from the 2nd SS Division: Kampfgruppe Weidinger (GER-KG-WEIDINGER; 27-28 June)',
               'Panzergrenadier Regiment 901; Panzergrenadier Regiment 902; Panzer Regiment 130; battle group from the 2nd SS Division: Kampfgruppe Weidinger (GER-KG-WEIDINGER; 27-28 June)')


def item3(claims):
    """The ten embedded unit ids of composing_text become `<unit_id> (qualifier)` entries, with the id in composing_units."""
    def conv(cid, old_text, new_text, old_units, new_units):
        claims.set(cid, 'composing_text', old_text, new_text)
        if old_units != new_units:
            claims.set(cid, 'composing_units', old_units, new_units)
    cur = lambda cid: claims.get(cid, 'composing_text')
    def swap(cid, old_entry, new_entry, unit_id, old_units):
        t = cur(cid)
        assert old_entry in t.split('; ') or old_entry in t, (cid, old_entry)
        new_units = (old_units + '; ' + unit_id) if old_units and unit_id not in old_units else (old_units or unit_id)
        conv(cid, t, t.replace(old_entry, new_entry, 1), old_units, new_units)
        return new_units
    swap('C0006', 'battle group formed from this division: Kampfgruppe Meyer (GER-KG-MEYER; reinforced 915th Regiment, 6 June)',
         'GER-KG-MEYER (battle group formed from this division; reinforced 915th Regiment, 6 June)', 'GER-KG-MEYER', '')
    swap('C0089', 'battle group from the 275th Division: Kampfgruppe Heintz (GER-KG-HEINTZ) after its arrival (CMH ch. IX)',
         'GER-KG-HEINTZ (battle group from the 275th Division; after its arrival, CMH ch. IX)', 'GER-KG-HEINTZ', '')
    swap('C0100', 'Combat Command A (US-CCA-002D) with the 101st Airborne Division at Carentan on 13 June',
         'US-CCA-002D (Combat Command A, with the 101st Airborne Division at Carentan on 13 June)', 'US-CCA-002D', 'US-CCA-002D')
    swap('C0126', '922nd Grenadier Regiment went into Kampfgruppe Rohrbach (GER-KG-ROHRBACH) on 7 June',
         'GER-KG-ROHRBACH (the 922nd Grenadier Regiment went into it on 7 June)', 'GER-KG-ROHRBACH', '')
    u = swap('C0127', 'battle group formed from this division: Kampfgruppe Meyer (GER-KG-MEYER; reinforced 915th Regiment, 6 June)',
             'GER-KG-MEYER (battle group formed from this division; reinforced 915th Regiment, 6 June)', 'GER-KG-MEYER', '')
    swap('C0127', 'battle group from the 353rd Division: Kampfgruppe Boehm (GER-KG-BOEHM; from evening 16 June)',
         'GER-KG-BOEHM (battle group from the 353rd Division; from evening 16 June)', 'GER-KG-BOEHM', u)
    swap('C0145', 'battle group formed in this division\'s sector: Kampfgruppe Rohrbach (GER-KG-ROHRBACH; 7 June)',
         'GER-KG-ROHRBACH (battle group formed in this division\'s sector; 7 June)', 'GER-KG-ROHRBACH', '')
    swap('C0170', 'battle group from the 1st SS Division: Kampfgruppe Frey (GER-KG-FREY; from 28 June)',
         'GER-KG-FREY (battle group from the 1st SS Division; from 28 June)', 'GER-KG-FREY', '')
    swap('C0173', 'battle group from the 2nd SS Division: Kampfgruppe Weidinger (GER-KG-WEIDINGER; 27-28 June)',
         'GER-KG-WEIDINGER (battle group from the 2nd SS Division; 27-28 June)', 'GER-KG-WEIDINGER', '')
    swap('C0184', 'battle group formed from this division: Kampfgruppe von Luck (GER-KG-VONLUCK; 23 June)',
         'GER-KG-VONLUCK (battle group formed from this division; 23 June)', 'GER-KG-VONLUCK', '')


ITEMS = {1: item1, 2: item2, 3: item3}


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
