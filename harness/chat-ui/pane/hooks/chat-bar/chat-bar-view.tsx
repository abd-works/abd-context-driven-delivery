import type { EngineInterface } from 'claude-code'

import type { ActionPickerJson, ChatBarViewJson, ChatFolderJson } from '../../types'
import { BRAND } from '../shared/brand'
import { GlyphButtonView } from '../shared/glyph-button-view'
import { ActionButtonView, PickerView } from './action-button-view'
import { askChatToFix, dismissFailure, fixFailure, runHandoff, type ChatBarClient } from './chat-bar-client'
import { followSession } from './chat-folder-client'
import { openFiles, openReport } from './fidelity-files-client'
import { selectFidelity, type FidelityProgressClient } from './fidelity-progress-client'
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
  folder: ChatFolderJson & { isElsewhere: boolean }
  busy: { doing: string; wheel: string }
  health: { band: unknown; panel: unknown }
  width: number
}

const SEPARATOR = '│'

// A label shown above an element while the pointer is on its keyed Box, as the canvas's hover tips.
function TipView({ Box, Text }: ElementTable, words: string, detail: string, detailColour: string) {
  return (
    <Box position="absolute" top={-1} left={0} paddingX={1} backgroundColor={BRAND.raised} display="none" hover={{ display: 'flex' }}>
      <Text color={BRAND.text}>{detail ? `${words} ` : words}</Text>
      {detail ? <Text color={detailColour}>{detail}</Text> : null}
    </Box>
  )
}

// One square in its practice colour, fainter the less is done, underlined on a light tint when selected, with the
// violation count in red beside it, a press on the count opening the validation report; the fidelity's name shows above
// it on hover, its state being on the session card.
export function FidelityView($: EngineInterface, elements: ElementTable, fidelity: FidelityProgressClient) {
  const { Box } = elements
  return (
    <Box key={`fidelity-${fidelity.slug}`} flexDirection="row" gap={0} backgroundColor={fidelity.isSelected ? BRAND.selectedTint : undefined}>
      {GlyphButtonView(elements, `dot-${fidelity.slug}`, '■', fidelity.shade, () => selectFidelity($, fidelity), fidelity.isSelected)}
      {fidelity.violationCount ? GlyphButtonView(elements, `violations-${fidelity.slug}`, String(fidelity.violationCount), BRAND.error, () => openReport($, fidelity)) : null}
      {TipView(elements, fidelity.slug, '', BRAND.muted)}
    </Box>
  )
}

// One stage icon, faint until reached, after a grey › from the stage before it. Only the session's own stage is
// underlined, which costs no extra row as an outline would; a stage shown instead of it is tinted. Its name and what it
// is for show above it on hover.
export function StageView($: EngineInterface, elements: ElementTable, stage: StageClient, index: number) {
  const { Box, Text } = elements
  return (
    <Box key={`stage-step-${stage.stage}`} flexDirection="row" gap={0}>
      {index ? <Text color={BRAND.border}>{' › '}</Text> : null}
      <Box key={`stage-box-${stage.stage}`} paddingX={1} backgroundColor={stage.tint}>
        {GlyphButtonView(elements, `stage-${stage.stage}`, stage.icon, stage.ink, () => selectStage($, stage), stage.isCurrent)}
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
          <Text weight="semibold" color={BRAND.text}>{chatBar.sessionName || 'main'}</Text>
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
      {chatBar.isMain ? null : IconButtonView(elements, 'close-button', '✕', 'close session', () => openClose($, chatBar))}
    </Box>
  )
}

// The line, left to right: health mark, session name, │, fidelity dots and the action chip, the stage path, then the
// session's buttons, packed to the left on one row.
function LineView($: EngineInterface, elements: ElementTable, draw: ChatBarDraw) {
  const { Box, Text } = elements
  const { chatBar } = draw
  if (!chatBar.hasSession) return <Box key="line" flexDirection="row" gap={1}>{SessionNameView($, elements, draw)}</Box>
  return (
    <Box key="line" flexDirection="row" gap={1} flexWrap="wrap" alignItems="center">
        {SessionNameView($, elements, draw)}
        <Text color={BRAND.border}>{SEPARATOR}</Text>
        <Box key="fidelity-column" flexDirection="row" gap={1} alignItems="center">
          {chatBar.fidelities.map(fidelity => FidelityView($, elements, fidelity))}
          {ActionButtonView($, elements, draw)}
        </Box>
        <Box flexDirection="row" gap={0} marginLeft={1}>
          {chatBar.stages.map((stage, index) => StageView($, elements, stage, index))}
        </Box>
        <Box flexGrow={1} />
        {SessionButtonsView($, elements, draw)}
    </Box>
  )
}

// This chat works in another folder than the active session's work, as after a switch made on the board or in another
// chat: the band says so and moves it on a press.
function ElsewhereView($: EngineInterface, { Box, Button, Text }: ElementTable, { chatBar, folder }: ChatBarDraw) {
  if (!folder.isElsewhere) return null
  return (
    <Box key="elsewhere" flexDirection="row" gap={1} alignItems="center">
      <Text color={BRAND.error}>{`This chat works in ${folder.current}; ${chatBar.sessionName || 'the open session'} works in ${folder.expected}.`}</Text>
      <Button key="follow-session" label="Move this chat there" onPress={() => followSession($, chatBar)} />
    </Box>
  )
}

// The board did not answer, in red above the line, with Fix to send it to the chat; the next read that works clears it.
function ProblemView($: EngineInterface, { Box, Button, Text }: ElementTable, shown: string) {
  return (
    <Box key="problem" flexDirection="row" gap={1} alignItems="center">
      <Text color={BRAND.error}>{shown}</Text>
      <Button key="fix-problem" label="Fix" variant="primary" onPress={() => askChatToFix($, shown)} />
    </Box>
  )
}

// An action that failed, in red above the line, until the person sends it to the chat with Fix or dismisses it with ✕.
function FailureView($: EngineInterface, elements: ElementTable, { chatBar }: ChatBarDraw) {
  const { Box, Button, Text } = elements
  if (!chatBar.failure) return null
  return (
    <Box key="failure" flexDirection="row" gap={1} alignItems="center">
      <Text color={BRAND.error}>{chatBar.failure}</Text>
      <Button key="fix-failure" label="Fix" variant="primary" onPress={() => fixFailure($, chatBar)} />
      {GlyphButtonView(elements, 'dismiss-failure', '✕', BRAND.muted, () => dismissFailure($))}
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
      {chatBar.problem ? ProblemView($, elements, `The board did not answer: ${chatBar.problem}`) : null}
      {FailureView($, elements, draw)}
      {draw.busy.doing ? <Text key="busy" color={BRAND.accent}>{`${draw.busy.wheel} ${draw.busy.doing}…`}</Text> : null}
      {ElsewhereView($, elements, draw)}
      {CloseView($, elements, draw)}
      {ActivateView($, elements, draw)}
      {SessionListView($, elements, draw)}
      {SessionCardView($, elements, draw)}
      {PickerView($, elements, draw)}
      {LineView($, elements, draw)}
    </Box>
  )
}
