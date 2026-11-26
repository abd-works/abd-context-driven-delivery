// The chat bar's glyph for each group of formats (harness/chat-ui/pane/hooks/chat-bar/bar-columns.ts FORMAT_GLYPHS), so
// a format looks the same on the bar and here. A group with no glyph shows its first and last letter, as it does there.
const FORMAT_GLYPHS: Record<string, string> = { markdown: 'M↓', diagram: '◇', code: '</>', canvas: '▦' }

export const formatGlyphOf = (label: string): string => FORMAT_GLYPHS[label] ?? `${label.charAt(0).toUpperCase()}${label.slice(-1)}`
