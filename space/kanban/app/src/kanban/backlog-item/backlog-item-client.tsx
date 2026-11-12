import { BacklogItemClientGenerated, type BacklogItemData } from '@cdd/space/kanban/backlog-item'
import type { TicketData } from '@cdd/space/kanban/ticket'

import type { BoardPage } from '../board/board-page'
import { EMPTY_DRAFT } from '../shared/board-store'

// Where a backlog item dropped on another lands: just above it, just below it, or inside it as its child.
export type ItemDrop = 'before' | 'after' | 'child'

// How far into a card, as a share of its height from either edge, a drop puts the dragged item above or below it.
const EDGE_SHARE = 0.25

// A backlog item as the page knows it. A tool that answers the item changed, such as editText or moveBefore, has the
// board read again, so the page shows it.
export class BacklogItemClient extends BacklogItemClientGenerated {
  private heldChildren?: BacklogItemClient[]

  constructor(
    json: BacklogItemData,
    private readonly page: BoardPage,
  ) {
    super(page.api, json)
    this.onChanged(() => void page.reader.refresh())
  }

  get address(): string {
    return `${this.column.name}/${this.title}`
  }

  // The items kept in its folder, stacked inside its card. Most items have none, and data read without the field holds
  // none either, so a card shows no stack rather than failing the page.
  get childItems(): BacklogItemClient[] {
    this.heldChildren ??= (this.children ?? []).map(child => this.page.item(child))
    return this.heldChildren
  }

  select(): void {
    this.page.board.select(this.address)
  }

  // Whether it can take dragged as its child: the Backlog nests one level, and never in a folder kept with a ticket's work.
  canTakeAsChild(dragged: BacklogItemClient): boolean {
    const isFolderOfWork = Boolean(this.ticket || dragged.ticket)
    return dragged.title !== this.title && dragged.parent !== this.title && !this.isStacked && !dragged.childItems.length && !isFolderOfWork
  }

  // What dropping dragged at depth (0 at the card's top edge, 1 at its bottom) does: near an edge it goes above or below;
  // in the middle it becomes this item's child, or, where it cannot, goes to the nearer edge.
  dropOf(dragged: BacklogItemClient, depth: number): ItemDrop | undefined {
    if (dragged.title === this.title) return undefined
    if (depth >= EDGE_SHARE && depth <= 1 - EDGE_SHARE && this.canTakeAsChild(dragged)) return 'child'
    return depth < 0.5 ? 'before' : 'after'
  }

  // Takes dragged where drop says. A child placed above or below a card leaves its parent first.
  async take(dragged: BacklogItemClient, drop: ItemDrop): Promise<void> {
    if (drop === 'child') {
      await dragged.nestUnder(this.title)
      this.page.store.toast(`${dragged.title} is now a child of ${this.title}`)
      return
    }
    if (dragged.isStacked) await dragged.leaveParent()
    await (drop === 'before' ? dragged.moveBefore(this.title) : dragged.moveAfter(this.title))
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
