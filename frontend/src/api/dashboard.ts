import { apiFetch } from './client'

export interface DashboardCards {
  varieties: number
  plants: number
  harvested_total: number
}

export interface YearLine {
  year: number
  points: { month: number; count: number }[]
}

export interface SeasonLine {
  year: number
  points: { month: number; flowers: number | null; buds: number | null; height: number | null }[]
}

export interface Dashboard {
  cards: DashboardCards
  plants_per_year: YearLine[]
  seasons: SeasonLine[]
}

export function getDashboard(): Promise<Dashboard> {
  return apiFetch<Dashboard>('/dashboard')
}
