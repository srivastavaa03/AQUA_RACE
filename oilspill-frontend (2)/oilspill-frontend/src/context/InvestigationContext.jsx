import React, {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useState,
} from 'react'

import {
  getInvestigation,
  ApiError,
} from '../api/investigationApi.js'

import { normalizeInvestigation } from '../api/normalizeInvestigation.js'

const InvestigationContext = createContext(null)

export function InvestigationProvider({ id, children }) {
  const [investigation, setInvestigation] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const reload = useCallback(async () => {
    if (!id) return

    try {
      const data = await getInvestigation(id)
      const normalized = normalizeInvestigation(data)

      setInvestigation(normalized)
      setError(null)

      return normalized
    } catch (err) {
      const apiError =
        err instanceof ApiError
          ? err
          : new ApiError(err.message, 'unknown')

      setError(apiError)

      return null
    } finally {
      setLoading(false)
    }
  }, [id])

  useEffect(() => {
    if (!id) {
      setLoading(false)
      return
    }

    let cancelled = false
    let timer = null

    async function poll() {
      if (cancelled) return

      const result = await reload()

      if (cancelled) return

      const status = result?.status

      if (status === 'queued' || status === 'running') {
        timer = setTimeout(poll, 2500)
      }
    }

    setLoading(true)
    poll()

    return () => {
      cancelled = true

      if (timer) {
        clearTimeout(timer)
      }
    }
  }, [id, reload])

  return (
    <InvestigationContext.Provider
      value={{
        investigation,
        loading,
        error,
        reload,
        id,
      }}
    >
      {children}
    </InvestigationContext.Provider>
  )
}

export function useInvestigation() {
  const ctx = useContext(InvestigationContext)

  if (!ctx) {
    throw new Error(
      'useInvestigation must be used within InvestigationProvider'
    )
  }

  return ctx
}

export function useInvestigationSafe() {
  return useContext(InvestigationContext)
}
