import { Navigation } from 'lucide-react'
import Panel, { Stat, Unavailable } from './Panel'

export default function DriftPanel({ hindcast }) {
  if (!hindcast) {
    return (
      <Panel icon={Navigation} title="96-hour backward drift hindcast" eyebrow="Copernicus current + ERA5 wind">
        <Unavailable label="Drift hindcast data not returned by the backend yet." />
      </Panel>
    )
  }

  return (
    <Panel
      icon={Navigation}
      title="96-hour backward drift hindcast"
      eyebrow="Copernicus current + ERA5 wind"
    >
      <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
        <Stat label="Backward window" value={hindcast.backwardHours} unit="hours" />
        <Stat label="Windage" value={hindcast.windagePct !== undefined ? Number(hindcast.windagePct).toFixed(1) : undefined} unit="%" />
        <Stat label="Track points" value={hindcast.trackPoints} />
        <Stat
          label="Scene time"
          value={hindcast.sceneTime ? new Date(hindcast.sceneTime).toISOString().slice(11, 16) : undefined}
          unit={hindcast.sceneTime ? 'UTC' : undefined}
        />
      </div>
      <div className="mt-4 border-t border-deck-600 pt-4">
        <p className="mb-1 text-[11px] text-mist-500">96h-back endpoint (estimated release point)</p>
        {hindcast.endpoint ? (
          <p className="font-mono text-[14px] text-sonar-400">
            {hindcast.endpoint.lat.toFixed(6)}, {hindcast.endpoint.lon.toFixed(6)}
          </p>
        ) : (
          <Unavailable />
        )}
      </div>
    </Panel>
  )
}
