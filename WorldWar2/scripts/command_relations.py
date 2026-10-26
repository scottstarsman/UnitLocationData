"""Command-relations tables: data/command_relations.csv (master) and data/command_relation_claims.csv (evidence join).

A command relation is one interval of one relationship between a subordinate unit and a higher unit (or an explicit
`unknown` placeholder with no higher unit). The claims no longer carry a `command_relationships` JSON cell: the master table holds
each interval once, the join table says which claim lists which relation and what that claim itself stated about the dates.
`entries(claim_id)` rebuilds the former per-claim entry list (in the canonical key order) so the validator, the audits and
build/all_claims.csv see exactly what the old column held. Library module (standard library only); see schema/README.md and
docs/methodology.md ("Command relations table").
"""
import json
import os

import common

REL_CSV = os.path.join(common.ROOT, 'data', 'command_relations.csv')
LINK_CSV = os.path.join(common.ROOT, 'data', 'command_relation_claims.csv')

OVERLAP_CSV = os.path.join(common.ROOT, 'data', 'command_relation_overlaps.csv')
OVERLAP_HEADER = ['relation_id_a', 'relation_id_b', 'overlap_from', 'overlap_to', 'kind', 'explanation']
STANDING_CLASS = ('assigned', 'unspecified_subordination')   # one standing parent class: a unit is assigned to one headquarters of an echelon at a time
FAR = '9999-12-31'

REL_HEADER = ['relation_id', 'subject_unit_id', 'higher_unit_id', 'relationship', 'valid_from', 'valid_from_latest', 'valid_from_time',
              'valid_from_basis', 'valid_to', 'valid_to_earliest', 'valid_to_time', 'valid_to_basis', 'end_unknown', 'change_undated',
              'date_basis', 'ordered_date', 'status', 'note']
# What a claim itself said about a relation (blank = the claim's entry had no such key); in the order of the canonical entry.
STATED = [('effective_from', 'stated_effective_from'), ('effective_from_latest', 'stated_effective_from_latest'),
          ('effective_time', 'stated_effective_time'), ('ordered_date', 'stated_ordered_date'), ('effective_to', 'stated_effective_to'),
          ('effective_to_earliest', 'stated_effective_to_earliest'), ('effective_to_time', 'stated_effective_to_time'),
          ('effective_to_basis', 'stated_effective_to_basis'), ('note', 'stated_note'), ('date_basis', 'stated_date_basis')]
LINK_HEADER = ['relation_id', 'claim_id', 'seq', 'role'] + [c for _k, c in STATED]
ROLES = ('asserts_start', 'asserts_end', 'asserts_start_and_end', 'observed_during')
# valid_to_basis / valid_from_basis values beyond the sourced ones of vocabulary relationship_date_basis
END_INFERRED = ('inferred_from_next_claim', 'open_at_last_claim')


def role_of(stated):
    """Role of a link from what the claim stated: dates it gave for the start and/or end, else it only observed the relation."""
    s, e = bool(stated.get('effective_from')), bool(stated.get('effective_to'))
    return 'asserts_start_and_end' if s and e else 'asserts_start' if s else 'asserts_end' if e else 'observed_during'


class Relations:
    def __init__(self, rows, links):
        self.rows, self.links = rows, links
        self.by_id = {r['relation_id']: r for r in rows}
        self.by_claim = {}
        for l in links:
            self.by_claim.setdefault(l['claim_id'], []).append(l)
        for v in self.by_claim.values():
            v.sort(key=lambda l: int(l['seq']))
        self.by_relation = {}
        for l in links:
            self.by_relation.setdefault(l['relation_id'], []).append(l)

    def entry(self, link):
        """The old-style command_relationships entry (dict, canonical key order) that `link` stands for."""
        rel = self.by_id[link['relation_id']]
        e = {'unit_id': rel['higher_unit_id'] or None, 'relationship': rel['relationship']}
        for key, col in STATED:
            if link[col] != '':
                e[key] = link[col]
        return e

    def entries(self, claim_id):
        return [self.entry(l) for l in self.by_claim.get(claim_id, []) if l['relation_id'] in self.by_id]

    def entries_json(self, claim_id):
        """The text the claims' command_relationships column used to hold: compact JSON, blank when the claim lists no relation."""
        es = self.entries(claim_id)
        return json.dumps(es, ensure_ascii=False, separators=(',', ':')) if es else ''


def contradictory_overlaps(rows, units):
    """Pairs of preferred relations of one subject that contradict each other on some days: same relationship class (assigned and unspecified_subordination
    count as one class; organic and unknown never conflict), different higher units of the SAME echelon (a unit is under one army, one corps, ... at a
    time; a higher unit of another echelon is the chain above or below, which is concurrent by design), and overlapping intervals (valid_to blank = open).
    Returns [(a, b, overlap_from, overlap_to)] with a['relation_id'] < b['relation_id'], overlap_to blank for an open overlap."""
    by = {}
    for r in rows:
        if r['status'] == 'preferred' and r['higher_unit_id'] and r['relationship'] not in ('organic', 'unknown'):
            by.setdefault(r['subject_unit_id'], []).append(r)
    out = []
    for uid in sorted(by):
        rs = sorted(by[uid], key=lambda r: r['relation_id'])
        for i, a in enumerate(rs):
            for b in rs[i + 1:]:
                cls = lambda r: 'standing' if r['relationship'] in STANDING_CLASS else r['relationship']
                if cls(a) != cls(b) or a['higher_unit_id'] == b['higher_unit_id']:
                    continue
                ea = (units.get(a['higher_unit_id']) or {}).get('echelon')
                if ea is None or ea != (units.get(b['higher_unit_id']) or {}).get('echelon'):
                    continue
                lo, hi = max(a['valid_from'], b['valid_from']), min(a['valid_to'] or FAR, b['valid_to'] or FAR)
                if lo <= hi:
                    out.append((a, b, lo, '' if hi == FAR else hi))
    return out


def overlap_explanation(a, b, lo, hi):
    return ('%s -> %s (%s, %s to %s, end %s) and %s -> %s (%s, %s to %s, start %s) are both listed on %s%s: the sources do not agree on the date of the change; '
            'nothing is resolved here' % (
                a['subject_unit_id'], a['higher_unit_id'], a['relationship'], a['valid_from'], a['valid_to'] or 'open', a['valid_to_basis'],
                b['subject_unit_id'], b['higher_unit_id'], b['relationship'], b['valid_from'], b['valid_to'] or 'open', b['valid_from_basis'],
                lo, (' to ' + hi) if hi and hi != lo else '' if hi else ' onward'))


def default_overlap_rows(rows, units):
    return [{'relation_id_a': a['relation_id'], 'relation_id_b': b['relation_id'], 'overlap_from': lo, 'overlap_to': hi,
             'kind': 'transfer_dates_differ', 'explanation': overlap_explanation(a, b, lo, hi)} for a, b, lo, hi in contradictory_overlaps(rows, units)]


_cache = {}


def load(force=False):
    """Load both tables (empty when the files do not exist yet, as during the migration)."""
    if force or 'rel' not in _cache:
        rows = common.read_dicts(REL_CSV)[1] if os.path.isfile(REL_CSV) else []
        links = common.read_dicts(LINK_CSV)[1] if os.path.isfile(LINK_CSV) else []
        _cache['rel'] = Relations(rows, links)
        _cache['rel'].overlaps = common.read_dicts(OVERLAP_CSV)[1] if os.path.isfile(OVERLAP_CSV) else []
    return _cache['rel']


def source_claim_ids(rel, rel_obj, claim_info):
    """Claim ids that list `rel` from preferred claims, oldest first (date, then claim id): the evidence shown in build/command_relations.csv."""
    ids = [l['claim_id'] for l in rel_obj.by_relation.get(rel['relation_id'], []) if claim_info.get(l['claim_id'], {}).get('claim_status', 'preferred') in ('preferred', '')]
    return sorted(set(ids), key=lambda c: (claim_info[c]['date'], c))


DERIVED_HEADER = ['relation_id', 'subject_unit_id', 'subject_name', 'higher_unit_id', 'higher_name', 'relationship', 'valid_from', 'valid_from_latest',
                  'valid_from_time', 'valid_from_basis', 'valid_to', 'valid_to_earliest', 'valid_to_time', 'valid_to_basis', 'support', 'ordered_date',
                  'source_claim_ids', 'note', 'end_unknown', 'change_undated']


def derived_rows(rel_obj, units, claim_rows):
    """Rows of build/command_relations.csv: every preferred relation of the master table except `organic` (a constituted component is not a
    command relationship to ask about), with names from units.csv and the evidence claim ids. Placeholders (no higher unit) are included with blank
    higher_* columns. support: documented (date_basis narrative/order), table (assignment_table), inferred (anything else)."""
    claim_info = {r['claim_id']: r for r in claim_rows}
    out = []
    for r in rel_obj.rows:
        if r['status'] != 'preferred' or r['relationship'] == 'organic':
            continue
        hu = units.get(r['higher_unit_id']) if r['higher_unit_id'] else None
        su = units[r['subject_unit_id']]
        sup = {'narrative': 'documented', 'order': 'documented', 'assignment_table': 'table'}.get(r['date_basis'], 'inferred')
        out.append([r['relation_id'], r['subject_unit_id'], su['unit_name'], r['higher_unit_id'],
                    common.display_name(hu['unit_name'], hu['nationality']) if hu else '', r['relationship'], r['valid_from'], r['valid_from_latest'],
                    r['valid_from_time'], r['valid_from_basis'], r['valid_to'], r['valid_to_earliest'], r['valid_to_time'], r['valid_to_basis'], sup,
                    r['ordered_date'], ' '.join(source_claim_ids(r, rel_obj, claim_info)), r['note'], r['end_unknown'], r['change_undated']])
    out.sort(key=lambda x: (x[1], x[6], x[3], x[5], x[0]))
    return out
