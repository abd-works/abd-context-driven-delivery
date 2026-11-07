import type { ColumnData } from '@cdd/space/kanban/board'
import { StageClientGenerated, type StageData } from '@cdd/space/kanban/stage'

import type { BacklogItemClient } from '../backlog-item/backlog-item-client'
import type { TicketClient } from '../ticket/ticket-client'
import type { BoardPage } from './board-page'

const limitFrom = (text: string): number | null => {
  const limit = Number.parseInt(text, 10)
  return limit >= 1 ? limit : null
}

// A column has no generated class, because Python returns it as a shape inside the board; a stage's tools are its own.
export class ColumnClient {
  constructor(
    private readonly data: ColumnData,
    private readonly page: BoardPage,
  ) {}

  get name(): string {
    return this.data.name
  }

  get isStage(): boolean {
    return this.data.work_required !== undefined
  }

  get isBacklog(): boolean {
    return this.data.items !== undefined
  }

  get workRequired(): string[] {
    return this.data.work_required ?? []
  }

  get formats(): Record<string, string[]> {
    return this.data.formats ?? {}
  }

  get defaultFormats(): Record<string, string> {
    return this.data.default_formats ?? {}
  }

  get wipLimit(): number | undefined {
    return this.data.wip_limit
  }

  get isOverLimit(): boolean {
    return this.data.is_over_limit ?? false
  }

  get items(): BacklogItemClient[] {
    return (this.data.items ?? []).map(item => this.page.item(item))
  }

  get inProgress(): TicketClient[] {
    return (this.data.in_progress ?? []).map(ticket => this.page.ticket(ticket))
  }

  get done(): TicketClient[] {
    return (this.data.done ?? []).map(ticket => this.page.ticket(ticket))
  }

  // Only Complete lists its tickets whole: a stage holds them In progress or Done.
  get tickets(): TicketClient[] {
    return (this.data.tickets ?? []).map(ticket => this.page.ticket(ticket))
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
