import { atom, read, update } from 'claude-code'
import type { EngineInterface } from 'claude-code'

import type { ActionStatesJson, ActivationJson, BoardJson, TicketFilesJson, TicketJson, TileJson, WorkspaceJson } from '../../types'
import { STATES } from './brand'
import { callTool, currentBoard, fillPrompt, refresh, runCommand } from './board-client'
import { violationsOf } from './ticket-summary'

const FIRST_LEAVING = ['commit', 'push']
const DEFAULT_ACTION = 'generate'

const openCard = atom({ plugin: 'cdd-board', key: 'openCard' } as const, null as string | null)
const tile = atom({ plugin: 'cdd-board', key: 'tile' } as const, null as TileJson | null, { shape: 'tile-1' })
const activation = atom({ plugin: 'cdd-board', key: 'activation' } as const, null as ActivationJson | null, { shape: 'activation-1' })

const guidanceSlug = (slug: string): string => slug.replaceAll('_', '-')

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

  get place(): string {
    const standing = this.isClosed ? '' : this.isDone ? 'done' : 'in progress'
    const origin = this.json.scope && this.json.parent ? `${this.json.scope} of ${this.json.parent}` : this.json.scope
    return [this.name, origin, this.column, standing].filter(Boolean).join(' · ')
  }

  get runNextLabel(): string {
    return this.next ? `Run next: ${this.nextAction} ${this.next}` : 'Run next'
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

  allows(slug: string, action: string): boolean {
    return (this.json.allowed_actions[slug] ?? []).includes(action)
  }

  reportOf(slug: string): string {
    return this.json.reports[slug] ?? ''
  }

  get firstReport(): string {
    return this.violations[0] ?? Object.keys(this.json.reports)[0] ?? ''
  }
}

export const ticketClients = (shown: BoardJson): TicketClient[] =>
  shown.columns.flatMap(column => [...(column.in_progress ?? []), ...(column.done ?? []), ...(column.tickets ?? [])]).map(json => new TicketClient(json))

export async function activeTicket($: EngineInterface): Promise<TicketClient | null> {
  const board = await currentBoard($)
  const json = board?.activeTicket
  return json ? new TicketClient(json) : null
}

export async function moveNext($: EngineInterface, ticket: string): Promise<void> {
  await callTool($, 'ticket.move_next', { ticket })
  await refresh($)
}

export async function movePrevious($: EngineInterface, ticket: string): Promise<void> {
  await callTool($, 'ticket.move_previous', { ticket })
  await refresh($)
}

export async function archive($: EngineInterface, ticket: TicketClient): Promise<void> {
  await callTool($, 'ticket.archive', { ticket: ticket.name })
  await refresh($)
}

export async function enablePractice($: EngineInterface, ticket: TicketClient, practice: string, isEnabled: boolean): Promise<void> {
  await callTool($, 'ticket.enable_practice', { ticket: ticket.name, practice, is_enabled: isEnabled })
  await refresh($)
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
  generate: '/actions-generate',
  validate: '/actions-validate',
  review: '/actions:review:review',
  satisfy: '/actions-satisfy',
}

export function fillRunNext($: EngineInterface, ticket: TicketClient) {
  return fillPrompt($, `${RUN_NEXT_COMMANDS[ticket.nextAction]} ${guidanceSlug(ticket.next ?? '')}`)
}

export function currentOpenCard($: EngineInterface) {
  return read($, openCard)
}

export function toggleCard($: EngineInterface, ticket: string) {
  return update($, openCard, open => (open === ticket ? null : ticket))
}

export function currentTile($: EngineInterface) {
  return read($, tile)
}

export async function openTile($: EngineInterface, ticket: string, stage: string, place: string, slugs: string[], isPinned: boolean): Promise<void> {
  const files = (await callTool<TicketFilesJson>($, 'ticket.files', { ticket })) ?? {}
  await update($, tile, () => ({ ticket, place, stage, slugs, action: DEFAULT_ACTION, picked: [], isPinned, files }))
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

export async function toggleTile($: EngineInterface, ticket: string, stage: string, place: string, slugs: string[]): Promise<void> {
  const open = await read($, tile)
  if (open?.place === place && open.isPinned) await closeTile($)
  else if (open?.place === place) await pinTile($)
  else await openTile($, ticket, stage, place, slugs, true)
}

export function chooseAction($: EngineInterface, action: string) {
  return update($, tile, open => (open ? { ...open, action, isPinned: true } : open))
}

export function toggleFormat($: EngineInterface, format: string) {
  return update($, tile, open =>
    open
      ? { ...open, isPinned: true, picked: open.picked.includes(format) ? open.picked.filter(entry => entry !== format) : [...open.picked, format] }
      : open,
  )
}

const slugsOf = (open: TileJson): string => open.slugs.map(guidanceSlug).join(' ')

// One command names every fidelity the tile acts on, so a stage's work stays a single turn.
export async function runTileAction($: EngineInterface, open: TileJson): Promise<void> {
  if (open.action === 'generate') {
    const commands = await callTool<string[]>($, 'ticket.generate_commands', { ticket: open.ticket, fidelities: open.slugs, formats: open.picked })
    for (const command of commands ?? []) await runCommand($, command)
    return
  }
  const formats = open.action === 'render' ? ` format=${open.picked.join(',')}` : ''
  await runCommand($, `/actions-${open.action} ${slugsOf(open)}${formats}`)
}

export function validateTile($: EngineInterface, open: TileJson) {
  return runCommand($, `/actions-validate ${slugsOf(open)}`)
}

export function reviewTile($: EngineInterface, open: TileJson) {
  return runCommand($, `/actions:review:review ${slugsOf(open)}`)
}

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
  const workspace = await callTool<WorkspaceJson>($, 'ticket.workspace', { ticket: ticket.name })
  const board = await currentBoard($)
  const leaving = isClosing ? ticket.title : board?.activeTicket?.title ?? ''
  await update($, activation, () => ({
    ticket: ticket.name,
    title: ticket.title,
    isClosing,
    leavingTitle: leaving,
    leaving: leaving ? FIRST_LEAVING : [],
    opening: workspace?.has_branch ? [] : ['branch'],
    workspace: workspace ?? { has_branch: false, has_worktree: false },
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

export async function confirmActivation($: EngineInterface, open: ActivationJson): Promise<void> {
  await update($, activation, () => null)
  if (open.isClosing) await callTool($, 'ticket.close', { ticket: open.ticket, leaving: open.leaving })
  else await callTool($, 'ticket.activate', { ticket: open.ticket, leaving: open.leaving, opening: open.opening })
  await refresh($)
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
