import React, { useEffect, useMemo, useRef, useState } from 'react'
import { MapContainer, TileLayer, useMap } from 'react-leaflet'
import 'leaflet/dist/leaflet.css'
import L from 'leaflet'
import SpillLayer from './SpillLayer.jsx'
import DriftLayer from './DriftLayer.jsx'
import OriginZoneLayer from './OriginZoneLayer.jsx'
import VesselLayer from './VesselLayer.jsx'
import MapLegend from './MapLegend.jsx'
import MapControls from './MapControls.jsx'

// Leaflet's default marker icons reference bundled assets that Vite
// won't resolve automatically; point them at CDN-hosted equivalents.
delete L.Icon.Default.prototype._getIconUrl
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
  iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
})

function FitBounds({ points }) {
  const map = useMap()
  useEffect(() => {
    if (!points || points.length === 0) return
    const bounds = L.latLngBounds(points)
    if (bounds.isValid()) {
      map.fitBounds(bounds, { padding: [32, 32] })
    }
  }, [points, map])
  return null
}

export default function InvestigationMap({
  investigation,
  showSpill = true,
  showDrift = true,
  showOrigin = true,
  showVessels = true,
  height = 420,
}) {
  const [layers, setLayers] = useState({
    spill: showSpill,
    drift: showDrift,
    origin: showOrigin,
    vessels: showVessels,
  })
  const [selectedMmsi, setSelectedMmsi] = useState(null)

  const spill = investigation?.spill_characterization
  const drift = investigation?.drift_hindcast
  const origin = investigation?.origin_zone
  const ais = investigation?.ais_correlation

  const vesselPoints = useMemo(() => {
    if (!ais?.vessel_track_points) return []
    return ais.vessel_track_points.map((p) => {
      const candidate = ais.candidates?.find((c) => c.mmsi === p.mmsi)
      return { ...p, vessel: candidate?.vessel ?? 'Unknown', distance_km: candidate?.distance_km ?? null }
    })
  }, [ais])

  const fallbackCenter = investigation?.target
    ? [investigation.target.latitude, investigation.target.longitude]
    : [19.0, 72.8]

  const boundsPoints = useMemo(() => {
    const pts = []
    if (spill?.centroid) pts.push([spill.centroid.lat, spill.centroid.lon])
    if (drift?.trajectory) pts.push(...drift.trajectory)
    if (origin?.estimated) {
      pts.push([origin.north, origin.east], [origin.south, origin.west])
    }
    vesselPoints.forEach((p) => pts.push([p.lat, p.lon]))
    return pts
  }, [spill, drift, origin, vesselPoints])

  function toggle(key) {
    setLayers((prev) => ({ ...prev, [key]: !prev[key] }))
  }

  const legendItems = [
    layers.spill && { symbol: '●', label: 'Spill candidate', color: '#E0A030' },
    layers.drift && { symbol: '—', label: 'Backward trajectory', color: '#3ED6D0' },
    layers.origin && { symbol: '▣', label: 'Estimated origin zone', color: '#D9534F' },
    layers.vessels && { symbol: '◆', label: 'AIS candidate', color: '#4FAE8C' },
  ].filter(Boolean)

  return (
    <div className="relative border border-border" style={{ height }}>
      <MapContainer center={fallbackCenter} zoom={9} style={{ height: '100%', width: '100%' }} zoomControl>
        <TileLayer
          className="map-tile-dark"
          attribution='&copy; OpenStreetMap contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        {layers.spill && <SpillLayer spill={spill} />}
        {layers.drift && <DriftLayer drift={drift} />}
        {layers.origin && <OriginZoneLayer originZone={origin} />}
        {layers.vessels && (
          <VesselLayer candidates={vesselPoints} selectedMmsi={selectedMmsi} onSelect={(v) => setSelectedMmsi(v.mmsi)} />
        )}
        <FitBounds points={boundsPoints} />
      </MapContainer>
      <MapControls
        layers={[
          { key: 'spill', label: 'Spill', visible: layers.spill },
          { key: 'drift', label: 'Trajectory', visible: layers.drift },
          { key: 'origin', label: 'Origin zone', visible: layers.origin },
          { key: 'vessels', label: 'AIS candidates', visible: layers.vessels },
        ]}
        toggle={toggle}
      />
      <MapLegend items={legendItems} />
    </div>
  )
}
