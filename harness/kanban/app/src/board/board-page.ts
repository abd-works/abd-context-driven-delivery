import type { BacklogItem, ReportRule, Ticket, Violation } from './board'
import { guidanceSlug } from './board'
import { ActivationClient } from './activation-client'
import { BacklogDraftClient, BacklogItemClient } from './backlog-item-client'
import { BoardApi } from './board-api'
import type { Send } from './board-api'
import { BoardClient } from './board-client'
import { BoardStore } from './board-store'
import { ChatClient } from '../chat/chat-client'
import { SidePanelClient } from './side-panel-client'
import { TicketClient } from './ticket-client'
import { TileClient } from './tile-client'

const CHAT_POLL_MILLISECONDS = 2000

export const locationOf = (violation: Violation): string => (violation.line ? `${violation.location}:${violation.line}` : violation.location)

// Everything the page's views act through, wired once.
export class BoardPage {
  readonly store = new BoardStore()
  readonly api: BoardApi
  readonly chat: ChatClient
  readonly panels: SidePanelClient
  readonly board: BoardClient
  readonly tiles: TileClient
  readonly activation = new ActivationClient(this)
  readonly draft = new BacklogDraftClient(this)

  constructor(send?: Send) {
    this.api = new BoardApi(this.store, send)
    this.chat = new ChatClient(this.store, this.api)
    this.panels = new SidePanelClient(this.store, this.api)
    this.board = new BoardClient(this.store, this.api, () => this.reloadOpen())
    this.tiles = new TileClient(this.store, this.api, this.chat, this.board)
  }

  private async reloadOpen(): Promise<void> {
    await Promise.all([this.tiles.reload(), this.panels.reload()])
  }

  ticket(json: Ticket): TicketClient {
    return new TicketClient(json, this)
  }

  item(json: BacklogItem): BacklogItemClient {
    return new BacklogItemClient(json, this)
  }

  // location names the file and its line.
  fixViolation(rule: ReportRule, violation: Violation): Promise<void> {
    return this.chat.command(`/actions-satisfy ${guidanceSlug(rule.fidelity)} ${locationOf(violation)} rule ${rule.name}`)
  }

  fixRule(rule: ReportRule): Promise<void> {
    return this.chat.command(`/actions-satisfy ${guidanceSlug(rule.fidelity)} rule ${rule.name}`)
  }

  openNewTicket(): Promise<void> {
    return this.chat.fill('Open a new ticket with ticket.new, titled: ')
  }

  start(): () => void {
    const stopBoard = this.board.startPolling()
    const chatTimer = setInterval(() => void this.chat.refresh(), CHAT_POLL_MILLISECONDS)
    void this.chat.refresh()
    return () => {
      stopBoard()
      clearInterval(chatTimer)
    }
  }
}
