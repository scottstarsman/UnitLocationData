#!/usr/bin/env python3
"""Semantic regression tests: what the data and the query tooling say about command situations that a reader will ask about.

The validator checks that the tables are consistent; these tests check what scripts/who_controls.py (which reads build/command_relations.csv)
ANSWERS for four representable scenarios, so that a change to the data, the build or the query rules that alters an answer is seen:

  1. First Army: operational control passes to 21st Army Group on 20 December 1944 (hour undocumented), and ends on 17 January 1945.
  2. VIII Corps: transfer from First Army to Third Army on 20 December 1944, hour undocumented: the corps level is UNKNOWN that day.
  3. 84th Infantry Division: a temporary corps-level attachment (XVIII Airborne Corps, 20 to 23 December) and the transfer to VII Corps.
  4. Administrative parent against operational headquarters: administrative_control is shown as a relationship but is not part of the operational chain.
  0. The staleness rule (R1-N-001): a relationship with no recorded end is certain only up to its last listing (schema/README.md, "Reading a command interval").
  5. NOT TESTED: an inferred position replaced by a sourced one. The data has no way to represent the replacement (no supersession or version field;
     `location_basis` marks only three claims as inferred), so there is nothing to assert yet.

Each expectation is what the data says today. Where the data differs from what one might assume, the test records the data and the comment says so; a
test is not a statement that the data is historically right, only that the answer has not changed without somebody noticing. If you change the data
on purpose, change the expectation in the same commit and say why.

Usage: python scripts/semantic_tests.py          (run python scripts/build.py first; exit code 1 if any expectation fails)
Standard library only.
"""
import contextlib
import io
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common  # noqa: E402
import who_controls as wc  # noqa: E402

REL_PATH = os.path.join(common.BUILD_DIR, 'command_relations.csv')
_ROWS = common.read_dicts(REL_PATH)[1]

# unit ids used below
FIRST_ARMY, THIRD_ARMY, NINTH_ARMY, SEVENTH_ARMY = 'US-ARMY-001A', 'US-ARMY-003A', 'US-ARMY-009A', 'US-ARMY-007A'
ARMY_GROUP_12, ARMY_GROUP_21 = 'US-AG-012G', 'UK-AG-021G'
CORPS_VII, CORPS_VIII, CORPS_XVIII_ABN, CORPS_VI, CORPS_BRIT_I = 'US-COR-007C', 'US-COR-008C', 'US-ABN-018C', 'US-COR-006C', 'UK-COR-001C'
DIV_84, DIV_104, DIV_45, DIV_29 = 'US-INF-084D', 'US-INF-104D', 'US-INF-045D', 'US-INF-029D'

FAILURES = []
CHECKED = [0]


class Answer(dict):
    """A missing (higher unit, relationship) reads as ('absent', ''), so that a missing interval is a failed expectation, not a crash."""
    def __missing__(self, key):
        return ('absent', '')


def intervals(unit, date, time=''):
    """{(higher_unit_id, relationship): (status, why-text)} for every interval of the unit that covers the date (status certain | possible)."""
    out = Answer()
    for r in _ROWS:
        if r['higher_unit_id'] and r['subject_unit_id'] == unit:
            st, why = wc.status(r, date, time)
            if st != 'no':
                out[(r['higher_unit_id'], r['relationship'])] = ('certain' if st == 'yes' else 'possible', '; '.join(why))
    return out


def chain(unit, date, time=''):
    """The operational chain printed by who_controls.py, as a list of (name, relationship or None, status) per level; an UNKNOWN level is
    ('UNKNOWN', names, None)."""
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        wc.main([unit, date] + ([time] if time else []))
    text = buf.getvalue()
    if 'operational chain:\n' not in text:
        return [('NO CHAIN', [], None)]
    lines = text.split('operational chain:\n', 1)[1].rstrip('\n').split('\n')
    out = []
    for line in lines:
        s = line.strip()
        m = re.match(r'UNKNOWN at this level: (.+?) \((.*)\)$', s)
        if m:
            out.append(('UNKNOWN', sorted(m.group(1).split(' or ')), None))
            continue
        m = re.match(r'(.+?) \((\w+), (certain|possible)', s)
        out.append((m.group(1), m.group(2), m.group(3)) if m else ('UNPARSED', s, None))
    return out


def expect(label, got, want):
    CHECKED[0] += 1
    if got != want:
        FAILURES.append('%s\n      expected: %r\n      got:      %r' % (label, want, got))


def expect_in(label, text, needle):
    CHECKED[0] += 1
    if needle not in text:
        FAILURES.append('%s\n      expected the text to contain %r\n      got: %r' % (label, needle, text))


def master(unit, higher, relationship, valid_from):
    """The relation of the unit to the higher unit with that relationship that starts on valid_from (a sequence can hold several intervals)."""
    rows = [r for r in _ROWS if r['subject_unit_id'] == unit and r['higher_unit_id'] == higher and r['relationship'] == relationship and r['valid_from'] == valid_from]
    expect('exactly one %s relation %s -> %s from %s in build/command_relations.csv' % (relationship, unit, higher, valid_from), len(rows), 1)
    return rows[0] if rows else {k: '' for k in _ROWS[0]}


def scenario_0_staleness():
    """R1-N-001: a standing relationship is certain only up to its last listing."""
    s = 'staleness (US-INF-029D, last claim 1944-09-29)'
    row = master(DIV_29, 'US-ARMY-001A', 'assigned', '1944-09-21')
    expect(s + ': last_listed_date of the assignment to First Army', row['last_listed_date'], '1944-09-29')
    expect(s + ': its end is not recorded', row['valid_to_basis'], 'open_at_last_claim')
    expect(s + ': 1944-09-29 (last listing) is certain', intervals(DIV_29, '1944-09-29')[('US-ARMY-001A', 'assigned')][0], 'certain')
    st, why = intervals(DIV_29, '1944-12-31')[('US-ARMY-001A', 'assigned')]
    expect(s + ': 1944-12-31 (93 days after) is possible, not certain', st, 'possible')
    expect_in(s + ': the reason names the last listing and the distance', why, 'after the last claim that lists it (1944-09-29, 93 days earlier)')
    expect_in(s + ': the reason says the standing relationship is carried forward', why, 'carried forward until a replacement is recorded')
    stale = {k: v[0] for k, v in intervals(DIV_29, '1944-12-31').items()}
    expect(s + ': every interval of the division on 1944-12-31 is possible', set(stale.values()), {'possible'})
    # an inferred end: certain up to the last listing, possible after it (the rule that already applied)
    inferred = [r for r in _ROWS if r['valid_to_basis'] == 'inferred_from_next_claim']
    expect(s + ': last_listed_date equals valid_to_earliest for every inferred end', [r['relation_id'] for r in inferred if r['last_listed_date'] != r['valid_to_earliest']], [])
    # a sourced end is not capped
    row = master(FIRST_ARMY, ARMY_GROUP_21, 'operational_control', '1944-12-20')
    expect(s + ': a sourced end (assignment table) is never capped by the last listing: 1945-01-10 is certain', intervals(FIRST_ARMY, '1945-01-10')[(ARMY_GROUP_21, 'operational_control')][0], 'certain')
    expect(s + ': ...although the last listing is 1945-01-17 (Batch 4: C0587 lists the relation on its end day)', row['last_listed_date'], '1945-01-17')


def scenario_1_first_army():
    s = 'scenario 1, First Army (operational control to 21st Army Group)'
    # data: the change is an operational_control overlay from 1944-12-20 (narrative, no hour) to 1945-01-17 (assignment table); the assignment
    # to 12th Army Group is NOT ended on 20 December (assigned, open). The reviewer's reading "control moves from 12th to 21st Army Group" is
    # therefore represented as operational control on top of an unchanged assignment.
    row = master(FIRST_ARMY, ARMY_GROUP_21, 'operational_control', '1944-12-20')
    expect(s + ': start 1944-12-20, basis narrative, no hour', (row['valid_from'], row['valid_from_basis'], row['valid_from_time']), ('1944-12-20', 'narrative', ''))
    expect(s + ': end 1945-01-17 from the assignment table', (row['valid_to'], row['valid_to_basis']), ('1945-01-17', 'assignment_table'))
    base = master(FIRST_ARMY, ARMY_GROUP_12, 'assigned', '1944-08-01')
    expect(s + ': the assignment to 12th Army Group stays open (not ended by the change)', (base['valid_to'], base['valid_to_basis']), ('', 'open_at_last_claim'))
    a = intervals(FIRST_ARMY, '1944-12-19')
    expect(s + ': 19 Dec: no relation to 21st Army Group', (ARMY_GROUP_21, 'operational_control') in a, False)
    expect(s + ': 19 Dec: chain starts with 12th Army Group, certain', chain(FIRST_ARMY, '1944-12-19')[0], ('US 12th Army Group', 'assigned', 'certain'))
    a = intervals(FIRST_ARMY, '1944-12-20')
    expect(s + ': 20 Dec: the 21st Army Group relation is possible (hour undocumented)', a[(ARMY_GROUP_21, 'operational_control')][0], 'possible')
    expect_in(s + ': 20 Dec: reason is the undocumented hour', a[(ARMY_GROUP_21, 'operational_control')][1], 'starts that day at an undocumented hour')
    expect(s + ': 20 Dec: chain starts with 21st Army Group as possible', chain(FIRST_ARMY, '1944-12-20')[0], ('British 21st Army Group', 'operational_control', 'possible'))
    expect(s + ': 20 Dec at 12:00: still possible (no hour is recorded to compare with)', chain(FIRST_ARMY, '1944-12-20', '12:00')[0], ('British 21st Army Group', 'operational_control', 'possible'))
    expect(s + ': 20 Dec: the 12th Army Group assignment still covers the day', (ARMY_GROUP_12, 'assigned') in a, True)
    expect(s + ': 21 Dec: chain starts with 21st Army Group, certain', chain(FIRST_ARMY, '1944-12-21')[0], ('British 21st Army Group', 'operational_control', 'certain'))
    # consequence of the staleness rule, recorded as the data gives it: before Batch 4 the assignment was last listed on 20 Dec, so from 21 Dec it was possible;
    # Batch 4 adds a First Army claim on 17 Jan 1945 that lists it, so the whole gap is now certain
    expect(s + ': 21 Dec: the assignment to 12th Army Group (listed again on 17 Jan 1945) is certain', intervals(FIRST_ARMY, '1944-12-21')[(ARMY_GROUP_12, 'assigned')][0], 'certain')
    expect(s + ': 17 Jan 1945: the end hour is undocumented, so possible', intervals(FIRST_ARMY, '1945-01-17')[(ARMY_GROUP_21, 'operational_control')][0], 'possible')
    a = intervals(FIRST_ARMY, '1945-01-18')
    expect(s + ': 18 Jan 1945: no relation to 21st Army Group', (ARMY_GROUP_21, 'operational_control') in a, False)
    expect(s + ': 18 Jan 1945: chain falls back to 12th Army Group (possible: last listed 17 Jan 1945, the day before)', chain(FIRST_ARMY, '1945-01-18')[0], ('US 12th Army Group', 'assigned', 'possible'))


def scenario_2_viii_corps():
    s = 'scenario 2, VIII Corps (transfer to Third Army on 20 Dec, hour uncertain)'
    first = master(CORPS_VIII, FIRST_ARMY, 'assigned', '1944-10-22')
    third = master(CORPS_VIII, THIRD_ARMY, 'assigned', '1944-12-20')
    expect(s + ': First Army assignment ends 1944-12-20 (narrative, earliest end 12-19)', (first['valid_to'], first['valid_to_basis'], first['valid_to_earliest'], first['valid_to_time']), ('1944-12-20', 'narrative', '1944-12-19', ''))
    expect(s + ': Third Army assignment starts 1944-12-20 (narrative, no hour), open', (third['valid_from'], third['valid_from_basis'], third['valid_from_time'], third['valid_to']), ('1944-12-20', 'narrative', '', ''))
    a = intervals(CORPS_VIII, '1944-12-19')
    expect(s + ': 19 Dec: First Army, certain; no Third Army', (a[(FIRST_ARMY, 'assigned')][0], (THIRD_ARMY, 'assigned') in a), ('certain', False))
    expect(s + ': 19 Dec: chain starts with First Army, certain', chain(CORPS_VIII, '1944-12-19')[0], ('US First Army', 'assigned', 'certain'))
    a = intervals(CORPS_VIII, '1944-12-20')
    expect(s + ': 20 Dec: both armies cover the day, both possible', (a[(FIRST_ARMY, 'assigned')][0], a[(THIRD_ARMY, 'assigned')][0]), ('possible', 'possible'))
    expect(s + ': 20 Dec: the army level is UNKNOWN', chain(CORPS_VIII, '1944-12-20')[0], ('UNKNOWN', ['US First Army', 'US Third Army'], None))
    expect(s + ': 20 Dec at 12:00: still UNKNOWN (the hour of the transfer is not recorded)', chain(CORPS_VIII, '1944-12-20', '12:00')[0], ('UNKNOWN', ['US First Army', 'US Third Army'], None))
    a = intervals(CORPS_VIII, '1944-12-21')
    expect(s + ': 21 Dec: only Third Army covers the day', sorted(k[0] for k in a), [THIRD_ARMY])
    # data differs from the natural expectation "certain after 20 Dec": the assignment was last listed on 20 Dec, so from 21 Dec it is carried forward.
    # The note of the relation says the first day certainly under Third Army is 21 Dec (Green Book, p399), but the table has no field for that
    # knowledge: the tool can only say "possible: last listed 20 Dec". The expectation records the tool's answer, not the historian's.
    expect(s + ': 21 Dec: Third Army is possible (last listed 20 Dec; carried forward)', a[(THIRD_ARMY, 'assigned')][0], 'possible')
    expect_in(s + ': 21 Dec: the reason names the last listing', a[(THIRD_ARMY, 'assigned')][1], 'after the last claim that lists it (1944-12-20, 1 day earlier)')
    expect(s + ': 21 Dec: chain starts with Third Army', chain(CORPS_VIII, '1944-12-21')[0], ('US Third Army', 'assigned', 'possible'))


def scenario_3_84th_division():
    s = 'scenario 3, 84th Infantry Division (corps-level attachment, then transfer)'
    att = master(DIV_84, CORPS_XVIII_ABN, 'attached', '1944-12-20')
    vii = master(DIV_84, CORPS_VII, 'unspecified_subordination', '1944-12-20')
    expect(s + ': XVIII Airborne Corps attachment 12-20 to 12-23, end between 12-22 and 12-23, from the narrative',
           (att['valid_from'], att['valid_to'], att['valid_to_earliest'], att['valid_to_basis']), ('1944-12-20', '1944-12-23', '1944-12-22', 'narrative'))
    # data differs from "transferred to VII Corps": the VII Corps relation is unspecified_subordination (the source does not say assigned or attached),
    # starts between 12-20 and 12-23 and is last listed on 12-20. The note of the relation says that operational control passed to VII Corps between
    # 22 and 23 Dec (Green Book, p426, p433), but the CMH table does not say assigned or attached, so no `attached` or `operational_control` row says so.
    expect(s + ': VII Corps relation is unspecified_subordination, start 12-20 (latest 12-23), open',
           (vii['valid_from'], vii['valid_from_latest'], vii['valid_to'], vii['valid_to_basis']), ('1944-12-20', '1944-12-23', '', 'open_at_last_claim'))
    a = intervals(DIV_84, '1944-12-19')
    expect(s + ': 19 Dec: neither corps covers the day', ((CORPS_XVIII_ABN, 'attached') in a, (CORPS_VII, 'unspecified_subordination') in a), (False, False))
    a = intervals(DIV_84, '1944-12-20')
    expect(s + ': 20 Dec: XVIII Airborne Corps possible (hour undocumented)', a[(CORPS_XVIII_ABN, 'attached')][0], 'possible')
    expect(s + ': 20 Dec: chain starts with XVIII Airborne Corps', chain(DIV_84, '1944-12-20')[0], ('US XVIII Airborne Corps', 'attached', 'possible'))
    for d in ('1944-12-21', '1944-12-22'):
        a = intervals(DIV_84, d)
        expect(s + ': %s: XVIII Airborne Corps attachment is certain' % d, a[(CORPS_XVIII_ABN, 'attached')][0], 'certain')
        expect(s + ': %s: chain starts with XVIII Airborne Corps, certain' % d, chain(DIV_84, d)[0], ('US XVIII Airborne Corps', 'attached', 'certain'))
        expect_in(s + ': %s: VII Corps is possible because its start is a range' % d, a[(CORPS_VII, 'unspecified_subordination')][1], 'start between 1944-12-20 and 1944-12-23')
    a = intervals(DIV_84, '1944-12-23')
    expect(s + ': 23 Dec: the attachment may end that day: possible', a[(CORPS_XVIII_ABN, 'attached')][0], 'possible')
    expect_in(s + ': 23 Dec: reason is the end range', a[(CORPS_XVIII_ABN, 'attached')][1], 'end between 1944-12-22 and 1944-12-23')
    a = intervals(DIV_84, '1944-12-24')
    expect(s + ': 24 Dec: the XVIII Airborne Corps attachment no longer covers the day', (CORPS_XVIII_ABN, 'attached') in a, False)
    expect(s + ': 24 Dec: VII Corps still covers the day, possible (carried forward from its last listing, 20 Dec)', a[(CORPS_VII, 'unspecified_subordination')][0], 'possible')
    # data differs from "VII Corps is the operational headquarters after the transfer": an attachment (here to First Army, from the assignment table)
    # outranks a standing relationship in the operational chain, so VII Corps never appears in the chain.
    expect(s + ': 24 Dec: the chain starts with First Army (attached, certain), not VII Corps', chain(DIV_84, '1944-12-24')[0], ('US First Army', 'attached', 'certain'))


def scenario_4_administrative_versus_operational():
    s = 'scenario 4, administrative parent against operational headquarters'
    expect(s + ': administrative_control is neither an active nor a standing relationship (it is not in the operational chain)',
           ('administrative_control' in common.relationship_group('active'), 'administrative_control' in common.relationship_group('standing')), (False, False))
    a = intervals(DIV_104, '1944-10-20')
    expect(s + ': 104th Division, 20 Oct 1944: Ninth Army administrative_control is listed and certain', a[(NINTH_ARMY, 'administrative_control')][0], 'certain')
    c = chain(DIV_104, '1944-10-20')
    expect(s + ': 104th Division: the operational chain starts with British I Corps (operational_control, certain)', c[0], ('British I Corps', 'operational_control', 'certain'))
    expect(s + ': 104th Division: Ninth Army is not in the operational chain', [x[0] for x in c if 'Ninth' in x[0]], [])
    a = intervals(DIV_45, '1944-08-20')
    expect(s + ': 45th Division, 20 Aug 1944: Seventh Army administrative_control is listed and certain', a[(SEVENTH_ARMY, 'administrative_control')][0], 'certain')
    c = chain(DIV_45, '1944-08-20')
    expect(s + ': 45th Division: the chain starts with VI Corps, not with the administrative parent', c[0][:2], ('US VI Corps', 'unspecified_subordination'))
    expect(s + ': 45th Division: Seventh Army appears only above VI Corps, through the corps relationship (assigned)', c[1][:2], ('US Seventh Army', 'assigned'))
    # First Army (scenario 1): an overlay of operational control does not remove the assignment to its army group
    expect(s + ': First Army, 21 Dec 1944: assigned to 12th Army Group and under operational control of 21st Army Group at the same time',
           sorted(k for k in intervals(FIRST_ARMY, '1944-12-21')), sorted([(ARMY_GROUP_12, 'assigned'), (ARMY_GROUP_21, 'operational_control')]))


def main():
    for fn in (scenario_0_staleness, scenario_1_first_army, scenario_2_viii_corps, scenario_3_84th_division, scenario_4_administrative_versus_operational):
        before = len(FAILURES)
        try:
            fn()
        except Exception as e:   # a changed answer can also break the shape of the output the tests read; that is a failure too
            FAILURES.append('%s raised %s: %s' % (fn.__name__, type(e).__name__, e))
        print('%-45s %s' % (fn.__name__, 'ok' if len(FAILURES) == before else 'FAILED (%d)' % (len(FAILURES) - before)))
    print('%-45s %s' % ('scenario_5_inferred_position_replaced', 'NOT TESTED: the data cannot represent the replacement of an inferred position by a sourced one'))
    if FAILURES:
        print('\n%d of %d expectations failed:' % (len(FAILURES), CHECKED[0]))
        for f in FAILURES:
            print('  - ' + f)
        return 1
    print('\nOK: %d expectations hold' % CHECKED[0])
    return 0


if __name__ == '__main__':
    sys.exit(main())
