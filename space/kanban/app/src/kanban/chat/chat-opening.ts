import { ChatClientGenerated } from '@cdd/harness/chat/chat'

import type { BoardApi } from '../board/board-api'
import type { BoardStore } from '../shared/board-store'

// A ticket's new chat is not opened again for this long, while the person confirms it and it checks in.
const STARTING_CHAT_MILLISECONDS = 120_000

// The prompt a ticket's new chat opens with. The Claude app gives a new chat no title, so the prompt asks for the ticket's.
const newChatPrompt = (ticket: string): string => `Title this session "${ticket}". You are the chat of the session board's ticket ${ticket}; work on that ticket. First call sessions.switch with name ${ticket}, so every tool works on its session, then read the session's latest handoff.`

// The tickets whose chats are on their way: opening a ticket's worktree and then its chat in the Claude app takes a
// while, so the click shows at once that the chat is coming, and until it checks in, clicking the ticket again opens no
// second one.
export class ChatOpening {
  constructor(
    private readonly store: BoardStore,
    private readonly api: BoardApi,
  ) {}

  begin(ticket: string): boolean {
    if (this.isOpeningFor(ticket)) return false
    this.store.change({ startingChats: { ...this.store.state.startingChats, [ticket]: Date.now() } })
    this.store.toast(`Opening the chat of ${ticket}…`)
    return true
  }

  // Until the ticket's chat checks in, which the ticket then names, it is on its way.
  isOpeningFor(ticket: string): boolean {
    const asked = this.store.state.startingChats[ticket]
    return asked !== undefined && Date.now() - asked < STARTING_CHAT_MILLISECONDS
  }

  // A ticket's new chat opens in the Claude app on the ticket's worktree, through Python's chat.open; the app asks the
  // person to confirm the folder and send. With no worktree there is nothing to open it on, and it is no longer coming.
  async startFor(ticket: string, worktree: string): Promise<void> {
    if (!worktree) {
      const { [ticket]: _given, ...starting } = this.store.state.startingChats
      this.store.change({ startingChats: starting })
      return
    }
    if (await ChatClientGenerated.open(this.api, worktree, newChatPrompt(ticket))) this.store.toast(`Confirm the folder and send in the Claude app to start the chat of ${ticket}`)
  }
}

// The chat a person has just assigned to each ticket, until a board read names it as the ticket's chat. A read can take
// longer than the person waits before pressing the ticket, and one started before the assignment still names the chat
// from before it, so until a read catches up the assignment is the ticket's chat.
export class ChatAssignments {
  private readonly assigning = new Map<string, string>()

  assign(ticket: string, chat: string): void {
    if (chat) this.assigning.set(ticket, chat)
    else this.assigning.delete(ticket)
  }

  // The id of ticket's chat: the one just assigned while board reads still name another, else the one the read names.
  chatOf(ticket: string, read: string): string {
    const assigned = this.assigning.get(ticket)
    if (assigned === undefined) return read
    if (assigned === read) this.assigning.delete(ticket)
    return assigned
  }
}
