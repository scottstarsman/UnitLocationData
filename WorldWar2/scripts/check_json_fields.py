#!/usr/bin/env python3
"""Validate every JSON-in-cell column against its JSON Schema.

The registry schema/json/fields.json lists each column (table glob, column, schema file). Every non-blank
cell must parse as JSON and satisfy its schema. Uses only the standard library: a small validator for the
JSON Schema keywords the schemas in schema/json/ use (type, enum, required, properties, additionalProperties,
minProperties, minLength, minimum, pattern, format date, anyOf, dependentRequired). It also checks that each
schema enum equals the matching vocabulary in schema/vocabularies.json. Exit code 1 on any problem.
"""
import csv, datetime, glob, json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SDIR = os.path.join(ROOT, 'schema', 'json')
USED = {'$schema', '$id', 'title', 'description', 'examples', 'type', 'enum', 'required', 'properties',
        'additionalProperties', 'minProperties', 'minLength', 'minimum', 'pattern', 'format', 'anyOf', 'dependentRequired'}
TYPES = {'object': dict, 'string': str, 'array': list, 'boolean': bool}


def is_type(v, t):
    if t == 'integer':
        return isinstance(v, int) and not isinstance(v, bool)
    if t == 'number':
        return isinstance(v, (int, float)) and not isinstance(v, bool)
    return isinstance(v, TYPES[t])


def validate(v, s, path='$'):
    errs = []
    unknown = set(s) - USED
    if unknown:
        return ['%s: schema uses unsupported keywords %s' % (path, sorted(unknown))]
    if 'type' in s and not is_type(v, s['type']):
        return ['%s: expected %s, got %s' % (path, s['type'], type(v).__name__)]
    if 'enum' in s and v not in s['enum']:
        errs.append('%s: %r not in %s' % (path, v, s['enum']))
    if isinstance(v, str):
        if len(v) < s.get('minLength', 0):
            errs.append('%s: shorter than %d' % (path, s['minLength']))
        if 'pattern' in s and not re.search(s['pattern'], v):
            errs.append('%s: %r does not match %s' % (path, v, s['pattern']))
        if s.get('format') == 'date':
            try:
                datetime.datetime.strptime(v, '%Y-%m-%d')
            except ValueError:
                errs.append('%s: %r is not a valid date' % (path, v))
    if is_type(v, 'number') and 'minimum' in s and v < s['minimum']:
        errs.append('%s: %r below minimum %r' % (path, v, s['minimum']))
    if isinstance(v, dict):
        for k in s.get('required', []):
            if k not in v:
                errs.append('%s: missing required key %r' % (path, k))
        if len(v) < s.get('minProperties', 0):
            errs.append('%s: needs at least %d keys' % (path, s['minProperties']))
        props = s.get('properties', {})
        for k, x in v.items():
            if k in props:
                errs += validate(x, props[k], '%s.%s' % (path, k))
            elif s.get('additionalProperties') is False:
                errs.append('%s: unknown key %r' % (path, k))
            elif isinstance(s.get('additionalProperties'), dict):
                errs += validate(x, s['additionalProperties'], '%s[%r]' % (path, k))
        for k, deps in s.get('dependentRequired', {}).items():
            if k in v:
                for d in deps:
                    if d not in v:
                        errs.append('%s: %r requires %r' % (path, k, d))
    if 'anyOf' in s and not any(not validate(v, alt, path) for alt in s['anyOf']):
        errs.append('%s: matches none of anyOf %s' % (path, [a.get('required', a) for a in s['anyOf']]))
    return errs


def vocab_drift(schema, vocabs, name):
    out = []
    for k, p in schema.get('properties', {}).items():
        voc = '%s_%s' % (name, k)
        if 'enum' in p and voc in vocabs and sorted(p['enum']) != sorted(vocabs[voc]['values']):
            out.append('%s.%s enum %s differs from vocabulary %s %s' % (name, k, sorted(p['enum']), voc, sorted(vocabs[voc]['values'])))
    return out


def main():
    reg = json.load(open(os.path.join(SDIR, 'fields.json')))
    vocabs = json.load(open(os.path.join(ROOT, 'schema', 'vocabularies.json')))
    problems, cells = [], 0
    for f in reg['fields']:
        schema = json.load(open(os.path.join(SDIR, f['schema'])))
        problems += vocab_drift(schema, vocabs, f['column'])
        for i, ex in enumerate(schema.get('examples', [])):
            problems += ['%s example %d: %s' % (f['schema'], i, e) for e in validate(ex, schema)]
        files = sorted(glob.glob(os.path.join(ROOT, f['table'])))
        for extra in f.get('also_in', []):
            files += [os.path.join(ROOT, extra)] if os.path.exists(os.path.join(ROOT, extra)) else []
        for path in files:
            rel = os.path.relpath(path, ROOT)
            with open(path, newline='', encoding='utf-8') as fh:
                for n, row in enumerate(csv.DictReader(fh), start=2):
                    v = row.get(f['column'], '')
                    if v == '':
                        if not f.get('blank_allowed', True):
                            problems.append('%s line %d: %s is blank' % (rel, n, f['column']))
                        continue
                    cells += 1
                    try:
                        d = json.loads(v)
                    except ValueError as e:
                        problems.append('%s line %d (%s): %s is not valid JSON (%s)' % (rel, n, row.get('claim_id', ''), f['column'], e))
                        continue
                    for e in validate(d, schema):
                        problems.append('%s line %d (%s): %s %s' % (rel, n, row.get('claim_id', ''), f['column'], e))
    for p in problems:
        print('ERROR ' + p)
    if problems:
        print('FAILED: %d JSON cell problem(s)' % len(problems))
        return 1
    print('OK: %d JSON cells in %d column(s) match their schemas' % (cells, len(reg['fields'])))
    return 0


if __name__ == '__main__':
    sys.exit(main())
