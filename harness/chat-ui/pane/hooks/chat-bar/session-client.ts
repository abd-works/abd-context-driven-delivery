import type { EngineInterface } from 'claude-code'

import type { LeaveChoicesData, OpenChoicesData } from '@cdd/space/kanban/ticket'

import { reasonOf } from '../shared/failure'
import { callTool, MAIN_SESSION, showFailure, type ChatBarClient } from './chat-bar-client'
import { cancelClose, cancelSwitch, currentChatBarView, showClose, showSwitch } from './session-dialogs-client'

// The person's moves between sessions: open one, create one, close the active one. The dialogs read what each Ticket
// offers; confirming one puts a command in the chat box, as the other chat bar buttons do, and the agent runs it. A
// switch has to move this chat between folders and may delete the worktree it works in, which only the agent can see
// through and recover from, so the chat bar asks it instead of running the steps itself.

const listed = (words: string[]): string => (words.length ? words.join(', ') : 'nothing')

// The steps the agent takes for a switch: leave the active session, open the new one, and move the chat to its folder.
function openCommandOf(name: string, current: string, leaving: string[], opening: string[]): string {
  const leave = current ? `Leave session ${current} doing: ${listed(leaving)}. ` : ''
  const open = name === MAIN_SESSION ? `call board.open_main with leaving=[${leaving.join(', ')}]` : `call ticket.activate with ticket=${name}, leaving=[${leaving.join(', ')}], opening=[${opening.join(', ')}]`
  return `Open session ${name}. ${leave}If leaving deletes the worktree or branch this chat works in, first move this chat to the main checkout with change_directory. Then ${open}, and move this chat with change_directory to the folder the session now works in.`
}

// Main has nothing to create: it is the repository's own folder, which board.open_main puts on the default branch.
const MAIN_OPENS_AS_IT_IS = { has_branch: true, candidate_branches: [], choices: [], chosen: [] } as OpenChoicesData

// Picking a session opens the activation dialog on it, with what leaving the active session and opening this one can
// do now, as their Tickets answer.
export async function pickSession($: EngineInterface, chatBar: ChatBarClient, name: string): Promise<void> {
  try {
    const [leaving, opening] = await Promise.all([
      chatBar.hasSession && !chatBar.isMain ? callTool<LeaveChoicesData>($, 'ticket.leave_choices', { ticket: chatBar.sessionName }) : null,
      name === MAIN_SESSION ? MAIN_OPENS_AS_IT_IS : callTool<OpenChoicesData>($, 'ticket.open_choices', { ticket: name }),
    ])
    await showSwitch($, name, leaving, opening)
  } catch (failure) {
    await showFailure($, `${name} cannot open: ${reasonOf(failure)}`)
  }
}

// Confirming the activation dialog puts the switch in the chat box.
export async function activateSession($: EngineInterface, chatBar: ChatBarClient, sessionName: string): Promise<void> {
  const { leaving, opening } = await currentChatBarView($)
  await cancelSwitch($)
  const current = chatBar.hasSession && !chatBar.isMain ? chatBar.sessionName : ''
  await $.prompt.fill({ text: openCommandOf(sessionName, current, leaving, opening), mode: 'replace' })
}

// A new session is created and opened by the agent, in its own worktree, the way a switch opens one.
export async function createSession($: EngineInterface, chatBar: ChatBarClient, sessionName: string): Promise<void> {
  const current = chatBar.hasSession && !chatBar.isMain ? ` Leave session ${chatBar.sessionName} first, asking me what to do with its work.` : ''
  await $.prompt.fill({ text: `Create session ${sessionName} with ticket.create, then open it in its own worktree with ticket.activate, opening=[worktree].${current} Then move this chat with change_directory to the new worktree.`, mode: 'replace' })
}

// The close dialog offers what the Python Ticket answers closing can do with the session's work.
export async function openClose($: EngineInterface, chatBar: ChatBarClient): Promise<void> {
  try {
    await showClose($, await callTool<LeaveChoicesData>($, 'ticket.close_choices', { ticket: chatBar.sessionName }))
  } catch (failure) {
    await showFailure($, `${chatBar.sessionName} cannot close: ${reasonOf(failure)}`)
  }
}

// Confirming the close dialog puts the close in the chat box; closing returns the chat to main.
export async function closeSession($: EngineInterface, chatBar: ChatBarClient): Promise<void> {
  const { leaving } = await currentChatBarView($)
  await cancelClose($)
  await $.prompt.fill({
    text: `Close session ${chatBar.sessionName} doing: ${listed(leaving)}. If that deletes the worktree or branch this chat works in, first move this chat to the main checkout with change_directory. Then call ticket.close with ticket=${chatBar.sessionName}, leaving=[${leaving.join(', ')}], and move this chat to the main checkout.`,
    mode: 'replace',
  })
}
