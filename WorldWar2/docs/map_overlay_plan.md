# Map overlay tool: plan (5 November 2026, not implemented)

## Goal
Overlay the dataset's claims on period maps so a reviewer can see, for one date and one sheet, where each claim puts a unit and where the map puts it. The output is review prompts only: map-derived evidence stays at confidence 0.3 or lower and never outranks text. No claim changes automatically.

## Inputs
- Claims: `data/claims/<country>/*.csv`, joined to `data/places.csv` (lat/lon, precision) and `data/units.csv`. Default: preferred rows, with alternates on a toggle.
- LoC 12th Army Group situation maps (R781): Drive "LoC 12th Army Group maps", 416 daily sheets. `tools/loc12ag/sheet_index.csv` maps date to sheet. `tools/loc12ag/georef.py` and `sheet*_control.json` already fit the base sheets (graticule GCPs, Lambert conformal conic projection plus an affine fit, about 1 km RMS) and register other scans of the same base sheet by phase correlation.
- B-709 sketch maps: Drive "source maps/B-709". These are hand sketches with no graticule, and their rows are already at 0.3. They are a phase-2 input.
- Map images stay in Drive or scratch folders only and are never committed. Overlay outputs (PNG/HTML) also stay outside the repo.

## MVP (v1)
One date and one sheet, for example 27 June 1944, scan `cs000022` (base sheet 3, already controlled).
1. Select the preferred claims dated within ±1 day of the sheet date that fall inside the sheet's lat/lon bounds.
2. Project each claim's lat/lon to pixels with the inverse of the `georef.py` fit.
3. Draw a marker plus label (unit_id, claim_id, confidence, date), with a circle for precision_km.
4. Write `overlay_<sheet>_<date>.png` and a CSV with one row per claim, both in a scratch folder.
5. The reviewer clicks or enters the pixel of the map's symbol for that unit. The CSV then gets the map lat/lon and the distance.

Script: `tools/map_overlay/overlay.py`. It needs numpy and Pillow like the `loc12ag` tools. It is not part of the build or `run_checks.sh`.

## Georeferencing options
| Option | How | Pros | Cons |
|---|---|---|---|
| A. Affine/LCC on the scanned sheet (recommended for LoC) | Reuse `georef.py` and the control JSONs; add control files for the other base sheets | Already built and measured (about 1 km); offline; exact pixel overlay | Each new base sheet needs about 15 graticule GCPs read once |
| B. Manual GCPs | Pick 6-10 towns on the scan and use their `places.csv` coordinates | Works on sketches with no graticule (B-709) | Error depends on the sketch; a 2D affine fit is poor for distorted sketches |
| C. Web map overlay | Plot the claims on OSM (Leaflet HTML); show the scan as a georeferenced image layer from A or B | Easy panning, modern place names | Still needs A or B to place the scan; heavier output |

Plan: use A for LoC sheets in v1, C as an optional HTML viewer in v2, and B only for B-709 in phase 2.

## Accuracy checks to surface
- **Distance**: claimed place to map symbol in km, flagged when greater than max(5 km, precision_km). This matches the 5 km agreement rule of 31 Oct 2026.
- **Date lag**: the gap in days between the claim date and the sheet date. Pick the nearest sheet; flag a lag over 1 day.
- **Missing**: a claim with no symbol on the sheet, or a map symbol with no claim. The second case is a coverage gap, not an error.
- **Echelon/position mismatch**: for example a headquarters claim placed at the front line. This is noted only, not scored.
- **Fit quality**: print the georef residual for each sheet; skip distance flags smaller than the residual.
- Summary per sheet: n claims, median and 90th-percentile distance, count of flags.

## Out of scope for v1
Automatic symbol detection or OCR; creating or changing claims; batch runs over all 416 sheets; B-709 sketches; Fold3 material; rebuilding or uploading the dataset zip; command-relation lines.

## Open questions for Scott
1. Should v1 be a static PNG plus CSV, or a Leaflet HTML viewer?
2. Which date and sheet should be the pilot? The default is 27 June 1944 (`cs000022`).
3. Should flagged distances feed `roadmap.md` items, a new review CSV, or private notes only?
4. Should overlay outputs live in Drive (for example "map overlays/"), and should they include alternate rows?
5. For B-709: is a manual-GCP fit acceptable given the sketch distortion, or is a visual check only enough?

## Suggested next step
Once Scott answers questions 1-2: on a new branch, add `tools/map_overlay/overlay.py` plus a README, run the pilot sheet, and report the per-sheet summary and a handful of flagged rows for review. One branch per task, push the branch only.
