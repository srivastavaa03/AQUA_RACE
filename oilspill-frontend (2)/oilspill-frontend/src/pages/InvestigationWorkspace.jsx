import React from 'react'
import InvestigationGate from '../components/investigation/InvestigationGate.jsx'
import InvestigationSummary from '../components/investigation/InvestigationSummary.jsx'
import PipelineProgress from '../components/investigation/PipelineProgress.jsx'
import InvestigationMap from '../components/map/InvestigationMap.jsx'

export default function InvestigationWorkspace() {
  return (
    <InvestigationGate>
      {(inv) => (
        <div className="flex flex-col gap-6 min-w-0">

          {/* Investigation information */}
          <section className="panel p-5 min-w-0">
            <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-5 font-mono text-[12px]">

              <div className="min-w-0">
                <div className="data-label">Investigation ID</div>
                <div className="text-ink-100 mt-1 truncate" title={inv.id}>
                  {inv.id}
                </div>
              </div>

              <div className="min-w-0">
                <div className="data-label">Target Coordinates</div>
                <div className="text-ink-100 mt-1 whitespace-nowrap">
                  {inv.target.latitude?.toFixed(4)}&deg;, {inv.target.longitude?.toFixed(4)}&deg;
                </div>
              </div>

              <div className="min-w-0">
                <div className="data-label">Observation Date</div>
                <div className="text-ink-100 mt-1">
                  {inv.target.observation_date || 'N/A'}
                </div>
              </div>

              <div className="min-w-0">
                <div className="data-label">Pipeline State</div>
                <div className="text-signal-green mt-1 uppercase truncate">
                  {inv.status || 'unknown'}
                </div>
              </div>

            </div>
          </section>

          {/* Map + summary */}
          <div className="grid grid-cols-1 2xl:grid-cols-[minmax(0,1fr)_340px] gap-4 min-w-0">

            <div className="min-w-0">
              <InvestigationMap investigation={inv} height={480} />
            </div>

            <div className="min-w-0">
              <InvestigationSummary investigation={inv} />
            </div>

          </div>

          {/* Pipeline */}
          <section className="panel p-5 min-w-0">
            <h2 className="text-[13px] font-semibold tracking-wide text-ink-100 mb-4">
              Pipeline Progress
            </h2>

            <div className="min-w-0 overflow-x-auto">
              <PipelineProgress
                stages={[
                  {
                    id: 'detection',
                    name: 'SAR Oil-Spill Detection',
                    status: 'completed',
                  },
                  {
                    id: 'characterization',
                    name: 'Spill Characterization',
                    status: 'completed',
                  },
                  {
                    id: 'drift',
                    name: 'Backward Drift Analysis',
                    status: inv.drift_hindcast?.available
                      ? 'completed'
                      : 'pending',
                  },
                  {
                    id: 'origin',
                    name: 'Origin Estimation',
                    status: inv.origin_zone?.estimated
                      ? 'completed'
                      : 'pending',
                  },
                  {
                    id: 'ais',
                    name: 'AIS Vessel Screening',
                    status:
                      inv.ais_correlation?.status === 'unavailable'
                        ? 'unavailable'
                        : 'completed',
                  },
                ]}
              />
            </div>
          </section>

        </div>
      )}
    </InvestigationGate>
  )
}
