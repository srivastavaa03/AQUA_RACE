export default function Panel({ icon: Icon, title, eyebrow, children, className = '', right }) {
  return (
    <section className={`rounded-md border border-deck-600 bg-deck-800/60 shadow-panel ${className}`}>
      <header className="flex items-center justify-between gap-3 border-b border-deck-600 px-4 py-3">
        <div className="flex items-center gap-2.5">
          {Icon && <Icon size={16} className="text-sonar-500 shrink-0" strokeWidth={1.75} />}
          <div>
            <h3 className="text-[13px] font-medium text-mist-100 leading-tight">{title}</h3>
            {eyebrow && <p className="text-[11px] text-mist-500 leading-tight mt-0.5">{eyebrow}</p>}
          </div>
        </div>
        {right}
      </header>
      <div className="p-4">{children}</div>
    </section>
  )
}

// A value is treated as "unavailable" (rather than falsy-but-real) only
// when it is null or undefined — 0, false and '' are legitimate values a
// backend can return and must still render normally.
export function isUnavailable(value) {
  return value === null || value === undefined
}

export function Stat({ label, value, unit, tone = 'default' }) {
  const toneClass = {
    default: 'text-mist-100',
    sonar: 'text-sonar-400',
    flare: 'text-flare-400',
    hazard: 'text-hazard-400',
  }[tone]

  const unavailable = isUnavailable(value)

  return (
    <div className="flex flex-col gap-0.5">
      <span className="text-[11px] text-mist-500">{label}</span>
      {unavailable ? (
        <span className="text-[12.5px] italic text-mist-700">Data unavailable</span>
      ) : (
        <span className={`font-mono text-[15px] font-medium ${toneClass}`}>
          {value}
          {unit && <span className="ml-1 text-[11px] text-mist-500">{unit}</span>}
        </span>
      )}
    </div>
  )
}

export function Unavailable({ label = 'Data unavailable' }) {
  return <p className="text-[12px] italic text-mist-700">{label}</p>
}
