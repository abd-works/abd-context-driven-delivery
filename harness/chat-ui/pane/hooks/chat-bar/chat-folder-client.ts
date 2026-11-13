import type { EngineInterface } from 'claude-code'

import type { ChatData } from '@cdd/harness/chat/chat'
import type { TicketData } from '@cdd/space/kanban/ticket'

import { reasonOf } from '../shared/failure'
import { callTool, showFailure } from './chat-bar-client'

// A ticket's work happens in a chat of its own, in the ticket's worktree: the server decides which ticket a chat works
// on from the folder it is in. Opening a ticket from the main chat never moves the main chat; it finds the ticket's chat
// or starts a new one in the worktree.

// The name a person reads for the chat working on a ticket, as chat.list names it; its id when the list names none.
async function nameOfChat($: EngineInterface, id: string): Promise<string> {
  const chats = await callTool<ChatData[]>($, 'chat.list', {})
  return chats.find(chat => chat.id === id)?.name || id
}

// The desktop app rewrites a Windows path to backslashes before its tools run, and auto mode refuses a call whose input
// changed after it was reviewed; asking in the spelling the app uses leaves nothing to rewrite.
const DRIVE_PATH = /^[A-Za-z]:\//
const inWindowsSpelling = (folder: string): string => (DRIVE_PATH.test(folder) ? folder.split('/').join('\\') : folder)

// The desktop app starts a new chat only through its start_session tool, which only the agent can call, so the agent is
// asked to start one in the ticket's worktree and to do nothing else. While Remote Control is on for the main chat, the
// app refuses to start a chat from a message it did not see the person type, and the chat bar cannot see Remote Control,
// so the agent is told what to say when that happens. The new chat's first step is sessions.switch to the
// ticket's session, so its chat bar, its log and every tool it calls work on the ticket from its first turn, not on main.
async function askAgentToStartChat($: EngineInterface, ticket: TicketData): Promise<void> {
  const folder = inWindowsSpelling(ticket.worktree)
  const text = [
    `Start a new chat for ticket ${ticket.name} in its worktree ${folder}: call the start_session tool with initiation "user_asked", context "fresh", cwd "${folder}", use_worktree false and title "${ticket.name}",`,
    `with a prompt saying it works on ticket ${ticket.name} (${ticket.title}), that its first step is to call sessions.switch with name ${ticket.name} before anything else, and that it should then read the session's latest handoff,`,
    'and a background saying the chat bar opened this ticket from the main chat.',
    'If start_session refuses because the user is working over Remote Control, say in one line that Remote Control is on for this chat,',
    'so the app will not start a chat from a request the chat bar typed: turn it off with the Remote Control switch, or type "start it" and the chat starts.',
    'Do nothing else, and stay in this chat.',
  ].join(' ')
  const answer = await $.prompt.submit({ text, asUser: true })
  if (answer.drop !== undefined) throw new Error(answer.drop || 'the chat did not take the request')
}

// Where a ticket that ticket.activate opened is worked on: its chat when one is open, else a new chat in its worktree.
// The desktop app offers no /cd and starts the chat through the agent; a terminal or IDE chat is opened by the person,
// so the chat bar names the folder to open it in.
export async function startedChatIn($: EngineInterface, ticket: TicketData): Promise<void> {
  if (ticket.working_chat) {
    $.ui.toast(`${ticket.name} is already open in the chat ${await nameOfChat($, ticket.working_chat.id).catch(failure => `${ticket.working_chat?.id} (chat.list failed: ${reasonOf(failure)})`)}`)
    return
  }
  if (!ticket.worktree) {
    await showFailure($, `${ticket.name} opened with no worktree, so there is no folder to start its chat in`)
    return
  }
  const isDesktopApp = !(await $.command.list()).some(command => command.name === 'cd')
  if (!isDesktopApp) {
    $.ui.toast(`${ticket.name} is open in ${ticket.worktree}: open a chat in that folder to work on it`)
    return
  }
  try {
    await askAgentToStartChat($, ticket)
    $.ui.toast(`Starting a chat for ${ticket.name} in ${ticket.worktree}`)
  } catch (failure) {
    await showFailure($, `No chat started for ${ticket.name}: ${reasonOf(failure)}. Open a chat in ${ticket.worktree} to work on it`)
  }
}
