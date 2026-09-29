import React from 'react'
import { Marker, Popup } from 'react-leaflet'
import L from 'leaflet'

const COLOR = '#4FAE8C'

function diamondIcon(selected) {
  return L.divIcon({
    className: '',
    html: `<div style="width:10px;height:10px;background:${COLOR};transform:rotate(45deg);border:1px solid #0A0E15;${
      selected ? 'box-shadow:0 0 0 3px rgba(79,174,140,0.35);' : ''
    }"></div>`,
    iconSize: [10, 10],
    iconAnchor: [5, 5],
  })
}

export default function VesselLayer({ candidates, selectedMmsi, onSelect }) {
  if (!candidates || candidates.length === 0) return null

  return (
    <>
      {candidates
        .filter((c) => c.lat != null && c.lon != null)
        .map((c) => (
          <Marker
            key={c.mmsi}
            position={[c.lat, c.lon]}
            icon={diamondIcon(c.mmsi === selectedMmsi)}
            eventHandlers={{ click: () => onSelect && onSelect(c) }}
          >
            <Popup>
              <div className="font-mono text-[11px]">
                <div className="text-ink-100 font-semibold mb-1">{c.vessel}</div>
                <div>MMSI: {c.mmsi}</div>
                <div>Distance: {c.distance_km} km</div>
              </div>
            </Popup>
          </Marker>
        ))}
    </>
  )
}
