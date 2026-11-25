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

  // A card of its own can be put above any other card of its own: in its column, in any stage, and in Complete where
  // Python lets it be dropped there.
  canDropAbove(target: TicketClient): boolean {
    if (this.ticket.isStacked || target.isStacked || target.name === this.ticket.name) return false
    const column = target.column.name
    if (column === this.ticket.column.name) return true
    return this.page.board.columnNamed(column)?.isStage ? true : this.canDropOn(column)
  }

  // Python moves it into target's column and list and puts it above target. An open ticket put above a closed one
  // closes through its Close dialog first, as a drop on Complete does, and is put above target once it has closed.
  async dropAbove(target: TicketClient): Promise<void> {
    if (target.isClosed && !this.ticket.isClosed && this.ticket.isOpen) await this.page.activation.startClosing(this.ticket, target.name)
    else await this.ticket.moveBefore(target.name)
  }

  // Python names the tickets another can be dropped on to become their child.
  canTakeAsChild(other: TicketClient): boolean {
    return other.parentChoices.includes(this.ticket.name)
  }
}
