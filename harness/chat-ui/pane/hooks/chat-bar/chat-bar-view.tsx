import type { EngineInterface } from 'claude-code'

import type { ActionPickerJson, ChatBarViewJson, FidelityFilesJson } from '../../types'
import {
  activateSession,
  cancelClose,
  cancelSwitch,
  closeSession,
  createSession,
  moveNext,
  openClose,
  pickSession,
  runHandoff,
  toggleCard,
  toggleSessionList,
  type ChatBarClient,
} from './chat-bar-client'
import {
  ACTION_ICONS,
  BUILDER_ACTIONS,
  chooseAction,
  closeFiles,
  openBoard,
  openFiles,
  reviewFidelity,
  runAction,
  selectFidelity,
  showFile,
  toggleActionPicker,
  type FidelityClient,
} from './fidelity-client'
import { selectStage, type StageClient } from './stage-client'

type ElementTable = ReturnType<EngineInterface['ui']['resolve']>

// What one draw of the chat bar reads: the client built from board.show, and which boxes are open above the line.
export type ChatBarDraw = { bar: ChatBarClient; view: ChatBarViewJson; picker: ActionPickerJson; files: FidelityFilesJson }

// The abd.works engineering colours of the canvas (design/StageStrip.dc.html).
const BRAND = { surface: '#141418', raised: '#1B1B20', border: '#2A2A2A', text: '#E8E8ED', muted: '#9B9BA8', accent: '#E5531A', error: '#EF4444', errorWash: '#2F1414' }
const SEPARATOR = '│'
// The choices the board's activation and close dialogs make first, as ticket.activate and ticket.close receive them.
const LEAVE_CHOICES = '☑ commit ☑ push'
const OPEN_CHOICES = '☑ create branch ☑ create worktree'
// A file's text in the files view shows this many lines, so the box keeps above the prompt.
const FILE_LINES = 24

const actionOf = (bar: ChatBarClient): string => (bar.canMoveNext ? 'advance' : (bar.actionFidelity?.nextAction ?? ''))

// The action button runs what it shows: advance moves the session on, review records the person's approval, and every
// other action is a command the chat runs.
function pressAction($: EngineInterface, bar: ChatBarClient, action: string): unknown {
  const fidelity = bar.actionFidelity
  if (action === 'advance') return moveNext($, bar)
  if (!fidelity) return undefined
  return action === 'review' ? reviewFidelity($, fidelity) : runAction($, fidelity, action)
}

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

function ActionButtonView($: EngineInterface, { Box, Button, Text }: ElementTable, { bar }: ChatBarDraw) {
  const action = actionOf(bar)
  if (!action) return null
  const target = action === 'advance' ? `move ${bar.sessionName} on` : `${action} ${bar.actionFidelity?.guidance ?? ''}`
  return (
    <Box key="action" flexDirection="row" gap={0}>
      <Button key="next-action" plain label={target} onPress={() => pressAction($, bar, action)}>
        <Text color={BRAND.accent}>{ACTION_ICONS[action] ?? '•'}</Text>
      </Button>
      <Box position="absolute" top={-1} left={0} paddingX={1} backgroundColor={BRAND.raised} display="none" hover={{ display: 'flex' }}>
        <Text color={BRAND.text}>{target}</Text>
      </Box>
      <Button key="action-picker" plain label="▾" onPress={() => toggleActionPicker($)} />
    </Box>
  )
}

function PickerView($: EngineInterface, { Box, Button }: ElementTable, { bar, picker }: ChatBarDraw) {
  const fidelity = bar.actionFidelity
  if (!picker.isOpen || !fidelity) return null
  return (
    <Box key="picker" flexDirection="row" gap={1} paddingX={1} borderStyle="single" borderColor={BRAND.border} backgroundColor={BRAND.raised}>
      {BUILDER_ACTIONS.map(action => (
        <Button key={`pick-${action}`} label={`${ACTION_ICONS[action]} ${action}`} variant={action === fidelity.nextAction ? 'primary' : undefined} onPress={() => chooseAction($, fidelity, action)} />
      ))}
    </Box>
  )
}

function SessionListView($: EngineInterface, elements: ElementTable, { bar, view }: ChatBarDraw) {
  const { Box, Button, Input, Text } = elements
  if (!view.isSessionListOpen) return null
  return (
    <Box key="session-list" flexDirection="column" paddingX={1} borderStyle="single" borderColor={BRAND.border} backgroundColor={BRAND.raised}>
      {bar.sessions.map(session => (
        <Box key={`session-row-${session.name}`} flexDirection="row" gap={1}>
          <Button key={`session-${session.name}`} plain label={session.name} onPress={() => pickSession($, session.name)}>
            <Text color={session.name === bar.sessionName ? BRAND.accent : BRAND.text}>{session.name}</Text>
          </Button>
          <Text color={BRAND.muted}>{session.stage}</Text>
        </Box>
      ))}
      <Input key="new-session" placeholder="New session name" value="" onSubmit={value => (value.trim() ? createSession($, value.trim()) : undefined)} />
    </Box>
  )
}

// Opening a session leaves the active one committed and pushed and opens the new one on its own branch and worktree.
function ActivateView($: EngineInterface, { Box, Button, Text }: ElementTable, { bar, view }: ChatBarDraw) {
  const switchTo = view.switchTo
  if (!switchTo) return null
  const leaving = bar.sessionName ? `${bar.sessionName} is committed and pushed. ` : ''
  return (
    <Box key="activate" flexDirection="column" paddingX={1} borderStyle="single" borderColor={BRAND.accent} backgroundColor={BRAND.raised}>
      <Text weight="semibold" color={BRAND.text}>{`Open ${switchTo}`}</Text>
      {bar.sessionName ? <Text color={BRAND.text}>{`LEAVE ${LEAVE_CHOICES} ☐ merge`}</Text> : null}
      <Text color={BRAND.text}>{`OPEN ${OPEN_CHOICES}`}</Text>
      <Text color={BRAND.muted}>{`${leaving}${switchTo} opens on its own branch and worktree.`}</Text>
      <Box flexDirection="row" gap={1}>
        <Button key="activate-cancel" label="Cancel" onPress={() => cancelSwitch($)} />
        <Button key="activate-confirm" label="Open" variant="primary" onPress={() => activateSession($, switchTo)} />
      </Box>
    </Box>
  )
}

function CloseView($: EngineInterface, { Box, Button, Text }: ElementTable, { bar, view }: ChatBarDraw) {
  if (!view.closing) return null
  const work = view.closing.hasBranch ? 'Its work is committed and pushed first.' : 'It has no branch of its own, so nothing is committed.'
  return (
    <Box key="close" flexDirection="column" paddingX={1} borderStyle="single" borderColor={BRAND.error} backgroundColor={BRAND.errorWash}>
      <Text weight="semibold" color={BRAND.text}>{`Close session ${bar.title}`}</Text>
      {view.closing.hasBranch ? <Text color={BRAND.text}>{`LEAVE ${LEAVE_CHOICES}`}</Text> : null}
      <Text color={BRAND.muted}>{work}</Text>
      <Box flexDirection="row" gap={1}>
        <Button key="close-cancel" label="Cancel" onPress={() => cancelClose($)} />
        <Button key="close-confirm" label="Close session" variant="primary" onPress={() => closeSession($, bar)} />
      </Box>
    </Box>
  )
}

// Each fidelity's colour, name and state over its dot, its folder beside it, and the shown stage over the stage icons.
function SessionCardView({ Box, Text }: ElementTable, { bar, view }: ChatBarDraw) {
  if (!view.isCardOpen) return null
  return (
    <Box key="session-card" flexDirection="column" paddingX={1} borderStyle="single" borderColor={BRAND.border} backgroundColor={BRAND.raised}>
      <Box flexDirection="row" gap={1}>
        <Text weight="semibold" color={BRAND.text}>{bar.title}</Text>
        <Text color={BRAND.accent}>{bar.shownStage}</Text>
      </Box>
      {bar.fidelities.map(fidelity => (
        <Box key={`card-${fidelity.fidelity}`} flexDirection="row" gap={1}>
          <Text color={fidelity.colour}>{fidelity.mark}</Text>
          <Text color={BRAND.text}>{`${fidelity.name} ${fidelity.word}`}</Text>
          <Text color={BRAND.muted}>{fidelity.folder}</Text>
        </Box>
      ))}
    </Box>
  )
}

function FilesView($: EngineInterface, { Box, Button, Text }: ElementTable, { files }: ChatBarDraw) {
  if (!files) return null
  const shown = files.tabs.find(tab => tab.path === files.shown)
  const lines = (shown?.text ?? '').split('\n').slice(0, FILE_LINES)
  return (
    <Box key="files" flexDirection="column" paddingX={1} borderStyle="single" borderColor={BRAND.border} backgroundColor={BRAND.surface}>
      <Box flexDirection="row" gap={1} flexWrap="wrap">
        {files.tabs.map(tab => (
          <Button key={`file-${tab.path}`} label={tab.path.split('/').at(-1) ?? tab.path} variant={tab.path === files.shown ? 'primary' : undefined} onPress={() => showFile($, tab.path)} />
        ))}
        <Button key="files-close" label="✕" onPress={() => closeFiles($)} />
      </Box>
      {files.tabs.length ? lines.map((line, index) => <Text key={`line-${index}`} color={BRAND.text}>{line}</Text>) : <Text color={BRAND.muted}>{`${files.fidelity} declares no files.`}</Text>}
    </Box>
  )
}

function SessionNameView($: EngineInterface, { Box, Button, Text }: ElementTable, healthBand: unknown, { bar }: ChatBarDraw) {
  return (
    <Box key="session-name" flexDirection="row" gap={1}>
      {healthBand}
      <Button key="session-name-button" plain label={bar.sessionName || 'no session'} onPress={() => toggleCard($)}>
        <Text weight="semibold" color={bar.sessionName ? BRAND.text : BRAND.muted}>{bar.sessionName || 'no session'}</Text>
      </Button>
      <Button key="session-list-button" plain label="▾" onPress={() => toggleSessionList($)} />
    </Box>
  )
}

function SessionButtonsView($: EngineInterface, { Box, Button }: ElementTable, { bar }: ChatBarDraw) {
  const fidelity = bar.actionFidelity
  return (
    <Box key="session-buttons" flexDirection="row" gap={1}>
      <Button key="handoff" plain label="⇥ handoff" onPress={() => runHandoff($, bar)} />
      {fidelity ? <Button key="files-button" plain label="▤ files" onPress={() => openFiles($, fidelity)} /> : null}
      <Button key="close-button" plain label="✕ close" onPress={() => openClose($, bar)} />
    </Box>
  )
}

function LineView($: EngineInterface, elements: ElementTable, healthBand: unknown, draw: ChatBarDraw) {
  const { Box, Text } = elements
  const { bar } = draw
  if (!bar.session) return <Box key="line" flexDirection="row" gap={1}>{SessionNameView($, elements, healthBand, draw)}</Box>
  return (
    <Box key="line" flexDirection="row" gap={1} flexWrap="wrap">
      {SessionNameView($, elements, healthBand, draw)}
      <Text color={BRAND.border}>{SEPARATOR}</Text>
      {bar.fidelities.map(fidelity => FidelityView($, elements, fidelity))}
      {ActionButtonView($, elements, draw)}
      <Text color={BRAND.border}>{SEPARATOR}</Text>
      {bar.stages.map(stage => StageView($, elements, stage))}
      <Box flexGrow={1} />
      {SessionButtonsView($, elements, draw)}
    </Box>
  )
}

// The chat bar above the prompt: the boxes a person opened sit above one line holding the server health mark, the
// session name, the fidelity dots, the action button, and the stage icons. A failed board read says so above the line.
export function ChatBarView($: EngineInterface, elements: ElementTable, healthBand: unknown, draw: ChatBarDraw, width: number) {
  const { Box, Text } = elements
  const { bar } = draw
  return (
    <Box key="chat-bar" flexDirection="column" width={width}>
      {bar.problem ? <Text color={BRAND.error}>{`The board did not answer: ${bar.problem}`}</Text> : null}
      {FilesView($, elements, draw)}
      {CloseView($, elements, draw)}
      {ActivateView($, elements, draw)}
      {SessionListView($, elements, draw)}
      {SessionCardView(elements, draw)}
      {PickerView($, elements, draw)}
      {LineView($, elements, healthBand, draw)}
    </Box>
  )
}
