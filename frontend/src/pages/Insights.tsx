import { useEffect, useState } from 'react'
import type { LocationScore, Weights } from '../api/insights'
import { getLocationRanking } from '../api/insights'

export default function Insights() {
  const [weights, setWeights] = useState<Weights>({ height: 1, flowers: 1, harvested: 1 })
  const [rows, setRows] = useState<LocationScore[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    setLoading(true)
    getLocationRanking(weights)
      .then((r) => setRows(r.locations))
      .catch((err) => setError(err instanceof Error ? err.message : String(err)))
      .finally(() => setLoading(false))
  }, [weights])

  function setWeight(key: keyof Weights, value: number) {
    setWeights((w) => ({ ...w, [key]: value }))
  }

  return (
    <div className="flex flex-col gap-4">
      <h2 className="text-lg font-semibold">Beste plek</h2>
      <p className="text-sm text-stone-500">
        Welke plek of bak gaf de beste groei? De score combineert hoogte, aantal bloemen en
        geoogste bloemen. Schuif het gewicht naar wat jij belangrijk vindt (0 = telt niet mee).
      </p>

      <section className="grid gap-3 rounded-xl border border-stone-200 bg-white p-4 shadow-sm sm:grid-cols-3">
        <WeightControl label="Hoogte" value={weights.height} onChange={(v) => setWeight('height', v)} />
        <WeightControl label="Bloemen" value={weights.flowers} onChange={(v) => setWeight('flowers', v)} />
        <WeightControl label="Geoogst" value={weights.harvested} onChange={(v) => setWeight('harvested', v)} />
      </section>

      {error && <p className="text-sm text-red-600">{error}</p>}
      {loading && <p className="text-stone-500">Laden…</p>}

      {!loading && rows.length === 0 && (
        <p className="rounded-xl border border-dashed border-stone-300 p-8 text-center text-stone-500">
          Nog geen gegevens. Zet planten op een plek en houd in het logboek hoogte en bloemen bij.
        </p>
      )}

      <ol className="flex flex-col gap-2">
        {rows.map((row, i) => (
          <li
            key={row.location_id}
            className="flex items-center gap-3 rounded-xl border border-stone-200 bg-white p-4 shadow-sm"
          >
            <span className="w-6 text-center text-lg font-semibold text-stone-400">{i + 1}</span>
            <div className="min-w-0 flex-1">
              <p className="font-medium">
                <span className="font-mono">{row.code}</span> · {row.label}
                {row.name ? ` — ${row.name}` : ''}
              </p>
              <p className="text-sm text-stone-500">
                {row.avg_height} cm · {row.avg_flowers} bloemen · {row.avg_harvested} geoogst ·{' '}
                {row.plantings} plant(en)
              </p>
            </div>
            <span className="shrink-0 rounded-full bg-emerald-100 px-3 py-1 font-semibold text-emerald-800">
              {row.score}
            </span>
          </li>
        ))}
      </ol>
    </div>
  )
}

function WeightControl({
  label,
  value,
  onChange,
}: {
  label: string
  value: number
  onChange: (v: number) => void
}) {
  return (
    <label className="flex flex-col gap-1">
      <span className="text-sm font-medium text-stone-600">
        {label}: {value}
      </span>
      <input
        type="range"
        min={0}
        max={3}
        step={1}
        value={value}
        onChange={(e) => onChange(Number(e.target.value))}
        className="accent-emerald-600"
      />
    </label>
  )
}
