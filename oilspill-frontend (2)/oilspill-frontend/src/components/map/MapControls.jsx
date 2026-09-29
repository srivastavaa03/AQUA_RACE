import React from 'react'
import { Eye, EyeOff } from 'lucide-react'

export default function MapControls({ layers, toggle }) {
  return (
    <div className="absolute top-3 right-3 z-[400] bg-abyss-800/90 border border-border px-3 py-2 backdrop-blur-sm flex flex-col gap-1.5">
      <div className="data-label mb-0.5">Layers</div>
      {layers.map((layer) => (
        <button
          key={layer.key}
          onClick={() => toggle(layer.key)}
          className="flex items-center gap-2 text-[11px] text-ink-300 hover:text-ink-100 transition-colors"
        >
          {layer.visible ? <Eye size={12} /> : <EyeOff size={12} className="text-ink-700" />}
          <span className={layer.visible ? '' : 'text-ink-700'}>{layer.label}</span>
        </button>
      ))}
    </div>
  )
}
