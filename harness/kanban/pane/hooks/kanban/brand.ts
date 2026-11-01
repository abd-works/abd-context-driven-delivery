// abd.works engineering (dark) tokens, from the brand repository's css/brand.css. The pane paints its own canvas,
// so these colors hold on either Claude Code theme.
export const BRAND = {
  canvas: '#0B0B0B',
  surface: '#111113',
  raised: '#1B1B20',
  border: '#2A2A2A',
  text: '#E8E8ED',
  muted: '#9B9BA8',
  idle: '#71717A',
  accent: '#E5531A',
  success: '#22C55E',
  warning: '#F59E0B',
  error: '#EF4444',
}

export const STATES: Record<string, { label: string; color: string }> = {
  done: { label: 'reviewed', color: BRAND.success },
  in_progress: { label: 'in progress', color: BRAND.warning },
  violations: { label: 'violations', color: BRAND.error },
  not_started: { label: 'not started', color: BRAND.idle },
}

export const ACTION_MARKS: Record<string, string> = { done: '✓', in_progress: '…', to_do: '·' }

export const PRACTICES = [
  { key: 'stories', name: 'Stories', prefix: 'stories-', color: '#6BCB77' },
  { key: 'ddd', name: 'DDD', prefix: 'ddd-', color: '#6C5CE7' },
  { key: 'ux', name: 'UX', prefix: 'ux-', color: '#E84393' },
  { key: 'clean_engineering', name: 'CE', prefix: 'clean_engineering-', color: '#4FC3F7' },
  { key: 'bdd', name: 'BDD', prefix: 'bdd-', color: '#6BCB77' },
]

// The brand's chevron: the symbol-only mark is the one for compact product UI.
export const CHEVRON =
  '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 256 256"><path fill="#e5531a" fill-rule="evenodd" ' +
  'd="M52.98,20.31l150.04,84.18v46.44S52.98,235.69,52.98,235.69v-54.77s104.7-53.41,104.7-53.41l-104.7-52.83V20.31Z"/></svg>'
export const CHEVRON_PIXELS = 18
