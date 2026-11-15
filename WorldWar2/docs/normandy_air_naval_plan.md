# Normandy air and naval pass: preparation and plan (branch `normandy-air-naval-prep`, 15 November 2026)

Scott asked on 15 November 2026 (t410u) for preparation before the larger Normandy ship and aircraft pass. This file is **prep, not data entry**: no unit, claim, place or relation is added by this branch. Section 1 is the source inventory (commit 1 of the branch), section 2 the table gaps (commit 2), sections 3-7 the plan (commit 3); Scott's answers of 15 November 2026 (t411u, t412u) are recorded in section 7 and where the plan said *new* or proposal (commit 4).

**Scope decisions (Scott, 15 November 2026, t410u).**

- **Ships:** every combatant of destroyer-escort size or larger is its own unit (the rule of `docs/air_naval_pilot.md` 6.1); landing craft and other small craft are entered at flotilla level.
- **Aircraft:** down to **squadron** level where the sources allow, with the groups and wings above them.
- **Window (default stated by the executor; confirmed by Scott 15 November 2026, t412u):** **1 June to 31 August 1944**, which covers the build-up to D-Day (the pre-invasion stations are dated 1 June), the landings, the Cherbourg and Brittany operations and the breakout to the Seine; Operation DRAGOON (15 August) is a separate theatre and stays out of this pass. Scott accepted it without change.

## 1. Source inventory (15 November 2026)

Method: each source below was opened or fetched on 15 November 2026 from the box (or with WebFetch where the box was blocked) and checked for the one thing the pass needs from it. "Held" means the repo already cites it in `data/references_meta.csv`. "Reachable" means it was opened this session, but no reference row exists yet: a row is added only when a claim cites it. The full-text copies used for the check were kept in scratch space outside the repo and are not committed (rule 24; Drive holds the private notes folder only).

**Rights shorthand.** *PD* = public domain (US government work, or marked public domain by the host); *copyright* = only facts, short quotations and the URL are used, as for the other copyrighted sources (`docs/reuse_and_attribution.md`).

### 1.1 Held (already cited in the repo)

| Source | Reference | What it gives this pass | Rights |
|---|---|---|---|
| Ellis, *Victory in the West* vol. I (archive.org full text) | `R670` (vol. II `R671`) | British naval and air narrative of Normandy (ships named in the bombardment, minesweeping and Mulberry chapters); Appendix II landing craft | Crown copyright (facts only) |
| NHHC, *Operation NEPTUNE* ch. 9 (US Naval Administrative History) | `R902` | Western Task Force forces U and O, Bombarding Forces A and C, ship tables | PD |
| USAF Historical Research Center, Continental Airfields (ETO) | `R898` | Allied airfield list with dates | PD |
| Nafziger Collection 944BGAA, 944GIAB (CARL) | `R594`, `R633` | German ground order of battle only (no air or naval part used) | facts only |
| Wikipedia pages of 366th Fighter Group, II. Jagdkorps, JG 26, Warspite, Texas, Ślązak and others | `R896`-`R911` | Pilot rows (air-naval pilot, `docs/air_naval_pilot.md` section 1) | CC BY-SA 4.0 |
| Wikipedia class and type pages | `R912`-`R1158` | 200 ship classes and 134 aircraft types already seeded (`data/ship_classes.csv`, `data/aircraft_types.csv`) | CC BY-SA 4.0 |

No naval or air **order of battle** is held as such: the repo has the pilot's 34 claims and the class and type tables, nothing at squadron, flotilla or ship-by-ship level.

### 1.2 Reachable (opened this session, not yet in the reference table)

**Allied naval**

| Source | URL | Checked | Rights |
|---|---|---|---|
| Morison, *History of United States Naval Operations in WWII*, vol. XI, *The Invasion of France and Germany*, **Appendix I, "The Western Naval Task Force in the Invasion of Normandy"** (pp. 333-338, page numbers from the running heads; 333 inferred) | https://archive.org/details/husno-volume-xi-the-invasion-of-france-and-germany-1944-1945 (full text) | Read: TF 122 down to ship names, Task Forces 125 (Utah), 124 (Omaha), 126 (follow-up), 129 (Cherbourg, 25 June 1944), with every cruiser, battleship, destroyer and destroyer escort named and the landing craft by type and number | copyright (facts only) |
| NHB (Naval Historical Branch), *Operation NEPTUNE* booklet, "Allied Naval Forces allocated to Operation NEPTUNE" and "Sword / Juno / Gold Force" pages, plus a dated Normandy naval chronology (6 June to 24 August, including German ships sunk) | https://britishfriendsofnormandy.org.uk/wp-content/uploads/2019/11/NHB-Neptune-D-Day-bklt-O.pdf | Read: Bombarding Forces D, E, K (every ship with its class), minesweeping flotillas (for example 40th, 14th), assault forces and their landing-craft counts | MOD booklet hosted by a third party; facts only |
| **Admiralty Battle Summary No. 39, *Operation NEPTUNE: Landings in Normandy, June 1944* (BR 1736 (43)), vol. I narrative and vol. II appendices** (the Naval Staff History) | https://www.forposterityssake.ca/RCN-DOCS/RCND0532.pdf (vol. I) and https://www.forposterityssake.ca/RCN-DOCS/RCND0533.pdf (vol. II) | Both PDFs downloaded and text-extracted. Vol. II **Appendix A(1)-A(4)** is a "classified list of H.M. ships of war with commanding officers and allocations to Operation NEPTUNE", in classes, squadrons and flotillas (battleships, monitors, cruisers, fleet destroyers by flotilla, escort destroyers, sloops, frigates, corvettes, minesweeper, MMS and BYMS flotillas, and so on) with the assault and post-assault allocation of each ship; **Appendix B(1)** the US ships; **Appendix C** the other Allied warships (French, and so on); Appendix D the Home Fleet distant cover; Appendix E the German disposition by area. This is the authoritative naval order of battle and settles the one gap of the earlier plan | Crown copyright, 1947 (facts only); a scan with OCR errors, so a name or date is read from the page image where the text is unclear |
| Roskill, *The War at Sea* vol. III part 2 (Royal Navy official history) | https://archive.org/details/war-at-sea-1939-1945-vol-3-part-2 (full text) | Text downloaded and searched, not read in full: it confirms the bombarding ships and the German naval reaction; it holds no organisation table, so it is a narrative cross-check only | Crown copyright (facts only) |
| `dday-overlord.com` Allied armada battle order | https://www.dday-overlord.com/en/d-day/armada/battle-order | Lists Task Forces and bombarding forces; a cross-check only | copyrighted web page; facts only |

**Allied air**

| Source | URL | Checked | Rights |
|---|---|---|---|
| Maurer, *Air Force Combat Units of World War II* (1961, reprint 1983) | https://archive.org/details/AirForceCombatUnitsOfWorldWarIi (full text) | Read the 366th Fighter Group entry: constitution, assignment to Ninth AF, combat start, D-Day sweep, move to the Continent | PD (US Air Force publication, marked public domain by the host) |
| Maurer, *Combat Squadrons of the Air Force, World War II* (1969) | https://archive.org/details/CombatSquadronsOfTheAirForceWWII-nsia (full text) | Read the 390th Fighter Squadron entry: lineage, group assignment, **dated stations** (for example Thruxton 1 March 1944, St Pierre du Mont 20 June 1944, Dreux 25 August 1944) and aircraft. The OCR has errors (Membury "10 Jan 1945" for 1944), so every date is checked against a second source | PD |
| Craven and Cate, *The Army Air Forces in WWII* vol. III, *Argument to V-E Day* | https://www.ibiblio.org/hyperwar/AAF/III/index.html (HyperWar, chapter by chapter) and https://archive.org/details/Vol3EuropeArgumentToVEDay | Index and full text opened; Normandy air operations in the NEPTUNE chapters (narrative; unit lists are in Maurer) | PD (US government history) |
| *Army Air Forces in World War II: Combat Chronology 1941-1945* (AFHRA) | https://archive.org/details/AFD-100525-035 | Full text opened; daily mission summary by air force and command | PD |
| No. 2 Group, 83 Group and 84 Group: 2nd TAC order of battle, 6 June 1944 (wings, squadrons, aircraft types, commanders) | https://wartimes.ca/wp-content/uploads/2018/04/2nd-TAC-Order-of-Battle-6th-Jun-1944.pdf | Read: wings and squadrons of 83 and 84 Groups with the types flown (Spitfire IX, Typhoon IB, Mustang III, Mosquito, Mitchell II, Boston IIIA) | third-party chart; facts only |
| RAF Web (Air of Authority), group pages | https://www.rafweb.org/Members%20Pages/Unit%20Details/Groups/No%2084%20Group.htm | Opened: 84 Group squadron list for June 1944; the other group pages follow the same pattern | copyrighted web page; facts only |
| Project Overlord, 2nd TAF order of battle | https://www.projectoverlord.co.uk/history/second-tactical-air-force-order-of-battle/ | Opened: squadron-by-squadron airfields and dates; a cross-check for Craven and Cate and the rafweb pages | copyrighted web page; facts only |
| Wikipedia unit pages (Ninth Air Force, IX Fighter Command, IX Troop Carrier Command, Eighth Air Force, VIII Fighter Command, 19th Air Division, No. 2, 11, 38, 46, 85 Group, 83 and 84 Groups, RAF Coastal Command) | https://en.wikipedia.org/wiki/Ninth_Air_Force and the others | Existence and size checked through the MediaWiki API (all present); content read only for the 366th Group in the pilot | CC BY-SA 4.0 |

**German air and naval**

| Source | URL | Checked | Rights |
|---|---|---|---|
| "Schematische Kriegsgliederung der Wehrmacht für die Operation Overlord" (German Wikipedia) | https://de.wikipedia.org/wiki/Schematische_Kriegsgliederung_der_Wehrmacht_f%C3%BCr_die_Operation_Overlord | Read: Luftflotte 3 down to Gruppe, aircraft on hand by type for 6 June 1944; Marinegruppenkommando West (5. Torpedobootflottille: T 28, Möwe, Jaguar, Kondor, Falke; S-boat flotillas 2, 4, 5, 8, 9; the Sicherungs-Divisionen and their minesweeper, Räumboot, Vorpostenboot and Sperrbrecher flotillas) | CC BY-SA 4.0 |
| HyperWar, *The G.A.F. and the Invasion of Normandy, 1944* | https://ibiblio.org/hyperwar/Germany/LW/GAF-Normandy/index.html | Read the opening chapters: Luftflotte 3 composition and strength on 5 and 6 June, the transfers of Jagdgruppen after D-Day | PD (translated German Air Ministry study, hosted on HyperWar) |
| "Luftflotte 3 Orders of Battle, 41-44" | https://www.oocities.org/sturmvogel_66/LF3.html | Opened: tables by Gruppe with aircraft, strength and airfield for dates through 1944 | copyrighted web page; facts only |
| Wikipedia, Luftflotte 3 | https://en.wikipedia.org/wiki/Luftflotte_3 | Opened (156 KB) | CC BY-SA 4.0 |
| uboat.net (Allied warships, boats listing) | https://uboat.net/allies/warships/ and https://uboat.net/boats/listing.html | Both open; boat lists and Allied warship histories | copyrighted web page; facts only |
| NHB booklet naval chronology (above) | as above | German ships sunk or damaged 6 June to 24 August (torpedo boats Möwe, Falke, Jaguar, Kondor; destroyers ZH 1, Z 24, Z 32, Z 23; minesweepers M 83, M 343 and others) | facts only |

### 1.3 Not reached

| Source | Why it matters | State |
|---|---|---|
| RAF Operations Record Books (AIR 27) | Station and date of every RAF squadron | The National Archives only; not online in a usable form |
| Luftwaffe Quartermaster-General returns (*Iststärke* returns) | Strength by Gruppe and type | not found online; the German Wikipedia page gives the 6 June totals without the source |
| AFHRA directly (`afhra.af.mil`, `media.defense.gov` PDFs) | Maurer and USAAF reference PDFs | the box gets HTTP 403 from `media.defense.gov`; the archive.org copies of the same books are used instead; `afhra.af.mil/Information/Studies-and-Publications/` returned 404 through WebFetch |
| niehorster.org Luftwaffe order of battle 6 June 1944 | Gruppe and Staffel tree with aircraft | the box gets HTTP 500; WebFetch returns only the page title and a one-line caption, so the unit tree is not extractable; not usable until a second route is found |
| Rohwer, *Chronology of the War at Sea*; Whitley, *German Destroyers of WWII* | German ships by day | not online; not held |

### 1.4 Summary

- **Held:** 4 usable sources (Ellis, NHHC ch. 9, USAF airfields, Wikipedia pages), none of them an order of battle.
- **Reachable (opened for the facts above):** 16 sources: the Admiralty Battle Summary 39 (both volumes), Morison XI, NHB booklet, Roskill III/2, Maurer units, Maurer squadrons, Craven and Cate III, the Combat Chronology, wartimes.ca 2nd TAC, rafweb, Project Overlord, German Wikipedia Kriegsgliederung, HyperWar GAF, oocities LF3, Wikipedia pages, uboat.net.
- **Missing:** the ANCXF Report itself (the Battle Summary is its published digest), the AIR 27 ORBs, the Luftwaffe returns, the niehorster tree and the Kriegsmarine daily chronologies.
- Everything reachable is either public domain or facts-only. The single point of weakness is the **RAF below wing level**: squadron stations rest on the wartimes.ca chart and rafweb, with Wikipedia as a second family.

## 2. Table gaps (seeded 15 November 2026)

Method: the ships and aircraft types named in the orders of battle read in section 1 (Admiralty Battle Summary 39 Appendices A-C, Morison XI Appendix I, the NHB booklet, the German Wikipedia Kriegsgliederung and the wartimes.ca 2nd TAC chart) were compared with `data/ship_classes.csv` (SC001-SC200) and `data/aircraft_types.csv` (AT001-AT134). Class and type pages were fetched again on 15 November 2026 (`accessed_date` 2026-11-15; the class notes say "15 November 2026"). Same conventions as the earlier seeding (`docs/air_naval_pilot.md` 8.2 and 9.2): infobox or Specifications text as written, each figure with its own `reference_id`, a key absent when the page gives nothing, no estimated figure, a family row with figures only on the sub-type or variant row.

**Added (commit 2): 11 ship classes `SC201`-`SC211`, 8 aircraft types `AT135`-`AT142`, 10 references `R1169`-`R1178`** (Wikipedia, family `wikipedia`). The Allied destroyer classes below were **not** attached to `SC102` (V and W class) or `SC103` (S class (1917)): both are First World War classes, and the Neptune destroyers of the same letters are the War Emergency Programme classes of 1942-1944.

| Row | Why it is needed (ships named in the sources) |
|---|---|
| `SC201` Wyoming class (US BB) | USS Arkansas, TF 124 bombardment group (Morison XI Appendix I; Admiralty Battle Summary 39 App. B(1)) |
| `SC202` Emerald class (UK CL) | HMS Emerald (Bombarding Force K) and HMS Enterprise (Force A) |
| `SC203` O and P class with `SC204` O class (4 inch), `SC205` O class (4.7 inch), `SC206` P class (UK DD) | HMS Onslow, Onslaught, Offa, Opportune, Orwell (Battle Summary 39 App. A(1), fleet destroyers); the page gives three infoboxes, so the family row has none and the three sub-type rows carry theirs; the sources do not say which O-class ships carried 4 inch guns, so no ship is tied to a sub-type yet |
| `SC207` S and T class (UK DD) | HMS Saumarez, Scorpion, Scourge, Serapis, Swift and the Norwegian Stord and Svenner (Force D, NHB booklet) |
| `SC208` U and V class (UK DD) | HMS Grenville, Ulster, Ulysses, Undaunted, Undine, Urania, Urchin, Ursa (Force K), Venus, Vigilant, Verulam, Virago; the page lists HMCS Algonquin (ex-Valentine) and Sioux (ex-Vixen) as the Canadian V class |
| `SC209` W and Z class with `SC210` W class, `SC211` Z class (UK DD) | HMS Kempenfelt (W class) and the other Emergency flotilla ships |
| `AT135` Fw 200 Condor with `AT136` Fw 200 C-3/U4 (Germany) | KG 40 (X. Fliegerkorps), German Wikipedia Kriegsgliederung: 45 Fw 200C on 6 June 1944 |
| `AT137` Ju 290 with `AT138` Ju 290 A-5 (Germany) | Fernaufklärungsgruppe 5 (6 Ju 290A-5 and 4 Ju 290A-7) |
| `AT139` LeO 45 with `AT140` LeO 451 (France, built; flown by the Luftwaffe transport units) | III./TG 1 and IV./TG 4 (the German page says "LeO 45") |
| `AT141` Seafire with `AT142` Seafire F Mk III (UK) | "Seafire LIII" appears three times on the 2nd TAC chart of 6 June 1944 (the squadrons are not yet identified; the page's Specifications section is headed F Mk III) |

**Seen but not seeded (each needs a decision or a different source), carried into the open questions in section 7:**

- **Ship type codes:** no `ship_type` for **monitors** (HMS Roberts, Erebus), **S-boats and R-boats**, and **landing ships and craft**; the pilot's section 6 chose the US hull codes. Monitors are single ships above the DE threshold, so they need a code: **`BM` approved by Scott (15 November 2026) and added to the `ship_type` vocabulary in the commit that records his answers**; S-boats, R-boats and landing ships stay at flotilla level with no code of their own.
- **Nationality codes** (Scott approved all five on 15 November 2026; **Norway `NOR`, Australia `AUS`, New Zealand `NZ` and South Africa `SAF` were added to `data/nationalities.csv` in that commit; Italy was not**, see open question 9) that were missing from `data/nationalities.csv`: Norway (Stord, Svenner, Glaisdale; 331 and 332 Squadrons), Australia (453 Squadron), New Zealand (485 Squadron), Italy (the SM.82 Marsupiale of TG 1; the German Wikipedia page counts 16), South Africa (SANF minesweepers Recruit, Rifleman), 164 Squadron, with its Argentine-British volunteers, is an RAF squadron and needs no code.
- **Aircraft types not yet read in any source of section 1:** the Lockheed Hudson, Fairey Swordfish, Grumman Avenger and Avro Anson (RAF and Fleet Air Arm types; the Wikipedia Specifications section of the Hudson is the Mk I, not a 1944 mark). The Coastal, Transport and Fleet Air Arm squadron lists of chunks 6 and 8 decide which are needed.
- **Variants** named in the sources and left as leftovers: Spitfire Mk IX (row `AT103` is the LF Mk IXe), Mk XI and Mk VII, Mosquito NF Mk XIII/XVII and Mk IX, Mustang I/IA/II (Allison), Auster Mk IV, Fw 190G-3 and G-8, Do 24, Bv 138, Ju 88R/C sub-variants, Lancaster/Halifax marks in the Bomber Command squadrons, Dakota and Stirling marks of 38 and 46 Group. A variant row is added when a claim needs its type link and the page names a specification.
- **Class gaps likely to appear** (not yet read at class level): the Canadian ex-Royal Navy destroyers (HMCS Ottawa, Kootenay, Chaudière, Gatineau, Skeena, St. Laurent), the Free French and Norwegian Hunt variants beyond `Hunt class` Type I-IV, `Adventure` and `Albatross` (single-ship classes), the Isles-class trawlers and the Fairmile boats (below the DE threshold, flotilla level), and the German `Sperrbrecher`, `Vorpostenboot` and `Artillerieträger` types (auxiliaries, flotilla level). Chunk 1 reads the exact class of each ship as it enters the pass.
- **Source quality:** all 19 new rows rest on English Wikipedia only (second source family missing for the figures); stronger sources (Jane's, navypedia, NHHC DANFS, Air Ministry pilot's notes) stay open as in roadmap 375 (l).

## 3. Scope

- **Window (default): 1 June to 31 August 1944** for all forces. Claims before 1 June are entered only where a unit's state on 1 June needs them (a unit's formation, an assignment still in force). DRAGOON (15 August) and the Mediterranean forces are out of this pass; a Normandy unit that ends or leaves the window is not followed beyond it (leftover list).
- **Ships:** every commissioned combatant of destroyer-escort size or larger is its own unit (`docs/air_naval_pilot.md` 6.1): battleships, monitors, cruisers, destroyers, escort destroyers, sloops, frigates, corvettes, fleet minesweepers, gunboats, submarines. Landing ships and craft, motor torpedo boats and gunboats (MTB, MGB, ML), S-boats, R-boats, trawlers, auxiliaries and the small minesweepers (MMS, BYMS) are **flotilla level** (`naval_division`), with a single craft only when a source singles it out and it traces to a parent.
- **Aircraft:** down to **squadron** level (USAAF and RAF squadron, Luftwaffe Staffel where a source lists it), with groups and wings above them. A Luftwaffe Staffel is listed in the source of 6 June 1944 only at Gruppe level; Staffel rows follow only where a second source gives them (decision of Scott, 15 November 2026: otherwise the unit stops at Gruppe).
- **Domain:** air and naval units go to `build/other_domains/` (rule 22 and the air-naval pilot section 8); the grid and the main outputs do not move, so each chunk's grid compare is expected to show **0 changes**. Coastal artillery and flak stay ground (rule 22).
- **Claims first, strength later:** a unit needs a dated location claim before it can carry a relation (the evidence rule, pilot 2.9). Aircraft counts (`strength_json.aircraft`) and refits come last (chunk 9) and only from a source that gives them.

## 4. Unit list by force

Counts are **estimates read from the sources of section 1** (OCR for the Battle Summary, so ±10%); chunk 1 of each force makes the exact count before entering anything. "Id pattern" follows `docs/air_naval_pilot.md` 8.1; patterns marked *new* extend it; **Scott approved every pattern of this section on 15 November 2026 and they are written into `schema/README.md` (unit_id pattern, "Naval and air id patterns")**.

### 4.1 Allied naval

| Force | Units | Principal source(s) | Id pattern | Estimate |
|---|---|---|---|---|
| Eastern Task Force (RN): Force S, J, G (assault forces, `task_group`); Bombarding Forces D, E, K; Force L and the follow-up forces | task groups; 4 battleships and 2 monitors (some in Western reserve); about 20 cruisers; destroyer flotillas as `naval_division`; every fleet destroyer and Hunt escort destroyer as a ship; sloops, frigates, corvettes (including the RCN, RAN, SANF, French and Norwegian crews); fleet minesweepers; submarines; X-craft | Admiralty Battle Summary 39 App. A(1)-A(4) (class lists and allocations); NHB booklet; Morison App. I for the US-flag ships | ship `UK-<type>-<NAME>` (`UK-CL-ARETHUSA`, as the pilot); flotilla `UK-DF-<nn>` (destroyer), `UK-MSF-<nn>` (minesweeping), `UK-MLF-<nn>` (landing-craft flotilla by number), `UK-CF-<nn>` (coastal forces: MTB, MGB, ML); task groups `UK-TF-<letter>`, `UK-BF-<letter>` (existing) | about 200 ship units plus about 60 flotillas |
| Western Task Force (US): TF 122, 125 (Utah), 124 (Omaha), 126, 129; bombardment, escort, minesweeper and support groups | task groups; Texas, Arkansas, Nevada, Augusta, Tuscaloosa, Quincy, the destroyers and destroyer escorts | Morison XI App. I; Battle Summary 39 App. B(1); NHHC *Operation NEPTUNE* ch. 9 (`R902`); NHHC DANFS | ship `US-<type>-<hull as 3 digits>` (pilot); task groups `US-TG-<group with dashes>` (pilot) | about 34 US ships listed in App. B(1) plus about 18 other Allied ships under US command; about 20 groups |
| Other Allied naval (French, Dutch, Polish, Norwegian, Canadian ships) | the ships under the RN forces above, listed under their own flag | Battle Summary 39 App. C | `FR-`, `NL-`, `POL-`, `CAN-` plus type and name; Norway has the code `NOR` | about 20 |
| Landing craft and ships (ETF and WTF) | assault groups and landing-craft flotillas | Battle Summary 39 App. A(3); Morison App. I; Ellis vol. I App. II | as the flotillas above | about 40 flotillas |

### 4.2 Allied air

| Force | Units | Principal source(s) | Id pattern | Estimate |
|---|---|---|---|---|
| USAAF Ninth Air Force (IX TAC, XIX TAC, IX Bomber Command (19th Air Division), IX Troop Carrier Command, 10th Photographic Group): groups, squadrons | fighter, medium and light bomber groups and squadrons; troop carrier groups and squadrons; reconnaissance | Maurer *Combat Units* (group) and *Combat Squadrons* (squadron: assignment, dated stations, aircraft); Craven and Cate III; the airfield list `R898`; Combat Chronology | group `US-FG-<nnn>` (existing for the 366th), bomb group `US-BG-<nnn>`, troop carrier `US-TCG-<nnn>`, squadron `US-FS-<nnn>`, `US-BS-<nnn>`, `US-TCS-<nnn>` (the squadron prefix follows the 390th, `US-FS-390`; the group and squadron patterns are approved); commands `US-TAC-<nnn>C` (existing) | to be counted from Maurer (a few dozen groups, about 3-4 squadrons each) |
| USAAF Eighth Air Force (VIII Bomber Command: three bomb divisions; VIII Fighter Command): groups, squadrons | heavy bomb groups and squadrons; fighter groups | Maurer; Craven and Cate III; Combat Chronology | as above | about 40 bomb groups and 15 fighter groups (to be counted); only the groups that flew against Normandy targets in the window |
| RAF 2nd Tactical Air Force (No. 2, 83, 84, 85 Group), ADGB (Fighter Command; the No. 11 Group page was checked), Bomber Command, Coastal Command, Transport (No. 38, 46 Group): groups (`air_wing`), wings (`air_group`), squadrons | 83 Group: 29 squadrons and 5 AOP squadrons on 6 June (counted from the wartimes.ca chart and the dday-overlord order of battle); 84 Group: 29 squadrons; 2 Group about 11; the others to be counted | wartimes.ca 2nd TAC chart; rafweb group pages; Project Overlord; Wikipedia group and station pages; Craven and Cate; the ORBs (AIR 27) are not reachable | squadron `UK-SQN-<nnn>` (RAF), `CAN-SQN-<nnn>`, `POL-SQN-<nnn>`, `CZ-SQN-<nnn>`, `FR-SQN-<nnn>`, `NL-SQN-<nnn>`, `BEL-SQN-<nnn>` (nationality prefix by squadron flag); wing `UK-WG-<nnn>`; group `UK-GRP-<nnn>` (approved 15 November 2026); Norwegian, Australian, New Zealand and South African squadrons use `NOR-SQN-<nnn>`, `AUS-SQN-<nnn>`, `NZ-SQN-<nnn>`, `SAF-SQN-<nnn>` | about 250 squadrons in the window; the 2nd TAF and ADGB first (about 120) |
| Fleet Air Arm squadrons (Seafire spotting squadrons on the 2nd TAC chart, Swordfish, escort carriers) | squadrons | the 2nd TAC chart; the NHB booklet "contribution of Naval Aviation"; Battle Summary 39 | `UK-FAA-<nnn>` (approved 15 November 2026; in scope, so the numbers cannot clash with RAF squadrons) | not yet counted |

### 4.3 German

| Force | Units | Principal source(s) | Id pattern | Estimate |
|---|---|---|---|---|
| Luftflotte 3 (existing unit): IX. and X. Fliegerkorps, II. Fliegerdivision, II. Jagdkorps, Fliegerführer and Jagdfliegerführer; Geschwader, Gruppen, Staffeln; the units that arrived from Germany under *Dr. Gustav West* | the units of the German Wikipedia Kriegsgliederung (about 35 Gruppen, with aircraft on hand by type); later arrivals from the HyperWar GAF text and the oocities LF3 tables | German Wikipedia (organisation 6 June 1944); HyperWar *G.A.F. and the Invasion of Normandy*; oocities LF3; Wikipedia unit pages; niehorster (once a route to its tree exists) | `GER-<type>-<nnn>` (pilot: `GER-JG-026`, `GER-JGGR-026-2`); Staffel `GER-JGST-026-4` pattern (approved 15 November 2026; only where a second source confirms the Staffel) | about 35 Gruppen, about 100 Staffeln (second source needed) |
| Kriegsmarine: Marinegruppenkommando West (existing `GER-MGW-000H`); 5. Torpedobootsflottille (T 28, Möwe, Jaguar, Kondor, Falke), 8. Zerstörerflottille (Z 23, Z 24, Z 32, ZH 1 and others of the Biscay group); S-boat flotillas 2, 4, 5, 8, 9; Sicherungs-Divisionen and their Minensuchflottillen, Räumbootsflottillen, Vorpostenflottillen; the U-boats of the Biscay and Channel groups | ships DE or larger as units (torpedo boats, destroyers, U-boats); the rest as flotillas | German Wikipedia Kriegsgliederung; NHB chronology (ships sunk and dates); uboat.net (boat lists and patrols); Battle Summary 39 App. E (German disposition) | `GER-DD-Z<nnn>` (Z 23), `GER-TB-T<nnn>` (T 28), `GER-TB-<NAME>` (Möwe), U-boat `GER-SS-U<nnn>` (pilot); flotillas `GER-TBF-<nnn>` (pilot), `GER-SBF-<nnn>`, `GER-MSF-<nnn>` (approved 15 November 2026) | about 40 ships, about 40 flotillas, plus the U-boats the patrol lists give |

### 4.4 Id ranges

Claim, place, relation, reference and group ids are allocated from the next free id of the repo at the time of each chunk (the repo convention; ranges cannot be reserved across branches). At the end of this branch the next free ids are **`C9459`, `PL4181`, `CR1317`, `R1179`, `G129`, `SC212`, `AT143`, `UL025`, scenario 273, roadmap 384**. Planning budget, to be re-estimated after chunk 1: one dated claim per unit as a minimum, two to five per ship or squadron in the window; the new units add rows to `data/units.csv` (domain `naval` or `air`), not to the main outputs.

## 5. Order of work (chunks)

One branch and one PR per chunk, separate commits per force within it, the full verification set at each (including a grid compare that must show 0 changes).

| Chunk | Content | Why in this order |
|---|---|---|
| 1 | **Western Task Force, US ships**: task forces and groups, the 34 US ships of App. B(1) and the Allied ships under US command; D-Day and the Cherbourg bombardment (25 June) as dated claims with `sea_position` places (cap 0.5) | the best-documented force (Morison, NHHC, DANFS, one appendix): proves the method for ships at scale |
| 2 | **Eastern Task Force, Royal Navy**: Bombarding Forces D, E, K, escort and screening destroyers, then sloops, frigates, corvettes and the fleet minesweepers; the Battle Summary 39 allocations as claims and relations | the largest ship list; needs the monitor code and the nationality codes |
| 3 | **Flotillas**: minesweeping, MMS and BYMS, coastal forces, landing-craft and LST groups, assault groups (ETF and WTF) | flotilla-level units under the task groups of chunks 1 and 2 |
| 4 | **Kriegsmarine West**: 5. Torpedobootsflottille, destroyers, S-boat and Sicherungs flotillas; German losses of the window (6 June to 24 August) from the NHB chronology | needs the S-boat and R-boat code decision |
| 5 | **USAAF Ninth Air Force**: groups and squadrons with their dated stations (Maurer) and aircraft types; IX TAC and XIX TAC chains | extends the 366th pilot; Maurer and Craven and Cate are public domain |
| 6 | **RAF 2nd TAF and ADGB**: groups, wings and squadrons of 6 June, then the station moves through the window | wartimes.ca and rafweb give the 6 June structure; the station dates need a second source |
| 7 | **Luftwaffe Luftflotte 3**: Fliegerkorps, Geschwader and Gruppen of 6 June, the arrivals of 7 June onward, strength by type where a source gives it | after the Allied air units, because their claims cross-reference |
| 8 | **USAAF Eighth Air Force, RAF Bomber, Coastal and Transport Commands**: groups and squadrons that flew against Normandy targets | large and lower priority for the ground-location question |
| 9 | **Strength and refits**: `strength_json.aircraft`, naval refits | only from sources that give figures; none yet |

## 6. Rules carried into the pass (from the pilot and the standing rules)

Never guess; every value has its source and a confidence by the rubric; sea positions are `sea_position` places, capped at 0.5 with a `coord_source_note`; the 1 June station of a flying unit uses `location_represents` `base`; a relation needs an evidence claim; a source conflict is kept as alternates in a conflict group; a unit below regiment needs a traceable parent; out-of-scope claims are recorded (rule 22); ids are never reused; private reading notes stay in the Drive folder, never committed (rule 24).

## 7. Open questions for Scott: all answered 15 November 2026

Scott answered on 15 November 2026 (t410u-t412u). The questions are kept with his decisions, so the pass does not reopen them.

1. **Window. Answered:** 1 June to 31 August 1944 confirmed (he accepted the default).
2. **Monitors and small craft codes. Answered:** `BM` approved for monitors (added to the `ship_type` vocabulary, `schema/README.md` and the vocabulary test); S-boats, R-boats and landing ships stay at flotilla level with no code.
3. **Air depth. Answered:** squadron level for the USAAF and RAF; the Luftwaffe goes down to Staffel only where a second source confirms it, otherwise to Gruppe; **Fleet Air Arm squadrons are in scope**, prefix `UK-FAA-<nnn>`.
4. **Nationality codes. Answered:** Norway, Australia, New Zealand, South Africa and Italy approved. Done in the commit: `NOR`, `AUS`, `NZ`, `SAF` (all Allied, kind nation, no unit yet). **Not done: Italy.** `data/nationalities.csv` allows one `alliance` value (`Allied` or `Axis`) per nation and Italy changed sides on 8 September 1943, so the value is a judgement that is open question 9; the code (proposal `IT`) is the **first step of chunk 2 or of the chunk that needs the SM.82**, whichever comes first.
5. **Id patterns. Answered:** approved as listed in section 4 and written into `schema/README.md`.
6. **Class conflicts. Answered:** the ship's own class page decides its class; other sources (the NHB booklet for Algonquin and Sioux) are recorded as a conflict in the unit note, since a ship's class has no alternates column.
7. **Stronger sources. Answered:** Wikipedia-only table rows (the 19 new rows) are accepted for now.
8. **Public-domain versus copyrighted sources. Answered:** Morison, Roskill, Ellis and the Battle Summary are used as primary sources for ships (facts only), and RAF squadron stations rest on the wartimes.ca chart plus Wikipedia for now.
9. **New, open: Italy's `alliance` value.** `Axis` (the Kingdom and the RSI as Axis powers until the armistice and for the RSI after it), `Allied` (the co-belligerent kingdom after 8 September 1943), or a third vocabulary value such as `co_belligerent`? Needed before the `IT` row is added; it affects only the SM.82 type row and any Italian unit. **Answered 15 November 2026 (t413u-t414u): the single column is not enough.** A dated table `data/nation_allegiance.csv` (roadmap 384, branch `nation-allegiance`) carries Italy as neutral to 9 June 1940, Axis 10 June 1940 to 8 September 1943 and co-belligerent from 13 October 1943, and the `IT` row was added to `data/nationalities.csv` there (its `alliance` value `Axis` is the provisional single label until that column is retired). The Italian Social Republic still has no code.

## 8. Not done in this branch

No unit, claim, place or relation is entered; no change to a script. The branch's schema changes are the `BM` vocabulary value and the id conventions in `schema/README.md`; the changes to a test are scenario 256 (aircraft nationalities gain France) and the `ship_type` vocabulary expectation (gains `BM`). The Battle Summary text, the Morison, Maurer, Craven and Cate and other downloads used for this inventory are kept in scratch space and are not committed.
