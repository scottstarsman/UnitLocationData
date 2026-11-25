# UnitLocationData

An open, claim-based dataset of where World War II units were, on a date, with coordinates, precision, confidence, sources, conflict handling and optional strength figures. Competing claims are kept, not averaged.

**Version 1.1.0-rc1** (`schema_version` 1.1.0). The current build has **12,770 claims** (9,507 ground, 2,343 air, 920 naval) in **2,635 units**. The surveyed focus is the Western Front, 6 June 1944 to 8 May 1945; claim dates in the files run from 16 September 1939 to 31 May 1945. Coverage is uneven and event-based, not a daily plot.

Everything lives in [`WorldWar2/`](WorldWar2/):

- [`WorldWar2/README.md`](WorldWar2/README.md): what the dataset is, how to read a claim, files and keys, quick start, licence and citation
- [`WorldWar2/build/`](WorldWar2/build/): ready-to-use combined files (`all_claims.csv`, `claims.geojson`, `units.csv`, `command_relations.csv`, `places.csv`, `operations.csv`, `manifest.json`, and the rest)
- [`WorldWar2/data/`](WorldWar2/data/): the master data (one claim file per unit, the unit table, places, command relations, and the other source tables)
- [`WorldWar2/docs/`](WorldWar2/docs/): methodology, sources, roadmap, coverage, reuse and attribution
- [`WorldWar2/docs/review/`](WorldWar2/docs/review/): review notes
- [`WorldWar2/CONTRIBUTING.md`](WorldWar2/CONTRIBUTING.md): how to fork, add a unit or a claim, run the checks, and start a new theater
- [`WorldWar2/docs/maintainers.md`](WorldWar2/docs/maintainers.md): how to run the checks and the public release rules
- [`WorldWar2/CITATION.cff`](WorldWar2/CITATION.cff): citation metadata
- [`WorldWar2/build/manifest.json`](WorldWar2/build/manifest.json): schema and data versions, checksums and row counts

Run the scripts from inside `WorldWar2/` (for example `cd WorldWar2 && python scripts/validate.py`). The GitHub Actions workflow in `.github/workflows/` runs the validators against `WorldWar2/`.

The whole repository — data, documentation, scripts and the web viewer — is licensed under CC BY-SA 4.0 (see [`LICENSE`](LICENSE)). Creative Commons recommends against using CC licences for software; Scott chose a single licence for the whole repository for simplicity (24 November 2026). Citation: `WorldWar2/CITATION.cff`.
