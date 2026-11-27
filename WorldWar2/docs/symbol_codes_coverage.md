# Symbol codes (SIDC) coverage report (roadmap 410 proposal)

> **Historical snapshot (23 November 2026).** This page reports SIDC coverage from a snapshot on branch `symbol-codes-410` of `data/units.csv` at `main` `62e65fd7` (2,635 units). It is not a live coverage report. Current derived codes are in `build/unit_symbols.csv` and the `sidc` column of the claims outputs.

Generated 23 November 2026 on branch `symbol-codes-410` from `data/units.csv` (main `62e65fd7`), `data/sidc_function_map.csv` and `data/sidc_echelon_map.csv` with a scratch evaluator that is not part of the repository; regenerated after Scott accepted the proposal (23 November 2026), with the question 12 rule for the Führer-Begleit-Brigade. The derived codes themselves are in `build/unit_symbols.csv` and the `sidc` column of the claims outputs (`scripts/sidc.py`). (`build/other_domains/` was folded into the unified `build/` files on 24 November 2026; filter on the `domain` column.)

Rule order: the first `function` rule whose conditions all hold (domain, echelon, ship_type, name pattern; a blank domain in `units.csv` counts as ground) gives the symbol set, entity and modifiers; then the two `addon` rules apply to land units only. In the SIDC patterns below `S` stands for the standard identity, which comes from the allegiance table on the date.

## Summary

- Units: 2635. Mapped by a rule: 2635. Fall through to the unspecified land default (GZ99): 0.
- By kind of match: default 1328, exact 695, no-exact 410, nearest 188, default-infantry 14.
  - `exact`: the 2525D entity is the arm or ship type itself. `nearest`: no exact entity, the nearest one (listed in the proposal). `no-exact`: one of the no-exact-symbol cases Scott decided on 23 November (headquarters, Kampfgruppen, fortresses, naval formations and so on). `default`: the domain default (other flying units, other naval formations). `default-infantry`: a land unit whose name names no arm (listed below).
- Add-on rules: ADD-ABN (modifier 2 Airborne) 3 units; ADD-TF (Task Force digit) 31 units.
- Ambiguous (the rule would change if the parenthesised part of the name were ignored, or the function changed on a date): 47 units, of which the ones that need a decision are listed below.

## Units per rule

| rule | kind | domain | match | SIDC pattern | units |
|---|---|---|---|---|---|
| HQ01 | no-exact | any | `Oberkommando der Wehrmacht` | `100S1002261100000000` | 1 |
| HQ02 | no-exact | any | `Supreme Headquarters\|Allied Force Headquarters\|Oberbefehlshaber\|Wehrmachtbefehlshaber\|Strategic Air Forces\|Allied Expeditionary Air Force` | `100S1002251100000000` | 7 |
| HQ03 | no-exact | any | `Luftgau\|Wehrkreis\|District` | `100S1002221100000000` | 4 |
| SH-BB | exact | naval | ship_type BB | `100S3000001202010000` | 7 |
| SH-BC | nearest | naval | ship_type BC |  | 0 |
| SH-BM | nearest | naval | ship_type BM | `100S3000001202000000` | 2 |
| SH-CA | exact | naval | ship_type CA | `100S3000001202020002` | 5 |
| SH-CL | exact | naval | ship_type CL | `100S3000001202020003` | 19 |
| SH-CV | exact | naval | ship_type CV |  | 0 |
| SH-CVL | exact | naval | ship_type CVL |  | 0 |
| SH-CVE | nearest | naval | ship_type CVE |  | 0 |
| SH-DD | exact | naval | ship_type DD | `100S3000001202030000` | 92 |
| SH-DE | nearest | naval | ship_type DE | `100S3000001202030400` | 39 |
| SH-PF | exact | naval | ship_type PF | `100S3000001202040000` | 7 |
| SH-CORV | exact | naval | ship_type CORV | `100S3000001202050000` | 20 |
| SH-TB | nearest | naval | ship_type TB | `100S3000001202031700` | 6 |
| SH-PG | nearest | naval | ship_type PG | `100S3000001205020000` | 7 |
| SH-CM | exact | naval | ship_type CM | `100S3000001204010000` | 1 |
| SH-AM | exact | naval | ship_type AM | `100S3000001204020000` | 102 |
| SH-AGC | exact | naval | ship_type AGC | `100S3000001203010000` | 5 |
| SH-APA | nearest | naval | ship_type APA | `100S3000001203000000` | 1 |
| SH-AV | nearest | naval | ship_type AV | `100S3000001301000000` | 1 |
| SH-SS | exact | naval | ship_type SS | `100S3500001101000002` | 52 |
| NF01 | exact | naval | `\(Task Force \d\|Task Force \d` | `100S3000001210020000` | 5 |
| NF02 | exact | naval | `Task Group \d\|\(TG \d` | `100S3000001210030000` | 20 |
| NF03 | exact | naval | `Task Unit\|Sweep Unit` | `100S3000001210040000` | 2 |
| NF04 | no-exact | naval | `Kommand\|Befehlshaber\|Führer der\|Group Command\|Admiral\|K-Stab\|Flag Officer\|Commander-in-Chief\|C-in-C` | `100S3002001210000000` | 16 |
| NF09 | no-exact | naval | `U-Bootsjagd\|U-Jagd\|U-Jäger\|Anti-Submarine\|Submarine Chaser` | `100S3000001210000300` | 1 |
| NF05 | no-exact | naval | `Unterseeboot\|Submarine Flotilla` | `100S3500001100000000` | 8 |
| NF06 | no-exact | naval | `Minesweep\|Minensuch\|Räumboot\|Sweep\|Minesweeper` | `100S3000001210000700` | 40 |
| NF07 | no-exact | naval | `Torpedo\|Schnellboot\|MTB\|PT Boat\|Motor Gun\|MGB\|Torpedoboot` | `100S3000001210001700` | 24 |
| NF08 | no-exact | naval | `Escort\|Sicherung\|Vorposten\|Support Group` | `100S3000001210000400` | 12 |
| NF99 | default | naval | (any) | `100S3000001210000000` | 321 |
| AD01 | no-exact | any | `Flak-Regiment 155 \(W\)` | `100S1000161307000000` | 5 |
| AD02 | exact | any | `Flak\|Anti-Aircraft\|Air Defense\|Air Defence` | `100S1000161301000000` | 25 |
| AS01 | no-exact | air | `Service Command` | `100S1000211600007800` | 1 |
| AS02 | no-exact | air | `Servicing\|Service Echelon\|Maintenance\|Salvage\|Repair\|Ground Support Unit\|Glider Maintenance\|Parachute Servicing` | `100S1000141611007800` | 165 |
| AS03 | nearest | air | `Marine Craft\|Air Sea Rescue\|Air-Sea Rescue` | `100S1000141418004600` | 60 |
| AS04 | nearest | air | `Staging Post` | `100S1000141202000000` | 4 |
| AN01 | nearest | air | `Observation Squadron\|VCS\|VOS` | `100S1000161208014600` | 1 |
| AN02 | nearest | air | `Naval Air Squadron\|Fleet Air Arm\|Fleet Air Wing\|Naval Fighter Wing\|\(VB-\|Bombing Squadron \d+\|Patrol Bombing\|\(VPB` | `100S1000161208004600` | 20 |
| AR01 | exact | air | `Reconnaissance\|Aufklärung\|Photographic\|Wettererkundung\|Weather\|\(PR\)\|Photo` | `100S1000171208010000` | 45 |
| AF99 | default | air | (any) | `100S1000161208000000` | 1007 |
| GF01 | no-exact | any | `Fortress\|Festung\|Garrison` | `100S1000001211000000` | 4 |
| GA01 | no-exact | any | `Volks-Artillerie-Korps\|Volksartilleriekorps` | `100S1000181303000000` | 12 |
| GA02 | nearest | any | `Marine-Artillerie\|Coast Artillery\|Coastal Artillery\|Küstenartillerie` | `100S1000161303004600` | 1 |
| GA03 | exact | any | `Artillerie\|Artillery\|Werfer\|Nebelwerfer\|Rocket` |  | 0 |
| GE01 | exact | any | `Fallschirm-Pionier\|Airborne Engineer\|Parachute Engineer` | `100S1000161407000001` | 2 |
| GE02 | exact | any | `Pionier\|Engineer\|Sapper` |  | 0 |
| GS01 | exact | any | `Nachrichten\|Signal` | `100S1000161110000001` | 1 |
| GT01 | exact | any | `Tank Destroyer\|Panzerjäger\|Anti-Tank\|Antitank` | `100S1000161204000001` | 2 |
| GT02 | nearest | any | `Sturmgeschütz\|Assault Gun\|StuG` | `100S1000181204010000` | 1 |
| GM01 | exact | any | `Panzergrenadier\|Panzer-Grenadier\|Armored Infantry\|Mechanized\|Führer-Begleit` | `100S1000211211020000` | 5 |
| GP01 | exact | any | `Airborne\|Parachute\|Fallschirm\|Luftlande\|Glider\|Air Landing` | `100S1000231211000001` | 32 |
| GK01 | no-exact | any | `Kampfgruppe\|Combat Command\|Task Force\|Kampfgruppen` | `100S1004171210000000` | 29 |
| GR01 | exact | any | `Heavy Panzer\|schwere Panzer\|s\.Pz\|Heavy Tank` | `100S1000161205000015` | 1 |
| GR02 | exact | any | `Panzer\|Armou?red\|Tank\|Armour\|Armor` | `100S1000181205000000` | 67 |
| GC01 | exact | any | `Reconnaissance\|Aufklärung\|Cavalry\|Recce` |  | 0 |
| GG01 | exact | any | `Gebirgs\|Mountain\|Alpine` | `100S1000211211000027` | 6 |
| GX01 | nearest | any | `Commando\|Special Service` | `100S1000181211007600` | 3 |
| GL01 | nearest | any | `Polizei\|Police` | `100S1000171417000000` | 1 |
| GU01 | nearest | any | `RAF Regiment` | `100S1000151211000000` | 41 |
| GI01 | exact | any | `Infantry\|Infanterie\|Grenadier\|Volksgrenadier\|Rifle\|Marine\|Landesschützen\|Sicherungs\|Stoottroepen\|Bewakingstroepen\|Binnenlandse Strijdkrachten\|Feld-Division\|Field Division\|Jäger` | `100S1000181211000000` | 172 |
| GI02 | default-infantry | any | `Division\|Regiment\|Brigade\|Battalion\|Bataillon` | `100S1000211211000000` | 14 |
| GH01 | no-exact | any | `Army Group\|Heeresgruppe\|Army\|Armee\|Corps\|Korps\|Group\|Détachement d.Armée\|Forces of the` | `100S1000231210000000` | 81 |
| GZ99 | default | any | (any) |  | 0 |
| ADD-ABN | addon | any | `Airborne\|Parachute\|Fallschirm\|Luftlande\|Glider\|Air Landing` |  | 3 |
| ADD-TF | addon | any | `Kampfgruppe\|Combat Command\|Task Force` |  | 31 |

## Units that fall to a default

- **GZ99 unspecified land unit:** 0 units.
- **AF99 fixed-wing default:** 1007 flying units and air commands whose names give no reconnaissance, naval or ground-service role (bombardment, fighter, troop carrier, liaison squadrons and groups, RAF numbered squadrons, Geschwader, Gruppen, Staffeln, commands). This is the intended symbol for them, not a gap; the proposal asks whether bomber, fighter and transport units should get modifiers (question 9).
- **NF99 naval-formation default:** 321 flotillas, squadrons, divisions and forces whose names give no mine-warfare, torpedo, escort or anti-submarine role (assault, LCT, LCI, LST, build-up, motor launch, landing barge, destroyer and support flotillas, assault groups, bombarding forces). This is the surface-group symbol Scott approved.
- **GI02 land unit with no arm in its name, drawn as infantry:** 14 units:

  - `FR-INF-GIRONDE` French Gironde Marching Division (Division de marche Gironde) (division)
  - `GER-DIV-136ZBV` Division z.b.V. 136 (division)
  - `GER-DIV-172` Division Nr. 172 (division)
  - `GER-DIV-405` Division Nr. 405 (division)
  - `GER-DIV-526` Division Nr. 526 (division)
  - `GER-DIV-905` Division Nr. 905 (division)
  - `GER-INF-HUTTN` Division Ulrich von Hutten (division)
  - `GER-INF-SCHRN` Division Scharnhorst (division)
  - `GER-RES-148D` 148th Reserve Division (division)
  - `GER-RES-157D` 157th Reserve Division (division)
  - `GER-RES-158D` 158th Reserve Division (division)
  - `GER-RES-165D` 165th Reserve Division (division)
  - `GER-RES-182D` 182nd Reserve Division (division)
  - `NL-INF-IRNEB` Royal Netherlands Brigade (Prinses Irene) (brigade)

## Ambiguous units

Each of these units matches a different entity when the part of its name in parentheses is ignored. Most are not real ambiguities (the parenthesis carries the role, as in "No. 35 (Reconnaissance) Wing RAF" or "(Task Group 124.3)"); the ones that need a decision are marked **decide**.

- `GER-ARMY-LUETT` Armeegruppe Lüttwitz (XXXIX and XLVII Panzer Corps, 30-31 December 1944): rule GR02 (`120500`); without the parenthesis GH01 (`121000`). decided (question 12, accepted 23 November 2026): an army-level group of two panzer corps for two days; armour from the parenthesis, combined arms from "Armeegruppe".
- `GER-FLAKA-155-1` I./Flak-Regiment 155 (W) (V-1 battalion): rule AD01 (`130700`); without the parenthesis AD02 (`130100`). decided (question 5, accepted 23 November 2026): as Flak-Regiment 155 (W).
- `GER-FLAKA-155-2` II./Flak-Regiment 155 (W) (V-1 battalion): rule AD01 (`130700`); without the parenthesis AD02 (`130100`). decided (question 5, accepted 23 November 2026): as Flak-Regiment 155 (W).
- `GER-FLAKA-155-3` III./Flak-Regiment 155 (W) (V-1 battalion): rule AD01 (`130700`); without the parenthesis AD02 (`130100`). decided (question 5, accepted 23 November 2026): as Flak-Regiment 155 (W).
- `GER-FLAKA-155-4` IV./Flak-Regiment 155 (W) (V-1 battalion): rule AD01 (`130700`); without the parenthesis AD02 (`130100`). decided (question 5, accepted 23 November 2026): as Flak-Regiment 155 (W).
- `GER-FLAKR-155` Flak-Regiment 155 (W) (V-1 regiment): rule AD01 (`130700`); without the parenthesis AD02 (`130100`). decided (question 5, accepted 23 November 2026): V-1 regiment drawn as Fires/Missile rather than air defense.
- `GER-WK-XI` Stellvertretendes Generalkommando XI (Wehrkreis XI): rule HQ03 (`110000`); without the parenthesis GZ99 (`000000`). no decision needed: the parenthesis carries the role.
- `UK-WG-034` No. 34 (Photographic Reconnaissance) Wing RAF: rule AR01 (`120801`); without the parenthesis AF99 (`120800`). no decision needed: the parenthesis carries the role.
- `UK-WG-035` No. 35 (Reconnaissance) Wing RAF: rule AR01 (`120801`); without the parenthesis AF99 (`120800`). no decision needed: the parenthesis carries the role.
- `UK-WG-039` No. 39 (Reconnaissance) Wing RAF: rule AR01 (`120801`); without the parenthesis AF99 (`120800`). no decision needed: the parenthesis carries the role.
- `UK-WG-152` No. 152 (General Reconnaissance) Wing RAF: rule AR01 (`120801`); without the parenthesis AF99 (`120800`). no decision needed: the parenthesis carries the role.
- `UK-WG-153` No. 153 (General Reconnaissance) Wing RAF: rule AR01 (`120801`); without the parenthesis AF99 (`120800`). no decision needed: the parenthesis carries the role.
- `UK-WG-154` No. 154 (General Reconnaissance) Wing RAF: rule AR01 (`120801`); without the parenthesis AF99 (`120800`). no decision needed: the parenthesis carries the role.
- `UK-WG-155` No. 155 (General Reconnaissance) Wing RAF: rule AR01 (`120801`); without the parenthesis AF99 (`120800`). no decision needed: the parenthesis carries the role.
- `UK-WG-156` No. 156 (General Reconnaissance) Wing RAF: rule AR01 (`120801`); without the parenthesis AF99 (`120800`). no decision needed: the parenthesis carries the role.
- `UK-WG-157` No. 157 (General Reconnaissance) Wing RAF: rule AR01 (`120801`); without the parenthesis AF99 (`120800`). no decision needed: the parenthesis carries the role.
- `US-BG-025` 25th Bombardment Group (Reconnaissance): rule AR01 (`120801`); without the parenthesis AF99 (`120800`). no decision needed: the parenthesis carries the role.
- `US-FG-363` 363rd Fighter Group (363rd Tactical Reconnaissance Group from September 1944): rule AR01 (`120801`); without the parenthesis AF99 (`120800`). decided (question 11, accepted 23 November 2026): fighter group until September 1944, tactical reconnaissance group after; one function for all dates.
- `US-FS-380` 380th Fighter Squadron (160th Tactical Reconnaissance Squadron from 25 August 1944): rule AR01 (`120801`); without the parenthesis AF99 (`120800`). decided (question 11, accepted 23 November 2026): fighter squadron until 25 August 1944, reconnaissance after.
- `US-FS-381` 381st Fighter Squadron (161st Tactical Reconnaissance Squadron from 25 August 1944): rule AR01 (`120801`); without the parenthesis AF99 (`120800`). decided (question 11, accepted 23 November 2026): as 380.
- `US-FS-382` 382nd Fighter Squadron (162nd Tactical Reconnaissance Squadron from 25 August 1944): rule AR01 (`120801`); without the parenthesis AF99 (`120800`). decided (question 11, accepted 23 November 2026): as 380.
- `US-TDB-001B` Task Force A (1st Tank Destroyer Brigade): rule GT01 (`120400`); without the parenthesis GK01 (`121000`). decided (question 12, accepted 23 November 2026): "Task Force A" is the 1st Tank Destroyer Brigade; drawn as antitank with the Task Force digit.
- `US-TG-122` Western Naval Task Force (Task Force 122): rule NF01 (`121002`); without the parenthesis NF99 (`121000`). no decision needed: the parenthesis carries the role.
- `US-TG-124` Assault Force O, Omaha Beach (Task Force 124): rule NF01 (`121002`); without the parenthesis NF99 (`121000`). no decision needed: the parenthesis carries the role.
- `US-TG-124-10` Minesweeper Group, Assault Force O (Task Group 124.10): rule NF02 (`121003`); without the parenthesis NF06 (`121000`). no decision needed: the parenthesis carries the role.
- `US-TG-124-3` Assault Group O-1, Assault Force O (Task Group 124.3): rule NF02 (`121003`); without the parenthesis NF99 (`121000`). no decision needed: the parenthesis carries the role.
- `US-TG-124-4` Assault Group O-2, Assault Force O (Task Group 124.4): rule NF02 (`121003`); without the parenthesis NF99 (`121000`). no decision needed: the parenthesis carries the role.
- `US-TG-124-5` Assault Group O-3, Assault Force O (Task Group 124.5): rule NF02 (`121003`); without the parenthesis NF99 (`121000`). no decision needed: the parenthesis carries the role.
- `US-TG-124-6` Escort Group, Assault Force O (Task Group 124.6): rule NF02 (`121003`); without the parenthesis NF08 (`121000`). no decision needed: the parenthesis carries the role.
- `US-TG-124-8` Gunfire Support Craft, Assault Force O (Task Group 124.8): rule NF02 (`121003`); without the parenthesis NF99 (`121000`). no decision needed: the parenthesis carries the role.
- `US-TG-124-9` Bombardment Group, Assault Force O (Task Group 124.9): rule NF02 (`121003`); without the parenthesis NF99 (`121000`). no decision needed: the parenthesis carries the role.
- `US-TG-125` Assault Force U, Utah Beach (Task Force 125): rule NF01 (`121002`); without the parenthesis NF99 (`121000`). no decision needed: the parenthesis carries the role.
- `US-TG-125-10` Far Shore Service Group, Assault Force U (Task Group 125.10): rule NF02 (`121003`); without the parenthesis NF99 (`121000`). no decision needed: the parenthesis carries the role.
- `US-TG-125-12` Follow-up Convoy Group, Assault Force U (Task Group 125.12): rule NF02 (`121003`); without the parenthesis NF99 (`121000`). no decision needed: the parenthesis carries the role.
- `US-TG-125-13` PT Boats, Assault Force U (Task Group 125.13): rule NF02 (`121003`); without the parenthesis NF07 (`121000`). no decision needed: the parenthesis carries the role.
- `US-TG-125-14` Special Task Groups, Assault Force U (Task Group 125.14): rule NF02 (`121003`); without the parenthesis NF99 (`121000`). no decision needed: the parenthesis carries the role.
- `US-TG-125-3` Force Flagship Group, Assault Force U (Task Group 125.3): rule NF02 (`121003`); without the parenthesis NF99 (`121000`). no decision needed: the parenthesis carries the role.
- `US-TG-125-4` Green Assault Group, Assault Force U (Task Group 125.4): rule NF02 (`121003`); without the parenthesis NF99 (`121000`). no decision needed: the parenthesis carries the role.
- `US-TG-125-5` Red Assault Group, Assault Force U (Task Group 125.5): rule NF02 (`121003`); without the parenthesis NF99 (`121000`). no decision needed: the parenthesis carries the role.
- `US-TG-125-6` Escort Group, Assault Force U (Task Group 125.6): rule NF02 (`121003`); without the parenthesis NF08 (`121000`). no decision needed: the parenthesis carries the role.
- `US-TG-125-7` Support Craft Group, Assault Force U (Task Group 125.7): rule NF02 (`121003`); without the parenthesis NF99 (`121000`). no decision needed: the parenthesis carries the role.
- `US-TG-125-8` Bombardment Group, Assault Force U (Task Group 125.8): rule NF02 (`121003`); without the parenthesis NF99 (`121000`). no decision needed: the parenthesis carries the role.
- `US-TG-125-9` Minesweeper Group, Assault Force U (Task Group 125.9): rule NF02 (`121003`); without the parenthesis NF06 (`121000`). no decision needed: the parenthesis carries the role.
- `US-TG-126` Follow-up Force B (Task Force 126): rule NF01 (`121002`); without the parenthesis NF99 (`121000`). no decision needed: the parenthesis carries the role.
- `US-TG-129` Cherbourg Bombardment Force (Task Force 129), 25 June 1944: rule NF01 (`121002`); without the parenthesis NF99 (`121000`). no decision needed: the parenthesis carries the role.
- `US-TG-129-1` Cherbourg Bombardment Group 1 (Task Group 129.1): rule NF02 (`121003`); without the parenthesis NF99 (`121000`). no decision needed: the parenthesis carries the role.
- `US-TG-129-2` Cherbourg Bombardment Group 2 (Task Group 129.2): rule NF02 (`121003`); without the parenthesis NF99 (`121000`). no decision needed: the parenthesis carries the role.
- `US-PRS-155` 155th Photographic Squadron (423rd Night Fighter Squadron until 22 June 1944): rule AR01 (reconnaissance) for all dates. decided (question 11, accepted 23 November 2026).
- `GER-PG-FUEBE` Führer-Begleit-Brigade (Führer-Begleit-Division from 26 January 1945): rule GM01 (mechanized infantry) since question 12 was accepted (23 November 2026; old: GI02 infantry default).

## Codes used and their verification

Every entity and modifier code the rules use, checked on 23 November 2026 against the JMSML instance files (Esri joint-military-symbology-xml, branch `dev`, commit `094e7647f0bd`, 19 September 2024; Base.xml says "No changes to APP-6(C)/2525D") and against the number-SIDC icon tables of milsymbol (spatialillusions/milsymbol, `master`, latest release v3.0.6 of 18 November 2026). "MISSING" means the code has no entry in that source.

| symbol set | kind | code | JMSML label | milsymbol icon key |
|---|---|---|---|---|
| 10 | entity | 000000 | Unspecified | MISSING |
| 10 | entity | 110000 | Command and Control | GR.IC.COMMAND AND CONTROL |
| 10 | entity | 111000 | Command and Control / Signal | GR.IC.FF.SIGNAL |
| 10 | entity | 120200 | Movement and Maneuver / Air Traffic Services/Airfield Operations | GR.IC.AIR TRAFFIC SERVICES |
| 10 | entity | 120400 | Movement and Maneuver / Antitank/Antiarmor | GR.IC.FF.ANTITANK/ANTIARMOUR |
| 10 | entity | 120401 | Movement and Maneuver / Antitank/Antiarmor / Armored | GR.IC.ARMOUR |
| 10 | entity | 120500 | Movement and Maneuver / Armor/Armored/Mechanized/Self-Propelled/Tracked | GR.IC.ARMOUR |
| 10 | entity | 120800 | Movement and Maneuver / Aviation Fixed Wing | GR.IC.AVIATION FIXED WING |
| 10 | entity | 120801 | Movement and Maneuver / Aviation Fixed Wing / Reconnaissance | GR.IC.AVIATION FIXED WING |
| 10 | entity | 121000 | Movement and Maneuver / Combined Arms | GR.IC.COMBINED ARMS |
| 10 | entity | 121100 | Movement and Maneuver / Infantry | GR.IC.FF.INFANTRY |
| 10 | entity | 121102 | Movement and Maneuver / Infantry / Armored/Mechanized/Tracked | GR.IC.ARMOUR |
| 10 | entity | 121300 | Movement and Maneuver / Reconnaissance/Cavalry/Scout | GR.IC.FF.RECONNAISSANCE |
| 10 | entity | 130100 | Fires / Air Defense | GR.IC.FF.AIR DEFENCE |
| 10 | entity | 130300 | Fires / Field Artillery | GR.IC.FIELD ARTILLERY |
| 10 | entity | 130700 | Fires / Missile | GR.IC.MISSILE |
| 10 | entity | 140700 | Protection / Engineer | GR.IC.ENGINEER |
| 10 | entity | 141700 | Protection / Security | GR.IC.SECURITY |
| 10 | entity | 141800 | Protection / Search and Rescue | GR.IC.SEARCH AND RESCUE |
| 10 | entity | 160000 | Sustainment | GR.IC.SUSTAINMENT |
| 10 | entity | 161100 | Sustainment / Maintenance | GR.IC.MAINTENANCE |
| 10 | modifier1 | 46 | Naval | GR.M1.NAVAL |
| 10 | modifier1 | 76 | Ranger | GR.M1.RANGER |
| 10 | modifier1 | 78 | Aviation | GR.M1.AVIATION |
| 10 | modifier2 | 01 | Airborne | GR.M2.AIRBORNE |
| 10 | modifier2 | 15 | Heavy | GR.M2.HEAVY |
| 10 | modifier2 | 27 | Mountain | GR.M2.MOUNTAIN |
| 30 | entity | 120100 | Military Combatant / Carrier | SE.IC.CARRIER |
| 30 | entity | 120200 | Military Combatant / Surface Combatant, Line | SE.IC.SURFACE COMBATANT, LINE |
| 30 | entity | 120201 | Military Combatant / Surface Combatant, Line / Battleship | SE.IC.BATTLESHIP |
| 30 | entity | 120202 | Military Combatant / Surface Combatant, Line / Cruiser | SE.IC.CRUISER, GUIDED MISSILE |
| 30 | entity | 120203 | Military Combatant / Surface Combatant, Line / Destroyer | SE.IC.DESTROYER |
| 30 | entity | 120204 | Military Combatant / Surface Combatant, Line / Frigate | SE.IC.FRIGATE |
| 30 | entity | 120205 | Military Combatant / Surface Combatant, Line / Corvette | SE.IC.CORVETTE |
| 30 | entity | 120300 | Military Combatant / Amphibious Warfare Ship | SE.IC.AMPHIBIOUS WARFARE SHIP |
| 30 | entity | 120301 | Military Combatant / Amphibious Warfare Ship / Amphibious Command Ship | SE.IC.AMPHIBIOUS FORCE FLAGSHIP |
| 30 | entity | 120401 | Military Combatant / Mine Warfare Ship / Mine Layer | SE.IC.MINELAYER |
| 30 | entity | 120402 | Military Combatant / Mine Warfare Ship / Mine Sweeper | SE.IC.MINESWEEPER |
| 30 | entity | 120502 | Military Combatant / Patrol Boat / Patrol Ship, General | SE.IC.PATROL GUN |
| 30 | entity | 121000 | Military Combatant / Navy Task Organization | SE.IC.NAVY TASK ORGANIZATION UNIT |
| 30 | entity | 121002 | Military Combatant / Navy Task Organization / Navy Task Force | SE.IC.NAVY TASK FORCE |
| 30 | entity | 121003 | Military Combatant / Navy Task Organization / Navy Task Group | SE.IC.NAVY TASK GROUP |
| 30 | entity | 121004 | Military Combatant / Navy Task Organization / Navy Task Unit | SE.IC.NAVY TASK UNIT |
| 30 | entity | 130100 | Military Noncombatant / Auxiliary Ship | SE.IC.AUXILIARY SHIP |
| 30 | modifier1 | 03 | Antisubmarine Warfare | SE.M1.ANTISUBMARINE WARFARE |
| 30 | modifier1 | 04 | Escort | SE.M1.ESCORT |
| 30 | modifier1 | 07 | Mine Countermeasures | SE.M1.MINE COUNTER MEASURES |
| 30 | modifier1 | 17 | Torpedo | SE.M1.TORPEDO |
| 30 | modifier2 | 02 | Heavy | SE.M2.HEAVY |
| 30 | modifier2 | 03 | Light | SE.M2.LIGHT |
| 35 | entity | 110000 | Military | SU.IC.MILITARY |
| 35 | entity | 110100 | Military / Submarine | SU.IC.SUBMARINE |
| 35 | modifier2 | 02 | Diesel Electric General | SU.M2.DIESEL PROPULSION |

Notes: `10` entity `000000` (Unspecified) has no milsymbol icon entry because milsymbol draws the frame with no icon for it, which is what "unspecified" means; it is used only by the fall-through rule GZ99, which maps no unit today. milsymbol keys the 2525D cruiser `120202` to an icon part named "CRUISER, GUIDED MISSILE"; the drawing has to be checked when the code step renders symbols (question 15).
