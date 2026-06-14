import { apiFetch } from './client'
import type { PlantingHistory } from './plants'
import type { LocationKind } from './locations'

export interface PlantingInput {
  plant_id: number
  location_id?: number | null
  new_location_kind?: LocationKind | null
  new_location_name?: string | null
  position?: string | null
  planted_on?: string | null
}

export function createPlanting(input: PlantingInput): Promise<PlantingHistory> {
  return apiFetch<PlantingHistory>('/plantings', {
    method: 'POST',
    body: JSON.stringify(input),
  })
}
