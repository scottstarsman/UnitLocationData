# Reuse and attribution

What to credit, and what applies, when you reuse the dataset or one of its derived files. This page describes what the repository records; it is not legal advice and it does not change any licence. The whole repository is licensed under CC BY-SA 4.0 (root [`LICENSE`](../../LICENSE)); the source-by-source notes are in [sources.md](sources.md); the per-source terms are in the `license_or_status` column of [`data/references.csv`](../data/references.csv).

## What you reuse

Every file in the repository — including `data/`, `build/`, `schema/`, `docs/`, the scripts and the web viewer — is licensed under CC BY-SA 4.0: you may copy, adapt and use it for any purpose, including commercially, if you give credit, say what you changed, and release your adaptation under the same licence. Cite the dataset with `CITATION.cff`.

The facts in the rows come from published sources. The repository stores facts (dates, places, unit names, relationships), short notes in its own words, and links; it does not copy source text, so the sources' own terms matter mainly for **credit** and for the **share-alike** inheritance of Wikipedia-derived material.

## By source family

The counts are the references of `data/references.csv` on 26 October 2026 (511 references; the count of claims per reference is in the same file; a few references have other terms, such as the OpenStreetMap geocoder and one French public-archive page under the Licence Ouverte).

| family | references | terms recorded | what a reuser should do |
|---|---:|---|---|
| US Army Center of Military History (the Green Books and order-of-battle tables, on HyperWar or the history.army.mil archive copies), other US Army reports | 119 recorded as public domain (113 of them in the `us_army_cmh` family) | public domain (US government work); the hosting mirror is private | no restriction on the facts; cite the volume and page (`source_locator`) and the link |
| English Wikipedia (unit, operation and order-of-battle pages) | 174 | CC BY-SA 4.0 (Wikipedia text); Wikidata coordinates are CC0 | credit Wikipedia as the origin of the facts and keep the share-alike licence on what you publish with them; the repository's data licence is CC BY-SA 4.0 for this reason |
| Lexikon der Wehrmacht | 164 | all rights reserved by the site; only short facts (dates, names) are used | credit the site; do not copy its text; the repository holds the facts and the link |
| other web pages, books on web mirrors, memorial and local-history pages (World War II by Day, erenow, Pegasus Archive, D-Day Overlord and others) | 51 recorded as copyrighted pages (30 of them World War II by Day) | copyrighted pages; only facts and the URL are used | credit the page where you rely on it; do not copy the page |
| OpenStreetMap Nominatim geocodes (reference R002) and Wikipedia article coordinates (R001) | 2 references, behind 170 and 204 of the 378 places | R002: ODbL 1.0, attribution "(c) OpenStreetMap contributors"; R001: Wikipedia, CC BY-SA, Wikidata CC0 | if you publish the point of a place with a `coord_reference_id` of R002, add the OpenStreetMap attribution; the coordinates of a place are place-centre geocodes (see "What a location point can mean" in `schema/README.md`) |

## By derived export

| export | what it contains | what to carry with it |
|---|---|---|
| `build/all_claims.csv`, `build/claims.geojson` | every claim with its place, command relationships and `reference_ids`, `source` and `source_locator` | the dataset credit; keep `reference_ids` (or `source`) with any claim you republish so the credit to each source family travels with the row; keep `confidence`, `precision_km`, `location_represents` and `claim_status` with a coordinate you map (they limit what the point means) |
| `build/places.csv`, `build/places.geojson` | places with coordinates and `coord_reference_id` | the OpenStreetMap attribution for places whose coordinate source is R002; the Wikipedia credit for R001 |
| `build/command_relations.csv` | relation intervals with `support`, bases, `end_unknown` and the evidence claim ids | the dataset credit and the `*_basis` columns; do not drop `end_unknown` or the bases (they say which boundaries are inferred) |
| `data/references.csv`, `build/claim_references.csv`, `build/unit_references.csv` | the sources and their links, terms and counts | the dataset credit; the per-source terms stay with each row |
| `build/operations.csv`, `build/coverage.csv`, `docs/coverage.md` | derived summaries | the dataset credit |

A suggested credit line: "Unit-location data from the WWII Unit Locations dataset (CC BY-SA 4.0), which draws on the US Army Center of Military History official histories, Wikipedia, the Lexikon der Wehrmacht and other sources listed in `data/references.csv`; changes: <what you changed>." Add "(c) OpenStreetMap contributors" if you publish coordinates of places geocoded with Nominatim.

## What the dataset does not give you

A claim is a sourced assertion, not a verified unit state; a point is usually a place centre; `confidence` scores the date and place. See "How to interpret the data" in the root `README.md` before you publish a map, a distance or a timeline built from these files.
