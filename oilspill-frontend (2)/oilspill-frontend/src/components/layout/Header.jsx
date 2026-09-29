import React, { useEffect, useState } from 'react'
import { checkApiHealth } from '../../api/investigationApi.js'
import { useInvestigationSafe } from '../../context/InvestigationContext.jsx'

export default function Header() {
  const ctx = useInvestigationSafe()
  const [online, setOnline] = useState(true)

  useEffect(() => {
    let mounted = true
    checkApiHealth().then((ok) => mounted && setOnline(ok))
    return () => {
      mounted = false
    }
  }, [])

  const inv = ctx?.investigation

  return (
    <header className="h-16 shrink-0 border-b border-border bg-abyss-900 flex items-center justify-between px-6">
      <div>
        <h1 className="text-[15px] font-semibold tracking-wide text-ink-100">OIL SPILL INVESTIGATION</h1>
        <p className="text-[10px] tracking-wider2 text-ink-500 mt-0.5">
          SAR &bull; OCEANOGRAPHIC &bull; AIS INTELLIGENCE
        </p>
      </div>

      <div className="flex items-center gap-6 font-mono text-[12px]">
        <div className="text-right">
          <div className="data-label">Investigation</div>
          <div className="text-ink-100">{inv ? inv.investigation_id : 'N/A'}</div>
        </div>
        <div className="text-right">
          <div className="data-label">Date</div>
          <div className="text-ink-100">{inv ? inv.target.observation_date : 'N/A'}</div>
        </div>
        <div className="flex items-center gap-2">
          <span
            className={[
              'inline-block w-1.5 h-1.5 rounded-full',
              online ? 'bg-signal-green' : 'bg-signal-red',
            ].join(' ')}
          />
          <span className={online ? 'text-signal-green' : 'text-signal-red'}>
            {online ? 'OPERATIONAL' : 'OFFLINE'}
          </span>
        </div>
      </div>
    </header>
  )
}
