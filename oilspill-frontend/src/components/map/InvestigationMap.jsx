import { MapContainer, TileLayer, CircleMarker, Polyline, Rectangle, Popup, Tooltip as LeafletTooltip } from 'react-leaflet'
import { MapPin } from 'lucide-react'
import Panel, { Unavailable } from '../panels/Panel'

export default function InvestigationMap({ result }) {
  const { characterization, hindcast, originZone, aisCandidates } = result

  const centroid = characterization?.centroid
  const spillBounds = characterization?.bounds
  const driftPath = hindcast?.path
  const originBounds = originZone?.bounds
  const originEndpoint = originZone?.endpoint
  // Only plot AIS candidates the backend actually located — never invent a
  // position for a candidate it only gave a distance/confidence for.
  const locatedCandidates = (aisCandidates ?? []).filter((c) => c.lat !== undefined && c.lon !== undefined)

  // Map needs at least one real coordinate to center on. Prefer the spill
  // centroid, fall back to the origin-zone endpoint.
  const center = centroid ? [centroid.lat, centroid.lon] : originEndpoint ? [originEndpoint.lat, originEndpoint.lon] : null

  if (!center) {
    return (
      <Panel icon={MapPin} title="Investigation map" eyebrow="Spill site · drift track · origin zone · AIS candidates" className="h-full">
        <Unavailable label="No geolocated data available yet to plot on the map." />
      </Panel>
    )
  }

  return (
    <Panel icon={MapPin} title="Investigation map" eyebrow="Spill site · drift track · origin zone · AIS candidates" className="h-full">
      <div className="h-[460px] overflow-hidden rounded-sm border border-deck-600">
        <MapContainer center={center} zoom={8} style={{ height: '100%', width: '100%' }} scrollWheelZoom>
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; CARTO'
            url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
          />

          {spillBounds && (
            <Rectangle
              bounds={[
                [spillBounds.south, spillBounds.west],
                [spillBounds.north, spillBounds.east],
              ]}
              pathOptions={{ color: '#E23B4E', weight: 1.5, fillOpacity: 0.15 }}
            >
              <LeafletTooltip direction="top">
                Detected spill extent
                {characterization.areaKm2 !== undefined ? ` — ${Number(characterization.areaKm2).toFixed(2)} km²` : ''}
              </LeafletTooltip>
            </Rectangle>
          )}

          {centroid && (
            <CircleMarker center={[centroid.lat, centroid.lon]} radius={6} pathOptions={{ color: '#E23B4E', fillColor: '#E23B4E', fillOpacity: 0.9 }}>
              <Popup>
                <div className="font-mono text-[12px]">
                  <p className="font-semibold text-hull-950">Spill centroid</p>
                  <p>{centroid.lat.toFixed(5)}, {centroid.lon.toFixed(5)}</p>
                  {characterization.areaKm2 !== undefined && <p>{Number(characterization.areaKm2).toFixed(2)} km²</p>}
                </div>
              </Popup>
            </CircleMarker>
          )}

          {driftPath && driftPath.length > 1 && (
            <Polyline
              positions={driftPath.map((p) => [p.lat, p.lon])}
              pathOptions={{ color: '#2DD4BF', weight: 2, dashArray: '4 5' }}
            />
          )}

          {originBounds && (
            <Rectangle
              bounds={[
                [originBounds.south, originBounds.west],
                [originBounds.north, originBounds.east],
              ]}
              pathOptions={{ color: '#F5A524', weight: 1.5, fillOpacity: 0.08, dashArray: '6 4' }}
            >
              <LeafletTooltip direction="top">
                Estimated origin zone{originZone.uncertaintyKm !== undefined ? ` — ±${originZone.uncertaintyKm} km` : ''}
              </LeafletTooltip>
            </Rectangle>
          )}

          {originEndpoint && (
            <CircleMarker
              center={[originEndpoint.lat, originEndpoint.lon]}
              radius={6}
              pathOptions={{ color: '#F5A524', fillColor: '#F5A524', fillOpacity: 0.9 }}
            >
              <Popup>
                <div className="font-mono text-[12px]">
                  <p className="font-semibold text-hull-950">96h-back endpoint</p>
                  <p>{originEndpoint.lat.toFixed(5)}, {originEndpoint.lon.toFixed(5)}</p>
                </div>
              </Popup>
            </CircleMarker>
          )}

          {locatedCandidates.map((c) => (
            <CircleMarker
              key={c.candidateId}
              center={[c.lat, c.lon]}
              radius={5}
              pathOptions={{ color: '#5EEAD4', fillColor: '#5EEAD4', fillOpacity: 0.7 }}
            >
              <Popup>
                <div className="font-mono text-[12px]">
                  <p className="font-semibold text-hull-950">{c.candidateId}</p>
                  <p>{c.vesselType ?? 'Unknown type'}</p>
                  {c.mmsiMasked && <p>MMSI {c.mmsiMasked}</p>}
                  {c.confidence !== undefined && <p>{Math.round(c.confidence * 100)}% confidence</p>}
                </div>
              </Popup>
            </CircleMarker>
          ))}
        </MapContainer>
      </div>

      <div className="mt-3 flex flex-wrap gap-x-5 gap-y-1.5 text-[11px] text-mist-500">
        <Legend color="#E23B4E" label="Detected spill" />
        <Legend color="#2DD4BF" label="96h drift track" dashed />
        <Legend color="#F5A524" label="Origin zone" dashed />
        <Legend color="#5EEAD4" label="AIS candidate" />
      </div>
      {aisCandidates && aisCandidates.length > 0 && locatedCandidates.length === 0 && (
        <p className="mt-2 text-[10.5px] text-mist-700">
          AIS candidates were returned without map coordinates, so they're listed in the AIS tab but not plotted here.
        </p>
      )}
    </Panel>
  )
}

function Legend({ color, label, dashed }) {
  return (
    <div className="flex items-center gap-1.5">
      <span
        className="inline-block h-0.5 w-4"
        style={{ backgroundColor: dashed ? 'transparent' : color, borderTop: dashed ? `2px dashed ${color}` : 'none' }}
      />
      <span className="h-2 w-2 rounded-full" style={{ backgroundColor: color }} />
      {label}
    </div>
  )
}
