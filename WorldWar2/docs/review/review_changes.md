# Spot-check review: verification and changes

Scope: the five rows named in the available part of the review of `spot_check_15.md` (the excerpt starts and ends mid-document, so for C0057, C0184 and C0141 only the headings were available, and for C0084 only the first sentence). Each point was checked independently against the sources below; a row was changed only where the sources support it. All edits are in `data/claims/**` (claim_ids unchanged); `build/` was regenerated, `validate.py`, `build.py` and `build.py --check` pass.

Summary:

| row | reviewer's point | verdict | what changed |
|---|---|---|---|
| C0001 2nd Canadian Armoured Brigade, 6 Jun | not an organic part of 3rd Canadian Infantry Division | agree | organic parent is now Second Army, 3rd Canadian Division is the attached operational parent, activity reworded, confidence 0.5 to 0.7 |
| C0084 I Corps, 12 Jun | "attacking from the Orne bridgehead" | partly agree: the corps attack did start on 12 June, but the wording was misleading | activity, engaged_with, location_name, notes |
| C0057 352nd Infantry Division, 9 Jun | strength interpretation and line location | agree on both | coordinate moved to the line midpoint, precision 5 to 10 km, strength note rewritten |
| C0184 21st Panzer Division, 28 Jun | opposing unit and aggregation of combat activity | agree on the opponent; not split | engaged_with, activity, notes, confidence 0.5 to 0.7 |
| C0141 82nd Airborne Division, 19 Jun | event date versus VIII Corps attachment date | VIII Corps is correct for 19 June; relationship type refined | VIII Corps entry organic to attached, notes |

---

## C0001: 2nd Canadian Armoured Brigade (1944-06-06)

**Reviewer's point.** The brigade supported the 3rd Canadian Infantry Division on Juno Beach but should not be modelled as its organic subordinate; separate the organisational parent (an independent brigade at a higher headquarters), the tactical relationship (attached to or supporting the 3rd Division) and the activity ("providing armoured support during the Juno landings").

**What the sources say.**
- Wikipedia, [2nd Canadian Armoured Brigade](https://en.wikipedia.org/wiki/2nd_Canadian_Armoured_Brigade): "(Independent)"; "assigned to the British 2nd Army in January 1944 to train for the upcoming amphibious assault"; selected in 1943 "to be part of the D-Day invasion force in support of the units of the 3rd Canadian Infantry Division"; "its primary role was infantry support and thus its regiments were usually individually tasked out to infantry units"; infobox "Part of: First Canadian Army, British Second Army".
- Wikipedia, [List of Allied forces in the Normandy campaign](https://en.wikipedia.org/wiki/List_of_Allied_forces_in_the_Normandy_campaign): lists it under "Independent and GHQ brigades".
- Wikipedia, [Normandy landings](https://en.wikipedia.org/wiki/Normandy_landings): "The 3rd Canadian Infantry Division, with the 2nd Canadian Armoured Brigade under command, landed in two brigade groups".
- Veterans Affairs Canada, [D-Day and the Battle of Normandy](https://www.veterans.gc.ca/en/remembrance/military-history/second-world-war/d-day-and-battle-normandy): "The invasion commanders designated the 3rd Canadian Infantry Division ... along with the 2nd Canadian Armoured Brigade, to take part in the seaborne assault."
- Juno Beach Centre, [D-Day](https://www.junobeach.org/canada-in-wwii/articles/d-day/): the 3rd Division "was under command of the Second British Army".
- Wikipedia, [First Canadian Army](https://en.wikipedia.org/wiki/First_Canadian_Army): the division and the brigade were "detached to British I Corps" for the assault; the army headquarters became operational in Normandy on 23 July 1944.

**Decision.** The reviewer is right: the brigade was independent (army-level), under the division's command for the assault only. The sources do not agree on the standing parent: the brigade's own page says Second Army, the First Canadian Army page implies First Canadian Army detached it to I Corps. I used Second Army (stated directly for the brigade, already in `units.csv`, and the Canadian army headquarters was not in Normandy on 6 June) and said so in the relationship note and in `notes`; no new unit was needed. `parent_unit_id` stays the 3rd Canadian Division because that is the operational parent on the row's date; its relationship is now `attached`. Confidence went from 0.5 to 0.7 by the existing rubric (approximate location, two source families: Wikipedia and Veterans Affairs Canada); this can be reverted if you would rather not re-score on a command-only correction. Not changed: `composing_units` (still `unknown`; Wikipedia's order of battle lists three armoured regiments and a squadron, which could be added later), `units.csv`.

**Before and after.**

**`command_relationships`**

- before: `[{"unit_id":"CAN-INF-003D","name":"Canadian 3rd Canadian Infantry Division","relationship":"organic"}]`
- after: `[{"unit_id":"UK-ARMY-002A","name":"British Second Army","relationship":"assigned","note":"Independent (army-level) armoured brigade, assigned to Second Army in January 1944 (Wikipedia); First Canadian Army was not operational in Normandy until 23 July"},{"unit_id":"CAN-INF-003D","name":"Canadian 3rd Canadian Infantry Division","relationship":"attached","effective_from":"1944-06-06","note":"Under command of the 3rd Canadian Infantry Division for the Juno assault"}]`

**`confidence`**

- before: `0.5`
- after: `0.7`

**`source`**

- before: `https://en.wikipedia.org/wiki/List_of_Allied_forces_in_the_Normandy_campaign | https://en.wikipedia.org/wiki/Operation_Perch ; coords: Wikipedia`
- after: `https://en.wikipedia.org/wiki/List_of_Allied_forces_in_the_Normandy_campaign | https://en.wikipedia.org/wiki/2nd_Canadian_Armoured_Brigade | https://en.wikipedia.org/wiki/Normandy_landings | https://www.veterans.gc.ca/en/remembrance/military-history/second-world-war/d-day-and-battle-normandy | https://en.wikipedia.org/wiki/Operation_Perch ; coords: Wikipedia`

**`current_activity`**

- before: `landing at Juno Beach in support of 3rd Canadian Division`
- after: `providing armoured support during the Juno landings`

**`notes`**

- before: `Brigade-level (below stated scope; included for context). Supported 3rd Canadian Division at Juno; 1st Hussars attacked Le Mesnil-Patry 11 June.`
- after: `Brigade-level (below stated scope; included for context). An independent armoured brigade, not an organic part of the 3rd Canadian Division: Wikipedia lists it among the independent brigades and says it was assigned to British Second Army in January 1944, and it landed on 6 June with the 3rd Canadian Infantry Division, under its command for the assault (Wikipedia; Veterans Affairs Canada names the division and the brigade together as the designated assault formations). Its regiments were usually tasked individually to infantry units. 1st Hussars attacked Le Mesnil-Patry 11 June. [Review: parent_unit_id stays the 3rd Canadian Division (operational parent, now relationship attached); organic parent is now Second Army (was the 3rd Canadian Division); current_activity reworded from 'landing at Juno Beach in support of 3rd Canadian Division'; confidence raised from 0.5 to 0.7 by the rubric (approximate location, two source families: Wikipedia and Veterans Affairs Canada). Wikipedia's First Canadian Army page says the division and brigade were detached from that army to British I Corps for the assault; that standing link is not modelled because the army was not in Normandy on this date.]`


---

## C0084: I Corps (1944-06-12)

**Reviewer's point (excerpt, cut off after this sentence).** "The current record says I Corps was attacking from the Orne bridgehead on June 12."

**What the sources say.**
- Wikipedia, [Operation Perch](https://en.wikipedia.org/wiki/Operation_Perch) (citing Ellis, *Victory in the West*, pp. 247-250, and Stacey): on 9 June I Corps (51st Highland Division and 4th Armoured Brigade) was to cross into the 6th Airborne Division's Orne bridgehead and attack toward Cagny; the attack "was postponed until 12 June, because of weather delays" that slowed the landing of the 51st Division and 4th Armoured Brigade; on 10 June German attacks on the 6th Airborne Division in the bridgehead "forestalled the British attack"; on 12 June "German attacks were launched from the Bréville area against the Orne bridgehead", fighting lasted all day, the Germans pulled back in the evening, and 12th Parachute Battalion captured Bréville by midnight; "the 51st Highland Division was opposed by the 21st Panzer Division in its efforts to push south to Saint Honorine and with the Highlanders contained, the offensive east of Caen was called off on 13 June". The same page's lead says I Corps "began the eastern thrust two days later from the Orne bridgehead".
- Wikipedia, [Battle of Bréville](https://en.wikipedia.org/wiki/Battle_of_Br%C3%A9ville): fought 7/8-13 June between the 6th Airborne Division and the German 346th Infantry Division; the 12 June German attack fell on the 3rd Parachute Brigade; the night attack took Bréville.
- Wikipedia, [51st (Highland) Infantry Division](https://en.wikipedia.org/wiki/51st_(Highland)_Infantry_Division): part of I Corps, sent across the Orne to support the 6th Airborne Division in its bridgehead; Bréville (11-12 June).
- Wikipedia, [I Corps (United Kingdom)](https://en.wikipedia.org/wiki/I_Corps_(United_Kingdom)): corps order of battle (3rd Infantry, 3rd Canadian and 6th Airborne Divisions on 6 June; 51st Highland added later).

**Decision.** Partly agree. It is true that the corps' postponed attack began on 12 June, but "attacking from the Orne bridgehead; held by 21st Panzer" overstates it: the attack was a limited effort by the 51st Division that was contained, the bridgehead itself was under heavy German attack that day (346th Infantry Division as well as 21st Panzer), the main gain was the 6th Airborne Division's night capture of Bréville, and the fighting was done by divisions rather than the corps headquarters. I reworded `current_activity` and `notes` accordingly, added the 346th Infantry Division to `engaged_with`, and made the point convention explicit in `location_name`. Event type stays `attack`, since the corps' offensive did start that day; coordinates, precision (10 km, a bridgehead-wide point), parent and confidence (0.5, one source family) are unchanged. Since the pasted review is cut off, I cannot tell whether the reviewer objected to something I did not address.

**Before and after.**

**`command_relationships`**

- before: `[{"unit_id":"UK-ARMY-002A","name":"British Second Army","relationship":"organic"}]`
- after: `[{"unit_id":"UK-ARMY-002A","name":"British Second Army","relationship":"assigned"}]`

**`location_name`**

- before: `Orne bridgehead / east of Caen`
- after: `Orne bridgehead / east of Caen (point = Bréville-les-Monts)`

**`source`**

- before: `https://en.wikipedia.org/wiki/Operation_Perch ; coords: Wikipedia`
- after: `https://en.wikipedia.org/wiki/Operation_Perch | https://en.wikipedia.org/wiki/Battle_of_Br%C3%A9ville | https://en.wikipedia.org/wiki/51st_(Highland)_Infantry_Division ; coords: Wikipedia`

**`current_activity`**

- before: `attacking from Orne bridgehead; held by 21st Panzer`
- after: `delayed 51st Highland Division attack from the Orne bridgehead, contained by 21st Panzer; bridgehead also under attack`

**`engaged_with`**

- before: `German 21st Panzer Division`
- after: `German 21st Panzer Division; German 346th Infantry Division`

**`notes`**

- before: `I Corps attack from the Orne bridgehead was postponed to 12 June by delays landing 51st Division and 4th Armoured Brigade; called off 13 June against 21st Panzer Division.`
- after: `I Corps' planned eastern thrust (51st (Highland) Division and 4th Armoured Brigade crossing into the 6th Airborne Division's Orne bridgehead, toward Cagny south-east of Caen) was postponed to 12 June because bad weather delayed the landing of the 51st Division and 4th Armoured Brigade (Wikipedia, Operation Perch, citing Ellis). The corps' own attack on 12 June was limited: the bridgehead was itself attacked all day from the Bréville area (346th Infantry Division per the Battle of Bréville page; the 21st Panzer Division was also opposing from the south), the Germans pulled back in the evening, and 12th Parachute Battalion and a Devonshire company captured Bréville that night. The 51st Division, opposed by 21st Panzer in its push south toward Sainte-Honorine, was contained, and the offensive east of Caen was called off on 13 June. The fighting was done by divisions (51st Highland, 6th Airborne), not by the corps headquarters; the point is a representative bridgehead point (Bréville-les-Monts commune coordinates), not the corps HQ. [Review: current_activity was 'attacking from Orne bridgehead; held by 21st Panzer' and notes did not say the bridgehead was under German attack; engaged_with added the 346th Infantry Division; location_name now states the point convention. Event type, coordinates, precision and confidence unchanged.]`


---

## C0057: 352nd Infantry Division (1944-06-09)

**Reviewer's point (heading only in the excerpt):** strength interpretation and line location.

**What the sources say.**
- CMH, [Cross-Channel Attack, ch. IX](https://www.ibiblio.org/hyperwar/USA/USA-E-XChannel/USA-E-XChannel-9.html): "At about 1900, 9 June, General Kraiss reported his hopeless situation to General Marcks at LXXXIV Corps and received orders to withdraw far to the south to establish a defense along the Elle River from Berigny to Airel. The withdrawal was to take place during darkness and to be completed by 0600, 10 June. For the defense of this new line of about ten miles, General Kraiss had 2,500 men, 14 artillery pieces, 16 antiaircraft guns, and 5 tanks." CMH also says that on 16-17 June the division was "already only a Kampfgruppe of about regimental strength".
- Wikipedia, [352nd Infantry Division (Germany)](https://en.wikipedia.org/wiki/352nd_Infantry_Division_(Germany)): about 17,200 at full strength on the old-type establishment (excluding the attached fusilier battalion); "the strength can vary between 10,971 and the 17,200".
- Wikipedia, [Normandy landings](https://en.wikipedia.org/wiki/Normandy_landings): "a full-strength unit of around 12,000".
- Wikipedia coordinates: [Airel](https://en.wikipedia.org/wiki/Airel) 49.2140, -1.0750; [Bérigny](https://en.wikipedia.org/wiki/B%C3%A9rigny) 49.1436, -0.9397.

**Decision.** Agree on both points.
- *Strength.* The 2,500 men, 14 guns and 5 tanks are what CMH says Kraiss had for the new Elle line, not a count of the whole division, and CMH says "had" rather than that he "reported" it; the row's note read as if it were the division's total. The conflicting establishment figures (about 17,200 versus about 12,000) measure a different thing (paper establishment and D-Day strength) and are kept as sourced in the `strength_json` note and the row `notes`, not reconciled. `strength_status` stays `heavily_depleted` (the line force was a small fraction of any establishment figure, and CMH calls the division a regimental-strength Kampfgruppe a week later); `personnel`, `tanks` and `basis` are unchanged; the 16 antiaircraft guns are now in the note.
- *Location.* The old point was Airel, one end of a line CMH puts at about ten miles (about 12 km between the two coordinates, about 16 km along the river), with a 5 km radius, so it did not cover the line. The point is now the midpoint of Bérigny and Airel (49.1788, -1.0074) with precision 10 km, and the notes say that this is the ordered line and not where the division stood during the day (it was still pulling out of the Aure/Trévières front on 9 June). `location_represents` stays `front_line_point`; confidence stays 0.7.

**Before and after.**

**`command_relationships`**

- before: `[{"unit_id":"GER-COR-084C","name":"German LXXXIV Corps","relationship":"organic"}]`
- after: `[{"unit_id":"GER-COR-084C","name":"German LXXXIV Corps","relationship":"assigned"}]`

**`latitude`**

- before: `49.214`
- after: `49.1788`

**`longitude`**

- before: `-1.075`
- after: `-1.0074`

**`location_name`**

- before: `Elle River line (Berigny-Airel; point = Airel)`
- after: `Elle River line (Berigny-Airel; point = midpoint of the two)`

**`precision_km`**

- before: `5`
- after: `10`

**`source`**

- before: `https://www.ibiblio.org/hyperwar/USA/USA-E-XChannel/USA-E-XChannel-9.html | https://en.wikipedia.org/wiki/Operation_Perch ; coords: Wikipedia`
- after: `https://www.ibiblio.org/hyperwar/USA/USA-E-XChannel/USA-E-XChannel-9.html | https://en.wikipedia.org/wiki/Operation_Perch | https://en.wikipedia.org/wiki/352nd_Infantry_Division_(Germany) | https://en.wikipedia.org/wiki/Normandy_landings ; coords: Wikipedia (Airel 49.2140,-1.0750; Berigny 49.1436,-0.9397; point = midpoint)`

**`strength_json`**

- before: `{"basis":"reported_actual","as_of":"1944-06-09","personnel":2500,"vehicles":{"tanks":5},"vehicle_count_type":"unknown","source":"CMH Cross-Channel Attack ch. IX","note":"Kraiss reported about 2,500 men, 14 guns and 5 tanks left; guns not counted as vehicles"}`
- after: `{"basis":"reported_actual","as_of":"1944-06-09","personnel":2500,"vehicles":{"tanks":5},"vehicle_count_type":"unknown","scope":"sub_force","source":"CMH Cross-Channel Attack ch. IX","note":"CMH: for the defence of the new Elle line (about ten miles) Kraiss had 2,500 men, 14 artillery pieces, 16 antiaircraft guns and 5 tanks; this is the force available for that line, not a count of the whole division. Other figures, different basis: Wikipedia 352nd Infantry Division page about 17,200 at full strength on the old-type establishment (range 10,971-17,200); Wikipedia Normandy landings page about 12,000 for D-Day. Guns not counted as vehicles"}`

**`notes`**

- before: `About 19:00 Kraiss reported hopeless situation to Marcks and was ordered to withdraw to the Elle River (Berigny-Airel) with ~2,500 men, 14 guns, 5 tanks; night 9/10 June retired toward Saint-Lô, opening the Caumont gap.`
- after: `About 19:00 Kraiss reported a hopeless situation to Marcks and was ordered to withdraw far to the south to a new line along the Elle River from Berigny to Airel (about ten miles), moving in darkness and finishing by 06:00 on 10 June; for that line he had 2,500 men, 14 artillery pieces, 16 antiaircraft guns and 5 tanks (CMH). Night 9/10 June the division retired toward Saint-Lô, opening the Caumont gap. The point is the midpoint of the ordered line, not a position held on the day: on 9 June the division was still pulling out of the Aure/Trévières front. The 2,500 figure is the strength CMH gives for holding the new line and is not a count of the whole division; strength is therefore heavily_depleted relative to the division's size, and by 16-17 June CMH calls the division only a Kampfgruppe of about regimental strength (see C0127). Establishment figures conflict by source and basis and are kept as sourced, not reconciled: Wikipedia's 352nd Division page gives about 17,200 at full strength on the old-type establishment (10,971-17,200 depending on battalion size); Wikipedia's Normandy landings page gives a full-strength unit of around 12,000. [Review: coordinate moved from Airel (49.2140,-1.0750, one end of the line) to the line midpoint and precision widened from 5 to 10 km because the line is about 12-16 km long; strength_json note rewritten (the figures are what was available for the Elle line; 16 antiaircraft guns added; the word 'reported' removed from the note because CMH says Kraiss 'had' these); status, confidence and event unchanged.]`


---

## C0184: 21st Panzer Division (1944-06-28)

**Reviewer's point (heading only in the excerpt):** opposing unit and aggregation of combat activity.

**What the sources say.**
- Wikipedia, [Operation Epsom](https://en.wikipedia.org/wiki/Operation_Epsom), 28 June: Kampfgruppe Frey (1st SS Panzer Division) "arrived at the front and was placed under the command of the 12th SS Panzer Division"; at 06:00 it "launched an attack north of the Odon, supported by Panzer IVs of the 21st Panzer Division. This reached the villages of Mouen and Tourville but the British counter-attacked from the direction of Cheux"; Frey's group "managed to gain control of Mouen" and British tank-supported counter-attacks "halted any further advance but were unable to retake the village". The same page has the 15th (Scottish) Division attacking Grainville-sur-Odon that morning, which is a different action, and has 159th Brigade (11th Armoured Division) crossing to Tourville the evening before.
- Tim Saunders, *Operation Epsom* (Pen & Sword), via [erenow.org, Day Three](https://erenow.org/ww/operation-epsom-viii-british-corps-vs-1st-ss-panzerkorps/6.php): Kampfgruppe Frey was joined by "the Wehrmacht Mark IVs of 4 Kompanie ... 22 Pz Regt" (Panzer Regiment 22 belonged to 21st Panzer); its attack at 06:00 along the railway and road toward Mouen and Tourville made slow progress "against the isolated C Company 3 Monmouths and tanks of 3 County of London Yeomanry"; a Mark IV commander says his Kompanie had five operational panzers in action; C Company (identified by its 11th Armoured Division flashes) was overwhelmed at Mouen; the Leibstandarte then attacked Colleville, held by 2nd Glasgow Highlanders, and was driven back by local counter-attacks; 10th Highland Light Infantry with a squadron of tanks attacked Mouen at 19:45.
- Wikipedia, Epsom (15th Scottish context): 2nd Glasgow Highlanders in 46th Brigade and 10th HLI in 227th Brigade, both 15th (Scottish) Division.

**Decision.** Agree that the opponent was incomplete: the row named only the 15th (Scottish) Division, which the Epsom page does not tie to the Mouen fight, whereas the first opponent at Mouen was a company of 3rd Monmouthshire (159th Brigade, 11th Armoured Division). `engaged_with` is now the 11th Armoured Division and the 15th (Scottish) Division (Colleville and the evening Mouen counter-attack). The 4th Armoured Brigade is in the area per Saunders but is not named as engaged with the Panzer IVs, so it is not listed.

On aggregation: yes, the row folds one connected action (morning attack on Mouen/Tourville, the thrust on Colleville, the evening British counter-attack) into one phrase, and only a company-sized element (about five operational Panzer IVs) of the division is documented. I did not split the row: the sources give no separate place or opponent for the pieces, and a split would invent distinctions that the sources do not make. The activity now says "a company of Panzer IVs" supporting Kampfgruppe Frey's attack on Mouen, and the notes say that the row records that element. Confidence 0.5 to 0.7 by the rubric (village-scale location, two source families: Wikipedia and Saunders); revert if you prefer. `strength_json` (Panzer IV count, unrelated to this action) is unchanged.

**Before and after.**

**`command_relationships`**

- before: `[{"unit_id":"GER-SSPZ-001C","name":"German I SS Panzer Corps","relationship":"organic"}]`
- after: `[{"unit_id":"GER-SSPZ-001C","name":"German I SS Panzer Corps","relationship":"assigned"}]`

**`confidence`**

- before: `0.5`
- after: `0.7`

**`source`**

- before: `https://en.wikipedia.org/wiki/Operation_Epsom ; coords: Wikipedia`
- after: `https://en.wikipedia.org/wiki/Operation_Epsom | https://erenow.org/ww/operation-epsom-viii-british-corps-vs-1st-ss-panzerkorps/6.php ; coords: Wikipedia`

**`current_activity`**

- before: `supporting Kampfgruppe Frey north of the Odon`
- after: `supporting Kampfgruppe Frey's attack on Mouen north of the Odon with a company of Panzer IVs`

**`engaged_with`**

- before: `British 15th (Scottish) Infantry Division`
- after: `British 11th Armoured Division; British 15th (Scottish) Infantry Division`

**`notes`**

- before: `Panzer IVs of 21st Panzer supported Kampfgruppe Frey north of the Odon on 28 June toward Mouen and Tourville. [v5: battle group added to composing_units.]`
- after: `Panzer IVs of 21st Panzer supported Kampfgruppe Frey (1st SS Panzergrenadier Regiment, placed under 12th SS Panzer) north of the Odon on 28 June toward Mouen and Tourville (Wikipedia, Epsom). Saunders, Operation Epsom (via erenow): the tanks were 4 Kompanie, Panzer Regiment 22, with five operational Mark IVs in action; Frey's grenadiers and tanks overwhelmed C Company 3rd Monmouthshire (159th Brigade, 11th Armoured Division) with 3rd County of London Yeomanry tanks at Mouen, attacked Colleville in the late morning (held by 2nd Glasgow Highlanders of 15th Scottish Division) and were driven back by local counter-attacks, and 10th Highland Light Infantry (227th Brigade, 15th Scottish) with a squadron of tanks counter-attacked Mouen at 19:45. Wikipedia: Frey gained Mouen and British counter-attacks supported by tanks halted any further advance but could not retake it. Only a company-sized element of the division is documented that day; the row records that element's part in one connected action (Mouen/Tourville attack, Colleville thrust, evening British counter-attack), not a division-wide operation. It is kept as one row because the sources give no separate place or opponent for the pieces. [v5: battle group added to composing_units.] [Review: engaged_with was 'British 15th (Scottish) Infantry Division' only; 11th Armoured Division added (C Company 3rd Monmouthshire at Mouen, 159th Brigade); activity reworded to state that the 21st Panzer share was a tank company; confidence raised from 0.5 to 0.7 by the rubric (approximate village-scale location, two source families: Wikipedia and Saunders).]`


---

## C0141: 82nd Airborne Division (1944-06-19)

**Reviewer's point (heading only in the excerpt):** event date versus VIII Corps attachment date.

**What the sources say.**
- CMH, [Cross-Channel Attack, ch. X](https://www.ibiblio.org/hyperwar/USA/USA-E-XChannel/USA-E-XChannel-10.html): "On 15 June VIII Corps (Maj. Gen. Troy H. Middleton) had become operational with the attachment of the 101st Airborne Division. ... The 82d Airborne Division would come under its control and, in preparation for this, was ordered to attack south on 17 June to establish a bridgehead south of Pont l'Abbé about a mile and a half deep." Later: "Control of the 90th and of the 82d Airborne Division passed on 19 June to VIII Corps".
- Wikipedia, [American airborne landings in Normandy](https://en.wikipedia.org/wiki/American_airborne_landings_in_Normandy): "On June 19 the division was assigned to VIII Corps, and the 507th established a bridgehead over the Douve south of Pont l'Abbé."

**Decision.** The parent for 19 June is right: VIII Corps took control of the division that day, so `parent_unit_id` `US-COR-008C` is unchanged. What the sources add is the timing problem behind the two claims in conflict group G007: the CMH attack to form the bridgehead was ordered for 17 June, while the division was still under VII Corps (C0131 correctly has VII Corps), and Wikipedia's 19 June date for the bridgehead probably coincides with the transfer date rather than the operation; CMH does not say when the bridgehead was complete. I left the 17 vs 19 June dates and both rows' `disputed` status as they were (no source resolves it), added CMH as a source, and put the timing in `notes`. I changed the VIII Corps entry from `organic` to `attached`, since CMH describes a transfer of control on 19 June, not a standing link (CMH uses "attachment" for the 101st Airborne Division and VIII Corps). The division's other rows keep the migrated `organic` corps link (VII Corps up to 17 June), so the 82nd's chain is now not uniform; that is deliberate here and could be revisited in a wider pass.

**Before and after.**

**`command_relationships`**

- before: `[{"unit_id":"US-COR-008C","name":"US VIII Corps","relationship":"organic"}]`
- after: `[{"unit_id":"US-COR-008C","name":"US VIII Corps","relationship":"attached","effective_from":"1944-06-19","note":"CMH ch. X: control of the 82d Airborne Division passed to VIII Corps on 19 June"},{"unit_id":null,"name":"standing parent not identified","relationship":"unknown","note":"XVIII Airborne Corps, the later parent, was organized after Normandy (Wikipedia, 82nd Airborne Division); none of the sources read names a standing parent on 19 June"}]`

**`source`**

- before: `https://en.wikipedia.org/wiki/American_airborne_landings_in_Normandy ; coords: OSM (Etienville commune centroid, approximate)`
- after: `https://en.wikipedia.org/wiki/American_airborne_landings_in_Normandy | https://www.ibiblio.org/hyperwar/USA/USA-E-XChannel/USA-E-XChannel-10.html ; coords: OSM (Etienville commune centroid, approximate)`

**`notes`**

- before: `Division assigned to VIII Corps 19 June; 507th PIR established a bridgehead over the Douve south of Pont-l'Abbe (Wikipedia). CMH dates the 82nd's attack to establish that bridgehead from 17 June (conflict G007; the claims may describe successive phases). Coordinate corrected in v2 to Pont-l'Abbe / Etienville (v1 pointed at La Haye-du-Puits).`
- after: `Division assigned to VIII Corps 19 June; 507th PIR established a bridgehead over the Douve south of Pont-l'Abbe (Wikipedia). CMH ch. X: VIII Corps became operational on 15 June with the 101st Airborne Division attached; the 82d 'would come under its control' and was ordered to attack south on 17 June to establish a bridgehead about a mile and a half deep south of Pont l'Abbé; 'control of the 90th and of the 82d Airborne Division passed on 19 June to VIII Corps'. So VIII Corps is the right parent for 19 June, but the 17 June attack (C0131) was made while the division was still under VII Corps, and Wikipedia's 19 June date for the bridgehead may coincide with the transfer date; CMH dates the attack to 17 June (conflict G007; the claims may describe successive phases or one operation dated two ways). Coordinate corrected in v2 to Pont-l'Abbe / Etienville (v1 pointed at La Haye-du-Puits). [Review: relationship to VIII Corps changed from organic to attached because CMH describes the 19 June transfer of control, not a standing link; parent_unit_id, coordinates, event, claim_status and confidence unchanged. The division's other rows keep the migrated organic corps link.] [Review 2: coordinate of C0131 moved to the ground south of the Douve, about 1.4 km from this row; an 'unknown' standing-parent entry added because XVIII Airborne Corps did not yet exist and no source read names another; the 507th after-action report puts the crossing toward Vindefontaine on the night of 18-19 June.]`


---

## C0131: 82nd Airborne Division (1944-06-17), fixed in the "Fix C0131 coordinates" commit

**Why it was open.** C0131 is the 17 June half of conflict group G007. Its point (49.2908, -1.5411) is the centre of La Haye-du-Puits, about 11 km south of the Pont-l'Abbé area, while the sister row C0141 (19 June) had been moved to Etienville. Not in the review excerpt; found while checking C0141.

**What the sources say.**
- CMH, [Cross-Channel Attack, ch. X](https://www.ibiblio.org/hyperwar/USA/USA-E-XChannel/USA-E-XChannel-10.html): VIII Corps became operational on 15 June; "The 82d Airborne Division would come under its control and, in preparation for this, was ordered to attack south on 17 June to establish a bridgehead south of Pont l'Abbé about a mile and a half deep." This is an order, and ch. X does not report its result. La Haye-du-Puits is not mentioned for 17 June; the division reached that area only in early July.
- CMH, [Utah Beach to Cherbourg, ch. 8](https://www.ibiblio.org/hyperwar/USA/USA-A-Utah/USA-A-Utah-8.html): by the night of 17 June the 82d "had secured control of the causeway over the Prairies Marécageuses south of St. Sauveur-le Vicomte" (about 7.5 km west of the new point; a different place, not used for this row), and "on 19 June the 82d Airborne Division and elements of the 90th Division also came under [VIII Corps'] control".
- CMH, Utah Beach to Cherbourg, ch. 7: the 508th crossed the Douve at Beuzeville-la-Bastille on the night of 12-13 June and reached Baupte, so a bridgehead south of the Douve already existed before 17 June.
- 507th Parachute Infantry after-action report ([scan, OCR garbled](https://www.airborneinnormandy.com/records/hickey/507th%20Prcht%20Inf%20After%20Action%20Report%20Normandy.pdf)): the regiment took over the 508th's bridgehead positions south of the Douve; on the night of 18-19 June its 1st Battalion crossed the swamp toward Vindefontaine "in conjunction with an attack by the rest of the Division south along the Douve farther to the west".
- Wikipedia, [American airborne landings in Normandy](https://en.wikipedia.org/wiki/American_airborne_landings_in_Normandy): on 19 June the 507th "established a bridgehead over the Douve south of Pont l'Abbé".
- OpenStreetMap Nominatim, checked 24 Oct 2026: Pont l'Abbé hamlet 49.3801, -1.4207; Etienville 49.3772, -1.4353; Les Moitiers-en-Bauptois 49.3646, -1.4334; Vindefontaine 49.3386, -1.4205; Beuzeville-la-Bastille 49.3564, -1.3745; La Haye-du-Puits 49.2911, -1.5451; St-Sauveur-le-Vicomte 49.3854, -1.5318.

**Decision.** The row describes the order of 17 June for a bridgehead about 1.5 miles (2.4 km) deep south of Pont l'Abbé, so the point is on that ground and `location_represents` is `objective` (the planned bridgehead), not `front_line_point`. Best point: Les Moitiers-en-Bauptois commune centre, about 2 km south-southwest of the Pont l'Abbé hamlet and 1.4 km from C0141; `precision_km` stays 5 (named place, approximate). Confidence stays 0.5 (disputed row cap, one source family for the location). `claim_status`, `event_type` and the parent are unchanged. The wording of `current_activity` is now what CMH says (an order), 82 characters, no hedging.

The CMH order (17 June) and Wikipedia's 19 June bridgehead may be the order and its execution; the 507th report places the crossing on the night of 18-19 June. The sources do not settle it, so G007 stays disputed and both rows keep their dates. The distance warning between C0131 and C0141 is gone (1.4 km, well inside the two precision radii).

**Not changed, flagged.** C0131's VII Corps entry is still the migrated `organic` link, like the division's other rows (C0028 to C0124). The sources read describe VII Corps control of the 82nd as operational, and no source names a standing parent before XVIII Airborne Corps (organised after Normandy), so those rows need a review pass; recorded in `docs/roadmap.md`.

**Before and after.**

**`command_relationships`**

- before: `[{"unit_id":"US-COR-007C","name":"US VII Corps","relationship":"organic"}]`
- after: `[{"unit_id":"US-COR-007C","name":"US VII Corps","relationship":"attached","note":"Wikipedia, VII Corps (United States): for Overlord the 82nd and 101st Airborne Divisions were attached to VII Corps"},{"unit_id":null,"name":"standing parent not identified","relationship":"unknown"}]`

**`latitude`**

- before: `49.2908`
- after: `49.3646`

**`longitude`**

- before: `-1.5411`
- after: `-1.4334`

**`location_name`**

- before: `Douve bridgehead south of Pont-l-Abbe (toward La Haye-du-Puits)`
- after: `Douve bridgehead objective south of Pont-l'Abbe (Les Moitiers-en-Bauptois)`

**`location_represents`**

- before: `front_line_point`
- after: `objective`

**`source`**

- before: `https://www.ibiblio.org/hyperwar/USA/USA-E-XChannel/USA-E-XChannel-10.html ; coords: OSM (Etienville commune centroid, approximate)`
- after: `https://www.ibiblio.org/hyperwar/USA/USA-E-XChannel/USA-E-XChannel-10.html | https://www.ibiblio.org/hyperwar/USA/USA-A-Utah/USA-A-Utah-8.html | https://www.airborneinnormandy.com/records/hickey/507th%20Prcht%20Inf%20After%20Action%20Report%20Normandy.pdf | https://en.wikipedia.org/wiki/VII_Corps_(United_States) ; coords: OSM (Les Moitiers-en-Bauptois commune centroid, approximate; Pont l'Abbé hamlet is at 49.3801,-1.4207)`

**`current_activity`**

- before: `attacking south of Pont-l'Abbé to form bridgehead`
- after: `ordered to attack south for a bridgehead about 1.5 miles deep south of Pont l'Abbé`

**`notes`**

- before: `CMH: the 82nd was ordered to attack south on 17 June to establish a bridgehead south of Pont-l'Abbe about a mile and a half deep; Wikipedia dates the bridgehead to 19 June after assignment to VIII Corps. Possibly successive phases of one action; kept as disputed.`
- after: `CMH (Harrison, ch. X): VIII Corps was to take control of the 82d, which "was ordered to attack south on 17 June to establish a bridgehead south of Pont l'Abbé about a mile and a half deep". This is an order; Harrison does not report the result. Point moved from La Haye-du-Puits (v1, about 11 km south) to the ground south of Pont l'Abbé: Les Moitiers-en-Bauptois centre is about 2 km south-southwest of the Pont l'Abbé hamlet (OSM), within the 1.5-mile depth. location_represents is now objective (the planned bridgehead), not front_line_point. Same area, later dates: Wikipedia puts the 507th's bridgehead over the Douve south of Pont l'Abbé on 19 June, and the 507th after-action report (scanned, OCR garbled) has its 1st Battalion crossing the swamp toward Vindefontaine (about 4.6 km south of Pont l'Abbé) on the night of 18-19 June; this row and C0141 may therefore be the order and its execution, and stay disputed. Documented elsewhere on 17 June: the 82d secured the causeway over the Prairies Marécageuses south of St. Sauveur-le-Vicomte by that night (Utah Beach to Cherbourg, ch. 8); that is about 7.5 km west and is not this row's point. [Review: coordinates, location_name, location_represents, source, current_activity and notes changed; parent, claim_status, event_type and confidence unchanged.] [Review 3: link to US VII Corps changed from organic to attached (Wikipedia, VII Corps (United States)); standing parent recorded as unknown. parent_unit_id, coordinates, event, status and confidence unchanged.]`


**C0141, sister row** (only `command_relationships` and `notes` changed in this commit): an `unknown` standing-parent entry was added (`unit_id` null, "standing parent not identified"), because XVIII Airborne Corps did not yet exist and no source read names another formation. The validator warning "attached entry without an organic entry" is therefore gone. No organic entry was invented.

(The final values of both changed fields are in the C0141 section above.)

---

## Reclassifying migrated `organic` links that are really attachments

**Why.** The migration from the old free-text `parent_formation` wrote every corps or division link as `organic`. While fixing C0131 it turned out that the 82nd Airborne's VII Corps link was never a standing one: Wikipedia ([VII Corps (United States)](https://en.wikipedia.org/wiki/VII_Corps_(United_States))) says "For Overlord, the 82nd and 101st Airborne Divisions were attached to VII Corps", and CMH ([Cross-Channel Attack, ch. X](https://www.ibiblio.org/hyperwar/USA/USA-E-XChannel/USA-E-XChannel-10.html)) says VIII Corps became operational on 15 June "with the attachment of the 101st Airborne Division" and that "control of the 90th and of the 82d Airborne Division passed on 19 June to VIII Corps". XVIII Airborne Corps, the later parent, was organised after Normandy, so no source read names a standing parent for either division.

**Rule applied.** Change `organic` to `attached` only where a source says attached, attachment, or control passed. Keep `parent_unit_id` (the operational parent on the row's date) unchanged, add an `unknown` standing-parent entry unless a source names one, and add `effective_from` only where a source gives a date (15 June for the 101st at VIII Corps; 19 June for the 82nd, done earlier in C0141). The VII Corps entries carry no date because the source says "for Overlord", not a day. Two British brigades follow the same rule: the 4th Armoured Brigade (C0165; Wikipedia, Operation Epsom: "although attached to the 11th Armoured Division") and the 31st Independent Tank Brigade (C0164; Wikipedia, Epsom order of battle: "Attached for Operation Epsom", parent VIII Corps as on the row).

**Rows changed (13), `command_relationships` before and after:**

| claim | unit | date | operational parent | before | after |
|---|---|---|---|---|---|
| C0028 | 82nd Airborne Division | 1944-06-06 | US-COR-007C | US VII Corps: organic | US VII Corps: attached; standing parent not identified: unknown |
| C0062 | 82nd Airborne Division | 1944-06-09 | US-COR-007C | US VII Corps: organic | US VII Corps: attached; standing parent not identified: unknown |
| C0075 | 82nd Airborne Division | 1944-06-10 | US-COR-007C | US VII Corps: organic | US VII Corps: attached; standing parent not identified: unknown |
| C0102 | 82nd Airborne Division | 1944-06-13 | US-COR-007C | US VII Corps: organic | US VII Corps: attached; standing parent not identified: unknown |
| C0124 | 82nd Airborne Division | 1944-06-16 | US-COR-007C | US VII Corps: organic | US VII Corps: attached; standing parent not identified: unknown |
| C0131 | 82nd Airborne Division | 1944-06-17 | US-COR-007C | US VII Corps: organic | US VII Corps: attached; standing parent not identified: unknown |
| C0024 | 101st Airborne Division | 1944-06-06 | US-COR-007C | US VII Corps: organic | US VII Corps: attached; standing parent not identified: unknown |
| C0072 | 101st Airborne Division | 1944-06-10 | US-COR-007C | US VII Corps: organic | US VII Corps: attached; standing parent not identified: unknown |
| C0085 | 101st Airborne Division | 1944-06-12 | US-COR-007C | US VII Corps: organic | US VII Corps: attached; standing parent not identified: unknown |
| C0098 | 101st Airborne Division | 1944-06-13 | US-COR-007C | US VII Corps: organic | US VII Corps: attached; standing parent not identified: unknown |
| C0117 | 101st Airborne Division | 1944-06-15 | US-COR-008C | US VIII Corps: organic | US VIII Corps: attached from 1944-06-15; standing parent not identified: unknown |
| C0164 | 31st Tank Brigade | 1944-06-26 | UK-COR-008C | British VIII Corps: organic | British VIII Corps: attached; standing parent not identified: unknown |
| C0165 | 4th Armoured Brigade | 1944-06-26 | UK-ARM-011D | British 11th Armoured Division: organic | British 11th Armoured Division: attached; standing parent not identified: unknown |

**Left as `organic`, ambiguous or outside the approved class** (also listed in `docs/roadmap.md`):
- 4th Infantry Division (VII Corps) and the other US infantry and armoured divisions: the sources read list them under a corps, but none says attached. the Wikipedia page for the British I Corps notes that "assignments of corps to armies, and divisions to corps, changed frequently", which supports treating such links as assignments rather than proven attachments.
- 79th and 90th Divisions: reviewed in the next section (79th changed, 90th stays `organic`).
- 6th Airborne Division (UK): Wikipedia gives I Airborne Corps as its standing parent (formed 1943 with the 1st and 6th Airborne Divisions under command) and lists the division with British I Corps on 6 June, but does not use the word attached for June. Not changed; the fix would need I Airborne Corps added to `data/units.csv`.
- 8th Armoured Brigade (50th Division, C0020): the source says only "supported by the 8th Armoured Brigade".
- 79th Armoured Division (21st Army Group) and the British and US corps-to-army links: standing links, correctly `organic`.
- C0212 (Combat Command A, with the 101st Airborne) was already `attached`.

## Backfilling `strength_json.scope` (10 of 12 rows, then the last two)

Each scope comes from what the row's own `note` and source say the figure covers. `sub_force` only where the source says a portion (landed on D-Day, led south); `whole_unit` only where the figure is clearly for the whole unit. Nothing else in the rows changed.

| claim | unit | personnel | scope | why |
|---|---|---|---|---|
| C0006 | 352nd Infantry Division | 12,000 | whole_unit | Wikipedia, Normandy landings: "a full-strength unit of around 12,000" |
| C0007 | 709th Static Infantry Division | 12,000 | whole_unit | Wikipedia: "initial strength of over 12,000" for the division |
| C0009 | 716th Static Infantry Division | 7,000 | whole_unit | Wikipedia: "At 7,000 troops, the division was significantly understrength" |
| C0065 | 3rd Fallschirmjäger Division | 15,976 | whole_unit | Wikipedia: "at full strength", soldiers and officers on arrival |
| C0167 | VIII Corps | 60,244 | whole_unit | Wikipedia, Operation Epsom: "VIII Corps total at the start of Epsom" |
| C0172 | Kampfgruppe Weidinger | 2,500 | whole_unit | Wikipedia, Epsom order of battle: battle group strength at arrival (the unit is the battle group) |
| C0022 | Second Army | 83,115 | sub_force | Wikipedia: men landed on D-Day, "not unit strength" |
| C0030 | First Army | 60,000 | sub_force | army.mil: troops landed on D-Day (about) |
| C0031 | V Corps | 34,250 | sub_force | Wikipedia: men landed on D-Day (about) |
| C0138 | 77th Infantry Division | 1,400 | sub_force | CMH ch. X: "about 1,400 men led south by Oberst Bacherer", a part of the division |

**The last two rows were resolved in the "Resolve scope for C0018 and C0027; require scope" commit:**
- **C0027, 4th Infantry Division** (before: personnel 21,000, no scope, Wikipedia Normandy landings; after: personnel 20,000, `scope` `sector`, CMH Utah Beach to Cherbourg [ch. 3](https://www.ibiblio.org/hyperwar/USA/USA-A-Utah/USA-A-Utah-3.html)). CMH says the whole 4th Division except the 20th Field Artillery Battalion landed in the first fifteen hours, "in addition" came one battalion of the 359th Infantry, the 65th Armored Field Artillery Battalion, the 87th Chemical Mortar Battalion, the 899th Tank Destroyer Battalion (less two companies), the 70th and 746th Tank Battalions, components of the 1st Engineer Special Brigade, seaborne elements of the airborne divisions and many smaller units, and "a total of over 20,000 troops and 1,700 vehicles reached Utah Beach by the end of 6 June". So the figure is the force landed at Utah, not the division; Wikipedia's "21,000 troops" (4th Division, from Whitmarsh) is kept in the note. The 197 casualties in the row's notes are the division's own (CMH).
- **C0018, 6th Airborne Division** (before: personnel 8,500, "men deployed 5-7 June", no scope; after: `strength_json` removed). Wikipedia, Operation Tonga says "out of the 8,500 men deployed" (citing the Air Ministry); the British Army page says "the 8,500 British and Canadian soldiers of 6th Airborne Division"; the Airborne Assault Museum gives 7,000 British paratroopers and glider-borne troops; other histories give about 12,000 for the full division. Pegasus Archive ([The Plan](https://pegasusarchive.org/normandy/depth_plan.htm)) says there were not enough aircraft "to bring in their full strength" and the remainder came by sea on the second day (Wikipedia, Operation Mallard: the rest of the 12th Devons arrived by sea on 7 June), but no source gives that number or says whether 8,500 includes it. Nothing settles whole_unit versus sub_force, so the figure was removed and the row's notes record the old figure, the competing figures and the reason. CMH has no figure for this division.

**Scope is now mandatory.** With no missing-scope warnings left, `scripts/validate.py` reports `strength_json` with `personnel` but no `scope` as an error (exit code 1). Tested on a scratch copy: removing `scope` from C0006 gave "ERROR ... strength_json has personnel but no scope" and exit code 1; the real repository validates. Updated: `scripts/validate.py`, `schema/README.md`, `schema/claims.schema.json`, `schema/vocabularies.json` (scope description, and the `sector` definition now also covers all forces landed on a beach), `docs/methodology.md` (also 20 of 212 rows now carry figures: 15 estimate, 5 reported_actual) and `CONTRIBUTING.md`.

## Verifying the 79th and 90th Division corps links (and other June corps changes)

**What the sources say.**
- CMH, Utah Beach to Cherbourg ([ch. 1](https://www.ibiblio.org/hyperwar/USA/USA-A-Utah/USA-A-Utah-1.html)): the revised VII Corps field order of 28 May "provided for the temporary attachment to the VII Corps of another division, the 79th". Cross-Channel Attack ([ch. X](https://www.ibiblio.org/hyperwar/USA/USA-E-XChannel/USA-E-XChannel-10.html)): "General Bradley assigned the 79th Division to VII Corps as a replacement for the 90th" (about 13 June); "the 79th Division moved south on 28 June to reorganize under VIII Corps"; "control of the 90th and of the 82d Airborne Division passed on 19 June to VIII Corps".
- Wikipedia, [79th Infantry Division](https://en.wikipedia.org/wiki/79th_Infantry_Division_(United_States)), assignments in ETO: 18 April 1944 VIII Corps, Third Army; 29 May "Third Army but attached to VII Corps, First Army"; 30 June "Third Army, but attached to First Army"; 1 July VIII Corps. [90th Infantry Division](https://en.wikipedia.org/wiki/90th_Infantry_Division_(United_States)): 5 March Third Army; 23 March "Third Army, but attached to First Army"; 27 March VII Corps; 19 June VIII Corps (no "attached" wording).
- Neither division is shown assigned to First Army or XV Corps for June; XV Corps appears only for the 90th on 1 August. No source read supports the guess in the task text.

**What was changed.**
- 79th Division (C0087, C0140, C0168; VII Corps): `attached`, `effective_from` 1944-05-29 (Wikipedia date; CMH puts the attachment in the 28 May field order). The standing parent is Third Army (Wikipedia), added as the `parent_only` unit `US-ARMY-003A`, so there is no `unknown` entry. C0087 (12 June) had parent `unknown`; the same sources show VII Corps attachment from 29 May, so its `parent_unit_id` is now VII Corps.
- 79th Division (C0193, 28 June; VIII Corps): `operational_control` from 1944-06-28, because CMH says only "reorganize under VIII Corps". Wikipedia dates the move 30 June (attached to First Army) and 1 July (VIII Corps); the CMH date is used.
- 90th Division (C0142, VIII Corps, 19 June): relationship stays `organic` (Wikipedia calls both corps links assignments and CMH says "control passed", not attached); only `effective_from` 1944-06-19 was added. The four earlier VII Corps rows are unchanged.
- 29th Division (C0112, C0130; XIX Corps): stays `organic`, `effective_from` 1944-06-14 added (CMH ch. IX: XIX Corps "took over from V Corps control of the 29th Division" on 14 June; no attachment wording).

**Rows changed (7), `command_relationships` before and after:**

| claim | unit | date | operational parent (before > after) | before | after |
|---|---|---|---|---|---|
| C0087 | 79th Infantry Division | 1944-06-12 | unknown > US-COR-007C | unknown | US VII Corps: attached from 1944-05-29; US Third Army: assigned |
| C0140 | 79th Infantry Division | 1944-06-19 | US-COR-007C > US-COR-007C | US VII Corps: organic | US VII Corps: attached from 1944-05-29; US Third Army: assigned |
| C0168 | 79th Infantry Division | 1944-06-26 | US-COR-007C > US-COR-007C | US VII Corps: organic | US VII Corps: attached from 1944-05-29; US Third Army: assigned |
| C0193 | 79th Infantry Division | 1944-06-28 | US-COR-008C > US-COR-008C | US VIII Corps: organic | US VIII Corps: operational_control from 1944-06-28; US Third Army: assigned |
| C0142 | 90th Infantry Division | 1944-06-19 | US-COR-008C > US-COR-008C | US VIII Corps: organic | US VIII Corps: assigned from 1944-06-19 |
| C0112 | 29th Infantry Division | 1944-06-14 | US-COR-019C > US-COR-019C | US XIX Corps: organic | US XIX Corps: assigned from 1944-06-14 |
| C0130 | 29th Infantry Division | 1944-06-17 | US-COR-019C > US-COR-019C | US XIX Corps: organic | US XIX Corps: assigned from 1944-06-14 |

**Checked and left unchanged, ambiguous:**
- 30th Division (C0118, XIX Corps `organic`; C0074 parent `unknown`): CMH ch. IX says XIX Corps "became operational on 13 June, with the 30th Division attached", but Wikipedia lists the 30th as assigned to XIX Corps, First Army from 18 February 1944. Sources conflict, so it was left.
- 83rd Division (C0134, 18 June, parent `unknown`): Wikipedia lists VIII Corps, Third Army (8 April) and attached to VIII Corps, First Army only from 25 June; no source gives the 18 June operational parent.
- 9th Division (VII Corps since 25 November 1943 per Wikipedia), 1st and 2nd Infantry Divisions (V Corps; the 2nd from 14 April 1944): assignments, not attachments, so `organic` stays.
- 2nd and 3rd Armored Divisions (V Corps rows; C0100 and C0152 unknown) and the 4th Infantry Division: no assignment table found, not changed.

## Resolving the G004 coordinate gap (C0067 / C0081, LXXXIV Corps)

`check_coordinates.py` flagged "C0081 is 49.0 km away, more than the 10 km the two precision radii allow" (radii 25 + 5 before this change).

**What the rows said.** Both rows are about the change of corps commander. C0067 (alternate, 10 June, confidence 0.3): Fahrmbacher takes command, from Wikipedia's [Wilhelm Fahrmbacher](https://en.wikipedia.org/wiki/Wilhelm_Fahrmbacher) succession box (LXXXIV Corps 10-16 June 1944). C0081 (preferred, 12 June, confidence 0.7): Marcks killed in an air attack, Fahrmbacher takes over that evening (CMH [Cross-Channel Attack ch. X](https://www.ibiblio.org/hyperwar/USA/USA-E-XChannel/USA-E-XChannel-10.html): "took command of LXXXIV Corps on the evening of 12 June", citing the Seventh Army war diary; Wikipedia's [Erich Marcks](https://en.wikipedia.org/wiki/Erich_Marcks) and [LXXXIV Army Corps](https://en.wikipedia.org/wiki/LXXXIV_Army_Corps_(Wehrmacht)) pages agree on 12 June).

**Diagnosis: (c) different things located, plus (b) a placeholder and a wrong label; not a place disagreement and not a legitimate distance.**
- The conflict is about the date (10 versus 12 June). No source gives a different place for either date.
- C0067's point (49.52,-1.47, "Cotentin sector (corps HQ location not verified)", 25 km) was a generic placeholder; the Fahrmbacher page names no place. It sat 49 km from C0081.
- C0081's point (49.1269,-1.165) is Wikipedia's coordinate for Hébécrevon, the place its Marcks page gives for his death, about 5 km west of Saint-Lô (Wikipedia: 49.12,-1.09; the corps was "stationed in Saint-Lô", and C0012 uses it as the headquarters). It was labelled `main_body`, but a commander's death place is not the corps' main body.

**Changes (coordinates of C0081 unchanged).**

| row | field | before | after |
|---|---|---|---|
| C0067 | latitude, longitude | 49.52, -1.47 | 49.12, -1.09 |
| C0067 | location_name | Cotentin sector (corps HQ location not verified) | Saint-Lô (corps HQ per Wikipedia, not tied to 10 June) |
| C0067 | location_represents | sector_center | headquarters |
| C0067 | precision_km | 25 | 10 (no source ties that HQ to 10 June) |
| C0067 | source | Fahrmbacher page | + Wikipedia LXXXIV Army Corps page |
| C0067 | confidence | 0.3 | 0.3 (alternate, date contested, place inferred) |
| C0081 | location_name | Hébécrevon (near Saint-Lô) | Hébécrevon (where Marcks was killed, near Saint-Lô) |
| C0081 | location_represents | main_body | approach_route (Marcks was travelling to Carentan) |
| C0081 | confidence | 0.7 | 0.5 (CMH supports the date and the death, not the place; the place rests on Wikipedia alone: "exact location with one secondary source") |

Both rows keep their group, status and activity text; each gained a `[Review 6: ...]` sentence in `notes`. The two points are now 5.5 km apart (radii 10 + 5). No allowance or threshold change was needed in `check_coordinates.py`, and none was added. The other four LXXXIV Corps rows with the same placeholder (C0106, C0116, C0123, C0128) were not changed: no source read places the headquarters on 14-17 June (listed in `docs/roadmap.md`).

## Placeholder units for the Western Front ("Add Western Front unit placeholders")

This commit creates placeholders for all ground units, German, British, US, French and others, with a formation date where easily available.

- **What was added:** 266 placeholder units (351 units in total: 76 with claims, 275 placeholders), covering army group, army, corps, division and significant independent brigade level for the Western Front, 6 June 1944 to 8 May 1945 (northwest Europe plus southern France; Italy excluded). `docs/coverage.md` and `build/coverage.csv` (generated by `scripts/build.py`) list every unit by nationality, echelon, record status, whether it has claim rows and how many. The 85 existing units are unchanged in their original eight columns; no claim row was touched.
- **Schema (additive):** new unit columns `record_status` (placeholder / partial / active), `formed_date`, `formed_date_source`, `initial_parent_unit_id`, `initial_parent_as_of`, `initial_parent_source`, `component_of_note`, `unit_note` and `listing_source`. The nine existing `parent_only = true` units became `placeholder`; all others `active`. New nationalities (Poland, France, Belgium, Netherlands, Czechoslovakia), reserved echelon values for later air and naval work (`air_force`, `air_formation`, `fleet`, `naval_unit`), reserved branches (`Marines`, `Air Force`, `Navy`) and two new vocabularies (`record_status`, `source_token`).
- **Why separate parent columns:** the existing `parent_unit_id` means organic parent of a battle group and the validator forces it to match `command_relationships`. A source listing is not that, so the placeholder parent lives in `initial_parent_*` with a date and a source token and is never used for `command_relationships`. Parents are filled only where a source gives them: the German 6 June 1944 order of battle (German Wikipedia), the first matching Lexikon der Wehrmacht timeline entry for later arrivals, and Wikipedia's Dragoon page for the VI Corps units. Allied placeholders otherwise have no parent.
- **Formation dates:** 233 of 351 units have `formed_date`. German dates come from the first sentence of the Lexikon der Wehrmacht page; a date that is only an order to form is left blank. Allied dates are the Wikipedia infobox start date, used only when it begins in 1939-1945 (units with a First World War lineage are left blank); starred infobox dates may be constitution dates and say so in `unit_note`. `formed_date` is formation or activation, never arrival in theater.
- **Validator:** `scripts/validate.py` now checks `record_status` against `parent_only` and the claim files (a claim file for a placeholder is an error; `scripts/promote_placeholders.py` fixes it), `formed_date` validity and source, the `initial_parent_*` set and resolution, source tokens, name uniqueness within a nationality, and warns when an `engaged_with` name does not match a unit (9 new warnings, all battalion, regiment, naval or air opponents or free-text artefacts). Referenced ids in claims (`unit_id`, `parent_unit_id`, `command_relationships`) were already checked.
- **Judgement calls to check:** reconstituted German divisions are separate records (352nd Infantry and 352nd Volksgrenadier Division, and so on); Reserve Corps and the Armeekorps they became are one record per Armeekorps; the 1945 Volks-Artillerie-Korps are corps-level placeholders; units of uncertain Western Front service (11th Army, 24th Army, Armee-Abteilung von Luettwitz, the French 1st Division naming, Canadian I Corps and the divisions that arrived from Italy) carry a note. The full list of exclusions and ambiguities is in `docs/roadmap.md`.

## US Batch 1: 1 July to 30 September 1944 ("US batch 1: Jul-Sep 1944")

Scope: US Army ground units on the Western Front at army group, army, corps and division level; no Marines; milestone rows, not daily positions. The sample for review is `spot_check_batch1.md` (15 rows chosen by risk).

- **What was added:** 268 new claims (C0213 to C0480): 209 division, 43 corps, 14 army, 2 army group. 480 claims in total. Per unit: 12th and 6th Army Groups 1 each; First Army 5, Third 5, Seventh 3, Ninth 1; V Corps 2, VI 4, VII 6, VIII 10, XII 8, XV 5, XIX 2, XX 5, XVIII Airborne 1; division counts are in `docs/coverage.md`.
- **Units activated (25):** US-AG-006G, US-AG-012G, US-ARMY-003A, -007A, -009A, US-COR-006C, -012C, -015C, -020C, US-ABN-018C, US-ARM-004D to -007D, and US-INF-003D, -005D, -008D, -026D, -028D, -035D, -036D, -044D, -045D, -080D, -094D (via `scripts/promote_placeholders.py`). The stub unit `ALL-AFHQ-000H` (Allied Force Headquarters, theater mediterranean, placeholder, listing source `WPDRAGOON`) was added as Seventh Army's parent until 15 September.
- **Method:** a hybrid. Division rows (arrival or landing, first combat, corps changes, commander changes, command-post rows) were generated from the CMH ETO-OB division pages (Wayback copies); army, army group and corps rows, and the division events that matter operationally (Cobra, Mortain, Brest, Paris, Moselle, Arracourt, Dragoon, Market Garden), were written by hand from the Green Books on HyperWar and Wikipedia. Every row has its source URLs; coordinates come from named places (Nominatim/Wikipedia) with `precision_km` and `confidence` by the rubric in `docs/methodology.md`. The generated rows' rules are in the new methodology section "US Army fill-in (Batch 1)".
- **Schema:** unchanged except the `theater` vocabulary descriptions (`schema/vocabularies.json`, `schema/README.md`): `western_europe` now includes southern France from the Dragoon landing on 15 August 1944; `mediterranean` covers southern France only before that. No new columns or values.
- **Conflict groups (3 new, 14 in total):** G012 4th Armored Division landing (CMH 13 July, preferred; Wikipedia 11 July, alternate, 0.3); G013 VIII Corps passing to Ninth Army (10 September from Breakout and Pursuit p636, preferred; 5 September from the CMH division tables and Wikipedia, alternate); G014 fall of Brest (18 September from the Green Book, preferred; 19 September Wikipedia, alternate).
- **Judgement calls to check:**
  - Army group and army headquarters places are mostly not stated in the sources used. Those rows (12th Army Group and Third Army on 1 August, 6th Army Group and Seventh Army on 15 September) use a named representative point, `sector_center`, 50 km, 0.3. First Army's 1 August change of commander (Hodges) has no row of its own because no place was found; it is mentioned in the 7 August row.
  - The CMH assignment table does not separate Assigned from Attached: corps links are recorded as `attached` with `effective_from` and confidence at most 0.5; army links are `organic`; where the table shows no army the entry is `unknown`. A corps change reversed within two days is ignored. The 15 September 'V' corps for the 45th Division is read as a transcription error for VI.
  - CP rows say only that CMH lists the CP at that town. The confidence and precision depend on the gap to the nearest CP date (0.7 / 3 km same day, down to 0.3 / 50 km); rows more than 14 days from any CP were not written.
  - 28th Division: CMH's first-combat date (22 July) is earlier than its arrival (24 July), so no first-combat row was written. 26th Division: the arrival row is dated 7 September from the Valognes CP; the CMH Continent date is 19 September. Both inconsistencies are in the source.
  - The Italy-based pre-landing rows for the 3rd, 36th and 45th Divisions were excluded (out of scope). A promotion without a change of commander (3rd Armored, 8th and 90th Divisions) is `other`, not `command_change`.
  - Some CMH region names look wrong for the town (for example Plomion, Punerot, Sees); the coordinates follow the real place and the check against the département was applied. About a dozen CMH hamlets that could not be placed with confidence were dropped (listed in the working notes, not in the data).
  - XIX Corps' 27 August row was replaced by the verified 29 August row. "Colonel von der Mosel" is given as "Von der Mosel".
- **Unsourced / not provided:** no Batch 1 row carries `strength_json` (the sources do not give per-date strength); the headquarters places above; `engaged_with` is filled only where a Green Book page names the opponent.
- **Existing claims:** none of the 212 existing claims was edited in this commit (the later review commit did edit them, see the section "Batch 1 review" below).
- **Coordinate checks:** `scripts/check_coordinates.py --geocode --country fr` gave 14 warnings over 480 rows, none a real error. Three are speed flags: C0053 (Panzer Lehr, pre-existing); C0280 (7th Armored, 182 km in 2 days: motor march from the assembly area to Dreux-Chartres); C0411 (29th Division, 813 km in 8 days: Brest to the Netherlands after 24 September). The other 11 are geocode flags from restricting the lookup to France: four for pre-existing rows (C0045, C0104, C0118, C0141) and seven new ones (C0214-C0219, C0240) for places outside France (Leicester and Newbury in England, Nijmegen in the Netherlands, Namur in Belgium) that the French-only lookup matched to a homonym; the coordinates were checked by hand against the named places. All the new French places that geocoded passed. Many CMH hamlets are not in Nominatim (listed in the tool's 'Not geocoded' line) and were checked only by the département test used when the rows were generated.

## Batch 1 review: second reviewer's check of the 15-row spot check (25 October 2026)

A second reviewer checked `spot_check_batch1.md`; each point was verified independently against real sources and the data was changed only where the sources support it. Verdicts: **agree** (the source supports the reviewer), **partly agree**, **disagree**. Of the 15 rows, 12 are agree, 3 partly agree (C0315/C0316 relationship type, C0243/C0244 landing dates, C0300 division rows); none is a flat disagreement, but several of the reviewer's specific claims could not be confirmed (the "Essential to Success" page could not be opened, the 704th Tank Destroyer Battalion dates, the NHHC page) and one proposal (an unspecified "confidence shared by rows with different evidence" check) was not implemented. Sources: CMH *Breakout and Pursuit* (HyperWar), the 6th Army Group G-3 Final Report, Wikipedia, Wikimanche, USHMM, EUCMH and the others listed in `docs/sources.md`. All edits are in `data/**` and `schema/**` (claim_ids and unit_ids unchanged; two new claims C0481 and C0482 and one new unit `ALL-FAAA-001A`); `build/` was regenerated; `validate.py`, `build.py --check` and `check_coordinates.py` pass.

Summary of the row verdicts:

| row | verdict | what changed |
|---|---|---|
| C0223 12th Army Group, 1 Aug | agree | HQ now Château des Mares, Saint-Sauveur-Lendelin (5 km, 0.7); `activation`; SHAEF `assigned`, 21st Army Group `coordinating` to 31 Aug |
| C0222 6th Army Group, 15 Sep | agree | HQ now Lyon (Palais de la Foire, east bank of the Rhône; approximate point, 0.5); SHAEF `operational_control`, AFHQ `administrative_control` |
| C0284 First Army, 25 Jul | agree | engaged_with widened to three units, non-exhaustive note, sector point marked as such |
| C0297 Ninth Army, 5 Sep | agree | `activation` (new event type), 12th Army Group `assigned` |
| C0315/C0316 VIII Corps, G013 | partly agree | 10 Sep `operational_control`; 5 Sep is the table date, `unspecified_subordination`, event definitions added |
| C0317/C0318 Brest, G014 | agree | activity reworded, event definitions added |
| C0333 XIX Corps, 29 Aug | agree | three divisions in `composing_units`; point relabelled as bridgehead area |
| C0213 XVIII Airborne Corps, 25 Aug | agree | `redesignation`; lineage note; `ALL-FAAA-001A` added |
| C0217 82nd Airborne, 17 Sep | agree | landing row and a new CP row (C0481); I Airborne Corps `operational_control`; same split for the 101st (C0220, C0482) |
| C0243/C0244 4th Armored, G012 | partly agree | both rows kept with event definitions; landing row moved to Utah Beach; reviewer's 704th battalion dates not confirmed |
| C0457 80th Infantry, 3 Aug | agree | links `unspecified_subordination` with dates |
| C0479 94th Infantry, 5 Sep | agree | location marked as the CP of 8 Sep (+3 days) |
| C0388 26th Infantry, 7 Sep | agree | 7 Sep kept and corroborated; 19 Sep explained |
| C0406 29th Infantry, 19 Aug | agree | location marked as the CP of 22 Aug (+3 days); Lannilis 23 Aug confirmed |
| C0300 VI Corps, Dragoon | partly agree | sectors named; division landing rows already existed |
| (audit) C0244, C0245, C0269 | found by the audit | the CMH place "Mesnil-St-Martin" was mis-geocoded about 50 km off; kept at 50 km, 0.3 |

---

## C0223: 12th Army Group (1944-08-01)

**Reviewer's point.** Headquarters was at Saint-Sauveur-Lendelin, not Avranches ("Essential to Success"); give the HQ at precision 5-10 and confidence about 0.8, keep Avranches only as an operational-area reference; the SHAEF relationship should not be "unknown": separate organisational authority, theater coordination (Montgomery until 1 September) and direct operational control.

**What the sources say.**
- Warfare History Network, "The 12th Army Group Gets Going": the group became operational at Saint-Sauveur-Lendelin at noon on 1 August.
- Wikimanche, "Château des Mares (Saint-Sauveur-Lendelin)", dday-overlord and KilroyTrip: the château was Bradley's headquarters; he received Churchill there on 7 August and Eisenhower on 8 August.
- CMH brochure "Northern France" and Pogue, *The Supreme Command* ch. 15 (HyperWar): Montgomery coordinated both army groups in the field until Eisenhower assumed direct command on 1 September. The 6th Army Group G-3 report and the trailblazers history also say the group came under SHAEF directly on 1 September.
- The Army "Essential to Success" PDF the reviewer cites could not be opened from this box (access denied), so it is not cited; the location rests on the sources above.

**Decision: agree.** The headquarters was at the Château des Mares. The row now points there (precision 5 km, confidence 0.7: the rubric has no 0.8, and an approximate place with two source families scores 0.7), `location_basis` `documented_on_date`, event type `activation`. Avranches stays only as a sentence in the notes. SHAEF is `assigned` (organisational parent, with a note that SHAEF took direct operational control on 1 September) and 21st Army Group is `coordinating` until 31 August. The point that the 21st Army Group role was "operational control" in some sources is kept in the note.

**Before and after.**

_C0223_

- **`command_relationships`**
  - before: `SHAEF: unknown`
  - after: `Supreme Headquarters Allied Expeditionary Force (SHAEF): assigned from 1944-08-01; British 21st Army Group: coordinating from 1944-08-01 to 1944-08-31`
- **`latitude`**
  - before: `48.6850`
  - after: `49.1274`
- **`longitude`**
  - before: `-1.3556`
  - after: `-1.4271`
- **`location_name`**
  - before: `Avranches, Manche (breakout area, representative point)`
  - after: `Saint-Sauveur-Lendelin (Château des Mares), Manche`
- **`location_represents`**
  - before: `sector_center`
  - after: `headquarters`
- **`precision_km`**
  - before: `50`
  - after: `5`
- **`confidence`**
  - before: `0.3`
  - after: `0.7`
- **`source`**
  - before: `https://www.ibiblio.org/hyperwar/USA/USA-E-Breakout/USA-E-Breakout-18.html#page343 | https://en.wikipedia.org/wiki/Twelfth_United_States_Army_Group ; coords: Wikipedia (en): Avranches`
  - after: `https://www.ibiblio.org/hyperwar/USA/USA-E-Breakout/USA-E-Breakout-18.html#page343 | https://en.wikipedia.org/wiki/Twelfth_United_States_Army_Group | https://warfarehistorynetwork.com/article/the-12th-army-group-gets-going/ | https://www.wikimanche.fr/Ch%C3%A2teau_des_Mares_(Saint-Sauveur-Lendelin) | https://www.dday-overlord.com/en/battle-of-normandy/cities/saint-sauveur-lendelin | https://www.ibiblio.org/hyperwar/USA/USA-E-Supreme/USA-E-Supreme-15.html ; coords: OpenStreetMap Nominatim (Château des Mares, Saint-Sauveur-Lendelin)`
- **`event_type`**
  - before: `command_change`
  - after: `activation`
- **`current_activity`**
  - before: `becoming operational under Bradley, controlling First and Third Armies`
  - after: `becoming operational at Saint-Sauveur-Lendelin under Bradley, controlling First and Third Armies`
- **`notes`**
  - before: `Green Book: 12th Army Group became operational at noon, 1 August, as armored columns streamed beyond Pontaubault; Hodges took First Army and Third Army became operational under Patton. HQ location not stated in the sources used; point is the breakout area.`
  - after: `Event date: Breakout-18 p343 (12th Army Group operational at noon, 1 August; First Army under Hodges, Third Army operational under Patton). Event definition: the army group becomes operational. Relationship: SHAEF is the organisational parent (assigned). Montgomery's 21st Army Group coordinated both army groups in the field until Eisenhower assumed direct operational control on 1 September (CMH "Northern France" brochure; Pogue, Supreme Command ch. 15); some sources describe this as 21st Army Group operational control. Location: the headquarters opened at the Château des Mares, Saint-Sauveur-Lendelin (Warfare History Network; Wikimanche; dday-overlord); Bradley received Churchill there on 7 August and Eisenhower on 8 August. Avranches (the earlier point on this row) was the breakout area, not the headquarters, and is kept only as an area reference. Coordinates: OpenStreetMap Nominatim for the château. The Army "Essential to Success" text cited in review could not be opened here (access denied); the location is confirmed by the other sources.`
- **`location_date`**
  - before: (blank)
  - after: `1944-08-01`
- **`location_basis`**
  - before: (blank)
  - after: `documented_on_date`
- **`location_temporal_offset_days`**
  - before: (blank)
  - after: `0`


---

## C0222: 6th Army Group (1944-09-15)

**Reviewer's point.** Vesoul is not a documented HQ. Find the actual HQ (Lyon/Vittel) or mark it an operational-area reference; the SHAEF relationship should be operational control, not organic.

**What the sources say.**
- 6th Army Group G-3 Section Final Report (`trailblazersww2.org/pdf/SixthArmyG3pdf.pdf`): the move from Saint-Tropez to Lyon began 9 September and was completed 15 September; the Palais de la Foire on the east bank of the Rhône was the first operational headquarters. Orders of the afternoon of 14 September placed Seventh Army and French Army B under the group from 0001B on 15 September; tactical control passed from AFHQ to SHAEF; supply, administrative and civil-affairs responsibility in the area overrun stayed with AFHQ.
- CMH *Riviera to the Rhine* and Pogue ch. 15 agree on 15 September. FRUS 1944 Quebec doc. 150 only expected Seventh Army headquarters north of Lyon.
- Vittel appears in the report for 27 December, not for September, so it is not the 15 September headquarters.

**Decision: agree.** The row now points at Lyon (Palais de la Foire, east bank of the Rhône), event type `activation`. The place could not be geocoded; the coordinate is the Cité Internationale area on the east bank (OpenStreetMap), approximate, so precision is 5 km and confidence 0.5 (one source family, approximate point). Relationships: SHAEF `operational_control` from 15 September and AFHQ `administrative_control`, each with the report as the basis.

**Before and after.**

_C0222_

- **`command_relationships`**
  - before: `SHAEF: organic`
  - after: `Supreme Headquarters Allied Expeditionary Force (SHAEF): operational_control from 1944-09-15; Allied Force Headquarters (AFHQ): administrative_control from 1944-09-15`
- **`latitude`**
  - before: `47.6231`
  - after: `45.7849`
- **`longitude`**
  - before: `6.1558`
  - after: `4.8538`
- **`location_name`**
  - before: `Vesoul, Haute-Saône (front, representative point)`
  - after: `Lyon, Palais de la Foire (east bank of the Rhône), Rhône`
- **`location_represents`**
  - before: `sector_center`
  - after: `headquarters`
- **`precision_km`**
  - before: `50`
  - after: `5`
- **`confidence`**
  - before: `0.3`
  - after: `0.5`
- **`source`**
  - before: `https://www.ibiblio.org/hyperwar/USA/USA-E-Breakout/USA-E-Breakout-32.html#page701 | https://www.ibiblio.org/hyperwar/USA/USA-E-Breakout/USA-E-Breakout-32.html#page683 | https://en.wikipedia.org/wiki/Sixth_United_States_Army_Group ; coords: Wikipedia (en): Vesoul`
  - after: `https://www.ibiblio.org/hyperwar/USA/USA-E-Breakout/USA-E-Breakout-32.html#page701 | https://www.ibiblio.org/hyperwar/USA/USA-E-Breakout/USA-E-Breakout-32.html#page683 | https://en.wikipedia.org/wiki/Sixth_United_States_Army_Group | https://www.trailblazersww2.org/pdf/SixthArmyG3pdf.pdf ; coords: OpenStreetMap Nominatim (Cité Internationale, Lyon; approximate stand-in for the Palais de la Foire)`
- **`event_type`**
  - before: `command_change`
  - after: `activation`
- **`current_activity`**
  - before: `becoming operational under Devers with Seventh Army and French First Army`
  - after: `becoming operational at Lyon under Devers with Seventh Army and French First Army`
- **`notes`**
  - before: `Breakout-32: 6th Army Group became operational on 15 September under SHAEF. Headquarters location is not stated in the sources used; point is the front area (Vesoul).`
  - after: `Event date: Breakout-32 p701 and the 6th Army Group G-3 Section Final Report (Seventh Army and French Army B placed under command from 0001B, 15 September). Event definition: the army group becomes operational. Relationship: tactical control passed from AFHQ to SHAEF at 0001B on 15 September, so SHAEF is the operational parent (operational_control); AFHQ retained supply, administrative and civil-affairs responsibility in the area overrun pending further developments (G-3 report). It was not organic to SHAEF. Location: the G-3 report says the move from Saint-Tropez began 9 September and was completed 15 September, and that the Palais de la Foire on the east bank of the Rhône was the first operational headquarters of the 6th Army Group. Vesoul (earlier point) was only the front area and is not a documented headquarters. Coordinates: approximate, the Cité Internationale area on the east bank of the Rhône (OpenStreetMap Nominatim); the Palais de la Foire could not be geocoded and the site is not independently confirmed.`
- **`location_date`**
  - before: (blank)
  - after: `1944-09-15`
- **`location_basis`**
  - before: (blank)
  - after: `documented_on_date`
- **`location_temporal_offset_days`**
  - before: (blank)
  - after: `0`


---

## C0284: First Army, Operation Cobra (1944-07-25)

**Reviewer's point.** Marigny marks the attack sector, not Bradley's HQ; engaged_with Panzer Lehr is not exhaustive.

**What the sources say.**
- Breakout and Pursuit ch. 13: in the penetration sector Panzer Lehr (with a regiment of the 5th Parachute Division attached), elements of the 353rd Division and the 5th Parachute Division, with the 275th Division and 2nd SS Panzer Division reacting later.

**Decision: agree.** The point stays a sector point (precision 10 km, `operational_area`) and the notes say it is not the army command post. `engaged_with` now lists Panzer Lehr, the 353rd Infantry and the 5th Fallschirmjäger Division (three, the validator limit) and the notes say the list is not exhaustive. The 21st Army Group link gets `effective_to` 31 July.

**Before and after.**

_C0284_

- **`command_relationships`**
  - before: `British 21st Army Group: operational_control`
  - after: `British 21st Army Group: operational_control to 1944-07-31`
- **`engaged_with`**
  - before: `German Panzer Lehr Division`
  - after: `German Panzer Lehr Division; German 353rd Infantry Division; German 5th Fallschirmjäger Division`
- **`notes`**
  - before: `Cobra opened 25 July (26 July was its second day, Breakout-13 p251); VII Corps made the main effort. Point is the penetration sector, not the army command post.`
  - after: `Event date: Cobra opened 25 July (26 July was its second day, Breakout-13 p251). Event definition: the First Army offensive; VII Corps made the main effort. Location: Marigny marks the Cobra penetration sector, not General Bradley's First Army command post (Breakout-13/14). Opponents: engaged_with is not exhaustive. Breakout-13 describes Panzer Lehr (with a regiment of the 5th Parachute Division attached), elements of the 353rd Division and the 5th Parachute Division in the penetration sector, with the 275th Division and 2nd SS Panzer Division reacting afterwards. Relationship: First Army operated under 21st Army Group (Montgomery) until 12th Army Group became operational on 1 August.`
- **`location_date`**
  - before: (blank)
  - after: `1944-07-25`
- **`location_basis`**
  - before: (blank)
  - after: `operational_area`
- **`location_temporal_offset_days`**
  - before: (blank)
  - after: `0`


---

## C0297: Ninth Army (1944-09-05)

**Reviewer's point.** The event type should be an activation: add activation and redesignation to the vocabulary.

**What the sources say.**
- Breakout and Pursuit p636: Ninth Army became operational at Rennes on 5 September. Pogue ch. 15: assigned to 12th Army Group.

**Decision: agree.** `activation` and `redesignation` were added to `event_type`. The row is `activation`; the 12th Army Group link is `assigned` from 5 September. The same change was made for the other "became operational" rows (12th Army Group, Third Army, 6th Army Group).

**Before and after.**

_C0297_

- **`command_relationships`**
  - before: `US 12th Army Group: organic`
  - after: `US 12th Army Group: assigned from 1944-09-05`
- **`event_type`**
  - before: `command_change`
  - after: `activation`
- **`notes`**
  - before: `Green Book (p636): Ninth Army became operational at Rennes on 5 September; VIII Corps passed to it five days later.`
  - after: `Event date: Breakout-30 p636: Ninth Army became operational at Rennes on 5 September; VIII Corps passed to it five days later (see conflict group G013). Event definition: the army becomes operational. Relationship: assigned to 12th Army Group (Pogue, Supreme Command ch. 15). Location: Rennes, named by the Green Book for the headquarters; point is the town centroid.`
- **`location_date`**
  - before: (blank)
  - after: `1944-09-05`
- **`location_basis`**
  - before: (blank)
  - after: `town_centroid`
- **`location_temporal_offset_days`**
  - before: (blank)
  - after: `0`


---

## C0315 / C0316: VIII Corps to Ninth Army, conflict group G013

**Reviewer's point.** Keep 10 September preferred as the operational-control transfer; label 5 September as the reported administrative/assignment-table date, with relationship operational_control, not organic.

**What the sources say.**
- Breakout and Pursuit p636: Ninth Army operational at Rennes on 5 September; VIII Corps passed to it five days later.
- CMH ETO-OB tables for the 8th and 83rd Divisions and Wikipedia: Ninth Army from 5 September. Pogue ch. 15 also has Ninth Army taking over the Brittany forces when it became operational on 5 September.

**Decision: partly agree.** 10 September stays preferred and is now `operational_control` from 10 September. The 5 September row keeps its alternate status and an `Event definition:` sentence calling it the assignment-table date. I did not make it `operational_control`: the CMH table does not say what kind of subordination it shows, so it is `unspecified_subordination` with `date_basis` `assignment_table`; and 5 September is not purely administrative (Pogue has Ninth Army taking over the Brittany forces that day). Both rows are marked `operational_area` (the Brest sector); the corps HQ is not located.

**Before and after.**

_C0315_

- **`command_relationships`**
  - before: `US Ninth Army: organic`
  - after: `US Ninth Army: unspecified_subordination from 1944-09-05`
- **`notes`**
  - before: `CMH ETO-OB assignment tables for the 8th and 83rd Divisions and Wikipedia date VIII Corps to Ninth Army from 5 September, the day Ninth Army became operational. Alternate to the 10 September date in Breakout-30 p636.`
  - after: `Event date: CMH ETO-OB assignment tables for the 8th and 83rd Divisions and Wikipedia date VIII Corps to Ninth Army from 5 September. Event definition: the assignment-table date, the day Ninth Army became operational and (per Pogue, Supreme Command ch. 15) took over the Brittany forces; the Green Book places the actual passing of VIII Corps to Ninth Army control on 10 September (preferred row). Relationship: the tables do not distinguish assigned from attached (unspecified_subordination). Location: the Brest sector; the corps headquarters is not located.`
- **`location_date`**
  - before: (blank)
  - after: `1944-09-05`
- **`location_basis`**
  - before: (blank)
  - after: `operational_area`
- **`location_temporal_offset_days`**
  - before: (blank)
  - after: `0`

_C0316_

- **`command_relationships`**
  - before: `US Ninth Army: organic`
  - after: `US Ninth Army: operational_control from 1944-09-10`
- **`notes`**
  - before: `Breakout-30 p636 places the transfer on 10 September, five days after Ninth Army became operational at Rennes. CMH ETO-OB division tables give 5 September (alternate row).`
  - after: `Event date: Breakout-30 p636 places the transfer on 10 September, five days after Ninth Army became operational at Rennes. Event definition: VIII Corps passes to Ninth Army operational control (preferred); the 5 September row (alternate) is the assignment-table date. Relationship: operational_control from 10 September. Location: the Brest sector; the corps headquarters is not located.`
- **`location_date`**
  - before: (blank)
  - after: `1944-09-10`
- **`location_basis`**
  - before: (blank)
  - after: `operational_area`
- **`location_temporal_offset_days`**
  - before: (blank)
  - after: `0`


---

## C0317 / C0318: Brest, conflict group G014

**Reviewer's point.** Two capitulations on 18 September; Ramcke escaped to Crozon; reword the activity precisely; keep 18 September preferred.

**What the sources say.**
- Breakout and Pursuit p636 and p650: the garrison capitulated in two parts on 18 September (von der Mosel to the 29th Division at Recouvrance, Pietzonka to the 2nd Division in the east of the city); Ramcke had withdrawn to the Crozon peninsula and surrendered on 19 September.

**Decision: agree.** C0317 now reads "receiving the capitulation of German forces in eastern Brest and Recouvrance" and stays preferred. C0318 (19 September, Wikipedia) stays as the alternate with an `Event definition:` saying 19 September is Ramcke's surrender on Crozon, not a second capture of the city. Both rows now carry the Ninth Army `operational_control` link (from 10 September).

**Before and after.**

_C0317_

- **`command_relationships`**
  - before: `US Ninth Army: organic`
  - after: `US Ninth Army: operational_control from 1944-09-10`
- **`current_activity`**
  - before: `Brest garrison surrenders in two parts to 29th and 2nd Divisions`
  - after: `receiving the capitulation of German forces in eastern Brest and Recouvrance`
- **`notes`**
  - before: `Breakout-30 p650: both German capitulations at Brest occurred on 18 September (Recouvrance to the 29th Division, the east of the city to the 2nd Division). Wikipedia gives 19 September (alternate row).`
  - after: `Event date: Breakout-30 p650: both German capitulations at Brest occurred on 18 September (Recouvrance to the 29th Division, the east of the city to the 2nd Division); the garrison commanders were von der Mosel (29th Division sector) and Pietzonka (2nd Division sector). Event definition: surrender of the German forces holding Brest and Recouvrance. Ramcke, the fortress commander, had escaped to the Crozon peninsula and surrendered there on 19 September (see the alternate row), so the garrison did not surrender in a single act. Relationship: Ninth Army (VIII Corps passed to it on 10 September).`
- **`location_date`**
  - before: (blank)
  - after: `1944-09-18`
- **`location_basis`**
  - before: (blank)
  - after: `documented_on_date`
- **`location_temporal_offset_days`**
  - before: (blank)
  - after: `0`

_C0318_

- **`command_relationships`**
  - before: `US Ninth Army: organic`
  - after: `US Ninth Army: operational_control from 1944-09-10`
- **`notes`**
  - before: `Wikipedia: VIII Corps liberated Brest on 19 September. Alternate to the 18 September surrender date in Breakout-30 p650.`
  - after: `Event date: Wikipedia gives 19 September for the liberation of Brest. Event definition: 19 September is the day Ramcke surrendered on the Crozon peninsula, ending organised resistance in the Brest area (Breakout-30 p650); it is not a separate capture of the city, which capitulated on 18 September (preferred row). The point stays at Brest; Crozon is about 20 km to the south-west.`
- **`location_date`**
  - before: (blank)
  - after: `1944-09-19`
- **`location_basis`**
  - before: (blank)
  - after: `documented_on_date`
- **`location_temporal_offset_days`**
  - before: (blank)
  - after: `0`


---

## C0333: XIX Corps (1944-08-29)

**Reviewer's point.** Record three subordinate relationships with effective dates (79th, 30th, 2nd Armored); distinguish the front-line point at Mantes from the corps HQ.

**What the sources say.**
- Breakout and Pursuit p672: at noon on 29 August XIX Corps took command of the three divisions east of the Seine. The divisions' own rows already carry the XIX Corps link from 29 August (C0452, C0421, C0230).

**Decision: agree.** `composing_units` lists the three divisions (all effective 29 August, with the dates held in the divisions' own rows, since the data model records the link on the subordinate's row). The point is relabelled a bridgehead-area `sector_center` (10 km, confidence 0.5, `operational_area`); the corps HQ on that date is not documented in the sources used. Note: the table dates 2nd Armored Division to XIX Corps from 19 August (C0229), earlier than the Green Book's 29 August for the divisions east of the Seine; this is not reconciled.

**Before and after.**

_C0333_

- **`command_relationships`**
  - before: `US First Army: organic`
  - after: `US First Army: assigned`
- **`location_name`**
  - before: `Mantes-Gassicourt bridgehead, Yvelines`
  - after: `Mantes-Gassicourt bridgehead area (Seine), Yvelines`
- **`location_represents`**
  - before: `front_line_point`
  - after: `sector_center`
- **`precision_km`**
  - before: `5`
  - after: `10`
- **`composing_units`**
  - before: `attached: 79th Infantry Division; 30th Infantry Division; 2nd Armored Division`
  - after: `79th Infantry Division; 30th Infantry Division; 2nd Armored Division`
- **`confidence`**
  - before: `0.7`
  - after: `0.5`
- **`notes`**
  - before: `Breakout-31 p672: at noon on 29 August, as XV Corps headquarters started for an assembly area southeast of Paris, Corlett's XIX Corps took command of the three divisions east of the Seine and moved 2nd Armored Division to the lead.`
  - after: `Event date: Breakout-31 p672: at noon on 29 August, as XV Corps headquarters started for an assembly area southeast of Paris, Corlett's XIX Corps took command of the three divisions east of the Seine and moved 2nd Armored Division to the lead. Event definition: XIX Corps takes command of the 79th, 30th and 2nd Armored Divisions, all effective 29 August (the divisions' own rows carry the matching corps entries). Location: the bridgehead area is the corps sector, not the corps command post, which is not located in the sources used (the earlier point was a front-line point at Mantes). Relationship: XIX Corps assigned to First Army.`
- **`location_date`**
  - before: (blank)
  - after: `1944-08-29`
- **`location_basis`**
  - before: (blank)
  - after: `operational_area`
- **`location_temporal_offset_days`**
  - before: (blank)
  - after: `0`


---

## C0213: XVIII Airborne Corps (1944-08-25)

**Reviewer's point.** Event type redesignation; keep identity continuity (XVIII Corps to XVIII Airborne Corps); give First Allied Airborne Army a stable unit id; time-effective relationships for the 82nd and 101st; do not imply it was operational as an airborne corps on the 12 August assignment date.

**What the sources say.**
- Wikipedia, XVIII Airborne Corps: constituted 14 January 1942 as II Armored Corps, redesignated XVIII Corps 9 October 1943, deployed to Europe 17 August 1944 and became XVIII Airborne Corps on 25 August 1944 at Ogbourne St George; the 82nd and 101st are listed as assigned from 12 August 1944 (previously VII Corps); the corps did not take part in Market Garden.
- Wikipedia, 1st Allied Airborne Army: activated 2 August 1944 under Brereton, over XVIII Airborne Corps and British I Airborne Corps.

**Decision: agree.** Event type `redesignation`; the unit note in `units.csv` records the identity chain. `ALL-FAAA-001A` (First Allied Airborne Army, placeholder) was added and used as the corps' parent (`unspecified_subordination`, because the CMH table does not separate assigned from attached). The notes state that the 12 August assignment was made while the corps was still XVIII Corps and still in the United States. The time-effective links for the 82nd and 101st sit on the divisions' rows (XVIII Airborne Corps `assigned` from 12 August to 17 September, British I Airborne Corps `operational_control` from 17 September).

**Before and after.**

_C0213_

- **`parent_unit_id`**
  - before: `unknown`
  - after: `ALL-FAAA-001A`
- **`command_relationships`**
  - before: `First Allied Airborne Army: organic`
  - after: `First Allied Airborne Army: unspecified_subordination`
- **`precision_km`**
  - before: `3`
  - after: `5`
- **`composing_units`**
  - before: `attached: 82nd Airborne Division; 101st Airborne Division`
  - after: `82nd Airborne Division; 101st Airborne Division`
- **`event_type`**
  - before: `other`
  - after: `redesignation`
- **`current_activity`**
  - before: `redesignated XVIII Airborne Corps at Ogbourne St George with 82nd and 101st Airborne Divisions`
  - after: `redesignated XVIII Airborne Corps at Ogbourne St George with the 82nd and 101st Airborne Divisions`
- **`notes`**
  - before: `Wikipedia: XVIII Corps deployed to Europe on 17 August and became XVIII Airborne Corps on 25 August 1944 at Ogbourne St George. CMH tables assign 82nd and 101st Airborne Divisions to it from 12 August. Corps was in England until Market Garden.`
  - after: `Event date: Wikipedia: XVIII Corps deployed to Europe on 17 August and became XVIII Airborne Corps on 25 August 1944 at Ogbourne St George (assuming command of the 82nd and 101st Airborne Divisions). Event definition: redesignation of the same headquarters (II Armored Corps, 1942; XVIII Corps, 9 October 1943; XVIII Airborne Corps, 25 August 1944; see units.csv note). Relationship: the CMH tables assign the 82nd and 101st Airborne Divisions to the corps from 12 August, when it was still the XVIII Corps and still in the United States; it is not an airborne corps headquarters in Europe before 25 August. The corps was assigned to First Allied Airborne Army (CMH tables, not distinguished as assigned or attached). It was in England during Market Garden, where British I Airborne Corps held operational control of the US airborne divisions.`
- **`location_date`**
  - before: (blank)
  - after: `1944-08-25`
- **`location_basis`**
  - before: (blank)
  - after: `town_centroid`
- **`location_temporal_offset_days`**
  - before: (blank)
  - after: `0`


---

## C0217: 82nd Airborne Division (1944-09-17)

**Reviewer's point.** Separate the landing (drop zones around Groesbeek, 12:50-14:00) from the division CP (about 1,000 yards west of Groesbeek at 17:00) and give new coordinates; distinguish attachment to British I Airborne Corps from the First Allied Airborne Army structure.

**What the sources say.**
- TracesOfWar, "Champion CP – Groesbeek", and the 82nd Airborne Division "Operation Market" historical data (CGSC): parachute lift 12:50-14:00, division HQ party jumped about 13:06, gliders about 13:50 on DZ N; CP CHAMPION set up about 17:00, about 1,000 yards (1 km) west of Groesbeek, in the woods between Groesbeek and Molenhoek near Hotel De Wolfsberg.
- Wikipedia, XVIII Airborne Corps: British I Airborne Corps held operational control of the US airborne divisions in Market Garden; the XVIII Airborne Corps stayed in England.

**Decision: agree.** C0217 is now the landing: a Groesbeek landing-area point (10 km, `operational_area`, confidence 0.5). A new row **C0481** (`hq_move`) records the CHAMPION command post at the Hotel De Wolfsberg (3 km, confidence 0.5; the exact site is not surveyed). Relationships on C0217: British I Airborne Corps `operational_control` from 17 September, XVIII Airborne Corps `assigned` 12 August to 17 September, First Allied Airborne Army `unspecified_subordination`; the parent is now I Airborne Corps. The same split was applied to the 101st Airborne Division (C0220 landing, new row **C0482** for the Zon CP) because that row had the same defect.

**Before and after.**

_C0217_

- **`parent_unit_id`**
  - before: `unknown`
  - after: `UK-ABN-001C`
- **`command_relationships`**
  - before: `British I Airborne Corps: attached from 1944-09-17; First Allied Airborne Army: organic`
  - after: `British I Airborne Corps: operational_control from 1944-09-17; US XVIII Airborne Corps: assigned from 1944-08-12 to 1944-09-17; First Allied Airborne Army: unspecified_subordination`
- **`latitude`**
  - before: `51.8475`
  - after: `51.7741`
- **`longitude`**
  - before: `5.8638`
  - after: `5.9305`
- **`location_name`**
  - before: `Nijmegen (vicinity south), Gelderland, Netherlands`
  - after: `Drop zones around Groesbeek (DZ N south of Groesbeek), Gelderland, Netherlands`
- **`location_represents`**
  - before: `headquarters`
  - after: `sector_center`
- **`confidence`**
  - before: `0.7`
  - after: `0.5`
- **`source`**
  - before: `https://web.archive.org/web/2018/http://www.history.army.mil/documents/ETO-OB/82ABD-ETO.htm ; coords: OpenStreetMap Nominatim (Nijmegen (vicinity south), Gelderland, Netherlands)`
  - after: `https://web.archive.org/web/2018/http://www.history.army.mil/documents/ETO-OB/82ABD-ETO.htm | https://www.tracesofwar.com/sights/155485/Champion-CP.htm | http://cgsc.contentdm.oclc.org/u?/p4013coll8,387 ; coords: OpenStreetMap Nominatim (Groesbeek, Gelderland)`
- **`current_activity`**
  - before: `parachute and glider landing near Groesbeek and Nijmegen (Market Garden)`
  - after: `parachute and glider landing on drop zones around Groesbeek (Market Garden)`
- **`notes`**
  - before: `CMH ETO-OB CP list: Nijmegen (vicinity S) on 17 September 1944. Division moved under British I Airborne Corps on 17 September per the CMH assignment table; the American XVIII Airborne Corps headquarters remained in England.`
  - after: `Event date: 17 September 1944; the 82nd's parachute lift dropped 12:50–14:00, the division headquarters party jumped about 13:06 and the gliders landed about 13:50 on DZ N south of Groesbeek (TracesOfWar; 82nd Airborne Division, Operation Market historical data). Event definition: the airborne landing. The division command post (CHAMPION, about 1,000 yards west of Groesbeek, set up about 17:00) is a separate row (hq_move). Location: the point is the Groesbeek landing area (OpenStreetMap Nominatim, Groesbeek centroid), not the CMH command-post vicinity of Nijmegen that this row used before. Relationship: for Market Garden British I Airborne Corps held operational control of the 82nd and 101st Airborne Divisions; the CMH table shows the division as under I Airborne Corps from 17 September. XVIII Airborne Corps (assigned from 12 August, ended 17 September per Wikipedia) stayed in England. First Allied Airborne Army was the higher Allied command over both corps.`
- **`location_date`**
  - before: (blank)
  - after: `1944-09-17`
- **`location_basis`**
  - before: (blank)
  - after: `operational_area`
- **`location_temporal_offset_days`**
  - before: (blank)
  - after: `0`

_C0481_

_New row. Fields:_ `event_type` = hq_move; `date` = 1944-09-17; `location_name` = CHAMPION command post, about 1 km west of Groesbeek (near Hotel De Wolfsberg), Gelderland, Netherlands; `latitude` = 51.7748; `longitude` = 5.9267; `location_represents` = headquarters; `precision_km` = 3; `confidence` = 0.5; `location_basis` = documented_on_date; `current_activity` = division command post CHAMPION established west of Groesbeek
- `command_relationships`: British I Airborne Corps: operational_control from 1944-09-17; US XVIII Airborne Corps: assigned from 1944-08-12 to 1944-09-17; First Allied Airborne Army: unspecified_subordination
- `notes`: Event date: 17 September 1944, about 17:00 (TracesOfWar, "Champion CP – Groesbeek"; 82nd Airborne Division, Operation Market historical data). Event definition: the division command post CHAMPION is set up in the woods between Groesbeek and Molenhoek, about 1,000 yards (1 km) west of the village, after the 12:50–14:00 landing (separate row C0217). Location: coordinate is the Hotel De Wolfsberg on the Mooksebaan, the landmark named for the site (OpenStreetMap Nominatim); the exact command post site is not surveyed. Relationship: as on C0217.


---

## C0243 / C0244: 4th Armored Division landing, conflict group G012

**Reviewer's point.** Keep both rows; they may be different phases (first element landed, main body, arrival completed, HQ established); the 704th Tank Destroyer Battalion boarded 11 July and landed 12 July; do not reuse the Mesnil-Saint-Martin point for a landing date without evidence.

**What the sources say.**
- USHMM "The 4th Armored Division during World War II" and Wikipedia: the division landed at Utah Beach on 11 July 1944. CMH ETO-OB chronology: arrived on the Continent 13 July, CP "Mesnil-St-Martin (1 mi SW)" on 13 July, Méautis on 18 July.
- tankdestroyer.net (citing Yeide): the 704th Tank Destroyer Battalion landed at Utah on 13 July. I found no source for the reviewer's "boarded 11 July, landed 12 July"; a 37th Tank Battalion report has elements in the division assembly area on 12 July.
- The audit found that "Mesnil-St-Martin" had been geocoded to a hamlet near Percy, about 50 km from the beaches: see C0244, C0245, C0269 below.

**Decision: partly agree.** Both rows stay. Each now has an `Event definition:` sentence (first landing at Utah Beach on 11 July, against CMH's arrival with the CP established on 13 July). The 11 July row now points at Utah Beach (landing area, confidence 0.5), not the CP. I did not confirm the reviewer's 704th battalion dates. Separately the Mesnil-St-Martin point itself was unreliable, so C0244, C0245 (4th Armored) and C0269 (6th Armored, same CMH place on 18 July) keep the point only at 50 km and confidence 0.3 (C0244 `inferred`; C0245 and C0269 keep their nearest-command-post basis) until the place is identified.

**Before and after.**

_C0243_

- **`command_relationships`**
  - before: `US XV Corps: attached from 1944-04-20; US Third Army: organic`
  - after: `US XV Corps: unspecified_subordination from 1944-04-20; US Third Army: unspecified_subordination from 1944-04-20`
- **`latitude`**
  - before: `48.9759`
  - after: `49.4157`
- **`longitude`**
  - before: `-1.2867`
  - after: `-1.1747`
- **`location_name`**
  - before: `vicinity of Mesnil-St-Martin, Manche`
  - after: `Utah Beach, Manche (landing area)`
- **`location_represents`**
  - before: `headquarters`
  - after: `sector_center`
- **`precision_km`**
  - before: `10`
  - after: `5`
- **`confidence`**
  - before: `0.3`
  - after: `0.5`
- **`source`**
  - before: `https://en.wikipedia.org/wiki/4th_Armored_Division_(United_States) ; coords: OpenStreetMap Nominatim (Mesnil-Saint-Martin, Manche, France)`
  - after: `https://en.wikipedia.org/wiki/4th_Armored_Division_(United_States) | https://encyclopedia.ushmm.org/content/en/article/the-4th-armored-division ; coords: OpenStreetMap Nominatim (Utah Beach, Sainte-Marie-du-Mont)`
- **`notes`**
  - before: `Wikipedia: the 4th Armored Division landed at Utah Beach on 11 July 1944. CMH ETO-OB gives 13 July (preferred row). Location reused from the CMH CP in the preferred row.`
  - after: `Event date: USHMM and Wikipedia: the 4th Armored Division landed at Utah Beach on 11 July 1944. Event definition: the first landing of the division at Utah Beach. The 13 July row (preferred) is the CMH ETO-OB chronology date for arrival on the Continent, with the division command post at Mesnil-St-Martin on that date; the two may describe different phases (first elements ashore, main body ashore, command post established) rather than a disagreement. A reviewer said the 704th Tank Destroyer Battalion boarded 11 July and landed 12 July; that was not confirmed (tankdestroyer.net, citing Yeide, has the battalion landing on 13 July). Location: Utah Beach area (OpenStreetMap Nominatim); the Mesnil-St-Martin command post this row reused belongs to the 13 July row only.`
- **`location_date`**
  - before: (blank)
  - after: `1944-07-11`
- **`location_basis`**
  - before: (blank)
  - after: `operational_area`
- **`location_temporal_offset_days`**
  - before: (blank)
  - after: `0`

_C0244_

- **`command_relationships`**
  - before: `US XV Corps: attached from 1944-04-20; US Third Army: organic`
  - after: `US XV Corps: unspecified_subordination from 1944-04-20; US Third Army: unspecified_subordination from 1944-04-20`
- **`location_name`**
  - before: `vicinity of Mesnil-St-Martin, Manche`
  - after: `vicinity of Mesnil-St-Martin, Manche (unresolved CMH place name)`
- **`precision_km`**
  - before: `10`
  - after: `50`
- **`confidence`**
  - before: `0.5`
  - after: `0.3`
- **`notes`**
  - before: `CMH ETO-OB chronology: arrived on the Continent 13 July 1944. CMH ETO-OB lists the command post at vicinity of Mesnil-St-Martin, Manche on this date. CMH gives the CP only as a vicinity of the town. Wikipedia gives 11 July for the Utah Beach landing (alternate row).`
  - after: `Event date: CMH ETO-OB chronology: arrived on the Continent 13 July 1944. Event definition: arrival of the division on the Continent as CMH records it, with the command post at the vicinity of Mesnil-St-Martin, Manche, listed on this date (CMH gives the CP only as a vicinity of the town). Wikipedia and USHMM give 11 July for the Utah Beach landing (alternate row): the rows may describe different phases of the landing. Location caveat: the CMH CP name "Mesnil-St-Martin" could not be resolved to a Manche commune with certainty. The Nominatim match used before (about 49.0, -1.29, near Percy) lies roughly 50 km from the landing beaches and is inconsistent with the later CP at Méautis (17-18 July) and with a unit that had just landed at Utah Beach (Coutances was not taken until 28 July); the point is therefore unreliable and is kept only as a very wide inferred point. The unit was in the Cotentin beachhead assembly area (a 37th Tank Battalion report puts the division assembly area in use on 12 July).`
- **`location_date`**
  - before: (blank)
  - after: `1944-07-13`
- **`location_basis`**
  - before: (blank)
  - after: `inferred`
- **`location_temporal_offset_days`**
  - before: (blank)
  - after: `0`


---

## C0457: 80th Infantry Division (1944-08-03)

**Reviewer's point.** Clarify attached versus organic (Third Army is a higher command, not organic); classify relationships by dates.

**What the sources say.**
- CMH ETO-OB 80th Division page: arrived on the Continent 3 August, CP at the vicinity of St-Jores on that date; the assignment table shows XII Corps and Third Army from 1 August and does not separate assigned from attached.

**Decision: agree.** Both links are now `unspecified_subordination` with `effective_from` 1 August and `date_basis` `assignment_table` (they were `attached` and `organic`). The notes say Third Army is a higher command, not an organic parent. Coordinate and date unchanged (the CP is listed on the row date; `location_basis` `town_centroid`).

**Before and after.**

_C0457_

- **`command_relationships`**
  - before: `US XII Corps: attached from 1944-08-01; US Third Army: organic`
  - after: `US XII Corps: unspecified_subordination from 1944-08-01; US Third Army: unspecified_subordination from 1944-08-01`
- **`notes`**
  - before: `CMH ETO-OB chronology: arrived on the Continent 3 August 1944. CMH ETO-OB lists the command post at vicinity of St-Jores, Manche on this date. CMH gives the CP only as a vicinity of the town.`
  - after: `Event date: CMH ETO-OB chronology: arrived on the Continent 3 August 1944. Event definition: arrival of the division. Location: CMH lists the command post at the vicinity of St-Jores, Manche on this date; CMH gives the CP only as a vicinity of the town. Relationship: the CMH assignment table shows XII Corps from 1 August and Third Army without distinguishing assigned from attached (both unspecified_subordination); Third Army is a higher command, not an organic parent.`
- **`location_date`**
  - before: (blank)
  - after: `1944-08-03`
- **`location_basis`**
  - before: (blank)
  - after: `town_centroid`
- **`location_temporal_offset_days`**
  - before: (blank)
  - after: `0`


---

## C0479: 94th Infantry Division (1944-09-05)

**Reviewer's point.** The row is dated 5 September but the location uses the CP of about 8 September: mark it later-dated, inferred or unlocated; note the Lorient duties in mid-September.

**What the sources say.**
- CMH ETO-OB 94th Division page (CP at Ste-Marie-du-Mont); Breakout and Pursuit p637: the division took over the Lorient and Saint-Nazaire containment in mid-September.

**Decision: agree.** `location_basis` `nearest_later_command_post`, `location_date` 1944-09-08, offset +3. Confidence stays 0.3 and precision 25 km. The notes say the Lorient duty came after this staging period. Relationships `unspecified_subordination`.

**Before and after.**

_C0479_

- **`command_relationships`**
  - before: `US-COR-013C: attached from 1944-08-28; US Ninth Army: organic`
  - after: `US XIII Corps: unspecified_subordination from 1944-08-28; US Ninth Army: unspecified_subordination from 1944-08-28`
- **`notes`**
  - before: `CMH ETO-OB chronology: arrived on the Continent 5 September 1944. Location is the nearest listed CP at Ste-Marie-du-Mont, Manche (CMH ETO-OB), 3 days after the row date; the division position on the day is not stated.`
  - after: `Event date: CMH ETO-OB chronology: arrived on the Continent 5 September 1944. Location: the coordinate is the CP at Ste-Marie-du-Mont listed by CMH three days later (8 September), not the position on 5 September, which is not stated. Context: the division took over the containment of the Lorient and Saint-Nazaire pockets in mid-September (Breakout-30 p637), after this staging period. Relationship: the CMH table does not distinguish assigned from attached.`
- **`location_date`**
  - before: (blank)
  - after: `1944-09-08`
- **`location_basis`**
  - before: (blank)
  - after: `nearest_later_command_post`
- **`location_temporal_offset_days`**
  - before: (blank)
  - after: `3`


---

## C0388: 26th Infantry Division (1944-09-07)

**Reviewer's point.** Keep 7 September and raise date confidence (the division history says it landed 7 September at Cherbourg/Utah); the Valognes coordinates are not verified; investigate the 19 September discrepancy.

**What the sources say.**
- CMH ETO-OB 26th Division page: every command appointment is dated 7 September; the CP list gives the Valognes staging area on 7 September; the chronology shows "Arrived Continent (D+105)" 19 September (D+105 is 19 September, so it is internally consistent).
- EUCMH, 26th Infantry Division history: left Camp Shanks 26 August, landed at Cherbourg and Utah Beach on 7 September (first convoy direct from the United States), moved to the Valognes staging area and set up headquarters at Bourg de Lestre.

**Decision: agree.** 7 September is kept. The confidence is already at the 0.7 cap for a preferred row, so it is not raised; the notes now cite both sources. The 19 September date is described as a separate CMH event definition (probably the division closing in the staging area), not corroborated elsewhere. The Valognes point is marked `town_centroid` and widened from 3 to 5 km; the notes record the Bourg de Lestre headquarters. The coordinates remain unverified.

**Before and after.**

_C0388_

- **`command_relationships`**
  - before: `US-COR-003C: attached from 1944-09-05; US Ninth Army: organic`
  - after: `US III Corps: unspecified_subordination from 1944-09-05; US Ninth Army: unspecified_subordination from 1944-09-05`
- **`precision_km`**
  - before: `3`
  - after: `5`
- **`source`**
  - before: `https://web.archive.org/web/2018/http://www.history.army.mil/documents/ETO-OB/26ID-ETO.htm ; coords: OpenStreetMap Nominatim (Valognes, Manche, France)`
  - after: `https://web.archive.org/web/2018/http://www.history.army.mil/documents/ETO-OB/26ID-ETO.htm | https://eucmh.com/2020/03/27/26-id-yankee-ww-2-eto/ ; coords: OpenStreetMap Nominatim (Valognes, Manche, France)`
- **`notes`**
  - before: `CMH ETO-OB lists the 26th Division CP at the Valognes staging area on 7 September (the division landed directly in France); the chronology table gives 19 September as the Continent arrival date, an internal inconsistency in the source.`
  - after: `Event date: 7 September 1944 is kept: the CMH command and staff table dates every command appointment to 7 September, CMH lists the CP at the Valognes staging area on that date, and the division history (EUCMH, from the division record) says the division landed at Cherbourg and Utah Beach on 7 September as the first convoy direct from the United States. The CMH chronology table gives "Arrived Continent (D+105)", 19 September 1944 (D+105 is 19 September, so the figure is internally consistent): it appears to be a separate CMH event definition, probably the date the division closed in the staging area, and is not corroborated elsewhere. Location: Valognes is the CMH-listed staging area; the commune centroid is used. The EUCMH history says the division established its headquarters at Bourg de Lestre in the staging area, so the headquarters may have been a few kilometres east of Valognes. The staging-area coordinates are not independently verified. Relationship: the CMH table does not distinguish assigned from attached.`
- **`location_date`**
  - before: (blank)
  - after: `1944-09-07`
- **`location_basis`**
  - before: (blank)
  - after: `town_centroid`
- **`location_temporal_offset_days`**
  - before: (blank)
  - after: `0`


---

## C0406: 29th Infantry Division (1944-08-19)

**Reviewer's point.** The CP coordinate is from a later date (assembling south of Lannilis by 23 August); retain the attachment; reduce location confidence independently.

**What the sources say.**
- Breakout and Pursuit ch. 30: the 29th Division assembled just south of Lannilis four days after 19 August (23 August). CMH lists the CP at Plouguin three days after the row date (22 August).

**Decision: agree.** `location_basis` `nearest_later_command_post`, `location_date` 1944-08-22, offset +3; the notes cite the Lannilis assembly. The attachment to VIII Corps is kept (now `unspecified_subordination` as in every table-derived link). The location confidence was already 0.3 (25 km), so it is not lowered further; there is no separate location-confidence column.

**Before and after.**

_C0406_

- **`command_relationships`**
  - before: `US VIII Corps: attached from 1944-08-19; US First Army: organic`
  - after: `US VIII Corps: unspecified_subordination from 1944-08-19; US First Army: unspecified_subordination from 1944-08-19`
- **`notes`**
  - before: `CMH ETO-OB assignment table entry dated 19 August 1944. Location is the nearest listed CP at Plouguin, Finistere (CMH ETO-OB), 3 days after the row date; the division position on the day is not stated.`
  - after: `Event date: CMH ETO-OB assignment table entry dated 19 August 1944 (division passes to VIII Corps). Location: the coordinate is the CP at Plouguin listed by CMH three days later (22 August); the division position on 19 August is not stated. Breakout-30 says the 29th Division assembled just south of Lannilis four days after 19 August (23 August), about 9 km from Plouguin. Plouguin is kept as a low-confidence point; the attachment to VIII Corps is supported separately by the CMH table. Relationship: the CMH table does not distinguish assigned from attached.`
- **`location_date`**
  - before: (blank)
  - after: `1944-08-22`
- **`location_basis`**
  - before: (blank)
  - after: `nearest_later_command_post`
- **`location_temporal_offset_days`**
  - before: (blank)
  - after: `3`


---

## C0300: VI Corps, Operation Dragoon (1944-08-15)

**Reviewer's point.** Three landing sectors (3rd Division Alpha, 45th Delta, 36th Camel); keep the corps row as a broad operational area but note the sectors, and/or add division landing rows if missing.

**What the sources say.**
- Wikipedia, Operation Dragoon: 3rd Division at Alpha, 45th at Delta, 36th at Camel (the 36th avoided Camel Red for Camel Green and Blue). Breakout/Riviera Green Book pp75-78 and p111.
- The NHHC page the reviewer names did not return the sector names to this check, so it is not cited.

**Decision: partly agree.** The corps row stays a broad operational-area point (25 km) and now names the three sectors. The division landing rows already existed (C0351 3rd Division Cavalaire, C0442 45th Division Bougnon Bay, C0436 36th Division east of Saint-Raphaël), so no rows were added.

**Before and after.**

_C0300_

- **`command_relationships`**
  - before: `US Seventh Army: organic`
  - after: `US Seventh Army: assigned`
- **`location_name`**
  - before: `Cape Saint-Tropez landing area, Var`
  - after: `Dragoon assault area (Alpha, Delta and Camel sectors), Var coast`
- **`source`**
  - before: `https://www.ibiblio.org/hyperwar/USA/USA-E-Riviera/USA-E-Riviera-5.html#page75 | https://www.ibiblio.org/hyperwar/USA/USA-E-Riviera/USA-E-Riviera-7.html | https://en.wikipedia.org/wiki/VI_Corps_(United_States) ; coords: Wikipedia (en): Saint-Tropez`
  - after: `https://www.ibiblio.org/hyperwar/USA/USA-E-Riviera/USA-E-Riviera-5.html#page75 | https://www.ibiblio.org/hyperwar/USA/USA-E-Riviera/USA-E-Riviera-7.html | https://en.wikipedia.org/wiki/VI_Corps_(United_States) | https://en.wikipedia.org/wiki/Operation_Dragoon ; coords: Wikipedia (en): Saint-Tropez`
- **`notes`**
  - before: `Riviera-5 p75–78: Truscott's VI Corps landed 3rd Division at Cavalaire Bay–Saint-Tropez, 45th across the gulf, and 36th east of Saint-Raphaël. Point is the landing area.`
  - after: `Event date: 15 August 1944 (Riviera-5 p75–78). Event definition: the VI Corps assault with three divisions in three sectors: 3rd Division on the Alpha beaches (Cavalaire Bay), 45th Division on the Delta beaches (Bougnon Bay), 36th Division on the Camel beaches east of Saint-Raphaël; the 36th avoided Camel Red and landed on Camel Green and Blue (Wikipedia, Operation Dragoon). The division landings have their own rows (C0351, C0442, C0436). Location: the point is the centre of the whole assault area at Cape Saint-Tropez (a broad operational-area point; the corps headquarters afloat is not a land position). The NHHC page named in review did not return the sector names to this check, so the sector assignments rest on the Green Book rows and Wikipedia.`
- **`location_date`**
  - before: (blank)
  - after: `1944-08-15`
- **`location_basis`**
  - before: (blank)
  - after: `operational_area`
- **`location_temporal_offset_days`**
  - before: (blank)
  - after: `0`


---

## C0244, C0245, C0269: unresolved "Mesnil-St-Martin" (found by the audit, not by the reviewer)

**Reviewer's point.** (Not raised.) The new coordinate-conflict check flagged G012 (C0243 and C0244 49.6 km apart).

**What the sources say.**
- CMH ETO-OB 4th Armored Division: CP "Mesnil-St-Martin (1 mi SW)" 13 July, Méautis 18 July. dday-overlord and a web search agree on the name. I found no Manche commune of that name; the Nominatim match near Percy is about 50 km south of Utah Beach, in ground not taken until 28 July.

**Decision: fixed as far as the sources allow.** The three rows keep the point but at precision 50 km and confidence 0.3 (C0244 `inferred`; C0245 and C0269 keep their nearest-command-post basis), and the notes explain. They are listed under "could not verify" in the systemic section.

**Before and after.**

_C0244_

- **`command_relationships`**
  - before: `US XV Corps: attached from 1944-04-20; US Third Army: organic`
  - after: `US XV Corps: unspecified_subordination from 1944-04-20; US Third Army: unspecified_subordination from 1944-04-20`
- **`location_name`**
  - before: `vicinity of Mesnil-St-Martin, Manche`
  - after: `vicinity of Mesnil-St-Martin, Manche (unresolved CMH place name)`
- **`precision_km`**
  - before: `10`
  - after: `50`
- **`confidence`**
  - before: `0.5`
  - after: `0.3`
- **`notes`**
  - before: `CMH ETO-OB chronology: arrived on the Continent 13 July 1944. CMH ETO-OB lists the command post at vicinity of Mesnil-St-Martin, Manche on this date. CMH gives the CP only as a vicinity of the town. Wikipedia gives 11 July for the Utah Beach landing (alternate row).`
  - after: `Event date: CMH ETO-OB chronology: arrived on the Continent 13 July 1944. Event definition: arrival of the division on the Continent as CMH records it, with the command post at the vicinity of Mesnil-St-Martin, Manche, listed on this date (CMH gives the CP only as a vicinity of the town). Wikipedia and USHMM give 11 July for the Utah Beach landing (alternate row): the rows may describe different phases of the landing. Location caveat: the CMH CP name "Mesnil-St-Martin" could not be resolved to a Manche commune with certainty. The Nominatim match used before (about 49.0, -1.29, near Percy) lies roughly 50 km from the landing beaches and is inconsistent with the later CP at Méautis (17-18 July) and with a unit that had just landed at Utah Beach (Coutances was not taken until 28 July); the point is therefore unreliable and is kept only as a very wide inferred point. The unit was in the Cotentin beachhead assembly area (a 37th Tank Battalion report puts the division assembly area in use on 12 July).`
- **`location_date`**
  - before: (blank)
  - after: `1944-07-13`
- **`location_basis`**
  - before: (blank)
  - after: `inferred`
- **`location_temporal_offset_days`**
  - before: (blank)
  - after: `0`

_C0245_

- **`command_relationships`**
  - before: `US VIII Corps: attached from 1944-07-15; US Third Army: organic`
  - after: `US VIII Corps: unspecified_subordination from 1944-07-15; US Third Army: unspecified_subordination from 1944-07-15`
- **`location_name`**
  - before: `vicinity of Mesnil-St-Martin, Manche`
  - after: `vicinity of Mesnil-St-Martin, Manche (unresolved CMH place name)`
- **`precision_km`**
  - before: `10`
  - after: `50`
- **`confidence`**
  - before: `0.5`
  - after: `0.3`
- **`notes`**
  - before: `CMH ETO-OB assignment table entry dated 15 July 1944. Location is the nearest listed CP at vicinity of Mesnil-St-Martin, Manche (CMH ETO-OB), 2 days before the row date; the division position on the day is not stated. CMH gives the CP only as a vicinity of the town.`
  - after: `CMH ETO-OB assignment table entry dated 15 July 1944. Location is the nearest listed CP at vicinity of Mesnil-St-Martin, Manche (CMH ETO-OB), 2 days before the row date; the division position on the day is not stated. CMH gives the CP only as a vicinity of the town. Location caveat: the CMH CP name "Mesnil-St-Martin" could not be resolved to a Manche commune with certainty. The Nominatim match used before (about 49.0, -1.29, near Percy) lies roughly 50 km from the landing beaches and is inconsistent with the later CP at Méautis (17-18 July) and with a unit that had just landed at Utah Beach (Coutances was not taken until 28 July); the point is therefore unreliable and is kept only as a very wide inferred point. The unit was in the Cotentin beachhead assembly area (a 37th Tank Battalion report puts the division assembly area in use on 12 July).`
- **`location_date`**
  - before: (blank)
  - after: `1944-07-13`
- **`location_basis`**
  - before: (blank)
  - after: `nearest_earlier_command_post`
- **`location_temporal_offset_days`**
  - before: (blank)
  - after: `-2`

_C0269_

- **`command_relationships`**
  - before: `US XX Corps: attached from 1944-03-09; Army not shown in CMH table: unknown`
  - after: `US XX Corps: unspecified_subordination from 1944-03-09; Army not shown in CMH table: unknown`
- **`location_name`**
  - before: `Le-Mesnil-St-Martin, Manche`
  - after: `Le-Mesnil-St-Martin, Manche (unresolved CMH place name)`
- **`precision_km`**
  - before: `10`
  - after: `50`
- **`confidence`**
  - before: `0.5`
  - after: `0.3`
- **`notes`**
  - before: `CMH ETO-OB chronology: arrived on the Continent 18 July 1944. Location is the nearest listed CP at Le-Mesnil-St-Martin, Manche (CMH ETO-OB), 1 days after the row date; the division position on the day is not stated.`
  - after: `CMH ETO-OB chronology: arrived on the Continent 18 July 1944. Location is the nearest listed CP at Le-Mesnil-St-Martin, Manche (CMH ETO-OB), 1 days after the row date; the division position on the day is not stated. Location caveat: the CMH CP name "Mesnil-St-Martin" could not be resolved to a Manche commune with certainty. The Nominatim match used before (about 49.0, -1.29, near Percy) lies roughly 50 km from the landing beaches and is inconsistent with the later CP at Méautis (17-18 July) and with a unit that had just landed at Utah Beach (Coutances was not taken until 28 July); the point is therefore unreliable and is kept only as a very wide inferred point. The unit was in the Cotentin beachhead assembly area (a 37th Tank Battalion report puts the division assembly area in use on 12 July).`
- **`location_date`**
  - before: (blank)
  - after: `1944-07-19`
- **`location_basis`**
  - before: (blank)
  - after: `nearest_later_command_post`
- **`location_temporal_offset_days`**
  - before: (blank)
  - after: `1`


---

### Systemic changes from the review

**1. Command relationships (schema, vocabulary, validator, data).**
- `relationship` gained `assigned`, `administrative_control`, `supporting`, `coordinating` and `unspecified_subordination` (the reviewer proposed all of these; I kept them). `organic` is now only for constituted components. Entries gained optional `effective_to` and `date_basis` (`order`, `assignment_table`, `narrative`, `inferred`; a new small vocabulary). The change is additive: no existing value was removed.
- Rule applied to **all 480 existing claims** (a one-off script that is not part of the repository; the rules are in `docs/methodology.md`): CMH-table links (corps `attached` and the table's army `organic`) became `unspecified_subordination` with `date_basis` `assignment_table` (202 corps links, 207 division-to-army links); any other `organic` link of a division, corps, army or army group to a higher headquarters became `assigned` (90 corps to army, 93 division to corps, 16 army to army group, 7 army group to other, 7 division to army, 4 army to other, 2 other to other, 1 division to army group, 1 brigade to army); 6 entries whose name was a raw unit id got a readable name; 9 entries naming First Allied Airborne Army, British I Airborne Corps or British XXX Corps got unit ids (`ALL-FAAA-001A` is new). In all, 432 of the 480 rows changed their `command_relationships` (164 of them in the 212 rows from before Batch 1).
- This is a **rule-based conversion**, not a re-reading of 480 sources: I re-read sources only for the 15 spot-checked rows and the rows the review named. `assigned` was given to links whose original source was a narrative or order-of-battle listing without attachment language; the reviewer\'s caution against turning a combined assigned/attached source into `attached` was followed (none of the table-derived links became `attached` or `assigned`).
- The 24 remaining `attached` links are from the earlier June reviews. `organic` now remains only on 13 entries (constituted components).
- Validator: new warnings for `organic` on a division, corps or army under a higher headquarters, a named higher headquarters without a unit id, an `effective_to` before the row date; errors for malformed dates and unknown `date_basis`.

**2. Location temporal provenance.**
- New optional columns `location_date`, `location_basis` (vocabulary: `documented_on_date`, `nearest_later_command_post`, `nearest_earlier_command_post`, `representative_point`, `town_centroid`, `operational_area`, `inferred`) and `location_temporal_offset_days`, appended at the end of every claim file (schema, README, build, GeoJSON properties, validator, all 101 claim files). I did **not** add `location_confidence`: `confidence`, `precision_km` and the basis already carry it, and a fifth location field would be bloat.
- Backfill: the 270 rows with a claim_id above C0212 (the 268 Batch 1 rows plus the two new rows C0481 and C0482) were filled from the wording of their notes: 128 rows list the CP on the row date (`town_centroid`, offset 0), 46 rows use a CP 1 to 3 days later or earlier (`nearest_*_command_post`, offset set), 3 rows use the last CP listed weeks earlier (82nd and 101st Airborne, C0215, C0216, C0219), the manual rows were classed by what the point stands for (`documented_on_date` 46, `operational_area` 19, `town_centroid` 7), and 23 rows named in the review were set by hand (for example `representative_point` for C0296). C0030 (First Army D-Day HQ at Bristol) was also marked. The 211 older rows are left blank: their notes do not say where the coordinate came from.
- Validator: errors for an offset that disagrees with the two dates, an offset without a date, a temporal basis without a date, and a `landing` row from a town centroid or a CP of another date; warnings for a `location_date` that differs from `date` without a temporal basis, a corps/army/army-group HQ that is only a town centroid at under 5 km, and a corps or army sector recorded as an exact `front_line_point`. I tested the rules on a scratch copy.

**3. Conflict equivalence.** G012 (landing against arrival), G013 (assignment table against operational transfer) and G014 (Brest, 18 against 19 September) were really different event definitions in part. Each row now carries an `Event definition:` sentence in `notes` (no new column). The validator warns when the rows of a group have different event types and a row lacks the sentence (it does not try to judge the other cases).

**4. Scripted audit of the 268 new rows** (`scripts/audit_command_location.py`, new, read-only; run with `--ids` for the claim ids):

| pattern | before the fixes | after |
|---|---|---|
| coordinate from a different date | 49 rows, unlabelled | 49 rows labelled with `location_date` and offset |
| corps/army/army-group HQ that is only a town centroid | 7 rows, 2 at under 5 km (C0290 3 km, C0295 3 km) | 7 rows flagged `town_centroid`; the 2 widened to 5 km; 3 more became real HQ points (C0223, C0222, C0289) |
| `organic` for a division, corps or army under a higher HQ | 221 entries | 0 (converted by rule) |
| corps or army sector recorded as an exact `front_line_point` (5 km or less) | 8 rows (C0323, C0325, C0327, C0329, C0330, C0336, C0337, C0339) | relabelled `sector_center` at 10 km, confidence capped at 0.5 |
| landing row with an HQ point | 3 new rows (C0217, C0220, C0243) plus the old C0030 | the 3 fixed (landing-area points; CP rows C0481 and C0482 added); C0030 kept on purpose (the army HQ in England controlled the landing) and annotated |
| named higher HQ without a unit id | 9 entries | 0 |
| wrong geocode found | none expected | Mesnil-St-Martin (C0244, C0245, C0269): kept as 50 km, 0.3 |

The audit also reports counts per pattern for all 482 claims: 213 rows now carry `unspecified_subordination`, 141 rows a headquarters at a town centroid, 1 row an `inferred` point.

**Could not be verified, left flagged:**
- The Army "Essential to Success" page cited for the 12th Army Group (could not be opened) and the NHHC Dragoon page (did not return the sector names): neither is cited.
- The reviewer\'s 704th Tank Destroyer Battalion dates (boarded 11 July, landed 12 July): the sources I found say 13 July.
- Exact sites: the Palais de la Foire in Lyon (approximate point), the Néhou orchard (town centroid; web sources only), the CHAMPION command post (Hotel De Wolfsberg as the landmark), the 101st landing zones (centre point), the 26th Division headquarters at Bourg de Lestre (not used as the coordinate).
- Headquarters not located: XIX Corps on 29 August, Seventh Army on 15 September, VIII Corps on 5 and 10 September, First Army on 25 July.
- Mesnil-St-Martin (three rows).
- 2nd Armored Division and XIX Corps: the CMH table has the division under XIX Corps from 19 August; the Green Book has XIX Corps taking command of the divisions east of the Seine on 29 August. Not reconciled.
- Older rows: `location_basis` is blank on 211 rows; division-to-corps links from before Batch 1 were converted by rule, not re-sourced; whether each `assigned` link was an assignment or an attachment is not re-checked.
- Not implemented: a "confidence shared by rows with different evidence" validator check (no testable definition) and a separate `location_confidence` column.
- Not started: Batch 2 (V, VII, XII, XV and XX Corps transitions; Brittany army transitions).

---

## Not changed, but noticed

- C0131 was found here and is now fixed (section above).
- The reviewer's text was cut off for C0057, C0184, C0141 (headings only) and C0084 (one sentence); anything beyond the excerpt is not covered here.

## Follow-up commits

The "US batch 1: Jul-Sep 1944" commit adds the 268 claims and the section above; it changes no existing claim. The "before" values above are from commit `a27cd35`; the "after" values are the final data. After the first correction commit (`4b5eef9`), the guardrails commit made four small data edits so the rows follow the new rules: C0084 `current_activity` shortened to 118 characters (the earlier wording joined two actions); C0057 `strength_json` gained `"scope":"sub_force"`; C0141 and C0001 `attached` entries gained `effective_from` (`1944-06-19` and `1944-06-06`). The "Fix C0131 coordinates" commit then corrected C0131 and added the `unknown` standing-parent entry to C0141 (see the C0131 section). The "Reclassify attached relationships for airborne divisions" commit then changed 13 more rows (see the section above) and removed the sentence in C0131's notes about its VII Corps link. The "Backfill strength scope; reclassify 79th/90th relationships" commit then added `scope` to 10 rows, changed the 79th Division rows (C0087, C0140, C0168, C0193), added `effective_from` to C0142, C0112 and C0130, and added the unit `US-ARMY-003A` (Third Army, `parent_only`). The "Resolve scope for C0018 and C0027; require scope" commit then resolved C0018 and C0027 and made `scope` mandatory (see the scope section). The "Resolve G004 coordinate gap" commit then changed C0067 and C0081 (see the G004 section). The "Add Western Front unit placeholders" commit then added 266 placeholder units and the unit-table columns, validator checks and coverage tracker (see the placeholder section); it changed no claim row. The reclassification table in the airborne section uses the commit before it (`63a86c3^`) as "before"; the table in the 79th/90th section uses `63a86c3`.

The "Apply Batch 1 review corrections; command and location-date semantics" commit implements the section "Batch 1 review" above: schema and vocabulary additions, the relationship and location-date passes over all claim files, 2 new claims (C0481, C0482), 1 new unit (`ALL-FAAA-001A`), and the docs. The "before" values in that section are from commit `66359ed`.

## Checks run

**After the Batch 1 review corrections:** `python3 scripts/validate.py` (101 claim files, 482 claims, 353 units, 14 conflict groups; 10 warnings, the same 10 as before: engaged_with name matches and one opponent count; none from the new checks), `python3 scripts/check_coordinates.py` (3 offline warnings: the speed flags C0053, C0280, C0411; the new G012 conflict flag raised by the Utah Beach row went away after the Mesnil-St-Martin correction), `python3 scripts/check_coordinates.py --geocode --country fr` (14 warnings: the 13 of Batch 1 plus C0482, Zon in the Netherlands, matched to a French homonym because of `--country fr`; coordinates checked by hand), `python3 scripts/build.py` and `build.py --check`, and `python3 scripts/audit_command_location.py`. The commit is "Apply Batch 1 review corrections; command and location-date semantics". **After US Batch 1:** `python3 scripts/validate.py` (101 claim files, 480 claims, 352 units, 14 conflict groups; 10 warnings, all already present before Batch 1 and none from the new rows), `python3 scripts/check_coordinates.py --geocode --country fr` (14 warnings, none real; see the Batch 1 section), `python3 scripts/build.py` and `build.py --check`. The commit is "US batch 1: Jul-Sep 1944". **Earlier:** `python3 scripts/validate.py` (76 claim files, 212 claims, 351 units, 11 conflict groups; 10 warnings: GER-COR-084C engaged_with and the 9 new engaged_with name matches; no missing-scope warnings remain), `python3 scripts/build.py`, `python3 scripts/build.py --check`, `python3 scripts/check_coordinates.py` (1 offline warning, known: Panzer Lehr C0053 155 km/day; the earlier C0067/C0081 49 km gap in G004 is resolved); commits "Apply spot-check review corrections", "Add review checklist and methodology guardrails", "Fix C0131 coordinates" and "Reclassify attached relationships for airborne divisions", "Backfill strength scope; reclassify 79th/90th relationships", "Resolve scope for C0018 and C0027; require scope", "Resolve G004 coordinate gap" and "Add Western Front unit placeholders". The data release is `build/all_claims.csv` together with the claim files; no zip archive is maintained.


## Batch 2: command transitions, 25 July to 15 September 1944 (25 October 2026)

Done on 25 October 2026 after the Batch 1 review. Scope: V, VII, VIII, XII, XV, XIX and XX Corps, First, Third and Ninth Army, 12th and 21st Army Group relationships, and the divisions whose corps or army links change in the window. Result: **32 new claims (C0483 to C0514)**, one new conflict group (G015), a regeneration of the table-derived relationships of 216 existing rows (160 of them dated in the window), and targeted edits to 19 existing rows. `build/all_claims.csv` now has 514 claims, 353 units, 101 claim files and 15 conflict groups.

### 1. A correction to the Batch 1 review text

The Batch 1 review stated that the CMH ETO-OB assignment table does not tell Assigned from Attached and therefore recorded every table link as `unspecified_subordination`. That is true only for the single **corps** column. The table has separate Army Assigned, Army Attached, Army Group Assigned and Army Group Attached columns (cells with `(Opn)`, `(Opns)` or `(Operations)` are operational control; `(Adm)`, `(Sup)` or `(Admin)` are administrative or supply). Batch 2 regenerated every table-derived entry from the table row dated `effective_from` (script not kept in the repository; the rule is now in `docs/methodology.md`, "Assignment table"):

| table entry | before | after |
|---|---|---|
| `unspecified_subordination` (corps and army) | 411 | 198 (192 US corps entries; 6 others in rows with no matching table row, left unchanged) |
| army `assigned` / army group `assigned` | 4 | 357 |
| army `attached` | 0 | 46 |
| `operational_control` / `administrative_control` from suffixes | 4 / 0 | 4 / 3 |

Examples: the 28th and 35th Divisions in July are now Third Army assigned and First Army attached (they fought under First Army; C0390's `parent_unit_id` moved to First Army); the 6th Armored Division on 25 July is VIII Corps (unspecified), First Army attached, 21st Army Group attached; 12th Army Group `assigned` now appears on every division row whose table row names it. Corps links stay `unspecified_subordination` unless a Green Book page says otherwise (section 2). Entries without an `effective_from` were given the date of the table row in force on the row date. Two entries duplicated within a row (82nd Airborne) were dropped. The 196 notes that said "not distinguished in the table" now say "single corps column; the table does not say assigned or attached for corps".

### 2. Command transitions: resolved and left

Resolved (new rows or corrected relationships, each with a source in the row):

| transition | result |
|---|---|
| 12th Army Group operational, First Army to Hodges, Third Army operational, 1 August (Breakout-18 p343) | C0484 (First Army, Vouilly, preferred), C0485 (alternate, Saint-Gilles, group G015), C0486 (Third Army leaves Néhou for Folligny on 2 August); C0289 (Third Army 1 August) re-sourced to 0.7 |
| First Army headquarters on 25 July | C0483: Vouilly (monument text and local history: 2 July to 2 August), 5 km, 0.7 |
| 12th Army Group to SHAEF direct control on 1 September (Breakout-32 p683) | C0488 (location Laval from the CMH list nine days earlier, 0.3 / 50 km) and C0489 (Palaiseau, 3 September) |
| Ninth Army operational 5 September, VIII Corps passed on 10 September, 6th Armored and 83rd under army control (Breakout-30 p636) | C0487 (army row), C0512 and C0513 (6th Armored to Ninth 5 September and back to Third 16 September), C0514 (83rd, 10 September); C0315/C0316 notes cite the Lesneven headquarters |
| VIII Corps assigned to Third Army but attached to First Army before 1 August (Breakout-3 p36) | five rows (C0120, C0144, C0195, C0310, C0311) now list Third assigned and First attached, parent First Army |
| VIII Corps headquarters moves (4 August south of Avranches; 18 August 120 miles to Lesneven) | C0498 (Vergoncey, 0.7), C0499 (Lesneven, 0.7) |
| V Corps takes the 35th Division and the front east of the Vire on 28 July; moves to Argentan on 17 August | C0490, C0491 (Alençon, Hôtel de France, 0.7); C0425 and C0426 now record the 35th as **attached** to V Corps (Breakout-15 p285, p289) |
| XIX Corps in July and August: Cobra fire support, displacement west of the Vire, 30th Division and CCA 2nd Armored transferred, concentration at Mortagne-Brezolles, attack on Elbeuf, Les Mureaux on 29 August | C0492 to C0496; C0414, C0415 and C0226 cite Breakout-16 p304 for the 28 July transfer ("transferred", so the relationship stays unspecified) |
| VII Corps passes two units to XIX Corps on 28 July | C0497 |
| XV Corps: first mission 1 August, Seine bridgehead at Mantes 20 August, passes from Third Army to First Army at 0600 on 24 August, hands the bridgehead to XIX Corps on 29 August | C0500 to C0503 (First Army modelled as `operational_control` from 24 August, Third Army stays `assigned`) |
| XX Corps and XII Corps headquarters | C0504 (Saint-Hilaire-du-Harcouët, 6 August), C0505 (Ducey, 7 August: remainder of the headquarters arrives) |
| 80th Division attached to XII Corps in late August (Breakout-28 p584) | C0463 and C0464 now `attached` |
| 2nd Armored Division and XIX Corps, 19 August versus 29 August | modelled as a sequence, not a conflict (section 3) |
| Cobra divisions: 1st (with CCB 3rd Armored attached), 2nd Armored (CCA, with the 22nd Infantry attached) on 26 July, 3rd Armored CCA on 27 July | C0506, C0507, C0508 |

Left open (stated in `docs/roadmap.md`): the Seventh Army headquarters place on 15 September (C0296 stays an unlocated representative point, 0.3); the VIII Corps headquarters on 5 and 10 September (documented only from 18 August; the rows keep Brest-sector points); the 83rd Division's simultaneous attachment to VIII and XV Corps (Breakout p428: not dated; the CMH table shows XV Corps on 1 August and VIII Corps on 3 August); the 2nd French Armoured Division's attachment to XV Corps (9 August, French unit not active); regiment-level Cobra rows for the 4th, 9th and 30th Divisions (no place and date together in the pages read); division-to-corps links that the table gives as one column and no Green Book page words as assigned or attached (198 entries).

### 3. The 2nd Armored Division and XIX Corps date question

CMH division table: XIX Corps from 19 August; V Corps on 18 August only; XV Corps on 28 August; XIX Corps again from 29 August. Green Book: XIX Corps was concentrated with the 2nd Armored, 28th and 30th Divisions in the Mortagne-Brezolles area by 19 August (Breakout-28 p576), attacked on 20 August with the 2nd Armored on the left (p578), and took command of the 79th, 30th and 2nd Armored in the Mantes bridgehead at noon on 29 August as XV Corps left (Breakout-31 p672). So the two dates are **two events**, not alternative dates for one event: the division joined XIX Corps on 19 August, was shown under XV Corps for the bridgehead crossing on 28 August, and returned to XIX Corps control on 29 August. This is recorded as three `command_change` rows (C0509, C0510, C0511), each with an `Event definition:`, and notes on C0229 and C0333; no conflict group. The single-day V Corps entry (18 August) is not explained by any source read and is noted in C0509.

### 4. New claims by unit

| id | unit | date | event | activity | place (represents, km, conf) | basis | status |
|---|---|---|---|---|---|---|---|
| C0483 | First Army | 1944-07-25 | hq_move | command post at Vouilly while Operation Cobra opens | Vouilly (Isigny-sur-Mer), Calvados (headquarters, 5 km, 0.7) | documented_on_date | preferred |
| C0484 | First Army | 1944-08-01 | command_change | Hodges assumes command as First Army passes to 12th Army Group | Vouilly (Isigny-sur-Mer), Calvados (headquarters, 5 km, 0.5) | documented_on_date | preferred G015 |
| C0485 | First Army | 1944-08-01 | command_change | Hodges assumes command as First Army passes to 12th Army Group | Saint-Gilles, Manche (headquarters, 5 km, 0.5) | documented_on_date | alternate G015 |
| C0486 | Third Army | 1944-08-02 | hq_move | army command post leaves Néhou for Folligny | Folligny, Manche (headquarters, 5 km, 0.5) | documented_on_date | preferred |
| C0487 | Ninth Army | 1944-09-10 | command_change | taking VIII Corps from Third Army and placing 6th Armored and 83rd Divisions under army control | Rennes, Ille-et-Vilaine (headquarters, 10 km, 0.5) | nearest_earlier_command_post -2d | preferred |
| C0488 | 12th Army Group | 1944-09-01 | command_change | SHAEF assumes direct control of the army group as Montgomery's coordination ends | Laval, Mayenne (headquarters, 50 km, 0.3) | nearest_earlier_command_post -9d | preferred |
| C0489 | 12th Army Group | 1944-09-03 | hq_move | army group headquarters at Palaiseau, south of Paris | Palaiseau, Essonne (headquarters, 5 km, 0.5) | documented_on_date | preferred |
| C0490 | V Corps | 1944-07-28 | command_change | taking control of the 35th Division and the front east of the Vire | Saint-Jean-des-Baisants ridge sector, Manche (sector_center, 10 km, 0.5) | operational_area | preferred |
| C0491 | V Corps | 1944-08-17 | command_change | taking three divisions near Argentan; command post at Alençon | Alençon, Orne (headquarters, 3 km, 0.7) | documented_on_date | preferred |
| C0492 | XIX Corps | 1944-07-25 | hq_move | command post at Trévières while corps artillery fires in support of Cobra | Trévières, Calvados (headquarters, 5 km, 0.5) | documented_on_date | preferred |
| C0493 | XIX Corps | 1944-07-28 | command_change | displacing west of the Vire and taking over the 30th Division and CCA, 2nd Armored | Saint-Lô, Manche (headquarters, 10 km, 0.5) | nearest_later_command_post +2d | preferred |
| C0494 | XIX Corps | 1944-08-19 | hq_move | command post at Tourouvre as the corps assembles for the Seine drive | Tourouvre au Perche, Orne (headquarters, 5 km, 0.5) | documented_on_date | preferred |
| C0495 | XIX Corps | 1944-08-20 | attack | attacking toward Elbeuf with 2nd Armored and 30th Divisions abreast | Verneuil-sur-Avre area, Eure (start of the attack) (sector_center, 10 km, 0.5) | operational_area | preferred |
| C0496 | XIX Corps | 1944-08-29 | hq_move | command post at Les Mureaux as the corps takes over the Mantes bridgehead | Les Mureaux, Yvelines (headquarters, 5 km, 0.5) | documented_on_date | preferred |
| C0497 | VII Corps | 1944-07-28 | command_change | passing the 30th Division and CCA, 2nd Armored to XIX Corps and turning south | Marigny, Manche (headquarters, 10 km, 0.5) | nearest_later_command_post +2d | preferred |
| C0498 | VIII Corps | 1944-08-04 | hq_move | command post moves south of Avranches | Vergoncey, Manche (headquarters, 5 km, 0.7) | documented_on_date | preferred |
| C0499 | VIII Corps | 1944-08-18 | hq_move | command post moves 120 miles to Lesneven to open the siege of Brest | Lesneven, Finistère (headquarters, 5 km, 0.7) | documented_on_date | preferred |
| C0500 | XV Corps | 1944-08-01 | other | receiving its first Third Army mission, to protect the Avranches corridor | Avranches–Brécey gap, Manche (midpoint of the two towns) (sector_center, 10 km, 0.5) | operational_area | preferred |
| C0501 | XV Corps | 1944-08-20 | attack | crossing the Seine at Mantes-Gassicourt with the 79th Division | Mantes-la-Jolie, Yvelines (headquarters, 5 km, 0.5) | documented_on_date | preferred |
| C0502 | XV Corps | 1944-08-24 | command_change | passing from Third Army to First Army control at 0600 | Mantes-la-Jolie, Yvelines (headquarters, 25 km, 0.3) | nearest_earlier_command_post -4d | preferred |
| C0503 | XV Corps | 1944-08-29 | command_change | handing the Mantes bridgehead to XIX Corps and moving for Third Army | Saint-Léger-en-Yvelines, Yvelines (headquarters, 5 km, 0.5) | documented_on_date | preferred |
| C0504 | XX Corps | 1944-08-06 | hq_move | command post at Saint-Hilaire-du-Harcouët as the corps enters Third Army operations | Saint-Hilaire-du-Harcouët, Manche (headquarters, 5 km, 0.5) | documented_on_date | preferred |
| C0505 | XII Corps | 1944-08-07 | arrival | remaining headquarters arrives; command post at Ducey | Ducey-Les Chéris, Manche (headquarters, 5 km, 0.5) | documented_on_date | preferred |
| C0506 | 1st Infantry Division | 1944-07-26 | attack | attacking toward Marigny with Combat Command B, 3rd Armored attached | Marigny, Manche (objective, 5 km, 0.5) | documented_on_date | preferred |
| C0507 | 2nd Armored Division | 1944-07-26 | attack | Combat Command A passing through the 30th Division toward Saint-Gilles | Saint-Gilles, Manche (objective, 5 km, 0.5) | documented_on_date | preferred |
| C0508 | 3rd Armored Division | 1944-07-27 | attack | Combat Command A advancing south of the Périers–Saint-Lô road toward Cerisy-la-Salle | Marigny–Saint-Gilles gap, Manche (sector_center, 10 km, 0.5) | operational_area | preferred |
| C0509 | 2nd Armored Division | 1944-08-19 | command_change | passing to XIX Corps for the Seine drive | Mortagne-au-Perche–Brezolles assembly area (sector_center, 25 km, 0.5) | operational_area | preferred |
| C0510 | 2nd Armored Division | 1944-08-28 | command_change | passing to XV Corps control east of the Seine | Le Neubourg, Eure (headquarters, 25 km, 0.3) | nearest_earlier_command_post -3d | preferred |
| C0511 | 2nd Armored Division | 1944-08-29 | command_change | returning to XIX Corps control in the Mantes bridgehead | Mantes-Gassicourt bridgehead area (Seine), Yvelines (sector_center, 10 km, 0.5) | operational_area | preferred |
| C0512 | 6th Armored Division | 1944-09-05 | command_change | passing to Ninth Army control with no corps | Plouay, Morbihan (headquarters, 10 km, 0.5) | documented_on_date | preferred |
| C0513 | 6th Armored Division | 1944-09-16 | command_change | returning to Third Army control; command post at Châteaubriant | Châteaubriant, Loire-Atlantique (headquarters, 3 km, 0.7) | documented_on_date | preferred |
| C0514 | 83rd Infantry Division | 1944-09-10 | command_change | placed directly under Ninth Army control, no corps | Vendôme, Loir-et-Cher (headquarters, 25 km, 0.3) | nearest_later_command_post +5d | preferred |

### 5. Conflicts

- **G015 (new):** First Army 1 August handover: C0484 (Vouilly, preferred) and C0485 (Saint-Gilles, alternate). Same event, two places 23 km apart: the monument text puts the army headquarters at Vouilly until 2 August; the CMH command-post list (as compiled by World War II by Day) lists Saint-Gilles from 1 August. The coordinate checker reports this conflict (expected).
- G012 to G014 are unchanged. No other conflict groups were added; the 2nd Armored sequence is not a conflict.

### 6. Existing rows edited (besides the regeneration)

C0289 (Third Army 1 August: confidence 0.5 to 0.7 and two sources added; the Néhou memorial and the CMH list agree on area and the 2 August departure); C0333, C0229 (notes on the 2nd Armored sequence); C0296 (Seventh Army unlocated, with what was searched); C0315, C0316 (VIII Corps headquarters note); C0120, C0144, C0195, C0310, C0311 (VIII Corps relationships); C0425, C0426 (35th attached to V Corps); C0414, C0415, C0226 (source for the 28 July transfer); C0463, C0464 (80th attached to XII Corps); C0390 (parent moved to First Army; note). No coordinates or dates of existing rows changed.

### 7. Validation and audit

- `scripts/validate.py`: OK, 514 claims, **12 warnings** (10 as before: engaged_with names and opponent counts; 2 new, both the 82nd and 101st Airborne rows C0214 and C0218, where the CMH table shows "Ninth" in the Army Attached column with no standing assignment in the Assigned column, so the validator's "attached entry without a standing parent" check fires; the table says exactly that, so it is recorded as written). A validator rule was relaxed: an attachment to an army no longer triggers the "parent_unit_id is not the attached unit" warning when the parent is a corps (otherwise 39 table rows such as the 35th Division would warn although the corps is the immediate parent).
- `scripts/check_coordinates.py`: 7 warnings (3 before). The four new ones are explained: G015 (the conflict itself); C0489 against C0488 (12th Army Group at Laval on 1 September, Palaiseau on 3 September; the Laval point is a 0.3 / 50 km nearest-earlier row); C0276 against C0513 (6th Armored Division CP list: Châteaubriant 16 September, Colombey-les-Belles 19 September); C0499 against C0313 (the documented 120-mile move to Lesneven).
- `scripts/audit_command_location.py` (all claims, before then after): rows with `unspecified_subordination` 213 to 204; coordinate from a different date (`location_date` != `date`) 49 to 56 (the seven new nearest-CP rows C0487, C0488, C0493, C0497, C0502, C0510, C0514, each with its offset); corps/army/army-group headquarters that is a town centroid 7 to 7 (the new Batch 2 headquarters rows use `documented_on_date`, so they are not counted); conflict groups with different event types 2 to 2; `location_basis` blank 211 to 211 (older rows, unchanged).

### 8. Sources and what could not be sourced

New sources: Breakout and Pursuit pages 36, 248-255, 264, 285, 289, 304, 343-350, 423-424, 431, 529, 576-578, 584, 636-638, 672, 683; normandie44lamemoire.com and uswarmemorials.org (Vouilly, Néhou); World War II by Day corps/army/army-group command-post lists (secondary; its VIII Corps list omits the documented 18 August Lesneven move, so it is not treated as complete). CMH's own corps and army pages could not be fetched from this box. **Unsourced or weak:** Seventh Army headquarters on 15 September; 12th Army Group on 1 September (Laval is the nearest earlier listed place); 83rd Division and XV Corps attachment dates; the XIX Corps displacement date (28 July from the division tables and Breakout-16 p304; the corps order itself was not found).

## Batch 2 review corrections (25 October 2026)

An outside reviewer assessed the 15-row Batch 2 spot check. Their findings were treated as unverified: each factual claim was checked against the Green Books (The Breakout and Pursuit; The Lorraine Campaign), the 6th Army Group G-3 report, the Third Army After Action Report and the other sources named below, and only what the sources support was applied. Where I disagree or went a different way, it is stated. Commit: "Apply Batch 2 review corrections".

### 1. Verdict on each finding

| # | Finding | Verified? | Result |
|---|---|---|---|
| 1 | C0502/C0503: end of First Army control; assigned versus operational control; "Mantes did not move" inference; restored Third Army control | **Mostly confirmed.** 0600 24 Aug and noon 29 Aug are in Breakout-28 p578 and Breakout-31 p672. The restoration is documented by date only. | Applied with qualifications (section 2.1). |
| 2 | C0509/C0510: 28 Aug XV Corps relationship; Le Neubourg point | **Confirmed.** Breakout-31 p672: XV Corps "continued in command" of the bridgehead until noon 29 Aug; the 2nd Armored crossed the Seine on 28 Aug. | Applied (2.2). |
| 3 | C0484 (G015): sequence rather than conflict | **Partly supported.** Plaque: Vouilly "from July 2nd to August 2nd"; CMH list: Saint-Gilles from 1 Aug. | Re-modelled as a sequence; group dissolved (2.3). |
| 4 | C0289: confidence of a coordinate backed by regional agreement | **Confirmed in part.** Three local sources say Néhou; the CMH list says Bricquebec, 8 km away. | Precision widened; 0.7 kept under the rubric; support spelled out (2.4). |
| 5 | C0487/C0514: divisional dates; Vendôme is a later observation | **Confirmed.** Breakout-30 p636 dates only the VIII Corps transfer. | Applied, with a better 83rd location than the reviewer proposed (2.5). |
| 6 | C0296: AFHQ is not administrative control; Vesoul is not a headquarters | **Confirmed.** The G-3 report says AFHQ retained supply, administrative functions and civil affairs "within the area overrun". The same wording is on C0222. | Applied to C0296 and C0222 (2.6). |
| 7 | C0493: add the 113th Cavalry Group; CCA separate | **Confirmed.** Breakout-15 p296. | Applied; new row C0515 (2.7). |
| 8 | C0488: Laval as last-known; both bounding dates; no implication of no higher HQ | **Confirmed.** | Applied (2.8). |
| 9 | C0310: Coutances is an objective | **Confirmed.** | Applied; same fix to four other objective rows (2.9). |
| 10 | C0499 speed warning: explained-exception mechanism | **Confirmed** (Breakout-30 p638). | Implemented (section 4). |

### 2. Row-by-row changes

**2.1 C0502, C0503 (XV Corps, 24 and 29 August).**
- C0502: First Army `operational_control` now has `effective_to` 1944-08-29 with `effective_to_basis` narrative. The hour of the end is not documented and stays in the note. Third Army "assigned" is kept but marked `date_basis: inferred`.
- **Assigned versus control, what the sources say.** Breakout-28 p578 says the corps "passed from the control of Third Army to that of First Army"; Breakout-31 p672 says it was to "rejoin" Third Army and moved for "eventual Third Army assignment"; Lorraine ch. IV (p185) says the headquarters "had been taken from the Third Army" and would be "returned"; the Third Army After Action Report says it was "released to First US Army" on 24 August and "did not revert to control of Third US Army until 29 August". No source says whether its formal assignment changed during 24-28 August (Wikipedia's subordination table, a secondary source, shows First Army only for those days). So the Batch 2 statement "the corps stays Third Army assigned" was an inference from the word "control" and is now labelled as one.
- **Mantes inference removed.** The note that XV Corps "did not move between" 20 and 28 August is withdrawn. The CMH list has Mantes-la-Jolie on 20 and 28 August and nothing between; the Mantes vicinity is inferred from those two entries and uninterrupted presence is not claimed. The row still uses the 20 August entry (four days earlier; 28 August is four days later), confidence 0.3 / 25 km.
- C0503: carries the explicit end of First Army control (29 August) and a new Third Army `operational_control` entry from 29 August (`date_basis` narrative; source: Third Army After Action Report, Lorraine ch. IV). **Disagreement with the reviewer's "restored ~noon 29 Aug":** the sources date the reversion to 29 August but give no hour for it; Breakout-31 p672 says the headquarters began to move at noon; Breakout-31 p665 says XV Corps "did not become available as soon as expected" and Lorraine ch. IV shows it with no divisions until 8-10 September. The entry is therefore dated 29 August, with the hour in the note as not documented. The standing assignment is inferred, as in C0502, and is not re-listed because no source uses that word for 29 August.
- Added to both rows: `Event support:` (high) and `Location support:` sentences. Sources added: Lorraine ch. IV, the Third Army After Action Report, Wikipedia XV Corps (secondary), Breakout-18 p344, Breakout-22 p423.

**2.2 C0509, C0510, C0511, C0229, C0333 (2nd Armored Division, 19 to 29 August).**
- C0510: XV Corps is now `operational_control`, 28 to 29 August (end `effective_to_basis` narrative). The CMH single corps column does not say assigned or attached, and the Green Book describes about a day of XV Corps command of the divisions in the Mantes bridgehead between two periods under XIX Corps, so the table is not read as a reassignment. The XIX Corps link is listed as `unspecified_subordination` with `date_basis: inferred` from 28 August (no source says it ended). First Army and 12th Army Group "assigned" (table army columns) are unchanged.
- C0510 location: the 25 August Le Neubourg command post is no longer used for 28 August, when the division crossed the Seine. The point is now the Mantes-Gassicourt bridgehead sector, `sector_center`, `operational_area`, `location_date` 28 August, 10 km, confidence 0.5. This is a sector point, not the division command post.
- C0509 and C0229: the XIX Corps entry now ends 27 August (`effective_to_basis` assignment_table), the last table day before XV Corps appears. C0511, C0229 and C0333 gained notes that the XV Corps command was temporary operational control. C0511 keeps `unspecified_subordination` to XIX Corps: Breakout-31 p672 says XIX Corps "took command" of the divisions at noon on 29 August, but the table only shows XIX Corps in the single corps column.

**2.3 C0484, C0485 (First Army, 1 August; conflict group G015 dissolved).**
- Checked: the Vouilly plaque (inaugurated 2018-2019) says the headquarters stayed "from July 2nd to August 2nd"; normandie44lamemoire says the same from the French text; the CMH list as compiled by World War II by Day has Saint-Gilles from 1 August (previous entry Isigny, 5 July, which includes Vouilly). The sources therefore do not exclude each other: the list date is one day before the plaque's departure date, and whether it marks an advance echelon, the main headquarters or an arrival convention is not stated.
- Both rows are now `preferred` with no conflict group; C0485 is an `hq_move` to Saint-Gilles in sequence after C0484 (Vouilly kept for the command change because the plaque has the headquarters there through 1 August). The coordinate checker's conflict warning disappears with the group; there are now 14 conflict groups. The order of events within 1-2 August is not documented.
- I did not go further than a sequence of rows: no source says which place held the main headquarters at noon on 1 August, so neither row is labelled "advance command post".

**2.4 C0289 (Third Army, 1 August).**
- Event: high (Breakout-18 p343). Locality: moderate. Coordinate: Néhou village centroid, orchard not located. The reviewer's reading is right that regional agreement is not agreement on the village: three local sources (KilroyTrip, normandie1944, the Néhou memorial) say Néhou, the CMH list says Bricquebec, 8 km away.
- `precision_km` widened from 5 to 10 so that the radius covers both villages. Confidence stays 0.7 because the rubric gives 0.7 for an approximate location with two source families; the note now says that this is a composite score and not a 70% probability for the coordinate. I did not add a confidence level outside the rubric (and no separate column, section 3c).

**2.5 C0487, C0512, C0514 (Ninth Army, 5 and 10 September).**
- C0487: current_activity now covers only the VIII Corps transfer, documented for 10 September (Breakout-30 p636). `composing_units` dates each component. The note says the two divisions came directly under army control by separate decisions the text does not date.
- C0512 (6th Armored): the start is an interval, `effective_from` 5 September (CMH table: Ninth Army shown from that day) with `effective_from_latest` 10 September (the narrative places the order after the VIII Corps transfer, and gives no date), and an end on 15 September (`effective_to_basis` assignment_table; table has Third Army on 16 September; Breakout-30 p637: moved east "around the middle of September"). The two sources are not reconcilable to one date; the interval records both.
- C0514 (83rd): date kept at 10 September with `date_basis` assignment_table, as the reviewer suggested. **Different from the reviewer on location:** instead of keeping Vendôme (15 September CP) as a `nearest_later_command_post`, the row now uses a better source: Breakout-30 p653-654 has the 83rd on the Loire protecting Third Army's south flank and receiving Elster's surrender on 10 September, with columns crossing at Orléans, Beaugency and Mer. The point is a sector point at Beaugency (`sector_center`, `operational_area`, 25 km, 0.5), not the command post; Vendôme (CMH list, 15 September) is named in the note as a later observation five days after, not a 10 September location. The note also records the tension that the text has the division in the Third Army south-flank zone while the table puts it under Ninth Army.

**2.6 C0296 and C0222 (Seventh Army and 6th Army Group, 15 September).**
- The G-3 report: AFHQ "retained" responsibility for "supply and administrative functions and for civil affairs within the area overrun pending further developments". That is a theater and territorial function; the source does not say AFHQ held administrative control of the army group or of Seventh Army. The `administrative_control` entry is withdrawn from both rows and replaced with relationship `unknown` and a scoped note (the vocabulary's `unknown` means a formation named but its relationship to the unit not stated). **Not `supporting`**, as the reviewer floated: `supporting` means the subject unit supports the named formation, which the source does not say either.
- C0296: `ordered_date` 14 September (the order reached the headquarters on the afternoon of 14 September) and `effective_from` 15 September (0001B). The Vesoul point was already a `representative_point` and `sector_center`; the note now says again that it is not a headquarters, and why confidence is 0.3.
- Documentation examples that cited AFHQ administrative control (methodology.md, schema/README.md) were corrected.

**2.7 C0493, new C0515 (XIX Corps and CCA, 28 July).**
- C0493: Breakout-15 p296 (cited as p285 and p304 before; p296 added) names the units XIX Corps took over at noon on 28 July: the 30th Division, CCA of the 2nd Armored Division reinforced by the 4th Division's 22nd Infantry, and the 113th Cavalry Group. `composing_units` now lists those three with dates and qualifiers, and the 29th and 28th Divisions only as "displacing into the zone, control not dated" (p296 says they moved into the new zone; it does not say they were under the corps at noon). The note says the list is not an organic order of battle.
- C0515 (new): CCA, 2nd Armored Division (unit `US-CCA-002D`, already in the table), 28 July, `command_change`, organic to the 2nd Armored Division and `unspecified_subordination` to XIX Corps (Breakout-15 p296 and Breakout-16 p304 say "transferred"; neither says attached or assigned). Location: Le Mesnil-Herman, its primary Cobra objective, in its possession at noon on 28 July (p296), village centroid, `main_body`, `documented_on_date`, 5 km, confidence 0.7. The rest of the 2nd Armored Division stayed with VII Corps (Breakout-16 p304: "2d Armored Division, less CCA"). Breakout-15 p302 shows CCA still under XIX Corps for the 1 August attack (attached to the 29th Division); the end of the arrangement is not dated for CCA, so no `effective_to` is invented.

**2.8 C0488, C0489 (12th Army Group, 1 and 3 September).**
- C0488: Laval is named as the last-known place in `location_name` and the note. Bounding dates: the CMH list has Laval from 23 August and Palaiseau on 3 September (C0489); a 12th Army Group history says Laval in August and Versailles in early September; Eisenhower met Bradley, Hodges and Patton at Chartres on 2 September (a conference place, not the headquarters). Nothing places the headquarters on 1 September; `nearest_earlier_command_post`, 0.3 / 50 km unchanged.
- The SHAEF relationship note and the notes now say that 1 September changes the channel (SHAEF direct, Eisenhower in personal command of the ground forces) and does not start the SHAEF relationship: SHAEF authority already existed, exercised through Montgomery's coordination of 21st Army Group (C0223, which already carries the `coordinating` entry to 31 August).

**2.9 C0310 and the objective rows.**
- C0310: `location_basis` changed from `documented_on_date` to `representative_point`; `location_name` now says the point is the 26 July objective, not the corps headquarters or its position (VIII Corps took Coutances on 28 July). **I did not add an `objective_location` column**: `location_represents: objective` already exists, and the only gap was the basis value; the vocabulary text for `representative_point` now covers a named objective.
- The same pattern was found by the audit in nine attack rows. Four with an objective that was not reached on the date got the same fix: C0305, C0506, C0507, C0309 (Marigny, Saint-Gilles, Aachen). Five were checked and left because the unit was fighting at the named place: C0254, C0301, C0314, C0322, C0338 (each gained an `Objective check:` sentence; the audit no longer flags a row with that sentence).

**2.10 C0499 and VIII Corps (documented versus last confirmed).**
- C0499 keeps `hq_move`, 18 August, `documented_on_date`, 0.7. Its note now says Lesneven is a documented observation and the last confirmed headquarters place before the CMH list's St Aubin on 24 September, not a verified position for the days between; the 5 and 10 September rows (C0315, C0316) keep their Brest-sector points and say so. The speed warning is now an explained exception (section 4).
- C0310, C0311, C0120, C0144, C0195 (VIII Corps before 1 August): the First Army `attached` entry gets `effective_to` 1944-08-01 (`effective_to_basis` narrative, Breakout-18 p344: Patton took command of VIII Corps on 1 August).

**2.11 Order versus effect: C0425, C0426.**
- The 35th Division: Bradley ordered the attachment to V Corps on the evening of 27 July (Breakout-15 p285); V Corps took control on 28 July (p289). The entry now carries `ordered_date` 1944-07-27 and `effective_from` 1944-07-28. C0425's row date moves from 27 to 28 July (the effective date), which makes the 28 July St-Lô division command post (CMH) a same-day location: `documented_on_date`, 3 km, confidence 0.7 (it was 0.5 / 10 km, nearest later command post). The CMH table's V Corps date of 27 July is the order date, noted. C0426 gets the same entry. C0296 uses the same pair (ordered 14 September, effective 15 September). I found no other window rows where a source gives both an order date and a different effective date.

**2.12 Event support sentences.** `Event support:` and `Location support:` (qualitative: high, moderate, low, with the reason) were added to the notes of the 19 Batch 2 command_change and activation rows (C0289, C0296, C0425, C0484, C0487, C0488, C0490, C0491, C0493, C0497, C0502, C0503, C0509 to C0515). This answers the reviewer's point that a well documented command event should not read as low-confidence because its location is uncertain, without a new column (3c).

### 3. Design suggestions: what was done and what was declined

- **(a) Validity intervals, `ordered_date`: done, additive.** New optional keys inside each relationship entry: `ordered_date`, `effective_from_latest` (earliest and latest possible start), `effective_to_earliest`, `effective_to_basis`. The validator checks formats and ordering (an order cannot follow its effective date; a range must be a range). It also prints a count of `attached` and `operational_control` entries that have no `effective_to` and are not listed by the unit's next claim (34 now); this is a note and not a warning because the 34 existing snapshot entries would otherwise add 34 warnings. The audit script counts the claims they sit on (32 claims). A missing `effective_to` is documented as never meaning "forever". Explicit ends were added where a source dates them (XV Corps, 2nd Armored, 6th Armored, VIII Corps' First Army attachment).
- **(b) Derived relations table: done, first version.** `build/command_relations.csv` (248 rows, US units with a claim from 24 July to 20 September 1944) is built by `scripts/build.py`: subject, higher, relationship, `valid_from`, `valid_from_latest`, `valid_to`, `valid_to_earliest`, `valid_to_basis` (the entry's own end basis, `inferred_from_next_claim`, or `open_at_last_claim`), `support` (documented, table, inferred), `ordered_date`, source claim ids. `python scripts/who_controls.py US-ARM-002D 1944-08-28` returns XV Corps `operational_control` (28-29 August, table), XIX Corps `unspecified_subordination` (inferred continuity), First Army and 12th Army Group assigned (table); for XV Corps on 30 August it returns Third Army operational control (not First Army). **Differences from the reviewer's sketch:** no numeric `confidence` (0.85 is outside the rubric; `support` says documented, table or inferred instead), and no timestamps (sources mix local, British and double-summer time; the time of day stays in the note). Other nations and periods are not derived yet.
- **(c) Event versus location confidence / `location_status`: declined again.** The `confidence` rubric is, by its own wording, a score for the location and its sources; `precision_km` and `location_basis` carry the rest; a status column (confirmed, last_known, interpolated, representative, unknown) would repeat `location_basis` almost one to one; and a second numeric column would need a judged value for 515 rows. What was added instead is the qualitative `Event support:` / `Location support:` pair in notes from Batch 2 on, a validator warning when a command row with confidence 0.3 or less lacks `Event support:`, and `support` in the derived table. The reviewer's separate suggestions to mark a town centroid separately from a source-geocoded location, and to separate temporal and geographic uncertainty, are already `location_basis: town_centroid` and `precision_km`, so nothing was added.
- **(d) `composing_units` with dates: roadmap.** C0493 and C0487 now carry dated, qualified entries as text. A derived composing view needs the components (combat commands, cavalry groups) to be units with relationship rows; the 113th Cavalry Group and several combat commands are not.
- **(e) `last_confirmed_hq_location`: roadmap.** It needs a temporal reconstruction layer over the derived tables. Meanwhile the rows say it in text (section 2.10).
- **`observed_at` and `ordered_at` as separate timestamps: partly.** `ordered_date` was added (date only). `observed_at` is declined: the claim's source and date already give the observation, and the derived table lists the claims.

### 4. Coordinate checker: explained exceptions

- New `data/coordinate_exceptions.csv` (check, claim_id, other_claim_id, reason, source). A listed warning prints as `EXPLAINED` and is counted separately; an entry that no longer matches any warning prints `STALE`. Five speed entries, each with a source: C0499 against C0313 (VIII Corps 120-mile move, Breakout-30 p638), C0411 against C0410 (29th Division from Brest to the Netherlands, Breakout-30 p653), C0276 against C0513 (6th Armored to Lorraine, Breakout-30 p637), C0280 against C0279 (7th Armored's hurried march, Breakout-28 p567), C0053 against C0038 (Panzer Lehr's 90-mile drive).
- **Behaviour change found while doing this:** the speed check counted days between the rows' dates, not between the dates the coordinates belong to. It now uses `location_date` when set. C0489's old warning (Laval 23 August to Palaiseau 3 September) disappears (it was never a 117 km/day move); three new ones surface that the old method hid: C0253 (4th Armored, 140 km against C0252 in one day), C0419 (30th Division, 127 km against C0418 in one day), C0480 (94th Division, 225 km against C0479 in one day; the C0479 point is a nearest-later command post, so part of this may be a location artefact). They are **not** explained: I did not find a source for them and did not add exceptions without one.

### 5. Checks, before and after this correction pass

| check | before | after |
|---|---|---|
| `validate.py` | OK, 514 claims, 12 warnings | OK, 515 claims, 12 warnings (the same 12: ten engaged_with prompts and the two airborne attachments C0214, C0218); one NOTE line (34 open-ended temporary entries) |
| `check_coordinates.py` | 7 open warnings | 3 open warnings (C0253, C0419, C0480, newly visible) and 5 explained exceptions; G015 and C0489 gone |
| `audit_command_location.py` | unspecified_subordination 204; coordinate from another date 56 | unspecified_subordination 205 (the new CCA row); coordinate from another date 53 (C0425, C0510, C0514 now carry same-day locations); new audit patterns: open-ended entries superseded by the next claim (32 claims); objective rows without an Objective check; low-confidence command rows without Event support (none flagged after the edits) |
| conflict groups | 15 | 14 (G015 dissolved) |
| `build.py --check` | up to date | up to date (5 generated files, including the new `command_relations.csv`) |

### 6. Rows changed (40 claim rows in 24 files, plus the new C0515)

C0120, C0144, C0195, C0310, C0311 (First Army attachment end; C0310 also objective); C0222 (AFHQ entry); C0229, C0509, C0510, C0511, C0333 (2nd Armored); C0254, C0301, C0314, C0322, C0338 (objective check notes); C0289; C0296; C0305, C0506, C0507, C0309 (objective basis); C0425, C0426; C0484, C0485; C0487, C0512, C0513 (note), C0514; C0488, C0489; C0490, C0491, C0497, C0499 (notes and support sentences); C0493; C0502, C0503; C0515 (new). The earlier Batch 2 text above is left as written, including its statements about G015, C0502 and C0510; this section supersedes them.

### 7. Open items after the review

- The order of events on 1-2 August at the First Army headquarters (Vouilly to Saint-Gilles) and which place held the main headquarters at noon on 1 August are not documented.
- The hour of XV Corps' return to Third Army control on 29 August and whether its formal assignment changed 24-28 August are not documented (Wikipedia's table is secondary).
- The 83rd and 6th Armored direct-control dates: the narrative gives none; the table dates are the basis. The end of CCA's attachment to XIX Corps is not dated.
- Seventh Army's headquarters on 15 September is still unlocated; VIII Corps headquarters on 5 and 10 September is still only inferred from Lesneven.
- Three speed warnings (C0253, C0419, C0480) are open and unchecked; 34 temporary entries (32 claims) still have no source-dated end (the derived table closes them at the next claim).
- The reviewer's derived-state design (daily order of battle from claims) is partly built (US, 24 July to 20 September 1944). Extending it, composing units and `last_confirmed_hq_location` are on the roadmap.

## Batch 3: US army group, army, corps and division milestones, 1 October to 31 December 1944 (25 October 2026)

Scope: army group, army, corps and division level on the Western Front, 1 October to 31 December 1944; milestones only, not every unit for every week. Sources: the CMH Green Books (Siegfried Line, Lorraine, Riviera to the Rhine, and the Ardennes volume), the CMH ETO order-of-battle assignment tables (Internet Archive copies), and the World War II by Day command-post lists as the secondary place source. Wikipedia was not needed for any row.

### 1. Result

- **48 new claims, C0516 to C0563** (16 corps, 20 division, 10 army and 2 army-group rows): 6th Army Group 1; 12th Army Group 1; First Army 3; Third Army 3; Seventh Army 2; Ninth Army 2; III Corps 2; VII Corps 2; VIII Corps 2; XII Corps 2; XIII Corps 2; XIX Corps 2; XV Corps 1; XVIII Airborne Corps 1; XX Corps 1; XXI Corps 1; 4th Armored 2; 10th Armored 2; 28th 1; 75th 1; 82nd Airborne 1; 84th 2; 87th 1; 100th 1; 101st Airborne 4; 102nd 1; 103rd 1; 104th 1; 106th 2.
- **12 placeholders became active** (`promote_placeholders.py`): III, XIII and XXI Corps; 10th Armored; 75th, 84th, 87th, 100th, 102nd, 103rd, 104th and 106th Infantry Divisions. Active units 101 to 113, placeholders 252 to 240.
- **Command transitions.** Resolved with a date and a source: First and Ninth Armies to 21st Army Group (20 Dec, hour undocumented; ends 17 Jan and 3 Apr 1945 from the CMH tables); VIII Corps First to Third Army (20 Dec, hour undocumented, both listed that day); XVIII Airborne Corps operational under First Army (19 Dec); XIX Corps to Ninth Army and VIII Corps to First Army (22 Oct noon); XIII Corps first sector (8 Nov); III Corps first division (4 Dec, CMH table); XXI Corps first division (27 Dec, CMH table); 84th Division under British XXX Corps 11-22 Nov (table) and to First Army 20 Dec; 101st Airborne to Third Army 20 Dec. **Open:** the hour on 20 December for the VIII Corps/101st transfer; the 101st's CMH-table date of 17 December against the Green Book's 20th (conflict G016); the 21st Army Group end dates are table-derived and sit outside this window; V Corps, 99th, 2nd and 9th Divisions and the 7th Armored in the Bulge were not read for this batch; the First Army move to Tongeren (24 Dec, atlas) has no row.
- **Conflicts.** One new group, **G016** (101st Airborne Third Army attachment: Green Book 20 Dec preferred 0.7, CMH table 17 Dec alternate 0.3). Event definitions are in both rows; a coordinate exception covers the 137 km between their points. The group number G015 was not reused (that group was dissolved in the Batch 2 corrections).
- **Unsourced / not found.** No row is without a source. Places that are not tied to the row date are marked: First Army 22 Oct (inferred, 0.3), XVIII Airborne Corps (neighbour's command post), Ninth Army 20 Dec (nearest earlier atlas entry 56 days before), XIII, XII, XV, XIX and VII Corps sector or headquarters points (13-36 days or sector points). Not found: the date a Green Book page gives for the III Corps first division (the table date is used), the XXI Corps start (table and an undated note), the hour of any 20 December change.

### 2. What was decided differently from the plan

- **First Army move to Chaudfontaine** is the 19th (Ardennes p423), not the 17th as first assumed; row C0519.
- **XIII Corps** gets two rows: first sector 8 November (Siegfried p401) and the sector takeover 24 November (p565); the first plan was to date the activation on 24 November.
- **12th Army Group and the 20 December change.** The CMH tables keep the 12th Army Group in the assigned column for First and Ninth Armies' units and add the 21st Army Group as attached, so the entries are: 12th Army Group `assigned` (unchanged) and 21st Army Group `operational_control` from 20 December with `effective_to` taken from the tables; `parent_unit_id` is the 21st Army Group for those rows.
- **101st at noon on 20 December.** `scripts/who_controls.py US-ABN-101D 1944-12-20` returns VIII Corps, First Allied Airborne Army (assigned), and Third Army and 12th Army Group (attached from 20 December, ends 19 January 1945 from the table); the hour and the 17 December table date are documented in the notes, not resolved.
- **Derived table.** `scripts/build.py` now builds `command_relations.csv` for claims from 24 July to 31 December 1944 (was 20 September) and ignores alternate and disputed rows, so conflict rows no longer extend an interval.
- **Confidence rubric applied by the rule:** a headquarters place more than three days from an atlas entry, or inferred, is 0.3 (several first drafts of mine had 0.5; corrected before commit). Preferred rows in G016 are capped at 0.7 and the alternate at 0.5 (0.3 used).

### 3. Checks, before and after

| check | before | after |
|---|---|---|
| claims / units active | 515 / 101 | 563 / 113 |
| `validate.py` | 12 warnings, 0 errors | 12 warnings, 0 errors (none new) |
| `check_coordinates.py` | 3 open, 5 explained | 3 open, 6 explained (the G016 conflict) |
| `audit_command_location.py`, `unspecified_subordination` | 205 | 223 (corps entries from the CMH tables) |
| `audit_command_location.py`, attached/operational_control without `effective_to` | not recorded | 35 in total; the Batch 3 rows that have none are the XVIII Airborne Corps under First Army and SHAEF control of the 6th and 12th Army Groups, which no source ends in the window |
| conflict groups | 14 | 15 |
| `build.py --check` | up to date | up to date |

`who_controls.py` spot checks: US-ABN-101D on 19 Dec (VIII Corps, First Allied Airborne Army; no Third Army), 20 Dec (adds Third Army and 12th Army Group) and 21 Dec; US-COR-008C on 20 Dec (First and Third Army both listed); US-ARMY-001A on 21 Dec (12th Army Group assigned, 21st Army Group operational control to 17 Jan 1945); US-ARMY-009A on 31 Dec; US-INF-084D on 18 Nov (British XXX Corps and Second Army operational control to 22 Nov) and on 21 Dec (First Army attached, VII Corps).

### 4. New claims

| claim | unit | date | event | activity | place (represents, km, conf) | basis | status |
|---|---|---|---|---|---|---|---|
| C0516 | 6th Army Group | 1944-10-02 | hq_move | army group command post at Dompaire | Dompaire, Vosges (headquarters, 5 km, 0.5) | documented_on_date | preferred |
| C0526 | Seventh Army | 1944-10-02 | hq_move | army command post at Épinal | Épinal, Vosges (headquarters, 5 km, 0.5) | documented_on_date | preferred |
| C0528 | XIX Corps | 1944-10-16 | attack | 30th Division links with 1st Division at Würselen, closing the Aachen ring | Heerlen, Limburg (headquarters, 5 km, 0.5) | nearest_earlier_command_post (-3 d) | preferred |
| C0529 | VII Corps | 1944-10-21 | capture | 1st Division takes Aachen; the garrison commander surrenders | Aachen, North Rhine-Westphalia (objective, 3 km, 0.7) | documented_on_date | preferred |
| C0518 | First Army | 1944-10-22 | command_change | takes VIII Corps and the Ardennes sector from Ninth Army; XIX Corps goes to Ninth | Spa, Liège (headquarters, 5 km, 0.3) | inferred | preferred |
| C0521 | Ninth Army | 1944-10-22 | command_change | takes XIX Corps from First Army and opens a command post at Maastricht | Maastricht, Limburg (headquarters, 5 km, 0.5) | nearest_later_command_post (+3 d) | preferred |
| C0543 | 104th Infantry Division | 1944-10-23 | attack | first combat: moves into the line with the 1st British Corps on the south bank of the Maas | Westmalle, Antwerp (headquarters, 5 km, 0.5) | nearest_earlier_command_post (-1 d) | preferred |
| C0523 | Third Army | 1944-11-08 | attack | XII Corps opens the Lorraine offensive; XX Corps attacks next day | Nancy, Meurthe-et-Moselle (headquarters, 10 km, 0.3) | nearest_earlier_command_post (-27 d) | preferred |
| C0532 | XIII Corps | 1944-11-08 | activation | takes over the 17-mile Ninth Army front west of Geilenkirchen with the 102nd Division and the 113th Cavalry Group | Tongeren, Limburg (headquarters, 10 km, 0.3) | nearest_earlier_command_post (-13 d) | preferred |
| C0534 | 102nd Infantry Division | 1944-11-08 | defense | holds the Ninth Army north flank west of Geilenkirchen under XIII Corps | Heerlen, Limburg (headquarters, 5 km, 0.3) | nearest_later_command_post (+4 d) | preferred |
| C0535 | XII Corps | 1944-11-08 | attack | opens the Lorraine offensive across the Seille | Nancy, Meurthe-et-Moselle (headquarters, 10 km, 0.3) | nearest_earlier_command_post (-27 d) | preferred |
| C0537 | 10th Armored Division | 1944-11-08 | relocation | relieved west of Metz by the 95th Division and moves north for the XX Corps envelopment | Ottange, Moselle (headquarters, 5 km, 0.5) | nearest_later_command_post (+1 d) | preferred |
| C0536 | XX Corps | 1944-11-09 | attack | crosses the Moselle north of Metz; the 5th Division follows on the 9th | Uckange, Moselle (sector_center, 10 km, 0.5) | documented_on_date | preferred |
| C0541 | 100th Infantry Division | 1944-11-12 | attack | first combat: crosses the Meurthe toward Raon-l'Étape | Baccarat, Meurthe-et-Moselle (headquarters, 5 km, 0.5) | nearest_earlier_command_post (-1 d) | preferred |
| C0540 | XV Corps | 1944-11-13 | attack | attacks from Lunéville toward Sarrebourg and the Saverne Gap | Lunéville, Meurthe-et-Moselle (headquarters, 10 km, 0.3) | nearest_earlier_command_post (-36 d) | preferred |
| C0530 | VII Corps | 1944-11-16 | attack | attacks toward the Roer after weather delays; heavy fighting at the Donnerberg and in the Hürtgen | Eschweiler, North Rhine-Westphalia (sector_center, 10 km, 0.3) | nearest_later_command_post (+4 d) | preferred |
| C0531 | XIX Corps | 1944-11-16 | attack | attacks toward the Roer; code words "The Democrats have won" telephoned to the 30th Division | Alsdorf, North Rhine-Westphalia (sector_center, 10 km, 0.3) | nearest_earlier_command_post (-34 d) | preferred |
| C0544 | 84th Infantry Division | 1944-11-18 | attack | first major attack: Operation Clipper toward Geilenkirchen under British operational control | Eygelshoven, Limburg (headquarters, 5 km, 0.5) | nearest_earlier_command_post (-2 d) | preferred |
| C0542 | 103rd Infantry Division | 1944-11-20 | attack | first combat: two regiments cross the Meurthe at the 3rd Division sites | Les Rouges-Eaux, Vosges (headquarters, 5 km, 0.5) | nearest_earlier_command_post (-1 d) | preferred |
| C0533 | XIII Corps | 1944-11-24 | attack | begins its push to the Roer: takes six miles of front from the Wurm at Müllendorf to the XIX Corps boundary below Ederen | Tongeren, Limburg (headquarters, 10 km, 0.3) | nearest_earlier_command_post (-29 d) | preferred |
| C0538 | 87th Infantry Division | 1944-12-04 | arrival | joins III Corps in Third Army after landing at Le Havre in November | Metz, Moselle (headquarters, 5 km, 0.3) | nearest_later_command_post (+4 d) | preferred |
| C0539 | III Corps | 1944-12-04 | activation | takes its first division, the 87th, in Third Army; had been assigned to Third Army since 10 October | Gravelotte, Moselle (headquarters, 5 km, 0.3) | nearest_later_command_post (+4 d) | preferred |
| C0527 | Seventh Army | 1944-12-08 | hq_move | army command post at Saverne | Saverne, Bas-Rhin (headquarters, 5 km, 0.5) | documented_on_date | preferred |
| C0548 | 106th Infantry Division | 1944-12-11 | regroup | relieves the 2nd Division on the Schnee Eifel front | Saint-Vith, Liège (headquarters, 5 km, 0.5) | documented_on_date | preferred |
| C0547 | 28th Infantry Division | 1944-12-16 | defense | defends the Our-Clerf line when the German offensive opens; division command post at Wiltz | Wiltz, Luxembourg (headquarters, 3 km, 0.7) | documented_on_date | preferred |
| C0550 | 10th Armored Division | 1944-12-17 | relocation | moves north to the Luxembourg-Bastogne area; CCB reaches Bastogne by the 18th | Luxembourg City, Luxembourg (headquarters, 5 km, 0.5) | documented_on_date | preferred |
| C0563 | 101st Airborne Division | 1944-12-17 | command_change | CMH table date for Third Army attachment (alternate to the Green Book date of 20 December) | Mourmelon-le-Grand, Marne (headquarters, 5 km, 0.3) | nearest_earlier_command_post (-16 d) | alternate G016 |
| C0545 | VIII Corps | 1944-12-18 | hq_move | most of the headquarters leaves Bastogne for Neufchâteau; Middleton stays in Bastogne with a small staff | Neufchâteau, Luxembourg (headquarters, 5 km, 0.5) | documented_on_date | preferred |
| C0551 | 82nd Airborne Division | 1944-12-18 | arrival | arrives at Werbomont after being diverted from Bastogne | Werbomont, Liège (headquarters, 3 km, 0.7) | documented_on_date | preferred |
| C0519 | First Army | 1944-12-19 | hq_move | headquarters moves from Spa to Chaudfontaine | Chaudfontaine, Liège (headquarters, 3 km, 0.7) | documented_on_date | preferred |
| C0552 | XVIII Airborne Corps | 1944-12-19 | activation | Ridgway opens the corps command post near the 82nd Airborne and the corps becomes operational under First Army | Habiémont, Lierneux (headquarters, 5 km, 0.5) | documented_on_date | preferred |
| C0553 | 101st Airborne Division | 1944-12-19 | arrival | arrives at Bastogne by truck from Camp Mourmelon; all four regiments in hand by 0900 | Bastogne, Luxembourg (headquarters, 3 km, 0.7) | documented_on_date | preferred |
| C0559 | XII Corps | 1944-12-19 | relocation | ordered to disengage in the Saar and move its command post to Luxembourg City | Luxembourg City, Luxembourg (headquarters, 5 km, 0.3) | nearest_later_command_post (+4 d) | preferred |
| C0517 | 12th Army Group | 1944-12-20 | command_change | First and Ninth Armies pass to 21st Army Group; Bradley keeps the south of the Bulge | Luxembourg City, Luxembourg (headquarters, 5 km, 0.7) | documented_on_date | preferred |
| C0520 | First Army | 1944-12-20 | command_change | passes to 21st Army Group under Montgomery | Chaudfontaine, Liège (headquarters, 3 km, 0.7) | documented_on_date | preferred |
| C0522 | Ninth Army | 1944-12-20 | command_change | passes to 21st Army Group under Montgomery | Maastricht, Limburg (headquarters, 10 km, 0.3) | nearest_earlier_command_post (-56 d) | preferred |
| C0524 | Third Army | 1944-12-20 | command_change | takes command south of the Bulge; VIII Corps passes to it | Nancy, Meurthe-et-Moselle (headquarters, 5 km, 0.5) | nearest_earlier_command_post (-2 d) | preferred |
| C0546 | VIII Corps | 1944-12-20 | command_change | passes from First Army to Third Army | Neufchâteau, Luxembourg (headquarters, 5 km, 0.7) | documented_on_date | preferred |
| C0549 | 106th Infantry Division | 1944-12-20 | command_change | passes to XVIII Airborne Corps; the 12th Army Group column keeps First Army and 21st Army Group listed | Vielsalm, Luxembourg (headquarters, 5 km, 0.5) | nearest_earlier_command_post (-2 d) | preferred |
| C0554 | 101st Airborne Division | 1944-12-20 | command_change | passes with VIII Corps from First Army to Third Army | Bastogne, Luxembourg (headquarters, 3 km, 0.7) | documented_on_date | preferred G016 |
| C0560 | 84th Infantry Division | 1944-12-20 | command_change | leaves Ninth Army's Roer front for First Army; temporarily attached to XVIII Airborne Corps, entering Marche that night | Marche-en-Famenne, Luxembourg (headquarters, 5 km, 0.5) | nearest_later_command_post (+1 d) | preferred |
| C0555 | 101st Airborne Division | 1944-12-21 | defense | Bastogne is surrounded; the division holds a perimeter around the town | Bastogne, Luxembourg (headquarters, 5 km, 0.5) | nearest_earlier_command_post (-2 d) | preferred |
| C0525 | Third Army | 1944-12-22 | attack | III and XII Corps counterattack north toward Bastogne | Nancy, Meurthe-et-Moselle (headquarters, 10 km, 0.3) | nearest_earlier_command_post (-4 d) | preferred |
| C0556 | 4th Armored Division | 1944-12-22 | attack | counterattacks north toward Bastogne with III Corps; H-hour 0600 | Arlon, Luxembourg (headquarters, 5 km, 0.5) | nearest_earlier_command_post (-2 d) | preferred |
| C0558 | III Corps | 1944-12-22 | attack | III Corps counterattack begins from Habay-la-Neuve and Arlon with the 26th, 80th and 4th Armored | Habay-la-Neuve, Luxembourg (sector_center, 10 km, 0.5) | documented_on_date | preferred |
| C0561 | 75th Infantry Division | 1944-12-22 | arrival | arrives in the Ardennes and joins VII Corps in First Army | Ocquier, Liège (headquarters, 5 km, 0.5) | documented_on_date | preferred |
| C0557 | 4th Armored Division | 1944-12-26 | attack | CCR spearhead reaches the Bastogne perimeter at Assenois at 1650 | Assenois, Luxembourg (front_line_point, 3 km, 0.7) | documented_on_date | preferred |
| C0562 | XXI Corps | 1944-12-27 | activation | takes its first division, the 36th, as XXI Corps headquarters takes over a Seventh Army sector in Alsace | Phalsbourg, Moselle (headquarters, 5 km, 0.5) | nearest_later_command_post (+1 d) | preferred |

### 5. Not done (carry to the next pass)

See `docs/roadmap.md`, "Batch 3" for the list. In short: V and VI Corps places; the 99th, 2nd, 9th, 78th and 95th Divisions and the other placeholders still listed as placeholders (9th, 11th, 12th and 14th Armored, 17th Airborne, 42nd); Hurtgen Forest (28th Division at Schmidt, 2 Nov); Metz and Strasbourg; the Colmar pocket beyond XXI Corps; the French First Army and II Corps relationships with Seventh Army; the 7th, 3rd and 9th Armored Divisions in the Bulge; and the First Army move to Tongeren on 24 December.

## Batch 3 review corrections and temporal audit (25 October 2026)

An outside review of the Batch 3 spot check (15 rows) recommended a cross-batch temporal audit before Batch 4. The review was treated as unverified: every point was checked against the Green Books (*Ardennes*, *Siegfried Line*, *Riviera to the Rhine*, *Lorraine*) and the CMH tables, and only what the sources support was applied. Result: 20 existing claim rows corrected (plus `campaign` on all 566 and `operation_name` blanked on 144), 3 new claims (C0564, C0565, C0566), 1 new unit (`US-CCR-004D`), conflict group G016 dissolved, one schema column and two event types added, `who_controls.py` extended, a nine-check audit script added. Batch 4 was not started.

### 1. Verdict on each point

| # | Review point | Verdict | What the sources say / what was done |
|---|---|---|---|
| 1 | C0563 / C0554 / G016: a table date and an operational transfer are not rival claims | **Agree** | The CMH table (VIII Corps, Third Army attached, 12th Army Group attached from 17 December) is a classification; the Green Book has the alert reaching the XVIII Airborne Corps chief of staff on the evening of 17 December (Ardennes p304), Hodges turning the division over to Middleton on 18 December (p306), and VIII Corps passing to Third Army "during the 20th" (p399). G016 is dissolved into a sequence: C0563 (17 December) is a `subordinate_assignment` row with XVIII Airborne Corps as parent and VIII Corps `unspecified_subordination` from 17 December (start between 17 and 18 December); C0553 and C0554 carry VIII Corps `operational_control` from 18 December; the 101st's parent is VIII Corps on 19-21 December; Third Army `attached` starts on C0554 (20 December) and is exercised through the corps. The table's Third Army and 12th Army Group dates are not encoded (kept in the notes). C0563 asserts no Third Army control. The 137 km coordinate exception for the old pair was removed (`data/coordinate_exceptions.csv`: 6 to 5 explained); the two rows no longer need it. `who_controls.py US-ABN-101D 1944-12-20 12:00` answers UNKNOWN at army level (First or Third) because the hour is not documented. |
| 2 | C0560: 84th Division, XVIII Airborne Corps to VII Corps, location inferred | **Agree in part; the sources are later than the review** | The review put VII Corps in control from about 21 December. The Green Book does not: the division was "temporarily attached to the XVIII Airborne Corps" (p426), received XVIII Airborne Corps instructions at noon on 21 December (p430) and on 22 December (p431: Ridgway extended its mission), and the VII Corps "officially assumed" its corps front "at 1630 on 23 December" (p433). The CMH table lists VII Corps from 20 December, which is an administrative date. C0560 now has XVIII Airborne Corps `attached` from 20 December to 23 December with `effective_to_earliest` 22 December and VII Corps `unspecified_subordination` from 20 December with `effective_from_latest` 23 December; its parent is XVIII Airborne Corps; a new row C0565 (VII Corps, 23 December, Durbuy from the atlas) carries the 1630 hour. The Marche point is kept as `nearest_later_command_post` (the command post is documented there on 21 December, p428; p429 has word of the Hotton attack reaching it at 0900 the same day, an inconsistency in the Green Book that the note records) and described as inferred for the 20th; confidence stays 0.5. |
| 3 | C0544: Clipper opened 19 November; XIII Corps "administrative_control" | **Disagree on the date; agree on the label** | Siegfried p545-546: the attack was scheduled originally for D plus 1 and postponed one day, to 18 November; p547 calls 18 November "D Day for Operation Clipper"; p549 gives 0600 (flail tanks) and 0700 (two battalions of the 334th). The date stays 18 November and event support rises from moderate to high. p545 says only that the division was "still tied for other purposes to the XIII Corps", so the entry is `unknown`, not `administrative_control`. `sub_operation_name` is now `Roer; Clipper`. |
| 4 | C0539, C0562: activations inferred from assignment tables; III Corps 18 December; C0532 | **Agree** | C0539 and C0562 are now `subordinate_assignment` (a table lists the first division under the corps), with wording that says so. C0562 no longer says Seventh Army made the corps operational on 27 December (Riviera p533 gives no date). The selection of III Corps for the Bastogne counterattack is on the night of 18 December (Ardennes p509: Bradley and Patton agree to move the headquarters from Metz to Arlon; the 26th, 80th and 4th Armored "selected almost automatically"): new row C0564, event type `other`, an intended-state decision (the attack is C0558, 22 December). C0532 stays `activation` with "first operational sector" wording (XIII Corps took the 17-mile front on 8 November, p401; the headquarters existed earlier). |
| 5 | C0522: Maastricht is last-known | **Agree** | The atlas lists Maastricht from 25 October and nothing until Rheydt on 11 March 1945; the Green Book pages read do not locate the Ninth Army headquarters on 20 December. The note now says "last-known"; the 3 April 1945 end is stated as separately sourced from the tables, outside the window, and the December confidence does not apply to it. |
| 6 | C0552: location inferred | **Agree** | `location_basis` is now `inferred` (the place is the 82nd's command post at Habiémont; the first atlas entry for the corps is Manhay on 20 December). |
| 7 | C0516: hq_move to observation; explain C0222 | **Agree** | New event type `hq_observation`. C0516 (Dompaire, 2 October) is a command-post list observation; the move north is not dated. C0222 (15 September) is not a contradiction: its Batch 1 point was Vesoul, a front-area reference; the Batch 2 review replaced it with the G-3 Section Final Report's Palais de la Foire at Lyon (see "C0222" in the Batch 1 review text); the note on C0516 says so. |
| 8 | C0557: engagement area / CCR component | **Agree on the component; declined the new location kind** | The spearhead was the Reserve Combat Command (Col. Wendell Blanchard) with the 37th Tank Battalion (Lt. Col. Abrams) and the 53rd Armored Infantry Battalion (Ardennes p552-554). New unit `US-CCR-004D` and row C0566 carry the 1650 contact at Assenois; C0557 (the division) is now an `objective` with `representative_point`, 5 km, 0.5. The existing note called the CCR commander "Abrams"; that was wrong (he commanded the 37th Tank Battalion) and is corrected. No `engagement_area` kind: `objective` plus `representative_point` already says it. |
| 9 | C0520: `effective_to` inclusive | **Agree** | `effective_to` is the inclusive last day; documented in `schema/README.md` and the derived table; the note on C0520 says 17 January is the last day of control (the tables' first row without the column is 18 January). Not `valid_until_exclusive`: one convention, documented. |
| 10 | C0517: two outbound transitions | **Agree** | Notes name them: First Army (C0520) and Ninth Army (C0522) each leave to 21st Army Group operational control; the army group's own relationship does not change. |
| 11 | C0546: explicit sequence | **Agree** | First Army `assigned` until the passage (`effective_to` 20 December, `effective_to_earliest` 19 December), Third Army from the passage (`effective_from_latest` 20 December); the boundary day is covered by both and the hour is not documented. |
| 12 | `campaign` column; fix "Overlord" | **Agree** | New required column `campaign` (CMH streamers: Normandy 6 June-24 July; Northern France 25 July-14 September; Southern France 15 August-14 September; Rhineland 15 September 1944-21 March 1945; Ardennes-Alsace 16 December-25 January 1945; Central Europe reserved), backfilled by date for all 566 rows by `scripts/migrate_campaign.py` (Normandy 233, Northern France 222, Rhineland 69, Ardennes-Alsace 26, Southern France 16). It is a date-and-area label, not unit credit. `operation_name` is now optional and dated: Overlord 6 June-30 August, Dragoon 15 August-14 September, Market Garden 17-25 September; blanked on 144 rows after their operation (132 Overlord, 12 Dragoon); `sub_operation_name` kept. Validator: error if the campaign does not cover the date or two campaigns do not overlap there; warning for an operation name outside its dates. |
| 13 | Ordered / effective / exercised states | **Agree, cheap form only** | Methodology and roadmap now describe the four states (intended, ordered, effective, exercised) and what already carries them (`ordered_date`, `effective_from` with optional `effective_time`, narrative rows, `other` rows for decisions such as C0564). The 7th Armored Division's move to St. Vith (chosen by 12th Army Group on the afternoon of 16 December, alerted at 1730, instructions at VIII Corps, Ardennes p273-274) is the motivating example. A state column is left on the roadmap. |
| 14 | Separate numeric event and location confidence | **Declined (third time)** | `confidence` already scores the location and its sources; the `Event support:` and `Location support:` sentences carry the event side in words (the validator requires `Event support:` on low-confidence command rows, now including `subordinate_assignment`); a second number would repeat `location_basis` and the notes and need a judged value for every row. |

Also declined, with reasons: `retained_nonoperational_responsibilities` (a relationship `unknown` with a scoped note does it; AFHQ is the precedent), `inferred_from_nearby_unit_hq` (`inferred` plus a note naming the neighbour), `valid_until_exclusive` (see item 9).

### 2. Schema, scripts and outputs added

- `claims` column `campaign` (required, vocabulary list) and optional `operation_name` with dated vocabulary; event types `subordinate_assignment` and `hq_observation`; relationship-entry keys `effective_time` and `effective_to_time` (HH:MM); `command_relations.csv` columns `valid_from_time` and `valid_to_time`.
- `scripts/who_controls.py UNIT DATE [HH:MM]`: every interval marked certain or possible, then the immediate operational parent and the chain above it, UNKNOWN where two headquarters meet on a boundary day with no hour.
- `scripts/audit_temporal_relationships.py` (read-only, exit 0): nine checks, report in `temporal_audit.md`, non-failing CI step; `scripts/migrate_campaign.py` (one-time, idempotent).
- Other fixes found by the audit (item 3 below): C0332 and C0540 (XV Corps to Seventh Army on 29 September, Riviera p253), C0198 and C0312 (dates moved into the entries).

### 3. The temporal audit

Nine checks over all 566 claims: overlap, parent_in_force, start_disagree, relisted_after_end, parent_change, echelon_skip, change_undated, same_day_place, group_date_spread (definitions in the script's docstring and in `docs/methodology.md`). The full triage is in `temporal_audit.md`. In brief: 17 findings from the tightened checks (four checks were first written too loosely and returned 71, 31, 15 and 7 findings, nearly all benign, and were tightened rather than reported). Real and fixed: 4 findings, 3 edits (XV Corps had Seventh Army from 15 September, which is Seventh Army's own date to the 6th Army Group; the source says 29 September and the Third Army link ends the same day; KG Weidinger and VIII Corps carried their transfer dates only in the note). Real and left open: 7 (the 101st has no row between 20 September and 17 December; five German June 1944 parent changes with no dated entry; G012's event types differ, landing against arrival). Explained patterns: 6 (two later periods of the same relationship counted twice, two a table-restatement effect, one subordinate-passing row, one sector point beside a headquarters point). Not found: two same-echelon holders over one unit, a parent not in force on the row date, a parent that skips an echelon.

### 4. Checks, before and after

| check | before (563 claims) | after (566 claims) |
|---|---|---|
| `validate.py` | OK, 12 warnings, 113 claim files, 353 units, 15 conflict groups | OK, 12 warnings (the same 12), 114 claim files, 354 units, 14 conflict groups |
| `build.py --check` | up to date | up to date |
| `check_coordinates.py` | 3 warnings, 6 explained exceptions | 3 warnings (C0253, C0419, C0480, unchanged), 5 explained exceptions (the G016 pair removed) |
| `audit_command_location.py` | unspecified_subordination 223; HQ town centroid 141 (corps/army 7); inferred or unresolved 2; derived-end entries 35 | unspecified_subordination 220; HQ town centroid 142 (corps/army 8: C0564 Metz); inferred or unresolved 3 (C0552); derived-end entries 35 |
| `audit_temporal_relationships.py` | n/a | 17 findings on the first run of the tightened checks; 13 on the final run after the fixes (7 open, 6 explained), see item 3 |
| `who_controls.py` | n/a | `US-ABN-101D 1944-12-20 12:00` UNKNOWN (First or Third Army); `US-ABN-101D 1944-12-22` VIII Corps, Third Army; `US-INF-084D 1944-12-21` XVIII Airborne Corps, First Army; `US-COR-015C 1944-10-15` Seventh Army |

### 5. Rows changed

C0563, C0553, C0554, C0555 (101st sequence); C0546 (VIII Corps); C0560 (84th); C0544 (84th, Clipper); C0539, C0562, C0532 (corps events); C0522, C0517, C0520 (armies and army group); C0552 (XVIII Airborne Corps); C0516 (6th Army Group); C0557 (4th Armored); C0332, C0540 (XV Corps); C0198 (KG Weidinger); C0312 (VIII Corps). New: C0564 (III Corps, 18 December), C0565 (VII Corps, 23 December), C0566 (Combat Command Reserve, 4th Armored, 26 December). `campaign` added to all rows; `operation_name` blanked on 144. Spot checks: Batch 3 regenerated in post-review state (18 rows); Batch 1 and 2 refreshed only for the `campaign` column and the corrected `operation_name`.

### 6. Open items

- The hour of VIII Corps' passage to Third Army (20 December) and the division-level date of the 84th's passage to VII Corps are not documented; both are carried as ranges.
- The 101st Airborne Division has no rows for 21 September to 16 December 1944 (Holland, return to Mourmelon); five German parent changes in June 1944 are undated; G012 (4th Armored landing date and event type) needs a source check.
- C0560's location for the 20th is a next-day command post; no source places the division headquarters on the 20th.
- Batch 4 is not started.
