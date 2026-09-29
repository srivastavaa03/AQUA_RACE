import React from 'react'
import InvestigationGate from '../components/investigation/InvestigationGate.jsx'
import SARMetadataCard from '../components/sar/SARMetadataCard.jsx'
import SARDetectionCard from '../components/sar/SARDetectionCard.jsx'
import SARMaskViewer from '../components/sar/SARMaskViewer.jsx'

export default function SARAnalysis() {
  return (
    <InvestigationGate>
      {(inv) => (
        <div className="flex flex-col gap-6">
          <div>
            <h1 className="text-[16px] font-semibold tracking-wide text-ink-100">SAR Analysis</h1>
            <p className="text-[12px] text-ink-500 mt-1">Investigation {inv.investigation_id}</p>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            <SARMetadataCard meta={inv.sentinel_metadata} />
            <SARDetectionCard detection={inv.ai_detection} />
          </div>

          <SARMaskViewer available={inv.ai_detection?.mask_available} />
        </div>
      )}
    </InvestigationGate>
  )
}
