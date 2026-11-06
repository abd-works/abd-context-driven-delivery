import type { EngineInterface } from 'claude-code'

import { BRAND } from '../brand'
import { actionOf } from './action-button-view'
import type { ChatBarClient } from './chat-bar-client'
import type { ChatBarDraw } from './chat-bar-view'
import { selectFidelity, type FidelityClient } from './fidelity-client'
import { openFiles } from './fidelity-files-client'

type ElementTable = ReturnType<EngineInterface['ui']['resolve']>

// The hover group of the session name and its card: the pointer on either keeps the card shown.
export const CARD_SCOPE = 'session-card'

// The cells each part of the line takes on the terminal, as LineView lays it out with a gap of one between parts, so
// the card's columns start over the parts they name.
const GAP = 1
const HEALTH_MARK = 1
// A bordered Button draws `[ ▾ ]`.
const LIST_BUTTON = 5
const SEPARATOR = 1
const DOT = 1
// The orange chip ` ▶ ` and its ▾.
const ACTION_BUTTON = 4
const STAGE_PATH_MARGIN = 1
// The card's own border and padding, which its rows start inside.
const CARD_FRAME = 2

type Columns = { name: number; fidelities: number; stages: number }

// The columns the session name, the first fidelity dot, and the stage path start at on the line.
function columnsOf(chatBar: ChatBarClient): Columns {
  const name = HEALTH_MARK + GAP
  const fidelities = name + chatBar.sessionName.length + GAP + LIST_BUTTON + GAP + SEPARATOR + GAP
  const dots = chatBar.fidelities.reduce((cells, fidelity) => cells + DOT + (fidelity.violationCount ? String(fidelity.violationCount).length : 0) + GAP, 0)
  const stages = fidelities + dots + (actionOf(chatBar) ? ACTION_BUTTON + GAP : 0) + STAGE_PATH_MARGIN
  return { name, fidelities, stages }
}

const indentFor = (column: number): number => Math.max(0, column - CARD_FRAME)

// The session name over the name, FIDELITY over the dots, and the shown stage over the stage path.
function HeaderView({ Box, Text }: ElementTable, chatBar: ChatBarClient, columns: Columns) {
  return (
    <Box key="card-header" flexDirection="row" marginLeft={indentFor(columns.name)}>
      <Box width={columns.fidelities - columns.name}>
        <Text weight="bold" color={BRAND.text}>{chatBar.sessionName}</Text>
      </Box>
      <Box width={columns.stages - columns.fidelities}>
        <Text size="caption" color={BRAND.muted}>FIDELITY</Text>
      </Box>
      <Box key="card-stage">
        <Text weight="bold" color={BRAND.accent}>{chatBar.shownStage}</Text>
      </Box>
    </Box>
  )
}

// One fidelity under the dots: its square, its name and its state, a press selecting it; its folder under the stage
// path, a press showing its files.
function FidelityRowView($: EngineInterface, { Box, Button, Text }: ElementTable, fidelity: FidelityClient, columns: Columns) {
  return (
    <Box key={`card-${fidelity.fidelity}`} flexDirection="row" marginLeft={indentFor(columns.fidelities)}>
      <Box width={columns.stages - columns.fidelities}>
        <Box key={`card-cell-${fidelity.fidelity}`} flexDirection="row" gap={1} alignItems="center">
          <Text color={fidelity.shade}>■</Text>
          <Button key={`card-pick-${fidelity.fidelity}`} plain label={fidelity.name} dimColor={fidelity.status === 'not_started'} onPress={() => selectFidelity($, fidelity)} />
          <Text color={fidelity.lookColour}>{`${fidelity.mark} ${fidelity.word}`}</Text>
        </Box>
      </Box>
      {fidelity.folder ? <Button key={`card-folder-${fidelity.fidelity}`} label={`▸ ${fidelity.folder}`} dimColor onPress={() => openFiles($, fidelity)} /> : null}
    </Box>
  )
}

// The session card, laid out over the strip beneath it: the server health panel on top, then the canvas's orange-edged
// grid, whose columns start over the session name, the dots and the stage path. Hovering the session name shows it; a
// press on the name pins it.
export function SessionCardView($: EngineInterface, elements: ElementTable, { chatBar, view, health }: ChatBarDraw) {
  const { Box } = elements
  if (!chatBar.hasSession) return null
  const shown = view.isCardOpen ? {} : { display: 'none' as const, hover: { display: 'flex' as const, scope: CARD_SCOPE } }
  const columns = columnsOf(chatBar)
  return (
    <Box key="session-card" flexDirection="column">
      <Box flexDirection="column" gap={1} {...shown}>
        {health.panel}
        <Box key="card-grid" flexDirection="column" paddingX={1} borderStyle="round" borderColor={BRAND.accent} backgroundColor={BRAND.raised}>
          {HeaderView(elements, chatBar, columns)}
          {chatBar.fidelities.map(fidelity => FidelityRowView($, elements, fidelity, columns))}
        </Box>
      </Box>
    </Box>
  )
}
