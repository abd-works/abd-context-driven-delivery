import { atom, read, update } from 'claude-code'
import type { EngineInterface } from 'claude-code'

import type { BoardData, ColumnData } from '@cdd/space/kanban/board'
import type { TicketData } from '@cdd/space/kanban/ticket'

import type { ChatBarJson } from '../../types'
import { reasonOf } from '../failure'
import { SERVER } from '../health/server-health-client'
import { FidelityClient, selectedFidelitySlug } from './fidelity-client'
import { StageClient, shownStageName } from './stage-client'

// The chat bar: the active session's line above the prompt. Sources: harness/chat-ui/.context/story-map.md,
// cdr/0001-stage-strip-band.md, design/StageStrip.dc.html. Every rule lives in the Python Ticket; this file shows its answers.
const chatBar = atom({ plugin: 'cdd-board', key: 'chatBar' } as const, { board: null, problem: null } as ChatBarJson)

const STAGES = ['Backlog', 'Discovery', 'Specification', 'Implementation', 'Complete']

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

  // The open sessions a person can switch to, each with the stage it is in.
  get sessions(): { name: string; stage: string }[] {
    const columns = this.board?.columns.filter(column => column.name !== 'Backlog' && column.name !== 'Complete') ?? []
    return columns.flatMap(column => ticketsOf(column).map(ticket => ({ name: ticket.name, stage: column.name })))
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

  // Ticket.is_done answers whether every fidelity of the stage is reviewed, so the action button moves the session on.
  get canMoveNext(): boolean {
    return (this.ticket?.is_done ?? false) && this.stage !== 'Complete'
  }

  get stages(): StageClient[] {
    const reached = STAGES.indexOf(this.stage)
    return STAGES.map(
      (name, index) =>
        new StageClient({
          name,
          status: index < reached ? 'done' : index === reached ? 'in_progress' : 'not_reached',
          isShown: name === this.shownStage && name !== this.stage,
          canShow: index > 0 && index < STAGES.length - 1,
        }),
    )
  }

  // The shown stage's fidelities of the practices this session has turned on: the ticket's progress on each fidelity
  // names its stage and holds the fidelity itself, in the order the stage requires them.
  get fidelities(): FidelityClient[] {
    const ticket = this.ticket
    if (!ticket) return []
    return ticket.progress
      .filter(progress => progress.stage.name === this.shownStage && progress.is_enabled)
      .map(
        progress =>
          new FidelityClient({
            slug: progress.slug,
            practice: progress.practice,
            name: progress.fidelity.name,
            progress: progress.state,
            violationCount: progress.violation_count,
            actions: progress.actions,
            defaultFormat: progress.fidelity.default_format,
            nextAction: progress.next_action,
            isSelected: progress.slug === this.selected,
            folder: ticket.session.practices[progress.practice]?.root ?? '',
          }),
      )
  }

  // The fidelity the action button acts on: the one a person selected, else the ticket's next, else the first shown.
  get actionFidelity(): FidelityClient | null {
    return this.selectedFidelity ?? this.fidelities.find(fidelity => fidelity.fidelity === this.ticket?.next?.slug) ?? this.fidelities[0] ?? null
  }

  // Null when the stored fidelity is not one of the shown stage's, so the selection never points into a hidden stage.
  get selectedFidelity(): FidelityClient | null {
    return this.fidelities.find(fidelity => fidelity.isSelected) ?? null
  }

  // The status line: the session, its stage, its next fidelity or done, and how many fidelities have violations.
  get statusLine(): string {
    const ticket = this.ticket
    if (!ticket) return ''
    const violations = ticket.progress.filter(progress => progress.state === 'violations').length
    const next = ticket.next ? `next: ${ticket.next.slug}` : ticket.is_done ? 'done' : ''
    return [ticket.name, ticket.column.name, next, violations ? `${violations} with violations` : ''].filter(Boolean).join(' · ')
  }

  // The agent context: what the agent is told about the active session in its system prompt, the same session the
  // person sees.
  get agentContext(): string {
    const ticket = this.ticket
    if (!ticket) return ''
    return (
      `CDD session board: you are working on ticket ${ticket.name} ("${ticket.title}"), in ${ticket.column.name}. ` +
      (ticket.next ? `Its next guidance is ${ticket.next.slug}. ` : 'Its stage is done and waits for a person to move it. ') +
      'Each fidelity goes through generate, validate, then review, which a person records on the board.'
    )
  }

  // The board sends the active session's ticket whole.
  private get ticket(): TicketData | null {
    return this.board?.active ?? null
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
  await $.prompt.fill({ text: `Write a handoff for ticket ${chatBar.sessionName} with /space-session-handoff-session.`, mode: 'append' })
}
