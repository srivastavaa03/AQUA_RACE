import React from 'react'

export default function StatCard({ label, value, sub, tone = 'default', mono = true, icon: Icon }) {
  const toneClass = {
    default: 'text-ink-100',
    cyan: 'text-cyan-accent',
    amber: 'text-signal-amber',
    red: 'text-signal-red',
    green: 'text-signal-green',
  }[tone]

  return (
    <div className="panel p-4 flex flex-col gap-2">
      <div className="flex items-center justify-between">
        <span className="data-label">{label}</span>
        {Icon && <Icon size={14} strokeWidth={1.75} className="text-ink-700" />}
      </div>
      <div className={['text-xl font-semibold', mono ? 'font-mono' : '', toneClass].join(' ')}>{value}</div>
      {sub && <div className="text-[11px] text-ink-500">{sub}</div>}
    </div>
  )
}
