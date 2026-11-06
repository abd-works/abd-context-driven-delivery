import type { EngineInterface } from 'claude-code'

import type { ActionPickerJson, ChatBarViewJson, FidelityFilesJson } from '../../types'
import { BRAND } from '../brand'
import { GlyphButtonView } from '../glyph-button-view'
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
// server health mark, its panel above the line, the same panel for the session card, and the columns the band may fill.
export type ChatBarDraw = {
  chatBar: ChatBarClient
  view: ChatBarViewJson
  picker: ActionPickerJson
  files: FidelityFilesJson
  health: { band: unknown; markPanel: unknown; panel: unknown }
  width: number
}

const SEPARATOR = '│'

// The first press on a dot selects it; a press on the selected dot opens the board there.
function pressDot($: EngineInterface, fidelity: FidelityClient): unknown {
  return fidelity.isSelected ? openBoard($, fidelity) : selectFidelity($, fidelity)
}

// A label shown above an element while the pointer is on its keyed Box, as the canvas's hover tips.
function TipView({ Box, Text }: ElementTable, words: string, detail: string, detailColour: string) {
  return (
    <Box position="absolute" top={-1} left={0} paddingX={1} backgroundColor={BRAND.raised} display="none" hover={{ display: 'flex' }}>
      <Text color={BRAND.text}>{`${words} `}</Text>
      <Text color={detailColour}>{detail}</Text>
    </Box>
  )
}

// One square in its practice colour, fainter the less is done, underlined when selected, with the violation count in
// red beside it; the fidelity and its state show above it on hover.
export function FidelityView($: EngineInterface, elements: ElementTable, fidelity: FidelityClient) {
  const { Box, Text } = elements
  return (
    <Box key={`fidelity-${fidelity.fidelity}`} flexDirection="row" gap={0}>
      {GlyphButtonView(elements, `dot-${fidelity.fidelity}`, '▪', fidelity.shade, () => pressDot($, fidelity), fidelity.isSelected)}
      {fidelity.violationCount ? <Text size="caption" weight="bold" color={BRAND.error}>{String(fidelity.violationCount)}</Text> : null}
      {TipView(elements, fidelity.fidelity, `${fidelity.mark} ${fidelity.word}`, fidelity.lookColour)}
    </Box>
  )
}

// One stage icon, faint until reached, after a grey › from the stage before it. Only the stage in progress is underlined,
// which costs no extra row as an outline would; a stage shown instead of it is tinted. Its name and what it is for show above it on hover.
export function StageView($: EngineInterface, elements: ElementTable, stage: StageClient, index: number) {
  const { Box, Text } = elements
  return (
    <Box key={`stage-step-${stage.stage}`} flexDirection="row" gap={0}>
      {index ? <Text color={BRAND.border}>{' › '}</Text> : null}
      <Box key={`stage-box-${stage.stage}`} paddingX={1} backgroundColor={stage.tint}>
        {GlyphButtonView(elements, `stage-${stage.stage}`, stage.icon, stage.ink, () => selectStage($, stage), stage.isInProgress)}
        {TipView(elements, stage.stage, stage.scope, BRAND.muted)}
      </Box>
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
      {GlyphButtonView({ Box, Button, Text }, 'session-list-button', '▾', BRAND.muted, () => toggleSessionList($))}
    </Box>
  )
}

// One icon a person presses, with no chip around it, whose words show above it on hover.
function IconButtonView(elements: ElementTable, key: string, icon: string, words: string, onPress: () => unknown) {
  const { Box } = elements
  return (
    <Box key={`${key}-box`}>
      {GlyphButtonView(elements, key, icon, BRAND.muted, onPress)}
      {TipView(elements, words, '', BRAND.muted)}
    </Box>
  )
}

// Handoff, files and close as icons. Files shows the action fidelity's files, else the first fidelity's.
function SessionButtonsView($: EngineInterface, elements: ElementTable, { chatBar }: ChatBarDraw) {
  const { Box } = elements
  const fidelity = chatBar.actionFidelity ?? chatBar.fidelities[0]
  return (
    <Box key="session-buttons" flexDirection="row" gap={1}>
      {IconButtonView(elements, 'handoff', '⇥', 'handoff', () => runHandoff($, chatBar))}
      {fidelity ? IconButtonView(elements, 'files-button', '▤', 'files', () => openFiles($, fidelity)) : null}
      {IconButtonView(elements, 'close-button', '✕', 'close session', () => openClose($, chatBar))}
    </Box>
  )
}

// The line, left to right: health mark, session name, │, fidelity dots and the action chip, the stage path, then the
// session's buttons, on one row. session-card-view.tsx counts these cells to lay the card over them.
function LineView($: EngineInterface, elements: ElementTable, draw: ChatBarDraw) {
  const { Box, Text } = elements
  const { chatBar } = draw
  if (!chatBar.hasSession) return <Box key="line" flexDirection="row" gap={1}>{SessionNameView($, elements, draw)}</Box>
  return (
    <Box key="line" flexDirection="row" gap={1} flexWrap="wrap" alignItems="center">
        {SessionNameView($, elements, draw)}
        <Text color={BRAND.border}>{SEPARATOR}</Text>
        {chatBar.fidelities.map(fidelity => FidelityView($, elements, fidelity))}
        {ActionButtonView($, elements, draw)}
        <Box flexDirection="row" gap={0} marginLeft={1}>
          {chatBar.stages.map((stage, index) => StageView($, elements, stage, index))}
        </Box>
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
      {SessionCardView($, elements, draw)}
      {PickerView($, elements, draw)}
      {draw.health.markPanel}
      {LineView($, elements, draw)}
    </Box>
  )
}
