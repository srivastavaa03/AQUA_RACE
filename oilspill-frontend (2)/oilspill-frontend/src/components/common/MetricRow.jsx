import React from 'react'

export default function MetricRow({ label, value, mono = true }) {
  return (
    <div className="flex items-center justify-between py-2 border-b border-border last:border-b-0">
      <span className="text-[12px] text-ink-500">{label}</span>
      <span className={['text-[12px] text-ink-100', mono ? 'font-mono' : ''].join(' ')}>
        {value === null || value === undefined || value === '' ? 'N/A' : value}
      </span>
    </div>
  )
}
