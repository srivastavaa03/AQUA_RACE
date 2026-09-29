import React from 'react'
import { Ship } from 'lucide-react'

export default function VesselCandidateCard({ candidate, onClick, selected }) {
  return (
    <button
      onClick={onClick}
      className={[
        'w-full text-left panel p-3 flex items-center justify-between hover:border-cyan-accent/60 transition-colors',
        selected ? 'border-cyan-accent' : '',
      ].join(' ')}
    >
      <div className="flex items-center gap-3">
        <Ship size={16} className="text-ink-500" />
        <div>
          <div className="text-[12px] text-ink-100">{candidate.vessel}</div>
          <div className="text-[10px] font-mono text-ink-500">{candidate.mmsi} &middot; {candidate.type}</div>
        </div>
      </div>
      <div className="text-[11px] font-mono text-ink-300">{candidate.score.toFixed(2)}</div>
    </button>
  )
}
