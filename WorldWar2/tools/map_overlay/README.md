# Map overlay tool

Overlay the dataset's preferred and alternate claims on a Library of Congress
12th Army Group situation-map scan so a reviewer can compare each claim with
the map symbol. The output is review prompts only: map-derived evidence stays
at confidence 0.3 or lower and never outranks text. This script never changes
claim rows.

It needs numpy and Pillow, like `tools/loc12ag`. It is not part of the build
or `run_checks.sh`.

Map scans and overlay outputs (PNG and CSV) stay in a scratch folder
outside the repository and are never committed.

## Pilot (27 June 1944, scan `cs000022`)

Control points are in `tools/loc12ag/sheet3_control.json` (base sheet 3, full
resolution). `tools/loc12ag/sheet_index.csv` has the date-to-sheet map and a
half-size IIIF link (`pct:50`). The image itself is not in the repository;
download it into a scratch folder outside git:

```bash
mkdir -p /tmp/map-overlay-scratch
curl -L -o /tmp/map-overlay-scratch/cs000022.jpg \
  'https://tile.loc.gov/image-services/iiif/service:gmd:gmd5m:g5701m:g5701sm:gct00021:cs000022/full/pct:50/0/default.jpg'
```

If you already have the full-resolution scan that the control points were
read from, use that instead (`--pixel-scale` stays 1). For the half-size
IIIF default the tool detects `--pixel-scale 0.5`.

From `WorldWar2/`:

```bash
python3 tools/map_overlay/overlay.py \
  --date 1944-06-27 \
  --sheet cs000022 \
  --control tools/loc12ag/sheet3_control.json \
  --image /tmp/map-overlay-scratch/cs000022.jpg \
  --out /tmp/map-overlay-scratch
```

That writes, only in `--out`:

- `overlay_cs000022_1944-06-27.png`
- `overlay_cs000022_1944-06-27.csv`

Stdout prints the georef residuals and RMS, the sheet lat/lon bounds, the
claim count (preferred vs alternate), and a short sample of rows.

## Arguments

| Argument | Default | Meaning |
|---|---|---|
| `--date` | `1944-06-27` | Situation date of the sheet (`YYYY-MM-DD`) |
| `--sheet` | `cs000022` | LoC scan id |
| `--control` | `tools/loc12ag/sheet3_control.json` | Control-point JSON for `georef.py` |
| `--image` | required | Path to the map scan |
| `--out` | required | Scratch directory for the PNG and CSV |
| `--data-root` | `WorldWar2/data` | Claims, `places.csv` and `units.csv` |
| `--window-days` | `1` | Keep claims dated within ±N days of `--date` |
| `--pixel-scale` | `auto` | `1` for the full-resolution scan, `0.5` for the IIIF `pct:50` image, or `auto` |

Claims are included when `claim_status` is `preferred` or `alternate`, the
claim date is inside the window, and the place's lat/lon falls inside the
sheet bounds (the lat/lon box of the image corners, after the georef fit)
and projects onto the image. Coordinates come from the claim row, or from
`places.csv` when the claim has none. Each place is projected with
`georef.Fit.inv`.

## Drawing

- Preferred rows: filled blue circle, solid precision circle.
- Alternate rows: open orange diamond, dashed precision circle.
- Label: `unit_id claim_id confidence date`.
- The precision circle uses `precision_km` converted through the same fit
  (one kilometre in the Lambert plane).

## Review CSV

One row per drawn claim. Columns are the claim fields a reviewer needs
(`claim_id`, `claim_status`, unit, date, lat/lon, place, precision,
confidence, and related location fields) plus:

- `pixel_x`, `pixel_y`: claim location on the written PNG (control-point
  pixels scaled to the image)
- `date_lag`: claim date minus sheet date, in days
- `map_symbol_px`, `map_symbol_py`, `map_lat`, `map_lon`, `distance_km`:
  left blank until a reviewer supplies the map-symbol pixel
- `flags`: blank in this version except `date_lag` when the absolute lag
  is greater than 1 day (the default window does not select those rows)

Copy the CSV to Drive for review if wanted. Do not commit it. Distance
flags (greater than max(5 km, `precision_km`)) wait until the map pixel
is filled in.
