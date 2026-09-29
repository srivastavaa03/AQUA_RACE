import React, { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { getInvestigationHistory } from '../api/investigationApi.js'
import { History as HistoryIcon, RefreshCw } from 'lucide-react'

export default function History() {
  const navigate = useNavigate()
  const [items, setItems] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  async function loadHistory() {
    setLoading(true)
    setError(null)

    try {
      const data = await getInvestigationHistory()
      setItems(data)
    } catch (err) {
      setError(err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadHistory()
  }, [])

  return (
    <div className="flex flex-col gap-6">
      <section className="flex items-center justify-between">
        <div>
          <h1 className="text-[18px] font-semibold tracking-wide text-ink-100">
            Investigation History
          </h1>
          <p className="text-[13px] text-ink-500 mt-1">
            Previous oil-spill investigations and their current status.
          </p>
        </div>

        <button
          onClick={loadHistory}
          className="flex items-center gap-2 px-3 py-2 border border-border text-[12px] text-ink-400 hover:text-ink-100 hover:bg-abyss-700/40 transition-colors"
        >
          <RefreshCw size={14} />
          Refresh
        </button>
      </section>

      {loading && (
        <div className="panel p-6 text-[12px] text-ink-500">
          Loading investigation history...
        </div>
      )}

      {error && (
        <div className="panel p-6 text-[12px] text-signal-red">
          {error.message}
        </div>
      )}

      {!loading && !error && items.length === 0 && (
        <div className="panel p-10 text-center">
          <HistoryIcon
            size={28}
            className="mx-auto mb-3 text-ink-600"
          />
          <div className="text-[13px] text-ink-300">
            No investigations yet
          </div>
          <div className="text-[11px] text-ink-600 mt-1">
            Start a new investigation to create a history record.
          </div>
        </div>
      )}

      {!loading && !error && items.length > 0 && (
        <div className="panel overflow-hidden">
          <div className="grid grid-cols-[1.4fr_1fr_1fr_1fr_auto] gap-4 px-5 py-3 border-b border-border data-label">
            <div>Investigation</div>
            <div>Location</div>
            <div>Date</div>
            <div>Status</div>
            <div></div>
          </div>

          {items
            .slice()
            .reverse()
            .map((item) => (
              <div
                key={item.id}
                className="grid grid-cols-[1.4fr_1fr_1fr_1fr_auto] gap-4 items-center px-5 py-4 border-b border-border last:border-b-0"
              >
                <div className="font-mono text-[11px] text-ink-300 truncate">
                  {item.id}
                </div>

                <div className="font-mono text-[11px] text-ink-400">
                  {Number(item.latitude).toFixed(4)},
                  {' '}
                  {Number(item.longitude).toFixed(4)}
                </div>

                <div className="font-mono text-[11px] text-ink-400">
                  {item.date}
                </div>

                <div>
                  <span
                    className={[
                      'text-[10px] font-mono uppercase tracking-wide',
                      item.status === 'completed'
                        ? 'text-signal-green'
                        : item.status === 'failed'
                          ? 'text-signal-red'
                          : 'text-cyan-accent',
                    ].join(' ')}
                  >
                    {item.status}
                  </span>
                </div>

                <button
                  onClick={() =>
                    navigate(`/investigation/${item.id}`)
                  }
                  className="px-3 py-1.5 border border-border text-[10px] tracking-wide text-ink-400 hover:text-ink-100 hover:border-cyan-accent transition-colors"
                >
                  OPEN
                </button>
              </div>
            ))}
        </div>
      )}
    </div>
  )
}