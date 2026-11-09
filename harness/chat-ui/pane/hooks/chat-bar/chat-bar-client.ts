import { atom, read, update } from 'claude-code'
import type { EngineInterface } from 'claude-code'

import type { BoardOverviewData, BoardPracticeData } from '@cdd/space/kanban/board'
import type { FidelityProgressData } from '@cdd/space/kanban/fidelity-progress'
import type { TicketData } from '@cdd/space/kanban/ticket'

import type { ChatBarJson } from '../../types'
import { reasonOf } from '../shared/failure'
import { SERVER } from '../health/server-health-client'
import { FidelityProgressClient, selectedFidelitySlug } from './fidelity-progress-client'
import { StageClient, shownStageName } from './stage-client'

// The chat bar: the active session's line above the prompt. Sources: harness/chat-ui/.context/story-map.md,
// cdr/0001-stage-strip-band.md, design/StageStrip.dc.html. Every rule lives in the Python Ticket; this file shows its answers.
const chatBar = atom({ plugin: 'cdd-board', key: 'chatBar' } as const, { board: null, problem: null, failure: null } as ChatBarJson, { shape: 'chat-bar-overview-2' })


// The active session's line: health mark, session name, fidelity dots, action button, stage icons.
export class ChatBarClient {
  private readonly board: BoardOverviewData | null

  constructor(
    json: ChatBarJson,
    private readonly shown: string | null,
    private readonly selected: string | null,
  ) {
    this.board = json.board as BoardOverviewData | null
    this.problem = json.problem
    this.failure = json.failure ?? null
  }

  readonly problem: string | null

  // An action the person ran that failed, in the server's own words, shown until they dismiss it.
  readonly failure: string | null

  // The tickets a person can switch to, each named in the stage it is in, as board.overview sends them.
  get openTickets(): { name: string; stage: string }[] {
    return (this.board?.columns ?? []).flatMap(column => column.tickets.map(ticket => ({ name: ticket.name, stage: column.name })))
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

  // The active ticket's own worktree, where the chat bar moves this chat; empty while it has none.
  get worktree(): string {
    return this.ticket?.worktree ?? ''
  }

  get title(): string {
    return this.ticket?.title ?? ''
  }

  get stage(): string {
    return this.ticket?.column.name ?? ''
  }

  // A stage icon a person picked shows that stage's fidelities; otherwise the dots show the stage the session is in.
  get shownStage(): string {
    return this.shown && this.board?.columns.some(column => column.name === this.shown && column.kind === 'stage') ? this.shown : this.stage
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
      .map(progress => new FidelityProgressClient(progress, ticket, this.practiceNamed(progress.practice.key), progress.fidelity.slug === this.selected, this.labelOf(progress.fidelity.slug)))
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

  // The active session's ticket, which the board sends whole.
  private get ticket(): TicketData | null {
    return this.board?.active ?? null
  }

  // A ticket the board's switch list names, found where its column sends it whole (harness/chat-ui/.context/cdr/0002).
  // A fidelity's label as the board names it, such as story-map; its slug when the board names none.
  private labelOf(slug: string): string {
    return this.board?.fidelities.find(shown => shown.fidelity.slug === slug)?.label ?? slug
  }

  // The practice a fidelity's progress names, as the board sends it with its colour.
  private practiceNamed(key: string): BoardPracticeData | undefined {
    return this.board?.practices.find(shown => shown.practice.key === key)
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
// carrying the server's own text. Every call names the folder the chat works in now as chat_folder, so the server reads
// the sessions of that folder's branch and worktree, not of the folder the chat connected from.
export async function callTool<T>($: EngineInterface, tool: string, args: object): Promise<T> {
  const result = await $.mcp.call(SERVER, tool, { ...args, chat_folder: await $.session.root() })
  const text = result.content[0]?.text ?? ''
  if (result.isError) throw new CddToolFailed(tool, text || `${tool} failed`)
  try {
    return JSON.parse(text) as T
  } catch {
    throw new CddToolFailed(tool, text || `${tool} sent back nothing`)
  }
}

// Atom chatBar, declared in pane/types/index.d.ts and kept in this file: the last board.overview answer.
export async function currentChatBar($: EngineInterface): Promise<ChatBarClient> {
  return new ChatBarClient(await read($, chatBar), await shownStageName($), await selectedFidelitySlug($))
}

// A failed read keeps the last board and says why, so the bar never draws old state as if it were current.
export async function refreshChatBar($: EngineInterface): Promise<void> {
  try {
    const board = await callTool<BoardOverviewData>($, 'board.overview', {})
    await update($, chatBar, json => ({ ...json, board, problem: null }))
  } catch (failure) {
    await update($, chatBar, json => ({ ...json, problem: reasonOf(failure) }))
  }
}

// An action that failed stays above the line until the person dismisses it: a toast passes before anyone reads it.
export async function showFailure($: EngineInterface, failure: string): Promise<void> {
  await update($, chatBar, json => ({ ...json, failure }))
}

export async function dismissFailure($: EngineInterface): Promise<void> {
  await update($, chatBar, json => ({ ...json, failure: null }))
}

// Fix sends what the chat bar shows to this chat's agent to find its cause and fix it.
export async function askChatToFix($: EngineInterface, shown: string): Promise<void> {
  await $.prompt.submit({ text: `The chat bar shows this; find its cause and fix it: ${shown}`, asUser: true })
}

// Fix on a failure sends it to the chat and clears it from the line.
export async function fixFailure($: EngineInterface, chatBar: ChatBarClient): Promise<void> {
  if (!chatBar.failure) return
  await askChatToFix($, chatBar.failure)
  await dismissFailure($)
}

export async function moveNext($: EngineInterface, chatBar: ChatBarClient): Promise<ChatBarClient | MoveRefused> {
  try {
    await callTool<TicketData>($, 'ticket.move_next', { ticket: chatBar.sessionName })
  } catch (failure) {
    await showFailure($, `${chatBar.sessionName} did not move: ${reasonOf(failure)}`)
    return new MoveRefused(reasonOf(failure))
  }
  await refreshChatBar($)
  return currentChatBar($)
}

export async function runHandoff($: EngineInterface, chatBar: ChatBarClient): Promise<void> {
  await $.prompt.fill({ text: `Write a handoff for ticket ${chatBar.sessionName} with /space-session-handoff-session session=${chatBar.sessionFile}`, mode: 'append' })
}

// fidelity-progress.finish_review refused the review, most often because the latest Validate did not pass. reason is the server's text.
export class ReviewRefused {
  constructor(readonly reason: string) {}
}

// Review is the person's own approval, recorded by the Python FidelityProgress, which refuses it until the latest
// Validate passed. The chat bar then reads the board again and answers the fidelity as it now stands.
export async function reviewFidelity($: EngineInterface, fidelity: FidelityProgressClient): Promise<FidelityProgressClient | ReviewRefused> {
  const ticket = fidelity.progress.ticket.name
  const slug = fidelity.slug
  try {
    await callTool<FidelityProgressData>($, 'fidelity-progress.finish_review', { ticket, fidelity: slug })
  } catch (failure) {
    $.ui.toast(`${slug} not reviewed: ${reasonOf(failure)}`)
    return new ReviewRefused(reasonOf(failure))
  }
  $.ui.toast(`${slug} reviewed on ${ticket}`)
  await refreshChatBar($)
  return (await currentChatBar($)).fidelities.find(entry => entry.slug === slug) ?? fidelity
}
