import type { EngineInterface } from 'claude-code'

import { BRAND } from '../brand'
import { GlyphButtonView } from '../glyph-button-view'
import { actionOf } from './action-button-view'
import type { ChatBarClient } from './chat-bar-client'
import type { ChatBarDraw } from './chat-bar-view'
import { selectFidelity, type FidelityClient } from './fidelity-client'
import { openFiles } from './fidelity-files-client'
import { closeCard } from './session-dialogs-client'

type ElementTable = ReturnType<EngineInterface['ui']['resolve']>

// The hover group of the session name and its card: the pointer on either keeps the card shown.
export const CARD_SCOPE = 'session-card'

// The line and the card share two column widths, so the card's columns start over the parts of the line they name, as
// on the canvas. The card's border and padding take the two cells the health mark and its gap take on the line.
// name: the session name, gap, ▾, gap, │, gap. fidelities: the dots and the action chip on the line, and the widest
// fidelity row on the card, with a gap after it.
export type CardColumns = { name: number; fidelities: number }
const NAME_TO_DOTS = 5
const ACTION_CHIP = 4
const GAP = 1
// The stage path's own margin and the line's gap before it, which the card's folder column starts after.
export const STAGE_PATH_OFFSET = 2

function rowWidthOf(fidelity: FidelityClient): number {
  return `■ ${fidelity.name} ${fidelity.mark} ${fidelity.word}`.length
}

function dotsWidthOf(chatBar: ChatBarClient): number {
  const dots = chatBar.fidelities.reduce((cells, fidelity) => cells + 1 + (fidelity.violationCount ? String(fidelity.violationCount).length : 0) + GAP, 0)
  return dots + (actionOf(chatBar) ? ACTION_CHIP : 0)
}

export function cardColumnsOf(chatBar: ChatBarClient): CardColumns {
  const widest = Math.max(dotsWidthOf(chatBar), ...chatBar.fidelities.map(rowWidthOf))
  return { name: chatBar.sessionName.length + NAME_TO_DOTS, fidelities: widest + GAP }
}

// The session name over the name, FIDELITY over the dots, the shown stage in orange over the stage path, and a ✕ that
// closes a card pinned open.
function HeaderView($: EngineInterface, elements: ElementTable, chatBar: ChatBarClient, columns: CardColumns) {
  const { Box, Text } = elements
  return (
    <Box key="card-header" flexDirection="row">
      <Box width={columns.name}>
        <Text weight="bold" color={BRAND.text}>{chatBar.sessionName}</Text>
      </Box>
      <Box width={columns.fidelities + STAGE_PATH_OFFSET}>
        <Text size="caption" color={BRAND.muted}>FIDELITY</Text>
      </Box>
      <Box key="card-stage">
        <Text weight="bold" color={BRAND.accent}>{chatBar.shownStage}</Text>
      </Box>
      <Box flexGrow={1} />
      {GlyphButtonView(elements, 'card-close', '✕', BRAND.muted, () => closeCard($))}
    </Box>
  )
}

// One fidelity under the dots: its square, its name (a press selects it) and its state, underlined when selected; its
// folder under the stage path as a small chip, a press showing its files.
function FidelityRowView($: EngineInterface, elements: ElementTable, fidelity: FidelityClient, columns: CardColumns) {
  const { Box, Text } = elements
  const nameColour = fidelity.status === 'not_started' ? BRAND.muted : BRAND.text
  return (
    <Box key={`card-${fidelity.fidelity}`} flexDirection="row" marginLeft={columns.name} alignItems="center">
      <Box width={columns.fidelities + STAGE_PATH_OFFSET}>
        <Box key={`card-cell-${fidelity.fidelity}`} flexDirection="row" gap={1} alignItems="center">
          <Text color={fidelity.shade}>■</Text>
          {GlyphButtonView(elements, `card-pick-${fidelity.fidelity}`, fidelity.name, nameColour, () => selectFidelity($, fidelity), fidelity.isSelected)}
          <Text color={fidelity.lookColour} underline={fidelity.isSelected}>{`${fidelity.mark} ${fidelity.word}`}</Text>
        </Box>
      </Box>
      {fidelity.folder ? (
        <Box key={`card-folder-chip-${fidelity.fidelity}`} paddingX={1} backgroundColor={BRAND.surface}>
          {GlyphButtonView(elements, `card-folder-${fidelity.fidelity}`, `▸ ${fidelity.folder}`, BRAND.muted, () => openFiles($, fidelity))}
        </Box>
      ) : null}
    </Box>
  )
}

// The session card above the line: the server health panel on top, then, once there is a session, the canvas's
// orange-edged card of the shown stage's fidelities. Hovering the session name or the health mark shows it; a press on
// either pins it, and ✕ or another press closes it.
export function SessionCardView($: EngineInterface, elements: ElementTable, { chatBar, view, health }: ChatBarDraw) {
  const { Box } = elements
  const shown = view.isCardOpen ? {} : { display: 'none' as const, hover: { display: 'flex' as const, scope: CARD_SCOPE } }
  const columns = cardColumnsOf(chatBar)
  return (
    <Box key="session-card" flexDirection="column">
      <Box flexDirection="column" gap={1} {...shown}>
        {health.panel}
        {chatBar.hasSession ? (
          <Box key="card-grid" flexDirection="column" paddingX={1} borderStyle="round" borderColor={BRAND.accent} backgroundColor={BRAND.raised}>
            {HeaderView($, elements, chatBar, columns)}
            {chatBar.fidelities.map(fidelity => FidelityRowView($, elements, fidelity, columns))}
          </Box>
        ) : null}
      </Box>
    </Box>
  )
}
