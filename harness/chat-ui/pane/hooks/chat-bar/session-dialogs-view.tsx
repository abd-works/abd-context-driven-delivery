import type { EngineInterface } from 'claude-code'

import { BRAND } from '../brand'
import type { ChatBarDraw } from './chat-bar-view'
import { activateSession, closeSession, createSession } from './session-client'
import { cancelClose, cancelSwitch, pickSession } from './session-dialogs-client'

type ElementTable = ReturnType<EngineInterface['ui']['resolve']>

// The choices the board's activation and close dialogs make first, as board.activate and ticket.close receive them.
const LEAVE_CHOICES = '☑ commit ☑ push'
const OPEN_CHOICES = '☑ create branch ☑ create worktree'

// The sessions a person can switch to, each with its stage, and a field to name a new one.
export function SessionListView($: EngineInterface, { Box, Button, Input, Text }: ElementTable, { chatBar, view }: ChatBarDraw) {
  if (!view.isSessionListOpen) return null
  return (
    <Box key="session-list" flexDirection="column" paddingX={1} borderStyle="single" borderColor={BRAND.border} backgroundColor={BRAND.raised}>
      {chatBar.sessions.map(session => (
        <Box key={`session-row-${session.name}`} flexDirection="row" gap={1}>
          <Button key={`session-${session.name}`} plain label={session.name} onPress={() => pickSession($, session.name)}>
            <Text color={session.name === chatBar.sessionName ? BRAND.accent : BRAND.text}>{session.name}</Text>
          </Button>
          <Text color={BRAND.muted}>{session.stage}</Text>
        </Box>
      ))}
      <Input key="new-session" placeholder="New session name" value="" onSubmit={value => (value.trim() ? createSession($, value.trim()) : undefined)} />
    </Box>
  )
}

// Opening a session leaves the active one committed and pushed and opens the new one on its own branch and worktree.
export function ActivateView($: EngineInterface, { Box, Button, Text }: ElementTable, { chatBar, view }: ChatBarDraw) {
  const switchTo = view.switchTo
  if (!switchTo) return null
  const leaving = chatBar.sessionName ? `${chatBar.sessionName} is committed and pushed. ` : ''
  return (
    <Box key="activate" flexDirection="column" paddingX={1} borderStyle="single" borderColor={BRAND.accent} backgroundColor={BRAND.raised}>
      <Text weight="semibold" color={BRAND.text}>{`Open ${switchTo}`}</Text>
      {chatBar.sessionName ? <Text color={BRAND.text}>{`LEAVE ${LEAVE_CHOICES} ☐ merge`}</Text> : null}
      <Text color={BRAND.text}>{`OPEN ${OPEN_CHOICES}`}</Text>
      <Text color={BRAND.muted}>{`${leaving}${switchTo} opens on its own branch and worktree.`}</Text>
      <Box flexDirection="row" gap={1}>
        <Button key="activate-cancel" label="Cancel" onPress={() => cancelSwitch($)} />
        <Button key="activate-confirm" label="Open" variant="primary" onPress={() => activateSession($, switchTo)} />
      </Box>
    </Box>
  )
}

export function CloseView($: EngineInterface, { Box, Button, Text }: ElementTable, { chatBar, view }: ChatBarDraw) {
  if (!view.closing) return null
  const work = view.closing.hasBranch ? 'Its work is committed and pushed first.' : 'It has no branch of its own, so nothing is committed.'
  return (
    <Box key="close" flexDirection="column" paddingX={1} borderStyle="single" borderColor={BRAND.error} backgroundColor={BRAND.errorWash}>
      <Text weight="semibold" color={BRAND.text}>{`Close session ${chatBar.title}`}</Text>
      {view.closing.hasBranch ? <Text color={BRAND.text}>{`LEAVE ${LEAVE_CHOICES}`}</Text> : null}
      <Text color={BRAND.muted}>{work}</Text>
      <Box flexDirection="row" gap={1}>
        <Button key="close-cancel" label="Cancel" onPress={() => cancelClose($)} />
        <Button key="close-confirm" label="Close session" variant="primary" onPress={() => closeSession($, chatBar)} />
      </Box>
    </Box>
  )
}
