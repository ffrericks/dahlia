import type { Origin } from './api/plants'

export const ORIGIN_LABELS: Record<Origin, string> = {
  purchased: 'Gekocht',
  gifted: 'Gekregen',
  split: 'Afsplitsing',
  seedling: 'Zaailing',
  unknown: 'Onbekend',
}

export const STATE_LABELS: Record<string, string> = {
  stored: 'In opslag',
  planted: 'Geplant',
  discarded: 'Weggegooid',
  given_away: 'Weggegeven',
  survived_winter: 'Winter overleefd',
}

export function stateLabel(state: string): string {
  return STATE_LABELS[state] ?? state
}

export const EYE_STATUS_LABELS: Record<string, string> = {
  awaiting_eye: 'Wacht op oog',
  has_eye: 'Heeft oog',
  blind: 'Blind',
}

export function eyeStatusLabel(status: string | null): string {
  if (status === null) return 'Onbekend'
  return EYE_STATUS_LABELS[status] ?? status
}
