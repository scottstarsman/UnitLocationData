"""Reproduce the coordinates of a 12th Army Group map reading.

usage: python3 pixel_to_latlon.py SHEET PX PY
SHEET is a scan id (e.g. cs000289), PX/PY the full-resolution pixel of the symbol centre.
Weekly sheets after cs000099 are first mapped onto cs000099 with the affine transform in
sheetG_registration.json (x' = x[0]*px + x[1]*py + x[2], same for y), then converted with the
town-control fit of the base sheet (sheetG_control.json). Base sheets with their own control file
(sheet3, sheetB-sheetF) are converted directly.
"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import georef as g
D = os.path.dirname(os.path.abspath(__file__))
BASE = {'cs000064': 'sheetB_control.json', 'cs000071': 'sheetC_control.json', 'cs000078': 'sheetD_control.json',
        'cs000085': 'sheetE_control.json', 'cs000092': 'sheetF_control.json', 'cs000099': 'sheetG_control.json'}

def latlon(sheet, px, py):
    reg = json.load(open(os.path.join(D, 'sheetG_registration.json')))
    if sheet in reg:
        r = reg[sheet]; x, y = r['x'], r['y']
        px, py = int(round(x[0] * px + x[1] * py + x[2])), int(round(y[0] * px + y[1] * py + y[2])); sheet = r['reference']
    if sheet not in BASE:
        raise SystemExit(f'{sheet}: no registration; the June-July sheets use sheet3_control.json via georef.register')
    lo, la = g.Fit(json.load(open(os.path.join(D, BASE[sheet])))['control'], 1)(px, py)
    return round(la, 4), round(lo, 4)

if __name__ == '__main__':
    print(*latlon(sys.argv[1], int(sys.argv[2]), int(sys.argv[3])))
