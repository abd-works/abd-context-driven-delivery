import type { EngineInterface } from 'claude-code'

import { BRAND } from '../shared/brand'
import type { ChatBarDraw } from './chat-bar-view'
import { activateSession, closeSession, createSession, pickSession } from './session-client'
import { cancelClose, cancelSwitch, toggleLeaving, toggleOpening } from './session-dialogs-client'
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

// Each choice the Ticket offers for leaving a session, by the word TicketCheckout.leave reads, as the dialog words it
// for the branch it acts on.
function leaveLabelOf(word: string, branch: string): string {
  const labels: Record<string, string> = {
    handoff: 'Create handoff',
    commit: 'commit',
    push: 'push',
    merge: 'merge into main',
    delete_branch: `delete branch ${branch}`,
    delete_worktree: 'delete worktree',
  }
  return labels[word] ?? word
}

function leavingChoices($: EngineInterface, prefix: string, view: ChatBarDraw['view']): Choice[] {
  return view.leaveChoices.map(word => ({ key: `${prefix}-${word}`, label: leaveLabelOf(word, view.leaveBranch), isChosen: view.leaving.includes(word), onPress: () => toggleLeaving($, word) }))
}

// The LEAVE line names the session being left and the branch its work is on.
function leaveHeadingOf(session: string, branch: string): string {
  return `LEAVE ${session}${branch ? ` on ${branch}` : ''}`
}

// The sessions a person can switch to, each after its stage's orange icon, and a field to name a new one.
export function SessionListView($: EngineInterface, { Box, Button, Input, Text }: ElementTable, { chatBar, view }: ChatBarDraw) {
  if (!view.isSessionListOpen) return null
  return (
    <Box key="session-list" flexDirection="column" paddingX={1} borderStyle="single" borderColor={BRAND.border} backgroundColor={BRAND.raised}>
      {chatBar.openTickets.map(ticket => (
        <Box key={`session-row-${ticket.name}`} flexDirection="row" gap={1}>
          <Text color={BRAND.accent}>{stageIconOf(ticket.stage)}</Text>
          <Button key={`session-${ticket.name}`} plain onPress={() => pickSession($, chatBar, ticket.name)}>
            <Text color={ticket.name === chatBar.sessionName ? BRAND.accent : BRAND.text}>{ticket.name}</Text>
          </Button>
        </Box>
      ))}
      <Input key="new-session" placeholder="New session name" value="" onSubmit={value => (value.trim() ? createSession($, chatBar, value.trim()) : undefined)} />
    </Box>
  )
}

// Opening a session leaves the active one with what the person chose, from what the active Ticket offers, and opens the
// new one with what its Ticket offers to create.
export function ActivateView($: EngineInterface, elements: ElementTable, { chatBar, view }: ChatBarDraw) {
  const { Box, Button, Text } = elements
  const switchTo = view.switchTo
  if (!switchTo) return null
  const leaving = leavingChoices($, 'leave', view)
  const opening: Choice[] = view.openChoices.map(word => ({ key: `open-${word}`, label: `create ${word}`, isChosen: view.opening.includes(word), onPress: () => toggleOpening($, word) }))
  return (
    <Box key="activate" flexDirection="column" paddingX={1} borderStyle="single" borderColor={BRAND.accent} backgroundColor={BRAND.raised}>
      <Text weight="semibold" color={BRAND.text}>{`Open ${switchTo}`}</Text>
      {chatBar.sessionName ? ChoicesView(elements, leaveHeadingOf(chatBar.sessionName, view.leaveBranch), leaving) : null}
      {ChoicesView(elements, 'OPEN', opening)}
      <Box flexDirection="row" gap={1}>
        <Button key="activate-cancel" label="Cancel" onPress={() => cancelSwitch($)} />
        <Button key="activate-confirm" label="Open" variant="primary" onPress={() => activateSession($, switchTo)} />
      </Box>
    </Box>
  )
}

// Closing offers what ticket.close_choices answers: a handoff always, and a commit and a push of the branch the
// session's work is on while it is checked out, named beside each.
export function CloseView($: EngineInterface, elements: ElementTable, { chatBar, view }: ChatBarDraw) {
  const { Box, Button, Text } = elements
  if (!view.closing) return null
  const { branch } = view.closing
  const choices = leavingChoices($, 'close', view)
  return (
    <Box key="close" flexDirection="column" paddingX={1} borderStyle="single" borderColor={BRAND.error} backgroundColor={BRAND.errorWash}>
      <Text weight="semibold" color={BRAND.text}>{`Close session ${chatBar.title}`}</Text>
      {ChoicesView(elements, leaveHeadingOf(chatBar.sessionName, view.leaveBranch), choices)}
      {branch ? null : <Text color={BRAND.muted}>Nothing checked out is this session's, so nothing is committed.</Text>}
      <Box flexDirection="row" gap={1}>
        <Button key="close-cancel" label="Cancel" onPress={() => cancelClose($)} />
        <Button key="close-confirm" label="Close session" variant="primary" onPress={() => closeSession($, chatBar)} />
      </Box>
    </Box>
  )
}
