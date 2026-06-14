import { useEffect, useState } from 'react'
import type { Variety, VarietyInput } from '../api/varieties'
import {
  createVariety,
  deleteVariety,
  listVarieties,
  updateVariety,
} from '../api/varieties'
import VarietyForm from '../components/VarietyForm'

// 'list' | 'new' | the variety being edited
type View = { mode: 'list' } | { mode: 'new' } | { mode: 'edit'; variety: Variety }

export default function Varieties() {
  const [varieties, setVarieties] = useState<Variety[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [view, setView] = useState<View>({ mode: 'list' })

  async function refresh() {
    setLoading(true)
    setError(null)
    try {
      setVarieties(await listVarieties())
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err))
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    refresh()
  }, [])

  async function save(input: VarietyInput) {
    if (view.mode === 'edit') {
      await updateVariety(view.variety.id, input)
    } else {
      await createVariety(input)
    }
    setView({ mode: 'list' })
    await refresh()
  }

  async function remove(variety: Variety) {
    if (!window.confirm(`Soort ${variety.code} (${variety.name}) verwijderen?`)) return
    try {
      await deleteVariety(variety.id)
      await refresh()
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err))
    }
  }

  if (view.mode === 'new') {
    return <VarietyForm onSave={save} onCancel={() => setView({ mode: 'list' })} />
  }
  if (view.mode === 'edit') {
    return (
      <VarietyForm
        existing={view.variety}
        onSave={save}
        onCancel={() => setView({ mode: 'list' })}
      />
    )
  }

  return (
    <div className="flex flex-col gap-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold">Soorten</h2>
        <button
          onClick={() => setView({ mode: 'new' })}
          className="rounded-lg bg-emerald-600 px-4 py-2 font-medium text-white hover:bg-emerald-700"
        >
          + Nieuwe soort
        </button>
      </div>

      {error && <p className="text-sm text-red-600">{error}</p>}
      {loading && <p className="text-stone-500">Laden…</p>}

      {!loading && varieties.length === 0 && (
        <p className="rounded-xl border border-dashed border-stone-300 p-8 text-center text-stone-500">
          Nog geen soorten. Voeg je eerste dahlia-soort toe.
        </p>
      )}

      <ul className="flex flex-col gap-2">
        {varieties.map((variety) => (
          <li
            key={variety.id}
            className="flex items-start gap-4 rounded-xl border border-stone-200 bg-white p-4 shadow-sm"
          >
            {variety.image_thumbnail ? (
              <img
                src={variety.image_thumbnail}
                alt={variety.name ?? variety.code}
                className="h-14 w-14 shrink-0 rounded-md object-cover"
              />
            ) : (
              <span className="flex h-14 w-14 shrink-0 items-center justify-center rounded-md bg-stone-800 font-mono text-sm font-semibold tracking-widest text-white">
                {variety.code}
              </span>
            )}
            <div className="min-w-0 flex-1">
              <p className="font-medium">
                <span className="mr-2 font-mono text-stone-500">{variety.code}</span>
                {variety.name ?? <span className="italic text-stone-400">naamloos</span>}
              </p>
              <p className="text-sm text-stone-400">
                {variety.plant_count} {variety.plant_count === 1 ? 'plant' : 'planten'}
              </p>
              {variety.description && (
                <p className="mt-1 line-clamp-2 text-sm text-stone-500">
                  {variety.description}
                </p>
              )}
              {variety.wikipedia_url && (
                <a
                  href={variety.wikipedia_url}
                  target="_blank"
                  rel="noreferrer"
                  className="mt-1 inline-block text-sm text-emerald-700 hover:underline"
                >
                  Bron ↗
                </a>
              )}
            </div>
            <div className="flex shrink-0 gap-2">
              <button
                onClick={() => setView({ mode: 'edit', variety })}
                className="rounded-lg border border-stone-300 px-3 py-1.5 text-sm font-medium text-stone-600 hover:bg-stone-100"
              >
                Bewerken
              </button>
              <button
                onClick={() => remove(variety)}
                className="rounded-lg border border-red-200 px-3 py-1.5 text-sm font-medium text-red-600 hover:bg-red-50"
              >
                Verwijderen
              </button>
            </div>
          </li>
        ))}
      </ul>
    </div>
  )
}
