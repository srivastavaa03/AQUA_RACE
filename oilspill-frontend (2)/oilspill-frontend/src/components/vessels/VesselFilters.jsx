import React from 'react'

export default function VesselFilters({ filters, setFilters, types, flags }) {
  return (
    <div className="flex flex-wrap gap-3 items-end mb-3">
      <FilterSelect
        label="Vessel Type"
        value={filters.type}
        onChange={(v) => setFilters((f) => ({ ...f, type: v }))}
        options={['All', ...types]}
      />
      <FilterSelect
        label="Flag"
        value={filters.flag}
        onChange={(v) => setFilters((f) => ({ ...f, flag: v }))}
        options={['All', ...flags]}
      />
      <label className="flex flex-col gap-1.5">
        <span className="data-label">Max Distance (km)</span>
        <input
          type="number"
          value={filters.maxDistance}
          onChange={(e) => setFilters((f) => ({ ...f, maxDistance: e.target.value }))}
          placeholder="Any"
          className="input-field w-28"
        />
      </label>
      <label className="flex flex-col gap-1.5">
        <span className="data-label">Max Time Window (h)</span>
        <input
          type="number"
          value={filters.maxTimeDiff}
          onChange={(e) => setFilters((f) => ({ ...f, maxTimeDiff: e.target.value }))}
          placeholder="Any"
          className="input-field w-28"
        />
      </label>
    </div>
  )
}

function FilterSelect({ label, value, onChange, options }) {
  return (
    <label className="flex flex-col gap-1.5">
      <span className="data-label">{label}</span>
      <select
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="input-field w-36"
      >
        {options.map((o) => (
          <option key={o} value={o}>
            {o}
          </option>
        ))}
      </select>
    </label>
  )
}
