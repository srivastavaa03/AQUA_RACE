import { Target } from 'lucide-react'
import Panel, { Stat, Unavailable } from './Panel'

export default function OriginZonePanel({ originZone }) {
  if (!originZone) {
    return (
      <Panel icon={Target} title="Estimated origin zone" eyebrow="Backward-hindcast endpoint + uncertainty buffer">
        <Unavailable label="Origin zone data not returned by the backend yet." />
      </Panel>
    )
  }

  const { bounds } = originZone
  return (
    <Panel icon={Target} title="Estimated origin zone" eyebrow="Backward-hindcast endpoint + uncertainty buffer">
      <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
        <Stat
          label="Uncertainty buffer"
          value={originZone.uncertaintyKm !== undefined ? Number(originZone.uncertaintyKm).toFixed(1) : undefined}
          unit="km"
          tone="flare"
        />
        <Stat
          label="Endpoint"
          value={
            originZone.endpoint
              ? `${originZone.endpoint.lat.toFixed(4)}, ${originZone.endpoint.lon.toFixed(4)}`
              : undefined
          }
        />
        <Stat label="North / South" value={bounds ? `${bounds.north.toFixed(3)} / ${bounds.south.toFixed(3)}` : undefined} />
        <Stat label="East / West" value={bounds ? `${bounds.east.toFixed(3)} / ${bounds.west.toFixed(3)}` : undefined} />
      </div>
    </Panel>
  )
}
