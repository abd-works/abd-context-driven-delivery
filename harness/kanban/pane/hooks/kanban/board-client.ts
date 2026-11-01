import { atom, read, update } from 'claude-code'
import type { EngineInterface } from 'claude-code'

import type { BacklogItemJson, BoardJson, ColumnJson, SplitLayoutJson, TicketJson } from '../../types'
import { activeTicketJson, allTickets, statusOf, ticketsOf } from './ticket-summary'

const SERVER = 'cdd'
const ITEM_COLUMN = 'Backlog'

// Change the tag when the board's shape changes: it declines what an earlier version stored.
const board = atom({ plugin: 'cdd-board', key: 'board' } as const, null as BoardJson | null, { shape: 'board-3' })
const selected = atom({ plugin: 'cdd-board', key: 'selected' } as const, null as string | null)
const splitLayout = atom({ plugin: 'cdd-board', key: 'splitLayout' } as const, { expanded: null, boardRows: null } as SplitLayoutJson)
const surfaceModulesFailed = atom({ plugin: 'cdd-board', key: 'surfaceModulesFailed' } as const, false)
const onlyActive = atom({ plugin: 'cdd-board', key: 'onlyActive' } as const, true)
const columnOffset = atom({ plugin: 'cdd-board', key: 'columnOffset' } as const, 0)

// A session can sit in closed/ under the name of an open one, so a column and name together say which ticket is meant.
export const ticketAddress = (ticket: TicketJson): string => `${ticket.column}/${ticket.name}`
export const itemAddress = (item: BacklogItemJson): string => `${ITEM_COLUMN}/${item.title}`

// Mirrors the Python Board for display.
export class BoardClient {
  constructor(private readonly json: BoardJson) {}

  get project(): string {
    return this.json.project
  }

  get active(): string | null {
    return this.json.active
  }

  get columns(): ColumnJson[] {
    return this.json.columns
  }

  get stages(): ColumnJson[] {
    return this.json.columns.filter(column => column.work_required)
  }

  get tickets(): TicketJson[] {
    return allTickets(this.json)
  }

  get ticketCount(): number {
    return new Set(this.tickets.map(ticket => ticket.name)).size
  }

  get backlogItems(): BacklogItemJson[] {
    return this.json.columns.flatMap(column => column.items ?? [])
  }

  get activeTicket(): TicketJson | undefined {
    return activeTicketJson(this.json)
  }

  get latestTicket(): TicketJson | undefined {
    return [...this.tickets].sort((one, other) => other.last_activity.localeCompare(one.last_activity))[0]
  }

  itemAt(address: string | null): BacklogItemJson | undefined {
    return this.backlogItems.find(item => itemAddress(item) === address)
  }

  ticketAt(address: string | null): TicketJson | undefined {
    return this.tickets.find(ticket => ticketAddress(ticket) === address)
  }

  ticketNamed(name: string): TicketJson | undefined {
    return this.tickets.find(ticket => ticket.name === name)
  }

  countOf(column: ColumnJson): number {
    return column.items ? column.items.length : ticketsOf(column).length
  }

  // The stage whose fidelities a ticket shows: Complete keeps showing Implementation's.
  stageOf(ticket: TicketJson): ColumnJson | undefined {
    return this.stages.find(stage => stage.name === ticket.column) ?? this.stages.at(-1)
  }

  allSlugs(): string[] {
    return this.stages.flatMap(stage => stage.work_required ?? [])
  }
}

// The mod's only MCP call, so a failure is shown to the person in one place.
export async function callTool<T>($: EngineInterface, tool: string, args: Record<string, unknown>): Promise<T | null> {
  let result
  try {
    result = await $.mcp.call(SERVER, tool, args)
  } catch (failure) {
    // The cdd server is not connected: say so on the status line rather than fail the hook.
    $.ui.status(`cdd board: ${String(failure)}`)
    return null
  }
  const text = result.content[0]?.text
  if (result.isError || text === undefined) {
    $.ui.toast(`cdd ${tool} failed${text ? `: ${text}` : ''}`)
    return null
  }
  return JSON.parse(text) as T
}

function announceChanges($: EngineInterface, before: BoardJson | null, after: BoardJson): void {
  if (!before) return
  const earlier = new Map(allTickets(before).map(ticket => [ticket.name, ticket]))
  const named = allTickets(after).map(ticket => ticket.name)
  for (const ticket of allTickets(after)) {
    const was = earlier.get(ticket.name)
    // A name held by an open and a closed session cannot be compared across reads, so it announces nothing.
    if (!was || named.indexOf(ticket.name) !== named.lastIndexOf(ticket.name)) continue
    if (was.column !== ticket.column) $.ui.toast(`${ticket.name} moved to ${ticket.column}`)
    for (const [slug, state] of Object.entries(ticket.progress)) {
      if (state === 'done' && was.progress[slug] !== 'done') $.ui.toast(`${slug} reviewed on ${ticket.name}`)
    }
  }
}

export async function refresh($: EngineInterface): Promise<void> {
  const shown = await callTool<BoardJson>($, 'board.show', {})
  if (!shown) return
  const before = await read($, board)
  await update($, board, () => shown)
  announceChanges($, before, shown)
  const active = activeTicketJson(shown)
  $.ui.status(active ? statusOf(active) : undefined)
  // The system prompt is cached; when the active ticket's summary changes, it is composed again next turn.
  const wasActive = before ? activeTicketJson(before) : undefined
  if (!before || (wasActive ? statusOf(wasActive) : '') !== (active ? statusOf(active) : '')) {
    await $.ui.invalidate('prompt.section')
  }
}

export async function currentBoard($: EngineInterface): Promise<BoardClient | null> {
  const shown = await read($, board)
  return shown ? new BoardClient(shown) : null
}

export function fillPrompt($: EngineInterface, text: string) {
  return $.prompt.fill({ text, mode: 'replace' })
}

// A prompt that starts with / is a command, which the engine runs only through $.command.run.
export async function runCommand($: EngineInterface, line: string): Promise<void> {
  const [name = '', ...words] = line.slice(1).split(' ')
  try {
    await $.command.run({ command: name, args: words.join(' ') })
  } catch (failure) {
    $.ui.toast(`${line} failed: ${String(failure)}`)
  }
}

export async function setWipLimit($: EngineInterface, stage: string, limit: number): Promise<void> {
  await callTool($, 'board.set_wip_limit', { stage, limit })
  await refresh($)
}

export function selectedAddress($: EngineInterface) {
  return read($, selected)
}

export function select($: EngineInterface, address: string) {
  return update($, selected, () => address)
}

export function currentSplitLayout($: EngineInterface) {
  return read($, splitLayout)
}

export function showRegion($: EngineInterface, expanded: SplitLayoutJson['expanded']) {
  return update($, splitLayout, layout => ({ ...layout, expanded }))
}

export function setBoardRows($: EngineInterface, boardRows: number) {
  return update($, splitLayout, layout => ({ ...layout, boardRows }))
}

export function noteSurfaceModulesFailed($: EngineInterface) {
  return update($, surfaceModulesFailed, () => true)
}

export function haveSurfaceModulesFailed($: EngineInterface) {
  return read($, surfaceModulesFailed)
}

export function isOnlyActive($: EngineInterface) {
  return read($, onlyActive)
}

export function toggleOnlyActive($: EngineInterface) {
  return update($, onlyActive, isOn => !isOn)
}

export function currentColumnOffset($: EngineInterface) {
  return read($, columnOffset)
}

export function scrollColumns($: EngineInterface, step: number) {
  return update($, columnOffset, offset => Math.max(0, offset + step))
}
