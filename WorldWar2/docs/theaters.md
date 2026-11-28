# Theaters and sub-theaters

This is the two-level list of Second World War theaters used by the dataset. The machine-readable source is [`schema/theaters.json`](../schema/theaters.json). Each entry has a code, a plain name, a parent (blank for a top-level theater), one or more loose bounding boxes, a date floor, and an official date span. The checks read that file; do not copy the lists into the scripts.

The list follows official Allied and Axis theater divisions: the US European, Mediterranean, Pacific Ocean (with North, Central and South Pacific Areas), Southwest Pacific, and China-Burma-India theaters; British and Commonwealth commands (Home Forces, 21st Army Group, Mediterranean and Middle East, Persia and Iraq, East Africa, South-East Asia Command); and the German OKW theaters (West, Süd, Südost, Norwegen) with the OKH Eastern Front. Sources are listed in `schema/theaters.json` and include the US Army Center of Military History Green Books, the United Kingdom official history series, and the standard descriptions of the OKW/OKH split.

## How a row uses the list

- Every claim, unit and operation has a required `theater`. The allowed values are the top-level theaters plus four legacy codes that were already in the data as if they were theaters: `north_africa`, `balkans`, `scandinavia` and `home_germany`. Those four are now classified as sub-theaters, but existing rows may keep them in the `theater` column. There is no breaking rename. On `data/units.csv` only, `theater` may list more than one of those codes, separated by a pipe (`western_europe|pacific`), when the unit served in more than one theater. Claim and operation `theater` stay a single code.
- An optional `sub_theater` names a child of that theater. Existing rows may leave it blank. If `theater` itself is one of the four legacy codes, leave `sub_theater` blank (or set it equal to the same code).
- A claim's `theater` must equal its operation's `theater`. If both the claim and the operation have a `sub_theater`, they must be equal; a claim may fill in a sub-theater when the holding umbrella does not have one.
- The unit's `theater` and `sub_theater` are only the unit's primary front (or fronts); a claim may differ. If the unit lists more than one theater and sets `sub_theater`, the sub-theater must be a child of at least one of those theaters.

## Top-level theaters and their sub-theaters

- **western_europe** — Western Europe (US ETO; German Westfront / OB West). Sub-theaters: `britain`, `france_low_countries`, `southern_france`, `germany_west`.
- **mediterranean** — Mediterranean (US MTO; British Mediterranean and Middle East Command; German OB Süd). Sub-theaters: `north_africa` (legacy theater code), `italy`, `balkans` (legacy theater code), `middle_east`.
- **eastern_front** — Eastern Front (OKH Ostfront), including the 1939 Polish campaign as filed in this dataset. Sub-theaters: `poland`, `soviet_union`, `finland`, `germany_east`. The `poland` bounding box was widened east to 30°E on 27 November 2026 (branch `poland-1939`) so 1939 places in the Kresy now in Lithuania, Belarus or Ukraine (Wilno, Pińsk, Równe, Tarnopol) pass the typo check; it remains a loose box, not a political border.
- **pacific** — Pacific (US POA, with North, Central and South Pacific Areas, and SWPA). Bounding boxes cover both sides of the antimeridian, including Hawaii and the eastern Pacific. Sub-theaters: `central_pacific`, `south_pacific`, `southwest_pacific`, `north_pacific`, `aleutians`, `japan_home`.
- **cbi** — China-Burma-India (US CBI, later China Theater and India-Burma Theater; British SEAC and India Command). Sub-theaters: `china`, `burma`, `india`, `indochina`.
- **atlantic** — Atlantic (the Battle of the Atlantic). A mid-ocean point here is expected and is not treated as a coordinate typo. Sub-theaters: `north_atlantic`, `mid_atlantic`, `caribbean`.
- **arctic** — Arctic and Scandinavia (German command in Norway; the Norwegian campaign; Arctic convoys). New code. Existing Norway and Denmark rows stay on `scandinavia`. Sub-theaters: `scandinavia` (legacy theater code), `arctic_convoys`.
- **home_front** — Home and rear areas that were not then a combat zone. New code. Existing German rear-area rows stay on `home_germany`. Sub-theaters: `home_germany` (legacy theater code), `home_britain`, `home_united_states`, `home_japan`.
- **other** — Residual class; explain in notes. Sub-theater: `east_africa`.

## Date floors

The earliest date the checks will accept depends on the row's theater. The global floor, used when the theater is blank or has no floor of its own, is **7 July 1937** (the Marco Polo Bridge incident, the opening of the China war in official US Army CBI histories). There is no longer a single European bound of 1 September 1939 for every front.

Typical floors (see `schema/theaters.json` for the full list, including sub-theaters):

- `cbi` and `china`: 1937-07-07
- `western_europe`, `mediterranean`, `arctic`, `scandinavia`, `home_germany`: 1939-09-01
- `eastern_front` and its sub-theater `poland`: 1939-08-01 (old value 1939-09-01, changed 28 November 2026 on branch poland1939-oneplus-august, so that the German assembly on the Polish border in August 1939 can be filed under the phase `OP-PHASE-FALL-WEISS-ASSEMBLY`; hostilities open on 1 September 1939)
- `atlantic`: 1939-09-03
- `north_africa`: 1940-06-10
- `balkans`: 1940-10-28
- `pacific`: 1941-07-01 (so pre-Pearl Harbor garrison rows are allowed; hostilities open on 7 December 1941)

The latest working bound of the dataset is 31 December 1945.

## Holding umbrellas

Each theater has a holding umbrella operation for claims that are not yet under a named campaign: `OP-PRE-INVASION` and `OP-POST-SURRENDER` for `western_europe`; `OP-FRONT-EASTERN`, `OP-FRONT-MEDITERRANEAN`, `OP-FRONT-BALKANS`, `OP-FRONT-NORTH-AFRICA`, `OP-FRONT-SCANDINAVIA`, `OP-HOME-GERMANY` for the fronts that already had one; and `OP-FRONT-PACIFIC`, `OP-FRONT-CBI`, `OP-FRONT-ATLANTIC`, `OP-FRONT-ARCTIC`, `OP-FRONT-HOME` and `OP-FRONT-OTHER` for the rest. A child operation keeps its parent's theater.

## Adding a theater or sub-theater

See [How to add a new theater](../CONTRIBUTING.md#how-to-add-a-new-theater). In short: prefer an existing code; if you must add one, add it to `schema/theaters.json` and the matching vocabulary in `schema/vocabularies.json` in the same pull request, with a parent, bounding box, date floor, official span and a cited source, and add a holding umbrella if you are adding a top-level theater.
