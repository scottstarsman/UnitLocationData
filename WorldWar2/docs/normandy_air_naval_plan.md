# Normandy air and naval pass: preparation and plan (branch `normandy-air-naval-prep`, 15 November 2026)

Scott asked on 15 November 2026 (t410u) for preparation before the larger Normandy ship and aircraft pass. This file is **prep, not data entry**: no unit, claim, place or relation is added by this branch. Section 1 (source inventory) is written first; the table gaps and the plan follow in later commits of the same branch.

**Scope decisions (Scott, 15 November 2026, t410u).**

- **Ships:** every combatant of destroyer-escort size or larger is its own unit (the rule of `docs/air_naval_pilot.md` 6.1); landing craft and other small craft are entered at flotilla level.
- **Aircraft:** down to **squadron** level where the sources allow, with the groups and wings above them.
- **Window (default, stated by the executor, not yet confirmed by Scott):** **1 June to 31 August 1944**, which covers the build-up to D-Day (the pre-invasion stations are dated 1 June), the landings, the Cherbourg and Brittany operations and the breakout to the Seine; Operation DRAGOON (15 August) is a separate theatre and stays out of this pass. Scott can widen or narrow it.

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
