import React, { useMemo, useState } from 'react'
import InvestigationGate from '../components/investigation/InvestigationGate.jsx'
import StatCard from '../components/common/StatCard.jsx'
import VesselMap from '../components/vessels/VesselMap.jsx'
import VesselTable from '../components/vessels/VesselTable.jsx'
import VesselFilters from '../components/vessels/VesselFilters.jsx'
import VesselDrawer from '../components/vessels/VesselDrawer.jsx'
import EmptyState from '../components/common/EmptyState.jsx'
import { Radio, Database, Calendar, ListChecks, Ship, Fingerprint } from 'lucide-react'

export default function VesselCorrelation() {
  return (
    <InvestigationGate>
      {(inv) => <VesselCorrelationView investigation={inv} />}
    </InvestigationGate>
  )
}

function VesselCorrelationView({ investigation }) {
  const ais = investigation.ais_correlation

  const [selectedVessel, setSelectedVessel] = useState(null)

  const [filters, setFilters] = useState({
    type: 'All',
    flag: 'All',
    maxDistance: '',
    maxTimeDiff: '',
  })

  const candidates = ais?.candidates ?? []

  const { types, flags } = useMemo(() => {
    const t = new Set()
    const f = new Set()

    candidates.forEach((c) => {
      if (c.type) t.add(c.type)
      if (c.flag) f.add(c.flag)
    })

    return {
      types: [...t],
      flags: [...f],
    }
  }, [candidates])

  const filtered = useMemo(() => {
    return candidates.filter((c) => {
      if (filters.type !== 'All' && c.type !== filters.type) return false
      if (filters.flag !== 'All' && c.flag !== filters.flag) return false

      if (
        filters.maxDistance &&
        (c.distance_km == null ||
          c.distance_km > parseFloat(filters.maxDistance))
      ) {
        return false
      }

      if (
        filters.maxTimeDiff &&
        (c.time_diff_h == null ||
          c.time_diff_h > parseFloat(filters.maxTimeDiff))
      ) {
        return false
      }

      return true
    })
  }, [candidates, filters])

  const dateRange = ais?.date_range ?? ais?.time_window ?? {}

  if (!ais || ais.status === 'unavailable') {
    return (
      <div className="flex flex-col gap-6">
        <div>
          <h1 className="text-[16px] font-semibold tracking-wide text-ink-100">
            Vessel Correlation
          </h1>

          <p className="text-[12px] text-ink-500 mt-1">
            AIS-based vessel presence screening around the estimated origin zone.
          </p>
        </div>

        <EmptyState
          title="AIS DATA UNAVAILABLE"
          description={
            ais?.message ||
            'AIS data is currently unavailable. No vessel attribution was performed.'
          }
        />

        <div className="border border-border bg-abyss-800 px-4 py-3">
          <p className="text-[11px] text-ink-500 leading-relaxed">
            AIS vessel presence is intended for screening candidate vessels only.
            It does not establish that a vessel caused the spill.
          </p>
        </div>
      </div>
    )
  }

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-[16px] font-semibold tracking-wide text-ink-100">
          Vessel Correlation
        </h1>

        <p className="text-[12px] text-ink-500 mt-1">
          AIS-based vessel presence screening around the estimated origin zone.
        </p>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
        <StatCard
          label="AIS Source"
          value={ais.source ?? 'N/A'}
          mono={false}
          icon={Radio}
        />

        <StatCard
          label="Dataset"
          value={ais.dataset ?? 'N/A'}
          mono={false}
          icon={Database}
        />

        <StatCard
          label="Date Range"
          value={
            dateRange.start && dateRange.end
              ? `${dateRange.start} ? ${dateRange.end}`
              : 'N/A'
          }
          icon={Calendar}
        />

        <StatCard
          label="Presence Records"
          value={ais.presence_records ?? 0}
          icon={ListChecks}
        />

        <StatCard
          label="Unique Vessels"
          value={ais.unique_vessels ?? 0}
          icon={Ship}
        />

        <StatCard
          label="Screening Candidates"
          value={ais.screening_candidates ?? candidates.length}
          icon={Fingerprint}
        />
      </div>

      {candidates.length === 0 ? (
        <EmptyState
          title="NO AIS VESSEL-PRESENCE RECORDS"
          description="No vessel candidates were returned for the defined screening area and time window."
        />
      ) : (
        <div className="grid grid-cols-1 xl:grid-cols-[1fr_480px] gap-4">
          <VesselMap investigation={investigation} />

          <div className="panel p-4">
            <VesselFilters
              filters={filters}
              setFilters={setFilters}
              types={types}
              flags={flags}
            />

            <VesselTable
              candidates={filtered}
              onSelect={(candidate) => setSelectedVessel(candidate)}
              selectedMmsi={selectedVessel?.mmsi ?? null}
            />
          </div>
        </div>
      )}

      <div className="border border-border bg-abyss-800 px-4 py-3">
        <p className="text-[11px] text-ink-500 leading-relaxed">
          AIS vessel presence identifies vessels observed within the defined
          screening area and time window. It does not provide an exact
          individual vessel track and does not establish that a vessel caused
          the spill.
        </p>
      </div>

      {selectedVessel && (
        <VesselDrawer
          candidate={selectedVessel}
          onClose={() => setSelectedVessel(null)}
        />
      )}
    </div>
  )
}
