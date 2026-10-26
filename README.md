# UnitLocationData

An open dataset of where World War II units were, when, and how sure we are: sourced, claim-based records with coordinates, precision, confidence and conflict handling.

Everything lives in [`WorldWar2/`](WorldWar2/):

- [`WorldWar2/README.md`](WorldWar2/README.md): what the dataset is, its layout and data model, quick start
- [`WorldWar2/build/`](WorldWar2/build/): ready-to-use combined files (`all_claims.csv`, `claims.geojson`, `places.csv`, `places.geojson`, `coverage.csv`)
- [`WorldWar2/data/`](WorldWar2/data/): the master data (one claim file per unit, the unit table, the places table and the command-relations tables)
- [`WorldWar2/docs/`](WorldWar2/docs/): methodology, sources, roadmap, coverage
- [`WorldWar2/docs/review/`](WorldWar2/docs/review/): review notes (what reviewers claimed, what the sources say, what changed)
- [`WorldWar2/CONTRIBUTING.md`](WorldWar2/CONTRIBUTING.md): how to add a unit or a claim

Run the scripts from inside `WorldWar2/` (for example `cd WorldWar2 && python scripts/validate.py`). The GitHub Actions workflow in `.github/workflows/` runs the validators against `WorldWar2/`.

Licences: data and documentation CC BY-SA 4.0 (`WorldWar2/LICENSE-DATA`), code MIT (`WorldWar2/LICENSE-CODE`); see the root `LICENSE` for which applies where. Citation: `WorldWar2/CITATION.cff`.
