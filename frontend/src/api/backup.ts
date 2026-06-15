export const exportUrl = '/api/backup/export'

export async function importBackup(file: File, confirm: string): Promise<void> {
  const form = new FormData()
  form.append('file', file)
  form.append('confirm', confirm)
  const response = await fetch('/api/backup/import', { method: 'POST', body: form })
  if (!response.ok) {
    let detail = `HTTP ${response.status}`
    try {
      const body = await response.json()
      if (typeof body?.detail === 'string') detail = body.detail
    } catch {
      // no JSON body
    }
    throw new Error(detail)
  }
}
