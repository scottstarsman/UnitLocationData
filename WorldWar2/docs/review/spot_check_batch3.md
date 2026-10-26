# Spot-check sample, Batch 3 (18 rows, post-review state)

**Post-review state (25 October 2026).** The 15 rows of the first Batch 3 sample, in their corrected form, plus the three rows the review added (C0564, C0565, C0566); the review dropped the one Batch 3 conflict group (G016), so no row below is in a conflict group. The "Why picked" lines say what changed. Rows were chosen by risk from the Batch 3 claims (C0516 to C0566, 1 October to 31 December 1944): the command transitions of 20 December, attachments with explicit ends, rows whose coordinate comes from an atlas entry other than the row date or from another unit's headquarters, activations that rest on a CMH table date, and the largest implied moves. All values are as in `build/all_claims.csv` at commit time. Each row has `Event support:` and `Location support:` sentences in its notes. Page cites are Green Book pages on HyperWar (ibiblio); atlas entries are World War II by Day, which compiles the CMH command-post lists.

## 1. C0517 — 12th Army Group (1944-12-20)

_Why picked: command transition: the 20 December change that puts First and Ninth Armies under 21st Army Group while the 12th Army Group keeps Third Army. Post-review: the two outbound transitions are named; the army group's own relationship does not change._

- **nationality**: US
- **echelon**: army_group
- **parent_formation**: Supreme Headquarters Allied Expeditionary Force (SHAEF) (ALL-SHAEF-000H)
- **command_relationships**: [{"unit_id":"ALL-SHAEF-000H","name":"Supreme Headquarters Allied Expeditionary Force (SHAEF)","relationship":"operational_control","effective_from":"1944-09-01","date_basis":"narrative","note":"Breakout-32 p683; see C0489"}]
- **commander**: Lieutenant General Omar N. Bradley
- **latitude**: 49.6114
- **longitude**: 6.1300
- **location_name**: Luxembourg City, Luxembourg
- **location_represents**: headquarters
- **precision_km**: 5
- **confidence**: 0.7
- **campaign**: Ardennes-Alsace
- **operation_name**: 
- **sub_operation_name**: Ardennes
- **composing_units**: 
- **event_type**: command_change
- **current_activity**: First and Ninth Armies pass to 21st Army Group; Bradley keeps the south of the Bulge
- **engaged_with**: 
- **strength_status**: unknown
- **strength_json**: 
- **conflict_group_id**: 
- **claim_status**: preferred
- **location_date**: 1944-12-20
- **location_basis**: documented_on_date
- **location_temporal_offset_days**: 0
- **source**: https://www.ibiblio.org/hyperwar/USA/USA-E-Ardennes/USA-E-Ardennes-18.html#page423 | https://www.ibiblio.org/hyperwar/USA/USA-E-Ardennes/USA-E-Ardennes-18.html#page425 | https://www.ibiblio.org/hyperwar/USA/USA-E-Ardennes/USA-E-Ardennes-15.html#page330 ; coords: Wikipedia (en): Luxembourg City
- **notes**: Event date: 20 December 1944 (Ardennes p423: Eisenhower agreed on the evening of 19 December and the next morning ordered the division of command; p425: Bradley telephoned the First Army later that morning and Montgomery reached Hodges' command post an hour or so after noon). The hour of effect is not documented. Event definition: the Allied army group boundary is redrawn from Givet to St. Vith and the U.S. First and Ninth Armies come under Montgomery's 21st Army Group; the 12th Army Group keeps the forces south of the salient (in effect Third Army). Relationship: SHAEF operational control (direct channel since 1 September, C0489); the army group was not organic to SHAEF. Two outbound transitions follow from the one order, each recorded on its own row with its own dates: First Army to 21st Army Group operational control (C0520) and Ninth Army to 21st Army Group operational control (C0522); in the CMH tables both armies keep the 12th Army Group in the assigned column. The 12th Army Group's own relationship to SHAEF does not change on 20 December; this row records the army group's side of the change. Location: Bradley's headquarters was at Luxembourg City during these days (Ardennes p330, p423); city centroid, the building is not stated. Coordinates: Wikipedia (en): Luxembourg City. Event support: high (Green Book narrative; the same order is in the CMH tables as the 12th and British 21st columns). Location support: high for the city, moderate for the site (a narrative statement, not a command-post list).

## 2. C0520 — First Army (1944-12-20)

_Why picked: command transition with an explicit end: 21st Army Group operational_control with effective_to 1945-01-17 (inclusive last day) taken from the CMH tables (outside the window), 12th Army Group "assigned" retained._

- **nationality**: US
- **echelon**: army
- **parent_formation**: 21st Army Group (UK-AG-021G)
- **command_relationships**: [{"unit_id":"US-AG-012G","name":"12th Army Group","relationship":"assigned","effective_from":"1944-08-01","date_basis":"narrative","note":"Breakout-18 p343: 12th Army Group became operational at noon on 1 August with First and Third Armies"},{"unit_id":"UK-AG-021G","name":"21st Army Group","relationship":"operational_control","effective_from":"1944-12-20","ordered_date":"1944-12-20","effective_to":"1945-01-17","effective_to_basis":"assignment_table","date_basis":"narrative","note":"Ardennes p423-425: Eisenhower placed First and Ninth Armies under Montgomery's 21st Army Group; the CMH assignment tables drop the 21st Army Group column for First Army units on 18 January 1945"}]
- **commander**: Lieutenant General Courtney H. Hodges
- **latitude**: 50.5833
- **longitude**: 5.6333
- **location_name**: Chaudfontaine, Liège
- **location_represents**: headquarters
- **precision_km**: 3
- **confidence**: 0.7
- **campaign**: Ardennes-Alsace
- **operation_name**: 
- **sub_operation_name**: Ardennes
- **composing_units**: 
- **event_type**: command_change
- **current_activity**: passes to 21st Army Group under Montgomery
- **engaged_with**: 
- **strength_status**: unknown
- **strength_json**: 
- **conflict_group_id**: 
- **claim_status**: preferred
- **location_date**: 1944-12-20
- **location_basis**: documented_on_date
- **location_temporal_offset_days**: 0
- **source**: https://www.ibiblio.org/hyperwar/USA/USA-E-Ardennes/USA-E-Ardennes-18.html#page425 | https://www.ibiblio.org/hyperwar/USA/USA-E-Ardennes/USA-E-Ardennes-18.html#page423 | https://www.ibiblio.org/hyperwar/USA/USA-E-Ardennes/USA-E-Ardennes-18.html#page426 ; coords: Wikipedia (en): Chaudfontaine
- **notes**: Event date: 20 December 1944 (Ardennes p425: Bradley telephoned this word to First Army later in the morning; Montgomery reached Hodges' command post an hour or so after noon). The hour of effect is not documented. Event definition: First Army (with Ninth Army) is placed under Montgomery's 21st Army Group; the 12th Army Group keeps Third Army. The CMH tables show the 12th Army Group column unchanged and the British 21st Army Group in the attached column. Relationship: British 21st Army Group operational_control from 20 December (Eisenhower's order placing First and Ninth Armies under Montgomery's command); 12th Army Group assigned stays listed because the CMH tables keep it in the assigned column. The control ends on 17 January 1945 (effective_to is the inclusive last day; the tables' first row without the 21st Army Group column is 18 January); that end date is outside this batch window and is taken from the tables. Location: Chaudfontaine, the headquarters since the 19th (Ardennes p423, p426 for 20 December). Coordinates: Wikipedia (en): Chaudfontaine. Event support: high (Green Book narrative and CMH tables agree). Location support: high for the commune, moderate for the site.

## 3. C0522 — Ninth Army (1944-12-20)

_Why picked: weakest location of the command-change rows: last-known Maastricht, 56 days before (0.3 / 10 km); the 3 April 1945 end is separately sourced from the tables._

- **nationality**: US
- **echelon**: army
- **parent_formation**: 21st Army Group (UK-AG-021G)
- **command_relationships**: [{"unit_id":"US-AG-012G","name":"12th Army Group","relationship":"assigned","effective_from":"1944-09-05","date_basis":"narrative","note":"Breakout-30 p636; CMH ETO-OB tables"},{"unit_id":"UK-AG-021G","name":"21st Army Group","relationship":"operational_control","effective_from":"1944-12-20","ordered_date":"1944-12-20","effective_to":"1945-04-03","effective_to_basis":"assignment_table","date_basis":"narrative","note":"Ardennes p423-425; CMH assignment tables show the British 21st Army Group attached to Ninth Army units from 20 December 1944 until 4 April 1945"}]
- **commander**: Lieutenant General William H. Simpson
- **latitude**: 50.8500
- **longitude**: 5.6833
- **location_name**: Maastricht, Limburg
- **location_represents**: headquarters
- **precision_km**: 10
- **confidence**: 0.3
- **campaign**: Rhineland
- **operation_name**: 
- **sub_operation_name**: Roer
- **composing_units**: 
- **event_type**: command_change
- **current_activity**: passes to 21st Army Group under Montgomery
- **engaged_with**: 
- **strength_status**: unknown
- **strength_json**: 
- **conflict_group_id**: 
- **claim_status**: preferred
- **location_date**: 1944-10-25
- **location_basis**: nearest_earlier_command_post
- **location_temporal_offset_days**: -56
- **source**: https://www.ibiblio.org/hyperwar/USA/USA-E-Ardennes/USA-E-Ardennes-18.html#page423 | https://www.ibiblio.org/hyperwar/USA/USA-E-Ardennes/USA-E-Ardennes-18.html#page425 | https://www.ww2byday.com/92/mapunit/ ; coords: Wikipedia (en): Maastricht
- **notes**: Event date: 20 December 1944 (Ardennes p423, p425: Eisenhower's order placing First and Ninth Armies under Montgomery's command; the CMH tables for Ninth Army divisions show the British 21st Army Group attached from 20 December). The hour is not documented. Event definition: Ninth Army (with First Army) is placed under 21st Army Group; the 12th Army Group keeps Third Army. Ninth Army is also stripped of the 84th Division (leaving on 20 December) and, by the 21st, the 2nd Armored Division (Ardennes p426). Relationship: British 21st Army Group operational_control from 20 December; 12th Army Group assigned stays listed (CMH tables keep it in the assigned column). The end date, 3 April 1945 (inclusive last day), is separately sourced from the CMH tables (the 4 April 1945 row restores the 12th Army Group) and lies outside this batch window; the confidence of this December row does not apply to it. Location: Maastricht is the last-known headquarters place, not a documented position on 20 December: the atlas lists Maastricht from 25 October and nothing later until Rheydt on 11 March 1945, and the Green Book pages read do not locate the Ninth Army headquarters on 20 December; no source used moves it, so the point is the nearest earlier listed place, 56 days earlier. Coordinates: Wikipedia (en): Maastricht. Event support: high (Green Book narrative and CMH tables). Location support: low (a 56-day gap to the nearest list entry, no narrative for the day).

## 4. C0546 — VIII Corps (1944-12-20)

_Why picked: command transition: VIII Corps passes from First to Third Army "during the 20th"; post-review a sequence with the First Army entry's earliest end (19 December) and the boundary day covered by both._

- **nationality**: US
- **echelon**: corps
- **parent_formation**: Third Army (US-ARMY-003A)
- **command_relationships**: [{"unit_id":"US-ARMY-001A","name":"First Army","relationship":"assigned","effective_from":"1944-10-22","effective_to":"1944-12-20","effective_to_basis":"narrative","date_basis":"narrative","note":"Siegfried p378 for the start; Ardennes p399 for the end: VIII Corps passed to Third Army during the 20th. Sequence: First Army until the passage, Third Army after it; 20 December is the boundary day and both entries cover it (effective_to is inclusive); the hour is not documented, so 19 December is the last day certainly under First Army","effective_to_earliest":"1944-12-19"},{"unit_id":"US-ARMY-003A","name":"Third Army","relationship":"assigned","effective_from":"1944-12-20","date_basis":"narrative","note":"Ardennes p399: VIII Corps passed to General Patton's Third Army during the 20th; the hour is not documented; first day certainly under Third Army: 21 December","effective_from_latest":"1944-12-20"}]
- **commander**: Major General Troy H. Middleton
- **latitude**: 49.8408
- **longitude**: 5.4351
- **location_name**: Neufchâteau, Luxembourg
- **location_represents**: headquarters
- **precision_km**: 5
- **confidence**: 0.7
- **campaign**: Ardennes-Alsace
- **operation_name**: 
- **sub_operation_name**: Ardennes
- **composing_units**: 
- **event_type**: command_change
- **current_activity**: passes from First Army to Third Army
- **engaged_with**: 
- **strength_status**: unknown
- **strength_json**: 
- **conflict_group_id**: 
- **claim_status**: preferred
- **location_date**: 1944-12-20
- **location_basis**: documented_on_date
- **location_temporal_offset_days**: 0
- **source**: https://www.ibiblio.org/hyperwar/USA/USA-E-Ardennes/USA-E-Ardennes-17.html#page399 | https://www.ww2byday.com/75/mapunit/ | https://www.ibiblio.org/hyperwar/USA/USA-E-Ardennes/USA-E-Ardennes-14.html#page321 ; coords: OpenStreetMap Nominatim: Neufchâteau, Luxembourg, Wallonie, 6840, België / Belgique / Belgien
- **notes**: Event date: 20 December 1944 (Ardennes p399: "The VIII Corps passed to General Patton's Third Army during the 20th", word of which was brought to the 101st trains by Colonel Ryan from the VIII Corps headquarters in Neufchâteau). The hour is not documented. Event definition: the corps and the units attached to it, including the 101st Airborne at Bastogne, pass from Hodges' First Army to Patton's Third Army; the same day Eisenhower's order puts First and Ninth Armies under 21st Army Group. Relationship (sequence): First Army assigned until the passage; Third Army assigned from the passage; both are listed on 20 December, the boundary day, because the hour is not documented (effective_to is inclusive, so the First Army entry ends on 20 December; its earliest possible end is 19 December). The row's parent is Third Army, the headquarters the event passes the corps to; the corps' controller at a given hour of 20 December is unknown. Location: Atlas and Green Book agree on Neufchâteau on 20 December (p399, p321: the corps re-forming around Neufchâteau and Arlon on 21 December). Coordinates: OpenStreetMap Nominatim: Neufchâteau, Luxembourg, Wallonie, 6840, België / Belgique / Belgien. Event support: high (Green Book narrative; hour not documented). Location support: high for the place (atlas and narrative on the date).

## 5. C0554 — 101st Airborne Division (1944-12-20)

_Why picked: post-review (G016 dissolved): the 101st's parent is VIII Corps; Third Army attached from 20 December through the corps, hour undocumented (who_controls answers UNKNOWN at army level at noon)._

- **nationality**: US
- **echelon**: division
- **parent_formation**: VIII Corps (US-COR-008C)
- **command_relationships**: [{"unit_id":"US-COR-008C","name":"VIII Corps","relationship":"operational_control","effective_from":"1944-12-18","date_basis":"narrative","note":"Ardennes p306: after Bradley allowed the diversion of the 101st to Bastogne, Hodges turned the division over to Middleton on 18 December (McAuliffe reached Bastogne about 1600); the hour of the turnover is not documented; the CMH table dates VIII Corps from 17 December (C0563)"},{"unit_id":"ALL-FAAA-001A","name":"First Allied Airborne Army","relationship":"assigned","effective_from":"1944-12-17","date_basis":"assignment_table","note":"CMH ETO-OB assignment table, Army Assigned column: \"First Allied Abn\""},{"unit_id":"US-ARMY-003A","name":"Third Army","relationship":"attached","effective_from":"1944-12-20","effective_to":"1945-01-19","effective_to_basis":"assignment_table","date_basis":"narrative","note":"Ardennes p399: VIII Corps passed to Third Army during the 20th, hour not documented; the CMH table dates the Third Army attachment from 1944-12-17, three days before the Green Book; the narrative date is used and the table date is not encoded (see C0563 and C0554 notes); Third Army's authority over the division is exercised through VIII Corps"},{"unit_id":"US-AG-012G","name":"12th Army Group","relationship":"attached","effective_from":"1944-12-20","effective_to":"1945-01-19","effective_to_basis":"assignment_table","date_basis":"inferred","note":"follows the corps to Third Army, a 12th Army Group army; the CMH table shows 12th Army Group attached from 1944-12-17 (table date not encoded, see C0563)"}]
- **commander**: Brigadier General Anthony C. McAuliffe
- **latitude**: 50.0042
- **longitude**: 5.7200
- **location_name**: Bastogne, Luxembourg
- **location_represents**: headquarters
- **precision_km**: 3
- **confidence**: 0.7
- **campaign**: Ardennes-Alsace
- **operation_name**: 
- **sub_operation_name**: Bastogne
- **composing_units**: 
- **event_type**: command_change
- **current_activity**: VIII Corps and the 101st at Bastogne pass from First Army to Third Army during the day
- **engaged_with**: 
- **strength_status**: unknown
- **strength_json**: 
- **conflict_group_id**: 
- **claim_status**: preferred
- **location_date**: 1944-12-20
- **location_basis**: documented_on_date
- **location_temporal_offset_days**: 0
- **source**: https://www.ibiblio.org/hyperwar/USA/USA-E-Ardennes/USA-E-Ardennes-17.html#page399 | https://www.ibiblio.org/hyperwar/USA/USA-E-Ardennes/USA-E-Ardennes-19.html#page456 | https://www.ww2byday.com/2/mapunit/ | https://web.archive.org/web/2018/http://www.history.army.mil/documents/ETO-OB/101ABN-ETO.htm ; coords: Wikipedia (en): Bastogne
- **notes**: Event date: 20 December 1944 (Ardennes p399: "The VIII Corps passed to General Patton's Third Army during the 20th", with some confusion among the units attached to the corps about their exact status; p456: planning at Bastogne that day). The hour is not documented. Event definition: the corps, and with it the 101st Airborne at Bastogne, passes from Hodges' First Army to Patton's Third Army at an undocumented hour of 20 December. The 101st's immediate parent is VIII Corps throughout (operational_control from 18 December, C0553); Third Army's authority over the division is inherited through the corps from the passage, not asserted separately for any earlier day. The question 'who controlled the division at noon on 20 December' is therefore unknown at army level (First Army before the passage, Third Army after it) and scripts/who_controls.py reports it as such. An earlier version of this row was the preferred half of conflict group G016; with the CMH table row reclassified as a table observation (C0563) the group is dissolved. Relationship: VIII Corps operational_control from 18 December; First Allied Airborne Army assigned (table); Third Army attached from 20 December (Green Book), against 17 December in the CMH table, a documented disagreement in which the narrative date is used; 12th Army Group attached through Third Army. Location: Bastogne, the division command post (atlas 19 December; Ardennes p456 for 20 December planning at Bastogne). Coordinates: Wikipedia (en): Bastogne. Event support: moderate (the day is documented; the hour is not, and the table date disagrees). Location support: high (command post at Bastogne for the day).

## 6. C0563 — 101st Airborne Division (1944-12-17)

_Why picked: post-review: a CMH table observation (subordinate_assignment), no longer an alternate; XVIII Airborne Corps is the operational parent and Third Army is not asserted._

- **nationality**: US
- **echelon**: division
- **parent_formation**: XVIII Airborne Corps (US-ABN-018C)
- **command_relationships**: [{"unit_id":"US-ABN-018C","name":"XVIII Airborne Corps","relationship":"unspecified_subordination","effective_to":"1944-12-18","effective_to_earliest":"1944-12-16","effective_to_basis":"narrative","date_basis":"narrative","note":"Ardennes p304: the division belonged to General Ridgway's XVIII Airborne Corps in SHAEF reserve at Reims; the 17 December orders reached the corps chief of staff, who relayed the alert to the 82d and 101st; the entry ends with the turnover to VIII Corps on 18 December (p306); the CMH table lists VIII Corps instead from 17 December, so the end lies between 16 and 18 December; the start of this stretch is not dated in the sources used"},{"unit_id":"US-COR-008C","name":"VIII Corps","relationship":"unspecified_subordination","effective_from":"1944-12-17","effective_from_latest":"1944-12-18","date_basis":"assignment_table","note":"CMH ETO-OB assignment table (single corps column; the table does not say assigned or attached for corps); the Green Book has the turnover to VIII Corps on 18 December (p306), so the start lies between 17 and 18 December; operational control is on the 19 December row"},{"unit_id":"ALL-FAAA-001A","name":"First Allied Airborne Army","relationship":"assigned","effective_from":"1944-12-17","date_basis":"assignment_table","note":"CMH ETO-OB assignment table, Army Assigned column: \"First Allied Abn\""}]
- **commander**: Brigadier General Anthony C. McAuliffe
- **latitude**: 49.1401
- **longitude**: 4.3658
- **location_name**: Mourmelon-le-Grand, Marne
- **location_represents**: headquarters
- **precision_km**: 5
- **confidence**: 0.3
- **campaign**: Ardennes-Alsace
- **operation_name**: 
- **sub_operation_name**: Ardennes
- **composing_units**: 
- **event_type**: subordinate_assignment
- **current_activity**: CMH table lists the division under VIII Corps from 17 December while it is still at Camp Mourmelon
- **engaged_with**: 
- **strength_status**: unknown
- **strength_json**: 
- **conflict_group_id**: 
- **claim_status**: preferred
- **location_date**: 1944-12-01
- **location_basis**: nearest_earlier_command_post
- **location_temporal_offset_days**: -16
- **source**: https://web.archive.org/web/2018/http://www.history.army.mil/documents/ETO-OB/101ABN-ETO.htm | https://www.ww2byday.com/2/mapunit/ | https://www.ibiblio.org/hyperwar/USA/USA-E-Ardennes/USA-E-Ardennes-13.html#page304 | https://www.ibiblio.org/hyperwar/USA/USA-E-Ardennes/USA-E-Ardennes-13.html#page306 ; coords: Wikipedia (en): Mourmelon-le-Grand
- **notes**: Event date: 17 December 1944 (the CMH ETO order-of-battle table for the 101st Airborne Division lists VIII Corps in its corps column from 17 December). Event definition: a table observation, not an operational transfer. The table date is an assignment date; the Green Book has the division in SHAEF reserve under the XVIII Airborne Corps, the alert reaching the corps chief of staff in the early evening of 17 December (Ardennes p304), the division leaving Camp Mourmelon that night, and Hodges turning it over to Middleton's VIII Corps on 18 December (p306). The operational passage to VIII Corps is on the 19 December row (C0553) and the passage of VIII Corps to Third Army on the 20 December row (C0554). An earlier version of this row was an alternate in conflict group G016 against C0554; the two rows record different things on different dates (a table classification and an operational event), so the group is dissolved and the rows are a sequence. Relationship: XVIII Airborne Corps is the operational parent on 17 December; VIII Corps unspecified_subordination from 17 December (CMH table, start between 17 and 18 December); First Allied Airborne Army assigned (table). The CMH table also lists Third Army and 12th Army Group as attached from 17 December; that is not encoded here, because the Green Book dates the corps' passage to Third Army on 20 December and a table classification three days earlier is not control by Third Army. The Third Army entry begins on C0554. Location: Camp Mourmelon (Mourmelon-le-Grand): the atlas lists the division there on 1 December and the Green Book has it moving out on the night of 18 December; no source places it elsewhere on 17 December. Coordinates: Wikipedia (en): Mourmelon-le-Grand. Event support: low (a table date, contradicted as an operational date by narrative pages). Location support: low (an inference from the departure; the atlas entry is 16 days earlier).

## 7. C0552 — XVIII Airborne Corps (1944-12-19)

_Why picked: activation with the location taken from another unit's command post (the 82nd at Habiémont); post-review the basis is `inferred` and the note says the corps post is not named._

- **nationality**: US
- **echelon**: corps
- **parent_formation**: First Army (US-ARMY-001A)
- **command_relationships**: [{"unit_id":"ALL-FAAA-001A","name":"First Allied Airborne Army","relationship":"assigned","effective_from":"1944-08-25","date_basis":"narrative","note":"see C0213"},{"unit_id":"US-ARMY-001A","name":"First Army","relationship":"operational_control","effective_from":"1944-12-19","ordered_date":"1944-12-19","date_basis":"narrative","note":"Ardennes p343: First Army directive making the corps operational"}]
- **commander**: Major General Matthew B. Ridgway
- **latitude**: 50.3710
- **longitude**: 5.7170
- **location_name**: Habiémont, Lierneux
- **location_represents**: headquarters
- **precision_km**: 5
- **confidence**: 0.5
- **campaign**: Ardennes-Alsace
- **operation_name**: 
- **sub_operation_name**: Ardennes
- **composing_units**: 
- **event_type**: activation
- **current_activity**: Ridgway opens the corps command post near the 82nd Airborne and the corps becomes operational under First Army
- **engaged_with**: 
- **strength_status**: unknown
- **strength_json**: 
- **conflict_group_id**: 
- **claim_status**: preferred
- **location_date**: 1944-12-19
- **location_basis**: inferred
- **location_temporal_offset_days**: 0
- **source**: https://www.ibiblio.org/hyperwar/USA/USA-E-Ardennes/USA-E-Ardennes-15.html#page343 | https://www.ibiblio.org/hyperwar/USA/USA-E-Ardennes/USA-E-Ardennes-15.html#page342 | https://www.ww2byday.com/48/mapunit/ | https://www.ww2byday.com/83/mapunit/ ; coords: Wikipedia (fr): Habiémont
- **notes**: Event date: 19 December 1944 (Ardennes p343: "the following morning" after the 82nd's night move of 18 December, Ridgway, who had resumed command of the airborne corps, opened his corps command post near that of the 82d; the First Army, then at Chaudfontaine, gave him the directive making the corps operational later that morning). Event definition: the XVIII Airborne Corps headquarters, in England until now, takes command of the 82nd Airborne and, soon after, the 7th Armored, 3rd Armored and 30th Divisions on First Army's left; the row dates the first operational day, not the corps arrival in France. Relationship: First Army operational_control from 19 December (directive making the corps operational); the corps stays assigned to the First Allied Airborne Army (CMH tables). Location: The Green Book puts the corps command post near the 82nd's; the atlas lists the 82nd command post at Habiémont on 19 December and the corps at Manhay on 20 December. Habiémont is the documented place of the 82nd's command post, used as an inference for the corps command post; no source names the corps command post for 19 December (the first atlas entry for the corps is Manhay on 20 December). Coordinates: Wikipedia (fr): Habiémont. Event support: high (Green Book narrative). Location support: moderate (the place is inferred from the neighbouring command post, not named for the corps).

## 8. C0544 — 84th Infantry Division (1944-11-18)

_Why picked: Operation Clipper: British XXX Corps and Second Army operational_control 11-22 November from the CMH table; post-review XIII Corps "still tied for other purposes" is `unknown`, not administrative_control, and the 18 November date is confirmed (D Day, p547)._

- **nationality**: US
- **echelon**: division
- **parent_formation**: XXX Corps (UK-COR-030C)
- **command_relationships**: [{"unit_id":"UK-COR-030C","name":"XXX Corps","relationship":"operational_control","effective_from":"1944-11-11","date_basis":"assignment_table","note":"CMH ETO-OB assignment table, corps column: \"30th Br (Opns)\"; the table row of 1944-11-23 no longer lists it, so the attachment is closed on 1944-11-22","effective_to":"1944-11-22","effective_to_basis":"assignment_table"},{"unit_id":"US-ARMY-009A","name":"Ninth Army","relationship":"assigned","effective_from":"1944-11-11","date_basis":"assignment_table","note":"CMH ETO-OB assignment table, Army Assigned column: \"Ninth\""},{"unit_id":"UK-ARMY-002A","name":"Second Army","relationship":"operational_control","effective_from":"1944-11-11","date_basis":"assignment_table","note":"CMH ETO-OB assignment table, Army Attached column: \"Second Br (Opns)\"; the table row of 1944-11-23 no longer lists it, so the attachment is closed on 1944-11-22","effective_to":"1944-11-22","effective_to_basis":"assignment_table"},{"unit_id":"US-AG-012G","name":"12th Army Group","relationship":"assigned","effective_from":"1944-11-11","date_basis":"assignment_table","note":"CMH ETO-OB assignment table, Army Group Assigned column: \"12th\""},{"unit_id":"UK-AG-021G","name":"21st Army Group","relationship":"attached","effective_from":"1944-11-11","date_basis":"assignment_table","note":"CMH ETO-OB assignment table, Army Group Attached column: \"Br 21st\"; the table row of 1944-11-23 no longer lists it, so the attachment is closed on 1944-11-22","effective_to":"1944-11-22","effective_to_basis":"assignment_table"},{"unit_id":"US-COR-013C","name":"XIII Corps","relationship":"unknown","effective_from":"1944-11-11","effective_to":"1944-11-22","effective_to_basis":"assignment_table","date_basis":"narrative","note":"Siegfried p545: the division was \"attached for operations to the British but still tied for other purposes to the XIII Corps\"; the source does not say what the other purposes were, so the relationship is not typed as administrative control; the dates are those of the CMH table's British operational-control entries"}]
- **commander**: Brigadier General Alexander R. Bolling
- **latitude**: 50.9000
- **longitude**: 6.0500
- **location_name**: Eygelshoven, Limburg
- **location_represents**: headquarters
- **precision_km**: 5
- **confidence**: 0.5
- **campaign**: Rhineland
- **operation_name**: 
- **sub_operation_name**: Roer; Clipper
- **composing_units**: 
- **event_type**: attack
- **current_activity**: attacks toward Geilenkirchen in Operation Clipper under British operational control
- **engaged_with**: 
- **strength_status**: unknown
- **strength_json**: 
- **conflict_group_id**: 
- **claim_status**: preferred
- **location_date**: 1944-11-16
- **location_basis**: nearest_earlier_command_post
- **location_temporal_offset_days**: -2
- **source**: https://www.ibiblio.org/hyperwar/USA/USA-E-Siegfried/USA-E-Siegfried-23.html#page545 | https://www.ibiblio.org/hyperwar/USA/USA-E-Siegfried/USA-E-Siegfried-24.html#page565 | https://www.ww2byday.com/50/mapunit/ | https://web.archive.org/web/2018/http://www.history.army.mil/documents/ETO-OB/84ID-ETO.htm | https://www.ibiblio.org/hyperwar/USA/USA-E-Siegfried/USA-E-Siegfried-23.html#page549 ; coords: Wikipedia (en): Eygelshoven
- **notes**: Event date: 18 November 1944 (Siegfried p545 and p546: the attack was scheduled originally for D plus 1 and postponed one day, to 18 November; p547 calls 18 November "D Day for Operation Clipper"; p549: the flail tanks of Drewforce moved at 0600 and two battalions of the 334th Infantry began moving through the gaps in the mine field an hour later). Event definition: the 84th Division, newly arrived, attacks toward Geilenkirchen alongside the British 43rd Division; the row dates the jump-off, which the Green Book documents with times. An outside review suggested the Clipper opening date was 19 November; the pages above give 18 November and the 19 November date was not found. Relationship: British XXX Corps and British Second Army operational_control from 11 to 22 November (CMH table); XIII Corps 'still tied for other purposes' (p545) with the relationship not stated (unknown); Ninth Army and 12th Army Group assigned. Location: Division command post at Eygelshoven on 16 November (atlas), two days earlier. Coordinates: Wikipedia (en): Eygelshoven. Event support: high (jump-off date and hour documented on p549, D Day on p547). Location support: moderate (two days before).

## 9. C0560 — 84th Infantry Division (1944-12-20)

_Why picked: post-review sequence: XVIII Airborne Corps attached 20 to 22-23 December, VII Corps from the table date 20 December (administrative) and officially from 1630 on 23 December; place is the nearest later command post._

- **nationality**: US
- **echelon**: division
- **parent_formation**: XVIII Airborne Corps (US-ABN-018C)
- **command_relationships**: [{"unit_id":"US-ABN-018C","name":"XVIII Airborne Corps","relationship":"attached","effective_from":"1944-12-20","effective_to":"1944-12-23","effective_to_earliest":"1944-12-22","effective_to_basis":"narrative","date_basis":"narrative","note":"Ardennes p426: \"Temporarily attached to the XVIII Airborne Corps\"; the corps was still giving the division orders at noon on 21 December (p430) and on 22 December (p431: Ridgway extended the division's mission); the VII Corps officially assumed its corps front at 1630 on 23 December (p433), which is the latest end; the division's own handover is not separately dated"},{"unit_id":"US-ARMY-009A","name":"Ninth Army","relationship":"assigned","effective_from":"1944-12-20","date_basis":"assignment_table","note":"CMH ETO-OB assignment table, Army Assigned column: \"Ninth\""},{"unit_id":"US-ARMY-001A","name":"First Army","relationship":"attached","effective_from":"1944-12-20","date_basis":"assignment_table","note":"CMH ETO-OB assignment table, Army Attached column: \"First\"","effective_to":"1945-02-02","effective_to_basis":"assignment_table"},{"unit_id":"US-AG-012G","name":"12th Army Group","relationship":"assigned","effective_from":"1944-12-20","date_basis":"assignment_table","note":"CMH ETO-OB assignment table, Army Group Assigned column: \"12th\""},{"unit_id":"UK-AG-021G","name":"21st Army Group","relationship":"attached","effective_from":"1944-12-20","date_basis":"assignment_table","note":"CMH ETO-OB assignment table, Army Group Attached column: \"Br 21st\"","effective_to":"1945-01-17","effective_to_basis":"assignment_table"},{"unit_id":"US-COR-007C","name":"VII Corps","relationship":"unspecified_subordination","effective_from":"1944-12-20","date_basis":"assignment_table","note":"CMH ETO-OB assignment table (single corps column; the table does not say assigned or attached for corps) lists VII Corps from 20 December, the same day as the XVIII Airborne Corps row; the Green Book has the VII Corps assembling around the division from 21 December and officially assuming its corps front at 1630 on 23 December (Ardennes p426, p433), so operational control passed between 22 and 23 December and the table date is administrative","effective_from_latest":"1944-12-23"}]
- **commander**: Brigadier General Alexander R. Bolling
- **latitude**: 50.2167
- **longitude**: 5.3333
- **location_name**: Marche-en-Famenne, Luxembourg
- **location_represents**: headquarters
- **precision_km**: 5
- **confidence**: 0.5
- **campaign**: Ardennes-Alsace
- **operation_name**: 
- **sub_operation_name**: Ardennes
- **composing_units**: 
- **event_type**: command_change
- **current_activity**: leaves Ninth Army's Roer front for First Army; temporarily attached to XVIII Airborne Corps
- **engaged_with**: 
- **strength_status**: unknown
- **strength_json**: 
- **conflict_group_id**: 
- **claim_status**: preferred
- **location_date**: 1944-12-21
- **location_basis**: nearest_later_command_post
- **location_temporal_offset_days**: 1
- **source**: https://www.ibiblio.org/hyperwar/USA/USA-E-Ardennes/USA-E-Ardennes-18.html#page426 | https://www.ibiblio.org/hyperwar/USA/USA-E-Ardennes/USA-E-Ardennes-18.html#page429 | https://web.archive.org/web/2018/http://www.history.army.mil/documents/ETO-OB/84ID-ETO.htm | https://www.ww2byday.com/50/mapunit/ ; coords: Wikipedia (en): Marche-en-Famenne | https://www.ibiblio.org/hyperwar/USA/USA-E-Ardennes/USA-E-Ardennes-18.html#page431 | https://www.ibiblio.org/hyperwar/USA/USA-E-Ardennes/USA-E-Ardennes-18.html#page433
- **notes**: Event date: 20 December 1944 (Ardennes p426: Bolling received orders on the night of the 19th to make ready for relief by the 102nd Division, and at noon on 20 December his leading regimental combat team, the 334th, was on the road to Belgium; "Temporarily attached to the XVIII Airborne Corps"; p427: two hours before midnight on 20 December the leading troops entered Marche; the CMH table lists XVIII Airborne Corps and then VII Corps on 20 December). Event definition: Bradley orders the 84th to leave the Ninth Army and come in on Ridgway's flank; the division moves 75 miles from the Geilenkirchen sector to Marche and is the nucleus of the new VII Corps front that Collins assembles from the early morning of the 21st (p426). Relationship (sequence): XVIII Airborne Corps attached from 20 December (narrative) until the VII Corps takes over, between 22 December (last documented XVIII Airborne Corps order, noon, p431) and 23 December (VII Corps officially assumes its front at 1630, p433); VII Corps unspecified_subordination from the CMH table date of 20 December, which is an administrative date, not the date operational control passed; First Army attached; Ninth Army and 12th Army Group assigned; British 21st Army Group attached (CMH table). The immediate parent on the row date is therefore the XVIII Airborne Corps, with First Army above it. Location: Marche is a nearest-later place (inferred): the leading troops entered the town at about 2200 on 20 December (p427), but the division command post is documented there only on 21 December (atlas; p428: the commander set up his command post in Marche on the late afternoon of 21 December, although p429 has word of the Hotton attack reaching the command post in Marche at 0900 that day, an inconsistency in the Green Book), so the headquarters position on the 20th itself is not documented. Coordinates: Wikipedia (en): Marche-en-Famenne. Event support: high (Green Book narrative with times). Location support: moderate (a one-day-later command post; the headquarters place on the date is inferred).

## 10. C0565 — VII Corps (1944-12-23)

_Why picked: new (C0565): the VII Corps front officially assumed at 1630 on 23 December, which dates the end of the XVIII Airborne Corps' control of the 84th Division._

- **nationality**: US
- **echelon**: corps
- **parent_formation**: First Army (US-ARMY-001A)
- **command_relationships**: [{"unit_id":"US-ARMY-001A","name":"First Army","relationship":"assigned","effective_from":"1944-08-01","date_basis":"narrative","note":"12th Army Group became operational 1 August with First and Third Armies; Breakout-18 p343"}]
- **commander**: Major General J. Lawton Collins
- **latitude**: 50.3517
- **longitude**: 5.4569
- **location_name**: Durbuy, Namur
- **location_represents**: headquarters
- **precision_km**: 5
- **confidence**: 0.5
- **campaign**: Ardennes-Alsace
- **operation_name**: 
- **sub_operation_name**: Ardennes
- **composing_units**: 84th Infantry Division; 2nd Armored Division; 75th Infantry Division
- **event_type**: command_change
- **current_activity**: officially assumes its Ardennes front at 1630 with the 84th Division in the centre
- **engaged_with**: 
- **strength_status**: unknown
- **strength_json**: 
- **conflict_group_id**: 
- **claim_status**: preferred
- **location_date**: 1944-12-23
- **location_basis**: documented_on_date
- **location_temporal_offset_days**: 0
- **source**: https://www.ibiblio.org/hyperwar/USA/USA-E-Ardennes/USA-E-Ardennes-18.html#page433 | https://www.ibiblio.org/hyperwar/USA/USA-E-Ardennes/USA-E-Ardennes-18.html#page432 | https://www.ww2byday.com/74/mapunit/ ; coords: Wikipedia (en): Durbuy
- **notes**: Event date: 23 December 1944 (Ardennes p433: "The new corps front (officially assumed by the VII Corps at 1630 on 23 December) would reach from the Ourthe River on the left to the junction of the Lesse and Meuse on the right, approximately fifty miles"; p432: on the 22nd Collins and some corps troops moved into the new area southwest of Liège). Event definition: the VII Corps takes over its Ardennes front, with the 84th Infantry Division already holding the centre, the 2nd Armored Division closing to the rear and the 75th Infantry Division in reserve; the 3rd Armored Division is still the right wing of the XVIII Airborne Corps (p432). The row exists to date the end of the XVIII Airborne Corps' control of the 84th Division (C0560): the CMH table lists VII Corps for the 84th from 20 December, but the Green Book has the XVIII Airborne Corps still giving the division orders on 21 and 22 December. Relationship: First Army assigned (C0530); the corps is under 21st Army Group's operational control through First Army from 20 December (C0520). Location: the atlas lists the corps command post at Durbuy on 23 December. Coordinates: Wikipedia (en): Durbuy. Event support: high (an hour is given by the Green Book). Location support: moderate (an atlas entry for the date; the Green Book does not name the place).

## 11. C0532 — XIII Corps (1944-11-08)

_Why picked: activation = first operational sector (wording clarified after review); the nearest earlier atlas entry is 13 days away (0.3 / 10 km)._

- **nationality**: US
- **echelon**: corps
- **parent_formation**: Ninth Army (US-ARMY-009A)
- **command_relationships**: [{"unit_id":"US-ARMY-009A","name":"Ninth Army","relationship":"assigned","effective_from":"1944-11-04","date_basis":"narrative","note":"Siegfried p399 and p401: Ninth Army plans and the 4 November directive to its two corps"}]
- **commander**: Major General Alvan C. Gillem Jr.
- **latitude**: 50.7833
- **longitude**: 5.4667
- **location_name**: Tongeren, Limburg
- **location_represents**: headquarters
- **precision_km**: 10
- **confidence**: 0.3
- **campaign**: Rhineland
- **operation_name**: 
- **sub_operation_name**: Roer
- **composing_units**: 
- **event_type**: activation
- **current_activity**: takes over the 17-mile Ninth Army front west of Geilenkirchen as its first operational sector
- **engaged_with**: 
- **strength_status**: unknown
- **strength_json**: 
- **conflict_group_id**: 
- **claim_status**: preferred
- **location_date**: 1944-10-26
- **location_basis**: nearest_earlier_command_post
- **location_temporal_offset_days**: -13
- **source**: https://www.ibiblio.org/hyperwar/USA/USA-E-Siegfried/USA-E-Siegfried-17.html#page401 | https://www.ibiblio.org/hyperwar/USA/USA-E-Siegfried/USA-E-Siegfried-17.html#page399 | https://www.ww2byday.com/78/mapunit/ ; coords: Wikipedia (en): Tongeren
- **notes**: Event date: 8 November 1944 (Siegfried p401: "Controlling the 113th Cavalry Group and the complete 102d Division, General Gillem's XIII Corps on 8 November took over defense of the seventeen-mile line west of Geilenkirchen"; p399: the corps had recently arrived from a Normandy staging area with no troops; the 4 November Ninth Army directive had given it the defensive line). Event definition: activation here means the corps' first operational sector: XIII Corps takes over a front with its first troops (the 113th Cavalry Group and the complete 102nd Division); the headquarters itself existed earlier (it had recently arrived from a Normandy staging area, p399) and Ninth Army had it assigned from 4 November; the British XXX Corps began arriving the next day to relieve it. Relationship: Ninth Army assigned (Siegfried p399, p401; CMH tables for the 84th and 102nd Divisions list XIII Corps from 7-8 November). Location: The atlas lists Tongeren from 26 October, 13 days earlier; no later place in the window before 8 November. Coordinates: Wikipedia (en): Tongeren. Event support: high (Green Book narrative). Location support: low (13 days to the nearest atlas entry; the headquarters is not tied to the date).

## 12. C0539 — III Corps (1944-12-04)

_Why picked: post-review: reclassified as subordinate_assignment (a CMH table date for the first division), not an activation; event support low._

- **nationality**: US
- **echelon**: corps
- **parent_formation**: Third Army (US-ARMY-003A)
- **command_relationships**: [{"unit_id":"US-ARMY-003A","name":"Third Army","relationship":"assigned","effective_from":"1944-10-10","ordered_date":"1944-10-10","date_basis":"narrative","note":"Lorraine p299: the III Corps headquarters was assigned to the Third Army on 10 October"}]
- **commander**: Major General John Millikin
- **latitude**: 49.1106
- **longitude**: 6.0306
- **location_name**: Gravelotte, Moselle
- **location_represents**: headquarters
- **precision_km**: 5
- **confidence**: 0.3
- **campaign**: Rhineland
- **operation_name**: 
- **sub_operation_name**: Lorraine
- **composing_units**: 
- **event_type**: subordinate_assignment
- **current_activity**: CMH table first lists the 87th Division under III Corps; the corps is in Third Army since 10 October
- **engaged_with**: 
- **strength_status**: unknown
- **strength_json**: 
- **conflict_group_id**: 
- **claim_status**: preferred
- **location_date**: 1944-12-08
- **location_basis**: nearest_later_command_post
- **location_temporal_offset_days**: 4
- **source**: https://www.ibiblio.org/hyperwar/USA/USA-E-Lorraine/USA-E-Lorraine-6.html#page299 | https://web.archive.org/web/2018/http://www.history.army.mil/documents/ETO-OB/87ID-ETO.htm | https://www.ww2byday.com/70/mapunit/ ; coords: Wikipedia (en): Gravelotte
- **notes**: Event date: 4 December 1944 (the CMH table of the 87th Division lists III Corps as its corps from 4 December; Lorraine p299: the III Corps headquarters, newly arrived in Normandy, was assigned to the Third Army on 10 October and "as yet commanded only a few corps troops"). Event definition: a table observation, not an activation. The CMH division table first shows III Corps over a division, the 87th, on 4 December; the headquarters had been in Third Army since 10 October and its operational start (its first attack) is the 22 December row (C0558); the corps was selected for the Bastogne counterattack on the night of 18 December (C0564). The 11th Armored Division table shows III Corps from 2 October while that division was still in England, a table quirk the row does not use. An earlier version of this row used activation as the event type. Relationship: Third Army assigned from 10 October (Lorraine p299). Location: Atlas lists the corps command post at Étain on 2 November and Gravelotte on 8 December; the later entry is used (four days). Coordinates: Wikipedia (en): Gravelotte. Event support: moderate (a Green Book statement for the assignment and a CMH table date for the first division). Location support: low (four days before the later atlas entry; the 2 November Étain entry is 32 days earlier).

## 13. C0564 — III Corps (1944-12-18)

_Why picked: new (C0564): a decision, not an execution: Bradley and Patton agree to move III Corps from Metz to Arlon and earmark three divisions (intended state)._

- **nationality**: US
- **echelon**: corps
- **parent_formation**: Third Army (US-ARMY-003A)
- **command_relationships**: [{"unit_id":"US-ARMY-003A","name":"Third Army","relationship":"assigned","effective_from":"1944-10-10","ordered_date":"1944-10-10","date_basis":"narrative","note":"Lorraine p299: the III Corps headquarters was assigned to the Third Army on 10 October"}]
- **commander**: Major General John Millikin
- **latitude**: 49.1203
- **longitude**: 6.1778
- **location_name**: Metz, Moselle
- **location_represents**: headquarters
- **precision_km**: 10
- **confidence**: 0.5
- **campaign**: Ardennes-Alsace
- **operation_name**: 
- **sub_operation_name**: Ardennes
- **composing_units**: 26th Infantry Division; 80th Infantry Division; 4th Armored Division
- **event_type**: other
- **current_activity**: Bradley and Patton agree to move III Corps headquarters from Metz to Arlon for the Bastogne counterattack
- **engaged_with**: 
- **strength_status**: unknown
- **strength_json**: 
- **conflict_group_id**: 
- **claim_status**: preferred
- **location_date**: 1944-12-18
- **location_basis**: town_centroid
- **location_temporal_offset_days**: 0
- **source**: https://www.ibiblio.org/hyperwar/USA/USA-E-Ardennes/USA-E-Ardennes-21.html#page509 | https://www.ww2byday.com/70/mapunit/ ; coords: copied from C0538 (Metz)
- **notes**: Event date: 18 December 1944 (Ardennes p509: the forces "had been earmarked as early as the night of 18 December when Bradley and Patton agreed to move the new III Corps headquarters (as yet inexperienced and untried) from Metz to Arlon"; the divisions given Millikin, the 26th, the 80th and the 4th Armored, "were selected almost automatically"). Event definition: a decision, not an execution. This row records the intended state of the sequence (agreed 18 December); the move to Arlon and the corps' counterattack front are later (the attack opens on 22 December, C0558). The corps stays assigned to Third Army throughout. Relationship: Third Army assigned (C0539). Location: Metz, the headquarters the corps leaves, named by the Green Book for the date; the atlas lists the command post at Gravelotte, about 10 km west, on 8 December, so the point is a town centroid with a wider precision. Coordinates: copied from C0538 (Metz). Event support: high (Green Book narrative, date stated). Location support: moderate (the town is named; the site within or near Metz is not).

## 14. C0562 — XXI Corps (1944-12-27)

_Why picked: post-review: reclassified as subordinate_assignment; the claim that Seventh Army made the corps operational on 27 December was not supported by the pages read._

- **nationality**: US
- **echelon**: corps
- **parent_formation**: Seventh Army (US-ARMY-007A)
- **command_relationships**: [{"unit_id":"US-ARMY-007A","name":"Seventh Army","relationship":"assigned","effective_from":"1944-12-27","date_basis":"assignment_table","note":"CMH ETO table, 36th Division row of 27 December: Seventh Army"},{"unit_id":"US-AG-006G","name":"6th Army Group","relationship":"assigned","effective_from":"1944-12-27","date_basis":"assignment_table","note":"CMH table: 6th"}]
- **commander**: Major General Frank W. Milburn
- **latitude**: 48.7700
- **longitude**: 7.2600
- **location_name**: Phalsbourg, Moselle
- **location_represents**: headquarters
- **precision_km**: 5
- **confidence**: 0.5
- **campaign**: Ardennes-Alsace
- **operation_name**: 
- **sub_operation_name**: Alsace
- **composing_units**: 
- **event_type**: subordinate_assignment
- **current_activity**: CMH table first lists the 36th Division under XXI Corps and Seventh Army
- **engaged_with**: 
- **strength_status**: unknown
- **strength_json**: 
- **conflict_group_id**: 
- **claim_status**: preferred
- **location_date**: 1944-12-28
- **location_basis**: nearest_later_command_post
- **location_temporal_offset_days**: 1
- **source**: https://web.archive.org/web/2018/http://www.history.army.mil/documents/ETO-OB/36ID-ETO.htm | https://www.ibiblio.org/hyperwar/USA/USA-E-Riviera/USA-E-Riviera-27.html#page512 | https://www.ibiblio.org/hyperwar/USA/USA-E-Riviera/USA-E-Riviera-29.html#page534 | https://www.ww2byday.com/85/mapunit/ ; coords: Wikipedia (en): Phalsbourg
- **notes**: Event date: 27 December 1944 (CMH ETO table of the 36th Division: XXI Corps and Seventh Army from 27 December; Riviera p512 note 26: the northern sector's place "was taken first by a regiment of the 36th Division and then by the new XXI Corps, which supervised a miscellaneous collection of units"; p534 names Maj. Gen. Frank W. Milburn). The date is the table's, not the Green Book's. Event definition: a table observation, not an activation. The table first lists the 36th Division under XXI Corps; the Green Book (p533) has the XXI Corps headquarters temporarily in charge of Patch's northern flank at a date it does not give, so the row does not claim that the corps took a sector or became operational on 27 December. Its later role in the Colmar pocket planning (Operation Cheerful) is outside this window. An earlier version of this row used activation as the event type and said Seventh Army made the corps operational on 27 December; the pages read do not support that. Relationship: Seventh Army assigned and 6th Army Group assigned (CMH table). Location: Atlas lists the corps command post at Phalsbourg on 28 December, one day after the table date. Coordinates: Wikipedia (en): Phalsbourg. Event support: low (a CMH table date and an undated Green Book note). Location support: moderate (one day later).

## 15. C0557 — 4th Armored Division (1944-12-26)

_Why picked: post-review: the division row is an objective with a representative point; the spearhead is the CCR component (C0566) under Col. Blanchard, Abrams commanding the 37th Tank Battalion._

- **nationality**: US
- **echelon**: division
- **parent_formation**: III Corps (US-COR-003C)
- **command_relationships**: [{"unit_id":"US-COR-003C","name":"III Corps","relationship":"unspecified_subordination","effective_from":"1944-12-19","date_basis":"assignment_table","note":"CMH ETO-OB assignment table (single corps column; the table does not say assigned or attached for corps)"},{"unit_id":"US-ARMY-003A","name":"Third Army","relationship":"assigned","effective_from":"1944-12-19","date_basis":"assignment_table","note":"CMH ETO-OB assignment table, Army Assigned column: \"Third\""},{"unit_id":"US-AG-012G","name":"12th Army Group","relationship":"assigned","effective_from":"1944-12-19","date_basis":"assignment_table","note":"CMH ETO-OB assignment table, Army Group Assigned column: \"12th\""}]
- **commander**: Major General Hugh J Gaffey
- **latitude**: 49.9665
- **longitude**: 5.6816
- **location_name**: Assenois, Luxembourg
- **location_represents**: objective
- **precision_km**: 5
- **confidence**: 0.5
- **campaign**: Ardennes-Alsace
- **operation_name**: 
- **sub_operation_name**: Bastogne
- **composing_units**: Combat Command Reserve, 4th Armored Division
- **event_type**: attack
- **current_activity**: relief column breaks through at Assenois at 1650 and contacts the Bastogne garrison
- **engaged_with**: 
- **strength_status**: unknown
- **strength_json**: 
- **conflict_group_id**: 
- **claim_status**: preferred
- **location_date**: 1944-12-26
- **location_basis**: representative_point
- **location_temporal_offset_days**: 0
- **source**: https://www.ibiblio.org/hyperwar/USA/USA-E-Ardennes/USA-E-Ardennes-21.html#page552 | https://www.ibiblio.org/hyperwar/USA/USA-E-Ardennes/USA-E-Ardennes-21.html#page553 | https://www.ibiblio.org/hyperwar/USA/USA-E-Ardennes/USA-E-Ardennes-21.html#page554 ; coords: OpenStreetMap Nominatim: Assenois, Vaux-sur-Sûre, Bastogne, Luxembourg, Wallonie, 6640, België / Belgique
- **notes**: Event date: 26 December 1944 (Ardennes p552: the plan for the attack on 26 December; p554: "At 1650 (the time is indelibly recorded in the 4th Armored Division record) Boggess saw some engineers in friendly uniform ... contact with the Bastogne garrison had been made"). Event definition: the division's relief of Bastogne. The spearhead was the Reserve Combat Command (CCR), commanded by Col. Wendell Blanchard, whose 37th Tank Battalion (Lt. Col. Creighton Abrams) and 53rd Armored Infantry Battalion dashed through Assenois and met the 326th Airborne Engineers of the 101st; the CCR component is recorded on its own row (C0566). The road stayed narrow and under fire for several days. An earlier version of this row called the CCR commander Abrams; he commanded the 37th Tank Battalion. Relationship: III Corps and Third Army (CMH table, from 19 December). Location: Assenois, the place the division's lead element captured, used as a representative point for the division, whose headquarters was not there (the division headquarters place on 26 December is not recorded in this row). Coordinates: OpenStreetMap Nominatim: Assenois, Vaux-sur-Sûre, Bastogne, Luxembourg, Wallonie, 6640, België / Belgique. Event support: high (a timed contact in the Green Book). Location support: moderate (the village is certain; it is the objective of the division's spearhead, not the division's own position). Objective check: the strategic objective was Bastogne; the contact is documented at Assenois on the row date, so Assenois is the place captured and Bastogne is not claimed.

## 16. C0566 — Combat Command Reserve, 4th Armored Division (1944-12-26)

_Why picked: new (C0566): the Reserve Combat Command, the component that made the 1650 contact at Assenois._

- **nationality**: US
- **echelon**: regiment/battle_group
- **parent_formation**: 4th Armored Division (US-ARM-004D)
- **command_relationships**: [{"unit_id":"US-ARM-004D","name":"4th Armored Division","relationship":"organic","date_basis":"narrative","note":"Ardennes p552: Gaffey formed the Reserve Combat Command as a balanced task force of the division"}]
- **commander**: Colonel Wendell Blanchard
- **latitude**: 49.9665
- **longitude**: 5.6816
- **location_name**: Assenois, Luxembourg
- **location_represents**: front_line_point
- **precision_km**: 3
- **confidence**: 0.7
- **campaign**: Ardennes-Alsace
- **operation_name**: 
- **sub_operation_name**: Bastogne
- **composing_units**: 37th Tank Battalion; 53rd Armored Infantry Battalion
- **event_type**: attack
- **current_activity**: reaches the Bastogne perimeter at Assenois at 1650 and meets the 326th Airborne Engineers
- **engaged_with**: 
- **strength_status**: unknown
- **strength_json**: 
- **conflict_group_id**: 
- **claim_status**: preferred
- **location_date**: 1944-12-26
- **location_basis**: documented_on_date
- **location_temporal_offset_days**: 0
- **source**: https://www.ibiblio.org/hyperwar/USA/USA-E-Ardennes/USA-E-Ardennes-21.html#page552 | https://www.ibiblio.org/hyperwar/USA/USA-E-Ardennes/USA-E-Ardennes-21.html#page553 | https://www.ibiblio.org/hyperwar/USA/USA-E-Ardennes/USA-E-Ardennes-21.html#page554 ; coords: OpenStreetMap Nominatim: Assenois, Vaux-sur-Sûre, Bastogne, Luxembourg, Wallonie, 6640, België / Belgique
- **notes**: Event date: 26 December 1944 (Ardennes p552-554: CCR's attack on the 26th; p554: at 1650 Boggess saw engineers in friendly uniform and contact with the Bastogne garrison had been made). Event definition: the lead tanks of the 37th Tank Battalion (Lt. Col. Creighton Abrams) and the 53rd Armored Infantry Battalion of CCR dash through Assenois and meet the 326th Airborne Engineers of the 101st at a pillbox just north of the village, ending the encirclement. CCR is a component of the 4th Armored Division (C0557 is the division row). Relationship: organic to the 4th Armored Division, which is under III Corps (C0557). Location: Assenois, the village through which the dash was made; the point is the road contact, not a headquarters. Coordinates: OpenStreetMap Nominatim: Assenois, Vaux-sur-Sûre, Bastogne, Luxembourg, Wallonie, 6640, België / Belgique. Event support: high (a timed contact in the Green Book). Location support: high for the village, moderate for the exact contact point. Objective check: the objective was Bastogne; the contact is documented at Assenois on the row date, so documented_on_date holds for this front-line point and not for the town.

## 17. C0529 — VII Corps (1944-10-21)

_Why picked: objective row: Aachen is both the objective and the place of the surrender, so documented_on_date holds; check the Objective check sentence._

- **nationality**: US
- **echelon**: corps
- **parent_formation**: First Army (US-ARMY-001A)
- **command_relationships**: [{"unit_id":"US-ARMY-001A","name":"First Army","relationship":"assigned","effective_from":"1944-08-01","date_basis":"narrative","note":"12th Army Group became operational 1 August with First and Third Armies; Breakout-18 p343"}]
- **commander**: Major General J. Lawton Collins
- **latitude**: 50.7756
- **longitude**: 6.0836
- **location_name**: Aachen, North Rhine-Westphalia
- **location_represents**: objective
- **precision_km**: 3
- **confidence**: 0.7
- **campaign**: Rhineland
- **operation_name**: 
- **sub_operation_name**: Aachen
- **composing_units**: 
- **event_type**: capture
- **current_activity**: 1st Division takes Aachen; the garrison commander surrenders
- **engaged_with**: 
- **strength_status**: unknown
- **strength_json**: 
- **conflict_group_id**: 
- **claim_status**: preferred
- **location_date**: 1944-10-21
- **location_basis**: documented_on_date
- **location_temporal_offset_days**: 0
- **source**: https://www.ibiblio.org/hyperwar/USA/USA-E-Siegfried/USA-E-Siegfried-13.html#page319 | https://www.ibiblio.org/hyperwar/USA/USA-E-Siegfried/USA-E-Siegfried-17.html#page390 | https://www.ibiblio.org/hyperwar/USA/USA-E-Siegfried/USA-E-Siegfried-13.html#page315 ; coords: Wikipedia (en): Aachen
- **notes**: Event date: 21 October 1944 (Siegfried p319: "21 October 1944 in Aachen, the first large German city lost in the war"; p390: "21 October, the day Aachen fell"; p315: Colonel Wilck was ready to end the fight). Event definition: the German garrison of Aachen, under Colonel Wilck, surrenders to the 26th Infantry of the VII Corps' 1st Division. The row is the city's fall, not the Aachen encirclement of 16 October. Relationship: First Army assigned. Location: Aachen city centroid; the surrender took place in a bunker inside the city, which this point does not claim to fix. Coordinates: Wikipedia (en): Aachen. Event support: high (dated three times in the Green Book). Location support: high for the city, low for the site inside it. Objective check: the objective was the city itself and the surrender happened in it on the row date, so documented_on_date holds.

## 18. C0516 — 6th Army Group (1944-10-02)

_Why picked: post-review: reclassified as hq_observation (a command-post list does not date a move); army group place from one atlas list only (0.5 / 5 km), 290 km and 17 days from the Lyon row._

- **nationality**: US
- **echelon**: army_group
- **parent_formation**: Supreme Headquarters Allied Expeditionary Force (SHAEF) (ALL-SHAEF-000H)
- **command_relationships**: [{"unit_id":"ALL-SHAEF-000H","name":"Supreme Headquarters Allied Expeditionary Force (SHAEF)","relationship":"operational_control","effective_from":"1944-09-15","ordered_date":"1944-09-14","date_basis":"order","note":"Tactical control passed from AFHQ to SHAEF at 0001B, 15 September 1944 (6th Army Group G-3 Section Final Report); see C0222"}]
- **commander**: Lieutenant General Jacob L. Devers
- **latitude**: 48.2225
- **longitude**: 6.2231
- **location_name**: Dompaire, Vosges
- **location_represents**: headquarters
- **precision_km**: 5
- **confidence**: 0.5
- **campaign**: Rhineland
- **operation_name**: 
- **sub_operation_name**: Vosges
- **composing_units**: 
- **event_type**: hq_observation
- **current_activity**: army group command post listed at Dompaire
- **engaged_with**: 
- **strength_status**: unknown
- **strength_json**: 
- **conflict_group_id**: 
- **claim_status**: preferred
- **location_date**: 1944-10-02
- **location_basis**: documented_on_date
- **location_temporal_offset_days**: 0
- **source**: https://www.ww2byday.com/98/mapunit/ ; coords: Wikipedia (en): Dompaire
- **notes**: Event date: 2 October 1944 (CMH command-post list as compiled by World War II by Day: Dompaire from 2 October; the army group's previous headquarters place in the dataset is Lyon on 15 September, C0222). Event definition: an observation of the army group headquarters at Dompaire from 2 October; the source is a command-post list, which does not date a move (the previous place in the dataset is Lyon, C0222; the Batch 1 point for that row was Vesoul, a front-area reference that the Batch 2 review replaced with the G-3 Section Final Report's Palais de la Foire at Lyon, see review_changes.md Batch 2, C0222). The move north from the Rhône valley, probably earlier, is not dated here. No Green Book page used dates the move. Relationship: SHAEF operational control from 0001B, 15 September (order of 14 September, G-3 Section Final Report; see C0222); the army group was not organic to SHAEF. Location: Dompaire commune centroid; the site within the commune is not stated. Coordinates: Wikipedia (en): Dompaire. Event support: moderate (single list; no narrative text dates the move). Location support: moderate (commune centroid from a command-post list, no second source for the place).
