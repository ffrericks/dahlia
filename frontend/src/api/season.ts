import { apiFetch } from './client'

export interface SeasonStatus {
  can_start_new: boolean
  blocking: { id: number; full_code: string }[]
  survived_count: number
}

export function getSeasonStatus(): Promise<SeasonStatus> {
  return apiFetch<SeasonStatus>('/season/status')
}

export function startNewSeason(): Promise<{ resumed: number }> {
  return apiFetch<{ resumed: number }>('/season/new', { method: 'POST' })
}
