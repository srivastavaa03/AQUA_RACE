import React from 'react'

const ITEMS = [
  { symbol: '●', label: 'Spill candidate', color: '#E0A030' },
  { symbol: '—', label: 'Backward trajectory', color: '#3ED6D0' },
  { symbol: '▣', label: 'Estimated origin zone', color: '#D9534F' },
  { symbol: '◆', label: 'AIS candidate', color: '#4FAE8C' },
]

export default function MapLegend({ items = ITEMS }) {
  return (
    <div className="absolute bottom-3 left-3 z-[400] bg-abyss-800/90 border border-border px-3 py-2 backdrop-blur-sm">
      <div className="flex flex-col gap-1">
        {items.map((item) => (
          <div key={item.label} className="flex items-center gap-2 text-[11px] text-ink-300">
            <span style={{ color: item.color }} className="font-mono w-3 text-center">
              {item.symbol}
            </span>
            <span>{item.label}</span>
          </div>
        ))}
      </div>
    </div>
  )
}
