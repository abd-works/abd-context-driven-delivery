import type { BacklogItemData } from '@cdd/space/kanban/backlog-item'
import type { FidelityGuidanceData } from '@cdd/space/kanban/board'
import { FidelityProgressClientGenerated, type ActionStatesData, type FidelityProgressData } from '@cdd/space/kanban/fidelity-progress'
import { TicketClientGenerated, type ReportRuleData, type TicketData, type ViolationData } from '@cdd/space/kanban/ticket'
import { PracticeSessionOutputClientGenerated } from '@cdd/space/session/practice-session-output'
import { SessionClientGenerated } from '@cdd/space/session/session'

import { STATES, WORK_LIGHT } from '../board/board-brand'
import type { BoardPage } from '../board/board-page'
import type { ColumnClient } from '../board/column-client'
import { TicketChat } from '../chat/chat-client'
import { fixReportPrompt, fixRulePrompt, fixViolationPrompt, ReportClient } from './report-client'

const RUN_NEXT_COMMANDS: Record<string, string> = {
  validate: '/actions-validate',
  satisfy: '/actions-satisfy',
}
// Steps the board does itself rather than sending to a chat: fixing violations opens the report, and a review is the
// person's own approval.
const STEPS_WITHOUT_CHAT = ['satisfy', 'review']
const CLOSE_SESSION_COMMAND = '/space:session:close-session'

// Each fidelity's files by format, as its own files tool answers, by the fidelity's slug: a tile or panel over several
// fidelities reads them side by side.
export type FilesByFidelity = Record<string, NonNullable<Awaited<ReturnType<FidelityProgressClientGenerated['files']>>>>

const isBacklogItem = (moved: TicketData | BacklogItemData): moved is BacklogItemData => !('column' in moved)

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
    return this.progress.filter(progress => progress.state === 'violations').map(progress => progress.slug)
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
    return this.next?.next_action ?? ''
  }

  // The ticket's session, its practices, and its fidelities' progress each answer their own tools, built from the data
  // the ticket already holds.
  get sessionClient(): SessionClientGenerated {
    return new SessionClientGenerated(this.api, this.session)
  }

  practiceClient(practice: string): PracticeSessionOutputClientGenerated {
    return new PracticeSessionOutputClientGenerated(this.api, this.session.practices[practice] ?? null)
  }

  progressNamed(slug: string): FidelityProgressData | undefined {
    return this.progress.find(progress => progress.slug === slug)
  }

  // Python sends progress for every fidelity the board requires, so a fidelity the ticket has none for is a page bug.
  progressOf(slug: string): FidelityProgressData {
    const progress = this.progressNamed(slug)
    if (!progress) throw new Error(`ticket ${this.name} has no progress on ${slug}`)
    return progress
  }

  progressClient(slug: string): FidelityProgressClientGenerated {
    return new FidelityProgressClientGenerated(this.api, this.progressOf(slug))
  }

  // The chat working on this ticket, which every command the board sends for it goes to.
  get chat(): TicketChat {
    return new TicketChat(this.page.chat, this)
  }

  // Each fidelity answers for its own files, so a tile or panel over several fidelities reads them side by side; none
  // when any read failed, because the page has already shown that failure.
  async filesOf(slugs: string[]): Promise<FilesByFidelity | null> {
    const read = await Promise.all(slugs.map(slug => this.progressClient(slug).files()))
    if (read.some(files => !files)) return null
    return Object.fromEntries(slugs.map((slug, index) => [slug, read[index]!]))
  }

  // One fidelity's latest report, or with no fidelity the violations of every fidelity of the ticket's stage.
  async reportOf(fidelity: string): Promise<ReportClient | null> {
    const report = await (fidelity ? this.progressClient(fidelity).report() : this.violations())
    return report ? new ReportClient(report) : null
  }

  get nextStepName(): string {
    return this.nextAction === 'satisfy' ? 'fix violations' : this.nextAction
  }

  get runNextLabel(): string {
    return this.next ? `Run next: ${this.nextStepName}` : 'Run next'
  }

  // The run-next icon's tooltip names the step and the fidelity it runs on, since the icon itself cannot.
  get runNextHint(): string {
    if (this.isLocked) return 'Activate this session to run its next step'
    if (!this.next) return 'Nothing to run next'
    return `${this.runNextLabel} on ${this.next.slug}`
  }

  get nextNote(): string {
    return this.next ? `Next: ${this.next.slug}, ${this.nextStepName}` : ''
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

  isEnabled(practice: string): boolean {
    return this.session.practices[practice]?.enabled ?? true
  }

  // Whether the ticket's session works on the practice of the fidelity slug names.
  isOn(slug: string): boolean {
    return this.progressOf(slug).is_enabled
  }

  stateOf(slug: string): { label: string; color: string; key: string } {
    const key = this.progressNamed(slug)?.state ?? 'not_started'
    return { ...STATES[key]!, key }
  }

  lightOf(slug: string): number {
    return this.isOn(slug) ? WORK_LIGHT[this.stateOf(slug).key]! : WORK_LIGHT.off!
  }

  actionsOf(slug: string): ActionStatesData {
    return this.progressOf(slug).actions
  }

  // How far one action has got across slugs: done only when it is done on all of them.
  standingOf(slugs: string[], action: keyof ActionStatesData): string {
    const states = slugs.map(slug => this.actionsOf(slug)[action])
    if (states.length && states.every(state => state === 'done')) return 'done'
    return states.some(state => state !== 'to_do') ? 'in_progress' : 'to_do'
  }

  violationCountOf(slugs: string[]): number {
    return slugs.reduce((total, slug) => total + (this.progressNamed(slug)?.violation_count ?? 0), 0)
  }

  enabledFidelities(stage: ColumnClient): FidelityGuidanceData[] {
    return stage.workRequired.filter(fidelity => this.isOn(fidelity.slug))
  }

  allows(slug: string, action: string): boolean {
    return (this.progressNamed(slug)?.allowed_actions ?? []).includes(action)
  }

  isNext(stage: ColumnClient, fidelity: FidelityGuidanceData): boolean {
    return this.next?.slug === fidelity.slug && this.next.stage.name === stage.name
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

  get canRunNext(): boolean {
    if (!this.next || this.isLocked) return false
    return STEPS_WITHOUT_CHAT.includes(this.nextAction) || this.page.chat.canSend
  }

  // Generate is sent straight to the chat, in the next fidelity's default format; the others fill the prompt.
  async runNext(): Promise<void> {
    const slug = this.next?.slug ?? ''
    if (this.nextAction === 'satisfy') return this.page.panels.openReport(this, slug)
    if (this.nextAction === 'review') return this.review(slug)
    if (this.nextAction !== 'generate') return this.chat.fill(this.actionCommand(`${RUN_NEXT_COMMANDS[this.nextAction]} ${slug}`))
    const format = this.next?.fidelity.default_format
    await this.chat.command(this.actionCommand(`/actions-generate ${slug}${format ? ` format=${format}` : ''}`))
  }
}
