import { useEffect, useState } from 'react'
import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import type { Dashboard as DashboardData } from '../api/dashboard'
import { getDashboard } from '../api/dashboard'
import Insights from './Insights'

const MONTHS = ['jan', 'feb', 'mrt', 'apr', 'mei', 'jun', 'jul', 'aug', 'sep', 'okt', 'nov', 'dec']
const COLORS = ['#059669', '#db2777', '#2563eb', '#d97706', '#7c3aed', '#0891b2', '#65a30d']

export default function Dashboard() {
  const [data, setData] = useState<DashboardData | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [year, setYear] = useState<number | null>(null)

  useEffect(() => {
    getDashboard()
      .then((d) => {
        setData(d)
        if (d.seasons.length > 0) setYear(d.seasons[d.seasons.length - 1].year)
      })
      .catch((err) => setError(err instanceof Error ? err.message : String(err)))
  }, [])

  if (error) return <p className="text-sm text-red-600">{error}</p>
  if (!data) return <p className="text-stone-500">Laden…</p>

  // Active-plants-per-year: one row per month, one column per year.
  const plantRows = MONTHS.map((label, i) => {
    const row: Record<string, number | string> = { month: label }
    for (const line of data.plants_per_year) row[String(line.year)] = line.points[i].count
    return row
  })

  const season = data.seasons.find((s) => s.year === year)
  const seasonRows = season
    ? MONTHS.map((label, i) => ({
        month: label,
        bloemen: season.points[i].flowers,
        knoppen: season.points[i].buds,
        hoogte: season.points[i].height,
      }))
    : []

  return (
    <div className="flex flex-col gap-6">
      <h2 className="text-lg font-semibold">Metrix</h2>

      {/* Stat cards */}
      <div className="grid grid-cols-3 gap-3">
        <StatCard label="Soorten" value={data.cards.varieties} />
        <StatCard label="Planten" value={data.cards.plants} />
        <StatCard label="Bloemen geoogst" value={data.cards.harvested_total} />
      </div>

      {/* Active plants per year */}
      <ChartCard title="Actieve planten per jaar">
        {data.plants_per_year.length === 0 ? (
          <Empty />
        ) : (
          <ResponsiveContainer width="100%" height={260}>
            <LineChart data={plantRows} margin={{ top: 8, right: 8, bottom: 0, left: -20 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e7e5e4" />
              <XAxis dataKey="month" fontSize={12} />
              <YAxis allowDecimals={false} fontSize={12} />
              <Tooltip />
              <Legend />
              {data.plants_per_year.map((line, idx) => (
                <Line
                  key={line.year}
                  type="monotone"
                  dataKey={String(line.year)}
                  stroke={COLORS[idx % COLORS.length]}
                  strokeWidth={2}
                  dot={false}
                />
              ))}
            </LineChart>
          </ResponsiveContainer>
        )}
      </ChartCard>

      {/* Per-season metrics */}
      <div className="flex items-center gap-3">
        <h3 className="text-sm font-medium uppercase tracking-wide text-stone-400">Per seizoen</h3>
        {data.seasons.length > 0 && (
          <select
            value={year ?? ''}
            onChange={(e) => setYear(Number(e.target.value))}
            className="rounded-lg border border-stone-300 px-3 py-1.5 text-sm"
          >
            {data.seasons.map((s) => (
              <option key={s.year} value={s.year}>
                {s.year}
              </option>
            ))}
          </select>
        )}
      </div>

      {data.seasons.length === 0 ? (
        <ChartCard title="Bloemen & knoppen">
          <Empty />
        </ChartCard>
      ) : (
        <>
          <ChartCard title="Bloemen & knoppen (piek per maand)">
            <ResponsiveContainer width="100%" height={240}>
              <LineChart data={seasonRows} margin={{ top: 8, right: 8, bottom: 0, left: -20 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e7e5e4" />
                <XAxis dataKey="month" fontSize={12} />
                <YAxis allowDecimals={false} fontSize={12} />
                <Tooltip />
                <Legend />
                <Line type="monotone" dataKey="bloemen" stroke="#db2777" strokeWidth={2} connectNulls />
                <Line type="monotone" dataKey="knoppen" stroke="#059669" strokeWidth={2} connectNulls />
              </LineChart>
            </ResponsiveContainer>
          </ChartCard>

          <ChartCard title="Hoogste plant (cm)">
            <ResponsiveContainer width="100%" height={240}>
              <LineChart data={seasonRows} margin={{ top: 8, right: 8, bottom: 0, left: -20 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e7e5e4" />
                <XAxis dataKey="month" fontSize={12} />
                <YAxis allowDecimals={false} fontSize={12} />
                <Tooltip />
                <Line type="monotone" dataKey="hoogte" stroke="#2563eb" strokeWidth={2} connectNulls />
              </LineChart>
            </ResponsiveContainer>
          </ChartCard>
        </>
      )}

      <div className="border-t border-stone-200 pt-4">
        <Insights />
      </div>
    </div>
  )
}

function StatCard({ label, value }: { label: string; value: number }) {
  return (
    <div className="rounded-xl border border-stone-200 bg-white p-4 text-center shadow-sm">
      <p className="text-2xl font-semibold">{value}</p>
      <p className="text-xs text-stone-500">{label}</p>
    </div>
  )
}

function ChartCard({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <section className="flex flex-col gap-2 rounded-xl border border-stone-200 bg-white p-4 shadow-sm">
      <h3 className="text-sm font-medium text-stone-600">{title}</h3>
      {children}
    </section>
  )
}

function Empty() {
  return <p className="py-8 text-center text-sm text-stone-400">Nog geen gegevens.</p>
}
