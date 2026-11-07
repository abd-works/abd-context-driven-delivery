export const STATES: Record<string, { label: string; color: string }> = {
  done: { label: 'done', color: 'var(--done)' },
  in_progress: { label: 'in progress', color: 'var(--progress)' },
  violations: { label: 'violations', color: 'var(--violations)' },
  not_started: { label: 'not started', color: 'var(--idle)' },
}

// Each practice's colour lights up with progress: dim until started, then brighter, then full when done.
// How bright a fidelity's segment and tile are: almost black when its practice is off for the ticket, then brighter as
// its work goes from not started to started to done. Violations stay bright so they are seen.
export const WORK_LIGHT: Record<string, number> = { off: 0.12, not_started: 0.35, in_progress: 0.7, violations: 1, done: 1 }

export const ACTION_STANDINGS: Record<string, { mark: string; color: string; label: string }> = {
  done: { mark: '✓', color: 'var(--done)', label: 'done' },
  in_progress: { mark: '…', color: 'var(--progress)', label: 'in progress' },
  to_do: { mark: '○', color: 'var(--muted)', label: 'to do' },
}

export const STEP_FAILED = '✕'

// The size the board draws each stage's scope at, by the shape Python names: wide and shallow for the whole solution,
// narrow and deep for one story.
export const SCOPE_SIZES: Record<string, { width: number; height: number }> = {
  solution: { width: 36, height: 12 },
  sprint: { width: 16, height: 22 },
  story: { width: 11, height: 28 },
}

export const FORMAT_GROUPS = [
  { label: 'diagram', formats: ['drawio'] },
  { label: 'markdown', formats: ['markdown'] },
  { label: 'code', formats: ['python', 'typescript', 'javascript', 'java', 'html'] },
]

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
