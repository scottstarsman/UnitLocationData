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


def main():
    for fn in (scenario_0_staleness, scenario_1_first_army, scenario_2_viii_corps, scenario_3_84th_division, scenario_4_administrative_versus_operational, scenario_6_german_parent_changes_1944, scenario_7_german_batch_1b_july_1944, scenario_8_german_batch_2_sep_oct_1944, scenario_9_german_batch_2_followup_model_lxxx, scenario_10_german_batch_3_nov_dec_1944, scenario_11_german_1945_batch_1_jan_mar, scenario_12_german_1945_batch_2_apr_may, scenario_13_cleanup_open_items_oct28):
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
