#!/usr/bin/env python3
"""Answer "which higher headquarters held this unit on this date (and hour)?" from build/command_relations.csv (the master data/command_relations.csv
with names and evidence; run python scripts/build.py first).

Usage: python scripts/who_controls.py US-ARM-002D 1944-08-28
       python scripts/who_controls.py US-ABN-101D 1944-12-20 12:00        (optional HH:MM, 24-hour)
       python scripts/who_controls.py "2nd Armored" 1944-08-28            (matches a substring of the subject name)

For an air or naval unit (not in the main table) the same answer is read from build/other_domains/command_relations.csv and a second block, the
administrative chain (an administrative_control relation, or an assigned relation while another headquarters holds operational_control or the
attachment), follows the operational chain; ground answers are unchanged (docs/air_naval_pilot.md section 9.4).

Prints every interval that covers the date, each marked [certain] or [possible: why], then the immediate operational parent
and the chain above it. Intervals are INCLUSIVE (valid_to is the last day), so on the day one relationship ends and the next
begins both cover the day; the hour decides, and where no hour is recorded the answer for that level is UNKNOWN rather than a
guess. A start range (valid_from..valid_from_latest), an end range (valid_to_earliest..valid_to) or an end inferred from the
next claim also makes an interval [possible].

Staleness rule (schema/README.md, "Reading a command interval"). Every interval whose end is not sourced also prints a label with the date of
the last claim that lists it (last_listed_date in build/command_relations.csv) and its end basis, whatever the status. A relationship is
[certain] only up to that date. For a date AFTER the last listing of a relationship that has no recorded end (valid_to_basis
open_at_last_claim) the interval is [possible] for at most OPEN_CARRY_FORWARD_DAYS (90) after that listing: the sources observed it last on that
date, and a standing relationship (assigned, unspecified_subordination) is carried forward only until a replacement is recorded, a temporary
one has an unknown end. Beyond 90 days the interval no longer covers the date (the answer is dropped, not a new state). No end date is
written into the tables; 90 days is the same threshold already used to flag stale-relation repair candidates, chosen because 60 days would
drop late-war divisions last listed only two months earlier, while 90 days still removes the VE-Day leftover (101 German units answering off
listings 90+ days old, including June 1944 Kampfgruppen). The reason names the last listing, the number of days since it and that kind of
carry-forward. This is the rule already applied to an end inferred from the next claim (a date after valid_to_earliest is [possible] within its
bounded interval); a sourced end is never capped. The operational parent is the lowest-echelon holder of operational_control or
attached, else of a standing relationship (assigned, unspecified_subordination). The table covers every unit that has a claim (all nationalities,
the whole period of the data); `organic` relations are not in it. A relation marked [change undated] belongs to one of the parent changes that no
source dates (change_undated in the master table): the change fell between the previous relation's last listing and this one's first. Where only
an explicit `unknown` placeholder (no higher unit named by any source) covers the date, the answer says so. Standard library only.

Organic fallback (14 November 2026). Before this rule a unit whose only relation on a date was `organic` (a combat command, a Kampfgruppe, a regiment of
its own division) had no operational answer, because `organic` is not in build/command_relations.csv. Now, at any level of the chain where NO non-organic
relation of any kind (operational_control, attached, assigned, unspecified_subordination, reserve, administrative_control, unknown with a named higher
unit, ...) covers the date, the lookup falls back to the unit's organic parent, read from build/organic_relations.csv (the preferred `organic` relations,
same columns and the same staleness rule, including OPEN_CARRY_FORWARD_DAYS, as every other interval), and goes on up the chain from that parent as
normal (the parent may itself fall back). An explicit non-organic relation always wins, even a [possible] one; the fallback never mixes with it. A
fallback answer is marked: the interval line ends [organic_fallback: ...] and the chain level reads "(organic_fallback, certain|possible)" instead of the
relationship, so it cannot be mistaken for a sourced operational link. An explicit `unknown` placeholder without a higher unit is not a superior and does
not block the fallback; it is printed as a note. The fallback adds no data: the organic relation is the sourced fact, only the lookup rule changed.

Per-relation overrides (14 November 2026, Scott's decision). build/who_controls_overrides.csv (a copy of data/who_controls_overrides.csv) lists relations that this
lookup sets aside when it answers for their subject (effect defer_to_organic_parent): the relation is not used as a hit, so the organic fallback applies and
the unit answers with its organic parent, exactly as if the relation did not exist. It is not a general rule: it covers only the listed relations (today CR0017 and
CR0026, the corps links of GER-KG-002PZ and GER-KG-MEYER). The relation stays in the data and in build/command_relations.csv; any other non-organic relation
that covers the date still wins. A set-aside relation that covers the date is printed as a note.
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

# An open_at_last_claim interval is answered as [possible] for at most this many days after last_listed_date.
# Beyond that the interval no longer covers the date. 90 days is the stale-relation repair threshold already
# used in the command-chain repair (docs/methodology.md, 9 November 2026) and is the value that removes the
# observed VE-Day leftover (101 German units still answering off listings 90+ days old) without dropping
# late-war divisions last listed 61-89 days earlier. This is a reading cutoff, not an invented end date.
OPEN_CARRY_FORWARD_DAYS = 90

# Basis printed for a chain level that is answered from the organic parent because no non-organic relation covers the date.
ORGANIC_FALLBACK = 'organic_fallback'


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
        if days > OPEN_CARRY_FORWARD_DAYS:
            return 'no', []   # reading cutoff: do not invent an end date; just stop answering possible
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
    other_path = os.path.join(common.BUILD_DIR, 'other_domains', 'command_relations.csv')   # air and naval subjects; consulted only when the main table has no answer
    other_rows = common.read_dicts(other_path)[1] if os.path.isfile(other_path) else []
    organic_path = os.path.join(common.BUILD_DIR, 'organic_relations.csv')   # the preferred organic relations; consulted only for the organic fallback
    organic_rows = common.read_dicts(organic_path)[1] if os.path.isfile(organic_path) else []
    override_path = os.path.join(common.BUILD_DIR, 'who_controls_overrides.csv')   # relations set aside for their subject (effect defer_to_organic_parent)
    overrides = {o['relation_id']: o for o in common.read_dicts(override_path)[1]} if os.path.isfile(override_path) else {}
    _uh, units = common.read_dicts(common.UNITS_CSV)
    ech = {u['unit_id']: u['echelon'] for u in units}

    set_aside = []   # (relation, status, why) of the overridden relations that cover the date, for the note

    def hits_for(uid_or_name, source=None):
        out = []
        for r in (rows if source is None else source):
            if not r['higher_unit_id']:
                continue   # explicit unknown placeholders are reported separately
            if source is None and r['relation_id'] in overrides and overrides[r['relation_id']]['effect'] == 'defer_to_organic_parent':
                if r['subject_unit_id'] == uid_or_name and status(r, date, time)[0] != 'no':
                    set_aside.append(r)   # not a hit: the organic parent answers (organic fallback)
                continue
            if r['subject_unit_id'] == uid_or_name or (uid_or_name.lower() in r['subject_name'].lower() and not uid_or_name.startswith(('US-', 'UK-', 'GER-', 'CAN-'))):
                st, why = status(r, date, time)
                if st != 'no':
                    out.append((r, st, why))
        return out

    def organic_hits_for(uid_or_name):
        return hits_for(uid_or_name, organic_rows)

    hits = hits_for(who)
    other_mode = False
    if not hits and other_rows and not any(not r['higher_unit_id'] and r['subject_unit_id'] == who for r in rows):
        rows = rows + other_rows   # an air or naval unit: its relations are in build/other_domains/command_relations.csv; ground answers never reach this line
        hits = hits_for(who)
        other_mode = bool(hits)
    holes = [r for r in rows if not r['higher_unit_id'] and (r['subject_unit_id'] == who or who.lower() in r['subject_name'].lower()) and status(r, date, time)[0] != 'no']
    fallback_hits = [] if hits else organic_hits_for(who)   # organic fallback: only where no non-organic relation covers the date
    if not hits and not fallback_hits:
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
    for r in sorted({s['relation_id']: s for s in set_aside if s['subject_unit_id'] == who}.values(), key=lambda s: s['relation_id']):
        o = overrides[r['relation_id']]   # a set-aside relation is a sourced fact kept in the data; say that it was not used and why
        print('note: relation %s (%s, %s) is set aside by a per-relation override (%s, %s): %s' % (r['relation_id'], r['relationship'], r['higher_name'], o['decided_by'], o['decided_on'], o['reason']))
    if fallback_hits:
        for r in holes:   # an explicit unknown placeholder names no superior, so it does not block the fallback; say that it exists
            print('note: relation %s is an explicit unknown (%s to %s): %s' % (r['relation_id'], r['valid_from'], r['valid_to'] or 'open', r['note']))
    for r, st, why in sorted(hits or fallback_hits, key=lambda h: (h[0]['relationship'], h[0]['higher_unit_id'])):
        label = ''
        if r['valid_to_basis'] == 'inferred_from_next_claim':
            label = ' [last listed %s; end inferred from next claim]' % (r['last_listed_date'] or r['valid_to_earliest'])
        if r['valid_to_basis'] == 'open_at_last_claim':
            label = ' [last listed %s; no end recorded]' % r['last_listed_date']
        print('%s -> %s: %s, %s%s to %s%s, support %s (%s) [%s] [%s%s]%s' % (
            r['subject_unit_id'], r['higher_name'], r['relationship'], r['valid_from'], (' ' + r['valid_from_time']) if r['valid_from_time'] else '',
            r['valid_to'] or 'open', (' ' + r['valid_to_time']) if r['valid_to_time'] else '', r['support'],
            r['valid_to_basis'] or r['valid_from_basis'], r['source_claim_ids'],
            'certain' if st == 'yes' else 'possible', (': ' + '; '.join(why)) if st == 'possible' else '', label + (
                ' [%s: no operational, attachment or other non-organic relation covers this date]' % ORGANIC_FALLBACK if fallback_hits else '')))

    # operational chain: lowest-echelon holder of operational_control/attached, else of a standing relationship
    print('operational chain:')
    cur, seen = who, set()
    cur_hits = hits
    cur_fallback = fallback_hits
    for depth in range(5):
        fb = False
        if cur_hits:
            pool = [h for h in cur_hits if h[0]['relationship'] in ACTIVE] or [h for h in cur_hits if h[0]['relationship'] in STANDING]
        else:   # no non-organic relation covers this level on the date: the organic parent stands in (marked organic_fallback)
            pool = cur_fallback
            fb = bool(pool)
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
        print('%s%s (%s, %s%s)' % (pad, names[pick], ORGANIC_FALLBACK if fb else h[0]['relationship'], 'certain' if h[1] == 'yes' else 'possible',
                                   ': ' + '; '.join(h[2]) if h[2] else ''))
        if pick in seen or not pick:
            break
        seen.add(pick)
        cur_hits = hits_for(pick)
        cur_fallback = [] if cur_hits else organic_hits_for(pick)
    if other_mode:   # air and naval: the administrative chain next to the operational one (docs/air_naval_pilot.md section 9.4)
        print('administrative chain:')
        cur, seen = who, set()
        cur_hits = hits
        for depth in range(5):
            pool = [h for h in cur_hits if h[0]['relationship'] == 'administrative_control']
            if not pool and any(h[0]['relationship'] in ACTIVE for h in cur_hits):
                pool = [h for h in cur_hits if h[0]['relationship'] in STANDING]   # assigned while another headquarters has operational control or the attachment
            if not pool:
                if depth == 0:
                    print('  (none recorded apart from the operational chain)')
                break
            low = min(RANK.get(ech.get(h[0]['higher_unit_id'], 'other'), 8) for h in pool)
            pool = [h for h in pool if RANK.get(ech.get(h[0]['higher_unit_id'], 'other'), 8) == low]
            h = sorted(pool, key=lambda x: (x[1] != 'yes', x[0]['higher_unit_id']))[0]
            pad = '  ' * (depth + 1)
            print('%s%s (%s, %s%s)' % (pad, h[0]['higher_name'], h[0]['relationship'], 'certain' if h[1] == 'yes' else 'possible', ': ' + '; '.join(h[2]) if h[2] else ''))
            if h[0]['higher_unit_id'] in seen:
                break
            seen.add(h[0]['higher_unit_id'])
            cur_hits = hits_for(h[0]['higher_unit_id'])
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
