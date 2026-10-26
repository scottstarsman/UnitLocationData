# Spot-check sample, Batch 1 (15 rows)

Rows were chosen by risk, not at random, from the 268 new US claims (C0213 to C0480): army group and army rows with unsourced places, the three conflict groups (G012 to G014), attachments, new arrivals (including the low-confidence class and the 26th Division date), airborne landings, and a Dragoon landing. Every row's `strength_json` is empty: no Batch 1 row carries strength data, so there are no strength rows to check. The first line under each heading says why the row was picked. `command_relationships` is shown in addition to the fields of the first sample because the attachment calls are the main judgment in this batch. Corps V, VII, XII, XV and XX and the other armies are not in this sample; they use the same rules and can be drawn into a second sample if wanted. **Refreshed 25 October 2026 (Batch 2 commit):** the rows below show the same 15 claims in their current state, after the Batch 1 review corrections and the Batch 2 relationship regeneration (for example C0223 now at Saint-Sauveur-Lendelin, not Avranches); the "Why picked" lines are the original ones, so they describe the pre-review rows. The fields `composing_units`, `location_date`, `location_basis` and `location_temporal_offset_days`, added after the first version, are shown too. **Refreshed 25 October 2026 (Batch 3 review commit):** the new `campaign` column is shown and `operation_name` is the corrected value (blank after the named operation's dates); no other field of these rows changed.

## 1. C0223 — 12th Army Group (1944-08-01)

_Why picked: army group HQ place not sourced: representative point, 0.3 / 50 km._

- **nationality**: US
- **echelon**: army_group
- **parent_formation**: Supreme Headquarters Allied Expeditionary Force (SHAEF) (ALL-SHAEF-000H)
- **command_relationships**: [{"unit_id":"ALL-SHAEF-000H","name":"Supreme Headquarters Allied Expeditionary Force (SHAEF)","relationship":"assigned","effective_from":"1944-08-01","date_basis":"narrative","note":"Eisenhower, Supreme Commander; direct operational control by SHAEF from 1 September 1944"},{"unit_id":"UK-AG-021G","name":"British 21st Army Group","relationship":"coordinating","effective_from":"1944-08-01","effective_to":"1944-08-31","date_basis":"narrative","note":"Montgomery coordinated Allied ground operations until Eisenhower took direct control on 1 September 1944"}]
- **commander**: Lieutenant General Omar N. Bradley
- **latitude**: 49.1274
- **longitude**: -1.4271
- **location_name**: Saint-Sauveur-Lendelin (Château des Mares), Manche
- **location_represents**: headquarters
- **precision_km**: 5
- **confidence**: 0.7
- **campaign**: Northern France
- **operation_name**: Overlord
- **sub_operation_name**: Cobra
- **composing_units**: 
- **event_type**: activation
- **current_activity**: becoming operational at Saint-Sauveur-Lendelin under Bradley, controlling First and Third Armies
- **engaged_with**: 
- **strength_status**: unknown
- **strength_json**: 
- **conflict_group_id**: 
- **claim_status**: preferred
- **location_date**: 1944-08-01
- **location_basis**: documented_on_date
- **location_temporal_offset_days**: 0
- **source**: https://www.ibiblio.org/hyperwar/USA/USA-E-Breakout/USA-E-Breakout-18.html#page343 | https://en.wikipedia.org/wiki/Twelfth_United_States_Army_Group | https://warfarehistorynetwork.com/article/the-12th-army-group-gets-going/ | https://www.wikimanche.fr/Ch%C3%A2teau_des_Mares_(Saint-Sauveur-Lendelin) | https://www.dday-overlord.com/en/battle-of-normandy/cities/saint-sauveur-lendelin | https://www.ibiblio.org/hyperwar/USA/USA-E-Supreme/USA-E-Supreme-15.html ; coords: OpenStreetMap Nominatim (Château des Mares, Saint-Sauveur-Lendelin)
- **notes**: Event date: Breakout-18 p343 (12th Army Group operational at noon, 1 August; First Army under Hodges, Third Army operational under Patton). Event definition: the army group becomes operational. Relationship: SHAEF is the organisational parent (assigned). Montgomery's 21st Army Group coordinated both army groups in the field until Eisenhower assumed direct operational control on 1 September (CMH "Northern France" brochure; Pogue, Supreme Command ch. 15); some sources describe this as 21st Army Group operational control. Location: the headquarters opened at the Château des Mares, Saint-Sauveur-Lendelin (Warfare History Network; Wikimanche; dday-overlord); Bradley received Churchill there on 7 August and Eisenhower on 8 August. Avranches (the earlier point on this row) was the breakout area, not the headquarters, and is kept only as an area reference. Coordinates: OpenStreetMap Nominatim for the château. The Army "Essential to Success" text cited in review could not be opened here (access denied); the location is confirmed by the other sources.

## 2. C0222 — 6th Army Group (1944-09-15)

_Why picked: 6th Army Group, its only row: representative point at Vesoul, 0.3 / 50 km._

- **nationality**: US
- **echelon**: army_group
- **parent_formation**: Supreme Headquarters Allied Expeditionary Force (SHAEF) (ALL-SHAEF-000H)
- **command_relationships**: [{"unit_id":"ALL-SHAEF-000H","name":"Supreme Headquarters Allied Expeditionary Force (SHAEF)","relationship":"operational_control","effective_from":"1944-09-15","date_basis":"order","note":"Tactical control transferred from AFHQ to SHAEF at 0001B, 15 September 1944"},{"unit_id":"ALL-AFHQ-000H","name":"Allied Force Headquarters (AFHQ)","relationship":"unknown","effective_from":"1944-09-15","date_basis":"order","note":"6th Army Group G-3 report: AFHQ retained responsibility for supply, administrative functions and civil affairs within the area overrun pending further developments; a theater and territorial responsibility, not stated as administrative control of the army group, so the relationship is left unknown"}]
- **commander**: Lieutenant General Jacob L. Devers
- **latitude**: 45.7849
- **longitude**: 4.8538
- **location_name**: Lyon, Palais de la Foire (east bank of the Rhône), Rhône
- **location_represents**: headquarters
- **precision_km**: 5
- **confidence**: 0.5
- **campaign**: Rhineland
- **operation_name**: 
- **sub_operation_name**: 
- **composing_units**: 
- **event_type**: activation
- **current_activity**: becoming operational at Lyon under Devers with Seventh Army and French First Army
- **engaged_with**: 
- **strength_status**: unknown
- **strength_json**: 
- **conflict_group_id**: 
- **claim_status**: preferred
- **location_date**: 1944-09-15
- **location_basis**: documented_on_date
- **location_temporal_offset_days**: 0
- **source**: https://www.ibiblio.org/hyperwar/USA/USA-E-Breakout/USA-E-Breakout-32.html#page701 | https://www.ibiblio.org/hyperwar/USA/USA-E-Breakout/USA-E-Breakout-32.html#page683 | https://en.wikipedia.org/wiki/Sixth_United_States_Army_Group | https://www.trailblazersww2.org/pdf/SixthArmyG3pdf.pdf ; coords: OpenStreetMap Nominatim (Cité Internationale, Lyon; approximate stand-in for the Palais de la Foire)
- **notes**: Event date: Breakout-32 p701 and the 6th Army Group G-3 Section Final Report (Seventh Army and French Army B placed under command from 0001B, 15 September). Event definition: the army group becomes operational. Relationship: tactical control passed from AFHQ to SHAEF at 0001B on 15 September, so SHAEF is the operational parent (operational_control); AFHQ retained responsibility for supply, administrative functions and civil affairs within the area overrun pending further developments (G-3 report); that is a theater and territorial responsibility, not a stated administrative control of the army group, so AFHQ is listed with relationship unknown (Batch 2 review; the earlier administrative_control entry was withdrawn). The group was not organic to SHAEF. Location: the G-3 report says the move from Saint-Tropez began 9 September and was completed 15 September, and that the Palais de la Foire on the east bank of the Rhône was the first operational headquarters of the 6th Army Group. Vesoul (earlier point) was only the front area and is not a documented headquarters. Coordinates: approximate, the Cité Internationale area on the east bank of the Rhône (OpenStreetMap Nominatim); the Palais de la Foire could not be geocoded and the site is not independently confirmed.

## 3. C0284 — First Army (1944-07-25)

_Why picked: First Army, Cobra: army-level row with place from the Green Book._

- **nationality**: US
- **echelon**: army
- **parent_formation**: 21st Army Group (UK-AG-021G)
- **command_relationships**: [{"unit_id":"UK-AG-021G","name":"British 21st Army Group","relationship":"operational_control","effective_to":"1944-07-31","date_basis":"narrative","note":"US First Army served under 21st Army Group until 12th Army Group became operational (1 August 1944)"}]
- **commander**: Lieutenant General Omar N. Bradley
- **latitude**: 49.0997
- **longitude**: -1.2389
- **location_name**: Marigny, Manche (Cobra penetration area)
- **location_represents**: sector_center
- **precision_km**: 10
- **confidence**: 0.5
- **campaign**: Northern France
- **operation_name**: Overlord
- **sub_operation_name**: Cobra
- **composing_units**: 
- **event_type**: attack
- **current_activity**: launching Operation Cobra west of Saint-Lô with VII Corps in the lead
- **engaged_with**: German Panzer Lehr Division; German 353rd Infantry Division; German 5th Fallschirmjäger Division
- **strength_status**: unknown
- **strength_json**: 
- **conflict_group_id**: 
- **claim_status**: preferred
- **location_date**: 1944-07-25
- **location_basis**: operational_area
- **location_temporal_offset_days**: 0
- **source**: https://www.ibiblio.org/hyperwar/USA/USA-E-Breakout/USA-E-Breakout-13.html#page251 | https://www.ibiblio.org/hyperwar/USA/USA-E-Breakout/USA-E-Breakout-14.html | https://en.wikipedia.org/wiki/First_Army_(United_States) ; coords: Wikipedia (en): Marigny, Manche
- **notes**: Event date: Cobra opened 25 July (26 July was its second day, Breakout-13 p251). Event definition: the First Army offensive; VII Corps made the main effort. Location: Marigny marks the Cobra penetration sector, not General Bradley's First Army command post (Breakout-13/14). Opponents: engaged_with is not exhaustive. Breakout-13 describes Panzer Lehr (with a regiment of the 5th Parachute Division attached), elements of the 353rd Division and the 5th Parachute Division in the penetration sector, with the 275th Division and 2nd SS Panzer Division reacting afterwards. Relationship: First Army operated under 21st Army Group (Montgomery) until 12th Army Group became operational on 1 August.

## 4. C0297 — Ninth Army (1944-09-05)

_Why picked: Ninth Army activation: army row, date and place from Breakout and Pursuit._

- **nationality**: US
- **echelon**: army
- **parent_formation**: 12th Army Group (US-AG-012G)
- **command_relationships**: [{"unit_id":"US-AG-012G","name":"US 12th Army Group","relationship":"assigned","effective_from":"1944-09-05","date_basis":"narrative"}]
- **commander**: Lieutenant General William H. Simpson
- **latitude**: 48.1147
- **longitude**: -1.6794
- **location_name**: Rennes, Ille-et-Vilaine
- **location_represents**: headquarters
- **precision_km**: 5
- **confidence**: 0.7
- **campaign**: Northern France
- **operation_name**: 
- **sub_operation_name**: Brittany
- **composing_units**: 
- **event_type**: activation
- **current_activity**: becoming operational at Rennes under Simpson
- **engaged_with**: 
- **strength_status**: unknown
- **strength_json**: 
- **conflict_group_id**: 
- **claim_status**: preferred
- **location_date**: 1944-09-05
- **location_basis**: town_centroid
- **location_temporal_offset_days**: 0
- **source**: https://www.ibiblio.org/hyperwar/USA/USA-E-Breakout/USA-E-Breakout-30.html#page636 | https://en.wikipedia.org/wiki/Ninth_Army_(United_States) ; coords: Wikipedia (en): Rennes
- **notes**: Event date: Breakout-30 p636: Ninth Army became operational at Rennes on 5 September; VIII Corps passed to it five days later (see conflict group G013). Event definition: the army becomes operational. Relationship: assigned to 12th Army Group (Pogue, Supreme Command ch. 15). Location: Rennes, named by the Green Book for the headquarters; point is the town centroid.

## 5. C0315 — VIII Corps (1944-09-05)

_Why picked: conflict G013 (alternate): VIII Corps to Ninth Army 5 Sep (CMH tables, Wikipedia) vs 10 Sep._

- **nationality**: US
- **echelon**: corps
- **parent_formation**: Ninth Army (US-ARMY-009A)
- **command_relationships**: [{"unit_id":"US-ARMY-009A","name":"US Ninth Army","relationship":"unspecified_subordination","effective_from":"1944-09-05","date_basis":"assignment_table","note":"CMH ETO-OB tables; Green Book (Breakout-30 p636) dates the operational transfer 10 September"}]
- **commander**: Major General Troy H. Middleton
- **latitude**: 48.3906
- **longitude**: -4.4861
- **location_name**: Brest, Finistère
- **location_represents**: sector_center
- **precision_km**: 10
- **confidence**: 0.5
- **campaign**: Northern France
- **operation_name**: 
- **sub_operation_name**: Brest
- **composing_units**: 
- **event_type**: command_change
- **current_activity**: passing from Third Army to Ninth Army control
- **engaged_with**: 
- **strength_status**: unknown
- **strength_json**: 
- **conflict_group_id**: G013
- **claim_status**: alternate
- **location_date**: 1944-09-05
- **location_basis**: operational_area
- **location_temporal_offset_days**: 0
- **source**: https://web.archive.org/web/2018/http://www.history.army.mil/documents/ETO-OB/8ID-ETO.htm | https://web.archive.org/web/2018/http://www.history.army.mil/documents/ETO-OB/83ID-ETO.htm | https://en.wikipedia.org/wiki/VIII_Corps_(United_States) ; coords: Wikipedia (en): Brest, France
- **notes**: Event date: CMH ETO-OB assignment tables for the 8th and 83rd Divisions and Wikipedia date VIII Corps to Ninth Army from 5 September. Event definition: the assignment-table date, the day Ninth Army became operational and (per Pogue, Supreme Command ch. 15) took over the Brittany forces; the Green Book places the actual passing of VIII Corps to Ninth Army control on 10 September (preferred row). Relationship: the tables do not distinguish assigned from attached (unspecified_subordination). Location: the Brest sector; the corps headquarters is not located. Batch 2: the corps command post was at Lesneven from 18 August (C0499, Breakout-30 p638); no source places it elsewhere before 24 September (CMH list: St Aubin), but the headquarters is not documented on this date, so the Brest-sector point is kept.

## 6. C0317 — VIII Corps (1944-09-18)

_Why picked: conflict G014 (preferred): fall of Brest, 18 Sep (Green Book) vs 19 Sep (C0318)._

- **nationality**: US
- **echelon**: corps
- **parent_formation**: Ninth Army (US-ARMY-009A)
- **command_relationships**: [{"unit_id":"US-ARMY-009A","name":"US Ninth Army","relationship":"operational_control","effective_from":"1944-09-10","date_basis":"narrative","note":"Breakout-30 p636"}]
- **commander**: Major General Troy H. Middleton
- **latitude**: 48.3906
- **longitude**: -4.4861
- **location_name**: Brest, Finistère
- **location_represents**: objective
- **precision_km**: 3
- **confidence**: 0.7
- **campaign**: Rhineland
- **operation_name**: 
- **sub_operation_name**: Brest
- **composing_units**: 
- **event_type**: capture
- **current_activity**: receiving the capitulation of German forces in eastern Brest and Recouvrance
- **engaged_with**: German 2nd Fallschirmjäger Division
- **strength_status**: unknown
- **strength_json**: 
- **conflict_group_id**: G014
- **claim_status**: preferred
- **location_date**: 1944-09-18
- **location_basis**: documented_on_date
- **location_temporal_offset_days**: 0
- **source**: https://www.ibiblio.org/hyperwar/USA/USA-E-Breakout/USA-E-Breakout-30.html#page650 ; coords: Wikipedia (en): Brest, France
- **notes**: Event date: Breakout-30 p650: both German capitulations at Brest occurred on 18 September (Recouvrance to the 29th Division, the east of the city to the 2nd Division); the garrison commanders were von der Mosel (29th Division sector) and Pietzonka (2nd Division sector). Event definition: surrender of the German forces holding Brest and Recouvrance. Ramcke, the fortress commander, had escaped to the Crozon peninsula and surrendered there on 19 September (see the alternate row), so the garrison did not surrender in a single act. Relationship: Ninth Army (VIII Corps passed to it on 10 September).

## 7. C0333 — XIX Corps (1944-08-29)

_Why picked: attachment: XIX Corps takes command of 79th, 30th and 2nd Armored in the Mantes bridgehead._

- **nationality**: US
- **echelon**: corps
- **parent_formation**: First Army (US-ARMY-001A)
- **command_relationships**: [{"unit_id":"US-ARMY-001A","name":"US First Army","relationship":"assigned"}]
- **commander**: Major General Charles H. Corlett
- **latitude**: 48.9908
- **longitude**: 1.7172
- **location_name**: Mantes-Gassicourt bridgehead area (Seine), Yvelines
- **location_represents**: sector_center
- **precision_km**: 10
- **confidence**: 0.5
- **campaign**: Northern France
- **operation_name**: Overlord
- **sub_operation_name**: Pursuit
- **composing_units**: 79th Infantry Division; 30th Infantry Division; 2nd Armored Division
- **event_type**: command_change
- **current_activity**: taking command of 79th, 30th and 2nd Armored Divisions in the Mantes bridgehead
- **engaged_with**: 
- **strength_status**: unknown
- **strength_json**: 
- **conflict_group_id**: 
- **claim_status**: preferred
- **location_date**: 1944-08-29
- **location_basis**: operational_area
- **location_temporal_offset_days**: 0
- **source**: https://www.ibiblio.org/hyperwar/USA/USA-E-Breakout/USA-E-Breakout-31.html#page671 | https://www.ibiblio.org/hyperwar/USA/USA-E-Breakout/USA-E-Breakout-31.html#page672 ; coords: Wikipedia (en): Mantes-la-Jolie
- **notes**: Event date: Breakout-31 p672: at noon on 29 August, as XV Corps headquarters started for an assembly area southeast of Paris, Corlett's XIX Corps took command of the three divisions east of the Seine and moved 2nd Armored Division to the lead. Event definition: XIX Corps takes command of the 79th, 30th and 2nd Armored Divisions, all effective 29 August (the divisions' own rows carry the matching corps entries). Location: the bridgehead area is the corps sector, not the corps command post, which is not located in the sources used (the earlier point was a front-line point at Mantes). Relationship: XIX Corps assigned to First Army. Batch 2: the corps command post that day was at Les Mureaux (C0496, CMH list via World War II by Day); this row keeps the bridgehead sector because the event is the takeover of the three divisions. The 2nd Armored sequence under XIX / XV / XIX Corps (19, 28, 29 August) is modelled in C0229 and the new rows C0509-C0511; the table date 19 August and the narrative date 29 August describe different events, not one. Batch 2 review: the XV Corps command of the 2nd Armored on 28 August is temporary operational control (C0510).

## 8. C0213 — XVIII Airborne Corps (1944-08-25)

_Why picked: newly active corps: XVIII Airborne Corps redesignation, England._

- **nationality**: US
- **echelon**: corps
- **parent_formation**: First Allied Airborne Army (ALL-FAAA-001A)
- **command_relationships**: [{"unit_id":"ALL-FAAA-001A","name":"First Allied Airborne Army","relationship":"unspecified_subordination","date_basis":"assignment_table","note":"CMH ETO-OB tables show XVIII Airborne Corps under First Allied Airborne Army"}]
- **commander**: Major General Matthew B. Ridgway
- **latitude**: 51.4680
- **longitude**: -1.7130
- **location_name**: Ogbourne St George, Wiltshire
- **location_represents**: headquarters
- **precision_km**: 5
- **confidence**: 0.7
- **campaign**: Northern France
- **operation_name**: Overlord
- **sub_operation_name**: Market Garden preparations
- **composing_units**: 82nd Airborne Division; 101st Airborne Division
- **event_type**: redesignation
- **current_activity**: redesignated XVIII Airborne Corps at Ogbourne St George with the 82nd and 101st Airborne Divisions
- **engaged_with**: 
- **strength_status**: unknown
- **strength_json**: 
- **conflict_group_id**: 
- **claim_status**: preferred
- **location_date**: 1944-08-25
- **location_basis**: town_centroid
- **location_temporal_offset_days**: 0
- **source**: https://en.wikipedia.org/wiki/XVIII_Airborne_Corps | https://web.archive.org/web/2018/http://www.history.army.mil/documents/ETO-OB/82ABD-ETO.htm | https://web.archive.org/web/2018/http://www.history.army.mil/documents/ETO-OB/101ABN-ETO.htm ; coords: Wikipedia (en): Ogbourne St George
- **notes**: Event date: Wikipedia: XVIII Corps deployed to Europe on 17 August and became XVIII Airborne Corps on 25 August 1944 at Ogbourne St George (assuming command of the 82nd and 101st Airborne Divisions). Event definition: redesignation of the same headquarters (II Armored Corps, 1942; XVIII Corps, 9 October 1943; XVIII Airborne Corps, 25 August 1944; see units.csv note). Relationship: the CMH tables assign the 82nd and 101st Airborne Divisions to the corps from 12 August, when it was still the XVIII Corps and still in the United States; it is not an airborne corps headquarters in Europe before 25 August. The corps was assigned to First Allied Airborne Army (CMH tables, not distinguished as assigned or attached). It was in England during Market Garden, where British I Airborne Corps held operational control of the US airborne divisions.

## 9. C0217 — 82nd Airborne Division (1944-09-17)

_Why picked: airborne landing, Market Garden: 82nd Airborne._

- **nationality**: US
- **echelon**: division
- **parent_formation**: I Airborne Corps (UK-ABN-001C)
- **command_relationships**: [{"unit_id":"US-ABN-018C","name":"US XVIII Airborne Corps","relationship":"assigned","effective_from":"1944-08-12","effective_to":"1944-09-17","date_basis":"assignment_table","note":"XVIII Airborne Corps headquarters stayed in England during Market Garden"},{"unit_id":"ALL-FAAA-001A","name":"First Allied Airborne Army","relationship":"assigned","effective_from":"1944-08-12","note":"CMH ETO-OB assignment table, Army Assigned column: \"First Allied Abn\"","date_basis":"assignment_table"},{"unit_id":"UK-ABN-001C","name":"British I Airborne Corps","relationship":"operational_control","effective_from":"1944-09-17","date_basis":"assignment_table","note":"CMH ETO-OB table; Market Garden plan placed the US airborne divisions under British I Airborne Corps"},{"unit_id":"UK-AG-021G","name":"British 21st Army Group","relationship":"attached","effective_from":"1944-09-17","note":"CMH ETO-OB assignment table, Army Group Attached column: \"Br 21st\"","date_basis":"assignment_table"}]
- **commander**: Brigadier General James M. Gavin
- **latitude**: 51.7741
- **longitude**: 5.9305
- **location_name**: Drop zones around Groesbeek (DZ N south of Groesbeek), Gelderland, Netherlands
- **location_represents**: sector_center
- **precision_km**: 10
- **confidence**: 0.5
- **campaign**: Rhineland
- **operation_name**: Market Garden
- **sub_operation_name**: Market Garden
- **composing_units**: attached: British 2nd Irish Guards (Guards Armoured Division) from 16 September
- **event_type**: landing
- **current_activity**: parachute and glider landing on drop zones around Groesbeek (Market Garden)
- **engaged_with**: 
- **strength_status**: unknown
- **strength_json**: 
- **conflict_group_id**: 
- **claim_status**: preferred
- **location_date**: 1944-09-17
- **location_basis**: operational_area
- **location_temporal_offset_days**: 0
- **source**: https://web.archive.org/web/2018/http://www.history.army.mil/documents/ETO-OB/82ABD-ETO.htm | https://www.tracesofwar.com/sights/155485/Champion-CP.htm | http://cgsc.contentdm.oclc.org/u?/p4013coll8,387 ; coords: OpenStreetMap Nominatim (Groesbeek, Gelderland)
- **notes**: Event date: 17 September 1944; the 82nd's parachute lift dropped 12:50–14:00, the division headquarters party jumped about 13:06 and the gliders landed about 13:50 on DZ N south of Groesbeek (TracesOfWar; 82nd Airborne Division, Operation Market historical data). Event definition: the airborne landing. The division command post (CHAMPION, about 1,000 yards west of Groesbeek, set up about 17:00) is a separate row (hq_move). Location: the point is the Groesbeek landing area (OpenStreetMap Nominatim, Groesbeek centroid), not the CMH command-post vicinity of Nijmegen that this row used before. Relationship: for Market Garden British I Airborne Corps held operational control of the 82nd and 101st Airborne Divisions; the CMH table shows the division as under I Airborne Corps from 17 September. XVIII Airborne Corps (assigned from 12 August, ended 17 September per Wikipedia) stayed in England. First Allied Airborne Army was the higher Allied command over both corps.

## 10. C0243 — 4th Armored Division (1944-07-11)

_Why picked: conflict G012 (alternate, 0.3): 4th Armored landing date 11 Jul (Wikipedia) vs 13 Jul (CMH)._

- **nationality**: US
- **echelon**: division
- **parent_formation**: XV Corps (US-COR-015C)
- **command_relationships**: [{"unit_id":"US-COR-015C","name":"US XV Corps","relationship":"unspecified_subordination","effective_from":"1944-04-20","note":"CMH ETO-OB assignment table (single corps column; the table does not say assigned or attached for corps)","date_basis":"assignment_table"},{"unit_id":"US-ARMY-003A","name":"US Third Army","relationship":"assigned","effective_from":"1944-04-20","note":"CMH ETO-OB assignment table, Army Assigned column: \"Third\"","date_basis":"assignment_table"}]
- **commander**: Major General John Wood
- **latitude**: 49.4157
- **longitude**: -1.1747
- **location_name**: Utah Beach, Manche (landing area)
- **location_represents**: sector_center
- **precision_km**: 5
- **confidence**: 0.5
- **campaign**: Normandy
- **operation_name**: Overlord
- **sub_operation_name**: 
- **composing_units**: 
- **event_type**: landing
- **current_activity**: landing at Utah Beach
- **engaged_with**: 
- **strength_status**: unknown
- **strength_json**: 
- **conflict_group_id**: G012
- **claim_status**: alternate
- **location_date**: 1944-07-11
- **location_basis**: operational_area
- **location_temporal_offset_days**: 0
- **source**: https://en.wikipedia.org/wiki/4th_Armored_Division_(United_States) | https://encyclopedia.ushmm.org/content/en/article/the-4th-armored-division ; coords: OpenStreetMap Nominatim (Utah Beach, Sainte-Marie-du-Mont)
- **notes**: Event date: USHMM and Wikipedia: the 4th Armored Division landed at Utah Beach on 11 July 1944. Event definition: the first landing of the division at Utah Beach. The 13 July row (preferred) is the CMH ETO-OB chronology date for arrival on the Continent, with the division command post at Mesnil-St-Martin on that date; the two may describe different phases (first elements ashore, main body ashore, command post established) rather than a disagreement. A reviewer said the 704th Tank Destroyer Battalion boarded 11 July and landed 12 July; that was not confirmed (tankdestroyer.net, citing Yeide, has the battalion landing on 13 July). Location: Utah Beach area (OpenStreetMap Nominatim); the Mesnil-St-Martin command post this row reused belongs to the 13 July row only.

## 11. C0457 — 80th Infantry Division (1944-08-03)

_Why picked: new arrival: 80th Division, CP-derived location, 0.5 / 10 km._

- **nationality**: US
- **echelon**: division
- **parent_formation**: XII Corps (US-COR-012C)
- **command_relationships**: [{"unit_id":"US-COR-012C","name":"US XII Corps","relationship":"unspecified_subordination","effective_from":"1944-08-01","note":"CMH ETO-OB assignment table (single corps column; the table does not say assigned or attached for corps)","date_basis":"assignment_table"},{"unit_id":"US-ARMY-003A","name":"US Third Army","relationship":"assigned","effective_from":"1944-08-01","note":"CMH ETO-OB assignment table, Army Assigned column: \"Third\"","date_basis":"assignment_table"},{"unit_id":"US-AG-012G","name":"US 12th Army Group","relationship":"assigned","effective_from":"1944-08-01","note":"CMH ETO-OB assignment table, Army Group Assigned column: \"12th\"","date_basis":"assignment_table"}]
- **commander**: Major General Horace L. McBride
- **latitude**: 49.3044
- **longitude**: -1.4051
- **location_name**: vicinity of St-Jores, Manche
- **location_represents**: headquarters
- **precision_km**: 10
- **confidence**: 0.5
- **campaign**: Northern France
- **operation_name**: Overlord
- **sub_operation_name**: 
- **composing_units**: 
- **event_type**: arrival
- **current_activity**: arriving on the Continent
- **engaged_with**: 
- **strength_status**: unknown
- **strength_json**: 
- **conflict_group_id**: 
- **claim_status**: preferred
- **location_date**: 1944-08-03
- **location_basis**: town_centroid
- **location_temporal_offset_days**: 0
- **source**: https://web.archive.org/web/2018/http://www.history.army.mil/documents/ETO-OB/80ID-ETO.htm ; coords: OpenStreetMap Nominatim (Saint-Jores, Manche, France)
- **notes**: Event date: CMH ETO-OB chronology: arrived on the Continent 3 August 1944. Event definition: arrival of the division. Location: CMH lists the command post at the vicinity of St-Jores, Manche on this date; CMH gives the CP only as a vicinity of the town. Relationship: the CMH assignment table shows XII Corps from 1 August and Third Army without distinguishing assigned from attached (both unspecified_subordination); Third Army is a higher command, not an organic parent.

## 12. C0479 — 94th Infantry Division (1944-09-05)

_Why picked: new arrival, lowest-confidence class: 94th Division, 0.3 / 25 km (nearest CP is more than 3 days away)._

- **nationality**: US
- **echelon**: division
- **parent_formation**: XIII Corps (US-COR-013C)
- **command_relationships**: [{"unit_id":"US-COR-013C","name":"US XIII Corps","relationship":"unspecified_subordination","effective_from":"1944-08-28","note":"CMH ETO-OB assignment table (single corps column; the table does not say assigned or attached for corps)","date_basis":"assignment_table"},{"unit_id":"US-ARMY-009A","name":"US Ninth Army","relationship":"assigned","effective_from":"1944-08-28","note":"CMH ETO-OB assignment table, Army Assigned column: \"Ninth\"","date_basis":"assignment_table"},{"unit_id":"US-AG-012G","name":"US 12th Army Group","relationship":"assigned","effective_from":"1944-08-28","note":"CMH ETO-OB assignment table, Army Group Assigned column: \"12th\"","date_basis":"assignment_table"}]
- **commander**: Major General Harry J. Malony
- **latitude**: 49.3788
- **longitude**: -1.2255
- **location_name**: Ste-Marie-du-Mont, Manche
- **location_represents**: headquarters
- **precision_km**: 25
- **confidence**: 0.3
- **campaign**: Northern France
- **operation_name**: 
- **sub_operation_name**: 
- **composing_units**: 
- **event_type**: arrival
- **current_activity**: arriving on the Continent
- **engaged_with**: 
- **strength_status**: unknown
- **strength_json**: 
- **conflict_group_id**: 
- **claim_status**: preferred
- **location_date**: 1944-09-08
- **location_basis**: nearest_later_command_post
- **location_temporal_offset_days**: 3
- **source**: https://web.archive.org/web/2018/http://www.history.army.mil/documents/ETO-OB/94ID-ETO.htm ; coords: OpenStreetMap Nominatim (Sainte-Marie-du-Mont, Manche, France)
- **notes**: Event date: CMH ETO-OB chronology: arrived on the Continent 5 September 1944. Location: the coordinate is the CP at Ste-Marie-du-Mont listed by CMH three days later (8 September), not the position on 5 September, which is not stated. Context: the division took over the containment of the Lorient and Saint-Nazaire pockets in mid-September (Breakout-30 p637), after this staging period. Relationship: the CMH table does not distinguish assigned from attached.

## 13. C0388 — 26th Infantry Division (1944-09-07)

_Why picked: new arrival with a judgment call: 26th Division dated 7 Sep from the Valognes CP; the Continent date in CMH is 19 Sep._

- **nationality**: US
- **echelon**: division
- **parent_formation**: III Corps (US-COR-003C)
- **command_relationships**: [{"unit_id":"US-COR-003C","name":"US III Corps","relationship":"unspecified_subordination","effective_from":"1944-09-05","note":"CMH ETO-OB assignment table (single corps column; the table does not say assigned or attached for corps)","date_basis":"assignment_table"},{"unit_id":"US-ARMY-009A","name":"US Ninth Army","relationship":"assigned","effective_from":"1944-09-05","note":"CMH ETO-OB assignment table, Army Assigned column: \"Ninth\"","date_basis":"assignment_table"},{"unit_id":"US-AG-012G","name":"US 12th Army Group","relationship":"assigned","effective_from":"1944-09-05","note":"CMH ETO-OB assignment table, Army Group Assigned column: \"12th\"","date_basis":"assignment_table"}]
- **commander**: Major General Willard S. Paul
- **latitude**: 49.5091
- **longitude**: -1.4706
- **location_name**: Valognes Staging Area, Manche
- **location_represents**: headquarters
- **precision_km**: 5
- **confidence**: 0.7
- **campaign**: Northern France
- **operation_name**: 
- **sub_operation_name**: 
- **composing_units**: 
- **event_type**: arrival
- **current_activity**: arriving on the Continent
- **engaged_with**: 
- **strength_status**: unknown
- **strength_json**: 
- **conflict_group_id**: 
- **claim_status**: preferred
- **location_date**: 1944-09-07
- **location_basis**: town_centroid
- **location_temporal_offset_days**: 0
- **source**: https://web.archive.org/web/2018/http://www.history.army.mil/documents/ETO-OB/26ID-ETO.htm | https://eucmh.com/2020/03/27/26-id-yankee-ww-2-eto/ ; coords: OpenStreetMap Nominatim (Valognes, Manche, France)
- **notes**: Event date: 7 September 1944 is kept: the CMH command and staff table dates every command appointment to 7 September, CMH lists the CP at the Valognes staging area on that date, and the division history (EUCMH, from the division record) says the division landed at Cherbourg and Utah Beach on 7 September as the first convoy direct from the United States. The CMH chronology table gives "Arrived Continent (D+105)", 19 September 1944 (D+105 is 19 September, so the figure is internally consistent): it appears to be a separate CMH event definition, probably the date the division closed in the staging area, and is not corroborated elsewhere. Location: Valognes is the CMH-listed staging area; the commune centroid is used. The EUCMH history says the division established its headquarters at Bourg de Lestre in the staging area, so the headquarters may have been a few kilometres east of Valognes. The staging-area coordinates are not independently verified. Relationship: the CMH table does not distinguish assigned from attached.

## 14. C0406 — 29th Infantry Division (1944-08-19)

_Why picked: attachment row, 0.3: 29th Division to VIII Corps control during the Brest operation._

- **nationality**: US
- **echelon**: division
- **parent_formation**: VIII Corps (US-COR-008C)
- **command_relationships**: [{"unit_id":"US-COR-008C","name":"US VIII Corps","relationship":"unspecified_subordination","effective_from":"1944-08-19","note":"CMH ETO-OB assignment table (single corps column; the table does not say assigned or attached for corps)","date_basis":"assignment_table"},{"unit_id":"US-ARMY-001A","name":"US First Army","relationship":"assigned","effective_from":"1944-08-19","note":"CMH ETO-OB assignment table, Army Assigned column: \"First\"","date_basis":"assignment_table"},{"unit_id":"US-ARMY-003A","name":"US Third Army","relationship":"attached","effective_from":"1944-08-19","note":"CMH ETO-OB assignment table, Army Attached column: \"Third\"","date_basis":"assignment_table"},{"unit_id":"US-AG-012G","name":"US 12th Army Group","relationship":"assigned","effective_from":"1944-08-19","note":"CMH ETO-OB assignment table, Army Group Assigned column: \"12th\"","date_basis":"assignment_table"}]
- **commander**: Major General Charles H. Gerhardt
- **latitude**: 48.5253
- **longitude**: -4.5977
- **location_name**: Plouguin, Finistere
- **location_represents**: headquarters
- **precision_km**: 25
- **confidence**: 0.3
- **campaign**: Northern France
- **operation_name**: Overlord
- **sub_operation_name**: 
- **composing_units**: 
- **event_type**: command_change
- **current_activity**: passing to VIII Corps control
- **engaged_with**: 
- **strength_status**: unknown
- **strength_json**: 
- **conflict_group_id**: 
- **claim_status**: preferred
- **location_date**: 1944-08-22
- **location_basis**: nearest_later_command_post
- **location_temporal_offset_days**: 3
- **source**: https://web.archive.org/web/2018/http://www.history.army.mil/documents/ETO-OB/29ID-ETO.htm ; coords: OpenStreetMap Nominatim (Plouguin, Finistere, France)
- **notes**: Event date: CMH ETO-OB assignment table entry dated 19 August 1944 (division passes to VIII Corps). Location: the coordinate is the CP at Plouguin listed by CMH three days later (22 August); the division position on 19 August is not stated. Breakout-30 says the 29th Division assembled just south of Lannilis four days after 19 August (23 August), about 9 km from Plouguin. Plouguin is kept as a low-confidence point; the attachment to VIII Corps is supported separately by the CMH table. Relationship: the CMH table does not distinguish assigned from attached.

## 15. C0300 — VI Corps (1944-08-15)

_Why picked: Dragoon landing: VI Corps, theater western_europe from 15 Aug._

- **nationality**: US
- **echelon**: corps
- **parent_formation**: Seventh Army (US-ARMY-007A)
- **command_relationships**: [{"unit_id":"US-ARMY-007A","name":"US Seventh Army","relationship":"assigned"}]
- **commander**: Major General Lucian K. Truscott Jr.
- **latitude**: 43.2733
- **longitude**: 6.6396
- **location_name**: Dragoon assault area (Alpha, Delta and Camel sectors), Var coast
- **location_represents**: sector_center
- **precision_km**: 25
- **confidence**: 0.5
- **campaign**: Southern France
- **operation_name**: Dragoon
- **sub_operation_name**: 
- **composing_units**: 
- **event_type**: landing
- **current_activity**: assaulting the Riviera with 3rd, 36th and 45th Divisions
- **engaged_with**: 
- **strength_status**: unknown
- **strength_json**: 
- **conflict_group_id**: 
- **claim_status**: preferred
- **location_date**: 1944-08-15
- **location_basis**: operational_area
- **location_temporal_offset_days**: 0
- **source**: https://www.ibiblio.org/hyperwar/USA/USA-E-Riviera/USA-E-Riviera-5.html#page75 | https://www.ibiblio.org/hyperwar/USA/USA-E-Riviera/USA-E-Riviera-7.html | https://en.wikipedia.org/wiki/VI_Corps_(United_States) | https://en.wikipedia.org/wiki/Operation_Dragoon ; coords: Wikipedia (en): Saint-Tropez
- **notes**: Event date: 15 August 1944 (Riviera-5 p75–78). Event definition: the VI Corps assault with three divisions in three sectors: 3rd Division on the Alpha beaches (Cavalaire Bay), 45th Division on the Delta beaches (Bougnon Bay), 36th Division on the Camel beaches east of Saint-Raphaël; the 36th avoided Camel Red and landed on Camel Green and Blue (Wikipedia, Operation Dragoon). The division landings have their own rows (C0351, C0442, C0436). Location: the point is the centre of the whole assault area at Cape Saint-Tropez (a broad operational-area point; the corps headquarters afloat is not a land position). The NHHC page named in review did not return the sector names to this check, so the sector assignments rest on the Green Book rows and Wikipedia.
