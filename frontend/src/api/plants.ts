import { apiFetch } from './client'

export type Origin = 'purchased' | 'gifted' | 'split' | 'seedling' | 'unknown'

export interface PlantLocation {
  code: string
  name: string | null
  label: string
  position: string | null
}

export interface PlantingHistory {
  id: number
  location_id: number
  location_code: string
  location_name: string | null
  location_label: string
  position: string | null
  planted_on: string
  lifted_on: string | null
}

export interface PlantStorage {
  box_code: string
  composite: string
}

export interface Plant {
  id: number
  variety_id: number
  variety_code: string
  variety_name: string | null
  ss: number | null
  ddd: number | null
  number: string | null
  full_code: string | null
  nickname: string | null
  label: string // full_code, else nickname, else "Onbekend"
  origin: Origin
  parent_plant_id: number | null
  state: string
  eye_status: string | null
  disease_warning: boolean
  thumbnail: string | null
  location: PlantLocation | null
  storage: PlantStorage | null
}

export interface Photo {
  id: number
  plant_id: number
  url: string
  thumbnail_url: string
  is_profile: boolean
}

export interface LogEntry {
  id: number
  plant_id: number
  entry_date: string
  text: string | null
  height_cm: number | null
  bud_count: number | null
  flower_count: number | null
  harvested_count: number | null
}

export interface Disposal {
  kind: string
  reason: string | null
  recipient: string | null
  disease_warning: boolean
  disposed_on: string
}

export interface Descendants {
  total: number
  owned: number
}

export interface YearHistory {
  year: number
  location_code: string
  location_label: string
  planted_on: string
  lifted_on: string | null
  height_max: number | null
  flowers_max: number | null
  harvested_total: number
}

export interface PlantDetail extends Plant {
  parent: Plant | null
  children: Plant[]
  photos: Photo[]
  plantings: PlantingHistory[]
  logs: LogEntry[]
  disposal: Disposal | null
  descendants: Descendants
  yearly: YearHistory[]
}

export interface LogInput {
  text?: string | null
  height_cm?: number | null
  bud_count?: number | null
  flower_count?: number | null
  harvested_count?: number | null
  entry_date?: string | null
}

export interface DisposalInput {
  kind: 'discarded' | 'given_away'
  reason?: string | null
  recipient?: string | null
  disease_warning?: boolean
  disposed_on?: string | null
}

export interface TreeNode extends Plant {
  children: TreeNode[]
}

export interface Summary {
  total: number
  by_state: Record<string, number>
}

export interface PlantCreateInput {
  origin: Origin
  parent_plant_id?: number | null
  variety_id?: number | null
  new_variety_code?: string | null
  new_variety_name?: string | null
  nickname?: string | null
}

export interface AssignVarietyInput {
  variety_id?: number | null
  new_variety_code?: string | null
  new_variety_name?: string | null
}

export function listPlants(includeGone = false): Promise<Plant[]> {
  return apiFetch<Plant[]>(`/plants${includeGone ? '?include_gone=true' : ''}`)
}

export function getPlant(id: number): Promise<PlantDetail> {
  return apiFetch<PlantDetail>(`/plants/${id}`)
}

export function createPlant(input: PlantCreateInput): Promise<Plant> {
  return apiFetch<Plant>('/plants', { method: 'POST', body: JSON.stringify(input) })
}

export function deletePlant(id: number): Promise<void> {
  return apiFetch<void>(`/plants/${id}`, { method: 'DELETE' })
}

export function updatePlant(id: number, nickname: string | null): Promise<Plant> {
  return apiFetch<Plant>(`/plants/${id}`, {
    method: 'PATCH',
    body: JSON.stringify({ nickname }),
  })
}

export function assignVariety(id: number, input: AssignVarietyInput): Promise<Plant> {
  return apiFetch<Plant>(`/plants/${id}/variety`, {
    method: 'PUT',
    body: JSON.stringify(input),
  })
}

export function getTree(): Promise<TreeNode[]> {
  return apiFetch<TreeNode[]>('/plants/tree')
}

export function getSummary(): Promise<Summary> {
  return apiFetch<Summary>('/plants/summary')
}

// Photo upload uses multipart/form-data, so it bypasses the JSON apiFetch helper.
export async function uploadPhoto(plantId: number, file: File): Promise<Photo> {
  const form = new FormData()
  form.append('file', file)
  const response = await fetch(`/api/plants/${plantId}/photos`, {
    method: 'POST',
    body: form,
  })
  if (!response.ok) {
    let detail = `HTTP ${response.status}`
    try {
      const body = await response.json()
      if (typeof body?.detail === 'string') detail = body.detail
    } catch {
      // no JSON body
    }
    throw new Error(detail)
  }
  return response.json()
}

export function setProfilePhoto(plantId: number, photoId: number): Promise<Photo> {
  return apiFetch<Photo>(`/plants/${plantId}/photos/${photoId}/profile`, { method: 'PUT' })
}

export function deletePhoto(plantId: number, photoId: number): Promise<void> {
  return apiFetch<void>(`/plants/${plantId}/photos/${photoId}`, { method: 'DELETE' })
}

// --- winter / storage actions ---

export function liftPlant(id: number, liftedOn?: string): Promise<Plant> {
  return apiFetch<Plant>(`/plants/${id}/lift`, {
    method: 'POST',
    body: JSON.stringify({ lifted_on: liftedOn ?? null }),
  })
}

export function markSurvivedWinter(id: number): Promise<Plant> {
  return apiFetch<Plant>(`/plants/${id}/survive-winter`, { method: 'POST' })
}

export function setEyeStatus(id: number, eyeStatus: string): Promise<Plant> {
  return apiFetch<Plant>(`/plants/${id}/eye-status`, {
    method: 'PATCH',
    body: JSON.stringify({ eye_status: eyeStatus }),
  })
}

export function assignStorage(id: number, number: number, year?: number): Promise<Plant> {
  return apiFetch<Plant>(`/plants/${id}/storage`, {
    method: 'PUT',
    body: JSON.stringify({ number, year: year ?? null }),
  })
}

export function removeStorage(id: number): Promise<void> {
  return apiFetch<void>(`/plants/${id}/storage`, { method: 'DELETE' })
}

// --- logbook & disposal ---

export function addLog(plantId: number, input: LogInput): Promise<LogEntry> {
  return apiFetch<LogEntry>(`/plants/${plantId}/logs`, {
    method: 'POST',
    body: JSON.stringify(input),
  })
}

export function deleteLog(plantId: number, logId: number): Promise<void> {
  return apiFetch<void>(`/plants/${plantId}/logs/${logId}`, { method: 'DELETE' })
}

export function disposePlant(plantId: number, input: DisposalInput): Promise<Plant> {
  return apiFetch<Plant>(`/plants/${plantId}/dispose`, {
    method: 'POST',
    body: JSON.stringify(input),
  })
}

export function markNotEmerged(plantId: number): Promise<Plant> {
  return apiFetch<Plant>(`/plants/${plantId}/not-emerged`, { method: 'POST' })
}
