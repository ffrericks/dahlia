import { useEffect, useState } from 'react'
import type { Location, LocationDetail, LocationKind } from '../api/locations'
import {
  createLocation,
  deleteLocation,
  getLocation,
  listLocations,
} from '../api/locations'

export default function Locations() {
  const [locations, setLocations] = useState<Location[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [detail, setDetail] = useState<LocationDetail | null>(null)

  // New-location form
  const [kind, setKind] = useState<LocationKind>('garden')
  const [name, setName] = useState('')

  async function refresh() {
    setLoading(true)
    setError(null)
    try {
      setLocations(await listLocations())
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err))
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    refresh()
  }, [])

  async function add(event: React.FormEvent) {
    event.preventDefault()
    setError(null)
    try {
      await createLocation(kind, name)
      setName('')
      await refresh()
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err))
    }
  }

  async function openDetail(id: number) {
    setError(null)
    try {
      setDetail(await getLocation(id))
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err))
    }
  }

  async function remove(loc: Location) {
    if (!window.confirm(`Plek ${loc.code} verwijderen?`)) return
    try {
      await deleteLocation(loc.id)
      await refresh()
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err))
    }
  }

  if (detail) {
    return (
      <div className="flex flex-col gap-4">
        <button
          onClick={() => setDetail(null)}
          className="self-start text-sm text-emerald-700 hover:underline"
        >
          ← Terug naar plekken
        </button>
        <header>
          <h2 className="font-mono text-2xl font-semibold">{detail.code}</h2>
          <p className="text-stone-500">
            {detail.label}
            {detail.name ? ` — ${detail.name}` : ''}
          </p>
        </header>
        <section className="rounded-xl border border-stone-200 bg-white p-4 shadow-sm">
          <h3 className="mb-2 text-sm font-medium uppercase tracking-wide text-stone-400">
            Planten hier ({detail.plants.length})
          </h3>
          {detail.plants.length === 0 ? (
            <p className="text-sm text-stone-400">Op dit moment staat hier niets.</p>
          ) : (
            <ul className="flex flex-col gap-1 text-sm">
              {detail.plants.map((p) => (
                <li key={p.plant_id}>
                  <span className="font-mono font-medium">{p.full_code}</span>
                  {p.variety_name ? ` — ${p.variety_name}` : ''}
                  {p.position ? <span className="text-stone-500"> ({p.position})</span> : ''}
                </li>
              ))}
            </ul>
          )}
        </section>
      </div>
    )
  }

  return (
    <div className="flex flex-col gap-4">
      <h2 className="text-lg font-semibold">Plekken</h2>

      <form
        onSubmit={add}
        className="flex flex-col gap-2 rounded-xl border border-stone-200 bg-white p-4 shadow-sm sm:flex-row"
      >
        <select
          value={kind}
          onChange={(e) => setKind(e.target.value as LocationKind)}
          className="rounded-lg border border-stone-300 px-3 py-2"
        >
          <option value="garden">Tuin (plek)</option>
          <option value="container">Pot / bak</option>
        </select>
        <input
          value={name}
          onChange={(e) => setName(e.target.value)}
          placeholder="Naam (optioneel)"
          className="flex-1 rounded-lg border border-stone-300 px-3 py-2"
        />
        <button
          type="submit"
          className="rounded-lg bg-emerald-600 px-4 py-2 font-medium text-white hover:bg-emerald-700"
        >
          + Plek toevoegen
        </button>
      </form>

      {error && <p className="text-sm text-red-600">{error}</p>}
      {loading && <p className="text-stone-500">Laden…</p>}

      {!loading && locations.length === 0 && (
        <p className="rounded-xl border border-dashed border-stone-300 p-8 text-center text-stone-500">
          Nog geen plekken. Voeg een tuinplek of een pot/bak toe.
        </p>
      )}

      <ul className="flex flex-col gap-2">
        {locations.map((loc) => (
          <li
            key={loc.id}
            className="flex items-center gap-3 rounded-xl border border-stone-200 bg-white p-3 shadow-sm"
          >
            <span className="rounded-md bg-stone-800 px-2 py-1 font-mono text-sm font-semibold text-white">
              {loc.code}
            </span>
            <button
              onClick={() => openDetail(loc.id)}
              className="min-w-0 flex-1 text-left hover:underline"
            >
              <span className="font-medium">{loc.label}</span>
              {loc.name ? ` — ${loc.name}` : ''}
              <span className="text-stone-400">
                {' '}· {loc.active_count} {loc.active_count === 1 ? 'plant' : 'planten'}
              </span>
            </button>
            {loc.active_count === 0 && (
              <button
                onClick={() => remove(loc)}
                className="shrink-0 rounded-lg border border-red-200 px-3 py-1.5 text-sm font-medium text-red-600 hover:bg-red-50"
              >
                Verwijderen
              </button>
            )}
          </li>
        ))}
      </ul>
    </div>
  )
}
