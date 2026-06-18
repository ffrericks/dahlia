const TIPS = [
  'Gebruik stekpoeder.',
  'Neem een stukje knol (een "hiel") mee.',
  'Haal zoveel mogelijk blad weg om verdamping tegen te gaan.',
  'Houd de grond goed vochtig.',
  'Zet de stek op een warme plaats.',
]

// Shown while a cutting is still rooting in its pot.
export default function CuttingTips() {
  return (
    <section className="rounded-xl border border-amber-200 bg-amber-50 p-4">
      <h3 className="font-medium text-amber-900">🌱 Verzorging van een stek</h3>
      <ul className="mt-2 list-disc pl-5 text-sm text-amber-800">
        {TIPS.map((tip) => (
          <li key={tip}>{tip}</li>
        ))}
      </ul>
    </section>
  )
}
