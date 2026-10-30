# Activity status: design note and pilot (October 2026)

Status: **rollout in progress** (batch 3 of about 6, October 2026: batch 1, 30 US divisions, 197 rows; batch 2, 28 US and 2 British divisions, 143 rows; batch 3, 11 British divisions, 98 rows; German batch 1, 30 divisions, 148 rows; German batch 2, 30 divisions (25 with values), 45 rows; German batch 3, 26 divisions (22 with values), 25 rows; see section 9). The columns exist in every claim file, but only 161 units carry values. All other rows are blank on purpose: there is no backfill. A blank means "not reviewed for activity". It does not mean the unit was idle.

## 1. Why

The dataset says where a unit was and who commanded it. It does not say whether the unit was available. A division "at Mourmelon" in December 1944 was resting and refitting, while a division "at Elst" was holding the line. Map users and query users keep asking for this difference. Today it is buried in the free text of `current_activity` and `notes`.

## 2. Schema

There are three optional columns, appended at the end of `schema/claims.schema.json`. Each one has a closed vocabulary in `schema/vocabularies.json`.

| column | values | meaning |
|---|---|---|
| `activity_status` | `in_line`, `reserve`, `refitting`, `garrison`, `transit` | The unit's state of availability. This is not its action on the day; that remains `event_type` / `current_activity`. |
| `activity_basis` | `stated`, `inferred` | `stated`: a source cited on the row says it in words. `inferred`: it is deduced from the row or from neighbouring rows. |
| `activity_span` | `start`, `end`, `point` | `start` opens a span, `end` closes the open span of the same value, and `point` holds on the row date only. |

Each row with a value also carries an `Activity:` sentence in `notes`, using the new note label. For a change to an existing row, that sentence gives the old value (blank in the pilot), the new value and the reason. For a new row, it points to the quotation in `Event support`.

**Vocabulary choice.** The five proposed values are kept, with two decisions:

- **Rest is folded into `refitting`.** The official histories almost always pair them ("resting and refitting", "rest and reorganize", German *Auffrischung*), and splitting them cannot be done from the sources.
- **`point` was added to the span vocabulary.** Many good sources describe a state on one day ("in XV Corps reserve") without dating its start or end. Forcing such a row into a span would invent dates.

`transit` is in the vocabulary but unused in the pilot. It is meant for moves between theatres or regions, such as the 1st Canadian Corps leaving Italy or the 1st Airborne returning to England.

## 3. Rules (enforced by `scripts/validate.py`, `check_activity`)

1. The three columns are all blank or all set.
2. A row with an activity has an `Activity:` sentence in `notes`.
3. For each unit, rows are taken in date order. An `end` row must close an open `start` of the same value; otherwise it is an error. Use `point` when there is no start.

`scripts/activity.py` applies these reading rules (they are not validation errors):

- **Implicit end.** A `start` of another value ends the open span on the day before. That end is reported as *inferred*.
- **Open span.** After the last `start` with no later activity row, the value is carried forward as **possible** for at most 30 days (`OPEN_HORIZON_DAYS`); after that there is no answer. The pilot grid showed why: without the horizon, the 4th Canadian Armoured Division read "refitting" until May 1945.
- **Point precedence.** A `point` takes precedence over a span on its own date.
- **After an end.** Once a span ends with an explicit `end`, there is no answer until the next activity row.

## 4. Confidence

The row's `confidence` keeps scoring the **location** under the usual rubric; activity does not change it. The confidence of an activity **answer** is derived and not stored:

- It is the lowest confidence of the rows that bound the answer (the start, plus the end where there is one).
- If either bounding row is `inferred`, or the end is implicit, the answer is capped at **0.3** and its support is reported as `inferred`.

## 5. How answers expose it

- `python scripts/activity.py UNIT DATE` returns the activity, a status (certain or possible), the support (stated or inferred), the confidence and the claim ids. The function `activity.activity_at(unit, date)` is the API.
- `scripts/who_controls.py` prints an `activity:` line under the date header, only for units with activity rows. Answers for every other unit are unchanged.
- `build/all_claims.csv` carries the three columns, because it follows the schema. `build/claims.geojson` does not yet carry them (open question 6).
- Example:

```
US-ABN-101D on 1944-12-05
activity: refitting (certain, inferred, confidence 0.3): inside the span C0573 to C1813
```

## 6. Pilot

The pilot covers 13 units and 25 activity rows: 16 existing rows annotated and 9 new source-backed claims (C1812–C1820, plus place PL0937 Abbeville).

| unit | rows | spans |
|---|---|---|
| US 101st Airborne Division | C0571, C1812 (new), C0573, C1813 (new) | in line on the Island from 5 Oct (inferred) to 27 Nov (MacDonald + Stacey); refitting at Mourmelon from 1 Dec (inferred) to 18 Dec (Cole) |
| US 82nd Airborne Division | C0217, C1814 (new), C1815 (new) | in line from 17 Sep (inferred) to 13 Nov (MacDonald + Stacey); refitting near Reims on 17 Dec (point, Cole) |
| British 1st Airborne Division | C1816 (new) | refitting at Nijmegen from 26 Sep (Ellis); open |
| British 50th Division | C1540, C1817 (new) | in line on the Island from 1 Oct; reserve from about 30 Nov (Stacey); open |
| 2nd Canadian Division | C1324, C1820 (new) | refitting at Dieppe from 1 to 6 Sep (Stacey) |
| 4th Canadian Armoured Division | C1818 (new) | refitting east of Abbeville from 4 Sep (Stacey); open |
| 9th SS Panzer Division | C0886, C0887 | refitting from 3 Sep (stated) to 17 Sep (inferred) |
| 10th SS Panzer Division | C0888, C0889 | refitting from 9 Sep (stated) to 17 Sep (inferred) |
| Fortress Lorient | C1804, C1805 | garrison from 7 Aug 1944 to 10 May 1945 |
| French 2nd Armoured Division | C1647 | XV Corps reserve on 3 Jan 1945 (point) |
| French 3rd Algerian Infantry Division | C1656 | in line at Strasbourg from 5 Jan 1945; open |
| 1st Polish Armoured Division | C1819 (new), C1553 | refitting after the Falaise gap from about 23 Aug (Stacey); in line from 4 Sep (inferred); implicit end of the refit on 3 Sep |
| Polish Independent Parachute Brigade | C1581, C1584 | in line from 21 Sep (inferred) to 26 Sep |

## 7. Risks

- **Silence read as idleness.** A blank activity could be read as "idle". The answer API returns nothing rather than a guess, and the docs say this.
- **Open spans.** Even with the 30-day horizon, an open span can overstate how long a state lasted: the 4th Canadian Armoured Division rejoined the pursuit within days of 4 September. The full rollout should close spans wherever a source allows it.
- **Overlapping states.** The states overlap: a division can be in corps reserve and refitting at once (the 101st in December was both "resting, refitting" and the SHAEF strategic reserve). The pilot records the more specific state, refitting; reserve is used only when nothing more is said.
- **Partial units.** A division with one brigade in the line and two at rest has no single value. The pilot uses the main body. Subordinate rows can carry their own value.
- **Inferred values.** These are cheap to add and could crowd out stated ones. The 0.3 cap keeps them visibly weak, and `Activity:` notes must say why the value was inferred.
- **Schema churn.** Three new columns were added to all 318 claim files. Downstream readers that index columns by position, rather than by name, would break; the build and tools use names.

## 8. Effort estimate for the full dataset

The dataset has 387 units and about 1,800 claims. About 120 divisions and fortresses have enough narrative for spans.

- Annotating existing rows is about 3 minutes per row once the source page is open. With about 2–4 spans per division-year, that is roughly 600–900 rows, or 30–45 hours.
- New end and start claims where the existing rows do not mark the transitions: about 1 new claim per span, so about 400 claims at about 6 minutes each, or roughly 40 hours.
- Review, tests and the grid are about 10 hours.

**Total: about 80–95 hours**, best done nationality by nationality, in batches of about 15 units, like the brigade batches. Corps, armies and brigades could stay blank; their state is mostly that of their divisions.

## 9. Rollout

Scott approved the rollout on 29 October 2026, in branches of about 30 units, starting with divisions and fortresses; corps, armies and brigades may stay blank.

| batch | units | rows | notes |
|---|---|---|---|
| 1 | 30 US divisions (20 infantry, 10 armored) | 113 (89 stated, 24 inferred) | existing rows only, mostly `in_line` points |
| 1 follow-up | the same 30 | +66 new claims (64 stated, 2 inferred); 7 existing rows changed; 179 in all | rest and refit periods, span closures and closing rows at 8 May 1945, from the Wikipedia division articles (CMH combat chronicles); occupation is `garrison` |
| 1 second source | the same 30 | +16 new claims; 195 in all | 8 May 1945 rows for 8 more divisions and 4 span closures from the CMH combat chronicles; 4 divisions still have no 8 May row |
| 1, 28th refit | 28th Infantry Division | +2 (C1903, C1904); 197 in all | Neufchâteau refit, 22 December 1944 to 2 January 1945, from the CMH combat chronicle |
| 2 | the remaining 28 US divisions; the British 11th Armoured and 15th (Scottish) Divisions | 142 (124 stated, 18 inferred): 60 existing rows labelled, 82 new claims (C1905-C1986) | done in one pass: labels, rest and refit, garrison, span closures and 8 May 1945 rows; US from the CMH combat chronicles, British from Wikipedia; 19 of 30 divisions have an 8 May row, 10 spans stay open |
| 3 | the remaining 11 British divisions (6th Airborne; 7th, 79th and Guards Armoured; 3rd, 43rd, 49th, 51st, 52nd, 53rd and 59th Infantry) | 98 (89 stated, 9 inferred): 89 existing rows labelled, 9 new claims (C1988-C1996) | done in one pass from Wikipedia (and the US 75th Division combat chronicle for the 6th Airborne relief); 2 of 11 divisions have an 8 May row; undated rests and reserves deferred |
| German 1 | 30 German divisions with the most claims | 148 existing rows labelled (122 stated, 26 inferred); no new claims | labels only, all points; order-of-battle listings, assignments, command changes, surrenders and destructions stay blank; 56 German divisions remain |
| German 2 | the next 30 unlabelled German divisions by claim count | 45 existing rows labelled (34 stated, 11 inferred) in 25 divisions; no new claims | labels only, all points; 5 divisions have listings only and stay blank; 26 German divisions remain for batch 3 |
| German 3 | the last 26 unlabelled German divisions | 25 existing rows labelled (20 stated, 5 inferred) in 22 divisions; no new claims | labels only, all points; 4 divisions have no state-bearing row; German divisions complete |
| 2, 86th 8 May | 86th Infantry Division | +1 (C1987); 143 in all | in_line point at Burghausen, 0.3, from the CMH combat chronicle; 20 of 30 divisions now have an 8 May row |
