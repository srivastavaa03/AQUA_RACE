import React, { useEffect, useState } from 'react'
import MetricRow from '../components/common/MetricRow.jsx'
import { BASE_URL, checkApiHealth } from '../api/investigationApi.js'

const FRONTEND_VERSION = '1.0.0'

export default function Settings() {
  const [online, setOnline] = useState(null)

  useEffect(() => {
    checkApiHealth().then(setOnline)
  }, [])

  return (
    <div className="max-w-2xl flex flex-col gap-6">
      <div>
        <h1 className="text-[16px] font-semibold tracking-wide text-ink-100">Settings</h1>
        <p className="text-[12px] text-ink-500 mt-1">System information and data sources.</p>
      </div>

      <div className="panel p-5">
        <h2 className="text-[12px] font-semibold tracking-wide text-ink-100 mb-2">System</h2>
        <MetricRow label="Frontend Version" value={FRONTEND_VERSION} />
        <MetricRow label="API Endpoint" value={BASE_URL} />
        <MetricRow label="Mode" value={'LIVE'} mono={false} />
        <MetricRow label="Model Status" value={online === null ? 'Checking…' : online ? 'ONLINE' : 'OFFLINE'} mono={false} />
      </div>

      <div className="panel p-5">
        <h2 className="text-[12px] font-semibold tracking-wide text-ink-100 mb-2">Map &amp; Data Sources</h2>
        <MetricRow label="Map Provider" value="OpenStreetMap" mono={false} />
        <MetricRow label="Satellite Data" value="Sentinel-1 SAR (Copernicus)" mono={false} />
        <MetricRow label="AIS Data" value="Global Fishing Watch — Public Global Presence" mono={false} />
        <MetricRow label="Ocean / Wind Data" value="Model reanalysis (source configured server-side)" mono={false} />
      </div>

      <p className="text-[11px] text-ink-700">
        API credentials and third-party access tokens are managed server-side and are never exposed to the frontend.
      </p>
    </div>
  )
}
