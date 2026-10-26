# Spot-check sample, Batch 2 (15 rows), post-review

Post-review state (25 October 2026). The same 15 rows as the first Batch 2 sample, after the reviewer's findings were verified against the sources and applied or declined (`review_changes.md`, "Batch 2 review corrections"); each 'Why picked' line now says what was corrected. Rows were chosen by risk from the 33 new Batch 2 claims (C0483 to C0515) and the existing rows whose command relationships or confidence Batch 2 changed (C0289, C0296, C0310, C0425): command transitions between armies and corps, the weakest locations, and the relationship-type judgments. New fields since the first sample: location_date, location_basis, location_temporal_offset_days, and relationship keys ordered_date, effective_to and effective_to_basis inside command_relationships. **Refreshed 25 October 2026 (Batch 3 review commit):** the new `campaign` column is shown and `operation_name` is the corrected value (blank after the named operation's dates); no other field of these rows changed.

## 1. C0484 — First Army (1944-08-01)

_Why picked: First Army 1 Aug handover to Hodges. Corrected: no longer a conflict (G015 dissolved); Vouilly (plaque: until 2 Aug) and Saint-Gilles (CMH list: from 1 Aug, C0485) are a move in sequence._

- **nationality**: US
- **echelon**: army
- **parent_formation**: 12th Army Group (US-AG-012G)
- **command_relationships**: [{"unit_id":"US-AG-012G","name":"US 12th Army Group","relationship":"assigned","effective_from":"1944-08-01","date_basis":"narrative","note":"Breakout-18 p343"}]
- **commander**: Lieutenant General Courtney H. Hodges
- **latitude**: 49.2953
- **longitude**: -1.0344
- **location_name**: Vouilly (Isigny-sur-Mer), Calvados
- **location_represents**: headquarters
- **precision_km**: 5
- **confidence**: 0.5
- **campaign**: Northern France
- **operation_name**: Overlord
- **sub_operation_name**: Pursuit
- **composing_units**: 
- **event_type**: command_change
- **current_activity**: Hodges assumes command as First Army passes to 12th Army Group
- **engaged_with**: 
- **strength_status**: unknown
- **strength_json**: 
- **conflict_group_id**: 
- **claim_status**: preferred
- **location_date**: 1944-08-01
- **location_basis**: documented_on_date
- **location_temporal_offset_days**: 0
- **source**: https://www.ibiblio.org/hyperwar/USA/USA-E-Breakout/USA-E-Breakout-18.html#page343 | https://www.normandie44lamemoire.com/en/2014/04/30/vouilly-isigny-sur-mer/ | https://www.uswarmemorials.org/html/monument_details.php?MemID=4000&SiteID=2906 ; coords: Wikipedia (en): Vouilly
- **notes**: Event date: Breakout-18 p343: at noon on 1 August the 12th Army Group became operational, General Hodges assumed command of First Army and Third Army came to life. Event definition: change of First Army commander (Bradley to Hodges) and of its parent headquarters (21st Army Group to 12th Army Group). Location: the Vouilly plaque and normandie44lamemoire say the army headquarters moved to Vouilly on 2 July and stayed until 2 August (a local memorial inaugurated in 2018-2019). The CMH list (World War II by Day) has Saint-Gilles from 1 August and Isigny (which includes Vouilly) from 5 July. Review (Batch 2 corrections): C0484 and C0485 were a conflict group, G015. The two sources do not exclude each other: one says the headquarters left Vouilly on 2 August, the other dates the Saint-Gilles entry to 1 August, 23 km away. They fit a move on 1-2 August, with the order of events within those two days not documented (an advance echelon, the main headquarters, or the list's arrival date convention), so G015 is dissolved and C0485 is the next headquarters location, not an alternative. This row keeps Vouilly because the plaque places the headquarters there through 1 August. Relationship: 12th Army Group assigned from 1 August; 21st Army Group control ended 31 July (C0483). Event support: high (Green Book, noon 1 August). Location support: moderate (local memorial; CMH list differs by a day and 23 km).

## 2. C0289 — Third Army (1944-08-01)

_Why picked: Third Army 1 Aug. Corrected: precision widened 5 to 10 km (Néhou vs Bricquebec, 8 km); 0.7 kept under the rubric, with Event / Locality / Coordinate support spelled out in the notes._

- **nationality**: US
- **echelon**: army
- **parent_formation**: 12th Army Group (US-AG-012G)
- **command_relationships**: [{"unit_id":"US-AG-012G","name":"US 12th Army Group","relationship":"assigned","effective_from":"1944-08-01","date_basis":"narrative"}]
- **commander**: Lieutenant General George S. Patton Jr.
- **latitude**: 49.4209
- **longitude**: -1.5430
- **location_name**: Néhou, Manche
- **location_represents**: headquarters
- **precision_km**: 10
- **confidence**: 0.7
- **campaign**: Northern France
- **operation_name**: Overlord
- **sub_operation_name**: Cobra
- **composing_units**: 
- **event_type**: activation
- **current_activity**: becoming operational under Patton at Néhou with VIII Corps passing to it
- **engaged_with**: 
- **strength_status**: unknown
- **strength_json**: 
- **conflict_group_id**: 
- **claim_status**: preferred
- **location_date**: 1944-08-01
- **location_basis**: town_centroid
- **location_temporal_offset_days**: 0
- **source**: https://www.ibiblio.org/hyperwar/USA/USA-E-Breakout/USA-E-Breakout-18.html#page343 | https://en.wikipedia.org/wiki/Third_Army_(United_States) | https://en.kilroytrip.fr/photos-ww2/qg-secret-patton | https://normandie1944.jimdoweb.com/kampf-um-cherbourg/orte-und-denkm%C3%A4ler-auf-dem-cotentin/nehou/ | https://www.uswarmemorials.org/html/monument_details.php?MemID=537&SiteID=307 | https://www.ww2byday.com/96/mapunit/ ; coords: OpenStreetMap Nominatim (Néhou, Manche, France)
- **notes**: Event date: Breakout-18 p343 (Third Army operational at noon, 1 August, with VIII Corps in the Pontaubault–Avranches area). Event definition: the army becomes operational. Location: local-history sources (KilroyTrip, normandie1944) place Patton's Third Army headquarters in an orchard at Néhou from 6 July to about 2 August 1944, so the headquarters was at Néhou on 1 August; the Green Book does not give the location. Coordinates: OpenStreetMap Nominatim centroid of Néhou (the orchard is not located). Relationship: 12th Army Group assigned (Breakout-18 p343). Previously this row carried an Avranches area point (50 km) because no headquarters location had been found. Batch 2 check: the Néhou memorial text (uswarmemorials.org) says Patton's command post was in the village from 6 July to 2 August 1944, and the CMH command-post list (World War II by Day) puts Third Army at Bricquebec-en-Cotentin, about 8 km away, from 26 July to 1 August with Folligny from 2 August (C0486). The two sources agree on the area and the departure date, so confidence is 0.7; the Néhou centroid is kept. Batch 2 review: event support is high (Breakout-18 p343: Third Army operational under Patton at noon on 1 August). Locality support is moderate: three local sources (KilroyTrip, normandie1944, the Néhou memorial) put the headquarters at Néhou, while the CMH list names Bricquebec, about 8 km away, so the precision radius is widened from 5 to 10 km to cover both. The coordinate is the Néhou village centroid and the orchard is not located. The 0.7 follows the rubric for an approximate location with two source families; it is a composite score and does not mean a 70% chance that the command post stood at these coordinates. Event support: high (Green Book, noon 1 August). Location support: moderate (village centroid, sources differ by 8 km).

## 3. C0487 — Ninth Army (1944-09-10)

_Why picked: Ninth Army 10 Sep. Corrected: the VIII Corps transfer (10 Sep, documented) is separated from the two divisions, whose dates the text does not give (C0512, C0514)._

- **nationality**: US
- **echelon**: army
- **parent_formation**: 12th Army Group (US-AG-012G)
- **command_relationships**: [{"unit_id":"US-AG-012G","name":"US 12th Army Group","relationship":"assigned","effective_from":"1944-09-05","date_basis":"narrative","note":"Breakout-30 p636; CMH ETO-OB tables"}]
- **commander**: Lieutenant General William H. Simpson
- **latitude**: 48.1147
- **longitude**: -1.6794
- **location_name**: Rennes, Ille-et-Vilaine
- **location_represents**: headquarters
- **precision_km**: 10
- **confidence**: 0.5
- **campaign**: Northern France
- **operation_name**: 
- **sub_operation_name**: Brittany
- **composing_units**: VIII Corps (from 10 September); 83rd Infantry Division (direct control from 10 September per CMH table); 6th Armored Division (direct control from 5-10 September, to mid-September)
- **event_type**: command_change
- **current_activity**: taking VIII Corps from Third Army control
- **engaged_with**: 
- **strength_status**: unknown
- **strength_json**: 
- **conflict_group_id**: 
- **claim_status**: preferred
- **location_date**: 1944-09-08
- **location_basis**: nearest_earlier_command_post
- **location_temporal_offset_days**: -2
- **source**: https://www.ibiblio.org/hyperwar/USA/USA-E-Breakout/USA-E-Breakout-30.html#page636 | https://www.ww2byday.com/92/mapunit/ | https://web.archive.org/web/2018/http://www.history.army.mil/documents/ETO-OB/8ID-ETO.htm ; coords: Wikipedia (en): Rennes
- **notes**: Event date: Breakout-30 p636: VIII Corps passed from Third Army to Ninth Army on 10 September; Ninth Army was operational at Rennes on 5 September. Event definition: Ninth Army takes over the Brest operation through VIII Corps (operational control). The 6th Armored and 83rd Divisions came directly under army control by separate decisions that the text does not date (see C0512 and C0514); they are not part of this event's date. Location: the CMH command-post list gives Ninth Army at Rennes on 8 September, two days before. Relationship: 12th Army Group assigned from 5 September. Event support: high for VIII Corps (Green Book, 10 September). Location support: moderate (command post listed two days earlier).

## 4. C0488 — 12th Army Group (1944-09-01)

_Why picked: 12th Army Group 1 Sep. Corrected: Laval named as last-known place with both bounding dates (23 Aug, 3 Sep) and the pre-1 Sep SHAEF / 21st Army Group chain stated; 0.3 / 50 km kept._

- **nationality**: US
- **echelon**: army_group
- **parent_formation**: Supreme Headquarters Allied Expeditionary Force (SHAEF) (ALL-SHAEF-000H)
- **command_relationships**: [{"unit_id":"ALL-SHAEF-000H","name":"SHAEF","relationship":"operational_control","effective_from":"1944-09-01","date_basis":"narrative","note":"Breakout-32 p683: on 1 September SHAEF became operational on the Continent and Eisenhower took direct command of the ground forces from Montgomery. Before this date SHAEF already held the Supreme Commander's authority over the campaign, exercised through 21st Army Group's coordination (C0223); only the direct operational channel begins on 1 September."}]
- **commander**: Lieutenant General Omar N. Bradley
- **latitude**: 48.0733
- **longitude**: -0.7689
- **location_name**: Laval, Mayenne (last listed command post)
- **location_represents**: headquarters
- **precision_km**: 50
- **confidence**: 0.3
- **campaign**: Northern France
- **operation_name**: 
- **sub_operation_name**: Pursuit
- **composing_units**: 
- **event_type**: command_change
- **current_activity**: SHAEF assumes direct control of the army group as Montgomery's coordination ends
- **engaged_with**: 
- **strength_status**: unknown
- **strength_json**: 
- **conflict_group_id**: 
- **claim_status**: preferred
- **location_date**: 1944-08-23
- **location_basis**: nearest_earlier_command_post
- **location_temporal_offset_days**: -9
- **source**: https://www.ibiblio.org/hyperwar/USA/USA-E-Breakout/USA-E-Breakout-32.html#page683 | https://www.ww2byday.com/97/mapunit/ | https://history.army.mil/brochures/norfran/norfran.htm | https://www.globalsecurity.org/military/library/report/other/us-army_germany_1944-46_ch10.htm | https://ibiblio.org/hyperwar/USA/USA-E-Supreme/USA-E-Supreme-14.html ; coords: Wikipedia (en): Laval, Mayenne
- **notes**: Event date: Breakout-32 p683: on 1 September SHAEF became operational on the Continent and Eisenhower took personal command of the ground forces, replacing Montgomery as pro tem commander. Event definition: 12th Army Group moves from 21st Army Group's coordination to direct SHAEF operational control; the higher-headquarters chain existed before (SHAEF authority exercised through Montgomery's coordination), so this is a change of channel, not the start of a relationship. Location: last-known position, not shown on the date. The CMH command-post list (World War II by Day) has the army group at Laval from 23 August and at Palaiseau from 3 September (C0489); a 12th Army Group history says Laval in August and Versailles in early September, and Eisenhower met Bradley, Hodges and Patton at Chartres on 2 September (a conference place, not the headquarters). So on 1 September the headquarters was at Laval or on the move to the Paris area; Laval is the last listed place, nine days earlier, with no stronger evidence for 1 September. Relationship: SHAEF operational control from 1 September; the 21st Army Group coordination (C0223) ended 31 August. Event support: high (Green Book, 1 September). Location support: low (last listed command post, nine days earlier).

## 5. C0502 — XV Corps (1944-08-24)

_Why picked: XV Corps 24 Aug. Corrected: First Army operational_control now ends 29 Aug; Third Army "assigned" marked inferred (no source documents it); the claim that the headquarters stayed at Mantes was removed._

- **nationality**: US
- **echelon**: corps
- **parent_formation**: First Army (US-ARMY-001A)
- **command_relationships**: [{"unit_id":"US-ARMY-001A","name":"US First Army","relationship":"operational_control","effective_from":"1944-08-24","effective_to":"1944-08-29","effective_to_basis":"narrative","date_basis":"narrative","note":"Breakout-28 p578: at 0600 on 24 August XV Corps passed from the control of Third Army to that of First Army. Breakout-31 p672: the XV Corps headquarters left the bridgehead at noon on 29 August (C0503). The hour the First Army relationship ended is not documented."},{"unit_id":"US-ARMY-003A","name":"US Third Army","relationship":"assigned","effective_from":"1944-08-01","date_basis":"inferred","note":"Standing assignment during 24-28 August is inferred, not documented: Breakout-22 p423 calls XV Corps a Third Army component; Lorraine ch. IV says the headquarters was taken from Third Army for the Seine operations and returned; no source says whether its formal assignment changed."}]
- **commander**: Major General Wade H. Haislip
- **latitude**: 48.9908
- **longitude**: 1.7172
- **location_name**: Mantes-la-Jolie, Yvelines
- **location_represents**: headquarters
- **precision_km**: 25
- **confidence**: 0.3
- **campaign**: Northern France
- **operation_name**: Overlord
- **sub_operation_name**: Pursuit
- **composing_units**: 
- **event_type**: command_change
- **current_activity**: passing from Third Army to First Army control at 0600
- **engaged_with**: 
- **strength_status**: unknown
- **strength_json**: 
- **conflict_group_id**: 
- **claim_status**: preferred
- **location_date**: 1944-08-20
- **location_basis**: nearest_earlier_command_post
- **location_temporal_offset_days**: -4
- **source**: https://www.ibiblio.org/hyperwar/USA/USA-E-Breakout/USA-E-Breakout-28.html#page578 | https://www.ww2byday.com/81/mapunit/ | https://ibiblio.org/hyperwar/USA/USA-E-Lorraine/USA-E-Lorraine-4.html | http://pattonthirdarmy.com/third-army/third-army-summary-of-after-action-in-world-war-ii-2/ | https://en.wikipedia.org/wiki/XV_Corps_(United_States) | https://www.ibiblio.org/hyperwar/USA/USA-E-Breakout/USA-E-Breakout-22.html#page423 | https://www.ibiblio.org/hyperwar/USA/USA-E-Breakout/USA-E-Breakout-31.html#page672 | https://www.ibiblio.org/hyperwar/USA/USA-E-Breakout/USA-E-Breakout-18.html#page344 ; coords: Wikipedia (en): Mantes-la-Jolie
- **notes**: Event date: Breakout-28 p578: at 0600 on 24 August XV Corps passed from the control of Third Army to that of First Army; Hodges told Haislip to clear the zone for British Second Army elements and to move the 5th Armored south. Event definition: control of the corps moves from Third Army to First Army; the row records First Army operational control. Relationship: First Army operational control from 0600 on 24 August is documented and ends on 29 August (C0503). Third Army assigned is inferred continuity (see the relationship note): Lorraine ch. IV says the corps was taken from Third Army and later returned, the Third Army After Action Report says it was released to First Army, and Wikipedia's subordination table shows First Army only for 24-28 August (secondary), so no source documents a retained Third Army assignment. Location: the CMH command-post list (World War II by Day) has the corps at Mantes-la-Jolie on 20 and on 28 August and no entry between. The Mantes vicinity is inferred from those two entries; it is not claimed that the headquarters stayed there without moving, and on 24 August it may have been elsewhere in the area. The row uses the 20 August entry (four days earlier; 28 August is four days later). Event support: high (Green Book, dated to the hour). Location support: low (command post listed four days earlier).

## 6. C0503 — XV Corps (1944-08-29)

_Why picked: XV Corps 29 Aug. Corrected: explicit end of First Army control; Third Army operational control restored 29 Aug (Third Army After Action Report), hour not documented._

- **nationality**: US
- **echelon**: corps
- **parent_formation**: Third Army (US-ARMY-003A)
- **command_relationships**: [{"unit_id":"US-ARMY-001A","name":"US First Army","relationship":"operational_control","effective_from":"1944-08-24","effective_to":"1944-08-29","effective_to_basis":"narrative","date_basis":"narrative","note":"Breakout-31 p672: at noon on 29 August XIX Corps took command of the divisions in the Mantes bridgehead as the XV Corps headquarters started for an assembly area southeast of Paris. The Third Army After Action Report dates the reversion to Third Army to 29 August. The hour is not documented."},{"unit_id":"US-ARMY-003A","name":"US Third Army","relationship":"operational_control","effective_from":"1944-08-29","date_basis":"narrative","note":"Third Army After Action Report: XV Corps did not revert to control of Third Army until 29 August; Breakout-31 p672 says the headquarters moved to an assembly area for eventual Third Army assignment; Lorraine ch. IV: returned to Third Army, with no divisions until 8-10 September. The hour of restoration is not documented; the standing assignment is inferred as in C0502."}]
- **commander**: Major General Wade H. Haislip
- **latitude**: 48.7222
- **longitude**: 1.7664
- **location_name**: Saint-Léger-en-Yvelines, Yvelines
- **location_represents**: headquarters
- **precision_km**: 5
- **confidence**: 0.5
- **campaign**: Northern France
- **operation_name**: Overlord
- **sub_operation_name**: Pursuit
- **composing_units**: 
- **event_type**: command_change
- **current_activity**: handing the Mantes bridgehead to XIX Corps and moving for Third Army
- **engaged_with**: 
- **strength_status**: unknown
- **strength_json**: 
- **conflict_group_id**: 
- **claim_status**: preferred
- **location_date**: 1944-08-29
- **location_basis**: documented_on_date
- **location_temporal_offset_days**: 0
- **source**: https://www.ibiblio.org/hyperwar/USA/USA-E-Breakout/USA-E-Breakout-31.html#page672 | https://www.ww2byday.com/81/mapunit/ | https://ibiblio.org/hyperwar/USA/USA-E-Lorraine/USA-E-Lorraine-4.html | http://pattonthirdarmy.com/third-army/third-army-summary-of-after-action-in-world-war-ii-2/ | https://en.wikipedia.org/wiki/XV_Corps_(United_States) ; coords: Wikipedia (en): Saint-Léger-en-Yvelines
- **notes**: Event date: Breakout-31 p672: at noon on 29 August XIX Corps took command of the three divisions in the Mantes bridgehead as the XV Corps headquarters started for an assembly area southeast of Paris and eventual Third Army assignment; the CMH list shows Saint-Léger-en-Yvelines on 29 August and Rozay-en-Brie on 30 August. Event definition: XV Corps gives up the Mantes bridgehead; First Army operational control ends and Third Army control resumes. Relationship: First Army operational control carries an explicit end on 29 August (the hour is not documented, only that the headquarters left at noon); Third Army operational control is restored from 29 August (Third Army After Action Report; Lorraine ch. IV) and the standing assignment during these days is inferred, as in C0502. Third Army 'assigned' is not re-listed because no source uses that word for 29 August. Location: Saint-Léger commune centroid, a stop on the move. Event support: high (Green Book, noon 29 August; Third Army After Action Report). Location support: moderate (CMH list, same day).

## 7. C0493 — XIX Corps (1944-07-28)

_Why picked: XIX Corps 28 Jul. Corrected: 113th Cavalry Group added; CCA, 2nd Armored is a separate temporary component (new row C0515); composing_units dated and qualified._

- **nationality**: US
- **echelon**: corps
- **parent_formation**: First Army (US-ARMY-001A)
- **command_relationships**: [{"unit_id":"US-ARMY-001A","name":"US First Army","relationship":"assigned"}]
- **commander**: Major General Charles H. Corlett
- **latitude**: 49.1200
- **longitude**: -1.0900
- **location_name**: Saint-Lô, Manche
- **location_represents**: headquarters
- **precision_km**: 10
- **confidence**: 0.5
- **campaign**: Northern France
- **operation_name**: Overlord
- **sub_operation_name**: Cobra
- **composing_units**: 30th Infantry Division (from noon 28 July); Combat Command A, 2nd Armored Division, with the 22nd Infantry attached (temporary, from noon 28 July); 113th Cavalry Group (from noon 28 July); 29th and 28th Infantry Divisions (displacing into the zone, control not dated)
- **event_type**: command_change
- **current_activity**: displacing west of the Vire and taking over the 30th Division and CCA, 2nd Armored
- **engaged_with**: 
- **strength_status**: unknown
- **strength_json**: 
- **conflict_group_id**: 
- **claim_status**: preferred
- **location_date**: 1944-07-30
- **location_basis**: nearest_later_command_post
- **location_temporal_offset_days**: 2
- **source**: https://www.ibiblio.org/hyperwar/USA/USA-E-Breakout/USA-E-Breakout-15.html#page285 | https://www.ibiblio.org/hyperwar/USA/USA-E-Breakout/USA-E-Breakout-16.html#page304 | https://www.ww2byday.com/80/mapunit/ | https://www.ibiblio.org/hyperwar/USA/USA-E-Breakout/USA-E-Breakout-15.html#page296 ; coords: Wikipedia (en): Saint-Lô
- **notes**: Event date: Breakout-15 p285 (evening of 27 July Bradley decided to displace XIX Corps west of the Vire; the 35th Division went to V Corps) and p296 (at noon on 28 July Corlett assumed responsibility for the units already engaged in his new zone: the 30th Division, CCA of the 2nd Armored Division reinforced by the 4th Division's 22nd Infantry, and the 113th Cavalry Group); Breakout-16 p304 (the 30th Division and CCA had been transferred from VII to XIX Corps by 28 July). Event definition: XIX Corps changes from the Vire sector east of the river to the zone west of it. The listed formations did not all come under the corps at one moment: three units from noon 28 July, the 28th and 29th Divisions displacing into the zone that day with no control date given. CCA is a separate temporary component (C0515): XIX Corps controlled CCA, not the whole 2nd Armored Division, which stayed with VII Corps until early August (C0507, C0226). composing_units therefore lists dated, qualified entries and is not an organic order of battle. Location: the CMH command-post list has the corps at Saint-Lô on 30 July, two days later. Relationship: First Army assigned; the transfer of the units is 'transferred' in the sources, not stated as assigned or attached, so their rows keep the table relationship. Event support: high (Green Book, noon 28 July). Location support: low (command post listed two days later).

## 8. C0490 — V Corps (1944-07-28)

_Why picked: V Corps 28 Jul: takes control of the 35th Division; sector point, not the HQ. Unchanged (reviewer: good)._

- **nationality**: US
- **echelon**: corps
- **parent_formation**: First Army (US-ARMY-001A)
- **command_relationships**: [{"unit_id":"US-ARMY-001A","name":"US First Army","relationship":"assigned"}]
- **commander**: Major General Leonard T. Gerow
- **latitude**: 49.0939
- **longitude**: -0.9731
- **location_name**: Saint-Jean-des-Baisants ridge sector, Manche
- **location_represents**: sector_center
- **precision_km**: 10
- **confidence**: 0.5
- **campaign**: Northern France
- **operation_name**: Overlord
- **sub_operation_name**: Cobra
- **composing_units**: 2nd Infantry Division; 5th Infantry Division; 35th Infantry Division (attached)
- **event_type**: command_change
- **current_activity**: taking control of the 35th Division and the front east of the Vire
- **engaged_with**: 
- **strength_status**: unknown
- **strength_json**: 
- **conflict_group_id**: 
- **claim_status**: preferred
- **location_date**: 1944-07-28
- **location_basis**: operational_area
- **location_temporal_offset_days**: 0
- **source**: https://www.ibiblio.org/hyperwar/USA/USA-E-Breakout/USA-E-Breakout-15.html#page285 | https://www.ibiblio.org/hyperwar/USA/USA-E-Breakout/USA-E-Breakout-15.html#page289 | https://www.ww2byday.com/71/mapunit/ ; coords: Wikipedia (en): Saint-Jean-des-Baisants
- **notes**: Event date: Breakout-15 p285 (evening of 27 July Bradley decided to displace XIX Corps west of the Vire, attached the 35th Division to V Corps and extended Gerow's responsibility to the river) and p289 (V Corps took control of the 35th on 28 July). Event definition: V Corps assumes all American-held ground east of the Vire with the 2nd, 5th and 35th Divisions; it secured the Saint-Jean-des-Baisants ridge that day. Relationship: First Army assigned; the 35th is attached to V Corps (see C0425). Location: ridge sector, not the corps command post; the CMH command-post list (World War II by Day) has V Corps at Balleroy from 21 July and Saint-Amand from 8 August. Event support: high (Green Book, dated to the day). Location support: low (sector, not the command post).

## 9. C0425 — 35th Infantry Division (1944-07-28)

_Why picked: 35th Division. Corrected: row dated 28 Jul (V Corps took control) with ordered_date 27 Jul preserved; location now the 28 Jul CMH division CP, 0.7 / 3 km._

- **nationality**: US
- **echelon**: division
- **parent_formation**: V Corps (US-COR-005C)
- **command_relationships**: [{"unit_id":"US-COR-005C","name":"US V Corps","relationship":"attached","effective_from":"1944-07-28","ordered_date":"1944-07-27","date_basis":"narrative","note":"Breakout-15 p285: on the evening of 27 July Bradley attached the 35th Division to V Corps (order); p289: V Corps took control of the division on 28 July (effective). The CMH table lists V Corps from 27 July, the order date."},{"unit_id":"US-ARMY-003A","name":"US Third Army","relationship":"assigned","effective_from":"1944-07-27","note":"CMH ETO-OB assignment table, Army Assigned column: \"Third\"","date_basis":"assignment_table"},{"unit_id":"US-ARMY-001A","name":"US First Army","relationship":"attached","effective_from":"1944-07-27","note":"CMH ETO-OB assignment table, Army Attached column: \"First\"","date_basis":"assignment_table"}]
- **commander**: Major General Paul W Baade
- **latitude**: 49.1158
- **longitude**: -1.0909
- **location_name**: St-Lo, Manche
- **location_represents**: headquarters
- **precision_km**: 3
- **confidence**: 0.7
- **campaign**: Northern France
- **operation_name**: Overlord
- **sub_operation_name**: 
- **composing_units**: 
- **event_type**: command_change
- **current_activity**: passing to V Corps control
- **engaged_with**: 
- **strength_status**: unknown
- **strength_json**: 
- **conflict_group_id**: 
- **claim_status**: preferred
- **location_date**: 1944-07-28
- **location_basis**: documented_on_date
- **location_temporal_offset_days**: 0
- **source**: https://web.archive.org/web/2018/http://www.history.army.mil/documents/ETO-OB/35ID-ETO.htm | https://www.ibiblio.org/hyperwar/USA/USA-E-Breakout/USA-E-Breakout-15.html#page285 | https://www.ibiblio.org/hyperwar/USA/USA-E-Breakout/USA-E-Breakout-15.html#page289 ; coords: OpenStreetMap Nominatim (Saint-Lo, Manche, France)
- **notes**: Event date: 28 July 1944, when V Corps took control of the 35th Division (Breakout-15 p289); the attachment was ordered on the evening of 27 July (p285) and the CMH assignment table lists V Corps from 27 July (the order date). Both dates are kept in the relationship entry (ordered_date and effective_from). Event definition: the 35th Division passes from XIX Corps to V Corps as XIX Corps displaces west of the Vire. Location: CMH division command post at St-Lô on 28 July (documented on the date; the row date was 27 July in Batch 2 and the St-Lô entry was then the nearest later one). Relationship: V Corps attached (Breakout-15); the army entries come from the CMH table (Third Army assigned, First Army attached). Event support: high (Green Book states the order and the control date). Location support: high (CMH command post, same day).

## 10. C0310 — VIII Corps (1944-07-26)

_Why picked: VIII Corps 26 Jul. Corrected: Coutances is the objective, so the basis is representative_point and the name says it is not the HQ; First Army attachment now ends 1 Aug._

- **nationality**: US
- **echelon**: corps
- **parent_formation**: First Army (US-ARMY-001A)
- **command_relationships**: [{"unit_id":"US-ARMY-003A","name":"US Third Army","relationship":"assigned","date_basis":"narrative","note":"Breakout-3 p36: VIII Corps was a headquarters assigned to Third Army but attached temporarily to First Army"},{"unit_id":"US-ARMY-001A","name":"US First Army","relationship":"attached","effective_to":"1944-08-01","effective_to_basis":"narrative","date_basis":"narrative","note":"Breakout-3 p36: attached temporarily to First Army; operational on the Continent 15 June; Breakout-18 p344: Patton took command of VIII Corps on 1 August, when Third Army became operational (end date)"}]
- **commander**: Major General Troy H. Middleton
- **latitude**: 49.0500
- **longitude**: -1.4400
- **location_name**: Coutances, Manche (objective of the 26 July attack; not the corps headquarters or its position)
- **location_represents**: objective
- **precision_km**: 10
- **confidence**: 0.5
- **campaign**: Northern France
- **operation_name**: Overlord
- **sub_operation_name**: Cobra
- **composing_units**: 
- **event_type**: attack
- **current_activity**: exploiting the Cobra breakthrough toward Coutances
- **engaged_with**: 
- **strength_status**: unknown
- **strength_json**: 
- **conflict_group_id**: 
- **claim_status**: preferred
- **location_date**: 1944-07-26
- **location_basis**: representative_point
- **location_temporal_offset_days**: 0
- **source**: https://www.ibiblio.org/hyperwar/USA/USA-E-Breakout/USA-E-Breakout-14.html | https://en.wikipedia.org/wiki/VIII_Corps_(United_States) | https://www.ibiblio.org/hyperwar/USA/USA-E-Breakout/USA-E-Breakout-3.html#page36 | https://www.ibiblio.org/hyperwar/USA/USA-E-Breakout/USA-E-Breakout-18.html#page344 ; coords: Wikipedia (en): Coutances
- **notes**: Wikipedia: VIII Corps joined the Cobra breakout on 26 July, took Coutances on 28 July and Avranches two days later. Batch 2 relationship fix: Breakout-3 p36 says VIII Corps was assigned to Third Army and attached temporarily to First Army, so the row lists both (parent is the army it served under). Batch 2 review: the point is the objective named for the attack (location_represents objective); VIII Corps took Coutances on 28 July, so on 26 July neither the corps headquarters nor its troops were there, and the basis is representative_point, not documented_on_date.

## 11. C0509 — 2nd Armored Division (1944-08-19)

_Why picked: 2nd Armored 19 Aug: XIX Corps relationship, assembly area. Corrected: the XIX entry ends 27 Aug (table day before XV Corps)._

- **nationality**: US
- **echelon**: division
- **parent_formation**: XIX Corps (US-COR-019C)
- **command_relationships**: [{"unit_id":"US-COR-019C","name":"US XIX Corps","relationship":"unspecified_subordination","effective_from":"1944-08-19","effective_to":"1944-08-27","effective_to_basis":"assignment_table","date_basis":"assignment_table","note":"CMH ETO-OB assignment table (single corps column; the table does not say assigned or attached for corps); the table shows XV Corps in the corps column from 28 August (C0510), so the last table day under XIX Corps is 27 August"},{"unit_id":"US-ARMY-001A","name":"US First Army","relationship":"assigned","effective_from":"1944-08-19","date_basis":"assignment_table","note":"CMH ETO-OB assignment table, Army Assigned column: \"First\""},{"unit_id":"US-AG-012G","name":"US 12th Army Group","relationship":"assigned","effective_from":"1944-08-19","date_basis":"assignment_table","note":"CMH ETO-OB assignment table, Army Group Assigned column: \"12th\""}]
- **commander**: Major General Edward H. Brooks
- **latitude**: 48.5208
- **longitude**: 0.5483
- **location_name**: Mortagne-au-Perche–Brezolles assembly area
- **location_represents**: sector_center
- **precision_km**: 25
- **confidence**: 0.5
- **campaign**: Northern France
- **operation_name**: Overlord
- **sub_operation_name**: Pursuit
- **composing_units**: 
- **event_type**: command_change
- **current_activity**: passing to XIX Corps for the Seine drive
- **engaged_with**: 
- **strength_status**: unknown
- **strength_json**: 
- **conflict_group_id**: 
- **claim_status**: preferred
- **location_date**: 1944-08-19
- **location_basis**: operational_area
- **location_temporal_offset_days**: 0
- **source**: https://web.archive.org/web/2018/http://www.history.army.mil/documents/ETO-OB/2AD-ETO.htm | https://www.ibiblio.org/hyperwar/USA/USA-E-Breakout/USA-E-Breakout-28.html#page576 ; coords: Wikipedia (en): Mortagne-au-Perche
- **notes**: Event date: CMH ETO-OB assignment table, 19 August 1944 (XIX Corps); Breakout-28 p576 has XIX Corps concentrated by 19 August with the 2nd Armored, 28th and 30th Divisions in the Mortagne-Brezolles area. Event definition: division assignment to a corps for the Seine drive. This is a different event from the 29 August corps takeover of the Mantes bridgehead (C0333), so the 19 August and 29 August dates are not alternative dates for one event. The table also shows V Corps for the single date 18 August, which no source used explains. Relationship: corps and army entries from the CMH table (corps column does not say assigned or attached). Event support: moderate (CMH table date; Green Book places the corps concentrated by 19 August). Location support: low (assembly area).

## 12. C0510 — 2nd Armored Division (1944-08-28)

_Why picked: 2nd Armored 28 Aug. Corrected: XV Corps is operational_control 28-29 Aug (temporary), not a reassignment; XIX link inferred to continue; point moved to the bridgehead sector (no Le Neubourg CP)._

- **nationality**: US
- **echelon**: division
- **parent_formation**: XV Corps (US-COR-015C)
- **command_relationships**: [{"unit_id":"US-COR-015C","name":"US XV Corps","relationship":"operational_control","effective_from":"1944-08-28","effective_to":"1944-08-29","effective_to_basis":"narrative","date_basis":"assignment_table","note":"CMH ETO-OB lists XV Corps in the single corps column on 28 August (table does not say assigned or attached). Breakout-31 p672: until XIX Corps headquarters took over the Mantes bridgehead at noon on 29 August XV Corps continued in command there, and the 2nd Armored crossed the Seine on 28 August to protect the left flank. About a day of command inside the bridgehead between two periods under XIX Corps, so recorded as temporary operational control, not a change of assignment."},{"unit_id":"US-COR-019C","name":"US XIX Corps","relationship":"unspecified_subordination","effective_from":"1944-08-28","date_basis":"inferred","note":"Standing corps link before (C0509, C0229) and after (C0511); continuation inferred from 28 August because no source says the XIX Corps link ended, only that XV Corps commanded the division in the bridgehead."},{"unit_id":"US-ARMY-001A","name":"US First Army","relationship":"assigned","effective_from":"1944-08-28","date_basis":"assignment_table","note":"CMH ETO-OB assignment table, Army Assigned column: \"First\""},{"unit_id":"US-AG-012G","name":"US 12th Army Group","relationship":"assigned","effective_from":"1944-08-28","date_basis":"assignment_table","note":"CMH ETO-OB assignment table, Army Group Assigned column: \"12th\""}]
- **commander**: Major General Edward H. Brooks
- **latitude**: 48.9908
- **longitude**: 1.7172
- **location_name**: Mantes-Gassicourt bridgehead area (Seine), Yvelines
- **location_represents**: sector_center
- **precision_km**: 10
- **confidence**: 0.5
- **campaign**: Northern France
- **operation_name**: Overlord
- **sub_operation_name**: Pursuit
- **composing_units**: 
- **event_type**: command_change
- **current_activity**: crossing the Seine into the Mantes bridgehead under XV Corps command
- **engaged_with**: 
- **strength_status**: unknown
- **strength_json**: 
- **conflict_group_id**: 
- **claim_status**: preferred
- **location_date**: 1944-08-28
- **location_basis**: operational_area
- **location_temporal_offset_days**: 0
- **source**: https://web.archive.org/web/2018/http://www.history.army.mil/documents/ETO-OB/2AD-ETO.htm | https://www.ibiblio.org/hyperwar/USA/USA-E-Breakout/USA-E-Breakout-31.html#page672 ; coords: Wikipedia (en): Mantes-la-Jolie
- **notes**: Event date: Breakout-31 p672: the 2nd Armored Division crossed the Seine on 28 August to protect the left flank of the Mantes-Gassicourt bridgehead, where XV Corps continued in command until noon on 29 August; the CMH assignment table lists XV Corps from 28 August. Event definition: temporary XV Corps operational control of the division inside the bridgehead between two periods under XIX Corps (C0509, C0511); it is not a change of assignment. The Army entries come from the CMH table (First Army assigned). Relationship: the table's corps column is single and does not say assigned or attached; the narrative shows a one-day command, so XV Corps is operational_control from 28 to 29 August and the XIX Corps link is shown as inferred continuity. Location: the bridgehead sector where the division crossed, not its command post. The earlier point (Le Neubourg, the 25 August command post, C0229) is not used because the division had crossed the Seine on 28 August. Event support: moderate (CMH table date and Green Book narrative; the relationship type is read from the narrative). Location support: low (bridgehead sector).

## 13. C0514 — 83rd Infantry Division (1944-09-10)

_Why picked: 83rd Division 10 Sep. Corrected: date kept from the table; point is the Loire sector where the division took Elster's surrender (0.5 / 25 km); Vendôme (15 Sep) is a later observation in the notes._

- **nationality**: US
- **echelon**: division
- **parent_formation**: Ninth Army (US-ARMY-009A)
- **command_relationships**: [{"unit_id":"US-ARMY-009A","name":"US Ninth Army","relationship":"assigned","effective_from":"1944-09-10","date_basis":"assignment_table","note":"CMH ETO-OB assignment table, Army Assigned column: \"Ninth\"; the table date 10 September is kept for the direct Ninth Army control, Breakout-30 p636 gives no date"},{"unit_id":"US-AG-012G","name":"US 12th Army Group","relationship":"assigned","effective_from":"1944-09-10","date_basis":"assignment_table","note":"CMH ETO-OB assignment table, Army Group Assigned column: \"12 th\""}]
- **commander**: Major General Robert C Macon
- **latitude**: 47.7792
- **longitude**: 1.6325
- **location_name**: Loire sector at Orléans, Beaugency and Mer, Loiret (sector point at Beaugency)
- **location_represents**: sector_center
- **precision_km**: 25
- **confidence**: 0.5
- **campaign**: Northern France
- **operation_name**: 
- **sub_operation_name**: Brittany
- **composing_units**: 
- **event_type**: command_change
- **current_activity**: placed directly under Ninth Army control, no corps
- **engaged_with**: 
- **strength_status**: unknown
- **strength_json**: 
- **conflict_group_id**: 
- **claim_status**: preferred
- **location_date**: 1944-09-10
- **location_basis**: operational_area
- **location_temporal_offset_days**: 0
- **source**: https://web.archive.org/web/2018/http://www.history.army.mil/documents/ETO-OB/83ID-ETO.htm | https://www.ibiblio.org/hyperwar/USA/USA-E-Breakout/USA-E-Breakout-30.html#page636 | https://www.ibiblio.org/hyperwar/USA/USA-E-Breakout/USA-E-Breakout-30.html#page653 | https://www.ibiblio.org/hyperwar/USA/USA-E-Breakout/USA-E-Breakout-30.html#page654 ; coords: Wikipedia (en): Beaugency
- **notes**: Event date: CMH ETO-OB assignment table, 10 September 1944 (Ninth Army assigned, no corps; the 5 September row still shows VIII Corps). Breakout-30 p636: Simpson placed the 6th Armored and 83rd Divisions directly under his own control so Middleton could concentrate on Brest; the text gives no date, so the table date is the basis (date_basis assignment_table). Event definition: division leaves VIII Corps for direct Ninth Army control. Location: Breakout-30 p653-654 has the 83rd Division on the Loire protecting the Third Army south flank and accepting the surrender of Elster's column (crossing at Orléans, Beaugency and Mer) on 10 September, so the point is a sector point on that stretch, not the division command post. The CMH command-post list has the division at Vendôme on 15 September (a later observation, five days after, not a 10 September location). Relationship: the table puts the division under Ninth Army with no corps while the text has it operating in the Third Army south-flank zone; both are recorded as the table shows. Event support: moderate (CMH table date; narrative undated). Location support: low (Loire sector).

## 14. C0296 — Seventh Army (1944-09-15)

_Why picked: Seventh Army 15 Sep. Corrected: AFHQ entry is unknown with a scoped note (retained functions, not administrative control); ordered_date 14 Sep, effective 15 Sep; Vesoul stays a representative point._

- **nationality**: US
- **echelon**: army
- **parent_formation**: 6th Army Group (US-AG-006G)
- **command_relationships**: [{"unit_id":"US-AG-006G","name":"US 6th Army Group","relationship":"assigned","effective_from":"1944-09-15","ordered_date":"1944-09-14","date_basis":"order","note":"6th Army Group G-3 report: on the afternoon of 14 September AFHQ ordered Seventh US Army and French Army B under 6th Army Group command as of 0001B hours, 15 September"},{"unit_id":"ALL-AFHQ-000H","name":"Allied Force Headquarters (AFHQ)","relationship":"unknown","effective_from":"1944-09-15","date_basis":"order","note":"6th Army Group G-3 report: responsibility for supply, administrative functions and civil affairs within the area overrun was retained by AFHQ pending further developments. That is a theater and territorial responsibility, not stated as command or administrative control of Seventh Army, so the relationship to the army is left unknown."}]
- **commander**: Lieutenant General Alexander M. Patch
- **latitude**: 47.6231
- **longitude**: 6.1558
- **location_name**: Vesoul, Haute-Saône (front, representative point)
- **location_represents**: sector_center
- **precision_km**: 50
- **confidence**: 0.3
- **campaign**: Rhineland
- **operation_name**: 
- **sub_operation_name**: 
- **composing_units**: 
- **event_type**: command_change
- **current_activity**: passing from AFHQ to 6th Army Group control
- **engaged_with**: 
- **strength_status**: unknown
- **strength_json**: 
- **conflict_group_id**: 
- **claim_status**: preferred
- **location_date**: 1944-09-15
- **location_basis**: representative_point
- **location_temporal_offset_days**: 0
- **source**: https://www.ibiblio.org/hyperwar/USA/USA-E-Breakout/USA-E-Breakout-32.html#page701 | https://en.wikipedia.org/wiki/Sixth_United_States_Army_Group ; coords: Wikipedia (en): Vesoul
- **notes**: Event date: Breakout-32 p701 (6th Army Group operational 15 September with Seventh Army and French First Army); the order reached the headquarters on the afternoon of 14 September, effective 0001B 15 September (6th Army Group G-3 report, ordered_date and effective_from). Event definition: Seventh Army passes from AFHQ to 6th Army Group command; tactical control of the group passed from AFHQ to SHAEF at the same time. Relationship: 6th Army Group assigned from 0001B, 15 September. AFHQ is listed with relationship unknown: the source says AFHQ kept supply, administrative and civil-affairs responsibility 'within the area overrun', which is a theater function and territory, not a statement that AFHQ held administrative control of Seventh Army; the earlier administrative_control entry was withdrawn in Batch 2 corrections. Location: Seventh Army headquarters on this date is not documented in the sources used (a SHAEF message of 9 September only expected it north of Lyon, FRUS 1944 Quebec, doc. 150); the Vesoul point is a representative point in the sector where VI Corps was operating, not a headquarters, and is why confidence is 0.3. Search: the 6th Army Group G-3 report (Lyon, 9-15 September) covers the army group only; the CMH list (World War II by Day) has Seventh Army first at Épinal on 2 October 1944; Breakout-32 p701 and Wikipedia name no place. Event support: high (6th Army Group report, order of 14 September). Location support: very low (representative point, headquarters not located).

## 15. C0499 — VIII Corps (1944-08-18)

_Why picked: VIII Corps 18 Aug: documented 120-mile move to Lesneven. Corrected: speed warning is now an explained exception; Lesneven is labelled the last confirmed place, not a verified position to 10 Sep._

- **nationality**: US
- **echelon**: corps
- **parent_formation**: Third Army (US-ARMY-003A)
- **command_relationships**: [{"unit_id":"US-ARMY-003A","name":"US Third Army","relationship":"assigned","effective_from":"1944-08-01","date_basis":"narrative","note":"Breakout-18 p343"}]
- **commander**: Major General Troy H. Middleton
- **latitude**: 48.5722
- **longitude**: -4.3147
- **location_name**: Lesneven, Finistère
- **location_represents**: headquarters
- **precision_km**: 5
- **confidence**: 0.7
- **campaign**: Northern France
- **operation_name**: Overlord
- **sub_operation_name**: Brest
- **composing_units**: 
- **event_type**: hq_move
- **current_activity**: command post moves 120 miles to Lesneven to open the siege of Brest
- **engaged_with**: 
- **strength_status**: unknown
- **strength_json**: 
- **conflict_group_id**: 
- **claim_status**: preferred
- **location_date**: 1944-08-18
- **location_basis**: documented_on_date
- **location_temporal_offset_days**: 0
- **source**: https://www.ibiblio.org/hyperwar/USA/USA-E-Breakout/USA-E-Breakout-30.html#page638 ; coords: Wikipedia (en): Lesneven
- **notes**: Event date: Breakout-30 p638: on 18 August the VIII Corps command post moved one hundred and twenty miles to Lesneven, fifteen miles from Brest, to undertake the siege. Event definition: headquarters move. Location: Lesneven town centroid. Later: no source used places the corps headquarters anywhere else before 24 September (St Aubin, CMH list), so Lesneven is the only documented headquarters for the 5 and 10 September command rows; those rows keep their Brest-sector points because the headquarters is not documented on those dates. Relationship: Third Army assigned. Coordinate check: the speed warning against C0313 (17 August) is the documented 120-mile move; the earlier point is the corps position before the move. Batch 2 review: Lesneven is a documented headquarters observation for 18 August. It is the last confirmed headquarters location before the CMH list's St Aubin on 24 September, not a verified position for each day between; the 5 and 10 September rows (C0315, C0316) do not use it as such. The speed warning against C0313 is an explained exception (data/coordinate_exceptions.csv).
