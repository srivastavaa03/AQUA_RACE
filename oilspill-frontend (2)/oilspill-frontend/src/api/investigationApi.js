import { getMockInvestigation } from '../mockData.js'

export const BASE_URL = 'http://127.0.0.1:8000'

export const USE_MOCK = false

const TIMEOUT_MS = 10000

export class ApiError extends Error {
  constructor(message, kind, status = null) {
    super(message)
    this.kind = kind
    this.status = status
  }
}

async function request(path, options = {}) {
  const controller = new AbortController()
  const timer = setTimeout(() => controller.abort(), TIMEOUT_MS)

  try {
    const res = await fetch(`${BASE_URL}${path}`, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...(options.headers || {}),
      },
      signal: controller.signal,
    })

    clearTimeout(timer)

    if (!res.ok) {
      if (res.status === 404) {
        throw new ApiError('Investigation not found.', 'not_found', 404)
      }

      throw new ApiError(
        `Investigation API returned ${res.status}.`,
        'server',
        res.status
      )
    }

    return await res.json()
  } catch (err) {
    clearTimeout(timer)

    if (err instanceof ApiError) throw err

    if (err.name === 'AbortError') {
      throw new ApiError(
        'Investigation API request timed out.',
        'timeout'
      )
    }

    throw new ApiError(
      'No connection to investigation API.',
      'offline'
    )
  }
}

export async function createInvestigation({
  latitude,
  longitude,
  observationDate,
}) {
  return request('/api/investigate', {
    method: 'POST',
    body: JSON.stringify({
      latitude,
      longitude,
      date: observationDate,
    }),
  })
}

export async function getInvestigation(id) {
  return request(`/api/investigation/${id}`)
}

export async function retryInvestigation(id) {
  return request(`/api/investigation/${id}/retry`, {
    method: 'POST',
  })
}

export async function getInvestigationStatus(id) {
  return request(`/api/investigation/${id}/status`)
}

export async function checkApiHealth() {
  try {
    const controller = new AbortController()
    const timer = setTimeout(() => controller.abort(), 3000)

    const res = await fetch(`${BASE_URL}/health`, {
      signal: controller.signal,
    })

    clearTimeout(timer)

    return res.ok
  } catch {
    return false
  }
}
export async function getInvestigationHistory() {
  const data = await request('/api/investigations')
  return Array.isArray(data?.investigations)
    ? data.investigations
    : []
}
