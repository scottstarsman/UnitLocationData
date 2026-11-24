# Implementation and verification

November 1, 2026. Local implementation on `codex/webui-situation-map`. No hosted publication, push, merge or dataset edits.

## Delivered

- React/TypeScript/Vite app with pinned dependencies and lockfile.
- Historical-reference palette, restrained vector basemap, compact formation symbols and echelon marks, zoom controls, scale and attribution.
- Date slider, date input, daily steps, next/previous observation date, play/pause and adjustable speed. No position interpolation.
- Last-observation age limits and distinct styling for older records. Multiple records on a unit's latest day are preserved.
- Searchable formation catalogue, nationality/echelon/operation filters, and optional placeholders. Operation filters include descendants without substituting an older location for a newer filtered-out one.
- Multi-unit history sets, date ranges, progressive reveal or whole-range display, colored points, dated labels with collision suppression, dashed directional connectors and fit-to-observations.
- Inspectable claims and full unit chronologies, competing accounts, original notes, provenance, precision radius, confidence, command entries, strength when available, and linked citations with locators/roles.
- Responsive formation drawer and detail panel, keyboard-operable controls, search shortcut and focus containment in the interpretation guide.
- Deterministic typed data package and manifest, generated from the existing dataset files with join/type checks. The package includes all 2,280 claims and 388 catalogued units.
- Bundled public-domain Europe outlines for an initial/fallback map; online detailed geography is optional.

## Verification record

- `npm run build`: passed, including TypeScript. Vite reports the expected large-map-library chunk warning; the build succeeds. The MapLibre worker is bundled explicitly for both development and production.
- `npm test`: nine tests cover calendar validity, age boundaries, no future observations, multiple same-day claims, disputed records, filter semantics, history clipping/ambiguity, alternate-account exclusion from connectors, descendant traversal, event stepping and real-package integrity.
- Development and production HTTP responses: 200.
- Browser QA: geographic layers and unit symbols render; two selected US divisions produce distinct colored histories; typed range endpoints constrain points and slider bounds; daily and observation-date stepping update the selected date; playback advances it; same-day filtering reports only same-day units; the interpretation guide opens; formation search and the phone drawer work.
- Desktop (1440 × 960), narrow app-pane and phone (390 × 844) breakpoints inspected. Responsive drawer selection was adjusted to close the catalogue when opening details.
- Browser inspection caught and corrected worker loading, overlay initialization after the online basemap style loads, and controlled date-entry behavior. No new production console errors were observed after these fixes; the browser log retains the earlier development worker error.
- `WorldWar2/scripts/validate.py`: passed, with 45 warnings and its existing note about 101 open claim-listed attachment/control entries. These are review prompts in unchanged source data; none was silently corrected by the app.
- `WorldWar2/scripts/build.py --check`: passed; all 12 generated outputs are up to date.
- `WorldWar2/scripts/semantic_tests.py`: all 590 expectations pass. Its existing inferred-position-replacement scenario remains explicitly not tested because the dataset cannot represent that replacement.
- Git whitespace checks: passed. The pre-existing `.idea/.gitignore` and previously staged notes were preserved.

The dataset checks used the local Python 3.14 interpreter (`python -B`). This directly installed interpreter was found after the earlier notes: the `python` WindowsApps alias and `py -3` launcher still failed. Python was already present; it was not installed for this app task. `tsx` tests required the normal account context because the sandbox's OS-profile lookup fails; ordinary terminal runs use the user's normal account.

## Current limits and next discussion

- Modern basemap geography is visually styled after the reference; there are no reconstructed wartime front lines, unit areas or verified roads/routes.
- History is observation sequence. Ambiguity and contested records break connectors; silence never establishes stationary units or inactivity.
- Source-record activity and command entries are displayed, but arbitrary-date activity inference and reconstructed command chains are intentionally outside this first interface.
- The age filter controls current symbols; historical points obey the history range and playback setting instead.
- Typed date values and selections survive the URL for date/mode/unit IDs only; other filters, ranges and viewport are session state.
- The full package loads into browser memory. At the current scale this keeps deployment simple; further optimization should follow measurement with larger data.
- Online fonts have system fallbacks. Detailed map tiles require internet access. The bundled outline layer has no offline road network or settlement-label catalogue. The initial outline and production online map were inspected; a fully disconnected browser session was not simulated.
- No formal military-symbol standard is claimed. Infantry, armor and headquarters shapes are visual conventions inspired by the reference.
- Preview servers used for QA are stopped at task teardown. Start the app with `npm run dev` as documented in `README.md`.
