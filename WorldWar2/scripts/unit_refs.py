"""Unit references in the claim columns engaged_with and composing_units (recommendation F3). Standard library only.

Stored in the claim files (see schema/README.md, "unit references in claims"):
  engaged_with      `;` list of unit_ids of the opponents fought that day (foreign key to units.unit_id), or the sentinel `unknown`; blank = no combat
  engaged_note      free text for opponents that are not a unit of units.csv (an air force, naval forces, an unnamed formation); `;` list, a `;` inside
                    parentheses does not split. Never repeats the name of a unit that has an id.
  composing_units   `;` list of unit_ids of the subordinate units, or `unknown`; blank = unchanged from the unit's previous row
  composing_text    free text for what is not a unit of units.csv (regiments, battalions, companies, groups, remarks); `;` list as above. An entry of the
                    form `<unit_id> (<qualifier>)` is the qualifier of a unit listed in composing_units ('GER-PZ-002D (elements)'). The word "attach" in any form is
                    forbidden: how a unit is joined to another belongs in data/command_relations.csv (docs/deferred_relations.md for a formation that is not a unit).
Derived, never stored (carried to build/all_claims.csv and returned by load_all_claims):
  engaged_with_names     the unit display names ('German 12th SS Panzer Division Hitlerjugend', see common.display_name) followed by the notes
  composing_units_names  the unit names (the unit_name when the unit has the claiming unit's nationality, else the display name) with their
                         qualifiers, followed by the other text
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common  # noqa: E402

SENTINEL = 'unknown'
DERIVED = ['engaged_with_names', 'composing_units_names']
QUALIFIED = re.compile(r'^([A-Z0-9]+(?:-[A-Z0-9]+)+) (\(.*\))$')
# The word "attach" in any form (attach, attached, attaches, attaching, attachment, attachments; whole word, any case, also after a hyphen) may not appear in
# composing_text (entries and qualifiers) or engaged_note: an attachment is a command relationship (data/command_relations.csv, or docs/deferred_relations.md
# when the subordinate formation is not a unit of the table). "detached" is a different word and is not caught.
BANNED = re.compile(r'\battach(?:ed|es|ing|ments?)?\b', re.I)
_cache = {}


def split_list(s):
    """Split a `;` list; a `;` inside parentheses does not split. Entries are stripped, blanks dropped."""
    out, depth, cur = [], 0, ''
    for ch in s or '':
        if ch == '(':
            depth += 1
        elif ch == ')':
            depth = max(0, depth - 1)
        if ch == ';' and depth == 0:
            out.append(cur.strip())
            cur = ''
        else:
            cur += ch
    out.append(cur.strip())
    return [e for e in out if e]


def split_ids(s):
    """Split a plain id list (no parentheses expected)."""
    return [t.strip() for t in (s or '').split(';') if t.strip()]


def load_units():
    if 'units' not in _cache or _cache.get('path') != common.UNITS_CSV:
        _cache['units'] = {u['unit_id']: u for u in common.read_dicts(common.UNITS_CSV)[1]}
        _cache['path'] = common.UNITS_CSV
        _cache.pop('index', None)
    return _cache['units']


def reset():
    _cache.clear()


def adjective_nations():
    out = {}
    for n in common.load_nationalities():
        for a in common.adjectives(n):
            out[a] = n['name']
    return out


def _forms(u):
    n = u['unit_name']
    return {n, re.sub(r'\s*\([^)]*\)$', '', n)}


def index():
    """{(nationality, name form): [unit_id]} over every unit."""
    units = load_units()
    if 'index' not in _cache:
        idx = {}
        for uid, u in units.items():
            for f in _forms(u):
                idx.setdefault((u['nationality'], f), []).append(uid)
        _cache['index'] = idx
    return _cache['index']


def trailing_paren(s):
    """(text before, '(...)') for a string that ends in a balanced parenthesis group preceded by other text; else (s, '')."""
    s = s.strip()
    if not s.endswith(')'):
        return s, ''
    depth = 0
    for i in range(len(s) - 1, -1, -1):
        if s[i] == ')':
            depth += 1
        elif s[i] == '(':
            depth -= 1
            if depth == 0:
                return (s[:i].strip(), s[i:]) if s[:i].strip() else (s, '')
    return s, ''


def resolve_name(base, claimer_nationality='', claimer_name=''):
    """unit_ids whose name is exactly `base`: with an explicit adjective ('US 82nd Airborne Division') in that nation; else in the claiming
    unit's nation (also `<base>, <claiming unit name>` for combat commands); else, as a last resort, when the name is unique across all nations.
    More than one id = ambiguous; none = not a unit of units.csv."""
    idx = index()
    adj = adjective_nations()
    for a in sorted(adj, key=len, reverse=True):
        if base.startswith(a + ' '):
            r = idx.get((adj[a], base[len(a) + 1:])) or idx.get((adj[a], base))
            if r:
                return list(r)
    if claimer_nationality:
        r = idx.get((claimer_nationality, base))
        if r:
            return list(r)
        if claimer_name:
            r = idx.get((claimer_nationality, base + ', ' + claimer_name)) or idx.get((claimer_nationality, base + ', ' + re.sub(r'^\w+ ', '', claimer_name)))
            if r:
                return list(r)
    out = []
    for (_n, f), v in idx.items():
        if f == base:
            out.extend(v)
    return list(dict.fromkeys(out))


def unit_name_for(uid, claimer_nationality=None):
    u = load_units().get(uid)
    if not u:
        return uid
    if claimer_nationality is not None and u['nationality'] == claimer_nationality:
        return u['unit_name']
    return common.display_name(u['unit_name'], u['nationality'])


def engaged_names(row):
    v = row.get('engaged_with', '')
    parts = [v] if v == SENTINEL else [unit_name_for(t) for t in split_ids(v)]
    return '; '.join(parts + split_list(row.get('engaged_note', '')))


def composing_names(row, claimer_nationality):
    v = row.get('composing_units', '')
    texts = split_list(row.get('composing_text', ''))
    quals = {}
    free = []
    for t in texts:
        m = QUALIFIED.match(t)
        if m:
            quals.setdefault(m.group(1), []).append(m.group(2))
        else:
            free.append(t)
    if v == SENTINEL:
        return SENTINEL
    parts = []
    for uid in split_ids(v):
        n = unit_name_for(uid, claimer_nationality)
        parts.append(' '.join([n] + quals.get(uid, [])))
    return '; '.join(parts + free)


def attach(rows):
    """Add engaged_with_names and composing_units_names to every claim dict (needs the claim's unit nationality, looked up in units.csv)."""
    units = load_units()
    for r in rows:
        u = units.get(r.get('unit_id', ''))
        r['engaged_with_names'] = engaged_names(r)
        r['composing_units_names'] = composing_names(r, u['nationality'] if u else '')
    return rows


def embedded_ids(text):
    """Tokens in free text that look like unit ids (a nationality code, then one or more -SEGMENTS)."""
    codes = '|'.join(re.escape(n['code']) for n in common.load_nationalities())
    return re.findall(r'(?<![A-Za-z0-9-])((?:%s)(?:-[A-Z0-9]+)+)(?![A-Za-z0-9-])' % codes, text)


def _name_clash(entry, nat, name):
    """unit_ids when a free-text entry is exactly the name of exactly one unit (so it should be an id); [] otherwise (also when ambiguous)."""
    for cand in (entry, trailing_paren(entry)[0]):
        r = resolve_name(cand, nat, name)
        if len(r) == 1:
            return r
    return []


def check(row):
    """(errors, warnings) for the four unit-reference columns of one claim dict (engaged_with, engaged_note, composing_units, composing_text)."""
    errs, warns = [], []
    units = load_units()
    me = units.get(row.get('unit_id', ''))
    nat = me['nationality'] if me else ''
    nname = me['unit_name'] if me else ''
    alliances = {n['name']: n['alliance'] for n in common.load_nationalities()}

    def canonical(col, entries):
        if row[col] != '; '.join(entries):
            errs.append('%s must be entries joined by "; " with no stray spaces or empty entries: %r' % (col, row[col]))

    def free(col, e, claimer_nat, claimer_name):
        for t in embedded_ids(e):
            if t not in units:
                errs.append('%s entry %r contains %s, which is not a unit_id in data/units.csv' % (col, e, t))
            elif col == 'engaged_note':
                errs.append('%s entry %r contains the unit id %s: list the opponent in engaged_with' % (col, e, t))
            elif col == 'composing_text':
                errs.append('%s entry %r contains the unit id %s inside free text: write "%s (qualifier)" and list the id in composing_units' % (col, e, t, t))
        r = _name_clash(e, claimer_nat, claimer_name)
        if r:
            errs.append('%s entry %r is the name of unit %s: use the id in %s' % (col, e, r[0], 'engaged_with' if col == 'engaged_note' else 'composing_units'))

    def banned(col, e):
        m = BANNED.search(e)
        if m:
            errs.append('%s entry %r uses the word %r: a relationship (attachment) belongs in data/command_relations.csv, or in docs/deferred_relations.md when the formation is not a unit of the table; '
                        'name the unit or the formation without relationship wording' % (col, e, m.group(0)))

    # engaged_with / engaged_note
    ew, note = row.get('engaged_with', ''), row.get('engaged_note', '')
    notes = split_list(note)
    if note:
        canonical('engaged_note', notes)
    for e in notes:
        banned('engaged_note', e)
        free('engaged_note', e, '', '')
    if ew == SENTINEL:
        if note:
            errs.append('engaged_with is unknown but engaged_note names opponents (%r)' % note)
        n_opp = 1
    else:
        ids = split_ids(ew)
        if ew:
            canonical('engaged_with', ids)
        if len(set(ids)) != len(ids):
            errs.append('engaged_with lists a unit twice: %r' % ew)
        for uid in ids:
            if uid == SENTINEL:
                errs.append('engaged_with: "unknown" cannot be mixed with unit ids')
            elif uid == row.get('unit_id'):
                errs.append('engaged_with lists the claiming unit itself (%s)' % uid)
            elif uid in units and me:
                a, b = alliances.get(me['nationality'], ''), alliances.get(units[uid]['nationality'], '')
                if a and a == b:
                    errs.append('engaged_with %s (%s) is on the same side as the claiming unit (%s)' % (uid, units[uid]['nationality'], me['nationality']))
        n_opp = len(ids) + len(notes)
    if n_opp > 3:
        warns.append('engaged_with and engaged_note list more than three opponents: check that they were fought in one action')

    # composing_units / composing_text
    cu, text = row.get('composing_units', ''), row.get('composing_text', '')
    texts = split_list(text)
    if text:
        canonical('composing_text', texts)
    ids = [] if cu == SENTINEL else split_ids(cu)
    if cu and cu != SENTINEL:
        canonical('composing_units', ids)
    if cu == SENTINEL and text:
        errs.append('composing_units is unknown but composing_text is not blank (%r)' % text)
    if len(set(ids)) != len(ids):
        errs.append('composing_units lists a unit twice: %r' % cu)
    for uid in ids:
        if uid == SENTINEL:
            errs.append('composing_units: "unknown" cannot be mixed with unit ids')
        elif uid == row.get('unit_id'):
            errs.append('composing_units lists the claiming unit itself (%s)' % uid)
    for t in texts:
        banned('composing_text', t)
        m = QUALIFIED.match(t)
        if m:
            if m.group(1) not in ids:
                errs.append('composing_text entry %r qualifies %s, which is not in composing_units' % (t, m.group(1)))
            continue
        lead = re.match(r'^((?:%s)(?:-[A-Z0-9]+)+)(?![A-Za-z0-9-])' % '|'.join(re.escape(n['code']) for n in common.load_nationalities()), t)
        if lead:
            errs.append('composing_text entry %r starts with the unit id %s: write it as "%s (qualifier)" and list the id in composing_units' % (t, lead.group(1), lead.group(1)))
        free('composing_text', t, nat, nname)
    return errs, warns
