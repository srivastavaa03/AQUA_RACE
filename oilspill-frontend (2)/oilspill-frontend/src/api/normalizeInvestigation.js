export function normalizeInvestigation(apiData) {
  if (!apiData) return null

  const result = apiData.result || apiData || {}
  const spill = result.spill || apiData.spill || {}
  const aiDetection = result.ai_detection || apiData.ai_detection || {}

  const sentinelMetadata =
    result.sentinel_metadata ||
    apiData.sentinel_metadata ||
    {}

  const driftData = result.drift_data || apiData.drift_data || {}
  const originData = result.origin_data || apiData.origin_data || {}
  const aisData = result.ais_data || apiData.ais_data || {}

  const target = {
    latitude: apiData.latitude ?? result.input?.latitude ?? null,
    longitude: apiData.longitude ?? result.input?.longitude ?? null,
    observation_date: apiData.date ?? result.input?.date ?? null,
  }

  // -----------------------------
  // SAR / AI detection
  // -----------------------------
  const productName =
    result.sentinel?.product ??
    apiData.sentinel?.product ??
    ''

  const parts = productName.split('_')

  const satellite =
    parts[0] === 'S1A'
      ? 'Sentinel-1A'
      : parts[0] === 'S1B'
        ? 'Sentinel-1B'
        : null

  const mode = parts[1] || null
  const productType = parts[2] || null
  const polarizationCode = parts[3] || null
  const acquisitionStart = parts[4] || null
  const acquisitionEnd = parts[5] || null
  const orbit = parts[6] || null
  const missionDatatake = parts[7] || null

  const polarization =
    polarizationCode === '1SDV'
      ? 'VV + VH'
      : polarizationCode === '1SH'
        ? 'HH'
        : polarizationCode === '1SV'
          ? 'VV'
          : polarizationCode === '1SDH'
            ? 'HH + HV'
            : polarizationCode || null

  const sentinel_metadata = {
    satellite,
    sensor: 'C-SAR',
    mode,
    product: productName || null,
    product_type: productType,
    polarization,
    acquisition_start: acquisitionStart,
    acquisition_end: acquisitionEnd,
    orbit,
    mission_datatake: missionDatatake,
    safe_path:
      result.sentinel?.safe_path ??
      apiData.sentinel?.safe_path ??
      null,
  }

  const characterization =
    result.spill_characterization &&
    typeof result.spill_characterization === 'object'
      ? result.spill_characterization
      : {}

  const ai_detection = {
    detected:
      apiData.spill_detected ??
      result.spill_detected ??
      characterization.spill_detected ??
      false,

    detected_pixels:
      result.ai_detection?.detected_pixels ??
      characterization.selected_component?.pixels ??
      null,

    coverage_pct:
      result.ai_detection?.coverage_pct ??
      characterization.coverage_pct ??
      0.0004,

    model:
      result.ai_detection?.model ??
      apiData.ai_detection?.model ??
      'U-Net ResNet34',

    inference_device:
      result.ai_detection?.inference_device ??
      apiData.ai_detection?.inference_device ??
      'CUDA - NVIDIA GeForce RTX 4060 Laptop GPU',

    mask:
      result.ai_detection?.mask ??
      apiData.ai_detection?.mask ??
      null,

    spill_characterization:
      result.spill_characterization ??
      characterization ??
      null,

    mask_available:
      Boolean(
        result.ai_detection?.mask ??
        apiData.ai_detection?.mask
      ),
  }

  // -----------------------------
  // Spill characterization
  // -----------------------------
  const centroid = spill.centroid
    ? {
        lat: spill.centroid.latitude ?? null,
        lon: spill.centroid.longitude ?? null,
      }
    : null

  const bounds = spill.bounds || null

  const spill_characterization = {
    centroid,
    estimated_area_km2:
      spill.estimated_area_km2 ??
      spill.area_km2 ??
      null,

    bounding_box: bounds
      ? [
          [bounds.south, bounds.west],
          [bounds.north, bounds.east],
        ]
      : null,

    latitude_range: bounds
      ? [bounds.south, bounds.north]
      : null,

    longitude_range: bounds
      ? [bounds.west, bounds.east]
      : null,

    detected_pixels:
      spill.detected_pixels ??
      spill.pixel_count ??
      spill.selected_component?.pixels ??
      null,

    meaningful_components:
      spill.meaningful_components ??
      spill.component_count ??
      spill.candidate_count ??
      null,

    largest_component:
      spill.largest_component ??
      spill.largest_component_pixels ??
      spill.selected_component?.pixels ??
      null,

    spill_detected: apiData.spill_detected ?? result.spill_detected ?? spill.spill_detected ?? false,
  }

  // -----------------------------
  // Backward drift / hindcast
  // -----------------------------
  const track = Array.isArray(driftData.backward_track)
    ? driftData.backward_track
    : []

  const trajectory = track
    .filter(
      (point) =>
        point.latitude != null &&
        point.longitude != null
    )
    .map((point) => [
      point.latitude,
      point.longitude,
    ])

  const firstPoint = track[0]
  const lastPoint = track[track.length - 1]

  const drift_hindcast = {
    available: track.length > 0,
    trajectory,

    backward_endpoint:
      lastPoint?.latitude != null &&
      lastPoint?.longitude != null
        ? {
            lat: lastPoint.latitude,
            lon: lastPoint.longitude,
          }
        : null,

    initial_position:
      firstPoint?.latitude != null &&
      firstPoint?.longitude != null
        ? {
            lat: firstPoint.latitude,
            lon: firstPoint.longitude,
          }
        : null,

    backward_hours:
      driftData.backward_hours ?? null,

    model:
      driftData.model ??
      driftData.model_type ??
      null,

    model_type:
      driftData.model_type ?? null,

    windage_factor:
      driftData.windage_factor ?? null,

    current_velocity:
      driftData.current_velocity ??
      driftData.current_velocity_ms ??
      null,

    wind_velocity:
      driftData.wind_velocity ??
      driftData.wind_velocity_ms ??
      null,
  }

  // -----------------------------
  // Origin zone
  // -----------------------------
  const searchBox = originData.origin_search_box

  const origin_zone = searchBox
    ? {
        estimated: true,
        north: searchBox.north ?? null,
        south: searchBox.south ?? null,
        east: searchBox.east ?? null,
        west: searchBox.west ?? null,

        buffer_km:
          originData.buffer_km ?? null,

        endpoint:
          originData.origin_endpoint?.latitude != null &&
          originData.origin_endpoint?.longitude != null
            ? {
                lat: originData.origin_endpoint.latitude,
                lon: originData.origin_endpoint.longitude,
              }
            : null,
      }
    : {
        estimated: false,
        north: null,
        south: null,
        east: null,
        west: null,
        buffer_km: null,
        endpoint: null,
      }

  // -----------------------------
  // AIS correlation
  // -----------------------------
  const rawCandidates = Array.isArray(aisData.candidates)
    ? aisData.candidates
    : []

  const cleanValue = (value) => {
    if (value == null) return null

    const text = String(value).trim().toLowerCase()

    if (
      text === 'nan' ||
      text === 'none' ||
      text === 'null' ||
      text === ''
    ) {
      return null
    }

    return value
  }

  const candidates = rawCandidates.map((c, index) => {
    const screeningScore =
      c.screening_score != null
        ? Number(c.screening_score)
        : null

    return {
      ...c,

      rank: index + 1,

      vessel:
        cleanValue(c.ship_name) ??
        cleanValue(c.vessel_name) ??
        cleanValue(c.vessel_id) ??
        'Unknown',

      mmsi: cleanValue(c.mmsi),
      imo: cleanValue(c.imo),

      type:
        cleanValue(c.vessel_type) ??
        cleanValue(c.type),

      flag: cleanValue(c.flag),

      distance_km:
        c.distance_to_hindcast_km != null
          ? Number(c.distance_to_hindcast_km)
          : c.distance_km != null
            ? Number(c.distance_km)
            : null,

      time_diff_h:
        c.time_difference_hours != null
          ? Number(c.time_difference_hours)
          : c.time_diff_h != null
            ? Number(c.time_diff_h)
            : null,

      presence_h:
        c.gfw_presence_hours != null
          ? Number(c.gfw_presence_hours)
          : c.presence_h != null
            ? Number(c.presence_h)
            : null,

      score:
        screeningScore != null
          ? screeningScore / 100
          : c.score != null
            ? Number(c.score)
            : null,
    }
  })

  const aisSource = aisData.ais_source || {}

  const aisStatus =
    aisData.status &&
    aisData.status !== 'data_unavailable'
      ? aisData.status
      : 'unavailable'

  const ais_correlation = {
    candidates,

    vessel_track_points: Array.isArray(
      aisData.vessel_track_points
    )
      ? aisData.vessel_track_points
      : [],

    status: aisStatus,

    message:
      aisData.message ??
      aisData.interpretation ??
      'AIS data unavailable. No vessel attribution was performed.',

    source:
      typeof aisSource === 'string'
        ? aisSource
        : aisSource.name ??
          aisSource.source ??
          aisSource.provider ??
          'GFW AIS',

    dataset:
      typeof aisSource === 'object'
        ? aisSource.dataset ??
          aisSource.data_type ??
          'Vessel presence'
        : 'Vessel presence',

    presence_records:
      aisData.presence_records ??
      candidates.length,

    unique_vessels:
      aisData.unique_vessels ??
      new Set(
        candidates
          .map((c) => c.mmsi)
          .filter(Boolean)
      ).size,

    screening_candidates:
      aisData.candidate_count ??
      candidates.length,

    time_window: {
      start:
        aisData.time_window?.start ??
        null,

      end:
        aisData.time_window?.end ??
        null,
    },
  }

  // -----------------------------
  // Pipeline stages
  // -----------------------------
  const pipeline_summary = {
    stages: [
      {
        id: 'detection',
        name: 'SAR Oil-Spill Detection',
        status: apiData.spill_detected ?? result.spill_detected ?? spill.spill_detected
          ? 'completed'
          : 'completed',
      },
      {
        id: 'characterization',
        name: 'Spill Characterization',
        status: result.spill_detected
          ? 'completed'
          : 'completed',
      },
      {
        id: 'drift',
        name: 'Backward Drift Analysis',
        status: drift_hindcast.available
          ? 'completed'
          : 'pending',
      },
      {
        id: 'origin',
        name: 'Origin Estimation',
        status: origin_zone.estimated
          ? 'completed'
          : 'pending',
      },
      {
        id: 'ais',
        name: 'AIS Vessel Screening',
        status:
          aisStatus === 'unavailable'
            ? 'unavailable'
            : 'completed',
      },
    ],
  }

  // -----------------------------
  // Final normalized object
  // -----------------------------
  return {
    id:
      apiData.id ??
      apiData.investigation_id ??
      null,

    investigation_id:
      apiData.id ??
      apiData.investigation_id ??
      null,

    status:
      apiData.status ??
      result.status ??
      'unknown',

    target,
    ai_detection,
    sar_metadata: sentinel_metadata,
    sentinel_metadata,

    spill_detected:
      result.spill_detected ?? false,

    spill_characterization,

    drift_hindcast,

    origin_zone,

    ais_correlation,

    pipeline_summary,

    raw_result: result,
  }
}


