import { Check, Loader2 } from 'lucide-react'
import { PIPELINE_STAGES } from '../../api/investigationApi'

export default function StatusTracker({ status, currentStage }) {
  const currentIndex = PIPELINE_STAGES.findIndex((s) => s.key === currentStage)
  const isComplete = status === 'complete'

  return (
    <div className="rounded-md border border-deck-600 bg-deck-800/60 p-4 shadow-panel">
      <div className="mb-3 flex items-center justify-between">
        <h3 className="text-[13px] font-medium text-mist-100">Pipeline progress</h3>
        <span className="font-mono text-[11px] text-mist-500">
          {isComplete ? '10/10' : `${Math.max(currentIndex, 0) + 1}/${PIPELINE_STAGES.length}`}
        </span>
      </div>
      <ol className="grid grid-cols-2 gap-x-6 gap-y-2 sm:grid-cols-5">
        {PIPELINE_STAGES.map((stage, i) => {
          const done = isComplete || i < currentIndex
          const active = !isComplete && i === currentIndex
          return (
            <li key={stage.key} className="flex items-center gap-2">
              <span
                className={`flex h-4 w-4 shrink-0 items-center justify-center rounded-full border text-[9px] ${
                  done
                    ? 'border-sonar-500 bg-sonar-500/20 text-sonar-400'
                    : active
                    ? 'border-flare-500 bg-flare-500/10 text-flare-400'
                    : 'border-deck-500 text-mist-700'
                }`}
              >
                {done ? <Check size={10} /> : active ? <Loader2 size={9} className="animate-spin" /> : i + 1}
              </span>
              <span className={`text-[11.5px] leading-tight ${done || active ? 'text-mist-100' : 'text-mist-500'}`}>
                {stage.label}
              </span>
            </li>
          )
        })}
      </ol>
    </div>
  )
}
