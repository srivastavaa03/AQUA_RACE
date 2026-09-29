import React from 'react'
import InvestigationGate from '../components/investigation/InvestigationGate.jsx'
import EvidenceTimeline from '../components/evidence/EvidenceTimeline.jsx'

export default function Evidence() {
  return (
    <InvestigationGate>
      {(inv) => (
        <div className="flex flex-col gap-6 max-w-3xl">
          <div>
            <h1 className="text-[16px] font-semibold tracking-wide text-ink-100">Investigation Evidence</h1>
            <p className="text-[12px] text-ink-500 mt-1">Chronological pipeline record — Investigation {inv.investigation_id}</p>
          </div>
          <EvidenceTimeline events={inv.evidence_timeline} />
        </div>
      )}
    </InvestigationGate>
  )
}
