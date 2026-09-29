import React from 'react'
import StatCard from '../common/StatCard.jsx'
import { Clock, Navigation, Gauge, Wind } from 'lucide-react'

export default function DriftSummary({ drift }) {
  if (!drift) return null
  const initStr = drift.initial_position
    ? `${drift.initial_position.lat.toFixed(4)}°, ${drift.initial_position.lon.toFixed(4)}°`
    : 'N/A'
  const endStr = drift.backward_endpoint
    ? `${drift.backward_endpoint.lat.toFixed(4)}°, ${drift.backward_endpoint.lon.toFixed(4)}°`
    : 'N/A'

  return (
    <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
      <StatCard label="Hindcast Duration" value={drift.hindcast_hours ? `${drift.hindcast_hours} HRS` : 'N/A'} icon={Clock} />
      <StatCard label="Initial Position" value={initStr} icon={Navigation} />
      <StatCard label="Backward Endpoint" value={endStr} icon={Navigation} />
      <StatCard label="Current Velocity" value={drift.current_velocity_ms != null ? `${drift.current_velocity_ms} m/s` : 'N/A'} icon={Gauge} />
      <StatCard label="Wind Velocity" value={drift.wind_velocity_ms != null ? `${drift.wind_velocity_ms} m/s` : 'N/A'} icon={Wind} />
      <StatCard label="Windage Factor" value={drift.windage_factor ?? 'N/A'} icon={Gauge} />
    </div>
  )
}
