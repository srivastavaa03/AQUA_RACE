import React from 'react'
import { Check, Loader2, X, Clock, HelpCircle } from 'lucide-react'

const ICONS = {
  waiting: Clock,
  pending: Clock,
  running: Loader2,
  complete: Check,
  completed: Check,
  failed: X,
  unavailable: HelpCircle,
}

const COLORS = {
  waiting: 'text-ink-700 border-ink-700',
  pending: 'text-ink-700 border-ink-700',
  running: 'text-signal-amber border-signal-amber',
  complete: 'text-signal-green border-signal-green',
  completed: 'text-signal-green border-signal-green',
  failed: 'text-signal-red border-signal-red',
  unavailable: 'text-ink-500 border-ink-500 opacity-60',
}

const LINE_COLORS = {
  waiting: 'bg-border',
  pending: 'bg-border',
  running: 'bg-signal-amber',
  complete: 'bg-signal-green',
  completed: 'bg-signal-green',
  failed: 'bg-signal-red',
  unavailable: 'bg-border',
}

export default function PipelineProgress({ stages, orientation = 'horizontal' }) {
  if (!stages || stages.length === 0) return null
  const isVertical = orientation === 'vertical'

  if (isVertical) {
    return (
      <div className="flex flex-col">
        {stages.map((stage, idx) => {
          const statusKey = stage.status || 'waiting'
          const Icon = ICONS[statusKey] || Clock
          const colorCls = COLORS[statusKey] || COLORS.waiting
          const lineCls = LINE_COLORS[statusKey] || LINE_COLORS.waiting
          const isLast = idx === stages.length - 1
          const stageTitle = stage.name || stage.label || ''

          return (
            <div key={stage.id || idx} className="flex gap-3">
              <div className="flex flex-col items-center">
                <div className={['w-8 h-8 flex items-center justify-center border shrink-0', colorCls].join(' ')}>
                  <Icon size={14} strokeWidth={2} className={statusKey === 'running' ? 'animate-spin' : ''} />
                </div>
                {!isLast && <div className={['w-px flex-1 min-h-[20px]', lineCls].join(' ')} />}
              </div>
              <div className="pb-5 pt-1.5">
                <div className="text-[12px] text-ink-100 font-medium">{stageTitle}</div>
                <div className="text-[10px] text-ink-500 uppercase tracking-wider">{stage.status}</div>
              </div>
            </div>
          )
        })}
      </div>
    )
  }

  return (
    <div className="flex items-start justify-between overflow-x-auto pb-2 w-full">
      {stages.map((stage, idx) => {
        const statusKey = stage.status || 'waiting'
        const Icon = ICONS[statusKey] || Clock
        const colorCls = COLORS[statusKey] || COLORS.waiting
        const prevStatus = stages[idx > 0 ? idx - 1 : 0]?.status || 'waiting'
        const lineCls = LINE_COLORS[prevStatus] || LINE_COLORS.waiting
        const isFirst = idx === 0
        const stageTitle = stage.name || stage.label || ''

        return (
          <React.Fragment key={stage.id || idx}>
            {!isFirst && <div className={['h-px flex-1 mt-4 min-w-[20px]', lineCls].join(' ')} />}
            <div className="flex flex-col items-center min-w-[110px] max-w-[150px]">
              <div className={['w-8 h-8 flex items-center justify-center border shrink-0', colorCls].join(' ')}>
                <Icon size={14} strokeWidth={2} className={statusKey === 'running' ? 'animate-spin' : ''} />
              </div>
              <span className="mt-2 text-[11px] font-medium text-ink-100 text-center leading-tight px-1">
                {stageTitle}
              </span>
              <span className="mt-1 text-[9px] text-ink-500 uppercase tracking-wider text-center">
                {stage.status}
              </span>
            </div>
          </React.Fragment>
        )
      })}
    </div>
  )
}
