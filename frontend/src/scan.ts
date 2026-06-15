// Interpret a scanned/typed value: it may be a deep-link URL (from a QR that points
// at the tool) or a bare code/storage-ID. Returns what to do with it.
export function parseScan(value: string): { plantId?: number; query?: string } {
  const trimmed = value.trim()
  try {
    const url = new URL(trimmed)
    const plant = url.searchParams.get('plant')
    if (plant && /^\d+$/.test(plant)) return { plantId: Number(plant) }
    const q = url.searchParams.get('q')
    if (q) return { query: q }
  } catch {
    // not a URL — fall through and treat it as a code/search term
  }
  return { query: trimmed }
}
