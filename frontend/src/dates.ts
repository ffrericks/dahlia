// Today's date as YYYY-MM-DD in local time (for prefilling editable <input type="date">).
export function todayISO(): string {
  const now = new Date()
  const offsetMs = now.getTimezoneOffset() * 60000
  return new Date(now.getTime() - offsetMs).toISOString().slice(0, 10)
}
