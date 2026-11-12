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

type TicketList = 'in_progress' | 'done' | 'tickets'
const LISTS: TicketList[] = ['in_progress', 'done', 'tickets']

// Every ticket the board sends: the cards of each column, and the children inside their parents' cards.
function everyTicket(board: BoardData): TicketData[] {
  const within = (tickets: TicketData[]): TicketData[] => tickets.flatMap(ticket => [ticket, ...within(ticket.children)])
  return within(board.columns.flatMap(column => LISTS.flatMap(list => column[list] ?? [])))
}

const ticketNamed = (board: BoardData, name: string): TicketData | undefined => everyTicket(board).find(ticket => ticket.name === name)

// The board with every ticket in every list, and every child inside its parent, given by changed.
function withTickets(board: BoardData, changed: (tickets: TicketData[]) => TicketData[]): BoardData {
  const inside = (tickets: TicketData[]): TicketData[] => changed(tickets).map(ticket => ({ ...ticket, children: inside(ticket.children) }))
  return withColumns(board, column => Object.fromEntries(Object.entries(column).map(([key, value]) => [key, LISTS.includes(key as TicketList) && Array.isArray(value) ? inside(value as TicketData[]) : value])) as ColumnData)
}

// The board with the ticket taken off wherever it shows: a card in its column, or a row in its parent's card.
const withoutTicket = (board: BoardData, name: string): BoardData => withTickets(board, tickets => tickets.filter(ticket => ticket.name !== name))

// The board with the ticket as a card of its own in its column: In progress or Done on a stage, its list in Complete.
function withCard(board: BoardData, card: TicketData): BoardData {
  const list: TicketList = board.columns.find(column => column.name === card.column.name)?.kind === 'stage' ? (card.is_done ? 'done' : 'in_progress') : 'tickets'
  return withColumns(board, column => (column.name === card.column.name ? { ...column, [list]: [...(column[list] ?? []), card] } : column))
}

// The board with child shown in parent's card, as a row there.
const withChild = (board: BoardData, parent: string, child: TicketData): BoardData =>
  withTickets(board, tickets => tickets.map(ticket => (ticket.name === parent ? { ...ticket, children: [...ticket.children.filter(row => row.name !== child.name), child] } : ticket)))

// A ticket given a parent, which stacks it in the parent's card unless the parent is closed; or given none, which makes it
// a card of its own in its column. Python says what a stacked child is (Ticket.is_stacked); the page only draws it early.
export class TicketNewParent implements PendingChange {
  constructor(
    private readonly ticket: string,
    private readonly parent: string | null,
  ) {}

  appliedTo(board: BoardData): BoardData {
    const moved = ticketNamed(board, this.ticket)
    if (!moved) return board
    const cleared = withoutTicket(board, this.ticket)
    if (this.parent === null) return withCard(cleared, { ...moved, is_stacked: false, is_pulled_out: false })
    const parent = ticketNamed(board, this.parent)
    if (!parent) return board
    const child = { ...moved, is_stacked: !parent.is_closed, is_pulled_out: false }
    const shown = withChild(cleared, this.parent, child)
    return parent.is_closed ? withCard(shown, child) : shown
  }

  isShownIn(board: BoardData): boolean {
    const holding = everyTicket(board).filter(ticket => ticket.children.some(child => child.name === this.ticket))
    return this.parent === null ? holding.length === 0 : holding.some(ticket => ticket.name === this.parent)
  }
}

// A child pulled out of its parent's card: a card of its own in its column, still a row in its parent's card.
export class TicketPulledOut implements PendingChange {
  constructor(private readonly ticket: string) {}

  appliedTo(board: BoardData): BoardData {
    const child = ticketNamed(board, this.ticket)
    if (!child || child.is_pulled_out) return board
    const pulled = { ...child, is_pulled_out: true, is_stacked: false }
    const kept = withTickets(board, tickets => tickets.map(ticket => (ticket.name === this.ticket ? pulled : ticket)))
    return withCard(kept, pulled)
  }

  isShownIn(board: BoardData): boolean {
    return ticketNamed(board, this.ticket)?.is_pulled_out ?? true
  }
}
