import type { EngineInterface } from 'claude-code'

import type { ChatData } from '@cdd/harness/chat/chat'
import type { TicketData } from '@cdd/space/kanban/ticket'

import { reasonOf, showFailure } from '../error-display/failure-client'
import { linkNotOpened } from '../shared/system-link'
import { callTool } from './chat-bar-client'

// A ticket's work happens in a chat of its own, in the ticket's worktree: the server decides which ticket a chat works
// on from the folder it is in. Opening a ticket from the main chat never moves the main chat; it finds the ticket's chat
// or starts a new one in the worktree.

// The name a person reads for the chat working on a ticket, as chat.list names it; its id when the list names none.
async function nameOfChat($: EngineInterface, id: string): Promise<string> {
  const chats = await callTool<ChatData[]>($, 'chat.list', {})
  return chats.find(chat => chat.id === id)?.name || id
}

// Where a ticket that ticket.activate opened is worked on: its chat when one is open, else a new chat in its worktree.
// The desktop app offers no /cd; the chat bar hands the ticket's new_chat_link to the app, which opens a new chat on the
// worktree with its prompt typed in, and the person sends it. No agent turn runs in this chat, and the app takes the
// person's send even while Remote Control is on. A terminal or IDE chat is opened by the person, so the chat bar names
// the folder to open it in.
export async function startedChatIn($: EngineInterface, ticket: TicketData): Promise<void> {
  if (ticket.working_chat) {
    $.ui.toast(`${ticket.name} is already open in the chat ${await nameOfChat($, ticket.working_chat.id).catch(failure => `${ticket.working_chat?.id} (chat.list failed: ${reasonOf(failure)})`)}`)
    return
  }
  if (!ticket.worktree) {
    await showFailure($, `${ticket.name} opened with no worktree, so there is no folder to start its chat in`, `Starting the chat of ${ticket.name} after ticket.activate`)
    return
  }
  const isDesktopApp = !(await $.command.list()).some(command => command.name === 'cd')
  if (!isDesktopApp) {
    $.ui.toast(`${ticket.name} is open in ${ticket.worktree}: open a chat in that folder to work on it`)
    return
  }
  const notOpened = await linkNotOpened($, ticket.new_chat_link)
  if (notOpened) {
    await showFailure($, `No chat opened for ${ticket.name}: the system did not hand the link to the Claude app (${notOpened}). Open a chat in ${ticket.worktree} to work on it`, `Starting the chat of ${ticket.name}, opening its new chat link ${ticket.new_chat_link}`)
    return
  }
  $.ui.toast(`Send the new chat's prompt in the Claude app to start the chat of ${ticket.name}`)
}
