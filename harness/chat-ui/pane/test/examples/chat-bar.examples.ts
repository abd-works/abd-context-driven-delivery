// The examples the chat bar's story tests share.
//
// Seed: state the cdd server owns, the TicketData and BoardData the Python Ticket and Board would report. A Given sets
// it on the stubbed server (cdd-stub.ts), never on the pane.
// Interaction: what a person types into the chat bar or reads from it, such as a new session's name.
import type { BoardData, ColumnData } from '@cdd/harness/kanban/board'
import type { ActionStatesData, TicketData } from '@cdd/harness/kanban/ticket'

// Seed: server-health.report while every part runs.
export const HEALTHY = { kanban_app_port: 8778, graph_app_port: 5173, is_hook_server_running: false }

// Seed: each stage's fidelities, in the order the board's columns name them.
export const DISCOVERY = ['stories-story_map', 'ddd-bounded_context', 'ux-ia', 'clean_engineering-modules', 'bdd-behavior']
export const SPECIFICATION = ['stories-scenarios', 'ddd-model', 'ux-mockup', 'clean_engineering-model', 'bdd-realization']
export const IMPLEMENTATION = ['stories-acceptance_tests', 'ddd-tactics', 'ux-front_end_code', 'clean_engineering-code', 'bdd-development']
export const WORK_OF: Record<string, string[]> = { Discovery: DISCOVERY, Specification: SPECIFICATION, Implementation: IMPLEMENTATION }
export const STAGE_ORDER = ['Discovery', 'Specification', 'Implementation', 'Complete']
const NOT_DONE: ActionStatesData = { generate: 'to_do', validate: 'to_do', review: 'to_do' }
const STEPS: (keyof ActionStatesData)[] = ['generate', 'validate', 'review']

// Seed: each fidelity's next action as the Python Ticket names it: satisfy while it has violations, else the first of
// generate, validate and review not done, nothing once it is done.
export function withNextActions(ticket: TicketData): TicketData {
  const nextOf = (slug: string): string => (ticket.progress[slug] === 'violations' ? 'satisfy' : (STEPS.find(step => ticket.actions[slug]?.[step] !== 'done') ?? ''))
  return { ...ticket, next_actions: Object.fromEntries(Object.keys(ticket.actions).map(slug => [slug, nextOf(slug)])) }
}

// Seed: checkout-flow, In progress in Specification with the practices Stories, UX and Clean Engineering, nothing yet done.
export function checkoutFlow(overrides: Partial<TicketData> = {}): TicketData {
  return withNextActions({
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
  } as TicketData)
}

type FidelityState = { progress: string; actions?: Partial<ActionStatesData>; violations?: number }
export const GENERATED: FidelityState = { progress: 'in_progress', actions: { generate: 'done' } }
export const VALIDATED: FidelityState = { progress: 'in_progress', actions: { generate: 'done', validate: 'done' } }
export const DONE: FidelityState = { progress: 'done', actions: { generate: 'done', validate: 'done', review: 'done' } }

// Seed: checkout-flow with these fidelities' progress, actions and violation counts as the Python Ticket would report them.
export function checkoutFlowWith(fidelities: Record<string, FidelityState>, overrides: Partial<TicketData> = {}): TicketData {
  const plain = checkoutFlow(overrides)
  const entries = Object.entries(fidelities)
  return withNextActions({
    ...plain,
    progress: { ...plain.progress, ...Object.fromEntries(entries.map(([slug, state]) => [slug, state.progress])) },
    actions: { ...plain.actions, ...Object.fromEntries(entries.map(([slug, state]) => [slug, { ...NOT_DONE, ...state.actions }])) },
    violation_counts: Object.fromEntries(entries.filter(([, state]) => state.violations).map(([slug, state]) => [slug, state.violations ?? 0])),
  })
}

// Seed: payment-retry, In progress in Discovery.
export function paymentRetry(): TicketData {
  return checkoutFlow({ title: 'Payment retry', name: 'payment-retry', column: 'Discovery', next: 'stories-story_map', session_file: '.sessions/payment-retry/session.json' })
}

const column = (name: string, tickets: TicketData[]): ColumnData => {
  const work = WORK_OF[name] ?? []
  return {
    name,
    in_progress: tickets.filter(ticket => ticket.column === name),
    ...(work.length ? { work_required: work, default_formats: { 'stories-scenarios': 'typescript', 'clean_engineering-model': 'typescript' } } : {}),
  }
}

// Seed: the board as board.show returns it, each ticket in the column it names.
export function boardOf(active: string | null, ...tickets: TicketData[]): BoardData {
  return { project: 'abd-context-driven-delivery', active, columns: [{ name: 'Backlog', items: [] }, ...STAGE_ORDER.map(name => column(name, tickets))] }
}

// Interaction: the name a person types in the session list's field.
export const NEW_SESSION_NAME = 'payment-retry'
