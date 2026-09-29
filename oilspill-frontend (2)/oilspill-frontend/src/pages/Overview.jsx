import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { createInvestigation } from '../api/investigationApi.js'
import InvestigationForm from '../components/investigation/InvestigationForm.jsx'
import LoadingState from '../components/common/LoadingState.jsx'
import ErrorState from '../components/common/ErrorState.jsx'

export default function Overview() {
  const navigate = useNavigate()
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState(null)

  async function handleSubmit(payload) {
    setSubmitting(true)
    setError(null)

    try {
      const { investigation_id } = await createInvestigation(payload)
      navigate(`/investigation/${investigation_id}`)
    } catch (err) {
      setError(err)
      setSubmitting(false)
    }
  }

  return (
    <div className="flex flex-col gap-6">
      <section className="panel p-5">
        <h2 className="text-[13px] font-semibold tracking-wide text-ink-100 mb-1">
          New Investigation
        </h2>

        <p className="text-[12px] text-ink-500 mb-4">
          Define a target location and observation date to begin analysis.
        </p>

        <InvestigationForm
          onSubmit={handleSubmit}
          submitting={submitting}
          compact
        />

        {error && (
          <p className="text-[12px] text-signal-red mt-3">
            {error.message}
          </p>
        )}
      </section>

      <section className="panel p-5">
        <h2 className="text-[13px] font-semibold tracking-wide text-ink-100 mb-2">
          Investigation Workflow
        </h2>

        <p className="text-[12px] text-ink-500">
          Submit a target location and observation date to run SAR-based
          oil-spill detection, spill characterization, backward drift
          analysis, origin estimation, and AIS screening.
        </p>
      </section>
    </div>
  )
}
