#!/usr/bin/env python3
"""Answer "which higher headquarters held this unit on this date (and hour)?" from build/command_relations.csv (the master data/command_relations.csv
with names and evidence; run python scripts/build.py first).

Usage: python scripts/who_controls.py US-ARM-002D 1944-08-28
       python scripts/who_controls.py US-ABN-101D 1944-12-20 12:00        (optional HH:MM, 24-hour)
       python scripts/who_controls.py "2nd Armored" 1944-08-28            (matches a substring of the subject name)

Prints every interval that covers the date, each marked [certain] or [possible: why], then the immediate operational parent
and the chain above it. Intervals are INCLUSIVE (valid_to is the last day), so on the day one relationship ends and the next
begins both cover the day; the hour decides, and where no hour is recorded the answer for that level is UNKNOWN rather than a
guess. A start range (valid_from..valid_from_latest), an end range (valid_to_earliest..valid_to) or an end inferred from the
next claim also makes an interval [possible].

Staleness rule (schema/README.md, "Reading a command interval"). Every interval whose end is not sourced also prints a label with the date of
the last claim that lists it (last_listed_date in build/command_relations.csv) and its end basis, whatever the status. A relationship is
[certain] only up to that date. For a date AFTER the last listing of a relationship that has no recorded end (valid_to_basis
open_at_last_claim) the interval is [possible], at any distance: the sources observed it last on that date, and a standing relationship (assigned,
unspecified_subordination) is carried forward only until a replacement is recorded, a temporary one has an unknown end. The reason names the
last listing, the number of days since it and that kind of carry-forward. This is the rule already applied to an end inferred from the next
claim (a date after valid_to_earliest is [possible]); there is no day threshold, and no date is invented. The operational parent is the lowest-echelon holder of operational_control or
attached, else of a standing relationship (assigned, unspecified_subordination). The table covers every unit that has a claim (all nationalities,
the whole period of the data); `organic` relations are not in it. A relation marked [change undated] belongs to one of the parent changes that no
source dates (change_undated in the master table): the change fell between the previous relation's last listing and this one's first. Where only
an explicit `unknown` placeholder (no higher unit named by any source) covers the date, the answer says so. Standard library only.
"""
import datetime
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common  # noqa: E402

RANK = common.echelon_rank()                    # schema/vocabularies.json, vocabulary echelon_rank
ACTIVE = common.relationship_group('active')    # schema/vocabularies.json, vocabulary relationship_groups
STANDING = ('assigned', 'unspecified_subordination')


def status(iv, date, time):
    """('yes' | 'no' | 'possible', [reasons]) for one interval on a date and optional HH:MM."""
    why = []
    frm, to = iv['valid_from'], iv['valid_to']
    if date < frm or (to and date > to):
        return 'no', why
    if date == frm and iv['valid_from_basis'] != 'claim_date':
        ft = iv.get('valid_from_time', '')
        if ft and time:
            if time < ft:
                return 'no', why
        else:
            why.append('starts that day at %s' % (ft or 'an undocumented hour'))
    if iv['valid_from_latest'] and date < iv['valid_from_latest']:
        why.append('start between %s and %s' % (frm, iv['valid_from_latest']))
    last = iv.get('last_listed_date', '')
    if iv['valid_to_basis'] == 'open_at_last_claim' and last and date > last:
        days = (datetime.date.fromisoformat(date) - datetime.date.fromisoformat(last)).days
        why.append('after the last claim that lists it (%s, %d day%s earlier); %s' % (
            last, days, '' if days == 1 else 's',
            'a standing relationship, carried forward until a replacement is recorded' if iv['relationship'] in STANDING + ('unknown', 'organic')
            else 'no end recorded'))
    if to:
        tt = iv.get('valid_to_time', '')
        if date == to and iv['valid_to_basis'] != 'inferred_from_next_claim':
            if tt and time:
                if time > tt:
                    return 'no', why
            else:
                why.append('ends that day at %s' % (tt or 'an undocumented hour'))
        if iv['valid_to_earliest'] and date > iv['valid_to_earliest']:
            why.append('end between %s and %s' % (iv['valid_to_earliest'], to) + (' (change undated: no source dates the change of parent)' if iv.get('change_undated') == 'true' else ''))
    return ('possible' if why else 'yes'), why


def main(argv):
    if len(argv) not in (2, 3):
        print(__doc__)
        return 2
    who, date = argv[0], argv[1]
    time = argv[2] if len(argv) == 3 else ''
    if time and not re.fullmatch(r'([01]\d|2[0-3]):[0-5]\d', time):
        print('time must be HH:MM (24-hour)')
        return 2
    path = os.path.join(common.BUILD_DIR, 'command_relations.csv')
    _h, rows = common.read_dicts(path)
    _uh, units = common.read_dicts(common.UNITS_CSV)
    ech = {u['unit_id']: u['echelon'] for u in units}

    def hits_for(uid_or_name):
        out = []
        for r in rows:
            if not r['higher_unit_id']:
                continue   # explicit unknown placeholders are reported separately
            if r['subject_unit_id'] == uid_or_name or (uid_or_name.lower() in r['subject_name'].lower() and not uid_or_name.startswith(('US-', 'UK-', 'GER-', 'CAN-'))):
                st, why = status(r, date, time)
                if st != 'no':
                    out.append((r, st, why))
        return out

    hits = hits_for(who)
    if not hits:
        holes = [r for r in rows if not r['higher_unit_id'] and (r['subject_unit_id'] == who or who.lower() in r['subject_name'].lower()) and status(r, date, time)[0] != 'no']
        if holes:
            for r in holes:
                print('%s on %s: no higher headquarters is recorded; relation %s is an explicit unknown (%s to %s): %s' % (
                    r['subject_unit_id'], date, r['relation_id'], r['valid_from'], r['valid_to'] or 'open', r['note']))
            return 1
        print('no relationship interval covers %s on %s in %s' % (who, date, os.path.relpath(path, common.ROOT)))
        return 1
    print('%s on %s%s' % (who, date, (' at ' + time) if time else ''))
    try:   # activity pilot: printed only for units with activity rows (docs/activity_status_design.md)
        import activity as _act
        _a = _act.activity_at(who, date)
        if _a:
            print('activity: ' + _act.describe(_a))
    except ImportError:
        pass
    for r, st, why in sorted(hits, key=lambda h: (h[0]['relationship'], h[0]['higher_unit_id'])):
        label = ''
        if r['valid_to_basis'] == 'inferred_from_next_claim':
            label = ' [last listed %s; end inferred from next claim]' % (r['last_listed_date'] or r['valid_to_earliest'])
        if r['valid_to_basis'] == 'open_at_last_claim':
            label = ' [last listed %s; no end recorded]' % r['last_listed_date']
        print('%s -> %s: %s, %s%s to %s%s, support %s (%s) [%s] [%s%s]%s' % (
            r['subject_unit_id'], r['higher_name'], r['relationship'], r['valid_from'], (' ' + r['valid_from_time']) if r['valid_from_time'] else '',
            r['valid_to'] or 'open', (' ' + r['valid_to_time']) if r['valid_to_time'] else '', r['support'],
            r['valid_to_basis'] or r['valid_from_basis'], r['source_claim_ids'],
            'certain' if st == 'yes' else 'possible', (': ' + '; '.join(why)) if st == 'possible' else '', label))

    # operational chain: lowest-echelon holder of operational_control/attached, else of a standing relationship
    print('operational chain:')
    cur, seen = who, set()
    cur_hits = hits
    for depth in range(5):
        pool = [h for h in cur_hits if h[0]['relationship'] in ACTIVE] or [h for h in cur_hits if h[0]['relationship'] in STANDING]
        if not pool:
            break
        low = min(RANK.get(ech.get(h[0]['higher_unit_id'], 'other'), 8) for h in pool)
        pool = [h for h in pool if RANK.get(ech.get(h[0]['higher_unit_id'], 'other'), 8) == low]
        ids = sorted({h[0]['higher_unit_id'] for h in pool})
        names = {h[0]['higher_unit_id']: h[0]['higher_name'] for h in pool}
        sure = [i for i in ids if any(h[0]['higher_unit_id'] == i and h[1] == 'yes' for h in pool)]
        pad = '  ' * (depth + 1)
        if len(ids) > 1 and not sure:
            print('%sUNKNOWN at this level: %s (%s%s)' % (pad, ' or '.join(names[i] for i in ids),
                  'hour of the change not documented' if any('undocumented hour' in w for h in pool for w in h[2]) else 'none is observed on this date', '' if not time else ' for %s' % time))
            break
        pick = sure[0] if sure else ids[0]
        h = [x for x in pool if x[0]['higher_unit_id'] == pick][0]
        print('%s%s (%s, %s%s)' % (pad, names[pick], h[0]['relationship'], 'certain' if h[1] == 'yes' else 'possible',
                                   ': ' + '; '.join(h[2]) if h[2] else ''))
        if pick in seen or not pick:
            break
        seen.add(pick)
        cur_hits = hits_for(pick)
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
