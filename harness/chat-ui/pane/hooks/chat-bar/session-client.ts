import type { EngineInterface } from 'claude-code'

import type { LeaveChoicesData, TicketData } from '@cdd/space/kanban/ticket'

import { shownAsFailure } from '../error-display/failure-client'
import { reasonOf } from '../shared/reason'
import { chosenFolder } from '../shared/folder-dialog'
import { callTool, callToolText } from '../shared/cdd-tool'
import { currentChatBar, refreshChatBar, type ChatBarClient } from './chat-bar-client'
import { whileBusy } from './busy-client'
import { startedChatIn } from './chat-folder-client'
import type { RepoRowJson } from '../../types'
import { cancelClose, chooseNewSessionFolder, closeRepoList, closeSessionList, currentChatBarView, showClose, showRepos, toggleRepoList } from './session-dialogs-client'

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
// started, does its work there. A ticket that did not open starts no chat, and its failure stays above the line.
export async function activateTicket($: EngineInterface, ticketName: string): Promise<void> {
  await closeSessionList($)
  try {
    const opened = await whileBusy($, `Opening ${ticketName}`, () => callTool<TicketData>($, 'ticket.activate', { ticket: ticketName }))
    await refreshChatBar($)
    await startedChatIn($, opened)
  } catch (failure) {
    await shownAsFailure($, `${ticketName} did not open`, `Opening ${ticketName} from the session list, calling ticket.activate`)(failure)
    await refreshChatBar($)
  }
}

// A new ticket opens as one picked from the list does, its session working on the folder chosen beside its name, or the
// whole repository when none was. Python refuses a folder outside the repository.
export async function createSession($: EngineInterface, sessionName: string): Promise<void> {
  const path = (await currentChatBarView($)).newSessionFolder
  try {
    const created = await callTool<TicketData>($, 'ticket.create', { title: sessionName, ...(path ? { path } : {}) })
    await chooseNewSessionFolder($, '')
    await activateTicket($, created.name)
  } catch (failure) {
    await shownAsFailure($, `${sessionName} was not created`, `Creating a session${path ? ` on ${path}` : ''}, calling ticket.create`)(failure)
    await refreshChatBar($)
  }
}

// The main chat's repo button opens the repositories beside this one, read afresh each time; a list that cannot read
// them opens empty, with the field for a new one.
export async function toggleRepoListWithRepos($: EngineInterface): Promise<void> {
  await toggleRepoList($)
  if (!(await currentChatBarView($)).isRepoListOpen) return
  try {
    await showRepos($, await callTool<RepoRowJson[]>($, 'repos.siblings', {}))
  } catch (failure) {
    await showRepos($, [])
    await shownAsFailure($, 'Repositories not listed', 'Opening the repository list, calling repos.siblings')(failure)
  }
}

// repos.open creates the repository when missing, publishes it private, installs CDD into it, and opens a new top-level
// chat there, where the person opens its main session.
export async function openRepo($: EngineInterface, name: string): Promise<void> {
  $.ui.toast(`Opening repository ${name}…`)
  await closeRepoList($)
  try {
    const answer = await whileBusy($, `Opening repository ${name}`, () => callToolText($, 'repos.open', { name, visibility: 'private' }))
    $.ui.toast(`${name}: ${answer.split('\n').pop()?.replace(/^- /, '') ?? 'opened'}`)
  } catch (failure) {
    await shownAsFailure($, `${name} did not open`, `Opening repository ${name}, calling repos.open`)(failure)
  }
}

// repo.make_repository makes the plain folder this chat works in a git repository on main, so its tickets get branches,
// worktrees and chats of their own; the bar is read again, and then draws the session in place of the request.
export async function makeRepository($: EngineInterface): Promise<void> {
  try {
    const answer = await whileBusy($, 'Making this folder a git repository', () => callToolText($, 'repo.make_repository', {}))
    $.ui.toast(answer)
  } catch (failure) {
    await shownAsFailure($, 'The folder was not made a git repository', 'Making a git repository from the chat bar, calling repo.make_repository')(failure)
  }
  await refreshChatBar($)
}

// The folder button beside the new session's name asks the system's folder picker, opened at the repository's top, for
// the folder the session will work on; cancelling it keeps the folder chosen before.
export async function chooseSessionFolder($: EngineInterface, chatBar: ChatBarClient): Promise<void> {
  const path = await chosenFolder($, { startIn: chatBar.folder, purpose: 'Choose the folder in this repository the new session works on' })
    .catch(shownAsFailure($, 'The folder picker did not open', 'The folder button beside the new session name'))
  if (path) await chooseNewSessionFolder($, path)
}

// The close dialog offers what the Python Ticket answers closing can do with the session's work.
export async function openClose($: EngineInterface, chatBar: ChatBarClient): Promise<void> {
  try {
    await showClose($, await callTool<LeaveChoicesData>($, 'ticket.close_choices', { ticket: chatBar.sessionName }))
  } catch (failure) {
    await shownAsFailure($, `${chatBar.sessionName} cannot close`, `Opening the close dialog, calling ticket.close_choices`)(failure)
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
    await shownAsFailure($, `${chatBar.title} did not close`, `Closing ${chatBar.sessionName}${leaving.length ? ` leaving ${leaving.join(', ')}` : ''}, calling ticket.close`)(failure)
    return new CloseRefused(reasonOf(failure))
  }
  const left = leaving.map(step => LEFT_STEPS[step] ?? step)
  $.ui.toast(`${left.length ? `${chatBar.title}: ${left.join(', ')} · ` : ''}Session ${chatBar.title} closed`)
  await refreshChatBar($)
  return currentChatBar($)
}
