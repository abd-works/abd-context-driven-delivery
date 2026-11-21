import { atom, read, update } from 'claude-code'
import type { EngineInterface } from 'claude-code'

import type { BoardOverviewData, BoardPracticeData } from '@cdd/space/kanban/board'
import type { FidelityProgressData } from '@cdd/space/kanban/fidelity-progress'
import type { TicketData } from '@cdd/space/kanban/ticket'

import type { ChatBarJson, FormatChoiceJson } from '../../types'
import { shownAsFailure } from '../error-display/failure-client'
import { reasonOf } from '../shared/reason'
import { callTool } from '../shared/cdd-tool'
import { debugCommandOf } from '../shared/debug-command'
import type { GuidanceSelectionData } from '@cdd/space/session/session'

import { FidelityProgressClient, PracticeDotClient } from './fidelity-progress-client'
import { currentGuidance } from './guidance-client'
import { StageClient } from './stage-client'

// The chat bar: the active session's line above the prompt. Sources: .context/story-map.md (Move Work Forward From Chat Bar),
// cdr/0001-stage-strip-band.md, design/StageStrip.dc.html. Every rule lives in the Python Ticket; this file shows its answers.
// Main is the default session: the default branch in the repository's own folder, a ticket on the board like any other.
export const MAIN_SESSION = 'main'

const chatBar = atom({ plugin: 'cdd-board', key: 'chatBar' } as const, { board: null, problem: null } as ChatBarJson, { shape: 'chat-bar-overview-3' })


// The active session's line: health mark, session name, fidelity dots, action button, stage icons.
export class ChatBarClient {
  private readonly board: BoardOverviewData | null

  constructor(
    json: ChatBarJson,
    private readonly guidance: GuidanceSelectionData | null,
  ) {
    this.board = json.board as BoardOverviewData | null
    this.problem = json.problem
  }

  readonly problem: string | null

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

  // The stages whose fidelities the dots show, in the board's order: those turned on with the stage buttons, here or in
  // a page the chat opened, none turned on meaning every stage; before either chose, the stage the session is in.
  get shownStages(): string[] {
    const stages = (this.board?.columns ?? []).filter(column => column.kind === 'stage').map(column => column.name)
    const selected = this.selectedStages
    if (!this.guidance?.is_stage_chosen || selected.length) return stages.filter(stage => selected.includes(stage))
    return stages
  }

  // The stages the stage buttons have turned on, by title; before any was chosen, the stage the session is in.
  private get selectedStages(): string[] {
    if (!this.guidance?.is_stage_chosen) return [this.stage]
    return this.guidance.stages.filter((stage: { is_selected: boolean }) => stage.is_selected).map((stage: { title: string }) => stage.title)
  }

  // The first stage shown, whose actions the action button offers: every stage takes the same steps.
  get shownStage(): string {
    return this.shownStages[0] ?? this.stage
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
    return columns.map((column, place) => new StageClient(column, place - sessionPlace, this.selectedStages.includes(column.name)))
  }

  // Every action a person can run on a fidelity of the shown stage, its steps first, as the stage sends them.
  // The ticket the session works on, by name; empty with none.
  // The Claude Design link recorded for the latest version of the session's design canvas, as the practice that keeps
  // one answers it (UX), which the file viewer opens; empty when none is recorded or that practice is off.
  get designView(): string {
    return Object.values(this.ticket?.session.practices ?? {}).find(practice => practice.design_view)?.design_view ?? ''
  }

  // The whole path of the folder the session works in, which the Graph app opens on; empty with no session.
  get sessionPath(): string {
    return this.ticket?.session_path ?? ''
  }

  // The actions of the shown stage whose command takes the formats the chips pick, generate and render.
  get actionsWithFormats(): string[] {
    const column = this.board?.columns.find(column => column.name === this.shownStage) as { actions_with_formats?: string[] } | undefined
    return column?.actions_with_formats ?? ['generate', 'render']
  }

  get actions(): string[] {
    return (this.board?.columns.find(column => column.name === this.shownStage)?.actions ?? [])
  }

  // Whether the session works on a practice, as its guidance selection says, else as the board read it.
  isPracticeOn(key: string): boolean {
    const practice = this.guidance?.practices.find(each => each.key === key)
    return practice ? practice.is_selected : (this.ticket?.progress.find(progress => progress.practice.key === key)?.is_enabled ?? true)
  }

  // The fidelities of the stages shown whose practice dot is on, no dot on meaning every practice: what every action
  // runs on, in the order the stages require them. They follow the dots as drawn, so a command never names a practice
  // whose dot is off, even while a press is drawn ahead of the session's answer, whose fidelity list is not yet updated.
  get fidelities(): FidelityProgressClient[] {
    const shown = this.fidelitiesOfShownStages
    const selected = shown.filter(fidelity => fidelity.isSelected)
    return selected.length ? selected : shown
  }

  // One dot per practice with fidelities in the stages shown, on or off: a press turns the practice on or off for the
  // session, all its fidelities of those stages.
  get practiceDots(): PracticeDotClient[] {
    const byPractice = new Map<string, FidelityProgressClient[]>()
    for (const fidelity of this.fidelitiesOfShownStages) byPractice.set(fidelity.progress.practice.key, [...(byPractice.get(fidelity.progress.practice.key) ?? []), fidelity])
    return [...byPractice].map(([key, fidelities]) => new PracticeDotClient(key, fidelities, this.isPracticeOn(key)))
  }

  // Every fidelity of the stages shown, its practice on or off, each marked selected while its practice is on.
  private get fidelitiesOfShownStages(): FidelityProgressClient[] {
    const ticket = this.ticket
    if (!ticket) return []
    return ticket.progress
      .filter(progress => this.shownStages.includes(progress.stage.name))
      .map(progress => new FidelityProgressClient(progress, ticket, this))
  }

  // The format chips: each format group the selected fidelities offer, selected or not, as the session holds them.
  get formatChoices(): FormatChoiceJson[] {
    return (this.guidance?.formats ?? []).map(format => ({ label: format.label, formats: format.formats, offered: format.offered, made: 0, is_chosen: format.is_selected }))
  }

  // Every fidelity of the shown stage, its practice on or off for the session: the Files app shows a toggle for each
  // practice and lists the files of the ones turned on, so turning one on there shows its files at once.
  get stageFidelitySlugs(): string[] {
    return (this.ticket?.progress ?? []).filter(progress => this.shownStages.includes(progress.stage.name)).map(progress => progress.fidelity.slug)
  }

  // The fidelities the session card lists a folder beside: practices that write under one folder share it, so each
  // folder is listed once, beside the first fidelity that writes there.
  get foldersListedBeside(): Set<string> {
    const first = new Map<string, string>()
    for (const fidelity of this.fidelities) if (fidelity.folder && !first.has(fidelity.folder)) first.set(fidelity.folder, fidelity.slug)
    return new Set(first.values())
  }

  // The fidelity whose next action the action button names: the ticket's next among those selected, else the first.
  get actionFidelity(): FidelityProgressClient | null {
    return this.fidelities.find(fidelity => fidelity.slug === this.ticket?.next?.fidelity.slug) ?? this.fidelities[0] ?? null
  }

  // The repository the board shows, by its folder's name.
  get repoName(): string {
    return this.board?.project ?? ''
  }

  // Whether the folder is a git repository, which CDD works in: tickets get worktrees and chats of their own. A board
  // read before the overview said so counts as one, so its tickets stay open.
  get isClone(): boolean {
    return this.board?.is_clone ?? true
  }

  // The project's folder on disk: where the new session's folder picker opens, and what a chat in a plain folder names
  // when it asks for the repository.
  get folder(): string {
    return this.board?.folder ?? ''
  }

  // A chat in a folder that is no git repository: CDD works only in one, so the bar asks to create it and shows nothing
  // else until it is there.
  get isPlainFolder(): boolean {
    return Boolean(this.board) && !this.isClone
  }

  // The folder an app's page loads: the whole path of the folder the session works in, its workpath; empty while no
  // ticket's session is open or it works in the whole repository.
  get workpath(): string {
    return this.ticket?.session.workpath ?? ''
  }

  // The status line below the chat: the repository and branch the session works on, as repo\branch, then the whole
  // path of its folder. The chat bar shows the repository and session as icons alone, so their names are read here.
  get statusLine(): string {
    const session = this.ticket?.session
    const place = session?.repo_name && session.branch ? `${session.repo_name}\\${session.branch}` : ''
    return [place, this.sessionPath].filter(Boolean).join('  ')
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
  labelOf(slug: string): string {
    return this.board?.fidelities.find(shown => shown.fidelity.slug === slug)?.label ?? slug
  }

  // The practice a fidelity's progress names, as the board sends it with its colour.
  practiceNamed(key: string): BoardPracticeData | undefined {
    return this.board?.practices.find(shown => shown.practice.key === key)
  }
}

// ticket.move_next refused the move. reason is the server's own text.
export class MoveRefused {
  constructor(readonly reason: string) {}
}

// Atom chatBar, declared in pane/types/index.d.ts and kept in this file: the last board.overview answer.
export async function currentChatBar($: EngineInterface): Promise<ChatBarClient> {
  return new ChatBarClient(await read($, chatBar), await currentGuidance($))
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

// cdd is often still connecting when a chat opens, so the first read fails and the bar would stay empty until a turn
// ended. Reading again every two seconds, for up to a minute, fills the bar in as soon as cdd answers.
const OPENING_RETRY_MILLISECONDS = 2000
const OPENING_TRIES = 30

// Read the board with read, then again after a short wait while the board has not answered, until it does or the tries
// run out; a chat whose cdd stays down reads it again after its next turn.
export function readChatBarUntilAnswered($: EngineInterface, readBar: () => Promise<void>, attempt = 1): void {
  $.clock.after(OPENING_RETRY_MILLISECONDS, () => void readAgainWhileUnanswered($, readBar, attempt))
}

async function readAgainWhileUnanswered($: EngineInterface, readBar: () => Promise<void>, attempt: number): Promise<void> {
  if ((await read($, chatBar)).problem === null) return
  await readBar()
  if ((await read($, chatBar)).problem !== null && attempt < OPENING_TRIES) readChatBarUntilAnswered($, readBar, attempt + 1)
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
    await refreshChatBar($)
  } catch (failure) {
    await shownAsFailure($, 'The cdd server did not restart', 'Restart on the health panel, calling cdd.restart')(failure)
  }
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
  'If the cause is a bug in CDD rather than an older server or install, run /space-session-debug-session choice=fix with '
    + 'this failure as its details: it fixes the bug in a sub-agent and pushes the fix to main where you can push there, '
    + 'or opens a pull request to the CDD repository where you cannot.',
]

export function boardProblemPrompt(shown: string): string {
  const steps = BOARD_PROBLEM_STEPS.map((step, index) => `${index + 1}. ${step}`).join('\n')
  return `The CDD chat bar above the prompt shows: ${shown}\n\nFind its cause and fix it:\n${steps}\n\nThen tell me what was wrong and what you changed.`
}

// Fix on a board that did not answer sends the chat the context and the steps that usually clear it.
export async function askChatToFixBoard($: EngineInterface, shown: string): Promise<void> {
  await $.prompt.submit({ text: boardProblemPrompt(shown), asUser: true })
}

export async function moveNext($: EngineInterface, chatBar: ChatBarClient): Promise<ChatBarClient | MoveRefused> {
  try {
    await callTool<TicketData>($, 'ticket.move_next', { ticket: chatBar.sessionName })
  } catch (failure) {
    await shownAsFailure($, `${chatBar.sessionName} did not move to the next stage`, 'The stage button on the chat bar, calling ticket.move_next')(failure)
    return new MoveRefused(reasonOf(failure))
  }
  await refreshChatBar($)
  return currentChatBar($)
}

// The debug button, right after handoff: puts the debug command in the prompt box, which captures what went wrong, asks
// the person for more, and fixes the bug or requests help.
export async function runDebug($: EngineInterface, chatBar: ChatBarClient): Promise<void> {
  await $.prompt.fill({ text: debugCommandOf(chatBar.sessionFile), mode: 'append' })
}

export async function runHandoff($: EngineInterface, chatBar: ChatBarClient): Promise<void> {
  await $.prompt.fill({ text: `Write a handoff for ticket ${chatBar.sessionName} with /space-session-handoff-session session=${chatBar.sessionFile}`, mode: 'append' })
}

