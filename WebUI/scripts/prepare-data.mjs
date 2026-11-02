import { readFile, writeFile, mkdir } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import { createHash } from 'node:crypto';
import { parse } from 'csv-parse/sync';

const root = new URL('../../WorldWar2/', import.meta.url);
const out = new URL('../public/data/', import.meta.url);
const inputs = new Map();
async function csv(path) {
  const bytes = await readFile(new URL(path, root));
  inputs.set(path, createHash('sha256').update(bytes).digest('hex'));
  return parse(bytes, { columns: true, bom: true, skip_empty_lines: true });
}
const [rawClaims, units, coverage, operations, references, referenceLinks, nationalities] = await Promise.all([
  csv('build/all_claims.csv'), csv('data/units.csv'), csv('build/coverage.csv'), csv('build/operations.csv'),
  csv('data/references.csv'), csv('build/claim_references.csv'), csv('data/nationalities.csv'),
]);
const numeric = ['latitude', 'longitude', 'precision_km', 'confidence', 'location_temporal_offset_days'];
const lists = ['reference_ids', 'engaged_with', 'composing_units'];
const claims = rawClaims.map(row => {
  const c = { ...row };
  for (const key of numeric) c[key] = row[key] === '' ? null : Number(row[key]);
  for (const key of ['established', 'disestablished', 'destroyed']) {
    if (!['true', 'false'].includes(row[key])) throw new Error(`${row.claim_id}: invalid ${key}`);
    c[key] = row[key] === 'true';
  }
  for (const key of lists) c[key] = row[key] ? row[key].split(';').map(x => x.trim()) : [];
  c.command_relationships = row.command_relationships ? JSON.parse(row.command_relationships) : [];
  c.strength_json = row.strength_json ? JSON.parse(row.strength_json) : null;
  if (!Number.isFinite(c.latitude) || !Number.isFinite(c.longitude)) throw new Error(`Bad coordinate: ${c.claim_id}`);
  return c;
}).sort((a, b) => a.date.localeCompare(b.date) || a.claim_id.localeCompare(b.claim_id));
const unique = (rows, key) => {
  const ids = new Set(rows.map(x => x[key]));
  if (ids.size !== rows.length) throw new Error(`Duplicate ${key}`);
  return ids;
};
const ids = unique(claims, 'claim_id');
const unitIds = unique(units, 'unit_id');
const refIds = unique(references, 'reference_id');
const opIds = unique(operations, 'operation_id');
for (const c of claims) {
  if (!unitIds.has(c.unit_id) || !opIds.has(c.operation_id)) throw new Error(`Unresolved claim join: ${c.claim_id}`);
  for (const id of c.reference_ids) if (!refIds.has(id)) throw new Error(`Missing reference ${id}`);
}
for (const link of referenceLinks) {
  if (!ids.has(link.claim_id) || !refIds.has(link.reference_id)) throw new Error('Unresolved reference link');
}
const summary = new Map(coverage.map(x => [x.unit_id, x]));
const unitExport = units.map(u => ({ ...u, claim_rows: Number(summary.get(u.unit_id)?.claim_rows ?? 0),
  first_claim_date: summary.get(u.unit_id)?.first_claim_date ?? '', last_claim_date: summary.get(u.unit_id)?.last_claim_date ?? '' }));
const hashes = Object.fromEntries([...inputs].sort(([a], [b]) => a.localeCompare(b)));
const manifest = {
  schemaVersion: 1,
  dataVersion: createHash('sha256').update(JSON.stringify(hashes)).digest('hex').slice(0, 12),
  firstDate: claims[0].date, lastDate: claims.at(-1).date,
  claimCount: claims.length, unitCount: units.length, observedUnitCount: new Set(claims.map(x => x.unit_id)).size,
  inputs: hashes,
  license: 'CC BY-SA 4.0',
  citation: 'WWII Unit Locations dataset',
  interpretation: 'Event-based observations; gaps do not establish location or inactivity. Connectors are not verified travel routes.',
};
await mkdir(out, { recursive: true });
await writeFile(new URL('atlas.json', out), JSON.stringify({ manifest, claims, units: unitExport, operations, references, referenceLinks, nationalities }));
await writeFile(new URL('manifest.json', out), JSON.stringify(manifest, null, 2) + '\n');
console.log(`Prepared ${claims.length} claims, ${units.length} units → ${fileURLToPath(out)} (${manifest.dataVersion})`);
