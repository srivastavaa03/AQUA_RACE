import React, { useEffect, useState } from 'react'
import { NavLink, useParams } from 'react-router-dom'
import {
  LayoutGrid,
  PlusSquare,
  Radar,
  Droplets,
  Waves,
  Ship,
  FileClock,
History as HistoryIcon,
Settings as SettingsIcon,
} from 'lucide-react'
import { checkApiHealth } from '../../api/investigationApi.js'

function NavItem({ to, icon: Icon, label, end }) {
  return (
    <NavLink
      to={to}
      end={end}
      className={({ isActive }) =>
        [
          'flex items-center gap-3 px-4 py-2.5 text-[13px] tracking-wide border-l-2 transition-colors',
          isActive
            ? 'border-cyan-accent bg-abyss-700/60 text-ink-100'
            : 'border-transparent text-ink-500 hover:text-ink-100 hover:bg-abyss-700/30',
        ].join(' ')
      }
    >
      <Icon size={15} strokeWidth={1.75} />
      <span>{label}</span>
    </NavLink>
  )
}

function SectionLabel({ children }) {
  return (
    <div className="px-4 pt-5 pb-1.5 data-label">{children}</div>
  )
}

export default function Sidebar() {
  const { id } = useParams()
  const [online, setOnline] = useState(true)

  useEffect(() => {
    let mounted = true
    checkApiHealth().then((ok) => mounted && setOnline(ok))
    const t = setInterval(() => {
      checkApiHealth().then((ok) => mounted && setOnline(ok))
    }, 15000)
    return () => {
      mounted = false
      clearInterval(t)
    }
  }, [])

  const base = id ? `/investigation/${id}` : null

  return (
    <aside className="w-60 shrink-0 h-full bg-abyss-900 border-r border-border flex flex-col">
      <div className="px-4 py-5 border-b border-border">
        <div className="text-[13px] font-semibold tracking-wider2 text-ink-100">SIH26143</div>
        <div className="text-[10px] tracking-wider2 text-cyan-accent mt-0.5">MARITIME INTELLIGENCE</div>
      </div>

      <nav className="flex-1 overflow-y-auto py-2">
        <NavItem to="/" end icon={LayoutGrid} label="OVERVIEW" />
        <NavItem to="/investigation/new" icon={PlusSquare} label="NEW INVESTIGATION" />

        <SectionLabel>Analysis</SectionLabel>
        <NavItem to={base ? `${base}/sar` : '/investigation/new'} icon={Radar} label="SAR ANALYSIS" />
        <NavItem to={base ? `${base}/spill` : '/investigation/new'} icon={Droplets} label="SPILL ANALYSIS" />
        <NavItem to={base ? `${base}/drift` : '/investigation/new'} icon={Waves} label="DRIFT & ORIGIN" />

        <SectionLabel>Correlation</SectionLabel>
        <NavItem to={base ? `${base}/vessels` : '/investigation/new'} icon={Ship} label="VESSEL CORRELATION" />

        <SectionLabel>&nbsp;</SectionLabel>
        <NavItem to={base ? `${base}/evidence` : '/investigation/new'} icon={FileClock} label="EVIDENCE" />

        <SectionLabel>System</SectionLabel>
	<NavItem to="/history" icon={HistoryIcon} label="HISTORY" />
	<NavItem to="/settings" icon={SettingsIcon} label="SETTINGS" />
      </nav>

      <div className="px-4 py-4 border-t border-border">
        <div className="data-label mb-1.5">System Status</div>
        <div className="flex items-center gap-2 text-[12px] font-mono">
          <span
            className={[
              'inline-block w-1.5 h-1.5 rounded-full',
              online ? 'bg-signal-green' : 'bg-signal-red',
            ].join(' ')}
          />
          <span className={online ? 'text-signal-green' : 'text-signal-red'}>
            {online ? 'API ONLINE' : 'API OFFLINE'}
          </span>
        </div>
      </div>
    </aside>
  )
}


