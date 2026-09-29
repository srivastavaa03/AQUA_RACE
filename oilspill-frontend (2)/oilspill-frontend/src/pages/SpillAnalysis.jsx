import React from 'react'
import InvestigationGate from '../components/investigation/InvestigationGate.jsx'
import SpillMetrics from '../components/spill/SpillMetrics.jsx'
import SpillCharacterization from '../components/spill/SpillCharacterization.jsx'
import InvestigationMap from '../components/map/InvestigationMap.jsx'

export default function SpillAnalysis() {
  return (
    <InvestigationGate>
      {(inv) => (
        <div className="flex flex-col gap-6">
          <div>
            <h1 className="text-[16px] font-semibold tracking-wide text-ink-100">Spill Characterization</h1>
            <p className="text-[12px] text-ink-500 mt-1">AI-detected oil-spill candidate — Investigation {inv.investigation_id}</p>
          </div>

          <SpillMetrics spill={inv.spill_characterization} />
          <InvestigationMap investigation={inv} showDrift={false} showVessels={false} height={440} />
          <SpillCharacterization spill={inv.spill_characterization} />
        </div>
      )}
    </InvestigationGate>
  )
}
