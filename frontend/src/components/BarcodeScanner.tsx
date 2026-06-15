import { useEffect, useRef, useState } from 'react'

interface Props {
  onScan: (value: string) => void
  onClose: () => void
}

// In-app scanning needs the Barcode API + camera, which browsers only allow in a
// secure context (https or localhost) — not over plain http on a LAN IP.
export const scannerSupported =
  typeof window !== 'undefined' &&
  'BarcodeDetector' in window &&
  window.isSecureContext &&
  !!navigator.mediaDevices

function makeDetector(): BarcodeDetector {
  // Prefer QR; fall back to all formats if the browser rejects the option.
  try {
    return new window.BarcodeDetector!({ formats: ['qr_code'] })
  } catch {
    return new window.BarcodeDetector!()
  }
}

export default function BarcodeScanner({ onScan, onClose }: Props) {
  const videoRef = useRef<HTMLVideoElement>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!scannerSupported) {
      setError('Scannen in de app kan niet in deze browser. Gebruik de camera-app van je telefoon.')
      return
    }

    let stream: MediaStream | null = null
    let timer: number | undefined
    let stopped = false
    const detector = makeDetector()

    async function start() {
      try {
        stream = await navigator.mediaDevices.getUserMedia({
          video: { facingMode: 'environment' }, // rear camera on a phone
        })
        if (stopped) return
        const video = videoRef.current!
        video.srcObject = stream
        await video.play()

        // Poll a few times a second until a code is found, then stop immediately.
        timer = window.setInterval(async () => {
          try {
            const codes = await detector.detect(video)
            if (codes.length > 0 && !stopped) {
              stopped = true
              if (timer) window.clearInterval(timer)
              onScan(codes[0].rawValue)
            }
          } catch {
            // transient decode errors are fine; keep trying
          }
        }, 250)
      } catch {
        setError('Geen toegang tot de camera. Geef toestemming, of gebruik de camera-app.')
      }
    }
    start()

    return () => {
      stopped = true
      if (timer) window.clearInterval(timer)
      stream?.getTracks().forEach((track) => track.stop())
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
        <>
          <div className="relative mx-auto w-full max-w-sm">
            <video
              ref={videoRef}
              className="aspect-square w-full rounded-lg bg-black object-cover"
              muted
              playsInline
            />
            {/* viewfinder frame */}
            <div className="pointer-events-none absolute inset-6 rounded-lg border-2 border-white/70" />
          </div>
          <p className="text-center text-xs text-stone-400">Houd de QR-code voor de camera.</p>
        </>
      )}
    </div>
  )
}
