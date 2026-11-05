import { atom, read, update } from 'claude-code'
import type { EngineInterface } from 'claude-code'

import type { BoardData, ColumnData } from '@cdd/harness/kanban/board'
import type { TicketData, WorkspaceData } from '@cdd/harness/kanban/ticket'

import type { ChatBarJson, ChatBarViewJson } from '../../types'
import { SERVER } from '../health/server-health-client'
import { FidelityClient, selectedFidelitySlug } from './fidelity-client'
import { StageClient, shownStageName } from './stage-client'

// The chat bar: the active session's line above the prompt. Sources: harness/chat-ui/.context/story-map.md,
// cdr/0001-stage-strip-band.md, design/StageStrip.dc.html. Every rule lives in the Python Ticket; this file shows its answers.
const chatBar = atom({ plugin: 'cdd-board', key: 'chatBar' } as const, { board: null, problem: null } as ChatBarJson)
const chatBarView = atom({ plugin: 'cdd-board', key: 'chatBarView' } as const, {
  isSessionListOpen: false,
  isCardOpen: false,
  switchTo: null,
  closing: null,
} as ChatBarViewJson)

export const STAGES = ['Backlog', 'Discovery', 'Specification', 'Implementation', 'Complete']
// What the board's activation dialog chooses first: leave the old session committed and pushed, open the new one on
// its own branch and worktree.
const LEAVING = ['commit', 'push']
const OPENING = ['branch', 'worktree']

const ticketsOf = (column: ColumnData): TicketData[] => [...(column.in_progress ?? []), ...(column.done ?? []), ...(column.tickets ?? [])]
const practiceOf = (slug: string): string => slug.slice(0, slug.indexOf('-'))
const reasonOf = (error: unknown): string => (error instanceof Error ? error.message : String(error))

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

  get session(): TicketData | null {
    const active = this.board?.active
    return this.board?.columns.flatMap(ticketsOf).find(ticket => ticket.name === active) ?? null
  }

  get sessionName(): string {
    return this.session?.name ?? ''
  }

  get title(): string {
    return this.session?.title ?? ''
  }

  get stage(): string {
    return this.session?.column ?? ''
  }

  // A stage icon a person picked shows that stage's fidelities; otherwise the dots show the stage the session is in.
  get shownStage(): string {
    return this.shown && this.board?.columns.some(column => column.name === this.shown && column.work_required) ? this.shown : this.stage
  }

  // Ticket.is_done answers whether every fidelity of the stage is reviewed, so the action button moves the session on.
  get canMoveNext(): boolean {
    return (this.session?.is_done ?? false) && this.stage !== 'Complete'
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

  // The shown stage's fidelities of the practices this session has turned on.
  get fidelities(): FidelityClient[] {
    const session = this.session
    const column = this.board?.columns.find(entry => entry.name === this.shownStage)
    if (!session || !column) return []
    return (column.work_required ?? [])
      .filter(slug => session.practices[practiceOf(slug)])
      .map(
        slug =>
          new FidelityClient({
            slug,
            progress: session.progress[slug] ?? 'not_started',
            violationCount: session.violation_counts[slug] ?? 0,
            actions: session.actions[slug] ?? { generate: 'to_do', validate: 'to_do', review: 'to_do' },
            defaultFormat: column.default_formats?.[slug] ?? '',
            nextOfTicket: session.next === slug ? session.next_action : '',
            isSelected: slug === this.selected,
            folder: session.practice_roots[practiceOf(slug)]?.root ?? '',
          }),
      )
  }

  // The fidelity the action button acts on: the one a person selected, else the ticket's next, else the first shown.
  get actionFidelity(): FidelityClient | null {
    return this.selectedFidelity ?? this.fidelities.find(fidelity => fidelity.fidelity === this.session?.next) ?? this.fidelities[0] ?? null
  }

  // Null when the stored fidelity is not one of the shown stage's, so the selection never points into a hidden stage.
  get selectedFidelity(): FidelityClient | null {
    return this.fidelities.find(fidelity => fidelity.isSelected) ?? null
  }
}

// ticket.move_next refused the move. reason is the server's own text.
export class MoveRefused {
  constructor(readonly reason: string) {}
}

// ticket.close refused to close the session. reason is the server's own text.
export class CloseRefused {
  constructor(readonly reason: string) {}
}

// The one place this mod's chat bar calls cdd: a reply that is not JSON, or one flagged isError, is a failure carrying
// the server's own text.
export async function callTool<T>($: EngineInterface, tool: string, args: object): Promise<T> {
  const result = await $.mcp.call(SERVER, tool, args)
  const text = result.content[0]?.text ?? ''
  if (result.isError) throw new Error(text || `${tool} failed`)
  try {
    return JSON.parse(text) as T
  } catch {
    throw new Error(text || `${tool} sent back nothing`)
  }
}

// Atom chatBar, declared in pane/types/index.d.ts and kept in this file: the last board.show answer.
export async function currentChatBar($: EngineInterface): Promise<ChatBarClient> {
  return new ChatBarClient(await read($, chatBar), await shownStageName($), await selectedFidelitySlug($))
}

export function currentChatBarView($: EngineInterface) {
  return read($, chatBarView)
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

export async function moveNext($: EngineInterface, bar: ChatBarClient): Promise<ChatBarClient | MoveRefused> {
  try {
    await callTool<TicketData>($, 'ticket.move_next', { ticket: bar.sessionName })
  } catch (failure) {
    $.ui.toast(`${bar.sessionName} did not move: ${reasonOf(failure)}`)
    return new MoveRefused(reasonOf(failure))
  }
  await refreshChatBar($)
  return currentChatBar($)
}

export async function runHandoff($: EngineInterface, bar: ChatBarClient): Promise<void> {
  await $.prompt.fill({ text: `Write a handoff for ticket ${bar.sessionName} with /space-handoff-handoff-session.`, mode: 'append' })
}

export async function toggleSessionList($: EngineInterface): Promise<void> {
  await update($, chatBarView, view => ({ ...view, isSessionListOpen: !view.isSessionListOpen, isCardOpen: false }))
}

export async function toggleCard($: EngineInterface): Promise<void> {
  await update($, chatBarView, view => ({ ...view, isCardOpen: !view.isCardOpen, isSessionListOpen: false }))
}

// Picking a session opens the activation dialog on it; the session opens only once the person confirms.
export async function pickSession($: EngineInterface, sessionName: string): Promise<void> {
  await update($, chatBarView, view => ({ ...view, isSessionListOpen: false, switchTo: sessionName }))
}

export async function cancelSwitch($: EngineInterface): Promise<void> {
  await update($, chatBarView, view => ({ ...view, switchTo: null }))
}

export async function activateSession($: EngineInterface, sessionName: string): Promise<ChatBarClient> {
  try {
    await callTool<TicketData>($, 'ticket.activate', { ticket: sessionName, leaving: LEAVING, opening: OPENING })
  } catch (failure) {
    $.ui.toast(`${sessionName} did not open: ${reasonOf(failure)}`)
  }
  await update($, chatBarView, view => ({ ...view, switchTo: null }))
  await refreshChatBar($)
  return currentChatBar($)
}

// A new session opens through the same activation dialog as one picked from the list.
export async function createSession($: EngineInterface, sessionName: string): Promise<ChatBarClient> {
  try {
    const created = await callTool<TicketData>($, 'ticket.create', { title: sessionName })
    await update($, chatBarView, view => ({ ...view, isSessionListOpen: false, switchTo: created.name }))
  } catch (failure) {
    $.ui.toast(`${sessionName} was not created: ${reasonOf(failure)}`)
  }
  await refreshChatBar($)
  return currentChatBar($)
}

// The close dialog offers to commit and push only when the session has a branch of its own.
export async function openClose($: EngineInterface, bar: ChatBarClient): Promise<void> {
  try {
    const workspace = await callTool<WorkspaceData>($, 'ticket.workspace', { ticket: bar.sessionName })
    await update($, chatBarView, view => ({ ...view, closing: { hasBranch: workspace.leaving_has_branch } }))
  } catch (failure) {
    $.ui.toast(`${bar.sessionName} cannot close: ${reasonOf(failure)}`)
  }
}

export async function cancelClose($: EngineInterface): Promise<void> {
  await update($, chatBarView, view => ({ ...view, closing: null }))
}

// Null when closing leaves no session active.
export async function closeSession($: EngineInterface, bar: ChatBarClient): Promise<ChatBarClient | null | CloseRefused> {
  const { closing } = await read($, chatBarView)
  const leaving = closing?.hasBranch ? LEAVING : []
  try {
    await callTool<TicketData>($, 'ticket.close', { ticket: bar.sessionName, leaving })
  } catch (failure) {
    $.ui.toast(`${bar.title} did not close: ${reasonOf(failure)}`)
    return new CloseRefused(reasonOf(failure))
  }
  const left = leaving.length ? `${bar.title}: committed, pushed · ` : ''
  $.ui.toast(`${left}Session ${bar.title} closed`)
  await update($, chatBarView, view => ({ ...view, closing: null }))
  await refreshChatBar($)
  const after = await currentChatBar($)
  return after.session ? after : null
}
