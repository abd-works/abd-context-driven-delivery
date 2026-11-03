import type { BacklogItemData } from '@cdd/harness/kanban/backlog-item'
import { TicketClientGenerated, type ActionStatesData, type TicketData } from '@cdd/harness/kanban/ticket'

import { guidanceSlug, PRACTICES, practiceOf, STATES, WORK_LIGHT } from '../board/board-brand'
import type { BoardPage } from '../board/board-page'
import type { ColumnClient } from '../board/column-client'

const RUN_NEXT_COMMANDS: Record<string, string> = {
  validate: '/actions-validate',
  review: '/actions:review:review',
  satisfy: '/actions-satisfy',
}

const isBacklogItem = (moved: TicketData | BacklogItemData): moved is BacklogItemData => !('column' in moved)

// The practice's skill for a fidelity: `clean_engineering-code` is /practices-clean-engineering-clean-engineering-code.
export const skillOf = (slug: string): string => `/practices-${guidanceSlug(practiceOf(slug)?.prefix ?? '')}${guidanceSlug(slug)}`

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
      .filter(([, state]) => state === 'violations')
      .map(([slug]) => slug)
  }

  get standing(): string {
    return this.isClosed ? '' : this.isDone ? 'done' : 'in progress'
  }

  get place(): string {
    const origin = this.scope && this.parent ? `${this.scope} of ${this.parent}` : this.scope
    return [this.name, origin, this.column, this.standing].filter(Boolean).join(' · ')
  }

  get nextStepName(): string {
    return this.nextAction === 'satisfy' ? 'fix violations' : this.nextAction
  }

  get runNextLabel(): string {
    return this.next ? `Run next: ${this.nextStepName}` : 'Run next'
  }

  get footer(): string {
    const handoff = this.handoff ? `Latest handoff: ${this.handoff}` : 'No handoff yet'
    const next = this.next ? ` · Next: ${this.next}, ${this.nextStepName}` : ''
    return `${handoff}${next}${this.isLocked ? ' · Activate this session to run actions' : ''}`
  }

  // The Backlog and Complete take a dropped card only where a move there means something: back to the Backlog from
  // Discovery's In progress, and into Complete from Implementation's Done, or the active ticket through its Close dialog,
  // because closing it asks what to do with its work.
  canDropOn(edge: string): boolean {
    if (edge === 'Backlog') return this.column === 'Discovery' && !this.isDone
    if (edge === 'Complete') return this.isActive || (this.column === 'Implementation' && this.isDone)
    return false
  }

  async dropOn(edge: string): Promise<void> {
    if (edge === 'Backlog') await this.movePrevious()
    else if (this.isActive) await this.page.activation.start(this, true)
    else await this.moveNext()
  }

  isEnabled(practice: string): boolean {
    return this.practices[practice] ?? true
  }

  stateOf(slug: string): { label: string; color: string; key: string } {
    const key = this.progress[slug] ?? 'not_started'
    return { ...STATES[key]!, key }
  }

  lightOf(slug: string): number {
    return this.isEnabled(practiceOf(slug)?.key ?? '') ? WORK_LIGHT[this.stateOf(slug).key]! : WORK_LIGHT.off!
  }

  actionsOf(slug: string): ActionStatesData {
    return this.actions[slug] ?? { generate: 'to_do', validate: 'to_do', review: 'to_do' }
  }

  // How far one action has got across slugs: done only when it is done on all of them.
  standingOf(slugs: string[], action: keyof ActionStatesData): string {
    const states = slugs.map(slug => this.actionsOf(slug)[action])
    if (states.length && states.every(state => state === 'done')) return 'done'
    return states.some(state => state !== 'to_do') ? 'in_progress' : 'to_do'
  }

  violationCountOf(slugs: string[]): number {
    return slugs.reduce((total, slug) => total + (this.violationCounts[slug] ?? 0), 0)
  }

  enabledSlugs(stage: ColumnClient): string[] {
    return stage.workRequired.filter(slug => this.isEnabled(practiceOf(slug)?.key ?? ''))
  }

  allows(slug: string, action: string): boolean {
    return (this.allowedActions[slug] ?? []).includes(action)
  }

  isNext(stage: ColumnClient, slug: string): boolean {
    return stage.name === this.column && this.next === slug
  }

  select(): void {
    this.page.board.select(this.address)
  }

  override async moveNext(): Promise<this | null> {
    return this.followed(await super.moveNext())
  }

  override async moveTo(stage: string, done?: boolean): Promise<this | null> {
    return this.followed(await super.moveTo(stage, done))
  }

  // The card stays open on the ticket wherever it moved.
  private async followed(moved: this | null): Promise<this | null> {
    await this.page.reader.refresh()
    if (moved) await this.page.cards.follow(this.page.ticket(moved.toJSON()))
    return moved
  }

  override async movePrevious(): Promise<TicketData | BacklogItemData | null> {
    const moved = await super.movePrevious()
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

  override async archive(): Promise<this | null> {
    const archived = await super.archive()
    await this.page.reader.refresh()
    return archived
  }

  override async enablePractice(practice: string, isEnabled: boolean): Promise<this | null> {
    const saved = await super.enablePractice(practice, isEnabled)
    await this.page.reader.refresh()
    if (!saved) return null
    if (!isEnabled) this.page.cards.dropPractice(this.name, practice)
    const name = PRACTICES.find(entry => entry.key === practice)?.name ?? practice
    this.page.store.toast(`${name} ${isEnabled ? 'on' : 'off'} for ${this.title} · saved to .sessions/${this.name}/session.json`)
    return saved
  }

  fillSplit(): Promise<void> {
    return this.page.chat.fill(`Split ticket ${this.name} into child tickets, one per story on its story map: call ticket.new with parent ${this.name} for each story.`)
  }

  fillHandoff(): Promise<void> {
    return this.page.chat.fill(`Write a handoff for ticket ${this.name} with /space-handoff-handoff-session.`)
  }

  fillSatisfy(): Promise<void> {
    return this.page.chat.fill(`/actions-satisfy ${this.violatedSlugs.map(guidanceSlug).join(' ')}`)
  }

  fillShowViolations(): Promise<void> {
    return this.page.chat.fill(`Show the violations on ${this.violatedSlugs.map(guidanceSlug).join(' ')} for ticket ${this.name}.`)
  }

  // Violations hold a ticket, so the step is to fix them from the report, which needs no chat.
  get canRunNext(): boolean {
    if (!this.next || this.isLocked) return false
    return this.nextAction === 'satisfy' || this.page.chat.canSend
  }

  // Generate can take two commands, a render and then the generate, so it runs them where the others fill the prompt.
  async runNext(): Promise<void> {
    const slug = this.next ?? ''
    if (this.nextAction === 'satisfy') return this.page.panels.openReport(this.name, slug)
    if (this.nextAction !== 'generate') return this.page.chat.fill(`${RUN_NEXT_COMMANDS[this.nextAction]} ${guidanceSlug(slug)}`)
    const format = this.page.board.stageNamed(this.column)?.defaultFormats[slug]
    await this.page.tileActions.runCommandsOf(this.name, [slug], format ? [format] : [])
  }
}
