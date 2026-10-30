# Source reading method

How to review a source document (official history, divisional history, memoir, report) and write reading notes for the unit-location dataset. Follow it for every source so notes stay consistent.

## Where notes live
- Notes from copyrighted sources are private: keep them on the assistant's computer (`/workspace/ww2-locations/sources/<source>_notes.md`) and one copy in the Google Drive folder `WWII Unit Locations/source notes/`. Never commit them; `.gitignore` excludes `**/sources/*_notes.md`.
- Replace the Drive copy in place when notes change (no duplicates) and confirm the Drive checksum matches the local file.
- Delete scratch text extracted from the source when done; keep the source PDF if it may be reread.

## How to read
1. Record the source: author, title, volume, year, edition, where it was read (link), copyright status, and its reference id if it is already in the dataset.
2. Read every page in order, front matter through appendices. Do not filter by keyword; facts often appear in sentences that do not name the unit (resolve the unit from context).
3. View every map, diagram and table as an image and transcribe what it shows. Mark map-derived positions "from map, approximate"; mark doubtful readings with "?".
4. Use the printed page numbers (running heads), not scan leaf numbers.
5. Paraphrase only. No quotations beyond a few words.
6. Each later pass over the same source adds a tag (`[pass2]`, `[pass3]`) to its new lines so passes stay distinguishable, and the header records what each pass covered.

## What to capture
For each fact: date or date range, unit, place, what happened, parent formation, printed page.
- **Units:** every dated location of every division, independent brigade, corps, army and army group, Allied and Axis.
- **Movements:** moves, reliefs, arrivals in and departures from the theatre, furthest point reached.
- **Activity:** in line, reserve, rest, refit, garrison or occupation, transit, with start and end dates where given.
- **Command:** attachments and changes of command with dates, headquarters locations and moves, army, corps and army group boundaries.
- **Operations and battles:** names, dates, objectives, the units involved and where.
- **Places:** towns, villages, rivers, bridges, hills and points, forests, canals and other features, with enough context to locate them.
- **Leaders:** commanders of formations and changes of command, with dates.
- **Strength and condition:** losses, tank and troop strength, units cut to a cadre, rebuilt, merged, renamed or disbanded.
- **Front lines:** dated front-line traces, including those read from maps.
- **Uncertainty:** vague dating, contradictions with other sources, and anything unreadable in the scan.

## Notes file layout
1. Header: source details, method, pass history, coverage and limits (which nationalities and dates the source is thin on).
2. Entries by unit, grouped by nationality.
3. Operations and battles index.
4. Places index and leaders index.
5. Chronological index.
6. Unreadable or skipped pages and maps.
7. Gap summary: for each fact, whether the dataset already has it, would gain from it, or disagrees with it, plus the gaps the source can fill.

## Reporting
After each pass, report: notes path and Drive location, counts of facts by nationality, the most significant new items (including what the maps gave), gaps the source can fill, anything still unread or unreadable, and usage (percent of the weekly limit used and time to reset). Adding data to the dataset is a separate task on its own branch.
