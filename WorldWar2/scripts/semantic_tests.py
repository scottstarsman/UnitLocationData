#!/usr/bin/env python3
"""Semantic regression tests: what the data and the query tooling say about command situations that a reader will ask about.

The validator checks that the tables are consistent; these tests check what scripts/who_controls.py (which reads build/command_relations.csv)
ANSWERS for four representable scenarios, so that a change to the data, the build or the query rules that alters an answer is seen:

  1. First Army: operational control passes to 21st Army Group on 20 December 1944 (hour undocumented), and ends on 17 January 1945.
  2. VIII Corps: transfer from First Army to Third Army on 20 December 1944, hour undocumented: the corps level is UNKNOWN that day.
  3. 84th Infantry Division: a temporary corps-level attachment (XVIII Airborne Corps, 20 to 23 December) and the transfer to VII Corps.
  4. Administrative parent against operational headquarters: administrative_control is shown as a relationship but is not part of the operational chain.
  0. The staleness rule (R1-N-001): a relationship with no recorded end is certain only up to its last listing (schema/README.md, "Reading a command interval").
  6. German Batch 1 (July-August 1944): undated German parent changes are answered 'possible' on the days between two listings.
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
    expect(s + ': 18 Jan 1945: chain falls back to 12th Army Group (certain: listed on 17 Jan 1945 and again on 11 Mar 1945)', chain(FIRST_ARMY, '1945-01-18')[0], ('US 12th Army Group', 'assigned', 'certain'))


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
    # Batch 5 (C0653, 84th Division, 11 April 1945): the relation is no longer open. The CMH table lists VII Corps until 22 January 1945 and XIII Corps
    # from 3 February 1945, and the new claim lists XIII Corps instead, so the relation is closed at the last day the table lists it (valid_to 1945-01-22,
    # inferred_from_next_claim, earliest 1944-12-20). The start and the 24 December expectations below are unchanged.
    expect(s + ': VII Corps relation is unspecified_subordination, start 12-20 (latest 12-23), closed 1945-01-22 by Batch 5 (table end)',
           (vii['valid_from'], vii['valid_from_latest'], vii['valid_to'], vii['valid_to_basis']), ('1944-12-20', '1944-12-23', '1945-01-22', 'inferred_from_next_claim'))
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


def scenario_6_german_parent_changes_1944():
    """German Batch 1 (July-August 1944): parent changes that no source dates are answered 'possible', never 'certain', on the days between the two listings."""
    s = 'scenario 6, German parent changes July-August 1944'
    pz47, lehr, ss12, d352 = 'GER-PZ-047C', 'GER-PZ-LEHRD', 'GER-SSPZ-012D', 'GER-INF-352D'
    a = intervals(lehr, '1944-07-09')
    expect(s + ': Panzer Lehr, 9 Jul: I SS Panzer Corps is certain (German Batch 1b: C0788 lists the relation on that day)', a[('GER-SSPZ-001C', 'assigned')][0], 'certain')
    a = intervals(lehr, '1944-07-10')
    expect(s + ': Panzer Lehr, 10 Jul: I SS Panzer Corps is possible only (the end is inferred, change undated; the last listing is 9 Jul)', a[('GER-SSPZ-001C', 'assigned')][0], 'possible')
    a = intervals(lehr, '1944-07-15')
    expect(s + ': Panzer Lehr, 15 Jul: Seventh Army (unspecified_subordination) is possible', a[('GER-ARMY-007A', 'unspecified_subordination')][0], 'possible')
    expect(s + ': Panzer Lehr, 15 Jul: the I SS Panzer Corps interval no longer applies', ('GER-SSPZ-001C', 'assigned') in a, False)
    a = intervals(lehr, '1944-07-25')
    expect(s + ': Panzer Lehr, 25 Jul (Cobra): LXXXIV Corps is certain', a[('GER-COR-084C', 'unspecified_subordination')][0], 'certain')
    expect(s + ': Panzer Lehr, 25 Jul: the chain is LXXXIV Corps, Seventh Army, Army Group B', [x[0] for x in chain(lehr, '1944-07-25')][:3], ['German LXXXIV Corps', 'German Seventh Army', 'German Army Group B'])
    a = intervals(pz47, '1944-08-10')
    expect(s + ': XLVII Panzer Corps, 10 Aug: Seventh Army is possible (end between 7 and 11 Aug)', a[('GER-ARMY-007A', 'unspecified_subordination')][0], 'possible')
    a = intervals(pz47, '1944-08-15')
    expect(s + ': XLVII Panzer Corps, 15 Aug: Panzer Group Eberbach is the only parent (possible)', sorted(a), [('GER-PZG-EBERB', 'unspecified_subordination')])
    expect(s + ': XLVII Panzer Corps, 15 Aug: ... and it is possible, not certain', a[('GER-PZG-EBERB', 'unspecified_subordination')][0], 'possible')
    a = intervals(pz47, '1944-08-19')
    expect(s + ': XLVII Panzer Corps, 19 Aug: back under the Seventh Army (possible: the start hour is undocumented)', a[('GER-ARMY-007A', 'unspecified_subordination')][0], 'possible')
    a = intervals(ss12, '1944-08-20')
    expect(s + ': 12th SS Panzer Division, 20 Aug: LXXXIV Corps (possible) and no I SS Panzer Corps interval', sorted(a), [('GER-COR-084C', 'unspecified_subordination')])
    a = intervals(d352, '1944-07-20')
    expect(s + ': 352nd Division, 20 Jul: the LXXXIV Corps assignment no longer applies (German Batch 1b moved its end to 10 Jul)', ('GER-COR-084C', 'assigned') in a, False)
    expect(s + ': 352nd Division, 20 Jul: the II Parachute Corps is certain (start moved to 11 Jul)', a[('GER-FJ-002C', 'unspecified_subordination')][0], 'certain')


def scenario_7_german_batch_1b_july_1944():
    """German Batch 1b (3 to 18 July 1944): relations that no source dates are possible; a relation listed on the day is certain."""
    s = 'scenario 7, German Batch 1b July 1944'
    a = intervals('GER-INF-352D', '1944-07-10')
    expect(s + ': 352nd Division, 10 Jul: LXXXIV Corps is possible (end between 17 Jun and 10 Jul, undated)', a[('GER-COR-084C', 'assigned')][0], 'possible')
    a = intervals('GER-INF-352D', '1944-07-11')
    expect(s + ': 352nd Division, 11 Jul: II Parachute Corps is possible (it starts that day at an undocumented hour)', a[('GER-FJ-002C', 'unspecified_subordination')][0], 'possible')
    a = intervals('GER-SSPG-017D', '1944-07-03')
    expect(s + ': 17th SS Panzer Grenadier Division, 3 Jul: II Parachute Corps is possible (end inferred)', a[('GER-FJ-002C', 'assigned')][0], 'possible')
    a = intervals('GER-SSPG-017D', '1944-07-20')
    expect(s + ': 17th SS Panzer Grenadier Division, 20 Jul: LXXXIV Corps is certain', a[('GER-COR-084C', 'unspecified_subordination')][0], 'certain')
    a = intervals('GER-SSPZ-001D', '1944-07-12')
    expect(s + ': 1st SS Panzer Division, 12 Jul: I SS Panzer Corps is certain', a[('GER-SSPZ-001C', 'assigned')][0], 'certain')
    a = intervals('GER-SSPZ-001D', '1944-08-10')
    expect(s + ': 1st SS Panzer Division, 10 Aug: XLVII Panzer Corps only (the I SS Panzer Corps relation ended 5 Aug)', sorted(a), [('GER-PZ-047C', 'unspecified_subordination')])
    a = intervals('GER-INF-353D', '1944-07-10')
    expect(s + ': 353rd Division, 10 Jul: LXXXIV Corps is possible (end between 3 and 23 Jul)', a[('GER-COR-084C', 'assigned')][0], 'possible')
    a = intervals('GER-SSPZ-002D', '1944-07-04')
    expect(s + ': 2nd SS Panzer Division, 4 Jul: Seventh Army reserve is possible (end between 3 and 5 Jul)', a[('GER-ARMY-007A', 'reserve')][0], 'possible')
    expect(s + ': 2nd SS Panzer Division, 10 Jul: no parent is recorded', intervals('GER-SSPZ-002D', '1944-07-10'), {})
    a = intervals('GER-INF-272D', '1944-07-11')
    expect(s + ': 272nd Division, 11 Jul: I SS Panzer Corps is certain', a[('GER-SSPZ-001C', 'assigned')][0], 'certain')
    a = intervals('GER-INF-272D', '1944-07-20')
    expect(s + ': 272nd Division, 20 Jul: I SS Panzer Corps is possible (4 days after the last listing)', a[('GER-SSPZ-001C', 'assigned')][0], 'possible')
    a = intervals('GER-INF-346D', '1944-07-20')
    expect(s + ': 346th Division, 20 Jul: LXXXVI Corps is possible (month-level start)', a[('GER-COR-086C', 'assigned')][0], 'possible')


def scenario_8_german_batch_2_sep_oct_1944():
    """German Batch 2 (September-October 1944): a parent shown on a dated row is certain on that day; a parent that is only closed by inference is possible; an old parent that the next row replaces no longer applies."""
    s = 'scenario 8, German Batch 2 September-October 1944'
    a = intervals('GER-PZ-021D', '1944-09-20')
    expect(s + ': 21st Panzer Division, 20 Sep: I SS Panzer Corps is possible only (CR0038 closed by inference on that day)', a[('GER-SSPZ-001C', 'assigned')][0], 'possible')
    expect(s + ': 21st Panzer Division, 20 Sep: XLVII Panzer Corps does not apply yet', ('GER-PZ-047C', 'assigned') in a, False)
    a = intervals('GER-PZ-021D', '1944-09-21')
    expect(s + ': 21st Panzer Division, 21 Sep (C0878, CMH ch. 5 p. 233): XLVII Panzer Corps is certain', a[('GER-PZ-047C', 'assigned')][0], 'certain')
    expect(s + ': 21st Panzer Division, 21 Sep: the I SS Panzer Corps interval no longer applies', ('GER-SSPZ-001C', 'assigned') in a, False)
    a = intervals('GER-PZ-021D', '1944-09-30')
    expect(s + ': 21st Panzer Division, 30 Sep: XLVII Panzer Corps is possible (8 days after the last listing)', a[('GER-PZ-047C', 'assigned')][0], 'possible')
    a = intervals('GER-SSPZ-009D', '1944-09-17')
    expect(s + ': 9th SS Panzer Division, 17 Sep: II SS Panzer Corps is certain (CMH ch. 7 p. 142)', a[('GER-SSPZ-002C', 'assigned')][0], 'certain')
    a = intervals('GER-SSPZ-010D', '1944-09-17')
    expect(s + ': 10th SS Panzer Division, 17 Sep: II SS Panzer Corps is certain (CMH ch. 7 p. 164)', a[('GER-SSPZ-002C', 'assigned')][0], 'certain')
    a = intervals('GER-PG-003D', '1944-09-12')
    expect(s + ': 3rd Panzer Grenadier Division, 12 Sep: First Army is certain (CMH ch. 2 p. 80 and ch. 1 p. 49)', a[('GER-ARMY-001A', 'assigned')][0], 'certain')
    a = intervals('GER-INF-059D', '1944-09-12')
    expect(s + ': 59th Division, 12 Sep: First Parachute Army is possible (Model\'s directive of 12 Sep is stated by the row of 17 Sep)', a[('GER-FJA-001A', 'assigned')][0], 'possible')
    expect(s + ': 59th Division, 11 Sep: no parent is recorded', intervals('GER-INF-059D', '1944-09-11'), {})
    a = intervals('GER-VG-559D', '1944-09-27')
    expect(s + ': 559th Division, 27 Sep: XIII SS Corps is certain (CMH ch. 5 p. 245-246)', a[('GER-SSCOR-013C', 'assigned')][0], 'certain')
    a = intervals('GER-PZ-116D', '1944-10-14')
    expect(s + ': 116th Panzer Division, 14 Oct: LXXXI Corps is possible only (the next listing, 15 Oct, is month-level)', a[('GER-COR-081C', 'assigned')][0], 'possible')
    a = intervals('GER-PZ-116D', '1944-10-15')
    expect(s + ': 116th Panzer Division, 15 Oct: I SS Panzer Corps (Lexikon, month-level row) and LXXXI Corps no longer applies', sorted(a), [('GER-SSPZ-001C', 'assigned')])
    a = intervals('GER-VG-246D', '1944-10-12')
    expect(s + ': 246th Division, 12 Oct: LXXXI Corps is certain (CMH ch. 12 p. 283)', a[('GER-COR-081C', 'assigned')][0], 'certain')
    expect(s + ': 21st Panzer Division, 22 Sep: the chain starts with the XLVII Panzer Corps', [x[0] for x in chain('GER-PZ-021D', '1944-09-22')][:1], ['German XLVII Panzer Corps'])


def scenario_9_german_batch_2_followup_model_lxxx():
    """German Batch 2 follow-up (Army Group B and the LXXX Corps): a transfer that only a narrative dates leaves the old parent possible on the day and the new one possible on the first day; units shown under the corps on a dated order of battle are certain on that day; the end of Army Group B closes its relation to OB West."""
    s = 'scenario 9, German Batch 2 follow-up (Model and the LXXX Corps)'
    L = 'GER-COR-080C'
    a = intervals(L, '1944-09-14')
    expect(s + ': LXXX Corps, 14 Sep: First Army is certain (CMH ch. 3 p. 42, 57 and the order of battle of 16 Sep)', a[('GER-ARMY-001A', 'assigned')][0], 'certain')
    a = intervals(L, '1944-09-17')
    expect(s + ': LXXX Corps, 17 Sep: First Army is possible only (closed by inference the day before the transfer row)', a[('GER-ARMY-001A', 'assigned')][0], 'possible')
    expect(s + ': LXXX Corps, 17 Sep: the Seventh Army does not apply yet', ('GER-ARMY-007A', 'assigned') in a, False)
    a = intervals(L, '1944-09-18')
    expect(s + ': LXXX Corps, 18 Sep (CMH ch. 3 p. 63, Lexikon): Seventh Army is possible on the first day', a[('GER-ARMY-007A', 'assigned')][0], 'possible')
    a = intervals(L, '1944-09-20')
    expect(s + ': LXXX Corps, 20 Sep: Seventh Army is certain (between listings)', a[('GER-ARMY-007A', 'assigned')][0], 'certain')
    expect(s + ': LXXX Corps, 20 Sep: the First Army no longer applies', ('GER-ARMY-001A', 'assigned') in a, False)
    a = intervals(L, '1944-12-16')
    expect(s + ': LXXX Corps, 16 Dec (CMH Ardennes ch. 9 p. 212-213): Seventh Army is certain', a[('GER-ARMY-007A', 'assigned')][0], 'certain')
    a = intervals(L, '1945-03-20')
    expect(s + ': LXXX Corps, 20 Mar 1945: Seventh Army is possible only (transfer in the night of 20 March, CMH ch. 12 p. 260)', a[('GER-ARMY-007A', 'assigned')][0], 'possible')
    a = intervals(L, '1945-03-22')
    expect(s + ': LXXX Corps, 22 Mar 1945 (CMH ch. 12 p. 263): First Army is certain', a[('GER-ARMY-001A', 'assigned')][0], 'certain')
    expect(s + ': LXXX Corps, 22 Mar 1945: the Seventh Army no longer applies', ('GER-ARMY-007A', 'assigned') in a, False)
    a = intervals(L, '1945-04-19')
    expect(s + ': LXXX Corps, 19 Apr 1945 (CMH ch. 18 p. 428): Nineteenth Army is certain', a[('GER-ARMY-019A', 'assigned')][0], 'certain')
    expect(s + ': LXXX Corps, 20 Sep: the chain runs Seventh Army, Army Group B, OB West', [x[0] for x in chain(L, '1944-09-20')][:3], ['German Seventh Army', 'German Army Group B', 'German Oberbefehlshaber West (OB West)'])
    expect(s + ': LXXX Corps, 25 Mar 1945: the chain starts with the First Army and Army Group G', [x[0] for x in chain(L, '1945-03-25')][:2], ['German First Army (Germany)', 'German Army Group G (Heeresgruppe G; Armeegruppe G until late 1944)'])
    a = intervals('GER-ARMY-007A', '1945-03-01')
    expect(s + ': Seventh Army, 1 Mar 1945: Army Group B is possible (closed on the day before the transfer of 2 March, CMH ch. 10 p. 198)', a[('GER-AG-00BG', 'assigned')][0], 'possible')
    a = intervals('GER-ARMY-007A', '1945-03-03')
    expect(s + ': Seventh Army, 3 Mar 1945: Army Group G is possible and Army Group B no longer applies', sorted(a), [('GER-AG-00GG', 'assigned')])
    a = intervals('GER-FJ-005D', '1944-09-15')
    expect(s + ': 5th Fallschirmjäger Division, 15 Sep: First Parachute Army is possible only (CR0630 closed by inference)', a[('GER-FJA-001A', 'assigned')][0], 'possible')
    a = intervals('GER-FJ-005D', '1944-09-16')
    expect(s + ': 5th Fallschirmjäger Division, 16 Sep (order of battle, CMH ch. 3 p. 42): LXXX Corps is certain', a[('GER-COR-080C', 'assigned')][0], 'certain')
    expect(s + ': 5th Fallschirmjäger Division, 16 Sep: the First Parachute Army no longer applies', ('GER-FJA-001A', 'assigned') in a, False)
    a = intervals('GER-PZ-LEHRD', '1944-09-16')
    expect(s + ': Panzer Lehr Division, 16 Sep: LXXX Corps is certain', a[('GER-COR-080C', 'assigned')][0], 'certain')
    a = intervals('GER-INF-353D', '1944-11-26')
    expect(s + ': 353rd Infantry Division, 26 Nov (order of battle): LXXX Corps is certain', a[('GER-COR-080C', 'assigned')][0], 'certain')
    expect(s + ': 212th Infantry Division, 25 Nov: no parent is recorded', intervals('GER-VG-212D', '1944-11-25'), {})
    a = intervals('GER-VG-212D', '1944-12-16')
    expect(s + ': 212th Volksgrenadier Division, 16 Dec (CMH Ardennes ch. 9 p. 213): LXXX Corps is certain', a[('GER-COR-080C', 'assigned')][0], 'certain')
    a = intervals('GER-VG-276D', '1944-12-16')
    expect(s + ': 276th Volksgrenadier Division, 16 Dec (CMH Ardennes ch. 9 p. 229): LXXX Corps is certain', a[('GER-COR-080C', 'assigned')][0], 'certain')
    a = intervals('GER-AG-00BG', '1945-04-16')
    expect(s + ': Army Group B, 16 Apr 1945: OB West is certain', a[('GER-OBW-000H', 'assigned')][0], 'certain')
    a = intervals('GER-AG-00BG', '1945-04-17')
    expect(s + ': Army Group B, 17 Apr 1945 (dissolution, CMH The Last Offensive ch. 16 p. 369): OB West is possible on the last day', a[('GER-OBW-000H', 'assigned')][0], 'possible')
    expect(s + ': Army Group B, 18 Apr 1945: no parent is recorded', intervals('GER-AG-00BG', '1945-04-18'), {})


def scenario_10_german_batch_3_nov_dec_1944():
    """German Batch 3 (1 November to 31 December 1944): a relation that a dated row supersedes is possible only until the day before that row; units shown under a command on a sourced day are certain on that day; a later Ardennes row closes a November relation the day before it; the deception Fifteenth Army in the Netherlands is the Twenty-fifth Army, so the Netherlands corps does not appear under the real Fifteenth Army."""
    s = 'scenario 10, German Batch 3 (November and December 1944)'
    a = intervals('GER-PZ-058C', '1944-10-31')
    expect(s + ': LVIII Panzer Corps, 31 Oct: Fifth Panzer Army is possible only (end between the last listing and 31 Oct)', a[('GER-PZA-005A', 'assigned')][0], 'possible')
    a = intervals('GER-PZ-058C', '1944-11-01')
    expect(s + ': LVIII Panzer Corps, 1 Nov (CMH Lorraine ch. 7 p. 312, Lexikon): Seventh Army is certain', a[('GER-ARMY-007A', 'assigned')][0], 'certain')
    expect(s + ': LVIII Panzer Corps, 1 Nov: the Fifth Panzer Army no longer applies', ('GER-PZA-005A', 'assigned') in a, False)
    a = intervals('GER-PZ-058C', '1944-11-20')
    expect(s + ': LVIII Panzer Corps, 20 Nov: Seventh Army is possible only (between two listings, end inferred)', a[('GER-ARMY-007A', 'assigned')][0], 'possible')
    a = intervals('GER-PZ-058C', '1944-12-16')
    expect(s + ': LVIII Panzer Corps, 16 Dec (CMH Ardennes ch. 8 p. 195, Nafziger): Fifth Panzer Army is certain', a[('GER-PZA-005A', 'assigned')][0], 'certain')
    expect(s + ': LVIII Panzer Corps, 16 Dec: the Seventh Army no longer applies', ('GER-ARMY-007A', 'assigned') in a, False)
    a = intervals('GER-COR-089C', '1944-11-01')
    expect(s + ': LXXXIX Corps, 1 Nov (CMH Lorraine ch. 7 p. 312, Lexikon): First Army is certain', a[('GER-ARMY-001A', 'assigned')][0], 'certain')
    a = intervals('GER-COR-089C', '1944-12-08')
    expect(s + ': LXXXIX Corps, 8 Dec (CMH Riviera ch. 26 p. 467): Army Group G is certain and the First Army no longer applies', sorted(a), [('GER-AG-00GG', 'assigned')])
    a = intervals('GER-COR-085C', '1944-11-07')
    expect(s + ': LXXXV Corps, 7 Nov (CMH Riviera ch. 20 p. 362): Nineteenth Army is certain', a[('GER-ARMY-019A', 'assigned')][0], 'certain')
    a = intervals('GER-COR-085C', '1944-12-16')
    expect(s + ': LXXXV Corps, 16 Dec: Seventh Army is certain and the Nineteenth Army no longer applies', sorted(a), [('GER-ARMY-007A', 'assigned')])
    a = intervals('GER-PZ-LEHRD', '1944-11-23')
    expect(s + ': Panzer Lehr Division, 23 Nov (CMH Lorraine ch. 10 p. 464): First Army is certain and the LXXX Corps no longer applies', sorted(a), [('GER-ARMY-001A', 'assigned')])
    a = intervals('GER-PZ-LEHRD', '1944-12-16')
    expect(s + ': Panzer Lehr Division, 16 Dec: XLVII Panzer Corps is certain and the First Army no longer applies', sorted(a), [('GER-PZ-047C', 'assigned')])
    a = intervals('GER-PZ-011D', '1944-11-10')
    expect(s + ': 11th Panzer Division, 10 Nov (CMH Lorraine ch. 7 p. 328): First Army reserve is certain', a[('GER-ARMY-001A', 'reserve')][0], 'certain')
    a = intervals('GER-PZ-021D', '1944-11-13')
    expect(s + ': 21st Panzer Division, 13 Nov (CMH Lorraine ch. 7 p. 365): XIII SS Corps is certain', a[('GER-SSCOR-013C', 'assigned')][0], 'certain')
    a = intervals('GER-INF-338D', '1944-11-07')
    expect(s + ': 338th Infantry Division, 7 Nov (CMH Riviera ch. 20 p. 362): LXXXV Corps is certain', a[('GER-COR-085C', 'assigned')][0], 'certain')
    expect(s + ': 338th Infantry Division, 7 Nov: the chain runs LXXXV Corps, Nineteenth Army, Army Group G', [x[0] for x in chain('GER-INF-338D', '1944-11-07')][:3], ['German LXXXV Corps (Generalkommando Knieß until July 1944)', 'German Nineteenth Army (Germany)', 'German Army Group G (Heeresgruppe G; Armeegruppe G until late 1944)'])
    a = intervals('GER-ARMY-019A', '1944-11-27')
    expect(s + ': Nineteenth Army, 27 Nov (CMH Riviera ch. 24 p. 437): Army Group G is certain', a[('GER-AG-00GG', 'assigned')][0], 'certain')
    a = intervals('GER-ARMY-019A', '1944-12-15')
    expect(s + ': Nineteenth Army, 15 Dec (CMH Riviera ch. 26 p. 485, Lexikon): Army Group Oberrhein is certain and Army Group G no longer applies', sorted(a), [('GER-AG-OBRHG', 'assigned')])
    a = intervals('GER-COR-064C', '1944-11-07')
    expect(s + ': LXIV Corps, 7 Nov (CMH Riviera ch. 20 p. 362): Nineteenth Army is certain', a[('GER-ARMY-019A', 'assigned')][0], 'certain')
    a = intervals('GER-INF-198D', '1944-11-10')
    expect(s + ': 198th Infantry Division, 10 Nov (CMH Riviera ch. 22 p. 391): IV Luftwaffe Field Corps is certain', a[('GER-LFC-004C', 'assigned')][0], 'certain')
    a = intervals('GER-FJA-001A', '1944-11-10')
    expect(s + ': First Parachute Army, 10 Nov (CMH Siegfried ch. 17 p. 395): Army Group H is certain', a[('GER-AG-00HG', 'assigned')][0], 'certain')
    a = intervals('GER-INF-070D', '1944-11-06')
    expect(s + ': 70th Infantry Division, 6 Nov (CMH Siegfried ch. 9 p. 229): Fifteenth Army is certain', a[('GER-ARMY-015A', 'assigned')][0], 'certain')
    a = intervals('GER-COR-088C', '1944-11-10')
    expect(s + ': LXXXVIII Corps, 10 Nov (Lexikon table, CMH ch. 17 p. 395): the Twenty-fifth Army is certain and the real Fifteenth Army does not apply', sorted(a), [('GER-ARMY-025A', 'assigned')])
    a = intervals('GER-COR-FELDT', '1944-12-09')
    expect(s + ': Korps Feldt, 9 Dec (Lexikon): First Parachute Army is certain', a[('GER-FJA-001A', 'assigned')][0], 'certain')
    a = intervals('GER-ARMY-015A', '1944-11-15')
    expect(s + ': Fifteenth Army, 15 Nov (CMH ch. 17 p. 395): Army Group B is certain', a[('GER-AG-00BG', 'assigned')][0], 'certain')


def scenario_11_german_1945_batch_1_jan_mar():
    """German 1945 Batch 1 (1 January to 31 March 1945): a dated row closes the earlier relation the day before it; the corps and armies move between army groups on the sourced day (Nordwind, the Colmar Pocket, the Rhineland); the Nineteenth Army ends under OB West; a corps under the Seventh Army moves to the Fifteenth Army on the day of the command change."""
    s = 'scenario 11, German 1945 Batch 1 (January to March 1945)'
    a = intervals('GER-SSPZ-001C', '1945-01-03')
    expect(s + ': I SS Panzer Corps, 3 Jan: Sixth Panzer Army is possible only (end inferred before the 4 Jan row)', a[('GER-PZA-006A', 'assigned')][0], 'possible')
    a = intervals('GER-SSPZ-001C', '1945-01-04')
    expect(s + ': I SS Panzer Corps, 4 Jan: Fifth Panzer Army is certain and the Sixth Panzer Army no longer applies', sorted(a), [('GER-PZA-005A', 'assigned')])
    a = intervals('GER-PZ-039C', '1945-01-09')
    expect(s + ': XXXIX Panzer Corps, 9 Jan (Nordwind): Army Group G is certain', a[('GER-AG-00GG', 'assigned')][0], 'certain')
    a = intervals('GER-PZ-039C', '1945-01-12')
    expect(s + ': XXXIX Panzer Corps, 12 Jan: Army Group Oberrhein is certain and Army Group G no longer applies', sorted(a), [('GER-AG-OBRHG', 'assigned')])
    a = intervals('GER-PZ-021D', '1945-01-07')
    expect(s + ': 21st Panzer Division, 7 Jan: XXXIX Panzer Corps is certain', sorted(a), [('GER-PZ-039C', 'assigned')])
    a = intervals('GER-PZ-021D', '1945-01-12')
    expect(s + ': 21st Panzer Division, 12 Jan: LXXXIX Corps is certain', sorted(a), [('GER-COR-089C', 'assigned')])
    a = intervals('GER-ARMY-019A', '1945-01-20')
    expect(s + ': Nineteenth Army, 20 Jan (Colmar Pocket): Army Group Oberrhein is certain', a[('GER-AG-OBRHG', 'assigned')][0], 'certain')
    a = intervals('GER-ARMY-019A', '1945-01-29')
    expect(s + ': Nineteenth Army, 29 Jan: Army Group G is certain and Army Group Oberrhein no longer applies', sorted(a), [('GER-AG-00GG', 'assigned')])
    a = intervals('GER-ARMY-019A', '1945-03-02')
    expect(s + ': Nineteenth Army, 2 Mar (CMH Last Offensive ch. 12 p. 237, Lexikon): OB West is certain and Army Group G no longer applies', sorted(a), [('GER-OBW-000H', 'assigned')])
    a = intervals('GER-INF-338D', '1945-01-20')
    expect(s + ': 338th Infantry Division, 20 Jan: LXIII Corps is certain', a[('GER-COR-063C', 'assigned')][0], 'certain')
    a = intervals('GER-INF-338D', '1945-02-25')
    expect(s + ': 338th Infantry Division, 25 Feb: XII SS Corps is certain and the LXIII Corps no longer applies', sorted(a), [('GER-SSCOR-012C', 'assigned')])
    a = intervals('GER-COR-053C', '1945-03-05')
    expect(s + ': LIII Corps, 5 Mar: Seventh Army is possible only (end inferred before the 6 Mar row)', a[('GER-ARMY-007A', 'assigned')][0], 'possible')
    a = intervals('GER-COR-053C', '1945-03-06')
    expect(s + ': LIII Corps, 6 Mar: Fifteenth Army is certain and the Seventh Army no longer applies', sorted(a), [('GER-ARMY-015A', 'assigned')])
    a = intervals('GER-ARMY-001A', '1945-03-23')
    expect(s + ': First Army, 23 Mar: Army Group G is certain', a[('GER-AG-00GG', 'assigned')][0], 'certain')
    a = intervals('GER-PZA-005A', '1945-01-22')
    expect(s + ': Fifth Panzer Army, 22 Jan: Army Group B is certain', a[('GER-AG-00BG', 'assigned')][0], 'certain')


def scenario_12_german_1945_batch_2_apr_may():
    """German 1945 Batch 2 (1 April to 8 May 1945): the Ruhr pocket closes the relations of the surrendered commands on the sourced day (13, 17, 18 April) and leaves nothing open for them afterwards; Army Group H becomes OB Nordwest under OKW on 6 April; the Eleventh and Twelfth Armies and the improvised divisions start and end on the sourced days; the Seventh and Nineteenth Armies change commander between OB West and Army Group G."""
    s = 'scenario 12, German 1945 Batch 2 (April to May 1945)'
    a = intervals('GER-ARMY-015A', '1945-04-12')
    expect(s + ': Fifteenth Army, 12 Apr (CMH Last Offensive ch. 16 p. 359): Army Group B is certain', a[('GER-AG-00BG', 'assigned')][0], 'certain')
    a = intervals('GER-ARMY-015A', '1945-04-14')
    expect(s + ': Fifteenth Army, 14 Apr (surrender 13 Apr, CMH ch. 16 p. 370, Lexikon): no relation applies', sorted(a), [])
    a = intervals('GER-COR-081C', '1945-04-14')
    expect(s + ': LXXXI Corps, 14 Apr (surrender 13 Apr): no relation applies', sorted(a), [])
    a = intervals('GER-PZA-005A', '1945-04-16')
    expect(s + ': Fifth Panzer Army, 16 Apr: Army Group B is certain', a[('GER-AG-00BG', 'assigned')][0], 'certain')
    a = intervals('GER-PZA-005A', '1945-04-18')
    expect(s + ': Fifth Panzer Army, 18 Apr (ended 17 Apr, Lexikon, CMH ch. 16 p. 370): no relation applies', sorted(a), [])
    a = intervals('GER-AA-LUETTW', '1945-04-17')
    expect(s + ': Gruppe von Luettwitz, 17 Apr (CMH ch. 16 p. 358-359): Army Group B is certain', a[('GER-AG-00BG', 'assigned')][0], 'certain')
    a = intervals('GER-AA-LUETTW', '1945-04-19')
    expect(s + ': Gruppe von Luettwitz, 19 Apr (end of resistance 18 Apr, CMH ch. 16 p. 372): no relation applies', sorted(a), [])
    a = intervals('GER-PZ-047C', '1945-04-19')
    expect(s + ': XLVII Panzer Corps, 19 Apr: no relation applies', sorted(a), [])
    a = intervals('GER-AG-00HG', '1945-04-06')
    expect(s + ': Army Group H, 6 Apr (CMH ch. 17 p. 385, Lexikon): OKW is certain', a[('GER-OKW-000H', 'assigned')][0], 'certain')
    a = intervals('GER-FJA-001A', '1945-04-10')
    expect(s + ': First Parachute Army, 10 Apr (Lexikon): OB Nordwest (Army Group H) is certain', a[('GER-AG-00HG', 'assigned')][0], 'certain')
    a = intervals('GER-ARMY-BLUMT', '1945-04-06')
    expect(s + ': Army Blumentritt, 6 Apr (CMH ch. 17 p. 385): OB Nordwest (Army Group H) is certain', a[('GER-AG-00HG', 'assigned')][0], 'certain')
    a = intervals('GER-ARMY-011A', '1945-04-22')
    expect(s + ': Eleventh Army, 22 Apr (Lexikon, CMH ch. 17 p. 405): OB West is certain', a[('GER-OBW-000H', 'assigned')][0], 'certain')
    a = intervals('GER-ARMY-011A', '1945-04-24')
    expect(s + ': Eleventh Army, 24 Apr (captured 23 Apr near Blankenburg): no relation applies', sorted(a), [])
    a = intervals('GER-ARMY-012A', '1945-04-10')
    expect(s + ': Twelfth Army, 10 Apr (Lexikon): OB West is certain', a[('GER-OBW-000H', 'assigned')][0], 'certain')
    a = intervals('GER-PZ-CLAUS', '1945-04-20')
    expect(s + ': Panzer Division von Clausewitz, 20 Apr (CMH ch. 17 p. 399-400): Twelfth Army is certain', a[('GER-ARMY-012A', 'assigned')][0], 'certain')
    a = intervals('GER-PZ-CLAUS', '1945-04-22')
    expect(s + ': Panzer Division von Clausewitz, 22 Apr (destroyed 21 Apr): no relation applies', sorted(a), [])
    a = intervals('GER-ARMY-007A', '1945-04-27')
    expect(s + ': Seventh Army, 27 Apr: Army Group G is possible only (end inferred before the 28 Apr row)', a[('GER-AG-00GG', 'assigned')][0], 'possible')
    a = intervals('GER-ARMY-007A', '1945-04-28')
    expect(s + ': Seventh Army, 28 Apr (CMH ch. 18): OB West is certain and Army Group G no longer applies', sorted(a), [('GER-OBW-000H', 'assigned')])
    a = intervals('GER-ARMY-019A', '1945-04-26')
    expect(s + ': Nineteenth Army, 26 Apr (Lexikon): Army Group G is certain', a[('GER-AG-00GG', 'assigned')][0], 'certain')
    a = intervals('GER-ARMY-024A', '1945-04-22')
    expect(s + ': Twenty-fourth Army, 22 Apr (CMH ch. 18 p. 434): the Nineteenth Army is possible only (an attachment with no sourced end)', a[('GER-ARMY-019A', 'attached')][0], 'possible')


def scenario_13_cleanup_open_items_oct28():
    """Clean-up of open items (28 October 2026): the conflict groups G021 to G025 (G022 and G024 settled, the rest open), the 243rd Division flags and the parent of the 353rd Division."""
    s = 'scenario 13, clean-up of open items (28 October 2026)'
    claims = {c['claim_id']: c for c in common.load_all_claims()[1]}
    status = lambda ids: [claims[i]['claim_status'] for i in ids]
    expect(s + ': G021 (Army Group B, Kluge): C0714 preferred, C0767 alternate (open, new Lexikon evidence in the notes)', status(['C0714', 'C0767']), ['preferred', 'alternate'])
    expect(s + ': G022 (Panzer Lehr): C0792 (dated list of 15 July) preferred, the June and Feldgrau month rows alternate', status(['C0792', 'C0790', 'C0791']), ['preferred', 'alternate', 'alternate'])
    expect(s + ': G023 (12th SS Panzer Division): still no winner', status(['C0782', 'C0783']), ['disputed', 'disputed'])
    expect(s + ': G024 (716th Division): C0815 (Lexikon text, southern France by 10 July) preferred, the Normandy table row alternate', status(['C0815', 'C0816']), ['preferred', 'alternate'])
    expect(s + ': G025 (711th Division): still no winner', status(['C0817', 'C0818']), ['disputed', 'disputed'])
    c = claims['C0197']
    expect(s + ': 243rd Division, C0197 (29 June): elements surrendered at Cherbourg, the division is not flagged destroyed or disestablished', (c['event_type'], c['destroyed'], c['disestablished']), ('surrender', 'false', 'false'))
    a = intervals('GER-INF-353D', '1944-09-20')
    expect(s + ': 353rd Division, 20 Sep (CMH Siegfried Line ch. 4 p. 87, 92): the LXXIV Corps is the parent, not the LXXXIV Corps', sorted(a), [('GER-COR-074C', 'assigned')])


def scenario_14_canadian_batch_1_jun_dec_1944():
    """Canadian Batch 1 (July to December 1944): same-day handovers at a recorded hour (3rd Division to II Canadian Corps at 15:00 on 11 July, I Corps to First Canadian Army at noon on 23 July, II Canadian Corps to the Army at noon on 31 July); the temporary attachments of the 2nd Division (26 September to midnight 6-7 October) and the 4th Armoured Division (from midnight 17-18 October) to I Corps; the 4th Armoured Division in Army Reserve in December."""
    s = 'scenario 14, Canadian Batch 1 (July to December 1944)'
    a = intervals('CAN-INF-003D', '1944-07-10')
    expect(s + ': 3rd Division, 10 Jul: I Corps is certain (Stacey p. 146, Montgomery told Dempsey to place the division under 2nd Corps only later)', sorted(a), [('UK-COR-001C', 'assigned')])
    a = intervals('CAN-INF-003D', '1944-07-11', '12:00')
    expect(s + ': 3rd Division, 11 Jul 12:00: I Corps is still certain', sorted(a), [('UK-COR-001C', 'assigned')])
    a = intervals('CAN-INF-003D', '1944-07-11', '16:00')
    expect(s + ': 3rd Division, 11 Jul 16:00 (Stacey p. 166, 3:00 p.m.): II Canadian Corps is certain and I Corps no longer applies', sorted(a), [('CAN-COR-002C', 'assigned')])
    a = intervals('CAN-INF-003D', '1944-07-11')
    expect(s + ': 3rd Division, 11 Jul without an hour: both corps are possible only', sorted(a), [('CAN-COR-002C', 'assigned'), ('UK-COR-001C', 'assigned')])
    expect(s + ': 3rd Division, 11 Jul without an hour: I Corps is possible', a[('UK-COR-001C', 'assigned')][0], 'possible')
    a = intervals('UK-COR-001C', '1944-07-23', '11:00')
    expect(s + ': I Corps, 23 Jul 11:00: Second Army is certain', sorted(a), [('UK-ARMY-002A', 'assigned')])
    a = intervals('UK-COR-001C', '1944-07-23', '13:00')
    expect(s + ': I Corps, 23 Jul 13:00 (Stacey p. 196, noon): First Canadian Army is certain and Second Army no longer applies', sorted(a), [('CAN-ARMY-001A', 'assigned')])
    a = intervals('CAN-COR-002C', '1944-07-20')
    expect(s + ': II Canadian Corps, 20 Jul: Second Army is certain', sorted(a), [('UK-ARMY-002A', 'assigned')])
    a = intervals('CAN-COR-002C', '1944-07-31', '13:00')
    expect(s + ': II Canadian Corps, 31 Jul 13:00 (Stacey pp. 200-201, noon): First Canadian Army is certain', sorted(a), [('CAN-ARMY-001A', 'assigned')])
    a = intervals('CAN-COR-002C', '1944-08-05')
    expect(s + ': II Canadian Corps, 5 Aug: First Canadian Army is certain', sorted(a), [('CAN-ARMY-001A', 'assigned')])
    a = intervals('CAN-INF-002D', '1944-09-27')
    expect(s + ': 2nd Division, 27 Sep (Stacey p. 367): II Canadian Corps assigned and I Corps attached, both certain', sorted(a), [('CAN-COR-002C', 'assigned'), ('UK-COR-001C', 'attached')])
    a = intervals('CAN-INF-002D', '1944-10-08')
    expect(s + ': 2nd Division, 8 Oct (Stacey p. 381, midnight 6-7 October): the attachment to I Corps has ended', sorted(a), [('CAN-COR-002C', 'assigned')])
    a = intervals('CAN-INF-002D', '1944-07-10')
    expect(s + ': 2nd Division, 10 Jul: no relation yet (the corps took over on 11 July)', sorted(a), [])
    a = intervals('CAN-ARM-004D', '1944-08-01')
    expect(s + ': 4th Armoured Division, 1 Aug (Stacey p. 202): II Canadian Corps is certain', sorted(a), [('CAN-COR-002C', 'assigned')])
    a = intervals('CAN-ARM-004D', '1944-10-17', '12:00')
    expect(s + ': 4th Armoured Division, 17 Oct 12:00: not yet under I Corps', sorted(a), [('CAN-COR-002C', 'assigned')])
    a = intervals('CAN-ARM-004D', '1944-10-20')
    expect(s + ': 4th Armoured Division, 20 Oct (Stacey p. 390, midnight of 17 October): I Corps attached and II Canadian Corps assigned', sorted(a), [('CAN-COR-002C', 'assigned'), ('UK-COR-001C', 'attached')])
    a = intervals('CAN-ARM-004D', '1944-12-24')
    expect(s + ': 4th Armoured Division, 24 Dec (Stacey p. 443): the attachment to I Corps has ended and the Army Reserve relation applies', sorted(a), [('CAN-ARMY-001A', 'reserve'), ('CAN-COR-002C', 'assigned')])
    expect(s + ': 4th Armoured Division, 24 Dec: the Army Reserve relation is possible only', a[('CAN-ARMY-001A', 'reserve')][0], 'possible')
    a = intervals('CAN-ARMY-001A', '1944-07-25')
    expect(s + ': First Canadian Army, 25 Jul: 21st Army Group is certain', sorted(a), [('UK-AG-021G', 'assigned')])
    claims = {c['claim_id']: c for c in common.load_all_claims()[1]}
    c = claims['C1278']
    expect(s + ': C1278 is the minimal I Corps evidence claim of 23 July', (c['unit_id'], c['date'], c['event_type']), ('UK-COR-001C', '1944-07-23', 'command_change'))


def scenario_15_canadian_batch_2_jan_may_1945():
    """Canadian Batch 2 (January to May 1945): the Army takes the 30th Corps (Veritable) and loses it to Second Army on 8 March; I Canadian Corps joins from Italy at noon on 15 March and the 1st British Corps leaves the Army at noon on 2 April; II Canadian Corps is with Second Army from 20 March to 1 April (day only, then 23:59); the divisions attached to British corps and II Canadian Corps."""
    s = 'scenario 15, Canadian Batch 2 (January to May 1945)'
    a = intervals('UK-COR-001C', '1945-04-02', '11:00')
    expect(s + ': 1st British Corps, 2 Apr 11:00: First Canadian Army is certain (Stacey p. 545, noon)', sorted(a), [('CAN-ARMY-001A', 'assigned')])
    a = intervals('UK-COR-001C', '1945-04-02', '13:00')
    expect(s + ': 1st British Corps, 2 Apr 13:00: no Canadian relation any longer (the corps passes to Second Army in the British batch)', sorted(a), [])
    a = intervals('CAN-COR-001C', '1945-03-15', '11:00')
    expect(s + ': I Canadian Corps, 15 Mar 11:00: not yet in the theatre relation (Stacey p. 529, noon)', sorted(a), [])
    a = intervals('CAN-COR-001C', '1945-03-15', '13:00')
    expect(s + ': I Canadian Corps, 15 Mar 13:00: First Canadian Army is certain', sorted(a), [('CAN-ARMY-001A', 'assigned')])
    a = intervals('CAN-COR-002C', '1945-03-10')
    expect(s + ': II Canadian Corps, 10 Mar: First Canadian Army is certain', sorted(a), [('CAN-ARMY-001A', 'assigned')])
    a = intervals('CAN-COR-002C', '1945-03-20')
    expect(s + ': II Canadian Corps, 20 Mar (day only): the Army and Second Army are possible only', sorted(a), [('CAN-ARMY-001A', 'assigned'), ('UK-ARMY-002A', 'assigned')])
    a = intervals('CAN-COR-002C', '1945-03-25')
    expect(s + ': II Canadian Corps, 25 Mar: Second Army is certain', sorted(a), [('UK-ARMY-002A', 'assigned')])
    a = intervals('CAN-COR-002C', '1945-04-01', '23:30')
    expect(s + ': II Canadian Corps, 1 Apr 23:30 (Stacey p. 545, 23:59): Second Army is still certain', sorted(a), [('UK-ARMY-002A', 'assigned')])
    a = intervals('CAN-COR-002C', '1945-04-02')
    expect(s + ': II Canadian Corps, 2 Apr: First Canadian Army is certain', sorted(a), [('CAN-ARMY-001A', 'assigned')])
    a = intervals('UK-COR-030C', '1945-03-09')
    expect(s + ': 30th British Corps, 9 Mar: the attachment to the Army has ended (18:00 on 8 March, Stacey p. 521)', sorted(a), [('UK-ARMY-002A', 'assigned')])
    a = intervals('CAN-INF-003D', '1945-02-10')
    expect(s + ': 3rd Division, 10 Feb: II Canadian Corps assigned and 30th Corps attached (Stacey p. 471)', sorted(a), [('CAN-COR-002C', 'assigned'), ('UK-COR-030C', 'attached')])
    a = intervals('CAN-INF-003D', '1945-02-20')
    expect(s + ': 3rd Division, 20 Feb: the attachment to 30th Corps has ended on 15 February (Stacey p. 482)', sorted(a), [('CAN-COR-002C', 'assigned')])
    a = intervals('CAN-INF-003D', '1945-03-28', '13:00')
    expect(s + ': 3rd Division, 28 Mar 13:00: back under II Canadian Corps only (Stacey p. 539, noon)', sorted(a), [('CAN-COR-002C', 'assigned')])
    a = intervals('CAN-ARM-004D', '1945-01-24')
    expect(s + ': 4th Armoured Division, 24 Jan: II Canadian Corps assigned, the Army Reserve relation possible only', sorted(a), [('CAN-ARMY-001A', 'reserve'), ('CAN-COR-002C', 'assigned')])
    expect(s + ': 4th Armoured Division, 24 Jan: Reserve is possible', a[('CAN-ARMY-001A', 'reserve')][0], 'possible')
    a = intervals('CAN-ARM-004D', '1945-01-28')
    expect(s + ': 4th Armoured Division, 28 Jan (Stacey p. 450): I Corps attached and II Canadian Corps assigned', sorted(a), [('CAN-COR-002C', 'assigned'), ('UK-COR-001C', 'attached')])
    a = intervals('CAN-INF-001D', '1945-04-05')
    expect(s + ': 1st Division, 5 Apr: I Canadian Corps assigned and II Canadian Corps attached', sorted(a), [('CAN-COR-001C', 'assigned'), ('CAN-COR-002C', 'attached')])
    a = intervals('CAN-INF-001D', '1945-04-14')
    expect(s + ': 1st Division, 14 Apr: back under I Canadian Corps only', sorted(a), [('CAN-COR-001C', 'assigned')])
    a = intervals('CAN-ARM-005D', '1945-04-20')
    expect(s + ': 5th Armoured Division, 20 Apr: I Canadian Corps', sorted(a), [('CAN-COR-001C', 'assigned')])
    a = intervals('CAN-ARM-005D', '1945-04-22')
    expect(s + ': 5th Armoured Division, 22 Apr (Stacey p. 591): II Canadian Corps', sorted(a), [('CAN-COR-002C', 'assigned')])
    a = intervals('UK-INF-049D', '1945-04-01')
    expect(s + ': 49th Division, 1 Apr: attached to I Canadian Corps (Stacey p. 529)', sorted(a)[0], ('CAN-COR-001C', 'attached'))
    claims = {c['claim_id']: c for c in common.load_all_claims()[1]}
    c = claims['C1343']
    expect(s + ': C1343 is the first Army claim of 1945', (c['unit_id'], c['date'], c['event_type']), ('CAN-ARMY-001A', '1945-01-18', 'command_change'))


def scenario_16_british_batch_1_jun_dec_1944():
    """British Batch 1 (June to December 1944): the attachments of the 7th Armoured and Guards Armoured Divisions to II Canadian Corps end by 30 July (sourced bound, day inferred); the 7th Armoured Division is with I Corps from 16 August and XII Corps from 31 August; XII Corps is activated and takes the 15th and 59th Divisions; the Guards and 11th Armoured Divisions are in XXX Corps at Brussels and Antwerp; the 1st Airborne Division is in I Airborne Corps at Arnhem; the 52nd Division is with the First Canadian Army at Walcheren."""
    s = 'scenario 16, British Batch 1 (June to December 1944)'
    a = intervals('UK-ARM-007D', '1944-07-22')
    expect(s + ': 7th Armoured Division, 22 Jul: attached to II Canadian Corps is certain (Stacey p. 186)', a[('CAN-COR-002C', 'attached')][0], 'certain')
    a = intervals('UK-ARM-007D', '1944-08-01')
    expect(s + ': 7th Armoured Division, 1 Aug: the attachment to II Canadian Corps has ended (latest 30 July, Ellis I pp. 378 and 388); XXX Corps is certain', sorted(a), [('UK-COR-030C', 'assigned')])
    expect(s + ': 7th Armoured Division, 1 Aug: XXX Corps is certain', a[('UK-COR-030C', 'assigned')][0], 'certain')
    a = intervals('UK-ARM-GRDD', '1944-07-27')
    expect(s + ': Guards Armoured Division, 27 Jul: VIII Corps is certain, II Canadian Corps is possible only (end between 25 and 30 July)', sorted(a), [('CAN-COR-002C', 'attached'), ('UK-COR-008C', 'assigned')])
    a = intervals('UK-ARM-GRDD', '1944-09-03')
    expect(s + ': Guards Armoured Division, 3 Sep (Brussels): XXX Corps is certain', sorted(a), [('UK-COR-030C', 'assigned')])
    a = intervals('UK-ARM-007D', '1944-08-20')
    expect(s + ': 7th Armoured Division, 20 Aug: attached to I Corps (Ellis I p. 432) is possible only, with XXX Corps', sorted(a), [('UK-COR-001C', 'attached'), ('UK-COR-030C', 'assigned')])
    a = intervals('UK-ARM-007D', '1944-09-05')
    expect(s + ': 7th Armoured Division, 5 Sep: XII Corps (from 31 August, Ellis I p. 469)', sorted(a), [('UK-COR-012C', 'assigned')])
    a = intervals('UK-COR-012C', '1944-08-10')
    expect(s + ': XII Corps, 10 Aug: Second Army is certain', sorted(a), [('UK-ARMY-002A', 'assigned')])
    a = intervals('UK-INF-043D', '1944-08-10')
    expect(s + ': 43rd Division, 10 Aug: XXX Corps is certain (Mont Pincon, Ellis I pp. 409-410)', sorted(a), [('UK-COR-030C', 'assigned')])
    a = intervals('UK-INF-059D', '1944-08-10')
    expect(s + ': 59th Division, 10 Aug: XII Corps', sorted(a), [('UK-COR-012C', 'assigned')])
    a = intervals('UK-INF-015D', '1944-08-28')
    expect(s + ': 15th Division, 28 Aug (Seine crossing): XII Corps', sorted(a), [('UK-COR-012C', 'assigned')])
    a = intervals('UK-INF-049D', '1944-09-11')
    expect(s + ': 49th Division, 11 Sep (Le Havre): I Corps', sorted(a), [('UK-COR-001C', 'assigned')])
    a = intervals('UK-ARM-011D', '1944-09-01')
    expect(s + ': 11th Armoured Division, 1 Sep: XXX Corps (from 21 August)', sorted(a), [('UK-COR-030C', 'assigned')])
    a = intervals('UK-ABN-001D', '1944-09-20')
    expect(s + ': 1st Airborne Division, 20 Sep (Arnhem): I Airborne Corps is certain', sorted(a), [('UK-ABN-001C', 'assigned')])
    a = intervals('UK-ABN-001C', '1944-09-20')
    expect(s + ': I Airborne Corps, 20 Sep: First Allied Airborne Army is certain', sorted(a), [('ALL-FAAA-001A', 'assigned')])
    a = intervals('BEL-INF-001B', '1944-08-25')
    expect(s + ': 1st Belgian Brigade, 25 Aug: attached to the 6th Airborne Division (Ellis I p. 448), under First Canadian Army (Stacey p. 323, added by the Allied contingents batch)', sorted(a), [('CAN-ARMY-001A', 'unspecified_subordination'), ('UK-ABN-006D', 'attached')])
    a = intervals('UK-INF-052D', '1944-11-05')
    expect(s + ': 52nd Division, 5 Nov (Walcheren): attached to the First Canadian Army (Ellis II pp. 84 and 114)', sorted(a), [('CAN-ARMY-001A', 'attached')])
    claims = {c['claim_id']: c for c in common.load_all_claims()[1]}
    c = claims['C1408']
    expect(s + ': C1408 is the first British row of the batch', (c['unit_id'], c['date']), ('UK-COR-001C', '1944-07-08'))
    c = claims['C1468']
    expect(s + ': C1468 is the last row of the batch (XXX Corps in the Ardennes)', (c['unit_id'], c['date']), ('UK-COR-030C', '1944-12-20'))


def scenario_17_british_batch_2_jan_may_1945():
    """British Batch 2 (January to May 1945): the divisions move between XXX, XII and VIII Corps and the Canadian formations in the sourced order; attachments end where the Rhine-crossing order of battle shows the new corps; the five new operations carry the relinked rows."""
    s = 'scenario 17, British Batch 2 (January to May 1945)'
    a = intervals('UK-INF-052D', '1945-01-20')
    expect(s + ': 52nd Division, 20 Jan (Waldfeucht): XII Corps is certain', a[('UK-COR-012C', 'assigned')][0], 'certain')
    a = intervals('UK-INF-052D', '1945-03-20')
    expect(s + ': 52nd Division, 20 Mar: XXX Corps only, the attachment to the First Canadian Army has ended', sorted(a), [('UK-COR-030C', 'assigned')])
    a = intervals('UK-INF-053D', '1945-01-05')
    expect(s + ': 53rd Division, 5 Jan: XXX Corps is certain', a[('UK-COR-030C', 'assigned')][0], 'certain')
    a = intervals('UK-INF-053D', '1945-03-25')
    expect(s + ': 53rd Division, 25 Mar (Rhine crossing): XII Corps', sorted(a), [('UK-COR-012C', 'assigned')])
    a = intervals('UK-INF-043D', '1945-03-03')
    expect(s + ': 43rd Division, 3 Mar (Calcar): attached to II Canadian Corps is certain', a[('CAN-COR-002C', 'attached')][0], 'certain')
    a = intervals('UK-INF-043D', '1945-03-23')
    expect(s + ': 43rd Division, 23 Mar: the attachment to II Canadian Corps has ended (Ellis II p. 285); XXX Corps only', sorted(a), [('UK-COR-030C', 'assigned')])
    a = intervals('UK-ARM-011D', '1945-02-27')
    expect(s + ': 11th Armoured Division, 27 Feb (Udem): attached to II Canadian Corps is certain', a[('CAN-COR-002C', 'attached')][0], 'certain')
    a = intervals('UK-ARM-011D', '1945-04-15')
    expect(s + ': 11th Armoured Division, 15 Apr (Belsen): VIII Corps only', sorted(a), [('UK-COR-008C', 'assigned')])
    a = intervals('UK-ABN-006D', '1945-03-24')
    expect(s + ': 6th Airborne Division, 24 Mar (Hamminkeln): attached to XVIII Airborne Corps is certain', a[('US-ABN-018C', 'attached')][0], 'certain')
    a = intervals('UK-ABN-006D', '1945-05-02')
    expect(s + ': 6th Airborne Division, 2 May (Wismar): VIII Corps and the attachment to XVIII Airborne Corps are both certain', sorted(a), [('UK-COR-008C', 'assigned'), ('US-ABN-018C', 'attached')])
    a = intervals('UK-INF-015D', '1945-04-14')
    expect(s + ': 15th Division, 14 Apr: VIII Corps is certain', sorted(a), [('UK-COR-008C', 'assigned')])
    a = intervals('UK-INF-003D', '1945-04-22')
    expect(s + ': 3rd Division, 22 Apr (Bremen): XXX Corps is certain', sorted(a), [('UK-COR-030C', 'assigned')])
    a = intervals('UK-COR-030C', '1945-02-10')
    expect(s + ': XXX Corps, 10 Feb (Veritable): Second Army and the First Canadian Army (attached) are both certain', sorted(a), [('CAN-ARMY-001A', 'attached'), ('UK-ARMY-002A', 'assigned')])
    a = intervals('UK-COR-030C', '1945-03-10')
    expect(s + ': XXX Corps, 10 Mar: back under Second Army only', sorted(a), [('UK-ARMY-002A', 'assigned')])
    claims = {c['claim_id']: c for c in common.load_all_claims()[1]}
    for cid, op in (('C1459', 'OP-ASTONIA'), ('C1329', 'OP-INFATUATE'), ('C1467', 'OP-INFATUATE'), ('C1469', 'OP-PHEASANT'), ('C1471', 'OP-CLIPPER'), ('C1510', 'OP-PLUNDER')):
        expect(s + ': %s belongs to %s' % (cid, op), claims[cid]['operation_id'], op)
    c = claims['C1469']
    expect(s + ': C1469 is the first row of the batch (XII Corps)', (c['unit_id'], c['date']), ('UK-COR-012C', '1944-10-22'))
    c = claims['C1538']
    expect(s + ': C1538 is the last row of the batch (21st Army Group, surrender)', (c['unit_id'], c['date'], c['event_type']), ('UK-AG-021G', '1945-05-04', 'surrender'))


def scenario_18_british_batch_2_followup():
    """British Batch 2 follow-up (28 October 2026): the 3rd Division is in VIII Corps (attached to II Canadian Corps from 29 December to 19 January) and joins XXX Corps by 25 February; the 50th Division is attached to II Canadian Corps from 9 to 29 November 1944; the 49th Division is attached to II Canadian Corps from the end of November; the 59th Division leaves XII Corps by 23 August; XVIII Airborne Corps is attached to the British Second Army from 9 March to 1 April 1945 (Plunder-Varsity) and is under the US First Army again from 2 April."""
    s = 'scenario 18, British Batch 2 follow-up'
    a = intervals('UK-INF-003D', '1944-10-01')
    expect(s + ': 3rd Division, 1 Oct 1944: VIII Corps is certain (Ellis II pp. 4, 159, 238); I Corps is no longer listed', sorted(a), [('UK-COR-008C', 'assigned')])
    a = intervals('UK-INF-003D', '1945-01-10')
    expect(s + ': 3rd Division, 10 Jan 1945: VIII Corps and the attachment to II Canadian Corps are both certain (Stacey p. 443)', sorted(a), [('CAN-COR-002C', 'attached'), ('UK-COR-008C', 'assigned')])
    a = intervals('UK-INF-003D', '1945-02-10')
    expect(s + ': 3rd Division, 10 Feb: VIII Corps is possible only (end between 19 January and 24 February), the attachment has ended', sorted(a), [('UK-COR-008C', 'assigned')])
    expect(s + ': 3rd Division, 10 Feb: VIII Corps is possible, not certain', a[('UK-COR-008C', 'assigned')][0], 'possible')
    a = intervals('UK-INF-003D', '1945-02-26')
    expect(s + ': 3rd Division, 26 Feb (Veritable, Stacey p. 494): XXX Corps is certain, VIII Corps has ended', sorted(a), [('UK-COR-030C', 'assigned')])
    a = intervals('UK-INF-050D', '1944-11-15')
    expect(s + ': 50th Division, 15 Nov: the attachment to II Canadian Corps is certain (Stacey pp. 428, 430)', a[('CAN-COR-002C', 'attached')][0], 'certain')
    a = intervals('UK-INF-050D', '1944-12-05')
    expect(s + ': 50th Division, 5 Dec: the attachment to II Canadian Corps has ended (Ellis II p. 159, Stacey p. 430)', sorted(a), [('UK-COR-030C', 'assigned')])
    a = intervals('UK-INF-049D', '1944-12-04')
    expect(s + ': 49th Division, 4 Dec: I Corps (assigned) and II Canadian Corps (attached) are both certain (Stacey p. 433)', sorted(a), [('CAN-COR-002C', 'attached'), ('UK-COR-001C', 'assigned')])
    a = intervals('UK-INF-049D', '1945-02-10')
    expect(s + ': 49th Division, 10 Feb 1945: the attachment to II Canadian Corps is possible only (end between 18 January and 14 March)', a[('CAN-COR-002C', 'attached')][0], 'possible')
    a = intervals('UK-INF-059D', '1944-08-10')
    expect(s + ': 59th Division, 10 Aug: XII Corps is possible only (end between 6 and 23 August, Ellis I p. 453)', a[('UK-COR-012C', 'assigned')][0], 'possible')
    a = intervals('UK-INF-059D', '1944-08-25')
    expect(s + ': 59th Division, 25 Aug: no corps (disbanded)', sorted(a), [])
    a = intervals('US-ABN-018C', '1945-03-24')
    expect(s + ': XVIII Airborne Corps, 24 Mar: attached to the British Second Army is certain (CMH ch. 14 p. 298, Ellis II p. 285), the US First Army relation has ended', sorted(a), [('ALL-FAAA-001A', 'assigned'), ('UK-ARMY-002A', 'attached')])
    a = intervals('US-ABN-018C', '1945-04-10')
    expect(s + ': XVIII Airborne Corps, 10 Apr: back under the US First Army (operational control, CMH ch. 16 p. 362), possible only; the Second Army attachment ended on 1 April', sorted(a), [('ALL-FAAA-001A', 'assigned'), ('US-ARMY-001A', 'operational_control')])
    a = intervals('US-ABN-018C', '1945-03-01')
    expect(s + ': XVIII Airborne Corps, 1 Mar: the First Army relation is possible only (end between 19 December and 8 March)', a[('US-ARMY-001A', 'operational_control')][0], 'possible')
    a = intervals('UK-INF-043D', '1945-03-28')
    expect(s + ': 43rd Division, 28 Mar (Megchelen): XXX Corps is certain', sorted(a), [('UK-COR-030C', 'assigned')])
    claims = {c['claim_id']: c for c in common.load_all_claims()[1]}
    c = claims['C1539']
    expect(s + ': C1539 is the first row of the follow-up (50th Division at Neerpelt)', (c['unit_id'], c['date']), ('UK-INF-050D', '1944-09-17'))
    c = claims['C1546']
    expect(s + ': C1546 is the last row of the follow-up (XVIII Airborne Corps, Varsity)', (c['unit_id'], c['date'], c['parent_unit_id']), ('US-ABN-018C', '1945-03-24', 'UK-ARMY-002A'))


def scenario_19_allied_contingents_1944_45():
    s = 'scenario 19, Allied contingents (June 1944 to May 1945)'
    a = intervals('POL-ARM-001D', '1944-08-10')
    expect(s + ': 1st Polish Armoured Division, 10 Aug: First Canadian Army and II Canadian Corps (Stacey p. 208)', sorted(a), [('CAN-ARMY-001A', 'unspecified_subordination'), ('CAN-COR-002C', 'attached')])
    a = intervals('POL-ARM-001D', '1944-11-01')
    expect(s + ': 1st Polish Armoured Division, 1 Nov: I Corps from 28 September (Stacey p. 367)', sorted(a), [('CAN-ARMY-001A', 'unspecified_subordination'), ('UK-COR-001C', 'attached')])
    a = intervals('POL-ARM-001D', '1945-02-10')
    expect(s + ': 1st Polish Armoured Division, 10 Feb 1945: I Corps is possible only (Netherlands District undated)', a[('UK-COR-001C', 'attached')][0], 'possible')
    a = intervals('POL-ARM-001D', '1945-04-20')
    expect(s + ': 1st Polish Armoured Division, 20 Apr 1945: back in II Canadian Corps from 8 April (Stacey p. 552)', sorted(a), [('CAN-ARMY-001A', 'unspecified_subordination'), ('CAN-COR-002C', 'attached')])
    a = intervals('POL-ABN-001B', '1944-09-21')
    expect(s + ': Polish Parachute Brigade, 21 Sep: under the 1st Airborne Division (Stacey p. 313)', sorted(a), [('UK-ABN-001D', 'attached')])
    a = intervals('POL-ABN-001B', '1944-09-28')
    expect(s + ': Polish Parachute Brigade, 28 Sep: no relation after Market Garden', sorted(a), [])
    a = intervals('CZ-ARM-001B', '1944-10-20')
    expect(s + ': Czechoslovak brigade, 20 Oct: First Canadian Army at Dunkirk (Stacey p. 368)', sorted(a), [('CAN-ARMY-001A', 'attached'), ('UK-AG-021G', 'unspecified_subordination')])
    a = intervals('CZ-ARM-001B', '1944-12-15')
    expect(s + ': Czechoslovak brigade, 15 Dec: 21st Army Group only from 27 November (Stacey p. 368)', sorted(a), [('UK-AG-021G', 'unspecified_subordination')])
    a = intervals('BEL-INF-001B', '1944-08-29')
    expect(s + ': Belgian brigade, 29 Aug: the 6th Airborne Division command ended on 27 August', sorted(a), [('CAN-ARMY-001A', 'unspecified_subordination')])
    a = intervals('BEL-INF-001B', '1944-10-01')
    expect(s + ': Belgian brigade, 1 Oct: Second Army from 2 September', sorted(a), [('UK-ARMY-002A', 'unspecified_subordination')])
    a = intervals('BEL-INF-001B', '1945-04-18')
    expect(s + ': Belgian brigade, 18 Apr 1945 (Opheusden): I Canadian Corps (Stacey p. 570)', sorted(a), [('CAN-COR-001C', 'unspecified_subordination')])
    a = intervals('NL-INF-IRNEB', '1944-08-25')
    expect(s + ': Princess Irene Brigade, 25 Aug: 6th Airborne Division possible only (end between 21 August and 1 September)', a[('UK-ABN-006D', 'attached')][0], 'possible')
    a = intervals('NL-INF-IRNEB', '1944-10-24')
    expect(s + ': Princess Irene Brigade, 24 Oct (Pheasant): Second Army', sorted(a), [('UK-ARMY-002A', 'unspecified_subordination')])
    a = intervals('NL-INF-IRNEB', '1945-04-25')
    expect(s + ': Princess Irene Brigade, 25 Apr 1945 (Hedel): no relation (Netherlands District is not a unit)', sorted(a), [])
    claims = {c['claim_id']: c for c in common.load_all_claims()[1]}
    c = claims['C1547']
    expect(s + ': C1547 is the first row of the batch (1st Polish Armoured Division, Totalize)', (c['unit_id'], c['date']), ('POL-ARM-001D', '1944-08-08'))
    c = claims['C1607']
    expect(s + ': C1607 is the last row of the batch (Princess Irene Brigade at Hedel)', (c['unit_id'], c['date'], c['parent_unit_id']), ('NL-INF-IRNEB', '1945-04-25', ''))


def scenario_20_french_1944_45():
    s = 'scenario 20, French batch (August 1944 to May 1945)'
    a = intervals('FR-ARM-002D', '1944-08-12')
    expect(s + ': 2d French Armored Division, 12 Aug: XV Corps and Third Army (Breakout and Pursuit p. 497)', sorted(a), [('US-ARMY-003A', 'unspecified_subordination'), ('US-COR-015C', 'attached')])
    a = intervals('FR-ARM-002D', '1944-08-25')
    expect(s + ': 2d French Armored Division, 25 Aug (Paris): V Corps and First Army', sorted(a), [('US-ARMY-001A', 'unspecified_subordination'), ('US-COR-005C', 'attached')])
    a = intervals('FR-ARM-002D', '1944-09-20')
    expect(s + ': 2d French Armored Division, 20 Sep: XV Corps of the Third Army from 8 September (Lorraine p. 185)', sorted(a), [('US-ARMY-003A', 'unspecified_subordination'), ('US-COR-015C', 'attached')])
    a = intervals('FR-ARM-002D', '1944-11-23')
    expect(s + ': 2d French Armored Division, 23 Nov (Strasbourg): XV Corps of the Seventh Army from 29 September (Riviera p. 254)', sorted(a), [('US-ARMY-007A', 'unspecified_subordination'), ('US-COR-015C', 'attached')])
    a = intervals('FR-ARM-002D', '1944-11-30')
    expect(s + ': 2d French Armored Division, 30 Nov: VI Corps from 27 November (Riviera p. 454)', sorted(a), [('US-ARMY-007A', 'unspecified_subordination'), ('US-COR-006C', 'attached')])
    a = intervals('FR-ARMY-001A', '1944-08-28')
    expect(s + ': Army B, 28 Aug (Toulon): under the Seventh Army', sorted(a), [('US-ARMY-007A', 'unspecified_subordination')])
    a = intervals('FR-ARMY-001A', '1944-09-17')
    expect(s + ': First French Army, 17 Sep: 6th Army Group, Patch directing operations until 19 September (Riviera p. 224)', sorted(a), [('US-AG-006G', 'assigned'), ('US-ARMY-007A', 'operational_control')])
    a = intervals('FR-ARMY-001A', '1945-04-22')
    expect(s + ': First French Army, 22 Apr 1945 (Stuttgart): 6th Army Group', sorted(a), [('US-AG-006G', 'assigned')])
    a = intervals('FR-COR-002C', '1945-03-31')
    expect(s + ': French II Corps, 31 Mar 1945 (Rhine crossing): First French Army from 1 September 1944', sorted(a), [('FR-ARMY-001A', 'assigned')])
    a = intervals('FR-ARM-001D', '1944-11-19')
    expect(s + ': French 1st Armored Division, 19 Nov (Rosenau): I Corps', sorted(a), [('FR-COR-001C', 'unspecified_subordination')])
    claims = {c['claim_id']: c for c in common.load_all_claims()[1]}
    c = claims['C1608']
    expect(s + ': C1608 is the first row of the batch (2d French Armored Division at le Mans)', (c['unit_id'], c['date'], c['parent_unit_id']), ('FR-ARM-002D', '1944-08-09', 'US-COR-015C'))
    c = claims['C1645']
    expect(s + ': C1645 is the last row of the batch (9th Colonial Infantry Division at Ensisheim)', (c['unit_id'], c['date'], c['parent_unit_id']), ('FR-INF-009D', '1945-02-06', 'FR-COR-001C'))


def scenario_21_french_followup():
    s = 'scenario 21, French follow-up (2d French Armored Division winter 1944-1945, Atlantic and Alpine formations)'
    a = intervals('FR-ARM-002D', '1944-12-10')
    expect(s + ': 2d French Armored Division, 10 Dec: First French Army operational control from 5 December (Riviera p. 464), Seventh Army standing', sorted(a), [('FR-ARMY-001A', 'operational_control'), ('US-ARMY-007A', 'unspecified_subordination')])
    a = intervals('FR-ARM-002D', '1944-12-20')
    expect(s + ': 2d French Armored Division, 20 Dec: II Corps attached (Riviera p. 486)', sorted(a), [('FR-ARMY-001A', 'operational_control'), ('FR-COR-002C', 'attached'), ('US-ARMY-007A', 'unspecified_subordination')])
    a = intervals('FR-ARM-002D', '1945-01-10')
    expect(s + ': 2d French Armored Division, 10 Jan 1945: XV Corps of the Seventh Army, not the VI Corps (Riviera pp. 496, 501)', sorted(a), [('US-ARMY-007A', 'unspecified_subordination'), ('US-COR-015C', 'attached')])
    a = intervals('FR-ARM-002D', '1945-02-01')
    expect(s + ': 2d French Armored Division, 1 Feb 1945: First French Army from 19 January (de Lattre p. 373), II Corps from 28 January (Grussenheim; CMH p. 548)', sorted(a), [('FR-ARMY-001A', 'unspecified_subordination'), ('FR-COR-002C', 'unspecified_subordination')])
    a = intervals('FR-INF-GIRONDE', '1945-04-16')
    expect(s + ': Gironde marching division, 16 Apr 1945 (Royan): Atlantic army detachment', sorted(a), [('FR-ARMY-ATLANT', 'unspecified_subordination')])
    a = intervals('FR-INF-014D', '1945-04-10')
    expect(s + ': French 14th Infantry Division, 10 Apr 1945: First French Army', sorted(a), [('FR-ARMY-001A', 'unspecified_subordination')])
    claims = {c['claim_id']: c for c in common.load_all_claims()[1]}
    expect(s + ': C1634 (1st DFL at Lyon) raised to 0.7 with the CMH history', claims['C1634']['confidence'], '0.7')
    expect(s + ': C1633 (5th Armored Division at Stuttgart) stays 21 April 1945, raised to 0.5 by the de Lattre pass', (claims['C1633']['date'], claims['C1633']['confidence']), ('1945-04-21', '0.5'))


def scenario_22_french_delattre():
    s = 'scenario 22, French follow-up de Lattre pass (History of the French First Army, R686)'
    a = intervals('FR-ARM-002D', '1945-01-18')
    expect(s + ': 2d French Armored Division, 18 Jan 1945: still Seventh Army and XV Corps', sorted(a), [('US-ARMY-007A', 'unspecified_subordination'), ('US-COR-015C', 'attached')])
    a = intervals('FR-ARM-002D', '1945-01-20')
    expect(s + ': 2d French Armored Division, 20 Jan 1945: First French Army from 19 January (de Lattre p. 373)', sorted(a), [('FR-ARMY-001A', 'unspecified_subordination')])
    a = intervals('FR-INF-014D', '1945-04-30')
    expect(s + ': French 14th Infantry Division, 30 Apr 1945: I Corps from 23 April (de Lattre p. 479) under the First French Army', sorted(a), [('FR-ARMY-001A', 'unspecified_subordination'), ('FR-COR-001C', 'unspecified_subordination')])
    a = intervals('FR-INF-003D', '1945-01-20')
    expect(s + ': 3rd Algerian Infantry Division, 20 Jan 1945: II Corps at Strasbourg from 5 January (de Lattre p. 312)', sorted(a), [('FR-COR-002C', 'unspecified_subordination')])
    claims = {c['claim_id']: c for c in common.load_all_claims()[1]}
    expect(s + ': C1644 (9th DIC at Toulon) raised to 0.7 with de Lattre as a second family', claims['C1644']['confidence'], '0.7')
    expect(s + ': C1637 (2nd DIM at Belfort) keeps 25 November 1944 and 0.7 despite de Lattre\'s 21 November', (claims['C1637']['date'], claims['C1637']['confidence']), ('1944-11-25', '0.7'))
    expect(s + ': C1656 (3rd DIA, Strasbourg) and C1657 (1st DB, Ulm) cite R686', ('R686' in claims['C1656']['reference_ids'], 'R686' in claims['C1657']['reference_ids']), (True, True))


def scenario_23_brigades_batch_1_uk_can():
    """Brigades Batch 1 (British and Canadian independent brigades, 1944-45): the 56th Infantry Brigade moves from the 50th Division to the 7th Armoured Division and back on 11-12 June 1944 and is organic to the 49th Division from 20 August (no independent relation after); the 27th Armoured Brigade has no relation after its break-up on 29 July 1944; the 1st Special Service Brigade has no relation while in England (September 1944 to January 1945); the 4th Special Service Brigade is under II Canadian Corps and the 52nd Division at Walcheren; the 2nd Canadian Armoured Brigade is under II Canadian Corps from 11 July 1944 and under I Corps and the Polish Armoured Division at Breda."""
    s = 'scenario 23, Brigades Batch 1 (British and Canadian)'
    a = intervals('UK-INF-056B', '1944-06-11')
    expect(s + ': 56th Brigade, 11 Jun (Tilly): XXX Corps certain, the 7th Armoured Division from that day (Ellis I p. 252)', sorted(a), [('UK-ARM-007D', 'attached'), ('UK-COR-030C', 'assigned')])
    a = intervals('UK-INF-056B', '1944-06-12')
    expect(s + ': 56th Brigade, 12 Jun: the handover day, both divisions possible (Ellis I p. 254)', (a[('UK-ARM-007D', 'attached')][0], a[('UK-INF-050D', 'attached')][0]), ('possible', 'possible'))
    a = intervals('UK-INF-056B', '1944-08-25')
    expect(s + ': 56th Brigade, 25 Aug: no independent relation (organic to the 49th Division from 20 August)', sorted(a), [])
    a = intervals('UK-ARM-027B', '1944-08-15')
    expect(s + ': 27th Armoured Brigade, 15 Aug: no relation after the break-up of 29 July', sorted(a), [])
    a = intervals('UK-CDO-001B', '1944-10-15')
    expect(s + ': 1st Special Service Brigade, 15 Oct: no relation (in England from 8-9 September, Wikipedia)', sorted(a), [])
    a = intervals('UK-CDO-004B', '1944-11-05')
    expect(s + ': 4th Special Service Brigade, 5 Nov (Walcheren): II Canadian Corps and the 52nd Division both certain (Stacey p. 412)', sorted(a), [('CAN-COR-002C', 'assigned'), ('UK-INF-052D', 'attached')])
    a = intervals('CAN-ARM-002B', '1944-07-15')
    expect(s + ': 2nd Canadian Armoured Brigade, 15 Jul: II Canadian Corps (from 11 July, Stacey p. 166) and the 3rd Canadian Division', sorted(a), [('CAN-COR-002C', 'assigned'), ('CAN-INF-003D', 'attached')])
    a = intervals('CAN-ARM-002B', '1944-10-27')
    expect(s + ': 2nd Canadian Armoured Brigade, 27 Oct (Breda): I Corps and the Polish Armoured Division (Ellis II p. 126)', sorted(a), [('POL-ARM-001D', 'attached'), ('UK-COR-001C', 'assigned')])
    a = intervals('UK-ARM-004B', '1945-04-17')
    expect(s + ': 4th Armoured Brigade, 17 Apr 1945 (Verden): XII Corps and the 53rd Division (Ellis II p. 310)', sorted(a), [('UK-COR-012C', 'assigned'), ('UK-INF-053D', 'attached')])
    claims = {c['claim_id']: c for c in common.load_all_claims()[1]}
    c = claims['C1658']
    expect(s + ': C1658 is the first row of the batch (4th Armoured Brigade)', (c['unit_id'], c['date']), ('UK-ARM-004B', '1944-06-10'))
    c = claims['C1713']
    expect(s + ': C1713 is the last row of the batch (2nd Canadian Armoured Brigade, Blockbuster)', (c['unit_id'], c['date']), ('CAN-ARM-002B', '1945-02-26'))
    expect(s + ': C1695 (56th Brigade joins the 49th Division) is a representative point at 0.3', (claims['C1695']['parent_unit_id'], claims['C1695']['confidence']), ('UK-INF-049D', '0.3'))


def scenario_24_brigades_batch_2_us():
    """Brigades Batch 2 (US independent units and task forces, 1944-45): the 1st Airborne Task Force is under the Seventh Army's direct (operational) control and has no relation after its dissolution on 23 November 1944; the 1st Special Service Force is under the Seventh Army on D-day and with the task force at the end of August; the 517th moves from the 1st Airborne Task Force to the XVIII Airborne Corps and is attached to the 82nd Airborne Division on 3 January 1945; the 551st has no relation after its inactivation on 27 January 1945; Task Force Butler is under VI Corps and, from 23 August 1944, the 36th Division; Task Force A is under VIII Corps."""
    s = 'scenario 24, Brigades Batch 2 (US)'
    a = intervals('US-ABTF-001D', '1944-08-15')
    expect(s + ': 1st Airborne Task Force, 15 Aug: Seventh Army direct control (Clarke and Smith ch. 3 p. 45)', sorted(a), [('US-ARMY-007A', 'operational_control')])
    a = intervals('US-ABTF-001D', '1944-12-01')
    expect(s + ': 1st Airborne Task Force, 1 Dec: no relation after the dissolution of 23 November', sorted(a), [])
    a = intervals('US-SSF-001B', '1944-08-15')
    expect(s + ': 1st Special Service Force, 15 Aug (Levant): Seventh Army, not VI Corps', sorted(a), [('US-ARMY-007A', 'operational_control')])
    a = intervals('US-SSF-001B', '1944-08-26')
    expect(s + ': 1st Special Service Force, 26 Aug (Villeneuve-Loubet): the 1st Airborne Task Force', sorted(a), [('US-ABTF-001D', 'attached')])
    a = intervals('US-PRCT-517', '1944-08-16')
    expect(s + ': 517th, 16 Aug (Les Arcs): the 1st Airborne Task Force', sorted(a), [('US-ABTF-001D', 'attached')])
    a = intervals('US-PRCT-517', '1945-01-03')
    expect(s + ': 517th, 3 Jan 1945: XVIII Airborne Corps and the 82nd Airborne Division (MacDonald ch. 2)', sorted(a), [('US-ABN-018C', 'assigned'), ('US-ABN-082D', 'attached')])
    a = intervals('US-PIB-551', '1945-02-15')
    expect(s + ': 551st, 15 Feb 1945: no relation after the inactivation of 27 January', sorted(a), [])
    a = intervals('US-TF-BUTLER', '1944-08-19')
    expect(s + ': Task Force Butler, 19 Aug (Sisteron): VI Corps only', sorted(a), [('US-COR-006C', 'assigned')])
    a = intervals('US-TF-BUTLER', '1944-08-26')
    expect(s + ': Task Force Butler, 26 Aug (Condillac): VI Corps and the 36th Division', sorted(a), [('US-COR-006C', 'assigned'), ('US-INF-036D', 'attached')])
    a = intervals('US-TDB-001B', '1944-08-08')
    expect(s + ': Task Force A, 8 Aug (Morlaix): VIII Corps', sorted(a), [('US-COR-008C', 'assigned')])
    claims = {c['claim_id']: c for c in common.load_all_claims()[1]}
    c = claims['C1714']
    expect(s + ': C1714 is the first row of the batch (1st Airborne Task Force, Le Muy)', (c['unit_id'], c['date']), ('US-ABTF-001D', '1944-08-15'))
    c = claims['C1758']
    expect(s + ': C1758 is the last row of the batch (Task Force A, Douarnenez)', (c['unit_id'], c['date']), ('US-TDB-001B', '1944-09-20'))


def scenario_25_brigades_batch_3_german():
    """Brigades Batch 3 (German brigades, Kampfgruppen and fortress garrisons, 1944-45): Panzer-Brigade 106 moves from the First Army to the XIII SS Corps; Panzer-Brigade 112 has no relation after its dissolution on 23 September 1944; the Führer-Begleit Brigade moves from the LXVI Corps to the LVIII and then the XXXIX Panzer Corps; the Führer-Grenadier Brigade goes into the Seventh Army reserve; Kampfgruppe Peiper is organic to the 1st SS Panzer Division; Kampfgruppe Chill is organic to the 85th Infantry Division; Lorient is under the XXV Corps until its surrender on 10 May 1945."""
    s = 'scenario 25, Brigades Batch 3 (German)'
    a = intervals('GER-PZB-106B', '1944-09-30')
    expect(s + ': Panzer-Brigade 106, 30 Sep: First Army and the XIII SS Corps', sorted(a), [('GER-ARMY-001A', 'operational_control'), ('GER-SSCOR-013C', 'assigned')])
    a = intervals('GER-PZB-112B', '1944-09-30')
    expect(s + ': Panzer-Brigade 112, 30 Sep: no relation after the dissolution of 23 September', sorted(a), [])
    a = intervals('GER-PG-FUEBE', '1944-12-22')
    expect(s + ': Führer-Begleit Brigade, 22 Dec (Rodt): LXVI Corps', sorted(a), [('GER-COR-066C', 'assigned')])
    a = intervals('GER-PG-FUEBE', '1944-12-28')
    expect(s + ': Führer-Begleit Brigade, 28 Dec (Herbaimont): XXXIX Panzer Corps', sorted(a), [('GER-PZ-039C', 'assigned')])
    a = intervals('GER-PG-FUEGR', '1945-01-02')
    expect(s + ': Führer-Grenadier Brigade, 2 Jan 1945: Seventh Army reserve', [x for x in sorted(a) if x[1] == 'reserve'], [('GER-ARMY-007A', 'reserve')])
    # organic relations are kept out of build/command_relations.csv by design, so these two read the master table
    master = common.read_dicts(os.path.join(os.path.dirname(common.BUILD_DIR), 'data', 'command_relations.csv'))[1]
    org = lambda u: sorted((r['higher_unit_id'], r['relationship']) for r in master if r['subject_unit_id'] == u)
    expect(s + ': Kampfgruppe Peiper is organic to the 1st SS Panzer Division and has no other relation', org('GER-KG-PEIPER'), [('GER-SSPZ-001D', 'organic')])
    expect(s + ': Kampfgruppe Chill is organic to the 85th Infantry Division and has no other relation', org('GER-KG-CHILL'), [('GER-INF-085D', 'organic')])
    a = intervals('GER-KG-PEIPER', '1944-12-19')
    expect(s + ': Kampfgruppe Peiper, 19 Dec: no non-organic interval (the organic tie is not in the build)', sorted(a), [])
    a = intervals('GER-FEST-LORIENT', '1945-01-01')
    expect(s + ': Lorient, 1 Jan 1945: XXV Corps', sorted(a), [('GER-COR-025C', 'assigned')])
    a = intervals('GER-FEST-LORIENT', '1945-05-11')
    expect(s + ': Lorient, 11 May 1945: no relation after the surrender', sorted(a), [])
    claims = {c['claim_id']: c for c in common.load_all_claims()[1]}
    c = claims['C1759']
    expect(s + ': C1759 is the first row of the batch (Panzer-Brigade 105, Büsbach)', (c['unit_id'], c['date']), ('GER-PZB-105B', '1944-09-15'))
    c = claims['C1811']
    expect(s + ': C1811 is the last row of the batch (La Rochelle surrender)', (c['unit_id'], c['date']), ('GER-FEST-LAROCH', '1945-05-08'))


# The official-history pass (October 2026) adds rows to units of the earlier activity batches; each batch scenario counts only its own rows,
# so rows whose notes name the official-history pass are left out of the batch counts (they are counted in scenario 34).
BATCH35 = lambda c: 'C2031' <= c['claim_id'] <= 'C2058'   # source fixes from de Lattre and Ellis (scenario 35) count only in their own scenario
BATCH36 = lambda c: 'C2060' <= c['claim_id'] <= 'C2077'   # FMS B-466 batch (scenario 36) counts only in its own scenario
BATCH37 = lambda c: 'C2078' <= c['claim_id'] <= 'C2115'   # FMS 19th Army batch (scenario 37) counts only in its own scenario
BATCH39 = lambda c: 'C2127' <= c['claim_id'] <= 'C2134'   # FMS B-811 Fifteenth Army batch (scenario 39) counts only in its own scenario
NOT_OHP = lambda c: 'official-history pass' not in c['notes'] and not BATCH35(c) and not BATCH36(c) and not BATCH37(c) and not BATCH39(c)


def scenario_26_activity_pilot():
    """Activity pilot (docs/activity_status_design.md): spans, implicit ends, points, open spans, the inferred cap, and blank units."""
    s = 'scenario 26'
    import activity
    idx = activity.load()
    A = lambda u, d: (lambda a: a and (a['activity'], a['status'], a['support'], a['confidence']))(activity.activity_at(u, d, idx))
    expect(s + ': 101st Airborne, 1 Nov 1944: in the line on the Island (inferred start, end implicit)', A('US-ABN-101D', '1944-11-01'), ('in_line', 'certain', 'inferred', 0.3))
    expect(s + ': 101st Airborne, 5 Dec 1944: refitting at Mourmelon (inferred start, stated end)', A('US-ABN-101D', '1944-12-05'), ('refitting', 'certain', 'inferred', 0.3))
    expect(s + ': 101st Airborne, 18 Dec 1944: last day of the refit', A('US-ABN-101D', '1944-12-18')[0], 'refitting')
    expect(s + ': 101st Airborne, 20 Dec 1944: no activity after the refit ends (blank is not idle)', A('US-ABN-101D', '1944-12-20'), None)
    expect(s + ': 82nd Airborne, 17 Dec 1944: refitting near Reims (point)', A('US-ABN-082D', '1944-12-17'), ('refitting', 'certain', 'stated', 0.3))
    expect(s + ': 82nd Airborne, 16 Dec 1944: the point does not spread to other days', A('US-ABN-082D', '1944-12-16'), None)
    expect(s + ': 50th Division, 15 Nov 1944: in the line, stated, implicit end by the reserve start', A('UK-INF-050D', '1944-11-15'), ('in_line', 'certain', 'inferred', 0.3))
    expect(s + ': 50th Division, 10 Dec 1944: reserve, open span', A('UK-INF-050D', '1944-12-10'), ('reserve', 'possible', 'stated', 0.3))
    expect(s + ': 2nd Canadian Division, 3 Sep 1944: refitting at Dieppe, stated span', A('CAN-INF-002D', '1944-09-03'), ('refitting', 'certain', 'stated', 0.7))
    expect(s + ': 9th SS Panzer, 10 Sep 1944: refitting (the end is inferred, so the answer is capped)', A('GER-SSPZ-009D', '1944-09-10'), ('refitting', 'certain', 'inferred', 0.3))
    expect(s + ': Lorient, 1 Jan 1945: garrison, stated span', A('GER-FEST-LORIENT', '1945-01-01')[:3], ('garrison', 'certain', 'stated'))
    expect(s + ': Lorient, 11 May 1945: no activity after the surrender', A('GER-FEST-LORIENT', '1945-05-11'), None)
    expect(s + ': 2e DB, 3 Jan 1945: XV Corps reserve (point)', A('FR-ARM-002D', '1945-01-03')[:3], ('reserve', 'certain', 'stated'))
    expect(s + ': 1st Polish Armoured, 1 Sep 1944: refitting after the gap, implicit end by the pursuit', A('POL-ARM-001D', '1944-09-01')[:3], ('refitting', 'certain', 'inferred'))
    expect(s + ': Polish Parachute Brigade, 23 Sep 1944: in the line at Driel', A('POL-ABN-001B', '1944-09-23')[:2], ('in_line', 'certain'))
    expect(s + ': 4th Canadian Armoured, 1 Dec 1944: the open refit span is not carried past 30 days', A('CAN-ARM-004D', '1944-12-01'), None)
    expect(s + ': a unit outside the pilot has no activity (no backfill)', A('US-INF-001D', '1944-12-01'), None)
    claims = common.load_all_claims()[1]
    pilot = {'US-ABN-101D', 'US-ABN-082D', 'UK-ABN-001D', 'UK-INF-050D', 'CAN-INF-002D', 'CAN-ARM-004D', 'GER-SSPZ-009D', 'GER-SSPZ-010D', 'GER-FEST-LORIENT', 'FR-ARM-002D', 'FR-INF-003D', 'POL-ARM-001D', 'POL-ABN-001B'}
    tagged = sorted({c['unit_id'] for c in claims if c.get('activity_status') and NOT_OHP(c) and c['unit_id'] in pilot})
    expect(s + ': the pilot covers 13 units', len(tagged), 13)
    expect(s + ': the pilot has 25 activity rows', sum(1 for c in claims if c.get('activity_status') and NOT_OHP(c) and c['unit_id'] in pilot), 25)


ROLLOUT_1 = ['US-INF-%03dD' % n for n in (1, 2, 3, 4, 5, 8, 9, 28, 29, 30, 35, 36, 45, 69, 79, 80, 83, 89, 90, 95)] + ['US-ARM-%03dD' % n for n in (2, 3, 4, 5, 6, 7, 8, 10, 12, 14)]


def scenario_27_activity_rollout_1():
    """Activity rollout, batch 1 (October 2026): 30 US divisions; existing rows, then the follow-up with new rest/refit, span-closure and 8 May 1945 closing claims (C1821-C1886)."""
    s = 'scenario 27'
    import activity
    A = lambda u, d: (lambda r: r and (r['activity'], r['status'], r['support'], r['confidence']))(activity.activity_at(u, d))
    expect(s + ': 1st Division on D-Day: in the line (point, stated)', A('US-INF-001D', '1944-06-06'), ('in_line', 'certain', 'stated', 0.5))
    expect(s + ': 1st Division, 1 Dec 1944: no activity row, so no answer (blank is not idle)', A('US-INF-001D', '1944-12-01'), None)
    expect(s + ': 2nd Armored, 9 Jun 1944: V Corps reserve on landing (point)', A('US-ARM-002D', '1944-06-09'), ('reserve', 'certain', 'stated', 0.7))
    expect(s + ': 5th Division, 20 Jul 1944: in the line, open span from the entry into combat', A('US-INF-005D', '1944-07-20'), ('in_line', 'possible', 'stated', 0.5))
    expect(s + ': 5th Division, 20 Aug 1944: the open span is not carried past 30 days', A('US-INF-005D', '1944-08-20'), None)
    expect(s + ': 4th Armored, 20 Jan 1945: reserve after Bourcy, open span', A('US-ARM-004D', '1945-01-20'), ('reserve', 'possible', 'stated', 0.5))
    expect(s + ': 90th Division, 19 Jun 1944: inferred point is capped at 0.3', A('US-INF-090D', '1944-06-19'), ('in_line', 'certain', 'inferred', 0.3))
    expect(s + ': 12th Armored, 4 Feb 1945: reserve north of Colmar (point)', A('US-ARM-012D', '1945-02-04')[:3], ('reserve', 'certain', 'stated'))
    claims = common.load_all_claims()[1]
    rows = [c for c in claims if c.get('activity_status') and NOT_OHP(c) and c['unit_id'] in ROLLOUT_1]
    expect(s + ': batch 1 covers 30 units', len({c['unit_id'] for c in rows}), 30)
    expect(s + ': batch 1 with its follow-up and second-source pass has 197 activity rows', len(rows), 197)
    expect(s + ': batch 1 with its follow-up and second-source pass has 170 stated and 27 inferred rows', (sum(c['activity_basis'] == 'stated' for c in rows), sum(c['activity_basis'] == 'inferred' for c in rows)), (170, 27))
    # second-source pass (CMH combat chronicles)
    expect(s + ': 79th Division, 1 Feb 1945: in the line on the Moder (span closed 6 Feb)', A('US-INF-079D', '1945-02-01')[:3], ('in_line', 'certain', 'stated'))
    expect(s + ': 79th Division, 1 May 1945: occupation in the Dortmund area', A('US-INF-079D', '1945-05-01')[:3], ('garrison', 'certain', 'stated'))
    expect(s + ': 10th Armored, 8 May 1945: at Innsbruck at the end of the war (point)', A('US-ARM-010D', '1945-05-08'), ('in_line', 'certain', 'stated', 0.5))
    expect(s + ': 28th Division, 25 Dec 1944: refitting at Neufchateau (stated span to 2 Jan)', A('US-INF-028D', '1944-12-25'), ('refitting', 'certain', 'stated', 0.5))
    expect(s + ': 28th Division, 10 Jan 1945: no answer after the refit ends', A('US-INF-028D', '1945-01-10'), None)
    expect(s + ': 83rd Division, 10 Mar 1945: no answer after the span closed on 2 Mar', A('US-INF-083D', '1945-03-10'), None)
    # follow-up (October 2026): new rest/refit rows, span closures and closing rows at 8 May 1945
    expect(s + ': 1st Division, 10 Dec 1944: refitting in the rear (stated start, implicit end by the Ardennes start)', A('US-INF-001D', '1944-12-10'), ('refitting', 'certain', 'inferred', 0.3))
    expect(s + ': 1st Division, 10 Jan 1945: in the line in the Ardennes (explicit end 28 Jan)', A('US-INF-001D', '1945-01-10'), ('in_line', 'certain', 'stated', 0.3))
    expect(s + ': 1st Division, 10 Feb 1945: no answer after the explicit end', A('US-INF-001D', '1945-02-10'), None)
    expect(s + ': 2nd Division, 22 Sep 1944: brief rest after Brest (stated span)', A('US-INF-002D', '1944-09-22'), ('refitting', 'certain', 'stated', 0.5))
    expect(s + ': 4th Armored, 12 Dec 1944: relieved on 8 Dec, so no answer', A('US-ARM-004D', '1944-12-12'), None)
    expect(s + ': 9th Division, 1 May 1945: holding the Mulde line (closed at 8 May)', A('US-INF-009D', '1945-05-01'), ('in_line', 'certain', 'stated', 0.5))
    expect(s + ': 35th Division, 5 May 1945: occupation at Hanover', A('US-INF-035D', '1945-05-05'), ('garrison', 'certain', 'stated', 0.5))
    expect(s + ': 7th Armored, 20 Nov 1944: rest near Maastricht, open span', A('US-ARM-007D', '1944-11-20'), ('refitting', 'possible', 'stated', 0.5))


ROLLOUT_2 = ['US-ABN-017D'] + ['US-ARM-%03dD' % n for n in (9, 11, 13, 16, 20)] + ['US-INF-%03dD' % n for n in (26, 42, 44, 63, 65, 66, 70, 71, 75, 76, 78, 84, 86, 87, 94, 97, 99, 100, 102, 103, 104, 106)] + ['UK-ARM-011D', 'UK-INF-015D']


def scenario_28_activity_rollout_2():
    """Activity rollout, batch 2 (October 2026): the remaining 28 US divisions and two British divisions; existing rows labelled, then new rest/refit, line, garrison, span-closing and 8 May 1945 claims (C1905-C1987) from the CMH combat chronicles and Wikipedia."""
    s = 'scenario 28'
    import activity
    A = lambda u, d: (lambda r: r and (r['activity'], r['status'], r['support'], r['confidence']))(activity.activity_at(u, d))
    claims = common.load_all_claims()[1]
    rows = [c for c in claims if c.get('activity_status') and NOT_OHP(c) and c['unit_id'] in ROLLOUT_2]
    expect(s + ': batch 2 covers 30 units', len({c['unit_id'] for c in rows}), 30)
    expect(s + ': batch 2 has 143 activity rows', len(rows), 143)
    expect(s + ': batch 2 has 125 stated and 18 inferred rows', (sum(c['activity_basis'] == 'stated' for c in rows), sum(c['activity_basis'] == 'inferred' for c in rows)), (125, 18))
    expect(s + ': 106th Division, 30 Dec 1944: refitting at Anthisnes (stated span to 9 Jan)', A('US-INF-106D', '1944-12-30'), ('refitting', 'certain', 'stated', 0.5))
    expect(s + ': 106th Division, 12 Jan 1945: no answer after the refit ends', A('US-INF-106D', '1945-01-12'), None)
    expect(s + ': 94th Division, 15 Nov 1944: containing the Brittany ports is in the line', A('US-INF-094D', '1944-11-15'), ('in_line', 'certain', 'stated', 0.5))
    expect(s + ': 94th Division, 4 Jan 1945: relieved on 1 Jan, so no answer', A('US-INF-094D', '1945-01-04'), None)
    expect(s + ': 87th Division, 26 Dec 1944: SHAEF reserve (implicit end, so inferred)', A('US-INF-087D', '1944-12-26'), ('reserve', 'certain', 'inferred', 0.3))
    expect(s + ': 100th Division, 8 May 1945: occupation at Goppingen', A('US-INF-100D', '1945-05-08'), ('garrison', 'certain', 'stated', 0.5))
    expect(s + ': 13th Armored, 5 May 1945: out of the line after 3 May, so no answer', A('US-ARM-013D', '1945-05-05'), None)
    expect(s + ': 9th Armored, 8 May 1945: shifting south (inferred, capped at 0.3)', A('US-ARM-009D', '1945-05-08'), ('in_line', 'certain', 'inferred', 0.3))
    expect(s + ': 15th (Scottish), 30 Jun 1944: in the line at Epsom (closed 2 Jul)', A('UK-INF-015D', '1944-06-30'), ('in_line', 'certain', 'stated', 0.3))
    expect(s + ': 15th (Scottish), 10 Jul 1944: no answer between Epsom and Caumont', A('UK-INF-015D', '1944-07-10'), None)
    expect(s + ': 86th Division, 8 May 1945: securing the XV Corps left flank at Burghausen (point)', A('US-INF-086D', '1945-05-08'), ('in_line', 'certain', 'stated', 0.3))
    expect(s + ': 11th Armoured, 5 Apr 1945: open span from the Rhine crossing at Wesel', A('UK-ARM-011D', '1945-04-05'), ('in_line', 'possible', 'stated', 0.5))


ROLLOUT_3 = ['UK-ABN-006D', 'UK-ARM-007D', 'UK-ARM-079D', 'UK-ARM-GRDD'] + ['UK-INF-%03dD' % n for n in (3, 43, 49, 51, 52, 53, 59)]


def scenario_29_activity_rollout_3():
    """Activity rollout, batch 3 (October 2026): the remaining 11 British divisions; existing rows labelled, then new rest, transit, line, span-closing and 8 May 1945 claims (C1988-C1996) from Wikipedia and one CMH combat chronicle."""
    s = 'scenario 29'
    import activity
    A = lambda u, d: (lambda r: r and (r['activity'], r['status'], r['support'], r['confidence']))(activity.activity_at(u, d))
    claims = common.load_all_claims()[1]
    rows = [c for c in claims if c.get('activity_status') and NOT_OHP(c) and c['unit_id'] in ROLLOUT_3]
    expect(s + ': batch 3 covers 11 units', len({c['unit_id'] for c in rows}), 11)
    expect(s + ': batch 3 has 98 activity rows', len(rows), 98)
    expect(s + ': batch 3 has 89 stated and 9 inferred rows', (sum(c['activity_basis'] == 'stated' for c in rows), sum(c['activity_basis'] == 'inferred' for c in rows)), (89, 9))
    expect(s + ': 6th Airborne, 15 Jul 1944: in the line in Normandy (span 6 Jun to 26 Aug)', A('UK-ABN-006D', '1944-07-15'), ('in_line', 'certain', 'stated', 0.5))
    expect(s + ': 6th Airborne, 10 Sep 1944: back in England, so no answer', A('UK-ABN-006D', '1944-09-10'), None)
    expect(s + ': 6th Airborne, 10 Feb 1945: on the Maas near Roermond (closed 21 Feb)', A('UK-ABN-006D', '1945-02-10'), ('in_line', 'certain', 'stated', 0.3))
    expect(s + ': 6th Airborne, 1 Mar 1945: relieved by the US 75th Division, so no answer', A('UK-ABN-006D', '1945-03-01'), None)
    expect(s + ': 7th Armoured, 8 May 1945: holding Hamburg (inferred, capped at 0.3)', A('UK-ARM-007D', '1945-05-08'), ('garrison', 'certain', 'inferred', 0.3))
    expect(s + ': 49th Division, 8 May 1945: Utrecht after the surrender (inferred)', A('UK-INF-049D', '1945-05-08'), ('garrison', 'certain', 'inferred', 0.3))
    expect(s + ': 43rd Division, 29 Aug 1944: rest after the Seine crossing', A('UK-INF-043D', '1944-08-29'), ('refitting', 'certain', 'stated', 0.3))
    expect(s + ': 3rd Division, 20 Jun 1944: D-Day entry is a point (no closing source), so no answer', A('UK-INF-003D', '1944-06-20'), None)


GERMAN_1 = ['GER-PZ-LEHRD'] + ['GER-%s' % u for u in 'SSPZ-012D FJ-003D PZ-116D PZ-021D SSPG-017D PZ-009D SSPZ-001D SSPZ-002D INF-353D PZ-011D FJ-005D PZ-002D INF-716D INF-084D INF-198D PG-003D INF-352D PG-015D INF-709D INF-338D VG-012D INF-245D PG-025D INF-059D INF-275D VG-246D LL-091D INF-089D INF-346D'.split()]


def scenario_30_activity_german_1():
    """German activity rollout, batch 1 (October 2026): 30 German divisions with the most claims; existing rows labelled (no new claims)."""
    s = 'scenario 30'
    import activity
    A = lambda u, d: (lambda r: r and (r['activity'], r['status'], r['support'], r['confidence']))(activity.activity_at(u, d))
    claims = common.load_all_claims()[1]
    rows = [c for c in claims if c.get('activity_status') and NOT_OHP(c) and c['unit_id'] in GERMAN_1]
    expect(s + ': German batch 1 covers 30 units', len({c['unit_id'] for c in rows}), 30)
    expect(s + ': German batch 1 has 148 activity rows', len(rows), 148)
    expect(s + ': German batch 1 has 122 stated and 26 inferred rows', (sum(c['activity_basis'] == 'stated' for c in rows), sum(c['activity_basis'] == 'inferred' for c in rows)), (122, 26))
    expect(s + ': German batch 1 rows are all points', {c['activity_span'] for c in rows}, {'point'})
    expect(s + ': 12th SS Panzer, 11 Jul 1944: sent to refit at Potigny', A('GER-SSPZ-012D', '1944-07-11'), ('refitting', 'certain', 'stated', 0.5))
    expect(s + ': 12th SS Panzer, 12 Jul 1944: a point, so no answer the next day', A('GER-SSPZ-012D', '1944-07-12'), None)
    expect(s + ': 9th Panzer, 23 Feb 1945: Army Group B reserve', A('GER-PZ-009D', '1945-02-23'), ('reserve', 'certain', 'stated', 0.5))
    expect(s + ': 716th Static, 10 Jul 1944: coastal sector in the south of France is garrison', A('GER-INF-716D', '1944-07-10'), ('garrison', 'certain', 'stated', 0.5))
    expect(s + ': 709th Static, 26 Jun 1944: Cherbourg fortress defence is in the line', A('GER-INF-709D', '1944-06-26'), ('in_line', 'certain', 'stated', 0.7))
    expect(s + ': 1st SS Panzer, 16 Dec 1944: ready to exploit (inferred reserve, 0.3)', A('GER-SSPZ-001D', '1944-12-16'), ('reserve', 'certain', 'inferred', 0.3))


GERMAN_2 = ['GER-%s' % u for u in 'INF-159D INF-180D INF-243D FJ-006D FJ-007D FJ-008D INF-048D INF-077D INF-176D INF-189D INF-269D INF-347D INF-711D VG-026D VG-326D VG-340D VG-553D VG-559D INF-049D INF-064D INF-070D INF-085D INF-271D INF-272D INF-712D INF-719D PZ-CLAUS VG-016D VG-062D VG-272D'.split()]


def scenario_31_activity_german_2():
    """German activity rollout, batch 2 (October 2026): the next 30 unlabelled German divisions by claim count; existing rows labelled (no new claims). Five of them (180th, 6th Fallschirmjäger, 85th, 712th, 719th) have only order-of-battle listings and stay blank."""
    s = 'scenario 31'
    import activity
    A = lambda u, d: (lambda r: r and (r['activity'], r['status'], r['support'], r['confidence']))(activity.activity_at(u, d))
    claims = common.load_all_claims()[1]
    rows = [c for c in claims if c.get('activity_status') and NOT_OHP(c) and c['unit_id'] in GERMAN_2]
    expect(s + ': German batch 2 labels 25 of its 30 units', len({c['unit_id'] for c in rows}), 25)
    expect(s + ': German batch 2 has 45 activity rows', len(rows), 45)
    expect(s + ': German batch 2 has 34 stated and 11 inferred rows', (sum(c['activity_basis'] == 'stated' for c in rows), sum(c['activity_basis'] == 'inferred' for c in rows)), (34, 11))
    expect(s + ': German batch 2 rows are all points', {c['activity_span'] for c in rows}, {'point'})
    expect(s + ': 70th Division, 18 Sep 1944: Walcheren fortress before the attack is garrison', A('GER-INF-070D', '1944-09-18'), ('garrison', 'certain', 'stated', 0.7))
    expect(s + ': 269th Division, 18 Jan 1945: on its way to the Eastern Front', A('GER-INF-269D', '1945-01-18'), ('transit', 'certain', 'stated', 0.5))
    expect(s + ': 326th VG, 17 Mar 1945: contingents at Remagen (inferred, 0.3)', A('GER-VG-326D', '1945-03-17'), ('in_line', 'certain', 'inferred', 0.3))
    expect(s + ': 85th Division: listings only, so no answer', A('GER-INF-085D', '1944-12-15'), None)


GERMAN_3 = ['GER-%s' % u for u in 'VG-276D VG-277D VG-361D VG-560D VG-708D FJ-002D GEB-002D INF-226D INF-277D INF-344D INF-363D INF-416D INF-462D INF-708D INF-HUTTN INF-SCHRN SSGEB-006D VG-018D VG-019D VG-036D VG-047D VG-183D VG-212D VG-256D VG-352D VG-462D'.split()]


def scenario_32_activity_german_3():
    """German activity rollout, batch 3 (October 2026): the last 26 unlabelled German divisions; existing rows labelled (no new claims). Four (2nd Fallschirmjäger, 226th, 416th, 6th SS Mountain) have no row that carries a state and stay blank."""
    s = 'scenario 32'
    import activity
    A = lambda u, d: (lambda r: r and (r['activity'], r['status'], r['support'], r['confidence']))(activity.activity_at(u, d))
    claims = common.load_all_claims()[1]
    rows = [c for c in claims if c.get('activity_status') and NOT_OHP(c) and c['unit_id'] in GERMAN_3]
    expect(s + ': German batch 3 labels 22 of its 26 units', len({c['unit_id'] for c in rows}), 22)
    expect(s + ': German batch 3 has 25 activity rows', len(rows), 25)
    expect(s + ': German batch 3 has 20 stated and 5 inferred rows', (sum(c['activity_basis'] == 'stated' for c in rows), sum(c['activity_basis'] == 'inferred' for c in rows)), (20, 5))
    expect(s + ': German batch 3 rows are all points', {c['activity_span'] for c in rows}, {'point'})
    expect(s + ': 462nd VG, 9 Nov 1944: the Metz garrison under attack is in the line', A('GER-VG-462D', '1944-11-09'), ('in_line', 'certain', 'stated', 0.5))
    expect(s + ': 344th Division, 20 Nov 1944: behind the 275th (inferred reserve, 0.3)', A('GER-INF-344D', '1944-11-20'), ('reserve', 'certain', 'inferred', 0.3))
    expect(s + ': 226th Division: listing only, so no answer', A('GER-INF-226D', '1944-12-15'), None)


CAN_FR = ['CAN-ARM-005D', 'CAN-INF-001D', 'CAN-INF-003D', 'FR-ARM-001D', 'FR-ARM-005D', 'FR-INF-001D', 'FR-INF-002D', 'FR-INF-004D', 'FR-INF-009D', 'FR-INF-010D', 'FR-INF-014D', 'FR-INF-027D', 'FR-INF-GIRONDE']


def scenario_33_activity_canada_france():
    """Activity rollout, Canada and France (October 2026): 3 Canadian and 10 French divisions; existing rows labelled, then new line, transit, reserve and 8 May 1945 claims (C1997-C2002) from Wikipedia and de Lattre (paraphrased)."""
    s = 'scenario 33'
    import activity
    A = lambda u, d: (lambda r: r and (r['activity'], r['status'], r['support'], r['confidence']))(activity.activity_at(u, d))
    claims = common.load_all_claims()[1]
    rows = [c for c in claims if c.get('activity_status') and c['unit_id'] in CAN_FR and ('Canada and France' in c['notes'] or c['claim_id'] in ('C1997', 'C2002'))]   # C1997 and C2002 were relabelled by the source fixes of 30 October 2026 (scenario 35) and stay rows of this batch
    expect(s + ': the batch covers 13 units', len({c['unit_id'] for c in rows}), 13)
    expect(s + ': the batch has 63 activity rows (64 before C1636 was retired on 30 October 2026)', len(rows), 63)
    expect(s + ': the batch has 43 stated and 20 inferred rows (C1636, stated, was retired on 30 October 2026; C1997 is inferred reserve since the source fixes of 30 October 2026; it was stated transit)', (sum(c['activity_basis'] == 'stated' for c in rows), sum(c['activity_basis'] == 'inferred' for c in rows)), (43, 20))
    expect(s + ': 3rd Canadian, 1 Jul 1944: in the line from D-Day (closed 31 Jul)', A('CAN-INF-003D', '1944-07-01'), ('in_line', 'certain', 'stated', 0.5))
    expect(s + ': 3rd Canadian, 5 Aug 1944: rest after 55 days, so no answer', A('CAN-INF-003D', '1944-08-05'), None)
    expect(s + ': 1st Canadian, 8 May 1945: takes control of a German corps area (garrison)', A('CAN-INF-001D', '1945-05-08'), ('garrison', 'certain', 'stated', 0.3))
    expect(s + ': 4th Moroccan Mountain, 8 May 1945: in the Vorarlberg (inferred)', A('FR-INF-004D', '1945-05-08'), ('in_line', 'certain', 'inferred', 0.3))
    expect(s + ': 5th Armoured (France), 24 Nov 1944: fighting on the Seppois roads (inferred in_line; changed from reserve by the source fixes of 30 October 2026, de Lattre p. 268)', A('FR-ARM-005D', '1944-11-24'), ('in_line', 'certain', 'inferred', 0.3))


def scenario_34_official_history_pass_1():
    """Official-history pass 1 (October 2026): 8 May 1945 rows, span closures and the first activity rows of 8 blank German divisions (C2003-C2030) from The Last Offensive, Conquer (Ninth Army), Stacey and de Lattre (paraphrased)."""
    s = 'scenario 34'
    import activity
    A = lambda u, d: (lambda r: r and (r['activity'], r['status'], r['support'], r['confidence']))(activity.activity_at(u, d))
    claims = common.load_all_claims()[1]
    rows = [c for c in claims if c.get('activity_status') and 'official-history pass' in c['notes']]
    expect(s + ': the pass has 28 activity rows in 24 units', (len(rows), len({c['unit_id'] for c in rows})), (28, 24))
    expect(s + ': the pass has 12 stated and 16 inferred rows', (sum(c['activity_basis'] == 'stated' for c in rows), sum(c['activity_basis'] == 'inferred' for c in rows)), (12, 16))
    expect(s + ': 75th Division, 20 Apr 1945: the rest span now ends by the occupation start of 22 Apr (inferred end)', A('US-INF-075D', '1945-04-20'), ('refitting', 'certain', 'inferred', 0.3))
    expect(s + ': 75th Division, 25 Apr 1945: occupation zone in the Ruhr (open span)', A('US-INF-075D', '1945-04-25'), ('garrison', 'possible', 'stated', 0.3))
    expect(s + ': 2nd Armored, 8 May 1945: assembled for Task Force Berlin (inferred garrison)', A('US-ARM-002D', '1945-05-08'), ('garrison', 'certain', 'inferred', 0.3))
    expect(s + ': 3rd Canadian, 8 May 1945: after the cease fire (inferred garrison)', A('CAN-INF-003D', '1945-05-08'), ('garrison', 'certain', 'inferred', 0.3))
    expect(s + ': 416th Infantry (German), 15 Jan 1945: holds the Orscholz Switch', A('GER-INF-416D', '1945-01-15'), ('in_line', 'certain', 'stated', 0.5))
    expect(s + ': 712th Infantry (German), 24 Dec 1944: a point does not spread to the next day', A('GER-INF-712D', '1944-12-24'), None)


def scenario_35_source_fixes_delattre_ellis():
    """Source fixes from de Lattre and Ellis (October 2026): 28 new claims (C2031-C2058), 10 changed rows, conflict group G028 (2nd Moroccan Division, 3 April 1945)."""
    s = 'scenario 35'
    import activity
    A = lambda u, d: (lambda r: r and (r['activity'], r['status'], r['support'], r['confidence']))(activity.activity_at(u, d))
    claims = common.load_all_claims()[1]
    new = [c for c in claims if 'C2031' <= c['claim_id'] <= 'C2058']
    expect(s + ': the batch adds 28 claims in 14 units', (len(new), len({c['unit_id'] for c in new})), (28, 14))
    expect(s + ': every new claim carries an activity value', sum(bool(c.get('activity_status')) for c in new), 28)
    by = {c['claim_id']: c for c in claims}
    expect(s + ': 4th Moroccan Mountain, 12 Jan 1945: at Lure, not Vieux-Thann', (by['C1997']['place_id'], by['C1997']['activity_status']), ('PL0987', 'reserve'))
    expect(s + ': group G028: Bruchsal preferred, Karlsruhe alternate', (by['C2050']['claim_status'], by['C1639']['claim_status'], by['C1639']['conflict_group_id']), ('preferred', 'alternate', 'G028'))
    expect(s + ': 9th Colonial, 4 Apr 1945: takes Karlsruhe (stated in_line)', A('FR-INF-009D', '1945-04-04'), ('in_line', 'certain', 'stated', 0.5))
    expect(s + ': 15th Panzergrenadier (German), 14 Oct 1944: moving to Venlo (inferred transit)', A('GER-PG-015D', '1944-10-14'), ('transit', 'certain', 'inferred', 0.3))
    expect(s + ': British 5th Division, 2 May 1945: behind the 11th Armoured at Lübeck (inferred reserve)', A('UK-INF-005D', '1945-05-02'), ('reserve', 'certain', 'inferred', 0.3))


def scenario_36_fms_b466_geyr():
    """FMS B-466 (Geyr von Schweppenburg) batch: 18 new German rows, conflict group G029, R761 added to 18 rows."""
    s = 'scenario 36'
    import activity
    A = lambda u, d: (lambda r: r and (r['activity'], r['status'], r['support'], r['confidence']))(activity.activity_at(u, d))
    claims = common.load_all_claims()[1]
    new = [c for c in claims if BATCH36(c)]
    by = {c['claim_id']: c for c in claims}
    expect(s + ': the batch adds 18 claims in 13 units', (len(new), len({c['unit_id'] for c in new})), (18, 13))
    expect(s + ': every new claim cites R761', sum('R761' in c['reference_ids'].split(';') for c in new), 18)
    expect(s + ': R761 added to 18 earlier rows', sum('R761' in c['reference_ids'].split(';') for c in claims if not BATCH36(c)), 18)
    expect(s + ': group G029: Thury-Harcourt preferred, Aunay-sur-Odon alternate', (by['C0053']['claim_status'], by['C2069']['claim_status'], by['C2069']['conflict_group_id']), ('preferred', 'alternate', 'G029'))
    expect(s + ': arrival rows capped at 0.3', tuple(by[i]['confidence'] for i in ('C2075', 'C2076', 'C2077')), ('0.3', '0.3', '0.3'))
    expect(s + ': LXXXVI Corps, 25 Jun 1944: in the line from 20 June, carried forward (possible, stated, 0.3)', A('GER-COR-086C', '1944-06-25'), ('in_line', 'possible', 'stated', 0.3))


def scenario_37_fms_19army():
    """FMS 19th Army batch (B-766, B-263, B-463, B-468, B-550): 38 new rows, conflict groups G030-G032, strength fill of 13 January 1945."""
    s = 'scenario 37'
    import json
    claims = common.load_all_claims()[1]
    new = [c for c in claims if BATCH37(c)]
    by = {c['claim_id']: c for c in claims}
    FMS = {'R762', 'R763', 'R764', 'R765', 'R766'}
    expect(s + ': the batch adds 38 claims', len(new), 38)
    expect(s + ': 35 preferred rows and 3 alternates', (sum(c['claim_status'] == 'preferred' for c in new), sum(c['claim_status'] == 'alternate' for c in new)), (35, 3))
    expect(s + ': 35 new rows cite an FMS manuscript (the 3 others are de Lattre-only roadmap rows)', sum(bool(FMS & set(c['reference_ids'].split(';'))) for c in new), 35)
    expect(s + ': groups G030-G032: CMH/Lexikon dates preferred, FMS dates alternate', tuple((by[a]['claim_status'], by[b]['claim_status'], by[b]['conflict_group_id']) for a, b in (('C1018', 'C2113'), ('C1188', 'C2114'), ('C1189', 'C2115'))),
           (('preferred', 'alternate', 'G030'), ('preferred', 'alternate', 'G031'), ('preferred', 'alternate', 'G032')))
    expect(s + ': arrival and departure rows capped at 0.3', tuple(by[i]['confidence'] for i in ('C2082', 'C2087', 'C2090', 'C2100')), ('0.3', '0.3', '0.3', '0.3'))
    expect(s + ': Nineteenth Army headquarters at Guebwiller (6 Oct 1944) and Kirchhofen (5 Feb 1945)', (by['C2084']['place_id'], by['C2096']['place_id']), ('PL1016', 'PL1017'))
    expect(s + ': 13 January strengths: 198th 421, 16th VG 1728', (json.loads(by['C1118']['strength_json'])['personnel'], json.loads(by['C1120']['strength_json'])['personnel']), (421, 1728))
    expect(s + ': 189th Division commander Zorn on 20 Jan 1945', by['C1117']['commander'].startswith('Generalmajor Zorn'), True)


def scenario_39_fms_b811_15army():
    """FMS B-811 (von Zangen, Fifteenth Army, 15 Nov 1944-22 Feb 1945): 8 new rows, R768 on C1089 and C1140."""
    s = 'scenario 39'
    claims = common.load_all_claims()[1]
    new = [c for c in claims if BATCH39(c)]
    by = {c['claim_id']: c for c in claims}
    expect(s + ': the batch adds 8 claims, all citing R768', (len(new), sum('R768' in c['reference_ids'].split(';') for c in new)), (8, 8))
    expect(s + ': Fifteenth Army takes over at Königshoven on 22 November 1944', (by['C2127']['date'], by['C2127']['place_id']), ('1944-11-22', 'PL1039'))
    expect(s + ': FMS-only changes keep a blank parent', tuple(by[i]['parent_unit_id'] for i in ('C2128', 'C2129', 'C2131', 'C2133')), ('', '', '', ''))
    expect(s + ': arrivals and approximate days capped at 0.3', tuple(by[i]['confidence'] for i in ('C2130', 'C2132', 'C2134')), ('0.3', '0.3', '0.3'))
    expect(s + ': B-811 added as second source to C1089 and C1140', tuple('R768' in by[i]['reference_ids'] for i in ('C1089', 'C1140')), (True, True))


def main():
    for fn in (scenario_0_staleness, scenario_1_first_army, scenario_2_viii_corps, scenario_3_84th_division, scenario_4_administrative_versus_operational, scenario_6_german_parent_changes_1944, scenario_7_german_batch_1b_july_1944, scenario_8_german_batch_2_sep_oct_1944, scenario_9_german_batch_2_followup_model_lxxx, scenario_10_german_batch_3_nov_dec_1944, scenario_11_german_1945_batch_1_jan_mar, scenario_12_german_1945_batch_2_apr_may, scenario_13_cleanup_open_items_oct28, scenario_14_canadian_batch_1_jun_dec_1944, scenario_15_canadian_batch_2_jan_may_1945, scenario_16_british_batch_1_jun_dec_1944, scenario_17_british_batch_2_jan_may_1945, scenario_18_british_batch_2_followup, scenario_19_allied_contingents_1944_45, scenario_20_french_1944_45, scenario_21_french_followup, scenario_22_french_delattre, scenario_23_brigades_batch_1_uk_can, scenario_24_brigades_batch_2_us, scenario_25_brigades_batch_3_german, scenario_26_activity_pilot, scenario_27_activity_rollout_1, scenario_28_activity_rollout_2, scenario_29_activity_rollout_3, scenario_30_activity_german_1, scenario_31_activity_german_2, scenario_32_activity_german_3, scenario_33_activity_canada_france, scenario_34_official_history_pass_1, scenario_35_source_fixes_delattre_ellis, scenario_36_fms_b466_geyr, scenario_37_fms_19army, scenario_39_fms_b811_15army):
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
