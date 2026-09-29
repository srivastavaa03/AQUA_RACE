import React from 'react'
import EvidenceItem from './EvidenceItem.jsx'
import EmptyState from '../common/EmptyState.jsx'

export default function EvidenceTimeline({ events }) {
  if (!events || events.length === 0) {
    return <EmptyState title="No evidence events recorded" description="Pipeline evidence will appear here as the investigation progresses." />
  }

  return (
    <div className="panel p-5">
      {events.map((event, idx) => (
        <EvidenceItem key={idx} event={event} isLast={idx === events.length - 1} />
      ))}
    </div>
  )
}
