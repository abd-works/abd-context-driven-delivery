import type { EngineInterface } from 'claude-code'

import type { WorkspaceData } from '@cdd/harness/kanban/board'
import type { TicketData } from '@cdd/harness/kanban/ticket'

import { reasonOf } from '../failure'
import { callTool, currentChatBar, refreshChatBar, type ChatBarClient } from './chat-bar-client'
import { cancelClose, cancelSwitch, currentChatBarView, pickSession, showClose } from './session-dialogs-client'

// The person's moves between sessions: open one, create one, close the active one. Each is one ticket tool; the
// dialogs they open and close are in session-dialogs-client.ts.

// What the board's activation dialog chooses first: leave the old session committed and pushed, open the new one on
// its own branch and worktree.
const LEAVING = ['commit', 'push']
const OPENING = ['branch', 'worktree']

// ticket.close refused to close the session. reason is the server's own text.
export class CloseRefused {
  constructor(readonly reason: string) {}
}

export async function activateSession($: EngineInterface, sessionName: string): Promise<ChatBarClient> {
  try {
    await callTool<TicketData>($, 'ticket.activate', { ticket: sessionName, leaving: LEAVING, opening: OPENING })
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

// The close dialog offers to commit and push only when the session has a branch of its own.
export async function openClose($: EngineInterface, chatBar: ChatBarClient): Promise<void> {
  try {
    const workspace = await callTool<WorkspaceData>($, 'ticket.workspace', { ticket: chatBar.sessionName })
    await showClose($, workspace.leaving_has_branch)
  } catch (failure) {
    $.ui.toast(`${chatBar.sessionName} cannot close: ${reasonOf(failure)}`)
  }
}

// Null when closing leaves no session active.
export async function closeSession($: EngineInterface, chatBar: ChatBarClient): Promise<ChatBarClient | null | CloseRefused> {
  const { closing } = await currentChatBarView($)
  const leaving = closing?.hasBranch ? LEAVING : []
  try {
    await callTool<TicketData>($, 'ticket.close', { ticket: chatBar.sessionName, leaving })
  } catch (failure) {
    $.ui.toast(`${chatBar.title} did not close: ${reasonOf(failure)}`)
    return new CloseRefused(reasonOf(failure))
  }
  const left = leaving.length ? `${chatBar.title}: committed, pushed · ` : ''
  $.ui.toast(`${left}Session ${chatBar.title} closed`)
  await cancelClose($)
  await refreshChatBar($)
  const after = await currentChatBar($)
  return after.hasSession ? after : null
}
