import { History, Satellite, ScanLine, Waves, Wind, Navigation, Target, Ship } from 'lucide-react'
import Panel, { Unavailable } from '../panels/Panel'

const ICONS = {
  source: Satellite,
  detection: ScanLine,
  characterization: Waves,
  environmental: Wind,
  hindcast: Navigation,
  origin: Target,
  ais: Ship,
}

export default function EvidenceTimeline({ timeline }) {
  if (!timeline || timeline.length === 0) {
    return (
      <Panel icon={History} title="Evidence timeline" eyebrow="Chronological pipeline audit trail">
        <Unavailable label="No timestamped stage data available yet to build a timeline." />
      </Panel>
    )
  }

  return (
    <Panel icon={History} title="Evidence timeline" eyebrow="Chronological pipeline audit trail">
      <ol className="relative ml-1.5 space-y-5 border-l border-deck-600 pl-5">
        {timeline.map((event, i) => {
          const Icon = ICONS[event.kind] ?? History
          return (
            <li key={i} className="relative">
              <span className="absolute -left-[27px] flex h-4 w-4 items-center justify-center rounded-full border border-sonar-500/40 bg-hull-900">
                <Icon size={9} className="text-sonar-400" />
              </span>
              <p className="font-mono text-[10.5px] text-mist-500">
                {new Date(event.time).toISOString().slice(0, 16).replace('T', ' ')} UTC
              </p>
              <p className="text-[12.5px] text-mist-100">{event.label}</p>
            </li>
          )
        })}
      </ol>
    </Panel>
  )
}
