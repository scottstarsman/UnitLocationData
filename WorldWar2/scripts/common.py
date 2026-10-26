"""Shared helpers for the validation, build and split scripts (standard library only)."""
import csv
import functools
import io
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLAIMS_DIR = os.path.join(ROOT, 'data', 'claims')
UNITS_CSV = os.path.join(ROOT, 'data', 'units.csv')
NATIONALITIES_CSV = os.path.join(ROOT, 'data', 'nationalities.csv')
SCHEMA_DIR = os.path.join(ROOT, 'schema')
BUILD_DIR = os.path.join(ROOT, 'build')


def load_json(path):
    with open(path, encoding='utf-8') as f:
        return json.load(f)


def load_schema(name='claims'):
    return load_json(os.path.join(SCHEMA_DIR, name + '.schema.json'))


def load_vocabularies():
    return load_json(os.path.join(SCHEMA_DIR, 'vocabularies.json'))


def vocab_values(name):
    """The allowed values of one vocabulary of schema/vocabularies.json, in file order (the single source; do not copy lists into code)."""
    return list(load_vocabularies()[name]['values'])


def vocab_descriptions(name):
    """{value: description} of one vocabulary."""
    return dict(load_vocabularies()[name]['values'])


def echelon_rank():
    """{echelon: rank} from the echelon_rank vocabulary (higher = larger formation)."""
    return dict(load_vocabularies()['echelon_rank']['values'])


def echelon_display_order():
    return list(load_vocabularies()['echelon_rank']['display_order'])


def relationship_group(name):
    """Tuple of command-relationship values in one group of the relationship_groups vocabulary ('standing', 'active')."""
    return tuple(load_vocabularies()['relationship_groups']['values'][name])


def higher_than_organic():
    return {k: tuple(v) for k, v in load_vocabularies()['higher_than_organic']['values'].items()}


@functools.lru_cache(maxsize=1)
def load_nationalities():
    """data/nationalities.csv as a list of dicts (code, name, adjective, alt_adjectives, alliance, kind, note); {} rows if missing."""
    if not os.path.isfile(NATIONALITIES_CSV):
        return ()
    return tuple(read_dicts(NATIONALITIES_CSV)[1])


def nationality_names():
    return [n['name'] for n in load_nationalities()]


def nationality_by_name():
    return {n['name']: n for n in load_nationalities()}


def adjectives(nat):
    """Adjectives of a nationality row, the primary one first (US: US, American)."""
    return [nat['adjective']] + [a.strip() for a in nat['alt_adjectives'].split(';') if a.strip()]


def display_name(unit_name, nationality):
    """Name used where a unit must be unambiguous across nations: '<adjective> <unit_name>' (US VII Corps, British I Corps).
    Multinational headquarters and names that already contain the adjective as a word stay as they are. Derived, never stored."""
    nat = nationality_by_name().get(nationality)
    if not nat or nat['kind'] == 'multinational':
        return unit_name
    if any(re.search(r'\b%s\b' % re.escape(a), unit_name) for a in adjectives(nat)):
        return unit_name
    return '%s %s' % (nat['adjective'], unit_name)


def field_names(schema):
    return [f['name'] for f in schema['fields']]


def read_rows(path):
    """Return (header, rows) where rows is a list of lists of strings (no padding)."""
    with open(path, encoding='utf-8', newline='') as f:
        rd = csv.reader(f)
        header = next(rd, [])
        return header, [r for r in rd]


def read_dicts(path):
    header, rows = read_rows(path)
    return header, [dict(zip(header, r)) for r in rows]


def csv_bytes(header, rows):
    """Deterministic CSV bytes: UTF-8, LF line endings, minimal quoting."""
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator='\n')
    w.writerow(header)
    for r in rows:
        w.writerow(r)
    return buf.getvalue().encode('utf-8')


def sort_key(row):
    return (row['date'], row['claim_id'])


def claim_files():
    """All claim csv paths under data/claims, in sorted order."""
    out = []
    for dirpath, _dirs, files in os.walk(CLAIMS_DIR):
        for fn in files:
            if fn.endswith('.csv'):
                out.append(os.path.join(dirpath, fn))
    return sorted(out)


def attach_command_relationships(rows):
    """Add the derived key `command_relationships` (the compact JSON list the claim files used to hold, rebuilt from data/command_relations.csv and
    data/command_relation_claims.csv; blank when the claim lists no relation) to every claim dict. It is not a column of the claim files."""
    import command_relations
    rel = command_relations.load()
    for r in rows:
        r['command_relationships'] = rel.entries_json(r['claim_id'])
    return rows


def load_all_claims():
    """Return (header, rows) with every claim as a dict, sorted by date then claim_id. `header` is the claim-file header; each row also has the
    derived key command_relationships (see attach_command_relationships)."""
    schema = load_schema('claims')
    header = field_names(schema)
    rows = []
    for p in claim_files():
        _h, dicts = read_dicts(p)
        rows.extend(dicts)
    rows.sort(key=sort_key)
    attach_command_relationships(rows)
    return header, rows
