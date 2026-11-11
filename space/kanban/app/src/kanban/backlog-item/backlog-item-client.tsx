import { BacklogItemClientGenerated, type BacklogItemData } from '@cdd/space/kanban/backlog-item'
import type { TicketData } from '@cdd/space/kanban/ticket'

import type { BoardPage } from '../board/board-page'
import { EMPTY_DRAFT } from '../shared/board-store'

export class BacklogItemClient extends BacklogItemClientGenerated {
  constructor(
    json: BacklogItemData,
    private readonly page: BoardPage,
  ) {
    super(page.api, json)
  }

  get address(): string {
    return `${this.column.name}/${this.title}`
  }

  select(): void {
    this.page.board.select(this.address)
  }

  // Dropped on a ticket's card, the item starts as that ticket's child, and the board is read again to show it there.
  override async startUnder(parent: string): Promise<TicketData | null> {
    const child = await super.startUnder(parent)
    await this.page.reader.refresh()
    if (child) this.page.store.toast(`${this.title} started as a child of ${parent}`)
    return child
  }

  override async start(scope?: string, path?: string): Promise<TicketData | null> {
    const ticket = await super.start(scope, path)
    await this.page.reader.refresh()
    if (!ticket) return null
    this.page.ticket(ticket).select()
    this.page.store.toast(`${this.title} started in Discovery`)
    return ticket
  }
}

// The form under the Backlog heading that writes a new item.
export class BacklogDraftClient {
  constructor(private readonly page: BoardPage) {}

  open(): void {
    this.page.store.change(state => ({ draft: { ...state.draft, isOpen: true } }))
  }

  cancel(): void {
    this.page.store.change({ draft: EMPTY_DRAFT })
  }

  type(field: 'title' | 'text', typed: string): void {
    this.page.store.change(state => ({ draft: { ...state.draft, [field]: typed } }))
  }

  async add(): Promise<void> {
    const { title, text } = this.page.store.state.draft
    if (!title.trim()) return
    this.cancel()
    const added = await BacklogItemClientGenerated.create(this.page.api, title.trim(), text.trim())
    await this.page.reader.refresh()
    if (!added) return
    const item = this.page.item(added)
    item.select()
    this.page.store.toast(`${item.title} added to Backlog`)
  }
}
