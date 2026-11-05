// The engine and the cdd server beneath the chat bar, for the story tests. board.show answers `board`, which a test
// changes to what the Python Ticket would return after a tool ran; every other tool answers from `answers`, or fails
// with the server's own text from `refusals`.
import type { BoardData, ColumnData } from '@cdd/harness/kanban/board'
import type { ActionStatesData, TicketData } from '@cdd/harness/kanban/ticket'

export const BAR = {
  plugin: 'cdd-board',
  component: 'AbovePrompt',
  surface: 'desktop',
  props: { hasSurvey: false, isWorking: false, maxRows: 24, bodyColumns: 160, scroll: { offset: 0, bodyRows: 24 }, view: {} },
} as const

export const HEALTHY = { kanban_app_port: 8778, graph_app_port: 5173, is_hook_server_running: false }
const cddTools = (count: number) => Array.from({ length: count }, (_, index) => ({ name: `mcp__plugin_cdd_cdd__tool_${index}`, description: '', mcp: true }))

export const SPECIFICATION = ['stories-scenarios', 'ddd-model', 'ux-mockup', 'clean_engineering-model', 'bdd-realization']
export const DISCOVERY = ['stories-story_map', 'ddd-bounded_context', 'ux-ia', 'clean_engineering-modules', 'bdd-behavior']
export const IMPLEMENTATION = ['stories-acceptance_tests', 'ddd-tactics', 'ux-front_end_code', 'clean_engineering-code', 'bdd-development']
const NOT_DONE = { generate: 'to_do', validate: 'to_do', review: 'to_do' }

// checkout-flow, In progress in Specification with the practices Stories, UX and Clean Engineering, nothing yet done.
export function checkoutFlow(overrides: Partial<TicketData> = {}): TicketData {
  return {
    title: 'Checkout flow',
    last_activity: '2026-11-05T06:00:00Z',
    name: 'checkout-flow',
    scope: '',
    parent: '',
    column: 'Specification',
    is_done: false,
    next: 'stories-scenarios',
    next_action: 'generate',
    handoff: '',
    reports: {},
    violation_counts: {},
    practices: { stories: true, ddd: false, ux: true, clean_engineering: true, bdd: false },
    workpath: '',
    worktree: '',
    practice_roots: {
      stories: { root: 'harness/chat-ui/.context', is_chosen: true },
      ux: { root: 'harness/chat-ui/design', is_chosen: true },
      clean_engineering: { root: 'harness/chat-ui/pane', is_chosen: true },
    },
    session_file: '.sessions/checkout-flow/session.json',
    progress: {},
    actions: Object.fromEntries([...DISCOVERY, ...SPECIFICATION, ...IMPLEMENTATION].map(slug => [slug, NOT_DONE])),
    allowed_actions: {},
    ...overrides,
  }
}

type FidelityState = { progress: string; actions?: Partial<ActionStatesData>; violations?: number }
export const GENERATED: FidelityState = { progress: 'in_progress', actions: { generate: 'done' } }
export const VALIDATED: FidelityState = { progress: 'in_progress', actions: { generate: 'done', validate: 'done' } }
export const DONE: FidelityState = { progress: 'done', actions: { generate: 'done', validate: 'done', review: 'done' } }

// checkout-flow with these fidelities' progress, actions and violation counts as the Python Ticket would report them.
export function checkoutFlowWith(fidelities: Record<string, FidelityState>, overrides: Partial<TicketData> = {}): TicketData {
  const plain = checkoutFlow(overrides)
  const entries = Object.entries(fidelities)
  return {
    ...plain,
    progress: { ...plain.progress, ...Object.fromEntries(entries.map(([slug, state]) => [slug, state.progress])) },
    actions: { ...plain.actions, ...Object.fromEntries(entries.map(([slug, state]) => [slug, { ...NOT_DONE, ...state.actions }])) },
    violation_counts: Object.fromEntries(entries.filter(([, state]) => state.violations).map(([slug, state]) => [slug, state.violations ?? 0])),
  }
}

export function paymentRetry(): TicketData {
  return checkoutFlow({ title: 'Payment retry', name: 'payment-retry', column: 'Discovery', next: 'stories-story_map', session_file: '.sessions/payment-retry/session.json' })
}

const column = (name: string, work: string[], tickets: TicketData[]): ColumnData => ({
  name,
  in_progress: tickets.filter(ticket => ticket.column === name),
  ...(work.length ? { work_required: work, default_formats: { 'stories-scenarios': 'typescript', 'clean_engineering-model': 'typescript' } } : {}),
})

// The board as board.show returns it, each ticket in the column it names.
export function boardOf(active: string | null, ...tickets: TicketData[]): BoardData {
  return {
    project: 'abd-context-driven-delivery',
    active,
    columns: [
      { name: 'Backlog', items: [] },
      column('Discovery', DISCOVERY, tickets),
      column('Specification', SPECIFICATION, tickets),
      column('Implementation', IMPLEMENTATION, tickets),
      column('Complete', [], tickets),
    ],
  }
}

type Call = { tool: string; args: any }

export type World = {
  board: BoardData
  calls: Call[]
  sent: string[]
  fills: string[]
  toasts: string[]
  answers: Record<string, unknown>
  refusals: Record<string, string>
  health: unknown
  healthText: string | null
  toolCount: number
  serverLost: boolean
  installExit: { exitCode: number; stderr: string }
  timers: (() => void)[]
  installs: string[][]
}

const answer = (value: unknown) => ({ value: { content: [{ type: 'text', text: JSON.stringify(value) }], isError: false } })

function answerTool(world: World, tool: string, args: unknown) {
  world.calls.push({ tool, args })
  if (world.serverLost) throw new Error('no connected MCP tool on a server named "plugin:cdd:cdd"')
  if (tool === 'server-health.report' && world.healthText !== null) return { value: { content: [{ type: 'text', text: world.healthText }], isError: false } }
  if (tool === 'server-health.report') return answer(world.health)
  if (world.refusals[tool]) return { value: { content: [{ type: 'text', text: world.refusals[tool] }], isError: true } }
  return answer(tool === 'board.show' ? world.board : world.answers[tool])
}

export function cdd(on: any, board: BoardData = boardOf('checkout-flow', checkoutFlow())): World {
  const world: World = { board, calls: [], sent: [], fills: [], toasts: [], answers: {}, refusals: {}, health: HEALTHY, healthText: null, toolCount: 116, serverLost: false, installExit: { exitCode: 0, stderr: '' }, timers: [], installs: [] }
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
  on('process.run', (_: unknown, e: { argv: string[] }) => {
    world.installs.push(e.argv)
    return { value: { ...world.installExit, stdout: '' } }
  })
  on('session.start', (_: unknown, e: { cwd: string }) => ({ cwd: e.cwd }))
  return world
}

// Starts the chat, sends one prompt so the chat bar has read the board, and mounts the bar above the prompt.
export async function openChatBar($: any) {
  await $.session.start({ cwd: '/', surface: 'desktop', isInteractive: true })
  await $.prompt.submit({ text: 'look' })
  return $.ui.mount(BAR)
}

export const findText = (ui: any, text: RegExp | string) => ui.find({ type: 'Text', text })

export const called = (world: World, tool: string) => world.calls.find(call => call.tool === tool)?.args

// The props of the element drawn with this key, or undefined when nothing is.
export const drawn = async (ui: any, key: string) => ui.find({ key })

// The keys of the Buttons drawn under an element, in the order they read left to right and top to bottom.
export function buttonKeys(node: any): string[] {
  if (!node || typeof node !== 'object') return []
  const own = node.type === 'Button' ? [String(node.key ?? node.props?.key)] : []
  const children = Array.isArray(node.children) ? node.children : node.children ? [node.children] : []
  return [...own, ...children.flatMap(buttonKeys)]
}

// Lets the engine finish what a timer or the installer started before a step reads the chat bar.
export const settle = () => new Promise(resolve => setTimeout(resolve, 50))

export async function dueTimers(world: World): Promise<void> {
  const due = world.timers.splice(0)
  for (const fire of due) fire()
  await settle()
}

// A Text's words, however the test kit hands the element back.
export const textOf = (node: any): string | undefined => node?.text ?? node?.children?.[0]

// The first Text drawn inside an element, such as a dot's mark or the health mark.
export const markOf = async (ui: any, key: string) => (await ui.find({ key }))?.children?.[0]

// A Button's label, the words a person reads on hover and a surface finds it by.
export const labelOf = async (ui: any, key: string): Promise<string | undefined> => {
  const node = await ui.find({ key })
  return node?.props?.label ?? node?.label
}
