import History from './pages/History.jsx'
import React from 'react'
import { Routes, Route, useParams } from 'react-router-dom'
import AppLayout from './components/layout/AppLayout.jsx'
import { InvestigationProvider } from './context/InvestigationContext.jsx'

import Overview from './pages/Overview.jsx'
import NewInvestigation from './pages/NewInvestigation.jsx'
import InvestigationWorkspace from './pages/InvestigationWorkspace.jsx'
import SARAnalysis from './pages/SARAnalysis.jsx'
import SpillAnalysis from './pages/SpillAnalysis.jsx'
import DriftOrigin from './pages/DriftOrigin.jsx'
import VesselCorrelation from './pages/VesselCorrelation.jsx'
import Evidence from './pages/Evidence.jsx'
import Settings from './pages/Settings.jsx'

// Wraps the whole /investigation/:id/* subtree — including the persistent
// Sidebar and Header — in one data provider, so every nested view (and the
// header's ID/date readout) shares a single fetch instead of re-requesting.
function InvestigationScopedLayout() {
  const { id } = useParams()
  return (
    <InvestigationProvider id={id}>
      <AppLayout />
    </InvestigationProvider>
  )
}

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<AppLayout />}>
        <Route index element={<Overview />} />
        <Route path="investigation/new" element={<NewInvestigation />} />
	<Route path="history" element={<History />} />
        <Route path="settings" element={<Settings />} />
      </Route>

      <Route path="/investigation/:id" element={<InvestigationScopedLayout />}>
        <Route index element={<InvestigationWorkspace />} />
        <Route path="sar" element={<SARAnalysis />} />
        <Route path="spill" element={<SpillAnalysis />} />
        <Route path="drift" element={<DriftOrigin />} />
        <Route path="vessels" element={<VesselCorrelation />} />
        <Route path="evidence" element={<Evidence />} />
      </Route>
    </Routes>
  )
}
