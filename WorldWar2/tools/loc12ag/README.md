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
