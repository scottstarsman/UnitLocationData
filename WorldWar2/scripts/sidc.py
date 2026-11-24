"""Military symbol identification codes (SIDCs) for units and claims (roadmap 410; Scott accepted the proposal on 23 November 2026, PR #134).

MIL-STD-2525D / APP-6D 20-digit numeric SIDC, derived, never entered (docs/symbol_codes_proposal.md):
  digits 1-2 version 10 (2525D), 3 context 0 (reality), 4 standard identity (from the side on the date, Allied viewpoint),
  5-6 symbol set, 7 status (0 present; 4 present/destroyed on a claim whose destroyed flag is true), 8 HQ/TF/dummy,
  9-10 echelon amplifier, 11-16 entity, 17-18 modifier 1, 19-20 modifier 2.
Tables: data/sidc_function_map.csv (rules, first matching `function` row wins; `addon` rows then apply to land units),
data/sidc_echelon_map.csv (amplifier per echelon value), data/sidc_codes.csv (the recorded code list: JMSML 2525D codes of
symbol sets 10, 30 and 35 with the milsymbol icon key). Side: scripts/allegiance.py (unit override, then nation row); a date after
the last row that covers the unit keeps that last side (question 3); a gap between rows stays without a side (standard identity 1 Unknown).

Used by scripts/build.py (sidc column of the claims outputs, build/unit_symbols.csv),
scripts/validate.py (check_sidc) and scripts/semantic_tests.py.
"""
import datetime
import os
import re

import allegiance
import common

FUNCTION_MAP = os.path.join(common.ROOT, 'data', 'sidc_function_map.csv')
ECHELON_MAP = os.path.join(common.ROOT, 'data', 'sidc_echelon_map.csv')
CODES = os.path.join(common.ROOT, 'data', 'sidc_codes.csv')
VERSION = '10'      # MIL-STD-2525D base version (question 15)
CONTEXT = '0'       # reality
SEA_SETS = ('30', '35')
FALLTHROUGH_RULE = 'GZ99'
# question 1 (Allied viewpoint) and question 4 (co-belligerents Friend); no side = 1 Unknown
IDENTITY = {'Allied': '3', 'co-belligerent': '3', 'Axis': '6', 'neutral': '4', 'non-aligned-belligerent': '4', None: '1'}
UNIT_SYMBOLS_HEADER = ['unit_id', 'unit_name', 'nationality', 'domain', 'echelon', 'valid_from', 'valid_to', 'side', 'standard_identity',
                       'sidc', 'function_rule', 'entity_label']
SIDC_RE = re.compile(r'\d{20}')


def _d(s):
    return allegiance._date(s)


class Coder:
    def __init__(self):
        self.rules = common.read_dicts(FUNCTION_MAP)[1]
        self.functions = [r for r in self.rules if r['kind'] == 'function']
        self.addons = [r for r in self.rules if r['kind'] == 'addon']
        self.echelon = {r['echelon']: r['amplifier'] for r in common.read_dicts(ECHELON_MAP)[1]}
        self.codes = {(r['symbol_set'], r['kind'], r['code']): r for r in common.read_dicts(CODES)[1]}
        self.res = allegiance.Resolver.load()
        self._fn = {}

    # ---- function (date-independent digits) ----
    @staticmethod
    def _match(r, u):
        if r['domain'] and r['domain'] != common.unit_domain(u):
            return False
        if r['echelon'] and r['echelon'] != u['echelon']:
            return False
        if r['ship_type'] and r['ship_type'] != u.get('ship_type', ''):
            return False
        if r['name_pattern'] and not re.search(r['name_pattern'], u['unit_name'], re.I):
            return False
        return True

    def function(self, u):
        """{rule_id, symbol_set, hq, amplifier, entity, modifier1, modifier2, entity_label, addons} for a unit row (dict with unit_id, unit_name,
        echelon, domain, ship_type); None when no rule matches (cannot happen while GZ99 has no condition)."""
        key = u['unit_id']
        if key in self._fn and u is self._fn[key][0]:
            return self._fn[key][1]
        f = next((r for r in self.functions if self._match(r, u)), None)
        if f is None:
            return None
        out = {'rule_id': f['rule_id'], 'symbol_set': f['symbol_set'], 'entity': f['entity'], 'modifier1': f['modifier1'],
               'modifier2': f['modifier2'], 'hq': f['hq_tf_dummy'] or '0', 'entity_label': f['entity_label'], 'addons': []}
        if common.unit_domain(u) == 'ground' and out['symbol_set'] == '10':
            for a in self.addons:
                if not self._match(a, u):
                    continue
                if a['modifier2'] and not out['modifier2']:
                    out['modifier2'] = a['modifier2']
                    out['addons'].append(a['rule_id'])
                if a['hq_tf_dummy'] == '4':
                    out['hq'] = '6' if out['hq'] == '2' else '4'
                    out['addons'].append(a['rule_id'])
        if out['symbol_set'] in SEA_SETS:
            out['amplifier'] = '00'
        else:
            out['amplifier'] = f['amplifier_override'] or self.echelon.get(u['echelon'], '')
        self._fn[key] = (u, out)
        return out

    # ---- side and standard identity (digit 4) ----
    def _rows_for(self, u):
        """Allegiance rows that apply to the unit: its overrides, then its nation's WW2 rows (as (from, to, side, kind))."""
        out = []
        for r in self.res.over.get(u['unit_id'], []):
            out.append((_d(r['valid_from']), _d(r['valid_to']) if r['valid_to'] else None, r['side'], 'override'))
        code = self.res.code.get(u['nationality'])
        for r in self.res.nation_rows:
            if r['nation'] == code and r['conflict'] == 'WW2':
                out.append((_d(r['valid_from']), _d(r['valid_to']) if r['valid_to'] else None, r['side'], 'nation'))
        return out

    def side(self, u, date):
        """Side of the unit on the date: override, then nation row; after the last row that applies, the last row's side (question 3); None in a gap."""
        d = _d(date) if isinstance(date, str) else date
        if d is None:
            return None
        rows = self._rows_for(u)
        for f, t, s, kind in rows:
            if kind == 'override' and f <= d and (t is None or d <= t):
                return s
        for f, t, s, kind in rows:
            if kind == 'nation' and f <= d and (t is None or d <= t):
                return s
        ends = [(t, s) for f, t, s, _k in rows if t is not None]
        if rows and all(t is not None for f, t, s, _k in rows):
            last_t, last_s = max(ends, key=lambda x: x[0])
            if d > last_t:
                return last_s
        return None

    # ---- the code ----
    def sidc(self, u, date, destroyed=False):
        f = self.function(u)
        if f is None or not f['amplifier']:
            return ''
        return (VERSION + CONTEXT + IDENTITY[self.side(u, date)] + f['symbol_set'] + ('4' if destroyed else '0') + f['hq'] + f['amplifier'] +
                f['entity'] + (f['modifier1'] or '00') + (f['modifier2'] or '00'))

    def claim_sidc(self, u, claim):
        return self.sidc(u, claim['date'], claim.get('destroyed') == 'true')

    def periods(self, u):
        """[(valid_from, valid_to, side)] for the unit, from the start of the first applicable row; consecutive days with the same side are merged;
        the last period is open-ended (valid_to blank) because a later date keeps the last side; a gap between rows is a period with side None."""
        rows = sorted(self._rows_for(u), key=lambda x: x[0])
        if not rows:
            return [('', '', None)]
        cuts = sorted({f for f, t, s, k in rows} | {t + datetime.timedelta(days=1) for f, t, s, k in rows if t})
        out = []
        for i, start in enumerate(cuts):
            s = self.side(u, start)
            end = cuts[i + 1] - datetime.timedelta(days=1) if i + 1 < len(cuts) else None
            if out and out[-1][2] == s:
                out[-1][1] = end
            else:
                out.append([start, end, s])
        return [(a.isoformat(), b.isoformat() if b else '', s) for a, b, s in out]

    def unit_rows(self, units):
        rows = []
        for u in units:
            f = self.function(u)
            for a, b, s in self.periods(u):
                rows.append([u['unit_id'], u['unit_name'], u['nationality'], common.unit_domain(u), u['echelon'], a, b, s or '', IDENTITY[s],
                             self.sidc(u, a) if a else '', f['rule_id'] if f else '', f['entity_label'] if f else ''])
        return rows


def check(units, claims):
    """(errors, warnings): lists of (where, message) for the maps, the code list and the computed codes (scripts/validate.py check_sidc)."""
    errs, warns = [], []
    c = Coder()
    vocab = common.load_vocabularies()
    for name, path in (('sidc_function_map', FUNCTION_MAP), ('sidc_echelon_map', ECHELON_MAP), ('sidc_codes', CODES)):
        want = [f['name'] for f in common.load_schema(name)['fields']]
        have = common.read_rows(path)[0]
        if have != want:
            errs.append(('data/%s.csv' % name, 'header %s != schema/%s.schema.json %s' % (have, name, want)))
    ids = [r['rule_id'] for r in c.rules]
    if len(set(ids)) != len(ids):
        errs.append(('data/sidc_function_map.csv', 'duplicate rule_id'))
    if not c.functions or c.functions[-1]['rule_id'] != FALLTHROUGH_RULE or any(c.functions[-1][k] for k in ('domain', 'echelon', 'ship_type', 'name_pattern')):
        errs.append(('data/sidc_function_map.csv', 'the last function rule must be %s with no condition' % FALLTHROUGH_RULE))
    for r in c.rules:
        w = 'data/sidc_function_map.csv rule %s' % r['rule_id']
        if r['kind'] not in ('function', 'addon'):
            errs.append((w, 'kind %r is not function or addon' % r['kind']))
        try:
            re.compile(r['name_pattern'])
        except re.error as e:
            errs.append((w, 'name_pattern does not compile: %s' % e))
        if r['echelon'] and r['echelon'] not in vocab['echelon']['values']:
            errs.append((w, 'echelon %r not in vocabulary echelon' % r['echelon']))
        if r['domain'] and r['domain'] not in ('ground', 'air', 'naval'):
            errs.append((w, 'domain %r is not ground, air or naval' % r['domain']))
        if r['hq_tf_dummy'] not in ('', '0', '2', '4', '6'):
            errs.append((w, 'hq_tf_dummy %r is not 0, 2, 4 or 6' % r['hq_tf_dummy']))
        if r['amplifier_override'] and not re.fullmatch(r'\d\d', r['amplifier_override']):
            errs.append((w, 'amplifier_override %r is not two digits' % r['amplifier_override']))
        ss = r['symbol_set'] if r['kind'] == 'function' else '10'
        if r['kind'] == 'function' and (ss, 'entity', r['entity']) not in c.codes:
            errs.append((w, 'entity %s is not a code of symbol set %s in data/sidc_codes.csv' % (r['entity'], ss)))
        for k in ('modifier1', 'modifier2'):
            if r[k] and (ss, k, r[k]) not in c.codes:
                errs.append((w, '%s %s is not a code of symbol set %s in data/sidc_codes.csv' % (k, r[k], ss)))
    for e in vocab['echelon']['values']:
        if e not in c.echelon:
            errs.append(('data/sidc_echelon_map.csv', 'echelon %s has no amplifier row' % e))
    for e, a in c.echelon.items():
        if not re.fullmatch(r'\d\d', a):
            errs.append(('data/sidc_echelon_map.csv', 'echelon %s: amplifier %r is not two digits' % (e, a)))
    for u in units.values():
        f = c.function(u)
        if f is None:
            errs.append(('data/units.csv %s' % u['unit_id'], 'no rule of data/sidc_function_map.csv matches'))
            continue
        if f['rule_id'] == FALLTHROUGH_RULE:
            warns.append(('data/units.csv %s' % u['unit_id'], 'military symbol falls through to %s (unspecified land unit); add a rule to data/sidc_function_map.csv' % FALLTHROUGH_RULE))
        for a, b, s in c.periods(u):
            code = c.sidc(u, a) if a else ''
            if not SIDC_RE.fullmatch(code):
                errs.append(('data/units.csv %s' % u['unit_id'], 'derived SIDC %r is not 20 digits' % code))
    for r in claims:
        u = units.get(r['unit_id'])
        if u is None:
            continue
        if c.side(u, r['date']) is None:
            warns.append(('claim %s' % r['claim_id'], 'no side on %s for %s (%s): the military symbol shows standard identity Unknown; check data/nation_allegiance.csv or data/unit_allegiance_overrides.csv' % (r['date'], r['unit_id'], u['nationality'])))
    return errs, warns
