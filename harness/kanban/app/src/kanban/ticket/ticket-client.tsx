import type { BacklogItemData } from '@cdd/harness/kanban/backlog-item'
import { FidelityProgressClientGenerated, type ActionStatesData } from '@cdd/harness/kanban/fidelity-progress'
import { TicketClientGenerated, type TicketData } from '@cdd/harness/kanban/ticket'
import { PracticeSessionOutputClientGenerated } from '@cdd/space/session/practice-session-output'
import { SessionClientGenerated } from '@cdd/space/session/session'

import { PRACTICES, practiceOf, STATES, WORK_LIGHT } from '../board/board-brand'
import type { BoardPage } from '../board/board-page'
import type { ColumnClient } from '../board/column-client'

const RUN_NEXT_COMMANDS: Record<string, string> = {
  validate: '/actions-validate',
}
// Steps the board does itself rather than sending to a chat: a review is the person's own, opening the report while the
// fidelity has violations and recording the approval once it has none.
const STEPS_WITHOUT_CHAT = ['review']
const CLOSE_SESSION_COMMAND = '/space:session:close-session'

const isBacklogItem = (moved: TicketData | BacklogItemData): moved is BacklogItemData => !('column' in moved)

// The practice's skill for a fidelity: `clean-engineering-code` is /practices-clean-engineering-clean-engineering-code.
export const skillOf = (slug: string): string => `/practices-${practiceOf(slug)?.prefix ?? ''}${slug}`

// A ticket as the page knows it, with what a person can do to it. Each operation reaches the ticket's tool through the
// generated client it extends, then brings the rest of the page up to date.
export class TicketClient extends TicketClientGenerated {
  constructor(
    json: TicketData,
    private readonly page: BoardPage,
  ) {
    super(page.api, json)
  }

  // A session can sit in closed/ under the name of an open one, so a column and name together say which ticket is meant.
  get address(): string {
    return `${this.column}/${this.name}`
  }

  get isClosed(): boolean {
    return this.column === 'Complete'
  }

  get isActive(): boolean {
    return this.name === this.page.board.active
  }

  // Commands run in the active session, so with Active session only on, another ticket cannot start one.
  get isLocked(): boolean {
    return this.page.store.state.onlyActive && !this.isActive
  }

  get violatedSlugs(): string[] {
    return Object.entries(this.progress)
      .filter(([, progress]) => progress.state === 'violations')
      .map(([slug]) => slug)
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
    return [this.column, this.standing].filter(Boolean).join(' · ')
  }

  // The action Run next sends: the next fidelity's own next action.
  get nextAction(): string {
    return this.next ? (this.progress[this.next]?.next_action ?? '') : ''
  }

  // The ticket's session, its practices, and its fidelities' progress each answer their own tools.
  get sessionClient(): SessionClientGenerated {
    return new SessionClientGenerated(this.api, this.session)
  }

  practiceClient(practice: string): PracticeSessionOutputClientGenerated {
    return PracticeSessionOutputClientGenerated.named(this.api, this.session.session_file, practice)
  }

  progressClient(slug: string): FidelityProgressClientGenerated {
    return FidelityProgressClientGenerated.named(this.api, this.name, slug)
  }

  get nextStepName(): string {
    return this.nextAction === 'review' && this.violationCountOf([this.next ?? '']) ? 'review violations' : this.nextAction
  }

  get runNextLabel(): string {
    return this.next ? `Run next: ${this.nextStepName}` : 'Run next'
  }

  // The run-next icon's tooltip names the step and the fidelity it runs on, since the icon itself cannot.
  get runNextHint(): string {
    if (this.isLocked) return 'Activate this session to run its next step'
    if (!this.next) return 'Nothing to run next'
    return `${this.runNextLabel} on ${this.next}`
  }

  get nextNote(): string {
    return this.next ? `Next: ${this.next}, ${this.nextStepName}` : ''
  }

  get lockNote(): string {
    return this.isLocked ? 'Activate this session to run actions' : ''
  }

  // The Backlog takes any ticket, which keeps its whole folder there. Complete takes one from Implementation's Done, or
  // the active ticket through its Close dialog, because closing it asks what to do with its work.
  canDropOn(edge: string): boolean {
    if (edge === 'Backlog') return true
    if (edge === 'Complete') return this.isActive || (this.column === 'Implementation' && this.isDone)
    return false
  }

  async dropOn(edge: string): Promise<void> {
    if (edge === 'Backlog') await this.moveTo('Backlog', false)
    else if (this.isActive) await this.page.activation.start(this, true)
    else await this.moveNext()
  }

  isEnabled(practice: string): boolean {
    return this.session.practices[practice]?.enabled ?? true
  }

  stateOf(slug: string): { label: string; color: string; key: string } {
    const key = this.progress[slug]?.state ?? 'not_started'
    return { ...STATES[key]!, key }
  }

  lightOf(slug: string): number {
    return this.isEnabled(practiceOf(slug)?.key ?? '') ? WORK_LIGHT[this.stateOf(slug).key]! : WORK_LIGHT.off!
  }

  actionsOf(slug: string): ActionStatesData {
    return this.progress[slug]?.actions ?? { generate: 'to_do', validate: 'to_do', review: 'to_do' }
  }

  // How far one action has got across slugs: done only when it is done on all of them.
  standingOf(slugs: string[], action: keyof ActionStatesData): string {
    const states = slugs.map(slug => this.actionsOf(slug)[action])
    if (states.length && states.every(state => state === 'done')) return 'done'
    return states.some(state => state !== 'to_do') ? 'in_progress' : 'to_do'
  }

  violationCountOf(slugs: string[]): number {
    return slugs.reduce((total, slug) => total + (this.progress[slug]?.violation_count ?? 0), 0)
  }

  enabledSlugs(stage: ColumnClient): string[] {
    return stage.workRequired.filter(slug => this.isEnabled(practiceOf(slug)?.key ?? ''))
  }

  allows(slug: string, action: string): boolean {
    return (this.progress[slug]?.allowed_actions ?? []).includes(action)
  }

  isNext(stage: ColumnClient, slug: string): boolean {
    return this.next === slug && stage.workRequired.includes(slug)
  }

  select(): void {
    this.page.board.select(this.address)
  }

  // A person clicking the ticket: it opens in the details, and the board's commands go to its chat, the one working in its
  // worktree. With no chat there yet, a new one opens there, after the worktree when the ticket has none. A ticket in
  // Complete has closed its work, so it gets no new branch, worktree, or chat.
  async choose(): Promise<void> {
    this.select()
    const chat = this.page.chat.chatFor(this.name, this.worktree)
    if (chat) return this.page.chat.choose(chat.id)
    if (this.isClosed || !this.page.chat.beginOpening(this.name)) return
    this.page.chat.startFor(this.name, await this.worktreeOpened())
  }

  private async worktreeOpened(): Promise<string> {
    if (this.worktree) return this.worktree
    const opened = await this.page.board.openWorktree(this.name)
    await this.page.reader.refresh()
    return opened?.worktree ?? ''
  }

  override async moveNext(): Promise<this | null> {
    return this.followed(await super.moveNext())
  }

  override async moveTo(stage: string, done?: boolean): Promise<TicketData | BacklogItemData | null> {
    return this.landed(await super.moveTo(stage, done))
  }

  // The card stays open on the ticket wherever it moved.
  private async followed(moved: this | null): Promise<this | null> {
    await this.page.reader.refresh()
    if (moved) await this.page.cards.follow(this.page.ticket(moved.toJSON()))
    return moved
  }

  override async movePrevious(): Promise<TicketData | BacklogItemData | null> {
    return this.landed(await super.movePrevious())
  }

  // A move can land the ticket on a stage, where the card follows it, or in the Backlog, where its item is selected.
  private async landed(moved: TicketData | BacklogItemData | null): Promise<TicketData | BacklogItemData | null> {
    await this.page.reader.refresh()
    if (!moved) return null
    if (isBacklogItem(moved)) this.release(moved)
    else await this.page.cards.follow(this.page.ticket(moved))
    return moved
  }

  // Moved to the Backlog, a ticket is off the board, so nothing stays open on it and its item is selected.
  private release(item: BacklogItemData): void {
    this.page.cards.releaseTicket(this.name)
    this.page.panels.closeTicketPanels(this.name)
    this.page.item(item).select()
  }

  async enablePractice(practice: string, isEnabled: boolean): Promise<boolean> {
    const saved = await this.practiceClient(practice).enable(isEnabled)
    await this.page.reader.refresh()
    if (!saved) return false
    if (!isEnabled) this.page.cards.dropPractice(this.name, practice)
    const name = PRACTICES.find(entry => entry.key === practice)?.name ?? practice
    this.page.store.toast(`${name} ${isEnabled ? 'on' : 'off'} for ${this.title} · saved to ${this.session.session_file}`)
    return true
  }

  private async review(slug: string): Promise<void> {
    await this.progressClient(slug).finishReview()
    await this.page.reader.refresh()
  }

  // A command runs in whichever chat it is sent to, whose open session can be another ticket's, so every action command
  // names this ticket's session.json.
  actionCommand(command: string): string {
    return `${command} session=${this.session.session_file}`
  }

  fillSplit(): Promise<void> {
    return this.page.chat.fill(`Split ticket ${this.name} into child tickets, one per story on its story map: call ticket.create with parent ${this.name} for each story.`, this.name, this.worktree)
  }

  // Closing ends the chat's session and leaves the ticket where it is; moving it into Complete is what completes it.
  closeSession(): Promise<void> {
    return this.page.chat.command(CLOSE_SESSION_COMMAND, this.name, this.worktree)
  }

  fillHandoff(): Promise<void> {
    return this.page.chat.fill(`Write a handoff for ticket ${this.name} with /space-handoff-handoff-session.`, this.name, this.worktree)
  }

  get canRunNext(): boolean {
    if (!this.next || this.isLocked) return false
    return STEPS_WITHOUT_CHAT.includes(this.nextAction) || this.page.chat.canSend
  }

  // Generate can take two commands, a render and then the generate, so it runs them where the others fill the prompt.
  async runNext(): Promise<void> {
    const slug = this.next ?? ''
    if (this.nextAction === 'review' && this.violationCountOf([slug])) return this.page.panels.openReport(this.name, slug)
    if (this.nextAction === 'review') return this.review(slug)
    if (this.nextAction !== 'generate') return this.page.chat.fill(this.actionCommand(`${RUN_NEXT_COMMANDS[this.nextAction]} ${slug}`), this.name, this.worktree)
    const format = this.stageRequiring(slug)?.defaultFormats[slug]
    await this.page.tileActions.runCommandsOf(this.name, [slug], format ? [format] : [])
  }

  // Run next can reach back to an earlier stage, so a fidelity's stage is the one that requires it, not the ticket's.
  private stageRequiring(slug: string): ColumnClient | undefined {
    return this.page.board.stages.find(stage => stage.workRequired.includes(slug))
  }
}
