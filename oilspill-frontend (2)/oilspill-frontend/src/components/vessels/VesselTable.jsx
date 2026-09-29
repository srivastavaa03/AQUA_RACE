import React from 'react'
import DataTable from '../common/DataTable.jsx'

export default function VesselTable({ candidates, onSelect, selectedMmsi }) {
  const columns = [
    { key: 'rank', label: 'Rank', mono: true },
    {
      key: 'vessel',
      label: 'Vessel',
      mono: false,
      render: (r) => r.vessel ?? r.ship_name ?? 'Unknown',
    },
    {
      key: 'mmsi',
      label: 'MMSI',
      mono: true,
      render: (r) => r.mmsi ?? 'N/A',
    },
    {
      key: 'imo',
      label: 'IMO',
      mono: true,
      render: (r) => r.imo ?? 'N/A',
    },
    {
      key: 'type',
      label: 'Type',
      mono: false,
      render: (r) => r.type ?? r.vessel_type ?? 'N/A',
    },
    {
      key: 'flag',
      label: 'Flag',
      mono: true,
      render: (r) => r.flag ?? 'N/A',
    },
    {
      key: 'distance_km',
      label: 'Distance (km)',
      mono: true,
      render: (r) =>
        r.distance_km != null
          ? r.distance_km.toFixed(1)
          : r.distance_to_hindcast_km != null
            ? r.distance_to_hindcast_km.toFixed(1)
            : 'N/A',
    },
    {
      key: 'time_diff_h',
      label: 'Time Diff (h)',
      mono: true,
      render: (r) =>
        r.time_diff_h != null
          ? r.time_diff_h.toFixed(1)
          : r.time_difference_hours != null
            ? r.time_difference_hours.toFixed(1)
            : 'N/A',
    },
    {
      key: 'presence_h',
      label: 'Presence (h)',
      mono: true,
      render: (r) =>
        r.presence_h != null
          ? r.presence_h.toFixed(1)
          : r.gfw_presence_hours != null
            ? r.gfw_presence_hours.toFixed(1)
            : 'N/A',
    },
    {
      key: 'score',
      label: 'Score',
      mono: true,
      render: (r) => {
        const score =
          r.score != null
            ? r.score
            : r.screening_score != null
              ? r.screening_score / 100
              : null

        if (score == null) return 'N/A'

        return (
          <span
            className={
              score >= 0.7
                ? 'text-signal-amber'
                : score >= 0.45
                  ? 'text-ink-100'
                  : 'text-ink-500'
            }
          >
            {score.toFixed(2)}
          </span>
        )
      },
    },
  ]

  return (
    <DataTable
      columns={columns}
      rows={candidates}
      rowKey={(r) => r.mmsi ?? r.vessel_id ?? 'unknown'}
      onRowClick={onSelect}
      selectedKey={selectedMmsi}
    />
  )
}
