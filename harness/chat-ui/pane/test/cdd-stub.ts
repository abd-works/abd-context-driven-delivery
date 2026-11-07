// The engine and the cdd server beneath the chat bar, for the story tests. board.show answers `board`, the Seed a Given
// sets. The ticket tools a press reaches change that board as the Python Ticket does, so a test reads the server's state
// after the press rather than setting it by hand. The read tools answer from the server's state for the ticket,
// fidelity or path asked for, as the Python Ticket, Session and FidelityProgress do: `branches` per ticket, `declared`
// files and `reports` per fidelity, `texts` per path. Any tool fails with the server's own text from `refusals`. An
// operation Python does not have, or an argument it does not take, is refused and kept in `unknown`, which every story
// expects empty, so a test fails when the chat bar calls a name Python dropped.
import type { BoardData } from '@cdd/space/kanban/board'
import type { FidelityProgressData, FileEntryData, ReportData } from '@cdd/space/kanban/fidelity-progress'
import type { BranchData, TicketData } from '@cdd/space/kanban/ticket'
import type { FileTextData } from '@cdd/space/session/session'

import { boardOf, checkoutFlow, HEALTHY, progressOf, STAGE_ORDER } from './examples/chat-bar.examples'

type Call = { tool: string; args: any }

export type World = {
  board: BoardData
  calls: Call[]
  unknown: string[]
  sent: string[]
  fills: string[]
  submits: string[]
  toasts: string[]
  branches: Record<string, BranchData>
  declared: Record<string, Record<string, FileEntryData[]>>
  reports: Record<string, ReportData>
  texts: Record<string, string>
  refusals: Record<string, string>
  health: unknown
  healthText: string | null
  toolCount: number
  serverLost: boolean
  installExit: { exitCode: number; stderr: string }
  timers: (() => void)[]
  installs: string[][]
  panes: { id: string; title?: string }[]
}

const cddTools = (count: number) => Array.from({ length: count }, (_, index) => ({ name: `mcp__plugin_cdd_cdd__tool_${index}`, description: '', mcp: true }))
const toolAnswer = (toolJson: unknown) => ({ value: { content: [{ type: 'text', text: JSON.stringify(toolJson) }], isError: false } })
const toolText = (text: string, isError: boolean) => ({ value: { content: [{ type: 'text', text }], isError } })

const ticketsOf = (board: BoardData): TicketData[] => board.columns.flatMap(column => [...(column.in_progress ?? []), ...(column.tickets ?? [])])

// The first fidelity of the ticket's stage, among its practices, that is not done; null once the stage is done.
function nextOf(ticket: TicketData): FidelityProgressData | null {
  return ticket.progress.find(progress => progress.stage.name === ticket.column.name && progress.is_enabled && progress.state !== 'done') ?? null
}

const activeName = (world: World): string | null => world.board.active?.name ?? null

function changed(world: World, ticket: TicketData, active: string | null = activeName(world)): TicketData {
  // Ticket.next_fidelity is none once the stage is done or the ticket is Complete, and names its progress otherwise.
  const progress = ticket.column.name === 'Complete' || ticket.is_done ? null : nextOf(ticket)
  const settled = { ...ticket, next: progress && { ticket: progress.ticket, fidelity: { slug: progress.fidelity.slug } } }
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
  const following = STAGE_ORDER[STAGE_ORDER.indexOf(moving.column.name) + 1] ?? 'Complete'
  return changed(world, { ...moving, column: { name: following }, is_done: false })
}

// FidelityProgress.finish_review: the fidelity is reviewed and done; the stage is done once every fidelity of it is.
function finishReview(world: World, { ticket, fidelity }: { ticket: string; fidelity: string }): FidelityProgressData {
  const reviewing = named(world, ticket)
  const progressNamed = (entry: TicketData) => entry.progress.find(progress => progress.fidelity.slug === fidelity)!
  const actions = { ...progressNamed(reviewing).actions, review: 'done' }
  const reviewed = { ...reviewing, progress: reviewing.progress.map(progress => (progress.fidelity.slug === fidelity ? progressOf(ticket, fidelity, 'done', actions) : progress)) }
  return progressNamed(changed(world, { ...reviewed, is_done: nextOf(reviewed) === null }))
}

// Ticket.close: the ticket goes to Complete and no session is active.
function close(world: World, { ticket }: { ticket: string }): TicketData {
  return changed(world, { ...named(world, ticket), column: { name: 'Complete' } }, activeName(world) === ticket ? null : activeName(world))
}

// Ticket.activate: the ticket becomes the board's active session.
function activate(world: World, { ticket }: { ticket: string }): TicketData {
  return changed(world, named(world, ticket), ticket)
}

// Ticket.create: a new ticket In progress in Discovery, named from its title.
function create(world: World, { title }: { title: string }): TicketData {
  const name = title.toLowerCase().replace(/[^a-z0-9]+/g, '-')
  const created = checkoutFlow({ title, name, column: 'Discovery', next: 'stories-story-map' })
  world.board = boardOf(activeName(world), ...ticketsOf(world.board), created)
  return created
}

// A refusal the cdd server sends back as its error text.
class Refused extends Error {}

// FidelityProgress.files: the files the asked fidelity declares, by format; none for a fidelity that declares none.
const files = (world: World, { fidelity }: { fidelity: string }): Record<string, FileEntryData[]> => world.declared[fidelity] ?? {}

// FidelityProgress.report: the asked fidelity's latest validation report; an empty report when it has none.
const report = (world: World, { fidelity }: { fidelity: string }): ReportData => world.reports[fidelity] ?? ({ path: '', text: '', rules: [], has_saved_graph: false, is_out_of_date: false } as ReportData)

// Session.read_file: the text of a path under the session's roots, no text once it is gone; a path that climbs out of
// the roots is refused with PathOutsideRootsError's text.
function readFile(world: World, { path }: { session: string; path: string }): FileTextData {
  if (path.split('/').includes('..')) throw new Refused(`${path} is outside the session's roots`)
  return { path, text: world.texts[path] ?? '' }
}

// Ticket.branch and Ticket.work_branch: the branch the story gives the ticket, such as main for work on main; for a
// ticket the story gives none, its own branch, named as the ticket, which the repository does not have.
const branch = (world: World, { ticket }: { ticket: string }): BranchData => world.branches[ticket] ?? { name: ticket, exists: false, is_checked_out: false }

const TOOLS: Record<string, (world: World, args: any) => unknown> = {
  'ticket.branch': branch,
  'ticket.work_branch': branch,
  'ticket.move_next': moveNext,
  'fidelity-progress.finish_review': finishReview,
  'ticket.close': close,
  'ticket.activate': activate,
  'ticket.create': create,
  'fidelity-progress.files': files,
  'fidelity-progress.report': report,
  'session.read_file': readFile,
}

// A tool call the agent makes on the cdd server, not the chat bar: the server's state changes and the chat bar only
// hears of it through the engine's tool.call event.
export function agentCalls(world: World, tool: string, args: unknown): void {
  TOOLS[tool]!(world, args)
}

// Each cdd operation the chat bar calls, with the arguments its Python signature takes: the tool subject's, such as
// ticket for Ticket.load, then the operation's own.
export const OPERATIONS: Record<string, string[]> = {
  'server-health.report': [],
  'board.show': [],
  'ticket.create': ['title', 'scope', 'parent', 'path'],
  'ticket.activate': ['ticket', 'leaving', 'opening'],
  'ticket.branch': ['ticket'],
  'ticket.work_branch': ['ticket'],
  'ticket.close': ['ticket', 'leaving'],
  'ticket.move_next': ['ticket'],
  'fidelity-progress.finish_review': ['ticket', 'fidelity'],
  'fidelity-progress.files': ['ticket', 'fidelity'],
  'fidelity-progress.report': ['ticket', 'fidelity'],
  'session.read_file': ['session', 'path'],
}

// What is wrong with calling tool with args, as the server words it; empty when Python has that operation and takes them.
function mismatchOf(tool: string, args: unknown): string {
  const taken = OPERATIONS[tool]
  if (!taken) return `${tool} is not a cdd operation`
  const extra = Object.keys(args ?? {}).filter(name => !taken.includes(name))
  return extra.length ? `${tool} takes no argument ${extra.join(', ')}` : ''
}

function answerTool(world: World, tool: string, args: unknown) {
  world.calls.push({ tool, args })
  if (world.serverLost) throw new Error('no connected MCP tool on a server named "plugin:cdd:cdd"')
  const mismatch = mismatchOf(tool, args)
  if (mismatch) {
    world.unknown.push(mismatch)
    return toolText(mismatch, true)
  }
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
    unknown: [],
    sent: [],
    fills: [],
    submits: [],
    toasts: [],
    branches: {},
    declared: {},
    reports: {},
    texts: {},
    refusals: {},
    health: HEALTHY,
    healthText: null,
    toolCount: 116,
    serverLost: false,
    installExit: { exitCode: 0, stderr: '' },
    timers: [],
    installs: [],
    panes: [],
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
  // The panes the chat bar opened beside the chat, the files pane among them, and closed again.
  on('ui.open', (_: unknown, e: { id: string; title?: string }) => {
    world.panes = [...world.panes.filter(pane => pane.id !== e.id), { id: e.id, title: e.title }]
    return { value: { isPlaced: true } }
  })
  on('ui.close', (_: unknown, e: { id: string }) => {
    world.panes = world.panes.filter(pane => pane.id !== e.id)
    return { value: undefined }
  })
  on('ui.log', () => ({ value: undefined }))
  on('prompt.fill', (_: unknown, e: { text: string }) => {
    world.fills.push(e.text)
    return { isFilled: true }
  })
  on('prompt.submit', (_: unknown, e: { text: string }) => {
    world.submits.push(e.text)
    return { text: e.text }
  })
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
