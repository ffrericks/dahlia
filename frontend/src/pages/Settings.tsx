import { useEffect, useState } from 'react'
import { getSettings, updateSettings } from '../api/settings'

export default function Settings() {
  const [toolUrl, setToolUrl] = useState('')
  const [autoFertilize, setAutoFertilize] = useState(true)
  const [defaultGarden, setDefaultGarden] = useState('')

  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [saved, setSaved] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    getSettings()
      .then((s) => {
        setToolUrl(s.tool_url ?? '')
        setAutoFertilize(s.auto_fertilize_bak)
        setDefaultGarden(s.default_garden_name ?? '')
      })
      .catch((err) => setError(err instanceof Error ? err.message : String(err)))
      .finally(() => setLoading(false))
  }, [])

  async function save(event: React.FormEvent) {
    event.preventDefault()
    setError(null)
    setSaved(false)
    setSaving(true)
    try {
      await updateSettings({
        tool_url: toolUrl.trim() || null,
        auto_fertilize_bak: autoFertilize,
        default_garden_name: defaultGarden.trim() || null,
      })
      setSaved(true)
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err))
    } finally {
      setSaving(false)
    }
  }

  if (loading) return <p className="text-stone-500">Laden…</p>

  return (
    <form onSubmit={save} className="flex flex-col gap-5">
      <h2 className="text-lg font-semibold">Instellingen</h2>

      <label className="flex flex-col gap-1">
        <span className="text-sm font-medium text-stone-600">Adres van de tool (URL)</span>
        <input
          value={toolUrl}
          onChange={(e) => {
            setToolUrl(e.target.value)
            setSaved(false)
          }}
          type="url"
          placeholder="http://dahlia.thuis:8000"
          className="rounded-lg border border-stone-300 px-3 py-2"
        />
        <span className="text-xs text-stone-400">
          Het adres waarop je de tool opent. Wordt straks gebruikt voor QR-codes en de API.
        </span>
      </label>

      <label className="flex items-start gap-2">
        <input
          type="checkbox"
          checked={autoFertilize}
          onChange={(e) => {
            setAutoFertilize(e.target.checked)
            setSaved(false)
          }}
          className="mt-1"
        />
        <span>
          <span className="text-sm font-medium text-stone-700">
            Hele bak bemesten tegelijk
          </span>
          <span className="block text-xs text-stone-400">
            Als je één plant als "bemest" markeert, geldt dat voor alle planten op dezelfde plek.
          </span>
        </span>
      </label>

      <label className="flex flex-col gap-1">
        <span className="text-sm font-medium text-stone-600">Standaard naam tuinplek</span>
        <input
          value={defaultGarden}
          onChange={(e) => {
            setDefaultGarden(e.target.value)
            setSaved(false)
          }}
          placeholder="bijv. Achtertuin"
          className="rounded-lg border border-stone-300 px-3 py-2"
        />
        <span className="text-xs text-stone-400">
          Wordt gebruikt als je een nieuwe tuinplek maakt zonder naam.
        </span>
      </label>

      {error && <p className="text-sm text-red-600">{error}</p>}
      {saved && <p className="text-sm text-emerald-700">Opgeslagen.</p>}

      <button
        type="submit"
        disabled={saving}
        className="self-start rounded-lg bg-emerald-600 px-4 py-2 font-medium text-white hover:bg-emerald-700 disabled:opacity-40"
      >
        {saving ? 'Opslaan…' : 'Opslaan'}
      </button>
    </form>
  )
}
