# 12th Army Group situation maps: helper files

Helpers for reading the Library of Congress series *HQ 12th Army Group situation maps*
(https://www.loc.gov/item/2001628569/, public domain, 416 daily sheets, 6 June 1944 to 26 July 1945; reference `R781`).
They are working tools for the map pass, not part of the build or the checks. The map images are not committed:
download them from the Library of Congress IIIF service into a scratch folder outside the repository.

- `sheet_index.csv`: every sheet sorted by its situation date (`date`, LoC image id `sheet_id`, a half-size IIIF image link,
  `weekly_pass1` = 1 for the weekly sheets of the first pass, 6 June 1944 then every seventh day to 8 May 1945, plus 9 May 1945).
  The series has one sheet for every day from 6 June 1944 to 26 July 1945; no day is missing.
- `georef.py`: pixel to latitude and longitude. A sheet is fitted from control points read off its graticule
  (the degree and half-degree ticks of the border) through a Lambert conformal conic plane and an affine transform,
  with the residuals printed in kilometres. Other scans of the same base sheet are registered to the fitted scan by
  phase correlation of five patches (translation per patch, then an affine fit). Needs numpy and Pillow,
  unlike the standard-library scripts in `scripts/`.
- `sheet3_control.json`: the control points of base sheet 3 (Normandy, 1:500,000), scan `cs000022` (27 June 1944):
  14 graticule ticks, affine residual RMS about 1 km, checked against Cerisy-la-Salle and Canisy (0.5 and 1.2 km).

Usage: `python3 georef.py sheet3_control.json` prints the residuals of the fit.
- `sheetB_control.json`, `sheetC_control.json`, `sheetD_control.json`: control points of the August 1944 base sheets, scans `cs000064` (8 August, Brittany-Normandy, 10 towns, RMS 1.2 km, leave-one-out at most 3.7 km), `cs000071` (15 August, Normandy-Maine to Chartres, 13 towns, RMS 1.1 km, leave-one-out at most 2.5 km) and `cs000078` (22 August, Normandy-Paris at a smaller scale, 9 towns, RMS 1.1 km, leave-one-out at most 2.8 km). Control points are town road junctions read at full resolution with OpenStreetMap Nominatim coordinates (the graticule labels of these sheets are too faint to read). The sheet of 1 August (`cs000057`) is still base sheet 3 and is registered to `cs000022` (residual 0.7 px; Avranches, Coutances, Granville and Bayeux within 1 km).
- `sheetE_control.json`, `sheetF_control.json`, `sheetG_control.json`: control points of the 1:750,000 and smaller-scale outline sheets of late August and September 1944, scans `cs000085` (29 August, Normandy-Paris-Champagne, 7 towns, RMS 1.7 km, leave-one-out at most 5.2 km), `cs000092` (5 September, Channel-Belgium-Champagne, 12 towns, RMS 1.3 km, leave-one-out at most 3.2 km) and `cs000099` (12 September, Channel to Rhine, 13 towns, RMS 1.6 km, leave-one-out at most 4.9 km). `sheetG_registration.json`: affine pixel transforms of `cs000106` (19 September), `cs000113` (26 September), `cs000120` (3 October), `cs000127` (10 October), `cs000134` (17 October), `cs000141` (24 October) and `cs000148` (31 October) and `cs000156` (7 November) and `cs000163` (14 November) onto `cs000099` (same base sheet; phase correlation of nine patches, residuals under 9 px, about 1 km).
