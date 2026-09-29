import React from 'react'

const STYLES = {
  waiting: 'text-ink-500 border-ink-700',
  running: 'text-signal-amber border-signal-amber',
  complete: 'text-signal-green border-signal-green',
  failed: 'text-signal-red border-signal-red',
  detected: 'text-signal-amber border-signal-amber',
  not_detected: 'text-signal-green border-signal-green',
}

export default function StatusBadge({ status, children }) {
  const cls = STYLES[status] || STYLES.waiting
  return (
    <span
      className={[
        'inline-flex items-center gap-1.5 px-2 py-0.5 text-[10px] font-mono uppercase tracking-wider2 border',
        cls,
      ].join(' ')}
    >
      <span className="w-1 h-1 rounded-full bg-current" />
      {children || status}
    </span>
  )
}
