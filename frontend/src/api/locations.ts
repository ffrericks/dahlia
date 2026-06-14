import { apiFetch } from './client'

export type LocationKind = 'garden' | 'container'

export interface Location {
  id: number
  kind: LocationKind
  code: string
  name: string | null
  label: string // tuin | pot | bak
  active_count: number
}

export interface LocationPlant {
  plant_id: number
  full_code: string
  variety_name: string | null
  position: string | null
}

export interface LocationDetail extends Location {
  plants: LocationPlant[]
}

export function listLocations(): Promise<Location[]> {
  return apiFetch<Location[]>('/locations')
}

export function getLocation(id: number): Promise<LocationDetail> {
  return apiFetch<LocationDetail>(`/locations/${id}`)
}

export function createLocation(kind: LocationKind, name?: string | null): Promise<Location> {
  return apiFetch<Location>('/locations', {
    method: 'POST',
    body: JSON.stringify({ kind, name: name?.trim() || null }),
  })
}

export function updateLocation(id: number, name: string | null): Promise<Location> {
  return apiFetch<Location>(`/locations/${id}`, {
    method: 'PATCH',
    body: JSON.stringify({ name: name?.trim() || null }),
  })
}

export function deleteLocation(id: number): Promise<void> {
  return apiFetch<void>(`/locations/${id}`, { method: 'DELETE' })
}
