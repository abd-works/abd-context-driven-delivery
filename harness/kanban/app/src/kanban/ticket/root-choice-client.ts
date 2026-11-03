import type { BacklogItemClient } from '../backlog-item/backlog-item-client'
import type { BoardPage } from '../board/board-page'
import type { RootChoice } from '../board/board-store'
import type { TicketClient } from './ticket-client'

// Browsing for the ticket's own root rather than one practice's.
export const TICKET_ROOT = 'ticket'

const parentOf = (path: string): string => path.split('/').slice(0, -1).join('/')

// The roots dialog: where a ticket's session works, and where each practice writes under it. Every choice goes to the
// ticket's tools, and the dialog reads the roots back from the board.
export class RootChoiceClient {
  constructor(private readonly page: BoardPage) {}

  private get choice(): RootChoice | null {
    return this.page.store.state.rootChoice
  }

  private change(changed: Partial<RootChoice>): void {
    this.page.store.change(state => ({ rootChoice: state.rootChoice ? { ...state.rootChoice, ...changed } : null }))
  }

  get ticket(): TicketClient | undefined {
    const name = this.choice?.ticket
    return name ? this.page.board.tickets.find(ticket => ticket.name === name) : undefined
  }

  openFor(ticket: TicketClient): void {
    this.page.store.change({ rootChoice: { ticket: ticket.name, startingItem: null, browsing: null } })
  }

  // An item starts once a person has chosen the folder its session works in.
  async openToStart(item: BacklogItemClient): Promise<void> {
    this.page.store.change({ rootChoice: { ticket: '', startingItem: item.toJSON(), browsing: null } })
    await this.browse(TICKET_ROOT, '')
  }

  async browse(target: string, path: string): Promise<void> {
    const folders = await this.page.board.folders(path)
    if (folders) this.change({ browsing: { target, path, folders } })
  }

  up(): Promise<void> {
    const browsing = this.choice?.browsing
    return browsing ? this.browse(browsing.target, parentOf(browsing.path)) : Promise.resolve()
  }

  stopBrowsing(): void {
    if (this.choice?.startingItem) return this.close()
    this.change({ browsing: null })
  }

  // The folder being browsed becomes the root of whatever is browsed for.
  async use(): Promise<void> {
    const browsing = this.choice?.browsing
    if (!browsing) return
    if (this.choice?.startingItem) return this.start(browsing.path)
    const ticket = this.ticket
    if (!ticket) return
    if (browsing.target === TICKET_ROOT) await ticket.chooseRoot(browsing.path)
    else await ticket.choosePracticeRoot(browsing.target, browsing.path)
    await this.page.reader.refresh()
    this.change({ browsing: null })
  }

  async useDefault(practice: string): Promise<void> {
    await this.ticket?.useDefaultPracticeRoot(practice)
    await this.page.reader.refresh()
  }

  // Started, the dialog stays open on the new ticket so its practices' roots can be set too.
  private async start(path: string): Promise<void> {
    const item = this.choice?.startingItem
    if (!item) return
    const ticket = await this.page.item(item).start(undefined, path)
    if (ticket) this.page.store.change({ rootChoice: { ticket: ticket.name, startingItem: null, browsing: null } })
  }

  close(): void {
    this.page.store.change({ rootChoice: null })
  }
}
