import type { EngineInterface } from 'claude-code'

import { BRAND } from '../brand'
import { actionOf } from './action-button-view'
import type { ChatBarClient } from './chat-bar-client'
import type { ChatBarDraw } from './chat-bar-view'

type ElementTable = ReturnType<EngineInterface['ui']['resolve']>

// The hover group of the session name and its card: the pointer on either keeps the card shown.
export const CARD_SCOPE = 'session-card'

// The cells each part of the line takes, as LineView lays it out with a gap of one between parts, so a card row can
// start in the column of the part it sits over.
const GAP = 1
const HEALTH_MARK = 1
const LIST_BUTTON = 1
const SEPARATOR = 1
const DOT = 1
const ACTION_BUTTON = 2
const STAGE_ICON = 1
// An outlined stage icon has a border cell each side.
const OUTLINE = 2
// The card's own border and padding, which its rows start inside.
const CARD_FRAME = 2

// The column each fidelity's dot and the shown stage's icon start at on the line.
function columnsOf(chatBar: ChatBarClient): { fidelities: number[]; stage: number } {
  let column = HEALTH_MARK + GAP + chatBar.sessionName.length + GAP + LIST_BUTTON + GAP + SEPARATOR + GAP
  const fidelities = chatBar.fidelities.map(fidelity => {
    const start = column
    column += DOT + (fidelity.violationCount ? String(fidelity.violationCount).length : 0) + GAP
    return start
  })
  column += (actionOf(chatBar) ? ACTION_BUTTON + GAP : 0) + SEPARATOR + GAP
  let stage = column
  for (const entry of chatBar.stages) {
    if (entry.stage === chatBar.shownStage) stage = column
    column += STAGE_ICON + (entry.status === 'in_progress' || entry.isShown ? OUTLINE : 0) + GAP
  }
  return { fidelities, stage }
}

const indentFor = (column: number): number => Math.max(0, column - CARD_FRAME)

// The session card, laid out over the strip beneath it: the server health panel stacked on top, then each fidelity's
// colour, name, state and folder starting in its dot's column, and the shown stage starting in its icon's column.
// Hovering the session name shows it; a press on the name pins it.
export function SessionCardView({ Box, Text }: ElementTable, { chatBar, view, health }: ChatBarDraw) {
  if (!chatBar.hasSession) return null
  const shown = view.isCardOpen ? {} : { display: 'none' as const, hover: { display: 'flex' as const, scope: CARD_SCOPE } }
  const columns = columnsOf(chatBar)
  return (
    <Box key="session-card" flexDirection="column">
      <Box flexDirection="column" paddingX={1} borderStyle="single" borderColor={BRAND.border} backgroundColor={BRAND.raised} {...shown}>
        {health.panel}
        {chatBar.fidelities.map((fidelity, index) => (
          <Box key={`card-${fidelity.fidelity}`} flexDirection="row" gap={1} marginLeft={indentFor(columns.fidelities[index])}>
            <Text color={fidelity.colour}>{fidelity.mark}</Text>
            <Text color={BRAND.text}>{`${fidelity.name} ${fidelity.word}`}</Text>
            <Text color={BRAND.muted}>{fidelity.folder}</Text>
          </Box>
        ))}
        <Box key="card-stage" marginLeft={indentFor(columns.stage)}>
          <Text weight="semibold" color={BRAND.accent}>{chatBar.shownStage}</Text>
        </Box>
      </Box>
    </Box>
  )
}
