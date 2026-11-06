import { BoardClientGenerated, type BoardData } from '@cdd/harness/kanban/board'

import type { BacklogItemClient } from '../backlog-item/backlog-item-client'
import type { TicketClient } from '../ticket/ticket-client'
import type { BoardPage } from './board-page'
import { ColumnClient } from './column-client'
import { PracticeClient } from './practice-client'

const standingOf = (ticket: TicketClient): string => (ticket.column === 'Complete' ? ticket.column : `${ticket.column} · ${ticket.isDone ? 'Done' : 'In progress'}`)

function changesOf(was: TicketClient, ticket: TicketClient): string[] {
  const moved = standingOf(was) === standingOf(ticket) ? [] : [`${ticket.title} moved to ${standingOf(ticket)}`]
  const done = Object.entries(ticket.progress)
    .filter(([slug, progress]) => progress.state === 'done' && was.progress[slug]?.state !== 'done')
    .map(([slug]) => `${slug} done on ${ticket.name}`)
  return [...moved, ...done]
}

// One read of the board, with what the page works out from it. Each read is a new client, built from the store.
export class BoardClient extends BoardClientGenerated {
  constructor(
    data: BoardData,
    private readonly page: BoardPage,
  ) {
    super(page.api, data)
  }

  get shownPractices(): PracticeClient[] {
    return this.practices.map(practice => new PracticeClient(practice))
  }

  // The practice a fidelity belongs to, found among the fidelities Python lists for each practice.
  practiceOf(slug: string): PracticeClient | undefined {
    return this.shownPractices.find(practice => practice.has(slug))
  }

  practiceNamed(key: string): PracticeClient | undefined {
    return this.shownPractices.find(practice => practice.key === key)
  }

  get shownColumns(): ColumnClient[] {
    return this.columns.map(column => new ColumnClient(column, this.page))
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
    return this.tickets.find(ticket => ticket.name === this.active)
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
    return this.stageNamed(ticket.column) ?? this.stages.at(-1)
  }

  stageNamed(name: string): ColumnClient | undefined {
    return this.stages.find(stage => stage.name === name)
  }

  select(address: string): void {
    this.page.store.change({ selected: address })
  }

  // A ticket moved back out of Discovery leaves the columns and comes back as a backlog item under its title.
  private returnsSince(before: BoardClient): string[] {
    const names = new Set(this.tickets.map(ticket => ticket.name))
    const earlierItems = before.backlogItems.map(item => item.title)
    const items = this.backlogItems.map(item => item.title)
    return before.tickets
      .filter(ticket => !names.has(ticket.name) && items.includes(ticket.title) && !earlierItems.includes(ticket.title))
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
