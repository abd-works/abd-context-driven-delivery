import type { BacklogItemData } from '@cdd/harness/kanban/backlog-item'
import type { BoardData } from '@cdd/harness/kanban/board'
import type { ReportRuleData, TicketData, ViolationData } from '@cdd/harness/kanban/ticket'

import { BacklogDraftClient, BacklogItemClient } from '../backlog-item/backlog-item-client'
import { ChatClient } from '../chat/chat-client'
import { ActivationClient } from '../ticket/activation-client'
import { FilesPanelClient } from '../ticket/files-panel-client'
import { OpenCardClient } from '../ticket/open-card-client'
import { fixReportPrompt, fixRulePrompt, fixViolationPrompt } from '../ticket/report-client'
import { RootChoiceClient } from '../ticket/root-choice-client'
import { TicketClient } from '../ticket/ticket-client'
import { TileActionsClient } from '../ticket/tile-actions-client'
import { TileClient } from '../ticket/tile-client'
import { BoardApi } from './board-api'
import type { Send } from './board-api'
import { BoardClient } from './board-client'
import { BoardLayoutClient } from './board-layout-client'
import { BoardReader } from './board-reader'
import { BoardStore } from './board-store'
import { BuildClient } from './build-client'
import { SidePanelClient } from './side-panel-client'

const CHAT_POLL_MILLISECONDS = 2000
const CDD_RESTART_PATH = '/cdd/restart'
const NOT_READ_YET: BoardData = { project: '', active: null, columns: [] }

// Everything the page's views act through, wired once.
export class BoardPage {
  readonly store = new BoardStore()
  readonly api: BoardApi
  readonly chat: ChatClient
  readonly panels: SidePanelClient
  readonly files: FilesPanelClient
  readonly build: BuildClient
  readonly layout = new BoardLayoutClient(this.store)
  readonly reader = new BoardReader(this)
  readonly tiles = new TileClient(this)
  readonly tileActions = new TileActionsClient(this)
  readonly cards = new OpenCardClient(this)
  readonly activation = new ActivationClient(this)
  readonly roots = new RootChoiceClient(this)
  readonly draft = new BacklogDraftClient(this)

  constructor(send?: Send) {
    this.api = new BoardApi(this.store, send)
    this.chat = new ChatClient(this.store, this.api)
    this.panels = new SidePanelClient(this.store, this.api)
    this.files = new FilesPanelClient(this.store, this.api)
    this.build = new BuildClient(this.store, this.api)
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

  fixViolation(ticket: string, rule: ReportRuleData, violation: ViolationData): Promise<void> {
    return this.chat.command(this.actionCommandFor(ticket, fixViolationPrompt(rule, violation)))
  }

  fixRule(ticket: string, rule: ReportRuleData): Promise<void> {
    return this.chat.command(this.actionCommandFor(ticket, fixRulePrompt(rule)))
  }

  fixReport(ticket: string, rules: ReportRuleData[]): Promise<void> {
    return this.chat.command(this.actionCommandFor(ticket, fixReportPrompt(rules)))
  }

  // A report's fixes are for the ticket whose report it is, so they name that ticket's session.
  private actionCommandFor(ticket: string, command: string): string {
    return this.board.tickets.find(shown => shown.name === ticket)?.actionCommand(command) ?? command
  }

  // Restarts the one cdd server every chat and the board share on the code as it is now, then reads the board again.
  async restartCdd(): Promise<void> {
    const restarted = await this.api.post<{ is_restarted: boolean }>(CDD_RESTART_PATH)
    if (!restarted) return
    await Promise.all([this.reader.refresh(), this.chat.refresh()])
    if (this.store.state.serverFailure) return
    this.store.toast('cdd restarted on the current code')
  }

  openNewTicket(): Promise<void> {
    return this.chat.fill('Open a new ticket with ticket.new, titled: ')
  }

  start(): () => void {
    const stopBoard = this.reader.startPolling()
    const chatTimer = setInterval(() => void Promise.all([this.chat.refresh(), this.build.check()]), CHAT_POLL_MILLISECONDS)
    void Promise.all([this.chat.refresh(), this.build.check()])
    return () => {
      stopBoard()
      clearInterval(chatTimer)
    }
  }
}
