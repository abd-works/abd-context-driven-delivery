import type { EngineInterface } from 'claude-code'

import type { ActionPickerJson, ChatBarViewJson } from '../../types'
import { BRAND } from '../shared/brand'
import { GlyphButtonView } from '../shared/glyph-button-view'
import { ActionButtonView, PickerView } from './action-button-view'
import { askChatToFix, dismissFailure, fixFailure, runHandoff, type ChatBarClient } from './chat-bar-client'
import { openFiles, openReport } from './fidelity-files-client'
import { selectFidelity, type FidelityProgressClient } from './fidelity-progress-client'
import { CARD_SCOPE, SessionCardView } from './session-card-view'
import { openClose } from './session-client'
import { toggleCard, toggleSessionList } from './session-dialogs-client'
import { ActivateView, CloseView, SessionListView } from './session-dialogs-view'
import { selectStage, toggleStagePicker, type StageClient } from './stage-client'

type ElementTable = ReturnType<EngineInterface['ui']['resolve']>

// What one draw of the chat bar reads: the client built from board.show, which boxes are open above the line, the
// server health mark, its panel above the line, the same panel for the session card, and the columns the band may fill.
export type ChatBarDraw = {
  chatBar: ChatBarClient
  view: ChatBarViewJson
  picker: ActionPickerJson
  isStagePickerOpen: boolean
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

// The shown stage as one orange chip, its icon and ▾, like the action button; a press opens the list of stages.
function StageButtonView($: EngineInterface, elements: ElementTable, { chatBar }: ChatBarDraw) {
  const { Box, Text } = elements
  const shown = chatBar.stages.find(stage => stage.stage === chatBar.shownStage)
  if (!shown) return null
  return (
    <Box key="stage-button" flexDirection="row" gap={0} paddingX={1} backgroundColor={BRAND.accent}>
      {GlyphButtonView(elements, 'stage-shown', shown.icon, BRAND.onAccent, () => toggleStagePicker($))}
      {GlyphButtonView(elements, 'stage-picker', '▾', BRAND.onAccent, () => toggleStagePicker($))}
      <Box position="absolute" top={-1} left={0} paddingX={1} backgroundColor={BRAND.raised} display="none" hover={{ display: 'flex' }}>
        <Text color={BRAND.text}>{shown.stage}</Text>
      </Box>
    </Box>
  )
}

// Every stage as a list above the stage button: its icon and name, the session's own marked, the shown one highlighted;
// a press shows that stage's fidelities.
export function StagePickerView($: EngineInterface, { Box, Button, Text }: ElementTable, { chatBar, isStagePickerOpen }: ChatBarDraw) {
  if (!isStagePickerOpen) return null
  return (
    <Box key="stage-list" flexDirection="column" alignSelf="flex-start" marginLeft={2} paddingX={1} borderStyle="round" borderColor={BRAND.border} backgroundColor={BRAND.raised}>
      {chatBar.stages.filter(stage => stage.canShow).map((stage: StageClient) => {
        const isShown = stage.stage === chatBar.shownStage
        return (
          <Box key={`stage-row-${stage.stage}`} flexDirection="row" gap={1} alignItems="center" backgroundColor={isShown ? BRAND.accentTint : undefined}>
            <Text color={stage.ink}>{stage.icon}</Text>
            <Button key={`stage-pick-${stage.stage}`} plain label={stage.isCurrent ? `${stage.stage} ·` : stage.stage} onPress={() => selectStage($, stage)} />
          </Box>
        )
      })}
    </Box>
  )
}

function SessionNameView($: EngineInterface, { Box, Button, Text }: ElementTable, { chatBar }: ChatBarDraw) {
  return (
    <Box key="session-name" flexDirection="row" gap={1}>
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

// The line, left to right: health mark, the stage button, │, fidelity dots and the action chip, then at the right end
// the session name and its buttons.
function LineView($: EngineInterface, elements: ElementTable, draw: ChatBarDraw) {
  const { Box, Text } = elements
  const { chatBar } = draw
  if (!chatBar.hasSession) return <Box key="line" flexDirection="row" gap={1}>{draw.health.band}<Box flexGrow={1} />{SessionNameView($, elements, draw)}</Box>
  return (
    <Box key="line" flexDirection="row" gap={1} flexWrap="wrap" alignItems="center">
        {draw.health.band}
        {StageButtonView($, elements, draw)}
        <Text color={BRAND.border}>{SEPARATOR}</Text>
        <Box key="fidelity-column" flexDirection="row" gap={1} alignItems="center">
          {chatBar.fidelities.map(fidelity => FidelityView($, elements, fidelity))}
          {ActionButtonView($, elements, draw)}
        </Box>
        <Box flexGrow={1} />
        {SessionNameView($, elements, draw)}
        {SessionButtonsView($, elements, draw)}
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
      {CloseView($, elements, draw)}
      {ActivateView($, elements, draw)}
      {SessionListView($, elements, draw)}
      {SessionCardView($, elements, draw)}
      {StagePickerView($, elements, draw)}
      {PickerView($, elements, draw)}
      {LineView($, elements, draw)}
    </Box>
  )
}
