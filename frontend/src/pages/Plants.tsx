import { useEffect, useState } from 'react'
import type { Plant, PlantCreateInput, Summary } from '../api/plants'
import { createPlant, getSummary, listPlants, searchPlants } from '../api/plants'
import BarcodeScanner, { scannerSupported } from '../components/BarcodeScanner'
import CareTips from '../components/CareTips'
import PlantDetail from '../components/PlantDetail'
import PlantForm from '../components/PlantForm'
import { ORIGIN_LABELS, stateLabel } from '../labels'

type View = { mode: 'list' } | { mode: 'new' } | { mode: 'detail'; id: number }

export default function Plants() {
  const [plants, setPlants] = useState<Plant[]>([])
  const [summary, setSummary] = useState<Summary | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [view, setView] = useState<View>({ mode: 'list' })
  const [showGone, setShowGone] = useState(false)

  const [query, setQuery] = useState('')
  const [results, setResults] = useState<Plant[]>([])
  const [scanning, setScanning] = useState(false)

  async function refresh() {
    setLoading(true)
    setError(null)
    try {
      const [p, s] = await Promise.all([listPlants(showGone), getSummary()])
      setPlants(p)
      setSummary(s)
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err))
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    refresh()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [showGone])

  // Live search by code / storage code / nickname.
  useEffect(() => {
    const q = query.trim()
    if (!q) {
      setResults([])
      return
    }
    let cancelled = false
    searchPlants(q)
      .then((r) => {
        if (!cancelled) setResults(r)
      })
      .catch((err) => setError(err instanceof Error ? err.message : String(err)))
    return () => {
      cancelled = true
    }
  }, [query])

  async function save(input: PlantCreateInput) {
    await createPlant(input)
    setView({ mode: 'list' })
    await refresh()
  }

  if (view.mode === 'new') {
    return <PlantForm onSave={save} onCancel={() => setView({ mode: 'list' })} />
  }
  if (view.mode === 'detail') {
    return (
      <PlantDetail
        plantId={view.id}
        onBack={() => setView({ mode: 'list' })}
        onNavigate={(id) => setView({ mode: 'detail', id })}
        onChanged={refresh}
      />
    )
  }

  const open = (id: number) => setView({ mode: 'detail', id })
  const searching = query.trim().length > 0

  return (
    <div className="flex flex-col gap-4">
      <CareTips />

      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold">Planten</h2>
        <button
          onClick={() => setView({ mode: 'new' })}
          className="rounded-lg bg-emerald-600 px-4 py-2 font-medium text-white hover:bg-emerald-700"
        >
          + Nieuwe plant
        </button>
      </div>

      {/* Search by flower ID (BUM01000) or storage ID (BUM01000D0126) */}
      <div className="flex gap-2">
        <input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Zoek op code, opslag-ID of bijnaam…"
          className="flex-1 rounded-lg border border-stone-300 px-3 py-2"
        />
        {query && (
          <button
            onClick={() => setQuery('')}
            className="rounded-lg border border-stone-300 px-3 py-2 text-sm text-stone-600 hover:bg-stone-100"
          >
            Wissen
          </button>
        )}
        {scannerSupported && (
          <button
            onClick={() => setScanning((v) => !v)}
            className="rounded-lg border border-emerald-600 px-3 py-2 text-sm font-medium text-emerald-700 hover:bg-emerald-50"
          >
            📷 Scan
          </button>
        )}
      </div>

      {scanning && (
        <BarcodeScanner
          onScan={(value) => {
            setQuery(value)
            setScanning(false)
          }}
          onClose={() => setScanning(false)}
        />
      )}

      {error && <p className="text-sm text-red-600">{error}</p>}

      {searching ? (
        <>
          <p className="text-sm text-stone-500">
            {results.length} resultaat{results.length === 1 ? '' : 'en'} voor "{query.trim()}"
          </p>
          <ul className="flex flex-col gap-2">
            {results.map((plant) => (
              <PlantRow key={plant.id} plant={plant} onClick={() => open(plant.id)} />
            ))}
          </ul>
        </>
      ) : (
        <>
          {summary && summary.total > 0 && (
            <div className="flex flex-wrap gap-2 text-sm">
              <Badge label={`Totaal: ${summary.total}`} />
              {Object.entries(summary.by_state).map(([state, count]) => (
                <Badge key={state} label={`${stateLabel(state)}: ${count}`} />
              ))}
            </div>
          )}

          <label className="flex items-center gap-2 text-sm text-stone-500">
            <input
              type="checkbox"
              checked={showGone}
              onChange={(e) => setShowGone(e.target.checked)}
            />
            Toon ook weggegooid/weggegeven
          </label>

          {loading && <p className="text-stone-500">Laden…</p>}

          {!loading && plants.length === 0 && (
            <p className="rounded-xl border border-dashed border-stone-300 p-8 text-center text-stone-500">
              Nog geen planten. Voeg je eerste plant toe (gekocht, gekregen, afsplitsing of
              zaailing).
            </p>
          )}

          <ul className="flex flex-col gap-2">
            {plants.map((plant) => (
              <PlantRow key={plant.id} plant={plant} onClick={() => open(plant.id)} />
            ))}
          </ul>
        </>
      )}
    </div>
  )
}

function PlantRow({ plant, onClick }: { plant: Plant; onClick: () => void }) {
  // Where to physically find it: storage box, else its current location.
  const locator = plant.storage?.box_code ?? plant.location?.code ?? null
  const gone = plant.state === 'discarded' || plant.state === 'given_away'
  return (
    <li>
      <button
        onClick={onClick}
        className={`flex w-full items-center gap-3 rounded-xl border border-stone-200 bg-white p-3 text-left shadow-sm hover:bg-stone-50 ${
          gone ? 'opacity-50' : ''
        }`}
      >
        {plant.thumbnail ? (
          <img src={plant.thumbnail} alt="" className="h-12 w-12 shrink-0 rounded-md object-cover" />
        ) : (
          <span className="h-12 w-12 shrink-0 rounded-md bg-stone-100" />
        )}
        <div className="min-w-0 flex-1">
          <p className="font-mono font-medium">{plant.label}</p>
          <p className="text-sm text-stone-500">
            {plant.variety_name ?? (plant.variety_id ? 'naamloos' : 'nog geen soort')} ·{' '}
            {ORIGIN_LABELS[plant.origin]}
            {locator && <span className="font-mono text-stone-400"> · {locator}</span>}
          </p>
          {plant.last_fertilized && (
            <p className="text-xs text-stone-400">🌿 bemest {plant.last_fertilized}</p>
          )}
        </div>
        <span className="shrink-0 rounded-full bg-stone-100 px-2 py-1 text-xs text-stone-600">
          {stateLabel(plant.state)}
        </span>
      </button>
    </li>
  )
}

function Badge({ label }: { label: string }) {
  return <span className="rounded-full bg-stone-100 px-3 py-1 text-stone-600">{label}</span>
}
