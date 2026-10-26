# parent_formation split: before and after examples

Eleven examples from this repository showing the old free-text `parent_formation` (v5 / previous commit) and the new `parent_unit_id` and `command_relationships` columns. Claim ids, row order and all other columns are unchanged.

Conversion rules: `scripts/migrate_parent_formation.py` and `docs/methodology.md` (Parents and command relationships).

## C0172: Battle group attached to another division (Weidinger under Panzer Lehr)

- Unit: `GER-KG-WEIDINGER` on 1944-06-27
- **Before** `parent_formation`: `German 2nd SS Panzer Division Das Reich (GER-SSPZ-002D); attached to German Panzer Lehr Division (GER-PZ-LEHRD)`
- **After** `parent_unit_id`: `GER-PZ-LEHRD`
- **After** `command_relationships`: `[{"unit_id":"GER-SSPZ-002D","name":"German 2nd SS Panzer Division Das Reich","relationship":"organic"},{"unit_id":"GER-PZ-LEHRD","name":"German Panzer Lehr Division","relationship":"attached","note":"Placed under Panzer Lehr on arrival"}]`

## C0198: Battle group attached to a corps (Weidinger, 29 June)

- Unit: `GER-KG-WEIDINGER` on 1944-06-29
- **Before** `parent_formation`: `German 2nd SS Panzer Division Das Reich (GER-SSPZ-002D); attached to German II SS Panzer Corps (GER-SSPZ-002C)`
- **After** `parent_unit_id`: `GER-SSPZ-002C`
- **After** `command_relationships`: `[{"unit_id":"GER-SSPZ-002D","name":"German 2nd SS Panzer Division Das Reich","relationship":"organic"},{"unit_id":"GER-SSPZ-002C","name":"German II SS Panzer Corps","relationship":"attached","note":"Transferred to II SS Panzer Corps on 29 June"}]`

## C0183: Battle group attached to a sister division (Frey under 12th SS)

- Unit: `GER-KG-FREY` on 1944-06-28
- **Before** `parent_formation`: `German 1st SS Panzer Division Leibstandarte SS Adolf Hitler (GER-SSPZ-001D); attached to German 12th SS Panzer Division Hitlerjugend (GER-SSPZ-012D)`
- **After** `parent_unit_id`: `GER-SSPZ-012D`
- **After** `command_relationships`: `[{"unit_id":"GER-SSPZ-001D","name":"German 1st SS Panzer Division Leibstandarte SS Adolf Hitler","relationship":"organic"},{"unit_id":"GER-SSPZ-012D","name":"German 12th SS Panzer Division Hitlerjugend","relationship":"attached","note":"Vanguard attached to the 12th SS Panzer Division"}]`

## C0212: Combat command attached to another division

- Unit: `US-CCA-002D` on 1944-06-13
- **Before** `parent_formation`: `US 2nd Armored Division (US-ARM-002D); attached to US 101st Airborne Division (US-ABN-101D)`
- **After** `parent_unit_id`: `US-ABN-101D`
- **After** `command_relationships`: `[{"unit_id":"US-ARM-002D","name":"US 2nd Armored Division","relationship":"organic"},{"unit_id":"US-ABN-101D","name":"US 101st Airborne Division","relationship":"attached","note":"CMH ch. IX: Combat Command A was still attached to the 101st Airborne Division"}]`

## C0211: Corps reserve (Kampfgruppe Meyer)

- Unit: `GER-KG-MEYER` on 1944-06-06
- **Before** `parent_formation`: `German 352nd Infantry Division (GER-INF-352D); German LXXXIV Corps (GER-COR-084C) (corps reserve)`
- **After** `parent_unit_id`: `GER-COR-084C`
- **After** `command_relationships`: `[{"unit_id":"GER-INF-352D","name":"German 352nd Infantry Division","relationship":"organic"},{"unit_id":"GER-COR-084C","name":"German LXXXIV Corps","relationship":"reserve"}]`

## C0035: Two unqualified parents, notes show army control (265th Kampfgruppe)

- Unit: `GER-KG-265` on 1944-06-07
- **Before** `parent_formation`: `German 265th Infantry Division (GER-INF-265D); German Seventh Army (GER-ARMY-007A)`
- **After** `parent_unit_id`: `GER-ARMY-007A`
- **After** `command_relationships`: `[{"unit_id":"GER-INF-265D","name":"German 265th Infantry Division","relationship":"organic"},{"unit_id":"GER-ARMY-007A","name":"German Seventh Army","relationship":"operational_control","note":"Seventh Army (Dollmann) ordered the 265th Kampfgruppe forward, per the claim notes"}]`

## C0171: Two unqualified parents, no evidence of control (2nd Panzer battle group)

- Unit: `GER-KG-002PZ` on 1944-06-27
- **Before** `parent_formation`: `German 2nd Panzer Division (GER-PZ-002D); German XLVII Panzer Corps (GER-PZ-047C)`
- **After** `parent_unit_id`: `GER-PZ-002D`
- **After** `command_relationships`: `[{"unit_id":"GER-PZ-002D","name":"German 2nd Panzer Division","relationship":"organic"},{"unit_id":"GER-PZ-047C","name":"German XLVII Panzer Corps","relationship":"unknown","note":"Higher formation listed with the parent in the original text; its relationship to the unit is not stated"}]`

## C0030: Army under an army group (US First Army, operational control)

- Unit: `US-ARMY-001A` on 1944-06-06
- **Before** `parent_formation`: `British 21st Army Group (UK-AG-021G)`
- **After** `parent_unit_id`: `UK-AG-021G`
- **After** `command_relationships`: `[{"unit_id":"UK-AG-021G","name":"British 21st Army Group","relationship":"operational_control","note":"US First Army served under 21st Army Group until 12th Army Group became operational (1 August 1944)"}]`

## C0003: High-command reserve; parent added as a parent_only unit (OKW)

- Unit: `GER-SSPZ-012D` on 1944-06-06
- **Before** `parent_formation`: `OKW (central mobile reserve)`
- **After** `parent_unit_id`: `GER-OKW-000H`
- **After** `command_relationships`: `[{"unit_id":"GER-OKW-000H","name":"Oberkommando der Wehrmacht (OKW)","relationship":"reserve"}]`

## C0074: Unverified parent

- Unit: `US-INF-030D` on 1944-06-10
- **Before** `parent_formation`: `unknown`
- **After** `parent_unit_id`: `unknown`
- **After** `command_relationships`: `unknown`

## C0014: Plain parent (Seventh Army under Army Group B)

- Unit: `GER-ARMY-007A` on 1944-06-06
- **Before** `parent_formation`: `German Army Group B (GER-AG-00BG)`
- **After** `parent_unit_id`: `GER-AG-00BG`
- **After** `command_relationships`: `[{"unit_id":"GER-AG-00BG","name":"German Army Group B","relationship":"organic"}]`
