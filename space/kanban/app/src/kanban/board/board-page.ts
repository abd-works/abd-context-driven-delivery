import { projectOfPage } from '@cdd/cdd-shared'
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
import { BoardApi, sendWithFetch } from './board-api'
import type { Send } from './board-api'
import { BoardClient } from './board-client'
import { BoardLayoutClient } from './board-layout-client'
import { BoardReader } from './board-reader'
import { BoardStore } from '../shared/board-store'
import { BuildClient } from './build-client'
import { EditorAppClient } from './editor-app-client'
import { SidePanelClient } from './side-panel-client'

const CHAT_POLL_MILLISECONDS = 2000
const REPORT_QUERY = 'report'
const HELP_QUERY = 'help'
const FILES_QUERY = 'files'
const SESSION_FOLDER_QUERY = 'session-folder'
const FILE_QUERY = 'file'
const TICKET_QUERY = 'ticket'
const FIDELITY_QUERY = 'fidelity'
const NOT_READ_YET: BoardData = { project: '', practices: [], open_tickets: [], active: null, columns: [], fidelities: [], sends_fixes_directly: false, unsaved: null }

// Everything the page's views act through, wired once.
// How much of a chat's id tells two chats with the same name apart.
const SHOWN_CHAT_ID = 8

export class BoardPage {
  readonly store = new BoardStore()
  readonly api: BoardApi
  // The api the board's own two-second read posts through, which says nothing when slow.
  readonly readingApi: BoardApi
  readonly chat: ChatClient
  readonly panels: SidePanelClient
  readonly files: FilesPanelClient
  readonly build: BuildClient
  readonly editorApp: EditorAppClient
  readonly layout = new BoardLayoutClient(this.store)
  readonly reader = new BoardReader(this)
  readonly tiles = new TileClient(this)
  readonly tileActions = new TileActionsClient(this)
  readonly cards = new OpenCardClient(this)
  readonly activation = new ActivationClient(this)
  readonly roots = new RootChoiceClient(this)
  readonly draft = new BacklogDraftClient(this)

  constructor(send: Send = sendWithFetch) {
    this.api = new BoardApi(this.store, send)
    this.readingApi = new BoardApi(this.store, send, projectOfPage(), false)
    this.chat = new ChatClient(this.store, this.api)
    this.panels = new SidePanelClient(this.store, this.api)
    this.files = new FilesPanelClient(this.store)
    this.build = new BuildClient(this.store, send)
    this.editorApp = new EditorAppClient(this.store, this.api)
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

  // A chat goes by its own name in the chat list; two chats with the same name, such as two titled the same in the app,
  // also show the start of their ids, so a person can tell them apart.
  chatName(chat: ChatData): string {
    const own = chat.name || chat.id
    const isShared = this.store.state.chats.some(other => other.id !== chat.id && (other.name || other.id) === own)
    return isShared ? `${own} (${chat.id.slice(0, SHOWN_CHAT_ID)})` : own
  }

  // A chat picked in the chat list while a ticket is selected is assigned to that ticket, kept in its session.json, so
  // the board sends its commands there from now on; with no ticket selected it is only the chat commands go to when no
  // ticket has one.
  async pickChat(chat: string): Promise<void> {
    this.chat.choose(chat)
    const selected = this.board.tickets.find(ticket => ticket.address === this.store.state.selected)
    if (!selected) return
    this.chat.assign(selected.name, chat)
    await selected.assignChat(chat)
    await this.reader.refresh()
  }

  ticket(json: TicketData): TicketClient {
    return new TicketClient(json, this)
  }

  item(json: BacklogItemData): BacklogItemClient {
    return new BacklogItemClient(json, this)
  }

  // Installs the board again through Python's App.install, which installs its packages and rebuilds its page, then loads
  // the page again from the new build. A failed install says why in a toast and keeps the page.
  async update(): Promise<void> {
    if (this.store.state.isUpdating) return
    this.store.change({ isUpdating: true })
    this.store.toast('Updating: installing the board and rebuilding its page')
    if (await this.editorApp.kanban.install()) this.store.change({ isNewBuild: true })
    this.store.change({ isUpdating: false })
  }

  openNewTicket(): Promise<void> {
    const session = this.board.activeTicket?.session.session_file
    return this.chat.fill(`Open a new ticket with ticket.create${session ? ` session=${session}` : ''}, titled: `)
  }

  // A link such as ?report=<ticket>&fidelity=<slug>, which the chat bar opens from a fidelity's violation count, opens
  // that ticket's report panel for that fidelity once the board has been read. A link naming nothing the board shows
  // opens nothing.
  async openLinkedReport(search: string): Promise<void> {
    const query = new URLSearchParams(search)
    const name = query.get(REPORT_QUERY)
    const slug = query.get(FIDELITY_QUERY)
    if (!name || !slug) return
    if (!this.store.state.board) await this.reader.refresh()
    const ticket = this.board.tickets.find(shown => shown.name === name)
    const progress = ticket?.progressNamed(slug)
    if (!ticket || !progress) return this.store.toast(`The board has no ${slug} report for ${name}.`, true)
    this.store.change({ selected: ticket.address })
    await this.panels.openReport(ticket, progress)
  }

  // A link such as ?help=<ticket>&fidelity=<slug>, which the chat bar opens from a fidelity's hover tip, opens that
  // fidelity's help panel, as its ? on the ticket's tile does. A link naming nothing the board shows opens nothing.
  async openLinkedHelp(search: string): Promise<void> {
    const query = new URLSearchParams(search)
    const name = query.get(HELP_QUERY)
    const slug = query.get(FIDELITY_QUERY)
    if (!name || !slug) return
    if (!this.store.state.board) await this.reader.refresh()
    const ticket = this.board.tickets.find(shown => shown.name === name)
    const progress = ticket?.progressNamed(slug)
    if (!ticket || !progress) return this.store.toast(`The board has no ${slug} help for ${name}.`, true)
    this.store.change({ selected: ticket.address })
    await this.panels.openFidelityHelp(progress)
  }

  // A link such as ?files=<ticket>&fidelity=<slug>,<slug>, which the chat bar's files button opens, opens the files panel
  // on that ticket's stage with those fidelities' practices turned on, as their files button on the tile does. A link
  // naming no fidelity the ticket has opens nothing.
  async openLinkedFiles(search: string): Promise<void> {
    const query = new URLSearchParams(search)
    const name = query.get(FILES_QUERY)
    const slugs = (query.get(FIDELITY_QUERY) ?? '').split(',').filter(Boolean)
    if (!name || !slugs.length) return
    if (!this.store.state.board) await this.reader.refresh()
    const ticket = this.board.tickets.find(shown => shown.name === name)
    const progress = slugs.flatMap(slug => ticket?.progressNamed(slug) ?? [])
    if (!ticket || !progress.length) return this.store.toast(`The board has no ${slugs.join(', ')} files for ${name}.`, true)
    this.store.change({ selected: ticket.address })
    this.layout.expandRegion('details')
    await this.files.openFiles(ticket, progress)
  }

  // A link such as ?session-folder=<ticket>, which the chat bar's session name opens, opens the files panel on that
  // ticket's session folder, as the details' session link does; with &file=<path>, as a file the Story UI editor asks
  // the chat to show, that file's tab is open. A link naming a ticket the board does not show says so.
  async openLinkedSessionFolder(search: string): Promise<void> {
    const query = new URLSearchParams(search)
    const name = query.get(SESSION_FOLDER_QUERY)
    if (!name) return
    if (!this.store.state.board) await this.reader.refresh()
    const ticket = this.board.tickets.find(shown => shown.name === name)
    if (!ticket) return this.store.toast(`The board has no ticket ${name}.`, true)
    this.store.change({ selected: ticket.address })
    this.layout.expandRegion('details')
    const file = query.get(FILE_QUERY)
    await (file ? this.files.openSessionFile(ticket, file) : this.files.openSessionFolder(ticket))
  }

  // A link such as ?ticket=<ticket>, which the chat bar opens from its health panel, opens the chat's ticket once the
  // board has been read, as a click on its card does. A link naming a ticket the board does not show says so.
  async openLinkedTicket(search: string): Promise<void> {
    const name = new URLSearchParams(search).get(TICKET_QUERY)
    if (!name) return
    if (!this.store.state.board) await this.reader.refresh()
    const ticket = this.board.tickets.find(shown => shown.name === name)
    if (!ticket) return this.store.toast(`The board has no ticket ${name}.`, true)
    this.cards.open(ticket)
  }

  start(): () => void {
    const search = typeof location === 'undefined' ? '' : location.search
    void this.openLinkedTicket(search)
    void this.openLinkedReport(search)
    void this.openLinkedHelp(search)
    void this.openLinkedFiles(search)
    void this.openLinkedSessionFolder(search)
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
