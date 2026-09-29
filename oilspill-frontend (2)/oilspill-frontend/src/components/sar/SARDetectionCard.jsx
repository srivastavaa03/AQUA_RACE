import React from 'react'
import { AlertOctagon, CheckCircle2 } from 'lucide-react'
import MetricRow from '../common/MetricRow.jsx'

export default function SARDetectionCard({ detection }) {
  if (!detection) return null
  const { detected, detected_pixels, coverage_pct, model, inference_device } = detection

  return (
    <div className="panel p-4">
      <h3 className="text-[12px] font-semibold tracking-wide text-ink-100 mb-3">AI Detection</h3>
      <div
        className={[
          'flex items-center gap-2 px-3 py-2.5 mb-3 border text-[13px] font-semibold tracking-wide',
          detected
            ? 'border-signal-amber text-signal-amber bg-signal-amber/5'
            : 'border-signal-green text-signal-green bg-signal-green/5',
        ].join(' ')}
      >
        {detected ? <AlertOctagon size={16} /> : <CheckCircle2 size={16} />}
        {detected ? 'OIL-SPILL CANDIDATE DETECTED' : 'NO OIL-SPILL CANDIDATE DETECTED'}
      </div>
      <MetricRow label="Detected Pixels" value={detected_pixels?.toLocaleString()} />
      <MetricRow label="Coverage" value={coverage_pct != null ? `${(coverage_pct * 100).toFixed(2)}%` : null} />
      <MetricRow label="Model" value={model} mono={false} />
      <MetricRow label="Inference Device" value={inference_device} />
    </div>
  )
}
