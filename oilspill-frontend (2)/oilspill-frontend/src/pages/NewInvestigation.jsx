import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { createInvestigation } from '../api/investigationApi.js'
import InvestigationForm from '../components/investigation/InvestigationForm.jsx'
import PipelineProgress from '../components/investigation/PipelineProgress.jsx'
import { CheckCircle2 } from 'lucide-react'

const WAITING_STAGES = [
  { id: 'sentinel_search', label: 'Sentinel-1 Search', status: 'waiting' },
  { id: 'sar_acquisition', label: 'SAR Acquisition', status: 'waiting' },
  { id: 'ai_detection', label: 'AI Detection', status: 'waiting' },
  { id: 'characterization', label: 'Characterization', status: 'waiting' },
  { id: 'geolocation', label: 'Geolocation', status: 'waiting' },
  { id: 'ocean_wind', label: 'Ocean + Wind', status: 'waiting' },
  { id: 'backward_hindcast', label: 'Backward Hindcast', status: 'waiting' },
  { id: 'origin_zone', label: 'Origin Zone', status: 'waiting' },
  { id: 'ais_correlation', label: 'AIS Correlation', status: 'waiting' },
]

export default function NewInvestigation() {
  const navigate = useNavigate()
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState(null)
  const [created, setCreated] = useState(null)

  async function handleSubmit(payload) {
    setSubmitting(true)
    setError(null)
    try {
      const { investigation_id } = await createInvestigation(payload)
      setCreated({ id: investigation_id, ...payload })
      setTimeout(() => navigate(`/investigation/${investigation_id}`), 900)
    } catch (err) {
      setError(err)
      setSubmitting(false)
    }
  }

  return (
    <div className="max-w-2xl">
      <h1 className="text-[18px] font-semibold tracking-wide text-ink-100">New Oil-Spill Investigation</h1>
      <p className="text-[13px] text-ink-500 mt-1 mb-6">Define the satellite investigation target.</p>

      {!created && (
        <div className="panel p-5">
          <InvestigationForm onSubmit={handleSubmit} submitting={submitting} />
          {error && <p className="text-[12px] text-signal-red mt-3">{error.message}</p>}
        </div>
      )}

      {created && (
        <div className="panel p-5">
          <div className="flex items-center gap-2 text-signal-green mb-4">
            <CheckCircle2 size={16} />
            <span className="text-[13px] font-semibold tracking-wide">Investigation Created</span>
          </div>
          <div className="grid grid-cols-3 gap-4 mb-6 font-mono text-[12px]">
            <div>
              <div className="data-label">ID</div>
              <div className="text-ink-100 mt-1">{created.id}</div>
            </div>
            <div>
              <div className="data-label">Location</div>
              <div className="text-ink-100 mt-1">
                {created.latitude.toFixed(4)}°, {created.longitude.toFixed(4)}°
              </div>
            </div>
            <div>
              <div className="data-label">Date</div>
              <div className="text-ink-100 mt-1">{created.observationDate}</div>
            </div>
          </div>
          <PipelineProgress stages={WAITING_STAGES} orientation="vertical" />
          <p className="text-[11px] text-ink-500 mt-2">Redirecting to investigation workspace…</p>
        </div>
      )}
    </div>
  )
}
