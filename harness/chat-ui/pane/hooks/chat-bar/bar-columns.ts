import type { ChatBarClient } from './chat-bar-client'

// Each list box is drawn against the button that opens it, so its left edge sits under the button wherever the line
// puts it. The buttons at the right end of the line leave a list little room, so a list wider than the room from its
// button to the line's end is moved left by the difference, counted in cells, rather than cut off at the edge.

// The canvas's glyph for each format group; a group with none shows its name.
// A format that is a group of its own, such as BDD's call graphs in realization, gets a glyph here; one not listed shows
// its first and last letter, as an overlay does, so a long name never widens the chat bar.
export const FORMAT_GLYPHS: Record<string, string> = { markdown: 'M↓', diagram: '◇', code: '</>', canvas: '▦', realization: '⇢', thin_slice: '☰' }
export const formatGlyphOf = (label: string): string => FORMAT_GLYPHS[label] ?? `${label.charAt(0).toUpperCase()}${label.slice(-1)}`

const GAP = 1
const HEALTH_MARK = 1
// A list box's round border and its padding, on both sides.
const LIST_FRAME = 4

// The icons after the session name at the right end, as SessionButtonsView draws them: push and push & merge in a
// repository, restart, and close in a ticket's own chat, a gap between each.
function sessionButtonCellsOf(chatBar: ChatBarClient): number {
  if (!chatBar.hasSession) return 0
  const icons = (chatBar.isClone ? 2 : 0) + 1 + (chatBar.isMain || chatBar.isPlainFolder ? 0 : 1)
  return GAP + icons + (icons - 1) * GAP
}

// The repo button, ⑂, its tip the repository's name, or "repo" while it has none.
export const REPO_GLYPH = '⑂'
export const repoWordOf = (chatBar: ChatBarClient): string => chatBar.repoName || 'repo'

// The session button after the repo button, +, its tip the session's name, or "main".
export const SESSION_GLYPH = '+'
export const sessionWordOf = (chatBar: ChatBarClient): string => chatBar.sessionName || 'main'
const sessionButtonWordCellsOf = (_chatBar: ChatBarClient): number => SESSION_GLYPH.length
const repoButtonWordCellsOf = (_chatBar: ChatBarClient): number => GAP + REPO_GLYPH.length

// The health mark and the version badge, such as v0.4, that end the line, a gap before each.
const endMarkCellsOf = (versionLabel: string): number => GAP + HEALTH_MARK + GAP + versionLabel.length

// From the start of "main +" to the line's end: the button, the session buttons, the health mark, and the version badge.
const sessionButtonRoomOf = (chatBar: ChatBarClient, versionLabel: string): number =>
  sessionButtonWordCellsOf(chatBar) + sessionButtonCellsOf(chatBar) + endMarkCellsOf(versionLabel)

// How far left of its button a list whose widest line is contentCells must start to end at the line's end; 0 when it fits.
const shiftToFit = (contentCells: number, room: number): number => Math.min(0, room - (contentCells + LIST_FRAME))

// The session list's offset from "main +".
export function sessionListShiftOf(chatBar: ChatBarClient, versionLabel: string, contentCells: number): number {
  return shiftToFit(contentCells, sessionButtonRoomOf(chatBar, versionLabel))
}

// The repo list's offset from the repository's name, the button just before "main +".
export function repoListShiftOf(chatBar: ChatBarClient, versionLabel: string, contentCells: number): number {
  return shiftToFit(contentCells, repoButtonWordCellsOf(chatBar) + sessionButtonRoomOf(chatBar, versionLabel))
}
