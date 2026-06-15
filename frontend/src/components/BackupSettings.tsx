import { useState } from 'react'
import { exportUrl, importBackup } from '../api/backup'

const CONFIRM_PHRASE = 'dahlia tool'

export default function BackupSettings() {
  const [file, setFile] = useState<File | null>(null)
  const [confirm, setConfirm] = useState('')
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const canImport = file !== null && confirm.trim().toLowerCase() === CONFIRM_PHRASE

  async function doImport() {
    if (!file) return
    setError(null)
    setBusy(true)
    try {
      await importBackup(file, confirm)
      window.alert('Back-up teruggezet. De pagina wordt opnieuw geladen.')
      window.location.reload()
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err))
      setBusy(false)
    }
  }

  return (
    <section className="flex flex-col gap-3 border-t border-stone-200 pt-6">
      <h2 className="text-lg font-semibold">Back-up</h2>

      {/* Export */}
      <div className="flex flex-col gap-1">
        <span className="text-sm font-medium text-stone-600">Downloaden</span>
        <a
          href={exportUrl}
          className="self-start rounded-lg bg-emerald-600 px-4 py-2 text-sm font-medium text-white hover:bg-emerald-700"
        >
          Download back-up
        </a>
        <span className="text-xs text-stone-400">
          Eén bestand met de database én alle foto's. Bewaar het op een veilige plek.
        </span>
      </div>

      {/* Import */}
      <div className="mt-2 flex flex-col gap-2 rounded-lg border border-red-200 bg-red-50 p-4">
        <span className="text-sm font-medium text-red-700">Terugzetten (overschrijft alles)</span>
        <p className="text-xs text-red-600">
          Dit vervangt al je huidige planten, foto's en logboeken door die uit het back-upbestand.
          De huidige gegevens worden eerst automatisch apart gezet, maar wees voorzichtig.
        </p>

        <div className="flex flex-wrap items-center gap-3">
          <label className="cursor-pointer rounded-lg border border-stone-300 bg-white px-4 py-2 text-sm font-medium text-stone-700 hover:bg-stone-100">
            Bestand kiezen
            <input
              type="file"
              accept=".zip"
              onChange={(e) => setFile(e.target.files?.[0] ?? null)}
              className="hidden"
            />
          </label>
          <span className="min-w-0 truncate text-sm text-stone-500">
            {file ? file.name : 'Geen bestand gekozen'}
          </span>
        </div>

        <label className="flex flex-col gap-1">
          <span className="text-xs text-stone-600">
            Typ <span className="font-mono font-semibold">dahlia tool</span> om te bevestigen:
          </span>
          <input
            value={confirm}
            onChange={(e) => setConfirm(e.target.value)}
            placeholder="dahlia tool"
            className="rounded-lg border border-stone-300 px-3 py-2"
          />
        </label>

        {error && <p className="text-sm text-red-700">{error}</p>}

        <button
          onClick={doImport}
          disabled={!canImport || busy}
          className="self-start rounded-lg bg-red-600 px-4 py-2 text-sm font-medium text-white hover:bg-red-700 disabled:opacity-40"
        >
          {busy ? 'Bezig met terugzetten…' : 'Back-up terugzetten'}
        </button>
      </div>
    </section>
  )
}
