import { CircleDot, Clock, CheckCircle2, AlertTriangle } from 'lucide-react'
import NewInvestigationForm from '../investigation/NewInvestigationForm'

const STATUS_META = {
  complete: { label: 'Complete', icon: CheckCircle2, class: 'text-sonar-400' },
  running: { label: 'Running', icon: CircleDot, class: 'text-flare-400 animate-pulseDot' },
  queued: { label: 'Queued', icon: Clock, class: 'text-mist-500' },
  error: { label: 'Error', icon: AlertTriangle, class: 'text-hazard-400' },
}

export default function Sidebar({ investigations, selectedId, onSelect, onStart, isStarting }) {
  return (
    <aside className="flex w-[300px] shrink-0 flex-col border-r border-deck-600 bg-hull-900">
      <div className="border-b border-deck-600 p-4">
        <h2 className="mb-3 text-[11px] font-medium uppercase tracking-wide text-mist-500">
          New investigation
        </h2>
        <NewInvestigationForm onStart={onStart} isStarting={isStarting} />
      </div>

      <div className="flex-1 overflow-y-auto p-2">
        <h2 className="px-2 py-2 text-[11px] font-medium uppercase tracking-wide text-mist-500">
          Investigations
        </h2>
        {investigations.length === 0 && (
          <p className="px-2 py-1 text-[11.5px] text-mist-700">
            No investigations yet — analyze a location to get started.
          </p>
        )}
        <ul className="space-y-1">
          {investigations.map((inv) => {
            const meta = STATUS_META[inv.status] ?? STATUS_META.queued
            const StatusIcon = meta.icon
            const active = inv.id === selectedId
            return (
              <li key={inv.id}>
                <button
                  onClick={() => onSelect(inv.id)}
                  className={`w-full rounded-sm border px-3 py-2.5 text-left transition-colors ${
                    active
                      ? 'border-sonar-500/40 bg-sonar-500/10'
                      : 'border-transparent hover:border-deck-500 hover:bg-deck-700/60'
                  }`}
                >
                  <div className="flex items-center justify-between gap-2">
                    <span className="font-mono text-[12px] text-mist-300">{inv.id}</span>
                    <span className={`flex items-center gap-1 text-[10px] ${meta.class}`}>
                      <StatusIcon size={11} />
                      {meta.label}
                    </span>
                  </div>
                  <p className="mt-1 truncate text-[12.5px] text-mist-100">{inv.label}</p>
                  <p className="mt-0.5 font-mono text-[10.5px] text-mist-500">
                    {inv.lat.toFixed(3)}, {inv.lon.toFixed(3)} · {inv.date}
                  </p>
                </button>
              </li>
            )
          })}
        </ul>
      </div>
    </aside>
  )
}
