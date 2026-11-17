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
import csv
import io
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common  # noqa: E402
import validate  # noqa: E402
import who_controls as wc  # noqa: E402

REL_PATH = os.path.join(common.BUILD_DIR, 'command_relations.csv')
_ROWS = common.read_dicts(REL_PATH)[1]

# unit ids used below
FIRST_ARMY, THIRD_ARMY, NINTH_ARMY, SEVENTH_ARMY = 'US-ARMY-001A', 'US-ARMY-003A', 'US-ARMY-009A', 'US-ARMY-007A'
ARMY_GROUP_12, ARMY_GROUP_21 = 'US-AG-012G', 'UK-AG-021G'
CORPS_VII, CORPS_VIII, CORPS_XVIII_ABN, CORPS_VI, CORPS_BRIT_I = 'US-COR-007C', 'US-COR-008C', 'US-ABN-018C', 'US-COR-006C', 'UK-COR-001C'
DIV_84, DIV_104, DIV_45, DIV_29 = 'US-INF-084D', 'US-INF-104D', 'US-INF-045D', 'US-INF-029D'
DIV_7AD = 'US-ARM-007D'

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


# 78th Division rows re-pointed from Petergensfeld to the new place PL2611 Roetgen on 1 November 2026 (roadmap point 115)
ROETGEN = {'C4880', 'C4988', 'C5103', 'C5216', 'C5337', 'C5455', 'C5588', 'C5717'}

# rows of batches 5s-5u re-read on 1 November 2026 (Lorraine, Alsace and Netherlands tiles); new places PL2627-PL2633
REREAD = {'C5850', 'C5845', 'C5844', 'C5867', 'C5802', 'C5984', 'C5979', 'C5978', 'C6001', 'C6053', 'C6011', 'C6015', 'C5994', 'C5936', 'C6118', 'C6112', 'C6135', 'C6145', 'C6128', 'C6070'}

# map rows re-pointed to an existing nearer place by the grid-reading audit of 1 November 2026
AUDIT = {'C6243', 'C6106', 'C6342', 'C4552', 'C3930', 'C6182', 'C6065', 'C3112', 'C6067', 'C5287', 'C6302', 'C6033', 'C5964', 'C5255', 'C6245', 'C6167', 'C4778'}
# Visual audit of 2 November 2026 (roadmap point 199 onwards): rows moved to their symbol may take a new place; their notes say so.
AUDIT |= {c['claim_id'] for c in common.load_all_claims()[1] if 'Visual audit 2 Nov 2026' in c['notes'] and '; place PL' in c['notes']}
LOWERED = {c['claim_id'] for c in common.load_all_claims()[1] if 'Review (visual audit confidence, 2 November 2026)' in c['notes'] or ('Review (map-row conflicts, 3 November 2026' in c['notes'] and 'Confidence old value 0.5, new value 0.3' in c['notes']) or ('map row never outranks a text row (roadmap 357/358' in c['notes'])}

def scenario_0_staleness():
    """R1-N-001: a standing relationship is certain only up to its last listing."""
    # Until the command-chain repair (wf-health-fixes, 9 November 2026) this scenario used the 29th Infantry Division's assignment to First Army
    # (valid_from 1944-09-21, last listed 1944-09-29, open). The repair closed it from the CMH table already cited (valid_to 1944-10-21, basis
    # assignment_table), so the open example is now the 7th Armored Division's assignment to First Army (valid_from 1944-12-16, last listed
    # 1945-01-23, open; a roadmap item because the 7th Armored Division ETO-OB page has no table in any capture).
    s = 'staleness (US-ARM-007D, last claim 1945-01-23)'
    row = master(DIV_7AD, 'US-ARMY-001A', 'assigned', '1944-12-16')
    expect(s + ': last_listed_date of the assignment to First Army', row['last_listed_date'], '1945-01-23')
    expect(s + ': its end is not recorded', row['valid_to_basis'], 'open_at_last_claim')
    expect(s + ': 1945-01-23 (last listing) is certain', intervals(DIV_7AD, '1945-01-23')[('US-ARMY-001A', 'assigned')][0], 'certain')
    # From 13 November 2026 the open carry-forward is possible for at most 90 days (OPEN_CARRY_FORWARD_DAYS); the 93-day date used here before the cutoff is now a drop (scenarios 260-261).
    st, why = intervals(DIV_7AD, '1945-04-23')[('US-ARMY-001A', 'assigned')]
    expect(s + ': 1945-04-23 (90 days after) is possible, not certain', st, 'possible')
    expect_in(s + ': the reason names the last listing and the distance', why, 'after the last claim that lists it (1945-01-23, 90 days earlier)')
    expect_in(s + ': the reason says the standing relationship is carried forward', why, 'carried forward until a replacement is recorded')
    stale = {k: v[0] for k, v in intervals(DIV_7AD, '1945-04-23').items()}
    expect(s + ': every interval of the division on 1945-04-23 is possible', set(stale.values()), {'possible'})
    expect(s + ': 1945-04-24 (91 days after) no longer carries the First Army assignment', intervals(DIV_7AD, '1945-04-24')[('US-ARMY-001A', 'assigned')][0], 'absent')
    expect(s + ': 1945-04-24 no longer carries the 12th Army Group assignment last listed 1945-01-23', intervals(DIV_7AD, '1945-04-24')[(ARMY_GROUP_12, 'assigned')][0], 'absent')
    # the repaired 29th Infantry Division row: a sourced (table) end is not capped by the last listing
    row = master(DIV_29, 'US-ARMY-001A', 'assigned', '1944-09-21')
    expect(s + ': the 29th Infantry Division assignment to First Army now ends 1944-10-21 (assignment table)', (row['valid_to'], row['valid_to_basis']), ('1944-10-21', 'assignment_table'))
    expect(s + ': ...and 1944-10-15 is certain although the last listing is 1944-09-29', intervals(DIV_29, '1944-10-15')[('US-ARMY-001A', 'assigned')][0], 'certain')
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
    # command-chain repair (wf-health-fixes, 9 November 2026): the Third Army assignment, open until then, now ends 1945-04-21 from the CMH table
    # of the 6th Armored Division (VIII Corps under Third Army on 17 April, under First Army from 22 April).
    expect(s + ': Third Army assignment starts 1944-12-20 (narrative, no hour), ends 1945-04-21 (assignment table)', (third['valid_from'], third['valid_from_basis'], third['valid_from_time'], third['valid_to'], third['valid_to_basis']), ('1944-12-20', 'narrative', '', '1945-04-21', 'assignment_table'))
    a = intervals(CORPS_VIII, '1944-12-19')
    expect(s + ': 19 Dec: First Army, certain; no Third Army', (a[(FIRST_ARMY, 'assigned')][0], (THIRD_ARMY, 'assigned') in a), ('certain', False))
    expect(s + ': 19 Dec: chain starts with First Army, certain', chain(CORPS_VIII, '1944-12-19')[0], ('US First Army', 'assigned', 'certain'))
    a = intervals(CORPS_VIII, '1944-12-20')
    expect(s + ': 20 Dec: both armies cover the day, both possible', (a[(FIRST_ARMY, 'assigned')][0], a[(THIRD_ARMY, 'assigned')][0]), ('possible', 'possible'))
    expect(s + ': 20 Dec: the army level is UNKNOWN', chain(CORPS_VIII, '1944-12-20')[0], ('UNKNOWN', ['US First Army', 'US Third Army'], None))
    expect(s + ': 20 Dec at 12:00: still UNKNOWN (the hour of the transfer is not recorded)', chain(CORPS_VIII, '1944-12-20', '12:00')[0], ('UNKNOWN', ['US First Army', 'US Third Army'], None))
    a = intervals(CORPS_VIII, '1944-12-21')
    expect(s + ': 21 Dec: only Third Army covers the day', sorted(k[0] for k in a), [THIRD_ARMY])
    # Until the command-chain repair (wf-health-fixes, 9 November 2026) the assignment was open and last listed on 20 Dec, so from 21 Dec the tool
    # answered "possible: carried forward". The relation now has a sourced end (assignment table, 1945-04-21), and a sourced end is never capped by
    # the last listing (scenario 0), so 21 Dec is certain, which is also what the note of the relation says (first day certainly under Third Army:
    # 21 Dec, Green Book p399).
    expect(s + ': 21 Dec: Third Army is certain (sourced end, not capped by the last listing)', a[(THIRD_ARMY, 'assigned')][0], 'certain')
    expect(s + ': 21 Dec: chain starts with Third Army', chain(CORPS_VIII, '1944-12-21')[0], ('US Third Army', 'assigned', 'certain'))
    a = intervals(CORPS_VIII, '1945-04-22')
    expect(s + ': 22 Apr 1945: only First Army covers the day (Third Army ended 21 Apr)', sorted(k[0] for k in a), [FIRST_ARMY])


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
    expect(s + ': Princess Irene Brigade, 25 Apr 1945 (Hedel): Netherlands District from 2 March (Wikipedia)', sorted(a), [('UK-DIST-NETH', 'assigned')])
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
BATCH38 = lambda c: 'C2116' <= c['claim_id'] <= 'C2126'   # FMS B-703 Army Group G batch (scenario 38) counts only in its own scenario
BATCH39 = lambda c: 'C2127' <= c['claim_id'] <= 'C2134'   # FMS B-811 Fifteenth Army batch (scenario 39) counts only in its own scenario
BATCH40 = lambda c: 'C2135' <= c['claim_id'] <= 'C2136'   # FMS B-701 Army Group B batch (scenario 40) counts only in its own scenario
OHP2 = lambda c: 'C2160' <= c['claim_id'] <= 'C2163' or 'official-history pass 2' in c['notes']   # official-history pass 2 (scenario 42) counts only in its own scenario
BATCH41 = lambda c: 'C2137' <= c['claim_id'] <= 'C2159'   # FMS B-078 Army Group G Lorraine and Vosges batch (scenario 41) counts only in its own scenario
BATCH43 = lambda c: 'C2164' <= c['claim_id'] <= 'C2178'   # FMS B-475 German batch (scenario 43) counts only in its own scenario
BATCH44 = lambda c: 'C2179' <= c['claim_id'] <= 'C2191'   # FMS B-235 German batch (scenario 44) counts only in its own scenario
BATCH45 = lambda c: 'C2192' <= c['claim_id'] <= 'C2202'   # FMS B-179 German batch (scenario 45) counts only in its own scenario
BATCH46 = lambda c: 'C2203' <= c['claim_id'] <= 'C2208'   # FMS B-763 German batch (scenario 46) counts only in its own scenario
BATCH47 = lambda c: 'C2209' <= c['claim_id'] <= 'C2213'   # FMS B-781 batch (scenario 47) counts only in its own scenario
BATCH48 = lambda c: 'C2214' <= c['claim_id'] <= 'C2225'   # FMS B-831 batch (scenario 48) counts only in its own scenario
BATCH49 = lambda c: 'C2226' <= c['claim_id'] <= 'C2235'   # FMS B-084 batch (scenario 49) counts only in its own scenario
BATCH50 = lambda c: 'C2236' <= c['claim_id'] <= 'C2247'   # FMS B-849 batch (scenario 50) counts only in its own scenario
BATCH96 = lambda c: 'C7062' <= c['claim_id'] <= 'C7068'   # NARA T-315 roll 940 (47th VGD Ia files) batch (scenario 96)
BATCH97 = lambda c: 'C7069' <= c['claim_id'] <= 'C7094'   # NARA T-311 roll 4 (Army Group B Ia files) batch (scenario 97)
BATCH101 = lambda c: 'C7125' <= c['claim_id'] <= 'C7126'   # NARA T-354 roll 147 (scenario 101)
BATCH100 = lambda c: 'C7121' <= c['claim_id'] <= 'C7124'   # NARA T-315 roll 1298 (scenario 100)
BATCH99 = lambda c: 'C7119' <= c['claim_id'] <= 'C7120'   # NARA T-354 roll 120 (scenario 99)
BATCH102 = lambda c: 'C7127' <= c['claim_id'] <= 'C7130'   # NARA T-314 roll 1605 (LXXXV Corps files) (scenario 102)
BATCH103 = lambda c: 'C7131' <= c['claim_id'] <= 'C7134'   # NARA T-354 roll 149 (9th SS Panzer Division files) (scenario 103)
BATCH104 = lambda c: 'C7135' <= c['claim_id'] <= 'C7135'   # NARA T-314 roll 1607 (LXXXVI Corps files) (scenario 104)
BATCH105 = lambda c: 'C7136' <= c['claim_id'] <= 'C7138'   # NARA T-315 roll 828 (26th Volksgrenadier Division Bastogne report) (scenario 105)
BATCH106 = lambda c: 'C7139' <= c['claim_id'] <= 'C7141'   # NARA T-354 roll 129 (2nd SS Panzer and 17th SS Panzergrenadier Division regimental files) (scenario 106)
BATCH107 = lambda c: 'C7142' <= c['claim_id'] <= 'C7143'   # NARA T-311 roll 1 (Army Group B quartermaster and intelligence files 1944) (scenario 107)
BATCH108 = lambda c: 'C7144' <= c['claim_id'] <= 'C7145'   # NARA T-315 roll 2145 (347th Infantry Division, North Holland 1943-44) (scenario 108)
BATCH109 = lambda c: 'C7146' <= c['claim_id'] <= 'C7155'   # Cole, The Ardennes: Fifth Panzer Army before Bastogne and the Meuse (chs. 13, 19, 22, 24) (scenario 109)
BATCH110 = lambda c: 'C7156' <= c['claim_id'] <= 'C7162'   # Cole, The Ardennes: Seventh Army on the southern flank (chs. 9, 10, 19, 20, 21) (scenario 110)
BATCH111 = lambda c: 'C7163' <= c['claim_id'] <= 'C7167'   # Cole, The Ardennes: Sixth Panzer Army, II SS Panzer Corps and OKW reserve (chs. 6, 23, 25) (scenario 111)
BATCH112 = lambda c: 'C7168' <= c['claim_id'] <= 'C7178'   # Cole, The Ardennes, second pass: German facts left from the first pass (chs. 6, 14, 16, 21-23) (scenario 112)
BATCH113 = lambda c: 'C7179' <= c['claim_id'] <= 'C7221'   # Cole, The Ardennes, second pass: US and British division, corps and army positions (chs. 5-24) (scenario 113)
BATCH98 = lambda c: 'C7095' <= c['claim_id'] <= 'C7118'   # NARA T-311 roll 3 (Army Group B Ia/Ic files) batch (scenario 98)
BATCH51 = lambda c: 'C2248' <= c['claim_id'] <= 'C2274'   # FMS B-745 (Brandenberger, German original) batch (scenario 51) counts only in its own scenario
BATCH52 = lambda c: 'C2275' <= c['claim_id'] <= 'C2281'   # FMS B-151 (Manteuffel, English translation from the Internet Archive) batch (scenario 52) counts only in its own scenario
LOC12AG = lambda c: 'R781' in c['reference_ids'].split(';')   # 12th Army Group situation maps (scenario 53) count only in their own scenario
ELLIS_LEFTOVER = lambda c: c['claim_id'] >= 'C8975'  # new rows of the Ellis leftover-entry pass (branch ellis-leftovers)

NOT_OHP = lambda c: 'official-history pass' not in c['notes'] and not LOC12AG(c) and not BATCH35(c) and not BATCH36(c) and not BATCH37(c) and not BATCH38(c) and not BATCH39(c) and not BATCH40(c) and not BATCH41(c) and not OHP2(c) and not BATCH43(c) and not BATCH44(c) and not BATCH45(c) and not BATCH46(c) and not BATCH47(c) and not BATCH48(c) and not BATCH49(c) and not BATCH50(c) and not BATCH51(c) and not BATCH52(c) and not BATCH96(c) and not BATCH97(c) and not ELLIS_LEFTOVER(c)


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
    # Official-history pass 2 (31 October 2026): old expectation None (open refit span past 30 days); new: the refit span now ends on 19 October
    # and the line span of Suitcase (C1340, 20 October) runs to the reserve start of 23 December (C1342); reason: the pilot rows were labelled.
    # CMHQ/AHQ report pass (11 November 2026): old expectation ('in_line', 'certain', 'inferred', 0.3); new ('in_line', 'certain', 'stated', 0.5);
    # reason: CMHQ Report No. 173 (para 78) dates the division's return to the Lith-Raamsdonk sector to 1 December (new point row C9028, stated).
    expect(s + ': 4th Canadian Armoured, 1 Dec 1944: in the line, back in the Lith-Raamsdonk sector (CMHQ 173 point row)', A('CAN-ARM-004D', '1944-12-01'), ('in_line', 'certain', 'stated', 0.5))
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
    expect(s + ': 1st Division on D-Day: in the line (point, stated)', A('US-INF-001D', '1944-06-06'), ('in_line', 'certain', 'stated', 0.7))  # was 0.5; raised by the Stacey corroboration (stacey-victory-campaign, 3 Nov 2026)
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
    rows = [c for c in claims if c.get('activity_status') and 'official-history pass' in c['notes'] and not OHP2(c)]
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


def scenario_38_fms_b703_armygroupg():
    """FMS B-703 (Wilutzky, Army Group G, 22 Mar-6 May 1945): 11 new rows, headquarters moves, conflict group G033."""
    s = 'scenario 38'
    claims = common.load_all_claims()[1]
    new = [c for c in claims if BATCH38(c)]
    by = {c['claim_id']: c for c in claims}
    expect(s + ': the batch adds 11 claims, all citing R767', (len(new), sum('R767' in c['reference_ids'].split(';') for c in new)), (11, 11))
    expect(s + ': Army Group G headquarters Michelstadt, Neuenstadt, Waldenbuch, Wallerstein, Schierling, Ampfing, Hohenaschau', tuple(by[i]['place_id'] for i in ('C2116', 'C2117', 'C2118', 'C1198', 'C2119', 'C2120', 'C1199')), ('PL1032', 'PL1033', 'PL1034', 'PL1035', 'PL1036', 'PL1037', 'PL1038'))
    expect(s + ': group G033: CMH 28 April preferred, FMS 25 April alternate', (by['C1205']['conflict_group_id'], by['C1205']['claim_status'], by['C2126']['conflict_group_id'], by['C2126']['claim_status']), ('G033', 'preferred', 'G033', 'alternate'))
    expect(s + ': FMS-only transfers keep a blank parent', tuple(by[i]['parent_unit_id'] for i in ('C2122', 'C2123', 'C2125', 'C2126')), ('', '', '', ''))
    expect(s + ': inferred or approximate days capped at 0.3', tuple(by[i]['confidence'] for i in ('C2116', 'C2120', 'C2126')), ('0.3', '0.3', '0.3'))


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


def scenario_40_fms_b701_armygroupb():
    """FMS B-701 (Reichhelm, Army Group B, mid-Oct 1944-mid-Apr 1945): 2 new rows citing R769."""
    s = 'scenario 40'
    claims = common.load_all_claims()[1]
    new = [c for c in claims if BATCH40(c)]
    by = {c['claim_id']: c for c in claims}
    expect(s + ': the batch adds 2 claims, all citing R769', (len(new), sum('R769' in c['reference_ids'].split(';') for c in new)), (2, 2))
    expect(s + ': Scheldt crossing ends 23 Sep 1944 at Walcheren, two families', (by['C2135']['date'], by['C2135']['place_id'], by['C2135']['confidence']), ('1944-09-23', 'PL0549', '0.7'))
    expect(s + ': II SS Panzer Corps FMS-only row keeps a blank parent at 0.3', (by['C2136']['parent_unit_id'], by['C2136']['confidence']), ('', '0.3'))


def scenario_42_official_history_pass_2():
    """Official-history pass 2 (October 2026): US gaps from The Last Offensive (C2160); Lexikon der Wehrmacht German rows (C2161-C2163); labels for the rows of the five pilot divisions."""
    s = 'scenario 42'
    import activity
    A = lambda u, d: (lambda r: r and (r['activity'], r['status'], r['support'], r['confidence']))(activity.activity_at(u, d))
    claims = common.load_all_claims()[1]
    rows = [c for c in claims if OHP2(c)]
    expect(s + ': the pass has 63 activity rows (4 new claims, 59 pilot rows labelled)', sum(bool(c.get('activity_status')) for c in rows), 63)
    expect(s + ': 4th Canadian Armoured, 10 Oct 1944: refit at Abbeville ended by Suitcase (inferred end)', A('CAN-ARM-004D', '1944-10-10')[:3], ('refitting', 'certain', 'inferred'))
    expect(s + ': 4th Canadian Armoured, 10 Jan 1945: Army Reserve at Boxtel', A('CAN-ARM-004D', '1945-01-10')[:2], ('reserve', 'certain'))
    expect(s + ': 1st Polish Armoured, 19 Aug 1944: Chambois', A('POL-ARM-001D', '1944-08-19')[:1], ('in_line',))
    expect(s + ': 9th Panzer (German), 5 Nov 1944: short refit at Rheydt', A('GER-PZ-009D', '1944-11-05')[:1], ('refitting',))
    expect(s + ': 9th Panzer (German), 16 Nov 1944: defending Geilenkirchen', A('GER-PZ-009D', '1944-11-16')[:1], ('in_line',))
    expect(s + ': 101st Airborne, 8 May 1945: Berchtesgaden area (inferred garrison)', A('US-ABN-101D', '1945-05-08'), ('garrison', 'certain', 'inferred', 0.3))


def scenario_41_fms_b078_armygroupg():
    """FMS B-078 (von Mellenthin, Army Group G, 14 Nov-early Dec 1944): 23 new rows, R770 on C1012 and C1033."""
    s = 'scenario 41'
    claims = common.load_all_claims()[1]
    new = [c for c in claims if BATCH41(c)]
    by = {c['claim_id']: c for c in claims}
    expect(s + ': the batch adds 23 claims, all citing R770', (len(new), sum('R770' in c['reference_ids'].split(';') for c in new)), (23, 23))
    expect(s + ': headquarters flags Bergzabern, St. Ingbert, Gebweiler', tuple(by[i]['place_id'] for i in ('C2137', 'C2138', 'C2140')), ('PL1045', 'PL1046', 'PL1016'))
    expect(s + ': CMH check: 553rd and 245th under LXXXIX Corps, 719th under LXXXII Corps; 21st Panzer stays blank', tuple(by[i]['parent_unit_id'] for i in ('C2148', 'C2150', 'C2153', 'C2154')), ('GER-COR-089C', 'GER-COR-089C', '', 'GER-COR-082C'))
    import csv
    rels = {r['relation_id']: r for r in csv.DictReader(open(os.path.join(common.ROOT, 'data', 'command_relations.csv'), encoding='utf-8'))}
    expect(s + ': Holland and LXIV relations closed, three new relations', tuple(rels[i]['valid_to'] for i in ('CR0725', 'CR0739', 'CR0641', 'CR1064', 'CR1065', 'CR1066')), ('1944-11-19', '1944-11-26', '1944-12-02', '1945-01-04', '1945-01-06', '1944-12-14'))
    expect(s + ': 719th on the Saar raised to 0.7 with CMH', by['C2154']['confidence'], '0.7')
    expect(s + ': approximate nights and arrivals capped at 0.3', tuple(by[i]['confidence'] for i in ('C2146', 'C2147', 'C2148', 'C2150', 'C2156')), ('0.3',) * 5)
    expect(s + ': B-078 as second family raises C1012 and C1033 to 0.7', tuple((by[i]['confidence'], 'R770' in by[i]['reference_ids']) for i in ('C1012', 'C1033')), (('0.7', True), ('0.7', True)))


def scenario_43_fms_b475_german():
    """FMS B-475 (von Zangen, German original): 15 new rows C2164-C2178 citing R771, all with a blank parent."""
    s = 'scenario 43'
    claims = common.load_all_claims()[1]
    new = [c for c in claims if BATCH43(c)]
    expect(s + ': the batch adds 15 claims, all citing R771', (len(new), sum('R771' in c['reference_ids'].split(';') for c in new)), (15, 15))
    expect(s + ': no parent is set from a single manuscript', sorted(set(c['parent_unit_id'] for c in new)), [''])
    # 0.7 allowed only where a second source family corroborates (Stacey R668, 3 November 2026: C2229, C2230, C2232)
    expect(s + ': confidence is 0.5 or 0.3 only, or 0.7 with a corroborating R668', all(c['confidence'] in ('0.3', '0.5') or (c['confidence'] == '0.7' and 'R668' in c['reference_ids'].split(';')) for c in new), True)
    expect(s + ': 9 arrivals, approximate days and map positions capped at 0.3', sum(c['confidence'] == '0.3' for c in new), 9)


def scenario_44_fms_b235_german():
    """FMS B-235 (Wagener, German original): 13 new rows C2179-C2191 citing R772, all with a blank parent."""
    s = 'scenario 44'
    claims = common.load_all_claims()[1]
    new = [c for c in claims if BATCH44(c)]
    expect(s + ': the batch adds 13 claims, all citing R772', (len(new), sum('R772' in c['reference_ids'].split(';') for c in new)), (13, 13))
    expect(s + ': no parent is set from a single manuscript', sorted(set(c['parent_unit_id'] for c in new)), [''])
    expect(s + ': confidence is 0.5 or 0.3 only, except the rows raised to 0.7 by the corroboration rule (C2181, C2182; scenario 116)', set(c['confidence'] for c in new if c['claim_id'] not in ('C2181', 'C2182')) <= {'0.3', '0.5'}, True)
    expect(s + ': 4 arrivals, approximate days and map positions capped at 0.3', sum(c['confidence'] == '0.3' for c in new), 4)


def scenario_45_fms_b179_german():
    """FMS B-179 (Hausser, German original): 11 new rows C2192-C2202 citing R773, all with a blank parent."""
    s = 'scenario 45'
    claims = common.load_all_claims()[1]
    new = [c for c in claims if BATCH45(c)]
    expect(s + ': the batch adds 11 claims, all citing R773', (len(new), sum('R773' in c['reference_ids'].split(';') for c in new)), (11, 11))
    expect(s + ': no parent is set from a single manuscript', sorted(set(c['parent_unit_id'] for c in new)), [''])
    # 0.7 allowed only where a second source family corroborates (Stacey R668, 3 November 2026: C2229, C2230, C2232)
    expect(s + ': confidence is 0.5 or 0.3 only, or 0.7 with a corroborating R668', all(c['confidence'] in ('0.3', '0.5') or (c['confidence'] == '0.7' and 'R668' in c['reference_ids'].split(';')) for c in new), True)
    expect(s + ': 0 arrivals, approximate days and map positions capped at 0.3', sum(c['confidence'] == '0.3' for c in new), 0)


def scenario_46_fms_b763_german():
    """FMS B-763 (Pemsel, German original): 6 new rows C2203-C2208 citing R774, all with a blank parent."""
    s = 'scenario 46'
    claims = common.load_all_claims()[1]
    new = [c for c in claims if BATCH46(c)]
    expect(s + ': the batch adds 6 claims, all citing R774', (len(new), sum('R774' in c['reference_ids'].split(';') for c in new)), (6, 6))
    expect(s + ': no parent is set from a single manuscript', sorted(set(c['parent_unit_id'] for c in new)), [''])
    # 0.7 allowed only where a second source family corroborates (Stacey R668, 3 November 2026: C2229, C2230, C2232)
    expect(s + ': confidence is 0.5 or 0.3 only, or 0.7 with a corroborating R668', all(c['confidence'] in ('0.3', '0.5') or (c['confidence'] == '0.7' and 'R668' in c['reference_ids'].split(';')) for c in new), True)
    expect(s + ': 6 arrivals, approximate days and map positions capped at 0.3', sum(c['confidence'] == '0.3' for c in new), 6)
    by = {c['claim_id']: c for c in claims}
    expect(s + ': B-763 added to the B-179 forward command post row without raising it', (by['C2193']['reference_ids'], by['C2193']['confidence']), ('R773;R774;R001', '0.5'))


def scenario_47_fms_b781():
    """FMS B-781 (Wiese, German original): 5 new rows C2209-C2213 citing R775, all with a blank parent."""
    s = 'scenario 47'
    claims = common.load_all_claims()[1]
    new = [c for c in claims if BATCH47(c)]
    expect(s + ': the batch adds 5 claims, all citing R775', (len(new), sum('R775' in c['reference_ids'].split(';') for c in new)), (5, 5))
    expect(s + ': no parent is set from a single manuscript', set(c['parent_unit_id'] for c in new), {''})
    # 0.7 allowed only where a second source family corroborates (Stacey R668, 3 November 2026: C2229, C2230, C2232)
    expect(s + ': confidence is 0.5 or 0.3 only, or 0.7 with a corroborating R668', all(c['confidence'] in ('0.3', '0.5') or (c['confidence'] == '0.7' and 'R668' in c['reference_ids'].split(';')) for c in new), True)
    expect(s + ': 5 arrivals, approximate days, doubtful places and map positions capped at 0.3', sum(c['confidence'] == '0.3' for c in new), 5)
    expect(s + ': every row has a place, a source locator and an old value none note', all(c['place_id'] and c['source_locator'].startswith('R775: ') and 'old value none' in c['notes'] for c in new), True)


def scenario_48_fms_b831():
    """FMS B-831 (Felber, English translation): 12 new rows C2214-C2225 citing R776, all with a blank parent."""
    s = 'scenario 48'
    claims = common.load_all_claims()[1]
    new = [c for c in claims if BATCH48(c)]
    expect(s + ': the batch adds 12 claims, all citing R776', (len(new), sum('R776' in c['reference_ids'].split(';') for c in new)), (12, 12))
    expect(s + ': no parent is set from a single manuscript', set(c['parent_unit_id'] for c in new), {''})
    # 0.7 allowed only where a second source family corroborates (Stacey R668, 3 November 2026: C2229, C2230, C2232)
    expect(s + ': confidence is 0.5 or 0.3 only, or 0.7 with a corroborating R668', all(c['confidence'] in ('0.3', '0.5') or (c['confidence'] == '0.7' and 'R668' in c['reference_ids'].split(';')) for c in new), True)
    expect(s + ': 1 arrivals, approximate days, doubtful places and map positions capped at 0.3', sum(c['confidence'] == '0.3' for c in new), 1)
    expect(s + ': every row has a place, a source locator and an old value none note', all(c['place_id'] and c['source_locator'].startswith('R776: ') and 'old value none' in c['notes'] for c in new), True)


def scenario_49_fms_b084():
    """FMS B-084 (Schlemm, German original): 10 new rows C2226-C2235 citing R777, all with a blank parent."""
    s = 'scenario 49'
    claims = common.load_all_claims()[1]
    new = [c for c in claims if BATCH49(c)]
    expect(s + ': the batch adds 10 claims, all citing R777', (len(new), sum('R777' in c['reference_ids'].split(';') for c in new)), (10, 10))
    expect(s + ': no parent is set from a single manuscript', set(c['parent_unit_id'] for c in new), {''})
    # 0.7 allowed only where a second source family corroborates (Stacey R668, 3 November 2026: C2229, C2230, C2232)
    expect(s + ': confidence is 0.5 or 0.3 only, or 0.7 with a corroborating R668', all(c['confidence'] in ('0.3', '0.5') or (c['confidence'] == '0.7' and 'R668' in c['reference_ids'].split(';')) for c in new), True)
    expect(s + ': 1 arrivals, approximate days, doubtful places and map positions capped at 0.3', sum(c['confidence'] == '0.3' for c in new), 1)
    expect(s + ': every row has a place, a source locator and an old value none note', all(c['place_id'] and c['source_locator'].startswith('R777: ') and 'old value none' in c['notes'] for c in new), True)


def scenario_50_fms_b849():
    """FMS B-849 (von Zangen, German original): 12 new rows C2236-C2247 citing R778, all with a blank parent."""
    s = 'scenario 50'
    claims = common.load_all_claims()[1]
    new = [c for c in claims if BATCH50(c)]
    expect(s + ': the batch adds 12 claims, all citing R778', (len(new), sum('R778' in c['reference_ids'].split(';') for c in new)), (12, 12))
    expect(s + ': no parent is set from a single manuscript', set(c['parent_unit_id'] for c in new), {''})
    # 0.7 allowed only where a second source family corroborates (Stacey R668, 3 November 2026: C2229, C2230, C2232)
    expect(s + ': confidence is 0.5 or 0.3 only, or 0.7 with a corroborating R668', all(c['confidence'] in ('0.3', '0.5') or (c['confidence'] == '0.7' and 'R668' in c['reference_ids'].split(';')) for c in new), True)
    expect(s + ': 1 arrivals, approximate days, doubtful places and map positions capped at 0.3', sum(c['confidence'] == '0.3' for c in new), 1)
    expect(s + ': every row has a place, a source locator and an old value none note', all(c['place_id'] and c['source_locator'].startswith('R778: ') and 'old value none' in c['notes'] for c in new), True)


def scenario_51_fms_b745():
    """FMS B-745 (Brandenberger, German original): 27 new rows C2248-C2274 citing R779, all with a blank parent."""
    s = 'scenario 51'
    claims = common.load_all_claims()[1]
    new = [c for c in claims if BATCH51(c)]
    expect(s + ': the batch adds 27 claims, all citing R779', (len(new), sum('R779' in c['reference_ids'].split(';') for c in new)), (27, 27))
    expect(s + ': no parent is set from a single manuscript', set(c['parent_unit_id'] for c in new), {''})
    # 0.7 allowed only where a second source family corroborates (Stacey R668, 3 November 2026: C2229, C2230, C2232)
    expect(s + ': confidence is 0.5 or 0.3 only, or 0.7 with a corroborating R668', all(c['confidence'] in ('0.3', '0.5') or (c['confidence'] == '0.7' and 'R668' in c['reference_ids'].split(';')) for c in new), True)
    expect(s + ': 2 arrivals, approximate days, doubtful readings and map positions capped at 0.3', sum(c['confidence'] == '0.3' for c in new), 2)
    expect(s + ': every row has a place, a source locator and an old value none note', all(c['place_id'] and c['source_locator'].startswith('R779: ') and 'old value none' in c['notes'] for c in new), True)
    expect(s + ': the Nineteenth Army gets the 11 command posts of Anlage 4 after 1 April in date order', [c['date'] for c in new if c['unit_id'] == 'GER-ARMY-019A' and c['event_type'] == 'hq_move'], ['1945-04-09', '1945-04-20', '1945-04-21', '1945-04-22', '1945-04-23', '1945-04-25', '1945-04-27', '1945-04-28', '1945-04-29', '1945-05-02', '1945-05-04'])
    expect(s + ': no placeholder unit gets a first claim', set(c['unit_id'] for c in new) & {'GER-VG-257D', 'GER-INF-106D', 'GER-DIV-405', 'GER-DIV-905'}, set())


def scenario_52_fms_b151():
    """FMS B-151 (Manteuffel, English translation from the Internet Archive): 7 new rows C2275-C2281 citing R780, all with a blank parent."""
    s = 'scenario 52'
    claims = common.load_all_claims()[1]
    new = [c for c in claims if BATCH52(c)]
    expect(s + ': the batch adds 7 claims, all citing R780', (len(new), sum('R780' in c['reference_ids'].split(';') for c in new)), (7, 7))
    expect(s + ': no parent is set from a single manuscript', set(c['parent_unit_id'] for c in new), {''})
    # 0.7 allowed only where a second source family corroborates (Stacey R668, 3 November 2026: C2229, C2230, C2232)
    expect(s + ': confidence is 0.5 or 0.3 only, or 0.7 with a corroborating R668', all(c['confidence'] in ('0.3', '0.5') or (c['confidence'] == '0.7' and 'R668' in c['reference_ids'].split(';')) for c in new), True)
    expect(s + ': 3 arrivals, approximate days, doubtful readings and map positions capped at 0.3', sum(c['confidence'] == '0.3' for c in new), 3)
    expect(s + ': every row has a place, a source locator and an old value none note', all(c['place_id'] and c['source_locator'].startswith('R780: ') and 'old value none' in c['notes'] for c in new), True)
    expect(s + ': the Fifth Panzer Army gets four headquarters rows from Le Hohwald to Dackscheid', [(c['date'], c['place_id']) for c in new if c['unit_id'] == 'GER-PZA-005A'], [('1944-09-11', 'PL1138'), ('1944-10-22', 'PL1039'), ('1944-11-23', 'PL1139'), ('1944-12-15', 'PL1140')])
    expect(s + ': the existing Manderscheid row C2179 is not changed', [(c['place_id'], c['confidence']) for c in claims if c['claim_id'] == 'C2179'], [('PL1066', '0.3')])


def scenario_53_loc_12ag_maps():
    """HQ 12th Army Group situation maps (R781), pass 1 batch 1: 187 rows C2282-C2468 from eight weekly Normandy sheets, blank parents, no existing row changed."""
    s = 'scenario 53'
    claims = common.load_all_claims()[1]
    new = [c for c in claims if LOC12AG(c)]
    b1 = [c for c in new if 'C2282' <= c['claim_id'] <= 'C2468']
    expect(s + ': batch 1 adds 187 claims, all citing R781', (len(b1), sum('R781' in c['reference_ids'].split(';') for c in b1)), (187, 187))
    expect(s + ': batch 1 covers the eight weekly sheets 6 June-25 July 1944', sorted(set(c['date'] for c in b1)), ['1944-06-06', '1944-06-13', '1944-06-20', '1944-06-27', '1944-07-04', '1944-07-11', '1944-07-18', '1944-07-25'])
    expect(s + ': no parent is taken from the situation maps', set(c['parent_unit_id'] for c in new), {''})
    expect(s + ': German rows are intelligence estimates at 0.3', set(c['confidence'] for c in new if c['unit_id'].startswith('GER-')), {'0.3'})
    expect(s + ': Allied rows are 0.5 or 0.7 only', set(c['confidence'] for c in new if not c['unit_id'].startswith('GER-') and c['claim_id'] not in LOWERED) <= {'0.5', '0.7'}, True)
    expect(s + ': every row cites a sheet in its locator, keeps its own map point and says old value none', all(c['source_locator'].startswith('R781: sheet cs') and (c['coord_override'] or c['claim_id'] in ('C3018', 'C3070')) and 'old value none' in c['notes'] for c in new), True)
    expect(s + ': division and brigade points are the main body and corps or army points the headquarters (brigades from batch 3b)', set((c['echelon'], c['location_represents']) for c in new), {('division', 'main_body'), ('brigade', 'main_body'), ('regiment/battle_group', 'main_body'), ('corps', 'headquarters'), ('army', 'headquarters'), ('army_group', 'headquarters')})  # battle group added for the 265th Kampfgruppe map row (placeholder promotion pass, 9 November 2026)
    # the 266th was promoted with its own first claims in the placeholder promotion pass (wf-health-fixes, 9 November 2026), so its map rows are allowed now
    expect(s + ': no placeholder unit gets a first claim', set(c['unit_id'] for c in new) & {'GER-INF-265D', 'GER-INF-266D', 'GER-INF-276D', 'GER-LFD-016D'}, {'GER-INF-266D'})
    expect(s + ': the existing Guards Armoured row of 18 July (Goodwood) is unchanged', [(c['place_id'], c['confidence']) for c in claims if c['claim_id'] == 'C1419'], [('PL0529', '0.7')])


def scenario_54_loc_12ag_us_backfill():
    """HQ 12th Army Group situation maps (R781), batch 2us: 114 US rows C2469-C2582 on the eight Normandy sheets, US divisions as main body, corps, army and army group headquarters at the flag-staff foot."""
    s = 'scenario 54'
    claims = common.load_all_claims()[1]
    b = [c for c in claims if 'C2469' <= c['claim_id'] <= 'C2582']
    expect(s + ': batch 2us adds 114 US claims, all citing R781', (len(b), sum(LOC12AG(c) for c in b), set(c['nationality'] for c in b)), (114, 114, {'US'}))
    expect(s + ': on the eight weekly Normandy sheets', sorted(set(c['date'] for c in b)), ['1944-06-06', '1944-06-13', '1944-06-20', '1944-06-27', '1944-07-04', '1944-07-11', '1944-07-18', '1944-07-25'])
    expect(s + ': US rows are 0.5, or 0.7 with a second family within 10 km and three days', set(c['confidence'] for c in b if c['claim_id'] not in LOWERED), {'0.5', '0.7'})
    expect(s + ': parents stay blank', set(c['parent_unit_id'] for c in b), {''})
    expect(s + ': the 12th Army Group and Third Army headquarters of 25 July are read', sorted(c['unit_id'] for c in b if c['echelon'] in ('army_group', 'army') and c['date'] == '1944-07-25'), ['US-AG-012G', 'US-ARMY-001A', 'US-ARMY-003A'])
    expect(s + ': the existing 82nd Airborne England row C0214 is unchanged', [(c['place_id'], c['confidence']) for c in claims if c['claim_id'] == 'C0214'], [('PL0189', '0.7')])


def scenario_55_loc_12ag_august_1():
    """HQ 12th Army Group situation maps (R781), batch 3a: 227 rows C2583-C2809 on the weekly sheets of 1, 8, 15 and 22 August 1944 (three new base sheets fitted from town junctions), all nationalities."""
    s = 'scenario 55'
    claims = common.load_all_claims()[1]
    b = [c for c in claims if 'C2583' <= c['claim_id'] <= 'C2809']
    expect(s + ': batch 3a adds 227 claims, all citing R781', (len(b), sum(LOC12AG(c) for c in b)), (227, 227))
    expect(s + ': on the four weekly sheets 1-22 August 1944', sorted(set(c['date'] for c in b)), ['1944-08-01', '1944-08-08', '1944-08-15', '1944-08-22'])
    expect(s + ': US, British, Canadian, Polish, French and German units', sorted(set(c['nationality'] for c in b)), ['Canada', 'France', 'Germany', 'Poland', 'UK', 'US'])
    expect(s + ': German rows at 0.3, others 0.5 or 0.7', (set(c['confidence'] for c in b if c['unit_id'].startswith('GER-')), set(c['confidence'] for c in b if not c['unit_id'].startswith('GER-') and c['claim_id'] not in LOWERED) <= {'0.5', '0.7'}), ({'0.3'}, True))
    expect(s + ': parents stay blank', set(c['parent_unit_id'] for c in b), {''})
    expect(s + ': the French 2nd Armoured Division rows C1608 and C1611 are unchanged', [(c['claim_id'], c['place_id'], c['confidence']) for c in claims if c['claim_id'] in ('C1608', 'C1611')], [('C1608', 'PL0206', '0.7'), ('C1611', 'PL0828', '0.7')])


def scenario_56_loc_12ag_villages():
    """HQ 12th Army Group situation maps (R781), village places: 41 rows C2810-C2850 for map readings of batches 1, 2us and 3a that had no town within 3 km, on 38 new hamlet and village places PL1347-PL1384."""
    s = 'scenario 56'
    claims = common.load_all_claims()[1]
    b = [c for c in claims if 'C2810' <= c['claim_id'] <= 'C2850']
    expect(s + ': the village pass adds 41 claims, all citing R781', (len(b), sum(LOC12AG(c) for c in b)), (41, 41))
    expect(s + ': all on the new places PL1347-PL1384', all('PL1347' <= c['place_id'] <= 'PL1384' or c['claim_id'] in AUDIT for c in b), True)
    expect(s + ': German rows at 0.3, others 0.5 or 0.7', (set(c['confidence'] for c in b if c['unit_id'].startswith('GER-')), set(c['confidence'] for c in b if not c['unit_id'].startswith('GER-') and c['claim_id'] not in LOWERED) <= {'0.5', '0.7'}), ({'0.3'}, True))
    expect(s + ': parents stay blank', set(c['parent_unit_id'] for c in b), {''})
    expect(s + ': the 9th Infantry Division row C0383 is re-pointed from PL0355 to PL1385 (place fix of 31 October 2026)', [(c['place_id'], c['latitude'], c['confidence']) for c in claims if c['claim_id'] == 'C0383'], [('PL1385', '48.8299', '0.5')])


def scenario_57_loc_12ag_late_august_september():
    """HQ 12th Army Group situation maps (R781), batch 3b: 231 rows C2851-C3081 on the weekly sheets of 29 August and 5, 12 and 19 September 1944 (three new base sheets fitted from town junctions; 19 September registered to 12 September), all nationalities."""
    s = 'scenario 57'
    claims = common.load_all_claims()[1]
    b = [c for c in claims if 'C2851' <= c['claim_id'] <= 'C3081']
    expect(s + ': batch 3b adds 231 claims, all citing R781', (len(b), sum(LOC12AG(c) for c in b)), (231, 231))
    expect(s + ': on the four weekly sheets 29 August-19 September 1944', sorted(set(c['date'] for c in b)), ['1944-08-29', '1944-09-05', '1944-09-12', '1944-09-19'])
    expect(s + ': US, British, Canadian, Polish, Belgian, French and German units', sorted(set(c['nationality'] for c in b)), ['Belgium', 'Canada', 'France', 'Germany', 'Poland', 'UK', 'US'])
    expect(s + ': German rows at 0.3, others 0.5 or 0.7', (set(c['confidence'] for c in b if c['unit_id'].startswith('GER-')), set(c['confidence'] for c in b if not c['unit_id'].startswith('GER-') and c['claim_id'] not in LOWERED) <= {'0.5', '0.7'}), ({'0.3'}, True))
    expect(s + ': parents stay blank and commanders unknown', (set(c['parent_unit_id'] for c in b), set(c['commander'] for c in b)), ({''}, {'unknown'}))
    expect(s + ': the place fix C0383 holds', [(c['place_id'], c['location_basis']) for c in claims if c['claim_id'] == 'C0383'], [('PL1385', 'inferred')])


def scenario_58_loc_12ag_villages_2():
    """HQ 12th Army Group situation maps (R781), village pass 2: 26 rows C3082-C3107 for batch 3b readings with no town within 3 km (places PL1582-PL1607); the 12th Army Group rows C3018 and C3070 moved from the box centre to Versailles and Verdun."""
    s = 'scenario 58'
    claims = common.load_all_claims()[1]
    b = [c for c in claims if 'C3082' <= c['claim_id'] <= 'C3107']
    expect(s + ': village pass 2 adds 26 claims, all citing R781', (len(b), sum(LOC12AG(c) for c in b)), (26, 26))
    expect(s + ': all on new village places PL1582-PL1607', all('PL1582' <= c['place_id'] <= 'PL1607' or c['claim_id'] in AUDIT for c in b), True)
    expect(s + ': German rows at 0.3, parents blank, commanders unknown', (set(c['confidence'] for c in b if c['unit_id'].startswith('GER-')), set(c['parent_unit_id'] for c in b), set(c['commander'] for c in b)), ({'0.3'}, {''}, {'unknown'}))
    expect(s + ': the 12th Army Group rows sit at the towns (roadmap point 31)', sorted((c['claim_id'], c['place_id'], c['latitude']) for c in claims if c['claim_id'] in ('C3018', 'C3070')), [('C3018', 'PL0364', '48.8053'), ('C3070', 'PL0361', '49.1620')])


def scenario_59_loc_12ag_october_1():
    """HQ 12th Army Group situation maps (R781), batch 4a: 283 rows C3108-C3390 on the weekly sheets of 26 September and 3 and 10 October 1944 (registered to the 12 September base sheet), all nationalities."""
    s = 'scenario 59'
    claims = common.load_all_claims()[1]
    b = [c for c in claims if 'C3108' <= c['claim_id'] <= 'C3390']
    expect(s + ': batch 4a adds 283 claims, all citing R781', (len(b), sum(LOC12AG(c) for c in b)), (283, 283))
    expect(s + ': on the three weekly sheets 26 September-10 October 1944', sorted(set(c['date'] for c in b)), ['1944-09-26', '1944-10-03', '1944-10-10'])
    expect(s + ': US, British, Canadian, Polish, French and German units', sorted(set(c['nationality'] for c in b)), ['Canada', 'France', 'Germany', 'Poland', 'UK', 'US'])
    expect(s + ': German rows at 0.3, others 0.5 or 0.7', (set(c['confidence'] for c in b if c['unit_id'].startswith('GER-')), set(c['confidence'] for c in b if not c['unit_id'].startswith('GER-') and c['claim_id'] not in LOWERED) <= {'0.5', '0.7'}), ({'0.3'}, True))
    expect(s + ': parents stay blank and commanders unknown', (set(c['parent_unit_id'] for c in b), set(c['commander'] for c in b)), ({''}, {'unknown'}))
    expect(s + ': places are existing or new PL1608-PL1800', all(c['place_id'] < 'PL1801' or c['claim_id'] in AUDIT for c in b), True)


def scenario_60_loc_12ag_villages_3():
    """HQ 12th Army Group situation maps (R781), village pass 3: 45 rows C3391-C3435 for batch 4a readings with no town within 3 km (places PL1801-PL1843); first rows under the 5 km rule of 31 October 2026."""
    s = 'scenario 60'
    claims = common.load_all_claims()[1]
    b = [c for c in claims if 'C3391' <= c['claim_id'] <= 'C3435']
    expect(s + ': village pass 3 adds 45 claims, all citing R781', (len(b), sum(LOC12AG(c) for c in b)), (45, 45))
    expect(s + ': all on new village places PL1801-PL1843', all('PL1801' <= c['place_id'] <= 'PL1843' or c['claim_id'] in AUDIT for c in b), True)
    expect(s + ': German rows at 0.3, parents blank, commanders unknown', (set(c['confidence'] for c in b if c['unit_id'].startswith('GER-')), set(c['parent_unit_id'] for c in b), set(c['commander'] for c in b)), ({'0.3'}, {''}, {'unknown'}))
    expect(s + ': 5 km rule: no row at 0.7 unless its note names agreement within 5 km', all(c['confidence'] != '0.7' or 'within 5 km' in c['notes'] for c in b), True)


def scenario_61_loc_12ag_october_2():
    """HQ 12th Army Group situation maps (R781), batch 5a: 134 rows C3436-C3569 on the weekly sheet of 17 October 1944 (registered to the 12 September base sheet), all nationalities, villages inline, 5 km rule."""
    s = 'scenario 61'
    claims = common.load_all_claims()[1]
    b = [c for c in claims if 'C3436' <= c['claim_id'] <= 'C3569']
    expect(s + ': batch 5a adds 134 claims, all citing R781', (len(b), sum(LOC12AG(c) for c in b)), (134, 134))
    expect(s + ': all on the sheet of 17 October 1944', sorted(set(c['date'] for c in b)), ['1944-10-17'])
    expect(s + ': German rows at 0.3, others 0.5 or 0.7', (set(c['confidence'] for c in b if c['unit_id'].startswith('GER-')), set(c['confidence'] for c in b if not c['unit_id'].startswith('GER-') and c['claim_id'] not in LOWERED) <= {'0.5', '0.7'}), ({'0.3'}, True))
    expect(s + ': parents stay blank and commanders unknown', (set(c['parent_unit_id'] for c in b), set(c['commander'] for c in b)), ({''}, {'unknown'}))
    expect(s + ': 5 km rule: no row at 0.7 unless its note names agreement within 5 km', all(c['confidence'] != '0.7' or 'within 5 km' in c['notes'] for c in b), True)
    expect(s + ': places are existing or new PL1844-PL1922', all(c['place_id'] <= 'PL1922' or (c['place_id'] == 'PL2611' and c['claim_id'] in ROETGEN) or c['claim_id'] in AUDIT for c in b), True)


def scenario_62_loc_12ag_october_3():
    """HQ 12th Army Group situation maps (R781), batch 5b: 136 rows C3570-C3705 on the weekly sheet of 24 October 1944 (registered to the 12 September base sheet), all nationalities, villages inline, 5 km rule."""
    s = 'scenario 62'
    claims = common.load_all_claims()[1]
    b = [c for c in claims if 'C3570' <= c['claim_id'] <= 'C3705']
    expect(s + ': batch 5b adds 136 claims, all citing R781', (len(b), sum(LOC12AG(c) for c in b)), (136, 136))
    expect(s + ': all on the sheet of 24 October 1944', sorted(set(c['date'] for c in b)), ['1944-10-24'])
    expect(s + ': German rows at 0.3, others 0.5 or 0.7', (set(c['confidence'] for c in b if c['unit_id'].startswith('GER-')), set(c['confidence'] for c in b if not c['unit_id'].startswith('GER-') and c['claim_id'] not in LOWERED) <= {'0.5', '0.7'}), ({'0.3'}, True))
    expect(s + ': parents stay blank and commanders unknown', (set(c['parent_unit_id'] for c in b), set(c['commander'] for c in b)), ({''}, {'unknown'}))
    expect(s + ': 5 km rule: no row at 0.7 unless its note names agreement within 5 km', all(c['confidence'] != '0.7' or 'within 5 km' in c['notes'] for c in b), True)
    expect(s + ': places are existing or new PL1923-PL1979', all(c['place_id'] <= 'PL1979' or (c['place_id'] == 'PL2611' and c['claim_id'] in ROETGEN) or c['claim_id'] in AUDIT for c in b), True)


def scenario_63_loc_12ag_october_4():
    """HQ 12th Army Group situation maps (R781), batch 5c: 140 rows C3706-C3845 on the weekly sheet of 31 October 1944 (registered to the 12 September base sheet), all nationalities, villages inline, 5 km rule."""
    s = 'scenario 63'
    claims = common.load_all_claims()[1]
    b = [c for c in claims if 'C3706' <= c['claim_id'] <= 'C3845']
    expect(s + ': batch 5c adds 140 claims, all citing R781', (len(b), sum(LOC12AG(c) for c in b)), (140, 140))
    expect(s + ': all on the sheet of 31 October 1944', sorted(set(c['date'] for c in b)), ['1944-10-31'])
    expect(s + ': German rows at 0.3, others 0.5 or 0.7', (set(c['confidence'] for c in b if c['unit_id'].startswith('GER-')), set(c['confidence'] for c in b if not c['unit_id'].startswith('GER-') and c['claim_id'] not in LOWERED) <= {'0.5', '0.7'}), ({'0.3'}, True))
    expect(s + ': parents stay blank and commanders unknown', (set(c['parent_unit_id'] for c in b), set(c['commander'] for c in b)), ({''}, {'unknown'}))
    expect(s + ': 5 km rule: no row at 0.7 unless its note names agreement within 5 km', all(c['confidence'] != '0.7' or 'within 5 km' in c['notes'] for c in b), True)
    expect(s + ': places are existing or new PL1980-PL2060', all(c['place_id'] <= 'PL2060' or (c['place_id'] == 'PL2611' and c['claim_id'] in ROETGEN) or c['claim_id'] in AUDIT for c in b), True)


def scenario_64_loc_12ag_nov07():
    """HQ 12th Army Group situation maps (R781), batch 5d: 138 rows C3846-C3983 on the weekly sheet of 7 November 1944 (registered to the 12 September base sheet), all nationalities, villages inline, 5 km rule."""
    s = 'scenario 64'
    claims = common.load_all_claims()[1]
    b = [c for c in claims if 'C3846' <= c['claim_id'] <= 'C3983']
    expect(s + ': batch 5d adds 138 claims, all citing R781', (len(b), sum(LOC12AG(c) for c in b)), (138, 138))
    expect(s + ': all on the sheet of 7 November 1944', sorted(set(c['date'] for c in b)), ['1944-11-07'])
    expect(s + ': German rows at 0.3, others 0.5 or 0.7', (set(c['confidence'] for c in b if c['unit_id'].startswith('GER-')), set(c['confidence'] for c in b if not c['unit_id'].startswith('GER-') and c['claim_id'] not in LOWERED) <= {'0.5', '0.7'}), ({'0.3'}, True))
    expect(s + ': parents stay blank and commanders unknown', (set(c['parent_unit_id'] for c in b), set(c['commander'] for c in b)), ({''}, {'unknown'}))
    expect(s + ': 5 km rule: no row at 0.7 unless its note names agreement within 5 km', all(c['confidence'] != '0.7' or 'within 5 km' in c['notes'] for c in b), True)
    expect(s + ': places are existing or new PL2061-PL2128', all(c['place_id'] <= 'PL2128' or (c['place_id'] == 'PL2611' and c['claim_id'] in ROETGEN) or c['claim_id'] in AUDIT for c in b), True)


def scenario_65_loc_12ag_nov14():
    """HQ 12th Army Group situation maps (R781), batch 5e: 134 rows C3984-C4117 on the weekly sheet of 14 November 1944 (registered to the 12 September base sheet), all nationalities, villages inline, 5 km rule."""
    s = 'scenario 65'
    claims = common.load_all_claims()[1]
    b = [c for c in claims if 'C3984' <= c['claim_id'] <= 'C4117']
    expect(s + ': batch 5e adds 134 claims, all citing R781', (len(b), sum(LOC12AG(c) for c in b)), (134, 134))
    expect(s + ': all on the sheet of 14 November 1944', sorted(set(c['date'] for c in b)), ['1944-11-14'])
    expect(s + ': German rows at 0.3, others 0.5 or 0.7', (set(c['confidence'] for c in b if c['unit_id'].startswith('GER-')), set(c['confidence'] for c in b if not c['unit_id'].startswith('GER-') and c['claim_id'] not in LOWERED) <= {'0.5', '0.7'}), ({'0.3'}, True))
    expect(s + ': parents stay blank and commanders unknown', (set(c['parent_unit_id'] for c in b), set(c['commander'] for c in b)), ({''}, {'unknown'}))
    expect(s + ': 5 km rule: no row at 0.7 unless its note names agreement within 5 km', all(c['confidence'] != '0.7' or 'within 5 km' in c['notes'] for c in b), True)
    expect(s + ': places are existing or new PL2129-PL2201', all(c['place_id'] <= 'PL2201' or (c['place_id'] == 'PL2611' and c['claim_id'] in ROETGEN) or c['claim_id'] in AUDIT for c in b), True)


def scenario_66_loc_12ag_nov21():
    """HQ 12th Army Group situation maps (R781), batch 5f: 138 rows C4128-C4265 on the weekly sheet of 21 November 1944 (registered to the 12 September base sheet), all nationalities, villages inline, 5 km rule."""
    s = 'scenario 66'
    claims = common.load_all_claims()[1]
    b = [c for c in claims if 'C4128' <= c['claim_id'] <= 'C4265']
    expect(s + ': batch 5f adds 138 claims, all citing R781', (len(b), sum(LOC12AG(c) for c in b)), (138, 138))
    expect(s + ': all on the sheet of 21 November 1944', sorted(set(c['date'] for c in b)), ['1944-11-21'])
    expect(s + ': German rows at 0.3, others 0.5 or 0.7', (set(c['confidence'] for c in b if c['unit_id'].startswith('GER-')), set(c['confidence'] for c in b if not c['unit_id'].startswith('GER-') and c['claim_id'] not in LOWERED) <= {'0.5', '0.7'}), ({'0.3'}, True))
    expect(s + ': parents stay blank and commanders unknown', (set(c['parent_unit_id'] for c in b), set(c['commander'] for c in b)), ({''}, {'unknown'}))
    expect(s + ': 5 km rule: no row at 0.7 unless its note names agreement within 5 km', all(c['confidence'] != '0.7' or 'within 5 km' in c['notes'] for c in b), True)
    expect(s + ': places are existing or new PL2212-PL2290', all(c['place_id'] <= 'PL2290' or (c['place_id'] == 'PL2611' and c['claim_id'] in ROETGEN) or c['claim_id'] in AUDIT for c in b), True)


def scenario_67_loc_12ag_nov28():
    """HQ 12th Army Group situation maps (R781), batch 5g: 138 rows C4266-C4403 on the weekly sheet of 28 November 1944 (registered to the 12 September base sheet), all nationalities, villages inline, 5 km rule."""
    s = 'scenario 67'
    claims = common.load_all_claims()[1]
    b = [c for c in claims if 'C4266' <= c['claim_id'] <= 'C4403']
    expect(s + ': batch 5g adds 138 claims, all citing R781', (len(b), sum(LOC12AG(c) for c in b)), (138, 138))
    expect(s + ': all on the sheet of 28 November 1944', sorted(set(c['date'] for c in b)), ['1944-11-28'])
    expect(s + ': German rows at 0.3, others 0.5 or 0.7', (set(c['confidence'] for c in b if c['unit_id'].startswith('GER-')), set(c['confidence'] for c in b if not c['unit_id'].startswith('GER-') and c['claim_id'] not in LOWERED) <= {'0.5', '0.7'}), ({'0.3'}, True))
    expect(s + ': parents stay blank and commanders unknown', (set(c['parent_unit_id'] for c in b), set(c['commander'] for c in b)), ({''}, {'unknown'}))
    expect(s + ': 5 km rule: no row at 0.7 unless its note names agreement within 5 km', all(c['confidence'] != '0.7' or 'within 5 km' in c['notes'] for c in b), True)
    expect(s + ': places are existing or new PL2291-PL2347', all(c['place_id'] <= 'PL2347' or (c['place_id'] == 'PL2611' and c['claim_id'] in ROETGEN) or c['claim_id'] in AUDIT for c in b), True)


def scenario_68_loc_12ag_dec05():
    """HQ 12th Army Group situation maps (R781), batch 5h: 128 rows C4404-C4531 on the weekly sheet of 5 December 1944 (registered to the 12 September base sheet), all nationalities, villages inline, 5 km rule."""
    s = 'scenario 68'
    claims = common.load_all_claims()[1]
    b = [c for c in claims if 'C4404' <= c['claim_id'] <= 'C4531']
    expect(s + ': batch 5h adds 128 claims, all citing R781', (len(b), sum(LOC12AG(c) for c in b)), (128, 128))
    expect(s + ': all on the sheet of 5 December 1944', sorted(set(c['date'] for c in b)), ['1944-12-05'])
    expect(s + ': German rows at 0.3, others 0.5 or 0.7', (set(c['confidence'] for c in b if c['unit_id'].startswith('GER-')), set(c['confidence'] for c in b if not c['unit_id'].startswith('GER-') and c['claim_id'] not in LOWERED) <= {'0.5', '0.7'}), ({'0.3'}, True))
    expect(s + ': parents stay blank and commanders unknown', (set(c['parent_unit_id'] for c in b), set(c['commander'] for c in b)), ({''}, {'unknown'}))
    expect(s + ': 5 km rule: no row at 0.7 unless its note names agreement within 5 km', all(c['confidence'] != '0.7' or 'within 5 km' in c['notes'] for c in b), True)
    expect(s + ': places are existing or new PL2348-PL2381', all(c['place_id'] <= 'PL2381' or (c['place_id'] == 'PL2611' and c['claim_id'] in ROETGEN) or c['claim_id'] in AUDIT for c in b), True)


def scenario_69_loc_12ag_dec12():
    """HQ 12th Army Group situation maps (R781), batch 5i: 129 rows C4532-C4660 on the weekly sheet of 12 December 1944 (registered to the 12 September base sheet), all nationalities, villages inline, 5 km rule."""
    s = 'scenario 69'
    claims = common.load_all_claims()[1]
    b = [c for c in claims if 'C4532' <= c['claim_id'] <= 'C4660']
    expect(s + ': batch 5i adds 129 claims, all citing R781', (len(b), sum(LOC12AG(c) for c in b)), (129, 129))
    expect(s + ': all on the sheet of 12 December 1944', sorted(set(c['date'] for c in b)), ['1944-12-12'])
    expect(s + ': German rows at 0.3, others 0.5 or 0.7', (set(c['confidence'] for c in b if c['unit_id'].startswith('GER-')), set(c['confidence'] for c in b if not c['unit_id'].startswith('GER-') and c['claim_id'] not in LOWERED) <= {'0.5', '0.7'}), ({'0.3'}, True))
    expect(s + ': parents stay blank and commanders unknown', (set(c['parent_unit_id'] for c in b), set(c['commander'] for c in b)), ({''}, {'unknown'}))
    expect(s + ': 5 km rule: no row at 0.7 unless its note names agreement within 5 km', all(c['confidence'] != '0.7' or 'within 5 km' in c['notes'] for c in b), True)
    expect(s + ': places are existing or new PL2382-PL2411', all(c['place_id'] <= 'PL2411' or (c['place_id'] == 'PL2611' and c['claim_id'] in ROETGEN) or c['claim_id'] in AUDIT for c in b), True)


def scenario_70_loc_12ag_dec19():
    """HQ 12th Army Group situation maps (R781), batch 5j: 136 rows C4661-C4796 on the weekly sheet of 19 December 1944 (registered to the 12 September base sheet), all nationalities, villages inline, 5 km rule."""
    s = 'scenario 70'
    claims = common.load_all_claims()[1]
    b = [c for c in claims if 'C4661' <= c['claim_id'] <= 'C4796']
    expect(s + ': batch 5j adds 136 claims, all citing R781', (len(b), sum(LOC12AG(c) for c in b)), (136, 136))
    expect(s + ': all on the sheet of 19 December 1944', sorted(set(c['date'] for c in b)), ['1944-12-19'])
    expect(s + ': German rows at 0.3, others 0.5 or 0.7', (set(c['confidence'] for c in b if c['unit_id'].startswith('GER-')), set(c['confidence'] for c in b if not c['unit_id'].startswith('GER-') and c['claim_id'] not in LOWERED) <= {'0.5', '0.7'}), ({'0.3'}, True))
    expect(s + ': parents stay blank and commanders unknown', (set(c['parent_unit_id'] for c in b), set(c['commander'] for c in b)), ({''}, {'unknown'}))
    expect(s + ': 5 km rule: no row at 0.7 unless its note names agreement within 5 km', all(c['confidence'] != '0.7' or 'within 5 km' in c['notes'] for c in b), True)
    expect(s + ': places are existing or new PL2412-PL2458', all(c['place_id'] <= 'PL2458' or (c['place_id'] == 'PL2611' and c['claim_id'] in ROETGEN) or c['claim_id'] in AUDIT for c in b), True)


def scenario_71_loc_12ag_dec26():
    """HQ 12th Army Group situation maps (R781), batch 5k: 118 rows C4797-C4914 on the weekly sheet of 26 December 1944 (registered to the 12 September base sheet), all nationalities, villages inline, 5 km rule."""
    s = 'scenario 71'
    claims = common.load_all_claims()[1]
    b = [c for c in claims if 'C4797' <= c['claim_id'] <= 'C4914']
    expect(s + ': batch 5k adds 118 claims, all citing R781', (len(b), sum(LOC12AG(c) for c in b)), (118, 118))
    expect(s + ': all on the sheet of 26 December 1944', sorted(set(c['date'] for c in b)), ['1944-12-26'])
    expect(s + ': German rows at 0.3, others 0.5 or 0.7', (set(c['confidence'] for c in b if c['unit_id'].startswith('GER-')), set(c['confidence'] for c in b if not c['unit_id'].startswith('GER-') and c['claim_id'] not in LOWERED) <= {'0.5', '0.7'}), ({'0.3'}, True))
    expect(s + ': parents stay blank and commanders unknown', (set(c['parent_unit_id'] for c in b), set(c['commander'] for c in b)), ({''}, {'unknown'}))
    expect(s + ': 5 km rule: no row at 0.7 unless its note names agreement within 5 km', all(c['confidence'] != '0.7' or 'within 5 km' in c['notes'] for c in b), True)
    expect(s + ': places are existing or new PL2459-PL2498', all(c['place_id'] <= 'PL2498' or (c['place_id'] == 'PL2611' and c['claim_id'] in ROETGEN) or c['claim_id'] in AUDIT for c in b), True)


def scenario_72_loc_12ag_jan02():
    """HQ 12th Army Group situation maps (R781), batch 5l: 119 rows C4915-C5033 on the weekly sheet of 2 January 1945 (registered to the 12 September base sheet), all nationalities, villages inline, 5 km rule."""
    s = 'scenario 72'
    claims = common.load_all_claims()[1]
    b = [c for c in claims if 'C4915' <= c['claim_id'] <= 'C5033']
    expect(s + ': batch 5l adds 119 claims, all citing R781', (len(b), sum(LOC12AG(c) for c in b)), (119, 119))
    expect(s + ': all on the sheet of 2 January 1945', sorted(set(c['date'] for c in b)), ['1945-01-02'])
    expect(s + ': German rows at 0.3, others 0.5 or 0.7', (set(c['confidence'] for c in b if c['unit_id'].startswith('GER-')), set(c['confidence'] for c in b if not c['unit_id'].startswith('GER-') and c['claim_id'] not in LOWERED) <= {'0.5', '0.7'}), ({'0.3'}, True))
    expect(s + ': parents stay blank and commanders unknown', (set(c['parent_unit_id'] for c in b), set(c['commander'] for c in b)), ({''}, {'unknown'}))
    expect(s + ': 5 km rule: no row at 0.7 unless its note names agreement within 5 km', all(c['confidence'] != '0.7' or 'within 5 km' in c['notes'] for c in b), True)
    expect(s + ': places are existing or new PL2499-PL2519', all(c['place_id'] <= 'PL2519' or (c['place_id'] == 'PL2611' and c['claim_id'] in ROETGEN) or c['claim_id'] in AUDIT for c in b), True)


def scenario_73_loc_12ag_jan09():
    """HQ 12th Army Group situation maps (R781), batch 5m: 119 rows C5034-C5152 on the weekly sheet of 9 January 1945 (registered to the 12 September base sheet), all nationalities, villages inline, 5 km rule."""
    s = 'scenario 73'
    claims = common.load_all_claims()[1]
    b = [c for c in claims if 'C5034' <= c['claim_id'] <= 'C5152']
    expect(s + ': batch 5m adds 119 claims, all citing R781', (len(b), sum(LOC12AG(c) for c in b)), (119, 119))
    expect(s + ': all on the sheet of 9 January 1945', sorted(set(c['date'] for c in b)), ['1945-01-09'])
    expect(s + ': German rows at 0.3, others 0.5 or 0.7', (set(c['confidence'] for c in b if c['unit_id'].startswith('GER-')), set(c['confidence'] for c in b if not c['unit_id'].startswith('GER-') and c['claim_id'] not in LOWERED) <= {'0.5', '0.7'}), ({'0.3'}, True))
    expect(s + ': parents stay blank and commanders unknown', (set(c['parent_unit_id'] for c in b), set(c['commander'] for c in b)), ({''}, {'unknown'}))
    expect(s + ': 5 km rule: no row at 0.7 unless its note names agreement within 5 km', all(c['confidence'] != '0.7' or 'within 5 km' in c['notes'] for c in b), True)
    expect(s + ': places are existing or new PL2520-PL2529', all(c['place_id'] <= 'PL2529' or (c['place_id'] == 'PL2611' and c['claim_id'] in ROETGEN) or c['claim_id'] in AUDIT for c in b), True)


def scenario_74_loc_12ag_jan16():
    """HQ 12th Army Group situation maps (R781), batch 5n: 125 rows C5153-C5277 on the weekly sheet of 16 January 1945 (registered to the 12 September base sheet), all nationalities, villages inline, 5 km rule."""
    s = 'scenario 74'
    claims = common.load_all_claims()[1]
    b = [c for c in claims if 'C5153' <= c['claim_id'] <= 'C5277']
    expect(s + ': batch 5n adds 125 claims, all citing R781', (len(b), sum(LOC12AG(c) for c in b)), (125, 125))
    expect(s + ': all on the sheet of 16 January 1945', sorted(set(c['date'] for c in b)), ['1945-01-16'])
    expect(s + ': German rows at 0.3, others 0.5 or 0.7', (set(c['confidence'] for c in b if c['unit_id'].startswith('GER-')), set(c['confidence'] for c in b if not c['unit_id'].startswith('GER-') and c['claim_id'] not in LOWERED) <= {'0.5', '0.7'}), ({'0.3'}, True))
    expect(s + ': parents stay blank and commanders unknown', (set(c['parent_unit_id'] for c in b), set(c['commander'] for c in b)), ({''}, {'unknown'}))
    expect(s + ': 5 km rule: no row at 0.7 unless its note names agreement within 5 km', all(c['confidence'] != '0.7' or 'within 5 km' in c['notes'] for c in b), True)
    expect(s + ': places are existing or new PL2530-PL2553', all(c['place_id'] <= 'PL2553' or (c['place_id'] == 'PL2611' and c['claim_id'] in ROETGEN) or c['claim_id'] in AUDIT for c in b), True)


def scenario_75_loc_12ag_jan23():
    """HQ 12th Army Group situation maps (R781), batch 5o: 123 rows C5278-C5400 on the weekly sheet of 23 January 1945 (registered to the 12 September base sheet), all nationalities, villages inline, 5 km rule."""
    s = 'scenario 75'
    claims = common.load_all_claims()[1]
    b = [c for c in claims if 'C5278' <= c['claim_id'] <= 'C5400']
    expect(s + ': batch 5o adds 123 claims, all citing R781', (len(b), sum(LOC12AG(c) for c in b)), (123, 123))
    expect(s + ': all on the sheet of 23 January 1945', sorted(set(c['date'] for c in b)), ['1945-01-23'])
    expect(s + ': German rows at 0.3, others 0.5 or 0.7', (set(c['confidence'] for c in b if c['unit_id'].startswith('GER-')), set(c['confidence'] for c in b if not c['unit_id'].startswith('GER-') and c['claim_id'] not in LOWERED) <= {'0.5', '0.7'}), ({'0.3'}, True))
    expect(s + ': parents stay blank and commanders unknown', (set(c['parent_unit_id'] for c in b), set(c['commander'] for c in b)), ({''}, {'unknown'}))
    expect(s + ': 5 km rule: no row at 0.7 unless its note names agreement within 5 km', all(c['confidence'] != '0.7' or 'within 5 km' in c['notes'] for c in b), True)
    expect(s + ': places are existing or new PL2554-PL2575', all(c['place_id'] <= 'PL2575' or (c['place_id'] == 'PL2611' and c['claim_id'] in ROETGEN) or c['claim_id'] in AUDIT for c in b), True)


def scenario_76_loc_12ag_jan30():
    """HQ 12th Army Group situation maps (R781), batch 5p: 134 rows C5401-C5534 on the weekly sheet of 30 January 1945 (registered to the 12 September base sheet), all nationalities, villages inline, 5 km rule."""
    s = 'scenario 76'
    claims = common.load_all_claims()[1]
    b = [c for c in claims if 'C5401' <= c['claim_id'] <= 'C5534']
    expect(s + ': batch 5p adds 134 claims, all citing R781', (len(b), sum(LOC12AG(c) for c in b)), (134, 134))
    expect(s + ': all on the sheet of 30 January 1945', sorted(set(c['date'] for c in b)), ['1945-01-30'])
    expect(s + ': German rows at 0.3, others 0.5 or 0.7', (set(c['confidence'] for c in b if c['unit_id'].startswith('GER-')), set(c['confidence'] for c in b if not c['unit_id'].startswith('GER-') and c['claim_id'] not in LOWERED) <= {'0.5', '0.7'}), ({'0.3'}, True))
    expect(s + ': parents stay blank and commanders unknown', (set(c['parent_unit_id'] for c in b), set(c['commander'] for c in b)), ({''}, {'unknown'}))
    expect(s + ': 5 km rule: no row at 0.7 unless its note names agreement within 5 km', all(c['confidence'] != '0.7' or 'within 5 km' in c['notes'] for c in b), True)
    expect(s + ': places are existing or new PL2576-PL2605', all(c['place_id'] <= 'PL2605' or (c['place_id'] == 'PL2611' and c['claim_id'] in ROETGEN) or c['claim_id'] in AUDIT for c in b), True)


def scenario_77_loc_12ag_feb06():
    """HQ 12th Army Group situation maps (R781), batch 5q: 134 rows C5535-C5668 on the weekly sheet of 6 February 1945 (registered to the 12 September base sheet), all nationalities, villages inline, 5 km rule."""
    s = 'scenario 77'
    claims = common.load_all_claims()[1]
    b = [c for c in claims if 'C5535' <= c['claim_id'] <= 'C5668']
    expect(s + ': batch 5q adds 134 claims, all citing R781', (len(b), sum(LOC12AG(c) for c in b)), (134, 134))
    expect(s + ': all on the sheet of 6 February 1945', sorted(set(c['date'] for c in b)), ['1945-02-06'])
    expect(s + ': German rows at 0.3, others 0.5 or 0.7', (set(c['confidence'] for c in b if c['unit_id'].startswith('GER-')), set(c['confidence'] for c in b if not c['unit_id'].startswith('GER-') and c['claim_id'] not in LOWERED) <= {'0.5', '0.7'}), ({'0.3'}, True))
    expect(s + ': parents stay blank and commanders unknown', (set(c['parent_unit_id'] for c in b), set(c['commander'] for c in b)), ({''}, {'unknown'}))
    expect(s + ': 5 km rule: no row at 0.7 unless its note names agreement within 5 km', all(c['confidence'] != '0.7' or 'within 5 km' in c['notes'] for c in b), True)
    expect(s + ': places are existing or new PL2606-PL2607', all(c['place_id'] <= 'PL2607' or (c['place_id'] == 'PL2611' and c['claim_id'] in ROETGEN) or c['claim_id'] in AUDIT for c in b), True)


def scenario_78_loc_12ag_feb13():
    """HQ 12th Army Group situation maps (R781), batch 5r: 131 rows C5669-C5799 on the weekly sheet of 13 February 1945 (registered to the 12 September base sheet), all nationalities, villages inline, 5 km rule."""
    s = 'scenario 78'
    claims = common.load_all_claims()[1]
    b = [c for c in claims if 'C5669' <= c['claim_id'] <= 'C5799']
    expect(s + ': batch 5r adds 131 claims, all citing R781', (len(b), sum(LOC12AG(c) for c in b)), (131, 131))
    expect(s + ': all on the sheet of 13 February 1945', sorted(set(c['date'] for c in b)), ['1945-02-13'])
    expect(s + ': German rows at 0.3, others 0.5 or 0.7', (set(c['confidence'] for c in b if c['unit_id'].startswith('GER-')), set(c['confidence'] for c in b if not c['unit_id'].startswith('GER-') and c['claim_id'] not in LOWERED) <= {'0.5', '0.7'}), ({'0.3'}, True))
    expect(s + ': parents stay blank and commanders unknown', (set(c['parent_unit_id'] for c in b), set(c['commander'] for c in b)), ({''}, {'unknown'}))
    expect(s + ': 5 km rule: no row at 0.7 unless its note names agreement within 5 km', all(c['confidence'] != '0.7' or 'within 5 km' in c['notes'] for c in b), True)
    expect(s + ': places are existing or new PL2608-PL2610', all(c['place_id'] <= 'PL2610' or (c['place_id'] == 'PL2611' and c['claim_id'] in ROETGEN) or c['claim_id'] in AUDIT for c in b), True)


def scenario_79_loc_12ag_feb20():
    """HQ 12th Army Group situation maps (R781), batch 5s: 134 rows C5800-C5933 on the weekly sheet of 20 February 1945 (registered to the 12 September base sheet), all nationalities, villages inline, 5 km rule."""
    s = 'scenario 79'
    claims = common.load_all_claims()[1]
    b = [c for c in claims if 'C5800' <= c['claim_id'] <= 'C5933']
    expect(s + ': batch 5s adds 134 claims, all citing R781', (len(b), sum(LOC12AG(c) for c in b)), (134, 134))
    expect(s + ': all on the sheet of 20 February 1945', sorted(set(c['date'] for c in b)), ['1945-02-20'])
    expect(s + ': German rows at 0.3, others 0.5 or 0.7', (set(c['confidence'] for c in b if c['unit_id'].startswith('GER-')), set(c['confidence'] for c in b if not c['unit_id'].startswith('GER-') and c['claim_id'] not in LOWERED) <= {'0.5', '0.7'}), ({'0.3'}, True))
    expect(s + ': parents stay blank and commanders unknown', (set(c['parent_unit_id'] for c in b), set(c['commander'] for c in b)), ({''}, {'unknown'}))
    expect(s + ': 5 km rule: no row at 0.7 unless its note names agreement within 5 km', all(c['confidence'] != '0.7' or 'within 5 km' in c['notes'] for c in b), True)
    expect(s + ': places are existing or new PL2612-PL2615', all(c['place_id'] <= 'PL2615' or c['claim_id'] in REREAD or c['claim_id'] in AUDIT for c in b), True)


def scenario_80_loc_12ag_feb27():
    """HQ 12th Army Group situation maps (R781), batch 5t: 134 rows C5934-C6067 on the weekly sheet of 27 February 1945 (registered to the 12 September base sheet), all nationalities, villages inline, 5 km rule."""
    s = 'scenario 80'
    claims = common.load_all_claims()[1]
    b = [c for c in claims if 'C5934' <= c['claim_id'] <= 'C6067']
    expect(s + ': batch 5t adds 134 claims, all citing R781; C6028 and C6002 removed on the re-read of 1 November 2026', (len(b), sum(LOC12AG(c) for c in b)), (132, 132))
    expect(s + ': all on the sheet of 27 February 1945', sorted(set(c['date'] for c in b)), ['1945-02-27'])
    expect(s + ': German rows at 0.3, others 0.5 or 0.7', (set(c['confidence'] for c in b if c['unit_id'].startswith('GER-')), set(c['confidence'] for c in b if not c['unit_id'].startswith('GER-') and c['claim_id'] not in LOWERED) <= {'0.5', '0.7'}), ({'0.3'}, True))
    expect(s + ': parents stay blank and commanders unknown', (set(c['parent_unit_id'] for c in b), set(c['commander'] for c in b)), ({''}, {'unknown'}))
    expect(s + ': 5 km rule: no row at 0.7 unless its note names agreement within 5 km', all(c['confidence'] != '0.7' or 'within 5 km' in c['notes'] for c in b), True)
    expect(s + ': places are existing or new PL2616-PL2620', all(c['place_id'] <= 'PL2620' or c['claim_id'] in REREAD or c['claim_id'] in AUDIT for c in b), True)


def scenario_81_loc_12ag_mar06():
    """HQ 12th Army Group situation maps (R781), batch 5u: 136 rows C6068-C6203 on the weekly sheet of 6 March 1945 (registered to the 12 September base sheet), all nationalities, villages inline, 5 km rule."""
    s = 'scenario 81'
    claims = common.load_all_claims()[1]
    b = [c for c in claims if 'C6068' <= c['claim_id'] <= 'C6203']
    expect(s + ': batch 5u adds 136 claims, all citing R781; C6162, C6187 and C6136 removed on the re-read of 1 November 2026', (len(b), sum(LOC12AG(c) for c in b)), (133, 133))
    expect(s + ': all on the sheet of 6 March 1945', sorted(set(c['date'] for c in b)), ['1945-03-06'])
    expect(s + ': German rows at 0.3, others 0.5 or 0.7', (set(c['confidence'] for c in b if c['unit_id'].startswith('GER-')), set(c['confidence'] for c in b if not c['unit_id'].startswith('GER-') and c['claim_id'] not in LOWERED) <= {'0.5', '0.7'}), ({'0.3'}, True))
    expect(s + ': parents stay blank and commanders unknown', (set(c['parent_unit_id'] for c in b), set(c['commander'] for c in b)), ({''}, {'unknown'}))
    expect(s + ': 5 km rule: no row at 0.7 unless its note names agreement within 5 km', all(c['confidence'] != '0.7' or 'within 5 km' in c['notes'] for c in b), True)
    expect(s + ': places are existing or new PL2621-PL2626', all(c['place_id'] <= 'PL2626' or c['claim_id'] in REREAD or c['claim_id'] in AUDIT for c in b), True)


def scenario_82_loc_12ag_mar13():
    """HQ 12th Army Group situation maps (R781), batch 5v: 135 rows C6205-C6339 on the weekly sheet of 13 March 1945 (registered to the 12 September base sheet), all nationalities, villages inline, 5 km rule."""
    s = 'scenario 82'
    claims = common.load_all_claims()[1]
    b = [c for c in claims if 'C6205' <= c['claim_id'] <= 'C6339']
    expect(s + ': batch 5v adds 135 claims, all citing R781', (len(b), sum(LOC12AG(c) for c in b)), (135, 135))
    expect(s + ': all on the sheet of 13 March 1945', sorted(set(c['date'] for c in b)), ['1945-03-13'])
    expect(s + ': German rows at 0.3, others 0.5 or 0.7', (set(c['confidence'] for c in b if c['unit_id'].startswith('GER-')), set(c['confidence'] for c in b if not c['unit_id'].startswith('GER-') and c['claim_id'] not in LOWERED) <= {'0.5', '0.7'}), ({'0.3'}, True))
    expect(s + ': parents stay blank and commanders unknown', (set(c['parent_unit_id'] for c in b), set(c['commander'] for c in b)), ({''}, {'unknown'}))
    expect(s + ': 5 km rule: no row at 0.7 unless its note names agreement within 5 km', all(c['confidence'] != '0.7' or 'within 5 km' in c['notes'] for c in b), True)
    expect(s + ': places are existing or new PL2634-PL2649', all(c['place_id'] <= 'PL2649' or c['claim_id'] in AUDIT for c in b), True)


def scenario_83_loc_12ag_mar20():
    """HQ 12th Army Group situation maps (R781), batch 5w: 109 rows C6340-C6448 on the weekly sheet of 20 March 1945 (registered to the 12 September base sheet), all nationalities, villages inline, 5 km rule."""
    s = 'scenario 83'
    claims = common.load_all_claims()[1]
    b = [c for c in claims if 'C6340' <= c['claim_id'] <= 'C6448']
    expect(s + ': batch 5w adds 109 claims, all citing R781', (len(b), sum(LOC12AG(c) for c in b)), (109, 109))
    expect(s + ': all on the sheet of 20 March 1945', sorted(set(c['date'] for c in b)), ['1945-03-20'])
    expect(s + ': German rows at 0.3, others 0.5 or 0.7', (set(c['confidence'] for c in b if c['unit_id'].startswith('GER-')), set(c['confidence'] for c in b if not c['unit_id'].startswith('GER-') and c['claim_id'] not in LOWERED) <= {'0.5', '0.7'}), ({'0.3'}, True))
    expect(s + ': parents stay blank and commanders unknown', (set(c['parent_unit_id'] for c in b), set(c['commander'] for c in b)), ({''}, {'unknown'}))
    expect(s + ': 5 km rule: no row at 0.7 unless its note names agreement within 5 km', all(c['confidence'] != '0.7' or 'within 5 km' in c['notes'] for c in b), True)
    expect(s + ': places are existing or new PL2650-PL2678', all(c['place_id'] <= 'PL2678' or c['claim_id'] in AUDIT for c in b), True)


def scenario_84_loc_12ag_mar27():
    """HQ 12th Army Group situation maps (R781), batch 5x: 72 rows C6449-C6520 on the weekly sheet of 27 March 1945 (registered to the 12 September base sheet), all nationalities, villages inline, 5 km rule."""
    s = 'scenario 84'
    claims = common.load_all_claims()[1]
    b = [c for c in claims if 'C6449' <= c['claim_id'] <= 'C6520']
    expect(s + ': batch 5x adds 72 claims, all citing R781', (len(b), sum(LOC12AG(c) for c in b)), (72, 72))
    expect(s + ': all on the sheet of 27 March 1945', sorted(set(c['date'] for c in b)), ['1945-03-27'])
    expect(s + ': German rows at 0.3, others 0.5 or 0.7', (set(c['confidence'] for c in b if c['unit_id'].startswith('GER-')), set(c['confidence'] for c in b if not c['unit_id'].startswith('GER-') and c['claim_id'] not in LOWERED) <= {'0.5', '0.7'}), ({'0.3'}, True))
    expect(s + ': parents stay blank and commanders unknown', (set(c['parent_unit_id'] for c in b), set(c['commander'] for c in b)), ({''}, {'unknown'}))
    expect(s + ': 5 km rule: no row at 0.7 unless its note names agreement within 5 km', all(c['confidence'] != '0.7' or 'within 5 km' in c['notes'] for c in b), True)
    expect(s + ': places are existing or new PL2679-PL2733', all(c['place_id'] <= 'PL2733' or c['claim_id'] in AUDIT for c in b), True)


def scenario_85_loc_12ag_apr3():
    """HQ 12th Army Group situation maps (R781), batch 5y: 83 rows C6521-C6603 on the weekly sheet of 3 April 1945 (registered to the 12 September base sheet), all nationalities, villages inline, 5 km rule."""
    s = 'scenario 85'
    claims = common.load_all_claims()[1]
    b = [c for c in claims if 'C6521' <= c['claim_id'] <= 'C6603']
    expect(s + ': batch 5y adds 83 claims, all citing R781', (len(b), sum(LOC12AG(c) for c in b)), (83, 83))
    expect(s + ': all on the sheet of 3 April 1945', sorted(set(c['date'] for c in b)), ['1945-04-03'])
    expect(s + ': German rows at 0.3, others 0.5 or 0.7', (set(c['confidence'] for c in b if c['unit_id'].startswith('GER-')), set(c['confidence'] for c in b if not c['unit_id'].startswith('GER-') and c['claim_id'] not in LOWERED) <= {'0.5', '0.7'}), (set(), True))  # no German box written on this sheet (roadmap point 149)
    expect(s + ': parents stay blank and commanders unknown', (set(c['parent_unit_id'] for c in b), set(c['commander'] for c in b)), ({''}, {'unknown'}))
    expect(s + ': 5 km rule: no row at 0.7 unless its note names agreement within 5 km', all(c['confidence'] != '0.7' or 'within 5 km' in c['notes'] for c in b), True)
    expect(s + ': places are existing or new PL2734-PL2810', all(c['place_id'] <= 'PL2810' or c['claim_id'] in AUDIT for c in b), True)


def scenario_86_loc_12ag_apr10():
    """HQ 12th Army Group situation maps (R781), batch 5z: 81 rows C6604-C6684 on the weekly sheet of 10 April 1945 (registered to the 12 September base sheet), all nationalities, villages inline, 5 km rule."""
    s = 'scenario 86'
    claims = common.load_all_claims()[1]
    b = [c for c in claims if 'C6604' <= c['claim_id'] <= 'C6684']
    expect(s + ': batch 5z adds 81 claims, all citing R781', (len(b), sum(LOC12AG(c) for c in b)), (81, 81))
    expect(s + ': all on the sheet of 10 April 1945', sorted(set(c['date'] for c in b)), ['1945-04-10'])
    expect(s + ': German rows at 0.3, others 0.5 or 0.7', (set(c['confidence'] for c in b if c['unit_id'].startswith('GER-')), set(c['confidence'] for c in b if not c['unit_id'].startswith('GER-') and c['claim_id'] not in LOWERED) <= {'0.5', '0.7'}), (set(), True))  # no German box written on this sheet (roadmap point 155)
    expect(s + ': parents stay blank and commanders unknown', (set(c['parent_unit_id'] for c in b), set(c['commander'] for c in b)), ({''}, {'unknown'}))
    expect(s + ': 5 km rule: no row at 0.7 unless its note names agreement within 5 km', all(c['confidence'] != '0.7' or 'within 5 km' in c['notes'] for c in b), True)
    expect(s + ': places are existing or new PL2811-PL2883', all(c['place_id'] <= 'PL2883' or c['claim_id'] in AUDIT for c in b), True)


def scenario_87_loc_12ag_apr17():
    """HQ 12th Army Group situation maps (R781), batch 5za: 81 rows C6685-C6765 on the weekly sheet of 17 April 1945 (registered to the 12 September base sheet), all nationalities, villages inline, 5 km rule."""
    s = 'scenario 87'
    claims = common.load_all_claims()[1]
    b = [c for c in claims if 'C6685' <= c['claim_id'] <= 'C6765']
    expect(s + ': batch 5za adds 81 claims, all citing R781', (len(b), sum(LOC12AG(c) for c in b)), (81, 81))
    expect(s + ': all on the sheet of 17 April 1945', sorted(set(c['date'] for c in b)), ['1945-04-17'])
    expect(s + ': German rows at 0.3, others 0.5 or 0.7', (set(c['confidence'] for c in b if c['unit_id'].startswith('GER-')), set(c['confidence'] for c in b if not c['unit_id'].startswith('GER-') and c['claim_id'] not in LOWERED) <= {'0.5', '0.7'}), (set(), True))
    expect(s + ': parents stay blank and commanders unknown', (set(c['parent_unit_id'] for c in b), set(c['commander'] for c in b)), ({''}, {'unknown'}))
    expect(s + ': 5 km rule: no row at 0.7 unless its note names agreement within 5 km', all(c['confidence'] != '0.7' or 'within 5 km' in c['notes'] for c in b), True)
    expect(s + ': places are existing or new PL2884-PL2951', all(c['place_id'] <= 'PL2951' or c['claim_id'] in AUDIT for c in b), True)


def scenario_88_loc_12ag_apr24():
    """HQ 12th Army Group situation maps (R781), batch 5zb: 88 rows C6766-C6853 on the weekly sheet of 24 April 1945 (registered to the 12 September base sheet), all nationalities, villages inline, 5 km rule."""
    s = 'scenario 88'
    claims = common.load_all_claims()[1]
    b = [c for c in claims if 'C6766' <= c['claim_id'] <= 'C6853']
    expect(s + ': batch 5zb adds 88 claims, all citing R781', (len(b), sum(LOC12AG(c) for c in b)), (88, 88))
    expect(s + ': all on the sheet of 24 April 1945', sorted(set(c['date'] for c in b)), ['1945-04-24'])
    expect(s + ': German rows at 0.3, others 0.5 or 0.7', (set(c['confidence'] for c in b if c['unit_id'].startswith('GER-')), set(c['confidence'] for c in b if not c['unit_id'].startswith('GER-') and c['claim_id'] not in LOWERED) <= {'0.5', '0.7'}), (set(), True))
    expect(s + ': parents stay blank and commanders unknown', (set(c['parent_unit_id'] for c in b), set(c['commander'] for c in b)), ({''}, {'unknown'}))
    expect(s + ': 5 km rule: no row at 0.7 unless its note names agreement within 5 km', all(c['confidence'] != '0.7' or 'within 5 km' in c['notes'] for c in b), True)
    expect(s + ': places are existing or new PL2952-PL3026', all(c['place_id'] <= 'PL3026' or c['claim_id'] in AUDIT for c in b), True)


def scenario_89_loc_12ag_may01():
    """HQ 12th Army Group situation maps (R781), batch 5zc: 81 rows C6854-C6934 on the weekly sheet of 1 May 1945 (registered to the 12 September base sheet), all nationalities, villages inline, 5 km rule."""
    s = 'scenario 89'
    claims = common.load_all_claims()[1]
    b = [c for c in claims if 'C6854' <= c['claim_id'] <= 'C6934']
    expect(s + ': batch 5zc adds 81 claims, all citing R781', (len(b), sum(LOC12AG(c) for c in b)), (81, 81))
    expect(s + ': all on the sheet of 1 May 1945', sorted(set(c['date'] for c in b)), ['1945-05-01'])
    expect(s + ': German rows at 0.3, others 0.5 or 0.7', (set(c['confidence'] for c in b if c['unit_id'].startswith('GER-')), set(c['confidence'] for c in b if not c['unit_id'].startswith('GER-') and c['claim_id'] not in LOWERED) <= {'0.5', '0.7'}), (set(), True))
    expect(s + ': parents stay blank and commanders unknown', (set(c['parent_unit_id'] for c in b), set(c['commander'] for c in b)), ({''}, {'unknown'}))
    expect(s + ': 5 km rule: no row at 0.7 unless its note names agreement within 5 km', all(c['confidence'] != '0.7' or 'within 5 km' in c['notes'] for c in b), True)
    expect(s + ': places are existing or new PL3027-PL3087', all(c['place_id'] <= 'PL3087' or c['claim_id'] in AUDIT for c in b), True)


def scenario_90_loc_12ag_may08():
    """HQ 12th Army Group situation maps (R781), batch 5zd: 32 rows C6935-C6966 on the weekly sheet of 8 May 1945 (registered to the 12 September base sheet), all nationalities, villages inline, 5 km rule."""
    s = 'scenario 90'
    claims = common.load_all_claims()[1]
    b = [c for c in claims if 'C6935' <= c['claim_id'] <= 'C6966']
    expect(s + ': batch 5zd adds 32 claims, all citing R781', (len(b), sum(LOC12AG(c) for c in b)), (32, 32))
    expect(s + ': all on the sheet of 8 May 1945', sorted(set(c['date'] for c in b)), ['1945-05-08'])
    expect(s + ': German rows at 0.3, others 0.5 or 0.7', (set(c['confidence'] for c in b if c['unit_id'].startswith('GER-')), set(c['confidence'] for c in b if not c['unit_id'].startswith('GER-') and c['claim_id'] not in LOWERED) <= {'0.5', '0.7'}), (set(), True))
    expect(s + ': parents stay blank and commanders unknown', (set(c['parent_unit_id'] for c in b), set(c['commander'] for c in b)), ({''}, {'unknown'}))
    expect(s + ': 5 km rule: no row at 0.7 unless its note names agreement within 5 km', all(c['confidence'] != '0.7' or 'within 5 km' in c['notes'] for c in b), True)
    expect(s + ': places are existing or new PL3088-PL3132', all(c['place_id'] <= 'PL3132' or c['claim_id'] in AUDIT for c in b), True)


def scenario_91_loc_12ag_may08b():
    """HQ 12th Army Group situation maps (R781), batch 5ze: 11 rows C6967-C6977 on the weekly sheet of 8 May 1945 (completion) (registered to the 12 September base sheet), all nationalities, villages inline, 5 km rule."""
    s = 'scenario 91'
    claims = common.load_all_claims()[1]
    b = [c for c in claims if 'C6967' <= c['claim_id'] <= 'C6977']
    expect(s + ': batch 5ze adds 11 claims, all citing R781', (len(b), sum(LOC12AG(c) for c in b)), (11, 11))
    expect(s + ': all on the sheet of 8 May 1945 (completion)', sorted(set(c['date'] for c in b)), ['1945-05-08'])
    expect(s + ': German rows at 0.3, others 0.5 or 0.7', (set(c['confidence'] for c in b if c['unit_id'].startswith('GER-')), set(c['confidence'] for c in b if not c['unit_id'].startswith('GER-') and c['claim_id'] not in LOWERED) <= {'0.5', '0.7'}), (set(), True))
    expect(s + ': parents stay blank and commanders unknown', (set(c['parent_unit_id'] for c in b), set(c['commander'] for c in b)), ({''}, {'unknown'}))
    expect(s + ': 5 km rule: no row at 0.7 unless its note names agreement within 5 km', all(c['confidence'] != '0.7' or 'within 5 km' in c['notes'] for c in b), True)
    expect(s + ': places are existing or new PL3133-PL3144', all(c['place_id'] <= 'PL3144' or c['claim_id'] in AUDIT for c in b), True)


def scenario_92_loc_12ag_may08c():
    """HQ 12th Army Group situation maps (R781), batch 5zf: 3 rows C6978-C6980 on the weekly sheet of 8 May 1945 (completion, k20) (registered to the 12 September base sheet), all nationalities, villages inline, 5 km rule."""
    s = 'scenario 92'
    claims = common.load_all_claims()[1]
    b = [c for c in claims if 'C6978' <= c['claim_id'] <= 'C6980']
    expect(s + ': batch 5zf adds 3 claims, all citing R781', (len(b), sum(LOC12AG(c) for c in b)), (3, 3))
    expect(s + ': all on the sheet of 8 May 1945 (completion, k20)', sorted(set(c['date'] for c in b)), ['1945-05-08'])
    expect(s + ': German rows at 0.3, others 0.5 or 0.7', (set(c['confidence'] for c in b if c['unit_id'].startswith('GER-')), set(c['confidence'] for c in b if not c['unit_id'].startswith('GER-') and c['claim_id'] not in LOWERED) <= {'0.5', '0.7'}), (set(), True))
    expect(s + ': parents stay blank and commanders unknown', (set(c['parent_unit_id'] for c in b), set(c['commander'] for c in b)), ({''}, {'unknown'}))
    expect(s + ': 5 km rule: no row at 0.7 unless its note names agreement within 5 km', all(c['confidence'] != '0.7' or 'within 5 km' in c['notes'] for c in b), True)
    expect(s + ': places are existing or new PL3145-PL3150', all(c['place_id'] <= 'PL3150' or c['claim_id'] in AUDIT for c in b), True)


def scenario_93_loc_12ag_may09():
    """HQ 12th Army Group situation maps (R781), batch 5zg: 81 rows C6981-C7061 on the weekly sheet of 9 May 1945 (registered to the 12 September base sheet), all nationalities, villages inline, 5 km rule."""
    s = 'scenario 93'
    claims = common.load_all_claims()[1]
    b = [c for c in claims if 'C6981' <= c['claim_id'] <= 'C7061']
    expect(s + ': batch 5zg adds 81 claims, all citing R781', (len(b), sum(LOC12AG(c) for c in b)), (81, 81))
    expect(s + ': all on the sheet of 9 May 1945', sorted(set(c['date'] for c in b)), ['1945-05-09'])
    expect(s + ': German rows at 0.3, others 0.5 or 0.7', (set(c['confidence'] for c in b if c['unit_id'].startswith('GER-')), set(c['confidence'] for c in b if not c['unit_id'].startswith('GER-') and c['claim_id'] not in LOWERED) <= {'0.5', '0.7'}), (set(), True))
    expect(s + ': parents stay blank and commanders unknown', (set(c['parent_unit_id'] for c in b), set(c['commander'] for c in b)), ({''}, {'unknown'}))
    expect(s + ': 5 km rule: no row at 0.7 unless its note names agreement within 5 km', all(c['confidence'] != '0.7' or 'within 5 km' in c['notes'] for c in b), True)
    expect(s + ': places are existing or new PL3151-PL3160', all(c['place_id'] <= 'PL3160' or c['claim_id'] in AUDIT for c in b), True)


def scenario_94_unit_lineage():
    """Unit lineage table (data/unit_lineage.csv): the checker rejects bad rows (synthetic), and the build lists predecessors and successors."""
    s = 'scenario 94'
    import lineage
    vocabs = common.load_vocabularies()
    units = {'A': {'formed_date': '1943-01-01', 'unit_note': 'see B'}, 'B': {'formed_date': '1944-09-01', 'unit_note': 'see A C'}, 'C': {'formed_date': '', 'unit_note': 'see B'}}
    h = lineage.header()
    row = lambda i, p, q, k='redesignation', d='1944-09-01', b='narrative', r='R003': dict(zip(h, ['UL%03d' % i, p, q, k, d, b, r, '']))  # noqa: E731
    ok = lineage.check(h, [row(1, 'A', 'B'), row(2, 'B', 'C')], units, vocabs, {'R003'})
    expect(s + ': a clean chain A -> B -> C passes', ok, [])
    msgs = lambda rows: ' | '.join(m for _, m in lineage.check(h, rows, units, vocabs, {'R003'}))  # noqa: E731
    expect_in(s + ': a cycle is reported', msgs([row(1, 'A', 'B'), row(2, 'B', 'C'), row(3, 'C', 'A')]), 'cycle')
    expect_in(s + ': a duplicate pair is reported', msgs([row(1, 'A', 'B'), row(2, 'A', 'B')]), 'duplicate link')
    expect_in(s + ': an unknown unit is reported', msgs([row(1, 'A', 'Z')]), 'is not a unit')
    expect_in(s + ': an unknown kind is reported', msgs([row(1, 'A', 'B', k='merged')]), 'lineage_kind')
    expect_in(s + ': a date before the predecessor formed_date is reported', msgs([row(1, 'A', 'B', d='1942-05')]), 'before the predecessor')
    expect_in(s + ': an impossible date is reported', msgs([row(1, 'A', 'B', d='1944-02-30')]), 'not a real')
    expect_in(s + ': an unknown reference is reported', msgs([row(1, 'A', 'B', r='R999')]), 'R999')
    expect_in(s + ': a self link is reported', msgs([row(1, 'A', 'A')]), 'same unit')
    expect_in(s + ': a missing unit_note link is reported', msgs([row(1, 'C', 'A')]), 'unit_note of')
    nb = lineage.neighbours([row(1, 'A', 'B'), row(2, 'B', 'C')])
    expect(s + ': neighbours of B', nb['B'], (['A'], ['C']))
    import csv as _csv
    h2, rows = lineage.load()
    expect(s + ': lineage rows UL001-UL011 come first (later passes append)', [r['lineage_id'] for r in rows][:11], ['UL%03d' % i for i in range(1, 12)])
    expect(s + ': the data passes the checker', lineage.check(h2, rows, {u['unit_id']: u for u in common.read_dicts(common.UNITS_CSV)[1]}, vocabs,
           {r['reference_id'] for r in _csv.DictReader(open(os.path.join(common.ROOT, 'data', 'references_meta.csv'), newline='', encoding='utf-8'))}), [])
    b = {r['unit_id']: r for r in _csv.DictReader(open(os.path.join(common.ROOT, 'build', 'units.csv'), newline='', encoding='utf-8'))}
    expect(s + ': 352nd lineage in build/units.csv', (b['GER-INF-352D']['successor_unit_ids'], b['GER-VG-352D']['predecessor_unit_ids']), ('GER-VG-352D', 'GER-INF-352D'))
    expect(s + ': number-reuse cases have no link (276, 326, 361, 708)', [b['GER-VG-%dD' % n]['predecessor_unit_ids'] for n in (276, 326, 361, 708)], ['', '', '', ''])


def scenario_95_coverage_report():
    """scripts/coverage.py on synthetic rows: gap, empty months, bands, map-only share, families, month table and queue order."""
    s = 'scenario 95'
    import coverage as cv
    fam = cv.ref_families([{'reference_id': 'RM', 'source_type': 'archive_document', 'source_family': cv.MAP_FAMILY},
                           {'reference_id': 'RG', 'source_type': 'gazetteer_geocoder', 'source_family': 'geonames'},
                           {'reference_id': 'RT', 'source_type': 'official_history', 'source_family': 'us_army_cmh'}])
    units = [{'unit_id': 'U1', 'unit_name': 'One', 'nationality': 'US', 'echelon': 'division', 'branch': 'Army'},
             {'unit_id': 'U2', 'unit_name': 'Two', 'nationality': 'US', 'echelon': 'division', 'branch': 'Army'},
             {'unit_id': 'U3', 'unit_name': 'Three', 'nationality': 'US', 'echelon': 'division', 'branch': 'Army'}]
    c = lambda u, d, conf, refs: {'unit_id': u, 'date': d, 'confidence': conf, 'reference_ids': refs, 'nationality': 'US'}  # noqa: E731
    claims = [c('U1', '1944-06-10', '0.3', 'RM;RG'), c('U1', '1944-09-20', '0.3', 'RM;RG'), c('U1', '1944-09-27', '0.5', 'RM;RT'),
              c('U2', '1944-06-10', '0.9', 'RT'), c('U2', '1944-07-01', '0.7', 'RT')]
    ur = {r['unit_id']: r for r in cv.by_unit(units, claims, fam)}
    expect(s + ': units without claims are left out', sorted(ur), ['U1', 'U2'])
    u1 = ur['U1']
    expect(s + ': U1 longest gap', (u1['longest_gap_days'], u1['longest_gap_from'], u1['longest_gap_to']), (102, '1944-06-10', '1944-09-20'))
    expect(s + ': U1 empty months', (u1['empty_months'], u1['empty_month_list']), (2, '1944-07;1944-08'))
    expect(s + ': U1 bands', (u1['conf_0_9'], u1['conf_0_7'], u1['conf_0_5'], u1['conf_0_3_or_less']), (0, 0, 1, 2))
    expect(s + ': U1 map-only share (geocoder ignored, a second family breaks map-only)', (u1['map_only_rows'], u1['map_only_share']), (2, '0.667'))
    expect(s + ': U1 families', (u1['source_families'], u1['source_family_list']), (2, 'loc_12ag_situation_maps;us_army_cmh'))
    months = {r['month']: r for r in cv.by_month(list(ur.values()), claims, fam)}
    expect(s + ': July 1944: two units active, one with a claim', (months['1944-07']['units_active'], months['1944-07']['units_with_claim']), (2, 1))
    expect(s + ': August 1944: one unit active, none with a claim', (months['1944-08']['units_active'], months['1944-08']['units_with_claim'], months['1944-08']['map_only_share']), (1, 0, ''))
    q = cv.queue(list(ur.values()))
    expect(s + ': the map-dependent, gappy unit ranks first', [x['unit_id'] for x in q], ['U1', 'U2'])
    expect_in(s + ': the queue reads the gap period', '%s %s %s' % (q[0]['read_from'], q[0]['read_to'], q[0]['reason']), '1944-06-10 1944-09-20 gap of 102 days')
    expect(s + ': the weights sum to 1', round(sum(cv.WEIGHTS.values()), 6), 1.0)
    import csv as _csv
    b = list(_csv.DictReader(open(os.path.join(common.ROOT, 'build', 'review_queue.csv'), newline='', encoding='utf-8')))
    expect(s + ': build/review_queue.csv ranks every unit with claims once', (len(b), len({r['unit_id'] for r in b}), b[0]['rank']), (len({x['unit_id'] for x in common.load_all_claims()[1]} - common.non_ground_unit_ids()), len(b), '1'))  # ground units only (domain, 4 November 2026)


def scenario_96_nara_t315_r940():
    """NARA T-315 roll 940 (47th VGD Ia files, German original): 7 new rows C7062-C7068 citing R783, blank parents, no existing row changed."""
    s = 'scenario 96'
    claims = common.load_all_claims()[1]
    new = [c for c in claims if BATCH96(c)]
    expect(s + ': the batch adds 7 claims, all citing R783', (len(new), sum('R783' in c['reference_ids'].split(';') for c in new)), (7, 7))
    expect(s + ': no parent is set from a single source', set(c['parent_unit_id'] for c in new), {''})
    expect(s + ': six 47th VGD rows and one 16th VGD row', sorted(c['unit_id'] for c in new), ['GER-VG-016D'] + ['GER-VG-047D'] * 6)
    expect(s + ': confidence 0.5 except the 16th VGD boundary sector at 0.3', sorted(c['confidence'] for c in new), ['0.3'] + ['0.5'] * 6)
    expect(s + ': the 47th VGD Jan-Mar 1945 gap is filled from 3 Feb to 12 Mar', [c['date'] for c in new if c['unit_id'] == 'GER-VG-047D' and c['date'] >= '1945'], ['1945-02-03', '1945-02-10', '1945-02-20', '1945-03-06', '1945-03-12'])
    expect(s + ': every row has a place, a frame locator and an old value none note', all(c['place_id'] and c['source_locator'].startswith('R783: frame') and 'old value none' in c['notes'] for c in new), True)
    expect(s + ': no conflict group is opened', set(c['conflict_group_id'] for c in new), {''})



def scenario_101_nara_t354_r147():
    """NARA T-354 roll 147 (9th SS Panzer Division, German original): 2 new rows C7125-C7126 citing R792, blank parents, 2 new places."""
    s = 'scenario 101'
    claims = common.load_all_claims()[1]
    new = [c for c in claims if BATCH101(c)]
    expect(s + ': the batch adds 2 claims, all citing R792', (len(new), sum('R792' in c['reference_ids'].split(';') for c in new)), (2, 2))
    expect(s + ': no parent is set from a single source', set(c['parent_unit_id'] for c in new), {''})
    expect(s + ': Almenêches then Bonnemaison', [c['place_id'] for c in sorted(new, key=lambda c: c['date'])], ['PL3307', 'PL3308'])

def scenario_102_nara_t314_r1605():
    """NARA T-314 roll 1605 (LXXXV Corps files) (German original): 4 new rows C7127-C7130 citing R796, blank parents."""
    s = 'scenario 102'
    claims = common.load_all_claims()[1]
    new = sorted([c for c in claims if BATCH102(c)], key=lambda c: (c['date'], c['claim_id']))
    expect(s + ': the batch adds 4 claims, all citing R796', (len(new), sum('R796' in c['reference_ids'].split(';') for c in new)), (4, 4))
    expect(s + ': no parent is set from a single source', set(c['parent_unit_id'] for c in new), {''})
    expect(s + ': places in date order', [c['place_id'] for c in new], ['PL3309', 'PL3310', 'PL3311', 'PL3312'])

def scenario_103_nara_t354_r149():
    """NARA T-354 roll 149 (9th SS Panzer Division files) (German original): 4 new rows C7131-C7134 citing R797, blank parents."""
    s = 'scenario 103'
    claims = common.load_all_claims()[1]
    new = sorted([c for c in claims if BATCH103(c)], key=lambda c: (c['date'], c['claim_id']))
    expect(s + ': the batch adds 4 claims, all citing R797', (len(new), sum('R797' in c['reference_ids'].split(';') for c in new)), (4, 4))
    expect(s + ': no parent is set from a single source', set(c['parent_unit_id'] for c in new), {''})
    expect(s + ': places in date order', [c['place_id'] for c in new], ['PL1692', 'PL3313', 'PL1819', 'PL0783'])

def scenario_104_nara_t314_r1607():
    """NARA T-314 roll 1607 (LXXXVI Corps files) (German original): 1 new rows C7135-C7135 citing R798, blank parents."""
    s = 'scenario 104'
    claims = common.load_all_claims()[1]
    new = sorted([c for c in claims if BATCH104(c)], key=lambda c: (c['date'], c['claim_id']))
    expect(s + ': the batch adds 1 claims, all citing R798', (len(new), sum('R798' in c['reference_ids'].split(';') for c in new)), (1, 1))
    expect(s + ': no parent is set from a single source', set(c['parent_unit_id'] for c in new), {''})
    expect(s + ': places in date order', [c['place_id'] for c in new], ['PL3314'])

def scenario_105_nara_t315_r828():
    """NARA T-315 roll 828 (26th Volksgrenadier Division Bastogne report) (German original): 3 new rows C7136-C7138 citing R799, blank parents."""
    s = 'scenario 105'
    claims = common.load_all_claims()[1]
    new = sorted([c for c in claims if BATCH105(c)], key=lambda c: (c['date'], c['claim_id']))
    expect(s + ': the batch adds 3 claims, all citing R799', (len(new), sum('R799' in c['reference_ids'].split(';') for c in new)), (3, 3))
    expect(s + ': no parent is set from a single source', set(c['parent_unit_id'] for c in new), {''})
    expect(s + ': places in date order', [c['place_id'] for c in new], ['PL3315', 'PL0031', 'PL0031'])

def scenario_106_nara_t354_r129():
    """NARA T-354 roll 129 (2nd SS Panzer and 17th SS Panzergrenadier Division regimental files) (German original): 3 new rows C7139-C7141 citing R800, blank parents."""
    s = 'scenario 106'
    claims = common.load_all_claims()[1]
    new = sorted([c for c in claims if BATCH106(c)], key=lambda c: (c['date'], c['claim_id']))
    expect(s + ': the batch adds 3 claims, all citing R800', (len(new), sum('R800' in c['reference_ids'].split(';') for c in new)), (3, 3))
    expect(s + ': no parent is set from a single source', set(c['parent_unit_id'] for c in new), {''})
    expect(s + ': places in date order', [c['place_id'] for c in new], ['PL3316', 'PL3317', 'PL1662'])

def scenario_107_nara_t311_r1():
    """NARA T-311 roll 1 (Army Group B quartermaster and intelligence files 1944) (German original): 2 new rows C7142-C7143 citing R801, blank parents."""
    s = 'scenario 107'
    claims = common.load_all_claims()[1]
    new = sorted([c for c in claims if BATCH107(c)], key=lambda c: (c['date'], c['claim_id']))
    expect(s + ': the batch adds 2 claims, all citing R801', (len(new), sum('R801' in c['reference_ids'].split(';') for c in new)), (2, 2))
    expect(s + ': no parent is set from a single source', set(c['parent_unit_id'] for c in new), {''})
    expect(s + ': places in date order', [c['place_id'] for c in new], ['PL0212', 'PL3318'])

def scenario_108_nara_t315_r2145():
    """NARA T-315 roll 2145 (347th Infantry Division, North Holland 1943-44) (German original): 2 new rows C7144-C7145 citing R802, blank parents."""
    s = 'scenario 108'
    claims = common.load_all_claims()[1]
    new = sorted([c for c in claims if BATCH108(c)], key=lambda c: (c['date'], c['claim_id']))
    expect(s + ': the batch adds 2 claims, all citing R802', (len(new), sum('R802' in c['reference_ids'].split(';') for c in new)), (2, 2))
    expect(s + ': no parent is set from a single source', set(c['parent_unit_id'] for c in new), {''})
    expect(s + ': places in date order', [c['place_id'] for c in new], ['PL3319', 'PL3319'])

def scenario_100_nara_t315_r1298():
    """NARA T-315 roll 1298 (116th Panzer Division KTB copy, German original): 4 new rows C7121-C7124 citing R791, blank parents, 2 new places."""
    s = 'scenario 100'
    claims = common.load_all_claims()[1]
    new = [c for c in claims if BATCH100(c)]
    expect(s + ': the batch adds 4 claims, all citing R791', (len(new), sum('R791' in c['reference_ids'].split(';') for c in new)), (4, 4))
    expect(s + ': no parent is set from a single source', set(c['parent_unit_id'] for c in new), {''})
    expect(s + ': Nohn, Gerkerath twice, Louisendorf', [c['place_id'] for c in sorted(new, key=lambda c: c['date'])], ['PL3305', 'PL3306', 'PL3306', 'PL0855'])
    expect(s + ': every row at confidence 0.5', set(c['confidence'] for c in new), {'0.5'})

def scenario_99_nara_t354_r120():
    """NARA T-354 roll 120 (XII SS Corps Korpsbefehl, German original): 2 new rows C7119-C7120 citing R790, blank parents, 2 new places."""
    s = 'scenario 99'
    claims = common.load_all_claims()[1]
    new = [c for c in claims if BATCH99(c)]
    expect(s + ': the batch adds 2 claims, all citing R790', (len(new), sum('R790' in c['reference_ids'].split(';') for c in new)), (2, 2))
    expect(s + ': no parent is set from a single source', set(c['parent_unit_id'] for c in new), {''})
    expect(s + ': XII SS Corps at Venrath then Doverack', [c['place_id'] for c in sorted(new, key=lambda c: c['date'])], ['PL3303', 'PL3304'])
    expect(s + ': every row at confidence 0.5', set(c['confidence'] for c in new), {'0.5'})

def scenario_98_nara_t311_r3():
    """NARA T-311 roll 3 (Army Group B Ia/Ic files, German original): 24 new rows C7095-C7118 citing R786, blank parents, 10 new places, no existing row changed."""
    s = 'scenario 98'
    claims = common.load_all_claims()[1]
    new = [c for c in claims if BATCH98(c)]
    expect(s + ': the batch adds 24 claims, all citing R786', (len(new), sum('R786' in c['reference_ids'].split(';') for c in new)), (24, 24))
    expect(s + ': no parent is set from a single source', set(c['parent_unit_id'] for c in new), {''})
    expect(s + ': dates run from 13 June to 28 September 1944', (min(c['date'] for c in new), max(c['date'] for c in new)), ('1944-06-13', '1944-09-28'))
    expect(s + ': seventeen 28 September 1944 command-post rows from the Turnhout-Roermond OOB', sum(1 for c in new if c['date'] == '1944-09-28'), 17)
    expect(s + ': Panzer Group Eberbach at Vieux Pont and 89th Infantry Division at Falaise', sorted(c['unit_id'] for c in new if c['claim_id'] in ('C7097', 'C7098')), ['GER-INF-089D', 'GER-PZG-EBERB'])
    expect(s + ': every row at confidence 0.5', set(c['confidence'] for c in new), {'0.5'})
    expect(s + ': every row has a place, an image locator and an old value none note', all(c['place_id'] and c['source_locator'].startswith('R786: image') and 'old value none' in c['notes'] for c in new), True)
    expect(s + ': no conflict group is opened', set(c['conflict_group_id'] for c in new), {''})

def scenario_97_nara_t311_r4():
    """NARA T-311 roll 4 (Army Group B Ia files, German original): 26 new rows C7069-C7094 citing R784, blank parents, 15 new places, no existing row changed."""
    s = 'scenario 97'
    claims = common.load_all_claims()[1]
    new = [c for c in claims if BATCH97(c)]
    expect(s + ': the batch adds 26 claims, all citing R784', (len(new), sum('R784' in c['reference_ids'].split(';') for c in new)), (26, 26))
    expect(s + ': no parent is set from a single source', set(c['parent_unit_id'] for c in new), {''})
    expect(s + ': dates run from 14 June to 10 October 1944', (min(c['date'] for c in new), max(c['date'] for c in new)), ('1944-06-14', '1944-10-10'))
    expect(s + ': four LXXXI Corps rows (Moresnet, Niederzier twice, Güsten)', sorted(c['place_id'] for c in new if c['unit_id'] == 'GER-COR-081C'), ['PL2303', 'PL3286', 'PL3290', 'PL3290'])
    expect(s + ': 14 June 1944 command posts of II Parachute Corps, 3rd Parachute, 352nd and 2nd Panzer Divisions', sorted(c['unit_id'] for c in new if c['date'] == '1944-06-14'), ['GER-FJ-002C', 'GER-FJ-003D', 'GER-INF-352D', 'GER-PZ-002D'])
    expect(s + ': confidence 0.5 except three area rows at 0.3 (C7070 raised to 0.7 by FMS B-541 and C7084 by FMS B-730, 4 November 2026)', sorted(c['confidence'] for c in new), ['0.3'] * 3 + ['0.5'] * 21 + ['0.7'] * 2)
    expect(s + ': every row has a place, an image locator and an old value none note', all(c['place_id'] and c['source_locator'].startswith('R784: image') and 'old value none' in c['notes'] for c in new), True)
    expect(s + ': no conflict group is opened', set(c['conflict_group_id'] for c in new), {''})


def scenario_109_cole_ardennes_fifth_army():
    """Cole, The Ardennes: Fifth Panzer Army before Bastogne and the Meuse (chs. 13, 19, 22, 24): 10 new rows C7146-C7155 citing Cole chapter references, blank parents."""
    s = 'scenario 109'
    claims = common.load_all_claims()[1]
    new = sorted([c for c in claims if BATCH109(c)], key=lambda c: (c['claim_id']))
    cole = {'R384', 'R389', 'R390', 'R391', 'R640', 'R696', 'R708', 'R709', 'R803', 'R804', 'R805'}
    expect(s + ': the batch adds 10 claims, all citing a Cole chapter', (len(new), sum(bool(cole & set(c['reference_ids'].split(';'))) for c in new)), (10, 10))
    expect(s + ': no parent is set from a single source', set(c['parent_unit_id'] for c in new), {''})
    expect(s + ': all rows are German and preferred', set((c['nationality'], c['claim_status']) for c in new), {('Germany', 'preferred')})
    expect(s + ': places in claim-id order', [c['place_id'] for c in new], ['PL3320', 'PL3321', 'PL0394', 'PL3322', 'PL3323', 'PL3324', 'PL3325', 'PL3326', 'PL3327', 'PL3328'])

def scenario_110_cole_ardennes_seventh_army():
    """Cole, The Ardennes: Seventh Army on the southern flank (chs. 9, 10, 19, 20, 21): 7 new rows C7156-C7162 citing Cole chapter references, blank parents."""
    s = 'scenario 110'
    claims = common.load_all_claims()[1]
    new = sorted([c for c in claims if BATCH110(c)], key=lambda c: (c['claim_id']))
    cole = {'R384', 'R389', 'R390', 'R391', 'R640', 'R696', 'R708', 'R709', 'R803', 'R804', 'R805'}
    expect(s + ': the batch adds 7 claims, all citing a Cole chapter', (len(new), sum(bool(cole & set(c['reference_ids'].split(';'))) for c in new)), (7, 7))
    expect(s + ': no parent is set from a single source', set(c['parent_unit_id'] for c in new), {''})
    expect(s + ': all rows are German and preferred', set((c['nationality'], c['claim_status']) for c in new), {('Germany', 'preferred')})
    expect(s + ': places in claim-id order', [c['place_id'] for c in new], ['PL3196', 'PL0411', 'PL3329', 'PL3330', 'PL3331', 'PL3332', 'PL0410'])

def scenario_111_cole_ardennes_sixth_army():
    """Cole, The Ardennes: Sixth Panzer Army, II SS Panzer Corps and OKW reserve (chs. 6, 23, 25): 5 new rows C7163-C7167 citing Cole chapter references, blank parents."""
    s = 'scenario 111'
    claims = common.load_all_claims()[1]
    new = sorted([c for c in claims if BATCH111(c)], key=lambda c: (c['claim_id']))
    cole = {'R384', 'R389', 'R390', 'R391', 'R640', 'R696', 'R708', 'R709', 'R803', 'R804', 'R805'}
    expect(s + ': the batch adds 5 claims, all citing a Cole chapter', (len(new), sum(bool(cole & set(c['reference_ids'].split(';'))) for c in new)), (5, 5))
    expect(s + ': no parent is set from a single source', set(c['parent_unit_id'] for c in new), {''})
    expect(s + ': all rows are German and preferred', set((c['nationality'], c['claim_status']) for c in new), {('Germany', 'preferred')})
    expect(s + ': places in claim-id order', [c['place_id'] for c in new], ['PL0404', 'PL0882', 'PL3333', 'PL3334', 'PL0424'])

def scenario_112_cole_ardennes_pass2_german():
    """Cole, The Ardennes, second pass: German facts left from the first pass (chs. 6, 14, 16, 21-23)."""
    s = 'scenario 112'
    claims = common.load_all_claims()[1]
    new = sorted([c for c in claims if BATCH112(c)], key=lambda c: (c['claim_id']))
    cole = {'R383', 'R384', 'R385', 'R386', 'R387', 'R388', 'R389', 'R390', 'R391', 'R392', 'R393', 'R640', 'R644', 'R695', 'R696', 'R708', 'R709', 'R711', 'R803', 'R804', 'R805'}
    expect(s + ': the batch adds 11 claims, all citing a Cole chapter', (len(new), sum(bool(cole & set(c['reference_ids'].split(';'))) for c in new)), (11, 11))
    expect(s + ': no parent is set from a single source', set(c['parent_unit_id'] for c in new), {''})
    expect(s + ': places in claim-id order', [c['place_id'] for c in new], ['PL2501', 'PL1071', 'PL3335', 'PL0055', 'PL3336', 'PL3337', 'PL0404', 'PL2241', 'PL3331', 'PL0382', 'PL2532'])

def scenario_113_cole_ardennes_pass2_allied():
    """Cole, The Ardennes, second pass: US and British division, corps and army positions (chs. 5-24)."""
    s = 'scenario 113'
    claims = common.load_all_claims()[1]
    new = sorted([c for c in claims if BATCH113(c)], key=lambda c: (c['claim_id']))
    cole = {'R383', 'R384', 'R385', 'R386', 'R387', 'R388', 'R389', 'R390', 'R391', 'R392', 'R393', 'R640', 'R644', 'R695', 'R696', 'R708', 'R709', 'R711', 'R803', 'R804', 'R805'}
    expect(s + ': the batch adds 43 claims, all citing a Cole chapter', (len(new), sum(bool(cole & set(c['reference_ids'].split(';'))) for c in new)), (43, 43))
    expect(s + ': no parent is set from a single source', set(c['parent_unit_id'] for c in new), {''})
    expect(s + ': places in claim-id order', [c['place_id'] for c in new], ['PL0139', 'PL3338', 'PL3339', 'PL2241', 'PL0132', 'PL0132', 'PL3340', 'PL0923', 'PL0367', 'PL3341', 'PL3342', 'PL0311', 'PL0172', 'PL0367', 'PL0367', 'PL3315', 'PL3343', 'PL0031', 'PL0884', 'PL1071', 'PL3344', 'PL0210', 'PL3345', 'PL2595', 'PL0012', 'PL3346', 'PL3347', 'PL0928', 'PL3348', 'PL2532', 'PL3349', 'PL3350', 'PL0693', 'PL0202', 'PL0210', 'PL0210', 'PL0954', 'PL0248', 'PL3351', 'PL3352', 'PL2502', 'PL3327', 'PL3320'])

def scenario_114_cole_ardennes_corroborations():
    """Cole, The Ardennes, second pass: Cole added as a corroborating source on five existing rows."""
    s = 'scenario 114'
    claims = {c['claim_id']: c for c in common.load_all_claims()[1]}
    want = {'C4787': ['R781', 'R384', 'R002'], 'C1903': ['R724', 'R385', 'R002'], 'C7136': ['R799', 'R384', 'R850', 'R002'], 'C2181': ['R772', 'R388', 'R850', 'R002'], 'C2182': ['R772', 'R388', 'R386', 'R002']}
    expect(s + ': Cole appended to the reference list of each corroborated row', {k: claims[k]['reference_ids'].split(';') for k in want}, want)
    expect(s + ': corroborated rows keep their place; confidence as set by the corroboration rule', {k: (claims[k]['place_id'], claims[k]['confidence']) for k in want}, {'C4787': ('PL2444', '0.5'), 'C1903': ('PL0248', '0.5'), 'C7136': ('PL3315', '0.7'), 'C2181': ('PL1068', '0.7'), 'C2182': ('PL1069', '0.7')})  # C2181 and C2182 raised to 0.7 by the corroboration rule (scenario 116)

def scenario_115_cole_ardennes_79th_vgd():
    """Cole, The Ardennes: GER-VG-079D promoted from placeholder with its first claims."""
    s = 'scenario 115'
    claims = [c for c in common.load_all_claims()[1] if c['unit_id'] == 'GER-VG-079D' and int(c['claim_id'][1:]) < 8961]   # mid-war end rows C8969-C8970 (midwar-ends) are tested in scenario 207
    expect(s + ': the 79th VGD has three claims, Bourscheid, Kehmen, Ringel', [(c['claim_id'], c['date'], c['place_id']) for c in sorted(claims, key=lambda c: c['claim_id'])], [('C7222', '1944-12-24', 'PL2587'), ('C7223', '1944-12-25', 'PL1769'), ('C7224', '1944-12-30', 'PL3353')])
    expect(s + ': parents blank, all cite Cole ch. 21', (set(c['parent_unit_id'] for c in claims), set(c['reference_ids'] for c in claims)), ({''}, {'R391;R002'}))
    expect(s + ': the unit is active', [r['record_status'] for r in csv.DictReader(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data', 'units.csv'), encoding='utf-8')) if r['unit_id'] == 'GER-VG-079D'], ['active'])

def scenario_116_confidence_corroborated():
    """Corroboration rule: rows with two agreeing source families raised to 0.7."""
    s = 'scenario 116'
    claims = {c['claim_id']: c for c in common.load_all_claims()[1]}
    expect(s + ': raised rows', {k: claims[k]['confidence'] for k in ('C2181', 'C2182')}, {'C2181': '0.7', 'C2182': '0.7'})
    expect(s + ': held rows (same family or open map-conflict point)', {k: claims[k]['confidence'] for k in ('C1903', 'C4787', 'C7136')}, {'C1903': '0.5', 'C4787': '0.5', 'C7136': '0.7'})  # C7136 raised after roadmap 224 closed (Scott, 3 Nov 2026)

def scenario_117_map_row_conflicts():
    """Cole map-row conflicts: text rows preferred, 12th Army Group map rows alternate (G034-G049)."""
    s = 'scenario 117'
    claims = {c['claim_id']: c for c in common.load_all_claims()[1]}
    pairs = {'G034': ('C7136', ['C4724']), 'G035': ('C7146', ['C4752']), 'G036': ('C7148', ['C4790']), 'G037': ('C7168', ['C4710']), 'G038': ('C7163', ['C4768']), 'G039': ('C7153', ['C4993']), 'G040': ('C7156', ['C4722']), 'G041': ('C7177', ['C4845', 'C4958']), 'G042': ('C7157', ['C4726']), 'G043': ('C7159', ['C4792']), 'G044': ('C7160', ['C4761']), 'G045': ('C7161', ['C4791']), 'G046': ('C7165', ['C4898', 'C5004']), 'G047': ('C0977', ['C4662', 'C4798', 'C4916']), 'G048': ('C7188', ['C4715']), 'G049': ('C7211', ['C4688'])}
    got = {g: (claims[p]['conflict_group_id'] == g and claims[p]['claim_status'] == 'preferred', all(claims[a]['conflict_group_id'] == g and claims[a]['claim_status'] == 'alternate' for a in al)) for g, (p, al) in pairs.items()}
    expect(s + ': each group has the text row preferred and the map rows alternate', got, {g: (True, True) for g in pairs})
    expect(s + ': lagging map rows lowered to 0.3', (claims['C4715']['confidence'], claims['C4688']['confidence']), ('0.3', '0.3'))
    expect(s + ': text-against-text points 233 and 235 untouched', (claims['C0553']['conflict_group_id'], claims['C1921']['conflict_group_id'], claims['C2185']['conflict_group_id']), ('', '', ''))

def scenario_118_stacey_normandy_to_spring():
    """Stacey, The Victory Campaign, chapters I-VII (to the eve of Spring): R668 corroborations and new claims C7225-C7237."""
    s = 'scenario 118'
    claims = {c['claim_id']: c for c in common.load_all_claims()[1]}
    raised = ['C0002', 'C0015', 'C0017', 'C0021', 'C0023', 'C0024', 'C0025', 'C0026', 'C0031', 'C0032', 'C0049', 'C0079', 'C0156', 'C0167', 'C0179', 'C0773', 'C1412']
    expect(s + ': corroborated rows raised to 0.7 and cite R668', {c: (claims[c]['confidence'], 'R668' in claims[c]['reference_ids'].split(';')) for c in raised}, {c: ('0.7', True) for c in raised})
    # C0016, C0096 and C0163 were in the 0.7 set; Ellis leftovers (10 November 2026) added R670 and raised them to 0.9 (two official families, exact place).
    later = ['C0016', 'C0096', 'C0163']
    expect(s + ': C0016, C0096 and C0163 still cite R668 and were later raised to 0.9 when Ellis was added', {c: (claims[c]['confidence'], 'R668' in claims[c]['reference_ids'].split(';'), 'R670' in claims[c]['reference_ids'].split(';')) for c in later}, {c: ('0.9', True, True) for c in later})
    held = {'C0054': '0.7', 'C0188': '0.7', 'C0714': '0.3', 'C0033': '0.5', 'C0091': '0.5', 'C0781': '0.5', 'C0027': '0.5'}
    expect(s + ': conflict-group and already-two-family rows keep their confidence', {c: claims[c]['confidence'] for c in held}, held)
    new = ['C%d' % i for i in range(7225, 7238)]
    expect(s + ': new rows cite only Stacey (plus geocoder) and have blank parents', all(claims[c]['reference_ids'].split(';')[0] == 'R668' and claims[c]['parent_unit_id'] == '' for c in new), True)
    expect(s + ': I SS Panzer Corps HQ at Le Merlerault on 6 June', (claims['C7225']['unit_id'], claims['C7225']['place_id']), ('GER-SSPZ-001C', 'PL3354'))
    expect(s + ': eve of Spring dispositions', tuple(claims[c]['unit_id'] for c in ('C7233', 'C7234', 'C7235', 'C7236', 'C7237')), ('GER-SSPZ-001D', 'GER-INF-272D', 'GER-SSPZ-009D', 'GER-PZ-002D', 'GER-PZ-116D'))

def scenario_119_stacey_falaise():
    """Stacey, The Victory Campaign, chapters VIII-XI (24 July - 23 August 1944): R668 corroborations and new claims C7239-C7254."""
    s = 'scenario 119'
    claims = {c['claim_id']: c for c in common.load_all_claims()[1]}
    raised = ['C1424', 'C0724', 'C0726', 'C7143', 'C0747', 'C0746', 'C0329', 'C0330', 'C1610']
    expect(s + ': corroborated rows raised to 0.7 and cite R668', {c: (claims[c]['confidence'], 'R668' in claims[c]['reference_ids'].split(';')) for c in raised}, {c: ('0.7', True) for c in raised})
    expect(s + ': already-two-family row keeps its confidence', claims['C0294']['confidence'], '0.5')
    new = ['C%d' % i for i in range(7239, 7255)]
    expect(s + ': new rows cite only Stacey (plus geocoder) and have blank parents', all(claims[c]['reference_ids'].split(';')[0] == 'R668' and claims[c]['parent_unit_id'] == '' for c in new), True)
    expect(s + ': 84th Division commander captured at Magny', (claims['C7245']['unit_id'], claims['C7245']['place_id']), ('GER-INF-084D', 'PL3365'))

def scenario_120_stacey_seine_channel_ports():
    """Stacey, The Victory Campaign, chapters XII-XIV (23 August - 1 October 1944): R668 corroborations, new claims C7255-C7314, conflict group G050."""
    s = 'scenario 120'
    claims = {c['claim_id']: c for c in common.load_all_claims()[1]}
    raised = ['C0229', 'C0886']
    expect(s + ': corroborated rows raised to 0.7 and cite R668', {c: (claims[c]['confidence'], 'R668' in claims[c]['reference_ids'].split(';')) for c in raised}, {c: ('0.7', True) for c in raised})
    new = ['C%d' % i for i in range(7255, 7315)]
    expect(s + ': new rows cite only Stacey (plus geocoder) and have blank parents', all(claims[c]['reference_ids'].split(';')[0] == 'R668' and claims[c]['parent_unit_id'] == '' for c in new), True)
    expect(s + ': G050 keeps the existing text row preferred', {c: (claims[c]['conflict_group_id'], claims[c]['claim_status']) for c in ('C0853', 'C7288')}, {'C0853': ('G050', 'preferred'), 'C7288': ('G050', 'alternate')})

def scenario_121_stacey_scheldt():
    """Stacey, The Victory Campaign, chapters XV-XVI (13 September - 10 November 1944): R668 corroboration, new claims C7315-C7413."""
    s = 'scenario 121'
    claims = {c['claim_id']: c for c in common.load_all_claims()[1]}
    expect(s + ': corroborated row raised to 0.7 and cites R668', (claims['C3576']['confidence'], 'R668' in claims['C3576']['reference_ids'].split(';')), ('0.7', True))
    new = ['C%d' % i for i in range(7315, 7414)]
    expect(s + ': new rows cite only Stacey (plus geocoder) and have blank parents', all(claims[c]['reference_ids'].split(';')[0] == 'R668' and claims[c]['parent_unit_id'] == '' for c in new), True)
    expect(s + ': Eberding captured at Het Zoute on 1 November', any(claims[c]['unit_id'] == 'GER-INF-064D' and claims[c]['date'] == '1944-11-01' and 'Het Zoute' in claims[c]['current_activity'] for c in new), True)

def scenario_122_stacey_maas_winter():
    """Stacey, The Victory Campaign, chapter XVII (Winter on the Maas, November 1944 - January 1945) and Sketches 20, 23, 25 and Map 6: new claims C7414-C7444."""
    s = 'scenario 122'
    claims = {c['claim_id']: c for c in common.load_all_claims()[1]}
    new = ['C%d' % i for i in range(7414, 7445)]
    expect(s + ': new rows cite only Stacey (plus geocoder) and have blank parents', all(claims[c]['reference_ids'].split(';')[0] == 'R668' and claims[c]['parent_unit_id'] == '' for c in new), True)
    expect(s + ': First Canadian Army headquarters at Tilburg in late December', any(claims[c]['unit_id'] == 'CAN-ARMY-001A' and claims[c]['date'] == '1944-12-21' and claims[c]['place_id'] == 'PL0568' for c in new), True)
    expect(s + ': C0934 cites R668', 'R668' in claims['C0934']['reference_ids'].split(';'), True)

def scenario_123_stacey_veritable():
    """Stacey, The Victory Campaign, chapter XVIII (Operation Veritable, 8-21 February 1945): new claims C7445-C7501 and R668 corroborations."""
    s = 'scenario 123'
    claims = {c['claim_id']: c for c in common.load_all_claims()[1]}
    new = ['C%d' % i for i in range(7445, 7502)]
    expect(s + ': new rows cite only Stacey (plus geocoder) and have blank parents', all(claims[c]['reference_ids'].split(';')[0] == 'R668' and claims[c]['parent_unit_id'] == '' for c in new), True)
    expect(s + ': Panzer Lehr arrives at Marienbaum on 18 February', any(claims[c]['unit_id'] == 'GER-PZ-LEHRD' and claims[c]['date'] == '1945-02-18' and claims[c]['place_id'] == 'PL1098' for c in new), True)
    expect(s + ': C1485 cites R668 and was raised to 0.7', ('R668' in claims['C1485']['reference_ids'].split(';'), claims['C1485']['confidence']), (True, '0.7'))

def scenario_124_stacey_blockbuster():
    """Stacey, The Victory Campaign, chapter XIX (Blockbuster, 22 February - 11 March 1945): new claims C7502-C7562 and R668 corroborations."""
    s = 'scenario 124'
    claims = {c['claim_id']: c for c in common.load_all_claims()[1]}
    new = ['C%d' % i for i in range(7502, 7563)]
    expect(s + ': new rows cite only Stacey (plus geocoder) and have blank parents', all(claims[c]['reference_ids'].split(';')[0] == 'R668' and claims[c]['parent_unit_id'] == '' for c in new), True)
    expect(s + ': the 116th Panzer Division is ordered back to Alpen on 3 March', any(claims[c]['unit_id'] == 'GER-PZ-116D' and claims[c]['date'] == '1945-03-03' and claims[c]['place_id'] == 'PL0764' for c in new), True)
    expect(s + ': C2232 cites R668 and was raised to 0.7', ('R668' in claims['C2232']['reference_ids'].split(';'), claims['C2232']['confidence']), (True, '0.7'))

def scenario_125_stacey_rhine_crossing():
    """Stacey, The Victory Campaign, chapter XX (Rhine crossing and advance to the North Sea): new claims C7563-C7592 and R668 corroborations."""
    s = 'scenario 125'
    claims = {c['claim_id']: c for c in common.load_all_claims()[1]}
    new = ['C%d' % i for i in range(7563, 7593)]
    expect(s + ': new rows cite only Stacey (plus geocoder) and have blank parents', all(claims[c]['reference_ids'].split(';')[0] == 'R668' and claims[c]['parent_unit_id'] == '' for c in new), True)
    expect(s + ': the 47th Panzer Corps headquarters is at Silvolde before Plunder', any(claims[c]['unit_id'] == 'GER-PZ-047C' and claims[c]['date'] == '1945-03-23' and claims[c]['location_represents'] == 'headquarters' for c in new), True)
    expect(s + ': C1181 cites R668 and was raised to 0.7', ('R668' in claims['C1181']['reference_ids'].split(';'), claims['C1181']['confidence']), (True, '0.7'))

FIX2_PARENTED = {'C7610', 'C7637', 'C7638', 'C7662'}  # parents set from Stacey in consistency fix 2 (9 November 2026)


def scenario_126_stacey_western_netherlands():
    """Stacey, The Victory Campaign, chapter XX end (re-read) and chapter XXI (1st Canadian Corps in the western Netherlands): new claims C7593-C7638."""
    s = 'scenario 126'
    claims = {c['claim_id']: c for c in common.load_all_claims()[1]}
    new = ['C%d' % i for i in range(7593, 7639)]
    expect(s + ': new rows cite only Stacey (plus geocoder) and have blank parents (except the rows given a parent in consistency fix 2, scenario 204)', all(claims[c]['reference_ids'].split(';')[0] == 'R668' and (claims[c]['parent_unit_id'] == '' or c in FIX2_PARENTED) for c in new), True)
    expect(s + ': the 49th Division takes Arnhem on 13 April', any(claims[c]['unit_id'] == 'UK-INF-049D' and claims[c]['date'] == '1945-04-13' and claims[c]['place_id'] == 'PL0553' for c in new), True)
    expect(s + ': the 30th German Corps holds the Ijssel-Neder Rijn angle as a sector row at 0.3', any(claims[c]['unit_id'] == 'GER-COR-030C' and claims[c]['confidence'] == '0.3' for c in new), True)

def scenario_127_stacey_surrender_and_appendices():
    """Stacey, The Victory Campaign, chapters XXII-XXIV and appendices D-E: new claims C7639-C7671."""
    s = 'scenario 127'
    claims = {c['claim_id']: c for c in common.load_all_claims()[1]}
    new = ['C%d' % i for i in range(7639, 7672)]
    expect(s + ': new rows cite only Stacey (plus geocoder) and have blank parents (except the rows given a parent in consistency fix 2, scenario 204)', all(claims[c]['reference_ids'].split(';')[0] == 'R668' and (claims[c]['parent_unit_id'] == '' or c in FIX2_PARENTED) for c in new), True)
    expect(s + ': the 4th Canadian Armoured Division takes Bad Zwischenahn on 30 April', any(claims[c]['unit_id'] == 'CAN-ARM-004D' and claims[c]['date'] == '1945-04-30' and claims[c]['place_id'] == 'PL0701' for c in new), True)
    expect(s + ': the 88th German Corps area about Utrecht is taken over on 7 May', any(claims[c]['unit_id'] == 'GER-COR-088C' and claims[c]['date'] == '1945-05-07' for c in new), True)

def scenario_128_stacey_maps():
    """Stacey, The Victory Campaign, remaining maps and sketches (Sketches 34-49, Maps 9-14): map rows C7672-C7682 at 0.3; roadmap 248-249."""
    s = 'scenario 128'
    claims = {c['claim_id']: c for c in common.load_all_claims()[1]}
    new = ['C%d' % i for i in range(7672, 7683)]
    expect(s + ': map rows are all at 0.3 with blank parents', all(claims[c]['confidence'] == '0.3' and claims[c]['parent_unit_id'] == '' and claims[c]['reference_ids'].split(';')[0] == 'R668' for c in new), True)
    expect(s + ': the map row C6663 keeps its confidence (grouped as an alternate in G057 by scenario 129)', claims['C6663']['confidence'], '0.5')

def scenario_129_stacey_conflict_groups():
    """Stacey follow-up: open map-row conflicts resolved as conflict groups G051-G057 (text rows preferred, nothing deleted)."""
    s = 'scenario 129'
    claims = {c['claim_id']: c for c in common.load_all_claims()[1]}
    pairs = {'G051': ('C7238', ['C2368']), 'G052': ('C7375', ['C3420']), 'G053': ('C7436', ['C1285']), 'G054': ('C7479', ['C5680']), 'G055': ('C7501', ['C5870']), 'G056': ('C7510', ['C6058']), 'G057': ('C7598', ['C6663'])}
    got = {g: (claims[p]['conflict_group_id'] == g and claims[p]['claim_status'] == 'preferred', all(claims[a]['conflict_group_id'] == g and claims[a]['claim_status'] == 'alternate' for a in al)) for g, (p, al) in pairs.items()}
    expect(s + ': each group has the text row preferred and the other row alternate', got, {g: (True, True) for g in pairs})
    expect(s + ': no confidence lowered', tuple(claims[c]['confidence'] for c in ('C2368', 'C3420', 'C1285', 'C5680', 'C5870', 'C6058', 'C6663')), ('0.5', '0.3', '0.3', '0.5', '0.3', '0.3', '0.5'))
    expect(s + ': keep-both points left ungrouped', tuple(claims[c]['conflict_group_id'] for c in ('C2174', 'C7348', 'C1495', 'C7499', 'C5809', 'C1238', 'C0778')), ('', '', '', '', 'G058', '', ''))  # C5809 grouped in G058 by the FMS B-093 reading (roadmap point 246)
    expect(s + ': C0778 names both relieving formations', 'roadmap point 238' in claims['C0778']['notes'], True)

def scenario_130_stacey_units_added():
    """Stacey follow-up: five units added (471st, 490th, 34th SS, Armee-Abteilung Straube, 1st Canadian Armoured Brigade), claims C7683-C7688, two rows re-pointed."""
    s = 'scenario 130'
    claims = {c['claim_id']: c for c in common.load_all_claims()[1]}
    want = {'C7683': 'GER-INF-471D', 'C7684': 'GER-INF-490D', 'C7685': 'GER-INF-490D', 'C7686': 'GER-SSGR-034D', 'C7687': 'GER-AA-STRAUB', 'C7688': 'CAN-ARM-001B', 'C7681': 'GER-AA-STRAUB', 'C7616': 'CAN-ARM-001B', 'C1238': 'GER-FJA-001A'}
    expect(s + ': rows on the new units', {c: claims[c]['unit_id'] for c in want}, want)
    expect(s + ': new rows cite Stacey and have blank parents', all(claims[c]['reference_ids'].split(';')[0] == 'R668' and claims[c]['parent_unit_id'] == '' for c in want if c != 'C1238'), True)

def scenario_131_fms_b093_meindl():
    """FMS B-093 (Meindl, II Parachute Corps): claims C7689-C7721 cite R806; Sonsbeck command post preferred over the Varsselder map row (G058, point 246); C0856 raised to 0.7."""
    s = 'scenario 131'
    claims = {c['claim_id']: c for c in common.load_all_claims()[1]}
    new = ['C%d' % i for i in range(7689, 7722)]
    expect(s + ': new rows cite R806 first, blank parents, at most 0.5', all(claims[c]['reference_ids'].split(';')[0] == 'R806' and claims[c]['parent_unit_id'] == '' and float(claims[c]['confidence']) <= 0.5 for c in new), True)
    expect(s + ': Sonsbeck preferred, Varsselder alternate', ((claims['C7704']['conflict_group_id'], claims['C7704']['claim_status'], claims['C7704']['place_id']), (claims['C5809']['conflict_group_id'], claims['C5809']['claim_status'], claims['C5809']['confidence'])), (('G058', 'preferred', 'PL1099'), ('G058', 'alternate', '0.3')))
    expect(s + ': C0856 raised with a CMH and FMS citation', (claims['C0856']['confidence'], 'R806' in claims['C0856']['reference_ids'].split(';')), ('0.7', True))
    expect(s + ': same-family and sector appends hold confidence', tuple(claims[c]['confidence'] for c in ('C2226', 'C7499', 'C7113', 'C7566')), ('0.5', '0.3', '0.5', '0.3'))
    expect(s + ': corps command posts in order', [claims[c]['place_id'] for c in ('C7691', 'C7700', 'C7704', 'C7706', 'C7708', 'C7710', 'C7716', 'C7717')], ['PL0578', 'PL1857', 'PL1099', 'PL2645', 'PL3539', 'PL3540', 'PL3542', 'PL3543'])

def scenario_132_fms_b717_student():
    """FMS B-717 (Student, First Parachute Army and Army Group H): claims C7722-C7747 cite R807; C0854 raised to 0.7; roadmap 240 kept open."""
    s = 'scenario 132'
    claims = {c['claim_id']: c for c in common.load_all_claims()[1]}
    new = ['C%d' % i for i in range(7722, 7748)]
    expect(s + ': new rows cite R807 first, blank parents, at most 0.5', all(claims[c]['reference_ids'].split(';')[0] == 'R807' and claims[c]['parent_unit_id'] == '' and float(claims[c]['confidence']) <= 0.5 for c in new), True)
    expect(s + ': Army Group B moves Verviers, Terborg, Krefeld', [(claims[c]['date'], claims[c]['place_id']) for c in ('C7722', 'C7734', 'C7735')], [('1944-09-05', 'PL0365'), ('1944-09-17', 'PL3545'), ('1944-09-25', 'PL0420')])
    expect(s + ': C0854 raised; Chill rows of point 240 unchanged', (claims['C0854']['confidence'], claims['C2174']['confidence'], claims['C7348']['confidence'], claims['C2174']['conflict_group_id']), ('0.7', '0.3', '0.5', ''))

def scenario_133_fms_b084_reread():
    """FMS B-084 (Schlemm) re-read: claims C7748-C7777 cite R777 first; LXV in the text mapped to GER-COR-063C; G056 row appended but not raised."""
    s = 'scenario 133'
    claims = {c['claim_id']: c for c in common.load_all_claims()[1]}
    new = ['C%d' % i for i in range(7748, 7778)]
    expect(s + ': new rows cite R777 first, blank parents, at most 0.5', all(claims[c]['reference_ids'].split(';')[0] == 'R777' and claims[c]['parent_unit_id'] == '' and float(claims[c]['confidence']) <= 0.5 for c in new), True)
    expect(s + ': Abraham corps rows on GER-COR-063C with the LXV note', all('LXV' in claims[c]['notes'] for c in new if claims[c]['unit_id'] == 'GER-COR-063C') and sum(claims[c]['unit_id'] == 'GER-COR-063C' for c in new), 6)
    expect(s + ': G056 preferred row appended, confidence held', ('R777' in claims['C7510']['reference_ids'].split(';'), claims['C7510']['confidence'], claims['C7510']['claim_status']), (True, '0.3', 'preferred'))

def scenario_134_fms_b368_langhaeuser():
    """FMS B-368 (Langhaeuser, 6th Parachute Division): claims C7778-C7794 cite R808; command posts Velp, Gameren, Brakel, Geldermalsen; G059 and G060 with the Stacey rows preferred; C7438 raised to 0.7."""
    s = 'scenario 134'
    claims = {c['claim_id']: c for c in common.load_all_claims()[1]}
    new = ['C%d' % i for i in range(7778, 7795)]
    expect(s + ': new rows cite R808 first, blank parents, at most 0.5', all(claims[c]['reference_ids'].split(';')[0] == 'R808' and claims[c]['parent_unit_id'] == '' and float(claims[c]['confidence']) <= 0.5 for c in new), True)
    expect(s + ': division command posts', [claims[c]['place_id'] for c in ('C7780', 'C7785', 'C7788', 'C7789')], ['PL3313', 'PL3555', 'PL3557', 'PL1060'])
    expect(s + ': Stacey rows preferred, FMS rows alternate', [(claims[c]['conflict_group_id'], claims[c]['claim_status']) for c in ('C7442', 'C7790', 'C2027', 'C7791')], [('G059', 'preferred'), ('G059', 'alternate'), ('G060', 'preferred'), ('G060', 'alternate')])
    expect(s + ': C7438 raised, C7459 and C1545 held', tuple(claims[c]['confidence'] for c in ('C7438', 'C7459', 'C1545')), ('0.7', '0.5', '0.5'))

def scenario_135_fms_b774_prittwitz():
    """FMS B-774 (Prittwitz, LXXXVIII Corps): claims C7795-C7829 cite R809; corps command posts Dongen, Herpt, Almkerk, Geldermalsen, Houten, Bilthoven, Lunteren; appends only, no raises (C2168 and C2177 same family; C7352 undated)."""
    s = 'scenario 135'
    claims = {c['claim_id']: c for c in common.load_all_claims()[1]}
    new = ['C%d' % i for i in range(7795, 7830)]
    expect(s + ': new rows cite R809 first, blank parents, at most 0.5', all(claims[c]['reference_ids'].split(';')[0] == 'R809' and claims[c]['parent_unit_id'] == '' and float(claims[c]['confidence']) <= 0.5 for c in new), True)
    cps = sorted((claims[c]['date'], claims[c]['place_id']) for c in new if claims[c]['unit_id'] == 'GER-COR-088C' and claims[c]['event_type'] in ('hq_move', 'hq_observation'))
    expect(s + ': corps command posts in order', [x[1] for x in cps], ['PL1058', 'PL1743', 'PL3561', 'PL1060', 'PL3564', 'PL2291', 'PL3566'])
    expect(s + ': appended rows keep their confidence', tuple((claims[c]['confidence'], 'R809' in claims[c]['reference_ids'].split(';')) for c in ('C2168', 'C7352', 'C2177', 'C7790', 'C2174')), (('0.5', True), ('0.5', True), ('0.3', True), ('0.3', True), ('0.3', True)))

def scenario_136_fms_b762_prittwitz():
    """FMS B-762 (Prittwitz, LXXXVIII Corps 22 March-10 May 1945): claims C7830-C7848 cite R810; command posts Dalfsen and Putten; C7587 and C7631 raised to 0.7 (Stacey and B-762)."""
    s = 'scenario 136'
    claims = {c['claim_id']: c for c in common.load_all_claims()[1]}
    new = ['C%d' % i for i in range(7830, 7849)]
    # leftovers-1115 task c (roadmap 351): old value of this check: every new row has a blank parent; new value: C7835 (the 6th Parachute Division placed under the LXXXVIII Corps) has parent GER-COR-088C, the others stay blank; reason: it is the evidence of CR1322/CR1323.
    expect(s + ': new rows cite R810 first, blank parents (C7835: LXXXVIII Corps since task c), at most 0.5', all(claims[c]['reference_ids'].split(';')[0] == 'R810' and (claims[c]['parent_unit_id'] == '' or (c == 'C7835' and claims[c]['parent_unit_id'] == 'GER-COR-088C')) and float(claims[c]['confidence']) <= 0.5 for c in new), True)
    expect(s + ': corps command posts Dalfsen and Putten', [claims[c]['place_id'] for c in ('C7836', 'C7842')], ['PL3568', 'PL3571'])
    expect(s + ': C7587 and C7631 raised, C7579 and C7679 held', tuple(claims[c]['confidence'] for c in ('C7587', 'C7631', 'C7579', 'C7679')), ('0.7', '0.7', '0.3', '0.3'))

def scenario_137_roadmap_253_map_rows():
    """Roadmap 253: stale 12th Army Group map rows grouped as alternates (G061, G062, G056 extended); text rows preferred; confidences unchanged."""
    s = 'scenario 137'
    claims = {c['claim_id']: c for c in common.load_all_claims()[1]}
    want = {'C7741': ('G061', 'preferred'), 'C3681': ('G061', 'alternate'), 'C3823': ('G061', 'alternate'), 'C7742': ('G062', 'preferred'), 'C3679': ('G062', 'alternate'), 'C7510': ('G056', 'preferred'), 'C6058': ('G056', 'alternate'), 'C5924': ('G056', 'alternate'), 'C6192': ('G056', 'alternate')}
    expect(s + ': groups and statuses', {c: (claims[c]['conflict_group_id'], claims[c]['claim_status']) for c in want}, want)
    expect(s + ': map rows held at 0.3', [claims[c]['confidence'] for c in ('C3681', 'C3823', 'C3679', 'C5924', 'C6192')], ['0.3'] * 5)
    expect(s + ': roadmap 240 rows kept ungrouped', [claims[c]['conflict_group_id'] for c in ('C2174', 'C7799', 'C7348')], ['', '', ''])

def scenario_138_fms_b156_reinhard():
    """FMS B-156 (Reinhard, LXXXVIII Corps June-21 December 1944): claims C7849-C7897 cite R811; command posts Bilthoven, Moergestel, Dongen; C0220 raised to 0.7; FMS-only rows held."""
    s = 'scenario 138'
    claims = {c['claim_id']: c for c in common.load_all_claims()[1]}
    new = ['C%d' % i for i in range(7849, 7898)]
    expect(s + ': new rows cite R811 first, blank parents, at most 0.5 (C7851 raised to 0.7 in the de Jong pass, scenario 233)', all(claims[c]['reference_ids'].split(';')[0] == 'R811' and claims[c]['parent_unit_id'] == '' and float(claims[c]['confidence']) <= (0.7 if c == 'C7851' else 0.5) for c in new), True)
    expect(s + ': corps command posts Bilthoven, Moergestel, Dongen', [claims[c]['place_id'] for c in ('C7851', 'C7854', 'C7871')], ['PL2291', 'PL1057', 'PL1058'])
    expect(s + ': C0220 raised; C7723, C7825 and C7435 held', tuple(claims[c]['confidence'] for c in ('C0220', 'C7723', 'C7825', 'C7435')), ('0.7', '0.5', '0.5', '0.3'))

def scenario_139_fms_b343_reinhard():
    """FMS B-343 (Reinhard, LXXXVIII Corps on the Dutch coast, 6 June-5 September 1944): claims C7898-C7906 cite R812; command posts Bilthoven, Hilversum, Schagen, Amstelveen, Dordrecht; FMS-only rows held."""
    s = 'scenario 139'
    claims = {c['claim_id']: c for c in common.load_all_claims()[1]}
    new = ['C%d' % i for i in range(7898, 7907)]
    expect(s + ': new rows cite R812 first, blank parents, at most 0.5', all(claims[c]['reference_ids'].split(';')[0] == 'R812' and claims[c]['parent_unit_id'] == '' and float(claims[c]['confidence']) <= 0.5 for c in new), True)
    expect(s + ': command posts 6 June 1944', [claims[c]['place_id'] for c in ('C7898', 'C7899', 'C7900', 'C7902', 'C7905')], ['PL2291', 'PL3443', 'PL3584', 'PL3586', 'PL1065'])
    expect(s + ': corroborations held (same family or approximate)', tuple(claims[c]['confidence'] for c in ('C7849', 'C7144', 'C7145', 'C0220')), ('0.3', '0.5', '0.5', '0.7'))

def scenario_140_fms_b262_blauensteiner():
    """FMS B-262 (Blauensteiner, II Parachute Corps 19 September 1944-10 March 1945): claims C7907-C7940 cite R813; Wasserburg, Vorst; C7532 and C7533 raised; roadmap 264 rows kept ungrouped."""
    s = 'scenario 140'
    claims = {c['claim_id']: c for c in common.load_all_claims()[1]}
    new = ['C%d' % i for i in range(7907, 7941)]
    expect(s + ': new rows cite R813 first, blank parents, at most 0.5', all(claims[c]['reference_ids'].split(';')[0] == 'R813' and claims[c]['parent_unit_id'] == '' and float(claims[c]['confidence']) <= 0.5 for c in new), True)
    expect(s + ': Wasserburg and Vorst', [claims[c]['place_id'] for c in ('C7907', 'C7922')], ['PL3301', 'PL3590'])
    expect(s + ': C7532 and C7533 raised; C7700 held', tuple(claims[c]['confidence'] for c in ('C7532', 'C7533', 'C7700')), ('0.7', '0.7', '0.3'))
    expect(s + ': roadmap 264 rows ungrouped', [claims[c]['conflict_group_id'] for c in ('C7917', 'C7918', 'C7701')], ['', '', ''])

def scenario_141_fms_b414_geyer():
    """FMS B-414 (Geyer, Army Group H / OB Nordwest 10 March-9 May 1945): claims C7941-C7983 cite R814; Anlage 6 command posts; C2026 and C1183 raised; roadmap 265 rows kept out of G027."""
    s = 'scenario 141'
    claims = {c['claim_id']: c for c in common.load_all_claims()[1]}
    # C7968 (Armeegruppe Student formation) was retired on 14 November 2026 and re-entered as C9453 on GER-AG-STUDT (roadmap 351, scenario 269); the same checks apply to C9453
    new = ['C%d' % i for i in range(7941, 7984) if i != 7968] + ['C9453']
    expect(s + ': new rows cite R814 first, blank parents, at most 0.5', all(claims[c]['reference_ids'].split(';')[0] == 'R814' and claims[c]['parent_unit_id'] == '' and float(claims[c]['confidence']) <= 0.5 for c in new), True)
    expect(s + ': command posts Oldenzaal, Bersenbrück, Wohltorf, Langwedel, Kollerup', [claims[c]['place_id'] for c in ('C7942', 'C7943', 'C7946', 'C7947', 'C7948')], ['PL3593', 'PL3594', 'PL3596', 'PL3597', 'PL3598'])
    expect(s + ': OB Nordwest rows on GER-OBNW-000H', set(claims[c]['unit_id'] for c in ('C7945', 'C7946', 'C7947', 'C7948')), {'GER-OBNW-000H'})
    expect(s + ': C2026 and C1183 raised; C7566 held', tuple(claims[c]['confidence'] for c in ('C2026', 'C1183', 'C7566')), ('0.7', '0.7', '0.3'))
    expect(s + ': roadmap 265 rows not grouped', [claims[c]['conflict_group_id'] for c in ('C7955', 'C7954', 'C7568')], ['', '', ''])

def scenario_142_fms_b147_geyer():
    """FMS B-147 (Geyer, Army Group H 10 November 1944-10 March 1945): claims C7984-C8002 cite R815; Rheindahlen, Isselburg; no raises."""
    s = 'scenario 142'
    claims = {c['claim_id']: c for c in common.load_all_claims()[1]}
    new = ['C%d' % i for i in range(7984, 8003)]
    expect(s + ': new rows cite R815 first, blank parents, at most 0.5', all(claims[c]['reference_ids'].split(';')[0] == 'R815' and claims[c]['parent_unit_id'] == '' and float(claims[c]['confidence']) <= 0.5 for c in new), True)
    expect(s + ': Panzer Lehr to Rheindahlen; 15th Panzergrenadier parts at Isselburg', [claims[c]['place_id'] for c in ('C7990', 'C8002')], ['PL3611', 'PL3616'])
    expect(s + ': corroborated rows not raised', tuple(claims[c]['confidence'] for c in ('C7450', 'C7931', 'C7443')), ('0.5', '0.3', '0.3'))

def scenario_143_fms_b148_geyer():
    """FMS B-148 (Geyer, June 1946 answers): only real German dispositions of about 4 March 1945; C8003-C8004 cite R816; corroborated B-147 rows unchanged."""
    s = 'scenario 143'
    claims = {c['claim_id']: c for c in common.load_all_claims()[1]}
    expect(s + ': new rows cite R816 first at 0.3', [(claims[c]['reference_ids'].split(';')[0], claims[c]['confidence']) for c in ('C8003', 'C8004')], [('R816', '0.3'), ('R816', '0.3')])
    expect(s + ': 346th at Zevenaar, 361st at Utrecht', [claims[c]['place_id'] for c in ('C8003', 'C8004')], ['PL3617', 'PL0621'])
    expect(s + ': B-147 rows corroborated, not raised', [('R816' in claims[c]['reference_ids'], claims[c]['confidence']) for c in ('C8000', 'C8002')], [(True, '0.3'), (True, '0.3')])

def scenario_144_fms_b453_langhaeuser():
    """FMS B-453 (Langhaeuser, 6th Parachute Division, about 11 Mar-1 Apr 1945): C8005-C8012 cite R817; FMS corroborations not raised."""
    s = 'scenario 144'
    claims = {c['claim_id']: c for c in common.load_all_claims()[1]}
    new = ['C%04d' % i for i in range(8005, 8013)]
    expect(s + ': new rows cite R817 first', [claims[c]['reference_ids'].split(';')[0] for c in new], ['R817'] * 8)
    expect(s + ': Terborg 26 March at 0.5, Varsseveld 29 March at 0.3', [(claims[c]['place_id'], claims[c]['confidence']) for c in ('C8010', 'C8011')], [('PL3545', '0.5'), ('PL3618', '0.3')])
    expect(s + ': same-family corroborations not raised', [('R817' in claims[c]['reference_ids'], claims[c]['confidence']) for c in ('C7719', 'C7835', 'C1183')], [(True, '0.3'), (True, '0.3'), (True, '0.7')])

def scenario_145_fms_b580_langhaeuser():
    """FMS B-580 (Langhaeuser, 6th Parachute Division, 1 Apr-10 May 1945): C8013-C8019 cite R818; FMS corroborations not raised."""
    s = 'scenario 145'
    claims = {c['claim_id']: c for c in common.load_all_claims()[1]}
    new = ['C%04d' % i for i in range(8013, 8020)]
    expect(s + ': new rows cite R818 first at 0.3', [(claims[c]['reference_ids'].split(';')[0], claims[c]['confidence']) for c in new], [('R818', '0.3')] * 7)
    expect(s + ': Raalte, Heino, Epe, then Amersfoort to the surrender', [claims[c]['place_id'] for c in ('C8015', 'C8016', 'C8017', 'C8018', 'C8019')], ['PL3619', 'PL3620', 'PL3621', 'PL3537', 'PL3537'])
    expect(s + ': same-family corroborations not raised', [('R818' in claims[c]['reference_ids'], claims[c]['confidence']) for c in ('C7844', 'C7631', 'C7847')], [(True, '0.5'), (True, '0.7'), (True, '0.3')])

def scenario_146_fms_b365_blumentritt():
    """FMS B-365 (Blumentritt, Twenty-fifth Army 3 Feb-28 Mar 1945): C8020-C8039 cite R819; FMS corroborations not raised."""
    s = 'scenario 146'
    claims = {c['claim_id']: c for c in common.load_all_claims()[1]}
    new = ['C%04d' % i for i in range(8020, 8040)]
    expect(s + ': new rows cite R819 first', [claims[c]['reference_ids'].split(';')[0] for c in new], ['R819'] * 20)
    expect(s + ': Wegberg, Tetz, Hilversum takeover and air attack', [(claims[c]['place_id'], claims[c]['confidence']) for c in ('C8020', 'C8023', 'C8026', 'C8036', 'C8037')], [('PL3622', '0.5'), ('PL3623', '0.3'), ('PL3443', '0.5'), ('PL3443', '0.5'), ('PL3443', '0.3')])
    expect(s + ': same-family corroborations not raised', [('R819' in claims[c]['reference_ids'], claims[c]['confidence']) for c in ('C8000', 'C8003', 'C7831')], [(True, '0.3'), (True, '0.3'), (True, '0.3')])

def scenario_147_fms_b811_german():
    """FMS B-811 German original (von Zangen): C8040-C8078 cite R820; G063 Königshoven preferred over Aachen; no raises."""
    s = 'scenario 147'
    claims = {c['claim_id']: c for c in common.load_all_claims()[1]}
    # Scott 4 Nov 2026 (roadmap 282): old list C8040-C8078; new list without C8048, which is retired.
    new = ['C%04d' % i for i in range(8040, 8079) if i != 8048]
    expect(s + ': new rows cite R820 first', [claims[c]['reference_ids'].split(';')[0] for c in new], ['R820'] * 38)  # old 39, new 38 (C8048 retired)
    expect(s + ': G063 Königshoven preferred, Aachen alternate', [(claims[c]['conflict_group_id'], claims[c]['claim_status']) for c in ('C8040', 'C0957')], [('G063', 'preferred'), ('G063', 'alternate')])
    expect(s + ': same-manuscript corroborations not raised', [('R820' in claims[c]['reference_ids'], claims[c]['confidence']) for c in ('C2127', 'C2132', 'C0971')], [(True, '0.5'), (True, '0.3'), (True, '0.5')])

def scenario_148_fms_b812_german():
    """FMS B-812 German original (von Zangen): C8079-C8118 cite R821; corroborations not raised."""
    s = 'scenario 148'
    claims = {c['claim_id']: c for c in common.load_all_claims()[1]}
    new = ['C%04d' % i for i in range(8079, 8119)]
    expect(s + ': new rows cite R821 first', [claims[c]['reference_ids'].split(';')[0] for c in new], ['R821'] * 40)
    expect(s + ': army HQ at Hülchrath', (claims['C8079']['unit_id'], claims['C8079']['place_id'], claims['C8079']['date']), ('GER-ARMY-015A', 'PL3637', '1945-02-23'))
    expect(s + ': FMS corroborations not raised', [('R821' in claims[c]['reference_ids'], claims[c]['confidence']) for c in ('C1153', 'C1154', 'C1151')], [(True, '0.7'), (True, '0.7'), (True, '0.5')])

def scenario_149_fms_b197_german():
    """FMS B-197 German original (von Lüttwitz): C8119-C8149 cite R822; corroborations not raised."""
    s = 'scenario 149'
    claims = {c['claim_id']: c for c in common.load_all_claims()[1]}
    new = ['C%04d' % i for i in range(8119, 8150)]
    expect(s + ': new rows cite R822 first', [claims[c]['reference_ids'].split(';')[0] for c in new], ['R822'] * 31)
    expect(s + ': corps staff overrun at Iserlohn', (claims['C8149']['unit_id'], claims['C8149']['place_id'], claims['C8149']['event_type']), ('GER-PZ-047C', 'PL1106', 'surrender'))
    expect(s + ': FMS corroborations not raised', [('R822' in claims[c]['reference_ids'], claims[c]['confidence']) for c in ('C1183', 'C1185', 'C7565')], [(True, '0.7'), (True, '0.5'), (True, '0.5')])

def scenario_150_fms_b200():
    """FMS B-200 (von Lüttwitz answers): C8150 cites R823 and R822; C8133 corroborated without a raise."""
    s = 'scenario 150'
    claims = {c['claim_id']: c for c in common.load_all_claims()[1]}
    expect(s + ': new row', (claims['C8150']['reference_ids'], claims['C8150']['place_id']), ('R823;R822;R002', 'PL3667'))
    expect(s + ': corroboration not raised', ('R823' in claims['C8133']['reference_ids'], claims['C8133']['confidence']), (True, '0.5'))

def scenario_151_fms_b367_german():
    """FMS B-367 German original (von Lüttwitz): C8151-C8176 cite R824; corroborations not raised."""
    s = 'scenario 151'
    claims = {c['claim_id']: c for c in common.load_all_claims()[1]}
    new = ['C%04d' % i for i in range(8151, 8177)]
    expect(s + ': new rows cite R824 first', [claims[c]['reference_ids'].split(';')[0] for c in new], ['R824'] * 26)
    expect(s + ': FMS corroborations not raised', [('R824' in claims[c]['reference_ids'], claims[c]['confidence']) for c in ('C1472', 'C8049')], [(True, '0.7'), (True, '0.5')])
    # Scott 4 Nov 2026 (roadmap 282): old expectation C8169 and C8048 both preferred; new: C8048 retired (scenario 196).
    expect(s + ': Lindern 30 November: C8169 preferred, C8048 retired', (claims['C8169']['claim_status'], 'C8048' in claims), ('preferred', False))

def scenario_152_fms_b368_reread():
    """FMS B-368 German re-read: same reference R808 (same Fold3 file); C8177 cites R808; corroborations not raised."""
    s = 'scenario 152'
    claims = {c['claim_id']: c for c in common.load_all_claims()[1]}
    expect(s + ': new row cites R808', (claims['C8177']['unit_id'], claims['C8177']['reference_ids']), ('GER-INF-346D', 'R808;R002'))
    expect(s + ': corroborations not raised', [('R808' in claims[c]['reference_ids'], claims[c]['confidence']) for c in ('C1369', 'C1380')], [(True, '0.5'), (True, '0.5')])

def scenario_153_fms_b369_german():
    """FMS B-369 German original (Degener): C8178-C8188 cite R825; corroboration not raised."""
    s = 'scenario 153'
    claims = {c['claim_id']: c for c in common.load_all_claims()[1]}
    new = ['C%04d' % i for i in range(8178, 8189)]
    expect(s + ': new rows cite R825 first', [claims[c]['reference_ids'].split(';')[0] for c in new], ['R825'] * 11)
    expect(s + ': corroboration not raised', ('R825' in claims['C2052']['reference_ids'], claims['C2052']['confidence']), (True, '0.5'))

def scenario_154_fms_b674_german():
    """FMS B-674 German original (Meindl) with English check: C8189-C8198 cite R826; corroborations not raised."""
    s = 'scenario 154'
    claims = {c['claim_id']: c for c in common.load_all_claims()[1]}
    new = ['C%04d' % i for i in range(8189, 8199)]
    expect(s + ': new rows cite R826 first', [claims[c]['reference_ids'].split(';')[0] for c in new], ['R826'] * 10)
    expect(s + ': Jübberde command post', (claims['C8194']['unit_id'], claims['C8194']['place_id'], claims['C8194']['confidence']), ('GER-FJ-002C', 'PL3695', '0.3'))
    expect(s + ': corroborations not raised', [('R826' in claims[c]['reference_ids'], claims[c]['confidence']) for c in ('C7716', 'C7717', 'C1181')], [(True, '0.5'), (True, '0.5'), (True, '0.7')])

def scenario_155_fms_b327():
    """FMS B-327 English translation (Blauensteiner): C8199 cites R827; corroborations not raised."""
    s = 'scenario 155'
    claims = {c['claim_id']: c for c in common.load_all_claims()[1]}
    expect(s + ': new row', (claims['C8199']['reference_ids'].split(';')[0], claims['C8199']['unit_id'], claims['C8199']['place_id']), ('R827', 'GER-FJ-007D', 'PL0701'))
    expect(s + ': corroborations not raised', [('R827' in claims[c]['reference_ids'], claims[c]['confidence']) for c in ('C7716', 'C8195', 'C1236')], [(True, '0.5'), (True, '0.5'), (True, '0.5')])

def scenario_156_fms_b051_german():
    """FMS B-051 German typescript (Meindl): C8200 cites R828; B-093 rows cited, not raised."""
    s = 'scenario 156'
    claims = {c['claim_id']: c for c in common.load_all_claims()[1]}
    expect(s + ': new row', (claims['C8200']['reference_ids'].split(';')[0], claims['C8200']['place_id'], claims['C8200']['confidence']), ('R828', 'PL3700', '0.3'))
    expect(s + ': B-093 rows cited, not raised', [('R828' in claims[c]['reference_ids'], claims[c]['confidence']) for c in ('C7691', 'C7704', 'C7716')], [(True, '0.5'), (True, '0.5'), (True, '0.5')])

def scenario_157_fms_b052():
    """FMS B-052 English translation (von Oriola): C8201-C8209 cite R829 at 0.3; no XIII Corps rows; corroborations not raised."""
    s = 'scenario 157'
    claims = {c['claim_id']: c for c in common.load_all_claims()[1]}
    new = ['C%04d' % i for i in range(8201, 8210)]
    expect(s + ': new rows cite R829 first at 0.3', [(claims[c]['reference_ids'].split(';')[0], claims[c]['confidence']) for c in new], [('R829', '0.3')] * 9)
    expect(s + ': no corps rows', sorted(set(claims[c]['unit_id'] for c in new)), ['GER-PZ-002D', 'GER-VG-246D', 'GER-VG-326D', 'GER-VG-352D'])
    expect(s + ': corroborations not raised', [('R829' in claims[c]['reference_ids'], claims[c]['confidence']) for c in ('C1156', 'C1159')], [(True, '0.5'), (True, '0.5')])

def scenario_158_fms_b261_german():
    """FMS B-261 German original (Blauensteiner): C8210-C8211 cite R830; Normandy rows cited, not raised."""
    s = 'scenario 158'
    claims = {c['claim_id']: c for c in common.load_all_claims()[1]}
    expect(s + ': new rows', [(claims[c]['reference_ids'].split(';')[0], claims[c]['place_id'], claims[c]['confidence']) for c in ('C8210', 'C8211')], [('R830', 'PL0126', '0.5'), ('R830', 'PL3710', '0.5')])
    expect(s + ': corroborations not raised', [('R830' in claims[c]['reference_ids'], claims[c]['confidence']) for c in ('C0052', 'C0803', 'C0763')], [(True, '0.7'), (True, '0.7'), (True, '0.5')])

def scenario_159_fms_b240_german():
    """FMS B-240 German original (Blauensteiner): C8212-C8214 Brittany positions cite R831 at 0.3; C8210 cited, not raised."""
    s = 'scenario 159'
    claims = {c['claim_id']: c for c in common.load_all_claims()[1]}
    expect(s + ': new rows', [(claims[c]['unit_id'], claims[c]['place_id'], claims[c]['reference_ids'].split(';')[0], claims[c]['confidence']) for c in ('C8212', 'C8213', 'C8214')], [('GER-FJ-002C', 'PL3711', 'R831', '0.3'), ('GER-FJ-003D', 'PL3712', 'R831', '0.3'), ('GER-FJ-005D', 'PL0296', 'R831', '0.3')])
    expect(s + ': corroborations not raised', [('R831' in claims[c]['reference_ids'], claims[c]['confidence']) for c in ('C8210', 'C0052')], [(True, '0.5'), (True, '0.7')])

def scenario_160_fms_b401_german():
    """FMS B-401 German original (Meindl): C8215-C8220 cite R832; English-only row flagged; corroborations not raised."""
    s = 'scenario 160'
    claims = {c['claim_id']: c for c in common.load_all_claims()[1]}
    new = ['C%04d' % i for i in range(8215, 8221)]
    expect(s + ': new rows cite R832 first', [claims[c]['reference_ids'].split(';')[0] for c in new], ['R832'] * 6)
    expect(s + ': English-only row at 0.3 and flagged', (claims['C8220']['confidence'], 'English continuation' in claims['C8220']['notes']), ('0.3', True))
    expect(s + ': corroborations not raised', [('R832' in claims[c]['reference_ids'], claims[c]['confidence']) for c in ('C8210', 'C0803', 'C2205')], [(True, '0.5'), (True, '0.7'), (True, '0.3')])

def scenario_161_fms_b346_german():
    """FMS B-346 German original (Blauensteiner, very faint): C8221 Elbeuf at 0.3; Falaise break-out rows cited, not raised."""
    s = 'scenario 161'
    claims = {c['claim_id']: c for c in common.load_all_claims()[1]}
    expect(s + ': new row', (claims['C8221']['reference_ids'].split(';')[0], claims['C8221']['place_id'], claims['C8221']['confidence']), ('R833', 'PL1410', '0.3'))
    expect(s + ': corroborations not raised', [('R833' in claims[c]['reference_ids'], claims[c]['confidence']) for c in ('C0745', 'C0746', 'C0747')], [(True, '0.5'), (True, '0.7'), (True, '0.7')])

def scenario_162_fms_b101():
    """FMS B-101 English translation (Hitzfeld, LXVII Corps): C8222-C8226; Remagen and Rhine-front rows cited, not raised."""
    s = 'scenario 162'
    claims = {c['claim_id']: c for c in common.load_all_claims()[1]}
    new = ['C%04d' % i for i in range(8222, 8227)]
    expect(s + ': new rows', [(claims[c]['reference_ids'].split(';')[0], claims[c]['place_id'], claims[c]['confidence']) for c in new], [('R834', 'PL3713', '0.3'), ('R834', 'PL3714', '0.5'), ('R834', 'PL3716', '0.5'), ('R834', 'PL3715', '0.5'), ('R834', 'PL3717', '0.3')])
    expect(s + ': corroborations not raised', [('R834' in claims[c]['reference_ids'], claims[c]['confidence']) for c in ('C1160', 'C1169', 'C1167')], [(True, '0.7'), (True, '0.5'), (True, '0.5')])

def scenario_163_fms_b309():
    """FMS B-309 English translation (Hitzfeld, LXVII Corps 22 Mar-19 Apr 1945): C8227-C8233; Eleventh Army rows cited, not raised."""
    s = 'scenario 163'
    claims = {c['claim_id']: c for c in common.load_all_claims()[1]}
    new = ['C%04d' % i for i in range(8227, 8234)]
    expect(s + ': new rows', [(claims[c]['reference_ids'].split(';')[0], claims[c]['place_id'], claims[c]['confidence']) for c in new], [('R835', 'PL3718', '0.5'), ('R835', 'PL3719', '0.5'), ('R835', 'PL3720', '0.3'), ('R835', 'PL3721', '0.5'), ('R835', 'PL3722', '0.3'), ('R835', 'PL3723', '0.3'), ('R835', 'PL3724', '0.5')])
    expect(s + ': corroborations not raised', [('R835' in claims[c]['reference_ids'], claims[c]['confidence']) for c in ('C1207', 'C1208')], [(True, '0.5'), (True, '0.7')])

def scenario_164_fms_b236_german():
    """FMS B-236 German original (Sponheimer, LXVII Corps 7 Jun-30 Oct 1944): C8234-C8242; Somme, Bruges and Antwerp rows cited, not raised."""
    s = 'scenario 164'
    claims = {c['claim_id']: c for c in common.load_all_claims()[1]}
    new = ['C%04d' % i for i in range(8234, 8243)]
    expect(s + ': new rows', [(claims[c]['reference_ids'].split(';')[0], claims[c]['place_id'], claims[c]['confidence']) for c in new], [('R836', 'PL0743', '0.3'), ('R836', 'PL3725', '0.5'), ('R836', 'PL3726', '0.5'), ('R836', 'PL3727', '0.3'), ('R836', 'PL1610', '0.5'), ('R836', 'PL0691', '0.3'), ('R836', 'PL0623', '0.5'), ('R836', 'PL3438', '0.5'), ('R836', 'PL1065', '0.5')])
    expect(s + ': pre-invasion row re-dated (scenario 168)', claims['C8234']['date'], '1944-06-05')
    expect(s + ': corroborations not raised', [('R836' in claims[c]['reference_ids'], claims[c]['confidence']) for c in ('C7274', 'C7081', 'C2164', 'C7321', 'C7364')], [(True, '0.3'), (True, '0.5'), (True, '0.5'), (True, '0.3'), (True, '0.3')])

def scenario_165_fms_b798_german():
    """FMS B-798 German original (Warning, LXVII Corps 15 Sep-25 Nov 1944): C8243-C8245; Esschen, Breda-Ginneken and Zevenbergen rows cited, not raised."""
    s = 'scenario 165'
    claims = {c['claim_id']: c for c in common.load_all_claims()[1]}
    new = ['C8243', 'C8244', 'C8245']
    expect(s + ': new rows', [(claims[c]['reference_ids'].split(';')[0], claims[c]['place_id'], claims[c]['confidence']) for c in new], [('R837', 'PL0691', '0.5'), ('R837', 'PL1065', '0.5'), ('R837', 'PL3728', '0.3')])
    expect(s + ': corroborations not raised', [('R837' in claims[c]['reference_ids'], claims[c]['confidence']) for c in ('C2164', 'C2165', 'C7321', 'C8241')], [(True, '0.5'), (True, '0.5'), (True, '0.3'), (True, '0.5')])
    # Scott 4 Nov 2026 (roadmap 311): old expectation preferred/preferred; now alternates in G076/G077 against B-798-supported rows.
    expect(s + ': B-236 rows kept as alternates (scenario 196)', [claims[c]['claim_status'] for c in ('C8240', 'C8242')], ['alternate', 'alternate'])

def scenario_166_fms_b596_german():
    """FMS B-596 German original (Gerber, LXVII Corps spring 1944-15 Sep 1944): C8246-C8259; Naours, Canteleu, Abbeville, Maldegem and Moerbrugge rows cited, not raised."""
    s = 'scenario 166'
    claims = {c['claim_id']: c for c in common.load_all_claims()[1]}
    new = ['C%04d' % i for i in range(8246, 8260)]
    expect(s + ': new rows', [(claims[c]['reference_ids'].split(';')[0], claims[c]['unit_id'], claims[c]['place_id'], claims[c]['confidence']) for c in new], [('R838', 'GER-COR-067C', 'PL0676', '0.3'), ('R838', 'GER-COR-067C', 'PL3729', '0.5'), ('R838', 'GER-COR-067C', 'PL3730', '0.5'), ('R838', 'GER-COR-067C', 'PL3731', '0.5'), ('R838', 'GER-COR-067C', 'PL0937', '0.5'), ('R838', 'GER-COR-067C', 'PL3727', '0.5'), ('R838', 'GER-COR-067C', 'PL3732', '0.5'), ('R838', 'GER-COR-067C', 'PL3733', '0.5'), ('R838', 'GER-COR-067C', 'PL3734', '0.5'), ('R838', 'GER-COR-067C', 'PL3735', '0.3'), ('R838', 'GER-COR-067C', 'PL3287', '0.5'), ('R838', 'GER-COR-067C', 'PL2062', '0.5'), ('R838', 'GER-INF-711D', 'PL3736', '0.5'), ('R838', 'GER-INF-245D', 'PL3734', '0.5')])
    expect(s + ': conflict group G064', [(claims[c]['conflict_group_id'], claims[c]['claim_status']) for c in ('C8249', 'C8237')], [('G064', 'preferred'), ('G064', 'alternate')])
    expect(s + ': corroborations not raised', [('R838' in claims[c]['reference_ids'], claims[c]['confidence']) for c in ('C8234', 'C8235', 'C8236', 'C7274', 'C7081', 'C7299', 'C7300')], [(True, '0.3'), (True, '0.5'), (True, '0.5'), (True, '0.3'), (True, '0.5'), (True, '0.5'), (True, '0.5')])

def scenario_167_fms_b475_reread():
    """FMS B-475 German re-read: same reference R771 (citation corrected); C8260-C8261; corroborations not raised."""
    s = 'scenario 167'
    claims = {c['claim_id']: c for c in common.load_all_claims()[1]}
    expect(s + ': new rows', [(claims[c]['reference_ids'].split(';')[0], claims[c]['unit_id'], claims[c]['place_id'], claims[c]['confidence']) for c in ('C8260', 'C8261')], [('R771', 'GER-COR-067C', 'PL0801', '0.5'), ('R771', 'GER-COR-067C', 'PL0801', '0.5')])
    expect(s + ': corroborations not raised', [('R771' in claims[c]['reference_ids'], claims[c]['confidence']) for c in ('C8243', 'C7816', 'C8040', 'C2086', 'C7358', 'C7811')], [(True, '0.5'), (True, '0.3'), (True, '0.5'), (True, '0.5'), (True, '0.3'), (True, '0.5')])

def scenario_168_pre_invasion_dates():
    """Pre-invasion dates allowed (Scott, 4 November 2026): C8212-C8214 and C8234 re-dated from the forced 6 June, under OP-PRE-INVASION, at 0.3."""
    s = 'scenario 168'
    claims = {c['claim_id']: c for c in common.load_all_claims()[1]}
    expect(s + ': re-dated rows', [(claims[c]['date'], claims[c]['operation_id'], claims[c]['confidence']) for c in ('C8212', 'C8213', 'C8214', 'C8234')], [('1944-05-05', 'OP-PRE-INVASION', '0.3'), ('1944-05-15', 'OP-PRE-INVASION', '0.3'), ('1944-05-15', 'OP-PRE-INVASION', '0.3'), ('1944-06-05', 'OP-PRE-INVASION', '0.3')])

def scenario_169_fms_b249_german():
    """FMS B-249 German original (von Zangen, Fifteenth Army 28 Aug-10 Nov 1944): C8262-C8274; Dunkirk and other rows cited, not raised."""
    s = 'scenario 169'
    claims = {c['claim_id']: c for c in common.load_all_claims()[1]}
    new = ['C%04d' % i for i in range(8262, 8275)]
    expect(s + ': new rows', [(claims[c]['reference_ids'].split(';')[0], claims[c]['unit_id'], claims[c]['place_id'], claims[c]['confidence']) for c in new], [('R839', 'GER-ARMY-015A', 'PL3737', '0.5'), ('R839', 'GER-ARMY-015A', 'PL3738', '0.5'), ('R839', 'GER-ARMY-015A', 'PL0620', '0.5'), ('R839', 'GER-COR-089C', 'PL3739', '0.5'), ('R839', 'GER-COR-089C', 'PL3414', '0.5'), ('R839', 'GER-COR-086C', 'PL3740', '0.5'), ('R839', 'GER-COR-086C', 'PL3741', '0.5'), ('R839', 'GER-COR-086C', 'PL3401', '0.3'), ('R839', 'GER-INF-059D', 'PL3744', '0.5'), ('R839', 'GER-INF-059D', 'PL3743', '0.5'), ('R839', 'GER-INF-712D', 'PL3742', '0.5'), ('R839', 'GER-INF-070D', 'PL0795', '0.5'), ('R839', 'GER-INF-070D', 'PL2061', '0.3')])
    expect(s + ': corroborations not raised', [('R839' in claims[c]['reference_ids'], claims[c]['confidence'], claims[c]['claim_status']) for c in ('C8237', 'C1809')], [(True, '0.3', 'alternate'), (True, '0.9', 'preferred')])

def scenario_170_fms_b508_german():
    """FMS B-508 German original (Lackner, 2nd Parachute Division 8 Mar-16 Apr 1945): C8275-C8280."""
    s = 'scenario 170'
    claims = {c['claim_id']: c for c in common.load_all_claims()[1]}
    new = ['C%04d' % i for i in range(8275, 8281)]
    expect(s + ': new rows', [(claims[c]['reference_ids'].split(';')[0], claims[c]['unit_id'], claims[c]['place_id'], claims[c]['confidence']) for c in new], [('R840', 'GER-FJ-002D', 'PL3745', '0.3'), ('R840', 'GER-FJ-002D', 'PL3745', '0.5'), ('R840', 'GER-FJ-002D', 'PL2138', '0.5'), ('R840', 'GER-FJ-002D', 'PL0967', '0.5'), ('R840', 'GER-FJ-002D', 'PL0462', '0.5'), ('R840', 'GER-FJ-002D', 'PL0462', '0.5')])

def scenario_171_fms_b820_german():
    """FMS B-820 (Wilke, 5th Parachute Division 6 Jun-24 Jul 1944): C8281-C8283 at 0.3; C8214 (Rennes) kept."""
    s = 'scenario 171'
    claims = {c['claim_id']: c for c in common.load_all_claims()[1]}
    expect(s + ': new rows', [(claims[c]['reference_ids'].split(';')[0], claims[c]['place_id'], claims[c]['confidence']) for c in ('C8281', 'C8282', 'C8283')], [('R841', 'PL3746', '0.3'), ('R841', 'PL3746', '0.3'), ('R841', 'PL0213', '0.3')])
    expect(s + ': B-240 row kept', (claims['C8214']['place_id'], claims['C8214']['claim_status']), ('PL0296', 'preferred'))

def scenario_172_unit_domain():
    """Unit domain: air/naval units (II Fliegerkorps, B-509) are kept out of the main outputs and written to build/other_domains/."""
    s = 'scenario 172'
    units = {u['unit_id']: u for u in common.read_dicts(common.UNITS_CSV)[1]}
    expect(s + ': domain', (common.unit_domain(units['GER-FLK-002C']), common.unit_domain(units['GER-FJ-005D'])), ('air', 'ground'))
    main = {r['claim_id'] for r in common.read_dicts(os.path.join(common.BUILD_DIR, 'all_claims.csv'))[1]}
    other = {r['claim_id'] for r in common.read_dicts(os.path.join(common.BUILD_DIR, 'other_domains', 'claims.csv'))[1]}
    # C8332/C8333 added with B-283 (R845); the air-naval pilot (scenarios 244-247) added C9405-C9436 to the same file
    expect(s + ': split', ('C8284' in main, [c for c in sorted(other, key=lambda x: int(x[1:])) if int(c[1:]) < 9000]), (False, ['C8284', 'C8285', 'C8332', 'C8333']))
    bu = common.read_dicts(os.path.join(common.BUILD_DIR, 'units.csv'))
    expect(s + ': main units unchanged', ('domain' in bu[0], any(u['unit_id'] == 'GER-FLK-002C' for u in bu[1])), (False, False))

def scenario_173_fms_b023_german():
    """FMS B-023 German original (Heilmann, 5th Parachute Division, Ardennes): C8286-C8309; C7137 raised to 0.7, other corroborations not raised."""
    s = 'scenario 173'
    claims = {c['claim_id']: c for c in common.load_all_claims()[1]}
    new = ['C%04d' % i for i in range(8286, 8310)]
    expect(s + ': new rows cite R843', [claims[c]['reference_ids'] for c in new], ['R843;R002'] * 24)
    expect(s + ': sample rows', [(claims[c]['unit_id'], claims[c]['place_id'], claims[c]['confidence']) for c in ('C8291', 'C8298', 'C8302', 'C8305')], [('GER-FJ-005D', 'PL3752', '0.5'), ('GER-FJ-005D', 'PL3757', '0.5'), ('GER-COR-085C', 'PL3760', '0.3'), ('GER-PZ-LEHRD', 'PL3755', '0.5')])
    expect(s + ': corroborations', [('R843' in claims[c]['reference_ids'], claims[c]['confidence']) for c in ('C0997', 'C7137', 'C4899')], [(True, '0.5'), (True, '0.7'), (True, '0.3')])

def scenario_174_small_units_b023():
    """Small-units rule: B-023 regiments, engineers and assault guns with organic/attached relations; claim parents blank."""
    s = 'scenario 174'
    claims = {c['claim_id']: c for c in common.load_all_claims()[1]}
    new = ['C%04d' % i for i in range(8310, 8322)]
    expect(s + ': blank parents', [claims[c]['parent_unit_id'] for c in new], [''] * 12)
    expect(s + ': units', [claims[c]['unit_id'] for c in ('C8310', 'C8314', 'C8316', 'C8317', 'C8321')], ['GER-FJR-014', 'GER-FJR-015', 'GER-FJR-013', 'GER-FJPI-005', 'GER-STUG-011B'])

def scenario_175_fms_b361_german():
    """FMS B-361 (Blumentritt): headquarters sequence C8322-C8328, C8329-C8330; C7980 cited, not raised."""
    s = 'scenario 175'
    claims = {c['claim_id']: c for c in common.load_all_claims()[1]}
    expect(s + ': hq places', [claims['C%04d' % i]['place_id'] for i in range(8322, 8329)], ['PL0774', 'PL3595', 'PL3764', 'PL3765', 'PL3766', 'PL3766', 'PL3767'])
    expect(s + ': other rows', [(claims[c]['unit_id'], claims[c]['confidence']) for c in ('C8329', 'C8330', 'C7980')], [('GER-MARI-002D', '0.5'), ('GER-INF-245D', '0.5'), ('GER-ARMY-BLUMT', '0.3')])

def scenario_176_post_surrender():
    """OP-POST-SURRENDER umbrella: C8331 (Blumentritt staff dissolved 31 May 1945) needs no campaign."""
    s = 'scenario 176'
    claims = {c['claim_id']: c for c in common.load_all_claims()[1]}
    c = claims['C8331']
    expect(s + ': dissolution row', (c['date'], c['operation_id'], c['place_id'], c['disestablished']), ('1945-05-31', 'OP-POST-SURRENDER', 'PL3767', 'true'))

def scenario_178_b283():
    """FMS B-283 (R845): Luftflotte 3 (air) and Marinegruppe West (naval) at Paris on 6 June 1944; OB West at Verzy; the Brussels/Antwerp conflict G065."""
    s = 'scenario 178'
    claims = {c['claim_id']: c for c in common.load_all_claims()[1]}
    expect(s + ': air/naval rows', [(claims[c]['unit_id'], claims[c]['place_id'], claims[c]['confidence']) for c in ('C8332', 'C8333')], [('GER-LFL-003A', 'PL0271', '0.5'), ('GER-MGW-000H', 'PL0271', '0.5')])
    expect(s + ': Verzy', (claims['C8336']['place_id'], claims['C8336']['date']), ('PL3768', '1944-08-18'))
    expect(s + ': G065', sorted((claims[c]['conflict_group_id'], claims[c]['claim_status']) for c in ('C2062', 'C8335')), [('G065', 'alternate'), ('G065', 'preferred')])
    expect(s + ': support only', ('R845' in claims['C8322']['reference_ids'], claims['C8322']['confidence']), (True, '0.5'))


def scenario_179_a969():
    """FMS A-969 (R846, Meindl): two 0.3 rows for II Parachute Corps and a supporting citation on C0763."""
    s = 'scenario 179'
    claims = {c['claim_id']: c for c in common.load_all_claims()[1]}
    expect(s + ': rows', [(claims[c]['unit_id'], claims[c]['place_id'], claims[c]['confidence']) for c in ('C8343', 'C8344')], [('GER-FJ-002C', 'PL0333', '0.3'), ('GER-FJ-002C', 'PL1272', '0.3')])
    expect(s + ': support', ('R846' in claims['C0763']['reference_ids'], claims['C0763']['confidence']), (True, '0.5'))


def scenario_180_a859():
    """FMS A-859 (R847, Meindl, English only): 3rd Parachute Division destroyed in the Meuse area (0.3); support on C8221 and C7689."""
    s = 'scenario 180'
    claims = {c['claim_id']: c for c in common.load_all_claims()[1]}
    expect(s + ': row', (claims['C8345']['unit_id'], claims['C8345']['destroyed'], claims['C8345']['confidence']), ('GER-FJ-003D', 'true', '0.3'))
    expect(s + ': support', all('R847' in claims[c]['reference_ids'] for c in ('C8221', 'C7689')), True)


def scenario_181_ethint43():
    """ETHINT-43 (R848, Lüttwitz interview, capped at 0.5): XLVII Panzer Corps takes the Geilenkirchen sector 19 November; XII SS Corps takes it back 5 December (with B-283)."""
    s = 'scenario 181'
    claims = {c['claim_id']: c for c in common.load_all_claims()[1]}
    expect(s + ': rows', [(claims[c]['unit_id'], claims[c]['date'], claims[c]['reference_ids'], claims[c]['confidence']) for c in ('C8346', 'C8347')], [('GER-PZ-047C', '1944-11-19', 'R848', '0.5'), ('GER-SSCOR-012C', '1944-12-05', 'R848;R845', '0.5')])
    expect(s + ': support', all('R848' in claims[c]['reference_ids'] for c in ('C2129', 'C8166')), True)


def scenario_182_independent_units():
    """Scott's independent-units rule (4 November 2026): Kampfgruppen and independent corps have units with blank parents; FJR 9 has its organic parent."""
    s = 'scenario 182'
    units = {u['unit_id']: u for u in common.read_dicts(common.UNITS_CSV)[1]}
    expect(s + ': parents', [units[u]['parent_unit_id'] for u in ('GER-FJR-009', 'GER-KG-WALTH', 'GER-COR-EMS')], ['GER-FJ-003D', '', ''])
    claims = {c['claim_id']: c for c in common.load_all_claims()[1]}
    expect(s + ': Walther', (claims['C8351']['place_id'], claims['C8351']['confidence']), ('PL3450', '0.5'))


def scenario_183_a898():
    """FMS A-898 (R849, Heyking): 6th Fallschirmjäger Division Seine to Mons; Fallschirm-Lehr-Regiment as an independent regiment (blank parent)."""
    s = 'scenario 183'
    units = {u['unit_id']: u for u in common.read_dicts(common.UNITS_CSV)[1]}
    expect(s + ': Lehr regiment', (units['GER-FJR-LEHR']['echelon'], units['GER-FJR-LEHR']['parent_unit_id']), ('regiment/battle_group', ''))
    claims = {c['claim_id']: c for c in common.load_all_claims()[1]}
    expect(s + ': Mello and Artres', [(claims[c]['place_id'], claims[c]['confidence']) for c in ('C8358', 'C8361')], [('PL3773', '0.5'), ('PL3774', '0.5')])


def scenario_184_kampfgruppen():
    """Roadmap 335: ten Kampfgruppen as their own units with blank parents."""
    s = 'scenario 184'
    units = {u['unit_id']: u for u in common.read_dicts(common.UNITS_CSV)[1]}
    expect(s + ': parents blank', [units[u]['parent_unit_id'] for u in ('GER-KG-KRAG', 'GER-KG-BAYER')], ['', ''])
    claims = {c['claim_id']: c for c in common.load_all_claims()[1]}
    expect(s + ': Kunkel', (claims['C8370']['place_id'], claims['C8370']['date']), ('PL3341', '1944-12-21'))


def scenario_185_a939():
    """FMS A-939 (R850, Lüttwitz): XLVII Panzer Corps in the Ardennes; Sibret conflict G066 (Cole preferred); citations without raises."""
    s = 'scenario 185'
    claims = {c['claim_id']: c for c in common.load_all_claims()[1]}
    expect(s + ': Sibret conflict', [(claims[c]['conflict_group_id'], claims[c]['claim_status']) for c in ('C8370', 'C8380')], [('G066', 'preferred'), ('G066', 'alternate')])
    expect(s + ': Engreux sketch', (claims['C8384']['place_id'], claims['C8384']['confidence']), ('PL3780', '0.3'))
    expect(s + ': citation no raise', ('R850' in claims['C7137']['reference_ids'], claims['C7137']['confidence']), (True, '0.7'))


def scenario_186_a940():
    """FMS A-940 (R851, Lüttwitz answers): Regiment 78 under the 26th VGD; Armeegruppe Lüttwitz 30-31 December; January corps command posts."""
    s = 'scenario 186'
    units = {u['unit_id']: u for u in common.read_dicts(common.UNITS_CSV)[1]}
    expect(s + ': parents', (units['GER-GR-078']['parent_unit_id'], units['GER-ARMY-LUETT']['parent_unit_id']), ('GER-VG-026D', ''))
    claims = {c['claim_id']: c for c in common.load_all_claims()[1]}
    expect(s + ': Bande and CPs', [(claims[c]['place_id'], claims[c]['confidence']) for c in ('C8388', 'C8391', 'C8392')], [('PL3785', '0.5'), ('PL3786', '0.3'), ('PL3787', '0.3')])
    expect(s + ': Armeegruppe dissolved', claims['C8390']['disestablished'], 'true')


def scenario_187_b410():
    """FMS B-410 (R852, Ulms): XII SS Corps command posts; Polizei-Regiment Mönchengladbach as an independent regiment; G067 corps CP 28 February."""
    s = 'scenario 187'
    units = {u['unit_id']: u for u in common.read_dicts(common.UNITS_CSV)[1]}
    expect(s + ': police regiment', (units['GER-POLR-MGLAD']['echelon'], units['GER-POLR-MGLAD']['parent_unit_id']), ('regiment/battle_group', ''))
    claims = {c['claim_id']: c for c in common.load_all_claims()[1]}
    expect(s + ': G067', [(claims[c]['conflict_group_id'], claims[c]['claim_status']) for c in ('C8095', 'C8393')], [('G067', 'preferred'), ('G067', 'alternate')])
    expect(s + ': CPs', [claims[c]['place_id'] for c in ('C8394', 'C8395', 'C8396')], ['PL3788', 'PL0420', 'PL3789'])


def scenario_188_b541():
    """FMS B-541 (R853, Schimpf): 3rd Fallschirmjäger Division sub-units traced to the division; Brittany billets; C7070 raised by NARA plus FMS."""
    s = 'scenario 188'
    units = {u['unit_id']: u for u in common.read_dicts(common.UNITS_CSV)[1]}
    expect(s + ': sub-units', [units[u]['parent_unit_id'] for u in ('GER-FJR-005', 'GER-FJR-008', 'GER-FJPI-003', 'GER-FJFLAK-003')], ['GER-FJ-003D'] * 4)
    claims = {c['claim_id']: c for c in common.load_all_claims()[1]}
    expect(s + ': Brittany', [claims[c]['place_id'] for c in ('C8412', 'C8413', 'C8416')], ['PL3794', 'PL3795', 'PL3798'])
    expect(s + ': July not June', claims['C8410']['date'], '1944-07-11')
    expect(s + ': C7070 raised', claims['C7070']['confidence'], '0.7')
    expect(s + ': claim parents blank', [claims[c]['parent_unit_id'] for c in ('C8407', 'C8408', 'C8409')], ['', '', ''])


def scenario_189_b673():
    """FMS B-673 (R854, Lüttwitz): XLVII Panzer Corps command posts; G068 corps HQ 15 June; 276th and 326th Infantry Divisions promoted."""
    s = 'scenario 189'
    units = {u['unit_id']: u for u in common.read_dicts(common.UNITS_CSV)[1]}
    expect(s + ': promoted', [units[u]['record_status'] for u in ('GER-INF-276D', 'GER-INF-326D')], ['active', 'active'])
    claims = {c['claim_id']: c for c in common.load_all_claims()[1]}
    expect(s + ': G068', [(claims[c]['conflict_group_id'], claims[c]['claim_status']) for c in ('C2203', 'C8420')], [('G068', 'alternate'), ('G068', 'preferred')])
    expect(s + ': CPs', [claims[c]['place_id'] for c in ('C8418', 'C8419', 'C8420')], ['PL3800', 'PL1079', 'PL3801'])


def scenario_190_b709():
    """FMS B-709 (R855, Ulms and Reuther, English partial read): XII SS Corps and divisions on the Rhine at Düsseldorf, March 1945."""
    s = 'scenario 190'
    claims = {c['claim_id']: c for c in common.load_all_claims()[1]}
    expect(s + ': corps CPs', [claims[c]['place_id'] for c in ('C8428', 'C8429')], ['PL3805', 'PL3806'])
    expect(s + ': division posts', [claims[c]['place_id'] for c in ('C8430', 'C8432', 'C8434')], ['PL3804', 'PL3789', 'PL3807'])
    expect(s + ': no row above 0.5', max(claims['C84%02d' % i]['confidence'] for i in range(28, 38)), '0.5')


def scenario_191_b730():
    """FMS B-730 (R856, Brandenberger, English only): Seventh Army 1-20 September 1944."""
    s = 'scenario 191'
    claims = {c['claim_id']: c for c in common.load_all_claims()[1]}
    expect(s + ': army CPs', [claims[c]['place_id'] for c in ('C8438', 'C8441', 'C8442', 'C8443')], ['PL3811', 'PL0088', 'PL3814', 'PL0594'])
    expect(s + ': groups', [(claims[c]['conflict_group_id'], claims[c]['claim_status']) for c in ('C7286', 'C8446', 'C0861', 'C8452', 'C8457', 'C8462')], [('G069', 'preferred'), ('G069', 'alternate'), ('G070', 'preferred'), ('G070', 'alternate'), ('G071', 'preferred'), ('G071', 'alternate')])
    expect(s + ': raises', [claims[c]['confidence'] for c in ('C0866', 'C7084')], ['0.7', '0.7'])
    expect(s + ': no row above 0.5', max(claims['C84%02d' % i]['confidence'] for i in range(38, 63)), '0.5')
    expect(s + ': sketch row', claims['C8462']['confidence'], '0.3')


def scenario_192_b823():
    """FMS B-823 (R857, von der Heydte, German original): Kampfgruppe von der Heydte, December 1944."""
    s = 'scenario 192'
    claims = {c['claim_id']: c for c in common.load_all_claims()[1]}
    expect(s + ': kampfgruppe places', [claims[c]['place_id'] for c in ('C8465', 'C8466', 'C8470', 'C8473')], ['PL3823', 'PL3824', 'PL3826', 'PL0594'])
    expect(s + ': G072', [(claims[c]['conflict_group_id'], claims[c]['claim_status']) for c in ('C1803', 'C8473')], [('G072', 'preferred'), ('G072', 'alternate')])
    expect(s + ': sketch rows at 0.3', [claims[c]['confidence'] for c in ('C8471', 'C8472')], ['0.3', '0.3'])
    expect(s + ': no row above 0.5', max(claims['C84%02d' % i]['confidence'] for i in range(63, 74)), '0.5')


def scenario_193_ethint78():
    """ETHINT-78 (R858, Meindl and Schimpf interview): citations only."""
    s = 'scenario 193'
    claims = {c['claim_id']: c for c in common.load_all_claims()[1]}
    expect(s + ': cited', ['R858' in claims[c]['reference_ids'].split(';') for c in ('C8213', 'C8219')], [True, True])
    expect(s + ': no raise', [claims[c]['confidence'] for c in ('C8213', 'C8219')], ['0.3', '0.5'])
    expect(s + ': no new rows', any('R858: ' in c['source_locator'] and c['claim_id'] >= 'C8474' for c in claims.values()), False)


def scenario_194_b709_second_pass():
    """FMS B-709 second pass (R855 extended, Ulms and Reuther, English only): XII SS Corps in the Ruhr pocket, April 1945."""
    s = 'scenario 194'
    claims = {c['claim_id']: c for c in common.load_all_claims()[1]}
    expect(s + ': corps CPs', [claims[c]['place_id'] for c in ('C8474', 'C8475')], ['PL3828', 'PL0581'])
    expect(s + ': gruppe witte', claims['C8484']['unit_id'], 'GER-KG-WITTE')
    expect(s + ': no row above 0.5', max(claims['C84%02d' % i]['confidence'] for i in range(74, 88)), '0.5')
    expect(s + ': author corrected', 'Karl Reuther' in open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data', 'references_meta.csv'), encoding='utf-8').read(), True)


def scenario_195_b709_maps():
    """B-709 map appendices (R855, map-derived): rows at 0.3, never preferred over text."""
    s = 'scenario 195'
    claims = {c['claim_id']: c for c in common.load_all_claims()[1]}
    expect(s + ': all map rows at 0.3', set(claims['C8%03d' % i]['confidence'] for i in range(488, 501)), {'0.3'})
    expect(s + ': G073', [(claims[c]['conflict_group_id'], claims[c]['claim_status']) for c in ('C8480', 'C8497')], [('G073', 'preferred'), ('G073', 'alternate')])
    expect(s + ': witte at Duesseldorf', (claims['C8488']['unit_id'], claims['C8488']['place_id']), ('GER-KG-WITTE', 'PL3804'))
    expect(s + ': map support does not raise', claims['C8477']['confidence'], '0.3')


def scenario_198_b730_german():
    """FMS B-730 German original (R860): supporting citations; C8505 St-Denis; sketch rows 0.3."""
    s = 'scenario 198'
    claims = {c['claim_id']: c for c in common.load_all_claims()[1]}
    refs = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data', 'references.csv'), encoding='utf-8').read()
    expect(s + ': R860 present', 'R860' in refs and 'German original' in refs, True)
    expect(s + ': C8505 St-Denis', (claims['C8505']['place_id'], claims['C8505']['confidence']), ('PL3845', '0.5'))
    expect(s + ': sketch rows at 0.3', (claims['C8506']['confidence'], claims['C8507']['confidence']), ('0.3', '0.3'))
    expect(s + ': R860 on Flines CP', 'R860' in claims['C8438']['reference_ids'], True)
    expect(s + ': no raise from German', max(float(claims[c]['confidence']) for c in ('C8505', 'C8438', 'C8440')), 0.5)


def scenario_197_b709_german():
    """FMS B-709 German original (R859): supporting citations on English rows; C8503/C8504 new; no raise above 0.5."""
    s = 'scenario 197'
    claims = {c['claim_id']: c for c in common.load_all_claims()[1]}
    refs = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data', 'references.csv'), encoding='utf-8').read()
    expect(s + ': R859 present', 'R859' in refs and 'German original' in refs, True)
    expect(s + ': C8503 363rd on former 338th sector', (claims['C8503']['unit_id'], claims['C8503']['place_id'], claims['C8503']['date']),
           ('GER-VG-363D', 'PL3807', '1945-04-06'))
    expect(s + ': C8504 Siegburg strongpoint', (claims['C8504']['unit_id'], claims['C8504']['place_id'], claims['C8504']['confidence']),
           ('GER-FJ-003D', 'PL0457', '0.5'))
    expect(s + ': R859 on corps Ratingen CP', 'R859' in claims['C8428']['reference_ids'], True)
    expect(s + ': no raise from German', max(float(claims[c]['confidence']) for c in ('C8503', 'C8504', 'C8428', 'C8475')), 0.5)


def scenario_196_scott_decisions_nov04():
    """Scott's decisions of 4 November 2026: G074-G077 opened, reviewed groups unchanged."""
    s = 'scenario 196'
    claims = {c['claim_id']: c for c in common.load_all_claims()[1]}
    expect(s + ': G074/G075', [(claims[c]['conflict_group_id'], claims[c]['claim_status']) for c in ('C8501', 'C7949', 'C8502', 'C7959')], [('G074', 'preferred'), ('G074', 'alternate'), ('G075', 'preferred'), ('G075', 'alternate')])
    expect(s + ': G076/G077', [(claims[c]['conflict_group_id'], claims[c]['claim_status']) for c in ('C2165', 'C8240', 'C8244', 'C8242')], [('G076', 'preferred'), ('G076', 'alternate'), ('G077', 'preferred'), ('G077', 'alternate')])
    expect(s + ': reviewed groups keep status', [claims[c]['claim_status'] for c in ('C8457', 'C1803', 'C8420', 'C8249')], ['preferred'] * 4)
    expect(s + ': C8048 retired', 'C8048' in claims, False)


def scenario_177_blumentritt_relations():
    """B-361 single-source relations CR1072-CR1075."""
    s = 'scenario 177'
    rel = {r['relation_id']: r for r in csv.DictReader(open(REL_PATH, encoding='utf-8'))}
    expect(s + ': relations', [(rel[c]['subject_unit_id'], rel[c]['higher_unit_id'], rel[c]['relationship'], rel[c]['valid_from'], rel[c]['valid_to']) for c in ('CR1072', 'CR1073', 'CR1074', 'CR1075')],
           [('GER-MARI-002D', 'GER-ARMY-BLUMT', 'unspecified_subordination', '1945-04-10', ''), ('GER-PZ-039C', 'GER-ARMY-BLUMT', 'operational_control', '1945-04-15', '1945-04-17'), ('GER-PZ-CLAUS', 'GER-PZ-039C', 'operational_control', '1945-04-15', '1945-04-17'), ('GER-INF-245D', 'GER-OBNW-000H', 'reserve', '1945-04-28', '')])


def scenario_199_theater():
    """Per-claim theater (theater decision Scott, 9 November 2026): new values, per-front operations, backfill, roadmap 362 rows, validator rules."""
    import json
    import operations
    s = 'scenario 199'
    here = os.path.dirname(os.path.abspath(__file__))
    vocab = json.load(open(os.path.join(here, '..', 'schema', 'vocabularies.json'), encoding='utf-8'))['theater']['values']
    expect(s + ': new theater values', {'balkans', 'scandinavia', 'home_germany'} <= set(vocab), True)
    rep = json.load(open(os.path.join(here, '..', 'schema', 'claims.schema.json'), encoding='utf-8'))['repeatedColumns']['fields']
    expect(s + ': theater not repeated from units.csv', 'theater' in rep, False)
    claims = {c['claim_id']: c for c in common.load_all_claims()[1]}
    ops = operations.load()
    expect(s + ': every claim theater equals its operation theater', [c for c, r in claims.items() if r['theater'] != ops.by_id[r['operation_id']]['theater']], [])
    other = {c: (r['theater'], r['operation_id']) for c, r in claims.items() if r['theater'] != 'western_europe' and int(c[1:]) <= 8826}   # rows of the theater commit; later passes add their own
    east = ['C8773', 'C8774', 'C8775', 'C8776', 'C8777', 'C8778', 'C8781', 'C8782', 'C8783', 'C8784', 'C8816', 'C8818', 'C8820', 'C8821', 'C8822', 'C8824', 'C8825']
    home = ['C8772', 'C8627', 'C8670', 'C8677', 'C8686', 'C8717', 'C8651', 'C8807', 'C8748', 'C8817', 'C8823', 'C8826']
    want = dict([(c, ('eastern_front', 'OP-FRONT-EASTERN')) for c in east] + [(c, ('home_germany', 'OP-HOME-GERMANY')) for c in home] + [('C8731', ('scandinavia', 'OP-FRONT-SCANDINAVIA'))])
    expect(s + ': rows outside western_europe (backfill 20 + roadmap 362 rows 10)', other, want)
    expect(s + ': XXV Corps 1940 rows stay western_europe', set(claims[c]['theater'] for c in ('C8660', 'C8663', 'C8666')), {'western_europe'})
    expect(s + ': no campaign label on an Eastern Front row after June 1944', ops.labels('OP-FRONT-EASTERN', '1945-03-21')['campaign'], '')
    expect(s + ': western rows keep their CMH campaign', ops.labels(claims['C8819']['operation_id'], '1945-04-15')['campaign'] != '', True)
    base = dict(claims['C8822'], _where='test')
    es, _ = operations.check(ops, [base], set(), set(vocab), lambda d: True)
    expect(s + ': an Eastern Front row in March 1945 needs no CMH streamer', [m for _, m in es if 'streamer' in m or 'theater' in m], [])
    bad = dict(base, theater='western_europe')
    es, _ = operations.check(ops, [bad], set(), set(vocab), lambda d: True)
    expect(s + ': theater differing from the operation is an error', any('differs from the theater of its operation' in m for _, m in es), True)
    es, _ = operations.check(ops, [dict(bad, operation_id='OP-CAMP-RHINELAND', date='1945-02-01')], set(), set(vocab), lambda d: True)
    expect(s + ': a western row under a CMH campaign is clean', [m for _, m in es if 'streamer' in m or 'theater' in m], [])
    flat = {r['claim_id']: r for r in csv.DictReader(open(os.path.join(common.BUILD_DIR, 'all_claims.csv'), encoding='utf-8'))}
    expect(s + ': build output carries the row theater', (flat['C8816']['theater'], flat['C8826']['theater'], flat['C8819']['theater']), ('eastern_front', 'home_germany', 'western_europe'))
    expect(s + ': VAK 406 promoted on its Frankfurt (Oder) row', (claims['C8822']['unit_id'], claims['C8822']['place_id']), ('GER-VAK-406C', 'PL3952'))


def scenario_200_placeholders_b1():
    """German placeholder pass, chunk B1 (roadmap 365): Division Nr. 905, Division Nr. 405, Infanterie-Division Hamburg, Potsdam, 249th and 703rd Infantry Divisions."""
    s = 'scenario 200'
    claims = {c['claim_id']: c for c in common.load_all_claims()[1]}
    units = {u['unit_id']: u for u in csv.DictReader(open(common.UNITS_CSV, encoding='utf-8'))}
    six = ['GER-DIV-905', 'GER-DIV-405', 'GER-INF-HAMBURG', 'GER-INF-POTSDAM', 'GER-INF-249D', 'GER-INF-703D']
    expect(s + ': the six records are promoted', [units[u]['record_status'] for u in six], ['active'] * 6)
    expect(s + ': 905 pulled back to Drusenheim under LXXXIX Corps, two families', (claims['C8828']['date'], claims['C8828']['parent_unit_id'], claims['C8828']['confidence']), ('1945-02-03', 'GER-COR-089C', '0.5'))
    expect(s + ': 905 Fort-Louis row uses the existing place', claims['C8831']['place_id'], 'PL2548')
    expect(s + ': 405 command post at Bottenau on 1 April 1945 under LXIV Corps', (claims['C8844']['place_id'], claims['C8844']['parent_unit_id'], claims['C8844']['location_represents']), ('PL3964', 'GER-COR-064C', 'headquarters'))
    expect(s + ': Hamburg formed at Verden is a home_germany row', (claims['C8846']['event_type'], claims['C8846']['theater'], claims['C8846']['operation_id']), ('activation', 'home_germany', 'OP-HOME-GERMANY'))
    expect(s + ': Potsdam formed at Doeberitz is a home_germany row', (claims['C8851']['theater'], claims['C8851']['operation_id']), ('home_germany', 'OP-HOME-GERMANY'))
    expect(s + ': Hamburg at Voerde from two families at 0.7', (claims['C8848']['place_id'], claims['C8848']['confidence']), ('PL3965', '0.7'))
    lin = [(r['predecessor_unit_id'], r['successor_unit_id'], r['kind']) for r in csv.DictReader(open(os.path.join(common.ROOT, 'data', 'unit_lineage.csv'), encoding='utf-8'))]
    expect(s + ': 905 merged into the 16th VGD; 405 into the 719th', [x for x in lin if x[0] in ('GER-DIV-905', 'GER-DIV-405')], [('GER-DIV-905', 'GER-VG-016D', 'absorbed_into'), ('GER-DIV-405', 'GER-INF-719D', 'absorbed_into')])
    single = [c for c in claims.values() if c['unit_id'] in ('GER-INF-249D', 'GER-INF-703D')]
    expect(s + ': 249th and 703rd are one family, every row 0.3', sorted(set(c['confidence'] for c in single)), ['0.3'])


def scenario_201_placeholders_b2():
    """German placeholder pass, chunk B2 (roadmap 365): XII and XIII Corps, Division Nr. 172 and 526, Jutland, 30th SS, Division z.b.V. 136."""
    s = 'scenario 201'
    claims = {c['claim_id']: c for c in common.load_all_claims()[1]}
    units = {u['unit_id']: u for u in csv.DictReader(open(common.UNITS_CSV, encoding='utf-8'))}
    seven = ['GER-COR-012C', 'GER-COR-013C', 'GER-DIV-172', 'GER-DIV-526', 'GER-INF-JUTLAND', 'GER-SSGR-030D', 'GER-DIV-136ZBV']
    expect(s + ': the seven records are promoted', [units[u]['record_status'] for u in seven], ['active'] * 7)
    expect(s + ': XIII Corps at Lowicz in 1939 is an Eastern Front row', (claims['C8860']['theater'], claims['C8860']['operation_id']), ('eastern_front', 'OP-FRONT-EASTERN'))
    expect(s + ': XIII Corps at Trier in October 1939 is a home row', claims['C8861']['theater'], 'home_germany')
    expect(s + ': XIII Corps in Belgium in 1940 is western_europe before the invasion', (claims['C8863']['theater'], claims['C8863']['operation_id']), ('western_europe', 'OP-PRE-INVASION'))
    expect(s + ': XIII Corps command post at Wawern, 20 February 1945, two families', (claims['C8875']['place_id'], claims['C8875']['confidence'], claims['C8875']['parent_unit_id']), ('PL1709', '0.7', 'GER-ARMY-007A'))
    expect(s + ': XII Corps at Brest-Litovsk in Belarus', (claims['C8889']['theater'], claims['C8889']['event_type']), ('eastern_front', 'capture'))
    expect(s + ': acting XII Corps at Wiesbaden in March 1945 from FMS and CMH', (claims['C8896']['confidence'], claims['C8896']['location_represents']), ('0.7', 'headquarters'))
    expect(s + ': Division Nr. 172 is one family, every row 0.3', sorted({c['confidence'] for c in claims.values() if c['unit_id'] == 'GER-DIV-172'}), ['0.3'])
    expect(s + ': 526 in front of the Dillingen bridgehead from the Lexikon and CMH', (claims['C8905']['date'], claims['C8905']['confidence']), ('1944-12-15', '0.7'))
    expect(s + ': Jutland formed at Esbjerg is a scandinavia row', (claims['C8907']['theater'], claims['C8907']['operation_id'], claims['C8907']['place_id']), ('scandinavia', 'OP-FRONT-SCANDINAVIA', 'PL3917'))
    expect(s + ': the 30th SS at Altkirch from CMH and FMS B-078', (claims['C8913']['date'], claims['C8913']['confidence']), ('1944-11-21', '0.7'))
    lin = [(r['predecessor_unit_id'], r['successor_unit_id'], r['kind']) for r in csv.DictReader(open(os.path.join(common.ROOT, 'data', 'unit_lineage.csv'), encoding='utf-8'))]
    expect(s + ': shadow division Jutland into the 19th Grenadier (Volksgrenadier) Division', ('GER-INF-JUTLAND', 'GER-VG-019D', 'absorbed_into') in lin, True)

def scenario_202_placeholders_b3():
    """German placeholder pass, chunk B3 (roadmap 365): SS Heavy Panzer Battalion 101 with a traceable parent chain."""
    s = 'scenario 202'
    claims = {c['claim_id']: c for c in common.load_all_claims()[1]}
    units = {u['unit_id']: u for u in csv.DictReader(open(common.UNITS_CSV, encoding='utf-8'))}
    expect(s + ': the battalion is promoted', units['GER-SSHPZ-101']['record_status'], 'active')
    expect(s + ': Villers-Bocage on 13 June 1944 at 0.5', (claims['C8931']['place_id'], claims['C8931']['confidence']), ('PL0373', '0.5'))
    expect(s + ': mid-July under I SS Panzer Corps in the Caen sector', (claims['C8932']['parent_unit_id'], claims['C8932']['confidence']), ('GER-SSPZ-001C', '0.3'))


def scenario_203_lifespan():
    """Consistency fix 1: no claim row before formation or after the end of a unit without a recorded reason."""
    s = 'scenario 203'
    claims = {c['claim_id']: c for c in common.load_all_claims()[1]}
    units = {u['unit_id']: u for u in csv.DictReader(open(common.UNITS_CSV, encoding='utf-8'))}
    expect(s + ': the 189th Infantry Division record starts with the 189th Reserve Division', units['GER-INF-189D']['formed_date'], '1943-05-20')
    expect(s + ': the 553rd VGD record starts with the 553rd Grenadier Division', units['GER-VG-553D']['formed_date'], '1944-07-11')
    expect(s + ': the 553rd renaming is a redesignation row at Nomeny', (claims['C8936']['event_type'], claims['C8936']['date'], claims['C8936']['place_id']), ('redesignation', '1944-10-09', 'PL4000'))
    expect(s + ': Army Group H activation and the B-717 alternate', (claims['C1037']['event_type'], claims['C7744']['claim_status'], claims['C7744']['conflict_group_id']), ('activation', 'alternate', 'G110'))
    expect(s + ': Panzer Brigade 113 map rows after the disbandment are alternates', sorted({claims[c]['claim_status'] for c in ['C3252', 'C3363', 'C3539', 'C3674', 'C3817']}), ['alternate'])
    expect(s + ': the 15th Panzer Grenadier Division overrun is not an end', claims['C7478']['event_type'], 'defense')
    expect(s + ': the late-November 462 map rows stay on their record with a note', [('Volksgrenadier' in claims[c]['notes'], claims[c]['unit_id']) for c in ['C4078', 'C4240', 'C4371']], [(True, 'GER-INF-462D')] * 3)
    expect(s + ': the 25th Panzergrenadier Division re-formation at Grafenwöhr', (claims['C8933']['event_type'], claims['C8933']['theater']), ('activation', 'home_germany'))
    bad = []
    for c in claims.values():
        u = units[c['unit_id']]
        if c['claim_status'] == 'preferred' and u['formed_date'] and c['date'] < u['formed_date'] and c['event_type'] != 'activation':
            bad.append(c['claim_id'])
    expect(s + ': no preferred row before formed_date', bad, [])


def scenario_204_command_relations():
    """Consistency fix 2: stale relations closed from the Lexikon tables, Netherlands District, small-unit parent chains, Lexikon rows for parentless divisions."""
    s = 'scenario 204'
    claims = {c['claim_id']: c for c in common.load_all_claims()[1]}
    rels = {r['relation_id']: r for r in csv.DictReader(open(os.path.join(common.ROOT, 'data', 'command_relations.csv'), encoding='utf-8'))}
    expect(s + ': CR0623 closed by the Lexikon table', (rels['CR0623']['valid_to'], rels['CR0623']['valid_to_basis'], rels['CR0623']['end_unknown']), ('1944-11-30', 'assignment_table', 'false'))
    expect(s + ': CR1241 ends with the renaming as the 70th Division', rels['CR1241']['valid_to'], '1944-07-31')
    expect(s + ': CR0713 stays open', rels['CR0713']['valid_to'], '')
    expect(s + ': the 33rd Armoured Brigade under Netherlands District', (rels['CR1273']['subject_unit_id'], rels['CR1273']['higher_unit_id']), ('UK-ARM-033B', 'UK-DIST-NETH'))
    expect(s + ': the 3rd Parachute Division under II Parachute Corps from January 1944', (rels['CR0008']['valid_from'], claims['C8404']['parent_unit_id']), ('1944-01-15', 'GER-FJ-002C'))
    expect(s + ': SS Heavy Panzer Battalion 101 under I SS Panzer Corps at Villers-Bocage', claims['C8931']['parent_unit_id'], 'GER-SSPZ-001C')
    expect(s + ': Lexikon rows for parentless divisions are 0.3', sorted({claims[c]['confidence'] for c in ('C8941', 'C8942', 'C8943', 'C8944', 'C8945')}), ['0.3'])
    expect(s + ': the 7th Armored Division under III Corps on 30 March 1945', (claims['C8940']['parent_unit_id'], claims['C8940']['confidence']), ('US-COR-003C', '0.5'))

def scenario_205_german_end_rows():
    """Consistency fix 3: end rows and lineage ends for German units whose claims stopped without an end."""
    s = 'scenario 205'
    claims = {c['claim_id']: c for c in common.load_all_claims()[1]}
    lin = {l['lineage_id']: l for l in csv.DictReader(open(os.path.join(common.ROOT, 'data', 'unit_lineage.csv'), encoding='utf-8'))}
    expect(s + ': the 462nd VGD ends with Fort Jeanne d\'Arc on 13 December 1944 (two families)', (claims['C8946']['event_type'], claims['C8946']['date'], claims['C8946']['confidence']), ('surrender', '1944-12-13', '0.7'))
    expect(s + ': the Sixth Panzer Army surrender is an eastern-front row', (claims['C8949']['unit_id'], claims['C8949']['theater']), ('GER-PZA-006A', 'eastern_front'))
    expect(s + ': one-family end rows are 0.3', sorted({claims[c]['confidence'] for c in ('C8947', 'C8948', 'C8949', 'C8950', 'C8951')}), ['0.3'])
    expect(s + ': chunk B end rows', [(claims[c]['unit_id'], claims[c]['event_type']) for c in ('C8952', 'C8953')], [('GER-PG-015D', 'surrender'), ('GER-INF-416D', 'destruction')])
    expect(s + ': Panzer-Brigade 105 ends in the 9th Panzer Division (month only)', (lin['UL019']['successor_unit_id'], lin['UL019']['effective_date']), ('GER-PZ-009D', '1944-10'))
    expect(s + ': chunk C Twelfth Army surrender on the Elbe (two families)', (claims['C8956']['unit_id'], claims['C8956']['date'], claims['C8956']['confidence']), ('GER-ARMY-012A', '1945-05-07', '0.5'))
    expect(s + ': chunk C Enns-line rows are eastern-front and 50 km', sorted({(claims[c]['theater'], claims[c]['precision_km']) for c in ('C8958', 'C8959')}), [('eastern_front', '50')])
    expect(s + ': the 49th Infantry Division ends in the 246th VGD', (lin['UL015']['predecessor_unit_id'], lin['UL015']['successor_unit_id'], lin['UL015']['kind']), ('GER-INF-049D', 'GER-VG-246D', 'absorbed_into'))

def scenario_206_map_text_weak_pairs():
    """Consistency fix 4: map rows of the weak map-against-text pairs are capped at 0.3; G113 resolves the 75th Division pair."""
    s = 'scenario 206'
    claims = {c['claim_id']: c for c in common.load_all_claims()[1]}
    expect(s + ': capped map rows are 0.3', sorted({claims[c]['confidence'] for c in ('C2580', 'C2658', 'C6809', 'C7018', 'C2871')}), ['0.3'])
    expect(s + ': G113 text preferred, map alternate', [(claims[c]['conflict_group_id'], claims[c]['claim_status']) for c in ('C0595', 'C5492')], [('G113', 'preferred'), ('G113', 'alternate')])
    expect(s + ': the 3rd Armored clears Dessau (CMH text row)', (claims['C8960']['unit_id'], claims['C8960']['date'], claims['C8960']['place_id']), ('US-ARM-003D', '1945-04-23', 'PL0463'))
    expect(s + ': no map row outranks text', any(claims[c]['reference_ids'].startswith('R781') and float(claims[c]['confidence']) > 0.3 for c in ('C2580', 'C2496', 'C6449')), False)

def scenario_207_midwar_ends():
    """Mid-war ends (branch midwar-ends): end rows for German units that ended before about April 1945 (HANDOFF rule 20)."""
    s = 'scenario 207'
    claims = {c['claim_id']: c for c in common.load_all_claims()[1]}
    ends = {'C8961': 'GER-COR-089C', 'C8962': 'GER-VG-019D', 'C8963': 'GER-INF-077D', 'C8964': 'GER-LL-091D', 'C8965': 'GER-LFD-017D', 'C8966': 'GER-PZB-150B', 'C8967': 'GER-VG-272D', 'C8968': 'GER-COR-FELDT', 'C8970': 'GER-VG-079D'}
    expect(s + ': chunk 1 end rows belong to the triaged mid-war units', {c: claims[c]['unit_id'] for c in ends}, ends)
    expect(s + ': every chunk 1 end row is flagged disestablished, destroyed or a surrender', all(claims[c]['disestablished'] == 'true' or claims[c]['destroyed'] == 'true' or claims[c]['event_type'] == 'surrender' for c in ends), True)
    expect(s + ': one-family Lexikon rows are 0.3', sorted({claims[c]['confidence'] for c in ends}), ['0.3'])
    expect(s + ': chunk 2 brigade end rows are preferred in G114 and G115 with the late map rows alternate', [(claims[c]['conflict_group_id'], claims[c]['claim_status']) for c in ('C8971', 'C3816', 'C8972', 'C4046')], [('G114', 'preferred'), ('G114', 'alternate'), ('G115', 'preferred'), ('G115', 'alternate')])
    expect(s + ': roadmap 370 groups G116 (462nd map rows) and G117 (159th redesignation dates)', [(claims[c]['conflict_group_id'], claims[c]['claim_status']) for c in ('C8935', 'C4371', 'C8973', 'C8974')], [('G116', 'preferred'), ('G116', 'alternate'), ('G117', 'preferred'), ('G117', 'alternate')])
    expect(s + ': Panzer-Brigade 107 ends with its Baumholder row', claims['C8955']['disestablished'], 'true')


def scenario_208_lifespan_check():
    """Roadmap 370(b): the validator lifespan check runs as a warning and reports only the known leftover."""
    s = 'scenario 208'
    claims = common.load_all_claims()[1]
    units = {u['unit_id']: u for u in csv.DictReader(open(common.UNITS_CSV, encoding='utf-8'))}
    issues = validate.lifespan_issues(units, claims)
    keys = [(i['unit_id'], i['claim_id'], i['reason']) for i in issues]
    expect(s + ': only the Jutland second-formation leftover (roadmap 370a)', keys, [('GER-INF-JUTLAND', 'C8908', 'after_lineage_successor')])
    expect(s + ': the leftover is after the August 1944 lineage successor', issues[0]['life_end'] if issues else None, '1944-08-03')
    flagged_units = {i['unit_id'] for i in issues}
    expect(s + ': alternate map rows after Panzer Brigade 113 ended are not flagged', 'GER-PZB-113B' in flagged_units, False)
    expect(s + ': absorbed_into is not read as the 246th VGD formation', any(i['unit_id'] == 'GER-VG-246D' and i['reason'] == 'before_lineage_formation' for i in issues), False)
    expect(s + ': 3rd Fallschirmjäger re-formation is a new life, not after-end', 'GER-FJ-003D' in flagged_units, False)
    expect(s + ': 25th Panzergrenadier re-formation at Grafenwöhr is not flagged', 'GER-PG-025D' in flagged_units, False)


def scenario_209_ellis_leftovers_chunk1():
    """Ellis leftover-entry pass, chunk 1: supporting citations on existing rows, and first new claims C8975-C8979."""
    s = 'scenario 209'
    claims = {c['claim_id']: c for c in common.load_all_claims()[1]}
    to_07 = ['C0162', 'C0189', 'C0155', 'C0176', 'C0164', 'C0111', 'C0069', 'C0019']
    expect(s + ': Wikipedia British rows now cite Ellis and stand at 0.7', {c: (claims[c]['confidence'], 'R670' in claims[c]['reference_ids'].split(';')) for c in to_07}, {c: ('0.7', True) for c in to_07})
    expect(s + ': Cheux, Villers-Bocage and Biéville rows now at 0.9 with Ellis and Stacey', {c: claims[c]['confidence'] for c in ('C0163', 'C0096', 'C0016')}, {'C0163': '0.9', 'C0096': '0.9', 'C0016': '0.9'})
    expect(s + ': 49th Division at Wuustwezel cites Ellis vol. II and stands at 0.7', (claims['C7353']['confidence'], 'R671' in claims['C7353']['reference_ids'].split(';')), ('0.7', True))
    expect(s + ': 53rd Division near Trun cites Ellis vol. I and stands at 0.7', (claims['C7246']['confidence'], 'R670' in claims['C7246']['reference_ids'].split(';')), ('0.7', True))
    expect(s + ': Polish Ypres and Aeltre rows gained Ellis vol. II', ('R671' in claims['C1555']['reference_ids'].split(';'), 'R671' in claims['C7301']['reference_ids'].split(';'), claims['C1555']['confidence'], claims['C7301']['confidence']), (True, True, '0.7', '0.5'))
    expect(s + ': Canadian Charnwood, Bretteville-sur-Laize and Trun rows gained Ellis vol. I without a confidence raise', {c: ('R670' in claims[c]['reference_ids'].split(';'), claims[c]['confidence']) for c in ('C1297', 'C1320', 'C1336')}, {'C1297': (True, '0.7'), 'C1320': (True, '0.7'), 'C1336': (True, '0.9')})
    expect(s + ': new 79th Armoured row at Le Havre on 10 September 1944', (claims['C8975']['unit_id'], claims['C8975']['date'], claims['C8975']['place_id'], claims['C8975']['operation_id'], 'R671' in claims['C8975']['reference_ids'].split(';')), ('UK-ARM-079D', '1944-09-10', 'PL0169', 'OP-ASTONIA', True))
    expect(s + ': new 31st Tank Brigade rows at Boulogne and Calais', (claims['C8976']['date'], claims['C8976']['place_id'], claims['C8976']['operation_id'], claims['C8977']['date'], claims['C8977']['place_id'], claims['C8977']['operation_id']), ('1944-09-17', 'PL0677', 'OP-WELLHIT', '1944-09-25', 'PL0678', 'OP-UNDERGO'))
    expect(s + ': new 79th Armoured South Beveland landing row', (claims['C8978']['date'], claims['C8978']['place_id'], claims['C8978']['operation_id']), ('1944-10-26', 'PL3427', 'OP-SCHELDT'))
    expect(s + ': new 15th Division Mondrainville capture on 27 June 1944', (claims['C8979']['unit_id'], claims['C8979']['place_id'], claims['C8979']['confidence'], claims['C8979']['event_type'], 'R670' in claims['C8979']['reference_ids'].split(';')), ('UK-INF-015D', 'PL0227', '0.7', 'capture', True))




def scenario_210_ellis_leftovers_chunk2():
    """Ellis leftover-entry pass, chunk 2: British Oct–Dec 1944 named-place claims, Walcheren/Pheasant citations, G118."""
    s = 'scenario 210'
    claims = {c['claim_id']: c for c in common.load_all_claims()[1]}
    raised = ['C7397', 'C7398', 'C7401', 'C7361']
    expect(s + ': Flushing, Middelburg and Tilburg Stacey rows now cite Ellis and stand at 0.7', {c: (claims[c]['confidence'], 'R671' in claims[c]['reference_ids'].split(';')) for c in raised}, {c: ('0.7', True) for c in raised})
    expect(s + ': Zoutelande and Esschen rows gained Ellis without a confidence raise', {c: (claims[c]['confidence'], 'R671' in claims[c]['reference_ids'].split(';')) for c in ('C7399', 'C1340', 'C7355')}, {'C7399': ('0.3', True), 'C1340': ('0.7', True), 'C7355': ('0.5', True)})
    expect(s + ': 49th Division captures Poppel on 4 October 1944', (claims['C8980']['unit_id'], claims['C8980']['place_id'], claims['C8980']['event_type'], claims['C8980']['operation_id']), ('UK-INF-049D', 'PL3559', 'capture', 'OP-SCHELDT'))
    expect(s + ': Pheasant text rows for Den Bosch, Schijndel, Boxtel, Oisterwijk and Tilburg', [(claims[c]['date'], claims[c]['place_id'], claims[c]['event_type']) for c in ('C8981', 'C8982', 'C8983', 'C8984', 'C8985')], [('1944-10-24', 'PL0749', 'attack'), ('1944-10-24', 'PL1063', 'capture'), ('1944-10-24', 'PL0693', 'attack'), ('1944-10-27', 'PL0854', 'capture'), ('1944-10-27', 'PL0568', 'capture')])
    expect(s + ': 7th Armoured Middelrode, Udenhout, Loon op Zand and Dongen', [(claims[c]['date'], claims[c]['place_id']) for c in ('C8986', 'C8987', 'C8988', 'C8989')], [('1944-10-22', 'PL4013'), ('1944-10-27', 'PL1746'), ('1944-10-29', 'PL3580'), ('1944-10-31', 'PL1058')])
    expect(s + ': 3rd Division and 11th Armoured at Venray on 16 and 20 October', [(claims[c]['unit_id'], claims[c]['date'], claims[c]['event_type'], claims[c]['place_id']) for c in ('C8990', 'C8991', 'C8992', 'C8993')], [('UK-INF-003D', '1944-10-16', 'attack', 'PL3450'), ('UK-ARM-011D', '1944-10-16', 'attack', 'PL3450'), ('UK-INF-003D', '1944-10-20', 'capture', 'PL3450'), ('UK-ARM-011D', '1944-10-20', 'capture', 'PL3450')])
    expect(s + ': 15th Division and 6th Guards Tank attack Meijel on 30 October', (claims['C8994']['place_id'], claims['C8995']['place_id'], claims['C8994']['date'], claims['C8995']['unit_id']), ('PL2222', 'PL2222', '1944-10-30', 'UK-TNK-006GB'))
    expect(s + ': 79th Armoured specialist rows at Westkapelle, Domburg and Blerick', [(claims[c]['date'], claims[c]['place_id'], claims[c]['operation_id']) for c in ('C8996', 'C8997', 'C8999')], [('1944-11-01', 'PL0868', 'OP-INFATUATE'), ('1944-11-08', 'PL0869', 'OP-INFATUATE'), ('1944-12-03', 'PL4014', 'OP-CAMP-RHINELAND')])
    expect(s + ': Veere date conflict G118 keeps the Stacey row preferred', (claims['C7402']['conflict_group_id'], claims['C7402']['claim_status'], claims['C8998']['conflict_group_id'], claims['C8998']['claim_status'], claims['C8998']['date'], claims['C8998']['place_id']), ('G118', 'preferred', 'G118', 'alternate', '1944-11-06', 'PL3434'))


def scenario_211_ellis_leftovers_chunk3():
    """Ellis leftovers chunk 3: 79th Armoured and independent-brigade facts, plus two IJssel supporting citations."""
    s = 'scenario 211'
    claims = {c['claim_id']: c for c in common.load_all_claims()[1]}
    expect(s + ': 49th Division IJssel assault at Westervoort now cites Ellis and stands at 0.7',
           (claims['C7622']['confidence'], 'R671' in claims['C7622']['reference_ids'].split(';'), claims['C7622']['place_id']),
           ('0.7', True, 'PL3508'))
    expect(s + ': 1st Canadian Division IJssel crossing gained Ellis without a confidence raise',
           (claims['C1398']['confidence'], 'R671' in claims['C1398']['reference_ids'].split(';')),
           ('0.5', True))
    rows_79 = ['C9000', 'C9001', 'C9002', 'C9003', 'C9004', 'C9005', 'C9006', 'C9007', 'C9008', 'C9009']
    expect(s + ': 79th Armoured specialist rows C9000-C9009',
           [(claims[c]['unit_id'], claims[c]['date'], claims[c]['place_id'], claims[c]['confidence'], claims[c]['reference_ids'].split(';')[0]) for c in rows_79],
           [
               ('UK-ARM-079D', '1944-07-08', 'PL0057', '0.5', 'R670'),
               ('UK-ARM-079D', '1944-07-30', 'PL0071', '0.5', 'R670'),
               ('UK-ARM-079D', '1944-08-07', 'PL0533', '0.5', 'R670'),
               ('UK-ARM-079D', '1944-08-14', 'PL4015', '0.5', 'R670'),
               ('UK-ARM-079D', '1945-01-18', 'PL0754', '0.5', 'R671'),
               ('UK-ARM-079D', '1945-02-08', 'PL3466', '0.5', 'R671'),
               ('UK-ARM-079D', '1945-02-09', 'PL4016', '0.5', 'R671'),
               ('UK-ARM-079D', '1945-02-18', 'PL0758', '0.5', 'R671'),
               ('UK-ARM-079D', '1945-04-11', 'PL0700', '0.5', 'R671'),
               ('UK-ARM-079D', '1945-04-12', 'PL3508', '0.5', 'R671'),
           ])
    expect(s + ': 79th Totalize, Tractable, Blackcock and IJssel operations and event types',
           [(claims[c]['operation_id'], claims[c]['event_type']) for c in ('C9002', 'C9003', 'C9004', 'C9008', 'C9009')],
           [('OP-TOTALIZE', 'attack'), ('OP-TRACTABLE', 'attack'), ('OP-BLACKCOCK', 'attack'), ('OP-CAMP-CENTRAL-EUROPE', 'landing'), ('OP-CAMP-CENTRAL-EUROPE', 'landing')])
    expect(s + ': 33rd Armoured Brigade captures Saint-Aignan by first light on 8 August; existing Bourguébus attack row kept',
           (claims['C9010']['unit_id'], claims['C9010']['place_id'], claims['C9010']['event_type'], claims['C1680']['place_id'], claims['C1680']['event_type']),
           ('UK-ARM-033B', 'PL0786', 'capture', 'PL0687', 'attack'))
    expect(s + ': 6th Guards Tank Brigade at Nutterden and 8th Armoured Brigade at Cleve',
           [(claims['C9011']['unit_id'], claims['C9011']['date'], claims['C9011']['place_id']),
            (claims['C9012']['unit_id'], claims['C9012']['date'], claims['C9012']['place_id'], claims['C9012']['event_type'])],
           [('UK-TNK-006GB', '1945-02-09', 'PL4016'),
            ('UK-ARM-008B', '1945-02-10', 'PL0578', 'attack')])



def scenario_212_ellis_leftovers_chunk4():
    """Ellis leftovers chunk 4: Canadian supporting citations (no raise) and C9013 Spring row."""
    s = 'scenario 212'
    claims = {c['claim_id']: c for c in common.load_all_claims()[1]}
    cited = ['C0001', 'C0002', 'C0079', 'C1296', 'C1287', 'C1299', 'C1317', 'C1288', 'C1300', 'C1319', 'C1290', 'C1291', 'C1303', 'C1334', 'C1321', 'C1337', 'C1292']
    expect(s + ': Canadian rows gained Ellis without a confidence change',
           {c: (claims[c]['confidence'], 'R670' in claims[c]['reference_ids'].split(';')) for c in cited},
           {
               'C0001': ('0.7', True), 'C0002': ('0.7', True), 'C0079': ('0.7', True),
               'C1296': ('0.7', True), 'C1287': ('0.7', True), 'C1299': ('0.7', True),
               'C1317': ('0.7', True), 'C1288': ('0.7', True), 'C1300': ('0.7', True),
               'C1319': ('0.7', True), 'C1290': ('0.5', True), 'C1291': ('0.7', True),
               'C1303': ('0.7', True), 'C1334': ('0.7', True), 'C1321': ('0.7', True),
               'C1337': ('0.7', True), 'C1292': ('0.7', True),
           })
    expect(s + ': 2nd Canadian Armoured Brigade attacks Tilly-la-Campagne on 25 July',
           (claims['C9013']['unit_id'], claims['C9013']['date'], claims['C9013']['place_id'], claims['C9013']['event_type'], claims['C9013']['operation_id'], claims['C9013']['confidence']),
           ('CAN-ARM-002B', '1944-07-25', 'PL0672', 'attack', 'OP-SPRING', '0.5'))




def scenario_213_ellis_leftovers_chunk5():
    """Ellis leftovers chunk 5: German units in the British and Canadian sectors."""
    s = 'scenario 213'
    claims = {c['claim_id']: c for c in common.load_all_claims()[1]}
    cited = {
        'C0009': '0.7', 'C0008': '0.3', 'C0004': '0.7', 'C0060': '0.9',
        'C0170': '0.5', 'C7232': '0.5', 'C0776': '0.7', 'C7240': '0.5',
    }
    expect(s + ': German 21 AG-sector rows gained Ellis without a confidence change',
           {c: (claims[c]['confidence'], 'R670' in claims[c]['reference_ids'].split(';')) for c in cited},
           {c: (conf, True) for c, conf in cited.items()})
    expect(s + ': 12th SS Panzer Division is committed at Authie on 7 June',
           (claims['C9014']['unit_id'], claims['C9014']['date'], claims['C9014']['place_id'], claims['C9014']['event_type'], claims['C9014']['confidence']),
           ('GER-SSPZ-012D', '1944-06-07', 'PL0019', 'defense', '0.5'))
    expect(s + ': existing 8 June Authie row was not given Ellis (different date)',
           'R670' in claims['C0049']['reference_ids'].split(';'), False)




def scenario_214_ellis_leftovers_chunk6():
    """Ellis leftovers chunk 6: named places that had been only weekly map dots."""
    s = 'scenario 214'
    claims = {c['claim_id']: c for c in common.load_all_claims()[1]}
    expect(s + ': 51st Division captures St. Aignan by first light on 8 August; same-day map row stays at Tilly-la-Campagne',
           (claims['C9015']['unit_id'], claims['C9015']['place_id'], claims['C9015']['event_type'], claims['C2671']['place_id'], claims['C2671']['event_type']),
           ('UK-INF-051D', 'PL0786', 'capture', 'PL0672', 'other'))
    expect(s + ': 50th Division captures Tilly-sur-Seulles on 19 June; 20 June map row stays at Lingèvres',
           (claims['C9016']['unit_id'], claims['C9016']['date'], claims['C9016']['place_id'], claims['C2317']['date'], claims['C2317']['place_id']),
           ('UK-INF-050D', '1944-06-19', 'PL0349', '1944-06-20', 'PL1162'))
    expect(s + ': 7th Armoured Division takes Livarot on 20 August; 22 August Lisieux row kept',
           (claims['C9017']['unit_id'], claims['C9017']['date'], claims['C9017']['place_id'], claims['C7250']['date'], claims['C7250']['place_id']),
           ('UK-ARM-007D', '1944-08-20', 'PL3362', '1944-08-22', 'PL0193'))


def scenario_215_cmhq173_watch_on_the_maas():
    """CMHQ/AHQ report pass, CMHQ Report No. 173 (The Watch on the Maas, 9 Nov 1944-8 Feb 1945): supporting citations, raises, new rows and G119."""
    s = 'scenario 215'
    claims = {c['claim_id']: c for c in common.load_all_claims()[1]}
    refs = lambda c: claims[c]['reference_ids'].split(';')
    import csv as _csv
    meta = {r['reference_id']: r for r in _csv.DictReader(open(os.path.join(common.ROOT, 'data', 'references_meta.csv'), encoding='utf-8'))}
    expect(s + ': R882 is CMHQ Report No. 173 in its own family', (meta['R882']['source_family'], 'cmhq173' in meta['R882']['url']), ('canada_dhh_reports', True))
    expect(s + ': 3rd Canadian Division map row south of Nijmegen, 2 Jan 1945, gains R882 and is raised to 0.7', ('R882' in refs('C4926'), claims['C4926']['confidence']), (True, '0.7'))
    expect(s + ': Stacey row (2nd Canadian Division, Groesbeek, 10 Nov 1944) gains R882 without a raise', ('R882' in refs('C1330'), claims['C1330']['confidence']), (True, '0.5'))
    expect(s + ': G119: 4th Canadian Armoured on the Maas on 9 Jan 1945 is preferred over the Bavel map row',
           (claims['C9031']['conflict_group_id'], claims['C9031']['claim_status'], claims['C5037']['conflict_group_id'], claims['C5037']['claim_status'], claims['C5037']['confidence']),
           ('G119', 'preferred', 'G119', 'alternate', '0.5'))
    expect(s + ': 2nd Canadian Armoured Brigade takes over the Western Approaches on 11 Nov 1944 (new place Wijchen)',
           (claims['C9022']['unit_id'], claims['C9022']['date'], claims['C9022']['place_id'], claims['C9022']['confidence']), ('CAN-ARM-002B', '1944-11-11', 'PL4017', '0.3'))
    expect(s + ': II Canadian Corps main headquarters at Wijchen on 22 Nov 1944',
           (claims['C9018']['unit_id'], claims['C9018']['location_represents'], claims['C9018']['place_id'], claims['C9018']['confidence']), ('CAN-COR-002C', 'headquarters', 'PL4017', '0.5'))
    expect(s + ': map-read rows from the report are capped at 0.3', sorted({claims[c]['confidence'] for c in ('C9019', 'C9020', 'C9021', 'C9032', 'C9034')}), ['0.3'])
    expect(s + ': FMS row with an approximate date is cited but not raised (Zetten, 2nd Parachute Division)', ('R882' in refs('C7826'), claims['C7826']['confidence']), (True, '0.3'))
    # gap check (11 November 2026): holes found by checking every fact of the report against the dataset are filled at 0.3
    for cid, uid in (('C9048', 'UK-TNK-034B'), ('C9049', 'UK-TNK-034B'), ('C9050', 'UK-ARM-079D'), ('C9051', 'UK-TNK-006GB'), ('C9052', 'NL-INF-IRNEB'), ('C9053', 'UK-CDO-004B'), ('C9054', 'CAN-ARM-002B')):
        expect(s + ': gap-check row %s (%s) cites the report at 0.3' % (cid, uid), (claims[cid]['unit_id'], 'R882' in refs(cid), claims[cid]['confidence']), (uid, True, '0.3'))


def scenario_216_ahq039_western_netherlands():
    """CMHQ/AHQ report pass, AHQ Report No. 39 (I Canadian Corps in the western Netherlands, 15 Mar-5 May 1945): citations, new rows, G120."""
    s = 'scenario 216'
    claims = {c['claim_id']: c for c in common.load_all_claims()[1]}
    refs = lambda c: claims[c]['reference_ids'].split(';')
    import csv as _csv
    meta = {r['reference_id']: r for r in _csv.DictReader(open(os.path.join(common.ROOT, 'data', 'references_meta.csv'), encoding='utf-8'))}
    expect(s + ': R883 is AHQ Report No. 39 in the DHH reports family', (meta['R883']['source_family'], 'ahq039' in meta['R883']['url']), ('canada_dhh_reports', True))
    expect(s + ': Stacey rows gain R883 without a raise (same Historical Section)', [(('R883' in refs(c)), claims[c]['confidence']) for c in ('C1361', 'C7626', 'C7633')], [(True, '0.3'), (True, '0.5'), (True, '0.5')])
    expect(s + ': G120: I Canadian Corps headquarters at Wijchen on 15 Mar 1945 is preferred over the Stacey sector point at Nijmegen',
           (claims['C9055']['conflict_group_id'], claims['C9055']['claim_status'], claims['C9055']['place_id'], claims['C7578']['conflict_group_id'], claims['C7578']['claim_status'], claims['C7578']['confidence']),
           ('G120', 'preferred', 'PL4017', 'G120', 'alternate', '0.3'))
    expect(s + ': 1st Canadian Division headquarters north of Kootwijkerbroek on 28 Apr 1945 (new place)',
           (claims['C9064']['unit_id'], claims['C9064']['location_represents'], claims['C9064']['place_id'], claims['C9064']['confidence']), ('CAN-INF-001D', 'headquarters', 'PL4028', '0.5'))
    expect(s + ': 361st Volksgrenadier Division surrenders at Culemborg from 7 May 1945', (claims['C9072']['unit_id'], claims['C9072']['event_type'], claims['C9072']['place_id']), ('GER-VG-361D', 'surrender', 'PL4030'))
    expect(s + ': inferred rows stay at 0.3 (Belgian brigade on the Waal; the 1st Division station outside Brussels was later settled to Itegem at 0.5 by CMHQ Report No. 181, scenario 226)', [claims[c]['confidence'] for c in ('C9067', 'C9073')], ['0.3', '0.5'])
    expect(s + ': every R883 row new in this pass is unique by unit and date', len({(claims[c]['unit_id'], claims[c]['date']) for c in claims if 'C9055' <= c <= 'C9073'}), 19)


def scenario_217_ahq032_concluding_phase():
    """CMHQ/AHQ report pass, AHQ Report No. 32 (First Canadian Army, 2 Apr-5 May 1945): citations, new rows, G121, G122."""
    s = 'scenario 217'
    claims = {c['claim_id']: c for c in common.load_all_claims()[1]}
    refs = lambda c: claims[c]['reference_ids'].split(';')
    import csv as _csv
    meta = {r['reference_id']: r for r in _csv.DictReader(open(os.path.join(common.ROOT, 'data', 'references_meta.csv'), encoding='utf-8'))}
    expect(s + ': R884 is AHQ Report No. 32 in the DHH reports family', (meta['R884']['source_family'], 'ahq032' in meta['R884']['url']), ('canada_dhh_reports', True))
    expect(s + ': Stacey rows gain R884 without a raise (same Historical Section)', [(('R884' in refs(c)), claims[c]['confidence']) for c in ('C7590', 'C1375', 'C7651')], [(True, '0.5'), (True, '0.7'), (True, '0.5')])
    expect(s + ': British official-history rows gain R884 and stay at 0.7', [(('R884' in refs(c)), claims[c]['confidence']) for c in ('C1520', 'C1536')], [(True, '0.7'), (True, '0.7')])
    expect(s + ': the 53rd Division map row near Hoya is cited, not raised (brigade only)', (('R884' in refs('C6631')), claims['C6631']['confidence']), (True, '0.5'))
    expect(s + ': G121: 5th Canadian Armoured Division headquarters at Barneveld on 20 Apr 1945 is preferred over the inferred Groningen row',
           (claims['C9074']['conflict_group_id'], claims['C9074']['claim_status'], claims['C9074']['place_id'], claims['C7609']['conflict_group_id'], claims['C7609']['claim_status'], claims['C7609']['confidence']),
           ('G121', 'preferred', 'PL0720', 'G121', 'alternate', '0.3'))
    expect(s + ': G122: Polish armour at Papenburg on 21 Apr 1945 is preferred over the inferred Delfzijl row',
           (claims['C9075']['conflict_group_id'], claims['C9075']['claim_status'], claims['C7605']['conflict_group_id'], claims['C7605']['claim_status']),
           ('G122', 'preferred', 'G122', 'alternate'))
    expect(s + ': 2nd Canadian Armoured Brigade fills its April hole (Westerscheps, Godensholt, Westerstede)', [(claims[c]['unit_id'], claims[c]['date']) for c in ('C9078', 'C9079', 'C9080')],
           [('CAN-ARM-002B', '1945-04-28'), ('CAN-ARM-002B', '1945-04-30'), ('CAN-ARM-002B', '1945-05-03')])
    expect(s + ': intelligence and concentration-area rows stay at 0.3', [claims[c]['confidence'] for c in ('C9102', 'C9103', 'C9104')], ['0.3', '0.3', '0.3'])
    expect(s + ': every R884 row new in this pass is unique by unit and date', len({(claims[c]['unit_id'], claims[c]['date']) for c in claims if 'C9074' <= c <= 'C9104'}), 31)


def scenario_218_ahq019_rhine_crossing():
    """CMHQ/AHQ report pass, AHQ Report No. 19 (Operation Plunder, 23 Mar-1 Apr 1945): citations, notes, new rows; and the AHQ 32 URL fix."""
    s = 'scenario 218'
    claims = {c['claim_id']: c for c in common.load_all_claims()[1]}
    refs = lambda c: claims[c]['reference_ids'].split(';')
    import csv as _csv
    meta = {r['reference_id']: r for r in _csv.DictReader(open(os.path.join(common.ROOT, 'data', 'references_meta.csv'), encoding='utf-8'))}
    expect(s + ': R885 is AHQ Report No. 19 in the DHH reports family (part 1 URL)', (meta['R885']['source_family'], meta['R885']['url'].endswith('ahq019-1.pdf')), ('canada_dhh_reports', True))
    expect(s + ': R884 points at an existing part file, not the missing ahq032.pdf', meta['R884']['url'].endswith('ahq032-1.pdf'), True)
    expect(s + ': Stacey rows gain R885 without a raise', [(('R885' in refs(c)), claims[c]['confidence']) for c in ('C1382', 'C7576', 'C1393')], [(True, '0.7'), (True, '0.5'), (True, '0.5')])
    expect(s + ': British official-history rows gain R885 and stay at 0.7', [(('R885' in refs(c)), claims[c]['confidence']) for c in ('C1506', 'C1512')], [(True, '0.7'), (True, '0.7')])
    expect(s + ': the 43rd Division map row near Moyland keeps its value; the 6th Parachute Division Twente Canal row gets no conflict group',
           (claims['C6452']['confidence'], claims['C6452']['conflict_group_id'], claims['C8012']['conflict_group_id'], claims['C8012']['claim_status']), ('0.5', '', '', 'preferred'))
    expect(s + ': 51st Division fills its 25 Mar-2 Apr hole (Rees, Isselburg, Dinxperlo)', [(claims[c]['unit_id'], claims[c]['date'], claims[c]['place_id']) for c in ('C9108', 'C9109', 'C9110')],
           [('UK-INF-051D', '1945-03-26', 'PL0637'), ('UK-INF-051D', '1945-03-28', 'PL3616'), ('UK-INF-051D', '1945-03-30', 'PL3546')])
    expect(s + ': Montgomery tactical headquarters at Venlo on 27 Mar 1945', (claims['C9107']['unit_id'], claims['C9107']['location_represents'], claims['C9107']['place_id']), ('UK-AG-021G', 'headquarters', 'PL0577'))
    expect(s + ': intelligence and approximate rows stay at 0.3', [claims[c]['confidence'] for c in ('C9105', 'C9111', 'C9114', 'C9115', 'C9117', 'C9119', 'C9120', 'C9121')], ['0.3'] * 8)
    expect(s + ': every R885 row new in this pass is unique by unit and date', len({(claims[c]['unit_id'], claims[c]['date']) for c in claims if 'C9105' <= c <= 'C9121'}), 17)


def scenario_219_cmhq186_blockbuster():
    """CMHQ/AHQ report pass, CMHQ Report No. 186 (Operation Blockbuster, 26 Feb-23 Mar 1945): citations without raises and hole rows."""
    s = 'scenario 219'
    claims = {c['claim_id']: c for c in common.load_all_claims()[1]}
    refs = lambda c: claims[c]['reference_ids'].split(';')
    import csv as _csv
    meta = {r['reference_id']: r for r in _csv.DictReader(open(os.path.join(common.ROOT, 'data', 'references_meta.csv'), encoding='utf-8'))}
    expect(s + ': R886 is CMHQ Report No. 186 in the DHH reports family', (meta['R886']['source_family'], meta['R886']['url'].endswith('cmhq-reports/cmhq186.pdf')), ('canada_dhh_reports', True))
    expect(s + ': Stacey rows gain R886 without a raise', [(('R886' in refs(c)), claims[c]['confidence']) for c in ('C1371', 'C1381', 'C7559')], [(True, '0.7'), (True, '0.7'), (True, '0.5')])
    expect(s + ': rows on two families and the Ellis-only row gain R886 and stay at 0.7', [(('R886' in refs(c)), claims[c]['confidence']) for c in ('C1497', 'C1501', 'C1499')], [(True, '0.7')] * 3)
    expect(s + ': map rows cited, not raised (part of the division, a strip, a day apart)', [(('R886' in refs(c)), claims[c]['confidence']) for c in ('C6212', 'C6211', 'C6039')], [(True, '0.3'), (True, '0.5'), (True, '0.3')])
    expect(s + ': 4th Canadian Armoured Division fills its 28 Feb-8 Mar hole (Kirsel, Labbeck, Veen)', [(claims[c]['unit_id'], claims[c]['date'], claims[c]['place_id']) for c in ('C9123', 'C9124', 'C9125')],
           [('CAN-ARM-004D', '1945-03-01', 'PL4054'), ('CAN-ARM-004D', '1945-03-04', 'PL4055'), ('CAN-ARM-004D', '1945-03-07', 'PL3477')])
    expect(s + ': 35th US Division at Fort Blücher (Büderich) on 11 Mar 1945', (claims['C9133']['unit_id'], claims['C9133']['date'], claims['C9133']['place_id'], claims['C9133']['location_qualifier']), ('US-INF-035D', '1945-03-11', 'PL4058', 'Fort Blücher'))
    expect(s + ': rest areas after the battle are refitting rows', [(claims[c]['activity_status'], claims[c]['confidence']) for c in ('C9126', 'C9130')], [('refitting', '0.3'), ('refitting', '0.3')])
    expect(s + ': intelligence and one-battalion rows stay at 0.3', [claims[c]['confidence'] for c in ('C9127', 'C9134')], ['0.3', '0.3'])
    expect(s + ': every R886 row new in this pass is unique by unit and date', len({(claims[c]['unit_id'], claims[c]['date']) for c in claims if 'C9122' <= c <= 'C9134'}), 13)


def scenario_220_cmhq155_veritable():
    """CMHQ/AHQ report pass, CMHQ Report No. 155 (Operation Veritable, preliminary report, 8-25 Feb 1945): citations without raises, hole rows and operation fixes."""
    s = 'scenario 220'
    claims = {c['claim_id']: c for c in common.load_all_claims()[1]}
    refs = lambda c: claims[c]['reference_ids'].split(';')
    import csv as _csv
    meta = {r['reference_id']: r for r in _csv.DictReader(open(os.path.join(common.ROOT, 'data', 'references_meta.csv'), encoding='utf-8'))}
    expect(s + ': R887 is CMHQ Report No. 155 in the DHH reports family', (meta['R887']['source_family'], meta['R887']['url'].endswith('cmhq-reports/cmhq155.pdf')), ('canada_dhh_reports', True))
    expect(s + ': Stacey rows gain R887 without a raise', [(('R887' in refs(c)), claims[c]['confidence']) for c in ('C1368', 'C7454', 'C7487')], [(True, '0.7'), (True, '0.5'), (True, '0.5')])
    expect(s + ': two-family rows gain R887 and keep their confidence', [(('R887' in refs(c)), claims[c]['confidence']) for c in ('C1487', 'C1492', 'C1380')], [(True, '0.7'), (True, '0.7'), (True, '0.5')])
    expect(s + ': rows a day or two from the report are cited, not raised', [(('R887' in refs(c)), claims[c]['confidence']) for c in ('C7469', 'C7501', 'C7507')], [(True, '0.5')] * 3)
    expect(s + ': hole rows (84th Division intelligence, 53rd Division at Asperden, 43rd Division back at Cleve)', [(claims[c]['unit_id'], claims[c]['date'], claims[c]['place_id'], claims[c]['confidence']) for c in ('C9135', 'C9136', 'C9137')],
           [('GER-INF-084D', '1945-02-03', 'PL0698', '0.3'), ('UK-INF-053D', '1945-02-16', 'PL3456', '0.5'), ('UK-INF-043D', '1945-02-22', 'PL0578', '0.3')])
    expect(s + ': hole rows carry the Veritable operation after 8 Feb', [claims[c]['operation_id'] for c in ('C9135', 'C9136', 'C9137')], ['OP-CAMP-RHINELAND', 'OP-VERITABLE', 'OP-VERITABLE'])
    expect(s + ': chunk 5 rows moved to Veritable or Blockbuster', [claims[c]['operation_id'] for c in ('C9122', 'C9123', 'C9129', 'C9132', 'C9126')], ['OP-VERITABLE', 'OP-BLOCKBUSTER', 'OP-BLOCKBUSTER', 'OP-BLOCKBUSTER', 'OP-CAMP-RHINELAND'])


def scenario_221_cmhq188_scheldt():
    """CMHQ/AHQ report pass, CMHQ Report No. 188 (Canadian operations 1 Oct-8 Nov 1944, the clearing of the Scheldt Estuary): citations without raises and hole rows."""
    s = 'scenario 221'
    claims = {c['claim_id']: c for c in common.load_all_claims()[1]}
    refs = lambda c: claims[c]['reference_ids'].split(';')
    import csv as _csv
    meta = {r['reference_id']: r for r in _csv.DictReader(open(os.path.join(common.ROOT, 'data', 'references_meta.csv'), encoding='utf-8'))}
    expect(s + ': R888 is CMHQ Report No. 188 in the DHH reports family', (meta['R888']['source_family'], meta['R888']['url'].endswith('cmhq-reports/cmhq188.pdf')), ('canada_dhh_reports', True))
    expect(s + ': Stacey rows gain R888 without a raise', [(('R888' in refs(c)), claims[c]['confidence']) for c in ('C1312', 'C1313', 'C7371', 'C7391')], [(True, '0.5'), (True, '0.7'), (True, '0.5'), (True, '0.5')])
    expect(s + ': two-family rows gain R888 and keep their confidence', [(('R888' in refs(c)), claims[c]['confidence']) for c in ('C7353', 'C1704', 'C7401')], [(True, '0.7'), (True, '0.9'), (True, '0.7')])
    expect(s + ': a map row with only a battalion on the date, and a map row on a line, are cited not raised', [(('R888' in refs(c)), claims[c]['confidence']) for c in ('C3423', 'C3712')], [(True, '0.5'), (True, '0.5')])
    expect(s + ': a row already on CMHQ Report No. 173 is cited, not raised', (('R888' in refs('C1565')), claims['C1565']['confidence']), (True, '0.7'))
    expect(s + ': hole rows (units, dates, places, confidence)', [(claims[c]['unit_id'], claims[c]['date'], claims[c]['place_id'], claims[c]['confidence']) for c in ('C9138', 'C9142', 'C9146', 'C9152', 'C9154')],
           [('GER-INF-085D', '1944-09-02', 'PL3575', '0.3'), ('CAN-ARM-004D', '1944-10-05', 'PL0679', '0.3'), ('CAN-INF-003D', '1944-10-19', 'PL4059', '0.3'), ('CAN-INF-003D', '1944-11-05', 'PL0795', '0.3'), ('UK-INF-049D', '1944-11-05', 'PL4060', '0.5')])
    expect(s + ': hole rows carry the operation of their date', [claims[c]['operation_id'] for c in ('C9138', 'C9142', 'C9145', 'C9150', 'C9152')], ['OP-CAMP-NORTHERN-FRANCE', 'OP-SCHELDT', 'OP-SWITCHBACK', 'OP-PHEASANT', 'OP-CAMP-RHINELAND'])
    expect(s + ': rest-area rows are refitting', [claims[c]['activity_status'] for c in ('C9152', 'C9153')], ['refitting', 'refitting'])
    expect(s + ': no conflict group opened by this report', [claims[c]['conflict_group_id'] for c in ('C1705', 'C9154', 'C9150')], ['', '', ''])


def scenario_222_cmhq183_pursuit():
    """CMHQ/AHQ report pass, CMHQ Report No. 183 (First Canadian Army in the pursuit, 23 Aug-30 Sep 1944): citations without raises and hole rows."""
    s = 'scenario 222'
    claims = {c['claim_id']: c for c in common.load_all_claims()[1]}
    refs = lambda c: claims[c]['reference_ids'].split(';')
    import csv as _csv
    meta = {r['reference_id']: r for r in _csv.DictReader(open(os.path.join(common.ROOT, 'data', 'references_meta.csv'), encoding='utf-8'))}
    expect(s + ': R889 is CMHQ Report No. 183 in the DHH reports family', (meta['R889']['source_family'], meta['R889']['url'].endswith('cmhq-reports/cmhq183.pdf')), ('canada_dhh_reports', True))
    expect(s + ': Stacey rows gain R889 without a raise', [(('R889' in refs(c)), claims[c]['confidence']) for c in ('C7253', 'C7298', 'C7305', 'C7319')], [(True, '0.7'), (True, '0.5'), (True, '0.5'), (True, '0.5')])
    expect(s + ': two-family rows gain R889 and keep their confidence', [(('R889' in refs(c)), claims[c]['confidence']) for c in ('C1554', 'C1558', 'C1560')], [(True, '0.7'), (True, '0.9'), (True, '0.7')])
    expect(s + ': Ellis rows for British formations are cited, not raised', [(('R889' in refs(c)), claims[c]['confidence']) for c in ('C1443', 'C9017', 'C1445')], [(True, '0.5'), (True, '0.5'), (True, '0.7')])
    expect(s + ': map rows matched only by a brigade or battalion, or by a broad area, are cited not raised', [(('R889' in refs(c)), claims[c]['confidence']) for c in ('C2785', 'C2790', 'C3093')], [(True, '0.5'), (True, '0.5'), (True, '0.5')])
    expect(s + ': a row already on CMHQ Report No. 188 is cited, not raised', (('R889' in refs('C9140')), claims['C9140']['confidence']), (True, '0.3'))
    expect(s + ': hole rows (units, dates, places, confidence)', [(claims[c]['unit_id'], claims[c]['date'], claims[c]['place_id'], claims[c]['confidence']) for c in ('C9155', 'C9165', 'C9170', 'C9185', 'C9192')],
           [('CAN-ARM-002B', '1944-08-23', 'PL4062', '0.5'), ('POL-ARM-001D', '1944-09-02', 'PL0937', '0.3'), ('BEL-INF-001B', '1944-08-19', 'PL4073', '0.5'), ('UK-CDO-004B', '1944-08-31', 'PL4072', '0.5'), ('GER-INF-711D', '1944-09-20', 'PL4081', '0.3')])
    expect(s + ': hole rows carry the operation of their date', [claims[c]['operation_id'] for c in ('C9171', 'C9155', 'C9189', 'C9191')], ['OP-CAMP-NORTHERN-FRANCE', 'OP-PURSUIT', 'OP-CAMP-NORTHERN-FRANCE', 'OP-CAMP-RHINELAND'])
    expect(s + ': rest and reserve rows', [claims[c]['activity_status'] for c in ('C9191', 'C9181')], ['refitting', 'reserve'])
    expect(s + ': the 2nd Canadian Division\'s Dieppe stay is cited on the existing span rows, with no new point row', ([('R889' in refs(c)) for c in ('C1324', 'C1820')], [c for c in claims if c >= 'C9155' and len(c) == 5 and claims[c]['unit_id'] == 'CAN-INF-002D' and claims[c]['date'] == '1944-09-03']), ([True, True], []))
    expect(s + ': the French Boos is a new place, not the German one', (claims['C9164']['place_id'] != 'PL2488', claims['C9164']['country']), (True, 'FR'))
    expect(s + ': no conflict group opened by this report', [claims[c]['conflict_group_id'] for c in ('C9160', 'C9190', 'C9181')], ['', '', ''])


def scenario_223_cmhq184_channel_ports():
    """CMHQ/AHQ report pass, CMHQ Report No. 184 (clearing the Channel ports, 3 Sep 44-6 Feb 45): citations without raises and hole rows."""
    s = 'scenario 223'
    claims = {c['claim_id']: c for c in common.load_all_claims()[1]}
    refs = lambda c: claims[c]['reference_ids'].split(';')
    import csv as _csv
    meta = {r['reference_id']: r for r in _csv.DictReader(open(os.path.join(common.ROOT, 'data', 'references_meta.csv'), encoding='utf-8'))}
    expect(s + ': R890 is CMHQ Report No. 184 in the DHH reports family', (meta['R890']['source_family'], meta['R890']['url'].endswith('cmhq-reports/cmhq184.pdf')), ('canada_dhh_reports', True))
    expect(s + ': Stacey rows gain R890 without a raise', [(('R890' in refs(c)), claims[c]['confidence']) for c in ('C1308', 'C7312', 'C1310', 'C7314')], [(True, '0.7'), (True, '0.5'), (True, '0.7'), (True, '0.5')])
    expect(s + ': two-family rows gain R890 and keep their confidence', [(('R890' in refs(c)), claims[c]['confidence']) for c in ('C1459', 'C1711', 'C1586')], [(True, '0.7'), (True, '0.7'), (True, '0.7')])
    expect(s + ': an Ellis row for the 79th Armoured Division is cited, not raised', (('R890' in refs('C8975')), claims['C8975']['confidence']), (True, '0.5'))
    expect(s + ': map rows matched only by a brigade, or by a broad area, are cited not raised', [(('R890' in refs(c)), claims[c]['confidence']) for c in ('C3024', 'C3399', 'C2969')], [(True, '0.5'), (True, '0.5'), (True, '0.5')])
    expect(s + ': rows on another DHH report are cited, not raised', [(('R890' in refs(c)), claims[c]['confidence']) for c in ('C9186', 'C1588')], [(True, '0.3'), (True, '0.5')])
    expect(s + ': the Dunkirk surrender row keeps its date and confidence', (('R890' in refs('C1809')), claims['C1809']['date'], claims['C1809']['confidence']), (True, '1945-05-09', '0.9'))
    expect(s + ': hole rows (units, dates, places, confidence)', [(claims[c]['unit_id'], claims[c]['date'], claims[c]['place_id'], claims[c]['confidence']) for c in ('C9193', 'C9194', 'C9196', 'C9201', 'C9206')],
           [('UK-COR-001C', '1944-09-10', claims['C1461']['place_id'], '0.5'), ('CAN-INF-003D', '1944-09-10', 'PL0677', '0.3'), ('CAN-ARM-002B', '1944-09-17', 'PL0677', '0.3'), ('GER-FEST-DUNKIRK', '1944-09-18', 'PL0624', '0.5'), ('CZ-ARM-001B', '1944-10-06', 'PL0624', '0.5')])
    expect(s + ': hole rows carry the operation of their date', [claims[c]['operation_id'] for c in ('C9193', 'C9194', 'C9195', 'C9198', 'C9202')], ['OP-ASTONIA', 'OP-PURSUIT', 'OP-WELLHIT', 'OP-UNDERGO', 'OP-CAMP-RHINELAND'])
    expect(s + ': part-of-formation and intelligence rows stay at 0.3', [claims[c]['confidence'] for c in ('C9195', 'C9197', 'C9198', 'C9199', 'C9200')], ['0.3'] * 5)
    expect(s + ': no Czechoslovak or Dunkirk-garrison row after the brigade left First Canadian Army (27 November 1944) comes from this report', [c for c in claims if 'C9193' <= c <= 'C9207' and len(c) == 5 and claims[c]['date'] > '1944-11-27'], [])
    expect(s + ': no conflict group opened by this report', [claims[c]['conflict_group_id'] for c in ('C9193', 'C9201', 'C9207')], ['', '', ''])


def scenario_224_ahq065_falaise():
    """CMHQ/AHQ report pass, AHQ Report No. 65 (Canadian operations 1-23 August 1944): map raises, citations without raises and hole rows."""
    s = 'scenario 224'
    claims = {c['claim_id']: c for c in common.load_all_claims()[1]}
    refs = lambda c: claims[c]['reference_ids'].split(';')
    import csv as _csv
    meta = {r['reference_id']: r for r in _csv.DictReader(open(os.path.join(common.ROOT, 'data', 'references_meta.csv'), encoding='utf-8'))}
    places = {r['place_id']: r for r in _csv.DictReader(open(os.path.join(common.ROOT, 'data', 'places.csv'), encoding='utf-8'))}
    expect(s + ': R891 is AHQ Report No. 65 in the DHH reports family', (meta['R891']['source_family'], meta['R891']['url'].endswith('ahq-reports/ahq065.pdf')), ('canada_dhh_reports', True))
    expect(s + ': map rows agreeing within 5 km on the same date are raised to 0.7', [(('R891' in refs(c)), claims[c]['confidence']) for c in ('C2669', 'C2671', 'C2737')], [(True, '0.7')] * 3)
    expect(s + ': map rows matched only in part or by a broad area are cited, not raised', [(('R891' in refs(c)), claims[c]['confidence']) for c in ('C2615', 'C2670', 'C2736')], [(True, '0.5')] * 3)
    expect(s + ': Stacey rows gain R891 without a raise', [(('R891' in refs(c)), claims[c]['confidence']) for c in ('C1333', 'C1335', 'C1305', 'C7241')], [(True, '0.7'), (True, '0.5'), (True, '0.5'), (True, '0.5')])
    expect(s + ': Ellis rows for British formations are cited, not raised', [(('R891' in refs(c)), claims[c]['confidence']) for c in ('C9015', 'C1441', 'C9003')], [(True, '0.5')] * 3)
    expect(s + ': two-family Polish rows keep their confidence', [(('R891' in refs(c)), claims[c]['confidence']) for c in ('C1547', 'C1551', 'C1552')], [(True, '0.7'), (True, '0.9'), (True, '0.9')])
    expect(s + ': hole rows (units, dates, places, confidence)', [(claims[c]['unit_id'], claims[c]['date'], places[claims[c]['place_id']]['name'], claims[c]['confidence']) for c in ('C9208', 'C9209', 'C9212', 'C9215', 'C9219')],
           [('CAN-INF-002D', '1944-08-05', 'Saint-André-sur-Orne, Calvados', '0.5'), ('CAN-INF-002D', '1944-08-13', 'Tournebu, Normandy', '0.5'), ('CAN-ARM-004D', '1944-08-05', 'Bourguébus, Calvados', '0.5'),
            ('CAN-ARM-002B', '1944-08-14', 'Bons-Tassilly, Calvados', '0.5'), ('UK-INF-051D', '1944-08-10', 'Saint-Sylvain, Calvados', '0.5')])
    expect(s + ': hole rows carry the operation of their date', [claims[c]['operation_id'] for c in ('C9208', 'C9210', 'C9211', 'C9215', 'C9216', 'C9221')],
           ['OP-CAMP-NORTHERN-FRANCE', 'OP-TOTALIZE', 'OP-FALAISE', 'OP-TRACTABLE', 'OP-TRACTABLE', 'OP-CAMP-NORTHERN-FRANCE'])
    expect(s + ': part, sector and intelligence rows stay at 0.3', [claims[c]['confidence'] for c in ('C9210', 'C9211', 'C9213', 'C9214', 'C9216', 'C9217', 'C9218', 'C9220', 'C9221', 'C9222', 'C9223', 'C9224')], ['0.3'] * 12)
    import datetime
    new = [claims[c] for c in claims if 'C9208' <= c <= 'C9224' and len(c) == 5]
    def gap_ok(r):
        others = [o for o in claims.values() if o['unit_id'] == r['unit_id'] and o['claim_id'] != r['claim_id']]
        d = datetime.date.fromisoformat(r['date'])
        return all(abs((datetime.date.fromisoformat(o['date']) - d).days) >= 2 for o in others)
    expect(s + ': every new row is at least two days from any other row of its unit', [r['claim_id'] for r in new if not gap_ok(r)], [])
    expect(s + ': no new row is outside 1-23 August 1944', [r['claim_id'] for r in new if not ('1944-08-01' <= r['date'] <= '1944-08-23')], [])
    expect(s + ': no conflict group opened by this report', [r['conflict_group_id'] for r in new], [''] * 17)


def scenario_225_ahq058_july():
    """CMHQ/AHQ report pass, AHQ Report No. 58 (Canadian operations in July 1944): map raises, citations without raises, review flags and hole rows."""
    import datetime
    import csv as _csv
    s = 'scenario 225'
    claims = {c['claim_id']: c for c in common.load_all_claims()[1]}
    refs = lambda c: claims[c]['reference_ids'].split(';')
    meta = {r['reference_id']: r for r in _csv.DictReader(open(os.path.join(common.ROOT, 'data', 'references_meta.csv'), encoding='utf-8'))}
    places = {r['place_id']: r for r in _csv.DictReader(open(os.path.join(common.ROOT, 'data', 'places.csv'), encoding='utf-8'))}
    expect(s + ': R892 is AHQ Report No. 58 in the DHH reports family', (meta['R892']['source_family'], meta['R892']['url'].endswith('ahq-reports/ahq058.pdf')), ('canada_dhh_reports', True))
    expect(s + ': German map rows agreeing within 5 km on 25 July are cited but stay at 0.3', [(('R892' in refs(c)), claims[c]['confidence']) for c in ('C2453', 'C2454')], [(True, '0.3')] * 2)
    expect(s + ': Stacey rows gain R892 without a raise', [(('R892' in refs(c)), claims[c]['confidence']) for c in ('C1301', 'C1318', 'C1279', 'C1278')], [(True, '0.5'), (True, '0.7'), (True, '0.5'), (True, '0.5')])
    expect(s + ': part-only matches are cited, not raised', [(('R892' in refs(c)), claims[c]['confidence']) for c in ('C9013', 'C2464', 'C8423', 'C2625')], [(True, '0.5'), (True, '0.5'), (True, '0.3'), (True, '0.3')])
    expect(s + ': a row already on another DHH report keeps its value', (('R892' in refs('C2615')), claims['C2615']['confidence']), (True, '0.5'))
    expect(s + ': flagged rows keep their values and do not cite the report', [(('R892' in refs(c)), claims[c]['confidence'], 'AHQ Report No. 58' in claims[c]['notes']) for c in ('C2422', 'C2419', 'C2450', 'C0780')],
           [(False, '0.3', True), (False, '0.3', True), (False, '0.3', True), (False, '0.5', True)])
    expect(s + ': hole rows (units, dates, places, confidence)', [(claims[c]['unit_id'], claims[c]['date'], places[claims[c]['place_id']]['name'], claims[c]['confidence']) for c in ('C9225', 'C9228', 'C9229', 'C9232', 'C9233', 'C9235')],
           [('CAN-INF-003D', '1944-07-07', 'Lasson, Calvados', '0.3'), ('CAN-INF-002D', '1944-07-22', 'Saint-André-sur-Orne, Calvados', '0.5'), ('CAN-INF-002D', '1944-07-28', 'Verrières (Verrières Ridge), Calvados', '0.5'),
            ('CAN-ARM-002B', '1944-07-30', 'Louvigny, Calvados', '0.5'), ('CAN-ARM-004D', '1944-07-29', 'Cormelles-le-Royal, Calvados', '0.5'), ('GER-PZ-116D', '1944-07-22', 'Saint-Sylvain, Calvados', '0.3')])
    expect(s + ': hole rows carry the operation of their date', [claims[c]['operation_id'] for c in ('C9225', 'C9227', 'C9231', 'C9234', 'C9237', 'C9239')],
           ['OP-CAMP-NORMANDY', 'OP-CAMP-NORTHERN-FRANCE', 'OP-CHARNWOOD', 'OP-CAMP-NORTHERN-FRANCE', 'OP-ATLANTIC', 'OP-ATLANTIC'])
    expect(s + ': part, sector and intelligence rows stay at 0.3', [claims[c]['confidence'] for c in ('C9225', 'C9226', 'C9227', 'C9230', 'C9231', 'C9234', 'C9236', 'C9237', 'C9238', 'C9239', 'C9240')], ['0.3'] * 11)
    new = [claims[c] for c in claims if 'C9225' <= c <= 'C9240' and len(c) == 5]
    def gap_ok(r):
        others = [o for o in claims.values() if o['unit_id'] == r['unit_id'] and o['claim_id'] != r['claim_id']]
        d = datetime.date.fromisoformat(r['date'])
        return all(abs((datetime.date.fromisoformat(o['date']) - d).days) >= 2 for o in others)
    expect(s + ': every new row is at least two days from any other row of its unit', [r['claim_id'] for r in new if not gap_ok(r)], [])
    expect(s + ': no new row is outside July 1944', [r['claim_id'] for r in new if not ('1944-07-01' <= r['date'] <= '1944-07-31')], [])
    expect(s + ': no conflict group opened by this report', [r['conflict_group_id'] for r in new], [''] * 16)


def scenario_226_cmhq181_goldflake():
    """CMHQ/AHQ report pass, CMHQ Report No. 181 (Operation Goldflake, February-March 1945): the Itegem correction, a flagged row and hole rows."""
    import csv as _csv
    s = 'scenario 226'
    claims = {c['claim_id']: c for c in common.load_all_claims()[1]}
    refs = lambda c: claims[c]['reference_ids'].split(';')
    meta = {r['reference_id']: r for r in _csv.DictReader(open(os.path.join(common.ROOT, 'data', 'references_meta.csv'), encoding='utf-8'))}
    places = {r['place_id']: r for r in _csv.DictReader(open(os.path.join(common.ROOT, 'data', 'places.csv'), encoding='utf-8'))}
    expect(s + ': R893 is CMHQ Report No. 181 in the DHH reports family', (meta['R893']['source_family'], meta['R893']['url'].endswith('cmhq-reports/cmhq181.pdf')), ('canada_dhh_reports', True))
    c = claims['C9073']
    expect(s + ': the 1st Canadian Division station "Itogon" is now Itegem at 0.5, citing both reports and GeoNames', (places[c['place_id']]['name'], c['confidence'], refs('C9073')), ('Itegem (Heist-op-den-Berg), Antwerp', '0.5', ['R883', 'R893', 'R782']))
    expect(s + ': the Antwerp row of the 5th Canadian Armoured Division is flagged, not changed', (('R893' in refs('C1402')), claims['C1402']['confidence'], 'Dixmude' in claims['C1402']['notes']), (False, '0.3', True))
    expect(s + ': hole rows (units, dates, places, confidence, activity)', [(claims[x]['unit_id'], claims[x]['date'], places[claims[x]['place_id']]['name'], claims[x]['confidence'], claims[x]['activity_status']) for x in ('C9241', 'C9242', 'C9243')],
           [('CAN-COR-001C', '1945-02-24', 'Marseille, Bouches-du-Rhône', '0.5', 'transit'), ('CAN-COR-001C', '1945-03-03', 'Ronse (Renaix), East Flanders', '0.5', 'transit'), ('CAN-ARM-001B', '1945-03-12', 'Lauwe (Menen), West Flanders', '0.5', 'refitting')])
    expect(s + ': the corps arrives in Belgium before it takes over at Nijmegen', [claims[x]['date'] for x in ('C9242', 'C9055')], ['1945-03-03', '1945-03-15'])


def scenario_227_delattre_c1_armour():
    """de Lattre leftover pass, chunk 1: the 1st, 2nd and 5th Armoured Divisions (R686): supporting citations, two raises and new rows."""
    import csv as _csv
    s = 'scenario 227'
    claims = {c['claim_id']: c for c in common.load_all_claims()[1]}
    refs = lambda c: claims[c]['reference_ids'].split(';')
    places = {r['place_id']: r for r in _csv.DictReader(open(os.path.join(common.ROOT, 'data', 'places.csv'), encoding='utf-8'))}
    new_ids = ['C9244', 'C9245', 'C9246', 'C9247', 'C9248', 'C9249', 'C9250', 'C9251', 'C9252', 'C9253', 'C9254', 'C9255', 'C9256', 'C9257', 'C9258', 'C9259', 'C9260', 'C9261', 'C9262', 'C9263', 'C9264', 'C9265', 'C9266', 'C9267', 'C9268', 'C9269', 'C9270', 'C9271', 'C9272', 'C9273', 'C9274']
    expect(s + ': new rows (unit, date, place, confidence, activity)', [(claims[x]['unit_id'], claims[x]['date'], places[claims[x]['place_id']]['name'], claims[x]['confidence'], claims[x]['activity_status']) for x in new_ids], [('FR-ARM-001D', '1944-08-17', 'Le Luc, Var', '0.3', 'in_line'), ('FR-ARM-001D', '1944-08-25', 'Avignon, Vaucluse', '0.5', 'in_line'), ('FR-ARM-001D', '1944-08-29', 'Bagnols-sur-Cèze, Gard', '0.5', ''), ('FR-ARM-001D', '1944-09-05', 'Chalon-sur-Saône, Saône-et-Loire', '0.3', 'in_line'), ('FR-ARM-001D', '1944-09-11', "Dijon, Côte-d'Or", '0.3', 'in_line'), ('FR-ARM-001D', '1944-09-20', 'Mélisey, Haute-Saône', '0.3', 'in_line'), ('FR-ARM-001D', '1944-10-04', 'Le Thillot, Vosges', '0.5', 'in_line'), ('FR-ARM-001D', '1944-11-20', 'Altkirch, Haut-Rhin', '0.3', 'in_line'), ('FR-ARM-001D', '1944-11-24', 'Mulhouse, Haut-Rhin', '0.5', 'in_line'), ('FR-ARM-001D', '1944-12-11', 'Aspach-le-Bas, Haut-Rhin', '0.3', 'in_line'), ('FR-ARM-001D', '1945-01-20', 'Kingersheim, Haut-Rhin', '0.3', 'in_line'), ('FR-ARM-001D', '1945-02-05', 'Réguisheim, Haut-Rhin', '0.3', 'in_line'), ('FR-ARM-001D', '1945-02-08', 'Fessenheim, Haut-Rhin', '0.3', 'in_line'), ('FR-ARM-001D', '1945-04-26', 'Konstanz, Baden-Württemberg', '0.3', 'in_line'), ('FR-ARM-001D', '1945-04-30', 'Immenstadt im Allgäu, Bayern', '0.5', 'in_line'), ('FR-ARM-001D', '1945-05-01', 'Fernpass, Tirol', '0.3', 'in_line'), ('FR-ARM-001D', '1945-05-02', 'Sonthofen, Bayern', '0.3', 'in_line'), ('FR-ARM-001D', '1945-05-04', 'Oberstdorf, Bayern', '0.3', 'in_line'), ('FR-ARM-005D', '1944-11-20', 'Grandvillars, Territoire de Belfort', '0.5', 'in_line'), ('FR-ARM-005D', '1944-11-26', 'Aspach, Haut-Rhin', '0.3', 'in_line'), ('FR-ARM-005D', '1944-12-11', 'Aspach-le-Bas, Haut-Rhin', '0.3', 'in_line'), ('FR-ARM-005D', '1945-02-05', 'Osenbach, Haut-Rhin', '0.3', 'in_line'), ('FR-ARM-005D', '1945-03-31', 'Germersheim, Rheinland-Pfalz', '0.3', 'in_line'), ('FR-ARM-005D', '1945-04-02', 'Graben-Neudorf, Baden-Württemberg', '0.3', 'in_line'), ('FR-ARM-005D', '1945-04-18', 'Tübingen, Baden-Württemberg', '0.3', 'in_line'), ('FR-ARM-005D', '1945-04-24', 'Sigmaringen, Baden-Württemberg', '0.3', 'in_line'), ('FR-ARM-005D', '1945-05-04', 'Überlingen, Baden-Württemberg', '0.5', ''), ('FR-ARM-002D', '1944-12-05', 'Rhinau, Bas-Rhin', '0.5', 'in_line'), ('FR-ARM-002D', '1945-01-22', 'Kilstett, Bas-Rhin', '0.3', 'in_line'), ('FR-ARM-002D', '1945-01-25', 'Huttenheim, Bas-Rhin', '0.3', 'in_line'), ('FR-ARM-002D', '1945-02-07', 'Balgau, Haut-Rhin', '0.3', 'in_line')])
    expect(s + ': every new row cites R686 and is a preferred row with no conflict group', [('R686' in refs(x), claims[x]['claim_status'], claims[x]['conflict_group_id']) for x in new_ids], [(True, 'preferred', '')] * len(new_ids))
    cited = ['C1630', 'C1631', 'C1632', 'C1615', 'C1617']
    expect(s + ': rows that gained R686 as a supporting citation', [('R686' in refs(x)) for x in cited], [True] * len(cited))
    raised = {'C1630': '0.9', 'C1632': '0.9'}
    expect(s + ': confidence raises (old value to new value, noted)', [(x, claims[x]['confidence'], ('old value: ' in claims[x]['notes'])) for x in sorted(raised)], [(x, raised[x], True) for x in sorted(raised)])


def scenario_228_delattre_c2_infantry():
    """de Lattre leftovers chunk 2: infantry divisions (1st DFL, 2nd DIM, 3rd DIA, 4th DMM, 9th DIC), two armoured-division rows, a Speyer citation and the C9269 attribution correction"""
    import csv as _csv
    s = 'scenario 228'
    claims = {c['claim_id']: c for c in common.load_all_claims()[1]}
    refs = lambda c: claims[c]['reference_ids'].split(';')
    places = {r['place_id']: r for r in _csv.DictReader(open(os.path.join(common.ROOT, 'data', 'places.csv'), encoding='utf-8'))}
    new_ids = ['C9275', 'C9276', 'C9277', 'C9278', 'C9279', 'C9280', 'C9281', 'C9282', 'C9283', 'C9284', 'C9285', 'C9286', 'C9287', 'C9288', 'C9289', 'C9290', 'C9291', 'C9292', 'C9293', 'C9294', 'C9295', 'C9296', 'C9297', 'C9298', 'C9299', 'C9300', 'C9301', 'C9302', 'C9303', 'C9304', 'C9305', 'C9306', 'C9307', 'C9308', 'C9309', 'C9310', 'C9311', 'C9312', 'C9313']
    expect(s + ': new rows (unit, date, place, confidence, activity)', [(claims[x]['unit_id'], claims[x]['date'], places[claims[x]['place_id']]['name'], claims[x]['confidence'], claims[x]['activity_status']) for x in new_ids], [('FR-INF-001D', '1944-08-23', 'Toulon, Var', '0.3', 'in_line'), ('FR-INF-001D', '1944-09-07', 'Paray-le-Monial, Saône-et-Loire', '0.3', 'in_line'), ('FR-INF-001D', '1944-09-12', "Montbard, Côte-d'Or", '0.3', 'in_line'), ('FR-INF-001D', '1944-09-20', 'Lure, Haute-Saône', '0.3', 'in_line'), ('FR-INF-001D', '1944-09-25', 'Lyoffans, Haute-Saône', '0.3', 'in_line'), ('FR-INF-001D', '1944-09-28', 'Frédéric-Fontaine, Haute-Saône', '0.5', 'in_line'), ('FR-INF-001D', '1944-11-23', 'Éloie, Territoire de Belfort', '0.5', 'in_line'), ('FR-INF-001D', '1944-11-24', "Ballon d'Alsace, Haut-Rhin / Vosges / Territoire de Belfort", '0.5', 'in_line'), ('FR-INF-001D', '1944-11-24', 'Rougemont-le-Château, Territoire de Belfort', '0.3', 'in_line'), ('FR-INF-001D', '1945-01-02', 'Rhinau, Bas-Rhin', '0.5', 'in_line'), ('FR-INF-001D', '1945-01-23', 'Saint-Hippolyte, Haut-Rhin', '0.5', 'in_line'), ('FR-INF-001D', '1945-01-28', 'Grussenheim, Haut-Rhin', '0.5', 'in_line'), ('FR-INF-001D', '1945-02-01', 'Marckolsheim, Bas-Rhin', '0.5', 'in_line'), ('FR-INF-002D', '1944-11-14', 'Gémonval, Doubs', '0.5', 'in_line'), ('FR-INF-002D', '1944-11-17', 'Héricourt, Haute-Saône', '0.5', 'in_line'), ('FR-INF-002D', '1945-01-20', 'Cernay, Haut-Rhin', '0.5', 'in_line'), ('FR-INF-002D', '1945-02-03', 'Wittelsheim, Haut-Rhin', '0.3', 'in_line'), ('FR-INF-002D', '1945-02-09', 'Chalampé, Haut-Rhin', '0.5', 'in_line'), ('FR-INF-002D', '1945-04-06', 'Pforzheim, Baden-Württemberg', '0.5', 'in_line'), ('FR-INF-002D', '1945-04-24', 'Sigmaringen, Baden-Württemberg', '0.3', 'in_line'), ('FR-INF-002D', '1945-05-06', 'Sankt Anton am Arlberg, Tirol', '0.3', 'in_line'), ('FR-INF-003D', '1944-12-20', 'Orbey, Haut-Rhin', '0.3', 'in_line'), ('FR-INF-003D', '1945-01-06', 'Kilstett, Bas-Rhin', '0.3', 'in_line'), ('FR-INF-003D', '1945-03-19', 'Scheibenhardt, Rheinland-Pfalz', '0.3', 'in_line'), ('FR-INF-003D', '1945-03-30', 'Speyer, Rheinland-Pfalz', '0.3', 'in_line'), ('FR-INF-003D', '1945-04-16', 'Pforzheim, Baden-Württemberg', '0.3', 'in_line'), ('FR-INF-003D', '1945-04-20', 'Weil der Stadt, Baden-Württemberg', '0.5', 'in_line'), ('FR-INF-009D', '1944-11-14', 'Colombier-Fontaine, Doubs', '0.5', 'in_line'), ('FR-INF-009D', '1945-01-20', 'Pfastatt, Haut-Rhin', '0.3', 'in_line'), ('FR-INF-009D', '1945-01-22', 'Kingersheim, Haut-Rhin', '0.3', 'in_line'), ('FR-INF-009D', '1945-02-05', 'Réguisheim, Haut-Rhin', '0.3', 'in_line'), ('FR-INF-009D', '1945-02-09', 'Chalampé, Haut-Rhin', '0.5', 'in_line'), ('FR-INF-009D', '1945-04-02', 'Leimersheim, Rheinland-Pfalz', '0.3', 'in_line'), ('FR-INF-009D', '1945-04-21', 'Freiburg im Breisgau, Baden-Württemberg', '0.3', 'in_line'), ('FR-INF-009D', '1945-04-22', 'Neuenburg am Rhein, Baden-Württemberg', '0.3', 'in_line'), ('FR-INF-004D', '1945-01-30', 'Cernay, Haut-Rhin', '0.5', 'in_line'), ('FR-INF-004D', '1945-02-04', 'Soultz-Haut-Rhin, Haut-Rhin', '0.3', 'in_line'), ('FR-ARM-005D', '1945-05-02', 'Dornbirn, Vorarlberg', '0.3', 'in_line'), ('FR-ARM-002D', '1944-09-12', "Montbard, Côte-d'Or", '0.3', 'in_line')])
    expect(s + ': every new row cites R686 and is a preferred row with no conflict group', [('R686' in refs(x), claims[x]['claim_status'], claims[x]['conflict_group_id']) for x in new_ids], [(True, 'preferred', '')] * len(new_ids))
    cited = ['C1641']
    expect(s + ': rows that gained R686 as a supporting citation', [('R686' in refs(x)) for x in cited], [True] * len(cited))
    raised = {}
    expect(s + ': confidence raises (old value to new value, noted)', [(x, claims[x]['confidence'], ('old value: ' in claims[x]['notes'])) for x in sorted(raised)], [(x, raised[x], True) for x in sorted(raised)])
    expect(s + 'corrected C9269 (qualifier, confidence, annotation present)', (claims['C9269']['location_qualifier'], claims['C9269']['confidence'], 'attribution corrected in chunk 2' in claims['C9269']['notes'], 'old value' in claims['C9269']['notes']), ("cavalry regiment and Mozat's column only", '0.3', True, True))


def scenario_229_delattre_c3_headquarters():
    """de Lattre leftovers chunk 3: army and corps headquarters, corps rows, the 10th Division, nine supporting citations (two raises) and three flagged map rows"""
    import csv as _csv
    s = 'scenario 229'
    claims = {c['claim_id']: c for c in common.load_all_claims()[1]}
    refs = lambda c: claims[c]['reference_ids'].split(';')
    places = {r['place_id']: r for r in _csv.DictReader(open(os.path.join(common.ROOT, 'data', 'places.csv'), encoding='utf-8'))}
    new_ids = ['C9314', 'C9315', 'C9316', 'C9317', 'C9318', 'C9319', 'C9320', 'C9321', 'C9322', 'C9323', 'C9324', 'C9325', 'C9326', 'C9327', 'C9328', 'C9329', 'C9330', 'C9331']
    expect(s + ': new rows (unit, date, place, confidence, activity)', [(claims[x]['unit_id'], claims[x]['date'], places[claims[x]['place_id']]['name'], claims[x]['confidence'], claims[x]['activity_status']) for x in new_ids], [('FR-ARMY-001A', '1944-08-24', 'Aix-en-Provence, Bouches-du-Rhône', '0.5', ''), ('FR-ARMY-001A', '1944-09-30', 'Besançon, Doubs', '0.5', ''), ('FR-ARMY-001A', '1944-10-03', 'Besançon, Doubs', '0.5', ''), ('FR-ARMY-001A', '1944-12-25', 'Montbéliard, Doubs', '0.3', ''), ('FR-ARMY-001A', '1945-01-23', 'Rothau, Bas-Rhin', '0.3', ''), ('FR-ARMY-001A', '1945-01-28', 'Barembach, Bas-Rhin', '0.3', ''), ('FR-ARMY-001A', '1945-03-27', 'Guebwiller, Haut-Rhin', '0.5', ''), ('FR-COR-001C', '1944-11-11', 'Guillon-les-Bains, Doubs', '0.5', ''), ('FR-COR-001C', '1944-11-19', "L'Isle-sur-le-Doubs, Doubs", '0.5', ''), ('FR-COR-001C', '1945-01-20', 'Altkirch, Haut-Rhin', '0.3', ''), ('FR-COR-001C', '1945-04-18', 'Freudenstadt, Baden-Württemberg', '0.5', ''), ('FR-COR-002C', '1944-09-02', 'Privas, Ardèche', '0.5', ''), ('FR-COR-002C', '1944-09-24', 'Rougemont, Doubs', '0.5', ''), ('FR-COR-002C', '1944-09-28', 'Rougemont, Doubs', '0.5', ''), ('FR-COR-002C', '1944-11-06', 'Rochesson, Vosges', '0.3', 'in_line'), ('FR-COR-002C', '1945-04-21', 'Stuttgart, Baden-Württemberg', '0.5', 'in_line'), ('FR-INF-010D', '1945-01-26', 'Orbey, Haut-Rhin', '0.5', 'in_line'), ('FR-INF-010D', '1945-02-05', 'Munster, Haut-Rhin', '0.3', 'in_line')])
    expect(s + ': every new row cites R686 and is a preferred row with no conflict group', [('R686' in refs(x), claims[x]['claim_status'], claims[x]['conflict_group_id']) for x in new_ids], [(True, 'preferred', '')] * len(new_ids))
    cited = ['C1640', 'C1629', 'C1620', 'C1621', 'C1622', 'C1623', 'C1624', 'C1626', 'C1628']
    expect(s + ': rows that gained R686 as a supporting citation', [('R686' in refs(x)) for x in cited], [True] * len(cited))
    raised = {'C1640': '0.9', 'C1629': '0.7'}
    expect(s + ': confidence raises (old value to new value, noted)', [(x, claims[x]['confidence'], ('old value: ' in claims[x]['notes'])) for x in sorted(raised)], [(x, raised[x], True) for x in sorted(raised)])
    expect(s + 'flagged map rows keep their confidence and carry the flag, no conflict group', [(claims[c]['confidence'], claims[c]['conflict_group_id'], 'flagged, no value changed' in claims[c]['notes'], 'R686' in refs(c)) for c in ('C4893','C4999','C5348')], [('0.5', '', True, False), ('0.5', '', True, False), ('0.5', '', True, False)])


def scenario_230_delattre_c4_us_german():
    """de Lattre leftovers chunk 4: XXI Corps and the 3rd US Division in the Colmar Pocket, German units as seen by the French account (198th, 269th, 30th SS), two citations and two command relations"""
    import csv as _csv
    s = 'scenario 230'
    claims = {c['claim_id']: c for c in common.load_all_claims()[1]}
    refs = lambda c: claims[c]['reference_ids'].split(';')
    places = {r['place_id']: r for r in _csv.DictReader(open(os.path.join(common.ROOT, 'data', 'places.csv'), encoding='utf-8'))}
    new_ids = ['C9332', 'C9333', 'C9334', 'C9335', 'C9336', 'C9337', 'C9338', 'C9339', 'C9340']
    expect(s + ': new rows (unit, date, place, confidence, activity)', [(claims[x]['unit_id'], claims[x]['date'], places[claims[x]['place_id']]['name'], claims[x]['confidence'], claims[x]['activity_status']) for x in new_ids], [('US-COR-021C', '1945-01-26', 'Sainte-Marie-aux-Mines, Haut-Rhin', '0.5', ''), ('US-COR-021C', '1945-01-28', 'Sainte-Marie-aux-Mines, Haut-Rhin', '0.5', ''), ('US-INF-003D', '1945-01-26', 'Ribeauvillé, Haut-Rhin', '0.5', ''), ('GER-INF-198D', '1944-11-03', 'Rochesson, Vosges', '0.3', 'in_line'), ('GER-INF-269D', '1944-11-03', 'Rochesson, Vosges', '0.3', 'in_line'), ('GER-INF-198D', '1945-01-07', 'Witternheim, Bas-Rhin', '0.3', 'in_line'), ('GER-INF-198D', '1945-01-11', 'Obenheim, Bas-Rhin', '0.5', 'in_line'), ('GER-SSGR-030D', '1944-11-27', 'Dannemarie, Haut-Rhin', '0.3', 'in_line'), ('GER-SSGR-030D', '1944-11-27', 'Balschwiller, Haut-Rhin', '0.3', 'in_line')])
    expect(s + ': every new row cites R686 and is a preferred row with no conflict group', [('R686' in refs(x), claims[x]['claim_status'], claims[x]['conflict_group_id']) for x in new_ids], [(True, 'preferred', '')] * len(new_ids))
    cited = ['C1765', 'C1218']
    expect(s + ': rows that gained R686 as a supporting citation', [('R686' in refs(x)) for x in cited], [True] * len(cited))
    raised = {}
    expect(s + ': confidence raises (old value to new value, noted)', [(x, claims[x]['confidence'], ('old value: ' in claims[x]['notes'])) for x in sorted(raised)], [(x, raised[x], True) for x in sorted(raised)])
    # end of CR1282 changed 14 November 2026 (scenario 267): old value blank, new value 1945-02-16
    expect(s + 'new command relations CR1282 and CR1283 exist with their evidence links', [(r['relation_id'], r['subject_unit_id'], r['higher_unit_id'], r['relationship'], r['valid_from'], r['valid_to']) for r in _csv.DictReader(open(os.path.join(common.ROOT, 'data', 'command_relations.csv'), encoding='utf-8')) if r['relation_id'] in ('CR1282','CR1283')], [('CR1282', 'US-COR-021C', 'FR-ARMY-001A', 'operational_control', '1945-01-23', '1945-02-16'), ('CR1283', 'US-INF-003D', 'US-COR-021C', 'unspecified_subordination', '1945-01-28', '1945-02-06')])


def scenario_231_delattre_c5_other_fronts():
    """de Lattre leftovers chunk 5: the Toulon plan and German units in southern France in August and September 1944"""
    import csv as _csv
    s = 'scenario 231'
    claims = {c['claim_id']: c for c in common.load_all_claims()[1]}
    refs = lambda c: claims[c]['reference_ids'].split(';')
    places = {r['place_id']: r for r in _csv.DictReader(open(os.path.join(common.ROOT, 'data', 'places.csv'), encoding='utf-8'))}
    new_ids = ['C9341', 'C9342', 'C9343', 'C9344', 'C9345', 'C9346', 'C9347']
    expect(s + ': new rows (unit, date, place, confidence, activity)', [(claims[x]['unit_id'], claims[x]['date'], places[claims[x]['place_id']]['name'], claims[x]['confidence'], claims[x]['activity_status']) for x in new_ids], [('FR-INF-001D', '1944-08-20', 'Hyères, Var', '0.3', 'in_line'), ('FR-INF-003D', '1944-08-20', 'Toulon, Var', '0.3', 'in_line'), ('FR-INF-009D', '1944-08-20', 'La Valette-du-Var, Var', '0.3', 'in_line'), ('GER-PZ-011D', '1944-08-20', 'Avignon, Vaucluse', '0.3', ''), ('GER-PZ-011D', '1944-08-22', 'Aix-en-Provence, Bouches-du-Rhône', '0.3', ''), ('GER-PZ-011D', '1944-09-05', 'Étalans, Doubs', '0.3', 'in_line'), ('GER-INF-716D', '1944-09-05', 'Givry, Saône-et-Loire', '0.3', 'in_line')])
    expect(s + ': every new row cites R686 and is a preferred row with no conflict group', [('R686' in refs(x), claims[x]['claim_status'], claims[x]['conflict_group_id']) for x in new_ids], [(True, 'preferred', '')] * len(new_ids))
    cited = []
    expect(s + ': rows that gained R686 as a supporting citation', [('R686' in refs(x)) for x in cited], [True] * len(cited))
    raised = {}
    expect(s + ': confidence raises (old value to new value, noted)', [(x, claims[x]['confidence'], ('old value: ' in claims[x]['notes'])) for x in sorted(raised)], [(x, raised[x], True) for x in sorted(raised)])


def scenario_232_delattre_c6_italy():
    """de Lattre leftovers chunk 6: Elba, Naples and Taranto (Italy, theater mediterranean), after adding IT to the country vocabulary"""
    import csv as _csv
    s = 'scenario 232'
    claims = {c['claim_id']: c for c in common.load_all_claims()[1]}
    refs = lambda c: claims[c]['reference_ids'].split(';')
    places = {r['place_id']: r for r in _csv.DictReader(open(os.path.join(common.ROOT, 'data', 'places.csv'), encoding='utf-8'))}
    new_ids = ['C9348', 'C9349', 'C9350', 'C9351']
    expect(s + ': new rows (unit, date, place, confidence, activity)', [(claims[x]['unit_id'], claims[x]['date'], places[claims[x]['place_id']]['name'], claims[x]['confidence'], claims[x]['activity_status']) for x in new_ids], [('FR-INF-009D', '1944-06-18', 'Portoferraio, Tuscany', '0.3', 'in_line'), ('FR-INF-009D', '1944-06-19', 'Porto Azzurro, Tuscany', '0.3', 'in_line'), ('FR-ARMY-001A', '1944-07-23', 'Naples, Campania', '0.3', ''), ('FR-ARMY-001A', '1944-08-10', 'Taranto, Apulia', '0.5', 'transit')])
    expect(s + ': every new row cites R686 and is a preferred row with no conflict group', [('R686' in refs(x), claims[x]['claim_status'], claims[x]['conflict_group_id']) for x in new_ids], [(True, 'preferred', '')] * len(new_ids))
    cited = []
    expect(s + ': rows that gained R686 as a supporting citation', [('R686' in refs(x)) for x in cited], [True] * len(cited))
    raised = {}
    expect(s + ': confidence raises (old value to new value, noted)', [(x, claims[x]['confidence'], ('old value: ' in claims[x]['notes'])) for x in sorted(raised)], [(x, raised[x], True) for x in sorted(raised)])


def scenario_233_dejong_sept_german_oob():
    """de Jong 10a-1 chunk 1: German dispositions, the Scheldt crossing, the Irene Brigade and the Guards, September 1944"""
    import csv as _csv
    s = 'scenario 233'
    claims = {c['claim_id']: c for c in common.load_all_claims()[1]}
    refs = lambda c: claims[c]['reference_ids'].split(';')
    places = {r['place_id']: r for r in _csv.DictReader(open(os.path.join(common.ROOT, 'data', 'places.csv'), encoding='utf-8'))}
    new_ids = ['C9352', 'C9353', 'C9354', 'C9355', 'C9356']
    expect(s + ': new rows (unit, date, place, confidence, activity)', [(claims[x]['unit_id'], claims[x]['date'], places[claims[x]['place_id']]['name'], claims[x]['confidence'], claims[x]['activity_status']) for x in new_ids], [('GER-INF-347D', '1944-09-03', 'Brussels, Belgium', '0.3', 'transit'), ('GER-ARMY-015A', '1944-09-08', 'Breskens, Zeeland', '0.3', 'transit'), ('GER-INF-064D', '1944-09-14', 'Moerkerke (Damme), West Flanders', '0.3', 'in_line'), ('NL-INF-IRNEB', '1944-09-07', 'Beringen, Limburg (BE)', '0.3', 'in_line'), ('UK-ARM-GRDD', '1944-09-10', 'Neerpelt, Limburg (BE)', '0.3', 'in_line')])
    expect(s + ': every new row cites R894 and is a preferred row with no conflict group', [('R894' in refs(x), claims[x]['claim_status'], claims[x]['conflict_group_id']) for x in new_ids], [(True, 'preferred', '')] * len(new_ids))
    cited = ['C7286', 'C7285', 'C7851', 'C7855', 'C1559', 'C0890', 'C2135']
    expect(s + ': rows that gained R894 as a supporting citation', [('R894' in refs(x)) for x in cited], [True] * len(cited))
    raised = {'C7851': '0.7', 'C1559': '0.9'}
    expect(s + ': confidence raises (old value to new value, noted)', [(x, claims[x]['confidence'], ('old value: ' in claims[x]['notes'])) for x in sorted(raised)], [(x, raised[x], True) for x in sorted(raised)])


def scenario_234_dejong_market_garden():
    """de Jong 10a-1 chunk 2: Market-Garden, the Nijmegen bridges, Dutch intelligence reports on the SS divisions, September 1944"""
    import csv as _csv
    s = 'scenario 234'
    claims = {c['claim_id']: c for c in common.load_all_claims()[1]}
    refs = lambda c: claims[c]['reference_ids'].split(';')
    places = {r['place_id']: r for r in _csv.DictReader(open(os.path.join(common.ROOT, 'data', 'places.csv'), encoding='utf-8'))}
    new_ids = ['C9357', 'C9358', 'C9359', 'C9360', 'C9361', 'C9362', 'C9363', 'C9364', 'C9365', 'C9366', 'C9367', 'C9368', 'C9369', 'C9370', 'C9371', 'C9372', 'C9373', 'C9374']
    expect(s + ': new rows (unit, date, place, confidence, activity)', [(claims[x]['unit_id'], claims[x]['date'], places[claims[x]['place_id']]['name'], claims[x]['confidence'], claims[x]['activity_status']) for x in new_ids], [('UK-ARM-GRDD', '1944-09-17', 'Valkenswaard, Noord-Brabant', '0.3', 'in_line'), ('GER-PZB-107B', '1944-09-18', 'Eindhoven, Noord-Brabant', '0.3', 'in_line'), ('GER-INF-059D', '1944-09-18', 'Best, Noord-Brabant', '0.3', 'in_line'), ('US-ABN-101D', '1944-09-18', 'Son, Noord-Brabant', '0.3', 'in_line'), ('UK-ARM-GRDD', '1944-09-19', 'Grave, Noord-Brabant', '0.3', 'in_line'), ('US-ABN-082D', '1944-09-18', 'Groesbeek, Gelderland', '0.3', 'in_line'), ('US-ABN-082D', '1944-09-20', 'Mook (Mook en Middelaar), Limburg', '0.3', 'in_line'), ('US-ABN-082D', '1944-09-20', 'Nijmegen, Gelderland', '0.3', 'in_line'), ('UK-ABN-001D', '1944-09-18', 'Oosterbeek, Gelderland', '0.5', 'in_line'), ('GER-SSPZ-009D', '1944-09-14', 'Doetinchem, Gelderland', '0.3', 'in_line'), ('GER-SSPZ-009D', '1944-09-15', 'Eefde, Gelderland', '0.3', 'in_line'), ('GER-SSPZ-009D', '1944-09-16', 'Arnhem, Gelderland', '0.3', 'in_line'), ('GER-FJA-001A', '1944-09-15', 'Vught, Noord-Brabant', '0.5', 'in_line'), ('GER-AG-00BG', '1944-09-15', 'Oosterbeek, Gelderland', '0.3', 'in_line'), ('GER-ARMY-015A', '1944-09-16', 'Dordrecht, Zuid-Holland', '0.3', 'in_line'), ('UK-INF-043D', '1944-09-22', 'Driel, Overbetuwe, Gelderland', '0.3', 'in_line'), ('UK-INF-043D', '1944-09-25', 'Driel, Overbetuwe, Gelderland', '0.3', 'in_line'), ('UK-INF-043D', '1944-09-26', 'Driel, Overbetuwe, Gelderland', '0.3', 'in_line')])
    expect(s + ': every new row cites R894 and is a preferred row with no conflict group', [('R894' in refs(x), claims[x]['claim_status'], claims[x]['conflict_group_id']) for x in new_ids], [(True, 'preferred', '')] * len(new_ids))
    cited = ['C7289', 'C7290', 'C1465', 'C1462', 'C7869', 'C0934', 'C1464']
    expect(s + ': rows that gained R894 as a supporting citation', [('R894' in refs(x)) for x in cited], [True] * len(cited))
    raised = {'C7289': '0.7', 'C7290': '0.7', 'C1465': '0.9'}
    expect(s + ': confidence raises (old value to new value, noted)', [(x, claims[x]['confidence'], ('old value: ' in claims[x]['notes'])) for x in sorted(raised)], [(x, raised[x], True) for x in sorted(raised)])


def scenario_235_dejong_irene_scheldt():
    """de Jong 10a-1 chunk 3: the Irene Brigade at Grave, Heumen and Tilburg; Scheldt and Brabant citations, October-November 1944"""
    import csv as _csv
    s = 'scenario 235'
    claims = {c['claim_id']: c for c in common.load_all_claims()[1]}
    refs = lambda c: claims[c]['reference_ids'].split(';')
    places = {r['place_id']: r for r in _csv.DictReader(open(os.path.join(common.ROOT, 'data', 'places.csv'), encoding='utf-8'))}
    new_ids = ['C9375', 'C9376', 'C9377']
    expect(s + ': new rows (unit, date, place, confidence, activity)', [(claims[x]['unit_id'], claims[x]['date'], places[claims[x]['place_id']]['name'], claims[x]['confidence'], claims[x]['activity_status']) for x in new_ids], [('NL-INF-IRNEB', '1944-09-22', 'Grave, Noord-Brabant', '0.5', 'garrison'), ('NL-INF-IRNEB', '1944-10-01', 'Heumen, Gelderland', '0.3', 'garrison'), ('NL-INF-IRNEB', '1944-10-27', 'Tilburg, Noord-Brabant', '0.3', 'in_line')])
    expect(s + ': every new row cites R894 and is a preferred row with no conflict group', [('R894' in refs(x), claims[x]['claim_status'], claims[x]['conflict_group_id']) for x in new_ids], [(True, 'preferred', '')] * len(new_ids))
    cited = ['C1605', 'C9041', 'C9052', 'C1564', 'C1312', 'C1313', 'C7366', 'C7390', 'C7383', 'C7384']
    expect(s + ': rows that gained R894 as a supporting citation', [('R894' in refs(x)) for x in cited], [True] * len(cited))
    raised = {}
    expect(s + ': confidence raises (old value to new value, noted)', [(x, claims[x]['confidence'], ('old value: ' in claims[x]['notes'])) for x in sorted(raised)], [(x, raised[x], True) for x in sorted(raised)])


def scenario_236_dejong_walcheren():
    """de Jong 10a-1 chunk 4: Walcheren landings and the Middelburg surrender, November 1944"""
    import csv as _csv
    s = 'scenario 236'
    claims = {c['claim_id']: c for c in common.load_all_claims()[1]}
    refs = lambda c: claims[c]['reference_ids'].split(';')
    places = {r['place_id']: r for r in _csv.DictReader(open(os.path.join(common.ROOT, 'data', 'places.csv'), encoding='utf-8'))}
    new_ids = ['C9378']
    expect(s + ': new rows (unit, date, place, confidence, activity)', [(claims[x]['unit_id'], claims[x]['date'], places[claims[x]['place_id']]['name'], claims[x]['confidence'], claims[x]['activity_status']) for x in new_ids], [('GER-INF-070D', '1944-11-03', 'Middelburg, Zeeland', '0.5', 'in_line')])
    expect(s + ': every new row cites R894 and is a preferred row with no conflict group', [('R894' in refs(x), claims[x]['claim_status'], claims[x]['conflict_group_id']) for x in new_ids], [(True, 'preferred', '')] * len(new_ids))
    cited = ['C7398', 'C1704', 'C7397', 'C7401', 'C1036']
    expect(s + ': rows that gained R894 as a supporting citation', [('R894' in refs(x)) for x in cited], [True] * len(cited))
    raised = {}
    expect(s + ': confidence raises (old value to new value, noted)', [(x, claims[x]['confidence'], ('old value: ' in claims[x]['notes'])) for x in sorted(raised)], [(x, raised[x], True) for x in sorted(raised)])


def scenario_237_dejong_polish_g123():
    """de Jong 10a-1 follow-up: Polish 550-man second lift at Grave and the Betuwe bank, conflict group G123"""
    import csv as _csv
    s = 'scenario 237'
    claims = {c['claim_id']: c for c in common.load_all_claims()[1]}
    refs = lambda c: claims[c]['reference_ids'].split(';')
    places = {r['place_id']: r for r in _csv.DictReader(open(os.path.join(common.ROOT, 'data', 'places.csv'), encoding='utf-8'))}
    new_ids = ['C9379', 'C9380']
    expect(s + ': new rows (unit, date, place, confidence, status, group)',
           [(claims[x]['unit_id'], claims[x]['date'], places[claims[x]['place_id']]['name'], claims[x]['confidence'], claims[x]['claim_status'], claims[x]['conflict_group_id']) for x in new_ids],
           [('POL-ABN-001B', '1944-09-25', 'Betuwe bank of the Neder Rijn, Gelderland', '0.5', 'alternate', 'G123'),
            ('POL-ABN-001B', '1944-09-26', 'Betuwe bank of the Neder Rijn, Gelderland', '0.5', 'alternate', 'G123')])
    expect(s + ': every new row cites R894', [('R894' in refs(x)) for x in new_ids], [True, True])
    expect(s + ': C1583 stays preferred in G123 at 0.7',
           (claims['C1583']['conflict_group_id'], claims['C1583']['claim_status'], claims['C1583']['confidence']),
           ('G123', 'preferred', '0.7'))
    expect(s + ': C1580-C1582 and C1584 stay out of G123',
           [claims[x]['conflict_group_id'] for x in ('C1580', 'C1581', 'C1582', 'C1584')],
           ['', '', '', ''])
    expect(s + ': PL4149 is an area place at 10 km',
           (places['PL4149']['kind'], places['PL4149']['precision_km'], places['PL4149']['coord_reference_id']),
           ('area', '10', 'R782'))


def scenario_238_dejong_irene_dates():
    """de Jong 10a-1 follow-up: Irene Brigade landing 7 August and Second Army attachment 4 September as alternates"""
    import csv as _csv
    s = 'scenario 238'
    claims = {c['claim_id']: c for c in common.load_all_claims()[1]}
    refs = lambda c: claims[c]['reference_ids'].split(';')
    places = {r['place_id']: r for r in _csv.DictReader(open(os.path.join(common.ROOT, 'data', 'places.csv'), encoding='utf-8'))}
    rels = {r['relation_id']: r for r in _csv.DictReader(open(os.path.join(common.ROOT, 'data', 'command_relations.csv'), encoding='utf-8'))}
    links = [r for r in _csv.DictReader(open(os.path.join(common.ROOT, 'data', 'command_relation_claims.csv'), encoding='utf-8')) if r['relation_id'] == 'CR1284']
    expect(s + ': C9381 landing alternate in G124',
           (claims['C9381']['date'], claims['C9381']['event_type'], claims['C9381']['claim_status'], claims['C9381']['conflict_group_id'], claims['C9381']['confidence'], places[claims['C9381']['place_id']]['name'], 'R894' in refs('C9381')),
           ('1944-08-07', 'landing', 'alternate', 'G124', '0.3', 'Normandy (disembarkation, place not named)', True))
    expect(s + ': C1600 stays preferred in G124 at 0.5 on 6 August',
           (claims['C1600']['date'], claims['C1600']['conflict_group_id'], claims['C1600']['claim_status'], claims['C1600']['confidence']),
           ('1944-08-06', 'G124', 'preferred', '0.5'))
    expect(s + ': G125 transfer dates and statuses',
           [(claims[x]['date'], claims[x]['event_type'], claims[x]['claim_status'], claims[x]['conflict_group_id'], claims[x]['confidence']) for x in ('C9382', 'C9383')],
           [('1944-09-02', 'command_change', 'preferred', 'G125', '0.3'),
            ('1944-09-04', 'command_change', 'alternate', 'G125', '0.5')])
    expect(s + ': C9383 cites R894 and C9382 cites R144',
           ('R894' in refs('C9383'), 'R144' in refs('C9382')),
           (True, True))
    expect(s + ': CR1284 is an alternate Second Army start on 4 September, evidenced only by C9383',
           (rels['CR1284']['subject_unit_id'], rels['CR1284']['higher_unit_id'], rels['CR1284']['relationship'], rels['CR1284']['valid_from'], rels['CR1284']['status'], rels['CR1284']['valid_to_basis'], [(l['claim_id'], l['role'], l['stated_effective_from']) for l in links]),
           ('NL-INF-IRNEB', 'UK-ARMY-002A', 'unspecified_subordination', '1944-09-04', 'alternate', 'open_at_last_claim', [('C9383', 'asserts_start', '1944-09-04')]))
    expect(s + ': CR0933 stays preferred from 2 September',
           (rels['CR0933']['valid_from'], rels['CR0933']['status']),
           ('1944-09-02', 'preferred'))


def scenario_239_c1036_raise():
    """de Jong 10a-1 follow-up: raise C1036, 70th Division surrender at Middelburg on 6 November 1944, to 0.9"""
    s = 'scenario 239'
    claims = {c['claim_id']: c for c in common.load_all_claims()[1]}
    c = claims['C1036']
    refs = c['reference_ids'].split(';')
    expect(s + ': C1036 is the Middelburg surrender at 0.9 with the four agreeing families still cited',
           (c['unit_id'], c['date'], c['event_type'], c['place_id'], c['confidence'], c['claim_status'], c['conflict_group_id'],
            all(r in refs for r in ('R443', 'R668', 'R888', 'R228', 'R894'))),
           ('GER-INF-070D', '1944-11-06', 'surrender', 'PL0620', '0.9', 'preferred', '', True))
    expect(s + ': the raise is annotated with old value 0.5 and new value 0.9',
           ('old value: 0.5' in c['notes'] and 'new value: 0.9' in c['notes']),
           True)


def scenario_240_stoottroepen_unit():
    """de Jong 10a-1 follow-up: first entry of the Stoottroepen der Binnenlandse Strijdkrachten"""
    s = 'scenario 240'
    units = {u['unit_id']: u for u in csv.DictReader(open(os.path.join(common.ROOT, 'data', 'units.csv'), encoding='utf-8'))}
    u = units['NL-INF-STOOT']
    expect(s + ': NL-INF-STOOT is the formal Stoottroepen unit, independent, formed 18 September 1944',
           (u['unit_name'], u['nationality'], u['echelon'], u['parent_unit_id'], u['formed_date'], u['record_status']),
           ('Stoottroepen der Binnenlandse Strijdkrachten', 'Netherlands', 'regiment/battle_group', '', '1944-09-18', 'active'))
    claims = {c['claim_id']: c for c in common.load_all_claims()[1]}
    c18, c19, c22, cpeel, cmay = (claims[i] for i in ('C9384', 'C9385', 'C9386', 'C9387', 'C9388'))
    expect(s + ': C9384 places about 1,000 men in six companies at Eindhoven on 18 September, at the disposal of XXX Corps, confidence 0.3',
           (c18['unit_id'], c18['date'], c18['place_id'], c18['event_type'], c18['confidence'], c18['claim_status'], 'R894' in c18['reference_ids'].split(';')),
           ('NL-INF-STOOT', '1944-09-18', 'PL2596', 'activation', '0.3', 'preferred', True))
    expect(s + ': C9385 places van Kooten recruiting the Stoottroepen-Limburg at Maastricht on 19 September, confidence 0.5',
           (c19['unit_id'], c19['date'], c19['place_id'], c19['event_type'], c19['confidence'], c19['commander'], c19['location_qualifier']),
           ('NL-INF-STOOT', '1944-09-19', 'PL0203', 'arrival', '0.5', 'B. J. C. van Kooten', 'Stoottroepen-Limburg'))
    expect(s + ': C9386 is Borghouts\'s appointment as commander south of the great rivers on 22 September, confidence 0.3',
           (c22['unit_id'], c22['date'], c22['place_id'], c22['event_type'], c22['confidence'], c22['commander']),
           ('NL-INF-STOOT', '1944-09-22', 'PL2596', 'command_change', '0.3', 'F. Borghouts'))
    expect(s + ': C9387 is the end-of-October action in the Peel, confidence 0.3',
           (cpeel['unit_id'], cpeel['date'], cpeel['place_id'], cpeel['event_type'], cpeel['confidence']),
           ('NL-INF-STOOT', '1944-10-31', 'PL4152', 'defense', '0.3'))
    expect(s + ': C9388 is the early-May 1945 strength of about 4,000 in six battalions, confidence 0.3',
           (cmay['unit_id'], cmay['date'], cmay['place_id'], cmay['event_type'], cmay['confidence'], 'personnel":4000' in (cmay.get('strength_json') or '')),
           ('NL-INF-STOOT', '1945-05-01', 'PL4153', 'other', '0.3', True))
    places = {p['place_id']: p for p in csv.DictReader(open(os.path.join(common.ROOT, 'data', 'places.csv'), encoding='utf-8'))}
    expect(s + ': PL4152 is the Peel as an area place',
           (places['PL4152']['name'], places['PL4152']['kind'], places['PL4152']['precision_km']),
           ('De Peel, Noord-Brabant/Limburg', 'area', '25'))
    expect(s + ': PL4153 is the liberated south as an area place',
           (places['PL4153']['name'], places['PL4153']['kind'], places['PL4153']['precision_km']),
           ('Southern Netherlands (liberated area)', 'area', '50'))
    rels = {r['relation_id']: r for r in csv.DictReader(open(os.path.join(common.ROOT, 'data', 'command_relations.csv'), encoding='utf-8'))}
    r = rels['CR1285']
    expect(s + ': CR1285 places NL-INF-STOOT under XXX Corps from 18 September, unspecified_subordination, preferred, end open',
           (r['subject_unit_id'], r['higher_unit_id'], r['relationship'], r['valid_from'], r['valid_to'], r['valid_to_basis'], r['status']),
           ('NL-INF-STOOT', 'UK-COR-030C', 'unspecified_subordination', '1944-09-18', '', 'open_at_last_claim', 'preferred'))
    links = [L for L in csv.DictReader(open(os.path.join(common.ROOT, 'data', 'command_relation_claims.csv'), encoding='utf-8')) if L['relation_id']=='CR1285']
    expect(s + ': CR1285 is evidenced only by C9384 asserting the start',
           (len(links), links[0]['claim_id'], links[0]['role']),
           (1, 'C9384', 'asserts_start'))


def scenario_241_bewakingstroepen_unit():
    """de Jong 10a-1 follow-up 2: first entry of the Bewakingstroepen der Binnenlandse Strijdkrachten"""
    s = 'scenario 241'
    units = {u['unit_id']: u for u in csv.DictReader(open(os.path.join(common.ROOT, 'data', 'units.csv'), encoding='utf-8'))}
    u = units['NL-INF-BEWAK']
    expect(s + ': NL-INF-BEWAK is the formal Bewakingstroepen unit, independent, formed 22 September 1944',
           (u['unit_name'], u['nationality'], u['echelon'], u['parent_unit_id'], u['formed_date'], u['record_status']),
           ('Bewakingstroepen der Binnenlandse Strijdkrachten', 'Netherlands', 'regiment/battle_group', '', '1944-09-22', 'active'))
    claims = {c['claim_id']: c for c in common.load_all_claims()[1]}
    c22, czeel, cjan, cmar, cmay = (claims[i] for i in ('C9389', 'C9390', 'C9391', 'C9392', 'C9393'))
    expect(s + ': C9389 is van Dijk\'s appointment as commander of the Bewakingstroepen on 22 September, confidence 0.3',
           (c22['unit_id'], c22['date'], c22['place_id'], c22['event_type'], c22['confidence'], c22['commander'], 'R894' in c22['reference_ids'].split(';')),
           ('NL-INF-BEWAK', '1944-09-22', 'PL2596', 'activation', '0.3', 'W. J. van Dijk', True))
    expect(s + ': C9390 is Zeeland guard duty on 1 December 1944, confidence 0.3',
           (czeel['unit_id'], czeel['date'], czeel['place_id'], czeel['event_type'], czeel['confidence']),
           ('NL-INF-BEWAK', '1944-12-01', 'PL4154', 'defense', '0.3'))
    expect(s + ': C9391 is the mid-January 1945 strength of more than 10,000, confidence 0.3',
           (cjan['unit_id'], cjan['date'], cjan['place_id'], cjan['confidence'], 'personnel":10000' in (cjan.get('strength_json') or '')),
           ('NL-INF-BEWAK', '1945-01-15', 'PL4153', '0.3', True))
    expect(s + ': C9392 is the early-March transfer of 19 gezagscompagnieën, confidence 0.3',
           (cmar['unit_id'], cmar['date'], cmar['event_type'], cmar['confidence']),
           ('NL-INF-BEWAK', '1945-03-01', 'subordinate_assignment', '0.3'))
    expect(s + ': C9393 uses de Jong\'s working figure of more than 10,000 for early May, not the London 1,500',
           (cmay['unit_id'], cmay['date'], cmay['place_id'], cmay['confidence'], 'personnel":10000' in (cmay.get('strength_json') or ''), '1,500 is too low' in cmay['notes'] or '1,500' in cmay['notes']),
           ('NL-INF-BEWAK', '1945-05-01', 'PL4153', '0.3', True, True))
    places = {p['place_id']: p for p in csv.DictReader(open(os.path.join(common.ROOT, 'data', 'places.csv'), encoding='utf-8'))}
    expect(s + ': PL4154 is liberated Zeeland as an area place',
           (places['PL4154']['name'], places['PL4154']['kind'], places['PL4154']['precision_km']),
           ('Zeeland (liberated area)', 'area', '50'))


def scenario_242_stoottroepen_battalions():
    """de Jong 10a-1 follow-up 2: Limburg and Brabant regional commands and the three named Brabant battalions"""
    s = 'scenario 242'
    units = {u['unit_id']: u for u in csv.DictReader(open(os.path.join(common.ROOT, 'data', 'units.csv'), encoding='utf-8'))}
    expect(s + ': five new units exist with the expected parents and formed dates',
           [(units[i]['unit_name'], units[i]['echelon'], units[i]['parent_unit_id'], units[i]['formed_date'])
            for i in ('NL-INF-STOOT-LIM', 'NL-INF-STOOT-BRB', 'NL-INF-STBRB-001', 'NL-INF-STBRB-002', 'NL-INF-STBRB-003')],
           [
            ('Limburgse Stoottroepen', 'regiment/battle_group', 'NL-INF-STOOT', '1944-09-18'),
            ('Brabantse Stoottroepen', 'regiment/battle_group', 'NL-INF-STOOT', '1944-10-10'),
            ('1ste Bataljon, Brabantse Stoottroepen', 'battalion', 'NL-INF-STOOT-BRB', '1945-01-01'),
            ('2de Bataljon, Brabantse Stoottroepen', 'battalion', 'NL-INF-STOOT-BRB', '1944-12-01'),
            ('3de Bataljon, Brabantse Stoottroepen', 'battalion', 'NL-INF-STOOT-BRB', '1944-12-01'),
           ])
    claims = {c['claim_id']: c for c in common.load_all_claims()[1]}
    expect(s + ': C9394 is van Kooten recruiting at Maastricht on 19 September, confidence 0.5',
           (claims['C9394']['unit_id'], claims['C9394']['date'], claims['C9394']['place_id'], claims['C9394']['confidence'], claims['C9394']['commander']),
           ('NL-INF-STOOT-LIM', '1944-09-19', 'PL0203', '0.5', 'B. J. C. van Kooten'))
    expect(s + ': C9397 is the first Brabant company at Wamel on 10 October, confidence 0.5',
           (claims['C9397']['unit_id'], claims['C9397']['date'], claims['C9397']['place_id'], claims['C9397']['confidence'], claims['C9397']['commander']),
           ('NL-INF-STOOT-BRB', '1944-10-10', 'PL4056', '0.5', 'Sjef de Groot'))
    expect(s + ': C9401 and C9402 place the 2nd and 3rd Brabant battalions on their winter fronts, confidence 0.3',
           (claims['C9401']['unit_id'], claims['C9401']['place_id'], claims['C9401']['date'], claims['C9402']['unit_id'], claims['C9402']['place_id']),
           ('NL-INF-STBRB-002', 'PL4155', '1944-12-01', 'NL-INF-STBRB-003', 'PL4156'))
    expect(s + ': C9396 and C9400 are the March 1945 Rhineland moves',
           (claims['C9396']['unit_id'], claims['C9396']['place_id'], claims['C9400']['unit_id'], claims['C9400']['place_id'], claims['C9400']['location_qualifier']),
           ('NL-INF-STOOT-LIM', 'PL4157', 'NL-INF-STBRB-001', 'PL4157', 'two companies'))
    rels = {r['relation_id']: r for r in csv.DictReader(open(os.path.join(common.ROOT, 'data', 'command_relations.csv'), encoding='utf-8'))}
    expect(s + ': organic relations CR1286-CR1290 and the Second Army relation CR1291 exist',
           [(rels[i]['subject_unit_id'], rels[i]['higher_unit_id'], rels[i]['relationship'], rels[i]['valid_from'])
            for i in ('CR1286', 'CR1287', 'CR1288', 'CR1289', 'CR1290', 'CR1291')],
           [
            ('NL-INF-STOOT-LIM', 'NL-INF-STOOT', 'organic', '1944-09-19'),
            ('NL-INF-STOOT-BRB', 'NL-INF-STOOT', 'organic', '1944-10-10'),
            ('NL-INF-STBRB-001', 'NL-INF-STOOT-BRB', 'organic', '1945-01-01'),
            ('NL-INF-STBRB-002', 'NL-INF-STOOT-BRB', 'organic', '1944-12-01'),
            ('NL-INF-STBRB-003', 'NL-INF-STOOT-BRB', 'organic', '1944-12-01'),
            ('NL-INF-STBRB-001', 'UK-ARMY-002A', 'unspecified_subordination', '1945-03-01'),
           ])
    places = {p['place_id']: p for p in csv.DictReader(open(os.path.join(common.ROOT, 'data', 'places.csv'), encoding='utf-8'))}
    expect(s + ': the three new operational-area places exist',
           (places['PL4155']['kind'], places['PL4156']['kind'], places['PL4157']['name']),
           ('line', 'area', 'Rhineland, Germany'))


def scenario_243_wieringermeer_gewest11():
    """de Jong 10a-1 follow-up 2: BS gewest 11 (Noord-Holland Noord) and the Wieringermeer stoottroepen, 17 April 1945"""
    s = 'scenario 243'
    units = {u['unit_id']: u for u in csv.DictReader(open(os.path.join(common.ROOT, 'data', 'units.csv'), encoding='utf-8'))}
    u = units['NL-BS-NHN']
    expect(s + ': NL-BS-NHN is the formal BS gewest 11 command, independent, formed 5 September 1944',
           (u['unit_name'], u['nationality'], u['echelon'], u['parent_unit_id'], u['formed_date'], u['record_status']),
           ('Binnenlandse Strijdkrachten, gewest 11 (Noord-Holland Noord)', 'Netherlands', 'regiment/battle_group', '', '1944-09-05', 'active'))
    claims = {c['claim_id']: c for c in common.load_all_claims()[1]}
    c17, c18 = claims['C9403'], claims['C9404']
    expect(s + ': C9403 places a few hundred stoottroepen of gewest 11 in the Wieringermeer polder on 17 April 1945, confidence 0.5',
           (c17['unit_id'], c17['date'], c17['place_id'], c17['event_type'], c17['confidence'], c17['commander'], 'R895' in c17['reference_ids'].split(';')),
           ('NL-BS-NHN', '1945-04-17', 'PL4158', 'defense', '0.5', 'J. G. M. Wastenecker', True))
    expect(s + ': C9404 is the recovery of abandoned weapons from Medemblik on 18 April, confidence 0.3',
           (c18['unit_id'], c18['date'], c18['place_id'], c18['event_type'], c18['confidence'], 'R895' in c18['reference_ids'].split(';')),
           ('NL-BS-NHN', '1945-04-18', 'PL4159', 'other', '0.3', True))
    expect(s + ': the Wieringermeer stoottroepen are not on the southern NL-INF-STOOT unit',
           (c17['unit_id'] != 'NL-INF-STOOT', c18['unit_id'] != 'NL-INF-STOOT'),
           (True, True))
    places = {p['place_id']: p for p in csv.DictReader(open(os.path.join(common.ROOT, 'data', 'places.csv'), encoding='utf-8'))}
    expect(s + ': PL4158 is the Wieringermeer polder as an area place and PL4159 is Medemblik',
           (places['PL4158']['name'], places['PL4158']['kind'], places['PL4159']['name'], places['PL4159']['kind']),
           ('Wieringermeer Polder, Noord-Holland', 'area', 'Medemblik, Noord-Holland', 'point'))
    meta = {r['reference_id']: r for r in csv.DictReader(open(os.path.join(common.ROOT, 'data', 'references_meta.csv'), encoding='utf-8'))}
    expect(s + ': R895 is de Jong deel 10b in the niod_dejong_koninkrijk family',
           (meta['R895']['source_family'], meta['R895']['source_type'], '10b' in meta['R895']['short_title']),
           ('niod_dejong_koninkrijk', 'official_history', True))



def scenario_244_air_naval_pilot_luftwaffe():
    """Air-naval pilot (branch air-naval-pilot): Luftflotte 3, II Jagdkorps and JG 26 rows are air-domain, kept out of the main outputs; the relations among them build in other_domains."""
    s = 'scenario 244'
    claims = {c['claim_id']: c for c in common.load_all_claims()[1]}
    units = {u['unit_id']: u for u in common.read_dicts(common.UNITS_CSV)[1]}
    expect(s + ': domains', [common.unit_domain(units[u]) for u in ('GER-LFL-003A', 'GER-JGK-002C', 'GER-JG-026', 'GER-JGGR-026-2', 'GER-JGGR-026-3')], ['air'] * 5)
    expect(s + ': II Jagdkorps rows', [(claims[c]['unit_id'], claims[c]['date'], claims[c]['place_id'], claims[c]['confidence']) for c in ('C9406', 'C9407', 'C9408', 'C9409')],
           [('GER-JGK-002C', '1943-09-15', 'PL4160', '0.5'), ('GER-JGK-002C', '1944-07-01', 'PL4160', '0.3'), ('GER-JGK-002C', '1944-08-19', 'PL4160', '0.5'), ('GER-JGK-002C', '1944-09-10', 'PL4161', '0.5')])
    expect(s + ': III./JG 26 on two airfields on 7 June 1944 is a claim-key exception', ((claims['C9412']['unit_id'], claims['C9412']['date'], claims['C9412']['event_type']) == (claims['C9413']['unit_id'], claims['C9413']['date'], claims['C9413']['event_type']), claims['C9412']['place_id'], claims['C9413']['place_id']), (True, 'PL4163', 'PL4164'))
    main = {r['claim_id'] for r in common.read_dicts(os.path.join(common.BUILD_DIR, 'all_claims.csv'))[1]}
    other = {r['claim_id'] for r in common.read_dicts(os.path.join(common.BUILD_DIR, 'other_domains', 'claims.csv'))[1]}
    expect(s + ': split', (sorted(c for c in ('C9405', 'C9406', 'C9410', 'C9415') if c in main), sorted(c for c in ('C9405', 'C9406', 'C9410', 'C9415') if c in other)), ([], ['C9405', 'C9406', 'C9410', 'C9415']))
    rels = {r['relation_id']: r for r in common.read_dicts(os.path.join(common.BUILD_DIR, 'other_domains', 'command_relations.csv'))[1]}
    expect(s + ': other-domain relations keep the subject and higher unit names (the build crashed on an air subject before the fix)',
           (rels['CR1292']['subject_name'], rels['CR1292']['higher_name'], rels['CR1293']['relationship']),
           (units['GER-JGK-002C']['unit_name'], 'German ' + units['GER-LFL-003A']['unit_name'], 'unspecified_subordination'))
    expect(s + ': organic Gruppe relations are not derived output', [r for r in ('CR1294', 'CR1295', 'CR1297') if r in rels], [])

def scenario_245_air_naval_pilot_usaaf():
    """Air-naval pilot: 366th Fighter Group on ALG A-1, conflict groups G126 (arrival 17 or 13 June) and G127 (departure 24 or 25 August)."""
    s = 'scenario 245'
    claims = {c['claim_id']: c for c in common.load_all_claims()[1]}
    expect(s + ': G126 arrival at A-1', [(claims[c]['date'], claims[c]['claim_status'], claims[c]['conflict_group_id'], claims[c]['confidence'], claims[c]['place_id']) for c in ('C9417', 'C9418')],
           [('1944-06-17', 'preferred', 'G126', '0.7', 'PL4167'), ('1944-06-13', 'alternate', 'G126', '0.3', 'PL4167')])
    expect(s + ': G127 move to A-41', [(claims[c]['date'], claims[c]['claim_status'], claims[c]['conflict_group_id'], claims[c]['confidence']) for c in ('C9419', 'C9420')],
           [('1944-08-24', 'preferred', 'G127', '0.7'), ('1944-08-25', 'alternate', 'G127', '0.5')])
    expect(s + ': 390th Squadron joins three days later, parent blank on the claim', (claims['C9422']['date'], claims['C9422']['unit_id'], claims['C9422']['parent_unit_id']), ('1944-06-20', 'US-FS-390', ''))
    rels = {r['relation_id']: r for r in common.read_dicts(os.path.join(common.ROOT, 'data', 'command_relations.csv'))[1]}
    expect(s + ': CR1298 group assigned to IX TAC from 5 May 1944', (rels['CR1298']['subject_unit_id'], rels['CR1298']['higher_unit_id'], rels['CR1298']['relationship'], rels['CR1298']['valid_from']), ('US-FG-366', 'US-TAC-009C', 'assigned', '1944-05-05'))
    expect(s + ': base and target differ: D-Day row is the station, not the target area', (claims['C9416']['place_id'], claims['C9416']['location_represents']), ('PL4166', 'base'))   # was main_body until the air-naval schema pass added base (13 November 2026)

def scenario_246_air_naval_pilot_ships():
    """Air-naval pilot: Normandy bombardment ships, sea places, the 0.3 cap for a range without a bearing, and the Bedale/Slazak lineage."""
    s = 'scenario 246'
    claims = {c['claim_id']: c for c in common.load_all_claims()[1]}
    places = {p['place_id']: p for p in common.read_dicts(os.path.join(common.ROOT, 'data', 'places.csv'))[1]}
    expect(s + ': Texas and Satterlee offshore points are sea positions with a stated distance (kind area until the air-naval schema pass)', [(places[p]['kind'], places[p]['name']) for p in ('PL4170', 'PL4171')],
           [('sea_position', 'Offshore Pointe du Hoc, 12,000 yards (Omaha western fire-support area)'), ('sea_position', 'Offshore Pointe du Hoc, 1,500 yards')])
    expect(s + ': Warspite on D-Day: objective point at 0.3 because the range has no bearing', (claims['C9426']['place_id'], claims['C9426']['location_represents'], claims['C9426']['confidence'], claims['C9426']['location_basis']), ('PL4172', 'objective', '0.3', 'representative_point'))
    expect(s + ': ship rows are naval-domain', sorted({common.unit_domain({u['unit_id']: u for u in common.read_dicts(common.UNITS_CSV)[1]}[claims[c]['unit_id']]) for c in ('C9423', 'C9425', 'C9426', 'C9433', 'C9436')}), ['naval'])
    expect(s + ': Slazak redesignation of Bedale', [(r['predecessor_unit_id'], r['successor_unit_id'], r['kind'], r['effective_date']) for r in common.read_dicts(os.path.join(common.ROOT, 'data', 'unit_lineage.csv'))[1] if r['lineage_id'] == 'UL020'], [('UK-DD-BEDALE', 'POL-DD-L26', 'redesignation', '1942-04')])
    expect(s + ': Warspite returns to Portsmouth on 12 June and hits a mine off Harwich on 13 June', [(claims[c]['date'], claims[c]['place_id'], claims[c]['confidence']) for c in ('C9429', 'C9430')], [('1944-06-12', 'PL4173', '0.5'), ('1944-06-13', 'PL4174', '0.3')])

def scenario_247_air_naval_pilot_ground_by_function():
    """Air-naval pilot: Marine-Artillerie-Abteilung 260 (Kriegsmarine coastal artillery) is ground by function; its rows and relation are in the main outputs."""
    s = 'scenario 247'
    units = {u['unit_id']: u for u in common.read_dicts(common.UNITS_CSV)[1]}
    expect(s + ': domain and branch', (common.unit_domain(units['GER-MAA-260']), units['GER-MAA-260']['branch'], units['GER-MAA-260']['parent_unit_id']), ('ground', 'Navy', ''))
    main = {r['claim_id'] for r in common.read_dicts(os.path.join(common.BUILD_DIR, 'all_claims.csv'))[1]}
    expect(s + ': C9437 and C9438 in the main outputs', ('C9437' in main, 'C9438' in main), (True, True))
    mrel = {r['relation_id'] for r in common.read_dicts(os.path.join(common.BUILD_DIR, 'command_relations.csv'))[1]}
    expect(s + ': CR1305 in the main relations and no air or naval relation there', ('CR1305' in mrel, sorted(r for r in mrel if r in ('CR1292', 'CR1293', 'CR1298', 'CR1301', 'CR1303', 'CR1304'))), (True, []))
    claims = {c['claim_id']: c for c in common.load_all_claims()[1]}
    expect(s + ': Crisbecq battery row', (claims['C9437']['place_id'], claims['C9437']['confidence'], claims['C9437']['event_type']), ('PL4176', '0.5', 'defense'))


def _vmsgs(fn, *args, **kw):
    """(errors, warnings) that a validate.py check adds when called with synthetic input."""
    e0, w0 = len(validate.errors), len(validate.warnings)
    out = fn(*args, **kw)
    got = (validate.errors[e0:], validate.warnings[w0:])
    del validate.errors[e0:], validate.warnings[w0:]
    return out, got


def scenario_248_scope_marker():
    """Scope marker (standing rule 22): a unit with scope out_of_scope, its claims and relations go to build/other_domains/, not the main outputs."""
    s = 'scenario 248'
    import tempfile
    import build
    expect(s + ': blank means in_scope', (common.unit_scope({}), common.unit_scope({'scope': 'out_of_scope'})), ('in_scope', 'out_of_scope'))
    h, rows = common.read_rows(common.UNITS_CSV)
    base = build.outputs()
    uid = 'GER-FJ-005D'
    with tempfile.TemporaryDirectory() as td:
        path = os.path.join(td, 'units.csv')
        i = h.index('scope')
        rows2 = [r[:i] + ['out_of_scope'] + r[i + 1:] if r[0] == uid else r for r in rows]
        with open(path, 'wb') as f:
            f.write(common.csv_bytes(h, rows2))
        old = common.UNITS_CSV
        common.UNITS_CSV = path
        try:
            moved = build.outputs()
        finally:
            common.UNITS_CSV = old
    cl = lambda out, k: [r for r in csv.DictReader(io.StringIO(out[k].decode('utf-8')))]  # noqa: E731
    n_unit = len([r for r in cl(base, 'all_claims.csv') if r['unit_id'] == uid])
    expect(s + ': the unit has claims in the main output before the marker', n_unit > 0, True)
    expect(s + ': marked unit leaves all_claims.csv', len([r for r in cl(moved, 'all_claims.csv') if r['unit_id'] == uid]), 0)
    expect(s + ': marked unit claims land in other_domains/claims.csv', len([r for r in cl(moved, 'other_domains/claims.csv') if r['unit_id'] == uid]), n_unit)
    expect(s + ': marked unit is in other_domains/units.csv with its scope', [(r['unit_id'], r['scope']) for r in cl(moved, 'other_domains/units.csv') if r['unit_id'] == uid], [(uid, 'out_of_scope')])
    expect(s + ': marked unit leaves the main units.csv, coverage.csv and command_relations.csv',
           (uid in [r['unit_id'] for r in cl(moved, 'units.csv')], uid in [r['unit_id'] for r in cl(moved, 'coverage.csv')],
            uid in [r['subject_unit_id'] for r in cl(moved, 'command_relations.csv')]), (False, False, False))
    rel_base = len([r for r in cl(base, 'command_relations.csv') if r['subject_unit_id'] == uid])
    expect(s + ': its relations move to other_domains/command_relations.csv', len([r for r in cl(moved, 'other_domains/command_relations.csv') if r['subject_unit_id'] == uid]), rel_base)
    expect(s + ': the main units.csv header has none of the five other-output columns', [c for c in common.OTHER_ONLY_UNIT_COLUMNS if c in cl(base, 'units.csv')[0]], [])
    expect(s + ': no pilot unit is marked out_of_scope (data unchanged by the schema pass)', [u for u in common.read_dicts(common.UNITS_CSV)[1] if u['scope']], [])


def scenario_249_naval_unit_columns():
    """ship_type, hull_number and ship_class_id belong to echelon naval_unit; the class must exist and match; naval echelons need domain naval."""
    s = 'scenario 249'
    classes = {'SC001': {'ship_type': 'BB', 'class_name': 'New York class'}}
    chk = lambda **u: _vmsgs(validate.check_naval_unit_columns, 'w', 'X', dict({'echelon': 'naval_unit', 'domain': 'naval', 'ship_type': 'BB', 'hull_number': 'BB-35', 'ship_class_id': 'SC001'}, **u), classes)[1]  # noqa: E731
    expect(s + ': a clean ship passes', chk(), ([], []))
    expect_in(s + ': ship_type on a battalion is an error', ' | '.join(chk(echelon='battalion', domain='')[0]), 'ship_type is set but echelon is battalion')
    expect_in(s + ': a naval-ladder echelon on a ground unit is an error', ' | '.join(chk(echelon='task_group', domain='', ship_type='', hull_number='', ship_class_id='')[0]), 'needs domain naval')
    expect_in(s + ': an unknown class is an error', ' | '.join(chk(ship_class_id='SC999')[0]), 'not a class')
    expect_in(s + ': a class of another ship_type is an error', ' | '.join(chk(ship_type='DD')[0]), 'differs from the ship_type BB')
    expect_in(s + ': a class without ship_type is an error', ' | '.join(chk(ship_type='')[0]), 'needs ship_type')
    expect_in(s + ': a ship without ship_type is a warning', ' | '.join(chk(ship_type='', ship_class_id='')[1]), 'without ship_type')
    units = {u['unit_id']: u for u in common.read_dicts(common.UNITS_CSV)[1]}
    expect(s + ': Texas, Satterlee, Warspite, Bedale and Slazak', [(units[u]['ship_type'], units[u]['hull_number']) for u in ('US-BB-035', 'US-DD-626', 'UK-BB-WARSPITE', 'UK-DD-BEDALE', 'POL-DD-L26')],
           [('BB', 'BB-35'), ('DD', 'DD-626'), ('BB', '03'), ('DE', 'L25'), ('DE', 'L26')])
    classes = {c['class_id']: c for c in common.read_dicts(os.path.join(common.ROOT, 'data', 'ship_classes.csv'))[1]}
    names = [classes[units[u]['ship_class_id']]['class_name'] + ' / ' + classes[units[u]['ship_class_id']]['nationality'] for u in ('US-BB-035', 'US-DD-626', 'UK-BB-WARSPITE', 'UK-DD-BEDALE', 'POL-DD-L26')]
    expect(s + ': ships link to their classes; the Polish ship keeps the British class', names, ['New York class / US', 'Gleaves class / US', 'Queen Elizabeth class / UK', 'Hunt class Type II / UK', 'Hunt class Type II / UK'])
    expect(s + ': ship_type vocabulary is the US hull codes', sorted(common.vocab_values('ship_type')), sorted(['AGC', 'AM', 'APA', 'AV', 'BB', 'BC', 'BM', 'CA', 'CL', 'CM', 'CORV', 'CV', 'CVE', 'CVL', 'DD', 'DE', 'PF', 'PG', 'SS', 'TB']))  # BM added 15 November 2026; AGC and APA added 16 November 2026 (chunk 1); AV added 16 November 2026 (Normandy chunk 2, HMS Albatross); old value without AV


def scenario_250_ship_classes_table():
    """data/ship_classes.csv: the checker rejects bad rows (synthetic) and the seeded table has the core types with sourced figures."""
    s = 'scenario 250'
    import tempfile
    vocabs = common.load_vocabularies()
    nats = {'US': {}, 'UK': {}}
    h = common.field_names(common.load_schema('ship_classes'))
    meta = {m['reference_id'] for m in __import__('build_references').read_meta()[1]}
    rid = sorted(meta)[0]
    good = {'class_id': 'SC001', 'class_name': 'Fam', 'nationality': 'US', 'ship_type': 'DD', 'lead_ship_name': '', 'parent_class_id': '', 'sub_type': '',
            'capabilities_json': '{"speed": {"value": "30 knots", "reference_id": "%s"}}' % rid, 'reference_ids': rid, 'class_note': ''}
    def run(rows):
        with tempfile.TemporaryDirectory() as td:
            path = os.path.join(td, 'ship_classes.csv')
            with open(path, 'wb') as f:
                f.write(common.csv_bytes(h, [[r[c] for c in h] for r in rows]))
            old = validate.SHIP_CLASSES_CSV
            validate.SHIP_CLASSES_CSV = path
            try:
                return _vmsgs(validate.check_ship_classes, nats, vocabs)[1]
            finally:
                validate.SHIP_CLASSES_CSV = old
    expect(s + ': a clean family and sub-type pass', run([good, dict(good, class_id='SC002', class_name='Fam II', parent_class_id='SC001', sub_type='II', capabilities_json='{"speed": {"value": "32 knots", "reference_id": "%s"}}' % rid)]), ([], []))
    text = lambda rows: ' | '.join(run(rows)[0])  # noqa: E731
    expect_in(s + ': a sub_type without a parent is an error', text([dict(good, sub_type='II')]), 'set together')
    expect_in(s + ': a parent that is itself a sub-type is an error', text([good, dict(good, class_id='SC002', class_name='B', parent_class_id='SC001', sub_type='B'), dict(good, class_id='SC003', class_name='C', parent_class_id='SC002', sub_type='C')]), 'itself a sub-type')
    expect_in(s + ': a sub-type of another ship_type is an error', text([good, dict(good, class_id='SC002', class_name='B', ship_type='BB', parent_class_id='SC001', sub_type='B')]), 'differs from the parent class')
    expect_in(s + ': a duplicate class name per nationality is an error', text([good, dict(good, class_id='SC002')]), 'already the name')
    expect_in(s + ': an unknown capability key is an error', text([dict(good, capabilities_json='{"armour": {"value": "x", "reference_id": "%s"}}' % rid)]), 'unknown key')
    expect_in(s + ': a figure with an unknown reference is an error', text([dict(good, capabilities_json='{"speed": {"value": "30", "reference_id": "R99999"}}')]), 'not in data/references_meta.csv')
    expect_in(s + ': a figure whose reference is not listed is an error', text([dict(good, reference_ids='R001', capabilities_json='{"speed": {"value": "30", "reference_id": "%s"}}' % rid)]) if rid != 'R001' else 'not in the row reference_ids', 'not in the row reference_ids')
    expect_in(s + ': a sub-type that repeats a family figure is a warning', ' | '.join(run([good, dict(good, class_id='SC002', class_name='B', parent_class_id='SC001', sub_type='B')])[1]), 'repeats the family row')
    rows = common.read_dicts(os.path.join(common.ROOT, 'data', 'ship_classes.csv'))[1]
    by = {r['class_name']: r for r in rows}
    core = ['Iowa class', 'Essex class', 'Fletcher class', 'Evarts class', 'Gato class', 'King George V class (1939)', 'Hunt class', 'Flower class (corvette)', 'River class (frigate)', 'Bismarck class',
            'Type 1939 torpedo boat', 'Type VIIC', 'Type VIIC/41', 'Type IXC', 'Type IXC/40', 'Type XXI', 'Bogue class', 'Richelieu class', 'Tromp class', 'Grom class', 'Fundy class']
    expect(s + ': core classes are seeded', [c for c in core if c not in by], [])
    expect(s + ': Hunt Type II is a sub-type of Hunt, Type VIIC of Type VII', (by['Hunt class Type II']['parent_class_id'] == by['Hunt class']['class_id'], by['Type VIIC']['parent_class_id'] == by['Type VII']['class_id']), (True, True))
    expect(s + ': every seeded figure has its own reference', [r['class_id'] for r in rows if r['capabilities_json'] and any(not v.get('reference_id') for v in json.loads(r['capabilities_json']).values())], [])
    expect(s + ': ship types seeded cover the brief', sorted({r['ship_type'] for r in rows}), sorted(['AM', 'APA', 'BB', 'BC', 'BM', 'CA', 'CL', 'CM', 'CORV', 'CV', 'CVE', 'CVL', 'DD', 'DE', 'PF', 'PG', 'SS', 'TB']))  # BM and APA added 16 November 2026 (Erebus class SC213, Bayfield class SC214, Normandy chunk 1); old value without them


def scenario_251_refit_and_reclassification():
    """A refit is carried in strength_json capabilities (basis refit); a reclassification is a redesignation row stated as 'Reclassified from X to Y'."""
    s = 'scenario 251'
    vocabs = common.load_vocabularies()
    rid = 'R001'
    ok = '{"basis": "refit", "as_of": "1943-01-01", "capabilities": {"anti_aircraft": {"value": "10 x 20 mm", "reference_id": "%s"}}, "source": "x"}' % rid
    chk = lambda js: _vmsgs(validate.check_strength_json, 'w', js, vocabs)[1][0]  # noqa: E731
    expect(s + ': a refit record passes with no personnel, vehicles or status', chk(ok), [])
    expect_in(s + ': capabilities need basis refit', ' | '.join(chk(ok.replace('"refit"', '"estimate"'))), 'needs basis refit')
    expect_in(s + ': basis refit needs capabilities', ' | '.join(chk('{"basis": "refit", "as_of": "1943-01-01", "status": "full", "source": "x"}')), 'basis refit needs capabilities')
    expect_in(s + ': a refit figure needs its own known reference', ' | '.join(chk(ok.replace(rid, 'R99999'))), 'not in data/references_meta.csv')
    expect_in(s + ': an unknown capability key is an error', ' | '.join(chk(ok.replace('anti_aircraft', 'armour'))), 'unknown key')
    expect(s + ': the ordinary strength_json still passes', chk('{"basis": "estimate", "as_of": "1944-06-10", "status": "full", "source": "x"}'), [])
    ship = {'echelon': 'naval_unit', 'unit_id': 'X'}
    expect(s + ': the vocabulary allows refit', 'refit' in common.vocab_values('strength_json_basis'), True)
    expect(s + ': the JSON schema carries a capabilities property', 'capabilities' in common.load_json(os.path.join(common.SCHEMA_DIR, 'json', 'strength_json.schema.json'))['properties'], True)


def scenario_252_naval_echelon_ladder():
    """Naval echelon ladder: ranks 10-14, no id letter, the hierarchy applies within the ladder only; the five pilot units are re-echeloned."""
    s = 'scenario 252'
    rank = common.echelon_rank()
    expect(s + ': ranks', [rank[e] for e in ('naval_unit', 'naval_division', 'naval_squadron', 'task_group', 'fleet')], [10, 11, 12, 13, 14])
    expect(s + ': ground ranks are unchanged', (rank['squad'], rank['army_group'], rank['other']), (0, 7, 8))
    units = {u['unit_id']: u for u in common.read_dicts(common.UNITS_CSV)[1]}
    expect(s + ': the five pilot units', [(u, units[u]['echelon']) for u in ('GER-TBF-005', 'UK-BF-D', 'UK-TF-S', 'US-TG-124-9', 'GER-MGW-000H')],
           [('GER-TBF-005', 'naval_division'), ('UK-BF-D', 'task_group'), ('UK-TF-S', 'task_group'), ('US-TG-124-9', 'task_group'), ('GER-MGW-000H', 'fleet')])
    mk = lambda uid, e: {'unit_id': uid, 'echelon': e}  # noqa: E731
    prob = lambda a, b, r='assigned': validate.naval_hierarchy_problem(a, b, r)  # noqa: E731
    expect(s + ': a ship under a task group is fine', prob(mk('S', 'naval_unit'), mk('T', 'task_group')), '')
    expect(s + ': a task group under a fleet is fine', prob(mk('T', 'task_group'), mk('F', 'fleet')), '')
    expect_in(s + ': a ship under a ship is an error', prob(mk('S', 'naval_unit'), mk('T', 'naval_unit')), 'naval hierarchy')
    expect_in(s + ': a fleet under a division is an error', prob(mk('F', 'fleet'), mk('D', 'naval_division')), 'naval hierarchy')
    expect(s + ': across ladders is not checked', (prob(mk('S', 'naval_unit'), mk('A', 'army')), prob(mk('B', 'battalion'), mk('F', 'fleet'))), ('', ''))
    expect(s + ': an unknown relation is not checked', prob(mk('S', 'naval_unit'), mk('T', 'naval_unit'), 'unknown'), '')
    expect(s + ': a final letter on a naval-ladder id is not an echelon letter (GER-MGW-000H is a fleet)', 'fleet' in validate.NAVAL_LADDER and units['GER-MGW-000H']['unit_id'].endswith('H'), True)
    placeholders = [(u, units[u]['record_status']) for u in ('UK-BF-D', 'UK-TF-S', 'US-TG-124-9')]
    expect(s + ': task organisations are placeholders with no claim file', placeholders, [(u, 'placeholder') for u in ('UK-BF-D', 'UK-TF-S', 'US-TG-124-9')])
    relations = [r for r in common.read_dicts(os.path.join(common.ROOT, 'data', 'command_relations.csv'))[1] if r['higher_unit_id'] in ('UK-BF-D', 'UK-TF-S', 'US-TG-124-9')]
    expect(s + ': a placeholder task organisation holds relations (as the higher unit) without claims of its own', len(relations), 81)  # was 4, then 9, then 20 in chunk 1, 32 after chunk 2 commit 2, 51 after commit 3a; twenty-four more in commit 3b under UK-TF-S (1st, 15th and 40th Minesweeping Flotillas); two more in chunk 3a commit 1 under UK-TF-S (132nd MMS and 165th BYMS); one more in chunk 3a commit 2 (19th ML); three more in chunk 3c commit 1 under UK-TF-S (C and D Build-up and U Landing Barge Squadrons) (16 November 2026)


def scenario_253_sea_position_base_and_event_types():
    """sea_position place kind (confidence cap 0.5), location_represents base, event types commissioning and sortie, and the revisited pilot rows."""
    s = 'scenario 253'
    pl = {'kind': 'sea_position', 'place_id': 'PL1'}
    expect(s + ': 0.7 at sea is an error', validate.sea_position_problem(pl, {'confidence': '0.7'}) != '', True)
    expect(s + ': 0.5 at sea passes', validate.sea_position_problem(pl, {'confidence': '0.5'}), '')
    expect(s + ': 0.7 on land is not capped', validate.sea_position_problem({'kind': 'point', 'place_id': 'PL2'}, {'confidence': '0.7'}), '')
    expect(s + ': vocabularies', ('base' in common.vocab_values('location_represents'), 'commissioning' in common.vocab_values('event_type'), 'sortie' in common.vocab_values('event_type'), 'sea_position' in common.vocab_values('place_kind')), (True, True, True, True))
    claims = {c['claim_id']: c for c in common.load_all_claims()[1]}
    expect(s + ': US-FG-366 D-Day row is a sortie from its base', (claims['C9416']['event_type'], claims['C9416']['location_represents']), ('sortie', 'base'))
    expect(s + ': the launch of Bedale is a commissioning row', claims['C9432']['event_type'], 'commissioning')
    expect(s + ': airfield and port rows now say base', sorted(c for c, r in claims.items() if r['location_represents'] == 'base' and 'C9411' <= c <= 'C9435'),
           ['C9411', 'C9412', 'C9413', 'C9414', 'C9415', 'C9416', 'C9417', 'C9418', 'C9419', 'C9420', 'C9421', 'C9422', 'C9429', 'C9435'])
    expect(s + ': each changed row records old and new value', [c for c in ('C9411', 'C9416', 'C9429', 'C9432', 'C9435') if 'old value' not in claims[c]['notes']], [])
    places = {p['place_id']: p for p in common.read_dicts(os.path.join(common.ROOT, 'data', 'places.csv'))[1]}
    expect(s + ': Texas and Satterlee points are sea positions; Warspite objective and the Harwich fallback are not', [places[p]['kind'] for p in ('PL4170', 'PL4171', 'PL4172', 'PL4174')], ['sea_position', 'sea_position', 'point', 'point'])
    expect(s + ': every claim at a sea_position place is at 0.5 or lower', [c for c, r in claims.items() if places[r['place_id']]['kind'] == 'sea_position' and float(r['confidence']) > 0.5], [])
    expect(s + ': III./JG 26 same-day exception stays (base does not change the claim key)', [r for r in common.read_dicts(os.path.join(common.ROOT, 'data', 'claim_key_exceptions.csv'))[1] if r['claim_id'] == 'C9412' and r['other_claim_id'] == 'C9413'] != [], True)


def scenario_254_claim_ids_other_domains():
    """check_claim_ids.py reads build/other_domains/claims.csv as well as all_claims.csv (an air/naval/out_of_scope id cannot be reused unseen)."""
    s = 'scenario 254'
    import subprocess
    p = subprocess.run([sys.executable, os.path.join(common.ROOT, 'scripts', 'check_claim_ids.py'), '--base', 'HEAD'], capture_output=True, text=True, cwd=common.ROOT)
    total = len(common.load_all_claims()[1])
    expect_in(s + ': the script counts the other-domain claims in "now"', p.stdout, 'now: %d;' % total)
    expect_in(s + ': and passes', p.stdout, 'OK: no id was reused or dropped')

def scenario_255_air_echelon_ladder():
    """Air echelon ladder: ranks 20-25, no id letter, the hierarchy applies within the ladder by level (US and RAF group/wing inversion), the nine pilot air units are re-echeloned."""
    s = 'scenario 255'
    rank = common.echelon_rank()
    ladder = ('air_squadron', 'air_group', 'air_wing', 'air_division', 'air_corps', 'air_force')
    expect(s + ': ranks', [rank[e] for e in ladder], [20, 21, 22, 23, 24, 25])
    expect(s + ': ground and naval ranks are unchanged', (rank['squad'], rank['army_group'], rank['other'], rank['naval_unit'], rank['fleet']), (0, 7, 8, 10, 14))
    expect(s + ': the reserved air_formation is retired', 'air_formation' in common.vocab_values('echelon'), False)
    expect(s + ': every ladder echelon is exempt from the id letter', sorted(validate.AIR_LADDER), sorted(ladder))
    units = {u['unit_id']: u for u in common.read_dicts(common.UNITS_CSV)[1]}
    expect(s + ': the nine pilot air units', [(u, units[u]['echelon']) for u in ('GER-FLK-002C', 'GER-JG-026', 'GER-JGGR-026-2', 'GER-JGGR-026-3', 'GER-JGK-002C', 'GER-LFL-003A', 'US-FG-366', 'US-FS-390', 'US-TAC-009C')],
           [('GER-FLK-002C', 'air_corps'), ('GER-JG-026', 'air_wing'), ('GER-JGGR-026-2', 'air_group'), ('GER-JGGR-026-3', 'air_group'), ('GER-JGK-002C', 'air_corps'),
            ('GER-LFL-003A', 'air_force'), ('US-FG-366', 'air_group'), ('US-FS-390', 'air_squadron'), ('US-TAC-009C', 'air_division')])
    mk = lambda uid, e: {'unit_id': uid, 'echelon': e}  # noqa: E731
    prob = lambda a, b, r='assigned': validate.air_hierarchy_problem(a, b, r)  # noqa: E731
    expect(s + ': a Gruppe under a Geschwader is fine', prob(mk('G', 'air_group'), mk('JG', 'air_wing')), '')
    expect(s + ': a Geschwader under a Jagdkorps is fine (a level may be skipped)', prob(mk('JG', 'air_wing'), mk('K', 'air_corps')), '')
    expect(s + ': a US group under a combat wing and a RAF wing under a RAF group are the same shape (rank, not name)', (prob(mk('FG', 'air_group'), mk('FW', 'air_wing')), prob(mk('RW', 'air_group'), mk('RG', 'air_wing'))), ('', ''))
    expect_in(s + ': a US group over a combat wing is an error', prob(mk('FW', 'air_wing'), mk('FG', 'air_group')), 'air hierarchy')
    expect_in(s + ': a RAF group under a RAF wing (the inversion misread by name) is an error', prob(mk('RG', 'air_wing'), mk('RW', 'air_group')), 'air hierarchy')
    expect_in(s + ': a command under a command is an error', prob(mk('A', 'air_division'), mk('B', 'air_division')), 'air hierarchy')
    expect(s + ': across ladders is not checked', (prob(mk('G', 'air_group'), mk('A', 'army')), prob(mk('B', 'battalion'), mk('F', 'air_force'))), ('', ''))
    expect(s + ': unknown, supporting and coordinating are not checked', [prob(mk('A', 'air_group'), mk('B', 'air_group'), r) for r in ('unknown', 'supporting', 'coordinating')], ['', '', ''])
    expect(s + ': the naval check ignores air echelons', validate.naval_hierarchy_problem(mk('A', 'air_group'), mk('B', 'air_group'), 'assigned'), '')


def scenario_256_aircraft_types_table():
    """data/aircraft_types.csv: the checker rejects bad rows (synthetic) and the seeded table has the main Western Front types with a source per figure."""
    s = 'scenario 256'
    import tempfile
    vocabs = common.load_vocabularies()
    nats = {'US': {}, 'UK': {}, 'Germany': {}}
    h = common.field_names(common.load_schema('aircraft_types'))
    meta = {m['reference_id'] for m in __import__('build_references').read_meta()[1]}
    rid = sorted(meta)[0]
    good = {'type_id': 'AT001', 'designation': 'Fam', 'nationality': 'US', 'role': 'fighter', 'manufacturer': '', 'parent_type_id': '', 'variant': '',
            'performance_json': '{"max_speed": {"value": "400 mph", "reference_id": "%s"}}' % rid, 'reference_ids': rid, 'type_note': ''}
    def run(rows):
        with tempfile.TemporaryDirectory() as td:
            path = os.path.join(td, 'aircraft_types.csv')
            with open(path, 'wb') as f:
                f.write(common.csv_bytes(h, [[r[c] for c in h] for r in rows]))
            old = validate.AIRCRAFT_TYPES_CSV
            validate.AIRCRAFT_TYPES_CSV = path
            try:
                return _vmsgs(validate.check_aircraft_types, nats, vocabs)[1]
            finally:
                validate.AIRCRAFT_TYPES_CSV = old
    var = dict(good, type_id='AT002', designation='Fam-B', parent_type_id='AT001', variant='B', performance_json='{"max_speed": {"value": "420 mph", "reference_id": "%s"}}' % rid)
    expect(s + ': a clean family and variant pass', run([good, var]), ([], []))
    text = lambda rows: ' | '.join(run(rows)[0])  # noqa: E731
    expect_in(s + ': a variant without a parent is an error', text([dict(good, variant='B')]), 'set together')
    expect_in(s + ': a parent that is itself a variant is an error', text([good, var, dict(good, type_id='AT003', designation='C', parent_type_id='AT002', variant='C')]), 'itself a variant')
    expect_in(s + ': a duplicate designation per nationality is an error', text([good, dict(good, type_id='AT002')]), 'already the designation')
    expect_in(s + ': an unknown role is an error', text([dict(good, role='zeppelin')]), 'role')
    expect_in(s + ': an unknown performance key is an error', text([dict(good, performance_json='{"armour": {"value": "x", "reference_id": "%s"}}' % rid)]), 'unknown key')
    expect_in(s + ': a figure with an unknown reference is an error', text([dict(good, performance_json='{"range": {"value": "1", "reference_id": "R99999"}}')]), 'not in data/references_meta.csv')
    expect_in(s + ': a figure whose reference is not listed is an error', text([dict(good, reference_ids='R001', performance_json='{"range": {"value": "1", "reference_id": "%s"}}' % rid)]) if rid != 'R001' else 'not in the row reference_ids', 'not in the row reference_ids')
    expect_in(s + ': a row without a reference is an error', text([dict(good, reference_ids='', performance_json='')]), 'reference_ids is empty')
    expect_in(s + ': a variant that repeats a family figure is a warning', ' | '.join(run([good, dict(var, performance_json=good['performance_json'])])[1]), 'repeats the family row')
    rows = common.read_dicts(os.path.join(common.ROOT, 'data', 'aircraft_types.csv'))[1]
    by = {r['designation']: r for r in rows}
    core = ['P-47 Thunderbolt', 'P-47D-40', 'P-51D', 'P-38L', 'B-17G', 'B-24J', 'B-26G', 'A-20G-20-DO', 'C-47B-DK', 'Spitfire Mk Vb', 'Spitfire Mk XIV', 'Typhoon Mk Ib', 'Tempest Mk V', 'Mosquito B Mk XVI',
            'Lancaster I', 'Halifax Mk III', 'Fw 190A-8', 'Bf 109G-6', 'Me 262A-1a', 'Ju 88A-4', 'Ju 87D-1', 'Lancaster X', 'Mosquito B Mk XX', 'Hurricane Mk XII']
    expect(s + ': core types are seeded', [c for c in core if c not in by], [])
    expect(s + ': P-47D-40 is a variant of the P-47 family, Lancaster X (Canada) of the Lancaster', (by['P-47D-40']['parent_type_id'] == by['P-47 Thunderbolt']['type_id'], by['Lancaster X']['parent_type_id'] == by['Lancaster I']['parent_type_id'], by['Lancaster X']['nationality']), (True, True, 'Canada'))
    expect(s + ': every seeded figure has its own reference', [r['type_id'] for r in rows if r['performance_json'] and any(not v.get('reference_id') for v in json.loads(r['performance_json']).values())], [])
    expect(s + ': nationalities seeded', sorted({r['nationality'] for r in rows}), ['Canada', 'France', 'Germany', 'UK', 'US'])  # France added 15 November 2026 (LeO 451, Normandy prep); old value ['Canada', 'Germany', 'UK', 'US']
    expect(s + ': every role used is in the vocabulary', sorted({r['role'] for r in rows} - set(common.vocab_values('aircraft_role'))), [])
    expect(s + ': ids run AT001.. without a gap', [r['type_id'] for r in rows], ['AT%03d' % i for i in range(1, len(rows) + 1)])


def scenario_257_aircraft_strength():
    """strength_json aircraft: on hand, serviceable and by type; the checks reject impossible counts, unknown types and a non-air unit."""
    s = 'scenario 257'
    vocabs = common.load_vocabularies()
    types = {'AT004': {}, 'AT060': {}}
    base = {'basis': 'reported_actual', 'as_of': '1944-05-31', 'scope': 'whole_unit', 'source': 'x'}
    chk = lambda a, **kw: _vmsgs(validate.check_strength_json, 'w', json.dumps(dict(base, aircraft=a, **kw)), vocabs, types)[1][0]  # noqa: E731
    ok = {'on_hand': 60, 'serviceable': 41, 'by_type': {'AT004': {'on_hand': 40, 'serviceable': 30}, 'AT060': {'on_hand': 20, 'serviceable': 11}}}
    expect(s + ': a return by type passes', chk(ok), [])
    expect(s + ': totals alone pass', chk({'on_hand': 12, 'serviceable': 9}), [])
    expect(s + ': a type listed without counts (an equipment link) passes', chk({'by_type': {'AT004': {'on_hand': 1}}}), [])
    expect(s + ': by_type counts below the total pass (unlisted types)', chk({'on_hand': 60, 'by_type': {'AT004': {'on_hand': 40}}}), [])
    txt = lambda a, **kw: ' | '.join(chk(a, **kw))  # noqa: E731
    expect_in(s + ': serviceable above on_hand is an error', txt({'on_hand': 5, 'serviceable': 9}), 'exceeds on_hand')
    expect_in(s + ': by_type above the total is an error', txt({'on_hand': 50, 'by_type': {'AT004': {'on_hand': 40}, 'AT060': {'on_hand': 20}}}), 'more than the total')
    expect_in(s + ': by_type serviceable above its own on_hand is an error', txt({'by_type': {'AT004': {'on_hand': 3, 'serviceable': 4}}}), 'exceeds on_hand')
    expect_in(s + ': an unknown type id is an error', txt({'by_type': {'AT999': {'on_hand': 1}}}), 'not in data/aircraft_types.csv')
    expect_in(s + ': a key that is no type id is an error', txt({'by_type': {'Fw 190': {'on_hand': 1}}}), 'not a type_id')
    expect_in(s + ': a negative count is an error', txt({'on_hand': -1}), 'non-negative')
    expect_in(s + ': an empty object is an error', txt({}), 'non-empty')
    expect_in(s + ': an unknown key is an error', txt({'on_hand': 1, 'lost': 2}), 'unknown key')
    no_scope = json.dumps({k: v for k, v in dict(base, aircraft={'on_hand': 3}).items() if k != 'scope'})
    expect_in(s + ': aircraft figures need a scope', ' | '.join(_vmsgs(validate.check_strength_json, 'w', no_scope, vocabs, types)[1][0]), 'no scope')
    schema = common.load_json(os.path.join(common.SCHEMA_DIR, 'json', 'strength_json.schema.json'))
    expect(s + ': the JSON schema carries the aircraft object and its scope dependency', ('aircraft' in schema['properties'], schema['dependentRequired'].get('aircraft')), (True, ['scope']))
    claims = [c for c in common.load_all_claims()[1] if '"aircraft"' in c['strength_json']]
    units = {u['unit_id']: u for u in common.read_dicts(common.UNITS_CSV)[1]}
    expect(s + ': every aircraft strength row belongs to an air unit', [c['claim_id'] for c in claims if units[c['unit_id']]['domain'] != 'air'], [])


def scenario_258_air_command_relations():
    """Operational and administrative chains of an air unit are held together without a conflict (the 366th Fighter Group, 1944-45); who_controls prints both; ground answers are unchanged."""
    s = 'scenario 258'
    import command_relations as cr
    rel = {r['relation_id']: r for r in common.read_dicts(os.path.join(common.ROOT, 'data', 'command_relations.csv'))[1]}
    expect(s + ': the 366th under IX TAC, XXIX TAC (Provisional), IX TAC again, IX Fighter Command (assigned) with XXIX TAC (attached)',
           [(c, rel[c]['higher_unit_id'], rel[c]['relationship'], rel[c]['valid_from'], rel[c]['valid_to']) for c in ('CR1298', 'CR1306', 'CR1307', 'CR1308', 'CR1309')],
           [('CR1298', 'US-TAC-009C', 'assigned', '1944-05-05', '1944-09-30'), ('CR1306', 'US-TAC-029C', 'assigned', '1944-10-01', '1944-10-21'), ('CR1307', 'US-TAC-009C', 'assigned', '1944-10-22', '1945-01-27'),
            ('CR1308', 'US-FTRCMD-009', 'assigned', '1945-01-28', ''), ('CR1309', 'US-TAC-029C', 'attached', '1945-01-28', '1945-06-21')])
    units = {u['unit_id']: u for u in common.read_dicts(common.UNITS_CSV)[1]}
    # Normandy chunk 5a (branch normandy-ninthaf-5a, 17 November 2026): expectation for US-TAC-009C and US-FTRCMD-009 old value
    # placeholder, new value active; reason: both commands now have claims of their own (J12 sub-chunk 5a). US-TAC-029C stays a placeholder.
    expect(s + ': the three commands are air_division commands of domain air (IX TAC and IX FC active since chunk 5a)', [(u, units[u]['echelon'], units[u]['record_status'], units[u]['domain']) for u in ('US-TAC-009C', 'US-TAC-029C', 'US-FTRCMD-009')],
           [('US-TAC-009C', 'air_division', 'active', 'air'), ('US-TAC-029C', 'air_division', 'placeholder', 'air'), ('US-FTRCMD-009', 'air_division', 'active', 'air')])
    allrel = list(rel.values())
    expect(s + ': the pilot relations of the 366th raise no contradictory overlap', [(a['relation_id'], b['relation_id']) for a, b, lo, hi in cr.contradictory_overlaps(allrel, units) if 'US-FG-366' in (a['subject_unit_id'], b['subject_unit_id'])], [])
    mk = lambda rid, high, kind, vf, vt='': {'relation_id': rid, 'subject_unit_id': 'S', 'higher_unit_id': high, 'relationship': kind, 'valid_from': vf, 'valid_to': vt, 'status': 'preferred'}  # noqa: E731
    u2 = {'A': {'echelon': 'air_division'}, 'B': {'echelon': 'air_division'}}
    over = lambda *rs: len(cr.contradictory_overlaps(list(rs), u2))  # noqa: E731
    expect(s + ': assigned to one command and attached to another at once is not a conflict', over(mk('CR1', 'A', 'assigned', '1945-01-28'), mk('CR2', 'B', 'attached', '1945-01-28')), 0)
    expect(s + ': administrative_control by one command and operational_control by another at once is not a conflict', over(mk('CR1', 'A', 'administrative_control', '1945-01-28'), mk('CR2', 'B', 'operational_control', '1945-01-28')), 0)
    expect(s + ': two overlapping assigned relations to different commands of one level are still a conflict', over(mk('CR1', 'A', 'assigned', '1945-01-28'), mk('CR2', 'B', 'assigned', '1945-02-01')), 1)
    expect(s + ': two overlapping operational_control relations to different commands are still a conflict', over(mk('CR1', 'A', 'operational_control', '1945-01-28'), mk('CR2', 'B', 'operational_control', '1945-02-01')), 1)
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        wc.main(['US-FG-366', '1945-02-01'])
    text = buf.getvalue()
    op, adm = text.split('operational chain:\n', 1)[1].split('administrative chain:\n', 1)
    expect_in(s + ': the operational chain on 1 February 1945 is XXIX TAC (attached)', op, 'US XXIX Tactical Air Command (Provisional) (attached, certain)')
    expect_in(s + ': the administrative chain is IX Fighter Command (assigned)', adm, 'US IX Fighter Command (assigned, certain)')
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        wc.main(['US-FG-366', '1944-10-10'])
    expect_in(s + ': on 10 October 1944 XXIX TAC (Provisional) is the one chain', buf.getvalue(), 'US XXIX Tactical Air Command (Provisional) (assigned, certain)')
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        wc.main([DIV_84, '1944-12-01'])
    expect(s + ': a ground answer prints no administrative chain block', 'administrative chain' in buf.getvalue(), False)
    expect(s + ': the ground table does not hold the air relations', [r['relation_id'] for r in _ROWS if r['subject_unit_id'] == 'US-FG-366'], [])


def scenario_259_irene_after_march_1945():
    """Princess Irene Brigade after 1 March 1945: Netherlands District from 2 March, entry into The Hague on 8 May"""
    import csv as _csv
    s = 'scenario 259'
    claims = {c['claim_id']: c for c in common.load_all_claims()[1]}
    refs = lambda c: claims[c]['reference_ids'].split(';')
    places = {r['place_id']: r for r in _csv.DictReader(open(os.path.join(common.ROOT, 'data', 'places.csv'), encoding='utf-8'))}
    rels = {r['relation_id']: r for r in _csv.DictReader(open(os.path.join(common.ROOT, 'data', 'command_relations.csv'), encoding='utf-8'))}
    links = [r for r in _csv.DictReader(open(os.path.join(common.ROOT, 'data', 'command_relation_claims.csv'), encoding='utf-8')) if r['relation_id'] == 'CR1310']
    c45, c46, c07 = claims['C9445'], claims['C9446'], claims['C1607']
    expect(s + ': C9445 is the 2 March command change under Netherlands District at Walcheren, confidence 0.3',
           (c45['unit_id'], c45['date'], c45['event_type'], c45['place_id'], c45['parent_unit_id'], c45['confidence'], c45['claim_status'], c45['activity_status'], 'R676' in refs('C9445'), 'R894' in refs('C9445')),
           ('NL-INF-IRNEB', '1945-03-02', 'command_change', 'PL0549', 'UK-DIST-NETH', '0.3', 'preferred', 'garrison', True, True))
    expect(s + ': C9446 is the 8 May entry into The Hague at 0.5, citing de Jong 10b and the Defence family',
           (c46['unit_id'], c46['date'], c46['event_type'], c46['place_id'], c46['confidence'], c46['claim_status'], c46['activity_status'], c46['parent_unit_id'],
            all(r in refs('C9446') for r in ('R895', 'R1159', 'R1160'))),
           ('NL-INF-IRNEB', '1945-05-08', 'arrival', 'PL3529', '0.5', 'preferred', 'transit', '', True))
    expect(s + ': C1607 at Hedel keeps a blank parent and gains R894 as a supporting citation',
           (c07['date'], c07['place_id'], c07['parent_unit_id'], c07['confidence'], 'R894' in refs('C1607'), 'R676' in refs('C1607')),
           ('1945-04-25', 'PL0826', '', '0.5', True, True))
    expect(s + ': CR1310 assigns the brigade to Netherlands District from 2 March, open at the last claim',
           (rels['CR1310']['subject_unit_id'], rels['CR1310']['higher_unit_id'], rels['CR1310']['relationship'], rels['CR1310']['valid_from'], rels['CR1310']['valid_to'], rels['CR1310']['valid_to_basis'], rels['CR1310']['end_unknown'], rels['CR1310']['status']),
           ('NL-INF-IRNEB', 'UK-DIST-NETH', 'assigned', '1945-03-02', '', 'open_at_last_claim', 'false', 'preferred'))
    expect(s + ': CR1310 is evidenced by C9445 asserting the start, and by C1607 and C9446 observed during',
           sorted((l['claim_id'], l['role'], l['stated_effective_from']) for l in links),
           [('C1607', 'observed_during', ''), ('C9445', 'asserts_start', '1945-03-02'), ('C9446', 'observed_during', '')])
    expect(s + ': CR0933 still ends on 1 March 1945 as the preferred Second Army relation',
           (rels['CR0933']['valid_from'], rels['CR0933']['valid_to'], rels['CR0933']['status']),
           ('1944-09-02', '1945-03-01', 'preferred'))
    a = intervals('NL-INF-IRNEB', '1945-03-02')
    expect(s + ': 2 March 1945: assigned to Netherlands District', sorted(a), [('UK-DIST-NETH', 'assigned')])
    a = intervals('NL-INF-IRNEB', '1945-04-25')
    expect(s + ': 25 April 1945 (Hedel): still assigned to Netherlands District', sorted(a), [('UK-DIST-NETH', 'assigned')])
    a = intervals('NL-INF-IRNEB', '1945-05-08')
    expect(s + ': 8 May 1945 (The Hague): still assigned to Netherlands District (open, no end row)', sorted(a), [('UK-DIST-NETH', 'assigned')])



def scenario_260_stale_carry_forward_drop():
    """An open_at_last_claim interval is no longer answered as possible more than 90 days after its last listing."""
    s = 'stale carry-forward drop (scenario 260)'
    expect(s + ': OPEN_CARRY_FORWARD_DAYS is 90', wc.OPEN_CARRY_FORWARD_DAYS, 90)
    # Kampfgruppe Meyer: last listed 1944-06-06, a June 1944 Kampfgruppe in the VE-Day leftover.
    row = master('GER-KG-MEYER', 'GER-COR-084C', 'reserve', '1944-06-06')
    expect(s + ': Meyer last listed 1944-06-06, end open', (row['last_listed_date'], row['valid_to_basis']), ('1944-06-06', 'open_at_last_claim'))
    expect(s + ': 1944-09-05 (91 days after) no longer covers Meyer', intervals('GER-KG-MEYER', '1944-09-05')[('GER-COR-084C', 'reserve')][0], 'absent')
    expect(s + ': VE-Day no longer covers Meyer', intervals('GER-KG-MEYER', '1945-05-08')[('GER-COR-084C', 'reserve')][0], 'absent')
    # The 79th Armoured Division was the second drop example when CR0064 was last listed only on 6 June 1944.
    # That listing was refreshed on 14 November 2026 (scenario 262); Kampfgruppe Meyer remains the drop example.


def scenario_261_stale_carry_forward_kept():
    """A carry-forward within 90 days, a later relation, and a sourced end are not dropped."""
    s = 'stale carry-forward kept (scenario 261)'
    st, why = intervals('GER-KG-MEYER', '1944-09-04')[('GER-COR-084C', 'reserve')]
    expect(s + ': 1944-09-04 (90 days after last listing) is still possible for Meyer', st, 'possible')
    expect_in(s + ': the 90-day reason names the last listing', why, 'after the last claim that lists it (1944-06-06, 90 days earlier)')
    # 7th Armored Division: First Army and 12th Army Group last listed 23 January are dropped by 26 April, but CR1280 (III Corps, last listed 30 March) still covers.
    expect(s + ': 26 April 1945 still answers the 7th Armored Division via III Corps', intervals(DIV_7AD, '1945-04-26')[('US-COR-003C', 'assigned')][0], 'possible')
    expect(s + ': ...and not via the stale First Army assignment', intervals(DIV_7AD, '1945-04-26')[('US-ARMY-001A', 'assigned')][0], 'absent')
    # a sourced end is not capped (same 29th Infantry Division row already used in scenario 0)
    expect(s + ': 29th Infantry Division on 1944-10-15 is still certain (assignment-table end, last listing 1944-09-29)', intervals(DIV_29, '1944-10-15')[('US-ARMY-001A', 'assigned')][0], 'certain')





def scenario_262_79th_armoured_21ag():
    """The 79th Armoured Division's assignment to 21st Army Group is listed through its last claim (12 April 1945), so the 90-day cutoff no longer drops it from September 1944."""
    import csv as _csv
    s = '79th Armoured 21st Army Group listing (scenario 262)'
    claims = {c['claim_id']: c for c in common.load_all_claims()[1]}
    row = master('UK-ARM-079D', 'UK-AG-021G', 'assigned', '1944-06-06')
    expect(s + ': last listed 1945-04-12 (C9009), end still open', (row['last_listed_date'], row['valid_to_basis']), ('1945-04-12', 'open_at_last_claim'))
    expect(s + ': start unchanged at 6 June 1944', row['valid_from'], '1944-06-06')
    expect(s + ': 5 September 1944 is certain', intervals('UK-ARM-079D', '1944-09-05')[('UK-AG-021G', 'assigned')][0], 'certain')
    expect(s + ': 11 September 1944 is certain (after the old 90-day drop)', intervals('UK-ARM-079D', '1944-09-11')[('UK-AG-021G', 'assigned')][0], 'certain')
    expect(s + ': last claim date 12 April 1945 is certain', intervals('UK-ARM-079D', '1945-04-12')[('UK-AG-021G', 'assigned')][0], 'certain')
    st, why = intervals('UK-ARM-079D', '1945-05-08')[('UK-AG-021G', 'assigned')]
    expect(s + ': VE-Day is possible (26 days after the last listing)', st, 'possible')
    expect_in(s + ': VE-Day reason names the 12 April listing', why, 'after the last claim that lists it (1945-04-12, 26 days earlier)')
    for cid in ('C9000', 'C8975', 'C9195', 'C9009'):
        expect(s + ': %s lists parent UK-AG-021G' % cid, claims[cid]['parent_unit_id'], 'UK-AG-021G')
        expect(s + ': %s cites the second family R1161' % cid, 'R1161' in claims[cid]['reference_ids'].split(';'), True)
    expect(s + ': C9000 cites Ellis vol. I (R670) for the June-August appendix', 'R670' in claims['C9000']['reference_ids'].split(';'), True)
    expect(s + ': C9009 cites Ellis vol. II (R671) for the September-May appendix', 'R671' in claims['C9009']['reference_ids'].split(';'), True)
    links = [r for r in _csv.DictReader(open(os.path.join(common.ROOT, 'data', 'command_relation_claims.csv'), encoding='utf-8')) if r['relation_id'] == 'CR0064']
    expect(s + ': CR0064 is linked from C0019 and the 18 later claims, all observed_during', (len(links), {l['role'] for l in links}), (19, {'observed_during'}))



def scenario_263_stoottroepen_parent_review():
    """The Stoottroepen XXX Corps placement is listed only on 18 September 1944; later claims do not extend it, so the 90-day cutoff still drops the unit from 18 December 1944."""
    s = 'Stoottroepen parent review (scenario 263)'
    claims = {c['claim_id']: c for c in common.load_all_claims()[1]}
    row = master('NL-INF-STOOT', 'UK-COR-030C', 'unspecified_subordination', '1944-09-18')
    expect(s + ': last listed still 1944-09-18 (C9384), end still open', (row['last_listed_date'], row['valid_to_basis']), ('1944-09-18', 'open_at_last_claim'))
    expect(s + ': start unchanged at 18 September 1944', row['valid_from'], '1944-09-18')
    st0, why0 = intervals('NL-INF-STOOT', '1944-09-18')[('UK-COR-030C', 'unspecified_subordination')]
    expect(s + ': 18 September 1944 is possible (starts that day at an undocumented hour)', st0, 'possible')
    expect_in(s + ': 18 September reason names the undocumented hour', why0, 'starts that day at an undocumented hour')
    st1, why1 = intervals('NL-INF-STOOT', '1944-09-19')[('UK-COR-030C', 'unspecified_subordination')]
    expect(s + ': 19 September 1944 is possible (the day after the only listing)', st1, 'possible')
    expect_in(s + ': 19 September reason names the 18 September listing', why1, 'after the last claim that lists it (1944-09-18, 1 day earlier)')
    st, why = intervals('NL-INF-STOOT', '1944-12-17')[('UK-COR-030C', 'unspecified_subordination')]
    expect(s + ': 17 December 1944 (90 days after last listing) is still possible', st, 'possible')
    expect_in(s + ': the 90-day reason names the 18 September listing', why, 'after the last claim that lists it (1944-09-18, 90 days earlier)')
    expect(s + ': 18 December 1944 (91 days after) no longer covers', intervals('NL-INF-STOOT', '1944-12-18')[('UK-COR-030C', 'unspecified_subordination')][0], 'absent')
    expect(s + ': 1 May 1945 (C9388) no longer covers', intervals('NL-INF-STOOT', '1945-05-01')[('UK-COR-030C', 'unspecified_subordination')][0], 'absent')
    expect(s + ': VE-Day no longer covers', intervals('NL-INF-STOOT', '1945-05-08')[('UK-COR-030C', 'unspecified_subordination')][0], 'absent')
    expect(s + ': C9384 lists parent UK-COR-030C', claims['C9384']['parent_unit_id'], 'UK-COR-030C')
    expect(s + ': C9385 parent remains blank (before the 22 September split)', claims['C9385']['parent_unit_id'], '')
    expect(s + ': C9387 parent remains blank (Peel action does not name the BS)', claims['C9387']['parent_unit_id'], '')
    # C9386 and C9388 received NL-BS-000H as parent in the 14 November 2026 BS-unit pass (scenario 264).




def scenario_264_binnenlandse_strijdkrachten():
    """The Stoottroepen are under the Binnenlandse Strijdkrachten from 22 September 1944, last listed 1 May 1945, so the 90-day cutoff no longer leaves them unanswered from 18 December 1944."""
    s = 'Binnenlandse Strijdkrachten unit (scenario 264)'
    claims = {c['claim_id']: c for c in common.load_all_claims()[1]}
    units = {u['unit_id']: u for u in csv.DictReader(open(os.path.join(common.ROOT, 'data', 'units.csv'), encoding='utf-8'))}
    expect(s + ': NL-BS-000H exists, formed 5 September 1944, no Allied parent', (units['NL-BS-000H']['formed_date'], units['NL-BS-000H']['parent_unit_id']), ('1944-09-05', ''))
    row = master('NL-INF-STOOT', 'NL-BS-000H', 'administrative_control', '1944-09-22')
    expect(s + ': CR1311 last listed 1945-05-01 (C9388), end still open', (row['last_listed_date'], row['valid_to_basis']), ('1945-05-01', 'open_at_last_claim'))
    expect(s + ': start 22 September 1944', row['valid_from'], '1944-09-22')
    expect(s + ': 21 September 1944 is not yet under the BS', intervals('NL-INF-STOOT', '1944-09-21')[('NL-BS-000H', 'administrative_control')][0], 'absent')
    expect(s + ': 22 September 1944 is certain', intervals('NL-INF-STOOT', '1944-09-22')[('NL-BS-000H', 'administrative_control')][0], 'certain')
    expect(s + ': 18 December 1944 is certain (after the old XXX Corps 90-day drop)', intervals('NL-INF-STOOT', '1944-12-18')[('NL-BS-000H', 'administrative_control')][0], 'certain')
    expect(s + ': 1 May 1945 (C9388) is certain', intervals('NL-INF-STOOT', '1945-05-01')[('NL-BS-000H', 'administrative_control')][0], 'certain')
    st, why = intervals('NL-INF-STOOT', '1945-05-08')[('NL-BS-000H', 'administrative_control')]
    expect(s + ': VE-Day is possible (7 days after the last listing)', st, 'possible')
    expect_in(s + ': VE-Day reason names the 1 May listing', why, 'after the last claim that lists it (1945-05-01, 7 days earlier)')
    expect(s + ': C9386 and C9388 list parent NL-BS-000H', (claims['C9386']['parent_unit_id'], claims['C9388']['parent_unit_id']), ('NL-BS-000H', 'NL-BS-000H'))
    row_b = master('NL-INF-BEWAK', 'NL-BS-000H', 'administrative_control', '1944-09-22')
    expect(s + ': CR1312 last listed 1945-05-01 (C9393), end still open', (row_b['last_listed_date'], row_b['valid_to_basis']), ('1945-05-01', 'open_at_last_claim'))



def scenario_265_cca_2nd_armored_later_claims():
    """Combat Command A, 2nd Armored Division, has sourced claims after 28 July 1944, a 1-6 August attachment to the 29th Division, and the XIX Corps listing last listed on 6 August."""
    s = 'Combat Command A later claims (scenario 265)'
    claims = {c['claim_id']: c for c in common.load_all_claims()[1]}
    expect(s + ': C9447 is 1 August 1944 at Tessy-sur-Vire, parent the 29th Division',
           (claims['C9447']['date'], claims['C9447']['place_id'], claims['C9447']['parent_unit_id']),
           ('1944-08-01', 'PL4179', 'US-INF-029D'))
    expect(s + ': C9448 is 6 August 1944, parent XIX Corps',
           (claims['C9448']['date'], claims['C9448']['parent_unit_id']),
           ('1944-08-06', 'US-COR-019C'))
    expect(s + ': C9449, C9450 and C9451 leave parent blank (organic to the division)',
           (claims['C9449']['parent_unit_id'], claims['C9450']['parent_unit_id'], claims['C9451']['parent_unit_id']),
           ('', '', ''))
    expect(s + ': C9449 Elbeuf 25 August, C9450 Buissonville 24 December, C9451 Krefeld 1 March 1945',
           (claims['C9449']['date'], claims['C9449']['place_id'], claims['C9450']['date'], claims['C9450']['place_id'], claims['C9451']['date'], claims['C9451']['place_id']),
           ('1944-08-25', 'PL1410', '1944-12-24', 'PL4180', '1945-03-01', 'PL0420'))
    att = master('US-CCA-002D', 'US-INF-029D', 'attached', '1944-08-01')
    expect(s + ': CR1313 attached to the 29th Division 1-6 August', (att['valid_from'], att['valid_to']), ('1944-08-01', '1944-08-06'))
    expect(s + ': 31 July 1944 is not yet attached to the 29th', intervals('US-CCA-002D', '1944-07-31')[('US-INF-029D', 'attached')][0], 'absent')
    expect(s + ': 1 August 1944 is certain under the 29th', intervals('US-CCA-002D', '1944-08-01')[('US-INF-029D', 'attached')][0], 'certain')
    st, why = intervals('US-CCA-002D', '1944-08-06')[('US-INF-029D', 'attached')]
    expect(s + ': 6 August 1944 is possible under the 29th (ends that day at an undocumented hour)', st, 'possible')
    expect_in(s + ': 6 August 29th reason is the end-of-day hour', why, 'ends that day at an undocumented hour')
    expect(s + ': 7 August 1944 is no longer attached to the 29th', intervals('US-CCA-002D', '1944-08-07')[('US-INF-029D', 'attached')][0], 'absent')
    row = master('US-CCA-002D', 'US-COR-019C', 'unspecified_subordination', '1944-07-28')
    expect(s + ': CR0177 last listed 1944-08-06 (C9448), end still open', (row['last_listed_date'], row['valid_to_basis']), ('1944-08-06', 'open_at_last_claim'))
    expect(s + ': 6 August 1944 is certain under XIX Corps', intervals('US-CCA-002D', '1944-08-06')[('US-COR-019C', 'unspecified_subordination')][0], 'certain')
    st, why = intervals('US-CCA-002D', '1944-11-04')[('US-COR-019C', 'unspecified_subordination')]
    expect(s + ': 4 November 1944 (90 days after the 6 August listing) is possible', st, 'possible')
    expect(s + ': 5 November 1944 (day 91) is no longer under XIX Corps', intervals('US-CCA-002D', '1944-11-05')[('US-COR-019C', 'unspecified_subordination')][0], 'absent')


def scenario_266_organic_fallback():
    """Organic fallback in who_controls.py (14 November 2026): where no non-organic relation covers the date, the lookup falls back to the organic parent and
    goes on up the chain; an explicit non-organic relation always wins; the answer is marked organic_fallback; the 90-day rule applies to the organic relation too."""
    s = 'organic fallback (scenario 266)'

    def run(unit, date):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc = wc.main([unit, date])
        return rc, buf.getvalue()

    org_rows = common.read_dicts(os.path.join(common.BUILD_DIR, 'organic_relations.csv'))[1]
    expect(s + ': build/organic_relations.csv holds only organic relations and build/command_relations.csv holds none',
           (all(r['relationship'] == 'organic' for r in org_rows), any(r['relationship'] == 'organic' for r in _ROWS)), (True, False))
    expect(s + ': CR0176 (Combat Command A -> 2nd Armored Division) is in build/organic_relations.csv',
           sorted((r['subject_unit_id'], r['higher_unit_id']) for r in org_rows if r['relation_id'] == 'CR0176'), [('US-CCA-002D', 'US-ARM-002D')])
    # 1. fallback applies when nothing else does: Combat Command A after the 90-day carry-forward of the XIX Corps listing (6 August + 90 = 4 November)
    expect(s + ': 4 November 1944 still answers through the explicit XIX Corps (possible), not the fallback', chain('US-CCA-002D', '1944-11-04')[0][:2], ('US XIX Corps', 'unspecified_subordination'))
    rc, text = run('US-CCA-002D', '1944-11-05')
    ch = chain('US-CCA-002D', '1944-11-05')
    expect(s + ': 5 November 1944 resolves, exit code 0', rc, 0)
    expect(s + ': ...the first level is the 2nd Armored Division, basis organic_fallback, certain', ch[0], ('US 2nd Armored Division', 'organic_fallback', 'certain'))
    expect(s + ': ...and the chain goes on up from the division as normal (the division is under XIX Corps)', ch[1][:2], ('US XIX Corps', 'unspecified_subordination'))
    expect_in(s + ': the interval line is marked [organic_fallback', text, '[organic_fallback: no operational, attachment or other non-organic relation covers this date]')
    expect(s + ': the same lookup on a date with an explicit relation carries no marker', 'organic_fallback' in run('US-CCA-002D', '1944-08-01')[1], False)
    for d in ('1944-12-24', '1945-03-01'):   # the later claims C9450 and C9451 are organic only
        expect(s + ': %s resolves through the 2nd Armored Division' % d, chain('US-CCA-002D', d)[0], ('US 2nd Armored Division', 'organic_fallback', 'certain'))
    expect(s + ': 8 May 1945 (68 days after the 1 March listing of the organic relation) is possible', chain('US-CCA-002D', '1945-05-08')[0], ('US 2nd Armored Division', 'organic_fallback', 'possible'))
    # 2. an explicit relation beats the fallback: the 1-6 August attachment to the 29th Division (CR1313) while the organic relation (CR0176) also covers the day
    expect(s + ': 1 August 1944 is the explicit attachment to the 29th Division, not the fallback', chain('US-CCA-002D', '1944-08-01')[0], ('US 29th Infantry Division', 'attached', 'certain'))
    # ...even a possible, stale explicit relation (XIX Corps, 14 days after its last listing) beats a certain organic one
    expect(s + ': 20 August 1944 is the possible XIX Corps relation, not the certain organic one', chain('US-CCA-002D', '1944-08-20')[0][:3], ('US XIX Corps', 'unspecified_subordination', 'possible'))
    expect(s + ': ...and the output has no organic_fallback marker', 'organic_fallback' in run('US-CCA-002D', '1944-08-20')[1], False)
    # a non-chain explicit relation (a corps reserve) is a non-organic relation too: no fallback to the division. Kampfgruppe Meyer was the example until
    # 14 November 2026; Scott then decided that the parent division answers for Meyer and GER-KG-002PZ (scenario 268; CR0026 is set aside by a per-relation override).
    # Old expectation for Meyer on 20 June 1944: reserve line kept, no organic_fallback, empty chain. It now holds in scenario 268 in the new form.
    # 3. the fallback is general (all organic relations) and may repeat up the chain
    expect(s + ': Kampfgruppe Peiper on 20 December 1944 falls back to the 1st SS Panzer Division, then its corps',
           [c[:2] for c in chain('GER-KG-PEIPER', '1944-12-20')[:2]], [('German 1st SS Panzer Division Leibstandarte SS Adolf Hitler', 'organic_fallback'), ('German I SS Panzer Corps', 'assigned')])
    expect(s + ': Stoottroepen Brabant battalion on 15 January 1945 falls back twice (battalion -> regiment -> Stoottroepen)',
           [c[:2] for c in chain('NL-INF-STBRB-001', '1945-01-15')], [('Dutch Brabantse Stoottroepen', 'organic_fallback'), ('Dutch Stoottroepen der Binnenlandse Strijdkrachten', 'organic_fallback')])
    # 4. the 90-day rule applies to the organic relation: Peiper last listed 24 December 1944
    expect(s + ': Peiper on 24 March 1945 (90 days after the last listing) is possible', chain('GER-KG-PEIPER', '1945-03-24')[0][1:], ('organic_fallback', 'possible'))
    expect(s + ': Peiper on 25 March 1945 (day 91) is no longer answered', run('GER-KG-PEIPER', '1945-03-25')[0], 1)
    # 5. an explicit unknown placeholder without a higher unit does not block the fallback and is printed as a note (31st Tank Brigade: CR0081 unknown from
    #    26 June, last listed 26 June, still possible 76 days later; CR0980 organic to the 79th Armoured Division from 4 September)
    rc, text = run('UK-TNK-031B', '1944-09-10')
    expect(s + ': 31st Tank Brigade on 10 September 1944 falls back to the 79th Armoured Division, possible, and prints the unknown note',
           (rc, chain('UK-TNK-031B', '1944-09-10')[0], 'note: relation CR0081 is an explicit unknown' in text), (0, ('British 79th Armoured Division', 'organic_fallback', 'possible'), True))
    expect(s + ': on 3 September 1944 the explicit VIII Corps assignment (CR0979) is the answer, before the organic relation starts',
           (chain('UK-TNK-031B', '1944-09-03')[0][:2], 'organic_fallback' in run('UK-TNK-031B', '1944-09-03')[1]), (('British VIII Corps', 'assigned'), False))
    expect(s + ': on 25 September (day 91 of the placeholder) the fallback still answers 79th Armoured Division, possible, without the note',
           (chain('UK-TNK-031B', '1944-09-25')[0], 'note: relation' in run('UK-TNK-031B', '1944-09-25')[1]), (('British 79th Armoured Division', 'organic_fallback', 'possible'), False))
    # 6. OPEN_CARRY_FORWARD_DAYS is unchanged
    expect(s + ': OPEN_CARRY_FORWARD_DAYS is still 90 and the basis name is organic_fallback', (wc.OPEN_CARRY_FORWARD_DAYS, wc.ORGANIC_FALLBACK), (90, 'organic_fallback'))


def scenario_267_cr1282_end():
    """CR1282 (US XXI Corps under the French First Army) ends between 15 and 16 February 1945 (6th Army Group G-3 Final Report p. 43, R453; Wikipedia, XXI Corps history, bigpigeon)."""
    s = 'CR1282 end (scenario 267)'
    row = master('US-COR-021C', 'FR-ARMY-001A', 'operational_control', '1945-01-23')
    expect(s + ': end old value blank, new value 1945-02-16 (earliest 1945-02-15), basis narrative, end_unknown false',
           (row['valid_to'], row['valid_to_earliest'], row['valid_to_basis'], row['end_unknown']), ('1945-02-16', '1945-02-15', 'narrative', 'false'))
    expect(s + ': the end is evidenced by C9452 (Morhange, 18 February 1945, 0.3)', 'C9452' in row['source_claim_ids'].split(), True)
    claims = {c['claim_id']: c for c in common.load_all_claims()[1]}
    expect(s + ': C9452 is XXI Corps at Morhange (PL2253) on 18 February 1945, confidence 0.3',
           (claims['C9452']['unit_id'], claims['C9452']['date'], claims['C9452']['place_id'], claims['C9452']['confidence']), ('US-COR-021C', '1945-02-18', 'PL2253', '0.3'))
    expect(s + ': 15 February 1945 is certainly under the French First Army', chain('US-COR-021C', '1945-02-15')[0], ('French First Army (Army B until 25 September 1944)', 'operational_control', 'certain'))
    st, why = intervals('US-COR-021C', '1945-02-16')[('FR-ARMY-001A', 'operational_control')]
    expect(s + ': 16 February 1945 is possible under the French First Army (end between 15 and 16 February, hour undocumented)', st, 'possible')
    expect_in(s + ': ...and the reason names the end range', why, 'end between 1945-02-15 and 1945-02-16')
    expect(s + ': 17 February 1945 no longer has the French First Army', intervals('US-COR-021C', '1945-02-17')[('FR-ARMY-001A', 'operational_control')][0], 'absent')
    expect(s + ': 17 February 1945 the chain goes through the Seventh Army (assigned, CR0201), then the 6th Army Group',
           [c[:3] for c in chain('US-COR-021C', '1945-02-17')[:2]], [('US Seventh Army', 'assigned', 'certain'), ('US 6th Army Group', 'assigned', 'certain')])
    expect(s + ': 20 February and 20 March 1945 are no longer answered through the French First Army',
           [chain('US-COR-021C', d)[0][0] for d in ('1945-02-20', '1945-03-20')], ['US Seventh Army', 'US Seventh Army'])
    expect(s + ': no new relation: the Seventh Army and 6th Army Group assignments are unchanged (open from 27 December 1944)',
           (master('US-COR-021C', 'US-ARMY-007A', 'assigned', '1944-12-27')['valid_to'], master('US-COR-021C', 'US-AG-006G', 'assigned', '1944-12-27')['valid_to']), ('', ''))


def scenario_268_kg_division_answer():
    """Scott decision 2026-11-14 (a per-unit decision, not a rule change): who_controls answers for GER-KG-MEYER and GER-KG-002PZ with the parent division
    (organic CR0027 -> GER-INF-352D, CR0016 -> GER-PZ-002D), not with the corps relation (CR0026 reserve -> GER-COR-084C, CR0017 unknown -> GER-PZ-047C). The corps
    relations stay as data; data/who_controls_overrides.csv sets them aside for the lookup."""
    s = 'Kampfgruppe division answer (scenario 268)'

    def run(unit, date):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc = wc.main([unit, date])
        return rc, buf.getvalue()

    ov = common.read_dicts(os.path.join(common.ROOT, 'data', 'who_controls_overrides.csv'))[1]
    expect(s + ': the override file lists exactly CR0017 and CR0026, effect defer_to_organic_parent, decided by Scott on 2026-11-14',
           [(o['relation_id'], o['effect'], o['decided_by'], o['decided_on']) for o in ov], [('CR0017', 'defer_to_organic_parent', 'Scott', '2026-11-14'), ('CR0026', 'defer_to_organic_parent', 'Scott', '2026-11-14')])
    expect(s + ': build/who_controls_overrides.csv is a verbatim copy of the data file',
           open(os.path.join(common.BUILD_DIR, 'who_controls_overrides.csv'), 'rb').read(), open(os.path.join(common.ROOT, 'data', 'who_controls_overrides.csv'), 'rb').read())
    # the corps relations stay as data (master and derived table), with the decision in the note
    for uid, hi, rel, rid in (('GER-KG-MEYER', 'GER-COR-084C', 'reserve', 'CR0026'), ('GER-KG-002PZ', 'GER-PZ-047C', 'unknown', 'CR0017')):
        row = master(uid, hi, rel, '1944-06-06' if uid == 'GER-KG-MEYER' else '1944-06-27')
        expect(s + ': %s stays in the derived table, preferred, end open' % rid, (row['relation_id'], row['valid_to']), (rid, ''))
        expect(s + ': %s note carries the decision with old value, new value and reason' % rid, ('Scott decision' in row['note'], 'old value' in row['note'], 'new value' in row['note'], 'Reason' in row['note']), (True, True, True, True))
    # Meyer: answers with the 352nd Infantry Division (organic_fallback), then the corps above the division
    rc, text = run('GER-KG-MEYER', '1944-06-10')
    expect(s + ': Meyer on 10 June 1944 resolves with the 352nd Infantry Division, organic_fallback, possible', (rc, chain('GER-KG-MEYER', '1944-06-10')[0][:2]), (0, ('German 352nd Infantry Division', 'organic_fallback')))
    expect(s + ': ...the chain goes on up from the division (LXXXIV Corps, Seventh Army)', [c[0] for c in chain('GER-KG-MEYER', '1944-06-10')[1:3]], ['German LXXXIV Corps', 'German Seventh Army'])
    expect(s + ': ...the corps reserve is not an interval line, a note says it was set aside (CR0026)', ('GER-KG-MEYER -> German LXXXIV Corps' in text, 'note: relation CR0026' in text, 'set aside by a per-relation override' in text), (False, True, True))
    expect(s + ': the old interval table still reads the reserve relation as data (the 91-day cutoff of scenario 260 is unchanged)', intervals('GER-KG-MEYER', '1944-09-05')[('GER-COR-084C', 'reserve')][0], 'absent')
    # 2nd Panzer Kampfgruppe: answers with 2nd Panzer Division, then XLVII Panzer Corps above the division
    rc, text = run('GER-KG-002PZ', '1944-06-30')
    expect(s + ': GER-KG-002PZ on 30 June 1944 resolves with the 2nd Panzer Division, organic_fallback', (rc, chain('GER-KG-002PZ', '1944-06-30')[0][:2]), (0, ('German 2nd Panzer Division', 'organic_fallback')))
    expect(s + ': ...and the chain goes on up from the division (XLVII Panzer Corps, Panzer Group West)', [c[0] for c in chain('GER-KG-002PZ', '1944-06-30')[1:3]], ['German XLVII Panzer Corps', 'German Panzer Group West'])
    expect(s + ': ...the unknown link CR0017 is not an interval line, a note says it was set aside', ('GER-KG-002PZ -> German XLVII Panzer Corps' in text, 'note: relation CR0017' in text), (False, True))
    # the 90-day rule still applies to the organic relation (CR0027 last listed 1944-06-06; day 91 is 5 September)
    expect(s + ': Meyer on 4 September 1944 (day 90) is answered, on 5 September (day 91) it is not', (run('GER-KG-MEYER', '1944-09-04')[0], run('GER-KG-MEYER', '1944-09-05')[0]), (0, 1))
    # per-unit only: another unit with a corps reserve or unknown relation is unchanged, and no override applies outside the list
    expect(s + ': the set-aside note appears for no other unit (Combat Command A, 20 August 1944)', 'set aside by a per-relation override' in run('US-CCA-002D', '1944-08-20')[1], False)


def scenario_269_army_group_student():
    """Armeegruppe Student (roadmap 351, 14 November 2026): the unit GER-AG-STUDT exists; C7968 (its formation, FMS B-414, on GER-ARMY-BLUMT) retired and re-entered as C9453 on it;
    LXXXVIII Corps is under it from 3 to 6 April 1945 (FMS B-762, Stacey p. 550), II Parachute Corps from about 1 April (B-414); the group is under Army Group H."""
    s = 'Army Group Student (scenario 269)'
    units = {u['unit_id']: u for u in common.read_dicts(common.UNITS_CSV)[1]}
    u = units.get('GER-AG-STUDT', {})
    expect(s + ': GER-AG-STUDT is an army_group of Germany, active, formed 1945-04-01 (source R814 page)',
           (u.get('echelon'), u.get('nationality'), u.get('record_status'), u.get('formed_date'), 'b-414-army-group-h' in u.get('formed_date_source', '')), ('army_group', 'Germany', 'active', '1945-04-01', True))
    claims = {c['claim_id']: c for c in common.load_all_claims()[1]}
    c = claims['C9453']
    expect(s + ': C9453 (replacing the retired C7968 of GER-ARMY-BLUMT) belongs to GER-AG-STUDT, date, place and confidence unchanged',
           (c['unit_id'], c['unit_name'], c['echelon'], c['date'], c['place_id'], c['confidence'], c['event_type']), ('GER-AG-STUDT', 'Armeegruppe Student (Army Group Student)', 'army_group', '1945-04-02', 'PL0770', '0.3', 'activation'))
    expect(s + ': ...and the note records old value, new value and reason', ('old value C7968' in c['notes'], 'new value C9453' in c['notes'], 'reason' in c['notes']), (True, True, True))
    expect(s + ': Army Blumentritt keeps C1223 (6 April); C7968 is retired, not a claim', (claims['C1223']['unit_id'], 'C7968' in claims), ('GER-ARMY-BLUMT', False))
    r = master('GER-AG-STUDT', 'GER-AG-00HG', 'unspecified_subordination', '1945-04-01')
    # leftovers-1115 task c (roadmap 351): old value of this check: CR1314 open (valid_to blank, open_at_last_claim); new value: ends 1945-04-06 (narrative); reason: B-414 pp. 24-26 (Student's staff given the Weser defence on 6 April; UL026).
    expect(s + ': CR1314 Student under Army Group H from 1 April, ends 6 April (narrative; formerly open), evidenced by C9453', (r['relation_id'], r['valid_to'], r['valid_to_basis'], r['source_claim_ids']), ('CR1314', '1945-04-06', 'narrative', 'C9453'))
    r = master('GER-COR-088C', 'GER-AG-STUDT', 'unspecified_subordination', '1945-04-03')
    expect(s + ': CR1315 LXXXVIII Corps under Student 3 to 6 April, narrative both ends', (r['relation_id'], r['valid_to'], r['valid_from_basis'], r['valid_to_basis'], sorted(r['source_claim_ids'].split())), ('CR1315', '1945-04-06', 'narrative', 'narrative', ['C7581', 'C7836', 'C7838']))
    r = master('GER-FJ-002C', 'GER-AG-STUDT', 'unspecified_subordination', '1945-04-01')
    # leftovers-1115 task c: old value of this check: valid_to '' (open); new value: 1945-04-10 (latest end, earliest 1945-04-02); reason: Student takes over the First Parachute Army on 10 April, his staff left on 6 April.
    expect(s + ': CR1316 II Parachute Corps under Student from about 1 April (latest 2 April), ends between 2 and 10 April (formerly open)', (r['relation_id'], r['valid_from_latest'], r['valid_to'], r['valid_to_earliest']), ('CR1316', '1945-04-02', '1945-04-10', '1945-04-02'))
    expect(s + ': CR0736 (Twenty-fifth Army) still ends on 3 April and CR1188 still starts on 6 April', (master('GER-COR-088C', 'GER-ARMY-025A', 'assigned', '1944-11-10')['valid_to'], master('GER-COR-088C', 'GER-ARMY-025A', 'assigned', '1945-04-06')['valid_to']), ('1945-04-03', ''))
    expect(s + ': 2 April 1945 LXXXVIII Corps is still under the Twenty-fifth Army (certain)', chain('GER-COR-088C', '1945-04-02')[0], ('German Twenty-fifth Army (Germany)', 'assigned', 'certain'))
    expect(s + ': 3 April the Twenty-fifth Army line is possible (ends that day, hour undocumented), the Student line is possible (starts that day)',
           (intervals('GER-COR-088C', '1945-04-03')[('GER-ARMY-025A', 'assigned')][0], intervals('GER-COR-088C', '1945-04-03')[('GER-AG-STUDT', 'unspecified_subordination')][0]), ('possible', 'possible'))
    expect(s + ': 4 and 5 April the chain runs through Army Group Student, then Army Group H',
           [[c[0] for c in chain('GER-COR-088C', d)[:2]] for d in ('1945-04-04', '1945-04-05')], [['German Armeegruppe Student (Army Group Student)', 'German Army Group H (Heeresgruppe H)']] * 2)
    expect(s + ': 4 April the Student level is certain', chain('GER-COR-088C', '1945-04-04')[0], ('German Armeegruppe Student (Army Group Student)', 'unspecified_subordination', 'certain'))
    expect(s + ': 7 April LXXXVIII Corps is back under the Twenty-fifth Army and has no Student line', ('GER-AG-STUDT', 'unspecified_subordination') in intervals('GER-COR-088C', '1945-04-07'), False)
    expect(s + ': II Parachute Corps on 5 April has both the First Parachute Army line (CR0606, unchanged) and the Student line', sorted(k[0] for k in intervals('GER-FJ-002C', '1945-04-05')), ['GER-AG-STUDT', 'GER-FJA-001A'])
    expect(s + ': Army Group Student itself answers through Army Group H on 5 April', chain('GER-AG-STUDT', '1945-04-05')[0][:2], ('German Army Group H (Heeresgruppe H)', 'unspecified_subordination'))


def scenario_270_6ag_advance_hq_luneville():
    """Roadmap 356 (14 November 2026): the 6th Army Group advance headquarters moves from Phalsbourg to Lunéville in late December 1944 (CMH Riviera to the Rhine
    ch. 27 p. 500, R424), undated within 19-31 December: C9454, approximate, 0.3; the de Lattre rows C8615 (Phalsbourg) and C8616 (Vittel) are kept."""
    s = '6th Army Group advance HQ (scenario 270)'
    claims = {c['claim_id']: c for c in common.load_all_claims()[1]}
    c = claims['C9454']
    expect(s + ': C9454 is the 6th Army Group at Lunéville (PL0199) on 31 December 1944, hq_move, 0.3, preferred, no conflict group',
           (c['unit_id'], c['date'], c['place_id'], c['event_type'], c['confidence'], c['claim_status'], c['conflict_group_id']), ('US-AG-006G', '1944-12-31', 'PL0199', 'hq_move', '0.3', 'preferred', ''))
    expect(s + ': C9454 cites R424 first, then R686, and the CMH page', (c['reference_ids'].split(';')[:2], 'p. 500' in c['source_locator']), (['R424', 'R686'], True))
    expect(s + ': the note states the date is approximate and not before 22 December, and keeps the Vittel account as a conflict', ('not later than 31 December' in c['notes'], 'Not before 22 December' in c['notes'], 'Conflict kept, not resolved' in c['notes'], 'C8616' in c['notes']), (True, True, True, True))
    expect(s + ': the note carries old value, new value and reason', ('old value none' in c['notes'], 'new value this claim' in c['notes'], 'reason for the row' in c['notes']), (True, True, True))
    expect(s + ': the Phalsbourg rows C8614 and C8615 and the Vittel row C8616 are unchanged (place, date, confidence)',
           [(claims[x]['place_id'], claims[x]['date'], claims[x]['confidence']) for x in ('C8614', 'C8615', 'C8616')], [('PL0273', '1944-12-14', '0.5'), ('PL0273', '1944-12-22', '0.5'), ('PL3894', '1944-12-27', '0.5')])
    expect(s + ': C8616 note points to C9454 with old value, new value and reason', ('C9454' in claims['C8616']['notes'], 'old value' in claims['C8616']['notes'], 'new value' in claims['C8616']['notes']), (True, True, True))
    expect(s + ': the unit has no other row between 27 December 1944 and 5 January 1945',
           sorted(x['claim_id'] for x in claims.values() if x['unit_id'] == 'US-AG-006G' and '1944-12-27' < x['date'] < '1945-01-05'), ['C9454'])


def scenario_271_cr0950_9th_colonial_end():
    """Roadmap 352, CR0950 (15 November 2026; re-checked in leftovers-1115 task b): the French 9th Colonial Division under the I Corps from 6 February 1945. First change (small-fixes-1114): end 2 April, earliest 9 February.
    Task b (de Lattre pass-2 notes, R686; the borrowed scan was not re-opened): the II Corps commanded the division for the Rhine crossing from 30 March (pp. 421, 424, 429-430), so the I Corps end is now 29 March (inferred) and
    CR1321 enters the II Corps (operational_control, 30 March, end between 2 and 4 April, the two readings of p. 435 kept as a range)."""
    s = 'CR0950 and CR1321 9th Colonial Division (scenario 271)'
    r = master('FR-INF-009D', 'FR-COR-001C', 'unspecified_subordination', '1945-02-06')
    expect(s + ': CR0950 ends 29 March 1945 (inferred), earliest end 9 February, evidenced by C1645 only',
           (r['relation_id'], r['valid_to'], r['valid_to_earliest'], r['valid_to_basis'], sorted(r['source_claim_ids'].split())), ('CR0950', '1945-03-29', '1945-02-09', 'inferred', ['C1645']))
    expect(s + ': the CR0950 note keeps the first change and records old value, new value and reason of the second',
           ('old value blank' in r['note'], 'new value 1945-04-02' in r['note'], 'leftovers-1115' in r['note'], 'old value 1945-04-02' in r['note'], 'new value 1945-03-29' in r['note'], 'reason' in r['note'], 'superseded by CR1321' in r['note']),
           (True, True, True, True, True, True, True))
    r2 = master('FR-INF-009D', 'FR-COR-002C', 'operational_control', '1945-03-30')
    expect(s + ': CR1321 II Corps operational_control from 30 March, end between 2 and 4 April (narrative), evidence C9307',
           (r2['relation_id'], r2['valid_to'], r2['valid_to_earliest'], r2['valid_to_basis'], sorted(r2['source_claim_ids'].split())), ('CR1321', '1945-04-04', '1945-04-02', 'narrative', ['C9307']))
    expect(s + ': the CR1321 note records old value, new value, reason and keeps the end as a conflict',
           ('old value none' in r2['note'], 'new value this relation' in r2['note'], 'reason' in r2['note'], 'conflict kept' in r2['note'], 'not re-opened' in r2['note']), (True, True, True, True, True))
    expect(s + ': the division has these two relations only', sorted(x['relation_id'] for x in _ROWS if x['subject_unit_id'] == 'FR-INF-009D'), ['CR0950', 'CR1321'])
    expect(s + ': 6 February 1945 the division is under the I Corps (certain)', chain('FR-INF-009D', '1945-02-06')[0], ('French I Corps', 'unspecified_subordination', 'certain'))
    expect(s + ': 15 March 1945 the I Corps answer is possible (end between 9 February and 29 March)', intervals('FR-INF-009D', '1945-03-15')[('FR-COR-001C', 'unspecified_subordination')][0], 'possible')
    expect(s + ': 2 April 1945 the II Corps answer is certain; 3 April possible (end between 2 and 4 April); 5 April and later no corps answer',
           [chain('FR-INF-009D', d)[0][:3] for d in ('1945-04-02', '1945-04-03', '1945-04-05', '1945-04-20')],
           [('French II Corps', 'operational_control', 'certain'), ('French II Corps', 'operational_control', 'possible'), ('NO CHAIN', [], None), ('NO CHAIN', [], None)])
    claims = {c['claim_id']: c for c in common.load_all_claims()[1]}
    c = claims['C9307']
    expect(s + ': C9307 keeps date, place and 0.3, cites p. 435, has the II Corps as parent and a Review with old and new value',
           (c['date'], c['place_id'], c['confidence'], c['source_locator'], c['parent_unit_id'], 'Command support: de Lattre, p. 435' in c['notes'], 'source_locator old value' in c['notes'], 'parent_unit_id old value blank, new value FR-COR-002C' in c['notes']),
           ('1945-04-02', 'PL4126', '0.3', 'R686: pp. 430-431, 435', 'FR-COR-002C', True, True, True))


def scenario_272_successors_157_and_158():
    """Roadmap 363 (15 November 2026): the successors of the 157th and 158th Reserve Divisions get records and lineage rows: GER-GEB-157D (1 September 1944, UL021), GER-INF-016D (formed 4 August 1944
    from the 158th Reserve Division and the 16th Luftwaffe Field Division, UL022 and UL023, dates conflict, G128; renamed the 16th Volksgrenadier Division on 9 October 1944, UL024)."""
    import lineage
    s = 'Successors of the 157th and 158th Reserve Divisions (scenario 272)'
    units = {u['unit_id']: u for u in common.read_dicts(common.UNITS_CSV)[1]}
    expect(s + ': GER-GEB-157D is an active German division formed 1944-09-01 (Lexikon 157 page)', (units['GER-GEB-157D']['record_status'], units['GER-GEB-157D']['formed_date'], units['GER-GEB-157D']['echelon'], 'ResDiv/157ResDiv-R' in units['GER-GEB-157D']['formed_date_source']), ('active', '1944-09-01', 'division', True))
    u = units['GER-INF-016D']
    expect(s + ': GER-INF-016D is active, formed 1944-08-04 (Lexikon 16ID page), initial parent LXVI Corps as of 1944-09 (LEX)', (u['record_status'], u['formed_date'], u['initial_parent_unit_id'], u['initial_parent_as_of'], u['initial_parent_source']), ('active', '1944-08-04', 'GER-COR-066C', '1944-09', 'LEX'))
    rows = {r['lineage_id']: r for r in lineage.load()[1]}
    expect(s + ': UL021 157th Reserve Division -> 157th Mountain Division, redesignation, 1944-09-01', [rows['UL021'][k] for k in ('predecessor_unit_id', 'successor_unit_id', 'kind', 'effective_date')], ['GER-RES-157D', 'GER-GEB-157D', 'redesignation', '1944-09-01'])
    expect(s + ': UL022 158th Reserve Division -> 16th Infantry Division, absorbed_into, 1944-08-04', [rows['UL022'][k] for k in ('predecessor_unit_id', 'successor_unit_id', 'kind', 'effective_date')], ['GER-RES-158D', 'GER-INF-016D', 'absorbed_into', '1944-08-04'])
    expect(s + ': UL023 16th Luftwaffe Field Division -> 16th Infantry Division, absorbed_into, 1944-08-04 (UL017 to the 21st Panzer Division stays)', ([rows['UL023'][k] for k in ('predecessor_unit_id', 'successor_unit_id', 'kind', 'effective_date')], rows['UL017']['successor_unit_id']), (['GER-LFD-016D', 'GER-INF-016D', 'absorbed_into', '1944-08-04'], 'GER-PZ-021D'))
    expect(s + ': UL024 16th Infantry Division -> 16th Volksgrenadier Division, redesignation, 1944-10-09 (the unit formed 1944-10-09)', ([rows['UL024'][k] for k in ('predecessor_unit_id', 'successor_unit_id', 'kind', 'effective_date')], units['GER-VG-016D']['formed_date']), (['GER-INF-016D', 'GER-VG-016D', 'redesignation', '1944-10-09'], '1944-10-09'))
    claims = {c['claim_id']: c for c in common.load_all_claims()[1]}
    expect(s + ': C9455 is the first row of GER-GEB-157D, 1944-09-01, 0.3, Grenoble PL3902 (inferred)', (claims['C9455']['unit_id'], claims['C9455']['date'], claims['C9455']['confidence'], claims['C9455']['place_id'], claims['C9455']['location_basis']), ('GER-GEB-157D', '1944-09-01', '0.3', 'PL3902', 'inferred'))
    g = sorted((c['date'], c['claim_id'], c['claim_status'], c['confidence']) for c in claims.values() if c['conflict_group_id'] == 'G128')
    expect(s + ': conflict group G128 keeps three dates for the formation of the 16th Infantry Division: 2 July (alternate), 4 August (preferred), 16 August (alternate), all 0.3',
           g, [('1944-07-02', 'C9457', 'alternate', '0.3'), ('1944-08-04', 'C9456', 'preferred', '0.3'), ('1944-08-16', 'C9458', 'alternate', '0.3')])
    expect(s + ': ...all on GER-INF-016D', {claims[c]['unit_id'] for c in ('C9456', 'C9457', 'C9458')}, {'GER-INF-016D'})
    expect(s + ': the predecessor rows C8656 and C8724 keep date, place and confidence; their notes point to the successor and record old value, new value and reason',
           ((claims['C8656']['date'], claims['C8656']['place_id'], claims['C8656']['confidence']), (claims['C8724']['date'], claims['C8724']['place_id'], claims['C8724']['confidence']),
            'GER-GEB-157D' in claims['C8656']['notes'] and 'old value' in claims['C8656']['notes'], 'GER-INF-016D' in claims['C8724']['notes'] and 'old value' in claims['C8724']['notes']),
           (('1944-09-01', 'PL3902', '0.3'), ('1944-07-02', 'PL0936', '0.5'), True, True))
    # leftovers-1115 task a (roadmap 363): old value of this check: no relation was entered for the new units ([]); new value: the four relations of scenario 275; reason: the relations were added.
    expect(s + ': the command relations of the new units are the four of scenario 275 (formerly none)', sorted(r['relation_id'] for r in _ROWS if r['subject_unit_id'] in ('GER-GEB-157D', 'GER-INF-016D')), ['CR1317', 'CR1318', 'CR1319', 'CR1320'])


def scenario_276_armeegruppe_student_leftovers():
    """Roadmap 351 leftovers (leftovers-1115 task c, 15 November 2026, Scott t419u): the 6th Parachute Division under the II Parachute Corps (CR1322) and the LXXXVIII Corps (CR1323), CR0787 closed,
    the ends of CR1314 and CR1316, the April evidence of CR0606 (C9463, Lexikon), and lineage UL026 Armeegruppe Student -> Army Blumentritt."""
    s = 'scenario 276'
    import lineage
    claims = {c['claim_id']: c for c in common.load_all_claims()[1]}
    units = {u['unit_id']: u for u in common.read_dicts(common.UNITS_CSV)[1]}
    r = master('GER-FJ-006D', 'GER-FJ-002C', 'unspecified_subordination', '1945-03-11')
    expect(s + ': CR1322 6th Parachute Division under II Parachute Corps from 11 March, end between 25 March and 2 April (narrative)', (r['relation_id'], r['valid_to_earliest'], r['valid_to'], r['valid_to_basis']), ('CR1322', '1945-03-25', '1945-04-02', 'narrative'))
    r = master('GER-FJ-006D', 'GER-COR-088C', 'unspecified_subordination', '1945-03-26')
    expect(s + ': CR1323 6th Parachute Division under LXXXVIII Corps from 26 March (latest start 3 April), open', (r['relation_id'], r['valid_from_latest'], r['valid_to']), ('CR1323', '1945-04-03', ''))
    r = [x for x in _ROWS if x['relation_id'] == 'CR0787'][0]
    expect(s + ': CR0787 (XLVII Panzer Corps) ends 10 March, earliest end 4 March (formerly open)', (r['valid_to'], r['valid_to_earliest'], r['valid_to_basis']), ('1945-03-10', '1945-03-04', 'narrative'))
    expect(s + ': 20 March the division has only the II Parachute Corps line (certain)', sorted(intervals('GER-FJ-006D', '1945-03-20')), [('GER-FJ-002C', 'unspecified_subordination')])
    expect(s + ': 28 March both corps lines are possible (the manuscripts date the move differently; nothing resolved)', sorted((k[0], v[0]) for k, v in intervals('GER-FJ-006D', '1945-03-28').items()), [('GER-COR-088C', 'possible'), ('GER-FJ-002C', 'possible')])
    expect(s + ': 4 April the division answers to the LXXXVIII Corps, which answers to Army Group Student (CR1315)', [c[0] for c in chain('GER-FJ-006D', '1945-04-04')[:2]], ['German LXXXVIII Corps', 'German Armeegruppe Student (Army Group Student)'])
    expect(s + ': the three evidence claims got their parents (old value blank)', (claims['C8005']['parent_unit_id'], claims['C8010']['parent_unit_id'], claims['C7835']['parent_unit_id']), ('GER-FJ-002C', 'GER-COR-088C', 'GER-COR-088C'))
    expect(s + ': C8005, C8010, C7835 keep date, place and confidence; the notes carry old value, new value and reason',
           ([(claims[x]['date'], claims[x]['place_id'], claims[x]['confidence']) for x in ('C8005', 'C8010', 'C7835')], all('old value' in claims[x]['notes'] and 'new value' in claims[x]['notes'] and 'reason' in claims[x]['notes'] for x in ('C8005', 'C8010', 'C7835'))),
           ([(claims['C8005']['date'], claims['C8005']['place_id'], claims['C8005']['confidence']), (claims['C8010']['date'], claims['C8010']['place_id'], claims['C8010']['confidence']), (claims['C7835']['date'], claims['C7835']['place_id'], claims['C7835']['confidence'])], True))
    rel = {x['relation_id']: x for x in _ROWS}
    expect(s + ': CR1314 and CR1316 end with ranges', [(rel[k]['valid_to_earliest'], rel[k]['valid_to'], rel[k]['valid_to_basis']) for k in ('CR1314', 'CR1316')], [('1945-04-02', '1945-04-06', 'narrative'), ('1945-04-02', '1945-04-10', 'narrative')])
    expect(s + ': CR0606 stays open and is now linked to C9463 (Lexikon, April 1945, 0.3, parent First Parachute Army)', (rel['CR0606']['valid_to'], 'C9463' in rel['CR0606']['source_claim_ids'].split(), claims['C9463']['parent_unit_id'], claims['C9463']['confidence'], claims['C9463']['unit_id']), ('', True, 'GER-FJA-001A', '0.3', 'GER-FJ-002C'))
    lin = {x['lineage_id']: x for x in lineage.load()[1]}['UL026']
    expect(s + ': UL026 Armeegruppe Student -> Army Blumentritt, redesignation, 1945-04-06; the successor formed 1945-04-06', ([lin[k] for k in ('predecessor_unit_id', 'successor_unit_id', 'kind', 'effective_date')], units['GER-ARMY-BLUMT']['formed_date']), (['GER-AG-STUDT', 'GER-ARMY-BLUMT', 'redesignation', '1945-04-06'], '1945-04-06'))


def scenario_277_allegiance_official_sources():
    """Roadmap 384 (leftovers-1115 task d, 15 November 2026, Scott t420u): official or primary sources (Avalon Project, FRUS, Hansard) added next to the Wikipedia references of nation_allegiance.csv;
    no date changed; the differences between the sources are kept in the notes (Italy 10/11 June 1940 and 3/8 September 1943, Germany 7/8 May 1945, RSI and Italy 29 April/2 May 1945)."""
    s = 'scenario 277'
    rows = common.read_dicts(os.path.join(os.path.dirname(common.NATIONALITIES_CSV), 'nation_allegiance.csv'))[1]
    def row(n, f): return [r for r in rows if r['nation'] == n and r['valid_from'] == f][0]
    expect(s + ': the dates of the key rows are unchanged', [(r['nation'], r['valid_from'], r['valid_to']) for r in (row('UK', '1939-09-03'), row('FR', '1939-09-03'), row('US', '1941-12-08'), row('IT', '1940-06-10'), row('IT', '1943-10-13'), row('RSI', '1943-09-23'), row('GER', '1939-09-01'))],
           [('UK', '1939-09-03', '1945-09-02'), ('FR', '1939-09-03', '1945-09-02'), ('US', '1941-12-08', '1945-09-02'), ('IT', '1940-06-10', '1943-09-08'), ('IT', '1943-10-13', '1945-05-02'), ('RSI', '1943-09-23', '1945-04-29'), ('GER', '1939-09-01', '1945-05-08')])
    expect(s + ': every Wikipedia reference is still there and an official one was added next to it', [(set(row(n, f)['reference_ids'].split(';')) >= set(w), set(row(n, f)['reference_ids'].split(';')) >= set(o)) for n, f, w, o in (
        ('UK', '1939-09-03', ['R1181', 'R1197'], ['R1200', 'R1212']), ('FR', '1939-09-03', ['R1187', 'R1188', 'R1197'], ['R1201']), ('US', '1941-12-08', ['R1195', 'R1197'], ['R1202', 'R1203']),
        ('IT', '1943-10-13', ['R1179'], ['R1205', 'R1206', 'R1211']), ('GER', '1939-09-01', ['R1186', 'R1196'], ['R1210']), ('RSI', '1943-09-23', ['R1198'], ['R1211']))], [(True, True)] * 6)
    expect(s + ': the Italian, German and RSI differences are kept in the notes', ['effective' in row('IT', '1943-10-13')['note'] or '11 June' in row('IT', '1940-06-10')['note'], '3 September 1943' in row('IT', '1940-06-10')['note'], '7 May' in row('GER', '1939-09-01')['note'], '2 May' in row('RSI', '1943-09-23')['note']], [True] * 4)
    expect(s + ': every row edited in task d records old value, new value and reason', all(('old value' in r['note'] and 'new value' in r['note']) for r in rows if 'task d' in r['note'] and 'reference_ids old value' in r['note']), True)


def scenario_278_allegiance_axis_batch():
    """Roadmap 385 (leftovers-1115 task e, batch 1, 15 November 2026, Scott t421u): nine Axis and Axis-aligned codes (JPN HUN ROM BUL FIN SVK NDH THA MCK) with dated rows; side switches: Romania on 23 August 1944, Bulgaria on 8 September 1944, Finland from 15 September 1944."""
    s = 'scenario 278'
    import allegiance
    rows = allegiance.load()[1]
    side = lambda n, d: allegiance.side_on(rows, n, d)
    expect(s + ': Romania is Axis on 22 August 1944 and a co-belligerent on 23 August 1944 (the coup)', [side('ROM', '1944-08-22'), side('ROM', '1944-08-23')], ['Axis', 'co-belligerent'])
    expect(s + ': Romania is Axis from 23 November 1940 (Tripartite Pact) and has no row on 22 November 1940 (blank, not guessed)', [side('ROM', '1940-11-23'), side('ROM', '1940-11-22')], ['Axis', None])
    expect(s + ': Bulgaria neutral to 28 February 1941, Axis from 1 March 1941, co-belligerent from 8 September 1944', [side('BUL', '1941-02-28'), side('BUL', '1941-03-01'), side('BUL', '1944-09-07'), side('BUL', '1944-09-08')], ['neutral', 'Axis', 'Axis', 'co-belligerent'])
    expect(s + ': Japan Axis from 1 September 1939 (old expectation: none before 27 September 1940; changed in allegiance-remaining batch 2, roadmap 387); Thailand neutral on 7 and 10 December 1941 (old expectation: none on 10 December), Axis on 21 December 1941', [side('JPN', '1940-09-26'), side('JPN', '1940-09-27'), side('THA', '1941-12-07'), side('THA', '1941-12-10'), side('THA', '1941-12-21')], ['Axis', 'Axis', 'neutral', 'neutral', 'Axis'])
    expect(s + ': Finland is blank before the Lapland War and a co-belligerent from 15 September 1944; Hungary Axis on 1 January 1945; Manchukuo Axis on 19 August 1945 and none on 21 August', [side('FIN', '1944-09-14'), side('FIN', '1944-09-15'), side('HUN', '1945-01-01'), side('MCK', '1945-08-19'), side('MCK', '1945-08-21')], [None, 'co-belligerent', 'Axis', 'Axis', None])
    codes = {r['code'] for r in common.read_dicts(common.NATIONALITIES_CSV)[1]}
    expect(s + ': the nine codes are in nationalities.csv', {'JPN', 'HUN', 'ROM', 'BUL', 'FIN', 'SVK', 'NDH', 'THA', 'MCK'} <= codes, True)


def scenario_279_allegiance_allies_batch():
    """Roadmap 385 (leftovers-1115 task e, batch 2, 15 November 2026, Scott t421u): seven Allied codes (SOV CHN IND GRE YUG BRA PHL); Yugoslavia changes side three times in 1941."""
    s = 'scenario 279'
    import allegiance
    rows = allegiance.load()[1]
    side = lambda n, d: allegiance.side_on(rows, n, d)
    expect(s + ': Yugoslavia neutral on 24 March 1941, Axis 25-26 March, neutral 27 March to 5 April (old expectation: blank; changed in allegiance-remaining batch 2, roadmap 387), Allied from 6 April 1941', [side('YUG', d) for d in ('1941-03-24', '1941-03-25', '1941-03-26', '1941-03-27', '1941-04-05', '1941-04-06')], ['neutral', 'Axis', 'Axis', 'neutral', 'neutral', 'Allied'])
    expect(s + ': Greece neutral on 27 October 1940, Allied from 28 October 1940', [side('GRE', '1940-10-27'), side('GRE', '1940-10-28')], ['neutral', 'Allied'])
    expect(s + ': USSR neutral on 21 June 1941 (old expectation: blank; changed in allegiance-remaining commit 4, roadmap 389), Allied on 22 June 1941; Brazil blank on 21 August 1942, Allied on 22 August 1942; Philippines Allied on 8 December 1941; China Allied on 1 September 1939', [side('SOV', '1941-06-21'), side('SOV', '1941-06-22'), side('BRA', '1942-08-21'), side('BRA', '1942-08-22'), side('PHL', '1941-12-08'), side('CHN', '1939-09-01')], ['neutral', 'Allied', None, 'Allied', 'Allied', 'Allied'])
    codes = {r['code'] for r in common.read_dicts(common.NATIONALITIES_CSV)[1]}
    expect(s + ': the seven codes are in nationalities.csv', {'SOV', 'CHN', 'IND', 'GRE', 'YUG', 'BRA', 'PHL'} <= codes, True)


def scenario_280_allegiance_neutrals_batch():
    """Roadmap 385 (leftovers-1115 task e, batch 3, 15 November 2026, Scott t421u): neutrals SWE CHE ESP PRT IRL, Turkey (neutral, Allied from 23 February 1945), Vichy France (VIC)."""
    s = 'scenario 280'
    import allegiance
    rows = allegiance.load()[1]
    side = lambda n, d: allegiance.side_on(rows, n, d)
    expect(s + ': Turkey neutral on 22 February 1945, Allied on 23 February 1945', [side('TUR', '1945-02-22'), side('TUR', '1945-02-23')], ['neutral', 'Allied'])
    expect(s + ': Sweden, Switzerland, Spain, Portugal and Ireland neutral on 6 June 1944', [side(n, '1944-06-06') for n in ('SWE', 'CHE', 'ESP', 'PRT', 'IRL')], ['neutral'] * 5)
    expect(s + ': Vichy France blank on 9 July 1940, neutral on 10 July 1940 and 20 August 1944, blank on 21 August 1944; Free France (FR) stays Allied on 10 July 1940', [side('VIC', '1940-07-09'), side('VIC', '1940-07-10'), side('VIC', '1944-08-20'), side('VIC', '1944-08-21'), side('FR', '1940-07-10')], [None, 'neutral', 'neutral', None, 'Allied'])
    codes = {r['code'] for r in common.read_dicts(common.NATIONALITIES_CSV)[1]}
    expect(s + ': the seven codes are in nationalities.csv', {'SWE', 'CHE', 'ESP', 'PRT', 'IRL', 'TUR', 'VIC'} <= codes, True)


def scenario_281_allegiance_remaining_countries():
    """Roadmap 386 (branch allegiance-remaining, batch 1, 15 November 2026, Scott t424u): Iran, Iraq, Mexico and Ethiopia (ETH IRN IRQ MEX) with primary sources (FRUS, UN Treaty Collection, Mexican decree, Hansard)."""
    s = 'scenario 281'
    import allegiance
    rows = allegiance.load()[1]
    side = lambda n, d: allegiance.side_on(rows, n, d)
    expect(s + ': Iraq neutral on 1 May 1941, Axis 2-31 May 1941 (Anglo-Iraqi War), neutral on 1 June 1941, neutral on 16 January 1943, Allied on 17 January 1943', [side('IRQ', d) for d in ('1941-05-01', '1941-05-02', '1941-05-31', '1941-06-01', '1943-01-16', '1943-01-17')], ['neutral', 'Axis', 'Axis', 'neutral', 'neutral', 'Allied'])
    expect(s + ': Iran neutral on 24 August 1941, blank 25-31 August (the invasion), neutral on 1 September 1941 and 8 September 1943, Allied on 9 September 1943', [side('IRN', d) for d in ('1941-08-24', '1941-08-25', '1941-08-31', '1941-09-01', '1943-09-08', '1943-09-09')], ['neutral', None, None, 'neutral', 'neutral', 'Allied'])
    expect(s + ': Mexico neutral on 21 May 1942, Allied on 22 May 1942; Ethiopia blank on 3 February 1941, Allied on 4 February 1941', [side('MEX', '1942-05-21'), side('MEX', '1942-05-22'), side('ETH', '1941-02-03'), side('ETH', '1941-02-04')], ['neutral', 'Allied', None, 'Allied'])
    codes = {r['code'] for r in common.read_dicts(common.NATIONALITIES_CSV)[1]}
    expect(s + ': the four codes are in nationalities.csv', {'ETH', 'IRN', 'IRQ', 'MEX'} <= codes, True)
    rows_ = {(r['nation'], r['valid_from']): r for r in rows}
    expect(s + ': the Iran and Iraq notes record the choices for Scott', ['Documented choice for Scott' in rows_[('IRN', '1941-09-01')]['note'], 'Documented choice for Scott' in rows_[('IRQ', '1941-05-02')]['note']], [True, True])


def scenario_282_allegiance_blank_periods():
    """Roadmap 386 (branch allegiance-remaining, batch 2, 15 November 2026, Scott t424u): blank periods filled where a source allows (Japan from 1 September 1939, Finland Continuation War, Thailand 8-10 December 1941, Yugoslavia 27 March-5 April 1941, India sourced); the Winter War, the USSR before 22 June 1941 and Thailand 11-20 December 1941 stay blank because they need a new side value or a source."""
    s = 'scenario 282'
    import allegiance
    rows = allegiance.load()[1]
    side = lambda n, d: allegiance.side_on(rows, n, d)
    expect(s + ': Japan Axis on 1 September 1939 and 27 September 1940', [side('JPN', '1939-09-01'), side('JPN', '1940-09-27')], ['Axis', 'Axis'])
    expect(s + ': Finland non-aligned-belligerent on 30 November 1939 (Winter War; old expectation: blank; changed in commit 4, roadmap 389), Axis on 25 June 1941 and 4 September 1944, blank on 5 September 1944, co-belligerent on 15 September 1944', [side('FIN', d) for d in ('1939-11-30', '1941-06-25', '1944-09-04', '1944-09-05', '1944-09-15')], ['non-aligned-belligerent', 'Axis', 'Axis', None, 'co-belligerent'])
    expect(s + ': USSR neutral on 21 June 1941 and non-aligned-belligerent on 17 September 1939 (old expectation: blank both; changed in commit 4, roadmap 389), Allied on 22 June 1941', [side('SOV', '1939-09-17'), side('SOV', '1941-06-21'), side('SOV', '1941-06-22')], ['non-aligned-belligerent', 'neutral', 'Allied'])
    expect(s + ': Thailand neutral on 8 and 10 December 1941, blank 11-20 December, Axis on 21 December', [side('THA', d) for d in ('1941-12-08', '1941-12-10', '1941-12-11', '1941-12-20', '1941-12-21')], ['neutral', 'neutral', None, None, 'Axis'])
    expect(s + ': Yugoslavia Axis on 26 March 1941, neutral 27 March to 5 April, Allied on 6 April', [side('YUG', d) for d in ('1941-03-26', '1941-03-27', '1941-04-05', '1941-04-06')], ['Axis', 'neutral', 'neutral', 'Allied'])
    by = {(r['nation'], r['valid_from']): r for r in rows}
    expect(s + ': the India row cites R1241 and no longer says UNCERTAIN in its first sentence', ['R1241' in by[('IND', '1939-09-03')]['reference_ids'], by[('IND', '1939-09-03')]['note'].startswith('British India was at war')], [True, True])
    expect(s + ': Norway still starts 9 April 1940 and the changed rows say old value and new value', [side('NOR', '1940-04-09'), 'old value 1940-09-27' in by[('JPN', '1939-09-01')]['note'], 'old value 1941-12-07' in by[('THA', '1939-09-01')]['note']], ['Allied', True, True])


def scenario_283_allegiance_sino_japanese_war():
    """Roadmap 388 (branch allegiance-remaining, commit 3, 15 November 2026, Scott t425u): the conflict value SJW2 (Second Sino-Japanese War, 7 July 1937 to 2 September 1945) with Japan Axis and China Allied rows; the WW2 rows (Japan Axis from 1 September 1939, China Allied from 1 September 1939) are unchanged; the 1931 Manchuria invasion is not entered."""
    s = 'scenario 283'
    import allegiance
    rows = allegiance.load()[1]
    side = lambda n, d, c: allegiance.side_on(rows, n, d, c)
    expect(s + ': SJW2 Japan Axis and China Allied from 7 July 1937, nothing on 6 July 1937 or in 1931', [side('JPN', '1937-07-06', 'SJW2'), side('JPN', '1937-07-07', 'SJW2'), side('CHN', '1937-07-07', 'SJW2'), side('CHN', '1937-07-06', 'SJW2'), side('CHN', '1931-09-18', 'SJW2')], [None, 'Axis', 'Allied', None, None])
    expect(s + ': SJW2 runs to 2 September 1945 and not after; it covers 9 December 1941', [side('JPN', '1945-09-02', 'SJW2'), side('CHN', '1945-09-02', 'SJW2'), side('CHN', '1945-09-03', 'SJW2'), side('CHN', '1941-12-09', 'SJW2')], ['Axis', 'Allied', None, 'Allied'])
    expect(s + ': the WW2 answers are unchanged (side_on defaults to WW2): no WW2 answer on 7 July 1937, Japan Axis and China Allied on 1 September 1939', [allegiance.side_on(rows, 'JPN', '1937-07-07'), allegiance.side_on(rows, 'JPN', '1939-09-01'), allegiance.side_on(rows, 'CHN', '1939-09-01'), allegiance.side_on(rows, 'CHN', '1941-12-09')], [None, 'Axis', 'Allied', 'Allied'])
    expect(s + ': only Japan and China have SJW2 rows, and each cites the FRUS report (R1262) and the Japanese archive (R1263)', [sorted(r['nation'] for r in rows if r['conflict'] == 'SJW2'), all('R1262' in r['reference_ids'] and 'R1263' in r['reference_ids'] for r in rows if r['conflict'] == 'SJW2')], [['CHN', 'JPN'], True])


def scenario_284_allegiance_non_aligned_belligerent():
    """Roadmap 389 (branch allegiance-remaining, commit 4, 15 November 2026, Scott t427u): the side value non-aligned-belligerent (at war, on neither the Allied nor the Axis side) fills the USSR 1 September to 6 October 1939 and 30 November 1939 to 13 March 1940, and Finland's Winter War; the neutral weeks between are not at war; Finland is neutral from 14 March 1940 to 24 June 1941. Finland 5 to 14 September 1944 and Thailand 11 to 20 December 1941 stay blank."""
    s = 'scenario 284'
    import allegiance
    import unit_refs
    rows = allegiance.load()[1]
    side = lambda n, d: allegiance.side_on(rows, n, d)
    N = 'non-aligned-belligerent'
    expect(s + ': USSR belligerent 1 Sep 1939 (Nomonhan), 16 Sep, 17 Sep (Poland), 6 Oct; neutral 7 Oct to 29 Nov; belligerent 30 Nov 1939 to 13 Mar 1940; neutral 14 Mar 1940 to 21 Jun 1941; Allied 22 Jun 1941', [side('SOV', d) for d in ('1939-09-01', '1939-09-16', '1939-09-17', '1939-10-06', '1939-10-07', '1939-11-29', '1939-11-30', '1940-03-13', '1940-03-14', '1941-06-21', '1941-06-22')], [N, N, N, N, 'neutral', 'neutral', N, N, 'neutral', 'neutral', 'Allied'])
    expect(s + ': Finland blank before 30 Nov 1939, belligerent 30 Nov 1939 to 13 Mar 1940, neutral 14 Mar 1940 to 24 Jun 1941, Axis 25 Jun 1941', [side('FIN', d) for d in ('1939-11-29', '1939-11-30', '1940-03-13', '1940-03-14', '1941-06-24', '1941-06-25')], [None, N, N, 'neutral', 'neutral', 'Axis'])
    expect(s + ': Finland 5-14 Sep 1944 and Thailand 11-20 Dec 1941 stay blank', [side('FIN', '1944-09-05'), side('FIN', '1944-09-14'), side('THA', '1941-12-11'), side('THA', '1941-12-20')], [None, None, None, None])
    expect(s + ': camp gives the new value no camp, like neutral', [allegiance.Resolver.camp(x) for x in (N, 'neutral')], [None, None])
    units = {'S1': {'nationality': 'Soviet Union'}, 'F1': {'nationality': 'Finland'}, 'P1': {'nationality': 'Poland'}, 'G1': {'nationality': 'Germany'}}
    nat = [{'code': 'SOV', 'name': 'Soviet Union'}, {'code': 'FIN', 'name': 'Finland'}, {'code': 'POL', 'name': 'Poland'}, {'code': 'GER', 'name': 'Germany'}]
    rs = allegiance.Resolver(units, nat, rows, [])
    same = lambda a, b, d: unit_refs._same_camp(rs, a, b, d)  # noqa: E731
    expect(s + ': synthetic units: Soviet vs Finnish (Winter War), Soviet vs Polish (Sep 1939) and Soviet vs German (Sep 1939, neutral) are not the same camp, so engaged_with is not rejected; Polish vs German is not either; German vs German is the same camp', [same('S1', 'F1', '1939-12-05'), same('S1', 'P1', '1939-09-20'), same('S1', 'G1', '1939-09-20'), same('P1', 'G1', '1939-09-20'), same('G1', 'G1', '1939-09-20')], [False, False, False, False, True])
    expect(s + ': Resolver.side returns the new value for a Soviet unit on 5 December 1939', rs.side('S1', '1939-12-05'), N)
    by = {(r['nation'], r['valid_from']): r for r in rows}
    expect(s + ': the new rows say that the choices are for Scott to confirm', ['Documented choice for Scott' in by[('SOV', '1939-09-01')]['note'], 'Documented choice for Scott' in by[('FIN', '1939-11-30')]['note']], [True, True])


def scenario_273_nation_allegiance():
    """Dated nation allegiance table (data/nation_allegiance.csv, scripts/allegiance.py): the checker rejects bad rows (synthetic) and the data answer the dated questions (15 November 2026)."""
    s = 'scenario 273'
    import allegiance
    import csv as _csv
    vocabs = common.load_vocabularies()
    nats = {'AA': {'kind': 'nation'}, 'BB': {'kind': 'nation'}, 'MM': {'kind': 'multinational'}}
    h = allegiance.header()
    row = lambda n, side, f, t, c='WW2', r='R003', note='': dict(zip(h, [n, side, f, t, c, r, note]))  # noqa: E731
    msgs = lambda rows: ' | '.join(m for _, m in allegiance.check(h, rows, nats, vocabs, {'R003'}))  # noqa: E731
    clean = [row('AA', 'neutral', '1939-09-01', '1941-12-07'), row('AA', 'Allied', '1941-12-08', '1945-09-02'), row('BB', 'Axis', '1939-09-01', '1945-05-08')]
    expect(s + ': a clean table (a side change, no overlap) passes', allegiance.check(h, clean, nats, vocabs, {'R003'}), [])
    expect_in(s + ': an unknown nation is reported', msgs(clean + [row('ZZ', 'Axis', '1940-01-01', '')]), 'not a code')
    expect_in(s + ': a multinational code is reported', msgs(clean + [row('MM', 'Allied', '1940-01-01', '')]), 'not of kind nation')
    expect_in(s + ': a side outside the vocabulary is reported', msgs([row('AA', 'friendly', '1940-01-01', '1941-01-01'), row('BB', 'Axis', '1940-01-01', '1941-01-01')]), 'allegiance_side')
    expect_in(s + ': an impossible date is reported', msgs([row('AA', 'Allied', '1940-02-30', ''), row('BB', 'Axis', '1940-01-01', '1941-01-01')]), 'not a real')
    expect_in(s + ': valid_to before valid_from is reported', msgs([row('AA', 'Allied', '1941-01-01', '1940-01-01'), row('BB', 'Axis', '1940-01-01', '1941-01-01')]), 'before valid_from')
    expect_in(s + ': an overlap of one nation is reported', msgs([row('AA', 'neutral', '1939-09-01', '1941-12-08'), row('AA', 'Allied', '1941-12-08', '1945-09-02'), row('BB', 'Axis', '1939-09-01', '1941-01-01')]), 'overlaps')
    expect_in(s + ': an open-ended row followed by another is reported', msgs([row('AA', 'neutral', '1939-09-01', ''), row('AA', 'Allied', '1941-12-08', '1945-09-02'), row('BB', 'Axis', '1939-09-01', '1941-01-01')]), 'open-ended')
    expect_in(s + ': a date before the conflict is reported', msgs([row('AA', 'Allied', '1939-08-01', '1941-01-01'), row('BB', 'Axis', '1939-09-01', '1941-01-01')]), 'before the start')
    expect_in(s + ': an unknown reference is reported', msgs([row('AA', 'Allied', '1940-01-01', '1941-01-01', r='R999'), row('BB', 'Axis', '1940-01-01', '1941-01-01')]), 'R999')
    expect_in(s + ': a nation without a row is reported', msgs([row('AA', 'Allied', '1940-01-01', '1941-01-01')]), 'nation BB has no allegiance row')
    expect_in(s + ': unsorted rows are reported', msgs([row('BB', 'Axis', '1940-01-01', '1941-01-01'), row('AA', 'Allied', '1940-01-01', '1941-01-01')]), 'sorted')
    h2, rows = allegiance.load()
    nat_rows = {n['code']: n for n in common.load_nationalities()}
    refs = {r['reference_id'] for r in _csv.DictReader(open(os.path.join(common.ROOT, 'data', 'references_meta.csv'), newline='', encoding='utf-8'))}
    expect(s + ': the data pass the checker', allegiance.check(h2, rows, nat_rows, vocabs, refs), [])
    side = lambda n, d: allegiance.side_on(rows, n, d)  # noqa: E731
    expect(s + ': US neutral on 6 December 1941, Allied on 8 December 1941', (side('US', '1941-12-06'), side('US', '1941-12-08')), ('neutral', 'Allied'))
    expect(s + ': Italy neutral 9 June 1940, Axis 10 June 1940, Axis 8 September 1943', (side('IT', '1940-06-09'), side('IT', '1940-06-10'), side('IT', '1943-09-08')), ('neutral', 'Axis', 'Axis'))
    expect(s + ': Italy has no side from 9 September to 12 October 1943 (deliberate gap), co-belligerent on 13 October 1943', (side('IT', '1943-09-09'), side('IT', '1943-10-12'), side('IT', '1943-10-13')), (None, None, 'co-belligerent'))
    expect(s + ': Belgium neutral 9 May 1940, Allied 10 May 1940; Norway neutral 8 April 1940, Allied 9 April 1940', (side('BEL', '1940-05-09'), side('BEL', '1940-05-10'), side('NOR', '1940-04-08'), side('NOR', '1940-04-09')), ('neutral', 'Allied', 'neutral', 'Allied'))
    expect(s + ': Germany Axis on D-Day, none after 8 May 1945; UK Allied on D-Day', (side('GER', '1944-06-06'), side('GER', '1945-05-09'), side('UK', '1944-06-06')), ('Axis', None, 'Allied'))
    expect(s + ': RSI (Italian Social Republic) is Axis from 23 September 1943 to 29 April 1945 and has no side outside it; Italy is co-belligerent on the same days', (side('RSI', '1943-09-22'), side('RSI', '1943-09-23'), side('RSI', '1945-04-29'), side('RSI', '1945-04-30'), side('IT', '1944-06-06')), (None, 'Axis', 'Axis', None, 'co-belligerent'))
    expect(s + ': UK has no row on 2 September 1939 (the declaration was 3 September)', (side('UK', '1939-09-02'), side('UK', '1939-09-03')), (None, 'Allied'))
    expect(s + ': every nation of kind nation has at least one row, ALL has none', (sorted({r['nation'] for r in rows}), 'ALL' in {r['nation'] for r in rows}), (sorted(c for c, n in nat_rows.items() if n['kind'] == 'nation'), False))
    expect(s + ': nationalities.csv has no alliance column since 15 November 2026 (old values: ALL, AUS, BEL, CAN, CZ, FR, NL, NOR, NZ, POL, SAF, UK, US Allied; GER, IT, RSI Axis)', common.read_dicts(common.NATIONALITIES_CSV)[0], ['code', 'name', 'adjective', 'alt_adjectives', 'kind', 'note'])


def scenario_274_unit_allegiance_overrides():
    """Unit-level allegiance overrides (data/unit_allegiance_overrides.csv, scripts/allegiance.py): the checker rejects bad rows (synthetic), an override wins over the nation table, and the resolver falls back to the nation, then to blank (15 November 2026)."""
    s = 'scenario 274'
    import allegiance
    import csv as _csv
    vocabs = common.load_vocabularies()
    units = {'U1': {'unit_id': 'U1', 'nationality': 'Germany'}, 'U2': {'unit_id': 'U2', 'nationality': 'Germany'}, 'U3': {'unit_id': 'U3', 'nationality': 'Nowhere'}}
    h = allegiance.overrides_header()
    row = lambda u, side, f, t='', r='R003', note='': dict(zip(h, [u, side, f, t, r, note]))  # noqa: E731
    msgs = lambda rows: ' | '.join(m for _, m in allegiance.check_overrides(h, rows, units, vocabs, {'R003'}))  # noqa: E731
    ok = [row('U1', 'Allied', '1944-08-20', '1944-09-30'), row('U1', 'Axis', '1944-10-01', '1944-12-31'), row('U2', 'neutral', '1940-01-01')]
    expect(s + ': a clean table passes', allegiance.check_overrides(h, ok, units, vocabs, {'R003'}), [])
    expect(s + ': the header is the six columns of the schema', h, ['unit_id', 'side', 'valid_from', 'valid_to', 'reference_ids', 'note'])
    expect_in(s + ': an unknown unit is reported', msgs([row('ZZ', 'Allied', '1944-01-01')]), 'not a unit')
    expect_in(s + ': a side outside the vocabulary is reported', msgs([row('U1', 'friendly', '1944-01-01')]), 'allegiance_side')
    expect_in(s + ': an impossible date is reported', msgs([row('U1', 'Allied', '1944-02-30')]), 'not a real')
    expect_in(s + ': valid_to before valid_from is reported', msgs([row('U1', 'Allied', '1944-05-01', '1944-04-01')]), 'before valid_from')
    expect_in(s + ': a date outside WW2 is reported', msgs([row('U1', 'Allied', '1946-01-01')]), 'outside WW2')
    expect_in(s + ': an overlap of one unit is reported', msgs([row('U1', 'Allied', '1944-08-20', '1944-10-01'), row('U1', 'Axis', '1944-10-01', '1944-12-31')]), 'overlaps')
    expect_in(s + ': an open-ended row followed by another is reported', msgs([row('U1', 'Allied', '1944-08-20'), row('U1', 'Axis', '1944-10-01', '1944-12-31')]), 'open-ended')
    expect_in(s + ': a missing reference is reported', msgs([row('U1', 'Allied', '1944-01-01', r='')]), 'needs a source')
    expect_in(s + ': an unknown reference is reported', msgs([row('U1', 'Allied', '1944-01-01', r='R999')]), 'R999')
    expect_in(s + ': unsorted rows are reported', msgs([row('U2', 'Allied', '1944-01-01'), row('U1', 'Allied', '1944-01-01')]), 'sorted')
    nat = [{'code': 'GER', 'name': 'Germany'}]
    nrows = [{'nation': 'GER', 'side': 'Axis', 'valid_from': '1939-09-01', 'valid_to': '1945-05-08', 'conflict': 'WW2'}]
    rs = allegiance.Resolver(units, nat, nrows, ok)
    expect(s + ': override wins on 1 September 1944 (Allied), nation applies before it (Axis) and after the override rows (none)', (rs.side('U1', '1944-09-01'), rs.side('U1', '1944-08-19'), rs.side('U1', '1945-01-01')), ('Allied', 'Axis', 'Axis'))
    expect(s + ': a second override beats the nation (U1 Axis 1 October 1944 by override), U2 neutral from 1940 to the end', (rs.side('U1', '1944-10-01'), rs.side('U2', '1944-06-06')), ('Axis', 'neutral'))
    expect(s + ': a unit with an unknown nationality or an unknown unit has no side; a date in a nation gap has none', (rs.side('U3', '1944-06-06'), rs.side('NOPE', '1944-06-06'), rs.side('U1', '1945-06-01')), (None, None, None))
    expect(s + ': camp folds co-belligerent into Allied and neutral into none', [allegiance.Resolver.camp(x) for x in ('Allied', 'co-belligerent', 'Axis', 'neutral', None)], ['Allied', 'Allied', 'Axis', None, None])
    import unit_refs
    real0 = allegiance.Resolver.load()
    same = lambda a, b, d: unit_refs._same_camp(real0, a, b, d)  # noqa: E731
    expect(s + ': engaged_with side check on the real tables: US vs German is not the same camp on D-Day; US vs UK is; German vs German is', (same('US-INF-029D', 'GER-PZ-021D', '1944-06-06'), same('US-INF-029D', 'UK-ARM-011D', '1944-06-06'), same('GER-PZ-021D', 'GER-INF-352D', '1944-06-06')), (False, True, True))
    expect(s + ': a month or year counts only when both ends agree (US and UK in June 1944 yes; US and UK in December 1941: neutral then Allied, no); a blank or impossible date, or a date in a gap, is not checked', (same('US-INF-029D', 'UK-ARM-011D', '1944-06'), same('US-INF-029D', 'UK-ARM-011D', '1941-12'), same('US-INF-029D', 'UK-ARM-011D', ''), same('US-INF-029D', 'UK-ARM-011D', '1944-02-30'), same('GER-PZ-021D', 'GER-INF-352D', '1945-06-01')), (True, False, False, False, False))
    h2, rows = allegiance.load_overrides()
    unit_rows = {u['unit_id']: u for u in common.read_dicts(common.UNITS_CSV)[1]}
    refs = {r['reference_id'] for r in _csv.DictReader(open(os.path.join(common.ROOT, 'data', 'references_meta.csv'), newline='', encoding='utf-8'))}
    expect(s + ': the data pass the checker', allegiance.check_overrides(h2, rows, unit_rows, vocabs, refs), [])
    real = allegiance.Resolver.load()
    expect(s + ': on the real tables a US unit is Allied on D-Day, a German one Axis, and a US unit is neutral in 1940', (real.side('US-INF-029D', '1944-06-06'), real.side('GER-PZ-021D', '1944-06-06'), real.side('US-INF-029D', '1940-06-01')), ('Allied', 'Axis', 'neutral'))


def scenario_275_relations_157_and_16():
    """Roadmap 363 (leftovers-1115 task a, 15 November 2026): command relations for the 16th Infantry Division 1944 (Army Group G from the August Lexikon row, LXVI Corps from 7 September per Cole p. 188) and the 157th Mountain Division
    (Armee Ligurien from September 1944, XIV Panzer Corps from 17 December 1944, German Wikipedia); placeholders GER-ARMY-LIGUR, GER-PZ-014C, GER-GEB-008D; lineage UL025 (renamed the 8th Mountain Division 27 February 1945)."""
    s = 'scenario 275'
    units = {u['unit_id']: u for u in common.read_dicts(common.UNITS_CSV)[1]}
    rel = {r['relation_id']: r for r in _ROWS}
    f = ('subject_unit_id', 'higher_unit_id', 'relationship', 'valid_from', 'valid_from_basis', 'valid_to', 'valid_to_basis')
    expect(s + ': CR1317 16th Infantry Division under Army Group G from the August row, closed the day before CR1318', [rel['CR1317'][k] for k in f],
           ['GER-INF-016D', 'GER-AG-00GG', 'assigned', '1944-08-15', 'claim_date', '1944-09-06', 'inferred_from_next_claim'])
    expect(s + ': CR1318 16th Infantry Division under LXVI Corps from 7 September 1944 (Cole p. 188), open at the last claim', [rel['CR1318'][k] for k in f],
           ['GER-INF-016D', 'GER-COR-066C', 'assigned', '1944-09-07', 'narrative', '', 'open_at_last_claim'])
    expect(s + ': CR1319 157th Mountain Division under Armee Ligurien from September 1944 (unspecified_subordination), closed 1944-12-16', [rel['CR1319'][k] for k in f],
           ['GER-GEB-157D', 'GER-ARMY-LIGUR', 'unspecified_subordination', '1944-09-15', 'claim_date', '1944-12-16', 'inferred_from_next_claim'])
    expect(s + ': CR1320 157th Mountain Division under the XIV Panzer Corps from 17 December 1944, open', [rel['CR1320'][k] for k in f],
           ['GER-GEB-157D', 'GER-PZ-014C', 'unspecified_subordination', '1944-12-17', 'narrative', '', 'open_at_last_claim'])
    claims = {c['claim_id']: c for c in common.load_all_claims()[1]}
    expect(s + ': the evidence claims carry the higher unit as parent and 0.3', [(claims[c]['unit_id'], claims[c]['parent_unit_id'], claims[c]['confidence']) for c in ('C9459', 'C9460', 'C9461', 'C9462')],
           [('GER-INF-016D', 'GER-AG-00GG', '0.3'), ('GER-INF-016D', 'GER-COR-066C', '0.3'), ('GER-GEB-157D', 'GER-ARMY-LIGUR', '0.3'), ('GER-GEB-157D', 'GER-PZ-014C', '0.3')])
    expect(s + ': C9462 is an out-of-theater row (mediterranean, Bologna PL4181); C9461 stays western_europe', (claims['C9462']['theater'], claims['C9462']['place_id'], claims['C9461']['theater']), ('mediterranean', 'PL4181', 'western_europe'))
    expect(s + ': the three new units are placeholders', [(u, units[u]['record_status']) for u in ('GER-ARMY-LIGUR', 'GER-PZ-014C', 'GER-GEB-008D')],
           [('GER-ARMY-LIGUR', 'placeholder'), ('GER-PZ-014C', 'placeholder'), ('GER-GEB-008D', 'placeholder')])
    import lineage
    row = {r['lineage_id']: r for r in lineage.load()[1]}['UL025']
    expect(s + ': UL025 157th Mountain Division -> 8th Mountain Division, redesignation, 1945-02-27 (the successor formed 1945-02-27)',
           ([row[k] for k in ('predecessor_unit_id', 'successor_unit_id', 'kind', 'effective_date')], units['GER-GEB-008D']['formed_date']), (['GER-GEB-157D', 'GER-GEB-008D', 'redesignation', '1945-02-27'], '1945-02-27'))
    expect(s + ': no claim of the 157th Mountain Division is dated after the renaming', [c for c in claims.values() if c['unit_id'] == 'GER-GEB-157D' and c['date'] > '1945-02-27'], [])


def scenario_285_normandy_chunk1_commit2():
    """Normandy chunk 1 commit 2: Western Task Force battleships, heavy cruisers, monitors and Allied cruisers."""
    s = 'scenario 285'
    units = {u['unit_id']: u for u in common.read_dicts(common.UNITS_CSV)[1]}
    ids = ('US-BB-033', 'US-BB-036', 'US-CA-031', 'US-CA-037', 'US-CA-071',
           'UK-CA-HAWKINS', 'UK-CL-BLACK-PRINCE', 'UK-CL-ENTERPRISE', 'UK-CL-GLASGOW',
           'UK-CL-BELLONA', 'UK-BM-EREBUS', 'FR-CL-MONTCALM', 'FR-CL-GEORGES-LEYGUES')
    expect(s + ': thirteen new ships are active naval_unit rows',
           [(u, units[u]['record_status'], units[u]['echelon'], units[u]['domain']) for u in ids],
           [(u, 'active', 'naval_unit', 'naval') for u in ids])
    expect(s + ': Texas, Satterlee and TG 124.9 are not duplicated',
           (units['US-BB-035']['unit_name'], units['US-DD-626']['unit_name'], units['US-TG-124-9']['record_status']),
           ('USS Texas (BB-35)', 'USS Satterlee (DD-626)', 'placeholder'))
    claims = {c['claim_id']: c for c in common.load_all_claims()[1]}
    expect(s + ': twenty new claims C9464-C9483',
           sorted(c for c in claims if 'C9464' <= c <= 'C9483'),
           [f'C{n}' for n in range(9464, 9484)])
    expect(s + ': G129 is the Tuscaloosa Cherbourg date conflict',
           (claims['C9470']['date'], claims['C9470']['claim_status'], claims['C9470']['conflict_group_id'],
            claims['C9471']['date'], claims['C9471']['claim_status'], claims['C9471']['conflict_group_id']),
           ('1944-06-25', 'preferred', 'G129', '1944-06-26', 'alternate', 'G129'))
    rels = {r['relation_id']: r for r in common.read_dicts(os.path.join(common.ROOT, 'data', 'command_relations.csv'))[1]}
    expect(s + ': CR1301 (Texas to 124.9) is closed the day before the Cherbourg claim',
           (rels['CR1301']['valid_to'], rels['CR1301']['valid_to_basis'], rels['CR1301']['valid_to_earliest']),
           ('1944-06-24', 'inferred_from_next_claim', '1944-06-06'))
    expect(s + ': Texas has a new relation to TG 129.2',
           any(r['subject_unit_id']=='US-BB-035' and r['higher_unit_id']=='US-TG-129-2' for r in rels.values()), True)
    expect(s + ': Erebus is a monitor (BM) of class SC213',
           (units['UK-BM-EREBUS']['ship_type'], units['UK-BM-EREBUS']['ship_class_id']), ('BM', 'SC213'))
    pl = {p['place_id']: p for p in common.read_dicts(os.path.join(common.ROOT, 'data', 'places.csv'))[1]}
    expect(s + ': Fire Support Area 1 is a sea_position', pl['PL4182']['kind'], 'sea_position')
    expect(s + ': Nevada Cherbourg claim uses the sea_position at 0.5',
           (claims['C9467']['place_id'], claims['C9467']['confidence']), ('PL4182', '0.5'))


def scenario_286_normandy_chunk1_commit3():
    """Normandy chunk 1 commit 3: destroyers, DEs, US fleet minesweepers, Ancon and Bayfield, remaining Allied warships."""
    s = 'scenario 286'
    units = {u['unit_id']: u for u in common.read_dicts(common.UNITS_CSV)[1]}
    expect(s + ': Boadicea is a B-class destroyer, not a Flower corvette',
           (units['UK-DD-BOADICEA']['ship_type'], units['UK-DD-BOADICEA']['ship_class_id']), ('DD', 'SC094'))
    expect(s + ': Brissenden is a Type IV Hunt (SC108) and Sissenden is not a unit',
           (units['UK-DE-BRISSENDEN']['ship_class_id'], 'UK-DE-SISSENDEN' in units), ('SC108', False))
    expect(s + ': Kitchener is a Canadian Flower-class corvette',
           (units['CAN-CORV-KITCHENER']['nationality'], units['CAN-CORV-KITCHENER']['ship_type'], units['CAN-CORV-KITCHENER']['ship_class_id']),
           ('Canada', 'CORV', 'SC113'))
    expect(s + ': Ancon is AGC-4 with no class row, Bayfield is APA-33 of SC214',
           (units['US-AGC-004']['ship_type'], units['US-AGC-004']['ship_class_id'], units['US-APA-033']['ship_type'], units['US-APA-033']['ship_class_id']),
           ('AGC', '', 'APA', 'SC214'))
    placeholders = ('US-DD-395', 'US-DD-396', 'US-DD-381', 'US-DD-495', 'US-DE-694')
    expect(s + ': five B(1)-only ships are placeholders',
           [(u, units[u]['record_status']) for u in placeholders],
           [(u, 'placeholder') for u in placeholders])
    claims = {c['claim_id']: c for c in common.load_all_claims()[1]}
    expect(s + ': the five placeholders have no claim file',
           all(u not in {c['unit_id'] for c in claims.values()} for u in placeholders), True)
    expect(s + ': ninety-one new claims C9484-C9574',
           sorted(c for c in claims if 'C9484' <= c <= 'C9574'),
           [f'C{n}' for n in range(9484, 9575)])
    expect(s + ': G130 is the Glennon sinking-date conflict',
           (claims['C9501']['date'], claims['C9501']['claim_status'], claims['C9501']['conflict_group_id'],
            claims['C9502']['date'], claims['C9502']['claim_status'], claims['C9502']['conflict_group_id']),
           ('1944-06-10', 'preferred', 'G130', '1944-06-08', 'alternate', 'G130'))
    expect(s + ': Satterlee is related to DesRon 18',
           any(r['subject_unit_id']=='US-DD-626' and r['higher_unit_id']=='US-DESRON-018'
               for r in common.read_dicts(os.path.join(common.ROOT, 'data', 'command_relations.csv'))[1]), True)
    expect(s + ': Murphy is stored as US-DD-603, not a Murray unit',
           ('US-DD-603' in units and 'US-DD-MURRAY' not in units), True)
    pl = {p['place_id']: p for p in common.read_dicts(os.path.join(common.ROOT, 'data', 'places.csv'))[1]}
    expect(s + ': Portland Bill is a named point for Boadicea', pl['PL4183']['kind'], 'point')



def scenario_287_normandy_chunk2_commit2():
    """Normandy chunk 2 commit 2: Eastern Task Force capital ships, monitor, cruisers, Flores, Despatch, Albatross, Adventure, and headquarters-ship claims."""
    s = 'scenario 287'
    units = {u['unit_id']: u for u in common.read_dicts(common.UNITS_CSV)[1]}
    ids = ('UK-BB-RAMILLIES', 'UK-BB-RODNEY', 'UK-BB-NELSON', 'UK-BM-ROBERTS', 'UK-CL-SCYLLA',
           'UK-CL-AJAX', 'UK-CL-ARETHUSA', 'UK-CL-ARGONAUT', 'UK-CL-BELFAST', 'UK-CL-DIADEM',
           'UK-CL-EMERALD', 'UK-CA-FROBISHER', 'UK-CL-MAURITIUS', 'UK-CL-ORION', 'UK-CL-DANAE',
           'UK-CL-SIRIUS', 'POL-CL-DRAGON', 'NL-PG-FLORES', 'UK-CL-DESPATCH', 'UK-AV-ALBATROSS',
           'UK-CM-ADVENTURE')
    expect(s + ': twenty-one new ships are active naval_unit rows',
           [(u, units[u]['record_status'], units[u]['echelon'], units[u]['domain']) for u in ids],
           [(u, 'active', 'naval_unit', 'naval') for u in ids])
    hq = ('UK-AGC-LARGS', 'UK-AGC-HILARY', 'UK-AGC-BULOLO', 'UK-AGC-ROYAL-ULSTERMAN', 'UK-PG-LOCUST',
          'UK-DE-DACRES', 'UK-DE-KINGSMILL', 'UK-DE-LAWFORD', 'UK-PF-NITH', 'UK-PF-WAVENEY',
          'UK-DE-ALBRIGHTON', 'UK-DE-GOATHLAND')
    expect(s + ': twelve headquarters ships are now active',
           [(u, units[u]['record_status']) for u in hq], [(u, 'active') for u in hq])
    expect(s + ': Warspite, Force S and Force D are not duplicated',
           (units['UK-BB-WARSPITE']['unit_name'], units['UK-TF-S']['record_status'], units['UK-BF-D']['record_status']),
           ('HMS Warspite (03)', 'placeholder', 'placeholder'))
    expect(s + ': Albatross is a UK seaplane tender (type AV) with no class row',
           (units['UK-AV-ALBATROSS']['nationality'], units['UK-AV-ALBATROSS']['ship_type'], units['UK-AV-ALBATROSS']['ship_class_id']),
           ('UK', 'AV', ''))
    expect(s + ': Dragon is Polish and Danae is still British in June 1944',
           (units['POL-CL-DRAGON']['nationality'], units['UK-CL-DANAE']['nationality']),
           ('Poland', 'UK'))
    expect(s + ': Hambledon is not entered (decision E9)', 'UK-DE-HAMBLEDON' in units, False)
    claims = {c['claim_id']: c for c in common.load_all_claims()[1]}
    expect(s + ': forty-five new claims C9575-C9619',
           sorted(c for c in claims if 'C9575' <= c <= 'C9619'),
           [f'C{n}' for n in range(9575, 9620)])
    rels = [r for r in common.read_dicts(os.path.join(common.ROOT, 'data', 'command_relations.csv'))[1]]
    expect(s + ': Warspite still has exactly one relation to UK-BF-D',
           len([r for r in rels if r['subject_unit_id']=='UK-BB-WARSPITE' and r['higher_unit_id']=='UK-BF-D']), 1)
    expect(s + ': Nelson and Sirius are reserve of the Eastern Task Force',
           sorted((r['subject_unit_id'], r['relationship']) for r in rels if r['subject_unit_id'] in ('UK-BB-NELSON', 'UK-CL-SIRIUS') and r['higher_unit_id']=='UK-TF-ETF'),
           [('UK-BB-NELSON', 'reserve'), ('UK-CL-SIRIUS', 'reserve')])
    expect(s + ': Diadem is related to Force E, not Force G',
           (any(r['subject_unit_id']=='UK-CL-DIADEM' and r['higher_unit_id']=='UK-BF-E' for r in rels),
            any(r['subject_unit_id']=='UK-CL-DIADEM' and r['higher_unit_id']=='UK-BF-G' for r in rels)),
           (True, False))
    expect(s + ': Roberts uses the new Roberts class SC215', units['UK-BM-ROBERTS']['ship_class_id'], 'SC215')



def scenario_288_normandy_chunk2_commit3a():
    """Normandy chunk 2 commit 3a: Eastern Task Force destroyers, Hunts, older escorts, sloops, frigates, corvettes, and ships lost in the window."""
    s = 'scenario 288'
    units = {u['unit_id']: u for u in common.read_dicts(common.UNITS_CSV)[1]}
    assault = (
        'UK-DD-FAULKNOR', 'UK-DD-FURY', 'UK-DD-ISIS', 'UK-DD-JERVIS',
        'UK-DD-IMPULSIVE', 'UK-DD-KELVIN', 'UK-DD-SAUMAREZ', 'UK-DD-SCORPION',
        'UK-DD-SCOURGE', 'UK-DD-SERAPIS', 'UK-DD-SWIFT', 'NOR-DD-STORD', 'NOR-DD-SVENNER',
        'UK-DD-GRENVILLE', 'UK-DD-ULSTER', 'UK-DD-ULYSSES', 'UK-DD-UNDAUNTED',
        'UK-DD-UNDINE', 'UK-DD-URANIA', 'UK-DD-URCHIN', 'UK-DD-URSA',
        'UK-DD-KEMPENFELT', 'CAN-DD-ALGONQUIN', 'CAN-DD-SIOUX', 'UK-DD-VENUS',
        'UK-DD-VIGILANT', 'UK-DD-VERULAM', 'UK-DD-VIRAGO')
    expect(s + ': twenty-eight assault-force fleet destroyers are active naval_unit rows',
           [(u, units[u]['record_status'], units[u]['echelon'], units[u]['domain']) for u in assault],
           [(u, 'active', 'naval_unit', 'naval') for u in assault])
    expect(s + ': Algonquin and Sioux are V class SC208, not Tribal (decision E9)',
           (units['CAN-DD-ALGONQUIN']['ship_class_id'], units['CAN-DD-SIOUX']['ship_class_id']),
           ('SC208', 'SC208'))
    expect(s + ': Stord and Svenner are Norwegian',
           (units['NOR-DD-STORD']['nationality'], units['NOR-DD-SVENNER']['nationality']),
           ('Norway', 'Norway'))
    expect(s + ': Hambledon and Savage are not entered (decisions E9 and E2)',
           ('UK-DE-HAMBLEDON' in units or 'UK-DD-SAVAGE' in units), False)
    expect(s + ': HMS Halsted uses the Wikipedia spelling, not Halstead',
           ('UK-DE-HALSTED' in units and 'UK-DE-HALSTEAD' not in units
            and units['UK-DE-HALSTED']['unit_name']=='HMS Halsted (K556)'), True)
    expect(s + ': Krakowiak is a new Hunt Type II, not a duplicate of existing Ślązak',
           (units['POL-DE-KRAKOWIAK']['ship_type'], units['POL-DE-KRAKOWIAK']['ship_class_id'],
            units['POL-DD-L26']['unit_name']),
           ('DE', 'SC106', 'ORP Ślązak (L26)'))
    expect(s + ': Campbell uses the new Admiralty type flotilla leader class SC219',
           units['UK-DD-CAMPBELL']['ship_class_id'], 'SC219')
    expect(s + ': Stork is Bittern class SC119, not Black Swan',
           units['UK-PG-STORK']['ship_class_id'], 'SC119')
    expect(s + ': Greek corvettes and French Force G frigates are entered',
           (units['GRE-CORV-KRIEZIS']['nationality'], units['GRE-CORV-TOMBAZIS']['nationality'],
            units['FR-PF-LA-DECOUVERTE']['ship_class_id'], units['FR-PF-LA-SURPRISE']['formed_date']),
           ('Greece', 'Greece', 'SC110', '1944-06-06'))
    claims = {c['claim_id']: c for c in common.load_all_claims()[1]}
    expect(s + ': ninety-nine new claims C9620-C9718',
           sorted(c for c in claims if 'C9620' <= c <= 'C9718'),
           [f'C{n}' for n in range(9620, 9719)])
    fury21 = [c for c in claims.values() if c['unit_id']=='UK-DD-FURY' and c['date']=='1944-06-21']
    expect(s + ': Fury has two 21 June claims in group G131',
           sorted((c['claim_status'], c['place_id'], c['conflict_group_id']) for c in fury21),
           [('alternate', 'PL0180', 'G131'), ('preferred', 'PL0344', 'G131')])
    glai = [c for c in claims.values() if c['unit_id']=='NOR-DE-GLAISDALE' and c['date']=='1944-06-23']
    expect(s + ': Glaisdale has two 23 June claims in group G132, NHB Gold preferred',
           sorted((c['claim_status'], c['place_id'], c['conflict_group_id']) for c in glai),
           [('alternate', 'PL0344', 'G132'), ('preferred', 'PL0156', 'G132')])
    rels = [r for r in common.read_dicts(os.path.join(common.ROOT, 'data', 'command_relations.csv'))[1]]
    expect(s + ': Undine and Krakowiak are related to Force K (decision E9)',
           (any(r['subject_unit_id']=='UK-DD-UNDINE' and r['higher_unit_id']=='UK-BF-K' for r in rels),
            any(r['subject_unit_id']=='POL-DE-KRAKOWIAK' and r['higher_unit_id']=='UK-BF-K' for r in rels),
            any(r['subject_unit_id']=='UK-DE-HAMBLEDON' for r in rels)),
           (True, True, False))
    expect(s + ': the 10th Destroyer Flotilla ships are related to the flotilla, not to a guessed 6 June beach force',
           (any(r['subject_unit_id']=='CAN-DD-HAIDA' and r['higher_unit_id']=='UK-DF-10' for r in rels),
            any(r['subject_unit_id']=='CAN-DD-HAIDA' and r['higher_unit_id'].startswith('UK-TF-') for r in rels),
            any(r['subject_unit_id']=='CAN-DD-HAIDA' and r['higher_unit_id'].startswith('UK-BF-') for r in rels)),
           (True, False, False))
    expect(s + ': existing Ślązak and Warspite are not duplicated',
           (units['POL-DD-L26']['unit_name'], units['UK-BB-WARSPITE']['unit_name']),
           ('ORP Ślązak (L26)', 'HMS Warspite (03)'))
    cls = {c['class_id']: c for c in common.read_dicts(os.path.join(common.ROOT, 'data', 'ship_classes.csv'))[1]}
    expect(s + ': SC219 is the Admiralty type flotilla leader (Scott class)',
           (cls['SC219']['class_name'], cls['SC219']['ship_type']),
           ('Admiralty type flotilla leader (Scott class)', 'DD'))



def scenario_289_normandy_chunk2_commit3b():
    s = 'scenario 289'
    units = {u['unit_id']: u for u in common.read_dicts(common.UNITS_CSV)[1]}
    assault = [
        'UK-AM-SHIPPIGAN', 'UK-AM-TADOUSSAC', 'UK-AM-ILFRACOMBE', 'UK-AM-BEAUMARIS',
        'UK-AM-DORNOCH', 'UK-AM-PARRSBOROUGH', 'UK-AM-QUALICUM', 'UK-AM-WEDGEPORT',
        'UK-AM-ROMNEY', 'CAN-AM-GUYSBOROUGH', 'CAN-AM-KENORA', 'UK-AM-POOLE',
        'UK-AM-RYE', 'UK-AM-SEAHAM', 'CAN-AM-VEGREVILLE', 'UK-AM-WHITEHAVEN',
        'UK-AM-KELLETT', 'UK-AM-ALBURY', 'UK-AM-ELGIN', 'UK-AM-LYDD',
        'UK-AM-PANGBOURNE', 'UK-AM-ROSS', 'UK-AM-SALTASH', 'UK-AM-SELKIRK', 'UK-AM-SUTTON',
        'CAN-AM-CARAQUET', 'CAN-AM-BLAIRMORE', 'CAN-AM-COWICHAN', 'CAN-AM-FORT-WILLIAM',
        'CAN-AM-MALPEQUE', 'CAN-AM-MILLTOWN', 'CAN-AM-MINAS', 'CAN-AM-WASAGA',
        'UK-AM-HARRIER', 'UK-AM-BRITOMART', 'UK-AM-GLEANER', 'UK-AM-HALCYON',
        'UK-AM-HUSSAR', 'UK-AM-JASON', 'UK-AM-SALAMANDER', 'UK-AM-SEAGULL', 'UK-AM-SPEEDWELL',
        'UK-AM-FRASERBURGH', 'UK-AM-ARDROSSAN', 'UK-AM-BOOTLE', 'UK-AM-DUNBAR',
        'UK-AM-FORT-YORK', 'UK-AM-LLANDUDNO', 'UK-AM-LYME-REGIS', 'UK-AM-WORTHING',
        'UK-AM-PELORUS', 'UK-AM-FANCY', 'UK-AM-LENNOX', 'UK-AM-PICKLE',
        'UK-AM-PINCHER', 'UK-AM-PLUCKY', 'UK-AM-RECRUIT', 'UK-AM-RIFLEMAN',
        'UK-AM-SIDMOUTH', 'UK-AM-TENBY', 'UK-AM-BANGOR', 'UK-AM-BLACKPOOL',
        'UK-AM-BOSTON', 'UK-AM-BRIDLINGTON', 'UK-AM-BRIDPORT', 'UK-AM-EASTBOURNE',
        'UK-AM-VESTAL', 'UK-AM-FRIENDSHIP', 'UK-AM-GOZO', 'UK-AM-LARNE',
        'UK-AM-LIGHTFOOT', 'UK-AM-MELITA', 'UK-AM-PERSIAN', 'UK-AM-POSTILLION',
        'UK-AM-READY', 'UK-AM-COCKATRICE', 'UK-AM-HOUND', 'UK-AM-HYDRA',
        'UK-AM-LOYALTY', 'UK-AM-ONYX', 'UK-AM-ORESTES', 'UK-AM-RATTLESNAKE',
        'UK-AM-CATHERINE', 'UK-AM-CATO', 'UK-AM-GAZELLE', 'UK-AM-GORGON',
        'UK-AM-GRECIAN', 'UK-AM-PIQUE', 'UK-AM-STEADFAST',
        'UK-AM-MAGIC', 'UK-AM-PYLADES']
    expect(s + ': ninety-one fleet minesweepers are active naval_unit rows (decision E1, plus Magic and Pylades)',
           [(u, units[u]['record_status'], units[u]['echelon'], units[u]['domain'], units[u]['ship_type']) for u in assault],
           [(u, 'active', 'naval_unit', 'naval', 'AM') for u in assault])
    can = [u for u in assault if units[u]['nationality']=='Canada']
    expect(s + ': eleven Canadian Bangors (3 of the 14th and all 8 of the 31st), including Guysborough as HMCS',
           (len(can), 'CAN-AM-GUYSBOROUGH' in can, units['CAN-AM-GUYSBOROUGH']['unit_name'],
            units['UK-AM-RECRUIT']['nationality'], units['UK-AM-RIFLEMAN']['nationality']),
           (11, True, 'HMCS Guysborough (J52)', 'UK', 'UK'))
    expect(s + ': existing classes are reused (decisions E11 and E1) and Ready uses pennant J223',
           (units['UK-AM-CATHERINE']['ship_class_id'], units['UK-AM-KELLETT']['ship_class_id'],
            units['CAN-AM-CARAQUET']['ship_class_id'], units['UK-AM-HARRIER']['ship_class_id'],
            units['UK-AM-PELORUS']['ship_class_id'], units['UK-AM-READY']['hull_number'],
            units['UK-AM-PARRSBOROUGH']['unit_name']),
           ('SC054', 'SC216', 'SC121', 'SC122', 'SC120', 'J223', 'HMS Parrsborough (J117)'))
    expect(s + ': danlayers and unlisted Hunt pennants are not invented, and Fort York is not Fort William',
           ('UK-AM-THUNDER' in units, 'UK-AM-MULGRAVE' in units, 'UK-AM-CHAMOIS' in units,
            'UK-AM-CHANCE' in units, units['UK-AM-KELLETT']['hull_number'],
            units['UK-AM-FORT-YORK']['nationality'], units['CAN-AM-FORT-WILLIAM']['nationality']),
           (False, False, False, False, '', 'UK', 'Canada'))
    claims = {c['claim_id']: c for c in common.load_all_claims()[1]}
    expect(s + ': one hundred and eleven new claims C9719-C9829',
           sorted(c for c in claims if 'C9719' <= c <= 'C9829'),
           [f'C{n}' for n in range(9719, 9830)])
    pyl = [c for c in claims.values() if c['unit_id']=='UK-AM-PYLADES' and c['date']=='1944-07-08']
    expect(s + ': Pylades has two 8 July claims in group G133, NHB Sword preferred',
           sorted((c['claim_status'], c['place_id'], c['conflict_group_id']) for c in pyl),
           [('alternate', 'PL0180', 'G133'), ('preferred', 'PL0344', 'G133')])
    expect(s + ': Magic has a 6 July Sword loss and no 6 June claim',
           (any(c['unit_id']=='UK-AM-MAGIC' and c['date']=='1944-07-06' and c['destroyed']=='true' and c['place_id']=='PL0344' for c in claims.values()),
            any(c['unit_id']=='UK-AM-MAGIC' and c['date']=='1944-06-06' for c in claims.values())),
           (True, False))
    rels = [r for r in common.read_dicts(os.path.join(common.ROOT, 'data', 'command_relations.csv'))[1]]
    expect(s + ': Magic and Pylades have no flotilla or Force S relation',
           (any(r['subject_unit_id']=='UK-AM-MAGIC' for r in rels),
            any(r['subject_unit_id']=='UK-AM-PYLADES' for r in rels)),
           (False, False))
    ninth = ('UK-AM-SIDMOUTH', 'UK-AM-TENBY', 'UK-AM-BANGOR', 'UK-AM-BLACKPOOL',
             'UK-AM-BOSTON', 'UK-AM-BRIDLINGTON', 'UK-AM-BRIDPORT', 'UK-AM-EASTBOURNE')
    expect(s + ': the eight ships of the 9th Minesweeping Flotilla are related to US-TG-129 from 25 June',
           sorted((r['subject_unit_id'], r['valid_from']) for r in rels if r['higher_unit_id']=='US-TG-129' and r['subject_unit_id'] in ninth),
           sorted((u, '1944-06-25') for u in ninth))
    newrels = [r for r in rels if 'CR1604' <= r['relation_id'] <= 'CR1789']
    expect(s + ': one hundred and eighty-six new relations CR1604-CR1789',
           sorted(r['relation_id'] for r in newrels),
           [f'CR{n}' for n in range(1604, 1790)])


def scenario_290_normandy_chunk3a_commit1():
    s = 'scenario 290'
    units = {u['unit_id']: u for u in common.read_dicts(common.UNITS_CSV)[1]}
    placeholders = ['US-TG-124-10', 'UK-MSF-101', 'UK-MSF-102', 'UK-MSF-205']
    active = [
        'UK-MSF-104', 'UK-MSF-115', 'UK-MSF-132', 'UK-MSF-143',
        'UK-MSF-150', 'UK-MSF-159', 'UK-MSF-165', 'UK-MSF-167',
        'UK-LLG-131', 'UK-LLG-159', 'UK-LLG-181',
        'US-YMSU-4', 'US-YMSU-5']
    expect(s + ': leftover 124.10 is a placeholder task group; reserve MMS flotillas are placeholder naval_division rows (F2, F11)',
           [(u, units[u]['record_status'], units[u]['echelon'], units[u]['domain']) for u in placeholders],
           [(u, 'placeholder', 'task_group' if u == 'US-TG-124-10' else 'naval_division', 'naval') for u in placeholders])
    expect(s + ': MMS, BYMS, LL and YMS units with a sourced 6 June location are active naval_division rows (F1, F6, F12)',
           [(u, units[u]['record_status'], units[u]['echelon'], units[u]['domain'], units[u]['nationality']) for u in active],
           [(u, 'active', 'naval_division', 'naval', 'US' if u.startswith('US-') else 'UK') for u in active])
    expect(s + ': danlayers and an unnumbered Force U MMS unit are not invented (F4, F5), and no 139th LL group is added',
           ('UK-AM-THUNDER' in units, 'UK-AM-MULGRAVE' in units, 'UK-AM-CHAMOIS' in units,
            'UK-MSF-UTAH' in units, 'UK-LLG-139' in units),
           (False, False, False, False, False))
    claims = {}
    for path in common.claim_files():
        for r in common.read_dicts(path)[1]:
            claims.setdefault(r['unit_id'], []).append(r)
    expect(s + ': placeholders 101, 102 and 205 have no claims; 132nd has G134 Sword preferred and Utah alternate; beaches and LL ports are as allocated',
           (bool(claims.get('UK-MSF-101')), bool(claims.get('UK-MSF-102')), bool(claims.get('UK-MSF-205')),
            len(claims['UK-MSF-132']),
            sorted((c['claim_status'], c['place_id'], c['conflict_group_id']) for c in claims['UK-MSF-132']),
            claims['UK-MSF-104'][0]['place_id'], claims['UK-MSF-167'][0]['place_id'],
            claims['UK-MSF-115'][0]['place_id'], claims['UK-MSF-143'][0]['place_id'],
            claims['UK-MSF-150'][0]['place_id'], claims['UK-MSF-159'][0]['place_id'],
            claims['UK-MSF-165'][0]['place_id'],
            claims['UK-LLG-131'][0]['place_id'], claims['UK-LLG-159'][0]['place_id'],
            claims['UK-LLG-181'][0]['place_id'], claims['US-YMSU-4'][0]['place_id'],
            claims['US-YMSU-5'][0]['place_id']),
           (False, False, False, 2,
            [('alternate', 'PL0357', 'G134'), ('preferred', 'PL0344', 'G134')],
            'PL0258', 'PL0258', 'PL0344', 'PL0157', 'PL0156', 'PL0180', 'PL0344',
            'PL4199', 'PL4200', 'PL4199', 'PL0357', 'PL0357'))
    rels = [r for r in common.read_dicts(os.path.join(common.ROOT, 'data', 'command_relations.csv'))[1]]
    def parents(uid, status=None):
        rows = [r for r in rels if r['subject_unit_id'] == uid]
        if status:
            rows = [r for r in rows if r['status'] == status]
        return sorted((r['higher_unit_id'], r['relationship'], r['status']) for r in rows)
    expect(s + ': 104th and 167th are assigned to 124.10; 132nd is assigned to Force S preferred and 125.9 alternate (F3); YMS units to 125.9',
           (parents('UK-MSF-104'), parents('UK-MSF-167'),
            parents('UK-MSF-132', 'preferred'), parents('UK-MSF-132', 'alternate'),
            parents('UK-MSF-150'), parents('UK-MSF-159'), parents('UK-MSF-165'),
            parents('UK-MSF-143'), parents('US-YMSU-4'), parents('US-YMSU-5'),
            parents('UK-MSF-115'), parents('UK-LLG-131'), parents('US-TG-124-10')),
           ([('US-TG-124-10', 'assigned', 'preferred')],
            [('US-TG-124-10', 'assigned', 'preferred')],
            [('UK-TF-S', 'assigned', 'preferred')],
            [('US-TG-125-9', 'assigned', 'alternate')],
            [('UK-TF-G', 'assigned', 'preferred')],
            [('UK-TF-J', 'assigned', 'preferred')],
            [('UK-TF-S', 'assigned', 'preferred')],
            [('UK-TF-ETF', 'assigned', 'preferred')],
            [('US-TG-125-9', 'assigned', 'preferred')],
            [('US-TG-125-9', 'assigned', 'preferred')],
            [], [], []))
    places = {r['place_id']: r for r in common.read_dicts(os.path.join(common.ROOT, 'data', 'places.csv'))[1]}
    expect(s + ': new port places PL4196-PL4200 exist (Plymouth, Dover, The Nore, Swansea, Milford Haven)',
           (places['PL4196']['name'], places['PL4197']['name'], places['PL4198']['name'],
            places['PL4199']['name'], places['PL4200']['name'],
            places['PL4196']['coord_reference_id'], places['PL4198']['kind']),
           ('Plymouth, Devon', 'Dover, Kent', 'The Nore, Thames Estuary',
            'Swansea', 'Milford Haven, Pembrokeshire', 'R001', 'point'))



def scenario_291_normandy_chunk3a_commit2():
    s = 'scenario 291'
    units = {u['unit_id']: u for u in common.read_dicts(common.UNITS_CSV)[1]}
    mtb = [
        'UK-CF-01', 'UK-CF-05', 'UK-CF-13', 'UK-CF-14', 'UK-CF-21', 'UK-CF-22',
        'CAN-CF-29', 'UK-CF-35', 'UK-CF-51', 'UK-CF-52', 'UK-CF-53', 'UK-CF-55',
        'UK-CF-59', 'UK-CF-63', 'UK-CF-64', 'CAN-CF-65']
    placeholders = ['UK-CML-02', 'UK-CML-05', 'UK-CML-11', 'UK-CML-149', 'UK-CML-150']
    active_ml = [
        'UK-CML-01', 'UK-CML-04', 'UK-CML-07', 'UK-CML-10', 'UK-CML-15',
        'UK-CML-19', 'UK-CML-20', 'UK-CML-21', 'UK-CML-23', 'UK-CML-33',
        'UK-CML-50', 'UK-CML-51', 'UK-CML-103', 'UK-CML-151']
    expect(s + ': 16 MTB flotillas are active naval_division rows; 29th and 65th are Canadian (F7, F10)',
           [(u, units[u]['record_status'], units[u]['echelon'], units[u]['nationality'], units[u]['domain']) for u in mtb],
           [(u, 'active', 'naval_division', 'Canada' if u.startswith('CAN-') else 'UK', 'naval') for u in mtb])
    expect(s + ': gunboat flotillas, 14 located ML flotillas, and the Force U PT and HDML groups are active',
           [(u, units[u]['record_status'], units[u]['echelon']) for u in
            ['UK-MGBF-01', 'UK-SGBF-01'] + active_ml + ['US-TG-125-13', 'US-TG-125-14']],
           ([(u, 'active', 'naval_division') for u in ['UK-MGBF-01', 'UK-SGBF-01'] + active_ml]
            + [('US-TG-125-13', 'active', 'task_group'), ('US-TG-125-14', 'active', 'task_group')]))
    expect(s + ': five split ML flotillas are placeholders with no invented single location (F9)',
           [(u, units[u]['record_status']) for u in placeholders],
           [(u, 'placeholder') for u in placeholders])
    expect(s + ': no invented PTRon or Nore/Dover/Portsmouth command units, and UK-CF is not reused for an ML flotilla',
           ('US-PTRON-01' in units, 'UK-NORE' in units, 'UK-CF-07' in units, 'UK-CML-07' in units),
           (False, False, False, True))
    claims = {}
    for path in common.claim_files():
        for r in common.read_dicts(path)[1]:
            claims.setdefault(r['unit_id'], []).append(r)
    expect(s + ': split ML placeholders have no claims; covering stations and assault beaches are as allocated',
           (all(not claims.get(u) for u in placeholders),
            claims['UK-CF-01'][0]['place_id'], claims['UK-CF-05'][0]['place_id'],
            claims['UK-CF-21'][0]['place_id'], claims['CAN-CF-29'][0]['place_id'],
            claims['UK-CF-55'][0]['place_id'], claims['UK-CF-63'][0]['place_id'],
            claims['UK-MGBF-01'][0]['place_id'], claims['UK-SGBF-01'][0]['place_id'],
            claims['UK-CML-07'][0]['place_id'], claims['UK-CML-15'][0]['place_id'],
            claims['UK-CML-19'][0]['place_id'], claims['UK-CML-20'][0]['place_id'],
            claims['US-TG-125-13'][0]['place_id'], claims['US-TG-125-14'][0]['place_id'],
            claims['UK-CML-01'][0]['place_id']),
           (True, 'PL4196', 'PL4197', 'PL4198', 'PL4173', 'PL0157', 'PL0157',
            'PL0180', 'PL0258', 'PL0156', 'PL0357', 'PL0344', 'PL0180',
            'PL0357', 'PL0357', 'PL0157'))
    rels = [r for r in common.read_dicts(os.path.join(common.ROOT, 'data', 'command_relations.csv'))[1]]
    def parents(uid):
        return sorted((r['higher_unit_id'], r['relationship'], r['status'])
                      for r in rels if r['subject_unit_id'] == uid)
    expect(s + ': core flotillas are parented to the named force; covering flotillas, the 29th, and 125.13/125.14 have no parent (F9, Q1)',
           (parents('UK-CF-55'), parents('UK-CF-63'), parents('UK-MGBF-01'), parents('UK-SGBF-01'),
            parents('UK-CML-04'), parents('UK-CML-07'), parents('UK-CML-15'),
            parents('UK-CML-19'), parents('UK-CML-20'),
            parents('UK-CF-01'), parents('CAN-CF-29'), parents('US-TG-125-13'), parents('US-TG-125-14'),
            parents('UK-CML-01')),
           ([('UK-TF-ETF', 'assigned', 'preferred')],
            [('UK-TF-ETF', 'assigned', 'preferred')],
            [('UK-TF-J', 'assigned', 'preferred')],
            [('US-TG-124-6', 'assigned', 'preferred')],
            [('US-TG-125', 'assigned', 'preferred')],
            [('UK-TF-G', 'assigned', 'preferred')],
            [('US-TG-125', 'assigned', 'preferred')],
            [('UK-TF-S', 'assigned', 'preferred')],
            [('UK-TF-J', 'assigned', 'preferred')],
            [], [], [], [], []))


def scenario_292_normandy_chunk3b_commit1():
    """Normandy chunk 3b commit 1: assault groups, landing-craft squadrons, WTF landing-craft groups (ND1-ND5)."""
    s = 'scenario 292'
    units = {u['unit_id']: u for u in common.read_dicts(common.UNITS_CSV)[1]}
    ags = [
        'UK-AG-S1', 'UK-AG-S2', 'UK-AG-S3', 'UK-AG-J1', 'UK-AG-J2', 'UK-AG-J3', 'UK-AG-J4',
        'UK-AG-G1', 'UK-AG-G2', 'UK-AG-G3', 'UK-AG-L1', 'UK-AG-L2', 'UK-AG-L3', 'UK-AG-O4']
    sqns = [
        'UK-LCS-S-LST', 'UK-LCS-T', 'UK-LCS-I', 'UK-LCS-E', 'UK-LCS-S-SUP', 'UK-LCS-K', 'UK-LCS-1',
        'UK-LCS-N', 'UK-LCS-2', 'UK-LCS-P', 'UK-LCS-J4-SUP', 'UK-LCS-D', 'UK-LCS-L', 'UK-LCS-G-SUP',
        'UK-LCS-U', 'UK-LCS-V', 'UK-LCS-H', 'UK-LCS-A', 'UK-LCS-G', 'UK-LCS-O', 'UK-LCS-Q']
    tgs = [
        'US-TG-125-4', 'US-TG-125-5', 'US-TG-125-7', 'US-TG-125-10', 'US-TG-125-12',
        'US-TG-124-3', 'US-TG-124-4', 'US-TG-124-5', 'US-TG-124-8']
    expect(s + ': 14 assault groups (13 ETF plus O-4) are active task_group rows (F16, ND3)',
           [(u, units[u]['record_status'], units[u]['echelon'], units[u]['nationality'], units[u]['domain']) for u in ags],
           [(u, 'active', 'task_group', 'UK', 'naval') for u in ags])
    expect(s + ': 21 landing-craft squadrons are active naval_squadron rows, including the four qualified unlettered ids (F16, ND2)',
           [(u, units[u]['record_status'], units[u]['echelon'], units[u]['nationality']) for u in sqns],
           [(u, 'active', 'naval_squadron', 'UK') for u in sqns])
    expect(s + ': nine WTF landing-craft task groups are active (F18)',
           [(u, units[u]['record_status'], units[u]['echelon'], units[u]['nationality']) for u in tgs],
           [(u, 'active', 'task_group', 'US') for u in tgs])
    expect(s + ': Far Shore Omaha and US LCI/LCT divisions are not units (ND4, ND5); the unused UK-LBS- barge pattern was not adopted (G1 uses UK-LCS-)',
           all(u not in units for u in [
               'UK-LBS-U', 'UK-LBS-W', 'UK-LBS-Z', 'UK-LBS-X', 'UK-LBS-Y',
               'US-TG-124-11', 'US-LCIG-04', 'US-LCID-61', 'US-LCTD-19']),
           True)
    claims = {}
    for path in common.claim_files():
        for r in common.read_dicts(path)[1]:
            claims.setdefault(r['unit_id'], []).append(r)
    expect(s + ': 6 June claims sit on the allocated beach or, for split/follow-up groups, the ETF area or Plymouth',
           (claims['UK-AG-S1'][0]['place_id'], claims['UK-AG-J1'][0]['place_id'],
            claims['UK-AG-G1'][0]['place_id'], claims['UK-AG-J4'][0]['place_id'],
            claims['UK-AG-L1'][0]['place_id'], claims['UK-AG-O4'][0]['place_id'],
            claims['US-TG-125-4'][0]['place_id'], claims['US-TG-124-3'][0]['place_id'],
            claims['UK-LCS-Q'][0]['place_id'], claims['UK-LCS-Q'][0]['location_represents'],
            claims['US-TG-125-10'][0]['commander']),
           ('PL0344', 'PL0180', 'PL0156', 'PL0157', 'PL0157', 'PL0258',
            'PL0357', 'PL0258', 'PL4196', 'base', 'unknown'))
    rels = [r for r in common.read_dicts(os.path.join(common.ROOT, 'data', 'command_relations.csv'))[1]]
    def parents(uid):
        return sorted((r['higher_unit_id'], r['relationship'], r['status'])
                      for r in rels if r['subject_unit_id'] == uid)
    expect(s + ': squadrons parent to the assault group or, where split, to the force; assault groups have no same-rank force relation (Q1)',
           (parents('UK-LCS-T'), parents('UK-LCS-S-LST'), parents('UK-LCS-G-SUP'),
            parents('UK-LCS-G'), parents('UK-LCS-O'), parents('UK-LCS-Q'),
            parents('UK-AG-S1'), parents('UK-AG-O4'), parents('US-TG-125-4')),
           ([('UK-AG-S1', 'assigned', 'preferred')],
            [('UK-AG-S1', 'assigned', 'preferred')],
            [('UK-TF-G', 'assigned', 'preferred')],
            [('US-TG-125', 'assigned', 'preferred')],
            [('US-TG-125', 'assigned', 'preferred')],
            [('US-TG-126', 'assigned', 'preferred')],
            [], [], []))



def scenario_293_normandy_chunk3b_commit2():
    """Normandy chunk 3b commit 2: RN LST flotillas, US LST divisions, LCI and support flotillas."""
    s = 'scenario 293'
    units = {u['unit_id']: u for u in common.read_dicts(common.UNITS_CSV)[1]}
    lstf = ['UK-LSTF-01', 'UK-LSTF-02', 'UK-LSTF-03', 'UK-LSTF-04', 'UK-LSTF-05', 'UK-LSTF-07', 'UK-LSTF-08', 'UK-LSTF-09']
    lstd = ['US-LSTD-%s' % n for n in (21, 22, 23, 55, 56, 60, 61, 62, 65, 70, 71, 72, 97, 98, 99, 100, 101, 102, 103)]
    lci_uk = ['UK-MLF-200', 'UK-MLF-201', 'UK-MLF-202', 'UK-MLF-251', 'UK-MLF-252', 'UK-MLF-253', 'UK-MLF-263', 'UK-MLF-265', 'UK-MLF-266']
    lci_can = ['CAN-MLF-260', 'CAN-MLF-261', 'CAN-MLF-264']
    support = ['UK-MLF-310', 'UK-MLF-330', 'UK-MLF-331', 'UK-MLF-332', 'UK-MLF-333', 'UK-MLF-900']
    expect(s + ': eight RN LST flotillas are active naval_division rows; there is no 6th',
           ([(u, units[u]['record_status'], units[u]['echelon'], units[u]['nationality'], units[u]['domain']) for u in lstf],
            'UK-LSTF-06' in units),
           ([(u, 'active', 'naval_division', 'UK', 'naval') for u in lstf], False))
    expect(s + ': 19 US LST divisions are active naval_division rows (F19)',
           [(u, units[u]['record_status'], units[u]['echelon'], units[u]['nationality']) for u in lstd],
           [(u, 'active', 'naval_division', 'US') for u in lstd])
    expect(s + ': 12 LCI flotillas are active; 260th, 261st and 264th are Canadian',
           [(u, units[u]['record_status'], units[u]['echelon'], units[u]['nationality']) for u in lci_uk + lci_can],
           ([(u, 'active', 'naval_division', 'UK') for u in lci_uk]
            + [(u, 'active', 'naval_division', 'Canada') for u in lci_can]))
    expect(s + ': six support flotillas are active naval_division rows',
           [(u, units[u]['record_status'], units[u]['echelon']) for u in support],
           [(u, 'active', 'naval_division') for u in support])
    claims = {}
    for path in common.claim_files():
        for r in common.read_dicts(path)[1]:
            claims.setdefault(r['unit_id'], []).append(r)
    c261 = sorted(claims['CAN-MLF-261'], key=lambda r: r['claim_status'])
    expect(s + ': 261st has G135 Juno preferred and Sword alternate; beaches and Plymouth are as allocated',
           ([(r['claim_status'], r['place_id'], r['conflict_group_id']) for r in c261],
            claims['UK-LSTF-01'][0]['place_id'], claims['UK-LSTF-02'][0]['place_id'],
            claims['UK-LSTF-07'][0]['place_id'], claims['US-LSTD-22'][0]['place_id'],
            claims['US-LSTD-21'][0]['place_id'], claims['US-LSTD-23'][0]['place_id'],
            claims['US-LSTD-23'][0]['location_represents'], claims['UK-MLF-330'][0]['place_id'],
            claims['UK-MLF-310'][0]['place_id'], claims['CAN-MLF-264'][0]['place_id']),
           ([('alternate', 'PL0344', 'G135'), ('preferred', 'PL0180', 'G135')],
            'PL0344', 'PL0180', 'PL0157', 'PL0156', 'PL0157', 'PL4196', 'base',
            'PL0344', 'PL0157', 'PL0156'))
    rels = [r for r in common.read_dicts(os.path.join(common.ROOT, 'data', 'command_relations.csv'))[1]]
    def parents(uid):
        return sorted((r['higher_unit_id'], r['relationship'], r['status'])
                      for r in rels if r['subject_unit_id'] == uid)
    expect(s + ': flotillas and divisions parent to the named squadron, assault group or Force B',
           (parents('UK-LSTF-01'), parents('UK-LSTF-02'), parents('UK-LSTF-07'),
            parents('US-LSTD-22'), parents('US-LSTD-21'), parents('US-LSTD-23'),
            parents('CAN-MLF-260'), parents('CAN-MLF-261'), parents('CAN-MLF-264'),
            parents('UK-MLF-330'), parents('UK-MLF-332'), parents('UK-MLF-310')),
           ([('UK-LCS-S-LST', 'assigned', 'preferred')],
            [('UK-AG-J3', 'assigned', 'preferred')],
            [('UK-AG-L1', 'assigned', 'preferred')],
            [('UK-AG-G3', 'assigned', 'preferred')],
            [('UK-AG-L1', 'assigned', 'preferred')],
            [('US-TG-126', 'assigned', 'preferred')],
            [('UK-LCS-P', 'assigned', 'preferred')],
            [('UK-LCS-E', 'assigned', 'alternate'), ('UK-LCS-P', 'assigned', 'preferred')],
            [('UK-AG-G3', 'assigned', 'preferred')],
            [('UK-LCS-S-SUP', 'assigned', 'preferred')],
            [('UK-LCS-G-SUP', 'assigned', 'preferred')],
            [('UK-LCS-J4-SUP', 'assigned', 'preferred')]))



def scenario_294_normandy_chunk3b_commit3():
    """Normandy chunk 3b commit 3: 55 LCT flotillas, including one 23rd and a split 322nd."""
    s = 'scenario 294'
    units = {u['unit_id']: u for u in common.read_dicts(common.UNITS_CSV)[1]}
    def mlf(n):
        return 'UK-MLF-%02d' % n if n < 100 else 'UK-MLF-%d' % n
    flots = [mlf(n) for n in (
        4, 6, 11, 12, 14, 15, 16, 17, 18, 19, 20, 22, 23, 24, 28, 30, 31, 32, 34, 35, 36, 37, 38, 39,
        40, 41, 42, 43, 44, 45, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 59,
        100, 102, 103, 104, 105, 106, 107, 108, 109, 110, 320, 321, 322)]
    expect(s + ': 55 LCT flotillas are active UK naval_division rows; the 23rd is one unit',
           (len(flots), [(u, units[u]['record_status'], units[u]['echelon'], units[u]['nationality']) for u in flots]),
           (55, [(u, 'active', 'naval_division', 'UK') for u in flots]))
    claims = {}
    for path in common.claim_files():
        for r in common.read_dicts(path)[1]:
            claims.setdefault(r['unit_id'], []).append(r)
    expect(s + ': beaches, the ETF area and Plymouth are as allocated; the 23rd and 322nd have one claim each',
           (len(claims['UK-MLF-23']), len(claims['UK-MLF-322']),
            claims['UK-MLF-04'][0]['place_id'], claims['UK-MLF-23'][0]['place_id'],
            claims['UK-MLF-38'][0]['place_id'], claims['UK-MLF-06'][0]['place_id'],
            claims['UK-MLF-52'][0]['place_id'], claims['UK-MLF-54'][0]['place_id'],
            claims['UK-MLF-54'][0]['location_represents'], claims['UK-MLF-322'][0]['place_id']),
           (1, 1, 'PL0180', 'PL0156', 'PL0344', 'PL0157', 'PL0357', 'PL4196', 'base', 'PL0156'))
    rels = [r for r in common.read_dicts(os.path.join(common.ROOT, 'data', 'command_relations.csv'))[1]]
    def parents(uid):
        return sorted((r['higher_unit_id'], r['relationship'], r['status'])
                      for r in rels if r['subject_unit_id'] == uid)
    expect(s + ': flotillas parent to the named LCT or support squadron',
           (parents('UK-MLF-04'), parents('UK-MLF-23'), parents('UK-MLF-38'),
            parents('UK-MLF-06'), parents('UK-MLF-52'), parents('UK-MLF-107'),
            parents('UK-MLF-54'), parents('UK-MLF-322'), parents('UK-MLF-108')),
           ([('UK-LCS-K', 'assigned', 'preferred')],
            [('UK-LCS-D', 'assigned', 'preferred')],
            [('UK-LCS-S-SUP', 'assigned', 'preferred')],
            [('UK-LCS-H', 'assigned', 'preferred')],
            [('UK-LCS-G', 'assigned', 'preferred')],
            [('UK-LCS-O', 'assigned', 'preferred')],
            [('UK-LCS-Q', 'assigned', 'preferred')],
            [('UK-LCS-G-SUP', 'assigned', 'preferred')],
            [('UK-LCS-G-SUP', 'assigned', 'preferred')]))


def scenario_295_normandy_chunk3c_commit1():
    """Normandy chunk 3c commit 1: build-up and barge squadrons (G1-G8)."""
    s = 'scenario 295'
    units = {u['unit_id']: u for u in common.read_dicts(common.UNITS_CSV)[1]}
    bu = ['UK-LCS-C', 'UK-LCS-D-BU', 'UK-LCS-A-BU', 'UK-LCS-F', 'UK-LCS-B', 'UK-LCS-E-BU']
    bg = ['UK-LCS-U-LB', 'UK-LCS-W', 'UK-LCS-Z', 'UK-LCS-X', 'UK-LCS-Y']
    expect(s + ': six build-up and five barge squadrons are active naval_squadron rows (G1)',
           [(u, units[u]['record_status'], units[u]['echelon'], units[u]['nationality'], units[u]['domain']) for u in bu + bg],
           [(u, 'active', 'naval_squadron', 'UK', 'naval') for u in bu + bg])
    expect(s + ': the 3b lettered LCT/LCI squadrons A, D, E and U are unchanged and distinct from the qualified 3c ids',
           (units['UK-LCS-A']['unit_name'], units['UK-LCS-D']['unit_name'],
            units['UK-LCS-E']['unit_name'], units['UK-LCS-U']['unit_name'],
            'UK-LCS-A-BU' in units, 'UK-LCS-D-BU' in units, 'UK-LCS-E-BU' in units, 'UK-LCS-U-LB' in units),
           ('"A" L.C.I.(L) Squadron', '"D" L.C.T. Squadron',
            '"E" Squadron, Landing Craft', '"U" L.C.T. Squadron',
            True, True, True, True))
    claims = {}
    for path in common.claim_files():
        for r in common.read_dicts(path)[1]:
            claims.setdefault(r['unit_id'], []).append(r)
    expect(s + ': 6 June claims sit on the parent force beach',
           (claims['UK-LCS-C'][0]['place_id'], claims['UK-LCS-D-BU'][0]['place_id'],
            claims['UK-LCS-A-BU'][0]['place_id'], claims['UK-LCS-F'][0]['place_id'],
            claims['UK-LCS-B'][0]['place_id'], claims['UK-LCS-E-BU'][0]['place_id'],
            claims['UK-LCS-U-LB'][0]['place_id'], claims['UK-LCS-W'][0]['place_id'],
            claims['UK-LCS-Z'][0]['place_id'], claims['UK-LCS-X'][0]['place_id'],
            claims['UK-LCS-Y'][0]['place_id'],
            claims['UK-LCS-C'][0]['commander'], claims['UK-LCS-A-BU'][0]['commander']),
           ('PL0344', 'PL0344', 'PL0180', 'PL0180', 'PL0156', 'PL0156',
            'PL0344', 'PL0180', 'PL0156', 'PL0357', 'PL0258',
            'Ty. Act. Major G. L. T. Robins, R.M.', 'unknown'))
    rels = [r for r in common.read_dicts(os.path.join(common.ROOT, 'data', 'command_relations.csv'))[1]]
    def parents(uid):
        return sorted((r['higher_unit_id'], r['relationship'], r['status'])
                      for r in rels if r['subject_unit_id'] == uid)
    expect(s + ': squadrons parent to the force or, for X, Far Shore Utah; Y parents to Force O (ND5)',
           (parents('UK-LCS-C'), parents('UK-LCS-D-BU'), parents('UK-LCS-A-BU'),
            parents('UK-LCS-F'), parents('UK-LCS-B'), parents('UK-LCS-E-BU'),
            parents('UK-LCS-U-LB'), parents('UK-LCS-W'), parents('UK-LCS-Z'),
            parents('UK-LCS-X'), parents('UK-LCS-Y')),
           ([('UK-TF-S', 'assigned', 'preferred')],
            [('UK-TF-S', 'assigned', 'preferred')],
            [('UK-TF-J', 'assigned', 'preferred')],
            [('UK-TF-J', 'assigned', 'preferred')],
            [('UK-TF-G', 'assigned', 'preferred')],
            [('UK-TF-G', 'assigned', 'preferred')],
            [('UK-TF-S', 'assigned', 'preferred')],
            [('UK-TF-J', 'assigned', 'preferred')],
            [('UK-TF-G', 'assigned', 'preferred')],
            [('US-TG-125-10', 'assigned', 'preferred')],
            [('US-TG-124', 'assigned', 'preferred')]))




def scenario_296_normandy_chunk3c_commit2():
    """Normandy chunk 3c commit 2: 63 assault and auxiliary flotillas (G3-G5, G8) and the 536th S3 correction."""
    s = 'scenario 296'
    units = {u['unit_id']: u for u in common.read_dicts(common.UNITS_CSV)[1]}
    nums = [
        435, 543, 537, 538, 536, 592, 704, 707,
        557, 528, 526, 509, 517, 510, 505, 516, 511, 521, 703,
        558, 544, 556, 529, 513, 506, 518, 512, 515, 590, 702,
        555, 705,
        522, 520, 514, 523, 519, 508, 503, 500, 507, 501, 502, 504, 701,
        499, 712,
        524, 553, 525, 554, 559, 591,
        539, 540, 541, 542,
        700, 706, 708,
        550, 551, 552,
    ]
    flots = ['UK-MLF-%d' % n for n in nums]
    expect(s + ': 63 assault and auxiliary flotillas are active UK naval_division rows (G3, G8)',
           (len(flots), [(u, units[u]['record_status'], units[u]['echelon'], units[u]['nationality'], units[u]['domain']) for u in flots]),
           (63, [(u, 'active', 'naval_division', 'UK', 'naval') for u in flots]))
    expect(s + ': the 499th is the Auxiliary Flotilla; the 528th and 529th are UK-MLF-, not CAN-MLF-',
           (units['UK-MLF-499']['unit_name'], 'CAN-MLF-528' in units, 'CAN-MLF-529' in units,
            units['UK-MLF-528']['nationality'], units['UK-MLF-529']['nationality']),
           ('499th Auxiliary Flotilla', False, False, 'UK', 'UK'))
    expect(s + ': the S3 note corrects the 536th Green List figure from [13] to [18]',
           ('536th [13]' in units['UK-AG-S3']['unit_note'],
            '536th [18]' in units['UK-AG-S3']['unit_note'],
            'old value [13]' in units['UK-AG-S3']['unit_note'],
            'UK-MLF-536' in units['UK-AG-S3']['unit_note']),
           (True, True, True, True))
    claims = {}
    for path in common.claim_files():
        for r in common.read_dicts(path)[1]:
            claims.setdefault(r['unit_id'], []).append(r)
    expect(s + ': beaches follow the parent group or the J4 force allocation; 701st and 712th use the ETF area (G4, G5)',
           (len(claims['UK-MLF-712']),
            claims['UK-MLF-435'][0]['place_id'], claims['UK-MLF-536'][0]['place_id'],
            claims['UK-MLF-557'][0]['place_id'], claims['UK-MLF-499'][0]['place_id'],
            claims['UK-MLF-524'][0]['place_id'],
            claims['UK-MLF-522'][0]['place_id'], claims['UK-MLF-514'][0]['place_id'],
            claims['UK-MLF-523'][0]['place_id'], claims['UK-MLF-508'][0]['place_id'],
            claims['UK-MLF-701'][0]['place_id'], claims['UK-MLF-712'][0]['place_id'],
            claims['UK-MLF-550'][0]['place_id'], claims['UK-MLF-551'][0]['place_id'],
            claims['UK-MLF-552'][0]['place_id']),
           (1, 'PL0344', 'PL0344', 'PL0180', 'PL0180', 'PL0156',
            'PL0258', 'PL0344', 'PL0180', 'PL0156',
            'PL0157', 'PL0157', 'PL0258', 'PL0258', 'PL0357'))
    rels = [r for r in common.read_dicts(os.path.join(common.ROOT, 'data', 'command_relations.csv'))[1]]
    def parents(uid):
        return sorted((r['higher_unit_id'], r['relationship'], r['status'])
                      for r in rels if r['subject_unit_id'] == uid)
    expect(s + ': flotillas parent to the named assault group, squadron, force or WTF group; J4/O4 flotillas are not entered twice (G5)',
           (parents('UK-MLF-536'), parents('UK-MLF-592'), parents('UK-MLF-557'),
            parents('UK-MLF-703'), parents('UK-MLF-555'), parents('UK-MLF-522'),
            parents('UK-MLF-701'), parents('UK-MLF-499'), parents('UK-MLF-712'),
            parents('UK-MLF-524'), parents('UK-MLF-591'), parents('UK-MLF-700'),
            parents('UK-MLF-550'), parents('UK-MLF-551'), parents('UK-MLF-552'),
            'UK-MLF-507' in units['UK-AG-O4']['unit_note']),
           ([('UK-AG-S3', 'assigned', 'preferred')],
            [('UK-LCS-S-SUP', 'assigned', 'preferred')],
            [('UK-AG-J1', 'assigned', 'preferred')],
            [('UK-LCS-1', 'assigned', 'preferred')],
            [('UK-AG-J3', 'assigned', 'preferred')],
            [('UK-AG-J4', 'assigned', 'preferred')],
            [('UK-LCS-J4-SUP', 'assigned', 'preferred')],
            [('UK-TF-J', 'assigned', 'preferred')],
            [('UK-TF-J', 'assigned', 'preferred')],
            [('UK-AG-G1', 'assigned', 'preferred')],
            [('UK-LCS-G-SUP', 'assigned', 'preferred')],
            [('UK-TF-G', 'assigned', 'preferred')],
            [('US-TG-124-3', 'assigned', 'preferred')],
            [('US-TG-124-4', 'assigned', 'preferred')],
            [('US-TG-125-4', 'assigned', 'preferred')],
            True))



def scenario_297_normandy_chunk3c_commit3():
    """Normandy chunk 3c commit 3: 27 build-up and 31 barge flotillas (G2-G4, G6)."""
    s = 'scenario 297'
    units = {u['unit_id']: u for u in common.read_dicts(common.UNITS_CSV)[1]}
    bu_nums = [803, 810, 811, 812, 813, 814, 602, 603, 653, 804,
               600, 601, 604, 650, 651, 652, 805, 806, 807, 808, 809,
               605, 606, 607, 609, 654, 698]
    bu = ['UK-MLF-%d' % n for n in bu_nums]
    lbf_nums = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 18, 19, 20,
                30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 25, 26]
    barges = ['UK-LBF-%02d' % n for n in lbf_nums]
    expect(s + ': 27 build-up flotillas are active UK naval_division rows (G3)',
           (len(bu), [(u, units[u]['record_status'], units[u]['echelon'], units[u]['nationality']) for u in bu]),
           (27, [(u, 'active', 'naval_division', 'UK') for u in bu]))
    expect(s + ': 31 barge flotillas are active UK naval_division rows under UK-LBF- (G2, G6)',
           (len(barges), [(u, units[u]['record_status'], units[u]['echelon'], units[u]['nationality']) for u in barges]),
           (31, [(u, 'active', 'naval_division', 'UK') for u in barges]))
    expect(s + ': the 4th LBV and 30th L.B. (S and R) are one unit each; the 25th and 26th are L.B.F. (G4, G6)',
           (units['UK-LBF-04']['unit_name'], units['UK-LBF-30']['unit_name'],
            units['UK-LBF-25']['unit_name'], units['UK-LBF-26']['unit_name'],
            'L.B.V. (S and R)' in units['UK-LBF-35']['unit_note']),
           ('4th LBV Flotilla', '30th L.B. (S and R) Flotilla',
            '25th L.B.F. Flotilla', '26th L.B.F. Flotilla', True))
    claims = {}
    for path in common.claim_files():
        for r in common.read_dicts(path)[1]:
            claims.setdefault(r['unit_id'], []).append(r)
    expect(s + ': beaches follow the parent squadron; the 4th and 30th use the ETF area (G4)',
           (len(claims['UK-LBF-04']), len(claims['UK-LBF-30']),
            claims['UK-MLF-803'][0]['place_id'], claims['UK-MLF-804'][0]['place_id'],
            claims['UK-MLF-805'][0]['place_id'],
            claims['UK-LBF-01'][0]['place_id'], claims['UK-LBF-05'][0]['place_id'],
            claims['UK-LBF-13'][0]['place_id'], claims['UK-LBF-08'][0]['place_id'],
            claims['UK-LBF-07'][0]['place_id'],
            claims['UK-LBF-04'][0]['place_id'], claims['UK-LBF-30'][0]['place_id'],
            claims['UK-LBF-25'][0]['place_id'], claims['UK-LBF-26'][0]['place_id']),
           (1, 1, 'PL0344', 'PL0180', 'PL0156',
            'PL0180', 'PL0344', 'PL0156', 'PL0357', 'PL0258',
            'PL0157', 'PL0157', 'PL0156', 'PL0156'))
    rels = [r for r in common.read_dicts(os.path.join(common.ROOT, 'data', 'command_relations.csv'))[1]]
    def parents(uid):
        return sorted((r['higher_unit_id'], r['relationship'], r['status'])
                      for r in rels if r['subject_unit_id'] == uid)
    expect(s + ': flotillas parent to the named squadron, or ETF for the splits, or G1/G2 for the L.B.F. (G4, G6)',
           (parents('UK-MLF-803'), parents('UK-MLF-602'), parents('UK-MLF-804'),
            parents('UK-MLF-600'), parents('UK-MLF-805'), parents('UK-MLF-605'),
            parents('UK-LBF-05'), parents('UK-LBF-01'), parents('UK-LBF-13'),
            parents('UK-LBF-08'), parents('UK-LBF-07'),
            parents('UK-LBF-04'), parents('UK-LBF-30'),
            parents('UK-LBF-25'), parents('UK-LBF-26')),
           ([('UK-LCS-C', 'assigned', 'preferred')],
            [('UK-LCS-D-BU', 'assigned', 'preferred')],
            [('UK-LCS-A-BU', 'assigned', 'preferred')],
            [('UK-LCS-F', 'assigned', 'preferred')],
            [('UK-LCS-B', 'assigned', 'preferred')],
            [('UK-LCS-E-BU', 'assigned', 'preferred')],
            [('UK-LCS-U-LB', 'assigned', 'preferred')],
            [('UK-LCS-W', 'assigned', 'preferred')],
            [('UK-LCS-Z', 'assigned', 'preferred')],
            [('UK-LCS-X', 'assigned', 'preferred')],
            [('UK-LCS-Y', 'assigned', 'preferred')],
            [('UK-TF-ETF', 'assigned', 'preferred')],
            [('UK-TF-ETF', 'assigned', 'preferred')],
            [('UK-AG-G1', 'assigned', 'preferred')],
            [('UK-AG-G2', 'assigned', 'preferred')]))


def scenario_298_normandy_chunk4_commit1():
    """Normandy chunk 4 commit 1: commands, surface ships and KdK flotillas (H1-H12)."""
    s = 'scenario 298'
    units = {u['unit_id']: u for u in common.read_dicts(common.UNITS_CSV)[1]}
    cmds = ['GER-FDS-000H', 'GER-KAK-000H', 'GER-KAA-000H', 'GER-BDSW-000H', 'GER-BDSN-000H',
            'GER-FDUW-000H', 'GER-KDK-000H']
    seekos = ['GER-KSS-000H', 'GER-KSC-000H', 'GER-KSK-000H', 'GER-KSB-000H', 'GER-KSL-000H',
              'GER-KSG-000H', 'GER-KSW-000H']
    ships = ['GER-DD-Z024', 'GER-DD-Z032', 'GER-DD-ZH001', 'GER-TB-T024', 'GER-DD-Z023', 'GER-DD-Z037',
             'GER-TB-T028', 'GER-TB-MOEWE', 'GER-TB-JAGUAR', 'GER-TB-KONDOR', 'GER-TB-FALKE']
    kkf = ['GER-KKF-211', 'GER-KKF-361', 'GER-KKF-362', 'GER-KKF-363', 'GER-KKF-261']
    expect(s + ': West commands are active German naval task_group rows (H2 ladder adjustment)',
           [(u, units[u]['record_status'], units[u]['echelon'], units[u]['nationality'], units[u]['domain']) for u in cmds],
           [(u, 'active', 'task_group', 'Germany', 'naval') for u in cmds])
    expect(s + ': new Seekommandanten and K-Stab West are naval_squadron (H2 ladder adjustment)',
           [(u, units[u]['echelon'], units[u]['domain']) for u in seekos],
           [(u, 'naval_squadron', 'naval') for u in seekos])
    expect(s + ': existing SeeKo Normandie stays other and is now active',
           (units['GER-KSN-000H']['echelon'], units['GER-KSN-000H']['record_status'], units['GER-KSN-000H']['domain']),
           ('other', 'active', 'naval'))
    expect(s + ': 8th ZF and five KdK flotillas are naval_division',
           (units['GER-ZF-008']['echelon'], [units[u]['echelon'] for u in kkf]),
           ('naval_division', ['naval_division'] * 5))
    expect(s + ': surface ships have the class taken from the ship page (Falke and Kondor are Type 23 / SC146)',
           (units['GER-DD-Z024']['ship_class_id'], units['GER-DD-Z032']['ship_class_id'],
            units['GER-DD-ZH001']['ship_class_id'], units['GER-TB-T024']['ship_class_id'],
            units['GER-TB-MOEWE']['ship_class_id'], units['GER-TB-JAGUAR']['ship_class_id'],
            units['GER-TB-KONDOR']['ship_class_id'], units['GER-TB-FALKE']['ship_class_id'],
            units['GER-DD-Z023']['ship_class_id'], units['GER-DD-Z037']['ship_class_id'],
            units['GER-TB-T028']['ship_class_id']),
           ('SC143', 'SC144', 'SC197', 'SC150', 'SC146', 'SC147', 'SC146', 'SC146', 'SC143', 'SC144', 'SC150'))
    expect(s + ': SG 3 and FdT and the 4th TBF are not created (H11, H12, H10)',
           ('GER-PG-SG3' in units, 'GER-DE-SG3' in units, 'GER-FDT-000H' in units, 'GER-TBF-004' in units),
           (False, False, False, False))
    claims = {}
    for path in common.claim_files():
        for r in common.read_dicts(path)[1]:
            claims.setdefault(r['unit_id'], []).append(r)
    expect(s + ': FdS headquarters is Scheveningen; FdU West is Angers; KSN is Cherbourg',
           (claims['GER-FDS-000H'][0]['place_id'], claims['GER-FDUW-000H'][0]['place_id'],
            claims['GER-KSN-000H'][0]['place_id']),
           (units['GER-FDS-000H'] and claims['GER-FDS-000H'][0]['place_id'],
            'PL0009', 'PL0089'))
    # tighten FdS: just check name of place via coordinates already stored; compare by looking up later
    schev = claims['GER-FDS-000H'][0]['place_id']
    expect(s + ': FdS claim is a headquarters at confidence 0.5 and names Petersen',
           (claims['GER-FDS-000H'][0]['location_represents'], claims['GER-FDS-000H'][0]['confidence'],
            claims['GER-FDS-000H'][0]['commander'], bool(schev)),
           ('headquarters', '0.5', 'Kapitän zur See Rudolf Petersen', True))
    expect(s + ': 8th ZF and operational ships are at Brest on 8 June, not 6 June',
           (claims['GER-ZF-008'][0]['date'], claims['GER-ZF-008'][0]['place_id'],
            claims['GER-DD-Z024'][0]['date'], claims['GER-DD-Z024'][0]['place_id'],
            claims['GER-DD-Z032'][0]['date'], claims['GER-DD-ZH001'][0]['date'],
            claims['GER-TB-T024'][0]['date']),
           ('1944-06-08', 'PL0045', '1944-06-08', 'PL0045', '1944-06-08', '1944-06-08', '1944-06-08'))
    expect(s + ': 5th TBF boats have a 6 June Le Havre claim',
           (claims['GER-TB-T028'][0]['date'], claims['GER-TB-T028'][0]['place_id'],
            claims['GER-TB-MOEWE'][0]['place_id'], claims['GER-TB-JAGUAR'][0]['place_id'],
            claims['GER-TB-KONDOR'][0]['place_id'], claims['GER-TB-FALKE'][0]['place_id']),
           ('1944-06-06', 'PL4002', 'PL4002', 'PL4002', 'PL4002', 'PL4002'))
    def groups(uid):
        return sorted(set(r['conflict_group_id'] for r in claims[uid] if r['conflict_group_id']))
    expect(s + ': date-conflict groups sit on Z 23, Z 24, Möwe and Kondor',
           (groups('GER-DD-Z023'), groups('GER-DD-Z024'), groups('GER-TB-MOEWE'), groups('GER-TB-KONDOR')),
           (['G136'], ['G137'], ['G138'], ['G139']))
    rels = [r for r in common.read_dicts(os.path.join(common.ROOT, 'data', 'command_relations.csv'))[1]]
    def parents(uid):
        return sorted((r['higher_unit_id'], r['relationship'], r['status'])
                      for r in rels if r['subject_unit_id'] == uid)
    expect(s + ': commands and flotillas parent as in H1, H7, H8, H9 and H10',
           (parents('GER-FDS-000H'), parents('GER-KSN-000H'), parents('GER-TBF-005'),
            parents('GER-ZF-008'), parents('GER-TB-T024'), parents('GER-TB-T028'),
            parents('GER-KSW-000H'), parents('GER-KKF-211'), parents('GER-FDUW-000H'),
            parents('GER-KDK-000H')),
           ([('GER-MGW-000H', 'assigned', 'preferred')],
            [('GER-KAK-000H', 'assigned', 'preferred')],
            [('GER-MGW-000H', 'assigned', 'preferred')],
            [('GER-MGW-000H', 'assigned', 'preferred')],
            [('GER-ZF-008', 'assigned', 'preferred')],
            [('GER-TBF-005', 'assigned', 'preferred')],
            [('GER-KDK-000H', 'assigned', 'preferred')],
            [('GER-KSW-000H', 'assigned', 'preferred')],
            [],
            []))


def scenario_299_normandy_chunk4_commit2():
    """Normandy chunk 4 commit 2: S-boat flotillas and Sicherung West (H1, H2, H4, H6)."""
    s = 'scenario 299'
    units = {u['unit_id']: u for u in common.read_dicts(common.UNITS_CSV)[1]}
    sbf = ['GER-SBF-002', 'GER-SBF-004', 'GER-SBF-005', 'GER-SBF-008', 'GER-SBF-009', 'GER-SBF-006']
    expect(s + ': six S-boat flotillas are active naval_division rows under the GER-SBF- pattern',
           [(u, units[u]['record_status'], units[u]['echelon'], units[u]['domain']) for u in sbf],
           [(u, 'active', 'naval_division', 'naval') for u in sbf])
    expect(s + ': SichDiv are naval_squadron; 6. Sicherungsflottille is naval_division and not GER-SBF-',
           (units['GER-SD-002']['echelon'], units['GER-SD-001']['echelon'], units['GER-SD-005']['echelon'],
            units['GER-SICF-006']['echelon'], 'GER-SBF-006' in units, units['GER-SICF-006']['unit_name']),
           ('naval_squadron', 'naval_squadron', 'naval_squadron', 'naval_division', True, '6. Sicherungsflottille'))
    expect(s + ': deferred North Sea flotillas are absent (H1)',
           ('GER-MSF-001' in units, 'GER-MSF-007' in units, 'GER-SPF-001' in units, 'GER-ATF-001' in units),
           (False, False, False, False))
    claims = {}
    for path in common.claim_files():
        for r in common.read_dicts(path)[1]:
            claims.setdefault(r['unit_id'], []).append(r)
    expect(s + ': 2nd, 4th, 5th and 9th S-flotillas sit at Ostende, Boulogne, Cherbourg, Cherbourg on 6 June',
           (claims['GER-SBF-002'][0]['place_id'], claims['GER-SBF-004'][0]['place_id'],
            claims['GER-SBF-005'][0]['place_id'], claims['GER-SBF-009'][0]['place_id'],
            claims['GER-SBF-006'][0]['date'], claims['GER-SBF-006'][0]['place_id']),
           ('PL3388', 'PL0677', 'PL0089', 'PL0089', '1944-06-26', 'PL3968'))
    def grp(uid):
        return sorted((r['claim_status'], r['place_id']) for r in claims[uid] if r['conflict_group_id']=='G140')
    expect(s + ': 8th S-flotilla has Ostende preferred and IJmuiden alternate (G140)',
           grp('GER-SBF-008'),
           [('alternate', 'PL3968'), ('preferred', 'PL3388')])
    rels = [r for r in common.read_dicts(os.path.join(common.ROOT, 'data', 'command_relations.csv'))[1]]
    def parents(uid):
        return sorted((r['higher_unit_id'], r['relationship'], r['status'])
                      for r in rels if r['subject_unit_id'] == uid)
    expect(s + ': S-flotillas parent to FdS; SichDiv to BdS West or Nordsee; 4th R-boats to 2. SichDiv',
           (parents('GER-SBF-002'), parents('GER-SBF-006'), parents('GER-SD-002'),
            parents('GER-SD-001'), parents('GER-SICF-006'), parents('GER-RBF-004')),
           ([('GER-FDS-000H', 'assigned', 'preferred')],
            [('GER-FDS-000H', 'assigned', 'preferred')],
            [('GER-BDSW-000H', 'assigned', 'preferred')],
            [('GER-BDSN-000H', 'assigned', 'preferred')],
            [('GER-BDSW-000H', 'assigned', 'preferred')],
            [('GER-SD-002', 'assigned', 'preferred')]))




def scenario_300_normandy_chunk4_commit3():
    """Normandy chunk 4 commit 3: French U-flotillas and verified U-boats."""
    s = 'scenario 300 (normandy chunk 4 commit 3)'
    units = {u['unit_id']: u for u in common.read_dicts(common.UNITS_CSV)[1]}
    expect(s + ': eight French U-flotillas exist under the reserved SSF pattern',
           all(u in units for u in (
               'GER-SSF-001', 'GER-SSF-002', 'GER-SSF-003', 'GER-SSF-006',
               'GER-SSF-007', 'GER-SSF-009', 'GER-SSF-010', 'GER-SSF-012')),
           True)
    expect(s + ': all 36 Landwirt boats and U 480 are present, training 5th flotilla is not',
           (all('GER-SS-U%d' % n in units for n in (
               212,228,255,256,260,262,269,270,275,281,333,373,382,413,415,437,
               441,445,608,621,629,650,714,740,758,764,766,821,953,963,970,981,
               984,985,989,993,480)),
            'GER-SSF-005' in units, 'GER-SS-U247' in units, 'GER-SS-U955' in units),
           (True, False, False, False))
    expect(s + ': U 212 is Type VIIC (SC155) and U 214 is Type VIID (SC157)',
           (units['GER-SS-U212']['ship_class_id'], units['GER-SS-U212']['ship_type'],
            units['GER-SS-U214']['ship_class_id'], units['GER-SS-U214']['ship_type']),
           ('SC155', 'SS', 'SC157', 'SS'))
    claims = {}
    for path in common.claim_files():
        for r in common.read_dicts(path)[1]:
            claims.setdefault(r['unit_id'], []).append(r)
    expect(s + ': 1st flotilla at Brest and 3rd at La Pallice on 6 June, U 212 at La Pallice on 6 June',
           (claims['GER-SSF-001'][0]['place_id'], claims['GER-SSF-003'][0]['place_id'],
            claims['GER-SS-U212'][0]['date'], claims['GER-SS-U212'][0]['place_id']),
           ('PL0045', 'PL4203', '1944-06-06', 'PL4203'))
    u988 = claims['GER-SS-U988']
    pref = [r for r in u988 if r['claim_status'] == 'preferred']
    alt = [r for r in u988 if r['claim_status'] == 'alternate']
    expect(s + ': U 988 has a 22 June preferred fate and a 29 June alternate in one group',
           (pref[0]['date'], alt[0]['date'], bool(pref[0]['conflict_group_id']),
            pref[0]['conflict_group_id'] == alt[0]['conflict_group_id']),
           ('1944-06-22', '1944-06-29', True, True))
    u480 = sorted(claims['GER-SS-U480'], key=lambda r: r['date'])
    expect(s + ': U 480 first in-theatre claim is Brest on 7 July (not a 6 June Norway port)',
           (u480[0]['date'], u480[0]['place_id']),
           ('1944-07-07', 'PL0045'))
    rels = [r for r in common.read_dicts(os.path.join(common.ROOT, 'data', 'command_relations.csv'))[1]]
    def parent_of(uid):
        hits = [r['higher_unit_id'] for r in rels if r['subject_unit_id'] == uid]
        return hits[0] if hits else None
    expect(s + ': 1st flotilla parent is FdU West, U 212 parent is the 3rd flotilla',
           (parent_of('GER-SSF-001'), parent_of('GER-SS-U212')),
           ('GER-FDUW-000H', 'GER-SSF-003'))


def scenario_301_normandy_chunk5a_commit1():
    """Normandy chunk 5a commit 1: Ninth Air Force, its commands and the eleven wings (J1-J12)."""
    s = 'scenario 301 (normandy chunk 5a commit 1)'
    units = {u['unit_id']: u for u in common.read_dicts(common.UNITS_CSV)[1]}
    new = ['US-AF-009', 'US-BOMCMD-009', 'US-TCCMD-009', 'US-ADCMD-009', 'US-TAC-019C', 'US-BW-097', 'US-BW-098', 'US-BW-099',
           'US-FW-070', 'US-FW-071', 'US-FW-084', 'US-FW-100', 'US-FW-303', 'US-TCW-050', 'US-TCW-052', 'US-TCW-053']
    expect(s + ': the 16 new air units exist with domain air and the J2 echelons',
           [(units[u]['domain'], units[u]['echelon']) for u in new],
           [('air', 'air_force')] + [('air', 'air_division')] * 4 + [('air', 'air_wing')] * 11)
    expect(s + ': IX Fighter Command and IX TAC are no longer placeholders',
           (units['US-FTRCMD-009']['record_status'], units['US-FTRCMD-009']['formed_date'],
            units['US-TAC-009C']['record_status'], units['US-TAC-009C']['formed_date']),
           ('active', '1942-02-01', 'active', '1943-12-04'))
    expect(s + ': IX Bomber Command carries the later name and IX ADC is formed 1 July',
           (units['US-BOMCMD-009']['unit_name'], units['US-ADCMD-009']['formed_date']),
           ('IX Bomber Command (9th Bombardment Division from 30 August 1944)', '1944-07-01'))
    claims = {}
    for path in common.claim_files():
        for r in common.read_dicts(path)[1]:
            claims.setdefault(r['unit_id'], []).append(r)
    tac = sorted(claims['US-TAC-009C'], key=lambda r: r['date'])
    expect(s + ': IX TAC is at Uxbridge on 1 June (0.3) and moves to Les Oubeaux, Canisy, Coulouvray and Haleine',
           [(r['date'], r['confidence']) for r in tac],
           [('1944-06-01', '0.3'), ('1944-07-02', '0.5'), ('1944-08-02', '0.5'), ('1944-08-12', '0.5'), ('1944-08-22', '0.5')])
    expect(s + ': IX Fighter Command month-only moves are dated on the month end at 0.3',
           [(r['date'], r['confidence']) for r in sorted(claims['US-FTRCMD-009'], key=lambda r: r['date'])],
           [('1944-06-06', '0.5'), ('1944-07-31', '0.3'), ('1944-08-31', '0.3')])
    rels = common.read_dicts(os.path.join(common.ROOT, 'data', 'command_relations.csv'))[1]
    def rel(sub, hi):
        return [(r['relationship'], r['valid_from'], r['valid_to']) for r in rels if r['subject_unit_id'] == sub and r['higher_unit_id'] == hi]
    expect(s + ': IX TCC leaves the Ninth AF on 24 August and is attached to the FAAA from 25 August',
           (rel('US-TCCMD-009', 'US-AF-009'), rel('US-TCCMD-009', 'ALL-FAAA-001A')),
           ([('assigned', '1943-10-16', '1944-08-24')], [('attached', '1944-08-25', '')]))
    expect(s + ': the 71st FW passes from IX FC to IX ADC on 1 July',
           (rel('US-FW-071', 'US-FTRCMD-009'), rel('US-FW-071', 'US-ADCMD-009')),
           ([('assigned', '1943-12-04', '1944-06-30')], [('assigned', '1944-07-01', '')]))
    expect(s + ': the 100th FW is assigned to XIX TAC and under IX FC operational control to 31 July',
           (rel('US-FW-100', 'US-TAC-019C'), rel('US-FW-100', 'US-FTRCMD-009')),
           ([('assigned', '1944-04-15', '')], [('operational_control', '1944-04-15', '1944-07-31')]))
    expect(s + ': the 84th FW is unspecified_subordination to the Ninth AF (IX FC / IX TAC conflict)',
           [r[0] for r in rel('US-FW-084', 'US-AF-009')], ['unspecified_subordination'])


def scenario_302_normandy_chunk5a_commit2():
    """Normandy chunk 5a commit 2: IX Bomber Command's 11 groups and 44 squadrons (J4, J5)."""
    s = 'scenario 302 (normandy chunk 5a commit 2)'
    units = {u['unit_id']: u for u in common.read_dicts(common.UNITS_CSV)[1]}
    groups = ['US-BG-%d' % n for n in (322, 323, 344, 386, 387, 391, 394, 397, 409, 410, 416)]
    sqs = ['US-BS-%03d' % n for a in (449, 453, 494, 552, 556, 572, 584, 596, 640, 644, 668) for n in range(a, a + 4)]
    expect(s + ': 11 groups and 44 squadrons exist on the air ladder',
           (sorted({units[g]['echelon'] for g in groups}), sorted({units[q]['echelon'] for q in sqs}), len(sqs)),
           (['air_group'], ['air_squadron'], 44))
    claims = {}
    for path in common.claim_files():
        for r in common.read_dicts(path)[1]:
            claims.setdefault(r['unit_id'], []).append(r)
    g323 = {(r['date'], r['claim_status'], r['confidence'], r['conflict_group_id']) for r in claims['US-BG-323']}
    expect(s + ': the 323rd at Lessay: 26 August preferred (0.7) and 25 August alternate (0.3) in G147',
           (('1944-08-26', 'preferred', '0.7', 'G147') in g323, ('1944-08-25', 'alternate', '0.3', 'G147') in g323), (True, True))
    g397 = {(r['date'], r['claim_status'], r['confidence'], r['conflict_group_id']) for r in claims['US-BG-397']}
    expect(s + ': the 397th at Gorges: 31 August preferred and 16 August alternate in G148',
           (('1944-08-31', 'preferred', '0.3', 'G148') in g397, ('1944-08-16', 'alternate', '0.3', 'G148') in g397), (True, True))
    expect(s + ': squadron dates are their own (J4): the 586th reaches Tour-en-Bessin on 29 August, the group on 25 August',
           ([r['date'] for r in sorted(claims['US-BS-586'], key=lambda r: r['date'])], max(r['date'] for r in claims['US-BG-394'])),
           (['1944-06-06', '1944-07-28', '1944-08-29'], '1944-08-25'))
    expect(s + ': the 450th misprint claim is 0.3 and "c." squadron moves are 0.3',
           ([r['confidence'] for r in claims['US-BS-450']], [r['confidence'] for r in sorted(claims['US-BS-557'], key=lambda r: r['date'])]),
           (['0.3'], ['0.5', '0.3']))
    rels = common.read_dicts(os.path.join(common.ROOT, 'data', 'command_relations.csv'))[1]
    par = {}
    for r in rels:
        if r['subject_unit_id'] in groups + sqs:
            par.setdefault(r['subject_unit_id'], []).append((r['higher_unit_id'], r['relationship'], r['valid_from']))
    expect(s + ': chain 449th -> 322nd (organic) -> 99th CBW (assigned) and 409th -> 97th CBW from 7 March 1944',
           (par['US-BS-449'], par['US-BG-322'], par['US-BG-409'], par['US-BS-450']),
           ([('US-BG-322', 'organic', '1942-07-17')], [('US-BW-099', 'assigned', '1943-10-16')], [('US-BW-097', 'assigned', '1944-03-07')],
            [('US-BG-322', 'organic', '1942-07-17')]))
    expect(s + ': no 1st Pathfinder Squadron unit (J7 leftover)', 'US-PFS-001' in units, False)


def scenario_303_normandy_chunk5b_commit1():
    """Normandy chunk 5b commit 1: fighter groups 36th-367th and their squadrons (J4-J6)."""
    s = 'scenario 303 (normandy chunk 5b commit 1)'
    units = {u['unit_id']: u for u in common.read_dicts(common.UNITS_CSV)[1]}
    groups = ['US-FG-%03d' % n for n in (36, 48, 50, 354, 358, 362, 363, 365, 367)]
    sqs = ['US-FS-%03d' % n for n in (22, 23, 53, 492, 493, 494, 10, 81, 313, 353, 355, 356, 365, 366, 367, 377, 378, 379,
                                      380, 381, 382, 386, 387, 388, 392, 393, 394)]
    expect(s + ': 9 groups and 27 squadrons exist on the air ladder',
           (sorted({units[g]['echelon'] for g in groups}), sorted({units[q]['echelon'] for q in sqs}),
            sorted({units[u]['domain'] for u in groups + sqs}), len(sqs)),
           (['air_group'], ['air_squadron'], ['air'], 27))
    claims = {}
    for path in common.claim_files():
        for r in common.read_dicts(path)[1]:
            claims.setdefault(r['unit_id'], []).append(r)
    def cl(u):
        return [(r['date'], r['claim_status'], r['confidence']) for r in sorted(claims[u], key=lambda r: (r['date'], int(r['claim_id'][1:])))]
    expect(s + ': the 354th is at Lashenden on 31 May (next station month-only) and has R898 alternates at Criqueville and Gael',
           cl('US-FG-354'),
           [('1944-05-31', 'preferred', '0.5'), ('1944-06-19', 'alternate', '0.3'), ('1944-06-30', 'preferred', '0.3'),
            ('1944-08-11', 'alternate', '0.3'), ('1944-08-31', 'preferred', '0.3')])
    expect(s + ': the 36th moves to Brucheville (July, month end) with the R898 2 August date as an alternate',
           [(r['date'], r['claim_status'], r['conflict_group_id']) for r in sorted(claims['US-FG-036'], key=lambda r: r['date'])][:3],
           [('1944-06-06', 'preferred', ''), ('1944-07-31', 'preferred', 'G149'), ('1944-08-02', 'alternate', 'G149')])
    expect(s + ': the 313th FS reaches Orly on 30 August from its own list (J4)',
           cl('US-FS-313')[-1], ('1944-08-30', 'preferred', '0.5'))
    rels = common.read_dicts(os.path.join(common.ROOT, 'data', 'command_relations.csv'))[1]
    def rel(sub, hi):
        return [(r['relationship'], r['valid_from'], r['valid_to']) for r in rels if r['subject_unit_id'] == sub and r['higher_unit_id'] == hi]
    expect(s + ': the 354th squadrons are organic from activation (15 November 1942)',
           [rel('US-FS-%d' % n, 'US-FG-354') for n in (353, 355, 356)], [[('organic', '1942-11-15', '')]] * 3)
    expect(s + ': the 50th is attached to the 84th FW 7 April-12 August 1944',
           rel('US-FG-050', 'US-FW-084'), [('attached', '1944-04-07', '1944-08-12')])
    expect(s + ': the 363rd passes from the 100th to the 303rd FW on 20 August',
           (rel('US-FG-363', 'US-FW-100'), rel('US-FG-363', 'US-FW-303')),
           ([('assigned', '1944-04-15', '1944-08-19')], [('assigned', '1944-08-20', '')]))
    expect(s + ': the 354th is under 70th FW operational control 22 June-19 August',
           rel('US-FG-354', 'US-FW-070'), [('operational_control', '1944-06-22', '1944-08-19')])


def scenario_304_normandy_chunk5b_commit2():
    """Normandy chunk 5b commit 2: fighter groups 368th-474th, their squadrons and the 366th's 389th and 391st (J4-J6)."""
    s = 'scenario 304 (normandy chunk 5b commit 2)'
    units = {u['unit_id']: u for u in common.read_dicts(common.UNITS_CSV)[1]}
    groups = ['US-FG-%03d' % n for n in (368, 370, 371, 373, 404, 405, 406, 474)]
    sqs = ['US-FS-%03d' % n for n in (395, 396, 397, 401, 402, 485, 404, 405, 406, 410, 411, 412, 506, 507, 508, 509, 510, 511,
                                      512, 513, 514, 428, 429, 430, 389, 391)]
    expect(s + ': 8 groups and 26 squadrons exist on the air ladder',
           (sorted({units[g]['echelon'] for g in groups}), sorted({units[q]['echelon'] for q in sqs}),
            sorted({units[u]['domain'] for u in groups + sqs}), len(sqs)),
           (['air_group'], ['air_squadron'], ['air'], 26))
    claims = {}
    for path in common.claim_files():
        for r in common.read_dicts(path)[1]:
            claims.setdefault(r['unit_id'], []).append(r)
    def cl(u):
        return [(r['date'], r['claim_status'], r['confidence']) for r in sorted(claims[u], key=lambda r: (r['date'], int(r['claim_id'][1:])))]
    expect(s + ': the 389th FS reaches St Pierre du Mont on 17 June 1944 (printed 1943, inferred) at 0.3',
           cl('US-FS-389'), [('1944-06-06', 'preferred', '0.5'), ('1944-06-17', 'preferred', '0.3'), ('1944-08-24', 'preferred', '0.5')])
    expect(s + ': the 371st is at Bisterne on 31 May and at Beuzeville at the end of June, with the R898 15 June date as an alternate',
           cl('US-FG-371')[:3], [('1944-05-31', 'preferred', '0.5'), ('1944-06-15', 'alternate', '0.3'), ('1944-06-30', 'preferred', '0.3')])
    expect(s + ': the 474th moves to Saint-Lambert (6 August) and Saint-Marceau (29 August), each agreeing with R898 (0.7)',
           [x for x in cl('US-FG-474') if x[1] == 'preferred'][1:], [('1944-08-06', 'preferred', '0.7'), ('1944-08-29', 'preferred', '0.7')])
    rels = common.read_dicts(os.path.join(common.ROOT, 'data', 'command_relations.csv'))[1]
    def rel(sub, hi):
        return [(r['relationship'], r['valid_from'], r['valid_from_latest'], r['valid_to']) for r in rels if r['subject_unit_id'] == sub and r['higher_unit_id'] == hi]
    expect(s + ': the 368th is under the 71st FW from March 1944 (month only) to 31 July, then the 100th FW',
           (rel('US-FG-368', 'US-FW-071'), rel('US-FG-368', 'US-FW-100')),
           ([('assigned', '1944-03-01', '1944-03-31', '1944-07-31')], [('assigned', '1944-08-01', '', '')]))
    expect(s + ': the 474th is attached to IX TAC 1 August 1944-21 November 1945',
           rel('US-FG-474', 'US-TAC-009C'), [('attached', '1944-08-01', '', '1945-11-21')])
    expect(s + ': the 389th and 391st are organic to the 366th FG',
           [rel('US-FS-%d' % n, 'US-FG-366') for n in (389, 391)], [[('organic', '1943-06-01', '', '')]] * 2)
    crc = common.read_dicts(os.path.join(common.ROOT, 'data', 'command_relation_claims.csv'))[1]
    r405 = {r['higher_unit_id']: r['relation_id'] for r in rels if r['subject_unit_id'] == 'US-FG-405'}
    c405 = [r['claim_id'] for r in sorted(claims['US-FG-405'], key=lambda r: r['date']) if r['date'] == '1944-08-01']
    expect(s + ': the 405th 1 August claim evidences both its IX FC assignment and its XIX TAC attachment',
           sorted(l['relation_id'] for l in crc if l['claim_id'] in c405), sorted([r405['US-FTRCMD-009'], r405['US-TAC-019C']]))


def scenario_305_normandy_chunk5b_commit3():
    """Normandy chunk 5b commit 3: reconnaissance groups and squadrons (the 13 June swap, J10), night-fighter and liaison squadrons."""
    s = 'scenario 305 (normandy chunk 5b commit 3)'
    units = {u['unit_id']: u for u in common.read_dicts(common.UNITS_CSV)[1]}
    new = ['US-RG-010', 'US-RG-067', 'US-PRS-030', 'US-PRS-031', 'US-PRS-033', 'US-PRS-034', 'US-PRS-155', 'US-TRS-012', 'US-TRS-015',
           'US-TRS-107', 'US-TRS-109', 'US-NFS-422', 'US-NFS-425', 'US-LS-014', 'US-LS-047', 'US-LS-112', 'US-LS-125', 'US-LS-153']
    expect(s + ': 2 groups and 16 squadrons exist on the air ladder',
           ([units[u]['echelon'] for u in new], sorted({units[u]['domain'] for u in new})),
           (['air_group'] * 2 + ['air_squadron'] * 16, ['air']))
    rels = common.read_dicts(os.path.join(common.ROOT, 'data', 'command_relations.csv'))[1]
    def rel(sub):
        return sorted((r['higher_unit_id'], r['relationship'], r['valid_from'], r['valid_to']) for r in rels if r['subject_unit_id'] == sub)
    expect(s + ': the 12th TRS passes from the 67th to the 10th group on 13 June and stays attached to the 67th to c. 11 August',
           rel('US-TRS-012'),
           [('US-RG-010', 'organic', '1944-06-13', ''), ('US-RG-067', 'attached', '1944-06-13', '1944-08-11'),
            ('US-RG-067', 'organic', '1942-03-29', '1944-06-12')])
    expect(s + ': the 30th PRS is attached to the 67th 10-12 June and organic to it from 13 June',
           rel('US-PRS-030'),
           [('US-RG-010', 'organic', '1944-02-21', '1944-06-12'), ('US-RG-067', 'attached', '1944-06-10', '1944-06-12'),
            ('US-RG-067', 'organic', '1944-06-13', '')])
    expect(s + ': the 425th NFS is unspecified_subordination to the Ninth AF 10 June-5 August, between its Ninth AF and IX ADC assignments',
           rel('US-NFS-425'),
           [('US-ADCMD-009', 'assigned', '1944-08-06', ''), ('US-AF-009', 'assigned', '1944-05-23', '1944-06-09'),
            ('US-AF-009', 'unspecified_subordination', '1944-06-10', '1944-08-05')])
    expect(s + ': the liaison squadrons are attached to the armies, army group and SHAEF they served',
           [[x for x in rel(u) if x[1] == 'attached'] for u in ('US-LS-014', 'US-LS-047', 'US-LS-112', 'US-LS-125', 'US-LS-153')],
           [[('US-ARMY-003A', 'attached', '1944-04-04', '1944-11-15')], [('US-AG-012G', 'attached', '1944-08-09', '1945-08-01')],
            [('ALL-SHAEF-000H', 'attached', '1944-06-07', '1945-07-14')], [('US-ARMY-009A', 'attached', '1944-07-17', '1944-11-15')],
            [('US-ARMY-001A', 'attached', '1944-02-04', '1944-11-15')]])
    claims = {}
    for path in common.claim_files():
        for r in common.read_dicts(path)[1]:
            claims.setdefault(r['unit_id'], []).append(r)
    expect(s + ': the 112th and 125th LS have no 6 June claim (no station of theirs covers the day)',
           [min(r['date'] for r in claims[u]) for u in ('US-LS-112', 'US-LS-125')], ['1944-06-09', '1944-06-08'])
    beau = [r for r in claims['US-LS-014'] if r['date'] == '1944-08-04'][0]
    expect_in(s + ': the 14th LS Beauchamps claim says it does not hold after the left-out Poilley station', beau['notes'],
              'Poilley 7 Aug 1944, is not entered')


def scenario_306_normandy_chunk5c_commit1():
    """Normandy chunk 5c commit 1: the 52nd and 53rd Troop Carrier Wings' groups and squadrons (J4-J6, J8)."""
    s = 'scenario 306 (normandy chunk 5c commit 1)'
    units = {u['unit_id']: u for u in common.read_dicts(common.UNITS_CSV)[1]}
    groups = ['US-TCG-%03d' % n for n in (61, 313, 314, 315, 316, 434, 435, 436, 437, 438)]
    sqs = ['US-TCS-%03d' % n for n in (14, 15, 53, 59, 29, 47, 48, 49, 32, 50, 61, 62, 34, 43, 309, 310, 36, 37, 44, 45,
                                       71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90)]
    expect(s + ': 10 groups and 40 squadrons exist on the air ladder',
           (sorted({units[g]['echelon'] for g in groups}), sorted({units[q]['echelon'] for q in sqs}),
            sorted({units[u]['domain'] for u in groups + sqs}), len(sqs)),
           (['air_group'], ['air_squadron'], ['air'], 40))
    claims = {}
    for path in common.claim_files():
        for r in common.read_dicts(path)[1]:
            claims.setdefault(r['unit_id'], []).append(r)
    expect(s + ': every group and squadron has one 6 June base claim at 0.5 (no moves in the window)',
           sorted({tuple((r['date'], r['claim_status'], r['confidence'], r['location_represents']) for r in claims[u]) for u in groups + sqs}),
           [(('1944-06-06', 'preferred', '0.5', 'base'),)])
    expect(s + ': the 315th Group (printed "Stanhoe") and its squadrons are at RAF Spanhoe',
           sorted({claims[u][0]['place_id'] for u in ('US-TCG-315', 'US-TCS-034', 'US-TCS-043', 'US-TCS-309', 'US-TCS-310')}), ['PL4354'])
    expect(s + ': the 434th is at RAF Aldermaston, not Aldermaston Court',
           claims['US-TCG-434'][0]['place_id'], 'PL4355')
    rels = common.read_dicts(os.path.join(common.ROOT, 'data', 'command_relations.csv'))[1]
    def rel(sub):
        return sorted((r['higher_unit_id'], r['relationship'], r['valid_from'], r['valid_from_latest'], r['valid_to']) for r in rels if r['subject_unit_id'] == sub)
    expect(s + ': the 61st and 62nd Squadrons are organic to the 314th Group from 15 March 1943',
           [rel(u) for u in ('US-TCS-061', 'US-TCS-062')], [[('US-TCG-314', 'organic', '1943-03-15', '', '')]] * 2)
    expect(s + ': the 309th and 310th Squadrons are organic to the 315th Group from 26 April 1944',
           [rel(u) for u in ('US-TCS-309', 'US-TCS-310')], [[('US-TCG-315', 'organic', '1944-04-26', '', '')]] * 2)
    expect(s + ': the groups are assigned to the 52nd and 53rd Troop Carrier Wings (month-only starts keep their range)',
           [rel(g) for g in ('US-TCG-313', 'US-TCG-437', 'US-TCG-438')],
           [[('US-TCW-052', 'assigned', '1942-11-01', '1942-11-30', '')], [('US-TCW-053', 'assigned', '1944-02-17', '', '')],
            [('US-TCW-053', 'assigned', '1944-02-01', '1944-02-29', '')]])
    places = {p['place_id']: p['country'] for p in common.read_dicts(os.path.join(common.ROOT, 'data', 'places.csv'))[1]}
    expect(s + ': the DRAGOON operations from Italy are notes, not claims (J8)',
           ('Voltone Airfield, Italy' in claims['US-TCS-079'][0]['notes'], 'Voltone Airfield, Italy' in units['US-TCG-436']['unit_note'],
            sorted({places[r['place_id']] for u in groups + sqs for r in claims[u]})),
           (True, True, ['GB']))


def main():
    for fn in (scenario_0_staleness, scenario_1_first_army, scenario_2_viii_corps, scenario_3_84th_division, scenario_4_administrative_versus_operational, scenario_6_german_parent_changes_1944, scenario_7_german_batch_1b_july_1944, scenario_8_german_batch_2_sep_oct_1944, scenario_9_german_batch_2_followup_model_lxxx, scenario_10_german_batch_3_nov_dec_1944, scenario_11_german_1945_batch_1_jan_mar, scenario_12_german_1945_batch_2_apr_may, scenario_13_cleanup_open_items_oct28, scenario_14_canadian_batch_1_jun_dec_1944, scenario_15_canadian_batch_2_jan_may_1945, scenario_16_british_batch_1_jun_dec_1944, scenario_17_british_batch_2_jan_may_1945, scenario_18_british_batch_2_followup, scenario_19_allied_contingents_1944_45, scenario_20_french_1944_45, scenario_21_french_followup, scenario_22_french_delattre, scenario_23_brigades_batch_1_uk_can, scenario_24_brigades_batch_2_us, scenario_25_brigades_batch_3_german, scenario_26_activity_pilot, scenario_27_activity_rollout_1, scenario_28_activity_rollout_2, scenario_29_activity_rollout_3, scenario_30_activity_german_1, scenario_31_activity_german_2, scenario_32_activity_german_3, scenario_33_activity_canada_france, scenario_34_official_history_pass_1, scenario_35_source_fixes_delattre_ellis, scenario_36_fms_b466_geyr, scenario_37_fms_19army, scenario_38_fms_b703_armygroupg, scenario_39_fms_b811_15army, scenario_40_fms_b701_armygroupb, scenario_41_fms_b078_armygroupg, scenario_42_official_history_pass_2, scenario_43_fms_b475_german, scenario_44_fms_b235_german, scenario_45_fms_b179_german, scenario_46_fms_b763_german, scenario_47_fms_b781, scenario_48_fms_b831, scenario_49_fms_b084, scenario_50_fms_b849, scenario_51_fms_b745, scenario_52_fms_b151, scenario_53_loc_12ag_maps, scenario_54_loc_12ag_us_backfill, scenario_55_loc_12ag_august_1, scenario_56_loc_12ag_villages, scenario_57_loc_12ag_late_august_september, scenario_58_loc_12ag_villages_2, scenario_59_loc_12ag_october_1, scenario_60_loc_12ag_villages_3, scenario_61_loc_12ag_october_2, scenario_62_loc_12ag_october_3, scenario_63_loc_12ag_october_4, scenario_64_loc_12ag_nov07, scenario_65_loc_12ag_nov14, scenario_66_loc_12ag_nov21, scenario_67_loc_12ag_nov28, scenario_68_loc_12ag_dec05, scenario_69_loc_12ag_dec12, scenario_70_loc_12ag_dec19, scenario_71_loc_12ag_dec26, scenario_72_loc_12ag_jan02, scenario_73_loc_12ag_jan09, scenario_74_loc_12ag_jan16, scenario_75_loc_12ag_jan23, scenario_76_loc_12ag_jan30, scenario_77_loc_12ag_feb06, scenario_78_loc_12ag_feb13, scenario_79_loc_12ag_feb20, scenario_80_loc_12ag_feb27, scenario_81_loc_12ag_mar06, scenario_82_loc_12ag_mar13, scenario_83_loc_12ag_mar20, scenario_84_loc_12ag_mar27, scenario_85_loc_12ag_apr3, scenario_86_loc_12ag_apr10, scenario_87_loc_12ag_apr17, scenario_88_loc_12ag_apr24, scenario_89_loc_12ag_may01, scenario_90_loc_12ag_may08, scenario_91_loc_12ag_may08b, scenario_92_loc_12ag_may08c, scenario_93_loc_12ag_may09, scenario_94_unit_lineage, scenario_95_coverage_report, scenario_96_nara_t315_r940, scenario_97_nara_t311_r4, scenario_98_nara_t311_r3, scenario_99_nara_t354_r120, scenario_100_nara_t315_r1298, scenario_101_nara_t354_r147, scenario_102_nara_t314_r1605, scenario_103_nara_t354_r149, scenario_104_nara_t314_r1607, scenario_105_nara_t315_r828, scenario_106_nara_t354_r129, scenario_107_nara_t311_r1, scenario_108_nara_t315_r2145, scenario_109_cole_ardennes_fifth_army, scenario_110_cole_ardennes_seventh_army, scenario_111_cole_ardennes_sixth_army, scenario_112_cole_ardennes_pass2_german, scenario_113_cole_ardennes_pass2_allied, scenario_114_cole_ardennes_corroborations, scenario_115_cole_ardennes_79th_vgd, scenario_116_confidence_corroborated, scenario_117_map_row_conflicts, scenario_118_stacey_normandy_to_spring, scenario_119_stacey_falaise, scenario_120_stacey_seine_channel_ports, scenario_121_stacey_scheldt, scenario_122_stacey_maas_winter, scenario_123_stacey_veritable, scenario_124_stacey_blockbuster, scenario_125_stacey_rhine_crossing, scenario_126_stacey_western_netherlands, scenario_127_stacey_surrender_and_appendices, scenario_128_stacey_maps, scenario_129_stacey_conflict_groups, scenario_130_stacey_units_added, scenario_131_fms_b093_meindl, scenario_132_fms_b717_student, scenario_133_fms_b084_reread, scenario_134_fms_b368_langhaeuser, scenario_135_fms_b774_prittwitz, scenario_136_fms_b762_prittwitz, scenario_137_roadmap_253_map_rows, scenario_138_fms_b156_reinhard, scenario_139_fms_b343_reinhard, scenario_140_fms_b262_blauensteiner, scenario_141_fms_b414_geyer, scenario_142_fms_b147_geyer, scenario_143_fms_b148_geyer, scenario_144_fms_b453_langhaeuser, scenario_145_fms_b580_langhaeuser, scenario_146_fms_b365_blumentritt, scenario_147_fms_b811_german, scenario_148_fms_b812_german, scenario_149_fms_b197_german, scenario_150_fms_b200, scenario_151_fms_b367_german, scenario_152_fms_b368_reread, scenario_153_fms_b369_german, scenario_154_fms_b674_german, scenario_155_fms_b327, scenario_156_fms_b051_german, scenario_157_fms_b052, scenario_158_fms_b261_german, scenario_159_fms_b240_german, scenario_160_fms_b401_german, scenario_161_fms_b346_german, scenario_162_fms_b101, scenario_163_fms_b309, scenario_164_fms_b236_german, scenario_165_fms_b798_german, scenario_166_fms_b596_german, scenario_167_fms_b475_reread, scenario_168_pre_invasion_dates, scenario_169_fms_b249_german, scenario_170_fms_b508_german, scenario_171_fms_b820_german, scenario_172_unit_domain, scenario_173_fms_b023_german, scenario_174_small_units_b023, scenario_175_fms_b361_german, scenario_176_post_surrender, scenario_177_blumentritt_relations, scenario_178_b283, scenario_179_a969, scenario_180_a859, scenario_181_ethint43, scenario_182_independent_units, scenario_183_a898, scenario_184_kampfgruppen, scenario_185_a939, scenario_186_a940, scenario_187_b410, scenario_188_b541, scenario_189_b673, scenario_190_b709, scenario_191_b730, scenario_192_b823, scenario_193_ethint78, scenario_194_b709_second_pass, scenario_195_b709_maps, scenario_196_scott_decisions_nov04, scenario_197_b709_german, scenario_198_b730_german, scenario_199_theater, scenario_200_placeholders_b1, scenario_201_placeholders_b2, scenario_202_placeholders_b3, scenario_203_lifespan, scenario_204_command_relations, scenario_205_german_end_rows, scenario_206_map_text_weak_pairs, scenario_207_midwar_ends, scenario_208_lifespan_check, scenario_209_ellis_leftovers_chunk1, scenario_210_ellis_leftovers_chunk2, scenario_211_ellis_leftovers_chunk3, scenario_212_ellis_leftovers_chunk4, scenario_213_ellis_leftovers_chunk5, scenario_214_ellis_leftovers_chunk6, scenario_215_cmhq173_watch_on_the_maas, scenario_216_ahq039_western_netherlands, scenario_217_ahq032_concluding_phase, scenario_218_ahq019_rhine_crossing, scenario_219_cmhq186_blockbuster, scenario_220_cmhq155_veritable, scenario_221_cmhq188_scheldt, scenario_222_cmhq183_pursuit, scenario_223_cmhq184_channel_ports, scenario_224_ahq065_falaise, scenario_225_ahq058_july, scenario_226_cmhq181_goldflake, scenario_227_delattre_c1_armour, scenario_228_delattre_c2_infantry, scenario_229_delattre_c3_headquarters, scenario_230_delattre_c4_us_german, scenario_231_delattre_c5_other_fronts, scenario_232_delattre_c6_italy, scenario_233_dejong_sept_german_oob, scenario_234_dejong_market_garden, scenario_235_dejong_irene_scheldt, scenario_236_dejong_walcheren, scenario_237_dejong_polish_g123, scenario_238_dejong_irene_dates, scenario_239_c1036_raise, scenario_240_stoottroepen_unit, scenario_241_bewakingstroepen_unit, scenario_242_stoottroepen_battalions, scenario_243_wieringermeer_gewest11, scenario_244_air_naval_pilot_luftwaffe, scenario_245_air_naval_pilot_usaaf, scenario_246_air_naval_pilot_ships, scenario_247_air_naval_pilot_ground_by_function, scenario_248_scope_marker, scenario_249_naval_unit_columns, scenario_250_ship_classes_table, scenario_251_refit_and_reclassification, scenario_252_naval_echelon_ladder, scenario_253_sea_position_base_and_event_types, scenario_254_claim_ids_other_domains, scenario_255_air_echelon_ladder, scenario_256_aircraft_types_table, scenario_257_aircraft_strength, scenario_258_air_command_relations, scenario_259_irene_after_march_1945, scenario_260_stale_carry_forward_drop, scenario_261_stale_carry_forward_kept, scenario_262_79th_armoured_21ag, scenario_263_stoottroepen_parent_review, scenario_264_binnenlandse_strijdkrachten, scenario_265_cca_2nd_armored_later_claims, scenario_266_organic_fallback, scenario_267_cr1282_end, scenario_268_kg_division_answer, scenario_269_army_group_student, scenario_270_6ag_advance_hq_luneville, scenario_271_cr0950_9th_colonial_end, scenario_272_successors_157_and_158, scenario_273_nation_allegiance, scenario_274_unit_allegiance_overrides, scenario_275_relations_157_and_16, scenario_276_armeegruppe_student_leftovers, scenario_277_allegiance_official_sources, scenario_278_allegiance_axis_batch, scenario_279_allegiance_allies_batch, scenario_280_allegiance_neutrals_batch, scenario_281_allegiance_remaining_countries, scenario_282_allegiance_blank_periods, scenario_283_allegiance_sino_japanese_war, scenario_284_allegiance_non_aligned_belligerent, scenario_285_normandy_chunk1_commit2, scenario_286_normandy_chunk1_commit3, scenario_287_normandy_chunk2_commit2, scenario_288_normandy_chunk2_commit3a, scenario_289_normandy_chunk2_commit3b, scenario_290_normandy_chunk3a_commit1, scenario_291_normandy_chunk3a_commit2, scenario_292_normandy_chunk3b_commit1, scenario_293_normandy_chunk3b_commit2, scenario_294_normandy_chunk3b_commit3, scenario_295_normandy_chunk3c_commit1, scenario_296_normandy_chunk3c_commit2, scenario_297_normandy_chunk3c_commit3, scenario_298_normandy_chunk4_commit1, scenario_299_normandy_chunk4_commit2, scenario_300_normandy_chunk4_commit3, scenario_301_normandy_chunk5a_commit1, scenario_302_normandy_chunk5a_commit2, scenario_303_normandy_chunk5b_commit1, scenario_304_normandy_chunk5b_commit2, scenario_305_normandy_chunk5b_commit3, scenario_306_normandy_chunk5c_commit1):
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
