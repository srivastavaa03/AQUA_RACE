import React from 'react'
import { useInvestigation } from '../../context/InvestigationContext.jsx'
import LoadingState from '../common/LoadingState.jsx'
import ErrorState from '../common/ErrorState.jsx'
import EmptyState from '../common/EmptyState.jsx'

const ERROR_TITLES = {
  offline: 'No connection to investigation API.',
  timeout: 'Investigation API request timed out.',
  not_found: 'Investigation not found.',
  server: 'Investigation API returned an error.',
}

/**
 * Shared loading/error/running gate used by every investigation-scoped page.
 * Renders children(investigation) once data is ready and the pipeline has run.
 */
export default function InvestigationGate({ children }) {
  const { investigation, loading, error, reload } = useInvestigation()

  if (loading) return <LoadingState message="Loading investigation data." />

  if (error) {
    return <ErrorState title={ERROR_TITLES[error.kind] || 'Investigation pipeline failed.'} onRetry={reload} />
  }

  if (!investigation) {
    return <EmptyState title="Investigation pipeline failed." description="No investigation data is available." />
  }

  if (investigation.status === 'running' || investigation.status === 'waiting') {
    return (
      <div className="flex flex-col gap-6">
        <EmptyState title="Investigation in progress." description="Pipeline stages are still executing. This view will populate as results become available." />
      </div>
    )
  }

  if (investigation.status === 'failed') {
    return <ErrorState title="Investigation pipeline failed." onRetry={reload} />
  }

  return children(investigation)
}
