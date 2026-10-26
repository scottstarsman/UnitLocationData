#!/usr/bin/env python3
"""One-time migration: unit ids in the text columns engaged_with and composing_units (recommendation F3). Standard library only.

What it does (from the claims as they were at the commit it is run on; see docs/changelog.md and docs/unit_references_review.md):
  engaged_with     60 opponent strings -> `;` list of unit_ids. Spellings that are not the display name of a unit ('Canadian 3rd Infantry Division') are
                   resolved by the ALIAS_ENGAGED table; a named unit that is not in data/units.csv becomes a placeholder unit (PLACEHOLDERS); a generic
                   opponent (an air force, naval forces, an unnamed formation) moves to the new column engaged_note, verbatim. `unknown` stays.
  composing_units  every entry that is exactly the name of a unit of data/units.csv (optionally with a trailing parenthesis, kept as the qualifier
                   `<unit_id> (<qualifier>)` in the new column composing_text) -> unit_id. Everything else stays as text in composing_text.
                   The `attached:` prefix is removed from the eight entries that had it: where data/command_relations.csv already holds the
                   relationship (subject = the attached unit, higher = the claiming unit, valid on the claim date) nothing more is kept; otherwise the
                   entry gets the qualifier `(attached)` so the claim loses no information, and it is listed for review.
  data/units.csv   the placeholder units, in unit_id order.

Usage: python scripts/migrate_unit_ids.py --dry-run        print the plan and the lists for review, write nothing
       python scripts/migrate_unit_ids.py --apply          write data/units.csv, the claim files and docs/unit_references_review.md
       python scripts/migrate_unit_ids.py --verify REF     regenerate the old strings from the new data and diff them against git ref REF
Needs schema/claims.schema.json to already have the new columns (engaged_note, composing_text).
NOTE: one-off, already applied (commit of the branch unit-ids-in-text-columns); --dry-run and --apply refuse to run on the migrated files. To re-check the migration run --verify with the commit before it
(the parent of that commit on main, daedcc2 at the time).
"""
import argparse
import collections
import csv
import io
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common  # noqa: E402
import unit_refs as ur  # noqa: E402

REVIEW_MD = os.path.join(common.ROOT, 'docs', 'unit_references_review.md')

# Opponent spellings that are not the display name of a unit but name one that is in the table: old string -> unit_id.
ALIAS_ENGAGED = {
    'Canadian 3rd Infantry Division': 'CAN-INF-003D',                 # unit_name is '3rd Canadian Infantry Division'
    'German 17th SS Panzergrenadier Division': 'GER-SSPG-017D',       # unit_name adds the name 'Götz von Berlichingen'
    'German Nineteenth Army': 'GER-ARMY-019A',                        # unit_name is 'Nineteenth Army (Germany)'
}
# Opponent names that are named units not in data/units.csv: old string -> unit_id (the unit is added, see PLACEHOLDERS).
NEW_ENGAGED = {
    'German 6th Fallschirmjäger Regiment': 'GER-FJR-006',
    'German SS Heavy Panzer Battalion 101': 'GER-SSHPZ-101',
}
# Spellings in composing_units that name a unit of the table (the old text -> unit_id), compared after the trailing parenthesis is split off.
ALIAS_COMPOSING = {
    'Panzer Lehr': 'GER-PZ-LEHRD',                                    # unit_name 'Panzer Lehr Division'
    '716th Infantry Division': 'GER-INF-716D',                        # unit_name '716th Static Infantry Division'
    '17th SS Panzergrenadier Division': 'GER-SSPG-017D',
    'Heavy SS Panzer Bn 101': 'GER-SSHPZ-101',                        # the placeholder added for engaged_with
    '6th Fallschirmjäger Regiment': 'GER-FJR-006',
}
PLACEHOLDERS = [
    # unit_id, unit_name, nationality, echelon, branch, theater, note
    ('GER-FJR-006', '6th Fallschirmjäger Regiment', 'Germany', 'regiment/battle_group', 'Luftwaffe', 'western_europe',
     'Added as a placeholder because claims name it as an opponent (engaged_with, claims C0072, C0085, C0088) and as a component of the 91st Luftlande Division (composing_units, C0010). '
     'Identity only: no parent, no formed date; echelon regiment from the name. The id has no echelon letter (the table has no letter for a regiment).'),
    ('GER-SSHPZ-101', 'SS Heavy Panzer Battalion 101', 'Germany', 'other', 'Waffen-SS', 'western_europe',
     'Added as a placeholder because claims name it as an opponent (engaged_with, claims C0096, C0097) and as a component of the I SS Panzer Corps (composing_units, C0160 "Heavy SS Panzer Bn 101"). '
     'Identity only: no parent, no formed date. The echelon vocabulary has no battalion value, so echelon is other (a battalion). The id has no echelon letter.'),
]


def old_rows(ref=None):
    """Claim files as {path: (header, [dict])} from the working tree, or from git ref."""
    out = {}
    if ref is None:
        for p in common.claim_files():
            h, rs = common.read_dicts(p)
            out[os.path.relpath(p, common.ROOT)] = (h, rs)
        return out
    names = subprocess.run(['git', '-C', common.ROOT, 'ls-tree', '-r', '--name-only', ref, 'data/claims'], capture_output=True, text=True, check=True).stdout.split()
    for n in names:
        txt = subprocess.run(['git', '-C', common.ROOT, 'show', '%s:%s' % (ref, n)], capture_output=True, check=True).stdout.decode('utf-8')
        rd = csv.reader(io.StringIO(txt))
        h = next(rd)
        out[n] = (h, [dict(zip(h, r)) for r in rd])
    return out


def old_units(ref=None):
    if ref is None:
        return common.read_dicts(common.UNITS_CSV)[1]
    txt = subprocess.run(['git', '-C', common.ROOT, 'show', '%s:data/units.csv' % ref], capture_output=True, check=True).stdout.decode('utf-8')
    rd = csv.reader(io.StringIO(txt))
    h = next(rd)
    return [dict(zip(h, r)) for r in rd]


def relations():
    return common.read_dicts(os.path.join(common.ROOT, 'data', 'command_relations.csv'))[1]


def covering(rels, subject, higher, date):
    return [r['relation_id'] for r in rels if r['subject_unit_id'] == subject and r['higher_unit_id'] == higher and r['relationship'] != 'unknown'
            and r['valid_from'] <= date and (not r['valid_to'] or date <= r['valid_to'])]


def convert_engaged(v, units, log):
    ids, notes = [], []
    if v == ur.SENTINEL:
        return v, ''
    for e in ur.split_list(v):
        if e in ALIAS_ENGAGED:
            uid, how = ALIAS_ENGAGED[e], 'alias'
        elif e in NEW_ENGAGED:
            uid, how = NEW_ENGAGED[e], 'placeholder'
        else:
            r = ur.resolve_name(e)
            uid, how = (r[0], 'name') if len(r) == 1 else (None, 'ambiguous' if r else 'text')
        if uid:
            if uid not in ids:
                ids.append(uid)
            log.append((e, uid, how))
        else:
            notes.append(e)
            log.append((e, '', how))
    return '; '.join(ids), '; '.join(notes)


def convert_composing(v, claim, units, rels, log, att):
    """(composing_units, composing_text) for one cell. log gets (entry, unit_id or '', how); att gets a row per entry that had the attached: prefix."""
    if v == ur.SENTINEL:
        return v, ''
    cu = units[claim['unit_id']]
    ids, texts = [], []
    for e in ur.split_list(v):
        attached = bool(re.match(r'^attached:\s*', e))
        body = re.sub(r'^attached:\s*', '', e)
        uid, qual, how = None, '', ''
        r = ur.resolve_name(body, cu['nationality'], cu['unit_name'])
        if len(r) == 1:
            uid, how = r[0], 'name'
            if units[uid]['nationality'] != cu['nationality'] and not any(body.startswith(a + ' ') for a in ur.adjective_nations()):
                how = 'name (other nation)'
        else:
            base, q = ur.trailing_paren(body)
            if q:
                key = ALIAS_COMPOSING.get(base)
                r2 = [key] if key else ur.resolve_name(base, cu['nationality'], cu['unit_name'])
                if len(r2) == 1:
                    uid, qual, how = r2[0], q, 'name+qualifier'
            elif body in ALIAS_COMPOSING:
                uid, how = ALIAS_COMPOSING[body], 'alias'
            if not uid and len(r) > 1:
                how = 'ambiguous'
        if uid == claim['unit_id']:
            uid = None
        cap = []
        if attached:
            if uid:
                cap = covering(rels, uid, claim['unit_id'], claim['date'])
                if not cap:
                    qual = qual[:-1] + '; attached)' if qual else '(attached)'
            att.append((claim['claim_id'], claim['date'], claim['unit_id'], e, uid or '', ','.join(cap)))
        if uid:
            if uid not in ids:
                ids.append(uid)
                if qual:
                    texts.append('%s %s' % (uid, qual))
            log.append((e, uid, how + (' attached' if attached else '')))
        else:
            t = body
            if attached:
                t = '%s (attached)' % body
            texts.append(t)
            log.append((e, '', (how or 'text') + (' attached' if attached else '')))
    return '; '.join(ids), '; '.join(texts)


def plan(old, rels):
    units = {u['unit_id']: u for u in old_units()}
    for p in PLACEHOLDERS:
        units.setdefault(p[0], {'unit_id': p[0], 'unit_name': p[1], 'nationality': p[2]})
    ur.reset()
    new, elog, clog, att = {}, [], [], []
    nat_codes = {n['name']: n['code'] for n in common.load_nationalities()}
    for path, (h, rs) in old.items():
        new[path] = [dict(d) for d in rs]
    for path, (h, rs) in old.items():
        for d, n in zip(rs, new[path]):
            lg = []
            n['engaged_with'], n['engaged_note'] = convert_engaged(d['engaged_with'], units, lg)
            elog.extend((d['claim_id'], d['unit_id']) + x for x in lg)
            lg = []
            n['composing_units'], n['composing_text'] = convert_composing(d['composing_units'], d, units, rels, lg, att)
            clog.extend((d['claim_id'], d['unit_id']) + x for x in lg)
    return new, elog, clog, att, units, nat_codes


def new_unit_rows():
    header = common.read_rows(common.UNITS_CSV)[0]
    rows = []
    for uid, name, nat, ech, br, th, note in PLACEHOLDERS:
        d = dict.fromkeys(header, '')
        d.update(unit_id=uid, unit_name=name, nationality=nat, echelon=ech, branch=br, theater=th, record_status='placeholder', unit_note=note)
        rows.append(d)
    return header, rows


def summary(elog, clog, att, new, old):
    lines = []
    ec = collections.Counter(x[4] for x in elog)
    lines.append('engaged_with: %d entries in %d claims; resolved %d (%s); to engaged_note %d' % (
        len(elog), sum(1 for p in old for d in old[p][1] if d['engaged_with'] and d['engaged_with'] != 'unknown'),
        sum(1 for x in elog if x[3]), dict(ec), sum(1 for x in elog if not x[3])))
    cc = collections.Counter(x[4] for x in clog)
    lines.append('composing_units: %d entries; converted to ids %d, kept as text %d (%s)' % (len(clog), sum(1 for x in clog if x[3]), sum(1 for x in clog if not x[3]), dict(cc)))
    lines.append('attached: prefix entries: %d (captured in command_relations %d, not captured %d)' % (len(att), sum(1 for a in att if a[5]), sum(1 for a in att if not a[5])))
    return lines


def check_no_loss(old, new, header_old):
    """Every old entry is accounted for exactly once: the number of entries in old and new engaged/composing columns agree, the other columns are untouched."""
    bad = []
    for path in old:
        h, rs = old[path]
        for d, n in zip(rs, new[path]):
            for c in h:
                if c in ('engaged_with', 'composing_units'):
                    continue
                if d[c] != n[c]:
                    bad.append((d['claim_id'], c))
            oe = [e for e in ur.split_list(d['engaged_with'])]
            ne = ur.split_ids(n['engaged_with']) if n['engaged_with'] != ur.SENTINEL else [ur.SENTINEL]
            ne_total = len(ne) + len(ur.split_list(n['engaged_note']))
            if oe and len(oe) != ne_total and len(set(ne)) == len(ne):
                bad.append((d['claim_id'], 'engaged count %d != %d' % (len(oe), ne_total)))
            oc = ur.split_list(d['composing_units'])
            nc_units = [] if n['composing_units'] == ur.SENTINEL else ur.split_ids(n['composing_units'])
            qual = [t for t in ur.split_list(n['composing_text']) if ur.QUALIFIED.match(t)]
            free = [t for t in ur.split_list(n['composing_text']) if not ur.QUALIFIED.match(t)]
            if d['composing_units'] and d['composing_units'] != ur.SENTINEL and len(oc) != len(nc_units) + len(free):
                bad.append((d['claim_id'], 'composing count %d != %d' % (len(oc), len(nc_units) + len(free))))
    return bad


def md_escape(s):
    return s.replace('|', '\\|')


def write_review(elog, clog, att, new, units):
    L = ['# Unit ids in the text columns: review', '',
         'Generated by `scripts/migrate_unit_ids.py --apply` from the claims as they were before the migration (recommendation F3 of `docs/normalization_review.md`). '
         'Everything here is the record of what the migration did and what it left for a decision; the data itself is in `data/claims/` and `data/units.csv`.', '']
    ec = collections.Counter(x[4] for x in elog)
    n_res = sum(1 for x in elog if x[3])
    L += ['## engaged_with', '',
          '%d entries in the old column (%d distinct strings): **%d resolved to a unit id**, %d kept as text in `engaged_note`. Of the resolved: %s.' % (
              len(elog), len({x[2] for x in elog}), n_res, len(elog) - n_res, ', '.join('%d by %s' % (v, k) for k, v in sorted(ec.items()) if k != 'text')), '',
          '| old string | unit id | how | claims |', '|---|---|---|---:|']
    agg = collections.OrderedDict()
    for cid, uid_, old_s, uid, how in sorted(elog, key=lambda x: (x[2], x[0])):
        agg.setdefault((old_s, uid, how), []).append(cid)
    for (s, uid, how), cs in agg.items():
        if s == ur.SENTINEL:
            continue
        L.append('| %s | %s | %s | %d |' % (md_escape(s), uid or '*engaged_note*', how, len(cs)))
    L += ['', '`how`: *name* = the old string is the display name of the unit (adjective + unit_name); *alias* = another spelling of a unit already in the table (the list is `ALIAS_ENGAGED` in the script); '
          '*placeholder* = a unit added by this migration; *text* = generic, kept verbatim in `engaged_note`. `unknown` is unchanged.', '',
          '### Placeholder units added', '', '| unit_id | unit_name | nationality | echelon | branch | claims that name it |', '|---|---|---|---|---|---|']
    for uid, name, nat, ech, br, th, note in PLACEHOLDERS:
        cl = sorted({x[0] for x in elog if x[3] == uid} | {x[0] for x in clog if x[3] == uid})
        L.append('| %s | %s | %s | %s | %s | %s |' % (uid, name, nat, ech, br, ', '.join(cl)))
    L += ['', 'Both are `record_status` placeholder with no parent, no formed date and no claim file; the unit note says why each was added. A new id has no echelon letter because the table has no letter for a regiment or battalion.', '']
    L += ['## composing_units', '']
    conv = [x for x in clog if x[3]]
    txt = [x for x in clog if not x[3]]
    L += ['%d entries in the old column (%d distinct strings): **%d became unit ids** (%d with a qualifier kept in `composing_text`), **%d stay free text** in `composing_text`.' % (
        len(clog), len({x[2] for x in clog}), len(conv), sum(1 for x in conv if 'qualifier' in x[4] or x[4] == 'alias' and False), len(txt)), '']
    L += ['### Converted to an id (distinct)', '', '| old string | unit id | how |', '|---|---|---|']
    seen = set()
    for cid, u, s, uid, how in sorted(conv, key=lambda x: x[2]):
        if (s, uid) in seen:
            continue
        seen.add((s, uid))
        L.append('| %s | %s | %s |' % (md_escape(s), uid, how))
    L += ['', '### Kept as text (distinct), by reason', '']
    reasons = collections.OrderedDict([
        ('embedded', 'contains a unit id inside a longer description (a battle group "formed from this division", "went into Kampfgruppe Rohrbach")'),
        ('ambiguous', 'a name that is more than one unit (needs the right nation)'),
        ('other', 'not a unit of the table (a regiment, battalion, company, group or remark)')])
    by = collections.defaultdict(list)
    for cid, u, s, uid, how in txt:
        k = 'ambiguous' if how.startswith('ambiguous') else ('embedded' if re.search(r'\b(?:%s)(?:-[A-Z0-9]+)+\b' % '|'.join(n['code'] for n in common.load_nationalities()), s) else 'other')
        by[k].append((s, cid))
    for k, desc in reasons.items():
        L += ['**%s** (%d entries): %s.' % (k, len(by[k]), desc), '']
        if k != 'other':
            for s, cid in sorted(by[k]):
                L.append('- %s (%s)' % (s, cid))
            L.append('')
    L += ['The `other` entries (%d, %d distinct) are listed in the claim files; they are what would become units if the table grew regiment- and battalion-level units (see the roadmap).' % (len(by['other']), len({s for s, _ in by['other']})), '']
    L += ['## `attached:` entries', '',
          'Eight entries had the prefix `attached:` (in these old strings the prefix marks the first entry after it; the entries after it in the same list carry no marker). The prefix is gone and is now a validation error. '
          'A relationship belongs in `data/command_relations.csv`: where a relation with the attached unit as subject and the claiming unit as higher, valid on the claim date, already exists, the entry is just the component and nothing else is kept; '
          'where there is none the entry keeps the qualifier `(attached)` (the way `30th Infantry Division (attached)` was already written) so the claim loses nothing. '
          'No relation was added: an interval needs a unit as subject and a sourced date, and none of the eight entries has both a table unit that is not already covered and a date from a source.', '',
          '| claim | date | claiming unit | old entry | unit id | command relation covering the date | result |', '|---|---|---|---|---|---|---|']
    for cid, date, u, e, uid, cap in att:
        res = ('in command_relations (%s); entry is now the plain component' % cap) if cap else ('unit has an id, **no relation**: kept as `%s (attached)`' % uid if uid else 'not a unit of the table: kept as text `(attached)`')
        L.append('| %s | %s | %s | %s | %s | %s | %s |' % (cid, date, u, md_escape(e), uid or '', cap or '', res))
    L += ['']   # the 'Decisions for the owner' section of docs/unit_references_review.md was written by hand after the run
    return L, by


def apply(old, new, units_hdr_rows):
    hdr = common.field_names(common.load_schema('claims'))
    for path in old:
        if 'engaged_note' in old[path][0]:
            sys.exit('%s already has engaged_note: nothing to migrate' % path)
    n = 0
    for path, rs in new.items():
        with open(os.path.join(common.ROOT, path), 'wb') as f:
            f.write(common.csv_bytes(hdr, [[d[c] for c in hdr] for d in rs]))
        n += 1
    uh, add = units_hdr_rows
    cur = common.read_dicts(common.UNITS_CSV)[1]
    allr = sorted(cur + add, key=lambda d: d['unit_id'])
    with open(common.UNITS_CSV, 'wb') as f:
        f.write(common.csv_bytes(uh, [[d[c] for c in uh] for d in allr]))
    return n


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--dry-run', action='store_true')
    ap.add_argument('--apply', action='store_true')
    ap.add_argument('--verify', metavar='REF')
    a = ap.parse_args()
    if a.verify:
        import verify_unit_ids
        return verify_unit_ids.run(a.verify)
    old = old_rows()
    if any('engaged_note' in h for h, _ in old.values()):
        sys.exit('the claim files already have engaged_note: the migration is applied (use --verify REF to re-check it)')
    rels = relations()
    new, elog, clog, att, units, nat_codes = plan(old, rels)
    # the placeholder units are needed by the index used to resolve names: make a view for the plan only
    for line in summary(elog, clog, att, new, old):
        print(line)
    bad = check_no_loss(old, new, None)
    print('no-loss check: %d problems' % len(bad))
    for b in bad:
        print('  ', b)
    if bad:
        return 1
    if not a.apply:
        print('\nENGAGED')
        for x in sorted(set(elog), key=lambda x: (x[3], x[2])):
            print(' ', x)
        print('\nCOMPOSING (not converted)')
        for x in sorted({y[2:] for y in clog if not y[3]}):
            print(' ', x)
        print('\nCOMPOSING (converted)')
        for x in sorted({y[2:] for y in clog if y[3]}):
            print(' ', x)
        print('\nATTACHED')
        for x in att:
            print(' ', x)
        return 0
    n = apply(old, new, new_unit_rows())
    ur.reset()
    L, _by = write_review(elog, clog, att, new, units)
    with open(REVIEW_MD, 'w', encoding='utf-8') as f:
        f.write('\n'.join(L) + '\n')
    print('wrote %d claim files, data/units.csv (+%d units) and docs/unit_references_review.md' % (n, len(PLACEHOLDERS)))
    return 0


if __name__ == '__main__':
    sys.exit(main())
