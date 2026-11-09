import type { ColumnData, FidelityGuidanceData, StageScopeData } from '@cdd/space/kanban/board'
import { StageClientGenerated, type StageData } from '@cdd/space/kanban/stage'
import type { TicketData } from '@cdd/space/kanban/ticket'

import type { BacklogItemClient } from '../backlog-item/backlog-item-client'
import type { TicketClient } from '../ticket/ticket-client'
import type { BoardPage } from './board-page'

const limitFrom = (text: string): number | null => {
  const limit = Number.parseInt(text, 10)
  return limit >= 1 ? limit : null
}

// A column has no generated class, because Python returns it as a shape inside the board; a stage's tools are its own.
// Its cards are made once, at the first ask, since its board is made once per read.
export class ColumnClient {
  private heldItems: BacklogItemClient[] | null = null
  private heldInProgress: TicketClient[] | null = null
  private heldDone: TicketClient[] | null = null
  private heldTickets: TicketClient[] | null = null

  constructor(
    private readonly data: ColumnData,
    private readonly page: BoardPage,
  ) {}

  get name(): string {
    return this.data.name
  }

  // The column says its own kind: backlog, stage, or complete.
  get isStage(): boolean {
    return this.data.kind === 'stage'
  }

  get isBacklog(): boolean {
    return this.data.kind === 'backlog'
  }

  // How much of the solution a stage's work covers; none on the Backlog and Complete.
  get scope(): StageScopeData | undefined {
    return this.data.scope
  }

  // The actions an action bar offers with formats: those that write a fidelity's files.
  get producingActions(): string[] {
    return this.data.producing_actions ?? []
  }

  // The actions whose command takes the formats the bar's chips pick: generate and render.
  get actionsWithFormats(): string[] {
    return this.data.actions_with_formats ?? []
  }

  // Each fidelity the stage requires, with the formats it writes and its default one.
  get workRequired(): FidelityGuidanceData[] {
    return this.data.work_required ?? []
  }

  get wipLimit(): number | undefined {
    return this.data.wip_limit
  }

  get isOverLimit(): boolean {
    return this.data.is_over_limit ?? false
  }

  get items(): BacklogItemClient[] {
    this.heldItems ??= (this.data.items ?? []).map(item => this.page.item(item))
    return this.heldItems
  }

  get inProgress(): TicketClient[] {
    this.heldInProgress ??= this.ticketsOf(this.data.in_progress)
    return this.heldInProgress
  }

  get done(): TicketClient[] {
    this.heldDone ??= this.ticketsOf(this.data.done)
    return this.heldDone
  }

  // Only Complete lists its tickets whole: a stage holds them In progress or Done.
  get tickets(): TicketClient[] {
    this.heldTickets ??= this.ticketsOf(this.data.tickets)
    return this.heldTickets
  }

  private ticketsOf(listed: TicketData[] | undefined): TicketClient[] {
    return (listed ?? []).map(ticket => this.page.ticket(ticket))
  }

  get everyTicket(): TicketClient[] {
    return [...this.inProgress, ...this.done, ...this.tickets]
  }

  get count(): number {
    return this.isBacklog ? this.items.length : this.everyTicket.length
  }

  // A stage's column holds every field of its stage, so its tools act on the stage the column shows.
  private get stage(): StageClientGenerated {
    return new StageClientGenerated(this.page.api, this.data as StageData)
  }

  // What a person typed becomes a limit only when it is a whole number of at least one.
  async submitWipLimit(text: string): Promise<void> {
    this.page.layout.cancelLimit()
    const limit = limitFrom(text)
    if (!limit || !this.isStage) return
    await this.stage.setWipLimit(limit)
    await this.page.reader.refresh()
  }
}
