import { useEffect, useState } from 'react'
import Insights from './pages/Insights'
import Locations from './pages/Locations'
import Plants from './pages/Plants'
import Settings from './pages/Settings'
import Storage from './pages/Storage'
import Tree from './pages/Tree'
import Varieties from './pages/Varieties'

type Tab =
  | 'plants'
  | 'varieties'
  | 'locations'
  | 'storage'
  | 'tree'
  | 'insights'
  | 'settings'

const TABS: { id: Tab; label: string }[] = [
  { id: 'plants', label: 'Planten' },
  { id: 'varieties', label: 'Soorten' },
  { id: 'locations', label: 'Plekken' },
  { id: 'storage', label: 'Opslag' },
  { id: 'tree', label: 'Stamboom' },
  { id: 'insights', label: 'Beste plek' },
  { id: 'settings', label: 'Instellingen' },
]

function readDeepLink(): { plantId: number | null; query: string | null } {
  const params = new URLSearchParams(window.location.search)
  const plant = params.get('plant')
  return {
    plantId: plant && /^\d+$/.test(plant) ? Number(plant) : null,
    query: params.get('q'),
  }
}

export default function App() {
  const [tab, setTab] = useState<Tab>('plants')
  // A QR scanned with the phone camera opens the app with ?plant= or ?q= — handle it once.
  const [deepLink, setDeepLink] = useState(readDeepLink)

  useEffect(() => {
    if (deepLink.plantId || deepLink.query) {
      window.history.replaceState({}, '', window.location.pathname)
      setDeepLink({ plantId: null, query: null }) // consume, so it doesn't reopen later
    }
  }, [])

  return (
    <div className="min-h-screen bg-stone-50 text-stone-800">
      <main className="mx-auto flex max-w-2xl flex-col gap-6 px-4 py-8">
        <header className="flex flex-col gap-1">
          <h1 className="text-3xl font-semibold tracking-tight">🌸 Dahlia Tool</h1>
          <p className="text-stone-500">Bijhouden en vermeerderen van je dahlia's.</p>
        </header>

        <nav className="flex gap-1 overflow-x-auto rounded-xl bg-stone-200/60 p-1">
          {TABS.map(({ id, label }) => (
            <button
              key={id}
              onClick={() => setTab(id)}
              className={`shrink-0 whitespace-nowrap rounded-lg px-3 py-2 text-sm font-medium transition ${
                tab === id
                  ? 'bg-white text-stone-900 shadow-sm'
                  : 'text-stone-500 hover:text-stone-700'
              }`}
            >
              {label}
            </button>
          ))}
        </nav>

        {tab === 'plants' && (
          <Plants initialPlantId={deepLink.plantId} initialQuery={deepLink.query} />
        )}
        {tab === 'varieties' && <Varieties />}
        {tab === 'locations' && <Locations />}
        {tab === 'storage' && <Storage />}
        {tab === 'tree' && <Tree />}
        {tab === 'insights' && <Insights />}
        {tab === 'settings' && <Settings />}
      </main>
    </div>
  )
}
