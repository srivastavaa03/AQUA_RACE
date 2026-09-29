import React from 'react'
import MetricRow from '../common/MetricRow.jsx'

export default function EnvironmentalConditions({ oceanWind }) {
  if (!oceanWind) return null
  const { ocean_current, wind } = oceanWind
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
      <div className="panel p-4">
        <h3 className="text-[12px] font-semibold tracking-wide text-ink-100 mb-2">Ocean Current</h3>
        <MetricRow label="U Component" value={ocean_current?.u != null ? `${ocean_current.u} m/s` : null} />
        <MetricRow label="V Component" value={ocean_current?.v != null ? `${ocean_current.v} m/s` : null} />
      </div>
      <div className="panel p-4">
        <h3 className="text-[12px] font-semibold tracking-wide text-ink-100 mb-2">Wind</h3>
        <MetricRow label="U10" value={wind?.u10 != null ? `${wind.u10} m/s` : null} />
        <MetricRow label="V10" value={wind?.v10 != null ? `${wind.v10} m/s` : null} />
      </div>
    </div>
  )
}
