import type { EngineInterface } from 'claude-code'

import { BRAND } from '../brand'
import type { ChatBarDraw } from './chat-bar-view'
import { activateSession, closeSession, createSession } from './session-client'
import { cancelClose, cancelSwitch, pickSession, toggleLeaving, toggleOpening } from './session-dialogs-client'
import { stageIconOf } from './stage-client'

type ElementTable = ReturnType<EngineInterface['ui']['resolve']>

// One choice of a dialog: a press turns it on or off, and its box shows which.
type Choice = { key: string; label: string; isChosen: boolean; onPress: () => unknown }

function ChoiceView({ Button }: ElementTable, choice: Choice) {
  return <Button key={choice.key} plain label={`${choice.isChosen ? '☑' : '☐'} ${choice.label}`} onPress={choice.onPress} />
}

// A dialog's group of choices, after its heading, such as LEAVE or OPEN.
function ChoicesView(elements: ElementTable, heading: string, choices: Choice[]) {
  const { Box, Text } = elements
  return (
    <Box key={`choices-${heading}`} flexDirection="row" gap={1} flexWrap="wrap" alignItems="center">
      <Text color={BRAND.text}>{heading}</Text>
      {choices.map(choice => ChoiceView(elements, choice))}
    </Box>
  )
}

// Ticket.leave reads each choice by this word: write a handoff for the session left, commit, push, merge.
function leavingChoice($: EngineInterface, prefix: string, chosen: string[], word: string, label: string): Choice {
  return { key: `${prefix}-${word}`, label, isChosen: chosen.includes(word), onPress: () => toggleLeaving($, word) }
}

// The sessions a person can switch to, each after its stage's orange icon, and a field to name a new one.
export function SessionListView($: EngineInterface, { Box, Button, Input, Text }: ElementTable, { chatBar, view }: ChatBarDraw) {
  if (!view.isSessionListOpen) return null
  return (
    <Box key="session-list" flexDirection="column" paddingX={1} borderStyle="single" borderColor={BRAND.border} backgroundColor={BRAND.raised}>
      {chatBar.sessions.map(session => (
        <Box key={`session-row-${session.name}`} flexDirection="row" gap={1}>
          <Text color={BRAND.accent}>{stageIconOf(session.stage)}</Text>
          <Button key={`session-${session.name}`} plain onPress={() => pickSession($, session.name)}>
            <Text color={session.name === chatBar.sessionName ? BRAND.accent : BRAND.text}>{session.name}</Text>
          </Button>
        </Box>
      ))}
      <Input key="new-session" placeholder="New session name" value="" onSubmit={value => (value.trim() ? createSession($, value.trim()) : undefined)} />
    </Box>
  )
}

// Opening a session leaves the active one with what the person chose, a handoff, a commit and a push at first, and
// opens the new one on its own branch and worktree.
export function ActivateView($: EngineInterface, elements: ElementTable, { chatBar, view }: ChatBarDraw) {
  const { Box, Button, Text } = elements
  const switchTo = view.switchTo
  if (!switchTo) return null
  const leaving = ['handoff', 'commit', 'push', 'merge'].map(word => leavingChoice($, 'leave', view.leaving, word, word === 'handoff' ? 'Create handoff' : word))
  const opening: Choice[] = ['branch', 'worktree'].map(word => ({ key: `open-${word}`, label: `create ${word}`, isChosen: view.opening.includes(word), onPress: () => toggleOpening($, word) }))
  return (
    <Box key="activate" flexDirection="column" paddingX={1} borderStyle="single" borderColor={BRAND.accent} backgroundColor={BRAND.raised}>
      <Text weight="semibold" color={BRAND.text}>{`Open ${switchTo}`}</Text>
      {chatBar.sessionName ? ChoicesView(elements, 'LEAVE', leaving) : null}
      {ChoicesView(elements, 'OPEN', opening)}
      <Box flexDirection="row" gap={1}>
        <Button key="activate-cancel" label="Cancel" onPress={() => cancelSwitch($)} />
        <Button key="activate-confirm" label="Open" variant="primary" onPress={() => activateSession($, switchTo)} />
      </Box>
    </Box>
  )
}

// Closing offers a handoff always, and to commit and push the branch the session's work is on, its own or main, while
// it is checked out. Main has no branch to merge and no worktree to remove, so closing never offers either.
export function CloseView($: EngineInterface, elements: ElementTable, { chatBar, view }: ChatBarDraw) {
  const { Box, Button, Text } = elements
  if (!view.closing) return null
  const { branch } = view.closing
  const handoff = leavingChoice($, 'close', view.leaving, 'handoff', 'Create handoff')
  const work = branch ? ['commit', 'push'].map(word => leavingChoice($, 'close', view.leaving, word, `${word} ${branch}`)) : []
  return (
    <Box key="close" flexDirection="column" paddingX={1} borderStyle="single" borderColor={BRAND.error} backgroundColor={BRAND.errorWash}>
      <Text weight="semibold" color={BRAND.text}>{`Close session ${chatBar.title}`}</Text>
      {ChoicesView(elements, 'LEAVE', [handoff, ...work])}
      {branch ? null : <Text color={BRAND.muted}>Nothing checked out is this session's, so nothing is committed.</Text>}
      <Box flexDirection="row" gap={1}>
        <Button key="close-cancel" label="Cancel" onPress={() => cancelClose($)} />
        <Button key="close-confirm" label="Close session" variant="primary" onPress={() => closeSession($, chatBar)} />
      </Box>
    </Box>
  )
}
