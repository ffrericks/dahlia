// Generic JSON fetch helper. Surfaces backend errors (with the API's detail message)
// rather than swallowing them, so failures are visible.
export async function apiFetch<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`/api${path}`, {
    headers: { 'Content-Type': 'application/json', ...(options?.headers ?? {}) },
    ...options,
  })

  if (!response.ok) {
    let detail = `HTTP ${response.status}`
    try {
      const body = await response.json()
      if (typeof body?.detail === 'string') detail = body.detail
    } catch {
      // response had no JSON body; keep the status-based message
    }
    throw new Error(detail)
  }

  if (response.status === 204) return undefined as T
  return response.json()
}
