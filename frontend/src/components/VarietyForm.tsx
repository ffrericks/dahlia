import { useState } from 'react'
import type { Variety, VarietyInput } from '../api/varieties'
import { fetchWikipediaExtract } from '../api/varieties'

interface Props {
  // When editing, the existing variety; when adding, undefined.
  existing?: Variety
  onSave: (input: VarietyInput) => Promise<void>
  onCancel: () => void
}

export default function VarietyForm({ existing, onSave, onCancel }: Props) {
  const isEdit = existing !== undefined
  const [code, setCode] = useState(existing?.code ?? '')
  const [name, setName] = useState(existing?.name ?? '')
  const [wikipediaUrl, setWikipediaUrl] = useState(existing?.wikipedia_url ?? '')
  const [description, setDescription] = useState(existing?.description ?? '')
  const [error, setError] = useState<string | null>(null)
  const [importing, setImporting] = useState(false)
  const [saving, setSaving] = useState(false)

  async function importFromWikipedia() {
    setError(null)
    setImporting(true)
    try {
      const { extract } = await fetchWikipediaExtract(wikipediaUrl)
      setDescription(extract)
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err))
    } finally {
      setImporting(false)
    }
  }

  async function submit(event: React.FormEvent) {
    event.preventDefault()
    setError(null)
    setSaving(true)
    try {
      await onSave({
        code,
        name: name.trim() || null,
        description: description.trim() || null,
        wikipedia_url: wikipediaUrl.trim() || null,
      })
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err))
      setSaving(false) // keep the form open so the user can fix the input
    }
  }

  return (
    <form
      onSubmit={submit}
      className="flex flex-col gap-4 rounded-xl border border-stone-200 bg-white p-5 shadow-sm"
    >
      <h2 className="text-lg font-semibold">
        {isEdit ? `Soort ${existing.code} bewerken` : 'Nieuwe soort'}
      </h2>

      <div className="grid gap-4 sm:grid-cols-[8rem_1fr]">
        <label className="flex flex-col gap-1">
          <span className="text-sm font-medium text-stone-600">Code (3 letters)</span>
          <input
            value={code}
            onChange={(e) => setCode(e.target.value.toUpperCase())}
            maxLength={3}
            // Code is the permanent prefix of every plant code, so it can't change after creation.
            disabled={isEdit}
            required
            className="rounded-lg border border-stone-300 px-3 py-2 uppercase tracking-widest disabled:bg-stone-100 disabled:text-stone-500"
            placeholder="WIT"
          />
        </label>

        <label className="flex flex-col gap-1">
          <span className="text-sm font-medium text-stone-600">Naam (optioneel)</span>
          <input
            value={name}
            onChange={(e) => setName(e.target.value)}
            className="rounded-lg border border-stone-300 px-3 py-2"
            placeholder="Witte Dahlia"
          />
        </label>
      </div>

      <label className="flex flex-col gap-1">
        <span className="text-sm font-medium text-stone-600">Wikipedia-link (optioneel)</span>
        <div className="flex flex-col gap-2 sm:flex-row">
          <input
            value={wikipediaUrl}
            onChange={(e) => setWikipediaUrl(e.target.value)}
            type="url"
            className="flex-1 rounded-lg border border-stone-300 px-3 py-2"
            placeholder="https://nl.wikipedia.org/wiki/Dahlia"
          />
          <button
            type="button"
            onClick={importFromWikipedia}
            disabled={!wikipediaUrl.trim() || importing}
            className="rounded-lg border border-emerald-600 px-3 py-2 text-sm font-medium text-emerald-700 hover:bg-emerald-50 disabled:opacity-40"
          >
            {importing ? 'Ophalen…' : 'Haal omschrijving op'}
          </button>
        </div>
      </label>

      <label className="flex flex-col gap-1">
        <span className="text-sm font-medium text-stone-600">Omschrijving</span>
        <textarea
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          rows={5}
          className="rounded-lg border border-stone-300 px-3 py-2"
          placeholder="Vul handmatig in of haal op van Wikipedia. Altijd aanpasbaar."
        />
      </label>

      {error && <p className="text-sm text-red-600">{error}</p>}

      <div className="flex gap-2">
        <button
          type="submit"
          disabled={saving}
          className="rounded-lg bg-emerald-600 px-4 py-2 font-medium text-white hover:bg-emerald-700 disabled:opacity-40"
        >
          {saving ? 'Opslaan…' : 'Opslaan'}
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
