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
Unit references in claims (scripts/unit_refs.py, see schema/README.md): engaged_with and composing_units are `;` lists of unit_ids (or the sentinel `unknown` alone),
each a row of units.csv (foreign key), no duplicate, never the claiming unit itself, an opponent on the other side of the war (nationalities.alliance); engaged_note
and composing_text are free text that never repeats the name of a unit that has an id, never starts with `attached:`, and never contains a unit id that does not exist; a
composing_text entry that starts with a unit id must be `<unit_id> (<qualifier>)` for an id listed in composing_units; engaged_note must hold no unit id; the lists are
written canonically (entries joined by "; ").
Command relations: a link of role listed_by_higher_unit belongs to the HIGHER unit's claim, which lists the subject in composing_units, keeps the wording in stated_note and states the start if it
lists the relation before it starts (see schema/README.md, "Command relations"). docs/deferred_relations.md: the relationships whose subordinate formation is not a unit of the table;
every row names an existing claim of its unit, a higher unit of the table, a vocabulary relationship and an entry that is still in the claim's composing_text.
Note labels: a sentence of `notes` that starts with `Label: ` uses a label of the vocabulary note_label (closed set, exact spelling); source and batch lead-ins are prose.
Claim ids: unique, C plus four digits or more; data/retired_claims.csv records removed claims (a retired id is never a claim again); unrecorded gaps in the numbering are
listed as a NOTE. Reuse across revisions: scripts/check_claim_ids.py (needs git history).
Claim key: unit_id + date + event_type identify one claim (schema/claims.schema.json `uniqueTogether`); a repeat is allowed only inside one conflict group or when
data/claim_key_exceptions.csv lists the pair with a reason (an exception that is not needed is an error).
Places: names and aliases identify one place each (no alias is another place's name or alias); data/place_merges.csv lists the ids retired by merging two places (the id is not a
row of places.csv, the survivor is, no claim uses a retired id).
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
an attached relationship whose unit is not the parent_unit_id or with no
standing entry (organic, assigned, unspecified_subordination or unknown), 'organic' used for a division, corps or army under a
higher headquarters, a named higher headquarters without a unit id, a command relationship that takes effect after the row's date or
ended before it, a location_date that differs from date without a temporal location_basis, a corps/army/army-group headquarters that is
only a town centroid (precision under 5 km), a corps or army sector recorded as an exact front_line_point, a conflict group whose rows
have different event types and no 'Event definition:' in notes, a current_activity that is long
(probably several actions in one row) or hedged ("probably", "likely"), and an engaged_with plus engaged_note list longer than three.
Errors also cover effective_time /
effective_to_time that are not HH:MM, location_date / location_temporal_offset_days / location_basis inconsistencies and a landing row whose coordinate is a
town centroid or a command post of another date.
Places (data/places.csv, schema/places.schema.json; scripts/places.py): header and field values, unique ids and names (ignoring case), sorted by place_id, no alias equal to another
place's name, coord_reference_id a gazetteer_geocoder reference that a claim at the place lists, every claim's place_id resolves, a claim's latitude/longitude equal the place's
exactly when coord_override is blank (and differ, within 5 km, when it is set), the coordinate note no longer ends `source`. A place with no claim is a warning.
Derived values are not stored (location_name, location_temporal_offset_days, strength_status, the roles of coordinate-service references; scripts/places.py,
scripts/build_references.py): a role row for a gazetteer_geocoder reference is an error; strength_json may carry `status` (full, reduced, heavily_depleted), which build/all_claims.csv turns into strength_status.
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
import places as placesmod  # noqa: E402
import unit_refs  # noqa: E402

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
    allowed = {'basis', 'as_of', 'personnel', 'vehicles', 'vehicle_count_type', 'scope', 'status', 'source', 'note'}
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
    if 'status' in d and d['status'] not in vocabs['strength_json_status']['values']:
        err(where, 'strength_json: status %r not in vocabulary strength_json_status %s (destroyed is derived from the destroyed flag)' % (d['status'], sorted(vocabs['strength_json_status']['values'])))
    if 'personnel' not in d and 'vehicles' not in d and 'status' not in d:
        err(where, 'strength_json: needs personnel, vehicles and/or status')
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
_LETTERS, NO_ID_LETTER, _CC = common.echelon_id_letters()
ID_LETTER_ECHELON = {letter: echelon for echelon, letter in _LETTERS.items()}   # 'D' -> 'division'
COMBAT_COMMAND_ID = re.compile(_CC)
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
    """location_date and location_basis: temporal provenance of the coordinate (the offset in days is derived: scripts/places.py)."""
    ld, lb = row.get('location_date', ''), row.get('location_basis', '')
    if ld:
        try:
            delta = (datetime.date.fromisoformat(ld) - datetime.date.fromisoformat(row['date'])).days
        except ValueError:
            return
        if delta != 0 and lb in ('', 'documented_on_date'):
            warn(where, 'location_date %s differs from date by %d days but location_basis is %r: use nearest_later_command_post, nearest_earlier_command_post or another basis' % (ld, delta, lb))
        if delta > 0 and lb == 'nearest_earlier_command_post' or delta < 0 and lb == 'nearest_later_command_post':
            err(where, 'location_basis %s contradicts the sign of the offset (%d days)' % (lb, delta))
    if lb in ('nearest_later_command_post', 'nearest_earlier_command_post') and not ld:
        err(where, 'location_basis %s requires location_date' % lb)
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
            if rid in by_id and by_id[rid]['source_type'] != 'gazetteer_geocoder' and rid not in {x[0] for x in cited.get(w, [])}:
                warn(w, 'reference_ids lists %s but no URL, coordinate note or strength source in the claim cites it: add its URL to `source`' % rid)
        if c.get('confidence') and float(c['confidence']) >= 0.9:
            fam = {by_id[r]['source_family'] for r in ids if r in by_id and by_id[r]['source_type'] != 'gazetteer_geocoder'}   # a coordinate service is not evidence
            if len(fam) < 2:
                warn(w, 'confidence %s needs references from at least two source families (Wikipedia counts as one; a gazetteer_geocoder reference is not evidence and does not count); has %s' % (c['confidence'], sorted(fam)))
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
        if r['reference_id'] in by_id and by_id[r['reference_id']]['source_type'] == 'gazetteer_geocoder':
            err(w, '%s is a gazetteer_geocoder reference: its role location is derived (build_references.py), not stored' % r['reference_id'])
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


def check_place_merges(places_by_id):
    """data/place_merges.csv (retired place id -> the place it was merged into): header, sorted, one row per retired id, a retired id is not a
    place in data/places.csv (ids are never reused), the survivor is a place and not itself retired, name and note are filled.
    Returns {retired_place_id: merged_into_place_id}."""
    where = 'data/place_merges.csv'
    if not os.path.isfile(placesmod.MERGES_CSV):
        err(where, 'missing (see scripts/places.py)')
        return {}
    h, rows = common.read_rows(placesmod.MERGES_CSV)
    if h != placesmod.MERGES_HEADER:
        err(where, 'header %s != %s' % (h, placesmod.MERGES_HEADER))
        return {}
    out, ids = {}, []
    for i, r in enumerate(rows, start=2):
        w = '%s line %d' % (where, i)
        if len(r) != len(h):
            err(w, 'expected %d fields, found %d' % (len(h), len(r)))
            continue
        d = dict(zip(h, r))
        for k in h:
            if not d[k].strip():
                err(w, '%s is blank' % k)
        for k in ('retired_place_id', 'merged_into_place_id'):
            if not re.match(r'^PL\d{4,}$', d[k]):
                err(w, '%s %r is not a place id (PL0001 onward)' % (k, d[k]))
        ids.append(d['retired_place_id'])
        if d['retired_place_id'] in out:
            err(w, 'place id %s is retired twice' % d['retired_place_id'])
        out[d['retired_place_id']] = d['merged_into_place_id']
        if d['retired_place_id'] == d['merged_into_place_id']:
            err(w, '%s cannot be merged into itself' % d['retired_place_id'])
        if d['retired_place_id'] in places_by_id:
            err(w, 'retired place id %s is still a row of data/places.csv (a retired id leaves the table and is never reused)' % d['retired_place_id'])
    if ids != sorted(ids):
        err(where, 'rows must be sorted by retired_place_id')
    for i, r in enumerate(rows, start=2):
        if len(r) == len(h) and r[1] not in places_by_id:
            err('%s line %d' % (where, i), 'merged_into_place_id %s is not a row of data/places.csv (a survivor is a live place, not a retired id)' % r[1])
    return out


NOTE_LEAD = re.compile(r'(?:^|(?<=\. )|(?<=; )|(?<=\] )|(?<=\) ))([A-Za-z]+(?: [A-Za-z]+){0,2})(?: \(([^()]*)\))?: ')   # a sentence-initial `Phrase: ` or `Phrase (qualifier): ` (start of the cell, or after '. ', '; ', '] ' or ') ')
NOTE_LABEL_SHAPE = re.compile(r'[A-Z][a-z]+(?: [a-z]+){0,2}')   # what a label looks like: not a source name, a batch, an id or a number
NOTE_PROSE_LEAD = ('Wikipedia',)                                 # a source name of label shape: the sentence quotes the source, it is not a label


def check_note_labels(where, row, labels):
    """The labels of `notes` (vocabulary note_label) are a closed set. A sentence that starts with `Label: ` or `Label (qualifier): ` must use a label of the
    vocabulary, spelled exactly; a sentence-initial phrase of label shape that is not one is an error (to add a label see schema/README.md, "Note labels").
    Lead-ins that name a source or a batch ('CMH ETO-OB chronology:', 'Breakout-28 p577:', 'Batch 2 review:', 'Wikipedia:') are prose and ignored."""
    folded = {x.casefold(): x for x in labels}
    for m in NOTE_LEAD.finditer(row['notes']):
        base = m.group(1)
        if base in labels:
            continue
        if base.casefold() in folded:
            err(where, "notes: label %r is spelled %r in the vocabulary note_label (use the exact spelling)" % (base + ':', folded[base.casefold()]))
        elif NOTE_LABEL_SHAPE.fullmatch(base) and not base.startswith(NOTE_PROSE_LEAD):
            err(where, "notes: unknown label %r (allowed: %s). A new label is added to the vocabulary note_label in schema/vocabularies.json, to schema/README.md "
                       "('Note labels') in the same change; otherwise rewrite the sentence so that it does not start with 'Word: '"
                % (base + ':', ', '.join(sorted(labels))))


RETIRED_CLAIMS_CSV = os.path.join(common.ROOT, 'data', 'retired_claims.csv')
RETIRED_CLAIMS_HEADER = ['claim_id', 'replaced_by_claim_id', 'reason']


def check_claim_ids(claims):
    """Claim ids (CONTRIBUTING.md, "Claim ids"): `claim_id` is C plus at least four digits and unique (duplicates are reported where the files are read); a claim
    that is removed is recorded in data/retired_claims.csv (claim_id, replaced_by_claim_id, reason) and its id is never a claim again; gaps in the numbering are
    allowed (an id that was never used is simply skipped) and are listed as a NOTE when they are not recorded. Whether an id of an earlier revision was dropped or
    reused needs git history: scripts/check_claim_ids.py. Returns the retired rows (dicts)."""
    where = 'data/retired_claims.csv'
    live = {c['claim_id'] for c in claims}
    out = []
    if not os.path.isfile(RETIRED_CLAIMS_CSV):
        err(where, 'missing (header %s)' % ','.join(RETIRED_CLAIMS_HEADER))
        return out
    h, rows = common.read_rows(RETIRED_CLAIMS_CSV)
    if h != RETIRED_CLAIMS_HEADER:
        err(where, 'header %s != %s' % (h, RETIRED_CLAIMS_HEADER))
        return out
    seen = set()
    for i, r in enumerate(rows, start=2):
        w = '%s line %d' % (where, i)
        if len(r) != len(h):
            err(w, 'expected %d fields, found %d' % (len(h), len(r)))
            continue
        d = dict(zip(h, r))
        out.append(d)
        if not re.fullmatch(r'C\d{4,}', d['claim_id']):
            err(w, 'claim_id %r is not a claim id (C0001 onward)' % d['claim_id'])
        if d['claim_id'] in seen:
            err(w, 'claim_id %s is retired twice' % d['claim_id'])
        seen.add(d['claim_id'])
        if d['claim_id'] in live:
            err(w, 'claim_id %s is retired but is also a claim: a retired id is never reused' % d['claim_id'])
        if d['replaced_by_claim_id'] and d['replaced_by_claim_id'] not in live:
            err(w, 'replaced_by_claim_id %s is not a claim' % d['replaced_by_claim_id'])
        if d['replaced_by_claim_id'] == d['claim_id']:
            err(w, '%s cannot be replaced by itself' % d['claim_id'])
        if not d['reason'].strip():
            err(w, 'reason is blank: say why the claim was removed (a wrong claim is corrected or contradicted, not deleted; see CONTRIBUTING.md)')
    if [d['claim_id'] for d in out] != sorted(d['claim_id'] for d in out):
        err(where, 'rows must be sorted by claim_id')
    nums = [int(x[1:]) for x in live | seen if re.fullmatch(r'C\d{4,}', x)]
    gaps = sorted(set(range(1, (max(nums) if nums else 0) + 1)) - set(nums))
    if gaps:
        print('NOTE: %d claim id(s) below the highest are neither a claim nor retired (a gap is allowed if the id was never used; a deleted claim must be in '
              'data/retired_claims.csv): %s\n' % (len(gaps), ', '.join('C%04d' % g for g in gaps[:20]) + (' ...' if len(gaps) > 20 else '')))
    return out


CLAIM_KEY_EXCEPTIONS_CSV = os.path.join(common.ROOT, 'data', 'claim_key_exceptions.csv')
CLAIM_KEY_EXCEPTIONS_HEADER = ['claim_id', 'other_claim_id', 'reason']


def check_claim_keys(claims, schema):
    """The natural key of a claim (schema/claims.schema.json, `uniqueTogether`: unit_id, date, event_type) is unique. Two claims with the same key are allowed
    only when (a) both are in the same conflict group (the sources disagree: one preferred, the others alternate, or all disputed) or (b) the pair is listed with a
    reason in data/claim_key_exceptions.csv (several actions of one kind by one unit on one day, one row per action). Returns the exception rows (dicts)."""
    where = 'data/claim_key_exceptions.csv'
    exc, pairs = [], {}
    if not os.path.isfile(CLAIM_KEY_EXCEPTIONS_CSV):
        err(where, 'missing (header %s)' % ','.join(CLAIM_KEY_EXCEPTIONS_HEADER))
    else:
        h, rows = common.read_rows(CLAIM_KEY_EXCEPTIONS_CSV)
        if h != CLAIM_KEY_EXCEPTIONS_HEADER:
            err(where, 'header %s != %s' % (h, CLAIM_KEY_EXCEPTIONS_HEADER))
        else:
            ids = {c['claim_id'] for c in claims}
            prev = None
            for i, r in enumerate(rows, start=2):
                w = '%s line %d' % (where, i)
                if len(r) != len(h):
                    err(w, 'expected %d fields, found %d' % (len(h), len(r)))
                    continue
                d = dict(zip(h, r))
                exc.append(d)
                if not d['reason'].strip():
                    err(w, 'reason is blank: say why the two claims are different actions and not duplicates')
                for k in ('claim_id', 'other_claim_id'):
                    if d[k] not in ids:
                        err(w, '%s %r is not a claim' % (k, d[k]))
                if d['claim_id'] >= d['other_claim_id']:
                    err(w, 'list the pair with the lower claim_id first (%s, %s)' % (d['claim_id'], d['other_claim_id']))
                key = (d['claim_id'], d['other_claim_id'])
                if key in pairs:
                    err(w, 'pair %s / %s is listed twice' % key)
                if prev is not None and key < prev:
                    err(where, 'rows must be sorted by claim_id, other_claim_id')
                prev = key
                pairs[key] = w
    used = set()
    for cols in schema.get('uniqueTogether', []):
        seen = {}
        for c in claims:
            seen.setdefault(tuple(c[x] for x in cols), []).append(c)
        for k, cs in sorted(seen.items()):
            if len(cs) < 2:
                continue
            cs = sorted(cs, key=lambda c: c['claim_id'])
            for i, a in enumerate(cs):
                for b in cs[i + 1:]:
                    if a['conflict_group_id'] and a['conflict_group_id'] == b['conflict_group_id']:
                        continue
                    if (a['claim_id'], b['claim_id']) in pairs:
                        used.add((a['claim_id'], b['claim_id']))
                        continue
                    err(b['_where'], 'claims %s and %s have the same %s = %s: one unit has one claim per date and event type. If the sources disagree, put both '
                                     'in one conflict group (same conflict_group_id, claim_status); if they are different actions of one kind on the same day, '
                                     'list the pair with a reason in data/claim_key_exceptions.csv; otherwise they are duplicates: correct the existing claim '
                                     '(see CONTRIBUTING.md, "Claim identity")' % (a['claim_id'], b['claim_id'], '/'.join(cols), ' / '.join(k)))
    for key, w in sorted(pairs.items()):
        if key not in used:
            err(w, 'pair %s / %s does not need an exception (the claims do not share unit_id, date and event_type, or they are in one conflict group): remove the row' % key)
    return exc


def check_places(claims, vocabs):
    """data/places.csv and the claim -> place links: header and field values from schema/places.schema.json, ids and names unique, aliases unambiguous,
    the coordinate service, and that each claim's point equals its place's exactly when coord_override is blank. Returns the place rows (with _where)."""
    import build_references as br
    where = 'data/places.csv'
    sch = common.load_schema('places')
    fields = sch['fields']
    header = [f['name'] for f in fields]
    if not os.path.isfile(placesmod.PLACES_CSV):
        err(where, 'missing (see scripts/places.py)')
        return []
    h, rows = common.read_rows(placesmod.PLACES_CSV)
    if h != header:
        err(where, 'header %s != schema/places.schema.json %s' % (h, header))
        return []
    meta = {m['reference_id']: m for m in br.read_meta()[1]}
    out, names, ids = [], {}, []
    for i, r in enumerate(rows, start=2):
        w = '%s line %d' % (where, i)
        if len(r) != len(h):
            err(w, 'expected %d fields, found %d' % (len(h), len(r)))
            continue
        d = dict(zip(h, r))
        d['_where'] = w
        check_row(w, d, fields, vocabs)
        out.append(d)
        ids.append(d['place_id'])
        k = d['name'].casefold()
        if k in names:
            err(w, 'name %r is already the name of %s (place names are unique, ignoring case)' % (d['name'], names[k]))
        names[k] = d['place_id']
        if d['coord_reference_id']:
            m = meta.get(d['coord_reference_id'])
            if m is None:
                err(w, 'coord_reference_id %s is not in data/references_meta.csv' % d['coord_reference_id'])
            elif m['source_type'] != 'gazetteer_geocoder':
                err(w, 'coord_reference_id %s is not a gazetteer_geocoder reference (the coordinate service); a hand-worked point leaves it blank and explains itself in coord_source_note' % d['coord_reference_id'])
    if ids != sorted(ids):
        err(where, 'rows must be sorted by place_id')
    if len(ids) != len(set(ids)):
        err(where, 'duplicate place_id')
    by_id = {d['place_id']: d for d in out}
    retired = check_place_merges(by_id)
    alias_of = {}
    for d in out:
        seen = set()
        for a in [x.strip() for x in d['alt_names'].split(';') if x.strip()]:
            if a.casefold() == d['name'].casefold():
                err(d['_where'], 'alt name %r repeats the name' % a)
            if a.casefold() in seen:
                err(d['_where'], 'alt name %r is listed twice' % a)
            seen.add(a.casefold())
            if a.casefold() in names and names[a.casefold()] != d['place_id']:
                err(d['_where'], 'alt name %r is the name of %s (an alias must not name another place)' % (a, names[a.casefold()]))
            if a.casefold() in alias_of and alias_of[a.casefold()] != d['place_id']:
                err(d['_where'], 'alt name %r is also an alias of %s (a name or alias identifies one place)' % (a, alias_of[a.casefold()]))
            alias_of.setdefault(a.casefold(), d['place_id'])
    used = {}
    for c in claims:
        p = by_id.get(c['place_id'])
        if c['place_id'] in retired:
            err(c['_where'], 'place_id %s was retired: the place was merged into %s (data/place_merges.csv); use %s' % (c['place_id'], retired[c['place_id']], retired[c['place_id']]))
        if p is None:
            continue   # unknown id: reported by the foreign-key check
        used.setdefault(p['place_id'], []).append(c)
        same = (float(c['latitude']), float(c['longitude'])) == (float(p['latitude']), float(p['longitude']))
        if same and c['coord_override']:
            err(c['_where'], 'coord_override is set but the claim point equals the place point of %s: leave it blank' % p['place_id'])
        if not same:
            dist = placesmod.km(float(c['latitude']), float(c['longitude']), float(p['latitude']), float(p['longitude']))
            if not c['coord_override']:
                err(c['_where'], 'latitude/longitude differ from place %s %r by %.0f m and coord_override is blank: use the place point or say why in coord_override' % (p['place_id'], p['name'], dist * 1000))
            elif dist > 5:
                err(c['_where'], 'the claim point is %.1f km from place %s %r: farther than 5 km is a different place' % (dist, p['place_id'], p['name']))
        if re.search(r' ; coords?:', c['source']):
            err(c['_where'], "source ends with a coordinate note ('; coords: ...'): the note is the place's coord_source_note (or the claim's coord_override)")
    for d in out:
        cs = used.get(d['place_id'], [])
        if not cs:
            warn(d['_where'], 'place %s %r has no claim: remove it or add the claim' % (d['place_id'], d['name']))
        elif d['coord_reference_id'] and not any(d['coord_reference_id'] in br.parse_ids(c['reference_ids']) for c in cs):
            err(d['_where'], 'coord_reference_id %s is not in the reference_ids of any claim at the place' % d['coord_reference_id'])
    return out


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
    decl = [(n, fk) for n in ('claims', 'units', 'places') for fk in common.load_schema(n).get('foreignKeys', [])]
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
        own = [l for l in links if l['role'] != crel.LISTED]
        listed = [l for l in links if l['role'] == crel.LISTED]
        lc = [cinfo[l['claim_id']] for l in own if l['claim_id'] in cinfo]       # claims of the subject unit
        lh = [cinfo[l['claim_id']] for l in listed if l['claim_id'] in cinfo]    # claims of the higher unit that list the subject
        if any(c['unit_id'] != r['subject_unit_id'] for c in lc):
            err(where, 'a linked claim belongs to another unit than the subject %s' % r['subject_unit_id'])
        for l in listed:
            c = cinfo.get(l['claim_id'])
            if c is None:
                continue
            if c['unit_id'] != r['higher_unit_id']:
                err(where, 'link to %s has role listed_by_higher_unit but the claim belongs to %s, not to the higher unit %s' % (c['claim_id'], c['unit_id'], r['higher_unit_id']))
            elif r['subject_unit_id'] not in unit_refs.split_ids(c.get('composing_units', '')) and r['subject_unit_id'] not in unit_refs.embedded_ids(c.get('composing_text', '')):
                err(where, 'link to %s has role listed_by_higher_unit but the claim does not list %s in composing_units' % (c['claim_id'], r['subject_unit_id']))
            if c['date'] < r['valid_from'] and l['stated_effective_from'] != r['valid_from']:
                err(where, 'claim %s (%s) lists the relation before it starts (%s) and does not state that start in stated_effective_from' % (c['claim_id'], c['date'], r['valid_from']))
            if not l['stated_note'].strip():
                err(where, 'link to %s has role listed_by_higher_unit: stated_note must keep what the claim said about the unit' % c['claim_id'])
        lc_all = lc + lh
        if r['status'] == 'preferred' and lc_all and not any(c['claim_status'] == 'preferred' for c in lc_all):
            err(where, 'a preferred relation needs a preferred claim as evidence')
        if r['status'] != 'preferred' and any(c['claim_status'] == 'preferred' for c in lc_all):
            err(where, 'a %s relation is evidenced by a preferred claim (it should be preferred)' % r['status'])
        if lc_all:
            first = min(c['date'] for c in (lc or lh))
            if r['valid_from_basis'] == 'claim_date' and r['valid_from'] != first:
                err(where, 'valid_from_basis claim_date but valid_from %s is not the date of the first linked claim %s' % (r['valid_from'], first))
            if r['valid_from_basis'] != 'claim_date' and not any(l['stated_effective_from'] for l in links):
                err(where, 'valid_from_basis %s but no linked claim states effective_from' % r['valid_from_basis'])
            if r['valid_to_basis'] == 'inferred_from_next_claim' and r['valid_to_earliest'] not in {c['date'] for c in lc_all}:
                err(where, 'valid_to_earliest %s must be the date of a linked claim (the last one that lists the relation before the inferred end)' % r['valid_to_earliest'])
            if r['valid_to_basis'] not in crel.END_INFERRED and not any(l['stated_effective_to'] for l in links):
                err(where, 'valid_to_basis %s but no linked claim states effective_to' % r['valid_to_basis'])
    for i, l in enumerate(rel.links, start=2):
        where = 'data/command_relation_claims.csv line %d' % i
        stated = {k: l[col] for k, col in crel.STATED if l[col] != ''}
        if l['role'] != crel.LISTED and l['role'] != crel.role_of(stated):
            err(where, 'role %s does not agree with the stated dates (expected %s)' % (l['role'], crel.role_of(stated)))
        if stated.get('effective_from_latest') and not stated.get('effective_from'):
            err(where, 'stated_effective_from_latest needs stated_effective_from')
        if stated.get('effective_to_earliest') and not stated.get('effective_to'):
            err(where, 'stated_effective_to_earliest needs stated_effective_to')
    for cid, ls in rel.by_claim.items():
        if [int(l['seq']) for l in ls] != list(range(1, len(ls) + 1)):
            err('data/command_relation_claims.csv', 'seq of claim %s is not 1..%d without gaps' % (cid, len(ls)))
        names = [rel.by_id[l['relation_id']]['higher_unit_id'] for l in ls if l['relation_id'] in rel.by_id and l['role'] != crel.LISTED]
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


def check_deferred_relations(units, vocabs, claims):
    """docs/deferred_relations.md: the relationships a claim states whose subordinate formation is not a unit of the table. Every row names an existing
    claim of claim_unit_id, a higher_unit_id that is a unit (or blank with a higher_unit name), a relationship of the vocabulary, a date and a source, and
    text_in_claim must be an entry of the claim's composing_text (so the formation stays named in the claim)."""
    path = os.path.join(common.ROOT, 'docs', 'deferred_relations.md')
    where = 'docs/deferred_relations.md'
    if not os.path.isfile(path):
        err(where, 'missing')
        return
    cols = ['id', 'claim_id', 'claim_unit_id', 'subject', 'higher_unit_id', 'higher_unit', 'relationship', 'date_as_stated', 'source_as_stated', 'text_in_claim']
    cinfo = {c['claim_id']: c for c in claims}
    seen = set()
    n = 0
    for i, line in enumerate(open(path, encoding='utf-8').read().split('\n'), start=1):
        if not re.match(r'^\| D\d+ \|', line):
            continue
        n += 1
        cells = [c.strip() for c in line.strip().strip('|').split(' | ')]
        w = '%s line %d' % (where, i)
        if len(cells) != len(cols):
            err(w, 'expected %d cells (%s), found %d (a "|" inside a cell?)' % (len(cols), ', '.join(cols), len(cells)))
            continue
        r = dict(zip(cols, cells))
        if r['id'] in seen:
            err(w, 'duplicate id %s' % r['id'])
        seen.add(r['id'])
        c = cinfo.get(r['claim_id'])
        if c is None:
            err(w, 'claim %s does not exist' % r['claim_id'])
            continue
        if c['unit_id'] != r['claim_unit_id']:
            err(w, 'claim %s belongs to %s, not to %s' % (r['claim_id'], c['unit_id'], r['claim_unit_id']))
        if r['higher_unit_id'] and r['higher_unit_id'] not in units:
            err(w, 'higher_unit_id %s is not a unit_id in data/units.csv' % r['higher_unit_id'])
        if not r['higher_unit_id'] and not r['higher_unit']:
            err(w, 'higher_unit_id or higher_unit must be given')
        if r['relationship'] not in vocabs['relationship']['values']:
            err(w, 'relationship %r is not in the vocabulary relationship' % r['relationship'])
        for k in ('subject', 'date_as_stated', 'source_as_stated', 'text_in_claim'):
            if not r[k]:
                err(w, '%s is empty' % k)
        if r['text_in_claim'] and r['text_in_claim'] not in unit_refs.split_list(c.get('composing_text', '')):
            err(w, 'text_in_claim %r is not an entry of composing_text of %s (%r)' % (r['text_in_claim'], r['claim_id'], c.get('composing_text', '')))
        if r['subject'] in units or r['subject'] in {u['unit_name'] for u in units.values()}:
            err(w, 'subject %r is a unit of the table: record the relationship in data/command_relations.csv' % r['subject'])
    if not n:
        err(where, 'no rows (D01 ...)')


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
            # echelon letter (vocabulary echelon_id_letter): an id ending in digits and G, A, C, D, B or H must have that echelon; regiments, battle groups and battalions have no letter
            lm = re.search(r'[0-9]([A-Z])$', uid)
            if lm and lm.group(1) in ID_LETTER_ECHELON and ID_LETTER_ECHELON[lm.group(1)] != u['echelon'] and not (u['echelon'] in NO_ID_LETTER and COMBAT_COMMAND_ID.match(uid)):
                err(where, 'unit_id %s ends in the echelon letter %s (%s) but echelon is %s: regiments, battle groups and battalions have no echelon letter in the id '
                           '(see vocabulary echelon_id_letter)' % (uid, lm.group(1), ID_LETTER_ECHELON[lm.group(1)], u['echelon']))
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

    unit_refs.reset()
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
            check_note_labels(where, row, vocabs['note_label']['values'])
            act = row['current_activity']
            if len(act) > ACTIVITY_MAX_CHARS:
                warn(where, 'current_activity is %d characters (> %d): one row should describe one documented action; put the rest in notes' % (len(act), ACTIVITY_MAX_CHARS))
            if HEDGE_WORDS.search(act):
                warn(where, 'current_activity contains a hedge word (%s): state only what the source documents; put doubt in notes' % HEDGE_WORDS.search(act).group(0))
            m = re.fullmatch(r'C(\d+)', row['claim_id'])
            if m and int(m.group(1)) >= EVENT_SUPPORT_FROM and row['event_type'] in ('command_change', 'activation', 'subordinate_assignment') \
                    and row['confidence'] and float(row['confidence']) <= 0.3 and 'Event support:' not in row['notes']:
                warn(where, 'low-confidence command row without an "Event support:" sentence in notes (confidence scores the location; say how well the event itself is documented)')
            ue, uw = unit_refs.check(row)
            for m in ue:
                err(where, m)
            for m in uw:
                warn(where, m)
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
    check_deferred_relations(units, vocabs, all_rows)
    check_operations(all_rows, vocabs)
    check_references(all_rows)
    check_claim_ids(all_rows)
    check_claim_keys(all_rows, claims_schema)
    place_rows = check_places(all_rows, vocabs)

    # ---- foreign keys declared in the schemas ----
    import build_references as br
    import operations as opsmod
    ops = opsmod.load()
    exc_path = os.path.join(common.ROOT, 'data', 'coordinate_exceptions.csv')
    tables = {'claims': all_rows, 'places': place_rows, 'units': list(units.values()), 'nationalities': list(nats.values()),
              'operations': ops.rows, 'operation_relations': ops.relations, 'operation_exceptions': ops.exceptions,
              'coordinate_exceptions': common.read_dicts(exc_path)[1] if os.path.isfile(exc_path) else [],
              'place_merges': placesmod.load_merges(),
              'retired_claims': common.read_dicts(RETIRED_CLAIMS_CSV)[1] if os.path.isfile(RETIRED_CLAIMS_CSV) else [],
              'claim_key_exceptions': common.read_dicts(CLAIM_KEY_EXCEPTIONS_CSV)[1] if os.path.isfile(CLAIM_KEY_EXCEPTIONS_CSV) else [],
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
