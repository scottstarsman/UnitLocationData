#!/usr/bin/env python3
"""TO&E templates and unit assignments (Task 3, TE1-TE16).

data/toe_templates.csv  official authorized tables (TT0001 onward)
data/unit_toe.csv       dated, sourced assignments of a unit to a template (UT0001 onward)

Authorized figures live on the template. They are never written onto claims.
"""
import json
import os
import re
from datetime import date, datetime

import common

TEMPLATES_CSV = os.path.join(common.ROOT, 'data', 'toe_templates.csv')
ASSIGNMENTS_CSV = os.path.join(common.ROOT, 'data', 'unit_toe.csv')
TEMPLATES_WHERE = 'data/toe_templates.csv'
ASSIGNMENTS_WHERE = 'data/unit_toe.csv'

TEMPLATE_RE = re.compile(r'^TT\d{4,}$')
ASSIGNMENT_RE = re.compile(r'^UT\d{4,}$')
DATE_RE = re.compile(r'^\d{4}-\d{2}-\d{2}$')
PARTIAL_DATE_RE = re.compile(r'^\d{4}(-\d{2})?(-\d{2})?$')
CONFIDENCE_VALUES = ('0.3', '0.5', '0.7', '0.9')

TEMPLATE_HEADER = [
    'template_id', 'template_name', 'nationality', 'domain', 'echelon', 'formation_type',
    'official_designation', 'edition_date', 'valid_from', 'valid_to', 'valid_to_basis',
    'parent_template_id', 'authorized_strength_json', 'structure_summary', 'reference_ids',
    'template_note',
]
ASSIGNMENT_HEADER = [
    'assignment_id', 'unit_id', 'template_id', 'valid_from', 'valid_from_basis',
    'valid_to', 'valid_to_basis', 'conformance', 'confidence', 'reference_ids', 'note',
]
BUILD_ASSIGNMENT_HEADER = ASSIGNMENT_HEADER + [
    'template_name', 'template_nationality', 'official_designation', 'formation_type',
    'authorized_personnel', 'authorized_strength_json',
]


def _load(path):
    if not os.path.isfile(path):
        return None, []
    return common.read_dicts(path)


def load_templates(path=TEMPLATES_CSV):
    return _load(path)


def load_assignments(path=ASSIGNMENTS_CSV):
    return _load(path)


def parse_ids(s):
    return [x.strip() for x in (s or '').split(';') if x.strip()]


def _date(s):
    s = (s or '').strip()
    if not s or not DATE_RE.match(s):
        return None
    try:
        return date.fromisoformat(s)
    except ValueError:
        return None


def _id_num(s, prefix):
    if not s or not s.startswith(prefix):
        return None
    try:
        return int(s[len(prefix):])
    except ValueError:
        return None


def personnel_of(template):
    """Authorized personnel total, or '' if the JSON has none."""
    cell = (template.get('authorized_strength_json') or '').strip()
    if not cell:
        return ''
    try:
        obj = json.loads(cell)
    except (TypeError, ValueError, json.JSONDecodeError):
        return ''
    if 'personnel' not in obj:
        return ''
    return str(obj['personnel'])


def covers(row, on_date):
    """True if the assignment or template interval covers YYYY-MM-DD (inclusive)."""
    if not on_date:
        return False
    frm, to = row.get('valid_from') or '', row.get('valid_to') or ''
    if frm and on_date < frm:
        return False
    if to and on_date > to:
        return False
    return True


def assignment_on(assignments_by_unit, uid, on_date):
    """The unique assignment covering on_date, or None. If more than one covers, return the list as a conflict."""
    hits = [a for a in (assignments_by_unit.get(uid) or []) if covers(a, on_date)]
    if not hits:
        return None, []
    if len(hits) > 1:
        return None, hits
    return hits[0], []


def derived_templates(templates):
    """Rows of build/toe_templates.csv: a copy of the data table, in file order (already sorted by id)."""
    return [[t.get(c, '') or '' for c in TEMPLATE_HEADER] for t in templates]


def derived_assignments(assignments, templates):
    """Rows of build/unit_toe.csv, with template fields joined on."""
    by_t = {t['template_id']: t for t in templates}
    out = []
    for a in assignments:
        t = by_t.get(a['template_id'], {})
        row = [a.get(c, '') or '' for c in ASSIGNMENT_HEADER]
        row.extend([
            t.get('template_name') or '',
            t.get('nationality') or '',
            t.get('official_designation') or '',
            t.get('formation_type') or '',
            personnel_of(t),
            t.get('authorized_strength_json') or '',
        ])
        out.append(row)
    return out


def build_outputs(templates=None, assignments=None):
    """{path relative to build/: bytes}."""
    if templates is None:
        templates = load_templates()[1] or []
    if assignments is None:
        assignments = load_assignments()[1] or []
    return {
        'toe_templates.csv': common.csv_bytes(TEMPLATE_HEADER, derived_templates(templates)),
        'unit_toe.csv': common.csv_bytes(BUILD_ASSIGNMENT_HEADER, derived_assignments(assignments, templates)),
    }


def _intervals_overlap(a, b):
    a0, a1 = _date(a.get('valid_from')), _date(a.get('valid_to'))
    b0, b1 = _date(b.get('valid_from')), _date(b.get('valid_to'))
    if a0 is None or b0 is None:
        return False
    a_end = a1 or date(9999, 12, 31)
    b_end = b1 or date(9999, 12, 31)
    return a0 <= b_end and b0 <= a_end


def check(templates_h, templates, assignments_h, assignments, units, vocabs, ref_ids, nat_names):
    """Return a list of (where, message) problems."""
    out = []
    if templates_h is None:
        out.append((TEMPLATES_WHERE, 'missing'))
        return out
    if templates_h != TEMPLATE_HEADER:
        out.append((TEMPLATES_WHERE, 'header %s != schema/toe_templates.schema.json %s' % (templates_h, TEMPLATE_HEADER)))
        return out
    if assignments_h is None:
        out.append((ASSIGNMENTS_WHERE, 'missing'))
        return out
    if assignments_h != ASSIGNMENT_HEADER:
        out.append((ASSIGNMENTS_WHERE, 'header %s != schema/unit_toe.schema.json %s' % (assignments_h, ASSIGNMENT_HEADER)))
        return out

    domains = vocabs['domain']['values']
    echelons = vocabs['echelon']['values']
    formation_types = vocabs['formation_type']['values']
    end_bases = vocabs['relation_end_basis']['values']
    start_bases = vocabs['relation_start_basis']['values']
    conformances = vocabs['toe_conformance']['values']
    count_keys = vocabs['authorized_count_key']['values']
    structure_keys = vocabs['authorized_structure_key']['values']

    # ---- templates ----
    seen_t, t_ids, by_t = set(), [], {}
    names_by_nat = {}
    for i, t in enumerate(templates, start=2):
        w = '%s line %d' % (TEMPLATES_WHERE, i)
        tid = t.get('template_id', '')
        if not TEMPLATE_RE.fullmatch(tid):
            out.append((w, 'template_id %r does not match TT0001' % tid))
        if tid in seen_t:
            out.append((w, 'duplicate template_id %s' % tid))
        seen_t.add(tid)
        t_ids.append(tid)
        by_t[tid] = t
        if not (t.get('template_name') or '').strip():
            out.append((w, 'template_name is blank'))
        nat = (t.get('nationality') or '').strip()
        if nat not in nat_names:
            out.append((w, 'nationality %r is not a name in data/nationalities.csv' % nat))
        key = (nat, (t.get('template_name') or '').strip())
        if key in names_by_nat:
            out.append((w, 'template_name %r is used twice for nationality %s' % (key[1], nat)))
        names_by_nat[key] = tid
        if t.get('domain') not in domains:
            out.append((w, 'domain %r not in vocabulary domain' % t.get('domain')))
        if t.get('echelon') not in echelons:
            out.append((w, 'echelon %r not in vocabulary echelon' % t.get('echelon')))
        if t.get('formation_type') not in formation_types:
            out.append((w, 'formation_type %r not in vocabulary formation_type' % t.get('formation_type')))
        if not (t.get('official_designation') or '').strip():
            out.append((w, 'official_designation is blank'))
        ed = (t.get('edition_date') or '').strip()
        if ed and not PARTIAL_DATE_RE.match(ed):
            out.append((w, 'edition_date %r is not YYYY, YYYY-MM or YYYY-MM-DD' % ed))
        vf, vt = _date(t.get('valid_from')), _date(t.get('valid_to'))
        if not t.get('valid_from') or vf is None:
            out.append((w, 'valid_from %r is not a real YYYY-MM-DD' % t.get('valid_from')))
        if t.get('valid_to') and vt is None:
            out.append((w, 'valid_to %r is not a real YYYY-MM-DD' % t.get('valid_to')))
        if vf and vt and vt < vf:
            out.append((w, 'valid_to %s is before valid_from %s' % (t.get('valid_to'), t.get('valid_from'))))
        if t.get('valid_to_basis') not in end_bases:
            out.append((w, 'valid_to_basis %r not in vocabulary relation_end_basis' % t.get('valid_to_basis')))
        if not (t.get('valid_to') or '').strip() and t.get('valid_to_basis') != 'open':
            out.append((w, 'blank valid_to requires valid_to_basis open'))
        if (t.get('valid_to') or '').strip() and t.get('valid_to_basis') == 'open':
            out.append((w, 'valid_to_basis open requires blank valid_to'))
        parent = (t.get('parent_template_id') or '').strip()
        if parent:
            if not TEMPLATE_RE.fullmatch(parent):
                out.append((w, 'parent_template_id %r does not match TT0001' % parent))
            elif parent == tid:
                out.append((w, 'parent_template_id must not be the row itself'))
        cell = (t.get('authorized_strength_json') or '').strip()
        if not cell:
            out.append((w, 'authorized_strength_json is blank'))
        else:
            try:
                obj = json.loads(cell)
            except (TypeError, ValueError, json.JSONDecodeError) as e:
                out.append((w, 'authorized_strength_json is not valid JSON: %s' % e))
                obj = None
            if isinstance(obj, dict):
                for k in obj:
                    if k not in ('personnel', 'counts', 'structure'):
                        out.append((w, 'authorized_strength_json has unknown key %r' % k))
                if 'personnel' in obj and (not isinstance(obj['personnel'], int) or obj['personnel'] < 0):
                    out.append((w, 'personnel must be an integer >= 0'))
                counts = obj.get('counts') or {}
                if counts and not isinstance(counts, dict):
                    out.append((w, 'counts must be an object'))
                else:
                    for k in counts:
                        if k not in count_keys:
                            out.append((w, 'counts key %r is not in vocabulary authorized_count_key' % k))
                structure = obj.get('structure') or {}
                if structure and not isinstance(structure, dict):
                    out.append((w, 'structure must be an object'))
                else:
                    for k in structure:
                        if k not in structure_keys:
                            out.append((w, 'structure key %r is not in vocabulary authorized_structure_key' % k))
        refs = parse_ids(t.get('reference_ids'))
        if not refs:
            out.append((w, 'reference_ids is blank'))
        for rid in refs:
            if rid not in ref_ids:
                out.append((w, 'reference_id %s is not in data/references_meta.csv' % rid))

    for i, t in enumerate(templates, start=2):
        parent = (t.get('parent_template_id') or '').strip()
        if parent and parent not in seen_t:
            out.append(('%s line %d' % (TEMPLATES_WHERE, i), 'parent_template_id %s is not a template in data/toe_templates.csv' % parent))
        if parent and parent in by_t and (by_t[parent].get('parent_template_id') or '').strip():
            out.append(('%s line %d' % (TEMPLATES_WHERE, i), 'parent_template_id %s is itself a variant; a parent is not a variant' % parent))

    if t_ids != sorted(t_ids, key=lambda x: int(x[2:]) if TEMPLATE_RE.fullmatch(x) else x):
        out.append((TEMPLATES_WHERE, 'rows must be sorted by template_id'))
    nums = [_id_num(x, 'TT') for x in t_ids]
    nums = [n for n in nums if n is not None]
    if nums:
        gaps = sorted(set(range(1, max(nums) + 1)) - set(nums))
        if gaps:
            out.append((TEMPLATES_WHERE, 'template id(s) below the highest are unused (ids are assigned without gaps): %s' %
                        (', '.join('TT%04d' % g for g in gaps[:20]) + (' ...' if len(gaps) > 20 else ''))))

    # ---- assignments ----
    seen_a, a_ids = set(), []
    by_unit = {}
    used_templates = set()
    for i, a in enumerate(assignments, start=2):
        w = '%s line %d' % (ASSIGNMENTS_WHERE, i)
        aid = a.get('assignment_id', '')
        if not ASSIGNMENT_RE.fullmatch(aid):
            out.append((w, 'assignment_id %r does not match UT0001' % aid))
        if aid in seen_a:
            out.append((w, 'duplicate assignment_id %s' % aid))
        seen_a.add(aid)
        a_ids.append(aid)
        uid, tid = a.get('unit_id', ''), a.get('template_id', '')
        if uid not in units:
            out.append((w, 'unit_id %r is not a unit of data/units.csv' % uid))
        if tid not in seen_t:
            out.append((w, 'template_id %r is not a template in data/toe_templates.csv' % tid))
        used_templates.add(tid)
        if a.get('valid_from_basis') not in start_bases:
            out.append((w, 'valid_from_basis %r not in vocabulary relation_start_basis' % a.get('valid_from_basis')))
        if a.get('valid_to_basis') not in end_bases:
            out.append((w, 'valid_to_basis %r not in vocabulary relation_end_basis' % a.get('valid_to_basis')))
        if a.get('valid_to_basis') == 'open_at_last_claim':
            out.append((w, 'valid_to_basis open_at_last_claim is for command relations; use open on unit_toe'))
        vf, vt = _date(a.get('valid_from')), _date(a.get('valid_to'))
        if not a.get('valid_from') or vf is None:
            out.append((w, 'valid_from %r is not a real YYYY-MM-DD' % a.get('valid_from')))
        if a.get('valid_to') and vt is None:
            out.append((w, 'valid_to %r is not a real YYYY-MM-DD' % a.get('valid_to')))
        if vf and vt and vt < vf:
            out.append((w, 'valid_to %s is before valid_from %s' % (a.get('valid_to'), a.get('valid_from'))))
        if not (a.get('valid_to') or '').strip() and a.get('valid_to_basis') != 'open':
            out.append((w, 'blank valid_to requires valid_to_basis open'))
        if (a.get('valid_to') or '').strip() and a.get('valid_to_basis') == 'open':
            out.append((w, 'valid_to_basis open requires blank valid_to'))
        if a.get('conformance') not in conformances:
            out.append((w, 'conformance %r not in vocabulary toe_conformance' % a.get('conformance')))
        if a.get('conformance') == 'modified' and not (a.get('note') or '').strip():
            out.append((w, 'conformance modified requires a note'))
        conf = (a.get('confidence') or '').strip()
        if conf not in CONFIDENCE_VALUES:
            out.append((w, 'confidence %r is not a usual tier (0.3, 0.5, 0.7, 0.9)' % a.get('confidence')))
        refs = parse_ids(a.get('reference_ids'))
        if not refs:
            out.append((w, 'reference_ids is blank'))
        for rid in refs:
            if rid not in ref_ids:
                out.append((w, 'reference_id %s is not in data/references_meta.csv' % rid))
        tmpl = by_t.get(tid)
        if tmpl and uid in units:
            ue, te = units[uid].get('echelon') or '', tmpl.get('echelon') or ''
            if ue and te and ue != te:
                out.append((w, 'WARNING unit echelon %s does not match template echelon %s' % (ue, te)))
            # nationality mismatch is allowed (Canadian unit on a British table) and is not an error
        if tmpl and vf:
            tf, tt = _date(tmpl.get('valid_from')), _date(tmpl.get('valid_to'))
            if tf and vf < tf:
                out.append((w, 'WARNING assignment begins %s before the template valid_from %s' % (a.get('valid_from'), tmpl.get('valid_from'))))
            if tt and vf and vf > tt and (not vt or _date(str(vt)) and vf > tt):
                # start after the template was superseded: unusual, warn
                out.append((w, 'WARNING assignment begins %s after the template valid_to %s' % (a.get('valid_from'), tmpl.get('valid_to'))))
        by_unit.setdefault(uid, []).append(a)

    for uid, rows in by_unit.items():
        for i, a in enumerate(rows):
            for b in rows[i + 1:]:
                if _intervals_overlap(a, b):
                    out.append((ASSIGNMENTS_WHERE, 'assignments %s and %s for unit %s have overlapping intervals' % (
                        a.get('assignment_id'), b.get('assignment_id'), uid)))

    if a_ids != sorted(a_ids, key=lambda x: int(x[2:]) if ASSIGNMENT_RE.fullmatch(x) else x):
        out.append((ASSIGNMENTS_WHERE, 'rows must be sorted by assignment_id'))
    nums = [_id_num(x, 'UT') for x in a_ids]
    nums = [n for n in nums if n is not None]
    if nums:
        gaps = sorted(set(range(1, max(nums) + 1)) - set(nums))
        if gaps:
            out.append((ASSIGNMENTS_WHERE, 'assignment id(s) below the highest are unused (ids are assigned without gaps): %s' %
                        (', '.join('UT%04d' % g for g in gaps[:20]) + (' ...' if len(gaps) > 20 else ''))))

    unused = sorted(seen_t - used_templates, key=lambda x: int(x[2:]) if TEMPLATE_RE.fullmatch(x) else x)
    # unused templates are allowed (a 1945 revision with no unit yet attached)

    return out


# So that a WARNING-prefixed message from check() can be routed as a warning, not an error.
WARNING_PREFIX = 'WARNING '
