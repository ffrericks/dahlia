import { useEffect, useState } from 'react'
import QRCode from 'qrcode'

// A printable QR label encoding the plant's code, so it can be scanned to find the plant back.
export default function QrLabel({ code }: { code: string }) {
  const [src, setSrc] = useState<string | null>(null)

  useEffect(() => {
    QRCode.toDataURL(code, { margin: 1, width: 180 })
      .then(setSrc)
      .catch(() => setSrc(null))
  }, [code])

  if (!src) return null

  return (
    <div className="flex flex-col items-center gap-2">
      <img src={src} alt={`QR ${code}`} width={180} height={180} />
      <span className="font-mono text-sm">{code}</span>
      <span className="text-xs text-stone-400">
        Print en plak als label; scan later om de plant terug te vinden.
      </span>
    </div>
  )
}
