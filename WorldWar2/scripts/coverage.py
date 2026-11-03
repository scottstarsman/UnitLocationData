"""Coverage report and source-review queue (derived outputs only; see docs/coverage_report.md).

build/coverage_by_unit.csv   one row per unit with claims: span, counts by confidence band, map-only share, source families, longest gap, empty months
build/coverage_by_month.csv  one row per nationality x month: units active, units with a claim, claim rows, map-only share
build/review_queue.csv       units ranked by where reading another source would help most, with the period and suggested source types

Called by scripts/build.py (outputs()); pure functions so that scripts/semantic_tests.py can test them on synthetic rows.
"""
import csv
import datetime
import os

import common

MAP_FAMILY = 'loc_12ag_situation_maps'
GEOCODER = 'gazetteer_geocoder'
BANDS = [('conf_0_9', lambda c: c >= 0.9), ('conf_0_7', lambda c: 0.7 <= c < 0.9), ('conf_0_5', lambda c: 0.5 <= c < 0.7), ('conf_0_3_or_less', lambda c: c < 0.5)]
UNIT_HEADER = ['unit_id', 'unit_name', 'nationality', 'echelon', 'branch', 'first_claim_date', 'last_claim_date', 'span_days', 'claim_count',
               'conf_0_9', 'conf_0_7', 'conf_0_5', 'conf_0_3_or_less', 'map_only_rows', 'map_only_share', 'source_families', 'source_family_list',
               'longest_gap_days', 'longest_gap_from', 'longest_gap_to', 'empty_months', 'empty_month_list']
MONTH_HEADER = ['nationality', 'month', 'units_active', 'units_with_claim', 'units_without_claim', 'claim_rows', 'map_only_rows', 'map_only_share']
QUEUE_HEADER = ['rank', 'score', 'unit_id', 'unit_name', 'nationality', 'echelon', 'read_from', 'read_to', 'reason', 'suggested_sources',
                'gap_score', 'map_score', 'low_conf_score', 'single_family_score', 'empty_month_score']
# ranking weights (docs/coverage_report.md, "Ranking")
WEIGHTS = {'gap': 0.30, 'map': 0.25, 'low_conf': 0.15, 'single_family': 0.15, 'empty_month': 0.15}
GAP_SATURATION_DAYS = 90
SUGGEST = {
    'Germany': 'FMS manuscripts (Foreign Military Studies, B- and A-series) for the formation or its corps/army; Lexikon der Wehrmacht/Tessin; Allied G-2 periodic reports',
    'US': 'CMH US Army in World War II volumes (Green Books) for the campaign; CMH combat chronicles and ETO order of battle; unit after-action reports',
    'UK': 'Ellis, Victory in the West (UK official history); Joslen, Orders of Battle; divisional histories and war diaries',
    'Canada': 'Stacey, The Victory Campaign (Canadian official history); CMHQ/AHQ reports; war diaries',
    'France': 'de Lattre, Histoire de la Première Armée française; French official histories (SHD); CMH Riviera to the Rhine',
    'Poland': 'Polish 1st Armoured Division history; Stacey and Ellis for the operations it took part in',
}
DEFAULT_SUGGEST = 'official histories of the army it served under (CMH, Ellis, Stacey); unit histories'


def ref_families(meta_rows):
    """reference_id -> source_family, leaving out gazetteer/geocoder references (they place a point, not the unit)."""
    return {r['reference_id']: r['source_family'] for r in meta_rows if r['source_type'] != GEOCODER}


def _d(s):
    return datetime.date.fromisoformat(s)


def _months(a, b):
    out, y, m = [], a.year, a.month
    while (y, m) <= (b.year, b.month):
        out.append('%04d-%02d' % (y, m))
        y, m = (y + 1, 1) if m == 12 else (y, m + 1)
    return out


def row_families(claim, fam):
    return sorted({fam[x] for x in claim['reference_ids'].split(';') if x in fam})


def is_map_only(claim, fam):
    f = row_families(claim, fam)
    return f == [MAP_FAMILY]


def by_unit(units, claims, fam):
    """units: list of unit dicts; claims: list of claim dicts; fam: ref -> family. Returns list of dict rows (UNIT_HEADER)."""
    per = {}
    for c in claims:
        per.setdefault(c['unit_id'], []).append(c)
    out = []
    for u in units:
        cs = per.get(u['unit_id'])
        if not cs:
            continue
        dates = sorted({_d(c['date']) for c in cs})
        row = {k: u[k] for k in ('unit_id', 'unit_name', 'nationality', 'echelon', 'branch')}
        row['first_claim_date'], row['last_claim_date'] = dates[0].isoformat(), dates[-1].isoformat()
        row['span_days'] = (dates[-1] - dates[0]).days
        row['claim_count'] = len(cs)
        for name, test in BANDS:
            row[name] = sum(1 for c in cs if test(float(c['confidence'])))
        mo = sum(1 for c in cs if is_map_only(c, fam))
        row['map_only_rows'], row['map_only_share'] = mo, '%.3f' % (mo / len(cs))
        fams = sorted({f for c in cs for f in row_families(c, fam)})
        row['source_families'], row['source_family_list'] = len(fams), ';'.join(fams)
        best = (0, '', '')
        for a, b in zip(dates, dates[1:]):
            g = (b - a).days
            if g > best[0]:
                best = (g, a.isoformat(), b.isoformat())
        row['longest_gap_days'], row['longest_gap_from'], row['longest_gap_to'] = best
        have = {d.strftime('%Y-%m') for d in dates}
        empty = [m for m in _months(dates[0], dates[-1]) if m not in have]
        row['empty_months'], row['empty_month_list'] = len(empty), ';'.join(empty)
        out.append(row)
    return out


def by_month(unit_rows, claims, fam):
    """Per nationality and month: units whose first..last claim span covers the month, how many have a claim in it, map-only share."""
    if not claims:
        return []
    allm = _months(min(_d(c['date']) for c in claims), max(_d(c['date']) for c in claims))
    nat_of = {r['unit_id']: r['nationality'] for r in unit_rows}
    cell = {}
    for c in claims:
        k = (nat_of.get(c['unit_id'], c['nationality']), c['date'][:7])
        e = cell.setdefault(k, [set(), 0, 0])
        e[0].add(c['unit_id'])
        e[1] += 1
        e[2] += is_map_only(c, fam)
    out = []
    for nat in sorted({r['nationality'] for r in unit_rows}):
        for m in allm:
            active = sum(1 for r in unit_rows if r['nationality'] == nat and r['first_claim_date'][:7] <= m <= r['last_claim_date'][:7])
            if not active:
                continue
            units_with, rows_n, mo = cell.get((nat, m), [set(), 0, 0])
            out.append({'nationality': nat, 'month': m, 'units_active': active, 'units_with_claim': len(units_with),
                        'units_without_claim': active - len(units_with), 'claim_rows': rows_n, 'map_only_rows': mo,
                        'map_only_share': '%.3f' % (mo / rows_n) if rows_n else ''})
    return out


def queue(unit_rows):
    """Rank units for further reading. Each factor is scaled to 0..1 and weighted (WEIGHTS); ties by unit_id."""
    out = []
    for r in unit_rows:
        n = r['claim_count']
        months = max(1, len(_months(_d(r['first_claim_date']), _d(r['last_claim_date']))))
        f = {'gap': min(r['longest_gap_days'] / GAP_SATURATION_DAYS, 1.0),
             'map': float(r['map_only_share']),
             'low_conf': r['conf_0_3_or_less'] / n,
             'single_family': 1.0 if r['source_families'] <= 1 else 0.0,
             'empty_month': r['empty_months'] / months}
        score = sum(WEIGHTS[k] * v for k, v in f.items())
        why = []
        if r['longest_gap_days'] >= 30:
            why.append('gap of %d days (%s to %s)' % (r['longest_gap_days'], r['longest_gap_from'], r['longest_gap_to']))
        if f['map'] >= 0.5:
            why.append('%d%% of rows from situation maps only' % round(100 * f['map']))
        if f['low_conf'] >= 0.5:
            why.append('%d%% of rows at confidence 0.3 or less' % round(100 * f['low_conf']))
        if f['single_family']:
            why.append('one source family (%s)' % (r['source_family_list'] or 'none'))
        if r['empty_months']:
            why.append('%d month(s) with no claim' % r['empty_months'])
        if r['longest_gap_days'] >= 30:
            rf, rt = r['longest_gap_from'], r['longest_gap_to']
        else:
            rf, rt = r['first_claim_date'], r['last_claim_date']
        out.append({'score': round(score, 4), 'unit_id': r['unit_id'], 'unit_name': r['unit_name'], 'nationality': r['nationality'],
                    'echelon': r['echelon'], 'read_from': rf, 'read_to': rt, 'reason': '; '.join(why) or 'no weak point',
                    'suggested_sources': SUGGEST.get(r['nationality'], DEFAULT_SUGGEST),
                    'gap_score': round(f['gap'], 3), 'map_score': round(f['map'], 3), 'low_conf_score': round(f['low_conf'], 3),
                    'single_family_score': f['single_family'], 'empty_month_score': round(f['empty_month'], 3)})
    out.sort(key=lambda q: (-q['score'], q['unit_id']))
    for i, q in enumerate(out, start=1):
        q['rank'] = i
    return out


def outputs(units, claims):
    with open(os.path.join(common.ROOT, 'data', 'references_meta.csv'), newline='', encoding='utf-8') as fh:
        fam = ref_families(list(csv.DictReader(fh)))
    ur = by_unit(units, claims, fam)
    tab = lambda h, rs: common.csv_bytes(h, [[r[c] for c in h] for r in rs])  # noqa: E731
    return {'coverage_by_unit.csv': tab(UNIT_HEADER, ur),
            'coverage_by_month.csv': tab(MONTH_HEADER, by_month(ur, claims, fam)),
            'review_queue.csv': tab(QUEUE_HEADER, queue(ur))}
