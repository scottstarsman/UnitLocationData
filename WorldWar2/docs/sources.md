# Sources

Every claim row cites its own sources in the `source` column. This page lists what the proof of concept used, how reliable each source family is for this purpose, and licensing notes. It is not legal advice; the project owner should review it before publishing.

## Source families

| source | used for | reliability | licence / reuse |
|---|---|---|---|
| **US Army Center of Military History (CMH), *Cross-Channel Attack* (Gordon Harrison, 1951), chapters VII-X**, read via HyperWar (`ibiblio.org/hyperwar/USA/USA-E-XChannel/`) | day-by-day US corps and division moves, German reinforcement movements and battle groups, command changes, the Cherbourg timeline | **High** for US operations and for German dispositions known to the US official historians; written in 1951 from captured German records, so German detail can be incomplete or dated. Treated as the authoritative source (confidence 0.7 when it is the only source). | US federal government work: public domain in the United States. HyperWar is a mirror; `history.army.mil` blocked automated fetching. Cite the chapter. |
| **English Wikipedia**: unit pages, operation and battle pages (Epsom, Perch, Martlet, Villers-Bocage, Carentan, Bloody Gulch, Tonga, Cherbourg, American airborne landings, Battle for Caen), order-of-battle pages, "List of Allied forces in the Normandy campaign" | British, Canadian and German details, regiment and brigade names, commanders, strength figures, many coordinates | **Medium**. Good as a first pass and well-referenced on these topics, but secondary and sometimes internally inconsistent (see conflict groups). Used with confidence 0.5 when it is the only source. | CC BY-SA 4.0 (text) with share-alike. Facts extracted into this dataset are attributed by URL in `source`; this is why the data licence recommendation is CC BY-SA 4.0. |
| **Wikipedia API / Wikidata coordinates** | most place coordinates | Medium-high for village and town centres; the point is a place centre, not a unit position | CC0 for Wikidata; Wikipedia coordinates follow Wikipedia licence |
| **OpenStreetMap Nominatim** | coordinates for places Wikipedia did not geocode (for example Rauray, Lebisey, Blay, La Caine, Hill 112) | Medium; place-centre geocodes, marked in each row's source note | ODbL, attribution "(c) OpenStreetMap contributors"; use sparingly (1 request/second, cache results) |
| **Veterans Affairs Canada** (`veterans.gc.ca`, D-Day and the Battle of Normandy) | Canadian D-Day order of battle: which Canadian formations made the Juno assault (C0001) | **High** for Canadian participation and dates, thin on command detail | Crown copyright web page: only facts and the URL are used |
| **Tim Saunders, *Operation Epsom* (Pen & Sword), read via an `erenow.org` mirror of the book** | who fought whom on 28 June at Mouen and Colleville (C0184), including the 21st Panzer tank company | **Medium-high** (published battle history using unit accounts); a web mirror of a copyrighted book, so only facts and the URL are used | Copyrighted: no text copied |
| **Local-history and regional sources** (europeremembers, Ouest-France / actu.fr, FranceArchives, army.mil article) | Montgomery's headquarters at Creullet and Blay, First Army at D-Day | Medium-low; useful for places, dates sometimes differ by a day (see conflict groups G005, G006) | Copyrighted web pages: only facts and URLs are used, no text copied |

## Reliability notes

- Prefer a primary or semi-primary source (official histories, unit war diaries, regimental histories) over Wikipedia whenever one exists; Wikipedia is a finding aid.
- Where CMH and Wikipedia disagree on a date or place, both claims are recorded as a conflict group and the preferred row is the better-supported one (usually CMH).
- German strength figures come from secondary sources (Wikipedia pages quoting unit reports; CMH), not from the primary German returns. Treat `strength_json` as indicative.
- A reviewer's spot check of 15 rows led to five corrections (C0001, C0057, C0084, C0141, C0184); each was checked against the sources above and only changed where they support it. Rows whose confidence changed were re-scored by the rubric in `methodology.md`.
- Source conflicts recorded in `notes`: 90th Division commander change (CMH 13 June vs Wikipedia July), Feuchtinger and Choltitz ranks, 12th SS commander's rank, and several strength figures (21st Panzer 146 vs 112 tanks; 716th Division 7,000 vs 7,771 vs about 9,343 men).

## Licensing notes

- **Data**: recommended CC BY-SA 4.0. Wikipedia text is CC BY-SA, and share-alike applies to adaptations; keeping the dataset BY-SA is the conservative option. CMH is public domain; OSM data is ODbL (geocodes of place names are factual, but keep the attribution note in `source`).
- **Code**: MIT, independent of the data licence.
- **No copied text**: `notes` and `current_activity` were written by the dataset authors from the sources; do not paste long passages from copyrighted pages.
- **Contributors** should only add facts they can source and must be able to license their contribution under the repository licences.
- Before publishing, the owner should confirm the licence choices, fill in the copyright holder, and decide whether to ask a lawyer to review the Wikipedia share-alike question for their intended use.
