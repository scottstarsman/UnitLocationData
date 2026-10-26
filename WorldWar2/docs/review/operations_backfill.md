# Operations backfill

How the 566 claims were moved from the three free-text columns (`campaign`, `operation_name`, `sub_operation_name`) to a single `operation_id` (`scripts/migrate_operations.py`). The old labels and the claim's date were the only inputs; nothing was guessed. A claim takes the most specific operation row named by its old labels when its date lies inside that row's dates; otherwise it takes the campaign it already carried and is listed here.

| outcome | claims |
|---|---:|
| operation row named by the old label, date inside the row's dates | 280 |
| same, date within 7 days of the dates (kept; listed in `data/operation_exceptions.csv`) | 11 |
| old label has no operation row, or the date is far outside the dates (campaign used) | 20 |
| two-label rows (one operation chosen) | 3 |
| rows with only a campaign or an umbrella label (campaign used) | 252 |

## Unmatched or ambiguous claims (campaign used)

These claims keep the CMH campaign as their `operation_id`. Add an operation row (see CONTRIBUTING.md) and set the claim's `operation_id` when a source supports one.

| claim | unit | date | old labels (campaign / operation_name / sub_operation_name) | operation_id | reason |
|---|---|---|---|---|---|
| C0213 | XVIII Airborne Corps | 1944-08-25 | Northern France / Overlord / Market Garden preparations | OP-CAMP-NORTHERN-FRANCE | Market Garden opens on 17 September; the rows are command changes of the airborne units in August |
| C0214 | 82nd Airborne Division | 1944-07-13 | Normandy / Overlord / Return to England | OP-CAMP-NORMANDY | a return move, not an operation |
| C0215 | 82nd Airborne Division | 1944-08-12 | Northern France / Overlord / Market Garden preparations | OP-CAMP-NORTHERN-FRANCE | Market Garden opens on 17 September; the rows are command changes of the airborne units in August |
| C0216 | 82nd Airborne Division | 1944-08-27 | Northern France / Overlord / Market Garden preparations | OP-CAMP-NORTHERN-FRANCE | Market Garden opens on 17 September; the rows are command changes of the airborne units in August |
| C0218 | 101st Airborne Division | 1944-07-15 | Normandy / Overlord / Return to England | OP-CAMP-NORMANDY | a return move, not an operation |
| C0219 | 101st Airborne Division | 1944-08-12 | Northern France / Overlord / Market Garden preparations | OP-CAMP-NORTHERN-FRANCE | Market Garden opens on 17 September; the rows are command changes of the airborne units in August |
| C0320 | XII Corps | 1944-08-13 | Northern France / Overlord / Le Mans | OP-CAMP-NORTHERN-FRANCE | no named operation or battle row (XV Corps capture of Le Mans, 8-9 August) |
| C0321 | XII Corps | 1944-08-19 | Northern France / Overlord / Loire | OP-CAMP-NORTHERN-FRANCE | no named operation or battle row (Loire valley sector) |
| C0328 | XV Corps | 1944-08-08 | Northern France / Overlord / Le Mans | OP-CAMP-NORTHERN-FRANCE | no named operation or battle row (XV Corps capture of Le Mans, 8-9 August) |
| C0330 | XV Corps | 1944-08-19 | Northern France / Overlord / Seine | OP-CAMP-NORTHERN-FRANCE | no named operation or battle row (Seine crossings) |
| C0335 | XX Corps | 1944-08-10 | Northern France / Overlord / Loire | OP-CAMP-NORTHERN-FRANCE | no named operation or battle row (Loire valley sector) |
| C0451 | 79th Infantry Division | 1944-08-19 | Northern France / Overlord / Seine | OP-CAMP-NORTHERN-FRANCE | no named operation or battle row (Seine crossings) |
| C0484 | First Army | 1944-08-01 | Northern France / Overlord / Pursuit | OP-CAMP-NORTHERN-FRANCE | dated 18 days before the dates of Pursuit across France (1944-08-19 to 1944-09-14) |
| C0485 | First Army | 1944-08-01 | Northern France / Overlord / Pursuit | OP-CAMP-NORTHERN-FRANCE | dated 18 days before the dates of Pursuit across France (1944-08-19 to 1944-09-14) |
| C0504 | XX Corps | 1944-08-06 | Northern France / Overlord / Pursuit | OP-CAMP-NORTHERN-FRANCE | dated 13 days before the dates of Pursuit across France (1944-08-19 to 1944-09-14) |
| C0505 | XII Corps | 1944-08-07 | Northern France / Overlord / Pursuit | OP-CAMP-NORTHERN-FRANCE | dated 12 days before the dates of Pursuit across France (1944-08-19 to 1944-09-14) |
| C0527 | Seventh Army | 1944-12-08 | Rhineland / - / Alsace | OP-CAMP-RHINELAND | no named operation or battle row (Alsace, December 1944; Operation Nordwind began on 31 December) |
| C0532 | XIII Corps | 1944-11-08 | Rhineland / - / Roer | OP-CAMP-RHINELAND | dated 8 days before the dates of Operation Queen (1944-11-16 to 1944-12-16) |
| C0534 | 102nd Infantry Division | 1944-11-08 | Rhineland / - / Roer | OP-CAMP-RHINELAND | dated 8 days before the dates of Operation Queen (1944-11-16 to 1944-12-16) |
| C0562 | XXI Corps | 1944-12-27 | Ardennes-Alsace / - / Alsace | OP-CAMP-ARDENNES-ALSACE | no named operation or battle row (Alsace, December 1944; Operation Nordwind began on 31 December) |

## Rows with two old labels

Each of these belonged to two operations at once in the old columns. The operation tree does not need a many-to-many table for them: one operation is chosen and the other is linked in `data/operation_relations.csv`. If more such cases appear, a `claim_operations` link table can be added.

| claim | unit | date | old sub_operation_name | operation_id | why |
|---|---|---|---|---|---|
| C0160 | I SS Panzer Corps | 1944-06-26 | Martlet; Epsom | OP-EPSOM | Martlet supported Epsom (data/operation_relations.csv); the rows are German reactions to the whole offensive, so the larger operation is taken |
| C0170 | 12th SS Panzer Division Hitlerjugend | 1944-06-27 | Martlet; Epsom | OP-EPSOM | Martlet supported Epsom (data/operation_relations.csv); the rows are German reactions to the whole offensive, so the larger operation is taken |
| C0544 | 84th Infantry Division | 1944-11-18 | Roer; Clipper | OP-CLIPPER | the row is the 84th Division attack at Geilenkirchen, which is Clipper; Clipper ran alongside the Roer offensive (Queen) |

## Rows kept with an exception (dated just outside the operation)

Preparation or aftermath rows the earlier dataset labelled with the operation; the full reasons are in `data/operation_exceptions.csv`.

| claim | unit | date | old label | operation_id | days outside |
|---|---|---|---|---|---|
| C0148 | Kampfgruppe von Luck | 1944-06-23 | Epsom | OP-EPSOM | 3 before |
| C0150 | 51st (Highland) Infantry Division | 1944-06-23 | Epsom | OP-EPSOM | 3 before |
| C0151 | I Corps | 1944-06-23 | Epsom | OP-EPSOM | 3 before |
| C0223 | 12th Army Group | 1944-08-01 | Cobra | OP-COBRA | 1 after |
| C0289 | Third Army | 1944-08-01 | Cobra | OP-COBRA | 1 after |
| C0319 | VIII Corps | 1944-09-26 | Brest | OP-BREST | 7 after |
| C0399 | 28th Infantry Division | 1944-08-29 | Paris | OP-PARIS | 4 after |
| C0416 | 30th Infantry Division | 1944-08-06 | Mortain | OP-MORTAIN | 1 before |
| C0513 | 6th Armored Division | 1944-09-16 | Pursuit | OP-PURSUIT | 2 after |
| C0522 | Ninth Army | 1944-12-20 | Roer | OP-QUEEN | 4 after |
| C0548 | 106th Infantry Division | 1944-12-11 | Ardennes | OP-BULGE | 5 before |

## Placement decisions and contested boundaries

Each is also stated in the `notes` and `parent_date_exception` columns of the operation row.

- **Cobra** is a child of the Northern France campaign, not Normandy: it opened on 25 July, the first day of the Northern France streamer (the first bombing, on 24 July, was aborted). The 17 Cobra rows keep the Overlord label through the chain (Cobra > Northern France > Overlord).
- **Overlord** ends on 30 August 1944 (Wikipedia; some sources say 25 August). It is an umbrella: it appears in the chain of Normandy and Northern France rows but, because the derived `operation_name` only names an operation on the dates it covers, it labels nothing after 30 August. No Rhineland or Ardennes-Alsace claim has it in its chain.
- **Northern France** is a child of Overlord although the streamer runs to 14 September (`parent_date_exception`).
- **Cherbourg** takes Wikipedia's wider window for the Cotentin operations (6 June-1 July) rather than the 22-27 June fight for the city, so the earlier VII Corps rows keep it.
- **Brittany and Brest**: the end date (19 September) is set from the Green Book narrative; Wikipedia gives only "August-September" for Brittany and 20 September for Brest.
- **Pursuit across France** is a derived phase (19 August-14 September): no source dates it. Pursuit-labelled rows before 19 August are listed above as unmatched.
- **Bulge**: Wikipedia ends the battle on 28 January 1945, the streamer on 25 January.
- **Aachen** starts on 12 September (Wikipedia), before the Rhineland streamer; the Siegfried Line campaign starts on 28 August (Wikipedia) but the Green Book volume on 11 September; the Vosges row takes Wikipedia's wide span (15 September 1944-15 February 1945).
- **Lorraine, Siegfried Line** have no parent because they span two streamers; the derived `campaign` of their claims comes from the date.
- **Operation Queen and Operation Clipper** are operations, so the derived `operation_name` of their rows is now Roer and Clipper (it was blank in the old columns); this is the only change in a derived value (4 rows).
- **German names**: Lüttich (Mortain) and Wacht am Rhein (the Bulge) are rows in the table, linked to the Allied battle as `related`; no claim points at them. Nordwind is not in the table yet because no claim needs it.

## Derived labels against the old columns

build/all_claims.csv still carries `campaign`, `operation_name` and `sub_operation_name`, now derived from the operation chain (see schema/README.md). Differences from the old stored values for `campaign` or `operation_name`: 4. `campaign` is identical for all 566 claims. The derived `sub_operation_name` differs from the old text for 36 claims, in three ways: the old label has no operation row (Return to England, Le Mans, Loire, Seine, Market Garden preparations, Alsace, early Pursuit and Roer rows), so it is blank; it repeated the operation_name (Market Garden) or is now the operation_name (Roer, Clipper); or the label was normalised (Martlet; Epsom to Epsom, Falaise-Argentan to Falaise, Siegfried Line approach to Siegfried Line).

| claim | date | old campaign | old operation_name | old sub | operation_id | derived campaign | derived operation_name |
|---|---|---|---|---|---|---|---|
| C0530 | 1944-11-16 | Rhineland | - | Roer | OP-QUEEN | Rhineland | Roer |
| C0533 | 1944-11-24 | Rhineland | - | Roer | OP-QUEEN | Rhineland | Roer |
| C0531 | 1944-11-16 | Rhineland | - | Roer | OP-QUEEN | Rhineland | Roer |
| C0544 | 1944-11-18 | Rhineland | - | Roer; Clipper | OP-CLIPPER | Rhineland | Clipper |

