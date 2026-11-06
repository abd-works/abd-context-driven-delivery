import type { EngineInterface } from 'claude-code'

import type { ActionPickerJson, ChatBarViewJson, FidelityFilesJson } from '../../types'
import { BRAND } from '../brand'
import { ActionButtonView, PickerView } from './action-button-view'
import { runHandoff, type ChatBarClient } from './chat-bar-client'
import { openBoard, selectFidelity, type FidelityClient } from './fidelity-client'
import { openFiles } from './fidelity-files-client'
import { FidelityFilesView } from './fidelity-files-view'
import { CARD_SCOPE, SessionCardView } from './session-card-view'
import { openClose } from './session-client'
import { toggleCard, toggleSessionList } from './session-dialogs-client'
import { ActivateView, CloseView, SessionListView } from './session-dialogs-view'
import { selectStage, type StageClient } from './stage-client'

type ElementTable = ReturnType<EngineInterface['ui']['resolve']>

// What one draw of the chat bar reads: the client built from board.show, which boxes are open above the line, the
// server health band at the mark and its panel for the session card, and the columns the band may fill.
export type ChatBarDraw = {
  chatBar: ChatBarClient
  view: ChatBarViewJson
  picker: ActionPickerJson
  files: FidelityFilesJson
  health: { band: unknown; panel: unknown }
  width: number
}

const SEPARATOR = '│'

const firstOpen = (panels: unknown[]): unknown => panels.find(panel => panel) ?? null

// The first press on a dot selects it; a press on the selected dot opens the board there.
function pressDot($: EngineInterface, fidelity: FidelityClient): unknown {
  return fidelity.isSelected ? openBoard($, fidelity) : selectFidelity($, fidelity)
}

// A desktop draws every Button natively and ignores the colour of the text inside it, so a coloured mark is Text, and
// the Button that acts on it sits on a card the mark reveals on hover, naming what it acts on.
function HoverCardView({ Box }: ElementTable, button: unknown) {
  return (
    <Box position="absolute" top={-1} left={0} backgroundColor={BRAND.raised} display="none" hover={{ display: 'flex' }}>
      {button}
    </Box>
  )
}

// One dot in its practice colour, shaded by progress and underlined while selected, with the violation count in red
// beside it.
export function FidelityView($: EngineInterface, elements: ElementTable, fidelity: FidelityClient) {
  const { Box, Button, Text } = elements
  return (
    <Box key={`fidelity-${fidelity.fidelity}`} flexDirection="row" gap={0}>
      <Text color={fidelity.shade} weight="bold" underline={fidelity.isSelected}>■</Text>
      {fidelity.violationCount ? <Text size="caption" weight="bold" color={BRAND.error}>{String(fidelity.violationCount)}</Text> : null}
      {HoverCardView(elements, <Button key={`dot-${fidelity.fidelity}`} plain label={`${fidelity.fidelity} ${fidelity.word}`} onPress={() => pressDot($, fidelity)} />)}
    </Box>
  )
}

// One stage icon, faint until reached; the stage in progress, or a stage shown in its place, is underlined.
export function StageView($: EngineInterface, elements: ElementTable, stage: StageClient) {
  const { Box, Button, Text } = elements
  return (
    <Box key={`stage-box-${stage.stage}`} flexDirection="row">
      <Text color={stage.ink} underline={stage.status === 'in_progress' || stage.isShown}>{stage.icon}</Text>
      {HoverCardView(elements, <Button key={`stage-${stage.stage}`} plain label={stage.stage} onPress={() => selectStage($, stage)} />)}
    </Box>
  )
}

function SessionNameView($: EngineInterface, { Box, Button, Text }: ElementTable, { chatBar, health }: ChatBarDraw) {
  return (
    <Box key="session-name" flexDirection="row" gap={1}>
      {health.band}
      <Box flexDirection="row" hover={{ scope: CARD_SCOPE }}>
        <Button key="session-name-button" plain onPress={() => toggleCard($)}>
          <Text weight="semibold" color={chatBar.sessionName ? BRAND.text : BRAND.muted}>{chatBar.sessionName || 'no session'}</Text>
        </Button>
      </Box>
      <Button key="session-list-button" plain label="▾" onPress={() => toggleSessionList($)} />
    </Box>
  )
}

function SessionButtonsView($: EngineInterface, { Box, Button }: ElementTable, { chatBar }: ChatBarDraw) {
  const fidelity = chatBar.actionFidelity
  return (
    <Box key="session-buttons" flexDirection="row" gap={1}>
      <Button key="handoff" label="⇥ handoff" onPress={() => runHandoff($, chatBar)} />
      {fidelity ? <Button key="files-button" label="▤ files" onPress={() => openFiles($, fidelity)} /> : null}
      <Button key="close-button" label="✕ close" onPress={() => openClose($, chatBar)} />
    </Box>
  )
}

// The line, left to right: health mark, session name, fidelity dots, action button, stage icons, then the session's
// buttons. session-card-view.tsx counts these cells to lay the card over them.
function LineView($: EngineInterface, elements: ElementTable, draw: ChatBarDraw) {
  const { Box, Text } = elements
  const { chatBar } = draw
  if (!chatBar.hasSession) return <Box key="line" flexDirection="row" gap={1}>{SessionNameView($, elements, draw)}</Box>
  return (
    <Box key="line" flexDirection="row" gap={1} flexWrap="wrap">
      {SessionNameView($, elements, draw)}
      <Text color={BRAND.border}>{SEPARATOR}</Text>
      {chatBar.fidelities.map(fidelity => FidelityView($, elements, fidelity))}
      {ActionButtonView($, elements, draw)}
      <Text color={BRAND.border}>{SEPARATOR}</Text>
      {chatBar.stages.flatMap((stage, index) => [index ? <Text key={`stage-lead-${stage.stage}`} color={BRAND.border}>›</Text> : null, StageView($, elements, stage)])}
      <Box flexGrow={1} />
      {SessionButtonsView($, elements, draw)}
    </Box>
  )
}

// The chat bar above the prompt: one line holding the server health mark, the session name, the fidelity dots, the
// action button, and the stage icons, with one open panel above it. The space above the prompt cuts from the bottom,
// so a second panel would push the line off screen; the first open panel in this order is the one drawn. A failed
// board read says so above the line.
export function ChatBarView($: EngineInterface, elements: ElementTable, draw: ChatBarDraw) {
  const { Box, Text } = elements
  const { chatBar } = draw
  return (
    <Box key="chat-bar" flexDirection="column" width={draw.width}>
      {chatBar.problem ? <Text color={BRAND.error}>{`The board did not answer: ${chatBar.problem}`}</Text> : null}
      {firstOpen([
        CloseView($, elements, draw),
        ActivateView($, elements, draw),
        FidelityFilesView($, elements, draw.files),
        PickerView($, elements, draw),
        SessionListView($, elements, draw),
        SessionCardView(elements, draw),
      ])}
      {LineView($, elements, draw)}
    </Box>
  )
}
