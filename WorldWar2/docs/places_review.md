# Places review: decisions needed

Produced with the places table (`scripts/migrate_places.py`, branch `places-table`). The migration was conservative: places were merged only when the (accent-folded) first name part matched and the points lay within 3 km of one another; a sector, area, beach, front or axis stays its own place even when its point is the geocoded centre of a town. The lists below are what Scott may want to change. Nothing here is an error: each item is a judgment call, and merging two places is a small edit (change `place_id` in the claim rows, delete the row, add the name to `alt_names`).

## Counts

- 421 distinct `location_name` values became 383 places (288 point, 79 area, 16 line); 26 places absorb 2-5 old names each (list 1), 14 aliases on 13 places, 4 places with a hand-worked point (list 5).
- 566 claims: 286 places have one claim, 62 have two, 16 three, 9 four, and 10 have five or more (largest PL0045 Brest, PL0258 Omaha Beach: 10 claims each).
- After the place merges of item 8 (section 7): 380 places (285 point, 79 area, 16 line); retired ids in `data/place_merges.csv`: 3.
- 20 claims keep their own point with a `coord_override` (list 3).
- Countries by the point's GeoNames nearest place: FR 332, BE 28, NL 10, DE 5, GB 4, LU 4. Places near a border (Saint-Vith, Luxembourg, the Netherlands and Belgium, Aachen) should be glanced at: the lookup uses the nearest GeoNames place, not a boundary polygon.

## 1. Merges made (old names that now share a place)

These are the 26 places that absorbed more than one old `location_name`. The old text is still shown in `build/all_claims.csv` `location_name` (derived from the place name and `location_qualifier`; 27 rows show a normalised spelling).

```
PL0001 Aachen, North Rhine-Westphalia | point | 2 old names
    Aachen (objective of the VII Corps drive) - 1
    Aachen, North Rhine-Westphalia - 1
PL0004 Alençon, Orne | point | 2 old names
    Alençon, Orne - 1
    Alencon, Orne - 1
PL0023 Avranches, Manche | point | 2 old names
    Avranches, Manche - 2
    vicinity of Avranches, Manche - 1
PL0045 Brest, Finistère | point | 3 old names
    Brest, Finistère - 8
    Brest, Finistère (departure area) - 1
    Brest, Finistère (Place du Président Wilson) - 1
PL0059 Caen sector | area | 2 old names
    Caen sector (corps HQ not verified) - 1
    Caen sector (counter-attacks on 3rd Infantry/3rd Canadian Divisions) - 1
PL0067 Carentan, Manche | point | 3 old names
    Carentan - 4
    Carentan, Manche - 1
    Carentan (counterattack southwest of the town) - 1
PL0068 Carentan / Manoir de Donville | area | 2 old names
    Carentan / Manoir de Donville (Méautis) - 1
    Carentan / Manoir de Donville (Meautis) - 1
PL0081 Châteaubriant, Loire-Atlantique | point | 2 old names
    Châteaubriant, Loire-Atlantique - 1
    Chateaubriant, Loire Infre - 1
PL0107 Coutances, Manche | point | 2 old names
    Coutances, Manche (objective of the 26 July attack; not the corps headquarters or its position) - 1
    vicinity of Coutances, Manche - 2
PL0114 Dieulouard, Meurthe-et-Moselle | point | 2 old names
    vicinity of Dieulouard, Meurthe-et-Moselle - 1
    Dieulouard, Meurthe-et-Moselle - 1
PL0135 Epsom attack area | area | 2 old names
    Epsom attack area (point = Cheux; army HQ not verified) - 1
    Epsom attack area (point = Cheux, first-day objective) - 1
PL0171 Hebecrevon, Manche | point | 2 old names
    Hébécrevon (where Marcks was killed, near Saint-Lô) - 1
    Hebecrevon, Manche - 1
PL0206 Le Mans, Sarthe | point | 5 old names
    Le Mans - 1
    Le Mans (7th Army HQ) - 1
    Le Mans (7th Army HQ; Dollmann died there per Wikipedia) - 1
    vicinity of Le Mans, Sarthe - 1
    Le Mans, Sarthe - 2
PL0213 Marigny, Manche | point | 4 old names
    Marigny, Manche (objective of the 26 July attack; not the division position) - 1
    Marigny, Manche (Cobra penetration area) - 2
    Marigny, Manche (objective of the 26 July column; not the corps headquarters) - 1
    Marigny, Manche - 2
PL0222 Mesnil-St-Martin, Manche | point | 2 old names
    Le-Mesnil-St-Martin, Manche (unresolved CMH place name) - 1
    vicinity of Mesnil-St-Martin, Manche (unresolved CMH place name) - 2
PL0228 Mons, Hainaut | point | 2 old names
    Mons, Belgium - 3
    vicinity of Mons, Hainaut - 1
PL0258 Omaha Beach | area | 4 old names
    Omaha Beach (Colleville-sur-Mer sector) - 1
    Omaha Beach (Vierville-sur-Mer sector) - 1
    Omaha Beach - 6
    Omaha Beach, Manche - 2
PL0261 Orléans, Loiret | point | 2 old names
    Orleans, Loiret - 2
    Orléans, Loiret - 1
PL0263 Orne bridgehead | area | 2 old names
    Orne bridgehead (east of Caen) - 1
    Orne bridgehead (Bréville-Ranville area) - 1
PL0279 Plouay, Morbihan | point | 2 old names
    vicinity of Plouay, Morbihan - 2
    Plouay, Morbihan - 1
PL0308 Southern Cotentin front | line | 2 old names
    Southern Cotentin front (La Haye-du-Puits approach) - 1
    Southern Cotentin front (representative) - 1
PL0309 Southern front, First Army zone | line | 2 old names
    Southern front, First Army zone (Saint-Lô sector, representative point) - 1
    Southern front, First Army zone (representative point) - 1
PL0324 Saint-Gilles, Manche | point | 2 old names
    Saint-Gilles, Manche - 1
    Saint-Gilles, Manche (objective of the 26 July attack; not the division position) - 1
PL0333 Saint-Lô, Manche | point | 4 old names
    Saint-Lô - 1
    Saint-Lô (corps HQ per Wikipedia, not tied to 10 June) - 1
    St-Lo, Manche - 1
    Saint-Lô, Manche - 1
PL0343 Saint-Vith, Liège | point | 2 old names
    Saint-Vith, Liège - 1
    St Vith, Liege - 1
PL0357 Utah Beach | area | 3 old names
    Utah Beach - 5
    Utah Beach, Manche (landing area) - 1
    Utah Beach, Manche - 2
Places with more than one old name: 26
```

## 2. Co-located places left separate (the main decision list)

A coordinate group is places whose points agree to 0.001 degree (about 100 m). They are separate because the names differ in kind (a town and the sector or front built on it), or because it is not certain that two names are the same place. 37 groups, 101 places after the merges of section 7; the full list follows. The five likely merge candidates were decided (item 8); the table shows what was done to each:

| Places | Why they may be one place |
|---|---|
| PL0070 Caumont / PL0071 Caumont-l'Éventé | **Merged** into PL0071 (see section 7); the same commune (Caumont-l'Éventé, Calvados), 0 m apart |
| PL0208 Mantes-Gassicourt / PL0209 Mantes-la-Jolie | **Merged** into PL0209 (see section 7); Gassicourt is a former village annexed to Mantes in 1930 (an earlier version of this table said 1962) and now a district of Mantes-la-Jolie; the town was called Mantes-Gassicourt until 1953; 0 m apart (PL0207 is the bridgehead area on the same point) |
| PL0045 Brest, Finistère / PL0294 Recouvrance, Brest | **Merged** into PL0045 (see section 7); Recouvrance is the district of Brest on the west bank of the Penfeld; 0 m apart |
| PL0258 Omaha Beach / PL0259 Omaha Beach sector | the beach and its sector share the point (both areas) |
| PL0173 Hill 112 / PL0174 Hill 112 / Odon salient | same point; the second is the wider salient, an area |

The groups (rounded point, then each place with its kind, name and claim count):

```
(49.12, -1.09) PL0154 line "Front before Saint-Lô" (1) | PL0309 line "Southern front, First Army zone" (2) | PL0330 area "Saint-Lô area" (1) | PL0331 area "Saint-Lô-Caumont gap sector" (1) | PL0333 point "Saint-Lô, Manche" (4) | PL0334 area "Saint-Lô sector" (1)
(49.167, -0.525) PL0016 area "Assembly west/south of Caen" (1) | PL0092 point "Cheux" (7) | PL0093 area "Cheux sector" (1) | PL0135 area "Epsom attack area" (2) | PL0136 line "Epsom front" (1)
(49.241, -0.226) PL0047 point "Bréville-les-Monts" (1) | PL0263 area "Orne bridgehead" (2) | PL0264 area "Orne bridgehead east bank" (4) | PL0265 area "Orne bridgehead / east of Caen" (1) | PL0317 area "Sainte-Honorine area, east of the Orne" (1)
(49.304, -1.247) PL0067 point "Carentan, Manche" (6) | PL0068 area "Carentan / Manoir de Donville" (2) | PL0069 area "Carentan / Vire crossing" (1) | PL0310 area "Southwest of Carentan" (1) | PL0380 area "West of Carentan" (1)
(49.335, -0.415) PL0158 area "Gold-Juno-Sword landing zone" (1) | PL0180 area "Juno Beach" (4) | PL0181 area "Juno/Sword" (2) | PL0185 area "Landed Normandy beachhead" (1) | PL0251 area "Normandy beachhead" (2)
(49.171, -0.579) PL0146 point "Fontenay-le-Pesnel" (2) | PL0147 area "Fontenay-le-Pesnel / Rauray sector" (1) | PL0270 area "Panzer Lehr sector" (1) | PL0348 area "Tilly-Fontenay sector" (1)
(49.091, -0.804) PL0048 area "Brigade box west of Villers-Bocage" (1) | PL0071 point "Caumont-l'Éventé" (3)
(49.181, -0.364) PL0057 point "Caen" (1) | PL0059 area "Caen sector" (2) | PL0060 area "Caen sector assembly areas" (1)
(43.273, 6.64) PL0066 area "Cape Saint-Tropez landing area, Var" (1) | PL0123 area "Dragoon assault area (Alpha, Delta and Camel sectors), Var coast" (1) | PL0342 point "Saint-Tropez, Var" (1)
(49.488, -1.378) PL0074 line "Central Cotentin axis, north of Valognes" (1) | PL0230 point "Montebourg Station" (1) | PL0231 line "Montebourg-Valognes axis" (1)
(49.52, -1.47) PL0102 area "Cotentin sector" (4) | PL0358 point "Valognes" (2) | PL0359 line "Valognes–Montebourg axis" (1)
(49.291, -1.541) PL0103 area "Cotentin west" (1) | PL0239 area "Moving south from Cherbourg to VIII Corps zone" (1) | PL0308 line "Southern Cotentin front" (2)
(49.387, -1.531) PL0121 line "Douve line, Sainte-Colombe / Saint-Sauveur-le-Vicomte area" (1) | PL0122 line "Douve River line / St-Sauveur-le-Vicomte axis" (1) | PL0339 point "Saint-Sauveur-le-Vicomte" (1)
(49.183, -0.892) PL0130 area "Elle River south of Foret de Cerisy" (1) | PL0149 area "Forêt de Cerisy" (1) | PL0150 area "Forêt de Cerisy / Caumont gap sector" (1)
(49.306, -0.321) PL0157 area "Gold/Juno/Sword" (1) | PL0344 area "Sword Beach" (1) | PL0345 area "Sword/Juno beaches" (1)
(49.139, -0.528) PL0161 point "Grainville-sur-Odon" (3) | PL0162 area "Grainville-sur-Odon / Odon salient" (1) | PL0378 area "West flank of the Odon salient" (1)
(48.991, 1.717) PL0207 area "Mantes-Gassicourt bridgehead area (Seine), Yvelines" (3) | PL0209 point "Mantes-la-Jolie, Yvelines" (4)
(49.207, -0.431) PL0019 point "Authie" (2) | PL0020 line "Authie-Carpiquet line" (1)
(47.24, 6.02) PL0038 point "Besançon, Doubs" (1) | PL0119 area "Doubs valley west of Besançon" (1)
(48.115, -1.679) PL0051 area "Brittany" (1) | PL0296 point "Rennes, Ille-et-Vilaine" (3)
(48.984, -0.473) PL0061 area "Caen sector (HQ around Thury-Harcourt; see 10 June)" (1) | PL0347 point "Thury-Harcourt" (2)
(49.067, -0.767) PL0062 point "Cahagnes" (1) | PL0063 line "Cahagnes - Villers-Bocage axis" (1)
(49.667, -1.833) PL0065 point "Cap de la Hague" (1) | PL0090 area "Cherbourg harbour forts / Cap de la Hague" (1)
(49.63, -1.62) PL0089 point "Cherbourg" (8) | PL0091 area "Cherbourg outer defences" (1)
(49.286, -0.1) PL0094 area "Coast east of the Orne/Dives" (1) | PL0266 area "Orne-Dives bridgehead" (1)
(49.409, -1.318) PL0101 area "Cotentin airborne landing area" (1) | PL0320 point "Sainte-Mère-Église" (2)
(49.157, -1.059) PL0131 area "Elle River / Villiers-Fossard sector" (2) | PL0374 point "Villiers-Fossard" (4)
(49.422, -1.409) PL0160 area "Gourbesville / Pont-l-Abbe area" (1) | PL0381 area "West of the Merderet" (2)
(49.124, -0.461) PL0173 point "Hill 112" (1) | PL0174 area "Hill 112 / Odon salient" (1)
(49.319, -1.101) PL0177 point "Isigny-sur-Mer" (1) | PL0178 area "Isigny / Vire–Elle sector" (2)
(51.565, 5.461) PL0186 area "Landing zones between Son and Veghel (centred at Sint-Oedenrode), Noord-Brabant, Netherlands" (1) | PL0336 point "St-Oedenrode, Nord Brabant, Netherlands" (1)
(49.176, -0.625) PL0192 area "Lingeves / Tilly-sur-Seulles sector" (1) | PL0349 point "Tilly-sur-Seulles" (4)
(50.85, 5.683) PL0202 area "Maastricht area, Albert Canal–Meuse" (1) | PL0203 point "Maastricht, Limburg" (2)
(49.1, -1.239) PL0213 point "Marigny, Manche" (6) | PL0214 area "Marigny–Saint-Gilles gap, Manche" (1)
(49.139, -0.516) PL0227 point "Mondrainville" (4) | PL0256 area "Odon bridgehead" (1)
(49.369, -0.869) PL0258 area "Omaha Beach" (10) | PL0259 area "Omaha Beach sector" (1)
(49.309, -0.903) PL0352 point "Trévières, Calvados" (1) | PL0353 area "Treviers-Mosles area" (1)
```

## 3. Claims that keep their own point (`coord_override`)

Within a merged cluster the place has the most-used point and a claim that read a different point keeps it. 20 claims, 37 m to 1.66 km from the place point:

| Claim | Unit | Place | Distance | Reason in `coord_override` |
|---|---|---|---|---|
| C0243 | US-ARM-004D | PL0357 Utah Beach | 294 m | OpenStreetMap Nominatim (Utah Beach, Sainte-Marie-du-Mont); 290 m from the place point |
| C0269 | US-ARM-006D | PL0222 Mesnil-St-Martin, Manche | 1146 m | OpenStreetMap Nominatim (Le-Mesnil-Saint-Martin, Manche, France); 1150 m from the place point |
| C0272 | US-ARM-006D | PL0023 Avranches, Manche | 215 m | OpenStreetMap Nominatim (Avranches, Manche, France); 220 m from the place point |
| C0512 | US-ARM-006D | PL0279 Plouay, Morbihan | 219 m | Wikipedia (en): Plouay; 220 m from the place point |
| C0513 | US-ARM-006D | PL0081 Châteaubriant, Loire-Atlantique | 185 m | Wikipedia (en): Châteaubriant; 190 m from the place point |
| C0491 | US-COR-005C | PL0004 Alençon, Orne | 162 m | Wikipedia (en): Alençon; 160 m from the place point |
| C0310 | US-COR-008C | PL0107 Coutances, Manche | 470 m | Wikipedia (en): Coutances; 470 m from the place point |
| C0321 | US-COR-012C | PL0261 Orléans, Loiret | 37 m | Wikipedia (en): Orléans; 37 m from the place point |
| C0372 | US-INF-005D | PL0361 Verdun, Meuse | 351 m | OpenStreetMap Nominatim (Verdun, Meuse, France); 350 m from the place point |
| C0375 | US-INF-008D | PL0357 Utah Beach | 294 m | OpenStreetMap Nominatim (Utah Beach, Manche, France); 290 m from the place point |
| C0376 | US-INF-008D | PL0357 Utah Beach | 294 m | OpenStreetMap Nominatim (Utah Beach, Manche, France); 290 m from the place point |
| C0382 | US-INF-009D | PL0213 Marigny, Manche | 274 m | OpenStreetMap Nominatim (Marigny, Manche, France); 270 m from the place point |
| C0390 | US-INF-028D | PL0258 Omaha Beach | 769 m | OpenStreetMap Nominatim (Omaha Beach, France); 770 m from the place point |
| C0391 | US-INF-028D | PL0258 Omaha Beach | 769 m | OpenStreetMap Nominatim (Omaha Beach, France); 770 m from the place point |
| C0413 | US-INF-030D | PL0171 Hebecrevon, Manche | 107 m | OpenStreetMap Nominatim (Hebecrevon, Manche, France); 110 m from the place point |
| C0425 | US-INF-035D | PL0333 Saint-Lô, Manche | 472 m | OpenStreetMap Nominatim (Saint-Lo, Manche, France); 470 m from the place point |
| C0430 | US-INF-035D | PL0206 Le Mans, Sarthe | 124 m | OpenStreetMap Nominatim (Le Mans, Sarthe, France); 120 m from the place point |
| C0465 | US-INF-080D | PL0114 Dieulouard, Meurthe-et-Moselle | 202 m | OpenStreetMap Nominatim (Dieulouard, Meurthe-et-Moselle, France); 200 m from the place point |
| C0467 | US-INF-083D | PL0067 Carentan, Manche | 1093 m | OpenStreetMap Nominatim (Carentan, Manche, France); 1090 m from the place point |
| C0548 | US-INF-106D | PL0343 Saint-Vith, Liège | 1658 m | Wikipedia (en): St. Vith; 1660 m from the place point |

Decision: where a point differs by a few hundred metres only because two geocoders were used, the override could be dropped and the claim moved to the place point (the claim point then changes in `claims.geojson`); it was kept so that no published position moved in this migration.

## 4. Close pairs of points (`check_coordinates.py --duplicates`)

Places of kind point within 1 km of each other:

- PL0070 Caumont and PL0071 Caumont-l'Éventé, 0 m (merged, see section 7)
- PL0208 Mantes-Gassicourt and PL0209 Mantes-la-Jolie, 0 m (merged, see section 7)
- PL0045 Brest and PL0294 Recouvrance, 0 m (merged, see section 7)
- PL0089 Cherbourg and PL0152 Fort du Roule, 459 m (the fort is part of the town's defences; probably different places)
- PL0107 Coutances and PL0285 Pont Herbert, 172 m (suspect data, see 6)
- PL0161 Grainville-sur-Odon and PL0227 Mondrainville, 911 m (different villages; keep)

## 5. Places with a hand-worked point

These have a blank `coord_reference_id` and the explanation in `coord_source_note`: PL0022 Avranches–Brécey gap (midpoint of two Wikipedia coordinates), PL0120 Douve bridgehead objective south of Pont-l'Abbe (commune centroid, approximate), PL0225 Meuse crossings between Verdun and Commercy (midpoint), PL0286 Pont-l'Abbe (commune centroid, approximate). A real point could replace the last two.

## 6. Suspect data noticed and not changed

- `Pont Herbert, Manche` (PL0285, claim C0225 of US-ARM-002D) lies 172 m from Coutances. Pont-Hébert is a different commune (about 25 km to the north-east); the point looks wrong or the name is a mix-up. It is a different place from Pont-Hébert, so it was not merged with anything.
- `St Anthonis, Nort Brabant` (PL0314) has a point in Belgium (Flanders, 51.18 N 4.19 E) although the name says North Brabant; St. Anthonis in the Netherlands is near 51.6 N 5.9 E (country and region come from the point, so the place reads as Belgian). The point should be checked against the source.
- Place `precision_km` is the finest precision any claim at the place has used (it is not a statement about the place itself); claims keep their own `precision_km`.

## 7. Place merges made (item 8, branch `place-merges`)

Item 8 of `docs/unit_references_review.md`: the five likely merge candidates of section 2 were decided and merged, one commit each, with `scripts/migrate_place_merges.py`. The survivor keeps its id and point; the retired id is listed in `data/place_merges.csv` and never reused; every moved claim keeps its own `precision_km`, `coord_override` and point, so no position in `build/claims.geojson` changed; the derived `location_name` of the moved claims changed (the survivor's name plus the qualifier). The `coord_reference_id` of each pair was the same, so nothing changed there. The other co-located places of section 2 are unchanged: where a group lost a place it is shown in its new form, the other groups are as before.

- **PL0070 Caumont -> PL0071 Caumont-l'Éventé.** The same commune (Caumont-l'Éventé, Calvados): both places used the point of the Wikipedia article Caumont-l'Éventé, 0 m apart. `Caumont` is now an alias of PL0071. One claim moved (C0104, V Corps, 13 June 1944); it keeps its qualifier `left of First Army line` and its own `precision_km` 10.

- **PL0208 Mantes-Gassicourt, Yvelines -> PL0209 Mantes-la-Jolie, Yvelines.** Checked first: Gassicourt is a district of Mantes-la-Jolie, not a separate commune. The English Wikipedia article Mantes-la-Jolie says the commune absorbed Gassicourt in 1930 (the merged commune was called Mantes-Gassicourt until it was renamed Mantes-la-Jolie on 7 May 1953) and lists Gassicourt among the four districts of the city; the French article describes Gassicourt as the former village west of the historic centre, annexed in 1930, now a residential district. A Nominatim read of the district (https://nominatim.openstreetmap.org/search?q=Gassicourt,+Mantes-la-Jolie) lies 1.85 km west of the shared point, inside the commune, under the 2 km limit set for this merge. In 1944 `Mantes-Gassicourt` was the name of the whole town, so it is kept as an alias of PL0209. Two claims moved (C0330 XV Corps and C0451 79th Infantry Division, both 19 August 1944: the 79th Division started across the Seine near Mantes that evening); they keep their precision (10 and 5 km) and get the qualifier `Mantes-Gassicourt, Seine crossing`. PL0207 (the bridgehead area on the same point) is a different kind of place and stays.

- **PL0294 Recouvrance, Brest -> PL0045 Brest, Finistère.** Recouvrance is a historic district of Brest on the Penfeld (https://fr.wikipedia.org/wiki/Recouvrance_(Brest)); both places used the Wikipedia point of Brest, 0 m apart (a Nominatim read of the district is 1.2 km away). `Recouvrance` is now an alias of PL0045. One claim moved (C0408, 29th Infantry Division, 18 September 1944: Von der Mosel surrendered the troops in Recouvrance); it gets the qualifier `Recouvrance district` and keeps its `precision_km` 3.
