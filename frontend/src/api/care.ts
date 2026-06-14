import { apiFetch } from './client'

export interface CareTip {
  id: string
  title: string
  text: string
  category: string
  months: number[]
}

export function getCareTips(): Promise<{ month: number; tips: CareTip[] }> {
  return apiFetch<{ month: number; tips: CareTip[] }>('/care-tips')
}
