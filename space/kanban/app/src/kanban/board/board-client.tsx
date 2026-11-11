import { BoardClientGenerated, type BoardData, type BoardFidelityData } from '@cdd/space/kanban/board'

import type { BacklogItemClient } from '../backlog-item/backlog-item-client'
import type { TicketClient } from '../ticket/ticket-client'
import type { BoardPage } from './board-page'
import { ColumnClient } from './column-client'
import { PracticeClient } from './practice-client'

const standingOf = ({ column, isClosed, isDone }: TicketClient): string => (isClosed ? column.name : `${column.name} · ${isDone ? 'Done' : 'In progress'}`)

function changesOf(was: TicketClient, ticket: TicketClient): string[] {
  const moved = standingOf(was) === standingOf(ticket) ? [] : [`${ticket.title} moved to ${standingOf(ticket)}`]
  const done = ticket.progress
    .filter(progress => progress.state === 'done' && was.progressNamed(progress.fidelity.slug)?.state !== 'done')
    .map(progress => `${progress.fidelity.slug} done on ${ticket.name}`)
  return [...moved, ...done]
}

// One read of the board, with what the page works out from it. Each read is a new client, built from the store, and
// it makes its practices and columns once, at the first ask, since the views ask for them many times in one render.
export class BoardClient extends BoardClientGenerated {
  private heldPractices: PracticeClient[] | null = null
  private heldColumns: ColumnClient[] | null = null

  constructor(
    readonly read: BoardData,
    private readonly page: BoardPage,
  ) {
    super(page.api, read)
  }

  get shownPractices(): PracticeClient[] {
    this.heldPractices ??= this.practices.map(practice => new PracticeClient(practice, this.fidelities.filter(shown => shown.practice.key === practice.key)))
    return this.heldPractices
  }

  // Set once for the repository: Python keeps it in the board's file, and the board is read again to show it.
  override async setSendsFixesDirectly(sends: boolean): Promise<this | null> {
    const saved = await super.setSendsFixesDirectly(sends)
    await this.page.reader.refresh()
    return saved
  }

  practiceNamed(key: string): PracticeClient | undefined {
    return this.shownPractices.find(practice => practice.key === key)
  }

  // A fidelity as its tile names it: its practice, its label, and its skill's slash command, as Python sends it.
  fidelityShown(slug: string): BoardFidelityData | undefined {
    return this.fidelities.find(shown => shown.fidelity.slug === slug)
  }

  get shownColumns(): ColumnClient[] {
    this.heldColumns ??= this.columns.map(column => new ColumnClient(column, this.page))
    return this.heldColumns
  }

  get stages(): ColumnClient[] {
    return this.shownColumns.filter(column => column.isStage)
  }

  get tickets(): TicketClient[] {
    return this.shownColumns.flatMap(column => column.everyTicket)
  }

  get ticketCount(): number {
    return new Set(this.tickets.map(ticket => ticket.name)).size
  }

  get backlogItems(): BacklogItemClient[] {
    return this.shownColumns.flatMap(column => column.items)
  }

  get activeTicket(): TicketClient | undefined {
    return this.tickets.find(ticket => ticket.isActive)
  }

  private get latestTicket(): TicketClient | undefined {
    return [...this.tickets].sort((one, other) => other.lastActivity.localeCompare(one.lastActivity))[0]
  }

  // With nothing pressed, the details show the active ticket, or else the one worked on last.
  get selectedTicket(): TicketClient | undefined {
    if (this.selectedItem) return undefined
    return this.tickets.find(ticket => ticket.address === this.page.store.state.selected) ?? this.activeTicket ?? this.latestTicket
  }

  get selectedItem(): BacklogItemClient | undefined {
    return this.backlogItems.find(item => item.address === this.page.store.state.selected)
  }

  // The stage whose fidelities a ticket shows: Complete keeps showing Implementation's.
  stageOf(ticket: TicketClient): ColumnClient | undefined {
    return this.stageNamed(ticket.column.name) ?? this.stages.at(-1)
  }

  columnNamed(name: string): ColumnClient | undefined {
    return this.shownColumns.find(column => column.name === name)
  }

  // A card in one of the two columns at the board's right edge opens leftwards, so it stays on the page.
  opensLeft(ticket: TicketClient): boolean {
    const columns = this.shownColumns
    return columns.findIndex(column => column.name === ticket.column.name) >= columns.length - 2
  }

  stageNamed(name: string): ColumnClient | undefined {
    return this.stages.find(stage => stage.name === name)
  }

  select(address: string): void {
    this.page.store.change({ selected: address })
  }

  // A ticket moved back into the Backlog leaves the columns and comes back as the backlog item that, Python says, holds it.
  private returnsSince(before: BoardClient): string[] {
    const names = new Set(this.tickets.map(ticket => ticket.name))
    const earlierHeld = before.backlogItems.map(item => item.ticket)
    const held = this.backlogItems.map(item => item.ticket)
    return before.tickets
      .filter(ticket => !names.has(ticket.name) && held.includes(ticket.name) && !earlierHeld.includes(ticket.name))
      .map(ticket => `${ticket.title} moved to Backlog`)
  }

  // What changed since an earlier read, in the words a toast says. A name held by an open and a closed session cannot
  // be compared across reads, so it announces nothing.
  announcementsSince(before: BoardClient): string[] {
    const earlier = new Map(before.tickets.map(ticket => [ticket.name, ticket]))
    const named = this.tickets.map(ticket => ticket.name)
    const isUnique = (ticket: TicketClient) => named.indexOf(ticket.name) === named.lastIndexOf(ticket.name)
    const changes = this.tickets.flatMap(ticket => {
      const was = earlier.get(ticket.name)
      return was && isUnique(ticket) ? changesOf(was, ticket) : []
    })
    return [...changes, ...this.returnsSince(before)]
  }
}
