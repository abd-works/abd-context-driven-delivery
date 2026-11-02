import type { ActionStates, BacklogItem, Column, Ticket } from './board'
import { guidanceSlug, ticketAddress, violationsOf } from './board'
import { pathPart } from './board-api'
import { PRACTICES, practiceOf, STATES } from './board-brand'
import { itemAddress } from './board-client'
import type { BoardPage } from './board-page'

const RUN_NEXT_COMMANDS: Record<string, string> = {
  validate: '/actions-validate',
  review: '/actions:review:review',
  satisfy: '/actions-satisfy',
}

const isBacklogItem = (moved: Ticket | BacklogItem): moved is BacklogItem => !('column' in moved)

// The practice's skill for a fidelity: `clean_engineering-code` is /practices-clean-engineering-clean-engineering-code.
export const skillOf = (slug: string): string => `/practices-${guidanceSlug(practiceOf(slug)?.prefix ?? '')}${guidanceSlug(slug)}`

export interface TicketClient extends Ticket {}

// A ticket as the page knows it, with what a person can do to it.
export class TicketClient {
  constructor(
    json: Ticket,
    private readonly page: BoardPage,
  ) {
    Object.assign(this, json)
  }

  private get path(): string {
    return `/tickets/${pathPart(this.name)}`
  }

  get address(): string {
    return ticketAddress(this)
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

  get violations(): string[] {
    return violationsOf(this)
  }

  get standing(): string {
    return this.isClosed ? '' : this.is_done ? 'done' : 'in progress'
  }

  get place(): string {
    const origin = this.scope && this.parent ? `${this.scope} of ${this.parent}` : this.scope
    return [this.name, origin, this.column, this.standing].filter(Boolean).join(' · ')
  }

  get nextStepName(): string {
    return this.next_action === 'satisfy' ? 'fix violations' : this.next_action
  }

  get runNextLabel(): string {
    return this.next ? `Run next: ${this.nextStepName}` : 'Run next'
  }

  get footer(): string {
    const handoff = this.handoff ? `Latest handoff: ${this.handoff}` : 'No handoff yet'
    const next = this.next ? ` · Next: ${this.next}, ${this.nextStepName}` : ''
    return `${handoff}${next}${this.isLocked ? ' · Activate this session to run actions' : ''}`
  }

  get backLabel(): string {
    const isFirst = this.column === 'Discovery' && !this.is_done
    return `Move ${this.title} to ${isFirst ? 'the Backlog' : 'the previous column'}`
  }

  isEnabled(practice: string): boolean {
    return this.practices[practice] ?? true
  }

  stateOf(slug: string): { label: string; color: string; key: string } {
    const key = this.progress[slug] ?? 'not_started'
    return { ...STATES[key]!, key }
  }

  actionsOf(slug: string): ActionStates {
    return this.actions[slug] ?? { generate: 'to_do', validate: 'to_do', review: 'to_do' }
  }

  // How far one action has got across slugs: done only when it is done on all of them.
  standingOf(slugs: string[], action: keyof ActionStates): string {
    const states = slugs.map(slug => this.actionsOf(slug)[action])
    if (states.length && states.every(state => state === 'done')) return 'done'
    return states.some(state => state !== 'to_do') ? 'in_progress' : 'to_do'
  }

  violationCountOf(slugs: string[]): number {
    return slugs.reduce((total, slug) => total + (this.violation_counts[slug] ?? 0), 0)
  }

  enabledSlugs(stage: Column): string[] {
    return (stage.work_required ?? []).filter(slug => this.isEnabled(practiceOf(slug)?.key ?? ''))
  }

  allows(slug: string, action: string): boolean {
    return (this.allowed_actions[slug] ?? []).includes(action)
  }

  isNext(stage: Column, slug: string): boolean {
    return stage.name === this.column && this.next === slug
  }

  select(): void {
    this.page.board.select(this.address)
  }

  async moveNext(): Promise<void> {
    const moved = await this.page.api.post<Ticket>(`${this.path}/move-next`)
    await this.page.board.refresh()
    if (moved) await this.page.tiles.follow(new TicketClient(moved, this.page))
  }

  async movePrevious(): Promise<void> {
    const moved = await this.page.api.post<Ticket | BacklogItem>(`${this.path}/move-previous`)
    await this.page.board.refresh()
    if (!moved) return
    if (isBacklogItem(moved)) this.release(moved)
    else await this.page.tiles.follow(new TicketClient(moved, this.page))
  }

  // Moved to the Backlog, a ticket is off the board, so nothing stays open on it and its item is selected.
  private release(item: BacklogItem): void {
    this.page.tiles.releaseTicket(this.name)
    this.page.panels.closeTicketPanels(this.name)
    this.page.board.select(itemAddress(item))
  }

  async archive(): Promise<void> {
    await this.page.api.post(`${this.path}/archive`)
    await this.page.board.refresh()
  }

  async enablePractice(practice: string, isEnabled: boolean): Promise<void> {
    const saved = await this.page.api.post<Ticket>(`${this.path}/practice`, { practice, is_enabled: isEnabled })
    await this.page.board.refresh()
    if (!saved) return
    if (!isEnabled) this.page.tiles.dropPractice(this.name, practice)
    const name = PRACTICES.find(entry => entry.key === practice)?.name ?? practice
    this.page.store.toast(`${name} ${isEnabled ? 'on' : 'off'} for ${this.title} · saved to .sessions/${this.name}/session.json`)
  }

  fillSplit(): Promise<void> {
    return this.page.chat.fill(`Split ticket ${this.name} into child tickets, one per story on its story map: call ticket.new with parent ${this.name} for each story.`)
  }

  fillHandoff(): Promise<void> {
    return this.page.chat.fill(`Write a handoff for ticket ${this.name} with /space-handoff-handoff-session.`)
  }

  fillSatisfy(): Promise<void> {
    return this.page.chat.fill(`/actions-satisfy ${this.violations.map(guidanceSlug).join(' ')}`)
  }

  fillShowViolations(): Promise<void> {
    return this.page.chat.fill(`Show the violations on ${this.violations.map(guidanceSlug).join(' ')} for ticket ${this.name}.`)
  }

  // Violations hold a ticket, so the step is to fix them from the report, which needs no chat.
  get canRunNext(): boolean {
    if (!this.next || this.isLocked) return false
    return this.next_action === 'satisfy' || this.page.chat.canSend
  }

  // Generate can take two commands, a render and then the generate, so it runs them where the others fill the prompt.
  async runNext(): Promise<void> {
    const slug = this.next ?? ''
    if (this.next_action === 'satisfy') return this.page.panels.openReport(this.name, slug)
    if (this.next_action !== 'generate') return this.page.chat.fill(`${RUN_NEXT_COMMANDS[this.next_action]} ${guidanceSlug(slug)}`)
    const format = this.page.board.stageNamed(this.column)?.default_formats?.[slug]
    await this.page.tiles.runCommandsOf(this.name, [slug], format ? [format] : [])
  }
}
