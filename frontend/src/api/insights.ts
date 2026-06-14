import { apiFetch } from './client'

export interface Weights {
  height: number
  flowers: number
  harvested: number
}

export interface LocationScore {
  location_id: number
  code: string
  label: string
  name: string | null
  plantings: number
  avg_height: number
  avg_flowers: number
  avg_harvested: number
  score: number
}

export function getLocationRanking(
  weights: Weights,
): Promise<{ weights: Weights; locations: LocationScore[] }> {
  const q = new URLSearchParams({
    w_height: String(weights.height),
    w_flowers: String(weights.flowers),
    w_harvested: String(weights.harvested),
  })
  return apiFetch(`/insights/locations?${q.toString()}`)
}
