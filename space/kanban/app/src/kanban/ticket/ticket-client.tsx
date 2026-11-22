import type { BacklogItemData } from '@cdd/space/kanban/backlog-item'
import { TicketClientGenerated, type TicketData } from '@cdd/space/kanban/ticket'
import { SessionClientGenerated } from '@cdd/space/session/session'

import type { BoardPage } from '../board/board-page'
import { TicketMove, TicketNewParent, TicketPlacedBefore, TicketPulledOut, TicketTextEdit } from '../shared/pending-changes'
import { TicketChat } from '../chat/chat-client'
import { TicketChatOpening } from './ticket-chat-opening'
import { TicketChatPrompts } from './ticket-chat-prompts'
import { TicketDrops } from './ticket-drops'
import { TicketFace } from './ticket-face'
import { TicketNextStep } from './ticket-next-step'
import { TicketPractices } from './ticket-practices'
import { TicketSelection } from './ticket-selection'
import { TicketWork } from './ticket-work'

// A ticket sends its fidelities' progress; a backlog item, which also names its column now, sends none.
const isBacklogItem = (moved: TicketData | BacklogItemData): moved is BacklogItemData => !('progress' in moved)

// A ticket as the page knows it, with what a person can do to it. Each operation reaches the ticket's tool through the
// generated client it extends, then brings the rest of the page up to date: a tool that answers the ticket changed, such
// as editText, tag, pullOut, reassignParent, moveBefore, or addChild, has the board read again, so the page shows it.
export class TicketClient extends TicketClientGenerated {
  constructor(
    json: TicketData,
    private readonly page: BoardPage,
  ) {
    super(page.api, json)
    this.onChanged(() => void page.reader.refresh())
    this.prompts = new TicketChatPrompts(this, page)
    this.work = new TicketWork(this, page)
    this.practices = new TicketPractices(this, page)
    this.face = new TicketFace(this)
    this.nextStep = new TicketNextStep(this, page)
    this.chatOpening = new TicketChatOpening(this, page)
    this.drops = new TicketDrops(this, page)
    this.selection = new TicketSelection(this, page)
  }

  // The practices its session works on, each turned on or off from the ticket.
  readonly practices: TicketPractices

  // Its progress on each fidelity the board requires, and the files and reports that progress answers for.
  readonly work: TicketWork

  // What the ticket asks its chat to do for it.
  readonly prompts: TicketChatPrompts

  // What its card, details, and panels write about it.
  readonly face: TicketFace

  // The step Run next takes on it.
  readonly nextStep: TicketNextStep

  // Opening its chat on its worktree.
  readonly chatOpening: TicketChatOpening

  // Where it can be dropped, and what a drop on the Backlog or Complete does.
  readonly drops: TicketDrops

  // Choosing it on the page, which opens it in the details and puts its chat at the top of the board.
  readonly selection: TicketSelection

  // Its children as tickets of the page: stacked inside its card, or pulled out and kept as dashed rows.
  get childTickets(): TicketClient[] {
    return this.children.map(child => this.page.ticket(child))
  }

  // A session can sit in closed/ under the name of an open one, so a column and name together say which ticket is meant.
  get address(): string {
    return `${this.column.name}/${this.name}`
  }

  // Commands run in the active session, so with Active session only on, another ticket cannot start one.
  get isLocked(): boolean {
    return this.page.store.state.onlyActive && !this.isActive
  }

  // The ticket's session, its practices, and its fidelities' progress each answer their own tools, built from the data
  // the ticket already holds.
  get sessionClient(): SessionClientGenerated {
    return new SessionClientGenerated(this.api, this.session)
  }

  // The chat working on this ticket, which Python names, and every command the board sends for it goes to.
  get chat(): TicketChat {
    return new TicketChat(this.page.chat, this.name, this.workingChat)
  }

  // Python says where Move next and Move previous put the ticket while it stays on a stage, so the card shows there at
  // once; a move that closes, reopens, or sends it to the Backlog waits for Python to show it.
  override async moveNext(): Promise<this | null> {
    const place = this.nextPlace
    const moved = place ? await this.page.reader.change(new TicketMove(this.name, place.stage.name, place.is_done), () => super.moveNext()) : await super.moveNext()
    return this.followed(moved)
  }

  // Dropped on a stage, the card shows there at once; moved to the Backlog it becomes an item, which only Python can show.
  override async moveTo(stage: string, done?: boolean): Promise<TicketData | BacklogItemData | null> {
    const moved = this.page.board.columnNamed(stage)?.isStage
      ? await this.page.reader.change(new TicketMove(this.name, stage, done ?? false), () => super.moveTo(stage, done))
      : await super.moveTo(stage, done)
    return this.landed(moved)
  }

  override async moveBefore(other: string): Promise<this | null> {
    return this.page.reader.change(new TicketPlacedBefore(this.name, other), () => super.moveBefore(other))
  }

  override async editText(text: string): Promise<this | null> {
    return this.page.reader.change(new TicketTextEdit(this.name, text), () => super.editText(text))
  }

  // Given a parent, the ticket shows in the parent's card at once; given none, as a card of its own.
  override async reassignParent(parent?: string): Promise<this | null> {
    return this.page.reader.change(new TicketNewParent(this.name, parent ?? null), () => super.reassignParent(parent))
  }

  override async pullOut(): Promise<this | null> {
    return this.page.reader.change(new TicketPulledOut(this.name), () => super.pullOut())
  }

  // The card stays open on the ticket wherever it moved.
  private async followed(moved: this | null): Promise<this | null> {
    await this.page.reader.refresh()
    if (moved) await this.page.cards.follow(this.page.ticket(moved.toJSON()))
    return moved
  }

  override async movePrevious(): Promise<TicketData | BacklogItemData | null> {
    const place = this.previousPlace
    const moved = place ? await this.page.reader.change(new TicketMove(this.name, place.stage.name, place.is_done), () => super.movePrevious()) : await super.movePrevious()
    return this.landed(moved)
  }

  // A move can land the ticket on a stage, where the card follows it, or in the Backlog, where its item is selected.
  private async landed(moved: TicketData | BacklogItemData | null): Promise<TicketData | BacklogItemData | null> {
    await this.page.reader.refresh()
    if (!moved) return null
    if (isBacklogItem(moved)) this.releaseInto(moved)
    else await this.page.cards.follow(this.page.ticket(moved))
    return moved
  }

  // Moved to the Backlog, a ticket is off the board, so nothing stays open on it and the item now holding it is selected.
  private releaseInto(holdingItem: BacklogItemData): void {
    this.letGo()
    this.page.item(holdingItem).select()
  }

  private letGo(): void {
    this.page.cards.releaseTicket(this)
    this.page.panels.closeTicketPanels(this)
  }

  // Deleted, the ticket and its session folder are gone, so nothing stays open on it. Python answers nothing either way,
  // so the board is read again to show what is there.
  override async delete(): Promise<null> {
    await super.delete()
    this.letGo()
    await this.page.reader.refresh()
    return null
  }
}
