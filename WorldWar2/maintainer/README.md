# Maintainer scripts

One-off ingest and working scripts used while building the dataset. They are not part of the public build, and `scripts/build.py` / `scripts/validate.py` do not call them.

- `add101.py` — a Fold3 reading pass for FMS B-101 (November 2026). Run it from this folder only if you are repeating that pass; it expects to live two levels below `WorldWar2/`.
