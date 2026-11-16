import type { BacklogItemData } from '@cdd/space/kanban/backlog-item'
import { TicketClientGenerated, type TicketData } from '@cdd/space/kanban/ticket'
import { FileCommentsClientGenerated } from '@cdd/space/session/file-comments'
import { SessionClientGenerated } from '@cdd/space/session/session'

import type { BoardPage } from '../board/board-page'
import { TicketMove, TicketNewParent, TicketPlacedBefore, TicketPulledOut, TicketTextEdit } from '../shared/pending-changes'
import { TicketChat } from '../chat/chat-client'
import { TicketChatPrompts } from './ticket-chat-prompts'
import { TicketPractices } from './ticket-practices'
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
  }

  // The practices its session works on, each turned on or off from the ticket.
  readonly practices: TicketPractices

  // Its progress on each fidelity the board requires, and the files and reports that progress answers for.
  readonly work: TicketWork

  // What the ticket asks its chat to do for it.
  readonly prompts: TicketChatPrompts

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

  get standing(): string {
    return this.isClosed ? '' : this.isDone ? 'done' : 'in progress'
  }

  // Where a split ticket came from: `story of epic`.
  get origin(): string {
    const { scope, parent } = this.session
    return scope && parent ? `${scope} of ${parent}` : scope
  }

  get stagePlace(): string {
    return [this.column.name, this.standing].filter(Boolean).join(' · ')
  }

  // The action Run next sends: the next fidelity's own next action.
  get nextAction(): string {
    return this.work.nextProgress?.nextAction ?? ''
  }

  // The ticket's session, its practices, and its fidelities' progress each answer their own tools, built from the data
  // the ticket already holds.
  get sessionClient(): SessionClientGenerated {
    return new SessionClientGenerated(this.api, this.session)
  }

  // The comments a person wrote on the files of its session, kept in the session's folder.
  get fileComments(): FileCommentsClientGenerated {
    return FileCommentsClientGenerated.named(this.api, this.session.session_file)
  }

  // The chat working on this ticket, which Python names, and every command the board sends for it goes to.
  get chat(): TicketChat {
    return new TicketChat(this.page.chat, this.name, this.workingChat)
  }

  get runNextLabel(): string {
    return this.next ? `Run next: ${this.nextAction}` : 'Run next'
  }

  // The run-next icon's tooltip names the step and the fidelity it runs on, since the icon itself cannot.
  get runNextHint(): string {
    if (this.isLocked) return 'Activate this session to run its next step'
    if (!this.next) return 'Nothing to run next'
    return `${this.runNextLabel} on ${this.next.fidelity.slug}`
  }

  get nextNote(): string {
    return this.next ? `Next: ${this.next.fidelity.slug}, ${this.nextAction}` : ''
  }

  get lockNote(): string {
    return this.isLocked ? 'Activate this session to run actions' : ''
  }

  // Python says which columns besides the stages take the ticket: the Backlog always, Complete only as it allows.
  canDropOn(edge: string): boolean {
    return this.dropTargets.includes(edge)
  }

  // Complete closes it: an open ticket through its Close dialog, which asks what to do with its work, and one not opened,
  // which has no worktree or chat to wind up, at once.
  async dropOn(edge: string): Promise<void> {
    if (this.page.board.columnNamed(edge)?.isBacklog) await this.moveTo(edge, false)
    else if (this.isOpen) await this.page.activation.startClosing(this)
    else await this.close()
  }

  // Python names the tickets another can be dropped on to become their child.
  canTakeAsChild(other: TicketClient): boolean {
    return other.parentChoices.includes(this.name)
  }

  select(): void {
    this.page.store.change({ selected: this.address })
  }

  // A person clicking the ticket: it opens in the details, and the chat at the top of the board is its chat, the one
  // working in its worktree; with none open, main's chat when main has one; else no chat, so the top never shows another
  // ticket's chat. A press only selects: opening a worktree and a chat is the card's own button.
  choose(): void {
    this.select()
    const chat = this.chat.found ?? this.page.board.mainTicket?.chat.found
    this.page.chat.choose(chat?.id ?? '')
  }

  get canOpenChat(): boolean {
    return !this.isClosed && !this.chat.found
  }

  // A new chat opens on the ticket's worktree, after activating opens one when the ticket has none. A ticket in Complete
  // has closed its work, so it gets no new branch, worktree, or chat.
  async openChat(): Promise<void> {
    const chat = this.chat
    if (!this.canOpenChat || !chat.beginOpening()) return
    await chat.start(await this.worktreeOpened())
  }

  // The ticket's worktree, opened by activating when the ticket has none.
  private async worktreeOpened(): Promise<string> {
    if (this.worktree) return this.worktree
    const opened = await this.activate()
    await this.page.reader.refresh()
    return opened?.worktree ?? ''
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
    this.page.cards.releaseTicket(this.name)
    this.page.panels.closeTicketPanels(this.name)
  }

  // Deleted, the ticket and its session folder are gone, so nothing stays open on it. Python answers nothing either way,
  // so the board is read again to show what is there.
  override async delete(): Promise<null> {
    await super.delete()
    this.letGo()
    await this.page.reader.refresh()
    return null
  }

  get canRunNext(): boolean {
    if (!this.next || this.isLocked) return false
    // Opening the report while violations hold the fidelity is done on the board, so it needs no chat.
    return this.work.nextProgress?.state === 'violations' || this.page.chat.canSend
  }

  // Python gives the command for the next action, naming the session and no format. Generate is sent straight to the
  // chat, in the format the fidelity keeps; the others fill the prompt. While violations hold the fidelity, Run next opens
  // its report on the board, where the person reads them and sends the fix.
  async runNext(): Promise<void> {
    const next = this.work.nextProgress
    if (!next) return
    if (next.state === 'violations') return this.page.panels.openReport(this, next)
    const command = next.commands[this.nextAction] ?? ''
    if (this.nextAction !== 'generate') return this.chat.fill(command)
    await this.chat.command(command)
  }
}
