import type { BoardPage } from '../board/board-page'
import type { TicketClient } from './ticket-client'

// Opening a ticket's chat from its card: a new chat in the Claude app on the ticket's worktree, which activating opens
// first when the ticket has none.
export class TicketChatOpening {
  constructor(
    private readonly ticket: TicketClient,
    private readonly page: BoardPage,
  ) {}

  get canOpen(): boolean {
    return !this.ticket.isClosed && !this.ticket.chat.found
  }

  // A ticket in Complete has closed its work, so it gets no new branch, worktree, or chat.
  async open(): Promise<void> {
    const chat = this.ticket.chat
    if (!this.canOpen || !chat.beginOpening()) return
    await chat.start(await this.worktreeOpened(), this.ticket.prompts.new_chat)
  }

  // The ticket's worktree, opened by activating when the ticket has none.
  private async worktreeOpened(): Promise<string> {
    if (this.ticket.worktree) return this.ticket.worktree
    const opened = await this.ticket.activate()
    await this.page.reader.refresh()
    return opened?.worktree ?? ''
  }
}
