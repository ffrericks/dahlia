import { useEffect, useRef, useState } from 'react'
import type { Plant, PlantDetail as Detail } from '../api/plants'
import {
  assignStorage,
  deletePhoto,
  deletePlant,
  getPlant,
  liftPlant,
  markSurvivedWinter,
  removeStorage,
  setEyeStatus,
  setProfilePhoto,
  updatePlant,
  uploadPhoto,
} from '../api/plants'
import { getSettings } from '../api/settings'
import { todayISO } from '../dates'
import { EYE_STATUS_LABELS, ORIGIN_LABELS, stateLabel } from '../labels'
import AssignVarietyForm from './AssignVarietyForm'
import DisposalActions from './DisposalActions'
import Logbook from './Logbook'
import PlantingForm from './PlantingForm'
import QrLabel from './QrLabel'

interface Props {
  plantId: number
  onBack: () => void
  onNavigate: (plantId: number) => void
  onChanged: () => void // tell the parent list to refresh
}

export default function PlantDetail({ plantId, onBack, onNavigate, onChanged }: Props) {
  const [detail, setDetail] = useState<Detail | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [busy, setBusy] = useState(false)
  const [planting, setPlanting] = useState(false)
  const [boxNumber, setBoxNumber] = useState('')
  const [liftDate, setLiftDate] = useState(todayISO())
  const [toolUrl, setToolUrl] = useState<string | null>(null)
  const fileInput = useRef<HTMLInputElement>(null)

  // Tool URL drives the QR deep-link (so a phone camera opens the plant directly).
  useEffect(() => {
    getSettings()
      .then((s) => setToolUrl(s.tool_url))
      .catch(() => setToolUrl(null))
  }, [])

  // Refresh this view and tell the parent list to refresh too.
  async function refreshAll() {
    await refresh()
    onChanged()
  }

  // Run a winter/storage action, then refresh this view and the parent list.
  async function runAction(action: () => Promise<unknown>) {
    setError(null)
    try {
      await action()
      await refreshAll()
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err))
    }
  }

  async function refresh() {
    setError(null)
    try {
      setDetail(await getPlant(plantId))
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err))
    }
  }

  useEffect(() => {
    refresh()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [plantId])

  async function handleUpload(event: React.ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0]
    if (!file) return
    setBusy(true)
    setError(null)
    try {
      await uploadPhoto(plantId, file)
      await refresh()
      onChanged()
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err))
    } finally {
      setBusy(false)
      if (fileInput.current) fileInput.current.value = ''
    }
  }

  async function makeProfile(photoId: number) {
    await setProfilePhoto(plantId, photoId)
    await refresh()
    onChanged()
  }

  async function removePhoto(photoId: number) {
    await deletePhoto(plantId, photoId)
    await refresh()
    onChanged()
  }

  async function removePlant() {
    if (!detail) return
    if (!window.confirm(`Plant ${detail.full_code} verwijderen?`)) return
    try {
      await deletePlant(plantId)
      onChanged()
      onBack()
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err))
    }
  }

  if (error && !detail) {
    return (
      <div className="flex flex-col gap-3">
        <BackButton onBack={onBack} />
        <p className="text-sm text-red-600">{error}</p>
      </div>
    )
  }
  if (!detail) return <p className="text-stone-500">Laden…</p>

  return (
    <div className="flex flex-col gap-5">
      <BackButton onBack={onBack} />

      <header className="flex flex-col gap-1">
        <h2 className="font-mono text-2xl font-semibold">{detail.label}</h2>
        <p className="text-stone-500">
          {detail.variety_name ?? (detail.variety_id ? 'naamloos' : 'nog geen soort')} ·{' '}
          {ORIGIN_LABELS[detail.origin]} · {stateLabel(detail.state)}
        </p>
        <NicknameEditor
          plantId={detail.id}
          nickname={detail.nickname}
          onSaved={refreshAll}
        />
      </header>

      {/* Provisional plant: assign a variety once known. */}
      {detail.variety_id === null && (
        <section className="flex flex-col gap-2 rounded-xl border border-stone-200 bg-white p-4 shadow-sm">
          <h3 className="text-sm font-medium uppercase tracking-wide text-stone-400">Soort</h3>
          <AssignVarietyForm plantId={detail.id} onDone={refreshAll} />
        </section>
      )}

      {/* Lineage navigation */}
      <section className="flex flex-col gap-2 rounded-xl border border-stone-200 bg-white p-4 shadow-sm">
        <h3 className="text-sm font-medium uppercase tracking-wide text-stone-400">Afstamming</h3>
        <div>
          <span className="text-sm text-stone-500">Moederplant: </span>
          {detail.parent ? (
            <LinkPlant plant={detail.parent} onNavigate={onNavigate} />
          ) : (
            <span className="text-sm text-stone-400">geen (stamplant)</span>
          )}
        </div>
        <div>
          <span className="text-sm text-stone-500">Afstammelingen: </span>
          {detail.children.length === 0 ? (
            <span className="text-sm text-stone-400">geen</span>
          ) : (
            <span className="inline-flex flex-wrap gap-2">
              {detail.children.map((c) => (
                <LinkPlant key={c.id} plant={c} onNavigate={onNavigate} />
              ))}
            </span>
          )}
        </div>
        {detail.descendants.total > 0 && (
          <p className="text-sm text-stone-500">
            In totaal {detail.descendants.total} afstammeling(en) gehad ·{' '}
            {detail.descendants.owned} nog in bezit
          </p>
        )}
      </section>

      {/* Location & planting history */}
      <section className="flex flex-col gap-3 rounded-xl border border-stone-200 bg-white p-4 shadow-sm">
        <h3 className="text-sm font-medium uppercase tracking-wide text-stone-400">Plek</h3>
        {detail.location ? (
          <p>
            <span className="font-mono font-medium">{detail.location.code}</span>{' '}
            <span className="text-stone-500">
              ({detail.location.label}
              {detail.location.name ? ` — ${detail.location.name}` : ''}
              {detail.location.position ? `, ${detail.location.position}` : ''})
            </span>
          </p>
        ) : (
          <p className="text-sm text-stone-400">Niet geplant (in opslag).</p>
        )}

        <p className="text-sm text-stone-600">
          🌿 Laatst bemest:{' '}
          {detail.last_fertilized ?? <span className="text-stone-400">nog niet</span>}
        </p>

        {/* Only a stored plant that isn't currently planted can be planted out. */}
        {!detail.location &&
          (detail.state === 'stored' || detail.state === 'survived_winter') &&
          (planting ? (
            <PlantingForm
              plantId={plantId}
              onDone={() => {
                setPlanting(false)
                refresh()
                onChanged()
              }}
              onCancel={() => setPlanting(false)}
            />
          ) : (
            <button
              onClick={() => setPlanting(true)}
              className="self-start rounded-lg bg-emerald-600 px-4 py-2 text-sm font-medium text-white hover:bg-emerald-700"
            >
              Plant op een plek
            </button>
          ))}

        {detail.plantings.length > 0 && (
          <div className="flex flex-col gap-1">
            <p className="text-xs font-medium uppercase tracking-wide text-stone-400">
              Geschiedenis
            </p>
            <ul className="flex flex-col gap-1 text-sm text-stone-600">
              {detail.plantings.map((p) => (
                <li key={p.id}>
                  <span className="font-mono">{p.location_code}</span> · {p.planted_on}
                  {p.lifted_on ? ` → ${p.lifted_on}` : ' → nu'}
                  {p.position ? ` (${p.position})` : ''}
                </li>
              ))}
            </ul>
          </div>
        )}
      </section>

      {/* Winter & storage */}
      {(detail.state === 'planted' || detail.state === 'stored') && (
        <section className="flex flex-col gap-3 rounded-xl border border-stone-200 bg-white p-4 shadow-sm">
          <h3 className="text-sm font-medium uppercase tracking-wide text-stone-400">
            Winter &amp; opslag
          </h3>

          {detail.state === 'planted' && (
            <div className="flex flex-col gap-2">
              <label className="flex items-center gap-2 text-sm text-stone-500">
                Rooidatum
                <input
                  type="date"
                  value={liftDate}
                  onChange={(e) => setLiftDate(e.target.value)}
                  className="rounded-lg border border-stone-300 px-2 py-1.5 text-sm text-stone-800"
                />
              </label>
              <div className="flex flex-wrap gap-2">
                <button
                  onClick={() => runAction(() => liftPlant(detail.id, liftDate))}
                  className="rounded-lg bg-emerald-600 px-4 py-2 text-sm font-medium text-white hover:bg-emerald-700"
                >
                  Rooien (uit de grond)
                </button>
                <button
                  onClick={() => runAction(() => markSurvivedWinter(detail.id))}
                  className="rounded-lg border border-stone-300 px-4 py-2 text-sm font-medium text-stone-600 hover:bg-stone-100"
                >
                  Winter overleefd (blijft staan)
                </button>
              </div>
            </div>
          )}

          {detail.state === 'stored' && (
            <div className="flex flex-col gap-3">
              <div className="flex flex-col gap-1">
                <span className="text-sm text-stone-500">Oog-status</span>
                <div className="flex flex-wrap gap-2">
                  {Object.entries(EYE_STATUS_LABELS).map(([value, label]) => (
                    <button
                      key={value}
                      onClick={() => runAction(() => setEyeStatus(detail.id, value))}
                      className={`rounded-lg border px-3 py-1.5 text-sm font-medium ${
                        detail.eye_status === value
                          ? 'border-emerald-600 bg-emerald-50 text-emerald-700'
                          : 'border-stone-300 text-stone-600 hover:bg-stone-100'
                      }`}
                    >
                      {label}
                    </button>
                  ))}
                </div>
              </div>

              <div className="flex flex-col gap-1">
                <span className="text-sm text-stone-500">Opslagdoos</span>
                {detail.storage ? (
                  <div className="flex items-center gap-3">
                    <span className="font-mono font-medium">{detail.storage.composite}</span>
                    <button
                      onClick={() => runAction(() => removeStorage(detail.id))}
                      className="text-sm text-red-600 hover:underline"
                    >
                      Uit doos halen
                    </button>
                  </div>
                ) : (
                  <div className="flex gap-2">
                    <input
                      type="number"
                      min={1}
                      max={99}
                      value={boxNumber}
                      onChange={(e) => setBoxNumber(e.target.value)}
                      placeholder="Doosnr."
                      className="w-28 rounded-lg border border-stone-300 px-3 py-2"
                    />
                    <button
                      onClick={() => {
                        const n = Number(boxNumber)
                        if (n >= 1) runAction(() => assignStorage(detail.id, n))
                      }}
                      disabled={!boxNumber}
                      className="rounded-lg bg-emerald-600 px-4 py-2 text-sm font-medium text-white hover:bg-emerald-700 disabled:opacity-40"
                    >
                      In doos plaatsen
                    </button>
                  </div>
                )}
              </div>
            </div>
          )}
        </section>
      )}

      {/* Photos */}
      <section className="flex flex-col gap-3 rounded-xl border border-stone-200 bg-white p-4 shadow-sm">
        <div className="flex items-center justify-between">
          <h3 className="text-sm font-medium uppercase tracking-wide text-stone-400">Foto's</h3>
          <label className="cursor-pointer rounded-lg border border-emerald-600 px-3 py-1.5 text-sm font-medium text-emerald-700 hover:bg-emerald-50">
            {busy ? 'Bezig…' : '+ Foto toevoegen'}
            <input
              ref={fileInput}
              type="file"
              accept="image/*"
              onChange={handleUpload}
              disabled={busy}
              className="hidden"
            />
          </label>
        </div>

        {error && <p className="text-sm text-red-600">{error}</p>}

        {detail.photos.length === 0 ? (
          <p className="text-sm text-stone-400">Nog geen eigen foto's van deze plant.</p>
        ) : (
          <div className="grid grid-cols-2 gap-3 sm:grid-cols-3">
            {detail.photos.map((photo) => (
              <div
                key={photo.id}
                className="relative overflow-hidden rounded-lg border border-stone-200"
              >
                <img src={photo.thumbnail_url} alt="" className="aspect-square w-full object-cover" />
                {photo.is_profile && (
                  <span className="absolute left-1 top-1 rounded bg-emerald-600 px-1.5 py-0.5 text-xs font-medium text-white">
                    Profiel
                  </span>
                )}
                <div className="flex justify-between gap-1 p-1">
                  {!photo.is_profile && (
                    <button
                      onClick={() => makeProfile(photo.id)}
                      className="text-xs text-emerald-700 hover:underline"
                    >
                      Profiel
                    </button>
                  )}
                  <button
                    onClick={() => removePhoto(photo.id)}
                    className="ml-auto text-xs text-red-600 hover:underline"
                  >
                    Verwijderen
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </section>

      {detail.yearly.length > 0 && (
        <section className="flex flex-col gap-2 rounded-xl border border-stone-200 bg-white p-4 shadow-sm">
          <h3 className="text-sm font-medium uppercase tracking-wide text-stone-400">
            Prestatie per jaar
          </h3>
          <ul className="flex flex-col gap-1 text-sm">
            {detail.yearly.map((y, i) => (
              <li key={i} className="flex flex-wrap gap-x-3 text-stone-600">
                <span className="font-medium text-stone-800">{y.year}</span>
                <span className="font-mono">{y.location_code}</span>
                {y.height_max !== null && <span>{y.height_max} cm</span>}
                {y.flowers_max !== null && <span>{y.flowers_max} bloemen</span>}
                {y.harvested_total > 0 && <span>{y.harvested_total} geoogst</span>}
              </li>
            ))}
          </ul>
        </section>
      )}

      {(detail.storage?.composite || detail.full_code) && (
        <section className="flex flex-col gap-3 rounded-xl border border-stone-200 bg-white p-4 shadow-sm">
          <h3 className="text-sm font-medium uppercase tracking-wide text-stone-400">Label</h3>
          <QrLabel
            value={
              toolUrl
                ? `${toolUrl}/?plant=${detail.id}`
                : (detail.storage?.composite ?? detail.full_code!)
            }
            caption={detail.storage?.composite ?? detail.full_code!}
          />
          {toolUrl ? (
            <p className="text-center text-xs text-stone-400">
              Scan met je telefooncamera om deze plant te openen.
            </p>
          ) : (
            <p className="text-center text-xs text-stone-400">
              Stel het adres van de tool in (Instellingen) zodat de QR-code de plant rechtstreeks
              opent.
            </p>
          )}
        </section>
      )}

      <Logbook plantId={plantId} logs={detail.logs} onChanged={refreshAll} />

      <DisposalActions detail={detail} onChanged={refreshAll} />

      <button
        onClick={removePlant}
        className="self-start text-sm text-stone-400 hover:text-red-600 hover:underline"
      >
        Plant verwijderen (alleen bij vergissing)
      </button>
    </div>
  )
}

function BackButton({ onBack }: { onBack: () => void }) {
  return (
    <button onClick={onBack} className="self-start text-sm text-emerald-700 hover:underline">
      ← Terug naar lijst
    </button>
  )
}

function NicknameEditor({
  plantId,
  nickname,
  onSaved,
}: {
  plantId: number
  nickname: string | null
  onSaved: () => void
}) {
  const [editing, setEditing] = useState(false)
  const [value, setValue] = useState(nickname ?? '')

  async function save() {
    await updatePlant(plantId, value.trim() || null)
    setEditing(false)
    onSaved()
  }

  if (!editing) {
    return (
      <button onClick={() => setEditing(true)} className="self-start text-sm text-emerald-700 hover:underline">
        {nickname ? `Bijnaam: ${nickname} — wijzigen` : '+ Bijnaam toevoegen'}
      </button>
    )
  }
  return (
    <div className="flex gap-2">
      <input
        value={value}
        onChange={(e) => setValue(e.target.value)}
        placeholder="Bijnaam"
        className="rounded-lg border border-stone-300 px-3 py-1.5 text-sm"
      />
      <button onClick={save} className="text-sm font-medium text-emerald-700 hover:underline">
        Opslaan
      </button>
      <button onClick={() => setEditing(false)} className="text-sm text-stone-500 hover:underline">
        Annuleren
      </button>
    </div>
  )
}

function LinkPlant({ plant, onNavigate }: { plant: Plant; onNavigate: (id: number) => void }) {
  return (
    <button
      onClick={() => onNavigate(plant.id)}
      className="font-mono text-sm text-emerald-700 hover:underline"
    >
      {plant.full_code}
    </button>
  )
}
