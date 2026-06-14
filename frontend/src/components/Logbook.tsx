import { useState } from 'react'
import type { LogEntry } from '../api/plants'
import { addLog, deleteLog } from '../api/plants'
import { todayISO } from '../dates'

interface Props {
  plantId: number
  logs: LogEntry[]
  onChanged: () => void
}

export default function Logbook({ plantId, logs, onChanged }: Props) {
  const [open, setOpen] = useState(false)
  const [text, setText] = useState('')
  const [height, setHeight] = useState('')
  const [buds, setBuds] = useState('')
  const [flowers, setFlowers] = useState('')
  const [harvested, setHarvested] = useState('')
  const [entryDate, setEntryDate] = useState(todayISO())
  const [error, setError] = useState<string | null>(null)

  const num = (v: string) => (v.trim() === '' ? null : Number(v))

  async function submit(event: React.FormEvent) {
    event.preventDefault()
    setError(null)
    try {
      await addLog(plantId, {
        text: text.trim() || null,
        height_cm: num(height),
        bud_count: num(buds),
        flower_count: num(flowers),
        harvested_count: num(harvested),
        entry_date: entryDate,
      })
      setText('')
      setHeight('')
      setBuds('')
      setFlowers('')
      setHarvested('')
      setEntryDate(todayISO())
      setOpen(false)
      onChanged()
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err))
    }
  }

  async function remove(logId: number) {
    await deleteLog(plantId, logId)
    onChanged()
  }

  return (
    <section className="flex flex-col gap-3 rounded-xl border border-stone-200 bg-white p-4 shadow-sm">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-medium uppercase tracking-wide text-stone-400">Logboek</h3>
        <button
          onClick={() => setOpen((v) => !v)}
          className="rounded-lg border border-emerald-600 px-3 py-1.5 text-sm font-medium text-emerald-700 hover:bg-emerald-50"
        >
          {open ? 'Sluiten' : '+ Notitie'}
        </button>
      </div>

      {open && (
        <form onSubmit={submit} className="flex flex-col gap-2 rounded-lg bg-stone-50 p-3">
          <textarea
            value={text}
            onChange={(e) => setText(e.target.value)}
            rows={2}
            placeholder="Notitie (bijv. getopt, opgebonden…)"
            className="rounded-lg border border-stone-300 px-3 py-2"
          />
          <div className="grid grid-cols-2 gap-2 sm:grid-cols-4">
            <Field label="Hoogte (cm)" value={height} onChange={setHeight} />
            <Field label="Knoppen" value={buds} onChange={setBuds} />
            <Field label="Bloemen" value={flowers} onChange={setFlowers} />
            <Field label="Geoogst" value={harvested} onChange={setHarvested} />
          </div>
          <label className="flex flex-col gap-1 text-xs text-stone-500">
            Datum
            <input
              type="date"
              value={entryDate}
              onChange={(e) => setEntryDate(e.target.value)}
              className="w-44 rounded-lg border border-stone-300 px-2 py-1.5 text-sm text-stone-800"
            />
          </label>
          {error && <p className="text-sm text-red-600">{error}</p>}
          <button
            type="submit"
            className="self-start rounded-lg bg-emerald-600 px-4 py-2 text-sm font-medium text-white hover:bg-emerald-700"
          >
            Opslaan
          </button>
        </form>
      )}

      {logs.length === 0 ? (
        <p className="text-sm text-stone-400">Nog geen notities.</p>
      ) : (
        <ul className="flex flex-col gap-2">
          {logs.map((log) => (
            <li key={log.id} className="flex items-start justify-between gap-3 border-b border-stone-100 pb-2 last:border-0">
              <div className="min-w-0">
                <p className="text-xs text-stone-400">{log.entry_date}</p>
                {log.text && <p className="text-sm">{log.text}</p>}
                <p className="text-sm text-stone-500">{metrics(log)}</p>
              </div>
              <button
                onClick={() => remove(log.id)}
                className="shrink-0 text-xs text-red-600 hover:underline"
              >
                Verwijderen
              </button>
            </li>
          ))}
        </ul>
      )}
    </section>
  )
}

function Field({ label, value, onChange }: { label: string; value: string; onChange: (v: string) => void }) {
  return (
    <label className="flex flex-col gap-1 text-xs text-stone-500">
      {label}
      <input
        type="number"
        min={0}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="rounded-lg border border-stone-300 px-2 py-1.5 text-sm text-stone-800"
      />
    </label>
  )
}

function metrics(log: LogEntry): string {
  const parts: string[] = []
  if (log.height_cm !== null) parts.push(`${log.height_cm} cm`)
  if (log.bud_count !== null) parts.push(`${log.bud_count} knoppen`)
  if (log.flower_count !== null) parts.push(`${log.flower_count} bloemen`)
  if (log.harvested_count !== null) parts.push(`${log.harvested_count} geoogst`)
  return parts.join(' · ')
}
