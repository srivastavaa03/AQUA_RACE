import React from 'react'
import { Polygon, CircleMarker, Popup } from 'react-leaflet'

const COLOR = '#E0A030'

export default function SpillLayer({ spill }) {
  if (!spill) return null
  const { bounding_box, centroid, estimated_area_km2 } = spill

  const polygonPositions =
    bounding_box && bounding_box.length === 2
      ? [
          [bounding_box[0][0], bounding_box[0][1]],
          [bounding_box[0][0], bounding_box[1][1]],
          [bounding_box[1][0], bounding_box[1][1]],
          [bounding_box[1][0], bounding_box[0][1]],
        ]
      : null

  return (
    <>
      {polygonPositions && (
        <Polygon
          positions={polygonPositions}
          pathOptions={{ color: COLOR, weight: 1.5, fillColor: COLOR, fillOpacity: 0.15 }}
        />
      )}
      {centroid && (
        <CircleMarker
          center={[centroid.lat, centroid.lon]}
          radius={6}
          pathOptions={{ color: COLOR, fillColor: COLOR, fillOpacity: 0.9, weight: 1.5 }}
        >
          <Popup>
            <div className="font-mono text-[11px]">
              <div className="text-ink-100 font-semibold mb-1">Spill Candidate</div>
              <div>Centroid: {centroid.lat.toFixed(4)}°, {centroid.lon.toFixed(4)}°</div>
              {estimated_area_km2 != null && <div>Area: {estimated_area_km2.toFixed(2)} km²</div>}
            </div>
          </Popup>
        </CircleMarker>
      )}
    </>
  )
}
