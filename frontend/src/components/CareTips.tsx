import { useEffect, useState } from 'react'
import type { CareTip } from '../api/care'
import { getCareTips } from '../api/care'

const MONTHS = [
  'januari', 'februari', 'maart', 'april', 'mei', 'juni',
  'juli', 'augustus', 'september', 'oktober', 'november', 'december',
]

export default function CareTips() {
  const [month, setMonth] = useState<number | null>(null)
  const [tips, setTips] = useState<CareTip[]>([])
  const [open, setOpen] = useState(false)

  useEffect(() => {
    getCareTips()
      .then((data) => {
        setMonth(data.month)
        setTips(data.tips)
      })
      .catch(() => {
        // Care tips are a nice-to-have; stay silent if they can't load.
      })
  }, [])

  if (month === null || tips.length === 0) return null

  return (
    <section className="rounded-xl border border-amber-200 bg-amber-50 p-4">
      <button
        onClick={() => setOpen((v) => !v)}
        className="flex w-full items-center justify-between text-left"
      >
        <span className="font-medium text-amber-900">
          🌱 Verzorging in {MONTHS[month - 1]} ({tips.length} tips)
        </span>
        <span className="text-amber-700">{open ? '▲' : '▼'}</span>
      </button>

      {open && (
        <ul className="mt-3 flex flex-col gap-3">
          {tips.map((tip) => (
            <li key={tip.id}>
              <p className="font-medium text-amber-900">{tip.title}</p>
              <p className="text-sm text-amber-800">{tip.text}</p>
            </li>
          ))}
        </ul>
      )}
    </section>
  )
}
