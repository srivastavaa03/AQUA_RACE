import React from 'react'
import StatusBadge from '../common/StatusBadge.jsx'

export default function EvidenceItem({ event, isLast }) {
  const time = new Date(event.timestamp)
  const timeStr = Number.isNaN(time.getTime())
    ? event.timestamp
    : `${time.toLocaleTimeString('en-GB', { hour: '2-digit', minute: '2-digit', timeZone: 'UTC' })} UTC`

  return (
    <div className="flex gap-4">
      <div className="flex flex-col items-center">
        <div className="w-2.5 h-2.5 rounded-full bg-cyan-accent shrink-0 mt-1.5" />
        {!isLast && <div className="w-px flex-1 bg-border min-h-[28px]" />}
      </div>
      <div className="pb-6">
        <div className="flex items-center gap-3 mb-1">
          <span className="text-[11px] font-mono text-ink-500">{timeStr}</span>
          <StatusBadge status={event.status} />
        </div>
        <div className="text-[13px] text-ink-100 font-medium">{event.source}</div>
        <div className="text-[12px] text-ink-500 mt-0.5">{event.result}</div>
      </div>
    </div>
  )
}
