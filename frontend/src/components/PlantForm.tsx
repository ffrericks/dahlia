import { useEffect, useState } from 'react'
import type { Origin, Plant, PlantCreateInput } from '../api/plants'
import { listPlants } from '../api/plants'
import type { Variety } from '../api/varieties'
import { listVarieties } from '../api/varieties'
import { ORIGIN_LABELS } from '../labels'

interface Props {
  onSave: (input: PlantCreateInput) => Promise<void>
  onCancel: () => void
}

const ORIGINS: Origin[] = ['purchased', 'gifted', 'split', 'seedling', 'unknown']

export default function PlantForm({ onSave, onCancel }: Props) {
  const [origin, setOrigin] = useState<Origin>('purchased')
  // For purchased/gifted: use an existing variety or create a new one.
  const [varietyMode, setVarietyMode] = useState<'existing' | 'new'>('existing')
  const [varietyId, setVarietyId] = useState<number | ''>('')
  const [parentId, setParentId] = useState<number | ''>('')
  const [newCode, setNewCode] = useState('')
  const [newName, setNewName] = useState('')
  const [nickname, setNickname] = useState('')

  const [varieties, setVarieties] = useState<Variety[]>([])
  const [plants, setPlants] = useState<Plant[]>([])
  const [error, setError] = useState<string | null>(null)
  const [saving, setSaving] = useState(false)

  useEffect(() => {
    Promise.all([listVarieties(), listPlants()])
      .then(([v, p]) => {
        setVarieties(v)
        setPlants(p)
      })
      .catch((err) => setError(err instanceof Error ? err.message : String(err)))
  }, [])

  const needsParent = origin === 'split' || origin === 'seedling'
  const choosesVariety = origin === 'purchased' || origin === 'gifted'
  const needsNewVariety = origin === 'seedling' || (choosesVariety && varietyMode === 'new')
  const needsExistingVariety = choosesVariety && varietyMode === 'existing'

  async function submit(event: React.FormEvent) {
    event.preventDefault()
    setError(null)
    setSaving(true)
    try {
      const input: PlantCreateInput = { origin, nickname: nickname.trim() || null }
      if (needsParent) input.parent_plant_id = Number(parentId)
      if (needsExistingVariety) input.variety_id = Number(varietyId)
      if (needsNewVariety) {
        input.new_variety_code = newCode
        input.new_variety_name = newName.trim() || null
      }
      await onSave(input)
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err))
      setSaving(false)
    }
  }

  function plantLabel(p: Plant) {
    return `${p.label}${p.variety_name ? ` — ${p.variety_name}` : ''}`
  }

  // A split/seedling mother must already have a variety (and thus a number).
  const parentOptions = plants.filter((p) => p.full_code !== null)

  return (
    <form
      onSubmit={submit}
      className="flex flex-col gap-4 rounded-xl border border-stone-200 bg-white p-5 shadow-sm"
    >
      <h2 className="text-lg font-semibold">Nieuwe plant</h2>

      <label className="flex flex-col gap-1">
        <span className="text-sm font-medium text-stone-600">Herkomst</span>
        <select
          value={origin}
          onChange={(e) => setOrigin(e.target.value as Origin)}
          className="rounded-lg border border-stone-300 px-3 py-2"
        >
          {ORIGINS.map((o) => (
            <option key={o} value={o}>
              {ORIGIN_LABELS[o]}
            </option>
          ))}
        </select>
      </label>

      {needsParent && (
        <label className="flex flex-col gap-1">
          <span className="text-sm font-medium text-stone-600">
            Moederplant {origin === 'seedling' && '(zaailing komt hiervan)'}
          </span>
          <select
            value={parentId}
            onChange={(e) => setParentId(e.target.value ? Number(e.target.value) : '')}
            required
            className="rounded-lg border border-stone-300 px-3 py-2"
          >
            <option value="">— Kies een plant —</option>
            {parentOptions.map((p) => (
              <option key={p.id} value={p.id}>
                {plantLabel(p)}
              </option>
            ))}
          </select>
        </label>
      )}

      {choosesVariety && (
        <div className="flex flex-col gap-2">
          <span className="text-sm font-medium text-stone-600">Soort</span>
          <div className="flex gap-4 text-sm">
            <label className="flex items-center gap-1">
              <input
                type="radio"
                checked={varietyMode === 'existing'}
                onChange={() => setVarietyMode('existing')}
              />
              Bestaande soort
            </label>
            <label className="flex items-center gap-1">
              <input
                type="radio"
                checked={varietyMode === 'new'}
                onChange={() => setVarietyMode('new')}
              />
              Nieuwe soort
            </label>
          </div>
          {varietyMode === 'existing' && (
            <select
              value={varietyId}
              onChange={(e) => setVarietyId(e.target.value ? Number(e.target.value) : '')}
              required
              className="rounded-lg border border-stone-300 px-3 py-2"
            >
              <option value="">— Kies een soort —</option>
              {varieties.map((v) => (
                <option key={v.id} value={v.id}>
                  {v.code}
                  {v.name ? ` — ${v.name}` : ''}
                </option>
              ))}
            </select>
          )}
        </div>
      )}

      {needsNewVariety && (
        <div className="grid gap-4 sm:grid-cols-[8rem_1fr]">
          <label className="flex flex-col gap-1">
            <span className="text-sm font-medium text-stone-600">Nieuwe code (3 letters)</span>
            <input
              value={newCode}
              onChange={(e) => setNewCode(e.target.value.toUpperCase())}
              maxLength={3}
              required
              className="rounded-lg border border-stone-300 px-3 py-2 uppercase tracking-widest"
              placeholder="ZAA"
            />
          </label>
          <label className="flex flex-col gap-1">
            <span className="text-sm font-medium text-stone-600">Naam (optioneel)</span>
            <input
              value={newName}
              onChange={(e) => setNewName(e.target.value)}
              className="rounded-lg border border-stone-300 px-3 py-2"
              placeholder="Nog naamloos"
            />
          </label>
        </div>
      )}

      <label className="flex flex-col gap-1">
        <span className="text-sm font-medium text-stone-600">
          Bijnaam {origin === 'unknown' ? '(bijv. "Links")' : '(optioneel)'}
        </span>
        <input
          value={nickname}
          onChange={(e) => setNickname(e.target.value)}
          className="rounded-lg border border-stone-300 px-3 py-2"
          placeholder={origin === 'unknown' ? 'Links' : ''}
        />
        {origin === 'unknown' && (
          <span className="text-xs text-stone-400">
            Nog geen soort bekend — je kunt later een soort toewijzen als je het weet.
          </span>
        )}
      </label>

      {error && <p className="text-sm text-red-600">{error}</p>}

      <div className="flex gap-2">
        <button
          type="submit"
          disabled={saving}
          className="rounded-lg bg-emerald-600 px-4 py-2 font-medium text-white hover:bg-emerald-700 disabled:opacity-40"
        >
          {saving ? 'Opslaan…' : 'Plant toevoegen'}
        </button>
        <button
          type="button"
          onClick={onCancel}
          className="rounded-lg border border-stone-300 px-4 py-2 font-medium text-stone-600 hover:bg-stone-100"
        >
          Annuleren
        </button>
      </div>
    </form>
  )
}
