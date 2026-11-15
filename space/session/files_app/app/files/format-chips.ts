// The chat bar's glyph for each group of formats (harness/chat-ui/pane/hooks/chat-bar/bar-columns.ts FORMAT_GLYPHS), so
// a format looks the same on the bar and here.
const FORMAT_GLYPHS: Record<string, string> = { markdown: 'M↓', diagram: '◇', code: '</>', canvas: '▦' }

export const formatGlyphOf = (label: string): string => FORMAT_GLYPHS[label] ?? label
