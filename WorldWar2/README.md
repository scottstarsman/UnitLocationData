# WWII Unit Locations

An open, claim-based dataset of where World War II units were, on a date, with coordinates, a precision radius, a confidence score, sources, and optional strength figures. Each row is one sourced claim: *this unit was at this place on this date*. Competing claims are kept as separate rows, not averaged away.

**Version 1.1.0-rc1** (`schema_version` 1.1.0). See `build/manifest.json` and `CITATION.cff`.

## Coverage and status

The surveyed focus is the **Western Front, 6 June 1944 to 8 May 1945**. The current build has **12,770 claims** in **2,635 units** (91 of them placeholders with no claim file). Claim dates in the files run from 16 September 1939 to 31 May 1945: most pre-6 June rows are Western Front pre-invasion positions under `OP-PRE-INVASION` and keep their real dates; a smaller number are incidental other-front or home-area rows (`eastern_front`, `home_germany`, and a few others). A few claims continue past 8 May 1945 (occupation and post-surrender rows, the latest on 31 May).

| Domain | Units | Claims |
|---|---:|---:|
| ground | 513 | 9,507 |
| air | 1,307 | 2,343 |
| naval | 815 | 920 |
| **All** | **2,635** | **12,770** |

Coverage is uneven and event-based, not a daily plot: a unit has a row on days when something substantial happened, so its position between rows is unknown. Live counts are in [docs/coverage.md](docs/coverage.md). Known gaps and later work are in [docs/roadmap.md](docs/roadmap.md).

## How to read a claim

One row is one sourced claim. `claim_status` is `preferred`, `alternate` or `disputed`; competing claims about the same unit and event share a `conflict_group_id`. The point is usually a place centre (`location_represents`), not a surveyed unit position. `confidence` measures date-and-place support, not “did the event happen.” Claim and relation dates are `YYYY-MM-DD`; `formed_date` and `initial_parent_as_of` may be a day, a month or a year, as the source gives them. Coordinates are decimal degrees, WGS84. The claim's `commander` field is the name the source gave on that row, and is often `unknown`. The derived `commander_on_date` column on the build claims export fills that gap from a preferred covering tenure when one exists (`commander_on_date_source` is `claim` or `tenure`; `commander_on_date_basis` is `stated`, `narrative`, or an `inferred_*` flag when the tenure started at the first claim date or has an inferred end). Dated tenures remain in `build/unit_commanders.csv` and `build/people.csv`. US armored formations use the `branch` value `Armored`; British, Commonwealth and other non-US armoured and panzer formations use `Armoured`.

Public ids (`C####`, `CR####`, `PL####`, `R####`, `G####`, `PE####`, `UC####`, `TT####`, `UT####`, and the others) are unique, never reused, and not renumbered across releases.

## Confidence tiers

The four levels are defined in [docs/methodology.md](docs/methodology.md):

| value | rule |
|---|---|
| 0.9 | exact place and two independent source families agree |
| 0.7 | exact place with one authoritative source, or an approximate place with two families |
| 0.5 | exact place with one secondary source, or an approximate place with one family |
| 0.3 | inferred or representative position, or an approximate date |

A single source is enough to create a unit (0.3). The preferred claim of a conflict group is at most 0.7; alternate and disputed claims are at most 0.5. Wikipedia is not a source family of its own in the sense of “two families”: every Wikipedia language is one family.

## Allied viewpoint

Sides and MIL-STD-2525D standard identity are stored from the Allied viewpoint (Allied and co-belligerent Friend, Axis Hostile). A viewer can swap digit 4 of the SIDC.

## Files and keys

The list of theaters and sub-theaters is in [`docs/theaters.md`](docs/theaters.md) and [`schema/theaters.json`](schema/theaters.json). To add a front, start with [How to add a new theater](CONTRIBUTING.md#how-to-add-a-new-theater).

Start here (paths relative to this folder). Filter claims on `domain` (`ground` / `air` / `naval`) and, for the surveyed Western Front, on `theater == "western_europe"`. The unit table has a `scope` column (`in_scope` / `out_of_scope`), but in this release every unit is `in_scope`; incidental other-front rows are distinguished by `theater` (and sometimes `operation_id`), not by `scope`. The who_controls grid is a derived point-in-time command tree used in checks and in the order-of-battle exporter; it still defaults to in-scope ground subjects.

- `build/all_claims.csv`, `build/all_claims.json`, `build/claims.geojson` — every claim, all domains, including the derived `commander_on_date` columns
- `build/units.csv`, `build/units.json` — the unit table
- `build/command_relations.csv`, `build/organic_relations.csv` — command relations (with a `domain` column)
- `build/places.csv`, `build/places.geojson` — places, with claim counts by domain
- `build/operations.csv`, `build/operations.geojson`, `build/operation_units.csv` — operations and participation
- `build/oob/` — flagship order-of-battle snapshots
- `build/people.csv`, `build/unit_commanders.csv` — commanders
- `build/toe_templates.csv`, `build/unit_toe.csv` — authorized TO&E
- `build/missions.csv`, `build/ship_classes.csv`, `build/aircraft_types.csv`
- `build/manifest.json` — schema and data versions, checksums and row counts
- `data/` — the master files the build is generated from
- [schema/README.md](schema/README.md) — the full column and vocabulary dictionary

The large combined files (`all_claims.csv`, `all_claims.json`, `claims.geojson`) are committed so a checkout is immediately usable.

## Quick start

```python
import csv
rows = list(csv.DictReader(open("build/all_claims.csv", encoding="utf-8")))
print(len(rows), "claims")
print(sum(1 for r in rows if r["domain"] == "ground"), "ground")
d13 = [r for r in rows if r["date"] == "1944-06-13" and r["claim_status"] == "preferred" and r["domain"] == "ground"]
print(len(d13), "preferred ground claims on 13 June 1944")

# Dated commanders live in unit_commanders.csv, not always on the claim row.
tenures = list(csv.DictReader(open("build/unit_commanders.csv", encoding="utf-8")))
july = [t for t in tenures if t["unit_id"] == "UK-ARM-007D"
        and t["status"] == "preferred"
        and t["valid_from"] <= "1944-07-31"
        and (t["valid_to"] == "" or t["valid_to"] >= "1944-07-01")]
print([t["canonical_name"] for t in july])
```

Run the scripts from this folder: `python scripts/validate.py`, `python scripts/build.py`, `python scripts/build.py --check`.

## How to cite

Starsman, Raymond Scott. 2026. *WWII Unit Locations: a claim-based dataset of unit positions (Western Front, 1944–1945)*. Version 1.1.0-rc1. https://github.com/scottstarsman/UnitLocationData. CC BY-SA 4.0.

Machine-readable metadata is in `CITATION.cff`. Copyright holder: Raymond Scott Starsman. Attribution guidance by source family and export is in [docs/reuse_and_attribution.md](docs/reuse_and_attribution.md).

## Limitations and known gaps

- Event-based, not a daily location for every unit.
- The surveyed focus is the Western Front, June 1944 to May 1945; other fronts and some earlier or later days appear only when a source happened to give them. Those rows are distinguished by `theater` and `operation_id`, not by a filled `out_of_scope` marker (every unit in this release is `in_scope`).
- Air and naval command relations are dense in June 1944 and thin later. Many air units have only one or two location claims, often a station or base change.
- Operation participation in `build/operation_units.csv` lists units whose claims (or descendant roll-ups) already carry that `operation_id`, and whose date falls inside that operation's start and end dates. It is not a complete historical order of battle. A campaign row is often used where a more specific operation was not tagged, and a blank `primary_place_id` means no sourced map pin.
- `commander` on a claim is the source-stated name on that row and is often `unknown`. The build export adds `commander_on_date` from a preferred covering tenure when the claim does not name one; `commander_on_date_basis` beginning `inferred_` means the tenure's start or end was inferred (often the first sourced claim, not the historical appointment). Many units still have no tenure at all.
- TO&E is high-level and incomplete (British official tables, earlier German KStN, and air establishments are still open).
- Some headquarters points are representative of a sector, not a surveyed command post.
- Wikipedia is not treated as a second family next to a work it summarises.

See [docs/roadmap.md](docs/roadmap.md) for the open items. Do not take this page as a complete inventory of gaps.

## Contributing and licence

Every row needs a source, conflicting claims become separate rows, and nothing is invented. [CONTRIBUTING.md](CONTRIBUTING.md) walks through a fork, a worked example (one unit, one claim, one source), the checks, and how to add another theater. Please also read the [code of conduct](CODE_OF_CONDUCT.md). Run `bash scripts/run_checks.sh` from this folder before you open a pull request; CI runs a subset of the same checks, including on pull requests from forks.

The whole repository — data, documentation, scripts and the web viewer — is licensed under [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/) (see the root [`LICENSE`](../LICENSE)). Creative Commons recommends against using CC licences for software, because they do not address patents and are not standard open-source software licences. Scott chose a single licence for the whole repository for simplicity (24 November 2026). Wikipedia-derived facts already require share-alike, which is why the data could not go under a non-share-alike licence.

Further documentation: [methodology](docs/methodology.md), [sources](docs/sources.md), [reuse and attribution](docs/reuse_and_attribution.md), [roadmap](docs/roadmap.md), [coverage](docs/coverage.md), [schema](schema/README.md), [maintainer notes](docs/maintainers.md).
