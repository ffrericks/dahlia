import { apiFetch } from './client'

export interface Variety {
  id: number
  code: string
  name: string | null
  description: string | null
  wikipedia_url: string | null
  plant_count: number
  image_thumbnail: string | null
}

export interface VarietyInput {
  code: string
  name?: string | null
  description?: string | null
  wikipedia_url?: string | null
}

export function listVarieties(): Promise<Variety[]> {
  return apiFetch<Variety[]>('/varieties')
}

export function createVariety(input: VarietyInput): Promise<Variety> {
  return apiFetch<Variety>('/varieties', {
    method: 'POST',
    body: JSON.stringify(input),
  })
}

export function updateVariety(
  id: number,
  input: Partial<VarietyInput>,
): Promise<Variety> {
  return apiFetch<Variety>(`/varieties/${id}`, {
    method: 'PATCH',
    body: JSON.stringify(input),
  })
}

export function deleteVariety(id: number): Promise<void> {
  return apiFetch<void>(`/varieties/${id}`, { method: 'DELETE' })
}

export function fetchDescription(url: string): Promise<{ extract: string }> {
  return apiFetch<{ extract: string }>('/varieties/description-extract', {
    method: 'POST',
    body: JSON.stringify({ url }),
  })
}
