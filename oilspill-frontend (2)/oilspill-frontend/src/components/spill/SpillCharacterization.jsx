import React from 'react'
import MetricRow from '../common/MetricRow.jsx'

export default function SpillCharacterization({ spill }) {
  if (!spill) return null
  const bbox = spill.bounding_box
    ? `[${spill.bounding_box[0][0].toFixed(3)}, ${spill.bounding_box[0][1].toFixed(3)}] – [${spill.bounding_box[1][0].toFixed(3)}, ${spill.bounding_box[1][1].toFixed(3)}]`
    : null

  return (
    <div className="panel p-4">
      <h3 className="text-[12px] font-semibold tracking-wide text-ink-100 mb-2">Bounding Box</h3>
      <MetricRow label="Bounding Box" value={bbox} />
      <p className="text-[11px] text-ink-500 mt-3 leading-relaxed">
        This scene contains an AI-detected oil-spill candidate. Detection reflects a model
        inference over the SAR scene and is subject to independent verification.
      </p>
    </div>
  )
}
