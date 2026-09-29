import React from 'react'
import InvestigationGate from '../components/investigation/InvestigationGate.jsx'
import InvestigationSummary from '../components/investigation/InvestigationSummary.jsx'
import PipelineProgress from '../components/investigation/PipelineProgress.jsx'
import InvestigationMap from '../components/map/InvestigationMap.jsx'

export default function InvestigationWorkspace() {
  return (
    <InvestigationGate>
      {(inv) => (
        <div className="flex flex-col gap-6">
          <section className="panel p-5">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 font-mono text-[12px]">
              <div>
                <div className="data-label">Investigation ID</div>
                <div className="text-ink-100 mt-1">{inv.id}</div>
              </div>

              <div>
                <div className="data-label">Target Coordinates</div>
                <div className="text-ink-100 mt-1">
                  {inv.target.latitude.toFixed(4)}°, {inv.target.longitude.toFixed(4)}°
                </div>
              </div>

              <div>
                <div className="data-label">Observation Date</div>
                <div className="text-ink-100 mt-1">
                  {inv.target.observation_date}
                </div>
              </div>

              <div>
                <div className="data-label">Pipeline State</div>
                <div className="text-signal-green mt-1 uppercase">
                  {inv.status}
                </div>
              </div>
            </div>
          </section>

          <div className="grid grid-cols-1 xl:grid-cols-[1fr_320px] gap-4">
            <InvestigationMap investigation={inv} height={480} />

            <div className="flex flex-col gap-3">
              <InvestigationSummary investigation={inv} />
            </div>
          </div>

          <section className="panel p-5">
            <h2 className="text-[13px] font-semibold tracking-wide text-ink-100 mb-4">
              Pipeline Progress
            </h2>

            <PipelineProgress
              stages={[
                { id: 'detection', name: 'SAR Oil-Spill Detection', status: inv.spill_detected ? 'completed' : 'completed' },
                { id: 'characterization', name: 'Spill Characterization', status: inv.spill_detected ? 'completed' : 'completed' },
                { id: 'drift', name: 'Backward Drift Analysis', status: inv.drift_hindcast?.available ? 'completed' : 'pending' },
                { id: 'origin', name: 'Origin Estimation', status: inv.origin_zone?.estimated ? 'completed' : 'pending' },
                { id: 'ais', name: 'AIS Vessel Screening', status: inv.ais_correlation?.status === 'unavailable' ? 'unavailable' : 'completed' },
              ]}
            />
          </section>
        </div>
      )}
    </InvestigationGate>
  )
}
