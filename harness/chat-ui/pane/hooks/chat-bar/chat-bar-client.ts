import { atom, read, update } from 'claude-code'
import type { EngineInterface } from 'claude-code'

import type { BoardOverviewData, BoardPracticeData } from '@cdd/space/kanban/board'
import type { FidelityProgressData } from '@cdd/space/kanban/fidelity-progress'
import type { TicketData } from '@cdd/space/kanban/ticket'

import type { ChatBarJson } from '../../types'
import { reasonOf } from '../shared/failure'
import { SERVER } from '../health/server-health-client'
import { FidelityProgressClient, selectedFidelitySlugs } from './fidelity-progress-client'
import { StageClient, shownStageName } from './stage-client'

// The chat bar: the active session's line above the prompt. Sources: harness/chat-ui/.context/story-map.md,
// cdr/0001-stage-strip-band.md, design/StageStrip.dc.html. Every rule lives in the Python Ticket; this file shows its answers.
// Main is the default session: the default branch in the repository's own folder, a ticket on the board like any other.
export const MAIN_SESSION = 'main'

const chatBar = atom({ plugin: 'cdd-board', key: 'chatBar' } as const, { board: null, problem: null, failure: null } as ChatBarJson, { shape: 'chat-bar-overview-2' })


// The active session's line: health mark, session name, fidelity dots, action button, stage icons.
export class ChatBarClient {
  private readonly board: BoardOverviewData | null

  constructor(
    json: ChatBarJson,
    private readonly shown: string | null,
    private readonly selected: string[],
  ) {
    this.board = json.board as BoardOverviewData | null
    this.problem = json.problem
    this.failure = json.failure ?? null
  }

  readonly problem: string | null

  // An action the person ran that failed, in the server's own words, shown until they dismiss it.
  readonly failure: string | null

  // The tickets a person can open from the main chat, each named in the stage it is in, as board.overview sends them.
  // Main is a ticket too, but the session list shows it first on its own row, so it is left out here.
  get openTickets(): { name: string; stage: string }[] {
    return (this.board?.columns ?? []).flatMap(column => column.tickets.filter(ticket => ticket.name !== MAIN_SESSION).map(ticket => ({ name: ticket.name, stage: column.name })))
  }

  // Every session has a ticket, main among them, so the bar draws the full panel whenever the board has answered.
  get hasSession(): boolean {
    return this.ticket !== null
  }

  // Main, the default session, is what a chat in the repository's own folder works on. It never closes, so the bar offers
  // no close for it, and only its chat opens other tickets.
  get isMain(): boolean {
    return this.ticket?.is_main ?? false
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
    return this.shown && this.board?.columns.some(column => column.name === this.shown && column.kind === 'stage') ? this.shown : this.stage
  }

  // Ticket.is_done answers whether every fidelity of the stage has passed validate, so the action button moves the session on;
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
  // The ticket the session works on, by name; empty with none.
  // The Claude Design link recorded for the latest version of the session's design canvas, as the practice that keeps
  // one answers it (UX), which the file viewer opens; empty when none is recorded or that practice is off.
  get designView(): string {
    return Object.values(this.ticket?.session.practices ?? {}).find(practice => practice.design_view)?.design_view ?? ''
  }

  get ticketName(): string {
    return this.ticket?.name ?? ''
  }

  // The whole path of the folder the session works in, which the Graph app opens on; empty with no session.
  get sessionPath(): string {
    return (this.ticket as (TicketData & { session_path?: string }) | null)?.session_path ?? ''
  }

  // The actions of the shown stage whose command takes the formats the chips pick, generate and render.
  get actionsWithFormats(): string[] {
    const column = this.board?.columns.find(column => column.name === this.shownStage) as { actions_with_formats?: string[] } | undefined
    return column?.actions_with_formats ?? ['generate', 'render']
  }

  get actions(): string[] {
    return (this.board?.columns.find(column => column.name === this.shownStage)?.actions ?? [])
  }

  // The shown stage's fidelities of the practices this session has turned on: the ticket's progress on each fidelity
  // names its stage and holds the fidelity itself, in the order the stage requires them.
  get fidelities(): FidelityProgressClient[] {
    const ticket = this.ticket
    if (!ticket) return []
    return ticket.progress
      .filter(progress => progress.stage.name === this.shownStage && progress.is_enabled)
      .map(progress => new FidelityProgressClient(progress, ticket, this.practiceNamed(progress.practice.key), this.selected.includes(progress.fidelity.slug), this.labelOf(progress.fidelity.slug)))
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

  // The first selected of the shown stage's fidelities; a selection in a hidden stage is ignored.
  get selectedFidelity(): FidelityProgressClient | null {
    return this.fidelities.find(fidelity => fidelity.isSelected) ?? null
  }

  // Every fidelity the action button acts on: each one selected, else the one actionFidelity names.
  get actionFidelities(): FidelityProgressClient[] {
    const selected = this.fidelities.filter(fidelity => fidelity.isSelected)
    if (selected.length) return selected
    const one = this.actionFidelity
    return one ? [one] : []
  }

  // The repository the board shows, by its folder's name.
  get repoName(): string {
    return this.board?.project ?? ''
  }

  // Whether the folder is a git repository, where tickets get worktrees and chats of their own. A board read before the
  // overview said so counts as one, so its tickets stay open.
  get isClone(): boolean {
    return this.board?.is_clone ?? true
  }

  // The project's folder on disk, which a chat in a plain folder shows instead of the repo and session buttons.
  get folder(): string {
    return this.board?.folder ?? ''
  }

  // A chat in a folder that is no git repository, such as one opened from FOLDER on its own session, has no branch to
  // switch or close and no other repository to open, so the bar shows its folder alone, read only.
  get isPlainFolder(): boolean {
    return Boolean(this.board) && !this.isClone
  }

  // The folder an app's page loads: the whole path of the folder the session works in, its workpath; empty while no
  // ticket's session is open or it works in the whole repository.
  get workpath(): string {
    return this.ticket?.session.workpath ?? ''
  }

  // The status line below the chat: the whole path of the folder the session works in, which already names the
  // repository, and a worktree's folder its branch.
  get statusLine(): string {
    return this.sessionPath
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
// the sessions of that folder's branch and worktree, not of the folder the chat connected from, and names the chat as
// conversation_id, so the server answers with the session this chat has open, as it does for the agent's own calls.
export async function callTool<T>($: EngineInterface, tool: string, args: object): Promise<T> {
  const text = await callToolText($, tool, args)
  try {
    return JSON.parse(text) as T
  } catch {
    throw new CddToolFailed(tool, text || `${tool} sent back nothing`)
  }
}

// A tool that answers in prose, such as repos.open, read as its text; one flagged isError is a CddToolFailed.
export async function callToolText($: EngineInterface, tool: string, args: object): Promise<string> {
  const result = await $.mcp.call(SERVER, tool, { ...args, chat_folder: await $.session.root(), conversation_id: await $.session.id() })
  const text = result.content[0]?.text ?? ''
  if (result.isError) throw new CddToolFailed(tool, text || `${tool} failed`)
  return text
}

// Atom chatBar, declared in pane/types/index.d.ts and kept in this file: the last board.overview answer.
export async function currentChatBar($: EngineInterface): Promise<ChatBarClient> {
  return new ChatBarClient(await read($, chatBar), await shownStageName($), await selectedFidelitySlugs($))
}

// A failed read keeps the last board and says why, so the bar never draws old state as if it were current.
export async function refreshChatBar($: EngineInterface): Promise<void> {
  try {
    const board = await readBoard($)
    await update($, chatBar, json => ({ ...json, board, problem: null }))
  } catch (failure) {
    await update($, chatBar, json => ({ ...json, problem: reasonOf(failure) }))
  }
}

// A restart of the cdd server, as an install does, cuts off a call in flight. board.overview only reads, so a read cut
// off that way is asked again once the server is back, before the bar says the board did not answer.
const CUT_OFF = 'connection closed'
const RESTART_WAIT_MILLISECONDS = 3000

async function readBoard($: EngineInterface): Promise<BoardOverviewData> {
  try {
    return await callTool<BoardOverviewData>($, 'board.overview', {})
  } catch (failure) {
    if (!reasonOf(failure).includes(CUT_OFF)) throw failure
    await $.clock.sleep(RESTART_WAIT_MILLISECONDS)
    return callTool<BoardOverviewData>($, 'board.overview', {})
  }
}

// Restart starts the cdd server again on the code in the checkout it serves, so a Python edit takes effect without an
// install; the chat bar itself reloads from that checkout as its files change. The bar is read again on the new code.
interface RestartData { tools: number }

export async function restartServer($: EngineInterface): Promise<void> {
  $.ui.toast('Restarting the cdd server…')
  try {
    const restarted = await callTool<RestartData>($, 'cdd.restart', {})
    $.ui.toast(`cdd server restarted with ${restarted.tools} tools`)
  } catch (failure) {
    await showFailure($, `cdd.restart failed: ${reasonOf(failure)}`)
    return
  }
  await refreshChatBar($)
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
  await $.prompt.submit({ text: `The CDD chat bar above the prompt shows this; find its cause and fix it: ${shown}`, asUser: true })
}

// What Fix on a board that did not answer sends: the chat bar reads the board from the cdd MCP server, which runs a
// pinned copy of CDD, so most of these failures are a server or install older than the CDD checkout.
export const BOARD_PROBLEM_STEPS = [
  'Context: the chat bar reads the session board from the cdd MCP server. That server runs a pinned copy of the CDD '
    + 'repository at ~/.cdd/runtime, and ~/.cdd/runtime.json names its commit. This chat reaches it through its cdd entry '
    + '(.mcp.json and ~/.claude.json), whose header helper names the chat\'s project and Claude Code process. Read '
    + 'harness/mcp/.context/module-context.md and harness/installation/.context/module-context.md in the CDD checkout first.',
  'Check versions: in the CDD checkout, git fetch, then compare the commit in ~/.cdd/runtime.json with HEAD of the '
    + 'checkout\'s branch and with origin/main. Search the commits between them for a fix to this error.',
  'Get the latest: pull the latest from the checkout\'s branch; on main, git pull origin main. Stop and tell me if the '
    + 'pull conflicts with uncommitted work.',
  'Reinstall: python scripts/install.py --ide Claude from the CDD checkout. It runs harness/installation/installer.py, '
    + 'which writes the cdd entry and plugins again and pins the server to the checkout\'s commit when it runs an older one. '
    + 'Other chats share that server, so message their sessions before --pin-runtime or cdd.restart. If the install '
    + 'fails, follow "When install fails" in harness/installation/installer.md: log it in the open session\'s '
    + '.sessions/{session}/install-failures.md, run /harness-diagnostics-agent-tools-diagnostics with the error, and '
    + 'update the themes in .sessions/_backlog/install-failure-themes.md.',
  'Ask me to run /reload-plugins, so this chat loads the new cdd entry and header helper, then check that the chat bar '
    + 'reads the board again.',
]

export function boardProblemPrompt(shown: string): string {
  const steps = BOARD_PROBLEM_STEPS.map((step, index) => `${index + 1}. ${step}`).join('\n')
  return `The CDD chat bar above the prompt shows: ${shown}\n\nFind its cause and fix it:\n${steps}\n\nThen tell me what was wrong and what you changed.`
}

// Fix on a board that did not answer sends the chat the context and the steps that usually clear it.
export async function askChatToFixBoard($: EngineInterface, shown: string): Promise<void> {
  await $.prompt.submit({ text: boardProblemPrompt(shown), asUser: true })
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

