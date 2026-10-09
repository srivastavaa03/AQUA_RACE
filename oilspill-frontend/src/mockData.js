// ---------------------------------------------------------------------------
// This file previously held synthetic investigation data used before the
// real FastAPI backend was connected. The app now talks to the real
// backend exclusively (see src/api/investigationApi.js) and no longer
// imports fake investigations or results from here.
//
// PIPELINE_STAGES is kept here because it's UI configuration (the ordered
// list of stage labels shown in the progress tracker), not fabricated
// investigation data.
// ---------------------------------------------------------------------------

export const PIPELINE_STAGES = [
  { key: 'fetch_product', label: 'Locating Sentinel-1 product' },
  { key: 'ai_detection', label: 'Running SAR AI detection (U-Net)' },
  { key: 'metadata', label: 'Extracting Sentinel-1 metadata' },
  { key: 'characterization', label: 'Characterizing spill candidate' },
  { key: 'geolocation', label: 'Geolocating detected pixels' },
  { key: 'environmental', label: 'Fetching ocean current + ERA5 wind' },
  { key: 'hindcast', label: 'Running 96h backward drift hindcast' },
  { key: 'origin_zone', label: 'Building origin search zone' },
  { key: 'ais_correlation', label: 'Correlating AIS vessel presence' },
  { key: 'complete', label: 'Investigation complete' },
]
