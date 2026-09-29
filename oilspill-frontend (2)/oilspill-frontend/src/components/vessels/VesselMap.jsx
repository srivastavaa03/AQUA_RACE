import React from 'react'
import InvestigationMap from '../map/InvestigationMap.jsx'

export default function VesselMap({ investigation }) {
  return <InvestigationMap investigation={investigation} showSpill={false} height={520} />
}
