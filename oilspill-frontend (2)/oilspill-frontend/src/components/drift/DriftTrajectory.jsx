import React from 'react'
import InvestigationMap from '../map/InvestigationMap.jsx'

export default function DriftTrajectory({ investigation }) {
  return (
    <InvestigationMap
      investigation={investigation}
      showVessels={false}
      height={440}
    />
  )
}
