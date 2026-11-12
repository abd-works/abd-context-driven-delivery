import type { BoardData, ColumnData } from '@cdd/space/kanban/board'
import type { TicketData } from '@cdd/space/kanban/ticket'

// A change a person made on the page that the server has not shown in a board read yet: how the board looks with it
// made, and whether a read already shows it.
export interface PendingChange {
  appliedTo(board: BoardData): BoardData
  isShownIn(board: BoardData): boolean
}

// How long a change the server took is laid over the board's reads. The server can put a ticket somewhere other than
// where it was dropped, such as reopening it out of Complete, and then no read shows the change as the page made it.
const KEPT_MILLISECONDS = 30_000

type Held = { change: PendingChange; since: number }

// The changes a person made that the board's reads do not show yet. The page shows a change the moment it is made, and
// lays it over every read until a read shows it: a read that started before the server saved the change would otherwise
// put the card back where it was. A change the server refuses is dropped, and the board shows the latest read without it.
export class PendingChanges {
  private held: Held[] = []

  constructor(private readonly now: () => number = Date.now) {}

  // The read with every change it does not show yet made over it; changes it shows, and changes kept too long, are
  // dropped.
  over(read: BoardData): BoardData {
    const now = this.now()
    this.held = this.held.filter(({ change, since }) => now - since < KEPT_MILLISECONDS && !change.isShownIn(read))
    return this.held.reduce((board, { change }) => change.appliedTo(board), read)
  }

  add(change: PendingChange): void {
    this.held.push({ change, since: this.now() })
  }

  drop(change: PendingChange): void {
    this.held = this.held.filter(held => held.change !== change)
  }
}

// The board with each column's lists of tickets given by changed, every other field as the read has it.
function withColumns(board: BoardData, changed: (column: ColumnData) => ColumnData): BoardData {
  return { ...board, columns: board.columns.map(changed) }
}

const without = (tickets: TicketData[] | undefined, name: string): TicketData[] | undefined => tickets?.filter(ticket => ticket.name !== name)

// The ticket as a card of its own in a stage, In progress or Done; a stacked child, a ticket in Complete, or one not on
// the board is not.
function stagedTicket(board: BoardData, name: string): TicketData | undefined {
  return board.columns.flatMap(column => [...(column.in_progress ?? []), ...(column.done ?? [])]).find(ticket => ticket.name === name)
}

// A ticket dropped on a stage's In progress or Done.
export class TicketMove implements PendingChange {
  constructor(
    private readonly ticket: string,
    private readonly stage: string,
    private readonly isDone: boolean,
  ) {}

  appliedTo(board: BoardData): BoardData {
    const moved = stagedTicket(board, this.ticket)
    const target = board.columns.find(column => column.name === this.stage && column.kind === 'stage')
    if (!moved || !target) return board
    const placed = { ...moved, column: { name: this.stage }, is_done: this.isDone }
    return withColumns(board, column => {
      const kept = { ...column, in_progress: without(column.in_progress, this.ticket), done: without(column.done, this.ticket) }
      if (column !== target) return kept
      return this.isDone ? { ...kept, done: [...(kept.done ?? []), placed] } : { ...kept, in_progress: [...(kept.in_progress ?? []), placed] }
    })
  }

  isShownIn(board: BoardData): boolean {
    const shown = stagedTicket(board, this.ticket)
    return !shown || (shown.column.name === this.stage && shown.is_done === this.isDone)
  }
}

// A card dragged just above another card of the same list in its column.
export class TicketPlacedBefore implements PendingChange {
  constructor(
    private readonly ticket: string,
    private readonly other: string,
  ) {}

  appliedTo(board: BoardData): BoardData {
    return withColumns(board, column => ({ ...column, in_progress: this.placedIn(column.in_progress), done: this.placedIn(column.done) }))
  }

  isShownIn(board: BoardData): boolean {
    const lists = board.columns.flatMap(column => [column.in_progress ?? [], column.done ?? []])
    const holding = lists.find(list => list.some(ticket => ticket.name === this.other))
    if (!holding) return true
    const names = holding.map(ticket => ticket.name)
    return !names.includes(this.ticket) || names.indexOf(this.ticket) === names.indexOf(this.other) - 1
  }

  // Only a list holding both cards changes: a card cannot be put above one in the other list or another column here.
  private placedIn(list: TicketData[] | undefined): TicketData[] | undefined {
    const moved = list?.find(ticket => ticket.name === this.ticket)
    if (!list || !moved || !list.some(ticket => ticket.name === this.other)) return list
    const rest = list.filter(ticket => ticket.name !== this.ticket)
    const at = rest.findIndex(ticket => ticket.name === this.other)
    return [...rest.slice(0, at), moved, ...rest.slice(at)]
  }
}

// A ticket's text, as a person typed it.
export class TicketTextEdit implements PendingChange {
  constructor(
    private readonly ticket: string,
    private readonly text: string,
  ) {}

  appliedTo(board: BoardData): BoardData {
    const edited = (tickets: TicketData[] | undefined) => tickets?.map(ticket => (ticket.name === this.ticket ? { ...ticket, text: this.text } : ticket))
    return withColumns(board, column => ({ ...column, in_progress: edited(column.in_progress), done: edited(column.done), tickets: edited(column.tickets) }))
  }

  isShownIn(board: BoardData): boolean {
    const shown = board.columns.flatMap(column => [...(column.in_progress ?? []), ...(column.done ?? []), ...(column.tickets ?? [])]).find(ticket => ticket.name === this.ticket)
    return !shown || shown.text === this.text
  }
}
