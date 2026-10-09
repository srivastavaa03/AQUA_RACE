import { Waves } from 'lucide-react'
import Panel, { Stat, Unavailable } from './Panel'

export default function CharacterizationPanel({ characterization }) {
  if (!characterization) {
    return (
      <Panel icon={Waves} title="Spill characterization" eyebrow="Connected-component analysis">
        <Unavailable label="Characterization data not returned by the backend yet." />
      </Panel>
    )
  }

  const { centroid, bounds } = characterization

  return (
    <Panel icon={Waves} title="Spill characterization" eyebrow="Connected-component analysis">
      <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
        <Stat label="Components found" value={characterization.connectedComponents?.toLocaleString()} />
        <Stat label="Meaningful" value={characterization.meaningfulComponents?.toLocaleString()} />
        <Stat label="Largest component" value={characterization.largestComponentPixels?.toLocaleString()} unit="px" />
        <Stat
          label="Estimated area"
          value={characterization.areaKm2 !== undefined ? Number(characterization.areaKm2).toFixed(2) : undefined}
          unit="km²"
          tone="sonar"
        />
      </div>

      <div className="mt-4 grid grid-cols-2 gap-4 border-t border-deck-600 pt-4 sm:grid-cols-4">
        <Stat label="Centroid lat" value={centroid?.lat?.toFixed(5)} />
        <Stat label="Centroid lon" value={centroid?.lon?.toFixed(5)} />
        <Stat
          label="Bounds N / S"
          value={bounds ? `${bounds.north.toFixed(3)} / ${bounds.south.toFixed(3)}` : undefined}
        />
        <Stat
          label="Bounds E / W"
          value={bounds ? `${bounds.east.toFixed(3)} / ${bounds.west.toFixed(3)}` : undefined}
        />
      </div>
    </Panel>
  )
}
