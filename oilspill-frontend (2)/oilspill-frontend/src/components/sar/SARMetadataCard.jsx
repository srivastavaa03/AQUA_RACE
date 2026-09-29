import React from 'react'
import MetricRow from '../common/MetricRow.jsx'

export default function SARMetadataCard({ meta }) {
  if (!meta) return null
  return (
    <div className="panel p-4">
      <h3 className="text-[12px] font-semibold tracking-wide text-ink-100 mb-2">Satellite</h3>
      <MetricRow label="Satellite" value={meta.satellite} mono={false} />
      <MetricRow label="Sensor" value={meta.sensor} mono={false} />
      <MetricRow label="Mode" value={meta.mode} mono={false} />
      <MetricRow label="Product" value={meta.product} mono={false} />
      <MetricRow label="Polarization" value={meta.polarization} mono={false} />
      <MetricRow label="Acquisition Start" value={meta.acquisition_start} />
      <MetricRow label="Acquisition End" value={meta.acquisition_end} />
      <MetricRow label="Orbit" value={meta.orbit} mono={false} />
      <MetricRow label="Mission Data Take" value={meta.mission_datatake} />
    </div>
  )
}
