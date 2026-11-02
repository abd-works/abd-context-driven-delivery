import type { BacklogItemData } from '@cdd/harness/kanban/backlog-item'
import type { BoardData } from '@cdd/harness/kanban/board'
import type { ReportRuleData, TicketData, ViolationData } from '@cdd/harness/kanban/ticket'

import { BacklogDraftClient, BacklogItemClient } from '../backlog-item/backlog-item-client'
import { ChatClient } from '../chat/chat-client'
import { ActivationClient } from '../ticket/activation-client'
import { FilesPanelClient } from '../ticket/files-panel-client'
import { OpenCardClient } from '../ticket/open-card-client'
import { locationOf } from '../ticket/report-client'
import { TicketClient } from '../ticket/ticket-client'
import { TileActionsClient } from '../ticket/tile-actions-client'
import { TileClient } from '../ticket/tile-client'
import { BoardApi } from './board-api'
import type { Send } from './board-api'
import { guidanceSlug } from './board-brand'
import { BoardClient } from './board-client'
import { BoardLayoutClient } from './board-layout-client'
import { BoardReader } from './board-reader'
import { BoardStore } from './board-store'
import { SidePanelClient } from './side-panel-client'

const CHAT_POLL_MILLISECONDS = 2000
const NOT_READ_YET: BoardData = { project: '', active: null, columns: [] }

// Everything the page's views act through, wired once.
export class BoardPage {
  readonly store = new BoardStore()
  readonly api: BoardApi
  readonly chat: ChatClient
  readonly panels: SidePanelClient
  readonly files: FilesPanelClient
  readonly layout = new BoardLayoutClient(this.store)
  readonly reader = new BoardReader(this)
  readonly tiles = new TileClient(this)
  readonly tileActions = new TileActionsClient(this)
  readonly cards = new OpenCardClient(this)
  readonly activation = new ActivationClient(this)
  readonly draft = new BacklogDraftClient(this)

  constructor(send?: Send) {
    this.api = new BoardApi(this.store, send)
    this.chat = new ChatClient(this.store, this.api)
    this.panels = new SidePanelClient(this.store, this.api)
    this.files = new FilesPanelClient(this.store, this.api)
  }

  get board(): BoardClient {
    return new BoardClient(this.store.state.board ?? NOT_READ_YET, this)
  }

  async reloadOpen(): Promise<void> {
    await Promise.all([this.tiles.reload(), this.panels.reload(), this.files.reload()])
  }

  ticket(json: TicketData): TicketClient {
    return new TicketClient(json, this)
  }

  item(json: BacklogItemData): BacklogItemClient {
    return new BacklogItemClient(json, this)
  }

  // location names the file and its line.
  fixViolation(rule: ReportRuleData, violation: ViolationData): Promise<void> {
    return this.chat.command(`/actions-satisfy ${guidanceSlug(rule.fidelity)} ${locationOf(violation)} rule ${rule.name}`)
  }

  fixRule(rule: ReportRuleData): Promise<void> {
    return this.chat.command(`/actions-satisfy ${guidanceSlug(rule.fidelity)} rule ${rule.name}`)
  }

  openNewTicket(): Promise<void> {
    return this.chat.fill('Open a new ticket with ticket.new, titled: ')
  }

  start(): () => void {
    const stopBoard = this.reader.startPolling()
    const chatTimer = setInterval(() => void this.chat.refresh(), CHAT_POLL_MILLISECONDS)
    void this.chat.refresh()
    return () => {
      stopBoard()
      clearInterval(chatTimer)
    }
  }
}
