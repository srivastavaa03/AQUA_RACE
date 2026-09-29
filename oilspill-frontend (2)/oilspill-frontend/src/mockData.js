// =============================================================
// DEMO DATA — NOT LIVE
// This file is the ONLY place mock/demo data is permitted to live.
// It is used exclusively when USE_MOCK is enabled in api/investigationApi.js.
// Nothing in here should ever be merged with a real API response.
// =============================================================

export const DEMO_LABEL = 'DEMO DATA — NOT LIVE'

function buildMockInvestigation(id) {
  const lat = 19.0761
  const lon = 72.8321
  const obsDate = '2026-06-14'

  return {
    investigation_id: id,
    status: 'complete', // waiting | running | complete | failed
    created_at: '2026-06-14T14:32:00Z',
    target: { latitude: lat, longitude: lon, observation_date: obsDate },
    name: null,

    pipeline_summary: {
      stages: [
        { key: 'sentinel_search', label: 'Sentinel-1 Search', status: 'complete' },
        { key: 'sar_acquisition', label: 'SAR Acquisition', status: 'complete' },
        { key: 'ai_detection', label: 'AI Detection', status: 'complete' },
        { key: 'characterization', label: 'Characterization', status: 'complete' },
        { key: 'geolocation', label: 'Geolocation', status: 'complete' },
        { key: 'ocean_wind', label: 'Ocean + Wind', status: 'complete' },
        { key: 'backward_hindcast', label: 'Backward Hindcast', status: 'complete' },
        { key: 'origin_zone', label: 'Origin Zone', status: 'complete' },
        { key: 'ais_correlation', label: 'AIS Correlation', status: 'complete' },
      ],
    },

    sentinel_metadata: {
      satellite: 'Sentinel-1',
      sensor: 'SAR',
      mode: 'IW',
      product: 'GRDH',
      polarization: 'VV / VH',
      acquisition_start: '2026-06-14T13:47:02Z',
      acquisition_end: '2026-06-14T13:47:31Z',
      orbit: 'Descending, Rel. Orbit 60',
      mission_datatake: '0x10AC3F',
    },

    ai_detection: {
      detected: true,
      detected_pixels: 18420,
      coverage_pct: 0.62,
      model: 'UNet-ResNet34-SAR-v3',
      inference_device: 'CUDA:0 (T4)',
      mask_available: true,
    },

    spill_characterization: {
      detected: true,
      estimated_area_km2: 4.86,
      centroid: { lat: 19.0512, lon: 72.9027 },
      lat_range: [18.998, 19.104],
      lon_range: [72.851, 72.958],
      bounding_box: [[18.998, 72.851], [19.104, 72.958]],
      detected_pixels: 18420,
      meaningful_components: 4,
      largest_component_km2: 3.12,
    },

    ocean_wind: {
      ocean_current: { u: 0.18, v: -0.07 },
      wind: { u10: -3.4, v10: 2.1 },
    },

    drift_hindcast: {
      hindcast_hours: 96,
      initial_position: { lat: 19.0512, lon: 72.9027 },
      backward_endpoint: { lat: 18.912, lon: 72.774 },
      current_velocity_ms: 0.19,
      wind_velocity_ms: 4.0,
      windage_factor: 0.03,
      trajectory: [
        [19.0512, 72.9027],
        [19.031, 72.881],
        [19.006, 72.858],
        [18.978, 72.831],
        [18.951, 72.807],
        [18.912, 72.774],
      ],
    },

    origin_zone: {
      estimated: true,
      north: 18.934,
      south: 18.889,
      east: 72.799,
      west: 72.748,
      buffer_km: 6,
      center: { lat: 18.912, lon: 72.774 },
    },

    ais_correlation: {
      source: 'Global Fishing Watch',
      dataset: 'Public Global Presence',
      date_range: { start: '2026-06-10', end: '2026-06-14' },
      presence_records: 214,
      unique_vessels: 31,
      screening_candidates: 6,
      candidates: [
        {
          rank: 1,
          vessel: 'MV KONKAN STAR',
          mmsi: '419123456',
          imo: '9312456',
          type: 'Tanker',
          flag: 'IN',
          distance_km: 3.1,
          time_diff_h: 2.4,
          presence_h: 11.2,
          score: 0.91,
          closest_observation: '2026-06-14T04:10:00Z',
          origin_zone_relationship: 'Within buffer',
        },
        {
          rank: 2,
          vessel: 'MT SEA HARVEST',
          mmsi: '419887210',
          imo: '9455812',
          type: 'Tanker',
          flag: 'PA',
          distance_km: 5.6,
          time_diff_h: 6.1,
          presence_h: 4.5,
          score: 0.77,
          closest_observation: '2026-06-14T00:20:00Z',
          origin_zone_relationship: 'Within buffer',
        },
        {
          rank: 3,
          vessel: 'MV RATNAGIRI PIONEER',
          mmsi: '419772341',
          imo: 'N/A',
          type: 'Bulk Carrier',
          flag: 'IN',
          distance_km: 8.9,
          time_diff_h: 9.8,
          presence_h: 2.1,
          score: 0.58,
          closest_observation: '2026-06-13T21:05:00Z',
          origin_zone_relationship: 'Edge of buffer',
        },
        {
          rank: 4,
          vessel: 'MT GULF NAVIGATOR',
          mmsi: '351098765',
          imo: '9288117',
          type: 'Tanker',
          flag: 'PA',
          distance_km: 11.4,
          time_diff_h: 14.2,
          presence_h: 3.7,
          score: 0.44,
          closest_observation: '2026-06-13T15:30:00Z',
          origin_zone_relationship: 'Outside buffer',
        },
        {
          rank: 5,
          vessel: 'MV COASTAL EXPRESS',
          mmsi: '419551023',
          imo: '9130044',
          type: 'Cargo',
          flag: 'IN',
          distance_km: 13.2,
          time_diff_h: 18.6,
          presence_h: 6.0,
          score: 0.36,
          closest_observation: '2026-06-13T09:45:00Z',
          origin_zone_relationship: 'Outside buffer',
        },
        {
          rank: 6,
          vessel: 'MT ORION TRADER',
          mmsi: '412665543',
          imo: '9366721',
          type: 'Tanker',
          flag: 'PA',
          distance_km: 15.8,
          time_diff_h: 22.1,
          presence_h: 1.4,
          score: 0.29,
          closest_observation: '2026-06-13T02:15:00Z',
          origin_zone_relationship: 'Outside buffer',
        },
      ],
      vessel_track_points: [
        { mmsi: '419123456', lat: 18.905, lon: 72.771, timestamp: '2026-06-14T04:10:00Z' },
        { mmsi: '419887210', lat: 18.928, lon: 72.792, timestamp: '2026-06-14T00:20:00Z' },
        { mmsi: '419772341', lat: 18.951, lon: 72.812, timestamp: '2026-06-13T21:05:00Z' },
      ],
    },

    evidence_timeline: [
      { timestamp: '2026-06-14T13:47:31Z', source: 'Sentinel-1', status: 'complete', result: 'SAR scene acquired' },
      { timestamp: '2026-06-14T13:52:10Z', source: 'AI Detection Model', status: 'complete', result: 'Oil-spill candidate detected in scene' },
      { timestamp: '2026-06-14T13:53:44Z', source: 'Spill Characterization', status: 'complete', result: 'Estimated spill area 4.86 km²' },
      { timestamp: '2026-06-14T13:54:02Z', source: 'Geolocation', status: 'complete', result: 'Centroid resolved to 19.0512°, 72.9027°' },
      { timestamp: '2026-06-14T13:55:19Z', source: 'Ocean Current Service', status: 'complete', result: 'U/V current components retrieved' },
      { timestamp: '2026-06-14T13:55:33Z', source: 'Wind Service', status: 'complete', result: 'U10/V10 wind components retrieved' },
      { timestamp: '2026-06-14T13:58:47Z', source: 'Hindcast Engine', status: 'complete', result: '96-hour backward trajectory computed' },
      { timestamp: '2026-06-14T13:59:02Z', source: 'Origin Zone Generator', status: 'complete', result: 'Estimated origin zone generated' },
      { timestamp: '2026-06-14T14:04:51Z', source: 'Global Fishing Watch', status: 'complete', result: '6 AIS screening candidates identified' },
    ],
  }
}

export function getMockInvestigation(id = 'DEMO-0001') {
  return buildMockInvestigation(id)
}

export const MOCK_INVESTIGATION = buildMockInvestigation('DEMO-0001')
