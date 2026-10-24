"""Shared helpers for the validation, build and split scripts (standard library only)."""
import csv
import io
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLAIMS_DIR = os.path.join(ROOT, 'data', 'claims')
UNITS_CSV = os.path.join(ROOT, 'data', 'units.csv')
SCHEMA_DIR = os.path.join(ROOT, 'schema')
BUILD_DIR = os.path.join(ROOT, 'build')


def load_json(path):
    with open(path, encoding='utf-8') as f:
        return json.load(f)


def load_schema(name='claims'):
    return load_json(os.path.join(SCHEMA_DIR, name + '.schema.json'))


def load_vocabularies():
    return load_json(os.path.join(SCHEMA_DIR, 'vocabularies.json'))


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


def load_all_claims():
    """Return (header, rows) with every claim as a dict, sorted by date then claim_id."""
    schema = load_schema('claims')
    header = field_names(schema)
    rows = []
    for p in claim_files():
        _h, dicts = read_dicts(p)
        rows.extend(dicts)
    rows.sort(key=sort_key)
    return header, rows
