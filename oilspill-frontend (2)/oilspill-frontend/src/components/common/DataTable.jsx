import React, { useMemo, useState } from 'react'
import { ArrowUp, ArrowDown, ArrowUpDown } from 'lucide-react'

/**
 * Generic sortable data table.
 * columns: [{ key, label, mono, render(row) }]
 */
export default function DataTable({ columns, rows, onRowClick, selectedKey, rowKey = (r) => r.id }) {
  const [sort, setSort] = useState({ key: null, dir: 'asc' })

  const sorted = useMemo(() => {
    if (!sort.key) return rows
    const copy = [...rows]
    copy.sort((a, b) => {
      const av = a[sort.key]
      const bv = b[sort.key]
      if (typeof av === 'number' && typeof bv === 'number') {
        return sort.dir === 'asc' ? av - bv : bv - av
      }
      return sort.dir === 'asc'
        ? String(av).localeCompare(String(bv))
        : String(bv).localeCompare(String(av))
    })
    return copy
  }, [rows, sort])

  function toggleSort(key) {
    setSort((prev) =>
      prev.key === key ? { key, dir: prev.dir === 'asc' ? 'desc' : 'asc' } : { key, dir: 'asc' }
    )
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-[12px] border-collapse">
        <thead>
          <tr className="border-b border-border">
            {columns.map((col) => (
              <th
                key={col.key}
                onClick={() => col.sortable !== false && toggleSort(col.key)}
                className="text-left px-3 py-2 data-label cursor-pointer select-none whitespace-nowrap"
              >
                <span className="inline-flex items-center gap-1">
                  {col.label}
                  {col.sortable !== false &&
                    (sort.key === col.key ? (
                      sort.dir === 'asc' ? (
                        <ArrowUp size={11} />
                      ) : (
                        <ArrowDown size={11} />
                      )
                    ) : (
                      <ArrowUpDown size={11} className="text-ink-700" />
                    ))}
                </span>
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {sorted.map((row) => (
            <tr
              key={rowKey(row)}
              onClick={() => onRowClick && onRowClick(row)}
              className={[
                'border-b border-border/60 transition-colors',
                onRowClick ? 'cursor-pointer hover:bg-abyss-700/40' : '',
                selectedKey && selectedKey === rowKey(row) ? 'bg-abyss-700/60' : '',
              ].join(' ')}
            >
              {columns.map((col) => (
                <td
                  key={col.key}
                  className={['px-3 py-2 whitespace-nowrap', col.mono ? 'font-mono' : ''].join(' ')}
                >
                  {col.render ? col.render(row) : row[col.key]}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
