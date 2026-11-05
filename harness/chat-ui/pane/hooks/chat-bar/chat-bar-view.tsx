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

// The first press on a dot selects it; a press on the selected dot opens the board there.
function pressDot($: EngineInterface, fidelity: FidelityClient): unknown {
  return fidelity.isSelected ? openBoard($, fidelity) : selectFidelity($, fidelity)
}

// One dot in its practice colour, shaded by progress, with the violation count in red beside it.
export function FidelityView($: EngineInterface, { Box, Button, Text }: ElementTable, fidelity: FidelityClient) {
  return (
    <Box key={`fidelity-${fidelity.fidelity}`} flexDirection="row" gap={0}>
      <Button key={`dot-${fidelity.fidelity}`} plain label={`${fidelity.fidelity} ${fidelity.word}`} onPress={() => pressDot($, fidelity)}>
        <Text color={fidelity.shade} weight={fidelity.isSelected ? 'semibold' : undefined}>{fidelity.isSelected ? '◉' : '●'}</Text>
      </Button>
      {fidelity.violationCount ? <Text color={BRAND.error}>{String(fidelity.violationCount)}</Text> : null}
    </Box>
  )
}

// One stage icon, faint until reached; the stage in progress is outlined, and a shown stage reads in full ink.
export function StageView($: EngineInterface, { Box, Button, Text }: ElementTable, stage: StageClient) {
  const outline = stage.status === 'in_progress' || stage.isShown ? { borderStyle: 'single' as const, borderColor: stage.ink } : {}
  return (
    <Box key={`stage-box-${stage.stage}`} {...outline}>
      <Button key={`stage-${stage.stage}`} plain label={stage.stage} onPress={() => selectStage($, stage)}>
        <Text color={stage.ink}>{stage.icon}</Text>
      </Button>
    </Box>
  )
}

function SessionNameView($: EngineInterface, { Box, Button, Text }: ElementTable, { chatBar, health }: ChatBarDraw) {
  return (
    <Box key="session-name" flexDirection="row" gap={1}>
      {health.band}
      <Box flexDirection="row" hover={{ scope: CARD_SCOPE }}>
        <Button key="session-name-button" plain label={chatBar.sessionName || 'no session'} onPress={() => toggleCard($)}>
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
      <Button key="handoff" plain label="⇥ handoff" onPress={() => runHandoff($, chatBar)} />
      {fidelity ? <Button key="files-button" plain label="▤ files" onPress={() => openFiles($, fidelity)} /> : null}
      <Button key="close-button" plain label="✕ close" onPress={() => openClose($, chatBar)} />
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
      {chatBar.stages.map(stage => StageView($, elements, stage))}
      <Box flexGrow={1} />
      {SessionButtonsView($, elements, draw)}
    </Box>
  )
}

// The chat bar above the prompt: the boxes a person opened sit above one line holding the server health mark, the
// session name, the fidelity dots, the action button, and the stage icons. A failed board read says so above the line.
export function ChatBarView($: EngineInterface, elements: ElementTable, draw: ChatBarDraw) {
  const { Box, Text } = elements
  const { chatBar } = draw
  return (
    <Box key="chat-bar" flexDirection="column" width={draw.width}>
      {chatBar.problem ? <Text color={BRAND.error}>{`The board did not answer: ${chatBar.problem}`}</Text> : null}
      {FidelityFilesView($, elements, draw.files)}
      {CloseView($, elements, draw)}
      {ActivateView($, elements, draw)}
      {SessionListView($, elements, draw)}
      {SessionCardView(elements, draw)}
      {PickerView($, elements, draw)}
      {LineView($, elements, draw)}
    </Box>
  )
}
