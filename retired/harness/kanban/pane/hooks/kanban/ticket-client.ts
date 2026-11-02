import { atom, read, update } from 'claude-code'
import type { EngineInterface } from 'claude-code'

import type { ActionStatesJson, ActivationJson, BacklogItemJson, BoardJson, ColumnJson, TicketFilesJson, TicketJson, TileJson, WorkspaceJson } from '../../types'
import { practiceOf, PRACTICES, STATES } from './brand'
import { callTool, currentBoard, fillPrompt, itemAddress, refresh, runCommand, select, ticketAddress } from './board-client'
import { cardRowsOf, CARD_ROOM_ABOVE } from './board-layout'
import { closeTicketPanels } from './side-panel-client'
import { guidanceSlug, violationsOf } from './ticket-summary'
import { chosenFormats, defaultPicks } from './tile-formats'

const FIRST_LEAVING = ['commit', 'push']
const DEFAULT_ACTION = 'generate'
const ACTIONS_WITH_FORMATS = ['generate', 'render']
const LEFT_STEPS: Record<string, string> = { commit: 'committed', push: 'pushed', merge: 'merged to main' }
const OPENED_STEPS: Record<string, string> = { branch: 'branch created', worktree: 'worktree created' }

const openCard = atom({ plugin: 'cdd-board', key: 'openCard' } as const, null as string | null)
const tile = atom({ plugin: 'cdd-board', key: 'tile' } as const, null as TileJson | null, { shape: 'tile-2' })
const activation = atom({ plugin: 'cdd-board', key: 'activation' } as const, null as ActivationJson | null, { shape: 'activation-2' })
const cardOffset = atom({ plugin: 'cdd-board', key: 'cardOffset' } as const, 0)

// Mirrors the Python Ticket for display.
export class TicketClient {
  constructor(private readonly json: TicketJson) {}

  get name(): string {
    return this.json.name
  }

  get title(): string {
    return this.json.title
  }

  get scope(): string {
    return this.json.scope
  }

  get column(): string {
    return this.json.column
  }

  get address(): string {
    return `${this.json.column}/${this.json.name}`
  }

  get isClosed(): boolean {
    return this.json.column === 'Complete'
  }

  get isDone(): boolean {
    return this.json.is_done
  }

  get canMoveNext(): boolean {
    return this.json.can_move_next
  }

  get next(): string | null {
    return this.json.next
  }

  get nextAction(): string {
    return this.json.next_action
  }

  get lastActivity(): string {
    return this.json.last_activity
  }

  get handoff(): string {
    return this.json.handoff
  }

  get reports(): Record<string, string> {
    return this.json.reports
  }

  get violations(): string[] {
    return violationsOf(this.json)
  }

  violationCountOf(slugs: string[]): number {
    return slugs.reduce((total, slug) => total + (this.json.violation_counts[slug] ?? 0), 0)
  }

  get place(): string {
    const standing = this.isClosed ? '' : this.isDone ? 'done' : 'in progress'
    const origin = this.json.scope && this.json.parent ? `${this.json.scope} of ${this.json.parent}` : this.json.scope
    return [this.name, origin, this.column, standing].filter(Boolean).join(' · ')
  }

  get nextStepName(): string {
    return this.nextAction === 'satisfy' ? 'fix violations' : this.nextAction
  }

  get runNextLabel(): string {
    return this.next ? `Run next: ${this.nextStepName}` : 'Run next'
  }

  isEnabled(practice: string): boolean {
    return this.json.practices[practice] ?? true
  }

  stateOf(slug: string): { label: string; color: string; key: string } {
    const key = this.json.progress[slug] ?? 'not_started'
    return { ...STATES[key], key } as { label: string; color: string; key: string }
  }

  actionsOf(slug: string): ActionStatesJson {
    return this.json.actions[slug] ?? { generate: 'to_do', validate: 'to_do', review: 'to_do' }
  }

  // How far one action has got across slugs: done only when it is done on all of them.
  standingOf(slugs: string[], action: keyof ActionStatesJson): string {
    const states = slugs.map(slug => this.actionsOf(slug)[action])
    if (states.length && states.every(state => state === 'done')) return 'done'
    return states.some(state => state !== 'to_do') ? 'in_progress' : 'to_do'
  }

  enabledSlugs(stage: ColumnJson): string[] {
    return (stage.work_required ?? []).filter(slug => this.isEnabled(practiceOf(slug)?.key ?? ''))
  }

  allows(slug: string, action: string): boolean {
    return (this.json.allowed_actions[slug] ?? []).includes(action)
  }

  reportOf(slug: string): string {
    return this.json.reports[slug] ?? ''
  }
}

export const ticketClients = (shown: BoardJson): TicketClient[] =>
  shown.columns.flatMap(column => [...(column.in_progress ?? []), ...(column.done ?? []), ...(column.tickets ?? [])]).map(json => new TicketClient(json))

export async function activeTicket($: EngineInterface): Promise<TicketClient | null> {
  const board = await currentBoard($)
  const json = board?.activeTicket
  return json ? new TicketClient(json) : null
}

// A ticket's address changes with its column, so the selection and an open bar go with it: the bar to the tile the
// ticket works on next. The files are those the tile already read, because this action's one call was the move.
async function followTicket($: EngineInterface, moved: TicketJson): Promise<void> {
  const address = ticketAddress(moved)
  await select($, address)
  const open = await read($, tile)
  if (open?.ticket !== moved.name) return
  const ticket = new TicketClient(moved)
  const stage = (await currentBoard($))?.stageOf(moved)
  const slugs = stage ? ticket.enabledSlugs(stage) : []
  const slug = slugs.find(entry => ticket.stateOf(entry).key !== 'done') ?? slugs[0]
  if (!stage || !slug) return closeTile($)
  const place = `${open.place.startsWith('card/') ? 'card/' : ''}${address}/${slug}`
  await update($, tile, () => ({ ...open, place, stage: stage.name, slugs: [slug], action: DEFAULT_ACTION, picked: defaultPicks(stage, [slug], open.files), isPinned: true }))
}

// Moved to the Backlog, a ticket is off the board, so nothing stays open on it and its item is selected.
async function releaseTicket($: EngineInterface, ticket: string, item: BacklogItemJson): Promise<void> {
  await update($, openCard, shown => (shown === ticket ? null : shown))
  await update($, tile, open => (open?.ticket === ticket ? null : open))
  await closeTicketPanels($, ticket)
  await select($, itemAddress(item))
}

export async function moveNext($: EngineInterface, ticket: string): Promise<void> {
  const moved = await callTool<TicketJson>($, 'ticket.move_next', { ticket })
  await refresh($)
  if (moved) await followTicket($, moved)
}

export async function movePrevious($: EngineInterface, ticket: string): Promise<void> {
  const moved = await callTool<TicketJson | BacklogItemJson>($, 'ticket.move_previous', { ticket })
  await refresh($)
  if (!moved) return
  if ('column' in moved) await followTicket($, moved)
  else await releaseTicket($, ticket, moved)
}

export async function archive($: EngineInterface, ticket: TicketClient): Promise<void> {
  await callTool($, 'ticket.archive', { ticket: ticket.name })
  await refresh($)
}

export async function enablePractice($: EngineInterface, ticket: TicketClient, practice: string, isEnabled: boolean): Promise<void> {
  const saved = await callTool<TicketJson>($, 'ticket.enable_practice', { ticket: ticket.name, practice, is_enabled: isEnabled })
  await refresh($)
  if (!saved) return
  if (!isEnabled) await dropPracticeFromTile($, ticket.name, practice)
  const name = PRACTICES.find(entry => entry.key === practice)?.name ?? practice
  $.ui.toast(`${name} ${isEnabled ? 'on' : 'off'} for ${ticket.title} · saved to .sessions/${ticket.name}/session.json`)
}

// A practice turned off has no tile to act on, so an open bar lets go of it.
function dropPracticeFromTile($: EngineInterface, ticket: string, practice: string) {
  return update($, tile, open => {
    if (open?.ticket !== ticket) return open
    const slugs = open.slugs.filter(slug => practiceOf(slug)?.key !== practice)
    return slugs.length ? { ...open, slugs } : null
  })
}

export function openNewTicket($: EngineInterface) {
  return fillPrompt($, 'Open a new ticket with ticket.new, titled: ')
}

export function fillSplit($: EngineInterface, ticket: TicketClient) {
  return fillPrompt($, `Split ticket ${ticket.name} into child tickets, one per story on its story map: call ticket.new with parent ${ticket.name} for each story.`)
}

export function fillHandoff($: EngineInterface, ticket: TicketClient) {
  return fillPrompt($, `Write a handoff for ticket ${ticket.name} with /space-handoff-handoff-session.`)
}

const RUN_NEXT_COMMANDS: Record<string, string> = {
  validate: '/actions-validate',
  review: '/actions:review:review',
  satisfy: '/actions-satisfy',
}

async function runCommandsOf($: EngineInterface, ticket: string, fidelities: string[], formats: string[]): Promise<void> {
  const commands = await callTool<string[]>($, 'ticket.generate_commands', { ticket, fidelities, formats })
  for (const command of commands ?? []) await runCommand($, command)
}

// Generate can take two commands, a render and then the generate, so it runs them where the others fill the prompt.
export async function runNext($: EngineInterface, ticket: TicketClient): Promise<void> {
  const slug = ticket.next ?? ''
  if (ticket.nextAction !== 'generate') return fillPrompt($, `${RUN_NEXT_COMMANDS[ticket.nextAction]} ${guidanceSlug(slug)}`).then(() => undefined)
  const stage = (await currentBoard($))?.stages.find(entry => entry.name === ticket.column)
  await runCommandsOf($, ticket.name, [slug], chosenDefault(stage, slug))
}

const chosenDefault = (stage: ColumnJson | undefined, slug: string): string[] => {
  const format = stage?.default_formats?.[slug]
  return format ? [format] : []
}

export function currentOpenCard($: EngineInterface) {
  return read($, openCard)
}

// A card opens with its action bar ready, over all its fidelities, so generating needs no hover first.
export async function toggleCard($: EngineInterface, ticket: string, stage: string, place: string, slugs: string[]): Promise<void> {
  const wasOpen = (await read($, openCard)) === ticket
  await select($, place)
  await update($, cardOffset, () => 0)
  await update($, openCard, () => (wasOpen ? null : ticket))
  if (wasOpen) await closeTile($)
  else await openTile($, ticket, stage, `card/${place}/menu`, slugs, true)
}

export function currentCardOffset($: EngineInterface) {
  return read($, cardOffset)
}

// The rows the opened card is expected to take, with the bar when it is open on the card.
export function expandedCardRows(ticket: TicketClient, stage: ColumnJson, open: TileJson | null): number {
  const isOnCard = open?.place.startsWith(`card/${ticket.address}/`) ?? false
  return cardRowsOf(ticket.enabledSlugs(stage).length, isOnCard)
}

export const cardScrollLimit = (cardRows: number, bodyRows: number): number => Math.max(cardRows + CARD_ROOM_ABOVE - bodyRows, 0)

// The wheel moves an opened card that is taller than the pane. A card that fits leaves the wheel to the board.
export async function scrollCard($: EngineInterface, by: number, bodyRows: number): Promise<boolean> {
  const name = await read($, openCard)
  const board = await currentBoard($)
  const json = name ? board?.ticketNamed(name) : undefined
  const stage = json ? board?.stageOf(json) : undefined
  if (!json || !stage) return false
  const limit = cardScrollLimit(expandedCardRows(new TicketClient(json), stage, await read($, tile)), bodyRows)
  if (!limit) return false
  await update($, cardOffset, offset => Math.min(Math.max(offset + by, 0), limit))
  return true
}

export function currentTile($: EngineInterface) {
  return read($, tile)
}

export async function openTile($: EngineInterface, ticket: string, stage: string, place: string, slugs: string[], isPinned: boolean): Promise<void> {
  const files = (await callTool<TicketFilesJson>($, 'ticket.files', { ticket, fidelities: slugs })) ?? {}
  const column = (await currentBoard($))?.stages.find(entry => entry.name === stage)
  const picked = column ? defaultPicks(column, slugs, files) : []
  await update($, tile, () => ({ ticket, place, stage, slugs, action: DEFAULT_ACTION, picked, isPinned, files }))
}

// A hover only looks, so it leaves a bar a person pressed open, such as an opened card's.
export async function hoverTile($: EngineInterface, ticket: string, stage: string, place: string, slugs: string[]): Promise<void> {
  if (!(await read($, tile))?.isPinned) await openTile($, ticket, stage, place, slugs, false)
}

// What a tile shows was generated can change under it, so it is read again with the board.
export async function reloadTile($: EngineInterface): Promise<void> {
  const open = await read($, tile)
  if (!open) return
  const files = await callTool<TicketFilesJson>($, 'ticket.files', { ticket: open.ticket, fidelities: open.slugs })
  if (files) await update($, tile, entry => (entry?.ticket === open.ticket ? { ...entry, files } : entry))
}

export function closeTile($: EngineInterface) {
  return update($, tile, () => null)
}

export function pinTile($: EngineInterface) {
  return update($, tile, open => (open ? { ...open, isPinned: true } : open))
}

export async function leaveTile($: EngineInterface, place: string): Promise<void> {
  const open = await read($, tile)
  if (open?.place === place && !open.isPinned) await closeTile($)
}

const addressOfPlace = (place: string): string => place.replace(/^card\//, '').split('/').slice(0, 2).join('/')

// Closing a tile on an opened card gives the bar back to the whole card.
export async function toggleTile($: EngineInterface, ticket: string, stage: string, place: string, slugs: string[], menuSlugs: string[] = []): Promise<void> {
  await select($, addressOfPlace(place))
  const open = await read($, tile)
  if (open?.place === place && open.isPinned && menuSlugs.length) await openTile($, ticket, stage, place.replace(/[^/]*$/, 'menu'), menuSlugs, true)
  else if (open?.place === place && open.isPinned) await closeTile($)
  else if (open?.place === place) await pinTile($)
  else await openTile($, ticket, stage, place, slugs, true)
}

export function chooseAction($: EngineInterface, action: string) {
  return update($, tile, open => (open ? { ...open, action, isPinned: true } : open))
}

export function toggleFormats($: EngineInterface, chip: string) {
  return update($, tile, open => {
    if (!open) return open
    const isOn = open.picked.includes(chip)
    return { ...open, isPinned: true, picked: isOn ? open.picked.filter(entry => entry !== chip) : [...open.picked, chip] }
  })
}

const slugsOf = (open: TileJson): string => open.slugs.map(guidanceSlug).join(' ')

// One command names every fidelity the tile acts on, so a stage's work stays a single turn.
export async function runTileAction($: EngineInterface, open: TileJson, stage: ColumnJson): Promise<void> {
  if (!ACTIONS_WITH_FORMATS.includes(open.action)) return runCommand($, `/actions-${open.action} ${slugsOf(open)}`)
  const formats = chosenFormats(stage, open.slugs, open.picked)
  await update($, tile, entry => (entry ? { ...entry, picked: [] } : entry))
  if (open.action === 'generate') await runCommandsOf($, open.ticket, open.slugs, formats)
  else await runCommand($, `/actions-render ${slugsOf(open)} format=${formats.join(',')}`)
}

export function validateTile($: EngineInterface, open: TileJson) {
  return runCommand($, `/actions-validate ${slugsOf(open)}`)
}

export function reviewTile($: EngineInterface, open: TileJson) {
  return runCommand($, `/actions:review:review ${slugsOf(open)}`)
}

// location names the file and its line.
export function fixViolation($: EngineInterface, fidelity: string, rule: string, location: string) {
  return runCommand($, `/actions-satisfy ${guidanceSlug(fidelity)} ${location} rule ${rule}`)
}

export function fixRule($: EngineInterface, fidelity: string, rule: string) {
  return runCommand($, `/actions-satisfy ${guidanceSlug(fidelity)} rule ${rule}`)
}

export function fillSatisfy($: EngineInterface, ticket: TicketClient) {
  return fillPrompt($, `/actions-satisfy ${ticket.violations.map(guidanceSlug).join(' ')}`)
}

export function fillShowViolations($: EngineInterface, ticket: TicketClient) {
  return fillPrompt($, `Show the violations on ${ticket.violations.map(guidanceSlug).join(' ')} for ticket ${ticket.name}.`)
}

export function currentActivation($: EngineInterface) {
  return read($, activation)
}

export async function openActivation($: EngineInterface, ticket: TicketClient, isClosing: boolean): Promise<void> {
  await select($, ticket.address)
  const workspace = await callTool<WorkspaceJson>($, 'ticket.workspace', { ticket: ticket.name })
  const board = await currentBoard($)
  const leaving = isClosing ? ticket.title : board?.activeTicket?.title ?? ''
  await update($, activation, () => ({
    ticket: ticket.name,
    title: ticket.title,
    isClosing,
    leavingTitle: leaving,
    leaving: workspace?.leaving_has_branch ? FIRST_LEAVING : [],
    opening: workspace?.has_branch ? [] : ['branch'],
    workspace: workspace ?? { has_branch: false, has_worktree: false, leaving_has_branch: false },
  }))
}

export function cancelActivation($: EngineInterface) {
  return update($, activation, () => null)
}

const toggled = (chosen: string[], option: string): string[] =>
  chosen.includes(option) ? chosen.filter(entry => entry !== option) : [...chosen, option]

export function toggleLeaving($: EngineInterface, option: string) {
  return update($, activation, open => (open ? { ...open, leaving: toggled(open.leaving, option) } : open))
}

export function toggleOpening($: EngineInterface, option: string) {
  return update($, activation, open => (open ? { ...open, opening: toggled(open.opening, option) } : open))
}

const stepsOf = (steps: Record<string, string>, chosen: string[]): string[] => Object.keys(steps).filter(step => chosen.includes(step)).map(step => steps[step] ?? step)

// What leaving did, in the canvas's words, ahead of what came of the session.
function reportActivation($: EngineInterface, open: ActivationJson, outcome: string, opened: string[]): void {
  const left = stepsOf(LEFT_STEPS, open.leaving)
  const reports = [left.length ? `${open.leavingTitle}: ${left.join(', ')}` : '', opened.length ? `${open.title}: ${opened.join(', ')}` : '', outcome]
  $.ui.toast(reports.filter(Boolean).join(' · '))
}

async function closeSession($: EngineInterface, open: ActivationJson): Promise<void> {
  const closed = await callTool<TicketJson>($, 'ticket.close', { ticket: open.ticket, leaving: open.leaving })
  await refresh($)
  if (!closed) return
  await select($, ticketAddress(closed))
  reportActivation($, open, `Session ${open.title} closed`, [])
}

async function activateSession($: EngineInterface, open: ActivationJson): Promise<void> {
  const activated = await callTool<TicketJson>($, 'ticket.activate', { ticket: open.ticket, leaving: open.leaving, opening: open.opening })
  await refresh($)
  if (activated) reportActivation($, open, `${open.title} is now active`, stepsOf(OPENED_STEPS, open.opening))
}

export async function confirmActivation($: EngineInterface, open: ActivationJson): Promise<void> {
  await update($, activation, () => null)
  await (open.isClosing ? closeSession($, open) : activateSession($, open))
}

// The command line's way in, which asks nothing first.
export async function closeNamed($: EngineInterface, ticket: string): Promise<void> {
  await callTool($, 'ticket.close', { ticket })
  await refresh($)
}

export async function activateNamed($: EngineInterface, ticket: string): Promise<void> {
  await callTool($, 'ticket.activate', { ticket })
  await refresh($)
}
