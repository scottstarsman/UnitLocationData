#!/usr/bin/env python3
"""OBSOLETE (superseded by scripts/migrate_operations.py, which replaced these columns by operation_id). One-off migration (Batch 3 review): add the `campaign` column to every claim file and stop using the umbrella operation_name labels.

1. Inserts `campaign` before `operation_name` in every file under data/claims/ (idempotent: skipped when the column exists).
2. Backfills `campaign` from the CMH campaign streamer dates (schema/vocabularies.json, vocabulary `campaign`):
     6 Jun-24 Jul 1944 Normandy; 25 Jul-14 Sep Northern France (rows of the Dragoon operation dated 15 Aug-14 Sep: Southern France);
     15 Sep-15 Dec Rhineland; 16 Dec 1944-25 Jan 1945 Ardennes-Alsace for rows of the Ardennes and Alsace fighting (sub_operation_name
     Ardennes, Bastogne, Alsace, Colmar, or operation Dragoon) and Rhineland for the others; 22 Mar-11 May 1945 Central Europe.
3. Blanks operation_name where the row is dated after the operation it names (Overlord after 30 Aug 1944, Dragoon after 14 Sep 1944,
   Market Garden outside 17-25 Sep 1944); sub_operation_name is kept as it was.
Run once from the repository root: python scripts/migrate_campaign.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common  # noqa: E402

ARD_ALS = {'Ardennes', 'Bastogne', 'Alsace', 'Colmar'}


def campaign_for(d, op, sub):
    if d <= '1944-07-24':
        return 'Normandy'
    if d <= '1944-09-14':
        return 'Southern France' if (op == 'Dragoon' and d >= '1944-08-15') else 'Northern France'
    if d <= '1944-12-15':
        return 'Rhineland'
    if d <= '1945-01-25':
        subs = {x.strip() for x in sub.split(';')}
        return 'Ardennes-Alsace' if (subs & ARD_ALS or op == 'Dragoon') else 'Rhineland'
    if d <= '1945-03-21':
        return 'Rhineland'
    return 'Central Europe'


def main():
    if 'operation_id' in common.field_names(common.load_schema('claims')):
        print('obsolete: the campaign, operation_name and sub_operation_name columns were replaced by operation_id (scripts/migrate_operations.py)')
        return 0
    vocabs = common.load_vocabularies()
    odates = vocabs['operation_name']['dates']
    names = common.field_names(common.load_schema('claims'))
    changed = 0
    for p in common.claim_files():
        header, rows = common.read_rows(p)
        if 'campaign' in header:
            continue
        i_op, i_sub, i_date = header.index('operation_name'), header.index('sub_operation_name'), header.index('date')
        new_rows = []
        for r in rows:
            op, sub, d = r[i_op], r[i_sub], r[i_date]
            camp = campaign_for(d, op, sub)
            if op in odates and not (odates[op][0] <= d <= odates[op][1]):
                r = r[:i_op] + [''] + r[i_op + 1:]
            new_rows.append(r[:i_op] + [camp] + r[i_op:])
        new_header = header[:i_op] + ['campaign'] + header[i_op:]
        assert new_header == names, (new_header, names)
        with open(p, 'wb') as f:
            f.write(common.csv_bytes(new_header, new_rows))
        changed += 1
    print('migrated %d claim files' % changed)


if __name__ == '__main__':
    main()
