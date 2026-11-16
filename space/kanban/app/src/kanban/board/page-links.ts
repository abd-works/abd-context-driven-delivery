import type { FidelityProgressClient } from '../ticket/fidelity-progress-client'
import type { TicketClient } from '../ticket/ticket-client'
import type { BoardPage } from './board-page'

const REPORT_QUERY = 'report'
const HELP_QUERY = 'help'
const FILES_QUERY = 'files'
const SESSION_FOLDER_QUERY = 'session-folder'
const FILE_QUERY = 'file'
const TICKET_QUERY = 'ticket'
const FIDELITY_QUERY = 'fidelity'
// Where every failure a link meets happened, as the chat that opened the page is told it.
const OPENING_FROM_A_LINK = 'Opening the Kanban board from a chat bar link'

// One fidelity of one ticket a link names, such as ?report=<ticket>&fidelity=<slug>.
type LinkedFidelity = { ticket: TicketClient; progress: FidelityProgressClient }

// The links a chat bar opens the board with: each names a ticket, and some a fidelity of it or a file, and opens what a
// press on the board would open, once the board has been read. A link naming nothing opens nothing; one naming what the
// board does not show says so.
export class PageLinks {
  constructor(private readonly page: BoardPage) {}

  // ?ticket=<ticket>, from the chat bar's health panel, opens the chat's ticket as a click on its card does.
  async openTicket(search: string): Promise<void> {
    const name = new URLSearchParams(search).get(TICKET_QUERY)
    if (!name) return
    const ticket = await this.ticketNamed(name)
    if (!ticket) return this.page.failures.fail(`The board has no ticket ${name}.`, OPENING_FROM_A_LINK)
    this.page.cards.open(ticket)
  }

  // ?report=<ticket>&fidelity=<slug>, from a fidelity's violation count, opens that ticket's report panel for it.
  async openReport(search: string): Promise<void> {
    const linked = await this.fidelityLinked(search, REPORT_QUERY, 'report')
    if (linked) await this.page.panels.openReport(linked.ticket, linked.progress)
  }

  // ?help=<ticket>&fidelity=<slug>, from a fidelity's hover tip, opens its help panel, as its ? on the tile does.
  async openHelp(search: string): Promise<void> {
    const linked = await this.fidelityLinked(search, HELP_QUERY, 'help')
    if (linked) await this.page.panels.openFidelityHelp(linked.progress)
  }

  // ?files=<ticket>&fidelity=<slug>,<slug>, from the chat bar's files button, opens the files panel on that ticket's
  // stage with those fidelities' practices turned on, as their files button on the tile does.
  async openFiles(search: string): Promise<void> {
    const query = new URLSearchParams(search)
    const name = query.get(FILES_QUERY)
    const slugs = (query.get(FIDELITY_QUERY) ?? '').split(',').filter(Boolean)
    if (!name || !slugs.length) return
    const ticket = await this.ticketNamed(name)
    const progress = slugs.flatMap(slug => ticket?.work.progressNamed(slug) ?? [])
    if (!ticket || !progress.length) return this.page.failures.fail(`The board has no ${slugs.join(', ')} files for ${name}.`, OPENING_FROM_A_LINK)
    this.select(ticket)
    await this.page.files.openFiles(ticket, progress)
  }

  // ?session-folder=<ticket>, from the chat bar's session name, opens the files panel on that ticket's session folder, as
  // the details' session link does; with &file=<path>, as a file the Story UI editor asks the chat to show, that file's
  // tab is open.
  async openSessionFolder(search: string): Promise<void> {
    const query = new URLSearchParams(search)
    const name = query.get(SESSION_FOLDER_QUERY)
    if (!name) return
    const ticket = await this.ticketNamed(name)
    if (!ticket) return this.page.failures.fail(`The board has no ticket ${name}.`, OPENING_FROM_A_LINK)
    this.select(ticket)
    const file = query.get(FILE_QUERY)
    await this.page.files.openFolder(ticket, 'session', file ?? '')
  }

  // The ticket a link names, the board read first when it has not been yet.
  private async ticketNamed(name: string): Promise<TicketClient | undefined> {
    if (!this.page.store.state.board) await this.page.reader.refresh()
    return this.page.board.tickets.find(shown => shown.name === name)
  }

  // The ticket and fidelity a report or help link names, the ticket selected; none, said, when the board has neither.
  private async fidelityLinked(search: string, ticketQuery: string, opened: string): Promise<LinkedFidelity | undefined> {
    const query = new URLSearchParams(search)
    const name = query.get(ticketQuery)
    const slug = query.get(FIDELITY_QUERY)
    if (!name || !slug) return undefined
    const ticket = await this.ticketNamed(name)
    const progress = ticket?.work.progressNamed(slug)
    if (!ticket || !progress) {
      this.page.failures.fail(`The board has no ${slug} ${opened} for ${name}.`, OPENING_FROM_A_LINK)
      return undefined
    }
    this.page.store.change({ selected: ticket.address })
    return { ticket, progress }
  }

  // A ticket opened in the files panel is selected, with the details region open beside it.
  private select(ticket: TicketClient): void {
    this.page.store.change({ selected: ticket.address })
    this.page.layout.expandRegion('details')
  }
}
