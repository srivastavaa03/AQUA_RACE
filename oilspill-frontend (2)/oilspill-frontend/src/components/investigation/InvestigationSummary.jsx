import React from 'react'
import { Radar, Droplets, MapPin, Clock, Target, Ship } from 'lucide-react'
import StatCard from '../common/StatCard.jsx'

export default function InvestigationSummary({ investigation }) {
  const { ai_detection, spill_characterization, drift_hindcast, origin_zone, ais_correlation } = investigation

  const centroid = spill_characterization?.centroid
  const centroidStr = centroid ? `${centroid.lat.toFixed(4)}\u00b0, ${centroid.lon.toFixed(4)}\u00b0` : 'N/A'

  return (
    <div className="grid grid-cols-2 sm:grid-cols-3 gap-2.5 w-full min-w-0">
      <StatCard
        label="SAR Detection"
        value={ai_detection?.detected ? 'YES' : 'NO'}
        tone={ai_detection?.detected ? 'amber' : 'green'}
        icon={Radar}
      />
      <StatCard
        label="Spill Area"
        value={
          spill_characterization?.estimated_area_km2 != null
            ? `${spill_characterization.estimated_area_km2.toFixed(2)} km\u00b2`
            : 'N/A'
        }
        icon={Droplets}
      />
      <StatCard label="Spill Centroid" value={centroidStr} icon={MapPin} />
      <StatCard
        label="Hindcast"
        value={drift_hindcast?.hindcast_hours ? `${drift_hindcast.hindcast_hours} HRS` : 'N/A'}
        icon={Clock}
      />
      <StatCard
        label="Origin Zone"
        value={origin_zone?.estimated ? 'ESTIMATED' : 'N/A'}
        tone="cyan"
        icon={Target}
      />
      <StatCard
        label="AIS Candidates"
        value={ais_correlation?.screening_candidates ?? 'N/A'}
        icon={Ship}
      />
    </div>
  )
}
