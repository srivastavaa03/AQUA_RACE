import React, { useState } from 'react'
import { Loader2, Navigation } from 'lucide-react'

export default function InvestigationForm({ onSubmit, submitting, compact = false }) {
  const [latitude, setLatitude] = useState('')
  const [longitude, setLongitude] = useState('')
  const [observationDate, setObservationDate] = useState('')
  const [name, setName] = useState('')
  const [validationError, setValidationError] = useState(null)

  function handleSubmit(e) {
    e.preventDefault()
    const lat = parseFloat(latitude)
    const lon = parseFloat(longitude)

    if (Number.isNaN(lat) || lat < -90 || lat > 90) {
      setValidationError('Latitude must be a number between -90 and 90.')
      return
    }
    if (Number.isNaN(lon) || lon < -180 || lon > 180) {
      setValidationError('Longitude must be a number between -180 and 180.')
      return
    }
    if (!observationDate) {
      setValidationError('Observation date is required.')
      return
    }
    setValidationError(null)
    onSubmit({ latitude: lat, longitude: lon, observationDate, name: name || null })
  }

  return (
    <form onSubmit={handleSubmit} className="flex flex-col gap-4">
      <div className={compact ? 'grid grid-cols-3 gap-3' : 'grid grid-cols-1 sm:grid-cols-3 gap-4'}>
        <Field label="Latitude">
          <input
            type="number"
            step="any"
            required
            placeholder="19.0761"
            value={latitude}
            onChange={(e) => setLatitude(e.target.value)}
            className="input-field"
          />
        </Field>
        <Field label="Longitude">
          <input
            type="number"
            step="any"
            required
            placeholder="72.8321"
            value={longitude}
            onChange={(e) => setLongitude(e.target.value)}
            className="input-field"
          />
        </Field>
        <Field label="Observation Date">
          <input
            type="date"
            required
            value={observationDate}
            onChange={(e) => setObservationDate(e.target.value)}
            className="input-field"
          />
        </Field>
      </div>

      {!compact && (
        <Field label="Investigation Name / Reference (optional)">
          <input
            type="text"
            placeholder="e.g. Mumbai Coast — June Sighting"
            value={name}
            onChange={(e) => setName(e.target.value)}
            className="input-field"
          />
        </Field>
      )}

      {validationError && <p className="text-[12px] text-signal-red">{validationError}</p>}

      <button
        type="submit"
        disabled={submitting}
        className="self-start flex items-center gap-2 px-5 py-2.5 bg-cyan-accent text-abyss-950 text-[12px] font-semibold uppercase tracking-wider2 hover:brightness-110 disabled:opacity-50 disabled:cursor-not-allowed transition"
      >
        {submitting ? <Loader2 size={14} className="animate-spin" /> : <Navigation size={14} />}
        {compact ? 'Analyze Location' : 'Start Investigation'}
      </button>
    </form>
  )
}

function Field({ label, children }) {
  return (
    <label className="flex flex-col gap-1.5">
      <span className="data-label">{label}</span>
      {children}
    </label>
  )
}
