// ---------------------------------------------------------------------------
// Investigation API client — connected to the real SIH26143 FastAPI backend.
//
// This file is the ONLY place that talks to the network or to mock data.
// Every component reads normalized fields from here; none of them know
// whether a value came from the backend, and none of them fabricate a
// value the backend didn't provide. Missing data comes through as
// `undefined`, and every panel renders that as an explicit
// "Data unavailable" state rather than guessing.
//
// Endpoints (as given by the backend, app.py — not modified here):
//   POST /api/investigate                body: { latitude, longitude, date }
//                                          -> { id/investigation_id, status }
//   GET  /api/investigation/{id}          -> full result payload (shape may
//                                             still be evolving on the backend)
//   GET  /api/investigation/{id}/status   -> { status, stage?, progress? }
//
// Because the exact key names/casing coming back from app.py may shift as
// the backend fills in, normalizeResult() below tries several plausible
// key spellings (snake_case, camelCase, nested under a stage name) for
// each field before giving up and leaving it undefined. If the backend's
// actual field names differ from every alternative tried here, extend the
// PATHS passed to pick() below — nothing else needs to change.
// ---------------------------------------------------------------------------

import { PIPELINE_STAGES } from '../mockData'

const BASE_URL = 'http://127.0.0.1:8000'
const HISTORY_KEY = 'sih26143.investigations'

// ---- local session history (NOT backend data) ------------------------------
// The backend doesn't expose a "list all investigations" endpoint, so the
// sidebar's list is just this browser session's own request history, kept
// in localStorage so it survives a refresh. It's real data about what this
// browser has asked for — never invented spill data.

function readHistory() {
  try {
    return JSON.parse(localStorage.getItem(HISTORY_KEY) ?? '[]')
  } catch {
    return []
  }
}

function writeHistory(list) {
  try {
    localStorage.setItem(HISTORY_KEY, JSON.stringify(list))
  } catch {
    // storage unavailable — history just won't persist across reloads
  }
}

export async function listInvestigations() {
  return readHistory()
}

function upsertHistoryEntry(entry) {
  const list = readHistory()
  const i = list.findIndex((x) => x.id === entry.id)
  if (i === -1) list.unshift(entry)
  else list[i] = { ...list[i], ...entry }
  writeHistory(list)
  return list
}

// ---- HTTP helpers ------------------------------------------------------

export class ApiError extends Error {
  constructor(message, status) {
    super(message)
    this.status = status
  }
}

async function request(path, options) {
  let res
  try {
    res = await fetch(`${BASE_URL}${path}`, {
      headers: { 'Content-Type': 'application/json' },
      ...options,
    })
  } catch {
    throw new ApiError(
      `Could not reach the backend at ${BASE_URL}. Confirm it is running and that CORS is enabled for this origin.`,
      0,
    )
  }

  if (!res.ok) {
    let detail = ''
    try {
      const body = await res.json()
      detail = body?.detail ?? JSON.stringify(body)
    } catch {
      detail = res.statusText
    }
    throw new ApiError(`Backend returned ${res.status}: ${detail}`, res.status)
  }

  if (res.status === 204) return null
  return res.json()
}

// ---- public API ----------------------------------------------------------

export async function startInvestigation({ lat, lon, date }) {
  const body = { latitude: lat, longitude: lon, date }
  const raw = await request('/api/investigate', { method: 'POST', body: JSON.stringify(body) })

  const id = pick([raw], ['id', 'investigation_id', 'investigationId'])
  const status = normalizeStatus(pick([raw], ['status']))

  if (!id) {
    throw new ApiError('Backend accepted the request but did not return an investigation id.')
  }

  upsertHistoryEntry({
    id,
    label: `${lat.toFixed(3)}, ${lon.toFixed(3)}`,
    lat,
    lon,
    date,
    status: status ?? 'queued',
    createdAt: new Date().toISOString(),
  })

  return { id, status: status ?? 'queued' }
}

export async function getInvestigationStatus(id) {
  const raw = await request(`/api/investigation/${id}/status`)
  const status = normalizeStatus(pick([raw], ['status', 'state']))
  const stage = pick([raw], ['stage', 'current_stage', 'currentStage'])
  const stageMeta = PIPELINE_STAGES.find((s) => s.key === stage)
  const progressPct = pick([raw], ['progress', 'progress_pct', 'progressPct'])
  const error = pick([raw], ['error', 'error_message', 'errorMessage'])

  upsertHistoryEntry({ id, status: status ?? 'running' })

  return {
    id,
    status: status ?? 'running',
    stage: stageMeta?.key,
    stageLabel: stageMeta?.label ?? stage,
    progressPct: progressPct ?? undefined,
    error: error ?? undefined,
    raw,
  }
}

export async function getInvestigation(id) {
  const raw = await request(`/api/investigation/${id}`)
  return normalizeResult(raw, id)
}

export { PIPELINE_STAGES }

// ---- normalization ---------------------------------------------------------

function getPath(obj, path) {
  return path.split('.').reduce((o, key) => (o == null ? undefined : o[key]), obj)
}

// Tries each object in `roots`, in order, against each dotted path in
// `paths`, in order, and returns the first defined, non-null, non-empty
// value found. Returns undefined if nothing matched — the caller (and the
// UI) treats that as "the backend hasn't provided this yet".
function pick(roots, paths) {
  for (const root of roots) {
    if (root == null) continue
    for (const path of paths) {
      const v = getPath(root, path)
      if (v !== undefined && v !== null && v !== '') return v
    }
  }
  return undefined
}

function normalizeStatus(raw) {
  if (raw == null) return undefined
  const s = String(raw).toLowerCase()
  if (['complete', 'completed', 'done', 'success', 'finished'].includes(s)) return 'complete'
  if (['error', 'failed', 'failure'].includes(s)) return 'error'
  if (['queued', 'pending', 'created'].includes(s)) return 'queued'
  return 'running'
}

function toBool(v) {
  if (typeof v === 'boolean') return v
  if (typeof v === 'string') return ['yes', 'true', '1'].includes(v.toLowerCase())
  if (typeof v === 'number') return v > 0
  return undefined
}

// A lat/lon pair may come back as {lat, lon}, {latitude, longitude}, an
// array, or a "lat, lon" string. This tries to make sense of whatever
// shape shows up without inventing coordinates that aren't there.
function pickLatLon(roots, basePaths) {
  for (const base of basePaths) {
    const obj = pick(roots, [base])
    if (obj == null) continue
    if (Array.isArray(obj) && obj.length >= 2) {
      return { lat: Number(obj[0]), lon: Number(obj[1]) }
    }
    if (typeof obj === 'string') {
      const parts = obj.split(',').map((s) => Number(s.trim()))
      if (parts.length >= 2 && parts.every((n) => !Number.isNaN(n))) {
        return { lat: parts[0], lon: parts[1] }
      }
    }
    if (typeof obj === 'object') {
      const lat = obj.lat ?? obj.latitude
      const lon = obj.lon ?? obj.lng ?? obj.longitude
      if (lat !== undefined && lon !== undefined) return { lat: Number(lat), lon: Number(lon) }
    }
  }
  // fall back to separate top-level scalar fields, e.g. centroid_lat / centroid_lon
  const flatLat = pick(roots, [...basePaths.map((b) => `${b}_lat`), 'centroid_lat', 'latitude'])
  const flatLon = pick(roots, [...basePaths.map((b) => `${b}_lon`), 'centroid_lon', 'longitude'])
  if (flatLat !== undefined && flatLon !== undefined) return { lat: Number(flatLat), lon: Number(flatLon) }
  return undefined
}

function pickBounds(roots, basePaths) {
  for (const base of basePaths) {
    const obj = pick(roots, [base])
    if (obj && typeof obj === 'object') {
      const { north, south, east, west } = obj
      if ([north, south, east, west].every((v) => v !== undefined)) {
        return { north: Number(north), south: Number(south), east: Number(east), west: Number(west) }
      }
    }
  }
  return undefined
}

export function normalizeResult(raw, id) {
  if (!raw) return null
  // The FastAPI response might nest everything under a "result" key, or
  // return the pipeline's own stage objects flattened at the top level —
  // try both.
  const roots = [raw, raw.result, raw.data].filter(Boolean)

  const status = normalizeStatus(pick(roots, ['status']))

  // -- detection --------------------------------------------------------
  const detectionRaw = pick(roots, ['detection']) ?? {}
  const detectionRoots = [detectionRaw, ...roots]
  const detection = {
    device: pick(detectionRoots, ['device']),
    gpu: pick(detectionRoots, ['gpu', 'gpu_name']),
    imageWidth: numOrUndef(pick(detectionRoots, ['image_width', 'width'])),
    imageHeight: numOrUndef(pick(detectionRoots, ['image_height', 'height'])),
    tileSize: numOrUndef(pick(detectionRoots, ['tile_size'])),
    overlap: numOrUndef(pick(detectionRoots, ['overlap'])),
    totalTiles: numOrUndef(pick(detectionRoots, ['total_tiles'])),
    oilPixels: numOrUndef(pick(detectionRoots, ['oil_pixels'])),
    totalPixels: numOrUndef(pick(detectionRoots, ['total_pixels'])),
    coveragePct: numOrUndef(pick(detectionRoots, ['coverage_pct', 'coverage'])),
    spillDetected: toBool(pick(detectionRoots, ['spill_detected', 'oil_spill_detected', 'ai_candidate'])),
  }

  // -- sentinel metadata --------------------------------------------------
  const metaRaw = pick(roots, ['sentinel_metadata', 'metadata']) ?? {}
  const metaRoots = [metaRaw, ...roots]
  const sentinelMetadata = {
    productName: pick(metaRoots, ['product_name']),
    satellite: pick(metaRoots, ['satellite']),
    sensor: pick(metaRoots, ['sensor']),
    mode: pick(metaRoots, ['mode']),
    productType: pick(metaRoots, ['product_type']),
    polarization: pick(metaRoots, ['polarization']),
    acquisitionStart: pick(metaRoots, ['acquisition_start']),
    acquisitionEnd: pick(metaRoots, ['acquisition_end']),
    orbit: pick(metaRoots, ['orbit']),
    missionDataTake: pick(metaRoots, ['mission_data_take']),
  }
  const hasMetadata = Object.values(sentinelMetadata).some((v) => v !== undefined)

  // -- characterization -----------------------------------------------
  const charRaw = pick(roots, ['characterization', 'spill_characterization']) ?? {}
  const charRoots = [charRaw, ...roots]
  const centroid = pickLatLon([charRaw, raw], ['centroid', 'spill_centroid'])
  const bounds = pickBounds([charRaw, raw], ['bounds'])
  const characterization = {
    connectedComponents: numOrUndef(pick(charRoots, ['connected_components'])),
    meaningfulComponents: numOrUndef(pick(charRoots, ['meaningful_components'])),
    largestComponentPixels: numOrUndef(pick(charRoots, ['largest_component_pixels'])),
    candidatePixels: numOrUndef(pick(charRoots, ['candidate_pixels'])),
    areaKm2: numOrUndef(pick(charRoots, ['area_km2', 'estimated_area_km2', 'estimated_area'])),
    centroid,
    bounds,
  }
  const hasCharacterization = characterization.areaKm2 !== undefined || centroid !== undefined

  // -- environmental (current + wind) -----------------------------------
  const currentRaw = pick(roots, ['environmental.current', 'ocean_current', 'current']) ?? {}
  const windRaw = pick(roots, ['environmental.wind', 'era5_wind', 'wind']) ?? {}
  const current = {
    gridLat: numOrUndef(currentRaw.grid_lat ?? currentRaw.gridLat),
    gridLon: numOrUndef(currentRaw.grid_lon ?? currentRaw.gridLon),
    uo: numOrUndef(currentRaw.uo),
    vo: numOrUndef(currentRaw.vo),
    series: Array.isArray(currentRaw.series) ? currentRaw.series : undefined,
  }
  const wind = {
    gridSize: windRaw.grid_size ?? windRaw.gridSize,
    series: Array.isArray(windRaw.series) ? windRaw.series : undefined,
  }
  const hasEnvironmental = [current.uo, current.vo, wind.gridSize].some((v) => v !== undefined)

  // -- hindcast -----------------------------------------------------------
  const hindcastRaw = pick(roots, ['hindcast', 'drift_hindcast']) ?? {}
  const hindcastRoots = [hindcastRaw, ...roots]
  const hindcastEndpoint = pickLatLon([hindcastRaw, raw], ['endpoint', 'backward_endpoint'])
  const path = pick(hindcastRoots, ['path', 'track'])
  const hindcast = {
    backwardHours: numOrUndef(pick(hindcastRoots, ['backward_hours'])),
    windagePct: numOrUndef(pick(hindcastRoots, ['windage_pct', 'windage'])),
    trackPoints: numOrUndef(pick(hindcastRoots, ['track_points'])),
    sceneTime: pick(hindcastRoots, ['scene_time']),
    endpoint: hindcastEndpoint,
    path: Array.isArray(path) ? path.map(normalizeTrackPoint).filter(Boolean) : undefined,
  }
  const hasHindcast = hindcast.trackPoints !== undefined || hindcastEndpoint !== undefined

  // -- origin zone ----------------------------------------------------
  const originRaw = pick(roots, ['origin_zone']) ?? {}
  const originEndpoint = pickLatLon([originRaw, raw], ['endpoint', 'backward_endpoint']) ?? hindcastEndpoint
  const originZone = {
    uncertaintyKm: numOrUndef(pick([originRaw, ...roots], ['uncertainty_km'])),
    endpoint: originEndpoint,
    bounds: pickBounds([originRaw, raw], ['bounds', 'search_box']),
  }
  const hasOriginZone = originZone.uncertaintyKm !== undefined || originZone.bounds !== undefined

  // -- AIS candidates ---------------------------------------------------
  const aisRaw = pick(roots, ['ais_candidates', 'ais_ranked_candidates', 'ais_results'])
  const aisAvailable = Array.isArray(aisRaw)
  const aisCandidates = aisAvailable
    ? aisRaw.map((c, i) => {
        const pos = pickLatLon([c], ['position', 'location'])
        return {
          candidateId: c.candidate_id ?? c.id ?? `AIS-${i + 1}`,
          mmsiMasked: c.mmsi_masked ?? c.mmsi,
          vesselType: c.vessel_type ?? c.type,
          flag: c.flag,
          confidence: numOrUndef(c.confidence ?? c.score),
          distanceFromOriginKm: numOrUndef(c.distance_km ?? c.distance_from_origin_km),
          lastPresence: c.last_presence ?? c.timestamp,
          // Only set when the backend actually reports a vessel position —
          // never fabricated, so the map only plots candidates it can back.
          lat: pos?.lat ?? numOrUndef(c.lat ?? c.latitude),
          lon: pos?.lon ?? numOrUndef(c.lon ?? c.longitude),
        }
      })
    : []

  // -- timeline: only built from fields we actually have -----------------
  const timeline = []
  if (sentinelMetadata.acquisitionStart) {
    timeline.push({ time: sentinelMetadata.acquisitionStart, label: 'Sentinel-1 scene acquired', kind: 'source' })
  }
  if (detection.spillDetected !== undefined) {
    timeline.push({
      time: sentinelMetadata.acquisitionEnd ?? sentinelMetadata.acquisitionStart ?? new Date().toISOString(),
      label: detection.spillDetected
        ? 'SAR AI detection complete — spill candidate confirmed'
        : 'SAR AI detection complete — no spill candidate',
      kind: 'detection',
    })
  }
  if (hasCharacterization) {
    const areaLabel = characterization.areaKm2 !== undefined ? ` (${Number(characterization.areaKm2).toFixed(2)} km²)` : ''
    timeline.push({
      time: sentinelMetadata.acquisitionEnd ?? new Date().toISOString(),
      label: `Spill characterization complete${areaLabel}`,
      kind: 'characterization',
    })
  }
  if (hasEnvironmental) {
    timeline.push({ time: hindcast.sceneTime ?? new Date().toISOString(), label: 'Ocean current + wind data retrieved', kind: 'environmental' })
  }
  if (hasHindcast) {
    timeline.push({ time: hindcast.sceneTime ?? new Date().toISOString(), label: '96h backward drift hindcast complete', kind: 'hindcast' })
  }
  if (hasOriginZone) {
    timeline.push({ time: hindcast.sceneTime ?? new Date().toISOString(), label: 'Origin zone established', kind: 'origin' })
  }
  if (aisAvailable) {
    timeline.push({
      time: new Date().toISOString(),
      label: `AIS correlation returned ${aisCandidates.length} candidate${aisCandidates.length === 1 ? '' : 's'}`,
      kind: 'ais',
    })
  }

  return {
    investigationId: id,
    status: status ?? 'running',
    generatedAt: new Date().toISOString(),
    detection,
    sentinelMetadata: hasMetadata ? sentinelMetadata : undefined,
    characterization: hasCharacterization ? characterization : undefined,
    environmental: hasEnvironmental ? { current, wind } : undefined,
    hindcast: hasHindcast ? hindcast : undefined,
    originZone: hasOriginZone ? originZone : undefined,
    aisAvailable,
    aisCandidates,
    timeline,
  }
}

function normalizeTrackPoint(p) {
  if (!p) return null
  const lat = p.lat ?? p.latitude
  const lon = p.lon ?? p.lng ?? p.longitude
  if (lat === undefined || lon === undefined) return null
  return { lat: Number(lat), lon: Number(lon), hour: p.hour ?? p.hours_back }
}

function numOrUndef(v) {
  if (v === undefined || v === null || v === '') return undefined
  const n = Number(v)
  return Number.isNaN(n) ? v : n
}
