import { useEffect, useState } from 'react'
import { assignVariety } from '../api/plants'
import type { Variety } from '../api/varieties'
import { listVarieties } from '../api/varieties'

interface Props {
  plantId: number
  onDone: () => void
}

export default function AssignVarietyForm({ plantId, onDone }: Props) {
  const [mode, setMode] = useState<'existing' | 'new'>('existing')
  const [varieties, setVarieties] = useState<Variety[]>([])
  const [varietyId, setVarietyId] = useState<number | ''>('')
  const [code, setCode] = useState('')
  const [name, setName] = useState('')
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    listVarieties()
      .then((v) => {
        setVarieties(v)
        if (v.length === 0) setMode('new')
      })
      .catch((err) => setError(err instanceof Error ? err.message : String(err)))
  }, [])

  async function submit(event: React.FormEvent) {
    event.preventDefault()
    setError(null)
    try {
      await assignVariety(
        plantId,
        mode === 'existing'
          ? { variety_id: Number(varietyId) }
          : { new_variety_code: code, new_variety_name: name.trim() || null },
      )
      onDone()
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err))
    }
  }

  return (
    <form onSubmit={submit} className="flex flex-col gap-2 rounded-lg bg-stone-50 p-3">
      <p className="text-sm text-stone-500">Nog geen soort. Wijs er een toe als je weet wat het is:</p>
      <div className="flex gap-4 text-sm">
        <label className="flex items-center gap-1">
          <input
            type="radio"
            checked={mode === 'existing'}
            onChange={() => setMode('existing')}
            disabled={varieties.length === 0}
          />
          Bestaande soort
        </label>
        <label className="flex items-center gap-1">
          <input type="radio" checked={mode === 'new'} onChange={() => setMode('new')} />
          Nieuwe soort
        </label>
      </div>

      {mode === 'existing' ? (
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
      ) : (
        <div className="flex flex-col gap-2 sm:flex-row">
          <input
            value={code}
            onChange={(e) => setCode(e.target.value.toUpperCase())}
            maxLength={3}
            required
            placeholder="Code (3 letters)"
            className="w-40 rounded-lg border border-stone-300 px-3 py-2 uppercase tracking-widest"
          />
          <input
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="Naam (optioneel)"
            className="flex-1 rounded-lg border border-stone-300 px-3 py-2"
          />
        </div>
      )}

      {error && <p className="text-sm text-red-600">{error}</p>}
      <button
        type="submit"
        className="self-start rounded-lg bg-emerald-600 px-4 py-2 text-sm font-medium text-white hover:bg-emerald-700"
      >
        Soort toewijzen
      </button>
    </form>
  )
}
