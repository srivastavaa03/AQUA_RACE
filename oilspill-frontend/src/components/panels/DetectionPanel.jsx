import { ScanLine } from 'lucide-react'
import Panel, { Stat } from './Panel'

export default function DetectionPanel({ detection }) {
  const badge =
    detection.spillDetected === undefined ? (
      <span className="rounded-full border border-deck-500 bg-hull-900 px-2 py-0.5 text-[10.5px] text-mist-500">
        Status unavailable
      </span>
    ) : (
      <span
        className={`rounded-full border px-2 py-0.5 text-[10.5px] ${
          detection.spillDetected
            ? 'border-hazard-500/40 bg-hazard-500/10 text-hazard-400'
            : 'border-sonar-500/40 bg-sonar-500/10 text-sonar-400'
        }`}
      >
        {detection.spillDetected ? 'Spill detected' : 'No spill'}
      </span>
    )

  return (
    <Panel
      icon={ScanLine}
      title="SAR AI detection"
      eyebrow={
        detection.device || detection.gpu
          ? `U-Net · ${(detection.device ?? '').toUpperCase()} · ${detection.gpu ?? ''}`
          : 'U-Net'
      }
      right={badge}
    >
      <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
        <Stat
          label="Scene size"
          value={
            detection.imageWidth !== undefined && detection.imageHeight !== undefined
              ? `${detection.imageWidth.toLocaleString()} × ${detection.imageHeight.toLocaleString()}`
              : undefined
          }
          unit="px"
        />
        <Stat
          label="Tiles processed"
          value={detection.totalTiles?.toLocaleString()}
          unit={detection.tileSize ? `@ ${detection.tileSize}px` : undefined}
        />
        <Stat label="Oil pixels" value={detection.oilPixels?.toLocaleString()} tone="hazard" />
        <Stat
          label="Coverage"
          value={detection.coveragePct !== undefined ? Number(detection.coveragePct).toFixed(3) : undefined}
          unit="%"
          tone="flare"
        />
      </div>
    </Panel>
  )
}
