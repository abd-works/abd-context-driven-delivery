import type { EngineInterface } from 'claude-code'

import type { LeaveChoicesData, OpenChoicesData, TicketData } from '@cdd/space/kanban/ticket'

import { reasonOf } from '../shared/failure'
import { callTool, currentChatBar, refreshChatBar, type ChatBarClient } from './chat-bar-client'
import { cancelClose, cancelSwitch, currentChatBarView, showClose, showSwitch } from './session-dialogs-client'

// The person's moves between sessions: open one, create one, close the active one. Each is one ticket tool; the
// dialogs they open and close, and what they chose, are in session-dialogs-client.ts.

// What a close did, in the board's words, ahead of what came of the session.
const LEFT_STEPS: Record<string, string> = { handoff: 'handoff written', commit: 'committed', push: 'pushed', merge: 'merged to main' }

// ticket.close refused to close the session. reason is the server's own text.
export class CloseRefused {
  constructor(readonly reason: string) {}
}

export async function activateSession($: EngineInterface, sessionName: string): Promise<ChatBarClient> {
  const { leaving, opening } = await currentChatBarView($)
  try {
    await callTool<TicketData>($, 'ticket.activate', { ticket: sessionName, leaving, opening })
  } catch (failure) {
    $.ui.toast(`${sessionName} did not open: ${reasonOf(failure)}`)
  }
  await cancelSwitch($)
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
    $.ui.toast(`${name} cannot open: ${reasonOf(failure)}`)
  }
}

// A new session opens through the same activation dialog as one picked from the list.
export async function createSession($: EngineInterface, chatBar: ChatBarClient, sessionName: string): Promise<ChatBarClient> {
  try {
    const created = await callTool<TicketData>($, 'ticket.create', { title: sessionName })
    await pickSession($, chatBar, created.name)
  } catch (failure) {
    $.ui.toast(`${sessionName} was not created: ${reasonOf(failure)}`)
  }
  await refreshChatBar($)
  return currentChatBar($)
}

// The close dialog offers what the Python Ticket answers closing can do with the session's work.
export async function openClose($: EngineInterface, chatBar: ChatBarClient): Promise<void> {
  try {
    await showClose($, await callTool<LeaveChoicesData>($, 'ticket.close_choices', { ticket: chatBar.sessionName }))
  } catch (failure) {
    $.ui.toast(`${chatBar.sessionName} cannot close: ${reasonOf(failure)}`)
  }
}

// Null when closing leaves no session active.
export async function closeSession($: EngineInterface, chatBar: ChatBarClient): Promise<ChatBarClient | null | CloseRefused> {
  const { leaving } = await currentChatBarView($)
  try {
    await callTool<TicketData>($, 'ticket.close', { ticket: chatBar.sessionName, leaving })
  } catch (failure) {
    $.ui.toast(`${chatBar.title} did not close: ${reasonOf(failure)}`)
    return new CloseRefused(reasonOf(failure))
  }
  const left = leaving.map(step => LEFT_STEPS[step] ?? step)
  $.ui.toast(`${left.length ? `${chatBar.title}: ${left.join(', ')} · ` : ''}Session ${chatBar.title} closed`)
  await cancelClose($)
  await refreshChatBar($)
  const after = await currentChatBar($)
  return after.hasSession ? after : null
}
