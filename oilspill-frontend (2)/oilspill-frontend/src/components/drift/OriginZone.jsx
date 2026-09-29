import React from 'react'
import MetricRow from '../common/MetricRow.jsx'
import { AlertTriangle } from 'lucide-react'

export default function OriginZone({ originZone }) {
  if (!originZone) return null
  return (
    <div className="panel p-4">
      <h3 className="text-[12px] font-semibold tracking-wide text-ink-100 mb-2">Estimated Origin Zone</h3>
      <MetricRow label="North" value={originZone.north != null ? `${originZone.north.toFixed(4)}°` : null} />
      <MetricRow label="South" value={originZone.south != null ? `${originZone.south.toFixed(4)}°` : null} />
      <MetricRow label="East" value={originZone.east != null ? `${originZone.east.toFixed(4)}°` : null} />
      <MetricRow label="West" value={originZone.west != null ? `${originZone.west.toFixed(4)}°` : null} />
      <MetricRow label="Buffer" value={originZone.buffer_km != null ? `${originZone.buffer_km} km` : null} />

      <div className="mt-4 flex gap-2 items-start border border-signal-amber/40 bg-signal-amber/5 px-3 py-2.5">
        <AlertTriangle size={14} className="text-signal-amber shrink-0 mt-0.5" />
        <p className="text-[11px] text-ink-300 leading-relaxed">
          Backward trajectory represents a possible source pathway and does not establish the
          exact spill source.
        </p>
      </div>
    </div>
  )
}
