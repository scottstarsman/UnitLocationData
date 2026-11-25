# WWII Unit Locations

A local React / TypeScript / MapLibre web app for the WWII Unit Locations dataset. The surveyed focus of the current data is the Western Front, June 1944 to May 1945, but the atlas is not limited to that front. The visual design takes its warm paper, muted blue water, subdued geography and compact military symbols from Scott's June 23, 1944 situation-map reference. The scan itself is not copied into the app.

## Run

Requires Node.js 22.12+ (developed with Node 22.20) and npm.

```powershell
cd WebUI
npm ci
npm run dev
```

Open the local URL printed by Vite, normally `http://127.0.0.1:5173/`. Keep that terminal running while using the app; press Ctrl+C to stop it.

```powershell
npm run build       # prepare the data, type-check, and build dist/
npm test            # temporal behavior and real-data contract checks
npm run preview     # serve the built application locally
```

`npm run dev` and `npm run build` regenerate the app's data package. `npm test` uses that prepared package; run `npm run data:prepare` first if testing in a fresh checkout. Dependencies are pinned in package.json and package-lock.json; use `npm ci` for repeatable installs.

## Using the atlas

- **Situation:** scrub the daily slider, type/pick a date, step one day, jump to the next/previous observation date, or play at 1–10 days per second. Playback stops at the end. Next/previous observation dates respect active filters and, in history mode, the selected formations/range.
- **Formation list:** search names or IDs; filter by nation, echelon and operation. Operation filters include descendants. The list is a catalogue, so it can include units without a visible observation on the selected date. Enable the catalogue's placeholder checkbox to include units with no claims.
- **Observation age:** the default map includes the latest observations within 30 days. Choose same-day-only, 7 days, 14 days, 30 days, or any earlier observation. Dashed symbols and `−Nd` labels distinguish older observations. This is a display of last recorded positions, not a claim that the units stayed there.
- **History:** check formations in the list or add them from their detail panel. Switch to Movement history, choose the date range, and optionally fit the map. By default, points are revealed only up to the slider date. “Show entire range” also displays later points in the chosen range. Each selected unit has a color; points are inspectable and labels show dates where space permits. The observation-age limit applies to current symbols, not the past points in a selected history range.
- **Details:** select a unit symbol, formation name, history point/date label, or chronology record. Inspect point meaning, precision, location provenance, confidence, command entries, strength where recorded, source links and locators, and original caveats. The chronology includes all that unit's claims, including alternatives and later records. Inspecting a record does not change the slider date; “Go to date” does.
- **Interpretation:** the guide explains point meanings, competing claims and attribution. Keyboard users can tab through controls; `/` focuses formation search and Escape closes the guide/formation drawer.

Multiple observations on a unit's latest day are retained rather than reduced to an arbitrary single position. Preferred and disputed claims are enabled by default; alternate claims are optional. History connectors are straight dashed links between successive unambiguous preferred observations, with direction arrows. Conflicts, ambiguous same-day records, and filtered-out intervening observations break connectors. These lines are not sourced routes, speed measurements or continuous locations. No interpolation or front lines are invented.

Infantry, armor and headquarters symbols are compact visual conventions inspired by the reference, not a complete implementation of a formal military symbology standard. Echelon marks, country labels, tooltips and full formation details accompany them.

## Data flow

`scripts/prepare-data.mjs` reads:

- `../WorldWar2/build/all_claims.csv`
- `../WorldWar2/build/coverage.csv`
- `../WorldWar2/build/operations.csv`
- `../WorldWar2/build/claim_references.csv`
- `../WorldWar2/data/units.csv`
- `../WorldWar2/data/references.csv`
- `../WorldWar2/data/nationalities.csv`

It writes ignored, deterministic `public/data/atlas.json` and `manifest.json`, which Vite copies into the production build. The package includes typed booleans/numbers, ID arrays, parsed relationship/strength JSON, all source metadata and input hashes. The manifest derives date bounds from actual claims (currently through May 10, 1945). The script validates IDs and required joins, but does not replace the dataset's own Python validators or determine build freshness.

Neither app generation nor the UI edits anything in WorldWar2. Regenerate the dataset upstream using its documented workflow before rebuilding the app when source data changes.

`src/engine.ts` contains pure calendar-date, observation selection, filter and history rules. `src/MapView.tsx` owns the map, overlays and symbol layout. `src/App.tsx` owns controls, selection and evidence panels. Calendar calculations use UTC day numbers to avoid local timezone shifts. Activity annotations and command entries are displayed as recorded by the selected claim; this version does not reconstruct an activity state or command tree for arbitrary dates.

The URL retains selected date, mode and history unit IDs. Filters, history bounds, playback and viewport are session-only in this version.

## Geography, network and attribution

The app requests a detailed vector style/tiles from **OpenFreeMap**, with OpenMapTiles / OpenStreetMap attribution. It restyles that geography with the reference-inspired palette. This basemap is modern: roads, settlement extents and borders are not asserted to be historical. There is no API key or backend. CSS requests Barlow Condensed and DM Sans through Google Fonts, with local system fallbacks.

The bundled `public/geography/europe.geojson` provides an offline outline fallback. It contains 28 country features selected from Natural Earth's public-domain 1:50m country polygons; see its adjacent source note. No historical boundaries or detailed offline road network are included. If only some online tiles fail after the style loads, the app flags that condition; the detail layers may be incomplete.

The web viewer, like the rest of the repository, is licensed under **CC BY-SA 4.0** (root `LICENSE`). Dataset credit and source evidence must be retained. Coordinate attribution includes OpenStreetMap contributors and the recorded Wikipedia/Wikidata sources. See `CITATION.cff` and `WorldWar2/docs/reuse_and_attribution.md` for attribution instructions. Source-specific licensing is available in `data/references.csv` and in the generated package.

## Verification

The first implementation was checked with a production build, TypeScript and nine regression/data-contract tests. Browser QA covers map rendering, formation search/selection, multi-unit history, range controls, daily/event stepping, playback, evidence details and responsive layouts. See `DEVELOPMENT_NOTES.md` for the final verification record and current limitations.

This is a local viewer; there is no hosted deployment in this release.
