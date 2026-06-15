import { apiFetch } from './client'

export interface AppSettings {
  tool_url: string | null
  auto_fertilize_bak: boolean
  default_garden_name: string | null
}

export function getSettings(): Promise<AppSettings> {
  return apiFetch<AppSettings>('/settings')
}

export function updateSettings(input: Partial<AppSettings>): Promise<AppSettings> {
  return apiFetch<AppSettings>('/settings', {
    method: 'PUT',
    body: JSON.stringify(input),
  })
}
