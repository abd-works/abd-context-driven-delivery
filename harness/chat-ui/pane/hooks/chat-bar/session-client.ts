import type { EngineInterface } from 'claude-code'

import type { LeaveChoicesData, TicketData } from '@cdd/space/kanban/ticket'

import { reasonOf } from '../shared/failure'
import { callTool, callToolText, currentChatBar, refreshChatBar, showFailure, type ChatBarClient } from './chat-bar-client'
import { whileBusy } from './busy-client'
import { startedChatIn } from './chat-folder-client'
import type { RepoRowJson } from '../../types'
import { cancelClose, closeSessionList, currentChatBarView, showClose, showRepos, toggleSessionList } from './session-dialogs-client'

// The person's moves between sessions: open a ticket from the main chat, create one, close the active one. Each is one
// ticket tool; the dialogs they open and close, and what they chose, are in session-dialogs-client.ts. Sessions open
// only from main, and opening one never moves this chat: the ticket is worked on in a chat of its own, in its worktree.

// What a close did, in the board's words, ahead of what came of the session.
const LEFT_STEPS: Record<string, string> = { handoff: 'handoff written', commit: 'committed', push: 'pushed', merge: 'merged to main', delete_branch: 'branch deleted', delete_worktree: 'worktree deleted' }

// ticket.close refused to close the session. reason is the server's own text.
export class CloseRefused {
  constructor(readonly reason: string) {}
}

// ticket.activate opens the ticket in its own worktree and leaves this chat on main; the ticket's chat, found or
// started, does its work there.
export async function activateTicket($: EngineInterface, ticketName: string): Promise<void> {
  await closeSessionList($)
  const opened = await whileBusy($, `Opening ${ticketName}`, () => activatedTicket($, ticketName))
  await refreshChatBar($)
  if (opened) await startedChatIn($, opened)
}

// Null when the ticket did not open: the failure stays above the line.
async function activatedTicket($: EngineInterface, ticketName: string): Promise<TicketData | null> {
  try {
    return await callTool<TicketData>($, 'ticket.activate', { ticket: ticketName })
  } catch (failure) {
    await showFailure($, `${ticketName} did not open: ${reasonOf(failure)}`)
    return null
  }
}

// A new ticket opens as one picked from the list does.
export async function createSession($: EngineInterface, sessionName: string): Promise<void> {
  try {
    const created = await callTool<TicketData>($, 'ticket.create', { title: sessionName })
    await activateTicket($, created.name)
  } catch (failure) {
    await showFailure($, `${sessionName} was not created: ${reasonOf(failure)}`)
    await refreshChatBar($)
  }
}

// The main chat's + opens the session list, and with it the repositories beside this one; a list that cannot read them
// still opens, with the tickets alone.
export async function toggleSessionListWithRepos($: EngineInterface): Promise<void> {
  await toggleSessionList($)
  if (!(await currentChatBarView($)).isSessionListOpen) return
  try {
    await showRepos($, await callTool<RepoRowJson[]>($, 'repos.siblings', {}))
  } catch (failure) {
    await showRepos($, [])
    $.ui.toast(`Repositories not listed: ${reasonOf(failure)}`)
  }
}

// repos.open creates the repository when missing, publishes it private, installs CDD into it, and opens a new top-level
// chat there, where the person opens its main session.
export async function openRepo($: EngineInterface, name: string): Promise<void> {
  $.ui.toast(`Opening repository ${name}…`)
  await closeSessionList($)
  try {
    const answer = await whileBusy($, `Opening repository ${name}`, () => callToolText($, 'repos.open', { name, visibility: 'private' }))
    $.ui.toast(`${name}: ${answer.split('\n').pop()?.replace(/^- /, '') ?? 'opened'}`)
  } catch (failure) {
    await showFailure($, `${name} did not open: ${reasonOf(failure)}`)
  }
}

// The close dialog offers what the Python Ticket answers closing can do with the session's work.
export async function openClose($: EngineInterface, chatBar: ChatBarClient): Promise<void> {
  try {
    await showClose($, await callTool<LeaveChoicesData>($, 'ticket.close_choices', { ticket: chatBar.sessionName }))
  } catch (failure) {
    await showFailure($, `${chatBar.sessionName} cannot close: ${reasonOf(failure)}`)
  }
}

export async function closeSession($: EngineInterface, chatBar: ChatBarClient): Promise<ChatBarClient | CloseRefused> {
  const view = await currentChatBarView($)
  await cancelClose($)
  return whileBusy($, `Closing ${chatBar.sessionName}`, () => closedSession($, chatBar, view.leaving))
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
