export interface Relation {
  unit_id: string | null;
  relationship: string;
  note?: string;
  effective_from?: string;
  effective_to?: string;
  date_basis?: string;
}
export interface Claim {
  claim_id: string; conflict_group_id: string; claim_status: 'preferred' | 'alternate' | 'disputed';
  unit_id: string; unit_name: string; date: string; nationality: string; echelon: string; branch: string;
  theater: string; sub_theater?: string; parent_unit_id: string; commander: string;
  latitude: number; longitude: number; precision_km: number; confidence: number;
  place_id: string; place_name: string; location_name: string; location_represents: string;
  location_qualifier: string; coord_override: string; coord_reference_id: string; coord_source_note: string;
  operation_id: string; operation: string; operation_path: string; campaign: string;
  event_type: string; current_activity: string; notes: string;
  reference_ids: string[]; source: string; source_locator: string;
  command_relationships: Relation[]; composing_units: string[]; composing_units_names: string; composing_text: string;
  engaged_with: string[]; engaged_with_names: string; engaged_note: string;
  strength_status: string; strength_json: Record<string, unknown> | null;
  location_date: string; location_basis: string; location_temporal_offset_days: number | null;
  activity_status: string; activity_basis: string; activity_span: string;
  established: boolean; destroyed: boolean; disestablished: boolean;
}
export interface Unit {
  unit_id: string; unit_name: string; nationality: string; echelon: string; branch: string;
  record_status: string; claim_rows: number; first_claim_date: string; last_claim_date: string;
  formed_date: string; unit_note: string;
}
export interface Operation { operation_id: string; name: string; parent_operation_id: string; depth: string; operation_path: string; }
export interface Reference {
  reference_id: string; short_title: string; full_citation: string; url: string; source_type: string;
  source_family: string; license_or_status: string; reliability_note: string;
}
export interface ReferenceLink { claim_id: string; reference_id: string; role: string; locator: string; }
export interface Atlas {
  manifest: { firstDate: string; lastDate: string; claimCount: number; unitCount: number; observedUnitCount: number; dataVersion: string; };
  claims: Claim[]; units: Unit[]; operations: Operation[]; references: Reference[]; referenceLinks: ReferenceLink[];
  nationalities: { name: string; adjective: string; alliance: string }[];
}
export type Mode = 'situation' | 'history';
export interface Filters { nationality: string; echelon: string; theater: string; operation: string; maxAge: number | null; includeAlternates: boolean; }
