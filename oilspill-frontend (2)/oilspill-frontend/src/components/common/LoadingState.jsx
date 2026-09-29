import React from 'react'
import { Loader2 } from 'lucide-react'

export default function LoadingState({ message = 'Loading investigation data.' }) {
  return (
    <div className="panel flex flex-col items-center justify-center gap-3 py-16 text-ink-500">
      <Loader2 size={22} className="animate-spin text-cyan-accent" strokeWidth={1.75} />
      <p className="text-[12px] tracking-wide">{message}</p>
    </div>
  )
}
