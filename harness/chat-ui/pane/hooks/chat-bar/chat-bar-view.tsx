import type { EngineInterface } from 'claude-code'

import type { ServerHealthIconsView } from '../health/server-health-view'
import type { ActionPickerJson, ChatBarViewJson } from '../../types'
import { BRAND } from '../shared/brand'
import { GlyphButtonView } from '../shared/glyph-button-view'
import { TipView } from '../shared/tip-view'
import { ActionButtonView, pickerRowsOf } from './action-button-view'
import { formatGlyphOf, REPO_GLYPH, repoWordOf, SESSION_GLYPH, sessionWordOf } from './bar-columns'
import type { FormatChips } from './format-choices-client'
import { toggleFormat, togglePractice, toggleStage } from './guidance-client'
import { toggleOverlay, toggleOverlayList, type OverlayChips } from './overlay-choices-client'
import { askChatToFixBoard, restartServer, runDebug, runHandoff, type ChatBarClient } from './chat-bar-client'
import type { FailureClient } from '../error-display/failure-client'
import { FailureView } from '../error-display/failure-view'
import { openReport, openSessionFolder, openStageFiles } from './fidelity-files-client'
import { openHelp } from './fidelity-help-client'
import type { PracticeDotClient } from './fidelity-progress-client'
import { CARD_SCOPE, SessionCardView } from './session-card-view'
import { makeRepository, openClose, toggleRepoListWithRepos } from './session-client'
import { toggleSessionList } from './session-dialogs-client'
import { CloseView, RepoListView, repoListRowsOf, SessionListView, sessionListRowsOf } from './session-dialogs-view'
import type { StageClient } from './stage-client'

type ElementTable = ReturnType<EngineInterface['ui']['resolve']>

// What one draw of the chat bar reads: the client built from board.show, which boxes are open above the line, the
// server health mark, its panel above the line, the failure shown above it, the same panel for the session card, and the columns the band may fill.
type HealthIcons = ReturnType<typeof ServerHealthIconsView>

export type ChatBarDraw = {
  chatBar: ChatBarClient
  failure: FailureClient | null
  view: ChatBarViewJson
  picker: ActionPickerJson
  formats: FormatChips
  overlays: OverlayChips
  busy: { doing: string; wheel: string }
  // walkQuestion is the dialog a timed e2e run's desktop walk question shows, null when none is open.
  health: { band: unknown; panel: unknown; icons: HealthIcons; walkQuestion: unknown }
  version: { label: string; badge: unknown; dialog: unknown }
  push: { buttons: unknown; dialog: unknown }
  width: number
  // The rows the band may take; a taller bar scrolls, and its window starts at the top, which hides the line.
  maxRows: number
}

const SEPARATOR = '│'

// One square for each practice in its colour, standing for its fidelities in every stage shown: while the practice is on,
// underlined on a light tint, so it reads on at a glance, fainter the less is done, their violations counted in red
// beside it, a press on the count opening the first one's report; while it is off, faint, with no tint or underline. A press on the square turns the practice on or off for the session. Its fidelities show
// above it on hover, each opening its help in a pane beside the chat; their states are on the session card.
export function PracticeDotView($: EngineInterface, elements: ElementTable, dot: PracticeDotClient) {
  const { Box } = elements
  const violating = dot.violating
  return (
    <Box key={`practice-${dot.practice}`} flexDirection="row" gap={0} backgroundColor={dot.isOn ? BRAND.selectedTint : undefined}>
      {GlyphButtonView(elements, `dot-${dot.practice}`, '■', dot.shade, () => togglePractice($, dot.sessionFile, dot.practice), dot.isOn)}
      {violating ? GlyphButtonView(elements, `violations-${dot.practice}`, String(dot.violationCount), BRAND.error, () => openReport($, violating)) : null}
      {PracticeTipView($, elements, dot)}
    </Box>
  )
}

// The practice's fidelities above its dot on hover, each a button that opens its help.
function PracticeTipView($: EngineInterface, { Box, Button, Text }: ElementTable, dot: PracticeDotClient) {
  return (
    <Box position="absolute" bottom={1} left={0} paddingX={1} gap={1} flexDirection="row" backgroundColor={BRAND.raised} display="none" hover={{ display: 'flex' }}>
      {dot.fidelities.map(fidelity => (
        <Button key={`help-${fidelity.slug}`} plain onPress={() => openHelp($, fidelity)}>
          <Text color={BRAND.text}>{fidelity.slug}</Text>
        </Button>
      ))}
    </Box>
  )
}

// Every stage button is this many columns wide, its icon centred: the desktop draws a stage icon wider than the one column
// a glyph is measured at, so a box sized to its icon came out a different width for each.
const STAGE_BUTTON_COLUMNS = 4

// A button for each stage, its icon filled orange while the stage is shown, its name above it on hover. A press shows
// that stage's fidelities beside those already shown, or no longer, here and in a page the chat opened, such as the Files
// app, so one action can run across several stages.
function StageButtonsView($: EngineInterface, elements: ElementTable, { chatBar }: ChatBarDraw) {
  const { Box } = elements
  const stages = chatBar.stages.filter(stage => stage.canShow)
  if (!stages.length) return null
  return (
    <Box key="stage-buttons" flexDirection="row" gap={1} flexShrink={0}>
      {stages.map((stage: StageClient) => (
        <Box key={`stage-${stage.stage}`} width={STAGE_BUTTON_COLUMNS} justifyContent="center" backgroundColor={stage.isShown ? BRAND.accent : undefined}>
          {GlyphButtonView(elements, `stage-button-${stage.stage}`, stage.icon, stage.isShown ? BRAND.onAccent : stage.ink, () => toggleStage($, chatBar.sessionFile, stage.stage.toLowerCase()))}
          {TipView(elements, stage.stage, stage.isCurrent ? 'the session is here' : '', BRAND.muted)}
        </Box>
      ))}
    </Box>
  )
}

// In the main chat, ⑂ comes first, a button that opens the list of repositories, then +, a button that opens the list of
// tickets to open; each shows its name above it on hover, and + shows the session card too. The line under the chat
// names the repository and branch, so the icons alone keep the line short. A ticket's own chat works only on that
// ticket, so it shows the name alone: a press opens the session's folder in the files pane, its card showing on hover.
function SessionNameView($: EngineInterface, elements: ElementTable, draw: ChatBarDraw) {
  const { chatBar } = draw
  const { Box, Button, Text } = elements
  if (chatBar.isMain) return MainChatListsView($, elements, draw)
  const name = (
    <Button key="session-name-button" plain onPress={() => openSessionFolder($)}>
      <Text weight="semibold" color={BRAND.text} wrap="truncate-end">{chatBar.sessionName}</Text>
    </Button>
  )
  // The name is the one part of the line that gives way: it shrinks and is cut short, so the buttons beside it stay in view.
  return (
    <Box key="session-name" flexDirection="row" gap={1} flexShrink={1} minWidth={0}>
      <Box flexDirection="row" flexShrink={1} minWidth={0} hover={{ scope: CARD_SCOPE }}>{name}</Box>
    </Box>
  )
}

// The main chat's two buttons, each with the list it opens and its name above it on hover.
function MainChatListsView($: EngineInterface, elements: ElementTable, draw: ChatBarDraw) {
  const { chatBar } = draw
  const { Box } = elements
  return (
    <Box key="session-name" flexDirection="row" gap={0}>
      <Box key="repo-anchor">
        {GlyphButtonView(elements, 'repo-list-button', REPO_GLYPH, BRAND.muted, () => toggleRepoListWithRepos($))}
        {draw.view.isRepoListOpen ? null : TipView(elements, repoWordOf(chatBar), '', BRAND.muted)}
        {RepoListView($, elements, draw)}
      </Box>
      <Box key="session-anchor" marginLeft={1}>
        <Box flexDirection="row" hover={{ scope: CARD_SCOPE }}>
          {GlyphButtonView(elements, 'session-list-button', SESSION_GLYPH, BRAND.muted, () => toggleSessionList($))}
        </Box>
        {draw.view.isSessionListOpen ? null : TipView(elements, sessionWordOf(chatBar), '', BRAND.muted)}
        {SessionListView($, elements, draw)}
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

// The debug button's bug: a flat outline in the muted brand grey, since the 🐞 emoji draws as a pink 3D bug. The desktop
// draws it as an image; a surface with no Svg element shows ⚑ instead.
const BUG_SVG = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" fill="none" stroke="${BRAND.muted}" stroke-width="1.3" stroke-linecap="round">`
  + '<ellipse cx="8" cy="9.5" rx="3.6" ry="4.5"/><path d="M8 5v9M5.6 4.6 4.5 3M10.4 4.6 11.5 3M4.4 8H2M11.6 8H14M4.6 11.5 2.6 13M11.4 11.5 13.4 13"/></svg>'

// The bug's size in the desktop's pixels, about one line of text tall.
const BUG_ICON_PIXELS = 14

function DebugButtonView($: EngineInterface, elements: ElementTable, chatBar: ChatBarClient) {
  if (!('Svg' in elements)) return IconButtonView(elements, 'debug', '⚑', DEBUG_WORDS, () => runDebug($, chatBar))
  const { Box, Button, Svg } = elements
  return (
    <Box key="debug-box">
      <Box key="debug-mark">
        <Svg source={BUG_SVG} alt="debug" width={BUG_ICON_PIXELS} height={BUG_ICON_PIXELS} />
        <Box position="absolute" top={0} left={0}>
          <Button key="debug" plain label=" " onPress={() => runDebug($, chatBar)} />
        </Box>
      </Box>
      {TipView(elements, DEBUG_WORDS, '', BRAND.muted)}
    </Box>
  )
}
const DEBUG_WORDS = 'debug: capture what went wrong, then fix it or request help'

// Files right after the action button: the shown stage's files in the Files app, every practice there with its toggle.
function FilesButtonView($: EngineInterface, elements: ElementTable, { chatBar }: ChatBarDraw) {
  return chatBar.stageFidelitySlugs.length ? IconButtonView(elements, 'files-button', '▤', 'files', () => openStageFiles($, chatBar)) : null
}

// Push, push & merge to origin/main, restart and close as icons.
function SessionButtonsView($: EngineInterface, elements: ElementTable, { chatBar, push }: ChatBarDraw) {
  const { Box } = elements
  return (
    <Box key="session-buttons" flexDirection="row" gap={1} flexShrink={0}>
      {push.buttons}
      {IconButtonView(elements, 'restart-button', '↻', 'restart cdd server', () => restartServer($))}
      {chatBar.isMain ? null : IconButtonView(elements, 'close-button', '✕', 'close session', () => openClose($, chatBar))}
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
        const colour = isOn ? BRAND.onAccent : BRAND.muted
        return (
          <Box key={`format-${choice.label}`} paddingX={1} backgroundColor={isOn ? BRAND.accent : undefined}>
            {GlyphButtonView(elements, `format-chip-${choice.label}`, formatGlyphOf(choice.label), colour, () => toggleFormat($, chatBar.sessionFile, choice.label))}
            {TipView(elements, choice.label, `offered by ${choice.offered}`, BRAND.muted)}
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
// CDD works in a git repository: a session's tickets get branches, worktrees and chats of their own. In a folder that is
// no repository the line asks for the repository first and offers nothing else; the folder's path is the part that
// gives way when the line is full.
function RepositoryRequiredView($: EngineInterface, elements: ElementTable, draw: ChatBarDraw) {
  const { Box, Button, Text } = elements
  return (
    <Box key="line" flexDirection="row" gap={1} alignItems="center">
      <Box flexDirection="row" flexShrink={1} minWidth={0}>
        <Text color={BRAND.muted} wrap="truncate-start">{`${draw.chatBar.folder} is no git repository, and CDD works in one`}</Text>
      </Box>
      <Button key="make-repository-button" label="Create the git repository" onPress={() => makeRepository($)} />
      <Box flexGrow={1} />
      {draw.health.band}
      {draw.version.badge}
    </Box>
  )
}

function LineView($: EngineInterface, elements: ElementTable, draw: ChatBarDraw) {
  const { Box, Text } = elements
  const { chatBar } = draw
  if (!chatBar.hasSession) return <Box key="line" flexDirection="row" gap={1}><Box flexGrow={1} />{SessionNameView($, elements, draw)}{draw.health.band}{draw.version.badge}</Box>
  if (chatBar.isPlainFolder) return RepositoryRequiredView($, elements, draw)
  return (
    <Box key="line" flexDirection="row" gap={1} alignItems="center">
        {StageButtonsView($, elements, draw)}
        <Text color={BRAND.border}>{SEPARATOR}</Text>
        {FidelityColumnView($, elements, draw)}
        <Box flexGrow={1} />
        {SessionNameView($, elements, draw)}
        {SessionButtonsView($, elements, draw)}
        {draw.health.band}
        {draw.version.badge}
    </Box>
  )
}

// The fidelity dots, the overlay and format chips, the action button, and the files, handoff, and debug buttons. The column
// never shrinks: a shrunk column drew its last buttons, debug first, under the session name, out of sight.
function FidelityColumnView($: EngineInterface, elements: ElementTable, draw: ChatBarDraw) {
  const { chatBar } = draw
  const { Box } = elements
  return (
    <Box key="fidelity-column" flexDirection="row" gap={1} alignItems="center" flexShrink={0}>
      {chatBar.practiceDots.map(dot => PracticeDotView($, elements, dot))}
      {OverlayChipsView($, elements, draw)}
      {FormatChipsView($, elements, draw)}
      {ActionButtonView($, elements, draw)}
      {FilesButtonView($, elements, draw)}
      {IconButtonView(elements, 'handoff', '⇥', 'handoff', () => runHandoff($, chatBar))}
      {DebugButtonView($, elements, chatBar)}
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
      {draw.health.walkQuestion}
      {CloseView($, elements, draw)}
      {chatBar.isPlainFolder ? null : SessionCardView($, elements, draw)}
      {chatBar.isPlainFolder ? null : ListRoomView(elements, draw)}
      {LineView($, elements, draw)}
    </Box>
  )
}
