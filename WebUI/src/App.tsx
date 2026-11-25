import { useEffect, useMemo, useState } from 'react';
import type { CSSProperties, KeyboardEvent as ReactKeyboardEvent } from 'react';
import type { Atlas, Claim, Filters, Mode } from './types';
import { adjacentEvent, buildIndex, dayNumber, daysBetween, echelonMark, formatDate, histories, historyColors, humanize, isCalendarDate, isoDay, matches, operationSet, situation } from './engine';
import { MapView } from './MapView';

function Icon({ name, size = 18 }: { name: string; size?: number }) {
  const paths: Record<string, string> = {
    search: 'm21 21-5-5M18 10a8 8 0 1 1-16 0 8 8 0 0 1 16 0',
    play: 'm8 4 12 8-12 8Z', pause: 'M8 4v16M16 4v16',
    next: 'm7 5 7 7-7 7M18 5v14', previous: 'm17 5-7 7 7 7M6 5v14',
    plus: 'M12 5v14M5 12h14', close: 'm6 6 12 12M6 18 18 6',
    locate: 'M3 9V3h6M15 3h6v6M21 15v6h-6M9 21H3v-6',
    arrow: 'M5 12h14m-6-6 6 6-6 6', info: 'M12 11v6M12 7h.01M22 12a10 10 0 1 1-20 0 10 10 0 0 1 20 0',
    route: 'M5 5h9a5 5 0 0 1 0 10H9a4 4 0 0 0-4 4M5 2v6M2 5h6M2 20h6',
  };
  return <svg width={size} height={size} viewBox="0 0 24 24" fill={name === 'play' ? 'currentColor' : 'none'} stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true"><path d={paths[name] ?? paths.info}/></svg>;
}

function safeLink(url: string) { try { const parsed = new URL(url); return ['http:', 'https:'].includes(parsed.protocol) ? parsed.href : undefined; } catch { return undefined; } }
const initialParams = new URLSearchParams(window.location.search);

function trapDialogFocus(event: ReactKeyboardEvent<HTMLElement>) {
  if (event.key !== 'Tab') return;
  const controls = [...event.currentTarget.querySelectorAll<HTMLElement>('button:not(:disabled), a[href], input, select, [tabindex="0"]')];
  const first = controls[0], last = controls.at(-1);
  if (event.shiftKey && document.activeElement === first) { event.preventDefault(); last?.focus(); }
  else if (!event.shiftKey && document.activeElement === last) { event.preventDefault(); first?.focus(); }
}

function DateField({ value, min, max, label, id, onCommit }: { value: string; min: string; max: string; label: string; id?: string; onCommit: (date: string) => void }) {
  const [draft, setDraft] = useState(value);
  useEffect(() => setDraft(value), [value]);
  const valid = (v: string) => isCalendarDate(v) && v >= min && v <= max;
  return (
    <input
      id={id}
      aria-label={label}
      type="date"
      value={draft}
      min={min}
      max={max}
      onChange={e => {
        const v = e.target.value;
        setDraft(v);
        if (valid(v)) onCommit(v);
      }}
      onInput={e => {
        const v = e.currentTarget.value;
        setDraft(v);
        if (valid(v)) onCommit(v);
      }}
      onBlur={e => {
        const v = e.currentTarget.value;
        if (valid(v)) onCommit(v);
        else setDraft(value);
      }}
      onKeyDown={e => {
        if (e.key === 'Enter') e.currentTarget.blur();
      }}
    />
  );
}

export default function App() {
  const [atlas, setAtlas] = useState<Atlas | null>(null);
  const [error, setError] = useState('');
  useEffect(() => {
    const abort = new AbortController();
    fetch(`${import.meta.env.BASE_URL}data/atlas.json`, { signal: abort.signal }).then(r => {
      if (!r.ok) throw new Error(`Dataset request failed (${r.status})`); return r.json();
    }).then(setAtlas).catch(e => { if (e.name !== 'AbortError') setError(e.message); });
    return () => abort.abort();
  }, []);
  if (error) return <main className="loading-screen"><span className="eyebrow">SITUATION ATLAS</span><h1>Unable to load the dataset</h1><p>{error}</p><p>Run <code>npm run data:prepare</code> in WebUI, then reload.</p><button onClick={() => location.reload()}>Try again</button></main>;
  if (!atlas) return <main className="loading-screen"><span className="eyebrow">WWII UNIT LOCATIONS</span><h1>Opening the field atlas<span className="loading-dot">…</span></h1><p>Loading sourced observations and formation records.</p></main>;
  return <AtlasApp atlas={atlas}/>;
}

function AtlasApp({ atlas }: { atlas: Atlas }) {
  const { firstDate, lastDate } = atlas.manifest;
  const index = useMemo(() => buildIndex(atlas.claims), [atlas]);
  const unitMap = useMemo(() => new Map(atlas.units.map(u => [u.unit_id, u])), [atlas]);
  const [date, setDate] = useState(() => {
    const p = initialParams.get('date') ?? '1944-06-23';
    return isCalendarDate(p) && p >= firstDate && p <= lastDate ? p : firstDate;
  });
  const [mode, setMode] = useState<Mode>(initialParams.get('mode') === 'history' ? 'history' : 'situation');
  const [selected, setSelected] = useState<string[]>(() => {
    const p = initialParams.get('units');
    return p !== null ? [...new Set(p.split(',').filter(id => unitMap.has(id)))] : ['US-INF-029D'];
  });
  const [focusedId, setFocusedId] = useState('');
  const [detailUnit, setDetailUnit] = useState(selected[0] ?? '');
  const [detailsOpen, setDetailsOpen] = useState(() => window.innerWidth > 1000);
  const [search, setSearch] = useState('');
  const [filters, setFilters] = useState<Filters>({ nationality: '', echelon: '', theater: '', operation: '', maxAge: 30, includeAlternates: false });
  const [rangeStart, setRangeStart] = useState(firstDate);
  const [rangeEnd, setRangeEnd] = useState(lastDate);
  const [wholeRange, setWholeRange] = useState(false);
  const [playing, setPlaying] = useState(false);
  const [speed, setSpeed] = useState(2);
  const [showPrecision, setShowPrecision] = useState(true);
  const [showLabels, setShowLabels] = useState(true);
  const [showHelp, setShowHelp] = useState(false);
  const [fitRequest, setFitRequest] = useState(0);
  const [includePlaceholders, setIncludePlaceholders] = useState(false);
  const [mobilePanel, setMobilePanel] = useState(false);
  const [timelineTab, setTimelineTab] = useState<'observation' | 'chronology'>('observation');
  const dataBounds = useMemo(() => {
    const pts = atlas.claims.filter(c => Number.isFinite(c.longitude) && Number.isFinite(c.latitude));
    if (!pts.length) return null;
    let west = pts[0].longitude, east = pts[0].longitude, south = pts[0].latitude, north = pts[0].latitude;
    for (const c of pts) {
      if (c.longitude < west) west = c.longitude;
      if (c.longitude > east) east = c.longitude;
      if (c.latitude < south) south = c.latitude;
      if (c.latitude > north) north = c.latitude;
    }
    return [west, south, east, north] as [number, number, number, number];
  }, [atlas]);
  const theaters = useMemo(() => [...new Set(atlas.claims.map(c => c.theater).filter(Boolean))].sort(), [atlas]);
  const dateCaption = useMemo(() => {
    const a = formatDate(firstDate).toUpperCase();
    const b = formatDate(lastDate).toUpperCase();
    return `${a} — ${b}`;
  }, [firstDate, lastDate]);
  const opSet = useMemo(() => operationSet(atlas.operations, filters.operation), [atlas, filters.operation]);
  const positions = useMemo(() => situation(index, date, filters, opSet), [index, date, filters, opSet]);
  const tracks = useMemo(() => histories(index, selected, rangeStart, rangeEnd, date, wholeRange, filters, opSet), [index, selected, rangeStart, rangeEnd, date, wholeRange, filters, opSet]);
  const mapPositions = useMemo(() => mode === 'history' ? positions.filter(c => selected.includes(c.unit_id) && c.date >= rangeStart && c.date <= rangeEnd) : positions, [mode, positions, selected, rangeStart, rangeEnd]);
  const visibleUnits = new Set(mapPositions.map(c => c.unit_id));
  const unitClaims = index.get(detailUnit) ?? [];
  const focused = atlas.claims.find(c => c.claim_id === focusedId) ?? [...unitClaims].reverse().find(c => c.date <= date && c.claim_status !== 'alternate') ?? null;
  const detail = focused ? unitMap.get(focused.unit_id) : unitMap.get(detailUnit);
  const chronology = index.get(detail?.unit_id ?? '') ?? [];
  const sliderStart = mode === 'history' ? rangeStart : firstDate;
  const sliderEnd = mode === 'history' ? rangeEnd : lastDate;
  const events = useMemo(() => [...new Set(atlas.claims.filter(c => matches(c, filters, opSet)
    && (filters.includeAlternates || c.claim_status !== 'alternate')
    && (mode !== 'history' || selected.includes(c.unit_id))
    && c.date >= sliderStart && c.date <= sliderEnd).map(c => c.date))].sort(), [atlas, filters, opSet, mode, selected, sliderStart, sliderEnd]);
  const filteredUnits = useMemo(() => atlas.units.filter(u => (includePlaceholders || u.claim_rows > 0)
    && (!filters.nationality || u.nationality === filters.nationality)
    && (!filters.echelon || u.echelon === filters.echelon)
    && (!filters.theater || (index.get(u.unit_id) ?? []).some(c => c.theater === filters.theater))
    && (!opSet || (index.get(u.unit_id) ?? []).some(c => opSet.has(c.operation_id)))
    && `${u.unit_name} ${u.unit_id} ${u.nationality}`.toLowerCase().includes(search.toLowerCase()))
    .sort((a, b) => a.nationality.localeCompare(b.nationality) || a.unit_name.localeCompare(b.unit_name, undefined, { numeric: true })), [atlas, filters, search, includePlaceholders, opSet, index]);

  useEffect(() => {
    const params = new URLSearchParams(); params.set('date', date); params.set('mode', mode);
    params.set('units', selected.join(','));
    window.history.replaceState(null, '', `${window.location.pathname}?${params}`);
  }, [date, mode, selected]);
  useEffect(() => {
    const keydown = (event: KeyboardEvent) => {
      if (event.key === 'Escape') { setShowHelp(false); setMobilePanel(false); }
      if (event.key === '/' && !(event.target instanceof HTMLInputElement) && !(event.target instanceof HTMLSelectElement) && !showHelp) {
        event.preventDefault(); setMobilePanel(true);
        requestAnimationFrame(() => document.querySelector<HTMLInputElement>('[aria-label="Search formations"]')?.focus());
      }
    };
    window.addEventListener('keydown', keydown);
    return () => window.removeEventListener('keydown', keydown);
  }, [showHelp]);
  useEffect(() => {
    if (!playing) return;
    const timer = window.setInterval(() => setDate(old => {
      if (old >= sliderEnd) { setPlaying(false); return old; }
      return isoDay(dayNumber(old) + 1);
    }), 1000 / speed);
    return () => clearInterval(timer);
  }, [playing, speed, sliderEnd]);
  useEffect(() => { setDate(d => d < sliderStart ? sliderStart : d > sliderEnd ? sliderEnd : d); }, [sliderStart, sliderEnd]);
  function changeDate(value: string) {
    if (!isCalendarDate(value)) return;
    setPlaying(false); setFocusedId('');
    setDate(value < sliderStart ? sliderStart : value > sliderEnd ? sliderEnd : value);
  }
  function focusClaim(c: Claim) {
    setPlaying(false); setFocusedId(c.claim_id); setDetailUnit(c.unit_id); setDetailsOpen(true);
  }
  function chooseUnit(id: string) { setDetailUnit(id); setFocusedId(''); setDetailsOpen(true); setMobilePanel(false); setTimelineTab('observation'); }
  function toggleUnit(id: string) { setSelected(old => old.includes(id) ? old.filter(u => u !== id) : [...old, id]); }
  function switchMode(value: Mode) { setMode(value); setPlaying(false); setFocusedId(''); }
  function stepEvent(direction: -1 | 1) { changeDate(adjacentEvent(events, date, direction)); }
  const sameDayCount = new Set(mapPositions.filter(c => c.date === date).map(c => c.unit_id)).size;
  const progress = (dayNumber(date) - dayNumber(sliderStart)) / Math.max(1, dayNumber(sliderEnd) - dayNumber(sliderStart)) * 100;

  return <div className="atlas-app">
    <header className="masthead">
      <div className="atlas-brand"><div className="brand-symbol" aria-hidden="true"><span>XX</span><svg viewBox="0 0 36 26" fill="none" stroke="currentColor" strokeWidth="1.5" preserveAspectRatio="none"><path d="M1 1H35V25H1ZM1 1 35 25M35 1 1 25" vectorEffect="non-scaling-stroke"/></svg></div><div><span className="eyebrow">THE OBSERVATION ATLAS</span><h1>WWII Unit Locations<span className="title-dot">.</span></h1></div></div>
      <div className="header-caption">A sourced record of formations<br/><strong>{dateCaption}</strong></div>
      <div className="header-actions"><span className="edition">FIELD EDITION <b>01</b></span><button className="icon-button help-button" title="About the atlas" aria-label="About the atlas" onClick={() => setShowHelp(true)}><Icon name="info"/></button></div>
    </header>

    <div className="workspace">
      <aside className={`formation-panel ${mobilePanel ? 'mobile-open' : ''}`}>
        <div className="panel-heading"><div><span className="eyebrow">ORDER OF BATTLE</span><h2>Formations <span>{atlas.manifest.observedUnitCount}</span></h2></div><button className="icon-button mobile-close" aria-label="Close formation list" onClick={() => setMobilePanel(false)}><Icon name="close"/></button></div>
        <label className="search-box"><Icon name="search" size={16}/><input aria-label="Search formations" placeholder="Find a formation…" value={search} onChange={e => setSearch(e.target.value)}/><kbd>/</kbd></label>
        <div className="filter-pair"><label>Nation<select aria-label="Filter nationality" value={filters.nationality} onChange={e => setFilters(f => ({ ...f, nationality: e.target.value }))}><option value="">All nations</option>{atlas.nationalities.map(n => <option key={n.name}>{n.name}</option>)}</select></label><label>Echelon<select aria-label="Filter echelon" value={filters.echelon} onChange={e => setFilters(f => ({ ...f, echelon: e.target.value }))}><option value="">All levels</option>{[...new Set(atlas.units.map(u => u.echelon))].sort().map(e => <option key={e} value={e}>{humanize(e)}</option>)}</select></label></div>
        <div className="filter-pair"><label>Theater<select aria-label="Filter theater" value={filters.theater} onChange={e => { const theater = e.target.value; setFilters(f => ({ ...f, theater })); setFitRequest(n => n + 1); }}><option value="">All theaters</option>{theaters.map(th => <option key={th} value={th}>{humanize(th)}</option>)}</select></label></div>
        <label className="operation-filter">Campaign / operation<select aria-label="Filter operation" value={filters.operation} onChange={e => setFilters(f => ({ ...f, operation: e.target.value }))}><option value="">All operations</option>{atlas.operations.map(o => <option key={o.operation_id} value={o.operation_id}>{'· '.repeat(Number(o.depth))}{o.name}</option>)}</select></label>
        <div className="formation-list-heading"><span>{filteredUnits.length} FORMATIONS</span><span title="Check formations to compare their movement histories">HISTORY</span></div>
        <div className="formation-list">
          {filteredUnits.map(u => {
            const chosen = selected.indexOf(u.unit_id);
            const last = (index.get(u.unit_id) ?? []).filter(c => c.date <= date && c.claim_status !== 'alternate').at(-1);
            return <div key={u.unit_id} className={`formation-row ${detail?.unit_id === u.unit_id ? 'active' : ''}`}>
              <button className="formation-name" onClick={() => chooseUnit(u.unit_id)}><span className="formation-echelon">{echelonMark(u.echelon)}</span><strong>{u.unit_name}</strong><span className="formation-meta"><i className={visibleUnits.has(u.unit_id) ? 'status-dot visible' : 'status-dot'}/>{u.nationality} · {last ? `last ${formatDate(last.date, true)}` : u.claim_rows ? 'not yet observed' : 'no claims'}</span></button>
              <label className="unit-check" style={{ '--track-color': chosen >= 0 ? historyColors[chosen % historyColors.length] : undefined } as CSSProperties}><input type="checkbox" aria-label={`Include ${u.nationality} ${u.unit_name} in movement history`} checked={chosen >= 0} onChange={() => toggleUnit(u.unit_id)}/><span>{chosen >= 0 ? '✓' : '+'}</span></label>
            </div>;
          })}
          {!filteredUnits.length && <div className="list-empty"><strong>No matching formations</strong><p>Try another name or clear the filters.</p><button className="text-button" onClick={() => { setSearch(''); setFilters(f => ({ ...f, nationality: '', echelon: '', theater: '', operation: '' })); }}>Clear search & filters</button></div>}
        </div>
        <div className="formation-footer"><label className="check-label"><input type="checkbox" checked={includePlaceholders} onChange={e => setIncludePlaceholders(e.target.checked)}/> Include units without claims</label><span>{atlas.manifest.claimCount.toLocaleString()} observations · {atlas.manifest.unitCount} catalogued units</span></div>
      </aside>

      <main className="map-workspace">
        <div className="map-toolbar"><div className="mode-switch" role="group" aria-label="Map mode"><button aria-pressed={mode === 'situation'} className={mode === 'situation' ? 'active' : ''} onClick={() => switchMode('situation')}><span className="tiny-cross">⊞</span> Situation</button><button aria-pressed={mode === 'history'} className={mode === 'history' ? 'active' : ''} onClick={() => switchMode('history')}><Icon name="route" size={16}/> Movement history</button></div><div className="toolbar-options"><button className="mobile-formations text-button" onClick={() => setMobilePanel(true)}>Formations</button><label className="check-label"><input type="checkbox" checked={showLabels} onChange={e => setShowLabels(e.target.checked)}/> Labels</label><button className="icon-button" title="Fit visible observations" aria-label="Fit visible observations" onClick={() => setFitRequest(n => n + 1)}><Icon name="locate"/></button></div></div>
        <div className="situation-strip"><div><span className="eyebrow">{mode === 'situation' ? 'SITUATION AS OF' : 'MOVEMENT RECORD'}</span><h2>{formatDate(date)}</h2></div><div className="situation-stats"><strong>{mode === 'situation' ? visibleUnits.size : tracks.reduce((n, t) => n + t.points.length, 0)}</strong><span>{mode === 'situation' ? 'formations shown' : 'observations in range'}</span><i/><strong>{mode === 'situation' ? sameDayCount : selected.length}</strong><span>{mode === 'situation' ? 'observed this day' : 'units selected'}</span></div></div>
        {mode === 'history' && <div className="history-controls"><label>From<DateField label="History start date" min={firstDate} max={rangeEnd} value={rangeStart} onCommit={v => { setRangeStart(v); setFocusedId(''); setPlaying(false); }}/></label><span>—</span><label>To<DateField label="History end date" min={rangeStart} max={lastDate} value={rangeEnd} onCommit={v => { setRangeEnd(v); setFocusedId(''); setPlaying(false); }}/></label><label className="check-label whole-range"><input type="checkbox" checked={wholeRange} onChange={e => setWholeRange(e.target.checked)}/> Show entire range</label></div>}
        <div className="map-area"><MapView initialBounds={dataBounds} positions={mapPositions} tracks={tracks} selected={selected} focused={focused} date={date} mode={mode} showPrecision={showPrecision} showLabels={showLabels} fitRequest={fitRequest} onClaim={focusClaim}/>
          {mode === 'history' && selected.length === 0 && <div className="map-empty"><Icon name="route" size={30}/><h3>Trace a formation’s history</h3><p>Check one or more formations in the list to compare their recorded locations.</p><button onClick={() => setMobilePanel(true)} className="mobile-formations">Choose formations</button></div>}
          {!(mode === 'history' && !selected.length) && mapPositions.length === 0 && (mode === 'situation' || !tracks.some(t => t.points.length)) && <div className="map-empty"><h3>No observations to show</h3><p>Try a later date, a wider history range, or a different filter.</p></div>}
        </div>
        <div className="observation-options"><label>Last observation within <select aria-label="Maximum observation age" value={filters.maxAge ?? 'all'} onChange={e => setFilters(f => ({ ...f, maxAge: e.target.value === 'all' ? null : Number(e.target.value) }))}><option value="0">Selected day only</option><option value="7">7 days</option><option value="14">14 days</option><option value="30">30 days</option><option value="all">Any time before date</option></select></label><label className="check-label"><input type="checkbox" checked={filters.includeAlternates} onChange={e => setFilters(f => ({ ...f, includeAlternates: e.target.checked }))}/> Alternate claims</label><button className="text-button" onClick={() => setShowHelp(true)}><Icon name="info" size={14}/> Reading this map</button></div>
        {selected.length > 0 && <div className="selection-tray"><span className="eyebrow">HISTORY SET</span><div className="selection-chips">{selected.map((id, i) => <button key={id} title={`Remove ${unitMap.get(id)?.unit_name}`} onClick={() => toggleUnit(id)} style={{ '--track-color': historyColors[i % historyColors.length] } as CSSProperties}><i/>{unitMap.get(id)?.unit_name ?? id}<Icon name="close" size={11}/></button>)}</div><button className="text-button clear-selection" onClick={() => setSelected([])}>Clear</button></div>}
        <section className="time-panel" aria-label="Time controls"><div className="time-controls"><button className="icon-button" title="Previous observation date" aria-label="Previous observation date" disabled={!events.some(d => d < date)} onClick={() => stepEvent(-1)}><Icon name="previous"/></button><button className="play-button" aria-label={playing ? 'Pause playback' : 'Play timeline'} onClick={() => { if (!playing && date >= sliderEnd) setDate(sliderStart); setFocusedId(''); setPlaying(p => !p); }}><Icon name={playing ? 'pause' : 'play'}/></button><button className="icon-button" title="Next observation date" aria-label="Next observation date" disabled={!events.some(d => d > date)} onClick={() => stepEvent(1)}><Icon name="next"/></button><select className="speed-select" aria-label="Playback speed" value={speed} onChange={e => setSpeed(Number(e.target.value))}><option value="1">1 day/s</option><option value="2">2 days/s</option><option value="5">5 days/s</option><option value="10">10 days/s</option></select><div className="current-date"><label htmlFor="selected-date">SELECTED DATE</label><DateField id="selected-date" label="Selected date" value={date} min={sliderStart} max={sliderEnd} onCommit={changeDate}/></div><div className="day-steppers"><button className="icon-button" aria-label="Previous day" disabled={date <= sliderStart} onClick={() => changeDate(isoDay(dayNumber(date) - 1))}>−</button><button className="icon-button" aria-label="Next day" disabled={date >= sliderEnd} onClick={() => changeDate(isoDay(dayNumber(date) + 1))}>+</button></div></div><div className="slider-track"><input type="range" aria-label="Situation date slider" aria-valuetext={formatDate(date)} min={dayNumber(sliderStart)} max={dayNumber(sliderEnd)} value={dayNumber(date)} style={{ '--progress': `${progress}%` } as CSSProperties} onChange={e => changeDate(isoDay(Number(e.target.value)))}/><div className="slider-labels"><span>{formatDate(sliderStart)}</span><span>{daysBetween(sliderStart, sliderEnd) + 1} DAYS OF RECORD</span><span>{formatDate(sliderEnd)}</span></div></div></section>
      </main>

      {detailsOpen && <aside className="detail-panel"><div className="detail-heading"><span className="eyebrow">FORMATION RECORD</span><button className="icon-button" aria-label="Close formation details" onClick={() => setDetailsOpen(false)}><Icon name="close" size={17}/></button></div>
        {detail ? <><div className="detail-unit"><span className="unit-kicker">{detail.nationality} / {humanize(detail.echelon)}</span><h2>{detail.unit_name}</h2><span className="unit-id">{detail.unit_id}</span><button className={`history-add ${selected.includes(detail.unit_id) ? 'included' : ''}`} onClick={() => toggleUnit(detail.unit_id)}><Icon name={selected.includes(detail.unit_id) ? 'close' : 'plus'} size={14}/>{selected.includes(detail.unit_id) ? 'Remove from history set' : 'Add to movement history'}</button></div>
          <div className="detail-tabs"><button className={timelineTab === 'observation' ? 'active' : ''} onClick={() => setTimelineTab('observation')}>Observation</button><button className={timelineTab === 'chronology' ? 'active' : ''} onClick={() => setTimelineTab('chronology')}>Chronology <span>{chronology.length}</span></button></div>
          <div className="detail-scroll">{timelineTab === 'chronology' ? <div className="chronology"><p className="small-note">All recorded claims for this formation, including competing accounts. Select a record to inspect it.</p>{chronology.map(c => <button className={`chronology-row ${focused?.claim_id === c.claim_id ? 'active' : ''} ${c.date > date ? 'future' : ''}`} key={c.claim_id} onClick={() => { focusClaim(c); setTimelineTab('observation'); }}><span>{formatDate(c.date)}</span><strong>{c.location_name}</strong><small>{humanize(c.event_type)} · {c.claim_status} · {c.claim_id}</small></button>)}</div> : focused ? <ClaimDetails atlas={atlas} claim={focused} date={date} showPrecision={showPrecision} onPrecision={setShowPrecision} onClaim={focusClaim} onDate={() => { if (focused.date < rangeStart || focused.date > rangeEnd) setMode('situation'); setDate(focused.date); setFocusedId(''); setPlaying(false); }}/>
            : <div className="detail-empty"><h3>{detail.claim_rows ? 'No observation by this date' : 'A catalogued formation'}</h3><p>{detail.claim_rows ? `Its first recorded observation is ${formatDate(detail.first_claim_date)}.` : 'This unit has no location claims yet. Its presence in the catalogue does not establish a position.'}</p>{detail.claim_rows > 0 && <button onClick={() => { setMode('situation'); changeDate(detail.first_claim_date); setDate(detail.first_claim_date); }}>Go to first observation <Icon name="arrow" size={14}/></button>}{detail.unit_note && <p className="small-note">{detail.unit_note}</p>}</div>}</div>
        </> : <div className="detail-empty"><h3>Select a formation</h3><p>Choose a symbol or formation to inspect its observation and evidence.</p></div>}
      </aside>}
    </div>
    <footer className="app-footer"><span><b>WWII UNIT LOCATIONS</b> · CC BY-SA 4.0 · <button onClick={() => setShowHelp(true)}>Sources & interpretation</button></span><span>OBSERVATIONS, WITH THEIR UNCERTAINTIES.</span><span title={`Data package ${atlas.manifest.dataVersion}`}>DATA {atlas.manifest.dataVersion.slice(0, 6)}</span></footer>
    {showHelp && <div className="modal-backdrop" onClick={e => { if (e.target === e.currentTarget) setShowHelp(false); }}><section className="help-modal" role="dialog" aria-modal="true" aria-labelledby="help-title" onKeyDown={trapDialogFocus}><button autoFocus className="icon-button modal-close" aria-label="Close map guide" onClick={() => setShowHelp(false)}><Icon name="close"/></button><span className="eyebrow">A NOTE ON THE RECORD</span><h2 id="help-title">Read the evidence.<br/>Leave room for the unknown.</h2><p>This atlas maps sourced observations, rather than a continuous reconstruction of every formation’s location.</p><dl><dt>The time slider</dt><dd>Symbols show the latest recorded observation on or before the selected date, within your observation-age limit. Dashed symbols mark earlier observations; their labels show days elapsed. A unit may have several observations on its latest day.</dd><dt>Movement history</dt><dd>Check formations, choose a range, and play through their dated points. Dashed connectors indicate sequence, not verified roads or routes. Contested records and ambiguous same-day observations break connectors. The age filter applies to current symbols; historical points remain visible within the range.</dd><dt>Precision and confidence</dt><dd>A radius is an estimated spatial precision, not a unit’s boundary. Confidence scores support for the date and location; it is not a probability or a score for whether the event happened. A point may stand for an HQ, objective, sector or main body.</dd><dt>Competing accounts</dt><dd>Preferred and disputed claims are visible by default. Enable alternate claims to inspect other accounts. No preference is invented when a group is disputed.</dd><dt>Geography</dt><dd>The detailed basemap is modern geography styled to evoke the historical reference. It does not establish 1944 roads, borders or front lines. Bundled Natural Earth outlines provide a fallback when detailed map tiles are unavailable.</dd><dt>Credit</dt><dd>Unit-location data: WWII Unit Locations dataset, CC BY-SA 4.0, drawing on official histories, Wikipedia, Lexikon der Wehrmacht and the sources attached to each claim. App changes: typed packaging and visualization. Coordinates include © OpenStreetMap contributors and Wikipedia/Wikidata sources. Basemap: OpenFreeMap / OpenMapTiles / OpenStreetMap; fallback: Natural Earth (public domain).</dd></dl><button className="primary-button" onClick={() => setShowHelp(false)}>Return to the atlas <Icon name="arrow" size={16}/></button></section></div>}
  </div>;
}

function ClaimDetails({ atlas, claim: c, date, showPrecision, onPrecision, onClaim, onDate }: { atlas: Atlas; claim: Claim; date: string; showPrecision: boolean; onPrecision: (v: boolean) => void; onClaim: (c: Claim) => void; onDate: () => void; }) {
  const age = daysBetween(c.date, date);
  const competing = c.conflict_group_id ? atlas.claims.filter(x => x.conflict_group_id === c.conflict_group_id && x.claim_id !== c.claim_id) : [];
  const links = atlas.referenceLinks.filter(l => l.claim_id === c.claim_id);
  return <>
    <div className={`observation-age ${age !== 0 ? 'aged' : ''}`}><span className="status-dot visible"/><strong>{age === 0 ? 'Observed on selected date' : age > 0 ? `Last observed ${age} day${age === 1 ? '' : 's'} earlier` : `Record is ${-age} days after selected date`}</strong>{age !== 0 && <button className="text-button" onClick={onDate}>Go to date <Icon name="arrow" size={12}/></button>}</div>
    <div className="record-date">{formatDate(c.date)}<span>{c.claim_id}</span></div><h3 className="record-location">{c.location_name}</h3><div className="event-pill">{humanize(c.event_type)}</div><p className="activity-description">{c.current_activity}</p>
    <div className="evidence-grid"><div><span>POINT REPRESENTS</span><strong>{humanize(c.location_represents)}</strong></div><div><span>EST. PRECISION</span><strong>{c.precision_km} km radius</strong></div><div><span>DATE / PLACE SUPPORT</span><strong>{c.confidence.toFixed(1)} <small>rubric score</small></strong></div><div><span>CLAIM STATUS</span><strong>{c.claim_status}</strong></div></div>
    <label className="check-label precision-toggle"><input type="checkbox" checked={showPrecision} onChange={e => onPrecision(e.target.checked)}/> Show this point’s precision radius</label>
    <div className="detail-section"><h4>Location provenance</h4><p>{c.location_basis ? humanize(c.location_basis) : 'Location basis not yet reviewed'}</p>{c.location_date && <p>Coordinate documented for {formatDate(c.location_date)}{c.location_temporal_offset_days !== null ? ` (${c.location_temporal_offset_days > 0 ? '+' : ''}${c.location_temporal_offset_days} days from event)` : ''}.</p>}{c.coord_override && <p>{c.coord_override}</p>}<small>{Math.abs(c.latitude).toFixed(4)}° {c.latitude >= 0 ? 'N' : 'S'}, {Math.abs(c.longitude).toFixed(4)}° {c.longitude >= 0 ? 'E' : 'W'} · {c.place_id}</small></div>
    {competing.length > 0 && <div className="conflict-box"><h4>Competing accounts · {c.conflict_group_id}</h4><p>Compare the evidence for this event.</p>{competing.map(other => <button key={other.claim_id} onClick={() => onClaim(other)}>{other.claim_id} · {other.claim_status}<span>{formatDate(other.date, true)} · {other.location_name}</span></button>)}</div>}
    <div className="detail-section"><h4>Operational context</h4><p className="operation-path">{c.operation_path}</p><dl className="context-list"><dt>Commander</dt><dd>{c.commander}</dd><dt>Activity annotation</dt><dd>{c.activity_status ? `${humanize(c.activity_status)} · ${c.activity_basis} · ${c.activity_span} record` : 'Not reviewed on this record'}</dd>{c.engaged_with_names && <><dt>Opponents</dt><dd>{c.engaged_with_names}</dd></>}</dl><small>Activity annotations describe this record. They are not carried forward as a current state.</small></div>
    {c.command_relationships.length > 0 && <details className="detail-disclosure"><summary>Command relationships <span>{c.command_relationships.length}</span></summary><p className="small-note">Relationships listed by this observation, not a reconstructed command chain for the slider date.</p>{c.command_relationships.map((r, i) => <div className="relationship" key={i}><span>{humanize(r.relationship)}</span><strong>{atlas.units.find(u => u.unit_id === r.unit_id)?.unit_name ?? r.unit_id ?? 'Unknown headquarters'}</strong>{r.effective_from && <small>From {r.effective_from}{r.effective_to ? ` through ${r.effective_to}` : ' · end not listed on this claim'}</small>}{r.note && <p>{r.note}</p>}</div>)}</details>}
    {c.strength_json && <details className="detail-disclosure"><summary>Sourced strength</summary><dl className="context-list">{Object.entries(c.strength_json).map(([k, v]) => <div key={k}><dt>{humanize(k)}</dt><dd>{typeof v === 'object' ? JSON.stringify(v) : String(v)}</dd></div>)}</dl></details>}
    <div className="detail-section sources-section"><h4>Sources & evidence <span>{c.reference_ids.length}</span></h4>{c.reference_ids.map(id => {
      const r = atlas.references.find(r => r.reference_id === id);
      const roles = links.filter(l => l.reference_id === id);
      return <div className="source-card" key={id}><div><span>{id}</span><small>{[...new Set(roles.map(l => humanize(l.role)))].join(' / ')}</small></div><a href={safeLink(r?.url ?? '')} target="_blank" rel="noopener noreferrer">{r?.short_title ?? id} <span>↗</span></a>{[...new Set(roles.map(l => l.locator).filter(Boolean))].map(loc => <p key={loc}>{loc}</p>)}<small>{r?.source_family.replaceAll('_', ' ')}</small></div>;
    })}</div>
    <details className="detail-disclosure record-notes"><summary>Record notes & caveats</summary><p>{c.notes}</p></details>
  </>;
}
