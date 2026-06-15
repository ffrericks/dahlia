import { useEffect, useState } from 'react'
import QRCode from 'qrcode'

// A printable QR label. `value` is what the QR encodes (a deep-link URL when the
// tool URL is set, otherwise the bare code); `caption` is the human-readable code.
export default function QrLabel({ value, caption }: { value: string; caption: string }) {
  const [src, setSrc] = useState<string | null>(null)

  useEffect(() => {
    QRCode.toDataURL(value, { margin: 1, width: 180 })
      .then(setSrc)
      .catch(() => setSrc(null))
  }, [value])

  if (!src) return null

  return (
    <div className="flex flex-col items-center gap-2">
      <img src={src} alt={`QR ${caption}`} width={180} height={180} />
      <span className="font-mono text-sm">{caption}</span>
      <span className="text-xs text-stone-400">
        Print en plak als label; scan later om de plant terug te vinden.
      </span>
    </div>
  )
}
