import { useState } from 'react'
import type { Origin, PlantDetail } from '../api/plants'
import { createPlant, disposePlant, markNotEmerged } from '../api/plants'
import { todayISO } from '../dates'

interface Props {
  detail: PlantDetail
  onChanged: () => void
  onBack: () => void
}

type Mode = null | 'discard' | 'giveaway'

export default function DisposalActions({ detail, onChanged, onBack }: Props) {
  const [mode, setMode] = useState<Mode>(null)
  const [reason, setReason] = useState('')
  const [disease, setDisease] = useState(false)
  const [recipient, setRecipient] = useState('')
  const [date, setDate] = useState(todayISO())
  const [error, setError] = useState<string | null>(null)

  async function run(action: () => Promise<unknown>) {
    setError(null)
    try {
      await action()
      setMode(null)
      onChanged()
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err))
    }
  }

  // Split or take a cutting: create a direct descendant, then go back to the overview
  // where it shows up with a "nieuw" badge.
  async function propagate(origin: Origin) {
    setError(null)
    try {
      const child = await createPlant({ origin, parent_plant_id: detail.id })
      const what = origin === 'cutting' ? 'Stek' : 'Afsplitsing'
      onChanged()
      onBack()
      window.alert(`${what} ${child.full_code ?? ''} aangemaakt. Hij staat met "nieuw" in de lijst.`)
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err))
    }
  }

  // Already disposed: show the record.
  if (detail.disposal) {
    const d = detail.disposal
    return (
      <section className="flex flex-col gap-1 rounded-xl border border-stone-200 bg-stone-50 p-4">
        <h3 className="text-sm font-medium uppercase tracking-wide text-stone-400">Afgevoerd</h3>
        <p>
          {d.kind === 'given_away' ? 'Weggegeven' : 'Weggegooid'} op {d.disposed_on}
          {d.recipient ? ` aan ${d.recipient}` : ''}
        </p>
        {d.reason && <p className="text-sm text-stone-500">Reden: {d.reason}</p>}
        {d.disease_warning && (
          <p className="text-sm font-medium text-red-700">
            ⚠️ Ziekte — in de kliko, niet op de composthoop. Gebruik de schaar niet zomaar voor
            andere dahlia's.
          </p>
        )}
      </section>
    )
  }

  return (
    <section className="flex flex-col gap-3 rounded-xl border border-stone-200 bg-white p-4 shadow-sm">
      <h3 className="text-sm font-medium uppercase tracking-wide text-stone-400">Acties</h3>

      {mode === null && (
        <div className="flex flex-col gap-2">
          {/* Propagate: a split or cutting becomes a direct descendant. */}
          {detail.variety_id !== null && (
            <div className="flex flex-wrap gap-2">
              <button
                onClick={() => propagate('split')}
                className="rounded-lg border border-emerald-600 px-4 py-2 text-sm font-medium text-emerald-700 hover:bg-emerald-50"
              >
                Splitsen
              </button>
              <button
                onClick={() => propagate('cutting')}
                className="rounded-lg border border-emerald-600 px-4 py-2 text-sm font-medium text-emerald-700 hover:bg-emerald-50"
              >
                Stekken
              </button>
            </div>
          )}
          <div className="flex flex-wrap gap-2">
            <button
              onClick={() => setMode('discard')}
              className="rounded-lg border border-red-200 px-4 py-2 text-sm font-medium text-red-600 hover:bg-red-50"
            >
              Weggooien
            </button>
            <button
              onClick={() => setMode('giveaway')}
              className="rounded-lg border border-stone-300 px-4 py-2 text-sm font-medium text-stone-600 hover:bg-stone-100"
            >
              Weggeven
            </button>
            <button
              onClick={() => run(() => markNotEmerged(detail.id))}
              className="rounded-lg border border-stone-300 px-4 py-2 text-sm font-medium text-stone-600 hover:bg-stone-100"
            >
              Niet opgekomen
            </button>
          </div>
        </div>
      )}

      {mode === 'discard' && (
        <div className="flex flex-col gap-2">
          <input
            value={reason}
            onChange={(e) => setReason(e.target.value)}
            placeholder="Reden (optioneel, bijv. verrot, ziek)"
            className="rounded-lg border border-stone-300 px-3 py-2"
          />
          <label className="flex items-center gap-2 text-sm text-stone-700">
            <input type="checkbox" checked={disease} onChange={(e) => setDisease(e.target.checked)} />
            Ziekte (gal/virus) — waarschuw broertjes en zusjes
          </label>
          <DateField value={date} onChange={setDate} />
          <Buttons
            onConfirm={() =>
              run(() =>
                disposePlant(detail.id, {
                  kind: 'discarded',
                  reason: reason.trim() || null,
                  disease_warning: disease,
                  disposed_on: date,
                }),
              )
            }
            onCancel={() => setMode(null)}
            confirmLabel="Weggooien"
          />
        </div>
      )}

      {mode === 'giveaway' && (
        <div className="flex flex-col gap-2">
          <input
            value={recipient}
            onChange={(e) => setRecipient(e.target.value)}
            placeholder="Aan wie? (naam)"
            className="rounded-lg border border-stone-300 px-3 py-2"
          />
          <a
            href={`/api/plants/${detail.id}/summary`}
            download
            className="text-sm text-emerald-700 hover:underline"
          >
            Download samenvatting (.txt) om mee te sturen
          </a>
          <DateField value={date} onChange={setDate} />
          <Buttons
            onConfirm={() =>
              run(() =>
                disposePlant(detail.id, {
                  kind: 'given_away',
                  recipient: recipient.trim() || null,
                  disposed_on: date,
                }),
              )
            }
            onCancel={() => setMode(null)}
            confirmLabel="Weggeven"
          />
        </div>
      )}

      {error && <p className="text-sm text-red-600">{error}</p>}
    </section>
  )
}

function DateField({ value, onChange }: { value: string; onChange: (v: string) => void }) {
  return (
    <label className="flex items-center gap-2 text-sm text-stone-500">
      Datum
      <input
        type="date"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="rounded-lg border border-stone-300 px-2 py-1.5 text-sm text-stone-800"
      />
    </label>
  )
}

function Buttons({
  onConfirm,
  onCancel,
  confirmLabel,
}: {
  onConfirm: () => void
  onCancel: () => void
  confirmLabel: string
}) {
  return (
    <div className="flex gap-2">
      <button
        onClick={onConfirm}
        className="rounded-lg bg-red-600 px-4 py-2 text-sm font-medium text-white hover:bg-red-700"
      >
        {confirmLabel}
      </button>
      <button
        onClick={onCancel}
        className="rounded-lg border border-stone-300 px-4 py-2 text-sm font-medium text-stone-600 hover:bg-stone-100"
      >
        Annuleren
      </button>
    </div>
  )
}
