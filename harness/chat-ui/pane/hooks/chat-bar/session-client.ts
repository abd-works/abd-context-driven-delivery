import type { EngineInterface } from 'claude-code'

import type { BranchData, TicketData } from '@cdd/space/kanban/ticket'

import { reasonOf } from '../failure'
import { callTool, currentChatBar, refreshChatBar, type ChatBarClient } from './chat-bar-client'
import { cancelClose, cancelSwitch, currentChatBarView, pickSession, showClose } from './session-dialogs-client'

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

// A new session opens through the same activation dialog as one picked from the list.
export async function createSession($: EngineInterface, sessionName: string): Promise<ChatBarClient> {
  try {
    const created = await callTool<TicketData>($, 'ticket.create', { title: sessionName })
    await pickSession($, created.name)
  } catch (failure) {
    $.ui.toast(`${sessionName} was not created: ${reasonOf(failure)}`)
  }
  await refreshChatBar($)
  return currentChatBar($)
}

// The close dialog offers to commit and push the branch the session's work is on, its own or main, only while it is
// checked out, since those steps act on whatever is checked out.
export async function openClose($: EngineInterface, chatBar: ChatBarClient): Promise<void> {
  try {
    const branch = await callTool<BranchData>($, 'ticket.work_branch', { ticket: chatBar.sessionName })
    await showClose($, branch.is_checked_out ? branch.name : null)
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
