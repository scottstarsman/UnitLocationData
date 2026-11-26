import { useEffect, useRef, useState } from 'react';
import * as maplibregl from 'maplibre-gl';
import type { GeoJSONSource, StyleSpecification } from 'maplibre-gl';
import type { FeatureCollection } from 'geojson';
import workerUrl from 'maplibre-gl/dist/maplibre-gl-worker.mjs?worker&url';
import type { Claim, Mode } from './types';
import type { Track } from './engine';
import { compactName, daysBetween, echelonMark, formatDate, precisionRing } from './engine';

maplibregl.setWorkerUrl(workerUrl);

const empty: FeatureCollection = { type: 'FeatureCollection', features: [] };
const fallbackStyle: StyleSpecification = {
  version: 8, sources: {
    land: { type: 'geojson', data: `${import.meta.env.BASE_URL}geography/europe.geojson`, attribution: 'Natural Earth · public domain' },
  }, layers: [
    { id: 'ocean', type: 'background', paint: { 'background-color': '#93adb1' } },
    { id: 'land', type: 'fill', source: 'land', paint: { 'fill-color': '#e9e1c6' } },
    { id: 'land-outline', type: 'line', source: 'land', paint: { 'line-color': '#8a9583', 'line-width': 0.8, 'line-opacity': 0.7 } },
  ],
};

interface Props {
  positions: Claim[]; tracks: Track[]; selected: string[]; focused: Claim | null;
  date: string; mode: Mode; showPrecision: boolean; showLabels: boolean; fitRequest: number;
  initialBounds?: [number, number, number, number] | null;
  headingTheater?: string;
  headingYears?: string;
  onClaim: (claim: Claim) => void;
}

function symbol(claim: Claim, color: string, old: boolean, selected: boolean, showLabel: boolean, date: string) {
  const el = document.createElement('button');
  el.type = 'button';
  el.className = `unit-marker ${old ? 'older' : ''} ${selected ? 'chosen' : ''} ${claim.claim_status !== 'preferred' ? 'contested' : ''}`;
  el.style.setProperty('--unit-color', color);
  const age = daysBetween(claim.date, date);
  el.title = `${claim.nationality} ${claim.unit_name} · ${formatDate(claim.date)} · ${age ? `last observed ${age} day${age === 1 ? '' : 's'} earlier` : 'observed on selected date'} · ${claim.claim_id}`;
  el.setAttribute('aria-label', el.title);
  const mark = document.createElement('span'); mark.className = 'echelon-mark'; mark.textContent = echelonMark(claim.echelon);
  const frame = document.createElement('span'); frame.className = `symbol-frame ${['army_group', 'army', 'corps', 'other'].includes(claim.echelon) ? 'headquarters' : /armou?red|panzer(?!grenadier)/i.test(claim.unit_name) ? 'armor' : 'infantry'}`;
  const label = document.createElement('span'); label.className = 'symbol-number'; label.textContent = compactName(claim);
  frame.append(label); el.append(mark, frame);
  if (showLabel || selected) {
    const name = document.createElement('span'); name.className = 'symbol-label';
    name.textContent = `${claim.nationality} ${compactName(claim)}${age ? ` · −${age}d` : ''}`;
    el.append(name);
  }
  if (claim.claim_status !== 'preferred') {
    const flag = document.createElement('span'); flag.className = 'symbol-question'; flag.textContent = '?'; el.append(flag);
  }
  return el;
}

export function MapView(props: Props) {
  const container = useRef<HTMLDivElement>(null);
  const mapRef = useRef<maplibregl.Map | null>(null);
  const markers = useRef<maplibregl.Marker[]>([]);
  const latest = useRef(props); latest.current = props;
  const [ready, setReady] = useState(false);
  const [styleVersion, setStyleVersion] = useState(0);
  const [base, setBase] = useState<'loading' | 'detail' | 'outline'>('loading');
  const [failure, setFailure] = useState('');
  const [mapError, setMapError] = useState(false);
  const arrangeLabels = () => {
    const map = mapRef.current;
    if (!map) return;
    const occupied: { x: number; y: number; w: number; h: number }[] = [];
    const sorted = [...markers.current].sort((a, b) => Number(b.getElement().classList.contains('chosen')) - Number(a.getElement().classList.contains('chosen')));
    for (const marker of sorted) {
      const element = marker.getElement();
      const label = element.querySelector<HTMLElement>('.symbol-label') ?? (element.classList.contains('history-date') ? element : null);
      if (!label) continue;
      const p = map.project(marker.getLngLat());
      const box = { x: p.x - 30, y: p.y + (element === label ? 0 : 19), w: Math.max(55, (label.textContent?.length ?? 0) * 5), h: 17 };
      const overlap = occupied.some(a => box.x < a.x + a.w && box.x + box.w > a.x && box.y < a.y + a.h && box.y + box.h > a.y);
      const show = element.classList.contains('chosen') || !overlap;
      label.style.visibility = show ? 'visible' : 'hidden';
      if (show) occupied.push(box);
    }
  };

  useEffect(() => {
    if (!container.current) return;
    let map: maplibregl.Map;
    try {
      const bounds = latest.current.initialBounds;
      const start = bounds
        ? { bounds: new maplibregl.LngLatBounds([bounds[0], bounds[1]], [bounds[2], bounds[3]]), fitBoundsOptions: { padding: 60, maxZoom: 6.6 } }
        : { center: [0.1, 49.05] as [number, number], zoom: 6.6 };
      map = new maplibregl.Map({ container: container.current, style: fallbackStyle,
        ...start, minZoom: 3, maxZoom: 13, maxPitch: 0,
        attributionControl: false, renderWorldCopies: false });
    } catch {
      setFailure('The map needs WebGL. Enable browser hardware acceleration or try another browser. The unit list and dated records remain available.');
      return;
    }
    mapRef.current = map;
    map.addControl(new maplibregl.NavigationControl({ showCompass: false }), 'top-right');
    map.addControl(new maplibregl.ScaleControl({ unit: 'metric', maxWidth: 130 }), 'bottom-left');
    map.addControl(new maplibregl.AttributionControl({ compact: true, customAttribution: 'WWII Unit Locations · CC BY-SA 4.0 · © OpenStreetMap contributors' }), 'bottom-right');
    const addOverlays = () => {
      if (map.getSource('history')) { setReady(true); setStyleVersion(v => v + 1); return; }
      if (!map.hasImage('route-direction')) {
        const canvas = document.createElement('canvas'); canvas.width = 20; canvas.height = 20;
        const ctx = canvas.getContext('2d')!;
        ctx.strokeStyle = '#f9f1d9'; ctx.lineWidth = 3; ctx.fillStyle = '#665b43';
        ctx.beginPath(); ctx.moveTo(4, 4); ctx.lineTo(15, 10); ctx.lineTo(4, 16); ctx.closePath(); ctx.stroke(); ctx.fill();
        map.addImage('route-direction', ctx.getImageData(0, 0, 20, 20));
      }
      map.addSource('history', { type: 'geojson', data: empty });
      map.addLayer({ id: 'history-casing', type: 'line', source: 'history', paint: { 'line-color': '#fbf6df', 'line-width': 5, 'line-opacity': 0.8 } });
      map.addLayer({ id: 'history-lines', type: 'line', source: 'history', paint: { 'line-color': ['get', 'color'], 'line-width': 2.2, 'line-dasharray': [3, 2] } });
      map.addLayer({ id: 'history-direction', type: 'symbol', source: 'history', layout: { 'symbol-placement': 'line', 'symbol-spacing': 100, 'icon-image': 'route-direction', 'icon-size': 0.6, 'icon-rotation-alignment': 'map', 'icon-allow-overlap': false, 'icon-keep-upright': false } });
      map.addSource('history-points', { type: 'geojson', data: empty });
      map.addLayer({ id: 'history-dots', type: 'circle', source: 'history-points', paint: { 'circle-radius': 4.5, 'circle-color': ['get', 'color'], 'circle-stroke-color': '#fff8e6', 'circle-stroke-width': 1.5 } });
      map.addSource('precision', { type: 'geojson', data: empty });
      map.addLayer({ id: 'precision-area', type: 'fill', source: 'precision', paint: { 'fill-color': '#927543', 'fill-opacity': 0.1 } });
      map.addLayer({ id: 'precision-edge', type: 'line', source: 'precision', paint: { 'line-color': '#927543', 'line-width': 1, 'line-dasharray': [3, 3] } });
      setReady(true);
      setStyleVersion(v => v + 1);
    };
    map.on('load', addOverlays);
    map.on('style.load', addOverlays);
    map.on('error', () => setMapError(true));
    map.on('move', arrangeLabels);
    map.on('click', 'history-dots', e => {
      const id = e.features?.[0]?.properties?.claim_id;
      const c = latest.current.tracks.flatMap(t => t.points).find(p => p.claim_id === id);
      if (c) latest.current.onClaim(c);
    });
    map.on('mouseenter', 'history-dots', () => { map.getCanvas().style.cursor = 'pointer'; });
    map.on('mouseleave', 'history-dots', () => { map.getCanvas().style.cursor = ''; });
    const resize = new ResizeObserver(() => map.resize()); resize.observe(container.current);
    return () => { resize.disconnect(); markers.current.forEach(m => m.remove()); map.remove(); mapRef.current = null; };
  }, []);

  // Detail is optional: the bundled outline remains usable without a tile service.
  useEffect(() => {
    if (!ready || base !== 'loading') return;
    const abort = new AbortController();
    const timer = window.setTimeout(() => abort.abort(), 9000);
    fetch('https://tiles.openfreemap.org/styles/positron', { signal: abort.signal })
      .then(r => { if (!r.ok) throw new Error('Basemap unavailable'); return r.json() as Promise<StyleSpecification>; })
      .then(style => {
        for (const layer of style.layers) {
          const paint = (layer.paint ??= {}) as Record<string, unknown>;
          const id = layer.id.toLowerCase();
          if (layer.type === 'background') paint['background-color'] = '#e9e1c6';
          if (layer.type === 'fill') {
            paint['fill-color'] = /water|ocean/.test(id) ? '#93adb1' : /park|wood|forest|grass/.test(id) ? '#d5d6b6' : '#e9e1c6';
            if (/building/.test(id)) paint['fill-color'] = '#c9c5ae';
          }
          if (layer.type === 'line') {
            paint['line-color'] = /water/.test(id) ? '#799ba6' : /boundary/.test(id) ? '#b0ab95' : '#a3a58c';
            paint['line-opacity'] = /boundary/.test(id) ? 0.35 : 0.55;
          }
          if (layer.type === 'symbol') {
            paint['text-color'] = /water/.test(id) ? '#517987' : '#79806d';
            paint['text-halo-color'] = '#e9e1c6'; paint['text-halo-width'] = 1;
            if (/poi|housenumber/.test(id)) (layer.layout ??= {}).visibility = 'none';
          }
        }
        setReady(false); mapRef.current?.setStyle(style); setBase('detail'); setMapError(false);
      }).catch(() => setBase('outline')).finally(() => clearTimeout(timer));
    return () => { clearTimeout(timer); abort.abort(); };
  }, [ready, base]);

  useEffect(() => {
    const map = mapRef.current;
    if (!ready || !map) return;
    const lines: FeatureCollection = { type: 'FeatureCollection', features: props.tracks.flatMap(t => t.segments.map(([a, b]) => ({
      type: 'Feature' as const, properties: { color: t.color }, geometry: { type: 'LineString' as const, coordinates: [[a.longitude, a.latitude], [b.longitude, b.latitude]] },
    }))) };
    const points: FeatureCollection = { type: 'FeatureCollection', features: props.tracks.flatMap(t => t.points.map(c => ({
      type: 'Feature' as const, properties: { color: t.color, claim_id: c.claim_id }, geometry: { type: 'Point' as const, coordinates: [c.longitude, c.latitude] },
    }))) };
    (map.getSource('history') as GeoJSONSource).setData(props.mode === 'history' ? lines : empty);
    (map.getSource('history-points') as GeoJSONSource).setData(props.mode === 'history' ? points : empty);
    (map.getSource('precision') as GeoJSONSource).setData(props.focused && props.showPrecision ? { type: 'FeatureCollection', features: [precisionRing(props.focused)] } : empty);
    markers.current.forEach(m => m.remove());
    markers.current = props.positions.map(c => {
      const track = props.tracks.find(t => t.unitId === c.unit_id);
      const color = props.mode === 'history' ? track?.color ?? '#3e4842' : c.nationality === 'Germany' ? '#716042' : '#354d54';
      const button = symbol(c, color, c.date !== props.date, props.selected.includes(c.unit_id), props.showLabels, props.date);
      button.addEventListener('click', () => latest.current.onClaim(c));
      return new maplibregl.Marker({ element: button, anchor: 'center' }).setLngLat([c.longitude, c.latitude]).addTo(map);
    });
    if (props.mode === 'history' && props.showLabels) {
      for (const track of props.tracks) for (const c of track.points) {
        const label = document.createElement('button'); label.className = 'history-date';
        label.textContent = formatDate(c.date, true); label.title = `${c.unit_name} · ${c.claim_id} · ${c.claim_status}`;
        label.setAttribute('aria-label', `Inspect ${c.unit_name} observation on ${formatDate(c.date)}, ${c.claim_id}`);
        label.addEventListener('click', () => latest.current.onClaim(c));
        markers.current.push(new maplibregl.Marker({ element: label, anchor: 'left', offset: [8, 0] }).setLngLat([c.longitude, c.latitude]).addTo(map));
      }
    }
    arrangeLabels();
    return () => { markers.current.forEach(m => m.remove()); markers.current = []; };
  }, [ready, styleVersion, props.positions, props.tracks, props.mode, props.date, props.focused, props.showPrecision, props.showLabels, props.selected]);

  useEffect(() => {
    const map = mapRef.current;
    if (!map || !ready || props.fitRequest === 0) return;
    const points = props.mode === 'history' ? props.tracks.flatMap(t => t.points) : props.positions;
    if (!points.length) return;
    const bounds = new maplibregl.LngLatBounds();
    points.forEach(c => bounds.extend([c.longitude, c.latitude]));
    map.fitBounds(bounds, { padding: 80, maxZoom: 9, duration: 700 });
    // Fit is a deliberate action; data updates should not move the user's viewport.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [props.fitRequest, ready]);

  return <div className="map-stage">
    <div ref={container} className="map-canvas" aria-label="Interactive situation map" />
    <div className="map-grain" />
    <div className="map-sheet-heading"><span>{props.headingTheater ?? 'WESTERN EUROPE'}</span><small>OBSERVATION ATLAS · {props.headingYears ?? '1944–45'}</small></div>
    <div className="compass" aria-hidden="true"><span>N</span><svg viewBox="0 0 30 44"><path d="M15 2 25 36 15 29 5 36Z" fill="none" stroke="currentColor"/><path d="m15 2 0 27-10 7Z" fill="currentColor"/></svg></div>
    <div className="map-legend"><strong>FIELD KEY</strong><span><i className="legend-box"/> Observed on selected date</span><span><i className="legend-box dashed"/> Earlier observation</span><span><i className="legend-route"/> Sequence, not verified route</span><span className="legend-muted">? Alternate or disputed claim</span></div>
    {base === 'outline' && <div className="basemap-note">Outline basemap · detailed tiles unavailable</div>}
    {base === 'detail' && <div className="basemap-note">Modern geography · historical unit observations{mapError ? ' · some map tiles unavailable' : ''}</div>}
    {failure && <div className="map-failure" role="alert">{failure}</div>}
  </div>;
}
