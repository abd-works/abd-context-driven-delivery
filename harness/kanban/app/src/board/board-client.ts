import type { BacklogItem, BoardData, Column, Ticket } from './board'
import { activeTicket, allTickets, ticketAddress, ticketsOf } from './board'
import type { BoardApi } from './board-api'
import type { BoardStore, Region } from './board-store'

const ITEM_COLUMN = 'Backlog'
const POLL_MILLISECONDS = 2000
const MINIMUM_REGION = 160
const ROOM_OVER_REGIONS = 90

export const itemAddress = (item: BacklogItem): string => `${ITEM_COLUMN}/${item.title}`

const standingOf = (ticket: Ticket): string => (ticket.column === 'Complete' ? ticket.column : `${ticket.column} · ${ticket.is_done ? 'Done' : 'In progress'}`)

const itemsOf = (board: BoardData): BacklogItem[] => board.columns.flatMap(column => column.items ?? [])

// A ticket moved back out of Discovery leaves the columns and comes back as a backlog item under its title.
function announceReturns(before: BoardData, after: BoardData): string[] {
  const names = new Set(allTickets(after).map(ticket => ticket.name))
  const earlierItems = itemsOf(before).map(item => item.title)
  const items = itemsOf(after).map(item => item.title)
  return allTickets(before)
    .filter(ticket => !names.has(ticket.name) && items.includes(ticket.title) && !earlierItems.includes(ticket.title))
    .map(ticket => `${ticket.title} moved to Backlog`)
}

function changesOf(was: Ticket, ticket: Ticket): string[] {
  const moved = standingOf(was) === standingOf(ticket) ? [] : [`${ticket.title} moved to ${standingOf(ticket)}`]
  const reviewed = Object.entries(ticket.progress)
    .filter(([slug, state]) => state === 'done' && was.progress[slug] !== 'done')
    .map(([slug]) => `${slug} reviewed on ${ticket.name}`)
  return [...moved, ...reviewed]
}

// What changed between two reads of the board, in the words a toast says. A name held by an open and a closed session
// cannot be compared across reads, so it announces nothing.
export function announcementsOf(before: BoardData | null, after: BoardData): string[] {
  if (!before) return []
  const earlier = new Map(allTickets(before).map(ticket => [ticket.name, ticket]))
  const named = allTickets(after).map(ticket => ticket.name)
  const isUnique = (ticket: Ticket) => named.indexOf(ticket.name) === named.lastIndexOf(ticket.name)
  const changes = allTickets(after).flatMap(ticket => {
    const was = earlier.get(ticket.name)
    return was && isUnique(ticket) ? changesOf(was, ticket) : []
  })
  return [...changes, ...announceReturns(before, after)]
}

// The board as last read, with what a person changes about how it is shown.
export class BoardClient {
  private reads = 0
  private latestApplied = 0
  private isPolling = false

  constructor(
    private readonly store: BoardStore,
    private readonly api: BoardApi,
    private readonly onChanged: () => Promise<void>,
  ) {}

  private get data(): BoardData | null {
    return this.store.state.board
  }

  get project(): string {
    return this.data?.project ?? ''
  }

  get active(): string | null {
    return this.data?.active ?? null
  }

  get columns(): Column[] {
    return this.data?.columns ?? []
  }

  get stages(): Column[] {
    return this.columns.filter(column => column.work_required)
  }

  get tickets(): Ticket[] {
    return this.data ? allTickets(this.data) : []
  }

  get ticketCount(): number {
    return new Set(this.tickets.map(ticket => ticket.name)).size
  }

  get backlogItems(): BacklogItem[] {
    return this.data ? itemsOf(this.data) : []
  }

  get activeTicket(): Ticket | undefined {
    return this.data ? activeTicket(this.data) : undefined
  }

  private get latestTicket(): Ticket | undefined {
    return [...this.tickets].sort((one, other) => other.last_activity.localeCompare(one.last_activity))[0]
  }

  // With nothing pressed, the details show the active ticket, or else the one worked on last.
  get selectedTicket(): Ticket | undefined {
    const { selected } = this.store.state
    if (this.selectedItem) return undefined
    return this.tickets.find(ticket => ticketAddress(ticket) === selected) ?? this.activeTicket ?? this.latestTicket
  }

  get selectedItem(): BacklogItem | undefined {
    return this.backlogItems.find(item => itemAddress(item) === this.store.state.selected)
  }

  countOf(column: Column): number {
    return column.items ? column.items.length : ticketsOf(column).length
  }

  // The stage whose fidelities a ticket shows: Complete keeps showing Implementation's.
  stageOf(ticket: Ticket): Column | undefined {
    return this.stages.find(stage => stage.name === ticket.column) ?? this.stages.at(-1)
  }

  stageNamed(name: string): Column | undefined {
    return this.stages.find(stage => stage.name === name)
  }

  // Reads can overlap with a move's own read, so a slower, older answer never replaces a newer one.
  async refresh(): Promise<void> {
    const order = ++this.reads
    const shown = await this.api.get<BoardData>('/board')
    if (!shown || order < this.latestApplied) return
    this.latestApplied = order
    await this.apply(shown)
  }

  private async apply(shown: BoardData): Promise<void> {
    const before = this.data
    this.store.change({ board: shown, now: Date.now() })
    for (const announcement of announcementsOf(before, shown)) this.store.toast(announcement)
    if (JSON.stringify(before) !== JSON.stringify(shown)) await this.onChanged()
  }

  async refreshPressed(): Promise<void> {
    await this.refresh()
    await this.onChanged()
  }

  startPolling(): () => void {
    const timer = setInterval(() => void this.poll(), POLL_MILLISECONDS)
    void this.poll()
    return () => clearInterval(timer)
  }

  // A read takes longer than the interval while the cdd server starts, so polls never stack up.
  private async poll(): Promise<void> {
    if (this.isPolling) return
    this.isPolling = true
    await this.refresh().finally(() => {
      this.isPolling = false
    })
  }

  select(address: string): void {
    this.store.change({ selected: address })
  }

  toggleRegion(region: Region): void {
    this.store.change(state => ({ expandedRegion: state.expandedRegion === region ? null : region }))
  }

  // Neither the board nor the details can be dragged shut, whatever height the page has.
  setBoardHeight(wanted: number, pageHeight: number): void {
    const largest = Math.max(pageHeight - ROOM_OVER_REGIONS - MINIMUM_REGION, MINIMUM_REGION)
    this.store.change({ boardHeight: Math.min(Math.max(wanted, MINIMUM_REGION), largest) })
  }

  toggleOnlyActive(): void {
    this.store.change(state => ({ onlyActive: !state.onlyActive }))
  }

  toggleHiddenPractices(): void {
    this.store.change(state => ({ hidesDisabled: !state.hidesDisabled }))
  }

  editLimit(stage: string): void {
    this.store.change({ editingLimit: stage })
  }

  cancelLimit(): void {
    this.store.change({ editingLimit: null })
  }

  async submitLimit(stage: string, text: string): Promise<void> {
    this.cancelLimit()
    const limit = Number.parseInt(text, 10)
    if (!(limit >= 1)) return
    await this.api.post('/board/wip-limit', { stage, limit })
    await this.refresh()
  }
}
