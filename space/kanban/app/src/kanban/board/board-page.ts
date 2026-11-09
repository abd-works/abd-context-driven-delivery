import type { BacklogItemData } from '@cdd/space/kanban/backlog-item'
import type { BoardData } from '@cdd/space/kanban/board'
import type { TicketData } from '@cdd/space/kanban/ticket'
import type { ChatData } from '@cdd/harness/chat/chat'

import { BacklogDraftClient, BacklogItemClient } from '../backlog-item/backlog-item-client'
import { ChatClient } from '../chat/chat-client'
import { ActivationClient } from '../ticket/activation-client'
import { FilesPanelClient } from '../ticket/files-panel-client'
import { OpenCardClient } from '../ticket/open-card-client'
import { RootChoiceClient } from '../ticket/root-choice-client'
import { TicketClient } from '../ticket/ticket-client'
import { TileActionsClient } from '../ticket/tile-actions-client'
import { TileClient } from '../ticket/tile-client'
import { BoardApi } from './board-api'
import type { Send } from './board-api'
import { BoardClient } from './board-client'
import { BoardLayoutClient } from './board-layout-client'
import { BoardReader } from './board-reader'
import { BoardStore } from '../shared/board-store'
import { BuildClient } from './build-client'
import { SidePanelClient } from './side-panel-client'

const CHAT_POLL_MILLISECONDS = 2000
const UPDATE_PATH = '/update'
const BUILD_PATH = '/build'
const SERVER_BACK_WITHIN_MILLISECONDS = 30_000
const SERVER_BACK_CHECK_MILLISECONDS = 1000
const CLAUDE_OPEN_PATH = '/claude/open'
const NOT_READ_YET: BoardData = { project: '', practices: [], open_tickets: [], active: null, columns: [], fidelities: [] }

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

  // Opens a claude:// link through the board server, because the Browser pane does not pass the link to the Claude app.
  // A spec replaces it to see the link.
  openLink: (link: string) => void = link => void this.api.post(CLAUDE_OPEN_PATH, { link })
  // How long the page waits between checks for the restarted server. A spec replaces it so it does not wait.
  pause: (milliseconds: number) => Promise<void> = milliseconds => new Promise(done => setTimeout(done, milliseconds))

  constructor(send?: Send) {
    this.api = new BoardApi(this.store, send)
    this.chat = new ChatClient(this.store, this.api, link => this.openLink(link))
    this.panels = new SidePanelClient(this.store, this.api)
    this.files = new FilesPanelClient(this.store)
    this.build = new BuildClient(this.store, this.api)
  }

  // The board as last read, made once for that read and again only when the store holds a new read, since the views
  // read it many times in one render.
  private shown: BoardClient | null = null

  get board(): BoardClient {
    const read = this.store.state.board ?? NOT_READ_YET
    if (this.shown?.read !== read) this.shown = new BoardClient(read, this)
    return this.shown
  }

  async reloadOpen(): Promise<void> {
    await Promise.all([this.tiles.reload(), this.panels.reload(), this.files.reload()])
  }

  // A chat working on a ticket, as Python names it, goes by the ticket's name.
  chatName(chat: ChatData): string {
    return this.board.tickets.find(ticket => ticket.workingChat?.id === chat.id)?.name ?? (chat.name || chat.id)
  }

  ticket(json: TicketData): TicketClient {
    return new TicketClient(json, this)
  }

  item(json: BacklogItemData): BacklogItemClient {
    return new BacklogItemClient(json, this)
  }

  // Brings the board and every chat onto the latest code: the installer pulls and pins cdd, the server rebuilds and restarts itself, and
  // the page loads again from it.
  async update(): Promise<void> {
    if (this.store.state.isUpdating) return
    this.store.change({ isUpdating: true })
    this.store.toast('Updating: getting the latest code, re-pinning cdd, and rebuilding')
    const updated = await this.api.post<{ is_updated: boolean }>(UPDATE_PATH)
    if (updated && (await this.boardServerIsBack())) this.store.change({ isNewBuild: true })
    this.store.change({ isUpdating: false })
  }

  // The server restarts after it answers, so the page waits for it to go away and then for the new one to answer.
  private async boardServerIsBack(): Promise<boolean> {
    for (let waited = 0; waited < SERVER_BACK_WITHIN_MILLISECONDS; waited += SERVER_BACK_CHECK_MILLISECONDS) {
      await this.pause(SERVER_BACK_CHECK_MILLISECONDS)
      if (await this.api.get<{ build: string }>(BUILD_PATH)) return true
    }
    this.store.toast('The board server did not come back after the update; run /board in a chat to start it.', true)
    return false
  }

  openNewTicket(): Promise<void> {
    const session = this.board.activeTicket?.session.session_file
    return this.chat.fill(`Open a new ticket with ticket.create${session ? ` session=${session}` : ''}, titled: `)
  }

  start(): () => void {
    const stopBoard = this.reader.startPolling()
    const chatTimer = setInterval(() => void this.pollChats(), CHAT_POLL_MILLISECONDS)
    void this.pollChats()
    return () => {
      stopBoard()
      clearInterval(chatTimer)
    }
  }

  // A slow cdd server answers after the next tick, so a tick is skipped while the last read is still pending, as the
  // board's own poll does; otherwise each tick opens another connection and they pile up on the server.
  private isPollingChats = false

  private async pollChats(): Promise<void> {
    if (this.isPollingChats) return
    this.isPollingChats = true
    await Promise.all([this.chat.refresh(), this.build.check()]).finally(() => {
      this.isPollingChats = false
    })
  }
}
