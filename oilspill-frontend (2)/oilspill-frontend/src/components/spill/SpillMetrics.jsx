import React from 'react'
import StatCard from '../common/StatCard.jsx'
import { Droplets, Layers, Grid3x3, Maximize } from 'lucide-react'

export default function SpillMetrics({ spill }) {
  if (!spill) return null
  const centroidStr = spill.centroid ? `${spill.centroid.lat.toFixed(4)}°, ${spill.centroid.lon.toFixed(4)}°` : 'N/A'
  const latRange = spill.lat_range ? `${spill.lat_range[0].toFixed(3)}° – ${spill.lat_range[1].toFixed(3)}°` : 'N/A'
  const lonRange = spill.lon_range ? `${spill.lon_range[0].toFixed(3)}° – ${spill.lon_range[1].toFixed(3)}°` : 'N/A'

  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
      <StatCard label="Estimated Area" value={spill.estimated_area_km2 != null ? `${spill.estimated_area_km2.toFixed(2)} km²` : 'N/A'} icon={Droplets} />
      <StatCard label="Centroid" value={centroidStr} icon={Maximize} />
      <StatCard label="Latitude Range" value={latRange} icon={Grid3x3} />
      <StatCard label="Longitude Range" value={lonRange} icon={Grid3x3} />
      <StatCard label="Detected Pixels" value={spill.detected_pixels?.toLocaleString() ?? 'N/A'} icon={Layers} />
      <StatCard label="Meaningful Components" value={spill.meaningful_components ?? 'N/A'} icon={Layers} />
      <StatCard label="Largest Component" value={spill.largest_component_km2 != null ? `${spill.largest_component_km2.toFixed(2)} km²` : 'N/A'} icon={Layers} />
      <StatCard label="Spill Detected" value={spill.spill_detected ? 'YES' : 'NO'} tone={spill.spill_detected ? 'amber' : 'green'} icon={Droplets} />
    </div>
  )
}

