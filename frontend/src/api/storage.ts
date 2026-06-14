import { apiFetch } from './client'

export interface StorageBoxPlant {
  plant_id: number
  full_code: string
  variety_name: string | null
  eye_status: string | null
}

export interface StorageBox {
  id: number
  number: number
  year: number
  code: string
  plants: StorageBoxPlant[]
}

export function getStorageBoxes(): Promise<StorageBox[]> {
  return apiFetch<StorageBox[]>('/storage-boxes')
}
