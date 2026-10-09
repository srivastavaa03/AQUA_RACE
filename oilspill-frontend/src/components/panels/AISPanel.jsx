import { Ship } from 'lucide-react'
import Panel, { Unavailable } from './Panel'

export default function AISPanel({ candidates, available }) {
  return (
    <Panel
      icon={Ship}
      title="AIS vessel candidates"
      eyebrow="Global Fishing Watch vessel-presence, origin zone"
      right={
        available ? (
          <span className="rounded-full border border-deck-500 bg-hull-900 px-2 py-0.5 text-[10.5px] text-mist-500">
            {candidates.length} candidate{candidates.length === 1 ? '' : 's'}
          </span>
        ) : null
      }
    >
      {!available ? (
        <Unavailable label="AIS correlation data not returned by the backend yet." />
      ) : candidates.length === 0 ? (
        <p className="py-4 text-center text-[12px] text-mist-500">
          No AIS vessel-presence records returned for this origin zone and date range.
        </p>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full text-[12px]">
            <thead>
              <tr className="border-b border-deck-600 text-left text-[10.5px] uppercase tracking-wide text-mist-500">
                <th className="pb-2 pr-3 font-medium">Candidate</th>
                <th className="pb-2 pr-3 font-medium">MMSI</th>
                <th className="pb-2 pr-3 font-medium">Type</th>
                <th className="pb-2 pr-3 font-medium">Distance</th>
                <th className="pb-2 pr-3 font-medium">Last presence</th>
                <th className="pb-2 font-medium">Confidence</th>
              </tr>
            </thead>
            <tbody>
              {candidates.map((c) => (
                <tr key={c.candidateId} className="border-b border-deck-700 last:border-0">
                  <td className="py-2 pr-3 font-mono text-mist-300">{c.candidateId}</td>
                  <td className="py-2 pr-3 font-mono text-mist-500">
                    {c.mmsiMasked ?? <span className="italic text-mist-700">unavailable</span>}
                  </td>
                  <td className="py-2 pr-3 text-mist-100">
                    {c.vesselType ?? <span className="italic text-mist-700">unavailable</span>}
                  </td>
                  <td className="py-2 pr-3 font-mono text-mist-100">
                    {c.distanceFromOriginKm !== undefined ? `${c.distanceFromOriginKm.toFixed(1)} km` : (
                      <span className="italic text-mist-700">unavailable</span>
                    )}
                  </td>
                  <td className="py-2 pr-3 font-mono text-mist-500">
                    {c.lastPresence ? new Date(c.lastPresence).toISOString().slice(0, 16).replace('T', ' ') : (
                      <span className="italic text-mist-700">unavailable</span>
                    )}
                  </td>
                  <td className="py-2">
                    {c.confidence !== undefined ? (
                      <ConfidenceBar value={c.confidence} />
                    ) : (
                      <span className="italic text-mist-700">unavailable</span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
      <p className="mt-3 text-[10.5px] text-mist-700">
        Candidates are unconfirmed and masked pending manual verification. This table reflects vessel-presence
        correlation only, not a determination of responsibility.
      </p>
    </Panel>
  )
}

function ConfidenceBar({ value }) {
  const pct = Math.round(value * 100)
  const tone = pct >= 50 ? 'bg-hazard-500' : pct >= 25 ? 'bg-flare-500' : 'bg-mist-700'
  return (
    <div className="flex items-center gap-2">
      <div className="h-1.5 w-16 overflow-hidden rounded-full bg-hull-900">
        <div className={`h-full ${tone}`} style={{ width: `${pct}%` }} />
      </div>
      <span className="font-mono text-[11px] text-mist-500">{pct}%</span>
    </div>
  )
}
