import React from 'react'
import { AlertTriangle } from 'lucide-react'

export default function ErrorState({ title = 'No connection to investigation API.', description, onRetry }) {
  return (
    <div className="panel flex flex-col items-center justify-center gap-3 py-16 text-center px-8 border-signal-red/40">
      <AlertTriangle size={22} className="text-signal-red" strokeWidth={1.75} />
      <p className="text-[13px] font-semibold text-ink-100 tracking-wide">{title}</p>
      {description && <p className="text-[12px] text-ink-500 max-w-md">{description}</p>}
      {onRetry && (
        <button
          onClick={onRetry}
          className="mt-2 px-4 py-1.5 text-[11px] uppercase tracking-wider2 border border-cyan-accent text-cyan-accent hover:bg-cyan-accent hover:text-abyss-950 transition-colors"
        >
          Retry
        </button>
      )}
    </div>
  )
}
