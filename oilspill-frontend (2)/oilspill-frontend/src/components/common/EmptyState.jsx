import React from 'react'
import { Inbox } from 'lucide-react'

export default function EmptyState({ title, description, icon: Icon = Inbox }) {
  return (
    <div className="panel flex flex-col items-center justify-center gap-2 py-16 text-center px-8">
      <Icon size={22} className="text-ink-700 mb-1" strokeWidth={1.5} />
      <p className="text-[13px] font-semibold text-ink-300 tracking-wide">{title}</p>
      {description && <p className="text-[12px] text-ink-500 max-w-md">{description}</p>}
    </div>
  )
}
