"""Name rules for new gazetteer candidates of the 12th Army Group map pass (added 1 November 2026).

1. prefer_municipality: if a GeoNames municipality seat (PPLA, PPLA2-4, PPLC) lies within 1.5 km of
   the candidate point, the candidate takes the municipality name rather than the district name
   returned by reverse geocoding (case: central Roetgen was named "Rott", a district of Roetgen).
2. guard: a candidate whose name equals an existing places.csv row but lies more than 3 km from it
   is not merged into that row; it is renamed "<name> (<nearest municipality>)" (or "<name> (2)")
   and becomes a new place.
GeoNames dumps (reference R782) are read from GEONAMES_DIR (default /workspace/geonames); they are
not part of the repository.
"""
import csv, math, os, pickle
GD = os.environ.get('GEONAMES_DIR', '/workspace/geonames')
SEATS = ('PPLA', 'PPLA2', 'PPLA3', 'PPLA4', 'PPLC')
_S = None

def km(a, b, c, d):
    r = math.radians
    return 6371 * 2 * math.asin(math.sqrt(math.sin(r(c - a) / 2) ** 2 + math.cos(r(a)) * math.cos(r(c)) * math.sin(r(d - b) / 2) ** 2))

def _seats():
    global _S
    if _S is None:
        pk = os.path.join(GD, 'seats.pkl')
        if os.path.exists(pk):
            _S = pickle.load(open(pk, 'rb'))
        else:
            _S = []
            for c in ('NL', 'BE', 'LU', 'DE', 'FR'):
                for l in open(os.path.join(GD, f'{c}.txt'), encoding='utf-8'):
                    f = l.rstrip('\n').split('\t')
                    if f[6] == 'P' and f[7] in SEATS:
                        _S.append((float(f[4]), float(f[5]), f[1], f[0]))
            pickle.dump(_S, open(pk, 'wb'))
    return _S

def nearest_seat(la, lo, r):
    best = None
    for a, b, n, i in _seats():
        if abs(a - la) < 0.1 and abs(b - lo) < 0.15:
            d = km(la, lo, a, b)
            if d <= r and (best is None or d < best[0]):
                best = (d, n, i)
    return best

def prefer_municipality(town, la, lo, r=1.5):
    s = nearest_seat(la, lo, r)
    return (s[1], s[2]) if s and s[1] != town else (town, None)

def guard(cands, places_csv, limit=3.0):
    """cands: list of dicts with name, latitude, longitude. Renames in place; returns {old: new}."""
    P = {}
    for r in csv.DictReader(open(places_csv)):
        P[r['name']] = (float(r['latitude']), float(r['longitude']))
    ren = {}
    for p in cands:
        if p['name'] in P:
            d = km(float(p['latitude']), float(p['longitude']), *P[p['name']])
            if d > limit:
                base, _, reg = p['name'].partition(', ')
                s = nearest_seat(float(p['latitude']), float(p['longitude']), 5.0)
                tag = s[1] if s and s[1] != base else '2'
                new = f'{base} ({tag}), {reg}' if reg else f'{base} ({tag})'
                ren[p['name']] = new
                p['coord_source_note'] = p.get('coord_source_note', '') + f'; not merged into the existing place "{p["name"]}" ({d:.1f} km away, more than {limit:g} km)'
                p['name'] = new
    return ren
