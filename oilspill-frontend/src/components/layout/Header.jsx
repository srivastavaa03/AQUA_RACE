import { Radar, Satellite } from 'lucide-react'

export default function Header() {
  return (
    <header className="flex h-14 shrink-0 items-center justify-between border-b border-deck-600 bg-hull-900 px-5">
      <div className="flex items-center gap-3">
        <div className="flex h-8 w-8 items-center justify-center rounded-sm bg-sonar-500/10 border border-sonar-500/30">
          <Radar size={16} className="text-sonar-400" strokeWidth={1.75} />
        </div>
        <div className="leading-tight">
          <p className="text-[13px] font-semibold tracking-tight text-mist-100">Oil Spill Origin Investigation</p>
          <p className="text-[11px] text-mist-500">SIH26143 · SAR + AIS correlation desk</p>
        </div>
      </div>

      <div className="flex items-center gap-4 text-[11px] text-mist-500">
        <div className="flex items-center gap-1.5">
          <Satellite size={13} strokeWidth={1.75} />
          <span>Sentinel-1 · Copernicus · ERA5 · GFW</span>
        </div>
        <span className="rounded-full border border-flare-500/30 bg-flare-500/10 px-2 py-0.5 text-flare-400">
          Mock data mode
        </span>
      </div>
    </header>
  )
}
