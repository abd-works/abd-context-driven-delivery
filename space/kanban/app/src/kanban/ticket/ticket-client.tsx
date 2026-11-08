import type { BacklogItemData } from '@cdd/space/kanban/backlog-item'
import type { FidelityGuidanceData } from '@cdd/space/kanban/board'
import type { FidelityProgressClientGenerated } from '@cdd/space/kanban/fidelity-progress'
import { TicketClientGenerated, type ActionStatesData, type ReportRuleData, type TicketData, type ViolationData } from '@cdd/space/kanban/ticket'
import { PracticeSessionOutputClientGenerated } from '@cdd/space/session/practice-session-output'
import { SessionClientGenerated } from '@cdd/space/session/session'

import type { BoardPage } from '../board/board-page'
import type { ColumnClient } from '../board/column-client'
import { TicketChat } from '../chat/chat-client'
import { FidelityProgressClient } from './fidelity-progress-client'
import { fixReportPrompt, fixRulePrompt, fixViolationPrompt, ReportClient } from './report-client'

const VALIDATE_COMMAND = '/actions-validate'
// Steps the board does itself rather than sending to a chat: a review is the person's own, opening the report while the
// fidelity has violations and recording the approval once it has none.
const STEPS_WITHOUT_CHAT = ['review']
const CLOSE_SESSION_COMMAND = '/space:session:close-session'

// Each fidelity's files by format, as its own files tool answers, by the fidelity's slug: a tile or panel over several
// fidelities reads them side by side.
export type FilesByFidelity = Record<string, NonNullable<Awaited<ReturnType<FidelityProgressClientGenerated['files']>>>>

const isBacklogItem = (moved: TicketData | BacklogItemData): moved is BacklogItemData => !('column' in moved)

// How far some of a ticket's work has got, as Python answers it for one fidelity's progress or for a stage's work taken
// together: what an action bar shows and allows.
export type WorkStanding = { actions: ActionStatesData; hasViolations: boolean; violationCount: number; allowedActions: string[] }

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
    return `${this.column.name}/${this.name}`
  }

  // Commands run in the active session, so with Active session only on, another ticket cannot start one.
  get isLocked(): boolean {
    return this.page.store.state.onlyActive && !this.isActive
  }

  get violatedSlugs(): string[] {
    return this.progress.filter(progress => progress.state === 'violations').map(progress => progress.fidelity.slug)
  }

  // Its progress on every fidelity the board requires, in stage order, each answering its own tools.
  get fidelityProgress(): FidelityProgressClient[] {
    return this.progress.map(progress => new FidelityProgressClient(progress, this))
  }

  // Its progress on the fidelities of a stage whose practices its session works on, in the order the stage requires them.
  progressIn(stage: ColumnClient): FidelityProgressClient[] {
    return this.fidelityProgress.filter(progress => progress.stage.name === stage.name && progress.isEnabled)
  }

  // Its progress on the fidelities a tile or a panel was opened over, read from this ticket as it is now.
  progressOn(fidelities: FidelityGuidanceData[]): FidelityProgressClient[] {
    return fidelities.flatMap(fidelity => this.progressNamed(fidelity.slug) ?? [])
  }

  // The data names a fidelity's progress by its slug, such as the ticket's next or a report rule's fidelity; this is
  // the one place such a name is turned into the progress.
  progressNamed(slug: string): FidelityProgressClient | undefined {
    return this.fidelityProgress.find(progress => progress.fidelity.slug === slug)
  }

  // The progress Run next works on: the one the ticket names as its next, none when it is done in its stage.
  get nextProgress(): FidelityProgressClient | undefined {
    return this.next ? this.progressNamed(this.next.fidelity.slug) : undefined
  }

  // Its work in a stage taken together, which a stage head's action bar shows and acts on.
  workIn(stage: ColumnClient): WorkStanding | undefined {
    const work = this.stageWork.find(entry => entry.stage.name === stage.name)
    return work && { actions: work.actions, hasViolations: work.has_violations, violationCount: work.violation_count, allowedActions: work.allowed_actions }
  }

  hasViolationsIn(stage: ColumnClient): boolean {
    return this.progress.some(progress => progress.state === 'violations' && progress.stage.name === stage.name)
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
    return this.nextProgress?.nextAction ?? ''
  }

  // The ticket's session, its practices, and its fidelities' progress each answer their own tools, built from the data
  // the ticket already holds.
  get sessionClient(): SessionClientGenerated {
    return new SessionClientGenerated(this.api, this.session)
  }

  practiceClient(practice: string): PracticeSessionOutputClientGenerated {
    return new PracticeSessionOutputClientGenerated(this.api, this.session.practices[practice] ?? null)
  }

  // The chat working on this ticket, which Python names, and every command the board sends for it goes to.
  get chat(): TicketChat {
    return new TicketChat(this.page.chat, this.name, this.workingChat)
  }

  // Each fidelity answers for its own files, so a tile or panel over several fidelities reads them side by side; none
  // when any read failed, because the page has already shown that failure.
  async filesOf(progress: FidelityProgressClient[]): Promise<FilesByFidelity | null> {
    const read = await Promise.all(progress.map(entry => entry.files()))
    if (read.some(files => !files)) return null
    return Object.fromEntries(progress.map((entry, index) => [entry.fidelity.slug, read[index]!]))
  }

  // One fidelity's latest report, or with none the violations of every fidelity of the ticket's stage.
  async reportOf(progress: FidelityProgressClient | null): Promise<ReportClient | null> {
    const report = await (progress ? progress.report() : this.violations())
    return report ? new ReportClient(report) : null
  }

  get nextStepName(): string {
    return this.nextAction === 'review' && this.nextProgress?.state === 'violations' ? 'review violations' : this.nextAction
  }

  get runNextLabel(): string {
    return this.next ? `Run next: ${this.nextStepName}` : 'Run next'
  }

  // The run-next icon's tooltip names the step and the fidelity it runs on, since the icon itself cannot.
  get runNextHint(): string {
    if (this.isLocked) return 'Activate this session to run its next step'
    if (!this.next) return 'Nothing to run next'
    return `${this.runNextLabel} on ${this.next.fidelity.slug}`
  }

  get nextNote(): string {
    return this.next ? `Next: ${this.next.fidelity.slug}, ${this.nextStepName}` : ''
  }

  get lockNote(): string {
    return this.isLocked ? 'Activate this session to run actions' : ''
  }

  // Python says which columns besides the stages take the ticket: the Backlog always, Complete only as it allows.
  canDropOn(edge: string): boolean {
    return this.dropTargets.includes(edge)
  }

  async dropOn(edge: string): Promise<void> {
    if (edge === 'Backlog') await this.moveTo('Backlog', false)
    else if (this.isActive) await this.page.activation.start(this, true)
    else await this.moveNext()
  }

  // Python sends every practice of the ticket's session with whether it works on it.
  isEnabled(practice: string): boolean {
    return this.session.practices[practice]?.enabled === true
  }

  select(): void {
    this.page.board.select(this.address)
  }

  // A person clicking the ticket: it opens in the details, and the board's commands go to its chat, the one working in its
  // worktree. With no chat there yet, a new one opens there, after the worktree when the ticket has none. A ticket in
  // Complete has closed its work, so it gets no new branch, worktree, or chat.
  async choose(): Promise<void> {
    this.select()
    const chat = this.chat
    const found = chat.found
    if (found) return this.page.chat.choose(found.id)
    if (this.isClosed || !chat.beginOpening()) return
    chat.start(await this.worktreeOpened())
  }

  private async worktreeOpened(): Promise<string> {
    if (this.worktree) return this.worktree
    const opened = await this.openWorktree()
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
    const name = this.page.board.practiceNamed(practice)?.name ?? practice
    this.page.store.toast(`${name} ${isEnabled ? 'on' : 'off'} for ${this.title} · saved to ${this.session.session_file}`)
    return true
  }

  private async review(progress: FidelityProgressClient): Promise<void> {
    await progress.finishReview()
    await this.page.reader.refresh()
  }

  // A command runs in whichever chat it is sent to, whose open session can be another ticket's, so every action command
  // names this ticket's session.json.
  actionCommand(command: string): string {
    return `${command} session=${this.session.session_file}`
  }

  fillSplit(): Promise<void> {
    return this.chat.fill(`Split ticket ${this.name} into child tickets, one per story on its story map: call ticket.create with parent ${this.name} for each story.`)
  }

  // Closing ends the chat's session and leaves the ticket where it is; moving it into Complete is what completes it.
  closeSession(): Promise<void> {
    return this.chat.command(CLOSE_SESSION_COMMAND)
  }

  fillHandoff(): Promise<void> {
    return this.chat.fill(`Write a handoff for ticket ${this.name} with /space-session-handoff-session.`)
  }

  // A report's fixes are for the ticket whose report it is, so they name its session and go to its chat.
  fixViolation(rule: ReportRuleData, violation: ViolationData): Promise<void> {
    return this.chat.command(this.actionCommand(fixViolationPrompt(rule, violation)))
  }

  fixRule(report: ReportClient, rule: ReportRuleData): Promise<void> {
    return this.chat.command(this.actionCommand(fixRulePrompt(report, rule)))
  }

  fixReport(report: ReportClient): Promise<void> {
    return this.chat.command(this.actionCommand(fixReportPrompt(report)))
  }

  // A report whose saved graph is out of date has lost its graph's rules, so its fidelity is validated again to find them.
  validateAgain(progress: FidelityProgressClient): Promise<void> {
    return this.chat.command(this.actionCommand(`${VALIDATE_COMMAND} ${progress.fidelity.slug}`))
  }

  get canRunNext(): boolean {
    if (!this.next || this.isLocked) return false
    return STEPS_WITHOUT_CHAT.includes(this.nextAction) || this.page.chat.canSend
  }

  // Python names the command for the next action. Generate is sent straight to the chat, in the format the fidelity
  // keeps; the others fill the prompt. A review is the person's own, made on the board.
  async runNext(): Promise<void> {
    const next = this.nextProgress
    if (!next) return
    if (this.nextAction === 'review' && next.state === 'violations') return this.page.panels.openReport(this, next)
    if (this.nextAction === 'review') return this.review(next)
    const command = this.actionCommand(next.nextCommand)
    if (this.nextAction !== 'generate') return this.chat.fill(command)
    await this.chat.command(command)
  }
}
