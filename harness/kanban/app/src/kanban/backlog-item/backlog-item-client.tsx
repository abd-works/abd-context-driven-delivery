import { BacklogItem, type BacklogItemData } from '@cdd/harness/kanban/backlog-item'
import type { TicketData } from '@cdd/harness/kanban/ticket'

import { pathPart } from '../board/board-api'
import type { BoardPage } from '../board/board-page'
import { EMPTY_DRAFT } from '../board/board-store'

const ITEM_COLUMN = 'Backlog'

export class BacklogItemClient extends BacklogItem {
  constructor(
    json: BacklogItemData,
    private readonly page: BoardPage,
  ) {
    super(json)
  }

  get address(): string {
    return `${ITEM_COLUMN}/${this.title}`
  }

  select(): void {
    this.page.board.select(this.address)
  }

  async start(): Promise<void> {
    const ticket = await this.page.api.post<TicketData>(`/backlog/${pathPart(this.title)}/start`)
    await this.page.reader.refresh()
    if (!ticket) return
    this.page.ticket(ticket).select()
    this.page.store.toast(`${this.title} started in Discovery`)
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
    const added = await this.page.api.post<BacklogItemData>('/backlog', { title: title.trim(), text: text.trim() })
    await this.page.reader.refresh()
    if (!added) return
    const item = this.page.item(added)
    item.select()
    this.page.store.toast(`${item.title} added to Backlog`)
  }
}
