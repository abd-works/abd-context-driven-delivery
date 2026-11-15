import type { EngineInterface } from 'claude-code'

import type { ActionPickerJson, ChatBarViewJson } from '../../types'
import { BRAND } from '../shared/brand'
import { GlyphButtonView } from '../shared/glyph-button-view'
import { TipView } from '../shared/tip-view'
import { ActionButtonView, pickerRowsOf } from './action-button-view'
import { formatGlyphOf, REPO_GLYPH, repoWordOf, sessionWordOf } from './bar-columns'
import { toggleFormat, type FormatChips } from './format-choices-client'
import { toggleOverlay, toggleOverlayList, type OverlayChips } from './overlay-choices-client'
import { askChatToFixBoard, restartServer, runHandoff, type ChatBarClient } from './chat-bar-client'
import type { FailureClient } from '../error-display/failure-client'
import { FailureView } from '../error-display/failure-view'
import { openFilesOf, openReport, openSessionFolder } from './fidelity-files-client'
import { openHelp } from './fidelity-help-client'
import { selectFidelity, type FidelityProgressClient } from './fidelity-progress-client'
import { CARD_SCOPE, SessionCardView } from './session-card-view'
import { openClose, toggleRepoListWithRepos } from './session-client'
import { toggleSessionList } from './session-dialogs-client'
import { CloseView, RepoListView, repoListRowsOf, SessionListView, sessionListRowsOf } from './session-dialogs-view'
import { selectStage, toggleStagePicker, type StageClient } from './stage-client'

type ElementTable = ReturnType<EngineInterface['ui']['resolve']>

// What one draw of the chat bar reads: the client built from board.show, which boxes are open above the line, the
// server health mark, its panel above the line, the failure shown above it, the same panel for the session card, and the columns the band may fill.
export type ChatBarDraw = {
  chatBar: ChatBarClient
  failure: FailureClient | null
  view: ChatBarViewJson
  picker: ActionPickerJson
  isStagePickerOpen: boolean
  formats: FormatChips
  overlays: OverlayChips
  busy: { doing: string; wheel: string }
  health: { band: unknown; panel: unknown }
  version: { label: string; badge: unknown; dialog: unknown }
  push: { buttons: unknown; dialog: unknown }
  width: number
  // The rows the band may take; a taller bar scrolls, and its window starts at the top, which hides the line.
  maxRows: number
}

const SEPARATOR = '│'

// One square in its practice colour, fainter the less is done, underlined on a light tint when selected, with the
// violation count in red beside it, a press on the count opening the validation report; the fidelity's name shows above
// it on hover, its state being on the session card, and a press on that name opens the fidelity's help in a pane beside the chat.
export function FidelityView($: EngineInterface, elements: ElementTable, fidelity: FidelityProgressClient) {
  const { Box } = elements
  return (
    <Box key={`fidelity-${fidelity.slug}`} flexDirection="row" gap={0} backgroundColor={fidelity.isSelected ? BRAND.selectedTint : undefined}>
      {GlyphButtonView(elements, `dot-${fidelity.slug}`, '■', fidelity.shade, () => selectFidelity($, fidelity), fidelity.isSelected)}
      {fidelity.violationCount ? GlyphButtonView(elements, `violations-${fidelity.slug}`, String(fidelity.violationCount), BRAND.error, () => openReport($, fidelity)) : null}
      {TipView(elements, fidelity.slug, '', BRAND.muted, () => openHelp($, fidelity), `help-${fidelity.slug}`)}
    </Box>
  )
}

// The shown stage as one orange chip, its icon and ▾, like the action button; a press opens the list of stages.
// The list opened from it is drawn beside the chip, in a box of its own, so hovering the list does not show the chip's tip.
function StageButtonView($: EngineInterface, elements: ElementTable, draw: ChatBarDraw) {
  const { Box, Text } = elements
  const { chatBar } = draw
  const shown = chatBar.stages.find(stage => stage.stage === chatBar.shownStage)
  if (!shown) return null
  return (
    <Box key="stage-anchor">
      <Box key="stage-button" flexDirection="row" gap={0} paddingX={1} backgroundColor={BRAND.accent}>
        {GlyphButtonView(elements, 'stage-shown', shown.icon, BRAND.onAccent, () => toggleStagePicker($))}
        {GlyphButtonView(elements, 'stage-picker', '▾', BRAND.onAccent, () => toggleStagePicker($))}
        <Box position="absolute" top={-1} left={0} paddingX={1} backgroundColor={BRAND.raised} display="none" hover={{ display: 'flex' }}>
          <Text color={BRAND.text}>{shown.stage}</Text>
        </Box>
      </Box>
      {StagePickerView($, elements, draw)}
    </Box>
  )
}

// The stages the stage list shows.
const shownStagesOf = (chatBar: ChatBarClient): StageClient[] => chatBar.stages.filter(stage => stage.canShow)

// Every stage as a list above the stage button, its left edge under the button's: its icon and name, the session's
// own marked, the shown one highlighted; a press shows that stage's fidelities.
function StagePickerView($: EngineInterface, { Box, Button, Text }: ElementTable, { chatBar, isStagePickerOpen }: ChatBarDraw) {
  if (!isStagePickerOpen) return null
  return (
    <Box key="stage-list" flexDirection="column" position="absolute" bottom={1} left={0} paddingX={1} borderStyle="round" borderColor={BRAND.border} backgroundColor={BRAND.raised}>
      {shownStagesOf(chatBar).map((stage: StageClient) => {
        const isShown = stage.stage === chatBar.shownStage
        return (
          <Box key={`stage-row-${stage.stage}`} backgroundColor={isShown ? BRAND.accentTint : undefined}>
            <Button key={`stage-pick-${stage.stage}`} plain onPress={() => selectStage($, stage)}>
              <Text color={stage.ink}>{`${stage.icon} `}</Text>
              <Text color={BRAND.text} weight={stage.isCurrent ? 'bold' : undefined}>{stage.stage}</Text>
            </Button>
          </Box>
        )
      })}
    </Box>
  )
}

// A word and its glyph as one whole button, the word in the text colour and the glyph muted. A see-through Button laid
// over text takes no press in the desktop app, so the words are the Button's own children.
function WordGlyphButtonView({ Button, Text }: ElementTable, key: string, word: string, glyph: string, onPress: () => unknown) {
  return (
    <Button key={key} plain onPress={onPress}>
      <Text weight="semibold" color={BRAND.text}>{word}</Text>
      <Text color={BRAND.muted}>{` ${glyph}`}</Text>
    </Button>
  )
}

// In the main chat, the repository's name with its ⑂ comes first, one button that opens the list of repositories, then
// "main +", one button that opens the list of tickets to open, its card showing on hover. A ticket's own chat works only on that
// ticket, so it shows the name alone: a press opens the session's folder in the files pane, its card showing on hover.
// A chat in a plain folder, in any session, has neither other repositories nor tickets nor a branch to close, so it
// shows the folder's path alone, read only, and no close button.
function SessionNameView($: EngineInterface, elements: ElementTable, draw: ChatBarDraw) {
  const { chatBar } = draw
  const { Box, Button, Text } = elements
  if (chatBar.isPlainFolder) {
    return (
      <Box key="session-name" flexDirection="row" gap={1}>
        <Box flexDirection="row" hover={{ scope: CARD_SCOPE }}>
          <Text weight="semibold" color={BRAND.text} wrap="truncate-start">{chatBar.folder}</Text>
        </Box>
      </Box>
    )
  }
  if (chatBar.isMain) {
    return (
      <Box key="session-name" flexDirection="row" gap={0}>
        <Box key="repo-anchor">
          {WordGlyphButtonView(elements, 'repo-list-button', repoWordOf(chatBar), REPO_GLYPH, () => toggleRepoListWithRepos($))}
          {RepoListView($, elements, draw)}
        </Box>
        <Box key="session-anchor" marginLeft={-1}>
          <Box flexDirection="row" hover={{ scope: CARD_SCOPE }}>
            {WordGlyphButtonView(elements, 'session-list-button', sessionWordOf(chatBar), '+', () => toggleSessionList($))}
          </Box>
          {SessionListView($, elements, draw)}
        </Box>
      </Box>
    )
  }
  return (
    <Box key="session-name" flexDirection="row" gap={1}>
      <Box flexDirection="row" hover={{ scope: CARD_SCOPE }}>
        <Button key="session-name-button" plain onPress={() => openSessionFolder($)}>
          <Text weight="semibold" color={BRAND.text}>{chatBar.sessionName}</Text>
        </Button>
      </Box>
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

// Files right after the action button: the action fidelity's files, else the first fidelity's.
function FilesButtonView($: EngineInterface, elements: ElementTable, { chatBar }: ChatBarDraw) {
  const fidelities = chatBar.actionFidelities.length ? chatBar.actionFidelities : chatBar.fidelities.slice(0, 1)
  return fidelities.length ? IconButtonView(elements, 'files-button', '▤', 'files', () => openFilesOf($, fidelities)) : null
}

// Push, push & merge to origin/main, restart and close as icons.
function SessionButtonsView($: EngineInterface, elements: ElementTable, { chatBar, push }: ChatBarDraw) {
  const { Box } = elements
  return (
    <Box key="session-buttons" flexDirection="row" gap={1}>
      {chatBar.isClone ? push.buttons : null}
      {IconButtonView(elements, 'restart-button', '↻', 'restart cdd server', () => restartServer($))}
      {chatBar.isMain || chatBar.isPlainFolder ? null : IconButtonView(elements, 'close-button', '✕', 'close session', () => openClose($, chatBar))}
    </Box>
  )
}

// One chip per format group the fidelities offer, just before the action button, as on a board ticket's action bar:
// orange while chosen in the session, green when every fidelity has a file in it already, grey otherwise; a press turns
// it on or off in the session.
function FormatChipsView($: EngineInterface, elements: ElementTable, { chatBar, formats }: ChatBarDraw) {
  const { Box } = elements
  if (!formats.choices.length) return null
  return (
    <Box key="format-chips" flexDirection="row" gap={0} marginX={1}>
      {formats.choices.map(choice => {
        const isOn = choice.is_chosen
        const colour = isOn ? BRAND.onAccent : choice.made && choice.made === choice.offered ? BRAND.success : BRAND.muted
        return (
          <Box key={`format-${choice.label}`} paddingX={1} backgroundColor={isOn ? BRAND.accent : undefined}>
            {GlyphButtonView(elements, `format-chip-${choice.label}`, formatGlyphOf(choice.label), colour, () => toggleFormat($, chatBar, formats, choice.label))}
            {TipView(elements, choice.label, `${choice.made}/${choice.offered} made`, BRAND.muted)}
          </Box>
        )
      })}
    </Box>
  )
}

// The + right after the fidelity dots, then one icon per pattern the session overlays on its graph, its first and last
// letter, the pattern's name above it on hover; the format chips and the action button follow them.
function OverlayChipsView($: EngineInterface, elements: ElementTable, draw: ChatBarDraw) {
  const { Box } = elements
  const { overlays } = draw
  if (!overlays.choices.length) return null
  return (
    <Box key="overlay-chips" flexDirection="row" gap={1} alignItems="center">
      <Box key="overlay-anchor">
        {GlyphButtonView(elements, 'overlay-list', '+', overlays.isOpen ? BRAND.accent : BRAND.muted, () => toggleOverlayList($))}
        {OverlayListView($, elements, draw)}
      </Box>
      {overlays.chosen.map(choice => (
        <Box key={`overlay-${choice.pattern}`}>
          <elements.Text color={BRAND.text}>{choice.icon}</elements.Text>
          {TipView(elements, choice.pattern, '', BRAND.muted)}
        </Box>
      ))}
    </Box>
  )
}

// Every pattern as a list box above the +, the session's overlays marked; a press on one adds it or takes it out, and
// the list stays open so a person can pick several.
function OverlayListView($: EngineInterface, { Box, Button, Text }: ElementTable, { overlays }: ChatBarDraw) {
  if (!overlays.isOpen) return null
  return (
    <Box key="overlay-list-box" flexDirection="column" position="absolute" bottom={1} left={0} paddingX={1} borderStyle="round" borderColor={BRAND.border} backgroundColor={BRAND.raised}>
      {overlays.choices.map(choice => (
        <Box key={`overlay-row-${choice.pattern}`} flexDirection="row" gap={1} alignItems="center" backgroundColor={choice.is_chosen ? BRAND.accentTint : undefined}>
          <Text color={choice.is_chosen ? BRAND.accent : BRAND.muted}>{choice.is_chosen ? '✓' : ' '}</Text>
          <Text color={BRAND.faint}>{choice.icon}</Text>
          <Button key={`overlay-pick-${choice.pattern}`} plain label={choice.pattern} onPress={() => toggleOverlay($, overlays, choice.pattern)} />
        </Box>
      ))}
    </Box>
  )
}

// The line, left to right: the stage button, │, fidelity dots and the action chip, then at the right end the session
// name, its buttons, the health mark, and the version badge.
function LineView($: EngineInterface, elements: ElementTable, draw: ChatBarDraw) {
  const { Box, Text } = elements
  const { chatBar } = draw
  if (!chatBar.hasSession) return <Box key="line" flexDirection="row" gap={1}><Box flexGrow={1} />{SessionNameView($, elements, draw)}{draw.health.band}{draw.version.badge}</Box>
  return (
    <Box key="line" flexDirection="row" gap={1} alignItems="center">
        {StageButtonView($, elements, draw)}
        <Text color={BRAND.border}>{SEPARATOR}</Text>
        <Box key="fidelity-column" flexDirection="row" gap={1} alignItems="center">
          {chatBar.fidelities.map(fidelity => FidelityView($, elements, fidelity))}
          {OverlayChipsView($, elements, draw)}
          {FormatChipsView($, elements, draw)}
          {ActionButtonView($, elements, draw)}
          {FilesButtonView($, elements, draw)}
          {IconButtonView(elements, 'handoff', '⇥', 'handoff', () => runHandoff($, chatBar))}
        </Box>
        <Box flexGrow={1} />
        {SessionNameView($, elements, draw)}
        {SessionButtonsView($, elements, draw)}
        {draw.health.band}
        {draw.version.badge}
    </Box>
  )
}

// The board did not answer, in red above the line, with Fix to send it to the chat; the next read that works clears it.
function ProblemView($: EngineInterface, { Box, Button, Text }: ElementTable, shown: string) {
  return (
    <Box key="problem" flexDirection="row" gap={1} alignItems="center">
      <Text color={BRAND.error}>{shown}</Text>
      <Button key="fix-problem" label="Fix" variant="primary" onPress={() => askChatToFixBoard($, shown)} />
    </Box>
  )
}

// The chat bar above the prompt: the boxes a person opened sit above one line holding the server health mark, the
// session name, the fidelity dots, the action button, and the stage icons. A failed board read says so above the line.
// A list box's round border, a row above and below its lines.
const LIST_BORDER_ROWS = 2

// The line itself, which the room above it must leave in view.
const LINE_ROWS = 1

// Empty rows above the line, as many as the open list box is tall. Each list is drawn against its button, out of the
// bar's flow, and the bar cuts off whatever is drawn outside it, so these rows give the list its room. They stop short
// of the band's limit so the line stays in view; a list taller than that loses its top rows instead.
function ListRoomView({ Box }: ElementTable, draw: ChatBarDraw) {
  const { chatBar, overlays } = draw
  const rows = Math.max(
    draw.isStagePickerOpen ? shownStagesOf(chatBar).length + LIST_BORDER_ROWS : 0,
    overlays.isOpen ? overlays.choices.length + LIST_BORDER_ROWS : 0,
    pickerRowsOf(draw),
    sessionListRowsOf(draw),
    repoListRowsOf(draw),
  )
  const room = Math.min(rows, Math.max(0, draw.maxRows - LINE_ROWS))
  return room ? <Box key="list-room" height={room} /> : null
}

export function ChatBarView($: EngineInterface, elements: ElementTable, draw: ChatBarDraw) {
  const { Box, Text } = elements
  const { chatBar } = draw
  return (
    <Box key="chat-bar" flexDirection="column" width={draw.width}>
      {chatBar.problem ? ProblemView($, elements, `The board did not answer: ${chatBar.problem}`) : null}
      {FailureView($, elements, draw.failure)}
      {draw.busy.doing ? <Text key="busy" color={BRAND.accent}>{`${draw.busy.wheel} ${draw.busy.doing}…`}</Text> : null}
      {draw.version.dialog}
      {draw.push.dialog}
      {CloseView($, elements, draw)}
      {SessionCardView($, elements, draw)}
      {ListRoomView(elements, draw)}
      {LineView($, elements, draw)}
    </Box>
  )
}
