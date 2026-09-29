import React from 'react'
import { ImageOff } from 'lucide-react'

export default function SARMaskViewer({ available }) {
  return (
    <div className="panel p-4">
      <h3 className="text-[12px] font-semibold tracking-wide text-ink-100 mb-3">SAR Visualization</h3>
      <div className="h-72 border border-border bg-abyss-900 flex items-center justify-center relative overflow-hidden">
        {available ? (
          <div className="absolute inset-0 bg-[radial-gradient(circle_at_38%_55%,rgba(224,160,48,0.28),transparent_45%),radial-gradient(circle_at_60%_40%,rgba(224,160,48,0.14),transparent_55%)]" >
            <svg viewBox="0 0 400 300" className="w-full h-full opacity-70">
              <defs>
                <filter id="grain">
                  <feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="2" stitchTiles="stitch" />
                  <feColorMatrix type="saturate" values="0" />
                </filter>
              </defs>
              <rect width="400" height="300" filter="url(#grain)" opacity="0.12" />
              <path
                d="M120,160 C140,140 170,130 200,140 C230,150 250,175 235,200 C220,225 180,220 160,205 C140,190 100,180 120,160 Z"
                fill="#E0A030"
                opacity="0.5"
              />
            </svg>
          </div>
        ) : (
          <div className="flex flex-col items-center gap-2 text-ink-700">
            <ImageOff size={22} strokeWidth={1.5} />
            <span className="text-[11px] uppercase tracking-wider2">SAR Visualization Unavailable</span>
          </div>
        )}
      </div>
    </div>
  )
}
