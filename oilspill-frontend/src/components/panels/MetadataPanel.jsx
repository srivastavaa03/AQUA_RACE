import { Satellite } from 'lucide-react'
import Panel, { Unavailable } from './Panel'

const ROWS = [
  ['productName', 'Product'],
  ['satellite', 'Satellite'],
  ['mode', 'Mode'],
  ['productType', 'Product type'],
  ['polarization', 'Polarization'],
  ['acquisitionStart', 'Acquisition start'],
  ['acquisitionEnd', 'Acquisition end'],
  ['orbit', 'Orbit'],
  ['missionDataTake', 'Mission data take'],
]

export default function MetadataPanel({ metadata }) {
  return (
    <Panel icon={Satellite} title="Sentinel-1 metadata" eyebrow="Copernicus SAFE product">
      {!metadata ? (
        <Unavailable label="Sentinel-1 metadata not returned by the backend yet." />
      ) : (
        <dl className="space-y-1.5">
          {ROWS.map(([key, label]) => (
            <div key={key} className="flex items-start justify-between gap-3 text-[12px]">
              <dt className="text-mist-500">{label}</dt>
              <dd className="truncate font-mono text-mist-100" title={metadata[key]}>
                {metadata[key] === undefined ? (
                  <span className="italic text-mist-700">Data unavailable</span>
                ) : (
                  metadata[key]
                )}
              </dd>
            </div>
          ))}
        </dl>
      )}
    </Panel>
  )
}
