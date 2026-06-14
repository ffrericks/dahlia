import { useEffect, useState } from 'react'
import type { Plant } from '../api/plants'
import { listPlants, setEyeStatus } from '../api/plants'
import type { SeasonStatus } from '../api/season'
import { getSeasonStatus, startNewSeason } from '../api/season'
import type { StorageBox } from '../api/storage'
import { getStorageBoxes } from '../api/storage'
import { EYE_STATUS_LABELS, eyeStatusLabel } from '../labels'

export default function Storage() {
  const [boxes, setBoxes] = useState<StorageBox[]>([])
  const [stored, setStored] = useState<Plant[]>([])
  const [season, setSeason] = useState<SeasonStatus | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)

  async function refresh() {
    setLoading(true)
    setError(null)
    try {
      const [b, plants, s] = await Promise.all([
        getStorageBoxes(),
        listPlants(),
        getSeasonStatus(),
      ])
      setBoxes(b)
      setStored(plants.filter((p) => p.state === 'stored'))
      setSeason(s)
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err))
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    refresh()
  }, [])

  async function newSeason() {
    if (!window.confirm('Een nieuw seizoen starten?')) return
    try {
      const { resumed } = await startNewSeason()
      window.alert(`Nieuw seizoen gestart. ${resumed} plant(en) hervat.`)
      await refresh()
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err))
    }
  }

  async function changeEye(plantId: number, status: string) {
    try {
      await setEyeStatus(plantId, status)
      await refresh()
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err))
    }
  }

  return (
    <div className="flex flex-col gap-5">
      <h2 className="text-lg font-semibold">Opslag &amp; winter</h2>
      {error && <p className="text-sm text-red-600">{error}</p>}
      {loading && <p className="text-stone-500">Laden…</p>}

      {/* Season rollover */}
      {season && (
        <section className="flex flex-col gap-2 rounded-xl border border-stone-200 bg-white p-4 shadow-sm">
          <h3 className="text-sm font-medium uppercase tracking-wide text-stone-400">
            Nieuw seizoen
          </h3>
          {season.can_start_new ? (
            <p className="text-sm text-stone-600">
              Geen planten meer in de grond. Je kunt een nieuw seizoen starten.
              {season.survived_count > 0 &&
                ` ${season.survived_count} plant(en) overleefden de winter en hervatten.`}
            </p>
          ) : (
            <p className="text-sm text-stone-600">
              Nog niet mogelijk: deze planten staan nog geplant. Rooi ze of markeer ze als
              'winter overleefd'.
            </p>
          )}
          {season.blocking.length > 0 && (
            <ul className="flex flex-wrap gap-2">
              {season.blocking.map((b) => (
                <li key={b.id} className="rounded-full bg-stone-100 px-3 py-1 font-mono text-sm">
                  {b.full_code}
                </li>
              ))}
            </ul>
          )}
          <button
            onClick={newSeason}
            disabled={!season.can_start_new}
            className="self-start rounded-lg bg-emerald-600 px-4 py-2 text-sm font-medium text-white hover:bg-emerald-700 disabled:opacity-40"
          >
            Nieuw seizoen starten
          </button>
        </section>
      )}

      {/* Storage boxes */}
      <section className="flex flex-col gap-3">
        <h3 className="text-sm font-medium uppercase tracking-wide text-stone-400">Dozen</h3>
        {boxes.length === 0 ? (
          <p className="text-sm text-stone-400">Geen dozen in gebruik.</p>
        ) : (
          boxes.map((box) => (
            <div key={box.id} className="rounded-xl border border-stone-200 bg-white p-4 shadow-sm">
              <p className="font-mono font-semibold">{box.code}</p>
              <ul className="mt-1 flex flex-col gap-0.5 text-sm text-stone-600">
                {box.plants.map((p) => (
                  <li key={p.plant_id}>
                    <span className="font-mono">{p.full_code}</span>
                    {p.variety_name ? ` — ${p.variety_name}` : ''} ·{' '}
                    {eyeStatusLabel(p.eye_status)}
                  </li>
                ))}
              </ul>
            </div>
          ))
        )}
      </section>

      {/* Stored tubers: spring eye-check overview */}
      <section className="flex flex-col gap-3">
        <h3 className="text-sm font-medium uppercase tracking-wide text-stone-400">
          Knollen in opslag — oog-check
        </h3>
        {stored.length === 0 ? (
          <p className="text-sm text-stone-400">Geen knollen in opslag.</p>
        ) : (
          stored.map((plant) => (
            <div
              key={plant.id}
              className="flex flex-col gap-2 rounded-xl border border-stone-200 bg-white p-3 shadow-sm sm:flex-row sm:items-center sm:justify-between"
            >
              <span className="font-mono font-medium">
                {plant.full_code}
                {plant.storage && (
                  <span className="ml-2 text-stone-400">{plant.storage.box_code}</span>
                )}
              </span>
              <div className="flex flex-wrap gap-2">
                {Object.entries(EYE_STATUS_LABELS).map(([value, label]) => (
                  <button
                    key={value}
                    onClick={() => changeEye(plant.id, value)}
                    className={`rounded-lg border px-2.5 py-1 text-xs font-medium ${
                      plant.eye_status === value
                        ? 'border-emerald-600 bg-emerald-50 text-emerald-700'
                        : 'border-stone-300 text-stone-500 hover:bg-stone-100'
                    }`}
                  >
                    {label}
                  </button>
                ))}
              </div>
            </div>
          ))
        )}
      </section>
    </div>
  )
}
