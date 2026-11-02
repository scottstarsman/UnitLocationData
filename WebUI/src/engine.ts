import type { Claim, Filters, Operation } from './types';
import type { Feature, Polygon } from 'geojson';

const DAY = 86_400_000;
export const dayNumber = (date: string) => Math.floor(Date.parse(`${date}T00:00:00Z`) / DAY);
export const isoDay = (day: number) => new Date(day * DAY).toISOString().slice(0, 10);
export const isCalendarDate = (date: string) => /^\d{4}-\d{2}-\d{2}$/.test(date) && Number.isFinite(dayNumber(date)) && isoDay(dayNumber(date)) === date;
export const daysBetween = (from: string, to: string) => dayNumber(to) - dayNumber(from);
export const formatDate = (date: string, short = false) => new Intl.DateTimeFormat('en-GB', {
  day: '2-digit', month: short ? 'short' : 'long', ...(short ? {} : { year: 'numeric' }), timeZone: 'UTC',
}).format(new Date(`${date}T00:00:00Z`));
export const humanize = (value: string) => value.replaceAll('_', ' ');
export const historyColors = ['#9c493b', '#32677a', '#8b6b24', '#655386', '#367361', '#925c77', '#4c5661', '#a76127'];
export const echelonMark = (echelon: string) => ({ army_group: 'XXXXX', army: 'XXXX', corps: 'XXX', division: 'XX', brigade: 'X', 'regiment/battle_group': 'III', battalion: 'II' }[echelon] ?? '•');
export function compactName(c: { unit_name: string; unit_id: string }) {
  const roman = c.unit_name.match(/^([IVXLCDM]+)\s/);
  if (roman) return roman[1];
  const group = c.unit_name.match(/(?:Army Group|Panzer Group)\s+(\w+)/i);
  if (group) return group[1];
  if (c.unit_name.includes('OB West')) return 'OB W';
  const n = c.unit_name.match(/\b\d+(?:st|nd|rd|th)?\b/i)?.[0];
  if (n) return `${/^US-CC[AR]-/.test(c.unit_id) ? c.unit_id.split('-')[1] + '/' : ''}${n.replace(/st|nd|rd|th/i, '')}`;
  const ordinal = ['First', 'Second', 'Third', 'Fourth', 'Fifth', 'Sixth', 'Seventh', 'Eighth', 'Ninth', 'Tenth', 'Eleventh', 'Twelfth', 'Thirteenth', 'Fourteenth', 'Fifteenth', 'Sixteenth', 'Seventeenth', 'Eighteenth', 'Nineteenth'];
  const word = c.unit_name.split(' ')[0];
  if (ordinal.includes(word)) return String(ordinal.indexOf(word) + 1);
  return c.unit_id.split('-').at(-1)?.replace(/^0+/, '').slice(0, 7) || c.unit_name.slice(0, 7);
}
export function operationSet(operations: Operation[], id: string): Set<string> | null {
  if (!id) return null;
  const result = new Set([id]);
  let changed = true;
  while (changed) {
    changed = false;
    for (const op of operations) if (result.has(op.parent_operation_id) && !result.has(op.operation_id)) {
      result.add(op.operation_id); changed = true;
    }
  }
  return result;
}
export function matches(c: Claim, filters: Filters, ops: Set<string> | null) {
  return (!filters.nationality || c.nationality === filters.nationality)
    && (!filters.echelon || c.echelon === filters.echelon)
    && (!ops || ops.has(c.operation_id));
}
export function buildIndex(claims: Claim[]) {
  const index = new Map<string, Claim[]>();
  for (const claim of claims) {
    const list = index.get(claim.unit_id) ?? [];
    list.push(claim); index.set(claim.unit_id, list);
  }
  for (const rows of index.values()) rows.sort((a, b) => a.date.localeCompare(b.date) || a.claim_id.localeCompare(b.claim_id));
  return index;
}
/** Retain every observation on the latest eligible day, including same-day ambiguity. Filter AFTER choosing the latest day. */
export function situation(index: Map<string, Claim[]>, date: string, filters: Filters, ops: Set<string> | null) {
  const result: Claim[] = [];
  for (const rows of index.values()) {
    const eligible = rows.filter(c => c.date <= date && (filters.includeAlternates || c.claim_status !== 'alternate'));
    const last = eligible.at(-1)?.date;
    if (!last || (filters.maxAge !== null && daysBetween(last, date) > filters.maxAge)) continue;
    result.push(...eligible.filter(c => c.date === last && matches(c, filters, ops)));
  }
  return result;
}
export interface Track { unitId: string; color: string; points: Claim[]; segments: [Claim, Claim][]; }
export function histories(index: Map<string, Claim[]>, selected: string[], start: string, end: string, date: string,
  wholeRange: boolean, filters: Filters, ops: Set<string> | null): Track[] {
  const cutoff = wholeRange ? end : (date < end ? date : end);
  return selected.map((unitId, i) => {
    const rows = (index.get(unitId) ?? []).filter(c => c.date >= start && c.date <= cutoff);
    const points = rows.filter(c => (filters.includeAlternates || c.claim_status !== 'alternate') && matches(c, filters, ops));
    const groups = new Map<string, Claim[]>();
    // All claims, including excluded alternatives, remain visible to the ambiguity check.
    for (const c of rows) { const group = groups.get(c.date) ?? []; group.push(c); groups.set(c.date, group); }
    const days = [...groups.values()];
    const segments: [Claim, Claim][] = [];
    for (let j = 1; j < days.length; j++) {
      const a = days[j - 1], b = days[j];
      if (a.length === 1 && b.length === 1 && [a[0], b[0]].every(c => c.claim_status === 'preferred'
        && !c.conflict_group_id && matches(c, filters, ops))) segments.push([a[0], b[0]]);
    }
    return { unitId, color: historyColors[i % historyColors.length], points, segments };
  });
}
export function adjacentEvent(dates: string[], date: string, direction: -1 | 1) {
  return direction === 1 ? dates.find(d => d > date) ?? date : dates.findLast(d => d < date) ?? date;
}

export function precisionRing(c: Claim): Feature<Polygon> {
  const coordinates = [];
  const radians = Math.PI / 180;
  const distance = c.precision_km / 6371;
  const lat = c.latitude * radians, lon = c.longitude * radians;
  for (let i = 0; i <= 64; i++) {
    const bearing = i / 64 * Math.PI * 2;
    const p = Math.asin(Math.sin(lat) * Math.cos(distance) + Math.cos(lat) * Math.sin(distance) * Math.cos(bearing));
    const q = lon + Math.atan2(Math.sin(bearing) * Math.sin(distance) * Math.cos(lat), Math.cos(distance) - Math.sin(lat) * Math.sin(p));
    coordinates.push([q / radians, p / radians]);
  }
  return { type: 'Feature', properties: {}, geometry: { type: 'Polygon', coordinates: [coordinates] } };
}
