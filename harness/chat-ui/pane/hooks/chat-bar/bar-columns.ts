import type { ChatBarClient } from './chat-bar-client'
import type { FormatChips } from './format-choices-client'
import type { OverlayChips } from './overlay-choices-client'

// Where each button sits on the chat bar's line, counted in cells as the line draws them, so the list box a button
// opens lines up with it: a list on the left of the line starts at its button's column, and one at the right end ends
// where its button ends.

// The canvas's glyph for each format group; a group with none shows its name.
export const FORMAT_GLYPHS: Record<string, string> = { markdown: 'M↓', diagram: '◇', code: '</>', canvas: '▦' }
export const formatGlyphOf = (label: string): string => FORMAT_GLYPHS[label] ?? label

// The health mark and its gap, the stage chip (its padding, icon and ▾) and its gap, │ and its gap.
const HEALTH_AND_GAP = 2
const STAGE_CHIP_AND_GAP = 5
const SEPARATOR_AND_GAP = 2
const GAP = 1

// The stage button's column: just after the health mark.
export const stageColumn = HEALTH_AND_GAP

// The overlays' + column: after the stage chip, │, and each fidelity dot with its violation count and its gap.
export function overlayColumnOf(chatBar: ChatBarClient): number {
  const dots = chatBar.fidelities.reduce((cells, fidelity) => cells + 1 + (fidelity.violationCount ? String(fidelity.violationCount).length : 0) + GAP, 0)
  return HEALTH_AND_GAP + STAGE_CHIP_AND_GAP + SEPARATOR_AND_GAP + dots
}

// The overlay chips: the + and each chosen pattern's icon, a gap between each; none drawn while there are no choices.
function overlayCellsOf(overlays: OverlayChips): number {
  if (!overlays.choices.length) return 0
  return 1 + overlays.chosen.reduce((cells, choice) => cells + GAP + choice.icon.length, 0) + GAP
}

// The format chips, each its glyph padded by a cell either side, the group a cell from its neighbours.
function formatCellsOf(formats: FormatChips): number {
  if (!formats.choices.length) return 0
  return 1 + formats.choices.reduce((cells, choice) => cells + formatGlyphOf(choice.label).length + 2, 0) + 1 + GAP
}

// The action button's column: after the overlay chips and the format chips.
export function actionColumnOf(chatBar: ChatBarClient, overlays: OverlayChips, formats: FormatChips): number {
  return overlayColumnOf(chatBar) + overlayCellsOf(overlays) + formatCellsOf(formats)
}

// The icons after the session name at the right end: handoff, files while there are fidelities, and close in a ticket's
// own chat, a gap between each.
function sessionButtonCellsOf(chatBar: ChatBarClient): number {
  if (!chatBar.hasSession) return 0
  const hasFiles = chatBar.actionFidelities.length > 0 || chatBar.fidelities.length > 0
  const icons = 1 + (hasFiles ? 1 : 0) + (chatBar.isMain ? 0 : 1)
  return GAP + icons + (icons - 1) * GAP
}

// The repo button: the repository's name, or "repo" while it has none, and its ⑂.
export const REPO_GLYPH = '⑂'
export const repoWordOf = (chatBar: ChatBarClient): string => chatBar.repoName || 'repo'
const repoButtonCellsOf = (chatBar: ChatBarClient): number => repoWordOf(chatBar).length + 1 + REPO_GLYPH.length

// How far the repo list's right edge sits from the line's end: the session buttons after the repo button.
export function repoListRightOf(chatBar: ChatBarClient): number {
  return sessionButtonCellsOf(chatBar)
}

// How far the session list's right edge sits from the line's end: the repo button and the session buttons after "main +".
export function sessionListRightOf(chatBar: ChatBarClient): number {
  return GAP + repoButtonCellsOf(chatBar) + sessionButtonCellsOf(chatBar)
}
