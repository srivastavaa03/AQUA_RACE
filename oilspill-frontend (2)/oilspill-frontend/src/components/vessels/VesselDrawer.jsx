import React from 'react'
import { X, Ship } from 'lucide-react'
import MetricRow from '../common/MetricRow.jsx'

export default function VesselDrawer({ candidate, onClose }) {
  if (!candidate) return null

  return (
    <div className="fixed inset-y-0 right-0 w-[380px] bg-abyss-800 border-l border-border z-[500] flex flex-col shadow-2xl">
      <div className="flex items-center justify-between px-5 py-4 border-b border-border">
        <div className="flex items-center gap-2">
          <Ship size={16} className="text-cyan-accent" />
          <span className="text-[13px] font-semibold tracking-wide text-ink-100">
            AIS Candidate
          </span>
        </div>

        <button
          type="button"
          onClick={onClose}
          aria-label="Close vessel details"
          className="flex h-8 w-8 items-center justify-center border border-border text-ink-400 hover:text-ink-100 hover:bg-abyss-900 transition-colors cursor-pointer"
        >
          <X size={18} />
        </button>
      </div>

      <div className="flex-1 overflow-y-auto px-5 py-4">
        <h3 className="text-[12px] font-semibold tracking-wide text-ink-100 mb-2">
          Vessel Profile
        </h3>

        <MetricRow label="Vessel Name" value={candidate.vessel ?? 'N/A'} mono={false} />
        <MetricRow label="MMSI" value={candidate.mmsi ?? 'N/A'} />
        <MetricRow label="IMO" value={candidate.imo ?? 'N/A'} />
        <MetricRow label="Type" value={candidate.type ?? 'N/A'} mono={false} />
        <MetricRow label="Flag" value={candidate.flag ?? 'N/A'} />

        <h3 className="text-[12px] font-semibold tracking-wide text-ink-100 mt-5 mb-2">
          Spatial Relation
        </h3>

        <MetricRow
          label="Distance to Origin"
          value={
            candidate.distance_km != null
              ? `${Number(candidate.distance_km).toFixed(3)} km`
              : 'N/A'
          }
        />

        <MetricRow
          label="Closest Observation"
          value={candidate.closest_observation ?? 'N/A'}
        />

        <MetricRow
          label="Origin-Zone Relationship"
          value={candidate.origin_zone_relationship ?? 'N/A'}
          mono={false}
        />

        <h3 className="text-[12px] font-semibold tracking-wide text-ink-100 mt-5 mb-2">
          Temporal Relation
        </h3>

        <MetricRow
          label="Time Difference"
          value={
            candidate.time_diff_h != null
              ? `${Number(candidate.time_diff_h).toFixed(2)} h`
              : 'N/A'
          }
        />

        <MetricRow
          label="Presence Duration"
          value={
            candidate.presence_h != null
              ? `${Number(candidate.presence_h).toFixed(1)} h`
              : 'N/A'
          }
        />

        <h3 className="text-[12px] font-semibold tracking-wide text-ink-100 mt-5 mb-2">
          Screening
        </h3>

        <MetricRow
          label="Screening Score"
          value={
            candidate.score != null
              ? Number(candidate.score).toFixed(2)
              : 'N/A'
          }
        />

        <div className="mt-5 border border-border bg-abyss-900 px-3 py-2.5">
          <p className="text-[11px] text-ink-500 leading-relaxed">
            AIS vessel presence identifies vessels observed within the defined screening area and
            time window. It does not provide an exact individual vessel track and does not
            establish that a vessel caused the spill.
          </p>
        </div>
      </div>
    </div>
  )
}
