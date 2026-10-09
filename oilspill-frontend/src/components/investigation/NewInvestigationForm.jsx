import { useState } from 'react'
import { Crosshair, Loader2 } from 'lucide-react'

export default function NewInvestigationForm({ onStart, isStarting }) {
  const [lat, setLat] = useState('28.5875')
  const [lon, setLon] = useState('48.5678')
  const [date, setDate] = useState('2020-08-10')
  const [error, setError] = useState('')

  function handleSubmit(e) {
    e.preventDefault()
    const latNum = Number(lat)
    const lonNum = Number(lon)

    if (Number.isNaN(latNum) || latNum < -90 || latNum > 90) {
      setError('Latitude must be between -90 and 90')
      return
    }
    if (Number.isNaN(lonNum) || lonNum < -180 || lonNum > 180) {
      setError('Longitude must be between -180 and 180')
      return
    }
    if (!date) {
      setError('Select a scene date')
      return
    }
    setError('')
    onStart({ lat: latNum, lon: lonNum, date })
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-3">
      <div className="grid grid-cols-2 gap-2">
        <Field label="Latitude">
          <input
            value={lat}
            onChange={(e) => setLat(e.target.value)}
            inputMode="decimal"
            className="input"
            placeholder="28.5875"
          />
        </Field>
        <Field label="Longitude">
          <input
            value={lon}
            onChange={(e) => setLon(e.target.value)}
            inputMode="decimal"
            className="input"
            placeholder="48.5678"
          />
        </Field>
      </div>

      <Field label="Scene date">
        <input
          type="date"
          value={date}
          onChange={(e) => setDate(e.target.value)}
          className="input"
        />
      </Field>

      {error && <p className="text-[11px] text-hazard-400">{error}</p>}

      <button
        type="submit"
        disabled={isStarting}
        className="flex w-full items-center justify-center gap-2 rounded-sm bg-sonar-600 py-2 text-[13px] font-medium text-hull-950 transition-colors hover:bg-sonar-500 disabled:cursor-not-allowed disabled:opacity-60"
      >
        {isStarting ? (
          <>
            <Loader2 size={14} className="animate-spin" /> Analyzing…
          </>
        ) : (
          <>
            <Crosshair size={14} /> Analyze Location
          </>
        )}
      </button>
    </form>
  )
}

function Field({ label, children }) {
  return (
    <label className="block">
      <span className="mb-1 block text-[11px] text-mist-500">{label}</span>
      {children}
    </label>
  )
}
