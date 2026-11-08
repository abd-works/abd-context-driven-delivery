import { atom, read, update } from 'claude-code'
import type { EngineInterface } from 'claude-code'

import type { BoardData, ColumnData, PracticeGuidanceData } from '@cdd/space/kanban/board'
import type { TicketData } from '@cdd/space/kanban/ticket'

import type { ChatBarJson } from '../../types'
import { reasonOf } from '../failure'
import { SERVER } from '../health/server-health-client'
import { FidelityProgressClient, selectedFidelitySlug } from './fidelity-progress-client'
import { StageClient, shownStageName } from './stage-client'

// The chat bar: the active session's line above the prompt. Sources: harness/chat-ui/.context/story-map.md,
// cdr/0001-stage-strip-band.md, design/StageStrip.dc.html. Every rule lives in the Python Ticket; this file shows its answers.
const chatBar = atom({ plugin: 'cdd-board', key: 'chatBar' } as const, { board: null, problem: null } as ChatBarJson)

const ticketsOf = (column: ColumnData): TicketData[] => [...(column.in_progress ?? []), ...(column.done ?? []), ...(column.tickets ?? [])]

// The active session's line: health mark, session name, fidelity dots, action button, stage icons.
export class ChatBarClient {
  private readonly board: BoardData | null

  constructor(
    json: ChatBarJson,
    private readonly shown: string | null,
    private readonly selected: string | null,
  ) {
    this.board = json.board as BoardData | null
    this.problem = json.problem
  }

  readonly problem: string | null

  // The tickets a person can switch to, as Board.open_tickets names them, each sent whole by the column it is in.
  get openTickets(): TicketData[] {
    return (this.board?.open_tickets ?? []).flatMap(named => this.ticketNamed(named.name) ?? [])
  }

  get hasSession(): boolean {
    return this.ticket !== null
  }

  get sessionName(): string {
    return this.ticket?.name ?? ''
  }

  // The session.json that names the session to the session tools.
  get sessionFile(): string {
    return this.ticket?.session.session_file ?? ''
  }

  get title(): string {
    return this.ticket?.title ?? ''
  }

  get stage(): string {
    return this.ticket?.column.name ?? ''
  }

  // A stage icon a person picked shows that stage's fidelities; otherwise the dots show the stage the session is in.
  get shownStage(): string {
    return this.shown && this.board?.columns.some(column => column.name === this.shown && column.work_required) ? this.shown : this.stage
  }

  // Ticket.is_done answers whether every fidelity of the stage is reviewed, so the action button moves the session on;
  // it is never done outside a stage.
  get canMoveNext(): boolean {
    return this.ticket?.is_done ?? false
  }

  // The board's columns in its order: Backlog, each stage, Complete, each placed against the session's column. Only a
  // stage holds fidelities to show.
  get stages(): StageClient[] {
    const columns = this.board?.columns ?? []
    const sessionPlace = columns.findIndex(column => column.name === this.stage)
    return columns.map((column, place) => new StageClient(column, place, sessionPlace, column.name === this.shownStage && column.name !== this.stage))
  }

  // Every action a person can run on a fidelity of the shown stage, its steps first, as the stage sends them.
  get actions(): string[] {
    return this.board?.columns.find(column => column.name === this.shownStage)?.actions ?? []
  }

  // The shown stage's fidelities of the practices this session has turned on: the ticket's progress on each fidelity
  // names its stage and holds the fidelity itself, in the order the stage requires them.
  get fidelities(): FidelityProgressClient[] {
    const ticket = this.ticket
    if (!ticket) return []
    return ticket.progress
      .filter(progress => progress.stage.name === this.shownStage && progress.is_enabled)
      .map(progress => new FidelityProgressClient(progress, ticket, this.practiceNamed(progress.practice.key), progress.fidelity.slug === this.selected))
  }

  // The fidelities the session card lists a folder beside: practices that write under one folder share it, so each
  // folder is listed once, beside the first fidelity that writes there.
  get foldersListedBeside(): Set<string> {
    const first = new Map<string, string>()
    for (const fidelity of this.fidelities) if (fidelity.folder && !first.has(fidelity.folder)) first.set(fidelity.folder, fidelity.slug)
    return new Set(first.values())
  }

  // The fidelity the action button acts on: the one a person selected, else the ticket's next, else the first shown.
  get actionFidelity(): FidelityProgressClient | null {
    return this.selectedFidelity ?? this.fidelities.find(fidelity => fidelity.slug === this.ticket?.next?.fidelity.slug) ?? this.fidelities[0] ?? null
  }

  // Null when the stored fidelity is not one of the shown stage's, so the selection never points into a hidden stage.
  get selectedFidelity(): FidelityProgressClient | null {
    return this.fidelities.find(fidelity => fidelity.isSelected) ?? null
  }

  // The status line: the session, its stage, its next fidelity or done, and how many fidelities have violations.
  get statusLine(): string {
    const ticket = this.ticket
    if (!ticket) return ''
    const violations = ticket.progress.filter(progress => progress.state === 'violations').length
    const next = ticket.next ? `next: ${ticket.next.fidelity.slug}` : ticket.is_done ? 'done' : ''
    return [ticket.name, ticket.column.name, next, violations ? `${violations} with violations` : ''].filter(Boolean).join(' · ')
  }

  // The agent context: what the Python Ticket tells the agent about the active session in its system prompt, the same
  // session the person sees.
  get agentContext(): string {
    return this.ticket?.agent_context ?? ''
  }

  // The board names the active session's ticket, which its column sends whole.
  private get ticket(): TicketData | null {
    const active = this.board?.active?.name
    return active ? this.ticketNamed(active) : null
  }

  // A ticket the board sends by its name, found where its column sends it whole.
  private ticketNamed(name: string): TicketData | null {
    return this.board?.columns.flatMap(ticketsOf).find(ticket => ticket.name === name) ?? null
  }

  // The practice a fidelity's progress names, as the board sends it with its colour.
  private practiceNamed(key: string): PracticeGuidanceData | undefined {
    return this.board?.practices.find(practice => practice.key === key)
  }
}

// A cdd tool answered with isError, or with no JSON. tool names it; the message is the server's own text.
export class CddToolFailed extends Error {
  constructor(
    readonly tool: string,
    reason: string,
  ) {
    super(reason)
  }
}

// ticket.move_next refused the move. reason is the server's own text.
export class MoveRefused {
  constructor(readonly reason: string) {}
}

// The one place this mod's chat bar calls cdd: a reply that is not JSON, or one flagged isError, is a CddToolFailed
// carrying the server's own text.
export async function callTool<T>($: EngineInterface, tool: string, args: object): Promise<T> {
  const result = await $.mcp.call(SERVER, tool, args)
  const text = result.content[0]?.text ?? ''
  if (result.isError) throw new CddToolFailed(tool, text || `${tool} failed`)
  try {
    return JSON.parse(text) as T
  } catch {
    throw new CddToolFailed(tool, text || `${tool} sent back nothing`)
  }
}

// Atom chatBar, declared in pane/types/index.d.ts and kept in this file: the last board.show answer.
export async function currentChatBar($: EngineInterface): Promise<ChatBarClient> {
  return new ChatBarClient(await read($, chatBar), await shownStageName($), await selectedFidelitySlug($))
}

// A failed read keeps the last board and says why, so the bar never draws old state as if it were current.
export async function refreshChatBar($: EngineInterface): Promise<void> {
  try {
    const board = await callTool<BoardData>($, 'board.show', {})
    await update($, chatBar, () => ({ board, problem: null }))
  } catch (failure) {
    await update($, chatBar, json => ({ ...json, problem: reasonOf(failure) }))
  }
}

export async function moveNext($: EngineInterface, chatBar: ChatBarClient): Promise<ChatBarClient | MoveRefused> {
  try {
    await callTool<TicketData>($, 'ticket.move_next', { ticket: chatBar.sessionName })
  } catch (failure) {
    $.ui.toast(`${chatBar.sessionName} did not move: ${reasonOf(failure)}`)
    return new MoveRefused(reasonOf(failure))
  }
  await refreshChatBar($)
  return currentChatBar($)
}

export async function runHandoff($: EngineInterface, chatBar: ChatBarClient): Promise<void> {
  await $.prompt.fill({ text: `Write a handoff for ticket ${chatBar.sessionName} with /space-session-handoff-session session=${chatBar.sessionFile}`, mode: 'append' })
}
