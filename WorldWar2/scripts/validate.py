#!/usr/bin/env python3
"""Validate every claim file and the unit table against the schema. Standard library only.

Checks: header and field count of every file, field types, booleans, lat/long ranges,
controlled vocabularies, unique claim_ids across the repository, unit_id matches both the
file name and data/units.csv, rows sorted by date then claim_id, conflict-group integrity,
strength_json structure (a scope is required whenever personnel is given), parent_unit_id resolves (blank, never a sentinel) and is the higher unit of one of the claim's relations.
Command relations (data/command_relations.csv, data/command_relation_claims.csv, data/command_relation_overlaps.csv; scripts/command_relations.py): header and
field values from schema/relations.schema.json, unique ids and natural keys, foreign keys, a blank higher unit only for relationship unknown with a note, interval and
date rules (valid_to not before valid_from, ranges, bases, end_unknown), the evidence agrees with the master (role against the stated dates, seq, same unit, first
listing and sourced dates), and every contradictory overlap (same relationship class, different higher units of one echelon) is documented or an error.
The rebuilt per-claim entries (what the old command_relationships column held) are still checked: valid keys, relationship values and resolving unit_ids (an entry with unit_id null must be relationship unknown with a note),
every row has a source URL, the columns repeated from units.csv (unit_name, nationality, echelon, branch, theater) equal the unit table.
Nationalities (data/nationalities.csv): header, unique code and name, alliance and kind vocabularies, adjective set; every unit's nationality is a row of the table,
its unit_id prefix is the row's code and its claim folder is the lower-case name.
Foreign keys: every foreignKeys entry declared in schema/claims.schema.json, units.schema.json and relations.schema.json is checked (blank allowed, list columns split on the
declared separator), and the declared primary keys of the side tables are unique.
Unit table (placeholders, see docs/methodology.md "Placeholder units"): record_status agrees with the
existence of a claim file (a placeholder must not have claim rows: run scripts/promote_placeholders.py once a claim file is
added), formed_date is a real YYYY, YYYY-MM or YYYY-MM-DD with a source URL, initial_parent_* columns are all set or all blank
and resolve, listing_source tokens are in the source_token vocabulary, and unit_name is unique within a nationality.

Operations (scripts/operations.py): every claim has an operation_id that exists in data/operations.csv; the operations table has valid ids, types, dates,
sources (or a note), an acyclic parent chain and resolving relation endpoints; some CMH campaign covers each claim's date.
Warning-only checks (printed as WARNING, never change the exit code; a claim dated outside its operation's dates without a row in
data/operation_exceptions.csv, or an operation outside its parent's dates without an explanation, are among them; see docs/methodology.md, "Review guardrails"):
an engaged_with entry that does not match a unit in data/units.csv (nationality adjective plus unit_name, or a leading part of it; free text is still
allowed for non-ground opponents),
an attached relationship whose unit is not the parent_unit_id or with no
standing entry (organic, assigned, unspecified_subordination or unknown), 'organic' used for a division, corps or army under a
higher headquarters, a named higher headquarters without a unit id, a command relationship that takes effect after the row's date or
ended before it, a location_date that differs from date without a temporal location_basis, a corps/army/army-group headquarters that is
only a town centroid (precision under 5 km), a corps or army sector recorded as an exact front_line_point, a conflict group whose rows
have different event types and no 'Event definition:' in notes, a current_activity that is long
(probably several actions in one row) or hedged ("probably", "likely"), and an engaged_with list longer than three.
Errors also cover effective_time /
effective_to_time that are not HH:MM, location_date / location_temporal_offset_days / location_basis inconsistencies and a landing row whose coordinate is a
town centroid or a command post of another date.
Coordinate checks live in scripts/check_coordinates.py.

Usage: python scripts/validate.py        (exit code 0 = OK, 1 = problems found; warnings do not count)
"""
import datetime
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common  # noqa: E402
import command_relations as crel  # noqa: E402

errors = []
warnings = []

ACTIVITY_MAX_CHARS = 120
EVENT_SUPPORT_FROM = 483  # first claim id of Batch 2, which introduced the Event support / Location support sentences
HEDGE_WORDS = re.compile(r'\b(probably|likely|presumably|apparently|possibly|perhaps|inferred|may have)\b', re.I)


def err(where, msg):
    errors.append('%s: %s' % (where, msg))


def warn(where, msg):
    warnings.append('%s: %s' % (where, msg))


def rel(path):
    return os.path.relpath(path, common.ROOT)


def is_number(s):
    try:
        float(s)
        return s.strip() == s and s.lower() not in ('nan', 'inf', '-inf', 'infinity', '-infinity')
    except ValueError:
        return False


def check_type(where, f, value):
    """Check one non-empty value against its schema field (type, format, constraints, vocabulary)."""
    t = f['type']
    c = f.get('constraints', {})
    if t == 'date':
        try:
            datetime.datetime.strptime(value, f.get('format', '%Y-%m-%d'))
            if not re.fullmatch(r'\d{4}-\d{2}-\d{2}', value):
                raise ValueError
        except ValueError:
            err(where, '%s: %r is not a valid date YYYY-MM-DD' % (f['name'], value))
    elif t == 'number':
        if not is_number(value):
            err(where, '%s: %r is not a number' % (f['name'], value))
        else:
            x = float(value)
            if 'minimum' in c and x < c['minimum']:
                err(where, '%s: %s below minimum %s' % (f['name'], value, c['minimum']))
            if 'maximum' in c and x > c['maximum']:
                err(where, '%s: %s above maximum %s' % (f['name'], value, c['maximum']))
    elif t == 'boolean':
        if value not in f.get('trueValues', ['true']) + f.get('falseValues', ['false']):
            err(where, '%s: %r must be lowercase true or false' % (f['name'], value))
    if 'pattern' in c and not re.fullmatch(c['pattern'], value):
        err(where, '%s: %r does not match pattern %s' % (f['name'], value, c['pattern']))


def check_vocab(where, f, value, vocabs):
    name = f.get('vocabulary')
    if name:
        allowed = vocabs[name]['values']
        if value not in allowed:
            err(where, '%s: %r not in vocabulary %s %s' % (f['name'], value, name, sorted(allowed)))
    lname = f.get('vocabulary_list')
    if lname:
        allowed = vocabs[lname]['values']
        for tok in [t.strip() for t in value.split(';')]:
            if tok not in allowed:
                err(where, '%s: token %r not in vocabulary %s %s' % (f['name'], tok, lname, sorted(allowed)))


def valid_partial_date(s):
    """True for a real YYYY, YYYY-MM or YYYY-MM-DD."""
    m = re.fullmatch(r'(\d{4})(?:-(\d{2})(?:-(\d{2}))?)?', s)
    if not m:
        return False
    try:
        datetime.date(int(m.group(1)), int(m.group(2) or 1), int(m.group(3) or 1))
    except ValueError:
        return False
    return True


def engaged_index(units):
    """Names that an engaged_with entry may use: '<adjective> <unit_name>' (also with the adjective removed from the name);
    the adjectives come from data/nationalities.csv."""
    idx = set()
    nats = common.nationality_by_name()
    for u in units.values():
        for adj in (common.adjectives(nats[u['nationality']]) if u['nationality'] in nats else []):
            idx.add('%s %s' % (adj, u['unit_name']))
            idx.add('%s %s' % (adj, re.sub(r'^(%s) ' % adj, '', u['unit_name'])))
            idx.add('%s %s' % (adj, u['unit_name'].replace(' %s ' % adj, ' ')))
    return idx


def check_row(where, row, fields, vocabs):
    for f in fields:
        v = row.get(f['name'], '')
        if v == '':
            if f.get('constraints', {}).get('required'):
                err(where, '%s is required but empty' % f['name'])
            continue
        if v != v.strip():
            err(where, '%s has leading or trailing whitespace' % f['name'])
        check_type(where, f, v)
        check_vocab(where, f, v, vocabs)


def check_strength_json(where, s, vocabs):
    if s == '':
        return
    try:
        d = json.loads(s)
    except ValueError as e:
        err(where, 'strength_json is not valid JSON (%s)' % e)
        return
    if not isinstance(d, dict):
        err(where, 'strength_json must be a JSON object')
        return
    allowed = {'basis', 'as_of', 'personnel', 'vehicles', 'vehicle_count_type', 'scope', 'source', 'note'}
    for k in d:
        if k not in allowed:
            err(where, 'strength_json: unknown key %r' % k)
    if d.get('basis') not in vocabs['strength_json_basis']['values']:
        err(where, 'strength_json: basis %r invalid' % d.get('basis'))
    try:
        datetime.datetime.strptime(str(d.get('as_of')), '%Y-%m-%d')
    except ValueError:
        err(where, 'strength_json: as_of must be YYYY-MM-DD')
    if not isinstance(d.get('source'), str) or not d.get('source'):
        err(where, 'strength_json: source is required')
    if 'note' in d and not isinstance(d['note'], str):
        err(where, 'strength_json: note must be a string')
    if 'personnel' in d and (not isinstance(d['personnel'], int) or isinstance(d['personnel'], bool) or d['personnel'] < 0):
        err(where, 'strength_json: personnel must be a non-negative integer')
    if 'vehicles' in d:
        v = d['vehicles']
        if not isinstance(v, dict) or not v:
            err(where, 'strength_json: vehicles must be a non-empty object')
        else:
            for k, n in v.items():
                if not isinstance(n, int) or isinstance(n, bool) or n < 0:
                    err(where, 'strength_json: vehicles[%r] must be a non-negative integer' % k)
        if d.get('vehicle_count_type') not in vocabs['strength_json_vehicle_count_type']['values']:
            err(where, 'strength_json: vehicle_count_type required with vehicles and must be in the vocabulary')
    elif 'vehicle_count_type' in d:
        err(where, 'strength_json: vehicle_count_type without vehicles')
    if 'personnel' not in d and 'vehicles' not in d:
        err(where, 'strength_json: needs personnel and/or vehicles')
    if 'scope' in d:
        if d['scope'] not in vocabs['strength_json_scope']['values']:
            err(where, 'strength_json: scope %r not in vocabulary strength_json_scope' % (d['scope'],))
    elif 'personnel' in d:
        err(where, 'strength_json has personnel but no scope: set scope to whole_unit, sub_force or sector (what the figure covers), or remove the personnel figure if no source says')


REPEATED_COLUMNS = common.load_schema('claims')['repeatedColumns']['fields']   # claim columns that must equal data/units.csv
NAT_HEADER = ['code', 'name', 'adjective', 'alt_adjectives', 'alliance', 'kind', 'note']

REL_KEYS = {'unit_id', 'relationship', 'effective_from', 'effective_from_latest', 'ordered_date', 'effective_to',
            'effective_to_earliest', 'effective_to_basis', 'date_basis', 'note', 'effective_time', 'effective_to_time'}
DATE_KEYS = ('effective_from', 'effective_from_latest', 'ordered_date', 'effective_to', 'effective_to_earliest')
# Single sources: schema/vocabularies.json (echelon_rank, relationship_groups, higher_than_organic, source_type)
STANDING_RELS = common.relationship_group('standing')
ACTIVE_RELS = common.relationship_group('active')
ECH_RANK = common.echelon_rank()
HIGHER_THAN_ORGANIC = common.higher_than_organic()


def row_echelon(row, units):
    u = units.get(row['unit_id'])
    return u['echelon'] if u else row.get('echelon', '')


def entries_of(s):
    """The dict entries of a command_relationships cell, [] when it is blank or not a valid list (reported elsewhere)."""
    if s == '':
        return []
    try:
        d = json.loads(s)
    except ValueError:
        return []
    return [e for e in d if isinstance(e, dict)] if isinstance(d, list) else []


def check_location_date(where, row):
    """location_date, location_basis and location_temporal_offset_days: temporal provenance of the coordinate."""
    ld, lb, off = row.get('location_date', ''), row.get('location_basis', ''), row.get('location_temporal_offset_days', '')
    if ld:
        try:
            delta = (datetime.date.fromisoformat(ld) - datetime.date.fromisoformat(row['date'])).days
        except ValueError:
            return
        if off == '':
            err(where, 'location_date is set but location_temporal_offset_days is blank')
        elif re.fullmatch(r'-?\d+', off) and int(off) != delta:
            err(where, 'location_temporal_offset_days %s != location_date - date (%d days)' % (off, delta))
        if delta != 0 and lb in ('', 'documented_on_date'):
            warn(where, 'location_date %s differs from date by %d days but location_basis is %r: use nearest_later_command_post, nearest_earlier_command_post or another basis' % (ld, delta, lb))
        if delta > 0 and lb == 'nearest_earlier_command_post' or delta < 0 and lb == 'nearest_later_command_post':
            err(where, 'location_basis %s contradicts the sign of the offset (%d days)' % (lb, delta))
    elif off != '':
        err(where, 'location_temporal_offset_days is set but location_date is blank')
    if lb in ('nearest_later_command_post', 'nearest_earlier_command_post') and not ld:
        err(where, 'location_basis %s requires location_date and the offset' % lb)
    if row['event_type'] == 'landing' and lb in ('town_centroid', 'nearest_later_command_post', 'nearest_earlier_command_post'):
        err(where, 'a landing row cannot take its coordinate from %s (an unrelated headquarters or town centroid); use the landing area (operational_area / documented_on_date)' % lb)
    if row['location_represents'] == 'headquarters' and lb == 'town_centroid' and row['echelon'] in ('corps', 'army', 'army_group') and row['precision_km'] not in ('', '5', '10', '25', '50'):
        warn(where, 'a %s headquarters coordinate that is only a town centroid needs precision_km >= 5 (found %s)' % (row['echelon'], row['precision_km']))
    if row['echelon'] in ('corps', 'army', 'army_group') and row['location_represents'] == 'front_line_point' and row['precision_km'] in ('1', '3', '5'):
        warn(where, 'a %s sector recorded as an exact front_line_point (precision %s km): use sector_center with a wider precision, or document the point' % (row['echelon'], row['precision_km']))


def check_command_relationships(where, row, units, vocabs):
    """parent_unit_id is a unit id (resolves) or blank (no parent, or none verified: then an unknown entry says so);
    command_relationships is blank or a JSON list. The sentinel text `unknown` is not accepted in either column."""
    pid, s = row['parent_unit_id'], row['command_relationships']
    if pid == 'unknown':
        err(where, "parent_unit_id 'unknown' is not allowed: leave it blank and give command_relationships one entry "
                   '{"unit_id": null, "relationship": "unknown", "note": "..."}')
    elif pid:
        if pid not in units:
            err(where, 'parent_unit_id %s not in units.csv' % pid)
        if pid == row['unit_id']:
            err(where, 'parent_unit_id is the unit itself')
    if s == 'unknown':
        err(where, "command_relationships 'unknown' is not allowed: leave it blank, or give the entry "
                   '{"unit_id": null, "relationship": "unknown", "note": "..."}')
        return
    if s == '':
        if pid:
            err(where, 'parent_unit_id %s needs a command_relationships entry for it' % pid)
        return
    try:
        d = json.loads(s)
    except ValueError as e:
        err(where, 'command_relationships is not valid JSON (%s)' % e)
        return
    if not isinstance(d, list) or not d:
        err(where, 'command_relationships must be a non-empty JSON list')
        return
    ids = []
    for e in d:
        if not isinstance(e, dict):
            err(where, 'command_relationships entries must be objects')
            continue
        for k in e:
            if k not in REL_KEYS:
                err(where, 'command_relationships: unknown key %r' % k)
        if 'name' in e:
            err(where, "command_relationships: 'name' is not stored (the name comes from units.csv); for an entry with unit_id null put the explanation in note")
        for k in ('unit_id', 'relationship'):
            if k not in e:
                err(where, 'command_relationships: entry missing %r' % k)
        uid = e.get('unit_id')
        if uid is not None:
            if not isinstance(uid, str) or uid not in units:
                err(where, 'command_relationships: unit_id %r not in units.csv' % (uid,))
            elif uid == row['unit_id']:
                err(where, 'command_relationships: the unit is listed as its own parent')
            ids.append(uid)
        if 'unit_id' in e and uid is None:
            if e.get('relationship') != 'unknown':
                err(where, 'command_relationships: unit_id null is only allowed with relationship unknown (a formation that is not a unit needs a placeholder in data/units.csv)')
            if not isinstance(e.get('note'), str) or not e.get('note').strip():
                err(where, 'command_relationships: an entry with unit_id null needs a note saying what is unknown')
        if e.get('relationship') not in vocabs['relationship']['values']:
            err(where, 'command_relationships: relationship %r not in vocabulary relationship' % e.get('relationship'))
        if 'note' in e and not isinstance(e['note'], str):
            err(where, 'command_relationships: note must be a string')
        okdates = {}
        for dk in DATE_KEYS:
            if dk in e:
                try:
                    if not re.fullmatch(r'\d{4}-\d{2}-\d{2}', str(e[dk])):
                        raise ValueError
                    datetime.datetime.strptime(e[dk], '%Y-%m-%d')
                    okdates[dk] = e[dk]
                except ValueError:
                    err(where, 'command_relationships: %s must be YYYY-MM-DD' % dk)
        if 'effective_from' in okdates and okdates['effective_from'] > row['date']:
            warn(where, 'command_relationships: %s is effective from %s, after the row date %s' % (
                e.get('unit_id'), okdates['effective_from'], row['date']))
        if 'effective_to' in okdates:
            if 'effective_from' in okdates and okdates['effective_to'] < okdates['effective_from']:
                err(where, 'command_relationships: effective_to %s is before effective_from %s' % (okdates['effective_to'], okdates['effective_from']))
            if okdates['effective_to'] < row['date']:
                warn(where, 'command_relationships: %s ended on %s, before the row date %s' % (e.get('unit_id'), okdates['effective_to'], row['date']))
        if 'ordered_date' in okdates and 'effective_from' in okdates and okdates['ordered_date'] > okdates['effective_from']:
            err(where, 'command_relationships: ordered_date %s is after effective_from %s (an order cannot follow the date it takes effect)' % (okdates['ordered_date'], okdates['effective_from']))
        if 'effective_from_latest' in okdates:
            if 'effective_from' not in okdates:
                err(where, 'command_relationships: effective_from_latest needs effective_from (the earliest possible start)')
            elif okdates['effective_from_latest'] < okdates['effective_from']:
                err(where, 'command_relationships: effective_from_latest %s is before effective_from %s' % (okdates['effective_from_latest'], okdates['effective_from']))
        if 'effective_to_earliest' in okdates:
            if 'effective_to' not in okdates:
                err(where, 'command_relationships: effective_to_earliest needs effective_to (the latest possible end)')
            elif okdates['effective_to_earliest'] > okdates['effective_to']:
                err(where, 'command_relationships: effective_to_earliest %s is after effective_to %s' % (okdates['effective_to_earliest'], okdates['effective_to']))
        for bk in ('date_basis', 'effective_to_basis'):
            if bk in e and e[bk] not in vocabs['relationship_date_basis']['values']:
                err(where, 'command_relationships: %s %r not in vocabulary relationship_date_basis' % (bk, e[bk]))
        if 'effective_to_basis' in e and 'effective_to' not in e:
            err(where, 'command_relationships: effective_to_basis without effective_to')
        for tk, dk in (('effective_time', 'effective_from'), ('effective_to_time', 'effective_to')):
            if tk in e:
                if not isinstance(e[tk], str) or not re.fullmatch(r'([01]\d|2[0-3]):[0-5]\d', e[tk]):
                    err(where, 'command_relationships: %s must be HH:MM (24-hour; say in the note which clock the source uses)' % tk)
                if dk not in e:
                    err(where, 'command_relationships: %s needs %s' % (tk, dk))
        ur = units.get(e.get('unit_id')) if e.get('unit_id') else None
        if e.get('relationship') == 'organic' and ur and ECH_RANK.get(row_echelon(row, units), 0) >= 4 and ur['echelon'] in HIGHER_THAN_ORGANIC.get(row_echelon(row, units), ()):
            warn(where, "command_relationships: 'organic' used for %s -> %s (%s); a division, corps or army under a higher headquarters is assigned, attached, "
                        "unspecified_subordination or operational_control, not organic" % (row_echelon(row, units), ur['echelon'], e.get('unit_id')))
    if len(ids) != len(set(ids)):
        err(where, 'command_relationships lists the same unit_id twice')
    if pid and pid not in ids:
        err(where, 'parent_unit_id %s is not listed in command_relationships' % pid)
    entries = [e for e in d if isinstance(e, dict)]
    ops = [e for e in entries if e.get('relationship') in ACTIVE_RELS]
    # An attachment to a higher headquarters than the parent (e.g. a division in a corps zone that the CMH table shows attached to an army)
    # does not make that army the immediate parent, so it is not flagged.
    pech = ECH_RANK.get((units.get(pid) or {}).get('echelon'), 0)
    ops = [e for e in ops if ECH_RANK.get((units.get(e.get('unit_id')) or {}).get('echelon'), 0) <= pech or e.get('unit_id') not in units]
    if ops and pid and pid not in [e.get('unit_id') for e in ops]:
        warn(where, 'an attached/operational_control entry exists but parent_unit_id %s is not one of them (parent_unit_id is the operational parent)' % pid)
    if any(e.get('relationship') == 'attached' for e in entries) and not any(
            e.get('relationship') in STANDING_RELS for e in entries):
        warn(where, 'attached entry without a standing parent entry (organic, assigned, unspecified_subordination or unknown)')
    u = units.get(row['unit_id'])
    if u and u['parent_unit_id'] and not any(
            isinstance(e, dict) and e.get('unit_id') == u['parent_unit_id'] and e.get('relationship') == 'organic' for e in d):
        err(where, 'units.csv parent_unit_id %s must appear as an organic entry in command_relationships' % u['parent_unit_id'])


REFERENCE_TYPES = set(common.vocab_values('source_type'))   # schema/vocabularies.json, vocabulary source_type


def check_references(claims):
    """Every cited URL (claims.source, units.formed_date_source), unit source token and strength source maps to a row of
    data/references_meta.csv; the metadata rows are well formed. (build.py --check verifies data/references.csv itself.)"""
    import build_references as br
    where = 'data/references_meta.csv'
    if not os.path.isfile(br.META_CSV):
        err(where, 'missing (see scripts/build_references.py)')
        return
    header, meta = br.read_meta()
    if header != br.META_HEADER:
        err(where, 'header %s != %s' % (header, br.META_HEADER))
        return
    seen_id, seen_url = set(), set()
    for i, m in enumerate(meta, start=2):
        w = '%s line %d' % (where, i)
        if not re.fullmatch(r'R\d{3,}', m['reference_id']):
            err(w, 'reference_id %r is not R### ' % m['reference_id'])
        if m['reference_id'] in seen_id:
            err(w, 'duplicate reference_id %s' % m['reference_id'])
        seen_id.add(m['reference_id'])
        if m['url']:
            if m['url'] in seen_url:
                err(w, 'duplicate url %s' % m['url'])
            seen_url.add(m['url'])
            if br.norm_url(m['url'])[0] != m['url']:
                err(w, 'url is not normalised (no fragment; www.ibiblio.org): %s' % m['url'])
            if not re.match(r'https?://', m['url']):
                err(w, 'url is not http(s): %s' % m['url'])
        else:
            err(w, 'url is empty')
        for f in ('short_title', 'full_citation', 'source_type', 'publisher', 'license_or_status', 'reliability_note', 'used_for'):
            if not m[f].strip():
                err(w, '%s is empty' % f)
        if m['source_type'] not in REFERENCE_TYPES:
            err(w, 'source_type %r not one of %s' % (m['source_type'], sorted(REFERENCE_TYPES)))
        if m['link_status'] not in ('', 'ok', 'blocked_403', 'not_found', 'error', 'unchecked'):
            err(w, 'link_status %r' % m['link_status'])
        if m['link_status'] == 'not_found':
            warn(w, '%s was not found at the last link check: replace it with a working URL from the same source' % m['url'])
    _c, _u, stats, missing, _m, _o = br.derive()
    for k, first in sorted(missing.items()):
        err('citation', '%s cited by %s has no row in data/references_meta.csv (run python scripts/build_references.py --seed)' % (k, first))
    for m in meta:
        st = stats[m['reference_id']]
        if not st['claims'] and not st['units'] and not st['ops']:
            warn(where, '%s (%s) is not cited by any claim, unit or operation: remove the row or cite it' % (m['reference_id'], m['short_title']))
        if not re.fullmatch(r'[a-z0-9_]+', m['source_family']):
            err(where, '%s source_family %r must be a lower-case token (see vocabularies.json source_family)' % (m['reference_id'], m['source_family']))
    check_claim_references(claims, meta)


def check_claim_references(claims, meta):
    """The stored claim -> reference links: reference_ids (every id exists, at least one per claim), source_locator, the roles table, the
    consistency of the readable `source` citation with the ids, and the independent-source rubric for confidence 0.9 (warning)."""
    import build_references as br
    by_id = {m['reference_id']: m for m in meta}
    by_claim = {c['claim_id']: c for c in claims}
    cited, _missing = br.cited_links(claims, meta)   # URLs of `source` / coordinate note / strength_json -> reference ids
    for c in claims:
        w = c['claim_id']
        ids = br.parse_ids(c.get('reference_ids', ''))
        if not ids:
            err(w, 'reference_ids is empty: every claim needs at least one reference (see CONTRIBUTING.md "How to cite a new source")')
            continue
        for rid in ids:
            if rid not in by_id:
                err(w, 'reference_ids: %s is not in data/references_meta.csv' % rid)
        if len(set(ids)) != len(ids):
            err(w, 'reference_ids lists a reference twice: %s' % c['reference_ids'])
        locs, bad = br.parse_locators(c.get('source_locator', ''))
        for b in bad:
            err(w, 'source_locator part %r is not "R###: page or section"' % b)
        for rid in locs:
            if rid not in ids:
                err(w, 'source_locator names %s, which is not in reference_ids' % rid)
        for rid in sorted({x[0] for x in cited.get(w, [])} - set(ids)):
            err(w, 'the citation (source / coordinate note / strength_json) resolves to %s but reference_ids does not list it' % rid)
        for rid in ids:
            if rid in by_id and rid not in {x[0] for x in cited.get(w, [])}:
                warn(w, 'reference_ids lists %s but no URL, coordinate note or strength source in the claim cites it: add its URL to `source`' % rid)
        if c.get('confidence') and float(c['confidence']) >= 0.9:
            fam = {by_id[r]['source_family'] for r in ids if r in by_id}
            if len(fam) < 2:
                warn(w, 'confidence %s needs references from at least two source families (Wikipedia counts as one); has %s' % (c['confidence'], sorted(fam)))
    where = 'data/claim_reference_roles.csv'
    if not os.path.isfile(br.ROLES_CSV):
        err(where, 'missing')
        return
    header, rows = br.read_roles()
    if header != br.ROLE_HEADER:
        err(where, 'header %s != %s' % (header, br.ROLE_HEADER))
        return
    seen = set()
    for i, r in enumerate(rows, start=2):
        w = '%s line %d' % (where, i)
        c = by_claim.get(r['claim_id'])
        if c is None:
            err(w, 'unknown claim_id %s' % r['claim_id'])
        elif r['reference_id'] not in br.parse_ids(c.get('reference_ids', '')):
            err(w, '%s is not in the reference_ids of %s' % (r['reference_id'], r['claim_id']))
        if r['role'] not in br.ROLES or r['role'] == 'general':
            err(w, 'role %r must be one of %s (general is the default and is not stored)' % (r['role'], br.ROLES[:-1]))
        if (r['claim_id'], r['reference_id'], r['role']) in seen:
            err(w, 'duplicate row')
        seen.add((r['claim_id'], r['reference_id'], r['role']))
        if not r['basis'].strip():
            err(w, 'basis is empty (say why the role was assigned)')


def check_operations(claims, vocabs):
    """data/operations.csv, operation_relations.csv, operation_exceptions.csv and every claim's operation_id (rules in scripts/operations.py;
    window and parent-date problems are warnings, structural problems errors)."""
    import operations
    import build_references as br
    refs = {m['reference_id'] for m in br.read_meta()[1]}
    es, ws = operations.check(operations.load(), claims, refs, set(vocabs['theater']['values']), valid_partial_date)
    for wh, m in es:
        err(wh, m)
    for wh, m in ws:
        warn(wh, m)


def check_nationalities():
    """data/nationalities.csv: header, unique code and name, vocabularies for alliance and kind, adjective set."""
    where = 'data/nationalities.csv'
    if not os.path.isfile(common.NATIONALITIES_CSV):
        err(where, 'missing')
        return {}
    header, rows = common.read_dicts(common.NATIONALITIES_CSV)
    if header != NAT_HEADER:
        err(where, 'header %s != %s' % (header, NAT_HEADER))
        return {}
    alliances, kinds = common.vocab_values('alliance'), common.vocab_values('nationality_kind')
    codes, names = set(), set()
    for i, r in enumerate(rows, start=2):
        w = '%s line %d' % (where, i)
        if not re.fullmatch(r'[A-Z]{2,4}', r['code']):
            err(w, 'code %r must be 2-4 capital letters (the unit_id prefix)' % r['code'])
        if r['code'] in codes:
            err(w, 'duplicate code %s' % r['code'])
        if r['name'] in names:
            err(w, 'duplicate name %s' % r['name'])
        codes.add(r['code'])
        names.add(r['name'])
        for f in ('name', 'adjective', 'alliance', 'kind', 'note'):
            if not r[f].strip():
                err(w, '%s is empty' % f)
        if r['name'] != r['name'].strip() or r['name'] == 'All':
            err(w, "name %r is invalid ('All' is reserved for operation scopes)" % r['name'])
        if r['alliance'] not in alliances:
            err(w, 'alliance %r not in vocabulary alliance %s' % (r['alliance'], alliances))
        if r['kind'] not in kinds:
            err(w, 'kind %r not in vocabulary nationality_kind %s' % (r['kind'], kinds))
    if [r['code'] for r in rows] != sorted(r['code'] for r in rows):
        err(where, 'rows must be sorted by code')
    return {r['name']: r for r in rows}


def check_foreign_keys(tables):
    """Enforce every foreignKeys entry declared in schema/claims.schema.json, units.schema.json and relations.schema.json, and the
    declared primary keys / unique columns of the side tables. `tables` maps resource name -> list of row dicts. A blank value is
    allowed (nullable reference); a column with a `separator` holds a list of keys; `alsoAllowed` lists extra accepted values."""
    decl = [(n, fk) for n in ('claims', 'units') for fk in common.load_schema(n).get('foreignKeys', [])]
    rel = common.load_json(os.path.join(common.SCHEMA_DIR, 'relations.schema.json'))['tables']
    for name, t in rel.items():
        decl.extend((name, fk) for fk in t.get('foreignKeys', []))
    for src, fk in decl:
        dst, dfield = fk['reference']['resource'], fk['reference']['fields']
        if src not in tables or dst not in tables:
            err('schema', 'foreign key %s.%s refers to unknown resource %s' % (src, fk['fields'], dst))
            continue
        allowed = {r[dfield] for r in tables[dst]} | set(fk.get('alsoAllowed', []))
        sep = fk.get('separator')
        for i, r in enumerate(tables[src], start=2):
            v = r.get(fk['fields'], '')
            if not v:
                continue
            for tok in ([t.strip() for t in v.split(sep) if t.strip()] if sep else [v]):
                if tok not in allowed:
                    err(r.get('_where') or 'data/%s row %d' % (src, i), 'foreign key %s.%s = %r is not a %s.%s' % (src, fk['fields'], tok, dst, dfield))
    for name, t in rel.items():
        pk = t.get('primaryKey')
        if not pk or name not in tables:
            continue
        pk = [pk] if isinstance(pk, str) else pk
        seen = set()
        for i, r in enumerate(tables[name], start=2):
            k = tuple(r[c] for c in pk)
            if '' in k:
                err('data/%s row %d' % (name, i), 'primary key %s is blank' % pk)
            if k in seen:
                err('data/%s row %d' % (name, i), 'duplicate primary key %s = %s' % (pk, k))
            seen.add(k)
        for col in t.get('unique', []):
            vals = [r[col] for r in tables[name]]
            if len(vals) != len(set(vals)):
                err('data/%s' % name, 'column %s must be unique' % col)
        for cols in t.get('uniqueTogether', []):
            seen = {}
            for i, r in enumerate(tables[name], start=2):
                k = tuple(r[c] for c in cols)
                if k in seen:
                    err('data/%s row %d' % (name, i), 'natural key %s = %s repeats row %d' % (cols, k, seen[k]))
                seen[k] = i


def check_command_relation_tables(units, vocabs, claims):
    """data/command_relations.csv (master), data/command_relation_claims.csv (evidence join) and data/command_relation_overlaps.csv: headers and
    field values from schema/relations.schema.json; the interval rules (see schema/README.md, "Validity of a relationship"); the evidence agrees with
    the master; every contradictory overlap is documented. Keys and foreign keys are checked by check_foreign_keys."""
    sch = common.load_json(os.path.join(common.SCHEMA_DIR, 'relations.schema.json'))['tables']
    paths = {'command_relations': crel.REL_CSV, 'command_relation_claims': crel.LINK_CSV, 'command_relation_overlaps': crel.OVERLAP_CSV}
    for name, path in paths.items():
        where = 'data/%s.csv' % name
        if not os.path.isfile(path):
            err(where, 'missing')
            continue
        fields = sch[name]['fields']
        header, rows = common.read_rows(path)
        if header != [f['name'] for f in fields]:
            err(where, 'header %s != schema/relations.schema.json %s' % (header, [f['name'] for f in fields]))
            continue
        for i, r in enumerate(rows, start=2):
            if len(r) != len(header):
                err('%s line %d' % (where, i), 'expected %d fields, found %d' % (len(header), len(r)))
            else:
                check_row('%s line %d' % (where, i), dict(zip(header, r)), fields, vocabs)
    rel = crel.load(True)
    ids = [r['relation_id'] for r in rel.rows]
    if ids != sorted(ids):
        err('data/command_relations.csv', 'rows must be sorted by relation_id')
    cinfo = {c['claim_id']: c for c in claims}
    standing = common.relationship_group('standing')
    for i, r in enumerate(rel.rows, start=2):
        where = 'data/command_relations.csv %s' % r['relation_id']
        links = rel.by_relation.get(r['relation_id'], [])
        if not r['higher_unit_id']:
            if r['relationship'] != 'unknown':
                err(where, 'higher_unit_id may be blank only for relationship unknown (an explicit placeholder)')
            if not r['note']:
                err(where, 'a relation with no higher unit needs a note saying what is unknown')
        elif r['higher_unit_id'] == r['subject_unit_id']:
            err(where, 'the unit is listed as its own parent')
        for a, b in (('valid_to', 'valid_from'), ('valid_from_latest', 'valid_from'), ('valid_to_earliest', 'valid_to')):
            if r[a] and r[b] and (r[a] < r[b] if a != 'valid_to_earliest' else r[a] > r[b]):
                err(where, '%s %s is %s %s %s' % (a, r[a], 'after' if a == 'valid_to_earliest' else 'before', b, r[b]))
        if r['valid_from_latest'] and r['valid_from_latest'] < r['valid_from']:
            err(where, 'valid_from_latest %s is before valid_from %s' % (r['valid_from_latest'], r['valid_from']))
        if r['valid_to_earliest'] and not r['valid_to']:
            err(where, 'valid_to_earliest needs valid_to (the latest possible end)')
        if r['valid_to'] and r['valid_to'] < r['valid_from']:
            err(where, 'valid_to %s is before valid_from %s' % (r['valid_to'], r['valid_from']))
        if r['ordered_date'] and r['ordered_date'] > r['valid_from']:
            err(where, 'ordered_date %s is after valid_from %s (an order cannot follow the date it takes effect)' % (r['ordered_date'], r['valid_from']))
        for tk, dk in (('valid_from_time', 'valid_from'), ('valid_to_time', 'valid_to')):
            if r[tk] and not r[dk]:
                err(where, '%s needs %s' % (tk, dk))
        if bool(r['valid_to']) != (r['valid_to_basis'] != 'open_at_last_claim'):
            err(where, 'valid_to %r and valid_to_basis %s disagree (blank valid_to <=> open_at_last_claim)' % (r['valid_to'], r['valid_to_basis']))
        if r['valid_to_basis'] == 'inferred_from_next_claim' and not r['valid_to_earliest']:
            err(where, 'inferred_from_next_claim needs valid_to_earliest (the last claim date that lists the relation)')
        want = 'true' if r['valid_to_basis'] in crel.END_INFERRED and r['relationship'] not in standing else 'false'
        if r['end_unknown'] != want:
            err(where, 'end_unknown is %s but must be %s (true = a temporary relationship with no sourced end)' % (r['end_unknown'], want))
        if r['change_undated'] == 'true' and (r['status'] != 'preferred' or not r['higher_unit_id'] or r['relationship'] == 'organic'):
            err(where, 'change_undated applies to preferred, named, non-organic relations only')
        if not links:
            err(where, 'no row in data/command_relation_claims.csv: a relation needs evidence')
            continue
        lc = [cinfo[l['claim_id']] for l in links if l['claim_id'] in cinfo]
        if any(c['unit_id'] != r['subject_unit_id'] for c in lc):
            err(where, 'a linked claim belongs to another unit than the subject %s' % r['subject_unit_id'])
        if r['status'] == 'preferred' and lc and not any(c['claim_status'] == 'preferred' for c in lc):
            err(where, 'a preferred relation needs a preferred claim as evidence')
        if r['status'] != 'preferred' and any(c['claim_status'] == 'preferred' for c in lc):
            err(where, 'a %s relation is evidenced by a preferred claim (it should be preferred)' % r['status'])
        if lc:
            first = min(c['date'] for c in lc)
            if r['valid_from_basis'] == 'claim_date' and r['valid_from'] != first:
                err(where, 'valid_from_basis claim_date but valid_from %s is not the date of the first linked claim %s' % (r['valid_from'], first))
            if r['valid_from_basis'] != 'claim_date' and not any(l['stated_effective_from'] for l in links):
                err(where, 'valid_from_basis %s but no linked claim states effective_from' % r['valid_from_basis'])
            if r['valid_to_basis'] == 'inferred_from_next_claim' and r['valid_to_earliest'] not in {c['date'] for c in lc}:
                err(where, 'valid_to_earliest %s must be the date of a linked claim (the last one that lists the relation before the inferred end)' % r['valid_to_earliest'])
            if r['valid_to_basis'] not in crel.END_INFERRED and not any(l['stated_effective_to'] for l in links):
                err(where, 'valid_to_basis %s but no linked claim states effective_to' % r['valid_to_basis'])
    for i, l in enumerate(rel.links, start=2):
        where = 'data/command_relation_claims.csv line %d' % i
        stated = {k: l[col] for k, col in crel.STATED if l[col] != ''}
        if l['role'] != crel.role_of(stated):
            err(where, 'role %s does not agree with the stated dates (expected %s)' % (l['role'], crel.role_of(stated)))
        if stated.get('effective_from_latest') and not stated.get('effective_from'):
            err(where, 'stated_effective_from_latest needs stated_effective_from')
        if stated.get('effective_to_earliest') and not stated.get('effective_to'):
            err(where, 'stated_effective_to_earliest needs stated_effective_to')
    for cid, ls in rel.by_claim.items():
        if [int(l['seq']) for l in ls] != list(range(1, len(ls) + 1)):
            err('data/command_relation_claims.csv', 'seq of claim %s is not 1..%d without gaps' % (cid, len(ls)))
        names = [rel.by_id[l['relation_id']]['higher_unit_id'] for l in ls if l['relation_id'] in rel.by_id]
        if len(names) != len(set(n for n in names if n)) + names.count(''):
            err('data/command_relation_claims.csv', 'claim %s lists the same higher unit twice' % cid)
    # contradictory overlaps: all documented, none stale, none duplicated
    found = {(a['relation_id'], b['relation_id']): (lo, hi) for a, b, lo, hi in crel.contradictory_overlaps(rel.rows, units)}
    listed = {}
    for o in rel.overlaps:
        k = (o['relation_id_a'], o['relation_id_b'])
        if k in listed:
            err('data/command_relation_overlaps.csv', 'overlap %s is listed twice' % (k,))
        listed[k] = o
        if o['relation_id_a'] >= o['relation_id_b']:
            err('data/command_relation_overlaps.csv', 'relation_id_a must be lower than relation_id_b (%s, %s)' % k)
        if k not in found:
            err('data/command_relation_overlaps.csv', 'listed overlap %s is not a contradictory overlap of the master table (stale entry)' % (k,))
        elif (o['overlap_from'], o['overlap_to']) != found[k]:
            err('data/command_relation_overlaps.csv', 'overlap %s lists %s to %s but the intervals overlap %s to %s' % (k, o['overlap_from'], o['overlap_to'], found[k][0], found[k][1]))
    for k, (lo, hi) in sorted(found.items()):
        if k not in listed:
            err('data/command_relations.csv', 'relations %s and %s overlap (%s to %s) but are contradictory (same relationship class, different higher units of one echelon) and not documented in data/command_relation_overlaps.csv' % (k[0], k[1], lo, hi or 'open'))
    ol = [o for o in rel.overlaps]
    ids = [(o['relation_id_a'], o['relation_id_b']) for o in ol]
    if ids != sorted(ids):
        err('data/command_relation_overlaps.csv', 'rows must be sorted by relation_id_a, relation_id_b')


def main():
    claims_schema = common.load_schema('claims')
    units_schema = common.load_schema('units')
    vocabs = common.load_vocabularies()
    cfields = claims_schema['fields']
    cheader = [f['name'] for f in cfields]
    ufields = units_schema['fields']
    uheader = [f['name'] for f in ufields]

    nats = check_nationalities()

    # ---- units.csv ----
    units = {}
    if not os.path.isfile(common.UNITS_CSV):
        err('data/units.csv', 'missing')
    else:
        header, rows = common.read_rows(common.UNITS_CSV)
        if header != uheader:
            err('data/units.csv', 'header %s != schema %s' % (header, uheader))
        for i, r in enumerate(rows, start=2):
            where = 'data/units.csv line %d' % i
            if len(r) != len(uheader):
                err(where, 'expected %d fields, found %d' % (len(uheader), len(r)))
                continue
            row = dict(zip(header, r))
            check_row(where, row, ufields, vocabs)
            if row['unit_id'] in units:
                err(where, 'duplicate unit_id %s' % row['unit_id'])
            units[row['unit_id']] = row
        ids = list(units)
        if ids != sorted(ids):
            err('data/units.csv', 'rows must be sorted by unit_id')
        seen_names = {}
        for uid, u in units.items():
            key = (u['nationality'], u['unit_name'])
            if key in seen_names:
                err('data/units.csv', 'unit_name %r is used by both %s and %s (names must be unique within a nationality)' % (u['unit_name'], seen_names[key], uid))
            seen_names[key] = uid
            where = 'data/units.csv unit %s' % uid
            nat = nats.get(u['nationality'])
            if nat and uid.split('-')[0] != nat['code']:
                err(where, 'unit_id prefix %s is not the code %s of nationality %s' % (uid.split('-')[0], nat['code'], u['nationality']))
            if u['formed_date']:
                if not valid_partial_date(u['formed_date']):
                    err(where, 'formed_date %r is not a real YYYY, YYYY-MM or YYYY-MM-DD' % u['formed_date'])
                if not u['formed_date_source']:
                    err(where, 'formed_date needs a formed_date_source URL')
            elif u['formed_date_source']:
                err(where, 'formed_date_source without formed_date')
            ip = [u['initial_parent_unit_id'], u['initial_parent_as_of'], u['initial_parent_source']]
            if any(ip) and not all(ip):
                err(where, 'initial_parent_unit_id, initial_parent_as_of and initial_parent_source must be all set or all blank')
            if u['initial_parent_as_of'] and not valid_partial_date(u['initial_parent_as_of']):
                err(where, 'initial_parent_as_of %r is not a real YYYY-MM or YYYY-MM-DD' % u['initial_parent_as_of'])
            if u['initial_parent_unit_id']:
                if u['initial_parent_unit_id'] not in units:
                    err(where, 'initial_parent_unit_id %s not in units' % u['initial_parent_unit_id'])
                if u['initial_parent_unit_id'] == uid:
                    err(where, 'initial_parent_unit_id is the unit itself')
        for uid in units:
            seen, cur = {uid}, units[uid]['initial_parent_unit_id']
            while cur and cur in units:
                if cur in seen:
                    err('data/units.csv', 'initial_parent_unit_id chain from %s loops at %s' % (uid, cur))
                    break
                seen.add(cur)
                cur = units[cur]['initial_parent_unit_id']
        for uid, u in units.items():
            p = u['parent_unit_id']
            if p and p not in units:
                err('data/units.csv', 'parent_unit_id %s of %s not in units' % (p, uid))
            if p == uid:
                err('data/units.csv', '%s is its own parent' % uid)

    eng_index = engaged_index(units)
    relset = crel.load(True)   # the command-relation tables (checked in check_command_relation_tables)

    # ---- claim files ----
    files = common.claim_files()
    if not files:
        err('data/claims', 'no claim files found')
    seen_ids = {}
    all_rows = []
    unit_with_file = set()
    for path in files:
        r_path = rel(path)
        parts = r_path.split(os.sep)
        if len(parts) != 4 or parts[:2] != ['data', 'claims']:
            err(r_path, 'claim files must be data/claims/<nationality>/<unit_id>.csv')
            continue
        folder, stem = parts[2], parts[3][:-4]
        if folder != folder.lower():
            err(r_path, 'nationality folder must be lowercase')
        header, rows = common.read_rows(path)
        if header != cheader:
            err(r_path, 'header does not match schema/claims.schema.json (expected %s)' % cheader)
            continue
        if stem not in units:
            err(r_path, 'unit_id %s (file name) not in data/units.csv' % stem)
        else:
            unit_with_file.add(stem)
            if units[stem]['record_status'] == 'placeholder':
                err(r_path, 'unit %s is a placeholder (record_status=placeholder) in units.csv but has a claim file: run scripts/promote_placeholders.py to set record_status=active' % stem)
            if units[stem]['nationality'].lower() != folder:
                err(r_path, 'folder %s does not match unit nationality %s' % (folder, units[stem]['nationality']))
        if not rows:
            err(r_path, 'file has no rows')
        prev = None
        for i, r in enumerate(rows, start=2):
            where = '%s line %d' % (r_path, i)
            if len(r) != len(cheader):
                err(where, 'expected %d fields, found %d' % (len(cheader), len(r)))
                continue
            row = dict(zip(header, r))
            check_row(where, row, cfields, vocabs)
            cid = row['claim_id']
            if cid in seen_ids:
                err(where, 'duplicate claim_id %s (also in %s)' % (cid, seen_ids[cid]))
            seen_ids[cid] = r_path
            if row['unit_id'] != stem:
                err(where, 'unit_id %s does not match file name %s' % (row['unit_id'], stem))
            u = units.get(row['unit_id'])
            if u:
                for col in REPEATED_COLUMNS:
                    if row[col] != u[col]:
                        err(where, '%s %r differs from units.csv %r' % (col, row[col], u[col]))
            k = (row['date'], row['claim_id'])
            if prev and k < prev:
                err(where, 'rows must be sorted by date then claim_id')
            prev = k
            if not re.search(r'https?://', row['source']):
                err(where, 'source must contain at least one URL')
            if row['claim_status'] != 'preferred' and not row['conflict_group_id']:
                err(where, 'claim_status %s requires a conflict_group_id' % row['claim_status'])
            check_strength_json(where, row['strength_json'], vocabs)
            row['command_relationships'] = relset.entries_json(cid)   # derived from the relation tables; not a claim-file column
            check_command_relationships(where, row, units, vocabs)
            check_location_date(where, row)
            act = row['current_activity']
            if len(act) > ACTIVITY_MAX_CHARS:
                warn(where, 'current_activity is %d characters (> %d): one row should describe one documented action; put the rest in notes' % (len(act), ACTIVITY_MAX_CHARS))
            if HEDGE_WORDS.search(act):
                warn(where, 'current_activity contains a hedge word (%s): state only what the source documents; put doubt in notes' % HEDGE_WORDS.search(act).group(0))
            m = re.fullmatch(r'C(\d+)', row['claim_id'])
            if m and int(m.group(1)) >= EVENT_SUPPORT_FROM and row['event_type'] in ('command_change', 'activation', 'subordinate_assignment') \
                    and row['confidence'] and float(row['confidence']) <= 0.3 and 'Event support:' not in row['notes']:
                warn(where, 'low-confidence command row without an "Event support:" sentence in notes (confidence scores the location; say how well the event itself is documented)')
            if row['engaged_with'] and row['engaged_with'] != 'unknown':
                for x in [x.strip() for x in row['engaged_with'].split(';') if x.strip()]:
                    if x != 'unknown' and x not in eng_index and not any(n.startswith(x + ' ') for n in eng_index):
                        warn(where, 'engaged_with %r does not match a unit in data/units.csv (nationality adjective + unit_name); fine for non-ground or unnamed opponents, otherwise add the unit as a placeholder' % x)
            if row['engaged_with'] and row['engaged_with'] != 'unknown' and len([x for x in row['engaged_with'].split(';') if x.strip()]) > 3:
                warn(where, 'engaged_with lists more than three opponents: check that they were fought in one action')
            row['_where'] = where
            all_rows.append(row)

    for uid, u in units.items():
        if u['record_status'] in ('partial', 'active') and uid not in unit_with_file:
            err('data/units.csv', '%s has record_status %s but no claim file (only a placeholder has none)' % (uid, u['record_status']))
        # a placeholder that has a claim file is reported at the claim file

    # ---- conflict groups ----
    groups = {}
    for r in all_rows:
        if r['conflict_group_id']:
            groups.setdefault(r['conflict_group_id'], []).append(r)
    for g, rs in sorted(groups.items()):
        where = 'conflict group %s' % g
        if len(rs) < 2:
            err(where, 'a conflict group needs at least two claims')
        if len({r['unit_id'] for r in rs}) != 1:
            err(where, 'all claims of a group must be about the same unit_id')
        st = [r['claim_status'] for r in rs]
        if st.count('preferred') > 1:
            err(where, 'more than one preferred claim')
        if 'preferred' in st and 'disputed' in st:
            err(where, 'a group with a preferred claim cannot also contain disputed claims')
        if 'preferred' not in st and any(s != 'disputed' for s in st):
            err(where, 'a group with no preferred claim must be all disputed')
        if len({r['date'] for r in rs}) < 2 and len({r['latitude'] + r['longitude'] for r in rs}) < 2:
            err(where, 'competing claims should differ in date or place')
        if len({r['event_type'] for r in rs}) > 1 and not all('Event definition:' in r['notes'] for r in rs):
            warn(where, 'rows have different event_type values (different event definitions, not just different sources): each row needs an "Event definition:" sentence in notes')

    # ---- command-relationship validity (informational; see schema/README.md "Validity of a relationship") ----
    by_unit = {}
    for r in all_rows:
        by_unit.setdefault(r['unit_id'], []).append(r)
    open_end = []
    for uid, rs in by_unit.items():
        rs.sort(key=lambda r: (r['date'], r['claim_id']))
        for i, r in enumerate(rs):
            if r['command_relationships'] == '':
                continue
            later = [x for x in rs[i + 1:] if x['date'] > r['date']]
            if not later:
                continue
            nxt = later[0]
            nxt_keys = {(f.get('unit_id'), f.get('relationship')) for f in entries_of(nxt['command_relationships'])}
            for e in entries_of(r['command_relationships']):
                if e.get('relationship') in ACTIVE_RELS and 'effective_to' not in e \
                        and (e.get('unit_id'), e.get('relationship')) not in nxt_keys:
                    open_end.append((r['claim_id'], nxt['claim_id']))
    if open_end:
        print('NOTE: %d attached/operational_control entries have no effective_to and are not listed by the unit\'s next claim; '
              'a missing effective_to never means indefinitely valid: data/command_relations.csv closes them at the next claim '
              '(valid_to_basis inferred_from_next_claim, end_unknown true). Add effective_to to the claim\'s link row (stated_effective_to) and the relation\'s '
              'valid_to where a source dates the end.\n' % len(open_end))

    check_command_relation_tables(units, vocabs, all_rows)
    check_operations(all_rows, vocabs)
    check_references(all_rows)

    # ---- foreign keys declared in the schemas ----
    import build_references as br
    import operations as opsmod
    ops = opsmod.load()
    exc_path = os.path.join(common.ROOT, 'data', 'coordinate_exceptions.csv')
    tables = {'claims': all_rows, 'units': list(units.values()), 'nationalities': list(nats.values()),
              'operations': ops.rows, 'operation_relations': ops.relations, 'operation_exceptions': ops.exceptions,
              'coordinate_exceptions': common.read_dicts(exc_path)[1] if os.path.isfile(exc_path) else [],
              'references_meta': br.read_meta()[1] if os.path.isfile(br.META_CSV) else [],
              'claim_reference_roles': br.read_roles()[1] if os.path.isfile(br.ROLES_CSV) else [],
              'command_relations': relset.rows, 'command_relation_claims': relset.links, 'command_relation_overlaps': relset.overlaps}
    check_foreign_keys(tables)

    for w in warnings:
        print('WARNING', w)
    if warnings:
        print('%d warning(s): prompts to re-check a row, not errors\n' % len(warnings))
    if errors:
        for e in errors:
            print('ERROR', e)
        print('\nFAILED: %d problem(s) in %d claim file(s)' % (len(errors), len(files)))
        return 1
    print('OK: %d claim files, %d claims, %d units, %d conflict groups' % (len(files), len(all_rows), len(units), len(groups)))
    return 0


if __name__ == '__main__':
    sys.exit(main())
