import React from 'react'
import { Polyline, CircleMarker, Popup } from 'react-leaflet'

const COLOR = '#3ED6D0'

export default function DriftLayer({ drift }) {
  if (!drift || !drift.trajectory || drift.trajectory.length === 0) return null
  const { trajectory, backward_endpoint } = drift

  return (
    <>
      <Polyline
        positions={trajectory}
        pathOptions={{ color: COLOR, weight: 2, dashArray: '6 5' }}
      />
      {backward_endpoint && (
        <CircleMarker
          center={[backward_endpoint.lat, backward_endpoint.lon]}
          radius={5}
          pathOptions={{ color: COLOR, fillColor: COLOR, fillOpacity: 0.9, weight: 1.5 }}
        >
          <Popup>
            <div className="font-mono text-[11px]">
              <div className="text-ink-100 font-semibold mb-1">Backward Endpoint</div>
              <div>
                {backward_endpoint.lat.toFixed(4)}°, {backward_endpoint.lon.toFixed(4)}°
              </div>
            </div>
          </Popup>
        </CircleMarker>
      )}
    </>
  )
}
