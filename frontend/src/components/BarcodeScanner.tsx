import { useEffect, useRef, useState } from 'react'

interface Props {
  onScan: (value: string) => void
  onClose: () => void
}

// Whether this browser can decode barcodes from the camera (Chrome/Android: yes; iOS Safari: no).
export const scannerSupported =
  typeof window !== 'undefined' && 'BarcodeDetector' in window

export default function BarcodeScanner({ onScan, onClose }: Props) {
  const videoRef = useRef<HTMLVideoElement>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!scannerSupported) {
      setError('Scannen wordt niet ondersteund in deze browser. Typ de code in.')
      return
    }

    let stream: MediaStream | null = null
    let timer: number | undefined
    let stopped = false
    const detector = new window.BarcodeDetector!()

    async function start() {
      try {
        stream = await navigator.mediaDevices.getUserMedia({
          video: { facingMode: 'environment' }, // rear camera on a phone
        })
        if (stopped) return
        const video = videoRef.current!
        video.srcObject = stream
        await video.play()

        // Poll a few times a second until a code is found.
        timer = window.setInterval(async () => {
          try {
            const codes = await detector.detect(video)
            if (codes.length > 0) {
              onScan(codes[0].rawValue)
            }
          } catch {
            // transient decode errors are fine; keep trying
          }
        }, 300)
      } catch {
        setError('Geen toegang tot de camera.')
      }
    }
    start()

    return () => {
      stopped = true
      if (timer) window.clearInterval(timer)
      stream?.getTracks().forEach((t) => t.stop())
    }
  }, [onScan])

  return (
    <div className="flex flex-col gap-3 rounded-xl border border-stone-200 bg-white p-4 shadow-sm">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-medium uppercase tracking-wide text-stone-400">
          Scan een label
        </h3>
        <button onClick={onClose} className="text-sm text-stone-500 hover:underline">
          Sluiten
        </button>
      </div>
      {error ? (
        <p className="text-sm text-red-600">{error}</p>
      ) : (
        <video ref={videoRef} className="w-full rounded-lg bg-black" muted playsInline />
      )}
      <p className="text-xs text-stone-400">Houd de QR-code voor de camera.</p>
    </div>
  )
}
