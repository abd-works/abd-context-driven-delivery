import type { BoardPage } from '../board/board-page'
import type { TicketClient } from './ticket-client'

// Where a dragged ticket can be dropped, as Python names it, and what a drop on the Backlog or Complete does to it.
export class TicketDrops {
  constructor(
    private readonly ticket: TicketClient,
    private readonly page: BoardPage,
  ) {}

  // Python says which columns besides the stages take the ticket: the Backlog always, Complete only as it allows.
  canDropOn(edge: string): boolean {
    return this.ticket.dropTargets.includes(edge)
  }

  // Complete closes it: an open ticket through its Close dialog, which asks what to do with its work, and one not opened,
  // which has no worktree or chat to wind up, at once.
  async dropOn(edge: string): Promise<void> {
    if (this.page.board.columnNamed(edge)?.isBacklog) await this.ticket.moveTo(edge, false)
    else if (this.ticket.isOpen) await this.page.activation.startClosing(this.ticket)
    else await this.ticket.close()
  }

  // Python names the tickets another can be dropped on to become their child.
  canTakeAsChild(other: TicketClient): boolean {
    return other.parentChoices.includes(this.ticket.name)
  }
}
