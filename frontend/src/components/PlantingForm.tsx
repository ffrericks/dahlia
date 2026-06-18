import { useEffect, useState } from 'react'
import type { Location, LocationKind } from '../api/locations'
import { listLocations } from '../api/locations'
import type { PlantingInput } from '../api/plantings'
import { createPlanting } from '../api/plantings'
import { todayISO } from '../dates'

interface Props {
  plantId: number
  onDone: () => void
  onCancel: () => void
  // Reused for "stek uitplanten": override the title/button and the save action.
  title?: string
  submitLabel?: string
  onSubmit?: (input: PlantingInput) => Promise<unknown>
}

export default function PlantingForm({
  plantId,
  onDone,
  onCancel,
  title = 'Plant op een plek',
  submitLabel = 'Planten',
  onSubmit,
}: Props) {
  const [mode, setMode] = useState<'existing' | 'new'>('existing')
  const [locationId, setLocationId] = useState<number | ''>('')
  const [newKind, setNewKind] = useState<LocationKind>('garden')
  const [newName, setNewName] = useState('')
  const [position, setPosition] = useState('')
  const [plantedOn, setPlantedOn] = useState(todayISO())

  const [locations, setLocations] = useState<Location[]>([])
  const [error, setError] = useState<string | null>(null)
  const [saving, setSaving] = useState(false)

  useEffect(() => {
    listLocations()
      .then((l) => {
        setLocations(l)
        if (l.length === 0) setMode('new') // no places yet -> create one
      })
      .catch((err) => setError(err instanceof Error ? err.message : String(err)))
  }, [])

  async function submit(event: React.FormEvent) {
    event.preventDefault()
    setError(null)
    setSaving(true)
    try {
      const input: PlantingInput = {
        plant_id: plantId,
        location_id: mode === 'existing' ? Number(locationId) : null,
        new_location_kind: mode === 'new' ? newKind : null,
        new_location_name: mode === 'new' ? newName.trim() || null : null,
        position: position.trim() || null,
        planted_on: plantedOn,
      }
      await (onSubmit ? onSubmit(input) : createPlanting(input))
      onDone()
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err))
      setSaving(false)
    }
  }

  return (
    <form onSubmit={submit} className="flex flex-col gap-3 rounded-lg border border-stone-200 bg-stone-50 p-4">
      <h4 className="font-medium">{title}</h4>

      <div className="flex gap-4 text-sm">
        <label className="flex items-center gap-1">
          <input
            type="radio"
            checked={mode === 'existing'}
            onChange={() => setMode('existing')}
            disabled={locations.length === 0}
          />
          Bestaande plek
        </label>
        <label className="flex items-center gap-1">
          <input type="radio" checked={mode === 'new'} onChange={() => setMode('new')} />
          Nieuwe plek
        </label>
      </div>

      {mode === 'existing' ? (
        <select
          value={locationId}
          onChange={(e) => setLocationId(e.target.value ? Number(e.target.value) : '')}
          required
          className="rounded-lg border border-stone-300 px-3 py-2"
        >
          <option value="">— Kies een plek —</option>
          {locations.map((loc) => (
            <option key={loc.id} value={loc.id}>
              {loc.code} · {loc.label}
              {loc.name ? ` — ${loc.name}` : ''}
            </option>
          ))}
        </select>
      ) : (
        <div className="flex flex-col gap-2 sm:flex-row">
          <select
            value={newKind}
            onChange={(e) => setNewKind(e.target.value as LocationKind)}
            className="rounded-lg border border-stone-300 px-3 py-2"
          >
            <option value="garden">Tuin (plek)</option>
            <option value="container">Pot / bak</option>
          </select>
          <input
            value={newName}
            onChange={(e) => setNewName(e.target.value)}
            placeholder="Naam (optioneel)"
            className="flex-1 rounded-lg border border-stone-300 px-3 py-2"
          />
        </div>
      )}

      <input
        value={position}
        onChange={(e) => setPosition(e.target.value)}
        placeholder="Plek in de bak (optioneel, bijv. voor/achter)"
        className="rounded-lg border border-stone-300 px-3 py-2"
      />

      <label className="flex flex-col gap-1">
        <span className="text-sm text-stone-500">Plantdatum</span>
        <input
          type="date"
          value={plantedOn}
          onChange={(e) => setPlantedOn(e.target.value)}
          className="rounded-lg border border-stone-300 px-3 py-2"
        />
      </label>

      {error && <p className="text-sm text-red-600">{error}</p>}

      <div className="flex gap-2">
        <button
          type="submit"
          disabled={saving}
          className="rounded-lg bg-emerald-600 px-4 py-2 text-sm font-medium text-white hover:bg-emerald-700 disabled:opacity-40"
        >
          {saving ? 'Bezig…' : submitLabel}
        </button>
        <button
          type="button"
          onClick={onCancel}
          className="rounded-lg border border-stone-300 px-4 py-2 text-sm font-medium text-stone-600 hover:bg-stone-100"
        >
          Annuleren
        </button>
      </div>
    </form>
  )
}
