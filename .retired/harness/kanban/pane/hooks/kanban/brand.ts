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
  accentText: '#FF6A2E',
  accentPressed: '#C64514',
  onAccent: '#0B0B0B',
  success: '#22C55E',
  warning: '#F59E0B',
  error: '#EF4444',
  // The canvas's failing line is the error colour at 16% over the canvas; a Box has no see-through colour.
  errorWash: '#2F1414',
  // Only surfaces that draw a browser's colors read the last pair, how much of the board shows through.
  backdrop: '#0000008C',
}

export const STATES: Record<string, { label: string; color: string }> = {
  done: { label: 'reviewed', color: BRAND.success },
  in_progress: { label: 'in progress', color: BRAND.warning },
  violations: { label: 'violations', color: BRAND.error },
  not_started: { label: 'not started', color: BRAND.idle },
}

// How far a card's segment shows its practice's color: on the canvas, its opacity for each state.
export const SEGMENT_LIGHT: Record<string, number> = { not_started: 0.2, in_progress: 0.8, violations: 1, done: 1 }
export const DIM_TEXT_LIGHT = 0.45
// The canvas's opacity for a practice turned off: its tiles, its label, and a main button that is off.
export const OFF_TILE_LIGHT = 0.2
export const OFF_LABEL_LIGHT = 0.5
export const OFF_BUTTON_LIGHT = 0.35

const channelsOf = (color: string): number[] => [1, 3, 5].map(start => Number.parseInt(color.slice(start, start + 2), 16))

// A color at part strength over the surface. dimColor does not show on text given a color, and a Box has no opacity.
export function faded(color: string, light: number): string {
  const ground = channelsOf(BRAND.surface)
  const mixed = channelsOf(color).map((channel, index) => Math.round(channel * light + (ground[index] ?? 0) * (1 - light)))
  return `#${mixed.map(channel => channel.toString(16).padStart(2, '0')).join('')}`
}

export const ACTION_STANDINGS: Record<string, { mark: string; color: string }> = {
  done: { mark: '✓', color: BRAND.success },
  in_progress: { mark: '…', color: BRAND.warning },
  to_do: { mark: '○', color: BRAND.muted },
}

export const STEP_FAILED = '✕'

export const PRACTICES = [
  { key: 'stories', name: 'Stories', prefix: 'stories-', color: '#6BCB77' },
  { key: 'ddd', name: 'DDD', prefix: 'ddd-', color: '#6C5CE7' },
  { key: 'ux', name: 'UX', prefix: 'ux-', color: '#E84393' },
  { key: 'clean_engineering', name: 'CE', prefix: 'clean_engineering-', color: '#4FC3F7' },
  { key: 'bdd', name: 'BDD', prefix: 'bdd-', color: '#6BCB77' },
]

export const practiceOf = (slug: string) => PRACTICES.find(candidate => slug.startsWith(candidate.prefix))

const EXAMPLES = 'https://forge.abdworks.net/abd-context-driven-delivery/examples'

// What each stage covers, drawn as a shape that narrows and deepens along the board.
export const STAGE_SCOPES: Record<string, { name: string; reach: string; covers: string; width: number; height: number; href: string }> = {
  Discovery: { name: 'Whole solution', reach: 'wide / shallow', covers: 'outcomes · scope · boundaries', width: 36, height: 12, href: `${EXAMPLES}/discovery.html` },
  Specification: { name: 'Sprint', reach: 'narrow / deeper', covers: 'behaviour · design · logic', width: 16, height: 22, href: `${EXAMPLES}/specification.html` },
  Implementation: { name: 'Story', reach: 'narrowest / deep', covers: 'tests · code · interface', width: 11, height: 28, href: `${EXAMPLES}/implementation.html` },
}

// A Button holds only text, so a format group's icon is a glyph.
export const FORMAT_GROUPS = [
  { label: 'diagram', glyph: '◫', formats: ['drawio'] },
  { label: 'markdown', glyph: 'M↓', formats: ['markdown'] },
  { label: 'code', glyph: '</>', formats: ['python', 'typescript', 'javascript', 'java', 'html'] },
]

export const EXPAND_MARK = '⤢'
export const COLLAPSE_MARK = '⤡'

export const scopeShape = (width: number, height: number): string =>
  `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${width} ${height}"><rect x="1" y="1" width="${width - 2}" height="${height - 2}" rx="1" fill="none" stroke="#e5531a" stroke-width="2"/></svg>`

// The brand's chevron: the symbol-only mark is the one for compact product UI.
export const CHEVRON =
  '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 256 256"><path fill="#e5531a" fill-rule="evenodd" ' +
  'd="M52.98,20.31l150.04,84.18v46.44S52.98,235.69,52.98,235.69v-54.77s104.7-53.41,104.7-53.41l-104.7-52.83V20.31Z"/></svg>'
export const CHEVRON_PIXELS = 18
