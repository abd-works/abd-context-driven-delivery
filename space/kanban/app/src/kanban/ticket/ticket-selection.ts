import type { BoardPage } from '../board/board-page'
import type { TicketClient } from './ticket-client'

// A ticket chosen on the page: it opens in the details, and the chat at the top of the board is its chat.
export class TicketSelection {
  constructor(
    private readonly ticket: TicketClient,
    private readonly page: BoardPage,
  ) {}

  select(): void {
    this.page.store.change({ selected: this.ticket.address })
  }

  // A person clicking the ticket: it opens in the details, and the chat at the top of the board is its chat, the one
  // working in its worktree; with none open, main's chat when main has one; else no chat, so the top never shows another
  // ticket's chat. A press only selects: opening a worktree and a chat is the card's own button.
  choose(): void {
    this.select()
    const chat = this.ticket.chat.found ?? this.page.board.mainTicket?.chat.found
    this.page.chat.choose(chat?.id ?? '')
  }
}
