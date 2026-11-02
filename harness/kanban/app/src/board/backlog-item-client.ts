import type { BacklogItem, Ticket } from './board'
import { ticketAddress } from './board'
import { pathPart } from './board-api'
import { itemAddress } from './board-client'
import type { BoardPage } from './board-page'
import { EMPTY_DRAFT } from './board-store'

export interface BacklogItemClient extends BacklogItem {}

export class BacklogItemClient {
  constructor(
    json: BacklogItem,
    private readonly page: BoardPage,
  ) {
    Object.assign(this, json)
  }

  get address(): string {
    return itemAddress(this)
  }

  select(): void {
    this.page.board.select(this.address)
  }

  async start(): Promise<void> {
    const ticket = await this.page.api.post<Ticket>(`/backlog/${pathPart(this.title)}/start`)
    await this.page.board.refresh()
    if (!ticket) return
    this.page.board.select(ticketAddress(ticket))
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

  type(field: 'title' | 'text', value: string): void {
    this.page.store.change(state => ({ draft: { ...state.draft, [field]: value } }))
  }

  async add(): Promise<void> {
    const { title, text } = this.page.store.state.draft
    if (!title.trim()) return
    this.cancel()
    const item = await this.page.api.post<BacklogItem>('/backlog', { title: title.trim(), text: text.trim() })
    await this.page.board.refresh()
    if (!item) return
    this.page.board.select(itemAddress(item))
    this.page.store.toast(`${item.title} added to Backlog`)
  }
}
