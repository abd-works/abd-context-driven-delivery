// What the canvas names and colours, in one place, so a practice looks the same on a card, a tile, and in help.
export const PRACTICES = [
  { key: 'stories', name: 'Stories', prefix: 'stories-', color: '#6BCB77' },
  { key: 'ddd', name: 'DDD', prefix: 'ddd-', color: '#6C5CE7' },
  { key: 'ux', name: 'UX', prefix: 'ux-', color: '#E84393' },
  { key: 'clean_engineering', name: 'CE', prefix: 'clean_engineering-', color: '#4FC3F7' },
  { key: 'bdd', name: 'BDD', prefix: 'bdd-', color: '#6BCB77' },
]

export type Practice = (typeof PRACTICES)[number]

export const practiceOf = (slug: string): Practice | undefined => PRACTICES.find(candidate => slug.startsWith(candidate.prefix))

export const fidelityOf = (slug: string): string => slug.slice(practiceOf(slug)?.prefix.length ?? 0)

export const STATES: Record<string, { label: string; color: string }> = {
  done: { label: 'reviewed', color: 'var(--reviewed)' },
  in_progress: { label: 'in progress', color: 'var(--progress)' },
  violations: { label: 'violations', color: 'var(--violations)' },
  not_started: { label: 'not started', color: 'var(--idle)' },
}

// Each practice's colour lights up with progress: dim until started, then brighter, then full when reviewed.
export const SEGMENT_LIGHT: Record<string, number> = { not_started: 0.2, in_progress: 0.8, violations: 1, done: 1 }

export const ACTION_STANDINGS: Record<string, { mark: string; color: string; label: string }> = {
  done: { mark: '✓', color: 'var(--reviewed)', label: 'done' },
  in_progress: { mark: '…', color: 'var(--progress)', label: 'in progress' },
  to_do: { mark: '○', color: 'var(--muted)', label: 'to do' },
}

export const STEP_FAILED = '✕'

const EXAMPLES = 'https://forge.abdworks.net/abd-context-driven-delivery/examples'

// What each stage covers, drawn as a shape that narrows and deepens along the board.
export const STAGE_SCOPES: Record<string, { name: string; reach: string; covers: string; width: number; height: number; href: string }> = {
  Discovery: { name: 'Whole solution', reach: 'wide / shallow', covers: 'outcomes · scope · boundaries', width: 36, height: 12, href: `${EXAMPLES}/discovery.html` },
  Specification: { name: 'Sprint', reach: 'narrow / deeper', covers: 'behaviour · design · logic', width: 16, height: 22, href: `${EXAMPLES}/specification.html` },
  Implementation: { name: 'Story', reach: 'narrowest / deep', covers: 'tests · code · interface', width: 11, height: 28, href: `${EXAMPLES}/implementation.html` },
}

export const FORMAT_GROUPS = [
  { label: 'diagram', formats: ['drawio'] },
  { label: 'markdown', formats: ['markdown'] },
  { label: 'code', formats: ['python', 'typescript', 'javascript', 'java', 'html'] },
]

export const TILE_ACTIONS = ['generate', 'render', 'sketch', 'iterate', 'document']

export const countOf = (count: number, noun: string): string => `${count} ${count === 1 ? noun : `${noun}s`}`

const MINUTE = 60_000
const MINUTES_PER_HOUR = 60
const HOURS_PER_DAY = 24

export function ageOf(now: number, stamp: string): string {
  if (!stamp) return 'no activity yet'
  const minutes = Math.floor((now - Date.parse(stamp)) / MINUTE)
  if (minutes < 1) return 'just now'
  if (minutes < MINUTES_PER_HOUR) return `${minutes} min ago`
  const hours = Math.floor(minutes / MINUTES_PER_HOUR)
  if (hours < HOURS_PER_DAY) return `${countOf(hours, 'hour')} ago`
  const days = Math.floor(hours / HOURS_PER_DAY)
  return days === 1 ? 'yesterday' : `${days} days ago`
}

export const guidanceSlug = (slug: string): string => slug.replaceAll('_', '-')
