import React from 'react'
import { Rectangle, Popup } from 'react-leaflet'

const COLOR = '#D9534F'

export default function OriginZoneLayer({ originZone }) {
  if (!originZone || !originZone.estimated) return null
  const { north, south, east, west } = originZone
  if ([north, south, east, west].some((v) => v == null)) return null

  return (
    <Rectangle
      bounds={[
        [south, west],
        [north, east],
      ]}
      pathOptions={{ color: COLOR, weight: 1.5, fillColor: COLOR, fillOpacity: 0.1, dashArray: '4 4' }}
    >
      <Popup>
        <div className="font-mono text-[11px]">
          <div className="text-ink-100 font-semibold mb-1">Estimated Origin Zone</div>
          <div>Buffer: {originZone.buffer_km ?? 'N/A'} km</div>
        </div>
      </Popup>
    </Rectangle>
  )
}
