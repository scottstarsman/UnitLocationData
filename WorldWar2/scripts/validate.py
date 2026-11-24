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
every row has a source URL, the columns repeated from units.csv (unit_name, nationality, echelon, branch) equal the unit table (theater is per row and must match the row's operation).
Military symbol codes (scripts/sidc.py, roadmap 410): data/sidc_function_map.csv, data/sidc_echelon_map.csv and data/sidc_codes.csv match their schemas, every rule's codes
are in the code list, every echelon has an amplifier, every unit maps and every derived SIDC is 20 digits; a GZ99 fall-through and a claim with no side are warnings.
Nationalities (data/nationalities.csv): header, unique code and name, kind vocabulary, adjective set; every unit's nationality is a row of the table,
its unit_id prefix is the row's code and its claim folder is the lower-case name.
Unit references in claims (scripts/unit_refs.py, see schema/README.md): engaged_with and composing_units are `;` lists of unit_ids (or the sentinel `unknown` alone),
each a row of units.csv (foreign key), no duplicate, never the claiming unit itself, an opponent on the other side of the war on the claim date (data/nation_allegiance.csv and data/unit_allegiance_overrides.csv, scripts/allegiance.py); engaged_note
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
(probably several actions in one row) or hedged ("probably", "likely"), an engaged_with plus engaged_note list longer than three, and a
non-alternate claim dated before the unit's formed_date or after an end row or a lineage successor date (an activation after an end
starts a new life; absorbed_into is not the successor's formation; a 3-day tail after an end and a 7-day window around a lineage date
are allowed; see check_lifespan).
Errors also cover effective_time /
effective_to_time that are not HH:MM, location_date / location_temporal_offset_days / location_basis inconsistencies and a landing row whose coordinate is a
town centroid or a command post of another date.
Places (data/places.csv, schema/places.schema.json; scripts/places.py): header and field values, unique ids and names (ignoring case), sorted by place_id, no alias equal to another
place's name, coord_reference_id a gazetteer_geocoder reference that a claim at the place lists, every claim's place_id resolves, a claim's latitude/longitude equal the place's
exactly when coord_override is blank (and differ, within 5 km, when it is set), the coordinate note no longer ends `source`. A place with no claim is a warning.
Derived values are not stored (location_name, location_temporal_offset_days, strength_status, the roles of coordinate-service references; scripts/places.py,
scripts/build_references.py): a role row for a gazetteer_geocoder reference is an error; strength_json may carry `status` (full, reduced, heavily_depleted), which build/all_claims.csv turns into strength_status.
Commanders (data/people.csv, data/unit_commanders.csv, data/unit_commander_claims.csv; scripts/commanders.py):
header and field values from the schemas, unique PE#### / UC#### without gaps, vocabularies, date and conflict-group
rules (blank valid_to <=> open_at_last_claim), foreign keys, every named commander cell linked to a tenure, and unknown
commander cells linked only as asserts_end (a sourced vacancy).
TO&E (data/toe_templates.csv, data/unit_toe.csv; scripts/toe.py):
header and field values from the schemas, unique TT#### / UT#### without gaps, vocabularies (including formation_type,
authorized_count_key, authorized_structure_key and toe_conformance), date rules (blank valid_to <=> open), non-overlapping
assignments per unit, and authorized_strength_json keys restricted to the vocabularies. Authorized figures live on the
template, never on claims.

Coordinate checks live in scripts/check_coordinates.py.

Usage: python scripts/validate.py        (exit code 0 = OK, 1 = problems found; warnings do not count)
"""
import calendar
import collections
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
import commanders as commandersmod  # noqa: E402
import toe as toemod  # noqa: E402

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


def check_capabilities(where, caps, vocabs, listed=None, key_vocab='ship_capability_key', what='capabilities'):
    """A figure object (ship_classes.capabilities_json and the strength_json capabilities of a refit: keys from vocabulary ship_capability_key;
    aircraft_types.performance_json: keys from aircraft_performance_key, what='performance'), each {value, unit, reference_id, note} with a reference_id of
    data/references_meta.csv; `listed` (a set of reference ids), when given, must include them."""
    import build_references as br
    if not isinstance(caps, dict) or not caps:
        err(where, '%s must be a non-empty JSON object' % what)
        return
    known = {m['reference_id'] for m in br.read_meta()[1]}
    for k, fig in caps.items():
        if k not in vocabs[key_vocab]['values']:
            err(where, '%s: unknown key %r (vocabulary %s)' % (what, k, key_vocab))
        if not isinstance(fig, dict) or not isinstance(fig.get('value'), str) or not fig.get('value').strip():
            err(where, '%s[%r]: needs a non-empty string value' % (what, k))
            continue
        rid = fig.get('reference_id')
        if not isinstance(rid, str) or rid not in known:
            err(where, '%s[%r]: reference_id %r is not in data/references_meta.csv (a figure carries its own source; nothing is entered unsourced)' % (what, k, rid))
        elif listed is not None and rid not in listed:
            err(where, '%s[%r]: reference_id %s is not in the row reference_ids' % (what, k, rid))


def check_aircraft_strength(where, a, aircraft_types=None):
    """The aircraft object of strength_json (docs/air_naval_pilot.md section 9): {on_hand, serviceable, by_type: {type_id: {on_hand, serviceable}}}. on_hand is the
    aircraft the unit holds on the as_of date (Luftwaffe Iststaerke, USAAF aircraft assigned or possessed) and serviceable those ready for operations (Luftwaffe
    einsatzbereit, USAAF operational or in commission). Counts are non-negative integers; serviceable never exceeds on_hand; a by_type key is an aircraft
    type_id of data/aircraft_types.csv (the family row when a source gives no variant); the by_type counts add up to at most the totals (a source may
    leave some types unlisted); at least one count or one by_type row is needed."""
    w = where + ' strength_json aircraft'
    if not isinstance(a, dict) or not a:
        err(w, 'aircraft must be a non-empty JSON object')
        return
    for k in a:
        if k not in ('on_hand', 'serviceable', 'by_type'):
            err(w, 'unknown key %r (on_hand, serviceable, by_type)' % k)
    isn = lambda n: isinstance(n, int) and not isinstance(n, bool) and n >= 0   # noqa: E731
    for k in ('on_hand', 'serviceable'):
        if k in a and not isn(a[k]):
            err(w, '%s must be a non-negative integer' % k)
    if isn(a.get('on_hand')) and isn(a.get('serviceable')) and a['serviceable'] > a['on_hand']:
        err(w, 'serviceable %d exceeds on_hand %d' % (a['serviceable'], a['on_hand']))
    if 'by_type' not in a:
        if 'on_hand' not in a and 'serviceable' not in a:
            err(w, 'needs on_hand, serviceable and/or by_type')
        return
    bt = a['by_type']
    if not isinstance(bt, dict) or not bt:
        err(w, 'by_type must be a non-empty object {type_id: {on_hand, serviceable}}')
        return
    sums = {'on_hand': 0, 'serviceable': 0}
    for tid, e in bt.items():
        if not re.fullmatch(r'AT[0-9]{3,}', tid):
            err(w, 'by_type key %r is not a type_id AT###' % tid)
            continue
        if aircraft_types is not None and tid not in aircraft_types:
            err(w, 'by_type type_id %s is not in data/aircraft_types.csv' % tid)
        if not isinstance(e, dict) or not e:
            err(w, 'by_type[%s] must be a non-empty object {on_hand, serviceable}' % tid)
            continue
        for k in e:
            if k not in ('on_hand', 'serviceable'):
                err(w, 'by_type[%s]: unknown key %r' % (tid, k))
        for k in ('on_hand', 'serviceable'):
            if k in e:
                if not isn(e[k]):
                    err(w, 'by_type[%s].%s must be a non-negative integer' % (tid, k))
                else:
                    sums[k] += e[k]
        if isn(e.get('on_hand')) and isn(e.get('serviceable')) and e['serviceable'] > e['on_hand']:
            err(w, 'by_type[%s]: serviceable %d exceeds on_hand %d' % (tid, e['serviceable'], e['on_hand']))
    for k in ('on_hand', 'serviceable'):
        if isn(a.get(k)) and sums[k] > a[k]:
            err(w, 'by_type %s counts add up to %d, more than the total %s %d' % (k, sums[k], k, a[k]))


def check_strength_json(where, s, vocabs, aircraft_types=None):
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
    allowed = {'basis', 'as_of', 'personnel', 'vehicles', 'vehicle_count_type', 'scope', 'status', 'source', 'note', 'capabilities', 'aircraft'}
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
    if 'capabilities' in d:
        check_capabilities(where + ' strength_json capabilities', d['capabilities'], vocabs)
        if d.get('basis') != 'refit':
            err(where, 'strength_json: capabilities (a refit override of the class figures) needs basis refit')
    elif d.get('basis') == 'refit':
        err(where, 'strength_json: basis refit needs capabilities')
    if 'aircraft' in d:
        check_aircraft_strength(where, d['aircraft'], aircraft_types)
    if 'personnel' not in d and 'vehicles' not in d and 'status' not in d and 'capabilities' not in d and 'aircraft' not in d:
        err(where, 'strength_json: needs personnel, vehicles, status, capabilities and/or aircraft')
    if 'scope' in d:
        if d['scope'] not in vocabs['strength_json_scope']['values']:
            err(where, 'strength_json: scope %r not in vocabulary strength_json_scope' % (d['scope'],))
    elif 'personnel' in d:
        err(where, 'strength_json has personnel but no scope: set scope to whole_unit, sub_force or sector (what the figure covers), or remove the personnel figure if no source says')
    elif 'aircraft' in d:
        err(where, 'strength_json has aircraft but no scope: set scope to whole_unit, sub_force or sector (what the aircraft figures cover: a Geschwader return, one Gruppe, one detachment)')


SHIP_CLASSES_CSV = os.path.join(common.ROOT, 'data', 'ship_classes.csv')
AIRCRAFT_TYPES_CSV = os.path.join(common.ROOT, 'data', 'aircraft_types.csv')
REPEATED_COLUMNS = common.load_schema('claims')['repeatedColumns']['fields']   # claim columns that must equal data/units.csv
NAT_HEADER = ['code', 'name', 'adjective', 'alt_adjectives', 'kind', 'note']   # the `alliance` column was retired on 15 November 2026 (data/nation_allegiance.csv)

REL_KEYS = {'unit_id', 'relationship', 'effective_from', 'effective_from_latest', 'ordered_date', 'effective_to',
            'effective_to_earliest', 'effective_to_basis', 'date_basis', 'note', 'effective_time', 'effective_to_time'}
DATE_KEYS = ('effective_from', 'effective_from_latest', 'ordered_date', 'effective_to', 'effective_to_earliest')
# Single sources: schema/vocabularies.json (echelon_rank, relationship_groups, higher_than_organic, source_type)
STANDING_RELS = common.relationship_group('standing')
ACTIVE_RELS = common.relationship_group('active')
ECH_RANK = common.echelon_rank()
_LETTERS, NO_ID_LETTER, _CC = common.echelon_id_letters()
NAVAL_LADDER = frozenset(common.load_vocabularies()['echelon_id_letter']['naval_exempt'])   # naval_unit .. fleet: ranks 10-14, no id letter
AIR_LADDER = frozenset(common.load_vocabularies()['echelon_id_letter']['air_exempt'])   # air_flight .. air_force: ranks 19-25, no id letter
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
    class_cited = set()
    for csv_path in (SHIP_CLASSES_CSV, AIRCRAFT_TYPES_CSV):
        if os.path.isfile(csv_path):
            for r in common.read_dicts(csv_path)[1]:
                class_cited |= set(br.parse_ids(r.get('reference_ids', '')))
    allegiance_path = os.path.join(common.ROOT, 'data', 'nation_allegiance.csv')   # added 15 November 2026: its rows cite references too
    if os.path.isfile(allegiance_path):
        for r in common.read_dicts(allegiance_path)[1]:
            class_cited |= set(br.parse_ids(r.get('reference_ids', '')))
    for m in meta:
        st = stats[m['reference_id']]
        if not st['claims'] and not st['units'] and not st['ops'] and not st['missions'] and not st.get('commanders') and not st.get('toe') and m['reference_id'] not in class_cited:
            warn(where, '%s (%s) is not cited by any claim, unit, operation, mission, commander tenure, TO&E template or assignment, ship class, aircraft type or nation allegiance row: remove the row or cite it' % (m['reference_id'], m['short_title']))
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
    """data/operations.csv, operation_relations.csv, operation_exceptions.csv, operation_places.csv and every claim's operation_id (rules in scripts/operations.py;
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


ACTIVITY_COLS = ('activity_status', 'activity_basis', 'activity_span')


def check_activity(claims):
    """Activity pilot (docs/activity_status_design.md): the three activity columns are all blank or all set; a row with an activity has an
    `Activity:` sentence in notes; per unit, in date order, an `end` row closes an open span of the same value started by an earlier `start` row."""
    by_unit = {}
    for c in claims:
        vals = [c.get(k, '') for k in ACTIVITY_COLS]
        where = '%s %s' % (c['unit_id'], c['claim_id'])
        if any(vals) and not all(vals):
            err(where, 'activity_status, activity_basis and activity_span are set together or not at all')
            continue
        if not vals[0]:
            continue
        if not re.search(r'(^|[.!?] )Activity: ', c['notes']):
            err(where, 'a row with activity_status needs an `Activity:` sentence in notes (basis; old value, new value and reason for a changed row)')
        by_unit.setdefault(c['unit_id'], []).append(c)
    for unit, rows in by_unit.items():
        rows.sort(key=lambda c: (c['date'], c['claim_id']))
        open_status = None
        for c in rows:
            where = '%s %s' % (unit, c['claim_id'])
            st, span = c['activity_status'], c['activity_span']
            if span == 'start':
                open_status = st
            elif span == 'end':
                if open_status != st:
                    err(where, 'activity_span end of %r without an open %r span (open: %r); add the start row or use point' % (st, st, open_status))
                open_status = None


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


def sea_position_problem(place, claim):
    """Message when a claim at a sea_position place has a confidence above 0.5 (a point at sea is capped at 0.5); '' otherwise."""
    if place['kind'] == 'sea_position' and claim['confidence'] and float(claim['confidence']) > 0.5:
        return 'confidence %s at the sea_position place %s: a point at sea is capped at 0.5' % (claim['confidence'], place['place_id'])
    return ''


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
        if sea_position_problem(p, c):
            err(c['_where'], sea_position_problem(p, c))
        if re.search(r' ; coords?:', c['source']):
            err(c['_where'], "source ends with a coordinate note ('; coords: ...'): the note is the place's coord_source_note (or the claim's coord_override)")
    for d in out:
        if d['kind'] == 'sea_position' and not d['coord_source_note'].strip():
            err(d['_where'], 'a sea_position place needs a coord_source_note: say whether the position is stated or worked from an anchor, a distance and a bearing')
        cs = used.get(d['place_id'], [])
        if not cs:
            pass   # a place with no claims is accepted (Scott, 4 November 2026); the warning was removed
        elif d['coord_reference_id'] and not any(d['coord_reference_id'] in br.parse_ids(c['reference_ids']) for c in cs):
            err(d['_where'], 'coord_reference_id %s is not in the reference_ids of any claim at the place' % d['coord_reference_id'])
    return out


def check_ship_classes(nats, vocabs):
    """data/ship_classes.csv: header and field values from schema/ship_classes.schema.json; class_id SC### unique and sorted; class_name unique per
    nationality; nationality known; sub_type exactly when parent_class_id is set, the parent is a family row (not itself a sub-type) of the same ship_type;
    capabilities_json is a sourced capabilities object whose reference ids are listed in reference_ids and exist in references_meta; a sub-type row
    repeats only what differs from its family row. Returns {class_id: row}."""
    import build_references as br
    where = 'data/ship_classes.csv'
    sch = common.load_schema('ship_classes')
    fields = sch['fields']
    if not os.path.isfile(SHIP_CLASSES_CSV):
        err(where, 'missing (schema/ship_classes.schema.json)')
        return {}
    h, rows = common.read_rows(SHIP_CLASSES_CSV)
    if h != [f['name'] for f in fields]:
        err(where, 'header %s != schema/ship_classes.schema.json' % h)
        return {}
    meta = {m['reference_id'] for m in br.read_meta()[1]}
    out, ids, names = {}, [], {}
    for i, r in enumerate(rows, start=2):
        w = '%s line %d' % (where, i)
        if len(r) != len(h):
            err(w, 'expected %d fields, found %d' % (len(h), len(r)))
            continue
        d = dict(zip(h, r))
        d['_where'] = w
        check_row(w, d, fields, vocabs)
        ids.append(d['class_id'])
        if d['class_id'] in out:
            err(w, 'duplicate class_id %s' % d['class_id'])
        out[d['class_id']] = d
        k = (d['nationality'], d['class_name'].casefold())
        if k in names:
            err(w, 'class_name %r of %s is already the name of %s (names are unique within a nationality)' % (d['class_name'], d['nationality'], names[k]))
        names[k] = d['class_id']
        if d['nationality'] not in nats:
            err(w, 'nationality %r is not in data/nationalities.csv' % d['nationality'])
        if bool(d['parent_class_id']) != bool(d['sub_type']):
            err(w, 'parent_class_id and sub_type are set together (a sub-type has both; a family or single-row class has neither)')
        rids = [x.strip() for x in d['reference_ids'].split(';') if x.strip()]
        if not rids:
            err(w, 'reference_ids is empty: a class row rests on at least one reference')
        for rid in rids:
            if rid not in meta:
                err(w, 'reference_id %s is not in data/references_meta.csv' % rid)
        if d['capabilities_json']:
            try:
                caps = json.loads(d['capabilities_json'])
            except ValueError as e:
                err(w, 'capabilities_json is not valid JSON (%s)' % e)
            else:
                check_capabilities(w + ' capabilities_json', caps, vocabs, set(rids))
    if ids != sorted(ids):
        err(where, 'rows must be sorted by class_id')
    for d in out.values():
        pid = d['parent_class_id']
        if not pid:
            continue
        par = out.get(pid)
        if par is None:
            err(d['_where'], 'parent_class_id %s is not a class' % pid)
            continue
        if par['parent_class_id']:
            err(d['_where'], 'parent_class_id %s is itself a sub-type (one level: family and sub-type)' % pid)
        if par['ship_type'] != d['ship_type']:
            err(d['_where'], 'ship_type %s differs from the parent class %s (%s)' % (d['ship_type'], pid, par['ship_type']))
        try:
            a, b = json.loads(d['capabilities_json'] or '{}'), json.loads(par['capabilities_json'] or '{}')
        except ValueError:
            continue
        for k in a:
            if k in b and a[k].get('value') == b[k].get('value') and a[k].get('unit') == b[k].get('unit'):
                warn(d['_where'], 'capabilities[%r] repeats the family row %s: a sub-type row keeps only the figures that differ' % (k, pid))
    return out


def check_aircraft_types(nats, vocabs):
    """data/aircraft_types.csv: header and field values from schema/aircraft_types.schema.json; type_id AT### unique and sorted; designation unique per
    nationality; nationality known; variant exactly when parent_type_id is set, the parent is a family row (not itself a sub-type) (the role may differ);
    performance_json is a sourced figure object whose reference ids are listed in reference_ids and exist in references_meta; a sub-type row
    repeats only what differs from its family row. Returns {type_id: row}."""
    import build_references as br
    where = 'data/aircraft_types.csv'
    sch = common.load_schema('aircraft_types')
    fields = sch['fields']
    if not os.path.isfile(AIRCRAFT_TYPES_CSV):
        err(where, 'missing (schema/aircraft_types.schema.json)')
        return {}
    h, rows = common.read_rows(AIRCRAFT_TYPES_CSV)
    if h != [f['name'] for f in fields]:
        err(where, 'header %s != schema/aircraft_types.schema.json' % h)
        return {}
    meta = {m['reference_id'] for m in br.read_meta()[1]}
    out, ids, names = {}, [], {}
    for i, r in enumerate(rows, start=2):
        w = '%s line %d' % (where, i)
        if len(r) != len(h):
            err(w, 'expected %d fields, found %d' % (len(h), len(r)))
            continue
        d = dict(zip(h, r))
        d['_where'] = w
        check_row(w, d, fields, vocabs)
        ids.append(d['type_id'])
        if d['type_id'] in out:
            err(w, 'duplicate type_id %s' % d['type_id'])
        out[d['type_id']] = d
        k = (d['nationality'], d['designation'].casefold())
        if k in names:
            err(w, 'designation %r of %s is already the designation of %s (designations are unique within a nationality)' % (d['designation'], d['nationality'], names[k]))
        names[k] = d['type_id']
        if d['nationality'] not in nats:
            err(w, 'nationality %r is not in data/nationalities.csv' % d['nationality'])
        if bool(d['parent_type_id']) != bool(d['variant']):
            err(w, 'parent_type_id and variant are set together (a variant has both; a family or single-row type has neither)')
        rids = [x.strip() for x in d['reference_ids'].split(';') if x.strip()]
        if not rids:
            err(w, 'reference_ids is empty: an aircraft type row rests on at least one reference')
        for rid in rids:
            if rid not in meta:
                err(w, 'reference_id %s is not in data/references_meta.csv' % rid)
        if d['performance_json']:
            try:
                caps = json.loads(d['performance_json'])
            except ValueError as e:
                err(w, 'performance_json is not valid JSON (%s)' % e)
            else:
                check_capabilities(w + ' performance_json', caps, vocabs, set(rids), 'aircraft_performance_key', 'performance')
    if ids != sorted(ids):
        err(where, 'rows must be sorted by type_id')
    for d in out.values():
        pid = d['parent_type_id']
        if not pid:
            continue
        par = out.get(pid)
        if par is None:
            err(d['_where'], 'parent_type_id %s is not an aircraft type' % pid)
            continue
        if par['parent_type_id']:
            err(d['_where'], 'parent_type_id %s is itself a variant (one level: family and variant)' % pid)
        try:
            a, b = json.loads(d['performance_json'] or '{}'), json.loads(par['performance_json'] or '{}')
        except ValueError:
            continue
        for k in a:
            if k in b and a[k].get('value') == b[k].get('value') and a[k].get('unit') == b[k].get('unit'):
                warn(d['_where'], 'performance[%r] repeats the family row %s: a variant row keeps only the figures that differ' % (k, pid))
    return out


def check_naval_unit_columns(where, uid, u, classes):
    """Naval columns of a units.csv row: the naval ladder (naval_unit .. fleet) needs domain naval; ship_type, hull_number and ship_class_id belong to a
    unit with echelon naval_unit; the class must exist and its ship_type must equal the unit's; a naval_unit without ship_type is a warning."""
    ech = u['echelon']
    dom = u.get('domain') or 'ground'
    if ech in NAVAL_LADDER and dom != 'naval':
        err(where, 'echelon %s is on the naval ladder and needs domain naval (not %s)' % (ech, dom))
    if ech in AIR_LADDER and dom != 'air':
        err(where, 'echelon %s is on the air ladder and needs domain air (not %s)' % (ech, dom))
    if dom == 'air' and ech not in AIR_LADDER:
        warn(where, 'a unit of domain air with the ground echelon %s: use the air ladder (air_flight, air_squadron, air_group, air_wing, air_division, air_corps, air_force; '
                    'docs/air_naval_pilot.md section 9) so the hierarchy check applies' % ech)
    for col in ('ship_type', 'hull_number', 'ship_class_id'):
        if u.get(col) and ech != 'naval_unit':
            err(where, '%s is set but echelon is %s: ship_type, hull_number and ship_class_id belong to a unit with echelon naval_unit (a ship)' % (col, ech))
    if ech == 'naval_unit' and not u.get('ship_type'):
        warn(where, 'a ship (naval_unit) without ship_type: set it (vocabulary ship_type)')
    cid = u.get('ship_class_id')
    if cid:
        c = classes.get(cid)
        if c is None:
            err(where, 'ship_class_id %s is not a class in data/ship_classes.csv' % cid)
        elif u.get('ship_type') and u['ship_type'] != c['ship_type']:
            err(where, 'ship_type %s differs from the ship_type %s of class %s (%s)' % (u['ship_type'], c['ship_type'], cid, c['class_name']))
        elif not u.get('ship_type'):
            err(where, 'ship_class_id %s needs ship_type (the class is %s)' % (cid, c['ship_type']))


def check_nationalities():
    """data/nationalities.csv: header, unique code and name, vocabulary for kind, adjective set (the alliance column was retired on 15 November 2026)."""
    where = 'data/nationalities.csv'
    if not os.path.isfile(common.NATIONALITIES_CSV):
        err(where, 'missing')
        return {}
    header, rows = common.read_dicts(common.NATIONALITIES_CSV)
    if header != NAT_HEADER:
        err(where, 'header %s != %s' % (header, NAT_HEADER))
        return {}
    kinds = common.vocab_values('nationality_kind')
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
        for f in ('name', 'adjective', 'kind', 'note'):
            if not r[f].strip():
                err(w, '%s is empty' % f)
        if r['name'] != r['name'].strip() or r['name'] == 'All':
            err(w, "name %r is invalid ('All' is reserved for operation scopes)" % r['name'])
        if r['kind'] not in kinds:
            err(w, 'kind %r not in vocabulary nationality_kind %s' % (r['kind'], kinds))
    if [r['code'] for r in rows] != sorted(r['code'] for r in rows):
        err(where, 'rows must be sorted by code')
    return {r['name']: r for r in rows}


def check_foreign_keys(tables):
    """Enforce every foreignKeys entry declared in schema/claims.schema.json, units.schema.json and relations.schema.json, and the
    declared primary keys / unique columns of the side tables. `tables` maps resource name -> list of row dicts. A blank value is
    allowed (nullable reference); a column with a `separator` holds a list of keys; `alsoAllowed` lists extra accepted values."""
    decl = [(n, fk) for n in ('claims', 'units', 'places', 'ship_classes', 'aircraft_types', 'people', 'unit_commanders', 'unit_commander_claims', 'toe_templates', 'unit_toe') for fk in common.load_schema(n).get('foreignKeys', [])]
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


def naval_hierarchy_problem(su, hu, relationship):
    """Message when a command relation between two units of the naval ladder (naval_unit < naval_division < naval_squadron < task_group < fleet) puts a
    higher unit that does not outrank the subject; '' otherwise. A relation across ladders (a ship under an army, a battalion under a navy command) is not checked."""
    if su and hu and su['echelon'] in NAVAL_LADDER and hu['echelon'] in NAVAL_LADDER and ECH_RANK[hu['echelon']] <= ECH_RANK[su['echelon']] and relationship != 'unknown':
        return ('naval hierarchy: %s (%s) is under %s (%s); within the naval ladder (naval_unit < naval_division < naval_squadron < task_group < fleet) '
                'the higher unit must have the higher echelon rank' % (su['unit_id'], su['echelon'], hu['unit_id'], hu['echelon']))
    return ''


AIR_LATERAL = ('supporting', 'coordinating')   # relationships that are not subordination and so are not rank-checked


def air_hierarchy_problem(su, hu, relationship):
    """Message when a subordination between two units of the air ladder (air_flight < air_squadron < air_group < air_wing < air_division < air_corps < air_force) puts a
    higher unit that does not outrank the subject; '' otherwise. The rank follows the LEVEL, not the national name: a Gruppe, a US group and a RAF wing are
    air_group; a Geschwader, a US combat wing and a RAF group are air_wing, so a RAF group over a RAF wing and a US wing over a US group are both fine
    and a US group over a US wing is not. Supporting and coordinating are lateral and not checked; unknown is a placeholder. A relation across ladders
    (an air group under an army, a flak regiment under a Fliegerkorps) is not checked."""
    if (su and hu and su['echelon'] in AIR_LADDER and hu['echelon'] in AIR_LADDER and ECH_RANK[hu['echelon']] <= ECH_RANK[su['echelon']]
            and relationship != 'unknown' and relationship not in AIR_LATERAL):
        return ('air hierarchy: %s (%s) is under %s (%s); within the air ladder (air_flight < air_squadron < air_group < air_wing < air_division < air_corps < air_force) '
                'the higher unit must have the higher echelon rank (the level counts, not the name: a RAF wing is air_group, a RAF group is air_wing)' % (
                    su['unit_id'], su['echelon'], hu['unit_id'], hu['echelon']))
    return ''


def check_command_relation_tables(units, vocabs, claims):
    """data/command_relations.csv (master), data/command_relation_claims.csv (evidence join) and data/command_relation_overlaps.csv: headers and
    field values from schema/relations.schema.json; the interval rules (see schema/README.md, "Validity of a relationship"); the evidence agrees with
    the master; every contradictory overlap is documented. Keys and foreign keys are checked by check_foreign_keys."""
    sch = common.load_json(os.path.join(common.SCHEMA_DIR, 'relations.schema.json'))['tables']
    paths = {'command_relations': crel.REL_CSV, 'command_relation_claims': crel.LINK_CSV, 'command_relation_overlaps': crel.OVERLAP_CSV, 'command_relation_overrides': crel.OVERRIDE_CSV}
    for name, path in paths.items():
        where = os.path.relpath(path, common.ROOT).replace(os.sep, '/')
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
        else:
            problem = (naval_hierarchy_problem(units.get(r['subject_unit_id']), units.get(r['higher_unit_id']), r['relationship'])
                       or air_hierarchy_problem(units.get(r['subject_unit_id']), units.get(r['higher_unit_id']), r['relationship']))
            if problem:
                err(where, problem)
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
    # who_controls overrides (data/who_controls_overrides.csv): each names a preferred, non-organic relation whose subject has a preferred organic parent to answer instead
    ov_ids = [o['relation_id'] for o in rel.overrides]
    if ov_ids != sorted(ov_ids):
        err('data/who_controls_overrides.csv', 'rows must be sorted by relation_id')
    if len(ov_ids) != len(set(ov_ids)):
        err('data/who_controls_overrides.csv', 'a relation is listed twice')
    for o in rel.overrides:
        r = rel.by_id.get(o['relation_id'])
        if r is None:
            continue   # the foreign key check reports it
        if r['status'] != 'preferred' or r['relationship'] == 'organic':
            err('data/who_controls_overrides.csv', '%s must be a preferred, non-organic relation (it is %s %s)' % (o['relation_id'], r['status'], r['relationship']))
        if not any(x['subject_unit_id'] == r['subject_unit_id'] and x['relationship'] == 'organic' and x['status'] == 'preferred' for x in rel.rows):
            err('data/who_controls_overrides.csv', '%s: %s has no preferred organic relation to answer instead (defer_to_organic_parent would leave no answer)' % (o['relation_id'], r['subject_unit_id']))


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



LIFESPAN_END_GRACE_DAYS = 3
LIFESPAN_LINEAGE_GRACE_DAYS = 7


def _lifespan_date(s, pad='mid'):
    """Parse YYYY, YYYY-MM or YYYY-MM-DD. pad='mid' (audit D()) uses the 15th or 1 July;
    pad='end' uses the last day of the month or 31 December (after a lineage successor)."""
    s = (s or '').strip()
    if not s:
        return None
    if len(s) == 10:
        return datetime.date.fromisoformat(s)
    if len(s) == 7:
        y, m = int(s[:4]), int(s[5:])
        day = calendar.monthrange(y, m)[1] if pad == 'end' else 15
        return datetime.date(y, m, day)
    if len(s) == 4:
        return datetime.date(int(s), 12, 31) if pad == 'end' else datetime.date(int(s), 7, 1)
    return None


def is_end_row(row):
    """A claim that ends a life: destruction, or destroyed / disestablished set.
    Surrender alone is not an end: many surrender rows record an enemy capitulation
    the unit accepted, not the unit's own end (consistency-fix-1 audit)."""
    return row['event_type'] == 'destruction' or row['destroyed'] == 'true' or row['disestablished'] == 'true'


def lifespan_issues(units, claims, lineage_rows=None):
    """Return one dict per non-alternate claim that falls outside the unit's life.

    Port of the consistency-fix-1 audit (scratch life2.py, 9 November 2026):
    - ignore claim_status alternate (kept on purpose in a conflict group);
    - an activation row after an end row starts a new life (re-formation);
    - an absorbed_into lineage link is not read as the successor's formation;
    - a 3-day tail after an end row and a 7-day window around a lineage date
      are allowed (month-precision lineage dates expand to the last day of the
      month when testing 'after the successor').
    Does not change the validator exit code; check_lifespan emits WARNING lines.
    """
    import lineage as _lineage
    if lineage_rows is None:
        _h, lineage_rows = _lineage.load()
    by_unit = collections.defaultdict(list)
    pref = collections.defaultdict(list)
    for c in claims:
        by_unit[c['unit_id']].append(c)
        if c['claim_status'] == 'preferred':
            pref[c['unit_id']].append(c)
    for v in by_unit.values():
        v.sort(key=lambda c: (c['date'], c['claim_id']))
    for v in pref.values():
        v.sort(key=lambda c: (c['date'], c['claim_id']))

    issues = []

    def add(unit_id, claim, reason, life_start, life_end, detail):
        issues.append({
            'unit_id': unit_id,
            'claim_id': claim['claim_id'],
            'date': claim['date'],
            'reason': reason,
            'life_start': life_start,
            'life_end': life_end,
            'detail': detail,
        })

    for unit_id, rows in by_unit.items():
        unit = units.get(unit_id)
        if not unit:
            continue
        formed = unit.get('formed_date') or ''
        if formed:
            for c in rows:
                if c['claim_status'] == 'alternate':
                    continue
                if c['date'] < formed and c['event_type'] != 'activation':
                    add(unit_id, c, 'before_formed_date', formed, None,
                        'before formed_date %s' % formed)

        ends = [c for c in pref[unit_id] if is_end_row(c)]
        if ends:
            end = min(ends, key=lambda c: (c['date'], c['claim_id']))
            later = [c for c in pref[unit_id] if c['date'] > end['date']]
            react = [c for c in later if c['event_type'] == 'activation']
            if react:
                later = [c for c in later if c['date'] < react[0]['date']]
            end_d = _lifespan_date(end['date'])
            kind = end['event_type'] if end['event_type'] != 'other' else (
                'destroyed' if end['destroyed'] == 'true' else 'disestablished')
            for c in later:
                if (_lifespan_date(c['date']) - end_d).days > LIFESPAN_END_GRACE_DAYS:
                    add(unit_id, c, 'after_end_row', None, end['date'],
                        'after end row %s %s (%s)' % (end['claim_id'], end['date'], kind))

        for link in lineage_rows:
            if link['predecessor_unit_id'] != unit_id:
                continue
            sd = _lifespan_date(link['effective_date'], pad='end')
            if not sd:
                continue
            later = [c for c in pref[unit_id] if c['date'] > sd.isoformat()
                     and (_lifespan_date(c['date']) - sd).days > LIFESPAN_LINEAGE_GRACE_DAYS]
            react = [c for c in later if c['event_type'] == 'activation']
            if react:
                later = [c for c in later if c['date'] < react[0]['date']]
            life_end = sd.isoformat()
            for c in later:
                add(unit_id, c, 'after_lineage_successor', None, life_end,
                    'more than %d days after lineage successor %s from %s (%s)' % (
                        LIFESPAN_LINEAGE_GRACE_DAYS, link['successor_unit_id'],
                        life_end, link['lineage_id']))

        for link in lineage_rows:
            if link['successor_unit_id'] != unit_id or link['kind'] == 'absorbed_into':
                continue
            mid = _lifespan_date(link['effective_date'], pad='mid')
            if not mid:
                continue
            earlier = [c for c in pref[unit_id]
                       if (mid - _lifespan_date(c['date'])).days > LIFESPAN_LINEAGE_GRACE_DAYS]
            for c in earlier:
                add(unit_id, c, 'before_lineage_formation', link['effective_date'], None,
                    'more than %d days before formation from %s on %s (%s, %s)' % (
                        LIFESPAN_LINEAGE_GRACE_DAYS, link['predecessor_unit_id'],
                        link['effective_date'], link['lineage_id'], link['kind']))
    issues.sort(key=lambda x: (x['unit_id'], x['date'], x['claim_id'], x['reason']))
    return issues


def check_lifespan(units, claims):
    """Warning-only lifespan check; never changes the exit code."""
    for issue in lifespan_issues(units, claims):
        bounds = []
        if issue['life_start']:
            bounds.append('life starts %s' % issue['life_start'])
        if issue['life_end']:
            bounds.append('life ended %s' % issue['life_end'])
        warn('%s %s' % (issue['unit_id'], issue['claim_id']),
             'dated %s, %s (%s)' % (issue['date'], issue['detail'],
                                    '; '.join(bounds) if bounds else 'life bounds unknown'))


def check_lineage(units, vocabs):
    """data/unit_lineage.csv (scripts/lineage.py): header, ids, unit ids exist, kind and date basis in the vocabularies, real dates
    not before the predecessor's formed_date, references exist, no duplicate pair, no cycle, both linked units' unit_note names the other."""
    import lineage
    import csv as _csv
    with open(os.path.join(common.ROOT, 'data', 'references_meta.csv'), newline='', encoding='utf-8') as fh:
        ref_ids = {r['reference_id'] for r in _csv.DictReader(fh)}
    h, rows = lineage.load()
    for where, msg in lineage.check(h, rows, units, vocabs, ref_ids):
        err(where, msg)


def check_allegiance(units, vocabs):
    """data/nation_allegiance.csv (scripts/allegiance.py): header, nation codes exist and are nations, side and conflict in the vocabularies,
    real dates inside the conflict, references exist, rows of one nation do not overlap, every nation has a row; and
    data/unit_allegiance_overrides.csv: unit exists, side valid, real dates inside WW2, no overlap per unit, references exist."""
    import allegiance
    import csv as _csv
    with open(os.path.join(common.ROOT, 'data', 'references_meta.csv'), newline='', encoding='utf-8') as fh:
        ref_ids = {r['reference_id'] for r in _csv.DictReader(fh)}
    h, rows = allegiance.load()
    nats = {n['code']: n for n in common.load_nationalities()}
    for where, msg in allegiance.check(h, rows, nats, vocabs, ref_ids):
        err(where, msg)
    oh, orows = allegiance.load_overrides()
    for where, msg in allegiance.check_overrides(oh, orows, units, vocabs, ref_ids):
        err(where, msg)


def check_sidc(units, claims):
    """Military symbol codes (roadmap 410, scripts/sidc.py): the three tables match their schemas; every rule compiles, uses vocabulary values and codes of
    data/sidc_codes.csv (entity in its symbol set, modifiers); every echelon value has a two-digit amplifier; every unit matches a rule and every derived
    SIDC is 20 digits (errors). A unit that falls through to GZ99 (unspecified) and a claim with no side on its date (standard identity Unknown) are warnings."""
    import sidc
    errs, warns = sidc.check(units, claims)
    for where, msg in errs:
        err(where, msg)
    for where, msg in warns:
        warn(where, msg)


MISSION_START = '1939-09-01'
TIME_RE = re.compile(r'([01][0-9]|2[0-3]):[0-5][0-9]')


def mission_base_gaps(units, claims, missions, relations):
    """{unit_id: [mission rows]} of missions whose unit (or, when the unit has no claims, its organic parent on the day) has no base claim in force on
    the mission date: the latest non-alternate claim on or before the date must have location_represents base. A month-only date is read as the last
    day of the month. Used by check_missions (warning) and the semantic tests."""
    by_unit = {}
    for c in claims:
        if c['claim_status'] != 'alternate':
            by_unit.setdefault(c['unit_id'], []).append(c)
    for rs in by_unit.values():
        rs.sort(key=lambda c: (c['date'], c['claim_id']))
    organic = {}
    for r in relations:
        if r['relationship'] == 'organic' and r['higher_unit_id']:
            organic.setdefault(r['subject_unit_id'], []).append(r)
    out = {}
    for m in missions:
        d = m['date'] if len(m['date']) == 10 else m['date'] + '-31'
        uid = m['unit_id']
        if uid not in by_unit:
            for r in organic.get(uid, []):
                if (not r['valid_from'] or r['valid_from'] <= d) and (not r['valid_to'] or d <= r['valid_to']):
                    uid = r['higher_unit_id']
                    break
        before = [c for c in by_unit.get(uid, []) if c['date'] <= d]
        if not before or before[-1]['location_represents'] != 'base':
            out.setdefault(m['unit_id'], []).append(m)
    return out


def check_missions(units, claims, place_rows, aircraft, vocabs, relset):
    """data/missions/<nationality folder>/<unit_id>.csv and data/retired_missions.csv (schema/missions.schema.json, decision J1; scripts/missions.py):
    header and field values (types, patterns, vocabularies mission_status, mission_type, mission_target_category, confidence); the file path and the
    unit (domain air, file name, nationality folder); unique MSN ids that are not retired; rows sorted by date then mission_id; a real date not before
    1939-09-01 (YYYY-MM allowed); HH:MM times; integer counts with aircraft_effective and aircraft_lost not above aircraft_dispatched; status and
    conflict group paired (an alternate needs a G id; a group has two or more rows of one unit and one preferred row; a G id is not also a claim group);
    supported and attacked units exist, are not the flying unit and are not repeated; a target at a sea_position place is at most 0.5; every source URL
    is the url of one of the row's reference_ids and every reference id exists; source_locator names only the row's references; note labels; hedge
    words in notes (warning); an operation whose dates do not cover the mission (warning); a mission with no base claim of its unit in force that day
    (warning, one per unit); the foreignKeys of the schema (unit, target place, aircraft type, supported and attacked units, operation, references); a
    place used only by missions has its coord_reference_id among those missions' references. Returns the mission rows (dicts with _where)."""
    import missions as msmod
    import build_references as br
    sch = common.load_schema('missions')
    fields = sch['fields']
    header = [f['name'] for f in fields]
    out = []
    seen = {}
    nat_folder = {u['unit_id']: u['nationality'].lower() for u in units.values()}
    for path in msmod.files():
        r_path = rel(path)
        parts = r_path.split(os.sep)
        if len(parts) != 4 or parts[:2] != ['data', 'missions']:
            err(r_path, 'mission files must be data/missions/<nationality>/<unit_id>.csv')
            continue
        folder, stem = parts[2], parts[3][:-4]
        h, rows = common.read_rows(path)
        if h != header:
            err(r_path, 'header does not match schema/missions.schema.json (expected %s)' % header)
            continue
        u = units.get(stem)
        if u is None:
            err(r_path, 'unit_id %s (file name) not in data/units.csv' % stem)
        else:
            if (u.get('domain') or 'ground') != 'air':
                err(r_path, 'unit %s has domain %s: missions belong to a unit of domain air' % (stem, u.get('domain') or 'ground'))
            if nat_folder[stem] != folder:
                err(r_path, 'folder %s does not match unit nationality %s' % (folder, u['nationality']))
        if not rows:
            err(r_path, 'file has no rows')
        prev = None
        for i, r in enumerate(rows, start=2):
            where = '%s line %d' % (r_path, i)
            if len(r) != len(header):
                err(where, 'expected %d fields, found %d' % (len(header), len(r)))
                continue
            row = dict(zip(header, r))
            row['_where'] = where
            check_row(where, row, fields, vocabs)
            mid = row['mission_id']
            if mid in seen:
                err(where, 'duplicate mission_id %s (also in %s)' % (mid, seen[mid]))
            seen[mid] = r_path
            if row['unit_id'] != stem:
                err(where, 'unit_id %s does not match file name %s' % (row['unit_id'], stem))
            if row['date'] and not valid_partial_date(row['date']):
                err(where, 'date %r is not a real YYYY-MM-DD or YYYY-MM' % row['date'])
            elif row['date'] and row['date'] < MISSION_START[:len(row['date'])]:
                err(where, 'date %s is before %s' % (row['date'], MISSION_START))
            k = msmod.sort_key(row)
            if prev and k < prev:
                err(where, 'rows must be sorted by date then mission_id')
            prev = k
            n = {}
            for c in ('aircraft_dispatched', 'aircraft_effective', 'aircraft_lost'):
                if row[c] != '':
                    if re.fullmatch(r'[0-9]+', row[c]):
                        n[c] = int(row[c])
                    else:
                        err(where, '%s %r is not a whole number' % (c, row[c]))
            for c in ('aircraft_effective', 'aircraft_lost'):
                if c in n and 'aircraft_dispatched' in n and n[c] > n['aircraft_dispatched']:
                    err(where, '%s %d is more than aircraft_dispatched %d' % (c, n[c], n['aircraft_dispatched']))
            if row['mission_status'] == 'alternate' and not row['conflict_group_id']:
                err(where, 'mission_status alternate requires a conflict_group_id')
            for c in ('supported_unit_ids', 'attacked_unit_ids'):
                toks = [t.strip() for t in row[c].split(';') if t.strip()]
                if row[c] and row[c] != '; '.join(toks):
                    err(where, '%s must be unit ids joined by "; "' % c)
                if len(toks) != len(set(toks)):
                    err(where, '%s lists a unit twice' % c)
                if row['unit_id'] in toks:
                    err(where, '%s lists the flying unit itself' % c)
            if set(t.strip() for t in row['supported_unit_ids'].split(';') if t.strip()) & set(t.strip() for t in row['attacked_unit_ids'].split(';') if t.strip()):
                err(where, 'a unit is both supported and attacked')
            if not re.search(r'https?://', row['source']):
                err(where, 'source must contain at least one URL')
            check_note_labels(where, row, vocabs['note_label']['values'])
            if HEDGE_WORDS.search(row['notes']):
                warn(where, 'notes contain a hedge word (%s): state only what the source documents' % HEDGE_WORDS.search(row['notes']).group(0))
            out.append(row)
    # retired ids
    if not os.path.isfile(msmod.RETIRED_CSV):
        err('data/retired_missions.csv', 'missing (header %s)' % ','.join(msmod.RETIRED_HEADER))
    else:
        h, rrows = common.read_dicts(msmod.RETIRED_CSV)
        if h != msmod.RETIRED_HEADER:
            err('data/retired_missions.csv', 'header %s != %s' % (h, msmod.RETIRED_HEADER))
        for i, d in enumerate(rrows, start=2):
            w = 'data/retired_missions.csv line %d' % i
            if not re.fullmatch(r'MSN\d{4,}', d.get('mission_id', '')):
                err(w, 'mission_id %r is not a mission id (MSN0001 onward)' % d.get('mission_id'))
            if d.get('mission_id') in seen:
                err(w, '%s is retired but is also a mission: a retired id is never reused' % d['mission_id'])
            if d.get('replaced_by_mission_id') and d['replaced_by_mission_id'] not in seen:
                err(w, 'replaced_by_mission_id %s is not a mission' % d['replaced_by_mission_id'])
            if not d.get('reason', '').strip():
                err(w, 'reason is blank')
    # conflict groups (shared G numbering with the claims)
    claim_groups = {c['conflict_group_id'] for c in claims if c['conflict_group_id']}
    groups = {}
    for m in out:
        if m['conflict_group_id']:
            groups.setdefault(m['conflict_group_id'], []).append(m)
    for g, ms in sorted(groups.items()):
        where = 'mission conflict group %s' % g
        if g in claim_groups:
            err(where, '%s is also a claim conflict group: a G id is one group, of claims or of missions' % g)
        if len(ms) < 2:
            err(where, 'a conflict group needs at least two missions')
        if len({m['unit_id'] for m in ms}) != 1:
            err(where, 'all missions of a group must be of the same unit_id')
        if [m['mission_status'] for m in ms].count('preferred') != 1:
            err(where, 'a mission conflict group has exactly one preferred row')
        if not any('Conflict' in m['notes'] or 'Review' in m['notes'] for m in ms):
            warn(where, 'no row says what differs (a "Review:" sentence)')
    # places, references, operations
    places = {p['place_id']: p for p in place_rows}
    _h, meta = br.read_meta()
    by_url = {m['url']: m['reference_id'] for m in meta if m['url']}
    ref_ids = {m['reference_id'] for m in meta}
    import operations as opsmod
    ops = opsmod.load()
    for m in out:
        w = m['_where']
        p = places.get(m['target_place_id'])
        if p is not None and p['kind'] == 'sea_position' and m['confidence'] and is_number(m['confidence']) and float(m['confidence']) > 0.5:
            err(w, 'target %s is a sea_position: confidence is at most 0.5' % p['place_id'])
        ids = br.parse_ids(m['reference_ids'])
        if not ids:
            err(w, 'reference_ids: at least one reference is required')
        if len(ids) != len(set(ids)):
            err(w, 'reference_ids lists a reference twice')
        urls, _note = br.split_source(m['source'])
        for raw in urls:
            u, _frag = br.norm_url(raw)
            rid = by_url.get(u)
            if rid is None:
                err(w, 'source URL %s has no row in data/references_meta.csv' % u)
            elif rid not in ids:
                err(w, 'source URL %s is reference %s, which is not in reference_ids' % (u, rid))
        locs, bad = br.parse_locators(m['source_locator'])
        for b in bad:
            err(w, 'source_locator part %r is not "R###: locator"' % b)
        for rid in locs:
            if rid not in ids:
                err(w, 'source_locator names %s, which is not in reference_ids' % rid)
        if m['operation_id'] and m['operation_id'] in ops.by_id and len(m['date']) == 10:
            o = ops.by_id[m['operation_id']]
            if o['start_date'] and o['end_date'] and not (o['start_date'] <= m['date'] <= o['end_date']):
                warn(w, 'mission date %s is outside operation %s (%s to %s)' % (m['date'], m['operation_id'], o['start_date'], o['end_date']))
    claim_places = {c['place_id'] for c in claims}
    for pid in sorted({m['target_place_id'] for m in out if m['target_place_id']} - claim_places):
        p = places.get(pid)
        if p is not None and p['coord_reference_id'] and not any(p['coord_reference_id'] in br.parse_ids(m['reference_ids']) for m in out if m['target_place_id'] == pid):
            err(p['_where'], 'coord_reference_id %s is not in the reference_ids of any claim or mission at the place' % p['coord_reference_id'])
    # foreign keys declared in schema/missions.schema.json (enforced here rather than in check_foreign_keys, so that a synthetic test can run them)
    keysets = {'units': set(units), 'places': set(places), 'aircraft_types': set(aircraft), 'operations': set(ops.by_id), 'references_meta': ref_ids}
    for fk in sch.get('foreignKeys', []):
        allowed = keysets[fk['reference']['resource']]
        for m in out:
            v = m.get(fk['fields'], '')
            for tok in ([t.strip() for t in v.split(fk['separator']) if t.strip()] if fk.get('separator') else ([v] if v else [])):
                if tok not in allowed:
                    err(m['_where'], 'foreign key missions.%s = %r is not a %s.%s' % (fk['fields'], tok, fk['reference']['resource'], fk['reference']['fields']))
    for uid, ms in sorted(mission_base_gaps(units, claims, out, relset.rows).items()):
        warn('data/missions unit %s' % uid, '%d mission(s) fall on a date with no base claim of the unit (or of its organic parent) in force: %s; '
             'the base of the day is not recorded' % (len(ms), ', '.join('%s (%s)' % (m['mission_id'], m['date']) for m in ms)))
    return out



def check_toe(units, vocabs, nats):
    """data/toe_templates.csv and data/unit_toe.csv (scripts/toe.py)."""
    import build_references as br
    ref_ids = {m['reference_id'] for m in br.read_meta()[1]} if os.path.isfile(br.META_CSV) else set()
    nat_names = {n['name'] for n in nats.values()} if isinstance(nats, dict) else {n['name'] for n in nats}
    th, templates = toemod.load_templates()
    ah, assignments = toemod.load_assignments()
    for where, msg in toemod.check(th, templates or [], ah, assignments or [], units, vocabs, ref_ids, nat_names):
        if msg.startswith(toemod.WARNING_PREFIX):
            warn(where, msg[len(toemod.WARNING_PREFIX):])
        else:
            err(where, msg)
    return templates or [], assignments or []


def check_commanders(units, vocabs, claims, nats):
    """data/people.csv, data/unit_commanders.csv and data/unit_commander_claims.csv (scripts/commanders.py)."""
    import build_references as br
    ref_ids = {m['reference_id'] for m in br.read_meta()[1]} if os.path.isfile(br.META_CSV) else set()
    nat_names = {n['name'] for n in nats.values()} if isinstance(nats, dict) else {n['name'] for n in nats}
    ph, people = commandersmod.load_people()
    th, tenures = commandersmod.load_tenures()
    lh, links = commandersmod.load_links()
    for where, msg in commandersmod.check(ph, people, th, tenures, lh, links, units, claims, vocabs, ref_ids, nat_names):
        err(where, msg)
    return people, tenures, links


def main():
    claims_schema = common.load_schema('claims')
    units_schema = common.load_schema('units')
    vocabs = common.load_vocabularies()
    cfields = claims_schema['fields']
    cheader = [f['name'] for f in cfields]
    ufields = units_schema['fields']
    uheader = [f['name'] for f in ufields]

    nats = check_nationalities()
    classes = check_ship_classes(nats, vocabs)
    aircraft = check_aircraft_types(nats, vocabs)

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
            if u.get('domain', '') not in ('ground', 'air', 'naval'):
                err(where, 'domain %r must be ground, air or naval (blank is no longer allowed; Task 4 / RP3)' % u['domain'])
            check_naval_unit_columns(where, uid, u, classes)
            nat = nats.get(u['nationality'])
            if nat and uid.split('-')[0] != nat['code']:
                err(where, 'unit_id prefix %s is not the code %s of nationality %s' % (uid.split('-')[0], nat['code'], u['nationality']))
            # echelon letter (vocabulary echelon_id_letter): an id ending in digits and G, A, C, D, B or H must have that echelon; regiments, battle groups and battalions have no letter
            lm = re.search(r'[0-9]([A-Z])$', uid)
            if lm and lm.group(1) in ID_LETTER_ECHELON and ID_LETTER_ECHELON[lm.group(1)] != u['echelon'] and not (u['echelon'] in NO_ID_LETTER and COMBAT_COMMAND_ID.match(uid)) and u['echelon'] not in NAVAL_LADDER and u['echelon'] not in AIR_LADDER:
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
            check_strength_json(where, row['strength_json'], vocabs, aircraft)
            if u and u['echelon'] == 'naval_unit':
                if row['event_type'] == 'redesignation' and not re.search(r'[Rr]eclassified from \S+ to \S+', row['notes']):
                    warn(where, 'a redesignation row of a ship: state a reclassification as "Reclassified from <old type or hull code> to <new>" in notes (docs/air_naval_pilot.md section 6.5)')
            elif u and row['strength_json'] and '"capabilities"' in row['strength_json']:
                err(where, 'strength_json capabilities (a refit) belongs to a unit with echelon naval_unit')
            if u and row['strength_json'] and '"aircraft"' in row['strength_json'] and (u.get('domain') or 'ground') != 'air':
                err(where, 'strength_json aircraft (aircraft on hand and serviceable, by type) belongs to a unit of domain air')
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
    check_activity(all_rows)
    check_claim_keys(all_rows, claims_schema)
    place_rows = check_places(all_rows, vocabs)
    check_lineage(units, vocabs)
    people_rows, tenure_rows, commander_links = check_commanders(units, vocabs, all_rows, nats)
    template_rows, assignment_rows = check_toe(units, vocabs, nats)
    check_allegiance(units, vocabs)
    check_sidc(units, all_rows)
    check_lifespan(units, all_rows)
    mission_rows = check_missions(units, all_rows, place_rows, aircraft, vocabs, relset)

    # ---- foreign keys declared in the schemas ----
    import build_references as br
    import operations as opsmod
    ops = opsmod.load()
    exc_path = os.path.join(common.ROOT, 'data', 'coordinate_exceptions.csv')
    tables = {'claims': all_rows, 'places': place_rows, 'units': list(units.values()), 'nationalities': list(nats.values()), 'ship_classes': list(classes.values()), 'aircraft_types': list(aircraft.values()),
              'operations': ops.rows, 'operation_relations': ops.relations, 'operation_exceptions': ops.exceptions, 'operation_places': ops.places,
              'coordinate_exceptions': common.read_dicts(exc_path)[1] if os.path.isfile(exc_path) else [],
              'place_merges': placesmod.load_merges(),
              'retired_claims': common.read_dicts(RETIRED_CLAIMS_CSV)[1] if os.path.isfile(RETIRED_CLAIMS_CSV) else [],
              'claim_key_exceptions': common.read_dicts(CLAIM_KEY_EXCEPTIONS_CSV)[1] if os.path.isfile(CLAIM_KEY_EXCEPTIONS_CSV) else [],
              'references_meta': br.read_meta()[1] if os.path.isfile(br.META_CSV) else [],
              'claim_reference_roles': br.read_roles()[1] if os.path.isfile(br.ROLES_CSV) else [],
              'command_relations': relset.rows, 'command_relation_claims': relset.links, 'command_relation_overlaps': relset.overlaps, 'command_relation_overrides': relset.overrides,
              'people': people_rows, 'unit_commanders': tenure_rows, 'unit_commander_claims': commander_links,
              'toe_templates': template_rows, 'unit_toe': assignment_rows}
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
    print('OK: %d claim files, %d claims, %d units, %d conflict groups, %d missions' % (len(files), len(all_rows), len(units), len(groups), len(mission_rows)))
    return 0


if __name__ == '__main__':
    sys.exit(main())
