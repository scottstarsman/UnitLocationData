#!/usr/bin/env python3
"""One-off migration (operations table): replace the claim columns campaign, operation_name and sub_operation_name by `operation_id`.

NOTE (places-table): Historical, one-off: it was written for claim files that still had `location_name`, `strength_status`, `location_temporal_offset_days` and the `; coords:` tail of `source`; since `places-table` those are a place (data/places.csv, scripts/migrate_places.py) and derived values (scripts/places.py), so it cannot be run on the current layout.

Kept for provenance; it does nothing once the claim files carry operation_id. Run once from the repository root:
    python scripts/migrate_operations.py [--report FILE]

For each claim the old labels are mapped to the most specific row of data/operations.csv:
  1. sub_operation_name (or Dragoon / Market Garden in operation_name) names an operation row  -> that row, when the claim's date lies
     inside the row's dates;
  2. when the date lies outside but within ADJACENT_DAYS of the dates (a preparation or aftermath row the earlier dataset labelled with
     the operation), the row is kept and the claim is added to data/operation_exceptions.csv with the reason;
  3. otherwise (no matching row, or a date far outside the dates) the claim takes the CMH campaign it already carried and is listed in
     the report as unmatched;
  4. a label with two values (Martlet; Epsom, Roer; Clipper) takes the operation named in LABEL_CHOICE and is listed in the report.
Nothing is inferred beyond the old labels and the dates. The script also checks that the derived campaign and operation_name
(scripts/operations.py) equal the old values for every claim and reports the differences.
"""
import argparse
import csv
import datetime
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common  # noqa: E402
import operations  # noqa: E402

ADJACENT_DAYS = 7

SUB_TO_OP = {
    'Neptune': 'OP-NEPTUNE', 'Tonga': 'OP-TONGA', 'Perch': 'OP-PERCH', 'Epsom': 'OP-EPSOM', 'Martlet': 'OP-MARTLET',
    'Cherbourg': 'OP-CHERBOURG', 'Cutting the Cotentin': 'OP-COTENTIN-CUT', 'Battle of Carentan': 'OP-CARENTAN',
    'Battle of Bloody Gulch': 'OP-BLOODY-GULCH', 'Cobra': 'OP-COBRA', 'Brittany': 'OP-BRITTANY', 'Brest': 'OP-BREST',
    'Mortain': 'OP-MORTAIN', 'Falaise': 'OP-FALAISE', 'Falaise-Argentan': 'OP-FALAISE', 'Paris': 'OP-PARIS', 'Pursuit': 'OP-PURSUIT',
    'Lorraine': 'OP-LORRAINE', 'Siegfried Line approach': 'OP-SIEGFRIED-LINE', 'Siegfried Line': 'OP-SIEGFRIED-LINE',
    'Aachen': 'OP-AACHEN', 'Scheldt': 'OP-SCHELDT', 'Vosges': 'OP-VOSGES', 'Roer': 'OP-QUEEN', 'Clipper': 'OP-CLIPPER',
    'Market Garden': 'OP-MARKET-GARDEN', 'Ardennes': 'OP-BULGE', 'Bastogne': 'OP-BASTOGNE',
}
OPERATION_TO_OP = {'Dragoon': 'OP-DRAGOON', 'Market Garden': 'OP-MARKET-GARDEN'}
CAMPAIGN_TO_OP = {'Normandy': 'OP-CAMP-NORMANDY', 'Northern France': 'OP-CAMP-NORTHERN-FRANCE', 'Southern France': 'OP-CAMP-SOUTHERN-FRANCE',
                  'Rhineland': 'OP-CAMP-RHINELAND', 'Ardennes-Alsace': 'OP-CAMP-ARDENNES-ALSACE', 'Central Europe': 'OP-CAMP-CENTRAL-EUROPE'}
# labels with two values: the operation taken, and why
LABEL_CHOICE = {
    'Martlet; Epsom': ('OP-EPSOM', 'Martlet supported Epsom (data/operation_relations.csv); the rows are German reactions to the whole offensive, so the larger operation is taken'),
    'Roer; Clipper': ('OP-CLIPPER', 'the row is the 84th Division attack at Geilenkirchen, which is Clipper; Clipper ran alongside the Roer offensive (Queen)'),
}
# why old labels have no operation row
NO_ROW = {
    'Return to England': 'a return move, not an operation',
    'Market Garden preparations': 'Market Garden opens on 17 September; the rows are command changes of the airborne units in August',
    'Le Mans': 'no named operation or battle row (XV Corps capture of Le Mans, 8-9 August)',
    'Loire': 'no named operation or battle row (Loire valley sector)',
    'Seine': 'no named operation or battle row (Seine crossings)',
    'Alsace': 'no named operation or battle row (Alsace, December 1944; Operation Nordwind began on 31 December)',
}


def days(a, b):
    f = lambda s: datetime.date.fromisoformat(s)  # noqa: E731
    return (f(a) - f(b)).days


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--report', help='write the backfill report (markdown) to this file')
    ap.add_argument('--dry-run', action='store_true')
    a = ap.parse_args()
    ops = operations.load()
    ids = set(ops.by_id)
    for v in list(SUB_TO_OP.values()) + list(OPERATION_TO_OP.values()) + list(CAMPAIGN_TO_OP.values()):
        assert v in ids, v
    stats = {'files': 0, 'rows': 0}
    matched, adjacent, unmatched, multi, diffs = [], [], [], [], []
    exceptions = []
    out_files = []
    for p in common.claim_files():
        header, rows = common.read_rows(p)
        if 'operation_id' in header:
            continue
        i_c, i_o, i_s, i_d = (header.index(x) for x in ('campaign', 'operation_name', 'sub_operation_name', 'date'))
        i_id, i_u = header.index('claim_id'), header.index('unit_name')
        new_header = header[:i_c] + ['operation_id'] + [h for j, h in enumerate(header) if j > i_s]
        new_rows = []
        for r in rows:
            camp, op, sub, date = r[i_c], r[i_o], r[i_s], r[i_d]
            cid = r[i_id]
            label = sub or op or camp
            if camp not in CAMPAIGN_TO_OP:
                raise SystemExit('%s: campaign %r has no operation row' % (cid, camp))
            leaf, why = CAMPAIGN_TO_OP[camp], ''
            cand, note = None, ''
            if sub in LABEL_CHOICE:
                cand, note = LABEL_CHOICE[sub]
                multi.append((cid, r[i_u], date, sub, cand, note))
            elif sub:
                cand = SUB_TO_OP.get(sub)
                if cand is None:
                    unmatched.append((cid, r[i_u], date, camp, op, sub, leaf, NO_ROW.get(sub, 'no operation row for this label')))
            elif op in OPERATION_TO_OP:
                cand = OPERATION_TO_OP[op]
            if cand:
                o = ops.by_id[cand]
                if o['start_date'] <= date <= o['end_date']:
                    leaf = cand
                    matched.append(cid)
                else:
                    gap = days(o['start_date'], date) if date < o['start_date'] else days(date, o['end_date'])
                    if gap <= ADJACENT_DAYS:
                        leaf = cand
                        side = 'before' if date < o['start_date'] else 'after'
                        reason = 'dated %d day(s) %s the dates of %s (%s to %s); the earlier dataset labelled the row %s (preparation or aftermath row)' % (
                            gap, side, o['name'], o['start_date'], o['end_date'], label)
                        exceptions.append([cid, cand, reason])
                        adjacent.append((cid, r[i_u], date, label, cand, gap, side))
                    else:
                        unmatched.append((cid, r[i_u], date, camp, op, sub, leaf,
                                          'dated %d days %s the dates of %s (%s to %s)' % (
                                              gap, 'before' if date < o['start_date'] else 'after', o['name'], o['start_date'], o['end_date'])))
            nr = r[:i_c] + [leaf] + [v for j, v in enumerate(r) if j > i_s]
            new_rows.append(nr)
            # compare derived labels with the old ones
            d = ops.labels(leaf, date)
            if d['campaign'] != camp or d['operation_name'] != op:
                diffs.append((cid, date, camp, op, sub, leaf, d['campaign'], d['operation_name']))
            stats['rows'] += 1
        stats['files'] += 1
        out_files.append((p, common.csv_bytes(new_header, new_rows)))
    print('files %d, rows %d: %d matched inside the dates, %d adjacent (exception), %d unmatched (campaign), %d two-label rows; %d derived-label differences'
          % (stats['files'], stats['rows'], len(matched), len(adjacent), len(unmatched), len(multi), len(diffs)))
    for d in diffs[:20]:
        print('  DIFF', d)
    if a.report:
        write_report(a.report, ops, matched, adjacent, unmatched, multi, diffs, stats)
    if a.dry_run or not out_files:
        return 0
    for p, data in out_files:
        with open(p, 'wb') as f:
            f.write(data)
    exceptions.sort()
    with open(operations.EXCEPTIONS_CSV, 'wb') as f:
        f.write(common.csv_bytes(operations.EXC_HEADER, exceptions))
    print('rewrote %d claim files and data/operation_exceptions.csv (%d rows)' % (len(out_files), len(exceptions)))
    return 0


def write_report(path, ops, matched, adjacent, unmatched, multi, diffs, stats):
    L = ['# Operations backfill', '',
         'How the 566 claims were moved from the three free-text columns (`campaign`, `operation_name`, `sub_operation_name`) to a single `operation_id` '
         '(`scripts/migrate_operations.py`). The old labels and the claim\'s date were the only inputs; nothing was guessed. A claim takes the most specific '
         'operation row named by its old labels when its date lies inside that row\'s dates; otherwise it takes the campaign it already carried and is listed here.', '',
         '| outcome | claims |', '|---|---:|',
         '| operation row named by the old label, date inside the row\'s dates | %d |' % len(matched),
         '| same, date within %d days of the dates (kept; listed in `data/operation_exceptions.csv`) | %d |' % (ADJACENT_DAYS, len(adjacent)),
         '| old label has no operation row, or the date is far outside the dates (campaign used) | %d |' % len(unmatched),
         '| two-label rows (one operation chosen) | %d |' % len(multi),
         '| rows with only a campaign or an umbrella label (campaign used) | %d |' % (stats['rows'] - len(matched) - len(adjacent) - len(unmatched) - len(multi)), '']
    L += ['## Unmatched or ambiguous claims (campaign used)', '',
          'These claims keep the CMH campaign as their `operation_id`. Add an operation row (see CONTRIBUTING.md) and set the claim\'s `operation_id` when a source supports one.', '',
          '| claim | unit | date | old labels (campaign / operation_name / sub_operation_name) | operation_id | reason |', '|---|---|---|---|---|---|']
    for cid, unit, date, camp, op, sub, leaf, why in sorted(unmatched):
        L.append('| %s | %s | %s | %s / %s / %s | %s | %s |' % (cid, unit, date, camp, op or '-', sub or '-', leaf, why))
    L += ['', '## Rows with two old labels', '',
          'Each of these belonged to two operations at once in the old columns. The operation tree does not need a many-to-many table for them: one operation is chosen and the other is linked in `data/operation_relations.csv`. If more such cases appear, a `claim_operations` link table can be added.', '',
          '| claim | unit | date | old sub_operation_name | operation_id | why |', '|---|---|---|---|---|---|']
    for cid, unit, date, sub, cand, note in sorted(multi):
        L.append('| %s | %s | %s | %s | %s | %s |' % (cid, unit, date, sub, cand, note))
    L += ['', '## Rows kept with an exception (dated just outside the operation)', '',
          'Preparation or aftermath rows the earlier dataset labelled with the operation; the full reasons are in `data/operation_exceptions.csv`.', '',
          '| claim | unit | date | old label | operation_id | days outside |', '|---|---|---|---|---|---|']
    for cid, unit, date, label, cand, gap, side in sorted(adjacent):
        L.append('| %s | %s | %s | %s | %s | %d %s |' % (cid, unit, date, label, cand, gap, side))
    L += ['', '## Placement decisions and contested boundaries', '',
          'Each is also stated in the `notes` and `parent_date_exception` columns of the operation row.', '',
          '- **Cobra** is a child of the Northern France campaign, not Normandy: it opened on 25 July, the first day of the Northern France streamer (the first bombing, on 24 July, was aborted). The 17 Cobra rows keep the Overlord label through the chain (Cobra > Northern France > Overlord).',
          '- **Overlord** ends on 30 August 1944 (Wikipedia; some sources say 25 August). It is an umbrella: it appears in the chain of Normandy and Northern France rows but, because the derived `operation_name` only names an operation on the dates it covers, it labels nothing after 30 August. No Rhineland or Ardennes-Alsace claim has it in its chain.',
          '- **Northern France** is a child of Overlord although the streamer runs to 14 September (`parent_date_exception`).',
          '- **Cherbourg** takes Wikipedia\'s wider window for the Cotentin operations (6 June-1 July) rather than the 22-27 June fight for the city, so the earlier VII Corps rows keep it.',
          '- **Brittany and Brest**: the end date (19 September) is set from the Green Book narrative; Wikipedia gives only "August-September" for Brittany and 20 September for Brest.',
          '- **Pursuit across France** is a derived phase (19 August-14 September): no source dates it. Pursuit-labelled rows before 19 August are listed above as unmatched.',
          '- **Bulge**: Wikipedia ends the battle on 28 January 1945, the streamer on 25 January.',
          '- **Aachen** starts on 12 September (Wikipedia), before the Rhineland streamer; the Siegfried Line campaign starts on 28 August (Wikipedia) but the Green Book volume on 11 September; the Vosges row takes Wikipedia\'s wide span (15 September 1944-15 February 1945).',
          '- **Lorraine, Siegfried Line** have no parent because they span two streamers; the derived `campaign` of their claims comes from the date.',
          '- **Operation Queen and Operation Clipper** are operations, so the derived `operation_name` of their rows is now Roer and Clipper (it was blank in the old columns); this is the only change in a derived value (4 rows).',
          '- **German names**: Lüttich (Mortain) and Wacht am Rhein (the Bulge) are rows in the table, linked to the Allied battle as `related`; no claim points at them. Nordwind is not in the table yet because no claim needs it.',
          '', '## Derived labels against the old columns', '',
          'build/all_claims.csv still carries `campaign`, `operation_name` and `sub_operation_name`, now derived from the operation chain (see schema/README.md). '
          'Differences from the old stored values for `campaign` or `operation_name`: %d. `campaign` is identical for all 566 claims. The derived `sub_operation_name` differs from the old text for 36 claims, in three ways: the old label has no operation row (Return to England, Le Mans, Loire, Seine, Market Garden preparations, Alsace, early Pursuit and Roer rows), so it is blank; it repeated the operation_name (Market Garden) or is now the operation_name (Roer, Clipper); or the label was normalised (Martlet; Epsom to Epsom, Falaise-Argentan to Falaise, Siegfried Line approach to Siegfried Line).' % len(diffs), '']
    if diffs:
        L += ['| claim | date | old campaign | old operation_name | old sub | operation_id | derived campaign | derived operation_name |', '|---|---|---|---|---|---|---|---|']
        for d in diffs:
            L.append('| ' + ' | '.join(x or '-' for x in d) + ' |')
        L.append('')
    with open(path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(L) + '\n')


if __name__ == '__main__':
    sys.exit(main())
