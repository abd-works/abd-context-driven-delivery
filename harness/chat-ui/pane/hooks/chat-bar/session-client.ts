import type { EngineInterface } from 'claude-code'

import type { LeaveChoicesData, OpenChoicesData, TicketData } from '@cdd/space/kanban/ticket'

import { reasonOf } from '../shared/failure'
import { callTool, currentChatBar, refreshChatBar, showFailure, type ChatBarClient } from './chat-bar-client'
import { whileBusy } from './busy-client'
import { followSession, moveToMainCheckout } from './chat-folder-client'
import { cancelClose, cancelSwitch, currentChatBarView, showClose, showSwitch } from './session-dialogs-client'

// The person's moves between sessions: open one, create one, close the active one. Each is one ticket tool; the
// dialogs they open and close, and what they chose, are in session-dialogs-client.ts.

// What a close did, in the board's words, ahead of what came of the session.
const LEFT_STEPS: Record<string, string> = { handoff: 'handoff written', commit: 'committed', push: 'pushed', merge: 'merged to main', delete_branch: 'branch deleted', delete_worktree: 'worktree deleted' }
// Deleting the worktree this chat works in would leave the chat in a folder that is gone, so it moves out first.
const DELETE_WORKTREE = 'delete_worktree'
// Deleting a branch deletes the worktree that has it checked out, so the chat moves out for it too.
const DELETE_BRANCH = 'delete_branch'

// ticket.close refused to close the session. reason is the server's own text.
export class CloseRefused {
  constructor(readonly reason: string) {}
}

// Deleting a worktree the chat still works in fails halfway, so the chat moves out first and nothing runs until it has.
// Answers why it could not, or '' when the chat is out or nothing deletes a worktree.
async function leftWorktreeFor($: EngineInterface, leaving: string[]): Promise<string> {
  return leaving.includes(DELETE_WORKTREE) || leaving.includes(DELETE_BRANCH) ? moveToMainCheckout($) : ''
}

export async function activateSession($: EngineInterface, sessionName: string): Promise<ChatBarClient> {
  const { leaving, opening } = await currentChatBarView($)
  await cancelSwitch($)
  const stuck = await whileBusy($, 'Moving this chat out of its worktree', () => leftWorktreeFor($, leaving))
  if (stuck) {
    await showFailure($, `${sessionName} did not open, and nothing was changed: ${stuck}`)
    return currentChatBar($)
  }
  const after = await whileBusy($, `Opening ${sessionName}`, () => activatedSession($, sessionName, leaving, opening))
  if (!after) return currentChatBar($)
  // The chat bar's switch moves this chat to the new session's worktree, so its branch and files follow CDD. The move
  // runs after the wheel stops: where the agent is asked to move the chat, its answer waits for the agent's turn to end.
  await followSession($, after)
  return after
}

// Null when the switch failed: the failure stays above the line and the chat stays where it is.
async function activatedSession($: EngineInterface, sessionName: string, leaving: string[], opening: string[]): Promise<ChatBarClient | null> {
  try {
    await callTool<TicketData>($, 'ticket.activate', { ticket: sessionName, leaving, opening })
  } catch (failure) {
    await refreshChatBar($)
    await showFailure($, `${sessionName} did not open: ${reasonOf(failure)}`)
    return null
  }
  await refreshChatBar($)
  return currentChatBar($)
}

// Picking a session opens the activation dialog on it, with what leaving the active session and opening this one can
// do now, as their Tickets answer.
export async function pickSession($: EngineInterface, chatBar: ChatBarClient, name: string): Promise<void> {
  try {
    const [leaving, opening] = await Promise.all([
      chatBar.hasSession ? callTool<LeaveChoicesData>($, 'ticket.leave_choices', { ticket: chatBar.sessionName }) : null,
      callTool<OpenChoicesData>($, 'ticket.open_choices', { ticket: name }),
    ])
    await showSwitch($, name, leaving, opening)
  } catch (failure) {
    await showFailure($, `${name} cannot open: ${reasonOf(failure)}`)
  }
}

// A new session opens through the same activation dialog as one picked from the list.
export async function createSession($: EngineInterface, chatBar: ChatBarClient, sessionName: string): Promise<ChatBarClient> {
  try {
    const created = await callTool<TicketData>($, 'ticket.create', { title: sessionName })
    await pickSession($, chatBar, created.name)
  } catch (failure) {
    await showFailure($, `${sessionName} was not created: ${reasonOf(failure)}`)
  }
  await refreshChatBar($)
  return currentChatBar($)
}

// The close dialog offers what the Python Ticket answers closing can do with the session's work.
export async function openClose($: EngineInterface, chatBar: ChatBarClient): Promise<void> {
  try {
    await showClose($, await callTool<LeaveChoicesData>($, 'ticket.close_choices', { ticket: chatBar.sessionName }))
  } catch (failure) {
    await showFailure($, `${chatBar.sessionName} cannot close: ${reasonOf(failure)}`)
  }
}

// Null when closing leaves no session active.
export async function closeSession($: EngineInterface, chatBar: ChatBarClient): Promise<ChatBarClient | null | CloseRefused> {
  const { leaving } = await currentChatBarView($)
  await cancelClose($)
  const stuck = await whileBusy($, 'Moving this chat out of its worktree', () => leftWorktreeFor($, leaving))
  if (stuck) {
    const reason = `${chatBar.title} did not close, and nothing was changed: ${stuck}`
    await showFailure($, reason)
    return new CloseRefused(reason)
  }
  const after = await whileBusy($, `Closing ${chatBar.sessionName}`, () => closedSession($, chatBar, leaving))
  if (after instanceof CloseRefused) return after
  // With the session closed, the chat goes back to the main checkout, which closing returned to the default branch.
  // The move runs after the wheel stops, as a switch's does.
  await followSession($, after)
  return after.hasSession ? after : null
}

async function closedSession($: EngineInterface, chatBar: ChatBarClient, leaving: string[]): Promise<ChatBarClient | CloseRefused> {
  try {
    await callTool<TicketData>($, 'ticket.close', { ticket: chatBar.sessionName, leaving })
  } catch (failure) {
    await refreshChatBar($)
    await showFailure($, `${chatBar.title} did not close: ${reasonOf(failure)}`)
    return new CloseRefused(reasonOf(failure))
  }
  const left = leaving.map(step => LEFT_STEPS[step] ?? step)
  $.ui.toast(`${left.length ? `${chatBar.title}: ${left.join(', ')} · ` : ''}Session ${chatBar.title} closed`)
  await refreshChatBar($)
  return currentChatBar($)
}
