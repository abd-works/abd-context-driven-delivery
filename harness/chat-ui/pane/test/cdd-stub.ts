// The engine and the cdd server beneath the chat bar, for the story tests. board.show answers `board`, the Seed a Given
// sets. The ticket tools a press reaches change that board as the Python Ticket does, so a test reads the server's state
// after the press rather than setting it by hand. The read tools answer from the server's state for the ticket,
// fidelity or path asked for, as the Python Session and FidelityProgress do: `declared` files and `reports` per
// fidelity, `texts` per path, `workspaces` per ticket. Any tool fails with the server's own text from `refusals`.
import type { BoardData, WorkspaceData } from '@cdd/harness/kanban/board'
import type { FidelityProgressData, FileEntryData, ReportData } from '@cdd/harness/kanban/fidelity-progress'
import type { FileTextData } from '@cdd/space/session/session'
import type { TicketData } from '@cdd/harness/kanban/ticket'

import { boardOf, checkoutFlow, HEALTHY, progressOf, STAGE_ORDER, WORK_OF } from './examples/chat-bar.examples'

type Call = { tool: string; args: any }

export type World = {
  board: BoardData
  calls: Call[]
  sent: string[]
  fills: string[]
  toasts: string[]
  declared: Record<string, Record<string, FileEntryData[]>>
  reports: Record<string, ReportData>
  texts: Record<string, string>
  workspaces: Record<string, WorkspaceData>
  refusals: Record<string, string>
  health: unknown
  healthText: string | null
  toolCount: number
  serverLost: boolean
  installExit: { exitCode: number; stderr: string }
  timers: (() => void)[]
  installs: string[][]
}

const cddTools = (count: number) => Array.from({ length: count }, (_, index) => ({ name: `mcp__plugin_cdd_cdd__tool_${index}`, description: '', mcp: true }))
const toolAnswer = (toolJson: unknown) => ({ value: { content: [{ type: 'text', text: JSON.stringify(toolJson) }], isError: false } })
const toolText = (text: string, isError: boolean) => ({ value: { content: [{ type: 'text', text }], isError } })

const ticketsOf = (board: BoardData): TicketData[] => board.columns.flatMap(column => [...(column.in_progress ?? []), ...(column.tickets ?? [])])

// The first fidelity of the ticket's stage, among its practices, that is not done; null once the stage is done.
function nextOf(ticket: TicketData): string | null {
  return (WORK_OF[ticket.column] ?? []).find(slug => ticket.session.practices[slug.slice(0, slug.indexOf('-'))]?.enabled && ticket.progress[slug]?.state !== 'done') ?? null
}

function changed(world: World, ticket: TicketData, active: string | null = world.board.active): TicketData {
  // Ticket.next_fidelity is none once the stage is done or the ticket is Complete.
  const next = ticket.column === 'Complete' || ticket.is_done ? null : nextOf(ticket)
  const settled = { ...ticket, next }
  world.board = boardOf(active, ...ticketsOf(world.board).map(entry => (entry.name === settled.name ? settled : entry)))
  return settled
}

const named = (world: World, name: string): TicketData => {
  const found = ticketsOf(world.board).find(ticket => ticket.name === name)
  if (!found) throw new Error(`no ticket named ${name}`)
  return found
}

// Ticket.move_next: a stage not yet done is marked done; a done stage moves the ticket into the next one, not started.
function moveNext(world: World, { ticket }: { ticket: string }): TicketData {
  const moving = named(world, ticket)
  if (!moving.is_done) return changed(world, { ...moving, is_done: true })
  const following = STAGE_ORDER[STAGE_ORDER.indexOf(moving.column) + 1] ?? 'Complete'
  return changed(world, { ...moving, column: following, is_done: false })
}

// FidelityProgress.finish_review: the fidelity is reviewed and done; the stage is done once every fidelity of it is.
function finishReview(world: World, { ticket, fidelity }: { ticket: string; fidelity: string }): FidelityProgressData {
  const reviewing = named(world, ticket)
  const actions = { ...reviewing.progress[fidelity]!.actions, review: 'done' }
  const reviewed = { ...reviewing, progress: { ...reviewing.progress, [fidelity]: progressOf(ticket, fidelity, 'done', actions) } }
  return changed(world, { ...reviewed, is_done: nextOf(reviewed) === null }).progress[fidelity]!
}

// Ticket.close: the ticket goes to Complete and no session is active.
function close(world: World, { ticket }: { ticket: string }): TicketData {
  return changed(world, { ...named(world, ticket), column: 'Complete' }, world.board.active === ticket ? null : world.board.active)
}

// Board.activate: the ticket becomes the board's active session.
function activate(world: World, { ticket }: { ticket: string }): TicketData {
  return changed(world, named(world, ticket), ticket)
}

// Ticket.create: a new ticket In progress in Discovery, named from its title.
function create(world: World, { title }: { title: string }): TicketData {
  const name = title.toLowerCase().replace(/[^a-z0-9]+/g, '-')
  const created = checkoutFlow({ title, name, column: 'Discovery', next: 'stories-story-map' })
  world.board = boardOf(world.board.active, ...ticketsOf(world.board), created)
  return created
}

// A refusal the cdd server sends back as its error text.
class Refused extends Error {}

// FidelityProgress.files: the files the asked fidelity declares, by format; none for a fidelity that declares none.
const files = (world: World, { fidelity }: { fidelity: string }): Record<string, FileEntryData[]> => world.declared[fidelity] ?? {}

// FidelityProgress.report: the asked fidelity's latest validation report; an empty report when it has none.
const report = (world: World, { fidelity }: { fidelity: string }): ReportData => world.reports[fidelity] ?? ({ path: '', text: '', rules: [], has_saved_graph: false } as ReportData)

// Session.read_file: the text of a path under the session's roots, no text once it is gone; a path that climbs out of
// the roots is refused with PathOutsideRootsError's text.
function readFile(world: World, { path }: { session: string; path: string }): FileTextData {
  if (path.split('/').includes('..')) throw new Refused(`${path} is outside the session's roots`)
  return { path, text: world.texts[path] ?? '' }
}

// Board.workspace: whether the ticket has a branch and a worktree of its own; none for a ticket that has neither.
const workspace = (world: World, { ticket }: { ticket: string }): WorkspaceData => world.workspaces[ticket] ?? ({ has_branch: false, has_worktree: false, leaving_has_branch: false } as WorkspaceData)

// Ticket.generate_commands: the generate command for the fidelities in the formats, in the ticket's session. The stub's
// fidelities have no earlier file to render from, so no render command comes first.
const generateCommands = (world: World, { ticket, fidelities, formats }: { ticket: string; fidelities: string[]; formats: string[] }): string[] => [
  `/actions-generate ${fidelities.join(' ')} format=${formats.join(',')} session=${named(world, ticket).session.session_file}`,
]

const TOOLS: Record<string, (world: World, args: any) => unknown> = {
  'ticket.generate_commands': generateCommands,
  'ticket.move_next': moveNext,
  'fidelity-progress.finish_review': finishReview,
  'ticket.close': close,
  'board.activate': activate,
  'ticket.create': create,
  'fidelity-progress.files': files,
  'fidelity-progress.report': report,
  'session.read_file': readFile,
  'board.workspace': workspace,
}

// A tool call the agent makes on the cdd server, not the chat bar: the server's state changes and the chat bar only
// hears of it through the engine's tool.call event.
export function agentCalls(world: World, tool: string, args: unknown): void {
  TOOLS[tool]!(world, args)
}

function answerTool(world: World, tool: string, args: unknown) {
  world.calls.push({ tool, args })
  if (world.serverLost) throw new Error('no connected MCP tool on a server named "plugin:cdd:cdd"')
  if (tool === 'server-health.report') return world.healthText !== null ? toolText(world.healthText, false) : toolAnswer(world.health)
  if (world.refusals[tool]) return toolText(world.refusals[tool], true)
  if (tool === 'board.show') return toolAnswer(world.board)
  const operation = TOOLS[tool]
  if (!operation) throw new Error(`the cdd stub has no tool ${tool}`)
  try {
    return toolAnswer(operation(world, args))
  } catch (failure) {
    if (failure instanceof Refused) return toolText(failure.message, true)
    throw failure
  }
}

function runProcess(world: World, argv: string[]) {
  world.installs.push(argv)
  return { value: { ...world.installExit, stdout: '' } }
}

// Stubs the engine's calls the chat bar makes and the cdd server beneath it, starting from checkout-flow active.
export function cdd(on: any, board: BoardData = boardOf('checkout-flow', checkoutFlow())): World {
  const world: World = {
    board,
    calls: [],
    sent: [],
    fills: [],
    toasts: [],
    declared: {},
    reports: {},
    texts: {},
    workspaces: {},
    refusals: {},
    health: HEALTHY,
    healthText: null,
    toolCount: 116,
    serverLost: false,
    installExit: { exitCode: 0, stderr: '' },
    timers: [],
    installs: [],
  }
  on('command.register', () => ({ value: undefined }))
  on('session.id', () => ({ value: 'chat-1' }))
  on('session.cwd', () => ({ value: '/' }))
  on('session.messages', () => ({ value: [] }))
  on('clock.every', () => ({ value: undefined }))
  // A timer comes due only when a test calls dueTimers, so a test decides when a reconnect tries again.
  on('clock.after', () => new Promise(resolve => world.timers.push(() => resolve({ value: undefined }))))
  on('tool.list', () => ({ value: cddTools(world.toolCount) }))
  on('tool.call', () => ({ result: {} }))
  on('mcp.call', (_: unknown, e: { tool: string; args: unknown }) => answerTool(world, e.tool, e.args))
  on('ui.toast', (_: unknown, e: { text: string }) => {
    world.toasts.push(e.text)
    return { value: undefined }
  })
  on('ui.status', () => ({ value: undefined }))
  on('ui.invalidate', () => ({ value: undefined }))
  on('ui.log', () => ({ value: undefined }))
  on('prompt.fill', (_: unknown, e: { text: string }) => {
    world.fills.push(e.text)
    return { isFilled: true }
  })
  on('prompt.submit', (_: unknown, e: { text: string }) => ({ text: e.text }))
  on('command.run', (_: unknown, e: { command: string; args: string }) => {
    world.sent.push(`/${e.command} ${e.args}`.trim())
    return { value: { text: '' } }
  })
  on('http.fetch', () => ({ value: { ok: true, status: 200, text: '' } }))
  on('env.get', () => ({ value: undefined }))
  on('fs.exists', () => ({ value: false }))
  on('process.run', (_: unknown, e: { argv: string[] }) => runProcess(world, e.argv))
  on('session.start', (_: unknown, e: { cwd: string }) => ({ cwd: e.cwd }))
  return world
}

// The arguments of the first call the chat bar made to tool, or undefined when it made none.
export const called = (world: World, tool: string) => world.calls.find(call => call.tool === tool)?.args
