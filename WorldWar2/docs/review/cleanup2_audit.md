# Clean-up 2: audit of the late-war Western Front data (29 October 2026)

Scope: every claim, relation and place of the Western Front, 6 June 1944 to 8 May 1945, at division level and above, all nationalities in the data (1,657 claims). Only sources already in the data were used. Each finding is listed with what was done; anything uncertain is an open question with a recommendation at the end. The fixes are in `docs/changelog.md` (section cleanup-2-late-war-west).

## Summary

| check | findings | fixed | left (why) |
|---|---:|---:|---|
| Conflict groups | 24 | 0 | all 24 are internally consistent (a preferred row or all disputed; the confidence caps hold); 9 are open because no source read settles them |
| Rows at 0.3 or 0.5 citing two source families | 227 | 1 | 76 read, 1 raised; 67 pair the CMH with a compilation of the same CMH lists; 84 not read row by row (open question 1) |
| Date gaps over 30 days, divisions | 231 gaps in 121 divisions | 0 | no source in the data covers them; adding rows needs a new batch |
| Movement faster than 80 km a day (consecutive rows) | 7 (+3 known coordinate warnings) | 0 | all explained by the sources (rail or road moves, signing places, representative points) |
| Command relations: overlaps, wrong for the date | temporal audit: 5 overlap, 8 start disagreements, 16 relisted after end, 194 undated parent changes, 1 undated change, 1 same-day place | 0 | all were checked against the notes; the overlaps and changes are documented or are real returns to an earlier headquarters |
| Missing or broken references, places, units, evidence links | 0 | 0 | none |
| Duplicate places | 4 true duplicates (of 131 pairs closer than 1 km) | 4 | the other pairs are deliberate sector or area names on a town point |
| Duplicate claims (same unit, day and place) | 5 pairs | 0 | each pair is two different events or a conflict group |
| Coordinate outliers (outside the theatre, or more than 5 km from the place) | 0 | 0 | none |
| Validator warnings | 25 | 1 | 24 left, each explained in its row (open question 2 for four of them) |

## 1. Conflict groups (24)

| group | rows | status |
|---|---|---|
| Seventh Army headquarters move, 28 or 29 June 1944 | 1944-06-28 preferred 0.7, 1944-06-29 alternate 0.5 | has a preferred row |
| 709th Division, end at Cherbourg, 26 or 29 June 1944 | 1944-06-26 preferred 0.7, 1944-06-29 alternate 0.5 | has a preferred row |
| LXXXIV Corps command and headquarters, 15 to 17 June 1944 | 1944-06-15 disputed 0.3, 1944-06-16 disputed 0.3, 1944-06-17 disputed 0.3 | all disputed; open (commander and handover dates not settled by any source read) |
| LXXXIV Corps, 10 or 12 June 1944 | 1944-06-10 alternate 0.3, 1944-06-12 preferred 0.5 | has a preferred row |
| 21st Army Group, 7 or 8 June 1944 | 1944-06-07 alternate 0.5, 1944-06-08 preferred 0.7 | has a preferred row |
| 21st Army Group, 22 or 23 June 1944 | 1944-06-22 disputed 0.5, 1944-06-23 disputed 0.5 | all disputed; open |
| 82nd Airborne Division, 17 or 19 June 1944 | 1944-06-17 disputed 0.5, 1944-06-19 disputed 0.5 | all disputed; open |
| 1st Infantry Division, 12 or 13 June 1944 | 1944-06-12 alternate 0.5, 1944-06-13 preferred 0.5 | has a preferred row |
| XIX Corps, 13 or 14 June 1944 | 1944-06-13 preferred 0.3, 1944-06-14 alternate 0.3 | has a preferred row |
| 51st Division, 7 or 8 June 1944 | 1944-06-07 preferred 0.5, 1944-06-08 alternate 0.5 | has a preferred row |
| 7th Armoured Division, 7 or 12 June 1944 | 1944-06-07 preferred 0.5, 1944-06-12 alternate 0.5 | has a preferred row |
| VIII Corps, 5 or 10 September 1944 | 1944-09-05 alternate 0.5, 1944-09-10 preferred 0.5 | has a preferred row |
| VIII Corps, 18 or 19 September 1944 | 1944-09-18 preferred 0.7, 1944-09-19 alternate 0.5 | has a preferred row |
| 89th Division Moselle crossing, 15 to 17 March 1945 | 1945-03-15 disputed 0.3, 1945-03-16 disputed 0.3, 1945-03-17 disputed 0.3 | all disputed; open |
| Model takes Army Group B, 17 or 19 August 1944 | 1944-08-19 disputed 0.3, 1944-08-17 disputed 0.3 | all disputed; open by Scott's earlier decision |
| Eberbach replaces Geyr, 2 or 4 July 1944 | 1944-07-04 preferred 0.3, 1944-07-02 alternate 0.3, 1944-07-02 alternate 0.3 | has a preferred row |
| Panzer Group West renamed Fifth Panzer Army, 1 or 5 August 1944 | 1944-08-05 preferred 0.3, 1944-08-01 alternate 0.3 | has a preferred row |
| Kluge takes Army Group B, 17 or 19 July 1944 | 1944-07-17 preferred 0.3, 1944-07-19 alternate 0.3 | has a preferred row; kept open on 28 October 2026 |
| Panzer Lehr under the LXXXIV Corps, June or July 1944 | 1944-06-15 alternate 0.3, 1944-07-15 alternate 0.3, 1944-07-15 preferred 0.5 | settled on 28 October 2026 |
| 12th SS Panzer Division corps, July 1944 | 1944-07-15 disputed 0.3, 1944-07-15 disputed 0.3 | all disputed; open |
| 716th Division, southern France or Normandy, July 1944 | 1944-07-10 preferred 0.5, 1944-07-15 alternate 0.3 | settled on 28 October 2026 (the two rows are 5 days apart with different event types: flagged by the temporal audit, explained in the notes) |
| 711th Division corps, July 1944 | 1944-07-15 disputed 0.3, 1944-07-15 disputed 0.3 | all disputed; open |
| LXXX Corps under the Seventh Army, September or October 1944 | 1944-09-18 preferred 0.5, 1944-10-13 alternate 0.3 | has a preferred row; open by design |
| First Parachute Army change of commander, 20 or 28 March 1945 | 1945-03-28 preferred 0.5, 1945-03-20 alternate 0.3 | has a preferred row (Scott confirmed keeping both) |

No group breaks a rule: no preferred row above 0.7, no alternate or disputed row above 0.5, and no group mixes a preferred row with disputed rows. No source already in the data settles an open group, so none was changed.

## 2. Confidence: rows that may be under-rated

227 rows at 0.3 or 0.5 (outside conflict groups) cite references from two source families (coordinate and geocoder references not counted).

- **76 rows whose notes state two families were read.** One was raised: the German First Army passing to Army Group G on 8 September 1944, 0.5 to 0.7 (both families give the day and describe the army sector; approximate place). In the other 75 the second family supports only the day, only the unit or the context, gives a month-level date (Lexikon tables), or the point is a representative headquarters point that the rubric holds at 0.3; none can be raised without a new source.
- **67 rows pair the CMH with the World War II by Day lists.** That site compiles the CMH command-post lists, so it is the same family (methodology, "Corps and army command-post places"). No change.
- **84 other rows** cite two families whose roles the notes do not state (mostly CMH with Wikipedia: 40; CMH with the Lexikon or Nafziger: 18). Not read row by row in this pass: open question 1.
- No row was found over-rated (no 0.9 row without two families).

## 3. Date gaps over 30 days (divisions)

231 gaps in 121 divisions: Germany 116, US 62, UK 33, France 12, Canada 6, Poland 2. The longest are the US divisions between their autumn 1944 rows and April 1945 (up to 232 days: the batches were milestone passes, and the 1945 US batches did not write rows for divisions in quiet sectors). None can be filled from sources already cited without reading them again for new rows, which is new work, not a clean-up. The full list is in the appendix. A gap means the position is unknown, not unchanged.

## 4. Movement speed

Seven consecutive-row pairs move more than 80 km a day (outside conflict groups); each was checked:

- the German armed forces signed in Reims on 7 May and in Berlin on 8 May 1945: signing places, not a move.
- Panzer Lehr Division from the Chartres area on 7 June to Thury-Harcourt on 8 June 1944: the sourced 90-mile drive (approach-route row, 50 km).
- 29th Infantry Division from Brittany (21 September) to Limburg (29 September 1944): an 8-day move after Brest; plausible.
- VIII Corps from Saint-Malo (17 August) to Lesneven (18 August 1944): the source states a 120-mile command-post move.
- 6th Armored Division, Châteaubriant (16 September) to Colombey-les-Belles (19 September 1944): a three-day road march, about 180 km a day; plausible for an armored division.
- 12th Army Group, 1 to 3 September 1944: the first row is a 50 km representative point.
- 7th Armored Division, Sainte-Suzanne (13 August) to Courville-sur-Eure (15 August 1944): about 90 km a day; plausible, but see open question 3 on the place.

The three known coordinate-check warnings (4th Armored Division 14-15 August, 30th Division 14-15 August, 94th Division 8-9 September 1944) stay as documented in the methodology. No change.

## 5. Command relations

The temporal audit (`scripts/audit_temporal_relationships.py`) was read for the Western Front period:

- **Overlaps (5):** the 95th Division in March 1945 (XIX Corps attached in the Green Book, XIII Corps operational control in the table; a kept source disagreement, Scott decided on 27 October 2026) and the XVIII Airborne Corps in March 1945 (Second Army for Plunder and First Army; the First Army relation is split and documented). No change.
- **Start disagreements (8)** and **relisted after end (16):** a unit that returns to an earlier headquarters (II Canadian Corps under Second Army again in March 1945, the 2d French Armored Division back in XV Corps in January 1945, the 3rd Canadian Division under XXX Corps twice). These are real returns, recorded as separate intervals. No change.
- **Undated parent changes (194):** consecutive rows of a unit name different parents and no relation dates the change; each such relation is closed as inferred (the day before the next claim) and annotated, as the method requires. No change; a change can only be dated with a new source.
- **Undated change (1):** VII Corps passing the 30th Division and a combat command to XIX Corps on 28 July 1944: the 30th Division relation to XIX Corps starts on 28 July (table row); the audit looks for a relation of the corps itself. No change.
- **Same-day places (1):** First Army on 25 July 1944 at the Cobra penetration area and at its headquarters, 26 km apart: an event row and a headquarters row. No change.
- No relation names a missing unit; 24 relations have no higher unit on purpose (explicit unknown parent). No claim lists a parent that has no relation covering its date.

## 6. References, places and duplicates

- Every claim has at least one reference; every reference, place and evidence link resolves.
- **Duplicate places merged (4):** Hébécrevon (Manche), Stolberg (Rhineland), Évrecy (Calvados) and Bains-les-Bains (Vosges) were each entered twice by different batches; the newer row is retired and its 7 claims re-pointed (see the changelog). 127 other place pairs closer than 1 km are deliberate: a sector, front or assembly area named on the point of its town.
- **Same unit, day and place (5 pairs):** the 709th Division at Cherbourg on 29 June 1944 (destruction and a conflict-group surrender row), Army Group B on 17 August 1944 (Model's arrival and a disputed command row), the Seventh Army on 20 August 1944 (command change and subordination), Panzer Group West on 2 July 1944 (two alternate rows of one group) and Panzer Lehr on 15 July 1944 (one conflict group). Different events or one group each; no change.

## 7. Coordinates

No claim is outside the theatre box (42-56 N, 5 W-17 E) and none is more than 5 km from its place without an override. `check_coordinates.py` shows the 3 known speed warnings and 7 explained exceptions. Four British corps or army rows record a front-line point at 3 or 5 km (validator warnings): open question 2.

## Open questions (each with a recommendation)

1. **84 rows at 0.3 or 0.5 with two cited families whose roles are not stated in the notes.** Recommendation: a short row-by-row read against the cited pages; raise only where both families give the day and the place.
2. **Four British front-line rows** (Second Army 29 August 1944, XII Corps 4 August 1944, XXX Corps 21 August and 17 September 1944) are corps or army sectors recorded as exact front-line points at 3 or 5 km. Ellis names the place where the front stood, so the point is sourced. Recommendation: keep the points and widen the precision to 10 km, which is the rule for a corps sector; this needs your go because it changes four values.
3. **7th Armored Division command post of 13 August 1944**, "Ste-Suzanne, Manche" in the CMH list: the Manche commune (Sainte-Suzanne-sur-Vire) fits the division's landing, while Sainte-Suzanne in Mayenne would fit XX Corps' assembly near Le Mans. Recommendation: keep the CMH reading; check it if the division's after-action report is ever read.
4. **The 231 date gaps.** Recommendation: leave them; fill the longest US gaps (autumn 1944 to April 1945) only in a later batch, on your go.
5. **The nine open conflict groups.** Recommendation: leave them until a new source (for example the OKW war diary volume for 1944-45) is read.

## Scott's answers (29 October 2026)

Scott accepted all five recommendations.

1. Done: the 84 rows were read one by one; 6 were raised from 0.5 to 0.7 because both families give the day and the place (82nd Airborne Division landing and command post at Groesbeek, 17 September 1944; 4th Armored Division at Utah Beach, 11 July 1944; VI Corps Dragoon assault, 15 August 1944; VIII Corps at Avranches, 30 July 1944; 89th Infantry Division at St. Goar, 26 March 1945). The other 78 are unchanged.
2. Done: the four British front-line rows keep their points and now carry a precision of 10 km; validator warnings fall from 24 to 20.
3. Accepted, no change: the 7th Armored Division command post of 13 August 1944 stays as the CMH list gives it.
4. Accepted, no change: the 231 date gaps are left for a later batch.
5. Accepted, no change: the 9 open conflict groups wait for a new source.

## Appendix: date gaps over 30 days (divisions)

| division | last row | next row | days |
|---|---|---|---:|
| 2nd Canadian Infantry Division (Canada) | 1944-12-29 | 1945-02-08 | 41 |
| 3rd Canadian Infantry Division (Canada) | 1944-11-13 | 1945-02-08 | 87 |
| 4th Canadian Armoured Division (Canada) | 1944-08-26 | 1944-10-18 | 53 |
| 4th Canadian Armoured Division (Canada) | 1944-11-04 | 1944-12-23 | 49 |
| 4th Canadian Armoured Division (Canada) | 1944-12-23 | 1945-01-26 | 34 |
| 5th Canadian Armoured Division (Canada) | 1945-02-28 | 1945-03-31 | 31 |
| French 10th Infantry Division (France) | 1944-10-01 | 1945-02-05 | 127 |
| French 14th Infantry Division (France) | 1945-02-09 | 1945-05-08 | 88 |
| French 1st Armoured Division (France) | 1944-11-20 | 1945-04-23 | 154 |
| French 1st Infantry Division (1st Free French Division) (France) | 1944-09-03 | 1945-01-23 | 142 |
| French 2nd Armoured Division (France) | 1944-09-28 | 1944-11-23 | 56 |
| French 2nd Armoured Division (France) | 1945-02-08 | 1945-04-18 | 69 |
| French 2nd Moroccan Infantry Division (France) | 1944-10-14 | 1944-11-25 | 42 |
| French 2nd Moroccan Infantry Division (France) | 1944-11-25 | 1945-03-31 | 126 |
| French 3rd Algerian Infantry Division (France) | 1944-08-28 | 1945-01-05 | 130 |
| French 3rd Algerian Infantry Division (France) | 1945-01-05 | 1945-03-31 | 85 |
| French 4th Moroccan Mountain Division (France) | 1945-02-05 | 1945-05-02 | 86 |
| French 9th Colonial Infantry Division (France) | 1944-08-27 | 1945-02-06 | 163 |
| 10th SS Panzer Division Frundsberg (Germany) | 1944-07-17 | 1944-09-09 | 54 |
| 10th SS Panzer Division Frundsberg (Germany) | 1944-10-15 | 1944-12-15 | 61 |
| 10th SS Panzer Division Frundsberg (Germany) | 1944-12-15 | 1945-01-16 | 32 |
| 116th Panzer Division (Germany) | 1944-09-12 | 1944-10-15 | 33 |
| 116th Panzer Division (Germany) | 1944-11-04 | 1944-12-16 | 42 |
| 116th Panzer Division (Germany) | 1944-12-16 | 1945-03-26 | 100 |
| 11th Panzer Division (Germany) | 1944-11-10 | 1945-02-23 | 105 |
| 11th Panzer Division (Germany) | 1945-03-11 | 1945-05-04 | 54 |
| 12th SS Panzer Division Hitlerjugend (Germany) | 1944-07-18 | 1944-08-20 | 33 |
| 12th SS Panzer Division Hitlerjugend (Germany) | 1944-10-15 | 1944-11-15 | 31 |
| 12th SS Panzer Division Hitlerjugend (Germany) | 1944-11-15 | 1944-12-16 | 31 |
| 12th Volksgrenadier Division (Germany) | 1944-09-17 | 1944-11-16 | 60 |
| 159th Infantry Division (Germany) | 1944-11-07 | 1944-12-15 | 38 |
| 159th Infantry Division (Germany) | 1944-12-15 | 1945-01-20 | 36 |
| 15th Panzergrenadier Division (Germany) | 1944-10-15 | 1944-11-17 | 33 |
| 15th Panzergrenadier Division (Germany) | 1944-12-15 | 1945-03-24 | 99 |
| 16th Volksgrenadier Division (Germany) | 1944-11-07 | 1945-01-20 | 74 |
| 176th Infantry Division (Germany) | 1944-11-15 | 1945-01-15 | 61 |
| 176th Infantry Division (Germany) | 1945-01-15 | 1945-04-01 | 76 |
| 17th SS Panzergrenadier Division Götz von Berlichingen (Germany) | 1944-07-24 | 1944-09-05 | 43 |
| 17th SS Panzergrenadier Division Götz von Berlichingen (Germany) | 1944-09-17 | 1944-11-08 | 52 |
| 17th SS Panzergrenadier Division Götz von Berlichingen (Germany) | 1944-11-08 | 1944-12-15 | 37 |
| 17th SS Panzergrenadier Division Götz von Berlichingen (Germany) | 1944-12-15 | 1945-04-02 | 108 |
| 180th Infantry Division (Germany) | 1944-12-15 | 1945-03-15 | 90 |
| 180th Infantry Division (Germany) | 1945-03-15 | 1945-04-15 | 31 |
| 189th Infantry Division (Germany) | 1944-11-07 | 1944-12-15 | 38 |
| 189th Infantry Division (Germany) | 1944-12-15 | 1945-01-20 | 36 |
| 198th Infantry Division (Germany) | 1944-11-10 | 1944-12-15 | 35 |
| 198th Infantry Division (Germany) | 1944-12-15 | 1945-01-20 | 36 |
| 198th Infantry Division (Germany) | 1945-01-20 | 1945-04-15 | 85 |
| 1st SS Panzer Division Leibstandarte SS Adolf Hitler (Germany) | 1944-09-15 | 1944-12-16 | 92 |
| 21st Panzer Division (Germany) | 1944-07-08 | 1944-09-21 | 75 |
| 21st Panzer Division (Germany) | 1944-09-22 | 1944-11-13 | 52 |
| 21st Panzer Division (Germany) | 1944-11-13 | 1944-12-15 | 32 |
| 245th Infantry Division (Germany) | 1944-10-15 | 1944-11-15 | 31 |
| 245th Infantry Division (Germany) | 1944-11-15 | 1945-01-07 | 53 |
| 245th Infantry Division (Germany) | 1945-01-07 | 1945-04-15 | 98 |
| 246th Volksgrenadier Division (Germany) | 1944-10-21 | 1945-02-27 | 129 |
| 25th Panzergrenadier Division (Germany) | 1944-11-12 | 1944-12-15 | 33 |
| 269th Infantry Division (Germany) | 1944-12-15 | 1945-01-18 | 34 |
| 26th Volksgrenadier Division (Germany) | 1945-01-04 | 1945-03-17 | 72 |
| 272nd Volksgrenadier Division (Germany) | 1944-12-16 | 1945-03-17 | 91 |
| 275th Infantry Division (Germany) | 1944-08-06 | 1944-09-12 | 37 |
| 275th Infantry Division (Germany) | 1944-09-12 | 1944-10-15 | 33 |
| 275th Infantry Division (Germany) | 1944-10-15 | 1944-11-16 | 32 |
| 276th Volksgrenadier Division (Germany) | 1944-12-16 | 1945-02-06 | 52 |
| 277th Volksgrenadier Division (Germany) | 1944-12-16 | 1945-03-17 | 91 |
| 2nd Panzer Division (Germany) | 1944-06-13 | 1944-08-07 | 55 |
| 2nd Panzer Division (Germany) | 1944-10-15 | 1944-12-16 | 62 |
| 2nd Panzer Division (Germany) | 1944-12-16 | 1945-01-22 | 37 |
| 2nd SS Panzer Division Das Reich (Germany) | 1944-08-07 | 1944-09-15 | 39 |
| 2nd SS Panzer Division Das Reich (Germany) | 1944-10-15 | 1945-01-03 | 80 |
| 326th Volksgrenadier Division (Germany) | 1944-12-16 | 1945-02-06 | 52 |
| 326th Volksgrenadier Division (Germany) | 1945-02-06 | 1945-03-17 | 39 |
| 338th Infantry Division (Germany) | 1944-11-07 | 1944-12-15 | 38 |
| 338th Infantry Division (Germany) | 1944-12-15 | 1945-01-20 | 36 |
| 338th Infantry Division (Germany) | 1945-01-20 | 1945-02-25 | 36 |
| 338th Infantry Division (Germany) | 1945-02-25 | 1945-04-15 | 49 |
| 340th Volksgrenadier Division (Germany) | 1944-11-21 | 1945-01-04 | 44 |
| 340th Volksgrenadier Division (Germany) | 1945-01-04 | 1945-03-13 | 68 |
| 346th Infantry Division (Germany) | 1944-06-06 | 1944-07-15 | 39 |
| 346th Infantry Division (Germany) | 1944-07-15 | 1944-12-15 | 153 |
| 346th Infantry Division (Germany) | 1944-12-15 | 1945-04-15 | 121 |
| 347th Infantry Division (Germany) | 1944-09-15 | 1944-11-27 | 73 |
| 347th Infantry Division (Germany) | 1944-11-27 | 1945-01-24 | 58 |
| 353rd Infantry Division (Germany) | 1944-10-15 | 1944-11-26 | 42 |
| 353rd Infantry Division (Germany) | 1944-11-26 | 1945-02-15 | 81 |
| 353rd Infantry Division (Germany) | 1945-02-15 | 1945-04-15 | 59 |
| 361st Volksgrenadier Division (Germany) | 1944-11-07 | 1945-04-15 | 159 |
| 3rd Fallschirmjäger Division (Germany) | 1944-06-10 | 1944-07-11 | 31 |
| 3rd Fallschirmjäger Division (Germany) | 1944-07-18 | 1944-08-20 | 33 |
| 3rd Fallschirmjäger Division (Germany) | 1944-09-04 | 1944-11-26 | 83 |
| 3rd Fallschirmjäger Division (Germany) | 1944-12-16 | 1945-02-15 | 61 |
| 3rd Panzergrenadier Division (Germany) | 1944-09-17 | 1944-11-17 | 61 |
| 3rd Panzergrenadier Division (Germany) | 1944-11-17 | 1945-03-17 | 120 |
| 49th Infantry Division (Germany) | 1944-09-12 | 1944-10-15 | 33 |
| 553rd Volksgrenadier Division (Germany) | 1944-09-19 | 1944-11-19 | 61 |
| 553rd Volksgrenadier Division (Germany) | 1944-11-19 | 1945-01-05 | 47 |
| 559th Volksgrenadier Division (Germany) | 1944-09-27 | 1944-11-09 | 43 |
| 59th Infantry Division (Germany) | 1944-10-15 | 1945-02-15 | 123 |
| 59th Infantry Division (Germany) | 1945-02-15 | 1945-04-15 | 59 |
| 5th Fallschirmjäger Division (Germany) | 1944-07-24 | 1944-09-04 | 42 |
| 5th Fallschirmjäger Division (Germany) | 1944-09-16 | 1944-12-16 | 91 |
| 5th Fallschirmjäger Division (Germany) | 1945-01-09 | 1945-02-15 | 37 |
| 62nd Volksgrenadier Division (Germany) | 1944-12-16 | 1945-03-17 | 91 |
| 6th Fallschirmjäger Division (Germany) | 1944-09-04 | 1944-12-15 | 102 |
| 6th Fallschirmjäger Division (Germany) | 1944-12-15 | 1945-02-13 | 60 |
| 708th Volksgrenadier Division (Germany) | 1944-11-10 | 1945-01-20 | 71 |
| 70th Infantry Division (Germany) | 1944-09-18 | 1944-11-06 | 49 |
| 711th Infantry Division (Germany) | 1944-06-06 | 1944-07-15 | 39 |
| 716th Static Infantry Division (Germany) | 1944-06-06 | 1944-07-10 | 34 |
| 716th Static Infantry Division (Germany) | 1944-07-15 | 1944-09-15 | 62 |
| 716th Static Infantry Division (Germany) | 1944-09-15 | 1944-11-10 | 56 |
| 716th Static Infantry Division (Germany) | 1944-11-10 | 1945-01-20 | 71 |
| 716th Static Infantry Division (Germany) | 1945-01-20 | 1945-04-14 | 84 |
| 719th Infantry Division (Germany) | 1944-09-15 | 1944-12-15 | 91 |
| 7th Fallschirmjäger Division (Germany) | 1945-01-10 | 1945-02-15 | 36 |
| 7th Fallschirmjäger Division (Germany) | 1945-02-15 | 1945-04-15 | 59 |
| 84th Infantry Division (Germany) | 1944-10-15 | 1944-12-15 | 61 |
| 84th Infantry Division (Germany) | 1944-12-15 | 1945-02-15 | 62 |
| 84th Infantry Division (Germany) | 1945-02-15 | 1945-03-24 | 37 |
| 85th Infantry Division (Germany) | 1944-12-15 | 1945-02-15 | 62 |
| 89th Infantry Division (Germany) | 1944-07-15 | 1944-10-15 | 92 |
| 89th Infantry Division (Germany) | 1944-11-04 | 1945-02-15 | 103 |
| 8th Fallschirmjäger Division (Germany) | 1945-01-15 | 1945-02-27 | 43 |
| 8th Fallschirmjäger Division (Germany) | 1945-02-27 | 1945-04-10 | 42 |
| 9th Panzer Division (Germany) | 1944-08-10 | 1944-09-16 | 37 |
| 9th Panzer Division (Germany) | 1944-10-15 | 1944-11-17 | 33 |
| 9th Panzer Division (Germany) | 1945-01-04 | 1945-02-23 | 50 |
| 9th Panzer Division (Germany) | 1945-03-09 | 1945-04-18 | 40 |
| 9th SS Panzer Division Hohenstaufen (Germany) | 1944-07-11 | 1944-09-03 | 54 |
| 9th SS Panzer Division Hohenstaufen (Germany) | 1944-10-15 | 1945-01-05 | 82 |
| Panzer Lehr Division (Germany) | 1944-07-25 | 1944-09-15 | 52 |
| Panzer Lehr Division (Germany) | 1944-09-16 | 1944-11-23 | 68 |
| Panzer Lehr Division (Germany) | 1944-12-16 | 1945-01-22 | 37 |
| Panzer Lehr Division (Germany) | 1945-01-22 | 1945-03-09 | 46 |
| 1st Polish Armoured Division (Poland) | 1944-11-09 | 1944-12-30 | 51 |
| 1st Polish Armoured Division (Poland) | 1945-01-07 | 1945-04-08 | 91 |
| 11th Armoured Division (UK) | 1944-09-04 | 1945-02-27 | 176 |
| 11th Armoured Division (UK) | 1945-02-27 | 1945-04-11 | 43 |
| 15th (Scottish) Infantry Division (UK) | 1944-08-27 | 1945-02-08 | 165 |
| 15th (Scottish) Infantry Division (UK) | 1945-02-18 | 1945-03-24 | 34 |
| 3rd Infantry Division (UK) | 1944-06-06 | 1944-07-08 | 32 |
| 3rd Infantry Division (UK) | 1944-07-18 | 1945-01-19 | 185 |
| 3rd Infantry Division (UK) | 1945-01-19 | 1945-02-25 | 37 |
| 3rd Infantry Division (UK) | 1945-03-01 | 1945-04-06 | 36 |
| 43rd (Wessex) Infantry Division (UK) | 1944-08-25 | 1944-11-18 | 85 |
| 43rd (Wessex) Infantry Division (UK) | 1944-11-18 | 1945-01-24 | 67 |
| 49th (West Riding) Infantry Division (UK) | 1944-07-15 | 1944-09-10 | 57 |
| 49th (West Riding) Infantry Division (UK) | 1944-09-10 | 1944-12-04 | 85 |
| 49th (West Riding) Infantry Division (UK) | 1944-12-04 | 1945-01-18 | 45 |
| 50th (Northumbrian) Infantry Division (UK) | 1944-06-14 | 1944-07-30 | 46 |
| 50th (Northumbrian) Infantry Division (UK) | 1944-07-30 | 1944-09-17 | 49 |
| 50th (Northumbrian) Infantry Division (UK) | 1944-10-01 | 1944-11-09 | 39 |
| 51st (Highland) Infantry Division (UK) | 1944-06-23 | 1944-08-14 | 52 |
| 51st (Highland) Infantry Division (UK) | 1944-09-11 | 1945-01-11 | 122 |
| 51st (Highland) Infantry Division (UK) | 1945-02-09 | 1945-03-23 | 42 |
| 52nd (Lowland) Infantry Division (UK) | 1944-11-03 | 1945-01-18 | 76 |
| 52nd (Lowland) Infantry Division (UK) | 1945-01-21 | 1945-02-21 | 31 |
| 52nd (Lowland) Infantry Division (UK) | 1945-03-09 | 1945-04-20 | 42 |
| 53rd (Welsh) Infantry Division (UK) | 1944-08-05 | 1944-10-27 | 83 |
| 53rd (Welsh) Infantry Division (UK) | 1944-10-27 | 1945-01-03 | 68 |
| 53rd (Welsh) Infantry Division (UK) | 1945-01-03 | 1945-02-08 | 36 |
| 6th Airborne Division (UK) | 1944-06-14 | 1944-08-21 | 68 |
| 6th Airborne Division (UK) | 1944-08-26 | 1945-01-03 | 130 |
| 6th Airborne Division (UK) | 1945-01-03 | 1945-03-24 | 80 |
| 7th Armoured Division (UK) | 1944-06-14 | 1944-07-19 | 35 |
| 7th Armoured Division (UK) | 1944-08-31 | 1945-01-17 | 139 |
| 7th Armoured Division (UK) | 1945-01-17 | 1945-03-27 | 69 |
| Guards Armoured Division (UK) | 1944-07-31 | 1944-08-31 | 31 |
| Guards Armoured Division (UK) | 1944-09-20 | 1945-03-06 | 167 |
| 100th Infantry Division (US) | 1944-11-12 | 1945-04-27 | 166 |
| 101st Airborne Division (US) | 1944-08-12 | 1944-09-17 | 36 |
| 101st Airborne Division (US) | 1944-10-05 | 1944-11-09 | 35 |
| 101st Airborne Division (US) | 1945-01-15 | 1945-05-04 | 109 |
| 103rd Infantry Division (US) | 1944-11-20 | 1945-05-04 | 165 |
| 104th Infantry Division (US) | 1944-10-23 | 1945-04-12 | 171 |
| 10th Armored Division (US) | 1944-11-08 | 1944-12-17 | 39 |
| 10th Armored Division (US) | 1944-12-17 | 1945-03-01 | 74 |
| 10th Armored Division (US) | 1945-03-01 | 1945-04-30 | 60 |
| 11th Armored Division (US) | 1945-01-16 | 1945-03-08 | 51 |
| 11th Armored Division (US) | 1945-03-08 | 1945-05-06 | 59 |
| 12th Armored Division (US) | 1945-02-04 | 1945-03-20 | 44 |
| 12th Armored Division (US) | 1945-03-24 | 1945-04-24 | 31 |
| 14th Armored Division (US) | 1945-01-31 | 1945-03-24 | 52 |
| 14th Armored Division (US) | 1945-03-24 | 1945-04-30 | 37 |
| 17th Airborne Division (US) | 1945-01-04 | 1945-03-24 | 79 |
| 1st Infantry Division (US) | 1944-06-13 | 1944-07-15 | 32 |
| 1st Infantry Division (US) | 1944-08-25 | 1945-03-09 | 196 |
| 1st Infantry Division (US) | 1945-03-09 | 1945-04-19 | 41 |
| 28th Infantry Division (US) | 1944-09-26 | 1944-12-16 | 81 |
| 29th Infantry Division (US) | 1944-06-17 | 1944-08-02 | 46 |
| 2nd Armored Division (US) | 1944-06-13 | 1944-07-18 | 35 |
| 2nd Armored Division (US) | 1944-09-12 | 1945-04-12 | 212 |
| 2nd Infantry Division (US) | 1944-06-13 | 1944-08-05 | 53 |
| 2nd Infantry Division (US) | 1944-09-30 | 1945-02-01 | 124 |
| 2nd Infantry Division (US) | 1945-02-01 | 1945-04-15 | 73 |
| 30th Infantry Division (US) | 1944-09-12 | 1945-04-17 | 217 |
| 3rd Armored Division (US) | 1944-09-21 | 1945-04-11 | 202 |
| 3rd Infantry Division (US) | 1944-09-20 | 1945-04-20 | 212 |
| 42nd Infantry Division (US) | 1945-03-22 | 1945-04-29 | 38 |
| 44th Infantry Division (US) | 1944-09-15 | 1945-05-05 | 232 |
| 45th Infantry Division (US) | 1944-09-20 | 1945-04-16 | 208 |
| 4th Armored Division (US) | 1944-09-19 | 1944-12-22 | 94 |
| 4th Armored Division (US) | 1945-01-10 | 1945-04-04 | 84 |
| 4th Infantry Division (US) | 1944-09-30 | 1945-01-29 | 121 |
| 5th Armored Division (US) | 1944-09-12 | 1945-04-12 | 212 |
| 5th Infantry Division (US) | 1944-09-13 | 1945-02-07 | 147 |
| 5th Infantry Division (US) | 1945-02-07 | 1945-03-22 | 43 |
| 63rd Infantry Division (US) | 1945-01-20 | 1945-03-15 | 54 |
| 65th Infantry Division (US) | 1945-03-19 | 1945-04-27 | 39 |
| 66th Infantry Division (US) | 1945-01-01 | 1945-03-31 | 89 |
| 69th Infantry Division (US) | 1945-03-06 | 1945-04-18 | 43 |
| 75th Infantry Division (US) | 1944-12-22 | 1945-01-31 | 40 |
| 7th Armored Division (US) | 1944-09-30 | 1945-01-23 | 115 |
| 80th Infantry Division (US) | 1944-09-29 | 1945-02-07 | 131 |
| 80th Infantry Division (US) | 1945-02-07 | 1945-05-05 | 87 |
| 82nd Airborne Division (US) | 1944-09-17 | 1944-12-18 | 92 |
| 82nd Airborne Division (US) | 1944-12-18 | 1945-05-03 | 136 |
| 83rd Infantry Division (US) | 1944-09-21 | 1945-04-13 | 204 |
| 84th Infantry Division (US) | 1944-11-18 | 1944-12-20 | 32 |
| 84th Infantry Division (US) | 1944-12-20 | 1945-04-11 | 112 |
| 8th Infantry Division (US) | 1944-09-14 | 1945-04-14 | 212 |
| 90th Infantry Division (US) | 1944-06-19 | 1944-07-25 | 36 |
| 90th Infantry Division (US) | 1944-09-22 | 1945-02-01 | 132 |
| 94th Infantry Division (US) | 1944-09-10 | 1945-02-22 | 165 |
| 99th Infantry Division (US) | 1945-02-04 | 1945-03-12 | 36 |
| 99th Infantry Division (US) | 1945-03-12 | 1945-04-15 | 34 |
| 9th Armored Division (US) | 1945-01-14 | 1945-03-07 | 52 |
| 9th Armored Division (US) | 1945-03-07 | 1945-04-16 | 40 |
| 9th Infantry Division (US) | 1944-06-29 | 1944-07-30 | 31 |
| 9th Infantry Division (US) | 1944-09-11 | 1945-02-01 | 143 |
| 9th Infantry Division (US) | 1945-02-01 | 1945-04-17 | 75 |
