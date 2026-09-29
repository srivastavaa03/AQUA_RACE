import React from 'react'
import InvestigationGate from '../components/investigation/InvestigationGate.jsx'
import DriftSummary from '../components/drift/DriftSummary.jsx'
import DriftTrajectory from '../components/drift/DriftTrajectory.jsx'
import EnvironmentalConditions from '../components/drift/EnvironmentalConditions.jsx'
import OriginZone from '../components/drift/OriginZone.jsx'

export default function DriftOrigin() {
  return (
    <InvestigationGate>
      {(inv) => (
        <div className="flex flex-col gap-6">
          <div>
            <h1 className="text-[16px] font-semibold tracking-wide text-ink-100">Drift &amp; Origin Analysis</h1>
            <p className="text-[12px] text-ink-500 mt-1">96-hour backward hindcast — Investigation {inv.investigation_id}</p>
          </div>

          <DriftTrajectory investigation={inv} />
          <DriftSummary drift={inv.drift_hindcast} />

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            <EnvironmentalConditions oceanWind={inv.ocean_wind} />
            <OriginZone originZone={inv.origin_zone} />
          </div>
        </div>
      )}
    </InvestigationGate>
  )
}
