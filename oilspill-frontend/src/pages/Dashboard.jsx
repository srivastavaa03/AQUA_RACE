import { useEffect, useRef, useState, useCallback } from 'react'
import { LayoutGrid, Ship, Navigation, History, AlertTriangle, RotateCw } from 'lucide-react'
import Sidebar from '../components/layout/Sidebar'
import Header from '../components/layout/Header'
import StatusTracker from '../components/investigation/StatusTracker'
import DetectionPanel from '../components/panels/DetectionPanel'
import MetadataPanel from '../components/panels/MetadataPanel'
import CharacterizationPanel from '../components/panels/CharacterizationPanel'
import EnvironmentalPanel from '../components/panels/EnvironmentalPanel'
import DriftPanel from '../components/panels/DriftPanel'
import OriginZonePanel from '../components/panels/OriginZonePanel'
import AISPanel from '../components/panels/AISPanel'
import InvestigationMap from '../components/map/InvestigationMap'
import EvidenceTimeline from '../components/timeline/EvidenceTimeline'
import {
  listInvestigations,
  startInvestigation,
  getInvestigation,
  getInvestigationStatus,
  ApiError,
} from '../api/investigationApi'

const TABS = [
  { key: 'overview', label: 'Overview', icon: LayoutGrid },
  { key: 'drift', label: 'Drift & origin', icon: Navigation },
  { key: 'ais', label: 'AIS candidates', icon: Ship },
  { key: 'timeline', label: 'Timeline', icon: History },
]

const POLL_INTERVAL_MS = 3000

export default function Dashboard() {
  const [investigations, setInvestigations] = useState([])
  const [selectedId, setSelectedId] = useState(null)
  const [status, setStatus] = useState(null)
  const [result, setResult] = useState(null)
  const [tab, setTab] = useState('overview')
  const [isStarting, setIsStarting] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState(null)

  const pollTimeoutRef = useRef(null)
  const pollTokenRef = useRef(0)

  useEffect(() => {
    listInvestigations().then((list) => {
      setInvestigations(list)
      if (list.length > 0) setSelectedId(list[0].id)
    })
  }, [])

  const stopPolling = useCallback(() => {
    pollTokenRef.current += 1
    if (pollTimeoutRef.current) {
      clearTimeout(pollTimeoutRef.current)
      pollTimeoutRef.current = null
    }
  }, [])

  // Polls /status until the backend reports complete or error, then loads
  // the full result. Runs immediately on selection, and again on every
  // "Start investigation" call.
  const pollUntilDone = useCallback((id) => {
    stopPolling()
    const myToken = pollTokenRef.current

    async function tick() {
      if (pollTokenRef.current !== myToken) return
      try {
        const statusRes = await getInvestigationStatus(id)
        if (pollTokenRef.current !== myToken) return
        setStatus(statusRes)
        setError(null)

        if (statusRes.status === 'complete') {
          const resultRes = await getInvestigation(id)
          if (pollTokenRef.current !== myToken) return
          setResult(resultRes)
          setIsLoading(false)
          return
        }
        if (statusRes.status === 'error') {
          setIsLoading(false)
          setError(statusRes.error ?? 'The backend reported an error processing this investigation.')
          return
        }
        setIsLoading(false)
        pollTimeoutRef.current = setTimeout(tick, POLL_INTERVAL_MS)
      } catch (err) {
        if (pollTokenRef.current !== myToken) return
        setIsLoading(false)
        setError(err instanceof ApiError ? err.message : 'Something went wrong talking to the backend.')
      }
    }

    tick()
  }, [stopPolling])

  useEffect(() => {
    if (!selectedId) return
    setResult(null)
    setStatus(null)
    setError(null)
    setIsLoading(true)
    pollUntilDone(selectedId)
    return stopPolling
  }, [selectedId, pollUntilDone, stopPolling])

  async function handleStart({ lat, lon, date }) {
    setIsStarting(true)
    setError(null)
    try {
      const { id } = await startInvestigation({ lat, lon, date })
      const list = await listInvestigations()
      setInvestigations(list)
      setTab('overview')
      if (id === selectedId) {
        // Re-trigger polling for the same id (rare, but keeps state fresh)
        setResult(null)
        setStatus(null)
        setIsLoading(true)
        pollUntilDone(id)
      } else {
        setSelectedId(id)
      }
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Could not start the investigation.')
    } finally {
      setIsStarting(false)
    }
  }

  function handleRetry() {
    if (selectedId) {
      setIsLoading(true)
      setError(null)
      pollUntilDone(selectedId)
    }
  }

  return (
    <div className="flex h-screen flex-col bg-hull-950">
      <Header />
      <div className="flex min-h-0 flex-1">
        <Sidebar
          investigations={investigations}
          selectedId={selectedId}
          onSelect={setSelectedId}
          onStart={handleStart}
          isStarting={isStarting}
        />

        <main className="min-w-0 flex-1 overflow-y-auto bg-[radial-gradient(ellipse_at_top,rgba(45,212,191,0.05),transparent_60%)] p-5">
          {error ? (
            <ErrorState message={error} onRetry={handleRetry} />
          ) : !selectedId ? (
            <EmptyState message="Enter a location and date, then Analyze Location to begin." />
          ) : !result ? (
            <div className="mx-auto max-w-[1400px] space-y-4">
              <StatusTracker status={status?.status ?? 'queued'} currentStage={status?.stage} />
              <EmptyState
                message={
                  isLoading
                    ? 'Contacting backend…'
                    : status?.stageLabel
                    ? `${status.stageLabel}…`
                    : 'Processing…'
                }
                loading
              />
            </div>
          ) : (
            <div className="mx-auto max-w-[1400px] space-y-4">
              <StatusTracker status={status?.status} currentStage={status?.stage} />

              <nav className="flex gap-1 border-b border-deck-600">
                {TABS.map((t) => {
                  const Icon = t.icon
                  const active = tab === t.key
                  return (
                    <button
                      key={t.key}
                      onClick={() => setTab(t.key)}
                      className={`flex items-center gap-1.5 border-b-2 px-3 py-2 text-[12.5px] transition-colors ${
                        active
                          ? 'border-sonar-500 text-mist-100'
                          : 'border-transparent text-mist-500 hover:text-mist-300'
                      }`}
                    >
                      <Icon size={13} />
                      {t.label}
                    </button>
                  )
                })}
              </nav>

              {tab === 'overview' && (
                <div className="grid grid-cols-1 gap-4 xl:grid-cols-[1.1fr_1fr]">
                  <div className="space-y-4">
                    <DetectionPanel detection={result.detection} />
                    <CharacterizationPanel characterization={result.characterization} />
                    <MetadataPanel metadata={result.sentinelMetadata} />
                  </div>
                  <InvestigationMap result={result} />
                </div>
              )}

              {tab === 'drift' && (
                <div className="grid grid-cols-1 gap-4 xl:grid-cols-[1fr_1fr]">
                  <div className="space-y-4">
                    <EnvironmentalPanel environmental={result.environmental} />
                    <DriftPanel hindcast={result.hindcast} />
                    <OriginZonePanel originZone={result.originZone} />
                  </div>
                  <InvestigationMap result={result} />
                </div>
              )}

              {tab === 'ais' && (
                <div className="grid grid-cols-1 gap-4 xl:grid-cols-[1fr_1fr]">
                  <AISPanel candidates={result.aisCandidates} available={result.aisAvailable} />
                  <InvestigationMap result={result} />
                </div>
              )}

              {tab === 'timeline' && (
                <div className="max-w-2xl">
                  <EvidenceTimeline timeline={result.timeline} />
                </div>
              )}
            </div>
          )}
        </main>
      </div>
    </div>
  )
}

function EmptyState({ message, loading }) {
  return (
    <div className="flex h-full min-h-[300px] items-center justify-center">
      <div className="flex items-center gap-2 text-center">
        {loading && <RotateCw size={13} className="animate-spin text-mist-500" />}
        <p className="font-mono text-[12px] text-mist-500">{message}</p>
      </div>
    </div>
  )
}

function ErrorState({ message, onRetry }) {
  return (
    <div className="flex h-full min-h-[300px] items-center justify-center">
      <div className="max-w-md rounded-md border border-hazard-500/30 bg-hazard-500/5 p-5 text-center">
        <AlertTriangle size={20} className="mx-auto mb-2 text-hazard-400" />
        <p className="mb-3 text-[13px] text-mist-100">{message}</p>
        <button
          onClick={onRetry}
          className="inline-flex items-center gap-1.5 rounded-sm border border-deck-500 bg-deck-700 px-3 py-1.5 text-[12px] text-mist-100 hover:bg-deck-600"
        >
          <RotateCw size={12} /> Retry
        </button>
      </div>
    </div>
  )
}
