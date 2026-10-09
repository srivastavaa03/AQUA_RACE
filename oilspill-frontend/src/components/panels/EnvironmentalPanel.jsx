import { Wind } from 'lucide-react'
import { ResponsiveContainer, AreaChart, Area, XAxis, YAxis, Tooltip, CartesianGrid } from 'recharts'
import Panel, { Stat, Unavailable } from './Panel'

export default function EnvironmentalPanel({ environmental }) {
  if (!environmental) {
    return (
      <Panel icon={Wind} title="Ocean current & wind" eyebrow="Copernicus Marine + ERA5 reanalysis">
        <Unavailable label="Ocean current and wind data not returned by the backend yet." />
      </Panel>
    )
  }

  const { current, wind } = environmental

  return (
    <Panel icon={Wind} title="Ocean current & wind" eyebrow="Copernicus Marine + ERA5 reanalysis">
      <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
        <Stat label="Current u₀ (E-W)" value={current.uo !== undefined ? Number(current.uo).toFixed(4) : undefined} unit="m/s" />
        <Stat label="Current v₀ (N-S)" value={current.vo !== undefined ? Number(current.vo).toFixed(4) : undefined} unit="m/s" />
        <Stat label="Wind grid" value={wind.gridSize} />
        <Stat
          label="Current grid"
          value={
            current.gridLat !== undefined && current.gridLon !== undefined
              ? `${current.gridLat.toFixed(3)}, ${current.gridLon.toFixed(3)}`
              : undefined
          }
        />
      </div>

      <div className="mt-4 grid grid-cols-1 gap-4 border-t border-deck-600 pt-4 md:grid-cols-2">
        {current.series ? (
          <MiniChart title="Current speed" data={current.series} color="#2DD4BF" unit="m/s" />
        ) : (
          <div>
            <p className="mb-1.5 text-[11px] text-mist-500">Current speed</p>
            <Unavailable label="Time-series data unavailable." />
          </div>
        )}
        {wind.series ? (
          <MiniChart title="Wind speed" data={wind.series} color="#F5A524" unit="m/s" />
        ) : (
          <div>
            <p className="mb-1.5 text-[11px] text-mist-500">Wind speed</p>
            <Unavailable label="Time-series data unavailable." />
          </div>
        )}
      </div>
    </Panel>
  )
}

function MiniChart({ title, data, color, unit }) {
  const gradId = `grad-${title.replace(/[^a-zA-Z0-9]/g, '')}`
  return (
    <div>
      <p className="mb-1.5 text-[11px] text-mist-500">{title}</p>
      <div className="h-28">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={data} margin={{ top: 4, right: 4, left: -20, bottom: 0 }}>
            <defs>
              <linearGradient id={gradId} x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor={color} stopOpacity={0.35} />
                <stop offset="95%" stopColor={color} stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid stroke="#182633" vertical={false} />
            <XAxis dataKey="t" tick={{ fontSize: 10, fill: '#7A8FA3' }} axisLine={false} tickLine={false} hide />
            <YAxis tick={{ fontSize: 10, fill: '#7A8FA3' }} axisLine={false} tickLine={false} width={30} />
            <Tooltip
              contentStyle={{ background: '#152029', border: '1px solid #25384A', fontSize: 11, borderRadius: 4 }}
              labelStyle={{ color: '#AEBECC' }}
              formatter={(value) => [`${value} ${unit}`, '']}
            />
            <Area type="monotone" dataKey="value" stroke={color} fill={`url(#${gradId})`} strokeWidth={1.75} />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}
